"""Generates JASS code for developer test commands:
- `-gen <1..4>`: Clears all wild creeps, spawns all Pokemon of that Gen on the arena field with floating labels.
- `-c <dex/name/rawcode>`: Transforms current hero into any Pokemon at Level 1.
- `-change <dex/name/rawcode>`: Alias of -c.
- `-nolvl` / `-freelvl` / `-lvlcap`: Toggles level cap rule on/off so Pokemon can level freely without gym badges.
- `-lvl <n>`: Instantly sets hero level to n.
- `-clear`: Cleans up all showcase units and text tags.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, HERE)

import gen14_expansion

def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[test_commands] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)

def build_test_commands_jass() -> tuple[str, str, list[str]]:
    with open(r"C:\Users\quocc\.gemini\antigravity\brain\03a56bef-3330-47b8-96ec-b770b628188f\scratch\gen14_inventory.json", "r", encoding="utf-8") as f:
        inv = json.load(f)

    dex_to_hero = {}
    dex_to_name = {}

    for ds, lst in inv.get("in_map", {}).items():
        d = int(ds)
        hid, nm = lst[0]
        dex_to_hero[d] = hid
        dex_to_name[d] = nm

    for sp in gen14_expansion.load_species_entries():
        d = sp["dex"]
        dex_to_hero[d] = sp["hero"]
        dex_to_name[d] = sp["name"]

    import legend_expansion_data
    for lg in legend_expansion_data.NEW_LEGENDS:
        d = lg["dex"]
        dex_to_hero[d] = lg["hero"]
        dex_to_name[d] = lg["name"]

    ALL_LEGEND_DEXES = [
        # Gen 1
        144, 145, 146, 150, 151,
        # Gen 2
        243, 244, 245, 249, 250, 251,
        # Gen 3
        377, 378, 379, 380, 382, 383, 384, 385, 386,
        # Gen 4
        480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493,
        # Gen 5 - Gen 8
        494, 643, 644, 646, 649, 716, 717, 718, 719, 720, 721,
        791, 792, 800, 801, 802, 888, 890
    ]
    valid_legends = [d for d in ALL_LEGEND_DEXES if d in dex_to_hero]

    globals_jass = """    // PAX_TestCommands globals
    group PAX_Gen_Group = null
    texttag array PAX_Gen_Tags
    integer PAX_Gen_TagCount = 0
    integer PAX_Gen_TargetLvl = 1
    boolean PAX_NoLevelCap = false
    boolean PAX_Test_NoFx = false
    integer array PAX_Dex_Hero
    string array PAX_Dex_Name
    integer array PAX_Legend_Dex
    integer PAX_Legend_Count = 0
"""

    out = []
    out.append("// ===========================================================================")
    out.append("// PAX_TestCommands: -gen <1..4>, -c <dex/name>, -nolvl, -lvl <n>, -clear")
    out.append("// ===========================================================================")

    init_funcs = []
    chunk_size = 100
    all_dexes = sorted(list(dex_to_hero.keys()))
    num_chunks = (len(all_dexes) + chunk_size - 1) // chunk_size

    for ch_idx in range(num_chunks):
        fn_name = f"PAX_Test_InitData{ch_idx + 1:02d}"
        init_funcs.append(fn_name)
        out.append(f"function {fn_name} takes nothing returns nothing")
        sub_dexes = all_dexes[ch_idx * chunk_size : (ch_idx + 1) * chunk_size]
        for d in sub_dexes:
            hid = dex_to_hero[d]
            nm = dex_to_name[d].replace('"', '').replace('\\', '').strip()
            out.append(f"    set PAX_Dex_Hero[{d}] = '{hid}'")
            out.append(f'    set PAX_Dex_Name[{d}] = "{nm}"')
        out.append("endfunction\n")

    init_funcs.append("PAX_Test_InitLegends")
    out.append("function PAX_Test_InitLegends takes nothing returns nothing")
    for idx, d in enumerate(valid_legends):
        out.append(f"    set PAX_Legend_Dex[{idx}] = {d}")
    out.append(f"    set PAX_Legend_Count = {len(valid_legends)}")
    out.append("endfunction\n")

    out.append("""function PAX_ClearGenTags takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= PAX_Gen_TagCount
        if PAX_Gen_Tags[i] != null then
            call DestroyTextTag(PAX_Gen_Tags[i])
            set PAX_Gen_Tags[i] = null
        endif
        set i = i + 1
    endloop
    set PAX_Gen_TagCount = 0
