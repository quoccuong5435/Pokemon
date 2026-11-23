"""MDX files made by code (glb_to_mdx.py) must be structurally sound: a bad one crashes WC3 while loading the map (4.3a)."""
import os
import struct
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import fix_glb_mdx  # noqa: E402
import mdx_check  # noqa: E402

MDX_DIR = os.path.join(WORK, 'imports', 'pokemon_3d_mdx')
GLB_DIR = os.path.join(os.path.dirname(WORK), 'imports', 'pokemon_3d_all')


def _atch_first_size(b):
    for tag, data in fix_glb_mdx._chunks(b):
        if tag == b'ATCH':
            return struct.unpack_from('<I', data, 0)[0]
    return None


def test_converter_writes_sized_attachments_and_no_global_sequence():
    if not os.path.isfile(os.path.join(GLB_DIR, '21.glb')):
        pytest.skip('glb sources not here')
    import glb_to_mdx
    with open(os.path.join(GLB_DIR, '21.glb'), 'rb') as fh:
        mdx, _tex = glb_to_mdx.convert_glb_to_mdx(fh.read(), model_name='Pk_21', tex_path_prefix='PkFx\\G14\\t\\21')
    assert _atch_first_size(mdx) == 364
    assert mdx_check.check(mdx) == []
    assert fix_glb_mdx.fix(mdx) is None  # nothing left to repair


def test_fix_repairs_the_old_layout():
    if not os.path.isdir(MDX_DIR):
        pytest.skip('converted models not here')
    old_dir = os.path.join(WORK, 'imports', 'pokemon_3d_mdx_backup_before_atch_fix')
    if not os.path.isfile(os.path.join(old_dir, '21.mdx')):
        pytest.skip('old models not here')
    with open(os.path.join(old_dir, '21.mdx'), 'rb') as fh:
        old = fh.read()
    assert _atch_first_size(old) == 96 and mdx_check.check(old)
    new = fix_glb_mdx.fix(old)
    assert _atch_first_size(new) == 364 and mdx_check.check(new) == []


def _verts(b):
    import numpy as np
    out = []
    for tag, data in fix_glb_mdx._chunks(b):
        if tag != b'GEOS':
            continue
        q = 0
        while q < len(data):
            gsize = struct.unpack_from('<I', data, q)[0]
            n = struct.unpack_from('<I', data, q + 8)[0]
            out.append(np.array(struct.unpack_from('<%df' % (n * 3), data, q + 12)).reshape(-1, 3))
            q += gsize
    return np.concatenate(out)


def test_gen14_models_have_their_target_size_and_stand_on_the_ground():
    # 4.3b: raw sizes went from 17 to 34564 (glTF node scale ignored), Seviper 229x its target
    if not os.path.isdir(GLB_DIR):
        pytest.skip('glb sources not here')
    import g14_reconvert
    import model_size_check
    heights = g14_reconvert.heights_by_dex()
    wrong = []
    for d in g14_reconvert.used_dex():
        with open(os.path.join(MDX_DIR, '%d.mdx' % d), 'rb') as fh:
            v = _verts(fh.read())
        lo, hi = v.min(0), v.max(0)
        size = max(hi[2] - lo[2], 0.4 * max(hi[0] - lo[0], hi[1] - lo[1]))
        target = model_size_check.target_size(heights[d])
        if abs(size - target) > 0.02 * target or abs(lo[2]) > 0.5:
            wrong.append((d, round(size), round(target), round(lo[2], 1)))
    assert not wrong, wrong[:10]


def test_gen14_scale_is_one_except_the_users_numbers():
    import gen14_expansion
    got = {e['dex']: e['scale'] for e in gen14_expansion.load_species_entries() if e['src'] == 'LOCAL_3D'}
    assert got[232] == 0.95 and got[241] == 0.95  # Donphan, Miltank (GEMINI.md section 13)
    assert {s for d, s in got.items() if d not in (232, 241)} == {1.0}


def test_every_converted_model_is_sound():
    if not os.path.isdir(MDX_DIR):
        pytest.skip('converted models not here')
    bad = {}
    for f in os.listdir(MDX_DIR):
        if f.endswith('.mdx'):
            with open(os.path.join(MDX_DIR, f), 'rb') as fh:
                errs = mdx_check.check(fh.read())
            if errs:
                bad[f] = errs[0]
    assert not bad, list(bad.items())[:5]


def _synthetic_glb(positions, indices):
    """A minimal glTF 2.0 binary: one mesh, POSITION + indices, no textures, no skin."""
    import json
    import numpy as np
    pos = np.array(positions, dtype='<f4')
    idx = np.array(indices, dtype='<u2')
    body = pos.tobytes() + idx.tobytes()
    body += b'\0' * (-len(body) % 4)
    meta = {
        'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
        'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'indices': 1}]}],
        'buffers': [{'byteLength': len(body)}],
        'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': pos.nbytes},
                        {'buffer': 0, 'byteOffset': pos.nbytes, 'byteLength': idx.nbytes}],
        'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3'},
                      {'bufferView': 1, 'componentType': 5123, 'count': len(idx), 'type': 'SCALAR'}],
    }
    js = json.dumps(meta).encode()
    js += b' ' * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(body)
    return (struct.pack('<III', 0x46546C67, 2, total) + struct.pack('<II', len(js), 0x4E4F534A) + js
            + struct.pack('<II', len(body), 0x004E4942) + body)


