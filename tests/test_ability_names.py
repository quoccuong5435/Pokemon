"""PokeAPI ability slugs <-> the map's ability numbers (tools/v412/ability_names.py)."""
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import ability_names  # noqa: E402


def test_slug_to_name():
    assert ability_names.slug_to_name("quark-drive") == "Quark Drive"
    assert ability_names.slug_to_name("power-of-alchemy") == "Power of Alchemy"


def test_first_known_matches_spelling_variants():
    assert ability_names.first_known({"Surge Surfer": 7}, ["surge-surfer"]) == 7
    assert ability_names.first_known({"Own Tempo": 3}, ["own-tempo"]) == 3
    assert ability_names.first_known({"Soul-Heart": 9}, ["soul-heart"]) == 9


def test_first_known_skips_unknown_and_keeps_order():
    index = {"Swarm": 4, "Sheer Force": 6}
    assert ability_names.first_known(index, ["no-such", "sheer-force", "swarm"]) == 6
    assert ability_names.first_known(index, ["no-such"]) is None
    assert ability_names.first_known(index, []) is None


def test_ability_index_last_definition_wins():
    script = 'set Ab_Name[5] = "Static"\nset Ab_Name[9] = "Static"\nset Ab_Name[16] = "Pressure"\n'
    assert ability_names.ability_index(script) == {"Static": 9, "Pressure": 16}


def test_ability_index_of_the_built_map(npa_data):
    index = ability_names.ability_index(npa_data["script"])
    # 195 numbers but only about 150 names: 41 names were reworked (ability_rw.py) and exist twice, old number < 91 and the
    # approved reworked one >= 91. The reworked one must win.
    assert index["Pressure"] >= 91
    assert index["Overgrow"] == 157
    assert len(index) >= 150
