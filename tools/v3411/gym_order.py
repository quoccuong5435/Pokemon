"""v4.3.3: gyms must be cleared in order (gym N needs the badge of gym N-1) and each gym has a minimum hero level.

Before: gyms opened in pairs (1-2, then 3-4 ...), any order inside a pair, no minimum level. Now `Gym_Allowed` = the
previous gym's badge, and `Gym_MinLevel(g)` = 10 * (g + 1) (10, 20 ... 80) is checked on the challenger in `Gym_Tick`.
The level caps by badge pairs (`Badge_Cap`) are unchanged. `patch_script(s)` raises ValueError on a missing anchor.
"""


def _rep(s, old, new):
    if s.count(old) != 1:
        raise ValueError('gym_order: expected 1 match, found %d:\n%s' % (s.count(old), old[:200]))
    return s.replace(old, new)


MINLEVEL = '''// v4.3.3: minimum hero level to enter gym g (0..7)
function Gym_MinLevel takes integer g returns integer
    return 10 * (g + 1)
endfunction

'''


def patch_script(s):
    s = _rep(s, '    return g < 2 * (Gym_Milestone(pid) + 1)\n',
             '    return g == 0 or Badge_Has[pid * 8 + g - 1]  // v4.3.3: in order, the badge of the gym before\n')
    s = _rep(s, 'function Gym_Allowed takes', MINLEVEL + 'function Gym_Allowed takes')
    s = _rep(s, '" is locked: you can challenge gyms 1-" + I2S(2 * (Gym_Milestone(pid) + 1)) + " (clear 2 gyms to open 2 more).|r")\n'
                '                        endif\n',
             '" is locked: clear Gym " + I2S(g) + " first.|r")\n'
             '                        endif\n'
             '                    elseif GetHeroLevel(u) < Gym_MinLevel(g) then  // v4.3.3\n'
             '                        if Mega_Time >= Gym_Warn[pid] then\n'
             '                            set Gym_Warn[pid] = Mega_Time + 10.0\n'
             '                            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + '
             '" needs level " + I2S(Gym_MinLevel(g)) + " (yours: " + I2S(GetHeroLevel(u)) + ").|r")\n'
             '                        endif\n')
    return s
