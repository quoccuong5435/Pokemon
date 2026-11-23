"""Estimate imported models / textures of a map that nothing refers to (object data, SLK / TXT, script, models).

Usage (from _PokemonArena2.0_work):  python -I analysis/unused_assets.py "../Pokemon Arena v4.2a.w3x" [out.txt]
A file counts as used when its full path, or its file name, appears in any of those texts. This over-counts "used"
(a name match is enough), so the result is a lower bound of what could be removed; check before deleting anything.
"""
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

TEXT_EXT = {'w3u', 'w3a', 'w3t', 'w3b', 'w3d', 'w3h', 'w3q', 'slk', 'txt', 'j', 'w3i', 'fdf', 'toc', 'imp', 'mdx',
            'mdl', 'doo'}
ASSET_EXT = {'mdx', 'mdl', 'blp', 'tga'}


def main():
    arc = mpq.MPQ(sys.argv[1])
    data = {}
    for name in arc.listfile():
        try:
            data[name] = arc.read(name)
        except Exception:  # noqa: BLE001
            pass
    ref = b'\n'.join(d.lower() for n, d in data.items() if n.rsplit('.', 1)[-1].lower() in TEXT_EXT)
    unused = []
    for name, blob in data.items():
        ext = name.rsplit('.', 1)[-1].lower()
        if ext not in ASSET_EXT:
            continue
        leaf = name.replace('\\', '/').split('/')[-1].lower()
        stem = os.path.splitext(leaf)[0]
        keys = [name.lower().encode(), leaf.encode(), (stem + '.').encode(), stem.replace('_portrait', '').encode() + b'.']
        if not any(k in ref for k in keys):
            unused.append((len(blob), name))
    unused.sort(reverse=True)
    total = sum(s for s, _n in unused)
    lines = ['%d files, %.1f MiB raw' % (len(unused), total / 1048576.0)]
    lines += ['%8.2f MiB  %s' % (s / 1048576.0, n) for s, n in unused]
    text = '\n'.join(lines)
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w', encoding='utf-8') as fh:
            fh.write(text)
    print('\n'.join(lines[:16]))


if __name__ == '__main__':
    main()
