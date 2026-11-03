import os
import re

import pytest

import objdata
import wild_data
from conftest import EXTRACTED

SCRIPT = open(os.path.join(EXTRACTED, 'scripts', 'war3map.j'), encoding='latin-1').read()
W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())

SPEC = {  # power: (names, level, hp, dmg, armor, gold)
    1: (('Hoothoot', 'Lotad', 'Diglett'), 3, 245, 15, 1, 10),
    2: (('Mareep', 'Houndour', 'Swinub'), 7, 630, 45, 2, 20),
    3: (('Sneasel', 'Misdreavus', 'Chinchou'), 12, 1050, 80, 4, 30),
    4: (('Noctowl', 'Flaaffy', 'Breloom'), 18, 1540, 120, 6, 45),
    5: (('Manectric', 'Piloswine', 'Vibrava'), 24, 2100, 160, 8, 60),
    6: (('Houndoom', 'Mismagius', 'Weavile'), 32, 2800, 210, 11, 80),
    7: (('Ampharos', 'Ludicolo', 'Flygon'), 40, 3850, 270, 14, 100),
    8: (('Mamoswine', 'Altaria', 'Absol'), 50, 5250, 340, 18, 130),
    9: (('Electivire', 'Magmortar', 'Rhyperior'), 62, 7000, 420, 22, 160),
    10: (('Snorlax', 'Lapras', 'Dusknoir'), 75, 9100, 500, 26, 200),
}


def test_species_table_matches_spec():
    sp = wild_data.SPECIES
    assert len(sp) == 30
    for i, s in enumerate(sp):
        assert s.index == i and s.id == 'nW%02X' % i
        names, lv, hp, dmg, armor, gold = SPEC[s.power]
        assert s.name in names
        assert (s.level, s.hp, s.dmg, s.armor, s.gold) == (lv, hp, dmg, armor, gold)
    for p, row in SPEC.items():
        assert sorted(s.name for s in sp if s.power == p) == sorted(row[0])


def test_power_for_level():
    f = wild_data.power_for_level
    assert [f(x) for x in (1, 2, 4, 5, 6, 9, 10, 12, 14, 15, 20, 21, 27, 28, 35, 36, 44, 45, 55, 56, 70, 71, 75)] == \
        [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10]


def test_wild_types_rule():
    types = set(wild_data.wild_types(W3U))
    for t in ('n00I', 'n01R', 'n01V', 'n02K', 'n02G', 'n028', 'n029', 'n023', 'n01Z', 'n01S', 'n00L', 'nogl'):
        assert t in types, t
    for t in ('n00R', 'n01E', 'n031', 'n032', 'n02H', 'n02I', 'n01O', 'n00C', 'n004', 'h010', 'n03A'):
        assert t not in types, t


def _init_creates():
    start = SCRIPT.index('local player p=Player(PLAYER_NEUTRAL_AGGRESSIVE)')
    end = SCRIPT.index('endfunction', start)
    return re.findall(r"CreateUnit\(p,'(\w{4})',", SCRIPT[start:end])


def test_camps_only_wild_types():
    types = set(wild_data.wild_types(W3U))
    camps = wild_data.camps(SCRIPT, W3U)
    wild_creates = [t for t in _init_creates() if t in types]
    assert sum(c.count for c in camps) == len(wild_creates)
    assert all(1 <= c.power <= 10 for c in camps)
    by_pos = {(round(c.x), round(c.y)): c for c in camps}
    assert by_pos[(5887, 3414)].power == 1          # Caterpie lv2 alone
    assert any(c.power == 3 for c in camps)          # Tentacruel lv12
    assert len(camps) > 30


def test_camps_merge_close_units():
    camps = wild_data.camps(SCRIPT, W3U)
    rattata = [c for c in camps if abs(c.x - 4741) < 5 and abs(c.y - 1728) < 5]
    assert len(rattata) == 1 and rattata[0].count == 3 and rattata[0].power == 2


@pytest.mark.parametrize('lv,power', [(2, 1), (8, 2), (12, 3)])
def test_power_samples(lv, power):
    assert wild_data.power_for_level(lv) == power


def test_tier_by_average_level():
    assert (wild_data.LEVEL_CHECK_SECONDS, wild_data.LEVELS_PER_TIER) == (300.0, 10)
    assert not hasattr(wild_data, 'TIER_SECONDS')
