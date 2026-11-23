"""One-off edit (v3.4): -legend gives 4 wishes, the Legend Wish NPC spends them (random roll with pity, or choose a legend)."""
import io

P = 'tools/jass/mega.j'
s = io.open(P, encoding='utf-8', newline='').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep("timer Duel_Timer = CreateTimer()\n", """timer Duel_Timer = CreateTimer()
// wish (v3.4): -legend gives 4 wishes once; the Legend Wish NPC (click it) spends them
unit Wish_Npc = null
constant real Wish_X = 2356.0
constant real Wish_Y = 260.0
boolean array Wish_Got
integer array Wish_Left
integer array Wish_Tok                  // tokens: 2 tokens = the next random wish is a sure legend with x2 reward
integer array Wish_Page
integer array Wish_Mode                 // 0 = main menu, 1 = list of legends to choose from
dialog array Wish_Dlg
button array Wish_Btn
integer array Wish_Val
""")

wish = r'''// ---------------------------------------------------------------------------------------------
// Legend wish (v3.4). -legend: 4 free wishes (once). Legend Wish NPC: a random wish (1 wish) gives a random legend Soul
// with 40% chance, otherwise 1 token; with 2 tokens the next random wish is a sure legend and gives 2 Souls. Choosing a
// legend yourself costs 2 wishes.
function Wish_Give takes integer pid, integer li, integer count returns nothing
    local unit h = Duel_Hero(pid)
    local integer n = 0
    loop
        exitwhen n >= count
        if h != null then
            call UnitAddItemById(h, Leg_Soul[li])
        else
            call CreateItem(Leg_Soul[li], Wish_X, Wish_Y)
        endif
        set n = n + 1
    endloop
    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 10.0, "|cffff66ccWish: " + Leg_Name[li] + " Soul x" + I2S(count) + "! Hold it in slot 1 and walk into the centre circle.|r")
    set h = null
endfunction

function Wish_Show takes integer pid returns nothing
    local dialog d = Wish_Dlg[pid]
    local integer b = pid * 12
    local integer n = 0
    local integer k = 0
    local integer page = Wish_Page[pid]
    local integer pages = (Leg_N + 7) / 8
    local string msg = ""
    call DialogClear(d)
    if Wish_Mode[pid] == 0 then
        set msg = "Legend Wish - wishes left: " + I2S(Wish_Left[pid]) + " | tokens: " + I2S(Wish_Tok[pid]) + "/2 (2 tokens: the next random wish is a sure legend, x2)"
        set Wish_Btn[b + n] = DialogAddButton(d, "Random wish (1 wish)", 0)
        set Wish_Val[b + n] = 1
        set n = n + 1
        set Wish_Btn[b + n] = DialogAddButton(d, "Choose a legend (2 wishes)", 0)
        set Wish_Val[b + n] = 2
        set n = n + 1
    else
        if page < 0 then
            set page = 0
        endif
        set Wish_Page[pid] = page
        loop
            exitwhen k >= 8 or page * 8 + k >= Leg_N
            set Wish_Btn[b + n] = DialogAddButton(d, Leg_Name[page * 8 + k], 0)
            set Wish_Val[b + n] = 100 + page * 8 + k
            set n = n + 1
            set k = k + 1
        endloop
        if page > 0 then
            set Wish_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
            set Wish_Val[b + n] = -1
            set n = n + 1
        endif
        if page < pages - 1 then
            set Wish_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
            set Wish_Val[b + n] = -2
            set n = n + 1
        endif
        set Wish_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Wish_Val[b + n] = -4
        set n = n + 1
        set msg = "Choose a legend (2 wishes), page " + I2S(page + 1) + " of " + I2S(pages)
    endif
    set Wish_Btn[b + n] = DialogAddButton(d, "Close", 0)
    set Wish_Val[b + n] = -3
    call DialogSetMessage(d, msg)
    call DialogDisplay(Player(pid), d, true)
    set d = null
endfunction

function Wish_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer v = 0
    local integer b = 0
    loop
        exitwhen pid >= 12 or Wish_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid < 12 and Leg_N > 0 then
        set b = pid * 12
        loop
            exitwhen i >= 12 or Wish_Btn[b + i] == bt
            set i = i + 1
        endloop
        if i < 12 then
            set v = Wish_Val[b + i]
            if v == 1 then
                if Wish_Left[pid] < 1 then
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 6.0, "|cffffcc00No wishes left. Type -legend to get 4 free wishes.|r")
                else
                    set Wish_Left[pid] = Wish_Left[pid] - 1
                    if Wish_Tok[pid] >= 2 then
                        set Wish_Tok[pid] = 0
                        call Wish_Give(pid, GetRandomInt(0, Leg_N - 1), 2)
                    elseif GetRandomInt(1, 100) <= 40 then
                        call Wish_Give(pid, GetRandomInt(0, Leg_N - 1), 1)
                    else
                        set Wish_Tok[pid] = Wish_Tok[pid] + 1
                        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cffffcc00Wish: a token (" + I2S(Wish_Tok[pid]) + "/2).|r")
                    endif
                endif
                set Wish_Mode[pid] = 0
                call Wish_Show(pid)
            elseif v == 2 then
                if Wish_Left[pid] < 2 then
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 6.0, "|cffffcc00Choosing a legend needs 2 wishes.|r")
                    call Wish_Show(pid)
                else
                    set Wish_Mode[pid] = 1
                    set Wish_Page[pid] = 0
                    call Wish_Show(pid)
                endif
            elseif v >= 100 then
                if Wish_Left[pid] >= 2 then
                    set Wish_Left[pid] = Wish_Left[pid] - 2
                    call Wish_Give(pid, v - 100, 1)
                endif
                set Wish_Mode[pid] = 0
                call Wish_Show(pid)
            elseif v == -1 then
                set Wish_Page[pid] = Wish_Page[pid] - 1
                call Wish_Show(pid)
            elseif v == -2 then
                set Wish_Page[pid] = Wish_Page[pid] + 1
                call Wish_Show(pid)
            elseif v == -4 then
                set Wish_Mode[pid] = 0
                call Wish_Show(pid)
            endif
        endif
    endif
    set d = null
    set bt = null
endfunction

function Wish_IsNpc takes nothing returns boolean
    return GetTriggerUnit() == Wish_Npc
endfunction

function Wish_OnSelect takes nothing returns nothing
    local integer pid = GetPlayerId(GetTriggerPlayer())
    set Wish_Mode[pid] = 0
    call Wish_Show(pid)
endfunction

function Wish_OnChat takes nothing returns nothing
    local integer pid = GetPlayerId(GetTriggerPlayer())
    if Wish_Got[pid] then
        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cffffcc00You already took your wishes. Wishes left: " + I2S(Wish_Left[pid]) + ". Click the Legend Wish NPC to use them.|r")
    else
        set Wish_Got[pid] = true
        set Wish_Left[pid] = 4
        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 10.0, "|cffff66ccYou got 4 wishes! Click the Legend Wish NPC to use them.|r")
        call PingMinimapForPlayer(Player(pid), Wish_X, Wish_Y, 6.0)
    endif
endfunction

function Wish_Init takes nothing returns nothing
    local trigger wc = CreateTrigger()
    local trigger ws = CreateTrigger()
    local trigger wd = CreateTrigger()
    local texttag tt = CreateTextTag()
    local integer i = 0
    set Wish_Npc = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'hpea', Wish_X, Wish_Y, 270.0)
    call SetUnitScale(Wish_Npc, 1.8, 1.8, 1.8)
    call SetUnitVertexColor(Wish_Npc, 255, 120, 220, 255)
    call SetUnitInvulnerable(Wish_Npc, true)
    call SetTextTagText(tt, "|cffff66ccLEGEND WISH|r (click)", 0.024)
    call SetTextTagPos(tt, Wish_X - 110.0, Wish_Y, 160.0)
    call SetTextTagPermanent(tt, true)
    call SetTextTagVisibility(tt, true)
    loop
        exitwhen i >= 12
        set Wish_Dlg[i] = DialogCreate()
        call TriggerRegisterPlayerChatEvent(wc, Player(i), "-legend", true)
        call TriggerRegisterPlayerUnitEvent(ws, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
        call TriggerRegisterDialogEvent(wd, Wish_Dlg[i])
        set i = i + 1
    endloop
    call TriggerAddAction(wc, function Wish_OnChat)
    call TriggerAddCondition(ws, Condition(function Wish_IsNpc))
    call TriggerAddAction(ws, function Wish_OnSelect)
    call TriggerAddAction(wd, function Wish_OnClick)
    set wc = null
    set ws = null
    set wd = null
    set tt = null
endfunction

'''
rep("function Npc_IsMan takes nothing returns boolean", wish + "function Npc_IsMan takes nothing returns boolean")
rep("    call Duel_Init()\n", "    call Duel_Init()\n    call Wish_Init()\n")
io.open(P, 'w', encoding='utf-8', newline='').write(s)

P = 'tools/jasscheck.py'
s = io.open(P, encoding='utf-8', newline='').read()
if "'PingMinimapForPlayer'" not in s:
    s = s.replace("'SetUnitMoveSpeed': 2,", "'SetUnitMoveSpeed': 2, 'PingMinimapForPlayer': 4,", 1)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
