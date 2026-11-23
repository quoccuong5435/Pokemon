"""Task 8: role of every final form / later Legend and the role effects of the awakened Hidden Power."""
import collections
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import hidden_power  # noqa: E402
import legend_expansion_data  # noqa: E402


def test_role_for_rules():
    assert hidden_power.role_for([60, 100, 60, 50, 60, 80], "str") == "striker"
    assert hidden_power.role_for([70, 50, 130, 50, 100, 40], "int") == "tank"  # (130 + 100) / 2 = 115
    assert hidden_power.role_for([70, 50, 60, 120, 60, 80], "int") == "caster"
    assert hidden_power.role_for([1, 1, 105, 1, 105, 1], "int") == "tank"  # bulk exactly 105
    assert hidden_power.role_for([1, 1, 104, 1, 105, 1], "int") == "caster"  # bulk 104.5
    assert hidden_power.role_for([1, 200, 104, 1, 105, 1], "str") == "striker"


def test_main_stat():
    assert hidden_power.main_stat([78, 130, 111, 130, 85, 100]) == "str"  # equal Attack / Sp.Atk: Attack (as the map does)
    assert hidden_power.main_stat([78, 84, 78, 109, 85, 100]) == "int"


def test_legend_roles_match_the_data_of_the_25_later_legends():
    assert sorted(hidden_power.LEGEND_ROLES) == list(range(33, 58))
    assert collections.Counter(hidden_power.LEGEND_ROLES.values()) == {"tank": 7, "caster": 11, "striker": 5, "drain": 2}
    for lg in legend_expansion_data.NEW_LEGENDS:
        assert hidden_power.LEGEND_ROLES[lg["idx"]] == lg["role"], lg["name"]


def test_drain_is_never_given_by_the_stat_rule():
    for stats in ([1, 1, 1, 1, 1, 1], [200, 200, 200, 1, 200, 1], [1, 1, 1, 200, 1, 200]):
        assert hidden_power.role_for(stats, hidden_power.main_stat(stats)) != "drain"


def test_every_final_form_but_dark_lugia_has_a_role(npa_data):
    script, fs = npa_data["script"], npa_data["opt_stats"]["form_stats"]
    roles, missing = hidden_power.build_roles(script, fs)
    slots = hidden_power.assign_slots(hidden_power.collect_final_keys(script))
    assert missing == ["mega:36"]  # not an official form: no stats, no role (it is Lugia's Legend slot in play anyway)
    assert set(slots.values()) - set(roles) == {slots["mega:36"]}
    assert all(roles[i] == r for i, r in hidden_power.LEGEND_ROLES.items())
    assert set(roles.values()) <= {"tank", "caster", "striker", "drain"}
    assert {roles[s] for s in slots.values() if s in roles} <= {"tank", "caster", "striker"}


def test_spot_checked_roles(npa_data):
    script, fs = npa_data["script"], npa_data["opt_stats"]["form_stats"]
    roles, _missing = hidden_power.build_roles(script, fs)
    slots = hidden_power.assign_slots(hidden_power.collect_final_keys(script))
    assert roles[slots["mega:0"]] == "tank"  # Mega Venusaur 80/100/123/122/120/80
    assert roles[slots["mega:1"]] == "striker"  # Mega Charizard X 78/130/111/130/85/100
    assert roles[slots["gmax:hG01"]] == "caster"  # Gigantamax Charizard: base Charizard 78/84/78/109/85/100
    assert roles[slots["form:22"]] == "striker"  # Great Tusk 115/131/131/53/53/87
