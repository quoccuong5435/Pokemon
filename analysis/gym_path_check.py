"""Read-only: can a hero walk from the West base room to the West gym gate (nwgt at -5120, 640)?
Buildings (base units, shops) block a disc of radius 130 on the walkability grid (war3map.wpm).

python -I analysis/gym_path_check.py [spot_x spot_y ...]   (extra shop spots to test)
"""
import collections
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.4.w3x'))
w3e = a.read('war3map.w3e')
p = 4 + 4 + 1 + 4
nt = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * nt
nc = struct.unpack_from('<i', w3e, p)[0]
p += 4 + 4 * nc
mw, mh = struct.unpack_from('<ii', w3e, p)
ox, oy = struct.unpack_from('<ff', w3e, p + 8)
wpm = a.read('war3map.wpm')
_v, pw, ph = struct.unpack_from('<iii', wpm, 4)
cells = wpm[16:16 + pw * ph]


def walk(x, y):
    cx, cy = int((x - ox) / 32), int((y - oy) / 32)
    return 0 <= cx < pw and 0 <= cy < ph and not (cells[cy * pw + cx] & 0x02)


script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
units = [(float(x), float(y)) for x, y in re.findall(r"CreateUnit\(p(?:layer\(PLAYER_NEUTRAL_PASSIVE\))?,\s*'\w{4}',\s*(-?[\d.]+),\s*(-?[\d.]+),", script)]
units = [u for u in units if u[0] < -4000 and abs(u[1]) < 1500]
extra = [(float(sys.argv[i]), float(sys.argv[i + 1])) for i in range(1, len(sys.argv) - 1, 2)]
blocks = units + extra
R = 130.0


def blocked(x, y):
    return any((x - bx) ** 2 + (y - by) ** 2 < R * R for bx, by in blocks)


start, goal = (-5300.0, 0.0), (-5120.0, 700.0)
seen = {start}
q = collections.deque([start])
ok = False
while q:
    x, y = q.popleft()
    if (x - goal[0]) ** 2 + (y - goal[1]) ** 2 < 200 ** 2:
        ok = True
        break
    for dx, dy in ((64, 0), (-64, 0), (0, 64), (0, -64)):
        n = (x + dx, y + dy)
        if n in seen or not (-9000 < n[0] < -1000 and -2000 < n[1] < 7000):
            continue
        if walk(*n) and not blocked(*n):
            seen.add(n)
            q.append(n)
print('gym gate reachable from the room:', ok, '| blocks:', len(blocks), 'extra:', extra)
