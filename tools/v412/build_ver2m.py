"""Build Pokemon Arena v4.1.2-ver2m:
1. VERTICAL SHOP ALIGNMENT WITH PC CENTER:
   - Battle Shop (nBS0) at (+/-5950.0, +240.0).
   - Paradox Shop (nFS1) at (+/-5950.0, -240.0).
   - Forms a single vertical column along back wall with PC Center (0.0), clearing 100% of the forward courtyard!
2. ACCURATE MOBA TARGET INDICATORS (Quick Attack & Line moves fixed):
   - Only true Area AoE moves (tt == 2) draw ground circle reticles.
   - Line (tt == 3, Quick Attack) and Single Target (tt == 1) moves strip bit 2, relying on clean hero cast range ring.
3. CELEBI BOSS DEATH DROP FIX:
   - Celebi (n035) now drops ISCE (Celebi Soul), Rare Candy, Calcium, Carbos, Iron, and announces [SOUL DROP]!
4. HAUNT LEGEND MID TELEPORT:
   - IL02 (Map Center Teleport) item in shop n030.
   - Step-on Circle of Power at (+/-5120.0, -/+740.0) with label |cff00ffffTo Mid|r warps directly to Center Altar (-128, 16).
5. SOULBOUND EQUIPMENT (120s) & HIGH-STAKES LEGEND DROP:
   - Items held >= 120s become permanently Soulbound to the owning player.
   - Other players picking up soulbound items have them immediately rejected.
   - Dying heroes drop any unbound Legend items (Boss Souls, Tiered Loot, Paradox Boosters, Mega Stones) on the ground!
6. COMMAND CARD ATTRIBUTE & TYPE STATUS ICON AT (Row 1, Col 1):
   - Ability PAXT (Buttonpos = 1, 1).
   - Hover Tooltip shows exact stat scaling formulas (STR/INT/AGI), STAB, and 18-type effectiveness chart.
   - Chat commands -stat and -type for live in-game breakdown.
7. CUSTOM TRANQUIL & WIGHT VFX PACK INTEGRATION:
   - 146 custom models and icons imported from Varioius Spells Effects and Wight Spell Models.
   - Stun Small wired to PAX_Leg_Stun, Shield Buff to barriers, etc.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import slk  # noqa: E402
import objdata  # noqa: E402
import base_layout  # noqa: E402
import starter_moves  # noqa: E402
import move_animations  # noqa: E402
import weather_fx  # noqa: E402
import starters  # noqa: E402
import starters_v412  # noqa: E402
import status_debuffs  # noqa: E402
import smart_creep_ai  # noqa: E402
import paradox_balance  # noqa: E402
import boss_buff  # noqa: E402
import english_locale  # noqa: E402
import pokemon_move_icons  # noqa: E402
import pokemon_item_icons  # noqa: E402
import ver2m_features  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2b.w3x')
NAME = 'v4.1.2-ver2m'

PJASS_PATH = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
COMMON_J = os.path.join(WORK, "analysis", "jass_ref", "common.j")
BLIZZARD_J = os.path.join(WORK, "analysis", "jass_ref", "blizzard.j")


def _v3411_build():
    spec = importlib.util.spec_from_file_location('v3411_build', os.path.join(WORK, 'tools', 'v3411', 'build.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules['v3411_build'] = mod
    spec.loader.exec_module(mod)
    return mod


def verify_jass(script_text: str):
    """Runs pjass syntax verification on the script."""
    if not (os.path.exists(PJASS_PATH) and os.path.exists(COMMON_J) and os.path.exists(BLIZZARD_J)):
        print("[verify_jass] pjass or reference JASS files not found, skipping compile check.")
        return True

    scratch_j = os.path.join(HERE, "temp_ver2m.j")
    with open(scratch_j, "w", encoding="utf-8") as f:
        f.write(script_text)

    try:
        cmd = [PJASS_PATH, COMMON_J, BLIZZARD_J, scratch_j]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            print("[verify_jass] PJASS FAILED with return code %d:" % res.returncode)
            print(res.stdout[:2000])
            print(res.stderr[:2000])
            raise RuntimeError(f"PJASS syntax check failed (return code {res.returncode})")
        print("[verify_jass] PJASS verification SUCCESSFUL! 0 syntax errors.")
        return True
    finally:
        if os.path.exists(scratch_j):
            os.remove(scratch_j)


def build(out, dry):
    print('Loading base map: %s' % BASE_MAP)
    base = mpq.MPQ(BASE_MAP)
    vb = _v3411_build()

    # 1. Patch Script
    print('Reading war3map.j...')
    script = base.read('scripts\\war3map.j').decode('latin-1')
    script = script.replace('\r\r\n', '\r\n').replace('\r\n', '\n')

    print('Applying Upgrade 1: Vertical shop alignment along back wall & clear courtyard...')
    script = base_layout.patch_script(script)

    print('Applying Upgrade 2: Starter move learnsets & Level 1 auto-equip...')
    script = starter_moves.patch_script(script)

    print('Applying Upgrade 3: Cast animations for all Pokemon...')
    script = move_animations.patch_script(script)

    print('Applying weather visual fx patch...')
    script = weather_fx.patch_script(script)

    print('Applying status debuffs and 100 vitamin drink limit patch...')
    script = status_debuffs.patch_script(script)

    print('Applying 33 starters script patch...')
    script = starters_v412.patch_script(script)

    print('Applying Smart Creep AI & 30s Stacking Reinforcements...')
    script = smart_creep_ai.patch_script(script)

    print('Applying Paradox Balance & Quest 3 Permanent 30s reduction on Legend Kill...')
    script = paradox_balance.patch_script(script)

    print('Applying Uniform Boss Buff (x10 HP, x2 ATK, x2 Armor, Infinite Mana, Kit, -50% CD)...')
    script = boss_buff.patch_script(script)

    print('Applying Native MOBA Skill Target Indicator (BlzEnableTargetIndicator)...')
    script = pokemon_move_icons.patch_script(script)

    print('Applying ver2m features (Celebi Soul Drop, Haunt Mid Portal, Soulbound 120s, Drop on Death, PAXT icon)...')
    script = ver2m_features.patch_script(script)

    print('Applying 100% clean authentic English locale patch...')
    script = english_locale.patch_script(script)

    # Update version text
    script = re.sub(r'v4\.1\.2-ver2[a-z]*', NAME, script)
    script = script.replace('\n', '\r\n')

    # Verify script with real pjass.exe compiler
    print('Verifying patched war3map.j with pjass.exe compiler...')
    verify_jass(script)

    # 2. Patch Objects & Items
    print('Patching units, items and abilities...')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    func = base.read('Units\\ItemFunc.txt').decode('utf-8')
    abil = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    buffs = slk.Slk(base.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')

    # Starters units & souls
    starters.unit_objects(w3u, objdata)
    func = starters.wild_objects(w3u, objdata, items, func, vb.set_keys, vb.copy_section)

    # Scale all 10 base shops to uniform sleek 0.20, and Haunt Legend (n030) to 0.65
    print('Scaling down all base shops to uniform 0.20 and Haunt Legend to 0.65 in war3map.w3u...')
    scales = {
        'n00P': 0.58,  # Poke Center
        'n00O': 0.20,  # Poke Mart 1
        'n00N': 0.20,  # Poke Super Mart 1
        'n00Q': 0.20,  # Poke Super Mart 2
        'nIS0': 0.20,  # Item Shop
        'nBS0': 0.20,  # Battle Shop
        'nMS1': 0.20,  # Mega Shop I
        'nMS2': 0.20,  # Mega Shop II
        'nMS3': 0.20,  # Mega Shop III
        'nFS0': 0.20,  # Form Shop
        'nFS1': 0.20,  # Paradox Shop
        'n030': 0.65,  # Haunt Legend NPC
    }
    for sid, sc in scales.items():
        u = w3u.find(sid)
        if u:
            u.set('usca', 1, sc)

    # Distinct Pokémon Shop Icons and Names
    print('Assigning authentic Pokemon icons to Form, Paradox, and Mega shops...')
    shop_customs = {
        'nFS0': ('Form Shop (Deoxys)', 'BTNDeoxys (64 x 64).blp'),
        'nFS1': ('Paradox Shop (Walking Wake)', 'ReplaceableTextures\\CommandButtons\\BTNPokeSuicune.blp'),
        'nMS1': ('Mega Shop I (Charizard X)', 'ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp'),
        'nMS2': ('Mega Shop II (Lucario)', 'ReplaceableTextures\\CommandButtons\\BTNMegaLucario.blp'),
        'nMS3': ('Mega Shop III (Rayquaza)', 'ReplaceableTextures\\CommandButtons\\BTNMegaRayquaza.blp'),
    }
    for sid, (name, icon) in shop_customs.items():
        u = w3u.find(sid)
        if u:
            u.set('unam', 3, name)
            u.set('uico', 3, icon)

    # Update all item icons in ItemFunc.txt to authentic Pokemon portraits & icons
    print('Applying authentic Pokemon portraits to Mega Stones, Form Orbs, Paradox Boosters & Held Items...')
    func = pokemon_item_icons.patch_item_func(func)

    # Paradox items cost kept at original 10,000g as requested
    print('Keeping Paradox items cost at original 10,000g in ItemData.slk...')
    if 'goldcost' in items.name_to_x:
        gx = items.name_to_x['goldcost']
        for itid in ['IM18', 'IM19', 'IM1A', 'IM1B', 'IM1C', 'IM1D', 'IM1E', 'IM1F', 'IM1G', 'IM1H']:
            r = items.find(itid)
            if r:
                r[gx] = '10000'

    # Vitamin stat items: infinite stock in ItemData.slk
    print('Setting infinite stock for Vitamin stat items in ItemData.slk...')
    stock_max_x = items.name_to_x.get('stockMax')
    stock_regen_x = items.name_to_x.get('stockRegen')
    stock_start_x = items.name_to_x.get('stockStart')
    for itid in ['I000', 'I001', 'I002', 'I003', 'I004', 'I005', 'I006']:
        r = items.find(itid)
        if r:
            if stock_max_x:
                r[stock_max_x] = '999'
            if stock_regen_x:
                r[stock_regen_x] = '0'
            if stock_start_x:
                r[stock_start_x] = '999'

    # Status moves & buff icons
    print('Applying status debuffs and buff icons...')
    strings = status_debuffs.patch_objects(abil, buffs, strings)

    # MOBA on-ground target indicators in AbilityData.slk (Only tt == 2 gets bit 2)
    print('Enabling on-ground MOBA AoE reticles (tt == 2 only) in AbilityData.slk...')
    pokemon_move_icons.patch_ability_slk(abil, script)

    # Authentic Pokémon move icons and range/shape indicators for all 378 moves
    print('Applying authentic Pokemon move icons and range/line indicators to all 378 moves...')
    strings = pokemon_move_icons.patch_ability_strings(strings, script, abil)

    # ver2m Object patches: PAXT ability at (1, 1) and IL02 item
    print('Applying ver2m object definitions (PAXT ability at Buttonpos 1,1 and IL02 teleport item)...')
    func, strings = ver2m_features.patch_objects(abil, items, func, strings, w3u)

    # 3. Patch w3i (Keep original 160x160 canvas, update title)
    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(b'v4.1.2-ver2', NAME.encode('latin-1'))

    # 4. Clean war3mapSkin.txt
    skin_raw = base.read('war3mapSkin.txt').decode('latin-1')
    skin_cleaned = re.sub(r'^(ChatFont|EscMenuTextFont|TextTagFont|InfoPanelTextFont|MessageFont|MasterFont|MasterFontBold)=.*?\r?\n',
                          '', skin_raw, flags=re.MULTILINE)

    # 5. Assemble files
    files = {
        'scripts\\war3map.j': script.encode('utf-8'),
        'war3map.w3i': w3i,
        'war3map.w3u': w3u.to_bytes(),
        'war3mapSkin.txt': skin_cleaned.encode('latin-1'),
        'Units\\AbilityData.slk': abil.to_text().encode('latin-1'),
        'Units\\AbilityBuffData.slk': buffs.to_text().encode('latin-1'),
        'Units\\ItemData.slk': items.to_text().encode('latin-1'),
        'Units\\ItemFunc.txt': func.encode('utf-8'),
        'Units\\CampaignAbilityStrings.txt': strings.encode('utf-8'),
    }

    # Starter models, textures, icons from Pokemon World
    print('Loading starter asset files from Pokemon World...')
    have = {n.lower() for n in base.listfile()}
    st_files = starters.files()
    for path, data in st_files.items():
        if path.lower() not in have and path not in files:
            files[path] = data

    # Extra custom move icons at ReplaceableTextures\CommandButtons\
    print('Loading extra custom Pokemon move icons...')
    mv_icons = pokemon_move_icons.extra_icon_files(base)
    for path, data in mv_icons.items():
        if path.lower() not in have and path not in files:
            files[path] = data

    # Custom VFX assets from Tranquil & Wight packs
    print('Loading 146 custom VFX models and icons from Tranquil & Wight packs...')
    vfx_assets = ver2m_features.load_custom_vfx_files()
    for path, data in vfx_assets.items():
        if path.lower() not in have and path not in files:
            files[path] = data

    print('Total files to package: %d' % len(files))
    if dry:
        print('Dry run: completed successfully without writing.')
        return

    if os.path.exists(out):
        print('Removing existing file: %s' % out)
        os.remove(out)

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    print('Saving map to: %s (hash_size=%d) ...' % (out, hsize))
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2m.w3x'))
    args = ap.parse_args()
    build(args.out, args.dry_run)
