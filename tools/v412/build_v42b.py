"""Build Pokemon Arena v4.2b on top of v4.2a:
1. Mega & Form permanent Unit ANcl fix + 12-slot Command Card overflow fix + 60s Form CD.
2. Anti-exploit Loot rework:
   - Removes x1.60 camp-factor inflation on tiny 2-creep camps; uses clean flat per-mob rates:
     Regular Wild 4% / Elite 12% / Mega Elite 18% / Legend Boss 45% (no guaranteed camp drops).
   - Increases Wild_Respawn from 10.0s -> 25.0s to stop 2-camp spawn-camping.
   - Keeps & enforces 20.0% Soul drop on all Elites (regular + Mega Elites).
3. 50/50 Left vs Right jungle balance (26 vs 26 camps):
   - Removes the 3 unmatched extra Right-side camps (camp 38, 39, 46) and their 4 pre-placed
     units, re-indexing Wild_CampN = 52 (26 Left vs 26 Right, 50/50 Roaming Legend spawns).
4. Minute-48 freeze / dead-forever / handle-leak & legacy-spawner fix:
   - Disables all 18 legacy v1.8 periodic wild creep spawners (Ox..xy), duplicate single-shot
     wild creep spawners (Jx..Vx, py..wy), and the buggy runaway dummy trigger `ts` (WL).
   - Fixes location leaks in room traps (sD..BD, JD, LD) and group/force leaks in Arena Duel
     (EL4..Fx4, Fy4).
   - Adds 14s Hero Revive Watchdog (PAX_ReviveWatchdog_Step in PAX_Leg_Tick1s) so no hero
     can ever stay dead forever or stuck paused.
"""
import argparse
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, "tools"))

import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402
import map_optimizer  # noqa: E402
import model_upgrades  # noqa: E402
import melee_ranged_classifier  # noqa: E402
import gen14_expansion  # noqa: E402
import test_commands  # noqa: E402
import move_ability_fix  # noqa: E402
import ability_rw  # noqa: E402
import hidden_ability  # noqa: E402
import move_tutor  # noqa: E402
import wild_mix  # noqa: E402
import random_gen  # noqa: E402
import item_fix  # noqa: E402
import boss_isolation  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, "Pokemon Arena v4.2a.w3x")
NAME = "v4.2b"
OUT_MAP = os.path.join(MAPS, f"Pokemon Arena {NAME}.w3x")
NEW_TITLE = f"Pokemon Arena {NAME}"
PJASS = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
REF = os.path.join(WORK, "analysis", "jass_ref")


def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[build_v42b] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


def _extract_section(strings: str, aid: str) -> str:
    m = re.search(rf"(?m)^\[{re.escape(aid)}\]\r?\n([\s\S]*?)(?=^\[|\Z)", strings)
    return m.group(1) if m else ""


def patch_objects_and_collect_map(w3u, abil, strings: str):
    """Creates A800..A851 Gold '+' unlock Hero skills, updates Hero `uhab`, and reverts AM* to Unit ANcl skills."""
    acol = abil.name_to_x
    template_ev = abil.find("AEev")
    if not template_ev:
        raise ValueError("[build_v42b] Base ability AEev not found in AbilityData.slk")

    # Collect all unique Mega/Form ability IDs currently in Hero `uhab` (deterministic order)
    cast_ids = []
    for u in w3u.original + w3u.custom:
        uh = str(u.get("uhab") or "").strip()
        if not uh:
            continue
        for aid in uh.split(","):
            aid = aid.strip()
            if aid and aid not in cast_ids:
                cast_ids.append(aid)

    if len(cast_ids) != 52:
        raise ValueError(f"[build_v42b] Expected 52 Mega/Form uhab abilities, found {len(cast_ids)}")

    # Map cast_id (AMxx) -> unlock_id (A800..A851)
    cast_to_unlock = {}
    unlock_to_cast = {}
    for idx, cid in enumerate(cast_ids):
        uid = f"A8{idx:02d}"
        cast_to_unlock[cid] = uid
        unlock_to_cast[uid] = cid

    # 1. Update every Hero's `uhab` in war3map.w3u from AMxx -> A8xx
    for u in w3u.original + w3u.custom:
        uh = str(u.get("uhab") or "").strip()
        if not uh:
            continue
        parts = [aid.strip() for aid in uh.split(",") if aid.strip()]
        new_parts = [cast_to_unlock.get(p, p) for p in parts]
        u.set("uhab", 3, ",".join(new_parts))

    # 2. For each of the 52 pairs:
    #    - Add A8xx (AEev passive Hero skill, hero=1, levels=1, reqLevel=50/70) to AbilityData.slk & Strings
    #    - Revert AMxx to pure Unit ANcl skill (hero=0, item=0, DataA1=0.01, DataB1=0, DataC1=1, DataD1=0.01, DataE1=0)
    #    - Ensure AMxx has matching Order=<DataF1> in CampaignAbilityStrings.txt
    extra_strings = []
    for cid in cast_ids:
        uid = cast_to_unlock[cid]
        crow = abil.find(cid)
        if not crow:
            raise ValueError(f"[build_v42b] Cast ability {cid} missing from AbilityData.slk")

        req_lv = crow.get(acol["reqLevel"], "50") or "50"
        order_str = crow.get(acol["DataF1"], "").strip('"')

        # Create A8xx Hero Unlock passive in AbilityData.slk
        urow = dict(template_ev)
        urow[1] = f'"{uid}"'
        urow[acol["hero"]] = "1"
        urow[acol["item"]] = "0"
        urow[acol["levels"]] = "1"
        urow[acol["reqLevel"]] = req_lv
        if "levelSkip" in acol:
            urow[acol["levelSkip"]] = "0"
        if "checkDep" in acol:
            urow[acol["checkDep"]] = "0"
        if "DataA1" in acol:
            urow[acol["DataA1"]] = "0"
        abil.rows.append(urow)

        # Revert AMxx to clean Unit ANcl ability (100% identical to working QWER AV01..AZ99!)
        crow[acol["hero"]] = "0"
        crow[acol["item"]] = "0"
        crow[acol["levels"]] = "1"
        crow[acol["reqLevel"]] = "0"
        crow[acol["DataA1"]] = "0.01"
        crow[acol["DataB1"]] = "0"
        crow[acol["DataC1"]] = "1"
        crow[acol["DataD1"]] = "0.01"
        crow[acol["DataE1"]] = "0"

        # Copy Research fields from AMxx to A8xx in CampaignAbilityStrings.txt
        cbody = _extract_section(strings, cid)
        rfields = {}
        for k in ("Name", "Art", "Researchart", "Researchbuttonpos", "Researchhotkey", "Researchtip", "Researchubertip"):
            m = re.search(rf"(?m)^{k}=([^\r\n]+)", cbody)
            if m:
                rfields[k] = m.group(1).strip()

        default_art = "ReplaceableTextures\\CommandButtons\\BTNArcaneOrb.blp"
        art_val = rfields.get("Researchart", rfields.get("Art", default_art))
        u_sec = [f"[{uid}]"]
        u_sec.append(f"Name={rfields.get('Name', cid)}")
        u_sec.append(f"Art={art_val}")
        u_sec.append("Buttonpos=1,1")
        u_sec.append(f"Researchart={art_val}")
        u_sec.append(f"Researchbuttonpos={rfields.get('Researchbuttonpos', '0,0')}")
        u_sec.append(f"Researchhotkey={rfields.get('Researchhotkey', 'D')}")
        u_sec.append(f"Researchtip={rfields.get('Researchtip', 'Unlock Mega/Form')}")
        default_uber = '"Unlocks Mega/Form on your Command Card."'
        u_sec.append(f"Researchubertip={rfields.get('Researchubertip', default_uber)}")
        extra_strings.append("\n".join(u_sec))

        # Ensure AMxx has Order=<DataF1> in CampaignAbilityStrings.txt (AM10..AM17 lacked Order=!)
        if order_str and not re.search(r"(?m)^Order=", cbody):
            sec_pat = re.compile(rf"(?m)^\[{re.escape(cid)}\]\r?\n")
            strings = sec_pat.sub(f"[{cid}]\nOrder={order_str}\n", strings, count=1)

    strings = strings.rstrip("\r\n") + "\n\n" + "\n\n".join(extra_strings) + "\n"
    return strings, unlock_to_cast


