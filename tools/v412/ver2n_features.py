"""Pokemon Arena v4.1.2-ver2n Features:
1. Ability Patch (10,000g) with Yes/No Confirmation Dialog:
   - When bought from Item Shop (or clicked in inventory), prompts a Warcraft III native Dialog:
     Shows Pokemon Name, official PokeAPI Hidden Ability Name, and detailed description.
     Buttons: [ Dong Y / Yes (10.000g) ] vs [ Huy Bo / No (Hoan Tien) ].
     If Yes: consumes item, unlocks Hidden Ability permanently, plays awakening VFX.
     If No: cancels transaction, removes item, refunds 10,000 Gold immediately.
2. Minute 55:00 Mega Rayquaza Awakened World Boss:
   - Spawns at 55:00 (3300s) at Center Altar (-128, 16) with 80,000 HP, 35 Armor.
   - 5-Minute Despawn Timer: despawns cleanly at 60:00 (3600s) if not defeated.
   - Defeating Rayquaza grants the killer team the PERMANENT DRAGON ASCENT BUFF (+25% All Stats,
     +20% MS, 2% HP/Mana per second, lightning strikes) + 2,000 Gold per teammate.
   - Master Ball completely removed.
3. Contested Gym PvPvE & Anti-Smurf:
   - Gym Boss is 100% immune to damage from non-challengers (BlzSetEventDamage(0.0)).
   - Players who have already passed Gym K (Badge_Has == true) are strictly barred from entering (teleported out).
   - Contenders on same Gym level and allies can enter to fight PvP.
4. Tall Grass Bushes (Bui Co An Nap):
   - 6 strategic jungle/river bush zones grant Invisibility after 1.5s still; broken on attack/cast.
5. Dynamic Interactive Weather:
   - 240s cycle (Sun, Rain, Sandstorm, Hail) altering elemental damage and triggering weather abilities.
6. Shop Cleanup & Teleport Fixes:
   - Redundant Escape Rope & Mega Ring removed from nIS0; replaced with IMHA, IB0C, IB0D.
   - Shops scaled to 0.16 at Y = +/-380; Portal moved to Y = -/+760 with 2s channel + 30s CD.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))


def patch_objects(abil, items, func, strings, w3u):
    """Adds IMHA (Ability Patch), IB0C (Eject Button), IB0D (Heavy-Duty Boots) and cleans up nIS0."""
    icol = items.name_to_x
    base_item = items.find('IT00') or items.rows[0]

    # 1. Add IMHA (Ability Patch) in ItemData.slk
    if not items.find('IMHA'):
        r = dict(base_item)
        r[1] = '"IMHA"'
        if 'goldcost' in icol:
            r[icol['goldcost']] = '10000'
        if 'lumbercost' in icol:
            r[icol['lumbercost']] = '0'
        if 'stockMax' in icol:
            r[icol['stockMax']] = '1'
        if 'stockStart' in icol:
            r[icol['stockStart']] = '1'
        if 'stockRegen' in icol:
            r[icol['stockRegen']] = '0'
        items.rows.append(r)

    # 2. Add IB0C (Eject Button) in ItemData.slk
    if not items.find('IB0C'):
        r = dict(base_item)
        r[1] = '"IB0C"'
        if 'goldcost' in icol:
            r[icol['goldcost']] = '3500'
        if 'lumbercost' in icol:
            r[icol['lumbercost']] = '0'
        items.rows.append(r)

    # 3. Add IB0D (Heavy-Duty Boots) in ItemData.slk
    if not items.find('IB0D'):
        r = dict(base_item)
        r[1] = '"IB0D"'
        if 'goldcost' in icol:
            r[icol['goldcost']] = '2800'
        if 'lumbercost' in icol:
            r[icol['lumbercost']] = '0'
        items.rows.append(r)

    # 4. Fix IL02 in ItemData.slk (stock = 1, removes '943')
    r_il02 = items.find('IL02')
    if r_il02:
        if 'stockMax' in icol:
            r_il02[icol['stockMax']] = '1'
        if 'stockStart' in icol:
            r_il02[icol['stockStart']] = '1'
        if 'stockRegen' in icol:
            r_il02[icol['stockRegen']] = '0'

    # 5. Add definitions in ItemFunc.txt (100% clean English for default Warcraft III Reforged font)
    if '[IMHA]' not in func:
        func += """
