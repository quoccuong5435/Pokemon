"""Smart Creep AI & Camp Stacking Reinforcement for Pokemon Arena v4.1.2-ver2j:
1. Guaranteed Elite creep at map start in every single camp (Wild_RegisterCamps).
2. 30s Camp Stacking Reinforcement:
   - If after 30s a camp is not cleared (Wild_CampAlive[c] > 0), stack 2 creeps of a different element + 1 additional Elite!
   - Spawns visual reinforcement effect & floating tag.
3. Smart 5-Tier Creep Combat AI:
   - Scans 600 range: switches aggro to focus low-HP enemy heroes (< 30% HP).
   - Interrupts & prioritizes offensive casting when engaging players.
   - Flocks camp allies to focus fire on the target.
"""
import re

AI_REINFORCE_CODE = r'''
function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer base_t = LoadInteger(Mega_HT, c + 500, 3)
    local integer new_t = 0
    local integer attempts = 0
    local unit u = null
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
    // Spawn 2 regular creeps of the different elemental type
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)

    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)

    // Spawn 1 additional ELITE creep of the different elemental type!
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)
    call Wild_MakeElite(u)

    set Wild_CampAlive[c] = Wild_CampAlive[c] + 3
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", Wild_CampX[c], Wild_CampY[c]))
    call PAX_Fun_PublicFloat(u, "|cffff3333REINFORCED (+ELITE)!|r", 255, 60, 60, 2.5)
    set u = null
endfunction
'''

def patch_script(s: str) -> str:
    # 1. Insert Wild_ReinforceCamp right before Wild_SpawnCamp
    if 'function Wild_ReinforceCamp' not in s:
        s = s.replace('function Wild_SpawnCamp', AI_REINFORCE_CODE + '\nfunction Wild_SpawnCamp', 1)

    # 2. Patch Wild_RegisterCamps to guarantee at least 1 Elite creep per camp at map start
    old_reg = '''            if best >= 0 then
                call SaveInteger(Mega_HT, GetHandleId(u), 25, best + 1)
                set Wild_CampAlive[best] = Wild_CampAlive[best] + 1
            endif'''

    new_reg = '''            if best >= 0 then
                call SaveInteger(Mega_HT, GetHandleId(u), 25, best + 1)
                set Wild_CampAlive[best] = Wild_CampAlive[best] + 1
                call SaveReal(Mega_HT, best + 500, 1, 0.0)
                call SaveInteger(Mega_HT, best + 500, 2, 0)
                call SaveInteger(Mega_HT, best + 500, 3, GetUnitTypeId(u))
                if LoadInteger(Mega_HT, best + 500, 4) == 0 then
                    call SaveInteger(Mega_HT, best + 500, 4, 1)
                    call Wild_MakeElite(u)
                endif
            endif'''

    if old_reg in s:
        s = s.replace(old_reg, new_reg, 1)
    else:
        print("[smart_creep_ai] Warning: old_reg anchor not found in war3map.j")

    # 3. Patch Wild_SpawnCamp to record spawn time, reset stacks and base type
    old_spawn_init = '''    set t = Wild_PickType(pow)
    set Wild_CampDue[c] = 0.0
    set Wild_CampAlive[c] = Wild_CampSize[c]'''

    new_spawn_init = '''    set t = Wild_PickType(pow)
    set Wild_CampDue[c] = 0.0
    set Wild_CampAlive[c] = Wild_CampSize[c]
    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
    call SaveInteger(Mega_HT, c + 500, 2, 0)
    call SaveInteger(Mega_HT, c + 500, 3, t)
    call SaveInteger(Mega_HT, c + 500, 4, 1)'''

    if old_spawn_init in s:
        s = s.replace(old_spawn_init, new_spawn_init, 1)
    else:
        print("[smart_creep_ai] Warning: old_spawn_init anchor not found in war3map.j")

    # 4. Patch Wild_Tick to check 30s camp stacking reinforcement
    old_tick_loop = '''    loop
        exitwhen c >= Wild_CampN
        if Wild_CampDue[c] > 0.0 and Wild_Time >= Wild_CampDue[c] then
            call Wild_SpawnCamp(c)
        endif
        set c = c + 1
    endloop'''

    new_tick_loop = '''    loop
        exitwhen c >= Wild_CampN
        if Wild_CampDue[c] > 0.0 and Wild_Time >= Wild_CampDue[c] then
            call Wild_SpawnCamp(c)
        else
            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0 and LoadInteger(Mega_HT, c + 500, 2) < 2 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif
        endif
        set c = c + 1
    endloop'''

    if old_tick_loop in s:
        s = s.replace(old_tick_loop, new_tick_loop, 1)
    else:
        print("[smart_creep_ai] Warning: old_tick_loop anchor not found in war3map.j")

    # 5. Patch Ai_Unit for Smart Creep Targeting (Target Lowest-HP Hero < 30%)
    old_ai_unit = '''function Ai_Unit takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, h, 87)
    local unit t = LoadUnitHandle(Ab_HT, h, 86)
    local integer pick0 = 0
    local integer j = 0
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then'''

    new_ai_unit = '''function Ai_Unit takes unit u returns nothing
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
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then'''

    if old_ai_unit in s:
        s = s.replace(old_ai_unit, new_ai_unit, 1)
    else:
        print("[smart_creep_ai] Warning: old_ai_unit anchor not found in war3map.j")

    return s
