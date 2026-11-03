"""Wild creeps: the 30 new species, which unit types count as wild, and respawn camps (see wild-legend spec)."""
import re

import balance
from dataclasses import dataclass

LEVEL_CHECK_SECONDS = 300.0  # v2.7: tier = (average level of the 2 lowest players) / LEVELS_PER_TIER, every 5 min
LEVELS_PER_TIER = 10
TIER_MAX = 10
WILD_SOUL_CHANCE = balance.WILD_SOUL_CHANCE  # % chance an elite drops its species' Soul
TIER_STEP = balance.WILD_TIER_STEP
TIER_ARMOR = balance.WILD_TIER_ARMOR
RESPAWN_SECONDS = balance.WILD_RESPAWN
CAMP_SIZE_MULT = balance.CAMP_SIZE_MULT
CAMP_RADIUS = 600.0
NOGL_LEVEL = 5           # 'nogl' (Machamp model) keeps the default Ogre Lord level
WILD_BASES = ('nmrm', 'nmrl', 'nmrr')
SPECIES_TEMPLATE = 'n00T'  # existing wild creep object the new species are cloned from

# power: (level, hp, damage, armor, gold)
POWER_STATS = {  # v3.2: HP x0.7 of the v3.1 table, so a tier-10 creep (x1.8) has about 16k HP instead of 32k
    1: (3, 245, 15, 1, 10), 2: (7, 630, 45, 2, 20), 3: (12, 1050, 80, 4, 30), 4: (18, 1540, 120, 6, 45),
    5: (24, 2100, 160, 8, 60), 6: (32, 2800, 210, 11, 80), 7: (40, 3850, 270, 14, 100),
    8: (50, 5250, 340, 18, 130), 9: (62, 7000, 420, 22, 160), 10: (75, 9100, 500, 26, 200),
}
_NAMES = {
    1: ('Hoothoot', 'Lotad', 'Diglett'), 2: ('Mareep', 'Houndour', 'Swinub'),
    3: ('Sneasel', 'Misdreavus', 'Chinchou'), 4: ('Noctowl', 'Flaaffy', 'Breloom'),
    5: ('Manectric', 'Piloswine', 'Vibrava'), 6: ('Houndoom', 'Mismagius', 'Weavile'),
    7: ('Ampharos', 'Ludicolo', 'Flygon'), 8: ('Mamoswine', 'Altaria', 'Absol'),
    9: ('Electivire', 'Magmortar', 'Rhyperior'), 10: ('Snorlax', 'Lapras', 'Dusknoir'),
}


# main type of each wild species: the elite creep gets the 5-skill kit of this type (skill_data)
SPECIES_TYPE = {
    'Hoothoot': 'flying', 'Lotad': 'water', 'Diglett': 'ground', 'Mareep': 'electric', 'Houndour': 'dark',
    'Swinub': 'ice', 'Sneasel': 'dark', 'Misdreavus': 'ghost', 'Chinchou': 'water', 'Noctowl': 'flying',
    'Flaaffy': 'electric', 'Breloom': 'grass', 'Manectric': 'electric', 'Piloswine': 'ice', 'Vibrava': 'ground',
    'Houndoom': 'dark', 'Mismagius': 'ghost', 'Weavile': 'dark', 'Ampharos': 'electric', 'Ludicolo': 'water',
    'Flygon': 'ground', 'Mamoswine': 'ice', 'Altaria': 'dragon', 'Absol': 'dark', 'Electivire': 'electric',
    'Magmortar': 'fire', 'Rhyperior': 'rock', 'Snorlax': 'normal', 'Lapras': 'water', 'Dusknoir': 'ghost',
}


@dataclass(frozen=True)
class Species:
    index: int
    name: str
    power: int

    @property
    def id(self):
        return 'nW%02X' % self.index

    @property
    def level(self):
        return POWER_STATS[self.power][0]

    @property
    def hp(self):
        return POWER_STATS[self.power][1]

    @property
    def dmg(self):
        return POWER_STATS[self.power][2]

    @property
    def armor(self):
        return POWER_STATS[self.power][3]

    @property
    def gold(self):
        return POWER_STATS[self.power][4]


SPECIES = [Species(i, name, p) for i, (p, name) in
           enumerate((p, n) for p in sorted(_NAMES) for n in _NAMES[p])]


@dataclass(frozen=True)
class Camp:
    x: float
    y: float
    count: int
    power: int


