import json, subprocess
from concurrent.futures import ThreadPoolExecutor
def get(i):
    out = subprocess.run(['curl', '-s', '-m', '30', 'https://pokeapi.co/api/v2/pokemon-species/%d/' % i],
                         capture_output=True).stdout.decode('utf-8', 'replace')
    try:
        d = json.loads(out)
    except (ValueError, TypeError):
        return i, None
    return i, {'id': i, 'name': d['name'], 'gen': d['generation']['name'],
               'legendary': d['is_legendary'], 'mythical': d['is_mythical']}
with ThreadPoolExecutor(12) as ex:
    rows = [r for _, r in ex.map(get, range(1, 1026)) if r]
legs = [r for r in rows if r['legendary'] or r['mythical']]
json.dump(legs, open('legendary_gen1_9.json', 'w', encoding='utf-8'), indent=1)
print('species fetched', len(rows), 'legendary/mythical', len(legs))
