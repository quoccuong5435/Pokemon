"""Form expansion for New Pokemon Arena 1.0 (from docs/form-models/cay-pha-he.html).

Wires all 105 active non-map form models of the 104 kept evolution lines:
1. Upgrades Mega Beedrill (hM04) & Mega Kangaskhan (hM08) + Paradoxes 13..19 (Roaring Moon,
   Sandy Shocks, Flutter Mane, Scream Tail, Iron Thorns, Iron Valiant, Iron Jugulis) from
   recolored base models to real isolated 3D .mdx skins, plus new Paradoxes 20..23
   (Iron Bundle, Iron Hands, Great Tusk, Iron Treads).
2. Adds 28 new Mega Evolutions (9 Hoenn/Sinnoh + 19 Z-A) into Mega_InitData (Mega_N = 72)
   with Gold '+' Hero Unlock passives (A852..A879) + permanent Unit ANcl skills (AF00..AF27).
3. Adds 12 Gigantamax skins (hG00..hG11) hooked into Dynamax Band (Fx_DynaCast / Fx_DynaEnd).
4. Creates 52 playable Hero units (PF00..PF51) for regional forms, regional evolutions,
   special forms (Ash-Pikachu, Spiky-eared Pichu, Ash-Greninja), and form-switch species
   (Castform, Cherrim, Shellos, Gastrodon, Aegislash, 5 Rotom forms) with exact PokeAPI
   types, stats, moves copied from their base Pokemon, foot/fly umvt/umvh, and Melee/Ranged
   classification.
5. Links regional evolutions (Form_EvoData), sells IRGC (Regional Charm) & IFSW (Form & Tera Orb)
   in n00Q (Poke Super Mart 2), and adds the -form interactive branch dialog.
6. Enforces Final-Form-Only Hidden Power via Awakening Quest (-quest slot 58): regular evolved
   Pokemon receive NO Hidden Power; only the 126 final form branches unlock Hidden Power after
   completing -quest.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(WORK, "tools"), HERE]

import ability_names  # noqa: E402
import form_assets  # noqa: E402
import form_pokeapi  # noqa: E402
import gen14_expansion  # noqa: E402
import melee_ranged_classifier  # noqa: E402
import objdata  # noqa: E402

POKEDEX_JSON = os.path.join(HERE, "gen14_pokedex.json")

TYPE_IDX = gen14_expansion.TYPE_IDX
TYPE_WORD = gen14_expansion.TYPE_WORD
ATTACK_COLOR = gen14_expansion.ATTACK_COLOR
TYPE_FALLBACK_AB = gen14_expansion.TYPE_FALLBACK_AB

# Physical-leaning species / forms that should fight in melee (rest get type-matched 500-range missiles)
MELEE_KEYS = {
    "beedrill-mega", "kangaskhan-mega", "mawile-mega", "medicham-mega", "banette-mega",
    "lopunny-mega", "abomasnow-mega", "aggron-mega", "sableye-mega", "gallade-mega",
    "feraligatr-mega", "dragonite-mega", "skarmory-mega", "emboar-mega", "chesnaught-mega",
    "absol-mega-z", "staraptor-mega", "garchomp-mega-z", "lucario-mega-z", "greninja-mega",
    "venusaur-gmax", "charizard-gmax", "blastoise-gmax", "pikachu-gmax", "meowth-gmax",
    "machamp-gmax", "kingler-gmax", "eevee-gmax", "snorlax-gmax",
    "rattata-alola", "raticate-alola", "diglett-alola", "dugtrio-alola", "meowth-alola",
    "persian-alola", "grimer-alola", "muk-alola", "marowak-alola", "exeggutor-alola",
    "meowth-galar", "perrserker", "ponyta-galar", "rapidash-galar", "farfetchd-galar",
    "zigzagoon-galar", "linoone-galar", "obstagoon", "slowbro-galar",
    "growlithe-hisui", "arcanine-hisui", "sneasel-hisui", "sneasler", "kleavor", "ursaluna",
    "aegislash-blade", "greninja-ash", "pikachu-world-cap", "pichu-spiky-eared",
    "roaring-moon", "iron-thorns", "iron-valiant", "iron-hands", "great-tusk", "iron-treads",
}

FLYING_OR_LEVITATE_KEYS = {
    "beedrill-mega", "butterfree-gmax", "charizard-gmax", "dragonite-mega", "skarmory-mega",
    "chimecho-mega", "staraptor-mega", "weezing-galar", "rotom-heat", "rotom-wash",
    "rotom-frost", "rotom-fan", "rotom-mow", "flutter-mane", "iron-jugulis", "roaring-moon",
}

# Existing in-map Regional/Paldean units that can be reached by Regional Charm from base heroes
EXISTING_FORM_HEROES = {
    "raichu-alola": "P06A",
    "sandshrew-alola": "P4MA",
    "sandslash-alola": "P4NA",
    "geodude-alola": "P03A",
    "graveler-alola": "P05A",
    "golem-alola": "P04A",
    "tauros-paldea-aqua-breed": "P42A",
    "tauros-paldea-blaze-breed": "P43A",
    "tauros-paldea-combat-breed": "P44A",
}

# Paradox keys mapped to PAX_Form_Id slots 13..23 (13..19 already exist in PAX_Form_Appearance)
PARADOX_SLOTS = {
    "roaring-moon": (13, ("dragon", "dark"), (25, 20, 0), 30),
    "sandy-shocks": (14, ("electric", "ground"), (0, 15, 20), 27),
    "flutter-mane": (15, ("ghost", "fairy"), (0, 20, 30), 28),
    "scream-tail": (16, ("fairy", "psychic"), (0, 10, 15), 29),
    "iron-thorns": (17, ("rock", "electric"), (20, 0, 10), 26),
    "iron-valiant": (18, ("fairy", "fighting"), (20, 15, 20), 31),
    "iron-jugulis": (19, ("dark", "flying"), (0, 15, 25), 32),
    "iron-bundle": (20, ("ice", "water"), (0, 25, 25), 58),
    "iron-hands": (21, ("fighting", "electric"), (30, 0, 0), 58),
    "great-tusk": (22, ("ground", "fighting"), (30, 10, 0), 58),
    "iron-treads": (23, ("ground", "steel"), (20, 15, 0), 58),
}

# Base hero -> G-Max key
GMAX_BASES = [
    ("venusaur-gmax", ("E002",)),
    ("charizard-gmax", ("E00E",)),
    ("blastoise-gmax", ("E000",)),
    ("butterfree-gmax", ("E01Q",)),
    ("pikachu-gmax", ("E005",)),
    ("meowth-gmax", ("P2QA",)),
    ("machamp-gmax", ("E010",)),
    ("gengar-gmax", ("E01G",)),
    ("kingler-gmax", ("E03D",)),
    ("lapras-gmax", ("P29A",)),
    ("eevee-gmax", ("E03A", "E038")),
    ("snorlax-gmax", ("P3TA",)),
]

# Base hero stats fallback (hp100, str, agi, int, armor, spe) when dex is not in gen14_pokedex
DEFAULT_STAT_BY_STAGE = (1600, 140, 140, 140, 5, 80)


def _clean_ascii(s: str) -> str:
    return re.sub(r"[^\x20-\x7e]", "", (s or "").replace("é", "e").replace("’", "'")).strip()


def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[form_expansion] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


def _copy_slk_row(tbl, src_id: str, new_id: str, overrides: dict):
    base = tbl.find(src_id)
    if base is None:
        raise KeyError(f"[form_expansion] SLK template {src_id!r} not found")
    row = dict(base)
    row[1] = f'"{new_id}"'
    for col, val in overrides.items():
        if col in tbl.name_to_x:
            row[tbl.name_to_x[col]] = val
    tbl.rows.append(row)


def _copy_ini_section(text: str, src_id: str, new_id: str, replacements: dict) -> str:
    m = re.search(rf"(?m)^\[{re.escape(src_id)}\]\r?\n([\s\S]*?)(?=^\[|\Z)", text)
    if not m:
        raise KeyError(f"[form_expansion] INI section [{src_id}] not found")
    lines = [f"[{new_id}]"]
    seen = set()
    for raw in m.group(1).splitlines():
        if "=" not in raw:
            continue
        k, _ = raw.split("=", 1)
        if k in replacements:
            lines.append(f"{k}={replacements[k]}")
            seen.add(k)
        else:
            lines.append(raw)
    for k, v in replacements.items():
        if k not in seen:
            lines.append(f"{k}={v}")
    return text.rstrip("\r\n") + "\n\n" + "\n".join(lines) + "\n"


def _clone_unit(w3u, tmpl_id: str, new_id: str, props: dict):
    tmpl = next((u for u in w3u.all() if u.id == tmpl_id), None)
    if tmpl is None:
        raise KeyError(f"[form_expansion] Unit template {tmpl_id!r} not found")
    nu = objdata.Obj(tmpl.orig, new_id, [])
    for m in tmpl.mods:
        nu.mods.append(objdata.Mod(m.field, m.type, m.value, m.level, m.data, m.end))
    for fld, (ftype, val) in props.items():
        nu.set(fld, ftype, val)
    w3u.custom.append(nu)
    return nu


def _set_usca(u, val: float):
    ftype = next((m.type for m in u.mods if m.field == "usca"), 1)
    u.set("usca", ftype, float(val))


def _load_pokedex_by_dex():
    if not os.path.isfile(POKEDEX_JSON):
        return {}
    raw = json.load(open(POKEDEX_JSON, encoding="utf-8"))
    if isinstance(raw, list):
        return {int(e["dex"]): e for e in raw if "dex" in e}
    if isinstance(raw, dict):
        return {int(v.get("dex", k)): v for k, v in raw.items() if str(v.get("dex", k)).isdigit()}
    return {}


def patch_all(w3u, abil, strings: str, items_slk, item_func: str, script: str, meta: dict):
    """Wires all 105 active form models, objects, items, -form dialog, and -quest Hidden Power."""
    _, active_fams = form_assets.load_active_tree()
    by_id = {u.id: u for u in w3u.all()}
    dex_info = _load_pokedex_by_dex()

    # Default Ability of a form hero / new Mega = the first normal PokeAPI Ability the map has (reworked number wins, see
    # ability_names). One the map does not have yet keeps the old by-type placeholder and is listed in stats.
    ab_index = ability_names.ability_index(script)
    ability_fallback = []
    mega_key_by_index = {}  # Mega index (44..) -> form key
    pf_key_by_id = {}  # PF.. hero id -> form key

    def real_ability(key, ptypes):
        rec = form_pokeapi.pokemon(key)
        number = ability_names.first_known(ab_index, rec["abilities"]) if rec else None
        if number is None:
            ability_fallback.append(key)
            return TYPE_FALLBACK_AB.get(ptypes[0], 16)
        return number

    # Collect active F_* nodes and edges
    f_nodes = {}
    all_edges = []
    for fam in active_fams:
        nodes = fam["nodes"]
        for nid, n in nodes.items():
            if nid.startswith("F_"):
                f_nodes[n.get("key", nid[2:])] = n
        for e in fam["edges"]:
            all_edges.append((fam, nodes, e[0], e[1], e[2], e[3]))

    # 1. Upgrade Beedrill-Mega (hM04) & Kangaskhan-Mega (hM08) in w3u + Mega_Scale in JASS
    for idx, skin_id, key in ((4, "hM04", "beedrill-mega"), (8, "hM08", "kangaskhan-mega")):
        u = by_id.get(skin_id)
        if u and key in meta:
            u.set("umdl", 3, meta[key]["mdl"])
            _set_usca(u, meta[key]["usca"])
            m_sc = re.search(rf"    set Mega_Scale\[{idx}\] = [\d.]+", script)
            if m_sc:
                script = _once(
                    script, m_sc.group(0),
                    f"    set Mega_Scale[{idx}] = {meta[key]['usca']:.3f}",
                    f"Mega_Scale[{idx}] upgrade",
                )

    # 2. Classify non-map keys into: Paradox skins (11), G-Max skins (12), New Megas (28), Playable Heroes (52)
    mega_keys = []
    for _fam, _nodes, src_nid, dst_nid, lbl, _knd in all_edges:
        if lbl in ("Mega Stone", "Mega Stone (Z-A)") and dst_nid.startswith("F_"):
            dn = _nodes[dst_nid]
            key = dn.get("key", dst_nid[2:])
            if dn.get("st") != "map" and key not in ("beedrill-mega", "kangaskhan-mega"):
                mega_keys.append((src_nid, key, dn, lbl))

    # Deduplicate mega_keys by key preserving order
    seen_mk = set()
    new_megas = []
    for src_nid, key, dn, lbl in mega_keys:
        if key not in seen_mk:
            seen_mk.add(key)
            new_megas.append((src_nid, key, dn, lbl))

    gmax_keys = {k for k, _ in GMAX_BASES}
    paradox_keys = set(PARADOX_SLOTS.keys())
    mega_key_set = {k for _, k, _, _ in new_megas}

    # Playable hero form keys = remaining active non-map keys
    hero_form_keys = sorted(
        k for k in meta
        if k not in paradox_keys and k not in gmax_keys and k not in mega_key_set
        and k not in ("beedrill-mega", "kangaskhan-mega")
    )

    # 3. Allocate Hero Form Units PF00..PFxx (52 units)
    hero_key_to_id = dict(EXISTING_FORM_HEROES)
    form_jass_setup = []
    # Also remember Mega_HT / Ab_HT copy list from base unit
    copy_move_pairs = []  # (new_hid, donor_hid, key, meta_info)

    # Map F_key -> parent base Hero ID (walk backwards in edges if multi-step regional evo)
    parent_edge = {}
    for _fam, _nodes, src_nid, dst_nid, lbl, _knd in all_edges:
        if dst_nid.startswith("F_"):
            dk = _nodes[dst_nid].get("key", dst_nid[2:])
            parent_edge[dk] = (src_nid, lbl)

    def resolve_base_hero(key_or_id: str) -> str:
        cur = key_or_id
        for _ in range(5):
            if not cur.startswith("F_") and cur in by_id:
                return cur
            fk = cur[2:] if cur.startswith("F_") else cur
            if fk in EXISTING_FORM_HEROES and EXISTING_FORM_HEROES[fk] in by_id:
                return EXISTING_FORM_HEROES[fk]
            if fk in parent_edge:
                cur = parent_edge[fk][0]
            else:
                break
        return "E003"

    final_hp_hero_ids = set()
    # Mark existing final regional heroes in map as final_hp
    for k_ex, hid_ex in EXISTING_FORM_HEROES.items():
        if f_nodes.get(k_ex, {}).get("hp"):
            final_hp_hero_ids.add(hid_ex)

    for idx, key in enumerate(hero_form_keys):
        nid_str = f"PF{idx:02d}"
        assert nid_str not in by_id, f"Unit ID collision {nid_str}"
        info = meta[key]
        donor = resolve_base_hero(key)
        du = by_id.get(donor, by_id["E003"])
        pname = _clean_ascii(info["name"])
        ptypes = info["types"] or ["normal"]
        is_melee = key in MELEE_KEYS
        is_fly = key in FLYING_OR_LEVITATE_KEYS or ("flying" in ptypes)

        props = {
            "unam": (3, pname),
            "upro": (3, pname),
            "umdl": (3, info["mdl"]),
            "usca": (1, float(info["usca"])),
            "umvt": (3, "fly" if is_fly else "foot"),
            "umvh": (2, 70.0 if is_fly else 0.0),
            "uhab": (3, ""),
        }
        nu = _clone_unit(w3u, donor if donor in by_id else "E003", nid_str, props)
        melee_ranged_classifier.apply_weapon_for_unit(nu, is_melee=is_melee, primary_type=ptypes[0], is_legend=False)
        by_id[nid_str] = nu
        hero_key_to_id[key] = nid_str
        copy_move_pairs.append((nid_str, donor, key, info))
        if info["hp"]:
            final_hp_hero_ids.add(nid_str)

    # 4. Create 11 Paradox Skins (hP00..hP10)
    paradox_skin_ids = {}
    for idx, (pkey, (fid, ptypes, _stats, _leg_idx)) in enumerate(sorted(PARADOX_SLOTS.items(), key=lambda x: x[1][0])):
        sid = f"hP{idx:02d}"
        assert sid not in by_id, f"Unit ID collision {sid}"
        info = meta[pkey]
        is_fly = pkey in FLYING_OR_LEVITATE_KEYS or ("flying" in ptypes)
        su = _clone_unit(w3u, "hM00", sid, {
            "unam": (3, _clean_ascii(info["name"])),
            "umdl": (3, info["mdl"]),
            "usca": (1, float(info["usca"])),
            "umvt": (3, "fly" if is_fly else "foot"),
            "umvh": (2, 70.0 if is_fly else 0.0),
        })
        by_id[sid] = su
        paradox_skin_ids[fid] = (sid, pkey, info)

    # 5. Create 12 G-Max Skins (hG00..hG11)
    gmax_skin_map = {}  # base_hid -> (skin_id, key)
    for idx, (gkey, base_hids) in enumerate(GMAX_BASES):
        sid = f"hG{idx:02d}"
        assert sid not in by_id, f"Unit ID collision {sid}"
        info = meta[gkey]
        ptypes = info["types"] or ["normal"]
        is_fly = gkey in FLYING_OR_LEVITATE_KEYS or ("flying" in ptypes)
        su = _clone_unit(w3u, "hM00", sid, {
            "unam": (3, _clean_ascii(info["name"])),
            "umdl": (3, info["mdl"]),
            "usca": (1, float(info["usca"])),
            "umvt": (3, "fly" if is_fly else "foot"),
            "umvh": (2, 70.0 if is_fly else 0.0),
        })
        by_id[sid] = su
        for bh in base_hids:
            gmax_skin_map[bh] = (sid, gkey, info)

    # 6. Create 28 New Megas (hF00..hF27, AF00..AF27 Unit ANcl, A852..A879 Hero '+' unlock)
    new_unlock_to_cast = {}
    new_mega_jass = []
    mega_idx = 44
    for i, (base_hid, mkey, dn, lbl) in enumerate(new_megas):
        assert base_hid in by_id, f"[form_expansion] Base hero {base_hid} for {mkey} not found"
        skin_id = f"hF{i:02d}"
        cast_id = f"AF{i:02d}"
        unlock_id = f"A8{52 + i:02d}"
        info = meta[mkey]
        mname = _clean_ascii(info["name"])
        ptypes = info["types"] or ["normal"]
        is_fly = mkey in FLYING_OR_LEVITATE_KEYS or ("flying" in ptypes)
        su = _clone_unit(w3u, "hM00", skin_id, {
            "unam": (3, mname),
            "umdl": (3, info["mdl"]),
            "usca": (1, float(info["usca"])),
            "umvt": (3, "fly" if is_fly else "foot"),
            "umvh": (2, 70.0 if is_fly else 0.0),
        })
        by_id[skin_id] = su

        # Unit ANcl ability
        order_str = "battleroar" if i % 2 == 0 else "carrionswarm"
        _copy_slk_row(abil, "AM0W", cast_id, {
            "hero": "0",
            "levels": "1",
            "DataF1": f'"{order_str}"',
        })
        strings = _copy_ini_section(strings, "AM0W", cast_id, {
            "Name": mname,
            "Tip": f"|cffff66cc{mname}|r",
            "Ubertip": f'"Mega Evolve into {mname} ({lbl})."',
            "Order": order_str,
        })

        # Hero Gold '+' passive unlock
        _copy_slk_row(abil, "AEev", unlock_id, {
            "hero": "1",
            "levels": "1",
            "reqLevel": "1",
            "DataA1": "0",
            "DataB1": "0",
        })
        btn_x = "0" if not str(by_id[base_hid].get("uhab") or "").strip() else "1"
        strings = _copy_ini_section(strings, "A800", unlock_id, {
            "Name": f"{mname} (Unlock)",
            "Researchtip": f'"Unlock {mname} (5,000 Gold)"',
            "Researchubertip": f'"Click to unlock {mname} permanently on your Command Card (5,000 Gold)."',
            "Researchbuttonpos": f"{btn_x},0",
        })

        bu = by_id[base_hid]
        cur_uhab = str(bu.get("uhab") or "").strip()
        parts = [x for x in cur_uhab.split(",") if x]
        if unlock_id not in parts:
            parts.append(unlock_id)
            bu.set("uhab", 3, ",".join(parts))

        new_unlock_to_cast[unlock_id] = cast_id
        b_scale = float(bu.get("usca") or 1.0)
        t1 = TYPE_IDX.get(ptypes[0], 12) + 1
        t2 = (TYPE_IDX[ptypes[1]] + 1) if len(ptypes) > 1 and ptypes[1] in TYPE_IDX else 0
        ab_idx = real_ability(mkey, ptypes)
        mega_key_by_index[mega_idx] = mkey
        new_mega_jass.extend([
            f"    set Mega_Base[{mega_idx}] = '{base_hid}'",
            f"    set Mega_Stone[{mega_idx}] = '{cast_id}'",
            f"    set Mega_Skin[{mega_idx}] = '{skin_id}'",
            f"    set Mega_Evolve[{mega_idx}] = '{cast_id}'",
            f"    set Mega_PStr[{mega_idx}] = 25",
            f"    set Mega_PAgi[{mega_idx}] = 25",
            f"    set Mega_PInt[{mega_idx}] = 25",
            f"    set Mega_Price[{mega_idx}] = 5000",
            f'    set Mega_Name[{mega_idx}] = "{mname}"',
            f'    set Mega_StoneName[{mega_idx}] = "{mname}"',
            f'    set Mega_Fx[{mega_idx}] = ""',
            f"    set Mega_Scale[{mega_idx}] = {info['usca']:.3f}",
            f"    set Mega_BaseScale[{mega_idx}] = {b_scale:.3f}",
            f"    set Mega_R[{mega_idx}] = 255",
            f"    set Mega_G[{mega_idx}] = 255",
            f"    set Mega_B[{mega_idx}] = 255",
            f"    call SaveInteger(Ab_HT, '{skin_id}', 53, {t1})",
            f"    set Ab_MegaAb[{mega_idx}] = {ab_idx}",
        ])
        if t2:
            new_mega_jass.append(f"    call SaveInteger(Ab_HT, '{skin_id}', 54, {t2})")
        mega_idx += 1

    # 7. Create Shop Items: IRGC (Regional Charm) & IFSW (Form & Tera Orb) + Hidden Power passive AFHP/AFHL
    _copy_slk_row(abil, "AM0W", "AIRG", {"hero": "0", "levels": "1", "Cool1": "5", "DataF1": '"charm"'})
    strings = _copy_ini_section(strings, "AM0W", "AIRG", {
        "Name": "Regional Charm",
        "Tip": "Use |cff4fd1c5Regional Charm|r",
        "Ubertip": '"Transform or branch into an Alolan, Galarian, Hisuian, or Paldean form."',
        "Order": "charm",
        "Art": "ReplaceableTextures\\CommandButtons\\BTNPendantOfEnergy.blp",
    })
    _copy_slk_row(items_slk, "IM0W", "IRGC", {"abilList": '"AIRG"', "goldcost": "3000"})
    item_func = _copy_ini_section(item_func, "IM0W", "IRGC", {
        "Name": "Regional Charm",
        "Tip": "Purchase |cff4fd1c5Regional Charm|r",
        "Ubertip": '"|cffffcc00Use (click in inventory):|r Open regional branch choices for your Pokemon."',
        "Description": "Unlocks Alolan, Galarian, Hisuian & Paldean branches.",
        "Art": "ReplaceableTextures\\CommandButtons\\BTNPendantOfEnergy.blp",
    })

    _copy_slk_row(abil, "AM0W", "AIFS", {"hero": "0", "levels": "1", "Cool1": "5", "DataF1": '"faeriefire"'})
    strings = _copy_ini_section(strings, "AM0W", "AIFS", {
        "Name": "Form & Tera Orb",
        "Tip": "Use |cfffacc15Form & Tera Orb|r",
        "Ubertip": '"Switch battle/weather forms (Rotom, Castform, Aegislash, Cherrim, Shellos, Ash-Greninja)."',
        "Order": "faeriefire",
        "Art": "ReplaceableTextures\\CommandButtons\\BTNOrbOfFrost.blp",
    })
    _copy_slk_row(items_slk, "IM0W", "IFSW", {"abilList": '"AIFS"', "goldcost": "3500"})
    item_func = _copy_ini_section(item_func, "IM0W", "IFSW", {
        "Name": "Form & Tera Orb",
        "Tip": "Purchase |cfffacc15Form & Tera Orb|r",
        "Ubertip": '"|cffffcc00Use (click in inventory):|r Switch battle/weather/Tera forms (also usable via -form)."',
        "Description": "Switches battle/weather/Tera forms on eligible Pokemon.",
        "Art": "ReplaceableTextures\\CommandButtons\\BTNOrbOfFrost.blp",
    })

    # Add IRGC, IFSW to n00Q (Poke Super Mart 2: currently 9/12 items -> 11/12)
    shop = by_id.get("n00Q")
    if shop:
        cur_i = str(shop.get("usei") or "")
        iparts = [x for x in cur_i.split(",") if x]
        for new_it in ("IRGC", "IFSW"):
            if new_it not in iparts:
                iparts.append(new_it)
        shop.set("usei", 3, ",".join(iparts))

    # Hidden Power passive icons: AFHP (Awakened) & AFHL (Locked)
    _copy_slk_row(abil, "AXP6", "AFHP", {"hero": "0", "levels": "1"})
    strings = _copy_ini_section(strings, "AXP6", "AFHP", {
        "Name": "Hidden Power: Awakened",
        "Tip": "|cffc084fcHidden Power: Awakened|r",
        "Ubertip": '"Final Form awakened via -quest! Grants +30% All Stats while in a final form branch."',
    })
    _copy_slk_row(abil, "AXP6", "AFHL", {"hero": "0", "levels": "1"})
    strings = _copy_ini_section(strings, "AXP6", "AFHL", {
        "Name": "Hidden Power: Locked",
        "Tip": "|cff94a3b8Hidden Power: Locked (Final Form)|r",
        "Ubertip": '"Final Form branch eligible for Hidden Power. Complete Awakening Quest (-quest) to unlock +30% All Stats!"',
    })

    # 8. Build JASS updates:
    # 8a. New Mega Unlock mappings inside PAX_UnlockToCastAb & PAX_HeroMega_KeepAlive
    map_ins = "\n".join(f"    elseif unlockAbId == '{u}' then\n        return '{c}'" for u, c in new_unlock_to_cast.items())
    script = _once(
        script,
        "    endif\n    return 0\nendfunction\n\nfunction PAX_HeroMega_KeepAlive",
        map_ins + "\n    endif\n    return 0\nendfunction\n\nfunction PAX_HeroMega_KeepAlive",
        "Extend PAX_UnlockToCastAb with new Megas",
    )
    keep_ins = "\n".join(
        f"    if LoadInteger(PAX_Leg_HT, heroHandleId, '{c}' + 262144) == 1 and GetUnitAbilityLevel(heroUnit, '{c}') == 0 then\n"
        f"        call UnitAddAbility(heroUnit, '{c}')\n        call UnitMakeAbilityPermanent(heroUnit, true, '{c}')\n    endif"
        for c in new_unlock_to_cast.values()
    )
    script = _once(
        script,
        "endfunction\n\n\nfunction PAX_ReviveWatchdog_Step",
        keep_ins + "\nendfunction\n\n\nfunction PAX_ReviveWatchdog_Step",
        "Extend PAX_HeroMega_KeepAlive with new Megas",
    )

    # 8b. Update Mega_N & append Mega[44..71]
    script = _once(
        script,
        "    set Mega_N = 44",
        f"    set Mega_N = {mega_idx}",
        "Update Mega_N",
    )
    script = _once(
        script,
        "    set Ab_MegaAb[35] = 81\nendfunction",
        "    set Ab_MegaAb[35] = 81\nendfunction\n\nfunction Form_MegaData takes nothing returns nothing\n"
        + "\n".join(new_mega_jass) + "\nendfunction",
        "Append new Megas via Form_MegaData",
    )
    script = _once(
        script,
        "    call Mega_InitData()",
        "    call Mega_InitData()\n    call ExecuteFunc(\"Form_MegaData\")",
        "Call Form_MegaData after Mega_InitData",
    )

    # 8c. Update PAX_Form_Appearance 13..19 from color tint to real skins + add 20..23
    for fid in range(13, 20):
        sid, pkey, pinfo = paradox_skin_ids[fid]
        pname = _clean_ascii(pinfo["name"]).split(" (")[0]
        if fid < 17:
            old_blk = f'    elseif formId == {fid} then\n        set name = "{pname}"\n        set green = 195\n        set blue = 145'
        else:
            old_blk = f'    elseif formId == {fid} then\n        set name = "{pname}"\n        set red = 175\n        set green = 205'
        new_blk = f'    elseif formId == {fid} then\n        set name = "{pname}"\n        call BlzSetUnitSkin(u, \'{sid}\')'
        script = _once(script, old_blk, new_blk, f"Paradox real model formId {fid}")

    extra_paradox_app = []
    extra_paradox_type = []
    extra_paradox_stats = []
    for fid in range(20, 24):
        sid, pkey, pinfo = paradox_skin_ids[fid]
        _, ptypes, (ps, pa, pi_), _ = PARADOX_SLOTS[pkey]
        pname = _clean_ascii(pinfo["name"]).split(" (")[0]
        extra_paradox_app.append(f'    elseif formId == {fid} then\n        set name = "{pname}"\n        call BlzSetUnitSkin(u, \'{sid}\')')
        t0 = "T_" + ptypes[0].upper()
        t1 = ("T_" + ptypes[1].upper()) if len(ptypes) > 1 else "-1"
        extra_paradox_type.append(f"    elseif formId == {fid} then\n        if k == 0 then\n            return {t0}\n        endif\n        return {t1}")
        extra_paradox_stats.append(
            f"    elseif formId == {fid} then\n"
            f"        set strPct = strPct + {ps * 0.01:.2f}\n"
            f"        set agiPct = agiPct + {pa * 0.01:.2f}\n"
            f"        set intPct = intPct + {pi_ * 0.01:.2f}"
        )

    script = _once(
        script,
        '    endif\n    call BlzSetHeroProperName(u, name)\n    call SetUnitVertexColor(u, red, green, blue, 255)',
        '\n'.join(extra_paradox_app) + '\n    endif\n    call BlzSetHeroProperName(u, name)\n    call SetUnitVertexColor(u, red, green, blue, 255)',
        "Extend PAX_Form_Appearance 20..23",
    )
    script = _once(
        script,
        "    elseif formId == 19 then\n        if k == 0 then\n            return T_DARK\n        endif\n        return T_FLYING\n    endif",
        "    elseif formId == 19 then\n        if k == 0 then\n            return T_DARK\n        endif\n        return T_FLYING\n"
        + "\n".join(extra_paradox_type) + "\n    endif",
        "Extend PAX_Form_Type 20..23",
    )
    script = _once(
        script,
        "    elseif formId == 19 then\n        set agiPct = agiPct + 0.15\n        set intPct = intPct + 0.25\n    endif",
        "    elseif formId == 19 then\n        set agiPct = agiPct + 0.15\n        set intPct = intPct + 0.25\n"
        + "\n".join(extra_paradox_stats) + "\n    endif",
        "Extend PAX_Form_SyncStats 20..23",
    )

    # 8c. The 4 new Paradox (form ids 20..23) had no Ability: Ab_Want stopped at form id 19.
    #     Great Tusk (22) Protosynthesis; Iron Bundle (20), Iron Hands (21), Iron Treads (23) Quark Drive.
    script = _once(
        script,
        "    elseif formId >= 17 and formId <= 19 then\n        return AB_QUARKDRIVE\n    endif",
        "    elseif formId >= 17 and formId <= 19 then\n        return AB_QUARKDRIVE\n"
        "    elseif formId == 22 then\n        return AB_PROTOSYNTHESIS\n"
        "    elseif formId >= 20 and formId <= 23 then\n        return AB_QUARKDRIVE\n    endif",
        "Ab_Want: Abilities of the new Paradox (form ids 20..23)",
    )

    # 8d. Emit Form_Data*, Form_EvoData, Gmax_SkinId, Form_IsFinalHP, Form_Dialog (-form / IRGC / IFSW)
    data_lines = []
    # Base stats, types, moves copy for PF00..PF51
    for hid, donor, key, info in copy_move_pairs:
        ptypes = info["types"] or ["normal"]
        t1 = TYPE_IDX.get(ptypes[0], 12) + 1
        t2 = (TYPE_IDX[ptypes[1]] + 1) if len(ptypes) > 1 and ptypes[1] in TYPE_IDX else 0
        ab_id = real_ability(key, ptypes)
        pf_key_by_id[hid] = key
        hp100, b_str, b_agi, b_int, b_arm, b_spe = DEFAULT_STAT_BY_STAGE
        di = dex_info.get(info["dex"])
        if di and "stats" in di:
            st = di["stats"]
            if isinstance(st, list) and len(st) >= 6:
                s_hp, s_atk, s_def, s_spa, _s_spd, s_spe = st[:6]
            else:
                s_hp = st.get("hp", 70)
                s_atk = st.get("atk", 75)
                s_def = st.get("def", 65)
                s_spa = st.get("spa", 75)
                s_spe = st.get("spe", 75)
            hp100 = max(1200, int(s_hp) * 22)
            b_str = max(80, int(s_atk) * 2)
            b_agi = max(80, int(s_spe) * 2)
            b_int = max(80, int(s_spa) * 2)
            b_arm = max(2, int(s_def) // 12)
            b_spe = int(s_spe)
        data_lines.extend([
            f"    call SaveInteger(Mega_HT, '{hid}', 80, {hp100})",
            f"    call SaveInteger(Mega_HT, '{hid}', 81, {b_arm})",
            f"    call SaveInteger(Mega_HT, '{hid}', 82, {b_str})",
            f"    call SaveInteger(Mega_HT, '{hid}', 83, {b_spe})",
            f"    call SaveInteger(Mega_HT, '{hid}', 84, {b_agi})",
            f"    call SaveInteger(Mega_HT, '{hid}', 85, {b_int})",
            f"    call SaveInteger(Ab_HT, '{hid}', 0, {ab_id})",
            f"    call SaveInteger(Ab_HT, '{hid}', 53, {t1})",
            f"    call Form_CopyMoves('{donor}', '{hid}')",
        ])
        if t2:
            data_lines.append(f"    call SaveInteger(Ab_HT, '{hid}', 54, {t2})")

    # Mark final-form heroes for Hidden Power
    for fhid in sorted(final_hp_hero_ids):
        data_lines.append(f"    call SaveBoolean(Mega_HT, '{fhid}', 998, true)")

    # Build branch dictionary: src_hero_id -> list of (mode, label, target_hid_or_formId)
    # mode 0 = Mega_SafeReplace to unit ID; mode 1 = PAX_Form_Apply(formId)
    branches = {}
    for _fam, _nodes, src_nid, dst_nid, lbl, _knd in all_edges:
        if lbl in ("Regional Charm", "Regional Charm (Hisui)", "Booster Energy", "Đổi dạng", "Tera Orb", "Đặc biệt") and dst_nid.startswith("F_"):
            dk = _nodes[dst_nid].get("key", dst_nid[2:])
            src_hid = hero_key_to_id.get(src_nid[2:], src_nid) if src_nid.startswith("F_") else src_nid
            if dk in PARADOX_SLOTS:
                fid = PARADOX_SLOTS[dk][0]
                branches.setdefault(src_hid, []).append((1, _clean_ascii(_nodes[dst_nid]["n"]).split(" (")[0], str(fid)))
            elif dk in hero_key_to_id:
                thid = hero_key_to_id[dk]
                branches.setdefault(src_hid, []).append((0, _clean_ascii(_nodes[dst_nid]["n"]), thid))
                # Also allow switching back from Đổi dạng forms to base!
                if lbl in ("Đổi dạng", "Tera Orb"):
                    branches.setdefault(thid, []).append((0, _clean_ascii(_nodes[src_nid]["n"]) + " (Base)", src_hid))

    # Regional level/stone evolutions -> Form_EvoData
    evo_lines = []
    for _fam, _nodes, src_nid, dst_nid, lbl, _knd in all_edges:
        if src_nid.startswith("F_") and dst_nid.startswith("F_"):
            sk = _nodes[src_nid].get("key", src_nid[2:])
            dk = _nodes[dst_nid].get("key", dst_nid[2:])
            if sk in hero_key_to_id and dk in hero_key_to_id and (sk, dk) not in (
                ("sandshrew-alola", "sandslash-alola"),
                ("geodude-alola", "graveler-alola"),
                ("graveler-alola", "golem-alola"),
            ):
                lv = 32
                m_lv = re.search(r"Lv (\d+)", lbl)
                if m_lv:
                    lv = int(m_lv.group(1))
                elif "Stone" in lbl or "Claw" in lbl:
                    lv = 28
                shid, dhid = hero_key_to_id[sk], hero_key_to_id[dk]
                evo_lines.extend([
                    f"    set Evo_From[Evo_N] = '{shid}'",
                    f"    set Evo_To[Evo_N] = '{dhid}'",
                    f"    set Evo_Level[Evo_N] = {lv}",
                    "    set Evo_N = Evo_N + 1",
                    f"    call SaveInteger(Ab_HT, '{shid}', 699, 1)",
                    f"    call SaveInteger(Ab_HT, '{shid}', 700, '{dhid}')",
                    f"    call SaveInteger(Ab_HT, '{shid}', 701, {lv})",
                ])

    # Chunk data_lines safely
    chunks = [data_lines[i:i + 250] for i in range(0, len(data_lines), 250)]
    fx_blocks = []
    late_blocks = []
    jass_calls = []

    fx_blocks.append("""
