"""v3.4.11: write the map = the v3.4.10 map + v3411/war3map.j (tools/v3411/apply.py) + object data changes.

    python -I tools/v3411/build.py --dry-run
    python -I tools/v3411/build.py           -> ..\\Pokemon Arena v<version>.w3x (never overwrites)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)
import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402
import league_area  # noqa: E402
import apply  # noqa: E402
import status_moves as SM  # noqa: E402
import fx_more  # noqa: E402
import starters  # noqa: E402
import megas  # noqa: E402

BASE_MAP = apply.BASE_MAP

# v3.4.16: buff bar icons AF1A.. / BF1A.. (order = Fx_IconUp / Fx_IconDown / Fx_IconStatus / Conf / Acc in fx_globals.j)
_STAT = ('Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed')
_UP = ('BTNSteelMelee', 'BTNHumanArmorUpOne', 'BTNSorceressMaster', 'BTNSpellShieldAmulet', 'BTNBootsOfSpeed')
_DOWN = ('BTNCripple', 'BTNFaerieFire', 'BTNCurse', 'BTNSilence', 'BTNSlow')
STAGE_ICONS = ([('|cff66ff66%s raised|r' % n, '%s stage above 0 (type -stats for the stage and the time left).' % n, i)
                for n, i in zip(_STAT, _UP)] +
               [('|cffff6666%s lowered|r' % n, '%s stage below 0 (type -stats for the stage and the time left).' % n, i)
                for n, i in zip(_STAT, _DOWN)] +
               [('|cffffcc66Burn|r', 'Burned: loses HP over time, physical damage -25%.', 'BTNImmolationOn'),
                ('|cffffcc66Poison|r', 'Poisoned: loses HP over time.', 'BTNEnvenomedSpear'),
                ('|cffffcc66Bad poison|r', 'Badly poisoned: loses more HP every second.', 'BTNOrbOfVenom'),
                ('|cffffcc66Paralysis|r', 'Paralyzed: slower, may be stopped for a moment.', 'BTNPurge'),
                ('|cffffcc66Sleep|r', 'Asleep: cannot act.', 'BTNSleep'),
                ('|cffffcc66Freeze|r', 'Frozen: cannot act.', 'BTNFrost'),
                ('|cffcc88ffConfused|r', 'Confused: attacks may hit itself.', 'BTNPossession'),
                ('|cffff6666Accuracy down|r', 'Attacks and moves miss 30% of the time.', 'BTNEnsnare')])


def set_keys(text, sid, pairs):
    head = text.find('[%s]' % sid)
    if head < 0:
        raise SystemExit('text section [%s] not found' % sid)
    start = text.find('\n', head) + 1
    nxt = text.find('\n[', start)
    end = len(text) if nxt < 0 else nxt + 1
    sec = text[start:end]
    for k, v in pairs:
        lines = sec.splitlines(True)
        for i, ln in enumerate(lines):
            if ln.split('=', 1)[0] == k:
                lines[i] = '%s=%s%s' % (k, v, '\r\n' if ln.endswith('\r\n') else '\n')
                break
        else:
            lines.append('%s=%s\r\n' % (k, v))
        sec = ''.join(lines)
    return text[:start] + sec + text[end:]


def copy_section(text, src, new):
    m = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % src, text, re.S)
    if not m:
        raise SystemExit('text section [%s] not found' % src)
    if '[%s]' % new in text:
        return text
    return text.rstrip('\r\n') + '\r\n[%s]\r\n%s\r\n' % (new, m.group(1).strip('\r\n'))


def ak_id(m):
    dig = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return 'AK' + dig[m // 36] + dig[m % 36]


def build(out, dry):
    p = json.load(open(os.path.join(apply.OUT_DIR, 'plan.json'), encoding='utf-8'))
    script = open(os.path.join(apply.OUT_DIR, 'war3map.j'), encoding='latin-1').read()
    if 'Fx_Init' not in script:
        raise SystemExit('run tools/v3411/apply.py first')
    base = mpq.MPQ(BASE_MAP)
    ip = p['items']
    files = {}
    # ---- script
    files['scripts\\war3map.j'] = script.encode('latin-1')
    # ---- items: type items keep only their stat abilities (the effects are code now); names, texts, prices
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    for iid, al in ip['abil_lists'].items():
        row = items.find(iid)
        if row is None:
            raise SystemExit('item %s not found' % iid)
        row[items.name_to_x['abilList']] = '"%s"' % ','.join(al)
    row = items.find('ITFY')
    row[items.name_to_x['goldcost']] = str(ip['prices']['ITFY'])
    # v3.4.16: stat vitamins (Carbos / Calcium / Protein x5, HP Up, Calcium, Protein, Carbos) without a shop limit
    for iid in ('I000', 'I001', 'I002', 'I003', 'I004', 'I005', 'I006'):
        row = items.find(iid)
        if row is None:
            raise SystemExit('item %s not found' % iid)
        row[items.name_to_x['stockMax']] = '99'
        row[items.name_to_x['stockStart']] = '99'
        row[items.name_to_x['stockRegen']] = '1'
    files['Units\\ItemData.slk'] = items.to_text().encode('latin-1')
    func = base.read('Units\\ItemFunc.txt').decode('utf-8', 'replace')
    for t, (iid, word) in ip['type_items'].items():
        txt = '+20% damage; ' + word + ' moves +20%. ' + apply.ITEM_TEXT[word] + \
              '|n|n|cffffcc00Equip with ' + word + ' Pokemon|r'
        func = set_keys(func, iid, [('Ubertip', '"%s"' % txt)])
    func = set_keys(func, 'I013', [('Name', 'Soft Sand'), ('Tip', 'Purchase Soft Sand')])
    func = set_keys(func, 'ITGD', [('Ubertip', '"Ground type item held by gym Pokemon (+20% damage; ' +
                                    apply.ITEM_TEXT['Ground'] + ')"')])
    func = set_keys(func, 'IL01', [('Name', 'Pokemon League'), ('Tip', 'Teleport to the |cffffcc00Pokemon League|r'),
                                   ('Ubertip', '"Takes you to the lobby of the Pokemon League (Elite Four and Champion,'
                                               ' 8 badges needed to battle)."')])
    files['Units\\ItemFunc.txt'] = func.encode('utf-8')
    # ---- abilities: no borrowed stun / slow on the move spells, quicker priority moves, 5 new info buttons
    abil = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    col = abil.name_to_x
    changed = 0
    for mi, rec in p['moves'].items():
        row = abil.find(ak_id(int(mi)))
        if row is None:
            continue
        code = abil.get(row, 'code')
        if code in ('AHtb', 'AOws', 'AUim', 'AUfn'):
            row[col['Dur1']] = '0.01'
            row[col['HeroDur1']] = '0.01'
            changed += 1
        elif code == 'AEsh':
            row[col['DataB1']] = '0'
            if 'DataC1' in col:
                row[col['DataC1']] = '0'
            changed += 1
        elif code == 'AHtc':
            row[col['DataC1']] = '0'
            row[col['DataD1']] = '0'
            changed += 1
        if rec['flags'] & apply.F_PRIO:
            cd = abil.get(row, 'Cool1')
            if cd:
                row[col['Cool1']] = '%g' % round(float(cd) * 0.7, 2)
    tmpl = abil.find('AB20')
    dig36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    info_id = lambda idx: 'AB' + dig36[(idx - 1) // 36] + dig36[(idx - 1) % 36]  # noqa: E731 (= Ab_InfoId)
    for idx, _n, _i in apply.NEW_ABILITIES:
        new = info_id(idx)
        if abil.find(new) is None:
            r = dict(tmpl)
            r[1] = '"%s"' % new
            abil.rows.append(r)
    # v3.4.12: the slot buttons of the 58 status moves (copies of Double Team's / a unit-target move's buttons)
    dig = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    templates = {0: ('AV8V', 'AW8V', 'AY8V', 'AZ8V'), 1: ('AV00', 'AW00', 'AY00', 'AZ00')}
    buttons = []
    for k, (name, ty, _act, tt, _params, cd, mana, icon, desc) in enumerate(SM.MOVES):
        mi = SM.STAT_BASE + k
        for slot, letter in enumerate('VWYZ'):
            new = 'A%s%s%s' % (letter, dig[mi // 36], dig[mi % 36])
            tmpl = templates[tt][slot]
            if abil.find(new) is None:
                r = dict(abil.find(tmpl))
                r[1] = '"%s"' % new
                r[col['Cool1']] = str(cd)
                r[col['Cost1']] = str(mana)
                if tt == 1:
                    r[col['Rng1']] = '600'
                    r[col['targs1']] = '"air,ground,enemy,neutral"'
                abil.rows.append(r)
            buttons.append((new, tmpl, name, ty, icon, desc))
    # v3.4.16 (fx_more.py): the moves with new effects use the art-less buff copies of v3.4.9
    fxm = p.get('fx_more') or {}
    buff_cols = [c for c in col if re.match(r'(BuffID|EfctID)\d+$', c)]
    for mv in fxm.get('moves', []):
        row = abil.find(mv['aid'])
        if row is None:
            raise SystemExit('fx_more: ability %s not found' % mv['aid'])
        for c in buff_cols:
            v = abil.get(row, c)
            if v:
                nv = ','.join(fx_more.BUFF_COPY.get(b, b) for b in v.split(','))
                if nv != v:
                    row[col[c]] = '"%s"' % nv
    # v3.4.16: hidden bonuses (stages as green / red numbers) and self-only auras (buff bar icons)
    bonus_new, icon_new = [], []
    for new, tmpl in (('AF0A', 'A08H'), ('AF0D', 'AId2'), ('AF0S', 'AMB3')):
        if abil.find(new) is None:
            r = dict(abil.find(tmpl))
            r[1] = '"%s"' % new
            r[col['levels']] = '2'
            r[col['item']] = '1'
            for c in ('DataA1', 'DataA2'):
                r[col[c]] = '0'
            abil.rows.append(r)
            bonus_new.append((new, tmpl))
    buffs = slk.Slk(base.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    for k, (_tip, _txt, _icon) in enumerate(STAGE_ICONS):
        aid, bid = 'AF1' + chr(65 + k), 'BF1' + chr(65 + k)
        if abil.find(aid) is None:
            r = dict(abil.find('AOae'))
            r[1] = '"%s"' % aid
            r[col['levels']] = '1'
            r[col['item']] = '1'
            r[col['hero']] = '0'
            r[col['DataA1']] = '0'
            r[col['DataB1']] = '0'
            r[col['Area1']] = '10'
            r[col['targs1']] = '"self"'
            r[col['BuffID1']] = '"%s"' % bid
            abil.rows.append(r)
        if buffs.find(bid) is None:
            r = dict(buffs.find('BOae'))
            r[1] = '"%s"' % bid
            buffs.rows.append(r)
        icon_new.append((aid, bid, k))
    files['Units\\AbilityBuffData.slk'] = buffs.to_text().encode('latin-1')
    files['Units\\AbilityData.slk'] = abil.to_text().encode('latin-1')
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    for new, tmpl, name, ty, icon, desc in buttons:
        tm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % tmpl, strings, re.S)
        hot = re.search(r'\[(\w)\]', re.search(r'(?m)^Tip=(.*)$', tm.group(1)).group(1)).group(1)
        strings = copy_section(strings, tmpl, new)
        strings = set_keys(strings, new, [('Name', name), ('Art', SM.ICON % icon),
                                          ('Tip', '|cffffcc00%s [%s]|r' % (name, hot)),
                                          ('Ubertip', '"%s|n|cffffcc00Status move:|r %s."' % (desc, ty.capitalize()))])
    for idx, name, info in apply.NEW_ABILITIES:
        new = info_id(idx)
        strings = copy_section(strings, 'AB20', new)
        strings = set_keys(strings, new, [('Name', 'Ability: %s' % name), ('Tip', 'Ability: |cffffcc00%s|r' % name),
                                          ('Ubertip', '"%s"' % info)])
    # v3.4.16: texts of the hidden bonuses and of the buff icons
    for new, tmpl in bonus_new:
        strings = copy_section(strings, tmpl, new)
        strings = set_keys(strings, new, [('Name', 'Stage bonus'), ('EditorSuffix', '(v3.4.16)')])
    for aid, bid, k in icon_new:
        tip, txt, icon = STAGE_ICONS[k]
        strings = copy_section(strings, 'AOae', aid)
        strings = set_keys(strings, aid, [('Name', tip), ('Targetart', ''), ('Casterart', ''), ('Areaeffectart', ''),
                                          ('Specialart', '')])
        strings = copy_section(strings, 'BOae', bid)
        strings = set_keys(strings, bid, [('Bufftip', tip), ('Buffubertip', '"%s"' % txt),
                                          ('Buffart', 'ReplaceableTextures\\CommandButtons\\%s.blp' % icon),
                                          ('Targetart', ''), ('Effectart', ''), ('Specialart', '')])
    # v3.4.16: old art off on the moves with new effects; melee missile moves travel at the dash speed
    for mv in fxm.get('moves', []):
        pairs = [(k, '') for k in fx_more.ART_KEYS]
        if mv['melee'] and mv['base'] in fx_more.MISSILE_BASES:
            pairs.append(('Missilespeed', '%d' % int(mv['dash'])))
        strings = set_keys(strings, mv['aid'], pairs)
    files['Units\\CampaignAbilityStrings.txt'] = strings.encode('utf-8')
    # v3.4.16: Pokemon World effect models (+ textures)
    if fxm.get('pw_models'):
        have = {n.lower() for n in base.listfile()}
        for path, data in fx_more.pw_files(fxm['pw_models']).items():
            if path.lower() in have and base.read(path) != data:
                raise SystemExit('fx_more: %s already in the map with other content' % path)
            if path.lower() not in have:
                files[path] = data
    # v3.4.16: starter models / icons and trainer models for the gym leaders / Elite Four
    have = {n.lower() for n in base.listfile()}
    for path, data in starters.files().items():
        if path.lower() in have and base.read(path) != data:
            raise SystemExit('starter: %s already in the map with other content' % path)
        if path.lower() not in have and path not in files:
            files[path] = data
    for path, data in fx_more.trainer_files().items():
        if path.lower() in have and base.read(path) != data:
            raise SystemExit('trainer: %s already in the map with other content' % path)
        if path.lower() not in have and path not in files:
            files[path] = data
    # ---- units: Darkrai as a random legend (nL19), Pixie Plate in Super Mart 2
    w3u_data = base.read('war3map.w3u')
    w3u = objdata.ObjFile(w3u_data)
    if w3u.to_bytes() != w3u_data:
        raise SystemExit('w3u does not round-trip')
    have = {o.new for o in w3u.custom}
    if 'nL19' not in have:
        src = next(o for o in w3u.custom if o.new == 'n00F')
        o = objdata.Obj(src.orig, 'nL19', [objdata.Mod(x.field, x.type, x.value, x.level, x.data, x.end)
                                            for x in src.mods])
        for md in o.mods:
            if md.field == 'unam':
                md.value = 'Wild Darkrai'
        w3u.custom.append(o)
    # v3.4.16: gym leaders / Elite Four NPCs (villager base: no attack, invulnerable, cannot move)
    for k, (who, model, _hi, _win) in enumerate(fx_more.TRAINERS):
        nid = fx_more.TRAINER_ID[k]
        if nid in have:
            raise SystemExit('unit id %s already used' % nid)
        title = 'Gym Leader %s' % who if k < 8 else ('Champion %s' % who if k == 12 else 'Elite Four %s' % who)
        w3u.custom.append(objdata.Obj('nvil', nid, [
            objdata.Mod('unam', 3, title), objdata.Mod('umdl', 3, 'PkFx\\Trainer\\%s.mdx' % model),
            objdata.Mod('uabi', 3, 'Avul'), objdata.Mod('umvs', 0, 0),
            objdata.Mod('usca', 1, fx_more.TRAINER_SCALE.get(model, 1.4))]))
    # v3.4.16: Team Rocket NPCs (Jessie, a grunt) of the raid event
    for nid, who, model, scale in fx_more.ROCKET_NPC:
        if nid in have:
            raise SystemExit('unit id %s already used' % nid)
        w3u.custom.append(objdata.Obj('nvil', nid, [
            objdata.Mod('unam', 3, who), objdata.Mod('umdl', 3, 'PkFx\\Trainer\\%s.mdx' % model),
            objdata.Mod('uabi', 3, 'Avul'), objdata.Mod('umvs', 0, 0), objdata.Mod('usca', 1, float(scale))]))
    # v3.4.16: skins of the regional forms (only their model / scale are used, via BlzSetUnitSkin)
    for nid, f, scale in fx_more.regional_skins():
        if nid in have:
            raise SystemExit('unit id %s already used' % nid)
        w3u.custom.append(objdata.Obj('nvil', nid, [
            objdata.Mod('unam', 3, 'Regional skin %s' % f), objdata.Mod('umdl', 3, 'PkFx\\Regional\\%s.mdx' % f),
            objdata.Mod('uabi', 3, 'Avul'), objdata.Mod('usca', 1, float(scale))]))
    n_start = starters.unit_objects(w3u, objdata)  # v3.4.16: 33 starter heroes
    # v3.4.16: Megas of Swampert, Sableye, Garchomp, Abomasnow (items, abilities, skins, shops)
    m_abil = slk.Slk(files['Units\\AbilityData.slk'].decode('latin-1'))
    m_items = slk.Slk(files['Units\\ItemData.slk'].decode('latin-1'))
    m_str, m_func = megas.objects(w3u, objdata, m_abil, m_items,
                                  files['Units\\CampaignAbilityStrings.txt'].decode('utf-8'),
                                  files['Units\\ItemFunc.txt'].decode('utf-8'), set_keys, copy_section)
    files['Units\\AbilityData.slk'] = m_abil.to_text().encode('latin-1')
    files['Units\\ItemData.slk'] = m_items.to_text().encode('latin-1')
    files['Units\\CampaignAbilityStrings.txt'] = m_str.encode('utf-8')
    # v3.4.16 Dynamax Band (item IDMX, its ability ADMX: copies of a Mega Stone / Mega Evolve with their own order)
    if m_abil.find('ADMX') is not None or m_items.find('IDMX') is not None:
        raise SystemExit('Dynamax ids already used')
    row = dict(m_abil.find('AM0W'))
    row[1] = '"ADMX"'
    row[m_abil.name_to_x['DataF1']] = '"robogoblin"'
    row[m_abil.name_to_x['Cool1']] = '150'
    m_abil.rows.append(row)
    row = dict(m_items.find('IM0W'))
    row[1] = '"IDMX"'
    row[m_items.name_to_x['abilList']] = '"ADMX"'
    row[m_items.name_to_x['goldcost']] = '8000'
    m_items.rows.append(row)
    dyn_icon = 'ReplaceableTextures\\CommandButtons\\BTNBerserk.blp'
    dyn_text = ('Dynamax for 20s: twice as big, +50% max HP, every move is a Max Move (+50% damage and a big blast'
                ' of its type). Cooldown 150s. Pokemon of level 20 or more.')
    m_str = copy_section(m_str, 'AM0W', 'ADMX')
    m_str = set_keys(m_str, 'ADMX', [('Name', 'Dynamax'), ('Art', dyn_icon), ('Tip', '|cffff5080Dynamax|r'),
                                     ('Ubertip', '"%s"' % dyn_text), ('Order', 'robogoblin')])
    m_func = copy_section(m_func, 'IM0W', 'IDMX')
    m_func = set_keys(m_func, 'IDMX', [('Name', 'Dynamax Band'), ('Tip', 'Purchase |cffff5080Dynamax Band|r'),
                                       ('Ubertip', '"|cffffcc00Use (click in the inventory):|r %s"' % dyn_text),
                                       ('Description', 'Lets a Pokemon Dynamax again and again.'), ('Art', dyn_icon)])
    for md in next(o for o in w3u.custom if o.new == 'n00Q').mods:
        if md.field == 'usei' and 'IDMX' not in md.value:
            md.value = md.value + ',IDMX'
    m_func = starters.wild_objects(w3u, objdata, m_items, m_func, set_keys, copy_section)  # v3.4.16
    files['Units\\ItemData.slk'] = m_items.to_text().encode('latin-1')
    files['Units\\ItemFunc.txt'] = m_func.encode('utf-8')
    shop = next(o for o in w3u.custom if o.new == 'n00Q')
    for md in shop.mods:
        if md.field == 'usei' and 'ITFY' not in md.value:
            md.value = md.value + ',ITFY'
    files['war3map.w3u'] = w3u.to_bytes()
    # ---- terrain of the League room, map name
    w3e, n = league_area.repaint(base.read('war3map.w3e'))
    files['war3map.w3e'] = w3e
    w3i = base.read('war3map.w3i')
    if b'v3.4.10' not in w3i:
        raise SystemExit('w3i: version text not found')
    files['war3map.w3i'] = w3i.replace(b'v3.4.10', ('v' + p['version']).encode('latin-1')[:7].ljust(7, b' '))
    print('move spells without borrowed stun / slow: %d; League room tiles repainted: %d; status move buttons: %d'
          % (changed, n, len(buttons)))
    for name in sorted(files):
        print('%-36s %9d bytes' % (name, len(files[name])))
    if dry:
        print('dry run: nothing written (would write %s)' % out)
        return
    if os.path.exists(out):
        raise SystemExit('refusing to overwrite %s' % out)
    listfile = sorted(set(base.listfile()) | set(files))
    # v3.4.16: ~440 new files no longer fit the 4096-slot hash table of the 3.4.10 map
    # the 3.4.10 map has a full listfile: re-lay the table by those names only (discover_names would read every file
    # of the 150 MB map looking for more names, too slow); entries without a known name are still kept (mpq copies
    # them to every candidate home slot)
    v18 = [x.strip() for x in open(os.path.join(HERE, 'names_v3410.txt'), encoding='latin-1') if x.strip()]
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra) | set(v18)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print('hash table: %d slots' % hsize)
    print('wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    version = open(os.path.join(HERE, 'version.txt')).read().strip()
    build(a.out or os.path.join(MAPS, 'Pokemon Arena v%s.w3x' % version), a.dry_run)


if __name__ == '__main__':
    main()
