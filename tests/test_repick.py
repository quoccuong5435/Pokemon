import inject
import jasscheck

MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
SRC = inject.module_source(MS, BS, None, ['E003', 'E008'], inject.evo_inputs())


def _func(name):
    i = SRC.index('function %s takes' % name)
    return SRC[i:SRC.index('endfunction', i)]


def test_module_with_repick_passes_checker():
    assert jasscheck.check(SRC, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_repick_limits():
    assert 'real Repick_Window = 120.0' in SRC and 'integer Repick_Max = 2' in SRC
    do = _func('Repick_Do')
    assert 'Mega_Time >= Repick_Window' in do
    assert 'Repick_Count[pid] >= Repick_Max' in do
    assert 'IsUnitType(h, UNIT_TYPE_DEAD)' in do and 'LoadInteger(Mega_HT, GetHandleId(h), 0) > 0' in do


def test_repick_saves_and_gives_back_hero_state():
    do = _func('Repick_Do')
    assert 'set Repick_XP[pid] = GetHeroXP(h)' in do
    assert 'UnitRemoveItem(h, it)' in do and 'SetItemVisible(it, false)' in do
    assert "CreateUnit(p, 'earc', -128.0, 4544.0, 270.0)" in do and 'RemoveUnit(h)' in do
    restore = _func('Repick_Restore')
    assert 'SetHeroXP(u, Repick_XP[pid], true)' in restore and 'UnitAddItem(u, it)' in restore
    assert 'call Repick_Restore(GetSoldUnit())' in _func('Repick_OnSell')
    assert 'call Repick_Restore(h)' in _func('Rand_Give')


def test_repick_registered():
    init = _func('Mega_Init')
    assert 'TriggerRegisterPlayerChatEvent(t, Player(i), "-repick", true)' in init
    assert 'EVENT_PLAYER_UNIT_SELL' in init and 'function Repick_OnSell' in init
