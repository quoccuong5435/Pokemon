// ===== move_tutor (tools/v412/move_tutor.py): moves NPC, move first then slot =====
// Npc_Mode: 0 home, 1 TM/HM list, 2 level-up list, 3 replace which slot, 4 forget list
// Lists are sorted best first (power, +50% when the move has the hero's type), 9 a page (Npc_TMPage).
function MT_Stab takes unit h, integer m returns boolean
    return m >= 0 and Mv_Pow[m] > 0 and Mv_Type[m] >= 0 and Ty_Has(h, Mv_Type[m])
endfunction

function MT_KeyOf takes unit h, integer m returns integer
    local integer keyVal = Mv_Score[m]
    if m >= Fx_StatBase or Mv_Pow[m] <= 0 then
        set keyVal = 45
    endif
    if MT_Stab(h, m) then
        set keyVal = keyVal + keyVal / 2
    endif
    return keyVal
endfunction

function MT_CostOf takes integer pid, integer m returns integer
    if Npc_Mode[pid] == 1 then
        return PAX_Npc_TMCost(m)
    endif
    return Npc_LearnCost
endfunction

function MT_Add takes integer pid, unit h, integer m returns nothing
    local integer base = pid * MT_Max
    local integer n = MT_CandN[pid]
    local integer k = 0
    if m < 0 or n >= MT_Max or Mv_Known(h, m) then
        return
    endif
    loop
        exitwhen k >= n
        if MT_Cand[base + k] == m then
            return
        endif
        set k = k + 1
    endloop
    set MT_Cand[base + n] = m
    set MT_Sc[base + n] = MT_KeyOf(h, m)
    set MT_CandN[pid] = n + 1
endfunction

// mode 1 = TM/HM list, 2 = level-up moves the hero's level allows; result in MT_Cand, best first
function MT_Build takes integer pid, unit h, integer mode returns nothing
    local integer id = GetUnitTypeId(h)
    local integer base = pid * MT_Max
    local integer cnt = 0
    local integer k = 0
    local integer j = 0
    local integer best = 0
    local integer tmp = 0
    set MT_CandN[pid] = 0
    if mode == 1 then
        set cnt = LoadInteger(Ab_HT, id, 299)
        loop
            exitwhen k >= cnt
            call MT_Add(pid, h, LoadInteger(Ab_HT, id, 300 + k))
            set k = k + 1
        endloop
    else
        set cnt = LoadInteger(Ab_HT, id, 99)
        loop
            exitwhen k >= cnt
            if LoadInteger(Ab_HT, id, 101 + 2 * k) <= GetHeroLevel(h) then
                call MT_Add(pid, h, LoadInteger(Ab_HT, id, 100 + 2 * k))
            endif
            set k = k + 1
        endloop
    endif
    set cnt = MT_CandN[pid]
    set k = 0
    loop
        exitwhen k >= cnt - 1
        set best = k
        set j = k + 1
        loop
            exitwhen j >= cnt
            if MT_Sc[base + j] > MT_Sc[base + best] then
                set best = j
            endif
            set j = j + 1
        endloop
        if best != k then
            set tmp = MT_Cand[base + k]
            set MT_Cand[base + k] = MT_Cand[base + best]
            set MT_Cand[base + best] = tmp
            set tmp = MT_Sc[base + k]
            set MT_Sc[base + k] = MT_Sc[base + best]
            set MT_Sc[base + best] = tmp
        endif
        set k = k + 1
    endloop
endfunction

function MT_SlotName takes unit h, integer s returns string
    if Mv_Slot(h, s) < 0 then
        return "-"
    endif
    return PAX_Npc_MoveName(Mv_Slot(h, s))
endfunction

function MT_AnyMove takes unit h returns boolean
    local integer k = 0
    loop
        exitwhen k >= Mv_Slots
        if Mv_Slot(h, k) >= 0 then
            return true
        endif
        set k = k + 1
    endloop
    return false
endfunction

function MT_Buy takes integer pid, unit h, integer s, integer m, integer cost returns boolean
    local player p = Player(pid)
    if GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) < cost then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Not enough gold.|r")
        set p = null
        return false
    endif
    call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) - cost)
    call Mv_Put(h, s, m)
    call SaveInteger(Ab_HT, GetHandleId(h), 200 + m, 1)
    call Mv_Notify(h, m)
    set p = null
    return true
endfunction