def _build_unlock_jass(unlock_to_cast: dict) -> str:
    map_lines = []
    first = True
    for uid, cid in unlock_to_cast.items():
        kw = "if" if first else "elseif"
        first = False
        map_lines.append(f"    {kw} unlockAbId == '{uid}' then\n        return '{cid}'")
    map_lines.append("    endif\n    return 0")
    map_body = "\n".join(map_lines)

    keep_checks = []
    for cid in unlock_to_cast.values():
        keep_checks.append(
            f"    if LoadInteger(PAX_Leg_HT, heroHandleId, '{cid}' + 262144) == 1 and GetUnitAbilityLevel(heroUnit, '{cid}') == 0 then\n"
            f"        call UnitAddAbility(heroUnit, '{cid}')\n"
            f"        call UnitMakeAbilityPermanent(heroUnit, true, '{cid}')\n"
            f"    endif"
        )
    keep_body = "\n".join(keep_checks)

    return f"""function PAX_UnlockToCastAb takes integer unlockAbId returns integer
{map_body}
endfunction

function PAX_HeroMega_KeepAlive takes unit heroUnit returns nothing
    local integer heroHandleId = 0
    if heroUnit == null or GetWidgetLife(heroUnit) <= 0.405 then
        return
    endif
    set heroHandleId = GetHandleId(heroUnit)
    if LoadInteger(PAX_Leg_HT, heroHandleId, 219) == 0 then
        return
    endif
{keep_body}
endfunction

function PAX_HeroMegaUnlock_OnLearn takes nothing returns boolean
    local unit heroUnit = GetTriggerUnit()
    local integer learnedAbId = GetLearnedSkill()
    local integer castAbId = PAX_UnlockToCastAb(learnedAbId)
    local integer heroHandleId = 0
    if castAbId != 0 then
        set heroHandleId = GetHandleId(heroUnit)
        // Remove dummy Gold '+' passive unlock skill so it takes 0 Command Card slots
        call UnitRemoveAbility(heroUnit, learnedAbId)
        // Grant the real permanent Unit ANcl Mega/Form ability (identical to Q/W/E/R moves!)
        if GetUnitAbilityLevel(heroUnit, castAbId) == 0 then
            call UnitAddAbility(heroUnit, castAbId)
        endif
        call UnitMakeAbilityPermanent(heroUnit, true, castAbId)
        call SaveInteger(PAX_Leg_HT, heroHandleId, castAbId + 262144, 1)
        call SaveInteger(PAX_Leg_HT, heroHandleId, 219, 1)
        call PAX_HeroUnlock_TryPay(heroUnit, castAbId)
    endif
    set heroUnit = null
    return false
endfunction"""


OLD_ONLEARN = """function PAX_HeroMegaUnlock_OnLearn takes nothing returns boolean
    local unit heroUnit = GetTriggerUnit()
    local integer learnedAbId = GetLearnedSkill()
    local integer megaIdx = Mega_IndexOfAbility(learnedAbId)
    local integer formSlot = PAX_Form_ItemIndex(learnedAbId)
    if megaIdx >= 0 or formSlot > 0 or learnedAbId == 'AM10' then
        call PAX_HeroUnlock_TryPay(heroUnit, learnedAbId)
    endif
    set heroUnit = null
    return false
endfunction"""

OLD_PAXT_FORM_APPLY = """    call PAX_Leg_Sync(u)
    call UnitAddAbility(u, 'PAXT')"""
NEW_PAXT_FORM_APPLY = """    call PAX_Leg_Sync(u)
    call UnitRemoveAbility(u, 'PAXT')"""

OLD_FORM_CD_DEOX = "call BlzStartUnitAbilityCooldown(u, 'AM17', 600.0)"
NEW_FORM_CD_DEOX = "call BlzStartUnitAbilityCooldown(u, 'AM17', 60.0)"

OLD_FORM_CD_OTHER = "call BlzStartUnitAbilityCooldown(u, PAX_Form_ItemAbility(slot), 600.0)"
NEW_FORM_CD_OTHER = "call BlzStartUnitAbilityCooldown(u, PAX_Form_ItemAbility(slot), 60.0)"

OLD_AB_SYNC_ADD = """        if want > 0 then
            call UnitAddAbility(u, Ab_InfoId(want))
            set fx = Ab_AuraModel(want)"""

NEW_AB_SYNC_ADD = """        if want > 0 then
            call UnitAddAbility(u, Ab_InfoId(want))
            if GetUnitTypeId(u) == 'E026' or GetUnitTypeId(u) == 'EL0A' then
                // Free 1 Row-1 slot on 2-Mega Legends (Mewtwo X/Y, Black/White Kyurem) so both Megas fit 12/12!
                call BlzUnitHideAbility(u, Ab_InfoId(want), true)
            endif
            set fx = Ab_AuraModel(want)"""

OLD_TICK1S_SYNC = """                call PAX_Champ_Sync(u)
                call PAX_Leg_Sync(u)"""
NEW_TICK1S_SYNC = """                if LoadInteger(PAX_Leg_HT, h, 220) != 0 then
                    call SaveInteger(PAX_Leg_HT, h, 220, 0)
                endif
                call PAX_Champ_Sync(u)
                call PAX_Leg_Sync(u)
                call PAX_HeroMega_KeepAlive(u)"""

OLD_TICK1S_HERO_END = """                        call PAX_Leg_JirachiWish(u, null)
                    endif
                endif
            endif
        endloop
        set pid = pid + 1"""
NEW_TICK1S_HERO_END = """                        call PAX_Leg_JirachiWish(u, null)
                    endif
                endif
            elseif IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitIllusion(u) and GetUnitTypeId(u) != 0 and GetUnitTypeId(u) != 'earc' and GetWidgetLife(u) <= 0.405 then
                call PAX_ReviveWatchdog_Step(u, pid)
            endif
        endloop
        set pid = pid + 1"""

REVIVE_WATCHDOG_JASS = """function PAX_ReviveWatchdog_Step takes unit deadHero, integer ownerPid returns nothing
    local integer heroHandleId = 0
    local integer deadSecs = 0
    local real revX = -5568.0
    local real revY = 0.0
    local player ownerPl = null
    if deadHero == null or ownerPid < 0 or ownerPid >= 12 then
        return
    endif
    set heroHandleId = GetHandleId(deadHero)
    set deadSecs = LoadInteger(PAX_Leg_HT, heroHandleId, 220) + 1
    if deadSecs < 14 then
        call SaveInteger(PAX_Leg_HT, heroHandleId, 220, deadSecs)
        return
    endif
    call SaveInteger(PAX_Leg_HT, heroHandleId, 220, 0)
    // Clear any stuck BlzPauseUnitEx counters so revived hero can never stay frozen
    if LoadInteger(PAX_Leg_HT, heroHandleId, 24) == 1 then
        call SaveInteger(PAX_Leg_HT, heroHandleId, 24, 0)
        call BlzPauseUnitEx(deadHero, false)
    endif
    if LoadInteger(PAX_Leg_HT, heroHandleId, 53) == 1 then
        call SaveInteger(PAX_Leg_HT, heroHandleId, 53, 0)
        call BlzPauseUnitEx(deadHero, false)
    endif
    if LoadInteger(PAX_Leg_HT, heroHandleId, 57) == 1 then
        call SaveInteger(PAX_Leg_HT, heroHandleId, 57, 0)
        call BlzPauseUnitEx(deadHero, false)
    endif
    if LoadInteger(Fx_HT, heroHandleId, 37) == 1 then
        call SaveInteger(Fx_HT, heroHandleId, 37, 0)
        call BlzPauseUnitEx(deadHero, false)
    endif
    if ownerPid >= 6 then
        set revX = 5568.0
    endif
    set ownerPl = Player(ownerPid)
    call ReviveHero(deadHero, revX, revY, false)
    call SetUnitManaPercentBJ(deadHero, 100)
    call PanCameraToTimedForPlayer(ownerPl, revX, revY, 0.50)
    call SelectUnitForPlayerSingle(deadHero, ownerPl)
    call DisplayTimedTextToPlayer(ownerPl, 0, 0, 5.0, "|cff00ffcc[REVIVE]|r Auto-revived your Pokemon at Base.")
    set ownerPl = null
endfunction"""

