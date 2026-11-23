"""v4.3: the gym features of 3.4.2 on the 3.4.16 script.

`patch_script(s)` text-patches the script that `apply.py` has already patched (3.4.16). JASS lives in
jass/gym342.j, one section per `// ==== BEFORE <function>` marker. A missing anchor raises ValueError.
Design: docs/superpowers/specs/2026-11-21-merge-3.4.2-into-3.4.16-design.md
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
JASS_FILE = os.path.join(HERE, 'jass', 'gym342.j')


def _rep(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise ValueError('gym342: expected %d match(es), found %d:\n%s' % (count, n, old[:300]))
    return s.replace(old, new)


# v3.4.1: tell the other heroes near a busy gym that it is busy (once per 5 s per player)
BUSY = '''            if Gym_Pid[g] >= 0 then  // v4.3 (3.4.1): tell the other players near the gym that it is busy
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
'''


def sections():
    """jass/gym342.j split by its `// ==== BEFORE <function>` markers: {function name: JASS text}."""
    text = open(JASS_FILE, encoding='utf-8').read()
    parts = re.split(r'(?m)^// ==== BEFORE (\w+)\n', text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def _insert_before(s, fname, code):
    return _rep(s, 'function %s takes' % fname, code.rstrip('\n') + '\n\nfunction %s takes' % fname)


def patch_script(s):
    sec = sections()
    # ---- gym difficulty: the Gym_Spawn lines and the skill-cast chance of Ai_Unit
    s = _rep(s, 'call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult))',
             'call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult * Gym_DiffHP(g)))  // v4.3 (3.4.2)')
    s = _rep(s, 'call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8), 0)',
             'call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8 * Gym_DiffDmg(g)), 0)')
    s = _rep(s, 'call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m)',
             'call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m * Gym_DiffDmg(g))')
    s = _rep(s, '    call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Gym_ASBoost, 0)\n',
             '    if Gym_Fast(g) then  // v4.3 (3.4.2): gyms 1-4 do not get the faster attack\n'
             '        call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Gym_ASBoost, 0)\n'
             '    endif\n')
    s = _rep(s, '    call SaveInteger(Ab_HT, h, 0, LoadInteger(Ab_HT, id, 0))  // the Ability of its species\n',
             '    call SaveInteger(Ab_HT, h, 0, LoadInteger(Ab_HT, id, 0))  // the Ability of its species\n'
             '    call SaveReal(Ab_HT, h, 88, Gym_DiffAI(g))  // v4.3 (3.4.2): skill-cast chance of Ai_Tick\n')
    s = _rep(s, 'GetRandomReal(0.0, 1.0) < Ai_CastChance then\n            set pick0 = GetRandomInt(0, 4)',
             'GetRandomReal(0.0, 1.0) < Ai_Chance(h) then  // v4.3 (3.4.2)\n            set pick0 = GetRandomInt(0, 4)')
    s = _insert_before(s, 'Gym_Spawn', sec['Gym_Spawn'])
    s = _insert_before(s, 'Ai_Unit', sec['Ai_Unit'])
    # ---- "gym N is busy" message to the other heroes near a busy gym (3.4.1)
    s = _rep(s, '            endif\n        else\n            set started = false\n',
             '            endif\n' + BUSY + '        else\n            set started = false\n')
    # ---- the -gym command
    s = _rep(s, '    call TriggerAddAction(t, function League_OnChat)\n',
             '    call TriggerAddAction(t, function League_OnChat)\n'
             '    set t = CreateTrigger()  // v4.3 (3.4.2): -gym\n'
             '    set i = 0\n    loop\n        exitwhen i >= 12\n'
             '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gym", true)\n'
             '        set i = i + 1\n    endloop\n'
             '    call TriggerAddAction(t, function Gym_OnChat)\n')  # what follows (set t = null / set t = CreateTrigger) stays
    # ---- stuck gyms (3.4.1 / 3.4.2): own threads, "dead but not moved on", "wandered off"
    s = _rep(s, '\nendglobals', '\n    integer Gym_ArgG = 0  // v4.3 (3.4.2): gym / slot for the ExecuteFunc entry points\n'
                              '    integer Gym_ArgK = 0\nendglobals')
    s = _rep(s, GYM_TICK_OLD, GYM_TICK_NEW)
    s = _rep(s, '                        call Gym_BuildTeam(g, u)\n                        call Gym_Spawn(g, 0)\n',
             '                        set Gym_ArgG = g  // v4.3 (3.4.2): team + first Pokemon in their own thread (op limit)\n'
             '                        call ExecuteFunc("Gym_StartIt")\n')
    s, advance = _split_death(s)
    s = _insert_before(s, 'Gym_OnDeath', advance + '\n' + sec['Gym_OnDeath'])
    return s


def _split_death(s):
    """Gym_OnDeath's inline "move the gym on" block becomes Gym_Advance(g, d); returns (script, Gym_Advance text)."""
    m = re.search(r'(?ms)^function Gym_OnDeath takes.*?^endfunction\n', s)
    if not m:
        raise ValueError('gym342: function Gym_OnDeath not found')
    fn = m.group(0)
    b = re.search(r'(?s)(        if Gym_Pid\[g\] >= 0 and Gym_Cur\[g\] != null and d == Gym_Cur\[g\] then\n)(.*?)'
                  r'(        endif\n        set g = g \+ 1\n)', fn)
    if not b:
        raise ValueError('gym342: the death block of Gym_OnDeath not found')
    block = b.group(2)
    spawn = '                call Gym_Spawn(g, Gym_Stage[g])\n'
    if block.count(spawn) != 1:
        raise ValueError('gym342: the next-Pokemon call of Gym_OnDeath not found')
    block = block.replace(spawn, '                set Gym_ArgG = g  // v4.3 (3.4.2): the next Pokemon in its own thread (op limit)\n'
                                 '                set Gym_ArgK = Gym_Stage[g]\n'
                                 '                call ExecuteFunc("Gym_SpawnIt")\n')
    body = ''.join(l[8:] if l.startswith(' ' * 8) else l for l in block.splitlines(True))
    advance = ('// v4.3 (3.4.2): what Gym_OnDeath did, as a function: Gym_Tick can also move a gym on (Gym_AdvanceIt)\n'
               'function Gym_Advance takes integer g, unit d returns nothing\n'
               '    local integer pid = 0\n' + body + 'endfunction\n')
    death = fn[:b.start()] + b.group(1) + '            call Gym_Advance(g, d)\n' + b.group(3) + fn[b.end():]
    return s[:m.start()] + death + s[m.end():], advance


