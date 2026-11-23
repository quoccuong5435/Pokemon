// v3.4.5 (proposal 11): one item NPC with a dialog list replaces the Battle Shop / Item Shop buildings.
// Click the NPC (or type -items next to it): a dialog lists the items, 8 per page, with the price. Click an item:
// its description and Buy / Back. Buy takes the gold and gives the item to the hero (battle items: at most 3).
// Ish_Code of the buttons: item k (>= 0), -1 previous page, -2 next page, -3 close, -4 buy, -5 back.

function Ish_Near takes unit h returns boolean
    local real dx = GetUnitX(h) - Ish_X
    local real dy = GetUnitY(h) - Ish_Y
    return dx * dx + dy * dy <= Npc_Range * Npc_Range
endfunction

// v3.4.6: battle items the hero holds (x / 3), shown in the dialog
function Ish_Battles takes unit h returns integer
    local integer s = 0
    local integer n = 0
    if h == null then
        return 0
    endif
    loop
        exitwhen s >= 6
        if UnitItemInSlot(h, s) != null and LoadInteger(Mega_HT, GetItemTypeId(UnitItemInSlot(h, s)), 90) == 3 then
            set n = n + 1
        endif
        set s = s + 1
    endloop
    return n
endfunction

function Ish_Show takes integer pid returns nothing
    local integer b = pid * 12
    local integer n = 0
    local integer k = 0
    local integer last = 0
    local integer s = Ish_Sel[pid]
    local dialog d = Ish_Dlg[pid]
    local string msg = ""
    local string info = "Gold " + I2S(GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD)) + " | Battle items " + I2S(Ish_Battles(Ish_Hero[pid])) + "/3"
    call DialogClear(d)
    if s >= 0 then
        set msg = Ish_Name[s] + " - " + I2S(Ish_Price[s]) + " gold|n" + Ish_Desc[s] + "|n" + info
        set Ish_Bt[b + n] = DialogAddButton(d, "Buy", 0)
        set Ish_Code[b + n] = -4
        set n = n + 1
        set Ish_Bt[b + n] = DialogAddButton(d, "Back", 0)
        set Ish_Code[b + n] = -5
        set n = n + 1
    else
        set msg = "Item shop, page " + I2S(Ish_Page[pid] + 1) + "/" + I2S((Ish_N + 7) / 8) + ". Choose an item:|n" + info
        set k = Ish_Page[pid] * 8
        set last = k + 8
        if last > Ish_N then
            set last = Ish_N
        endif
        loop
            exitwhen k >= last
            set Ish_Bt[b + n] = DialogAddButton(d, Ish_Name[k] + " - " + I2S(Ish_Price[k]), 0)
            set Ish_Code[b + n] = k
            set n = n + 1
            set k = k + 1
        endloop
        if Ish_Page[pid] > 0 then
            set Ish_Bt[b + n] = DialogAddButton(d, "< Previous page", 0)
            set Ish_Code[b + n] = -1
            set n = n + 1
        endif
        if (Ish_Page[pid] + 1) * 8 < Ish_N then
            set Ish_Bt[b + n] = DialogAddButton(d, "Next page >", 0)
            set Ish_Code[b + n] = -2
            set n = n + 1
        endif
        set Ish_Bt[b + n] = DialogAddButton(d, "Close", 0)
        set Ish_Code[b + n] = -3
        set n = n + 1
    endif
    call DialogSetMessage(d, msg)
    call DialogDisplay(Player(pid), d, true)
endfunction

