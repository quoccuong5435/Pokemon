"""Build "Pokemon Arena v3.4.3.w3x" from "Pokemon Arena v3.4.2.w3x": gym fixes (bugs present since v3.4.0).

1. Gym stops after a few Pokemon / the next gym never starts.
   Ty_InitData (v3.4 gym evolution table) and Mv_InitData (TM list) both used Ab_HT keys 299 / 300.. of the unit type.
   For a form without an evolution entry, Gym_FormAt read the TM list as evolutions and returned a move number as
   a unit type: CreateUnit failed, Gym_Cur stayed null, the gym waited forever and Gym_Busy kept the player out of
   every other gym. Mv_InitData runs after Ty_InitData, so the TM list overwrote the evolution table of every
   Pokemon with TMs (simulated: 36% of gym teams hang at base level 15, 67% at level 60). Eviolite and
   Mega_IsEvolution read the same wrong data (any Pokemon with TMs counted as "can evolve").
   -> evolution table moved to keys 699 / 700 + 2k / 701 + 2k (TM list keeps 299 / 300..339);
      readers Gym_FormAt, Mega_IsEvolution, Ext_DamageMult (Eviolite) follow.
   -> Gym_Spawn falls back to the root form if the unit cannot be created; Gym_Tick respawns the current gym
      Pokemon if it vanished (replaced by an evolution trigger), so a gym can no longer hang.
2. Gym Pokemon drop items besides the badge.
   Gym_Spawn gave each gym Pokemon the type item of its first type (Charcoal, Metal Coat...). The v1.8 pickup
   triggers drop a type item held by a Pokemon outside their list (item on the ground) and Metal Coat evolves
   Onix / Scyther (unit replaced). -> gym Pokemon no longer hold an item.

    python -I merge_v343.py "<...>/Pokemon Arena v3.4.2.w3x" "<...>/Pokemon Arena v3.4.3.w3x" [--tools <tools>]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = '3.4.2', '3.4.3'
EVO = 400  # evolution keys move from 299 / 300.. to 699 / 700..


def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit('%s: expected 1 match, found %d' % (what, n))
    return s.replace(old, new)


def func(s, name):
    m = re.search(r'^function %s takes.*?^endfunction\n' % re.escape(name), s, re.M | re.S)
    if not m:
        raise SystemExit('war3map.j: function %s not found' % name)
    return m


def patch_script(s, log):
    # ---- 1. evolution table on its own keys
    body = func(s, 'Ty_InitData').group(0)

    def mv(m):
        return "SaveInteger(Ab_HT, '%s', %d, " % (m.group(1), int(m.group(2)) + EVO)
    new, n = re.subn(r"SaveInteger\(Ab_HT, '(\w{4})', (299|3[0-3]\d), ", mv, body)
    s = s.replace(body, new)
    log.append('Ty_InitData: %d evolution entries moved to keys 699..' % n)
    for name, pairs in (('Gym_FormAt', [('LoadInteger(Ab_HT, cur, 299)', 'LoadInteger(Ab_HT, cur, 699)'),
                                        ('LoadInteger(Ab_HT, cur, 301 + 2 * k)', 'LoadInteger(Ab_HT, cur, 701 + 2 * k)'),
                                        ('LoadInteger(Ab_HT, cur, 300 + 2 * k)', 'LoadInteger(Ab_HT, cur, 700 + 2 * k)')]),
                        ('Mega_IsEvolution', [('LoadInteger(Ab_HT, from, 299)', 'LoadInteger(Ab_HT, from, 699)'),
                                              ('LoadInteger(Ab_HT, from, 300 + 2 * k)', 'LoadInteger(Ab_HT, from, 700 + 2 * k)')]),
                        ('Ext_DamageMult', [('LoadInteger(Ab_HT, GetUnitTypeId(t), 299) > 0',
                                             'LoadInteger(Ab_HT, GetUnitTypeId(t), 699) > 0')])):
        b = func(s, name).group(0)
        b2 = b
        for o, nw in pairs:
            cnt = b2.count(o)
            if cnt < 1:
                raise SystemExit('%s: %s not found' % (name, o))
            b2 = b2.replace(o, nw)
        s = s.replace(b, b2)
    s = s.replace('Ty_InitData: Ab_HT of the unit type, key 299 = number, 300 + 2k = evolved type, 301 + 2k = level',
                  'Ty_InitData: Ab_HT of the unit type, key 699 = number, 700 + 2k = evolved type, 701 + 2k = level '
                  '(v3.4.3: was 299 / 300.., the TM list of Mv_InitData)')
    s = s.replace('(gym evolution data: Ab_HT 299 / 300 + 2k on the type)',
                  '(gym evolution data: Ab_HT 699 / 700 + 2k on the type)')

    # ---- Gym_Spawn: fallback to the root form, no held item
    b = func(s, 'Gym_Spawn').group(0)
    b2 = sub1(b, '    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)\n',
              '    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)\n'
              '    if u == null and Gym_Root[g * 6 + k] != 0 then  // v3.4.3: never leave the gym without a Pokemon\n'
              '        set id = Gym_Root[g * 6 + k]\n'
              '        set Gym_Team[g * 6 + k] = id\n'
              '        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)\n'
              '    endif\n', 'Gym_Spawn CreateUnit')
    b2 = sub1(b2, '    if ti != 0 then\n        if UnitInventorySize(u) == 0 then\n            call UnitAddAbility(u, \'AInv\')\n'
                  '        endif\n        call SetItemDropOnDeath(UnitAddItemById(u, ti), false)\n    endif\n',
              '    // v3.4.3: no held type item any more (the v1.8 pickup triggers dropped it or evolved the Pokemon)\n',
              'Gym_Spawn held item')
    s = s.replace(b, b2)

    # ---- Gym_Tick: the current gym Pokemon vanished (replaced) -> spawn it again
    b = func(s, 'Gym_Tick').group(0)
    b2 = sub1(b, '            else\n                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]\n',
              '            elseif Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0 then\n'
              '                set Gym_Cur[g] = null  // v3.4.3: the gym Pokemon was removed / replaced: bring it back\n'
              '                call Gym_Spawn(g, Gym_Stage[g])\n'
              '            else\n                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]\n', 'Gym_Tick vanished')
    s = s.replace(b, b2)
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    log.append('Gym_FormAt / Mega_IsEvolution / Eviolite on keys 699..; Gym_Spawn fallback, no held item; '
               'Gym_Tick respawns a vanished gym Pokemon; v%s' % NEW)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tools', default=os.path.dirname(HERE))
    a = ap.parse_args()
    if os.path.exists(a.dst):
        raise SystemExit('%s exists, not overwriting' % a.dst)
    sys.path.insert(0, a.tools)
    import mpq
    arc = mpq.MPQ(a.src)
    log = []
    s = patch_script(arc.read('scripts\\war3map.j').decode('latin-1'), log)
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')
    arc.save_with(a.dst, {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.w3i': w3i})
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
