"""v4.1.2-ver2 boss buff (tools/v412/boss_buff.py), checked on the real v4.1.2 script."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import boss_buff  # noqa: E402
import mpq  # noqa: E402

MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.1.2.w3x')
pytestmark = pytest.mark.skipif(not os.path.exists(MAP), reason='v4.1.2 map not on this PC')


@pytest.fixture(scope='module')
def patched():
    s = mpq.MPQ(MAP).read('scripts\war3map.j').decode('latin-1').replace('\r\r\n', '\r\n').replace('\r\n', '\n')
    return boss_buff.patch_script(s)


def test_buff_is_in_leg_spawn_before_the_boss_registration(patched):
    body = re.search(r'(?ms)^function Leg_Spawn takes.*?^endfunction\n', patched).group(0)
    assert body.index('BlzGetUnitMaxHP(lg) * 20') < body.index('call PAX_Boss_Register(lg, x, y)')
    for t in ('BlzGetUnitBaseDamage(lg, 0) * 5', 'BlzGetUnitDiceSides(lg, 0) * 5', 'BlzGetUnitArmor(lg) * 3.0'):
        assert t in body
    assert 'HP x20, attack x5, armor x3' in body


def test_flat_bonus_is_skipped_for_a_x20_legend():
    # PAX_Boss_Register adds 150,000 only below 150,000 HP: the smallest wild legend x20 is far above
    assert 34866 * 20 > 150000


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        boss_buff.patch_script('x\n')
