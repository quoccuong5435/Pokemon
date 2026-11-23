"""Convert again, from the .glb sources, the models gen14_expansion uses (src LOCAL_3D) at their target size.

python tools/v412/g14_reconvert.py [dex ...]
Each model gets max(height, 0.4 x length) = model_size_check.target_size(real height) and stands on the ground, so
gen14 shows it with usca 1.0 (GEMINI.md sections 13 and 21). Writes imports/pokemon_3d_mdx/<dex>.mdx + textures.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(WORK, 'tools')]

import glb_to_mdx  # noqa: E402
import mdx_check  # noqa: E402
import model_size_check  # noqa: E402

GLB_DIR = os.path.join(os.path.dirname(WORK), 'imports', 'pokemon_3d_all')
OUT_DIR = os.path.join(WORK, 'imports', 'pokemon_3d_mdx')
TEX_DIR = os.path.join(OUT_DIR, 'textures')


def heights_by_dex():
    with open(os.path.join(WORK, 'tools', 'pokeapi', 'pokemon_size.json'), encoding='utf-8') as fh:
        species = json.load(fh)
    return {int(v['dex']): float(v['height_m']) for v in species.values()}


def used_dex():
    import gen14_expansion
    return [e['dex'] for e in gen14_expansion.load_species_entries() if e['src'] == 'LOCAL_3D']


def convert(dex, height_m):
    with open(os.path.join(GLB_DIR, '%d.glb' % dex), 'rb') as fh:
        mdx, tex = glb_to_mdx.convert_glb_to_mdx(fh.read(), model_name='Pk_%d' % dex,
                                                 tex_path_prefix='PkFx\\G14\\t\\%d' % dex,
                                                 target_size=model_size_check.target_size(height_m))
    errs = mdx_check.check(mdx)
    if errs:
        raise ValueError('%d: %s' % (dex, errs[0]))
    with open(os.path.join(OUT_DIR, '%d.mdx' % dex), 'wb') as fh:
        fh.write(mdx)
    for rel, data in tex.items():
        with open(os.path.join(TEX_DIR, os.path.basename(rel)), 'wb') as fh:
            fh.write(data)


def main(args):
    heights = heights_by_dex()
    todo = [int(a) for a in args] or used_dex()
    os.makedirs(TEX_DIR, exist_ok=True)
    bad = []
    for d in todo:
        try:
            convert(d, heights[d])
        except Exception as e:  # noqa: BLE001
            bad.append('%d: %s' % (d, e))
    print('converted %d of %d' % (len(todo) - len(bad), len(todo)))
    for b in bad:
        print('  FAILED', b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
