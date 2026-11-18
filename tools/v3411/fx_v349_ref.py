"""v3.4.9 data: effects of WW3/Skill on Pokemon moves, exactly as mapped in Skill_Map_XemTruoc.xlsx (12/11/2026):
one 9xHeroDefense skill -> one Pokemon move (151 rows, 84 of them from the ENG map), built from v3.4.5.
Visual / movement only: damage, range, area, cooldown and mana stay as they are.

Every model was checked before use (analysis/v349_model_check.csv): MDX v800, all textures present and readable,
and a render of the animation the game plays (mdx-m3-viewer, headless). Models in BAD are not used; a move whose
models are all bad keeps its Pokemon art. RADIUS is the horizontal radius measured on that render (95 % of the lit
pixels, top view) and replaces the frame radius of DanhSachHieuUng.csv, which is far off for many ENG models.

SPEC[move] = layers, each a folder name of WW3/Skill/<group>/ ('war3:' = model of the game itself):
  p   projectile caster -> target (ranged) / aura riding on the user during the dash (melee)
  h, h2, h3  impacts (target, line end, caster for self AoE, point for channel AoE)
  t   trail: ranged = along the line or to the target; melee = along the dash path
  r   ring of rn effects around the impact
  c   effect at the user when the move starts, turned towards the target (beams, slashes)
  m   main impact repeated m times
  ps / hs / h2s / h3s / ts / rs / cs  scale override,  ds  dash speed of a melee move
MELEE = column "Phân loại" = "Cận chiến" of the workbook: the user dashes to the target (War Stomp / Thunder Clap
moves already hit around the user and do not dash).
"""

