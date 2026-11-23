"""v4.3.1: -repick gives the typer one random Pokemon (tools/v3411/repick_random.py)."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'v3411'))
import repick_random  # noqa: E402

SAMPLE = open(os.path.join(HERE, 'fixtures', 'repick_3416_sample.j'), encoding='latin-1').read()


def func(s, name):
    m = re.search(r'(?ms)^function %s takes.*?^endfunction\n' % name, s)
    assert m, name
    return m.group(0)


@pytest.fixture(scope='module')
def patched():
    return repick_random.patch_script(SAMPLE)


def test_chat_runs_the_random_wrapper(patched):
    assert 'call TriggerAddAction(t, function Repick_RandomOnChat)' in func(patched, 'Chat_Init')
    assert 'function Repick_OnChat)' not in patched


def test_wrapper_gives_a_random_pokemon_after_a_valid_repick(patched):
    body = func(patched, 'Repick_RandomOnChat')
    assert 'call Repick_Do(p)' in body
    assert 'Repick_Pending[pid] and Rand_FindWisp(p) != null' in body
    assert 'call Rand_Give(p)' in body
    # JASS: the wrapper must come after everything it calls
    for dep in ('Repick_Do', 'Rand_FindWisp', 'Rand_Give'):
        assert patched.index('function %s takes' % dep) < patched.index('function Repick_RandomOnChat takes')


def test_old_species_is_remembered_and_excluded(patched):
    assert 'integer array Repick_Old' in patched
    assert patched.index('integer array Repick_Old') < patched.index('endglobals')
    do = func(patched, 'Repick_Do')
    assert do.index('set Repick_Old[pid] = GetUnitTypeId(h)') < do.index('call RemoveUnit(h)')
    give = func(patched, 'Rand_Give')
    assert 'exitwhen tries >= 20 or (not Rand_IsTaken(t) and t != Repick_Old[GetPlayerId(p)])' in give
    assert 'set Repick_Old[GetPlayerId(p)] = 0' in give


def test_limits_and_xp_restore_are_untouched(patched):
    do = func(patched, 'Repick_Do')
    assert 'Mega_Time >= Repick_Window' in do and 'Repick_Count[pid] >= Repick_Max' in do
    assert 'Repick_Pending[pid] = true' in do
    assert 'call Repick_Restore(h)' in func(patched, 'Rand_Give')


def test_texts_say_random(patched):
    assert 'to get another random Pokemon' in func(patched, 'Rand_Hint')
    assert 'to get a random one instead' in func(patched, 'Other_Msg')
    assert 'to choose again' not in patched


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        repick_random.patch_script('globals\nendglobals\nfunction Other takes nothing returns nothing\nendfunction\n')
