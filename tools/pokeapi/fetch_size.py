"""Real height, types and abilities of Pokemon #1..#N from PokeAPI -> tools/pokeapi/pokemon_size.json.

Usage (from _PokemonArena2.0_work):  python -I tools/pokeapi/fetch_size.py [max_dex=1025]
Cached in analysis/pokeapi_cache_meta/size__<dex>.json. Also fetches the regional forms listed in FORMS.
Output: {slug: {"dex", "name", "height_m", "types", "abilities"}}
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
API = 'https://pokeapi.co/api/v2/pokemon/'
CACHE = os.path.join(WORK, 'analysis', 'pokeapi_cache_meta')
FORMS = ['raichu-alola', 'graveler-alola', 'golem-alola', 'geodude-alola', 'sandslash-alola', 'ninetales-alola',
         'vulpix-alola', 'marowak-alola', 'exeggutor-alola', 'meowth-alola', 'persian-alola', 'muk-alola',
         'grimer-alola', 'diglett-alola', 'dugtrio-alola', 'rattata-alola', 'raticate-alola', 'sandshrew-alola',
         'tauros-paldea-aqua-breed', 'tauros-paldea-blaze-breed', 'tauros-paldea-combat-breed']


def get(key):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, 'size__%s.json' % key)
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    data = None
    for attempt in range(4):
        out = subprocess.run(['curl', '-s', '-m', '60', API + str(key) + '/'], capture_output=True)
        text = out.stdout.decode('utf-8', 'replace')
        if text.strip().startswith('Not Found'):
            return None
        try:
            data = json.loads(text)
            break
        except ValueError:
            time.sleep(2 * (attempt + 1))
    if data is None:
        raise RuntimeError('cannot fetch %s' % key)
    rec = {'dex': data['species']['url'].rstrip('/').split('/')[-1], 'slug': data['name'],
           'height_m': data['height'] / 10.0,
           'types': [t['type']['name'] for t in sorted(data['types'], key=lambda t: t['slot'])],
           'abilities': [a['ability']['name'] for a in data['abilities']]}
    with open(path + '.tmp', 'w', encoding='utf-8') as fh:
        json.dump(rec, fh)
    os.replace(path + '.tmp', path)
    return rec


def main():
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 1025
    keys = [str(i) for i in range(1, top + 1)] + FORMS
    with ThreadPoolExecutor(6) as pool:
        recs = list(pool.map(get, keys))
    out = {r['slug']: r for r in recs if r}
    with open(os.path.join(HERE, 'pokemon_size.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print('wrote', len(out), 'Pokemon')


if __name__ == '__main__':
    main()