def power_for_level(level):
    for p, top in enumerate((4, 9, 14, 20, 27, 35, 44, 55, 70), 1):
        if level <= top:
            return p
    return 10


def _level(obj_by_id, uid):
    if uid == 'nogl':
        return NOGL_LEVEL
    o = obj_by_id.get(uid)
    return o.get('ulev') if o is not None else None


def wild_types(w3u):
    """Custom wild creeps of v1.8 (nmrm/nmrl/nmrr, level <= 12, not a '_Loc' guardian) + 'nogl'."""
    out = []
    for o in w3u.custom:
        lv = o.get('ulev')
        if o.orig in WILD_BASES and lv is not None and lv <= 12 and '_Loc' not in (o.get('unam') or ''):
            out.append(o.new)
    return out + ['nogl']


def _init_creeps(script):
    start = script.index('local player p=Player(PLAYER_NEUTRAL_AGGRESSIVE)')
    end = script.index('endfunction', start)
    return [(m.group(1), float(m.group(2)), float(m.group(3))) for m in
            re.finditer(r"CreateUnit\(p,'(\w{4})',(-?[\d.]+),(-?[\d.]+),", script[start:end])]


def camps(script, w3u):
    """Cluster the pre-placed wild creeps (single linkage, distance < CAMP_RADIUS)."""
    types = set(wild_types(w3u))
    objs = {o.new: o for o in w3u.custom}
    pts = [c for c in _init_creeps(script) if c[0] in types]
    parent = list(range(len(pts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if (pts[i][1] - pts[j][1]) ** 2 + (pts[i][2] - pts[j][2]) ** 2 < CAMP_RADIUS ** 2:
                parent[find(i)] = find(j)
    groups = {}
    for i, p in enumerate(pts):
        groups.setdefault(find(i), []).append(p)
    out = []
    for members in sorted(groups.values(), key=lambda g: (g[0][1], g[0][2])):
        lv = max(_level(objs, m[0]) or 1 for m in members)
        out.append(Camp(sum(m[1] for m in members) / len(members), sum(m[2] for m in members) / len(members),
                        len(members), power_for_level(lv)))
    return out


# ------------------------------------------------------------------ own-species Souls (v2.6)
EXISTING_SOULS = {'Magikarp': 'I01O'}  # the map already has these Souls (and their transform trigger)


@dataclass(frozen=True)
class WildSoul:
    name: str
    hero: str          # playable unit the Soul turns a Pokemon into
    item: str          # Soul item id
    new: bool          # True = item and transform trigger added by us
    wild_types: tuple  # wild unit types of this species that may drop it


def _species_name(objs, t):
    if t == 'nogl':
        return 'Machamp'
    if t in objs:
        return objs[t].get('unam')
    return {s.id: s.name for s in SPECIES}[t]


def wild_souls(w3u):
    """One Soul per wild species that has a playable version (v1.8 heroes and the new Pokemon)."""
    import poke_data
    objs = {o.new: o for o in w3u.custom}
    heroes = {}
    for o in w3u.custom:
        if o.new[:1] == 'E' and o.get('upro'):
            heroes.setdefault(o.get('upro').lower(), o.new)
    for f in poke_data.FORMS:
        heroes.setdefault(f.name.lower(), f.id)
    order, types = [], {}
    for t in wild_types(w3u) + [s.id for s in SPECIES]:
        name = _species_name(objs, t)
        if (name or '').lower() not in heroes:
            continue
        if name not in types:
            order.append(name)
        types.setdefault(name, []).append(t)
    out, n = [], 0
    for name in order:
        if name in EXISTING_SOULS:
            item, new = EXISTING_SOULS[name], False
        else:
            item, new = 'IS%02X' % n, True
            n += 1
        out.append(WildSoul(name, poke_data.base_form_id(heroes[name.lower()]), item, new, tuple(types[name])))
    out.append(WildSoul('Celebi', poke_data.CELEBI_HERO, 'ISCE', True, ()))  # v3.3: Soul of the Celebi legend
    import legend_data
    for k, lg in enumerate(n for n in legend_data.PKL_LEGEND_NAMES):  # v3.3: Souls of the PKLegends legends
        form = next(f for f in poke_data.FORMS if f.name == lg)
        out.append(WildSoul(lg, poke_data.base_form_id(form.id), 'ISL%d' % k, True, ()))
    return out
