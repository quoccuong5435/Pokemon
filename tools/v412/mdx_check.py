"""Structural check of MDX 800 models (the ones code generates: glb_to_mdx.py) before they go into a map.

python -I tools/v412/mdx_check.py <file.mdx | folder> ...
A wrong size / index in an MDX does not give an error in WC3 Reforged: the game crashes while loading the map
(4.3a: ATCH entries without their inclusive size -> the game read "orig" of "origin Ref" as a size, crash on load).
"""
import os
import struct
import sys

NODE_KINDS = (b'BONE', b'HELP', b'ATCH')  # read entry by entry (EVTS / CLID entries have no own size)
OTHER_NODES = (b'LITE', b'PREM', b'PRE2', b'RIBB', b'EVTS', b'CLID', b'CORN')


def chunks(b):
    if b[:4] != b'MDLX':
        raise ValueError('not an MDLX file')
    i, out = 4, []
    while i < len(b):
        if i + 8 > len(b):
            raise ValueError('truncated chunk header at %d' % i)
        tag = b[i:i + 4]
        if tag == b'\0\0\0\0':
            break  # zero padding at the end
        n = struct.unpack_from('<I', b, i + 4)[0]
        if i + 8 + n > len(b):
            raise ValueError('chunk %r runs past the end of the file' % tag)
        out.append((tag, i + 8, n))
        i += 8 + n
    return out


def _tracks(b, o, end, errs, where, nglobal):
    """skip the K??? tracks of a node or attachment starting at o; return the offset after them"""
    sizes = {b'KGTR': 12, b'KGSC': 12, b'KGRT': 16, b'KATV': 4}
    while o + 16 <= end and b[o:o + 4] in sizes:
        tag = b[o:o + 4]
        n, interp, gs = struct.unpack_from('<IIi', b, o + 4)
        if gs != -1 and not 0 <= gs < nglobal:
            errs.append('%s %s uses global sequence %d, model has %d' % (where, tag.decode(), gs, nglobal))
        per = 4 + sizes[tag] * (3 if interp > 1 else 1)
        o += 16 + n * per
    return o


