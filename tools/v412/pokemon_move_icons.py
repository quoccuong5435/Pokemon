"""Assigns authentic Pokemon Move Icons and Range / Line AOE indicators to all 378 moves in Pokemon Arena.
1. Replaces generic Warcraft 3 ability icons with official Pokemon Type icons and signature move icons:
   (Blast Burn, Flamethrower, Bubble Beam, Razor Leaf, Hyper Beam, Outrage, Shadow Ball, Sky Attack,
    Brick Break, Tackle, Swift, Super Fang, String Shot, Thunder, Thunderbolt, Thunder Punch, Toxic,
    Twin Needle, Waterfall, Whirlpool, Pound, Double Slap, Body Slam, Sing, Disarming Voice, Rollout, Rest, etc.).
2. Annotates skill tooltips with exact geometric dimensions:
   - Line moves: [Line AOE] Range: X, Width: Y
   - Area moves: [Area AOE] Range: X, Radius: Y
   - Single target moves: [Single Target] Range: X
   - Self moves: [Self / Instant Buff]
"""
import re

B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

TYPE_NAMES = [
    'Bug', 'Dark', 'Dragon', 'Electr', 'Fairy', 'Fighting',
    'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice',
    'Normal', 'Poison', 'Psy', 'Rock', 'Steel', 'Water'
]

