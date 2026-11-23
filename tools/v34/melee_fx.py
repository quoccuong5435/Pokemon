"""v3.4.3, proposal 6 (docs/v3.4/6-de-xuat-hieu-ung-chieu.md): effects of the moves from PKLegends 3.2 models.

  Cận chiến (106)   range 150, no missile, the model on the target          (Targetart)
  Đạn (81)          the projectile is the model of the table               (Missileart)
  Diện rộng (66)    the model on the target area                            (Targetart)
  Hiệu ứng riêng (10) the model as projectile                               (Missileart)
Giữ nguyên (56) is not touched.

Each model is copied with its textures into its own folder war3mapImported\\V34\\FX\\<model>\\, so two models with
the same texture name cannot overwrite each other.

plan(script) -> (ability row overrides, ability text sets, imported files) for build_v34.py
"""
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import learn_data as ld  # noqa: E402
import mpq  # noqa: E402

DOC = os.path.join(WORK, 'docs', 'v3.4', '6-de-xuat-hieu-ung-chieu.md')
PKL = os.path.join(os.path.dirname(WORK), 'PKLegendsv3.2.w3x')
MELEE_RANGE = '150'
FX_DIR = 'war3mapImported\\V34\\FX\\'
TEX_REC = 268  # one TEXS record of an MDX file: replaceable id (4), path (260), flags (4)


def _rows():
    """(move name, kind, model) of the proposal table; kind is melee / ranged / area / special"""
    out = []
    for line in open(DOC, encoding='utf-8'):
        if not re.match(r'^\| \d+ \|', line):
            continue
        cells = [c.strip() for c in line.split('|')]
        p = cells[7]
        if p.startswith('Giữ'):
            continue
        if p.startswith('Cận chiến'):
            kind = 'melee'
        elif p.startswith('Đạn'):
            kind = 'ranged'
        elif p.startswith('Diện rộng'):
            kind = 'area'
        elif p.startswith('Hiệu ứng riêng'):
            kind = 'special'
        else:
            raise SystemExit('unknown proposal in the table: %s' % p[:40])
        m = re.search(r':\s*(.+?)(?: trên mục tiêu)?\s*$', p)
        if not m:
            raise SystemExit('no model in the table row of %s' % cells[2])
        model = m.group(1).strip()
        # v3.4.5: AnimatedBash is a looping ground ring (Stand 2.4 s, Death 3.3 s) that stayed on the battlefield;
        # the punch moves use slash-luc (one second)
        if model == 'AnimatedBash':
            model = 'slash-luc'
        out.append((cells[2], kind, model))
    return out


