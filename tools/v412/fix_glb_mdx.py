"""Repair the MDX files glb_to_mdx.py wrote before the 4.3a crash fix (imports/pokemon_3d_mdx).

python -I tools/v412/fix_glb_mdx.py [folder]
Two format errors (see GEMINI.md section 20):
- ATCH entries had no inclusive size: WC3 read "orig" of "origin Ref" as a size and crashed while loading the map.
- the Root bone's KGTR pointed at global sequence 0, the model has none (-1 = none).
A file is changed only when it has the old layout, so running it again does nothing.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
DEFAULT_DIR = os.path.join(WORK, 'imports', 'pokemon_3d_mdx')
OLD_ENTRY = 96 + 260 + 4  # node + path + id, no size in front


def _chunks(b):
    i, out = 4, []
    while i + 8 <= len(b):
        tag = b[i:i + 4]
        n = struct.unpack_from('<I', b, i + 4)[0]
        out.append([tag, b[i + 8:i + 8 + n]])
        i += 8 + n
    return out


def fix(b):
    """return the repaired bytes, or None when the file does not have the old glb_to_mdx layout"""
    if b[:4] != b'MDLX':
        return None
    cs = _chunks(b)
    tags = [t for t, _ in cs]
    if b'ATCH' not in tags:
        return None
    atch = cs[tags.index(b'ATCH')][1]
    if len(atch) % OLD_ENTRY or struct.unpack_from('<I', atch, 0)[0] != 96:
        return None
    new = bytearray()
    for k in range(len(atch) // OLD_ENTRY):
        e = atch[k * OLD_ENTRY:(k + 1) * OLD_ENTRY]
        e = e[:-4] + struct.pack('<I', k)  # attachment id
        new += struct.pack('<I', 4 + len(e)) + e
    cs[tags.index(b'ATCH')][1] = bytes(new)
    if b'BONE' in tags:
        bone = bytearray(cs[tags.index(b'BONE')][1])
        o = 4 + 80 + 12  # node size, name, object id / parent / flags
        if bone[o:o + 4] == b'KGTR' and struct.unpack_from('<i', bone, o + 12)[0] == 0:
            struct.pack_into('<i', bone, o + 12, -1)
        cs[tags.index(b'BONE')][1] = bytes(bone)
    return b'MDLX' + b''.join(t + struct.pack('<I', len(d)) + d for t, d in cs)


def main(folder):
    done = skipped = 0
    for f in sorted(os.listdir(folder)):
        if not f.lower().endswith('.mdx'):
            continue
        p = os.path.join(folder, f)
        with open(p, 'rb') as fh:
            out = fix(fh.read())
        if out is None:
            skipped += 1
            continue
        with open(p, 'wb') as fh:
            fh.write(out)
        done += 1
    print('repaired %d, left %d (already fixed or other layout) in %s' % (done, skipped, folder))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR)
