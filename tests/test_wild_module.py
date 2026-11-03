import os

import inject
import jasscheck
import objdata
import wild_data
from conftest import EXTRACTED

SCRIPT = open(os.path.join(EXTRACTED, 'scripts', 'war3map.j'), encoding='latin-1').read()
W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
WILD = inject.wild_inputs(SCRIPT, W3U)


def _func(src, name):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_wild_inputs():
    assert len(WILD['camps']) == len(wild_data.camps(SCRIPT, W3U))
    pool = dict(WILD['pool'])
    assert pool['nW00'] == 1 and pool['nW1D'] == 10
    assert pool['n00I'] == 1 and pool['n01R'] == 2   # old wild types keep their power
    assert set(WILD['types']) == set(wild_data.wild_types(W3U)) | {s.id for s in wild_data.SPECIES}


def test_wild_module_passes_checker():
    src = inject.module_source(MS, BS, WILD)
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_wild_data_init():
    d = inject.gen_data_init(MS, BS, WILD)
    assert "set Wild_Pool[0] = '" in d
    assert 'set Wild_CampN = %d' % len(WILD['camps']) in d
    assert 'set Wild_PoolN = %d' % len(WILD['pool']) in d
    assert 'set Wild_TypeN = %d' % len(WILD['types']) in d
    assert 'set Wild_CampX[0] = ' in d and 'set Wild_CampPow[0] = ' in d


def test_wild_apply_uses_stored_bases():
    src = inject.module_source(MS, BS, WILD)
    assert 'call Wild_Scale(u)' in _func(src, 'Wild_Apply')
    body = _func(src, 'Wild_Scale')
    assert 'BlzSetUnitMaxHP(u, R2I(I2R(LoadInteger(Mega_HT, h, 20)) * m * hpf))' in body
    assert 'BlzSetUnitBaseDamage(u, R2I(I2R(LoadInteger(Mega_HT, h, 21)) * m * dmf * Wild_DmgMult), 0)' in body
    assert 'BlzSetUnitArmor(u, LoadReal(Mega_HT, h, 22) + I2R(Wild_Tier * Wild_TierArmor) + armadd)' in body
    assert 'LoadInteger(Mega_HT, h, 23)' in body


def test_elite_camp_creep():
    src = inject.module_source(MS, BS, WILD)
    spawn = _func(src, 'Wild_SpawnCamp')
    assert 'call Wild_MakeElite(u)' in spawn and 'GetRandomInt(0, Wild_CampSize[c] - 1)' in spawn
    assert 'call SaveInteger(Mega_HT, GetHandleId(u), 29, 1)' in _func(src, 'Wild_MakeElite')
    assert 'real Wild_EliteHP = 2.0' in src and 'real Wild_EliteGold = 3.0' in src
    assert 'LoadInteger(Mega_HT, h, 29) == 1' in _func(src, 'Wild_Scale')


def test_wild_constants_match_spec():
    src = inject.module_source(MS, BS, WILD)
    for line in ('real Wild_LevelCheck = 300.0', 'integer Wild_LevelsPerTier = 10', 'integer Wild_TierMax = 10',
                 'real Wild_TierStep = 0.08', 'integer Wild_TierArmor = 1', 'real Wild_Respawn = 10.0',
                 'real Wild_CampRadius = 600.0'):
        assert line in src, line
    assert 'Wild_TierSeconds' not in src and 'Wild_NextTier' not in src  # no more time-based tiers
    assert 'call Wild_RegisterCamps()' in _func(src, 'Mega_Init')
    assert 'call Wild_OnDeath(' in _func(src, 'Mega_OnDeath')


def test_tier_follows_average_hero_level():
    src = inject.module_source(MS, BS, WILD)
    upd = _func(src, 'Wild_UpdateTier')
    assert 'GetHeroLevel(u)' in upd and "GetUnitTypeId(u) != 'earc'" in upd
    assert 'IsUnitType(u, UNIT_TYPE_HERO)' in upd
    assert 'set t = Wild_AvgLevel / Wild_LevelsPerTier' in upd
    # average of the two lowest players (each player counts with their highest hero)
    assert 'set Wild_AvgLevel = (low_a + low_b) / 2' in upd and 'set Wild_AvgLevel = low_a' in upd
    assert 'call Wild_UpdateTier()' in _func(src, 'Wild_Tick')
    level = _func(src, 'Wild_ApplyLevel')
    assert 'BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, lv)' in level and 'LoadInteger(Mega_HT, h, 26)' in level
    assert 'call Wild_ApplyLevel(u)' in _func(src, 'Wild_Scan')


def test_injected_script_runs_wild_init():
    t = inject.inject(SCRIPT, MS, BS, WILD)
    assert 'function Wild_InitData takes nothing returns nothing' in t
    assert t.index('function Wild_InitData') < t.index('function Mega_Init takes')
