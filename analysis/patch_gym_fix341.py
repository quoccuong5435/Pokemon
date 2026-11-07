"""One-off edit for v3.4.1 gym fixes:
- gym.j: a missing current gym Pokemon is spawned again; other players near a busy gym are told who is in it;
  League gets the same watchdog
- apply.py: Mega_SafeReplace never replaces a gym Pokemon (key 33) and moves the gym / League challenger to the
  unit that replaced it (a challenger that evolves in the middle of a gym no longer counts as having lost)
- apply.py: Ext_OnKill on its own death trigger (a condition after League_OnDeath, which returns false, never ran)
"""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


edit('tools/v34/jass/gym.j', [
    ("""                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                endif
            endif
        else
            set started = false""",
     """                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                elseif Gym_Stage[g] < 6 and (Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0) then
                    // v3.4.1: the current gym Pokemon vanished (removed or replaced): bring it back
                    call Gym_Spawn(g, Gym_Stage[g])
                endif
            endif
            if Gym_Pid[g] >= 0 then  // v3.4.1: tell the other players near the gym that it is busy
                call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)
                loop
                    set u = FirstOfGroup(Wild_Tmp)
                    exitwhen u == null
                    call GroupRemoveUnit(Wild_Tmp, u)
                    set pid = GetPlayerId(GetOwningPlayer(u))
                    if pid < 12 and pid != Gym_Pid[g] and IsUnitType(u, UNIT_TYPE_HERO) and Mega_Time >= Gym_Warn[pid] then
                        set Gym_Warn[pid] = Mega_Time + 5.0
                        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Gym " + I2S(g + 1) + " is busy: " + GetPlayerName(Player(Gym_Pid[g])) + " is challenging it (Pokemon " + I2S(Gym_Stage[g] + 1) + " of 6). Wait for your turn or try another gym.|r")
                    endif
                endloop
            endif
        else
            set started = false"""),
    ("""            set dx = GetUnitX(League_Unit) - Gym_X[8]
            set dy = GetUnitY(League_Unit) - Gym_Y[8]
            if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                call League_Lose("you left the arena.")
            endif""",
     """            set dx = GetUnitX(League_Unit) - Gym_X[8]
            set dy = GetUnitY(League_Unit) - Gym_Y[8]
            if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                call League_Lose("you left the arena.")
            elseif Gym_Stage[8] < 6 and (Gym_Cur[8] == null or GetUnitTypeId(Gym_Cur[8]) == 0) then
                call Gym_Spawn(8, Gym_Stage[8])
            endif"""),
])

edit('tools/v34/apply.py', [
    ("""SAFE_NEW = ('    if not Mega_EvoItem and Itm_Has(u, Itm_Everstone) and Mega_IsEvolution(GetUnitTypeId(u), newId) then\\n'""",
     """SAFE_NEW = ('    if LoadInteger(Mega_HT, h, 33) == 1 then\\n'
            '        return  // v3.4.1: gym / League Pokemon are never replaced (the gym would lose track of them)\\n'
            '    endif\\n'
            '    if not Mega_EvoItem and Itm_Has(u, Itm_Everstone) and Mega_IsEvolution(GetUnitTypeId(u), newId) then\\n'"""),
    ("""SHINY_NEW = SHINY_OLD + ('        call SaveInteger(Ab_HT, GetHandleId(nu), 123, LoadInteger(Ab_HT, h, 123))  // v3.4 Shiny stays\\n'
                         '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)\\n')""",
     """SHINY_NEW = SHINY_OLD + ('        call SaveInteger(Ab_HT, GetHandleId(nu), 123, LoadInteger(Ab_HT, h, 123))  // v3.4 Shiny stays\\n'
                         '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)\\n'
                         '        set i = 0  // v3.4.1: a gym / League challenger that evolves keeps its battle\\n'
                         '        loop\\n'
                         '            exitwhen i > 8\\n'
                         '            if Gym_Hero[i] == u then\\n'
                         '                set Gym_Hero[i] = nu\\n'
                         '            endif\\n'
                         '            set i = i + 1\\n'
                         '        endloop\\n'
                         '        if League_Unit == u then\\n'
                         '            set League_Unit = nu\\n'
                         '        endif\\n')"""),
    ("""          '    call TriggerAddCondition(t, Condition(function League_OnDeath))\\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnKill))\\n'""",
     """          '    call TriggerAddCondition(t, Condition(function League_OnDeath))\\n'
          '    set t = CreateTrigger()\\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)\\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnKill))\\n'"""),
])