SPECIFIC_ICON_MAP = {
    'blast burn': 'ReplaceableTextures\\CommandButtons\\BTNBlast Burn (64 x 64).blp',
    'brick break': 'ReplaceableTextures\\CommandButtons\\BTNBreak Brick (64 x 64).blp',
    'bubble beam': 'ReplaceableTextures\\CommandButtons\\BTNBubble Beam (64 x 64).blp',
    'bubblebeam': 'ReplaceableTextures\\CommandButtons\\BTNBubble Beam (64 x 64).blp',
    'dig': 'ReplaceableTextures\\CommandButtons\\BTNDig (64 x 64).blp',
    'dragon breath': 'ReplaceableTextures\\CommandButtons\\BTNDragon Breath (64 x 64).blp',
    'feather dance': 'ReplaceableTextures\\CommandButtons\\BTNFeather Dance (64 x 64).blp',
    'fire punch': 'ReplaceableTextures\\CommandButtons\\BTNFire Punch (64 x 64).blp',
    'fire spin': 'ReplaceableTextures\\CommandButtons\\BTNFire Spin (64 x 64).blp',
    'flamethrower': 'ReplaceableTextures\\CommandButtons\\BTNFlame Thrower (64 x 64).blp',
    'frenzy plant': 'ReplaceableTextures\\CommandButtons\\BTNFrenzy Plant (64 x 64).blp',
    'hyper beam': 'ReplaceableTextures\\CommandButtons\\BTNHyper Beam (64 x 64).blp',
    'ice punch': 'ReplaceableTextures\\CommandButtons\\BTNIce Punch (64 x 64).blp',
    'leech seed': 'ReplaceableTextures\\CommandButtons\\BTNLeech Seed (64 x 64).blp',
    'magnitude': 'ReplaceableTextures\\CommandButtons\\BTNMagnitude (64 x 64).blp',
    'outrage': 'ReplaceableTextures\\CommandButtons\\BTNOut Rage (64 x 64).blp',
    'poison jab': 'ReplaceableTextures\\CommandButtons\\BTNPoison Jab (64 x 64).blp',
    'psychic': 'ReplaceableTextures\\CommandButtons\\BTNPsychic (64 x 64).blp',
    'psycho cut': 'ReplaceableTextures\\CommandButtons\\BTNPsycho Cut (64 x 64).blp',
    'razor leaf': 'ReplaceableTextures\\CommandButtons\\BTNRazol Leaf (64 x 64).blp',
    'shadow ball': 'ReplaceableTextures\\CommandButtons\\BTNShadow Ball (64 x 64).blp',
    'shock wave': 'ReplaceableTextures\\CommandButtons\\BTNShock Wave (64 x 64).blp',
    'sky attack': 'ReplaceableTextures\\CommandButtons\\BTNSky Attack (64 x 64).blp',
    'sandstorm': 'ReplaceableTextures\\CommandButtons\\btnsand_storm.blp',
    # Iconic signature and starter moves
    'tackle': 'ReplaceableTextures\\CommandButtons\\BTNSwift (64 x 64).blp',
    'swift': 'ReplaceableTextures\\CommandButtons\\BTNSwift (64 x 64).blp',
    'super fang': 'ReplaceableTextures\\CommandButtons\\BTNSuper Fang (64 x 64).blp',
    'string shot': 'ReplaceableTextures\\CommandButtons\\BTNString Shot (64 x 64).blp',
    'thunder': 'ReplaceableTextures\\CommandButtons\\BTNThunder (64 x 64).blp',
    'thunderbolt': 'ReplaceableTextures\\CommandButtons\\BTNThunder Bolt (64 x 64).blp',
    'thunder punch': 'ReplaceableTextures\\CommandButtons\\BTNThunder Punch (64 x 64).blp',
    'toxic': 'ReplaceableTextures\\CommandButtons\\BTNToxic (64 x 64).blp',
    'twin needle': 'ReplaceableTextures\\CommandButtons\\BTNTwi Needle (64 x 64).blp',
    'waterfall': 'ReplaceableTextures\\CommandButtons\\BTNWater Fall (64 x 64).blp',
    'whirlpool': 'ReplaceableTextures\\CommandButtons\\BTNWhirl Pool (64 x 64).blp',
    'pound': 'ReplaceableTextures\\CommandButtons\\BTNBreak Brick (64 x 64).blp',
    'double slap': 'ReplaceableTextures\\CommandButtons\\BTNBreak Brick (64 x 64).blp',
    'doubleslap': 'ReplaceableTextures\\CommandButtons\\BTNBreak Brick (64 x 64).blp',
    'body slam': 'ReplaceableTextures\\CommandButtons\\BTNSmash.blp',
    'sing': 'ReplaceableTextures\\CommandButtons\\BTNString Shot (64 x 64).blp',
    'disarming voice': 'ReplaceableTextures\\CommandButtons\\BTNSwift (64 x 64).blp',
    'rollout': 'ReplaceableTextures\\CommandButtons\\BTNMagnitude (64 x 64).blp',
    'rest': 'ReplaceableTextures\\CommandButtons\\BTNFull_Restore (64 x 64).blp',
    'quick attack': 'ReplaceableTextures\\CommandButtons\\BTNWindWalkOn.blp',
    'extreme speed': 'ReplaceableTextures\\CommandButtons\\BTNBoots.blp',
    'thunder shock': 'ReplaceableTextures\\CommandButtons\\BTNLightningShield.blp',
    'thundershock': 'ReplaceableTextures\\CommandButtons\\BTNLightningShield.blp',
    'spark': 'ReplaceableTextures\\CommandButtons\\BTNPurge.blp',
    'discharge': 'ReplaceableTextures\\CommandButtons\\BTNChainLightning.blp',
    'charge beam': 'ReplaceableTextures\\CommandButtons\\BTNManaFlare.blp',
    'wild charge': 'ReplaceableTextures\\CommandButtons\\BTNStaticField.blp',
    'volt tackle': 'ReplaceableTextures\\CommandButtons\\BTNMonsoon.blp',
    'thunder wave': 'ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp',
    'electro ball': 'ReplaceableTextures\\CommandButtons\\BTNLightningOrb.blp',
    'zap cannon': 'ReplaceableTextures\\CommandButtons\\BTNStormBolt.blp',
    'ember': 'ReplaceableTextures\\CommandButtons\\BTNFire.blp',
    'fire blast': 'ReplaceableTextures\\CommandButtons\\BTNFlameStrike.blp',
    'flare blitz': 'ReplaceableTextures\\CommandButtons\\BTNFireBolt.blp',
    'heat wave': 'ReplaceableTextures\\CommandButtons\\BTNBreathOfFire.blp',
    'inferno': 'ReplaceableTextures\\CommandButtons\\BTNImmolationOn.blp',
    'eruption': 'ReplaceableTextures\\CommandButtons\\BTNVolcano.blp',
    'will-o-wisp': 'ReplaceableTextures\\CommandButtons\\BTNWallOfFire.blp',
    'water gun': 'ReplaceableTextures\\CommandButtons\\BTNSummonWaterElemental.blp',
    'hydro pump': 'ReplaceableTextures\\CommandButtons\\BTNCrushingWave.blp',
    'surf': 'ReplaceableTextures\\CommandButtons\\BTNTsunami.blp',
    'aqua tail': 'ReplaceableTextures\\CommandButtons\\BTNWaterElemental.blp',
    'aqua jet': 'ReplaceableTextures\\CommandButtons\\BTNFrost.blp',
    'muddy water': 'ReplaceableTextures\\CommandButtons\\BTNGeyser.blp',
    'vine whip': 'ReplaceableTextures\\CommandButtons\\BTNEntanglingRoots.blp',
    'solar beam': 'ReplaceableTextures\\CommandButtons\\BTNStarfall.blp',
    'giga drain': 'ReplaceableTextures\\CommandButtons\\BTNLifeDrain.blp',
    'energy ball': 'ReplaceableTextures\\CommandButtons\\BTNNaturesTouch.blp',
    'leaf blade': 'ReplaceableTextures\\CommandButtons\\BTNThorns.blp',
    'petal blizzard': 'ReplaceableTextures\\CommandButtons\\BTN Tranquility.blp',
    'ice beam': 'ReplaceableTextures\\CommandButtons\\BTNFrostBolt.blp',
    'blizzard': 'ReplaceableTextures\\CommandButtons\\BTNBlizzard.blp',
    'icy wind': 'ReplaceableTextures\\CommandButtons\\BTNFrostArmor.blp',
    'ice shard': 'ReplaceableTextures\\CommandButtons\\BTNColdArrows.blp',
    'sheer cold': 'ReplaceableTextures\\CommandButtons\\BTNGlacier.blp',
    'earthquake': 'ReplaceableTextures\\CommandButtons\\BTNEarthquake.blp',
    'earth power': 'ReplaceableTextures\\CommandButtons\\BTNImpale.blp',
    'mud-slap': 'ReplaceableTextures\\CommandButtons\\BTNWarStomp.blp',
    'rock slide': 'ReplaceableTextures\\CommandButtons\\BTNWGolemStormBolt.blp',
    'stone edge': 'ReplaceableTextures\\CommandButtons\\BTNStoneForm.blp',
    'rock tomb': 'ReplaceableTextures\\CommandButtons\\BTNStone.blp',
    'ancient power': 'ReplaceableTextures\\CommandButtons\\BTNResistantSkin.blp',
    'air slash': 'ReplaceableTextures\\CommandButtons\\BTNTornado.blp',
    'aerial ace': 'ReplaceableTextures\\CommandButtons\\BTNWarEagle.blp',
    'hurricane': 'ReplaceableTextures\\CommandButtons\\BTNCyclone.blp',
    'brave bird': 'ReplaceableTextures\\CommandButtons\\BTNPhoenix.blp',
    'wing attack': 'ReplaceableTextures\\CommandButtons\\BTNStormCrow.blp',
    'close combat': 'ReplaceableTextures\\CommandButtons\\BTNGauntletsOfOgrePower.blp',
    'aura sphere': 'ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp',
    'cross chop': 'ReplaceableTextures\\CommandButtons\\BTNCriticalStrike.blp',
    'dynamic punch': 'ReplaceableTextures\\CommandButtons\\BTNBash.blp',
    'confusion': 'ReplaceableTextures\\CommandButtons\\BTNControlMagic.blp',
    'psybeam': 'ReplaceableTextures\\CommandButtons\\BTNManaBurn.blp',
    'future sight': 'ReplaceableTextures\\CommandButtons\\BTNFarSight.blp',
    'zen headbutt': 'ReplaceableTextures\\CommandButtons\\BTNSpellSteal.blp',
    'lick': 'Spells\\Wight\\Icons\\BTNWightBreath.blp',
    'night shade': 'Spells\\Wight\\Icons\\BTNWightAuraOfDeath.blp',
    'shadow claw': 'Spells\\Wight\\Icons\\BTNWightHandOfDeath.blp',
    'hex': 'Spells\\Wight\\Icons\\BTNWightSpirits.blp',
    'phantom force': 'Spells\\Wight\\Icons\\BTNWightScythe.blp',
    'bite': 'ReplaceableTextures\\CommandButtons\\BTNDevour.blp',
    'crunch': 'ReplaceableTextures\\CommandButtons\\BTNCannibalize.blp',
    'dark pulse': 'ReplaceableTextures\\CommandButtons\\BTNOrbOfDarkness.blp',
    'night slash': 'ReplaceableTextures\\CommandButtons\\BTNShadowStrike.blp',
    'feint attack': 'ReplaceableTextures\\CommandButtons\\BTNAmbush.blp',
    'snarl': 'ReplaceableTextures\\CommandButtons\\BTNHowlOfTerror.blp',
    'sludge bomb': 'ReplaceableTextures\\CommandButtons\\BTNAcidBomb.blp',
    'acid': 'ReplaceableTextures\\CommandButtons\\BTNCorrosiveBreath.blp',
    'poison sting': 'ReplaceableTextures\\CommandButtons\\BTNEnvenomedSpear.blp',
    'venoshock': 'ReplaceableTextures\\CommandButtons\\BTNPlagueCloud.blp',
    'dragon claw': 'ReplaceableTextures\\CommandButtons\\BTNRedDragonDevour.blp',
    'dragon pulse': 'ReplaceableTextures\\CommandButtons\\BTNOrbOfFire.blp',
    'draco meteor': 'ReplaceableTextures\\CommandButtons\\BTNInfernal.blp',
    'dragon tail': 'ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp',
    'iron tail': 'ReplaceableTextures\\CommandButtons\\BTNArcaniteMelee.blp',
    'metal claw': 'ReplaceableTextures\\CommandButtons\\BTNSteelMelee.blp',
    'flash cannon': 'ReplaceableTextures\\CommandButtons\\BTNThoriumRanged.blp',
    'meteor mash': 'ReplaceableTextures\\CommandButtons\\BTNThoriumMelee.blp',
    'moonblast': 'ReplaceableTextures\\CommandButtons\\BTNMoonStone.blp',
    'dazzling gleam': 'ReplaceableTextures\\CommandButtons\\BTNStarWand.blp',
    'play rough': 'ReplaceableTextures\\CommandButtons\\BTNFaerieFire.blp',
    'x-scissor': 'ReplaceableTextures\\CommandButtons\\BTNCarrionSwarm.blp',
    'bug buzz': 'ReplaceableTextures\\CommandButtons\\BTNLocustSwarm.blp',
    'signal beam': 'ReplaceableTextures\\CommandButtons\\BTNParasite.blp',
}

