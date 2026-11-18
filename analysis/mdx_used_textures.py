"""Read-only: which textures of a Pokemon World model the material layers really use.

    python -I -X utf8 analysis/mdx_used_textures.py 495 496 ...
"""
import os
import struct
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import mpq  # noqa: E402
import mdxinfo  # noqa: E402


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def used(d):
    tex, ids = [], set()
    for tag, body in mdxinfo.chunks(d):
        if tag == b'TEXS':
            for k in range(len(body) // 268):
                e = body[k * 268:(k + 1) * 268]
                tex.append(e[4:264].split(b'\0')[0].decode('latin-1'))
        elif tag == b'MTLS':
            p = 0
            while p < len(body):
                msize = struct.unpack_from('<I', body, p)[0]
                mat = body[p:p + msize]
                q = 4 + 4 + 4  # size, priority plane, flags
                if mat[q:q + 4] != b'LAYS':  # v800 has no shader name
                    q += 80
                q += 4
                nl = struct.unpack_from('<I', mat, q)[0]
                q += 4
                for _ in range(nl):
                    lsize = struct.unpack_from('<I', mat, q)[0]
                    ids.add(struct.unpack_from('<I', mat, q + 12)[0])
                    q += lsize
                p += msize
    return tex, ids


def main():
    pw = PW(os.path.join(os.path.dirname(WORK), 'Pokemon World V1.71.w3x'))
    for d in sys.argv[1:]:
        tex, ids = used(pw.read('Unit\\%s.mdx' % d))
        miss = [(i, t) for i, t in enumerate(tex) if t and not pw.has(t) and not t.lower().startswith(('textures', 'replaceable'))]
        print(d, 'missing textures used by layers:', [t for i, t in miss if i in ids], '| unused:', [t for i, t in miss if i not in ids])


if __name__ == '__main__':
    main()
