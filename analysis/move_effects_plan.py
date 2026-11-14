"""Read-only: classify the learned moves of a dumped map script by their real Pokemon effect (PokeAPI short effect in
analysis/pokeapi_cache/move__*.json) for the move rework plan.

python -I analysis/dump_map.py "../Pokemon Arena v3.4.10.w3x" v3410
python -I analysis/move_effects_plan.py out/v3410/scripts_war3map.j  -> prints group counts, writes out/move_effects.tsv
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(WORK, 'analysis', 'pokeapi_cache')
script = open(sys.argv[1], encoding='latin-1').read()


def arr(name, cast=str):
    out = {}
    for m in re.finditer(r'set %s\[(\d+)\] = (.*)' % name, script):
        v = m.group(2).strip()
        out[int(m.group(1))] = cast(v)
    return out


label = arr('Mv_Label')
text = arr('Mv_Text')
order = arr('Mv_Ord')
pow_ = arr('Mv_Pow', lambda v: int(v) if v.lstrip('-').isdigit() else 0)
phys = arr('Mv_Phys', lambda v: int(v) if v.isdigit() else 0)

# effect groups, checked in this order; a move may get several tags
RULES = [
    ('recharge', r'recharge'),
    ('charge-turn', r'first turn|charges|charge up|Requires a turn to charge|turn later|underground|into the air|vanish'),
    ('recoil', r'recoil'),
    ('drain', r'Drains|drains|heal(s)? the user by half the damage'),
    ('self-drop', r'Lowers the user'),
    ('self-raise', r'Raises the user|raise the user'),
    ('target-drop', r'Lowers the target|lower the target|Lowers all targets|lower all'),
    ('burn', r'burn'),
    ('paralyze', r'paralyz'),
    ('poison', r'poison'),
    ('freeze', r'freeze'),
    ('sleep', r'sleep'),
    ('confuse', r'confus'),
    ('flinch', r'flinch'),
    ('multi-hit', r'Hits (2|two|3|three)|2-5 times|twice|multiple times'),
    ('high-crit', r'critical'),
    ('trap', r'Prevents the target from (leaving|fleeing)|Traps|trap'),
    ('heal-self', r'Heals the user|heals the user|restores'),
    ('protect', r'Prevents any moves'),
    ('pivot', r'switch|Switch'),
    ('fixed', r'Inflicts damage equal|Inflicts .* HP of damage|level'),
    ('ohko', r'one-hit|OHKO|faints'),
    ('never-miss', r'Never misses|never misses'),
]


def cache_key(name):
    n = name.lower().replace("'", '').replace('.', '')
    n = re.sub(r'[^a-z0-9]+', '-', n).strip('-')
    return n


rows = []
counts = collections.Counter()
missing = []
for i in sorted(label):
    lab = label[i].strip('"')
    name = re.sub(r'\s*\(.*$', '', lab)
    p = os.path.join(CACHE, 'move__%s.json' % cache_key(name))
    eff, prio, cls = '', 0, ''
    if os.path.exists(p):
        d = json.load(open(p, encoding='utf-8'))
        eff = (d.get('effect') or '').replace('’', "'").replace('�', "'")
        prio = d.get('priority') or 0
        cls = d.get('class') or ''
    else:
        missing.append(name)
    tags = [t for t, rx in RULES if re.search(rx, eff)]
    if prio > 0:
        tags.append('priority')
    if not tags:
        tags = ['plain']
    for t in tags:
        counts[t] += 1
    kind = re.search(r'"([a-z]+)"', order.get(i, ''))
    cur = re.sub(r'\|n.*', '', text.get(i, '').strip('"'))
    rows.append((i, name, cls, pow_.get(i, 0), kind.group(1) if kind else '', ','.join(tags), eff[:160], cur[:120]))

print('moves', len(rows), 'missing in cache', len(missing), missing[:20])
for t, c in counts.most_common():
    ex = [r[1] for r in rows if t in r[5].split(',')][:8]
    print('%-12s %3d  %s' % (t, c, ', '.join(ex)))
kinds = collections.Counter(r[4] for r in rows)
print('\nbase spell kinds:', len(kinds), kinds.most_common(30))
cur = collections.Counter(r[7] for r in rows)
print('\ndistinct current descriptions:', len(cur))
for d, c in cur.most_common(30):
    print('  %3d  %s' % (c, d))
os.makedirs(os.path.join(WORK, 'out'), exist_ok=True)
with open(os.path.join(WORK, 'out', 'move_effects.tsv'), 'w', encoding='utf-8') as f:
    f.write('idx\tname\tclass\tpower\tkind\ttags\teffect\tcurrent\n')
    for r in rows:
        f.write('\t'.join(str(x) for x in r) + '\n')
