"""v4.1.4: Max HP from loot has a soft cap instead of a hard one (tools/v412/loot_hp.py)."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'v412'))
import loot_hp  # noqa: E402
import loot_balance  # noqa: E402

SAMPLE = open(os.path.join(HERE, 'fixtures', 'loot_hp_4112_sample.j'), encoding='latin-1', newline='').read()


def func(s, name):
    m = re.search(r'function %s takes.*?\r\nendfunction\r\n' % name, s, re.S)
    assert m, name
    return m.group(0)


@pytest.fixture(scope='module')
def patched():
    return loot_hp.patch_script(SAMPLE)


def counted(raw, cap, rest_div):
    return raw if raw <= cap else cap + (raw - cap) // rest_div


def test_hard_cap_is_gone_and_replaced_by_a_soft_cap(patched):
    body = func(patched, 'PAX_TestItem_SyncEx')
    assert 'set newHP = 15000\r\n' not in body
    m = re.search(r'set newHP = (\d+) \+ \(newHP - (\d+)\) / (\d+)', body)
    assert m, 'soft cap expression'
    cap, cap2, div = (int(x) for x in m.groups())
    assert cap == cap2 == 15000 and div == 2
    # the example of the report: hero 10,000 HP + loot 23,000 (was 25,000 in total)
    assert 10000 + counted(23000, cap, div) == 29000
    # below the cap nothing changes, and more loot never means less HP
    assert counted(9000, cap, div) == 9000 and counted(15000, cap, div) == 15000
    assert all(counted(v + 1, cap, div) >= counted(v, cap, div) for v in range(0, 60000, 997))


def test_raw_total_is_saved_before_the_cap(patched):
    body = func(patched, 'PAX_TestItem_SyncEx')
    save = body.index('call SaveInteger(PAX_Item_HT, h, 130, newHP)')
    assert save < body.index('set newHP = 15000 + (newHP - 15000) / 2')
    assert save > body.index('exitwhen i >= 6')  # after the loop that sums the items


def test_player_is_told_when_the_loot_total_is_over_the_cap(patched):
    body = func(patched, 'PAX_TestItem_SyncEx')
    block = body[body.index('if newHP != oldHP then'):]
    block = block[:block.index('endif\r\n    if newMS')]
    assert 'LoadInteger(PAX_Item_HT, h, 130) > 15000' in block
    assert '[LOOT] Max HP from loot:' in block and 'DisplayTimedTextToPlayer(GetOwningPlayer(u)' in block
    # the HP maths of the old code stay
    assert 'BlzSetUnitMaxHP(u, R2I(newMaxHP))' in block


def test_me_shows_the_raw_total_and_the_caps(patched):
    body = func(patched, 'PAX_Me_OnChat')
    assert 'local string hpNote = ""' in body
    assert 'LoadInteger(PAX_Item_HT, h, 130) > 15000' in body
    assert '+ I2S(rHp) + " HP" + hpNote)' in body
    assert 'I2S(lsPct) + "% (max 25%)' in body and 'I2S(critPct) + "% (max 60%)' in body


def test_line_endings_stay_crlf(patched):
    assert not re.search(r'(?<!\r)\n', patched)


def test_bump_version_takes_the_version():
    s, w3i = loot_balance.bump_version('v4.1.2 v4.1.2\r\n', b'v4.1.2', 2, 1, '4.1.4')
    assert s == 'v4.1.4 v4.1.4\r\n' and w3i == b'v4.1.4'
    with pytest.raises(ValueError):
        loot_balance.bump_version('v4.1.2', b'v4.1.2', 1, 1, '4.1.44')  # the w3i needs the same length


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        loot_hp.patch_script('globals\r\nendglobals\r\nfunction Other takes nothing returns nothing\r\nendfunction\r\n')
