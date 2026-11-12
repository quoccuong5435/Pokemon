"""v3.4.6 data: which 9xHeroDefense effect goes on which Pokemon move (from Skill_Map_DeXuat.xlsx).

ASSET[stt] = (hero skill id in the 9xHeroDefense list, effect folder in WW3/Skill/HieuUng, [Pokemon moves])
MISSILE[move] = effect folder used as the move's Missileart (the move's own wave / bolt flies with it); those moves
get no extra JASS effect unless they are also in END_AFTER_MISSILE.
Only visuals change: damage, range, area, cooldown and mana of the moves are untouched.
"""

ASSET = {
    1: ('A090', 'CenarionFury', ['Giga Drain', 'Mega Drain', 'Absorb']),
    4: ('A01B', 'WaterBlast', ['Water Gun', 'Hydro Pump', 'Water Pulse']),
    5: ('A01A', 'AquaSpikeVersion2', ['Liquidation', 'Aqua Tail']),
    6: ('A0CE', 'TidalEruption', ['Hydro Cannon', 'Waterfall']),
    8: ('A01P', 'HolyBomb', ['Extreme Speed', 'Quick Attack']),
    9: ('A02J', 'DivineRage', ['Slash', 'Fury Cutter', 'Double Hit']),
    10: ('A018', 'A-Bomb', ['Heat Wave', 'Overheat']),
    11: ('A03Z', 'Mokuton Tree 1', ['Frenzy Plant', 'Power Whip']),
    12: ('A0BJ', 'Mokuton (2)', ['Petal Dance', 'Petal Blizzard', 'Leaf Storm']),
    13: ('A05N', 'Black Stomp', ['Burning Jealousy', 'Hex']),
    14: ('A046', 'Amaterasu_New', ['Temper Flare', 'Mystical Fire']),
    15: ('A0AE', 'EmpBomb', ['Discharge', 'Spark', 'Thunder Shock']),
    16: ('A04A', 'GreatLightning', ['Thunder', 'Thunderbolt']),
    18: ('A009', 'Explosion', ['Expanding Force', 'Psychic']),
    20: ('A00A', 'Explosion', ['Judgment', 'Boomburst', 'Hyper Voice']),
    21: ('A0CH', 'BlizzardEruption', ['Water Spout', 'Brine']),
    22: ('A00U', 'BlueBall', ['Bubble Beam', 'Chilling Water']),
    23: ('A06I', 'A-Bomb', ['Explosion', 'Self Destruct', 'Misty Explosion']),
    24: ('A04E', 'Sand_New_Spell', ['Sand Tomb', 'Scorching Sands']),
    25: ('A04L', 'Sand_Effect', ['Earth Power', 'Earthquake', 'Precipice Blades']),
    26: ('A0CK', 'SuperShinyThingy', ['Hyper Beam', 'Flash Cannon', 'Steel Beam']),
    27: ('A0DY', 'FireStone', ['Draco Meteor', 'Rock Slide']),
    28: ('A0CF', 'PsiWave', ['Sacred Sword', 'Psycho Cut', 'Smart Strike']),
    29: ('A0K1', 'KatonGoukaMesshitsu', ['Fire Blast', 'Ember', 'Incinerate']),
    30: ('A0K3', 'FireShockRun1', ['Flame Wheel', 'Flame Charge']),
    31: ('A0K4', 'Yellow Goku Effect', ['Confusion', 'Extrasensory']),
    32: ('A0K6', 'Susanoo Tsukumo', ['Psycho Boost', 'Psystrike']),
    33: ('A0LT', 'Hyourinmaru 1', ['Ice Beam']),
    34: ('A0LU', 'IceStomp', ['Freeze Dry', 'Ice Fang']),
    35: ('A0LV', 'Ice Pillar', ['Icicle Crash']),
    36: ('A0LW', 'Hyouten Hyakkasou', ['Blizzard']),
    37: ('A0LZ', 'GlowLineBlue', ['Icicle Spear', 'Ice Shard']),
    38: ('A0HV', 'Black Ball', ['Dark Pulse', 'Shadow Ball']),
    39: ('A0LD', 'ThunderStrike', ['Zap Cannon', 'Charge Beam']),
    40: ('A0AG', 'RedDragonHead', ['Fire Fang']),
    41: ('A0AU', 'Lava Crack', ['Flare Blitz']),
    42: ('A0AT', 'Lava_Fall', ['Eruption']),
    43: ('A0BB', 'ArcaneExplosion', ['Aurora Beam']),
    44: ('A0BX', 'ArcaneExplosion', ['Ice Punch']),
    45: ('A0BV', 'IceNova', ['Icy Wind', 'Powder Snow']),
    46: ('A0HK', 'Slam Ice', ['Avalanche', 'Ice Spinner']),
    47: ('A0AZ', 'WaterfallFX', ['Whirlpool', 'Wave Crash']),
    48: ('A0E3', 'WhirlPool', ['Surf', 'Muddy Water', 'Origin Pulse']),
    49: ('A047', 'Cross Flame', ['Fire Pledge']),
    50: ('A0AK', 'FireStomp', ['Lava Plume']),
    51: ('A0AI', 'Fire Ace', ['Inferno']),
    52: ('A0HG', 'Natsu Spell E', ['Fire Spin']),
    53: ('A0J2', 'Goshikito', ['X Scissor']),
    54: ('A0FA', 'Raienryuu no Houkou', ['Flamethrower']),
    55: ('A0F9', 'Flame_Model_2', ['Fire Punch', 'Blaze Kick']),
    56: ('A0F7', 'Natsu Flame 2', ['Blast Burn', 'Sacred Fire']),
    57: ('A0GH', 'White Effect 1', ['Dragon Pulse', 'Dragon Breath']),
    58: ('A0GM', 'White Holy', ['Dazzling Gleam', 'Moonblast']),
    59: ('A0DO', 'Liberation', ['Snarl']),
    60: ('A0DQ', 'GlowBlack', ['Shadow Force', 'Phantom Force']),
    61: ('A0JU', 'Doku Fugu', ['Sludge Bomb', 'Sludge']),
    62: ('A0JV', 'Doku Gumo 2', ['Smog', 'Clear Smog', 'Acid Spray']),
    63: ('A0HE', 'PurpleExplosion_2', ['Sludge Wave', 'Gunk Shot', 'Venoshock']),
    64: ('A06W', 'Pondo Hou', ['Air Slash', 'Air Cutter']),
    65: ('A0B0', 'HolyTornado', ['Hurricane', 'Twister', 'Gust']),
    66: ('A0FM', 'Final Wave Zoro', ['Leaf Blade', 'Solar Blade']),
    67: ('A064', 'Blood_Strike', ['Bone Rush', 'Bonemerang']),
}

