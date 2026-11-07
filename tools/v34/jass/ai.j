// ---------------------------------------------------------------------------------------------
// v3.4: wild elites, gym Pokemon and legends cast their 5 kit skills. The kit skills are hero skills of the game
// (Shadow Strike, Frost Nova, Shockwave ...) and the creep AI never casts those, so these units kept full mana.
// Ab_HT on the unit: 86 its target (the unit it last hit or that last hit it, Ab_OnDamaging), 87 kit + 1.
// Ab_HT on a skill: 58 its order string (Ty_InitData).
// ---------------------------------------------------------------------------------------------
function Ai_TryCast takes unit u, unit t, integer abil returns boolean
    local string orderstr = LoadStr(Ab_HT, abil, 58)
    if abil == 0 or orderstr == null or orderstr == "" or GetUnitAbilityLevel(u, abil) <= 0 then
        return false
    endif
    if BlzGetUnitAbilityCooldownRemaining(u, abil) > 0.0 then
        return false
    endif
    // unit target, else point target, else no target (Swords Dance, Future Sight ...)
    if IssueTargetOrder(u, orderstr, t) then
        return true
    endif
    if IssuePointOrder(u, orderstr, GetUnitX(t), GetUnitY(t)) then
        return true
    endif
    return IssueImmediateOrder(u, orderstr)
endfunction

// v3.4.2: chance per second to cast (gym Pokemon of gyms 1-4 cast less: Ab_HT key 88)
function Ai_Chance takes integer h returns real
    if HaveSavedReal(Ab_HT, h, 88) then
        return LoadReal(Ab_HT, h, 88)
    endif
    return Ai_CastChance
endfunction

function Ai_Unit takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, h, 87)
    local unit t = LoadUnitHandle(Ab_HT, h, 86)
    local integer pick0 = 0
    local integer j = 0
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then
        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_Chance(h) then
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
endfunction

function Ai_Tick takes nothing returns nothing
    local unit u = null
    call GroupEnumUnitsOfPlayer(Ai_G, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Ai_G)
        exitwhen u == null
        call GroupRemoveUnit(Ai_G, u)
        if GetWidgetLife(u) > 0.405 and LoadInteger(Ab_HT, GetHandleId(u), 87) > 0 then
            call Ai_Unit(u)
        endif
    endloop
endfunction

// a legend gets the 5 skills of its first type (it had only War Stomp / Bash, never cast)
function Ai_GiveKit takes unit u returns nothing
    local integer kit = Ty_Of(u, 0) + 1
    local integer j = 0
    if kit <= 0 then
        return
    endif
    loop
        exitwhen j >= 5
        if Wild_KitSkill[(kit - 1) * 5 + j] != 0 then
            call UnitAddAbility(u, Wild_KitSkill[(kit - 1) * 5 + j])
        endif
        set j = j + 1
    endloop
    call SaveInteger(Ab_HT, GetHandleId(u), 87, kit)
endfunction
