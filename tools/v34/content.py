"""v3.4 content from PKLegends v3.2 (docs/v3.4/2-mega-form-quai-hoang.md, approved 2026-11-07):

  - 8 Megas (Slowbro, Sharpedo, Ampharos, Houndoom, Aerodactyl, Manectric, Heracross, Altaria): skin units hM0P..hM0W,
    stones IM0P..IM0W in the Mega Shops, item abilities AM0P..AM0W, Mega data 25..32
  - new Pokemon: Meganium (Bayleef lv 32), Porygon2 (Porygon lv 50), Latias & Latios (random legend nL18, Soul ISL9),
    Darmanitan's Zen Mode skin hZ00
  - 211 wild species (every non-legend playable Pokemon that had no wild creep) nX00.., each with its Soul IU00..

make() is used by apply.py (JASS data + the unit list the generators read) and by build_v34.py (object data, files).
Both get the same ids: everything is ordered by name.
"""
import io
import os
import re
import tempfile

import objdata
from objdata import T_INT, T_REAL, T_STRING

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
PKL_MAP = os.path.join(MAPS, 'PKLegendsv3.2.w3x')
POKEDEX = os.path.join(MAPS, 'Pokedex_files')
BTN = 'ReplaceableTextures\\CommandButtons\\'
DIS = 'ReplaceableTextures\\CommandButtonsDisabled\\'
V34_DIR = 'war3mapImported\\V34\\'
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# key, Mega name, base species, stone, price, STR / AGI / INT points (% change, PokemonDB), PKL unit, types, Ability, shop
MEGAS = [
    ('MegaSlowbro', 'Mega Slowbro', 'Slowbro', 'Slowbronite', 5000, 0, 0, 30, 'h07Z', 'Water Psychic', 'Shell Armor', 1),
    ('MegaSharpedo', 'Mega Sharpedo', 'Sharpedo', 'Sharpedonite', 5000, 17, 11, 16, 'h0DG', 'Water Dark', 'Strong Jaw', 1),
    ('MegaAmpharos', 'Mega Ampharos', 'Ampharos', 'Ampharosite', 6000, 27, -18, 43, 'h0E3', 'Electric Dragon',
     'Mold Breaker', 1),
    ('MegaHoundoom', 'Mega Houndoom', 'Houndoom', 'Houndoominite', 5000, 0, 21, 27, 'h0E5', 'Dark Fire', 'Solar Power', 2),
    ('MegaAerodactyl', 'Mega Aerodactyl', 'Aerodactyl', 'Aerodactylite', 6000, 29, 15, 17, 'h0FH', 'Rock Flying',
     'Tough Claws', 2),
    ('MegaManectric', 'Mega Manectric', 'Manectric', 'Manectite', 5000, 0, 29, 29, 'h0FU', 'Electric', 'Intimidate', 2),
    ('MegaHeracross', 'Mega Heracross', 'Heracross', 'Heracronite', 6000, 48, -12, 0, 'h0LV', 'Bug Fighting',
     'Skill Link', 3),
    ('MegaAltaria', 'Mega Altaria', 'Altaria', 'Altarianite', 6000, 57, 0, 57, 'h0LW', 'Dragon Fairy', 'Pixilate', 3),
]
MEGA_FIRST = 25          # Mega_N of v3.3.3
SHOPS = {1: 'nMS1', 2: 'nMS2', 3: 'nMS3'}
# order strings for the stone abilities (channel): the first 8 the map does not use yet (most are used by moves)
ORDER_CANDIDATES = ['darkportal', 'fingerofdeath', 'firebolt', 'rejuvination', 'sanctuary', 'creepheal', 'recharge',
                    'preservation', 'spirittroll', 'dreadlordinferno', 'creepanimatedead']

