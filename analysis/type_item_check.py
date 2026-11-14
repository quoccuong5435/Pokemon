"""Read-only: for every type item of a map (Type_Item list + Soft Sand + the gym-only items), list its abilities with
base code, main data and buff, whether the script uses that buff (trigger-based effects), and the item text.

python -I analysis/type_item_check.py "../Pokemon Arena v3.4.10.w3x" out/v3410
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402
import objdata  # noqa: E402

map_path, dump = sys.argv[1], sys.argv[2]


def slk(path):
    t = open(path, encoding='latin-1').read()
    rows, cur = {}, None
    for line in t.splitlines():
        if not line.startswith('C;'):
            continue
        parts = {}
        for p in line.split(';')[1:]:
            if p:
                parts[p[0]] = p[1:]
        if 'Y' in parts:
            cur = int(parts['Y'])
        rows.setdefault(cur, {})[int(parts['X'])] = parts.get('K', '').strip('"')
    hdr = rows[1]
    col = {v: k for k, v in hdr.items()}
    return {r.get(1): {h: r.get(c, '') for h, c in col.items()} for y, r in rows.items() if y > 1}


items = slk(os.path.join(dump, 'Units_ItemData.slk'))
abil = slk(os.path.join(dump, 'Units_AbilityData.slk'))
func = open(os.path.join(dump, 'Units_ItemFunc.txt'), encoding='utf-8', errors='replace').read()
script = open(os.path.join(dump, 'scripts_war3map.j'), encoding='latin-1').read()
m = mpq.MPQ(map_path)
w3a = objdata.ObjFile(m.read('war3map.w3a'), leveled=True)
w3a_by = {}
for o in w3a.original + w3a.custom:
    w3a_by[o.new or o.orig] = o


def item_text(iid):
    mm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % iid, func, re.S)
    if not mm:
        return '?', ''
    n = re.search(r'(?m)^Name=(.*)$', mm.group(1))
    t = re.search(r'(?m)^Ubertip=(.*)$', mm.group(1))
    return (n.group(1).strip() if n else '?'), (t.group(1).strip().strip('"')[:140] if t else '')


ids = [i for _, i in re.findall(r"set Type_Item\[(\d+)\] = '(\w{4})'", script)]
for extra in ('I013', 'ITGD', 'ITFY'):
    if extra not in ids:
        ids.append(extra)
for iid in ids:
    name, tip = item_text(iid)
    al = [a for a in (items.get(iid, {}).get('abilList') or '').split(',') if a]
    print('\n%s %s | %s' % (iid, name, re.sub(r'\|n.*', '', tip)))
    for a in al:
        r = abil.get(a, {})
        o = w3a_by.get(a)
        code = r.get('code') or (o.orig if o else '?')
        data = {k: r.get(k) for k in ('DataA1', 'DataB1', 'DataC1', 'DataD1', 'DataE1', 'Area1', 'Dur1', 'Cool1')
                if r.get(k) not in (None, '', '-', '_', '0')}
        if o:
            data.update({md.field: md.value for md in o.mods if md.field not in ('aart', 'anam', 'atp1', 'aub1', 'ansf')})
        buff = r.get('BuffID1') or ''
        uses = len(re.findall("'%s'" % buff, script)) if buff else 0
        print('   %s code=%s buff=%s script-uses-buff=%d data=%s' % (a, code, buff, uses, data))
