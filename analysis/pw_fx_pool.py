"""Read-only: check the Pokemon World effect models (names from the skin files, from other maps and from the decoded
script) and write tools/v3411/fx_pool_pw.json: path, MDX radius, animations, textures, missing / clashing textures.

    python -I analysis/pw_fx_pool.py
"""
import json
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import mpq  # noqa: E402
import mdxinfo  # noqa: E402

MAPS = os.path.dirname(WORK)
OUT = os.path.join(WORK, 'out', 'pkworld')
GAME_DIRS = ('textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\', 'environment\\', 'ui\\', 'objects\\',
             'doodads\\', 'sharedmodels\\', 'buildings\\', 'terrainart\\')
SKIP = ('unit\\', 'building\\', 'doodads\\', 'tree\\')


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def main():
    pw = PW(os.path.join(MAPS, 'Pokemon World V1.71.w3x'))
    ar = mpq.MPQ(os.path.join(MAPS, 'Pokemon Arena v3.4.10.w3x'))
    arnames = {n.lower() for n in ar.listfile()}
    names = set(json.load(open(os.path.join(OUT, 'names.json'))))
    names |= set(json.load(open(os.path.join(OUT, 'script_models.json')))['in_map'])
    cands = sorted(n for n in names if n.lower().endswith('.mdx') and not n.lower().startswith(SKIP)
                   and '_portrait' not in n.lower())
    pool = {}
    for n in cands:
        try:
            d = pw.read(n)
            i = mdxinfo.info(d)
        except Exception:  # noqa: BLE001 - unreadable model
            continue
        texs = [t for t in i['textures'] if not t.lower().startswith(GAME_DIRS)]
        bad, clash, size = [], [], len(d)
        for t in texs:
            if not pw.has(t):
                bad.append(t)
                continue
            td = pw.read(t)
            size += len(td)
            if t.lower() in arnames and ar.read(t) != td:
                clash.append(t)
        key = n.split('\\')[-1][:-4]
        if key in pool:
            continue
        pool[key] = dict(path=n, radius=i['radius'], anim=mdxinfo.anim_text(i['seqs']), tex=texs, missing=bad,
                         clash=clash, kb=size // 1024, ver=i['version'])
    ok = [k for k, v in pool.items() if not v['missing'] and not v['clash'] and v['ver'] == 800]
    json.dump(pool, open(os.path.join(WORK, 'tools', 'v3411', 'fx_pool_pw.json'), 'w'), indent=0)
    print('models', len(pool), 'usable', len(ok))


if __name__ == '__main__':
    main()
