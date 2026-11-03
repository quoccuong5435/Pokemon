"""Drop the PKL forms that duplicate one of the 21 hand-written forms (Torchic, Ralts, ...) and the typo 'Politeod',
then regenerate PKL_EVOLUTIONS (analysis/gen_pkl_evolutions.py)."""
import io
import re
import subprocess
import sys

sys.path.insert(0, 'tools')
import poke_data as pd  # noqa: E402

own = {f.name.lower() for f in pd.FORMS if f.id.startswith('EN')} | {'politeod'}
p = 'tools/pkl_forms.py'
s = io.open(p, encoding='utf-8', newline='').read()
kept, dropped = [], []
for m in re.finditer(r"    \('(P[0-9A-Z]{2}A)', '(.*?)', (\w+)\),", s):
    fid, name, lvl = m.groups()
    name = name.replace("\\'", "'")
    (dropped if name.lower() in own else kept).append((fid, name, lvl))
head = s[:s.index('PKL_FORMS = [')]
lines = ['PKL_FORMS = [']
for fid, name, lvl in kept:
    lines.append('    (%r, %r, %s),' % (fid, name, lvl))
lines.append(']')
io.open(p, 'w', encoding='utf-8', newline='').write(head + chr(10).join(lines) + chr(10) + chr(10) + 'PKL_EVOLUTIONS = {}' + chr(10))
print('kept', len(kept), 'dropped', len(dropped), [d[1] for d in dropped])
print(subprocess.run([sys.executable, '-I', 'analysis/gen_pkl_evolutions.py'], capture_output=True, text=True).stdout)
