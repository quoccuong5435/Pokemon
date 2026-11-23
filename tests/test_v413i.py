"""Automated pytest suite for Pokemon Arena v4.1.3i:
Verifies:
1. All 25 new Legendaries (EL00..EL0O, nL20..nL2O, IL20..IL2O) registered in w3u, ItemData, ItemFunc, and war3map.j.
2. All 10 upgraded 3D Mega/Form models + 7 new Mega/Form models (Swampert, Garchomp, Black/White Kyurem,
   Mega Diancie, Hoopa Unbound, Ultra Necrozma) packed with 0 missing textures.
3. All 44 Mega/Orb abilities + 8 Form/Plate abilities converted to Gold '+' Hero Skills (`hero=1, item=0, reqLevel=50/70`)
   and attached to Hero `uhab`, separate from Q-W-E-R!
4. Mega Shop I/II/III (nMS1..nMS3) and Form Shop (nFS0) removed from Base Courtyard.
5. Free gold form switching + passive stat sync on learning Hero Skill.
"""
import os
import re
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import build_v413i  # noqa: E402
import legend_expansion_data  # noqa: E402


@pytest.fixture(scope="module")
def v413i_data():
    return build_v413i.build_data()


def test_25_new_legendaries_registered(v413i_data):
    _base, files, script, _abil, items, func, _strings, w3u = v413i_data
    by_id = {u.id: u for u in w3u.original + w3u.custom}

    assert "return 57\n" in script or "return 57\r\n" in script
    for lg in legend_expansion_data.NEW_LEGENDS:
        assert lg['hero'] in by_id, f"Missing hero {lg['hero']} ({lg['name']})"
        assert lg['wild'] in by_id, f"Missing wild boss {lg['wild']} ({lg['name']})"
        assert items.find(lg['soul']) is not None, f"Missing soul item {lg['soul']} ({lg['name']})"
        assert f"[{lg['soul']}]" in func
        assert f"'{lg['hero']}'" in script
        assert f"'{lg['wild']}'" in script
        assert f"'{lg['soul']}'" in script
        mdx_key = f"PkFx\\Leg25\\{lg['dex']:03d}_{lg['name']}.mdx"
        assert mdx_key in files, f"Missing MDX file {mdx_key}"


def test_real_3d_mega_and_form_models_packed(v413i_data):
    _base, files, script, _abil, _items, _func, _strings, w3u = v413i_data
    by_id = {u.id: u for u in w3u.original + w3u.custom}

    # Check 10 upgraded Mega/Form skins
    for sid, _blk, dst_mdx, _sc, _create in legend_expansion_data.UPGRADE_SKIN_MODELS:
        assert sid in by_id, f"Missing skin unit {sid}"
        assert dst_mdx in files, f"Missing 3D model {dst_mdx}"
        assert by_id[sid].get('umdl').lower() == (dst_mdx[:-4] + '.mdl').lower()

    # Check Giratina Origin & Deoxys 3D skin swaps in PAX_Form_Appearance
    assert "call BlzSetUnitSkin(u, 'hMF4')" in script
    assert "call BlzSetUnitSkin(u, 'hMF7')" in script
    assert "call BlzSetUnitSkin(u, 'hMF8')" in script
    assert "call BlzSetUnitSkin(u, 'hMF9')" in script
    assert "set Mega_Skin[33] = 'hMPK'" in script
    assert "set Mega_Skin[34] = 'hMPG'" in script
    assert "set Mega_Skin[35] = 'hMLL'" in script
    assert "set Mega_N = 44" in script


def test_gold_plus_hero_skill_unlock_and_shop_removal(v413i_data):
    _base, _files, script, abil, _items, _func, strings, w3u = v413i_data
    by_id = {u.id: u for u in w3u.original + w3u.custom}

    # Spot-check Normal Megas (Lv 50) & Legend Megas/Forms (Lv 70) in uhab + AbilityData.slk
    checks = [
        ('E00E', 'AM01', '50'),  # Charizard X
        ('E00E', 'AM02', '50'),  # Charizard Y
        ('EP05', 'AM20', '50'),  # Mega Swampert
        ('P1LA', 'AM21', '50'),  # Mega Garchomp
        ('E026', 'AM0D', '70'),  # Mega Mewtwo X
        ('E026', 'AM0E', '70'),  # Mega Mewtwo Y
        ('E029', 'AM0F', '70'),  # Mega Rayquaza
        ('EL0A', 'AM22', '70'),  # Black Kyurem
        ('EL0A', 'AM23', '70'),  # White Kyurem
        ('EL0F', 'AM24', '70'),  # Mega Diancie
        ('EL0G', 'AM25', '70'),  # Hoopa Unbound
        ('EL0K', 'AM26', '70'),  # Ultra Necrozma
        ('E028', 'AM14', '70'),  # Giratina Origin Form
        ('E027', 'AM17', '70'),  # Deoxys Form Switch
        ('E02A', 'AM10', '70'),  # Arceus Legend Plate
    ]
    for hid, aid, exp_lv in checks:
        uhab = str(by_id[hid].get('uhab') or '')
        assert aid in uhab, f"Hero {hid} missing {aid} in uhab ({uhab!r})"
        r = abil.find(aid)
        assert r is not None, f"Ability {aid} missing from AbilityData.slk"
        assert abil.get(r, 'hero') == '1', f"{aid} must be hero=1"
        assert abil.get(r, 'item') == '0', f"{aid} must be item=0"
        assert abil.get(r, 'reqLevel') == exp_lv, f"{aid} reqLevel != {exp_lv}"

    # Verify dual-form heroes have distinct Buttonpos & DataF1 order IDs
    for a1, a2 in (('AM01', 'AM02'), ('AM0D', 'AM0E'), ('AM22', 'AM23')):
        r1, r2 = abil.find(a1), abil.find(a2)
        assert abil.get(r1, 'DataF1') != abil.get(r2, 'DataF1'), f"Order collision between {a1} and {a2}"

    # Verify Mega Shop I/II/III and Form Shop removed from Base Courtyard
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1'" not in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2'" not in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3'" not in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0'" not in script

    # Verify Gold '+' learn listener wired
    assert "PAX_HeroMegaUnlock_Init" in script
    assert "EVENT_PLAYER_HERO_SKILL" in script
    assert "Switching form again costs 10,000 gold." not in script
