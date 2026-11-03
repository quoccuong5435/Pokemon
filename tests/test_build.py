import hashlib
import os
import re
import subprocess

import pytest

import build_v2
import mpq
import objdata
import slk
from conftest import PKL, V18
from mega_data import MEGAS


def _sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


@pytest.fixture(scope='module')
def out(tmp_path_factory):
    before = _sha(V18)
    d = tmp_path_factory.mktemp('build')
    path = str(d / 'Pokemon Arena v2.8.w3x')
    report = build_v2.build(V18, PKL, str(d / 'no_models'), path, version='2.8')
    return path, report, before


def test_version_file_and_default_output():
    ver = build_v2.current_version()
    assert re.fullmatch(r'\d+\.\d+(\.\d+)?', ver)
    assert build_v2.default_output(ver).endswith('Pokemon Arena v%s.w3x' % ver)


def test_patch_w3i_any_version():
    w3i = mpq.MPQ(V18).read('war3map.w3i')
    new = build_v2.patch_w3i(w3i, '2.10')
    assert b'Pokemon Arena v2.10\x00' in new and b'v2.10: ' in new and b'v1.8' not in new


def _exists(arc, v18, path):
    if not path:
        return False
    cands = [path]
    if path.lower().endswith('.mdl'):
        cands.append(path[:-4] + '.mdx')
    return any(arc.has(c) for c in cands)


def test_output_opens_and_v18_untouched(out):
    path, report, before = out
    arc = mpq.MPQ(path)
    assert arc.has('scripts\\war3map.j')
    assert _sha(V18) == before
    assert report.added >= 70
    assert report.size == len(open(path, 'rb').read())


def test_all_references_exist(out):
    path, _, _ = out
    arc = mpq.MPQ(path)
    v18 = mpq.MPQ(V18)
    units = objdata.ObjFile(arc.read('war3map.w3u'))
    for m in MEGAS:
        o = units.find(m.skin_id)
        assert _exists(arc, v18, o.get('umdl')), o.get('umdl')
        assert _exists(arc, v18, o.get('uico')), o.get('uico')
    assert _exists(arc, v18, units.find('hMK0').get('umdl'))
    for name in ('Units\\ItemFunc.txt', 'Units\\CampaignAbilityStrings.txt'):
        text = arc.read(name).decode('utf-8')
        seen = 0
        for sec in re.split(r'^(?=\[)', text, flags=re.M):
            sid = sec[1:5]
            if re.fullmatch(r'(IM|AM)0[0-9A-F]', sid):
                art = re.search(r'^Art=(.*)$', sec, re.M).group(1).strip()
                assert _exists(arc, v18, art), (sid, art)
                seen += 1
        assert seen == 16
    s = slk.Slk(arc.read('Units\\ItemData.slk').decode('latin-1'))
    assert all(s.find(m.stone_id) is not None for m in MEGAS)


def test_w3i_renamed(out):
    path, _, _ = out
    w3i = mpq.MPQ(path).read('war3map.w3i')
    assert b'Pokemon Arena v2.8\x00' in w3i
    assert b'v1.8' not in w3i
    assert b'v2.8: ' in w3i and b'Mega Evolution' in w3i
    j = mpq.MPQ(path).read('scripts\\war3map.j').decode('latin-1')
    assert 'call SetMapName("Pokemon Arena v2.8")' in j


def test_script_contains_module(out):
    path, _, _ = out
    j = mpq.MPQ(path).read('scripts\\war3map.j').decode('latin-1')
    assert 'call Mega_Init()' in j
    assert 'function Mega_InitData takes nothing returns nothing' in j


def test_listfile_lists_new_files(out):
    path, _, _ = out
    arc = mpq.MPQ(path)
    names = set(arc.listfile())
    assert 'war3mapImported\\Mega\\MegaCharizardX.mdx' in names
    assert 'scripts\\war3map.j' in names


def test_build_hash_capacity_and_wild(out):
    path, _, _ = out
    arc = mpq.MPQ(path)
    used = sum(1 for e in arc.hash_table if e[4] < len(arc.block_table))
    assert len(arc.hash_table) == 4096 and used < 3500
    assert arc.has('war3mapImported/Wild/Snorlax.mdx')
    j = arc.read('scripts/war3map.j').decode('latin-1')
    assert "set Wild_Pool[" in j and 'set Wild_CampN = 0' not in j
    assert 'set Rand_N = ' in j and '"-random"' in j
    units = objdata.ObjFile(arc.read('war3map.w3u'))
    assert units.find('nW1D') is not None and units.find('n01O').get('ulev') == 100


