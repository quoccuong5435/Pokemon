"""Boss Passive, Camp Leash (700 units) & Under-100 Player Protection (GEMINI.md section 17).

1. PASSIVE STANCE (SetUnitAcquireRange = 0.0):
   - Wild Legend Bosses stand completely peaceful at their camps without auto-attacking nearby players.
   - Nearby players below Lv 100 can freely farm regular creeps at the same camp without interference.

2. UNDER-100 PROTECTION (No aggro & 0 damage both ways):
   - Players below Lv 100 cannot damage Bosses (damage = 0.0, friendly warning).
   - Bosses NEVER retaliate, chase, or target players below Lv 100.
   - Ai_Unit ignores heroes below Lv 100 when picking low-HP focus targets or casting offensive kit skills.
   - Any damage from Boss onto a hero below Lv 100 is neutralized to 0.0, and Boss immediately stops.

3. DAMAGE-ONLY RETALIATION (Real HP Damage from Lv 100 Hero):
   - ONLY when a Lv 100 hero deals actual HP damage (damage > 0.0) does the Boss wake up and retaliate.

4. CAMP LEASH RADIUS (700 units):
   - Boss is tethered tightly to its camp center (hx, hy).
   - If dist > 700.0: Boss drops aggro, stops attacking, clears target, and walks back to camp center.
   - While returning, Boss regenerates 3% HP/s.
   - If dist > 1200.0 (displacement/knockback): instantly warps back to camp center.

5. DYNAMIC SPAWN PACING (After 30 min Speed-Up Frenzy):
   - 0 - 30 minutes: Normal pace (first spawn at 4:00, every 4 minutes 2 Bosses).
   - After 30 minutes (Wild_Time >= 1800.0): Legendary Frenzy mode! Spawns accelerate to every 90s (1.5 min), 3 Bosses per wave!
"""
import re
import jpatch

WHO = "boss_isolation"

OLD_LEG_INTERVAL = "real Leg_Interval = 360.0\nreal Leg_Next = 360.0"
NEW_LEG_INTERVAL = "real Leg_Interval = 240.0\nreal Leg_Next = 240.0"

OLD_WILD_TICK_LEG = """    if Wild_Time >= Leg_Next then
        set Leg_Next = Leg_Next + Leg_Interval
        if Leg_Alive < Leg_Max then
            call Leg_Spawn()
        endif
        if Leg_Alive < Leg_Max then
            call Leg_Spawn()
        endif
    endif"""

NEW_WILD_TICK_LEG = """    if Wild_Time >= Leg_Next then
        if Wild_Time >= 1800.0 then
            // After 30 minutes: Speed up! Spawn every 90 seconds (1.5 min), 3 bosses per wave!
            if LoadInteger(PAX_Boss_HT, 0, 30) == 0 then
                call SaveInteger(PAX_Boss_HT, 0, 30, 1)
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 12.0, "|cffffcc00[LEGENDARY FRENZY!]|r |cffe8ecf2Minute 30 reached! Wild Legendary Boss spawns have accelerated (every 90s, 3 Bosses per wave)!|r")
            endif
            set Leg_Next = Leg_Next + 90.0
            if Leg_Alive < Leg_Max then
                call Leg_Spawn()
            endif
            if Leg_Alive < Leg_Max then
                call Leg_Spawn()
            endif
            if Leg_Alive < Leg_Max then
                call Leg_Spawn()
            endif
        else
            // First 30 minutes: Normal pace (every 4 min, 2 bosses per wave)
            set Leg_Next = Leg_Next + 240.0
            if Leg_Alive < Leg_Max then
                call Leg_Spawn()
            endif
            if Leg_Alive < Leg_Max then
                call Leg_Spawn()
            endif
        endif
    endif"""

OLD_LEG_SPAWN = """    call Ai_GiveKit(lg)  // v3.4: and the 5 skills of their type, cast by Ai_Tick
    // Uniform Legend Boss scaling handled once inside PAX_Boss_Register (1M-1.5M HP, 1.5k-2.5k ATK, 450-700 Armor)
    call PAX_Boss_Register(lg, x, y)"""

NEW_LEG_SPAWN = """    call Ai_GiveKit(lg)  // v3.4: and the 5 skills of their type, cast by Ai_Tick
    // Uniform Legend Boss scaling handled once inside PAX_Boss_Register (1M-1.5M HP, 1.5k-2.5k ATK, 450-700 Armor)
    call SetUnitAcquireRange(lg, 0.0)
    call PAX_Boss_Register(lg, x, y)"""

OLD_BOSS_REGISTER = """            call GroupAddUnit(PAX_Leg_G, lg)
        endif
    endif
endfunction"""

NEW_BOSS_REGISTER = """            call GroupAddUnit(PAX_Leg_G, lg)
            call SetUnitAcquireRange(lg, 0.0)
        endif
    endif
endfunction"""

