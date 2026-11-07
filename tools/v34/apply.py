"""Assemble the v3.4 map script.

    v34/war3map_v333.j  (the script of "Pokemon Arena v3.3.3.w3x", the last built map; its source is lost)
  + tools/v34/jass/*.j  (new / replaced JASS)
  + data generated here (Ability table, type chart, unit and move types, gym pool)
  = v34/war3map.j

Run from the work folder:  python -I tools/v34/apply.py [--map "../Pokemon Arena v3.3.3.w3x"]
The base map is read only for its unit data (war3map.w3u). Nothing is written into any map here (see build_v34.py).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WORK = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import objdata  # noqa: E402
import abilities  # noqa: E402
import mega_look  # noqa: E402
import content  # noqa: E402

JASS = os.path.join(HERE, 'jass')
BASE_SCRIPT = os.path.join(WORK, 'v34', 'war3map_v333.j')
OUT_SCRIPT = os.path.join(WORK, 'v34', 'war3map.j')
BASE_MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.3.3.w3x')
VERSION_FILE = os.path.join(HERE, 'version.txt')

TYPES = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice',
         'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']  # kit order (kit k = TYPES[k - 1])
TI = {t: i for i, t in enumerate(TYPES)}

# attacker -> {defender: multiplier} (games since gen 6)
CHART = {
    'Normal': {'Rock': .5, 'Ghost': 0, 'Steel': .5},
    'Fire': {'Fire': .5, 'Water': .5, 'Grass': 2, 'Ice': 2, 'Bug': 2, 'Rock': .5, 'Dragon': .5, 'Steel': 2},
    'Water': {'Fire': 2, 'Water': .5, 'Grass': .5, 'Ground': 2, 'Rock': 2, 'Dragon': .5},
    'Electric': {'Water': 2, 'Electric': .5, 'Grass': .5, 'Ground': 0, 'Flying': 2, 'Dragon': .5},
    'Grass': {'Fire': .5, 'Water': 2, 'Grass': .5, 'Poison': .5, 'Ground': 2, 'Flying': .5, 'Bug': .5, 'Rock': 2,
              'Dragon': .5, 'Steel': .5},
    'Ice': {'Fire': .5, 'Water': .5, 'Grass': 2, 'Ice': .5, 'Ground': 2, 'Flying': 2, 'Dragon': 2, 'Steel': .5},
    'Fighting': {'Normal': 2, 'Ice': 2, 'Poison': .5, 'Flying': .5, 'Psychic': .5, 'Bug': .5, 'Rock': 2, 'Ghost': 0,
                 'Dark': 2, 'Steel': 2, 'Fairy': .5},
    'Poison': {'Grass': 2, 'Poison': .5, 'Ground': .5, 'Rock': .5, 'Ghost': .5, 'Steel': 0, 'Fairy': 2},
    'Ground': {'Fire': 2, 'Electric': 2, 'Grass': .5, 'Poison': 2, 'Flying': 0, 'Bug': .5, 'Rock': 2, 'Steel': 2},
    'Flying': {'Electric': .5, 'Grass': 2, 'Fighting': 2, 'Bug': 2, 'Rock': .5, 'Steel': .5},
    'Psychic': {'Fighting': 2, 'Poison': 2, 'Psychic': .5, 'Dark': 0, 'Steel': .5},
    'Bug': {'Fire': .5, 'Grass': 2, 'Fighting': .5, 'Poison': .5, 'Flying': .5, 'Psychic': 2, 'Ghost': .5, 'Dark': 2,
            'Steel': .5, 'Fairy': .5},
    'Rock': {'Fire': 2, 'Ice': 2, 'Fighting': .5, 'Ground': .5, 'Flying': 2, 'Bug': 2, 'Steel': .5},
    'Ghost': {'Normal': 0, 'Psychic': 2, 'Ghost': 2, 'Dark': .5},
    'Dragon': {'Dragon': 2, 'Steel': .5, 'Fairy': 0},
    'Dark': {'Fighting': .5, 'Psychic': 2, 'Ghost': 2, 'Dark': .5, 'Fairy': .5},
    'Steel': {'Fire': .5, 'Water': .5, 'Electric': .5, 'Ice': 2, 'Rock': 2, 'Steel': .5, 'Fairy': 2},
    'Fairy': {'Fire': .5, 'Fighting': 2, 'Poison': .5, 'Dragon': 2, 'Dark': 2, 'Steel': .5},
}

# hero type words that are not types
SPECIAL_WORDS = {'God': ['Normal'], 'Time': ['Steel', 'Dragon'], 'Space': ['Water', 'Dragon']}

MEGA_TYPES = {
    'Mega Venusaur': 'Grass Poison', 'Mega Charizard X': 'Fire Dragon', 'Mega Charizard Y': 'Fire Flying',
    'Mega Blastoise': 'Water', 'Mega Beedrill': 'Bug Poison', 'Mega Pidgeot': 'Normal Flying',
    'Mega Alakazam': 'Psychic', 'Mega Gengar': 'Ghost Poison', 'Mega Kangaskhan': 'Normal',
    'Mega Pinsir': 'Bug Flying', 'Mega Gyarados': 'Water Dark', 'Mega Steelix': 'Steel Ground',
    'Mega Scizor': 'Bug Steel', 'Mega Mewtwo X': 'Psychic Fighting', 'Mega Mewtwo Y': 'Psychic',
    'Mega Rayquaza': 'Dragon Flying', 'Mega Blaziken': 'Fire Fighting', 'Mega Sceptile': 'Grass Dragon',
    'Mega Tyranitar': 'Rock Dark', 'Mega Gardevoir': 'Psychic Fairy', 'Mega Gallade': 'Psychic Fighting',
    'Mega Salamence': 'Dragon Flying', 'Mega Metagross': 'Steel Psychic', 'Mega Lucario': 'Fighting Steel',
    'Mega Absol': 'Dark',
}

# gyms use first forms of the -random pool except the legends
LEGENDS = {'Articuno', 'Zapdos', 'Moltres', 'Mewtwo', 'Mew', 'Raikou', 'Entei', 'Suicune', 'Lugia', 'Ho-Oh', 'Celebi',
           'Kyogre', 'Groudon', 'Rayquaza', 'Jirachi', 'Deoxys', 'Dialga', 'Palkia', 'Giratina', 'Darkrai', 'Arceus',
           'Regirock', 'Regigigas', 'Buzzwole', 'Kingambit', 'Latias & Latios'}

# v1.8 Pokemon that evolve by stone / trade / Soul (no level in the map): the level a gym uses for them
# v3.4 new Pokemon (content.py): the real level evolutions of the map, read like the map's own Evo_* data
V34_EVOLUTIONS = [('Bayleef', 'Meganium', 32), ('Porygon', 'Porygon2', 50)]
MANUAL_EVOLUTIONS = [
    ('Pikachu', 'Raichu', 36), ('Vulpix', 'Ninetales', 36), ('Growlithe', 'Arcanine', 36), ('Staryu', 'Starmie', 36),
    ('Exeggcute', 'Exeggutor', 36), ('Shellder', 'Cloyster', 36), ('Onix', 'Steelix', 40), ('Scyther', 'Scizor', 40),
    ('Nidorino', 'Nidoking', 36), ('Weepinbell', 'Victreebel', 45), ('Eevee', 'Vaporeon', 36), ('Eevee', 'Jolteon', 36),
    ('Eevee', 'Flareon', 36), ('Alolan-Sandshrew', 'Alolan-Sandslash', 36), ('Alolan-Geodude', 'Alolan-Graveler', 25),
    ('Alolan-Graveler', 'Alolan-Golem', 40),
]

# wild creeps: v3.2.15 HP table by power (wild_data.POWER_STATS: level, HP)
POWER_LV_HP = {1: (3, 245), 2: (7, 630), 3: (12, 1050), 4: (18, 1540), 5: (24, 2100), 6: (32, 2800), 7: (40, 3850),
               8: (50, 5250), 9: (62, 7000), 10: (75, 9100)}


# ------------------------------------------------------------------ text helpers
def jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def find_function(script, name):
    """(start, end) of 'function NAME takes ... endfunction' (end after the endfunction line)."""
    m = re.search(r'(?m)^function %s takes' % re.escape(name), script)
    if not m:
        raise KeyError('function %s not found' % name)
    e = script.find('\nendfunction', m.start())
    if e < 0:
        raise KeyError('end of %s not found' % name)
    e = script.find('\n', e + 1)
    return m.start(), (e + 1 if e >= 0 else len(script))


def replace_range(script, first, last, text, start_at=None):
    s = find_function(script, first)[0] if start_at is None else script.index(start_at)
    e = find_function(script, last)[1]
    if e <= s:
        raise ValueError('bad range %s..%s' % (first, last))
    return script[:s] + text.rstrip('\n') + '\n' + script[e:]


def replace_once(script, old, new):
    if script.count(old) != 1:
        raise ValueError('expected one %r, found %d' % (old[:80], script.count(old)))
    return script.replace(old, new)


def snippet(name):
    with open(os.path.join(JASS, name), encoding='utf-8') as f:
        return f.read().replace('\r\n', '\n')


def replace_functions(script, text):
    """text holds '//@replace NAME' blocks: each block replaces function NAME (it may define helpers before it)."""
    parts = re.split(r'(?m)^//@replace (\w+)\n', text)
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        s, e = find_function(script, name)
        script = script[:s] + body.rstrip('\n') + '\n' + script[e:]
    return script


# ------------------------------------------------------------------ data from the base map / script
def unit_data(map_path):
    w3u = objdata.ObjFile(mpq.MPQ(map_path).read('war3map.w3u'))
    return {o.id: o for o in w3u.custom}


def hero_types(units):
    """unit id -> [type, type] for the playable Pokemon (unit name 'Fire&Flying Pokemon') and the Megas;
    proper name -> types."""
    by_id, by_name = {}, {}
    for uid, o in units.items():
        nam = o.get('unam') or ''
        pro = (o.get('upro') or '').split(',')[0].strip()
        types = None
        if nam.endswith(' Pokemon') and uid[0].isupper():
            types = []
            for w in nam[:-8].split('&'):
                w = w.strip()
                types += SPECIAL_WORDS.get(w, [w] if w in TI else [])
        elif nam in MEGA_TYPES:
            types = MEGA_TYPES[nam].split()
        if types:
            by_id[uid] = types[:2]
            if pro and nam.endswith(' Pokemon'):
                by_name.setdefault(pro, types[:2])
    return by_id, by_name


def creep_types(units, by_name, kit_of):
    """non-hero units named after a species ('Wild Zapdos', 'Nidoran_M') -> types; else the kit type (key 30)."""
    out = {}
    fix = {'Aerodactyle': 'Aerodactyl', 'Nidoran_M': 'Nidoran', 'Nidoran_F': 'Nidoran', 'Mr.mime': 'Mr. Mime'}
    for uid, o in units.items():
        if uid[0].isupper():
            continue
        nam = (o.get('unam') or '').strip()
        if nam.startswith('Wild '):
            nam = nam[5:]
        nam = fix.get(nam, nam)
        if nam in by_name:
            out[uid] = by_name[nam]
        elif uid in kit_of:
            out[uid] = [TYPES[kit_of[uid] - 1]]
    out.setdefault('nogl', ['Fighting'])  # Machamp creep of the base game
    return out


def parse_moves(script):
    s, e = find_function(script, 'Mv_InitData')
    body = script[s:e]
    n = int(re.search(r'set Mv_N = (\d+)', body).group(1))
    labels = dict((int(a), b) for a, b in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', body))
    texts = dict((int(a), b) for a, b in re.findall(r'set Mv_Text\[(\d+)\] = "([^"]*)"', body))
    moves = []
    for m in range(n):
        lab, txt = labels.get(m, ''), texts.get(m, '')
        mt = re.search(r'\((\w+), power (\d+)\)', lab)
        ty = mt.group(1) if mt else (re.search(r'\((\w+)', lab).group(1) if re.search(r'\((\w+)', lab) else '')
        pw = int(mt.group(2)) if mt else 0
        phys = 1 if 'Physical move' in txt else 2
        moves.append((m, TI.get(ty, -1), pw, phys, lab))
    return moves


def _norm(name):
    n = re.sub(r'[^a-z0-9]', '', name.lower())
    return 'nidoran' if n in ('nidoranm', 'nidoranf') else n


def hero_names(units):
    """unit id -> proper name, for the playable Pokemon (name 'X Pokemon', id with an uppercase letter)."""
    out = {}
    for uid, o in units.items():
        if uid[0].isupper() and (o.get('unam') or '').endswith(' Pokemon'):
            out[uid] = (o.get('upro') or '').split(',')[0].strip()
    return out


def gym_evolutions(script, units, report):
    """Evolutions for the forms of the gym Pokemon, by species name: the map's Evo_* (mod Pokemon), the level
    triggers of v1.8 (Charmander lv 16 ...) and the PokeAPI chains (tools/evolutions.json) for the stone / trade /
    friendship evolutions, which get level 36 (first stage) or 45 (second stage). -> [(from id, to id, level)]"""
    import json
    names = hero_names(units)
    ids = {}
    for uid in sorted(names, key=lambda u: (u[0] != 'E', u)):
        ids.setdefault(names[uid], []).append(uid)
    by_norm = {_norm(n): n for n in ids}
    edges, prefer = {}, {}

    def add(a, b, lv, to_id=None):
        if a in ids and b in ids and a != b and (a, b) not in edges:
            edges[(a, b)] = lv
            if to_id:
                prefer.setdefault(b, to_id)

    s, e = find_function(script, 'Evo_InitData')
    for _i, a, b, lv in re.findall(r"set Evo_From\[(\d+)\] = '(....)'\n    set Evo_To\[\d+\] = '(....)'\n    set Evo_Level\[\d+\] = (\d+)",
                                   script[s:e]):
        if int(lv) > 1:
            add(names.get(a), names.get(b), int(lv), b)
    for a, b, lv in V34_EVOLUTIONS:
        add(a, b, lv)
    n_map = len(edges)
    conds = {}
    for m in re.finditer(r'(?m)^function (\w+) takes nothing returns boolean\n(.*?)\nendfunction', script, re.S):
        body = m.group(2)
        lv = re.search(r'Get(?:Unit|Hero)Level\(GetLevelingUnit\(\)\)>(=?)(\d+)', body)
        ty = re.findall(r"GetUnitTypeId\(GetLevelingUnit\(\)\)=='(....)'", body)
        if lv and ty:
            conds[m.group(1)] = (ty, int(lv.group(2)) + (0 if lv.group(1) else 1))
    for m in re.finditer(r"if\((\w+)\(\)\)then\n(?:[^\n]*\n){0,4}?call Mega_SafeReplace\(GetTriggerUnit\(\),'(....)'", script):
        if m.group(1) in conds:
            for fr in conds[m.group(1)][0]:
                add(names.get(fr), names.get(m.group(2)), conds[m.group(1)][1], m.group(2))
    n_v18 = len(edges) - n_map
    chains = json.load(open(os.path.join(TOOLS, 'evolutions.json'), encoding='utf-8'))['species']
    incoming = {b for (_a, b) in edges}
    for _sp, info in sorted(chains.items()):
        for step in info.get('chain', []):
            fa, fb, _trig, lv = step[0], step[1], step[2], step[3] if len(step) > 3 else None
            for pre in ('', 'Alolan-'):
                a = by_norm.get(_norm(pre + fa)) if pre else by_norm.get(_norm(fa))
                b = by_norm.get(_norm(pre + fb)) if pre else by_norm.get(_norm(fb))
                if a and b and (a, b) not in edges:
                    level = int(lv) if isinstance(lv, (int, float)) and lv else (45 if a in incoming else 36)
                    add(a, b, level)
    n_api = len(edges) - n_map - n_v18
    for a, b, level in MANUAL_EVOLUTIONS:
        add(a, b, level)
    report.append('gym evolutions: %d from the map data, %d v1.8 triggers, %d PokeAPI, %d by hand'
                  % (n_map, n_v18, n_api, len(edges) - n_map - n_v18 - n_api))
    out = []
    for (a, b), lv in sorted(edges.items()):
        to_id = prefer.get(b, ids[b][0])
        for fid in ids[a]:
            out.append((fid, to_id, lv))
    return out, edges, ids, names


def gym_pool_of(rand, edges, ids, names, report):
    """first form of each evolution line of the -random pool, one per line (variants count as one), no legends"""
    back = {b: a for (a, b) in edges}
    variant = {'Tauros Aqua': 'Tauros', 'Tauros Blaze': 'Tauros', 'Tauros Combat': 'Tauros', 'Mr.mime': 'Mr. Mime'}
    pool, seen = [], set()
    for uid in rand:
        n = names.get(uid)
        if not n:
            continue
        guard = 0
        while n in back and guard < 4:
            n, guard = back[n], guard + 1
        fam = variant.get(n, n)
        if fam in seen or fam in LEGENDS or n in LEGENDS:
            continue
        seen.add(fam)
        pool.append(uid if names.get(uid) == n else ids[n][0])
    report.append('gym pool: %d lines' % len(pool))
    return pool


def kit_orders(map_path, script):
    """[(skill id, order string)] for the 90 kit skills (Wild_KitSkill), read from CampaignAbilityStrings.txt"""
    text = mpq.MPQ(map_path).read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    out = []
    for abil in dict.fromkeys(re.findall(r"set Wild_KitSkill\[\d+\] = '(\w{4})'", script)):
        m = re.search(r'\[%s\]\r?\n((?:[^\[\r\n][^\r\n]*\r?\n?)*)' % abil, text)
        o = re.search(r'(?m)^Order=(\w+)', m.group(1)) if m else None
        if o:
            out.append((abil, o.group(1)))
    return out


def old_ability_links(script):
    s, e = find_function(script, 'Ab_InitData')
    body = script[s:e]
    links = re.findall(r"    call SaveInteger\(Ab_HT, '(....)', 0, (\d+)\)", body)
    megas = re.findall(r'    set Ab_MegaAb\[(\d+)\] = (\d+)', body)
    return [(u, int(n)) for u, n in links], [(int(i), int(n)) for i, n in megas]


# ------------------------------------------------------------------ generated JASS
def gen_globals():
    lines = ['// generated by tools/v34/apply.py']
    for n, const, _name, _t in abilities.ABILITIES:
        lines.append('constant integer AB_%s = %d' % (const, n))
    for i, t in enumerate(TYPES):
        lines.append('constant integer T_%s = %d' % (t.upper(), i))
    return '\n'.join(lines)


def gen_ab_init(links, megas, units, report):
    names = abilities.by_name()
    lines = ['// v3.4 (generated by tools/v34/apply.py from tools/v34/abilities.py): names, tooltips, who has which Ability',
             'function Ab_InitData takes nothing returns nothing',
             '    set Ab_N = %d' % len(abilities.ABILITIES)]
    for n, _c, name, text in abilities.ABILITIES:
        lines.append('    set Ab_Name[%d] = %s' % (n, jstr(name)))
        lines.append('    set Ab_Info[%d] = %s' % (n, jstr(text)))
        lines.append('    call BlzSetAbilityTooltip(Ab_InfoId(%d), %s, 0)' % (n, jstr('Ability: |cffffcc00%s|r' % name)))
        lines.append('    call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), %s, 0)' % (n, jstr(text)))
    have = {u for u, _n in links}
    added = []
    for uid, o in sorted(units.items()):
        pro = (o.get('upro') or '').split(',')[0].strip()
        if uid[0].isupper() and pro in abilities.MISSING and uid not in have:
            links.append((uid, names[abilities.MISSING[pro]]))
            added.append('%s %s -> %s' % (uid, pro, abilities.MISSING[pro]))
    report.append('Abilities added for %d Pokemon: %s' % (len(added), '; '.join(added)))
    for uid, o in sorted(units.items()):
        pro = (o.get('upro') or '').split(',')[0].strip()
        if uid[0].isupper() and pro in abilities.REPLACE:
            links = [(u, names[abilities.REPLACE[pro]] if u == uid else n) for u, n in links]
            report.append('Ability of %s %s -> %s' % (uid, pro, abilities.REPLACE[pro]))
    for uid, n in links:
        lines.append("    call SaveInteger(Ab_HT, '%s', 0, %d)" % (uid, n))
    for i, n in megas:
        lines.append('    set Ab_MegaAb[%d] = %d' % (i, n))
    lines.append('endfunction')
    return '\n'.join(lines)


def gen_ty_init(moves, gym_pool, gym_evo, orders=()):
    lines = ['// v3.4 (generated by tools/v34/apply.py): type names and chart, move types, wild HP by power, gym pool',
             'function Ty_InitData takes nothing returns nothing',
             '    local integer i = 0']
    for i, t in enumerate(TYPES):
        lines.append('    set Ty_Name[%d] = "%s"' % (i, t))
    lines += ['    loop', '        exitwhen i >= 324', '        set Ty_Eff[i] = 1.0', '        set i = i + 1', '    endloop']
    for a, row in CHART.items():
        for d, v in row.items():
            lines.append('    set Ty_Eff[%d] = %s' % (TI[a] * 18 + TI[d], repr(float(v))))
    for m, ty, pw, phys, _lab in moves:
        lines.append('    set Mv_Type[%d] = %d' % (m, ty))
        lines.append('    set Mv_Pow[%d] = %d' % (m, pw))
        lines.append('    set Mv_Phys[%d] = %d' % (m, phys))
    for p, (lv, hp) in POWER_LV_HP.items():
        lines.append('    set Wild_PowHP[%d] = %s' % (p, repr(float(hp))))
        lines.append('    set Wild_PowLv[%d] = %d' % (p, lv))
    lines.append('    set Gym_PoolN = %d' % len(gym_pool))
    for i, uid in enumerate(gym_pool):
        lines.append("    set Gym_Pool[%d] = '%s'" % (i, uid))
    by_from = {}
    for a, b, lv in gym_evo:
        by_from.setdefault(a, []).append((b, lv))
    for a in sorted(by_from):
        lines.append("    call SaveInteger(Ab_HT, '%s', 299, %d)" % (a, len(by_from[a])))
        for k, (b, lv) in enumerate(by_from[a]):
            lines.append("    call SaveInteger(Ab_HT, '%s', %d, '%s')" % (a, 300 + 2 * k, b))
            lines.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (a, 301 + 2 * k, lv))
    for abil, order in orders:  # Ai_Tick: order string of each kit skill (Ab_HT key 58 on the skill)
        lines.append("    call SaveStr(Ab_HT, '%s', 58, %s)" % (abil, jstr(order)))
    lines.append('endfunction')
    return '\n'.join(lines)


def gen_ty_units(types):
    lines = ['// v3.4 (generated): types of every Pokemon unit type, Ab_HT keys 53 / 54 = type + 1',
             'function Ty_InitUnits takes nothing returns nothing']
    for uid in sorted(types):
        ts = types[uid]
        lines.append("    call SaveInteger(Ab_HT, '%s', 53, %d)" % (uid, TI[ts[0]] + 1))
        if len(ts) > 1 and ts[1] != ts[0]:
            lines.append("    call SaveInteger(Ab_HT, '%s', 54, %d)" % (uid, TI[ts[1]] + 1))
    lines.append('endfunction')
    return '\n'.join(lines)


# ------------------------------------------------------------------ assembly
HERO_HP_OLD = ('    set want = R2I(I2R(LoadInteger(Mega_HT, t, 80)) * f + Stat_BonusHP * I2R(tot - nat) - Hero_StrHP * I2R(tot))'
               ' - LoadInteger(Mega_HT, t, 81)\n')
HERO_HP_NEW = HERO_HP_OLD + ('    if LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_THICKFAT then  // v3.4: Thick Fat +10% max HP\n'
                             '        set want = want + R2I(0.1 * I2R(LoadInteger(Mega_HT, t, 80)) * f)\n'
                             '    endif\n')
HERO_CD_OLD = '    set cd = R2I(I2R(LoadInteger(Mega_HT, t, 86)) / pct)\n'
HERO_CD_NEW = ('    // v3.4: x Hero_ASBoost, x the Ability / attack-slow multiplier that Ab_Pulse keeps in Ab_HT key 84\n'
               '    set pct = pct * Hero_ASBoost\n'
               '    if LoadReal(Ab_HT, h, 84) > 0.0 then\n'
               '        set pct = pct * LoadReal(Ab_HT, h, 84)\n'
               '    endif\n' + HERO_CD_OLD)
WILD_HP_OLD = '    call BlzSetUnitMaxHP(u, R2I(I2R(LoadInteger(Mega_HT, h, 20)) * m * hpf))\n'
WILD_HP_NEW = ('    // v3.4: HP = the v3.2.15 table of its power (key 31; else by its own level) x the tier step\n'
               '    set lo = LoadInteger(Mega_HT, h, 31)\n'
               '    if lo < 1 then\n'
               '        set lo = 1\n'
               '        loop\n'
               '            exitwhen lo >= 10 or Wild_PowLv[lo + 1] > own\n'
               '            set lo = lo + 1\n'
               '        endloop\n'
               '    endif\n'
               '    if lo > 10 then\n'
               '        set lo = 10\n'
               '    endif\n'
               '    call BlzSetUnitMaxHP(u, R2I(Wild_PowHP[lo] * gm * hpf))\n')
KILL_HERO_OLD = 'function bS4 takes nothing returns boolean\nif(not GetBooleanAnd('
KILL_HERO_NEW = ('function bS4 takes nothing returns boolean\n'
                 'if GetOwningPlayer(GetDyingUnit()) == Player(PLAYER_NEUTRAL_AGGRESSIVE) then\n'
                 'return false\n'
                 'endif\n'
                 'if(not GetBooleanAnd(')
# v3.4: tell the owner which Ability the Mega form has (the info button at 3,1 was the only sign of the change)
MEGA_MSG_OLD = ('    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, GetPlayerName(p) + "\'s " + LoadStr(Mega_HT, h, 2)'
                ' + " Mega Evolved into |cffff66cc" + Mega_Name[idx] + "|r!")\n')
MEGA_MSG_NEW = MEGA_MSG_OLD + (
    '    if Ab_MegaAb[idx] > 0 then\n'
    '        call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffff66cc" + Mega_Name[idx] + "|r Ability: |cffffcc00"'
    ' + Ab_Name[Ab_MegaAb[idx]] + "|r - " + Ab_Info[Ab_MegaAb[idx]])\n'
    '    endif\n')
ELITE_OLD = ('            call UnitAddAbility(u, Wild_KitSkill[(k - 1) * 5 + j])\n'
             '            set j = j + 1\n'
             '        endloop\n'
             '    endif\n')
ELITE_NEW = ('            call UnitAddAbility(u, Wild_KitSkill[(k - 1) * 5 + j])\n'
             '            set j = j + 1\n'
             '        endloop\n'
             '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\n'
             '    endif\n'
             '    call Wild_EliteMega(u)\n')
LEG_OLD = '    call SaveInteger(Ab_HT, GetHandleId(lg), 0, LoadInteger(Ab_HT, Leg_Type[i], 0))  // v3.3: legends have an Ability\n'
LEG_NEW = LEG_OLD + '    call Ai_GiveKit(lg)  // v3.4: and the 5 skills of their type, cast by Ai_Tick\n'
# v3.4: the 211 new wild species (Mega_HT key 39 on their type) take damage / armor / gold / level from the power of
# their camp (key 31), so one species can appear at several powers
WILD_POWSTATS = ('function Wild_PowStats takes unit u returns nothing\n'
                 '    local integer h = GetHandleId(u)\n'
                 '    local integer powi = LoadInteger(Mega_HT, h, 31)\n'
                 '    if powi > 10 then\n'
                 '        set powi = 10\n'
                 '    endif\n'
                 '    call SaveReal(Mega_HT, h, 37, Wild_PowDmg[powi])\n'
                 '    call SaveReal(Mega_HT, h, 22, Wild_PowArm[powi])\n'
                 '    call SaveInteger(Mega_HT, h, 23, Wild_PowGold[powi])\n'
                 '    call SaveInteger(Mega_HT, h, 26, Wild_PowLv[powi])\n'
                 'endfunction\n')
WILD_APPLY_OLD = ('        if not HaveSavedInteger(Mega_HT, h, 26) then\n'
                  '            call SaveInteger(Mega_HT, h, 26, GetUnitLevel(u))\n'
                  '        endif\n'
                  '    endif\n')
WILD_APPLY_NEW = ('        if not HaveSavedInteger(Mega_HT, h, 26) then\n'
                  '            call SaveInteger(Mega_HT, h, 26, GetUnitLevel(u))\n'
                  '        endif\n'
                  '        if LoadInteger(Mega_HT, GetUnitTypeId(u), 39) > 0 and LoadInteger(Mega_HT, h, 31) > 0 then\n'
                  '            call Wild_PowStats(u)\n'
                  '        endif\n'
                  '    endif\n')
# ---- v3.4 extras: patches of the v3.3.3 script (docs/v3.4/3-item-league-tinh-nang.md)
EARLY_HELPERS = (
    '// v3.4: does u carry an item of type id (early helper: Everstone, Mega Ring)\n'
    'function Itm_Has takes unit u, integer id returns boolean\n'
    '    local integer s = 0\n'
    '    if id == 0 then\n'
    '        return false\n'
    '    endif\n'
    '    loop\n'
    '        exitwhen s >= 6\n'
    '        if GetItemTypeId(UnitItemInSlot(u, s)) == id then\n'
    '            return true\n'
    '        endif\n'
    '        set s = s + 1\n'
    '    endloop\n'
    '    return false\n'
    'endfunction\n\n'
    '// v3.4: is `to` a direct evolution of `from` (gym evolution data: Ab_HT 299 / 300 + 2k on the type)\n'
    'function Mega_IsEvolution takes integer from, integer to returns boolean\n'
    '    local integer k = 0\n'
    '    loop\n'
    '        exitwhen k >= LoadInteger(Ab_HT, from, 299)\n'
    '        if LoadInteger(Ab_HT, from, 300 + 2 * k) == to then\n'
    '            return true\n'
    '        endif\n'
    '        set k = k + 1\n'
    '    endloop\n'
    '    return false\n'
    'endfunction\n\n')
SAFE_OLD = ('    if HaveSavedReal(Mega_HT, h, 9) and Mega_Time - LoadReal(Mega_HT, h, 9) < 10.0 then\n'
            '        return\n'
            '    endif\n')
SAFE_NEW = ('    if LoadInteger(Mega_HT, h, 33) == 1 then\n'
            '        return  // v3.4.1: gym / League Pokemon are never replaced (the gym would lose track of them)\n'
            '    endif\n'
            '    if not Mega_EvoItem and Itm_Has(u, Itm_Everstone) and Mega_IsEvolution(GetUnitTypeId(u), newId) then\n'
            '        return  // v3.4 Everstone: no level evolution (stones and Souls set Mega_EvoItem)\n'
            '    endif\n') + SAFE_OLD
SHINY_OLD = '    set nu = bj_lastReplacedUnit\n    if nu != null then\n'
SHINY_NEW = SHINY_OLD + ('        call SaveInteger(Ab_HT, GetHandleId(nu), 123, LoadInteger(Ab_HT, h, 123))  // v3.4 Shiny stays\n'
                         '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)\n'
                         '        set i = 0  // v3.4.1: a gym / League challenger that evolves keeps its battle\n'
                         '        loop\n'
                         '            exitwhen i > 8\n'
                         '            if Gym_Hero[i] == u then\n'
                         '                set Gym_Hero[i] = nu\n'
                         '            endif\n'
                         '            set i = i + 1\n'
                         '        endloop\n'
                         '        if League_Unit == u then\n'
                         '            set League_Unit = nu\n'
                         '        endif\n')
RING_DUR_OLD = '    call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration)\n'
RING_DUR_NEW = ('    if Itm_Has(u, Itm_MegaRing) then  // v3.4 Mega Ring: 90s\n'
                '        call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration + 30.0)\n'
                '    else\n'
                '        call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration)\n'
                '    endif\n')
RING_CD_OLD = '            call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown)\n'
RING_CD_NEW = ('            if Itm_Has(u, Itm_MegaRing) then  // v3.4 Mega Ring: recharges 30% faster\n'
               '                call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown * 0.7)\n'
               '            else\n'
               '                call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown)\n'
               '            endif\n')
ELITE_MEGA = (
    '// v3.4: an elite of a species that has a Mega is a Mega elite 1 time in 4 (Mega skin, +20% HP and damage,\n'
    '// 5% to drop its Mega Stone). Mega_HT: key 41 on the type = Mega index + 1, key 44 on the unit\n'
    'function Wild_EliteMega takes unit u returns nothing\n'
    '    local integer mi = LoadInteger(Mega_HT, GetUnitTypeId(u), 41) - 1\n'
    '    local real megasc = 0.0\n'
    '    if mi < 0 or mi >= Mega_N or GetRandomReal(0.0, 1.0) >= Wild_MegaChance then\n'
    '        return\n'
    '    endif\n'
    '    call SaveInteger(Mega_HT, GetHandleId(u), 44, mi + 1)\n'
    '    call BlzSetUnitSkin(u, Mega_Skin[mi])\n'
    '    set megasc = Wild_EliteScale * Mega_Scale[mi] / RMaxBJ(Mega_BaseScale[mi], 0.1)\n'
    '    call SetUnitScale(u, megasc, megasc, megasc)\n'
    '    call SetUnitVertexColor(u, Mega_R[mi], Mega_G[mi], Mega_B[mi], 255)\n'
    '    call BlzSetUnitName(u, Mega_Name[mi])\n'
    '    call Wild_Scale(u)\n'
    'endfunction\n\n')
SCALE_OLD = ('    if LoadInteger(Mega_HT, h, 29) == 1 then\n'
             '        set hpf = Wild_EliteHP\n'
             '        set dmf = Wild_EliteDmg\n'
             '        set goldf = Wild_EliteGold\n'
             '        set armf = Wild_EliteArmor\n'
             '    endif\n')
SCALE_NEW = SCALE_OLD + ('    if LoadInteger(Mega_HT, h, 44) > 0 then  // v3.4 Mega elite\n'
                         '        set hpf = hpf * 1.2\n'
                         '        set dmf = dmf * 1.2\n'
                         '    endif\n')
DROP_OLD = '        // v3.3.3: wild creeps no longer drop Mega Stones (only from the Mega Shops)\n'
DROP_NEW = ('        if LoadInteger(Mega_HT, h, 44) > 0 and GetRandomReal(0.0, 100.0) < 5.0 then  // v3.4 Mega elite\n'
            '            call CreateItem(Mega_Stone[LoadInteger(Mega_HT, h, 44) - 1], GetUnitX(u), GetUnitY(u))\n'
            '            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff66ccA Mega elite dropped its Mega Stone!|r")\n'
            '        endif\n') + DROP_OLD
NEXT_FORM = (
    '// v3.4: what a camp becomes when the tier goes up: its own next form once that form\'s power is reached\n'
    '// (Mega_HT on the type: 45 next form, 47 / 48 the powers it appears at), the same species while still in range,\n'
    '// else a random species of the power as before\n'
    'function Wild_NextForm takes integer t, integer pow returns integer\n'
    '    local integer cur = t\n'
    '    local integer nt = LoadInteger(Mega_HT, t, 45)\n'
    '    local integer guard = 0\n'
    '    loop\n'
    '        exitwhen nt == 0 or LoadInteger(Mega_HT, nt, 47) > pow or guard >= 3\n'
    '        set cur = nt\n'
    '        set nt = LoadInteger(Mega_HT, cur, 45)\n'
    '        set guard = guard + 1\n'
    '    endloop\n'
    '    if cur != t then\n'
    '        return cur\n'
    '    endif\n'
    '    if LoadInteger(Mega_HT, t, 48) >= pow then\n'
    '        return t\n'
    '    endif\n'
    '    return Wild_PickType(pow)\n'
    'endfunction\n\n')
UPG_OLD = '                    set Wild_UpT[c] = Wild_PickType(pow)\n'
UPG_NEW = '                    set Wild_UpT[c] = Wild_NextForm(GetUnitTypeId(u), pow)\n'
LIMIT_OLD = '    if k == 1 then\n        set lim = Item_MaxBadges\n    endif\n'
LIMIT_NEW = LIMIT_OLD + '    if k == 3 then  // v3.4 battle items\n        set lim = 3\n    endif\n'
LIMIT_MSG_OLD = ('        if k == 1 then\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most " + I2S(lim) + " gym badges can be carried.|r")\n'
                 '        else\n')
LIMIT_MSG_NEW = ('        if k == 1 then\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most " + I2S(lim) + " gym badges can be carried.|r")\n'
                 '        elseif k == 3 then\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most 3 battle items can be held.|r")\n'
                 '        else\n')
EVO_ITEM_OLD = '            call Mega_SafeReplace(u, Evo_ItemTo[i], bj_UNIT_STATE_METHOD_RELATIVE)\n'
EVO_ITEM_NEW = ('            set Mega_EvoItem = true\n' + EVO_ITEM_OLD + '            set Mega_EvoItem = false\n')
SOUL_OLD = '            call Mega_SafeReplace(u, Soul_Hero[i], bj_UNIT_STATE_METHOD_RELATIVE)\n'
SOUL_NEW = ('            set Mega_EvoItem = true\n' + SOUL_OLD + '            set Mega_EvoItem = false\n'
            '            if bj_lastReplacedUnit != null then  // v3.4: a Soul rolls Shiny anew\n'
            '                call RemoveSavedInteger(Ab_HT, GetHandleId(bj_lastReplacedUnit), 124)\n'
            '                call SaveInteger(Ab_HT, GetHandleId(bj_lastReplacedUnit), 123, 0)\n'
            '            endif\n')
WIRING = ('    call TimerStart(CreateTimer(), 1.0, true, function League_Tick)\n'
          '    call TimerStart(CreateTimer(), 300.0, true, function Wth_Tick)\n'
          '    set t = CreateTrigger()\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)\n'
          '    call TriggerAddCondition(t, Condition(function League_OnDeath))\n'
          '    set t = CreateTrigger()\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnKill))\n'
          '    set t = CreateTrigger()\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_PICKUP_ITEM)\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnPickup))\n'
          '    set t = CreateTrigger()\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_USE_ITEM)\n'
          '    call TriggerAddAction(t, function Ext_OnUseItem)\n'
          '    set t = CreateTrigger()\n'
          '    set i = 0\n'
          '    loop\n'
          '        exitwhen i >= 12\n'
          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-league", true)\n'
          '        set i = i + 1\n'
          '    endloop\n'
          '    call TriggerAddAction(t, function League_OnChat)\n'
          '    set t = CreateTrigger()\n'
          '    set i = 0\n'
          '    loop\n'
          '        exitwhen i >= 12\n'
          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gym", true)\n'
          '        set i = i + 1\n'
          '    endloop\n'
          '    call TriggerAddAction(t, function Gym_OnChat)\n')
# v3.4.2: type items for all 18 types (Soft Sand was sold but not registered as Ground; Fairy had no item)
TYPE_INIT_OLD = '    set Type_N = 16\n'
TYPE_INIT_NEW = ('    set Type_N = 18\n'
                 "    set Type_Item[16] = 'I013'\n"
                 '    set Type_Word[16] = "Ground"\n'
                 '    set Type_Cost[16] = 3000\n'
                 "    set Type_Item[17] = 'ITFY'\n"
                 '    set Type_Word[17] = "Fairy"\n'
                 '    set Type_Cost[17] = 3000\n')
LEGTELE_OLD = '        call SetUnitPosition(b, -9600.0, -2209.0)\n'
LEGTELE_NEW = '        call SetUnitPosition(b, League_LX, League_LY)  // v3.4.2: Darkrai\'s room is the Pokemon League\n'
TYPE_SELL_OLD = '            if not Type_Has(GetUnitName(b), Type_Word[i]) then\n'
TYPE_SELL_NEW = ('            if not Type_Has(GetUnitName(b), Type_Word[i]) and LoadInteger(Mega_HT, GetUnitTypeId(b), 92) != id then'
                 '  // v3.4.2: unless it evolves with it\n')
GYM_HEADER = '// ---------------------------------------------------------------------------------------------\n// Gym teams of 6 (v3.3)'
FX_HEADER = '// ---- timed effects: kind 1 damage over time'


def assemble(base_script, units, version, orders=(), extra=None):
    report = []
    script = base_script.replace('\r\n', '\n')
    kit_of = dict((u, int(k)) for u, k in re.findall(r"call SaveInteger\(Mega_HT, '(....)', 30, (\d+)\)", script))
    by_id, by_name = hero_types(units)
    types = dict(by_id)
    types.update(creep_types(units, by_name, kit_of))
    moves = parse_moves(script)
    links, megas = old_ability_links(script)
    if extra is not None:
        links += extra.links
        megas += extra.megas
    rand = re.findall(r"set Rand_Type\[\d+\] = '(....)'", script)
    gym_evo, edges, ids, names = gym_evolutions(script, units, report)
    gym_pool = [u for u in gym_pool_of(rand, edges, ids, names, report) if u in types]
    report.append('unit types with types: %d; moves %d (%d without a type)'
                  % (len(types), len(moves), sum(1 for m in moves if m[1] < 0)))

    # globals
    g = snippet('globals.j').replace('//V34_GEN_GLOBALS', gen_globals())
    script = replace_once(script, '//MEGA_GLOBALS_END\n', g.rstrip('\n') + '\n//MEGA_GLOBALS_END\n')
    script = replace_once(script, 'constant integer Ab_FxMax = 64', 'constant integer Ab_FxMax = 256')
    # data: the old Ability table goes, the new data functions come right before Mega_Init
    script = replace_range(script, 'Ab_InitData', 'Ab_InitData', '')
    gen = '\n'.join([gen_ab_init(links, megas, units, report), gen_ty_init(moves, gym_pool, gym_evo, orders), gen_ty_units(types)])
    calls = ''
    if extra is not None:
        cfuncs, calls = extra.jass()
        gen = cfuncs + '\n' + gen
    script = replace_once(script, '\nfunction Mega_Init takes', '\n' + gen + '\n\nfunction Mega_Init takes')
    # hero HP / attack speed, wild HP
    script = replace_once(script, HERO_HP_OLD, HERO_HP_NEW)
    script = replace_once(script, HERO_CD_OLD, HERO_CD_NEW)
    script = replace_once(script, WILD_HP_OLD, WILD_HP_NEW)
    # type chart before the gyms, the gyms, the Abilities
    script = replace_once(script, GYM_HEADER, snippet('types.j') + snippet('ai.j') + snippet('extra.j') + GYM_HEADER)
    script = replace_once(script, ELITE_OLD, ELITE_NEW)
    # v3.4 extras
    script = replace_once(script, '\nfunction Mega_SafeReplace takes', '\n' + EARLY_HELPERS + 'function Mega_SafeReplace takes')
    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
    script = replace_once(script, LEGTELE_OLD, LEGTELE_NEW)
    script = replace_once(script, TYPE_INIT_OLD, TYPE_INIT_NEW)
    for o, n in ((SAFE_OLD, SAFE_NEW), (SHINY_OLD, SHINY_NEW), (RING_DUR_OLD, RING_DUR_NEW), (RING_CD_OLD, RING_CD_NEW),
                 (SCALE_OLD, SCALE_NEW), (DROP_OLD, DROP_NEW), (UPG_OLD, UPG_NEW), (LIMIT_OLD, LIMIT_NEW),
                 (LIMIT_MSG_OLD, LIMIT_MSG_NEW), (EVO_ITEM_OLD, EVO_ITEM_NEW), (SOUL_OLD, SOUL_NEW)):
        script = replace_once(script, o, n)
    script = replace_once(script, '\nfunction Wild_MakeElite takes', '\n' + ELITE_MEGA + 'function Wild_MakeElite takes')
    script = replace_once(script, '\nfunction Wild_Upgrade takes', '\n' + NEXT_FORM + 'function Wild_Upgrade takes')
    # wild: pick by power (index), the new species take their stats from the power of the camp
    script = replace_functions(script, snippet('wild.j'))
    script = replace_once(script, '\nfunction Wild_Apply takes', '\n' + WILD_POWSTATS + '\nfunction Wild_Apply takes')
    script = replace_once(script, WILD_APPLY_OLD, WILD_APPLY_NEW)
    script = replace_once(script, LEG_OLD, LEG_NEW)
    script = replace_range(script, 'Gym_Level', 'Gym_OnDeath', snippet('gym.j'))
    script = replace_functions(script, snippet('ab_head.j'))
    script = replace_functions(script, snippet('moves.j'))  # v3.4.1: one learned move per kind (no shared button)
    script = replace_range(script, 'Ab_FxFind', 'Ab_BeatFx', snippet('ab_core.j'), start_at=FX_HEADER)
    script = replace_range(script, 'Ab_Hero', 'Ab_OnDamaging', snippet('ab_tick.j'))
    script = replace_once(script, '\nfunction Ab_Hero takes', '\n' + snippet('extra_late.j') + '\nfunction Ab_Hero takes')
    # wiring in Mega_Init
    # own threads (ExecuteFunc): Mega_Init already runs ~20k lines of data, keep it away from the op limit
    script = replace_once(script, '    call Ab_InitData()\n',
                          '    call ExecuteFunc("Ab_InitData")\n    call ExecuteFunc("Ty_InitData")\n'
                          '    call ExecuteFunc("Ty_InitUnits")\n')
    script = replace_once(script, '    call Wild_RegisterCamps()\n', calls + '    call ExecuteFunc("Wild_IndexPool")\n'
                          '    call Wild_RegisterCamps()\n    call Ty_InitKits()\n')
    script = replace_once(script, '    call TriggerAddCondition(t, Condition(function Mega_OnCast))\n',
                          '    call TriggerAddCondition(t, Condition(function Mega_OnCast))\n'
                          '    set t = CreateTrigger()\n'
                          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)\n'
                          '    call TriggerAddCondition(t, Condition(function Ty_OnCast))\n')
    script = replace_once(script, '    call TimerStart(CreateTimer(), 3.0, false, function Rand_Hint)\n',
                          '    call TimerStart(CreateTimer(), 3.0, false, function Rand_Hint)\n'
                          '    set t = CreateTrigger()\n'
                          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)\n'
                          '    call TriggerAddCondition(t, Condition(function Ty_OnDeath))\n'
                          '    call TimerStart(CreateTimer(), 1.0, true, function Ai_Tick)\n' + WIRING)
    script = replace_once(script, '    call Base_Init()\n', '    call Base_Init()\n    call Ext_PlaceShops()\n'
                          '    call ExecuteFunc("League_Setup")\n'
                          '    call TimerStart(CreateTimer(), 0.5, true, function League_PortalTick)\n')
    # v1.8 "Kill Hero" (+500 XP, +1 lumber) must not pay for the gym Pokemon (neutral heroes since v3.4)
    script = replace_once(script, KILL_HERO_OLD, KILL_HERO_NEW)
    script = replace_once(script, MEGA_MSG_OLD, MEGA_MSG_NEW)
    # map name
    script = replace_once(script, 'call SetMapName("Pokemon Arena v3.3.3")', 'call SetMapName("Pokemon Arena v%s")' % version)
    return script, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=BASE_MAP)
    args = ap.parse_args()
    version = open(VERSION_FILE).read().strip()
    with open(BASE_SCRIPT, encoding='utf-8') as f:
        base = f.read()
    units = unit_data(args.map)
    extra = content.make(base, units, mpq.MPQ(args.map))
    MEGA_TYPES.update(extra.mega_types)
    units.update(extra.units)
    script, report = assemble(base, units, version, kit_orders(args.map, base), extra)
    report = extra.report + report
    import move_icons  # the table of the move icons build_v34 writes
    rows = move_icons.plan(base)
    move_icons.write_doc(rows, os.path.join(WORK, 'docs', 'v3.4', '4-icon-chieu.md'))
    report.append('move icons: %d by name, %d by type (docs/v3.4/4-icon-chieu.md)'
                  % (sum(1 for r in rows if r[4] == 'name'), sum(1 for r in rows if r[4] != 'name')))
    # the 5 Megas without a Mega model: imported model from mega_models/, else bigger + colour + aura
    script = mega_look.patch_script(script, mpq.MPQ(args.map), units, report)
    with open(OUT_SCRIPT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(script)
    sys.stdout.reconfigure(encoding='utf-8')
    print('\n'.join(report))
    print('wrote %s (%d lines, version %s)' % (OUT_SCRIPT, script.count('\n'), version))


if __name__ == '__main__':
    main()
