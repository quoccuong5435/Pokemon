"""Read-only: the Gen 2-7 starter lines in Pokemon World: model file, textures, scale, icon (from its skin data).

    python -I -X utf8 analysis/pw_starter_check.py
"""
import json
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
sys.path.insert(0, os.path.join(WORK, 'analysis'))
import mpq  # noqa: E402
import mdxinfo  # noqa: E402
import pw_spell_fx as P  # noqa: E402

MAPS = os.path.dirname(WORK)
GAME = ('textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\', 'environment\\', 'objects\\', 'ui\\')
DEX = [158, 159, 160, 258, 259, 260, 387, 388, 389, 390, 391, 392, 393, 394, 395, 495, 496, 497, 498, 499, 500,
       650, 651, 652, 653, 654, 655, 656, 657, 658, 725, 726, 727]


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def main():
    pw = PW(os.path.join(MAPS, 'Pokemon World V1.71.w3x'))
    sk = P.parse_obj(os.path.join(WORK, 'out', 'pkworld', 'war3mapSkin.w3u'), False)
    un = P.parse_obj(os.path.join(WORK, 'out', 'pkworld', 'war3map.w3u'), False)
    by_model = {}
    for k, v in sk.items():
        mdl = str(v.get('umdl', '')).replace('/', '\\').lower()
        by_model.setdefault(mdl, (k, v))
    out = {}
    tot = 0
    for d in DEX:
        f = '%03d' % d
        p = 'Unit\\%s.mdx' % f
        row = {'dex': d, 'model': p if pw.has(p) else None}
        if pw.has(p):
            data = pw.read(p)
            i = mdxinfo.info(data)
            tex = [t for t in i['textures'] if not t.lower().startswith(GAME)]
            row['missing'] = [t for t in tex if not pw.has(t)]
            row['kb'] = (len(data) + sum(len(pw.read(t)) for t in tex if pw.has(t))) // 1024
            row['seqs'] = [s for s, _ in i['seqs']][:5]
            tot += row['kb']
        k, v = by_model.get(('unit\\%s.mdl' % f), (None, {}))
        row['pw_unit'] = k
        row['name'] = un.get(k, {}).get('unam') if k else None
        row['scale'] = v.get('usca')
        icon = v.get('uico') or v.get('uico1')
        row['icon'] = icon
        row['icon_ok'] = bool(icon) and pw.has(str(icon).replace('/', '\\'))
        out[d] = row
        print(d, row['name'], row.get('kb'), 'KB', 'scale', row['scale'], 'icon', icon, row['icon_ok'],
              'missing', row.get('missing', [])[:2])
    print('total KB', tot)
    json.dump(out, open(os.path.join(WORK, 'out', 'pkworld', 'starters.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()
