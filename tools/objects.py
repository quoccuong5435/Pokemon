"""Add Mega object data: skin/Kid/shop units (w3u), stones (ItemData.slk + ItemFunc.txt),
abilities (AbilityData.slk + CampaignAbilityStrings.txt)."""
import os

import learn_data as ld
import legend_data
import objdata
import poke_data as pd
import skill_data
import slk
from ability_data import INFO_POS, RAW_ABILITIES, info_id
from mega_data import (ATTR_PCT_PER_POINT, BONUS_IDS, BONUS_VALUES, COOLDOWN, DAMAGE_BONUS, DURATION, KID_ID,
                       MEGAS, SHOP_RANGES)
from objdata import T_INT, T_REAL, T_STRING

W3U = 'war3map.w3u'
ITEM_SLK = 'Units\\ItemData.slk'
ITEM_TXT = 'Units\\ItemFunc.txt'
ABIL_SLK = 'Units\\AbilityData.slk'
ABIL_TXT = 'Units\\CampaignAbilityStrings.txt'
Y_VARIANTS = (2, 14)  # Charizard Y, Mewtwo Y -> second button slot
OBJECT_FILES = (W3U, ITEM_SLK, ITEM_TXT, ABIL_SLK, ABIL_TXT)


def _q(s):
    return '"%s"' % s


# ------------------------------------------------------------------ units
def _clone(obj, new_id):
    return objdata.Obj(obj.orig, new_id, [objdata.Mod(x.field, x.type, x.value, x.level, x.data, x.end)
                                          for x in obj.mods])


