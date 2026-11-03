"""Bisect builds of v3.0 to find what makes the map 'unavailable or corrupted' in the game.

A: ability data kept, but the ability JASS is not wired (no Ab_InitData call, no Ab damage trigger,
   no Ab timer, no revive trigger). The Ab functions stay in the script but nothing calls them.
B: ability data removed (no AB info buttons, no AX bonus abilities), JASS kept.

Usage (from _PokemonArena2.0_work):
  python -I analysis/bisect_v30.py A
  python -I analysis/bisect_v30.py B
  python -I analysis/bisect_v30.py D   (no Ability code at all: no data, no JASS; skill rework and host commands stay)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
import build_v2  # noqa: E402
import inject  # noqa: E402
import objects  # noqa: E402

WIRING = [
    ('call Ab_InitData()\n', ''),
    ('    call TriggerAddCondition(t, Condition(function Ab_OnDamaging))\n', ''),
    ('    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_REVIVE_FINISH)\n', ''),
    ('    call TriggerAddAction(t, function Ab_OnRevive)\n', ''),
    ('    call TimerStart(Ab_Timer, 0.5, true, function Ab_Tick)\n', ''),
]


GLOB_CUT = '// Pokemon Abilities (v2.8): data filled'
FUNC_FROM = '// Pokemon Abilities (v2.8). Per-unit keys'
FUNC_TO = 'function Mega_Init takes'


def strip_ability_jass(glob, prelude, funcs):
    """Remove every Ability global and function (mode D)."""
    glob = glob[:glob.index(GLOB_CUT)]
    i = funcs.index(FUNC_FROM)
    j = funcs.index(FUNC_TO)
    return glob, prelude, funcs[:i] + funcs[j:]


def main(which, tag=''):
    out = os.path.join(HERE, '..', 'out', 'bisect_v30_%s%s.w3x' % (which, tag))
    orig_inject = inject.inject
    orig_ability_objects = objects._ability_objects
    orig_gen_ab_init = inject.gen_ab_init

    if which in ('B', 'D'):
        objects._ability_objects = lambda s, abilities: []  # no AB info rows, no AX bonus rows
    if which == 'D':
        orig_split = inject._split_module
        inject.gen_ab_init = lambda abil: ''
        inject._split_module = lambda: strip_ability_jass(*orig_split())

    def patched_inject(script, *args, **kw):
        text = orig_inject(script, *args, **kw)
        if which in ('A', 'D'):
            for old, new in WIRING:
                n = text.count(old)
                if n != 1:
                    raise ValueError('wiring not found exactly once: %r (%d)' % (old, n))
                text = text.replace(old, new)
            # keep the legend damage check registered, like before v2.8
            text = text.replace('Condition(function Ab_OnDamaging)', 'Condition(function Leg_OnDamage)')
        return text

    inject.inject = patched_inject
    try:
        pkl = os.path.join(HERE, '..', '..', 'PKLegendsv3.1b.w3x')
        src = os.path.join(HERE, '..', '..', 'Pokemon Arena v1.8.w3x')
        r = build_v2.build(src, pkl, os.path.join(HERE, '..', 'mega_models'), out, version='3.0 bisect %s' % which)
        print('built', out, r.size)
    finally:
        inject.inject = orig_inject
        objects._ability_objects = orig_ability_objects
        if which == 'D':
            inject._split_module = orig_split
            inject.gen_ab_init = orig_gen_ab_init


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '')