OLD_LEG_ON_DAMAGE = """function Leg_OnDamage takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local player p = null
    local integer pid = 0
    if Leg_IsLegend(GetUnitTypeId(t)) then
        set p = GetOwningPlayer(GetEventDamageSource())
        set pid = GetPlayerId(p)
        if pid < 12 and Leg_PlayerLevel(p) < Leg_MinLevel then
            call BlzSetEventDamage(0.0)
            if Mega_Time - Leg_Warned[pid] > 3.0 then
                set Leg_Warned[pid] = Mega_Time
                call DisplayTimedTextToPlayer(p, 0, 0, 3.0, "|cffff0000Only level 100 Pokemon can hurt " + GetUnitName(t) + "!|r")
            endif
        endif
    endif
    set t = null
    set p = null
    return false
endfunction"""

NEW_LEG_ON_DAMAGE = """function Leg_OnDamage takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local unit src = GetEventDamageSource()
    local player p = null
    local integer pid = 0
    if Leg_IsLegend(GetUnitTypeId(t)) then
        set p = GetOwningPlayer(src)
        set pid = GetPlayerId(p)
        if pid < 12 and Leg_PlayerLevel(p) < Leg_MinLevel then
            call BlzSetEventDamage(0.0)
            if Mega_Time - Leg_Warned[pid] > 3.0 then
                set Leg_Warned[pid] = Mega_Time
                call DisplayTimedTextToPlayer(p, 0, 0, 3.0, "|cffffcc00Only level 100 Pokemon can awaken " + GetUnitName(t) + "!|r")
            endif
        elseif pid < 12 and Leg_PlayerLevel(p) >= Leg_MinLevel and GetEventDamage() > 0.0 then
            // Level 100 hero dealt REAL damage into Boss HP -> Boss retaliates!
            call SaveUnitHandle(Ab_HT, GetHandleId(t), 86, src)
            call SaveReal(Ab_HT, GetHandleId(t), 60, Mega_Time)
            call IssueTargetOrder(t, "attack", src)
        endif
    endif
    if Leg_IsLegend(GetUnitTypeId(src)) then
        set p = GetOwningPlayer(t)
        set pid = GetPlayerId(p)
        if pid < 12 and Leg_PlayerLevel(p) < Leg_MinLevel then
            call BlzSetEventDamage(0.0)
            call IssueImmediateOrder(src, "stop")
            call SaveUnitHandle(Ab_HT, GetHandleId(src), 86, null)
        endif
    endif
    set t = null
    set src = null
    set p = null
    return false
endfunction"""