OLD_LOOT_CHANCE = """    if isLegend then
        set chance = 45.0
    elseif isElite then
        set chance = 15.0
    elseif isWild then
        set chance = 5.0
    else
        set it = null
        return
    endif
    if not isLegend then  // v4.1.3: the same expected loot for every camp
        set chance = RMinBJ(100.0, chance * PAX_Loot_CampFactor(dead))
    endif"""

NEW_LOOT_CHANCE = """    if isLegend then
        set chance = 45.0
    elseif LoadInteger(Mega_HT, GetHandleId(dead), 44) > 0 then
        set chance = 18.0
    elseif isElite then
        set chance = 12.0
    elseif isWild then
        set chance = 4.0
    else
        set it = null
        return
    endif"""

OLD_BOSS_ARMOR_SET = """            // Uniform Rebalanced Legend Boss Stats (Fixed Room + Roaming Wild Legends):
            // HP: 1,000,000 .. 1,500,000 | ATK: 1,500 .. 2,500 | Armor: 450 .. 700 (scaled by natural stats)"""

NEW_BOSS_ARMOR_SET = """            // Uniform Rebalanced Legend Boss Stats (Fixed Room + Roaming Wild Legends):
            // HP: 1,000,000 .. 1,500,000 | ATK: 1,500 .. 2,500 | Armor: 150 .. 200 (scaled by natural stats)"""

OLD_BOSS_ARMOR_CALL = """                // Armor mapped from base [75..225] -> [450..700]
                set arm = BlzGetUnitArmor(lg)
                set bossArmRatio = (arm - 75.0) / 150.0
                if bossArmRatio < 0.0 then
                    set bossArmRatio = 0.0
                elseif bossArmRatio > 1.0 then
                    set bossArmRatio = 1.0
                endif
                call BlzSetUnitArmor(lg, 450.0 + bossArmRatio * 250.0)"""

NEW_BOSS_ARMOR_CALL = """                // Armor mapped from base [75..225] -> [150..200] (HP stays 1,000,000..1,500,000)
                set arm = BlzGetUnitArmor(lg)
                set bossArmRatio = (arm - 75.0) / 150.0
                if bossArmRatio < 0.0 then
                    set bossArmRatio = 0.0
                elseif bossArmRatio > 1.0 then
                    set bossArmRatio = 1.0
                endif
                call BlzSetUnitArmor(lg, 150.0 + bossArmRatio * 50.0)"""

OLD_WILD_RESPAWN = "real Wild_Respawn = 10.0"
NEW_WILD_RESPAWN = "real Wild_Respawn = 5.0"

OLD_WILD_TICK_LOOP = """    loop
        exitwhen c >= Wild_CampN
        if Wild_CampDue[c] > 0.0 and Wild_Time >= Wild_CampDue[c] then
            call Wild_SpawnCamp(c)
        else
            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time < 600.0 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                elseif Wild_CampAlive[c] < 6 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 90.0 and LoadInteger(Mega_HT, c + 500, 2) < 1 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif
        endif
        set c = c + 1
    endloop"""

NEW_WILD_TICK_LOOP = """    loop
        exitwhen c >= Wild_CampN
        // Only respawn when ALL creeps in the camp are dead (Wild_CampAlive <= 0 triggers Wild_CampDue)
        // No reinforcement while creeps are still alive, preventing creep swarms
        if Wild_CampDue[c] > 0.0 and Wild_Time >= Wild_CampDue[c] then
            call Wild_SpawnCamp(c)
        endif
        set c = c + 1
    endloop"""

OLD_WILD_SOUL_CHECK = "if soul != 0 and LoadInteger(Mega_HT, h, 29) == 1 and GetRandomReal(0.0, 100.0) < Wild_SoulChance then"
NEW_WILD_SOUL_CHECK = "if soul != 0 and (LoadInteger(Mega_HT, h, 29) == 1 or LoadInteger(Mega_HT, h, 44) > 0) and GetRandomReal(0.0, 100.0) < Wild_SoulChance then"

# v4.2b: Clear old v1.8 pre-placed wild creeps + anti-duplicate diverse species picker for all 52 camps
WILD_UNIQUE_HELPERS_JASS = """function Wild_IsTypeUsed takes integer candidateType, integer skipCamp, boolean sameSideOnly returns boolean
    local integer campIdx = 0
    local boolean wantLeft = Wild_CampX[skipCamp] < 0.0
    loop
        exitwhen campIdx >= Wild_CampN
        if campIdx != skipCamp and (Wild_CampAlive[campIdx] > 0 or Wild_CampDue[campIdx] > 0.0) then
            if (not sameSideOnly) or ((Wild_CampX[campIdx] < 0.0) == wantLeft) then
                if LoadInteger(Mega_HT, campIdx + 500, 3) == candidateType then
                    return true
                endif
            endif
        endif
        set campIdx = campIdx + 1
    endloop
    return false
endfunction

function Wild_PickUniqueType takes integer basePow, integer campIdx returns integer
    local integer attempt = 0
    local integer tryPow = basePow
    local integer pickedType = 0
    // Pass 1: prefer globally unique Soul-bearing species across +/-1 power tier for high Soul diversity
    loop
        exitwhen attempt >= 24
        set tryPow = basePow
        if attempt >= 8 and attempt < 16 then
            set tryPow = basePow + 1
        elseif attempt >= 16 then
            set tryPow = basePow - 1
        endif
        if tryPow < 1 then
            set tryPow = 1
        elseif tryPow > 10 then
            set tryPow = 10
        endif
        set pickedType = Wild_PickType(tryPow)
        if LoadInteger(Mega_HT, pickedType, 8) != 0 and not Wild_IsTypeUsed(pickedType, campIdx, false) then
            return pickedType
        endif
        set attempt = attempt + 1
    endloop
    // Pass 2: at least unique on the same side (Left vs Right)
    set attempt = 0
    loop
        exitwhen attempt >= 16
        set pickedType = Wild_PickType(basePow)
        if not Wild_IsTypeUsed(pickedType, campIdx, true) then
            return pickedType
        endif
        set attempt = attempt + 1
    endloop
    return Wild_PickType(basePow)
endfunction"""

OLD_WILD_SPAWNCAMP_PICK = """    set t = Wild_PickType(pow)
    set Wild_CampDue[c] = 0.0"""
NEW_WILD_SPAWNCAMP_PICK = """    set t = Wild_PickUniqueType(pow, c)
    set Wild_CampDue[c] = 0.0"""

OLD_WILD_REGISTER_CAMPS = """function Wild_RegisterCamps takes nothing returns nothing
    local unit u = null
    local integer i = 0
    local integer best = 0
    local real bd = 0.0
    local real d = 0.0
    loop
        exitwhen i >= Wild_TypeN
        call SaveBoolean(Mega_HT, Wild_Type[i], 7, true)
        set i = i + 1
    endloop
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if Wild_IsWildType(GetUnitTypeId(u)) then
            set best = -1
            set bd = Wild_CampRadius * Wild_CampRadius
            set i = 0
            loop
                exitwhen i >= Wild_CampN
                set d = (GetUnitX(u) - Wild_CampX[i]) * (GetUnitX(u) - Wild_CampX[i]) + (GetUnitY(u) - Wild_CampY[i]) * (GetUnitY(u) - Wild_CampY[i])
                if d < bd then
                    set bd = d
                    set best = i
                endif
                set i = i + 1
            endloop
            if best >= 0 then
                call SaveInteger(Mega_HT, GetHandleId(u), 25, best + 1)
                set Wild_CampAlive[best] = Wild_CampAlive[best] + 1
                call SaveReal(Mega_HT, best + 500, 1, 0.0)
                call SaveInteger(Mega_HT, best + 500, 2, 0)
                call SaveInteger(Mega_HT, best + 500, 3, GetUnitTypeId(u))
                if LoadInteger(Mega_HT, best + 500, 4) == 0 then
                    call SaveInteger(Mega_HT, best + 500, 4, 1)
                    call Wild_MakeElite(u)
                endif
            endif
        endif
    endloop
endfunction"""

