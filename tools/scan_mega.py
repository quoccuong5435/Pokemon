"""List files whose names contain a keyword inside other maps (read-only)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpq  # noqa: E402

CORE = ('war3map.w3u', 'war3map.j', 'scripts\\war3map.j', 'Units\\UnitUI.slk', 'war3map.lua',
        'war3map.w3a', 'war3map.w3t', 'Units\\ItemFunc.txt', 'war3map.imp')


def main():
    kw = sys.argv[1].lower()
    for path in sys.argv[2:]:
        try:
            a = mpq.MPQ(path)
        except Exception as e:  # noqa
            print('##', os.path.basename(path), 'ERR', e)
            continue
        names = set(a.listfile())
        for core in CORE:
            try:
                d = a.read(core)
            except Exception:
                continue
            for m in re.finditer(rb'[A-Za-z0-9_\\/ ().\-]{2,120}\.(?:mdx|mdl|blp)', d, re.I):
                names.add(m.group(0).decode('latin-1'))
        hits = sorted(n for n in names if kw in n.lower())
        print('##', os.path.basename(path), 'listfile', len(a.listfile()), 'hits', len(hits))
        for n in hits:
            ok = a.has(n) or (n.lower().endswith('.mdl') and a.has(n[:-4] + '.mdx'))
            print('   ', 'OK ' if ok else '-- ', n)


if __name__ == '__main__':
    main()
