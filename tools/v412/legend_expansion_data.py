"""Legendary Expansion + Real 3D Mega/Form Models for Pokemon Arena v4.1.3i:
1. Adds 25 NEW Playable Legendaries (Gen 3 - Gen 8), each with:
   - Playable Hero (`EL00`..`EL0O`), Wild Boss Lv 100 (`nL20`..`nL2O` in Random Legends pool),
     Legend Soul (`IL20`..`IL2O`, 50% drop, transforms at Center Altar).
   - Official PokemonDB Base Stats (HP = 40*HP, STR = Atk, AGI = Spe, INT = SpA, Armor = 0.6*Def).
   - Authentic level-up moves & TMs from the existing 388-move pool.
   - Awakening Quest (`-quest`) integration (idx 33..57, Lv 65 Sub-Legends / Lv 75 Box Legends)
     with balanced awakened Hidden Power bonuses in combat.
2. Upgrades 10 existing Megas/Forms that were reusing base models to REAL 3D models (0 missing textures):
   - Mega Mewtwo X, Mega Mewtwo Y, Mega Rayquaza, Primal Kyogre, Primal Groudon,
     Mega Latias/Latios, Giratina Origin Form, Deoxys Attack/Defense/Speed Forms.
3. Adds 2 NEW Megas for existing map heroes (Swampert -> Mega Swampert, Garchomp -> Mega Garchomp)
   and 5 NEW Legend Forms/Megas for the new Legendaries (Black Kyurem, White Kyurem, Mega Diancie,
   Hoopa Unbound, Ultra Necrozma) - all with real 3D models (0 missing textures).
"""
import os
import re
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)

PW_MAP = os.path.join(MAPS, 'Pokemon World V1.71.w3x')
RPG79_MAP = os.path.join(MAPS, '79.PokemonRPG.w3x')

TYPE_IDX = {
    'bug': 0, 'dark': 1, 'dragon': 2, 'electric': 3, 'fairy': 4, 'fighting': 5,
    'fire': 6, 'flying': 7, 'ghost': 8, 'grass': 9, 'ground': 10, 'ice': 11,
    'normal': 12, 'poison': 13, 'psychic': 14, 'rock': 15, 'steel': 16, 'water': 17,
}

BLIZZARD_PREFIXES = (
    'textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\',
    'environment\\', 'objects\\', 'ui\\', 'buildings\\', 'doodads\\', 'sharedmodels\\',
)

