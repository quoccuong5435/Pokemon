import json
import re

with open('_PokemonArena2.0_work/war3map_ver2m.j', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Extract all Ab_Name[i] = "..."
ab_name_map = {}
for m in re.finditer(r'set\s+Ab_Name\[(\d+)\]\s*=\s*"([^"]+)"', text):
    ab_name_map[int(m.group(1))] = m.group(2)

print(f"Total in-map abilities defined in Ab_Name: {len(ab_name_map)}")
for i in sorted(ab_name_map.keys()):
    print(f"{i:2d}: {ab_name_map[i]}")

# Read PokeAPI data
with open('_PokemonArena2.0_work/pokeapi_abilities.json', 'r', encoding='utf-8') as f:
    pokeapi_data = json.load(f)

# Find all abilities in pokeapi_data
poke_abilities_all = {}
for mon, d in pokeapi_data.items():
    for norm in d.get('normal', []):
        poke_abilities_all.setdefault(norm, {'normal': [], 'hidden': []})['normal'].append(mon)
    for hid in d.get('hidden', []):
        poke_abilities_all.setdefault(hid, {'normal': [], 'hidden': []})['hidden'].append(mon)

print(f"\nTotal unique abilities from PokeAPI: {len(poke_abilities_all)}")

in_map_names_lower = {name.lower().strip(): name for name in ab_name_map.values()}

already_in_map = []
not_in_map = []

for ab, data in poke_abilities_all.items():
    ab_clean = ab.lower().strip()
    if ab_clean in in_map_names_lower:
        already_in_map.append(ab)
    else:
        not_in_map.append(ab)

print(f"\n=== Already in map ({len(already_in_map)}) ===")
print(', '.join(sorted(already_in_map)))

print(f"\n=== NOT in map ({len(not_in_map)}) ===")
result_list = []
for ab in sorted(not_in_map):
    norm_mons = poke_abilities_all[ab]['normal']
    hid_mons = poke_abilities_all[ab]['hidden']
    result_list.append({
        'name': ab,
        'normal_count': len(norm_mons),
        'normal_examples': norm_mons[:4],
        'hidden_count': len(hid_mons),
        'hidden_examples': hid_mons[:4]
    })
    print(f"- {ab}: Normal={len(norm_mons)} ({', '.join(norm_mons[:3])}) | Hidden={len(hid_mons)} ({', '.join(hid_mons[:3])})")

with open('_PokemonArena2.0_work/abilities_not_in_map.json', 'w', encoding='utf-8') as f:
    json.dump(result_list, f, indent=2, ensure_ascii=False)
