"""Pokemon Arena Big: the v3.2.10 build with the terrain (w3e, wpm, shd, doo), playable size and camera of
_NarutoRPGPlus1.120.w3x. The script, units and abilities are kept, so the arena keeps its world coordinates."""
import struct, sys
sys.path.insert(0, 'tools')
import mpq

BASE = '../Pokemon Arena v3.2.10.w3x'
DONOR = '../_NarutoRPGPlus1.120.w3x'
OUT = '../POKEMON NEW/Pokemon Arena Big.w3x'
NAME = b'Pokemon Arena Big'
TERRAIN = ['war3map.w3e', 'war3map.wpm', 'war3map.shd', 'war3map.doo']


def after_strings(d):
    p = 12
    for _ in range(4):
        p = d.index(b'\x00', p) + 1
    return p


base = mpq.MPQ(BASE)
donor = mpq.MPQ(DONOR)
bw = bytearray(base.read('war3map.w3i'))
dw = donor.read('war3map.w3i')
pb = after_strings(bw)
pd = after_strings(dw)
bw[pb:pb + 32] = dw[pd:pd + 32]                       # camera bounds
w, h = struct.unpack_from('<2i', dw, pd + 48)
struct.pack_into('<2i', bw, pb + 48, w, h)            # playable size
bw[pb + 60] = dw[pd + 60]                              # tileset letter
name_end = bw.index(b'\x00', 12)                       # first string = map name shown in the game list
bw = bytearray(bytes(bw[:12]) + NAME + b'\x00' + bytes(bw[name_end + 1:]))
files = {'war3map.w3i': bytes(bw)}
for n in TERRAIN:
    files[n] = donor.read(n)
base.save_with(OUT, files, extra_listfile=None)
print('wrote', OUT, 'playable', w, h)
