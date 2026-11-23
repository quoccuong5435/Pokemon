// ===== move_tutor (tools/v412/move_tutor.py): level-up move question, Pokemon style =====
// A hero with 4 moves that reaches a new level-up move: its human owner chooses the slot to replace or skips.
// The question waits while an enemy is within LvAsk_Range (a dialog blocks the player's controls).
// Computer / neutral owners keep the old rule (replace the weakest move when the new one scores higher).
function LvAsk_IsHuman takes player p returns boolean
    return GetPlayerController(p) == MAP_CONTROL_USER and GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING
endfunction

function LvAsk_EnemyNear takes unit u returns boolean
    local player p = GetOwningPlayer(u)
    local unit x = null
    local boolean found = false
    call GroupEnumUnitsInRange(LvAsk_G, GetUnitX(u), GetUnitY(u), LvAsk_Range, null)
    loop
        set x = FirstOfGroup(LvAsk_G)
        exitwhen x == null
        call GroupRemoveUnit(LvAsk_G, x)
        if not found and GetWidgetLife(x) > 0.405 and IsUnitEnemy(x, p) and not IsUnitType(x, UNIT_TYPE_STRUCTURE) and GetUnitAbilityLevel(x, 'Aloc') == 0 then
            set found = true
        endif
    endloop
    set p = null
    return found
endfunction

function LvAsk_Offer takes unit u, integer m returns nothing
    local player p = GetOwningPlayer(u)
    local integer pid = GetPlayerId(p)
    local integer h = GetHandleId(u)
    local integer k = 0
    local dialog d = null
    if pid >= 12 or not LvAsk_IsHuman(p) then
        if Mv_Score[m] > Mv_WeakScore(u) then
            call Mv_Put(u, Mv_WeakSlot(u), m)
            call Mv_Notify(u, m)
        endif
        call SaveInteger(Ab_HT, h, 200 + m, 1)
        set p = null
        return
    endif
    if LvAsk_Move[pid] != 0 then
        set p = null
        return
    endif
    if LvAsk_EnemyNear(u) then
        if not LoadBoolean(LvAsk_HT, h, m) then
            call SaveBoolean(LvAsk_HT, h, m, true)
            call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00" + GetHeroProperName(u) + " can learn " + Mv_Label[m] + ". You choose once no enemy is near.|r")
        endif
        set p = null
        return
    endif
    set d = LvAsk_Dlg[pid]
    call DialogClear(d)
    call DialogSetMessage(d, GetHeroProperName(u) + " wants to learn " + Mv_Label[m] + ". Forget which move?")
    loop
        exitwhen k >= Mv_Slots
        set LvAsk_Btn[pid * 6 + k] = DialogAddButton(d, "Slot " + I2S(k + 1) + ": " + Mv_Label[Mv_Slot(u, k)], 0)
        set k = k + 1
    endloop
    set LvAsk_Btn[pid * 6 + Mv_Slots] = DialogAddButton(d, "Skip (learn it later at the moves NPC)", 0)
    set LvAsk_Unit[pid] = u
    set LvAsk_Move[pid] = m + 1
    call DialogDisplay(p, d, true)
    set d = null
    set p = null
endfunction

function LvAsk_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer k = 0
    local integer m = 0
    local unit u = null
    loop
        exitwhen pid >= 12 or LvAsk_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid < 12 and LvAsk_Move[pid] != 0 then
        set m = LvAsk_Move[pid] - 1
        set u = LvAsk_Unit[pid]
        loop
            exitwhen k > Mv_Slots or LvAsk_Btn[pid * 6 + k] == bt
            set k = k + 1
        endloop
        if u != null and GetUnitTypeId(u) != 0 then
            if k < Mv_Slots and not Mv_Known(u, m) then
                call Mv_Put(u, k, m)
                call Mv_Notify(u, m)
            endif
            call SaveInteger(Ab_HT, GetHandleId(u), 200 + m, 1)
        endif
        set LvAsk_Move[pid] = 0
        set LvAsk_Unit[pid] = null
    endif
    set d = null
    set bt = null
    set u = null
endfunction