NEW_WILD_REGISTER_CAMPS = """function Wild_RegisterCamps takes nothing returns nothing
    local unit u = null
    local integer i = 0
    loop
        exitwhen i >= Wild_TypeN
        call SaveBoolean(Mega_HT, Wild_Type[i], 7, true)
        set i = i + 1
    endloop
    // v4.2b: Clear all repetitive legacy v1.8 pre-placed wild creeps (keeps Bosses, Shops, Trainers untouched)
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if Wild_IsWildType(GetUnitTypeId(u)) then
            call RemoveUnit(u)
        endif
    endloop
    // Stagger fresh diverse spawns across 3 Wild_Tick cycles (0:02, 0:04, 0:06) to avoid init op-limit spikes
    set i = 0
    loop
        exitwhen i >= Wild_CampN
        set Wild_CampAlive[i] = 0
        call SaveInteger(Mega_HT, i + 500, 3, 0)
        if i < 18 then
            set Wild_CampDue[i] = 0.1
        elseif i < 36 then
            set Wild_CampDue[i] = 2.5
        else
            set Wild_CampDue[i] = 4.5
        endif
        set i = i + 1
    endloop
    set u = null
endfunction"""

# v4.2b: -tp full debuff cleanse + -mid command to teleport to Center (-128, 16)
CLEANSE_AND_MID_JASS = """function PAX_CleanseAllDebuffs takes unit targetHero returns nothing
    local integer heroH = 0
    local integer stIdx = 1
    local effect debuffFx = null
    if targetHero == null then
        return
    endif
    set heroH = GetHandleId(targetHero)
    // 1. Remove all WC3 negative buffs (Slow, Poison, Stun, Hex, Curse, Cripple, Acid Bomb, etc.)
    call UnitRemoveBuffs(targetHero, false, true)
    // 2. Cure all custom Pokemon status conditions (Burn, Freeze, Paralysis, Poison, Sleep, Confusion)
    call Fx_Cure(targetHero)
    // 3. Clear negative stat stages & accuracy drop (keep positive buffs)
    loop
        exitwhen stIdx > 6
        if LoadInteger(Fx_HT, heroH, stIdx) < 0 then
            call SaveInteger(Fx_HT, heroH, stIdx, 0)
            call SaveReal(Fx_HT, heroH, 10 + stIdx, 0.0)
        endif
        set stIdx = stIdx + 1
    endloop
    if HaveSavedHandle(Fx_HT, heroH, 73) then
        set debuffFx = LoadEffectHandle(Fx_HT, heroH, 73)
        if debuffFx != null then
            call DestroyEffect(debuffFx)
        endif
        call RemoveSavedHandle(Fx_HT, heroH, 73)
        set debuffFx = null
    endif
    call SaveReal(Fx_HT, heroH, 26, 0.0)
    if LoadInteger(Fx_HT, heroH, 37) == 1 then
        call SaveInteger(Fx_HT, heroH, 37, 0)
        call BlzPauseUnitEx(targetHero, false)
    endif
    // 4. Clear Legend Burn, Freeze, Stun & Slow CC
    call GroupRemoveUnit(PAX_Leg_BurnG, targetHero)
    call RemoveSavedInteger(PAX_Leg_HT, heroH, 60)
    call RemoveSavedReal(PAX_Leg_HT, heroH, 61)
    call RemoveSavedHandle(PAX_Leg_HT, heroH, 62)
    call GroupRemoveUnit(PAX_Leg_FreezeG, targetHero)
    call SaveReal(PAX_Leg_HT, heroH, 52, 0.0)
    if HaveSavedHandle(PAX_Leg_HT, heroH, 58) then
        set debuffFx = LoadEffectHandle(PAX_Leg_HT, heroH, 58)
        if debuffFx != null then
            call DestroyEffect(debuffFx)
        endif
        call RemoveSavedHandle(PAX_Leg_HT, heroH, 58)
        set debuffFx = null
    endif
    if LoadInteger(PAX_Leg_HT, heroH, 53) == 1 then
        call SaveInteger(PAX_Leg_HT, heroH, 53, 0)
        call BlzPauseUnitEx(targetHero, false)
    endif
    call GroupRemoveUnit(PAX_Leg_CCG, targetHero)
    if LoadReal(PAX_Leg_HT, heroH, 56) > Mega_Time and LoadReal(PAX_Leg_HT, heroH, 55) > 0.0 then
        call SetUnitMoveSpeed(targetHero, LoadReal(PAX_Leg_HT, heroH, 55))
    endif
    call RemoveSavedReal(PAX_Leg_HT, heroH, 54)
    call RemoveSavedReal(PAX_Leg_HT, heroH, 55)
    call RemoveSavedReal(PAX_Leg_HT, heroH, 56)
    if LoadInteger(PAX_Leg_HT, heroH, 57) == 1 then
        call SaveInteger(PAX_Leg_HT, heroH, 57, 0)
        call BlzPauseUnitEx(targetHero, false)
    endif
    // 5. Clear Loot Soul Burn
    call GroupRemoveUnit(PAX_Loot_BurnG, targetHero)
    call RemoveSavedInteger(PAX_Item_HT, heroH, 200)
    call RemoveSavedInteger(PAX_Item_HT, heroH, 201)
    call RemoveSavedHandle(PAX_Item_HT, heroH, 202)
    call Fx_Show(targetHero)
    set debuffFx = null
endfunction"""

MID_CMD_JASS = r"""function PAX_MidGo takes nothing returns nothing
    local timer midTm = GetExpiredTimer()
    local integer midH = GetHandleId(midTm)
    local unit midHero = LoadUnitHandle(Fx_HT, midH, 0)
    local player midPl = null
    local integer midPid = 0
    if midHero != null and Ab_Alive(midHero) then
        set midPl = GetOwningPlayer(midHero)
        set midPid = GetPlayerId(midPl)
        if Fx_HasLegendSoul(midHero) then
            call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffff4040Cannot teleport to Mid while carrying a Legend Soul!|r")
        elseif Fx_HomeBusy(midPid) or (PAX_Solo_Active and (midPid == PAX_Solo_A or midPid == PAX_Solo_B)) then
            call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffff4040-mid cancelled: you are in a battle.|r")
        else
            call SetUnitPosition(midHero, -128.0, 16.0)
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", -128.0, 16.0))
            call PanCameraToTimedForPlayer(midPl, -128.0, 16.0, 0.3)
        endif
    endif
    call FlushChildHashtable(Fx_HT, midH)
    call DestroyTimer(midTm)
    set midTm = null
    set midHero = null
    set midPl = null
endfunction

function PAX_MidChat takes nothing returns nothing
    local player midPl = GetTriggerPlayer()
    local integer midPid = GetPlayerId(midPl)
    local unit midHero = League_Hero(midPid)
    local timer midTm = null
    if midHero == null then
        call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffffcc00-mid: you need a living Pokemon.|r")
    elseif Fx_HasLegendSoul(midHero) then
        call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffff4040Cannot teleport to Mid while carrying a Legend Soul!|r")
    elseif Fx_HomeBusy(midPid) or (PAX_Solo_Active and (midPid == PAX_Solo_A or midPid == PAX_Solo_B)) then
        call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffff4040-mid does not work during a gym, League, or duel battle.|r")
    elseif Mega_Time < Player_MidTpCd[midPid] then
        call DisplayTimedTextToPlayer(midPl, 0, 0, 5.0, "|cffffcc00-mid: ready again in " + I2S(R2I(Player_MidTpCd[midPid] - Mega_Time + 0.99)) + "s.|r")
    else
        set Player_MidTpCd[midPid] = Mega_Time + 30.0
        call DisplayTimedTextToPlayer(midPl, 0, 0, 3.0, "|cff00ffff-mid: teleporting to Center Arena in 3 seconds...|r")
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportCaster.mdl", midHero, "origin"))
        set midTm = CreateTimer()
        call SaveUnitHandle(Fx_HT, GetHandleId(midTm), 0, midHero)
        call TimerStart(midTm, 3.0, false, function PAX_MidGo)
    endif
    set midPl = null
    set midHero = null
    set midTm = null
endfunction"""

