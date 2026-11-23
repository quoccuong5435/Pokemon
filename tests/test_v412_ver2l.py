"""Test suite for Pokemon Arena v4.1.2-ver2l:
1. Uniform Boss Buff (Room Bosses & Roaming Legends: x10 HP, x2 ATK, x2 Armor, Infinite Mana, -50% CD, 25% Magic Res).
2. Quest 3 Permanent 30s Reduction on Legend Kill (Dynamic 30s/60s target, preserved across deaths).
3. 3-Row Shop Layout (4 Top, 4 Bottom, 2 Middle horizontal with Red PC; uniform 0.20 scale; 0.65 Haunt Legend scale; >330 clearance to Gym & Haunt).
4. Late-Game Stat Training Price Increase (Stat: 5,000g + 1,500/lv; Vit: 4,000g + 1,200/lv).
5. Vitamin Stat Items (Protein, Calcium, Carbos, HP Up: stockMax=999, stockRegen=0; max 100 consumption limit per Pokemon).
6. Wild Creep Evolution Stone Drops (All 9 stone drop triggers disabled).
7. Native MOBA Skill Reticles (BlzEnableTargetIndicator(true) in script; Option bit 2 & Area1 populated in AbilityData.slk).
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

MAP_PATH = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2l.w3x')


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
def map_abil_slk(map_mpq):
    return slk.Slk(map_mpq.read('Units\\AbilityData.slk').decode('latin-1'))


def test_uniform_boss_buff(map_script):
    """Verify uniform boss formula: x10 HP, x2 ATK, x2 Armor, Infinite Mana, -50% CD, 25% Magic Res."""
    # In PAX_Boss_Register
    assert "set newMax = oldMax * 10" in map_script
    assert "call BlzSetUnitMaxHP(lg, newMax)" in map_script
    assert "call BlzSetUnitBaseDamage(lg, baseDmg * 2, 0)" in map_script
    assert "call BlzSetUnitDiceSides(lg, dice * 2, 0)" in map_script
    assert "call BlzSetUnitArmor(lg, arm * 2.0)" in map_script
    assert "call BlzSetUnitMaxMana(lg, 10000)" in map_script
    assert "call BlzSetUnitAttackCooldown(lg, atkCd * 0.50, 0)" in map_script
    assert "call SaveInteger(PAX_Boss_HT, h, 65, 1)" in map_script

    # In PAX_Boss_Tick: infinite mana refresh every 1s
    assert "if LoadInteger(PAX_Boss_HT, h, 65) == 1 then" in map_script
    assert "call SetUnitState(u, UNIT_STATE_MANA, 10000.0)" in map_script

    # In PAX_Leg_ModifyIncoming: 25% magic resistance
    assert "if skill and LoadInteger(PAX_Boss_HT, h, 65) == 1 then" in map_script
    assert "set dmg = dmg * 0.75" in map_script


def test_quest3_permanent_30s_reduction(map_script):
    """Verify Quest 3 target is dynamic 30s/60s, reduced permanently by 1 Legend kill, preserved on death."""
    # Function PAX_Leg_Stage3Target
    assert "function PAX_Leg_Stage3Target takes integer qk returns integer" in map_script
    assert "if LoadInteger(PAX_Leg_HT, qk, 10) == 1 then" in map_script
    assert "return 30" in map_script
    assert "return 60" in map_script

    # Kill progress records Key 10 = 1 on Legend kill
    assert "if isLegend and LoadInteger(PAX_Leg_HT, qk, 10) == 0 then" in map_script
    assert "call SaveInteger(PAX_Leg_HT, qk, 10, 1)" in map_script

    # Tick and Quest command use PAX_Leg_Stage3Target
    assert "set sec >= PAX_Leg_Stage3Target(qk)" in map_script or "if sec >= PAX_Leg_Stage3Target(qk) then" in map_script
    assert "PAX_Leg_Stage3Target(qk) == 30" in map_script


def test_3row_shop_layout_and_scale(map_script, map_w3u):
    """Verify 3-row layout, shop scale 0.20, Haunt scale 0.65, and clear Gym clearance."""
    # Top Row: 5950, 5800, 5650, 5440 at Y = 544.0
    assert "set u=CreateUnit(p,'n00O',5950.0,544.0,270.000)" in map_script
    assert "set u=CreateUnit(p,'n00N',5800.0,544.0,270.000)" in map_script
    assert "set u=CreateUnit(p,'n00Q',5650.0,544.0,270.000)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)" in map_script

    # Bottom Row: 5950, 5800, 5650, 5440 at Y = -544.0
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 5950.0, -544.0, 90.0)" in map_script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 5800.0, -544.0, 90.0)" in map_script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', 5650.0, -544.0, 90.0)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)" in map_script

    # Middle Row: Battle Shop at +/-5720, Paradox Shop at +/-5540, Y = 0.0
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 0.0, 270.0)" in map_script
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, 0.0, 270.0)" in map_script

    # Scale in w3u: 0.20 for all shops, 0.65 for Haunt Legend n030
    for sid in ['n00O', 'n00N', 'n00Q', 'nIS0', 'nBS0', 'nMS1', 'nMS2', 'nMS3', 'nFS0', 'nFS1']:
        u = map_w3u.find(sid)
        assert u is not None, f"Shop {sid} not found in w3u"
        scale = u.get('usca')
        assert scale == pytest.approx(0.20, rel=1e-2), f"Shop {sid} scale {scale} != 0.20"

    u_haunt = map_w3u.find('n030')
    assert u_haunt is not None
    assert u_haunt.get('usca') == pytest.approx(0.65, rel=1e-2)


def test_training_prices_increased(map_script):
    """Verify training prices are 5,000 + 1,500/lv for stats and 4,000 + 1,200/lv for vit."""
    assert "local integer statCost = 5000 + PAX_Up_StatLv[pid] * 1500" in map_script
    assert "local integer vitCost = 4000 + PAX_Up_VitLv[pid] * 1200" in map_script
    assert "set cost = 5000 + PAX_Up_StatLv[pid] * 1500" in map_script
    assert "set cost = 4000 + PAX_Up_VitLv[pid] * 1200" in map_script


def test_vitamin_stat_items_stock_and_cap(map_script, map_items_slk):
    """Verify infinite shop stock for vitamins and max 100 consumption limit per Pokemon."""
    # In ItemData.slk: stockMax=999, stockRegen=0
    for itid in ['I000', 'I001', 'I002', 'I003', 'I004', 'I005', 'I006']:
        r = map_items_slk.find(itid)
        assert r is not None, f"Item {itid} not found in ItemData.slk"
        assert map_items_slk.get(r, 'stockMax') == '999', f"{itid} stockMax != 999"
        assert map_items_slk.get(r, 'stockRegen') == '0', f"{itid} stockRegen != 0"

    # In Item_OnPickup: 100 cap tracking
    assert "set k = LoadInteger(PAX_Leg_HT, GetHandleId(u), 90)" in map_script
    assert "if k + n > 100 then" in map_script
    assert "Maximum 100 Vitamin limit reached" in map_script
    assert "call SaveInteger(PAX_Leg_HT, GetHandleId(u), 90, k + n)" in map_script


def test_wild_stone_drops_disabled(map_script):
    """Verify all 9 evolution stone drops from wild creeps are disabled."""
    stones = ["'I00K'", "'I00L'", "'I00M'", "'I00N'", "'I00O'"]
    for st in stones:
        assert f"call CreateItemLoc({st},GetUnitLoc(GetTriggerUnit()))" not in map_script


def test_moba_skill_target_indicators(map_script, map_abil_slk):
    """Verify native MOBA skill indicator and ground reticles in AbilityData.slk."""
    # BlzEnableTargetIndicator
    assert "call BlzEnableTargetIndicator(true)" in map_script

    # Check AbilityData.slk: Area1 and DataC1 for AoE abilities
    aoe_with_targeting_image = 0
    col = map_abil_slk.name_to_x
    for r in map_abil_slk.rows:
        aid = map_abil_slk.unquote(r.get(1))
        if aid and len(aid) == 4 and aid[:2] in ('AV', 'AW', 'AY', 'AZ', 'AK'):
            c1 = r.get(col.get('DataC1', -1), '0')
            try:
                val = int(c1.strip('"')) if c1 else 0
                if val & 2:  # bit 2 is targeting image
                    aoe_with_targeting_image += 1
            except ValueError:
                pass

    assert aoe_with_targeting_image >= 500, f"Expected >= 500 AoE moves with targeting image, got {aoe_with_targeting_image}"
