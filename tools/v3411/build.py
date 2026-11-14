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

BASE_MAP = apply.BASE_MAP


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
    for k in range(1, 6):
        new = 'AB2%d' % k
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
    files['Units\\AbilityData.slk'] = abil.to_text().encode('latin-1')
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    for new, tmpl, name, ty, icon, desc in buttons:
        tm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % tmpl, strings, re.S)
        hot = re.search(r'\[(\w)\]', re.search(r'(?m)^Tip=(.*)$', tm.group(1)).group(1)).group(1)
        strings = copy_section(strings, tmpl, new)
        strings = set_keys(strings, new, [('Name', name), ('Art', SM.ICON % icon),
                                          ('Tip', '|cffffcc00%s [%s]|r' % (name, hot)),
                                          ('Ubertip', '"%s|n|cffffcc00Status move:|r %s."' % (desc, ty.capitalize()))])
    for k, (idx, name, info) in enumerate(apply.NEW_ABILITIES, 1):
        new = 'AB2%d' % k
        strings = copy_section(strings, 'AB20', new)
        strings = set_keys(strings, new, [('Name', 'Ability: %s' % name), ('Tip', 'Ability: |cffffcc00%s|r' % name),
                                          ('Ubertip', '"%s"' % info)])
    files['Units\\CampaignAbilityStrings.txt'] = strings.encode('utf-8')
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
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'))
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