# Rich pools of 100% square bordered Warcraft 3 spell icons by type (0..17) so no move ever uses round flat BTNPkmn*.blp badges
TYPE_SQUARE_ICON_POOLS = {
    0: [  # Bug
        'ReplaceableTextures\\CommandButtons\\BTNCarrionSwarm.blp',
        'ReplaceableTextures\\CommandButtons\\BTNLocustSwarm.blp',
        'ReplaceableTextures\\CommandButtons\\BTNParasite.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWeb.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSpiderGreen.blp',
    ],
    1: [  # Dark
        'ReplaceableTextures\\CommandButtons\\BTNOrbOfDarkness.blp',
        'ReplaceableTextures\\CommandButtons\\BTNShadowStrike.blp',
        'ReplaceableTextures\\CommandButtons\\BTNAmbush.blp',
        'ReplaceableTextures\\CommandButtons\\BTNDevour.blp',
        'ReplaceableTextures\\CommandButtons\\BTNHowlOfTerror.blp',
        'Spells\\Wight\\Icons\\BTNWightScythe.blp',
    ],
    2: [  # Dragon
        'ReplaceableTextures\\CommandButtons\\BTNRedDragonDevour.blp',
        'ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp',
        'ReplaceableTextures\\CommandButtons\\BTNDragonHawk.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBreathOfFire.blp',
        'ReplaceableTextures\\CommandButtons\\BTNInfernal.blp',
    ],
    3: [  # Electric
        'ReplaceableTextures\\CommandButtons\\BTNChainLightning.blp',
        'ReplaceableTextures\\CommandButtons\\BTNLightningShield.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPurge.blp',
        'ReplaceableTextures\\CommandButtons\\BTNMonsoon.blp',
        'ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp',
        'ReplaceableTextures\\CommandButtons\\BTNStormBolt.blp',
        'ReplaceableTextures\\CommandButtons\\BTNManaFlare.blp',
    ],
    4: [  # Fairy
        'ReplaceableTextures\\CommandButtons\\BTNMoonStone.blp',
        'ReplaceableTextures\\CommandButtons\\BTNStarWand.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFaerieFire.blp',
        'ReplaceableTextures\\CommandButtons\\BTNStarfall.blp',
        'ReplaceableTextures\\CommandButtons\\BTNHeal.blp',
    ],
    5: [  # Fighting
        'ReplaceableTextures\\CommandButtons\\BTNGauntletsOfOgrePower.blp',
        'ReplaceableTextures\\CommandButtons\\BTNCriticalStrike.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBash.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSmash.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBerserk.blp',
    ],
    6: [  # Fire
        'ReplaceableTextures\\CommandButtons\\BTNFlameStrike.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBreathOfFire.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFireBolt.blp',
        'ReplaceableTextures\\CommandButtons\\BTNImmolationOn.blp',
        'ReplaceableTextures\\CommandButtons\\BTNIncinerate.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWallOfFire.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFire.blp',
    ],
    7: [  # Flying
        'ReplaceableTextures\\CommandButtons\\BTNTornado.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWarEagle.blp',
        'ReplaceableTextures\\CommandButtons\\BTNCyclone.blp',
        'ReplaceableTextures\\CommandButtons\\BTNStormCrow.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWindWalkOn.blp',
    ],
    8: [  # Ghost
        'Spells\\Wight\\Icons\\BTNWightHandOfDeath.blp',
        'Spells\\Wight\\Icons\\BTNWightSpirits.blp',
        'Spells\\Wight\\Icons\\BTNWightAuraOfDeath.blp',
        'Spells\\Wight\\Icons\\BTNWightBreath.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPossession.blp',
        'ReplaceableTextures\\CommandButtons\\BTNDeathCoil.blp',
    ],
    9: [  # Grass
        'ReplaceableTextures\\CommandButtons\\BTNEntanglingRoots.blp',
        'ReplaceableTextures\\CommandButtons\\BTNLifeDrain.blp',
        'ReplaceableTextures\\CommandButtons\\BTNThorns.blp',
        'ReplaceableTextures\\CommandButtons\\BTNNaturesTouch.blp',
        'ReplaceableTextures\\CommandButtons\\BTNRejuvenation.blp',
    ],
    10: [  # Ground
        'ReplaceableTextures\\CommandButtons\\BTNEarthquake.blp',
        'ReplaceableTextures\\CommandButtons\\BTNImpale.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWarStomp.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPulverize.blp',
    ],
    11: [  # Ice
        'ReplaceableTextures\\CommandButtons\\BTNFrostBolt.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBlizzard.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFrostArmor.blp',
        'ReplaceableTextures\\CommandButtons\\BTNColdArrows.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBreathOfFrost.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFreezingBreath.blp',
    ],
    12: [  # Normal
        'ReplaceableTextures\\CommandButtons\\BTNWindWalkOn.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSmash.blp',
        'ReplaceableTextures\\CommandButtons\\BTNBattleRoar.blp',
        'ReplaceableTextures\\CommandButtons\\BTNInnerFire.blp',
        'ReplaceableTextures\\CommandButtons\\BTNThunderclap.blp',
        'ReplaceableTextures\\CommandButtons\\BTNCommand.blp',
    ],
    13: [  # Poison
        'ReplaceableTextures\\CommandButtons\\BTNAcidBomb.blp',
        'ReplaceableTextures\\CommandButtons\\BTNCorrosiveBreath.blp',
        'ReplaceableTextures\\CommandButtons\\BTNEnvenomedSpear.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPlagueCloud.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPoisonArrow.blp',
    ],
    14: [  # Psychic
        'ReplaceableTextures\\CommandButtons\\BTNControlMagic.blp',
        'ReplaceableTextures\\CommandButtons\\BTNManaBurn.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFarSight.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSpellSteal.blp',
        'ReplaceableTextures\\CommandButtons\\BTNPolymorph.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSlow.blp',
    ],
    15: [  # Rock
        'ReplaceableTextures\\CommandButtons\\BTNStone.blp',
        'ReplaceableTextures\\CommandButtons\\BTNStoneForm.blp',
        'ReplaceableTextures\\CommandButtons\\BTNGolemStormBolt.blp',
        'ReplaceableTextures\\CommandButtons\\BTNResistantSkin.blp',
    ],
    16: [  # Steel
        'ReplaceableTextures\\CommandButtons\\BTNArcaniteMelee.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSteelMelee.blp',
        'ReplaceableTextures\\CommandButtons\\BTNThoriumRanged.blp',
        'ReplaceableTextures\\CommandButtons\\BTNThoriumMelee.blp',
        'ReplaceableTextures\\CommandButtons\\BTNDevotion.blp',
    ],
    17: [  # Water
        'ReplaceableTextures\\CommandButtons\\BTNCrushingWave.blp',
        'ReplaceableTextures\\CommandButtons\\BTNSummonWaterElemental.blp',
        'ReplaceableTextures\\CommandButtons\\BTNWaterElemental.blp',
        'ReplaceableTextures\\CommandButtons\\BTNFrost.blp',
        'ReplaceableTextures\\CommandButtons\\BTNMonsoon.blp',
    ],
}

