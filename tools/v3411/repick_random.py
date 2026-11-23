"""v4.3.1: `-repick` gives the player who typed it one random Pokemon.

Before: `-repick` removed the Pokemon and left a picker wisp, the player then chose a new one at a tavern.
Now: the same checks (first 2 minutes, 2 repicks, living Pokemon that is not in Mega form), then the wisp is
swapped for a random Pokemon of the `-random` pool at once (`Rand_Give`): not one already taken by anybody and not
the species just given up. XP and items carry over exactly as before (`Repick_Restore`).

`patch_script(s)` text-patches the script apply.py has already patched (3.4.16 + 4.3); a missing anchor raises ValueError.
"""

WRAPPER = '''// v4.3.1: -repick = the old repick (checks, remove the Pokemon, picker wisp) followed by a random Pokemon
function Repick_RandomOnChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    call Repick_Do(p)
    if Repick_Pending[pid] and Rand_FindWisp(p) != null then
        call Rand_Give(p)
    endif
    set p = null
endfunction
'''


def _rep(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise ValueError('repick_random: expected %d match(es), found %d:\n%s' % (count, n, old[:300]))
    return s.replace(old, new)


def patch_script(s):
    # the species just given up (so the random pick is a different one)
    s = _rep(s, 'boolean array Repick_Pending\n',
             'boolean array Repick_Pending\ninteger array Repick_Old  // v4.3.1: species just given up by -repick\n')
    s = _rep(s, "    call RemoveUnit(h)\n    set u = CreateUnit(p, 'earc', -128.0, 4544.0, 270.0)\n",
             "    set Repick_Old[pid] = GetUnitTypeId(h)  // v4.3.1\n"
             "    call RemoveUnit(h)\n    set u = CreateUnit(p, 'earc', -128.0, 4544.0, 270.0)\n")
    s = _rep(s, '        exitwhen tries >= 20 or not Rand_IsTaken(t)\n',
             '        exitwhen tries >= 20 or (not Rand_IsTaken(t) and t != Repick_Old[GetPlayerId(p)])  // v4.3.1\n')
    s = _rep(s, '    set h = CreateUnit(p, t, GetUnitX(w), GetUnitY(w), 270.0)\n    call Repick_Restore(h)\n',
             '    set h = CreateUnit(p, t, GetUnitX(w), GetUnitY(w), 270.0)\n'
             '    set Repick_Old[GetPlayerId(p)] = 0  // v4.3.1\n    call Repick_Restore(h)\n')
    # the chat command runs the wrapper (defined after Rand_Give, which it calls)
    s = _rep(s, 'function Host_Id takes', WRAPPER + '\nfunction Host_Id takes')
    s = _rep(s, 'call TriggerAddAction(t, function Repick_OnChat)', 'call TriggerAddAction(t, function Repick_RandomOnChat)')
    # texts
    s = _rep(s, 'Type -repick in the first 2 minutes to choose again (2 times, level and items are kept).',
             'Type -repick in the first 2 minutes to get another random Pokemon (2 times, level and items are kept).')
    s = _rep(s, 'You already have a Pokemon. Type -repick in the first 2 minutes to choose again.',
             'You already have a Pokemon. Type -repick in the first 2 minutes to get a random one instead.')
    return s
