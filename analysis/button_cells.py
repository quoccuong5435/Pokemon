"""Which command-card cells do the hero skills of the built map use? (to place the Ability info passive)"""
import collections
import re
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402
import objdata  # noqa: E402

a = mpq.MPQ(sys.argv[1])
w3u = objdata.ObjFile(a.read('war3map.w3u'))
txt = {}
for n in a.listfile():
    if n.startswith('Units\\') and n.endswith(('Func.txt', 'Strings.txt')):
        cur = None
        for line in a.read(n).decode('utf-8', 'replace').replace('\r\n', '\n').split('\n'):
            m = re.match(r'\[(\w{4})\]', line)
            if m:
                cur = m.group(1)
                txt.setdefault(cur, {})
            elif cur and '=' in line:
                k, v = line.split('=', 1)
                txt[cur].setdefault(k, v)
cells = collections.Counter()
per_hero_free = collections.Counter()
for o in w3u.custom:
    if o.new[:1].isupper() and o.get('uhab'):
        used = set()
        for s in o.get('uhab').split(','):
            bp = txt.get(s, {}).get('Buttonpos')
            if bp:
                used.add(bp)
        for bp in used:
            cells[bp] += 1
        for x in range(4):
            for y in range(3):
                if '%d,%d' % (x, y) not in used:
                    per_hero_free['%d,%d' % (x, y)] += 1
print('cells used by hero skills:', sorted(cells.items()))
print('cells free per hero (of 137):', sorted(per_hero_free.items()))
print('Mega evolve buttons use 0,1 and 1,1; Mega Evolve txt:', [txt.get(i, {}).get('Buttonpos') for i in ('hM00', 'AM00', 'IM00')])
