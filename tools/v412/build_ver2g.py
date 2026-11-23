"""Build Pokemon Arena v4.1.2-ver2g:
- TIENG VIET CO DAU CHUAN (Vietnamese WITH ACCENTS / DIACRITICS) for selected parts:
  1. Main announcements, welcome banner, -help guide, startup hints
  2. Move descriptions (Mv_Text: sát thương, hiệu ứng, hệ, uy lực)
  3. Item tooltips (bình máu, trang bị, bùa Charm)
  4. In-game event alerts (Altar, Wanted, Gyarados, Solo 1v1, League Champion)
  Strictly preserving English Pokemon names, Move names, item proper names, and chat commands.
- EMBEDDED UNICODE FONT & SKIN:
  Embeds war3mapSkin.txt and Fonts\\FRIZQT__.ttf into the map archive so all clients display diacritics cleanly.
- SCALED DOWN BASE SHOPS:
  Reduces oversized base buildings (~25% smaller):
  Poke Center (0.75 -> 0.58), Mart shops & Mega/Form shops (0.40 -> 0.30), Moves NPC (1.50 -> 1.15).
- AUTHENTIC POKEMON MOVE ICONS:
  All 378 moves equipped with authentic Pokemon Type icons (BTNPkmnFire, Water, Grass, etc.)
  and specific custom move icons (Blast Burn, Flamethrower, Bubble Beam, Razor Leaf, etc.).
- 3 CORE UPGRADES:
  160x160 canvas, spacious base layout, 33 starter move learnsets, and authentic casting animations.
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
import localize_vi_accented  # noqa: E402
import pokemon_move_icons  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2b.w3x')
NAME = 'v4.1.2-ver2g'

PJASS_PATH = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
COMMON_J = os.path.join(WORK, "analysis", "jass_ref", "common.j")
BLIZZARD_J = os.path.join(WORK, "analysis", "jass_ref", "blizzard.j")
FONT_SRC = r"C:\Windows\Fonts\arial.ttf"


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

    scratch_j = os.path.join(HERE, "temp_ver2g.j")
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

    print('Applying Vietnamese ACCENTED localization patch (có dấu chuẩn)...')
    script = localize_vi_accented.patch_script(script)

    # Update version text
    script = re.sub(r'v4\.1\.2-ver2[a-z]*', NAME, script)
    script = script.replace('v4.1.2-ver2g: PvP & Legend Balance', 'v4.1.2-ver2g: Tiếng Việt Có Dấu, PvP & Cân Bằng Legend')
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

    # Item tooltips in accented Vietnamese
    func = localize_vi_accented.patch_strings(items, func, strings)

    # 3. Patch w3i (Keep original 160x160 canvas, update title)
    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(b'v4.1.2-ver2', NAME.encode('latin-1'))

    # 4. CustomSkin definition for embedded font support
    skin_txt = (
        "[CustomSkin]\r\n"
        "MasterFont=Fonts\\FRIZQT__.ttf\r\n"
        "MasterFontBold=Fonts\\FRIZQT__.ttf\r\n"
        "MessageFont=Fonts\\FRIZQT__.ttf\r\n"
        "ChatFont=Fonts\\FRIZQT__.ttf\r\n"
        "EscMenuTextFont=Fonts\\FRIZQT__.ttf\r\n"
        "InfoPanelTextFont=Fonts\\FRIZQT__.ttf\r\n"
    )

    # 5. Assemble files
    files = {
        'scripts\\war3map.j': script.encode('utf-8'),
        'war3map.w3i': w3i,
        'war3map.w3u': w3u.to_bytes(),
        'war3mapSkin.txt': skin_txt.encode('latin-1'),
        'Units\\AbilityData.slk': abil.to_text().encode('latin-1'),
        'Units\\AbilityBuffData.slk': buffs.to_text().encode('latin-1'),
        'Units\\ItemData.slk': items.to_text().encode('latin-1'),
        'Units\\ItemFunc.txt': func.encode('utf-8'),
        'Units\\CampaignAbilityStrings.txt': strings.encode('utf-8'),
    }

    # Embed Vietnamese Unicode font directly into map archive
    if os.path.exists(FONT_SRC):
        print('Embedding Unicode font from %s into map archive...' % FONT_SRC)
        with open(FONT_SRC, 'rb') as f:
            font_bytes = f.read()
        files['Fonts\\FRIZQT__.ttf'] = font_bytes

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
