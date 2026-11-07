"""One-off edit for v3.4.2 gym fixes (gym stuck at a stage with no Pokemon):
- the team is built and each Pokemon spawned in its own thread (ExecuteFunc): an op-limit stop inside Gym_Tick
  (8 gyms, group scans) can no longer leave team slots empty
- an empty / invalid team slot gets a fallback Pokemon; a gym Pokemon that died without the death trigger still
  moves the gym on; one that wandered far is put back
- "-gym": the state of your gym (stage, current Pokemon, team)
"""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


g = 'tools/v34/jass/gym.j'
edit(g, [
    # fallback for an empty slot
    ("""    local integer id = Gym_Team[g * 6 + k]
""", """    local integer id = Gym_Team[g * 6 + k]
"""),
])
s = open(g, encoding='utf-8').read()
start = s.index('function Gym_Spawn takes integer g, integer k returns nothing')
body_start = s.index('    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id,', start)
fallback = """    if id == 0 or Ty_OfType(id, 0) < 0 then  // v3.4.2: an empty or broken team slot gets a Pokemon of the pool
        set id = Gym_FormAt(Gym_Pool[GetRandomInt(0, Gym_PoolN - 1)], lv)
        set Gym_Team[g * 6 + k] = id
        set ty = Ty_OfType(id, 0)
        if kt < 0 then
            set kt = ty
        endif
    endif
"""
s = s[:body_start] + fallback + s[body_start:]
open(g, 'w', encoding='utf-8').write(s)
print('fallback added')

