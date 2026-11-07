"""Read-only: effect models of PKLegends v3.2 (imported .mdx not used as a unit model) and the art its abilities use,
to pick move effects from. -> analysis/pkl_effects.txt

python -I analysis/pkl_effects.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import content  # noqa: E402

pkl = content.Pkl(content.PKL_MAP)
names = pkl.mpq.listfile()
unit_models = {re.sub(r'\.md[lx]$', '', str(d.get('umdl') or ''), flags=re.I).lower() for d in pkl.units.values()}
mdx = [n for n in names if n.lower().endswith('.mdx') and not n.lower().endswith('_portrait.mdx')]
effects = [n for n in mdx if re.sub(r'\.mdx$', '', n, flags=re.I).lower() not in unit_models]
# art referenced by abilities (txt files)
used = {}
for fn in names:
    if fn.lower().startswith('units\\') and fn.lower().endswith('.txt'):
        t = pkl.mpq.read(fn).decode('utf-8', 'replace')
        for sec, body in re.findall(r'\[(\w{4})\]\r?\n(.*?)(?=\r?\n\[|\Z)', t, re.S):
            nm = re.search(r'(?m)^Name=([^\r\n]*)', body)
            for key in ('Missileart', 'Effectart', 'Targetart', 'Casterart', 'Specialart', 'Areaeffectart'):
                for v in re.findall(r'(?m)^%s=([^\r\n]*)' % key, body):
                    for p in v.split(','):
                        p = p.strip().strip('"')
                        if p.lower().startswith('war3mapimported'):
                            used.setdefault(p, set()).add((nm.group(1) if nm else sec))
lines = ['PKLegends v3.2: %d imported models, %d not unit models (effects)' % (len(mdx), len(effects)), '']
for e in sorted(effects, key=str.lower):
    key = re.sub(r'\.mdx$', '.mdl', e, flags=re.I)
    users = used.get(key) or used.get(e) or set()
    lines.append('%-60s %8d  %s' % (e, len(pkl.mpq.read(e)), ', '.join(sorted(users))[:120]))
open(os.path.join(WORK, 'analysis', 'pkl_effects.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines[:3]))
