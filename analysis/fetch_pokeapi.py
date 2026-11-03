"""Download level-up learnsets, types, base stats and abilities of every Pokemon of the mod from PokeAPI.

Species lists: analysis/arena_species.txt (heroes of the map) and analysis/pkl_not_in_arena.txt (PKLegends models that
are not playable yet). Output: tools/learnsets.json (schema 2). Raw answers are cached in analysis/pokeapi_cache/.

Usage (from _PokemonArena2.0_work):  python -I analysis/fetch_pokeapi.py
"""
import json
import os
import sys
import time
import subprocess

API = 'https://pokeapi.co/api/v2/'
CACHE = os.path.join('analysis', 'pokeapi_cache')
OUT = os.path.join('tools', 'learnsets.json')
# newest first: the most recent games in which a species has level-up moves
GROUPS = ['scarlet-violet', 'sword-shield', 'ultra-sun-ultra-moon', 'sun-moon', 'omega-ruby-alpha-sapphire', 'x-y',
          'black-2-white-2', 'black-white', 'heartgold-soulsilver', 'platinum', 'diamond-pearl', 'emerald',
          'firered-leafgreen', 'ruby-sapphire', 'crystal', 'gold-silver', 'yellow', 'red-blue']
SPECIAL = {
    'aegislash': 'aegislash-shield', 'mr.mime': 'mr-mime', "farfetch'd": 'farfetchd', "sirfetch'd": 'sirfetchd', 'nidoran': 'nidoran-m',
    'deoxys': 'deoxys-normal', 'giratina': 'giratina-altered', 'darmanitan': 'darmanitan-standard',
    'leafleon': 'leafeon', 'tauros aqua': 'tauros-paldea-aqua-breed', 'tauros blaze': 'tauros-paldea-blaze-breed',
    'tauros combat': 'tauros-paldea-combat-breed', 'mr. mime': 'mr-mime', 'ho-oh': 'ho-oh',
}
SKIP = {'heimsuchung', 'maschinedramon', 'politeod'}  # not Pokemon / typo of Politoed


def slug(name):
    n = name.strip().lower()
    if n in SPECIAL:
        return SPECIAL[n]
    if n.startswith('alolan-'):
        return n[len('alolan-'):] + '-alola'
    return n.replace(' ', '-').replace('.', '').replace("'", '')


def get(path):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, path.replace('/', '__') + ('__v2' if path.startswith('pokemon/') else '') + '.json')
    if os.path.isfile(f):
        return json.load(open(f, encoding='utf-8'))
    data = None
    for attempt in range(4):
        out = subprocess.run(['curl', '-s', '-m', '60', API + path], capture_output=True).stdout.decode('utf-8', 'replace')
        if out.strip().startswith('Not Found'):
            return None
        try:
            data = json.loads(out)
            break
        except ValueError:
            time.sleep(2 * (attempt + 1))
    if data is None:
        raise RuntimeError('cannot fetch ' + path)
    trimmed = trim(path, data)
    json.dump(trimmed, open(f, 'w', encoding='utf-8'))
    return trimmed


def trim(path, d):
    if path.startswith('pokemon/'):
        groups, machines = {}, {}
        for m in d['moves']:
            for v in m['version_group_details']:
                if v['move_learn_method']['name'] == 'level-up':
                    groups.setdefault(v['version_group']['name'], []).append([v['level_learned_at'], m['move']['name']])
                elif v['move_learn_method']['name'] == 'machine':
                    machines.setdefault(v['version_group']['name'], []).append(m['move']['name'])
        return {'id': d['id'], 'name': d['name'], 'types': [t['type']['name'] for t in sorted(d['types'], key=lambda t: t['slot'])],
                'stats': [s['base_stat'] for s in d['stats']], 'abilities': [[a['ability']['name'], a['is_hidden']] for a in d['abilities']],
                'groups': groups, 'machines': machines}
    if path.startswith('move/'):
        return {'name': d['name'], 'type': d['type']['name'], 'class': d['damage_class']['name'], 'power': d['power'],
                'accuracy': d['accuracy'], 'pp': d['pp'], 'priority': d['priority'],
                'effect': (next((e['short_effect'] for e in d['effect_entries'] if e['language']['name'] == 'en'), '') or '')}
    return d


def pretty(move):
    return ' '.join(w.capitalize() for w in move.split('-'))


def main():
    arena = [l.strip() for l in open(os.path.join('analysis', 'arena_species.txt'), encoding='utf-8') if l.strip()]
    pkl = [l.strip() for l in open(os.path.join('analysis', 'pkl_not_in_arena.txt'), encoding='utf-8') if l.strip()]
    species, moves, missing = {}, {}, []
    for origin, names in (('arena', arena), ('pkl', pkl)):
        for name in names:
            s = slug(name)
            if s in SKIP:
                missing.append((name, 'skipped'))
                continue
            if s in species:  # the Arena typo 'Leafleon' and PKLegends 'Leafeon' are the same species
                continue
            p = get('pokemon/' + s)
            if p is None:
                missing.append((name, 'not found'))
                continue
            group = next((g for g in GROUPS if p['groups'].get(g)), None)
            rows = sorted(p['groups'].get(group, []), key=lambda r: (r[0], r[1]))
            mgroup = next((g for g in GROUPS if p['machines'].get(g)), None)
            tm = sorted(set(p['machines'].get(mgroup, [])))
            for _lv, mv in rows:
                if mv not in moves:
                    moves[mv] = get('move/' + mv)
            for mv in tm:
                if mv not in moves:
                    moves[mv] = get('move/' + mv)
            species[s] = {'name': name, 'origin': origin, 'dex': p['id'], 'types': p['types'], 'stats': p['stats'],
                          'abilities': p['abilities'], 'group': group, 'moves': [[lv, mv] for lv, mv in rows],
                          'tm_group': mgroup, 'tm': tm}
            print('%-22s %-9s %-24s %3d moves' % (name, origin, group, len(rows)), flush=True)
    table = {}
    for mv, m in moves.items():
        if m is None:
            continue
        table[mv] = {'name': pretty(mv), 'type': m['type'], 'class': m['class'], 'power': m['power'] or 0,
                     'accuracy': m['accuracy'] or 0, 'pp': m['pp'] or 0, 'priority': m['priority'], 'effect': m['effect']}
    out = {'schema': 2, 'source': 'PokeAPI (https://pokeapi.co): level-up moves of the newest game group that has the species',
           'stat_order': ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'],
           'species': species, 'moves': table, 'missing': missing}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('species', len(species), 'moves', len(table), 'missing', missing)


if __name__ == '__main__':
    main()
