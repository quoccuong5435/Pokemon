"""Automated pytest suite for Pokemon Arena v4.1.3j (Gold-Gated '+' Hero Skill Mega & Form Unlock)."""
import os
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import build_v413j  # noqa: E402


@pytest.fixture(scope="module")
def v413j_data():
    return build_v413j.build_data()


def test_gold_cost_on_hero_mega_and_form_unlock(v413j_data):
    _base, _files, script, _abil, _items, _func, strings, _w3u = v413j_data

    # Verify gold-gating functions & paid flag checks
    assert "function PAX_HeroUnlock_Cost takes unit heroUnit, integer abid returns integer" in script
    assert "function PAX_HeroUnlock_TryPay takes unit heroUnit, integer abid returns boolean" in script
    assert "call SetPlayerState(ownerPl, PLAYER_STATE_RESOURCE_GOLD, curGold - cost)" in script
    assert "call SaveInteger(PAX_Leg_HT, h, abid, 1)" in script
    assert "if PAX_HeroUnlock_TryPay(castUnit, abid) then" in script

    # Verify passive stats only granted once paid (LoadInteger == 1)
    assert "LoadInteger(PAX_Leg_HT, h, Mega_Evolve[i]) == 1" in script
    assert "LoadInteger(PAX_Leg_HT, h, 'AM14') == 1" in script

    # Verify tooltips show 5,000g (normal) and 8,000g (legend) instead of Free
    assert "5,000g" in strings
    assert "8,000g" in strings
    assert ", Free)" not in strings
