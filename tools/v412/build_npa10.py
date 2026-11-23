"""Build New Pokemon Arena 1.0.w3x on top of the friend's Pokemon Arena v4.2.w3x:

- Preserves ALL v4.2 base features & balance changes (No Player-ID lock, Auto Arena PAX_Arena_*,
  PAX_Solo_CanStart, Forge proximity PAX_Forge_Near + title 15, Relic effectType 8 + CDR +
  BossShred, Wild_Respawn = 25.0s, PAX_Loot_CampFactor, Wild_IsParadoxSoul 10%, PAX_HealMult
  0.60/0.40, Hard Stone 20% reflect, PAX_GodChu on Raichu, Agility MS/CDR scaling).
- Ports ALL v4.3c features & fixes (A800..A851 Gold '+' unlock + 12-slot overflow fix + 60s CD,
  14s Revive Watchdog clearing stuck BlzPauseUnitEx, Boss Armor 150..200, 50/50 52 wild camps,
  leak fixes, -tp cleanse, -mid, move_ability_fix, ability_rw 105 abilities, hidden_ability,
  move_tutor, wild_mix, item_fix, boss_isolation, model_upgrades 88 HD, melee_ranged_classifier,
  gen14_expansion +166 Gen 1-4 species, random_gen, --dev / online mode, map_optimizer).
- Keeps ONLY the 104 form-bearing evolution lines (first-stage only) in Taverns, -pick,
  -random AND Wild Creep Camps (form_roster).
- Packs all 105 active form models (form_assets) + Mega Z-A, 12 G-Max Dynamax skins, Regional
  Charm, Form & Tera Orb, Booster Energy real models, and -quest Final-Form Hidden Power
  (form_expansion).

Run from _PokemonArena2.0_work:
  python tools/v412/build_npa10.py [--dev] [--dry-run] [--overwrite]
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path[:0] = [os.path.join(WORK, "tools"), HERE]

import ability_rw  # noqa: E402
import boss_isolation  # noqa: E402
import build_v43  # noqa: E402
import form_assets  # noqa: E402
import form_expansion  # noqa: E402
import form_pokeapi  # noqa: E402
import form_roster  # noqa: E402
import gen14_expansion  # noqa: E402
import hidden_ability  # noqa: E402
import hidden_ability_new  # noqa: E402
import hidden_power  # noqa: E402
import item_fix  # noqa: E402
import map_optimizer  # noqa: E402
import mdx_check  # noqa: E402
import melee_ranged_classifier  # noqa: E402
import model_upgrades  # noqa: E402
import move_ability_fix  # noqa: E402
import move_tutor  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402
import random_gen  # noqa: E402
import slk  # noqa: E402
import test_commands  # noqa: E402
import wild_mix  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, "Pokemon Arena v4.2.w3x")
NEW_TITLE = "New Pokemon Arena 1.0"
OUT_MAP = os.path.join(MAPS, f"{NEW_TITLE}.w3x")
PJASS = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
REF = os.path.join(WORK, "analysis", "jass_ref")


def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[build_npa10] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


def patch_core_v42_compat(s: str, unlock_to_cast: dict) -> str:
    """Applies build_v43 core patches while preserving v4.2's Wild_Respawn=25s, CampFactor loot & Paradox 10% soul."""
    full_block = build_v43._build_unlock_jass(unlock_to_cast)
    helper_part, onlearn_part = full_block.split("\nfunction PAX_HeroMegaUnlock_OnLearn", 1)
    onlearn_part = "function PAX_HeroMegaUnlock_OnLearn" + onlearn_part

    # Ensure ReviveWatchdog also clears PAX_DeadSince so v4.2's 15s check and 14s watchdog never double-revive
    watchdog = build_v43.REVIVE_WATCHDOG_JASS.replace(
        "    call SaveInteger(PAX_Leg_HT, heroHandleId, 220, 0)\n",
        "    call SaveInteger(PAX_Leg_HT, heroHandleId, 220, 0)\n    set PAX_DeadSince[ownerPid] = 0.0\n",
        1,
    )

    s = _once(
        s,
        "function PAX_Leg_Tick1s takes nothing returns nothing",
        helper_part + "\n\n" + watchdog + "\n\nfunction PAX_Leg_Tick1s takes nothing returns nothing",
        "Insert Mega KeepAlive & Watchdog before PAX_Leg_Tick1s",
    )
    s = _once(s, build_v43.OLD_ONLEARN, onlearn_part, "Replace PAX_HeroMegaUnlock_OnLearn")
    s = _once(s, build_v43.OLD_PAXT_FORM_APPLY, build_v43.NEW_PAXT_FORM_APPLY, "Remove PAXT from PAX_Form_Apply")
    s = _once(s, build_v43.OLD_FORM_CD_DEOX, build_v43.NEW_FORM_CD_DEOX, "Deoxys Form CD 600s -> 60s")
    s = _once(s, build_v43.OLD_FORM_CD_OTHER, build_v43.NEW_FORM_CD_OTHER, "Form Switch CD 600s -> 60s")
    s = _once(s, build_v43.OLD_AB_SYNC_ADD, build_v43.NEW_AB_SYNC_ADD, "Hide cosmetic Ab_InfoId on Mewtwo/Kyurem")
    s = _once(s, build_v43.OLD_TICK1S_SYNC, build_v43.NEW_TICK1S_SYNC, "Wire PAX_HeroMega_KeepAlive in PAX_Leg_Tick1s")
    s = _once(s, build_v43.OLD_TICK1S_HERO_END, build_v43.NEW_TICK1S_HERO_END, "Wire PAX_ReviveWatchdog_Step in PAX_Leg_Tick1s")

    # Boss armor 150..200 rebalance
    s = _once(s, build_v43.OLD_BOSS_ARMOR_SET, build_v43.NEW_BOSS_ARMOR_SET, "Legend Boss Armor comment")
    s = _once(s, build_v43.OLD_BOSS_ARMOR_CALL, build_v43.NEW_BOSS_ARMOR_CALL, "Legend Boss Armor 150..200")

    # Wild_Respawn stays 25.0s and PAX_Loot_CampFactor + Wild_IsParadoxSoul 10% stay intact from v4.2;
    # keep Mega Elite Soul check & no mid-combat reinforcement cap
    s = _once(s, build_v43.OLD_WILD_TICK_LOOP, build_v43.NEW_WILD_TICK_LOOP, "Respawn only when whole camp dead")
    old_wild_soul_v42 = "if soul != 0 and LoadInteger(Mega_HT, h, 29) == 1 and GetRandomReal(0.0, 100.0) < chance then"
    new_wild_soul_v42 = "if soul != 0 and (LoadInteger(Mega_HT, h, 29) == 1 or LoadInteger(Mega_HT, h, 44) > 0) and GetRandomReal(0.0, 100.0) < chance then"
    s = _once(s, old_wild_soul_v42, new_wild_soul_v42, "Soul drop on regular + Mega Elites (v4.2 chance)")

    s = _once(
        s,
        "function Wild_SpawnCamp takes integer c returns nothing",
        build_v43.WILD_UNIQUE_HELPERS_JASS + "\n\nfunction Wild_SpawnCamp takes integer c returns nothing",
        "Insert Wild_IsTypeUsed & Wild_PickUniqueType",
    )
    s = _once(s, build_v43.OLD_WILD_SPAWNCAMP_PICK, build_v43.NEW_WILD_SPAWNCAMP_PICK, "Use Wild_PickUniqueType")
    s = _once(s, build_v43.OLD_WILD_REGISTER_CAMPS, build_v43.NEW_WILD_REGISTER_CAMPS, "Clear v1.8 creeps & stagger spawns")

    # -tp full cleanse + -mid command
    s = _once(
        s,
        "function Fx_TpGo takes nothing returns nothing",
        build_v43.CLEANSE_AND_MID_JASS + "\n\nfunction Fx_TpGo takes nothing returns nothing",
        "Insert PAX_CleanseAllDebuffs before Fx_TpGo",
    )
    s = _once(s, build_v43.OLD_TP_CURE, build_v43.NEW_TP_CURE, "Call PAX_CleanseAllDebuffs in Fx_TpGo")
    s = _once(
        s,
        "function Fx_HomeChat takes nothing returns nothing",
        build_v43.MID_CMD_JASS + "\n\nfunction Fx_HomeChat takes nothing returns nothing",
        "Insert PAX_MidGo & PAX_MidChat",
    )
    s = _once(s, build_v43.OLD_FX_INIT_HOME, build_v43.NEW_FX_INIT_HOME, "Register -mid chat command")

    # 50/50 52 camps + leak fixes
    s = build_v43._patch_wild_camps_50_50(s)
    s = _once(s, build_v43.OLD_MEGA_INIT_END, build_v43.NEW_MEGA_INIT_END, "Disable legacy spawners & runaway ts")
    s = _once(s, build_v43.OLD_TRAP_SD_BD, build_v43.NEW_TRAP_SD_BD, "Fix location leaks in sD..BD traps")
    s = _once(s, build_v43.OLD_TRAP_JD_LD, build_v43.NEW_TRAP_JD_LD, "Fix location leaks in JD/LD traps")
    s = _once(s, build_v43.OLD_FY4, build_v43.NEW_FY4, "Fix force leaks in Fy4 Arena Duel")
    for outer, inner in build_v43.DUEL_GROUP_HELPERS:
        old_h = f"function {outer} takes nothing returns nothing\ncall ForGroupBJ(Wy(GetEnumPlayer()),function {inner})\nendfunction"
        new_h = (
            f"function {outer} takes nothing returns nothing\n"
            f"local group duelGrp=Wy(GetEnumPlayer())\n"
            f"call ForGroupBJ(duelGrp,function {inner})\n"
            f"call DestroyGroup(duelGrp)\n"
            f"set duelGrp=null\n"
            f"endfunction"
        )
        s = _once(s, old_h, new_h, f"Fix group leak in {outer}")
    return s


