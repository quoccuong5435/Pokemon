"""v3.4.7 data: 9xHeroDefense effects on Pokemon moves (from Skill_Map_DeXuat.xlsx), built from v3.4.5.

Visual only. The old art of each move is removed (missile, caster/target/effect/special/area art, lightning, and the
target art of its buffs through art-less buff copies; the stun stars BPSE stay as the stun marker) and replaced by
JASS special effects, scaled up.

SPEC[move] = dict of layers (model = folder name in WW3/Skill/HieuUng):
  p   projectile flying caster -> target / line end at the move's own missile speed (impact layers fire on arrival)
  h   main impact (target, line end, caster for self AoE, point for channel AoE)
  h2  second impact stacked on h
  t   trail: effects along the line, timed with the wave
  r   ring of rn effects around the impact
  c   effect on the caster when the move starts
  m   main impact repeated m times (0.2 s apart, small offset)
  ps / hs / ts / rs / cs  scale override
"""

ASSET_OF = {}   # move -> asset number in Skill_Map_DeXuat (report only)

def _a(stt, moves):
    for mv in moves:
        ASSET_OF[mv] = stt


SPEC = {
    # 1 Mokuton Life Energy
    'Giga Drain': dict(h='CenarionFury', h2='AncientExplode', h2s=0.45),
    'Mega Drain': dict(h='CenarionFury', h2='AncientExplode', h2s=0.4),
    'Absorb': dict(h='CenarionFury'),
    # 4 Suiton Mizurappa
    'Water Gun': dict(p='WaterBlobs1', t='WaterBlast', h='WaterBlast'),
    'Hydro Pump': dict(p='WaterBlobs1', t='BlizzardEruption', h='WaterBlast'),
    'Water Pulse': dict(p='WaterBlobs1', t='WaterBlast', h='WaterBlast'),
    # 5 Suiton Suijinheki
    'Liquidation': dict(p='WaterBlobs1', h='AquaSpikeVersion2', r='AquaSpikeVersion2', rn=5),
    'Aqua Tail': dict(p='WaterBlobs1', h='AquaSpikeVersion2', r='AquaSpikeVersion2', rn=5),
    # 6 Suiton Suiryuu Koubaku
    'Hydro Cannon': dict(p='WaterBlobs1', t='TidalEruption', h='TidalEruption'),
    'Waterfall': dict(p='WaterBlobs1', h='TidalEruption'),
    # 8 Yellow Flash
    'Extreme Speed': dict(c='HolyBomb', t='DivineRage', h='HolyBomb'),
    'Quick Attack': dict(c='HolyBomb', t='DivineRage', h='HolyBomb'),
    # 9 Omnislash
    'Slash': dict(h='DivineRage', m=3),
    'Fury Cutter': dict(h='DivineRage', m=4),
    'Double Hit': dict(h='DivineRage', m=2),
    # 10 Katon Gouka Mekkyaku
    'Heat Wave': dict(h='A-Bomb', r='A-Bomb', rn=6),
    'Overheat': dict(t='A-Bomb', h='A-Bomb'),
    # 11 Mokuton Jukai Koutan
    'Frenzy Plant': dict(h='Mokuton Tree 1', h2='Mokuton (2)'),
    'Power Whip': dict(t='Mokuton Tree 1', h='Mokuton (2)'),
    # 12 Mokuton Kajukai Kourin
    'Petal Dance': dict(h='Mokuton (2)'),
    'Petal Blizzard': dict(h='Mokuton (2)', r='Mokuton Tree 1', rn=6),
    'Leaf Storm': dict(h='Mokuton (2)'),
    # 13 Amaterasu
    'Burning Jealousy': dict(t='Black Stomp', h='Enton Honoikazuchi 1'),
    'Hex': dict(h='Black Stomp', h2='Enton Honoikazuchi 1'),
    # 14 Enton Kagutsuchi
    'Temper Flare': dict(p='Amaterasu_New', h='PurpleExplosion_2', h2='Black Stomp'),
    'Mystical Fire': dict(p='Amaterasu_New', t='Amaterasu_New', h='PurpleExplosion_2'),
    # 15 Chidori Nagashi
    'Discharge': dict(h='EmpBomb', r='GreatLightning', rn=6),
    'Spark': dict(p='LightningBoom', h='EmpBomb'),
    'Thunder Shock': dict(h='EmpBomb', h2='LightningBoom'),
    # 16 Raiton Kirin
    'Thunder': dict(h='GreatLightning', r='GreatLightning', rn=6),
    'Thunderbolt': dict(h='GreatLightning', h2='LightningBoom'),
    # 18 Shinra Tensei
    'Expanding Force': dict(h='Explosion'),
    'Psychic': dict(h='Explosion'),
    # 20 Excellent Shinra Tensei
    'Judgment': dict(h='Explosion', r='Explosion', rn=8),
    'Boomburst': dict(h='Explosion'),
    'Hyper Voice': dict(h='Explosion', r='Explosion', rn=6),
    # 21 Suiton Soodai Kaisaku
    'Water Spout': dict(h='BlizzardEruption'),
    'Brine': dict(p='WaterBlobs1', t='BlizzardEruption', h='BlizzardEruption'),
    # 22 Suiton Dai Bakusui Shouha
    'Bubble Beam': dict(p='BlueBall', ps=0.45, h='WaterBlast'),
    'Chilling Water': dict(p='BlueBall', ps=0.45, h='WaterBlast'),
    # 23 Explosive
    'Explosion': dict(h='A-Bomb', r='A-Bomb', rn=6),
    'Self Destruct': dict(h='A-Bomb', r='A-Bomb', rn=6),
    'Misty Explosion': dict(h='A-Bomb', r='A-Bomb', rn=6),
    # 24 Sabaku Taisou
    'Sand Tomb': dict(t='Sand_New_Spell', h='Sand_Effect'),
    'Scorching Sands': dict(t='Sand_New_Spell', h='Sand_Effect'),
    # 25 Ryuusa Bakuryuu
    'Earth Power': dict(h='Sand_Effect', r='Sand_New_Spell', rn=6),
    'Earthquake': dict(h='Sand_Effect', r='Sand_New_Spell', rn=8),
    'Precipice Blades': dict(h='Sand_Effect', r='Sand_New_Spell', rn=8),
    # 26 Kamehame Ha x10 (the KamehameHa trail draws the beam)
    'Hyper Beam': dict(p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy', h2='White Explosion'),
    'Flash Cannon': dict(p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy'),
    'Steel Beam': dict(p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy', h2='White Explosion'),
    # 27 Meteorain
    'Draco Meteor': dict(t='FireStone', h='FireStone', h2='FireStomp'),
    'Rock Slide': dict(h='FireStone', r='FireStone', rn=5),
    # 28 Ultimate Swords
    'Sacred Sword': dict(h='PsiWave', m=2, h2='Blue Explosion'),
    'Psycho Cut': dict(h='PsiWave', m=2),
    'Smart Strike': dict(h='PsiWave', h2='Blue Explosion'),
    # 29 Katon Goukakyuu No Jutsu
    'Fire Blast': dict(h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=6),
    'Ember': dict(p='RedDragonFlame', h='KatonGoukaMesshitsu'),
    'Incinerate': dict(p='RedDragonFlame', t='RedDragonFlame', h='KatonGoukaMesshitsu'),
    # 30 Uchiha Style Halo Dance
    'Flame Wheel': dict(p='FireShockRun1', h='RedDragonFlame', m=2),
    'Flame Charge': dict(t='FireShockRun1', h='RedDragonFlame'),
    # 31 Kotoamatsukami
    'Confusion': dict(c='GainLife', h='Yellow Goku Effect'),
    'Extrasensory': dict(c='GainLife', h='Yellow Goku Effect'),
    # 32 Susanoo Tsukumo
    'Psycho Boost': dict(p='Susanoo Tsukumo', t='Susanoo Tsukumo', h='CenarionFury'),
    'Psystrike': dict(h='Susanoo Tsukumo', m=4, h2='Blood_Strike'),
    # 33 Hyourinmaru
    'Ice Beam': dict(p='SpiritArrow_ByEpsilon', t='Hyourinmaru 1', h='ArcaneExplosion'),
    # 34 Ryuusenka
    'Freeze Dry': dict(h='IceStomp', h2='Hyourinmaru 1'),
    'Ice Fang': dict(h='Hyourinmaru 1', h2='ArcaneExplosion'),
    # 35 Sennen Hyourou
    'Icicle Crash': dict(h='IceNova', r='Ice Pillar', rn=6, rs=2.5),
    # 36 Hyouten Hyakkasou
    'Blizzard': dict(h='Hyouten Hyakkasou', r='IceNova', rn=6),
    # 37 Gunchou Tsurara
    'Icicle Spear': dict(h='GlowLineBlue', h2='ArcaneExplosion', m=3),
    'Ice Shard': dict(h='GlowLineBlue', h2='ArcaneExplosion'),
    # 38 Cero Oscuras
    'Dark Pulse': dict(p='Black Ball', t='HarvestLife', h='EarthNova'),
    'Shadow Ball': dict(h='Black Ball', h2='EarthNova'),
    # 39 Vasto Lorde Lightning Blast
    'Zap Cannon': dict(p='Red Cero', t='ThunderStrike', h='Red Explosion'),
    'Charge Beam': dict(p='Red Cero', t='ThunderStrike', h='Red Damage'),
    # 40 Inugami Guren
    'Fire Fang': dict(p='RedDragonHead', h='RedDragonFlame', h2='Lava Crack', h2s=0.5),
    # 41 Meigo
    'Flare Blitz': dict(t='Lava Crack', h='Lava Crack'),
    # 42 Ryusei Kazan
    'Eruption': dict(h='Lava_Fall', h2='Slam'),
    # 43 Pheasant Beak
    'Aurora Beam': dict(p='SpiritArrow_ByEpsilon', t='ArcaneExplosion', h='ArcaneExplosion'),
    # 44 Ice Time
    'Ice Punch': dict(h='ArcaneExplosion', h2='IceNova'),
    # 45 Ice Age
    'Icy Wind': dict(h='IceNova', r='ArcaneExplosion', rn=6),
    'Powder Snow': dict(t='IceNova', h='ArcaneExplosion'),
    # 46 Ice Time Capsule
    'Avalanche': dict(h='Slam Ice', h2='ArcaneExplosion'),
    'Ice Spinner': dict(h='Slam Ice', h2='ArcaneExplosion'),
    # 47 Tidal Wave
    'Whirlpool': dict(p='WaterBlobs1', t='WaterfallFX', h='WhirlPool'),
    'Wave Crash': dict(t='WaterfallFX', h='Freezing_Ring2', h2='WaterfallFX'),
    # 48 Tsunami
    'Surf': dict(h='WhirlPool', r='WaterfallFX', rn=8),
    'Muddy Water': dict(h='WhirlPool', r='WaterBlobs1', rn=8),
    'Origin Pulse': dict(p='WaterBlobs1', t='WaterfallFX', h='WhirlPool'),
    # 49 Hiken
    'Fire Pledge': dict(p='Effect_1', t='Cross Flame', h='Cross Flame'),
    # 50 Mera Mera No Mi
    'Lava Plume': dict(h='FireStomp', r='FireStomp', rn=6),
    # 51 Kyokaen
    'Inferno': dict(h='Flame_Model_2', r='Fire Ace', rn=8),
    # 52 Enjomo
    'Fire Spin': dict(t='Natsu Spell E', h='Natsu Spell E', r='Natsu Spell E', rn=4),
    # 53 Goshikito
    'X Scissor': dict(h='Goshikito', h2='White Ring'),
    # 54 Karyuu No Houkou
    'Flamethrower': dict(p='Raienryuu no Houkou', t='Flame_Model_2', h='Flame_Model_2'),
    # 55 Guren Karyuu Ken
    'Fire Punch': dict(p='Wind', ps=2.0, h='Flame_Model_2', m=3),
    'Blaze Kick': dict(p='Wind', ps=2.0, h='Flame_Model_2', m=2),
    # 56 Metsuryuu Ougi Guren Bakuenjin
    'Blast Burn': dict(c='Natsu Wing', h='Natsu Flame 2', h2='Flame_Model_2'),
    'Sacred Fire': dict(c='Natsu Wing', p='Natsu Flame 2', h='Flame_Model_2'),
    # 57 Hakuryuu No Houkou
    'Dragon Pulse': dict(p='White Effect 1', t='WhiteShockwave', h='White Explosion'),
    'Dragon Breath': dict(p='White Effect 1', t='White Effect 1', h='WhiteShockwave'),
    # 58 Hakuryuu No Holy Buresu
    'Dazzling Gleam': dict(h='White Holy', r='WhiteShockwave', rn=6),
    'Moonblast': dict(h='White Holy', h2='Spell W Law'),
    # 59 Liberation
    'Snarl': dict(h='Liberation', h2='BigCloudFogBlack', r='Black Stomp', rn=6),
    # 60 Black Hole
    'Phantom Force': dict(c='BlackSmoke', h='GlowBlack', h2='BigCloudFogBlack'),
    'Shadow Force': dict(c='BlackSmoke', h='GlowBlack', h2='BigCloudFogBlack'),
    # 61 Doku Fugu
    'Sludge Bomb': dict(p='Doku Fugu', h='Hydra Damage', h2='PurpleExplosion_2'),
    'Sludge': dict(p='Doku Fugu', h='Hydra Damage'),
    # 62 Doku Gumo
    'Smog': dict(h='Doku Gumo 2', h2='Doku Gumo 1'),
    'Clear Smog': dict(h='Doku Gumo 2', h2='Doku Gumo 1'),
    'Acid Spray': dict(t='Doku Gumo 1', h='Doku Gumo 2'),
    # 63 Hydra
    'Sludge Wave': dict(h='PurpleExplosion_2', r='Doku Gumo 1', rn=8),
    'Gunk Shot': dict(t='Doku Gumo 1', h='PurpleExplosion_2'),
    'Venoshock': dict(h='PurpleExplosion_2', h2='Hydra Damage'),
    # 64 Ittouryuu Sanjuuroku Pondo Hou
    'Air Slash': dict(p='Pondo Hou', h='Blue Explosion'),
    'Air Cutter': dict(h='Blue Explosion', r='Pondo Hou', rn=6),
    # 65 Santouryuu Kokujou Ou Tatsumaki
    'Hurricane': dict(h='HolyTornado', r='ArcaneTornado', rn=4),
    'Twister': dict(h='HolyTornado', r='ArcaneTornado', rn=3),
    'Gust': dict(p='HolyTornado', ps=0.6, h='ArcaneTornado'),
    # 66 Ittouryuu Daishinkan
    'Leaf Blade': dict(h='Final Wave Zoro', h2='CenarionFury'),
    'Solar Blade': dict(p='Zoro Wave', h='CenarionFury'),
    # 67 Tsubaki No Mai
    'Bone Rush': dict(t='Blood_Strike', h='Blood_Strike', m=2),
    'Bonemerang': dict(t='Blood_Strike', h='Blood_Strike'),
}

for _stt, _ms in {1: ['Giga Drain', 'Mega Drain', 'Absorb'], 4: ['Water Gun', 'Hydro Pump', 'Water Pulse'],
                  5: ['Liquidation', 'Aqua Tail'], 6: ['Hydro Cannon', 'Waterfall'], 8: ['Extreme Speed', 'Quick Attack'],
                  9: ['Slash', 'Fury Cutter', 'Double Hit'], 10: ['Heat Wave', 'Overheat'], 11: ['Frenzy Plant', 'Power Whip'],
                  12: ['Petal Dance', 'Petal Blizzard', 'Leaf Storm'], 13: ['Burning Jealousy', 'Hex'],
                  14: ['Temper Flare', 'Mystical Fire'], 15: ['Discharge', 'Spark', 'Thunder Shock'],
                  16: ['Thunder', 'Thunderbolt'], 18: ['Expanding Force', 'Psychic'],
                  20: ['Judgment', 'Boomburst', 'Hyper Voice'], 21: ['Water Spout', 'Brine'],
                  22: ['Bubble Beam', 'Chilling Water'], 23: ['Explosion', 'Self Destruct', 'Misty Explosion'],
                  24: ['Sand Tomb', 'Scorching Sands'], 25: ['Earth Power', 'Earthquake', 'Precipice Blades'],
                  26: ['Hyper Beam', 'Flash Cannon', 'Steel Beam'], 27: ['Draco Meteor', 'Rock Slide'],
                  28: ['Sacred Sword', 'Psycho Cut', 'Smart Strike'], 29: ['Fire Blast', 'Ember', 'Incinerate'],
                  30: ['Flame Wheel', 'Flame Charge'], 31: ['Confusion', 'Extrasensory'], 32: ['Psycho Boost', 'Psystrike'],
                  33: ['Ice Beam'], 34: ['Freeze Dry', 'Ice Fang'], 35: ['Icicle Crash'], 36: ['Blizzard'],
                  37: ['Icicle Spear', 'Ice Shard'], 38: ['Dark Pulse', 'Shadow Ball'], 39: ['Zap Cannon', 'Charge Beam'],
                  40: ['Fire Fang'], 41: ['Flare Blitz'], 42: ['Eruption'], 43: ['Aurora Beam'], 44: ['Ice Punch'],
                  45: ['Icy Wind', 'Powder Snow'], 46: ['Avalanche', 'Ice Spinner'], 47: ['Whirlpool', 'Wave Crash'],
                  48: ['Surf', 'Muddy Water', 'Origin Pulse'], 49: ['Fire Pledge'], 50: ['Lava Plume'], 51: ['Inferno'],
                  52: ['Fire Spin'], 53: ['X Scissor'], 54: ['Flamethrower'], 55: ['Fire Punch', 'Blaze Kick'],
                  56: ['Blast Burn', 'Sacred Fire'], 57: ['Dragon Pulse', 'Dragon Breath'],
                  58: ['Dazzling Gleam', 'Moonblast'], 59: ['Snarl'], 60: ['Shadow Force', 'Phantom Force'],
                  61: ['Sludge Bomb', 'Sludge'], 62: ['Smog', 'Clear Smog', 'Acid Spray'],
                  63: ['Sludge Wave', 'Gunk Shot', 'Venoshock'], 64: ['Air Slash', 'Air Cutter'],
                  65: ['Hurricane', 'Twister', 'Gust'], 66: ['Leaf Blade', 'Solar Blade'],
                  67: ['Bone Rush', 'Bonemerang']}.items():
    _a(_stt, _ms)

# ---- how big ("epic"): wanted horizontal radius of each layer, in game units
R_TARGET = 230.0     # impact on a single target
R_PROJ = 110.0       # flying model
R_CAST = 200.0
R_LINE_END = 260.0
AREA_MULT = 1.2      # self / point / nova impact = area x this
TRAIL_MIN = 170.0    # trail effect radius = max(area x 1.6, this)
RING_FRAC = 0.5      # each ring effect = area x this
SCALE_MIN, SCALE_MAX = 1.0, 6.0
PROJ_MIN, PROJ_MAX = 1.0, 3.5
R_UNKNOWN = 150.0    # model radius when the library has none
LIFE_MAX = 3.5       # seconds an impact stays at most
TRAIL_LIFE_MAX = 2.0
TRAIL_STEP = 170.0   # default distance between trail effects
WAVES_MAX = 12     # channel AoE (blizzard base): one impact per wave

# buffs whose target art is the old effect: mapped moves get an art-less copy (new id -> base buff)
BUFF_COPY = {'BEer': 'BP00', 'Bfro': 'BP01', 'BHbd': 'BP02', 'BNbf': 'BP03', 'BEsh': 'BP04', 'BUim': 'BP05',
             'BHtc': 'BP06', 'XHbz': 'XP00'}
