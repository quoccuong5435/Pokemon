import re

with open('_PokemonArena2.0_work/war3map_ver2m.j', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for Wild_Type lines
wild_lines = []
for line in text.splitlines():
    if 'Wild_Type[' in line and '=' in line:
        wild_lines.append(line.strip())

print(f"Total Wild_Type assignments: {len(wild_lines)}")
for l in wild_lines[:20]:
    print(l)
