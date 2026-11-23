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

unit_ha = {}
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
                    unit_ha[u.id] = (s, ha_name, ha_desc)
                break

print(f"Total mapped units: {len(unit_ha)}")

# Generate JASS blocks split into chunks so PJASS or op-limit never complains
chunks = []
current_chunk = []
for i, (uid, (s, ha, d)) in enumerate(sorted(unit_ha.items())):
    d_clean = d.replace('"', "'")
    current_chunk.append(f"    call SaveStr(AbilityPatch_HT, '{uid}', 1, \"{ha}\")")
    current_chunk.append(f"    call SaveStr(AbilityPatch_HT, '{uid}', 2, \"{d_clean}\")")
    if len(current_chunk) >= 100:
        chunks.append(current_chunk)
        current_chunk = []
if current_chunk:
    chunks.append(current_chunk)

print(f"Generated {len(chunks)} sub-functions for AbilityPatch_Init")