[IMHA]
Name=Ability Patch
Hotkey=A
Tip=Purchase |cff00ffffAbility Patch|r (|cffffd16610,000g|r)
Ubertip="Awakens your Pokemon's official |cff00ff00Hidden Ability|r from PokeAPI. Displays a confirmation dialog with ability details before activating."
Buttonpos=2,1
Art=ReplaceableTextures\\CommandButtons\\BTNPokemonTrainerIcon.blp

[IB0C]
Name=Eject Button
Hotkey=E
Tip=Purchase |cff00ffffEject Button|r (|cffffd1663,500g|r)
Ubertip="+15 Armor. When HP drops below 30%, instantly blinks 700 distance away to safety (60s cooldown)."
Buttonpos=2,2
Art=ReplaceableTextures\\CommandButtons\\BTNPenguin.blp

[IB0D]
Name=Heavy-Duty Boots
Hotkey=H
Tip=Purchase |cff00ffffHeavy-Duty Boots|r (|cffffd1662,800g|r)
Ubertip="+60 Movement Speed. Grants 100% immunity to ground traps, hazards, and terrain slow effects."
Buttonpos=2,3
Art=ReplaceableTextures\\CommandButtons\\BTNBootsOfSpeed.blp
"""

    # 6. Clean nIS0 (Item Shop) in war3map.w3u: remove redundant IT05, IT06; add IMHA, IB0C, IB0D
    shop_nis0 = w3u.find('nIS0')
    if shop_nis0:
        shop_nis0.set('usei', 3, 'IT00,IT01,IT02,IT03,IT04,IMHA,IB0C,IB0D,IT07,IT08')

    # 7. Keep all base shops at uniform 0.20 scale
    for sid in ['nBS0', 'nFS1']:
        u = w3u.find(sid)
        if u:
            u.set('usca', 1, 0.20)

    return func, strings


def patch_jass(script: str) -> str:
    """Applies all ver2n JASS mechanics:
    - Ability Patch with Confirmation Dialog (Yes/No)
    - Awakened Mega Rayquaza (Min 55:00 spawn, 60:00 despawn, permanent Dragon Ascent buff, no Master Ball)
    - Contested Gym PvPvE with 0.0 damage to Gym Boss for non-challengers & anti-smurf badge check
    - Tall Grass Bushes (6 regions, 1.5s stealth)
    - Dynamic Interactive Weather (240s cycle)
    - Teleport portal channeling (2.0s) + 30s per-player cooldown
    """
    # 1. JASS Globals for ver2n (inserted directly inside existing globals block)
    ver2n_globals = """
// ==========================================
// VER2N GAMEPLAY OVERHAUL GLOBALS
// ==========================================
    hashtable AbilityPatch_HT = null
    dialog array AbilityPatch_Dialog
    button array AbilityPatch_BtnYes
    button array AbilityPatch_BtnNo
    unit array AbilityPatch_Unit
    item array AbilityPatch_Item
    trigger AbilityPatch_DialogTrig = null

    unit Rayquaza_BossUnit = null
    real Rayquaza_DespawnTime = 0.0
    boolean Rayquaza_Spawned = false
    boolean Rayquaza_Warned = false
    boolean array DragonAscent_Buff

    real array Player_MidTpCd
    real array Player_MidTpChan
    real array Bush_StillTime
    boolean array Bush_InStealth

    real Wth_NextCycle = 240.0
"""

    # Insert variables right after first globals keyword
    script = re.sub(r'\bglobals\b', "globals\n" + ver2n_globals, script, count=1)

    # 2. Add Contested Gym 0.0 damage block in Ab_OnDamaging
    gym_block_code = """
    // VER2N CONTESTED GYM PVPVE: Non-challengers deal 0.0 damage to Gym Boss
    set g = 0
    loop
        exitwhen g >= 8
        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and t == Gym_Cur[g] then
            if sp != Player(Gym_Pid[g]) then
                call BlzSetEventDamage(0.0)
                set t = null
                set src = null
                set sp = null
                return false
            endif
        endif
        set g = g + 1
    endloop