OLD_TP_CURE = """            call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
            call Fx_Cure(u)
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", x, y))"""

NEW_TP_CURE = """            call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
            call PAX_CleanseAllDebuffs(u)
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", x, y))"""

OLD_FX_INIT_HOME = """    call TriggerAddAction(t, function Fx_HomeChat)
    call TimerStart(CreateTimer(), 0.5, true, function Fx_Tick)"""

NEW_FX_INIT_HOME = """    call TriggerAddAction(t, function Fx_HomeChat)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-mid", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function PAX_MidChat)
    call TimerStart(CreateTimer(), 0.5, true, function Fx_Tick)"""

OLD_MEGA_INIT_END = """    call PAX_Fun_Init()
    call PAX_Late_Init()
    call PAX_Chaos_Init()"""

NEW_MEGA_INIT_END = """    call PAX_Fun_Init()
    call PAX_Late_Init()
    call PAX_Chaos_Init()
    // v4.2b: Disable legacy v1.8 uncontrolled creep spawners & runaway dummy trigger `ts` (fixes min-48 freeze/crash & loot spam)
    call DisableTrigger(Ox)
    call DisableTrigger(Sx)
    call DisableTrigger(Wx)
    call DisableTrigger(Xx)
    call DisableTrigger(Yx)
    call DisableTrigger(Zx)
    call DisableTrigger(ey)
    call DisableTrigger(fy)
    call DisableTrigger(gy)
    call DisableTrigger(hy)
    call DisableTrigger(iy)
    call DisableTrigger(jy)
    call DisableTrigger(ky)
    call DisableTrigger(my)
    call DisableTrigger(ny)
    call DisableTrigger(ry)
    call DisableTrigger(sy)
    call DisableTrigger(xy)
    call DisableTrigger(Jx)
    call DisableTrigger(Kx)
    call DisableTrigger(Lx)
    call DisableTrigger(Mx)
    call DisableTrigger(Nx)
    call DisableTrigger(Px)
    call DisableTrigger(Qx)
    call DisableTrigger(Rx)
    call DisableTrigger(Tx)
    call DisableTrigger(Ux)
    call DisableTrigger(Vx)
    call DisableTrigger(py)
    call DisableTrigger(qy)
    call DisableTrigger(ty)
    call DisableTrigger(uy)
    call DisableTrigger(vy)
    call DisableTrigger(wy)
    call DisableTrigger(ts)"""

OLD_TRAP_SD_BD = """function sD takes nothing returns nothing
call IssuePointOrderLocBJ(Eh,"flamestrike",GetRandomLocInRect(en))
endfunction
function tD takes nothing returns nothing
set fp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(fp,(3.00/2.00))
call TriggerAddAction(fp,function sD)
endfunction
function uD takes nothing returns nothing
call IssuePointOrderLocBJ(Fh,"flamestrike",GetRandomLocInRect(fn))
endfunction
function vD takes nothing returns nothing
set gp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(gp,(3.00/2.00))
call TriggerAddAction(gp,function uD)
endfunction
function wD takes nothing returns nothing
call IssuePointOrderLocBJ(Gh,"flamestrike",GetRandomLocInRect(gn))
endfunction
function xD takes nothing returns nothing
set hp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(hp,(3.00/2.00))
call TriggerAddAction(hp,function wD)
endfunction
function yD takes nothing returns nothing
call IssuePointOrderLocBJ(Hh,"flamestrike",GetRandomLocInRect(hn))
endfunction
function zD takes nothing returns nothing
set ip=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(ip,(3.00/2.00))
call TriggerAddAction(ip,function yD)
endfunction
function AD takes nothing returns nothing
call IssuePointOrderLocBJ(Ih,"flamestrike",GetRandomLocInRect(in))
endfunction
function aD takes nothing returns nothing
set jp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(jp,(3.00/2.00))
call TriggerAddAction(jp,function AD)
endfunction
function BD takes nothing returns nothing
call IssuePointOrderLocBJ(lh,"flamestrike",GetRandomLocInRect(jn))
endfunction
function bD takes nothing returns nothing
set kp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(kp,(3.00/2.00))
call TriggerAddAction(kp,function BD)
endfunction"""

NEW_TRAP_SD_BD = """function sD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(en)
call IssuePointOrderLocBJ(Eh,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function tD takes nothing returns nothing
set fp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(fp,(3.00/2.00))
call TriggerAddAction(fp,function sD)
endfunction
function uD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(fn)
call IssuePointOrderLocBJ(Fh,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function vD takes nothing returns nothing
set gp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(gp,(3.00/2.00))
call TriggerAddAction(gp,function uD)
endfunction
function wD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(gn)
call IssuePointOrderLocBJ(Gh,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function xD takes nothing returns nothing
set hp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(hp,(3.00/2.00))
call TriggerAddAction(hp,function wD)
endfunction
function yD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(hn)
call IssuePointOrderLocBJ(Hh,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function zD takes nothing returns nothing
set ip=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(ip,(3.00/2.00))
call TriggerAddAction(ip,function yD)
endfunction
function AD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(in)
call IssuePointOrderLocBJ(Ih,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function aD takes nothing returns nothing
set jp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(jp,(3.00/2.00))
call TriggerAddAction(jp,function AD)
endfunction
function BD takes nothing returns nothing
local location trapLoc=GetRandomLocInRect(jn)
call IssuePointOrderLocBJ(lh,"flamestrike",trapLoc)
call RemoveLocation(trapLoc)
set trapLoc=null
endfunction
function bD takes nothing returns nothing
set kp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(kp,(3.00/2.00))
call TriggerAddAction(kp,function BD)
endfunction"""

OLD_TRAP_JD_LD = """function JD takes nothing returns nothing
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(rn),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(sn))
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(sn),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(sn))
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(tn),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(tn))
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(un),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(tn))
endfunction
function KD takes nothing returns nothing
set pp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(pp,10.00)
call TriggerAddAction(pp,function JD)
endfunction
function LD takes nothing returns nothing
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(zn),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(sn))
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),GetRandomLocInRect(An),bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",GetRandomLocInRect(tn))
endfunction"""

NEW_TRAP_JD_LD = """function JD takes nothing returns nothing
local location stampLocA=GetRandomLocInRect(rn)
local location stampLocB=GetRandomLocInRect(sn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=GetRandomLocInRect(sn)
set stampLocB=GetRandomLocInRect(sn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=GetRandomLocInRect(tn)
set stampLocB=GetRandomLocInRect(tn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=GetRandomLocInRect(un)
set stampLocB=GetRandomLocInRect(tn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=null
set stampLocB=null
endfunction
function KD takes nothing returns nothing
set pp=CreateTrigger()
call TriggerRegisterTimerEventPeriodic(pp,10.00)
call TriggerAddAction(pp,function JD)
endfunction
function LD takes nothing returns nothing
local location stampLocA=GetRandomLocInRect(zn)
local location stampLocB=GetRandomLocInRect(sn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=GetRandomLocInRect(An)
set stampLocB=GetRandomLocInRect(tn)
call CreateNUnitsAtLoc(1,'h010',Player(PLAYER_NEUTRAL_AGGRESSIVE),stampLocA,bj_UNIT_FACING)
call SetUnitAbilityLevelSwapped('A06D',GetLastCreatedUnit(),3)
call UnitApplyTimedLifeBJ(8.00,'BTLF',GetLastCreatedUnit())
call IssuePointOrderLocBJ(GetLastCreatedUnit(),"stampede",stampLocB)
call RemoveLocation(stampLocA)
call RemoveLocation(stampLocB)
set stampLocA=null
set stampLocB=null
endfunction"""

