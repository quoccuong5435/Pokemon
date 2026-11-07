"""v3.4.2: the Pokemon League in Darkrai's closed room (x -10240..-6816, y -5120..-160, west edge).
Ground textures of the room are repainted (no height / cliff change, so pathing stays the same); JASS puts the
portals, statues and the arena centre there. plan() is shared by the preview and the build.

    python -I tools/v34/league_area.py   -> docs/v3.4/league_preview.png (current room vs plan)
"""
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))

ROOM = (-10240.0, -5120.0, -6816.0, -160.0)
ARENA = (-8768.0, -2640.0)          # centre of the battle circle (Gym_X[8] / Gym_Y[8])
ARENA_R = 900.0                     # white marble floor
RING_R = 1060.0                     # black marble ring
LOBBY = (-7360.0, -2640.0)          # where the entrance portal sends you
EXIT = (-7040.0, -2640.0)           # exit portal (to your own base)
PATH_HALF = 192.0                   # half width of the tiled walkway lobby -> arena
# statues of the Elite Four and the Champion around the arena: (who, Pokemon, angle in degrees)
STATUES = [('Will', 'Espeon', 150), ('Koga', 'Weezing', 210), ('Bruno', 'Machamp', 120), ('Karen', 'Umbreon', 240),
           ('Lance', 'Dragonite', 180)]
STATUE_R = 1250.0
# entrance portal in each base (west x is negated for the east base)
BASE_GATE = (-5392.0, -288.0)
TEX = {'floor': 'Xwmb', 'ring': 'Xblm', 'path': 'Xsqd', 'lobby': 'Yrtl', 'trim': 'Xgsb'}


def plan(x, y):
    """texture key for a tile corner at world (x, y) inside the room, None = keep"""
    dx, dy = x - ARENA[0], y - ARENA[1]
    r = (dx * dx + dy * dy) ** 0.5
    if r <= ARENA_R:
        return 'floor'
    if r <= RING_R:
        return 'ring'
    if abs(y - ARENA[1]) <= PATH_HALF and ARENA[0] < x <= LOBBY[0] + 256:
        return 'path'
    if abs(x - LOBBY[0]) <= 448 and abs(y - LOBBY[1]) <= 448 or abs(x - EXIT[0]) <= 192 and abs(y - EXIT[1]) <= 320:
        return 'lobby'
    if r <= RING_R + 256:
        return 'trim'
    return None


def read_w3e(data):
    p = 8 + 1 + 4
    n = struct.unpack_from('<i', data, p)[0]
    tiles = [data[p + 4 + 4 * i: p + 8 + 4 * i].decode() for i in range(n)]
    p += 4 + 4 * n
    c = struct.unpack_from('<i', data, p)[0]
    p += 4 + 4 * c
    w, h = struct.unpack_from('<2i', data, p)
    ox, oy = struct.unpack_from('<2f', data, p + 8)
    return tiles, w, h, ox, oy, p + 16


def repaint(data):
    """w3e bytes with the room repainted (ground texture nibble only)"""
    tiles, w, h, ox, oy, base = read_w3e(data)
    idx = {k: tiles.index(v) for k, v in TEX.items()}
    out = bytearray(data)
    changed = 0
    for j in range(h):
        y = oy + 128 * j
        if not ROOM[1] <= y <= ROOM[3]:
            continue
        for i in range(w):
            x = ox + 128 * i
            if not ROOM[0] <= x <= ROOM[2]:
                continue
            k = plan(x, y)
            if k:
                o = base + 7 * (j * w + i) + 4
                out[o] = (out[o] & 0xF0) | idx[k]
                changed += 1
    return bytes(out), changed


