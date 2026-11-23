globals
real Repick_Window = 120.0
integer Repick_Max = 2
integer array Repick_Count
integer array Repick_XP
boolean array Repick_Pending
endglobals

function Repick_Do takes player p returns nothing
    local integer pid = GetPlayerId(p)
    local unit h = null
    local unit u = null
    local item it = null
    local integer i = 0
    if Mega_Time >= Repick_Window then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Repick is only allowed in the first 2 minutes.|r")
        return
    endif
    if Repick_Count[pid] >= Repick_Max then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You have no repicks left.|r")
        return
    endif
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) then
            set h = u
        endif
    endloop
    if h == null or IsUnitType(h, UNIT_TYPE_DEAD) or LoadInteger(Mega_HT, GetHandleId(h), 0) > 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You need a living Pokemon (not in Mega form) to repick.|r")
        set h = null
        return
    endif
    set Repick_Count[pid] = Repick_Count[pid] + 1
    set Repick_XP[pid] = GetHeroXP(h)
    set Repick_Pending[pid] = true
    loop
        exitwhen i >= 6
        set it = UnitItemInSlot(h, i)
        if it != null then
            call UnitRemoveItem(h, it)
            call SetItemVisible(it, false)
        endif
        call SaveItemHandle(Mega_HT, 900 + pid, i, it)
        set i = i + 1
    endloop
    call RemoveUnit(h)
    set u = CreateUnit(p, 'earc', -128.0, 4544.0, 270.0)
    call SelectUnitForPlayerSingle(u, p)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r repicked (" + I2S(Repick_Count[pid]) + "/2)")
    set h = null
    set u = null
    set it = null
endfunction

function Repick_OnChat takes nothing returns nothing
    call Repick_Do(GetTriggerPlayer())
endfunction

function Rand_FindWisp takes player p returns unit
    local unit u = null
    local unit w = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if GetUnitTypeId(u) == 'earc' then
            set w = u
        endif
    endloop
    return w
endfunction

function Rand_Give takes player p returns nothing
    local unit w = Rand_FindWisp(p)
    local unit h = null
    local integer t = 0
    local integer tries = 0
    if w == null or Rand_N == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You already have a Pokemon.|r")
        return
    endif
    loop
        set t = Rand_Type[GetRandomInt(0, Rand_N - 1)]
        set tries = tries + 1
        exitwhen tries >= 20 or not Rand_IsTaken(t)
    endloop
    set h = CreateUnit(p, t, GetUnitX(w), GetUnitY(w), 270.0)
    call Repick_Restore(h)
    call RemoveUnit(w)
    call SelectUnitForPlayerSingle(h, p)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r Has Choosen (random) |cffffcc00" + GetHeroProperName(h) + "|r")
    set w = null
    set h = null
endfunction

function Host_Id takes nothing returns integer
    local integer i = 0
    loop
        exitwhen i >= 12 or GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING
        set i = i + 1
    endloop
    return i
endfunction

function Rand_Hint takes nothing returns nothing
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 15.0, "|cffffcc00The host types -random and every player gets a random Pokemon. Players who have not chosen after 45 seconds get one automatically. Type -repick in the first 2 minutes to choose again (2 times, level and items are kept).|r")
endfunction

function Chat_Init takes nothing returns nothing
    call TriggerAddAction(t, function Repick_OnChat)
endfunction

function Other_Msg takes nothing returns nothing
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00You already have a Pokemon. Type -repick in the first 2 minutes to choose again.|r")
endfunction
