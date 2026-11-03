import re

import pytest

import inject
import jasscheck
from ability_data import ABILITIES, FAMILY, info_id

MEGA_SCALE = {i: 1.0 + i / 100 for i in range(16)}
BASE_SCALE = {i: 2.0 for i in range(16)}
ABIL = {'abilities': ABILITIES, 'types': {'E003': 2}, 'megas': {1: 27}}


@pytest.fixture(scope='module')
def src():
    return inject.module_source(MEGA_SCALE, BASE_SCALE, abil=ABIL)


def _func(src, name):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_module_with_abilities_passes_checker(src):
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_family_constants_match_ability_data(src):
    found = {m.group(1): int(m.group(2)) for m in re.finditer(r'constant integer Ab_F_(\w+) = (\d+)', src)}
    assert found == {name: i for name, i in FAMILY.items()}


def test_scaling_constants(src):
    assert 'constant real Ab_ScaleK = %r' % float(__import__('balance').SKILL_SCALE_K) in src
    assert 'constant real Ab_ScaleBase = 50.0' in src
    assert 'constant real Ab_LevelK = %r' % float(__import__('balance').LEVEL_SKILL_K) in src
    assert 'GetHeroLevel(src) > 50' in _func(src, 'Ab_OnDamaging')
    assert 'constant real Ab_ScaleMax = 5.0' in src
    assert 'Ab_SkillMult(stat)' in _func(src, 'Ab_OnDamaging')
    body = _func(src, 'Ab_SkillMult')
    assert 'stat <= Ab_ScaleBase' in body and 'm > Ab_ScaleMax' in body


def test_damage_trigger_rules(src):
    dmg = _func(src, 'Ab_OnDamaging')
    assert dmg.index('call Leg_OnDamage()') < dmg.index('GetEventDamage()')  # legends first
    assert 'Ab_Busy' in dmg and 'src == t' in dmg
    assert 'BlzGetEventDamageType() != DAMAGE_TYPE_NORMAL' in dmg
    assert 'IsUnitEnemy(t, sp)' in dmg and 'GetPlayerId(sp) < 12' in dmg
    assert 'BlzSetEventDamage(dmg * m)' in dmg


def test_reflect_is_guarded_against_recursion(src):
    body = _func(src, 'Ab_InMult')
    assert body.count('set Ab_Busy = true') == 1 and body.count('set Ab_Busy = false') == 1


def test_mega_init_registers_one_damage_trigger(src):
    init = _func(src, 'Mega_Init')
    assert 'Condition(function Ab_OnDamaging)' in init
    assert 'Condition(function Leg_OnDamage)' not in init
    assert init.count('EVENT_PLAYER_UNIT_DAMAGING') == 1
    assert 'TimerStart(Ab_Timer, 0.5, true, function Ab_Tick)' in init
    assert 'EVENT_PLAYER_HERO_REVIVE_FINISH' in init and 'function Ab_OnRevive' in src
    assert 'call Ab_InitData()' in init


def test_info_button_swaps_with_ability(src):
    body = _func(src, 'Ab_Sync')
    assert 'UnitRemoveAbility(u, Ab_InfoId(have))' in body
    assert 'UnitAddAbility(u, Ab_InfoId(want))' in body
    assert 'Ab_Want' in body
    want = _func(src, 'Ab_Want')
    assert 'Mega_HT' in want and 'Ab_MegaAb[mi]' in want


def test_timed_effects_have_one_stop_path(src):
    assert 'call Ab_FxStop(i)' in _func(src, 'Ab_FxRun')
    stop = _func(src, 'Ab_FxStop')
    assert 'PauseUnit(u, false)' in stop and 'SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11))' in stop


def test_ab_init_has_effects_and_types(src):
    d = _func(src, 'Ab_InitData')
    assert "call SaveInteger(Ab_HT, 'E003', 0, 2)" in d and 'set Ab_MegaAb[1] = 27' in d


def _raw(text):
    return int.from_bytes(text.encode('ascii'), 'big')


def _info_code(a):
    """Same arithmetic as Ab_InfoId in mega.j."""
    def dig(d):
        return 48 + d if d < 10 else 55 + d
    i = a - 1
    hi = i // 36
    lo = i - hi * 36
    return _raw('AB00') - 12336 + dig(hi) * 256 + dig(lo)


def test_info_id_arithmetic_matches_ability_data():
    for a in range(1, len(ABILITIES) + 1):
        assert _info_code(a) == _raw(info_id(a - 1)), a
