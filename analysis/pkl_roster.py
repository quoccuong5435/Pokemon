"""List Pokemon species in PKLegends that have an imported model and are not playable in Arena (read-only)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402

pkl = mpq.MPQ(sys.argv[2])
arena = mpq.MPQ(sys.argv[3])
wts = {}
t = pkl.read('war3map.wts').decode('utf-8', 'replace')
for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
    wts[int(m.group(1))] = m.group(2)


def res(v):
    if isinstance(v, str) and v.startswith('TRIGSTR_'):
        return wts.get(int(v[8:].split()[0] or 0), v)
    return v


objs = {}
for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
    for o in objdata.ObjFile(pkl.read(fn)).all():
        objs.setdefault(o.id, []).extend(o.mods)

arena_names = set()
for o in objdata.ObjFile(arena.read('war3map.w3u')).custom:
    for f in ('upro', 'unam'):
        v = o.get(f)
        if v:
            arena_names.add(v.lower().replace(' pokemon', ''))

species = {}
for oid, mods in objs.items():
    d = {}
    for m in mods:
        d.setdefault(m.field, res(m.value))
    name = str(d.get('unam') or '')
    mm = re.match(r'^([A-Za-z.\' -]+?)\s*\((?:lvl|Lvl)\.?\s*\d+\)', name)
    if not mm:
        continue
    sp = mm.group(1).strip()
    mdl = d.get('umdl') or ''
    if not mdl.lower().startswith('war3mapimported'):
        continue
    has = pkl.has(mdl[:-4] + '.mdx')
    if not has or sp.lower().startswith('mega'):
        continue
    species.setdefault(sp, (mdl, d.get('uico')))

new = sorted(s for s in species if s.lower() not in arena_names)
print('PKL species with models:', len(species), ' not in Arena:', len(new))
print(', '.join(new))
