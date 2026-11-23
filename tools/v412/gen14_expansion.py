r"""Gen 1-4 Full Expansion for Pokemon Arena v4.2b+: adds 166 verified Gen 1-4 species
(completing 100% Gen 1 [151/151], 100% Gen 2 [100/100], 84% Gen 3 [114/135], 84% Gen 4 [89/107]
-> 454/493 Gen 1-4 species, raising total playable unique species in the map to ~510!).

Features:
- Official PokeAPI stats, types, abilities, level-up moves, TMs, and cross-gen evolutions
  (connecting seamlessly to existing Heroes like Pichu -> Pikachu, Porygon2 -> Porygon-Z, etc.).
- Automatic Melee vs Ranged (Archer) weapon setup matching `melee_ranged_classifier.py`.
- 4 new Gen 2/4 Legendaries/Mythicals (Lugia, Phione, Manaphy, Shaymin) integrated into the
  Roaming Random Legends Boss + 50% Soul Drop + Center Altar transform system.
- 162 regular species integrated into Wild Creeps (`nG*`), Wild Pool (powers 1..10, bumping
  `Wild_PowStride` 400 -> 1000), Soul Drops (`IG*`), `-pick` Type Dialog (`Pick_InitData`),
  `-random` (`Rand_Type`), and Gym Pool (`Gym_Pool`).
- Isolated asset namespace (`PkFx\G14\...`, `PkFx\G14\t\...`, `BTN_G14_*`), 0 missing textures,
  BLP1-JPEG compression (256px q72 regular / 512px q75 legends), and op-limit-safe JASS chunking
  via `ExecuteFunc("G14_Data*")` and `ExecuteFunc("G14_Wild*")`.
"""
import json
import os
import re
import struct
from PIL import Image
import numpy as np

import ability_names
import form_pokeapi
import map_optimizer
import melee_ranged_classifier
import mpq
import objdata

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)

PW_MAP = os.path.join(MAPS, "Pokemon World V1.71.w3x")
RPG79_MAP = os.path.join(MAPS, "79.PokemonRPG.w3x")
MEW_MAP = os.path.join(MAPS, "Pokemon Mew RPG 3.20B.w3x")

POKEDEX_JSON = os.path.join(HERE, "gen14_pokedex.json")
MODELS_JSON = os.path.join(HERE, "gen14_models.json")
ICON_CACHE = os.path.join(HERE, "g14_icons_cache")

DIG = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BLIZZARD_PREFIXES = (
    "textures\\", "replaceabletextures\\", "units\\", "abilities\\",
    "environment\\", "objects\\", "ui\\", "buildings\\", "doodads\\", "sharedmodels\\",
)

TYPE_IDX = {
    "bug": 0, "dark": 1, "dragon": 2, "electric": 3, "fairy": 4, "fighting": 5,
    "fire": 6, "flying": 7, "ghost": 8, "grass": 9, "ground": 10, "ice": 11,
    "normal": 12, "poison": 13, "psychic": 14, "rock": 15, "steel": 16, "water": 17,
}
TYPE_WORD = {k: k.capitalize() for k in TYPE_IDX}
ATTACK_COLOR = {
    "bug": "ffa6b91a", "dark": "ff705746", "dragon": "ff6f35fc", "electric": "fff7d02c",
    "fairy": "ffd685ad", "fighting": "ffc22e28", "fire": "ffee8130", "flying": "ffa98ff3",
    "ghost": "ff735797", "grass": "ff7ac74c", "ground": "ffe2bf65", "ice": "ff96d9d6",
    "normal": "ffa8a77a", "poison": "ffa33ea1", "psychic": "fff95587", "rock": "ffb6a136",
    "steel": "ffb7b7ce", "water": "ff6390f0",
}
TYPE_FALLBACK_AB = {
    "bug": 4, "dark": 15, "dragon": 15, "electric": 5, "fairy": 8, "fighting": 27,
    "fire": 2, "flying": 10, "ghost": 10, "grass": 1, "ground": 14, "ice": 18,
    "normal": 16, "poison": 7, "psychic": 9, "rock": 18, "steel": 18, "water": 3,
}
# Guaranteed authentic fallback moves (Mv_Label indices) if a species (e.g. Unown/Wobbuffet) has < 4 mapped moves
TYPE_FALLBACK_MOVES = {
    "bug": [37, 250, 297, 304], "dark": [54, 51, 200, 15], "dragon": [67, 68, 69, 65],
    "electric": [289, 285, 290, 245], "fairy": [56, 178, 15, 209], "fighting": [32, 45, 72, 142],
    "fire": [83, 104, 96, 186], "flying": [3, 7, 134, 315], "ghost": [243, 244, 246, 182],
    "grass": [170, 84, 159, 255], "ground": [79, 80, 180, 228], "ice": [147, 140, 23, 141],
    "normal": [280, 127, 26, 137], "poison": [252, 299, 253, 201], "psychic": [46, 209, 214, 118],
    "rock": [227, 228, 267, 205], "steel": [173, 106, 151, 265], "water": [308, 237, 276, 136],
}

HERO_TMPL = ("E003", "E007", "E00E")
WILD_TMPL = ("nX5B", "nX26", "nX4B")
LEG_WILD_TMPL = "nL18"
SOUL_TMPL = "IU5B"
WILD_POW = ((1, 2), (3, 5), (6, 10))


class _PWArchive(mpq.MPQ):
    def _find_header(self):
        return 1024


def clean_ascii(name: str) -> str:
    s = (name or "").replace("♀", " F").replace("♂", " M").replace("é", "e").replace("’", "'")
    return re.sub(r"[^\x20-\x7e]", "", s).strip()


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", clean_ascii(name).lower().replace("'", "").replace(".", "")).strip("-")


def safe_file_slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", clean_ascii(name))


