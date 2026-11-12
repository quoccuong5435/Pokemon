"""v3.4.8 data: 9xHeroDefense effects on Pokemon moves (Skill_Map_DeXuat.xlsx + the 3 skills added in its
"Update" column), built from v3.4.5. Visual only: damage, range, area, cooldown and mana stay as they are.

Changes against v3.4.7:
- every mapped move uses only the effect models of its own 9xHeroDefense skill (as in the original skill), in more
  layers, scaled up again ("epic");
- 3 more assets (Update = x): Hashirama "Mokuton Hijutsu Jukai Koutan", Sarutobi "Katon Karyuu Endan", Pain "Rain".
  None of them exists in the 9xHeroDefense library (WW3/Skill), so they are built from the models of the closest
  skills of that map (Mokuton Jukai Koutan + the unused Mokuton Tree 2, Inugami Guren's dragon head + fire, the rain
  of Gedou Rinne Tensei);
- contact moves (Tackle, Quick Attack, punches, bites, slashes ...) are melee: the user dashes to the target and the
  hit lands when it arrives (MELEE below, all of them, mapped or not).

SPEC[move] = dict of layers (model = folder in WW3/Skill/<group>/; a group other than HieuUng is written
'ChuaDungTrongMap/<folder>'; a name starting with 'war3:' is a model of the game itself):
  p   projectile caster -> target (ranged move) / aura that rides on the user during the dash (melee move)
  h   main impact (target, line end, caster for self AoE, point for channel AoE)
  h2, h3  more impacts stacked on h
  t   trail: ranged = along the line with the wave; melee = along the dash path
  r   ring of rn effects around the impact
  c   effect on the user when the move starts
  m   main impact repeated m times (0.2 s apart, small offset)
  ps / hs / h2s / h3s / ts / rs / cs  scale override,  ds  dash speed of a melee move
"""

ASSET_OF = {}   # move -> asset number in Skill_Map_DeXuat (report only)
ASSET_NAME = {}


def _a(stt, name, moves):
    for mv in moves:
        ASSET_OF[mv] = stt
        ASSET_NAME[mv] = name


