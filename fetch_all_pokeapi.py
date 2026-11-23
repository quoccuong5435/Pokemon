import os
import sys
import json
import urllib.request
import concurrent.futures

sys.path.insert(0, '_PokemonArena2.0_work/tools')
import mpq, objdata

m = mpq.MPQ('Pokemon Arena v4.1.2-ver2m.w3x')
w3u = objdata.ObjFile(m.read('war3map.w3u'))

# Map of unit ID -> species name
unit_to_species = {}
all_species = set()
for u in w3u.original + w3u.custom:
    p = u.get('upro')
    if p:
        for s in p.split(','):
            s = s.strip()
            if s and not s.isdigit() and len(s) > 2:
                all_species.add(s)
                unit_to_species[u.id] = s

species_list = sorted(all_species)
print(f"Total unique species to fetch: {len(species_list)}")

NAME_OVERRIDES = {
    'Nidoran-F': 'nidoran-f',
    'Nidoran-M': 'nidoran-m',
    'Alolan-Raichu': 'raichu-alola',
    'Alolan-Geodude': 'geodude-alola',
    'Alolan-Graveler': 'graveler-alola',
    'Alolan-Golem': 'golem-alola',
    'Alolan-Sandshrew': 'sandshrew-alola',
    'Alolan-Sandslash': 'sandslash-alola',
    'Alolan-Vulpix': 'vulpix-alola',
    'Alolan-Ninetales': 'ninetales-alola',
    'Alolan-Diglett': 'diglett-alola',
    'Alolan-Dugtrio': 'dugtrio-alola',
    'Alolan-Meowth': 'meowth-alola',
    'Alolan-Persian': 'persian-alola',
    'Alolan-Grimer': 'grimer-alola',
    'Alolan-Muk': 'muk-alola',
    'Alolan-Exeggutor': 'exeggutor-alola',
    'Alolan-Marowak': 'marowak-alola',
    'Galarian-Ponyta': 'ponyta-galar',
    'Galarian-Rapidash': 'rapidash-galar',
    'Galarian-Slowpoke': 'slowpoke-galar',
    'Galarian-Slowbro': 'slowbro-galar',
    'Galarian-Farfetchd': 'farfetchd-galar',
    'Galarian-Weezing': 'weezing-galar',
    'Galarian-Zigzagoon': 'zigzagoon-galar',
    'Galarian-Linoone': 'linoone-galar',
    'Galarian-Darumaka': 'darumaka-galar',
    'Galarian-Darmanitan': 'darmanitan-galar-standard',
    'Galarian-Corsola': 'corsola-galar',
    'Galarian-Yamask': 'yamask-galar',
    'Galarian-Stunfisk': 'stunfisk-galar',
    'Galarian-Articuno': 'articuno-galar',
    'Galarian-Zapdos': 'zapdos-galar',
    'Galarian-Moltres': 'moltres-galar',
    'Deoxys-Attack': 'deoxys-attack',
    'Deoxys-Defense': 'deoxys-defense',
    'Deoxys-Speed': 'deoxys-speed',
    'Giratina-Origin': 'giratina-origin',
    'Shaymin-Sky': 'shaymin-sky',
    'Rotom-Wash': 'rotom-wash',
    'Rotom-Heat': 'rotom-heat',
    'Rotom-Frost': 'rotom-frost',
    'Rotom-Fan': 'rotom-fan',
    'Rotom-Mow': 'rotom-mow',
    'Kyurem-Black': 'kyurem-black',
    'Kyurem-White': 'kyurem-white',
    'Meloetta-Pirouette': 'meloetta-pirouette',
    'Greninja-Ash': 'greninja-battle-bond',
    'Aegislash-Blade': 'aegislash-blade',
    'Zygarde-10': 'zygarde-10',
    'Zygarde-Complete': 'zygarde-complete',
    'Oricorio-Pom-Pom': 'oricorio-pom-pom',
    'Oricorio-Pau': 'oricorio-pau',
    'Oricorio-Sensu': 'oricorio-sensu',
    'Lycanroc-Midnight': 'lycanroc-midnight',
    'Lycanroc-Dusk': 'lycanroc-dusk',
    'Wishiwashi-School': 'wishiwashi-school',
    'Necrozma-Dusk-Mane': 'necrozma-dusk',
    'Necrozma-Dawn-Wings': 'necrozma-dawn',
    'Necrozma-Ultra': 'necrozma-ultra',
    'Urshifu-Rapid-Strike': 'urshifu-rapid-strike',
    'Calyrex-Ice-Rider': 'calyrex-ice',
    'Calyrex-Shadow-Rider': 'calyrex-shadow',
}

def to_api_name(p):
    if p in NAME_OVERRIDES:
        return NAME_OVERRIDES[p]
    clean = p.lower()
    for prefix in ['mega-', 'primal-', 'g-max-', 'gmax-']:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    clean = clean.replace(' ', '-').replace("'", '').replace('.', '')
    return clean

def fetch_one(p):
    api_name = to_api_name(p)
    url = f"https://pokeapi.co/api/v2/pokemon/{api_name}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            normal_abis = []
            hidden_abis = []
            for a in data.get('abilities', []):
                aname = a['ability']['name'].replace('-', ' ').title()
                if a['is_hidden']:
                    hidden_abis.append(aname)
                else:
                    normal_abis.append(aname)
            return p, {
                'species': p,
                'api_name': api_name,
                'normal': normal_abis,
                'hidden': hidden_abis,
                'types': [t['type']['name'].capitalize() for t in data.get('types', [])]
            }
    except Exception as e:
        return p, {
            'species': p,
            'api_name': api_name,
            'error': str(e),
            'normal': ['Adaptability'],
            'hidden': ['Protean'],
            'types': ['Normal']
        }

print("Fetching PokeAPI data in parallel (20 threads)...")
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    future_to_p = {ex.submit(fetch_one, p): p for p in species_list}
    completed = 0
    for future in concurrent.futures.as_completed(future_to_p):
        p, info = future.result()
        results[p] = info
        completed += 1
        if completed % 50 == 0 or completed == len(species_list):
            print(f"Progress: {completed} / {len(species_list)}")

out_path = r"_PokemonArena2.0_work/pokeapi_abilities.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} species data to {out_path}")
success_count = sum(1 for r in results.values() if 'error' not in r)
print(f"Success: {success_count} / {len(results)}")
