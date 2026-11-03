import io
import os

import pytest
from PIL import Image

import assets
import mdx
import mpq
import objdata
from conftest import PKL, V18
from mega_data import MEGAS

PKL_IDX = (0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 12) + tuple(range(16, 25))
FALLBACK_IDX = (4, 8, 13, 14, 15)


@pytest.fixture(scope='module')
def maps():
    return mpq.MPQ(PKL), mpq.MPQ(V18)


@pytest.fixture(scope='module')
def poke(maps):
    return assets.collect_poke(maps[0], maps[1])


@pytest.fixture(scope='module')
def result(maps, poke, tmp_path_factory):
    empty = tmp_path_factory.mktemp('empty_models')
    return assets.collect(maps[0], maps[1], str(empty), poke=poke)


def test_poke_assets(poke, maps):
    import poke_data
    assert len(poke.model_path) == len(poke_data.FORMS)  # v3.3: 21 + the PKLegends forms
    for f in poke_data.FORMS:
        assert poke.model_path[f.id] == 'war3mapImported\\Poke\\%s.mdl' % f.name
        assert 'war3mapImported\\Poke\\%s.mdx' % f.name in poke.files
        btn = 'ReplaceableTextures\\CommandButtons\\BTNPoke%s.blp' % f.name
        dis = 'ReplaceableTextures\\CommandButtonsDisabled\\DISBTNPoke%s.blp' % f.name
        assert poke.icon_path[f.id] == btn
        for n in (btn, dis):
            Image.open(io.BytesIO(poke.files[n])).load()
    for name, data in poke.files.items():
        assert not maps[1].has(name), name
        if name.lower().endswith('.mdx'):
            for _, tex in mdx.inspect(data)['textures']:
                if tex and not tex.lower().startswith(assets._GAME_PREFIXES) and not _missing_in_pkl(poke, tex):
                    assert tex.startswith('war3mapImported\\Poke\\') and tex in poke.files, (name, tex)


def _missing_in_pkl(res, tex):
    """Textures the PKLegends model already lacked are left as-is and reported as warnings."""
    return any(w.endswith('missing texture %s' % tex) for w in res.warnings)


def test_poke_scale_is_pklegends_scale(poke, maps):
    import poke_data
    fields = assets.pkl_species_fields(maps[0])
    for f in poke_data.FORMS:
        nh = mdx.model_height(poke.files['war3mapImported\\Poke\\%s.mdx' % f.name])
        assert poke.model_height[f.id] == nh
        assert poke.scale[f.id] == pytest.approx(fields[f.name.lower()].get('usca') or 1.0)
    assert 0.5 <= poke.scale['EN0K'] <= 3.0  # Absol must not be shrunk to the 0.2 floor


def _base_units(v18):
    f = objdata.ObjFile(v18.read('war3map.w3u'))
    return {o.id: o for o in f.custom}


def test_patch_texture_paths_keeps_size():
    a = mpq.MPQ(PKL)
    d = a.read('war3mapImported\\MegaGengar.mdx')
    p = mdx.patch_texture_paths(d, {'MegaGengar.blp': 'war3mapImported\\Mega\\MegaGengar.blp'})
    assert len(p) == len(d)
    assert [t for _, t in mdx.inspect(p)['textures']] == ['war3mapImported\\Mega\\MegaGengar.blp']


def test_all_pkl_megas_resolved(result):
    for i in PKL_IDX:
        key = MEGAS[i].key
        assert result.model_path[i] == 'war3mapImported\\Mega\\%s.mdl' % key
        assert 'war3mapImported\\Mega\\%s.mdx' % key in result.files


def test_fallbacks_use_base_model(result, maps):
    units = _base_units(maps[1])
    for i in FALLBACK_IDX:
        assert result.model_path[i] == units[MEGAS[i].base_unit].get('umdl')


def test_kid_model_imported(result):
    assert result.kid_model == 'war3mapImported\\Mega\\KidKangama.mdl'
    assert 'war3mapImported\\Mega\\KidKangama.mdx' in result.files


