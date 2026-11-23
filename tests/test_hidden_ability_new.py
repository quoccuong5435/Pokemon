"""Task 6: Hidden Ability (Ability Patch) for the new Gen 1-4 heroes and hero forms (tools/v412/hidden_ability_new.py)."""
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import ability_names  # noqa: E402
import form_pokeapi  # noqa: E402
import gen14_expansion  # noqa: E402
import hidden_ability_new as H  # noqa: E402

TINY = (
    "constant integer AB_SNIPER = 7\n"
    "constant integer AB_NOCODE = 8\n"
    'set Ab_Name[7] = "Sniper"\n'
    'set Ab_Info[7] = "Crits deal +\\"50%\\" more."\n'
    'set Ab_Name[8] = "No Code"\n'
    'set Ab_Info[8] = "x"\n'
    "function Foo takes nothing returns nothing\n    if a == AB_SNIPER then\n    endif\nendfunction\n"
    "function AbilityPatch_Init takes nothing returns nothing\n    local integer i = 0\n    call HiddenAb_InitIdx()\n"
    "    loop\n        exitwhen i >= 12\n    endloop\nendfunction\n"
)


def test_collect_entries_keeps_only_abilities_the_map_has():
    got = H.collect_entries(TINY, {"EG00": "sniper", "EG01": "no-such-ability", "EG02": None})
    assert got == {"EG00": "Sniper"}


def test_patch_writes_name_text_and_number_before_the_loop():
    out = H.patch(TINY, {"EG00": "Sniper"})
    assert "call SaveStr(AbilityPatch_HT, 'EG00', 1, \"Sniper\")" in out
    assert 'call SaveStr(AbilityPatch_HT, \'EG00\', 2, "Crits deal +\\"50%\\" more.")' in out
    assert "call SaveInteger(AbilityPatch_HT, 'EG00', 3, 7)" in out
    assert out.index("function HiddenAb_InitNew") < out.index("function AbilityPatch_Init")
    assert out.index("call HiddenAb_InitNew()") > out.index("call HiddenAb_InitIdx()")


def test_ability_without_code_is_named_but_not_sold():
    out = H.patch(TINY, {"EG00": "No Code"})
    assert "'EG00', 1, \"No Code\"" in out
    assert "'EG00', 3," not in out  # number 0 / missing = the Ability Patch refunds


def test_patch_refuses_a_script_without_its_anchors():
    import pytest
    with pytest.raises(ValueError):
        H.patch("function Other takes nothing returns nothing\nendfunction\n", {"EG00": "Sniper"})


def _entries_in(script):
    names = dict(re.findall(r"call SaveStr\(AbilityPatch_HT, '(\w{4})', 1, \"(.*?)\"\)", script))
    return names


def test_built_map_has_hidden_abilities_for_the_new_heroes(npa_data):
    script = npa_data["script"]
    index = ability_names.ability_index(script)
    names = _entries_in(script)
    expected = 0
    for sp in gen14_expansion.load_species_entries():
        hidden = form_pokeapi.by_dex(sp["dex"])["hidden"]
        if hidden and ability_names.first_known(index, [hidden]) is not None:
            expected += 1
            assert names.get(sp["hero"]) is not None, sp["slug"]
    assert expected > 100
    assert npa_data["opt_stats"]["hidden_ability_new"] >= expected


def test_no_mega_or_gigantamax_skin_gets_a_hidden_ability(npa_data):
    names = _entries_in(npa_data["script"])
    assert not [u for u in names if u.startswith(("hF", "hG", "hP"))]


def test_every_new_entry_name_exists_in_the_map(npa_data):
    script = npa_data["script"]
    index = ability_names.ability_index(script)
    fs = npa_data["opt_stats"]["form_stats"]
    names = _entries_in(script)
    for hid in list(fs["form_heroes"]) + [sp["hero"] for sp in gen14_expansion.load_species_entries()]:
        if hid in names:
            assert names[hid] in index, (hid, names[hid])
