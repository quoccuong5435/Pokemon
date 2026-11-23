"""On-screen size of every hero model: model height (from the .mdx) x unit scale, plus move type / fly height.

Usage (from _PokemonArena2.0_work):
  python -I analysis/hero_model_size.py "../Pokemon Arena v4.2b.w3x" [names,comma,separated] [out.json]
Height comes from tools/mdx.model_height (geoset vertices, else the MODL extent, else the stand sequence).
"""
import json
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mdx  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402

BS = chr(92)


def read_model(arc, path):
    path = path.replace('/', BS)
    tries = [path]
    if path.lower().endswith('.mdl'):
        tries.append(path[:-4] + '.mdx')
    elif not path.lower().endswith('.mdx'):
        tries.append(path + '.mdx')
    for p in tries:
        try:
            return arc.read(p)
        except Exception:  # noqa: BLE001
            continue
    return None


def main():
    arc = mpq.MPQ(sys.argv[1])
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    rows = []
    for u in w3u.custom:
        name = u.get('upro') or u.get('unam')  # heroes: proper name = the Pokemon, unam = its type line
        if not name or (only and name not in only) or not u.id[:1].isupper():
            continue
        data = read_model(arc, u.get('umdl') or '')
        height = mdx.model_height(data) if data else None
        scale = u.get('usca') or 1.0
        rows.append({'id': u.id, 'name': name, 'model_h': round(height, 1) if height else None, 'scale': round(scale, 2),
                     'screen_h': round(height * scale) if height else None,
                     'move': u.get('umvt'), 'fly_h': u.get('umvh')})
    rows.sort(key=lambda r: -(r['screen_h'] or 0))
    for r in rows:
        print('%-12s %s model %6s x %.2f = %5s  move=%s fly=%s' % (r['name'], r['id'], r['model_h'], r['scale'],
                                                                  r['screen_h'], r['move'], r['fly_h']))
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'w', encoding='utf-8') as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