SPEC = {
    'Aerial Ace': dict(c='HolyBomb', p='DivineRage', t='DivineRage', h='HolyBomb', ds=3000),
    'Aeroblast': dict(p='Fuuton Rasen Shuriken 2020', t='WaterAura', ts=0.3, h='Fuuton Rasen Shuriken 2020', h2='WaterAura'),
    'Air Cutter': dict(h='Momoshiki Effect (1)', r='Style Effect Kaido (6)', rn=4),
    'Air Slash': dict(c='Haki DV', p='Pondo Hou', h='Blue Explosion', h2='Blue Boom', h2s=0.5),
    'Aqua Cutter': dict(c='E Tanjiro (5)', p='E Tanjiro (3)', h='E Tanjiro (1)', h2='E Tanjiro (2)', h3='E Tanjiro (4)'),
    'Aqua Jet': dict(p='@Terumi_SP_Sp3', ps=0.5, t='E Tanjiro (2)', h='AquaSpikeVersion2 (ENG)', h2='BD_Goku (6)', h3='Momoshiki Effect (5)'),
    'Aura Sphere': dict(c='Clone', h='Sage Rasengan 2021', h2='Clone'),
    'Aurora Beam': dict(t='ArcaneExplosion', h='ArcaneExplosion'),
    'Avalanche': dict(t='ArcaneExplosion', h='Slam Ice', h2='Getsuga Effect', h3='ArcaneExplosion'),
    'Blast Burn': dict(c='Natsu Wing', h='Natsu Flame 2', h2='Flame_Model_2', r='Flame_Model_2', rn=4),
    'Blaze Kick': dict(c='Bijuu Aura', cs=0.4, p='FireShockRun1', t='DustWave_2021', h='Style Effect Kaido (24)', h2='Daisen Sekai Type 1'),
    'Blizzard': dict(c='Water Float', h='Hyouten Hyakkasou', h2='IceStompMist', h3='IceStomp', r='IceNova', rn=6),
    'Bone Rush': dict(t='Blood_Strike', h='Blood_Strike', m=3),
    'Boomburst': dict(h='Explosion', r='Explosion', rn=6),
    'Brick Break': dict(p='@Rock_Lee_Green_Aura', h='Style Effect Kaido (24)', h2='ShockWave Green', h2s=0.4, h3='SuperBigBombExplosion Green', h3s=0.25),
    'Bulldoze': dict(h='Newgate Style (8)', h2='Newgate Style (2)', r='Newgate Style (6)', rn=6),
    'Bullet Seed': dict(h='Mokuton Sashiki All', hs=0.5, m=3),
    'Burning Jealousy': dict(t='Black Stomp', ts=0.3, h='Enton Honoikazuchi 1', h2='Black Stomp'),
    'Charge Beam': dict(t="Indra's Effect", h="Indra's Effect"),
    'Close Combat': dict(h='GJ Style (5)', r='PVegeta Style (15)', rn=6),
    'Confusion': dict(h='Black_Effect2', h2='Aizen Skill - Kyouka Suigetsu 2'),
    'Crush Claw': dict(t='FInuyasha (3)', h='FInuyasha (14)', hs=0.3, h2='Sage Effect Damage'),
    'Cut': dict(c='RZoro Effect (28)', cs=0.6, h='Uitachi Style (16)', h2='Doku Doku Effect (5)', h3='RZoro Effect (27)', h3s=0.6),
    'Dark Pulse': dict(c='Liberation', t='Black Stomp', ts=0.3, h='BigCloudFogBlack', h2='Black Stomp'),
    'Dazzling Gleam': dict(h='White Holy', h2='Spell W Law', r='WhiteShockwave', rn=6),
    'Discharge': dict(h='EmpBomb', h2='GreatLightning', r='GreatLightning', rn=6),
    'Dive': dict(t='AquaSpikeVersion2 (ENG)', h='AquaSpikeVersion2 (ENG)', r='AquaSpikeVersion2 (ENG)', rn=4),
    'Double Hit': dict(c='Clone', h='Clone', m=2),
    'Double Kick': dict(c='Bijuu Aura', cs=0.4, p='FireShockRun1', h='DustWave_2021', m=2),
    'Draco Meteor': dict(t='FireStone', h='FireStone', h2='FireStomp', r='FireStone', rn=3),
    'Dragon Breath': dict(c='Style Effect Kaido (14)', cs=0.35, p='Style Effect Kaido (13)', ps=1.5, h='Style Effect Kaido (13)', hs=2.0),
    'Dragon Claw': dict(p='Natsu Spell E', ps=0.6, t='SpecialAnimeDustWave', h='Daisen Sekai Type 2', h2='Mokuton Fire', h2s=0.5, h3='Spell W Law'),
    'Dragon Pulse': dict(c='White Spell Aura 1', p='White Haku', t='White Effect 1', h='White Explosion', h2='WhiteShockwave', h2s=0.5),
    'Dragon Rush': dict(p='RedDragonHead', t='RedDragonFlame', h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=4),
    'Dream Eater': dict(h='MS Tsukuyomi #1', h2='MS Tsukuyomi #2'),
    'Dynamic Punch': dict(c='PVegeta Style (15)', p='GJ Style (2)', h='PVegeta Style (16)', h2='GJ Style (5)', h2s=0.5, h3='PVegeta Style (21)'),
    'Earth Power': dict(h='Sand_Loop', r='Sand_Loop', rn=6),
    'Earthquake': dict(h='BY_Wood_Effect_Order_DanGe_DaoGuang_BaoZha_2_2_2', h2='Newgate Style (2)', r='Newgate Style (6)', rn=8),
    'Ember': dict(p='Uitachi Style (21)', h='Uitachi Style (22)'),
    'Energy Ball': dict(h='Green Effect', h2='SuperShinyThingy1'),
    'Eruption': dict(h='Lava_Fall', hs=0.45, h2='Slam', h3='Splat', h3s=0.3),
    'Expanding Force': dict(c='Explosion', h='Explosion'),
    'Explosion': dict(h='A-Bomb', r='A-Bomb', rn=8),
    'Extreme Speed': dict(c='HolyBomb', p='DivineRage', t='DivineRage', h='HolyBomb', ds=3200),
    'Fire Blast': dict(c='RedDragonFlame', h='KatonGoukaMesshitsu', r='RedDragonFlame', rn=8),
    'Fire Fang': dict(p='RedDragonHead', t='RedDragonFlame', h='RedDragonHead', h2='RedDragonFlame', ds=2400),
    'Fire Pledge': dict(p='Effect_1', ps=0.5, h='Effect_1'),
    'Fire Punch': dict(p='Flame_Model_2', ps=0.4, t='Wind', ts=0.5, h='Flame_Model_2', m=3, ds=2400),
    'Fire Spin': dict(t='Natsu Spell E', h='Natsu Spell E', r='Natsu Spell E', rn=6),
    'Flame Charge': dict(p='FireShockRun1', t='FireShockRun1', h='RedDragonFlame', ds=2200),
    'Flame Wheel': dict(p='E Tanjiro (43)', ps=0.35, h='E Tanjiro (43)', h2='E Tanjiro (24)', h2s=0.25, ds=2200),
    'Flamethrower': dict(p='Raienryuu no Houkou', t='Raienryuu no Houkou', h='Raienryuu no Houkou'),
    'Flare Blitz': dict(h='Bijuu Dama 2', hs=0.5),
    'Flash Cannon': dict(c='PVegeta Style (12)', cs=0.25, h='ShockwaveYellow', hs=0.6, h2='Sand Style Mokuton 2'),
    'Focus Blast': dict(p='BD_Goku (26)', h='BD_Goku (32)', h2='BD_Goku (26)'),
    'Force Palm': dict(h='HakkeAura 1', hs=0.5, m=2),
    'Freeze Dry': dict(c='WaterEnchant', t='SpiritArrow_ByEpsilon', h='IceStomp', h2='Hyourinmaru 1', h3='AncientExplode_Blue', h3s=0.5),
    'Frenzy Plant': dict(h='Mokuton Tree 2', h2='Mokuton (2)', r='Mokuton Tree 1', rn=6),
    'Fury Cutter': dict(t='DivineRage', h='DivineRage', m=5, ds=2600),
    'Future Sight': dict(t='BlueDoom (ENG)', h='Lion Fists Crit 1', h2='BlueDoom (ENG)'),
    'Giga Drain': dict(c='CenarionFury', h='CenarionFury', h2='AncientExplode', h2s=0.6),
    'Gunk Shot': dict(p='Red Damage', h='AZ_Fireblue Doku 2', h2='AZ_Storm_Red 2'),
    'Hammer Arm': dict(h='Earth Slam 2020'),
    'Heat Wave': dict(h='A-Bomb', r='A-Bomb', rn=8),
    'Hex': dict(h='Kanzen Eishou Kurohitsugi 1', h2='Kanzen Eishou Kurohitsugi 2'),
    'High Jump Kick': dict(c='@Rock_Lee_Green_Aura', h='Crack Green Mihawk', h2='ShockWave Green', r='Style Effect Kaido (24)', rn=5),
    'Hurricane': dict(h='HolyTornado', h2='Blood_Strike', r='ArcaneTornado', rn=5),
    'Hydro Cannon': dict(t='TidalEruption', h='TidalEruption', r='TidalEruption', rn=4),
    'Hydro Pump': dict(t='BlizzardEruption', ts=0.5, h='WaterBlast', h2='BlizzardEruption'),
    'Hyper Beam': dict(c='Glow', p='KamehameHa', ps=0.4, t='KamehameHa', ts=0.4, tstep=90, h='SuperShinyThingy', h2='White Explosion', h3='IonCannonBlue', h3s=0.5),
    'Hyper Voice': dict(c='Style Effect Kaido (1)', cs=0.5, h='Style Effect Kaido (2)', h2='Style Effect Kaido (4)'),
    'Ice Beam': dict(c='WaterEnchant', t='Hyourinmaru 1', h='ArcaneExplosion', h2='Hyourinmaru 1'),
    'Ice Punch': dict(t='ArcaneExplosion', ts=0.6, h='ArcaneExplosion', m=2, ds=2400),
    'Ice Shard': dict(h='BToshiro (20)', m=2),
    'Ice Spinner': dict(c='BToshiro (26)', cs=0.5, p='BToshiro (5)', ps=0.5, h='BToshiro (59)', h2='BToshiro (20)', h3='BToshiro (37)', h3s=0.3, ds=2400),
    'Icicle Crash': dict(h='IceNova', h2='IceStomp', h3='Cero', r='Ice Pillar', rs=3.0, rn=8),
    'Icicle Spear': dict(h='GlowLineBlue', h2='ArcaneExplosion', m=4),
    'Icy Wind': dict(h='IceNova', r='ArcaneExplosion', rn=8),
    'Incinerate': dict(t='SYamamoto (20)', h='SYamamoto (1)', h2='GJ Style (3)', h3='E Tanjiro (39)', h3s=0.2),
    'Inferno': dict(h='Fire Ace', h2='Flame_Model_2', r='Fire Ace', rn=8),
    'Judgment': dict(c='SuperShinyThingy7', h='ShockwavePurple', r='Missile Black (30)', rn=8),
    'Lava Plume': dict(h='FireStomp', r='FireStomp', rn=6),
    'Leaf Blade': dict(t='Zoro Wave', ts=0.4, h='Final Wave Zoro', h2='CenarionFury', ds=2600),
    'Liquidation': dict(t='AquaSpikeVersion2', ts=0.3, h='AquaSpikeVersion2', r='AquaSpikeVersion2', rn=6),
    'Mega Kick': dict(c='Bijuu Aura', cs=0.4, p='FireShockRun1', h='DustWave_2021', hs=3.0),
    'Misty Explosion': dict(h='Super Big Explosion White 2020'),
    'Moonblast': dict(h='HCifer Style (12)'),
    'Mystical Fire': dict(p='Amaterasu_New', t='Amaterasu_New', h='PurpleExplosion_2', h2='Black Stomp'),
    'Night Slash': dict(h='HCifer Style (25)'),
    'Origin Pulse': dict(c='BD_Goku (16)', cs=0.5, p='BD_Goku (20)', ps=0.5, h='Super Big Explosion Blue 2020', h2='BD_Goku (28)'),
    'Outrage': dict(p='BD_Goku (23)', ps=0.5, h='RZoro Effect (31)'),
    'Overheat': dict(c='Style Effect Kaido (14)', cs=0.35, p='GJ Style (21)', ps=0.4, h='GJ Style (5)', hs=0.6, h2='PVegeta Style (16)', h2s=0.4, h3='PVegeta Style (15)'),
    'Petal Blizzard': dict(c='TheShow', h='Mokuton (2)', r='TheShow', rn=6),
    'Petal Dance': dict(h='BByakuya (30)', h2='BByakuya (59)', h3='BByakuya (51)'),
    'Phantom Force': dict(c='UO Kamai Style 1', h='UO Kamai Style 2', h2='UO Kamai Style 1'),
    'Poison Jab': dict(h='X Sesshomaru (17)', m=3),
    'Power Gem': dict(c='Bankai Aura 2021', t='FInuyasha (4)', h='FInuyasha (10)', h2='FInuyasha (14)', h2s=0.4),
    'Power Whip': dict(t='Sand Style Mokuton 1', ts=0.6, h='Sand Style Mokuton 2', h2='NewBlood'),
    'Psybeam': dict(p='Missile Black (18)', t='Missile Black (1)', h='Missile Black (2)', hs=0.5, h2='Missile Black (5)'),
    'Psychic': dict(c='GainLife', h='Yellow Goku Effect', h2='Kurama Effect'),
    'Psycho Boost': dict(c='CenarionFury', t='Susanoo Tsukumo', ts=0.5, h='Susanoo Tsukumo', m=3, h2='Blood_Strike'),
    'Psycho Cut': dict(p='Missile Black (14)', h='animeslashfinal', h2='ShockwavePurple', h2s=0.4, h3='E Tanjiro (20)', h3s=0.4),
    'Quick Attack': dict(c='AZenitsu (7)', cs=0.3, ds=3200),
    'Rapid Spin': dict(p='Kokuto Arashi Style 2', h='Kokuto Arashi Style 2', m=2),
    'Razor Leaf': dict(c='BByakuya (34)', h='BByakuya (30)', h2='BByakuya (53)', h2s=0.4, r='BByakuya (58)', rs=0.3, rn=4),
    'Razor Shell': dict(t='E Tanjiro (2)', h='E Tanjiro (9)', h2='E Tanjiro (19)'),
    'Revenge': dict(c='GJ Style (20)', cs=0.5, p='GJ Style (25)', ps=0.3, h='GJ Style (8)', h2='PVegeta Style (16)', h2s=0.35, h3='GJ Style (5)', h3s=0.5),
    'Rock Wrecker': dict(h='Chibaku Tensei Sasuke', h2='Aizen Skill - Fragor Effect Damage', r='AZ Air Dust', rs=0.3, rn=4),
    'Sacred Fire': dict(c='SYamamoto (20)', p='FS_Natsu (6)', ps=0.4, h='FS_Natsu (29)', h2='Momoshiki Effect (14)', h2s=0.35, h3='FS_Natsu (16)'),
    'Sacred Sword': dict(c='WaterArmor', t='PsiWave', ts=0.5, h='PsiWave', m=3, h2='Blue Explosion', ds=2400),
    'Sand Tomb': dict(t='Sand_New_Spell', ts=0.6, h='Sand_Effect', h2='SandAura'),
    'Scorching Sands': dict(t='Sand Slash', h='Sand_New_Spell', h2='SandAura'),
    'Self Destruct': dict(h='DON Flame New 2020', r='DON Flame New 2020', rn=6),
    'Shadow Ball': dict(c='HarvestLife', h='Black Ball', h2='EarthNova', h2s=0.5, h3='Green Explosion'),
    'Shock Wave': dict(t="Indra's Effect", h='Lightning Explosion 2020', h2="Dust Indra's Slyte 1"),
    'Slash': dict(c='FInuyasha (17)', t='FInuyasha (4)', h='FInuyasha (45)', m=2, h2='FInuyasha (47)', h2s=0.6, h3='Aizen Effect Damage', h3s=0.5, ds=2600),
    'Sludge Bomb': dict(p='Doku Fugu', h='Hydra Damage', h2='PurpleExplosion_2'),
    'Sludge Wave': dict(h='PurpleExplosion_2', r='Doku Gumo 1', rn=10),
    'Smog': dict(p='Doku Gumo 2', h='Doku Gumo 2', h2='Doku Gumo 1'),
    'Snarl': dict(h='Style Effect Kaido (3)', r='Red Lightning Haki', rn=5),
    'Solar Beam': dict(t='ShockwaveYellow', ts=0.25, h='Empyrean Nova Classic', h2='ShockwaveYellow', h2s=0.6),
    'Solar Blade': dict(c='RZoro Effect (23)', cs=0.5, ds=2600),
    'Spacial Rend': dict(c='FInuyasha (18)', p='FInuyasha (4)', t='Style Effect Kaido (27)', ts=0.5, h='FInuyasha (29)', h2='FInuyasha (36)', h3='Aizen Effect Damage', h3s=0.5),
    'Spark': dict(p='EmpBomb', ps=0.6, h='Nagashi 2020 Style 1', hs=0.25, h2='EmpBomb', ds=2600),
    'Sucker Punch': dict(t='BByakuya (34)', h='BByakuya (50)', h2='BByakuya (27)'),
    'Supercell Slam': dict(h='Effect AZ Tornado Shock', hs=0.5, h2='Getsuga Gran Rey Cero 2', r='Style Effect Kaido (5)', rn=6),
    'Surf': dict(c='Air', h='WhirlPool', h2='WaterBlobs1', r='WaterBlobs1', rn=8),
    'Swift': dict(h='Uitachi Style (7)', h2='Uitachi Style (28)', h2s=0.4),
    'Temper Flare': dict(p='Natsu Spell E', ps=0.6, h='Mokuton Fire', hs=0.5, h2='Natsu Spell E'),
    'Thrash': dict(t='RZoro Effect (14)', h='RZoro Effect (33)', h2='Empyrean Nova Classic', h3='RZoro Effect (31)', r='RZoro Effect (21)', rn=4),
    'Thunder': dict(h='GreatLightning', h2='LightningBoom', r='GreatLightning', rn=6),
    'Thunder Punch': dict(p='EmpBomb', ps=0.6, h='BlackChidori Style 2', h2='EmpBomb', ds=2600),
    'Thunder Shock': dict(h='Momoshiki Effect (3)', h2='Nagashi 2020 Style 2'),
    'Thunderbolt': dict(t="Indra's Effect", h="Dust Indra's Slyte 1", h2='Nagashi 2020 Style 2'),
    'Twister': dict(h='Momoshiki Effect (1)', r='Style Effect Kaido (20)', rn=4),
    'Upper Hand': dict(c='PVegeta Style (15)', h='GJ Style (8)', h2='Sengoku Effect Spell (10)', h3='Momoshiki Effect (14)', h3s=0.3),
    'Vacuum Wave': dict(t='Danku Dust', ts=0.4, h='Sengoku Effect Spell (4)', h2='Sengoku Effect Spell (8)', h3='Sengoku Effect Spell (11)'),
    'Venoshock': dict(p='Doku Doku Effect (2)', h='Doku Doku Effect (6)', h2='Doku Doku Effect (1)'),
    'Vine Whip': dict(c='X Sesshomaru (3)', cs=0.4, h='Style Effect Kaido (20)'),
    'Water Gun': dict(t="Shiva's Wrath (ENG)", ts=0.5, h="Shiva's Wrath (ENG)"),
    'Water Pulse': dict(p='BlueBall', ps=0.35, h='BlueBall'),
    'Water Spout': dict(h='BlizzardEruption', r='BlizzardEruption', rn=6),
    'Waterfall': dict(t='E Tanjiro (2)', h='E Tanjiro (11)', h2='E Tanjiro (19)', h3='E Tanjiro (10)', h3s=0.3),
    'Wave Crash': dict(p='E Tanjiro (6)', ps=0.4, t='E Tanjiro (2)', h='E Tanjiro (19)'),
    'Weather Ball': dict(h='AnimatedEnviromentalEffectRain', hs=0.25, h2='WaterBlobs1', r='WaterBlobs1', rn=6),
    'Whirlpool': dict(c='Air', t='WaterfallFX', h='WhirlPool', h2='Freezing_Ring2'),
    'Wild Charge': dict(t='RZoro Effect (6)', ts=0.6, h='RZoro Effect (6)'),
    'Wood Hammer': dict(t='Mokuton Tree 1', h='Mokuton (2)', h2='Mokuton Tree 1'),
    'X Scissor': dict(c='White Haku', h='Goshikito', h2='White Ring', h3='Blood_Strike', ds=2400),
    'Zap Cannon': dict(c='Red Cero', p='Red Damage', t='ThunderStrike', ts=0.5, h='Red Explosion', h2='ThunderStrike'),
}

