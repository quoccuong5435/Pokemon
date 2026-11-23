import sys
sys.path.insert(0, '_PokemonArena2.0_work/tools')
import mpq, objdata, json

m = mpq.MPQ('Pokemon Arena v4.1.2-ver2m.w3x')
w3u = objdata.ObjFile(m.read('war3map.w3u'))

with open('_PokemonArena2.0_work/pokeapi_abilities.json', 'r', encoding='utf-8') as f:
    pokeapi = json.load(f)

with open('_PokemonArena2.0_work/abilities_not_in_map_detailed.json', 'r', encoding='utf-8') as f:
    detailed = json.load(f)

desc_lookup = {item['name'].lower(): item['desc'] for item in detailed}

# Build mapping of unit ID -> (species, ha_name, ha_desc)
unit_ha_map = {}
for u in w3u.original + w3u.custom:
    p = u.get('upro')
    if p:
        for s in p.split(','):
            s = s.strip()
            if s in pokeapi:
                ha_list = pokeapi[s].get('hidden', [])
                if ha_list:
                    ha_name = ha_list[0]
                    ha_desc = desc_lookup.get(ha_name.lower(), f"Đặc tính ẩn {ha_name} gia tăng năng lực chiến đấu.")
                    unit_ha_map[u.id] = (s, ha_name, ha_desc)
                break

print(f"Total units mapped with Hidden Abilities: {len(unit_ha_map)}")
# Show sample
for uid in list(unit_ha_map.keys())[:10]:
    s, ha, d = unit_ha_map[uid]
    print(f"  '{uid}' => {s}: {ha} | {d[:60]}...")
