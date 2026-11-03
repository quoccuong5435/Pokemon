"""Collect Mega models / textures / icons to import into the v2.0 map.

Resolution per Mega: mega_models/<key>.mdx  >  PKLegends model  >  fallback (base unit model, nothing imported).
"""
import io
import os
import re
from dataclasses import dataclass, field

from PIL import Image

import mdx
import objdata
from mega_data import FALLBACK_SCALE, KID_MODEL_PKL, MEGAS

MEGA_TALLER = 1.15  # Mega model ends up 15% taller than the base form

MEGA_DIR = 'war3mapImported\\Mega\\'
BTN_DIR = 'ReplaceableTextures\\CommandButtons\\'
DIS_DIR = 'ReplaceableTextures\\CommandButtonsDisabled\\'
_GAME_PREFIXES = ('textures\\', 'units\\', 'abilities\\', 'replaceabletextures\\', 'doodads\\',
                  'environment\\', 'objects\\', 'ui\\', 'buildings\\', 'sharedmodels\\')


@dataclass
class Assets:
    files: dict = field(default_factory=dict)
    model_path: dict = field(default_factory=dict)
    icon_path: dict = field(default_factory=dict)
    kid_model: str = ''
    scale: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


class _Source:
    """A place files can come from: an MPQ (PKL) or a folder (mega_models)."""

    def __init__(self, pkl=None, folder=None):
        self.pkl = pkl
        self.folder = folder

    def get(self, name):
        if self.folder:
            p = os.path.join(self.folder, name.replace('\\', os.sep))
            if os.path.isfile(p):
                with open(p, 'rb') as f:
                    return f.read()
            return None
        if self.pkl is not None and self.pkl.has(name):
            return self.pkl.read(name)
        return None

    def texture(self, path):
        base = path.replace('/', '\\').split('\\')[-1]
        for cand in (path, base, 'war3mapImported\\' + base):
            d = self.get(cand)
            if d is not None:
                return d
        return None


def _disabled_icon(blp):
    im = Image.open(io.BytesIO(blp)).convert('L').point(lambda v: int(v * 0.6)).convert('RGB')
    out = io.BytesIO()
    im.quantize(256).save(out, format='BLP', blp_version='BLP1')
    return out.getvalue()


def _import_model(res, src, data, dest_stem, label, dest_dir=MEGA_DIR):
    """Namespace the model's textures under dest_dir and add model + textures to res.files."""
    mapping = {}
    for _, tex in mdx.inspect(data)['textures']:
        if not tex or tex in mapping:
            continue
        base = tex.replace('/', '\\').split('\\')[-1]
        tdata = src.texture(tex)
        if tdata is None:
            if tex.lower().startswith(_GAME_PREFIXES):
                continue  # built-in game texture
            res.warnings.append('%s: missing texture %s' % (label, tex))
            continue
        new = dest_dir + base
        if res.files.get(new, tdata) != tdata:  # same name, other content (e.g. "Eye.blp")
            new = dest_dir + dest_stem + '_' + base
        mapping[tex] = new
        res.files[new] = tdata
    patched = mdx.patch_texture_paths(data, mapping)
    extra = [m.group(0).decode('latin-1') for m in
             re.finditer(rb'[A-Za-z0-9_\\/ .\-]{4,259}\.(?:mdl|mdx)', patched, re.I)]
    if extra:
        res.warnings.append('%s: model references other files %s' % (label, extra))
    res.files[dest_dir + dest_stem + '.mdx'] = patched


def _pkl_portrait(pkl, stem):
    for suffix in ('_portrait', '_Portrait'):
        n = 'war3mapImported\\' + stem + suffix + '.mdx'
        if pkl is not None and pkl.has(n):
            return pkl.read(n)
    return None


def _pkl_model(pkl, stem):
    if pkl is None or not stem:
        return None
    for n in ('war3mapImported\\' + stem + '.mdx', stem + '.mdx'):
        if pkl.has(n):
            return pkl.read(n)
    return None


class _BaseUnit:
    """What a Mega needs from its base Pokemon: model path/bytes, scale, icon (v1.8 unit or new Pokemon)."""

    def __init__(self, umdl, model, usca, icon):
        self.umdl, self.model, self.usca, self.icon = umdl, model, usca, icon

    def get(self, field):
        return {'umdl': self.umdl, 'usca': self.usca}.get(field)


def _base_unit(m, units, base, poke):
    if m.base_unit in units:
        bu = units[m.base_unit]
        mdl = bu.get('umdl')
        model = base.read(mdl[:-4] + '.mdx') if base.has(mdl[:-4] + '.mdx') else None
        return _BaseUnit(mdl, model, bu.get('usca') or 1.0, base.read(bu.get('uico')))
    path = poke.model_path[m.base_unit]
    return _BaseUnit(path, poke.files[path[:-4] + '.mdx'], poke.scale[m.base_unit],
                     poke.files[poke.icon_path[m.base_unit]])


