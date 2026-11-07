"""Read-only: what build_v34 would write for the items / shops (no map is written).

python -I analysis/check_items_342.py
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
import objects  # noqa: E402
import slk  # noqa: E402
import build_v34 as B  # noqa: E402
import content  # noqa: E402

base = mpq.MPQ(B.BASE_MAP)
w3u = objdata.ObjFile(base.read('war3map.w3u'))
units = {o.id: o for o in w3u.custom}
c = content.make(open(B.BASE_SCRIPT, encoding='utf-8').read(), units, base, with_files=False)
B.patch_units(w3u, c)
item_slk, item_txt = B.patch_items(base.read(objects.ITEM_SLK), base.read(objects.ITEM_TXT), c.item_rows, c.item_txt,
                                   c.item_mods, c.item_txt_mods)
s = slk.Slk(item_slk.decode('latin-1'))
cols = {v: k for k, v in s.name_to_x.items()}
t = item_txt.decode('utf-8')
for iid in ('ITFY', 'I013', 'I01X', 'IB00', 'IT05'):
    row = {cols.get(k, k): v for k, v in (s.find(iid) or {}).items()}
    sec = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % iid, t, re.S).group(1)
    print(iid, row.get('abilList'), row.get('goldcost'), '|', sec.replace('\n', ' | ')[:260])
for sid in ('n00N', 'n00Q', 'nBS0', 'nIS0'):
    print(sid, w3u.find(sid).get('unam'), w3u.find(sid).get('usei'))
