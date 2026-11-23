"""PokeAPI data of the new Pokemon (tools/pokeapi/form_pokemon.json, read through tools/v412/form_pokeapi.py)."""
import json
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import form_assets  # noqa: E402
import form_pokeapi  # noqa: E402


def test_aegislash_blade():
    p = form_pokeapi.pokemon("aegislash-blade")
    assert p["types"] == ["steel", "ghost"]
    assert "stance-change" in p["abilities"]


def test_every_form_key_present_or_listed_missing():
    _files, meta = form_assets.load_form_assets(compress_blp=False, pack_files=False)
    present = {k for k in meta if form_pokeapi.pokemon(k)}
    missing = set(form_pokeapi.missing())
    assert set(meta) == present | (missing & set(meta))
    assert not (present & missing)


def test_g14_entries_have_hidden_flag():
    with open(os.path.join(WORK, "tools", "v412", "gen14_pokedex.json"), encoding="utf-8") as fh:
        pokedex = json.load(fh)
    for sp in pokedex:
        rec = form_pokeapi.by_dex(sp["dex"])
        assert rec is not None, sp["dex"]
        assert "hidden" in rec, sp["dex"]


def test_hidden_not_in_abilities():
    with open(os.path.join(WORK, "tools", "pokeapi", "form_pokemon.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    for slug, rec in data["pokemon"].items():
        assert rec["hidden"] is None or rec["hidden"] not in rec["abilities"], slug


def test_cosmetic_forms_use_their_base_species_data():
    # PokeAPI has no /pokemon entry for these (only a /pokemon-form); official typing and abilities equal the base species
    for key, base in (("cherrim-sunshine", "cherrim"), ("shellos-east", "shellos"), ("gastrodon-east", "gastrodon"),
                      ("pichu-spiky-eared", "pichu")):
        assert form_pokeapi.pokemon(key) == form_pokeapi.pokemon(base), key
    assert form_pokeapi.pokemon("cherrim-sunshine")["types"] == ["grass"]
    assert form_pokeapi.missing() == ["mega:36"]  # Dark Lugia, not an official form


def test_old_mega_has_stats():
    slug = form_pokeapi.OLD_MEGA_SLUGS[1]  # Mega Charizard X
    assert slug == "charizard-mega-x"
    assert form_pokeapi.pokemon(slug)["stats"][1] == 130  # Attack


def test_form_ids_1_to_23_have_stats():
    # hidden_power needs the base stats of every in-map form id (Galarian birds, Origin, Deoxys, Paradox ...) for its role
    assert sorted(form_pokeapi.FORM_ID_SLUG) == list(range(1, 24))
    for form_id, slug in form_pokeapi.FORM_ID_SLUG.items():
        assert form_pokeapi.pokemon(slug) is not None, (form_id, slug)
    assert form_pokeapi.pokemon("giratina-origin")["stats"][2] == 100  # Defense 100


def test_heroes_that_were_already_in_the_map_have_stats():
    import form_expansion  # EXISTING_FORM_HEROES: Alolan lines etc. that the family tree marks as already in the map
    for key in form_expansion.EXISTING_FORM_HEROES:
        assert form_pokeapi.pokemon(key) is not None, key
