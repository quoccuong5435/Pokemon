"""Learned moves (see docs/superpowers/specs/2026-11-01-learned-moves-design.md): which real moves each Pokemon can learn,
how a move becomes a skill template, and the ids of the move abilities (one per move and command-card slot).

Data comes from tools/learnsets.json (analysis/fetch_pokeapi.py).
"""
import json
import os
from dataclasses import dataclass, field

import poke_data

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = 4                 # learned-move buttons: command card row 0, hotkeys Q W E R
SLOT_LETTER = 'VWYZ'      # second character of the ability id of slot 0..3
SLOT_HOTKEYS = 'QWER'
MIN_OFFER = 10            # a move is available from this hero level at the earliest
CAND_MAX = 8              # candidate moves kept per species (the best by score)
SLOTS = 4                 # move slots on the command card (Q W E R)
STEP = 8                  # the k-th candidate is available from hero level MIN_OFFER + STEP * k at the earliest
B36 = poke_data.B36

try:
    _DATA = json.load(open(os.path.join(HERE, 'learnsets.json'), encoding='utf-8'))
except OSError:
    _DATA = {'species': {}, 'moves': {}}
SPECIES = _DATA['species']
MOVES = _DATA['moves']

SPECIAL = {
    'aegislash': 'aegislash-shield', 'mr.mime': 'mr-mime', "farfetch'd": 'farfetchd', "sirfetch'd": 'sirfetchd', 'nidoran': 'nidoran-m',
    'deoxys': 'deoxys-normal', 'giratina': 'giratina-altered', 'darmanitan': 'darmanitan-standard',
    'leafleon': 'leafeon', 'tauros aqua': 'tauros-paldea-aqua-breed', 'tauros blaze': 'tauros-paldea-blaze-breed',
    'tauros combat': 'tauros-paldea-combat-breed', 'mr. mime': 'mr-mime',
}


def slug(name):
    """PokeAPI species name of a Pokemon name used in the map / PKLegends."""
    n = name.strip().lower()
    if n in SPECIAL:
        return SPECIAL[n]
    if n.startswith('alolan-'):
        return n[len('alolan-'):] + '-alola'
    return n.replace(' ', '-').replace('.', '').replace("'", '')


def score(info):
    """Strength of a move: power x accuracy (accuracy 0 in the data = never misses)."""
    return info['power'] * (info['accuracy'] or 100) / 100.0


def candidates(species_slug):
    """[(available hero level, move slug)] of the best damaging moves of a species, by learn level."""
    s = SPECIES.get(species_slug)
    if s is None:
        return []
    best = {}
    for lv, mv in s['moves']:
        info = MOVES.get(mv)
        if info is None or info['power'] <= 0:
            continue
        if mv not in best or lv < best[mv]:
            best[mv] = lv
    top = sorted(best, key=lambda mv: (-score(MOVES[mv]), best[mv], mv))[:CAND_MAX]
    ordered = sorted(((best[mv], mv) for mv in top), key=lambda c: (c[0], -score(MOVES[c[1]]), c[1]))
    # v3.3: every move comes at its real learn level (the Bulbapedia / PokeAPI level-up list), so a new
    # Pokemon starts with the level-1 moves only; a move replaces the weakest known move when it is stronger
    return [(max(1, lv), mv) for lv, mv in ordered]


# power band -> (physical template, special template, tier thresholds: tier 1 up to a, tier 2 up to b, else tier 3)
_BANDS = ((60, 'DAGGER', 'CHAIN', 40, 50), (90, 'BOLT', 'WAVE', 70, 80), (115, 'LINE', 'NOVA', 100, 108),
          (10 ** 6, 'ULT_STOMP', 'ULT_WAVE', 130, 140))


# v3.3: the shape of the skill follows the move (names), not only its power
AREA_MOVES = {'earthquake', 'surf', 'discharge', 'explosion', 'self-destruct', 'hyper voice', 'bulldoze', 'rock slide',
              'heat wave', 'blizzard', 'muddy water', 'sludge wave', 'razor leaf', 'air cutter', 'icy wind', 'magnitude',
              'boomburst', 'petal blizzard', 'eruption', 'water spout', 'twister', 'parabolic charge', 'sparkling aria',
              'precipice blades', 'lava plume', 'overdrive', 'snarl', 'dazzling gleam', 'misty explosion', 'mind blown',
              'earth power', 'rock tomb', 'sandstorm', 'hurricane', 'thunder', 'fire blast', 'inferno', 'judgment',
              'supercell slam', 'stomping tantrum', 'high horsepower', 'diamond storm', 'springtide storm'}
LINE_WORDS = ('beam', 'ray', 'cannon', 'laser', 'pulse', 'driver', 'lance')
CONE_WORDS = ('flamethrower', 'breath', 'spray', 'gas', 'powder', 'whirlwind', 'overheat', 'burn out', 'sludge bomb')


