"""Read-only: for every Mega of a map, base unit / skin unit / models / Abilities, to find Megas that look unchanged.

python -I analysis/mega_check.py tools "../Pokemon Arena v3.3.3.w3x" v34/war3map_v333.j
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402

a = mpq.MPQ(sys.argv[2])
script = open(sys.argv[3], encoding='utf-8', errors='replace').read()
units = {o.id: o for o in objdata.ObjFile(a.read('war3map.w3u')).all()}
names = set(ln.strip().lower() for ln in a.read('(listfile)').decode('latin-1').splitlines())


def arr(name, kind=r"'(\w{4})'"):
    return dict((int(i), v) for i, v in re.findall(r'set %s\[(\d+)\] = %s' % (name, kind), script))


base, skin = arr('Mega_Base'), arr('Mega_Skin')
mname = arr('Mega_Name', r'"([^"]*)"')
mega_ab = dict((int(i), int(n)) for i, n in re.findall(r'set Ab_MegaAb\[(\d+)\] = (\d+)', script))
ab_of = dict((u, int(n)) for u, n in re.findall(r"call SaveInteger\(Ab_HT, '(\w{4})', 0, (\d+)\)", script))
ab_name = dict((int(i), v) for i, v in re.findall(r'set Ab_Name\[(\d+)\] = "([^"]*)"', script))
evo = re.findall(r"set Evo_From\[\d+\] = '(\w{4})'\n    set Evo_To\[\d+\] = '(\w{4})'", script)


def f(uid, field):
    o = units.get(uid)
    return o.get(field) if o else None


def has_model(path):
    if not path:
        return False
    stem = re.sub(r'\.md[lx]$', '', path, flags=re.I).lower()
    return stem + '.mdx' in names or stem + '.mdl' in names


# every hero type per proper name (a Mega needs the exact base type)
by_pro = {}
for uid, o in units.items():
    if uid[0].isupper() and (o.get('unam') or '').endswith(' Pokemon'):
        by_pro.setdefault((o.get('upro') or '').split(',')[0].strip(), []).append(uid)

print('Mega_N', len(base))
for i in sorted(base):
    b, s = base[i], skin.get(i)
    bm, sm = f(b, 'umdl'), f(s, 'umdl')
    pro = (f(b, 'upro') or '').split(',')[0].strip()
    same = (bm or '').lower() == (sm or '').lower()
    others = [u for u in by_pro.get(pro, []) if u != b]
    print('%2d %-18s base=%s(%s) mdl=%s | skin=%s mdl=%s %s%s | Ab base=%s mega=%s%s | other types of %s: %s'
          % (i, mname.get(i), b, pro, bm, s, sm, 'IN-MAP' if has_model(sm) else 'BUILTIN/MISSING',
             ' SAME-MODEL' if same else '', ab_name.get(ab_of.get(b)), ab_name.get(mega_ab.get(i)),
             ' SAME-AB' if ab_of.get(b) == mega_ab.get(i) else '', pro, others))
print()
print('evolutions INTO a Mega base type (the evolved unit must be that exact type):')
for i in sorted(base):
    srcs = [fr for fr, to in evo if to == base[i]]
    print('  %s <- %s' % (mname.get(i), srcs))
