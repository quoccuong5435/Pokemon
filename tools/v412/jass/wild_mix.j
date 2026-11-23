// ===== wild_mix (tools/v412/wild_mix.py): every creep of a camp is its own species, none repeated on the map =====
// WD_MarkAlive puts every living wild species in a set (stamp in WD_HT, key 0); WD_Pick takes a species of the
// camp's power that is not in the set (Soul species first, power +-1 allowed), adds it, and only repeats one
// when the pool of that power is used up. The elite stays one random creep of the camp.
function WD_MarkAlive takes nothing returns nothing
    local unit u = null
    set WD_Stamp = WD_Stamp + 1
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if GetWidgetLife(u) > 0.405 and Wild_IsWildType(GetUnitTypeId(u)) then
            call SaveInteger(WD_HT, GetUnitTypeId(u), 0, WD_Stamp)
        endif
    endloop
endfunction

function WD_Used takes integer t returns boolean
    return LoadInteger(WD_HT, t, 0) == WD_Stamp
endfunction

function WD_Pick takes integer pow returns integer
    local integer attempt = 0
    local integer tryPow = pow
    local integer t = 0
    loop
        exitwhen attempt >= 36
        set tryPow = pow
        if attempt >= 16 and attempt < 26 then
            set tryPow = pow + 1
        elseif attempt >= 26 then
            set tryPow = pow - 1
        endif
        if tryPow < 1 then
            set tryPow = 1
        elseif tryPow > 10 then
            set tryPow = 10
        endif
        set t = Wild_PickType(tryPow)
        if LoadInteger(Mega_HT, t, 8) != 0 and not WD_Used(t) then
            call SaveInteger(WD_HT, t, 0, WD_Stamp)
            return t
        endif
        set attempt = attempt + 1
    endloop
    set attempt = 0
    loop
        exitwhen attempt >= 20
        set t = Wild_PickType(pow)
        if not WD_Used(t) then
            call SaveInteger(WD_HT, t, 0, WD_Stamp)
            return t
        endif
        set attempt = attempt + 1
    endloop
    set t = Wild_PickType(pow)
    call SaveInteger(WD_HT, t, 0, WD_Stamp)
    return t
endfunction

// the creep's own next form when the tier reaches it, else the same species while still in range, else a new one
function WD_NextForm takes integer t, integer pow returns integer
    local integer cur = t
    local integer nt = LoadInteger(Mega_HT, t, 45)
    local integer guard = 0
    loop
        exitwhen nt == 0 or LoadInteger(Mega_HT, nt, 47) > pow or guard >= 3
        set cur = nt
        set nt = LoadInteger(Mega_HT, cur, 45)
        set guard = guard + 1
    endloop
    if cur != t and not WD_Used(cur) then
        call SaveInteger(WD_HT, cur, 0, WD_Stamp)
        return cur
    endif
    if LoadInteger(Mega_HT, t, 48) >= pow then
        return t
    endif
    return WD_Pick(pow)
endfunction

