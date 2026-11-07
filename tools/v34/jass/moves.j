//@replace Mv_Put
// v3.4.1: the 319 moves are made from 11 game skills (Storm Bolt, Shadow Strike, Frost Nova ...); two moves of the
// same skill share its order, so the second button cast the first move (pressing Q used the move of E or W).
// A Pokemon holds at most one move of each kind (Mv_Kind): a move of a kind it holds replaces that move.
function Mv_Put takes unit u, integer s, integer m returns nothing
    local integer h = GetHandleId(u)
    local integer old = 0
    local integer slotB = 0
    local integer other = 0
    loop
        exitwhen slotB >= Mv_Slots
        set other = LoadInteger(Ab_HT, h, 40 + slotB) - 1
        if slotB != s and other >= 0 and other != m and Mv_Kind[other] == Mv_Kind[m] then
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cffffcc00" + Mv_Label[m] + " replaces " + Mv_Label[other] + " (same kind of move: they would share one button).|r")
            set s = slotB
            set slotB = Mv_Slots
        endif
        set slotB = slotB + 1
    endloop
    set old = LoadInteger(Ab_HT, h, 40 + s) - 1
    if old >= 0 then
        call UnitRemoveAbility(u, Mv_Id(s, old))
    endif
    call SaveInteger(Ab_HT, h, 40 + s, m + 1)
    call UnitAddAbility(u, Mv_Id(s, m))
endfunction
//@replace Mv_Sync
// slot of the move of the same kind as m that u holds, -1 if none
function Mv_KindSlot takes unit u, integer m returns integer
    local integer s = 0
    loop
        exitwhen s >= Mv_Slots
        if Mv_Slot(u, s) >= 0 and Mv_Kind[Mv_Slot(u, s)] == Mv_Kind[m] then
            return s
        endif
        set s = s + 1
    endloop
    return -1
endfunction

// v3.4.1: first drop a second move of a kind already held (saved before v3.4.1 or copied by an evolution); a new
// move of a kind already held replaces that move only if it is stronger
function Mv_Sync takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer id = GetUnitTypeId(u)
    local integer lv = GetHeroLevel(u)
    local integer n = LoadInteger(Ab_HT, id, 99)
    local integer k = 0
    local integer s = 0
    local integer slotB = 0
    local integer m = 0
    loop
        exitwhen s >= Mv_Slots
        set m = Mv_Slot(u, s)
        if m >= 0 then
            set slotB = 0
            loop
                exitwhen slotB >= s
                if Mv_Slot(u, slotB) >= 0 and Mv_Kind[Mv_Slot(u, slotB)] == Mv_Kind[m] then
                    call UnitRemoveAbility(u, Mv_Id(s, m))
                    call SaveInteger(Ab_HT, h, 40 + s, 0)
                    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cffffcc00" + Mv_Label[m] + " was forgotten: it shared one button with " + Mv_Label[Mv_Slot(u, slotB)] + ".|r")
                    set m = -1
                    set slotB = s
                endif
                set slotB = slotB + 1
            endloop
        endif
        if m >= 0 then
            if GetUnitAbilityLevel(u, Mv_Id(s, m)) == 0 then
                call UnitAddAbility(u, Mv_Id(s, m))
            endif
        endif
        set s = s + 1
    endloop
    loop
        exitwhen k >= n
        if lv >= LoadInteger(Ab_HT, id, 101 + 2 * k) then
            set m = LoadInteger(Ab_HT, id, 100 + 2 * k)
            if LoadInteger(Ab_HT, h, 200 + m) == 0 then
                if Mv_Known(u, m) then
                    call SaveInteger(Ab_HT, h, 200 + m, 1)
                elseif Mv_KindSlot(u, m) >= 0 then
                    set s = Mv_KindSlot(u, m)
                    if Mv_Score[m] > Mv_Score[Mv_Slot(u, s)] then
                        call Mv_Put(u, s, m)
                        call Mv_Notify(u, m)
                    endif
                    call SaveInteger(Ab_HT, h, 200 + m, 1)
                else
                    set s = Mv_FreeSlot(u)
                    if s >= 0 then
                        call Mv_Put(u, s, m)
                        call Mv_Notify(u, m)
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    elseif Mv_Score[m] > Mv_WeakScore(u) then
                        call Mv_Put(u, Mv_WeakSlot(u), m)
                        call Mv_Notify(u, m)
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    else
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    endif
                endif
            endif
        endif
        set k = k + 1
    endloop
endfunction