def _poke_heroes(f, poke):
    """New playable Pokemon: clone of an Arena hero of the same type/stage with new model, name and skills."""
    for form in pd.FORMS:
        o = _clone(f.find(form.template), form.id)
        kit = pd.KITS.get(form.kit, [])
        o.set('upro', T_STRING, form.name)
        o.set('upru', T_INT, 1)
        o.set('unam', T_STRING, pd.KIT_TYPES[form.kit] if form.kit in pd.KIT_TYPES else __import__('type_taverns').type_label(form.name))
        o.set('umdl', T_STRING, poke.model_path[form.id])
        o.set('uico', T_STRING, poke.icon_path[form.id])
        o.set('ussi', T_STRING, poke.icon_path[form.id])
        o.set('usca', T_REAL, float(poke.scale[form.id]))
        o.set('uhab', T_STRING, '')  # v3.2: moves come from the + system only
        o.set('uabi', T_STRING, 'AInv')
        hot = ''
        if form.id in pd.STARTERS:
            i = pd.STARTERS.index(form.id)
            hot = pd.TAVERN_HOTKEYS[i]
            o.set('uhot', T_STRING, hot)
            o.set('ubpx', T_INT, i % 4)
            o.set('ubpy', T_INT, i // 4)
        key = ' |cffffcc00[%s]|r' % hot if hot else ''
        o.set('utip', T_STRING, 'Summon %s%s' % (form.name, key))
        o.set('uawt', T_STRING, 'Revive %s%s' % (form.name, key))
        o.set('utpr', T_STRING, 'Revive %s%s' % (form.name, key))
        evo = ''
        if form.evolves_to:
            evo = 'Evolves into |cffffcc00%s|r at lv %d. ' % (pd.FORM_BY_ID[form.evolves_to].name, form.level)
        for frm, item, to in pd.ITEM_EVOLUTIONS:
            if frm == form.id:
                evo += 'Evolves into |cffffcc00%s|r with a Sun Stone. ' % pd.FORM_BY_ID[to].name
        o.set('utub', T_STRING, '|cffffcc00%s|r (%s). %sCan learn %s.' % (
            form.name, pd.KIT_TYPES.get(form.kit, 'Pokemon'), evo, ', '.join(s.name for s in kit)))
        f.custom.append(o)
    tav = _clone(f.find(pd.TAVERN_TEMPLATE), pd.TAVERN_ID)
    tav.set('unam', T_STRING, pd.TAVERN_NAME)
    tav.set('useu', T_STRING, '')  # v3.3: one list building, the Pokemon are chosen in the picker menu (Pick_*)
    f.custom.append(tav)
    import type_taverns
    return  # (the 18 type taverns are merged into the list building)
    for i, (typ, ids) in enumerate(type_taverns.groups(), 1):  # v3.3: one tavern per type
        tt = _clone(f.find(pd.TAVERN_TEMPLATE), type_taverns.tavern_id(i))
        tt.set('unam', T_STRING, type_taverns.tavern_name(typ))
        tt.set('useu', T_STRING, ','.join(ids))
        tt.set('uico', T_STRING, 'ReplaceableTextures\\CommandButtons\\%s.blp' % type_taverns.TYPE_ICON[typ])
        f.custom.append(tt)
        for k, fid in enumerate(ids):
            o = f.find(fid)
            o.set('ubpx', T_INT, k % 4)
            o.set('ubpy', T_INT, k // 4)
            o.set('uhot', T_STRING, type_taverns.SELL_HOTKEYS[k])


TELE_ABILITY = 'A005'  # v1.8 Teleport (Blink) of the map: the teleport button of Celebi and Darkrai
TELE_UNITS = ('n00F', 'n035', 'E023', 'PZZA')  # Darkrai legend, Celebi legend, playable Darkrai
DANGLING_ABILITIES = ('ACcb', 'ACtc', 'A01P', 'A00X')  # referenced by v1.8 units but not defined in the map
# v3.3: teleport items of the Haunt Legendary shop (n030): id, name, icon, button position, hotkey
LEGEND_TELE_ITEMS = (('IL00', "Celebi's Location", 'BTNCelebi (64 x 64).blp', '2,1', 'C'),
                     ('IL01', "Darkrai's Location", 'BTNDarkrai (64 x 64).blp', '3,1', 'D'))
LEGEND_HP_MULT = 1.25  # legend HP: x0.5 (v3.2) times 2.5
LEGEND_DMG_MULT = 2.0   # legend damage: x0.8 (v3.2) times 2.5
LEGEND_ARMOR_MULT = 2.5  # legend armor: min(armor, 35) (v3.2) times 2.5
POKE_CENTER_HEAL_MULT = 3.0  # Poke Center regeneration x3 (5% -> 15% of max HP per second)
HERO_HP_MULT = 2.0  # v3.3: playable Pokemon max HP x2 (a lv 100 Pokemon had ~8k, wild elites reach 25k+)


def _units(data, a):
    f = objdata.ObjFile(data)
    for hid, typ in skill_data.hero_types().items():  # v3.0: every v1.8 Pokemon gets its type's 5-skill kit
        o = f.find(hid)
        if o is not None:
            o.set('uhab', T_STRING, '')  # v3.2: moves come from the + system only
    shop = f.find('n030')
    if shop is not None:  # v3.3: Haunt Legendary also teleports to Celebi and Darkrai
        shop.set('usei', T_STRING, shop.get('usei') + ',' + ','.join(i[0] for i in LEGEND_TELE_ITEMS))
    poke = getattr(a, 'poke', None)
    if poke is not None:
        _poke_heroes(f, poke)
    for hid in list(skill_data.hero_types()) + [fm.id for fm in pd.FORMS]:
        o = f.find(hid)
        if o is not None:
            o.set('uhpm', T_INT, int(round(o.get('uhpm') * HERO_HP_MULT)))
            o.set('uabi', T_STRING, 'AInv')  # v3.3: drop the v1.8 abilities (their buttons duplicated the Pokemon's card)
    boss = f.find('n035')
    if boss is not None and f.find(pd.CELEBI_HERO) is None:  # v3.3: playable Celebi, model and icon of the boss
        ch = _clone(f.find(pd.PKL_TEMPLATE), pd.CELEBI_HERO)
        ch.set('upro', T_STRING, 'Celebi')
        ch.set('unam', T_STRING, 'Psychic&Grass Pokemon')
        ch.set('umdl', T_STRING, boss.get('umdl'))
        ch.set('uico', T_STRING, boss.get('uico'))
        ch.set('usca', T_REAL, 1.4)
        ch.set('uhab', T_STRING, '')
        ch.set('uabi', T_STRING, 'AInv')
        ch.set('utip', T_STRING, 'Celebi')
        f.custom.append(ch)
    for uid in TELE_UNITS:
        o = f.find(uid)
        if o is not None:
            cur = o.get('uabi') or ''
            if TELE_ABILITY not in cur.split(','):
                o.set('uabi', T_STRING, ','.join(x for x in (cur, TELE_ABILITY) if x))
    for m in MEGAS:
        if f.find(m.base_unit) is None:
            continue  # Mega of a new Pokemon that is not part of this build
        # clone the base Pokemon so every art field a skin may carry (sounds, missile art...) stays the same
        o = _clone(f.find(m.base_unit), m.skin_id)
        o.set('umdl', T_STRING, a.model_path[m.index])
        o.set('uico', T_STRING, a.icon_path[m.index])
        o.set('unam', T_STRING, m.name)
        o.set('usca', T_REAL, float(a.scale[m.index]))
        f.custom.append(o)
    # v3.3: abilities that do not exist in the map's ability data (already dangling in v1.8) make the World Editor
    # report "Unit data missing or invalid"; drop those references
    for o in f.custom:
        keep = [x for x in (o.get('uabi') or '').split(',') if x and x not in DANGLING_ABILITIES]
        if (o.get('uabi') or '') and len(keep) != len([x for x in (o.get('uabi') or '').split(',') if x]):
            o.set('uabi', T_STRING, ','.join(keep))
    kid = objdata.Obj('hfoo', KID_ID, [])
    kid.set('umdl', T_STRING, a.kid_model)
    kid.set('unam', T_STRING, 'Kangaskhan Kid')
    kid.set('uabi', T_STRING, 'Aloc,Avul')
    kid.set('umvs', T_INT, 400)
    kid.set('ucol', T_REAL, 0.0)
    kid.set('uaen', T_INT, 0)
    kid.set('ufoo', T_INT, 0)
    kid.set('usca', T_REAL, 1.0)
    f.custom.append(kid)
    mart = f.find('n00O')
    for (sid, first, end), name in zip(SHOP_RANGES, ('Mega Shop I', 'Mega Shop II', 'Mega Shop III')):
        stones = [m for m in MEGAS[first:end] if f.find(m.skin_id) is not None]
        if not stones:
            continue
        o = _clone(mart, sid)
        o.set('unam', T_STRING, name)
        o.set('usei', T_STRING, ','.join(m.stone_id for m in stones))
        o.set('uclr', T_INT, 200)
        o.set('uclg', T_INT, 120)
        o.set('uclb', T_INT, 255)
        f.custom.append(o)
    wild = getattr(a, 'wild', None)
    if wild is not None:
        _wild_units(f, wild)
    _legends(f)
    for leg in getattr(a, 'legends', None) or ():
        o = _clone(f.find(leg.boss), leg.id)  # clone after _legends: already level 100 and buffed
        o.set('unam', T_STRING, 'Wild %s' % leg.name)
        poke = getattr(a, 'poke', None)
        if leg.name in legend_data.PKL_LEGEND_NAMES and poke is not None:  # v3.3: PKLegends model, icon and scale
            form = next(x for x in pd.FORMS if x.name == leg.name)
            o.set('umdl', T_STRING, poke.model_path[form.id])
            o.set('uico', T_STRING, poke.icon_path[form.id])
            o.set('usca', T_REAL, float(poke.scale[form.id]) * 1.5)
        f.custom.append(o)
    return f.to_bytes()


LEGENDS = ('n001', 'n00C', 'n00D', 'n00F', 'n00G', 'n01I', 'n01J', 'n01K', 'n01L', 'n01M', 'n037', 'n01N',
           'n01O', 'n033', 'n034', 'n035')


def _legends(f):
    """Legend bosses (v3.3 balance): level 100, HP x1.25, damage x2.0, armor min(armor, 35) x2.5 (all x2.5 over v3.2)."""
    for lid in LEGENDS:
        o = f.find(lid)
        o.set('ulev', T_INT, 100)
        o.set('uhpm', T_INT, int(round(o.get('uhpm') * LEGEND_HP_MULT)))
        o.set('ua1b', T_INT, int(round(o.get('ua1b') * LEGEND_DMG_MULT)))
        o.set('udef', T_INT, int(round(min(o.get('udef') or 0, 35) * LEGEND_ARMOR_MULT)))


def _wild_units(f, wild):
    import wild_data
    tmpl = f.find(wild_data.SPECIES_TEMPLATE)
    for s in wild_data.SPECIES:
        o = _clone(tmpl, s.id)
        o.set('unam', T_STRING, s.name)
        o.set('umdl', T_STRING, wild.model_path[s.index])
        o.set('uico', T_STRING, wild.icon_path[s.index])
        o.set('usca', T_REAL, float(wild.scale[s.index]))
        o.set('ulev', T_INT, s.level)
        o.set('uhpm', T_INT, s.hp)
        o.set('ua1b', T_INT, s.dmg)
        o.set('udef', T_INT, s.armor)
        o.set('ubba', T_INT, s.gold)
        o.set('ua1w', T_STRING, 'normal')
        o.set('ua1r', T_INT, 100)
        o.remove('ua1m')
        f.custom.append(o)


# ------------------------------------------------------------------ helpers for SLK rows
def _row_from(s, template_id, new_id, values):
    tmpl = s.find(template_id)
    row = dict(tmpl) if tmpl is not None else {}
    row[1] = _q(new_id)
    for col, v in values.items():
        x = s.name_to_x[col]
        if v is None:
            row.pop(x, None)
        else:
            row[x] = v
    s.rows.append(row)


def _new_row(s, new_id, values):
    row = {1: _q(new_id)}
    for col, v in values.items():
        row[s.name_to_x[col]] = v
    s.rows.append(row)


def _section(sid, pairs):
    return '[%s]\n' % sid + ''.join('%s=%s\n' % kv for kv in pairs)


def _append_txt(data, sections):
    text = data.decode('utf-8')
    if not text.endswith('\n'):
        text += '\n'
    return (text + ''.join(sections)).encode('utf-8')


# ------------------------------------------------------------------ items
def _bonus_text(m):
    p = ATTR_PCT_PER_POINT
    return ('+%d%% STR, +%d%% AGI, +%d%% INT, +%d%% damage, +%s armor, +%s move speed, +%d%% attack speed'
            % (m.str_ * p, m.agi * p, m.int_ * p, int(DAMAGE_BONUS * 100), BONUS_VALUES['AMB1'],
               BONUS_VALUES['AMB2'], int(float(BONUS_VALUES['AMB3']) * 100)))


def _stone_tip(m):
    return ('Hold to unlock |cffff66ccMega Evolve|r for |cffffcc00%s|r: becomes |cffff66cc%s|r for %ds '
            '(%s). Cooldown %ds.|n|n|cffffcc00Equip with %s|r'
            % (m.base_name, m.name, int(DURATION), _bonus_text(m), int(COOLDOWN), m.base_name))


def _shop_slot(m):
    for _sid, first, end in SHOP_RANGES:
        if first <= m.index < end:
            return m.index - first
    raise ValueError(m.index)


def _items(slk_data, txt_data, a):
    s = slk.Slk(slk_data.decode('latin-1'))
    sections = []
    for m in MEGAS:
        if m.index not in a.icon_path:
            continue  # Mega of a new Pokemon that is not part of this build
        _row_from(s, 'I012', m.stone_id, {
            'class': _q('Permanent'), 'abilList': _q(''), 'cooldownID': None, 'goldcost': str(m.price),
            'stockMax': '1', 'stockRegen': '60', 'stockStart': '0', 'Level': '8', 'oldLevel': '8',
            'pickRandom': '0'})
        slot = _shop_slot(m)
        sections.append(_section(m.stone_id, [
            ('Name', m.stone_name),
            ('Tip', 'Purchase |cffff66cc%s|r' % m.stone_name),
            ('Ubertip', _stone_tip(m)),
            ('Description', 'Mega Stone of %s.' % m.base_name),
            ('Art', a.icon_path[m.index]),
            ('Buttonpos', '%d,%d' % (slot % 4, slot // 4)),
        ]))
    for iid, iname, ico, pos, hot in LEGEND_TELE_ITEMS:
        _row_from(s, 'I025', iid, {})
        sections.append(_section(iid, [
            ('Name', iname), ('Hotkey', hot), ('Tip', 'Teleport to |cffffcc00%s [%s]|r' % (iname, hot)),
            ('Ubertip', 'Haunt ' + iname.split("'")[0]), ('Description', 'Haunt ' + iname.split("'")[0]),
            ('Art', ico), ('Buttonpos', pos)]))
    import type_items
    for iid, word, iname, ico in type_items.EXTRA_ITEMS:  # v3.4: held by gym Pokemon of the type
        _row_from(s, 'I00Q', iid, {})
        sections.append(_section(iid, [
            ('Name', iname), ('Tip', iname), ('Ubertip', '%s type item held by gym Pokemon.' % word),
            ('Description', '%s type item.' % word),
            ('Art', 'ReplaceableTextures\\CommandButtons\\%s.blp' % ico)]))
    souls = [w for w in (getattr(a, 'wild_souls', None) or ()) if w.new]
    if souls:
        art = _txt_sections(txt_data.decode('utf-8', 'replace')).get('I01C', {}).get('Art', '')
        for w in souls:  # same item data as the map's legend Souls
            _row_from(s, 'I01C', w.item, {})
            sections.append(_section(w.item, [
                ('Name', '%s Soul' % w.name),
                ('Tip', '%s Soul' % w.name),
                ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to become '
                            '|cffffcc00%s|r.' % (pd.FORM_BY_ID[w.hero].name if w.hero in pd.FORM_BY_ID else w.name)),
                ('Description', 'Soul of a wild %s.' % w.name),
                ('Art', 'ReplaceableTextures\\CommandButtons\\BTNSoul%s.blp' % w.item if _soul_icon(w.item) else art),
            ]))
    return s.to_text().encode('latin-1'), _append_txt(txt_data, sections)


# ------------------------------------------------------------------ abilities
_TEMPLATE_STRING_KEYS = ('Order', 'Missileart', 'Missilespeed', 'MissileHoming', 'MissileArc', 'Casterart',
                         'Casterattach', 'Effectart', 'Specialart', 'Targetart', 'Animnames', 'LightningEffect')


def _soul_icon(item):
    return os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'soul_icons', 'BTNSoul%s.blp' % item))


def _txt_sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith('[') and line.rstrip().endswith(']'):
            cur = line.strip()[1:-1]
            out[cur] = {}
        elif cur and '=' in line:
            k, v = line.split('=', 1)
            out[cur][k] = v
    return out


def _num(v):
    return str(int(v)) if float(v) == int(v) else ('%g' % v)


def _skill_text(t, lv):
    """Template description for one level: {DataA} -> value, {DataA%} -> value as percent."""
    text = t.text
    for stem, vals in t.values.items():
        v = vals[lv - 1]
        text = text.replace('{%s%%}' % stem, '%d%%' % round(v * 100)).replace('{%s}' % stem, _num(v))
    return text


SCALE_TIP = "Damage grows with the hero's main attribute."
_NO_SCALE = ('BUFF', 'CRIT', 'EVADE', 'BASH')  # not damage skills: no scaling line in the tooltip


def _poke_skill(s, strings, sk):
    t = pd.TEMPLATES[sk.template]
    req, pos, hot = pd.SLOTS[sk.slot]
    row = dict(s.find(t.code))
    row[1] = _q(sk.id)
    tmpl_cols = {s.cols[x]: v for x, v in row.items() if x in s.cols}

    def put(col, v):
        row[s.name_to_x[col]] = v

    for col, v in tmpl_cols.items():  # fill level 2/3 columns the template leaves empty
        if col.endswith('1') and col[:-1] + '2' in s.name_to_x:
            for lv in (2, 3):
                if col[:-1] + str(lv) not in tmpl_cols:
                    put(col[:-1] + str(lv), v)
    for col, v in (('hero', '1'), ('item', '0'), ('levels', '3'), ('reqLevel', str(req)), ('levelSkip', '10'),
                   ('checkDep', '0')):
        put(col, v)
    for stem, vals in t.values.items():
        for lv in (1, 2, 3):
            for c in (('Dur', 'HeroDur') if stem == 'Dur' else (stem,)):
                put('%s%d' % (c, lv), _num(vals[lv - 1]))
    if t.cooldown:
        for lv in (1, 2, 3):
            put('Cool%d' % lv, _num(t.cooldown))
            put('Cost%d' % lv, _num(t.mana[lv - 1]))
    s.rows.append(row)
    key = ' [%s]' % hot if hot else ''
    tip = '' if sk.template in _NO_SCALE else ' ' + SCALE_TIP
    pairs = [(k, strings.get(t.code, {})[k]) for k in _TEMPLATE_STRING_KEYS if k in strings.get(t.code, {})]
    pairs = [(k, pd.ELEMENT_ART[sk.element] if k == 'Missileart' else v) for k, v in pairs]
    pairs += [
        ('Name', sk.name),
        ('Art', t.icon), ('Researchart', t.icon.replace('PassiveButtons\\PASBTN', 'CommandButtons\\BTN')),
        ('Buttonpos', pos), ('Researchbuttonpos', pos.split(',')[0] + ',0'),
        ('Tip', ','.join('|cffffcc00%s%s|r - [|cffffcc00Level %d|r]' % (sk.name, key, lv) for lv in (1, 2, 3))),
        ('Ubertip', ','.join('"%s%s"' % (_skill_text(t, lv), tip) for lv in (1, 2, 3))),
        ('Researchtip', '"Learn |cffffcc00%s%s|r - [|cffffcc00Level %%d|r]"' % (sk.name, key)),
        ('Researchubertip', '"%s"' % _skill_text(t, 1)),
    ]
    if hot:
        pairs += [('Hotkey', hot), ('Researchhotkey', hot)]
    return _section(sk.id, pairs)


# v3.2: type icon of the move (PKLegends BTNPkmn<Type>), else the icon of its template
TYPE_ICON = {'fire': 'BTNPkmnFire', 'water': 'BTNPkmnWater', 'grass': 'BTNPkmnGrass', 'electric': 'BTNPkmnElectr',
             'psychic': 'BTNPkmnPsy', 'rock': 'BTNPkmnRock', 'dragon': 'BTNPkmnDragon', 'normal': 'BTNPkmnNormal',
             'fighting': 'BTNPkmnFighting', 'ground': 'BTNPkmnGround', 'flying': 'BTNPkmnFlying',
             'poison': 'BTNPkmnPoison', 'bug': 'BTNPkmnBug', 'ghost': 'BTNPkmnGhost', 'ice': 'BTNPkmnIce',
             'steel': 'BTNPkmnSteel', 'fairy': 'BTNPkmnFairy', 'dark': 'BTNPkmnDark'}


def _move_icon(m, t):
    stem = TYPE_ICON.get(m.type)
    return 'ReplaceableTextures\\CommandButtons\\%s.blp' % stem if stem else t.icon


def _move_skill(s, strings, m, slot):
    """Ability of a learned move in one command-card slot (single level, normal ability, row 0 of the card)."""
    t = pd.TEMPLATES[m.template]
    aid = ld.ability_id(slot, m.index)
    row = dict(s.find(t.code))
    row[1] = _q(aid)

    def put(col, v):
        row[s.name_to_x[col]] = v

    for col, v in (('hero', '0'), ('item', '0'), ('levels', '1'), ('reqLevel', '0'), ('levelSkip', '0'),
                   ('checkDep', '0')):
        put(col, v)
    for stem, vals in t.values.items():
        for c in (('Dur', 'HeroDur') if stem == 'Dur' else (stem,)):
            put('%s1' % c, _num(vals[m.tier - 1]))
    if t.cooldown:
        put('Cool1', _num(t.cooldown))
        put('Cost1', _num(t.mana[m.tier - 1]))
    s.rows.append(row)
    hot = ld.SLOT_HOTKEYS[slot]
    pairs = [(k, strings.get(t.code, {})[k]) for k in _TEMPLATE_STRING_KEYS if k in strings.get(t.code, {})]
    pairs = [(k, pd.ELEMENT_ART[m.type] if k == 'Missileart' else v) for k, v in pairs]
    # every slot gets its own order string: two moves on one hero that share a template (same base ability and
    # order string) made the game cast the first one for both buttons ("press A, skill B fires")
    old_order = dict(pairs).get('Order', '')
    pairs = [(k, v) for k, v in pairs if k != 'Order'] + [('Order', (old_order.strip('"') or 'pkmove') + hot.lower())]
    info = '|n|cffffcc00%s move:|r %s, Power %d.' % (m.cls.capitalize(), m.type.capitalize(), m.power)
    pairs += [
        ('Name', m.name), ('Art', _move_icon(m, t)), ('Buttonpos', '%d,0' % slot), ('Hotkey', hot),
        ('Tip', '|cffffcc00%s [%s]|r' % (m.name, hot)),
        ('Ubertip', '"%s%s %s"' % (_skill_text(t, m.tier), info, SCALE_TIP)),
    ]
    return _section(aid, pairs)


# template -> the damage stems of its description (the numbers the main-attribute multiplier applies to)
DAMAGE_STEMS = {'WAVE': ('DataA',), 'LINE': ('DataA',), 'CONE': ('DataA', 'DataE'), 'CHAIN': ('DataA',),
                'BOLT': ('DataA',), 'DAGGER': ('DataE', 'DataA'), 'STOMP': ('DataA',), 'NOVA': ('DataB', 'DataA'),
                'ULT_WAVE': ('DataA',), 'ULT_LINE': ('DataA',), 'ULT_RAIN': ('DataB',), 'ULT_STAR': ('DataA',),
                'ULT_STOMP': ('DataA',)}


def move_tip_tokens(m):
    """(description with @1 / @2 where a damage number goes, [base damage 1, base damage 2]): the game scales these
    numbers to the hero's current main attribute and level (Mv_Tip in mega.j)."""
    t = pd.TEMPLATES[m.template]
    stems = DAMAGE_STEMS.get(m.template, ())
    text, base = t.text, []
    for k, stem in enumerate(stems, 1):
        text = text.replace('{%s}' % stem, '@%d' % k)
        base.append(int(round(t.values[stem][m.tier - 1])))
    for stem, vals in t.values.items():
        text = text.replace('{%s%%}' % stem, '%d%%' % round(vals[m.tier - 1] * 100)).replace('{%s}' % stem, _num(vals[m.tier - 1]))
    info = '|n|cffffcc00%s move:|r %s, Power %d.' % (m.cls.capitalize(), m.type.capitalize(), m.power)
    return text + info, (base + [0, 0])[:2]


def _ability_objects(s, abilities):
    """Passive info button per Pokemon Ability (command card cell INFO_POS, data-only: DataA1 0) and the item bonus
    abilities that Defense/Speed add to the hero."""
    sections = []
    for i, ab in enumerate(abilities):
        aid = info_id(i)
        _row_from(s, 'AEev', aid, {'hero': '0', 'item': '0', 'levels': '1', 'DataA1': '0'})
        sections.append(_section(aid, [
            ('Name', 'Ability: %s' % ab.name),
            ('Art', ab.icon),
            ('Buttonpos', INFO_POS),
            ('Tip', 'Ability: |cffffcc00%s|r' % ab.name),
            ('Ubertip', ab.text),
        ]))
    for raw, (code, value) in RAW_ABILITIES.items():
        _new_row(s, raw, {'code': _q(code), 'item': '1', 'levels': '1', 'targs1': _q('_'), 'DataA1': str(value)})
        sections.append(_section(raw, [('Name', 'Ability Bonus')]))
    return sections


def _abilities(slk_data, txt_data, a):
    s = slk.Slk(slk_data.decode('latin-1'))
    sections = []
    strings = _txt_sections(txt_data.decode('utf-8', 'replace'))
    if getattr(a, 'poke', None) is not None:
        for kit in pd.KITS.values():
            for sk in kit:
                sections.append(_poke_skill(s, strings, sk))
        for sk in skill_data.new_skills():
            sections.append(_poke_skill(s, strings, sk))
    if getattr(a, 'abilities', None):
        sections += _ability_objects(s, a.abilities)
    if getattr(a, 'moves', None):
        for m in a.moves.moves:
            for slot in range(ld.SLOTS):
                sections.append(_move_skill(s, strings, m, slot))
    for m in MEGAS:
        if m.index not in a.icon_path:
            continue
        _new_row(s, m.evolve_id, {
            'code': _q('ANcl'), 'version': '1', 'useInEditor': '1', 'hero': '0', 'item': '0',
            'race': _q('other'), 'checkDep': '0', 'levels': '1', 'reqLevel': '0', 'levelSkip': '0',
            'priority': '0', 'targs1': _q('_'), 'Cast1': '0', 'Dur1': '0', 'HeroDur1': '0',
            'Cool1': str(int(COOLDOWN)), 'Cost1': '0', 'Area1': '0', 'Rng1': '0',
            'DataA1': '0', 'DataB1': '0', 'DataC1': '1', 'DataD1': '0', 'DataE1': '0', 'DataF1': _q(m.order)})
        y = m.index in Y_VARIANTS
        hot = 'F' if y else 'D'
        sections.append(_section(m.evolve_id, [
            ('Name', 'Mega Evolve'),
            ('Art', a.icon_path[m.index]),
            ('Buttonpos', '0,1' if y else '1,1'),
            ('Hotkey', hot),
            ('Order', m.order),
            ('Tip', 'Mega Evolve - |cffff66cc%s|r |cffffcc00[%s]|r' % (m.name, hot)),
            ('Ubertip', '%s Mega Evolves into |cffff66cc%s|r for %ds: %s.|n|n|cffffcc00Cooldown:|r %ds'
             % (m.base_name, m.name, int(DURATION), _bonus_text(m), int(COOLDOWN))),
        ]))
    for aid, code in zip(BONUS_IDS, ('AIde', 'AIms', 'AIsx')):
        _new_row(s, aid, {'code': _q(code), 'item': '1', 'levels': '1', 'targs1': _q('_'),
                          'DataA1': BONUS_VALUES[aid]})
        sections.append(_section(aid, [('Name', 'Mega Power')]))
    # v3.3: the Poke Center (unit n00P) heals faster: its regeneration aura ACnr, DataA1 = fraction of max HP per second
    row = s.find('ACnr')
    if row is not None:
        x = s.name_to_x['DataA1']
        row[x] = repr(round(float(row[x]) * POKE_CENTER_HEAL_MULT, 4))
    return s.to_text().encode('latin-1'), _append_txt(txt_data, sections)


def apply(files, a):
    out = {W3U: _units(files[W3U], a)}
    out[ITEM_SLK], out[ITEM_TXT] = _items(files[ITEM_SLK], files[ITEM_TXT], a)
    out[ABIL_SLK], out[ABIL_TXT] = _abilities(files[ABIL_SLK], files[ABIL_TXT], a)
    return out