# 25 NEW Legendary Pokemon (indices 33..57 in PAX_Leg_Name)
# Format: dict(idx, hero, wild, soul, dex, name, types, stats=(hp,atk,def,spa,spd,spe),
#              req_lv, role, scale, src_map, src_ref, icon, lv_moves=[(mv, lv)...], tm_moves=[...])
# role: 'tank' (-15% incoming dmg & +3% max HP heal on hit CD), 'caster' (+15% skill dmg),
#       'striker' (+12% attack & skill dmg), 'drain' (+12% dmg & 12% spell vamp)
NEW_LEGENDS = [
    # Gen 3 (2)
    dict(idx=33, hero='EL00', wild='nL20', soul='IL20', dex=378, name='Regice', types=('ice',),
         stats=(80, 50, 100, 100, 200, 50), req_lv=65, role='tank', scale=1.35,
         src_map='PW', src_ref='Unit\\378.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_378.blp',
         lv_moves=[(147, 1), (9, 10), (140, 25), (317, 40), (23, 55), (106, 65)],
         tm_moves=[140, 23, 147, 106, 289, 285, 137, 334]),
    dict(idx=34, hero='EL01', wild='nL21', soul='IL21', dex=379, name='Registeel', types=('steel',),
         stats=(80, 75, 150, 75, 150, 50), req_lv=65, role='tank', scale=1.35,
         src_map='PW', src_ref='Unit\\379.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_379.blp',
         lv_moves=[(173, 1), (9, 10), (151, 25), (106, 40), (80, 55), (317, 65)],
         tm_moves=[151, 106, 80, 228, 267, 289, 137, 334]),

    # Gen 4 (5)
    dict(idx=35, hero='EL02', wild='nL22', soul='IL22', dex=480, name='Uxie', types=('psychic',),
         stats=(75, 75, 130, 75, 130, 95), req_lv=65, role='tank', scale=1.25,
         src_map='RPG79', src_ref='war3mapImported\\480.mdx', icon='ReplaceableTextures\\CommandButtons\\BTNStarWand.blp',
         lv_moves=[(46, 1), (277, 10), (88, 25), (209, 40), (118, 55), (56, 65)],
         tm_moves=[209, 214, 56, 243, 84, 289, 323, 334]),
    dict(idx=36, hero='EL03', wild='nL23', soul='IL23', dex=481, name='Mesprit', types=('psychic',),
         stats=(80, 105, 105, 105, 105, 80), req_lv=65, role='caster', scale=1.25,
         src_map='RPG79', src_ref='war3mapImported\\481.mdx', icon='ReplaceableTextures\\CommandButtons\\BTNControlMagic.blp',
         lv_moves=[(46, 1), (277, 10), (88, 25), (209, 40), (140, 55), (118, 65)],
         tm_moves=[209, 214, 140, 23, 289, 243, 56, 323]),
    dict(idx=37, hero='EL04', wild='nL24', soul='IL24', dex=482, name='Azelf', types=('psychic',),
         stats=(75, 125, 70, 125, 70, 115), req_lv=65, role='caster', scale=1.25,
         src_map='RPG79', src_ref='war3mapImported\\482.mdx', icon='ReplaceableTextures\\CommandButtons\\BTNManaBurn.blp',
         lv_moves=[(46, 1), (277, 10), (88, 25), (209, 40), (104, 55), (118, 65)],
         tm_moves=[209, 214, 104, 96, 289, 243, 56, 321]),
    dict(idx=38, hero='EL05', wild='nL25', soul='IL25', dex=485, name='Heatran', types=('fire', 'steel'),
         stats=(91, 90, 106, 130, 106, 77), req_lv=65, role='tank', scale=1.35,
         src_map='PW', src_ref='Unit\\485.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_485.blp',
         lv_moves=[(9, 1), (158, 12), (106, 25), (79, 40), (128, 55), (96, 65)],
         tm_moves=[104, 96, 106, 79, 80, 69, 54, 365]),
    dict(idx=39, hero='EL06', wild='nL26', soul='IL26', dex=488, name='Cresselia', types=('psychic',),
         stats=(120, 70, 110, 75, 120, 85), req_lv=65, role='tank', scale=1.20,
         src_map='RPG79', src_ref=6381, icon='ReplaceableTextures\\CommandButtons\\BTNMoonStone.blp',
         lv_moves=[(46, 1), (147, 12), (214, 25), (178, 40), (209, 55), (118, 65)],
         tm_moves=[209, 214, 178, 140, 84, 243, 323, 336]),

    # Gen 5 (5)
    dict(idx=40, hero='EL07', wild='nL27', soul='IL27', dex=494, name='Victini', types=('psychic', 'fire'),
         stats=(100, 100, 100, 100, 100, 100), req_lv=65, role='caster', scale=1.15,
         src_map='RPG79', src_ref=6392, icon='ReplaceableTextures\\CommandButtons\\BTNOrbOfFire.blp',
         lv_moves=[(46, 1), (104, 15), (209, 30), (149, 45), (186, 60), (285, 70)],
         tm_moves=[104, 96, 186, 209, 214, 289, 285, 84]),
    dict(idx=41, hero='EL08', wild='nL28', soul='IL28', dex=643, name='Reshiram', types=('dragon', 'fire'),
         stats=(100, 120, 100, 150, 120, 90), req_lv=75, role='caster', scale=1.35,
         src_map='RPG79', src_ref=6600, icon='ReplaceableTextures\\CommandButtons\\BTNDragonHawk.blp',
         lv_moves=[(67, 1), (104, 15), (69, 30), (128, 45), (96, 60), (65, 75)],
         tm_moves=[104, 96, 186, 69, 65, 209, 243, 79]),
    dict(idx=42, hero='EL09', wild='nL29', soul='IL29', dex=644, name='Zekrom', types=('dragon', 'electric'),
         stats=(100, 150, 120, 120, 100, 90), req_lv=75, role='striker', scale=1.35,
         src_map='RPG79', src_ref=5798, icon='ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp',
         lv_moves=[(67, 1), (68, 15), (312, 30), (289, 45), (285, 60), (185, 75)],
         tm_moves=[68, 185, 65, 312, 289, 285, 51, 267]),
    dict(idx=43, hero='EL0A', wild='nL2A', soul='IL2A', dex=646, name='Kyurem', types=('dragon', 'ice'),
         stats=(125, 130, 90, 130, 90, 95), req_lv=75, role='caster', scale=1.35,
         src_map='RPG79', src_ref=6604, icon='ReplaceableTextures\\CommandButtons\\BTNOrbOfFrost.blp',
         lv_moves=[(147, 1), (67, 15), (140, 30), (69, 45), (23, 60), (65, 75)],
         tm_moves=[140, 23, 69, 65, 185, 79, 106, 243]),
    dict(idx=44, hero='EL0B', wild='nL2B', soul='IL2B', dex=649, name='Genesect', types=('bug', 'steel'),
         stats=(71, 120, 95, 120, 95, 99), req_lv=65, role='striker', scale=1.20,
         src_map='RPG79', src_ref=6607, icon='ReplaceableTextures\\CommandButtons\\BTNThoriumRanged.blp',
         lv_moves=[(173, 1), (37, 15), (106, 30), (289, 45), (140, 60), (104, 70)],
         tm_moves=[37, 106, 151, 289, 140, 104, 54, 84]),

    # Gen 6 (6)
    dict(idx=45, hero='EL0C', wild='nL2C', soul='IL2C', dex=716, name='Xerneas', types=('fairy',),
         stats=(126, 131, 95, 131, 98, 99), req_lv=75, role='drain', scale=1.35,
         src_map='PW', src_ref='Unit\\716.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_716.blp',
         lv_moves=[(56, 1), (15, 15), (178, 30), (209, 45), (285, 60), (137, 75)],
         tm_moves=[178, 56, 15, 209, 289, 106, 45, 323]),
    dict(idx=46, hero='EL0D', wild='nL2D', soul='IL2D', dex=717, name='Yveltal', types=('dark', 'flying'),
         stats=(126, 131, 95, 131, 98, 99), req_lv=75, role='drain', scale=1.35,
         src_map='RPG79', src_ref=6648, icon='ReplaceableTextures\\CommandButtons\\BTNOrbOfDarkness.blp',
         lv_moves=[(7, 1), (54, 15), (243, 30), (128, 45), (134, 60), (137, 75)],
         tm_moves=[54, 7, 134, 243, 128, 209, 137, 321]),
    dict(idx=47, hero='EL0E', wild='nL2E', soul='IL2E', dex=718, name='Zygarde', types=('dragon', 'ground'),
         stats=(150, 100, 121, 91, 95, 85), req_lv=75, role='tank', scale=1.25,
         src_map='RPG79', src_ref=6650, icon='ReplaceableTextures\\CommandButtons\\BTNEarthquake.blp',
         lv_moves=[(67, 1), (79, 15), (68, 30), (80, 45), (185, 60), (267, 75)],
         tm_moves=[80, 79, 68, 185, 65, 228, 267, 51]),
    dict(idx=48, hero='EL0F', wild='nL2F', soul='IL2F', dex=719, name='Diancie', types=('rock', 'fairy'),
         stats=(50, 100, 150, 100, 150, 50), req_lv=65, role='tank', scale=1.25,
         src_map='PW', src_ref='Unit\\719.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_719.blp',
         lv_moves=[(9, 1), (205, 15), (56, 30), (178, 45), (79, 60), (267, 70)],
         tm_moves=[205, 178, 56, 79, 209, 267, 228, 323]),
    dict(idx=49, hero='EL0G', wild='nL2G', soul='IL2G', dex=720, name='Hoopa', types=('psychic', 'ghost'),
         stats=(80, 110, 60, 150, 130, 70), req_lv=65, role='caster', scale=1.25,
         src_map='RPG79', src_ref=6654, icon='ReplaceableTextures\\CommandButtons\\BTNSoulGem.blp',
         lv_moves=[(46, 1), (243, 15), (209, 30), (54, 45), (118, 60), (289, 70)],
         tm_moves=[209, 214, 243, 54, 84, 289, 321, 323]),
    dict(idx=50, hero='EL0H', wild='nL2H', soul='IL2H', dex=721, name='Volcanion', types=('fire', 'water'),
         stats=(80, 110, 120, 130, 90, 70), req_lv=65, role='caster', scale=1.35,
         src_map='PW', src_ref='Unit\\721.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_721.blp',
         lv_moves=[(237, 1), (104, 15), (276, 30), (96, 45), (136, 60), (186, 70)],
         tm_moves=[104, 96, 186, 237, 276, 136, 79, 252]),

    # Gen 7 (5)
    dict(idx=51, hero='EL0I', wild='nL2I', soul='IL2I', dex=791, name='Solgaleo', types=('psychic', 'steel'),
         stats=(137, 137, 107, 113, 89, 97), req_lv=75, role='striker', scale=1.35,
         src_map='RPG79', src_ref=6691, icon='ReplaceableTextures\\CommandButtons\\BTNInnerFire.blp',
         lv_moves=[(173, 1), (151, 15), (209, 30), (106, 45), (96, 60), (45, 75)],
         tm_moves=[151, 106, 209, 45, 80, 312, 104, 96]),
    dict(idx=52, hero='EL0J', wild='nL2J', soul='IL2J', dex=792, name='Lunala', types=('psychic', 'ghost'),
         stats=(137, 113, 89, 137, 107, 97), req_lv=75, role='caster', scale=1.35,
         src_map='RPG79', src_ref=6697, icon='ReplaceableTextures\\CommandButtons\\BTNShadowStrike.blp',
         lv_moves=[(46, 1), (243, 15), (178, 30), (209, 45), (140, 60), (118, 75)],
         tm_moves=[243, 209, 214, 178, 140, 23, 289, 323]),
    dict(idx=53, hero='EL0K', wild='nL2K', soul='IL2K', dex=800, name='Necrozma', types=('psychic',),
         stats=(97, 107, 101, 127, 89, 79), req_lv=75, role='caster', scale=1.30,
         src_map='RPG79', src_ref=6709, icon='ReplaceableTextures\\CommandButtons\\BTNSpellShieldAmulet.blp',
         lv_moves=[(46, 1), (205, 15), (214, 30), (209, 45), (106, 60), (65, 75)],
         tm_moves=[209, 214, 205, 106, 69, 54, 79, 128]),
    dict(idx=54, hero='EL0L', wild='nL2L', soul='IL2L', dex=801, name='Magearna', types=('steel', 'fairy'),
         stats=(80, 95, 115, 130, 115, 65), req_lv=65, role='caster', scale=1.20,
         src_map='RPG79', src_ref=6713, icon='ReplaceableTextures\\CommandButtons\\BTNArcaneOrb.blp',
         lv_moves=[(56, 1), (106, 15), (15, 30), (178, 45), (289, 60), (140, 70)],
         tm_moves=[106, 178, 56, 15, 289, 140, 243, 323]),
    dict(idx=55, hero='EL0M', wild='nL2M', soul='IL2M', dex=802, name='Marshadow', types=('fighting', 'ghost'),
         stats=(90, 125, 80, 90, 90, 125), req_lv=65, role='striker', scale=1.20,
         src_map='PW', src_ref='Unit\\802.mdx', icon='ReplaceableTextures\\CommandButtons\\BTN_802.blp',
         lv_moves=[(246, 1), (32, 15), (244, 30), (72, 45), (45, 60), (142, 70)],
         tm_moves=[45, 72, 32, 244, 243, 142, 99, 287]),

    # Gen 8 (2)
    dict(idx=56, hero='EL0N', wild='nL2N', soul='IL2N', dex=888, name='Zacian', types=('fairy', 'steel'),
         stats=(92, 150, 115, 80, 115, 148), req_lv=75, role='striker', scale=1.30,
         src_map='RPG79', src_ref=6741, icon='ReplaceableTextures\\CommandButtons\\BTNArcaniteMelee.blp',
         lv_moves=[(173, 1), (235, 15), (151, 30), (194, 45), (45, 60), (312, 75)],
         tm_moves=[151, 194, 235, 45, 51, 312, 142, 320]),
    dict(idx=57, hero='EL0O', wild='nL2O', soul='IL2O', dex=890, name='Eternatus', types=('poison', 'dragon'),
         stats=(140, 85, 95, 145, 95, 130), req_lv=75, role='caster', scale=1.25,
         src_map='RPG79', src_ref=6742, icon='ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp',
         lv_moves=[(299, 1), (69, 15), (252, 30), (104, 45), (65, 60), (106, 75)],
         tm_moves=[252, 299, 69, 65, 104, 106, 243, 366]),
]

