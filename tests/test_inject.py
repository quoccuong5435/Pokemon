import os
import re

import pytest

import inject
import jasscheck
from conftest import EXTRACTED

V18_J = open(os.path.join(EXTRACTED, 'scripts', 'war3map.j'), encoding='latin-1').read()
MEGA_SCALE = {i: 1.0 + i / 100 for i in range(16)}
BASE_SCALE = {i: 2.0 for i in range(16)}


@pytest.fixture(scope='module')
def injected():
    return inject.inject(V18_J, MEGA_SCALE, BASE_SCALE, version='2.0')


def test_inject_version_parameter():
    t = inject.inject(V18_J, MEGA_SCALE, BASE_SCALE, version='2.3')
    assert 'call SetMapName("Pokemon Arena v2.3")' in t and 'v1.8' not in t


def test_module_passes_checker():
    src = inject.module_source(MEGA_SCALE, BASE_SCALE)
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_inject_positions(injected):
    t = injected
    eg = t.find('endglobals')
    assert 0 < t.find('hashtable Mega_HT') < eg
    assert eg < t.find('function Mega_Init takes') < t.find('function main takes nothing returns nothing')
    i = t.find('function main takes nothing returns nothing')
    j = t.find('endfunction', i)
    assert t[i:j].rstrip().endswith('call Mega_Init()')
    assert 'call SetMapName("Pokemon Arena v2.0")' in t
    assert 'v1.8' not in t


def test_original_script_otherwise_unchanged(injected):
    t = injected
    g0, g1 = t.find(inject.GLOBALS_BEGIN), t.find(inject.GLOBALS_END) + len(inject.GLOBALS_END)
    p0, p1 = t.find(inject.PRELUDE_BEGIN), t.find(inject.PRELUDE_END) + len(inject.PRELUDE_END)
    f0, f1 = t.find(inject.FUNCS_BEGIN), t.find(inject.FUNCS_END) + len(inject.FUNCS_END)
    assert g1 < p0 < p1 < f0
    stripped = t[:g0] + t[g1:p0] + t[p1:f0] + t[f1:]
    stripped = stripped.replace('call Mega_Init()\n', '', 1).replace('Pokemon Arena v2.0', 'Pokemon Arena v1.8')
    expected = V18_J.replace('call ReplaceUnitBJ(', 'call Mega_SafeReplace(')
    expected = expected.replace(inject.REVIVE_SLEEP_OLD, inject.REVIVE_SLEEP_NEW)
    expected = expected.replace(inject.REVIVE_MSG_OLD, inject.REVIVE_MSG_NEW)
    expected = inject.patch_boss_souls(expected)  # v3.3: boss Soul chance 30% -> 100%
    assert re.sub(r'\s+', '', stripped) == re.sub(r'\s+', '', expected)


def test_evolution_replacements_are_guarded(injected):
    t = injected
    own = inject.module_source(MEGA_SCALE, BASE_SCALE).count('call Mega_SafeReplace(')  # Evo_* of the module
    assert t.count('call Mega_SafeReplace(') == 74 + own
    assert t.count('ReplaceUnitBJ(') == 1  # only inside the wrapper
    wrapper = t.find('function Mega_SafeReplace takes')
    assert t.find('endglobals') < wrapper < t.find('call Mega_SafeReplace(')


def test_prelude_passes_checker():
    src = inject.module_source(MEGA_SCALE, BASE_SCALE)
    assert 'function Mega_SafeReplace takes unit u, integer newId, integer method returns nothing' in src
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_revive_is_10_seconds(injected):
    t = injected
    assert 'TriggerSleepAction(I2R((1*GetUnitLevel(GetTriggerUnit()))))' not in t
    assert t.count('call TriggerSleepAction(10.00)') == V18_J.count('call TriggerSleepAction(10.00)') + 1
    assert t.count('" will revive after "+(("|cffffcc00"+"10")') == 2


