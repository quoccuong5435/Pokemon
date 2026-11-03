import os
import tempfile

import assets
import inject
import jasscheck
import mpq
import objdata
import objects
import slk
import wild_data
from conftest import EXTRACTED, PKL, V18

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
SOULS = wild_data.wild_souls(W3U)
MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
SCRIPT = open(os.path.join(EXTRACTED, 'scripts', 'war3map.j'), encoding='latin-1').read()
WILD = inject.wild_inputs(SCRIPT, W3U)
SRC = inject.module_source(MS, BS, WILD)


def _func(name):
    i = SRC.index('function %s takes' % name)
    return SRC[i:SRC.index('endfunction', i)]


def test_only_playable_species_have_souls():
    by_name = {s.name: s for s in SOULS}
    assert by_name['Rattata'].hero == 'E00T' and by_name['Absol'].hero == 'EN0K'
    assert by_name['Magikarp'].item == 'I01O' and by_name['Magikarp'].new is False  # the map's own Magikarp Soul
    assert 'Nidoqueen' not in by_name  # v3.3: Hoothoot and Snorlax are playable now (PKLegends forms)
    new = [s for s in SOULS if s.new]
    assert [s.item for s in new][:2] == ['IS00', 'IS01'] and len({s.item for s in new}) == len(new)
    assert set(by_name['Rattata'].wild_types) == {'n01R', 'n01S'}
    assert wild_data.WILD_SOUL_CHANCE == 20.0


def test_soul_items_added():
    v18 = mpq.MPQ(V18)
    a = assets.collect(mpq.MPQ(PKL), v18, tempfile.mkdtemp())
    a.wild_souls = SOULS
    out = objects.apply({n: v18.read(n) for n in objects.OBJECT_FILES}, a)
    s = slk.Slk(out['Units\\ItemData.slk'].decode('latin-1'))
    txt = out['Units\\ItemFunc.txt'].decode('utf-8')
    for soul in SOULS:
        if soul.new:
            assert s.find(soul.item) is not None, soul.item
            assert '[%s]\nName=%s Soul\n' % (soul.item, soul.name) in txt


def test_module_passes_checker():
    assert jasscheck.check(SRC, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_wild_creeps_drop_their_own_soul():
    d = inject.gen_data_init(MS, BS, WILD)
    assert "call SaveInteger(Mega_HT, 'n01R', 8, 'IS%s')" % SOULS[[s.name for s in SOULS].index('Rattata')].item[2:] in d
    death = _func('Wild_OnDeath')
    assert 'LoadInteger(Mega_HT, GetUnitTypeId(u), 8)' in death
    assert 'GetRandomReal(0.0, 100.0) < Wild_SoulChance' in death
    assert 'Leg_Soul[GetRandomInt' not in death


def test_new_souls_transform_in_the_centre_circle():
    d = inject.gen_data_init(MS, BS, WILD)
    rattata = [s for s in SOULS if s.name == 'Rattata'][0]
    assert "set Soul_Item[%d] = '%s'" % ([s for s in SOULS if s.new].index(rattata), rattata.item) in d
    enter = _func('Soul_OnEnter')
    assert 'UnitItemInSlot(u, 0)' in enter and 'call Mega_SafeReplace(u, Soul_Hero[i], bj_UNIT_STATE_METHOD_RELATIVE)' in enter
    assert 'TriggerRegisterEnterRectSimple(t, Hi)' in _func('Mega_Init')
