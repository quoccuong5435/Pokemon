"""Build Pokemon Arena v4.1.2-ver2o:
1. FIXED SHOP OVERLAP AT POKÉ CENTER (2-Row 10-Shop Layout, Zero Overlap):
   - Top Row (Y = 544.0, Facing 270.0 South, Spacing 150, Scale 0.20):
     * Poké Mart 1 (n00O): +/-5950.0
     * Poké Mart 2 (n00N): +/-5800.0
     * Poké Mart 3 (n00Q): +/-5650.0
     * Item Shop (nIS0):   +/-5500.0
     * Battle Shop (nBS0): +/-5350.0
   - Bottom Row (Y = -544.0, Facing 90.0 North, Spacing 150, Scale 0.20):
     * Mega Shop I (nMS1):   +/-5950.0
     * Mega Shop II (nMS2):  +/-5800.0
     * Mega Shop III (nMS3): +/-5650.0
     * Form Shop (nFS0):     +/-5500.0
     * Paradox Shop (nFS1):  +/-5350.0
   - Poké Center (n00P at +/-5952.0, 0.0) has 544+ units of clearance with 0 overlapping buildings.
   - Haunt Legend Mid Teleport Portal placed cleanly at (sx * 5120.0, sx * 760.0).
2. 100% UNIFORM & SYNCHRONIZED SQUARE MOVE ICONS:
   - Eliminates all flat round circular type badges (BTNPkmn*.blp) from move abilities.
   - All 388 moves across all 5 slots (AV, AW, AY, AZ, AK) use 100% uniform 64x64 square bordered spell icons:
     signature custom Pokémon move icons, Wight icons, and varied thematic WC3 spell icons.
3. DEFAULT WARCRAFT III REFORGED FONT COMPATIBILITY:
   - war3mapSkin.txt stripped of all font overrides; no embedded font files.
   - All in-game dialogs, alerts, and tooltips in clean English so default Reforged font renders 0 broken characters.
4. INCLUDES ALL VER2M & VER2N SYSTEMS:
   - Ability Patch (10,000g) with Yes/No confirmation dialog, Min 55:00 Mega Rayquaza world boss,
     Contested Gym PvPvE & Anti-Smurf, Tall Grass stealth, 240s Weather cycle, Soulbound 120s,
     Celebi Soul drop, PAXT type & stat icon, and Dota 2 / Tranquil / Wight VFX.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import slk  # noqa: E402
import objdata  # noqa: E402
import pokemon_move_icons  # noqa: E402
import ver2n_features  # noqa: E402
import ver2n_dota2_vfx  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2m.w3x')
ORIG_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2b.w3x')
NAME = 'v4.1.2-ver2o'

OLD_VER2M_PLACE_SHOPS = '''function Ext_PlaceShops takes nothing returns nothing
    local integer side = 0
    local real sx = 0.0
    local real x = 0.0
    local real face = 0.0
    local unit shop = null
    loop
        exitwhen side >= 2
        set sx = -1.0
        set face = 0.0
        if side == 1 then
            set sx = 1.0
            set face = 180.0
        endif
        // Top row (Y = 544.0, Facing South 270.0): Item Shop (nIS0 at 5440.0)
        set x = sx * 5440.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)
        call PAX_MapLabel("|cffffcc00Item Shop|r", x - 38.0, 544.0, 165.0)

        // Bottom row (Y = -544.0, Facing North 90.0): Form Shop (nFS0 at 5440.0)
        set x = sx * 5440.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)
        if shop != null then
            call SetUnitVertexColor(shop, 255, 215, 80, 255)
            call PAX_MapLabel("|cffffd750Form Shop|r", x - 42.0, -544.0, 165.0)
        endif

        // Vertical column along back wall (X = sx * 5950.0, aligned with PC Center at Y = 0.0):
        // Battle Shop at Y = +240.0 (Facing lawn)
        set x = sx * 5950.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 240.0, face)
        call PAX_MapLabel("|cffffcc00Battle Shop|r", x - 42.0, 240.0, 165.0)

        // Paradox Shop at Y = -240.0 (Facing lawn)
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -240.0, face)
        if shop != null then
            call SetUnitVertexColor(shop, 170, 130, 255, 255)
            call PAX_MapLabel("|cffd899ffParadox|r", x - 34.0, -240.0, 165.0)
        endif

        // Haunt Legend Mid Teleport Portal (Circle of Power next to Haunt Legend at Y = -sx * 740.0)
        call AddSpecialEffect("buildings\\\\other\\\\CircleOfPower\\\\CircleOfPower.mdl", sx * 5120.0, -sx * 740.0)
        call PAX_MapLabel("|cff00ffffTo Mid|r", sx * 5120.0 - 24.0, -sx * 740.0, 165.0)

        set side = side + 1
    endloop
    set shop = null
endfunction'''

NEW_VER2O_PLACE_SHOPS = '''function Ext_PlaceShops takes nothing returns nothing
    local integer side = 0
    local real sx = 0.0
    local real x = 0.0
    local unit shop = null
    loop
        exitwhen side >= 2
        set sx = -1.0
        if side == 1 then
            set sx = 1.0
        endif
        // Top row (Y = 544.0, Facing South 270.0):
        // Mart 1 (5950), Mart 2 (5800), Mart 3 (5650), Item Shop (5500), Battle Shop (5350)
        set x = sx * 5500.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)
        call PAX_MapLabel("|cffffcc00Item Shop|r", x - 38.0, 544.0, 165.0)

        set x = sx * 5350.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 544.0, 270.0)
        call PAX_MapLabel("|cffffcc00Battle Shop|r", x - 42.0, 544.0, 165.0)

        // Bottom row (Y = -544.0, Facing North 90.0):
        // Mega 1 (5950), Mega 2 (5800), Mega 3 (5650), Form Shop (5500), Paradox Shop (5350)
        set x = sx * 5500.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)
        if shop != null then
            call SetUnitVertexColor(shop, 255, 215, 80, 255)
            call PAX_MapLabel("|cffffd750Form Shop|r", x - 42.0, -544.0, 165.0)
        endif

        set x = sx * 5350.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -544.0, 90.0)
        if shop != null then
            call SetUnitVertexColor(shop, 170, 130, 255, 255)
            call PAX_MapLabel("|cffd899ffParadox|r", x - 34.0, -544.0, 165.0)
        endif

        // Haunt Legend Mid Teleport Portal (Circle of Power next to Haunt Legend at Y = sx * 760.0)
        call AddSpecialEffect("buildings\\\\other\\\\CircleOfPower\\\\CircleOfPower.mdl", sx * 5120.0, sx * 760.0)
        call PAX_MapLabel("|cff00ffffTo Mid|r", sx * 5120.0 - 24.0, sx * 760.0, 165.0)

        set side = side + 1
    endloop
    set shop = null
endfunction'''


def build_data():
    """Builds and returns (base, files, script, abil, buffs, items, func, strings, w3u) in memory."""
    base = mpq.MPQ(BASE_MAP)
    orig = mpq.MPQ(ORIG_MAP)

    script = base.read('scripts\\war3map.j').decode('utf-8')
    script = script.replace('\r\r\n', '\r\n').replace('\r\n', '\n')

    if OLD_VER2M_PLACE_SHOPS not in script:
        raise SystemExit("build_ver2o: OLD_VER2M_PLACE_SHOPS anchor not found in war3map.j")
    script = script.replace(OLD_VER2M_PLACE_SHOPS, NEW_VER2O_PLACE_SHOPS, 1)

    # Disable instant PAX_HauntPortalTick so Ver2n_Tick's 2.0s channel + 30s CD handles the Mid Portal cleanly
    script = script.replace("    call PAX_HauntPortalTick()\n", "")

    # Apply ver2n JASS Patches (in 100% clean English for default Warcraft III Reforged font)
    script = ver2n_features.patch_jass(script)

    script = re.sub(r'v4\.1\.2-ver2[a-z]*', NAME, script)
    script = script.replace('\n', '\r\n')

    abil = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    buffs = slk.Slk(base.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    func = base.read('Units\\ItemFunc.txt').decode('utf-8')
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    orig_strings = orig.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))

    # Apply ver2n Object Patches (IMHA, IB0C, IB0D, nIS0 cleanup, uniform 0.20 shop scale)
    func, strings = ver2n_features.patch_objects(abil, items, func, strings, w3u)

    # Apply 100% uniform & synchronized square move icons across all 388 moves (AV, AW, AY, AZ, AK)
    strings = pokemon_move_icons.patch_ability_strings(strings, script, abil, orig_strings_txt=orig_strings)

    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(b'v4.1.2-ver2m', NAME.encode('latin-1'))
    w3i = w3i.replace(b'ver2m', b'ver2o')

    skin_raw = base.read('war3mapSkin.txt').decode('latin-1')
    skin_cleaned = re.sub(r'^(ChatFont|EscMenuTextFont|TextTagFont|InfoPanelTextFont|MessageFont|MasterFont|MasterFontBold)=.*?\r?\n',
                          '', skin_raw, flags=re.MULTILINE)

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

    have = {n.lower() for n in base.listfile()}
    dota2_assets = ver2n_dota2_vfx.load_dota2_vfx_assets()
    for path, data in dota2_assets.items():
        if path.lower() not in have and path not in files:
            files[path] = data

    return base, files, script, abil, buffs, items, func, strings, w3u


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit(f"Output file already exists (refusing to overwrite per GEMINI.md): {out}")

    base, files, _script, *_ = build_data()
    print('Total files to package for %s: %d' % (NAME, len(files)))
    if dry:
        for k in sorted(files)[:15]:
            print('  [dry-run]', k)
        print('Dry run completed successfully without writing.')
        return

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=os.path.join(MAPS, f'Pokemon Arena {NAME}.w3x'))
    args = ap.parse_args()
    build(args.out, args.dry_run)
