"""v4.3.2: Team Rocket raid schedule, spawn guard and the host test command (tools/v3411/jass/fx_main.j)."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(os.path.dirname(HERE), 'tools', 'v3411', 'jass', 'fx_main.j'), encoding='utf-8').read()


def func(name):
    m = re.search(r'(?ms)^function %s takes.*?^endfunction\n' % name, SRC)
    assert m, name
    return m.group(0)


def test_first_raid_at_10_min_then_every_15_min():
    # a periodic timer started at game start would fire at 15:00 after the raid of 10:00;
    # the periodic timer must be started by the first raid
    init = func('Fx_EventsInit')
    assert 'call TimerStart(CreateTimer(), Fx_RocketFirst, false, function Fx_RocketFirstX)' in init
    assert 'function Fx_RocketStart)' not in init
    first = func('Fx_RocketFirstX')
    assert 'call TimerStart(CreateTimer(), Fx_RocketEvery, true, function Fx_RocketStart)' in first
    assert 'call DestroyTimer(GetExpiredTimer())' in first
    assert 'call Fx_RocketStart()' in first
    assert SRC.index('function Fx_RocketFirstX takes') < SRC.index('function Fx_EventsInit takes')


def test_raid_is_cancelled_when_no_pokemon_could_be_created():
    start = func('Fx_RocketStart')
    assert 'local integer made = 0' in start
    assert 'if u != null then' in start
    assert 'set made = made + 1' in start
    assert 'if made == 0 then' in start
    cancel = start[start.index('if made == 0 then'):]
    assert 'call Fx_RocketClear()' in cancel.split('endif')[0]
    assert 'cancelled' in cancel.split('endif')[0]
    # the message names the number of Pokemon that really came
    assert 'I2S(made)' in start and 'I2S(Fx_RocketCount)' not in start.split('Defeat their')[1].split('Pokemon within')[0]


def test_host_can_start_a_raid_with_rocket_command():
    cmd = func('Fx_RocketCmd')
    assert 'Host_Id()' in cmd and 'Fx_RocketOn' in cmd and 'call Fx_RocketStart()' in cmd
    init = func('Fx_EventsInit')
    assert '"-rocket", true)' in init and 'function Fx_RocketCmd)' in init
    assert SRC.index('function Fx_RocketCmd takes') < SRC.index('function Fx_EventsInit takes')