function Form_CopyMoves takes integer srcId, integer dstId returns nothing
    local integer i = 0
    local integer cnt = LoadInteger(Fx_HT, srcId, 99)
    local integer mv = 0
    local integer lv = 0
    loop
        exitwhen i >= cnt or i >= 16
        set mv = LoadInteger(Fx_HT, srcId, 100 + i)
        set lv = LoadInteger(Fx_HT, srcId, 120 + i)
        call Fx_AddLv(dstId, mv, lv)
        set i = i + 1
    endloop
endfunction
""")

    for ci, ch in enumerate(chunks):
        fn = f"Form_InitData{ci}"
        jass_calls.append(f'    call ExecuteFunc("{fn}")')
        fx_blocks.append(f"function {fn} takes nothing returns nothing\n" + "\n".join(ch) + "\nendfunction\n")

    fx_blocks.append("function Form_EvoData takes nothing returns nothing\n" + "\n".join(evo_lines) + "\nendfunction\n")
    jass_calls.append('    call ExecuteFunc("Form_EvoData")')

    # Gmax_SkinId & Form_IsFinalHP / Form_QuestIdx (placed right before PAX_Leg_Awakened; 0 forward calls)
    gmax_if = []
    for bh, (gsid, _gk, _gi) in sorted(gmax_skin_map.items()):
        kw = "if" if not gmax_if else "elseif"
        gmax_if.append(f"    {kw} ut == '{bh}' then\n        return '{gsid}'")
    gmax_jass = "function Gmax_SkinId takes integer ut returns integer\n" + "\n".join(gmax_if) + "\n    endif\n    return 0\nendfunction\n"

    form_hp_jass = """
