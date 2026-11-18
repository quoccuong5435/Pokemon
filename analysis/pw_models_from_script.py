"""Read-only: decoded Pokemon World script + the effect models it names.

    python -I analysis/pw_models_from_script.py
writes out/pkworld/war3map_decoded.j, out/pkworld/script_models.json
"""
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'analysis'))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import pw_decrypt as D  # noqa: E402
import mpq  # noqa: E402

OUT = os.path.join(WORK, 'out', 'pkworld')
LIT = re.compile(r'RxL\("((?:[^"\\]|\\.)*)"\)')


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def main():
    t = open(os.path.join(OUT, 'war3map.j'), encoding='latin-1').read()

    def rep(m):
        s = D.decode(D.unescape(m.group(1)))
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

    dec = LIT.sub(rep, t)
    open(os.path.join(OUT, 'war3map_decoded.j'), 'w', encoding='latin-1', errors='replace').write(dec)
    strings = [D.decode(D.unescape(x)) for x in LIT.findall(t)]
    mods = sorted({v for v in strings if re.search(r'\.(mdx|mdl)$', v, re.I)})
    pw = PW(os.path.join(os.path.dirname(WORK), 'Pokemon World V1.71.w3x'))
    known = set(n.lower() for n in json.load(open(os.path.join(OUT, 'names.json'))))
    inmap, game = [], []
    for m in mods:
        c = m.replace('/', '\\')
        hit = next((x for x in (c, c[:-4] + '.mdx') if pw.has(x)), None)
        if hit:
            inmap.append(hit)
        else:
            game.append(m)
    new = sorted(set(x for x in inmap if x.lower() not in known))
    print('model strings', len(mods), 'in the map', len(set(inmap)), 'game models', len(game), 'new names', len(new))
    print(new)
    json.dump({'in_map': sorted(set(inmap)), 'new': new, 'game': game},
              open(os.path.join(OUT, 'script_models.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()
