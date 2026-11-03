"""Pokemon Abilities (v2.8): the effects, who gets which Ability, and the item bonus abilities they use.

Effect parameters by family (x, y, z, w are reals, s a string, raw an object id of RAW_ABILITIES):
  PINCH x=HP fraction below which it works, y=damage bonus
  CONTACT x=chance, y=kind (1 stun, 2 burn, 3 poison, 4 slow), z=seconds, w=fraction (HP over z seconds / speed lost)
  ABSORB s=type word of the attacker, x=healed fraction, y=damage bonus afterwards, z=bonus seconds
  INTIMIDATE x=range, y=damage penalty, z=seconds           PRESSURE x=mana lost per hit
  STURDY x=fraction of max HP left, z=cooldown seconds      DEFENSE raw=armor bonus ability
  MULTISCALE x=damage reduction at full HP                  RECOVERY x=max HP fraction per second, y=seconds unhit
  POWER x=damage bonus                                      RISING x=bonus per hit taken, y=max stacks, z=seconds
  SPEED raw=move speed bonus ability                        LUCKY x=chance to deal double damage with attacks
  DODGE x=chance to dodge attacks                           AURA x=range, y=kind (1 slow, 2 damage), w=fraction
  REFLECT x=fraction of damage taken returned               MULTITYPE x=damage bonus, y=damage reduction
  SLOWSTART x=damage penalty, y=seconds, z=damage bonus afterwards
"""
from dataclasses import dataclass

from mega_data import MEGAS

B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_I = 'ReplaceableTextures\\CommandButtons\\'
INFO_POS = '3,1'  # command card cell that is free for every hero (Mega Evolve uses 0,1 and 1,1)

FAMILY = {n: i for i, n in enumerate(
    'PINCH CONTACT ABSORB INTIMIDATE PRESSURE STURDY DEFENSE MULTISCALE RECOVERY POWER RISING SPEED LUCKY DODGE AURA '
    'REFLECT MULTITYPE SLOWSTART'.split(), 1)}
RAW_ABILITIES = {'AXA4': ('AIde', 4), 'AXA6': ('AIde', 6), 'AXS4': ('AIms', 40), 'AXS7': ('AIms', 70)}
_ICON = {
    'PINCH': 'BTNBerserkForTrolls', 'CONTACT': 'BTNBash', 'ABSORB': 'BTNGlacier', 'INTIMIDATE': 'BTNWarStomp',
    'PRESSURE': 'BTNShadowStrike', 'STURDY': 'BTNHumanArmorUpTwo', 'DEFENSE': 'BTNHumanArmorUpOne',
    'MULTISCALE': 'BTNHumanArmorUpTwo', 'RECOVERY': 'BTNHeal', 'POWER': 'BTNCriticalStrike', 'RISING': 'BTNBerserkForTrolls',
    'SPEED': 'BTNBootsOfSpeed', 'LUCKY': 'BTNCriticalStrike', 'DODGE': 'BTNEvasion', 'AURA': 'BTNCarrionSwarm',
    'REFLECT': 'BTNShadowStrike', 'MULTITYPE': 'BTNStarfall', 'SLOWSTART': 'BTNStarfall', 'NONE': 'BTNEvasion',
}


@dataclass(frozen=True)
class Effect:
    fam: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0
    s: str = ''
    raw: str = ''


@dataclass(frozen=True)
class Ability:
    key: str       # unique; Mega variants of an Ability start with "Mega "
    name: str      # shown to the player
    effects: tuple
    text: str
    icon: str


_MEGA_NAMES = ('Mega Launcher', 'Mega Adaptability', 'Mega Technician', 'Mega Inner Focus')  # keep the "Mega" word: the base Ability has the same name


def _a(key, text, *effects):
    name = key[5:] if key.startswith('Mega ') and key not in _MEGA_NAMES else key
    fam = effects[0].fam if effects else 'NONE'
    return Ability(key, name, tuple(effects), text, _I + _ICON[fam] + '.blp')


