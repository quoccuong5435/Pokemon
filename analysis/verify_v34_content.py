"""Read-only check of the v3.4 content (what build_v34 would write): models / icons exist, ids are consistent between
the JASS data (v34/war3map.j) and the object data, Mega Shops, Souls.

python -I analysis/verify_v34_content.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import mpq  # noqa: E402
import objdata  # noqa: E402
import build_v34 as B  # noqa: E402
import content  # noqa: E402

base = mpq.MPQ(B.BASE_MAP)
w3u = objdata.ObjFile(base.read('war3map.w3u'))
units = {o.id: o for o in w3u.custom}
c = content.make(open(B.BASE_SCRIPT, encoding='utf-8').read(), units, base, with_files=True)
script = open(B.SCRIPT, encoding='utf-8').read()
problems = []


def exists(path):
    if not path:
        return False
    p = path.replace('/', '\\')
    stem = re.sub(r'\.md[lx]$', '', p, flags=re.I)
    cands = [p] + ([stem + '.mdx'] if stem != p else [])
    return any(x in c.files or base.has(x) for x in cands)


for o in c.objs:
    for f in ('umdl', 'uico'):
        v = o.get(f)
        if v and not exists(v):
            problems.append('%s %s: %s not found' % (o.id, f, v))
# JASS <-> objects
new_ids = {o.id for o in c.objs}
for t in re.findall(r"set Wild_Type\[\d+\] = '(\w{4})'", script):
    if t not in new_ids and t not in units:
        problems.append('Wild_Type %s has no unit' % t)
item_new = {r[1] for r in c.item_rows}
for it in re.findall(r"set Soul_Item\[\d+\] = '(\w{4})'", script):
    if it.startswith(('IU', 'ISL9')) and it not in item_new:
        problems.append('Soul %s has no item row' % it)
for sid, pairs in c.item_txt:
    art = dict(pairs).get('Art')
    if art and not exists(art):
        problems.append('item %s icon %s missing' % (sid, art))
for sid, pairs in c.abil_txt:
    art = dict(pairs).get('Art')
    if art and not exists(art):
        problems.append('ability %s icon %s missing' % (sid, art))
for shop, items in c.shop_add.items():
    cur = (w3u.find(shop).get('usei') or '').split(',')
    print(shop, len(cur), '+', items)
for m in re.findall(r"set Mega_Skin\[(\d+)\] = '(\w{4})'", script):
    if int(m[0]) >= 25 and m[1] not in new_ids:
        problems.append('Mega skin %s missing' % m[1])
print('new units %d, items %d, abilities %d, files %d' % (len(c.objs), len(c.item_rows), len(c.abil_rows), len(c.files)))
print('warnings:', [r for r in c.report if 'WARN' in r or 'replaced' in r])
for uid in ('nX00', 'nX10', 'nX5U', 'PV0A', 'hM0P', 'nL18', 'hZ00'):
    o = c.units[uid]
    print(uid, [(m.field, m.value) for m in o.mods if m.field in ('unam', 'upro', 'umdl', 'usca', 'ulev', 'uhpm', 'ua1w',
                                                                  'ua1r', 'ua1b', 'ua1s', 'udef', 'ubba', 'uhpm', 'ustr')])
print('PROBLEMS:', len(problems))
for p in problems[:40]:
    print(' ', p)
