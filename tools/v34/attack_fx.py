"""v3.4.5, plan 9 (docs/v3.4/9-ke-hoach-don-danh-thuong.md): the basic attack of the wild / gym / legend units
(nX..) whose species hits physically (Attack >= Sp. Attack in learnsets.json) becomes a melee attack: no missile,
range ATTACK_RANGE. Units with a special attacker keep their missile. Units whose species is not in learnsets.json
are left alone (listed in the report).

apply(w3u) -> list of (unit id, species) changed; report printed by build_v34.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
LEARNSETS = os.path.join(TOOLS, 'learnsets.json')
ATTACK_RANGE = 128.0  # the standard melee range of Warcraft III


def _species_key(name):
    """learnsets.json key of a unit name: Alolan-X -> x-alola (as learn_data), Tauros Aqua / Blaze / Combat -> tauros"""
    n = name.strip().lower()
    for form in ('tauros aqua', 'tauros blaze', 'tauros combat'):
        if n == form:
            return 'tauros'
    if n.startswith('alolan-'):
        return n[len('alolan-'):] + '-alola'
    return n.replace(' ', '-').replace('.', '').replace("'", '')


def _stats():
    species = json.load(open(LEARNSETS, encoding='utf-8'))['species']
    return species


def apply(w3u):
    from objdata import T_REAL, T_STRING
    species = _stats()
    changed, skipped = [], []
    for o in w3u.custom:
        if not str(o.id).startswith('nX'):
            continue
        if (o.get('ua1w') or '') != 'missile':
            continue
        name = str(o.get('unam') or '')
        s = species.get(_species_key(name))
        if s is None:
            skipped.append(name)
            continue
        atk, spa = s['stats'][1], s['stats'][3]
        if atk < spa:
            continue  # special attacker: keeps the missile
        o.set('ua1w', T_STRING, 'normal')
        o.set('ua1r', T_REAL, ATTACK_RANGE)
        o.remove('ua1m')
        changed.append((o.id, name))
    return changed, skipped