def shape_of(info):
    """'area' (around the user), 'line', 'cone' or 'single' (a target) from the move name."""
    name = (info.get('name') or '').lower()
    if name in AREA_MOVES:
        return 'area'
    if any(w in name for w in LINE_WORDS):
        return 'line'
    if any(w in name for w in CONE_WORDS):
        return 'cone'
    return 'single'


def template_for(info):
    """(poke_data template key, level column 1..3) of a damaging move: the shape picks the template family, the"""
    """class (physical / special) the variant and the power the tier."""
    p = info['power']
    special = info['class'] != 'physical'
    for top, _phys, _spec, a, b in _BANDS:
        if p <= top:
            tier = 1 if p <= a else 2 if p <= b else 3
            break
    else:
        raise AssertionError(p)
    reg = 1 if p <= 60 else 2 if p <= 100 else 3  # tier of the regular templates, from the power
    shape = shape_of(info)
    if shape == 'area':
        if p > 115 and not special:
            return 'ULT_STOMP', tier
        return ('NOVA' if special else 'STOMP'), reg
    if shape == 'line':
        if p > 115:
            return 'ULT_WAVE', tier
        return ('WAVE' if special else 'LINE'), reg
    if shape == 'cone':
        return 'CONE', reg
    if p <= 60:
        return ('CHAIN' if special else 'DAGGER'), reg
    return 'BOLT', reg


def ability_id(slot, move_index):
    """Object id of the ability of a move in a command-card slot: A + V/W/Y/Z + two base-36 digits."""
    return 'A' + SLOT_LETTER[slot] + B36[move_index // 36] + B36[move_index % 36]


@dataclass(frozen=True)
class Move:
    index: int
    slug: str
    name: str
    type: str
    cls: str
    power: int
    accuracy: int
    score: int
    template: str
    tier: int


@dataclass
class MovePlan:
    moves: list      # Move, indexed by Move.index
    by_unit: dict    # unit type id -> [(available hero level, move index)]
    tm_by_unit: dict = field(default_factory=dict)  # v3.3: unit type id -> [move index] of its TM/HM moves


def hero_species(w3u):
    """Unit type id -> Pokemon name of every playable hero: the v1.8 heroes of the map plus the new forms of v2.3."""
    out = {o.new: o.get('upro') for o in w3u.custom if o.new[:1] == 'E' and o.get('upro')}
    out.update({f.id: f.name for f in poke_data.FORMS})
    out[poke_data.CELEBI_HERO] = 'Celebi'
    return out


def kit_names(uid):
    """Lower-case names of the 5 kit skills of a hero type (v1.8 heroes and the new forms)."""
    import skill_data
    typ = skill_data.hero_types().get(uid)
    if typ is not None:
        kit = skill_data.kit_for_type(typ)
    else:
        form = poke_data.FORM_BY_ID.get(uid)
        kit = poke_data.KITS.get(form.kit, []) if form else []
    return {sk.name.lower() for sk in kit}


TM_MAX = 40  # TM/HM moves kept per species (the strongest damaging ones)


def tm_candidates(species_slug):
    """Damaging TM/HM moves (move slugs) of a species, strongest first."""
    s = SPECIES.get(species_slug)
    if s is None:
        return []
    mv = [m for m in s.get("tm", []) if m in MOVES and MOVES[m]["power"] > 0]
    return sorted(mv, key=lambda m: (-score(MOVES[m]), m))[:TM_MAX]


def build_plan(units):
    """units: {unit type id: Pokemon name} -> MovePlan (moves sorted by slug, only the ones some Pokemon can learn)."""
    per_unit = {uid: [(lv, mv) for lv, mv in candidates(slug(name)) if MOVES[mv]['name'].lower() not in kit_names(uid)]
                for uid, name in units.items()}
    tm_unit = {uid: [m for m in tm_candidates(slug(name)) if MOVES[m]["name"].lower() not in kit_names(uid)]
               for uid, name in units.items()}
    slugs = sorted({mv for lst in per_unit.values() for _, mv in lst} | {m for lst in tm_unit.values() for m in lst})
    index = {mv: i for i, mv in enumerate(slugs)}
    moves = []
    for mv in slugs:
        info = MOVES[mv]
        tmpl, tier = template_for(info)
        moves.append(Move(index[mv], mv, info['name'], info['type'], info['class'], info['power'], info['accuracy'],
                          round(score(info)), tmpl, tier))
    by_unit = {uid: [(lv, index[mv]) for lv, mv in lst] for uid, lst in per_unit.items() if lst}
    tm_by_unit = {uid: [index[m] for m in lst] for uid, lst in tm_unit.items() if lst}
    return MovePlan(moves, by_unit, tm_by_unit)
