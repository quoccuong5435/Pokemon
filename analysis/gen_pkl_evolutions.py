"""Add PKL_EVOLUTIONS = {form id: (evolves-to form id, level)} to tools/pkl_forms.py (from tools/evolutions.json).

Level evolutions keep their level (at least 2); stone / trade / happiness evolutions get a default level:
36 for a first evolution, 55 for a later one. Only links between playable PKL forms are written."""
import io
import json
import os
import re
import sys

sys.path.insert(0, 'analysis')
sys.path.insert(0, 'tools')
import fetch_pokeapi as fp  # noqa: E402
import pkl_forms  # noqa: E402

evo = json.load(io.open('tools/evolutions.json', encoding='utf-8'))['species']
by_slug = {fp.slug(name): fid for fid, name, _lvl in pkl_forms.PKL_FORMS}
edges = {}
for name, d in evo.items():
    for frm, to, trigger, lv in d.get('chain', []):
        edges.setdefault(frm, {})[to] = (trigger, lv)

# stage of each slug inside its chain (1 = base)
parents = {}
for frm, tos in edges.items():
    for to in tos:
        parents[to] = frm


def stage(slug):
    n = 1
    while slug in parents:
        slug = parents[slug]
        n += 1
    return n


result = {}
for slug, fid in by_slug.items():
    for to, (trigger, lv) in edges.get(slug, {}).items():
        if to not in by_slug:
            continue
        if trigger == 'level-up' and isinstance(lv, int) and lv >= 2:
            level = lv
        else:
            level = 36 if stage(slug) == 1 else 55
        result[fid] = (by_slug[to], level)
        break  # one evolution per form (branching chains keep the first)

p = 'tools/pkl_forms.py'
s = io.open(p, encoding='utf-8', newline='').read()
s = re.sub(r'\nPKL_EVOLUTIONS = \{.*?\n\}\n', '\n', s, flags=re.S)
lines = ['', 'PKL_EVOLUTIONS = {']
for fid, (to, level) in sorted(result.items()):
    lines.append('    %r: (%r, %d),' % (fid, to, level))
lines.append('}')
io.open(p, 'w', encoding='utf-8', newline='').write(s.rstrip(chr(10)) + chr(10) + chr(10).join(lines) + chr(10))
print('evolution links', len(result))