E = Effect
_PINCH = 'Below 33% HP: +40% damage dealt.'
_SLOW = 'When hit: 20% chance to slow the attacker by 40% for 3s.'
ABILITIES = [
    _a('Overgrow', _PINCH, E('PINCH', 0.33, 0.40)), _a('Blaze', _PINCH, E('PINCH', 0.33, 0.40)),
    _a('Torrent', _PINCH, E('PINCH', 0.33, 0.40)), _a('Swarm', _PINCH, E('PINCH', 0.33, 0.40)),
    _a('Static', 'When hit: 20% chance to stun the attacker for 1s.', E('CONTACT', 0.20, 1, 1.0)),
    _a('Flame Body', 'When hit: 20% chance to burn the attacker for 3% of its max HP over 3s.', E('CONTACT', 0.20, 2, 3.0, 0.03)),
    _a('Poison Point', 'When hit: 20% chance to poison the attacker for 4% of its max HP over 4s.', E('CONTACT', 0.20, 3, 4.0, 0.04)),
    _a('Cute Charm', _SLOW, E('CONTACT', 0.20, 4, 3.0, 0.40)),
    _a('Synchronize', _SLOW, E('CONTACT', 0.20, 4, 3.0, 0.40)),
    _a('Levitate', 'Takes no damage from Ground Pokemon.', E('ABSORB', s='Ground')),
    _a('Water Absorb', 'Takes no damage from Water Pokemon and heals 25% of it.', E('ABSORB', 0.25, s='Water')),
    _a('Volt Absorb', 'Takes no damage from Electric Pokemon and heals 25% of it.', E('ABSORB', 0.25, s='Electric')),
    _a('Lightning Rod', 'Takes no damage from Electric Pokemon and heals 25% of it.', E('ABSORB', 0.25, s='Electric')),
    _a('Flash Fire', 'Takes no damage from Fire Pokemon; +30% damage dealt for 6s afterwards.', E('ABSORB', 0.0, 0.30, 6.0, s='Fire')),
    _a('Intimidate', 'When hit after 10s out of combat: enemies within 500 deal 20% less damage for 6s.', E('INTIMIDATE', 500, 0.20, 6.0)),
    _a('Pressure', 'Attackers lose 20 mana per hit.', E('PRESSURE', 20)),
    _a('Sturdy', 'A lethal hit leaves 10% HP. Once every 90s.', E('STURDY', 0.10, 0, 90.0)),
    _a('Shell Armor', '+4 armor.', E('DEFENSE', raw='AXA4')), _a('Battle Armor', '+4 armor.', E('DEFENSE', raw='AXA4')),
    _a('Clear Body', '+4 armor.', E('DEFENSE', raw='AXA4')), _a('Rock Head', '+4 armor.', E('DEFENSE', raw='AXA4')),
    _a('Soundproof', '+4 armor.', E('DEFENSE', raw='AXA4')),
    _a('Multiscale', 'At full HP: 40% less damage taken.', E('MULTISCALE', 0.40)),
    _a('Shed Skin', 'After 5s without being hit: regenerates 2.5% max HP per second.', E('RECOVERY', 0.025, 5.0)),
    _a('Early Bird', 'After 5s without being hit: regenerates 2.5% max HP per second.', E('RECOVERY', 0.025, 5.0)),
    _a('Natural Cure', 'After 5s without being hit: regenerates 2.5% max HP per second.', E('RECOVERY', 0.025, 5.0)),
    _a('Iron Fist', '+20% damage dealt.', E('POWER', 0.20)), _a('Adaptability', '+20% damage dealt.', E('POWER', 0.20)),
    _a('Hyper Cutter', '+20% damage dealt.', E('POWER', 0.20)), _a('Technician', '+20% damage dealt.', E('POWER', 0.20)),
    _a('Reckless', '+20% damage dealt.', E('POWER', 0.20)),
    _a('Guts', 'Each hit taken: +5% damage dealt (up to 6 stacks, 5s).', E('RISING', 0.05, 6, 5.0)),
    _a('Anger Point', 'Each hit taken: +5% damage dealt (up to 6 stacks, 5s).', E('RISING', 0.05, 6, 5.0)),
    _a('Chlorophyll', '+40 movement speed.', E('SPEED', raw='AXS4')), _a('Swift Swim', '+40 movement speed.', E('SPEED', raw='AXS4')),
    _a('Run Away', '+40 movement speed.', E('SPEED', raw='AXS4')),
    _a('Keen Eye', '12% chance to deal double damage with attacks.', E('LUCKY', 0.12)),
    _a('Compound Eyes', '12% chance to deal double damage with attacks.', E('LUCKY', 0.12)),
    _a('Sand Veil', '15% chance to dodge attacks.', E('DODGE', 0.15)), _a('Snow Cloak', '15% chance to dodge attacks.', E('DODGE', 0.15)),
    _a('Leaf Guard', '15% chance to dodge attacks.', E('DODGE', 0.15)), _a('Inner Focus', '15% chance to dodge attacks.', E('DODGE', 0.15)),
    _a('Air Lock', '15% chance to dodge attacks.', E('DODGE', 0.15)),
    _a('Magnet Pull', 'Enemies within 400 are slowed by 15%.', E('AURA', 400, 1, w=0.15)),
    _a('Bad Dreams', 'Enemies within 450 lose 1% max HP per second.', E('AURA', 450, 2, w=0.01)),
    _a('Multitype', '+10% damage dealt and 10% less damage taken.', E('MULTITYPE', 0.10, 0.10)),
    _a('Slow Start', 'First 30s after spawning or reviving: 40% less damage dealt; afterwards +25% damage.', E('SLOWSTART', 0.40, 30.0, 0.25)),
    # Mega only
    _a('Thick Fat', '+6 armor.', E('DEFENSE', raw='AXA6')),
    _a('Tough Claws', '+30% damage dealt.', E('POWER', 0.30)), _a('Mega Launcher', '+30% damage dealt.', E('POWER', 0.30)),
    _a('Aerilate', '+30% damage dealt.', E('POWER', 0.30)), _a('Pixilate', '+30% damage dealt.', E('POWER', 0.30)),
    _a('Mold Breaker', '+30% damage dealt.', E('POWER', 0.30)), _a('Mega Adaptability', '+30% damage dealt.', E('POWER', 0.30)),
    _a('Mega Technician', '+30% damage dealt.', E('POWER', 0.30)),
    _a('Drought', 'Enemies within 450 lose 1% max HP per second.', E('AURA', 450, 2, w=0.01)),
    _a('Sand Stream', 'Enemies within 450 lose 1% max HP per second.', E('AURA', 450, 2, w=0.01)),
    _a('Shadow Tag', 'Enemies within 400 are slowed by 30%.', E('AURA', 400, 1, w=0.30)),
    _a('No Guard', '+20% damage dealt and 12% chance to deal double damage with attacks.', E('POWER', 0.20), E('LUCKY', 0.12)),
    _a('Trace', '25% chance to dodge attacks.', E('DODGE', 0.25)), _a('Delta Stream', '25% chance to dodge attacks.', E('DODGE', 0.25)),
    _a('Insomnia', '20% chance to dodge attacks.', E('DODGE', 0.20)), _a('Mega Inner Focus', '20% chance to dodge attacks.', E('DODGE', 0.20)),
    _a('Parental Bond', 'The Kid fights alongside (see Mega Evolution).'),
    _a('Sand Force', 'A lethal hit leaves 10% HP (once every 90s); +6 armor.', E('STURDY', 0.10, 0, 90.0), E('DEFENSE', raw='AXA6')),
    _a('Steadfast', 'Each hit taken: +7% damage dealt (up to 6 stacks, 5s).', E('RISING', 0.07, 6, 5.0)),
    _a('Speed Boost', '+70 movement speed.', E('SPEED', raw='AXS7')),
    _a('Magic Bounce', 'Reflects 20% of the damage taken back to the attacker.', E('REFLECT', 0.20)),
]
_NUMBER = {a.key: i + 1 for i, a in enumerate(ABILITIES)}

