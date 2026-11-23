"""Task 3: types and Abilities of the 52 form heroes (PF00..) and 28 new Megas (hF00..) come from PokeAPI, not from placeholders."""
import os
import re
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import ability_names  # noqa: E402
import form_assets  # noqa: E402
import form_pokeapi  # noqa: E402
import gen14_expansion  # noqa: E402

TYPE_IDX = gen14_expansion.TYPE_IDX
PRESSURE = 16  # the old, placeholder number


def _ab(script, uid, key):
    ms = re.findall(r"SaveInteger\(Ab_HT, '%s', %d, (\d+)\)" % (uid, key), script)
    return int(ms[-1]) if ms else None


def _types(script, uid):
    return [t for t in (_ab(script, uid, 53), _ab(script, uid, 54)) if t]


def test_form_types_come_from_pokeapi():
    _files, meta = form_assets.load_form_assets(compress_blp=False, pack_files=False)
    assert meta["aegislash-blade"]["types"] == ["steel", "ghost"]
    assert meta["kleavor"]["types"] == ["bug", "rock"]


def test_missing_type_data_stops_the_build(monkeypatch):
    # Review focus 1: a form with neither tree types nor PokeAPI data must fail loudly, not become Normal
    monkeypatch.setattr(form_pokeapi, "pokemon", lambda slug: None)
    with pytest.raises(RuntimeError, match="kleavor"):
        form_assets.load_form_assets(compress_blp=False, pack_files=False)


def test_pf_types_match_pokeapi(npa_data):
    fs = npa_data["opt_stats"]["form_stats"]
    assert len(fs["form_heroes"]) == 52
    for hid, key in fs["form_heroes"].items():
        want = [TYPE_IDX[t] + 1 for t in form_pokeapi.pokemon(key)["types"]]
        assert _types(npa_data["script"], hid) == want, (hid, key)


def test_new_megas_types_match_pokeapi(npa_data):
    fs = npa_data["opt_stats"]["form_stats"]
    assert len(fs["mega_keys"]) == 28
    for idx, key in fs["mega_keys"].items():
        skin = "hF%02d" % (idx - 44)  # Mega 44 is the skin unit hF00
        want = [TYPE_IDX[t] + 1 for t in form_pokeapi.pokemon(key)["types"]]
        assert _types(npa_data["script"], skin) == want, (skin, key)


def test_no_form_or_mega_is_still_the_placeholder_pair(npa_data):
    fs = npa_data["opt_stats"]["form_stats"]
    normal = TYPE_IDX["normal"] + 1
    pairs = [(h, k) for h, k in fs["form_heroes"].items()] + [("hF%02d" % (i - 44), k) for i, k in fs["mega_keys"].items()]
    assert len(pairs) == 52 + 28
    still = [k for h, k in pairs if _types(npa_data["script"], h) == [normal] and _ab(npa_data["script"], h, 0) == PRESSURE]
    real_normal = [k for k in still if form_pokeapi.pokemon(k)["types"] == ["normal"]]
    assert set(still) == set(real_normal), sorted(set(still) - set(real_normal))


def test_form_default_ability_is_the_first_known_pokeapi_ability(npa_data):
    script, fs = npa_data["script"], npa_data["opt_stats"]["form_stats"]
    index = ability_names.ability_index(script)
    for hid, key in fs["form_heroes"].items():
        want = ability_names.first_known(index, form_pokeapi.pokemon(key)["abilities"])
        if want is None:
            assert key in fs["ability_fallback"], key
        else:
            assert _ab(script, hid, 0) == want, (hid, key)


def test_new_mega_ability_is_the_first_known_pokeapi_ability(npa_data):
    script, fs = npa_data["script"], npa_data["opt_stats"]["form_stats"]
    index = ability_names.ability_index(script)
    given = {int(i): int(n) for i, n in re.findall(r"set Ab_MegaAb\[(\d+)\] = (\d+)", script)}
    for idx, key in fs["mega_keys"].items():
        want = ability_names.first_known(index, form_pokeapi.pokemon(key)["abilities"])
        if want is None:
            assert key in fs["ability_fallback"], key
        else:
            assert given[idx] == want, (idx, key)


def test_every_fallback_has_an_unknown_ability_and_data_is_never_missing(npa_data):
    script, fs = npa_data["script"], npa_data["opt_stats"]["form_stats"]
    index = ability_names.ability_index(script)
    for key in fs["ability_fallback"]:
        rec = form_pokeapi.pokemon(key)
        assert rec is not None, key
        assert ability_names.first_known(index, rec["abilities"]) is None, key


def _ab_want_for_form(script, form_id):
    """What the formId branches of Ab_Want return for `form_id` (the first branch whose condition holds), or None."""
    body = script.split("function Ab_Want takes unit u returns integer")[1].split("endfunction")[0]
    lines = [l.strip() for l in body.split("\n")]
    for i, line in enumerate(lines):
        m = re.match(r"(?:if|elseif) formId >= (\d+) and formId <= (\d+) then$", line)
        e = re.match(r"(?:if|elseif) formId == (\d+) then$", line)
        if (m and int(m.group(1)) <= form_id <= int(m.group(2))) or (e and int(e.group(1)) == form_id):
            return lines[i + 1].replace("return ", "")
    return None


def test_new_paradox_have_their_ability(npa_data):
    script = npa_data["script"]
    assert _ab_want_for_form(script, 22) == "AB_PROTOSYNTHESIS"  # Great Tusk
    for form_id in (20, 21, 23):  # Iron Bundle, Iron Hands, Iron Treads
        assert _ab_want_for_form(script, form_id) == "AB_QUARKDRIVE", form_id


def test_old_paradox_and_form_abilities_are_unchanged(npa_data):
    script = npa_data["script"]
    assert _ab_want_for_form(script, 3) == "81 + formId"
    assert _ab_want_for_form(script, 8) == "AB_DEOXYSFORM"
    assert _ab_want_for_form(script, 13) == "AB_PROTOSYNTHESIS"
    assert _ab_want_for_form(script, 18) == "AB_QUARKDRIVE"
