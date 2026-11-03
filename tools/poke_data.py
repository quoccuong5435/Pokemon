"""New playable Pokemon (8 lines, 21 forms), their 9 skill kits and the 17 skill templates (see new-pokemon spec)."""
from dataclasses import dataclass

B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
TAVERN_ID = 'nTV5'
TAVERN_TEMPLATE = 'n01H'
TAVERN_NAME = 'Pokemon List (click to choose)'
TAVERN_POS = (-128.0, 4544.0, 270.0)  # v3.3: slot 0 of the tavern grid (type_taverns.grid_slot(0))
POKE_DIR = 'war3mapImported\\Poke\\'
TAVERN_HOTKEYS = 'QWERASDF'


@dataclass(frozen=True)
class Form:
    id: str
    name: str
    template: str
    evolves_to: object
    level: object
    kit: str


FORMS = [Form(*r) for r in (
    ('EN00', 'Torchic', 'E003', 'EN01', 16, 'K1'), ('EN01', 'Combusken', 'E007', 'EN02', 36, 'K1'),
    ('EN02', 'Blaziken', 'E01C', None, None, 'K1'),
    ('EN03', 'Treecko', 'E008', 'EN04', 16, 'K2'), ('EN04', 'Grovyle', 'E001', 'EN05', 36, 'K2'),
    ('EN05', 'Sceptile', 'E002', None, None, 'K2'),
    ('EN06', 'Larvitar', 'E00N', 'EN07', 30, 'K3'), ('EN07', 'Pupitar', 'E00O', 'EN08', 55, 'K3'),
    ('EN08', 'Tyranitar', 'E00P', None, None, 'K3'),
    ('EN09', 'Ralts', 'E00G', 'EN0A', 20, 'K4'), ('EN0A', 'Kirlia', 'E00H', 'EN0B', 30, 'K4'),
    ('EN0B', 'Gardevoir', 'E00I', None, None, 'K4'),
    ('EN0C', 'Gallade', 'E010', None, None, 'K5'),
    ('EN0D', 'Bagon', 'E01S', 'EN0E', 30, 'K6'), ('EN0E', 'Shelgon', 'E01T', 'EN0F', 50, 'K6'),
    ('EN0F', 'Salamence', 'E01K', None, None, 'K6'),
    ('EN0G', 'Beldum', 'E031', 'EN0H', 20, 'K7'), ('EN0H', 'Metang', 'E032', 'EN0I', 45, 'K7'),
    ('EN0I', 'Metagross', 'E03V', None, None, 'K7'),
    ('EN0J', 'Lucario', 'E01Z', None, None, 'K8'),
    ('EN0K', 'Absol', 'E03I', None, None, 'K9'),
)]
# legendary / mythical PKL forms: not offered in the tavern picker (they stay playable units, e.g. for Souls)
LEGENDARY_NAMES = {'Entei', 'Ho-Oh', 'Jirachi', 'Kyogre', 'Raikou', 'Regirock', 'Suicune', 'Groudon', 'Buzzwole'}
CELEBI_HERO = 'PZZA'  # v3.3: playable Celebi (the Soul of the random legend Celebi turns a Pokemon into it)
PKL_TEMPLATE = 'E003'  # v1.8 hero cloned for the PKLegends Pokemon (stats are set per species later)
try:
    from pkl_forms import PKL_FORMS, PKL_EVOLUTIONS
except ImportError:  # pragma: no cover
    PKL_FORMS, PKL_EVOLUTIONS = [], {}
FORMS = FORMS + [Form(fid, name, PKL_TEMPLATE, *PKL_EVOLUTIONS.get(fid, (None, None)), '') for fid, name, _lvl in PKL_FORMS]
FORM_BY_ID = {f.id: f for f in FORMS}


def base_form_id(fid):
    """First form of the evolution family of a form (the form itself when nothing evolves into it)."""
    parents = {f.evolves_to: f.id for f in FORMS if f.evolves_to}
    while fid in parents:
        fid = parents[fid]
    return fid
KIT_TYPES = {'K1': 'Fire&Fighting Pokemon', 'K2': 'Grass Pokemon', 'K3': 'Rock&Dark Pokemon',
             'K4': 'Psychic&Fairy Pokemon', 'K5': 'Psychic&Fighting Pokemon', 'K6': 'Dragon&Flying Pokemon',
             'K7': 'Steel&Psychic Pokemon', 'K8': 'Fighting&Steel Pokemon', 'K9': 'Dark Pokemon'}
ITEM_EVOLUTIONS = [('EN0A', 'I00P', 'EN0C')]  # Kirlia + Sun Stone -> Gallade
STARTERS = ['EN00', 'EN03', 'EN06', 'EN09', 'EN0D', 'EN0G', 'EN0J', 'EN0K']

# slot: (required level, button position, hotkey)
SLOTS = {'Q': (3, '0,2', 'Q'), 'W': (6, '1,2', 'W'), 'E': (10, '2,2', 'E'), 'P': (33, '3,2', ''),
         'R': (36, '2,1', 'R')}


