"""Tests for Pokemon Arena v4.2b: Mega & Form permanent Unit ANcl fix + 12-slot overflow fix."""
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, os.path.join(WORK, "tools", "v412"))

import build_v42b  # noqa: E402
import map_optimizer  # noqa: E402
import model_upgrades  # noqa: E402
import melee_ranged_classifier  # noqa: E402
import gen14_expansion  # noqa: E402


def test_mega_form_permanent_unit_ancl_and_gold_plus_unlock():
    base, files, _dels, _stats, script, w3u, abil, strings, unlock_to_cast = build_v42b.build_data(optimize_assets=False)
    s = script.replace("\r\n", "\n")
    acol = abil.name_to_x

    # 1. Exactly 52 A800..A851 Gold '+' unlock skills mapped cleanly to AM*
    assert len(unlock_to_cast) == 52
    for uid, cid in unlock_to_cast.items():
        urow = abil.find(uid)
        crow = abil.find(cid)
        assert urow is not None and crow is not None
        # Unlock skill = AEev hero passive (hero=1, levels=1)
        assert urow[acol["code"]] == '"AEev"'
        assert urow[acol["hero"]] == "1"
        assert urow[acol["levels"]] == "1"
        # Castable Mega/Form skill = pure Unit ANcl (hero=0, item=0, Visible=1, follow-through=0.01)
        assert crow[acol["code"]] == '"ANcl"'
        assert crow[acol["hero"]] == "0"
        assert crow[acol["item"]] == "0"
        assert crow[acol["DataC1"]] == "1"
        assert crow[acol["DataA1"]] == "0.01"
        assert crow[acol["DataD1"]] == "0.01"
        # CampaignAbilityStrings has both [A8xx] and Order= on [AMxx]
        assert f"[{uid}]" in strings
        m = re.search(rf"(?m)^\[{re.escape(cid)}\]\r?\n([\s\S]*?)(?=^\[|\Z)", strings)
        assert m and "Order=" in m.group(1), f"Missing Order= on {cid}"

    # 2. Hero uhab now points strictly to A8xx (never AMxx)
    for u in w3u.original + w3u.custom:
        uh = str(u.get("uhab") or "").strip()
        if uh:
            for aid in uh.split(","):
                assert aid.strip().startswith("A8"), f"Hero {u.id} still has non-A8 uhab: {uh}"

    # 3. JASS fixes: UnitMakeAbilityPermanent, KeepAlive in Tick1s, PAXT removed, 60s form CD, Mewtwo/Kyurem slot fix
    assert "call UnitRemoveAbility(heroUnit, learnedAbId)" in s
    assert "call UnitMakeAbilityPermanent(heroUnit, true, castAbId)" in s
    assert "call PAX_HeroMega_KeepAlive(u)" in s
    assert "call UnitAddAbility(u, 'PAXT')" not in s
    assert "BlzStartUnitAbilityCooldown(u, 'AM17', 60.0)" in s
    assert "BlzStartUnitAbilityCooldown(u, PAX_Form_ItemAbility(slot), 60.0)" in s
    assert "BlzStartUnitAbilityCooldown(u, 'AM17', 600.0)" not in s
    assert "call BlzUnitHideAbility(u, Ab_InfoId(want), true)" in s
    assert "v4.2b" in s
    assert b"Pokemon Arena v4.2b" in files["war3map.w3i"]

    # 4. Anti-exploit loot rework: flat 4/12/18/45% (no CampFactor inflation), 5s respawn, 20% Elite Soul
    assert "chance * PAX_Loot_CampFactor(dead)" not in s
    assert "set chance = 18.0" in s
    assert "set chance = 12.0" in s
    assert "set chance = 4.0" in s
    assert "real Wild_Respawn = 5.0" in s
    assert "real Wild_SoulChance = 20.0" in s
    assert "(LoadInteger(Mega_HT, h, 29) == 1 or LoadInteger(Mega_HT, h, 44) > 0)" in s

    # 5. 50/50 Left vs Right jungle camps (26 vs 26 = 52 camps total)
    assert "set Wild_CampN = 52" in s
    xs = [float(m.group(1)) for m in re.finditer(r"set Wild_CampX\[\d+\] = (-?[\d.]+)", s)]
    assert len(xs) == 52
    assert sum(1 for x in xs if x < -400) == 26
    assert sum(1 for x in xs if x > 150) == 26
    for removed_u in (
        "CreateUnit(p,'nogl',4932.5,-3436.6",
        "CreateUnit(p,'nogl',3555.8,-1840.3",
        "CreateUnit(p,'nogl',3281.3,-1940.1",
        "CreateUnit(p,'nogl',3788.3,-5578.9",
    ):
        assert removed_u not in s

    # 6. Minute-48 freeze/dead-forever fix: legacy spawners + ts disabled, leaks fixed, Revive Watchdog active
    for trig in ("Ox", "Sx", "Wx", "xy", "ny", "Jx", "ts"):
        assert f"call DisableTrigger({trig})" in s
    assert "call PAX_ReviveWatchdog_Step(u, pid)" in s
    assert "call DestroyForce(duelFrc)" in s
    assert "call DestroyGroup(duelGrp)" in s
    assert "call RemoveLocation(trapLoc)" in s
    assert "call RemoveLocation(stampLocA)" in s

    # 7. Legend 3D scale normalization (EL0*, nL2*, hM2* & Mega_Scale[39..43])
    by_id = {u.id: u for u in w3u.custom}
    assert abs(float(by_id["EL0J"].get("usca")) - 0.40) < 1e-4  # Lunala
    assert abs(float(by_id["nL2J"].get("usca")) - 0.46) < 1e-4  # Wild Lunala boss
    assert abs(float(by_id["EL0C"].get("usca")) - 0.42) < 1e-4  # Xerneas
    assert abs(float(by_id["EL0E"].get("usca")) - 0.45) < 1e-4  # Zygarde
    assert abs(float(by_id["EL09"].get("usca")) - 0.72) < 1e-4  # Zekrom
    assert abs(float(by_id["hM22"].get("usca")) - 0.80) < 1e-4  # Black Kyurem
    assert "set Mega_Scale[39] = 0.800" in s
    assert "set Mega_BaseScale[39] = 0.650" in s
    assert "set Mega_Scale[40] = 0.650" in s
    assert "set Mega_Scale[42] = 0.880" in s
    assert "set Mega_Scale[43] = 1.080" in s

    # 8. Orphan detection safety: never deletes any live Leg25 MDX/BLP or icon, catches unused Dota2Fx dupes
    deletes = map_optimizer.collect_orphan_deletes(base, files)
    del_low = {d.lower().replace("/", "\\") for d in deletes}
    assert len(deletes) >= 900
    assert "pkfx\\leg25\\644_zekrom.mdx" not in del_low
    assert "pkfx\\leg25\\644a.blp" not in del_low
    assert "pkfx\\leg25\\792_lunala.mdx" not in del_low
    assert not any(d.startswith("replaceabletextures\\") for d in del_low)
    assert not any(d.startswith("units\\") or d.startswith("scripts\\") for d in del_low)

    # 9. BLP1-JPEG round-trip quality & WC3 header safety (<= 624 B)
    sample_raw = base.read("war3mapImported\\Poke\\Rexblisar.blp")
    rgba0, ab, ex = map_optimizer.decode_blp1_jpeg(sample_raw)
    reenc = map_optimizer.encode_blp1_jpeg(rgba0, abits=ab, extra=ex, quality=76, max_dim=512)
    assert len(reenc) < len(sample_raw) * 0.50
    rgba1, _, _ = map_optimizer.decode_blp1_jpeg(reenc)
    assert rgba0.shape == rgba1.shape

    # 10. Legend Boss HP kept (1M..1.5M) & Armor reduced (150..200)
    assert "set newMax = 1000000 + R2I(bossHpRatio * 500000.0)" in s
    assert "call BlzSetUnitArmor(lg, 150.0 + bossArmRatio * 50.0)" in s
    assert "450.0 + bossArmRatio * 250.0" not in s

    # 11. -tp full debuff cleanse, -mid command, v1.8 creep clear & anti-duplicate diverse species
    assert "call PAX_CleanseAllDebuffs(u)" in s
    assert "call UnitRemoveBuffs(targetHero, false, true)" in s
    assert 'call TriggerRegisterPlayerChatEvent(t, Player(i), "-mid", true)' in s
    assert "function PAX_MidChat takes nothing returns nothing" in s
    assert ("set t = Wild_PickUniqueType(pow, c)" in s) or ("set t = WD_Pick(pow)" in s)
    assert "call RemoveUnit(u)" in s and "set Wild_CampDue[i] = 4.5" in s

    # 12. HD 3D model upgrades (88 visually-verified Heroes + 120+ matching Wild/Boss/Mega units)
    assert len(model_upgrades.HERO_UPGRADES) == 88
    all_u = {u.id: u for u in w3u.original + w3u.custom}
    for hid, _dex, _nm, _src, _ref, dst_mdx, _osc, nsc in model_upgrades.HERO_UPGRADES:
        u = all_u[hid]
        assert u.get("umdl") == dst_mdx[:-4] + ".mdl"
        assert abs(float(u.get("usca")) - nsc) < 1e-4
        assert 0.30 <= nsc <= 2.40
    # Broken texture heroes & worst broken/low-poly meshes fixed
    assert all_u["EN0C"].get("umdl") == "PkFx\\HD\\475_Gallade.mdl"
    assert all_u["P4UA"].get("umdl") == "PkFx\\HD\\383_Groudon.mdl"
    assert all_u["E01G"].get("umdl") == "PkFx\\HD\\094_Gengar.mdl"
    assert all_u["E02P"].get("umdl") == "PkFx\\HD\\115_Kangaskhan.mdl"
    assert all_u["E02Z"].get("umdl") == "PkFx\\HD\\112_Rhydon.mdl"
    assert all_u["E035"].get("umdl") == "PkFx\\HD\\141_Kabutops.mdl"
    assert all_u["E03M"].get("umdl") == "PkFx\\HD\\212_Scizor.mdl"
    assert all_u["E01B"].get("umdl") == "PkFx\\HD\\077_Ponyta.mdl"
    assert all_u["P1TA"].get("umdl") == "PkFx\\HD\\250_HoOh.mdl"
    assert all_u["EL00"].get("umdl") == "PkFx\\HD\\378_Regice.mdl"
    assert all_u["E008"].get("umdl") == "PkFx\\HD\\001_Bulbasaur.mdl"
    assert abs(float(all_u["E008"].get("usca")) - 1.15) < 1e-4
    # QA-excluded units remain untouched (never replaced with wrong/shiny/regression models)
    for kept_id in ("PZZA", "E025", "E027", "E021", "E02G", "E02I", "hM0N"):
        assert not (all_u[kept_id].get("umdl") or "").startswith("PkFx\\HD\\")
    # Matching Wild/Boss/Mega Kangaskhan synced
    assert all_u["n01A"].get("umdl") == "PkFx\\HD\\094_Gengar.mdl"
    assert all_u["n00Z"].get("umdl") == "PkFx\\HD\\006_Charizard.mdl"
    assert all_u["hM08"].get("umdl") == "PkFx\\HD\\115_Kangaskhan.mdl"
    # Mega_BaseScale[7] (Gengar) & Mega_Scale[8] (Mega Kangaskhan) synced in JASS
    assert "set Mega_BaseScale[7] = 0.730" in s
    assert "set Mega_Scale[8] = 1.540" in s

    # 13. Melee vs Ranged (Archer) Rework: every checklist Hero matches weapon/range/missile + 3 JASS contact hooks
    checklist = melee_ranged_classifier.parse_checklist()
    assert len(checklist) == 360
    for hid, is_melee in checklist.items():
        u = all_u[hid]
        if is_melee:
            assert u.get("ua1w") == "normal", f"Melee hero {hid} has ua1w={u.get('ua1w')}"
            assert 128 <= int(u.get("ua1r")) <= 175, f"Melee hero {hid} has ua1r={u.get('ua1r')}"
            assert (u.get("ua1m") or "") == "", f"Melee hero {hid} still has missile {u.get('ua1m')}"
        else:
            assert u.get("ua1w") in ("missile", "mbounce"), f"Archer hero {hid} has ua1w={u.get('ua1w')}"
            assert 450 <= int(u.get("ua1r")) <= 600, f"Archer hero {hid} has ua1r={u.get('ua1r')}"
            assert (u.get("ua1m") or "") != "", f"Archer hero {hid} missing missile art"
            assert "lavaspawn" not in (u.get("ua1m") or "").lower(), f"Archer {hid} still uses LavaSpawnMissile"
    # Key spot checks: Zacian/Zekrom/Groudon = Melee; Lunala/Reshiram/Regice/Kyogre = Archer with type missile
    for m_id in ("EL0N", "EL09", "P4UA", "E010"):
        assert all_u[m_id].get("ua1w") == "normal"
    for r_id in ("EL0J", "EL08", "EL00", "P26A"):
        assert all_u[r_id].get("ua1w") == "missile" and int(all_u[r_id].get("ua1r")) >= 500
    assert "LichMissile.mdl" in all_u["EL00"].get("ua1m")
    assert "WaterElementalMissile.mdl" in all_u["P26A"].get("ua1m")
    assert all_u["E04M"].get("ua1w") == "mbounce"  # Starmie keeps mbounce
    # 3 JASS contact hooks patched cleanly
    assert "if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0 then" in s
    assert "if atk and (IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0) then" in s
    assert "Itm_Flag(t, 7) and (IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) or BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 200.0) then" in s

    # 14. Gen 1-4 Full Expansion (+205 species: 100% Gen 1, 100% Gen 2, 100% Gen 3, 100% Gen 4 = 493/493 complete!)
    g14_entries = gen14_expansion.load_species_entries()
    assert len(g14_entries) == 205
    for sp in g14_entries:
        hu = all_u[sp["hero"]]
        wu = all_u[sp["wild"]]
        assert hu.get("umdl") == sp["dst_mdx"][:-4] + ".mdl"
        assert wu.get("umdl") == sp["dst_mdx"][:-4] + ".mdl"
        assert (hu.get("uhab") or "") == ""
        if sp["is_melee"]:
            assert hu.get("ua1w") == "normal" and 128 <= int(hu.get("ua1r")) <= 175
        else:
            assert hu.get("ua1w") == "missile" and 450 <= int(hu.get("ua1r")) <= 600
            assert "lavaspawn" not in (hu.get("ua1m") or "").lower()
    assert "constant integer Wild_PowStride = 1000" in s
    assert 'call ExecuteFunc("G14_Data01")' in s
    assert 'call ExecuteFunc("G14_Wild01")' in s
    assert 'set Leg_Name[Leg_N] = "Lugia"' in s
    assert 'set Leg_Name[Leg_N] = "Manaphy"' in s
    assert 'set Leg_Name[Leg_N] = "Shaymin"' in s
    assert b"[IG00]" in files["Units\\ItemFunc.txt"]
    assert b'"IG00"' in files["Units\\ItemData.slk"]