def mdx_textures(data):
    """texture file names of an MDX model (TEXS chunk)"""
    if data[:4] != b'MDLX':
        return []
    names = []
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4]
        size = struct.unpack_from('<I', data, p + 4)[0]
        if tag == b'TEXS':
            for i in range(size // TEX_REC):
                rec = data[p + 8 + i * TEX_REC:p + 8 + (i + 1) * TEX_REC]
                path = rec[4:264].split(b'\0')[0].decode('latin-1')
                if path:
                    names.append(path)
        p += 8 + size
    return names


def _pkl_file(pkl, name):
    """bytes of a file of the PKL map, None if missing"""
    return pkl.read(name) if pkl.has(name) else None


# v3.4.7 (the user asked for DotA-style effects): the projectile and the area effect of a move are taken from the
# DotA map by the type of the move. Type (T_* index) -> (projectile model, area model). Only ranged / special /
# area moves change; melee moves keep their PKLegends model. The choice is by name, not by looking at the effect:
# check it in game and change the table if an effect does not fit.
DOTA_PATH = os.path.join(os.path.dirname(WORK), 'DotA_fix_01.w3x')
DOTA_BY_TYPE = {
    0: ('splinterblastmainprojectile_pe', 'icewindgroundfx'),      # Bug
    1: ('chaosbolt', 'darklightningnova'),                          # Dark
    2: ('sunfiremissile', 'firenova2'),                             # Dragon
    3: ('forkedlightningorange', 'staticstorm_9'),                  # Electric
    4: ('orbfirex', 'radiancehands'),                               # Fairy
    5: ('mortalstrikecaster', 'explosion'),                         # Fighting
    6: ('fireblast', 'firenova2'),                                  # Fire
    7: ('icywind', 'outlandstorm'),                                 # Flying
    8: ('soulmissile', 'darklightningnova'),                        # Ghost
    9: ('sunfiremissile', 'flamedash_ground'),                      # Grass
    10: ('splinterblastmainprojectile_pe', 'thunderstorm_groundeffect'),  # Ground
    11: ('icebolt', 'icenova'),                                     # Ice
    12: ('shockwavemissilepurple', 'superdarkflash'),               # Normal
    13: ('bloodbreathdamage', 'bloodrite'),                         # Poison
    14: ('void', 'willthealmighty-void5'),                          # Psychic
    15: ('splinterblastsubprojectile_pe', 'flamestriketarget_nosound'),  # Rock
    16: ('orbfirex', 'newsoularmor'),                               # Steel
    17: ('blinkstrike', 'superdarkflash'),                          # Water
}
DOTA_NAMES = {'%s' % n for pair in DOTA_BY_TYPE.values() for n in pair}


def _dota_map():
    return mpq.MPQ(DOTA_PATH)


def _model_source(model, pkl, dota):
    """the archive a model is copied from: the DotA map for its effects, else PKLegends 3.2"""
    return dota if model in DOTA_NAMES else pkl


def model_dir(model):
    return FX_DIR + model + '\\'


def model_path(model):
    return model_dir(model) + model + '.mdx'


def model_files(models):
    """{map path: bytes} of the models and their textures, copied from PKLegends 3.2"""
    pkl = mpq.MPQ(PKL)
    dota = _dota_map()
    files, missing, missing_tex = {}, [], []
    for model in sorted(set(models)):
        src = _model_source(model, pkl, dota)
        data = _pkl_file(src, 'war3mapImported\\%s.mdx' % model)
        if data is None:
            missing.append(model)
            continue
        files[model_path(model)] = data
        for tex in mdx_textures(data):
            name = tex.replace('/', '\\')
            tdata = _pkl_file(src, 'war3mapImported\\' + name)
            if tdata is None:  # some textures sit at the root of the map
                tdata = _pkl_file(src, name)
            if tdata is None:
                # not in the PKL map: a texture of the game itself (UI\..., Textures\...) or a missing one
                missing_tex.append('%s: %s' % (model, tex))
                continue
            files[model_dir(model) + name] = tdata
    if missing:
        raise SystemExit('models not in PKLegends 3.2: %s' % missing)
    for line in missing_tex:
        print('melee_fx: texture not copied (game texture or missing):', line)
    return files


def move_index(script):
    """{move name: index} from the Mv_Label lines of the script"""
    out = {}
    for i, lab in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        out[lab.split(' (')[0]] = int(i)
    return out


def plan(script):
    """(slk overrides [(ability id, {column: value})], text sets [(ability id, [(key, value)])], files)"""
    rows = _rows()
    index = move_index(script)
    missing = [name for name, _k, _m in rows if name not in index]
    if missing:
        raise SystemExit('moves not found in the script: %s' % missing[:5])
    types = {int(m): int(t) for m, t in re.findall(r'set Mv_Type\[(\d+)\] = (\d+)', script)}
    slk_over, txt_sets = [], []
    chosen = []
    for name, kind, model in rows:
        # v3.4.7: DotA effect for ranged / special (projectile) and area moves, by the type of the move
        ty = types.get(index[name])
        if ty is not None and kind in ('ranged', 'special', 'area') and ty in DOTA_BY_TYPE:
            model = DOTA_BY_TYPE[ty][1] if kind == 'area' else DOTA_BY_TYPE[ty][0]
        chosen.append(model)
        path = model_path(model)
        for slot in range(4):
            aid = ld.ability_id(slot, index[name])
            if kind == 'melee':
                slk_over.append((aid, {'Rng1': MELEE_RANGE}))
                txt_sets.append((aid, [('Missileart', ''), ('Targetart', path)]))
            elif kind == 'area':
                txt_sets.append((aid, [('Targetart', path)]))
            else:  # ranged / special: the model is the projectile
                txt_sets.append((aid, [('Missileart', path)]))
    return slk_over, txt_sets, model_files(chosen)