def collect(pkl, base, override_dir, poke=None):
    res = Assets()
    units = {o.id: o for o in objdata.ObjFile(base.read('war3map.w3u')).custom}
    pkl_src = _Source(pkl=pkl)
    over_src = _Source(folder=override_dir) if override_dir and os.path.isdir(override_dir) else None

    for m in MEGAS:
        if m.base_unit not in units and poke is None:
            continue  # Megas of new Pokemon need the new Pokemon assets
        bu = _base_unit(m, units, base, poke)
        # ---- model
        over = over_src.get(m.key + '.mdx') if over_src else None
        if over is not None:
            _import_model(res, over_src, over, m.key, m.key)
            port = over_src.get(m.key + '_portrait.mdx')
            if port is not None:
                _import_model(res, over_src, port, m.key + '_portrait', m.key + ' portrait')
            res.model_path[m.index] = MEGA_DIR + m.key + '.mdl'
        elif _pkl_model(pkl, m.pkl_model) is not None:
            _import_model(res, pkl_src, _pkl_model(pkl, m.pkl_model), m.key, m.key)
            port = _pkl_portrait(pkl, m.pkl_model)
            if port is not None:
                _import_model(res, pkl_src, port, m.key + '_portrait', m.key + ' portrait')
            res.model_path[m.index] = MEGA_DIR + m.key + '.mdl'
        else:
            res.model_path[m.index] = bu.get('umdl')
            if m.pkl_model is not None or m.fx:
                res.warnings.append('%s: no Mega model, using fallback (%s)' % (m.key, bu.get('umdl')))
        # ---- scale
        base_scale = bu.usca
        mega_file = res.files.get(MEGA_DIR + m.key + '.mdx')
        if mega_file is None:
            res.scale[m.index] = base_scale * (FALLBACK_SCALE if m.fx else 1.0)
        else:
            bh = mdx.model_height(bu.model) if bu.model else None
            mh = mdx.model_height(mega_file)
            if bh and mh:
                res.scale[m.index] = min(6.0, max(0.2, base_scale * bh * MEGA_TALLER / mh))
            else:
                res.scale[m.index] = base_scale
                res.warnings.append('%s: model height unknown, using base scale' % m.key)
        # ---- icon
        btn = dis = None
        if over_src:
            btn = over_src.get('BTN' + m.key + '.blp')
            dis = over_src.get('DISBTN' + m.key + '.blp')
        if btn is None and m.pkl_icon and pkl is not None:
            btn = pkl_src.get(BTN_DIR + m.pkl_icon)
            dis = pkl_src.get(DIS_DIR + 'DIS' + m.pkl_icon)
        if btn is None:
            btn = bu.icon
            dis = None
        if dis is None:
            dis = _disabled_icon(btn)
        res.files[BTN_DIR + 'BTN' + m.key + '.blp'] = btn
        res.files[DIS_DIR + 'DISBTN' + m.key + '.blp'] = dis
        res.icon_path[m.index] = BTN_DIR + 'BTN' + m.key + '.blp'

    # ---- Kangaskhan Kid
    kid = None
    if over_src:
        kid = over_src.get('KidKangaskhan.mdx')
        if kid is not None:
            _import_model(res, over_src, kid, 'KidKangama', 'KidKangaskhan')
    if kid is None and pkl is not None and pkl.has('war3mapImported\\' + KID_MODEL_PKL + '.mdx'):
        _import_model(res, pkl_src, pkl.read('war3mapImported\\' + KID_MODEL_PKL + '.mdx'), 'KidKangama', 'Kid')
        kid = True
    if kid is None:
        res.warnings.append('Kid: no model, Kid uses Kangaskhan base model')
        res.kid_model = units['E02P'].get('umdl')
    else:
        res.kid_model = MEGA_DIR + 'KidKangama.mdl'
    # v3.2: the type icons of the move buttons (PKLegends): fire, water, grass... (BTNPkmn<Type>)
    for stem in ('BTNPkmnFire', 'BTNPkmnWater', 'BTNPkmnGrass', 'BTNPkmnElectr', 'BTNPkmnPsy', 'BTNPkmnRock',
                 'BTNPkmnDragon', 'BTNPkmnNormal'):
        for folder, prefix in (('ReplaceableTextures\\CommandButtons\\', ''),
                               ('ReplaceableTextures\\CommandButtonsDisabled\\', 'DIS')):
            name = folder + prefix + stem + '.blp'
            if pkl is not None and pkl.has(name):
                res.files[name] = pkl.read(name)
    # v3.2: 10 type icons made by tools/make_type_icons.py (PKLegends has no icon for these types)
    made = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'type_icons')
    for fn in sorted(os.listdir(made)):
        folder = 'ReplaceableTextures\\CommandButtonsDisabled\\' if fn.startswith('DIS') else 'ReplaceableTextures\\CommandButtons\\'
        res.files[folder + fn] = open(os.path.join(made, fn), 'rb').read()
    # v3.3: Soul icons (species sprite on a tile) made by analysis/make_soul_icons.py
    souls = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'soul_icons')
    for fn in sorted(os.listdir(souls)) if os.path.isdir(souls) else ():
        folder = 'ReplaceableTextures\\CommandButtonsDisabled\\' if fn.startswith('DIS') else 'ReplaceableTextures\\CommandButtons\\'
        res.files[folder + fn] = open(os.path.join(souls, fn), 'rb').read()
    return res