function Form_IsFinalHP takes unit u returns boolean
    local integer h = 0
    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) then
        return false
    endif
    set h = GetHandleId(u)
    if LoadInteger(Mega_HT, h, 0) > 0 then
        return true
    endif
    if LoadInteger(PAX_Leg_HT, h, 140) >= 1 then
        return true
    endif
    if HaveSavedReal(Fx_HT, h, 87) and Mega_Time < LoadReal(Fx_HT, h, 87) and Gmax_SkinId(GetUnitTypeId(u)) != 0 then
        return true
    endif
    return LoadBoolean(Mega_HT, GetUnitTypeId(u), 998)
endfunction

function Form_QuestIdx takes unit u returns integer
    local integer idx = 0
    if u == null then
        return 0
    endif
    set idx = PAX_Leg_Index(GetUnitTypeId(u))
    if not Form_IsFinalHP(u) then
        return 0
    endif
    if idx > 0 then
        return idx
    endif
    return 58
endfunction
"""
    early_blocks = [gmax_jass, form_hp_jass]

    # Form Branch Dialog (-form, IRGC, IFSW)
    branch_cases = []
    for src_hid, opts in sorted(branches.items()):
        kw = "if" if not branch_cases else "elseif"
        branch_cases.append(f"    {kw} ut == '{src_hid}' then")
        for bi, (mode, blbl, targ) in enumerate(opts[:10]):
            t_lit = f"'{targ}'" if mode == 0 else targ
            branch_cases.append(f"        set Form_DlgMode[pid * 12 + {bi}] = {mode}")
            branch_cases.append(f"        set Form_DlgVal[pid * 12 + {bi}] = {t_lit}")
            branch_cases.append(f'        set Form_DlgBtn[pid * 12 + {bi}] = DialogAddButton(d, "{blbl}", 0)')
            branch_cases.append(f"        set cnt = {bi + 1}")
    branch_body = ("\n".join(branch_cases) + "\n    endif") if branch_cases else ""

    form_ui_jass = f"""
