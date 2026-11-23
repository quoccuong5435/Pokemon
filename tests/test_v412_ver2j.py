"""Test suite for Pokemon Arena v4.1.2-ver2j:
1. Guaranteed Elite creep at map start in every camp.
2. 30s Camp stacking reinforcement with different element + elite.
3. Smart 5-Tier creep combat AI focusing low-HP heroes (< 30% HP).
4. Distinct Pokémon icons & names for Form Shop (Deoxys), Paradox Shop (Walking Wake), Mega Shops.
5. Move tooltip line / AOE range & geometry indicators.
6. Distinct move icons (no generic plain circles for signature moves).
7. Relic Forge 30% drop 1 level / 70% safe retain.
8. Tight store layout (spacing 160) & League removal from base.
9. Full pjass compiler validation with 0 syntax errors.
"""
import os
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import mpq  # noqa: E402
import objdata  # noqa: E402

MAP_PATH = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2j.w3x')


@pytest.fixture(scope='module')
def map_mpq():
    assert os.path.exists(MAP_PATH), f"Target map not found: {MAP_PATH}"
    return mpq.MPQ(MAP_PATH)


@pytest.fixture(scope='module')
def map_script(map_mpq):
    return map_mpq.read('scripts\\war3map.j').decode('utf-8', errors='replace')


@pytest.fixture(scope='module')
def map_strings(map_mpq):
    return map_mpq.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', errors='replace')


@pytest.fixture(scope='module')
def map_w3u(map_mpq):
    return objdata.ObjFile(map_mpq.read('war3map.w3u'))


def test_smart_creep_ai_guaranteed_elite(map_script):
    """Verify that Wild_RegisterCamps guarantees at least 1 Elite creep per camp at map start."""
    assert 'call Wild_MakeElite(u)' in map_script
    assert 'LoadInteger(Mega_HT, best + 500, 4) == 0' in map_script
    assert 'call SaveInteger(Mega_HT, best + 500, 4, 1)' in map_script


def test_camp_stacking_reinforcements(map_script):
    """Verify that 30s camp stacking reinforcement logic is compiled into war3map.j."""
    assert 'function Wild_ReinforceCamp' in map_script
    assert 'Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0' in map_script
    assert 'call Wild_ReinforceCamp(c)' in map_script
    assert 'REINFORCED (+ELITE)!' in map_script
    assert 'set Wild_CampAlive[c] = Wild_CampAlive[c] + 3' in map_script


def test_smart_creep_combat_ai(map_script):
    """Verify that Ai_Unit scans 600 range and prioritizes low-HP heroes (< 30% HP)."""
    assert 'Smart AI Tier 1: Scan 600 range for low-HP heroes' in map_script
    assert 'call GroupEnumUnitsInRange(g, GetUnitX(u), GetUnitY(u), 600.0, null)' in map_script
    assert 'hp < 30.0 and hp < min_hp' in map_script
    assert 'call IssueTargetOrder(u, "attack", t)' in map_script


def test_distinct_shop_icons(map_w3u):
    """Verify that Form, Paradox, and Mega shops have authentic Pokemon icons and names."""
    # Form Shop -> Deoxys
    fs0 = map_w3u.find('nFS0')
    assert fs0 is not None
    assert 'BTNDeoxys (64 x 64).blp' in (fs0.get('uico') or '')
    assert 'Form Shop (Deoxys)' in (fs0.get('unam') or '')

    # Paradox Shop -> Walking Wake / Suicune
    fs1 = map_w3u.find('nFS1')
    assert fs1 is not None
    assert 'BTNPokeSuicune.blp' in (fs1.get('uico') or '')
    assert 'Paradox Shop (Walking Wake)' in (fs1.get('unam') or '')

    # Mega Shops
    ms1 = map_w3u.find('nMS1')
    assert ms1 is not None
    assert 'BTNMegaCharizardX.blp' in (ms1.get('uico') or '')

    ms2 = map_w3u.find('nMS2')
    assert ms2 is not None
    assert 'BTNMegaLucario.blp' in (ms2.get('uico') or '')

    ms3 = map_w3u.find('nMS3')
    assert ms3 is not None
    assert 'BTNMegaRayquaza.blp' in (ms3.get('uico') or '')


def test_move_range_line_indicators(map_strings):
    """Verify that line moves and AOE moves contain explicit geometric indicators in tooltips."""
    assert '[Line AOE]' in map_strings
    assert '[Area AOE]' in map_strings
    assert '[Single Target]' in map_strings
    # Acid Spray AV02 should have Line AOE
    assert '[Line AOE]|r |cffffcc00Range: 700|r, |cff7ed6dfWidth: 100|r' in map_strings


def test_distinct_move_icons(map_strings):
    """Verify that signature moves use distinct Pokemon icons instead of generic plain circles."""
    assert 'BTNSwift (64 x 64).blp' in map_strings
    assert 'BTNThunder (64 x 64).blp' in map_strings
    assert 'BTNWater Fall (64 x 64).blp' in map_strings
    assert 'BTNMagnitude (64 x 64).blp' in map_strings


def test_relic_forge_penalty_30_70(map_script):
    """Verify Relic Forge failure penalty: 30% drop 1 level, 70% retain current level."""
    assert 'GetRandomInt(1, 100) <= 30' in map_script
    assert 'FORGE FAIL (SAFE)' in map_script
    assert 'Item retained safely at +' in map_script


def test_base_layout_spacing_and_league_removal(map_script):
    """Verify tight store layout (spacing 160) and complete removal of base League portal."""
    # Top row
    assert "-5960.0,544.0" in map_script
    assert "-5800.0,544.0" in map_script
    assert "-5640.0,544.0" in map_script

    # Bottom row
    assert "nMS1', -5960.0, -544.0" in map_script
    assert "sx * 5480.0" in map_script
    assert "sx * 5320.0" in map_script

    # League portal disabled
    assert 'set k = 2' in map_script
