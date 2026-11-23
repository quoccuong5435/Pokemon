import sys
sys.path.insert(0, '_PokemonArena2.0_work/tools')
import mpq, slk

m = mpq.MPQ('Pokemon Arena v4.1.2-ver2m.w3x')
items_slk = slk.Slk(m.read('Units\\ItemData.slk').decode('utf-8'))
row = items_slk.find('IL02')
print("IL02 found:", row is not None)
if row:
    for k, v in row.items():
        col_name = items_slk.cols.get(k, k)
        print(f"{col_name} (col {k}): {v}")

print("\n--- Compare with IL00 ---")
row0 = items_slk.find('IL00')
if row0:
    for k, v in row0.items():
        col_name = items_slk.cols.get(k, k)
        print(f"{col_name} (col {k}): {v}")