def _convert_arrow():
    """glTF convention (what the Pokemon .glb files use): +Y up, the model FACES +Z, so its left side is +X.
    Vertices: 0 centre, 1 left side (+X), 2 top (+Y), 3 nose (+Z)."""
    import glb_to_mdx
    glb = _synthetic_glb([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0.5, 3)], [0, 1, 2, 0, 2, 3, 1, 3, 2, 0, 3, 1])
    mdx, _tex = glb_to_mdx.convert_glb_to_mdx(glb, model_name='Pk_arrow', tex_path_prefix='PkFx\\Forms\\t\\arrow')
    return mdx


def test_converted_model_faces_plus_x_like_every_wc3_unit():
    # WC3: facing angle 0 = +X, +Z up, left = +Y. 4.3c / NPA 1.0 mapped glTF (x, y, z) -> (x, -z, y): the nose ended
    # on -Y, so every converted Pokemon (G14 Gen 1-4, the 92 form models) walked sideways.
    v = _verts(_convert_arrow())
    centre, left, top, nose = v
    assert nose[0] > centre[0] + 50, 'nose must point to +X (forward), got %s' % (nose - centre)
    assert abs(nose[1] - centre[1]) < 1e-3, 'nose must not drift sideways'
    assert left[1] > centre[1] + 50, 'the left side (+X in glTF) must end on +Y, got %s' % (left - centre)
    assert top[2] > centre[2], 'up stays up'
    assert v[:, 2].min() >= -1e-3, 'model stands on the ground'


def test_per_model_yaw_override_turns_a_model_whose_source_faces_another_way(monkeypatch):
    # Relicanth (#369): its .glb has the head along +Y after the standard mapping. FACING_FIX_DEG (by model name)
    # turns such a model about the up axis; +90 turns +X into +Y.
    import glb_to_mdx
    glb = _synthetic_glb([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0.5, 3)], [0, 1, 2, 0, 2, 3, 1, 3, 2, 0, 3, 1])
    monkeypatch.setitem(glb_to_mdx.FACING_FIX_DEG, 'Pk_arrow_yaw', 90.0)
    mdx, _tex = glb_to_mdx.convert_glb_to_mdx(glb, model_name='Pk_arrow_yaw', tex_path_prefix='PkFx\\Forms\\t\\arrow')
    centre, left, top, nose = _verts(mdx)
    assert nose[1] > centre[1] + 50 and abs(nose[0] - centre[0]) < 1e-3, 'nose must now point to +Y'
    assert left[0] < centre[0] - 50, 'the left side (+Y) turns to -X'
    assert glb_to_mdx.FACING_FIX_DEG.get('Pk_369') is not None, 'Relicanth keeps its fix'


FORMS_GLB_DIR = os.path.join(os.path.dirname(WORK), 'imports', 'pokemon_3d_forms')


@pytest.mark.parametrize('src,name', [
    ('pokemon_3d_all/162.glb', 'Pk_162'),            # Furret
    ('pokemon_3d_all/262.glb', 'Pk_262'),            # Mightyena
    ('pokemon_3d_all/264.glb', 'Pk_264'),            # Linoone
    ('pokemon_3d_all/369.glb', 'Pk_369'),            # Relicanth: needs FACING_FIX_DEG
    ('pokemon_3d_forms/linoone-galar.glb', 'Pk_linoone-galar'),
    ('pokemon_3d_forms/persian-alola.glb', 'Pk_persian-alola'),
    ('pokemon_3d_forms/arcanine-hisui.glb', 'Pk_arcanine-hisui'),
])
def test_long_bodied_real_models_lie_along_x(src, name):
    # a walking quadruped / fish is longer than it is wide: facing +X means its long axis is X (it was Y: sideways)
    path = os.path.join(os.path.dirname(WORK), 'imports', *src.split('/'))
    if not os.path.isfile(path):
        pytest.skip('glb source not here')
    import glb_to_mdx
    with open(path, 'rb') as fh:
        mdx, _tex = glb_to_mdx.convert_glb_to_mdx(fh.read(), model_name=name, tex_path_prefix='PkFx\\Forms\\t\\x',
                                                  target_size=100.0)
    v = _verts(mdx)
    lo, hi = v.min(0), v.max(0)
    assert (hi[0] - lo[0]) > (hi[1] - lo[1]), '%s: x extent %.0f, y extent %.0f (sideways)' % (name, hi[0] - lo[0], hi[1] - lo[1])


def test_attack_lunges_forward_along_plus_x():
    mdx = _convert_arrow()
    at = mdx.index(b'KGTR')
    n, _interp, _gseq = struct.unpack_from('<IIi', mdx, at + 4)
    keys = [struct.unpack_from('<I3f', mdx, at + 16 + 16 * k) for k in range(n)]
    lunge = next(k for k in keys if k[0] == 3000)
    assert lunge[1] > 1.0 and lunge[2] == 0.0, 'the attack lunge must go forward (+X), got %s' % (lunge,)
