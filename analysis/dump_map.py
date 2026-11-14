"""Read-only: dump the script, w3i strings, listfile and object text files of a built map into out/<tag>/.

python -I analysis/dump_map.py "../Pokemon Arena v3.4.10.w3x" v3410
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

path, tag = sys.argv[1], sys.argv[2]
out = os.path.join(WORK, 'out', tag)
os.makedirs(out, exist_ok=True)
m = mpq.MPQ(path)
for name in ('scripts\\war3map.j', 'war3map.j', '(listfile)', 'war3map.w3i', 'war3map.wts',
             'Units\\CampaignAbilityStrings.txt', 'Units\\ItemFunc.txt', 'Units\\ItemData.slk',
             'Units\\AbilityData.slk', 'Units\\AbilityBuffData.slk', 'war3mapSkin.txt', 'war3mapMisc.txt'):
    if m.has(name):
        data = m.read(name)
        fn = name.replace('\\', '_').replace('(', '').replace(')', '')
        open(os.path.join(out, fn), 'wb').write(data)
        print('wrote', fn, len(data))
w3i = m.read('war3map.w3i')
print('w3i strings:', [s.decode('utf-8', 'replace') for s in re.findall(rb'[\x20-\x7e\xc0-\xff]{4,}', w3i)][:12])
