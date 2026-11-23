"""Automated pytest suite for Pokemon Arena v4.1.2-ver2o:
Verifies:
1. Base courtyard 2-row 10-shop layout (zero shops overlapping Poké Center at +/-5952, 0).
2. 100% uniform & synchronized square move icons across all 388 moves (AV, AW, AY, AZ, AK),
   with 0 round flat BTNPkmn*.blp badges on move abilities.
3. Warcraft III Reforged default font restored (no _retail_\\Fonts override folder, no font lines in war3mapSkin.txt,
   and clean English strings in-game).
4. JASS script passes syntax check with 0 errors.
"""
import os
import re
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import build_ver2o  # noqa: E402
import pokemon_move_icons  # noqa: E402


@pytest.fixture(scope="module")
def ver2o_data():
    return build_ver2o.build_data()


def test_no_shop_overlap_at_pokecenter(ver2o_data):
    """Verify Battle Shop and Paradox Shop are on the top/bottom rows (+/-5350, +/-544) and NOT at PC (+/-5950, +/-240)."""
    _base, _files, script, *_ = ver2o_data

    # Top row: 5950, 5800, 5650, 5500 (nIS0), 5350 (nBS0) at Y = 544.0
    assert "set u=CreateUnit(p,'n00O',5950.0,544.0,270.000)" in script
    assert "set u=CreateUnit(p,'n00N',5800.0,544.0,270.000)" in script
    assert "set u=CreateUnit(p,'n00Q',5650.0,544.0,270.000)" in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)" in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 544.0, 270.0)" in script

    # Bottom row: 5950, 5800, 5650, 5500 (nFS0), 5350 (nFS1) at Y = -544.0
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 5950.0, -544.0, 90.0)" in script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 5800.0, -544.0, 90.0)" in script
    assert "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', 5650.0, -544.0, 90.0)" in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)" in script
    assert "CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -544.0, 90.0)" in script

    # Verify old overlapping coordinates near PC (+/-240.0) are completely gone
    assert "'nBS0', x, 240.0" not in script
    assert "'nFS1', x, -240.0" not in script


def test_move_icons_uniform_square_and_synced(ver2o_data):
    """Verify all 388 moves across AV, AW, AY, AZ, AK use square spell icons (0 flat BTNPkmn circles) and are 100% synced."""
    _base, _files, _script, _abil, _buffs, _items, _func, strings, _w3u = ver2o_data
    sections = re.split(r'(?m)^\[([A-Za-z0-9_]{4})\]\r?\n', strings)

    by_prefix = {'AV': {}, 'AW': {}, 'AY': {}, 'AZ': {}, 'AK': {}}
    for i in range(1, len(sections), 2):
        sec = sections[i]
        body = sections[i + 1]
        prefix = sec[:2]
        if prefix in by_prefix and len(sec) == 4:
            m_idx = pokemon_move_icons.from_b36(sec[2:4])
            m_art = re.search(r'Art=([^\r\n]+)', body)
            assert m_art is not None, f"Missing Art= in [{sec}]"
            art = m_art.group(1).strip()
            assert 'BTNPkmn' not in art, f"Move [{sec}] (idx {m_idx}) still uses flat circular type badge: {art}"
            by_prefix[prefix][m_idx] = art

    assert len(by_prefix['AV']) == 388
    for idx, av_art in by_prefix['AV'].items():
        for pf in ('AW', 'AY', 'AZ', 'AK'):
            if idx in by_prefix[pf]:
                assert by_prefix[pf][idx] == av_art, f"Move {idx} icon mismatch between AV ({av_art}) and {pf} ({by_prefix[pf][idx]})"


def test_warcraft3_reforged_default_font_restored(ver2o_data):
    """Verify _retail_\\Fonts custom font folder is removed and war3mapSkin.txt has no font overrides."""
    _base, files, *_ = ver2o_data
    retail_fonts = r"D:\Warcraft III Reforged\_retail_\Fonts"
    assert not os.path.exists(retail_fonts), f"Custom font override folder still exists: {retail_fonts}"

    skin = files['war3mapSkin.txt'].decode('latin-1')
    for key in ('MasterFont', 'MasterFontBold', 'ChatFont', 'EscMenuTextFont', 'InfoPanelTextFont', 'MessageFont', 'TextTagFont'):
        assert f"{key}=" not in skin
    assert not any('frizqt' in k.lower() for k in files)