def test_build_new_pokemon(out):
    import poke_data
    path, _, _ = out
    arc = mpq.MPQ(path)
    j = arc.read('scripts/war3map.j').decode('latin-1')
    assert 'set Mega_N = 25' in j and ('set Evo_N = %d' % len([f for f in __import__('poke_data').FORMS if f.evolves_to])) in j and "'nTV5', -128.0, 4544.0, 270.0" in j
    units = objdata.ObjFile(arc.read('war3map.w3u'))
    for f in poke_data.FORMS:
        o = units.find(f.id)
        assert o is not None and arc.has(o.get('umdl')[:-4] + '.mdx') and arc.has(o.get('uico'))
    abil = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    assert all(abil.find(s.id) is not None for k in poke_data.KITS.values() for s in k)
    for m in MEGAS[16:]:
        assert arc.has(units.find(m.skin_id).get('umdl')[:-4] + '.mdx')
    for n in mpq.discover_names(mpq.MPQ(V18), open('tools/known_names_v18.txt').read().splitlines()):
        assert arc.has(n), n


def test_build_random_legends(out):
    import legend_data
    path, _, _ = out
    arc = mpq.MPQ(path)
    j = arc.read('scripts/war3map.j').decode('latin-1')
    assert ('set Leg_N = %d' % len(__import__('legend_data').SPAWN_LEGENDS)) in j and 'EVENT_PLAYER_UNIT_DAMAGING' in j
    units = objdata.ObjFile(arc.read('war3map.w3u'))
    for leg in legend_data.SPAWN_LEGENDS:  # v3.3: only the roomless legends have a random clone
        assert units.find(leg.id).get('ulev') == 100


def test_build_v26_features(out):
    path, _, _ = out
    arc = mpq.MPQ(path)
    raw = arc.read('scripts/war3map.j')
    assert 't là gà'.encode('utf-8') in raw  # chat command stored as UTF-8
    j = raw.decode('latin-1')
    assert "'nMS1', -4416.0, 640.0, 0.0" in j and "call SaveInteger(Mega_HT, 'n01R', 8, 'IS04')" in j
    items = slk.Slk(arc.read('Units\\ItemData.slk').decode('latin-1'))
    assert items.find('IS00') is not None and items.find('IS1B') is not None


def test_build_abilities(out):
    import jasscheck
    import inject
    path, _, _ = out
    arc = mpq.MPQ(path)
    s = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    assert s.find('AB00') is not None and s.find('AXA4') is not None and s.find('AXS7') is not None
    j = arc.read('scripts\\war3map.j').decode('latin-1')
    assert 'function Ab_OnDamaging takes nothing returns boolean' in j and 'call Ab_InitData()' in j
    assert "call SaveInteger(Ab_HT, 'E" in j  # type -> Ability links (v1.8 heroes)
    assert 'set Ab_N = 68' in j and 'set Ab_MegaAb[15] = ' in j
    # the injected blocks alone pass the checker (the rest of the v1.8 script has known false errors)
    blocks = {}
    for name, begin, end in (('glob', inject.GLOBALS_BEGIN, inject.GLOBALS_END),
                             ('pre', inject.PRELUDE_BEGIN, inject.PRELUDE_END),
                             ('funcs', inject.FUNCS_BEGIN, inject.FUNCS_END)):
        blocks[name] = j[j.index(begin) + len(begin):j.index(end)].strip('\n') + '\n'
    src = 'globals\n' + blocks['glob'] + 'endglobals\n' + blocks['pre'] + blocks['funcs']
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


PJASS = 'D:/Warcraft III Reforged/_retail_/x86_64/JassHelper/pjass.exe'
JASS_REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'analysis', 'jass_ref')


def test_built_script_compiles_with_pjass(out, tmp_path):
    """The real JASS compiler (tools/jasscheck.py only checks names and argument counts, not types or natives)."""
    common, blizzard = os.path.join(JASS_REF, 'common.j'), os.path.join(JASS_REF, 'Blizzard.j')
    if not all(os.path.isfile(f) for f in (PJASS, common, blizzard)):
        pytest.skip('pjass or its common.j / Blizzard.j (analysis/jass_ref) are not available')
    script = tmp_path / 'war3map.j'
    script.write_bytes(mpq.MPQ(out[0]).read('scripts\\war3map.j'))
    r = subprocess.run([PJASS, common, blizzard, str(script)], capture_output=True, text=True)
    text = (r.stdout + r.stderr).replace('\r', '')
    assert 'Parse failed' not in text and 'Parse successful' in text, text[-1500:]


def test_build_learned_moves(out):
    path, _, _ = out
    arc = mpq.MPQ(path)
    s = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    j = arc.read('scripts\\war3map.j').decode('latin-1')
    assert s.find('AV00') is not None and s.find('AW00') is not None and s.find('AY00') is not None and s.find('AZ00') is not None
    assert 'function Mv_InitData takes nothing returns nothing' in j and 'call Mv_Init()' in j
    assert "call SaveInteger(Ab_HT, 'E00E', 99, " in j and 'set Mv_Label[0] = "' in j
    assert 'call Mv_Sync(u)' in j and 'bj_lastReplacedUnit' in j
