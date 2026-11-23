"""v4.3.3: gym order and minimum levels (tools/v3411/gym_order.py)."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'v3411'))
import gym_order  # noqa: E402

SAMPLE = '''function Gym_Allowed takes integer pid, integer g returns boolean
    return g < 2 * (Gym_Milestone(pid) + 1)
endfunction
function Gym_Tick takes nothing returns nothing
                    if not Gym_Allowed(pid, g) then
                        if Mega_Time >= Gym_Warn[pid] then
                            set Gym_Warn[pid] = Mega_Time + 10.0
                            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + " is locked: you can challenge gyms 1-" + I2S(2 * (Gym_Milestone(pid) + 1)) + " (clear 2 gyms to open 2 more).|r")
                        endif
                    elseif Mega_Time < Gym_PCool[pid * 8 + g] then
                    endif
endfunction
'''


@pytest.fixture(scope='module')
def patched():
    return gym_order.patch_script(SAMPLE)


def test_order_rule(patched):
    assert 'return g == 0 or Badge_Has[pid * 8 + g - 1]' in patched
    assert 'Gym_Milestone' not in patched


def test_min_levels_are_10_to_80():
    assert re.search(r'return 10 \* \(g \+ 1\)', gym_order.MINLEVEL)
    assert [10 * (g + 1) for g in range(8)] == [10, 20, 30, 40, 50, 60, 70, 80]


def test_level_check_before_cooldown_branch_and_defined_first(patched):
    assert patched.index('function Gym_MinLevel') < patched.index('function Gym_Allowed')
    assert patched.index('GetHeroLevel(u) < Gym_MinLevel(g)') < patched.index('elseif Mega_Time < Gym_PCool')
    assert 'needs level' in patched and 'clear Gym " + I2S(g) + " first' in patched


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        gym_order.patch_script('x')