def test_texture_paths_are_namespaced(result):
    for name, data in result.files.items():
        if not name.lower().endswith('.mdx'):
            continue
        for _, tex in mdx.inspect(data)['textures']:
            if tex and not tex.lower().startswith(assets._GAME_PREFIXES) and not _missing_in_pkl(result, tex):
                assert tex.startswith('war3mapImported\\Mega\\'), (name, tex)
                assert tex in result.files, (name, tex)


def test_no_existing_file_overwritten(result, maps):
    for name in result.files:
        assert not maps[1].has(name), name


def test_every_mega_has_btn_and_disbtn(result):
    for m in MEGAS:
        btn = 'ReplaceableTextures\\CommandButtons\\BTN%s.blp' % m.key
        dis = 'ReplaceableTextures\\CommandButtonsDisabled\\DISBTN%s.blp' % m.key
        assert result.icon_path[m.index] == btn
        for n in (btn, dis):
            assert n in result.files, n
            Image.open(io.BytesIO(result.files[n])).load()


def test_model_height_from_vertices():
    a = mpq.MPQ(PKL)
    data = a.read('war3mapImported\\MegaGlurakX.mdx')
    h = mdx.model_height(data)
    assert h == mdx.vertex_height(data)
    assert h is not None and h > 10


def test_scale_fallback_is_base_times_1_25(result, maps):
    units = _base_units(maps[1])
    for i in FALLBACK_IDX:
        base = units[MEGAS[i].base_unit].get('usca') or 1.0
        expected = base * 1.25 if MEGAS[i].fx else base
        assert result.scale[i] == pytest.approx(expected)


def test_scale_makes_mega_about_15_percent_taller(result, maps, poke):
    units = _base_units(maps[1])
    v18 = maps[1]
    for i in PKL_IDX:
        b = MEGAS[i].base_unit
        if b in units:
            base_h = mdx.model_height(v18.read(units[b].get('umdl')[:-4] + '.mdx'))
            base_scale = units[b].get('usca') or 1.0
        else:
            base_h, base_scale = poke.model_height[b], poke.scale[b]
        mega_h = mdx.model_height(result.files['war3mapImported\\Mega\\%s.mdx' % MEGAS[i].key])
        if base_h and mega_h:
            assert mega_h * result.scale[i] == pytest.approx(base_h * base_scale * 1.15, rel=1e-3)
        assert 0.2 <= result.scale[i] <= 6.0


def test_override_dir_wins(maps, tmp_path):
    pkl = maps[0]
    (tmp_path / 'MegaRayquaza.mdx').write_bytes(pkl.read('war3mapImported\\MegaGengar.mdx'))
    (tmp_path / 'MegaGengar.blp').write_bytes(pkl.read('MegaGengar.blp'))
    r = assets.collect(pkl, maps[1], str(tmp_path))
    assert r.model_path[15] == 'war3mapImported\\Mega\\MegaRayquaza.mdl'
    assert 'war3mapImported\\Mega\\MegaGengar.blp' in r.files
    assert not any('MegaRayquaza' in w for w in r.warnings)


@pytest.fixture(scope='module')
def wild(maps):
    return assets.collect_wild(maps[0], maps[1])


def test_wild_assets_namespaced(wild, maps):
    import wild_data
    assert len(wild.model_path) == 30 and len(wild.icon_path) == 30
    for s in wild_data.SPECIES:
        mp = wild.model_path[s.index]
        assert mp == 'war3mapImported\\Wild\\%s.mdl' % s.name
        assert mp[:-4] + '.mdx' in wild.files
        assert wild.icon_path[s.index] in wild.files
        assert 0.2 <= wild.scale[s.index] <= 6.0
    for name, data in wild.files.items():
        assert not maps[1].has(name), name
        if name.lower().endswith('.mdx'):
            for _, tex in mdx.inspect(data)['textures']:
                if tex and not tex.lower().startswith(assets._GAME_PREFIXES):  # built-in game textures are fine
                    assert tex.startswith('war3mapImported\\Wild\\') and tex in wild.files, (name, tex)


def test_wild_scale_targets_height(wild):
    import wild_data
    for s in wild_data.SPECIES:
        h = mdx.model_height(wild.files['war3mapImported\\Wild\\%s.mdx' % s.name])
        if h:
            target = min(6.0, max(0.2, (100 + 10 * s.power) / h))
            assert wild.scale[s.index] == pytest.approx(target)
