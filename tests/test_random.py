import os

import inject
import jasscheck
import objdata
from conftest import EXTRACTED

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}


def _func(src, name):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_random_pool_is_the_four_taverns():
    pool = inject.random_pool(W3U)
    assert len(pool) == 43 and len(set(pool)) == 43
    assert {'E003', 'E008', 'E004', 'E005', 'E03A', 'E04N'} <= set(pool)
    assert 'E00E' not in pool  # Charizard is an evolution, not sold


def test_random_data_init():
    d = inject.gen_data_init(MS, BS, None, inject.random_pool(W3U))
    assert 'set Rand_N = 43' in d
    assert "set Rand_Type[0] = '" in d


def test_random_module_passes_checker():
    src = inject.module_source(MS, BS, None, inject.random_pool(W3U))
    assert jasscheck.check(src, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_random_wiring():
    src = inject.module_source(MS, BS, None, inject.random_pool(W3U))
    init = _func(src, 'Mega_Init')
    assert 'TriggerRegisterPlayerChatEvent(t, Player(i), "-random", true)' in init
    assert 'call TimerStart(Rand_Timer, Rand_AutoSeconds, false, function Rand_Auto)' in init
    assert 'real Rand_AutoSeconds = 45.0' in src
    give = _func(src, 'Rand_Give')
    assert "Rand_FindWisp(p)" in give and 'RemoveUnit(w)' in give and 'CreateUnit(p, t,' in give
    assert "GetUnitTypeId(u) == 'earc'" in _func(src, 'Rand_FindWisp')


def test_random_is_host_command_for_everyone():
    src = inject.module_source(MS, BS, None, inject.random_pool(W3U))
    host = _func(src, 'Host_Id')
    assert 'GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING' in host
    on_chat = _func(src, 'Rand_OnChat')
    assert 'GetPlayerId(GetTriggerPlayer()) != Host_Id()' in on_chat and 'call Rand_Auto()' in on_chat
