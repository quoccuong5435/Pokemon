"""Build Pokemon Arena v4.2a on top of v4.2:
Removes Player-ID ownership lock on items (anyone/teammates can pick up & share dropped items freely),
while keeping all safe-on-death rules intact:
  - Common ('ofir') & Rare ('ocor') loot: safe on death immediately (never drop on death).
  - Mystery Loot Box (-up), Gamble (-gamble), and Forge (-forge) items: safe on death immediately on creation.
  - Epic ('oli2') & Legendary ('tgrh') wild drops (+ Legend Souls & Paradox Boosters):
    drop on death ONLY if held < 60s; after 60s held in inventory, permanently safe on death!
"""
import argparse
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, "tools"))

import mpq  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, "Pokemon Arena v4.2.w3x")
NAME = "v4.2a"
OUT_MAP = os.path.join(MAPS, f"Pokemon Arena {NAME}.w3x")
NEW_TITLE = f"Pokemon Arena {NAME}"
PJASS = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
REF = os.path.join(WORK, "analysis", "jass_ref")


def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[build_v42a] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


OLD_PICKUP_LOCK = """    local integer itH = 0
    local integer ownerPid = 0
    local integer pickupItemId = 0
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set itH = GetHandleId(it)
        set ownerPid = GetPlayerId(GetOwningPlayer(u))
        set pickupItemId = GetItemTypeId(it)
        if LoadInteger(PAX_Leg_HT, itH, 210) == 1 and LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040[SOULBOUND] This item belongs to Player " + I2S(LoadInteger(PAX_Leg_HT, itH, 211) + 1) + " and cannot be used!|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        if LoadInteger(PAX_Leg_HT, itH, 210) == 0 then
            if PAX_IsInstantSoulboundItem(pickupItemId) then
                call PAX_Soulbound_BindNow(it, ownerPid)
            elseif PAX_IsSoulboundProtectedItem(pickupItemId) then
                if LoadInteger(PAX_Leg_HT, itH, 213) == 0 or LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid then
                    call SaveInteger(PAX_Leg_HT, itH, 211, ownerPid)
                    call SaveInteger(PAX_Leg_HT, itH, 212, 0)
                    call SaveInteger(PAX_Leg_HT, itH, 213, 1)
                    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffffd166[UNBOUND]|r Hold |cffffcc00" + GetItemName(it) + "|r for |cffffd16660s|r to Soulbind it (drops on death until bound)!")
                endif
            endif
        endif
    endif"""

NEW_PICKUP_LOCK = """    local integer itH = 0
    local integer ownerPid = 0
    local integer pickupItemId = 0
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    // No Player-ID lock: any player can pick up/share items; safe-on-death protection still applies
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set itH = GetHandleId(it)
        set ownerPid = GetPlayerId(GetOwningPlayer(u))
        set pickupItemId = GetItemTypeId(it)
        if LoadInteger(PAX_Leg_HT, itH, 210) == 0 then
            if PAX_IsInstantSoulboundItem(pickupItemId) then
                call PAX_Soulbound_BindNow(it, ownerPid)
            elseif PAX_IsSoulboundProtectedItem(pickupItemId) then
                if LoadInteger(PAX_Leg_HT, itH, 213) == 0 or LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid then
                    call SaveInteger(PAX_Leg_HT, itH, 211, ownerPid)
                    call SaveInteger(PAX_Leg_HT, itH, 212, 0)
                    call SaveInteger(PAX_Leg_HT, itH, 213, 1)
                    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffffd166[UNSECURED]|r Hold |cffffcc00" + GetItemName(it) + "|r for |cffffd16660s|r to make it safe on death (drops on death until secured)!")
                endif
            endif
        endif
    endif"""