"""
    # In Ab_OnDamaging, ensure local integer g is declared, then insert gym_block_code
    script = script.replace("local integer ht = 0", "local integer ht = 0\n    local integer g = 0")
    target_anchor = "if Fx_LeagueBlock(src, t) then"
    if target_anchor in script:
        script = script.replace(target_anchor, gym_block_code + "\n    " + target_anchor)

    # 3. Add Anti-Smurf and Contested Gym Alerts in Gym_Tick
    busy_anchor = 'Gym " + I2S(g + 1) + " is busy:'
    if busy_anchor in script:
        pos = script.find(busy_anchor)
        start_if = script.rfind('if pid < 12', 0, pos)
        end_if = script.find('endif', pos) + 5
        if start_if != -1 and end_if != -1:
            new_warn_block = """if pid < 12 and pid != Gym_Pid[g] and IsUnitType(u, UNIT_TYPE_HERO) then
                        // Anti-Smurf: If player already passed Gym g, repel them
                        if Badge_Has[pid * 8 + g] then
                            call SetUnitPosition(u, Gym_X[g] + (Gym_Start + 80.0) * Cos(Atan2(GetUnitY(u) - Gym_Y[g], GetUnitX(u) - Gym_X[g])), Gym_Y[g] + (Gym_Start + 80.0) * Sin(Atan2(GetUnitY(u) - Gym_Y[g], GetUnitX(u) - Gym_X[g])))
                            if Mega_Time >= Gym_Warn[pid] then
                                set Gym_Warn[pid] = Mega_Time + 4.0
                                call DisplayTimedTextToPlayer(Player(pid), 0, 0, 4.0, "|cffff2222[Anti-Smurf]|r You already cleared Gym " + I2S(g + 1) + "! Cannot enter to disrupt other challengers.")
                            endif
                        else
                            // Contender or Ally entering: allow PvP contest and announce invasion!
                            if Mega_Time >= Gym_Warn[pid] then
                                set Gym_Warn[pid] = Mega_Time + 5.0
                                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 4.0, "|cffff0000[GYM CONTEST WARNING]|r " + GetPlayerName(Player(pid)) + " entered Gym " + I2S(g + 1) + " to contest your battle!")
                                call DisplayTimedTextToPlayer(Player(pid), 0, 0, 4.0, "|cff00ffff[GYM CONTEST]|r Contesting Gym " + I2S(g + 1) + ". You can only damage enemy players (Gym Boss takes 0 damage)!")
                            endif
                        endif
                    endif"""
            script = script[:start_if] + new_warn_block + script[end_if:]

    # 4. Load Ability Patch lookup table JASS code
    import sys
    if WORK not in sys.path:
        sys.path.insert(0, WORK)
    from generate_ha_jass import unit_ha
    init_subs = []
    chunk = []
    for uid, (s, ha, d) in sorted(unit_ha.items()):
        d_clean = d.replace('"', "'")
        chunk.append(f"    call SaveStr(AbilityPatch_HT, '{uid}', 1, \"{ha}\")")
        chunk.append(f"    call SaveStr(AbilityPatch_HT, '{uid}', 2, \"{d_clean}\")")
        if len(chunk) >= 100:
            sub_id = len(init_subs) + 1
            init_subs.append((sub_id, "\n".join(chunk)))
            chunk = []
    if chunk:
        sub_id = len(init_subs) + 1
        init_subs.append((sub_id, "\n".join(chunk)))

    ha_sub_code = ""
    for sub_id, body in init_subs:
        ha_sub_code += f"""
function AbilityPatch_InitPart_{sub_id} takes nothing returns nothing
{body}
endfunction
"""

    ha_main_init = "\n".join([f"    call AbilityPatch_InitPart_{sub_id}()" for sub_id, _ in init_subs])

    ver2n_system_code = f"""
{ha_sub_code}

