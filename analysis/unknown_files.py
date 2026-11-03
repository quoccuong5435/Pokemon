"""Identify the unknown-named files of v1.8 by content (read-only)."""
import collections
import sys

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
known = {a.find_hash(n) for n in mpq.discover_names(a)}
kinds = collections.Counter()
for p, e in enumerate(a.hash_table):
    if e[4] >= mpq.HASH_DELETED or p in known:
        continue
    off, csize, fsize, flags = a.block_table[e[4]]
    if fsize == 0:
        kinds['empty'] += 1
        continue
    try:
        d = a.read_block(e[4])
    except Exception as ex:  # noqa
        kinds['unreadable'] += 1
        print(p, 'unreadable', ex)
        continue
    magic = d[:4]
    kind = {b'BLP1': 'blp1', b'BLP2': 'blp2', b'MDLX': 'mdx', b'RIFF': 'wav', b'ID3\x03': 'mp3',
            b'\x00\x01\x00\x00': 'ttf'}.get(magic, repr(magic))
    kinds[kind] += 1
    extra = ''
    if kind == 'blp1':
        import struct
        comp, flags_, w, h = struct.unpack_from('<IIII', d, 4)
        extra = '%dx%d comp=%d' % (w, h, comp)
    print(p, kind, fsize, extra)
print(kinds)