OLD_FY4 = """function Fy4 takes nothing returns nothing
call ForForce(hz(Player(0)),function EL4)
call ForForce(gz(Player(0)),function EO4)
call PauseAllUnitsBJ(true)
call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Duel Time - Battle in the Arena!")
call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Kill all enemies in 40s!")
call TriggerSleepAction(3.00)
call ForForce(gz(Player(0)),function EQ4)
call ForForce(hz(Player(0)),function E54)
call TriggerSleepAction(2.00)
call PauseAllUnitsBJ(false)
set Oe=1
loop
exitwhen Oe>40
call TriggerSleepAction(1.00)
call DisplayTimedTextToForce(GetPlayersAll(),1.00,I2S(Oe))
set Pe=0
call ForForce(hz(Player(0)),function EX4)
if(F74())then
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Team 1 Win")
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Each Pokemon raise 1 level.")
call ForForce(gz(Player(0)),function F44)
set Oe=50
else
endif
set Pe=0
call ForForce(gz(Player(0)),function Ff4)
if(Fm4())then
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Team 2 Win")
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Each Pokemon raise 1 level")
call ForForce(hz(Player(0)),function Fk4)
set Oe=50
else
endif
call ForForce(GetPlayersAll(),function Fr4)
set Oe=Oe+1
endloop
call ForForce(hz(Player(0)),function Fu4)
call ForForce(gz(Player(0)),function Fx4)
endfunction"""

NEW_FY4 = """function Fy4 takes nothing returns nothing
local force duelFrc=hz(Player(0))
call ForForce(duelFrc,function EL4)
call DestroyForce(duelFrc)
set duelFrc=gz(Player(0))
call ForForce(duelFrc,function EO4)
call DestroyForce(duelFrc)
call PauseAllUnitsBJ(true)
call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Duel Time - Battle in the Arena!")
call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Kill all enemies in 40s!")
call TriggerSleepAction(3.00)
set duelFrc=gz(Player(0))
call ForForce(duelFrc,function EQ4)
call DestroyForce(duelFrc)
set duelFrc=hz(Player(0))
call ForForce(duelFrc,function E54)
call DestroyForce(duelFrc)
call TriggerSleepAction(2.00)
call PauseAllUnitsBJ(false)
set Oe=1
loop
exitwhen Oe>40
call TriggerSleepAction(1.00)
call DisplayTimedTextToForce(GetPlayersAll(),1.00,I2S(Oe))
set Pe=0
set duelFrc=hz(Player(0))
call ForForce(duelFrc,function EX4)
call DestroyForce(duelFrc)
if(F74())then
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Team 1 Win")
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Each Pokemon raise 1 level.")
set duelFrc=gz(Player(0))
call ForForce(duelFrc,function F44)
call DestroyForce(duelFrc)
set Oe=50
else
endif
set Pe=0
set duelFrc=gz(Player(0))
call ForForce(duelFrc,function Ff4)
call DestroyForce(duelFrc)
if(Fm4())then
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Team 2 Win")
call DisplayTimedTextToForce(GetPlayersAll(),3.00,"Each Pokemon raise 1 level")
set duelFrc=hz(Player(0))
call ForForce(duelFrc,function Fk4)
call DestroyForce(duelFrc)
set Oe=50
else
endif
call ForForce(GetPlayersAll(),function Fr4)
set Oe=Oe+1
endloop
set duelFrc=hz(Player(0))
call ForForce(duelFrc,function Fu4)
call DestroyForce(duelFrc)
set duelFrc=gz(Player(0))
call ForForce(duelFrc,function Fx4)
call DestroyForce(duelFrc)
set duelFrc=null
endfunction"""

DUEL_GROUP_HELPERS = [
    ("EL4", "EK4"),
    ("EO4", "EN4"),
    ("EQ4", "EP4"),
    ("E54", "ES4"),
    ("EX4", "EW4"),
    ("F44", "E_4"),
    ("Ff4", "Fe4"),
    ("Fk4", "Fj4"),
    ("Fr4", "Fq4"),
    ("Fu4", "Ft4"),
    ("Fx4", "Fw4"),
]

REMOVED_RIGHT_CAMPS = {38, 39, 46}
REMOVED_PREPLACED_LINES = [
    "set u=CreateUnit(p,'nogl',4932.5,-3436.6,242.300)\n",
    "set u=CreateUnit(p,'nogl',3555.8,-1840.3,278.292)\n",
    "set u=CreateUnit(p,'nogl',3281.3,-1940.1,9.405)\n",
    "set u=CreateUnit(p,'nogl',3788.3,-5578.9,40.969)\n",
]


def _patch_wild_camps_50_50(s: str) -> str:
    """Removes the 3 unmatched extra Right-side camps (38, 39, 46) and re-indexes Wild_CampN = 52 (26 vs 26)."""
    s = _once(s, "    set Wild_CampN = 55", "    set Wild_CampN = 52", "Set Wild_CampN = 52")
    m = re.search(r"(    set Wild_CampX\[0\][\s\S]*?    set Wild_CampPow\[54\] = \d+)", s)
    if not m:
        raise ValueError("[build_v42b] Could not locate Wild_CampX[0..54] block")
    old_block = m.group(1)
    entries = re.findall(
        r"    set Wild_CampX\[(\d+)\] = (-?[\d.]+)\n"
        r"    set Wild_CampY\[\1\] = (-?[\d.]+)\n"
        r"    set Wild_CampSize\[\1\] = (\d+)\n"
        r"    set Wild_CampPow\[\1\] = (\d+)",
        old_block,
    )
    if len(entries) != 55:
        raise ValueError(f"[build_v42b] Expected 55 Wild_Camp entries, found {len(entries)}")
    new_lines = []
    new_idx = 0
    for idx_s, x, y, sz, pw in entries:
        if int(idx_s) in REMOVED_RIGHT_CAMPS:
            continue
        new_lines.append(f"    set Wild_CampX[{new_idx}] = {x}")
        new_lines.append(f"    set Wild_CampY[{new_idx}] = {y}")
        new_lines.append(f"    set Wild_CampSize[{new_idx}] = {sz}")
        new_lines.append(f"    set Wild_CampPow[{new_idx}] = {pw}")
        new_idx += 1
    assert new_idx == 52
    s = _once(s, old_block, "\n".join(new_lines), "Re-index Wild_Camp[0..51] (26 Left vs 26 Right)")
    for pline in REMOVED_PREPLACED_LINES:
        s = _once(s, pline, "", f"Remove pre-placed unit at removed camp: {pline.strip()}")
    return s


