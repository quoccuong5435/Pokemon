"""Overview image of a map's terrain: one pixel per tile, coloured by ground texture index (w3e),
with the known world positions of the mod marked. World coords: tile = (x - offset) / 128."""
import struct, sys, colorsys
from PIL import Image, ImageDraw
sys.path.insert(0, 'tools')
import mpq

MAP = sys.argv[1] if len(sys.argv) > 1 else '../POKEMON NEW/Pokemon Arena Big.w3x'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'analysis/map_overview.png'

m = mpq.MPQ(MAP)
e = m.read('war3map.w3e')
p = 8 + 1 + 4
n = struct.unpack_from('<i', e, p)[0]; p += 4 + 4 * n
c = struct.unpack_from('<i', e, p)[0]; p += 4 + 4 * c
w, h = struct.unpack_from('<2i', e, p); p += 8   # vertices = tiles + 1
ox, oy = struct.unpack_from('<2f', e, p); p += 8
tw, th = w - 1, h - 1
ground = [[0] * w for _ in range(h)]
cliff = [[0] * w for _ in range(h)]
for j in range(h):
    for i in range(w):
        rec = e[p + 7 * (j * w + i): p + 7 * (j * w + i) + 7]
        ground[j][i] = rec[4] & 0x0F
        cliff[j][i] = rec[5] & 0x3F  # cliff/texture details (coarse)

S = 2  # pixels per tile
img = Image.new('RGB', (tw * S, th * S), (0, 0, 0))
px = img.load()
def colour(t):
    r, g, b = colorsys.hsv_to_rgb((t * 0.618) % 1.0, 0.55, 0.85)
    return int(r * 255), int(g * 255), int(b * 255)
palette = {t: colour(t) for t in range(16)}
for j in range(th):
    for i in range(tw):
        col = palette[ground[j][i]]
        for dy in range(S):
            for dx in range(S):
                px[i * S + dx, j * S + dy] = col
d = ImageDraw.Draw(img)
def mark(x, y, label, col):
    tx = (x - ox) / 128.0
    ty = th - (y - oy) / 128.0   # image row 0 = top = max y
    X, Y = tx * S, ty * S
    d.ellipse([X - 4, Y - 4, X + 4, Y + 4], outline=col, width=2)
    d.text((X + 6, Y - 6), label, fill=col)
for x, y, lab in [(0, 0, 'arena'), (4416, 640, 'shop E'), (-4416, -640, 'shop W'),
                  (2356, -43, 'NPC hoc chieu'), (-3008, -3, 'pos -3008'), (648, 4512, 'NPC cu')]:
    mark(x, y, lab, (255, 255, 255))
img.save(OUT)
print('size tiles', tw, th, 'origin', ox, oy, 'saved', OUT)
print('ground textures used', sorted({t for row in ground for t in row}))