# ------------------------------------------------------------------ wild species (PKLegends models)
WILD_DIR = 'war3mapImported\\Wild\\'


def pkl_species_index(pkl):
    """English species name -> (model path, icon path) from PKLegends units named like 'Snorlax (Lvl.50)'."""
    return {k: (d['umdl'], d.get('uico')) for k, d in pkl_species_fields(pkl).items()}


def pkl_species_fields(pkl):
    """English species name -> resolved unit fields (umdl, uico, usca...) of the first PKLegends unit of that species."""
    cached = getattr(pkl, '_species_fields', None)
    if cached is not None:
        return cached
    wts = {}
    if pkl.has('war3map.wts'):
        text = pkl.read('war3map.wts').decode('utf-8', 'replace')
        for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', text, re.S):
            wts[int(m.group(1))] = m.group(2)
    fields = {}
    for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
        if pkl.has(fn):
            for o in objdata.ObjFile(pkl.read(fn)).all():
                d = fields.setdefault(o.id, {})
                for mod in o.mods:
                    v = mod.value
                    if isinstance(v, str) and v.startswith('TRIGSTR_'):
                        v = wts.get(int(v[8:].split()[0] or 0), v)
                    d.setdefault(mod.field, v)
    index = {}
    for d in fields.values():
        m = re.match(r'^([A-Za-z.\' -]+?)\s*\([Ll]vl\.?\s*\d+\)', str(d.get('unam') or ''))
        mdl = d.get('umdl') or ''
        if m and mdl and pkl.has(mdl[:-4] + '.mdx'):
            index.setdefault(m.group(1).strip().lower(), d)
    pkl._species_fields = index
    return index


def collect_wild(pkl, base):
    """Models/textures/icons for the 30 wild species; scale so the model is about 100 + 10*power tall."""
    import wild_data
    res = Assets()
    index = pkl_species_index(pkl)
    src = _Source(pkl=pkl)
    for s in wild_data.SPECIES:
        mdl, ico = index[s.name.lower()]
        data = pkl.read(mdl[:-4] + '.mdx')
        _import_model(res, src, data, s.name, s.name, dest_dir=WILD_DIR)
        res.model_path[s.index] = WILD_DIR + s.name + '.mdl'
        icon = BTN_DIR + 'BTNWild' + s.name + '.blp'
        res.files[icon] = pkl.read(ico) if ico and pkl.has(ico) else base.read('BTNPikachu (64 x 64).blp')
        res.icon_path[s.index] = icon
        h = mdx.model_height(data)
        res.scale[s.index] = min(6.0, max(0.2, (100 + 10 * s.power) / h)) if h else 1.0
    return res


# ------------------------------------------------------------------ new playable Pokemon (PKLegends models)
@dataclass
class PokeAssets:
    files: dict = field(default_factory=dict)
    model_path: dict = field(default_factory=dict)    # form id -> 'war3mapImported\Poke\<Name>.mdl'
    icon_path: dict = field(default_factory=dict)
    scale: dict = field(default_factory=dict)
    model_height: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


def collect_poke(pkl, base):
    """Models/portraits/icons of the 21 new Pokemon, with the scale PKLegends uses for them."""
    import poke_data
    res = PokeAssets()
    units = {o.id: o for o in objdata.ObjFile(base.read('war3map.w3u')).custom}
    index = pkl_species_index(pkl)
    fields = pkl_species_fields(pkl)
    src = _Source(pkl=pkl)
    for f in poke_data.FORMS:
        mdl, ico = index[f.name.lower()]
        stem = mdl.replace('/', '\\').split('\\')[-1][:-4]
        data = pkl.read(mdl[:-4] + '.mdx')
        _import_model(res, src, data, f.name, f.name, dest_dir=poke_data.POKE_DIR)
        port = _pkl_portrait(pkl, stem)
        if port is not None:
            _import_model(res, src, port, f.name + '_portrait', f.name + ' portrait', dest_dir=poke_data.POKE_DIR)
        res.model_path[f.id] = poke_data.POKE_DIR + f.name + '.mdl'
        btn = pkl.read(ico) if ico and pkl.has(ico) else base.read(units[f.template].get('uico'))
        dis_src = DIS_DIR + 'DIS' + (ico or '').split('\\')[-1]
        dis = pkl.read(dis_src) if ico and pkl.has(dis_src) else _disabled_icon(btn)
        res.files[BTN_DIR + 'BTNPoke' + f.name + '.blp'] = btn
        res.files[DIS_DIR + 'DISBTNPoke' + f.name + '.blp'] = dis
        res.icon_path[f.id] = BTN_DIR + 'BTNPoke' + f.name + '.blp'
        # PKLegends tuned each model's scale and uses the same size convention as Arena; bind-pose heights are
        # unreliable for some models (e.g. Umbreon's), so keep PKLegends' scale.
        res.model_height[f.id] = mdx.model_height(data)
        res.scale[f.id] = fields[f.name.lower()].get('usca') or 1.0
    return res
