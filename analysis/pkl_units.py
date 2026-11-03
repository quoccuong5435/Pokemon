"""List PKLegends units whose name/model mentions a keyword (read-only)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402

a = mpq.MPQ(sys.argv[2])
kws = [k.lower() for k in sys.argv[3:]]
wts = {}
if a.has('war3map.wts'):
    t = a.read('war3map.wts').decode('utf-8', 'replace')
    for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
        wts[int(m.group(1))] = m.group(2)


def res(v):
    if isinstance(v, str) and v.startswith('TRIGSTR_'):
        return wts.get(int(v[8:].split()[0] or 0), v)
    return v


objs = {}
for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
    if not a.has(fn):
        continue
    f = objdata.ObjFile(a.read(fn))
    for o in f.all():
        objs.setdefault(o.id, []).extend(o.mods)
for oid, mods in objs.items():
    d = {}
    for m in mods:
        d.setdefault(m.field, res(m.value))
    blob = ' '.join(str(d.get(k, '')) for k in ('unam', 'upro', 'umdl', 'uico')).lower()
    if any(k in blob for k in kws):
        print(oid, '|', d.get('unam'), '|', d.get('upro'), '| mdl=', d.get('umdl'), '| ico=', d.get('uico'),
              '| sca=', d.get('usca'), '| hp=', d.get('uhpm'))