function Form_ShowDialog takes player p, unit u returns nothing
    local integer pid = GetPlayerId(p)
    local integer ut = GetUnitTypeId(u)
    local dialog d = null
    local integer cnt = 0
    local integer i = 0
    if pid < 0 or pid >= 12 or u == null then
        return
    endif
    if Form_Dlg[pid] == null then
        set Form_Dlg[pid] = DialogCreate()
        call TriggerRegisterDialogEvent(Form_DlgTrig, Form_Dlg[pid])
    endif
    set d = Form_Dlg[pid]
    call DialogClear(d)
    call DialogSetMessage(d, "Choose Form Branch")
    set Form_Hero[pid] = u
    loop
        exitwhen i >= 12
        set Form_DlgBtn[pid * 12 + i] = null
        set Form_DlgVal[pid * 12 + i] = 0
        set Form_DlgMode[pid * 12 + i] = -1
        set i = i + 1
    endloop
{branch_body}
    if cnt == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[FORM]|r This Pokemon has no Regional/Form-switch branch.")
        set d = null
        return
    endif
    set Form_DlgBtn[pid * 12 + cnt] = DialogAddButton(d, "Cancel", 0)
    set Form_DlgMode[pid * 12 + cnt] = -1
    call DialogDisplay(p, d, true)
    set d = null
