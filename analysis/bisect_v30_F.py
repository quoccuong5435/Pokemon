"""Bisect F: v3.0 with the Ability globals kept but every Ability function removed and not wired.
D (no Ability code) works; A (Ability functions kept, not wired) fails. F tells whether the globals alone break it.

Usage: python -I analysis/bisect_v30_F.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import build_v2  # noqa: E402
import bisect_v30 as b  # noqa: E402
import inject  # noqa: E402
import objects  # noqa: E402


def strip_funcs_only(glob, prelude, funcs):
    i = funcs.index(b.FUNC_FROM)
    j = funcs.index(b.FUNC_TO)
    return glob, prelude, funcs[:i] + funcs[j:]


def main():
    out = os.path.join(HERE, '..', 'out', 'bisect_v30_F.w3x')
    orig = (inject.inject, objects._ability_objects, inject.gen_ab_init, inject._split_module)
    objects._ability_objects = lambda s, abilities: []
    inject.gen_ab_init = lambda abil: ''
    inject._split_module = lambda: strip_funcs_only(*orig[3]())
    orig_inj = inject.inject

    def wired(script, *args, **kw):
        text = orig_inj(script, *args, **kw)
        for old, new in b.WIRING:
            assert text.count(old) == 1, old
            text = text.replace(old, new)
        return text.replace('Condition(function Ab_OnDamaging)', 'Condition(function Leg_OnDamage)')

    inject.inject = wired
    try:
        pkl = os.path.join(HERE, '..', '..', 'PKLegendsv3.1b.w3x')
        src = os.path.join(HERE, '..', '..', 'Pokemon Arena v1.8.w3x')
        r = build_v2.build(src, pkl, os.path.join(HERE, '..', 'mega_models'), out, version='3.0 bisect F')
        print('built', out, r.size)
    finally:
        inject.inject, objects._ability_objects, inject.gen_ab_init, inject._split_module = orig


if __name__ == '__main__':
    main()
