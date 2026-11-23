"""v4.1.5: stronger Storm Shock, Soul Burn, Mana Surge (tools/v412/charm_buff.py), checked on the real v4.1.2 script."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import charm_buff  # noqa: E402
import mpq  # noqa: E402

MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.1.2.w3x')
pytestmark = pytest.mark.skipif(not os.path.exists(MAP), reason='v4.1.2 map not on this PC')


@pytest.fixture(scope='module')
def patched():
    return charm_buff.patch_script(mpq.MPQ(MAP).read('scripts\war3map.j').decode('latin-1'))


def test_storm_shock(patched):
    assert 'GetRandomReal(0.0, 100.0) < 45.0' in patched and '>= 1.2 and' in patched
    assert re.findall(r'set effectVal = (\d+)\r\n            elseif tier == \d then\r\n                set effectVal = (\d+)', patched)  # still tiered
    assert 'Storm Shock: 45% chance for' in patched and '(1.2s ICD)' in patched and 'Storm Shock: 30% chance' not in patched


def test_soul_burn_has_a_main_stat_part(patched):
    assert 'PAX_Leg_MainStat(attacker) * I2R(pct) * 0.02' in patched
    assert patched.index('function PAX_Leg_MainStat takes') < patched.index('function PAX_Loot_Tick takes')
    assert patched.count('Soul Burn (+2% x pct main stat)') == 5  # 4 tiers + the Mythic Forge text


def test_mana_surge_doubled(patched):
    assert 'I2R(val) * 0.002' in patched
    for t in ('3.0% max mana on hit', '5.0% max mana on hit', '7.0% max mana on hit', '10.0% max mana on hit'):
        assert t in patched
    assert '1.5% max mana on hit' not in patched


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        charm_buff.patch_script('x\r\n')