def test_gen14_assets_isolated_zero_missing_textures():
    g14_files = gen14_expansion.load_g14_assets(compress_blp=False)
    g14_low = {k.lower(): v for k, v in g14_files.items()}
    entries = gen14_expansion.load_species_entries()
    mdx_keys = [k for k in g14_files if k.lower().endswith(".mdx")]
    assert len(mdx_keys) == len(entries)
    for sp in entries:
        assert sp["icon_path"].lower() in g14_low
        assert sp["dis_icon_path"].lower() in g14_low
    for mk in mdx_keys:
        raw = g14_files[mk]
        assert raw[:4] == b"MDLX", f"Invalid MDX header in {mk}"
        for tp in map_optimizer.mdx_textures(raw):
            if tp.startswith(gen14_expansion.BLIZZARD_PREFIXES):
                continue
            assert tp.startswith("pkfx\\g14\\t\\"), f"Unisolated texture {tp} in {mk}"
            assert tp in g14_low, f"Missing texture {tp} referenced by {mk}"
            assert g14_low[tp][:4] in (b"BLP1", b"BLP2"), f"Invalid BLP header in {tp}"


def test_hd_model_assets_isolated_zero_missing_textures():
    hd_files = model_upgrades.load_hd_assets(compress_blp=False)
    hd_low = {k.lower(): v for k, v in hd_files.items()}
    mdx_keys = [k for k in hd_files if k.lower().endswith(".mdx")]
    assert len(mdx_keys) == len(model_upgrades.HERO_UPGRADES) + len(model_upgrades.MEGA_SKIN_UPGRADES)
    for mk in mdx_keys:
        raw = hd_files[mk]
        assert raw[:4] == b"MDLX", f"Invalid MDX header in {mk}"
        for tp in map_optimizer.mdx_textures(raw):
            if tp.startswith(model_upgrades.BLIZZARD_PREFIXES):
                continue
            assert tp.startswith("pkfx\\hd\\t\\"), f"Unisolated texture {tp} in {mk}"
            assert tp in hd_low, f"Missing texture {tp} referenced by {mk}"
            assert hd_low[tp][:4] in (b"BLP1", b"BLP2"), f"Invalid BLP header in {tp}"
