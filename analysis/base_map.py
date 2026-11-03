"""Render the walkable area around both bases with shop positions and candidate spots (read-only)."""
import re
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
w3e = a.read('war3map.w3e')
p = 4 + 4 + 1 + 4
ng = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * ng
nc = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * nc
mx, my = struct.unpack_from('<ii', w3e, p)
cx, cy = struct.unpack_from('<ff', w3e, p + 8)
wpm = a.read('war3map.wpm')
pw, ph = struct.unpack_from('<ii', wpm, 8)
cells = wpm[16:16 + pw * ph]
print('tiles', mx, my, 'origin', cx, cy, 'pathing', pw, ph)


def cell(x, y):
    i = int((x - cx) / 32)
    j = int((y - cy) / 32)
    if 0 <= i < pw and 0 <= j < ph:
        return cells[j * pw + i]
    return 0xFF


j = a.read('scripts\\war3map.j').decode('latin-1')
units = [(m.group(1), float(m.group(2)), float(m.group(3))) for m in
         re.finditer(r"CreateUnit\(p,'(\w{4})',(-?[\d.]+),(-?[\d.]+),", j)]
labels = {'n00P': 'PokeCenter', 'n00O': 'PokeMart', 'n00N': 'SuperMart1', 'n00Q': 'SuperMart2', 'nwgt': 'Waygate',
          'n030': 'Legendary'}
ours = [('MegaI', -5248, 384), ('MegaII', -5248, -384), ('MegaIII', -4864, 0)]
cands = {'A': (-6400, 1100), 'B': (-6400, -1100), 'C': (-5952, 1100), 'D': (-5952, -1100),
         'E': (-6656, 384), 'F': (-6656, -384)}

for side, sx in (('west', -1), ('east', 1)):
    x0, x1, y0, y1 = (-7400, -3600, -2200, 2200) if sx < 0 else (3600, 7400, -2200, 2200)
    scale = 0.25  # px per world unit
    W, H = int((x1 - x0) * scale), int((y1 - y0) * scale)
    img = Image.new('RGB', (W, H))
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            wx = x0 + xx / scale
            wy = y1 - yy / scale
            c = cell(wx, wy)
            walk = not (c & 0x02)
            build = not (c & 0x08)
            px[xx, yy] = (60, 140, 60) if walk and build else ((140, 140, 90) if walk else (25, 25, 35))
    d = ImageDraw.Draw(img)

    def mark(x, y, text, col):
        u, v = (x - x0) * scale, (y1 - y) * scale
        d.rectangle([u - 14, v - 14, u + 14, v + 14], outline=col, width=3)
        d.text((u + 16, v - 8), text, fill=col)

    for uid, x, y in units:
        if uid in labels and x0 <= x <= x1 and y0 <= y <= y1:
            mark(x, y, labels[uid], (255, 255, 255))
    for name, x, y in ours:
        mark(x * -sx * -1 if sx > 0 else x, y * (-1 if sx > 0 else 1), name, (200, 80, 255))
    for k, (x, y) in cands.items():
        X = x if sx < 0 else -x
        Y = y if sx < 0 else -y
        ok = all(not (cell(X + dx, Y + dy) & 0x0A) for dx in range(-128, 129, 32) for dy in range(-128, 129, 32))
        mark(X, Y, k + ('' if ok else ' (blocked)'), (255, 220, 0) if ok else (255, 60, 60))
    img.save(sys.argv[3] + '_%s.png' % side)
    print('saved', side)
