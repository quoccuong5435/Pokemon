"""Read-only: find the names of the files of the v3.4.10 map that its listfile lacks (300 of them), by reading
the contents of the other files, and write tools/v3411/names_v3410.txt (one name per line) for build.py, which
needs every name to grow the hash table.

    python -I analysis/names_v3410.py
"""
import os
import sys
import time

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.10.w3x')
OUT = os.path.join(WORK, 'tools', 'v3411', 'names_v3410.txt')


def main():
    t = time.time()
    m = mpq.MPQ(MAP)
    lf = set(m.listfile())
    found = mpq.discover_names(m, tuple(lf))
    known = {m.find_hash(n) for n in found if m.find_hash(n) is not None}
    used = [i for i, e in enumerate(m.hash_table) if e[4] < mpq.HASH_DELETED]
    left = [i for i in used if i not in known]
    new = sorted(n for n in found if n not in lf)
    open(OUT, 'w', encoding='latin-1').write('\r\n'.join(new) + '\r\n')
    print('names found beyond the listfile: %d; entries still without a name: %d; %.0f s' % (len(new), len(left), time.time() - t))


if __name__ == '__main__':
    main()
