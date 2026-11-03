"""v3.3: one tavern per type for the PKLegends Pokemon (the ones nothing evolves into, no legends), laid out in a grid
next to the old tavern. Slot 0 of the grid is the Gen 3-4 tavern (poke_data.TAVERN_ID), slots 1.. are the type taverns."""
import learn_data
import poke_data

B36 = poke_data.B36
PICK_TYPES = ('normal', 'fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 'ground', 'flying',
              'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy')
TAVERN_PREFIX = 'nTP'
SELL_HOTKEYS = 'QWERASDFZXCV'
# grid of 4 columns x 5 rows packed into the dirt patch around the Archer wisp at (-128, 4544) (world coordinates)
GRID_X = (-320.0, -192.0, -64.0, 64.0)
GRID_Y = (4764.0, 4654.0, 4544.0, 4434.0, 4324.0)
FACE = 270.0
TYPE_ICON = {'normal': 'BTNPkmnNormal', 'fire': 'BTNPkmnFire', 'water': 'BTNPkmnWater', 'grass': 'BTNPkmnGrass',
             'electric': 'BTNPkmnElectr', 'psychic': 'BTNPkmnPsy', 'rock': 'BTNPkmnRock', 'dragon': 'BTNPkmnDragon',
             'fighting': 'BTNPkmnFighting', 'ground': 'BTNPkmnGround', 'flying': 'BTNPkmnFlying',
             'poison': 'BTNPkmnPoison', 'bug': 'BTNPkmnBug', 'ghost': 'BTNPkmnGhost', 'ice': 'BTNPkmnIce',
             'steel': 'BTNPkmnSteel', 'fairy': 'BTNPkmnFairy', 'dark': 'BTNPkmnDark'}


def primary_type(name):
    sp = learn_data.SPECIES.get(learn_data.slug(name))
    t = sp['types'][0] if sp and sp.get('types') else 'normal'
    return t if t in PICK_TYPES else 'normal'


def type_label(name):
    """Unit type name of a PKLegends form, like the v1.8 heroes: 'Fire&Fighting Pokemon'."""
    sp = learn_data.SPECIES.get(learn_data.slug(name))
    types = [t for t in (sp.get('types') if sp else None) or ['normal'] if t in PICK_TYPES] or ['normal']
    return '&'.join(t.capitalize() for t in types) + ' Pokemon'


def later_form_names():
    """Names of the forms that are form 2 or 3 of their family in the PokeAPI evolution chain (even when the earlier
    form is not playable): they are not offered in the picker or by -random."""
    import json
    import os
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evolutions.json'), encoding='utf-8') as fh:
        species = json.load(fh)['species']
    have = {learn_data.slug(f.name) for f in poke_data.FORMS}  # an earlier form that is not in the game does not count
    return {n for n, v in species.items() if any(b == learn_data.slug(n) and a in have for a, b, *_ in v.get('chain', []))}


def pickable_forms():
    """PKLegends forms offered in the type taverns: not evolved from another form, not legendary."""
    targets = {f.evolves_to for f in poke_data.FORMS if f.evolves_to}
    later = later_form_names()
    return [f for f in poke_data.FORMS if f.id[:1] == 'P' and f.id not in targets and f.name not in later
            and f.name not in poke_data.LEGENDARY_NAMES]


def groups():
    """[(type, [form ids sorted by name])] for the types that have at least one pickable form, in PICK_TYPES order."""
    by = {}
    for f in pickable_forms():
        by.setdefault(primary_type(f.name), []).append(f)
    return [(t, [f.id for f in sorted(by[t], key=lambda f: f.name.lower())]) for t in PICK_TYPES if t in by]


def tavern_id(i):
    return TAVERN_PREFIX + B36[i]


def grid_slot(k):
    """(x, y, face) of grid slot k (0 = the Gen 3-4 tavern)."""
    return GRID_X[k % len(GRID_X)], GRID_Y[k // len(GRID_X)], FACE


def tavern_name(typ):
    return '%s Tavern' % typ.capitalize()