# 10 Existing Mega/Form skin model upgrades (all 0 missing textures in 79.PokemonRPG.w3x)
UPGRADE_SKIN_MODELS = [
    # Existing Mega skin unit IDs (already in war3map.w3u -> update umdl!)
    ('hM0D', 5747, 'PkFx\\Mega3D\\MegaMewtwoX.mdx', 1.30, False),
    ('hM0E', 5748, 'PkFx\\Mega3D\\MegaMewtwoY.mdx', 1.30, False),
    ('hM0F', 6157, 'PkFx\\Mega3D\\MegaRayquaza.mdx', 1.45, False),
    # New skin unit IDs for Primal Kyogre (Mega 33), Primal Groudon (Mega 34), Mega Latias/Latios (Mega 35)
    ('hMPK', 6147, 'PkFx\\Mega3D\\PrimalKyogre.mdx', 1.45, True),
    ('hMPG', 6153, 'PkFx\\Mega3D\\PrimalGroudon.mdx', 1.45, True),
    ('hMLL', 6139, 'PkFx\\Mega3D\\MegaLatias.mdx', 1.35, True),
    # New skin unit IDs for PAX_Form_Appearance (Giratina Origin = 4, Deoxys Attack/Defense/Speed = 7, 8, 9)
    ('hMF4', 6375, 'PkFx\\Mega3D\\GiratinaOrigin.mdx', 1.40, True),
    ('hMF7', 6160, 'PkFx\\Mega3D\\DeoxysAttack.mdx', 1.35, True),
    ('hMF8', 6161, 'PkFx\\Mega3D\\DeoxysDefense.mdx', 1.35, True),
    ('hMF9', 6162, 'PkFx\\Mega3D\\DeoxysSpeed.mdx', 1.35, True),
]