SOURCE_ICON_FILES = [
    'BTNBlast Burn (64 x 64).blp',
    'BTNBreak Brick (64 x 64).blp',
    'BTNBubble Beam (64 x 64).blp',
    'BTNDig (64 x 64).blp',
    'BTNDragon Breath (64 x 64).blp',
    'BTNFeather Dance (64 x 64).blp',
    'BTNFire Punch (64 x 64).blp',
    'BTNFire Spin (64 x 64).blp',
    'BTNFlame Thrower (64 x 64).blp',
    'BTNFrenzy Plant (64 x 64).blp',
    'BTNHyper Beam (64 x 64).blp',
    'BTNIce Punch (64 x 64).blp',
    'BTNLeech Seed (64 x 64).blp',
    'BTNMagnitude (64 x 64).blp',
    'BTNOut Rage (64 x 64).blp',
    'BTNPoison Jab (64 x 64).blp',
    'BTNPsychic (64 x 64).blp',
    'BTNPsycho Cut (64 x 64).blp',
    'BTNRazol Leaf (64 x 64).blp',
    'BTNShadow Ball (64 x 64).blp',
    'BTNShock Wave (64 x 64).blp',
    'BTNSky Attack (64 x 64).blp',
    'btnsand_storm.blp',
    'BTNSwift (64 x 64).blp',
    'BTNSuper Fang (64 x 64).blp',
    'BTNString Shot (64 x 64).blp',
    'BTNThunder (64 x 64).blp',
    'BTNThunder Bolt (64 x 64).blp',
    'BTNThunder Punch (64 x 64).blp',
    'BTNToxic (64 x 64).blp',
    'BTNTwi Needle (64 x 64).blp',
    'BTNWater Fall (64 x 64).blp',
    'BTNWhirl Pool (64 x 64).blp',
    'BTNFull_Restore (64 x 64).blp',
]


