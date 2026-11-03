import os

import learn_data as ld
import objdata
import poke_data
from conftest import EXTRACTED

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
UNITS = ld.hero_species(W3U)
PLAN = ld.build_plan(UNITS)


def test_slug_handles_special_names():
    assert ld.slug('Mr.mime') == 'mr-mime' and ld.slug("Farfetch'd") == 'farfetchd' and ld.slug('Nidoran') == 'nidoran-m'
    assert ld.slug('Alolan-Geodude') == 'geodude-alola' and ld.slug('Leafleon') == 'leafeon'
    assert ld.slug('Charizard') == 'charizard'


def test_hero_species_covers_v18_and_new_forms():
    assert UNITS['E00E'] == 'Charizard' and UNITS['EN0K'] == 'Absol'
    assert all(f.id in UNITS for f in poke_data.FORMS)
    assert len(UNITS) >= 130


def test_candidates_are_the_best_damaging_moves_by_learn_level():
    cands = ld.candidates('charizard')
    assert 1 <= len(cands) <= ld.CAND_MAX
    levels = [lv for lv, _ in cands]
    assert levels == sorted(levels) and min(levels) >= 1
    names = {ld.MOVES[mv]['name'] for _, mv in cands}
    assert 'Flare Blitz' in names and 'Flamethrower' in names
    assert all(ld.MOVES[mv]['power'] > 0 for _, mv in cands)
    assert len({mv for _, mv in cands}) == len(cands)


def test_species_without_damaging_moves_have_no_candidates():
    assert ld.candidates('abra') == []
    assert 1 <= len(ld.candidates('magikarp')) <= 1


def test_template_by_class_and_power():
    t = ld.template_for
    assert t({'class': 'physical', 'power': 40}) == ('DAGGER', 1)
    assert t({'class': 'special', 'power': 40}) == ('CHAIN', 1)
    # v3.3: the move name decides the shape; without a name a move is single target
    assert t({'class': 'physical', 'power': 80})[0] == 'BOLT' and t({'class': 'special', 'power': 80})[0] == 'BOLT'
    assert t({'class': 'physical', 'power': 100})[0] == 'BOLT' and t({'class': 'special', 'power': 150}) == ('BOLT', 3)
    assert t({'name': 'Earthquake', 'class': 'physical', 'power': 100})[0] == 'STOMP'
    assert t({'name': 'Blizzard', 'class': 'special', 'power': 110})[0] == 'NOVA'
    assert t({'name': 'Hyper Beam', 'class': 'special', 'power': 150}) == ('ULT_WAVE', 3)
    assert t({'name': 'Flamethrower', 'class': 'special', 'power': 90})[0] == 'CONE'
    assert t({'name': 'Iron Tail', 'class': 'physical', 'power': 100})[0] == 'BOLT'
    for cls in ('physical', 'special'):
        for p in range(5, 251, 5):
            key, lv = t({'class': cls, 'power': p})
            assert key in poke_data.TEMPLATES and lv in (1, 2, 3)


def test_ability_ids_are_unique_valid_rawcodes():
    assert ld.ability_id(0, 0) == 'AV00' and ld.ability_id(1, 37) == 'AW11' and ld.ability_id(3, 1295) == 'AZZZ'
    ids = {ld.ability_id(s, m) for s in range(4) for m in range(len(PLAN.moves))}
    assert len(ids) == 4 * len(PLAN.moves) and all(len(i) == 4 for i in ids)
    assert 100 < len(PLAN.moves) < 400


def test_plan_lists_candidates_per_unit():
    charizard = PLAN.by_unit['E00E']
    assert 4 <= len(charizard) <= ld.CAND_MAX
    assert [PLAN.moves[m].name for _, m in charizard][-1] in ('Flare Blitz', 'Flamethrower', 'Heat Wave', 'Dragon Claw')
    assert PLAN.by_unit.get('E00G', []) == []  # Abra
    assert all(0 <= m < len(PLAN.moves) for lst in PLAN.by_unit.values() for _, m in lst)
    mv = PLAN.moves[charizard[0][1]]
    assert mv.template in poke_data.TEMPLATES and mv.tier in (1, 2, 3) and mv.score > 0