def test_data_init_matches_table():
    d = inject.gen_data_init(MEGA_SCALE, BASE_SCALE)
    assert "set Mega_Base[1] = 'E00E'" in d
    assert "set Mega_Stone[13] = 'IM0D'" in d
    assert "set Mega_Skin[15] = 'hM0F'" in d
    assert "set Mega_Evolve[2] = 'AM02'" in d
    assert 'Mega_Attr' not in d
    assert 'set Mega_PStr[1] = 20' in d
    assert 'set Mega_PInt[2] = 20' in d
    assert 'set Mega_Name[1] = "Mega Charizard X"' in d
    assert 'set Mega_Scale[3] = 1.030' in d
    assert 'set Mega_BaseScale[3] = 2.000' in d
    assert 'set Mega_Fx[4] = "Abilities\\\\Spells\\\\Other\\\\GeneralAuraTarget\\\\GeneralAuraTarget.mdl"' in d
    assert 'set Mega_R[13] = 170' in d


def test_module_constants():
    src = inject.module_source(MEGA_SCALE, BASE_SCALE)
    assert 'real Mega_Duration = 60.0' in src
    assert 'real Mega_Cooldown = 150.0' in src
    # shops stand outside the base door (v2.6), not in the doorway
    assert "'nMS1', -4416.0, 640.0, 0.0" in src and "'nMS1', 4416.0, -640.0, 180.0" in src
    assert "'nMS2', -4416.0, -640.0, 0.0" in src and "'nMS2', 4416.0, 640.0, 180.0" in src
    assert '5248.0, 384.0' not in src


def _func(src, name):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_mega_buff_in_module():
    src = inject.module_source(MEGA_SCALE, BASE_SCALE)
    start, end = _func(src, 'Mega_Start'), _func(src, 'Mega_End')
    for body in (start, end):
        for call in ('SetHeroStr(', 'SetHeroAgi(', 'SetHeroInt(', 'BlzSetUnitBaseDamage('):
            assert call in body, call
    for key in (10, 11, 12, 13):
        assert 'SaveInteger(Mega_HT, h, %d,' % key in start
        assert 'LoadInteger(Mega_HT, h, %d)' % key in end
    assert 'Mega_PctPerPoint' in start and 'Mega_DamageBonus' in start


AB_GLOBALS = """globals
hashtable Ab_HT
integer Ab_N = 0
integer array Ab_Fam
real array Ab_X
real array Ab_Y
real array Ab_Z
real array Ab_W
string array Ab_S
integer array Ab_Raw
string array Ab_Name
string array Ab_Info
integer array Ab_MegaAb
endglobals
"""


def test_ab_init_empty():
    d = inject.gen_ab_init(None)
    assert d.startswith('function Ab_InitData takes nothing returns nothing\n    set Ab_N = 0\n')
    assert d.rstrip().endswith('endfunction')
    assert jasscheck.check(AB_GLOBALS + d, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_ab_init_data():
    from ability_data import ABILITIES
    d = inject.gen_ab_init({'abilities': ABILITIES, 'types': {'E003': 2}, 'megas': {1: 27}})
    blaze = 2  # 1-based: Overgrow is 1, Blaze is 2 -> effects 4 and 5
    assert 'set Ab_N = %d' % len(ABILITIES) in d
    assert 'set Ab_Name[%d] = "Blaze"' % blaze in d
    assert 'set Ab_Fam[%d] = 1' % (blaze * 2) in d  # PINCH
    assert 'set Ab_X[%d] = 0.3300' % (blaze * 2) in d and 'set Ab_Y[%d] = 0.4000' % (blaze * 2) in d
    assert "call SaveInteger(Ab_HT, 'E003', 0, 2)" in d
    assert 'set Ab_MegaAb[1] = 27' in d
    shell = [k for k, ab in enumerate(ABILITIES, 1) if ab.name == 'Shell Armor'][0]
    assert "set Ab_Raw[%d] = 'AXA4'" % (shell * 2) in d
    assert jasscheck.check(AB_GLOBALS + d, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_data_init_takes_abilities():
    from ability_data import ABILITIES
    abil = {'abilities': ABILITIES, 'types': {}, 'megas': {}}
    d = inject.gen_data_init(MEGA_SCALE, BASE_SCALE, abil=abil)
    assert 'function Ab_InitData' in d and 'set Ab_N = %d' % len(ABILITIES) in d
    assert 'set Ab_N = 0' in inject.gen_data_init(MEGA_SCALE, BASE_SCALE)
