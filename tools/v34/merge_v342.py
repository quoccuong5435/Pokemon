"""Build "Pokemon Arena v3.4.2.w3x" from "Pokemon Arena v3.4.1.w3x": type effectiveness back on, with the k rule.

Chart: pokemondb.net/type (Gen 6+), the same 18 x 18 chart as Ty_Eff of v3.4 (checked cell by cell, 2026-11-08).
For each type of the target (1 or 2, Mega types included), against the type of the hit:
    super effective (x2)               k + 1
    not very effective (x0.5)          k - 1
    no effect (x0)                     k - 1   (counted as not very effective)
    k >= 0: damage x (1 + 0.5 k)        -> x1.5 (k = 1), x2.0 (k = 2)
    k <  0: damage x (1 + 0.25 k)       -> x0.75 (k = -1), x0.5 (k = -2)
The type of the hit: the move just used (skills, as v3.4.1) or, for a basic attack, the attacker's first type
(the "Basic attack: <type>" of the tooltips). Units without a type (dummies...) hit / are hit with k = 0.

Also: "Super effective!" / "Not very effective..." for any k != 0, Expert Belt back in the Battle Shop (+25% when
k > 0, attacks too), gym counter picks use the same rule, map name v3.4.2.

    python -I merge_v342.py "<...>/Pokemon Arena v3.4.1.w3x" "<...>/Pokemon Arena v3.4.2.w3x" [--tools <tools>]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = '3.4.1', '3.4.2'
EXPERT_BELT = 'IB06'


def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit('%s: expected 1 match, found %d' % (what, n))
    return s.replace(old, new)


def func(s, name):
    m = re.search(r'^function %s takes.*?^endfunction\n' % re.escape(name), s, re.M | re.S)
    if not m:
        raise SystemExit('war3map.j: function %s not found' % name)
    return m


K_FUNCS = '''// v3.4.2: type effectiveness, k rule. a / b = the target's types (-1 = none). Per type: x2 -> k + 1,
// x0.5 or x0 -> k - 1. Result 1 + Ty_KUp * k (k >= 0) or 1 + Ty_KDown * k (k < 0): x0.5 .. x2.
function Ty_KMult takes integer mt, integer a, integer b returns real
    local integer k = 0
    local real e = 1.0
    if mt < 0 then
        return 1.0
    endif
    if a >= 0 then
        set e = Ty_Eff[mt * 18 + a]
        if e > 1.0 then
            set k = k + 1
        elseif e < 1.0 then
            set k = k - 1
        endif
    endif
    if b >= 0 and b != a then
        set e = Ty_Eff[mt * 18 + b]
        if e > 1.0 then
            set k = k + 1
        elseif e < 1.0 then
            set k = k - 1
        endif
    endif
    if k >= 0 then
        return 1.0 + Ty_KUp * I2R(k)
    endif
    return 1.0 + Ty_KDown * I2R(k)
endfunction

function Ty_TypeMult takes integer mt, integer uid returns real
    return Ty_KMult(mt, LoadInteger(Ab_HT, uid, 53) - 1, LoadInteger(Ab_HT, uid, 54) - 1)
endfunction
'''


def patch_script(s, log):
    s = sub1(s, 'constant boolean Ty_Enabled = false     // v3.4.1: type effectiveness off for now (types still shown)',
             'constant boolean Ty_Enabled = true      // v3.4.2: type effectiveness on, k rule (Ty_KMult)\n'
             'constant real Ty_KUp = 0.5              // v3.4.2: k >= 0 -> x (1 + 0.5 k): x1.5 / x2\n'
             'constant real Ty_KDown = 0.25           // v3.4.2: k < 0 -> x (1 + 0.25 k): x0.75 / x0.5',
             'Ty_Enabled')
    # the k rule replaces the x2 / x0.5 product (Ty_ImmuneMult / Ty_MaxMult are no longer used)
    s = s.replace(func(s, 'Ty_TypeMult').group(0), K_FUNCS)
    s = s.replace(func(s, 'Ty_Mult').group(0),
                  'function Ty_Mult takes integer mt, unit t returns real\n'
                  '    return Ty_KMult(mt, Ty_Of(t, 0), Ty_Of(t, 1))  // v3.4.2: the target\'s current types (Mega)\n'
                  'endfunction\n')
    # gym counter picks: "super effective" = k > 0 now
    s = sub1(s, 'return (a >= 0 and Ty_TypeMult(a, def) >= 1.99) or (b >= 0 and Ty_TypeMult(b, def) >= 1.99)',
             'return (a >= 0 and Ty_TypeMult(a, def) > 1.01) or (b >= 0 and Ty_TypeMult(b, def) > 1.01)',
             'Ty_Counters')
    # Expert Belt: k > 0
    s = sub1(s, '        if eff >= 1.99 and Itm_Flag(src, 6) then',
             '        if eff > 1.01 and Itm_Flag(src, 6) then  // v3.4.2: any super effective hit', 'Expert Belt')
    # Ab_OnDamaging: basic attacks get the attacker's first type for effectiveness only
    m = func(s, 'Ab_OnDamaging')
    body = m.group(0)
    body = sub1(body, '    local real eff = 1.0\n', '    local real eff = 1.0\n    local integer et = -1\n',
                'Ab_OnDamaging locals')
    body = sub1(body, '    if Ty_Enabled and mt >= 0 then  // v3.4.1: off for now\n        set eff = Ty_Mult(mt, t)\n',
                '    // v3.4.2: effectiveness of skills (type of the move) and basic attacks (first type of the attacker)\n'
                '    set et = mt\n'
                '    if atk and et < 0 then\n'
                '        set et = Ty_Of(src, 0)\n'
                '    endif\n'
                '    if Ty_Enabled and et >= 0 then\n'
                '        set eff = Ty_Mult(et, t)\n', 'Ab_OnDamaging effectiveness')
    body = sub1(body, 'if mt >= 0 and Mega_Time >= LoadReal(Ab_HT, ht, 57) and (eff >= 1.99 or eff <= 0.51) then',
                'if et >= 0 and Mega_Time >= LoadReal(Ab_HT, ht, 57) and (eff > 1.01 or eff < 0.99) then',
                'effectiveness text')
    body = sub1(body, '            if eff >= 1.99 then\n                call Ab_Say(t, "Super effective!"',
                '            if eff > 1.01 then\n                call Ab_Say(t, "Super effective!"', 'super effective text')
    s = s.replace(m.group(0), body)
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    log.append('war3map.j: k rule, basic attacks typed, texts / Expert Belt / gym counters on k, v%s' % NEW)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tools', default=os.path.dirname(HERE))
    a = ap.parse_args()
    if os.path.exists(a.dst):
        raise SystemExit('%s exists, not overwriting' % a.dst)
    sys.path.insert(0, a.tools)
    import mpq
    import objdata
    arc = mpq.MPQ(a.src)
    log = []
    s = patch_script(arc.read('scripts\\war3map.j').decode('latin-1'), log)
    # Expert Belt back in the Battle Shop, after Assault Vest's neighbour IB05 (v3.4.0 order)
    f = objdata.ObjFile(arc.read('war3map.w3u'))
    for o in f.all():
        if o.id == 'nBS0':
            sei = o.get('usei').split(',')
            if EXPERT_BELT not in sei:
                sei.insert(sei.index('IB05') + 1, EXPERT_BELT)
                o.set('usei', next(x.type for x in o.mods if x.field == 'usei'), ','.join(sei))
            log.append('Battle Shop: ' + ','.join(sei))
    w3u = f.to_bytes()
    itf = arc.read('Units\\ItemFunc.txt').decode('utf-8')
    itf = sub1(itf, 'Ubertip=Super effective moves deal +25% damage.',
               'Ubertip=Super effective hits (attacks and moves) deal +25% damage.', 'ItemFunc Expert Belt')
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')
    arc.save_with(a.dst, {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.w3u': w3u,
                          'Units\\ItemFunc.txt': itf.encode('utf-8'), 'war3map.w3i': w3i})
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
