"""v3.4.16: the Gen 2-7 starter lines that Arena did not have, as playable Pokemon (33 heroes EP00..EP0W).

Models and icons: "Pokemon World V1.71.w3x" (Unit\\<dex>.mdx, ReplaceableTextures\\CommandButtons\\BTN_<dex>.blp; real
MPQ header at 1024). Stats, types, Abilities, level-up moves and TMs: tools/learnsets.json (PokeAPI, origin 'starter').
Numbers follow the existing heroes (Treecko EN03..): HP = 40 x HP, STR = Atk, AGI = Spe, INT = Sp. Atk, per level
stat / 50, armor = 0.6 x Def, Fx_HT 1 / 2 = Def / Sp. Def, main stat STR if Atk >= Sp. Atk else INT.

    used by tools/v3411/apply.py (script data, picker) and tools/v3411/build.py (units, models)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
PW_MAP = os.path.join(os.path.dirname(WORK), 'Pokemon World V1.71.w3x')

# (names of the line, dex numbers, evolution levels, Arena Ability index: 1 Overgrow, 2 Blaze, 3 Torrent)
LINES = [
    (('Totodile', 'Croconaw', 'Feraligatr'), (158, 159, 160), (18, 30), 3),
    (('Mudkip', 'Marshtomp', 'Swampert'), (258, 259, 260), (16, 36), 3),
    (('Turtwig', 'Grotle', 'Torterra'), (387, 388, 389), (18, 32), 1),
    (('Chimchar', 'Monferno', 'Infernape'), (390, 391, 392), (14, 36), 2),
    (('Piplup', 'Prinplup', 'Empoleon'), (393, 394, 395), (16, 36), 3),
    (('Snivy', 'Servine', 'Serperior'), (495, 496, 497), (17, 36), 1),
    (('Tepig', 'Pignite', 'Emboar'), (498, 499, 500), (17, 36), 2),
    (('Chespin', 'Quilladin', 'Chesnaught'), (650, 651, 652), (16, 36), 1),
    (('Fennekin', 'Braixen', 'Delphox'), (653, 654, 655), (16, 36), 2),
    (('Froakie', 'Frogadier', 'Greninja'), (656, 657, 658), (16, 36), 3),
    (('Litten', 'Torracat', 'Incineroar'), (725, 726, 727), (17, 34), 2),
]
# own Abilities of the final forms (Arena indices: 15 Intimidate, 18 Shell Armor, 27 Iron Fist, 31 Reckless,
# 70 Strong Jaw, 3 Torrent = Greninja changed from 79 Protean to avoid colliding with Primordial Sea in v4.1.2)
FINAL_AB = {'Feraligatr': 70, 'Torterra': 18, 'Infernape': 27, 'Emboar': 31, 'Greninja': 3, 'Incineroar': 15}
# Pokemon World's unit scale for the model (None there -> 1.2)
SCALE = {158: 0.7, 159: 1.4, 160: 1.5, 258: 1.5, 260: 1.2, 387: 1.5, 388: 3.0, 389: 5.0, 390: 2.8, 391: 0.55,
         392: 2.8, 393: 0.3, 394: 0.5, 395: 0.95, 495: 1.2, 497: 1.3, 498: 1.8, 499: 1.7, 500: 1.5, 652: 1.65,
         653: 1.2, 654: 1.25, 655: 1.2, 656: 0.4, 657: 0.55, 658: 1.25, 725: 0.8, 727: 1.6}
# object data template per first type and stage (Squirtle / Torchic / Treecko lines)
TEMPLATE = {'water': ('E004', 'E009', 'E000'), 'fire': ('EN00', 'EN01', 'EN02'), 'grass': ('EN03', 'EN04', 'EN05')}
PICK_GROUP = {'water': 'Water', 'fire': 'Fire', 'grass': 'Grass'}
T = {'bug': 0, 'dark': 1, 'dragon': 2, 'electric': 3, 'fairy': 4, 'fighting': 5, 'fire': 6, 'flying': 7, 'ghost': 8,
     'grass': 9, 'ground': 10, 'ice': 11, 'normal': 12, 'poison': 13, 'psychic': 14, 'rock': 15, 'steel': 16,
     'water': 17}
TYPE_WORD = {k: k.capitalize() for k in T}
ATTACK_COLOR = {'water': 'ff6390f0', 'fire': 'ffee8130', 'grass': 'ff7ac74c'}
DIG = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def species():
    """[dict(id, name, dex, stage, line, types, stats, ability, moves, tm, evo_to, evo_lv, first)] in LINES order."""
    L = json.load(open(os.path.join(WORK, 'tools', 'learnsets.json'), encoding='utf-8'))['species']
    out, k = [], 0
    for names, dexes, levels, ab in LINES:
        ids = ['EP' + DIG[(k + j) // 36] + DIG[(k + j) % 36] for j in range(3)]
        for j, (name, dex) in enumerate(zip(names, dexes)):
            s = L.get(name.lower())
            if s is None:
                raise SystemExit('starters: %s not in tools/learnsets.json (run analysis/fetch_pokeapi.py)' % name)
            out.append(dict(id=ids[j], name=name, dex=dex, stage=j, line=ids, types=s['types'], stats=s['stats'],
                            ability=FINAL_AB.get(name, ab), moves=s['moves'], tm=s['tm'], first=ids[0],
                            evo_to=ids[j + 1] if j < 2 else None, evo_lv=levels[j] if j < 2 else None))
        k += 3
    return out


def stat_values(sp):
    hp, atk, de, spa, spd, spe = sp['stats']
    return dict(hp=40 * hp, str=atk, agi=spe, int=spa, de=de, spd=spd, main=1 if atk >= spa else 3,
                cd=(2000, 1900, 1800)[sp['stage']], armor=int(round(0.6 * de)))


def type_label(sp):
    return '&'.join(TYPE_WORD[t] for t in sp['types']) + ' Pokemon'


def description(sp, by_id):
    first = sp['types'][0]
    s = '|cffffcc00%s|r (%s).' % (sp['name'], type_label(sp))
    if sp['evo_to']:
        s += ' Evolves into |cffffcc00%s|r at lv %d.' % (by_id[sp['evo_to']]['name'], sp['evo_lv'])
    s += ' New in v3.4.16 (Gen %s starter).|n|c%sBasic attack: %s|r' % (
        {158: 2, 258: 3, 387: 4, 390: 4, 393: 4, 495: 5, 498: 5, 650: 6, 653: 6, 656: 6, 725: 7}.get(
            next(x for x in by_id.values() if x['id'] == sp['first'])['dex'], '?'),
        ATTACK_COLOR[first], TYPE_WORD[first])
    return s


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace("'", '').replace('.', '')).strip('-')


def data_lines(script, status_slugs):
    """JASS lines (run in Fx_Data, after Mv_Learn / Evo / Rand data): stats, types, Ability, moves, evolutions,
    random pick, gym pool. status_slugs: {slug: move index} of the status moves."""
    moves = {}
    for i, label in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        m = re.match(r'(.*) \((\w+), power \d+\)', label)
        if m:
            moves.setdefault(slug(m.group(1)), int(i))
    moves.update(status_slugs)
    sps = species()
    lines, n_lv, n_tm = [], 0, 0
    for sp in sps:
        v = stat_values(sp)
        u = sp['id']
        lines += ["    call SaveInteger(Mega_HT, '%s', 80, %d)" % (u, v['hp']),
                  "    call SaveInteger(Mega_HT, '%s', 81, %d)" % (u, v['hp']),
                  "    call SaveInteger(Mega_HT, '%s', 82, %d)" % (u, v['str']),
                  "    call SaveInteger(Mega_HT, '%s', 83, %d)" % (u, v['agi']),
                  "    call SaveInteger(Mega_HT, '%s', 84, %d)" % (u, v['int']),
                  "    call SaveInteger(Mega_HT, '%s', 85, %d)" % (u, v['main']),
                  "    call SaveInteger(Mega_HT, '%s', 86, %d)" % (u, v['cd']),
                  "    call SaveInteger(Fx_HT, '%s', 1, %d)" % (u, v['de']),
                  "    call SaveInteger(Fx_HT, '%s', 2, %d)" % (u, v['spd']),
                  "    call SaveInteger(Ab_HT, '%s', 0, %d)" % (u, sp['ability']),
                  "    call SaveInteger(Ab_HT, '%s', 53, %d)" % (u, T[sp['types'][0]] + 1)]
        if len(sp['types']) > 1:
            lines.append("    call SaveInteger(Ab_HT, '%s', 54, %d)" % (u, T[sp['types'][1]] + 1))
        lv = {}
        for lvl, ms in sp['moves']:
            if ms in moves and ms not in lv:
                lv[ms] = max(1, int(lvl))
        for ms, lvl in sorted(lv.items(), key=lambda kv: kv[1]):
            lines.append("    call Fx_AddLv('%s', %d, %d)" % (u, moves[ms], lvl))
            n_lv += 1
        for ms in sp['tm']:
            if ms in moves and ms not in lv:
                lines.append("    call Fx_AddTm('%s', %d)" % (u, moves[ms]))
                n_tm += 1
        if sp['evo_to']:
            lines += ["    set Evo_From[Evo_N] = '%s'" % u, "    set Evo_To[Evo_N] = '%s'" % sp['evo_to'],
                      '    set Evo_Level[Evo_N] = %d' % sp['evo_lv'], '    set Evo_N = Evo_N + 1']
        if sp['stage'] == 0:
            lines += ["    set Rand_Type[Rand_N] = '%s'" % u, '    set Rand_N = Rand_N + 1',
                      "    set Gym_Pool[Gym_PoolN] = '%s'" % u, '    set Gym_PoolN = Gym_PoolN + 1']
    return lines, (n_lv, n_tm)


def patch_picker(s):
    """Add the first forms to the type groups of the picker (static data block of the base script)."""
    a = s.index('    set Pick_N = ')
    b = s.index('endfunction', a)
    blk = s[a:b]
    types = dict((int(i), v) for i, v in re.findall(r"set Pick_Type\[(\d+)\] = '(\w{4})'", blk))
    names = dict((int(i), v) for i, v in re.findall(r'set Pick_Name\[(\d+)\] = "([^"]*)"', blk))
    gname = dict((int(i), v) for i, v in re.findall(r'set Pick_TName\[(\d+)\] = "([^"]*)"', blk))
    gfirst = dict((int(i), int(v)) for i, v in re.findall(r'set Pick_TFirst\[(\d+)\] = (\d+)', blk))
    gcount = dict((int(i), int(v)) for i, v in re.findall(r'set Pick_TCount\[(\d+)\] = (\d+)', blk))
    groups = []
    for g in sorted(gname):
        groups.append([gname[g], [(types[i], names[i]) for i in range(gfirst[g], gfirst[g] + gcount[g])]])
    if sum(len(x[1]) for x in groups) != len(types):
        raise SystemExit('starters: picker groups do not cover the list')
    for sp in species():
        if sp['stage'] != 0:
            continue
        want = PICK_GROUP[sp['types'][0]]
        grp = next(x for x in groups if x[0] == want)
        if any(t == sp['id'] for t, _n in grp[1]):
            raise SystemExit('starters: %s already in the picker' % sp['id'])
        grp[1].append((sp['id'], sp['name']))
    out, k = ['    set Pick_N = %d' % sum(len(x[1]) for x in groups)], 0
    for _g, members in groups:
        for t, n in members:
            out += ["    set Pick_Type[%d] = '%s'" % (k, t), '    set Pick_Name[%d] = "%s"' % (k, n)]
            k += 1
    out.append('    set Pick_TN = %d' % len(groups))
    k = 0
    for g, (gn, members) in enumerate(groups):
        out += ['    set Pick_TName[%d] = "%s"' % (g, gn), '    set Pick_TFirst[%d] = %d' % (g, k),
                '    set Pick_TCount[%d] = %d' % (g, len(members))]
        k += len(members)
    return s[:a] + '\n'.join(out) + '\n' + s[b:]


def unit_objects(w3u, objdata):
    """Add the 33 hero unit types to w3u (copies of the template heroes with the new identity and stats)."""
    have = {o.new for o in w3u.custom}
    sps = species()
    by_id = {sp['id']: sp for sp in sps}
    for sp in sps:
        if sp['id'] in have:
            raise SystemExit('starters: unit id %s already used' % sp['id'])
        tmpl = TEMPLATE[sp['types'][0]][sp['stage']]
        src = next(o for o in w3u.custom if o.new == tmpl)
        v = stat_values(sp)
        d = '%03d' % sp['dex']
        icon = 'ReplaceableTextures\\CommandButtons\\BTN_%s.blp' % d
        new = {'umdl': 'PkFx\\Starter\\%s.mdx' % d, 'uico': icon, 'ussi': icon, 'upro': sp['name'],
               'unam': type_label(sp), 'utub': description(sp, by_id), 'uawt': 'Revive %s' % sp['name'],
               'utip': 'Summon %s' % sp['name'], 'utpr': 'Revive %s' % sp['name'], 'uhpm': v['hp'],
               'ustr': v['str'], 'uagi': v['agi'], 'uint': v['int'], 'ustp': round(v['str'] / 50.0, 2),
               'uagp': round(v['agi'] / 50.0, 2), 'uinp': round(v['int'] / 50.0, 2),
               'upra': 'STR' if v['main'] == 1 else 'INT', 'udef': v['armor'],
               'usca': float(SCALE.get(sp['dex'], 1.2))}
        mods = []
        for x in src.mods:
            val = new.pop(x.field, x.value) if x.field in new else x.value
            mods.append(objdata.Mod(x.field, x.type, val, x.level, x.data, x.end))
        kinds = {'uhpm': 0, 'ustr': 0, 'uagi': 0, 'uint': 0, 'udef': 0, 'ustp': 2, 'uagp': 2, 'uinp': 2, 'usca': 1}
        for f, val in new.items():  # fields the template does not set
            mods.append(objdata.Mod(f, kinds.get(f, 3), val))
        w3u.custom.append(objdata.Obj(src.orig, sp['id'], mods))
    return len(sps)


# ---- v3.4.16: the starters as wild Pokemon too, each dropping its Soul (walk into the centre circle to become it).
# Like Treecko / Grovyle / Sceptile (nX5B / nX26 / nX4B): powers 1-2 / 3-5 / 6-10, Mega_HT on the wild type 8 Soul,
# 30 kit type + 1, 39 = 1 (stats from the power table), 45 next form, 47 / 48 powers it appears at.
WILD_TMPL = ('nX5B', 'nX26', 'nX4B')
WILD_POW = ((1, 2), (3, 5), (6, 10))
SOUL_TMPL = 'IU5B'


def wild_id(k):
    return 'nZ' + DIG[k // 36] + DIG[k % 36]


def soul_id(k):
    return 'IZ' + DIG[k // 36] + DIG[k % 36]


def patch_wild(s):
    """Append the 33 wild types, their pool entries and Souls to the static wild data of the base script."""
    mt = re.search(r'    set Wild_TypeN = (\d+)\n    set Wild_PoolN = (\d+)\n    set Soul_N = (\d+)\n', s)
    if not mt or s.count(mt.group(0)) != 1:
        raise SystemExit('starters: Wild_TypeN / Wild_PoolN / Soul_N block not found once')
    nt, npool, nsoul = (int(x) for x in mt.groups())
    lines = []
    for k, sp in enumerate(species()):
        w, so = wild_id(k), soul_id(k)
        lines += ["    set Wild_Type[%d] = '%s'  // v3.4.16 %s" % (nt, w, sp['name']),
                  "    call SaveInteger(Mega_HT, '%s', 8, '%s')" % (w, so),
                  "    call SaveInteger(Mega_HT, '%s', 30, %d)" % (w, T[sp['types'][0]] + 1),
                  "    call SaveInteger(Mega_HT, '%s', 39, 1)" % w,
                  "    set Soul_Item[%d] = '%s'" % (nsoul, so), "    set Soul_Hero[%d] = '%s'" % (nsoul, sp['id'])]
        nt += 1
        nsoul += 1
        lo, hi = WILD_POW[sp['stage']]
        for pw in range(lo, hi + 1):
            lines += ["    set Wild_Pool[%d] = '%s'" % (npool, w), '    set Wild_PoolPow[%d] = %d' % (npool, pw)]
            npool += 1
    new = '\n'.join(lines) + '\n    set Wild_TypeN = %d\n    set Wild_PoolN = %d\n    set Soul_N = %d\n' % (nt, npool, nsoul)
    return s.replace(mt.group(0), new)


def wild_data_lines():
    """Per wild type: powers, next form, Ability, types, Def / Sp. Def; per hero: gym evolution (Ab_HT 699..701)."""
    sps = species()
    idx = {sp['id']: k for k, sp in enumerate(sps)}
    out = []
    for k, sp in enumerate(sps):
        w = wild_id(k)
        v = stat_values(sp)
        lo, hi = WILD_POW[sp['stage']]
        out += ["    call SaveInteger(Mega_HT, '%s', 47, %d)" % (w, lo), "    call SaveInteger(Mega_HT, '%s', 48, %d)" % (w, hi),
                "    call SaveInteger(Ab_HT, '%s', 0, %d)" % (w, sp['ability']),
                "    call SaveInteger(Ab_HT, '%s', 53, %d)" % (w, T[sp['types'][0]] + 1),
                "    call SaveInteger(Fx_HT, '%s', 1, %d)" % (w, v['de']), "    call SaveInteger(Fx_HT, '%s', 2, %d)" % (w, v['spd'])]
        if len(sp['types']) > 1:
            out.append("    call SaveInteger(Ab_HT, '%s', 54, %d)" % (w, T[sp['types'][1]] + 1))
        if sp['evo_to']:
            out += ["    call SaveInteger(Mega_HT, '%s', 45, '%s')" % (w, wild_id(idx[sp['evo_to']])),
                    "    call SaveInteger(Ab_HT, '%s', 699, 1)" % sp['id'],
                    "    call SaveInteger(Ab_HT, '%s', 700, '%s')" % (sp['id'], sp['evo_to']),
                    "    call SaveInteger(Ab_HT, '%s', 701, %d)" % (sp['id'], sp['evo_lv'])]
    return out


def wild_objects(w3u, objdata, items, func, set_keys, copy_section):
    """Wild unit types nZ.. (copies of the Treecko line's wild types) and Soul items IZ... Returns func."""
    by = {o.new: o for o in w3u.custom}
    for k, sp in enumerate(species()):
        w, so = wild_id(k), soul_id(k)
        if w in by or items.find(so) is not None:
            raise SystemExit('starters: id %s / %s already used' % (w, so))
        src = by[WILD_TMPL[sp['stage']]]
        d = '%03d' % sp['dex']
        icon = 'ReplaceableTextures\\CommandButtons\\BTN_%s.blp' % d
        new = {'umdl': 'PkFx\\Starter\\%s.mdx' % d, 'unam': sp['name'], 'uico': icon,
               'usca': float(SCALE.get(sp['dex'], 1.2))}
        mods = [objdata.Mod(x.field, x.type, new.pop(x.field, x.value), x.level, x.data, x.end) for x in src.mods]
        for f, val in new.items():
            mods.append(objdata.Mod(f, 1 if f == 'usca' else 3, val))
        w3u.custom.append(objdata.Obj(src.orig, w, mods))
        row = dict(items.find(SOUL_TMPL))
        row[1] = '"%s"' % so
        items.rows.append(row)
        func = copy_section(func, SOUL_TMPL, so)
        func = set_keys(func, so, [('Name', '%s Soul' % sp['name']), ('Tip', '%s Soul' % sp['name']),
                                   ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to'
                                               ' become |cffffcc00%s|r.' % sp['name']),
                                   ('Description', 'Soul of a wild %s.' % sp['name']), ('Art', icon)])
    return func


