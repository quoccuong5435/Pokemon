"""Fetch PokeAPI metadata and Pokemon HOME sprites for the missing 38/39 Gen 1-4 species.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
CACHE_DIR = os.path.join(WORK, "analysis", "pokeapi_cache")
SPRITES_DIR = os.path.join(WORK, "analysis", "home_sprites")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(SPRITES_DIR, exist_ok=True)

MISSING_38 = [
    268, 273, 274, 275, 276, 277, 278, 279, 300, 301,
    316, 317, 325, 326, 339, 340, 351, 352, 353, 354,
    370, 401, 402, 412, 413, 414, 418, 419, 420, 421,
    422, 423, 431, 432, 434, 435, 441, 455
]
ALL_39 = MISSING_38 + [430]

HEADERS = {"User-Agent": "PokemonArena/4.2 (Warcraft III Modding Tool)"}

def http_get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.0 * (attempt + 1))

def http_download_file(url, dst_path):
    if os.path.isfile(dst_path) and os.path.getsize(dst_path) > 1000:
        return
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                tmp = dst_path + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, dst_path)
                return
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.0 * (attempt + 1))

def fetch_species_data(dex):
    cache_file = os.path.join(CACHE_DIR, f"g14_pokemon_{dex}.json")
    if os.path.isfile(cache_file) and os.path.getsize(cache_file) > 100:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Fetching PokeAPI data for dex {dex}...")
    p_data = http_get_json(f"https://pokeapi.co/api/v2/pokemon/{dex}")
    s_data = http_get_json(f"https://pokeapi.co/api/v2/pokemon-species/{dex}")

    # Name and slug
    slug = p_data["name"]
    name = s_data.get("names", [{}])[0].get("name", slug.capitalize())
    for n in s_data.get("names", []):
        if n.get("language", {}).get("name") == "en":
            name = n["name"]
            break

    # Types
    types = [t["type"]["name"] for t in sorted(p_data["types"], key=lambda x: x["slot"])]

    # Stats: hp, atk, def, spa, spd, spe
    stats_dict = {s["stat"]["name"]: s["base_stat"] for s in p_data["stats"]}
    stats = [
        stats_dict.get("hp", 50),
        stats_dict.get("attack", 50),
        stats_dict.get("defense", 50),
        stats_dict.get("special-attack", 50),
        stats_dict.get("special-defense", 50),
        stats_dict.get("speed", 50),
    ]
    bst = sum(stats)

    # Abilities
    abilities = [a["ability"]["name"] for a in sorted(p_data["abilities"], key=lambda x: x["slot"])]

    # Learnset (Gen 4/5/7/8 preferred, or latest)
    lv_moves = {}
    tm_moves = set()
    for m in p_data["moves"]:
        m_name = m["move"]["name"]
        for v in m["version_group_details"]:
            vg = v["version_group"]["name"]
            method = v["move_learn_method"]["name"]
            lvl = v["level_learned_at"]
            if method == "level-up":
                if m_name not in lv_moves or lvl < lv_moves[m_name]:
                    lv_moves[m_name] = lvl
            elif method == "machine":
                tm_moves.add(m_name)

    # Sort level moves by level
    sorted_lv = sorted([[lvl, m] for m, lvl in lv_moves.items()], key=lambda x: (x[0], x[1]))
    # Filter to reasonable level-up progression (max 15 moves)
    if len(sorted_lv) > 16:
        # keep key progression levels
        step = max(1, len(sorted_lv) // 14)
        filtered = [sorted_lv[0]] + sorted_lv[1:-1:step] + [sorted_lv[-1]]
        sorted_lv = filtered

    is_baby = s_data.get("is_baby", False)
    is_legend = s_data.get("is_legendary", False) or s_data.get("is_mythical", False)

    # Evolution info
    evo_from = None
    if s_data.get("evolves_from_species"):
        url = s_data["evolves_from_species"]["url"].rstrip("/")
        evo_from = int(url.split("/")[-1])

    # Stage
    stage = 0
    if evo_from is not None:
        stage = 1

    entry = {
        "dex": dex,
        "slug": slug,
        "name": name,
        "types": types,
        "stats": stats,
        "bst": bst,
        "abilities": abilities,
        "lv_moves": sorted_lv,
        "tm_moves": sorted(list(tm_moves))[:40],
        "stage": stage,
        "is_legend": is_legend,
        "is_baby": is_baby,
        "evo_from": evo_from,
        "evo_to": []
    }

    tmp_cache = cache_file + ".tmp"
    with open(tmp_cache, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)
    os.replace(tmp_cache, cache_file)
    return entry

def download_sprite(dex):
    dst = os.path.join(SPRITES_DIR, f"{dex}.png")
    if os.path.isfile(dst) and os.path.getsize(dst) > 2000:
        return
    home_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{dex}.png"
    art_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{dex}.png"
    print(f"Downloading sprite for dex {dex}...")
    try:
        http_download_file(home_url, dst)
    except Exception as e:
        print(f"  Home sprite failed for {dex}, trying official artwork: {e}")
        http_download_file(art_url, dst)

def main():
    print(f"Starting fetch for {len(MISSING_38)} missing pokedex entries...")
    fetched_entries = []
    for dex in MISSING_38:
        try:
            entry = fetch_species_data(dex)
            fetched_entries.append(entry)
        except Exception as e:
            print(f"Error fetching dex {dex}: {e}")

    # Fix stages for 3-stage lines:
    # If A -> B -> C: A is 0, B is 1, C is 2
    by_dex = {e["dex"]: e for e in fetched_entries}
    # Also load existing pokedex entries to check cross-gen evolution lines
    with open(os.path.join(HERE, "gen14_pokedex.json"), "r", encoding="utf-8") as f:
        existing = json.load(f)
    for ex in existing:
        by_dex[ex["dex"]] = ex

    for dex, e in by_dex.items():
        if e.get("evo_from") and e["evo_from"] in by_dex:
            parent = by_dex[e["evo_from"]]
            if parent.get("evo_from"):
                e["stage"] = 2
            else:
                e["stage"] = 1

    print(f"Starting download of HOME sprites for {len(ALL_39)} Pokemon...")
    for dex in ALL_39:
        try:
            download_sprite(dex)
        except Exception as e:
            print(f"Error downloading sprite for dex {dex}: {e}")

    # Save fetched missing 38 to a temporary json
    out_json = os.path.join(HERE, "fetched_missing_38.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump([by_dex[d] for d in MISSING_38 if d in by_dex], f, indent=2)
    print(f"Successfully saved {len([d for d in MISSING_38 if d in by_dex])} entries to {out_json}!")

if __name__ == "__main__":
    main()