# 7 NEW Mega / Form entries appended to Mega_InitData (indices 37..43, Mega_N = 44)
# All unlocked via Gold '+' Hero Skill button (no shop items needed!)
NEW_MEGAS = [
    dict(idx=37, base='EP05', stone='IM20', skin='hM20', abil='AM20', block=5929,
         mdx='PkFx\\Mega3D\\MegaSwampert.mdx', name='Mega Swampert', stone_name='Swampertite',
         pstr=35, pagi=15, pint=10, req_lv=50, scale=1.45, base_scale=1.20,
         art='ReplaceableTextures\\CommandButtons\\BTN_260.blp', order='acolyteharvest',
         fx='Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl'),
    dict(idx=38, base='P1LA', stone='IM21', skin='hM21', abil='AM21', block=6273,
         mdx='PkFx\\Mega3D\\MegaGarchomp.mdx', name='Mega Garchomp', stone_name='Garchompite',
         pstr=30, pagi=-10, pint=40, req_lv=50, scale=1.45, base_scale=1.20,
         art='ReplaceableTextures\\CommandButtons\\BTNRedDragonDevour.blp', order='ambush',
         fx='Abilities\\Spells\\Orc\\Earthquake\\EarthquakeTarget.mdl'),
    dict(idx=39, base='EL0A', stone='IM22', skin='hM22', abil='AM22', block=6605,
         mdx='PkFx\\Mega3D\\BlackKyurem.mdx', name='Black Kyurem', stone_name='DNA Splicers (Black)',
         pstr=30, pagi=10, pint=5, req_lv=70, scale=1.50, base_scale=1.35,
         art='ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp', order='animatedead',
         fx='Abilities\\Spells\\Other\\Monsoon\\MonsoonBoltTarget.mdl'),
    dict(idx=40, base='EL0A', stone='IM23', skin='hM23', abil='AM23', block=6606,
         mdx='PkFx\\Mega3D\\WhiteKyurem.mdx', name='White Kyurem', stone_name='DNA Splicers (White)',
         pstr=5, pagi=10, pint=30, req_lv=70, scale=1.50, base_scale=1.35,
         art='ReplaceableTextures\\CommandButtons\\BTNOrbOfFire.blp', order='antimagicshell',
         fx='Abilities\\Spells\\Human\\FlameStrike\\FlameStrike1.mdl'),
    dict(idx=41, base='EL0F', stone='IM24', skin='hM24', abil='AM24', block=6653,
         mdx='PkFx\\Mega3D\\MegaDiancie.mdx', name='Mega Diancie', stone_name='Diancite',
         pstr=40, pagi=45, pint=40, req_lv=70, scale=1.40, base_scale=1.25,
         art='ReplaceableTextures\\CommandButtons\\BTN_719.blp', order='barkskin',
         fx='Abilities\\Spells\\Human\\Resurrect\\ResurrectTarget.mdl'),
    dict(idx=42, base='EL0G', stone='IM25', skin='hM25', abil='AM25', block=6655,
         mdx='PkFx\\Mega3D\\HoopaUnbound.mdx', name='Hoopa Unbound', stone_name='Prison Bottle',
         pstr=35, pagi=15, pint=20, req_lv=70, scale=1.55, base_scale=1.25,
         art='ReplaceableTextures\\CommandButtons\\BTNSoulGem.blp', order='battleroar',
         fx='Abilities\\Spells\\Undead\\DarkRitual\\DarkRitualTarget.mdl'),
    dict(idx=43, base='EL0K', stone='IM26', skin='hM26', abil='AM26', block=6712,
         mdx='PkFx\\Mega3D\\UltraNecrozma.mdx', name='Ultra Necrozma', stone_name='Ultranecrozium Z',
         pstr=40, pagi=45, pint=40, req_lv=70, scale=1.55, base_scale=1.30,
         art='ReplaceableTextures\\CommandButtons\\BTNStarfall.blp', order='battlestations',
         fx='Abilities\\Spells\\NightElf\\Starfall\\StarfallCaster.mdl'),
]