OLD_TICK_MSG = 'call DisplayTimedTextToPlayer(Player(sbPid), 0, 0, 5.0, "|cff00ffcc[SOULBOUND]|r |cffffcc00" + GetItemName(sbItem) + "|r |cffe8ecf2is now permanently locked to you (safe on death)!|r")'
NEW_TICK_MSG = 'call DisplayTimedTextToPlayer(Player(sbPid), 0, 0, 5.0, "|cff00ffcc[SAFE]|r |cffffcc00" + GetItemName(sbItem) + "|r |cffe8ecf2is now secured (will not drop on death)!|r")'

OLD_BOX_MSG = 'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[LOOT BOX]|r Opened a " + PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + "|r Loot (|cff00ffccSoulbound|r to you) at your feet!")'
NEW_BOX_MSG = 'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[LOOT BOX]|r Opened a " + PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + "|r Loot (|cff00ffccSafe on death|r) at your feet!")'

OLD_GAMBLE_MSG = 'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[GAMBLE]|r Lucky drop! A |cff00ffccSoulbound|r Rare/Epic Loot spawned at your feet!")'
NEW_GAMBLE_MSG = 'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[GAMBLE]|r Lucky drop! A |cff00ffccSafe-on-death|r Rare/Epic Loot spawned at your feet!")'

OLD_WILD_REINFORCE_FN = r"""function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer base_t = LoadInteger(Mega_HT, c + 500, 3)
    local integer new_t = 0
    local integer attempts = 0
    local integer capRemain = 10 - Wild_CampAlive[c]
    local integer spawnedCnt = 0
    local unit u = null
    if capRemain <= 0 then
        return
    endif
    if pow > 10 then
        set pow = 10
    endif
    set new_t = Wild_PickType(pow)
    loop
        exitwhen new_t != base_t or attempts >= 6
        set new_t = Wild_PickType(pow)
        set attempts = attempts + 1
    endloop
    if new_t == base_t and Wild_PoolN > 1 then
        set new_t = Wild_Pool[ModuloInteger(c + 3, Wild_PoolN)]
    endif
    // Hard cap: NEVER exceed 10 alive creeps in any camp (prevents late-game lag/crash)
    if capRemain >= 3 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 2 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 1 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        call Wild_MakeElite(u)
        set spawnedCnt = spawnedCnt + 1
    endif

    set Wild_CampAlive[c] = Wild_CampAlive[c] + spawnedCnt
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", Wild_CampX[c], Wild_CampY[c]))
    if u != null then
        call PAX_Fun_PublicFloat(u, "|cffff3333REINFORCED (+ELITE)!|r", 255, 60, 60, 2.5)
    endif
    set u = null
endfunction"""

NEW_WILD_REINFORCE_FN = r"""function Wild_CountTotalAlive takes nothing returns integer
    local integer campScanIdx = 0
    local integer totalAlive = 0
    loop
        exitwhen campScanIdx >= Wild_CampN
        if Wild_CampAlive[campScanIdx] > 0 then
            set totalAlive = totalAlive + Wild_CampAlive[campScanIdx]
        endif
        set campScanIdx = campScanIdx + 1
    endloop
    return totalAlive
endfunction

function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer base_t = LoadInteger(Mega_HT, c + 500, 3)
    local integer new_t = 0
    local integer attempts = 0
    local integer capRemain = 6 - Wild_CampAlive[c]
    local integer spawnedCnt = 0
    local unit u = null
    // Anti-crash strict caps: max 6 creeps per camp AND max 260 wild creeps across entire map
    if capRemain <= 0 or Wild_CountTotalAlive() >= 260 then
        return
    endif
    if pow > 10 then
        set pow = 10
    endif
    set new_t = Wild_PickType(pow)
    loop
        exitwhen new_t != base_t or attempts >= 6
        set new_t = Wild_PickType(pow)
        set attempts = attempts + 1
    endloop
    if new_t == base_t and Wild_PoolN > 1 then
        set new_t = Wild_Pool[ModuloInteger(c + 3, Wild_PoolN)]
    endif
    // Light reinforcement: at most 1 regular + 1 Elite (+2 max), never exceeding 6/camp
    if capRemain >= 2 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 1 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        call Wild_MakeElite(u)
        set spawnedCnt = spawnedCnt + 1
    endif

    set Wild_CampAlive[c] = Wild_CampAlive[c] + spawnedCnt
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", Wild_CampX[c], Wild_CampY[c]))
    if u != null then
        call PAX_Fun_PublicFloat(u, "|cffff3333REINFORCED (+ELITE)!|r", 255, 60, 60, 2.5)
    endif
    set u = null
endfunction"""