edit(g, [
    # gym start in its own thread
    ("""                        call Gym_BuildTeam(g, u)
                        call Gym_Spawn(g, 0)""",
     """                        set Gym_ArgG = g  // v3.4.2: team + first Pokemon in their own thread (op limit)
                        call ExecuteFunc("Gym_StartIt")"""),
    # watchdog: spawn in own thread, dead-but-unprocessed, wandered off
    ("""                elseif Gym_Stage[g] < 6 and (Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0) then
                    // v3.4.1: the current gym Pokemon vanished (removed or replaced): bring it back
                    call Gym_Spawn(g, Gym_Stage[g])
                endif""",
     """                elseif Gym_Stage[g] < 6 and (Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0) then
                    // v3.4.1: the current gym Pokemon vanished (removed or replaced): bring it back
                    set Gym_ArgG = g
                    set Gym_ArgK = Gym_Stage[g]
                    call ExecuteFunc("Gym_SpawnIt")
                elseif GetWidgetLife(Gym_Cur[g]) <= 0.405 then
                    // v3.4.2: it died but the death trigger did not move the gym on
                    set Gym_ArgG = g
                    call ExecuteFunc("Gym_AdvanceIt")
                else
                    set dx = GetUnitX(Gym_Cur[g]) - Gym_X[g]
                    set dy = GetUnitY(Gym_Cur[g]) - Gym_Y[g]
                    if SquareRoot(dx * dx + dy * dy) > Gym_Leave then  // v3.4.2: it wandered off: back to the gym
                        call SetUnitPosition(Gym_Cur[g], Gym_X[g], Gym_Y[g])
                    endif
                endif"""),
    # death trigger -> shared advance
    ("""        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then
            call Gym_ClearItems(d)  // v3.3.2: gym Pokemon drop nothing but the badge
            set Gym_Dead[g * 6 + Gym_Stage[g]] = d
            set Gym_Cur[g] = null
            set Gym_Stage[g] = Gym_Stage[g] + 1
            if Gym_Stage[g] >= 6 then
                set pid = Gym_Pid[g]
                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
                set Badge_Has[pid * 8 + g] = true
                call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(pid)) + "/8, level cap " + I2S(Badge_Cap(pid)) + ".|r")
                set Gym_PCool[pid * 8 + g] = Mega_Time + Gym_ClearCool
                call Gym_Reset(g)
            else
                call Gym_Spawn(g, Gym_Stage[g])
            endif
        endif""",
     """        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then
            call Gym_Advance(g, d)
        endif"""),
    ("""function Gym_OnDeath takes nothing returns boolean""",
     """// the current gym Pokemon d of gym g is down: next one, or the badge after the 6th
function Gym_Advance takes integer g, unit d returns nothing
    local integer pid = Gym_Pid[g]
    call Gym_ClearItems(d)  // v3.3.2: gym Pokemon drop nothing but the badge
    set Gym_Dead[g * 6 + Gym_Stage[g]] = d
    set Gym_Cur[g] = null
    set Gym_Stage[g] = Gym_Stage[g] + 1
    if Gym_Stage[g] >= 6 then
        call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
        set Badge_Has[pid * 8 + g] = true
        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(pid)) + "/8, level cap " + I2S(Badge_Cap(pid)) + ".|r")
        set Gym_PCool[pid * 8 + g] = Mega_Time + Gym_ClearCool
        call Gym_Reset(g)
    else
        set Gym_ArgG = g
        set Gym_ArgK = Gym_Stage[g]
        call ExecuteFunc("Gym_SpawnIt")  // v3.4.2: own thread (op limit)
    endif
endfunction

// v3.4.2: ExecuteFunc entry points (arguments in Gym_ArgG / Gym_ArgK)
function Gym_StartIt takes nothing returns nothing
    local integer g = Gym_ArgG
    call Gym_BuildTeam(g, Gym_Hero[g])
    call Gym_Spawn(g, 0)
endfunction

function Gym_SpawnIt takes nothing returns nothing
    call Gym_Spawn(Gym_ArgG, Gym_ArgK)
endfunction

function Gym_AdvanceIt takes nothing returns nothing
    if Gym_Pid[Gym_ArgG] >= 0 and Gym_Cur[Gym_ArgG] != null then
        call Gym_Advance(Gym_ArgG, Gym_Cur[Gym_ArgG])
    endif
endfunction

// v3.4.2 "-gym": state of the gym you are in (or of all busy gyms)
function Gym_OnChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local integer g = 0
    local integer k = 0
    local string s = ""
    local boolean any = false
    loop
        exitwhen g >= 9
        if Gym_Pid[g] >= 0 then
            set any = true
            set s = "|cffffcc00Gym " + I2S(g + 1) + "|r: " + GetPlayerName(Player(Gym_Pid[g])) + ", Pokemon " + I2S(Gym_Stage[g] + 1) + " of 6"
            if Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0 then
                set s = s + ", current: none (it will be spawned again)"
            else
                set s = s + ", current: " + GetUnitName(Gym_Cur[g]) + " " + I2S(R2I(GetWidgetLife(Gym_Cur[g]))) + " HP at " + I2S(R2I(SquareRoot((GetUnitX(Gym_Cur[g]) - Gym_X[g]) * (GetUnitX(Gym_Cur[g]) - Gym_X[g]) + (GetUnitY(Gym_Cur[g]) - Gym_Y[g]) * (GetUnitY(Gym_Cur[g]) - Gym_Y[g])))) + " from the centre"
            endif
            call DisplayTimedTextToPlayer(p, 0, 0, 15.0, s)
            if Gym_Pid[g] == pid then
                set s = "  team:"
                set k = 0
                loop
                    exitwhen k >= 6
                    set s = s + " " + I2S(k + 1) + "=" + GetObjectName(Gym_Team[g * 6 + k])
                    set k = k + 1
                endloop
                call DisplayTimedTextToPlayer(p, 0, 0, 15.0, s)
            endif
        endif
        set g = g + 1
    endloop
    if not any then
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00No gym battle right now.|r")
    endif
    set p = null
endfunction

function Gym_OnDeath takes nothing returns boolean"""),
])
s = open(g, encoding='utf-8').read()
# Gym_OnDeath no longer uses pid
s = s.replace("""function Gym_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    local integer g = 0
    local integer pid = 0
""", """function Gym_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    local integer g = 0
""", 1)
open(g, 'w', encoding='utf-8').write(s)

s = open('tools/v34/jass/globals.j', encoding='utf-8').read().rstrip('\n')
s += '\ninteger Gym_ArgG = 0                    // v3.4.2: gym / slot for the ExecuteFunc entry points of gym.j\ninteger Gym_ArgK = 0\n'
open('tools/v34/jass/globals.j', 'w', encoding='utf-8').write(s)
print('globals edited')

edit('tools/v34/apply.py', [(
    """          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-league", true)\\n'
          '        set i = i + 1\\n'
          '    endloop\\n'
          '    call TriggerAddAction(t, function League_OnChat)\\n')""",
    """          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-league", true)\\n'
          '        set i = i + 1\\n'
          '    endloop\\n'
          '    call TriggerAddAction(t, function League_OnChat)\\n'
          '    set t = CreateTrigger()\\n'
          '    set i = 0\\n'
          '    loop\\n'
          '        exitwhen i >= 12\\n'
          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gym", true)\\n'
          '        set i = i + 1\\n'
          '    endloop\\n'
          '    call TriggerAddAction(t, function Gym_OnChat)\\n')""")])
