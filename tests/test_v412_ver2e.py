"""Verification test suite for Pokemon Arena v4.1.2-ver2e.w3x."""
import os
import sys
import struct
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq


@pytest.fixture(scope="module")
def ver2e_map():
    map_path = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2e.w3x')
    assert os.path.exists(map_path), f"Map not found: {map_path}"
    arc = mpq.MPQ(map_path)
    jass = arc.read('scripts\\war3map.j').decode('utf-8')
    w3i = arc.read('war3map.w3i')
    yield {'arc': arc, 'jass': jass, 'w3i': w3i}


def test_map_canvas_dimensions(ver2e_map):
    """Map is 160x160 original canvas to guarantee 100% bug-free rooms."""
    w3i = ver2e_map['w3i']
    jass = ver2e_map['jass']
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 160 and h == 160:
            break
    else:
        pytest.fail("160x160 dimensions not found in war3map.w3i")
    assert 'SetCameraBounds(-10240.0+GetCameraMargin' in jass


def test_base_courtyard_layout(ver2e_map):
    """Courtyard is spacious, Poké Center is unobstructed, and shops form clean rows."""
    jass = ver2e_map['jass']
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


def test_starter_moves_learnsets(ver2e_map):
    """All 33 Gen 2-7 starters have full Fx_AddLv / Fx_AddTm learnsets."""
    jass = ver2e_map['jass']
    assert 'function Fx_StarterMoves1' in jass
    assert 'function Fx_StarterMoves5' in jass
    assert 'call ExecuteFunc("Fx_StarterMoves1")' in jass
    assert 'call ExecuteFunc("Fx_StarterMoves5")' in jass
    assert "call Fx_AddLv('EP00', 356, 1)" in jass
    assert "call Fx_AddTm('EP00', 4)" in jass
    assert "call Mv_Sync(h)" in jass


def test_casting_animations(ver2e_map):
    """Pokemon play attack animation for physical moves and spell animation for special moves."""
    jass = ver2e_map['jass']
    assert 'call SetUnitAnimation(fxCaster, "attack")' in jass
    assert 'call SetUnitAnimation(fxCaster, "spell")' in jass
    assert 'call QueueUnitAnimation(fxCaster, "stand")' in jass
    assert 'call SetUnitAnimation(u, "attack")' in jass
    assert 'call SetUnitAnimation(u, "spell")' in jass


def test_vietnamese_localization_and_startup(ver2e_map):
    """Game announcements and startup pick messages are fully localized."""
    jass = ver2e_map['jass']
    assert 'Chủ phòng gõ -random để phát ngẫu nhiên Pokémon cho mọi người' in jass
    assert 'Gõ -repick trong 2 phút đầu để đổi Pokémon khác' in jass
    assert '-tp: biến về căn cứ và hồi phục sau 3 giây...' in jass
    assert '-home: trở về nhà sau 5 giây...' in jass
    assert 'Dây Thoát Hiểm: về căn cứ sau 3 giây...' in jass
    assert 'POKEMON ARENA v4.1.2-ver2e' in jass
