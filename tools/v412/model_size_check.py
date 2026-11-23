"""Check the on-screen size and the walk / fly setup of every hero of a built map (GEMINI.md section 13).

Usage (from _PokemonArena2.0_work):
  python -I tools/v412/model_size_check.py "../Pokemon Arena v4.2b.w3x" [--md docs/hero-model-size.md] [--strict]
--strict: exit code 1 when any hero is flagged (for build scripts / tests).

How the size is judged:
- model size = max(height, 0.4 x length) of the model's geoset vertices (bind pose), from the .mdx in the map;
  on screen = model size x unit scale (usca). Calibrated on the user's choices: Onix / Steelix 0.90, Donphan 0.95.
- target = 80 x (real height / 0.4 m) ^ 0.45, kept between 55 and 230 (Pikachu 0.4 m -> 80, Charizard 1.7 m -> ~153,
  anything above ~7 m -> 230). Real heights: tools/pokeapi/pokemon_size.json (PokeAPI).
- "too big" above 1.35 x target, "too small" below 0.7 x target; suggested scale = scale x target / on screen.
Walk / fly: not Flying-type and no Levitate -> must walk (umvt foot, umvh 0); Flying / Levitate -> fly height <= 100.
"""
import argparse
import json
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mdx  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402

BS = chr(92)
SPECIAL = {'mr. mime': 'mr-mime', 'mime jr.': 'mime-jr', "farfetch'd": 'farfetchd', 'nidoran': 'nidoran-m',
           'nidoran f': 'nidoran-f', 'nidoran m': 'nidoran-m', 'deoxys': 'deoxys-normal', 'giratina': 'giratina-altered',
           'wormadam': 'wormadam-plant', 'shaymin': 'shaymin-land', 'latias & latios': 'latias', 'ho-oh': 'ho-oh',
           'porygon-z': 'porygon-z', 'porygon2': 'porygon2', 'zygarde': 'zygarde-50', 'darmanitan': 'darmanitan-standard',
           'aegislash': 'aegislash-shield', 'kyurem': 'kyurem', 'castform': 'castform', 'basculin': 'basculin-red-striped',
           'mr.mime': 'mr-mime', 'leafleon': 'leafeon', 'tauros aqua': 'tauros-paldea-aqua-breed',
           'tauros blaze': 'tauros-paldea-blaze-breed', 'tauros combat': 'tauros-paldea-combat-breed'}
# scales the user fixed (GEMINI.md section 13): name -> (low, high)
USER_SCALE = {'Croconaw': (1.20, 1.25), 'Feraligatr': (1.15, 1.20), 'Steelix': (0.90, 0.90), 'Miltank': (0.90, 1.00),
              'Donphan': (0.95, 0.95)}


def slug(name):
    n = name.strip().lower()
    if n in SPECIAL:
        return SPECIAL[n]
    m = re.match(r'(alolan|alola)[- ](.+)', n)
    if m:
        return m.group(2).replace(' ', '-') + '-alola'
    return re.sub(r'[^a-z0-9]+', '-', n.replace("'", '').replace('.', '')).strip('-')


def extents(data):
    """(height, length) of all geoset vertices; falls back to tools/mdx.model_height for the height"""
    if not data or data[:4] != b'MDLX':
        return None, None
    lo = [None, None, None]
    hi = [None, None, None]
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4]
        size = struct.unpack_from('<I', data, p + 4)[0]
        if tag == b'GEOS':
            q, end = p + 8, p + 8 + size
            while q < end:
                gsize = struct.unpack_from('<I', data, q)[0]
                if data[q + 4:q + 8] == b'VRTX':
                    n = struct.unpack_from('<I', data, q + 8)[0]
                    vals = struct.unpack_from('<%df' % (n * 3), data, q + 12)
                    for axis in range(3):
                        seq = vals[axis::3]
                        if seq:
                            lo[axis] = min(seq) if lo[axis] is None else min(lo[axis], min(seq))
                            hi[axis] = max(seq) if hi[axis] is None else max(hi[axis], max(seq))
                q += max(gsize, 4)
        p += 8 + size
    if lo[2] is None:
        return mdx.model_height(data), None
    return hi[2] - lo[2], max(hi[0] - lo[0], hi[1] - lo[1])


def read_model(arc, path):
    path = (path or '').replace('/', BS)
    tries = [path]
    if path.lower().endswith('.mdl'):
        tries.insert(0, path[:-4] + '.mdx')
    elif not path.lower().endswith('.mdx'):
        tries.append(path + '.mdx')
    for p in tries:
        try:
            return arc.read(p)
        except Exception:  # noqa: BLE001
            continue
    return None