@dataclass(frozen=True)
class Template:
    key: str
    code: str
    values: dict        # SLK column stem (DataA, Dur, Area, Rng...) -> (lv1, lv2, lv3)
    cooldown: float
    mana: tuple
    icon: str
    text: str           # English description with {0} {1} {2}... filled from values per level


def _t(key, code, values, cd, mana, icon, text):
    return Template(key, code, values, cd, mana, icon, text)


_I = 'ReplaceableTextures\\CommandButtons\\'
_P = 'ReplaceableTextures\\PassiveButtons\\'
TEMPLATES = {t.key: t for t in (
    _t('WAVE', 'AUcs', {'DataA': (150, 250, 350), 'DataB': (600, 1000, 1400), 'DataC': (800, 800, 800),
                        'Rng': (700, 700, 700)}, 10, (75, 125, 175), _I + 'BTNCarrionSwarm.blp',
       'Sends a wave that deals {DataA} damage to enemies in a line.'),
    _t('LINE', 'AOsh', {'DataA': (175, 275, 375), 'DataB': (700, 1100, 1500), 'DataC': (800, 800, 800),
                        'Rng': (700, 700, 700)}, 11, (90, 140, 190), _I + 'BTNShockWave.blp',
       'Strikes in a line, dealing {DataA} damage to enemy ground units.'),
    _t('CONE', 'ANbf', {'DataA': (125, 200, 275), 'DataB': (600, 1000, 1400), 'DataE': (15, 25, 35),
                        'Dur': (5, 5, 5)}, 10, (75, 125, 175), _I + 'BTNBreathOfFire.blp',
       'Breathes a cone dealing {DataA} damage, then {DataE} damage per second for 5 seconds.'),
    _t('CHAIN', 'AOcl', {'DataA': (120, 190, 260), 'DataB': (4, 5, 6), 'DataC': (0.15, 0.15, 0.15)}, 10,
       (90, 140, 190), _I + 'BTNChainLightning.blp', 'Hits up to {DataB} enemies for {DataA} damage each.'),
    _t('BOLT', 'AHtb', {'DataA': (200, 325, 450), 'Dur': (1, 1.25, 1.5)}, 12, (100, 150, 200),
       _I + 'BTNStormBolt.blp', 'Deals {DataA} damage to a target and stuns it for {Dur} seconds.'),
    _t('DAGGER', 'AEsh', {'DataE': (100, 175, 250), 'DataA': (20, 30, 40), 'Dur': (6, 6, 6)}, 12, (90, 130, 170),
       _I + 'BTNShadowStrike.blp', 'Deals {DataE} damage, then {DataA} damage every few seconds and slows.'),
    _t('STOMP', 'AOws', {'DataA': (175, 275, 375), 'Area': (300, 300, 300), 'Dur': (1.25, 1.5, 1.75)}, 14,
       (120, 170, 220), _I + 'BTNWarStomp.blp', 'Deals {DataA} damage around and stuns for {Dur} seconds.'),
    _t('NOVA', 'AUfn', {'DataB': (200, 300, 400), 'DataA': (125, 200, 275), 'Dur': (3, 3, 3),
                        'Area': (200, 200, 200)}, 12, (110, 160, 210), _I + 'BTNGlacier.blp',
       'Deals {DataB} damage to the target and {DataA} around it, slowing for 3 seconds.'),
    _t('BUFF', 'Absk', {'DataA': (0.15, 0.25, 0.35), 'DataB': (0.25, 0.45, 0.65), 'DataC': (0.1, 0.1, 0.1),
                        'Dur': (10, 10, 10)}, 18, (75, 100, 125), _I + 'BTNBerserkForTrolls.blp',
       'For 10 seconds: +{DataA%} move speed, +{DataB%} attack speed, takes 10% more damage.'),
    _t('CRIT', 'AOcr', {'DataA': (15, 20, 25), 'DataB': (2, 2.5, 3)}, 0, (0, 0, 0),
       _P + 'PASBTNCriticalStrike.blp', '{DataA}% chance to deal {DataB} times damage.'),
    _t('EVADE', 'AEev', {'DataA': (0.12, 0.18, 0.24)}, 0, (0, 0, 0), _P + 'PASBTNEvasion.blp',
       '{DataA%} chance to dodge attacks.'),
    _t('BASH', 'AHbh', {'DataA': (15, 20, 25), 'DataC': (60, 120, 180), 'Dur': (0.75, 0.75, 0.75)}, 0, (0, 0, 0),
       _P + 'PASBTNBash.blp', '{DataA}% chance to deal {DataC} bonus damage and stun.'),
    _t('ULT_WAVE', 'AUcs', {'DataA': (450, 700, 950), 'DataB': (2000, 3000, 4000), 'DataC': (1000, 1000, 1000),
                            'Rng': (800, 800, 800)}, 40, (250, 400, 550), _I + 'BTNCarrionSwarm.blp',
       'A huge wave dealing {DataA} damage to every enemy in its path.'),
    _t('ULT_LINE', 'AOsh', {'DataA': (500, 750, 1000), 'DataB': (2000, 3000, 4000), 'DataC': (1000, 1000, 1000),
                            'Rng': (800, 800, 800)}, 40, (250, 400, 550), _I + 'BTNShockWave.blp',
       'A devastating line attack dealing {DataA} damage.'),
    _t('ULT_RAIN', 'AHbz', {'DataA': (8, 10, 12), 'DataB': (90, 130, 170), 'DataF': (1000, 1500, 2000),
                            'Area': (300, 300, 300)}, 45, (250, 400, 550), _I + 'BTNBlizzard.blp',
       'Calls {DataA} waves that deal {DataB} damage each in an area.'),
    _t('ULT_STAR', 'AEsf', {'DataA': (60, 90, 120), 'Dur': (15, 15, 15), 'Area': (800, 800, 800)}, 60,
       (300, 450, 600), _I + 'BTNStarfall.blp', 'For 15 seconds strikes nearby enemies for {DataA} damage.'),
    _t('ULT_STOMP', 'AOws', {'DataA': (450, 700, 950), 'Area': (450, 450, 450), 'Dur': (2, 2.5, 3)}, 40,
       (250, 400, 550), _I + 'BTNWarStomp.blp', 'Deals {DataA} damage around and stuns for {Dur} seconds.'),
)}

