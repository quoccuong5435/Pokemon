"""Read-only: the 74 wild creep types of v3.3.3 (name, power, model) and the playable species with no wild creep.

python -I analysis/wild_v333.py tools "../Pokemon Arena v3.3.3.w3x" v34/war3map_v333.j
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402

a = mpq.MPQ(sys.argv[2])
script = open(sys.argv[3], encoding='latin-1').read()
wts = {}
if a.has('war3map.wts'):
    t = a.read('war3map.wts').decode('utf-8', 'replace')
    for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
        wts[int(m.group(1))] = m.group(2)
units = {}
for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
    if a.has(fn):
        for o in objdata.ObjFile(a.read(fn)).all():
            d = units.setdefault(o.id, {})
            for m in o.mods:
                v = m.value
                if isinstance(v, str) and v.startswith('TRIGSTR_'):
                    v = wts.get(int(v[8:].split()[0] or 0), v)
                d.setdefault(m.field, v)

pool = dict((int(i), t) for i, t in re.findall(r"set Wild_Pool\[(\d+)\] = '(\w{4})'", script))
pw = dict((int(i), int(p)) for i, p in re.findall(r"set Wild_PoolPow\[(\d+)\] = (\d+)", script))
print('wild pool', len(pool))
by_pow = {}
wild_names = set()
for i in sorted(pool):
    u = units.get(pool[i], {})
    n = re.sub(r'^Wild ', '', str(u.get('unam') or pool[i]))
    wild_names.add(re.sub(r'[^a-z]', '', n.lower()))
    by_pow.setdefault(pw.get(i), []).append('%s(%s)' % (n, pool[i]))
for p in sorted(by_pow, key=lambda x: x or 0):
    print('power', p, len(by_pow[p]), ':', ', '.join(by_pow[p]))

heroes = {}
for uid, u in units.items():
    if uid[0].isupper() and u.get('upro'):
        sp = str(u.get('upro')).strip()
        heroes.setdefault(sp, uid)
print('\nplayable species (by proper name):', len(heroes))
miss = sorted(s for s in heroes if re.sub(r'[^a-z]', '', s.lower()) not in wild_names)
print('playable with no wild creep:', len(miss))
print(', '.join(miss))
