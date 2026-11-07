"""Read-only: walkable cells (war3map.wpm) around both bases with the shops drawn in, to choose free shop spots.

python -I analysis/base_layout.py
"""
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x'))
w3e = a.read('war3map.w3e')
p = 4 + 4 + 1 + 4
ntile = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * ntile
ncliff = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * ncliff
mw, mh = struct.unpack_from('<ii', w3e, p)
ox, oy = struct.unpack_from('<ff', w3e, p + 8)
wpm = a.read('war3map.wpm')
_v, pw, ph = struct.unpack_from('<iii', wpm, 4)
cells = wpm[16:16 + pw * ph]
print('w3e %dx%d offset %.0f,%.0f; wpm %dx%d' % (mw, mh, ox, oy, pw, ph))


def walkable(x, y):
    cx, cy = int((x - ox) / 32), int((y - oy) / 32)
    if not (0 <= cx < pw and 0 <= cy < ph):
        return False
    return not (cells[cy * pw + cx] & 0x02)


script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
shops = [(t, float(x), float(y)) for t, x, y in re.findall(r"CreateUnit\(p,'(\w{4})',(-?[\d.]+),(-?[\d.]+),", script)]
shops += [(t, float(x), float(y)) for t, x, y in
          re.findall(r"CreateUnit\(Player\(PLAYER_NEUTRAL_PASSIVE\), '(\w{4})', (-?[\d.]+), (-?[\d.]+),", script)]
shops = [s for s in shops if abs(s[1]) > 4000 and abs(s[2]) < 1500]
for side in (-1, 1):
    print('\n%s base (x %s), one char = 64 units; # blocked, . walkable, letters = shops' % ('West' if side < 0 else 'East', side))
    xs = list(range(-6900, -4300, 64)) if side < 0 else list(range(4300, 6900, 64))
    marks = {}
    for t, x, y in shops:
        if (x < 0) == (side < 0):
            marks[(int((x - xs[0]) // 64), int((1400 - y) // 64))] = t[-1]
    for row, y in enumerate(range(1400, -1400, -64)):
        line = ''
        for col, x in enumerate(xs):
            line += marks.get((col, row), '.' if walkable(x, y) else '#')
        print('%6d %s' % (y, line))
    print('shops:', [(t, x, y) for t, x, y in shops if (x < 0) == (side < 0)])
cands = [(-5088, 544), (-5088, -544), (-4784, 544), (-4784, -544), (-6304, 544), (-6304, -544), (-5392, 0), (-5088, 0)]
for side in (-1, 1):
    print('\ncandidates side %d:' % side, [((side * -cx), cy, walkable(side * -cx, cy)) for cx, cy in cands])
