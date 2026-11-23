import sys
sys.path.insert(0, '_PokemonArena2.0_work/tools')
import mpq, objdata
m = mpq.MPQ('Pokemon Arena v4.1.2-ver2m.w3x')
w3u = objdata.ObjFile(m.read('war3map.w3u'))
strings = m.read('Units\\ItemFunc.txt').decode('utf-8', errors='ignore')

def get_name(it):
    idx = strings.find(f'[{it}]')
    if idx != -1:
        for line in strings[idx:idx+200].splitlines():
            if line.startswith('Name='):
                return line[5:].strip()
    return '?'

all_items = []
for u in w3u.original + w3u.custom:
    usei = u.get('usei')
    if usei:
        for it in usei.split(','):
            it = it.strip()
            if it:
                all_items.append((u.id, u.get('unam'), it, get_name(it)))

print(f"Total items found across all shops: {len(all_items)}")
for u, sname, it, iname in all_items:
    print(f"{it} ({iname}) in {u} ({sname})")
