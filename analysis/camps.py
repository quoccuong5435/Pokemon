"""Cluster pre-placed neutral-hostile creeps of v1.8 into camps (read-only analysis)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import objdata  # noqa: E402

j = open(sys.argv[2], encoding='latin-1').read()
units = {o.id: o for o in objdata.ObjFile(open(sys.argv[3], 'rb').read()).custom}
start = j.index("local player p=Player(PLAYER_NEUTRAL_AGGRESSIVE)")
end = j.index('endfunction', start)
creeps = []
for m in re.finditer(r"CreateUnit\(p,'(\w{4})',(-?[\d.]+),(-?[\d.]+),", j[start:end]):
    uid, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    o = units.get(uid)
    creeps.append((uid, x, y, o.get('unam') if o else uid, o.get('ulev') if o else None))
camps = []
for c in creeps:
    for camp in camps:
        if any((c[1] - d[1]) ** 2 + (c[2] - d[2]) ** 2 < 600 ** 2 for d in camp):
            camp.append(c)
            break
    else:
        camps.append([c])
print('creeps', len(creeps), 'camps', len(camps))
for camp in camps:
    names = sorted({'%s(lv%s)' % (c[3], c[4]) for c in camp})
    cx = sum(c[1] for c in camp) / len(camp)
    cy = sum(c[2] for c in camp) / len(camp)
    print('%3d units at (%6.0f,%6.0f): %s' % (len(camp), cx, cy, ', '.join(names)))
