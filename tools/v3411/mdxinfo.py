"""Read-only MDX facts: model extent (radius) and sequences (name, seconds), texture paths."""
import re
import struct


def chunks(d):
    if d[:4] != b'MDLX':
        raise ValueError('not MDX')
    p = 4
    while p + 8 <= len(d):
        tag = d[p:p + 4]
        n = struct.unpack_from('<I', d, p + 4)[0]
        yield tag, d[p + 8:p + 8 + n]
        p += 8 + n


def info(d):
    out = {'radius': None, 'seqs': [], 'textures': [], 'version': None}
    for tag, body in chunks(d):
        if tag == b'VERS':
            out['version'] = struct.unpack_from('<I', body)[0]
        elif tag == b'MODL' and len(body) >= 372:
            r, x0, y0, z0, x1, y1, z1 = struct.unpack_from('<7f', body, 340)
            out['radius'] = max(abs(x0), abs(x1), abs(y0), abs(y1)) if abs(x1 - x0) < 1e6 else None
            out['bounds'] = r
        elif tag == b'SEQS':
            for k in range(len(body) // 132):
                e = body[k * 132:(k + 1) * 132]
                name = e[:80].split(b'\0')[0].decode('latin-1')
                a, b = struct.unpack_from('<II', e, 80)
                out['seqs'].append((name, (b - a) / 1000.0))
        elif tag == b'TEXS':
            for k in range(len(body) // 268):
                e = body[k * 268:(k + 1) * 268]
                rid = struct.unpack_from('<I', e)[0]
                path = e[4:264].split(b'\0')[0].decode('latin-1')
                if rid == 0 and path:
                    out['textures'].append(path)
    return out


def anim_text(seqs):
    return ', '.join('%s (%.1fs)' % (n, s) for n, s in seqs)
