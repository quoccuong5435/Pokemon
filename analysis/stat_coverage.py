"""Read-only: how many Pokemon unit types have Def / SpD in the PokeAPI cache, Mega forms in the cache, and the
physical / special class of the 90 kit skills (by move name in tools/learnsets.json).

python -I analysis/stat_coverage.py
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import apply as A  # noqa: E402
import mpq  # noqa: E402

CACHE = os.path.join(WORK, 'analysis', 'pokeapi_cache')


def stats(name):
    n = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-').replace('.', ''))
    n = n.replace('alolan-', '') + ('-alola' if name.startswith('Alolan-') else '')
    for cand in (n, n.split('-')[0]):
        p = os.path.join(CACHE, 'pokemon__%s.json' % cand)
        if os.path.exists(p):
            st = json.load(open(p, encoding='utf-8')).get('stats') or []
            return [s['base_stat'] if isinstance(s, dict) else s for s in st]
    return None


units = A.unit_data(A.BASE_MAP)
names = A.hero_names(units)
species = sorted(set(names.values()))
have = [s for s in species if stats(s)]
miss = [s for s in species if not stats(s)]
print('playable species: %d, with stats: %d, missing: %s' % (len(species), len(have), miss))
megas = sorted(f[len('pokemon__'):-5] for f in os.listdir(CACHE) if f.startswith('pokemon__') and 'mega' in f)
print('mega forms in cache:', megas[:40])
data = json.load(open(os.path.join(WORK, 'tools', 'learnsets.json'), encoding='utf-8'))
moves = data['moves']
script = open(A.BASE_SCRIPT, encoding='utf-8').read()
text = mpq.MPQ(A.BASE_MAP).read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
kit = list(dict.fromkeys(re.findall(r"set Wild_KitSkill\[\d+\] = '(\w{4})'", script)))
cls = {'physical': 0, 'special': 0, 'status': 0, '?': 0}
unknown = []
for aid in kit:
    m = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % aid, text, re.S)
    nm = re.search(r'(?m)^Name=([^\r\n]*)', m.group(1)).group(1) if m else aid
    key = re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')
    info = moves.get(key) or moves.get(nm.lower())
    c = (info or {}).get('class') or (info or {}).get('damage_class') or '?'
    cls[c if c in cls else '?'] += 1
    if c == '?':
        unknown.append(nm)
print('kit skills %d by class: %s; unknown: %s' % (len(kit), cls, unknown[:20]))
print('sample move record:', next(iter(moves.items())))
