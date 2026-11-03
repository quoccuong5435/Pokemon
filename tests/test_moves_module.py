import os

import ability_data
import inject
import jasscheck
import learn_data as ld
import objdata
from conftest import EXTRACTED

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
PLAN = ld.build_plan(ld.hero_species(W3U))
ABIL = {'abilities': ability_data.ABILITIES, 'types': ability_data.type_abilities(W3U),
        'megas': ability_data.mega_ability_index()}
MS = {i: 1.0 for i in range(16)}
BS = {i: 1.0 for i in range(16)}
SRC = inject.module_source(MS, BS, abil=ABIL, moves=PLAN)


def _func(name, src=SRC):
    i = src.index('function %s takes' % name)
    return src[i:src.index('endfunction', i)]


def test_module_passes_checker():
    assert jasscheck.check(SRC, jasscheck.NATIVES, jasscheck.KNOWN_GLOBALS) == []


def test_gen_mv_init_empty():
    d = inject.gen_mv_init(None)
    assert 'function Mv_InitData takes nothing returns nothing' in d and 'set Mv_N = 0' in d
    assert 'SaveInteger' not in d


def test_gen_mv_init_lists_moves_and_candidates():
    d = inject.gen_mv_init(PLAN)
    assert 'set Mv_N = %d' % len(PLAN.moves) in d
    blitz = next(m for m in PLAN.moves if m.name == 'Flare Blitz')
    assert 'set Mv_Label[%d] = "Flare Blitz (Fire, power 120)"' % blitz.index in d
    assert 'set Mv_Score[%d] = 120' % blitz.index in d
    cand = PLAN.by_unit['E00E']
    assert "call SaveInteger(Ab_HT, 'E00E', 99, %d)" % len(cand) in d
    lv, m = cand[0]
    assert "call SaveInteger(Ab_HT, 'E00E', 100, %d)" % m in d and "call SaveInteger(Ab_HT, 'E00E', 101, %d)" % lv in d
    assert "'E00G', 99," not in d  # Abra has no damaging level-up move (v3.3: it has TM moves, keys 299 and 300+)
    tm = PLAN.tm_by_unit['E00G']
    assert "call SaveInteger(Ab_HT, 'E00G', 299, %d)" % len(tm) in d


def test_move_id_formula_matches_python():
    body = _func('Mv_Id')
    assert "'A000' - 3158064" in body and '86' in body and '87' in body and '89' in body and '90' in body

    def dig(d):  # Ab_Dig
        return 48 + d if d < 10 else 55 + d
    letters = {0: 86, 1: 87, 2: 89, 3: 90}
    for slot in range(4):
        for m in (0, 1, 9, 10, 35, 36, 227, 1295):
            expect = ld.ability_id(slot, m)
            got = 65 * 2 ** 24 + letters[slot] * 65536 + dig(m // 36) * 256 + dig(m % 36)
            assert got == int.from_bytes(expect.encode('ascii'), 'big'), (slot, m)


def test_sync_learns_candidates_and_offers_when_full():
    body = _func('Mv_Sync')
    assert 'LoadInteger(Ab_HT, id, 99)' in body and '101 + 2 * k' in body and '100 + 2 * k' in body
    assert 'Mv_FreeSlot(u)' in body and 'Mv_Put(u, s, m)' in body and 'Mv_Notify(u, m)' in body
    assert 'elseif Mv_Score[m] > Mv_WeakScore(u) then' in body and 'call Mv_Put(u, Mv_WeakSlot(u), m)' in body
    assert 'Mv_Offer' not in body and 'Dialog' not in body
    assert 'LoadInteger(Ab_HT, h, 200 + m) == 0' in body and 'SaveInteger(Ab_HT, h, 200 + m, 1)' in body
    assert 'Mv_Known(u, m)' in body and 'if lv >= LoadInteger(Ab_HT, id, 101 + 2 * k) then' in body


def test_moves_are_synced_with_the_hero_beat_and_init():
    assert 'call Mv_Sync(u)' in _func('Ab_Hero')
    init = _func('Mega_Init')
    assert 'call Mv_Init()' in init
    assert 'call Mv_InitData()' in _func('Mv_Init')
    assert 'Mv_Offer' not in SRC and 'call Npc_Show(pid, h, -1)' in SRC  # no automatic dialog; the NPC menu only


def test_weakest_slot_is_the_lowest_score():
    body = _func('Mv_WeakSlot')
    assert 'if Mv_Score[m] < best then' in body and 'return w' in body


def test_evolution_keeps_the_learned_moves():
    body = _func('Mega_SafeReplace')
    assert 'bj_lastReplacedUnit' in body and 'LoadInteger(Ab_HT, h, i)' in body
    assert 'set i = 40' in body and 'exitwhen i > 43' in body and '200 + i' in body and 'exitwhen i >= Mv_N' in body


def test_heroes_without_an_ability_still_record_the_last_hit():
    body = _func('Ab_OnDamaging')
    assert 'if ta == 0 and IsUnitType(t, UNIT_TYPE_HERO) then' in body