NEW_AI_UNIT = """// boss_isolation: Ai_Unit comes before Leg_IsLegend / Leg_PlayerLevel in the script, and JASS needs a function
// declared above its caller, so Ai_Unit uses these copies (same code, Leg_* globals are fine anywhere)
function BossIso_IsLegend takes integer id returns boolean
    local integer i = 0
    loop
        exitwhen i >= Leg_N
        if Leg_Type[i] == id then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

function BossIso_PlayerLevel takes player p returns integer
    local unit u = null
    local integer best = 0
    call GroupEnumUnitsOfPlayer(Leg_Tmp, p, null)
    loop
        set u = FirstOfGroup(Leg_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Leg_Tmp, u)
        if IsUnitType(u, UNIT_TYPE_HERO) and GetHeroLevel(u) > best then
            set best = GetHeroLevel(u)
        endif
    endloop
    return best
endfunction

function Ai_Unit takes unit u returns nothing
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
    local boolean isLeg = BossIso_IsLegend(GetUnitTypeId(u))
    if isLeg and t != null and BossIso_PlayerLevel(GetOwningPlayer(t)) < Leg_MinLevel then
        set t = null
        call SaveUnitHandle(Ab_HT, h, 86, null)
    endif
    // Anti-lag/crash: only scan nearby low-HP heroes when creep is actively in combat (and null all local handles!)
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then
        set aiScanG = CreateGroup()
        call GroupEnumUnitsInRange(aiScanG, GetUnitX(u), GetUnitY(u), 600.0, null)
        loop
            set cand = FirstOfGroup(aiScanG)
            exitwhen cand == null
            call GroupRemoveUnit(aiScanG, cand)
            if IsUnitEnemy(cand, GetOwningPlayer(u)) and GetWidgetLife(cand) > 0.405 and IsUnitType(cand, UNIT_TYPE_HERO) then
                if not isLeg or BossIso_PlayerLevel(GetOwningPlayer(cand)) >= Leg_MinLevel then
                    set hp = GetUnitLifePercent(cand)
                    if hp < 30.0 and hp < min_hp then
                        set min_hp = hp
                        set weak = cand
                    endif
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

OLD_BOSS_TICK_LEASH = """            if returning == 1 then
                if lastCombat > returnStart then
                    call SaveInteger(PAX_Boss_HT, h, 6, 0)
                    call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
                else
                    if GetWidgetLife(u) < maxhp then
                        call SetWidgetLife(u, RMinBJ(maxhp, GetWidgetLife(u) + 0.02 * maxhp))
                    endif
                    if dist > 2500.0 then
                        call SetUnitPosition(u, hx, hy)
                        call IssueImmediateOrder(u, "stop")
                        call SaveInteger(PAX_Boss_HT, h, 6, 0)
                        call SaveReal(PAX_Boss_HT, h, 3, hx)
                        call SaveReal(PAX_Boss_HT, h, 4, hy)
                        call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
                    elseif dist > 250.0 then
                        call IssuePointOrder(u, "move", hx, hy)
                    else
                        call SaveInteger(PAX_Boss_HT, h, 6, 0)
                    endif
                endif
            else
                if moved then
                    set lastActive = Mega_Time
                    call SaveReal(PAX_Boss_HT, h, 5, lastActive)
                elseif Mega_Time - lastActive >= 10.0 then
                    if GetWidgetLife(u) < maxhp then
                        call SetWidgetLife(u, RMinBJ(maxhp, GetWidgetLife(u) + 0.02 * maxhp))
                    endif
                if dist > 2500.0 then
                    call SetUnitPosition(u, hx, hy)
                    call IssueImmediateOrder(u, "stop")
                    call SaveReal(PAX_Boss_HT, h, 3, hx)
                    call SaveReal(PAX_Boss_HT, h, 4, hy)
                    call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
                elseif dist > 250.0 then
                    call SaveInteger(PAX_Boss_HT, h, 6, 1)
                    call SaveReal(PAX_Boss_HT, h, 7, Mega_Time)
                    call IssuePointOrder(u, "move", hx, hy)
                endif
                endif
            endif"""

NEW_BOSS_TICK_LEASH = """            if dist > 1200.0 then
                call SetUnitPosition(u, hx, hy)
                call IssueImmediateOrder(u, "stop")
                call SaveUnitHandle(Ab_HT, h, 86, null)
                call SaveInteger(PAX_Boss_HT, h, 6, 0)
                call SaveReal(PAX_Boss_HT, h, 3, hx)
                call SaveReal(PAX_Boss_HT, h, 4, hy)
                call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
            elseif dist > 700.0 then
                call IssueImmediateOrder(u, "stop")
                call SaveUnitHandle(Ab_HT, h, 86, null)
                call SaveInteger(PAX_Boss_HT, h, 6, 1)
                call SaveReal(PAX_Boss_HT, h, 7, Mega_Time)
                call IssuePointOrder(u, "move", hx, hy)
            elseif returning == 1 then
                if dist > 150.0 then
                    call IssuePointOrder(u, "move", hx, hy)
                    if GetWidgetLife(u) < maxhp then
                        call SetWidgetLife(u, RMinBJ(maxhp, GetWidgetLife(u) + 0.03 * maxhp))
                    endif
                else
                    call SaveInteger(PAX_Boss_HT, h, 6, 0)
                endif
            else
                if moved then
                    set lastActive = Mega_Time
                    call SaveReal(PAX_Boss_HT, h, 5, lastActive)
                elseif Mega_Time - lastActive >= 10.0 then
                    if GetWidgetLife(u) < maxhp then
                        call SetWidgetLife(u, RMinBJ(maxhp, GetWidgetLife(u) + 0.02 * maxhp))
                    endif
                    if dist > 150.0 then
                        call SaveInteger(PAX_Boss_HT, h, 6, 1)
                        call SaveReal(PAX_Boss_HT, h, 7, Mega_Time)
                        call IssuePointOrder(u, "move", hx, hy)
                    endif
                endif
            endif"""


def patch_script(s: str) -> str:
    s = jpatch.once(s, OLD_LEG_INTERVAL, NEW_LEG_INTERVAL, "Leg_Interval 240s & Leg_Next 240s", WHO)
    s = jpatch.once(s, OLD_WILD_TICK_LEG, NEW_WILD_TICK_LEG, "Wild_Tick 30m Frenzy Speedup (every 90s, 3 Bosses)", WHO)
    s = jpatch.once(s, OLD_LEG_SPAWN, NEW_LEG_SPAWN, "Leg_Spawn SetUnitAcquireRange 0.0", WHO)
    s = jpatch.once(s, OLD_BOSS_REGISTER, NEW_BOSS_REGISTER, "PAX_Boss_Register SetUnitAcquireRange 0.0", WHO)
    s = jpatch.once(s, OLD_LEG_ON_DAMAGE, NEW_LEG_ON_DAMAGE, "Leg_OnDamage Lv100 wakeup & Under-100 player protection", WHO)
    s = jpatch.replace_function(s, "function Ai_Unit takes unit u returns nothing", NEW_AI_UNIT, "Ai_Unit under-100 protection", WHO)
    s = jpatch.once(s, OLD_BOSS_TICK_LEASH, NEW_BOSS_TICK_LEASH, "PAX_Boss_Tick Leash 700.0 & Warp 1200.0", WHO)
    return s
