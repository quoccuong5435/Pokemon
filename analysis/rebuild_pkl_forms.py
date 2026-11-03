"""Rebuild tools/pkl_forms.py from analysis/pkl_playable_plan.json: same ids as before (index in the plan), without the
20 names that duplicate one of the 21 hand-written forms or are typos, then regenerate PKL_EVOLUTIONS."""
import io
import json
import subprocess
import sys

sys.path.insert(0, 'tools')
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
OWN = {'torchic', 'combusken', 'blaziken', 'treecko', 'grovyle', 'sceptile', 'larvitar', 'pupitar', 'tyranitar',
       'ralts', 'kirlia', 'gardevoir', 'gallade', 'bagon', 'shelgon', 'salamence', 'beldum', 'metang', 'metagross',
       'lucario', 'absol', 'politeod'}
plan = json.load(io.open('analysis/pkl_playable_plan.json', encoding='utf-8'))
dex = {r['name'].lower(): r for r in json.load(io.open('analysis/pklegends_pokedex.json', encoding='utf-8'))}
rows = []
for i, name in enumerate(plan):
    if name.lower() in OWN:
        continue
    d = dex.get(name.lower())
    rows.append(('P' + B36[i // 36] + B36[i % 36] + 'A', name, d['lvl'] if d else None))
lines = ['"""Generated: PKLegends species that are playable (not in the v1.8 arena nor among the 21 hand-written forms)."""',
         'PKL_FORMS = [']
for fid, name, lvl in rows:
    lines.append('    (%r, %r, %r),' % (fid, name, lvl))
lines += [']', '', 'PKL_EVOLUTIONS = {}', '']
io.open('tools/pkl_forms.py', 'w', encoding='utf-8', newline='').write(chr(10).join(lines))
print('forms', len(rows))
print(subprocess.run([sys.executable, '-I', 'analysis/gen_pkl_evolutions.py'], capture_output=True, text=True).stdout)