# models not used after the check: folder -> reason (Vietnamese, goes to the report)
BAD = {
    "Cross Flame": "render thử không hiện gì ở mọi animation",
    "GlowBlack": "render thử không hiện gì ở mọi animation",
    "Uitachi Style (18)": "gần như không hiện (dưới 0,2% khung hình)",
    "Uitachi Style (17)": "chỉ vài mảnh đen rời rạc, gần như không thấy",
    "Lava Crack": "không render thử được (model gọi hiệu ứng phụ của game), chưa xác nhận",
    "BByakuya (37)": "là model nhân vật, không phải hiệu ứng",
    "Lava_Bomd": "chỉ là một chấm rất nhỏ, khung model lỗi (bán kính vô cực)",
    "BlackChidori": "gần như không hiện (dưới 0,3% khung hình)",
    "Style Effect Kaido (17)": "gần như không hiện (dưới 0,4% khung hình)",
    "UItachi_Susanoo_S1": "model triệu hồi (Susanoo), hiển thị không đúng khi dùng làm hiệu ứng"
}

# measured horizontal radius at scale 1 (render, animation the game plays)
RADIUS = {
"Mokuton Tree 2": 373,
"A-Bomb": 663,
"Amaterasu_New": 138,
"AncientExplode": 497,
"AncientExplode_Blue": 497,
"AquaSpikeVersion2": 524,
"ArcaneExplosion": 193,
"ArcaneTornado": 235,
"BigCloudFogBlack": 290,
"Bijuu Dama 2": 884,
"Black Ball": 110,
"Black Stomp": 663,
"BlackSmoke": 248,
"BlizzardEruption": 400,
"Blood_Strike": 193,
"Blue Boom": 524,
"Blue Explosion": 221,
"BlueBall": 497,
"CenarionFury": 248,
"Cero": 359,
"Clone": 152,
"DivineRage": 138,
"Doku Fugu": 124,
"Doku Gumo 1": 386,
"Doku Gumo 2": 221,
"EarthNova": 773,
"Effect_1": 290,
"EmpBomb": 166,
"Enton Honoikazuchi 1": 207,
"Explosion": 276,
"Final Wave Zoro": 345,
"Fire Ace": 152,
"FireShockRun1": 207,
"FireStomp": 718,
"FireStone": 607,
"Flame_Model_2": 442,
"Freezing_Ring2": 262,
"GainLife": 166,
"Getsuga Effect": 179,
"Glow": 41,
"Goshikito": 331,
"GreatLightning": 331,
"Green Explosion": 221,
"Haki DV": 179,
"HarvestLife": 166,
"HolyBomb": 276,
"HolyTornado": 262,
"Hydra Damage": 221,
"Hyourinmaru 1": 110,
"Hyouten Hyakkasou": 317,
"Ice Pillar": 69,
"IceNova": 317,
"IceStomp": 939,
"IceStompMist": 442,
"Indra's Effect": 193,
"IonCannonBlue": 552,
"KamehameHa": 442,
"KatonGoukaMesshitsu": 386,
"Kurama Effect": 235,
"Lava_Bomd": 41,
"Lava_Fall": 1491,
"Liberation": 83,
"LightningBoom": 262,
"Mokuton (2)": 304,
"Mokuton Tree 1": 373,
"Natsu Flame 2": 248,
"Natsu Spell E": 262,
"Natsu Wing": 400,
"NewBlood": 276,
"Pondo Hou": 110,
"PsiWave": 359,
"PurgeBuffTarget": 83,
"PurpleExplosion_2": 221,
"Raienryuu no Houkou": 124,
"Red Cero": 276,
"Red Damage": 110,
"Red Explosion": 221,
"RedDragonFlame": 166,
"RedDragonHead": 166,
"SandAura": 290,
"Sand_Effect": 290,
"Sand_Loop": 607,
"Sand_New_Spell": 345,
"ShockwaveYellow": 607,
"Slam": 193,
"Slam Ice": 455,
"SpecialAnimeDustWave": 166,
"Spell W Law": 179,
"SpiritArrow_ByEpsilon": 41,
"Splat": 1491,
"SuperShinyThingy": 455,
"Susanoo Tsukumo": 428,
"TheShow": 97,
"ThunderStrike": 497,
"TidalEruption": 290,
"Water Float": 331,
"WaterArmor": 124,
"WaterAura": 552,
"WaterBlast": 152,
"WaterBlobs1": 83,
"WaterEnchant": 166,
"WaterfallFX": 235,
"WhirlPool": 607,
"White Effect 1": 179,
"White Explosion": 221,
"White Haku": 110,
"White Holy": 455,
"White Ring": 248,
"White Spell Aura 1": 276,
"WhiteShockwave": 773,
"Wind": 359,
"Yellow Goku Effect": 235,
"Zoro Wave": 442,
"@Rock_Lee_Green_Aura": 152,
"@Terumi_SP_Sp3": 442,
"AZ Air Dust": 994,
"AZ_Fireblue Doku 2": 428,
"AZ_Storm_Red 2": 607,
"AZenitsu (7)": 3682,
"Aizen Effect Damage": 524,
"Aizen Skill - Fragor Effect Damage": 235,
"Aizen Skill - Kyouka Suigetsu 2": 41,
"AquaSpikeVersion2 (ENG)": 524,
"BByakuya (27)": 442,
"BByakuya (30)": 939,
"BByakuya (34)": 97,
"BByakuya (37)": 97,
"BByakuya (42)": 1325,
"BByakuya (50)": 386,
"BByakuya (51)": 262,
"BByakuya (53)": 773,
"BByakuya (58)": 773,
"BByakuya (59)": 828,
"BD_Goku (16)": 1546,
"BD_Goku (20)": 552,
"BD_Goku (26)": 262,
"BD_Goku (28)": 317,
"BD_Goku (32)": 442,
"BD_Goku (6)": 317,
"BToshiro (20)": 386,
"BToshiro (26)": 497,
"BToshiro (37)": 994,
"BToshiro (5)": 290,
"BToshiro (59)": 262,
"BY_Wood_Effect_Order_DanGe_DaoGuang_BaoZha_2_2_2": 663,
"Bankai Aura 2021": 248,
"Bijuu Aura": 552,
"BlackChidori": 55,
"BlackChidori Style 2": 483,
"Black_Effect2": 828,
"BlueDoom (ENG)": 262,
"Chibaku Tensei Sasuke": 1491,
"Crack Green Mihawk": 179,
"DON Flame New 2020": 317,
"Daisen Sekai Type 1": 359,
"Daisen Sekai Type 2": 414,
"Danku Dust": 345,
"Doku Doku Effect (1)": 221,
"Doku Doku Effect (2)": 179,
"Doku Doku Effect (5)": 276,
"Doku Doku Effect (6)": 373,
"Dust Indra's Slyte 1": 221,
"DustWave_2021": 110,
"E Tanjiro (1)": 235,
"E Tanjiro (10)": 1988,
"E Tanjiro (11)": 469,
"E Tanjiro (19)": 552,
"E Tanjiro (2)": 221,
"E Tanjiro (20)": 773,
"E Tanjiro (24)": 1767,
"E Tanjiro (3)": 110,
"E Tanjiro (39)": 1657,
"E Tanjiro (4)": 124,
"E Tanjiro (43)": 607,
"E Tanjiro (5)": 207,
"E Tanjiro (6)": 663,
"E Tanjiro (9)": 235,
"Earth Slam 2020": 386,
"Effect AZ Tornado Shock": 828,
"Empyrean Nova Classic": 483,
"FInuyasha (10)": 262,
"FInuyasha (14)": 1325,
"FInuyasha (17)": 138,
"FInuyasha (18)": 166,
"FInuyasha (29)": 607,
"FInuyasha (3)": 345,
"FInuyasha (36)": 331,
"FInuyasha (4)": 69,
"FInuyasha (45)": 248,
"FInuyasha (46)": 248,
"FInuyasha (47)": 511,
"FInuyasha (48)": 497,
"FS_Natsu (16)": 469,
"FS_Natsu (29)": 607,
"FS_Natsu (6)": 663,
"Fuuton Rasen Shuriken 2020": 193,
"GJ Style (2)": 55,
"GJ Style (20)": 524,
"GJ Style (21)": 524,
"GJ Style (25)": 497,
"GJ Style (3)": 386,
"GJ Style (5)": 773,
"GJ Style (8)": 345,
"Getsuga Gran Rey Cero 2": 607,
"Green Effect": 290,
"HCifer Style (12)": 607,
"HCifer Style (25)": 290,
"HakkeAura 1": 773,
"Kanzen Eishou Kurohitsugi 1": 386,
"Kanzen Eishou Kurohitsugi 2": 207,
"Kokuto Arashi Style 2": 235,
"Lightning Explosion 2020": 359,
"Lion Fists Crit 1": 828,
"MS Tsukuyomi #1": 400,
"MS Tsukuyomi #2": 373,
"Missile Black (1)": 69,
"Missile Black (14)": 248,
"Missile Black (18)": 193,
"Missile Black (2)": 773,
"Missile Black (30)": 262,
"Missile Black (5)": 442,
"Mokuton Fire": 718,
"Mokuton Sashiki All": 828,
"Momoshiki Effect (1)": 235,
"Momoshiki Effect (14)": 1215,
"Momoshiki Effect (3)": 207,
"Momoshiki Effect (5)": 304,
"Nagashi 2020 Style 1": 2025,
"Nagashi 2020 Style 2": 317,
"Newgate Style (2)": 497,
"Newgate Style (6)": 193,
"Newgate Style (8)": 331,
"Newgate Style (9)": 248,
"PVegeta Style (12)": 8100,
"PVegeta Style (15)": 428,
"PVegeta Style (16)": 994,
"PVegeta Style (21)": 138,
"RZoro Effect (14)": 235,
"RZoro Effect (21)": 235,
"RZoro Effect (23)": 884,
"RZoro Effect (27)": 773,
"RZoro Effect (28)": 994,
"RZoro Effect (31)": 359,
"RZoro Effect (32)": 1546,
"RZoro Effect (33)": 552,
"RZoro Effect (6)": 276,
"Red Lightning Haki": 442,
"SYamamoto (1)": 331,
"SYamamoto (20)": 345,
"Sage Effect Damage": 524,
"Sage Rasengan 2021": 41,
"Sand Slash": 193,
"Sand Style Mokuton 1": 262,
"Sand Style Mokuton 2": 359,
"Sengoku Effect Spell (10)": 607,
"Sengoku Effect Spell (11)": 497,
"Sengoku Effect Spell (4)": 552,
"Sengoku Effect Spell (8)": 304,
"Shiva's Wrath (ENG)": 248,
"ShockWave Green": 773,
"ShockwavePurple": 773,
"Solar_Force_Explosion": 1104,
"Style Effect Kaido (1)": 718,
"Style Effect Kaido (13)": 994,
"Style Effect Kaido (14)": 2761,
"Style Effect Kaido (17)": 207,
"Style Effect Kaido (2)": 400,
"Style Effect Kaido (20)": 276,
"Style Effect Kaido (24)": 386,
"Style Effect Kaido (27)": 373,
"Style Effect Kaido (3)": 828,
"Style Effect Kaido (4)": 1104,
"Style Effect Kaido (5)": 235,
"Style Effect Kaido (6)": 179,
"Super Big Explosion Blue 2020": 1270,
"Super Big Explosion White 2020": 884,
"SuperBigBombExplosion Green": 1270,
"SuperShinyThingy1": 442,
"SuperShinyThingy7": 442,
"UO Kamai Style 1": 469,
"UO Kamai Style 2": 331,
"Uitachi Style (16)": 442,
"Uitachi Style (17)": 138,
"Uitachi Style (21)": 41,
"Uitachi Style (22)": 262,
"Uitachi Style (28)": 884,
"Uitachi Style (7)": 663,
"X Sesshomaru (17)": 179,
"X Sesshomaru (3)": 1104,
"animeslashfinal": 166,
"BD_Goku (23)": 718,
"UItachi_Susanoo_S1": 83
}

