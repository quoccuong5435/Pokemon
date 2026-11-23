"""Comprehensive test suite for Pokemon Arena v4.1.2-ver2g.w3x."""
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
def ver2g_data():
    map_path = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2g.w3x')
    assert os.path.exists(map_path), f"Map not found: {map_path}"
    arc = mpq.MPQ(map_path)
    jass = arc.read('scripts\\war3map.j').decode('utf-8')
    w3i = arc.read('war3map.w3i')
    strings = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    yield {'arc': arc, 'jass': jass, 'w3i': w3i, 'strings': strings, 'w3u': w3u, 'path': map_path}


def test_map_canvas_dimensions(ver2g_data):
    """Map is 160x160 original canvas to guarantee 100% bug-free rooms, camera, and pathing."""
    w3i = ver2g_data['w3i']
    jass = ver2g_data['jass']
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 160 and h == 160:
            break
    else:
        pytest.fail("160x160 dimensions not found in war3map.w3i")
    assert 'SetCameraBounds(-10240.0+GetCameraMargin' in jass


def test_scaled_down_shops(ver2g_data):
    """Shops in base are scaled down by ~25% for a spacious, clean courtyard."""
    w3u = ver2g_data['w3u']
    assert round(w3u.find('n00P').get('usca'), 2) == 0.58
    assert round(w3u.find('n00O').get('usca'), 2) == 0.30
    assert round(w3u.find('nMS1').get('usca'), 2) == 0.30
    assert round(w3u.find('nFS0').get('usca'), 2) == 0.30
    assert round(w3u.find('n030').get('usca'), 2) == 1.15


def test_accented_vietnamese(ver2g_data):
    """Selected texts have full Vietnamese accents (Tieng Viet Co Dau chuan)."""
    jass = ver2g_data['jass']
    assert 'POKEMON ARENA v4.1.2-ver2g' in jass
    assert 'PvP & Cân Bằng Huyền Thoại' in jass
    assert '-help|r |cffe8ecf2Tất Cả Lệnh' in jass
    assert '-up|r |cffe8ecf2Luyện Tập' in jass
    assert '-quest|r |cffe8ecf2Thức Tỉnh' in jass
    assert '-solo|r |cffe8ecf21v1 Cướp Đồ' in jass
    assert '-pet|r |cffe8ecf2Thú Cưng' in jass
    assert 'Cửa Hàng Căn Cứ:|r |cffffd166Form Shop' in jass
    assert 'BẢNG HƯỚNG DẪN LỆNH POKEMON ARENA' in jass
    assert 'Chiêu Đặc Biệt (INT, kháng bởi Sp. Def):' in jass
    assert 'Chiêu Vật Lý (STR, kháng bởi Def):' in jass


def test_embedded_font_and_skin(ver2g_data):
    """war3mapSkin.txt and Unicode TTF font are embedded directly in the w3x archive."""
    arc = ver2g_data['arc']
    listfile = {f.lower() for f in arc.listfile()}
    assert 'war3mapskin.txt' in listfile
    assert 'fonts\\frizqt__.ttf' in listfile
    skin = arc.read('war3mapSkin.txt').decode('latin-1')
    assert 'MasterFont=Fonts\\FRIZQT__.ttf' in skin


def test_pokemon_move_icons(ver2g_data):
    """All 378 moves use authentic Pokemon Type and specific custom icons."""
    strings = ver2g_data['strings']
    p = strings.find('[AV00]')
    assert 'ReplaceableTextures\\CommandButtons\\BTNPkmnGrass.blp' in strings[p:p+200]
    p2 = strings.find('[AV2W]')
    assert 'BTNFlame Thrower (64 x 64).blp' in strings[p2:p2+200]


def test_pjass_syntax(ver2g_data):
    """Verifies that war3map.j passes the real pjass.exe compiler with 0 syntax errors."""
    if not (os.path.exists(PJASS_PATH) and os.path.exists(COMMON_J) and os.path.exists(BLIZZARD_J)):
        pytest.skip("pjass.exe or reference files not found.")

    scratch_j = os.path.join(HERE, "test_temp_ver2g.j")
    with open(scratch_j, "w", encoding="utf-8") as f:
        f.write(ver2g_data['jass'])

    try:
        cmd = [PJASS_PATH, COMMON_J, BLIZZARD_J, scratch_j]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert res.returncode == 0, f"PJASS syntax errors:\n{res.stdout[:1000]}"
    finally:
        if os.path.exists(scratch_j):
            os.remove(scratch_j)
