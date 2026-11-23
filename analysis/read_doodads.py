"""Read-only: list the doodads (war3map.doo) of a map, optionally only those near the two bases.

python -I analysis/read_doodads.py "../Pokemon Arena v3.4.2.w3x" [--base] [--all]

Layout (checked on v3.4.2): 'W3do', int32 version (8), int32 subversion (11), int32 doodad count,
then 50-byte records: char[4] type, int32 variation, float x y z, float angle, float sx sy sz,
byte flags, byte life, int32 item table (-1), int32 item sets (0), int32 doodad id;
then int32 special version + int32 special count (both 0 here). The reader checks that all
bytes are consumed.
"""
import argparse
import collections
import os
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

REC = 50


def parse(data):
    magic, version, sub, count = struct.unpack_from('<4siii', data, 0)
    if magic != b'W3do':
        raise ValueError('not a doo file')
    out = []
    p = 16
    for _ in range(count):
        typ, var, x, y, z, ang, sx, sy, sz, flags, life, item, sets, did = struct.unpack_from(
            '<4si3f f3f BBiii', data, p)
        out.append({'type': typ.decode('latin-1'), 'var': var, 'x': x, 'y': y, 'z': z, 'angle': ang,
                    'scale': (sx, sy, sz), 'flags': flags, 'life': life, 'id': did})
        p += REC
    spec_ver, spec_cnt = struct.unpack_from('<ii', data, p)
    p += 8
    if p != len(data) or spec_cnt != 0:
        raise ValueError('layout mismatch: consumed %d of %d bytes, special=%d' % (p, len(data), spec_cnt))
    return version, sub, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--base', action='store_true', help='only doodads near the two bases (|x| > 4000, |y| < 1500)')
    ap.add_argument('--all', action='store_true', help='print every doodad')
    args = ap.parse_args()
    data = mpq.MPQ(args.map).read('war3map.doo')
    version, sub, doos = parse(data)
    print('doo version %d.%d, %d doodads, all bytes read' % (version, sub, len(doos)))
    near = [d for d in doos if abs(d['x']) > 4000 and abs(d['y']) < 1500]
    print('near the bases: %d' % len(near))
    counts = collections.Counter(d['type'] for d in near)
    print('types near the bases:')
    for t, n in counts.most_common():
        print('  %s x%d' % (t, n))
    if args.all or args.base:
        for d in near if args.base else doos:
            print('%s x=%.0f y=%.0f z=%.0f angle=%.2f scale=%s id=%d' % (
                d['type'], d['x'], d['y'], d['z'], d['angle'], tuple(round(s, 2) for s in d['scale']), d['id']))


if __name__ == '__main__':
    main()
