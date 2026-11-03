"""v3.0 skill rework for the 117 v1.8 Pokemon: every one gets a 5-skill kit chosen by its main type.

Kits of the 9 new Pokemon lines (poke_data.KITS) are reused for the types they already cover; the other
types get the kits below. Skill ids of the new kits are 'AQ' + base-36 index (poke_data uses 'AP').
The numbers of every skill come from its template (poke_data.TEMPLATES), so the rework keeps balance.
"""
import poke_data as pd

# main type -> kit key (poke_data.KITS for the 7 types the 21 new Pokemon already use)
TYPE_KIT = {
    'fire': 'K1', 'grass': 'K2', 'rock': 'K3', 'psychic': 'K4', 'dragon': 'K6', 'steel': 'K7', 'dark': 'K9',
}

# new kits: type -> list of (skill name, template), slots Q W E P R
_NEW = {
    'water': [('Water Pulse', 'CHAIN'), ('Aqua Tail', 'LINE'), ('Hydro Pump', 'CONE'), ('Withdraw', 'EVADE'),
              ('Hydro Cannon', 'ULT_WAVE')],
    'electric': [('Thunder Shock', 'CHAIN'), ('Spark', 'BOLT'), ('Thunderbolt', 'NOVA'), ('Charge', 'BUFF'),
                 ('Thunder', 'ULT_RAIN')],
    'ground': [('Mud Shot', 'DAGGER'), ('Bulldoze', 'STOMP'), ('Earth Power', 'NOVA'), ('Dig', 'EVADE'),
               ('Earth Crush', 'ULT_STOMP')],
    'ice': [('Ice Shard', 'WAVE'), ('Ice Punch', 'BOLT'), ('Icicle Crash', 'LINE'), ('Ice Armor', 'BUFF'),
            ('Blizzard', 'ULT_RAIN')],
    'fighting': [('Karate Chop', 'BASH'), ('Force Palm', 'STOMP'), ('Brick Break', 'LINE'), ('Bulk Up', 'BUFF'),
                 ('Close Combat', 'ULT_STOMP')],
    'poison': [('Poison Sting', 'DAGGER'), ('Sludge', 'CHAIN'), ('Acid', 'WAVE'), ('Toxic', 'NOVA'),
               ('Sludge Bomb', 'ULT_WAVE')],
    'bug': [('Bug Bite', 'DAGGER'), ('Pin Missile', 'CHAIN'), ('Silver Wind', 'WAVE'), ('Quiver Dance', 'BUFF'),
            ('Megahorn', 'ULT_LINE')],
    'ghost': [('Shadow Ball', 'BOLT'), ('Lick', 'DAGGER'), ('Night Shade', 'WAVE'), ('Shadow Sneak', 'EVADE'),
              ('Shadow Force', 'ULT_STAR')],
    'flying': [('Peck', 'DAGGER'), ('Air Slash', 'LINE'), ('Wing Attack', 'CONE'), ('Roost', 'EVADE'),
               ('Hurricane', 'ULT_RAIN')],
    'normal': [('Tackle', 'DAGGER'), ('Body Slam', 'BOLT'), ('Hyper Beam', 'LINE'), ('Growth', 'BUFF'),
               ('Hyper Voice', 'ULT_WAVE')],
    'fairy': [('Fairy Wind', 'WAVE'), ('Dazzling Gleam', 'NOVA'), ('Play Rough', 'BOLT'), ('Charm', 'CRIT'),
              ('Moonlight', 'ULT_STAR')],
}

# the 117 v1.8 Pokemon by main type (names in the comments)
HERO_TYPE = {
    'fire': ['E003', 'E007', 'E00E', 'E01B', 'E01C', 'E01H', 'E021', 'E02F', 'E038', 'E04O', 'E04P'],  # Charmander..Ninetales
    'water': ['E004', 'E009', 'E000', 'E012', 'E013', 'E014', 'E01F', 'E02D', 'E02E', 'E037', 'E03C', 'E03D',
              'E03E', 'E03F', 'E04D', 'E04N', 'E04M', 'E01I'],
    'grass': ['E001', 'E002', 'E008', 'E01A', 'E02B', 'E02C', 'E02U', 'E02W', 'E03S'],
    'electric': ['E005', 'E006', 'E01D', 'E01E', 'E01X', 'E031', 'E032', 'E03J'],
    'ground': ['E00A', 'E00F', 'E02Y', 'E02Z'],
    'rock': ['E00N', 'E00O', 'E00P', 'E035', 'E03P', 'E03Q', 'E03R', 'E03U'],
    'psychic': ['E00G', 'E00H', 'E00I', 'E024', 'E026', 'E027', 'E022', 'E03H', 'E040'],
    'fighting': ['E00Y', 'E00Z', 'E010', 'E01Z', 'E02S', 'E02T', 'E03Y', 'E03Z'],
    'poison': ['E019', 'E01J', 'E01L', 'E01M', 'E01V', 'E046', 'E048', 'E049'],
    'bug': ['E01N', 'E01P', 'E01Q', 'E02I', 'E02J', 'E02K', 'E03L', 'E03M', 'E03W'],
    'ghost': ['E01G', 'E02G', 'E02H', 'E028'],
    'dragon': ['E01K', 'E01S', 'E01T', 'E029'],
    'dark': ['E023', 'E03I'],
    'steel': ['E03V', 'E04C'],
    'flying': ['E00B', 'E00C', 'E00D'],
    'normal': ['E00T', 'E00U', 'E018', 'E02P', 'E03A', 'E02A', 'E025'],
    'fairy': ['E03X'],
    'ice': ['E020', 'E03T'],
}


def _kit_key(t):
    return TYPE_KIT.get(t) or 'Q' + t  # 'Qwater' etc. for the new kits


def _build_new_kits():
    kits = {}
    n = 0
    for t, moves in _NEW.items():
        key = _kit_key(t)
        kits[key] = []
        for (name, tmpl), slot in zip(moves, 'QWEPR'):
            kits[key].append(pd.Skill('AQ' + pd.B36[n // 36] + pd.B36[n % 36], name, tmpl, slot, t, key))
            n += 1
    return kits


NEW_KITS = _build_new_kits()

# the missile art of the new types: the nearest existing element art (poke_data.ELEMENT_ART has the rest)
for _t in _NEW:
    pd.ELEMENT_ART.setdefault(_t, pd.ELEMENT_ART['aura'])


def kit_for_type(t):
    """Skills (pd.Skill) of the kit of type t."""
    key = _kit_key(t)
    return pd.KITS[key] if key in pd.KITS else NEW_KITS[key]


def hero_types():
    """v1.8 unit id -> main type."""
    return {h: t for t, ids in HERO_TYPE.items() for h in ids}


def new_skills():
    """Skills that must be written as new ability rows (the new kits; the reused poke_data kits already are)."""
    return [sk for kit in NEW_KITS.values() for sk in kit]