OLD_WILD_SPAWN_CAP = """    if Wild_CampSize[c] > 10 then
        set Wild_CampAlive[c] = 10
    else
        set Wild_CampAlive[c] = Wild_CampSize[c]
    endif"""

NEW_WILD_SPAWN_CAP = """    if Wild_CampSize[c] > 6 then
        set Wild_CampAlive[c] = 6
    else
        set Wild_CampAlive[c] = Wild_CampSize[c]
    endif"""

OLD_WILD_TICK_CAP = """            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time < 600.0 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                elseif Wild_CampAlive[c] < 10 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0 and LoadInteger(Mega_HT, c + 500, 2) < 2 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif"""

NEW_WILD_TICK_CAP = """            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time < 600.0 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                elseif Wild_CampAlive[c] < 6 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 90.0 and LoadInteger(Mega_HT, c + 500, 2) < 1 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif"""

OLD_AI_UNIT = """function Ai_Unit takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, h, 87)
    local unit t = LoadUnitHandle(Ab_HT, h, 86)
    local integer pick0 = 0
    local integer j = 0
    local group g = CreateGroup()
    local unit cand = null
    local unit weak = null
    local real min_hp = 100.0
    local real hp = 0.0
    // Smart AI Tier 1: Scan 600 range for low-HP heroes (< 30% HP) to focus down
    call GroupEnumUnitsInRange(g, GetUnitX(u), GetUnitY(u), 600.0, null)
    loop
        set cand = FirstOfGroup(g)
        exitwhen cand == null
        call GroupRemoveUnit(g, cand)
        if IsUnitEnemy(cand, GetOwningPlayer(u)) and not IsUnitType(cand, UNIT_TYPE_DEAD) and IsUnitType(cand, UNIT_TYPE_HERO) then
            set hp = GetUnitLifePercent(cand)
            if hp < 30.0 and hp < min_hp then
                set min_hp = hp
                set weak = cand
            endif
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    if weak != null then
        set t = weak
        call SaveUnitHandle(Ab_HT, h, 86, t)
        call SaveReal(Ab_HT, h, 60, Mega_Time)
        call IssueTargetOrder(u, "attack", t)
    endif
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then
        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_Chance(h) then  // v4.3 (3.4.2)
            set pick0 = GetRandomInt(0, 4)
            loop
                exitwhen j >= 5
                if Ai_TryCast(u, t, Wild_KitSkill[(kit - 1) * 5 + ModuloInteger(pick0 + j, 5)]) then
                    set j = 5
                endif
                set j = j + 1
            endloop
        endif
    endif
    set t = null
endfunction"""