endfunction

function Form_OnDlgClick takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local button bt = GetClickedButton()
    local unit u = Form_Hero[pid]
    local unit nu = null
    local integer i = 0
    local integer val = 0
    local integer mode = -1
    if pid < 0 or pid >= 12 then
        set p = null
        set bt = null
        set u = null
        return
    endif
    call DialogDisplay(p, Form_Dlg[pid], false)
    loop
        exitwhen i >= 12 or Form_DlgBtn[pid * 12 + i] == bt
        set i = i + 1
    endloop
    if i < 12 and u != null and GetWidgetLife(u) > 0.405 then
        set mode = Form_DlgMode[pid * 12 + i]
        set val = Form_DlgVal[pid * 12 + i]
        if mode == 0 and val != 0 then
            call RemoveSavedReal(Mega_HT, GetHandleId(u), 9)
            set Mega_EvoItem = true
            call Mega_SafeReplace(u, val, bj_UNIT_STATE_METHOD_RELATIVE)
            set Mega_EvoItem = false
            set nu = bj_lastReplacedUnit
            if nu != null then
                call Ab_Sync(nu)
                call Hero_HPSync(nu)
                call PAX_Leg_Sync(nu)
                call SelectUnitForPlayerSingle(nu, p)
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectTarget.mdl", nu, "origin"))
            endif
        elseif mode == 1 and val > 0 then
            call PAX_Form_Apply(u, val)
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectTarget.mdl", u, "origin"))
        endif
    endif
    set p = null
    set bt = null
    set u = null
    set nu = null
endfunction
"""
    late_blocks.append(form_ui_jass)

    # 8e. Build -show (newly added GLB models only: Gen 3+ G14 + 92 GLB Forms; hides old v4.2/Gen1-2/PW/PKL) and -showall (all 354)
    import gen14_expansion as _g14_exp
    _g14_local_dex = {int(e["dex"]) for e in _g14_exp.load_species_entries() if e.get("src") == "LOCAL_3D"}
    _pw_pkl_keys = set(form_assets.PW_FORMS) | set(form_assets.PKL_FORMS)

    show_items = []       # (unit_or_skin_id, label) -> newly added / converted GLB models only
    show_gen12_items = [] # (unit_or_skin_id, label) -> older v4.2 / Gen 1-2 / PW / PKL models
    seen_show = set()
    kept_base_ids = set()
    for fam in active_fams:
        for nid, n in fam["nodes"].items():
            if not nid.startswith("F_") and nid in by_id and nid not in seen_show:
                seen_show.add(nid)
                kept_base_ids.add(nid)
                dex_num = int(n.get("d", 0) or 0)
                entry = (nid, _clean_ascii(n["n"]))
                if dex_num > 251 and dex_num in _g14_local_dex:
                    show_items.append(entry)
                else:
                    show_gen12_items.append(entry)
    # In-map Megas (Mega[0..43] base filter: only if base is in kept families)
    for idx in range(44):
        mb = re.search(rf"set Mega_Base\[{idx}\] = '(\w{{4}})'", script)
        ms = re.search(rf"set Mega_Skin\[{idx}\] = '(\w{{4}})'", script)
        mn = re.search(rf'set Mega_Name\[{idx}\] = "([^"]+)"', script)
        if mb and ms and mb.group(1) in kept_base_ids:
            sid = ms.group(1)
            if sid not in seen_show and sid in by_id:
                seen_show.add(sid)
                entry = (sid, _clean_ascii(mn.group(1) if mn else sid))
                # Only upgraded GLB Megas (hM04 Mega Beedrill, hM08 Mega Kangaskhan) go in -show
                if sid in ("hM04", "hM08"):
                    show_items.append(entry)
                else:
                    show_gen12_items.append(entry)
    # New playable Form heroes (PF00..), Megas (hF00..), G-Max (hG00..), Paradox (hP00..)
    for hid, _donor, key, info in copy_move_pairs:
        if hid not in seen_show:
            seen_show.add(hid)
            entry = (hid, _clean_ascii(info["name"]))
            if key in _pw_pkl_keys:
                show_gen12_items.append(entry)
            else:
                show_items.append(entry)
    for i, (_bh, mkey, _dn, _lbl) in enumerate(new_megas):
        sid = f"hF{i:02d}"
        if sid not in seen_show:
            seen_show.add(sid)
            show_items.append((sid, _clean_ascii(meta[mkey]["name"])))
    for i, (gkey, _bhs) in enumerate(GMAX_BASES):
        sid = f"hG{i:02d}"
        if sid not in seen_show:
            seen_show.add(sid)
            show_items.append((sid, _clean_ascii(meta[gkey]["name"])))
    for fid in sorted(paradox_skin_ids):
        sid, _pk, pinfo = paradox_skin_ids[fid]
        if sid not in seen_show:
            seen_show.add(sid)
            show_items.append((sid, _clean_ascii(pinfo["name"]).split(" (")[0]))

    show_jass = ["""
function Form_ShowClearTags takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= Form_Show_TagCount
        if Form_Show_Tags[i] != null then
            call DestroyTextTag(Form_Show_Tags[i])
            set Form_Show_Tags[i] = null
        endif
        set i = i + 1
    endloop
    set Form_Show_TagCount = 0
endfunction