# move -> (asset column, real skill) of the workbook
ASSET = {
"Aerial Ace": [
"Tobirama – Hiraishin Giri",
"Hiraishin Giri"
],
"Aeroblast": [
"Naruto – Fuuton: Rasenshuriken",
"Fuuton: Rasenshuriken (A0EU, map ENG)"
],
"Air Cutter": [
"Kaido – Kaifu",
"Kaifu (A135, map ENG)"
],
"Air Slash": [
"Zorro – Q",
"Ittouryuu Sanjuuroku Pondo Hou (A06W)"
],
"Aqua Cutter": [
"Tanjiro – Ni no Kata: Mizu Guruma",
"Ni no Kata: Mizu Guruma (A17O, map ENG)"
],
"Aqua Jet": [
"Tanjiro – Shichi no Kata: Shizuku Hamon Tsuki",
"Shichi no Kata: Shizuku Hamon Tsuki (A17P, map ENG)"
],
"Aura Sphere": [
"Naruto – Senpou: Oodama Rasengan",
"Senpou: Oodama Rasengan (A004, map ENG)"
],
"Aurora Beam": [
"Aokiji – Q",
"Pheasant Beak (A0BB)"
],
"Avalanche": [
"Aokiji – Ice Time Capsule",
"Ice Time Capsule (A0HK)"
],
"Blast Burn": [
"Natsu – R",
"Metsuryuu Ougi Guren Bakuenjin (A0F7)"
],
"Blaze Kick": [
"Sanji – Diable Jambe: Mouton Shot",
"Diable Jambe: Mouton Shot (A0VA, map ENG)"
],
"Blizzard": [
"Toshiro – D",
"Hyouten Hyakkasou (A0LW)"
],
"Bone Rush": [
"Kimimaro – Tsubaki No Mai",
"Tsubaki No Mai (A064)"
],
"Boomburst": [
"Pain – R",
"Excellent Shinra Tensei (A00A)"
],
"Brick Break": [
"Might Guy – Konoha Kaigansho",
"Konoha Kaigansho (A0TC, map ENG)"
],
"Bulldoze": [
"Edward Newgate – Kaishin",
"Kaishin (A0B1, map ENG)"
],
"Bullet Seed": [
"Tobi – Mokuton: Sashiki no Jutsu",
"Mokuton: Sashiki no Jutsu (A0S4, map ENG)"
],
"Burning Jealousy": [
"Itachi – R",
"Amaterasu (A05N)"
],
"Charge Beam": [
"Enel – El Thor",
"El Thor (A0W4, map ENG)"
],
"Close Combat": [
"Jiren – Infinity Rush",
"Infinity Rush (A01U, map ENG)"
],
"Confusion": [
"Aizen – Shikai: Kyouka Suigetsu",
"Shikai: Kyouka Suigetsu (A0YE, map ENG)"
],
"Crush Claw": [
"Inuyasha – Sankon Tessou",
"Sankon Tessou (A19U, map ENG)"
],
"Cut": [
"Zorro – Ittoryuu Iai: Shi - Shishi Sonson",
"Ittoryuu Iai: Shi - Shishi Sonson (A0IZ, map ENG)"
],
"Dark Pulse": [
"Teach – W",
"Liberation (A0DO)"
],
"Dazzling Gleam": [
"Sting – R",
"Hakuryuu No Holy Buresu (A0GM)"
],
"Discharge": [
"Sasuke – W",
"Chidori Nagashi (A0AE)"
],
"Dive": [
"Kisame – Suiton Goshokuzame",
"Suiton Goshokuzame (A00N, map ENG)"
],
"Double Hit": [
"Naruto – E",
"Kage Bunshin No Jutsu (A007)"
],
"Double Kick": [
"Sanji – Poêle à Frire: Spectre",
"Poêle à Frire: Spectre (A0VB, map ENG)"
],
"Draco Meteor": [
"Cloud – Meteorain",
"Meteorain (A0DY)"
],
"Dragon Breath": [
"Kaido – Bolo Breath",
"Bolo Breath (A139, map ENG)"
],
"Dragon Claw": [
"Sabo – Ryu No Kagizume",
"Ryu No Kagizume (A0PW, map ENG)"
],
"Dragon Pulse": [
"Sting – Q",
"Hakuryuu No Houkou (A0GH)"
],
"Dragon Rush": [
"Sarutobi – Katon Karyuu Endan",
"Katon Karyuu Endan"
],
"Dream Eater": [
"Itachi – Tsukuyomi",
"Tsukuyomi (A05O, map ENG)"
],
"Dynamic Punch": [
"Jiren – Power Impact",
"Power Impact (A01R, map ENG)"
],
"Earth Power": [
"Gaara – D",
"Ryuusa Bakuryuu (A04L)"
],
"Earthquake": [
"Edward Newgate – Gura Gura No Mi",
"Gura Gura No Mi (A0AY, map ENG)"
],
"Ember": [
"Itachi – Katon: Housenka Tsumabeni",
"Katon: Housenka Tsumabeni (A08N, map ENG)"
],
"Energy Ball": [
"Broly – Eraser Cannon",
"Eraser Cannon (A0OL, map ENG)"
],
"Eruption": [
"Akainu – D",
"Ryusei Kazan (A0AT)"
],
"Expanding Force": [
"Pain – W",
"Shinra Tensei (A009)"
],
"Explosion": [
"Deidra – E",
"Explosive (A06I)"
],
"Extreme Speed": [
"Minato – Q",
"Yellow Flash (A01P)"
],
"Fire Blast": [
"Shisui – Q",
"Katon Goukakyuu No Jutsu (A0K1)"
],
"Fire Fang": [
"Akainu – Q",
"Inugami Guren (A0AG)"
],
"Fire Pledge": [
"D Ace – Q",
"Hiken (A047)"
],
"Fire Punch": [
"Natsu – W",
"Guren Karyuu Ken (A0F9)"
],
"Fire Spin": [
"D Ace – Enjomo",
"Enjomo (A0HG)"
],
"Flame Charge": [
"Shisui – E",
"Uchiha Style Halo Dance (A0K3)"
],
"Flame Wheel": [
"Tanjiro – Hinokami Kagura: Kasha",
"Hinokami Kagura: Kasha (A188, map ENG)"
],
"Flamethrower": [
"Natsu – Q",
"Karyuu No Houkou (A0FA)"
],
"Flare Blitz": [
"Akainu – E",
"Meigo (A0AU)"
],
"Flash Cannon": [
"Vegeta – Final Flash",
"Final Flash (A15B, map ENG)"
],
"Focus Blast": [
"Goku – Genki Dama",
"Genki Dama (A0CK, map ENG)"
],
"Force Palm": [
"Hinata – Juukenhou Hakke Sanjuu Ni Shou",
"Juukenhou Hakke Sanjuu Ni Shou (A06O, map ENG)"
],
"Freeze Dry": [
"Toshiro – W",
"Ryuusenka (A0LU)"
],
"Frenzy Plant": [
"Hashirama – Mokuton Hijustsu Jukai Koutan",
"Mokuton Hijutsu Jukai Koutan"
],
"Fury Cutter": [
"Minato – W",
"Omnislash (A02J)"
],
"Future Sight": [
"Itachi – Izanami",
"Izanami (A0JP, map ENG)"
],
"Giga Drain": [
"Hashirama – E",
"Mokuton Life Energy (A090)"
],
"Gunk Shot": [
"Magellan – Jigoku no Shinpan",
"Jigoku no Shinpan (A118, map ENG)"
],
"Hammer Arm": [
"Broly – Bloody Smash",
"Bloody Smash (A0ON, map ENG)"
],
"Heat Wave": [
"Madara – Q",
"Katon Gouka Mekkyaku (A018)"
],
"Hex": [
"Aizen – Kanzen Eishou: Kurohitsugi",
"Kanzen Eishou: Kurohitsugi (A0YR, map ENG)"
],
"High Jump Kick": [
"Might Guy – Dynamic Entry",
"Dynamic Entry (A0TB, map ENG)"
],
"Hurricane": [
"Zorro – D",
"Santouryuu Kokujou Ou Tatsumaki (A0B0)"
],
"Hydro Cannon": [
"Tobirama – Suiton Suiryuu Koubaku",
"Suiton Suiryuu Koubaku (A0CE)"
],
"Hydro Pump": [
"Tobirama – Q",
"Suiton Mizurappa (A01B)"
],
"Hyper Beam": [
"Goku – Kamehame Ha x10",
"Kamehame Ha x10 (A0CK)"
],
"Hyper Voice": [
"Kaido – Daihoukou",
"Daihoukou (A12V, map ENG)"
],
"Ice Beam": [
"Toshiro – Q",
"Hyourinmaru (A0LT)"
],
"Ice Punch": [
"Aokiji – W",
"Ice Time (A0BX)"
],
"Ice Shard": [
"Toshiro – Shinkuu Hyoujin",
"Shinkuu Hyoujin (A0NX, map ENG)"
],
"Ice Spinner": [
"Toshiro – Hyouryuu Senbi",
"Hyouryuu Senbi (A0LY, map ENG)"
],
"Icicle Crash": [
"Toshiro – R",
"Sennen Hyourou (A0LV)"
],
"Icicle Spear": [
"Toshiro – Gunchou Tsurara",
"Gunchou Tsurara (A0LZ)"
],
"Icy Wind": [
"Aokiji – R",
"Ice Age (A0BV)"
],
"Incinerate": [
"Yamamoto – Gotei 13: Ryuujin Jakka: Taimatsu",
"Gotei 13: Ryuujin Jakka: Taimatsu (A190, map ENG)"
],
"Inferno": [
"D Ace – R",
"Kyokaen (A0AI)"
],
"Judgment": [
"Zamasu – Shinbatsu Shikkou",
"Shinbatsu Shikkou (A0OB, map ENG)"
],
"Lava Plume": [
"D Ace – E",
"Mera Mera No Mi (A0AK)"
],
"Leaf Blade": [
"Zorro – Ittouryuu Daishinkan",
"Ittouryuu Daishinkan (A0FM)"
],
"Liquidation": [
"Tobirama – W",
"Suiton Suijinheki (A01A)"
],
"Mega Kick": [
"Sanji – Flanchet Strike",
"Flanchet Strike (A0V7, map ENG)"
],
"Misty Explosion": [
"Deidara – Kibaku Nendo C4 Karura",
"Kibaku Nendo C4 Karura (A0IE, map ENG)"
],
"Moonblast": [
"Ulquiorra – Luz de la Luna",
"Luz de la Luna (A0HT, map ENG)"
],
"Mystical Fire": [
"Sasuke – Q",
"Enton Kagutsuchi (A046)"
],
"Night Slash": [
"Ichigo – Mugetsu",
"Mugetsu (A0LE, map ENG)"
],
"Origin Pulse": [
"Goku – Kamehame Ha",
"Kamehame Ha (A05F, map ENG)"
],
"Outrage": [
"Goku – Ryuu Ken",
"Ryuu Ken (A06L, map ENG)"
],
"Overheat": [
"Jiren – Overheat Magnetron",
"Overheat Magnetron (A02Q, map ENG)"
],
"Petal Blizzard": [
"Madara – Mokuton Kajukai Kourin",
"Mokuton Kajukai Kourin (A0BJ)"
],
"Petal Dance": [
"Byakuya – Senbon Zakura Kageyoshi: Senbon Zakura",
"Senbon Zakura Kageyoshi: Senbon Zakura (A1DO, map ENG)"
],
"Phantom Force": [
"Tobi – Kamui",
"Kamui (A0S5, map ENG)"
],
"Poison Jab": [
"Sesshomaru – Dokkasou",
"Dokkasou (A1C5, map ENG)"
],
"Power Gem": [
"Inuyasha – Kongou Souha",
"Kongou Souha (A1A1, map ENG)"
],
"Power Whip": [
"Hashirama – Mokuton Hotei no Jutsu",
"Mokuton Hotei no Jutsu (A090, map ENG)"
],
"Psybeam": [
"Goku Black – Black Kamehame Ha",
"Black Kamehame Ha (A0LM, map ENG)"
],
"Psychic": [
"Shisui – R",
"Kotoamatsukami (A0K4)"
],
"Psycho Boost": [
"Shisui – Susanoo Tsukumo",
"Susanoo Tsukumo (A0K6)"
],
"Psycho Cut": [
"Goku Black – Shin Retsuzan",
"Shin Retsuzan (A0LO, map ENG)"
],
"Quick Attack": [
"Zenitsu – Ichi no Kata: Hekireki Issen - Shinsoku",
"Ichi no Kata: Hekireki Issen - Shinsoku (A1BG, map ENG)"
],
"Rapid Spin": [
"Edward Newgate – Naginata Senkai",
"Naginata Senkai (A148, map ENG)"
],
"Razor Leaf": [
"Byakuya – Senbon Zakura Kageyoshi: Senbon Zakura Kageyoshi: Kasan",
"Senbon Zakura Kageyoshi: Senbon Zakura Kageyoshi: Kasan (A1DQ, map ENG)"
],
"Razor Shell": [
"Tanjiro – Roku no Kata: Nejire Uzu",
"Roku no Kata: Nejire Uzu (A17R, map ENG)"
],
"Revenge": [
"Jiren – Counter Impact",
"Counter Impact (A02M, map ENG)"
],
"Rock Wrecker": [
"Madara – Tengai Ryuusei",
"Tengai Ryuusei (A100, map ENG)"
],
"Sacred Fire": [
"Yamamoto – Zanka no Tachi: Hado #96: Itto Kasou",
"Zanka no Tachi: Hado #96: Itto Kasou (A191, map ENG)"
],
"Sacred Sword": [
"Cloud – Ultimate Swords",
"Ultimate Swords (A0CF)"
],
"Sand Tomb": [
"Gaara – R",
"Sabaku Taisou (A04E)"
],
"Scorching Sands": [
"Gaara – Sabaku Sou Taisou",
"Sabaku Sou Taisou (A08V, map ENG)"
],
"Self Destruct": [
"Deidara – Jibaku Bunshin",
"Jibaku Bunshin (A06H, map ENG)"
],
"Shadow Ball": [
"Ulquiorra – R",
"Cero Oscuras (A0HV)"
],
"Shadow Force": [
"Teach – R",
"Black Hole (A0DQ)"
],
"Shock Wave": [
"Enel – Kari",
"Kari (A0VV, map ENG)"
],
"Slash": [
"Inuyasha – Tessaiga Zangeki",
"Tessaiga Zangeki (A19W, map ENG)"
],
"Sludge Bomb": [
"Magellan – Q",
"Doku Fugu (A0JU)"
],
"Sludge Wave": [
"Magellan – R",
"Hydra (A0HE)"
],
"Smog": [
"Magellan – W",
"Doku Gumo (A0JV)"
],
"Snarl": [
"Kaido – Haoshoku Haki",
"Haoshoku Haki (A12U, map ENG)"
],
"Solar Beam": [
"Vegeta – God Final Flash",
"God Final Flash (A15K, map ENG)"
],
"Solar Blade": [
"Mihawk – Busoshoku Haki Form: Sekaiichi no Zangeki",
"Busoshoku Haki Form: Sekaiichi no Zangeki (A0SR, map ENG)"
],
"Spacial Rend": [
"Inuyasha – Meidou Zangetsuha",
"Meidou Zangetsuha (A1A4, map ENG)"
],
"Spark": [
"Sasuke – Chidori Nagashi",
"Chidori Nagashi (A0CR, map ENG)"
],
"Sucker Punch": [
"Byakuya – Shuppo: Senka",
"Shuppo: Senka (A1E4, map ENG)"
],
"Supercell Slam": [
"Kaido – Raimei Hakke",
"Raimei Hakke (A12W, map ENG)"
],
"Surf": [
"Edward Newgate – Tsunami",
"Tsunami (A0E3)"
],
"Swift": [
"Itachi – Yasaka no Magatama",
"Yasaka no Magatama (A0AR, map ENG)"
],
"Temper Flare": [
"Sabo – Hiken",
"Hiken (A0PV, map ENG)"
],
"Thrash": [
"Zorro – Kiki Kyutoryuu: Ashura Bakkei - Moja no Tawamure",
"Kiki Kyutoryuu: Ashura Bakkei - Moja no Tawamure (A18K, map ENG)"
],
"Thunder": [
"Sasuke – R",
"Raiton Kirin (A04A)"
],
"Thunder Punch": [
"Sasuke – Amenotejikara: Chidori",
"Amenotejikara: Chidori (A0AE, map ENG)"
],
"Thunder Shock": [
"Momoshiki – Yakusa no Ikazuchi",
"Yakusa no Ikazuchi (A127, map ENG)"
],
"Thunderbolt": [
"Enel – Sango",
"Sango (A0VU, map ENG)"
],
"Twister": [
"Kaido – Tatsumaki Kaifu",
"Tatsumaki Kaifu (A137, map ENG)"
],
"Upper Hand": [
"Jiren – High Power Uppercut",
"High Power Uppercut (A02P, map ENG)"
],
"Vacuum Wave": [
"Sengoku – Shougeki Ha",
"Shougeki Ha (A11K, map ENG)"
],
"Venoshock": [
"Magellan – Venom Wisp",
"Venom Wisp (A0HI, map ENG)"
],
"Vine Whip": [
"Sesshomaru – Hikari no Muchi",
"Hikari no Muchi (A1BI, map ENG)"
],
"Water Gun": [
"Tobirama – Suiton Kouka Suijin",
"Suiton Kouka Suijin (A0CD, map ENG)"
],
"Water Pulse": [
"Kisama – E",
"Suiton Dai Bakusui Shouha (A00U)"
],
"Water Spout": [
"Kisama – W",
"Suiton Soodai Kaisaku (A0CH)"
],
"Waterfall": [
"Tanjiro – Hachi no Kata: Takitsubo",
"Hachi no Kata: Takitsubo (A17Z, map ENG)"
],
"Wave Crash": [
"Tanjiro – Juu no Kata: Seisei Ruten",
"Juu no Kata: Seisei Ruten (A17S, map ENG)"
],
"Weather Ball": [
"Pain – Rain",
"Rain"
],
"Whirlpool": [
"Edward Newgate – R",
"Tidal Wave (A0AZ)"
],
"Wild Charge": [
"Zenitsu – Ichi no Kata: Hekireki Issen - Rokuren",
"Ichi no Kata: Hekireki Issen - Rokuren (A1B9, map ENG)"
],
"Wood Hammer": [
"Madara – W",
"Mokuton Jukai Koutan (A03Z)"
],
"X Scissor": [
"Doflamingo – Q",
"Goshikito (A0J2)"
],
"Zap Cannon": [
"Ichigo – Vasto Lorde Lightning Blast",
"Vasto Lorde Lightning Blast (A0LD)"
]
}