ELEMENT_ART = {
    'fire': 'Abilities\\Weapons\\RedDragonBreath\\RedDragonMissile.mdl',
    'grass': 'Abilities\\Weapons\\GreenDragonMissile\\GreenDragonMissile.mdl',
    'rock': 'Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl',
    'psychic': 'Abilities\\Weapons\\FaerieDragonMissile\\FaerieDragonMissile.mdl',
    'dragon': 'Abilities\\Weapons\\FrostWyrmMissile\\FrostWyrmMissile.mdl',
    'steel': 'Abilities\\Weapons\\GryphonRiderMissile\\GryphonRiderMissile.mdl',
    'aura': 'Abilities\\Weapons\\ZigguratMissile\\ZigguratMissile.mdl',
    'dark': 'Abilities\\Weapons\\AvengerMissile\\AvengerMissile.mdl',
}


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    template: str
    slot: str
    element: str
    kit: str


_KITS = (
    ('K1', 'fire', [('Ember', 'CONE'), ('Double Kick', 'BOLT'), ('Blaze Kick', 'STOMP'), ('Blaze', 'CRIT'),
                    ('Blast Burn', 'ULT_WAVE')]),
    ('K2', 'grass', [('Bullet Seed', 'CHAIN'), ('Leaf Blade', 'DAGGER'), ('Agility', 'BUFF'), ('Overgrow', 'EVADE'),
                     ('Leaf Storm', 'ULT_LINE')]),
    ('K3', 'rock', [('Rock Slide', 'LINE'), ('Crunch', 'BOLT'), ('Earthquake', 'STOMP'), ('Sand Stream', 'BASH'),
                    ('Stone Edge', 'ULT_RAIN')]),
    ('K4', 'psychic', [('Confusion', 'WAVE'), ('Psychic', 'BOLT'), ('Moonblast', 'NOVA'), ('Trace', 'EVADE'),
                       ('Future Sight', 'ULT_STAR')]),
    ('K5', 'psychic', [('Psycho Cut', 'LINE'), ('Night Slash', 'DAGGER'), ('Swords Dance', 'BUFF'),
                       ('Sharpness', 'CRIT'), ('Close Combat', 'ULT_STOMP')]),
    ('K6', 'dragon', [('Dragon Breath', 'CONE'), ('Dragon Claw', 'BOLT'), ('Dragon Dance', 'BUFF'),
                      ('Intimidate', 'BASH'), ('Draco Meteor', 'ULT_RAIN')]),
    ('K7', 'steel', [('Bullet Punch', 'BOLT'), ('Zen Headbutt', 'LINE'), ('Earthquake', 'STOMP'),
                     ('Tough Claws', 'CRIT'), ('Meteor Mash', 'ULT_RAIN')]),
    ('K8', 'aura', [('Aura Sphere', 'BOLT'), ('Force Palm', 'STOMP'), ('Extreme Speed', 'BUFF'),
                    ('Justified', 'CRIT'), ('Aura Storm', 'ULT_WAVE')]),
    ('K9', 'dark', [('Night Slash', 'DAGGER'), ('Sucker Punch', 'BOLT'), ('Swords Dance', 'BUFF'),
                    ('Super Luck', 'CRIT'), ('Future Sight', 'ULT_STAR')]),
)
KITS = {}
_n = 0
for _kit, _elem, _moves in _KITS:
    KITS[_kit] = []
    for (_name, _tmpl), _slot in zip(_moves, 'QWEPR'):
        KITS[_kit].append(Skill('AP' + B36[_n // 36] + B36[_n % 36], _name, _tmpl, _slot, _elem, _kit))
        _n += 1
