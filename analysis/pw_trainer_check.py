"""Read-only: check the Pokemon World trainer models picked for gym leaders / Elite Four (version, textures, size).

    python -I analysis/pw_trainer_check.py Brock Ondine ...
"""
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import mpq  # noqa: E402
import mdxinfo  # noqa: E402

MAPS = os.path.dirname(WORK)
GAME = ('textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\', 'environment\\', 'objects\\', 'ui\\')


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def main():
    pw = PW(os.path.join(MAPS, 'Pokemon World V1.71.w3x'))
    ar = mpq.MPQ(os.path.join(MAPS, 'Pokemon Arena v3.4.10.w3x'))
    an = {n.lower() for n in ar.listfile()}
    tot = 0
    for n in sys.argv[1:]:
        p = 'Unit\\%s.mdx' % n
        if not pw.has(p):
            print(n, 'NOT IN MAP')
            continue
        d = pw.read(p)
        i = mdxinfo.info(d)
        tex = [t for t in i['textures'] if not t.lower().startswith(GAME)]
        miss = [t for t in tex if not pw.has(t)]
        clash = [t for t in tex if pw.has(t) and t.lower() in an and ar.read(t) != pw.read(t)]
        kb = (len(d) + sum(len(pw.read(t)) for t in tex if pw.has(t))) // 1024
        tot += kb
        print(n, i['version'], kb, 'KB', [s for s, _ in i['seqs']][:6], 'missing', miss[:2], 'clash', clash[:2],
              'portrait', pw.has('Unit\\%s_portrait.mdx' % n))
    print('total KB', tot)


if __name__ == '__main__':
    main()