function Form_ShowClearCreeps takes nothing returns nothing
    local group g = CreateGroup()
    local unit u = null
    local integer c = 0
    if Form_Show_Group != null then
        loop
            set u = FirstOfGroup(Form_Show_Group)
            exitwhen u == null
            call GroupRemoveUnit(Form_Show_Group, u)
            call RemoveUnit(u)
        endloop
    endif
    call Form_ShowClearTags()
    call GroupEnumUnitsOfPlayer(g, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if not IsUnitType(u, UNIT_TYPE_STRUCTURE) then
            call RemoveUnit(u)
        endif
    endloop
    call GroupEnumUnitsOfPlayer(g, Player(bj_PLAYER_NEUTRAL_VICTIM), null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if not IsUnitType(u, UNIT_TYPE_STRUCTURE) then
            call RemoveUnit(u)
        endif
    endloop
    set c = 0
    loop
        exitwhen c >= Wild_CampN
        set Wild_CampAlive[c] = 0
        set Wild_CampDue[c] = 999999.0
        set c = c + 1
    endloop
    set Leg_Next = 999999.0
    call PauseTimer(PAX_Arena_Schedule)
    if Form_Show_WalkTimer != null then
        call PauseTimer(Form_Show_WalkTimer)
    endif
    call DestroyGroup(g)
    set g = null
    set u = null
endfunction

function Form_ShowNextPos takes nothing returns nothing
    set Form_Show_Col = Form_Show_Col + 1
    if Form_Show_Col >= 12 then
        set Form_Show_Col = 0
        set Form_Show_Row = Form_Show_Row + 1
    endif
endfunction

function Form_ShowOne takes integer ut, string lbl returns nothing
    local real curX = -1430.0 + Form_Show_Col * 260.0
    local real curY = 2200.0 - Form_Show_Row * 195.0
    local unit u = null
    local texttag tt = null
    loop
        exitwhen not (curX > -580.0 and curX < 580.0 and curY > -480.0 and curY < 480.0)
        call Form_ShowNextPos()
        set curX = -1430.0 + Form_Show_Col * 260.0
        set curY = 2200.0 - Form_Show_Row * 195.0
    endloop
    set u = CreateUnit(Player(bj_PLAYER_NEUTRAL_VICTIM), ut, curX, curY, 270.0)
    if u != null then
        call PauseUnit(u, true)
        call SetUnitInvulnerable(u, true)
        call SaveInteger(Ab_HT, GetHandleId(u), 10, 1)
        call SaveInteger(Ab_HT, GetHandleId(u), 124, 1)
        if HaveSavedHandle(Ab_HT, GetHandleId(u), 80) then
            call DestroyEffect(LoadEffectHandle(Ab_HT, GetHandleId(u), 80))
            call RemoveSavedHandle(Ab_HT, GetHandleId(u), 80)
        endif
        set tt = CreateTextTag()
        if tt != null then
            call SetTextTagText(tt, "|cffffcc00" + lbl + "|r", 0.019)
            call SetTextTagPos(tt, curX, curY, 45.0)
            call SetTextTagColor(tt, 255, 220, 80, 255)
            call SetTextTagPermanent(tt, true)
            call SetTextTagVisibility(tt, true)
            set Form_Show_Tags[Form_Show_TagCount] = tt
            set Form_Show_TagCount = Form_Show_TagCount + 1
        endif
        call GroupAddUnit(Form_Show_Group, u)
        set Form_Show_Total = Form_Show_Total + 1
    endif
    call Form_ShowNextPos()
    set u = null
    set tt = null
endfunction
"""]
    # Also build Form_ShowFormsOnly batches (the 105 new/upgraded form models)
    form_only_items = []
    seen_fo = set()
    for fid in ("hM04", "hM08"):
        if fid in by_id:
            seen_fo.add(fid)
            form_only_items.append((fid, "Mega Beedrill" if fid == "hM04" else "Mega Kangaskhan"))
    for uid, lbl in show_items + show_gen12_items:
        if uid.startswith(("PF", "hF", "hG", "hP")) and uid not in seen_fo:
            seen_fo.add(uid)
            form_only_items.append((uid, lbl))

    show_chunks = [show_items[i:i + 45] for i in range(0, len(show_items), 45)]
    batch_calls = []
    for sci, schunk in enumerate(show_chunks):
        sfn = f"Form_ShowBatch{sci}"
        batch_calls.append(f'    call ExecuteFunc("{sfn}")')
        lines = [f"function {sfn} takes nothing returns nothing"]
        for uid, lbl in schunk:
            safe_lbl = lbl.replace('"', "").replace("\\", "")
            lines.append(f'    call Form_ShowOne(\'{uid}\', "{safe_lbl}")')
        lines.append("endfunction\n")
        show_jass.append("\n".join(lines))

    gen12_chunks = [show_gen12_items[i:i + 45] for i in range(0, len(show_gen12_items), 45)]
    gen12_batch_calls = []
    for sci, schunk in enumerate(gen12_chunks):
        sfn = f"Form_ShowGen12Batch{sci}"
        gen12_batch_calls.append(f'    call ExecuteFunc("{sfn}")')
        lines = [f"function {sfn} takes nothing returns nothing"]
        for uid, lbl in schunk:
            safe_lbl = lbl.replace('"', "").replace("\\", "")
            lines.append(f'    call Form_ShowOne(\'{uid}\', "{safe_lbl}")')
        lines.append("endfunction\n")
        show_jass.append("\n".join(lines))

    form_chunks = [form_only_items[i:i + 45] for i in range(0, len(form_only_items), 45)]
    form_batch_calls = []
    for sci, schunk in enumerate(form_chunks):
        sfn = f"Form_ShowOnlyBatch{sci}"
        form_batch_calls.append(f'    call ExecuteFunc("{sfn}")')
        lines = [f"function {sfn} takes nothing returns nothing"]
        for uid, lbl in schunk:
            safe_lbl = lbl.replace('"', "").replace("\\", "")
            lines.append(f'    call Form_ShowOne(\'{uid}\', "{safe_lbl}")')
        lines.append("endfunction\n")
        show_jass.append("\n".join(lines))

    show_jass.append(f"""function Form_Show takes player pTrig returns nothing
    local unit hero = League_Hero(GetPlayerId(pTrig))
    call Form_ShowClearCreeps()
    call FogEnable(false)
    call FogMaskEnable(false)
    if Form_Show_Group == null then
        set Form_Show_Group = CreateGroup()
    endif
    set Form_Show_Col = 0
    set Form_Show_Row = 0
    set Form_Show_Total = 0
{chr(10).join(batch_calls)}
    if hero != null and Ab_Alive(hero) then
        call SetUnitPosition(hero, -128.0, 2480.0)
    endif
    call PanCameraToTimedForPlayer(pTrig, -128.0, 1950.0, 0.4)
    set hero = null
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 10.0, "|cff00ffff[SHOW] Spawned " + I2S(Form_Show_Total) + " models (Gen 1-2 hidden; 12/row, fog off). Use -showwalk to test walk, -showall for Gen 1-4, -showforms for 105 forms only.|r")
endfunction

function Form_ShowAll takes player pTrig returns nothing
    local unit hero = League_Hero(GetPlayerId(pTrig))
    call Form_ShowClearCreeps()
    call FogEnable(false)
    call FogMaskEnable(false)
    if Form_Show_Group == null then
        set Form_Show_Group = CreateGroup()
    endif
    set Form_Show_Col = 0
    set Form_Show_Row = 0
    set Form_Show_Total = 0
{chr(10).join(batch_calls)}
{chr(10).join(gen12_batch_calls)}
    if hero != null and Ab_Alive(hero) then
        call SetUnitPosition(hero, -128.0, 2480.0)
    endif
    call PanCameraToTimedForPlayer(pTrig, -128.0, 1950.0, 0.4)
    set hero = null
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 10.0, "|cff00ffff[SHOWALL] Spawned " + I2S(Form_Show_Total) + " models including Gen 1-2 (12/row, fog off, spawners paused).|r")
endfunction

function Form_ShowFormsOnly takes player pTrig returns nothing
    local unit hero = League_Hero(GetPlayerId(pTrig))
    call Form_ShowClearCreeps()
    call FogEnable(false)
    call FogMaskEnable(false)
    if Form_Show_Group == null then
        set Form_Show_Group = CreateGroup()
    endif
    set Form_Show_Col = 0
    set Form_Show_Row = 0
    set Form_Show_Total = 0
{chr(10).join(form_batch_calls)}
    if hero != null and Ab_Alive(hero) then
        call SetUnitPosition(hero, -128.0, 2480.0)
    endif
    call PanCameraToTimedForPlayer(pTrig, -128.0, 1700.0, 0.4)
    set hero = null
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 10.0, "|cff00ffff[SHOWFORMS] Spawned " + I2S(Form_Show_Total) + " form models (12/row, fog off, spawners paused). Type -clear or -respawn to resume.|r")
endfunction

function Form_ShowPickTarget takes unit u returns nothing
    local real tx = GetRandomReal(-5600.0, 5600.0)
    local real ty = GetRandomReal(-5200.0, 4400.0)
    local real curX = GetUnitX(u)
    local real curY = GetUnitY(u)
    local real mdeg = ModuloReal(Atan2(ty - curY, tx - curX) * bj_RADTODEG + 360.0, 360.0)
    call SaveReal(Ab_HT, GetHandleId(u), 901, mdeg)
    call SaveReal(Ab_HT, GetHandleId(u), 903, tx)
    call SaveReal(Ab_HT, GetHandleId(u), 904, ty)
    call SaveInteger(Ab_HT, GetHandleId(u), 902, 1)
    call IssuePointOrder(u, "move", tx, ty)
endfunction

function Form_ShowWalkInitUnit takes nothing returns nothing
    local unit u = GetEnumUnit()
    local real sx = 0.0
    local real sy = 0.0
    if u != null and GetWidgetLife(u) > 0.405 then
        call PauseUnit(u, false)
        call SetUnitPathing(u, false)
        call SetUnitMoveSpeed(u, 420.0)
        // Spread starting positions gently so 100+ models don't collide in a single pile
        set sx = GetRandomReal(-4200.0, 4200.0)
        set sy = GetRandomReal(-3800.0, 3400.0)
        call SetUnitX(u, sx)
        call SetUnitY(u, sy)
        call Form_ShowPickTarget(u)
    endif
    set u = null
endfunction

function Form_ShowWalkUnit takes nothing returns nothing
    local unit u = GetEnumUnit()
    local integer hid = 0
    local real dx = 0.0
    local real dy = 0.0
    if u != null and GetWidgetLife(u) > 0.405 then
        set hid = GetHandleId(u)
        set dx = GetUnitX(u) - LoadReal(Ab_HT, hid, 903)
        set dy = GetUnitY(u) - LoadReal(Ab_HT, hid, 904)
        if LoadInteger(Ab_HT, hid, 902) != 1 or GetUnitCurrentOrder(u) == 0 or (dx * dx + dy * dy) < 160000.0 then
            call Form_ShowPickTarget(u)
        endif
    endif
    set u = null
endfunction

function Form_ShowStopUnit takes nothing returns nothing
    local unit u = GetEnumUnit()
    if u != null and GetWidgetLife(u) > 0.405 then
        call IssueImmediateOrder(u, "stop")
        call SetUnitPathing(u, true)
        call PauseUnit(u, true)
    endif
    set u = null
endfunction

function Form_ShowWalkTick takes nothing returns nothing
    if Form_Show_Group != null then
        call ForGroup(Form_Show_Group, function Form_ShowWalkUnit)
    endif
endfunction

function Form_UnitLabel takes unit u returns string
    local string uname = GetUnitName(u)
    local string pname = ""
    if IsUnitType(u, UNIT_TYPE_HERO) then
        set pname = GetHeroProperName(u)
        if pname != "" and pname != uname then
            return pname + " [" + uname + "]"
        endif
    endif
    return uname
endfunction

function Form_ShowStartWalk takes player pTrig returns nothing
    if Form_Show_Group == null or CountUnitsInGroup(Form_Show_Group) == 0 then
        call Form_Show(pTrig)
    endif
    call Form_ShowClearTags()
    if Form_Show_WalkTimer == null then
        set Form_Show_WalkTimer = CreateTimer()
    endif
    call ForGroup(Form_Show_Group, function Form_ShowWalkInitUnit)
    call TimerStart(Form_Show_WalkTimer, 2.0, true, function Form_ShowWalkTick)
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cff00ff00[SHOWWALK] All shown Pokemon spread & walking across the WHOLE MAP (Gen 1-2 hidden, no collision)! Click to inspect, -mark to hide+log, -showlog to dump, -showstop to freeze.|r")
endfunction