MELEE = set(["Acrobatics", "Aerial Ace", "Aqua Jet", "Aqua Tail", "Assurance", "Astonish", "Avalanche", "Axe Kick", "Bite", "Blaze Kick", "Body Press", "Body Slam", "Bone Rush", "Bounce", "Brave Bird", "Breaking Swipe", "Brick Break", "Brutal Swing", "Bug Bite", "Bulldoze", "Bullet Punch", "Close Combat", "Covet", "Crabhammer", "Cross Chop", "Cross Poison", "Crunch", "Crush Claw", "Cut", "Darkest Lariat", "Dig", "Dive", "Double Edge", "Double Hit", "Double Kick", "Dragon Ascent", "Dragon Claw", "Dragon Rush", "Dragon Tail", "Drain Punch", "Draining Kiss", "Drill Peck", "Drill Run", "Dual Wingbeat", "Dynamic Punch", "Earthquake", "Explosion", "Extreme Speed", "Facade", "Fake Out", "False Swipe", "Feint", "Fell Stinger", "Fire Fang", "Fire Punch", "First Impression", "Flame Charge", "Flame Wheel", "Flare Blitz", "Flip Turn", "Fly", "Focus Punch", "Force Palm", "Foul Play", "Fury Attack", "Fury Cutter", "Fury Swipes", "Giga Impact", "Grassy Glide", "Hammer Arm", "Head Smash", "Headbutt", "High Horsepower", "High Jump Kick", "Horn Attack", "Hyper Fang", "Ice Fang", "Ice Punch", "Ice Spinner", "Iron Head", "Iron Tail", "Knock Off", "Kowtow Cleave", "Lash Out", "Last Resort", "Leaf Blade", "Leech Life", "Lick", "Liquidation", "Low Sweep", "Lunge", "Mach Punch", "Mega Kick", "Mega Punch", "Megahorn", "Metal Claw", "Meteor Assault", "Meteor Mash", "Misty Explosion", "Night Slash", "Outrage", "Payback", "Peck", "Phantom Force", "Play Rough", "Pluck", "Poison Fang", "Poison Jab", "Poison Tail", "Pounce", "Pound", "Power Whip", "Precipice Blades", "Psychic Fangs", "Pursuit", "Quick Attack", "Rage", "Rage Fist", "Raging Bull", "Rapid Spin", "Razor Shell", "Retaliate", "Revenge", "Rollout", "Sacred Sword", "Scratch", "Self Destruct", "Shadow Claw", "Shadow Force", "Shadow Punch", "Shadow Sneak", "Skitter Smack", "Sky Attack", "Slam", "Slash", "Smart Strike", "Solar Blade", "Spark", "Steel Wing", "Stomp", "Stomping Tantrum", "Storm Throw", "Strength", "Submission", "Sucker Punch", "Supercell Slam", "Superpower", "Tackle", "Take Down", "Temper Flare", "Thief", "Thrash", "Throat Chop", "Thunder Fang", "Thunder Punch", "Trailblaze", "Triple Axel", "Twineedle", "U Turn", "Upper Hand", "Vice Grip", "Vine Whip", "Vital Throw", "Waterfall", "Wave Crash", "Wild Charge", "Wing Attack", "Wood Hammer", "Wrap", "X Scissor", "Zen Headbutt"])

