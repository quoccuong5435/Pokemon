"""v3.4.12: the 58 status moves (buff / defense / debuff) of the approved plan. Move index = STAT_BASE + position.

Action codes (Fx_HT[100000 + move] key 40, read by Fx_DoStatusMove): 1 own stages, 2 own stages x2 in harsh sun
(Growth), 3 Focus Energy, 4 Belly Drum, 5 Protect, 6 heal key42 permille, 7 heal by weather, 8 Rest, 9 Reflect,
10 Light Screen, 11 Substitute, 12 heal over time, 13 Wish, 20 stages of enemies around the user, 21 stages of the
target, 22 accuracy down, 23 status (key42 kind, key43 chance, key44 1 = Grass immune, 2 = Ground immune), 24 Yawn,
25 Confuse Ray, 26 Swagger, 27 Leech Seed, 28 Taunt.
Stages: own in keys 11..15, target in keys 21..25 (1 Atk 2 Def 3 SpA 4 SpD 5 Spe).
"""
STAT_BASE = 320
ICON = 'ReplaceableTextures\\CommandButtons\\%s.blp'

# (name, type, action, target 0 none / 1 unit, {param: value}, cooldown, mana, icon, description)
MOVES = [
    # ---- buffs
    ('Swords Dance', 'normal', 1, 0, {11: 2}, 20, 80, 'BTNBerserk', '+2 Attack for 12 seconds.'),
    ('Nasty Plot', 'dark', 1, 0, {13: 2}, 20, 80, 'BTNDevourMagic', '+2 Sp. Atk for 12 seconds.'),
    ('Dragon Dance', 'dragon', 1, 0, {11: 1, 15: 1}, 20, 80, 'BTNUnholyFrenzy', '+1 Attack and +1 Speed for 12 seconds.'),
    ('Calm Mind', 'psychic', 1, 0, {13: 1, 14: 1}, 20, 80, 'BTNBrilliance', '+1 Sp. Atk and +1 Sp. Def for 12 seconds.'),
    ('Bulk Up', 'fighting', 1, 0, {11: 1, 12: 1}, 20, 80, 'BTNAnimalWarTraining',
     '+1 Attack and +1 Defense for 12 seconds.'),
    ('Quiver Dance', 'bug', 1, 0, {13: 1, 14: 1, 15: 1}, 20, 90, 'BTNStrengthOfTheMoon',
     '+1 Sp. Atk, +1 Sp. Def and +1 Speed for 12 seconds.'),
    ('Shell Smash', 'normal', 1, 0, {11: 2, 13: 2, 15: 2, 12: -1, 14: -1}, 25, 100, 'BTNMetamorphosis',
     '+2 Attack, +2 Sp. Atk, +2 Speed, -1 Defense and -1 Sp. Def for 12 seconds.'),
    ('Agility', 'psychic', 1, 0, {15: 2}, 20, 60, 'BTNEvasion', '+2 Speed for 12 seconds.'),
    ('Rock Polish', 'rock', 1, 0, {15: 2}, 20, 60, 'BTNBootsOfSpeed', '+2 Speed for 12 seconds.'),
    ('Work Up', 'normal', 1, 0, {11: 1, 13: 1}, 20, 70, 'BTNBattleRoar', '+1 Attack and +1 Sp. Atk for 12 seconds.'),
    ('Growth', 'normal', 2, 0, {11: 1, 13: 1}, 20, 70, 'BTNNatureTouchGrow',
     '+1 Attack and +1 Sp. Atk for 12 seconds (+2 each in harsh sun).'),
    ('Curse', 'ghost', 1, 0, {11: 1, 12: 1, 15: -1}, 20, 70, 'BTNSoulBurn',
     '+1 Attack, +1 Defense and -1 Speed for 12 seconds.'),
    ('Focus Energy', 'normal', 3, 0, {}, 20, 60, 'BTNStasisTrap',
     'The next 3 attacks or moves have a 50% chance to deal x1.5 damage.'),
    ('Belly Drum', 'normal', 4, 0, {}, 30, 50, 'BTNSacrifice', 'Loses 50% max HP to raise Attack to +4 (needs more than half HP).'),
    # ---- defense
    ('Protect', 'normal', 5, 0, {}, 18, 60, 'BTNDivineIntervention', 'Takes no damage and no status for 1.5 seconds.'),
    ('Detect', 'fighting', 5, 0, {}, 18, 60, 'BTNSpellBreakerMagicDefend',
     'Takes no damage and no status for 1.5 seconds.'),
    ('Recover', 'normal', 6, 0, {42: 500}, 30, 100, 'BTNHeal', 'Heals 50% of its max HP.'),
    ('Roost', 'flying', 6, 0, {42: 500}, 30, 100, 'BTNRavenForm', 'Heals 50% of its max HP.'),
    ('Slack Off', 'normal', 6, 0, {42: 500}, 30, 100, 'BTNScrollOfHealing', 'Heals 50% of its max HP.'),
    ('Soft-Boiled', 'normal', 6, 0, {42: 500}, 30, 100, 'BTNRejuvenation', 'Heals 50% of its max HP.'),
    ('Synthesis', 'grass', 7, 0, {}, 30, 100, 'BTNEntanglingRoots',
     'Heals 50% of its max HP (66% in harsh sun, 25% in rain, sandstorm or hail).'),
    ('Moonlight', 'fairy', 7, 0, {}, 30, 100, 'BTNMoonStone',
     'Heals 50% of its max HP (66% in harsh sun, 25% in rain, sandstorm or hail).'),
    ('Morning Sun', 'normal', 7, 0, {}, 30, 100, 'BTNStarWand',
     'Heals 50% of its max HP (66% in harsh sun, 25% in rain, sandstorm or hail).'),
    ('Rest', 'psychic', 8, 0, {}, 40, 120, 'BTNSleep', 'Fully heals and cures its status, then sleeps for 3 seconds.'),
    ('Iron Defense', 'steel', 1, 0, {12: 2}, 20, 70, 'BTNArmorGolem', '+2 Defense for 12 seconds.'),
    ('Acid Armor', 'poison', 1, 0, {12: 2}, 20, 70, 'BTNAcidBomb', '+2 Defense for 12 seconds.'),
    ('Amnesia', 'psychic', 1, 0, {14: 2}, 20, 70, 'BTNSpellShieldAmulet', '+2 Sp. Def for 12 seconds.'),
    ('Cosmic Power', 'psychic', 1, 0, {12: 1, 14: 1}, 20, 70, 'BTNStarfall', '+1 Defense and +1 Sp. Def for 12 seconds.'),
    ('Reflect', 'psychic', 9, 0, {}, 30, 100, 'BTNDefend', 'Allies within 600 take 30% less physical damage for 8 seconds.'),
    ('Light Screen', 'psychic', 10, 0, {}, 30, 100, 'BTNLightningShield',
     'Allies within 600 take 30% less special damage for 8 seconds.'),
    ('Substitute', 'normal', 11, 0, {}, 25, 80, 'BTNMirrorImage',
     'Loses 25% max HP to get a shield of that much for 10 seconds; no status while it holds.'),
    ('Aqua Ring', 'water', 12, 0, {}, 25, 80, 'BTNWellSpring', 'Heals 2% max HP per second for 12 seconds.'),
    ('Ingrain', 'grass', 12, 0, {}, 25, 80, 'BTNRegenerate', 'Heals 2% max HP per second for 12 seconds.'),
    ('Wish', 'normal', 13, 0, {}, 30, 100, 'BTNHolyBolt',
     'After 2 seconds the most hurt allied Pokemon within 250 of the spot heals 50% of its max HP.'),
    # ---- debuffs
    ('Growl', 'normal', 20, 0, {21: -1}, 15, 50, 'BTNHowlOfTerror', 'Enemies within 500: -1 Attack for 12 seconds.'),
    ('Charm', 'fairy', 21, 1, {21: -2}, 15, 60, 'BTNCharm', 'The target: -2 Attack for 12 seconds.'),
    ('Leer', 'normal', 20, 0, {22: -1}, 15, 50, 'BTNThunderclap', 'Enemies within 500: -1 Defense for 12 seconds.'),
    ('Tail Whip', 'normal', 20, 0, {22: -1}, 15, 50, 'BTNDizzy', 'Enemies within 500: -1 Defense for 12 seconds.'),
    ('Screech', 'normal', 21, 1, {22: -2}, 15, 60, 'BTNPurge', 'The target: -2 Defense for 12 seconds.'),
    ('Fake Tears', 'dark', 21, 1, {24: -2}, 15, 60, 'BTNCripple', 'The target: -2 Sp. Def for 12 seconds.'),
    ('Metal Sound', 'steel', 21, 1, {24: -2}, 15, 60, 'BTNSpellSteal', 'The target: -2 Sp. Def for 12 seconds.'),
    ('Scary Face', 'normal', 21, 1, {25: -2}, 15, 60, 'BTNSlow', 'The target: -2 Speed for 12 seconds.'),
    ('String Shot', 'bug', 20, 0, {25: -1}, 15, 50, 'BTNWeb', 'Enemies within 500: -1 Speed for 12 seconds.'),
    ('Sand Attack', 'ground', 22, 1, {}, 15, 50, 'BTNEnsnare', 'The target misses 20% of its attacks and moves for 6 seconds.'),
    ('Thunder Wave', 'electric', 23, 1, {42: 4, 43: 100, 44: 2}, 18, 70, 'BTNOrbOfLightning',
     'Paralyzes the target (Ground Pokemon are immune).'),
    ('Will-O-Wisp', 'fire', 23, 1, {42: 1, 43: 100}, 18, 70, 'BTNImmolationOn', 'Burns the target.'),
    ('Toxic', 'poison', 23, 1, {42: 3, 43: 100}, 18, 70, 'BTNOrbOfVenom', 'Badly poisons the target.'),
    ('Poison Powder', 'poison', 23, 1, {42: 2, 43: 100, 44: 1}, 18, 60, 'BTNEnvenomedSpear',
     'Poisons the target (Grass Pokemon are immune).'),
    ('Stun Spore', 'grass', 23, 1, {42: 4, 43: 100, 44: 1}, 18, 60, 'BTNStasisTrap',
     'Paralyzes the target (Grass Pokemon are immune).'),
    ('Hypnosis', 'psychic', 23, 1, {42: 5, 43: 75}, 20, 80, 'BTNHex', '75% chance to put the target to sleep for 2 seconds.'),
    ('Sleep Powder', 'grass', 23, 1, {42: 5, 43: 75, 44: 1}, 20, 80, 'BTNSleep',
     '75% chance to put the target to sleep for 2 seconds (Grass Pokemon are immune).'),
    ('Spore', 'grass', 23, 1, {42: 5, 43: 100, 44: 1}, 20, 90, 'BTNWandOfNeutralization',
     'Puts the target to sleep for 2 seconds (Grass Pokemon are immune).'),
    ('Sing', 'normal', 23, 1, {42: 5, 43: 75}, 20, 80, 'BTNTranquility', '75% chance to put the target to sleep for 2 seconds.'),
    ('Yawn', 'normal', 24, 1, {}, 20, 70, 'BTNScatterRockets', 'The target falls asleep after 2 seconds.'),
    ('Confuse Ray', 'ghost', 25, 1, {}, 18, 70, 'BTNPossession',
     'Confuses the target for 4 seconds (its attacks may hit itself).'),
    ('Swagger', 'normal', 26, 1, {}, 18, 60, 'BTNDispelMagic', 'Confuses the target for 4 seconds, but gives it +2 Attack.'),
    ('Leech Seed', 'grass', 27, 1, {}, 18, 70, 'BTNLifeDrain',
     'Drains 2% of the target\'s max HP per second to the user for 8 seconds (Grass Pokemon are immune).'),
    ('Taunt', 'dark', 28, 1, {}, 18, 60, 'BTNTaunt', 'The target cannot use status moves for 4 seconds.'),
]

# the status move each kit type uses (AI of elites, gym Pokemon, Elite Four, legends); gyms 1-4 avoid sleep / confusion
AI_MOVE = {'bug': 'Quiver Dance', 'dark': 'Nasty Plot', 'dragon': 'Dragon Dance', 'electric': 'Thunder Wave',
           'fairy': 'Moonlight', 'fighting': 'Bulk Up', 'fire': 'Will-O-Wisp', 'flying': 'Roost',
           'ghost': 'Confuse Ray', 'grass': 'Sleep Powder', 'ground': 'Sand Attack', 'ice': 'Amnesia',
           'normal': 'Swords Dance', 'poison': 'Toxic', 'psychic': 'Calm Mind', 'rock': 'Rock Polish',
           'steel': 'Iron Defense', 'water': 'Aqua Ring'}
AI_EASY = dict(AI_MOVE, ghost='Curse', grass='Synthesis')


def index_of(name):
    for k, mv in enumerate(MOVES):
        if mv[0] == name:
            return STAT_BASE + k
    raise KeyError(name)
