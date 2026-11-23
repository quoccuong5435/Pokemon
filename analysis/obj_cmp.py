"""Read-only: object data counts of two maps (units from war3map.w3u, items / abilities from the SLK files + w3a).

python -I analysis/obj_cmp.py "../Pokemon Arena v3.2.16.w3x" "../Pokemon Arena v3.4.2.w3x"
Prints counts, and the new ids of B grouped by their first 2 characters with names.
"""
import collections
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402
import objdata  # noqa: E402


def units(m):
    o = objdata.ObjFile(m.read('war3map.w3u'))
    out = {}
    for x in o.all():
        out[x.id] = (x.get('unam') or '', x.get('upro') or '', x.orig)
    return out


def slk_ids(m, name):
    if not m.has(name):
        return {}
    t = m.read(name).decode('latin-1')
    ids = {}
    for line in t.splitlines():
        g = re.match(r'C;(?:Y\d+;)?X1;(?:Y\d+;)?K"(\w{4})"', line)
        if g:
            ids[g.group(1)] = ''
    return ids


def txt_names(m, name):
    """[ID] blocks of a *Func / *Strings txt -> Name="""
    if not m.has(name):
        return {}
    t = m.read(name).decode('utf-8', 'replace')
    out = {}
    cur = None
    for line in t.splitlines():
        g = re.match(r'\[(\w{4})\]', line)
        if g:
            cur = g.group(1)
            out.setdefault(cur, '')
            continue
        if cur and line.startswith('Name='):
            out[cur] = line[5:].strip().strip('"')
    return out


def abil_w3a(m):
    if not m.has('war3map.w3a'):
        return {}
    o = objdata.ObjFile(m.read('war3map.w3a'), leveled=True)
    return {x.id: (x.get('anam') or '') for x in o.all()}


A, B = mpq.MPQ(sys.argv[1]), mpq.MPQ(sys.argv[2])
ua, ub = units(A), units(B)
ia, ib = slk_ids(A, 'Units\\ItemData.slk'), slk_ids(B, 'Units\\ItemData.slk')
na = {**txt_names(A, 'Units\\ItemFunc.txt'), **txt_names(A, 'Units\\CampaignAbilityStrings.txt')}
nb = {**txt_names(B, 'Units\\ItemFunc.txt'), **txt_names(B, 'Units\\CampaignAbilityStrings.txt')}
aa = {**slk_ids(A, 'Units\\AbilityData.slk'), **abil_w3a(A)}
ab = {**slk_ids(B, 'Units\\AbilityData.slk'), **abil_w3a(B)}
print('units     A %5d  B %5d  new %d removed %d' % (len(ua), len(ub), len(set(ub) - set(ua)), len(set(ua) - set(ub))))
print('items     A %5d  B %5d  new %d removed %d' % (len(ia), len(ib), len(set(ib) - set(ia)), len(set(ia) - set(ib))))
print('abilities A %5d  B %5d  new %d removed %d' % (len(aa), len(ab), len(set(ab) - set(aa)), len(set(aa) - set(ab))))

for title, new, names in (('UNITS', sorted(set(ub) - set(ua)), {k: v[0] for k, v in ub.items()}),
                          ('ITEMS', sorted(set(ib) - set(ia)), nb),
                          ('ABILITIES', sorted(set(ab) - set(aa)), {**nb, **{k: v for k, v in ab.items() if v}})):
    g = collections.defaultdict(list)
    for i in new:
        g[i[:2]].append('%s=%s' % (i, names.get(i, '')))
    print('\n== new %s by prefix' % title)
    for p, xs in sorted(g.items(), key=lambda x: -len(x[1])):
        print('  %s %4d  %s' % (p, len(xs), ', '.join(xs)[:700]))
