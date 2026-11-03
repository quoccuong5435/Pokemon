import inject
import jasscheck
import poke_data as pd

MS25 = {i: 1.0 for i in range(25)}
BS25 = {i: 1.0 for i in range(25)}
MS16 = {i: 1.0 for i in range(16)}
EVO = inject.evo_inputs()


def _func(src, name):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_evo_inputs_from_poke_data():
    assert EVO['level'][0] == ('EN00', 'EN01', 16)
    assert ('EN0A', 'EN0B', 30) in EVO['level'] and len(EVO['level']) == len([f for f in __import__('poke_data').FORMS if f.evolves_to])
    assert EVO['item'] == [('EN0A', 'I00P', 'EN0C')]


def test_evo_module_passes_checker():
    src = inject.module_source(MS25, BS25, None, None, EVO)
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_evo_data_init():
    d = inject.gen_data_init(MS25, BS25, None, None, EVO)
    for line in ("set Evo_From[0] = 'EN00'", "set Evo_To[0] = 'EN01'", 'set Evo_Level[0] = 16',
                 "set Evo_ItemFrom[0] = 'EN0A'", "set Evo_Item[0] = 'I00P'", "set Evo_ItemTo[0] = 'EN0C'",
                 ('set Evo_N = %d' % len([f for f in __import__('poke_data').FORMS if f.evolves_to])), 'set Evo_ItemN = 1', 'set Mega_N = 25',
                 "'nTV5', -128.0, 4544.0, 270.0", "'nMS3', -4416.0, 1088.0, 0.0", "'nMS3', 4416.0, -1088.0, 180.0"):
        assert line in d, line


def test_mega_n_follows_present_megas():
    d = inject.gen_data_init(MS16, MS16)
    assert 'set Mega_N = 16' in d and "set Mega_Base[16]" not in d and "'nTV5'" not in d


def test_evo_uses_safe_replace_and_is_registered():
    src = inject.module_source(MS25, BS25, None, None, EVO)
    assert 'call Mega_SafeReplace(u, Evo_To[i], bj_UNIT_STATE_METHOD_RELATIVE)' in _func(src, 'Evo_OnLevel')
    assert 'call Mega_SafeReplace(u, Evo_ItemTo[i], bj_UNIT_STATE_METHOD_RELATIVE)' in _func(src, 'Evo_OnPickup')
    init = _func(src, 'Mega_Init')
    assert 'EVENT_PLAYER_HERO_LEVEL' in init and 'function Evo_OnLevel' in init
    assert 'EVENT_PLAYER_UNIT_PICKUP_ITEM' in init and 'function Evo_OnPickup' in init
    assert 'call Evo_InitData()' in init


def test_random_pool_includes_new_starters():
    import os
    import objdata
    from conftest import EXTRACTED
    w3u = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
    pool = inject.random_pool(w3u, pd.STARTERS)
    assert len(pool) == 51 and pool[-8:] == pd.STARTERS
