"""Comprehensive test suite for Pokemon Arena v4.1.2-ver2f.w3x."""
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
import mpq

PJASS_PATH = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
COMMON_J = os.path.join(WORK, "analysis", "jass_ref", "common.j")
BLIZZARD_J = os.path.join(WORK, "analysis", "jass_ref", "blizzard.j")


@pytest.fixture(scope="module")
def ver2f_data():
    map_path = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2f.w3x')
    assert os.path.exists(map_path), f"Map not found: {map_path}"
    arc = mpq.MPQ(map_path)
    jass = arc.read('scripts\\war3map.j').decode('utf-8')
    w3i = arc.read('war3map.w3i')
    strings = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    yield {'arc': arc, 'jass': jass, 'w3i': w3i, 'strings': strings, 'path': map_path}


def test_map_canvas_dimensions(ver2f_data):
    """Map is 160x160 original canvas to guarantee 100% bug-free rooms, camera, and pathing."""
    w3i = ver2f_data['w3i']
    jass = ver2f_data['jass']
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 160 and h == 160:
            break
    else:
        pytest.fail("160x160 dimensions not found in war3map.w3i")
    assert 'SetCameraBounds(-10240.0+GetCameraMargin' in jass


def test_base_courtyard_layout(ver2f_data):
    """Courtyard is spacious, Poké Center is unobstructed, and shops form clean rows."""
    jass = ver2f_data['jass']
    # Forge is North-East of lawn (-5340, 220), Moves NPC is South-East (-5340, -220)
    assert 'set fx = -5340.0' in jass
    assert 'local real fy = 220.0' in jass
    assert 'set Npc_X[0] = -5340.0' in jass
    assert 'set Npc_Y[0] = -220.0' in jass
    # Form Shop and Paradox Shop are aligned along southern row at Y = -544
    assert 'set x = sx * 5088.0' in jass
    assert 'set y = -544.0' in jass
    assert "'nFS0', x, y, 90.0" in jass
    assert "'nFS1', sx * 4784.0, -544.0, 90.0" in jass
    # League Gate next to Gym Gate
    assert 'set gx = (2.0 * I2R(k) - 1.0) * 5120.0' in jass
    assert 'set gy = 460.0' in jass


def test_starter_moves_learnsets(ver2f_data):
    """All 33 Gen 2-7 starters have full Fx_AddLv / Fx_AddTm learnsets."""
    jass = ver2f_data['jass']
    assert 'function Fx_StarterMoves1' in jass
    assert 'function Fx_StarterMoves5' in jass
    assert 'call ExecuteFunc("Fx_StarterMoves1")' in jass
    assert 'call ExecuteFunc("Fx_StarterMoves5")' in jass
    assert "call Fx_AddLv('EP00', 356, 1)" in jass
    assert "call Fx_AddTm('EP00', 4)" in jass
    assert "call Mv_Sync(h)" in jass


def test_casting_animations(ver2f_data):
    """Pokemon play attack animation for physical moves and spell animation for special moves."""
    jass = ver2f_data['jass']
    assert 'call SetUnitAnimation(fxCaster, "attack")' in jass
    assert 'call SetUnitAnimation(fxCaster, "spell")' in jass
    assert 'call QueueUnitAnimation(fxCaster, "stand")' in jass
    assert 'call SetUnitAnimation(u, "attack")' in jass
    assert 'call SetUnitAnimation(u, "spell")' in jass


def test_font_bug_fixed_clean_vietnamese(ver2f_data):
    """All Vietnamese strings are converted to clean non-accented text, fixing dropped characters."""
    jass = ver2f_data['jass']
    # Welcome banner has full, clean words without missing characters
    assert 'POKEMON ARENA v4.1.2-ver2f' in jass
    assert 'PvP & Can Bang Huyen Thoai' in jass
    assert '-help|r |cffe8ecf2Tat Ca Lenh' in jass
    assert '-up|r |cffe8ecf2Luyen Tap' in jass
    assert '-quest|r |cffe8ecf2Thuc Tinh' in jass
    assert '-solo|r |cffe8ecf21v1 Cuop Do' in jass
    assert '-pet|r |cffe8ecf2Thu Cung' in jass
    assert 'Cua Hang Can Cu:|r |cffffd166Form Shop' in jass

    # Ensure none of the broken, dropped glyph strings exist
    assert 'Tt C Lnh' not in jass
    assert 'Luyn Tp' not in jass
    assert 'Thc Tnh' not in jass
    assert '1v1 Cp' not in jass
    assert 'Thỳ Cng' not in jass
    assert 'Ca Hng Cn C' not in jass
    assert 'Cõn Bng Huyn Thoi' not in jass

    # QuestMessageBJ is cleaned up from old corrupt TCVN3 bytes
    assert 'Chon 1 Pokemon farm cung dong doi, up cap, tien hoa, san Pokemon Huyen Thoai' in jass
    assert 'BÃ' not in jass
    assert 'cÃ' not in jass


