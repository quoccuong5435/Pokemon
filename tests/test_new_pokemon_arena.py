"""Verification suite for New Pokemon Arena 1.0 (v4.2 + v4.3c + 104-line Form Roster & Expansion)."""
import os
import re
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPS = os.path.dirname(WORK)
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import build_npa10  # noqa: E402
import form_assets  # noqa: E402
import form_roster  # noqa: E402

BASE_MAP = build_npa10.BASE_MAP
pytestmark = pytest.mark.skipif(not os.path.isfile(BASE_MAP), reason="v4.2 base map not here")


@pytest.fixture(scope="module")
def built_data():
    base, files, _dels, opt_stats, script = build_npa10.build_data(optimize_assets=False, dev_mode=True)
    return files, opt_stats, script


def test_preserves_v42_custom_features(built_data):
    _files, _stats, script = built_data
    s = script.replace("\r\n", "\n")
    for marker in (
        "function PAX_Arena_Start",
        "function PAX_Solo_CanStart",
        "function PAX_Forge_Near",
        "real Wild_Respawn = 25.0",
        "function PAX_Loot_CampFactor",
        "function Wild_IsParadoxSoul",
        "return 0.40 * RW_HealMult(u)",
        "No Player-ID lock",
    ):
        assert marker in s, f"Missing preserved v4.2 marker: {marker}"


def test_ports_v43c_features(built_data):
    _files, _stats, script = built_data
    s = script.replace("\r\n", "\n")
    for marker in (
        "function PAX_HeroMegaUnlock_OnLearn",
        "function PAX_ReviveWatchdog_Step",
        "function PAX_CleanseAllDebuffs",
        "function PAX_MidChat",
        "function MT_Build",
        "function GA_Shred",
        "function BossIso_IsLegend",
        "function HiddenAb_InitIdx",
        "function RW_Init",
        "function Wild_PickUniqueType",
        "function G14_Data27",
    ):
        assert marker in s, f"Missing ported v4.3c marker: {marker}"


def test_roster_and_wild_pool_filtered_to_104_lines(built_data):
    files, _stats, script = built_data
    s = script.replace("\r\n", "\n")
    assert "function Roster_FilterWild" in s
    assert "call ExecuteFunc(\"Roster_FilterWild\")\n    call ExecuteFunc(\"Wild_IndexPool\")" in s
    drop = form_roster.start_exclude()
    pick_body = re.search(r"function Pick_InitData takes nothing returns nothing\n([\s\S]*?)\nendfunction", s).group(1)
    assert not (set(re.findall(r"set Pick_Type\[\d+\] = '(\w{4})'", pick_body)) & drop)
    assert not (set(re.findall(r"set Rand_Type\[[^\]]+\] = '(\w{4})'", s)) & drop)
    # Taverns clean
    import objdata
    w3u = objdata.ObjFile(files["war3map.w3u"])
    for o in w3u.all():
        v = o.get("useu")
        if v:
            assert not ({x for x in str(v).split(",") if x} & drop)


def test_form_expansion_objects_hidden_power_and_show_command(built_data):
    files, opt_stats, script = built_data
    s = script.replace("\r\n", "\n")
    assert opt_stats["form_models"] == 105
    fs = opt_stats["form_stats"]
    assert fs["new_megas"] == 28
    assert fs["gmax_skins"] == 12
    assert fs["paradox_skins"] == 11
    assert fs["hero_forms"] == 52
    assert "set Mega_N = 72" in s
    assert "function Gmax_SkinId" in s
    assert "function Form_IsFinalHP" in s
    assert "function Form_QuestIdx" in s
    assert "function Form_ShowAll" in s
    assert "return 58" in s  # PAX_Leg_Count
    assert 'TriggerRegisterPlayerChatEvent(t, Player(0), "-show", true)' in s
    assert 'TriggerRegisterPlayerChatEvent(t, Player(0), "-clear", true)' in s
    # Verify IRGC & IFSW sold in n00Q
    import objdata
    w3u = objdata.ObjFile(files["war3map.w3u"])
    shop = next(u for u in w3u.all() if u.id == "n00Q")
    usei = str(shop.get("usei") or "")
    assert "IRGC" in usei and "IFSW" in usei and "IDMX" in usei
    # Verify every new PF* hero has valid umvt (foot or fly, never hover) and umvh <= 100
    for u in w3u.custom:
        if u.id.startswith("PF"):
            umvt = str(u.get("umvt") or "")
            umvh = float(u.get("umvh") or 0.0)
            assert umvt in ("foot", "fly"), (u.id, umvt)
            assert 0.0 <= umvh <= 100.0, (u.id, umvh)
            if umvt == "foot":
                assert umvh == 0.0, (u.id, umvh)


def test_105_active_form_metadata():
    _files, meta = form_assets.load_form_assets(compress_blp=False, pack_files=False)
    assert len(meta) == 105
