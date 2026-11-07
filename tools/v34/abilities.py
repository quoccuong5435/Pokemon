"""v3.4 Pokemon Abilities: number, JASS constant, name, in-game text (docs/v3.4/1-ability.md).

The effects themselves are written in tools/v34/jass/ab_core.j and ab_tick.j; this table only gives the numbers
(1..73: the 68 of v3.3.3, Super Luck, and 70..73 for the new Megas and Darmanitan, docs/v3.4/2-mega-form-quai-hoang.md), the names and the tooltip text of the info button.
"""

ABILITIES = [
    # (number, constant, name, text)
    (1, 'OVERGROW', 'Overgrow', 'Below 40% HP: +50% damage and regenerates 2% max HP per second.'),
    (2, 'BLAZE', 'Blaze', 'Below 40% HP: +50% damage; attacks burn the target for 2% of its max HP per second for 3s.'),
    (3, 'TORRENT', 'Torrent', 'Below 40% HP: +50% damage and +40% attack speed.'),
    (4, 'SWARM', 'Swarm', 'Below 40% HP: +50% damage and heals 20% of the damage dealt.'),
    (5, 'STATIC', 'Static', 'Attacking or being attacked: 20% chance to release lightning that jumps to 4 enemies, '
                            'each hit = 1x main stat and a 0.5s stun.'),
    (6, 'FLAMEBODY', 'Flame Body', 'Burns enemies within 350 for 1% of their max HP per second. Melee attackers also '
                                   'burn for 3% of their max HP over 3s.'),
    (7, 'POISONPOINT', 'Poison Point', 'Attacking or being attacked: 25% chance to poison for 6% max HP over 4s and '
                                       'slow by 20%.'),
    (8, 'CUTECHARM', 'Cute Charm', 'When attacked: 20% chance to charm the attacker for 1.5s (cannot attack, 50% slower).'),
    (9, 'SYNCHRONIZE', 'Synchronize', 'When hit by a move: 25% of its damage is sent back and the attacker is slowed '
                                      'by 30% for 3s.'),
    (10, 'LEVITATE', 'Levitate', 'Immune to Ground moves. 15% chance to dodge attacks.'),
    (11, 'WATERABSORB', 'Water Absorb', 'Water moves deal no damage and heal 25% of it. Regenerates 1% max HP per '
                                        'second out of combat.'),
    (12, 'VOLTABSORB', 'Volt Absorb', 'Electric moves deal no damage and heal 25% of it; then +30% attack speed for 5s.'),
    (13, 'LIGHTNINGROD', 'Lightning Rod', 'Electric moves deal no damage and heal 25% of it; then +30% move damage '
                                          'for 6s.'),
    (14, 'FLASHFIRE', 'Flash Fire', 'Fire moves deal no damage; then +40% damage for 8s.'),
    (15, 'INTIMIDATE', 'Intimidate', 'Entering combat (every 20s): enemies within 600 deal 25% less damage and have '
                                     '-5 armor for 6s.'),
    (16, 'PRESSURE', 'Pressure', 'Enemies within 600: -20% attack speed and lose 2% max mana per second.'),
    (17, 'STURDY', 'Sturdy', 'A lethal hit leaves 15% HP and 1.5s of invulnerability. Once every 60s.'),
    (18, 'SHELLARMOR', 'Shell Armor', 'Cannot be critically hit. Takes 20% less damage from attacks.'),
    (19, 'BATTLEARMOR', 'Battle Armor', 'Cannot be critically hit. Blocks 2 x level damage of every attack.'),
    (20, 'CLEARBODY', 'Clear Body', 'Removes harmful effects every 6s. Takes 15% less damage from moves.'),
    (21, 'ROCKHEAD', 'Rock Head', 'Attacks have a 15% chance to stun for 1s. Takes 10% less damage.'),
    (22, 'SOUNDPROOF', 'Soundproof', 'Takes 30% less damage from moves.'),
    (23, 'MULTISCALE', 'Multiscale', 'Above 80% HP: takes 40% less damage.'),
    (24, 'SHEDSKIN', 'Shed Skin', 'Every 5s: 30% chance to remove harmful effects and heal 5% max HP.'),
    (25, 'EARLYBIRD', 'Early Bird', 'Out of combat for 3s: regenerates 2% max HP per second.'),
    (26, 'NATURALCURE', 'Natural Cure', 'Out of combat for 3s: regenerates 3% max HP per second and removes harmful '
                                        'effects.'),
    (27, 'IRONFIST', 'Iron Fist', '+35% attack damage; every 4th attack deals double damage.'),
    (28, 'ADAPTABILITY', 'Adaptability', '+40% damage with moves of its own type.'),
    (29, 'HYPERCUTTER', 'Hyper Cutter', 'Attacks reduce the target\'s armor by 3 for 6s (stacks 5 times).'),
    (30, 'TECHNICIAN', 'Technician', 'Moves with power 60 or less deal x1.5 damage.'),
    (31, 'RECKLESS', 'Reckless', '+35% damage; loses HP equal to 5% of the damage dealt.'),
    (32, 'GUTS', 'Guts', 'Below 50% HP or under a harmful effect: +40% attack damage and +20% attack speed.'),
    (33, 'ANGERPOINT', 'Anger Point', 'Falling below 50% HP (every 30s): +60% damage and +40% attack speed for 6s.'),
    (34, 'CHLOROPHYLL', 'Chlorophyll', '+40 move speed and +20% attack speed.'),
    (35, 'SWIFTSWIM', 'Swift Swim', '+60 move speed. 10% chance to dodge attacks.'),
    (36, 'RUNAWAY', 'Run Away', 'Falling below 30% HP (every 30s): invisible and +60% move speed for 2s.'),
    (37, 'KEENEYE', 'Keen Eye', '15% chance to deal double damage with attacks. Its attacks cannot be dodged.'),
    (38, 'COMPOUNDEYES', 'Compound Eyes', '20% chance to deal x1.75 damage with attacks. +10% move damage.'),
    (39, 'SANDVEIL', 'Sand Veil', '20% chance to dodge attacks; a dodged attacker is slowed by 20% for 2s.'),
    (40, 'SNOWCLOAK', 'Snow Cloak', '20% chance to dodge attacks; a dodged attacker is slowed by 40% for 2s.'),
    (41, 'LEAFGUARD', 'Leaf Guard', '20% chance to dodge attacks; each dodge heals 3% max HP.'),
    (42, 'INNERFOCUS', 'Inner Focus', '15% chance to dodge attacks. Takes 20% less damage from moves.'),
    (43, 'AIRLOCK', 'Air Lock', 'Enemies within 600 lose their Abilities. 15% chance to dodge attacks.'),
    (44, 'MAGNETPULL', 'Magnet Pull', 'Enemies within 500: 20% slower (Steel types 40%) and -5 armor.'),
    (45, 'BADDREAMS', 'Bad Dreams', 'Enemies within 500 lose 2% max HP per second.'),
    (46, 'MULTITYPE', 'Multitype', '+15% damage and 15% less damage taken.'),
    (47, 'SLOWSTART', 'Slow Start', 'First 30s after spawning or reviving: 40% less damage; afterwards +40% damage '
                                    'and +20% attack speed.'),
    (48, 'THICKFAT', 'Thick Fat', 'Takes 50% less damage from Fire and Ice moves. +10% max HP.'),
    (49, 'TOUGHCLAWS', 'Tough Claws', '+40% attack damage, +20% damage with physical moves.'),
    (50, 'MEGALAUNCHER', 'Mega Launcher', '+40% damage with special moves.'),
    (51, 'AERILATE', 'Aerilate', 'Normal moves become Flying moves. +30% damage with Flying moves.'),
    (52, 'PIXILATE', 'Pixilate', 'Normal moves become Fairy moves. +30% damage with Fairy moves.'),
    (53, 'MOLDBREAKER', 'Mold Breaker', 'Ignores the target\'s Ability. +20% damage.'),
    (54, 'MEGAADAPT', 'Mega Adaptability', '+60% damage with moves of its own type.'),
    (55, 'MEGATECH', 'Mega Technician', 'Moves with power 60 or less deal x1.6 damage. +20% attack speed.'),
    (56, 'DROUGHT', 'Drought', 'Harsh sun (700): allies deal +30% damage with Fire moves; enemies lose 1% max HP '
                               'per second.'),
    (57, 'SANDSTREAM', 'Sand Stream', 'Sandstorm (600): enemies that are not Rock, Ground or Steel lose 1% max HP per '
                                      'second (Mega: 1.5%). Takes 20% less damage from moves.'),
    (58, 'SHADOWTAG', 'Shadow Tag', 'Enemies within 450: 35% slower and -15% attack speed.'),
    (59, 'NOGUARD', 'No Guard', '+25% damage; 15% chance to deal double damage with attacks. Its attacks cannot be '
                                'dodged.'),
    (60, 'TRACE', 'Trace', 'Copies the Ability of the target it hits. Without a copy: 25% chance to dodge attacks.'),
    (61, 'DELTASTREAM', 'Delta Stream', 'Super effective moves deal it only normal damage. 25% chance to dodge attacks.'),
    (62, 'INSOMNIA', 'Insomnia', '20% chance to dodge attacks. Immune to Bad Dreams.'),
    (63, 'MEGAINNERFOCUS', 'Mega Inner Focus', '25% chance to dodge attacks. Takes 30% less damage from moves.'),
    (64, 'PARENTALBOND', 'Parental Bond', 'The Kid fights alongside (see Mega Evolution). Moves deal +25% damage.'),
    (65, 'SANDFORCE', 'Sand Force', 'A lethal hit leaves 15% HP and 1.5s of invulnerability (every 60s). +20% damage '
                                    'with Rock, Ground and Steel moves.'),
    (66, 'STEADFAST', 'Steadfast', 'Each hit taken: +6% damage and +6% attack speed (up to 6 stacks, 5s).'),
    (67, 'SPEEDBOOST', 'Speed Boost', 'Every 10s in combat: +8% attack speed and +10 move speed (up to 5 times, until '
                                      'it dies).'),
    (68, 'MAGICBOUNCE', 'Magic Bounce', 'Moves: 20% chance to block them; otherwise 35% of their damage is sent back.'),
    (69, 'SUPERLUCK', 'Super Luck', '25% chance to deal x1.5 damage with attacks.'),
    (70, 'STRONGJAW', 'Strong Jaw', 'Attacks deal +30% damage. 20% chance to bite again for 50% damage and make the '
                                    'target bleed 1% max HP per second for 3s.'),
    (71, 'SOLARPOWER', 'Solar Power', 'Moves deal +40% damage. In combat it loses 1% max HP per second (not below '
                                      '30% HP).'),
    (72, 'SKILLLINK', 'Skill Link', '30% chance for an attack to strike 2 more times (50% damage each). Moves deal '
                                    '+20% damage (every hit lands).'),
    (73, 'ZENMODE', 'Zen Mode', 'Below 50% HP it turns into Zen Mode (Fire/Psychic): moves +50% damage, attacks -50% '
                                'damage, +25 armor. Back to normal above 50% HP.'),
]