endfunction

function PAX_ClearAllFieldCreeps takes nothing returns nothing
    local group g = CreateGroup()
    local unit u = null
    local integer c = 0

    // 1. Clear all showcase units in PAX_Gen_Group
    if PAX_Gen_Group != null then
        loop
            set u = FirstOfGroup(PAX_Gen_Group)
            exitwhen u == null
            call GroupRemoveUnit(PAX_Gen_Group, u)
            call RemoveUnit(u)
        endloop
    endif
    call PAX_ClearGenTags()

    // 2. Clear ALL wild creeps & roaming legends across all 52 camps
    call GroupEnumUnitsOfPlayer(g, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if not IsUnitType(u, UNIT_TYPE_STRUCTURE) then
            call RemoveUnit(u)
        endif
    endloop

    // 3. Clear ALL neutral victim units (leftover showcase / test units)
    call GroupEnumUnitsOfPlayer(g, Player(bj_PLAYER_NEUTRAL_VICTIM), null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if not IsUnitType(u, UNIT_TYPE_STRUCTURE) then
            call RemoveUnit(u)
        endif
    endloop

    // 4. Reset & pause all 52 wild camps so creeps do NOT respawn during showcase testing!
    set c = 0
    loop
        exitwhen c >= Wild_CampN
        set Wild_CampAlive[c] = 0
        set Wild_CampDue[c] = 999999.0
        set c = c + 1
    endloop

    call DestroyGroup(g)
    set g = null
    set u = null
endfunction

function PAX_ShowcaseLegends takes player pTrig returns nothing
    local integer i = 0
    local integer d = 0
    local integer col = 0
    local integer row = 0
    local integer perRow = 11
    local real startX = -1380.0
    local real startY = 1450.0
    local real curX = 0.0
    local real curY = 0.0
    local unit u = null
    local texttag tt = null

    // Clean all field creeps and previous showcase models completely
    call PAX_ClearGenTags()
    call PAX_ClearAllFieldCreeps()

    if PAX_Gen_Group == null then
        set PAX_Gen_Group = CreateGroup()
    endif

    set i = 0
    loop
        exitwhen i >= PAX_Legend_Count
        set d = PAX_Legend_Dex[i]
        if d > 0 and PAX_Dex_Hero[d] != 0 then
            set curX = startX + col * 270.0
            set curY = startY - row * 290.0
            set u = CreateUnit(Player(bj_PLAYER_NEUTRAL_VICTIM), PAX_Dex_Hero[d], curX, curY, 270.0)
            if u != null then
                // Set Level 100 for all Legendary Bosses
                call SetHeroLevel(u, 100, false)

                // Apply EXACT Raid Boss Buffs from Leg_Spawn: HP x20, Attack x5, Armor x3
                call BlzSetUnitMaxHP(u, BlzGetUnitMaxHP(u) * 20)
                call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
                call BlzSetUnitBaseDamage(u, BlzGetUnitBaseDamage(u, 0) * 5, 0)
                call BlzSetUnitDiceSides(u, BlzGetUnitDiceSides(u, 0) * 5, 0)
                call BlzSetUnitArmor(u, BlzGetUnitArmor(u) * 3.0)

                call PauseUnit(u, true)
                call SetUnitInvulnerable(u, true)

                // Suppress ambient auras so models are clean to inspect
                call SaveInteger(Ab_HT, GetHandleId(u), 10, 1)
                call SaveInteger(Ab_HT, GetHandleId(u), 124, 1)
                if HaveSavedHandle(Ab_HT, GetHandleId(u), 80) then
                    call DestroyEffect(LoadEffectHandle(Ab_HT, GetHandleId(u), 80))
                    call RemoveSavedHandle(Ab_HT, GetHandleId(u), 80)
                endif

                // Overhead text tag showing full boss stats: Lv 100 Boss, HP, ATK, ARM
                set tt = CreateTextTag()
                if tt != null then
                    call SetTextTagText(tt, "|cffffcc00#" + I2S(d) + " " + PAX_Dex_Name[d] + " [Lv.100 Boss]|r\\n|cffff4444HP: " + I2S(BlzGetUnitMaxHP(u)) + "|r |cffffaa00ATK: " + I2S(BlzGetUnitBaseDamage(u, 0)) + "|r |cff44aaffARM: " + I2S(R2I(BlzGetUnitArmor(u))) + "|r", 0.020)
                    call SetTextTagPos(tt, curX, curY, 65.0)
                    call SetTextTagPermanent(tt, true)
                    call SetTextTagVisibility(tt, true)
                    set PAX_Gen_Tags[PAX_Gen_TagCount] = tt
                    set PAX_Gen_TagCount = PAX_Gen_TagCount + 1
                endif
                call GroupAddUnit(PAX_Gen_Group, u)
            endif
            set col = col + 1
            if col >= perRow then
                set col = 0
                set row = row + 1
            endif
        endif
        set i = i + 1
    endloop

    set u = League_Hero(GetPlayerId(pTrig))
    if u != null and Ab_Alive(u) then
        call SetUnitPosition(u, startX + 5 * 270.0, startY + 180.0)
        call PanCameraToTimedForPlayer(pTrig, startX + 5 * 270.0, startY + 180.0, 0.4)
    endif
    set u = null

    call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cffff66cc[Boss Showcase] All " + I2S(PAX_Legend_Count) + " Legendary Bosses spawned at Lv 100 with Raid Boss Buffs (HP x20, ATK x5, ARM x3)!|r")
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cffffcc00Type -clear to remove showcase, -respawn to restore wild creeps.|r")
endfunction

function PAX_ShowcaseGen takes player pTrig, integer genNum returns nothing
    local integer startDex = 1
    local integer endDex = 151
    local integer d = 0
    local integer col = 0
    local integer row = 0
    local integer perRow = 12
    local real startX = -1430.0
    local real startY = 1450.0
    local real curX = 0.0
    local real curY = 0.0
    local unit u = null
    local texttag tt = null
    local string genTitle = "Gen 1 (Kanto)"

    if genNum == 1 then
        set startDex = 1
        set endDex = 151
        set genTitle = "Gen 1 (Kanto: #001 - #151)"
    elseif genNum == 2 then
        set startDex = 152
        set endDex = 251
        set genTitle = "Gen 2 (Johto: #152 - #251)"
    elseif genNum == 3 then
        set startDex = 252
        set endDex = 386
        set genTitle = "Gen 3 (Hoenn: #252 - #386)"
    elseif genNum == 4 then
        set startDex = 387
        set endDex = 493
        set genTitle = "Gen 4 (Sinnoh: #387 - #493)"
    elseif genNum == 5 then
        call PAX_ShowcaseLegends(pTrig)
        return
    else
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cffff4040Usage: -gen 1, -gen 2, -gen 3, -gen 4, or -legend (-gen 5)|r")
        return
    endif

    // Clean all field creeps and previous showcase models completely
    call PAX_ClearGenTags()
    call PAX_ClearAllFieldCreeps()

    if PAX_Gen_Group == null then
        set PAX_Gen_Group = CreateGroup()
    endif

    set d = startDex
    loop
        exitwhen d > endDex
        if PAX_Dex_Hero[d] != 0 then
            set curX = startX + col * 260.0
            set curY = startY - row * 270.0
            set u = CreateUnit(Player(bj_PLAYER_NEUTRAL_VICTIM), PAX_Dex_Hero[d], curX, curY, 270.0)
            if u != null then
                if PAX_Gen_TargetLvl > 1 then
                    call SetHeroLevel(u, PAX_Gen_TargetLvl, false)
                endif
                call PauseUnit(u, true)
                call SetUnitInvulnerable(u, true)
                // Suppress ambient auras and shiny effects on showcase models so models are clean to inspect
                call SaveInteger(Ab_HT, GetHandleId(u), 10, 1)
                call SaveInteger(Ab_HT, GetHandleId(u), 124, 1)
                if HaveSavedHandle(Ab_HT, GetHandleId(u), 80) then
                    call DestroyEffect(LoadEffectHandle(Ab_HT, GetHandleId(u), 80))
                    call RemoveSavedHandle(Ab_HT, GetHandleId(u), 80)
                endif
                // Overhead Dex number and name tag
                set tt = CreateTextTag()
                if tt != null then
                    call SetTextTagText(tt, "|cffffcc00#" + I2S(d) + " " + PAX_Dex_Name[d] + "|r", 0.021)
                    call SetTextTagPos(tt, curX, curY, 40.0)
                    call SetTextTagColor(tt, 255, 204, 0, 255)
                    call SetTextTagPermanent(tt, true)
                    call SetTextTagVisibility(tt, true)
                    set PAX_Gen_Tags[PAX_Gen_TagCount] = tt
                    set PAX_Gen_TagCount = PAX_Gen_TagCount + 1
                endif
                call GroupAddUnit(PAX_Gen_Group, u)
            endif
            set col = col + 1
            if col >= perRow then
                set col = 0
                set row = row + 1
            endif
        endif
        set d = d + 1
    endloop

    set u = League_Hero(GetPlayerId(pTrig))
    if u != null and Ab_Alive(u) then
        call SetUnitPosition(u, startX + 5 * 260.0, startY + 180.0)
        call PanCameraToTimedForPlayer(pTrig, startX + 5 * 260.0, startY + 180.0, 0.4)
    endif
    set u = null

    call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cff00ffff[Showcase] " + genTitle + " spawned! (" + I2S(endDex - startDex + 1) + " Pokemon)|r")
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cffffcc00Type -clear to remove showcase, -respawn to restore wild creeps.|r")
endfunction

function PAX_FindDexByName takes string q returns integer
    local integer i = 1
    local string lowerQ = StringCase(q, false)
    loop
        exitwhen i > 1025
        if StringCase(PAX_Dex_Name[i], false) == lowerQ then
            return i
        endif
        set i = i + 1
    endloop
    return 0
endfunction

function PAX_ChangeHeroToDex takes player pTrig, integer targetDex returns nothing
    local integer pid = GetPlayerId(pTrig)
    local unit oldHero = League_Hero(pid)
    local unit newHero = null
    local integer newTypeId = 0
    local real hx = 0.0
    local real hy = 0.0

    if targetDex < 1 or targetDex > 1025 or PAX_Dex_Hero[targetDex] == 0 then
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cffff4040[Error] Pokemon Dex #" + I2S(targetDex) + " not found.|r")
        return
    endif

    if oldHero == null or not Ab_Alive(oldHero) then
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cffff4040[Error] You need an active living Pokemon to change.|r")
        return
    endif

    set newTypeId = PAX_Dex_Hero[targetDex]
    set hx = GetUnitX(oldHero)
    set hy = GetUnitY(oldHero)

    call DestroyEffect(AddSpecialEffect("Abilities/Spells/Human/MassTeleport/MassTeleportTarget.mdl", hx, hy))
    set Mega_EvoItem = true
    call Mega_SafeReplace(oldHero, newTypeId, bj_UNIT_STATE_METHOD_RELATIVE)
    set Mega_EvoItem = false
    set newHero = bj_lastReplacedUnit

    if newHero != null then
        // User requirement: reset to Level 1 when changed
        call SetHeroLevel(newHero, 1, false)
        call SetHeroXP(newHero, 0, false)
        call SetUnitState(newHero, UNIT_STATE_LIFE, GetUnitState(newHero, UNIT_STATE_MAX_LIFE))
        call SetUnitState(newHero, UNIT_STATE_MANA, GetUnitState(newHero, UNIT_STATE_MAX_MANA))
        if PAX_NoLevelCap then
            call SuspendHeroXP(newHero, false)
        endif

        // Sync ability info button & HP for new hero
        call Ab_Sync(newHero)
        call Hero_HPSync(newHero)
        call SelectUnitForPlayerSingle(newHero, pTrig)

        call DisplayTimedTextToPlayer(pTrig, 0, 0, 6.0, "|cff00ff00[Change] Success! Transformed into #" + I2S(targetDex) + " " + PAX_Dex_Name[targetDex] + " (Level 1)!|r")
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 6.0, "|cffffcc00Type -lvl 50 or -lvl 100 to learn full moveset!|r")
    endif

    set oldHero = null
    set newHero = null
endfunction

function PAX_TestChatHandler takes nothing returns nothing
    local player pTrig = GetTriggerPlayer()
    local integer pid = GetPlayerId(pTrig)
    local string msg = GetEventPlayerChatString()
    local string param = ""
    local integer targetDex = 0
    local integer lvl = 1
    local integer c = 0
    local unit hero = null
    local unit u = null
    local group g = null

    if SubString(msg, 0, 3) == "-c " then
        set param = SubString(msg, 3, StringLength(msg))
        set targetDex = S2I(param)
        if targetDex == 0 then
            set targetDex = PAX_FindDexByName(param)
        endif
        call PAX_ChangeHeroToDex(pTrig, targetDex)

    elseif SubString(msg, 0, 8) == "-change " then
        set param = SubString(msg, 8, StringLength(msg))
        set targetDex = S2I(param)
        if targetDex == 0 then
            set targetDex = PAX_FindDexByName(param)
        endif
        call PAX_ChangeHeroToDex(pTrig, targetDex)

    elseif msg == "-legend" or msg == "-legends" or msg == "-ub" or msg == "-mythic" or msg == "-mythics" or msg == "-boss" or msg == "-bosses" then
        call PAX_ShowcaseLegends(pTrig)

    elseif SubString(msg, 0, 5) == "-gen " then
        set param = SubString(msg, 5, StringLength(msg))
        call PAX_ShowcaseGen(pTrig, S2I(param))

    elseif SubString(msg, 0, 4) == "-gen" and StringLength(msg) >= 5 then
        set param = SubString(msg, 4, StringLength(msg))
        if SubString(param, 0, 1) == "_" then
            set param = SubString(param, 1, StringLength(param))
        endif
        call PAX_ShowcaseGen(pTrig, S2I(param))

    elseif msg == "-nolvl" or msg == "-freelvl" or msg == "-lvlcap" then
        set PAX_NoLevelCap = not PAX_NoLevelCap
        set hero = League_Hero(pid)
        if PAX_NoLevelCap then
            if hero != null then
                call SuspendHeroXP(hero, false)
            endif
            call DisplayTimedTextToPlayer(pTrig, 0, 0, 6.0, "|cff00ff00[Test] Level Cap is now DISABLED! All Pokemon can level up freely without gym badges.|r")
        else
            if hero != null then
                call Badge_LevelCap(hero, pid)
            endif
            call DisplayTimedTextToPlayer(pTrig, 0, 0, 6.0, "|cffff8800[Test] Level Cap is now ENABLED. Standard gym badge rules apply.|r")
        endif
        set hero = null

    elseif SubString(msg, 0, 5) == "-lvl " then
        set param = SubString(msg, 5, StringLength(msg))
        set lvl = S2I(param)
        set hero = League_Hero(pid)
        if lvl >= 1 and lvl <= 100 then
            set PAX_Gen_TargetLvl = lvl
            if hero != null then
                call SetHeroLevel(hero, lvl, true)
                if PAX_NoLevelCap then
                    call SuspendHeroXP(hero, false)
                endif
            endif
            if PAX_Gen_Group != null then
                set g = CreateGroup()
                call GroupAddGroup(PAX_Gen_Group, g)
                loop
                    set u = FirstOfGroup(g)
                    exitwhen u == null
                    call GroupRemoveUnit(g, u)
                    if IsUnitType(u, UNIT_TYPE_HERO) then
                        call SetHeroLevel(u, lvl, false)
                    endif
                endloop
                call DestroyGroup(g)
                set g = null
            endif
            call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cff00ff00[Test] Hero and showcase Pokemon set to Level " + I2S(lvl) + "!|r")
        endif
        set hero = null
        set u = null

    elseif msg == "-clear" then
        call PAX_ClearAllFieldCreeps()
        set PAX_Gen_TargetLvl = 1
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cffffcc00[Test] Showcase cleared and field refreshed.|r")

    elseif msg == "-respawn" then
        set c = 0
        loop
            exitwhen c >= Wild_CampN
            set Wild_CampDue[c] = Wild_Time + 1.0
            set c = c + 1
        endloop
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cff00ff00[Test] Wild camps respawning in 1 second!|r")

    elseif msg == "-fx" or msg == "-vfx" or msg == "-aura" then
        set PAX_Test_NoFx = not PAX_Test_NoFx
        set hero = League_Hero(pid)
        if PAX_Test_NoFx then
            if hero != null then
                if HaveSavedHandle(Ab_HT, GetHandleId(hero), 80) then
                    call DestroyEffect(LoadEffectHandle(Ab_HT, GetHandleId(hero), 80))
                    call RemoveSavedHandle(Ab_HT, GetHandleId(hero), 80)
                endif
                if HaveSavedHandle(Mega_HT, GetHandleId(hero), 3) then
                    call DestroyEffect(LoadEffectHandle(Mega_HT, GetHandleId(hero), 3))
                    call RemoveSavedHandle(Mega_HT, GetHandleId(hero), 3)
                endif
            endif
            call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cffffcc00[Test] Hero ambient auras & effects DISABLED for clean model inspection.|r")
        else
            call DisplayTimedTextToPlayer(pTrig, 0, 0, 5.0, "|cff00ff00[Test] Hero ambient auras & effects ENABLED.|r")
        endif
        set hero = null
    endif

    set pTrig = null
endfunction

function PAX_Test_Setup takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0
""")
    for fn in init_funcs:
        out.append(f'    call ExecuteFunc("{fn}")')

    out.append("""    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-c ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-change ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gen", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-nolvl", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-freelvl", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-lvlcap", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-lvl ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-clear", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-respawn", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-fx", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-vfx", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-aura", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function PAX_TestChatHandler)
    set t = null
endfunction
""")

    code_jass = "\n".join(out)
    return globals_jass, code_jass, init_funcs

def patch_script(s: str) -> str:
    crlf = "\r\n" in s
    s = s.replace("\r\n", "\n")
    globals_jass, code_jass, _ = build_test_commands_jass()

    # 1. Insert globals right before endglobals of 01_clean_globals.j
    old_g = "\nendglobals\n// ======== [END FILE: 01_clean_globals.j] ========"
    new_g = "\n" + globals_jass + "\nendglobals\n// ======== [END FILE: 01_clean_globals.j] ========"
    s = _once(s, old_g, new_g, "Insert PAX_Test globals")

    # 2. Patch Badge_LevelCap to bypass when PAX_NoLevelCap is active
    old_cap = "function Badge_LevelCap takes unit u, integer pid returns nothing\n    local integer cap = Badge_Cap(pid)"
    new_cap = "function Badge_LevelCap takes unit u, integer pid returns nothing\n    local integer cap = 0\n    if PAX_NoLevelCap then\n        call SuspendHeroXP(u, false)\n        return\n    endif\n    set cap = Badge_Cap(pid)"
    s = _once(s, old_cap, new_cap, "Patch Badge_LevelCap with PAX_NoLevelCap bypass")

    # 3. Insert code_jass right before function PAX_MidChat
    s = _once(s, "function PAX_MidChat takes nothing returns nothing", code_jass + "\nfunction PAX_MidChat takes nothing returns nothing", "Insert PAX_Test code before PAX_MidChat")

    # 4. Hook PAX_Test_Setup right after call PAX_MidChat registration
    old_hook = '    call TriggerAddAction(t, function PAX_MidChat)'
    new_hook = '    call TriggerAddAction(t, function PAX_MidChat)\n    call PAX_Test_Setup()'
    s = _once(s, old_hook, new_hook, "Hook PAX_Test_Setup in chat init")

    if crlf:
        s = s.replace("\n", "\r\n")
    return s