# projectile-like models (they have a Stand animation) that replace the move's own missile
MISSILE = {
    'Hyper Beam': 'KamehameHa', 'Flash Cannon': 'KamehameHa', 'Steel Beam': 'KamehameHa',
    'Air Slash': 'Pondo Hou', 'Solar Blade': 'Zoro Wave', 'Flamethrower': 'Raienryuu no Houkou',
    'Sludge Bomb': 'Doku Fugu', 'Fire Fang': 'RedDragonHead', 'Dark Pulse': 'Black Ball',
}
# these keep a JASS impact effect at the end of the wave as well
END_AFTER_MISSILE = {'Hyper Beam', 'Flash Cannon', 'Steel Beam'}

# base ability -> how the JASS effect is placed
#   0 target: on the target unit (after the missile flight time when the base has a missile)
#   1 self: on the caster (stomp / clap)
#   2 point: on the target point
#   3 line: several effects along the line caster -> target, timed with the wave
#   4 end: one effect at the end of the line
MODE_OF_BASE = {'AHtb': 0, 'AEsh': 0, 'AEer': 0, 'AUfn': 0, 'AHtc': 1, 'AOws': 1, 'AHbz': 2,
                'AUcs': 3, 'AOsh': 3, 'AUim': 3, 'ANbf': 3}
SINGLE_TARGET = {'AHtb', 'AEsh', 'AEer'}
# big models: one effect at the end of a line instead of several along it
BIG_FOR_LINE = {'BlueBall', 'FireStone', 'KatonGoukaMesshitsu', 'Cross Flame', 'Natsu Spell E', 'HolyTornado',
                'WhirlPool', 'Sand_Effect', 'A-Bomb', 'Lava_Fall', 'GreatLightning', 'Hyouten Hyakkasou',
                'SuperShinyThingy', 'Raienryuu no Houkou', 'Doku Fugu', 'CenarionFury', 'TidalEruption'}
MAX_LIFE = 6.0       # seconds an effect stays at most
