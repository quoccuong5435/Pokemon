"""v3.4.16: Megas the map lacked for Pokemon it has: Swampert (new starter), Sableye, Garchomp, Abomasnow.

No Mega model exists for them on this PC, so they look like the other model-less Megas (Mega Beedrill ...): the base
model 40% bigger, tinted, with an aura. Everything else follows Mega Altaria (index 32): a Mega Stone item IMxx (use it
to Mega Evolve, 60 s, cooldown 150 s), its item ability AMxx, a skin unit hMxx with the Mega types / Def / Sp. Def.
Stat bonuses = Mega base stats / normal base stats - 1 (Atk -> STR, Spe -> AGI, Sp. Atk -> INT).
"""
import re

# (index, hero, name, stone, Mega Ability index, types, (Def, Sp. Def), (STR %, AGI %, INT %), tint, shop)
MEGAS = [
    (33, 'EP05', 'Swampert', 'Swampertite', 35, ('T_WATER', 'T_GROUND'), (110, 110), (36, 17, 12), (255, 170, 90), 'nMS1'),
    (34, 'P3DA', 'Sableye', 'Sablenite', 68, ('T_DARK', 'T_GHOST'), (125, 115), (13, -60, 31), (200, 120, 255), 'nMS2'),
    (35, 'P1LA', 'Garchomp', 'Garchompite', 65, ('T_DRAGON', 'T_GROUND'), (115, 95), (31, -10, 50), (255, 120, 120), 'nMS3'),
    (36, 'P00A', 'Abomasnow', 'Abomasite', 80, ('T_GRASS', 'T_ICE'), (105, 105), (43, -50, 43), (180, 230, 255), 'n00Q'),
]
PRICE = 6000
AURA = 'Abilities\\\\Spells\\\\Other\\\\GeneralAuraTarget\\\\GeneralAuraTarget.mdl'  # as a JASS literal
DIG = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def ids(index):
    """index 33 -> ('IM0X', 'AM0X', 'hM0X')."""
    c = DIG[index // 36] + DIG[index % 36]
    return 'IM' + c, 'AM' + c, 'hM' + c


def patch_script(s, base_scale):
    """Mega_* entries 33..36 after Altaria (32), Mega_N, Ab_MegaAb. base_scale: {hero id: model scale}."""
    anchor = '    set Mega_B[32] = 255\n'
    if s.count(anchor) != 1:
        raise SystemExit('megas: Mega Altaria entry not found')
    add = []
    for idx, hero, name, stone, _ab, _ty, _dd, (ps, pa, pi), (r, g, b), _shop in MEGAS:
        im, am, hm = ids(idx)
        bs = base_scale[hero]
        add += ["    set Mega_Base[%d] = '%s'" % (idx, hero), "    set Mega_Stone[%d] = '%s'" % (idx, im),
                "    set Mega_Skin[%d] = '%s'" % (idx, hm), "    set Mega_Evolve[%d] = '%s'" % (idx, am),
                '    set Mega_PStr[%d] = %d' % (idx, ps), '    set Mega_PAgi[%d] = %d' % (idx, pa),
                '    set Mega_PInt[%d] = %d' % (idx, pi), '    set Mega_Price[%d] = %d' % (idx, PRICE),
                '    set Mega_Name[%d] = "Mega %s"' % (idx, name), '    set Mega_StoneName[%d] = "%s"' % (idx, stone),
                '    set Mega_Fx[%d] = "%s"' % (idx, AURA), '    set Mega_Scale[%d] = %.3f' % (idx, bs * 1.4),
                '    set Mega_BaseScale[%d] = %.3f' % (idx, bs), '    set Mega_R[%d] = %d' % (idx, r),
                '    set Mega_G[%d] = %d' % (idx, g), '    set Mega_B[%d] = %d' % (idx, b)]
    s = s.replace(anchor, anchor + '\n'.join(add) + '  // v3.4.16: Megas 33..36 (tools/v3411/megas.py)\n')
    if s.count('    set Mega_N = 33\n') != 1:
        raise SystemExit('megas: Mega_N = 33 not found')
    s = s.replace('    set Mega_N = 33\n', '    set Mega_N = %d  // v3.4.16\n' % (MEGAS[-1][0] + 1))
    anchor = '    set Ab_MegaAb[32] = 52\n'
    if s.count(anchor) != 1:
        raise SystemExit('megas: Ab_MegaAb[32] not found')
    s = s.replace(anchor, anchor + ''.join('    set Ab_MegaAb[%d] = %d\n' % (m[0], m[4]) for m in MEGAS))
    return s


def data_lines():
    """Skin types / Def / Sp. Def, stone 'one per Pokemon' flag and price (like IM0W)."""
    out = []
    for idx, _hero, _name, _stone, _ab, (t1, t2), (de, sd), _p, _c, _shop in MEGAS:
        im, _am, hm = ids(idx)
        out += ["    call SaveInteger(Ab_HT, '%s', 53, %s + 1)" % (hm, t1),
                "    call SaveInteger(Ab_HT, '%s', 54, %s + 1)" % (hm, t2),
                "    call SaveInteger(Fx_HT, '%s', 1, %d)" % (hm, de), "    call SaveInteger(Fx_HT, '%s', 2, %d)" % (hm, sd),
                "    call SaveInteger(Fx_HT, '%s', 2, 1)" % im, "    call SaveInteger(Fx_HT, '%s', 3, %d)" % (im, PRICE)]
    return out


def objects(w3u, objdata, abil, items, strings, func, set_keys, copy_section):
    """Skin units, stone items, Mega Evolve abilities, shop lists. Returns (strings, func)."""
    by = {o.new: o for o in w3u.custom}
    tmpl_u = by['hM0W']
    for idx, hero, name, stone, _ab, _ty, _dd, (ps, pa, pi), _c, shop in MEGAS:
        im, am, hm = ids(idx)
        if hm in by or abil.find(am) is not None or items.find(im) is not None:
            raise SystemExit('megas: id of Mega %s already used' % name)
        h = {x.field: x.value for x in by[hero].mods}
        scale = float(h.get('usca', 1.0)) * 1.4
        new = {'umdl': h['umdl'], 'uico': h.get('uico', ''), 'ussi': h.get('uico', ''), 'unam': 'Mega %s' % name,
               'upro': name, 'usca': scale, 'uawt': 'Mega %s' % name, 'utip': 'Mega %s' % name,
               'utpr': 'Mega %s' % name, 'utub': '|cffff66ccMega %s|r' % name}
        mods = [objdata.Mod(x.field, x.type, new.pop(x.field, x.value), x.level, x.data, x.end) for x in tmpl_u.mods]
        w3u.custom.append(objdata.Obj(tmpl_u.orig, hm, mods))
        row = dict(abil.find('AM0W'))
        row[1] = '"%s"' % am
        abil.rows.append(row)
        row = dict(items.find('IM0W'))
        row[1] = '"%s"' % im
        row[items.name_to_x['abilList']] = '"%s"' % am
        row[items.name_to_x['goldcost']] = str(PRICE)
        items.rows.append(row)
        bonus = '+%d%% STR, %+d%% AGI, %+d%% INT' % (ps, pa, pi)
        strings = copy_section(strings, 'AM0W', am)
        strings = set_keys(strings, am, [('Art', h.get('uico', '')), ('Tip', 'Mega Evolve - |cffff66ccMega %s|r' % name),
                                         ('Ubertip', '"%s Mega Evolves into |cffff66ccMega %s|r for 60s: %s.|n|n'
                                                     '|cffffcc00Cooldown:|r 150s"' % (name, name, bonus))])
        func = copy_section(func, 'IM0W', im)
        func = set_keys(func, im, [('Name', stone), ('Tip', 'Purchase |cffff66cc%s|r' % stone),
                                   ('Ubertip', '"|cffffcc00Use (click in the inventory):|r |cffff66ccMega Evolve|r '
                                               '|cffffcc00%s|r into |cffff66ccMega %s|r for 60s (%s). Cooldown 150s.'
                                               '|n|n|cffffcc00Only %s can use it.|r"' % (name, name, bonus, name)),
                                   ('Description', 'Mega Stone of %s.' % name), ('Art', h.get('uico', ''))])
        so = by[shop]
        for md in so.mods:
            if md.field == 'usei' and im not in md.value:
                if len(md.value.split(',')) >= 12:
                    raise SystemExit('megas: shop %s is full' % shop)
                md.value = md.value + ',' + im
    return strings, func


def base_scales(w3u_objs, starters_scale):
    out = {}
    for _i, hero, *_rest in MEGAS:
        if hero in starters_scale:
            out[hero] = starters_scale[hero]
        else:
            h = {x.field: x.value for x in w3u_objs[hero].mods}
            out[hero] = float(h.get('usca', 1.0))
    return out