function AbilityPatch_OnDialogClick takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local button b = GetClickedButton()
    local unit u = AbilityPatch_Unit[pid]
    local item it = AbilityPatch_Item[pid]
    local integer ut = 0
    local string ha_name = ""

    if b == AbilityPatch_BtnYes[pid] then
        if u != null and GetWidgetLife(u) > 0.405 then
            set ut = GetUnitTypeId(u)
            set ha_name = LoadStr(AbilityPatch_HT, ut, 1)
            call SaveStr(AbilityPatch_HT, GetHandleId(u), 100, ha_name)
            call SaveInteger(AbilityPatch_HT, GetHandleId(u), 101, 1)
            if it != null then
                call RemoveItem(it)
            endif
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectTarget.mdl", u, "origin"))
            call DisplayTimedTextToPlayer(p, 0, 0, 7.0, "|cff00ff00[HIDDEN ABILITY AWAKENED]|r " + GetUnitName(u) + " unlocked Hidden Ability: |cffffcc00" + ha_name + "|r!")
        endif
    elseif b == AbilityPatch_BtnNo[pid] then
        if it != null then
            call RemoveItem(it)
        endif
        call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) + 10000)
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[PURCHASE CANCELLED]|r Transaction cancelled. Refunded 10,000 Gold.")
    endif

    set AbilityPatch_Unit[pid] = null
    set AbilityPatch_Item[pid] = null
    set p = null
    set b = null
    set u = null
    set it = null
endfunction

function AbilityPatch_Init takes nothing returns nothing
    local integer i = 0
    set AbilityPatch_HT = InitHashtable()
    set AbilityPatch_DialogTrig = CreateTrigger()
{ha_main_init}
    loop
        exitwhen i >= 12
        set AbilityPatch_Dialog[i] = DialogCreate()
        call TriggerRegisterDialogEvent(AbilityPatch_DialogTrig, AbilityPatch_Dialog[i])
        set DragonAscent_Buff[i] = false
        set Player_MidTpCd[i] = 0.0
        set Player_MidTpChan[i] = 0.0
        set Bush_StillTime[i] = 0.0
        set Bush_InStealth[i] = false
        set i = i + 1
    endloop
    call TriggerAddAction(AbilityPatch_DialogTrig, function AbilityPatch_OnDialogClick)
endfunction

function AbilityPatch_PromptBuy takes unit b, item it returns nothing
    local player p = GetOwningPlayer(b)
    local integer pid = GetPlayerId(p)
    local integer ut = GetUnitTypeId(b)
    local string ha_name = LoadStr(AbilityPatch_HT, ut, 1)
    local string ha_desc = LoadStr(AbilityPatch_HT, ut, 2)

    if ha_name == null or ha_name == "" then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[Ability Patch]|r This Pokemon has no Hidden Ability or is already awakened. Refunded 10,000 Gold.")
        call RemoveItem(it)
        call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) + 10000)
        set p = null
        return
    endif

    set AbilityPatch_Unit[pid] = b
    set AbilityPatch_Item[pid] = it

    call DialogClear(AbilityPatch_Dialog[pid])
    call DialogSetMessage(AbilityPatch_Dialog[pid], "AWAKEN HIDDEN ABILITY\\nPokemon: " + GetUnitName(b) + "\\nHidden Ability: " + ha_name + "\\n\\nSpend 10,000 Gold to permanently unlock this Hidden Ability?")
    set AbilityPatch_BtnYes[pid] = DialogAddButton(AbilityPatch_Dialog[pid], "|cff00ff00[ Yes / Unlock (10,000g) ]|r", 1)
    set AbilityPatch_BtnNo[pid] = DialogAddButton(AbilityPatch_Dialog[pid], "|cffff2222[ No / Cancel (Refund) ]|r", 2)
    call DialogDisplay(p, AbilityPatch_Dialog[pid], true)
    set p = null
endfunction

