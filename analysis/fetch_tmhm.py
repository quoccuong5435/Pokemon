import json, subprocess
from concurrent.futures import ThreadPoolExecutor
def get(i):
    out = subprocess.run(['curl', '-s', '-m', '30', 'https://pokeapi.co/api/v2/machine/%d/' % i],
                         capture_output=True).stdout.decode('utf-8', 'replace')
    try:
        d = json.loads(out)
    except (ValueError, TypeError):
        return None
    return {'id': d['id'], 'item': d['item']['name'], 'version_group': d['version_group']['name'],
            'move': d['move']['name']}
with ThreadPoolExecutor(12) as ex:
    rows = [r for r in ex.map(get, range(1, 2373)) if r]
sv = [r for r in rows if r['version_group'] == 'scarlet-violet']
json.dump(sv, open('tmhm_scarlet_violet.json', 'w', encoding='utf-8'), indent=1)
print('machines fetched', len(rows), 'scarlet-violet', len(sv))