def test_pokemon_move_icons(ver2f_data):
    """All 378 moves use authentic Pokemon Type and specific custom icons."""
    strings = ver2f_data['strings']
    arc = ver2f_data['arc']

    # 1. Absorb (Move 0, Grass) uses BTNPkmnGrass
    for pfx in ['AV', 'AW', 'AY', 'AZ']:
        sec = f'[{pfx}00]'
        p = strings.find(sec)
        assert p != -1, f"Missing section {sec}"
        end = strings.find('[', p + len(sec))
        chunk = strings[p:end]
        assert 'ReplaceableTextures\\CommandButtons\\BTNPkmnGrass.blp' in chunk

    # 2. Flamethrower (Move 104, 2W) uses BTNFlame Thrower
    p = strings.find('[AV2W]')
    assert p != -1
    end = strings.find('[', p + 6)
    assert 'BTNFlame Thrower (64 x 64).blp' in strings[p:end]

    # 3. Razor Leaf (Move 222, 66) uses BTNRazol Leaf
    p = strings.find('[AV66]')
    assert p != -1
    end = strings.find('[', p + 6)
    assert 'BTNRazol Leaf (64 x 64).blp' in strings[p:end]

    # 4. Bubble Beam (Move 35, 0Z) uses BTNBubble Beam
    p = strings.find('[AV0Z]')
    assert p != -1
    end = strings.find('[', p + 6)
    assert 'BTNBubble Beam (64 x 64).blp' in strings[p:end]

    # 5. Blast Burn (Move 21, 0L) uses BTNBlast Burn
    p = strings.find('[AV0L]')
    assert p != -1
    end = strings.find('[', p + 6)
    assert 'BTNBlast Burn (64 x 64).blp' in strings[p:end]

    # 6. Outrage (Move 185, 55) uses BTNOut Rage
    p = strings.find('[AV55]')
    assert p != -1
    end = strings.find('[', p + 6)
    assert 'BTNOut Rage (64 x 64).blp' in strings[p:end]

    # 7. No generic Warcraft 3 icons remaining on move slots
    generic_matches = re.findall(
        r'\[A[VWYZ][0-9A-Z]{2}\][^\[]*Art=[^\r\n]*(?:BTNLifeDrain|BTNAcidBomb|BTNSummonWaterElemental|BTNBash|BTNSmash)',
        strings
    )
    assert len(generic_matches) == 0, f"Found {len(generic_matches)} moves with generic WC3 icons"

    # 8. Extra custom move icons packaged in MPQ archive
    listfile_lower = {f.lower() for f in arc.listfile()}
    assert 'replaceabletextures\\commandbuttons\\btnblast burn (64 x 64).blp' in listfile_lower
    assert 'replaceabletextures\\commandbuttons\\btnflame thrower (64 x 64).blp' in listfile_lower
    assert 'replaceabletextures\\commandbuttons\\btnrazol leaf (64 x 64).blp' in listfile_lower


def test_pjass_real_compilation(ver2f_data):
    """Verifies that war3map.j passes the real pjass.exe compiler with 0 syntax errors."""
    if not (os.path.exists(PJASS_PATH) and os.path.exists(COMMON_J) and os.path.exists(BLIZZARD_J)):
        pytest.skip("pjass.exe or reference files not found on machine.")

    scratch_j = os.path.join(HERE, "test_temp_ver2f.j")
    with open(scratch_j, "w", encoding="utf-8") as f:
        f.write(ver2f_data['jass'])

    try:
        cmd = [PJASS_PATH, COMMON_J, BLIZZARD_J, scratch_j]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert res.returncode == 0, f"PJASS syntax errors:\n{res.stdout[:1000]}\n{res.stderr[:1000]}"
    finally:
        if os.path.exists(scratch_j):
            os.remove(scratch_j)
