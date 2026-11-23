"""Task 7: one quest slot per final form (Mega, form, Gigantamax, final hero form), quest key widened to 256 slots per player."""
import os
import re
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import hidden_power  # noqa: E402


def _body(script, header):
    return script.split(header)[1].split("\nendfunction")[0]


def test_assign_slots_unique_and_in_range():
    keys = ["mega:%d" % i for i in range(72)] + ["form:%d" % i for i in range(1, 24)] + \
           ["gmax:hG%02d" % i for i in range(12)] + ["type:T%03d" % i for i in range(43)]
    slots = hidden_power.assign_slots(keys)
    assert len(slots) == 150
    assert sorted(slots.values()) == list(range(59, 59 + 150))
    assert slots["mega:0"] == 59


def test_assign_slots_refuses_more_than_the_key_allows():
    with pytest.raises(ValueError):
        hidden_power.assign_slots(["k%d" % i for i in range(255 - 59 + 2)])
    assert len(hidden_power.assign_slots(["k%d" % i for i in range(255 - 59 + 1)])) == 197


def test_qkey_uses_256_and_never_collides(npa_data):
    script = npa_data["script"]
    assert "return 1000 + pid * 256 + idx" in _body(script, "function PAX_Leg_QKey takes integer pid, integer idx returns integer")
    keys = {1000 + pid * 256 + idx for pid in range(12) for idx in range(256)}
    assert len(keys) == 12 * 256  # player 11, slot 255 does not land on player 12 / another slot (Review focus 3)
    assert max(keys) < 100000  # handle ids start at 1048576: no clash with the unit-handle keys of the same hashtable


def test_slot_belongs_to_the_form_not_the_hero(npa_data):
    # Review focus 4: Mega Charizard X, Mega Charizard Y and Gigantamax Charizard are three forms of one hero
    keys = hidden_power.collect_final_keys(npa_data["script"])
    slots = hidden_power.assign_slots(keys)
    assert len({slots["mega:1"], slots["mega:2"], slots["gmax:hG01"]}) == 3
    assert len(keys) == len(set(keys)) == len(slots)


def test_final_forms_found_in_the_script(npa_data):
    keys = hidden_power.collect_final_keys(npa_data["script"])
    kinds = {k.split(":")[0] for k in keys}
    assert kinds == {"mega", "form", "gmax", "type"}
    assert sum(k.startswith("mega:") for k in keys) == 72
    assert sum(k.startswith("form:") for k in keys) == 23
    assert sum(k.startswith("gmax:") for k in keys) == 12
    assert sum(k.startswith("type:") for k in keys) == 43
    assert len(keys) == 150


def test_form_questidx_returns_the_slot_of_the_form(npa_data):
    script = npa_data["script"]
    body = _body(script, "function Form_QuestIdx takes unit u returns integer")
    assert "return Form_FinalSlot(u)" in body
    assert "return 58" not in body
    assert script.index("function Form_FinalSlot") < script.index("function Form_QuestIdx")


def test_final_slot_function_covers_every_final_form(npa_data):
    script = npa_data["script"]
    slots = hidden_power.assign_slots(hidden_power.collect_final_keys(script))
    body = _body(script, "function Form_FinalSlot takes unit u returns integer")
    assert "return 59 + mi" in body and "mi < 72" in body
    assert "return 131 + formId - 1" in body and "formId <= 23" in body
    for key, slot in slots.items():
        kind, ident = key.split(":", 1)
        if kind in ("gmax", "type"):
            assert re.search(r"== '%s' then\s+return %d\b" % (ident, slot), body), key
    assert body.rstrip().endswith("return 58")  # an unknown final form still gets the shared slot


def test_slot_names_and_unlock_all(npa_data):
    script = npa_data["script"]
    names = _body(script, "function Form_SlotName takes integer idx returns string")
    assert "Mega_Name[idx - 59]" in names and "Iron Treads" in names and "GetObjectName('hG00')" in names
    assert "elseif idx >= 59 then" in _body(script, "function PAX_Leg_Name takes integer idx returns string")
    last = max(hidden_power.assign_slots(hidden_power.collect_final_keys(script)).values())
    assert "return %d" % last in _body(script, "function PAX_Quest_Last takes nothing returns integer")
    assert "exitwhen idx > PAX_Quest_Last()" in _body(script, "function PAX_Leg_UnlockCmd takes nothing returns nothing")


def test_legend_dialog_still_lists_58_entries(npa_data):
    # PAX_Leg_Count() also sizes the paged legend dialog: it must not grow with the final-form slots
    assert "return 58" in _body(npa_data["script"], "function PAX_Leg_Count takes nothing returns integer")