def from_b36(tag: str) -> int:
    """Decodes a 2-char base-36 tag into move index."""
    if len(tag) != 2:
        return -1
    d1 = B36.find(tag[0])
    d2 = B36.find(tag[1])
    if d1 == -1 or d2 == -1:
        return -1
    return d1 * 36 + d2


def parse_move_data_from_jass(jass_code: str):
    """Extracts Mv_Type, Mv_Label and Mv_TT mappings from war3map.j."""
    mv_types = {int(a): int(b) for a, b in re.findall(r'set\s+Mv_Type\[(\d+)\]\s*=\s*(\d+)', jass_code)}
    mv_labels = {int(a): b for a, b in re.findall(r'set\s+Mv_Label\[(\d+)\]\s*=\s*"([^"]+)"', jass_code)}
    mv_tts = {int(a): int(b) for a, b in re.findall(r'set\s+Mv_TT\[(\d+)\]\s*=\s*(\d+)', jass_code)}
    return mv_types, mv_labels, mv_tts


def get_move_icon(m_idx: int, mv_types: dict, mv_labels: dict, orig_av_icon: str = None) -> str:
    """Returns a 100% square bordered spell icon path for move index m_idx (never flat round BTNPkmn*.blp badges)."""
    label = mv_labels.get(m_idx, '')
    clean_name = label.split('(')[0].strip().lower()
    if clean_name in SPECIFIC_ICON_MAP:
        return SPECIFIC_ICON_MAP[clean_name]
    t_idx = mv_types.get(m_idx, 12)  # Default Normal
    pool = TYPE_SQUARE_ICON_POOLS.get(t_idx, TYPE_SQUARE_ICON_POOLS[12])
    # If original AV icon exists, is not a flat BTNPkmn circle, and is not over-repeated (like StormBolt/Bash), use it;
    # otherwise pick a varied thematic square spell icon from the type pool
    if orig_av_icon and 'BTNPkmn' not in orig_av_icon and not any(g in orig_av_icon for g in ('BTNStormBolt.blp', 'BTNBash.blp', 'BTNSmash.blp')):
        return orig_av_icon
    return pool[m_idx % len(pool)]


