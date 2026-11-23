"""Download the move / ability / Pokemon-ability data of the map from PokeAPI into tools/pokeapi/.

Inputs:  tools/learnsets.json (536 moves, 325 species with their abilities), analysis/melee_ranged.json (360 heroes).
Outputs (all JSON, UTF-8):
  tools/pokeapi/moves.json             slug -> power, accuracy, pp, type, class, priority, target, effect_chance,
                                       meta (ailment, ailment_chance, flinch_chance, stat_chance, drain, healing,
                                       crit_rate, min/max hits), stat_changes [[stat, delta]], short_effect
  tools/pokeapi/abilities.json         slug -> name, generation, short_effect, effect
  tools/pokeapi/pokemon_abilities.json species slug -> [[ability slug, is_hidden], ...]
Raw answers are cached in analysis/pokeapi_cache_meta/ (delete a file there to fetch it again).

Usage (from _PokemonArena2.0_work):  python -I tools/pokeapi/fetch.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
API = 'https://pokeapi.co/api/v2/'
CACHE = os.path.join(WORK, 'analysis', 'pokeapi_cache_meta')
LEARN = os.path.join(WORK, 'tools', 'learnsets.json')
ROSTER = os.path.join(WORK, 'analysis', 'melee_ranged.json')

# roster names that are not species keys of learnsets.json -> PokeAPI pokemon slug(s)
EXTRA = {
    'Azelf': ['azelf'], 'Cresselia': ['cresselia'], 'Diancie': ['diancie'], 'Eternatus': ['eternatus'],
    'Genesect': ['genesect'], 'Heatran': ['heatran'], 'Hoopa': ['hoopa'], 'Kyurem': ['kyurem'],
    'Latias & Latios': ['latias', 'latios'], 'Lunala': ['lunala'], 'Magearna': ['magearna'],
    'Marshadow': ['marshadow'], 'Mesprit': ['mesprit'], 'Necrozma': ['necrozma'], 'Regice': ['regice'],
    'Registeel': ['registeel'], 'Reshiram': ['reshiram'], 'Solgaleo': ['solgaleo'], 'Uxie': ['uxie'],
    'Victini': ['victini'], 'Volcanion': ['volcanion'], 'Xerneas': ['xerneas'], 'Yveltal': ['yveltal'],
    'Zacian': ['zacian'], 'Zekrom': ['zekrom'], 'Zygarde': ['zygarde-50'], 'Meganium': ['meganium'],
    'Mr. Mime': ['mr-mime'], 'Porygon2': ['porygon2'],
}


def en(entries, key):
    for e in entries or []:
        if e.get('language', {}).get('name') == 'en':
            return (e.get(key) or '').replace('\n', ' ').replace('’', "'")
    return ''


def trim(kind, d):
    if kind == 'move':
        meta = d.get('meta') or {}
        return {
            'name': en(d.get('names'), 'name') or d['name'], 'type': d['type']['name'],
            'class': d['damage_class']['name'], 'power': d['power'], 'accuracy': d['accuracy'], 'pp': d['pp'],
            'priority': d['priority'], 'target': d['target']['name'], 'effect_chance': d.get('effect_chance'),
            'meta': {
                'category': (meta.get('category') or {}).get('name'), 'ailment': (meta.get('ailment') or {}).get('name'),
                'ailment_chance': meta.get('ailment_chance'), 'flinch_chance': meta.get('flinch_chance'),
                'stat_chance': meta.get('stat_chance'), 'drain': meta.get('drain'), 'healing': meta.get('healing'),
                'crit_rate': meta.get('crit_rate'), 'min_hits': meta.get('min_hits'), 'max_hits': meta.get('max_hits'),
                'min_turns': meta.get('min_turns'), 'max_turns': meta.get('max_turns'),
            },
            'stat_changes': [[s['stat']['name'], s['change']] for s in d.get('stat_changes') or []],
            'short_effect': en(d.get('effect_entries'), 'short_effect'),
        }
    if kind == 'ability':
        return {'name': en(d.get('names'), 'name') or d['name'], 'generation': d['generation']['name'],
                'main_series': d.get('is_main_series'), 'short_effect': en(d.get('effect_entries'), 'short_effect'),
                'effect': en(d.get('effect_entries'), 'effect'),
                'flavor': en(list(reversed(d.get('flavor_text_entries') or [])), 'flavor_text')}
    if kind == 'pokemon':
        return {'name': d['name'], 'abilities': [[a['ability']['name'], a['is_hidden']]
                                                 for a in sorted(d['abilities'], key=lambda a: a['slot'])]}
    return d


def get(kind, slug):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, '%s__%s.json' % (kind, slug))
    if os.path.isfile(f):
        with open(f, encoding='utf-8') as fh:
            return json.load(fh)
    data = None
    for attempt in range(4):
        out = subprocess.run(['curl', '-s', '-m', '60', API + kind + '/' + slug + '/'], capture_output=True)
        text = out.stdout.decode('utf-8', 'replace')
        if text.strip().startswith('Not Found'):
            print('not found:', kind, slug, file=sys.stderr)
            return None
        try:
            data = json.loads(text)
            break
        except ValueError:
            time.sleep(2 * (attempt + 1))
    if data is None:
        raise RuntimeError('cannot fetch %s/%s' % (kind, slug))
    rec = trim(kind, data)
    with open(f + '.tmp', 'w', encoding='utf-8') as fh:
        json.dump(rec, fh, ensure_ascii=False)
    os.replace(f + '.tmp', f)
    return rec


def prefetch(kind, slugs, workers=6):
    """fill the cache with a few requests at a time (one by one took ~5 s per move)"""
    from concurrent.futures import ThreadPoolExecutor
    todo = [s for s in slugs if not os.path.isfile(os.path.join(CACHE, '%s__%s.json' % (kind, s)))]
    print('fetching', len(todo), kind, flush=True)
    with ThreadPoolExecutor(workers) as pool:
        for i, _ in enumerate(pool.map(lambda s: get(kind, s), todo)):
            if i % 50 == 0:
                print(kind, i, '/', len(todo), flush=True)


def main():
    with open(LEARN, encoding='utf-8') as fh:
        learn = json.load(fh)
    with open(ROSTER, encoding='utf-8') as fh:
        roster = json.load(fh)

    moves = {}
    prefetch('move', sorted(learn['moves']))
    for i, slug in enumerate(sorted(learn['moves'])):
        rec = get('move', slug)
        if rec:
            moves[slug] = rec
        if i % 100 == 0:
            print('moves', i, '/', len(learn['moves']), flush=True)

    poke_ab = {slug: sp['abilities'] for slug, sp in learn['species'].items()}
    by_name = {sp['name'].lower(): slug for slug, sp in learn['species'].items()}
    for r in roster:
        if r['name'].lower() in by_name or r['name'].lower() in poke_ab:
            continue
        for slug in EXTRA.get(r['name'], []):
            rec = get('pokemon', slug)
            if rec:
                poke_ab[slug] = rec['abilities']

    abilities = {}
    names = sorted({a for lst in poke_ab.values() for a, _h in lst})
    prefetch('ability', names)
    for i, slug in enumerate(names):
        rec = get('ability', slug)
        if rec:
            abilities[slug] = rec
        if i % 100 == 0:
            print('abilities', i, '/', len(names), flush=True)

    for name, obj in (('moves.json', moves), ('abilities.json', abilities), ('pokemon_abilities.json', poke_ab)):
        with open(os.path.join(HERE, name), 'w', encoding='utf-8') as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print('wrote', len(moves), 'moves,', len(abilities), 'abilities,', len(poke_ab), 'species')


if __name__ == '__main__':
    main()
