"""Read-only: flood fill of the walkable cells (war3map.wpm) from a point: size and bounds of the room, and whether it
connects to a second point (is the room closed?).

python -I analysis/room_flood.py <x> <y> [<x2> <y2>]
"""
import os
import struct
import sys
from collections import deque

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x'))
wpm = a.read('war3map.wpm')
_v, pw, ph = struct.unpack_from('<iii', wpm, 4)
cells = wpm[16:16 + pw * ph]
ox = oy = -10240.0
x, y = float(sys.argv[1]), float(sys.argv[2])
start = (int((x - ox) / 32), int((y - oy) / 32))
goal = (int((float(sys.argv[3]) - ox) / 32), int((float(sys.argv[4]) - oy) / 32)) if len(sys.argv) > 4 else None
seen = {start}
q = deque([start])
while q:
    cx, cy = q.popleft()
    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
        if 0 <= nx < pw and 0 <= ny < ph and (nx, ny) not in seen and not (cells[ny * pw + nx] & 0x02):
            seen.add((nx, ny))
            q.append((nx, ny))
xs = [c[0] for c in seen]
ys = [c[1] for c in seen]
print('cells %d (%.0f%% of the map); bounds x %.0f..%.0f, y %.0f..%.0f' % (
    len(seen), 100.0 * len(seen) / (pw * ph), min(xs) * 32 + ox, max(xs) * 32 + ox, min(ys) * 32 + oy, max(ys) * 32 + oy))
if goal:
    print('reaches', sys.argv[3:5], goal in seen)
