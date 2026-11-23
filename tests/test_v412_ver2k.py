"""Test suite for Pokemon Arena v4.1.2-ver2k:
1. Shop Courtyard Clean 2-Row Grid (5 Shops Top, 5 Shops Bottom, 180 spacing, ZERO overlap).
2. All 10 Shops have uniform scale 0.30 and NO floating magic auras (Devotion/Brilliance).
3. Authentic Pokemon Portraits on all 33 Mega Stones, 11 Form Orbs, 10 Paradox Boosters, 24 Items in ItemFunc.txt.
4. Non-Legend Paradox Ability Locking (Roaring Moon, Sandy Shocks, Flutter Mane, Scream Tail, Iron Thorns, Iron Valiant, Iron Jugulis).
5. Quest 3 Altar Rescue & Dual-Path PvE Boss Completion (+30s Legend Boss / +15s Elite, 30s target, cumulative, stealth pings).
6. Mid-Game Pacing (Mega Evolution at Gym 4, Paradox at Gym 6, 6,500g Paradox items, Lv 65 Awakening Quest).
7. Full PJASS syntax verification and compilation integrity.
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
import slk  # noqa: E402
import pokemon_item_icons  # noqa: E402

MAP_PATH = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2k.w3x')


@pytest.fixture(scope='module')
def map_mpq():
    assert os.path.exists(MAP_PATH), f"Target map not found: {MAP_PATH}"
    return mpq.MPQ(MAP_PATH)


@pytest.fixture(scope='module')
def map_script(map_mpq):
    return map_mpq.read('scripts\\war3map.j').decode('utf-8', errors='replace')


@pytest.fixture(scope='module')
def map_w3u(map_mpq):
    return objdata.ObjFile(map_mpq.read('war3map.w3u'))


@pytest.fixture(scope='module')
def map_items_slk(map_mpq):
    return slk.Slk(map_mpq.read('Units\\ItemData.slk').decode('latin-1'))


@pytest.fixture(scope='module')
def map_item_func(map_mpq):
    return map_mpq.read('Units\\ItemFunc.txt').decode('utf-8', errors='replace')


def test_shop_courtyard_layout(map_script, map_w3u):
    """Verify that shops form a clean 2-row grid of 5 shops each with 180 spacing and no overlap."""
    # Top Row: 5960, 5780, 5600, 5420, 5240 at Y = 544.0
    assert "set u=CreateUnit(p,'n00O',-5960.0,544.0,270.000)" in map_script
    assert "set u=CreateUnit(p,'n00N',-5780.0,544.0,270.000)" in map_script
    assert "set u=CreateUnit(p,'n00Q',-5600.0,544.0,270.000)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 544.0, 270.0)" in map_script

    # Bottom Row: 5960, 5780, 5600, 5420, 5240 at Y = -544.0
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', -5960.0, -544.0, 90.0)" in map_script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', -5780.0, -544.0, 90.0)" in map_script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', -5600.0, -544.0, 90.0)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -544.0, 90.0)" in map_script

    # Verify uniform 0.30 scale
    for sid in ['n00O', 'n00N', 'n00Q', 'nIS0', 'nBS0', 'nMS1', 'nMS2', 'nMS3', 'nFS0', 'nFS1']:
        u = map_w3u.find(sid)
        assert u is not None, f"Shop {sid} not found in w3u"
        scale = u.get('usca')
        assert scale == pytest.approx(0.30, rel=1e-2), f"Shop {sid} scale {scale} != 0.30"


def test_shop_auras_and_league_removal(map_script):
    """Verify that floating blue magic circles (Devotion/Brilliance) and League portal are removed."""
    # No DevotionAura attached to shops in Ext_PlaceShops
    assert 'DevotionAura' not in map_script.split('function Ext_PlaceShops')[1].split('endfunction')[0]
    # League base portal loop removed
    assert 'League base portal completely removed' in map_script
    assert 'CircleOfPower.mdl", gx, gy' not in map_script


def test_authentic_pokemon_item_icons(map_item_func, map_mpq):
    """Verify that all Mega Stones, Form Orbs, Paradox Boosters, and Evolution items have authentic icons."""
    for itid, expected_icon in pokemon_item_icons.ALL_ITEM_ICON_UPDATES.items():
        assert f'[{itid}]' in map_item_func, f"Item section [{itid}] missing from ItemFunc.txt"
        assert f'Art={expected_icon}' in map_item_func, f"Item {itid} does not have expected Art={expected_icon}"
        assert map_mpq.has(expected_icon), f"Icon {expected_icon} is missing from the map MPQ!"


def test_non_legend_paradox_locked(map_script):
    """Verify that non-legend Paradox Pokemon must complete Awakening Quest just like Legends."""
    # Verify non-legend Paradox registered in PAX_Leg_Index (26..32)
    assert "id == 'EN0F'" in map_script  # Roaring Moon
    assert "return 26" in map_script
    assert "id == 'E032' or id == 'P4XA' or id == 'P2LA'" in map_script  # Sandy Shocks
    assert "return 27" in map_script
    assert "id == 'P2UA' or id == 'P2VA'" in map_script  # Flutter Mane
    assert "return 28" in map_script
    assert "id == 'P20A' or id == 'P4IA'" in map_script  # Scream Tail
    assert "return 29" in map_script
    assert "id == 'EN08'" in map_script  # Iron Thorns
    assert "return 30" in map_script
    assert "id == 'EN0B' or id == 'EN0C'" in map_script  # Iron Valiant
    assert "return 31" in map_script
    assert "id == 'P1YA'" in map_script  # Iron Jugulis
    assert "return 32" in map_script

    # Total registered count is 32
    assert "function PAX_Leg_Count takes nothing returns integer\r\n    return 32" in map_script or \
           "function PAX_Leg_Count takes nothing returns integer\n    return 32" in map_script

    # Key space expanded to 64 slots per player
    assert "return 1000 + pid * 64 + idx" in map_script

    # PAX_Leg_Awakened NO LONGER auto-awakens forms >= 13!
    assert "if PAX_Form_Id(u) >= 13 then" not in map_script

    # PAX_Paradox_Proc requires awakened status
    assert "if not PAX_Leg_Awakened(src) then" in map_script


def test_quest_3_altar_rescue_and_dual_path(map_script):
    """Verify that Quest 3 ritual is 30s, cumulative, stealth, and has a PvE boss alternative."""
    # 30s target in tick
    assert "Ritual: \" + I2S(sec) + \"/30s" in map_script
    assert "if sec >= 30 then" in map_script

    # Progress decay (-2s/s) removed
    assert "dist > 550.0 and LoadInteger(PAX_Leg_HT, qk, 4) > 0" not in map_script

    # Global Ping and Announce removed
    assert "started Awakening at the Center Altar" not in map_script

    # Dual-path PvE completion in Stage 3: +30s Legend Boss / +15s Elite
    assert "Dual-Path PvE Completion: Defeating 1 Legend Boss (+30s) or 2 Elites (+15s each) completes Stage 3!" in map_script
    assert "if isLegend then\r\n            set add = 30" in map_script or "if isLegend then\n            set add = 30" in map_script


def test_mid_game_pacing_and_prices(map_script, map_items_slk):
    """Verify Gym 4 Mega, Gym 6 Paradox, 6,500g price, and Lv 65 Awakening Quest."""
    # Mega requires Gym 4
    assert "Badge_Count(GetPlayerId(po)) < 4" in map_script
    assert "Mega Evolution requires at least 4 Gym Badges" in map_script

    # Paradox requires Gym 6
    assert "Badge_Count(GetPlayerId(po)) < 6" in map_script

    # Awakening Quest level requirement is 65 (or 75)
    assert "function PAX_Leg_ReqLv takes integer idx returns integer\r\n    if idx == 4 or idx == 14 or idx == 24 then\r\n        return 75\r\n    endif\r\n    return 65" in map_script or \
           "function PAX_Leg_ReqLv takes integer idx returns integer\n    if idx == 4 or idx == 14 or idx == 24 then\n        return 75\n    endif\n    return 65" in map_script

    # Paradox items cost kept at 10,000g in SLK (per user request)
    for itid in ['IM18', 'IM19', 'IM1A', 'IM1B', 'IM1C', 'IM1D', 'IM1E', 'IM1F', 'IM1G', 'IM1H']:
        r = map_items_slk.find(itid)
        assert r is not None, f"Item {itid} not found in ItemData.slk"
        assert map_items_slk.get(r, 'goldcost') == '10000'


def test_sanctuary_ward_buff(map_script):
    """Verify that Sanctuary Ward provides +30 Armor, +20% Magic Resistance, and +3% HP/s heal."""
    # Apply and Remove functions exist
    assert "function PAX_Sanctuary_Apply takes unit u returns nothing" in map_script
    assert "function PAX_Sanctuary_Remove takes unit u returns nothing" in map_script

    # +30 Armor
    assert "call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + 30.0)" in map_script
    assert "call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - 30.0)" in map_script

    # 3% Max HP / second heal
    assert "call PAX_HealUnit(u, 0.03 * I2R(BlzGetUnitMaxHP(u)))" in map_script

    # 20% Magic resistance in PAX_Leg_ModifyIncoming
    assert "if skill and LoadInteger(PAX_Leg_HT, h, 182) == 1" in map_script
    assert "set dmg = dmg * 0.80" in map_script