function Npc_Show takes integer pid, unit h, integer s returns nothing
    local integer b = pid * 12
    local integer base = pid * MT_Max
    local integer n = 0
    local integer k = 0
    local integer m = 0
    local integer cnt = 0
    local integer first = 0
    local integer pages = 1
    local string msg = ""
    local string tag = ""
    local dialog d = Npc_Dlg[pid]
    local player p = Player(pid)
    set Npc_Slot[pid] = s
    call DialogClear(d)
    if Npc_Mode[pid] == 3 then
        set m = MT_Pend[pid]
        set msg = GetHeroProperName(h) + " learns " + PAX_Npc_MoveName(m) + " (" + PAX_Npc_PriceStr(MT_PendCost[pid]) + "). Replace which move?"
        loop
            exitwhen k >= Mv_Slots
            set Npc_Btn[b + n] = DialogAddButton(d, "Slot " + I2S(k + 1) + ": " + Npc_Label(h, k), 0)
            set Npc_Kind[b + n] = 8
            set Npc_Val[b + n] = k
            set n = n + 1
            set k = k + 1
        endloop
        set Npc_Btn[b + n] = DialogAddButton(d, "Cancel", 0)
        set Npc_Kind[b + n] = 10
        set n = n + 1
    elseif Npc_Mode[pid] == 4 then
        set msg = "Forget which move? (free)"
        loop
            exitwhen k >= Mv_Slots
            if Mv_Slot(h, k) >= 0 then
                set Npc_Btn[b + n] = DialogAddButton(d, "Forget " + PAX_Npc_MoveName(Mv_Slot(h, k)), 0)
                set Npc_Kind[b + n] = 9
                set Npc_Val[b + n] = k
                set n = n + 1
            endif
            set k = k + 1
        endloop
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 4
        set n = n + 1
    elseif Npc_Mode[pid] == 1 or Npc_Mode[pid] == 2 then
        call MT_Build(pid, h, Npc_Mode[pid])
        set cnt = MT_CandN[pid]
        if Npc_TMPage[pid] < 0 or Npc_TMPage[pid] * 9 >= cnt then
            set Npc_TMPage[pid] = 0
        endif
        set first = Npc_TMPage[pid] * 9
        if cnt > 9 then
            set pages = (cnt + 8) / 9
        endif
        if Npc_Mode[pid] == 1 then
            set msg = "TM/HM moves, best first"
        else
            set msg = "Level-up moves, best first"
        endif
        if cnt == 0 then
            set msg = msg + ": nothing new to learn"
        elseif pages > 1 then
            set msg = msg + " (page " + I2S(Npc_TMPage[pid] + 1) + "/" + I2S(pages) + ")"
        endif
        set k = first
        loop
            exitwhen k >= cnt or k >= first + 9
            set m = MT_Cand[base + k]
            set tag = ""
            if MT_Stab(h, m) then
                set tag = " STAB"
            endif
            set Npc_Btn[b + n] = DialogAddButton(d, PAX_Npc_ShortMove(m, MT_CostOf(pid, m)) + tag, 0)
            set Npc_Kind[b + n] = 7
            set Npc_Val[b + n] = m
            set n = n + 1
            set k = k + 1
        endloop
        if Npc_TMPage[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
            set Npc_Kind[b + n] = 5
            set n = n + 1
        endif
        if first + 9 < cnt then
            set Npc_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
            set Npc_Kind[b + n] = 6
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 4
        set n = n + 1
    else
        set Npc_Mode[pid] = 0
        set msg = GetHeroProperName(h) + ": " + MT_SlotName(h, 0) + " / " + MT_SlotName(h, 1) + " / " + MT_SlotName(h, 2) + " / " + MT_SlotName(h, 3)
        call MT_Build(pid, h, 2)
        if MT_CandN[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Level-up moves (" + I2S(MT_CandN[pid]) + " new, " + PAX_Npc_PriceStr(Npc_LearnCost) + ")", 0)
            set Npc_Kind[b + n] = 1
            set n = n + 1
        endif
        call MT_Build(pid, h, 1)
        if MT_CandN[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "TM/HM moves (" + I2S(MT_CandN[pid]) + ", 3k - 15k)", 0)
            set Npc_Kind[b + n] = 2
            set n = n + 1
        endif
        if MT_AnyMove(h) then
            set Npc_Btn[b + n] = DialogAddButton(d, "Forget a move", 0)
            set Npc_Kind[b + n] = 3
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Close", 0)
        set Npc_Kind[b + n] = 0
        set n = n + 1
    endif
    call DialogSetMessage(d, msg)
    call DialogDisplay(p, d, true)
    set d = null
    set p = null
endfunction