def get_move_indicator(m_idx: int, tt: int, rng: str, area: str) -> str:
    """Builds a colored geometry & range indicator banner for move tooltips."""
    if tt == 3:  # Point Line AOE
        r_str = rng if rng and rng != 'None' else '700'
        w_str = area if area and area != 'None' else '125'
        return f"|cff5dade2[Line AOE]|r |cffffcc00Range: {r_str}|r, |cff7ed6dfWidth: {w_str}|r"
    elif tt == 2:  # Area / Circle AOE
        r_str = rng if rng and rng != 'None' else '800'
        rad_str = area if area and area != 'None' else '300'
        return f"|cff5dade2[Area AOE]|r |cffffcc00Range: {r_str}|r, |cff7ed6dfRadius: {rad_str}|r"
    elif tt == 1:  # Single Target
        r_str = rng if rng and rng != 'None' else '600'
        extra = f", |cff7ed6dfArea: {area}|r" if area and area != 'None' else ""
        return f"|cff5dade2[Single Target]|r |cffffcc00Range: {r_str}|r{extra}"
    else:  # Instant / Self
        return "|cff5dade2[Self / Instant Buff]|r"


def patch_ability_strings(strings_txt: str, jass_code: str, abil_slk=None, orig_strings_txt: str = None) -> str:
    """Updates CampaignAbilityStrings.txt with 100% uniform square Pokemon move icons and range indicators."""
    mv_types, mv_labels, mv_tts = parse_move_data_from_jass(jass_code)

    # Split precisely on section headers at line starts: [XXXX]
    sections = re.split(r'(?m)^\[([A-Za-z0-9_]{4})\]\r?\n', strings_txt)
    ref_sections = re.split(r'(?m)^\[([A-Za-z0-9_]{4})\]\r?\n', orig_strings_txt) if orig_strings_txt else sections

    # First pass: collect original AV icons and names for all moves (including status moves 378..387)
    orig_av_icons = {}
    for i in range(1, len(ref_sections), 2):
        sec_name = ref_sections[i]
        body = ref_sections[i + 1]
        if sec_name.startswith('AV') and len(sec_name) == 4:
            m_idx = from_b36(sec_name[2:4])
            if m_idx >= 0:
                m_art = re.search(r'Art=([^\r\n]+)', body)
                if m_art:
                    orig_av_icons[m_idx] = m_art.group(1).strip()
                if m_idx not in mv_labels:
                    m_name = re.search(r'Name=([^\r\n]+)', body)
                    if m_name:
                        mv_labels[m_idx] = m_name.group(1).strip()

    for i in range(1, len(sections), 2):
        sec_name = sections[i]
        body = sections[i + 1]
        if sec_name.startswith('AV') and len(sec_name) == 4:
            m_idx = from_b36(sec_name[2:4])
            if m_idx >= 0:
                if m_idx not in orig_av_icons:
                    m_art = re.search(r'Art=([^\r\n]+)', body)
                    if m_art:
                        orig_av_icons[m_idx] = m_art.group(1).strip()
                if m_idx not in mv_labels:
                    m_name = re.search(r'Name=([^\r\n]+)', body)
                    if m_name:
                        mv_labels[m_idx] = m_name.group(1).strip()

    # Precompute synchronized square move icons for all move indices
    icons_by_idx = {}
    all_indices = set(mv_types.keys()) | set(orig_av_icons.keys())
    for m_idx in sorted(all_indices):
        icons_by_idx[m_idx] = get_move_icon(m_idx, mv_types, mv_labels, orig_av_icons.get(m_idx))

    result = [sections[0]]

    patched_count = 0
    indicator_count = 0

    for i in range(1, len(sections), 2):
        sec_name = sections[i]
        body = sections[i + 1]
        prefix = sec_name[:2]

        if prefix in ('AV', 'AW', 'AY', 'AZ', 'AK') and len(sec_name) == 4:
            m_idx = from_b36(sec_name[2:4])
            if m_idx in icons_by_idx:
                icon = icons_by_idx[m_idx]

                # 1. Update Art
                if 'Art=' in body:
                    body = re.sub(r'Art=[^\r\n]+', lambda _: f'Art={icon}', body, count=1)
                else:
                    body = f'Art={icon}\n' + body

                # 2. Update Ubertip with range/shape indicator banner
                tt = mv_tts.get(m_idx, 0)
                rng = None
                area = None
                if abil_slk:
                    row = abil_slk.find(sec_name)
                    if row:
                        rng = abil_slk.get(row, 'Rng1')
                        area = abil_slk.get(row, 'Area1')
                indicator = get_move_indicator(m_idx, tt, rng, area)

                def _replace_ubertip(m):
                    nonlocal indicator_count
                    val = m.group(1).strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    # Avoid double indicator if already present
                    if '[Line AOE]' in val or '[Area AOE]' in val or '[Single Target]' in val or '[Self / Instant' in val:
                        return m.group(0)
                    indicator_count += 1
                    return f'Ubertip="{indicator}|n{val}"'

                body = re.sub(r'Ubertip=([^\r\n]+)', _replace_ubertip, body, count=1)

                result.append(f'[{sec_name}]\n{body}')
                patched_count += 1
                continue

        result.append(f'[{sec_name}]\n{body}')

    print(f"[pokemon_move_icons] Patched {patched_count} ability sections with authentic Pokemon icons.")
    print(f"[pokemon_move_icons] Added geometric range indicators to {indicator_count} move tooltips.")
    return ''.join(result)