function Ish_Open takes player p returns nothing
    local integer pid = GetPlayerId(p)
    local unit u = null
    local unit h = null
    call GroupEnumUnitsOfPlayer(Ish_Tmp, p, null)
    loop
        set u = FirstOfGroup(Ish_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Ish_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then
            set h = u
        endif
    endloop
    if h == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You need a living Pokemon.|r")
    elseif not Ish_Near(h) then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Go to the item NPC first.|r")
    else
        set Ish_Hero[pid] = h
        set Ish_Sel[pid] = -1
        set Ish_Page[pid] = 0
        call Ish_Show(pid)
    endif
    set u = null
    set h = null
endfunction

function Ish_OnSelect takes nothing returns nothing
    call Ish_Open(GetTriggerPlayer())
endfunction

function Ish_OnChat takes nothing returns nothing
    call Ish_Open(GetTriggerPlayer())
endfunction

function Ish_Buy takes integer pid, integer k returns nothing
    local unit h = Ish_Hero[pid]
    local player p = Player(pid)
    local integer s = 0
    local integer battles = 0
    local item it = null
    if h == null or GetWidgetLife(h) <= 0.405 or k < 0 or k >= Ish_N then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Choose a living Pokemon and an item first.|r")
        return
    endif
    if GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) < Ish_Price[k] then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Not enough gold.|r")
        return
    endif
    // battle items: at most 3 on a Pokemon (Mega_HT key 90 = 3 on the item type)
    if LoadInteger(Mega_HT, Itm_Id[k], 90) == 3 then
        loop
            exitwhen s >= 6
            set it = UnitItemInSlot(h, s)
            if it != null and LoadInteger(Mega_HT, GetItemTypeId(it), 90) == 3 then
                set battles = battles + 1
            endif
            set s = s + 1
        endloop
        if battles >= 3 then
            call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00At most 3 battle items on a Pokemon.|r")
            set it = null
            return
        endif
    endif
    set s = 0
    loop
        exitwhen s >= 6 or UnitItemInSlot(h, s) == null
        set s = s + 1
    endloop
    if s >= 6 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00The inventory is full.|r")
        return
    endif
    call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) - Ish_Price[k])
    set it = CreateItem(Itm_Id[k], GetUnitX(h), GetUnitY(h))
    call UnitAddItem(h, it)
    call Itm_Refresh(h)
    call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cff66ff66Bought " + Ish_Name[k] + ".|r")
    set it = null
    set h = null
endfunction

function Ish_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer choice = -3
    local integer b = 0
    loop
        exitwhen pid >= 12 or Ish_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid >= 12 then
        return
    endif
    set b = pid * 12
    loop
        exitwhen i >= 12
        if Ish_Bt[b + i] == bt then
            set choice = Ish_Code[b + i]
            set i = 12
        endif
        set i = i + 1
    endloop
    if choice >= 0 then
        set Ish_Sel[pid] = choice
        call Ish_Show(pid)
    elseif choice == -1 then
        set Ish_Page[pid] = Ish_Page[pid] - 1
        call Ish_Show(pid)
    elseif choice == -2 then
        set Ish_Page[pid] = Ish_Page[pid] + 1
        call Ish_Show(pid)
    elseif choice == -4 then
        call Ish_Buy(pid, Ish_Sel[pid])
        set Ish_Sel[pid] = -1
        call Ish_Show(pid)
    elseif choice == -5 then
        set Ish_Sel[pid] = -1
        call Ish_Show(pid)
    endif
endfunction

function Ish_IsNpc takes nothing returns boolean
    return GetTriggerUnit() == Ish_Npc
endfunction

// at map start: the item NPC, its label, the dialogs and their triggers
function Ish_Init takes nothing returns nothing
    local integer i = 0
    local trigger t = null
    local texttag tt = null
    set Ish_Tmp = CreateGroup()
    // v3.4.6: the item NPC looks like a Goblin Merchant (the moves NPC stays a peasant)
    set Ish_Npc = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'ngme', Ish_X, Ish_Y, 0.0)
    call SetUnitScale(Ish_Npc, 1.8, 1.8, 1.8)
    call SetUnitInvulnerable(Ish_Npc, true)
    call CreateMinimapIcon(Ish_X, Ish_Y, 255, 215, 0, "UI\\Minimap\\MiniMap-QuestObjective.mdl", FOG_OF_WAR_VISIBLE)  // v3.4.6 A1
    set tt = CreateTextTag()
    call SetTextTagText(tt, "|cffffcc00ITEM SHOP|r (click)", 0.024)
    call SetTextTagPos(tt, Ish_X - 110.0, Ish_Y, 160.0)
    call SetTextTagPermanent(tt, true)
    call SetTextTagVisibility(tt, true)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerUnitEvent(t, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
        set i = i + 1
    endloop
    call TriggerAddCondition(t, Condition(function Ish_IsNpc))
    call TriggerAddAction(t, function Ish_OnSelect)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-items", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Ish_OnChat)
    set i = 0
    loop
        exitwhen i >= 12
        set Ish_Dlg[i] = DialogCreate()
        set Ish_Sel[i] = -1
        set i = i + 1
    endloop
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterDialogEvent(t, Ish_Dlg[i])
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Ish_OnClick)
    set t = null
    set tt = null
endfunction
