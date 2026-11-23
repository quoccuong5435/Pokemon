"""Automated pytest suite for Pokemon Arena v4.1.2-ver2m.
Verifies all 7 core features:
1. Vertical shop alignment with PC Center along back wall (X = +/-5950.0, Y = +/-240.0).
2. MOBA target indicator fix: Line moves (Quick Attack) have Bit 2 OFF; Area AoE moves have Bit 2 ON.
3. Celebi (n035) boss death drop trigger (ISCE soul and candies).
4. Haunt Legend Mid Teleport (IL02 item and step-on Circle of Power).
5. Soulbound 120s timer and unbound Legend drop on death.
6. Command Card PAXT attribute & type status icon at (Row 1, Col 1) and chat help.
7. Custom VFX assets from Tranquil and Wight packs packaged into map MPQ.
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
import slk  # noqa: E402
import objdata  # noqa: E402

MAP_PATH = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2m.w3x')


@pytest.fixture(scope="module")
def map_mpq():
    assert os.path.exists(MAP_PATH), f"Target map not found: {MAP_PATH}"
    return mpq.MPQ(MAP_PATH)


@pytest.fixture(scope="module")
def map_script(map_mpq):
    return map_mpq.read('scripts\\war3map.j').decode('latin-1')


@pytest.fixture(scope="module")
def map_abil(map_mpq):
    return slk.Slk(map_mpq.read('Units\\AbilityData.slk').decode('latin-1'))


@pytest.fixture(scope="module")
def map_items(map_mpq):
    return slk.Slk(map_mpq.read('Units\\ItemData.slk').decode('latin-1'))


@pytest.fixture(scope="module")
def map_w3u(map_mpq):
    return objdata.ObjFile(map_mpq.read('war3map.w3u'))


@pytest.fixture(scope="module")
def map_strings(map_mpq):
    return map_mpq.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')


def test_shop_vertical_alignment(map_script):
    """Verify Battle Shop (+240) and Paradox Shop (-240) are aligned along back wall with PC Center (5950)."""
    assert "set x = sx * 5950.0" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 240.0, face)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -240.0, face)" in map_script
    # Middle courtyard is clear
    assert "Ext_ShopSpot" not in map_script or "5720.0" not in map_script


def test_moba_target_indicator_aoe_vs_line(map_abil):
    """Verify only Area AoE moves get bit 2, while Line (Quick Attack) moves strip bit 2."""
    col = map_abil.name_to_x
    c1_x = col.get('DataC1')
    assert c1_x is not None

    # AV0L is Blast Burn (tt == 2 Area AoE) -> Bit 2 must be ON (c1_val == 3)
    # AV04 is Aerial Ace (tt == 3 Line) -> Bit 2 must be OFF (c1_val == 1)
    blast_row = map_abil.find('AV0L')
    assert blast_row is not None
    c1_val = int(blast_row.get(c1_x, '1').strip('"'))
    assert (c1_val & 2) == 2, "Blast Burn (Area AoE) must have Bit 2 (Targeting Image) set"

    aerial_row = map_abil.find('AV04')
    assert aerial_row is not None
    c1_aerial = int(aerial_row.get(c1_x, '1').strip('"'))
    assert (c1_aerial & 2) == 0, "Aerial Ace (Line) must NOT have Bit 2 set"


def test_celebi_soul_drop(map_script):
    """Verify Celebi (n035) has death trigger that drops ISCE and stat boosters."""
    assert "function PAX_CelebiDeathCondition" in map_script
    assert "GetUnitTypeId(GetTriggerUnit()) == 'n035'" in map_script
    assert "call CreateItem('ISCE', x, y)" in map_script
    assert "PAX_CelebiDeathInit" in map_script


def test_haunt_legend_mid_teleport(map_script, map_items, map_w3u):
    """Verify IL02 item and ground Circle of Power teleport to (-128.0, 16.0)."""
    # Item in slk
    il02_row = map_items.find('IL02')
    assert il02_row is not None

    # Item in Haunt Legend usei
    u_haunt = map_w3u.find('n030')
    assert u_haunt is not None
    assert 'IL02' in u_haunt.get('usei')

    # Script sell handler
    assert "elseif it == 'IL02' then" in map_script
    assert "call SetUnitPosition(b, -128.0, 16.0)" in map_script

    # Ground portal check in script
    assert "PAX_HauntPortalTick" in map_script
    assert "To Mid" in map_script


def test_soulbound_and_legend_drop(map_script):
    """Verify 120s soulbound timer, pickup reject, and unbound legend drop on death."""
    assert "PAX_IsSoulboundProtectedItem" in map_script
    assert "PAX_SoulboundTick" in map_script
    assert "Mega_Time - timeHeld >= 120.0" in map_script
    assert "[SOULBOUND] This item belongs to Player" in map_script
    assert "[LEGEND DROP]" in map_script


def test_paxt_command_card_attribute_icon(map_abil, map_strings, map_script):
    """Verify PAXT ability is at Buttonpos 1, 1 with full formula and type chart."""
    paxt_row = map_abil.find('PAXT')
    assert paxt_row is not None

    # Strings definition contains Buttonpos=1,1
    assert "[PAXT]" in map_strings
    assert "Buttonpos=1,1" in map_strings
    assert "Pokemon Type & Attributes [T]" in map_strings
    assert "DAMAGE SCALING FORMULAS" in map_strings
    assert "Physical Moves:|r Base Dmg x (|cffff8000STR|r / 50.0)" in map_strings

    # Added to Pokemon in script
    assert "call UnitAddAbility(u, 'PAXT')" in map_script
    assert "PAX_InitChatHelp" in map_script
    assert "-stat" in map_script
    assert "-type" in map_script


def test_custom_vfx_assets(map_mpq):
    """Verify Tranquil and Wight models and icons are packed into the map."""
    listfile = {f.lower() for f in map_mpq.listfile()}
    assert "spells\\tranquil\\stun small.mdx" in listfile
    assert "spells\\tranquil\\shield buff.mdx" in listfile
    assert "spells\\tranquil\\fire nova.mdx" in listfile
    assert "spells\\tranquil\\frost nova.mdx" in listfile
    assert "spells\\wight\\handofdeath.mdx" in listfile
    assert "spells\\wight\\stranglehold.mdx" in listfile
    assert "spells\\wight\\spiritbolt.mdx" in listfile