def patch_ability_slk(abil_slk, jass_code: str):
    """Enables on-ground AOE targeting reticle (Option bit 2) and sets Area1 in AbilityData.slk."""
    _mv_types, _mv_labels, mv_tts = parse_move_data_from_jass(jass_code)
    col = abil_slk.name_to_x
    datac1_x = col.get('DataC1')
    area1_x = col.get('Area1')
    count = 0
    for r in abil_slk.rows:
        aid = abil_slk.unquote(r.get(1))
        if not aid or len(aid) != 4:
            continue
        prefix = aid[:2]
        if prefix in ('AV', 'AW', 'AY', 'AZ', 'AK'):
            m_idx = from_b36(aid[2:4])
            tt = mv_tts.get(m_idx, 0)
            if tt == 2:  # ONLY true Area AoE moves get on-ground circular reticle
                # Bit 2 = targeting image on ground
                if datac1_x:
                    cur_c1 = r.get(datac1_x, '1')
                    try:
                        c1_val = int(cur_c1.strip('"')) if cur_c1 else 1
                    except ValueError:
                        c1_val = 1
                    r[datac1_x] = str(c1_val | 2)
                # Set Area1
                if area1_x:
                    cur_a = r.get(area1_x)
                    need_set = False
                    if not cur_a or cur_a == 'None':
                        need_set = True
                    else:
                        try:
                            if float(cur_a.strip('"')) < 120.0:
                                need_set = True
                        except ValueError:
                            need_set = True
                    if need_set:
                        r[area1_x] = '300'
                count += 1
            else:
                # Line moves (tt == 3, e.g. Quick Attack) and Single Target (tt == 1): strip bit 2 (no ground circle)
                if datac1_x:
                    cur_c1 = r.get(datac1_x, '1')
                    try:
                        c1_val = int(cur_c1.strip('"')) if cur_c1 else 1
                    except ValueError:
                        c1_val = 1
                    r[datac1_x] = str(c1_val & ~2)
    print(f"[pokemon_move_icons] Enabled on-ground MOBA targeting indicators for {count} AOE abilities in AbilityData.slk.")


def patch_script(s: str) -> str:
    """Enables Reforged native MOBA target indicator system."""
    old_init = "call Mega_Init()"
    new_init = "call Mega_Init()\ncall BlzEnableTargetIndicator(true)"
    if old_init in s and "call BlzEnableTargetIndicator" not in s:
        s = s.replace(old_init, new_init, 1)
        print("[pokemon_move_icons] Added BlzEnableTargetIndicator(true) to main().")
    return s


def extra_icon_files(mpq_archive) -> dict:
    """Returns extra files to write to the map archive to ensure all custom move icons are found."""
    extras = {}
    listfile_lower = {f.lower(): f for f in mpq_archive.listfile()}
    for fname in SOURCE_ICON_FILES:
        target_path = f"ReplaceableTextures\\CommandButtons\\{fname}"
        if target_path.lower() not in listfile_lower:
            src = listfile_lower.get(fname.lower())
            if src:
                extras[target_path] = mpq_archive.read(src)
    return extras
