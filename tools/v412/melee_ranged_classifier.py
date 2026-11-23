"""Melee vs Ranged (Archer) Rework for Pokemon Arena v4.2b+.

Reads the user-editable visual checklist `docs/HERO_MELEE_CHECKLIST.md` as single source of truth:
- `[x]` Melee:  ua1w = "normal", ua1r = 128..175, ua1m = "", ua1z = 0, uacq = 500.0
- `[ ]` Archer: ua1w = "missile" (or preserves "mbounce"), ua1r = 450..600,
                ua1m = type-matched WC3 missile (replaces LavaSpawnMissile / empty),
                ua1z = 1150, uacq = 650.0
- Also exports `apply_weapon_for_species(u, is_melee, primary_type, is_legend=False)` so
  newly added Gen 1-4+ Pokemon follow the exact same clean Melee/Archer rules.
- Patches the 3 JASS contact checks (Ab_InContact, Fx_OnHit, Ext_OnHit) so Static,
  Flame Body, Poison Point, Hard Stone, Zapdos contact, and Rocky Helmet fire reliably
  for Melee attackers and never for Archers.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
CHECKLIST_PATH = os.path.join(WORK, "docs", "HERO_MELEE_CHECKLIST.md")

# 100% built-in WC3 missile models mapped to Pokemon primary type (zero extra MPQ size)
TYPE_MISSILE_MAP = {
    "fire": "Abilities\\Weapons\\RedDragonBreath\\RedDragonMissile.mdl",
    "water": "Abilities\\Weapons\\WaterElementalMissile\\WaterElementalMissile.mdl",
    "ice": "Abilities\\Weapons\\LichMissile\\LichMissile.mdl",
    "electric": "Abilities\\Weapons\\ChimaeraLightningMissile\\ChimaeraLightningMissile.mdl",
    "psychic": "Abilities\\Weapons\\FaerieDragonMissile\\FaerieDragonMissile.mdl",
    "ghost": "Abilities\\Weapons\\AvengerMissile\\AvengerMissile.mdl",
    "dark": "Abilities\\Weapons\\AvengerMissile\\AvengerMissile.mdl",
    "fairy": "Abilities\\Weapons\\PriestMissile\\PriestMissile.mdl",
    "grass": "Abilities\\Weapons\\KeeperGroveMissile\\KeeperGroveMissile.mdl",
    "poison": "Abilities\\Weapons\\SludgeMissile\\SludgeMissile.mdl",
    "dragon": "Abilities\\Weapons\\GreenDragonMissile\\GreenDragonMissile.mdl",
    "flying": "Abilities\\Spells\\NightElf\\FanOfKnives\\FanOfKnivesMissile.mdl",
    "steel": "Abilities\\Weapons\\GlaiveMissile\\GlaiveMissile.mdl",
    "rock": "Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl",
    "ground": "Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl",
    "bug": "Abilities\\Weapons\\Dryadmissile\\Dryadmissile.mdl",
    "normal": "Abilities\\Weapons\\Dryadmissile\\Dryadmissile.mdl",
    "fighting": "Abilities\\Weapons\\Dryadmissile\\Dryadmissile.mdl",
}

MELEE_PRIMARY_TYPES = {"fighting", "rock", "ground", "steel", "bug", "normal", "dark"}
RANGED_PRIMARY_TYPES = {"psychic", "ghost", "fairy", "electric", "ice", "water", "fire", "grass"}

CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+.*?`([A-Z0-9]{4})`")


def parse_checklist(md_path: str = CHECKLIST_PATH) -> dict:
    """Returns {hero_id: bool_is_melee} parsed from HERO_MELEE_CHECKLIST.md."""
    if not os.path.isfile(md_path):
        raise FileNotFoundError(f"[melee_ranged] Checklist not found: {md_path}")
    out = {}
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            m = CHECKBOX_RE.match(line)
            if not m:
                continue
            mark, hid = m.group(1), m.group(2)
            out[hid] = (mark.lower() == "x")
    if len(out) < 350:
        raise ValueError(f"[melee_ranged] Expected >=350 heroes in checklist, parsed {len(out)}")
    return out


def infer_primary_type(unit_obj) -> str:
    """Extracts primary Pokemon type from `unam` (e.g. 'Ice&Flying Pokemon' -> 'ice')."""
    unam = str(unit_obj.get("unam") or "")
    m = re.match(r"([A-Za-z]+)", unam.strip())
    if m:
        t = m.group(1).lower()
        if t in TYPE_MISSILE_MAP:
            return t
    return "normal"


def classify_species_is_melee(types, stats) -> bool:
    """Automatic Melee vs Archer classification for newly added Gen 1-4+ Pokemon.

    stats = (hp, atk, def, spa, spd, spe).
    """
    _hp, atk, _df, spa, _spd, _spe = stats
    t0 = types[0].lower() if types else "normal"
    if t0 == "fighting":
        return atk >= spa - 15
    if t0 in ("psychic", "ghost", "fairy", "electric"):
        return atk >= spa + 25
    if atk >= spa + 10:
        return True
    if spa >= atk + 10:
        return False
    return t0 in MELEE_PRIMARY_TYPES


def apply_weapon_for_unit(unit_obj, is_melee: bool, primary_type: str = None, is_legend: bool = False) -> None:
    """Applies clean Melee (`normal`) or Archer (`missile`/`mbounce`) weapon fields to a w3u Obj."""
    ptype = (primary_type or infer_primary_type(unit_obj)).lower()
    if ptype not in TYPE_MISSILE_MAP:
        ptype = "normal"

    cur_r_raw = unit_obj.get("ua1r")
    cur_r = int(cur_r_raw) if cur_r_raw is not None else 0
    cur_w = str(unit_obj.get("ua1w") or "").strip().lower()
    cur_m = str(unit_obj.get("ua1m") or "").strip()

    if is_melee:
        # True WC3 Melee: normal weapon, 128..175 range, no missile art
        if 128 <= cur_r <= 175:
            new_r = cur_r
        else:
            new_r = 165 if is_legend else 150
        unit_obj.set("ua1w", 3, "normal")
        unit_obj.set("ua1r", 0, int(new_r))
        unit_obj.set("ua1m", 3, "")
        unit_obj.set("ua1z", 0, 0)
        unit_obj.set("uacq", 2, 500.0)
    else:
        # True WC3 Archer: missile (or keep mbounce), 450..600 range, type-matched missile
        new_w = "mbounce" if cur_w == "mbounce" else "missile"
        if 450 <= cur_r <= 600:
            new_r = cur_r
        else:
            new_r = 550 if is_legend else 500
        # Replace generic LavaSpawnMissile or blank missile with type-matched WC3 missile
        if (not cur_m) or ("lavaspawn" in cur_m.lower()):
            new_m = TYPE_MISSILE_MAP[ptype]
        else:
            new_m = cur_m
        unit_obj.set("ua1w", 3, new_w)
        unit_obj.set("ua1r", 0, int(new_r))
        unit_obj.set("ua1m", 3, new_m)
        unit_obj.set("ua1z", 0, 1150)
        unit_obj.set("uacq", 2, 650.0)


def _replace_once(script: str, old: str, new: str, label: str) -> str:
    cnt = script.count(old)
    if cnt != 1:
        raise ValueError(f"[melee_ranged] Anchor {label!r} matched {cnt} times (expected 1)")
    return script.replace(old, new, 1)


def patch_jass_contact_checks(script: str) -> str:
    """Patches Ab_InContact, Fx_OnHit, and Ext_OnHit (Rocky Helmet) in war3map.j."""
    if "function Ab_IsMelee takes unit u returns boolean" in script:
        # Friend's v4.2 already uses Ab_IsMelee() (UNIT_TYPE_MELEE_ATTACKER or range <= 220) in all three hooks
        return script
    script = _replace_once(
        script,
        "    if a == AB_STATIC or a == AB_FLAMEBODY or a == AB_POISONPOINT then  // v3.4.11: 30% status on the attacker\n"
        "        if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then",
        "    if a == AB_STATIC or a == AB_FLAMEBODY or a == AB_POISONPOINT then  // v3.4.11: 30% status on the attacker\n"
        "        if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0 then",
        "Ab_InContact melee check",
    )
    script = _replace_once(
        script,
        "    // contact (melee basic attack) on the target\n"
        "    if atk and IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then",
        "    // contact (melee basic attack) on the target\n"
        "    if atk and (IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0) then",
        "Fx_OnHit melee check",
    )
    script = _replace_once(
        script,
        "    if atk and IsUnitType(t, UNIT_TYPE_HERO) and Itm_Flag(t, 7) and BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 250.0 then",
        "    if atk and IsUnitType(t, UNIT_TYPE_HERO) and Itm_Flag(t, 7) and (IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0) then",
        "Ext_OnHit Rocky Helmet melee check",
    )
    return script


def apply_melee_ranged(w3u, script: str, md_path: str = CHECKLIST_PATH):
    """Applies Melee/Archer classification from HERO_MELEE_CHECKLIST.md to all 360 Heroes,
    syncs matching Wild/Boss units (same umdl), and patches the 3 JASS contact hooks."""
    checklist = parse_checklist(md_path)
    by_id = {u.id: u for u in w3u.original + w3u.custom}

    melee_cnt = 0
    archer_cnt = 0
    umdl_role = {}  # umdl_lower -> (is_melee, ptype)

    for hid, is_melee in checklist.items():
        u = by_id.get(hid)
        if u is None:
            raise KeyError(f"[melee_ranged] Hero {hid} from checklist not found in war3map.w3u")
        ptype = infer_primary_type(u)
        is_leg = hid.startswith("EL") or hid in (
            "E020", "E021", "E022", "E023", "E024", "E025", "E026", "E027", "E028", "E029",
            "E03J", "E040", "E041", "E042", "E043", "E044", "E045", "P1TA", "P26A", "P4UA",
            "PV2A", "PZZA",
        )
        apply_weapon_for_unit(u, is_melee=is_melee, primary_type=ptype, is_legend=is_leg)
        umdl = str(u.get("umdl") or "").strip().lower().replace("/", "\\")
        if umdl:
            umdl_role[umdl] = (is_melee, ptype)
        if is_melee:
            melee_cnt += 1
        else:
            archer_cnt += 1

    # Sync matching Wild creeps / Legend Bosses sharing exact same model
    wild_synced = 0
    for u in w3u.original + w3u.custom:
        if u.id in checklist or u.id.startswith(("hM", "nTV", "nTP", "n01H")):
            continue
        if not u.id.startswith(("n0", "nX", "nZ", "nL", "nog", "nst")):
            continue
        umdl = str(u.get("umdl") or "").strip().lower().replace("/", "\\")
        if umdl in umdl_role:
            is_m, pt = umdl_role[umdl]
            apply_weapon_for_unit(u, is_melee=is_m, primary_type=pt, is_legend=u.id.startswith("nL"))
            wild_synced += 1

    script = patch_jass_contact_checks(script)
    stats = {"melee": melee_cnt, "archer": archer_cnt, "wild_synced": wild_synced}
    return script, stats
