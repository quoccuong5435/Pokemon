import sys
sys.path.insert(0, '_PokemonArena2.0_work/tools')
import mpq
m = mpq.MPQ('Pokemon Arena v4.1.2-ver2m.w3x')
listfile = m.read('(listfile)').decode('utf-8', errors='ignore')
jass = m.read(r'scripts\war3map.j').decode('utf-8', errors='ignore')

from v412.pokemon_move_icons import parse_move_data_from_jass
mv_types, mv_labels, mv_tts = parse_move_data_from_jass(jass)

# All files in MPQ
files_lower = {}
for f in listfile.splitlines():
    base = f.replace('\\', '/').split('/')[-1].lower()
    files_lower[base] = f

matched = []
unmatched = []

for m_idx, label in sorted(mv_labels.items()):
    clean_name = label.split('(')[0].strip()
    c_lower = clean_name.lower()
    c_nospace = c_lower.replace(' ', '')
    c_under = c_lower.replace(' ', '_')
    
    candidates = [
        f"btn{c_lower} (64 x 64).blp",
        f"btn{c_under} (64 x 64).blp",
        f"btn{c_nospace} (64 x 64).blp",
        f"btn{c_lower}.blp",
        f"btn{c_under}.blp",
        f"btn{c_nospace}.blp",
    ]
    found = None
    for c in candidates:
        if c in files_lower:
            found = files_lower[c]
            break
    if found:
        matched.append((m_idx, clean_name, found))
    else:
        unmatched.append((m_idx, clean_name, mv_types.get(m_idx)))

print(f"Matched exact move icons: {len(matched)} / {len(mv_labels)}")
print("First 20 matched:")
for m in matched[:20]:
    print(" ", m)

print(f"\nUnmatched: {len(unmatched)}")
print("First 20 unmatched:")
for u in unmatched[:20]:
    print(" ", u)
