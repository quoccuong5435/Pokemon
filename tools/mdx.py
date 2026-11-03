"""Tiny MDX inspector: version, sequences, textures (enough to import a model safely)."""
import struct


def inspect(data):
    if data[:4] != b'MDLX':
        return {'error': 'not MDLX'}
    info = {'version': None, 'name': '', 'sequences': [], 'textures': [], 'size': len(data)}
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4].decode('latin-1')
        size = struct.unpack_from('<I', data, p + 4)[0]
        body = data[p + 8:p + 8 + size]
        if tag == 'VERS':
            info['version'] = struct.unpack_from('<I', body)[0]
        elif tag == 'MODL':
            info['name'] = body[:80].split(b'\x00')[0].decode('latin-1')
        elif tag == 'SEQS':
            for i in range(len(body) // 132):
                s = body[i * 132:(i + 1) * 132]
                info['sequences'].append(s[:80].split(b'\x00')[0].decode('latin-1'))
        elif tag == 'TEXS':
            for i in range(len(body) // 268):
                t = body[i * 268:(i + 1) * 268]
                rid = struct.unpack_from('<I', t)[0]
                path = t[4:264].split(b'\x00')[0].decode('latin-1')
                info['textures'].append((rid, path))
        p += 8 + size
    return info


def vertex_height(data):
    """Height (max z - min z) of all geoset vertices in bind pose; None if no vertices."""
    if data[:4] != b'MDLX':
        return None
    zmin, zmax = None, None
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4]
        size = struct.unpack_from('<I', data, p + 4)[0]
        if tag == b'GEOS':
            q = p + 8
            end = q + size
            while q < end:
                gsize = struct.unpack_from('<I', data, q)[0]
                if data[q + 4:q + 8] == b'VRTX':
                    n = struct.unpack_from('<I', data, q + 8)[0]
                    zs = struct.unpack_from('<%df' % (n * 3), data, q + 12)[2::3]
                    if zs:
                        lo, hi = min(zs), max(zs)
                        zmin = lo if zmin is None else min(zmin, lo)
                        zmax = hi if zmax is None else max(zmax, hi)
                q += gsize
        p += 8 + size
    if zmin is None or zmax - zmin <= 1.0:
        return None
    return zmax - zmin


def model_height(data):
    """Model height: geoset vertices first, else MODL extent, else first 'stand' sequence; None if unknown."""
    if data[:4] != b'MDLX':
        return None
    vh = vertex_height(data)
    if vh is not None:
        return vh
    modl = seq = None
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4]
        size = struct.unpack_from('<I', data, p + 4)[0]
        body = data[p + 8:p + 8 + size]
        if tag == b'MODL' and len(body) >= 368:
            mn = struct.unpack_from('<3f', body, 344)
            mx = struct.unpack_from('<3f', body, 356)
            modl = mx[2] - mn[2]
        elif tag == b'SEQS':
            for i in range(len(body) // 132):
                s = body[i * 132:(i + 1) * 132]
                if s[:80].split(b'\x00')[0].decode('latin-1').lower().startswith('stand'):
                    mn = struct.unpack_from('<3f', s, 108)
                    mx = struct.unpack_from('<3f', s, 120)
                    seq = mx[2] - mn[2]
                    break
        p += 8 + size
    for h in (modl, seq):
        if h is not None and 1.0 < h < 100000.0:
            return h
    return None


def patch_texture_paths(data, mapping):
    """Rewrite TEXS path fields (260 bytes, zero padded) using mapping old->new. Size unchanged."""
    out = bytearray(data)
    p = 4
    while p + 8 <= len(out):
        tag = bytes(out[p:p + 4])
        size = struct.unpack_from('<I', out, p + 4)[0]
        if tag == b'TEXS':
            for i in range(size // 268):
                f = p + 8 + i * 268 + 4
                old = bytes(out[f:f + 260]).split(b'\x00')[0].decode('latin-1')
                if old in mapping:
                    new = mapping[old].encode('latin-1')
                    if len(new) >= 260:
                        raise ValueError('texture path too long: %s' % mapping[old])
                    out[f:f + 260] = new + b'\x00' * (260 - len(new))
        p += 8 + size
    return bytes(out)

