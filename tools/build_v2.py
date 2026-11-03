"""Build Pokemon Arena v2.x (Mega Evolution) from the untouched v1.8 map.

The version comes from tools/version.txt (bump it for every update: 2.1 -> 2.2 -> ...);
the output defaults to "../Pokemon Arena v<version>.w3x" and older versions are kept.

Usage (from _PokemonArena2.0_work):
  python -I tools/build_v2.py --src "../Pokemon Arena v1.8.w3x" --pkl "../PKLegendsv3.1b.w3x" --models mega_models
"""
import argparse
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ability_data  # noqa: E402
import assets  # noqa: E402
import inject  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402
import objects  # noqa: E402
import learn_data  # noqa: E402
import legend_data  # noqa: E402
import poke_data  # noqa: E402
import wild_data  # noqa: E402
from mega_data import MEGAS  # noqa: E402

SCRIPT = 'scripts\\war3map.j'
W3I = 'war3map.w3i'
OBJECT_FILES = (objects.W3U, objects.ITEM_SLK, objects.ITEM_TXT, objects.ABIL_SLK, objects.ABIL_TXT)
OLD_DESC = b'Release new ver when have 2000 times download\x00'
NEW_DESC = 'v%s: Mega Evolution! Mua Mega Stone o Mega Shop.\x00'
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(TOOLS_DIR, 'version.txt')
MAPS_DIR = os.path.dirname(os.path.dirname(TOOLS_DIR))


HASH_SIZE = 4096
KNOWN_NAMES_FILE = os.path.join(TOOLS_DIR, 'known_names_v18.txt')


def known_names_v18():
    """Real names of v1.8 files the listfile/content scan cannot find (found by brute force)."""
    with open(KNOWN_NAMES_FILE, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def current_version():
    with open(VERSION_FILE, encoding='utf-8') as f:
        return f.read().strip()


def default_output(version):
    return os.path.join(MAPS_DIR, 'Pokemon Arena v%s.w3x' % version)


@dataclass
class BuildReport:
    added: int = 0
    replaced: int = 0
    size: int = 0
    warnings: list = field(default_factory=list)


def patch_w3i(data, version):
    if OLD_DESC not in data:
        raise ValueError('w3i description not found')
    name = ('Pokemon Arena v%s\x00' % version).encode('latin-1')
    return data.replace(b'Pokemon Arena v1.8\x00', name).replace(OLD_DESC, (NEW_DESC % version).encode('latin-1'))


def build(src, pkl_path, models_dir, out, version=None):
    version = version or current_version()
    if os.path.abspath(src) == os.path.abspath(out):
        raise ValueError('refusing to overwrite the source map')
    base = mpq.MPQ(src)
    pkl = mpq.MPQ(pkl_path) if pkl_path and os.path.isfile(pkl_path) else None
    poke = assets.collect_poke(pkl, base) if pkl is not None else None
    a = assets.collect(pkl, base, models_dir, poke=poke)
    a.wild = assets.collect_wild(pkl, base) if pkl is not None else None
    a.poke = poke
    a.legends = legend_data.SPAWN_LEGENDS
    a.abilities = ability_data.ABILITIES
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    a.wild_souls = wild_data.wild_souls(w3u) if a.wild is not None else None
    a.moves = learn_data.build_plan(learn_data.hero_species(w3u))

    files = dict(a.files)
    for extra in (a.wild, poke):
        if extra is not None:
            files.update(extra.files)
    files.update(objects.apply({n: base.read(n) for n in OBJECT_FILES}, a))
    units = {o.id: o for o in w3u.custom}
    base_scale = {m.index: (units[m.base_unit].get('usca') or 1.0) if m.base_unit in units
                  else poke.scale[m.base_unit] for m in MEGAS if m.index in a.scale}
    script = base.read(SCRIPT).decode('latin-1')
    wild = inject.wild_inputs(script, w3u) if a.wild is not None else None
    import type_taverns
    rand = inject.random_pool(w3u, (list(poke_data.STARTERS) + [fid for _t, ids in type_taverns.groups() for fid in ids])
                              if poke is not None else ())
    evolved = {f.evolves_to for f in poke_data.FORMS if f.evolves_to}  # -random gives first forms only
    later = type_taverns.later_form_names()
    evolved |= {f.id for f in poke_data.FORMS if f.name in later}
    rand = [t for t in dict.fromkeys(rand) if t not in evolved]
    evo = inject.evo_inputs() if poke is not None else None
    abil = {'abilities': a.abilities, 'types': ability_data.type_abilities(w3u),
            'megas': ability_data.mega_ability_index()}
    files[SCRIPT] = inject.inject(script, a.scale, base_scale, wild, rand, version, evo, a.legends,
                                  abil, a.moves).encode('latin-1')
    files[W3I] = patch_w3i(base.read(W3I), version)

    replaced = sum(1 for n in files if base.has(n))
    known = known_names_v18()
    listfile = sorted(set(base.listfile()) | set(files) | set(mpq.discover_names(base, known)))
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=HASH_SIZE, extra_names=known)
    return BuildReport(added=len(files) - replaced, replaced=replaced, size=os.path.getsize(out),
                       warnings=list(a.warnings))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--pkl', default='')
    ap.add_argument('--models', default='mega_models')
    ap.add_argument('--version', default='')
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    version = args.version or current_version()
    out = args.out or default_output(version)
    r = build(args.src, args.pkl, args.models, out, version)
    print('Built %s (v%s): %d files added, %d replaced, %.1f MB'
          % (out, version, r.added, r.replaced, r.size / 1048576))
    for w in r.warnings:
        print('WARNING:', w)


if __name__ == '__main__':
    main()