def target_size(height_m):
    return max(55.0, min(230.0, 80.0 * (max(0.1, height_m) / 0.4) ** 0.45))


def check(map_path):
    with open(os.path.join(WORK, 'tools', 'pokeapi', 'pokemon_size.json'), encoding='utf-8') as fh:
        species = json.load(fh)
    arc = mpq.MPQ(map_path)
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    rows = []
    for u in w3u.custom:
        name = u.get('upro')
        if not name or not u.id[:1].isupper():
            continue
        name = re.sub(r'^#\d+\s+', '', name.split(',')[0].strip())  # 4.3: Gen 1-4 heroes are named "#172 Pichu"
        sp = species.get(slug(name))
        height, length = extents(read_model(arc, u.get('umdl')))
        scale = u.get('usca') or 1.0
        move = u.get('umvt') or '(default)'
        fly_h = u.get('umvh') or 0.0
        flags = []
        size = screen = target = None
        suggest = None
        if height:
            size = max(height, 0.4 * (length or 0.0))
            screen = size * scale
            if height < 15 or height > 800:
                flags.append('model lạ (cao %d)' % height)
        if sp:
            target = target_size(sp['height_m'])
            if name in USER_SCALE:
                low, high = USER_SCALE[name]
                if not low - 0.001 <= scale <= high + 0.001:
                    flags.append('khác số đã chốt (%.2f-%.2f)' % (low, high))
                    suggest = round((low + high) / 2.0, 2)
            elif screen:
                if screen > 1.35 * target:
                    flags.append('quá to')
                elif screen < 0.7 * target:
                    flags.append('quá nhỏ')
                if flags and flags[-1] in ('quá to', 'quá nhỏ'):  # noqa: E501
                    suggest = round(max(0.3, min(2.0, scale * target / screen)) * 20) / 20.0
            flies = 'flying' in sp['types'] or 'levitate' in sp['abilities']
            if not flies and (move in ('hover', 'fly') or fly_h > 0):
                flags.append('lơ lửng sai (%s, cao %d)' % (move, fly_h))
            if flies and fly_h > 100:
                flags.append('bay quá cao (%d)' % fly_h)
        else:
            flags.append('không có dữ liệu loài')
        if not height:
            flags.append('không đọc được model')
        rows.append({'id': u.id, 'name': name, 'real_m': sp['height_m'] if sp else None,
                     'model_h': round(height) if height else None, 'model_len': round(length) if length else None,
                     'scale': round(scale, 2), 'screen': round(screen) if screen else None,
                     'target': round(target) if target else None, 'suggest': suggest, 'move': move,
                     'fly_h': fly_h, 'flags': flags})
    rows.sort(key=lambda r: (not r['flags'], r['name']))
    return rows


def to_markdown(rows, map_name):
    bad = [r for r in rows if r['flags']]
    out = ['# Kích thước và đi bộ / bay của hero: %s' % map_name, '',
           '%d hero, %d bị đánh dấu. Tạo bằng `tools/v412/model_size_check.py` (GEMINI.md mục 13).' % (len(rows), len(bad)), '',
           'Cao trên màn hình = kích thước model x scale. Mục tiêu tính từ chiều cao thật của loài (PokeAPI). '
           'Scale đề xuất đưa con đó về đúng mục tiêu; vẫn phải xem trong game.', '',
           '| Hero | Id | Cao thật (m) | Model cao / dài | Scale | Trên màn hình | Mục tiêu | Scale đề xuất | Di chuyển | Vấn đề |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        out.append('| %s | %s | %s | %s / %s | %.2f | %s | %s | %s | %s %s | %s |' % (
            r['name'], r['id'], r['real_m'] if r['real_m'] is not None else '-', r['model_h'] or '-', r['model_len'] or '-',
            r['scale'], r['screen'] or '-', r['target'] or '-', ('%.2f' % r['suggest']) if r['suggest'] else '',
            r['move'], ('%d' % r['fly_h']) if r['fly_h'] else '', '; '.join(r['flags']) or 'ổn'))
    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--md')
    ap.add_argument('--json')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    rows = check(a.map)
    bad = [r for r in rows if r['flags']]
    if a.md:
        with open(a.md, 'w', encoding='utf-8') as fh:
            fh.write(to_markdown(rows, os.path.basename(a.map)))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)
    print('%d heroes, %d flagged' % (len(rows), len(bad)))
    kinds = {}
    for r in bad:
        for f in r['flags']:
            k = f.split(' (')[0]
            kinds[k] = kinds.get(k, 0) + 1
    print(kinds)
    if a.strict and bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