SPEC = {
    # 1 Mokuton Life Energy (AncientExplode, CenarionFury)
    'Giga Drain': dict(c='CenarionFury', h='CenarionFury', h2='AncientExplode', h2s=0.55),
    'Mega Drain': dict(c='CenarionFury', h='CenarionFury', h2='AncientExplode', h2s=0.45),
    'Absorb': dict(h='CenarionFury', h2='AncientExplode', h2s=0.35),
    # 2 (Update) Mokuton Hijutsu Jukai Koutan: forest bursting out of the ground
    'Grass Pledge': dict(h='ChuaDungTrongMap/Mokuton Tree 2', h2='Mokuton (2)', r='Mokuton Tree 1', rn=6),
    'Wood Hammer': dict(p='Mokuton (2)', ps=0.6, t='Mokuton Tree 1', h='ChuaDungTrongMap/Mokuton Tree 2',
                        h2='Mokuton (2)', r='Mokuton Tree 1', rn=5),
    # 4 Suiton Mizurappa (BlizzardEruption, WaterBlast)
    'Water Gun': dict(t='WaterBlast', h='WaterBlast', h2='BlizzardEruption'),
    'Hydro Pump': dict(t='BlizzardEruption', h='WaterBlast', h2='BlizzardEruption'),
    'Water Pulse': dict(t='WaterBlast', h='WaterBlast', h2='BlizzardEruption'),
    # 5 Suiton Suijinheki (AquaSpikeVersion2)
    'Liquidation': dict(t='AquaSpikeVersion2', h='AquaSpikeVersion2', r='AquaSpikeVersion2', rn=6),
    'Aqua Tail': dict(t='AquaSpikeVersion2', h='AquaSpikeVersion2', r='AquaSpikeVersion2', rn=6),
    # 6 Suiton Suiryuu Koubaku (TidalEruption)
    'Hydro Cannon': dict(t='TidalEruption', h='TidalEruption', r='TidalEruption', rn=4),
    'Waterfall': dict(t='TidalEruption', h='TidalEruption', r='TidalEruption', rn=3),
    # 7 (Update) Katon Karyuu Endan: a fire dragon, the user charges inside it
    'Outrage': dict(c='KatonGoukaMesshitsu', cs=1.0, p='RedDragonHead', t='RedDragonFlame', h='KatonGoukaMesshitsu',
                    r='RedDragonFlame', rn=6),
    'Dragon Rush': dict(p='RedDragonHead', t='RedDragonFlame', h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=4),
    # 8 Yellow Flash (DivineRage, HolyBomb): a yellow flash to the target
    'Extreme Speed': dict(c='HolyBomb', p='DivineRage', t='DivineRage', h='HolyBomb', h2='DivineRage', ds=3200),
    'Quick Attack': dict(c='HolyBomb', p='DivineRage', t='DivineRage', h='HolyBomb', ds=3000),
    # 9 Omnislash (DivineRage): flash cuts
    'Slash': dict(t='DivineRage', h='DivineRage', m=3, ds=2600),
    'Fury Cutter': dict(t='DivineRage', h='DivineRage', m=5, ds=2600),
    'Double Hit': dict(t='DivineRage', h='DivineRage', m=2, ds=2600),
    # 10 Katon Gouka Mekkyaku (A-Bomb)
    'Heat Wave': dict(h='A-Bomb', r='A-Bomb', rn=8),
    'Overheat': dict(t='A-Bomb', h='A-Bomb', r='A-Bomb', rn=4),
    # 11 Mokuton Jukai Koutan (Mokuton Tree 1, Mokuton (2))
    'Frenzy Plant': dict(h='Mokuton Tree 1', h2='Mokuton (2)', r='Mokuton Tree 1', rn=6),
    'Power Whip': dict(t='Mokuton Tree 1', h='Mokuton (2)', h2='Mokuton Tree 1'),
    # 12 Mokuton Kajukai Kourin (Mokuton (2), TheShow)
    'Petal Dance': dict(c='TheShow', h='Mokuton (2)', h2='TheShow'),
    'Petal Blizzard': dict(c='TheShow', h='Mokuton (2)', r='TheShow', rn=6),
    'Leaf Storm': dict(c='TheShow', h='Mokuton (2)', h2='TheShow'),
    # 13 Amaterasu of Itachi (Black Stomp, Enton Honoikazuchi 1)
    'Burning Jealousy': dict(t='Black Stomp', h='Enton Honoikazuchi 1', h2='Black Stomp'),
    'Hex': dict(h='Black Stomp', h2='Enton Honoikazuchi 1', m=2),
    # 14 Enton Kagutsuchi (Amaterasu_New, Black Stomp, PurpleExplosion_2)
    'Temper Flare': dict(p='Amaterasu_New', ps=0.8, t='Black Stomp', h='PurpleExplosion_2', h2='Amaterasu_New'),
    'Mystical Fire': dict(p='Amaterasu_New', t='Amaterasu_New', h='PurpleExplosion_2', h2='Black Stomp'),
    # 15 Chidori Nagashi (EmpBomb, GreatLightning)
    'Discharge': dict(h='EmpBomb', h2='GreatLightning', r='GreatLightning', rn=6),
    'Spark': dict(p='EmpBomb', ps=0.6, t='GreatLightning', ts=0.5, h='EmpBomb', h2='GreatLightning', ds=2600),
    'Thunder Shock': dict(h='EmpBomb', h2='GreatLightning', h2s=0.8),
    # 16 Raiton Kirin (GreatLightning, LightningBoom)
    'Thunder': dict(h='GreatLightning', h2='LightningBoom', r='GreatLightning', rn=6),
    'Thunderbolt': dict(h='GreatLightning', h2='LightningBoom', m=2),
    # 18 Shinra Tensei (Explosion)
    'Expanding Force': dict(c='Explosion', h='Explosion', r='Explosion', rn=6),
    'Psychic': dict(h='Explosion', m=2),
    # 19 (Update) Rain of Pain: a rain cloud over the target area
    'Weather Ball': dict(h='AnimatedEnviromentalEffectRain', hs=0.25, h2='WaterBlobs1', r='WaterBlobs1', rn=6),
    'Water Pledge': dict(t='WaterBlobs1', h='AnimatedEnviromentalEffectRain', hs=0.2, h2='WaterBlobs1'),
    # 20 Excellent Shinra Tensei (Explosion)
    'Judgment': dict(c='Explosion', h='Explosion', r='Explosion', rn=10),
    'Boomburst': dict(c='Explosion', h='Explosion', r='Explosion', rn=6),
    'Hyper Voice': dict(h='Explosion', r='Explosion', rn=8),
    # 21 Suiton Soodai Kaisaku (BlizzardEruption)
    'Water Spout': dict(h='BlizzardEruption', r='BlizzardEruption', rn=6),
    'Brine': dict(t='BlizzardEruption', h='BlizzardEruption', r='BlizzardEruption', rn=3),
    # 22 Suiton Dai Bakusui Shouha (BlueBall)
    'Bubble Beam': dict(p='BlueBall', ps=0.5, h='BlueBall'),
    'Chilling Water': dict(p='BlueBall', ps=0.5, h='BlueBall'),
    # 23 Explosive (A-Bomb)
    'Explosion': dict(h='A-Bomb', r='A-Bomb', rn=8),
    'Self Destruct': dict(h='A-Bomb', r='A-Bomb', rn=6),
    'Misty Explosion': dict(h='A-Bomb', r='A-Bomb', rn=6),
    # 24 Sabaku Taisou (Sand_Effect, Sand_New_Spell, SandAura)
    'Sand Tomb': dict(t='Sand_New_Spell', h='Sand_Effect', h2='Sand_New_Spell'),
    'Scorching Sands': dict(t='Sand_New_Spell', h='Sand_Effect', h2='Sand_New_Spell'),
    # 25 Ryuusa Bakuryuu (Sand_Loop)
    'Earth Power': dict(h='Sand_Loop', r='Sand_Loop', rn=6),
    'Earthquake': dict(h='Sand_Loop', r='Sand_Loop', rn=8),
    'Precipice Blades': dict(h='Sand_Loop', r='Sand_Loop', rn=10),
    # 26 Kamehame Ha x10 (KamehameHa draws the beam, SuperShinyThingy / White Explosion at the end)
    'Hyper Beam': dict(c='Glow', p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy', h2='White Explosion'),
    'Flash Cannon': dict(c='Glow', p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy'),
    'Steel Beam': dict(c='Glow', p='KamehameHa', t='KamehameHa', tstep=90, h='SuperShinyThingy', h2='White Explosion'),
    # 27 Meteorain (FireStone, FireStomp)
    'Draco Meteor': dict(t='FireStone', h='FireStone', h2='FireStomp', r='FireStone', rn=3),
    'Rock Slide': dict(h='FireStone', h2='FireStomp', r='FireStone', rn=5),
    # 28 Ultimate Swords (Blue Explosion, PsiWave, RedDragonFlame, WaterArmor)
    'Sacred Sword': dict(c='WaterArmor', t='PsiWave', h='PsiWave', m=3, h2='Blue Explosion', ds=2400),
    'Psycho Cut': dict(t='PsiWave', h='PsiWave', m=2, h2='Blue Explosion'),
    'Smart Strike': dict(c='WaterArmor', t='RedDragonFlame', h='PsiWave', h2='Blue Explosion', ds=2400),
    # 29 Katon Goukakyuu No Jutsu (KatonGoukaMesshitsu, RedDragonFlame)
    'Fire Blast': dict(c='RedDragonFlame', h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=8),
    'Ember': dict(t='RedDragonFlame', h='KatonGoukaMesshitsu', hs=1.6),
    'Incinerate': dict(t='RedDragonFlame', h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=4),
    # 30 Uchiha Style Halo Dance (FireShockRun1, RedDragonFlame): runs in fire
    'Flame Wheel': dict(p='FireShockRun1', t='RedDragonFlame', h='RedDragonFlame', m=2, ds=2200),
    'Flame Charge': dict(p='FireShockRun1', t='FireShockRun1', h='RedDragonFlame', ds=2200),
    # 31 Kotoamatsukami (GainLife, Kurama Effect, Yellow Goku Effect)
    'Confusion': dict(c='GainLife', h='Yellow Goku Effect', h2='Kurama Effect', h2s=0.6),
    'Extrasensory': dict(c='Kurama Effect', cs=0.8, h='Yellow Goku Effect', h2='GainLife'),
    # 32 Susanoo Tsukumo (Blood_Strike, CenarionFury, Susanoo Tsukumo)
    'Psycho Boost': dict(c='CenarionFury', t='Susanoo Tsukumo', h='Susanoo Tsukumo', m=3, h2='Blood_Strike'),
    'Psystrike': dict(c='CenarionFury', h='Susanoo Tsukumo', m=5, h2='Blood_Strike'),
    # 33 Hyourinmaru (ArcaneExplosion, Hyourinmaru 1, WaterEnchant)
    'Ice Beam': dict(c='WaterEnchant', t='Hyourinmaru 1', h='ArcaneExplosion', h2='Hyourinmaru 1'),
    # 34 Ryuusenka (IceStomp, Hyourinmaru 1, ArcaneExplosion, SpiritArrow_ByEpsilon, WaterEnchant)
    'Freeze Dry': dict(c='WaterEnchant', t='SpiritArrow_ByEpsilon', h='IceStomp', h2='Hyourinmaru 1', h3='AncientExplode_Blue', h3s=0.4),
    'Ice Fang': dict(c='WaterEnchant', t='Hyourinmaru 1', h='Hyourinmaru 1', h2='ArcaneExplosion', ds=2400),
    # 35 Sennen Hyourou (Ice Pillar, IceNova, IceStomp, Cero, ArcaneExplosion)
    'Icicle Crash': dict(h='IceNova', h2='IceStomp', r='Ice Pillar', rn=8),
    # 36 Hyouten Hyakkasou (Hyouten Hyakkasou, IceNova, IceStomp, IceStompMist, Water Float)
    'Blizzard': dict(c='Water Float', h='Hyouten Hyakkasou', h2='IceStompMist', r='IceNova', rn=6),
    # 37 Gunchou Tsurara (GlowLineBlue, ArcaneExplosion, Hyouten Hyakkasou)
    'Icicle Spear': dict(h='GlowLineBlue', h2='ArcaneExplosion', m=4),
    'Ice Shard': dict(h='GlowLineBlue', h2='ArcaneExplosion', m=2),
    # 38 Cero Oscuras (Black Ball, EarthNova, Green Explosion, HarvestLife)
    'Dark Pulse': dict(c='HarvestLife', p='Black Ball', t='HarvestLife', h='EarthNova', h2='Green Explosion'),
    'Shadow Ball': dict(c='HarvestLife', h='Black Ball', h2='EarthNova', h3='Green Explosion'),
    # 39 Vasto Lorde Lightning Blast (Red Cero, ThunderStrike, Red Explosion, Red Damage)
    'Zap Cannon': dict(c='Red Cero', p='Red Cero', t='ThunderStrike', h='Red Explosion', h2='ThunderStrike'),
    'Charge Beam': dict(p='Red Cero', t='ThunderStrike', h='Red Damage', h2='ThunderStrike'),
    # 40 Inugami Guren (RedDragonHead, RedDragonFlame, Lava_Bomd): magma dog head bites
    'Fire Fang': dict(p='RedDragonHead', t='RedDragonFlame', h='RedDragonHead', h2='RedDragonFlame', ds=2400),
    # 41 Meigo (Lava Crack, Lava_Bomd)
    'Flare Blitz': dict(p='RedDragonFlame', t='Lava Crack', ts=0.6, h='Lava Crack', h2='RedDragonFlame'),
    # 42 Ryusei Kazan (Lava_Fall, Slam, Splat)
    'Eruption': dict(h='Lava_Fall', h2='Slam', r='Lava_Fall', rn=4, rs=1.2),
    # 43 Pheasant Beak (ArcaneExplosion)
    'Aurora Beam': dict(t='ArcaneExplosion', ts=0.6, h='ArcaneExplosion'),
    # 44 Ice Time (ArcaneExplosion)
    'Ice Punch': dict(t='ArcaneExplosion', ts=0.4, h='ArcaneExplosion', m=2, ds=2400),
    # 45 Ice Age (IceNova, ArcaneExplosion)
    'Icy Wind': dict(h='IceNova', r='ArcaneExplosion', rn=8),
    'Powder Snow': dict(t='IceNova', h='ArcaneExplosion', h2='IceNova'),
    # 46 Ice Time Capsule (Slam Ice, Getsuga Effect, ArcaneExplosion)
    'Avalanche': dict(t='ArcaneExplosion', ts=0.4, h='Slam Ice', h2='Getsuga Effect', h3='ArcaneExplosion', ds=2400),
    'Ice Spinner': dict(p='Getsuga Effect', ps=0.5, h='Slam Ice', h2='ArcaneExplosion', ds=2400),
    # 47 Tidal Wave (WaterfallFX, WhirlPool, Freezing_Ring2, Air)
    'Whirlpool': dict(t='WaterfallFX', h='WhirlPool', h2='Freezing_Ring2'),
    'Wave Crash': dict(c='Air', p='WaterfallFX', t='WaterfallFX', h='Freezing_Ring2', h2='WhirlPool', h2s=0.7),
    # 48 Tsunami (WhirlPool, WaterBlobs1, Air)
    'Surf': dict(c='Air', h='WhirlPool', h2='WaterBlobs1', r='WaterBlobs1', rn=8),
    'Muddy Water': dict(c='Air', h='WhirlPool', r='WaterBlobs1', rn=8),
    'Origin Pulse': dict(c='Air', t='WaterBlobs1', h='WhirlPool', r='WaterBlobs1', rn=6),
    # 49 Hiken (Cross Flame, Effect_1)
    'Fire Pledge': dict(p='Effect_1', t='Cross Flame', ts=0.6, h='Cross Flame'),
    # 50 Mera Mera No Mi (FireStomp)
    'Lava Plume': dict(h='FireStomp', r='FireStomp', rn=8),
    # 51 Kyokaen (Fire Ace, Flame_Model_2)
    'Inferno': dict(h='Fire Ace', h2='Flame_Model_2', r='Fire Ace', rn=8),
    # 52 Enjomo (Natsu Spell E)
    'Fire Spin': dict(t='Natsu Spell E', h='Natsu Spell E', r='Natsu Spell E', rn=6),
    # 53 Goshikito (Goshikito, White Ring, White Haku, Blood_Strike)
    'X Scissor': dict(c='White Haku', h='Goshikito', h2='White Ring', h3='Blood_Strike', ds=2400),
    # 54 Karyuu No Houkou (Raienryuu no Houkou)
    'Flamethrower': dict(p='Raienryuu no Houkou', t='Raienryuu no Houkou', h='Raienryuu no Houkou'),
    # 55 Guren Karyuu Ken (Flame_Model_2, Wind): flaming fists
    'Fire Punch': dict(p='Flame_Model_2', ps=0.7, t='Wind', h='Flame_Model_2', m=3, ds=2400),
    'Blaze Kick': dict(p='Flame_Model_2', ps=0.7, t='Wind', h='Flame_Model_2', m=2, ds=2400),
    # 56 Metsuryuu Ougi Guren Bakuenjin (Natsu Wing, Natsu Flame 2, Flame_Model_2)
    'Blast Burn': dict(c='Natsu Wing', h='Natsu Flame 2', h2='Flame_Model_2', r='Flame_Model_2', rn=6),
    'Sacred Fire': dict(c='Natsu Wing', t='Flame_Model_2', h='Natsu Flame 2', h2='Flame_Model_2'),
    # 57 Hakuryuu No Houkou (White Effect 1, WhiteShockwave, White Explosion, White Haku, White Spell Aura 1)
    'Dragon Pulse': dict(c='White Spell Aura 1', t='White Effect 1', h='White Explosion', h2='WhiteShockwave'),
    'Dragon Breath': dict(c='White Haku', t='White Effect 1', h='WhiteShockwave', h2='White Explosion', h2s=0.6),
    # 58 Hakuryuu No Holy Buresu (White Holy, WhiteShockwave, Spell W Law)
    'Dazzling Gleam': dict(h='White Holy', h2='Spell W Law', r='WhiteShockwave', rn=6),
    'Moonblast': dict(t='WhiteShockwave', h='White Holy', h2='Spell W Law'),
    # 59 Liberation (Liberation, BigCloudFogBlack, Black Stomp)
    'Snarl': dict(c='Liberation', h='BigCloudFogBlack', h2='Black Stomp', r='Black Stomp', rn=6),
    # 60 Black Hole (GlowBlack, BigCloudFogBlack, BlackSmoke, Liberation)
    'Phantom Force': dict(c='BlackSmoke', p='BigCloudFogBlack', ps=0.6, h='GlowBlack', h2='Liberation'),
    'Shadow Force': dict(c='BlackSmoke', p='BigCloudFogBlack', ps=0.6, h='GlowBlack', h2='Liberation'),
    # 61 Doku Fugu (Doku Fugu, Hydra Damage, PurpleExplosion_2)
    'Sludge Bomb': dict(p='Doku Fugu', h='Hydra Damage', h2='PurpleExplosion_2'),
    'Sludge': dict(p='Doku Fugu', h='Hydra Damage', h2='PurpleExplosion_2', h2s=0.8),
    # 62 Doku Gumo (Doku Gumo 1, Doku Gumo 2)
    'Smog': dict(h='Doku Gumo 2', h2='Doku Gumo 1', r='Doku Gumo 1', rn=4),
    'Clear Smog': dict(h='Doku Gumo 2', h2='Doku Gumo 1', r='Doku Gumo 1', rn=4),
    'Acid Spray': dict(t='Doku Gumo 1', h='Doku Gumo 2', h2='Doku Gumo 1'),
    # 63 Hydra (PurpleExplosion_2, Doku Gumo 1)
    'Sludge Wave': dict(h='PurpleExplosion_2', r='Doku Gumo 1', rn=10),
    'Gunk Shot': dict(t='Doku Gumo 1', h='PurpleExplosion_2', h2='Doku Gumo 1'),
    'Venoshock': dict(h='PurpleExplosion_2', h2='Doku Gumo 1', m=2),
    # 64 Ittouryuu Sanjuuroku Pondo Hou (Pondo Hou, Blue Explosion, Blue Boom, Haki DV)
    'Air Slash': dict(c='Haki DV', cs=0.8, p='Pondo Hou', h='Blue Explosion', h2='Blue Boom', h2s=0.6),
    'Air Cutter': dict(c='Haki DV', cs=0.8, h='Blue Explosion', r='Pondo Hou', rn=6),
    # 65 Santouryuu Kokujou Ou Tatsumaki (HolyTornado, ArcaneTornado, Blood_Strike)
    'Hurricane': dict(h='HolyTornado', r='ArcaneTornado', rn=5, h2='Blood_Strike'),
    'Twister': dict(h='HolyTornado', r='ArcaneTornado', rn=3, h2='Blood_Strike'),
    'Gust': dict(t='ArcaneTornado', ts=0.6, h='HolyTornado'),
    # 66 Ittouryuu Daishinkan (Final Wave Zoro, Zoro Wave, CenarionFury)
    'Leaf Blade': dict(t='Zoro Wave', ts=0.5, h='Final Wave Zoro', h2='CenarionFury', ds=2600),
    'Solar Blade': dict(p='Zoro Wave', ps=0.6, h='Final Wave Zoro', h2='CenarionFury', ds=2600),
    # 67 Tsubaki No Mai (Blood_Strike)
    'Bone Rush': dict(t='Blood_Strike', h='Blood_Strike', m=3),
    'Bonemerang': dict(t='Blood_Strike', h='Blood_Strike', m=2),
}

for _stt, _name, _ms in [
        (1, 'Mokuton Life Energy', ['Giga Drain', 'Mega Drain', 'Absorb']),
        (2, 'Mokuton Hijutsu Jukai Koutan (Update)', ['Grass Pledge', 'Wood Hammer']),
        (4, 'Suiton Mizurappa', ['Water Gun', 'Hydro Pump', 'Water Pulse']),
        (5, 'Suiton Suijinheki', ['Liquidation', 'Aqua Tail']),
        (6, 'Suiton Suiryuu Koubaku', ['Hydro Cannon', 'Waterfall']),
        (7, 'Katon Karyuu Endan (Update)', ['Outrage', 'Dragon Rush']),
        (8, 'Yellow Flash', ['Extreme Speed', 'Quick Attack']),
        (9, 'Omnislash', ['Slash', 'Fury Cutter', 'Double Hit']),
        (10, 'Katon Gouka Mekkyaku', ['Heat Wave', 'Overheat']),
        (11, 'Mokuton Jukai Koutan', ['Frenzy Plant', 'Power Whip']),
        (12, 'Mokuton Kajukai Kourin', ['Petal Dance', 'Petal Blizzard', 'Leaf Storm']),
        (13, 'Amaterasu (Itachi)', ['Burning Jealousy', 'Hex']),
        (14, 'Enton Kagutsuchi', ['Temper Flare', 'Mystical Fire']),
        (15, 'Chidori Nagashi', ['Discharge', 'Spark', 'Thunder Shock']),
        (16, 'Raiton Kirin', ['Thunder', 'Thunderbolt']),
        (18, 'Shinra Tensei', ['Expanding Force', 'Psychic']),
        (19, 'Rain (Update)', ['Weather Ball', 'Water Pledge']),
        (20, 'Excellent Shinra Tensei', ['Judgment', 'Boomburst', 'Hyper Voice']),
        (21, 'Suiton Soodai Kaisaku', ['Water Spout', 'Brine']),
        (22, 'Suiton Dai Bakusui Shouha', ['Bubble Beam', 'Chilling Water']),
        (23, 'Explosive', ['Explosion', 'Self Destruct', 'Misty Explosion']),
        (24, 'Sabaku Taisou', ['Sand Tomb', 'Scorching Sands']),
        (25, 'Ryuusa Bakuryuu', ['Earth Power', 'Earthquake', 'Precipice Blades']),
        (26, 'Kamehame Ha x10', ['Hyper Beam', 'Flash Cannon', 'Steel Beam']),
        (27, 'Meteorain', ['Draco Meteor', 'Rock Slide']),
        (28, 'Ultimate Swords', ['Sacred Sword', 'Psycho Cut', 'Smart Strike']),
        (29, 'Katon Goukakyuu No Jutsu', ['Fire Blast', 'Ember', 'Incinerate']),
        (30, 'Uchiha Style Halo Dance', ['Flame Wheel', 'Flame Charge']),
        (31, 'Kotoamatsukami', ['Confusion', 'Extrasensory']),
        (32, 'Susanoo Tsukumo', ['Psycho Boost', 'Psystrike']),
        (33, 'Hyourinmaru', ['Ice Beam']),
        (34, 'Ryuusenka', ['Freeze Dry', 'Ice Fang']),
        (35, 'Sennen Hyourou', ['Icicle Crash']),
        (36, 'Hyouten Hyakkasou', ['Blizzard']),
        (37, 'Gunchou Tsurara', ['Icicle Spear', 'Ice Shard']),
        (38, 'Cero Oscuras', ['Dark Pulse', 'Shadow Ball']),
        (39, 'Vasto Lorde Lightning Blast', ['Zap Cannon', 'Charge Beam']),
        (40, 'Inugami Guren', ['Fire Fang']),
        (41, 'Meigo', ['Flare Blitz']),
        (42, 'Ryusei Kazan', ['Eruption']),
        (43, 'Pheasant Beak', ['Aurora Beam']),
        (44, 'Ice Time', ['Ice Punch']),
        (45, 'Ice Age', ['Icy Wind', 'Powder Snow']),
        (46, 'Ice Time Capsule', ['Avalanche', 'Ice Spinner']),
        (47, 'Tidal Wave', ['Whirlpool', 'Wave Crash']),
        (48, 'Tsunami', ['Surf', 'Muddy Water', 'Origin Pulse']),
        (49, 'Hiken', ['Fire Pledge']),
        (50, 'Mera Mera No Mi', ['Lava Plume']),
        (51, 'Kyokaen', ['Inferno']),
        (52, 'Enjomo', ['Fire Spin']),
        (53, 'Goshikito', ['X Scissor']),
        (54, 'Karyuu No Houkou', ['Flamethrower']),
        (55, 'Guren Karyuu Ken', ['Fire Punch', 'Blaze Kick']),
        (56, 'Metsuryuu Ougi Guren Bakuenjin', ['Blast Burn', 'Sacred Fire']),
        (57, 'Hakuryuu No Houkou', ['Dragon Pulse', 'Dragon Breath']),
        (58, 'Hakuryuu No Holy Buresu', ['Dazzling Gleam', 'Moonblast']),
        (59, 'Liberation', ['Snarl']),
        (60, 'Black Hole', ['Shadow Force', 'Phantom Force']),
        (61, 'Doku Fugu', ['Sludge Bomb', 'Sludge']),
        (62, 'Doku Gumo', ['Smog', 'Clear Smog', 'Acid Spray']),
        (63, 'Hydra', ['Sludge Wave', 'Gunk Shot', 'Venoshock']),
        (64, 'Ittouryuu Sanjuuroku Pondo Hou', ['Air Slash', 'Air Cutter']),
        (65, 'Santouryuu Kokujou Ou Tatsumaki', ['Hurricane', 'Twister', 'Gust']),
        (66, 'Ittouryuu Daishinkan', ['Leaf Blade', 'Solar Blade']),
        (67, 'Tsubaki No Mai', ['Bone Rush', 'Bonemerang'])]:
    _a(_stt, _name, _ms)

# ---- contact moves: the user dashes to the target (Pokemon "makes contact" moves of this map). Whips hit from
# afar and stay ranged; self-centred stomps (High Jump Kick, Close Combat ... on War Stomp) already hit around the user.
MELEE = set('''Acrobatics|Aerial Ace|Aqua Jet|Aqua Tail|Assurance|Astonish|Avalanche|Bite|Blaze Kick|Body Press|
Body Slam|Bounce|Brave Bird|Breaking Swipe|Brick Break|Brutal Swing|Bug Bite|Bullet Punch|Covet|Crabhammer|
Cross Chop|Cross Poison|Crunch|Crush Claw|Cut|Darkest Lariat|Dig|Dive|Double Edge|Double Hit|Double Kick|
Dragon Ascent|Dragon Claw|Dragon Rush|Dragon Tail|Drain Punch|Drill Peck|Drill Run|Dual Wingbeat|Dynamic Punch|
Extreme Speed|Facade|Fake Out|False Swipe|Feint|Fell Stinger|Fire Fang|Fire Punch|First Impression|Flame Charge|
Flame Wheel|Flare Blitz|Flip Turn|Fly|Force Palm|Foul Play|Fury Attack|Fury Cutter|Fury Swipes|Giga Impact|
Grassy Glide|Hammer Arm|Head Smash|Headbutt|Horn Attack|Hyper Fang|Ice Fang|Ice Punch|Ice Spinner|Iron Head|
Iron Tail|Knock Off|Kowtow Cleave|Lash Out|Last Resort|Leaf Blade|Leech Life|Lick|Liquidation|Low Sweep|Lunge|
Mach Punch|Mega Kick|Mega Punch|Megahorn|Metal Claw|Meteor Mash|Night Slash|Outrage|Payback|Peck|Phantom Force|
Play Rough|Pluck|Poison Fang|Poison Jab|Poison Tail|Pounce|Pound|Psychic Fangs|Pursuit|Quick Attack|Rage|
Rage Fist|Raging Bull|Rapid Spin|Razor Shell|Retaliate|Revenge|Rollout|Sacred Sword|Scratch|Shadow Claw|
Shadow Force|Shadow Punch|Shadow Sneak|Skitter Smack|Slam|Slash|Smart Strike|Solar Blade|Spark|Steel Wing|Stomp|
Storm Throw|Strength|Submission|Sucker Punch|Superpower|Tackle|Take Down|Temper Flare|Thief|Thrash|Throat Chop|
Thunder Fang|Thunder Punch|Trailblaze|Triple Axel|U Turn|Upper Hand|Vice Grip|Vital Throw|Waterfall|Wave Crash|
Wild Charge|Wing Attack|Wood Hammer|Wrap|X Scissor|Zen Headbutt'''.replace('\n', '').split('|'))

DASH_SPEED = 2000.0      # default dash speed of a melee move (game units / s); the move's missile / wave speed follows
DASH_STOP = 90.0         # the dash ends this far from a target unit
# melee move without a 9xHeroDefense effect: dust along the dash, its old missile model bursts on the target
GENERIC_TRAIL = 'war3:Objects\\Spawnmodels\\Undead\\ImpaleTargetDust\\ImpaleTargetDust.mdl'
GENERIC_HIT = 'war3:Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl'

# ---- how big ("epic", v3.4.7 x ~1.4): wanted horizontal radius of each layer, in game units
R_TARGET = 320.0     # impact on a single target
R_PROJ = 150.0       # flying model / aura on a dashing user
R_CAST = 260.0
R_LINE_END = 360.0
AREA_MULT = 1.6      # self / point / nova impact = area x this
TRAIL_MIN = 220.0    # trail effect radius = max(area x 2, this)
RING_FRAC = 0.7      # each ring effect = area x this
SCALE_MIN, SCALE_MAX = 1.2, 8.0
PROJ_MIN, PROJ_MAX = 1.2, 4.5
SMALL_MIN = 0.08     # lowest scale for huge models (rain 4000, splat 2500 ...)
R_UNKNOWN = 150.0    # model radius when the library has none
LIFE_MAX = 4.0       # seconds an impact stays at most
TRAIL_LIFE_MAX = 2.0
TRAIL_STEP = 160.0   # default distance between trail effects
WAVES_MAX = 12       # channel AoE (blizzard base): one impact per wave

# buffs whose target art is the old effect: mapped moves get an art-less copy (new id -> base buff)
BUFF_COPY = {'BEer': 'BP00', 'Bfro': 'BP01', 'BHbd': 'BP02', 'BNbf': 'BP03', 'BEsh': 'BP04', 'BUim': 'BP05',
             'BHtc': 'BP06', 'XHbz': 'XP00'}
