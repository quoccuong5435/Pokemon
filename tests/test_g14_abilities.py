"""Task 4: the 205 Gen 1-4 heroes (EG..) get their real PokeAPI ability, not one picked by type or by an old AB_ constant."""
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import ability_names  # noqa: E402
import form_pokeapi  # noqa: E402
import gen14_expansion  # noqa: E402


def _ab(script, uid):
    ms = re.findall(r"SaveInteger\(Ab_HT, '%s', 0, (\d+)\)" % uid, script)
    return int(ms[-1]) if ms else None


def test_spearow_default_is_keen_eye(npa_data):
    script = npa_data["script"]
    assert _ab(script, "EG00") == ability_names.ability_index(script)["Keen Eye"]


def test_every_g14_default_is_the_first_known_normal_pokeapi_ability(npa_data):
    script = npa_data["script"]
    index = ability_names.ability_index(script)
    wrong = []
    for sp in gen14_expansion.load_species_entries():
        rec = form_pokeapi.by_dex(sp["dex"])
        want = ability_names.first_known(index, rec["abilities"])
        if want is None:
            want = gen14_expansion.TYPE_FALLBACK_AB.get(sp["types"][0], 16)
        if _ab(script, sp["hero"]) != want:
            wrong.append((sp["hero"], sp["slug"], _ab(script, sp["hero"]), want))
    assert not wrong, wrong[:8]


def test_wild_creep_uses_the_same_ability_as_its_hero(npa_data):
    script = npa_data["script"]
    for sp in gen14_expansion.load_species_entries():
        assert _ab(script, sp["wild"]) == _ab(script, sp["hero"]), sp["slug"]