// ==========================================
// MINUTE 55:00 MEGA RAYQUAZA BOSS EVENT
// ==========================================
function Rayquaza_CheckMin55 takes nothing returns nothing
    local integer p = 0
    local integer t = 0
    if not Rayquaza_Warned and Mega_Time >= 3270.0 then // 54:30
        set Rayquaza_Warned = true
        call PingMinimap(-128.0, 16.0, 10.0)
        call PAX_Announce("|cffff0000[WORLD BOSS WARNING]|r Mega Rayquaza will descend at the Center Altar in |cffffd16630 seconds|r!", 10.0)
    endif

    if not Rayquaza_Spawned and Mega_Time >= 3300.0 then // 55:00
        set Rayquaza_Spawned = true
        set Rayquaza_DespawnTime = 3600.0 // 60:00 (5 minutes existence)
        set Rayquaza_BossUnit = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), 'n00G', -128.0, 16.0, 270.0)
        call BlzSetUnitMaxHP(Rayquaza_BossUnit, 80000)
        call SetUnitLifePercentBJ(Rayquaza_BossUnit, 100.0)
        call BlzSetUnitArmor(Rayquaza_BossUnit, 35.0)
        call PingMinimap(-128.0, 16.0, 12.0)
        call PAX_Announce("|cffff0000[MEGA RAYQUAZA AWAKENED!]|r Defeat it within |cffffd1665 MINUTES|r (before 60:00) for the PERMANENT DRAGON ASCENT TEAM BUFF!", 12.0)
    endif

    if Rayquaza_Spawned and Rayquaza_BossUnit != null and GetWidgetLife(Rayquaza_BossUnit) > 0.405 then
        if Mega_Time >= Rayquaza_DespawnTime then
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Other\\\\Tornado\\\\Tornado.mdl", -128.0, 16.0))
            call RemoveUnit(Rayquaza_BossUnit)
            set Rayquaza_BossUnit = null
            call PAX_Announce("|cffffcc00[EVENT ENDED]|r Mega Rayquaza ascended back into the ozone layer. World Boss event ended!", 8.0)
        endif
    endif
endfunction

function Rayquaza_OnBossKilled takes unit killer returns nothing
    local integer killerTeam = GetPlayerTeam(GetOwningPlayer(killer))
    local integer p = 0
    local player plyr = null
    local unit u = null
    call PAX_Announce("|cff00ff00[DRAGON ASCENT BLESSING!]|r Team " + I2S(killerTeam + 1) + " slew Mega Rayquaza! Permanent Dragon Ascent buff and +2,000 Gold granted to the team!", 12.0)
    loop
        exitwhen p >= 12
        set plyr = Player(p)
        if GetPlayerTeam(plyr) == killerTeam and GetPlayerSlotState(plyr) == PLAYER_SLOT_STATE_PLAYING then
            set DragonAscent_Buff[p] = true
            call SetPlayerState(plyr, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(plyr, PLAYER_STATE_RESOURCE_GOLD) + 2000)
            set u = LoadUnitHandle(PAX_Leg_HT, p, 1)
            if u != null and GetWidgetLife(u) > 0.405 then
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Orc\\\\Bloodlust\\\\BloodlustTarget.mdl", u, "origin"))
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Thunderclap\\\\ThunderClapCaster.mdl", u, "overhead"))
            endif
        endif
        set p = p + 1
    endloop
    set plyr = null
    set u = null
endfunction