DASH_SPEED = 2000.0      # default dash speed of a melee move (game units / s); the move's missile / wave speed follows
DASH_STOP = 90.0         # the dash ends this far from a target unit
# melee move without a 9xHeroDefense effect: dust along the dash, its old missile model bursts on the target
GENERIC_TRAIL = 'war3:Objects\\Spawnmodels\\Undead\\ImpaleTargetDust\\ImpaleTargetDust.mdl'
GENERIC_HIT = 'war3:Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl'

# ---- how big ("epic", measured radius): wanted horizontal radius of each layer, in game units
R_TARGET = 320.0     # impact on a single target
R_PROJ = 150.0       # flying model / aura on a dashing user
R_CAST = 260.0
R_LINE_END = 360.0
AREA_MULT = 1.6      # self / point / nova impact = area x this
TRAIL_MIN = 220.0    # trail effect radius = max(area x 2, this)
RING_FRAC = 0.7      # each ring effect = area x this
SCALE_MIN, SCALE_MAX = 0.15, 8.0
PROJ_MIN, PROJ_MAX = 0.15, 4.5
SMALL_MIN = 0.08     # lowest scale for huge models (rain 4000, splat 2500 ...)
R_UNKNOWN = 150.0    # model radius when the library has none
LIFE_MAX = 4.0       # seconds an impact stays at most
TRAIL_LIFE_MAX = 2.0
TRAIL_STEP = 160.0   # default distance between trail effects
WAVES_MAX = 12       # channel AoE (blizzard base): one impact per wave

# buffs whose target art is the old effect: mapped moves get an art-less copy (new id -> base buff)
BUFF_COPY = {'BEer': 'BP00', 'Bfro': 'BP01', 'BHbd': 'BP02', 'BNbf': 'BP03', 'BEsh': 'BP04', 'BUim': 'BP05',
             'BHtc': 'BP06', 'XHbz': 'XP00'}
