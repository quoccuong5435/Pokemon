"""Check PKL models/icons for the planned wild species (read-only)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import mdx  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402

WANT = ['Hoothoot', 'Lotad', 'Diglett', 'Mareep', 'Houndour', 'Swinub', 'Sneasel', 'Misdreavus', 'Chinchou',
        'Noctowl', 'Flaaffy', 'Breloom', 'Manectric', 'Piloswine', 'Vibrava', 'Houndoom', 'Mismagius', 'Weavile',
        'Ampharos', 'Ludicolo', 'Flygon', 'Mamoswine', 'Altaria', 'Absol', 'Electivire', 'Magmortar', 'Rhyperior',
        'Snorlax', 'Lapras', 'Dusknoir']
pkl = mpq.MPQ(sys.argv[2])
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
found = {}
for oid, mods in objs.items():
    d = {}
    for m in mods:
        d.setdefault(m.field, res(m.value))
    name = str(d.get('unam') or '')
    for w in WANT:
        if name.lower().startswith(w.lower() + ' (') and w not in found:
            found[w] = (d.get('umdl'), d.get('uico'), d.get('ua1w'), d.get('ua1m'))
total = 0
for w in WANT:
    if w not in found:
        print('MISSING', w)
        continue
    mdl, ico, weap, miss = found[w]
    data = pkl.read(mdl[:-4] + '.mdx')
    info = mdx.inspect(data)
    size = len(data) + sum(len(pkl.read(tp)) for _, tp in info['textures'] if tp and pkl.has(tp))
    total += size
    print('%-11s %-40s %7d  icon=%s ico_ok=%s h=%s weap=%s' % (w, mdl, size, ico, pkl.has(ico or ''),
                                                             round(mdx.model_height(data) or 0), weap))
print('total bytes', total)
