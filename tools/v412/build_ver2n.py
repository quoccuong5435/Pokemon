"""Build Pokemon Arena v4.1.2-ver2n:
1. ABILITY PATCH (10,000g) WITH YES/NO CONFIRMATION DIALOG:
   - Purchased from Item Shop (or clicked in inventory).
   - Prompts native Warcraft III Dialog with Pokemon Name, PokeAPI Hidden Ability Name, and detailed description.
   - Buttons: [ Dong Y / Yes (10.000g) ] vs [ Huy Bo / No (Hoan Tien) ].
   - If Yes: permanently unlocks Hidden Ability, consumes item, plays holy awakening VFX.
   - If No: cancels, refunds 10,000 Gold immediately, removes item.
2. MINUTE 55:00 MEGA RAYQUAZA AWAKENED WORLD BOSS:
   - Spawns at 55:00 (3300s) at Center Altar (-128, 16) with 80,000 HP, 35 Armor.
   - 5-Minute Despawn Timer: despawns cleanly at 60:00 (3600s) if not killed.
   - Killing Rayquaza grants the killer team the PERMANENT DRAGON ASCENT BUFF (+25% All Stats,
     +20% MS, 2% HP/Mana per second, lightning strike on attack) + 2,000 Gold per teammate.
   - Master Ball completely removed.
3. CONTESTED GYM PVPVE & ANTI-SMURF:
   - Gym Boss is 100% immune to damage from non-challengers (BlzSetEventDamage(0.0)).
   - Players who have already passed Gym K (Badge_Has == true) are strictly barred from entering (teleported out).
   - Contenders on same Gym level and allies can enter to fight PvP.
4. TALL GRASS BUSHES (BUI CO AN NAP):
   - 6 strategic jungle/river bush zones grant Invisibility after 1.5s still; broken on attack/cast.
5. DYNAMIC INTERACTIVE WEATHER:
   - 240s cycle (Sun, Rain, Sandstorm, Hail) altering elemental damage and triggering weather abilities.
6. SHOP DUPLICATE CLEANUP & TELEPORT FIXES:
   - Redundant Escape Rope & Mega Ring removed from nIS0; replaced with IMHA, IB0C, IB0D.
   - Shops scaled to 0.16 at Y = +/-380; Portal moved to Y = -/+760 with 2s channel + 30s CD.
   - IL02 shop item button pos = (1, 2) with BTNScrollUber.blp and stock = 1 (removes '943').
7. DOTA 2 VFX & ICON SYNC:
   - 92 MDX models and 259 BLP textures loaded into MPQ archive.
   - 378 move icons synchronized.
   - MOBA targeting reticles active.
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import slk  # noqa: E402
import objdata  # noqa: E402
import ver2n_features  # noqa: E402
import ver2n_dota2_vfx  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2m.w3x')
NAME = 'v4.1.2-ver2n'
OUT_MAP = os.path.join(MAPS, f'Pokemon Arena {NAME}.w3x')

PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')


def build():
    print(f"=== BUILDING POKEMON ARENA {NAME} ===")
    print(f"Base map: {BASE_MAP}")
    base = mpq.MPQ(BASE_MAP)

    # 1. Read files from base map
    print("Reading base archive files...")
    script = base.read('scripts\\war3map.j').decode('utf-8')
    abil = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    buffs = slk.Slk(base.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    func = base.read('Units\\ItemFunc.txt').decode('latin-1')
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))

    # 2. Apply ver2n Object Patches
    print("Applying ver2n object patches (IMHA, IB0C, IB0D, nIS0 cleanup, shop scales)...")
    func, strings = ver2n_features.patch_objects(abil, items, func, strings, w3u)

    # 3. Apply ver2n JASS Patches
    print("Applying ver2n JASS patches (Ability Patch Yes/No dialog, Min 55 Rayquaza, Contested Gym, Tall Grass, Weather)...")
    script = ver2n_features.patch_jass(script)

    # 4. Patch w3i
    print("Patching war3map.w3i...")
    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(b'v4.1.2-ver2m', NAME.encode('latin-1'))
    w3i = w3i.replace(b'ver2m', b'ver2n')

    # 5. Assemble files
    files = {
        'scripts\\war3map.j': script.encode('utf-8'),
        'war3map.w3i': w3i,
        'war3map.w3u': w3u.to_bytes(),
        'Units\\AbilityData.slk': abil.to_text().encode('latin-1'),
        'Units\\AbilityBuffData.slk': buffs.to_text().encode('latin-1'),
        'Units\\ItemData.slk': items.to_text().encode('latin-1'),
        'Units\\ItemFunc.txt': func.encode('utf-8'),
        'Units\\CampaignAbilityStrings.txt': strings.encode('utf-8'),
    }

    # 6. Load Dota 2 VFX assets
    print("Loading 92 MDX models and 259 BLP textures from Dota 2 VFX pack...")
    dota2_assets = ver2n_dota2_vfx.load_dota2_vfx_assets()
    have = {n.lower() for n in base.listfile()}
    added_dota2 = 0
    for path, data in dota2_assets.items():
        if path.lower() not in have and path not in files:
            files[path] = data
            added_dota2 += 1
    print(f"Added {added_dota2} new Dota 2 assets into files dictionary.")

    # 7. Write to output map
    if os.path.exists(OUT_MAP):
        print(f"Removing old build: {OUT_MAP}")
        os.remove(OUT_MAP)

    print(f"Saving new map: {OUT_MAP}...")
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    print(f"Writing archive (hash_size={hsize})...")
    base.save_with(OUT_MAP, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print(f"Map saved successfully! Size: {os.path.getsize(OUT_MAP):,} bytes")

    # 8. Run PJASS Syntax Check
    if os.path.exists(PJASS):
        print("Running PJASS syntax verification...")
        tmp_script = os.path.join(REF, '_tmp_ver2n_war3map.j')
        with open(tmp_script, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp_script],
                           capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().replace('\r', '')
        lines = [l for l in out.split('\n') if l.strip()]
        print(f"PJASS Output ({len(lines)} lines):")
        for l in lines[:15]:
            print("  ", l)
        if r.returncode != 0:
            print("WARNING: PJASS reported errors!")
        else:
            print("SUCCESS: PJASS passed with 0 errors!")


if __name__ == '__main__':
    build()
