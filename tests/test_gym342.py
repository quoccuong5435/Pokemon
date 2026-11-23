"""v4.3: the 3.4.2 gym features on the 3.4.16 script (tools/v3411/gym342.py)."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools', 'v3411'))
import gym342  # noqa: E402

SAMPLE = open(os.path.join(HERE, 'fixtures', 'gym_3416_sample.j'), encoding='latin-1').read()
JASS = open(os.path.join(os.path.dirname(HERE), 'tools', 'v3411', 'jass', 'gym342.j'), encoding='utf-8').read() \
    if os.path.exists(os.path.join(os.path.dirname(HERE), 'tools', 'v3411', 'jass', 'gym342.j')) else ''


def func(s, name):
    m = re.search(r'(?ms)^function %s takes.*?^endfunction\n' % name, s)
    assert m, name
    return m.group(0)


@pytest.fixture(scope='module')
def patched():
    return gym342.patch_script(SAMPLE)


# ---- Task 1: difficulty table and Ai_Chance
def test_spawn_uses_table(patched):
    body = func(patched, 'Gym_Spawn')
    assert '* Gym_HPMult * Gym_DiffHP(g)))' in body
    assert '* 0.8 * Gym_DiffDmg(g)), 0)' in body
    assert '* m * Gym_DiffDmg(g))' in body
    assert 'if Gym_Fast(g) then' in body
    assert 'call SaveReal(Ab_HT, h, 88, Gym_DiffAI(g))' in body
    # the 3.4.16 hooks stay
    for hook in ('Fx_KitStatusX', 'Fx_GymItemX', 'Gym_Root'):
        assert hook in body


def test_ai_unit_uses_chance(patched):
    body = func(patched, 'Ai_Unit')
    assert '< Ai_Chance(h) then' in body
    assert '< Ai_CastChance then' not in body


def test_helpers_defined_before_use(patched):
    assert patched.index('function Gym_DiffHP takes') < patched.index('function Gym_Spawn takes')
    assert patched.index('function Ai_Chance takes') < patched.index('function Ai_Unit takes')


def test_table_values():
    body = func(JASS, 'Gym_DiffHP')
    assert re.search(r'g == 0 then\s+return 0\.35', body)
    assert re.search(r'g == 3 then\s+return 0\.85', body)
    assert 'return 1.0' in body
    ai = func(JASS, 'Gym_DiffAI')
    assert re.search(r'g == 0 or g == 1 then\s+return 0\.25', ai)
    assert re.search(r'g == 2 or g == 3 then\s+return 0\.45', ai)
    assert 'return 0.6' in ai
    fast = func(JASS, 'Gym_Fast')
    assert 'g >= 4' in fast


def test_league_slot_is_not_easy():
    # index 8 (the League) must fall through to the normal values
    assert re.search(r'g < 4|g >= 4', func(JASS, 'Gym_Fast'))
    assert 'return 1.0' in func(JASS, 'Gym_DiffDmg')


# ---- Task 2: -gym and the busy message
def test_chat_registered(patched):
    assert patched.index('function Gym_OnChat takes') < patched.index('function Chat_Init takes')
    init = func(patched, 'Chat_Init')
    assert '"-gym", true)' in init
    assert 'function Gym_OnChat)' in init
    assert 'function League_OnChat)' in init


def test_chat_text():
    body = func(JASS, 'Gym_OnChat')
    assert 'No gym battle right now.' in body
    assert ', current: none (it will be spawned again)' in body


def test_busy_message(patched):
    body = func(patched, 'Gym_Tick')
    assert 'is busy: ' in body
    assert 'Gym_Warn[pid] = Mega_Time + 5.0' in body
    assert 'GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)' in body


# ---- Task 3: stuck-gym fixes with threads
def test_death_uses_advance(patched):
    death = func(patched, 'Gym_OnDeath')
    assert 'call Gym_Advance(g, d)' in death
    assert 'Fx_BadgeX' not in death
    adv = func(patched, 'Gym_Advance')
    for text in ('Fx_BadgeX', 'Gym_ClearItems(d)', 'Badge_Has[pid * 8 + g] = true', 'ExecuteFunc("Gym_SpawnIt")',
                 'call Gym_Reset(g)', 'Fx_ArgU = Gym_Hero[g]'):
        assert text in adv
    assert 'call Gym_Spawn(g, Gym_Stage[g])' not in adv
    assert patched.index('function Gym_Advance takes') < patched.index('function Gym_AdvanceIt takes') \
        < patched.index('function Gym_OnDeath takes')


def test_tick_threads(patched):
    tick = func(patched, 'Gym_Tick')
    for text in ('ExecuteFunc("Gym_StartIt")', 'ExecuteFunc("Gym_SpawnIt")', 'ExecuteFunc("Gym_AdvanceIt")',
                 'call SetUnitPosition(Gym_Cur[g], Gym_X[g], Gym_Y[g])',
                 'Gym_Stage[g] < 6 and (Gym_Cur[g] == null'):
        assert text in tick
    assert 'call Gym_BuildTeam(g, u)' not in tick
    assert 'call Gym_Spawn(g, 0)' not in tick
    for hook in ('Gym_Down(g, Gym_Hero[g])', 'Fx_LeaderHiX', 'Gym_DownSince[g] = 0.0'):
        assert hook in tick


def test_entry_points_and_globals(patched):
    for name in ('Gym_StartIt', 'Gym_SpawnIt', 'Gym_AdvanceIt'):
        assert 'function %s takes nothing returns nothing' % name in patched
    assert 'call Gym_BuildTeam(g, Gym_Hero[g])' in func(patched, 'Gym_StartIt')
    assert patched.index('integer Gym_ArgG = 0') < patched.index('endglobals')
    assert 'integer Gym_ArgK = 0' in patched


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        gym342.patch_script('globals\nendglobals\nfunction Other takes nothing returns nothing\nendfunction\n')
