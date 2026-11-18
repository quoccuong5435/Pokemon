"""v3.4.16: effects for the 169 damaging moves that v3.4.9 (fx_v349, GitHub branch v3.4.0) left without one.

Same engine as v3.4.9 (PkFx_* in the v3.4.10 script): PkFx_HT['AKxx'] 0 = data index; this adds new data indices
after the old ones and re-points the AK id of each move here (the 103 melee moves that only had the generic dash
lose the generic layers, the 66 ranged moves lose their old WC3 art).

Models:
  'Name'      = model already in the map from v3.4.9 (tools/v3411/fx_lib.json: path, measured radius, animations)
  'pw:Name'   = model from "Pokemon World V1.71.w3x" (protected map, real MPQ header at 1024), imported as
                PkFx\\PW_<Name>.mdx + its textures at the paths it asks for (tools/v3411/fx_pool_pw.json)
  'war3:path' = model of the game itself

SPEC keys as in fx_v349: p projectile (ranged) / aura on the user during the dash (melee); h, h2, h3 impacts;
t trail; r ring of rn effects; c effect at the user when the move starts; m hits of h; <key>s scale override;
ds dash speed of a melee move. Visual / movement only: damage, range, area, cooldown and mana are unchanged.

    used by tools/v3411/apply.py (script) and tools/v3411/build.py (object data + imports)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
PW_MAP = os.path.join(os.path.dirname(WORK), 'Pokemon World V1.71.w3x')

SPEC = {
    # ---- Normal
    'Body Slam': dict(h='pw:AnimatedBash', h2='Slam', h3='pw:WarStompCaster'),
    'Covet': dict(c='pw:ZHeart', h='pw:AnimatedBash', h2='White Ring'),
    'Double Edge': dict(p='Haki DV', t='DustWave_2021', h='pw:AnimatedBash', h2='Explosion', ds=2600),
    'Echoed Voice': dict(h='pw:soundwave', h2='PsiWave', m=2),
    'Facade': dict(c='pw:Aura Inner Fire', h='pw:AnimatedBash', h2='Red Explosion'),
    'Fake Out': dict(c='pw:BlinkNew', h='pw:AnimatedBash', h2='pw:Yellow_PurgeBuffTarget', ds=3200),
    'False Swipe': dict(h='pw:slash-b', h2='White Effect 1'),
    'Feint': dict(c='pw:BlackBlink', h='pw:slash-luc', ds=3000),
    'Fury Attack': dict(h='pw:AnimatedBash', m=3),
    'Fury Swipes': dict(h='pw:slash-b', m=3),
    'Giga Impact': dict(p='Bijuu Aura', ps=0.5, t='DustWave_2021', h='Super Big Explosion White 2020',
                        h2='GJ Style (5)', ds=2600),
    'Headbutt': dict(h='pw:AnimatedBash', h2='Slam'),
    'Hidden Power': dict(h='pw:Allovecolorfulsparks', h2='SuperShinyThingy7', r='pw:Yellow Ball', rn=5),
    'Horn Attack': dict(h='Spell W Law', h2='pw:AnimatedBash', ds=2600),
    'Hyper Fang': dict(h='pw:Hemorrhage', h2='Red Damage', h3='pw:AnimatedBash'),
    'Last Resort': dict(p='White Spell Aura 1', t='DustWave_2021', h='Super Big Explosion White 2020',
                        h2='WhiteShockwave', ds=2800),
    'Mega Punch': dict(h='pw:AnimatedBash', h2='Lion Fists Crit 1', h3='Explosion'),
    'Pay Day': dict(p='pw:Item_GoldCoins.1', h='pw:Item_GoldCoins.1', m=3, h2='SuperShinyThingy7'),
    'Pound': dict(h='pw:AnimatedBash', h2='Slam'),
    'Rage': dict(c='pw:Aura Inner Fire', h='pw:AnimatedBash', h2='Red Explosion'),
    'Raging Bull': dict(t='DustWave_2021', h='pw:RedCharkaExplosion', h2='pw:AnimatedBash', ds=2800),
    'Retaliate': dict(c='Red Lightning Haki', h='pw:AnimatedBash', h2='Explosion'),
    'Round': dict(h='pw:soundwave', h2='White Ring', m=2),
    'Scratch': dict(h='pw:slash-b'),
    'Slam': dict(h='Slam', h2='pw:WarStompCaster'),
    'Snore': dict(h='pw:soundwave', h2='White Ring'),
    'Stomp': dict(h='pw:WarStompCaster', h2='Earth Slam 2020'),
    'Strength': dict(h='pw:AnimatedBash', h2='Earth Slam 2020', h3='Lion Fists Crit 1'),
    'Tackle': dict(t='DustWave_2021', h='pw:AnimatedBash', h2='Slam'),
    'Take Down': dict(t='DustWave_2021', h='pw:AnimatedBash', h2='Explosion', ds=2600),
    'Tera Blast': dict(c='pw:Allovecolorfulsparks', h='pw:SolarBlast2', h2='SuperShinyThingy7'),
    'Tri Attack': dict(h='Red Explosion', h2='Blue Explosion', h3='LightningBoom'),
    'Uproar': dict(h='pw:soundwave', h2='Explosion', r='PsiWave', rn=4),
    'Vice Grip': dict(h='pw:slash-b', h2='pw:AnimatedBash'),
    'Wrap': dict(h='pw:Web', h2='pw:SpinFX2'),
    # ---- Fighting
    'Axe Kick': dict(h='Earth Slam 2020', h2='Newgate Style (2)', r='pw:WarStompCaster', rn=4),
    'Body Press': dict(h='Newgate Style (6)', h2='pw:WarStompCaster'),
    'Cross Chop': dict(h='pw:slash-b', h2='Newgate Style (6)'),
    'Drain Punch': dict(h='pw:AnimatedBash', h2='HarvestLife', h3='GainLife'),
    'Focus Punch': dict(c='HakkeAura 1', h='Lion Fists Crit 1', h2='pw:AnimatedBash'),
    'Low Sweep': dict(t='Danku Dust', h='pw:SpinFX2', h2='Earth Slam 2020'),
    'Mach Punch': dict(c='pw:BlinkNew', h='pw:AnimatedBash', m=2, h2='Spell W Law', ds=3400),
    'Meteor Assault': dict(c='Haki DV', h='Super Big Explosion White 2020', h2='Lion Fists Crit 1', r='Explosion', rn=6),
    'Storm Throw': dict(h='pw:SpinFX2', h2='Newgate Style (6)'),
    'Submission': dict(h='pw:SpinFX2', h2='pw:AnimatedBash', m=2),
    'Superpower': dict(c='Red Lightning Haki', h='Lion Fists Crit 1', h2='GJ Style (5)', r='Explosion', rn=4),
    'Vital Throw': dict(h='pw:SpinFX2', h2='Newgate Style (8)'),
    # ---- Flying
    'Acrobatics': dict(c='pw:BlinkCaster', t='Wind', h='pw:crossslashmissile', ds=2800),
    'Bounce': dict(c='pw:BlinkCaster', h='pw:WarStompCaster', h2='Danku Dust', ds=2400),
    'Brave Bird': dict(p='DivineRage', t='Wind', h='pw:SkyRing', h2='White Explosion', h3='pw:FeatherMissile', ds=3000),
    'Dragon Ascent': dict(c='pw:BlinkCaster', p='White Spell Aura 1', t='Wind', h='Super Big Explosion White 2020',
                          h2='pw:SkyRing', ds=3200),
    'Drill Peck': dict(p='pw:Tornado2', ps=0.4, h='pw:SpinFX2', h2='White Explosion', ds=2600),
    'Dual Wingbeat': dict(t='Wind', h='pw:FeatherMissile', m=2, h2='White Explosion'),
    'Fly': dict(c='Wind', t='AZ Air Dust', h='pw:WarStompCaster', h2='White Explosion', ds=2600),
    'Gust': dict(p='pw:Tornado2', ps=0.6, t='Wind', h='ArcaneTornado'),
    'Peck': dict(h='pw:AnimatedBash', h2='pw:FeatherMissile'),
    'Pluck': dict(h='pw:FeatherMissile', h2='pw:AnimatedBash'),
    'Sky Attack': dict(c='Natsu Wing', p='White Spell Aura 1', t='Wind', h='Super Big Explosion White 2020',
                       h2='pw:SkyRing', ds=3200),
    'Wing Attack': dict(t='Wind', h='pw:FeatherMissile', h2='White Explosion'),
    # ---- Poison
    'Acid': dict(p='pw:OrbOfVenom', h='Doku Doku Effect (5)', h2='pw:greengas'),
    'Acid Spray': dict(p='pw:OrbOfVenom', t='Doku Doku Effect (2)', h='Doku Gumo 2'),
    'Belch': dict(p='Doku Fugu', t='Doku Doku Effect (1)', h='Doku Gumo 1'),
    'Clear Smog': dict(p='pw:OrbOfVenom', h='pw:ElitePlagueCloud', h2='BigCloudFogBlack'),
    'Cross Poison': dict(t='Doku Doku Effect (2)', h='pw:slash-luc', h2='Doku Doku Effect (5)'),
    'Poison Fang': dict(h='pw:Hemorrhage', h2='Doku Doku Effect (5)'),
    'Poison Sting': dict(p='pw:OrbOfVenom', ps=0.5, h='Doku Doku Effect (2)'),
    'Poison Tail': dict(t='Doku Doku Effect (1)', h='pw:SpinFX2', h2='Doku Doku Effect (5)'),
    # ---- Ground
    'Bonemerang': dict(p='pw:boomerrangbone', t='SpecialAnimeDustWave', h='Blood_Strike'),
    'Dig': dict(c='Sand_Effect', t='Sand_Loop', h='pw:newdirtexnofire', h2='Danku Dust'),
    'Drill Run': dict(p='pw:SandTornado', ps=0.5, t='Sand_Effect', h='pw:SpinFX2', h2='Earth Slam 2020'),
    'High Horsepower': dict(h='Newgate Style (2)', h2='pw:WarStompCaster', r='Danku Dust', rn=5),
    'Mud Shot': dict(t='Sand_New_Spell', h='Sand_Effect', h2='pw:newdirtexnofire'),
    'Mud Slap': dict(t='Danku Dust', h='Sand_Effect'),
    'Precipice Blades': dict(h='Lava_Fall', hs=0.35, h2='Earth Slam 2020', h3='FireStomp', r='Sand_New_Spell', rn=8),
    'Stomping Tantrum': dict(h='Newgate Style (2)', h2='pw:WarStompCaster', r='Earth Slam 2020', rn=4),
    # ---- Rock
    'Ancient Power': dict(c='pw:SwirlingEarth', h='pw:chibakurock', h2='Earth Slam 2020'),
    'Head Smash': dict(p='Haki DV', h='pw:chibakurock', h2='Earth Slam 2020', h3='Explosion', ds=2600),
    'Meteor Beam': dict(c='pw:Accelerator Gate Yellow', t='pw:laseryellow', h='pw:chibakurock',
                        h2='Super Big Explosion Blue 2020'),
    'Rock Blast': dict(p='pw:chibakurock', ps=0.4, h='Earth Slam 2020', m=3),
    'Rock Slide': dict(h='pw:chibakurock', h2='Danku Dust', r='pw:chibakurock', rn=5),
    'Rock Throw': dict(p='pw:chibakurock', ps=0.5, h='Earth Slam 2020'),
    'Rock Tomb': dict(h='Sand Style Mokuton 2', h2='Earth Slam 2020', r='pw:chibakurock', rn=4),
    'Rollout': dict(p='pw:SwirlingEarth', ps=0.3, t='Danku Dust', h='Earth Slam 2020', ds=2400),
    'Smack Down': dict(p='pw:chibakurock', ps=0.4, h='Earth Slam 2020', h2='Danku Dust'),
    'Stone Edge': dict(t='Sand Style Mokuton 1', h='pw:chibakurock', h2='Earth Slam 2020', r='pw:chibakurock', rn=3),
    # ---- Bug
    'Bug Bite': dict(h='pw:Green Claw', h2='Green Explosion'),
    'Bug Buzz': dict(t='pw:soundwave', h='Green Effect', h2='ShockWave Green'),
    'Fell Stinger': dict(h='pw:Green Claw', h2='Crack Green Mihawk'),
    'First Impression': dict(c='pw:BlinkCaster', h='pw:Green Claw', h2='SuperBigBombExplosion Green', h2s=0.2, ds=3200),
    'Infestation': dict(t='pw:greengas', h='pw:Web', h2='Doku Doku Effect (6)'),
    'Leech Life': dict(h='pw:Green Claw', h2='HarvestLife', h3='GainLife'),
    'Lunge': dict(c='pw:BlinkCaster', h='pw:Green Claw', h2='Green Explosion', ds=3000),
    'Megahorn': dict(p='@Rock_Lee_Green_Aura', h='SuperBigBombExplosion Green', h2='pw:Green Claw', ds=2600),
    'Pin Missile': dict(p='SpiritArrow_ByEpsilon', h='Green Explosion', m=3),
    'Pollen Puff': dict(t='pw:natureexplosion', h='pw:Life Magic', h2='SuperShinyThingy1'),
    'Pounce': dict(c='pw:BlinkCaster', h='pw:Green Claw', h2='Danku Dust'),
    'Skitter Smack': dict(c='pw:BlinkCaster', h='pw:Green Claw', h2='pw:AnimatedBash'),
    'Struggle Bug': dict(t='pw:greengas', h='Green Explosion'),
    'Twineedle': dict(h='pw:Green Claw', m=2, h2='Doku Doku Effect (2)'),
    'U Turn': dict(c='pw:BlinkNew', h='pw:Green Claw', h2='pw:BlinkCaster', ds=3400),
    # ---- Ghost
    'Astonish': dict(h='pw:Soul Discharge Purple', h2='PurpleExplosion_2'),
    'Lick': dict(h='pw:Soul Discharge Purple', h2='PurpleExplosion_2'),
    'Poltergeist': dict(p='pw:SoulMissile', h='pw:Soul Discharge Purple', h2='MS Tsukuyomi #1'),
    'Rage Fist': dict(c='Red Lightning Haki', h='pw:AnimatedBash', h2='pw:Soul Discharge Purple', h3='Red Explosion'),
    'Shadow Claw': dict(h='pw:ShadowSlash', h2='Missile Black (5)'),
    'Shadow Punch': dict(c='pw:BlackBlink', h='pw:AnimatedBash', h2='pw:Soul Discharge Purple'),
    'Shadow Sneak': dict(c='pw:BlackBlink', t='BigCloudFogBlack', ts=0.4, h='pw:ShadowSlash', ds=3400),
    # ---- Steel
    'Bullet Punch': dict(c='pw:BlinkNew', h='pw:AnimatedBash', h2='Spell W Law', ds=3200),
    'Doom Desire': dict(c='pw:Accelerator Gate Yellow', t='GlowLineBlue', h='pw:SolarBlast2',
                        h2='Super Big Explosion White 2020'),
    'Iron Head': dict(p='pw:Defence-Force-Field', h='pw:AnimatedBash', h2='ShockwaveYellow', ds=2400),
    'Iron Tail': dict(t='DustWave_2021', h='pw:SpinFX2', h2='White Explosion', h3='pw:AnimatedBash'),
    'Metal Claw': dict(h='pw:slash-b', h2='ShockwaveYellow'),
    'Meteor Mash': dict(c='pw:Liberty Yellow', h='pw:SolarBlast2', h2='pw:AnimatedBash', h3='ShockwaveYellow'),
    'Smart Strike': dict(c='pw:BlinkNew', h='pw:slash-b', h2='ShockwaveYellow'),
    'Steel Beam': dict(c='pw:Accelerator Gate Yellow', t='pw:laseryellow', h='ShockwaveYellow',
                       h2='Super Big Explosion White 2020'),
    'Steel Wing': dict(t='Wind', h='pw:slash-b', h2='ShockwaveYellow'),
    # ---- Water
    'Aqua Tail': dict(p='WaterEnchant', t='E Tanjiro (2)', h='pw:AquaSpike', h2='TidalEruption'),
    'Brine': dict(p='pw:Water Shot', t='WaterBlobs1', h='WaterBlast', h2='TidalEruption'),
    'Bubble Beam': dict(p='WaterBlobs1', t='WaterBlobs1', h='WaterBlast'),
    'Chilling Water': dict(p='pw:Frost Missile', t='WaterBlobs1', h='pw:iceslam'),
    'Crabhammer': dict(p='WaterEnchant', h='AquaSpikeVersion2', h2='WaterBlast', ds=2400),
    'Flip Turn': dict(p='WaterEnchant', t='WaterBlobs1', h='WaterBlast', h2='pw:AquaSpike'),
    'Muddy Water': dict(h='TidalEruption', h2='Sand_Loop', r='WaterBlast', rn=6),
    'Scald': dict(p='pw:Water Shot', t='pw:flames&smoke', ts=0.4, h='TidalEruption', h2='WaterBlast'),
    'Water Pledge': dict(t='WaterfallFX', h='TidalEruption', h2='AquaSpikeVersion2', r='WaterBlast', rn=4),
    # ---- Grass
    'Absorb': dict(c='GainLife', h='pw:Life Magic', h2='HarvestLife'),
    'Grass Pledge': dict(h='Mokuton Tree 1', h2='pw:GrowingTreeImpaleEffect', r='Mokuton (2)', rn=4),
    'Grassy Glide': dict(t='pw:natureexplosion', h='Green Explosion'),
    'Leaf Storm': dict(h='Mokuton Sashiki All', hs=0.4, h2='pw:natureexplosion', r='pw:GrowingTreeImpaleEffect', rn=5),
    'Leafage': dict(h='pw:natureexplosion', h2='Green Effect'),
    'Magical Leaf': dict(c='pw:Life Magic', h='pw:natureexplosion', h2='Mokuton (2)'),
    'Mega Drain': dict(c='GainLife', h='HarvestLife', h2='pw:Life Magic'),
    'Seed Bomb': dict(h='pw:natureexplosion', h2='Green Explosion', m=2),
    'Trailblaze': dict(t='pw:natureexplosion', h='Green Explosion', h2='Mokuton (2)'),
    # ---- Electric
    'Electroweb': dict(h='pw:Web', h2='pw:Lightningnova', h3='LightningBoom'),
    'Thunder Fang': dict(h='pw:Hemorrhage', h2='LightningBoom', h3='pw:LightningEmpowerTarget'),
    'Volt Switch': dict(c='pw:LightningEmpowerTarget', h='pw:Lightningnova', h2='LightningBoom'),
    # ---- Psychic
    'Extrasensory': dict(h='MS Tsukuyomi #2', h2='pw:Void Rift II Purple'),
    'Psychic Fangs': dict(h='pw:Hemorrhage', h2='PsiWave', h3='pw:Void Rift II Purple'),
    'Psychic Noise': dict(h='pw:soundwave', h2='PsiWave', h3='MS Tsukuyomi #2'),
    'Psyshock': dict(h='pw:Void Disc', h2='PsiWave', r='pw:Void Rift II Purple', rn=4),
    'Psystrike': dict(c='Aizen Skill - Fragor Effect Damage', h='Aizen Effect Damage', h2='pw:Void Rift II Purple',
                      r='PsiWave', rn=4),
    'Stored Power': dict(c='pw:Liberty Yellow', h='Aizen Skill - Fragor Effect Damage', h2='PsiWave'),
    'Zen Headbutt': dict(p='pw:Void Disc', h='PsiWave', h2='pw:AnimatedBash', ds=2600),
    # ---- Ice
    'Ice Fang': dict(h='pw:Ice Shard', h2='Freezing_Ring2', h3='IceNova'),
    'Powder Snow': dict(t='pw:SnowyBlizzardTarget', h='pw:frostnova', h2='IceStompMist'),
    'Triple Axel': dict(h='pw:iceslam', m=3, h2='IceNova'),
    # ---- Dragon
    'Breaking Swipe': dict(t='SpecialAnimeDustWave', h='animeslashfinal', h2='Daisen Sekai Type 2'),
    'Dragon Tail': dict(t='SpecialAnimeDustWave', h='Daisen Sekai Type 1', h2='pw:SpinFX2'),
    'Roar Of Time': dict(c='Empyrean Nova Classic', t='pw:Blue Laser Ray', h='Super Big Explosion Blue 2020',
                         h2='IonCannonBlue'),
    'Scale Shot': dict(p='pw:GoldDragonMissile', h='White Explosion', m=3),
    # ---- Dark
    'Assurance': dict(t='BigCloudFogBlack', ts=0.4, h='pw:ShadowSlash', h2='Missile Black (30)'),
    'Bite': dict(t='BigCloudFogBlack', ts=0.4, h='pw:Hemorrhage', h2='Red Damage'),
    'Brutal Swing': dict(h='RZoro Effect (6)', h2='pw:SpinFX2'),
    'Crunch': dict(c='Liberation', h='pw:Hemorrhage', h2='Missile Black (5)'),
    'Darkest Lariat': dict(p='Bankai Aura 2021', h='pw:SpinFX2', h2='Black Stomp', h3='pw:BlackChakraExplosion'),
    'Foul Play': dict(c='BigCloudFogBlack', h='pw:ShadowSlash', h2='Missile Black (2)'),
    'Knock Off': dict(h='pw:AnimatedBash', h2='BigCloudFogBlack', h3='pw:BlackBlink'),
    'Kowtow Cleave': dict(c='pw:BlackBlink', h='pw:ShadowSlash', h2='Uitachi Style (16)'),
    'Lash Out': dict(h='pw:BlackChakraExplosion', h2='pw:ShadowSlash'),
    'Payback': dict(c='Liberation', h='pw:ShadowSlash', h2='Missile Black (30)'),
    'Pursuit': dict(c='pw:BlackBlink', h='pw:ShadowSlash', ds=3400),
    'Thief': dict(c='pw:BlackBlink', h='pw:ShadowSlash', h2='pw:Item_GoldCoins.1'),
    'Throat Chop': dict(h='pw:ShadowSlash', h2='pw:Hemorrhage'),
    # ---- Fairy
    'Alluring Voice': dict(h='pw:soundwave', h2='pw:PinkSurge', r='White Ring', rn=4),
    'Disarming Voice': dict(h='pw:soundwave', h2='White Spell Aura 1', r='pw:PinkSurge', rn=3),
    'Draining Kiss': dict(h='pw:ZHeart', h2='pw:PinkSurge', h3='GainLife'),
    'Fairy Wind': dict(h='pw:PinkSurge', h2='pw:blazingwind1', r='White Ring', rn=3),
    'Play Rough': dict(h='pw:PinkSurge', h2='pw:SpinFX2', h3='Danku Dust', r='pw:ZHeart', rn=4),
}

# ---- Pokemon World's own move effects (decoded script: analysis/pw_spell_fx.py -> out/pkworld/spell_fx.csv)
# replace the main layers of these moves with the model Pokemon World uses for the same / a close move
SPEC.update({
    'Acid': dict(p='pw:OrbOfVenom', h='pw:VenomousGaleV2', h2='Doku Doku Effect (5)'),
    'Bite': dict(t='BigCloudFogBlack', ts=0.4, h='pw:Culling Cleave Purple', h2='Red Damage'),
    'Bubble Beam': dict(p='pw:BubbleMissile', t='WaterBlobs1', h='WaterBlast', h2='pw:WaterBurst'),
    'Bug Bite': dict(h='pw:ThornSlam', h2='pw:Green Claw'),
    'Bug Buzz': dict(t='pw:soundwave', h='pw:InfestationInsectBolt', h2='Green Effect'),
    'Bullet Punch': dict(c='pw:BlinkNew', h='pw:Punch', h2='pw:Shockwave White', ds=3200),
    'Cross Chop': dict(h='pw:CrossSlashMissileRed', h2='Newgate Style (6)'),
    'Crunch': dict(c='Liberation', h='pw:Culling Cleave Silver', h2='pw:Hemorrhage'),
    'Dig': dict(c='Sand_Effect', t='Sand_Loop', h='pw:DustAndRocks', h2='pw:newdirtexnofire'),
    'Fury Swipes': dict(h='pw:Effect-01', m=3),
    'Gust': dict(p='pw:Tornado2', ps=0.6, t='Wind', h='pw:GiantVortex2'),
    'Headbutt': dict(h='pw:ArcaneExplode', h2='pw:AnimatedBash'),
    'Hyper Fang': dict(h='pw:Culling Cleave Red', h2='Red Damage', h3='pw:AnimatedBash'),
    'Iron Head': dict(p='pw:Defence-Force-Field', h='pw:AnimatedBash', h2='pw:DustAndRocks', ds=2400),
    'Leafage': dict(h='pw:LeafBolt', h2='pw:natureexplosion'),
    'Leaf Storm': dict(h='Mokuton Sashiki All', hs=0.4, h2='pw:natureexplosion', r='pw:WindcutterLeafs', rn=6),
    'Magical Leaf': dict(c='pw:Life Magic', h='pw:LeechSeed_Missle', h2='pw:natureexplosion'),
    'Mega Punch': dict(h='pw:Punch', h2='Lion Fists Crit 1', h3='Explosion'),
    'Megahorn': dict(p='@Rock_Lee_Green_Aura', h='SuperBigBombExplosion Green', h2='pw:Missile_DIM_Alpha_Upgrade', ds=2600),
    'Metal Claw': dict(h='pw:Blue Claw', h2='ShockwaveYellow'),
    'Meteor Mash': dict(c='pw:Liberty Yellow', h='pw:Comet', h2='pw:AnimatedBash', h3='ShockwaveYellow'),
    'Mud Slap': dict(c='pw:SandBreath', t='Danku Dust', h='Sand_Effect'),
    'Pound': dict(h='pw:TicklesHandRight', h2='pw:AnimatedBash'),
    'Powder Snow': dict(t='pw:SnowyBlizzardTarget', h='pw:IceTornado', h2='pw:frostnova'),
    'Pursuit': dict(c='pw:BlackBlink', h='pw:ShadowSlash', h2='pw:PurpleBansheeCryMissile', ds=3400),
    'Rage': dict(c='pw:Aura Inner Fire', h='pw:AnimatedBash', h2='pw:RedAftershock'),
    'Rock Blast': dict(p='war3:Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl',
                       h='Earth Slam 2020', m=3),
    'Rock Throw': dict(p='war3:Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl',
                       h='Earth Slam 2020', h2='pw:DustAndRocks'),
    'Scratch': dict(h='pw:Culling Cleave Silver'),
    'Seed Bomb': dict(h='pw:Seed Shot', h2='Green Explosion'),
    'Stone Edge': dict(t='Sand Style Mokuton 1', h='pw:tsunadeslam', h2='pw:DustSmash', r='pw:chibakurock', rn=3),
    'Strength': dict(c='pw:StoneWalk', h='pw:AnimatedBash', h2='Earth Slam 2020', h3='Lion Fists Crit 1'),
    'Submission': dict(h='pw:DetroitSmash_Effect', h2='pw:SpinFX2'),
    'Tri Attack': dict(h='pw:FireVolcanusFury', h2='pw:IcySkewerGround', h3='pw:Lightningnova'),
    'Trailblaze': dict(t='pw:WindcutterLeafs', h='Green Explosion', h2='Mokuton (2)'),
    'Grassy Glide': dict(t='pw:WindcutterLeafs', h='Green Explosion'),
    'Vice Grip': dict(h='pw:GetsugaNewYellow', h2='pw:AnimatedBash'),
    'Water Pledge': dict(t='WaterfallFX', h='TidalEruption', h2='pw:Water_Dragon', r='WaterBlast', rn=4),
    'Wing Attack': dict(t='Wind', h='pw:FeatherMissile', h2='HolyTornado'),
    'Wrap': dict(h='pw:CelebrationdaySpiraldragon', h2='pw:Web'),
    'Zen Headbutt': dict(c='pw:BlinkCaster', p='pw:Void Disc', h='PsiWave', h2='pw:AnimatedBash', ds=2600),
})

# ---- v3.4.16: moves of v3.4.9 (fx_v349_ref.py = tools/v34/fx_v349.py of GitHub branch v3.4.0) that Pokemon World
# gives a Pokemon-like model: the v3.4.9 layers stay, the layer below is added / replaced by that model
V349_PW = {
    'Air Slash': {'h3': 'pw:TotemWave'},
    'Aqua Jet': {'h2': 'pw:AquaSpike'},
    'Confusion': {'h3': 'pw:Void Disc'},
    'Dragon Breath': {'h2': 'pw:BreathofDecay'},
    'Dragon Claw': {'h3': 'pw:HellSpike'},
    'Dream Eater': {'h3': 'pw:Big_ICM_Purple'},
    'Dynamic Punch': {'h3': 'pw:Punch'},
    'Fire Punch': {'h2': 'pw:Punch'},
    'Fire Spin': {'h2': 'pw:FireTornado'},
    'Flame Wheel': {'h3': 'pw:Blaze Saw'},
    'Flash Cannon': {'h3': 'pw:laser'},
    'Hydro Pump': {'h3': 'pw:TidalErruption2'},
    'Hyper Beam': {'h': 'pw:FinalKamehamehaEffbyValkemiere'},
    'Ice Punch': {'h2': 'pw:Punch'},
    'Psybeam': {'h3': 'pw:Void Rift II Purple'},
    'Psychic': {'h3': 'pw:Void Drown'},
    'Razor Leaf': {'h3': 'pw:LeafBolt'},
    'Shadow Ball': {'h3': 'pw:void_Bomb'},
    'Slash': {'h3': 'pw:Culling Slash Red'},
    'Sludge Bomb': {'h3': 'pw:BlackDeath'},
    'Smog': {'h3': 'pw:PurpleSmoke'},
    'Solar Beam': {'h3': 'pw:GreenSurgeFin'},
    'Spark': {'h3': 'pw:Valiant Charge Holy'},
    'Surf': {'h3': 'pw:WaterfallFX'},
    'Swift': {'h3': 'pw:Comet'},
    'Thunder': {'h3': 'pw:LightningWrath'},
    'Thunder Punch': {'h3': 'pw:Punch'},
    'Vine Whip': {'h2': 'pw:Mokuton2'},
    'Water Gun': {'h2': 'pw:Water Shot'},
    'Water Pulse': {'h2': 'pw:WaterElementalMissile'},
    'Zap Cannon': {'h3': 'pw:Yellow Ball'},
}


def _v349_specs():
    import fx_v349_ref as V
    lib = json.load(open(os.path.join(HERE, 'fx_lib.json'), encoding='utf-8'))
    out = {}
    for mv, add in V349_PW.items():
        spec = dict(V.SPEC[mv])
        for key, name in add.items():
            spec[key] = name
            spec.pop(key + 's', None)
        for key in list(spec):
            name = spec[key]
            if key in SLOT and isinstance(name, str) and not name.startswith(('pw:', 'war3:')):
                if name not in lib and name.replace('@', '') not in lib and name + ' (ENG)' not in lib:
                    del spec[key]            # model left out by v3.4.9 (BAD) -> not in the map
                    spec.pop(key + 's', None)
        out[mv] = spec
    return out


# ---- the 58 status moves of v3.4.12 (status_moves.py, indices 320..377): a visual on top of their small WC3 art.
# Keyed on their 4 slot buttons (A V/W/Y/Z + index). Self moves: layers at the user (ring = around the user);
# moves on a unit: c at the user, h / h2 on the target.
STATUS_SPEC = {
    'Swords Dance': dict(h='pw:Lightningempowercaster', h2='pw:slash-b', r='pw:slash-luc', rn=4),
    'Nasty Plot': dict(h='pw:BlackChakraExplosion', h2='Liberation'),
    'Dragon Dance': dict(h='pw:Fire Spirit Dragon', h2='Bijuu Aura'),
    'Calm Mind': dict(h='pw:Void Disc', h2='PsiWave'),
    'Bulk Up': dict(h='pw:AuraOfStrengtht', h2='pw:RedAftershock'),
    'Quiver Dance': dict(h='pw:Wild Growth', h2='pw:Allovecolorfulsparks'),
    'Shell Smash': dict(h='pw:RedCharkaExplosion', h2='Explosion'),
    'Agility': dict(h='Wind', h2='pw:BlinkNew'),
    'Rock Polish': dict(h='pw:DustAndRocks', h2='SuperShinyThingy7'),
    'Work Up': dict(h='pw:AuraOfStrengtht', h2='pw:Alloveblastbuff'),
    'Growth': dict(h='pw:Alloveblastbuff', h2='pw:Wild Growth'),
    'Curse': dict(h='pw:Call of Dread Purple', h2='PurpleExplosion_2'),
    'Focus Energy': dict(h='pw:YellowSaiyanAura', h2='pw:Lightningempowercaster'),
    'Belly Drum': dict(h='pw:CommonExplosion_Y', h2='pw:RedAftershock'),
    'Protect': dict(h='pw:Defence-Force-Field', h2='White Ring'),
    'Detect': dict(h='pw:Defence-Force-Field', h2='pw:Liberty Yellow'),
    'Recover': dict(h='pw:Heal', h2='GainLife'),
    'Roost': dict(h='pw:FeatherMissile', m=3, h2='pw:Heal'),
    'Slack Off': dict(h='pw:Heal', h2='GainLife'),
    'Soft-Boiled': dict(h='pw:Alloveelunesholybolt', h2='pw:Heal'),
    'Synthesis': dict(h='pw:Green Light', h2='pw:Life Magic'),
    'Moonlight': dict(h='pw:LightofElune', h2='GainLife'),
    'Morning Sun': dict(h='pw:HolyLightBlessing', h2='GainLife'),
    'Rest': dict(h='pw:Alloveelunesholybolt', h2='White Spell Aura 1'),
    'Iron Defense': dict(h='pw:Astral_Runic_Shield', h2='ShockwaveYellow'),
    'Acid Armor': dict(h='pw:VenomousAura', h2='Doku Doku Effect (6)'),
    'Amnesia': dict(h='pw:Void Rift II Purple', h2='PsiWave'),
    'Cosmic Power': dict(h='pw:StarfallTarget2', h2='pw:Allovecolorfulsparks'),
    'Reflect': dict(h='pw:Astral_Runic_Shield', h2='White Ring'),
    'Light Screen': dict(h='pw:TealCasterAura', h2='White Ring'),
    'Substitute': dict(h='pw:MirrorImageCaster2', h2='Clone'),
    'Aqua Ring': dict(h='pw:WaterNovaTarget', h2='WaterAura'),
    'Ingrain': dict(h='pw:Wild Growth', h2='Mokuton Tree 1'),
    'Wish': dict(h='pw:StarfallTarget2', h2='pw:HolyLightBlessing'),
    'Growl': dict(h='pw:BattleCryCaster', r='pw:soundwave', rn=6),
    'Charm': dict(h='pw:ZHeart', h2='pw:PinkSurge'),
    'Leer': dict(h='pw:Castredillusory', r='pw:DTRingWhite', rn=4),
    'Tail Whip': dict(h='pw:lightning boom2', r='Danku Dust', rn=4),
    'Screech': dict(c='pw:DTRingWhite', h='pw:soundwave', h2='PsiWave'),
    'Fake Tears': dict(h='WaterBlobs1', h2='pw:BlackBlink'),
    'Metal Sound': dict(h='pw:SoundWaveBlue', h2='ShockwaveYellow'),
    'Scary Face': dict(h='pw:Castredillusory', h2='BigCloudFogBlack'),
    'String Shot': dict(h='pw:greengas', r='pw:Web', rn=5),
    'Sand Attack': dict(h='Sand_Effect', h2='pw:SandBreath'),
    'Thunder Wave': dict(h='pw:HellLightning', h2='LightningBoom'),
    'Will-O-Wisp': dict(h='pw:Flamestrike I', h2='Amaterasu_New'),
    'Toxic': dict(h='pw:ElitePlagueCloud', h2='Doku Doku Effect (6)'),
    'Poison Powder': dict(h='pw:greengas', h2='Doku Doku Effect (5)'),
    'Stun Spore': dict(h='pw:Allovecolorfulsparks', h2='pw:greengas'),
    'Hypnosis': dict(h='pw:Void Rift II Purple', h2='MS Tsukuyomi #2'),
    'Sleep Powder': dict(h='pw:greengas', h2='pw:Green Light'),
    'Spore': dict(h='pw:natureexplosion', h2='pw:greengas'),
    'Sing': dict(h='pw:soundwave', h2='pw:ZHeart'),
    'Yawn': dict(h='pw:CloudOfFog', h2='White Ring'),
    'Confuse Ray': dict(h='pw:Yellow Ball', h2='pw:Void Disc'),
    'Swagger': dict(h='pw:RedAftershock', h2='pw:BattleCryCaster'),
    'Leech Seed': dict(h='pw:LeechSeed_Missle', h2='Mokuton (2)'),
    'Taunt': dict(h='pw:Gravitone', h2='pw:BattleCryCaster'),
    # v3.4.16: new debuffs
    'Feather Dance': dict(h='war3:Abilities\\Spells\\NightElf\\FanOfKnives\\FanOfKnivesCaster.mdl', h2='pw:FeatherMissile'),
    'Cotton Spore': dict(h='pw:Wind_Blink', r='pw:greengas', rn=5),
    'Tickle': dict(h='pw:TicklesHandLeft', h2='pw:TicklesHandRight'),
    'Eerie Impulse': dict(h='pw:LightningEmpowerTarget', h2='LightningBoom'),
    'Confide': dict(h='pw:soundwave', r='White Ring', rn=4),
    'Baby-Doll Eyes': dict(h='pw:ZHeart', r='pw:PinkSurge', rn=4),
    'Smokescreen': dict(h='pw:CloudOfFog', h2='pw:BlackCloudKingSize'),
    'Kinesis': dict(h='pw:Void Disc', h2='PsiWave'),
    'Sweet Kiss': dict(h='pw:ZHeart', h2='pw:Yellow Ball'),
    'Transform': dict(c='pw:MirrorImageCaster2', h='pw:BlinkCaster'),
}
STATUS_AREA = 120.0
# v3.4.16: gym leaders (gyms 1..8, Kanto order like the badges) and Elite Four + Champion: name, Pokemon World model
# (Unit\<model>.mdx), line when a challenge starts, line when the challenger wins. Unit types nT00.. (build.py).
TRAINERS = [
    ('Brock', 'Brock', 'My rock-hard willpower is my strength. Show me yours!', 'I took you for granted. Here, the Boulder Badge!'),
    ('Misty', 'Ondine', "My policy is an all-out offensive! Let's go!", "Wow, you're too much! Take the Cascade Badge."),
    ('Lt. Surge', 'ElectricTypeChampion', "You won't live long in combat. Get ready to be zapped!", 'Whoa! You earned the Thunder Badge!'),
    ('Erika', 'GrassTypeChampion', 'I shall not lose. Let the flowers bloom!', 'Oh! I concede defeat. The Rainbow Badge is yours.'),
    ('Janine', 'PoisonTypeChampion', 'You will feel the despair of poison!', 'Father would be proud of you. The Soul Badge!'),
    ('Sabrina', 'Serena', 'I foresaw your coming... and your defeat.', 'I did not foresee this. The Marsh Badge is yours.'),
    ('Blaine', 'FireTypeChampion', 'Hah! You better have Burn Heal!', 'I have burnt out! You have earned the Volcano Badge!'),
    ('Giovanni', 'Gentleman', 'So, you have come this far. Let me show you true power.', 'Ha! That was a truly intense fight. The Earth Badge!'),
    ('Will', 'Medium', 'I am Will of the Elite Four. My psychic Pokemon await you.', ''),
    ('Koga', 'Scout', 'Fwahahaha! A ninja knows no fear. Face my poison!', ''),
    ('Bruno', 'BlackBelt', "We will grind you down with our superior power! Hoo hah!", ''),
    ('Karen', 'Jessie', 'Strong Pokemon. Weak Pokemon. Show me your favourites.', ''),
    ('Lance', 'LeagueMaster', 'I am the Champion. Dragons are mighty Pokemon. Come!', ''),
]
TRAINER_ID = ['nT0' + '0123456789ABC'[k] for k in range(len(TRAINERS))]
# v3.4.16 Team Rocket raid: NPCs (unit id, name, Pokemon World model, scale) and the wild types of its Pokemon
# (Arbok, Weezing, Meowth, Ekans, Koffing)
ROCKET_NPC = [('nT0D', 'Jessie', 'Jessie', 1.4), ('nT0E', 'Team Rocket Grunt', 'RocketGruntMale', 1.6)]
# v3.4.16 Dynamax: the big blast of a Max Move, per type in T_ order (bug, dark, dragon, electric, fairy, fighting,
# fire, flying, ghost, grass, ground, ice, normal, poison, psychic, rock, steel, water); models already in the map
MAX_FX = ('SuperBigBombExplosion Green', 'Black Stomp', 'Bijuu Dama 2', 'GreatLightning', 'White Holy',
          'Lion Fists Crit 1', 'FireStomp', 'AZ Air Dust', 'MS Tsukuyomi #1', 'Mokuton Sashiki All', 'EarthNova',
          'IceStomp', 'Super Big Explosion White 2020', 'Doku Doku Effect (6)', 'PsiWave', 'Earth Slam 2020',
          'ShockwaveYellow', 'TidalEruption')
MAX_R = 550.0  # wanted radius of the blast
ROCKET_TYPES = ('nX09', 'nX5P', 'nX3F', 'nX1I', 'nX2T', 'nX3S')  # + Persian
# model scale (Pokemon World's own unit scale where it has one)
TRAINER_SCALE = {'Brock': 1.35, 'ElectricTypeChampion': 1.6, 'GrassTypeChampion': 1.25, 'PoisonTypeChampion': 1.6,
                 'FireTypeChampion': 1.25, 'Scout': 1.3}

# v3.4.16: regional forms of wild Pokemon: wild type ids, skin (a Pokemon World model 'pw:<file>' -> unit nR0x, or an
# Arena unit type), name, types. 10% of the spawns of these species (Fx_RegionalX); gold x1.5.
REGIONAL = [
    (('nX5L',), 'pw:2007', 1.5, 'Alolan Vulpix', ('T_ICE', None)),
    (('nX3L',), 'pw:2008', 0.9, 'Alolan Ninetales', ('T_ICE', 'T_FAIRY')),
    (('n027',), 'pw:2003', 1.6, 'Alolan Exeggutor', ('T_GRASS', 'T_DRAGON')),
    (('nX3D',), 'pw:2004', 1.15, 'Alolan Marowak', ('T_FIRE', 'T_GHOST')),
    (('nX5C',), 'pw:2011', 2.5, 'Hisuian Typhlosion', ('T_FIRE', 'T_GHOST')),
    (('nW06',), 'pw:2022', 1.3, 'Hisuian Sneasel', ('T_FIGHTING', 'T_POISON')),
    (('nX28',), 'pw:2002', 2.1, 'Red Gyarados', ('T_WATER', 'T_FLYING')),
    (('nX45',), 'P06A', None, 'Alolan Raichu', ('T_ELECTRIC', 'T_PSYCHIC')),
    (('n01V', 'n01W'), 'P4MA', None, 'Alolan Sandshrew', ('T_ICE', 'T_STEEL')),
    (('n01U', 'n01T'), 'P4NA', None, 'Alolan Sandslash', ('T_ICE', 'T_STEEL')),
    (('nX1X',), 'P03A', None, 'Alolan Geodude', ('T_ROCK', 'T_ELECTRIC')),
    (('nX25',), 'P05A', None, 'Alolan Graveler', ('T_ROCK', 'T_ELECTRIC')),
    (('nX23',), 'P04A', None, 'Alolan Golem', ('T_ROCK', 'T_ELECTRIC')),
]


def regional_skins():
    """[(unit id nR0x, model file in Pokemon World, scale)] for the 'pw:' skins, in REGIONAL order."""
    out, k = [], 0
    for _ids, skin, scale, _name, _ty in REGIONAL:
        if skin.startswith('pw:'):
            out.append(('nR0' + '0123456789'[k], skin[3:], scale))
            k += 1
    return out
BADGES = ('Boulder', 'Cascade', 'Thunder', 'Rainbow', 'Soul', 'Marsh', 'Volcano', 'Earth')  # gyms 1..8 (Kanto)   # impact size of a status move (x AREA_MULT, at least 200 x AREA_MULT)

# ---- same rules as v3.4.9 (fx_v349 / merge_v349)
MODE_OF_BASE = {'AHtb': 0, 'AEsh': 0, 'AHtc': 1, 'AOws': 1, 'AHbz': 2,
                'AUcs': 3, 'AOsh': 3, 'ANbf': 3, 'AUim': 3, 'AEer': 4, 'AUfn': 4}
MELEE_BASES = {'AHtb', 'AEsh', 'AUcs', 'AOsh', 'AUim', 'AEer', 'AUfn'}
MISSILE_BASES = {'AHtb', 'AEsh', 'AUcs', 'AOsh'}
LINE_LEN_COL = {'AUcs': 'DataC1', 'AOsh': 'DataC1', 'ANbf': 'DataC1', 'AUim': 'DataA1'}
SLOT = {'p': 10, 'h': 20, 'h2': 30, 't': 40, 'r': 50, 'c': 60, 'h3': 70}
ART_KEYS = ('Missileart', 'Casterart', 'Targetart', 'Effectart', 'Specialart', 'Areaeffectart', 'LightningEffect')
# buffs with visible target art -> art-less copies made by v3.4.9 (already in the v3.4.10 map)
BUFF_COPY = {'BEer': 'BP00', 'Bfro': 'BP01', 'BHbd': 'BP02', 'BNbf': 'BP03', 'BEsh': 'BP04', 'BUim': 'BP05',
             'BHtc': 'BP06', 'XHbz': 'XP00'}
DASH_SPEED = 2000.0
R_TARGET, R_PROJ, R_CAST, R_LINE_END = 320.0, 150.0, 260.0, 360.0
AREA_MULT, TRAIL_MIN, RING_FRAC = 1.6, 220.0, 0.7
SCALE_MIN, SCALE_MAX = 0.15, 8.0
PROJ_MIN, PROJ_MAX = 0.15, 4.5
R_UNKNOWN = 150.0
PW_MIN_R, PW_SCALE_MAX = 120.0, 3.0   # Pokemon World models not measured on a render: radius floor, highest scale
PW_RENDER_MAX = 5.0                   # highest scale of a measured Pokemon World model (tiny hit sparks)
RENDER_R = {k: v for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         'fx_render_pw.json'), encoding='utf-8')).items()
            if not k.startswith('_')}
LIFE_MAX, TRAIL_LIFE_MAX, TRAIL_STEP, WAVES_MAX = 4.0, 2.0, 160.0, 12
# v3.4.9's list of contact moves (the user dashes when the base allows it)
MELEE = set("""Acrobatics|Aerial Ace|Aqua Jet|Aqua Tail|Assurance|Astonish|Avalanche|Axe Kick|Bite|Blaze Kick|Body Press|
Body Slam|Bone Rush|Bounce|Brave Bird|Breaking Swipe|Brick Break|Brutal Swing|Bug Bite|Bulldoze|Bullet Punch|
Close Combat|Covet|Crabhammer|Cross Chop|Cross Poison|Crunch|Crush Claw|Cut|Darkest Lariat|Dig|Dive|Double Edge|
Double Hit|Double Kick|Dragon Ascent|Dragon Claw|Dragon Rush|Dragon Tail|Drain Punch|Draining Kiss|Drill Peck|
Drill Run|Dual Wingbeat|Dynamic Punch|Earthquake|Explosion|Extreme Speed|Facade|Fake Out|False Swipe|Feint|
Fell Stinger|Fire Fang|Fire Punch|First Impression|Flame Charge|Flame Wheel|Flare Blitz|Flip Turn|Fly|Focus Punch|
Force Palm|Foul Play|Fury Attack|Fury Cutter|Fury Swipes|Giga Impact|Grassy Glide|Hammer Arm|Head Smash|Headbutt|
High Horsepower|High Jump Kick|Horn Attack|Hyper Fang|Ice Fang|Ice Punch|Ice Spinner|Iron Head|Iron Tail|Knock Off|
Kowtow Cleave|Lash Out|Last Resort|Leaf Blade|Leech Life|Lick|Liquidation|Low Sweep|Lunge|Mach Punch|Mega Kick|
Mega Punch|Megahorn|Metal Claw|Meteor Assault|Meteor Mash|Misty Explosion|Night Slash|Outrage|Payback|Peck|
Phantom Force|Play Rough|Pluck|Poison Fang|Poison Jab|Poison Tail|Pounce|Pound|Power Whip|Precipice Blades|
Psychic Fangs|Pursuit|Quick Attack|Rage|Rage Fist|Raging Bull|Rapid Spin|Razor Shell|Retaliate|Revenge|Rollout|
Sacred Sword|Scratch|Self Destruct|Shadow Claw|Shadow Force|Shadow Punch|Shadow Sneak|Skitter Smack|Sky Attack|Slam|
Slash|Smart Strike|Solar Blade|Spark|Steel Wing|Stomp|Stomping Tantrum|Storm Throw|Strength|Submission|Sucker Punch|
Supercell Slam|Superpower|Tackle|Take Down|Temper Flare|Thief|Thrash|Throat Chop|Thunder Fang|Thunder Punch|
Trailblaze|Triple Axel|Twineedle|U Turn|Upper Hand|Vice Grip|Vine Whip|Vital Throw|Waterfall|Wave Crash|Wild Charge|
Wing Attack|Wood Hammer|Wrap|X Scissor|Zen Headbutt""".replace('\n', '').split('|'))

DIG = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def ak_id(i):
    return 'AK' + DIG[i // 36] + DIG[i % 36]


def safe(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def anim_life(text, cap):
    """Seconds to keep an effect: birth + stand animations; 0 = destroy at once (death animation only)."""
    life, death = 0.0, False
    for name, sec in re.findall(r'([A-Za-z][^,(]*?)\s*\(([\d.]+)s\)', text or ''):
        n = name.strip().lower()
        if n.startswith(('birth', 'bith', 'stand', 'attack', 'fffstand', 'fffbirth')):
            life += float(sec)
        elif n.startswith(('death', 'fffdea')):
            death = True
    if life <= 0.0:
        return 0.0 if death else 1.5
    return min(cap, max(0.8, life))


def load_libs():
    lib = json.load(open(os.path.join(HERE, 'fx_lib.json'), encoding='utf-8'))
    pw = json.load(open(os.path.join(HERE, 'fx_pool_pw.json'), encoding='utf-8'))
    return lib, pw


def resolve(name, lib, pw):
    """-> (path in the map, radius, animation text, source) ; source 'map' | 'pw' | 'war3'."""
    if name.startswith('war3:'):
        return name[5:], R_UNKNOWN, 'Birth (1.0s)', 'war3'
    if name.startswith('pw:'):
        key = name[3:]
        e = pw.get(key)
        if e is None or e['missing'] or e['clash']:
            raise SystemExit('fx_more: %s is not a usable Pokemon World model' % name)
        path = 'PkFx\\PW_%s.mdx' % safe(key)
        rr = RENDER_R.get(key, 0)
        if rr > 0:  # measured on a render (tools/v3411/fx_render_pw.json, analysis/render)
            return path, float(max(rr, 25)), e['anim'], 'pwr'
        # else the MDX extent (geometry only, particles not counted): never below PW_MIN_R, scale capped
        r = e['radius'] or 0
        return path, (max(r, PW_MIN_R) if r <= 5000 else R_UNKNOWN), e['anim'], 'pw'
    e = lib.get(name) or lib.get(name + ' (ENG)')
    if e is None:
        raise SystemExit('fx_more: model %s is not in the map (fx_lib.json)' % name)
    return e['path'], float(e['radius'] or R_UNKNOWN), e['anim'], 'map'


def move_index(script):
    """{move name: index} from the Mv_Label lines of the v3.4.10 script (damaging moves only)."""
    out = {}
    for i, label in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        m = re.match(r'(.*) \((\w+), power (\d+)\)', label)
        if m:
            out[m.group(1)] = int(i)
    return out


def first_free_index(script):
    used = [int(x) for x in re.findall(r'call SaveInteger\(PkFx_HT, (\d+), 0, ', script)]
    if not used:
        raise SystemExit('fx_more: no PkFx data in the script (base is not the v3.4.10 lineage?)')
    return max(used) + 1


def plan(script, abil, strings_secs):
    """abil: slk.Slk of Units\\AbilityData.slk; strings_secs: {id: {key: value}} of CampaignAbilityStrings.
    -> list of (index, ability id, header, layers, spec name, report text), set of Pokemon World models used."""
    lib, pw = load_libs()
    idx_of = move_index(script)
    rows = {abil.unquote(r.get(1)): r for r in abil.rows}

    def num(aid, col, default):
        try:
            return float(abil.get(rows[aid], col))
        except (TypeError, ValueError, KeyError):
            return default

    nxt = first_free_index(script)
    out, pw_used = [], set()

    def build_layers(mv, spec, mode, melee, want, base):
        layers, how = {}, []
        for key, slot in SLOT.items():
            name = spec.get(key)
            if not name:
                continue
            if not melee and key == 'p' and mode not in (0, 3):
                raise SystemExit('fx_more: %s: projectile on a base without a missile (%s)' % (mv, base))
            if not melee and key == 't' and mode not in (0, 3, 4):
                raise SystemExit('fx_more: %s: trail on a base without a line (%s)' % (mv, base))
            path, rad, anim, src = resolve(name, lib, pw)
            if src in ('pw', 'pwr'):
                pw_used.add(name[3:])
            if key + 's' in spec:
                scale = spec[key + 's']
            elif key == 'p':
                scale = max(PROJ_MIN, min(PROJ_MAX, want[key] / rad))
            else:
                scale = max(SCALE_MIN, min(SCALE_MAX, want[key] / rad))
            if src == 'pw' and key + 's' not in spec:
                scale = min(scale, PW_SCALE_MAX)
            elif src == 'pwr' and key + 's' not in spec:
                scale = min(scale, PW_RENDER_MAX)
            if key == 't':
                life = anim_life(anim, TRAIL_LIFE_MAX)
            elif key == 'p':
                life = 0.0
            else:
                life = anim_life(anim, LIFE_MAX)
            layers[slot] = (path, scale, life)
            how.append('%s=%s x%.2f' % (key, name, scale))
        return layers, how
    allspec = dict(SPEC)
    allspec.update(_v349_specs())  # v3.4.16: v3.4.9 moves with a Pokemon World layer
    for mv in sorted(allspec):
        spec = allspec[mv]
        if mv not in idx_of:
            raise SystemExit('fx_more: move %s not in the script' % mv)
        aid = ak_id(idx_of[mv])
        if aid not in rows:
            raise SystemExit('fx_more: %s (%s) has no ability row' % (mv, aid))
        base = abil.get(rows[aid], 'code')
        if base not in MODE_OF_BASE:
            raise SystemExit('fx_more: %s base %s unknown' % (mv, base))
        sec = strings_secs.get(aid, {})
        melee = mv in MELEE and base in MELEE_BASES
        mode = MODE_OF_BASE[base]
        area = num(aid, 'Area1', 0.0)
        speed = float(sec.get('Missilespeed') or 0)
        dash = float(spec.get('ds', DASH_SPEED)) if melee else 0.0
        if melee and base in MISSILE_BASES:
            speed = dash
        if speed <= 0:
            speed = 1100.0 if mode == 3 else 0.0
        length = num(aid, LINE_LEN_COL[base], num(aid, 'Rng1', 700.0)) if mode == 3 else 0.0
        waves = min(WAVES_MAX, int(num(aid, 'DataA1', 1))) if mode == 2 else 0
        if mode in (1, 2):
            want_h, ring_r = max(area, 200.0) * AREA_MULT, max(area, 200.0) * 0.8
        elif mode == 4:
            want_h, ring_r = max(area * 1.3, R_TARGET), max(area, 200.0) * 0.7
        elif mode == 3 and not melee:
            want_h, ring_r = max(R_LINE_END, area * 2.5), 190.0
        else:
            want_h, ring_r = R_TARGET, 170.0
        want = {'h': want_h, 'h2': want_h, 'h3': want_h, 'c': R_CAST, 'p': R_PROJ,
                't': max(area * 2.0, TRAIL_MIN), 'r': max(area, 200.0) * RING_FRAC}
        layers, how = build_layers(mv, spec, mode, melee, want, base)
        hd = dict(mode=mode, speed=speed, len=length, area=area, waves=max(waves, 1), ring_r=ring_r,
                  multi=spec.get('m', 1), tstep=float(spec.get('tstep', TRAIL_STEP)),
                  ring_n=spec.get('rn', 0) if SLOT['r'] in layers else 0, melee=melee, dash=dash, ids=[aid])
        kind = ('melee dash %d' % dash) if melee else ['missile', 'self', 'channel', 'line', 'target'][mode]
        out.append((nxt, aid, hd, layers, mv, '%s | %s | %s' % (base, kind, '; '.join(how))))
        nxt += 1
    # status moves: their 4 slot buttons
    import status_moves as SM
    names = [mv[0] for mv in SM.MOVES]
    for k, smv in enumerate(SM.MOVES):
        name, tt = smv[0], smv[3]
        spec = STATUS_SPEC.get(name)
        if spec is None:
            raise SystemExit('fx_more: status move %s has no STATUS_SPEC entry' % name)
        mi = SM.STAT_BASE + k
        ids = ['A%s%s%s' % (letter, DIG[mi // 36], DIG[mi % 36]) for letter in 'VWYZ']
        mode = 4 if tt == 1 else 1
        if mode == 4:
            want_h, ring_r = R_TARGET * 0.8, 200.0 * 0.7
        else:
            want_h, ring_r = max(STATUS_AREA, 200.0) * AREA_MULT * 0.7, 200.0 * 0.8
        want = {'h': want_h, 'h2': want_h, 'h3': want_h, 'c': R_CAST, 'p': R_PROJ, 't': TRAIL_MIN,
                'r': 200.0 * RING_FRAC}
        layers, how = build_layers(name, spec, mode, False, want, 'status')
        hd = dict(mode=mode, speed=0.0, len=0.0, area=STATUS_AREA, waves=1, ring_r=ring_r, multi=spec.get('m', 1),
                  tstep=TRAIL_STEP, ring_n=spec.get('rn', 0) if SLOT['r'] in layers else 0, melee=False, dash=0.0,
                  ids=ids, status=True)
        out.append((nxt, ids[0], hd, layers, name, 'status | %s | %s' % (['', 'self', '', '', 'target'][mode],
                                                                         '; '.join(how))))
        nxt += 1
    for b in BADGES:  # v3.4.16: gym badges (Fx_BadgeX)
        pw_used.add(b + 'Badge')
    extra = sorted(set(STATUS_SPEC) - set(names))
    if extra:
        raise SystemExit('fx_more: STATUS_SPEC names not in status_moves: %s' % extra)
    return out, pw_used


def jstr(path):
    return '"' + path.replace('\\', '\\\\') + '"'


def jass(entries):
    """-> (data functions text, ExecuteFunc call lines) ; functions PkFx_More1.. (12 moves each)."""
    blocks = []
    for idx, aid, hd, layers, _mv, _rep in entries:
        b = ["    call SaveInteger(PkFx_HT, '%s', 0, %d)" % (a, idx) for a in hd.get('ids', [aid])]
        b += ['    call SaveInteger(PkFx_HT, %d, 0, %d)' % (idx, hd['mode']),
             '    call SaveReal(PkFx_HT, %d, 1, %.1f)' % (idx, hd['speed']),
             '    call SaveReal(PkFx_HT, %d, 2, %.1f)' % (idx, hd['len']),
             '    call SaveReal(PkFx_HT, %d, 3, %.1f)' % (idx, hd['area']),
             '    call SaveInteger(PkFx_HT, %d, 4, %d)' % (idx, hd['waves']),
             '    call SaveReal(PkFx_HT, %d, 5, %.1f)' % (idx, hd['ring_r']),
             '    call SaveInteger(PkFx_HT, %d, 6, %d)' % (idx, hd['multi']),
             '    call SaveReal(PkFx_HT, %d, 7, %.1f)' % (idx, hd['tstep']),
             '    call SaveInteger(PkFx_HT, %d, 8, %d)' % (idx, hd['ring_n'])]
        if hd['melee']:
            b.append('    call SaveInteger(PkFx_HT, %d, 90, 1)' % idx)
            b.append('    call SaveReal(PkFx_HT, %d, 91, %.1f)' % (idx, hd['dash']))
        for slot, (path, scale, life) in sorted(layers.items()):
            b.append('    call SaveStr(PkFx_HT, %d, %d, %s)' % (idx, slot, jstr(path)))
            b.append('    call SaveReal(PkFx_HT, %d, %d, %.2f)' % (idx, slot + 1, scale))
            b.append('    call SaveReal(PkFx_HT, %d, %d, %.2f)' % (idx, slot + 2, life))
        blocks.append('\n'.join(b))
    funcs, calls = [], []
    for k in range(0, len(blocks), 12):
        name = 'PkFx_More%d' % (len(calls) + 1)
        funcs.append('function %s takes nothing returns nothing\n%s\nendfunction\n' % (name, '\n'.join(blocks[k:k + 12])))
        calls.append('    call ExecuteFunc("%s")  // v3.4.16' % name)
    return '// v3.4.16: effects for the moves v3.4.9 left without one (tools/v3411/fx_more.py)\n' + \
        '\n'.join(funcs) + '\n', '\n'.join(calls) + '\n'


def patch_script(s, entries):
    """Insert the data before PkFx_Init and run it after the v3.4.9 data (later saves win)."""
    data, calls = jass(entries)
    lines = []
    for g, b in enumerate(BADGES):
        lines.append('    set Fx_BadgeModel[%d] = %s' % (g, jstr('PkFx\\PW_%sBadge.mdx' % b)))
        lines.append('    set Fx_BadgeName[%d] = "%s"' % (g, b))
    import math
    import league_area as LA
    angle = {who: ang for who, _mon, ang in LA.STATUES}
    for k, (who, _model, hi, win) in enumerate(TRAINERS):
        lines += ["    set Fx_LeaderType[%d] = '%s'" % (k, TRAINER_ID[k]),
                  '    set Fx_LeaderName[%d] = %s' % (k, jstr(who)),
                  '    set Fx_LeaderHi[%d] = %s' % (k, jstr(hi)),
                  '    set Fx_LeaderWin[%d] = %s' % (k, jstr(win))]
        if k >= 8:
            a = math.radians(angle[who])
            r = LA.STATUE_R - 220.0
            lines += ['    set Fx_LeaderX[%d] = %.1f' % (k, LA.ARENA[0] + r * math.cos(a)),
                      '    set Fx_LeaderY[%d] = %.1f' % (k, LA.ARENA[1] + r * math.sin(a))]
    skins = iter(regional_skins())
    n = 0
    for ids, skin, _scale, name, (t1, t2) in REGIONAL:
        sid = next(skins)[0] if skin.startswith('pw:') else skin
        for wid in ids:
            lines += ["    set Fx_RegFrom[%d] = '%s'" % (n, wid), "    set Fx_RegSkin[%d] = '%s'" % (n, sid),
                      '    set Fx_RegName[%d] = %s' % (n, jstr(name)), '    set Fx_RegT1[%d] = %s' % (n, t1),
                      '    set Fx_RegT2[%d] = %s' % (n, t2 or '-1')]
            n += 1
    lines.append('    set Fx_RegN = %d' % n)
    lines += ["    set Fx_RocketType[%d] = '%s'" % (k, t) for k, t in enumerate(ROCKET_TYPES)]
    lib, pwp = load_libs()
    for ty, name in enumerate(MAX_FX):  # v3.4.16 Dynamax: Max Move blast per type (T_BUG .. T_WATER order)
        path, rad, _anim, _src = resolve(name, lib, pwp)
        lines += ['    set Fx_MaxFx[%d] = %s' % (ty, jstr(path)),
                  '    set Fx_MaxScale[%d] = %.2f' % (ty, max(0.2, min(6.0, MAX_R / rad)))]
    data += 'function PkFx_Badges takes nothing returns nothing\n%s\nendfunction\n' % '\n'.join(lines)
    calls += '    call ExecuteFunc("PkFx_Badges")  // v3.4.16\n'
    anchor = 'function PkFx_Init takes nothing returns nothing\n'
    if s.count(anchor) != 1:
        raise SystemExit('fx_more: PkFx_Init not found once')
    s = s.replace(anchor, data + '\n' + anchor)
    hook = '    call TriggerRegisterAnyUnitEventBJ(fxTrig, EVENT_PLAYER_UNIT_SPELL_EFFECT)\n'
    head = s.index(anchor)
    pos = s.index(hook, head)
    return s[:pos] + calls + s[pos:]


def parse_strings(txt):
    secs = {}
    for m in re.finditer(r'^\[(\w{4})\]\r?\n(.*?)(?=^\[|\Z)', txt, re.M | re.S):
        secs[m.group(1)] = dict(ln.split('=', 1) for ln in m.group(2).splitlines() if '=' in ln)
    return secs


def trainer_files():
    """{path in the Arena map: bytes}: trainer models (PkFx\\Trainer\\<model>.mdx) + the textures they ask for."""
    import mpq
    import mdxinfo

    class PW(mpq.MPQ):
        def _find_header(self):
            return 1024

    arc = PW(PW_MAP)
    game = ('textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\', 'environment\\', 'objects\\', 'ui\\')
    out = {}
    wanted = [('Unit\\%s.mdx' % model, 'PkFx\\Trainer\\%s.mdx' % model) for _w, model, _h, _x in TRAINERS]
    wanted += [('Unit\\%s.mdx' % f, 'PkFx\\Regional\\%s.mdx' % f) for _id, f, _s in regional_skins()]
    wanted += [('Unit\\%s.mdx' % model, 'PkFx\\Trainer\\%s.mdx' % model) for _i, _n, model, _s in ROCKET_NPC
               if model not in [t[1] for t in TRAINERS]]
    for src, dst in wanted:
        data = arc.read(src)
        out[dst] = data
        for t in mdxinfo.info(data)['textures']:
            if not t.lower().startswith(game):
                out[t] = arc.read(t)
    return out


def pw_files(names):
    """{path in the Arena map: bytes} for the Pokemon World models used (model + textures)."""
    import mpq

    class PW(mpq.MPQ):
        def _find_header(self):
            return 1024  # the header at 512 is a decoy

    _lib, pool = load_libs()
    arc = PW(PW_MAP)
    out = {}
    for key in sorted(names):
        e = pool[key]
        out['PkFx\\PW_%s.mdx' % safe(key)] = arc.read(e['path'])
        for t in e['tex']:
            out[t] = arc.read(t)
    return out
