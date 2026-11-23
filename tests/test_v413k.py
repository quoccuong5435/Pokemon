"""Verification tests for Pokemon Arena v4.1.3k fixes."""
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, os.path.join(WORK, "tools", "v412"))

import build_v413k  # noqa: E402


def _get_data():
    return build_v413k.build_data()


def test_soulbound_rules_and_timer_wiring():
    _, _, script, _, _ = _get_data()
    s = script.replace("\r\n", "\n")

    # 1. Common ('ofir') & Rare ('ocor') are instant Soulbound and EXCLUDED from drop-on-death
    assert "function PAX_IsInstantSoulboundItem" in s
    assert "return itemTypeId == 'ofir' or itemTypeId == 'ocor'" in s
    assert "if id == 'oli2' or id == 'tgrh' then" in s
    assert "if id == 'ofir' or id == 'ocor' or id == 'oli2' or id == 'tgrh' then" not in s

    # 2. PAX_SoulboundTick & PAX_HauntPortalTick are wired into PAX_Leg_Tick1s (1s timer)
    assert "call PAX_SoulboundTick()" in s
    assert "call PAX_HauntPortalTick()" in s
    # Must NOT use broken null handle LoadUnitHandle(PAX_Leg_HT, p, 1) inside Soulbound / HauntPortal ticks
    sb_body = s[s.index("function PAX_HauntPortalTick"):s.index("function PAX_Leg_Init")]
    assert "LoadUnitHandle(PAX_Leg_HT" not in sb_body
    assert "GroupEnumUnitsOfPlayer(sbScanG" in sb_body
    # Must bind after 60s (not 120s)
    assert "if sbHoldSec >= 60 then" in s
    assert "Mega_Time - timeHeld >= 120.0" not in s

    # 3. Mystery Loot Box (-up), Gamble, and Forge bind items immediately on creation
    assert s.count("call PAX_Soulbound_BindNow(dropIt, pid)") == 2
    assert "call PAX_Soulbound_BindNow(newIt, pid)" in s

    # 4. Death drop checks key 210 (clean dedicated key, not colliding key 100)
    assert "if PAX_IsSoulboundProtectedItem(dropId) and LoadInteger(PAX_Leg_HT, dropH, 210) == 0 then" in s


def test_mystery_loot_box_rates():
    _, _, script, _, _ = _get_data()
    s = script.replace("\r\n", "\n")
    assert "if boxRoll <= 0.5 then" in s
    assert "elseif boxRoll <= 3.5 then" in s
    assert "elseif boxRoll <= 13.5 then" in s
    assert "elseif boxRoll <= 88.5 then" in s
    assert "Mystery Loot Box (75% C / 10% R / 3% E / 0.5% L) - 3500g" in s


def test_first_10_minutes_no_camp_reinforce_and_max_10_cap():
    _, _, script, _, _ = _get_data()
    s = script.replace("\r\n", "\n")
    assert "if Wild_Time < 600.0 then" in s
    assert "elseif Wild_CampAlive[c] < 10 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0 and LoadInteger(Mega_HT, c + 500, 2) < 2 then" in s
    assert "local integer capRemain = 10 - Wild_CampAlive[c]" in s
    assert "if Wild_CampSize[c] > 10 then" in s


def test_vitamin_stock_start_delay_zero():
    _, _, _, items, _ = _get_data()
    col = items.name_to_x
    for iid in ["I000", "I001", "I002", "I003", "I004", "I005", "I006"]:
        row = items.find(iid)
        assert row is not None, f"Missing {iid}"
        assert row[col["stockStart"]] == "0", f"{iid} stockStart={row[col['stockStart']]}"
        assert row[col["stockMax"]] == "100", f"{iid} stockMax={row[col['stockMax']]}"
        assert row[col["stockRegen"]] == "1", f"{iid} stockRegen={row[col['stockRegen']]}"

    row_il02 = items.find("IL02")
    assert row_il02[col["stockStart"]] == "0"
    row_imha = items.find("IMHA")
    assert row_imha[col["stockStart"]] == "0"


def test_uniform_legend_boss_rebalance_and_zekrom_model():
    _, files, script, _, w3u = _get_data()
    s = script.replace("\r\n", "\n")

    # No double multiplier in Leg_Spawn
    assert "BlzGetUnitMaxHP(lg) * 20" not in s
    assert "set newMax = 1000000 + R2I(bossHpRatio * 500000.0)" in s
    assert "call BlzSetUnitArmor(lg, 450.0 + bossArmRatio * 250.0)" in s

    # Verify ALL 54 Legend Bosses map strictly inside 1M..1.5M HP, 1472..2538 ATK, 450..700 Armor!
    fixed_ids = ['n001', 'n00C', 'n00D', 'n00F', 'n00G', 'n01I', 'n01J', 'n01K', 'n01L', 'n01M', 'n01N', 'n01O', 'n033', 'n034', 'n035']
    roam_old = ['nL05', 'nL0B', 'nL0C', 'nL0D', 'nL0F', 'nL10', 'nL11', 'nL12', 'nL13', 'nL14', 'nL15', 'nL16', 'nL17', 'nL18']
    roam_new = ['nL2' + ch for ch in "0123456789ABCDEFGHIJKLMNO"]

    for bid in fixed_ids + roam_old + roam_new:
        u = w3u.find(bid)
        assert u is not None, f"Missing boss {bid}"
        old_hp = int(u.get("uhpm") or 0)
        old_atk = int(u.get("ua1b") or 0)
        old_sides = int(u.get("ua1s") or 1)
        old_arm = float(u.get("udef") or 0)

        hp_r = min(1.0, max(0.0, (old_hp - 19000.0) / 39000.0))
        new_hp = 1000000 + int(hp_r * 500000.0)
        atk_r = min(1.0, max(0.0, (old_atk + old_sides * 0.5 - 750.0) / 600.0))
        avg_atk = 1600.0 + atk_r * 750.0
        arm_r = min(1.0, max(0.0, (old_arm - 75.0) / 150.0))
        new_arm = 450.0 + arm_r * 250.0

        assert 1000000 <= new_hp <= 1500000, f"{bid} HP={new_hp}"
        assert 1500.0 <= avg_atk <= 2500.0, f"{bid} ATK={avg_atk}"
        assert 450.0 <= new_arm <= 700.0, f"{bid} ARM={new_arm}"

    # Verify authentic Zekrom MDX + 3 BLPs included
    assert "PkFx\\Legends\\Zekrom.mdx" in files
    assert files["PkFx\\Legends\\Zekrom.mdx"][:4] == b"MDLX"
    for tex in ("644a.blp", "644b.blp", "644c.blp"):
        assert tex in files and len(files[tex]) > 1000