# new playable Pokemon: name, id, template, PKL unit, stem, base stats HP/Atk/Def/SpA/SpD/Spe, unit name, evolution,
# moves (template's learnset + extra moves, or own list)
FORMS = [
    dict(name='Meganium', id='PV0A', template='Bayleef', pkl='h0LS', stem='Meganium', stats=(80, 82, 100, 83, 100, 80),
         unam='Grass Pokemon', evo=('Bayleef', 32), moves_from='Bayleef',
         moves=[('Petal Blizzard', 32), ('Petal Dance', 60)]),
    dict(name='Porygon2', id='PV1A', template='Porygon', pkl='h0GD', stem='Porygon2', stats=(85, 80, 90, 105, 95, 60),
         unam='Normal Pokemon', evo=('Porygon', 50), moves_from='Porygon', moves=[('Tri Attack', 50), ('Zap Cannon', 62)]),
    dict(name='Latias & Latios', id='PV2A', template='Raikou', pkl='h0JA', stem='LatiasLatios',
         stats=(80, 85, 85, 120, 120, 110), unam='Dragon&Psychic Pokemon', evo=None, moves_from=None,
         moves=[('Dragon Breath', 1), ('Confusion', 1), ('Psybeam', 20), ('Dragon Pulse', 35), ('Zen Headbutt', 40),
                ('Psychic', 45), ('Dragon Claw', 50), ('Draco Meteor', 70)]),
]
LEGEND = dict(name='Latias & Latios', id='nL18', template='nL0F', soul='ISL9', soul_template='ISL0', hero='PV2A',
              pkl_template_species='Raikou')
ZEN = dict(id='hZ00', template='hM0O', pkl='h0EQ', pkl_base='h0EN', stem='DarmanitanZen', species='Darmanitan')

# wild creeps
WILD_TEMPLATE = 'nW1B'
WILD_SKIP = {'Latias & Latios', 'Leafleon'}  # a legend; Leafleon = second unit of Leafeon
POW_DPS = {1: 30, 2: 45, 3: 65, 4: 100, 5: 130, 6: 160, 7: 185, 8: 230, 9: 260, 10: 280}
POW_ARM = {1: 8, 2: 12, 3: 15, 4: 16, 5: 16, 6: 18, 7: 20, 8: 20, 9: 21, 10: 22}
POW_GOLD = {1: 10, 2: 15, 3: 30, 4: 45, 5: 60, 6: 80, 7: 100, 8: 130, 9: 160, 10: 200}
ATTACK_LOOK = ('ua1m', 'ua1z', 'ulpx', 'ulpy', 'ulpz', 'uimz', 'ua1r')
CHUNK = 1200   # JASS lines per data function (each runs in its own ExecuteFunc thread: op limit)