def patch_script(s: str, unlock_to_cast: dict) -> str:
    # 1. Mega & Form permanent Unit ANcl fix + 12-slot overflow + 60s form CD
    full_block = _build_unlock_jass(unlock_to_cast)
    split_marker = "\nfunction PAX_HeroMegaUnlock_OnLearn"
    helper_part, onlearn_part = full_block.split(split_marker, 1)
    onlearn_part = "function PAX_HeroMegaUnlock_OnLearn" + onlearn_part

    s = _once(
        s,
        "function PAX_Leg_Tick1s takes nothing returns nothing",
        helper_part + "\n\n" + REVIVE_WATCHDOG_JASS + "\n\nfunction PAX_Leg_Tick1s takes nothing returns nothing",
        "Insert PAX_UnlockToCastAb, PAX_HeroMega_KeepAlive & PAX_ReviveWatchdog_Step before PAX_Leg_Tick1s",
    )
    s = _once(s, OLD_ONLEARN, onlearn_part, "Replace PAX_HeroMegaUnlock_OnLearn")
    s = _once(s, OLD_PAXT_FORM_APPLY, NEW_PAXT_FORM_APPLY, "Remove PAXT from PAX_Form_Apply")
    s = _once(s, OLD_FORM_CD_DEOX, NEW_FORM_CD_DEOX, "Fix Deoxys Form CD 600s -> 60s")
    s = _once(s, OLD_FORM_CD_OTHER, NEW_FORM_CD_OTHER, "Fix Form Switch CD 600s -> 60s")
    s = _once(s, OLD_AB_SYNC_ADD, NEW_AB_SYNC_ADD, "Hide cosmetic Ab_InfoId on Mewtwo/Kyurem")
    s = _once(s, OLD_TICK1S_SYNC, NEW_TICK1S_SYNC, "Wire PAX_HeroMega_KeepAlive & reset watchdog in PAX_Leg_Tick1s")
    s = _once(s, OLD_TICK1S_HERO_END, NEW_TICK1S_HERO_END, "Wire PAX_ReviveWatchdog_Step in PAX_Leg_Tick1s")

    # 2. Anti-exploit loot rework (flat 4%/12%/18%/45%, Wild_Respawn 25s, 20% Elite Soul) + Boss Armor rebalance
    s = _once(s, OLD_LOOT_CHANCE, NEW_LOOT_CHANCE, "Flat anti-exploit loot rates (4/12/18/45%)")
    s = _once(s, OLD_BOSS_ARMOR_SET, NEW_BOSS_ARMOR_SET, "Update Legend Boss comment Armor 150..200")
    s = _once(s, OLD_BOSS_ARMOR_CALL, NEW_BOSS_ARMOR_CALL, "Rebalance Legend Boss Armor 150..200 (keep HP 1M..1.5M)")
    s = _once(s, OLD_WILD_RESPAWN, NEW_WILD_RESPAWN, "Wild_Respawn 10.0 -> 5.0s")
    s = _once(s, OLD_WILD_TICK_LOOP, NEW_WILD_TICK_LOOP, "Only respawn when entire camp is dead (no mid-combat reinforcement)")
    s = _once(s, OLD_WILD_SOUL_CHECK, NEW_WILD_SOUL_CHECK, "20% Soul drop on regular + Mega Elites")

    # 2b. Clear legacy v1.8 pre-placed wild creeps + anti-duplicate diverse species picker
    s = _once(
        s,
        "function Wild_SpawnCamp takes integer c returns nothing",
        WILD_UNIQUE_HELPERS_JASS + "\n\nfunction Wild_SpawnCamp takes integer c returns nothing",
        "Insert Wild_IsTypeUsed & Wild_PickUniqueType before Wild_SpawnCamp",
    )
    s = _once(s, OLD_WILD_SPAWNCAMP_PICK, NEW_WILD_SPAWNCAMP_PICK, "Use Wild_PickUniqueType in Wild_SpawnCamp")
    s = _once(s, OLD_WILD_REGISTER_CAMPS, NEW_WILD_REGISTER_CAMPS, "Clear v1.8 wild creeps & stagger diverse initial camp spawns")

    # 2c. -tp full debuff cleanse + -mid teleport command
    s = _once(
        s,
        "function Fx_TpGo takes nothing returns nothing",
        CLEANSE_AND_MID_JASS + "\n\nfunction Fx_TpGo takes nothing returns nothing",
        "Insert PAX_CleanseAllDebuffs before Fx_TpGo",
    )
    s = _once(s, OLD_TP_CURE, NEW_TP_CURE, "Call PAX_CleanseAllDebuffs in Fx_TpGo")
    s = _once(
        s,
        "function Fx_HomeChat takes nothing returns nothing",
        MID_CMD_JASS + "\n\nfunction Fx_HomeChat takes nothing returns nothing",
        "Insert PAX_MidGo & PAX_MidChat before Fx_HomeChat",
    )
    s = _once(s, OLD_FX_INIT_HOME, NEW_FX_INIT_HOME, "Register -mid chat command in Fx_Init")

    # 3. 50/50 Left vs Right jungle camps (26 vs 26)
    s = _patch_wild_camps_50_50(s)

    # 4. Minute-48 freeze/crash fix: disable 18 legacy periodic + duplicate single-shot spawners + `ts`, fix trap & Duel handle leaks
    s = _once(s, OLD_MEGA_INIT_END, NEW_MEGA_INIT_END, "Disable legacy spawners & runaway ts in Mega_Init")
    s = _once(s, OLD_TRAP_SD_BD, NEW_TRAP_SD_BD, "Fix location leaks in sD..BD room traps")
    s = _once(s, OLD_TRAP_JD_LD, NEW_TRAP_JD_LD, "Fix location leaks in JD/LD stampede traps")
    s = _once(s, OLD_FY4, NEW_FY4, "Fix force leaks in Fy4 Arena Duel")
    for outer, inner in DUEL_GROUP_HELPERS:
        old_h = f"function {outer} takes nothing returns nothing\ncall ForGroupBJ(Wy(GetEnumPlayer()),function {inner})\nendfunction"
        new_h = (
            f"function {outer} takes nothing returns nothing\n"
            f"local group duelGrp=Wy(GetEnumPlayer())\n"
            f"call ForGroupBJ(duelGrp,function {inner})\n"
            f"call DestroyGroup(duelGrp)\n"
            f"set duelGrp=null\n"
            f"endfunction"
        )
        s = _once(s, old_h, new_h, f"Fix group leak in {outer}")
    return s


def patch_hm3w_header(path: str, new_title: str) -> None:
    with open(path, "r+b") as f:
        hdr = bytearray(f.read(512))
        assert hdr[:4] == b"HM3W", "Not a valid HM3W .w3x file"
        nul = hdr.index(0, 8)
        flags, max_players = struct.unpack_from("<II", hdr, nul + 1)
        new_hdr = bytearray(512)
        new_hdr[:4] = b"HM3W"
        title_b = new_title.encode("utf-8") + b"\x00"
        new_hdr[8:8 + len(title_b)] = title_b
        struct.pack_into("<II", new_hdr, 8 + len(title_b), flags, max_players)
        f.seek(0)
        f.write(new_hdr)


