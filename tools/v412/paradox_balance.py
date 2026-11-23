"""Paradox Balance & Mid-Game Progression Module for Pokemon Arena v4.1.2:
1. NON-LEGEND PARADOX ABILITY LOCKING:
   - Non-legend Paradox Pokemon (Roaring Moon, Sandy Shocks, Flutter Mane, Scream Tail,
     Iron Thorns, Iron Valiant, Iron Jugulis) now have their passives LOCKED initially.
   - Registered in PAX_Leg_Index (indices 26..32) and must complete Awakening Quest (-quest)
     to unlock their full Paradox procs and stat bonuses.
   - Removed automatic bypass 'if PAX_Form_Id(u) >= 13 then return true endif' from PAX_Leg_Awakened.
   - Added awakened check to PAX_Paradox_Proc.
2. QUEST 3 ALTAR RESCUE & ANTI-CAMPING:
   - Ritual duration reduced from 60s to 30s.
   - SANCTUARY WARD (Buff Bảo Hộ) while channeling in Center Altar:
     +30 Armor, +20% Magic Resistance (-20% skill damage), and +3% Max HP/s Regeneration!
     Prevents channeling hero from getting bursted down in a single split-second combo.
     Automatically removed when leaving the Altar circle.
   - Removed -2s/s progress decay on retreat: cumulative progress is preserved!
   - Removed enemy minimap pings and broadcast alerts to prevent altar ganking.
   - DUAL-PATH PvE COMPLETION: Defeating 1 Legend Boss (+30s) or 2 Wild Elites (+15s each)
     also grants Stage 3 completion, completely breaking altar monopoly camping!
3. MID-GAME PACING:
   - Mega Evolution unlocked after Gym 4 (Badge_Count >= 4, Cap Lv 50).
   - Paradox & Form Boosters unlocked after Gym 6 (Badge_Count >= 6, Cap Lv 70).
   - Paradox items price reduced from 10,000g to 6,500g.
   - Awakening Quest requirement lowered from Lv 85/95 to Lv 65/75.
"""

