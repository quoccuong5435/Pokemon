import re

with open('_PokemonArena2.0_work/war3map_ver2m.j', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for Hero proper names or unit names
for line in text.splitlines():
    if 'Bulbasaur' in line or 'Charmander' in line or 'Pikachu' in line or 'Greninja' in line:
        print(line[:120])