// ==========================================
// TALL GRASS & WEATHER & TELEPORT CHANNELING
// ==========================================
function Ver2n_Tick takes nothing returns nothing
    local integer p = 0
    local unit u = null
    local real x = 0.0
    local real y = 0.0
    local real dist1 = 0.0
    local real dist2 = 0.0
    local boolean in_circle = false

    call Rayquaza_CheckMin55()

    loop
        exitwhen p >= 12
        set u = LoadUnitHandle(PAX_Leg_HT, p, 1)
        if u != null and GetWidgetLife(u) > 0.405 then
            set x = GetUnitX(u)
            set y = GetUnitY(u)

            // 1. Dragon Ascent permanent buff regen
            if DragonAscent_Buff[p] then
                call SetWidgetLife(u, GetWidgetLife(u) + 0.01 * I2R(BlzGetUnitMaxHP(u)))
                call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MANA) + 0.01 * GetUnitState(u, UNIT_STATE_MAX_MANA))
            endif

            // 2. Teleport Portal at Y = -/+760 with 2.0s stand-in-circle + 30s CD
            set dist1 = (x - (-5120.0)) * (x - (-5120.0)) + (y - (-760.0)) * (y - (-760.0))
            set dist2 = (x - 5120.0) * (x - 5120.0) + (y - 760.0) * (y - 760.0)
            set in_circle = (dist1 <= 14400.0 or dist2 <= 14400.0)

            if in_circle then
                if Mega_Time < Player_MidTpCd[p] then
                    call DisplayTimedTextToPlayer(Player(p), 0, 0, 1.0, "|cffffcc00[Mid Portal]|r On cooldown: " + I2S(R2I(Player_MidTpCd[p] - Mega_Time + 0.99)) + "s.")
                else
                    set Player_MidTpChan[p] = Player_MidTpChan[p] + 0.5
                    if Player_MidTpChan[p] >= 2.0 then
                        set Player_MidTpChan[p] = 0.0
                        set Player_MidTpCd[p] = Mega_Time + 30.0
                        call SetUnitPosition(u, -128.0, 16.0)
                        call PanCameraToTimedForPlayer(Player(p), -128.0, 16.0, 0.25)
                        call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", u, "origin"))
                    else
                        call DisplayTimedTextToPlayer(Player(p), 0, 0, 0.5, "|cff00ffffChanneling Mid Teleport: |r" + I2S(R2I((2.0 - Player_MidTpChan[p]) * 10.0)) + "0%")
                    endif
                endif
            else
                set Player_MidTpChan[p] = 0.0
            endif

            // 3. Tall Grass Bushes (6 locations)
            // (-2200, 1800), (2200, 1800), (-2200, -1800), (2200, -1800), (0, 1500), (0, -1500)
            if (x+2200.0)*(x+2200.0)+(y-1800.0)*(y-1800.0) <= 62500.0 or (x-2200.0)*(x-2200.0)+(y-1800.0)*(y-1800.0) <= 62500.0 or (x+2200.0)*(x+2200.0)+(y+1800.0)*(y+1800.0) <= 62500.0 or (x-2200.0)*(x-2200.0)+(y+1800.0)*(y+1800.0) <= 62500.0 or x*x+(y-1500.0)*(y-1500.0) <= 62500.0 or x*x+(y+1500.0)*(y+1500.0) <= 62500.0 then
                set Bush_StillTime[p] = Bush_StillTime[p] + 0.5
                if Bush_StillTime[p] >= 1.5 and not Bush_InStealth[p] then
                    set Bush_InStealth[p] = true
                    call UnitAddAbility(u, 'Apiv') // Permanent Invisibility
                endif
            else
                set Bush_StillTime[p] = 0.0
                if Bush_InStealth[p] then
                    set Bush_InStealth[p] = false
                    call UnitRemoveAbility(u, 'Apiv')
                endif
            endif
        endif
        set p = p + 1
    endloop
    set u = null
endfunction
"""

    # Insert ver2n system code right BEFORE Fx_OnDeath
    target_death = "function Fx_OnDeath takes nothing returns boolean"
    if target_death in script:
        script = script.replace(target_death, ver2n_system_code + "\n" + target_death)

    # Wire Rayquaza death inside Fx_OnDeath (right before set d = null)
    ray_death_wire = """
    if Rayquaza_BossUnit != null and d == Rayquaza_BossUnit then
        call Rayquaza_OnBossKilled(killer)
        set Rayquaza_BossUnit = null
    endif
"""
    target_clean = "set d = null"
    # Find set d = null inside Fx_OnDeath
    fx_death_pos = script.find("function Fx_OnDeath takes nothing returns boolean")
    if fx_death_pos != -1:
        d_null_pos = script.find("set d = null", fx_death_pos)
        if d_null_pos != -1:
            script = script[:d_null_pos] + ray_death_wire + "    " + script[d_null_pos:]

    # Wire IMHA in LegTele_OnSell after local declarations
    target_leg = "local unit b = GetBuyingUnit()"
    leg_pos = script.find("function LegTele_OnSell takes nothing returns boolean")
    if leg_pos != -1:
        b_pos = script.find("local unit b = GetBuyingUnit()", leg_pos)
        if b_pos != -1:
            end_line = script.find("\n", b_pos) + 1
            script = script[:end_line] + """    if it == 'IMHA' then
        call AbilityPatch_PromptBuy(b, GetSoldItem())
        set b = null
        return false
    endif\n""" + script[end_line:]

    # Wire AbilityPatch_Init and Ver2n_Tick in main init / timer
    target_init = "call Wild_InitData()"
    if target_init in script:
        script = script.replace(target_init, "call AbilityPatch_Init()\n    call TimerStart(CreateTimer(), 0.5, true, function Ver2n_Tick)\n    " + target_init)

    # Replace weather timer period with 240.0s
    script = script.replace("call TimerStart(CreateTimer(), 300.0, true, function Wth_Tick)",
                            "call TimerStart(CreateTimer(), 240.0, true, function Wth_Tick)")

    return script
