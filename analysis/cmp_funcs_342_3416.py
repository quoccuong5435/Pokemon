import os
import re
import sys

sys.path.insert(0, r'C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\_PokemonArena2.0_work\tools')
import mpq

BASE = r'C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download'
OUT = r'C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\_PokemonArena2.0_work\out\v412'

maps = {'v342': 'Pokemon Arena v3.4.2.w3x', 'v3416': 'Pokemon Arena v3.4.16.w3x', 'v333': 'Pokemon Arena v3.3.3.w3x'}
funcs = {}
globs = {}
for tag, name in maps.items():
    p = os.path.join(BASE, name)
    if not os.path.exists(p):
        print(tag, 'MISSING', name)
        continue
    a = mpq.MPQ(p)
    s = None
    for f in ('scripts\\war3map.j', 'war3map.j'):
        try:
            s = a.read(f).decode('latin-1')
            break
        except Exception:
            pass
    if s is None:
        print(tag, 'no script')
        continue
    s = s.replace('\r', '\n')
    sq = '\n'.join(l for l in s.split('\n') if l.strip())
    open(os.path.join(OUT, tag + '_sq.j'), 'w', encoding='latin-1', newline='').write(sq)
    funcs[tag] = set(re.findall(r'^function (\w+) takes', sq, re.M))
    print(tag, len(sq.split('\n')), 'lines', len(funcs[tag]), 'functions', os.path.getsize(p) // 1024 // 1024, 'MB')

if 'v342' in funcs and 'v3416' in funcs:
    a, b = funcs['v342'], funcs['v3416']
    only_a = sorted(a - b)
    only_b = sorted(b - a)
    print('only in 3.4.2:', len(only_a))
    print('only in 3.4.16:', len(only_b))
    open(os.path.join(OUT, 'only_342.txt'), 'w').write('\n'.join(only_a))
    open(os.path.join(OUT, 'only_3416.txt'), 'w').write('\n'.join(only_b))
    for k in ('Hero_HPSync', 'Ext_AfterHit', 'Mv_Fire', 'Ab_OnDamaging', 'Gym_StartIt', 'League_Setup', 'Mv_Kind', 'Wild_NextForm', 'Fx_Rocket_Start'):
        print(' ', k, 'in342' if k in a else '-', 'in3416' if k in b else '-')
    pre = {}
    for n in only_a:
        m = re.match(r'([A-Za-z]+)_', n)
        pre.setdefault(m.group(1) if m else '?', []).append(n)
    print('3.4.2-only by prefix:', {k: len(v) for k, v in sorted(pre.items(), key=lambda x: -len(x[1]))[:15]})
    pre = {}
    for n in only_b:
        m = re.match(r'([A-Za-z]+)_', n)
        pre.setdefault(m.group(1) if m else '?', []).append(n)
    print('3.4.16-only by prefix:', {k: len(v) for k, v in sorted(pre.items(), key=lambda x: -len(x[1]))[:15]})
