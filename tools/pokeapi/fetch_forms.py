"""PokeAPI data of the new Pokemon -> tools/pokeapi/form_pokemon.json and form_pokemon_missing.json.

Usage (from _PokemonArena2.0_work):  python -X utf8 -I tools/pokeapi/fetch_forms.py
Fetches the 105 form keys of form_assets, the old Mega slugs of form_pokeapi.OLD_MEGA_SLUGS and the 205 Gen 1-4 species of
tools/v412/gen14_pokedex.json. Cached per slug in analysis/pokeapi_cache_meta/form__<slug>.json (delete a cache file to
fetch that slug again). Read the result with tools/v412/form_pokeapi.py.
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(WORK, "tools"), os.path.join(WORK, "tools", "v412")]

import form_assets  # noqa: E402
import form_pokeapi  # noqa: E402

API = "https://pokeapi.co/api/v2/pokemon/"
CACHE = os.path.join(WORK, "analysis", "pokeapi_cache_meta")
STAT_ORDER = ("hp", "attack", "defense", "special-attack", "special-defense", "speed")
# our form key -> PokeAPI slug, only where they differ. These four are cosmetic forms: PokeAPI has no /pokemon entry for
# them (only /pokemon-form), and their official typing and abilities equal the base species.
ALIASES = {
    "cherrim-sunshine": "cherrim",
    "shellos-east": "shellos",
    "gastrodon-east": "gastrodon",
    "pichu-spiky-eared": "pichu",
}


def record(data):
    """One PokeAPI /pokemon/<slug> answer as the record stored in form_pokemon.json."""
    abilities = sorted(data["abilities"], key=lambda a: a["slot"])
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    return {
        "dex": int(data["species"]["url"].rstrip("/").split("/")[-1]),
        "slug": data["name"],
        "types": [t["type"]["name"] for t in sorted(data["types"], key=lambda t: t["slot"])],
        "abilities": [a["ability"]["name"] for a in abilities if not a["is_hidden"]],
        "hidden": next((a["ability"]["name"] for a in abilities if a["is_hidden"]), None),
        "stats": [stats[k] for k in STAT_ORDER],
    }


def get(slug):
    """The record of `slug`, from the cache or PokeAPI; None when PokeAPI says Not Found."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "form__%s.json" % slug)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    data = None
    for attempt in range(4):
        out = subprocess.run(["curl", "-s", "-m", "60", API + slug + "/"], capture_output=True)
        text = out.stdout.decode("utf-8", "replace")
        if text.strip().startswith("Not Found"):
            return None
        try:
            data = json.loads(text)
            break
        except ValueError:
            time.sleep(2 * (attempt + 1))
    if data is None:
        raise RuntimeError("cannot fetch %s" % slug)
    if isinstance(data, dict) and data.get("status") == 404:
        return None
    if not isinstance(data, dict) or "abilities" not in data:
        raise RuntimeError("unexpected answer for %s: %s" % (slug, str(data)[:200]))
    rec = record(data)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(rec, fh)
    os.replace(path + ".tmp", path)
    return rec


def form_keys():
    """The non-map form keys of the family tree, as form_assets.load_form_assets names them. Read straight from the tree:
    load_form_assets itself now needs the file this script writes."""
    _data, active = form_assets.load_active_tree()
    keys = set()
    for fam in active:
        for nid, n in fam["nodes"].items():
            if nid.startswith("F_") and n.get("st") != "map":
                keys.add(n.get("key", nid[2:]))
    return sorted(keys)


def main():
    meta = form_keys()
    with open(os.path.join(WORK, "tools", "v412", "gen14_pokedex.json"), encoding="utf-8") as fh:
        pokedex = json.load(fh)
    wanted = {}  # our key -> slug (None = no slug exists)
    for key in meta:
        wanted[key] = ALIASES.get(key, key)
    for idx, slug in form_pokeapi.OLD_MEGA_SLUGS.items():
        wanted["mega:%d" % idx] = slug
    for form_id, slug in form_pokeapi.FORM_ID_SLUG.items():
        wanted["formid:%d" % form_id] = slug
    import form_expansion  # late: it needs form_pokeapi, which needs nothing from here
    for key in form_expansion.EXISTING_FORM_HEROES:
        wanted["existing:%s" % key] = key
    for sp in pokedex:
        wanted["g14:%d" % sp["dex"]] = sp["slug"]

    todo = sorted({s for s in wanted.values() if s})
    with ThreadPoolExecutor(6) as pool:
        recs = dict(zip(todo, pool.map(get, todo)))

    pokemon = {slug: rec for slug, rec in recs.items() if rec}
    by_dex = {str(sp["dex"]): sp["slug"] for sp in pokedex if sp["slug"] in pokemon}
    missing = sorted(k for k, slug in wanted.items() if not slug or slug not in pokemon)
    with open(os.path.join(HERE, "form_pokemon.json"), "w", encoding="utf-8") as fh:
        json.dump({"pokemon": pokemon, "by_dex": by_dex, "aliases": dict(ALIASES)}, fh, ensure_ascii=False, indent=1,
                  sort_keys=True)
    with open(os.path.join(HERE, "form_pokemon_missing.json"), "w", encoding="utf-8") as fh:
        json.dump(missing, fh, ensure_ascii=False, indent=1)
    print("wrote %d records; %d keys missing:" % (len(pokemon), len(missing)))
    for k in missing:
        print("  ", k, "->", wanted[k])


if __name__ == "__main__":
    main()
