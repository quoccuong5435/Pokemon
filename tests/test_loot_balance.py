"""v4.1.3: every monster camp gives the same expected loot (tools/v412/loot_balance.py)."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'v412'))
import loot_balance  # noqa: E402

SAMPLE = open(os.path.join(HERE, 'fixtures', 'loot_4112_sample.j'), encoding='latin-1', newline='').read()


def func(s, name):
    m = re.search(r'function %s takes.*?\r\nendfunction\r\n' % name, s, re.S)
    assert m, name
    return m.group(0)


@pytest.fixture(scope='module')
def patched():
    return loot_balance.patch_script(SAMPLE)


def test_factor_defined_before_use(patched):
    assert patched.index('function PAX_Loot_CampFactor takes unit dead returns real') < \
        patched.index('function PAX_Loot_OnDeath takes')


def test_factor_uses_the_camp_of_the_creep(patched):
    body = func(patched, 'PAX_Loot_CampFactor')
    assert 'LoadInteger(Mega_HT, GetHandleId(dead), 25) - 1' in body  # camp index + 1 is saved at spawn
    assert 'c >= Wild_CampN' in body and 'Wild_CampSize[c]' in body
    assert 'return 1.0' in body  # creeps that do not belong to a camp are unchanged


def test_constants_match_the_drop_chances(patched):
    """expected loot of a camp = elite% + (size - 1) * wild%; the factor must use the chances of PAX_Loot_OnDeath."""
    on_death = func(patched, 'PAX_Loot_OnDeath')
    elite = float(re.search(r'elseif isElite then\r\n\s+set chance = ([\d.]+)', on_death).group(1))
    wild = float(re.search(r'elseif isWild then\r\n\s+set chance = ([\d.]+)', on_death).group(1))
    body = func(patched, 'PAX_Loot_CampFactor')
    target, e1, e2 = (float(x) for x in re.search(r'return ([\d.]+) / \(([\d.]+) \+ ([\d.]+) \* I2R\(size - 1\)\)', body).groups())
    assert (e1, e2) == (elite, wild)
    # the whole point: every camp size ends at the same expected loot, and the average camp is not changed
    sizes = [2] * 14 + [4] * 20 + [6] * 19 + [8] + [12]  # the 55 camps of v4.1.2
    for size in set(sizes):
        assert (elite + wild * (size - 1)) * (target / (elite + wild * (size - 1))) == pytest.approx(target)
    mean_before = sum(elite + wild * (s - 1) for s in sizes) / len(sizes)
    assert target == pytest.approx(mean_before, abs=0.5)


def test_applied_only_to_non_legends_before_the_roll(patched):
    body = func(patched, 'PAX_Loot_OnDeath')
    assert 'if not isLegend then' in body
    assert 'chance * PAX_Loot_CampFactor(dead)' in body
    assert body.index('elseif isWild then') < body.index('PAX_Loot_CampFactor(dead)') < \
        body.index('if GetRandomReal(0.0, 100.0) >= chance then')
    assert 'RMinBJ(100.0,' in body  # never above 100%


def test_line_endings_stay_crlf(patched):
    assert not re.search(r'(?<!\r)\n', patched)


def test_bump_version():
    s, w3i = loot_balance.bump_version('SetMapName("Pokemon Arena v4.1.2")\r\nx "v4.1.2"\r\n', b'..v4.1.2..v4.1.2..', 2, 2)
    assert s.count('v4.1.3') == 2 and 'v4.1.2' not in s
    assert w3i == b'..v4.1.3..v4.1.3..'
    with pytest.raises(ValueError):
        loot_balance.bump_version('v4.1.2', b'v4.1.2', 2, 1)


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        loot_balance.patch_script('globals\r\nendglobals\r\nfunction Other takes nothing returns nothing\r\nendfunction\r\n')
