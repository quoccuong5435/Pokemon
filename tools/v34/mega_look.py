"""v3.4: the 5 Megas that have no Mega model of their own (Beedrill, Kangaskhan, Mewtwo X, Mewtwo Y, Rayquaza).

Since v2.0 their Mega skin unit uses the model of the base Pokemon, so Mega Evolution hardly shows
(Kangaskhan: nothing but the Kid). No local map has Mega models for them (PKLegends 2.0 .. 3.2 searched).

- If mega_models/<key>.mdx exists (e.g. mega_models/MegaMewtwoX.mdx, textures next to it or in a sub folder,
  optional <key>_portrait.mdx), build_v34 imports it to war3mapImported\\Mega\\<key>.mdx and points the skin unit
  at it; the Mega gets the size of the other Megas (15% taller than the base form) and no tint.
- Else the Mega looks clearly different with game effects: 40% bigger, a strong colour of its own and an aura.
"""
import os
import re

import mdx
import objdata

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'mega_models')
MEGA_DIR = 'war3mapImported\\Mega\\'
AURA = 'Abilities\\\\Spells\\\\Other\\\\GeneralAuraTarget\\\\GeneralAuraTarget.mdl'  # as written in JASS
TALLER = 1.15
BIGGER = 1.4

# Mega index, key (model file name), skin unit, base unit, colour without a model
FALLBACK = [
    (4, 'MegaBeedrill', 'hM04', 'E02K', (255, 190, 40)),
    (8, 'MegaKangaskhan', 'hM08', 'E02P', (255, 175, 120)),
    (13, 'MegaMewtwoX', 'hM0D', 'E026', (110, 150, 255)),
    (14, 'MegaMewtwoY', 'hM0E', 'E026', (235, 120, 255)),
    (15, 'MegaRayquaza', 'hM0F', 'E029', (60, 255, 120)),
]


def model_file(key, models_dir=MODELS):
    p = os.path.join(models_dir, key + '.mdx')
    return p if os.path.isfile(p) else None


def _set(body, name, idx, value):
    pat = r'(    set %s\[%d\] = )[^\n]*' % (name, idx)
    if not re.search(pat, body):
        raise ValueError('Mega_InitData: no %s[%d]' % (name, idx))
    return re.sub(pat, lambda m: m.group(1) + value, body, count=1)


def _base_scale(body, idx):
    return float(re.search(r'    set Mega_BaseScale\[%d\] = ([0-9.]+)' % idx, body).group(1))


def _model_scale(base_mpq, units, base_id, key, base_scale, models_dir):
    """scale that makes the imported Mega 15% taller than its base form (same rule as the other Megas)"""
    bm = units[base_id].get('umdl') or ''
    stem = re.sub(r'\.md[lx]$', '', bm, flags=re.I)
    bh = mdx.model_height(base_mpq.read(stem + '.mdx')) if base_mpq.has(stem + '.mdx') else None
    mh = mdx.model_height(open(model_file(key, models_dir), 'rb').read())
    if bh and mh:
        return min(6.0, max(0.2, base_scale * bh * TALLER / mh))
    return base_scale * TALLER


def patch_script(script, base_mpq, units, report, models_dir=MODELS):
    """new size / colour / aura of the 5 Megas in Mega_InitData"""
    m = re.search(r'(?ms)^function Mega_InitData takes nothing returns nothing\n.*?^endfunction\n', script)
    body = m.group(0)
    for idx, key, _skin, base_id, rgb in FALLBACK:
        bs = _base_scale(body, idx)
        if model_file(key, models_dir):
            sc, rgb, fx = _model_scale(base_mpq, units, base_id, key, bs, models_dir), (255, 255, 255), '""'
            report.append('%s: model mega_models/%s.mdx, scale %.3f' % (key, key, sc))
        else:
            sc, fx = bs * BIGGER, '"%s"' % AURA
            report.append('%s: no model, bigger x%.1f + colour %s + aura' % (key, BIGGER, rgb))
        body = _set(body, 'Mega_Scale', idx, '%.3f' % sc)
        body = _set(body, 'Mega_Fx', idx, fx)
        for name, v in zip(('Mega_R', 'Mega_G', 'Mega_B'), rgb):
            body = _set(body, name, idx, str(v))
    return script[:m.start()] + body + script[m.end():]


class _Folder:
    def __init__(self, root):
        self.root = root

    def get(self, name):
        p = os.path.join(self.root, name.replace('\\', os.sep))
        return open(p, 'rb').read() if os.path.isfile(p) else None

    def texture(self, path):
        base = path.replace('/', '\\').split('\\')[-1]
        for cand in (path, base):
            d = self.get(cand)
            if d is not None:
                return d
        for dirpath, _dirs, files in os.walk(self.root):  # textures in a sub folder of mega_models
            for f in files:
                if f.lower() == base.lower():
                    return open(os.path.join(dirpath, f), 'rb').read()
        return None


def map_files(w3u, models_dir=MODELS):
    """(files to add, warnings) for the Megas with a model in mega_models; w3u (objdata.ObjFile) is patched in place"""
    files, warns = {}, []
    src = _Folder(models_dir)
    units = {o.id: o for o in w3u.custom}
    for _idx, key, skin, _base, _rgb in FALLBACK:
        path = model_file(key, models_dir)
        if not path:
            continue
        for stem in (key, key + '_portrait'):
            data = src.get(stem + '.mdx')
            if data is None:
                continue
            mapping = {}
            for _, tex in mdx.inspect(data)['textures']:
                if not tex or tex in mapping:
                    continue
                tdata = src.texture(tex)
                if tdata is None:
                    if not tex.lower().startswith(('textures\\', 'units\\', 'replaceabletextures\\', 'abilities\\')):
                        warns.append('%s: texture %s not found in mega_models' % (stem, tex))
                    continue
                new = MEGA_DIR + key + '_' + tex.replace('/', '\\').split('\\')[-1]
                mapping[tex] = new
                files[new] = tdata
            files[MEGA_DIR + stem + '.mdx'] = mdx.patch_texture_paths(data, mapping)
        units[skin].set('umdl', objdata.T_STRING, MEGA_DIR + key + '.mdl')
    return files, warns