GYM_TICK_OLD = '''            elseif Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0 then
                set Gym_Cur[g] = null  // v3.4.3: the gym Pokemon was removed / replaced: bring it back
                call Gym_Spawn(g, Gym_Stage[g])
            else
                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]
                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]
                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                endif
'''

GYM_TICK_NEW = '''            elseif Gym_Stage[g] < 6 and (Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0) then
                set Gym_Cur[g] = null  // v3.4.3: the gym Pokemon was removed / replaced: bring it back (v4.3: own thread)
                set Gym_ArgG = g
                set Gym_ArgK = Gym_Stage[g]
                call ExecuteFunc("Gym_SpawnIt")
            elseif GetWidgetLife(Gym_Cur[g]) <= 0.405 then
                // v4.3 (3.4.2): it died but the death trigger did not move the gym on
                set Gym_ArgG = g
                call ExecuteFunc("Gym_AdvanceIt")
            else
                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]
                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]
                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                else
                    set dx = GetUnitX(Gym_Cur[g]) - Gym_X[g]
                    set dy = GetUnitY(Gym_Cur[g]) - Gym_Y[g]
                    if SquareRoot(dx * dx + dy * dy) > Gym_Leave then  // v4.3 (3.4.2): it wandered off: back to the gym
                        call SetUnitPosition(Gym_Cur[g], Gym_X[g], Gym_Y[g])
                    endif
                endif
'''
