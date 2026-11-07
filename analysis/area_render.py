"""Read-only: picture of a map area (ground texture per tile, blocked cells darkened, cliffs, units the script creates)
to plan terrain work. Writes analysis/area_<name>.png and prints the units in the area.

python -I analysis/area_render.py <name> <xmin> <ymin> <xmax> <ymax> [map]
"""
import colorsys
import os
import re
import struct
import sys

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

name = sys.argv[1]
x0, y0, x1, y1 = (float(v) for v in sys.argv[2:6])
MAP = sys.argv[6] if len(sys.argv) > 6 else os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x')
a = mpq.MPQ(MAP)
e = a.read('war3map.w3e')
p = 8 + 1 + 4
n = struct.unpack_from('<i', e, p)[0]
tiles = [e[p + 4 + 4 * i: p + 8 + 4 * i].decode() for i in range(n)]
p += 4 + 4 * n
c = struct.unpack_from('<i', e, p)[0]
p += 4 + 4 * c
w, h = struct.unpack_from('<2i', e, p)
ox, oy = struct.unpack_from('<2f', e, p + 8)
p += 16
wpm = a.read('war3map.wpm')
_v, pw, ph = struct.unpack_from('<iii', wpm, 4)
cells = wpm[16:16 + pw * ph]


def vert(i, j):
    r = e[p + 7 * (j * w + i): p + 7 * (j * w + i) + 7]
    height = struct.unpack_from('<h', r, 0)[0]
    return r[4] & 0x0F, r[6] & 0x0F, height  # ground texture, layer height (cliff level), height


S = 8   # pixels per tile (128 units)
i0, i1 = int((x0 - ox) / 128), int((x1 - ox) / 128)
j0, j1 = int((y0 - oy) / 128), int((y1 - oy) / 128)
img = Image.new('RGB', ((i1 - i0) * S, (j1 - j0) * S))
d = ImageDraw.Draw(img)
used = {}
for j in range(j0, j1):
    for i in range(i0, i1):
        t, layer, _hgt = vert(i, j)
        used[tiles[t] if t < len(tiles) else t] = used.get(tiles[t] if t < len(tiles) else t, 0) + 1
        hue = (t * 0.13) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.45, 0.35 + 0.08 * layer)
        d.rectangle([(i - i0) * S, (j1 - 1 - j) * S, (i - i0 + 1) * S - 1, (j1 - j) * S - 1],
                    fill=(int(r * 255), int(g * 255), int(b * 255)))
# blocked pathing cells (32 units) darkened
for cy in range(int((y0 - oy) / 32), int((y1 - oy) / 32)):
    for cx in range(int((x0 - ox) / 32), int((x1 - ox) / 32)):
        if cells[cy * pw + cx] & 0x02:
            px = (cx * 32 + ox - x0) / 128 * S
            py = (y1 - (cy * 32 + oy)) / 128 * S
            d.rectangle([px, py - S / 4, px + S / 4, py], fill=(20, 20, 20))
script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
units = re.findall(r"CreateUnit\((?:p|Player\(\w+\)),\s*'(\w{4})',\s*(-?[\d.]+),\s*(-?[\d.]+)", script)
shown = []
for uid, ux, uy in units:
    ux, uy = float(ux), float(uy)
    if x0 <= ux <= x1 and y0 <= uy <= y1:
        px, py = (ux - x0) / 128 * S, (y1 - uy) / 128 * S
        d.ellipse([px - 4, py - 4, px + 4, py + 4], outline=(255, 255, 0))
        d.text((px + 5, py - 5), uid, fill=(255, 255, 0))
        shown.append((uid, ux, uy))
out = os.path.join(WORK, 'analysis', 'area_%s.png' % name)
img.save(out)
print('wrote', out, img.size, 'tiles used:', sorted(used.items(), key=lambda kv: -kv[1])[:8])
print('tileset textures:', tiles)
print('units:', shown[:60])
