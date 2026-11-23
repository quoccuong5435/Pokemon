"""Comprehensive test suite for Pokemon Arena v4.1.2-ver2i.w3x."""
import os
import re
import struct
import subprocess
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq, objdata

PJASS_PATH = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
COMMON_J = os.path.join(WORK, "analysis", "jass_ref", "common.j")
BLIZZARD_J = os.path.join(WORK, "analysis", "jass_ref", "blizzard.j")


@pytest.fixture(scope="module")
def ver2i_data():
    map_path = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2i.w3x')
    assert os.path.exists(map_path), f"Map not found: {map_path}"
    arc = mpq.MPQ(map_path)
    jass = arc.read('scripts\\war3map.j').decode('utf-8')
    w3i = arc.read('war3map.w3i')
    strings = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    yield {'arc': arc, 'jass': jass, 'w3i': w3i, 'strings': strings, 'w3u': w3u, 'path': map_path}


def test_map_canvas_dimensions(ver2i_data):
    """Map is 160x160 original canvas."""
    w3i = ver2i_data['w3i']
    jass = ver2i_data['jass']
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 160 and h == 160:
            break
    else:
        pytest.fail("160x160 dimensions not found in war3map.w3i")
    assert 'SetCameraBounds(-10240.0+GetCameraMargin' in jass


def test_tight_adjacent_shops(ver2i_data):
    """Shops are tightly adjacent (xát nhau) with 160 spacing and unblocked."""
    jass = ver2i_data['jass']
    # Mart shops tight row
    assert "-5960.0,544.0" in jass
    assert "-5800.0,544.0" in jass
    assert "-5640.0,544.0" in jass

    # Mega shops tight row
    assert "nMS1', -5960.0, -544.0" in jass
    assert "nMS2', -5800.0, -544.0" in jass
    assert "nMS3', -5640.0, -544.0" in jass

    # Form & Paradox shops completing the 5-shop row
    assert "sx * 5480.0" in jass
    assert "sx * 5320.0" in jass


def test_league_portal_removed_from_base(ver2i_data):
    """League portal CircleOfPower and label are completely removed from base."""
    jass = ver2i_data['jass']
    assert "League base portal completely removed" in jass
    assert "call Fx_Label(\"League\", gx, gy, 255, 204, 0)" not in jass


def test_relic_forge_penalty_30_70(ver2i_data):
    """Relic Forge failure penalty: 30% drop 1 level, 70% keep current level."""
    jass = ver2i_data['jass']
    assert "GetRandomInt(1, 100) <= 30" in jass
    assert "Failed (30% penalty)! Item dropped to +" in jass
    assert "Failed (70% safe)! Item retained safely at +" in jass


def test_fixed_debuff_icons_no_double_backslash(ver2i_data):
    """Buffart paths have single backslash, resolving green box for Sp. Def lowered."""
    strings = ver2i_data['strings']
    idx = strings.find('[BF1I]')
    assert idx != -1
    section = strings[idx:idx+250]
    assert 'Buffart=ReplaceableTextures\\CommandButtons\\BTNSilence.blp' in section
    assert 'ReplaceableTextures\\\\' not in section


def test_pjass_syntax(ver2i_data):
    """Verifies that war3map.j passes the real pjass.exe compiler with 0 syntax errors."""
    if not (os.path.exists(PJASS_PATH) and os.path.exists(COMMON_J) and os.path.exists(BLIZZARD_J)):
        pytest.skip("pjass.exe or reference files not found.")

    scratch_j = os.path.join(HERE, "test_temp_ver2i.j")
    with open(scratch_j, "w", encoding="utf-8") as f:
        f.write(ver2i_data['jass'])

    try:
        cmd = [PJASS_PATH, COMMON_J, BLIZZARD_J, scratch_j]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert res.returncode == 0, f"PJASS syntax check failed:\n{res.stdout[:1500]}\n{res.stderr[:1500]}"
    finally:
        if os.path.exists(scratch_j):
            os.remove(scratch_j)
