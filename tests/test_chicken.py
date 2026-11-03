import inject
import jasscheck

MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
SRC = inject.module_source(MS, BS)


def _func(name):
    i = SRC.index('function %s takes' % name)
    return SRC[i:SRC.index('endfunction', i)]


def _jass(text):
    """How a UTF-8 string literal appears in the latin-1 decoded script text."""
    return text.encode('utf-8').decode('latin-1')


def test_module_passes_checker():
    assert jasscheck.check(SRC, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_chicken_commands_registered_as_utf8():
    init = _func('Mega_Init')
    for cmd in ('t là gà', 'tôi là gà', 't la ga', 'toi la ga', 'chicken', '-chicken'):
        assert 'TriggerRegisterPlayerChatEvent(t, Player(i), "%s", true)' % _jass(cmd) in init, cmd
    assert 'function Chicken_OnChat' in init


def test_chicken_gives_10_levels_and_10000_gold_once():
    assert 'integer Chicken_Levels = 10' in SRC and 'integer Chicken_Gold = 10000' in SRC
    do = _func('Chicken_Do')
    assert 'if Chicken_Used[pid] then' in do and 'set Chicken_Used[pid] = true' in do
    assert 'call SetHeroLevel(h, lv, true)' in do and 'if lv > 100 then' in do
    assert 'SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) + Chicken_Gold)' in do


def test_chicken_is_host_command_for_everyone():
    on_chat = _func('Chicken_OnChat')
    assert 'GetPlayerId(GetTriggerPlayer()) != Host_Id()' in on_chat
    assert 'call Chicken_Do(Player(i))' in on_chat and 'exitwhen i >= 12' in on_chat