def preview(map_path, out_png):
    import sys
    from PIL import Image, ImageDraw
    sys.path.insert(0, os.path.dirname(HERE))
    import mpq
    data = mpq.MPQ(map_path).read('war3map.w3e')
    new, changed = repaint(data)
    colours = {'Xdrt': (120, 92, 64), 'Xwmb': (225, 225, 220), 'Xblm': (45, 45, 55), 'Xsqd': (196, 170, 120),
               'Yrtl': (170, 150, 140), 'Xgsb': (90, 140, 70), 'Xbtl': (150, 80, 60)}
    S = 6
    imgs = []
    for d in (data, new):
        tiles, w, h, ox, oy, base = read_w3e(d)
        i0, i1 = int((ROOM[0] - ox) / 128), int((ROOM[2] - ox) / 128) + 1
        j0, j1 = int((ROOM[1] - oy) / 128), int((ROOM[3] - oy) / 128) + 1
        img = Image.new('RGB', ((i1 - i0) * S, (j1 - j0) * S))
        dr = ImageDraw.Draw(img)
        for j in range(j0, j1):
            for i in range(i0, i1):
                t = tiles[d[base + 7 * (j * w + i) + 4] & 0x0F]
                dr.rectangle([(i - i0) * S, (j1 - 1 - j) * S, (i - i0 + 1) * S - 1, (j1 - j) * S - 1],
                             fill=colours.get(t, (100, 100, 100)))
        imgs.append((img, i0, j1, ox, oy, dr))
    img, i0, j1, ox, oy, dr = imgs[1]

    def at(x, y):
        return (x - ox) / 128 * S - i0 * S, j1 * S - (y - oy) / 128 * S

    import math
    for who, poke, ang in STATUES:
        x = ARENA[0] + STATUE_R * math.cos(math.radians(ang))
        y = ARENA[1] + STATUE_R * math.sin(math.radians(ang))
        px, py = at(x, y)
        dr.rectangle([px - 4, py - 4, px + 4, py + 4], fill=(150, 150, 160), outline=(0, 0, 0))
        dr.text((px - 18, py + 5), who, fill=(255, 255, 255))
    for (x, y), label, col in ((LOBBY, 'Entrance', (80, 160, 255)), (EXIT, 'Exit', (255, 120, 80)),
                               (ARENA, 'Arena', (255, 215, 0))):
        px, py = at(x, y)
        dr.ellipse([px - 6, py - 6, px + 6, py + 6], outline=col, width=2)
        dr.text((px - 20, py + 8), label, fill=col)
    both = Image.new('RGB', (imgs[0][0].width * 2 + 10, imgs[0][0].height), (255, 255, 255))
    both.paste(imgs[0][0], (0, 0))
    both.paste(img, (imgs[0][0].width + 10, 0))
    both.save(out_png)
    return changed


if __name__ == '__main__':
    out = os.path.join(WORK, 'docs', 'v3.4', 'league_preview.png')
    n = preview(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x'), out)
    print('wrote', out, '-', n, 'tile corners repainted')


def jass_lines(ids):
    """data lines for V34_Data: arena, lobby, portals, statues (ids: proper name -> [unit ids])"""
    import math
    f = lambda v: repr(float(v))  # noqa: E731
    lines = ['    set League_AX = %s' % f(ARENA[0]), '    set League_AY = %s' % f(ARENA[1]),
             '    set League_LX = %s' % f(LOBBY[0]), '    set League_LY = %s' % f(LOBBY[1]),
             '    set League_EX = %s' % f(EXIT[0]), '    set League_EY = %s' % f(EXIT[1]),
             '    set League_GX = %s' % f(BASE_GATE[0]), '    set League_GY = %s' % f(BASE_GATE[1]),
             '    set League_RoomX0 = %s' % f(ROOM[0]), '    set League_RoomY0 = %s' % f(ROOM[1]),
             '    set League_RoomX1 = %s' % f(ROOM[2]), '    set League_RoomY1 = %s' % f(ROOM[3])]
    for k, (who, poke, ang) in enumerate(STATUES):
        x = ARENA[0] + STATUE_R * math.cos(math.radians(ang))
        y = ARENA[1] + STATUE_R * math.sin(math.radians(ang))
        lines += ["    set League_StatueType[%d] = '%s'" % (k, ids[poke][0]),
                  '    set League_StatueX[%d] = %s' % (k, f(x)), '    set League_StatueY[%d] = %s' % (k, f(y)),
                  '    set League_StatueName[%d] = "%s"' % (k, who)]
    lines.append('    set League_StatueN = %d' % len(STATUES))
    return lines
