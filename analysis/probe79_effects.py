"""Read-only: effect models the abilities / units of 79.PokemonRPG.w3x point at (its file list is hidden, but files can
be read by the names its object data uses). -> analysis/probe79_effects.txt

python -I analysis/probe79_effects.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), '79.PokemonRPG.w3x'))
paths = {}
for fn in ('war3map.w3a', 'war3mapSkin.w3a', 'war3map.w3u', 'war3mapSkin.w3u', 'war3map.w3h', 'war3mapSkin.w3h',
           'war3map.j', 'scripts\\war3map.j', 'war3map.lua', 'Units\\CampaignAbilityStrings.txt',
           'Units\\AbilityData.slk'):
    try:
        if not a.has(fn):
            continue
        data = a.read(fn)
    except Exception as e:  # noqa: BLE001
        print(fn, 'unreadable', e)
        continue
    for m in re.finditer(rb'[A-Za-z0-9_\\/ .\-\[\]()]{3,120}\.md[lx]', data):
        p = m.group(0).decode('latin-1').replace('/', '\\').replace('\\\\', '\\')
        paths.setdefault(p, set()).add(fn)
    print(fn, len(data), 'bytes')
found = []
for p in sorted(paths):
    stem = re.sub(r'\.md[lx]$', '', p, flags=re.I)
    for cand in (stem + '.mdx', 'war3mapImported\\' + stem.split('\\')[-1] + '.mdx'):
        try:
            if a.has(cand):
                found.append((cand, len(a.read(cand))))
                break
        except Exception:  # noqa: BLE001
            pass
lines = ['%d model paths referenced, %d found inside the map' % (len(paths), len(found))]
lines += ['%-70s %9d' % f for f in found]
open(os.path.join(WORK, 'analysis', 'probe79_effects.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(lines[0])