# Pokemon (proper name) -> Ability name, for the 21 Pokemon that had none in v3.3.3 (Abilities of the games)
MISSING = {
    'Torchic': 'Blaze', 'Combusken': 'Blaze', 'Blaziken': 'Blaze',
    'Treecko': 'Overgrow', 'Grovyle': 'Overgrow', 'Sceptile': 'Overgrow',
    'Ralts': 'Synchronize', 'Kirlia': 'Synchronize', 'Gardevoir': 'Trace', 'Gallade': 'Steadfast',
    'Bagon': 'Rock Head', 'Shelgon': 'Rock Head', 'Salamence': 'Intimidate',
    'Beldum': 'Clear Body', 'Metang': 'Clear Body', 'Metagross': 'Clear Body',
    'Larvitar': 'Guts', 'Pupitar': 'Shed Skin', 'Tyranitar': 'Sand Stream',
    'Lucario': 'Inner Focus', 'Absol': 'Super Luck',
    # v3.4 new Pokemon (tools/v34/content.py)
    'Meganium': 'Overgrow', 'Porygon2': 'Trace', 'Latias & Latios': 'Levitate',
}

# v3.4: these keep their unit type but get another Ability (Darmanitan's wild creeps keep Blaze: Zen Mode needs a hero)
REPLACE = {'Darmanitan': 'Zen Mode'}

# icon of the info button of the Abilities added in v3.4 (69 .. 73); the older ones keep the map's buttons
NEW_ICONS = {
    69: 'ReplaceableTextures\CommandButtons\BTNCriticalStrike.blp',
    70: 'ReplaceableTextures\CommandButtons\BTNCriticalStrike.blp',
    71: 'ReplaceableTextures\CommandButtons\BTNOrbOfFire.blp',
    72: 'ReplaceableTextures\CommandButtons\BTNHumanMissileUpOne.blp',
    73: 'ReplaceableTextures\CommandButtons\BTNMagicImmunity.blp',
}

SUPER_LUCK_ICON = 'ReplaceableTextures\\CommandButtons\\BTNCriticalStrike.blp'


def by_name():
    return {name: n for n, _c, name, _t in ABILITIES}
