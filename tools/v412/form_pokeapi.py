"""PokeAPI data of the new Pokemon: types, normal abilities, hidden ability, base stats.

Data file: tools/pokeapi/form_pokemon.json, written by tools/pokeapi/fetch_forms.py:
    {"pokemon": {slug: {"dex", "slug", "types", "abilities", "hidden", "stats"}}, "by_dex": {"21": "spearow"}}
`abilities` holds the normal abilities in slot order; the hidden one is in `hidden` (never also in `abilities`).
`stats` = [hp, attack, defense, special-attack, special-defense, speed].
Keys that PokeAPI does not have are listed in tools/pokeapi/form_pokemon_missing.json (a form key, or "mega:<index>").
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(WORK, "tools", "pokeapi", "form_pokemon.json")
MISSING = os.path.join(WORK, "tools", "pokeapi", "form_pokemon_missing.json")

# Mega_Name[0..43] of the map -> PokeAPI slug. 35 stands for Latias AND Latios (one hero, Latias' data is used).
# 36 "Dark Lugia" is not an official form: it has no slug and is listed as missing.
OLD_MEGA_SLUGS = {
    0: "venusaur-mega", 1: "charizard-mega-x", 2: "charizard-mega-y", 3: "blastoise-mega", 4: "beedrill-mega",
    5: "pidgeot-mega", 6: "alakazam-mega", 7: "gengar-mega", 8: "kangaskhan-mega", 9: "pinsir-mega",
    10: "gyarados-mega", 11: "steelix-mega", 12: "scizor-mega", 13: "mewtwo-mega-x", 14: "mewtwo-mega-y",
    15: "rayquaza-mega", 16: "blaziken-mega", 17: "sceptile-mega", 18: "tyranitar-mega", 19: "gardevoir-mega",
    20: "gallade-mega", 21: "salamence-mega", 22: "metagross-mega", 23: "lucario-mega", 24: "absol-mega",
    25: "slowbro-mega", 26: "sharpedo-mega", 27: "ampharos-mega", 28: "houndoom-mega", 29: "aerodactyl-mega",
    30: "manectric-mega", 31: "heracross-mega", 32: "altaria-mega", 33: "kyogre-primal", 34: "groudon-primal",
    35: "latias-mega", 36: None, 37: "swampert-mega", 38: "garchomp-mega", 39: "kyurem-black",
    40: "kyurem-white", 41: "diancie-mega", 42: "hoopa-unbound", 43: "necrozma-ultra",
}

# In-map form ids (PAX_Form_Id, names in PAX_Form_Appearance) -> PokeAPI slug. Ids 13..23 are also form keys of the family tree.
FORM_ID_SLUG = {
    1: "articuno-galar", 2: "zapdos-galar", 3: "moltres-galar", 4: "giratina-origin", 5: "dialga-origin",
    6: "palkia-origin", 7: "deoxys-attack", 8: "deoxys-defense", 9: "deoxys-speed", 10: "walking-wake",
    11: "gouging-fire", 12: "raging-bolt", 13: "roaring-moon", 14: "sandy-shocks", 15: "flutter-mane",
    16: "scream-tail", 17: "iron-thorns", 18: "iron-valiant", 19: "iron-jugulis", 20: "iron-bundle",
    21: "iron-hands", 22: "great-tusk", 23: "iron-treads",
}

_cache = {}


def _data():
    if "data" not in _cache:
        with open(DATA, encoding="utf-8") as fh:
            _cache["data"] = json.load(fh)
    return _cache["data"]


def pokemon(slug):
    """The record of a PokeAPI slug or form key (a cosmetic form resolves to its base species), or None."""
    data = _data()
    return data["pokemon"].get(slug) or data["pokemon"].get(data.get("aliases", {}).get(slug))


def by_dex(dex):
    """The record of the base species of National Dex number `dex`, or None."""
    slug = _data()["by_dex"].get(str(dex))
    return pokemon(slug) if slug else None


def missing():
    """Keys PokeAPI does not have (form keys, or "mega:<index>")."""
    with open(MISSING, encoding="utf-8") as fh:
        return json.load(fh)