NEW_AI_UNIT = """function Ai_Unit takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, h, 87)
    local unit t = LoadUnitHandle(Ab_HT, h, 86)
    local integer pick0 = 0
    local integer j = 0
    local group aiScanG = null
    local unit cand = null
    local unit weak = null
    local real min_hp = 100.0
    local real hp = 0.0
    // Anti-lag/crash: only scan nearby low-HP heroes when creep is actively in combat (and null all local handles!)
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then
        set aiScanG = CreateGroup()
        call GroupEnumUnitsInRange(aiScanG, GetUnitX(u), GetUnitY(u), 600.0, null)
        loop
            set cand = FirstOfGroup(aiScanG)
            exitwhen cand == null
            call GroupRemoveUnit(aiScanG, cand)
            if IsUnitEnemy(cand, GetOwningPlayer(u)) and GetWidgetLife(cand) > 0.405 and IsUnitType(cand, UNIT_TYPE_HERO) then
                set hp = GetUnitLifePercent(cand)
                if hp < 30.0 and hp < min_hp then
                    set min_hp = hp
                    set weak = cand
                endif
            endif
        endloop
        call DestroyGroup(aiScanG)
        set aiScanG = null
        if weak != null then
            set t = weak
            call SaveUnitHandle(Ab_HT, h, 86, t)
            call SaveReal(Ab_HT, h, 60, Mega_Time)
            call IssueTargetOrder(u, "attack", t)
        endif
        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_Chance(h) then  // v4.3 (3.4.2)
            set pick0 = GetRandomInt(0, 4)
            loop
                exitwhen j >= 5
                if Ai_TryCast(u, t, Wild_KitSkill[(kit - 1) * 5 + ModuloInteger(pick0 + j, 5)]) then
                    set j = 5
                endif
                set j = j + 1
            endloop
        endif
    endif
    set cand = null
    set weak = null
    set t = null
endfunction"""


def patch_script(s: str) -> str:
    s = _once(s, OLD_PICKUP_LOCK, NEW_PICKUP_LOCK, "Item_OnPickup remove Player-ID lock")
    s = _once(s, OLD_TICK_MSG, NEW_TICK_MSG, "PAX_SoulboundTick message")
    s = _once(s, OLD_BOX_MSG, NEW_BOX_MSG, "PAX_Up_OnClick message")
    s = _once(s, OLD_GAMBLE_MSG, NEW_GAMBLE_MSG, "PAX_Fun_Gamble message")
    s = _once(s, OLD_WILD_REINFORCE_FN, NEW_WILD_REINFORCE_FN, "Wild_ReinforceCamp anti-crash cap")
    s = _once(s, OLD_WILD_SPAWN_CAP, NEW_WILD_SPAWN_CAP, "Wild_SpawnCamp max 6 cap")
    s = _once(s, OLD_WILD_TICK_CAP, NEW_WILD_TICK_CAP, "Wild_Tick 90s 1-wave max-6 cap")
    s = _once(s, OLD_AI_UNIT, NEW_AI_UNIT, "Ai_Unit combat-only scan + leak fix")
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


def build_data():
    base = mpq.MPQ(BASE_MAP)
    script = base.read("scripts" + BS + "war3map.j").decode("utf-8")
    crlf = "\r\n" in script
    script = script.replace("\r\r\n", "\r\n").replace("\r\n", "\n")

    script = patch_script(script)
    script = script.replace("v4.2", NAME)
    if crlf:
        script = script.replace("\n", "\r\n")

    w3i = base.read("war3map.w3i").replace(b"Pokemon Arena v4.2", NEW_TITLE.encode("utf-8"))

    files = {
        "scripts" + BS + "war3map.j": script.encode("utf-8"),
        "war3map.w3i": w3i,
    }
    return base, files, script


def build(out, dry, skip_pjass=False):
    if not dry and os.path.exists(out):
        raise SystemExit(f"Output exists, refusing to overwrite per GEMINI.md: {out}")

    base, files, script = build_data()
    tmp = os.path.join(REF, "_tmp_v42a_war3map.j")
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

    print("Total files modified for %s: %d" % (NAME, len(files)))
    if dry:
        print("Dry run OK.")
        return

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(
        out,
        files,
        extra_listfile=("\r\n".join(listfile) + "\r\n").encode("latin-1"),
        extra_names=listfile,
    )
    patch_hm3w_header(out, NEW_TITLE)
    print("Wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1048576.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-pjass", action="store_true")
    ap.add_argument("--out", default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run, a.skip_pjass)