def _fix_shiny_paths(data, has):
    """Texture paths of the model that Pokemon World lacks ('495SSA.blp' shiny skins) -> the normal skin."""
    import mdxinfo
    import struct
    out = bytearray(data)
    p = 4
    while p + 8 <= len(out):
        tag = bytes(out[p:p + 4])
        n = struct.unpack_from('<I', out, p + 4)[0]
        if tag == b'TEXS':
            for k in range(n // 268):
                at = p + 8 + k * 268 + 4
                path = bytes(out[at:at + 260]).split(b'\0')[0].decode('latin-1')
                if path and not has(path) and not path.lower().startswith(('textures', 'replaceable')):
                    alt = re.sub(r'(?i)ss(?=[a-z]?\.blp$)', '', path)
                    if alt != path and has(alt):
                        out[at:at + 260] = alt.encode('latin-1').ljust(260, b'\0')
        p += 8 + n
    mdxinfo.info(bytes(out))  # still parses
    return bytes(out)


def files():
    """{path in the Arena map: bytes}: models (PkFx\\Starter\\<dex>.mdx), their textures, icons."""
    import mpq
    import mdxinfo

    class PW(mpq.MPQ):
        def _find_header(self):
            return 1024

    arc = PW(PW_MAP)
    game = ('textures\\', 'replaceabletextures\\', 'units\\', 'abilities\\', 'environment\\', 'objects\\', 'ui\\')
    out = {}
    for sp in species():
        d = '%03d' % sp['dex']
        data = _fix_shiny_paths(arc.read('Unit\\%s.mdx' % d), arc.has)
        out['PkFx\\Starter\\%s.mdx' % d] = data
        for t in mdxinfo.info(data)['textures']:
            if t and not t.lower().startswith(game) and arc.has(t):
                out[t] = arc.read(t)
        for icon in ('ReplaceableTextures\\CommandButtons\\BTN_%s.blp' % d,
                     'ReplaceableTextures\\CommandButtonsDisabled\\DISBTN_%s.blp' % d):
            if arc.has(icon):
                out[icon] = arc.read(icon)
    return out