def hero_id(k: int) -> str:
    return "EG" + DIG[k // 36] + DIG[k % 36]


def wild_id(k: int) -> str:
    return "nG" + DIG[k // 36] + DIG[k % 36]


def soul_id(k: int) -> str:
    return "IG" + DIG[k // 36] + DIG[k % 36]


NEW_3D_MDX_DIR = os.path.join(WORK, "imports", "pokemon_3d_mdx")
NEW_3D_TEX_DIR = os.path.join(NEW_3D_MDX_DIR, "textures")

# Authentic 3D substitute mapping for any species lacking standalone 3D models (fallback only):
SUBSTITUTE_3D_MAP = {
    268: 266, 273: 331, 274: 332, 275: 332, 276: 397, 277: 398, 278: 396, 279: 398,
    300: 52, 301: 53, 316: 88, 317: 89, 325: 96, 326: 97, 339: 194, 340: 195,
    351: 175, 352: 252, 353: 355, 354: 356, 370: 223, 401: 167, 402: 168,
    412: 204, 413: 205, 414: 267, 418: 158, 419: 184, 420: 43, 421: 44,
    422: 194, 423: 195, 430: 198, 431: 52, 432: 53, 434: 261, 435: 262,
    441: 198, 455: 71,
}

SUBSTITUTE_PW_PATHS = {
    43: "Unit\\043.mdx", 44: "Unit\\044.mdx", 52: "Unit\\052.mdx", 53: "Unit\\053.mdx",
    71: "Unit\\071.mdx", 88: "Unit\\088.mdx", 89: "Unit\\089.mdx", 96: "Unit\\096.mdx",
    97: "Unit\\097.mdx", 158: "Unit\\158.mdx", 167: "Unit\\167.mdx", 168: "Unit\\168.mdx", 175: "Unit\\175.mdx",
    184: "Unit\\184.mdx", 194: "Unit\\194.mdx", 195: "Unit\\195.mdx",
    198: "Unit\\198.mdx", 204: "Unit\\204.mdx", 205: "Unit\\205.mdx", 223: "Unit\\223.mdx",
    252: "Unit\\252.mdx", 261: "Unit\\261.mdx", 262: "Unit\\262.mdx", 266: "Unit\\266.mdx",
    267: "Unit\\267.mdx", 331: "Unit\\331.mdx", 332: "Unit\\332.mdx", 355: "Unit\\355.mdx",
    356: "Unit\\356.mdx", 396: "Unit\\396.mdx", 397: "Unit\\397.mdx", 398: "Unit\\398.mdx",
}


def load_species_entries():
    """Returns ordered list of 166 verified Gen 1-4 species dicts with assigned rawcode IDs and model info."""
    with open(POKEDEX_JSON, encoding="utf-8") as fh:
        pokedex = json.load(fh)
    with open(MODELS_JSON, encoding="utf-8") as fh:
        models = json.load(fh)

    entries = []
    k = 0
    for sp in pokedex:
        ds = str(sp["dex"])
        if ds not in models:
            continue
        mi = dict(models[ds])
        dex_num = int(sp["dex"])

        # Check for newly converted authentic 3D models first
        local_mdx = os.path.join(NEW_3D_MDX_DIR, f"{dex_num}.mdx")
        if os.path.isfile(local_mdx):
            mi["src"] = "LOCAL_3D"
            mi["ref"] = local_mdx
        elif mi.get("src") == "2.5D" and dex_num in SUBSTITUTE_3D_MAP:
            sub_d = SUBSTITUTE_3D_MAP[dex_num]
            mi["src"] = "PW"
            mi["ref"] = SUBSTITUTE_PW_PATHS[sub_d]

        nm = clean_ascii(sp["name"])
        stage = int(sp["stage"])
        is_leg = bool(sp["is_legend"])
        bh = float(mi.get("bh") or 100.0)
        if mi.get("src") == "LOCAL_3D":
            # g14_reconvert.py already sizes these models to their target (GEMINI.md section 21), so usca 1.0;
            # Donphan / Miltank 0.95 = the user's numbers (section 13). The old 0.95 / 1.10 / 1.25 per stage was on
            # models whose raw size went from 17 to 34564.
            scale = 0.95 if dex_num in (232, 241) else 1.0
        elif dex_num == 49:  # Venomoth: keep proportionate moth scale (down from oversized 1.95)
            scale = 0.95
        elif dex_num == 232:  # Donphan: user request to reduce scale (1.22 -> 0.95)
            scale = 0.95
        elif dex_num == 241:  # Miltank: raw mesh height is 881.8! scale 0.11 brings it to natural ~97 height
            scale = 0.11
        elif dex_num == 336:  # Seviper: body is coiled/thin, scale up to 1.30
            scale = 1.30
        else:
            target_h = 175.0 if is_leg else (82.0 if stage == 0 else (108.0 if stage == 1 else 132.0))
            scale = round(max(0.35, min(1.35, target_h / max(15.0, bh))), 2)
        fslug = safe_file_slug(nm)
        entries.append(dict(
            k=k,
            dex=dex_num,
            name=nm,
            slug=sp["slug"],
            hero=hero_id(k),
            wild=wild_id(k),
            soul=soul_id(k),
            types=sp["types"],
            stats=sp["stats"],
            bst=int(sp["bst"]),
            abilities=sp["abilities"],
            lv_moves=sp["lv_moves"],
            tm_moves=sp["tm_moves"],
            stage=stage,
            is_legend=is_leg,
            evo_from=sp.get("evo_from"),
            evo_to=sp.get("evo_to") or [],
            src=mi["src"],
            ref=mi["ref"],
            btn_src=mi.get("btn"),
            dst_mdx=f"PkFx\\G14\\{dex_num:03d}_{fslug}.mdx",
            icon_path=f"ReplaceableTextures\\CommandButtons\\BTN_G14_{dex_num:03d}.blp",
            dis_icon_path=f"ReplaceableTextures\\CommandButtonsDisabled\\DISBTN_G14_{dex_num:03d}.blp",
            scale=scale,
            is_melee=melee_ranged_classifier.classify_species_is_melee(sp["types"], sp["stats"]),
        ))
        k += 1
    return entries


def _stat_values(sp):
    hp, atk, de, spa, spd, spe = sp["stats"]
    cd_map = {0: 2000, 1: 1900, 2: 1800, 3: 1750}
    return dict(
        hp=40 * hp, str=atk, agi=spe, int=spa, de=de, spd=spd,
        main=1 if atk >= spa else 3,
        cd=cd_map.get(sp["stage"], 1850),
        armor=int(round(0.6 * de)),
    )


def _type_label(types):
    return "&".join(TYPE_WORD[t] for t in types if t in TYPE_WORD) + " Pokemon"


def _set_usca(u, val: float):
    ftype = 1
    for m in u.mods:
        if m.field == "usca":
            ftype = m.type
            break
    u.set("usca", ftype, float(val))


def _clone_obj(src_obj, new_id: str, overrides: dict):
    ov = dict(overrides)
    mods = []
    for m in src_obj.mods:
        if m.field in ov:
            val, ftype = ov.pop(m.field)
            mods.append(objdata.Mod(m.field, ftype, val, m.level, m.data, m.end))
        else:
            mods.append(objdata.Mod(m.field, m.type, m.value, m.level, m.data, m.end))
    for field, (val, ftype) in ov.items():
        mods.append(objdata.Mod(field, ftype, val))
    return objdata.Obj(src_obj.orig, new_id, mods)


def _build_existing_dex_map(w3u) -> dict:
    """Builds {dex: hero_id} for existing heroes in w3u using tools/learnsets.json + legend_expansion_data."""
    ls_path = os.path.join(WORK, "tools", "learnsets.json")
    name_to_dex = {}
    if os.path.isfile(ls_path):
        with open(ls_path, encoding="utf-8") as fh:
            for k, v in json.load(fh).get("species", {}).items():
                if "dex" in v:
                    name_to_dex[slug(k)] = int(v["dex"])
                    if "name" in v:
                        name_to_dex[slug(v["name"])] = int(v["dex"])
    special = {
        "nidoran": 32, "mr-mime": 122, "farfetchd": 83, "ho-oh": 250,
        "deoxys": 386, "giratina": 487, "leafleon": 470, "politeod": 186,
        "porygon2": 233, "meganium": 154, "mime-jr": 439, "porygon-z": 474,
    }
    name_to_dex.update(special)

    dex_to_hid = {}
    for u in w3u.original + w3u.custom:
        if not u.id or not u.id[0].isupper():
            continue
        if u.id.startswith(("EG", "hM")):
            continue
        upro = str(u.get("upro") or "").strip()
        if not upro or upro.lower().startswith("alolan"):
            continue
        sl = slug(upro)
        dn = name_to_dex.get(sl)
        if dn and 1 <= dn <= 493:
            # Prefer E0*/EN*/EP*/EL* over duplicate P* IDs
            if dn not in dex_to_hid or (dex_to_hid[dn].startswith("P") and not u.id.startswith("P")):
                dex_to_hid[dn] = u.id
    return dex_to_hid


def _parse_jass_maps(script: str):
    """Extracts move slug -> index directly from war3map.j."""
    move_map = {}
    for idx_s, label in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        m = re.match(r"(.*) \((\w+), power \d+\)", label)
        if m:
            move_map.setdefault(slug(m.group(1)), int(idx_s))
    # Also include status moves
    for idx_s, label in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        idx = int(idx_s)
        if idx >= 300:
            nm = label.split(" (")[0].strip()
            move_map.setdefault(slug(nm), idx)

    return move_map


def _resolve_ability(sp, ab_index: dict) -> int:
    """Number of the species' first NORMAL PokeAPI ability the map has (the reworked number wins, see ability_names);
    the hidden one is for the Ability Patch, never the default. Without one, the old by-type placeholder."""
    rec = form_pokeapi.by_dex(sp["dex"])
    number = ability_names.first_known(ab_index, rec["abilities"]) if rec else None
    return number if number is not None else TYPE_FALLBACK_AB.get(sp["types"][0], 16)


def _chunk_jass(lines: list, prefix: str, max_per_func: int = 340):
    """Splits JASS lines into op-limit-safe functions `prefix01..prefixNN`."""
    funcs = []
    names = []
    for i in range(0, max(1, len(lines)), max_per_func):
        idx = len(names) + 1
        fn = f"{prefix}{idx:02d}"
        names.append(fn)
        body = "\n".join(lines[i:i + max_per_func])
        funcs.append(f"function {fn} takes nothing returns nothing\n{body}\nendfunction")
    return "\n\n".join(funcs), names


def _replace_once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[gen14] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


def _patch_picker(script: str, entries: list, all_dex_to_hid: dict) -> str:
    """Adds all new non-legend base-form Gen 1-4 Pokemon into Pick_InitData (paginated Type dialog)."""
    m = re.search(r"function Pick_InitData takes nothing returns nothing\n([\s\S]*?)endfunction", script)
    if not m:
        raise ValueError("[gen14] Pick_InitData not found")
    body = m.group(1)

    types_list = dict(re.findall(r"set Pick_Type\[(\d+)\] = '([^']+)'", body))
    names_list = dict(re.findall(r'set Pick_Name\[(\d+)\] = "([^"]*)"', body))
    g_names = dict(re.findall(r'set Pick_TName\[(\d+)\] = "([^"]*)"', body))
    g_first = dict(re.findall(r"set Pick_TFirst\[(\d+)\] = (\d+)", body))
    g_count = dict(re.findall(r"set Pick_TCount\[(\d+)\] = (\d+)", body))

    # Reconstruct ordered groups
    groups = []
    group_by_name = {}
    for gi in sorted(g_names, key=int):
        gn = g_names[gi]
        f0 = int(g_first[gi])
        cnt = int(g_count[gi])
        members = [(types_list[str(i)], names_list[str(i)]) for i in range(f0, f0 + cnt)]
        groups.append((gn, members))
        group_by_name[gn] = members

    # Ensure every type exists if needed
    existing_ids = {t for _, ms in groups for t, _ in ms}
    added_pick = 0
    for sp in entries:
        if sp["is_legend"]:
            continue
        # Base form = no evolution parent present in the map
        parent_dex = sp["evo_from"]
        if parent_dex and parent_dex in all_dex_to_hid:
            continue
        if sp["hero"] in existing_ids:
            continue
        gn = TYPE_WORD[sp["types"][0]]
        if gn not in group_by_name:
            ms = []
            groups.append((gn, ms))
            group_by_name[gn] = ms
        group_by_name[gn].append((sp["hero"], sp["name"]))
        existing_ids.add(sp["hero"])
        added_pick += 1

    # Sort each type's entries alphabetically by Pokemon name
    for gn, ms in groups:
        ms.sort(key=lambda x: x[1].lower())

    total = sum(len(ms) for _, ms in groups)
    out = [f"    set Pick_N = {total}"]
    k = 0
    for _gn, ms in groups:
        for hid, nm in ms:
            out.append(f"    set Pick_Type[{k}] = '{hid}'")
            out.append(f'    set Pick_Name[{k}] = "{nm}"')
            k += 1
    out.append(f"    set Pick_TN = {len(groups)}")
    k = 0
    for gi, (gn, ms) in enumerate(groups):
        out.append(f'    set Pick_TName[{gi}] = "{gn}"')
        out.append(f"    set Pick_TFirst[{gi}] = {k}")
        out.append(f"    set Pick_TCount[{gi}] = {len(ms)}")
        k += len(ms)

    new_fn = "function Pick_InitData takes nothing returns nothing\n" + "\n".join(out) + "\nendfunction"
    return _replace_once(script, m.group(0), new_fn, "Pick_InitData"), added_pick


def patch_objects_and_script(w3u, items_slk, item_func: str, script: str):
    """Creates all 166 Gen 1-4 Hero units, Wild/Boss units, Soul items, and JASS registrations."""
    entries = load_species_entries()
    by_id = {u.id: u for u in w3u.original + w3u.custom}
    existing_dex_to_hid = _build_existing_dex_map(w3u)

    all_dex_to_hid = dict(existing_dex_to_hid)
    g14_dex_to_entry = {}
    for sp in entries:
        all_dex_to_hid[sp["dex"]] = sp["hero"]
        g14_dex_to_entry[sp["dex"]] = sp

    move_map = _parse_jass_maps(script)
    ab_index = ability_names.ability_index(script)

    # Check existing Evo_From IDs so we never add a conflicting second linear level-up evo
    existing_evo_from = set(re.findall(r"set Evo_From\[\d+\] = '([^']+)'", script))

    # 1. Create w3u objects + ItemData.slk + ItemFunc.txt
    soul_tmpl_row = items_slk.find(SOUL_TMPL)
    if soul_tmpl_row is None:
        raise ValueError(f"[gen14] Soul template {SOUL_TMPL} not found in ItemData.slk")

    func_additions = []
    for sp in entries:
        hid, wid, sid = sp["hero"], sp["wild"], sp["soul"]
        if hid in by_id or wid in by_id or items_slk.find(sid) is not None:
            raise ValueError(f"[gen14] ID collision: {hid} / {wid} / {sid}")

        v = _stat_values(sp)
        t0 = sp["types"][0]
        t_lbl = _type_label(sp["types"])
        mdl_val = sp["dst_mdx"][:-4] + ".mdl"

        # Evolution note for tooltip
        evo_note = ""
        for target_dex, evo_lv in sp["evo_to"]:
            if target_dex in all_dex_to_hid and sp["dex"] != 133:
                tname = g14_dex_to_entry[target_dex]["name"] if target_dex in g14_dex_to_entry else str(by_id[all_dex_to_hid[target_dex]].get("upro") or "")
                if tname:
                    evo_note = f" Evolves into |cffffcc00{tname}|r at lv {evo_lv}."
                    break
        style_lbl = "Melee" if sp["is_melee"] else "Ranged"
        utub = (
            f"|cffffcc00{sp['name']}|r ({t_lbl}).{evo_note}"
            f"|n|c{ATTACK_COLOR[t0]}Basic attack: {TYPE_WORD[t0]} ({style_lbl})|r"
        )

        # Authentic movement type & height setup:
        # Non-flying walkers must be grounded on foot (umvh = 0.0), flying Pokemon float at natural eye level (65.0)
        is_flyer = "flying" in sp["types"] or sp["dex"] in (201, 351, 355, 356)  # flying type or levitating ghosts/unown
        mov_type = "hover" if is_flyer else "foot"
        fly_height = 65.0 if is_flyer else 0.0

        # Clone Hero unit
        ht_id = HERO_TMPL[min(2, sp["stage"])]
        h_src = by_id[ht_id]
        h_obj = _clone_obj(h_src, hid, {
            "umdl": (mdl_val, 3),
            "uico": (sp["icon_path"], 3),
            "ussi": (sp["icon_path"], 3),
            "upro": (f"#{sp['dex']} {sp['name']}", 3),
            "unam": (t_lbl, 3),
            "utub": (utub, 3),
            "uawt": (f"Revive {sp['name']}", 3),
            "utip": (f"Summon {sp['name']}", 3),
            "utpr": (f"Revive {sp['name']}", 3),
            "uhpm": (v["hp"], 0),
            "ustr": (v["str"], 0),
            "uagi": (v["agi"], 0),
            "uint": (v["int"], 0),
            "ustp": (round(v["str"] / 50.0, 2), 2),
            "uagp": (round(v["agi"] / 50.0, 2), 2),
            "uinp": (round(v["int"] / 50.0, 2), 2),
            "upra": ("STR" if v["main"] == 1 else "INT", 3),
            "udef": (v["armor"], 0),
            "usca": (float(sp["scale"]), 1),
            "umvt": (mov_type, 3),
            "umvh": (float(fly_height), 1),
            "uhab": ("", 3),
        })
        melee_ranged_classifier.apply_weapon_for_unit(h_obj, is_melee=sp["is_melee"], primary_type=t0, is_legend=sp["is_legend"])
        w3u.custom.append(h_obj)
        by_id[hid] = h_obj

        # Clone Wild / Legend Boss unit
        w_src = by_id[LEG_WILD_TMPL] if sp["is_legend"] else by_id[WILD_TMPL[min(2, sp["stage"])]]
        w_scale = round(min(2.20, sp["scale"] * 1.15), 2) if sp["is_legend"] else float(sp["scale"])
        w_obj = _clone_obj(w_src, wid, {
            "umdl": (mdl_val, 3),
            "unam": (sp["name"], 3),
            "uico": (sp["icon_path"], 3),
            "usca": (w_scale, 1),
            "umvt": (mov_type, 3),
            "umvh": (float(fly_height), 1),
        })
        melee_ranged_classifier.apply_weapon_for_unit(w_obj, is_melee=sp["is_melee"], primary_type=t0, is_legend=sp["is_legend"])
        w3u.custom.append(w_obj)
        by_id[wid] = w_obj

        # Clone Soul item in ItemData.slk & ItemFunc.txt
        row = dict(soul_tmpl_row)
        row[1] = f'"{sid}"'
        items_slk.rows.append(row)
        soul_desc = f"Soul of Legend {sp['name']}." if sp["is_legend"] else f"Soul of a wild {sp['name']}."
        func_additions.append(
            f"[{sid}]\r\n"
            f"Name={sp['name']} Soul\r\n"
            f"Tip={sp['name']} Soul\r\n"
            f"Ubertip=Equip in slot 1 and walk into the circle at the centre of the map to become |cffffcc00{sp['name']}|r.\r\n"
            f"Description={soul_desc}\r\n"
            f"Art={sp['icon_path']}\r\n"
        )

    item_func = item_func.rstrip() + "\r\n" + "".join(func_additions)

    # 2. Build JASS data lines (Stats, Abilities, Moves, TMs, Evos, Rand, Gym, Legends)
    data_lines = []
    wild_lines = []
    evos_added = 0
    legends_added = 0
    wild_added = 0
    registered_evo_from = set(existing_evo_from)

    for sp in entries:
        hid, wid, sid = sp["hero"], sp["wild"], sp["soul"]
        v = _stat_values(sp)
        ab_id = _resolve_ability(sp, ab_index)
        t1 = TYPE_IDX[sp["types"][0]] + 1
        t2 = (TYPE_IDX[sp["types"][1]] + 1) if len(sp["types"]) > 1 else 0

        data_lines.extend([
            f"    call SaveInteger(Mega_HT, '{hid}', 80, {v['hp']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 81, {v['hp']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 82, {v['str']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 83, {v['agi']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 84, {v['int']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 85, {v['main']})",
            f"    call SaveInteger(Mega_HT, '{hid}', 86, {v['cd']})",
            f"    call SaveInteger(Fx_HT, '{hid}', 1, {v['de']})",
            f"    call SaveInteger(Fx_HT, '{hid}', 2, {v['spd']})",
            f"    call SaveInteger(Ab_HT, '{hid}', 0, {ab_id})",
            f"    call SaveInteger(Ab_HT, '{hid}', 53, {t1})",
        ])
        if t2:
            data_lines.append(f"    call SaveInteger(Ab_HT, '{hid}', 54, {t2})")

        # Level-up moves (deduplicated, sorted by level; fallback if < 4 moves)
        lv_seen = {}
        for lv, mslug in sp["lv_moves"]:
            mi = move_map.get(mslug)
            if mi is not None and mi not in lv_seen:
                lv_seen[mi] = max(1, min(75, int(lv)))
        if len(lv_seen) < 4:
            for fb_lv, fb_mi in zip((1, 14, 30, 48), TYPE_FALLBACK_MOVES[sp["types"][0]]):
                if fb_mi not in lv_seen:
                    lv_seen[fb_mi] = fb_lv
        for mi, lv in sorted(lv_seen.items(), key=lambda kv: (kv[1], kv[0]))[:14]:
            data_lines.append(f"    call Fx_AddLv('{hid}', {mi}, {lv})")

        # TMs (capped at 16 most relevant per species to keep script compact)
        tm_seen = []
        for mslug in sp["tm_moves"]:
            mi = move_map.get(mslug)
            if mi is not None and mi not in tm_seen:
                tm_seen.append(mi)
                if len(tm_seen) >= 16:
                    break
        for mi in tm_seen:
            data_lines.append(f"    call Fx_AddTm('{hid}', {mi})")

        # Evolutions: both outgoing (new -> new/existing) and incoming (existing -> new)
        for target_dex, evo_lv in sp["evo_to"]:
            if target_dex in all_dex_to_hid and hid not in registered_evo_from:
                to_hid = all_dex_to_hid[target_dex]
                data_lines.extend([
                    f"    set Evo_From[Evo_N] = '{hid}'",
                    f"    set Evo_To[Evo_N] = '{to_hid}'",
                    f"    set Evo_Level[Evo_N] = {evo_lv}",
                    "    set Evo_N = Evo_N + 1",
                    f"    call SaveInteger(Ab_HT, '{hid}', 699, 1)",
                    f"    call SaveInteger(Ab_HT, '{hid}', 700, '{to_hid}')",
                    f"    call SaveInteger(Ab_HT, '{hid}', 701, {evo_lv})",
                ])
                registered_evo_from.add(hid)
                evos_added += 1

        # Incoming cross-gen evolution from an EXISTING hero (e.g. Porygon2 -> Porygon-Z, Magneton -> Magnezone)
        parent_dex = sp["evo_from"]
        if parent_dex and parent_dex in existing_dex_to_hid and parent_dex != 133:
            p_hid = existing_dex_to_hid[parent_dex]
            if p_hid not in registered_evo_from:
                evo_lv = 36 if sp["stage"] >= 2 else 22
                data_lines.extend([
                    f"    set Evo_From[Evo_N] = '{p_hid}'",
                    f"    set Evo_To[Evo_N] = '{hid}'",
                    f"    set Evo_Level[Evo_N] = {evo_lv}",
                    "    set Evo_N = Evo_N + 1",
                    f"    call SaveInteger(Ab_HT, '{p_hid}', 699, 1)",
                    f"    call SaveInteger(Ab_HT, '{p_hid}', 700, '{hid}')",
                    f"    call SaveInteger(Ab_HT, '{p_hid}', 701, {evo_lv})",
                ])
                registered_evo_from.add(p_hid)
                evos_added += 1

        # Base non-legend forms join -random & Gym Pool
        if not sp["is_legend"] and (not parent_dex or parent_dex not in all_dex_to_hid):
            data_lines.extend([
                f"    set Rand_Type[Rand_N] = '{hid}'",
                "    set Rand_N = Rand_N + 1",
                f"    set Gym_Pool[Gym_PoolN] = '{hid}'",
                "    set Gym_PoolN = Gym_PoolN + 1",
            ])

        # Legend vs Regular Wild & Soul registration
        if sp["is_legend"]:
            data_lines.extend([
                f"    set Leg_Type[Leg_N] = '{wid}'",
                f"    set Leg_Soul[Leg_N] = '{sid}'",
                f'    set Leg_Name[Leg_N] = "{sp["name"]}"',
                "    set Leg_N = Leg_N + 1",
                f"    set Soul_Item[Soul_N] = '{sid}'",
                f"    set Soul_Hero[Soul_N] = '{hid}'",
                "    set Soul_N = Soul_N + 1",
                f"    call SaveInteger(Mega_HT, '{wid}', 8, '{sid}')",
                f"    call SaveInteger(Mega_HT, '{wid}', 30, {t1})",
                f"    call SaveInteger(Ab_HT, '{wid}', 0, {ab_id})",
                f"    call SaveInteger(Ab_HT, '{wid}', 53, {t1})",
                f"    call SaveInteger(Fx_HT, '{wid}', 1, {v['de']})",
                f"    call SaveInteger(Fx_HT, '{wid}', 2, {v['spd']})",
            ])
            if t2:
                data_lines.append(f"    call SaveInteger(Ab_HT, '{wid}', 54, {t2})")
            legends_added += 1
        else:
            lo, hi = WILD_POW[min(2, sp["stage"])]
            wild_lines.extend([
                f"    set Wild_Type[Wild_TypeN] = '{wid}'",
                "    set Wild_TypeN = Wild_TypeN + 1",
                f"    call SaveInteger(Mega_HT, '{wid}', 8, '{sid}')",
                f"    call SaveInteger(Mega_HT, '{wid}', 30, {t1})",
                f"    call SaveInteger(Mega_HT, '{wid}', 39, 1)",
                f"    call SaveInteger(Mega_HT, '{wid}', 47, {lo})",
                f"    call SaveInteger(Mega_HT, '{wid}', 48, {hi})",
                f"    call SaveInteger(Ab_HT, '{wid}', 0, {ab_id})",
                f"    call SaveInteger(Ab_HT, '{wid}', 53, {t1})",
                f"    call SaveInteger(Fx_HT, '{wid}', 1, {v['de']})",
                f"    call SaveInteger(Fx_HT, '{wid}', 2, {v['spd']})",
                f"    set Soul_Item[Soul_N] = '{sid}'",
                f"    set Soul_Hero[Soul_N] = '{hid}'",
                "    set Soul_N = Soul_N + 1",
            ])
            if t2:
                wild_lines.append(f"    call SaveInteger(Ab_HT, '{wid}', 54, {t2})")
            for target_dex, _elv in sp["evo_to"]:
                if target_dex in g14_dex_to_entry:
                    wild_lines.append(f"    call SaveInteger(Mega_HT, '{wid}', 45, '{g14_dex_to_entry[target_dex]['wild']}')")
                    break
            for pw in range(lo, hi + 1):
                wild_lines.extend([
                    f"    set Wild_Pool[Wild_PoolN] = '{wid}'",
                    f"    set Wild_PoolPow[Wild_PoolN] = {pw}",
                    "    set Wild_PoolN = Wild_PoolN + 1",
                ])
            wild_added += 1

    # 3. Patch war3map.j cleanly:
    # 3a. Bump Wild_PowStride 400 -> 1000
    script = _replace_once(
        script,
        "constant integer Wild_PowStride = 400",
        "constant integer Wild_PowStride = 1000",
        "Wild_PowStride bump",
    )

    # 3b. Update Pick_InitData with all new Gen 1-4 base forms
    script, added_pick = _patch_picker(script, entries, all_dex_to_hid)

    # 3c. Insert G14_Data* and G14_Wild* chunked functions right after Fx_Data16
    data_jass, data_fns = _chunk_jass(data_lines, "G14_Data", max_per_func=340)
    wild_jass, wild_fns = _chunk_jass(wild_lines, "G14_Wild", max_per_func=340)

    p = script.find("function Fx_Data16 takes nothing returns nothing")
    if p < 0:
        raise ValueError("[gen14] function Fx_Data16 not found")
    p_end = script.find("endfunction", p)
    if p_end < 0:
        raise ValueError("[gen14] endfunction of Fx_Data16 not found")
    ins = p_end + len("endfunction")
    script = script[:ins] + "\n\n" + data_jass + "\n\n" + wild_jass + script[ins:]

    # 3d. Hook G14_Data* right after ExecuteFunc("Fx_Data16")
    data_calls = "\n".join(f'    call ExecuteFunc("{fn}")' for fn in data_fns)
    script = _replace_once(
        script,
        '    call ExecuteFunc("Fx_Data16")',
        '    call ExecuteFunc("Fx_Data16")\n' + data_calls,
        "Hook G14_Data after Fx_Data16",
    )

    # 3e. Hook G14_Wild* right BEFORE ExecuteFunc("Wild_IndexPool") in Mega_Init
    wild_calls = "\n".join(f'    call ExecuteFunc("{fn}")' for fn in wild_fns)
    script = _replace_once(
        script,
        '    call ExecuteFunc("Wild_IndexPool")',
        wild_calls + '\n    call ExecuteFunc("Wild_IndexPool")',
        "Hook G14_Wild before Wild_IndexPool",
    )

    stats = {
        "g14_species": len(entries),
        "g14_wild": wild_added,
        "g14_legends": legends_added,
        "g14_evos": evos_added,
        "g14_pick_added": added_pick,
        "g14_data_chunks": len(data_fns),
        "g14_wild_chunks": len(wild_fns),
    }
    return script, item_func, stats


def _resolve_tex_in_arc(arc, tp: str):
    if arc.has(tp):
        return tp
    alt = re.sub(r"(?i)(?:ss(?=[a-z]?\.blp$)|_shiny(?=\.blp$))", "", tp)
    if alt != tp and arc.has(alt):
        return alt
    return None


def _repack_mdx_isolated(raw: bytes, arc, src_tag: str, tex_out: dict, tex_cache: dict, compress_blp: bool, max_dim: int, quality: int) -> bytes:
    out = bytearray(raw)
    pos = 4
    n = len(out)
    while pos + 8 <= n:
        tag = bytes(out[pos:pos + 4])
        sz, = struct.unpack_from("<I", out, pos + 4)
        pos += 8
        if tag == b"TEXS":
            for k in range(sz // 268):
                at = pos + k * 268 + 4
                tp = bytes(out[at:at + 260]).split(b"\x00", 1)[0].decode("latin-1", errors="ignore").strip()
                if not tp or tp.lower().startswith(BLIZZARD_PREFIXES):
                    continue
                resolved = _resolve_tex_in_arc(arc, tp)
                if resolved is None:
                    raise RuntimeError(f"[gen14] Missing texture {tp!r} in {src_tag}")
                ckey = (src_tag, resolved.lower().replace("/", "\\"))
                if ckey not in tex_cache:
                    base_nm = os.path.basename(resolved.replace("/", "\\"))
                    clean_nm = re.sub(r"[^A-Za-z0-9_.-]+", "_", base_nm)
                    dst_tp = f"PkFx\\G14\\t\\{src_tag}_{clean_nm}"
                    suffix = 1
                    used_low = {v.lower() for v in tex_cache.values()}
                    while dst_tp.lower() in used_low:
                        stem, ext = os.path.splitext(clean_nm)
                        dst_tp = f"PkFx\\G14\\t\\{src_tag}_{stem}_{suffix}{ext}"
                        suffix += 1
                    tdata = arc.read(resolved)
                    if tdata[:4] == b"BLP1":
                        comp = struct.unpack_from("<I", tdata, 4)[0]
                        if comp == 0:
                            try:
                                rgba, ab, ex = map_optimizer.decode_blp1_jpeg(tdata)
                                # Fix corrupted zero-alpha textures from Pokemon World (e.g. 293&295, 307&308, 337&338)
                                if ab > 0 and (rgba[:, :, 3].max() == 0 or rgba[:, :, 3].mean() < 1):
                                    rgba[:, :, 3] = 255
                                    tdata = map_optimizer.encode_blp1_jpeg(rgba, abits=8, extra=ex, quality=quality, max_dim=max_dim)
                                elif compress_blp and len(tdata) >= 32_000:
                                    reenc = map_optimizer.encode_blp1_jpeg(rgba, abits=ab, extra=ex, quality=quality, max_dim=max_dim)
                                    map_optimizer.decode_blp1_jpeg(reenc)
                                    if len(reenc) < len(tdata):
                                        tdata = reenc
                            except Exception:
                                pass
                    tex_cache[ckey] = dst_tp
                    tex_out[dst_tp] = tdata
                dst_tp = tex_cache[ckey]
                enc = dst_tp.encode("latin-1")
                if len(enc) >= 260:
                    raise RuntimeError(f"[gen14] Texture path too long: {dst_tp}")
                out[at:at + 260] = enc.ljust(260, b"\x00")
            break
        pos += sz
    return bytes(out)


def build_billboard_mdx(tex_path: str, model_name: str = "PokemonBillboard", width: float = 75.0, height: float = 75.0) -> bytes:
    hw = width / 2.0
    h = height

    # 1. VERS
    vers_body = struct.pack("<I", 800)
    vers = b"VERS" + struct.pack("<I", len(vers_body)) + vers_body

    # 2. MODL
    modl_name = clean_ascii(model_name).encode("latin-1")[:80].ljust(80, b"\x00")
    anim_file = b"\x00" * 260
    r = (hw * hw + h * h) ** 0.5
    bounds = struct.pack("<7f", r, -hw, -hw, 0.0, hw, hw, h)
    blend_time = struct.pack("<I", 150)
    modl_body = modl_name + anim_file + bounds + blend_time
    modl = b"MODL" + struct.pack("<I", len(modl_body)) + modl_body

    # 3. SEQS (Stand 0..1000, Walk 1333..2333, Attack 2667..3667, Death 4000..5000)
    seqs = [
        ("Stand", 0, 1000, 0.0, 0),
        ("Walk", 1333, 2333, 250.0, 0),
        ("Attack", 2667, 3667, 0.0, 1),
        ("Death", 4000, 5000, 0.0, 1),
    ]
    seq_bytes = bytearray()
    for sname, start, end, movespeed, nonloop in seqs:
        sn = sname.encode("latin-1")[:80].ljust(80, b"\x00")
        seq_bytes += sn
        seq_bytes += struct.pack("<II", start, end)
        seq_bytes += struct.pack("<f", movespeed)
        seq_bytes += struct.pack("<I", nonloop)
        seq_bytes += struct.pack("<fI", 0.0, 0)
        seq_bytes += bounds
    seqs_chunk = b"SEQS" + struct.pack("<I", len(seq_bytes)) + bytes(seq_bytes)

    # 4. MTLS (1 material, 1 layer: Transparent filterMode=1, two-sided=0x11, unshaded=0x1)
    layer = struct.pack("<IIIIiIf", 28, 1, 0x11, 0, -1, 0, 1.0)
    lays = b"LAYS" + struct.pack("<I", 1) + layer
    mat = struct.pack("<III", 12 + len(lays), 0, 0) + lays
    mtls_chunk = b"MTLS" + struct.pack("<I", len(mat)) + mat

    # 5. TEXS (1 texture)
    tp = tex_path.encode("latin-1")[:260].ljust(260, b"\x00")
    tex_entry = struct.pack("<I", 0) + tp + struct.pack("<I", 0)
    texs_chunk = b"TEXS" + struct.pack("<I", len(tex_entry)) + tex_entry

    # 6. GEOS (1 geoset: quad in Y=0 plane)
    v_data = struct.pack("<12f", -hw, 0.0, 0.0, hw, 0.0, 0.0, hw, 0.0, h, -hw, 0.0, h)
    vrtx = b"VRTX" + struct.pack("<I", 4) + v_data

    n_data = struct.pack("<12f", 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0)
    nrms = b"NRMS" + struct.pack("<I", 4) + n_data

    ptyp = b"PTYP" + struct.pack("<I", 1) + struct.pack("<I", 4)
    pcnt = b"PCNT" + struct.pack("<I", 1) + struct.pack("<I", 6)
    pvtx = b"PVTX" + struct.pack("<I", 6) + struct.pack("<6H", 0, 1, 2, 0, 2, 3)
    gndx = b"GNDX" + struct.pack("<I", 4) + b"\x00\x00\x00\x00"

    mtgc = b"MTGC" + struct.pack("<I", 1) + struct.pack("<I", 1)
    mats = b"MATS" + struct.pack("<I", 1) + struct.pack("<I", 0)

    hdr = struct.pack("<III", 0, 0, 0) + bounds + struct.pack("<I", 0)

    uv_data = struct.pack("<8f", 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
    uvbs = b"UVBS" + struct.pack("<I", 4) + uv_data
    uvas = b"UVAS" + struct.pack("<I", 1) + uvbs

    geoset_data = vrtx + nrms + ptyp + pcnt + pvtx + gndx + mtgc + mats + hdr + uvas
    geoset_total = struct.pack("<I", 4 + len(geoset_data)) + geoset_data
    geos_chunk = b"GEOS" + struct.pack("<I", len(geoset_total)) + geoset_total

    # 7. BONE (1 bone: Root with BillboardedLockZ flag 0x48 + KGTR animation tracks)
    node_name = b"Root".ljust(80, b"\x00")
    node_base = node_name + struct.pack("<IIi", 0, 0xffffffff, 0x48)

    kgtr_keys = [
        # Stand
        (0, (0.0, 0.0, 0.0)),
        (500, (0.0, 0.0, 3.0)),
        (1000, (0.0, 0.0, 0.0)),
        # Walk
        (1333, (0.0, 0.0, 0.0)),
        (1583, (0.0, 0.0, 14.0)),
        (1833, (0.0, 0.0, 0.0)),
        (2083, (0.0, 0.0, 14.0)),
        (2333, (0.0, 0.0, 0.0)),
        # Attack
        (2667, (0.0, 0.0, 0.0)),
        (3000, (0.0, -22.0, 5.0)),
        (3667, (0.0, 0.0, 0.0)),
        # Death
        (4000, (0.0, 0.0, 0.0)),
        (5000, (0.0, 0.0, -50.0)),
    ]
    kgtr_body = struct.pack("<IIi", len(kgtr_keys), 1, 0)
    for time_ms, pos in kgtr_keys:
        kgtr_body += struct.pack("<I3f", time_ms, pos[0], pos[1], pos[2])
    kgtr = b"KGTR" + kgtr_body

    node_total_len = 4 + len(node_base) + len(kgtr)
    bone_body = struct.pack("<I", node_total_len) + node_base + kgtr + struct.pack("<ii", 0, -1)
    bone_chunk = b"BONE" + struct.pack("<I", len(bone_body)) + bone_body

    # 8. ATCH & PIVT (Standard WC3 Attachment layout: 364 bytes per entry, inclusiveSize 364, node inclusiveSize 96, flags 0x800)
    atch_entries = [
        ("origin Ref", 1, 0, (0.0, 0.0, 0.0)),
        ("overhead Ref", 2, 0, (0.0, 0.0, h + 10.0)),
        ("chest Ref", 3, 0, (0.0, 0.0, h * 0.5)),
    ]
    atch_body = bytearray()
    pivt_extra = bytearray()
    for aname, aoid, apid, apos in atch_entries:
        an = aname.encode("latin-1")[:80].ljust(80, b"\x00")
        node = struct.pack("<I", 96) + an + struct.pack("<III", aoid, apid, 0x00000800)
        att_entry = struct.pack("<I", 364) + node + (b"\x00" * 260) + struct.pack("<I", 0)
        atch_body += att_entry
        pivt_extra += struct.pack("<3f", apos[0], apos[1], apos[2])

    atch_chunk = b"ATCH" + struct.pack("<I", len(atch_body)) + bytes(atch_body)
    pivt_chunk = b"PIVT" + struct.pack("<I", 12 + len(pivt_extra)) + struct.pack("<3f", 0.0, 0.0, 0.0) + bytes(pivt_extra)

    full_mdx = b"MDLX" + vers + modl + seqs_chunk + mtls_chunk + texs_chunk + geos_chunk + bone_chunk + atch_chunk + pivt_chunk
    return full_mdx


def load_g14_assets(compress_blp: bool = True) -> dict:
    """Loads & packs all 205 Gen 1-4 MDXs + isolated compressed BLPs + BTN/DISBTN icons."""
    entries = load_species_entries()
    arcs = {
        "PW": _PWArchive(PW_MAP),
        "RPG79": mpq.MPQ(RPG79_MAP),
        "MEW": mpq.MPQ(MEW_MAP),
    }
    files = {}
    tex_cache = {}

    for sp in entries:
        d = sp["dex"]
        if sp["src"] == "LOCAL_3D":
            with open(sp["ref"], "rb") as fp:
                files[sp["dst_mdx"]] = fp.read()
            # Pack all converted textures for this dex
            d_str = str(d)
            if os.path.isdir(NEW_3D_TEX_DIR):
                for tfile in os.listdir(NEW_3D_TEX_DIR):
                    if tfile.startswith(f"{d_str}_") and tfile.endswith(".blp"):
                        with open(os.path.join(NEW_3D_TEX_DIR, tfile), "rb") as tfp:
                            files[f"PkFx\\G14\\t\\{tfile}"] = tfp.read()
        elif sp["src"] == "2.5D":
            sprite_path = os.path.join(WORK, sp["ref"]) if not os.path.isabs(sp["ref"]) else sp["ref"]
            im = Image.open(sprite_path).convert("RGBA")
            bbox = im.getbbox()
            cropped = im.crop(bbox) if bbox else im
            bw, bh = cropped.size
            aspect = bw / float(bh)
            h = float(sp.get("bh") or 75.0)
            w = h * aspect
            tex_rel = f"PkFx\\G14\\t\\25d_{d:03d}.blp"
            files[sp["dst_mdx"]] = build_billboard_mdx(tex_rel, sp["name"], width=w, height=h)

            dim = max(bw, bh)
            sq = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
            sq.paste(cropped, ((dim - bw) // 2, (dim - bh) // 2))
            tex_im = sq.resize((256, 256), Image.LANCZOS)
            tex_arr = np.array(tex_im, dtype=np.uint8)
            files[tex_rel] = map_optimizer.encode_blp1_jpeg(tex_arr, abits=8, quality=80, max_dim=256)
        else:
            arc = arcs[sp["src"]]
            ref = sp["ref"]
            raw = arc.read_block(ref) if isinstance(ref, int) else arc.read(ref)
            max_dim = 512 if sp["is_legend"] else 256
            qual = 75 if sp["is_legend"] else 72
            files[sp["dst_mdx"]] = _repack_mdx_isolated(
                raw, arc, sp["src"], files, tex_cache,
                compress_blp=compress_blp, max_dim=max_dim, quality=qual,
            )

        # Pack BTN + DISBTN icons (from PW/RPG79/MEW if available, else pre-rendered g14_icons_cache)
        btn_bytes = None
        dis_bytes = None
        if sp["btn_src"]:
            for arc_name in ("PW", sp["src"]):
                if arc_name in arcs and arcs[arc_name].has(sp["btn_src"]):
                    btn_bytes = arcs[arc_name].read(sp["btn_src"])
                    dis_src = sp["btn_src"].replace("CommandButtons\\BTN_", "CommandButtonsDisabled\\DISBTN_")
                    if arcs[arc_name].has(dis_src):
                        dis_bytes = arcs[arc_name].read(dis_src)
                    break
        if btn_bytes is None:
            cp = os.path.join(ICON_CACHE, f"BTN_{d:03d}.blp")
            if os.path.isfile(cp):
                btn_bytes = open(cp, "rb").read()
        if dis_bytes is None:
            dp = os.path.join(ICON_CACHE, f"DISBTN_{d:03d}.blp")
            if os.path.isfile(dp):
                dis_bytes = open(dp, "rb").read()
            elif btn_bytes is not None:
                dis_bytes = btn_bytes
        if btn_bytes is None:
            raise RuntimeError(f"[gen14] Missing BTN icon for dex {d} ({sp['name']})")
        files[sp["icon_path"]] = btn_bytes
        files[sp["dis_icon_path"]] = dis_bytes

    return files