_SPECIES = {
    'Overgrow': 'Bulbasaur Ivysaur Venusaur', 'Blaze': 'Charmander Charmeleon Charizard',
    'Torrent': 'Squirtle Wartortle Blastoise', 'Swarm': 'Weedle Kakuna Beedrill Scyther',
    'Static': 'Pikachu Raichu Voltorb Electrode', 'Synchronize': 'Abra Kadabra Alakazam Mew Espeon Umbreon',
    'Poison Point': 'Nidoran Nidorino Nidoking', 'Flame Body': 'Ponyta Rapidash', 'Cute Charm': 'Sylveon',
    'Levitate': 'Weezing Koffing Gastly Haunter Gengar', 'Water Absorb': 'Poliwag Poliwhirl Poliwrath Vaporeon',
    'Volt Absorb': 'Jolteon', 'Lightning Rod': 'Rhyhorn Rhydon', 'Flash Fire': 'Flareon Vulpix Ninetales',
    'Intimidate': 'Tauros Growlithe Arcanine Gyarados Hitmontop',
    'Pressure': 'Articuno Moltres Zapdos Mewtwo Deoxys Giratina Dialga Palkia',
    'Sturdy': 'Geodude Graveler Golem Steelix', 'Shell Armor': 'Shellder Cloyster', 'Clear Body': 'Tentacool Tentacruel',
    'Battle Armor': 'Kabuto Kabutops', 'Rock Head': 'Onix', 'Soundproof': 'Mr.mime', 'Multiscale': 'Dragonite Lugia',
    'Shed Skin': 'Dratini Dragonair', 'Early Bird': 'Kangaskhan', 'Natural Cure': 'Staryu Starmie',
    'Iron Fist': 'Hitmonchan', 'Adaptability': 'Eevee', 'Hyper Cutter': 'Krabby Kingler Pinsir', 'Technician': 'Scizor',
    'Reckless': 'Hitmonlee', 'Guts': 'Machop Machoke Machamp', 'Anger Point': 'Mankey Primeape',
    'Chlorophyll': 'Bellsprout Weepinbell Victreebel Exeggcute Exeggutor', 'Swift Swim': 'Omanyte Omastar Magikarp',
    'Run Away': 'Rattata Raticate', 'Keen Eye': 'Pidgey Pidgeotto Pidgeot', 'Compound Eyes': 'Caterpie Metapod Butterfree',
    'Sand Veil': 'Sandshrew Sandslash', 'Snow Cloak': 'Glaceon', 'Leaf Guard': 'Leafleon', 'Inner Focus': 'Zubat Golbat Crobat',
    'Air Lock': 'Rayquaza', 'Magnet Pull': 'Magnemite Magneton', 'Bad Dreams': 'Darkrai', 'Multitype': 'Arceus',
    'Slow Start': 'Regigigas',
}
_MEGA = {
    'Mega Venusaur': 'Thick Fat', 'Mega Charizard X': 'Tough Claws', 'Mega Charizard Y': 'Drought',
    'Mega Blastoise': 'Mega Launcher', 'Mega Beedrill': 'Mega Adaptability', 'Mega Pidgeot': 'No Guard',
    'Mega Alakazam': 'Trace', 'Mega Gengar': 'Shadow Tag', 'Mega Kangaskhan': 'Parental Bond', 'Mega Pinsir': 'Aerilate',
    'Mega Gyarados': 'Mold Breaker', 'Mega Steelix': 'Sand Force', 'Mega Scizor': 'Mega Technician',
    'Mega Mewtwo X': 'Steadfast', 'Mega Mewtwo Y': 'Insomnia', 'Mega Rayquaza': 'Delta Stream',
    'Mega Blaziken': 'Speed Boost', 'Mega Sceptile': 'Lightning Rod', 'Mega Tyranitar': 'Sand Stream',
    'Mega Gardevoir': 'Pixilate', 'Mega Gallade': 'Mega Inner Focus', 'Mega Salamence': 'Aerilate',
    'Mega Metagross': 'Tough Claws', 'Mega Lucario': 'Mega Adaptability', 'Mega Absol': 'Magic Bounce',
}


