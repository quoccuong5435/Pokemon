"""Tests for Pokemon Arena v4.1.2-ver2c.w3x:
- 192x192 map dimensions (w3e, wpm, shd, w3i)
- Weather visual fx (fog and thunder)
- Base layout coordinates (clear center, Forge, Moves, Form, Paradox, League)
- 33 Gen 2-7 starter heroes, wild types, Souls, Greninja Torrent, models/icons
- 9 new debuffs, Transform, and 18 visible stage buff icons
"""
import os
import struct
import mpq
import slk
import objdata

MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Pokemon Arena v4.1.2-ver2c.w3x')


def test_map_exists():
    assert os.path.exists(MAP_PATH), 'Pokemon Arena v4.1.2-ver2c.w3x must exist'


def test_map_dimensions_192():
    arc = mpq.MPQ(MAP_PATH)

    # 1. w3e
    w3e = arc.read('war3map.w3e')
    p = 4 + 4 + 1 + 4
    n_g = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_g * 4
    n_c = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_c * 4
    mx, my, ox, oy = struct.unpack_from('<IIff', w3e, p)
    assert mx == 193 and my == 193, f'Expected 193x193 corners, got {mx}x{my}'
    assert ox == -12288.0 and oy == -12288.0, f'Expected offset -12288, got ({ox}, {oy})'

    # 2. wpm
    wpm = arc.read('war3map.wpm')
    magic, ver, w, h = struct.unpack_from('<4sIII', wpm, 0)
    assert magic == b'MP3W' and w == 768 and h == 768, f'Expected 768x768 pathing cells, got {w}x{h}'

    # 3. shd
    shd = arc.read('war3map.shd')
    assert len(shd) == 768 * 768, f'Expected 768x768 shadow cells, got {len(shd)}'

    # 4. w3i
    w3i = arc.read('war3map.w3i')
    found_192 = False
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 192 and h == 192:
            found_192 = True
            break
    assert found_192, 'Expected (192, 192) in w3i'


def test_base_layout():
    arc = mpq.MPQ(MAP_PATH)
    j = arc.read('scripts\\war3map.j').decode('latin-1')

    # Moves NPC
    assert 'set Npc_X[0] = -5340.0' in j and 'set Npc_Y[0] = -220.0' in j
    assert 'set Npc_X[1] = 5340.0' in j and 'set Npc_Y[1] = -220.0' in j

    # Mythic Forge
    assert 'set fx = -5952.0' in j and 'set fx = 5952.0' in j
    assert 'local real fy = -220.0' in j

    # Form Shop & Paradox Shop
    assert 'set x = sx * 5440.0' in j
    assert "set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', sx * 5200.0, 200.0, 270.0)" in j

    # League portal
    assert 'set gx = (2.0 * I2R(k) - 1.0) * 5120.0' in j and 'set gy = 460.0' in j


def test_weather_fx():
    arc = mpq.MPQ(MAP_PATH)
    j = arc.read('scripts\\war3map.j').decode('latin-1')
    assert 'SetTerrainFogEx(0, 900.0, 5000.0, 0.5, 0.25, 0.35, 0.55)' in j
    assert 'function Wth_Thunder takes nothing returns nothing' in j
    assert 'call TimerStart(CreateTimer(), 3.0, true, function Wth_Thunder)' in j


def test_33_starters():
    arc = mpq.MPQ(MAP_PATH)
    j = arc.read('scripts\\war3map.j').decode('latin-1')
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    items = slk.Slk(arc.read('Units\\ItemData.slk').decode('latin-1'))
    func = arc.read('Units\\ItemFunc.txt').decode('utf-8')

    # 33 Hero units EP00..EP0W
    custom_units = {o.new: o for o in w3u.custom}
    dig = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for k in range(33):
        hid = 'EP' + dig[k // 36] + dig[k % 36]
        wid = 'nZ' + dig[k // 36] + dig[k % 36]
        sid = 'IZ' + dig[k // 36] + dig[k % 36]
        assert hid in custom_units, f'Hero unit {hid} missing'
        assert wid in custom_units, f'Wild unit {wid} missing'
        assert items.find(sid) is not None, f'Soul item {sid} missing in ItemData.slk'
        assert f'[{sid}]' in func, f'Soul item {sid} missing in ItemFunc.txt'

    # Greninja Ability is Torrent (3)
    assert "call SaveInteger(Ab_HT, 'EP0R', 0, 3)" in j

    # Chunked functions
    assert 'function Fx_Data13 takes nothing returns nothing' in j
    assert 'function Fx_Data16 takes nothing returns nothing' in j
    assert 'call ExecuteFunc("Fx_Data13")' in j
    assert 'call ExecuteFunc("Fx_Data16")' in j

    # Assets
    assert arc.has('PkFx\\Starter\\158.mdx'), 'Totodile model missing'
    assert arc.has('PkFx\\Starter\\658.mdx'), 'Greninja model missing'
    assert arc.has('ReplaceableTextures\\CommandButtons\\BTN_158.blp'), 'Totodile icon missing'


def test_status_debuffs_and_stages():
    arc = mpq.MPQ(MAP_PATH)
    j = arc.read('scripts\\war3map.j').decode('latin-1')
    abil = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    buffs = slk.Slk(arc.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    strings = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')

    # 18 visible stage buff icons
    for k in range(18):
        aid = 'AF1' + chr(65 + k)
        bid = 'BF1' + chr(65 + k)
        assert abil.find(aid) is not None, f'Ability {aid} missing'
        assert buffs.find(bid) is not None, f'Buff {bid} missing'
        assert f'[{aid}]' in strings, f'Tooltip for {aid} missing'
        assert f'[{bid}]' in strings, f'Buff tooltip for {bid} missing'

    # Bonus abilities
    for bid in ('AF0A', 'AF0D', 'AF0S'):
        assert abil.find(bid) is not None, f'Bonus ability {bid} missing'

    # Transform (Ditto)
    assert 'act == 29' in j
    assert 'BlzSetUnitSkin(u, GetUnitTypeId(tgt))' in j
    assert 'function Fx_StatSync takes unit u returns nothing' in j