class Content:
    def __init__(self):
        self.objs = []          # new w3u objects (objdata.Obj)
        self.shop_add = {}      # shop unit id -> [item ids]
        self.item_rows = []     # (template id, new id, {column: value}) for ItemData.slk
        self.item_txt = []      # (section id, [(key, value)]) for ItemFunc.txt
        self.abil_rows = []     # same for AbilityData.slk
        self.abil_txt = []      # same for CampaignAbilityStrings.txt
        self.links = []         # (unit type, Ability number) for Ab_InitData
        self.megas = []         # (Mega index, Ability number)
        self.mega_types = {}    # 'Mega X' -> 'Type Type'
        self.data = []          # JASS data lines (split into functions by jass())
        self.files = {}         # imported files (build only)
        self.report = []
        self.wild = []          # the wild plan rows

    @property
    def units(self):
        return {o.id: o for o in self.objs}

    def jass(self):
        """(functions, calls): data functions V34_Data1.. and the ExecuteFunc lines for Mega_Init"""
        funcs, calls = [], []
        for k in range(0, len(self.data), CHUNK):
            name = 'V34_Data%d' % (k // CHUNK + 1)
            funcs.append('function %s takes nothing returns nothing\n%s\nendfunction' %
                         (name, '\n'.join(self.data[k:k + CHUNK])))
            calls.append('    call ExecuteFunc("%s")\n' % name)
        head = '// v3.4 (generated by tools/v34/content.py): new Megas, Pokemon, legend, wild creeps and Souls\n'
        return head + '\n'.join(funcs) + '\n', ''.join(calls)


# ------------------------------------------------------------------ helpers
def b36(i, width=2):
    s = ''
    for _ in range(width):
        s = B36[i % 36] + s
        i //= 36
    return s


def jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _q(s):
    return '"%s"' % s


def clone(obj, new_id):
    return objdata.Obj(obj.orig, new_id, [objdata.Mod(x.field, x.type, x.value, x.level, x.data, x.end)
                                          for x in obj.mods])


def setf(obj, field, value, typ):
    """set a field, keeping the type the object already uses for it"""
    for m in obj.mods:
        if m.field == field:
            typ = m.type
            break
    if typ == T_INT:
        value = int(value)
    elif typ != T_STRING:
        value = float(value)
    obj.set(field, typ, value)


def stem_of(path):
    return re.sub(r'\.md[lx]$', '', path or '', flags=re.I)


def script_int(script, pattern):
    return int(re.search(pattern, script).group(1))


class Pkl:
    """PKLegends unit data (war3map.w3u + war3mapSkin.w3u merged) and files"""

    def __init__(self, path):
        import mpq
        self.mpq = mpq.MPQ(path)
        self.units = {}
        for fn in ('war3map.w3u', 'war3mapSkin.w3u'):
            if self.mpq.has(fn):
                for o in objdata.ObjFile(self.mpq.read(fn)).all():
                    d = self.units.setdefault(o.id, {})
                    for m in o.mods:
                        d.setdefault(m.field, m.value)
        wts = {}
        if self.mpq.has('war3map.wts'):
            t = self.mpq.read('war3map.wts').decode('utf-8', 'replace')
            for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
                wts[int(m.group(1))] = m.group(2)
        self.by_species = {}
        for uid, d in self.units.items():
            n = str(d.get('unam') or '')
            if n.startswith('TRIGSTR_'):
                n = wts.get(int(n[8:].split()[0] or 0), n)
            m = re.match(r'^(.+?)\s*\((?:lvl|Lvl|LVL)\.?\s*(\d+)\)', re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', n))
            if m:
                self.by_species.setdefault(m.group(1).strip(), []).append((int(m.group(2)), uid))

    def scale(self, uid):
        return float(self.units.get(uid, {}).get('usca') or 1.0)

    def species_unit(self, name):
        cands = sorted(self.by_species.get(name, []))
        return cands[-1][1] if cands else None


def _pokedex_png(name):
    for n in (name, name.replace("'", ''), name.replace('.', ''), name.replace(' ', '-')):
        p = os.path.join(POKEDEX, n + '.png')
        if os.path.isfile(p):
            return p
    return None


def soul_icon(name, fallback_blp):
    """(BTN, DISBTN) BLP bytes: the Pokemon on a dark glowing tile, like the Souls of v2.6 (make_soul_icons.py)"""
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
    import make_type_icons as mti
    png = _pokedex_png(name)
    if png:
        spr = Image.open(png).convert('RGBA')
    elif fallback_blp:
        spr = Image.open(io.BytesIO(fallback_blp)).convert('RGBA')
    else:
        return None
    bb = spr.getbbox()
    if bb:
        spr = spr.crop(bb)
    size = mti.SIZE
    spr.thumbnail((size - 12, size - 12), Image.LANCZOS)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([1, 1, size - 2, size - 2], radius=10, fill=(24, 18, 44, 255),
                                          outline=(150, 90, 230, 255), width=3)
    glow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([8, 8, size - 8, size - 8], fill=(150, 90, 230, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(spr, ((size - spr.width) // 2, (size - spr.height) // 2))
    grey = ImageOps.grayscale(img.convert('RGB')).convert('RGBA')
    grey.putalpha(img.getchannel('A'))
    out = []
    for im in (img, grey):
        fd, tmp = tempfile.mkstemp(suffix='.blp')
        os.close(fd)
        try:
            mti.write_blp1(im, tmp)
            out.append(open(tmp, 'rb').read())
        finally:
            os.remove(tmp)
    return out[0], out[1]


class _Res:
    def __init__(self):
        self.files, self.warnings = {}, []


def import_model(c, pkl, stem, dest_stem):
    """PKL model (+ portrait, textures) -> war3mapImported\\V34\\<dest_stem>\\; returns the model path for units"""
    import assets
    src = assets._Source(pkl=pkl.mpq)
    data = assets._pkl_model(pkl.mpq, stem)
    if data is None:
        c.report.append('WARNING: PKL model %s not found' % stem)
        return None
    import mdx
    alt = {}  # textures PKL lacks too (Mega Altaria's shiny "334SSAmega"): use the normal one ("334Amega")
    for _, tex in mdx.inspect(data)['textures']:
        if tex and src.texture(tex) is None and 'SS' in tex and src.texture(tex.replace('SS', '')) is not None:
            alt[tex] = tex.replace('SS', '')
    if alt:
        data = mdx.patch_texture_paths(data, alt)
        c.report.append('%s: textures missing in PKL replaced: %s' % (dest_stem, alt))
    res = _Res()
    folder = V34_DIR + dest_stem + '\\'
    assets._import_model(res, src, data, dest_stem, dest_stem, dest_dir=folder)
    port = assets._pkl_portrait(pkl.mpq, stem)
    if port is not None:
        assets._import_model(res, src, port, dest_stem + '_portrait', dest_stem + ' portrait', dest_dir=folder)
    c.files.update(res.files)
    c.report.extend('WARNING: ' + w for w in res.warnings)
    return folder + dest_stem + '.mdl'


def import_icon(c, pkl, pkl_icon, dest_name):
    import assets
    if not pkl_icon or not pkl.mpq.has(pkl_icon):
        c.report.append('WARNING: PKL icon %s not found' % pkl_icon)
        return None
    data = pkl.mpq.read(pkl_icon)
    c.files[BTN + dest_name] = data
    try:
        c.files[DIS + 'DIS' + dest_name] = assets._disabled_icon(data)
    except Exception as e:  # noqa: BLE001
        c.report.append('WARNING: no disabled icon for %s (%s)' % (dest_name, e))
    return BTN + dest_name


# ------------------------------------------------------------------ the parts
def _used_orders(base):
    import slk
    used = set()
    text = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    used.update(o.lower() for o in re.findall(r'(?m)^Order=(\w+)', text))
    s = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    for row in s.rows:
        for v in row.values():
            if isinstance(v, str) and re.fullmatch(r'"[a-z]+"', v):
                used.add(v.strip('"'))
    return used


def _megas(c, script, units, ids, base, pkl, ab_num, with_files):
    import apply as A
    first = script_int(script, r'set Mega_N = (\d+)')
    assert first == MEGA_FIRST, 'Mega_N of the base script is %d' % first
    used = _used_orders(base)
    orders = [o for o in ORDER_CANDIDATES if o not in used][:len(MEGAS)]
    assert len(orders) == len(MEGAS), 'not enough free order strings'
    slot = {1: 8, 2: 8, 3: 9}
    tmpl = units['hM0O']
    for i, (key, name, base_sp, stone, price, ps, pa, pi, pkl_id, types, ab, shop) in enumerate(MEGAS):
        idx = first + i
        sid, iid, aid = 'hM0' + B36[25 + i], 'IM0' + B36[25 + i], 'AM0' + B36[25 + i]
        bid = ids[base_sp][0]
        bu = units[bid]
        short = name.replace('Mega ', '')
        icon = BTN + 'BTNMega%s.blp' % short
        o = clone(tmpl, sid)
        mdl = 'war3mapImported\\V34\\%s\\%s.mdl' % (key, key)
        if with_files:
            mdl = import_model(c, pkl, stem_of(pkl.units[pkl_id].get('umdl')).split('\\')[-1], key) or mdl
            import_icon(c, pkl, pkl.units[pkl_id].get('uico'), 'BTNMega%s.blp' % short)
        setf(o, 'umdl', mdl, T_STRING)
        setf(o, 'uico', icon, T_STRING)
        setf(o, 'ussi', bu.get('ussi') or bu.get('uico') or icon, T_STRING)
        setf(o, 'unam', name, T_STRING)
        setf(o, 'upro', base_sp, T_STRING)
        c.objs.append(o)
        c.mega_types[name] = types
        base_scale = float(bu.get('usca') or 1.0)
        pkl_base = pkl.species_unit(base_sp)
        scale = base_scale * pkl.scale(pkl_id) / (pkl.scale(pkl_base) if pkl_base else 1.0)
        bonus = '+%d%% STR, %+d%% AGI, %+d%% INT, +10 armor, +80 move speed, +40%% attack speed' % (ps, pa, pi)
        bonus = bonus.replace('+-', '-')
        c.data += [
            "    set Mega_Base[%d] = '%s'" % (idx, bid),
            "    set Mega_Stone[%d] = '%s'" % (idx, iid),
            "    set Mega_Skin[%d] = '%s'" % (idx, sid),
            "    set Mega_Evolve[%d] = '%s'" % (idx, aid),
            '    set Mega_PStr[%d] = %d' % (idx, ps),
            '    set Mega_PAgi[%d] = %d' % (idx, pa),
            '    set Mega_PInt[%d] = %d' % (idx, pi),
            '    set Mega_Price[%d] = %d' % (idx, price),
            '    set Mega_Name[%d] = %s' % (idx, jstr(name)),
            '    set Mega_StoneName[%d] = %s' % (idx, jstr(stone)),
            '    set Mega_Fx[%d] = ""' % idx,
            '    set Mega_Scale[%d] = %.3f' % (idx, scale),
            '    set Mega_BaseScale[%d] = %.3f' % (idx, base_scale),
            '    set Mega_R[%d] = 255' % idx, '    set Mega_G[%d] = 255' % idx, '    set Mega_B[%d] = 255' % idx,
        ]
        c.megas.append((idx, ab_num[ab]))
        # stone item, its ability, the shop
        n = slot[shop]
        slot[shop] += 1
        c.item_rows.append(('IM00', iid, {'abilList': _q(aid), 'cooldownID': _q(aid), 'goldcost': str(price)}))
        c.item_txt.append((iid, [
            ('Name', stone), ('Tip', 'Purchase |cffff66cc%s|r' % stone),
            ('Ubertip', '|cffffcc00Use (click in the inventory):|r |cffff66ccMega Evolve|r |cffffcc00%s|r into '
                        '|cffff66cc%s|r for 60s (%s). Cooldown 150s. Mega Ability: |cffffcc00%s|r.|n|n'
                        '|cffffcc00Only %s can use it.|r' % (base_sp, name, bonus, ab, base_sp)),
            ('Description', 'Mega Stone of %s.' % base_sp), ('Art', icon), ('Buttonpos', '%d,%d' % (n % 4, n // 4))]))
        c.abil_rows.append(('AM00', aid, {'DataF1': _q(orders[i])}))
        c.abil_txt.append((aid, [
            ('Name', 'Mega Evolve'), ('Art', icon), ('Buttonpos', '1,1'), ('Order', orders[i]),
            ('Tip', 'Mega Evolve - |cffff66cc%s|r' % name),
            ('Ubertip', '%s Mega Evolves into |cffff66cc%s|r for 60s: %s.|n|n|cffffcc00Cooldown:|r 150s' %
             (base_sp, name, bonus))]))
        c.shop_add.setdefault(SHOPS[shop], []).append(iid)
    c.data.append('    set Mega_N = %d' % (first + len(MEGAS)))
    c.report.append('Megas: %d new (Mega_N %d), stone orders %s' % (len(MEGAS), first + len(MEGAS), orders))


def _learnset(script, uid):
    n = re.search(r"call SaveInteger\(Ab_HT, '%s', 99, (\d+)\)" % uid, script)
    out = []
    if n:
        for k in range(int(n.group(1))):
            m = int(re.search(r"call SaveInteger\(Ab_HT, '%s', %d, (\d+)\)" % (uid, 100 + 2 * k), script).group(1))
            lv = int(re.search(r"call SaveInteger\(Ab_HT, '%s', %d, (\d+)\)" % (uid, 101 + 2 * k), script).group(1))
            out.append((m, lv))
    return out


def _forms(c, script, units, ids, pkl, with_files):
    labels = dict((re.sub(r' \(.*', '', lab), int(i))
                  for i, lab in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script))
    evo_n = script_int(script, r'set Evo_N = (\d+)')
    for f in FORMS:
        tid = ids[f['template']][0]
        t = units[tid]
        o = clone(t, f['id'])
        hp, atk, df, spa, spd, spe = f['stats']
        nm, stem = f['name'], f['stem']
        icon = BTN + 'BTNPoke%s.blp' % stem
        mdl = V34_DIR + '%s\\%s.mdl' % (stem, stem)
        if with_files:
            pu = pkl.units[f['pkl']]
            mdl = import_model(c, pkl, stem_of(pu.get('umdl')).split('\\')[-1], stem) or mdl
            import_icon(c, pkl, pu.get('uico'), 'BTNPoke%s.blp' % stem)
        pt = pkl.species_unit(f['template'])
        scale = float(t.get('usca') or 1.0) * pkl.scale(f['pkl']) / (pkl.scale(pt) if pt else 1.0)
        primary_str = atk > spa
        for field, value, typ in (
                ('umdl', mdl, T_STRING), ('uico', icon, T_STRING), ('ussi', icon, T_STRING),
                ('unam', f['unam'], T_STRING), ('upro', nm, T_STRING),
                ('uawt', 'Revive %s' % nm, T_STRING), ('utip', 'Summon %s' % nm, T_STRING),
                ('utpr', 'Revive %s' % nm, T_STRING), ('utub', '|cffffcc00%s|r (Pokemon). Can learn .' % nm, T_STRING),
                ('uhpm', hp * 20, T_INT), ('ustr', atk, T_INT), ('uagi', spe, T_INT), ('uint', spa, T_INT),
                ('ustp', atk / 50.0, T_REAL), ('uagp', spe / 50.0, T_REAL), ('uinp', spa / 50.0, T_REAL),
                ('udef', int((df + spd) / 4.0 + 0.5), T_INT), ('usca', scale, T_REAL),
                ('upra', 'STR' if primary_str else 'INT', T_STRING)):
            setf(o, field, value, typ)
        c.objs.append(o)
        ids.setdefault(nm, [f['id']])
        # stats (Hero_HPSync), learnset, evolution
        c.data += ["    call SaveInteger(Mega_HT, '%s', %d, %d)" % (f['id'], k, v) for k, v in (
            (80, hp * 20), (81, hp * 20), (82, atk), (83, spe), (84, spa), (85, 1 if primary_str else 3), (86, 2000))]
        moves = _learnset(script, ids[f['moves_from']][0]) if f['moves_from'] else []
        have = {m for m, _lv in moves}
        for mname, lv in f['moves']:
            if mname not in labels:
                raise ValueError('move %s not in the map' % mname)
            if labels[mname] not in have:
                moves.append((labels[mname], lv))
        c.data.append("    call SaveInteger(Ab_HT, '%s', 99, %d)" % (f['id'], len(moves)))
        for k, (m, lv) in enumerate(moves):
            c.data.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (f['id'], 100 + 2 * k, m))
            c.data.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (f['id'], 101 + 2 * k, lv))
        if f['evo']:
            pre, lv = f['evo']
            c.data += ["    set Evo_From[%d] = '%s'" % (evo_n, ids[pre][0]), "    set Evo_To[%d] = '%s'" % (evo_n, f['id']),
                       '    set Evo_Level[%d] = %d' % (evo_n, lv)]
            evo_n += 1
        c.report.append('new Pokemon %s %s: %d moves, scale %.2f' % (f['id'], nm, len(moves), scale))
    c.data.append('    set Evo_N = %d' % evo_n)


def _legend(c, script, units, pkl, soul_n, with_files):
    lg = LEGEND
    leg_n = script_int(script, r'set Leg_N = (\d+)')
    t = units[lg['template']]
    o = clone(t, lg['id'])
    stem = 'LatiasLatios'
    mdl = V34_DIR + '%s\\%s.mdl' % (stem, stem)
    raikou = pkl.species_unit(lg['pkl_template_species'])
    scale = float(t.get('usca') or 1.0) * pkl.scale('h0JA') / (pkl.scale(raikou) if raikou else 1.0)
    setf(o, 'unam', 'Wild ' + lg['name'], T_STRING)
    setf(o, 'umdl', mdl, T_STRING)
    setf(o, 'uico', BTN + 'BTNPoke%s.blp' % stem, T_STRING)
    setf(o, 'usca', scale, T_REAL)
    c.objs.append(o)
    c.data += ["    set Leg_Type[%d] = '%s'" % (leg_n, lg['id']), "    set Leg_Soul[%d] = '%s'" % (leg_n, lg['soul']),
               '    set Leg_Name[%d] = %s' % (leg_n, jstr(lg['name'])), '    set Leg_N = %d' % (leg_n + 1),
               "    set Soul_Item[%d] = '%s'" % (soul_n, lg['soul']), "    set Soul_Hero[%d] = '%s'" % (soul_n, lg['hero'])]
    c.item_rows.append((lg['soul_template'], lg['soul'], {}))
    c.item_txt.append((lg['soul'], [
        ('Name', '%s Soul' % lg['name']), ('Tip', '%s Soul' % lg['name']),
        ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to become |cffffcc00%s|r.'
         % lg['name']), ('Description', 'Soul of a wild %s.' % lg['name']),
        ('Art', BTN + 'BTNSoul%s.blp' % lg['soul'])]))
    if with_files:
        ico = soul_icon(lg['name'], None)
        if ico:
            c.files[BTN + 'BTNSoul%s.blp' % lg['soul']], c.files[DIS + 'DISBTNSoul%s.blp' % lg['soul']] = ico
    return soul_n + 1


def _zen(c, units, ids, pkl, with_files):
    z = ZEN
    o = clone(units[z['template']], z['id'])
    mdl = V34_DIR + '%s\\%s.mdl' % (z['stem'], z['stem'])
    icon = BTN + 'BTNPoke%s.blp' % z['stem']
    if with_files:
        pu = pkl.units[z['pkl']]
        mdl = import_model(c, pkl, stem_of(pu.get('umdl')).split('\\')[-1], z['stem']) or mdl
        if not import_icon(c, pkl, pu.get('uico'), 'BTNPoke%s.blp' % z['stem']):
            icon = units[ids[z['species']][0]].get('uico')
    setf(o, 'umdl', mdl, T_STRING)
    setf(o, 'uico', icon, T_STRING)
    setf(o, 'unam', 'Darmanitan Zen Mode', T_STRING)
    setf(o, 'upro', z['species'], T_STRING)
    c.objs.append(o)
    dar = units[ids[z['species']][0]]
    base = float(dar.get('usca') or 1.0)
    zen = base * pkl.scale(z['pkl']) / pkl.scale(z['pkl_base'])
    c.data += ["    set Ab_ZenSkin = '%s'" % z['id'], '    set Ab_ZenScale = %.3f' % zen, '    set Ab_ZenBase = %.3f' % base]


def power_of_level(lv):
    import apply as A
    p = 1
    for k, (plv, _hp) in sorted(A.POWER_LV_HP.items()):
        if plv <= lv:
            p = k
    return p


def _bst(name):
    import json
    n = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-').replace('.', ''))
    n = n.replace('alolan-', '') + ('-alola' if name.startswith('Alolan-') else '')
    for cand in (n, n.split('-')[0]):
        p = os.path.join(WORK, 'analysis', 'pokeapi_cache', 'pokemon__%s.json' % cand)
        if os.path.exists(p):
            st = json.load(open(p, encoding='utf-8')).get('stats') or []
            return sum(s['base_stat'] if isinstance(s, dict) else s for s in st) or None
    return None


def _single_start(total):
    if total is None:
        return 3
    for lim, p in ((330, 1), (400, 2), (450, 3), (480, 4), (500, 5), (520, 6), (540, 7)):
        if total < lim:
            return p
    return 8


def wild_plan(script, units, edges, ids, by_name):
    """rows for every non-legend playable species without a wild creep: power range from the evolution levels"""
    import apply as A
    wild = set()
    for _i, t in re.findall(r"set Wild_Pool\[(\d+)\] = '(\w{4})'", script):
        o = units.get(t)
        n = (o.get('unam') if o else t) or t
        wild.add(A._norm(n[5:] if n.startswith('Wild ') else n))
    wild.add('nidoran')
    incoming, outgoing = {}, {}
    for (a, b), lv in edges.items():
        incoming[b] = min(lv, incoming.get(b, 999))
        outgoing.setdefault(a, []).append(b)
    seen, rows = set(), []
    for sp in sorted(ids, key=str.lower):
        key = A._norm(sp)
        if sp in A.LEGENDS or sp in WILD_SKIP or key in seen or key in wild or not by_name.get(sp):
            continue
        seen.add(key)
        if sp in incoming:
            lv, pmin = incoming[sp], power_of_level(incoming[sp])
        elif sp in outgoing:
            lv, pmin = 1, 1
        else:
            lv, pmin = None, _single_start(_bst(sp))
        nexts = [power_of_level(edges[(sp, b)]) for b in outgoing.get(sp, [])]
        pmax = max(pmin, min(nexts) - 1) if nexts else 10
        rows.append(dict(species=sp, hero=ids[sp][0], types=by_name[sp], level=lv, pmin=pmin, pmax=pmax))
    return rows


def _wild(c, script, units, ids, by_name, links, soul_n, base, with_files):
    import apply as A
    report = []
    _out, edges, ids2, _names = A.gym_evolutions(script, units, report)
    rows = wild_plan(script, units, edges, ids2, by_name)
    c.wild = rows
    type_n = script_int(script, r'set Wild_TypeN = (\d+)')
    pool_n = script_int(script, r'set Wild_PoolN = (\d+)')
    tmpl = units[WILD_TEMPLATE]
    ab_of = dict(links)  # Ability of each playable Pokemon: the map's links + the ones added in v3.4 (MISSING)
    import abilities
    num = abilities.by_name()
    for sp, uids in ids2.items():
        if sp in abilities.MISSING:
            for u in uids:
                ab_of.setdefault(u, num[abilities.MISSING[sp]])
    for i, r in enumerate(rows):
        uid, iid = 'nX' + b36(i), 'IU' + b36(i)
        hero = units[r['hero']]
        o = clone(tmpl, uid)
        p0 = r['pmin']
        lv, hp = A.POWER_LV_HP[p0]
        dps = POW_DPS[p0]
        for m in hero.mods:  # attack look of the playable Pokemon (missile, range, launch heights)
            if m.field in ATTACK_LOOK:
                o.set(m.field, m.type, m.value)
        ranged = (hero.get('ua1r') or 0) >= 200 and bool(hero.get('ua1m'))
        for field, value, typ in (
                ('unam', r['species'], T_STRING), ('umdl', hero.get('umdl'), T_STRING),
                ('uico', hero.get('uico'), T_STRING), ('usca', float(hero.get('usca') or 1.0), T_REAL),
                ('ua1w', 'missile' if ranged else 'normal', T_STRING), ('ulev', lv, T_INT), ('uhpm', hp, T_INT),
                ('ua1c', 1.0, T_REAL), ('ua1b', max(1, int(dps * 0.9)) - 1, T_INT), ('ua1d', 1, T_INT),
                ('ua1s', max(1, int(dps * 0.2)), T_INT), ('udef', POW_ARM[p0], T_INT), ('ubba', POW_GOLD[p0], T_INT),
                ('umvs', 320, T_INT)):
            setf(o, field, value, typ)
        if not ranged:
            setf(o, 'ua1r', 100, T_INT)
        c.objs.append(o)
        kit = A.TI[r['types'][0]] + 1
        c.data += ["    set Wild_Type[%d] = '%s'" % (type_n + i, uid),
                   "    call SaveInteger(Mega_HT, '%s', 8, '%s')" % (uid, iid),
                   "    call SaveInteger(Mega_HT, '%s', 30, %d)" % (uid, kit),
                   "    call SaveInteger(Mega_HT, '%s', 39, 1)" % uid,
                   "    set Soul_Item[%d] = '%s'" % (soul_n + i, iid),
                   "    set Soul_Hero[%d] = '%s'" % (soul_n + i, r['hero'])]
        for p in range(r['pmin'], r['pmax'] + 1):
            c.data += ["    set Wild_Pool[%d] = '%s'" % (pool_n, uid), '    set Wild_PoolPow[%d] = %d' % (pool_n, p)]
            pool_n += 1
        if r['hero'] in ab_of:
            c.links.append((uid, ab_of[r['hero']]))
        c.item_rows.append(('IS00', iid, {}))
        c.item_txt.append((iid, [
            ('Name', '%s Soul' % r['species']), ('Tip', '%s Soul' % r['species']),
            ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to become '
                        '|cffffcc00%s|r.' % r['species']),
            ('Description', 'Soul of a wild %s.' % r['species']), ('Art', BTN + 'BTNSoul%s.blp' % iid)]))
        if with_files:
            fb = base.read(hero.get('uico')) if hero.get('uico') and base.has(hero.get('uico')) else None
            ico = soul_icon(r['species'], fb)
            if ico:
                c.files[BTN + 'BTNSoul%s.blp' % iid], c.files[DIS + 'DISBTNSoul%s.blp' % iid] = ico
            else:
                c.report.append('WARNING: no Soul icon for %s' % r['species'])
    c.data += ['    set Wild_TypeN = %d' % (type_n + len(rows)), '    set Wild_PoolN = %d' % pool_n,
               '    set Soul_N = %d' % (soul_n + len(rows))]
    for p in range(1, 11):
        c.data += ['    set Wild_PowDmg[%d] = %s' % (p, repr(float(POW_DPS[p]))),
                   '    set Wild_PowArm[%d] = %s' % (p, repr(float(POW_ARM[p]))),
                   '    set Wild_PowGold[%d] = %d' % (p, POW_GOLD[p])]
    per = {p: sum(1 for r in rows if r['pmin'] <= p <= r['pmax']) for p in range(1, 11)}
    c.report.append('wild: %d new species (%s .. %s), pool %d entries, new species per power %s'
                    % (len(rows), 'nX00', 'nX' + b36(len(rows) - 1), pool_n, per))


def make(script, units, base, pkl_path=PKL_MAP, with_files=False):
    """everything new of v3.4 (see the module text). units = custom units of the v3.3.3 map (id -> Obj)."""
    import abilities
    import apply as A
    c = Content()
    pkl = Pkl(pkl_path)
    ab_num = abilities.by_name()
    names = A.hero_names(units)
    ids = {}
    for uid in sorted(names, key=lambda u: (u[0] != 'E', u)):
        ids.setdefault(names[uid], []).append(uid)
    links, _megas_old = A.old_ability_links(script)
    _megas(c, script, units, ids, base, pkl, ab_num, with_files)
    _forms(c, script, units, ids, pkl, with_files)
    soul_n = script_int(script, r'set Soul_N = (\d+)')
    soul_n = _legend(c, script, units, pkl, soul_n, with_files)
    c.links.append((LEGEND['id'], ab_num['Levitate']))
    _zen(c, units, ids, pkl, with_files)
    allu = dict(units)
    allu.update(c.units)
    _by_id, by_name = A.hero_types(allu)
    _wild(c, script, allu, ids, by_name, links, soul_n, base, with_files)
    import extras
    allu.update(c.units)
    extras.add(c, script, units, allu, ids, by_name, base)
    return c
