"""Read-only: PKLegends v3.2 units (Mega / forms / species with a model) vs the Arena v3.3.3 map.

python -I analysis/pkl32_compare.py tools ../PKLegendsv3.2.w3x "../Pokemon Arena v3.3.3.w3x" > analysis/pkl32_compare_out.txt
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402


def load_units(path):
    a = mpq.MPQ(path)
    wts = {}
    if a.has('war3map.wts'):
        t = a.read('war3map.wts').decode('utf-8', 'replace')
        for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
            wts[int(m.group(1))] = m.group(2)

    def res(v):
        if isinstance(v, str) and v.startswith('TRIGSTR_'):
            return wts.get(int(v[8:].split()[0] or 0), v)
        return v

    objs, base = {}, {}
    for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
        if not a.has(fn):
            continue
        f = objdata.ObjFile(a.read(fn))
        for o in f.all():
            objs.setdefault(o.id, []).extend(o.mods)
            if getattr(o, 'base', None):
                base[o.id] = o.base
    out = {}
    for oid, mods in objs.items():
        d = {}
        for m in mods:
            d.setdefault(m.field, res(m.value))
        d['_base'] = base.get(oid)
        out[oid] = d
    return a, out


def clean(s):
    s = re.sub(r'\|c[0-9a-fA-F]{8}', '', str(s or ''))
    return s.replace('|r', '').strip()


pkl, pu = load_units(sys.argv[2])
arena, au = load_units(sys.argv[3])

arena_names = {}
for oid, d in au.items():
    for f in ('unam', 'upro'):
        n = clean(d.get(f)).lower()
        n = re.sub(r'\s*\((?:lvl|lv)\.?\s*\d+\)', '', n).replace(' pokemon', '').strip()
        if n:
            arena_names.setdefault(n, set()).add(oid)

rows = []
for oid, d in sorted(pu.items()):
    name = clean(d.get('unam'))
    mdl = str(d.get('umdl') or '')
    has_mdl = mdl.lower().startswith('war3mapimported') and pkl.has(re.sub(r'\.md[lx]$', '', mdl, flags=re.I) + '.mdx')
    m = re.match(r'^(.+?)\s*\((?:lvl|Lvl|LVL)\.?\s*(\d+)\)', name)
    sp, lv = (m.group(1).strip(), int(m.group(2))) if m else (name, None)
    key = sp.lower().replace(' pokemon', '').strip()
    rows.append(dict(id=oid, base=d['_base'], name=name, species=sp, lvl=lv, model=mdl, has_model=has_mdl,
                     in_arena=key in arena_names, hp=d.get('uhpm'), hero=str(oid)[0].isupper()))

json.dump(rows, open('analysis/pkl32_units.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
mega = [r for r in rows if re.search(r'mega|primal|gigantamax|gmax', r['name'], re.I)]
print('PKL v3.2 units:', len(rows), ' with imported model:', sum(r['has_model'] for r in rows))
print('\n== Mega / Primal / Gmax units (%d) ==' % len(mega))
for r in mega:
    print('%s base=%s | %s | model=%s %s | in_arena=%s' % (r['id'], r['base'], r['name'], r['model'],
                                                           'OK' if r['has_model'] else 'NO', r['in_arena']))
form = [r for r in rows if re.search(r'alola|galar|hisui|paldea|shiny|form|origin|therian|attack|defense|speed|'
                                     r'aqua|blaze|combat|crowned|black|white|dawn|dusk|ultra', r['species'], re.I)
        and not re.search(r'mega', r['name'], re.I)]
print('\n== Regional / alternate forms (%d) ==' % len(form))
for r in form:
    print('%s | %s | model %s | in_arena=%s' % (r['id'], r['name'], 'OK' if r['has_model'] else 'NO', r['in_arena']))
sp = {}
for r in rows:
    if r['lvl'] is not None and r['has_model']:
        sp.setdefault(r['species'], r)
missing = sorted(s for s, r in sp.items() if not r['in_arena'])
print('\n== Species with model and (lvl N) name not in Arena by name (%d) ==' % len(missing))
print(', '.join(missing))
