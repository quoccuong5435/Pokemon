"""One-off edit (v3.4): badges + level cap, duel commands, gym team of 6 different species. Run from _PokemonArena2.0_work."""
import io

P = 'tools/jass/mega.j'
s = io.open(P, encoding='utf-8', newline='').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep("integer array Gym_Chain\n", """integer array Gym_Chain
integer array Gym_Used                  // g * 6 + k: wild type of the k-th Pokemon of the current challenge
// badges and level cap (v3.4): a cleared gym gives a badge; XP stops at the level cap of the badges
boolean array Badge_Has                 // pid * 8 + gym index
// duel (v3.4): -duel <player>, -accept, -decline, -rank
integer array Duel_Foe                  // opponent player id while dueling (-1 = none)
integer array Duel_Ask                  // player id that challenged this player (-1 = none)
unit array Duel_U
real array Duel_RX
real array Duel_RY
real array Duel_T
boolean array Duel_Allied               // a * 12 + b: they were allies before the duel
integer array Duel_Wins
integer array Duel_Losses
timer Duel_Timer = CreateTimer()
""")

rep("function Hero_HPSync takes unit u returns nothing", """function Badge_Count takes integer pid returns integer
    local integer g = 0
    local integer n = 0
    loop
        exitwhen g >= 8
        if Badge_Has[pid * 8 + g] then
            set n = n + 1
        endif
        set g = g + 1
    endloop
    return n
endfunction

function Badge_Cap takes integer pid returns integer
    local integer c = 30 + 10 * Badge_Count(pid)
    if c > 100 then
        set c = 100
    endif
    return c
endfunction

function Hero_HPSync takes unit u returns nothing""")

rep("                call Evo_Check(u)\n            endif\n        endloop\n        set pid = pid + 1",
    """                call Evo_Check(u)
                call SuspendHeroXP(u, GetHeroLevel(u) >= Badge_Cap(pid))
            endif
        endloop
        set pid = pid + 1""")

rep("""                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped.|r")""",
    """                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
                set Badge_Has[Gym_Pid[g] * 8 + g] = true
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(Gym_Pid[g])) + "/8, level cap " + I2S(Badge_Cap(Gym_Pid[g])) + ".|r")""")

# gym team: six different species
rep("""    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_PickType(pow), Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
""", """    loop
        set wt = Wild_PickType(pow)
        set j = 0
        set dup = false
        loop
            exitwhen j >= k
            if Gym_Used[g * 6 + j] == wt then
                set dup = true
            endif
            set j = j + 1
        endloop
        set tries = tries + 1
        exitwhen not dup or tries >= 30
    endloop
    set Gym_Used[g * 6 + k] = wt
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), wt, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
""")
rep("    local integer ti = 0\n    if pow < 1 then", "    local integer ti = 0\n    local integer wt = 0\n    local integer j = 0\n    local integer tries = 0\n    local boolean dup = false\n    if pow < 1 then")