def info_id(i):
    """Object id of the passive info button of ABILITIES[i]: AB00, AB01, ..."""
    return 'AB' + B36[i // 36] + B36[i % 36]


def species_abilities():
    """Pokemon proper name -> Ability key (the nine v2.3 lines are not listed: their skill 4 is the Ability)."""
    return {name: key for key, names in _SPECIES.items() for name in names.split()}


def mega_abilities():
    return dict(_MEGA)


# v3.3: signature Ability of a type, for Pokemon whose own Ability we do not have
TYPE_ABILITY = {
    'normal': 'Run Away', 'fire': 'Blaze', 'water': 'Torrent', 'grass': 'Overgrow', 'electric': 'Static',
    'ice': 'Snow Cloak', 'fighting': 'Guts', 'poison': 'Poison Point', 'ground': 'Sand Veil', 'flying': 'Keen Eye',
    'psychic': 'Synchronize', 'bug': 'Swarm', 'rock': 'Sturdy', 'ghost': 'Levitate', 'dragon': 'Multiscale',
    'dark': 'Pressure', 'steel': 'Clear Body', 'fairy': 'Cute Charm',}


_ALIAS = {'Politeod': 'Politoed', 'Nidoran_M': 'Nidoran', 'Nidoran_F': 'Nidoran', 'Nidorina': 'Nidoran',
          'Nidoqueen': 'Nidoran'}  # typos and names the tables do not know


def _real_name(slug):
    return ' '.join(w.capitalize() for w in slug.split('-'))


def ability_key_for(name):
    """Ability key of a species: the explicit table, else its first non-hidden real ability that we have,
    else the signature Ability of its primary type (None when the species is unknown)."""
    by_name = species_abilities()
    name = _ALIAS.get(name, name)
    if name in by_name:
        return by_name[name]
    import learn_data
    sp = learn_data.SPECIES.get(learn_data.slug(name or ''))
    if sp is None:
        return None
    for ab, hidden in sp.get('abilities', []):
        if not hidden and _real_name(ab) in _NUMBER:
            return _real_name(ab)
    return TYPE_ABILITY.get((sp.get('types') or ['normal'])[0], 'Run Away')


def all_unit_names(w3u):
    """Unit type id -> Pokemon name of the units that get an Ability in v3.3 besides the v1.8 heroes:
    the PKLegends forms, the wild creeps and the legends (boss units and their random clones)."""
    import legend_data
    import poke_data
    import wild_data
    out = {f.id: f.name for f in poke_data.FORMS if f.id[:1] == 'P'}
    out[poke_data.CELEBI_HERO] = 'Celebi'
    objs = {o.new: o for o in w3u.custom}
    for t in wild_data.wild_types(w3u):
        out[t] = wild_data._species_name(objs, t)
    out.update({s.id: s.name for s in wild_data.SPECIES})
    for lg in legend_data.LEGENDS:
        out[lg.id] = lg.name
        if lg.name not in legend_data.PKL_LEGEND_NAMES:  # the PKL legends borrow the boss n00C as a template
            out[lg.boss] = lg.name
    return out


def type_abilities(w3u):
    """Unit type id -> Ability number (1-based index into ABILITIES) of every v1.8 hero, PKLegends form, wild
    creep and legend (every Pokemon has an Ability in v3.3)."""
    out = {}
    for o in w3u.custom:
        if o.new[:1] == 'E' and o.get('upro'):
            key = ability_key_for(o.get('upro'))
            if key:
                out[o.new] = _NUMBER[key]
    for uid, name in all_unit_names(w3u).items():
        key = ability_key_for(name)
        if key:
            out[uid] = _NUMBER[key]
    return out


def mega_ability_index():
    """Mega index (MEGAS[i].index) -> Ability number."""
    return {m.index: _NUMBER[_MEGA[m.name]] for m in MEGAS}