def check(b):
    """list of problems (empty = the structure is sound)"""
    errs = []
    try:
        cs = chunks(b)
    except ValueError as e:
        return [str(e)]
    by = {}
    for tag, o, n in cs:
        by.setdefault(tag, (o, n))
    if b'VERS' in by and struct.unpack_from('<I', b, by[b'VERS'][0])[0] != 800:
        return []  # only MDX 800 is checked
    nglobal = by[b'GLBS'][1] // 4 if b'GLBS' in by else 0
    ntex = by[b'TEXS'][1] // 268 if b'TEXS' in by else 0
    if b'TEXS' in by and by[b'TEXS'][1] % 268:
        errs.append('TEXS size %d is not a multiple of 268' % by[b'TEXS'][1])
    # materials: count them and check the texture of each layer
    nmat = 0
    if b'MTLS' in by:
        o, n = by[b'MTLS']
        end = o + n
        while o < end:
            size = struct.unpack_from('<I', b, o)[0]
            if size < 12 or o + size > end:
                errs.append('material %d has size %d' % (nmat, size))
                break
            if b[o + 12:o + 16] == b'LAYS':
                nl = struct.unpack_from('<I', b, o + 16)[0]
                lo = o + 20
                for _ in range(nl):
                    lsize, _f, _s, tex = struct.unpack_from('<IIII', b, lo)
                    if tex >= ntex:
                        errs.append('material %d uses texture %d, model has %d' % (nmat, tex, ntex))
                    lo += lsize
            nmat += 1
            o += size
    # objects: every node needs a pivot, ids 0..n-1
    ids = []
    for tag in NODE_KINDS:
        if tag not in by:
            continue
        o, n = by[tag]
        end = o + n
        while o < end:
            size = struct.unpack_from('<I', b, o)[0]
            node_o = o + 4 if tag not in (b'BONE', b'HELP') else o
            if tag in (b'BONE', b'HELP'):
                node_size = size
            else:
                node_size = struct.unpack_from('<I', b, node_o)[0]
                if node_size != 96 and node_size > size:
                    errs.append('%s entry: node size %d is larger than the entry (%d)' % (tag.decode(), node_size, size))
                    break
            name = b[node_o + 4:node_o + 84].split(b'\0')[0]
            if not name or not all(c >= 32 for c in name):  # GBK (Chinese) names are fine
                errs.append('%s entry has an unreadable name %r (wrong size before it?)' % (tag.decode(), name[:20]))
                break
            oid, parent = struct.unpack_from('<Ii', b, node_o + 84)
            ids.append((oid, parent, tag.decode(), name.decode('latin-1')))
            _tracks(b, node_o + 96, node_o + node_size, errs, '%s %r' % (tag.decode(), name.decode('latin-1')), nglobal)
            if tag in (b'BONE', b'HELP'):
                if tag == b'BONE':
                    gs_id = struct.unpack_from('<i', b, node_o + node_size)[0]
                    if gs_id != -1 and gs_id >= 0 and b'GEOS' not in by:
                        errs.append('bone %r points at geoset %d, model has none' % (name.decode('latin-1'), gs_id))
                o = node_o + node_size + (8 if tag == b'BONE' else 0)
            else:
                if size < 4 + node_size:
                    errs.append('%s entry size %d is smaller than its node' % (tag.decode(), size))
                    break
                o += size
    npiv = by[b'PIVT'][1] // 12 if b'PIVT' in by else 0
    got = sorted(i for i, _p, _t, _n in ids)
    if not any(t in by for t in OTHER_NODES) and got != list(range(len(ids))):
        errs.append('object ids are %s, expected 0..%d' % (got, len(ids) - 1))
    if npiv < len(ids):
        errs.append('PIVT has %d pivots for %d objects' % (npiv, len(ids)))
    for oid, parent, tag, name in ids:
        if parent != -1 and not 0 <= parent < max(len(ids), npiv):
            errs.append('%s %r has parent %d (no such object)' % (tag, name, parent))
    nbones = sum(1 for _i, _p, t, _n in ids if t == 'BONE')
    # geosets: material, index range, matrix groups
    if b'GEOS' in by:
        o, n = by[b'GEOS']
        end = o + n
        k = 0
        while o < end:
            size = struct.unpack_from('<I', b, o)[0]
            g, gend = o + 4, o + size
            vcount = nidx = 0
            groups = []
            while g + 8 <= gend and b[g:g + 4].isalpha():
                tag = b[g:g + 4]
                cnt = struct.unpack_from('<I', b, g + 4)[0]
                g += 8
                if tag == b'VRTX':
                    vcount = cnt
                    g += 12 * cnt
                elif tag == b'NRMS':
                    g += 12 * cnt
                elif tag in (b'PTYP', b'PCNT', b'MTGC', b'MATS'):
                    vals = struct.unpack_from('<%dI' % cnt, b, g)
                    if tag == b'MTGC':
                        groups = vals
                    if tag == b'MATS':
                        bad = [v for v in vals if ids and v >= len(ids)]
                        if bad:
                            errs.append('geoset %d matrix uses object %s, model has %d' % (k, bad[:3], len(ids)))
                    g += 4 * cnt
                elif tag == b'PVTX':
                    idx = struct.unpack_from('<%dH' % cnt, b, g)
                    nidx = cnt
                    if idx and max(idx) >= vcount:
                        errs.append('geoset %d face uses vertex %d, has %d' % (k, max(idx), vcount))
                    g += 2 * cnt
                elif tag == b'GNDX':
                    gi = b[g:g + cnt]
                    if gi and groups and max(gi) >= len(groups):
                        errs.append('geoset %d vertex group %d, has %d groups' % (k, max(gi), len(groups)))
                    g += cnt
                else:
                    break
            if g + 12 <= gend:
                mat = struct.unpack_from('<I', b, g)[0]
                if mat >= nmat:
                    errs.append('geoset %d uses material %d, model has %d' % (k, mat, nmat))
            if nidx % 3:
                errs.append('geoset %d has %d indices (not triangles)' % (k, nidx))
            k += 1
            o += size
    return errs


def main(paths):
    bad = 0
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith('.mdx')]
        else:
            files.append(p)
    for f in files:
        with open(f, 'rb') as fh:
            errs = check(fh.read())
        if errs:
            bad += 1
            print('%s: %s' % (os.path.basename(f), '; '.join(errs[:3])))
    print('%d models, %d with problems' % (len(files), bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
