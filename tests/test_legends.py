import os
import tempfile

import pytest

import assets
import inject
import jasscheck
import legend_data as ld
import mpq
import objdata
import objects
from conftest import EXTRACTED, PKL, V18

MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
SRC = inject.module_source(MS, BS, None, None, None, ld.LEGENDS)


def _func(name):
    i = SRC.index('function %s takes' % name)
    return SRC[i:SRC.index('endfunction', i)]


def test_legend_pool():
    assert len(ld.LEGENDS) == 24
    assert [(l.id, l.boss, l.soul) for l in ld.LEGENDS[:2]] == [('nL00', 'n00C', 'I01C'), ('nL01', 'n00D', 'I01D')]
    assert len({l.id for l in ld.LEGENDS}) == 24 and len({l.soul for l in ld.LEGENDS}) == 24
    names = open(os.path.join(EXTRACTED, 'Units', 'ItemFunc.txt'), encoding='utf-8').read()
    for l in [x for x in ld.LEGENDS if x.soul[:2] != 'IS']:  # v3.3: the Celebi Soul (ISCE) is added by us
        assert '[%s]\nName=%s Soul' % (l.soul, l.name) in names.replace('\r\n', '\n')
    assert (ld.SPAWN_SECONDS, ld.MAX_ALIVE, ld.SOUL_CHANCE, ld.WILD_SOUL_CHANCE, ld.MIN_LEVEL) == (180.0, 99, 100, 20.0, 100)


def test_legend_units_are_lv100_clones():
    v18 = mpq.MPQ(V18)
    pkl = mpq.MPQ(PKL)
    a = assets.collect(pkl, v18, tempfile.mkdtemp())
    a.legends = ld.LEGENDS
    files = {n: v18.read(n) for n in objects.OBJECT_FILES}
    f = objdata.ObjFile(objects.apply(files, a)['war3map.w3u'])
    for l in ld.LEGENDS:
        o, boss = f.find(l.id), f.find(l.boss)
        assert o is not None and o.orig == boss.orig
        assert o.get('ulev') == 100 and o.get('uhpm') == boss.get('uhpm') and o.get('ua1b') == boss.get('ua1b')
        assert o.get('unam') == 'Wild %s' % l.name


def test_module_passes_checker():
    assert jasscheck.check(SRC, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_data_init():
    d = inject.gen_data_init(MS, BS, None, None, None, ld.LEGENDS)
    assert 'set Leg_N = 24' in d and "set Leg_Type[0] = 'nL00'" in d and "set Leg_Soul[0] = 'I01C'" in d
    assert 'set Leg_Name[0] = "Articuno"' in d


def test_spawn_every_5_minutes_max_2():
    assert 'real Leg_Interval = 180.0' in SRC and 'integer Leg_Max = 99' in SRC and 'real Leg_Next = 180.0' in SRC
    tick = _func('Wild_Tick')
    assert 'Wild_Time >= Leg_Next' in tick and 'Leg_Alive < Leg_Max' in tick and 'call Leg_Spawn()' in tick
    spawn = _func('Leg_Spawn')
    assert 'PingMinimap(' in spawn and 'Wild_CampX[c]' in spawn


def test_only_level_100_damages_random_legends():
    dmg = _func('Leg_OnDamage')
    assert 'Leg_IsLegend(GetUnitTypeId(t))' in dmg
    assert 'Leg_PlayerLevel(p) < Leg_MinLevel' in dmg and 'call BlzSetEventDamage(0.0)' in dmg
    assert 'integer Leg_MinLevel = 100' in SRC
    assert 'EVENT_PLAYER_UNIT_DAMAGING' in _func('Mega_Init')


def test_drops():
    death = _func('Leg_OnDeath')
    assert 'GetRandomInt(1, 100) <= Leg_SoulChance' in death and 'Leg_Soul[i]' in death
    for item in ("'I00B'", "'I001'", "'I000'"):
        assert item in death
    assert 'real Wild_SoulChance = 20.0' in SRC
    assert 'call Leg_OnDeath(' in _func('Mega_OnDeath')