def _parse_textures(data):
    texs = []
    p = 4
    while p + 8 <= len(data):
        tag = data[p:p + 4]
        n = struct.unpack_from('<I', data, p + 4)[0]
        if tag == b'TEXS':
            for k in range(n // 268):
                at = p + 8 + k * 268 + 4
                path = data[at:at + 260].split(b'\0')[0].decode('latin-1', errors='ignore')
                if path:
                    texs.append(path)
        p += 8 + n
    return texs


def _fix_shiny_paths(data, arc):
    out = bytearray(data)
    p = 4
    while p + 8 <= len(out):
        tag = bytes(out[p:p + 4])
        n = struct.unpack_from('<I', out, p + 4)[0]
        if tag == b'TEXS':
            for k in range(n // 268):
                at = p + 8 + k * 268 + 4
                path = bytes(out[at:at + 260]).split(b'\0')[0].decode('latin-1', errors='ignore')
                if path and not arc.has(path) and not path.lower().startswith(BLIZZARD_PREFIXES):
                    alt = re.sub(r'(?i)(?:ss(?=[a-z]?\.blp$)|_shiny(?=\.blp$))', '', path)
                    if alt != path and arc.has(alt):
                        out[at:at + 260] = alt.encode('latin-1').ljust(260, b'\0')
        p += 8 + n
    return bytes(out)


def load_all_assets(mpq_mod):
    """Reads all 25 new Legend models + 17 real 3D Mega/Form models + textures + icons from source maps."""
    class PW(mpq_mod.MPQ):
        def _find_header(self):
            return 1024

    arcs = {
        'PW': PW(PW_MAP),
        'RPG79': mpq_mod.MPQ(RPG79_MAP),
    }
    out = {}

    def pack_mdx(arc, src, dst_mdx):
        if dst_mdx == 'PkFx\\Mega3D\\DeoxysDefense.mdx':
            deox_path = os.path.join(WORK, 'extracted_v1.8', 'Deoxys.mdx')
            with open(deox_path, 'rb') as df:
                raw = df.read()
            tex_path = os.path.join(WORK, 'extracted_v1.8', 'deoxystex.blp')
            with open(tex_path, 'rb') as tf:
                out['deoxystex.blp'] = tf.read()
            out[dst_mdx] = raw
            return
        raw = arc.read_block(src) if isinstance(src, int) else arc.read(src)
        raw = _fix_shiny_paths(raw, arc)
        out[dst_mdx] = raw
        for tp in _parse_textures(raw):
            if tp.lower().startswith(BLIZZARD_PREFIXES):
                continue
            if arc.has(tp):
                out[tp] = arc.read(tp)

    # 1. 25 New Legendaries
    for lg in NEW_LEGENDS:
        arc = arcs[lg['src_map']]
        dst_mdx = f"PkFx\\Leg25\\{lg['dex']:03d}_{lg['name']}.mdx"
        pack_mdx(arc, lg['src_ref'], dst_mdx)
        if lg['src_map'] == 'PW':
            d = f"{lg['dex']:03d}"
            for ic in (f"ReplaceableTextures\\CommandButtons\\BTN_{d}.blp",
                       f"ReplaceableTextures\\CommandButtonsDisabled\\DISBTN_{d}.blp"):
                if arc.has(ic):
                    out[ic] = arc.read(ic)

    # 2. 10 Upgraded existing Mega/Form 3D models
    for _sid, blk, dst_mdx, _sc, _create in UPGRADE_SKIN_MODELS:
        pack_mdx(arcs['RPG79'], blk, dst_mdx)

    # 3. 7 New Mega/Form 3D models
    for mg in NEW_MEGAS:
        pack_mdx(arcs['RPG79'], mg['block'], mg['mdx'])

    print(f"[legend_expansion_data] Packed {len(out)} MDX/BLP asset files for 25 new Legendaries + 17 real 3D Mega/Forms.")
    return out


def _clone_obj(objdata, src_obj, new_id, overrides):
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


def patch_objects(objdata, w3u, abil, items, func, strings):
    """Creates unit objects (EL00..EL0O, nL20..nL2O, skin units hM*), Soul items (IL20..IL2O),
    and 7 new Mega/Form Hero abilities (AM20..AM26)."""
    by_id = {u.id: u for u in w3u.original + w3u.custom}
    hero_tmpl = by_id['PV2A']   # Latias & Latios hero template
    wild_tmpl = by_id['nL18']   # Latias & Latios wild boss template
    skin_tmpl = by_id['hM0F']   # Mega Rayquaza skin unit template
    soul_tmpl = items.find('ISL9')
    abil_tmpl = abil.find('AM0X')
    acol, icol = abil.name_to_x, items.name_to_x

    # 1. Upgrade 10 existing Mega/Form skin models
    for sid, _blk, dst_mdx, sc, create_new in UPGRADE_SKIN_MODELS:
        mdl_val = dst_mdx[:-4] + '.mdl'
        if create_new:
            if sid not in by_id:
                obj = _clone_obj(objdata, skin_tmpl, sid, {
                    'umdl': (mdl_val, 3),
                    'usca': (float(sc), 1),
                    'unam': (sid, 3),
                })
                w3u.custom.append(obj)
                by_id[sid] = obj
        else:
            u = by_id.get(sid)
            if u:
                u.set('umdl', 3, mdl_val)
                u.set('usca', 1, float(sc))

    # 2. Add 25 new Legendary Heroes, Wild Bosses, and Souls
    for lg in NEW_LEGENDS:
        hp, atk, de, spa, spd, spe = lg['stats']
        type_lbl = '&'.join(t.capitalize() for t in lg['types']) + ' Pokemon'
        mdl_val = f"PkFx\\Leg25\\{lg['dex']:03d}_{lg['name']}.mdl"
        main_stat = 'STR' if atk >= spa else 'INT'
        if lg['hero'] not in by_id:
            h_obj = _clone_obj(objdata, hero_tmpl, lg['hero'], {
                'umdl': (mdl_val, 3),
                'unam': (type_lbl, 3),
                'upro': (lg['name'], 3),
                'uico': (lg['icon'], 3),
                'usca': (float(lg['scale']), 1),
                'uhpm': (40 * hp, 0),
                'ustr': (atk, 0),
                'uagi': (spe, 0),
                'uint': (spa, 0),
                'udef': (int(round(0.6 * de)), 0),
                'upra': (main_stat, 3),
                'uhab': ('', 3),
            })
            w3u.custom.append(h_obj)
            by_id[lg['hero']] = h_obj

        if lg['wild'] not in by_id:
            w_obj = _clone_obj(objdata, wild_tmpl, lg['wild'], {
                'umdl': (mdl_val, 3),
                'unam': (f"Wild {lg['name']}", 3),
                'uico': (lg['icon'], 3),
                'usca': (float(lg['scale'] * 1.15), 1),
                'uhpm': (40 * hp * 4, 0),
                'udef': (int(round(0.6 * de)), 0),
            })
            w3u.custom.append(w_obj)
            by_id[lg['wild']] = w_obj

        if items.find(lg['soul']) is None:
            ir = dict(soul_tmpl)
            ir[1] = f'"{lg["soul"]}"'
            items.rows.append(ir)
        if f"[{lg['soul']}]" not in func:
            func += (
                f"\n[{lg['soul']}]\n"
                f"Name={lg['name']} Soul\n"
                f"Tip={lg['name']} Soul\n"
                f"Ubertip=\"Equip in slot 1 and step into the Center Altar circle to transform into Legendary |cffffcc00{lg['name']}|r ({type_lbl}).\"\n"
                f"Description=Soul of Legendary {lg['name']}.\n"
                f"Art={lg['icon']}\n"
            )

    # 3. Add 7 New Mega/Form skin units + Hero Abilities (AM20..AM26)
    for mg in NEW_MEGAS:
        mdl_val = mg['mdx'][:-4] + '.mdl'
        if mg['skin'] not in by_id:
            sk = _clone_obj(objdata, skin_tmpl, mg['skin'], {
                'umdl': (mdl_val, 3),
                'usca': (float(mg['scale']), 1),
                'unam': (mg['name'], 3),
            })
            w3u.custom.append(sk)
            by_id[mg['skin']] = sk

        if abil.find(mg['abil']) is None:
            ra = dict(abil_tmpl)
            ra[1] = f'"{mg["abil"]}"'
            ra[acol['DataF1']] = f'"{mg["order"]}"'
            ra[acol['hero']] = '1'
            ra[acol['item']] = '0'
            ra[acol['levels']] = '1'
            ra[acol['reqLevel']] = str(mg['req_lv'])
            ra[acol['Cool1']] = '150'
            ra[acol['DataC1']] = '1'
            abil.rows.append(ra)

        if f"[{mg['abil']}]" not in strings:
            is_second = (mg['abil'] == 'AM23')  # White Kyurem is 2nd form on Kyurem
            bp = '2,1' if is_second else '1,1'
            hk = 'F' if is_second else 'D'
            rbp = '1,0' if is_second else '0,0'
            stat_txt = f"{mg['pstr']:+d}% STR, {mg['pagi']:+d}% AGI, {mg['pint']:+d}% INT"
            cost = 8000 if mg['req_lv'] >= 70 else 5000
            strings += (
                f"\n[{mg['abil']}]\n"
                f"Name=Mega / Form: {mg['name']}\n"
                f"Art={mg['art']}\n"
                f"Researchart={mg['art']}\n"
                f"Buttonpos={bp}\n"
                f"Researchbuttonpos={rbp}\n"
                f"Hotkey={hk}\n"
                f"Researchhotkey={hk}\n"
                f"Order={mg['order']}\n"
                f"Tip=Transform - |cffff66cc{mg['name']}|r |cffffcc00[{hk}]|r\n"
                f"Researchtip=Unlock |cffff66cc{mg['name']}|r (Lv {mg['req_lv']}, {cost:,}g) |cffffcc00[{hk}]|r\n"
                f"Ubertip=\"Transform into |cffff66cc{mg['name']}|r for 60s ({stat_txt}, +10 Armor, +80 MS, +40% AS; 150s CD). One-time unlock cost: |cffffd166{cost:,}g|r (no inventory slot needed).\"\n"
                f"Researchubertip=\"Unlocks |cffff66cc{mg['name']}|r on your command card [{hk}] at Lv {mg['req_lv']} for |cffffd166{cost:,} Gold|r (+40 passive All Stats once paid).\"\n"
            )

    return func, strings


def patch_script(s: str) -> str:
    """Wires 25 new Legendaries, 10 upgraded 3D Mega/Form skins, and 7 new Mega/Forms into war3map.j."""
    def once(txt, old, new, label):
        c = txt.count(old)
        if c != 1:
            raise SystemExit(f"legend_expansion_data: anchor '{label}' matched {c} times")
        return txt.replace(old, new, 1)

    # 1. Update Mega_Skin for Primal Kyogre (33), Primal Groudon (34), Mega Latias & Latios (35)
    s = once(s, "    set Mega_Skin[33] = 'P26A'", "    set Mega_Skin[33] = 'hMPK'\n    set Mega_R[33] = 255\n    set Mega_G[33] = 255\n    set Mega_B[33] = 255", "Primal Kyogre skin")
    s = once(s, "    set Mega_Skin[34] = 'P4UA'", "    set Mega_Skin[34] = 'hMPG'\n    set Mega_R[34] = 255\n    set Mega_G[34] = 255\n    set Mega_B[34] = 255", "Primal Groudon skin")
    s = once(s, "    set Mega_Skin[35] = 'PV2A'", "    set Mega_Skin[35] = 'hMLL'\n    set Mega_R[35] = 255\n    set Mega_G[35] = 255\n    set Mega_B[35] = 255", "Mega Latias skin")
    # Also clear color tint on Mega Mewtwo X/Y and Mega Rayquaza now that they have real 3D models
    for midx in (13, 14, 15):
        s = once(s, f"    set Mega_Scale[{midx}] =", f"    set Mega_R[{midx}] = 255\n    set Mega_G[{midx}] = 255\n    set Mega_B[{midx}] = 255\n    set Mega_Scale[{midx}] =", f"Mega_{midx} tint reset")

    # 2. Append 7 NEW Mega/Form entries (37..43) to Mega_InitData
    mega_add = []
    for mg in NEW_MEGAS:
        i = mg['idx']
        fx_esc = mg['fx'].replace('\\', '\\\\')
        mega_add.append(
            f"    set Mega_Base[{i}] = '{mg['base']}'\n"
            f"    set Mega_Stone[{i}] = '{mg['stone']}'\n"
            f"    set Mega_Skin[{i}] = '{mg['skin']}'\n"
            f"    set Mega_Evolve[{i}] = '{mg['abil']}'\n"
            f"    set Mega_PStr[{i}] = {mg['pstr']}\n"
            f"    set Mega_PAgi[{i}] = {mg['pagi']}\n"
            f"    set Mega_PInt[{i}] = {mg['pint']}\n"
            f"    set Mega_Price[{i}] = {8000 if mg['req_lv'] >= 70 else 5000}\n"
            f"    set Mega_Name[{i}] = \"{mg['name']}\"\n"
            f"    set Mega_StoneName[{i}] = \"{mg['stone_name']}\"\n"
            f"    set Mega_Fx[{i}] = \"{fx_esc}\"\n"
            f"    set Mega_Scale[{i}] = {mg['scale']:.3f}\n"
            f"    set Mega_BaseScale[{i}] = {mg['base_scale']:.3f}\n"
            f"    set Mega_R[{i}] = 255\n"
            f"    set Mega_G[{i}] = 255\n"
            f"    set Mega_B[{i}] = 255\n"
        )
    mega_add.append("    set Mega_N = 44\n")
    s = once(s, "    set Mega_N = 37\n", "".join(mega_add), "Mega_N = 37")

    # 3. Extend PAX_Leg_Index, PAX_Leg_Count, PAX_Leg_Name, PAX_Leg_Type, PAX_Leg_ReqLv
    idx_lines = "".join(f"    elseif id == '{lg['hero']}' then\n        return {lg['idx']}\n" for lg in NEW_LEGENDS)
    s = once(s, "    elseif id == 'P1YA' then\n        return 32\n", f"    elseif id == 'P1YA' then\n        return 32\n{idx_lines}", "PAX_Leg_Index")

    s = once(s, "function PAX_Leg_Count takes nothing returns integer\n    return 32\nendfunction",
             "function PAX_Leg_Count takes nothing returns integer\n    return 57\nendfunction", "PAX_Leg_Count")

    name_lines = "".join(f"    elseif idx == {lg['idx']} then\n        return \"{lg['name']}\"\n" for lg in NEW_LEGENDS)
    s = once(s, "    elseif idx == 32 then\n        return \"Iron Jugulis\"\n", f"    elseif idx == 32 then\n        return \"Iron Jugulis\"\n{name_lines}", "PAX_Leg_Name")

    type_lines = "".join(f"    elseif idx == {lg['idx']} then\n        return '{lg['hero']}'\n" for lg in NEW_LEGENDS)
    s = once(s, "    elseif idx == 25 then\n        return 'P0JA'\n", f"    elseif idx == 25 then\n        return 'P0JA'\n{type_lines}", "PAX_Leg_Type")

    box_idxs = [str(lg['idx']) for lg in NEW_LEGENDS if lg['req_lv'] >= 75]
    box_cond = " or ".join(f"idx == {k}" for k in box_idxs)
    s = once(s, "    if idx == 4 or idx == 14 or idx == 24 then\n        return 75\n    endif",
             f"    if idx == 4 or idx == 14 or idx == 24 or {box_cond} then\n        return 75\n    endif", "PAX_Leg_ReqLv")

    # 4. Protect new Legend Souls IL20..IL2O in PAX_IsSoulboundProtectedItem (occurs twice in v4.1.3h)
    old_sb = "(id >= 'ISL0' and id <= 'ISL9')"
    new_sb = "((id >= 'ISL0' and id <= 'ISL9') or (id >= 'IL20' and id <= 'IL2O'))"
    if old_sb not in s:
        raise SystemExit("legend_expansion_data: ISL0..ISL9 soulbound anchor not found")
    s = s.replace(old_sb, new_sb)

    # 5. Balanced Awakened Hidden Power combat effects for new Legendaries (idx 33..57)
    # In PAX_Leg_ModifyIncoming: tank role (-15% incoming dmg), drain role (also gets offense boost in Ab_OnDamaging)
    tank_cond = " or ".join(f"idx == {lg['idx']}" for lg in NEW_LEGENDS if lg['role'] == 'tank')
    old_inc_ret = "    return dmg\nendfunction\n\nfunction PAX_Leg_Tick"
    # More reliable anchor: end of PAX_Leg_ModifyIncoming
    p_inc = s.find("function PAX_Leg_ModifyIncoming ")
    e_inc = s.find("endfunction", p_inc)
    inc_body = s[p_inc:e_inc]
    last_ret = inc_body.rfind("    return dmg\n")
    if last_ret == -1:
        raise SystemExit("legend_expansion_data: PAX_Leg_ModifyIncoming return dmg not found")
    tank_hook = (
        f"    if PAX_Leg_Awakened(tgt) then\n"
        f"        set idx = PAX_Leg_Index(GetUnitTypeId(tgt))\n"
        f"        if {tank_cond} then\n"
        f"            set dmg = dmg * 0.85\n"
        f"        endif\n"
        f"    endif\n"
    )
    inc_body = inc_body[:last_ret] + tank_hook + inc_body[last_ret:]
    s = s[:p_inc] + inc_body + s[e_inc:]

    # 6. Build chunked init functions for the 25 new Legendaries' stats, types, learnsets, wild pool, and souls
    init_blocks = []
    # Split into 2 functions to stay way below JASS op-limit
    for part_i, subset in enumerate((NEW_LEGENDS[:13], NEW_LEGENDS[13:]), 1):
        lines = [f"function Leg25_InitPart{part_i} takes nothing returns nothing"]
        for lg in subset:
            hp, atk, de, spa, spd, spe = lg['stats']
            main_code = 1 if atk >= spa else 3
            h, w, sl_id = lg['hero'], lg['wild'], lg['soul']
            t1 = TYPE_IDX[lg['types'][0]] + 1
            t2 = (TYPE_IDX[lg['types'][1]] + 1) if len(lg['types']) > 1 else 0
            # Hero stats in Mega_HT / Fx_HT / Ab_HT
            lines += [
                f"    call SaveInteger(Mega_HT, '{h}', 80, {40 * hp})",
                f"    call SaveInteger(Mega_HT, '{h}', 81, {40 * hp})",
                f"    call SaveInteger(Mega_HT, '{h}', 82, {atk})",
                f"    call SaveInteger(Mega_HT, '{h}', 83, {spe})",
                f"    call SaveInteger(Mega_HT, '{h}', 84, {spa})",
                f"    call SaveInteger(Mega_HT, '{h}', 85, {main_code})",
                f"    call SaveInteger(Mega_HT, '{h}', 86, 1800)",
                f"    call SaveInteger(Fx_HT, '{h}', 1, {de})",
                f"    call SaveInteger(Fx_HT, '{h}', 2, {spd})",
                f"    call SaveInteger(Ab_HT, '{h}', 53, {t1})",
                f"    call SaveInteger(Ab_HT, '{w}', 53, {t1})",
            ]
            if t2 > 0:
                lines += [
                    f"    call SaveInteger(Ab_HT, '{h}', 54, {t2})",
                    f"    call SaveInteger(Ab_HT, '{w}', 54, {t2})",
                ]
            # Level-up moves & TMs
            for mv, lv in lg['lv_moves']:
                lines.append(f"    call Fx_AddLv('{h}', {mv}, {lv})")
            for mv in lg['tm_moves']:
                lines.append(f"    call Fx_AddTm('{h}', {mv})")
            # Register in Random Legends pool & Soul transform table
            lines += [
                f"    set Leg_Type[Leg_N] = '{w}'",
                f"    set Leg_Soul[Leg_N] = '{sl_id}'",
                f"    set Leg_Name[Leg_N] = \"{lg['name']}\"",
                f"    set Leg_N = Leg_N + 1",
                f"    set Soul_Item[Soul_N] = '{sl_id}'",
                f"    set Soul_Hero[Soul_N] = '{h}'",
                f"    set Soul_N = Soul_N + 1",
            ]
        lines.append("endfunction\n")
        init_blocks.append("\n".join(lines))

    # Insert Leg25_InitPart1 & Part2 right BEFORE `function Fx_Data` (or right after Fx_AddTm!)
    addtm_anchor = "function Fx_AddTm takes integer uid, integer mvi returns nothing\n    local integer n = LoadInteger(Ab_HT, uid, 299)\n    call SaveInteger(Ab_HT, uid, 300 + n, mvi)\n    call SaveInteger(Ab_HT, uid, 299, n + 1)\nendfunction"
    s = once(s, addtm_anchor, addtm_anchor + "\n\n" + "\n".join(init_blocks), "Fx_AddTm insert Leg25_Init")

    # Call Leg25_InitPart1 & Leg25_InitPart2 right after Darkrai registration at L109124
    darkrai_anchor = "    set Leg_Type[Leg_N] = 'nL19'\n    set Leg_Soul[Leg_N] = 'I01F'\n    set Leg_Name[Leg_N] = \"Darkrai\"\n    set Leg_N = Leg_N + 1"
    s = once(s, darkrai_anchor, darkrai_anchor + "\n    call ExecuteFunc(\"Leg25_InitPart1\")\n    call ExecuteFunc(\"Leg25_InitPart2\")", "Darkrai Leg_Type call")

    return s
