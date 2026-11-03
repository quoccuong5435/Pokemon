"""Print the name/tip text of a few custom abilities straight from war3map.w3a (levels/pointer layout)."""
import struct
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402

d = mpq.MPQ(sys.argv[1]).read('war3map.w3a')
want = set(sys.argv[2:])
p = 0


def i():
    global p
    v = struct.unpack_from('<i', d, p)[0]
    p += 4
    return v


def f():
    global p
    v = struct.unpack_from('<f', d, p)[0]
    p += 4
    return v


def s():
    global p
    e = d.index(b'\x00', p)
    v = d[p:e]
    p = e + 1
    return v.decode('utf-8', 'replace')


ver = i()
for table in range(2):
    n = i()
    for _ in range(n):
        orig = d[p:p + 4].decode('latin-1'); p += 4
        new = d[p:p + 4].decode('latin-1'); p += 4
        mc = i()
        out = {}
        for _ in range(mc):
            mid = d[p:p + 4].decode('latin-1'); p += 4
            typ = i()
            lvl = i()
            i()  # data pointer
            v = i() if typ == 0 else f() if typ in (1, 2) else s()
            i()  # trailing 0
            if mid in ('anam', 'atp1', 'aub1', 'aret', 'ahky'):
                out.setdefault(mid, v)
        key = new if new != '\x00\x00\x00\x00' else orig
        if key in want or orig in want:
            print(key, orig, out)