function Form_ShowStopWalk takes player pTrig returns nothing
    if Form_Show_WalkTimer != null then
        call PauseTimer(Form_Show_WalkTimer)
    endif
    if Form_Show_Group != null then
        call ForGroup(Form_Show_Group, function Form_ShowStopUnit)
    endif
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 6.0, "|cffffcc00[SHOWSTOP] All showcase Pokemon frozen in place.|r")
endfunction

function Form_AngleDiff takes real a, real b returns real
    local real d = RAbsBJ(ModuloReal(a - b + 360.0, 360.0))
    if d > 180.0 then
        set d = 360.0 - d
    endif
    return d
endfunction

function Form_OnSelectShowcase takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local player p = GetTriggerPlayer()
    local integer hid = 0
    local real fac = 0.0
    local real mdeg = 0.0
    local real diff = 0.0
    if p != Player(0) or u == null or Form_Show_Group == null then
        set u = null
        set p = null
        return
    endif
    if not IsUnitInGroup(u, Form_Show_Group) then
        set u = null
        set p = null
        return
    endif
    set Form_Show_LastSel = u
    set hid = GetHandleId(u)
    set fac = ModuloReal(GetUnitFacing(u) + 360.0, 360.0)
    if LoadInteger(Ab_HT, hid, 902) == 1 then
        set mdeg = LoadReal(Ab_HT, hid, 901)
        set diff = Form_AngleDiff(fac, mdeg)
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cff00ffff[SHOWLOG]|r " + Form_UnitLabel(u) + " | Facing=" + I2S(R2I(fac)) + " deg | Move=" + I2S(R2I(mdeg)) + " deg | Diff=" + I2S(R2I(diff)) + " deg (type -mark to flag)")
    else
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cff00ffff[SHOWLOG]|r " + Form_UnitLabel(u) + " | Facing=" + I2S(R2I(fac)) + " deg (idle, type -mark to flag)")
    endif
    set u = null
    set p = null
endfunction

function Form_ShowLogCheckUnit takes nothing returns nothing
    local unit u = GetEnumUnit()
    local integer hid = 0
    local real fac = 0.0
    local real mdeg = 0.0
    local real diff = 0.0
    local string line = ""
    if u != null then
        set hid = GetHandleId(u)
        if LoadInteger(Ab_HT, hid, 902) == 1 then
            set fac = ModuloReal(GetUnitFacing(u) + 360.0, 360.0)
            set mdeg = LoadReal(Ab_HT, hid, 901)
            set diff = Form_AngleDiff(fac, mdeg)
            if diff > 35.0 then
                set line = "[TURN/STUCK] " + Form_UnitLabel(u) + " Fac=" + I2S(R2I(fac)) + " Move=" + I2S(R2I(mdeg)) + " Diff=" + I2S(R2I(diff))
                call Preload(line)
                if Form_Log_Shown < 12 then
                    call DisplayTimedTextToPlayer(Player(0), 0, 0, 12.0, "|cffff6666  " + line + "|r")
                endif
                set Form_Log_Shown = Form_Log_Shown + 1
            endif
        endif
    endif
    set u = null
endfunction

function Form_SaveLogFile takes nothing returns nothing
    local integer i = 0
    call PreloadGenClear()
    call Preload("=== New Pokemon Arena 1.0 -showlog ===")
    loop
        exitwhen i >= Form_Log_Count
        call Preload("MARKED: " + Form_Log_Lines[i])
        set i = i + 1
    endloop
    call PreloadGenEnd("NewPokemonArena_ShowLog.txt")
endfunction

function Form_PrintShowLog takes player pTrig returns nothing
    local integer i = 0
    call PreloadGenClear()
    call Preload("=== New Pokemon Arena 1.0 -showlog ===")
    call DisplayTimedTextToPlayer(pTrig, 0, 0, 12.0, "|cff00ffff=== [SHOWLOG] Marked models (" + I2S(Form_Log_Count) + ") ===|r")
    loop
        exitwhen i >= Form_Log_Count
        call Preload("MARKED: " + Form_Log_Lines[i])
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 12.0, "  " + I2S(i + 1) + ". " + Form_Log_Lines[i])
        set i = i + 1
    endloop
    set Form_Log_Shown = 0
    if Form_Show_Group != null then
        call ForGroup(Form_Show_Group, function Form_ShowLogCheckUnit)
    endif
    call PreloadGenEnd("NewPokemonArena_ShowLog.txt")
    if Form_Log_Count == 0 and Form_Log_Shown == 0 then
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cff44ff44[SHOWLOG] Saved CustomMapData/NewPokemonArena_ShowLog.txt (0 stuck/marked). Click any sideways model and type -mark!|r")
    else
        call DisplayTimedTextToPlayer(pTrig, 0, 0, 8.0, "|cff00ffff[SHOWLOG] Also saved to CustomMapData/NewPokemonArena_ShowLog.txt!|r")
    endif
endfunction

function Form_MarkUnit takes unit su, player p returns nothing
    local integer hid = 0
    local string entry = ""
    if su == null or Form_Show_Group == null or not IsUnitInGroup(su, Form_Show_Group) then
        return
    endif
    set hid = GetHandleId(su)
    set entry = Form_UnitLabel(su) + " (Fac=" + I2S(R2I(GetUnitFacing(su)))
    if LoadInteger(Ab_HT, hid, 902) == 1 then
        set entry = entry + ", Move=" + I2S(R2I(LoadReal(Ab_HT, hid, 901)))
    endif
    set entry = entry + ")"
    if Form_Log_Count < 300 then
        set Form_Log_Lines[Form_Log_Count] = entry
        set Form_Log_Count = Form_Log_Count + 1
    endif
    call ShowUnit(su, false)
    call GroupRemoveUnit(Form_Show_Group, su)
    call RemoveUnit(su)
    call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00[MARKED & HIDDEN]|r " + entry)
endfunction

function Form_OnChatOrItem takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local string msg = GetEventPlayerChatString()
    local unit u = null
    local group gSel = null
    local integer markedNow = 0
    local integer c = 0
    if msg == "-form" then
        set u = PAX_MB_FindHero(GetPlayerId(p))
        if u != null and GetWidgetLife(u) > 0.405 then
            call Form_ShowDialog(p, u)
        endif
    elseif msg == "-show" and p == Player(0) then
        call Form_Show(p)
    elseif msg == "-showall" and p == Player(0) then
        call Form_ShowAll(p)
    elseif msg == "-showforms" and p == Player(0) then
        call Form_ShowFormsOnly(p)
    elseif (msg == "-showwalk" or msg == "-wander" or msg == "-walk") and p == Player(0) then
        call Form_ShowStartWalk(p)
    elseif (msg == "-showstop" or msg == "-stopwalk") and p == Player(0) then
        call Form_ShowStopWalk(p)
    elseif msg == "-mark" and p == Player(0) then
        set gSel = CreateGroup()
        call GroupEnumUnitsSelected(gSel, p, null)
        loop
            set u = FirstOfGroup(gSel)
            exitwhen u == null
            call GroupRemoveUnit(gSel, u)
            if Form_Show_Group != null and IsUnitInGroup(u, Form_Show_Group) then
                call Form_MarkUnit(u, p)
                set markedNow = markedNow + 1
            endif
        endloop
        call DestroyGroup(gSel)
        set gSel = null
        if markedNow == 0 and Form_Show_LastSel != null then
            if Form_Show_Group != null and IsUnitInGroup(Form_Show_LastSel, Form_Show_Group) then
                call Form_MarkUnit(Form_Show_LastSel, p)
                set markedNow = 1
            endif
        endif
        set Form_Show_LastSel = null
        if markedNow > 0 then
            call Form_SaveLogFile()
        else
            call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffff4444Click (or drag-select) showcase Pokemon first, then type -mark.|r")
        endif
    elseif msg == "-showlog" and p == Player(0) then
        call Form_PrintShowLog(p)
    elseif msg == "-clear" and p == Player(0) then
        call Form_ShowClearCreeps()
        set Form_Log_Count = 0
        set Form_Show_LastSel = null
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[SHOW] All field creeps & showcase models cleared (spam paused).|r")
    elseif msg == "-respawn" and p == Player(0) then
        set c = 0
        loop
            exitwhen c >= Wild_CampN
            set Wild_CampDue[c] = Wild_Time + 1.0
            set c = c + 1
        endloop
        set Leg_Next = Wild_Time + 60.0
        call ResumeTimer(PAX_Arena_Schedule)
        call FogEnable(PAX_FogEnabled)
        call FogMaskEnable(PAX_FogEnabled)
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cff00ff00[SHOW] Wild camps, Bosses & Arena timers resumed!|r")
    elseif GetSpellAbilityId() == 'AIRG' or GetSpellAbilityId() == 'AIFS' then
        set u = GetTriggerUnit()
        if u != null and GetWidgetLife(u) > 0.405 then
            call Form_ShowDialog(p, u)
        endif
    endif
    set p = null
    set u = null
endfunction

function Form_InitSystem takes nothing returns nothing
    local integer i = 0
    local trigger t = CreateTrigger()
    local trigger tSel = CreateTrigger()
    set Form_DlgTrig = CreateTrigger()
    call TriggerAddAction(Form_DlgTrig, function Form_OnDlgClick)
    call TriggerRegisterPlayerUnitEventSimple(tSel, Player(0), EVENT_PLAYER_UNIT_SELECTED)
    call TriggerAddAction(tSel, function Form_OnSelectShowcase)
    set tSel = null
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-form", true)
        set i = i + 1
    endloop
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-show", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-showall", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-showforms", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-showwalk", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-wander", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-walk", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-showstop", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-stopwalk", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-mark", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-showlog", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-clear", true)
    call TriggerRegisterPlayerChatEvent(t, Player(0), "-respawn", true)
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(t, function Form_OnChatOrItem)
    set t = null
endfunction
""")
    late_blocks.extend(show_jass)

    # Inject Form globals right before endglobals
    form_globals = """    dialog array Form_Dlg
    button array Form_DlgBtn
    integer array Form_DlgVal
    integer array Form_DlgMode
    unit array Form_Hero
    trigger Form_DlgTrig = null
    group Form_Show_Group = null
    timer Form_Show_WalkTimer = null
    unit Form_Show_LastSel = null
    string array Form_Log_Lines
    integer Form_Log_Count = 0
    integer Form_Log_Shown = 0
    texttag array Form_Show_Tags
    integer Form_Show_TagCount = 0
    integer Form_Show_Col = 0
    integer Form_Show_Row = 0
    integer Form_Show_Total = 0