def build_data(optimize_assets=False):
    base = mpq.MPQ(BASE_MAP)
    script = base.read("scripts" + BS + "war3map.j").decode("utf-8")
    crlf = "\r\n" in script
    script = script.replace("\r\r\n", "\r\n").replace("\r\n", "\n")

    w3u = objdata.ObjFile(base.read("war3map.w3u"))
    abil = slk.Slk(base.read("Units" + BS + "AbilityData.slk").decode("latin-1"))
    strings = base.read("Units" + BS + "CampaignAbilityStrings.txt").decode("utf-8")
    items_slk = slk.Slk(base.read("Units" + BS + "ItemData.slk").decode("latin-1"))
    item_func = base.read("Units" + BS + "ItemFunc.txt").decode("utf-8", errors="replace")

    strings, unlock_to_cast = patch_objects_and_collect_map(w3u, abil, strings)

    # 1. PokeAPI Move / Ability Fix (GEMINI.md section 11)
    script = move_ability_fix.patch(script)

    # 2. Complete Ability Rework 3 Rounds (GEMINI.md section 12)
    script = ability_rw.patch(script)

    # 3. Hidden Ability Awakening (GEMINI.md section 12)
    script = hidden_ability.patch(script)

    # 4. Core v4.2b System Patches (Mega ANcl, Loot, 50/50 Camps, Watchdog)
    script = patch_script(script, unlock_to_cast)

    # 5. Move Tutor NPC & Level-Up Inquiry (GEMINI.md section 14)
    script = move_tutor.patch_script(script)

    # 6. Multi-Species Wild Camps (GEMINI.md section 15)
    script = wild_mix.patch_script(script)

    # 7. -random [gen] Command & Gen Roster (GEMINI.md section 15)
    script, _gen_stats = random_gen.patch_script(script, w3u)

    # 8. Shell Bell, Gym 8 Armor Shred & Rocky Helmet (GEMINI.md section 16)
    item_fix.patch_objects(abil)
    item_func = item_fix.patch_item_text(item_func)
    script = item_fix.patch_script(script)

    # 9. Boss Isolation, Leash 700 & Under-100 Protection & 30m Frenzy (GEMINI.md section 17)
    script = boss_isolation.patch_script(script)
    # 5. Normalize oversized new PkFx\Leg25 Legend Hero/Boss/Mega 3D scales
    script = map_optimizer.normalize_legend_scales(w3u, script)
    # Normalize scales for #159 Croconaw, #160 Feraligatr, #251 Celebi
    for u in w3u.original + w3u.custom:
        if u.id in ("EP01", "nZ01"):  # Croconaw: increase scale from 1.05 -> 1.25
            u.set("usca", 2, 1.25)
        elif u.id in ("EP02", "nZ02"):  # Feraligatr: reduce scale from 1.50 -> 1.15
            u.set("usca", 2, 1.15)
        elif u.id == "PZZA":  # Celebi: mesh height is only 4.4, scale 1.40 was microscopic (wild n035 was 6.0)
            u.set("usca", 2, 4.50)
    # 6. Upgrade 88 ugly/low-poly/broken Heroes + matching Wild/Boss units to HD 3D
    script, hd_stats = model_upgrades.patch_objects_and_script(w3u, script)
    # 7. Melee vs Ranged (Archer) Rework from HERO_MELEE_CHECKLIST.md + 3 JASS contact hooks
    script, mr_stats = melee_ranged_classifier.apply_melee_ranged(w3u, script)
    # 8. Gen 1-4 Full Expansion (+166 verified Gen 1-4 species: 100% Gen 1, 100% Gen 2, 84% Gen 3-4)
    script, item_func, g14_stats = gen14_expansion.patch_objects_and_script(w3u, items_slk, item_func, script)
    # 9. Developer Test Commands (-gen 1..4, -c <dex/name>, -nolvl, -lvl <n>, -clear)
    script = test_commands.patch_script(script)
    script = script.replace("v4.2a", NAME)
    if crlf:
        script = script.replace("\n", "\r\n")

    w3i = base.read("war3map.w3i").replace(b"Pokemon Arena v4.2a", NEW_TITLE.encode("utf-8"))

    files = {
        "scripts" + BS + "war3map.j": script.encode("utf-8"),
        "war3map.w3i": w3i,
        "war3map.w3u": w3u.to_bytes(),
        "Units" + BS + "AbilityData.slk": abil.to_text().encode("latin-1"),
        "Units" + BS + "CampaignAbilityStrings.txt": strings.encode("utf-8"),
        "Units" + BS + "ItemData.slk": items_slk.to_text().encode("latin-1"),
        "Units" + BS + "ItemFunc.txt": item_func.encode("utf-8"),
    }
    delete_files = []
    opt_stats = {
        "orphans_deleted": 0,
        "blps_optimized": 0,
        "blp_raw_saved_mb": 0.0,
        "hd_heroes": hd_stats["heroes_upgraded"],
        "hd_synced_units": hd_stats["matching_units_synced"],
        "hd_files_added": 0,
        "mr_melee": mr_stats["melee"],
        "mr_archer": mr_stats["archer"],
        "mr_wild_synced": mr_stats["wild_synced"],
        "g14_species": g14_stats["g14_species"],
        "g14_pick_added": g14_stats["g14_pick_added"],
        "g14_files_added": 0,
    }
    if optimize_assets:
        delete_files = map_optimizer.collect_orphan_deletes(base, files)
        opt_blps, bstats = map_optimizer.optimize_live_blps(base, delete_files, min_size=90_000, quality=76, max_dim=512)
        hd_files = model_upgrades.load_hd_assets(compress_blp=True)
        g14_files = gen14_expansion.load_g14_assets(compress_blp=True)
        files.update(opt_blps)
        files.update(hd_files)
        files.update(g14_files)
        # Override corrupted DeoxysDefense.mdx from legacy v4.1.3
        deox_path = os.path.join(WORK, "extracted_v1.8", "Deoxys.mdx")
        with open(deox_path, "rb") as df:
            files["PkFx\\Mega3D\\DeoxysDefense.mdx"] = df.read()
        opt_stats = {
            "orphans_deleted": len(delete_files),
            "blps_optimized": bstats["blps_optimized"],
            "blp_raw_saved_mb": round(bstats["raw_bytes_saved"] / 1048576.0, 2),
            "hd_heroes": hd_stats["heroes_upgraded"],
            "hd_synced_units": hd_stats["matching_units_synced"],
            "hd_files_added": len(hd_files),
            "mr_melee": mr_stats["melee"],
            "mr_archer": mr_stats["archer"],
            "mr_wild_synced": mr_stats["wild_synced"],
            "g14_species": g14_stats["g14_species"],
            "g14_pick_added": g14_stats["g14_pick_added"],
            "g14_files_added": len(g14_files),
        }
    return base, files, delete_files, opt_stats, script, w3u, abil, strings, unlock_to_cast


def build(out, dry, skip_pjass=False, optimize_assets=True, overwrite=False):
    if not dry and os.path.exists(out):
        if overwrite:
            print(f"[build_v42b] Overwriting existing map: {out}")
        else:
            raise SystemExit(f"Output exists, refusing to overwrite per GEMINI.md: {out}")

    base, files, delete_files, opt_stats, script, *_ = build_data(optimize_assets=optimize_assets)
    tmp = os.path.join(REF, "_tmp_v42b_war3map.j")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(script)

    if not skip_pjass and os.path.exists(PJASS):
        try:
            r = subprocess.run(
                [PJASS, os.path.join(REF, "common.j"), os.path.join(REF, "Blizzard.j"), tmp],
                capture_output=True,
                text=True,
            )
            print("PJASS rc=%d" % r.returncode)
            if r.returncode:
                print((r.stdout + r.stderr)[:1500])
                raise SystemExit(1)
        except OSError as e:
            print(f"[pjass skipped due to OS sandbox error: {e}]")

    print(
        "Total files modified for %s: %d | Melee/Archer: %d/%d (+%d wild) | HD heroes: %d (+%d synced, +%d files) | Gen1-4: +%d species (+%d pick, +%d files) | orphans deleted: %d | BLPs re-encoded: %d (raw saved %.2f MB)"
        % (
            NAME, len(files), opt_stats["mr_melee"], opt_stats["mr_archer"], opt_stats["mr_wild_synced"],
            opt_stats["hd_heroes"], opt_stats["hd_synced_units"], opt_stats["hd_files_added"],
            opt_stats["g14_species"], opt_stats["g14_pick_added"], opt_stats["g14_files_added"],
            opt_stats["orphans_deleted"], opt_stats["blps_optimized"], opt_stats["blp_raw_saved_mb"],
        )
    )
    if dry:
        print("Dry run OK.")
        return

    del_lower = {d.lower().replace("/", "\\") for d in delete_files}
    listfile = sorted(
        {nm for nm in base.listfile() if nm.lower().replace("/", "\\") not in del_lower} | set(files)
    )
    map_optimizer.save_compact(
        base,
        out,
        files,
        delete_files=delete_files,
        extra_listfile=("\r\n".join(listfile) + "\r\n").encode("latin-1"),
    )
    patch_hm3w_header(out, NEW_TITLE)
    print("Wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1048576.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-pjass", action="store_true")
    ap.add_argument("--no-optimize", action="store_true")
    ap.add_argument("--overwrite", "-f", action="store_true", help="Overwrite existing output map")
    ap.add_argument("--out", default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run, a.skip_pjass, optimize_assets=not a.no_optimize, overwrite=a.overwrite)