def patch_script(s: str) -> str:
    # 1. Update PAX_Leg_Index with non-legend Paradox Pokemon (indices 26..32)
    old_leg_index = '''    elseif id == 'E02A' then
        return 24
    elseif id == 'P0JA' then
        return 25
    endif
    return 0
endfunction'''

    new_leg_index = '''    elseif id == 'E02A' then
        return 24
    elseif id == 'P0JA' then
        return 25
    elseif id == 'EN0F' then
        return 26
    elseif id == 'E032' or id == 'P4XA' or id == 'P2LA' then
        return 27
    elseif id == 'P2UA' or id == 'P2VA' then
        return 28
    elseif id == 'P20A' or id == 'P4IA' then
        return 29
    elseif id == 'EN08' then
        return 30
    elseif id == 'EN0B' or id == 'EN0C' then
        return 31
    elseif id == 'P1YA' then
        return 32
    endif
    return 0
endfunction'''
    if old_leg_index not in s:
        raise SystemExit('paradox_balance: old_leg_index not found')
    s = s.replace(old_leg_index, new_leg_index, 1)

    # 2. Update PAX_Leg_Count to 32
    old_leg_count = '''function PAX_Leg_Count takes nothing returns integer
    return 25
endfunction'''
    new_leg_count = '''function PAX_Leg_Count takes nothing returns integer
    return 32
endfunction'''
    if old_leg_count not in s:
        raise SystemExit('paradox_balance: old_leg_count not found')
    s = s.replace(old_leg_count, new_leg_count, 1)

    # 3. Update PAX_Leg_QKey to 64 slots per player
    old_qkey = '''function PAX_Leg_QKey takes integer pid, integer idx returns integer
    return 1000 + pid * 32 + idx
endfunction'''
    new_qkey = '''function PAX_Leg_QKey takes integer pid, integer idx returns integer
    return 1000 + pid * 64 + idx
endfunction'''
    if old_qkey not in s:
        raise SystemExit('paradox_balance: old_qkey not found')
    s = s.replace(old_qkey, new_qkey, 1)

    # 4. Update PAX_Leg_Name with names for indices 26..32
    old_leg_name = '''    elseif idx == 24 then
        return "Arceus"
    elseif idx == 25 then
        return "Buzzwole"
    endif
    return "Legend"
endfunction'''

    new_leg_name = '''    elseif idx == 24 then
        return "Arceus"
    elseif idx == 25 then
        return "Buzzwole"
    elseif idx == 26 then
        return "Roaring Moon"
    elseif idx == 27 then
        return "Sandy Shocks"
    elseif idx == 28 then
        return "Flutter Mane"
    elseif idx == 29 then
        return "Scream Tail"
    elseif idx == 30 then
        return "Iron Thorns"
    elseif idx == 31 then
        return "Iron Valiant"
    elseif idx == 32 then
        return "Iron Jugulis"
    endif
    return "Legend"
endfunction'''
    if old_leg_name not in s:
        raise SystemExit('paradox_balance: old_leg_name not found')
    s = s.replace(old_leg_name, new_leg_name, 1)

    # 6. Lower Awakening Level Requirement from 85/95 to 65/75
    old_reqlv = '''function PAX_Leg_ReqLv takes integer idx returns integer
    if idx == 4 or idx == 14 or idx == 24 then
        return 95
    endif
    return 85
endfunction'''
    new_reqlv = '''function PAX_Leg_ReqLv takes integer idx returns integer
    if idx == 4 or idx == 14 or idx == 24 then
        return 75
    endif
    return 65
endfunction

function PAX_Leg_Stage3Target takes integer qk returns integer
    if LoadInteger(PAX_Leg_HT, qk, 10) == 1 then
        return 30
    endif
    return 60
endfunction'''
    if old_reqlv not in s:
        raise SystemExit('paradox_balance: old_reqlv not found')
    s = s.replace(old_reqlv, new_reqlv, 1)

    # 6. Lock Non-Legend Paradox in PAX_Leg_Awakened
    old_awakened = '''function PAX_Leg_Awakened takes unit u returns boolean
    local integer idx = 0
    local integer pid = 0
    local integer qk = 0
    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) then
        return false
    endif
    set idx = PAX_Leg_Index(GetUnitTypeId(u))
    set pid = GetPlayerId(GetOwningPlayer(u))
    if pid >= 12 then
        return false
    endif
    if PAX_Form_Id(u) >= 13 then
        return true
    endif
    if idx == 0 then
        return false
    endif
    set qk = PAX_Leg_QKey(pid, idx)
    return LoadInteger(PAX_Leg_HT, qk, 0) == 4
endfunction'''

    new_awakened = '''function PAX_Leg_Awakened takes unit u returns boolean
    local integer idx = 0
    local integer pid = 0
    local integer qk = 0
    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) then
        return false
    endif
    set idx = PAX_Leg_Index(GetUnitTypeId(u))
    set pid = GetPlayerId(GetOwningPlayer(u))
    if pid >= 12 then
        return false
    endif
    // Non-legend Paradox Pokemon must complete Awakening Quest (-quest) just like Legends
    if idx == 0 then
        return false
    endif
    set qk = PAX_Leg_QKey(pid, idx)
    return LoadInteger(PAX_Leg_HT, qk, 0) == 4
endfunction'''
    if old_awakened not in s:
        raise SystemExit('paradox_balance: old_awakened not found')
    s = s.replace(old_awakened, new_awakened, 1)

    # 7. Add Awakened check to PAX_Paradox_Proc
    old_pax_proc = '''function PAX_Paradox_Proc takes unit src, unit tgt, integer formId, boolean moveCast returns nothing
    local integer h = GetHandleId(src)
    local real x = GetUnitX(src)
    local real y = GetUnitY(src)
    local real stat = 0.0
    local real icd = 3.0
    if PAX_Leg_InProc or (moveCast and formId != 16 and formId != 19) or (tgt == null and not moveCast) then
        return
    endif'''

    new_pax_proc = '''function PAX_Paradox_Proc takes unit src, unit tgt, integer formId, boolean moveCast returns nothing
    local integer h = GetHandleId(src)
    local real x = GetUnitX(src)
    local real y = GetUnitY(src)
    local real stat = 0.0
    local real icd = 3.0
    if not PAX_Leg_Awakened(src) then
        return
    endif
    if PAX_Leg_InProc or (moveCast and formId != 16 and formId != 19) or (tgt == null and not moveCast) then
        return
    endif'''
    if old_pax_proc not in s:
        raise SystemExit('paradox_balance: old_pax_proc not found')
    s = s.replace(old_pax_proc, new_pax_proc, 1)

    # 8. Define Sanctuary Ward functions BEFORE PAX_Leg_OnKillProgress
    old_before_kill = '''function PAX_Leg_OnKillProgress takes unit killer, unit dead, boolean isWild, boolean isElite, boolean isLegend returns nothing'''

    new_before_kill = '''function PAX_Sanctuary_Remove takes unit u returns nothing
    local integer h = 0
    local effect fx = null
    if u == null then
        return
    endif
    set h = GetHandleId(u)
    if LoadInteger(PAX_Leg_HT, h, 182) == 1 then
        call SaveInteger(PAX_Leg_HT, h, 182, 0)
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - 30.0)
        set fx = LoadEffectHandle(PAX_Leg_HT, h, 184)
        if fx != null then
            call DestroyEffect(fx)
            call RemoveSavedHandle(PAX_Leg_HT, h, 184)
        endif
        call PAX_Leg_Float(u, "Sanctuary Lost", 200, 200, 200, GetOwningPlayer(u), GetOwningPlayer(u))
    endif
    set fx = null
endfunction

function PAX_Sanctuary_Apply takes unit u returns nothing
    local integer h = 0
    local effect fx = null
    local player p = null
    if u == null or GetWidgetLife(u) <= 0.405 then
        return
    endif
    set h = GetHandleId(u)
    set p = GetOwningPlayer(u)
    // If not already active, grant +30 armor and divine visual barrier
    if LoadInteger(PAX_Leg_HT, h, 182) == 0 then
        call SaveInteger(PAX_Leg_HT, h, 182, 1)
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + 30.0)
        set fx = AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\DivineShield\\\\DivineShieldTarget.mdl", u, "origin")
        call SaveEffectHandle(PAX_Leg_HT, h, 184, fx)
        call PAX_Leg_Float(u, "|cffffd700Sanctuary Ward (+30 Def / -20% Magic / +3% HP/s)|r", 255, 215, 0, p, p)
    endif
    // Regenerate 3% Max HP per second
    call PAX_HealUnit(u, 0.03 * I2R(BlzGetUnitMaxHP(u)))
    // Refresh magic resistance active timestamp
    call SaveReal(PAX_Leg_HT, h, 183, Mega_Time + 1.5)
    set p = null
    set fx = null
endfunction

function PAX_Leg_OnKillProgress takes unit killer, unit dead, boolean isWild, boolean isElite, boolean isLegend returns nothing'''
    if old_before_kill not in s:
        raise SystemExit('paradox_balance: old_before_kill not found')
    s = s.replace(old_before_kill, new_before_kill, 1)

    # 9. Permanent 30s target on Legend Kill & Stage progression in PAX_Leg_OnKillProgress
    old_kill_prog = '''    elseif stage == 2 then
        if isLegend then
            set add = 6
        elseif enemyHero then
            set add = 3
        elseif isElite then
            set add = 2
        endif
        if add > 0 then
            set pts = LoadInteger(PAX_Leg_HT, qk, 3) + add
            if pts >= 6 then
                call SaveInteger(PAX_Leg_HT, qk, 3, 6)
                call SaveInteger(PAX_Leg_HT, qk, 0, 3)
                call SaveInteger(PAX_Leg_HT, qk, 4, 0)
                call SaveInteger(PAX_Leg_HT, qk, 6, 0)
                set p = GetOwningPlayer(killer)
                call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffd896ff[STAGE 2 COMPLETE]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Stage 3: hold the Awakening Ritual at the Center Altar for|r |cffffd16660s|r!")
                set p = null
            else
                call SaveInteger(PAX_Leg_HT, qk, 3, pts)
            endif
        endif
    endif
endfunction'''

    new_kill_prog = '''    elseif stage == 2 then
        // If killing a Legend Boss, permanently reduce Stage 3 target to 30s (Key 10 = 1, preserved across deaths!)
        if isLegend and LoadInteger(PAX_Leg_HT, qk, 10) == 0 then
            call SaveInteger(PAX_Leg_HT, qk, 10, 1)
            set p = GetOwningPlayer(killer)
            call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffd896ff[LEGEND HUNT]|r Defeated Legend Boss! Stage 3 Ritual target permanently reduced from 60s to |cffffd16630s|r!")
            set p = null
        endif
        if isLegend then
            set add = 6
        elseif enemyHero then
            set add = 3
        elseif isElite then
            set add = 2
        endif
        if add > 0 then
            set pts = LoadInteger(PAX_Leg_HT, qk, 3) + add
            if pts >= 6 then
                call SaveInteger(PAX_Leg_HT, qk, 3, 6)
                call SaveInteger(PAX_Leg_HT, qk, 0, 3)
                call SaveInteger(PAX_Leg_HT, qk, 4, 0)
                call SaveInteger(PAX_Leg_HT, qk, 6, 0)
                set p = GetOwningPlayer(killer)
                if PAX_Leg_Stage3Target(qk) == 30 then
                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffd896ff[STAGE 2 COMPLETE]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Stage 3: Hold Ritual at Center Altar (|cffffd16630s|r [Legend Hunt active])!|r")
                else
                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffd896ff[STAGE 2 COMPLETE]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Stage 3: Hold Ritual at Center Altar (60s) OR defeat 1 Legend Boss to reduce target to |cffffd16630s|r!|r")
                endif
                set p = null
            else
                call SaveInteger(PAX_Leg_HT, qk, 3, pts)
            endif
        endif
    elseif stage == 3 then
        if isLegend and LoadInteger(PAX_Leg_HT, qk, 10) == 0 then
            call SaveInteger(PAX_Leg_HT, qk, 10, 1)
            set p = GetOwningPlayer(killer)
            call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffd896ff[LEGEND HUNT]|r Defeated Legend Boss! Stage 3 Ritual target permanently reduced from 60s to |cffffd16630s|r!")
            set p = null
        endif
        set pts = LoadInteger(PAX_Leg_HT, qk, 4)
        if pts >= PAX_Leg_Stage3Target(qk) then
            call SaveInteger(PAX_Leg_HT, qk, 4, PAX_Leg_Stage3Target(qk))
            call SaveInteger(PAX_Leg_HT, qk, 0, 4)
            call SaveInteger(PAX_Leg_HT, qk, 6, 0)
            set p = GetOwningPlayer(killer)
            call PAX_Sanctuary_Remove(killer)
            call PAX_Celebrate(killer, "Awakened!", "Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectCaster.mdl")
            call PAX_MajorEvent("|cffd896ff", "[AWAKENING COMPLETE]", "|cff7dd3fc" + GetPlayerName(p) + "|r's |cffffd166" + PAX_Leg_Name(idx) + "|r has awakened its Hidden Power!", 12.0)
            call PAX_Leg_Sync(killer)
            set p = null
        endif
    endif
endfunction'''
    if old_kill_prog not in s:
        raise SystemExit('paradox_balance: old_kill_prog not found')
    s = s.replace(old_kill_prog, new_kill_prog, 1)

    # 10. In PAX_Leg_ModifyIncoming: apply +20% magic resistance
    old_bless_check = '''    if IsUnitType(tgt, UNIT_TYPE_HERO) and (atk or skill) and dmg > 0.0 and Mega_Time < LoadReal(PAX_Leg_HT, h, 125) then
        set dmg = dmg * (1.0 - LoadReal(PAX_Leg_HT, h, 126))
    endif'''
    new_bless_check = '''    if IsUnitType(tgt, UNIT_TYPE_HERO) and (atk or skill) and dmg > 0.0 and Mega_Time < LoadReal(PAX_Leg_HT, h, 125) then
        set dmg = dmg * (1.0 - LoadReal(PAX_Leg_HT, h, 126))
    endif
    // Sanctuary Ward: +20% Magic Resistance (reduces skill/spell damage by 20%)
    if skill and LoadInteger(PAX_Leg_HT, h, 182) == 1 and Mega_Time <= LoadReal(PAX_Leg_HT, h, 183) then
        set dmg = dmg * 0.80
    endif'''
    if old_bless_check not in s:
        raise SystemExit('paradox_balance: old_bless_check not found')
    s = s.replace(old_bless_check, new_bless_check, 1)

    # 11. Quest 3 Altar Rescue in PAX_Leg_Tick1s: 30s target, cumulative (no decay), stealth pings, Sanctuary Ward buff
    old_stage3_tick = '''                    elseif stage == 3 then
                        set dx = GetUnitX(u) + 128.0
                        set dy = GetUnitY(u) - 16.0
                        set dist = SquareRoot(dx * dx + dy * dy)
                        if dist <= 450.0 then
                            if LoadInteger(PAX_Leg_HT, qk, 6) == 0 then
                                call SaveInteger(PAX_Leg_HT, qk, 6, 1)
                                call SaveReal(PAX_Leg_HT, qk, 5, Mega_Time - 4.0)
                                call PingMinimap(-128.0, 16.0, 6.0)
                                call PAX_Announce("|cffff5c5c[RITUAL]|r |cff7dd3fc" + GetPlayerName(p) + "|r (|cffffd166" + PAX_Leg_Name(idx) + "|r) |cffe8ecf2started Awakening at the Center Altar!|r", 10.0)
                            endif
                            set sec = LoadInteger(PAX_Leg_HT, qk, 4) + 1
                            call SaveInteger(PAX_Leg_HT, qk, 4, sec)
                            call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\HolyBolt\\\\HolyBoltSpecialArt.mdl", u, "origin"))
                            call PAX_Leg_Float(u, "Ritual: " + I2S(sec) + "/60s", 255, 210, 80, p, p)
                            if Mega_Time - LoadReal(PAX_Leg_HT, qk, 5) >= 4.0 then
                                call SaveReal(PAX_Leg_HT, qk, 5, Mega_Time)
                                call PingMinimap(-128.0, 16.0, 4.0)
                            endif
                            if sec >= 60 then
                                call SaveInteger(PAX_Leg_HT, qk, 4, 60)
                                call SaveInteger(PAX_Leg_HT, qk, 0, 4)
                                call SaveInteger(PAX_Leg_HT, qk, 6, 0)
                                call PAX_Celebrate(u, "Awakened!", "Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectCaster.mdl")
                                call PAX_MajorEvent("|cffd896ff", "[AWAKENING COMPLETE]", "|cff7dd3fc" + GetPlayerName(p) + "|r's |cffffd166" + PAX_Leg_Name(idx) + "|r has awakened its Hidden Power!", 12.0)
                                call PAX_Leg_Sync(u)
                            endif
                        elseif dist > 550.0 and LoadInteger(PAX_Leg_HT, qk, 4) > 0 then
                            set sec = LoadInteger(PAX_Leg_HT, qk, 4) - 2
                            if sec < 0 then
                                set sec = 0
                            endif
                            call SaveInteger(PAX_Leg_HT, qk, 4, sec)
                            if sec == 0 then
                                call SaveInteger(PAX_Leg_HT, qk, 6, 0)
                            endif
                        endif
                    endif'''

    new_stage3_tick = '''                    elseif stage == 3 then
                        set dx = GetUnitX(u) + 128.0
                        set dy = GetUnitY(u) - 16.0
                        set dist = SquareRoot(dx * dx + dy * dy)
                        if dist <= 450.0 then
                            call PAX_Sanctuary_Apply(u)
                            if LoadInteger(PAX_Leg_HT, qk, 6) == 0 then
                                call SaveInteger(PAX_Leg_HT, qk, 6, 1)
                                call SaveReal(PAX_Leg_HT, qk, 5, Mega_Time - 4.0)
                                if GetLocalPlayer() == p then
                                    call PingMinimap(-128.0, 16.0, 6.0)
                                endif
                                call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffd896ff[RITUAL]|r |cffe8ecf2Awakening Ritual started! |cffffd700Sanctuary Ward active (+30 Armor, +20% Magic Res, +3% HP/s)|r (" + I2S(PAX_Leg_Stage3Target(qk)) + "s required)...|r")
                            endif
                            set sec = LoadInteger(PAX_Leg_HT, qk, 4) + 1
                            call SaveInteger(PAX_Leg_HT, qk, 4, sec)
                            call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\HolyBolt\\\\HolyBoltSpecialArt.mdl", u, "origin"))
                            call PAX_Leg_Float(u, "Ritual: " + I2S(sec) + "/" + I2S(PAX_Leg_Stage3Target(qk)) + "s", 255, 210, 80, p, p)
                            if sec >= PAX_Leg_Stage3Target(qk) then
                                call PAX_Sanctuary_Remove(u)
                                call SaveInteger(PAX_Leg_HT, qk, 4, PAX_Leg_Stage3Target(qk))
                                call SaveInteger(PAX_Leg_HT, qk, 0, 4)
                                call SaveInteger(PAX_Leg_HT, qk, 6, 0)
                                call PAX_Celebrate(u, "Awakened!", "Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectCaster.mdl")
                                call PAX_MajorEvent("|cffd896ff", "[AWAKENING COMPLETE]", "|cff7dd3fc" + GetPlayerName(p) + "|r's |cffffd166" + PAX_Leg_Name(idx) + "|r has awakened its Hidden Power!", 12.0)
                                call PAX_Leg_Sync(u)
                            endif
                        else
                            call PAX_Sanctuary_Remove(u)
                        endif
                    else
                        call PAX_Sanctuary_Remove(u)
                    endif'''
    if old_stage3_tick not in s:
        raise SystemExit('paradox_balance: old_stage3_tick not found')
    s = s.replace(old_stage3_tick, new_stage3_tick, 1)

    # 12. In PAX_Leg_Tick1s: Cleanup sanctuary for dead heroes or idx == 0
    old_dead_clean = '''            if IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then'''
    new_dead_clean = '''            if IsUnitType(u, UNIT_TYPE_HERO) then
                if GetWidgetLife(u) <= 0.405 then
                    call PAX_Sanctuary_Remove(u)
                endif
            endif
            if IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then'''
    if old_dead_clean not in s:
        raise SystemExit('paradox_balance: old_dead_clean not found')
    s = s.replace(old_dead_clean, new_dead_clean, 1)

    # 13. Update PAX_Leg_QuestCmd text to mention Sanctuary Ward and dynamic 30s/60s target
    old_quest_cmd = '''                elseif stage == 3 then
                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff66cc[Stage 3/3]|r Ritual |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 4)) + "/60s|r at the Awakening Altar (Center).")'''
    new_quest_cmd = '''                elseif stage == 3 then
                    if PAX_Leg_Stage3Target(qk) == 30 then
                        call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff66cc[Stage 3/3]|r Ritual |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 4)) + "/30s|r at Center Altar [Sanctuary Ward active] (|cffffd166Legend Hunt active: 30s target!|r)")
                    else
                        call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff66cc[Stage 3/3]|r Ritual |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 4)) + "/60s|r at Center Altar [Sanctuary Ward active] (Defeat 1 Legend Boss to reduce target to 30s permanently!)")
                    endif'''
    if old_quest_cmd not in s:
        raise SystemExit('paradox_balance: old_quest_cmd not found')
    s = s.replace(old_quest_cmd, new_quest_cmd, 1)

    # 14. Mid-game badge checks in Fx_PickupGo (Mega at Gym 4, Paradox at Gym 6)
    old_pickup_go = '''        if PAX_Form_ItemIndex(id) >= 8 and GetPlayerId(po) < 12 and Badge_Count(GetPlayerId(po)) < 8 then
            if LoadInteger(Fx_HT, GetHandleId(it), 1) == 1 then
                call AdjustPlayerStateBJ(LoadInteger(Fx_HT, id, 3), po, PLAYER_STATE_RESOURCE_GOLD)
                call RemoveItem(it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[PARADOX]|r You must clear all |cffffd1668 Gyms|r (" + I2S(Badge_Count(GetPlayerId(po))) + "/8) before buying Paradox Booster Energy! Gold refunded.")
            else
                call UnitRemoveItem(u, it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[PARADOX]|r You must clear all |cffffd1668 Gyms|r (" + I2S(Badge_Count(GetPlayerId(po))) + "/8) to hold Paradox Booster Energy!")
            endif
            call Itm_Refresh(u)
            call FlushChildHashtable(Fx_HT, k)
            call DestroyTimer(tm)
            set tm = null
            set u = null
            set it = null
            set po = null
            return
        endif'''

    new_pickup_go = '''        if Mega_IndexOfStone(id) >= 0 and GetPlayerId(po) < 12 and Badge_Count(GetPlayerId(po)) < 4 then
            if LoadInteger(Fx_HT, GetHandleId(it), 1) == 1 then
                call AdjustPlayerStateBJ(LoadInteger(Fx_HT, id, 3), po, PLAYER_STATE_RESOURCE_GOLD)
                call RemoveItem(it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[MEGA]|r You must clear Gym 4 (" + I2S(Badge_Count(GetPlayerId(po))) + "/4) before buying a Mega Stone! Gold refunded.")
            else
                call UnitRemoveItem(u, it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[MEGA]|r You must clear Gym 4 (" + I2S(Badge_Count(GetPlayerId(po))) + "/4) to hold a Mega Stone!")
            endif
            call Itm_Refresh(u)
            call FlushChildHashtable(Fx_HT, k)
            call DestroyTimer(tm)
            set tm = null
            set u = null
            set it = null
            set po = null
            return
        endif
        if PAX_Form_ItemIndex(id) >= 8 and GetPlayerId(po) < 12 and Badge_Count(GetPlayerId(po)) < 6 then
            if LoadInteger(Fx_HT, GetHandleId(it), 1) == 1 then
                call AdjustPlayerStateBJ(LoadInteger(Fx_HT, id, 3), po, PLAYER_STATE_RESOURCE_GOLD)
                call RemoveItem(it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[PARADOX]|r You must clear Gym 6 (" + I2S(Badge_Count(GetPlayerId(po))) + "/6) before buying Paradox Booster Energy! Gold refunded.")
            else
                call UnitRemoveItem(u, it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffff5c5c[PARADOX]|r You must clear Gym 6 (" + I2S(Badge_Count(GetPlayerId(po))) + "/6) to hold Paradox Booster Energy!")
            endif
            call Itm_Refresh(u)
            call FlushChildHashtable(Fx_HT, k)
            call DestroyTimer(tm)
            set tm = null
            set u = null
            set it = null
            set po = null
            return
        endif'''
    if old_pickup_go not in s:
        raise SystemExit('paradox_balance: old_pickup_go not found')
    s = s.replace(old_pickup_go, new_pickup_go, 1)

    # 15. Check Badge in Mega_CanStart
    old_can_start = '''    if LoadInteger(Mega_HT, h, 0) > 0 then
        return "|cffff66ccMega refused: already in Mega form|r"
    endif'''
    new_can_start = '''    if Badge_Count(GetPlayerId(GetOwningPlayer(u))) < 4 then
        return "|cffff66ccMega Evolution requires at least 4 Gym Badges.|r"
    endif
    if LoadInteger(Mega_HT, h, 0) > 0 then
        return "|cffff66ccMega refused: already in Mega form|r"
    endif'''
    if old_can_start not in s:
        raise SystemExit('paradox_balance: old_can_start not found')
    s = s.replace(old_can_start, new_can_start, 1)

    # 16. Paradox item price in Fx_Data6: User requested to keep the original 10,000g price
    # for itid in ['IM18', 'IM19', 'IM1A', 'IM1B', 'IM1C', 'IM1D', 'IM1E', 'IM1F', 'IM1G', 'IM1H']:
    #     s = s.replace(f"call SaveInteger(Fx_HT, '{itid}', 3, 10000)", f"call SaveInteger(Fx_HT, '{itid}', 3, 6500)")

    return s