"""
    script = _once(script, "\nendglobals", "\n" + form_globals + "endglobals", "Insert Form globals")

    # Hook Fx_DynaCast & Fx_DynaEnd for 12 G-Max skins
    script = _once(
        script,
        "    set fxScale = BlzGetUnitRealField(u, UNIT_RF_SCALING_VALUE)\n    call SaveReal(Fx_HT, hand, 88, fxScale)\n    call SetUnitScale(u, fxScale * Fx_DynaScale, fxScale * Fx_DynaScale, fxScale * Fx_DynaScale)",
        "    set fxScale = BlzGetUnitRealField(u, UNIT_RF_SCALING_VALUE)\n    call SaveReal(Fx_HT, hand, 88, fxScale)\n"
        "    if Gmax_SkinId(GetUnitTypeId(u)) != 0 then\n"
        "        call BlzSetUnitSkin(u, Gmax_SkinId(GetUnitTypeId(u)))\n"
        "        call SetUnitScale(u, 1.35, 1.35, 1.35)\n"
        "        call PAX_Leg_Sync(u)\n"
        "    else\n"
        "        call SetUnitScale(u, fxScale * Fx_DynaScale, fxScale * Fx_DynaScale, fxScale * Fx_DynaScale)\n"
        "    endif",
        "Hook G-Max skin in Fx_DynaCast",
    )
    script = _once(
        script,
        "    call RemoveSavedReal(Fx_HT, hand, 87)\n    call SetUnitScale(u, fxScale, fxScale, fxScale)",
        "    call RemoveSavedReal(Fx_HT, hand, 87)\n    if Gmax_SkinId(GetUnitTypeId(u)) != 0 then\n"
        "        call BlzSetUnitSkin(u, GetUnitTypeId(u))\n    endif\n"
        "    call SetUnitScale(u, fxScale, fxScale, fxScale)\n    call PAX_Leg_Sync(u)",
        "Revert G-Max skin in Fx_DynaEnd",
    )

    # Place JASS functions in strict top-down declaration order:
    script = _once(
        script,
        "function PAX_Leg_Awakened takes unit u returns boolean",
        "\n".join(early_blocks) + "\nfunction PAX_Leg_Awakened takes unit u returns boolean",
        "Insert Gmax_SkinId, Form_IsFinalHP, Form_QuestIdx before PAX_Leg_Awakened",
    )
    script = _once(
        script,
        "function Fx_Init takes nothing returns nothing",
        "\n".join(fx_blocks) + "\nfunction Fx_Init takes nothing returns nothing",
        "Insert Form_CopyMoves, Form_InitData*, Form_EvoData before Fx_Init",
    )
    script = _once(
        script,
        "function Mega_Init takes nothing returns nothing",
        "\n".join(late_blocks) + "\nfunction Mega_Init takes nothing returns nothing",
        "Insert Form UI & Showcase before Mega_Init",
    )

    # Update PAX_Leg_Count = 58, PAX_Leg_Name(58), PAX_Leg_Awakened, PAX_Leg_QuestCmd, PAX_Leg_Tick1s, PAX_Leg_Sync
    script = _once(
        script,
        "function PAX_Leg_Count takes nothing returns integer\n    return 57",
        "function PAX_Leg_Count takes nothing returns integer\n    return 58",
        "PAX_Leg_Count = 58",
    )
    script = _once(
        script,
        '    elseif idx == 57 then\n        return "Eternatus"\n    endif',
        '    elseif idx == 57 then\n        return "Eternatus"\n    elseif idx == 58 then\n        return "Final Form (Hidden Power)"\n    endif',
        "PAX_Leg_Name(58)",
    )
    script = _once(
        script,
        "function PAX_Leg_Awakened takes unit u returns boolean\n    local integer idx = 0\n    local integer pid = 0\n    local integer qk = 0\n    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) then\n        return false\n    endif\n    set idx = PAX_Leg_Index(GetUnitTypeId(u))",
        "function PAX_Leg_Awakened takes unit u returns boolean\n    local integer idx = 0\n    local integer pid = 0\n    local integer qk = 0\n    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) then\n        return false\n    endif\n    set idx = Form_QuestIdx(u)",
        "PAX_Leg_Awakened uses Form_QuestIdx",
    )
    script = _once(
        script,
        "        if IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then\n            set idx = PAX_Leg_Index(GetUnitTypeId(u))",
        "        if IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then\n            set idx = Form_QuestIdx(u)",
        "PAX_Leg_QuestCmd uses Form_QuestIdx",
    )
    script = _once(
        script,
        "                call PAX_HeroMega_KeepAlive(u)\n                set idx = PAX_Leg_Index(GetUnitTypeId(u))",
        "                call PAX_HeroMega_KeepAlive(u)\n                set idx = Form_QuestIdx(u)",
        "PAX_Leg_Tick1s uses Form_QuestIdx",
    )
    script = _once(
        script,
        "    set idx = PAX_Leg_Index(GetUnitTypeId(src))\n    set pid = GetPlayerId(GetOwningPlayer(src))",
        "    set idx = Form_QuestIdx(src)\n    set pid = GetPlayerId(GetOwningPlayer(src))",
        "PAX_Leg damage progress uses Form_QuestIdx",
    )
    script = _once(
        script,
        "    set idx = PAX_Leg_Index(GetUnitTypeId(killer))\n    if idx == 0 then\n        return\n    endif\n    set qk = PAX_Leg_QKey(pid, idx)\n    set stage = PAX_Leg_Stage(qk)",
        "    set idx = Form_QuestIdx(killer)\n    if idx == 0 then\n        return\n    endif\n    set qk = PAX_Leg_QKey(pid, idx)\n    set stage = PAX_Leg_Stage(qk)",
        "PAX_Leg kill progress uses Form_QuestIdx",
    )
    # In PAX_Leg_Sync: give final-form heroes AFHP when awakened, AFHL when locked; strip both if not Form_IsFinalHP
    script = _once(
        script,
        "    set idx = PAX_Leg_Index(GetUnitTypeId(u))\n    set pid = GetPlayerId(GetOwningPlayer(u))\n    set mi = LoadInteger(Mega_HT, GetHandleId(u), 0) - 1\n    set formId = PAX_Form_Id(u)\n    if pid < 12 and (idx > 0 or formId >= 13) then\n        if PAX_Leg_Awakened(u) then\n            set megaAb = PAX_Leg_MegaAbId(mi)\n            set wantAb = PAX_Form_AbId(formId)\n            if megaAb != 0 then\n                set wantAb = megaAb\n            elseif wantAb == 0 then\n                set wantAb = PAX_Leg_AwAbId(idx)\n            endif\n        elseif idx > 0 then\n            set wantAb = PAX_Leg_AbId(idx)\n        endif\n    endif",
        "    set idx = Form_QuestIdx(u)\n    set pid = GetPlayerId(GetOwningPlayer(u))\n    set mi = LoadInteger(Mega_HT, GetHandleId(u), 0) - 1\n    set formId = PAX_Form_Id(u)\n    if pid < 12 and idx > 0 then\n        if PAX_Leg_Awakened(u) then\n            set megaAb = PAX_Leg_MegaAbId(mi)\n            set wantAb = PAX_Form_AbId(formId)\n            if megaAb != 0 then\n                set wantAb = megaAb\n            elseif wantAb == 0 then\n                set wantAb = PAX_Leg_AwAbId(idx)\n            endif\n            if wantAb == 0 then\n                set wantAb = 'AFHP'\n            endif\n        else\n            set wantAb = PAX_Leg_AbId(idx)\n            if wantAb == 0 then\n                set wantAb = 'AFHL'\n            endif\n        endif\n    endif\n"
        "    if wantAb == 'AFHP' then\n        if GetUnitAbilityLevel(u, 'AFHP') == 0 then\n            call UnitAddAbility(u, 'AFHP')\n        endif\n    elseif GetUnitAbilityLevel(u, 'AFHP') > 0 then\n        call UnitRemoveAbility(u, 'AFHP')\n    endif\n"
        "    if wantAb == 'AFHL' then\n        if GetUnitAbilityLevel(u, 'AFHL') == 0 then\n            call UnitAddAbility(u, 'AFHL')\n        endif\n    elseif GetUnitAbilityLevel(u, 'AFHL') > 0 then\n        call UnitRemoveAbility(u, 'AFHL')\n    endif",
        "PAX_Leg_Sync final-form Hidden Power gating",
    )

    # Hook Form_InitData*, Form_EvoData, and Form_InitSystem at end of Fx_Init / Mega_Init
    script = _once(
        script,
        '    call ExecuteFunc("G14_Data27")\n',
        '    call ExecuteFunc("G14_Data27")\n' + "\n".join(jass_calls) + "\n",
        "Call Form_InitData & Form_EvoData after G14_Data27",
    )
    script = _once(
        script,
        '    call TimerStart(CreateTimer(), 0.5, true, function Ver2n_Tick)',
        '    call TimerStart(CreateTimer(), 0.5, true, function Ver2n_Tick)\n    call Form_InitSystem()',
        "Hook Form_InitSystem in Mega_Init",
    )

    stats = {
        "new_megas": len(new_megas),
        "gmax_skins": len(GMAX_BASES),
        "paradox_skins": len(paradox_skin_ids),
        "hero_forms": len(hero_form_keys),
        "final_hp_heroes": len(final_hp_hero_ids),
        "ability_fallback": sorted(set(ability_fallback)),
        "form_heroes": pf_key_by_id,
        "mega_keys": mega_key_by_index,
    }
    if stats["ability_fallback"]:
        print("[form_expansion] WARNING: no Ability in the map yet for %d forms (old by-type placeholder kept): %s"
              % (len(stats["ability_fallback"]), ", ".join(stats["ability_fallback"])))
    print(f"[form_expansion] Added +{stats['new_megas']} Megas (total {mega_idx}), "
          f"+{stats['gmax_skins']} G-Max, +{stats['paradox_skins']} Paradox skins, "
          f"+{stats['hero_forms']} form heroes ({stats['final_hp_heroes']} final-HP units)")
    return strings, item_func, script, stats
