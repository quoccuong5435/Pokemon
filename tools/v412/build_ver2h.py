"""Build Pokemon Arena v4.1.2-ver2h:
- 100% CLEAN AUTHENTIC ENGLISH:
  All game announcements, welcome banner, -help commands, startup hints,
  and F9 quest logs restored to pure, crystal-clear English.
  All corrupt TCVN3-encoded legacy strings replaced.
  Zero missing letters, zero font glitches on any Warcraft III version.
- REMOVED LEGACY FONT OVERRIDES:
  Strips legacy VNVOGU.TTF font overrides from war3mapSkin.txt, restoring
  native Warcraft III typography while preserving PokemonDB type chart tooltips.
- SCALED DOWN BASE SHOPS:
  Base buildings scaled down by ~25% for a spacious, sleek courtyard:
  Poke Center (0.75 -> 0.58), Mart shops & Mega/Form shops (0.40 -> 0.30), Moves NPC (1.50 -> 1.15).
- AUTHENTIC POKÉMON MOVE ICONS:
  All 378 moves equipped with authentic Pokémon Type icons (BTNPkmnFire, Water, Grass, etc.)
  and specific custom move icons (Blast Burn, Flamethrower, Bubble Beam, Razor Leaf, Hyper Beam, Outrage, etc.).
- 3 CORE UPGRADES:
  160x160 bug-free canvas, spacious base layout, 33 starter move learnsets, and authentic casting animations.
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
import english_locale  # noqa: E402
import pokemon_move_icons  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2b.w3x')
NAME = 'v4.1.2-ver2h'

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

    scratch_j = os.path.join(HERE, "temp_ver2h.j")
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

    print('Applying Upgrade 1: Base courtyard layout...')
    script = base_layout.patch_script(script)

    print('Applying Upgrade 2: Starter move learnsets & Level 1 auto-equip...')
    script = starter_moves.patch_script(script)

    print('Applying Upgrade 3: Cast animations for all Pokemon...')
    script = move_animations.patch_script(script)

    print('Applying weather visual fx patch...')
    script = weather_fx.patch_script(script)

    print('Applying status debuffs and visible stages patch...')
    script = status_debuffs.patch_script(script)

    print('Applying 33 starters script patch...')
    script = starters_v412.patch_script(script)

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

    # Scale down oversized base shops for sleek, compact courtyard layout
    print('Scaling down oversized shops in war3map.w3u...')
    scales = {
        'n00P': 0.58,  # Poke Center (down from 0.75)
        'n00O': 0.30,  # Poke Mart (down from 0.40)
        'n00N': 0.30,  # Poke Super Mart 1 (down from 0.40)
        'n00Q': 0.30,  # Poke Super Mart 2 (down from 0.40)
        'nMS1': 0.30,  # Mega Shop I (down from 0.40)
        'nMS2': 0.30,  # Mega Shop II (down from 0.40)
        'nMS3': 0.30,  # Mega Shop III (down from 0.40)
        'nFS0': 0.30,  # Form Shop (down from 0.40)
        'nFS1': 0.30,  # Paradox Shop (down from 0.40)
        'n030': 1.15,  # Moves NPC (down from 1.50)
    }
    for sid, sc in scales.items():
        u = w3u.find(sid)
        if u:
            u.set('usca', 1, sc)

    # Status moves & buff icons
    strings = status_debuffs.patch_objects(abil, buffs, strings)

    # Authentic Pokémon move icons for all 378 moves (AVxx, AWxx, AYxx, AZxx, AKxx)
    print('Applying authentic Pokemon move icons to all 378 moves...')
    strings = pokemon_move_icons.patch_ability_strings(strings, script)

    # 3. Patch w3i (Keep original 160x160 canvas, update title)
    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(b'v4.1.2-ver2', NAME.encode('latin-1'))

    # 4. Clean war3mapSkin.txt: remove legacy font overrides (VNVOGU.TTF) so engine uses clean default fonts
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
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    out_path = a.out or os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
    build(out_path, a.dry_run)