duel = r'''// ---------------------------------------------------------------------------------------------
// Duel (v3.4): -duel <player name start>, then the other player types -accept. Both Pokemon are healed and the guest is
// moved next to the challenger; the duel ends when one Pokemon is under 15% HP (or dies), after 2 minutes (draw) or
// when a Pokemon is gone. Winner: +500 gold and a win in -rank.
function Duel_Hero takes integer pid returns unit
    local unit u = null
    local unit r = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, Player(pid), null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if r == null and IsUnitType(u, UNIT_TYPE_HERO) and GetUnitTypeId(u) != 'earc' and GetWidgetLife(u) > 0.405 then
            set r = u
        endif
    endloop
    set u = null
    return r
endfunction

function Duel_Heal takes unit u returns nothing
    if u != null and GetUnitTypeId(u) != 0 then
        call SetUnitState(u, UNIT_STATE_LIFE, I2R(BlzGetUnitMaxHP(u)))
        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
    endif
endfunction

function Duel_Find takes string arg, integer self returns integer
    local string a = StringCase(arg, false)
    local string n = ""
    local integer i = 0
    if a == "" then
        return -1
    endif
    loop
        exitwhen i >= 12
        if i != self and GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING then
            set n = StringCase(GetPlayerName(Player(i)), false)
            if SubString(n, 0, StringLength(a)) == a then
                return i
            endif
        endif
        set i = i + 1
    endloop
    return -1
endfunction

function Duel_Finish takes integer a, integer b, integer win returns nothing
    local integer lose = -1
    if win == a then
        set lose = b
    elseif win == b then
        set lose = a
    endif
    call SetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE, Duel_Allied[a * 12 + b])
    call SetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE, Duel_Allied[b * 12 + a])
    if GetUnitTypeId(Duel_U[a]) != 0 then
        if GetWidgetLife(Duel_U[a]) <= 0.405 then
            call ReviveHero(Duel_U[a], GetUnitX(Duel_U[a]), GetUnitY(Duel_U[a]), false)
        endif
        call Duel_Heal(Duel_U[a])
        call SetUnitPosition(Duel_U[a], Duel_RX[a], Duel_RY[a])
    endif
    if GetUnitTypeId(Duel_U[b]) != 0 then
        if GetWidgetLife(Duel_U[b]) <= 0.405 then
            call ReviveHero(Duel_U[b], GetUnitX(Duel_U[b]), GetUnitY(Duel_U[b]), false)
        endif
        call Duel_Heal(Duel_U[b])
        call SetUnitPosition(Duel_U[b], Duel_RX[b], Duel_RY[b])
    endif
    set Duel_Foe[a] = -1
    set Duel_Foe[b] = -1
    set Duel_U[a] = null
    set Duel_U[b] = null
    if win >= 0 then
        set Duel_Wins[win] = Duel_Wins[win] + 1
        set Duel_Losses[lose] = Duel_Losses[lose] + 1
        call SetPlayerState(Player(win), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(win), PLAYER_STATE_RESOURCE_GOLD) + 500)
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00Duel: " + GetPlayerName(Player(win)) + " beat " + GetPlayerName(Player(lose)) + "! (+500 gold)|r")
    else
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00Duel: " + GetPlayerName(Player(a)) + " and " + GetPlayerName(Player(b)) + " drew.|r")
    endif
endfunction

function Duel_Start takes integer a, integer b returns nothing
    local unit ha = Duel_Hero(a)
    local unit hb = Duel_Hero(b)
    if ha == null or hb == null then
        call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
        call DisplayTimedTextToPlayer(Player(b), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
    else
        set Duel_Foe[a] = b
        set Duel_Foe[b] = a
        set Duel_Ask[a] = -1
        set Duel_Ask[b] = -1
        set Duel_U[a] = ha
        set Duel_U[b] = hb
        set Duel_T[a] = 0.0
        set Duel_RX[a] = GetUnitX(ha)
        set Duel_RY[a] = GetUnitY(ha)
        set Duel_RX[b] = GetUnitX(hb)
        set Duel_RY[b] = GetUnitY(hb)
        set Duel_Allied[a * 12 + b] = GetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE)
        set Duel_Allied[b * 12 + a] = GetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE)
        call SetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE, false)
        call SetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE, false)
        call SetUnitPosition(hb, GetUnitX(ha) + 400.0, GetUnitY(ha))
        call Duel_Heal(ha)
        call Duel_Heal(hb)
        call PanCameraToTimedForPlayer(Player(b), GetUnitX(hb), GetUnitY(hb), 0.25)
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff8800Duel: " + GetPlayerName(Player(a)) + " vs " + GetPlayerName(Player(b)) + "! The first Pokemon under 15% HP loses.|r")
    endif
    set ha = null
    set hb = null
endfunction

function Duel_Tick takes nothing returns nothing
    local integer a = 0
    local integer b = 0
    local unit ha = null
    local unit hb = null
    loop
        exitwhen a >= 12
        set b = Duel_Foe[a]
        if b > a then
            set Duel_T[a] = Duel_T[a] + 0.25
            if GetUnitTypeId(Duel_U[a]) == 0 then
                set Duel_U[a] = Duel_Hero(a)
            endif
            if GetUnitTypeId(Duel_U[b]) == 0 then
                set Duel_U[b] = Duel_Hero(b)
            endif
            set ha = Duel_U[a]
            set hb = Duel_U[b]
            if ha == null or GetUnitTypeId(ha) == 0 then
                call Duel_Finish(a, b, b)
            elseif hb == null or GetUnitTypeId(hb) == 0 then
                call Duel_Finish(a, b, a)
            elseif GetWidgetLife(ha) <= 0.405 or GetWidgetLife(ha) < 0.15 * I2R(BlzGetUnitMaxHP(ha)) then
                call Duel_Finish(a, b, b)
            elseif GetWidgetLife(hb) <= 0.405 or GetWidgetLife(hb) < 0.15 * I2R(BlzGetUnitMaxHP(hb)) then
                call Duel_Finish(a, b, a)
            elseif Duel_T[a] >= 120.0 then
                call Duel_Finish(a, b, -1)
            endif
        endif
        set a = a + 1
    endloop
    set ha = null
    set hb = null
endfunction

function Duel_OnChat takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local string s = GetEventPlayerChatString()
    local string arg = SubString(s, 6, StringLength(s))
    local integer foe = Duel_Find(arg, me)
    if Duel_Foe[me] >= 0 then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00You are already in a duel.|r")
    elseif foe < 0 then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 8.0, "|cffffcc00Type -duel and the start of a player's name, for example -duel Ash.|r")
    elseif Duel_Foe[foe] >= 0 or Gym_Busy(me) or Gym_Busy(foe) then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00That player (or you) is busy in a duel or gym.|r")
    elseif Duel_Hero(me) == null or Duel_Hero(foe) == null then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
    else
        set Duel_Ask[foe] = me
        call DisplayTimedTextToPlayer(Player(foe), 0, 0, 12.0, "|cffff8800" + GetPlayerName(Player(me)) + " challenges you to a duel! Type -accept or -decline.|r")
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 8.0, "|cffffcc00Challenge sent to " + GetPlayerName(Player(foe)) + ".|r")
    endif
endfunction

function Duel_OnAccept takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local integer a = Duel_Ask[me]
    if a < 0 or Duel_Foe[a] >= 0 or Duel_Foe[me] >= 0 or Gym_Busy(me) or Gym_Busy(a) then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Nobody is waiting for your answer.|r")
    else
        call Duel_Start(a, me)
    endif
endfunction

function Duel_OnDecline takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local integer a = Duel_Ask[me]
    if a >= 0 then
        set Duel_Ask[me] = -1
        call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00" + GetPlayerName(Player(me)) + " declined the duel.|r")
    endif
endfunction

function Duel_OnRank takes nothing returns nothing
    local integer i = 0
    local player p = GetTriggerPlayer()
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00Duel record (wins / losses) and badges:|r")
    loop
        exitwhen i >= 12
        if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING then
            call DisplayTimedTextToPlayer(p, 0, 0, 12.0, GetPlayerName(Player(i)) + ": " + I2S(Duel_Wins[i]) + " / " + I2S(Duel_Losses[i]) + " | badges " + I2S(Badge_Count(i)) + "/8, level cap " + I2S(Badge_Cap(i)))
        endif
        set i = i + 1
    endloop
    set p = null
endfunction

function Duel_Init takes nothing returns nothing
    local trigger t1 = CreateTrigger()
    local trigger t2 = CreateTrigger()
    local trigger t3 = CreateTrigger()
    local trigger t4 = CreateTrigger()
    local integer i = 0
    loop
        exitwhen i >= 12
        set Duel_Foe[i] = -1
        set Duel_Ask[i] = -1
        call TriggerRegisterPlayerChatEvent(t1, Player(i), "-duel", false)
        call TriggerRegisterPlayerChatEvent(t2, Player(i), "-accept", true)
        call TriggerRegisterPlayerChatEvent(t3, Player(i), "-decline", true)
        call TriggerRegisterPlayerChatEvent(t4, Player(i), "-rank", true)
        call TriggerRegisterPlayerChatEvent(t4, Player(i), "-badges", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t1, function Duel_OnChat)
    call TriggerAddAction(t2, function Duel_OnAccept)
    call TriggerAddAction(t3, function Duel_OnDecline)
    call TriggerAddAction(t4, function Duel_OnRank)
    call TimerStart(Duel_Timer, 0.25, true, function Duel_Tick)
    set t1 = null
    set t2 = null
    set t3 = null
    set t4 = null
endfunction

'''
rep("function Npc_IsMan takes nothing returns boolean", duel + "function Npc_IsMan takes nothing returns boolean")
rep("    call Gym_Init()\n", "    call Gym_Init()\n    call Duel_Init()\n")
io.open(P, 'w', encoding='utf-8', newline='').write(s)

# checker: new natives / globals
P = 'tools/jasscheck.py'
s = io.open(P, encoding='utf-8', newline='').read()
add = "'SuspendHeroXP': 2, 'SetPlayerAlliance': 4, 'GetPlayerAlliance': 3, 'GetEventPlayerChatString': 0, 'StringCase': 2, "
if "'ReviveHero'" not in s:
    add += "'ReviveHero': 4, "
s = s.replace("'SetUnitMoveSpeed': 2,", "'SetUnitMoveSpeed': 2, " + add.rstrip(' '), 1)
s = s.replace("'UNIT_STATE_MAX_LIFE',", "'UNIT_STATE_MAX_LIFE', 'UNIT_STATE_MAX_MANA', 'ALLIANCE_PASSIVE',", 1)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