def build_data(optimize_assets: bool = True, dev_mode: bool = False):
    base = mpq.MPQ(BASE_MAP)
    script = base.read("scripts" + BS + "war3map.j").decode("utf-8")
    crlf = "\r\n" in script
    script = script.replace("\r\r\n", "\r\n").replace("\r\n", "\n")

    w3u = objdata.ObjFile(base.read("war3map.w3u"))
    abil = slk.Slk(base.read("Units" + BS + "AbilityData.slk").decode("latin-1"))
    strings = base.read("Units" + BS + "CampaignAbilityStrings.txt").decode("utf-8")
    items_slk = slk.Slk(base.read("Units" + BS + "ItemData.slk").decode("latin-1"))
    item_func = base.read("Units" + BS + "ItemFunc.txt").decode("utf-8", errors="replace")

    # 1. Gold '+' Mega/Form Unlock (52 base Megas)
    strings, unlock_to_cast = build_v43.patch_objects_and_collect_map(w3u, abil, strings)

    # 2. PokeAPI Move Fix + 105 Ability Rework + Hidden Ability (compatible with v4.2 PAX_HealMult)
    script = move_ability_fix.patch(script)
    script = ability_rw.patch(script)
    strings = ability_rw.patch_objects(abil, strings)
    script = hidden_ability.patch(script)

    # 3. Core v4.3c fixes adapted to preserve v4.2 custom features/balances
    script = patch_core_v42_compat(script, unlock_to_cast)

    # 4. Move Tutor, Wild Mix, Item Fix, Boss Isolation
    script = move_tutor.patch_script(script)
    script = wild_mix.patch_script(script)
    item_fix.patch_objects(abil)
    item_func = item_fix.patch_item_text(item_func)
    script = item_fix.patch_script(script)
    script = boss_isolation.patch_script(script)

    # 5. Legend scale fix + 88 HD Hero Upgrades + Melee/Ranged 360 Heroes
    script = map_optimizer.normalize_legend_scales(w3u, script)
    for u in w3u.original + w3u.custom:
        if u.id in ("EP01", "nZ01"):
            u.set("usca", 1, 1.25)
        elif u.id in ("EP02", "nZ02"):
            u.set("usca", 1, 1.15)
        elif u.id == "PZZA":
            u.set("usca", 1, 4.50)
    script, hd_stats = model_upgrades.patch_objects_and_script(w3u, script)
    script, mr_stats = melee_ranged_classifier.apply_melee_ranged(w3u, script)

    # 6. Gen 1-4 Expansion (+166 species) & Form Assets + Form Expansion (105 form models + Hidden Power)
    script, item_func, g14_stats = gen14_expansion.patch_objects_and_script(w3u, items_slk, item_func, script)
    form_files, form_meta = form_assets.load_form_assets(compress_blp=optimize_assets, pack_files=True)
    strings, item_func, script, form_stats = form_expansion.patch_all(
        w3u, abil, strings, items_slk, item_func, script, form_meta
    )

    # 6b. Hidden Ability (Ability Patch) for the new Gen 1-4 heroes and form heroes (never Megas / Gigantamax)
    hidden_ids = {sp["hero"]: (form_pokeapi.by_dex(sp["dex"]) or {}).get("hidden")
                  for sp in gen14_expansion.load_species_entries()}
    hidden_ids.update({hid: (form_pokeapi.pokemon(key) or {}).get("hidden")
                       for hid, key in form_stats["form_heroes"].items()})
    hidden_new = hidden_ability_new.collect_entries(script, hidden_ids)
    script = hidden_ability_new.patch(script, hidden_new)

    # 6c. Hidden Power of the final forms: one awakening quest slot per form (quest key 256 per player)
    script = hidden_power.patch(script)

    # 7. -random [gen] + Form Roster Filter (104 kept lines in Taverns, -pick, -random AND Wild Camps)
    script, _gen_stats = random_gen.patch_script(script, w3u)
    script = form_roster.patch_script(script)
    script = form_roster.patch_wild_pool(script)
    form_roster.patch_taverns(w3u)

    # 8. Dev test commands (--dev) & version branding
    if dev_mode:
        print("[build_npa10] --dev mode active: Including test commands (-gen, -c, -lvl, etc.)")
        script = test_commands.patch_script(script)
    else:
        print("[build_npa10] Online multiplayer mode: Developer cheat commands stripped.")

    script = re.sub(r"POKEMON ARENA v4\.2[a-z]?", "NEW POKEMON ARENA 1.0", script)
    script = script.replace("Pokemon Arena v4.2", NEW_TITLE).replace("PA v4.2", "NPA 1.0")
    if crlf:
        script = script.replace("\n", "\r\n")

    w3i = base.read("war3map.w3i").replace(b"Pokemon Arena v4.2", NEW_TITLE.encode("utf-8"))

    files = {
        "scripts" + BS + "war3map.j": script.encode("utf-8"),
        "war3map.w3i": w3i,
        "war3map.w3u": w3u.to_bytes(),
        "Units" + BS + "AbilityData.slk": abil.to_text().encode("latin-1"),
        "Units" + BS + "CampaignAbilityStrings.txt": strings.encode("utf-8"),
        "Units" + BS + "ItemData.slk": items_slk.to_text().encode("latin-1"),
        "Units" + BS + "ItemFunc.txt": item_func.encode("utf-8"),
    }

    delete_files = []
    opt_stats = {
        "orphans_deleted": 0,
        "blps_optimized": 0,
        "blp_raw_saved_mb": 0.0,
        "hd_heroes": hd_stats["heroes_upgraded"],
        "hd_synced_units": hd_stats["matching_units_synced"],
        "mr_melee": mr_stats["melee"],
        "mr_archer": mr_stats["archer"],
        "g14_species": g14_stats["g14_species"],
        "form_models": len(form_meta),
        "form_stats": form_stats,
        "hidden_ability_new": len(hidden_new),
    }
    if optimize_assets:
        files.update(form_files)
        hd_files = model_upgrades.load_hd_assets(compress_blp=True)
        g14_files = gen14_expansion.load_g14_assets(compress_blp=True)
        files.update(hd_files)
        files.update(g14_files)
        deox_path = os.path.join(WORK, "extracted_v1.8", "Deoxys.mdx")
        if os.path.isfile(deox_path):
            with open(deox_path, "rb") as df:
                files["PkFx\\Mega3D\\DeoxysDefense.mdx"] = df.read()
        delete_files = map_optimizer.collect_orphan_deletes(base, files)
        opt_blps, bstats = map_optimizer.optimize_live_blps(base, delete_files, min_size=80_000, quality=75, max_dim=512)
        files.update(opt_blps)
        opt_stats["orphans_deleted"] = len(delete_files)
        opt_stats["blps_optimized"] = bstats["blps_optimized"]
        opt_stats["blp_raw_saved_mb"] = round(bstats["raw_bytes_saved"] / 1048576.0, 2)

    return base, files, delete_files, opt_stats, script


