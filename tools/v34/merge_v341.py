"""Build "Pokemon Arena v3.4.1.w3x" = "Pokemon Arena v3.4.0.w3x" + the v3.3.4 / v3.3.5 choices of the merge plan.

Every file of v3.4.0 is kept; only these change:
  scripts\\war3map.j                 stats, legends, wild tier check, mob mana, type data / display, no type
                                    effectiveness (Ty_Enabled = false), map name
  war3map.w3u                       player HP x2 (uhpm), legend attack / armor x3/2.3, "Basic attack: <type>"
                                    tooltips, Expert Belt out of the Battle Shop
  Units\\CampaignAbilityStrings.txt  "Type: <type>" in the 74 elite skill tooltips (from v3.3.5)
  war3map.w3i                       name / description v3.4.1

Choices (merge plan, 2026-11-07):
  player HP  = HP x 40 x g(L)       (v3.3.5; v3.4.0 was x 20)        -> Stat keys 80/81 x2, uhpm x2
  player attack speed x2, Beedrill x1 (v3.3.5)                       -> Hero_ASBoost 2.0, Beedrill key 86 x2
  gym / Elite Four attack speed x1.7 (unchanged, own constant)       -> Gym_ASBoost 1.7
  legend attack / armor x3          (v3.3.5; v3.4.0 was x2.3)
  legend once per game, every 6 min; wild tier check every 3 min; full mana on spawn (v3.3.4)
  types: pokemondb.net/pokedex/all (Pokemon) + pokemondb.net/move/all (moves), coloured damage numbers with
  the type name (v3.3.5), no type effectiveness for now (Ty_Enabled = false), Expert Belt not sold

    python -I merge_v341.py "<...>/Pokemon Arena v3.4.0.w3x" "<...>/Pokemon Arena v3.4.1.w3x"
Needs tools/mpq.py and tools/objdata.py (same folder's parent or --tools). Never overwrites an existing map.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = '3.4.0', '3.4.1'
T4 = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 'flying', 'ghost', 'grass', 'ground', 'ice',
      'normal', 'poison', 'psychic', 'rock', 'steel', 'water']          # v3.4 T_ order (T_BUG = 0 ...)
COLORS = {'normal': 'A8A77A', 'fire': 'EE8130', 'water': '6390F0', 'electric': 'F7D02C', 'grass': '7AC74C',
          'ice': '96D9D6', 'fighting': 'C22E28', 'poison': 'A33EA1', 'ground': 'E2BF65', 'flying': 'A98FF3',
          'psychic': 'F95587', 'bug': 'A6B91A', 'rock': 'B6A136', 'ghost': '735797', 'dragon': '6F35FC',
          'dark': '705746', 'steel': 'B7B7CE', 'fairy': 'D685AD'}       # v3.3.5 damage_types.COLORS
HP_MULT = 2              # HP x 20 -> x 40
LEGEND_MULT = 3.0 / 2.3  # legend attack / armor x2.3 -> x3
BEEDRILL = 'E02K'
EXPERT_BELT = 'IB06'


def tidx(t):
    return T4.index(t) + 1  # stored + 1 in Ab_HT


def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit('war3map.j: %s: expected 1 match, found %d' % (what, n))
    return s.replace(old, new)


def func(s, name):
    m = re.search(r'^function %s takes.*?^endfunction\n' % re.escape(name), s, re.M | re.S)
    if not m:
        raise SystemExit('war3map.j: function %s not found' % name)
    return m


def patch_script(s, data, hero_ids, log):
    # ---- globals
    s = sub1(s, 'constant real Hero_ASBoost = 1.7        // v3.4: the players\' Pokemon attack 1.7x faster (Hero_HPSync)',
             'constant real Hero_ASBoost = 2.0        // v3.4.1: the players\' Pokemon attack 2x faster (v3.3.5), Beedrill x1\n'
             'constant real Gym_ASBoost = 1.7         // v3.4.1: gym / Elite Four Pokemon keep x1.7 (Gym_Spawn)\n'
             'constant boolean Ty_Enabled = false     // v3.4.1: type effectiveness off for now (types still shown)\n'
             'string array Type_Label                 // v3.4.1 (v3.3.5): name / colour of type T_ + 1\n'
             'string array Type_Color\n'
             'integer Dmg_Type = 0                    // type + 1 of the damage being shown (Dmg_OnDamaged)',
             'Hero_ASBoost')
    s = sub1(s, 'real Wild_LevelCheck = 300.0', 'real Wild_LevelCheck = 180.0', 'Wild_LevelCheck')
    s = sub1(s, 'real Leg_Interval = 180.0', 'real Leg_Interval = 360.0', 'Leg_Interval')
    s = sub1(s, 'real Leg_Next = 180.0', 'real Leg_Next = 360.0', 'Leg_Next')
    s = sub1(s, 'BlzGetUnitAttackCooldown(u, 0) / Hero_ASBoost, 0)', 'BlzGetUnitAttackCooldown(u, 0) / Gym_ASBoost, 0)',
             'Gym_Spawn attack speed')

    # ---- player HP x2 (keys 80 / 81), Beedrill attack cooldown x2 (key 86) to cancel Hero_ASBoost 2.0
    def hp(m):
        return "SaveInteger(Mega_HT, '%s', %s, %d)" % (m.group(1), m.group(2), int(m.group(3)) * HP_MULT)
    s, n = re.subn(r"SaveInteger\(Mega_HT, '(\w{4})', (8[01]), (\d+)\)", hp, s)
    log.append('HP keys 80/81 x2: %d lines' % n)
    m = re.search(r"SaveInteger\(Mega_HT, '%s', 86, (\d+)\)" % BEEDRILL, s)
    s = s.replace(m.group(0), "SaveInteger(Mega_HT, '%s', 86, %d)" % (BEEDRILL, int(m.group(1)) * 2))
    log.append('Beedrill key 86: %s -> %d' % (m.group(1), int(m.group(1)) * 2))

    # ---- Pokemon types (Ab_HT keys 53 / 54) from pokemondb
    ut = data['unit_types']
    out, done, changed = [], set(), 0
    for line in s.split('\n'):
        m = re.match(r"(\s*)call SaveInteger\(Ab_HT, '(\w{4})', (5[34]), (\d+)\)\s*$", line)
        if m and m.group(2) in ut:
            ind, uid = m.group(1), m.group(2)
            if uid in done:
                continue
            done.add(uid)
            _, t1, t2 = ut[uid]
            out.append("%scall SaveInteger(Ab_HT, '%s', 53, %d)" % (ind, uid, tidx(t1)))
            if t2:
                out.append("%scall SaveInteger(Ab_HT, '%s', 54, %d)" % (ind, uid, tidx(t2)))
            continue
        out.append(line)
    s2 = '\n'.join(out)
    log.append('types 53/54 rewritten for %d units' % len(done))
    s = s2

    # ---- kit skill types (Ab_HT key 50): the real move's type on pokemondb
    m = func(s, 'Ty_InitKits')
    body = m.group(0)
    extra = ''.join("    call SaveInteger(Ab_HT, '%s', 50, %d)  // v3.4.1: type of the move on pokemondb\n"
                    % (a, tidx(t)) for a, t in sorted(data['kit_types'].items()))
    s = s.replace(body, body[:-len('endfunction\n')] + extra + 'endfunction\n')
    log.append('kit skill types: %d' % len(data['kit_types']))

    # ---- no type effectiveness (eff stays 1.0: no x2 / x0.5, no Expert Belt, no "Super effective!")
    s = sub1(s, '    if mt >= 0 then\n        set eff = Ty_Mult(mt, t)',
             '    if Ty_Enabled and mt >= 0 then  // v3.4.1: off for now\n        set eff = Ty_Mult(mt, t)',
             'Ty_Mult in Ab_OnDamaging')

    # ---- legends: once per game (v3.3.4) + the 5 skills of v3.4
    j5 = data['jass_v335']
    leg = j5['Leg_Spawn']
    anchor = '// v3.3: legends have an Ability\n'
    if leg.count(anchor) != 1:
        raise SystemExit('Leg_Spawn v3.3.5: anchor not found')
    leg = leg.replace(anchor, anchor + '    call Ai_GiveKit(lg)  // v3.4: and the 5 skills of their type, cast by Ai_Tick\n')
    s = s.replace(func(s, 'Leg_Spawn').group(0), leg + '\n')
    s = s.replace(func(s, 'Leg_OnDeath').group(0), j5['Leg_OnDeath'] + '\n')

    # ---- coloured damage numbers with the type name (v3.3.5), the type from the v3.4 data
    m = func(s, 'Dmg_OnDamaged')
    body = m.group(0)
    body = sub1(body, '    local texttag tt = null\n',
                '    local texttag tt = null\n    local string str = ""\n', 'Dmg_OnDamaged locals')
    body = sub1(body, '    if src != null and d >= 1.0 and Dmg_Tags < Dmg_TagMax and not BlzGetEventIsAttack() then\n',
                '    set Dmg_Type = 0\n'
                '    if src != null and d >= 1.0 and Dmg_Tags < Dmg_TagMax and not BlzGetEventIsAttack() then\n'
                '        set Dmg_Type = Ty_Resolve(src) + 1  // v3.4.1: the move just used, else the Pokemon\'s first type\n'
                '        if Dmg_Type <= 0 and IsUnitType(src, UNIT_TYPE_HERO) then\n'
                '            set Dmg_Type = Ty_Of(src, 0) + 1\n'
                '        endif\n', 'Dmg_OnDamaged type')
    body = sub1(body, '            call SetTextTagText(tt, I2S(R2I(d)), 0.025)\n',
                '            set str = I2S(R2I(d))\n'
                '            if Dmg_Type > 0 then  // v3.3.5: the number in the colour of the type, with its name\n'
                '                set str = Type_Color[Dmg_Type] + str + " " + Type_Label[Dmg_Type] + "|r"\n'
                '            else\n'
                '                set str = "|cffffd228" + str + "|r"\n'
                '            endif\n'
                '            call SetTextTagText(tt, str, 0.025)\n', 'Dmg_OnDamaged text')
    body = sub1(body, '            call SetTextTagColor(tt, 255, 210, 40, 255)\n',
                '            call SetTextTagColor(tt, 255, 255, 255, 255)\n', 'Dmg_OnDamaged colour')
    s = s.replace(m.group(0), body)

    # ---- new functions before Mega_Init: mob mana (v3.3.4), type labels
    labels = ['function Dmg_InitTypes takes nothing returns nothing']
    for i, t in enumerate(T4):
        labels.append('    set Type_Label[%d] = "%s"' % (i + 1, t.capitalize()))
        labels.append('    set Type_Color[%d] = "|cff%s"' % (i + 1, COLORS[t].lower()))
    labels.append('endfunction')
    new_funcs = '\n'.join([j5['Mob_FullMana'], j5['Mob_OnEnter'], j5['Mob_InitMana'], '\n'.join(labels)]) + '\n'
    m = func(s, 'Mega_Init')
    s = s.replace(m.group(0), new_funcs + m.group(0))
    s = sub1(s, '    call Ext_PlaceShops()\n    call Item_InitData()\n',
             '    call Ext_PlaceShops()\n    call Mob_InitMana()  // v3.4.1 (v3.3.4): wild Pokemon spawn with full mana\n'
             '    call Item_InitData()\n    call Dmg_InitTypes()\n', 'Mega_Init calls')

    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    return s


def patch_w3u(raw, data, hero_ids, objdata, log):
    f = objdata.ObjFile(raw)
    ut = data['unit_types']
    n_hp = n_tip = n_leg = 0
    for o in f.all():
        uid = o.id
        if uid in hero_ids:
            hpm = o.get('uhpm')
            if hpm is not None:
                o.set('uhpm', next(m.type for m in o.mods if m.field == 'uhpm'), int(hpm) * HP_MULT)
                n_hp += 1
            tub = o.get('utub')
            if tub is not None and uid in ut and 'Basic attack:' not in tub:
                t = ut[uid][1]
                typ = next(m.type for m in o.mods if m.field == 'utub')
                o.set('utub', typ, tub + '|n|cff%s' % COLORS[t].lower() + 'Basic attack: %s|r' % t.capitalize())
                n_tip += 1
        if uid in data['legends']:
            exact = data.get('legend_stats_v335', {}).get(uid)  # the v3.3.5 values (x3 of the base data)
            for j, fld in enumerate(('ua1b', 'udef')):
                v = o.get(fld)
                typ = next(m.type for m in o.mods if m.field == fld)
                o.set(fld, typ, type(v)(exact[j] if exact else round(v * LEGEND_MULT)))
            n_leg += 1
        if uid == 'nBS0':
            sei = o.get('usei').split(',')
            sei.remove(EXPERT_BELT)
            o.set('usei', next(m.type for m in o.mods if m.field == 'usei'), ','.join(sei))
    log.append('w3u: uhpm x2 %d heroes, Basic attack tooltip %d, legends x3/2.3 %d, Expert Belt out of the shop'
               % (n_hp, n_tip, n_leg))
    return f.to_bytes()


def patch_strings(txt, data, log):
    lines = txt.split('\n')
    cur, n = None, 0
    tips = data['elite_ubertip_v335']
    for i, line in enumerate(lines):
        m = re.match(r'^\[(\w{4})\]\s*$', line)
        if m:
            cur = m.group(1)
            continue
        if cur in tips and line.startswith('Ubertip='):
            lines[i] = 'Ubertip=' + tips[cur] + ('\r' if line.endswith('\r') else '')
            n += 1
    if n != len(tips):
        raise SystemExit('CampaignAbilityStrings: %d of %d elite tooltips replaced' % (n, len(tips)))
    log.append('elite skill tooltips "Type:": %d' % n)
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tools', default=os.path.dirname(HERE))
    ap.add_argument('--data', default=os.path.join(HERE, 'v341_data.json'))
    ap.add_argument('--dump', help='folder to write the patched files to (for checks)')
    a = ap.parse_args()
    if os.path.exists(a.dst):
        raise SystemExit('%s exists, not overwriting' % a.dst)
    sys.path.insert(0, a.tools)
    import mpq
    import objdata
    data = json.load(open(a.data, encoding='utf-8'))
    arc = mpq.MPQ(a.src)
    log = []
    s = arc.read('scripts\\war3map.j').decode('latin-1')
    hero_ids = set(re.findall(r"SaveInteger\(Mega_HT, '(\w{4})', 80, ", s))
    data['legends'] = data.get('legends') or []
    s = patch_script(s, data, hero_ids, log)
    w3u = patch_w3u(arc.read('war3map.w3u'), data, hero_ids, objdata, log)
    cas = patch_strings(arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8'), data, log)
    w3i = arc.read('war3map.w3i')
    old = ('Pokemon Arena v%s' % OLD).encode()
    if old not in w3i:
        raise SystemExit('w3i: name not found')
    w3i = w3i.replace(old, ('Pokemon Arena v%s' % NEW).encode()).replace(
        ('v%s:' % OLD).encode(), ('v%s:' % NEW).encode())
    files = {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.w3u': w3u,
             'Units\\CampaignAbilityStrings.txt': cas.encode('utf-8'), 'war3map.w3i': w3i}
    if a.dump:
        os.makedirs(a.dump, exist_ok=True)
        for k, v in files.items():
            p = os.path.join(a.dump, k.replace('\\', '_'))
            open(p, 'wb').write(v)
    arc.save_with(a.dst, files)
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
