"""Read-only probe for the v3.4 content work: where item strings live, which ids are free, legend data.

python -I analysis/probe_v34_ids.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.3.3.w3x'))
script = open(os.path.join(WORK, 'v34', 'war3map_v333.j'), encoding='utf-8').read()
for fn in ('Units\\ItemStrings.txt', 'Units\\ItemFunc.txt', 'Units\\CampaignAbilityStrings.txt',
           'Units\\CommonAbilityStrings.txt', 'Units\\NeutralAbilityStrings.txt'):
    t = a.read(fn).decode('utf-8', 'replace')
    hits = [k for k in ('[IM00]', '[IS00]', '[ISL0]', '[I01H]', '[AM00]', '[AB1V]') if k in t]
    print(fn, len(t), hits)
items = slk.Slk(a.read('Units\\ItemData.slk').decode('latin-1'))
item_ids = set((r.get(1) or '').strip('"') for r in items.rows)
abil = slk.Slk(a.read('Units\\AbilityData.slk').decode('latin-1'))
abil_ids = set((r.get(1) or '').strip('"') for r in abil.rows)
w3u = objdata.ObjFile(a.read('war3map.w3u'))
unit_ids = set(o.id for o in w3u.all())
print('items', len(item_ids), 'abilities', len(abil_ids), 'units', len(unit_ids))
for pre in ('IU', 'IS', 'IM', 'ISL'):
    print(pre, sorted(i for i in item_ids if i.startswith(pre))[-6:])
print('AM', sorted(i for i in abil_ids if i.startswith('AM'))[-6:])
for pre in ('nX', 'nL', 'hM', 'hZ', 'PV', 'nW'):
    print(pre, sorted(i for i in unit_ids if i.startswith(pre))[-8:])
print('legend:', re.findall(r"set Leg_(?:Type|Soul|Name)\[\d+\] = ([^\n]*)", script))
print('legend souls in Soul_Item:', [s for s in re.findall(r"set Soul_Item\[\d+\] = '(\w+)'", script) if s.startswith(('ISL', 'I01', 'I02'))])
souls = dict(re.findall(r"set Soul_Item\[(\d+)\] = '(\w+)'", script))
heroes = dict(re.findall(r"set Soul_Hero\[(\d+)\] = '(\w+)'", script))
for i in sorted(souls, key=int):
    if souls[i].startswith(('ISL', 'I0')):
        print('  soul', souls[i], '->', heroes.get(i), (w3u.find(heroes.get(i)) or objdata.Obj('', '', [])).get('upro'))
for uid in ('nL0F', 'nL10'):
    o = w3u.find(uid)
    print(uid, [(m.field, m.value) for m in o.mods][:30] if o else None)
r = items.find('ISL0')
cols = {v: k for k, v in items.name_to_x.items()}
print('ISL0 row', {cols.get(k, k): v for k, v in (r or {}).items()})
