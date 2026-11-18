// v3.4.16: moves NPC with a price and requirements per move and a confirm screen with the move's details
// (replaces Npc_Show / Npc_OnClick of the base script). Npc_Mode: 0 slot menu, 1 TM list, 2 confirm
// (Npc_Pend[pid] move, Npc_PendTm[pid] from the TM list). Button kinds: 12 buy, 13 back from the confirm screen.
function Npc_Show takes integer pid, unit h, integer s returns nothing
    local integer b = pid * 12
    local integer k = 0
    local integer n = 0
    local integer id = GetUnitTypeId(h)
    local integer m = 0
    local integer lv = 0
    local integer cnt = 0
    local integer shown = 0
    local string msg = ""
    local string need = ""
    local dialog d = Npc_Dlg[pid]
    local player p = Player(pid)
    set Npc_Slot[pid] = s
    call DialogClear(d)
    if s < 0 then
        set msg = "Moves of " + GetHeroProperName(h) + ". Choose a slot:"
        loop
            exitwhen k >= Mv_Slots
            set Npc_Btn[b + k] = DialogAddButton(d, "Slot " + I2S(k + 1) + ": " + Npc_Label(h, k), 0)
            set Npc_Kind[b + k] = 1
            set Npc_Val[b + k] = k
            set k = k + 1
        endloop
        set n = Mv_Slots
        set Npc_Btn[b + n] = DialogAddButton(d, "Close", 0)
        set Npc_Kind[b + n] = 0
        set n = n + 1
    elseif Npc_Mode[pid] == 2 then
        set m = Npc_Pend[pid]
        set need = Fx_MoveNeedText(m, Npc_PendTm[pid])
        set msg = Mv_Label[m] + " - " + I2S(Fx_MovePrice(m, Npc_PendTm[pid])) + " gold (details in the chat)"
        call Fx_MoveDetail(pid, h, m, Npc_PendTm[pid])
        if Fx_MoveCanBuy(pid, h, m, Npc_PendTm[pid]) then
            set Npc_Btn[b + n] = DialogAddButton(d, "Buy for " + I2S(Fx_MovePrice(m, Npc_PendTm[pid])) + " gold", 0)
            set Npc_Kind[b + n] = 12
        else
            set Npc_Btn[b + n] = DialogAddButton(d, "Locked: needs " + need, 0)
            set Npc_Kind[b + n] = 13
        endif
        set n = n + 1
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 13
        set n = n + 1
    elseif Npc_Mode[pid] == 1 then
        set msg = "TM/HM moves for slot " + I2S(s + 1) + " (page " + I2S(Npc_TMPage[pid] + 1) + ", click one to see it)"
        set cnt = LoadInteger(Ab_HT, id, 299)
        set k = 0
        set lv = 0
        loop
            exitwhen k >= cnt
            set m = LoadInteger(Ab_HT, id, 300 + k)
            if not Mv_Known(h, m) then
                if lv >= Npc_TMPage[pid] * 8 and lv < Npc_TMPage[pid] * 8 + 8 then
                    if Fx_MoveCanBuy(pid, h, m, true) then
                        set Npc_Btn[b + n] = DialogAddButton(d, Mv_Label[m] + " - " + I2S(Fx_MovePrice(m, true)) + "g", 0)
                    else
                        set Npc_Btn[b + n] = DialogAddButton(d, "[" + Fx_MoveNeedText(m, true) + "] " + Mv_Label[m], 0)
                    endif
                    set Npc_Kind[b + n] = 6
                    set Npc_Val[b + n] = m
                    set n = n + 1
                endif
                set lv = lv + 1
            endif
            set k = k + 1
        endloop
        if Npc_TMPage[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
            set Npc_Kind[b + n] = 7
            set n = n + 1
        endif
        if lv > (Npc_TMPage[pid] + 1) * 8 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
            set Npc_Kind[b + n] = 8
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 9
        set n = n + 1
    else
        set msg = "Slot " + I2S(s + 1) + ": " + Npc_Label(h, s) + ". Click a move to see it:"
        if Mv_Slot(h, s) >= 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Forget " + Npc_Label(h, s) + " (free)", 0)
            set Npc_Kind[b + n] = 2
            set Npc_Val[b + n] = s
            set n = n + 1
        endif
        // the level-up moves are paged, 6 a page (buttons: forget + 6 + prev + next + TM + back <= 12)
        set cnt = LoadInteger(Ab_HT, id, 99)
        set shown = 0
        loop
            exitwhen k >= cnt
            set m = LoadInteger(Ab_HT, id, 100 + 2 * k)
            set lv = LoadInteger(Ab_HT, id, 101 + 2 * k)
            if lv <= GetHeroLevel(h) and not Mv_Known(h, m) then
                if shown >= Npc_LvPage[pid] * 6 and shown < Npc_LvPage[pid] * 6 + 6 then
                    set Npc_Btn[b + n] = DialogAddButton(d, Mv_Label[m] + " - " + I2S(Fx_MovePrice(m, false)) + "g", 0)
                    set Npc_Kind[b + n] = 3
                    set Npc_Val[b + n] = m
                    set n = n + 1
                endif
                set shown = shown + 1
            endif
            set k = k + 1
        endloop
        if Npc_LvPage[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
            set Npc_Kind[b + n] = 10
            set n = n + 1
        endif
        if shown > (Npc_LvPage[pid] + 1) * 6 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
            set Npc_Kind[b + n] = 11
            set n = n + 1
        endif
        if LoadInteger(Ab_HT, id, 299) > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "TM/HM moves (" + I2S(Fx_PriceTmBase + Fx_PriceTmPow * 40) + "-" + I2S(Fx_PriceTmBase + Fx_PriceTmPow * 150) + " gold)", 0)
            set Npc_Kind[b + n] = 5
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 4
        set n = n + 1
    endif
    call DialogSetMessage(d, msg)
    call DialogDisplay(p, d, true)
    set d = null
    set p = null
endfunction

function Npc_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer b = 0
    local integer cost = 0
    local integer m = 0
    local unit h = null
    loop
        exitwhen pid >= 12 or Npc_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid < 12 then
        set b = pid * 12
        loop
            exitwhen i >= 12 or Npc_Btn[b + i] == bt
            set i = i + 1
        endloop
        set h = Npc_Unit[pid]
        if i < 12 and h != null and GetUnitTypeId(h) != 0 then
            if Npc_Kind[b + i] == 0 then
                call DialogDisplay(Player(pid), d, false)
            elseif Npc_Kind[b + i] == 1 then
                set Npc_LvPage[pid] = 0
                set Npc_Mode[pid] = 0
                call Npc_Show(pid, h, Npc_Val[b + i])
            elseif Npc_Kind[b + i] == 10 then
                set Npc_LvPage[pid] = Npc_LvPage[pid] - 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 11 then
                set Npc_LvPage[pid] = Npc_LvPage[pid] + 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 2 then
                call Mv_Clear(h, Npc_Val[b + i])
                call Npc_Show(pid, h, -1)
            elseif Npc_Kind[b + i] == 5 then
                set Npc_Mode[pid] = 1
                set Npc_TMPage[pid] = 0
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 7 then
                set Npc_TMPage[pid] = Npc_TMPage[pid] - 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 8 then
                set Npc_TMPage[pid] = Npc_TMPage[pid] + 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 9 then
                set Npc_Mode[pid] = 0
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 3 or Npc_Kind[b + i] == 6 then
                // a move was clicked: the confirm screen with its details
                set Npc_Pend[pid] = Npc_Val[b + i]
                set Npc_PendTm[pid] = Npc_Kind[b + i] == 6
                set Npc_Mode[pid] = 2
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 13 then
                if Npc_PendTm[pid] then
                    set Npc_Mode[pid] = 1
                else
                    set Npc_Mode[pid] = 0
                endif
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 12 then
                set m = Npc_Pend[pid]
                set cost = Fx_MovePrice(m, Npc_PendTm[pid])
                if not Fx_MoveCanBuy(pid, h, m, Npc_PendTm[pid]) then
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffff4040This move needs " + Fx_MoveNeedText(m, Npc_PendTm[pid]) + ".|r")
                    call Npc_Show(pid, h, Npc_Slot[pid])
                elseif GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) >= cost then
                    call SetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) - cost)
                    call Mv_Put(h, Npc_Slot[pid], m)
                    call SaveInteger(Ab_HT, GetHandleId(h), 200 + m, 1)
                    call Mv_Notify(h, m)
                    call Mv_Tips(h)
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 6.0, "|cff66ff66Learned " + Mv_Label[m] + " for " + I2S(cost) + " gold.|r")
                    set Npc_Mode[pid] = 0
                    call Npc_Show(pid, h, -1)
                else
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Not enough gold (" + I2S(cost) + " needed).|r")
                    call Npc_Show(pid, h, Npc_Slot[pid])
                endif
            else
                set Npc_Mode[pid] = 0
                call Npc_Show(pid, h, -1)
            endif
        endif
    endif
    set d = null
    set bt = null
    set h = null
endfunction
