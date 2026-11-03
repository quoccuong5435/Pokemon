"""Stats of some heroes at level 1 and 100 vs wild creep HP, to calibrate a skill-damage coefficient."""
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402
import objdata  # noqa: E402
import wild_data  # noqa: E402

w3u = objdata.ObjFile(mpq.MPQ(sys.argv[1]).read('war3map.w3u'))
objs = {o.new: o for o in w3u.custom}
for hid in ('E00E', 'E010', 'E005', 'E026', 'EN0K', 'E02A'):
    o = objs[hid]
    print(hid, o.get('upro'), {k: o.get(k) for k in ('upra', 'ustr', 'ustp', 'uagi', 'uagp', 'uint', 'uinp', 'uhpm', 'ua1b', 'udic', 'ua1d', 'ua1s')})
print('wild power -> (level, hp, dmg, armor, gold); tier x(1+0.15*t) at t=10 is x2.5')
for p, (lv, hp, dmg, ar, g) in wild_data.POWER_STATS.items():
    print(p, lv, hp, int(hp * 2.5), dmg)
