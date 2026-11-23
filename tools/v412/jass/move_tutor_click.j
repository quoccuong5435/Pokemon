function Npc_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer b = 0
    local integer kind = 0
    local integer m = 0
    local integer s = 0
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
            set kind = Npc_Kind[b + i]
            if kind == 0 then
                call DialogDisplay(Player(pid), d, false)
            else
                if kind == 1 then
                    set Npc_Mode[pid] = 2
                    set Npc_TMPage[pid] = 0
                elseif kind == 2 then
                    set Npc_Mode[pid] = 1
                    set Npc_TMPage[pid] = 0
                elseif kind == 3 then
                    set Npc_Mode[pid] = 4
                elseif kind == 4 then
                    set Npc_Mode[pid] = 0
                elseif kind == 5 then
                    set Npc_TMPage[pid] = Npc_TMPage[pid] - 1
                elseif kind == 6 then
                    set Npc_TMPage[pid] = Npc_TMPage[pid] + 1
                elseif kind == 7 then
                    set m = Npc_Val[b + i]
                    if not Mv_Known(h, m) then
                        set s = Mv_FreeSlot(h)
                        if s >= 0 then
                            call MT_Buy(pid, h, s, m, MT_CostOf(pid, m))
                        else
                            set MT_Pend[pid] = m
                            set MT_PendCost[pid] = MT_CostOf(pid, m)
                            set MT_PrevMode[pid] = Npc_Mode[pid]
                            set Npc_Mode[pid] = 3
                        endif
                    endif
                elseif kind == 8 then
                    if not Mv_Known(h, MT_Pend[pid]) then
                        call MT_Buy(pid, h, Npc_Val[b + i], MT_Pend[pid], MT_PendCost[pid])
                    endif
                    set Npc_Mode[pid] = MT_PrevMode[pid]
                elseif kind == 9 then
                    call Mv_Clear(h, Npc_Val[b + i])
                    if not MT_AnyMove(h) then
                        set Npc_Mode[pid] = 0
                    endif
                elseif kind == 10 then
                    set Npc_Mode[pid] = MT_PrevMode[pid]
                else
                    set Npc_Mode[pid] = 0
                endif
                call Npc_Show(pid, h, -1)
            endif
        endif
    endif
    set d = null
    set bt = null
    set h = null
endfunction