def build(out: str, dry: bool, skip_pjass: bool = False, optimize_assets: bool = True,
          overwrite: bool = False, dev_mode: bool = False):
    if not dry and os.path.exists(out) and not overwrite:
        raise SystemExit(f"Output exists, refusing to overwrite per GEMINI.md: {out}")

    base, files, delete_files, opt_stats, script = build_data(optimize_assets=optimize_assets, dev_mode=dev_mode)

    bad_mdx = {
        n: e[0]
        for n, d in files.items()
        if n.lower().startswith(("pkfx\\g14\\", "pkfx\\forms\\")) and n.lower().endswith(".mdx")
        for e in [mdx_check.check(d)] if e
    }
    if bad_mdx:
        raise SystemExit(f"Broken MDX ({len(bad_mdx)}): {list(bad_mdx.items())[:3]}")

    tmp = os.path.join(REF, "_tmp_npa10_war3map.j")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(script)

    if not skip_pjass and os.path.exists(PJASS):
        r = subprocess.run([PJASS, os.path.join(REF, "common.j"), os.path.join(REF, "Blizzard.j"), tmp],
                           capture_output=True, text=True)
        print("PJASS rc=%d" % r.returncode)
        if r.returncode:
            print((r.stdout + r.stderr)[:1500])
            raise SystemExit(1)

    print(
        f"[build_npa10] files={len(files)} | forms={opt_stats['form_models']} "
        f"| orphans_del={opt_stats['orphans_deleted']} | blps_opt={opt_stats['blps_optimized']} "
        f"(saved {opt_stats['blp_raw_saved_mb']} MB)"
    )
    if dry:
        print("Dry run OK.")
        return

    del_lower = {d.lower().replace("/", "\\") for d in delete_files}
    listfile = sorted(
        {nm for nm in base.listfile() if nm.lower().replace("/", "\\") not in del_lower} | set(files)
    )
    map_optimizer.save_compact(
        base,
        out,
        files,
        delete_files=delete_files,
        extra_listfile=("\r\n".join(listfile) + "\r\n").encode("latin-1"),
    )
    build_v43.patch_hm3w_header(out, NEW_TITLE)
    print(f"Wrote {out} ({os.path.getsize(out) / 1048576.0:.1f} MB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true", help="Include test commands (-gen, -c, -lvl, etc.)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-pjass", action="store_true")
    ap.add_argument("--no-optimize", action="store_true")
    ap.add_argument("--overwrite", "-f", action="store_true")
    ap.add_argument("--out", default=OUT_MAP)
    args = ap.parse_args()
    build(args.out, args.dry_run, args.skip_pjass, optimize_assets=not args.no_optimize,
          overwrite=args.overwrite, dev_mode=args.dev)
