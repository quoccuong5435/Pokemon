"""Build "Pokemon Arena v<version>.w3x" from "Pokemon Arena v3.3.3.w3x" + v34/war3map.j (made by apply.py).

The v3.3.3 map is the base because its source is lost: every file of it is kept, only these change:
  scripts\\war3map.j                  <- v34/war3map.j
  war3map.w3i                        map name / description with the new version
  war3map.w3u                        + content.py units (8 Mega skins, 3 Pokemon, Zen skin, legend, 211 wild
                                     creeps), Mega Shop lists; mega_look.py models of the 5 Megas without one
  Units\\ItemData.slk, ItemFunc.txt   + 8 Mega Stones, 212 Souls
  Units\\AbilityData.slk              + info buttons of Abilities 69..73 (copies of AB1V), 8 stone abilities
  Units\\CampaignAbilityStrings.txt   + their text; new tooltip text for the 73 Ability buttons; move icons
  war3mapImported\\V34\\..., icons     models / textures / icons from PKLegends v3.2, Soul icons

    python -I tools/v34/apply.py
    python -I tools/v34/check.py                (pjass must pass)
    python -I tools/v34/build_v34.py --dry-run  (everything but writing the map)
    python -I tools/v34/build_v34.py            (writes ../Pokemon Arena v<tools/v34/version.txt>.w3x)
Never overwrites an existing map (the user keeps every version).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WORK = os.path.dirname(TOOLS)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import slk  # noqa: E402
import objects  # noqa: E402
import abilities  # noqa: E402
import mega_look  # noqa: E402
import objdata  # noqa: E402
import content  # noqa: E402
import move_icons  # noqa: E402
import league_area  # noqa: E402

BASE_VERSION = '3.3.3'
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v%s.w3x' % BASE_VERSION)
BASE_SCRIPT = os.path.join(WORK, 'v34', 'war3map_v333.j')
SCRIPT = os.path.join(WORK, 'v34', 'war3map.j')
HASH_SIZE = 4096
KNOWN_NAMES = os.path.join(TOOLS, 'known_names_v18.txt')
DESC = 'v%s: Mega Evolution! Mua Mega Stone o Mega Shop.\x00'
OLD_ABILITIES = 68   # info buttons AB01 .. AB1V exist in the v3.3.3 map


def info_id(n):
    b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return 'AB' + b36[(n - 1) // 36] + b36[(n - 1) % 36]


def patch_w3i(data, version):
    old_name = ('Pokemon Arena v%s\x00' % BASE_VERSION).encode('latin-1')
    old_desc = (DESC % BASE_VERSION).encode('latin-1')
    if old_name not in data or old_desc not in data:
        raise ValueError('w3i: name or description of v%s not found' % BASE_VERSION)
    return data.replace(old_name, ('Pokemon Arena v%s\x00' % version).encode('latin-1')) \
               .replace(old_desc, (DESC % version).encode('latin-1'))


def patch_ability_slk(data, rows):
    s = slk.Slk(data.decode('latin-1'))
    for n, _c, _name, _t in abilities.ABILITIES:
        if n > OLD_ABILITIES and s.find(info_id(n)) is None:
            objects._row_from(s, info_id(OLD_ABILITIES), info_id(n), {})
    for tmpl, new, values in rows:
        if s.find(new) is None:
            objects._row_from(s, tmpl, new, values)
    return s.to_text().encode('latin-1')


def _append_sections(text, sections):
    if not text.endswith('\n'):
        text += '\n'
    for sid, pairs in sections:
        if '[%s]' % sid not in text:
            text += objects._section(sid, pairs)
    return text


def patch_ability_txt(data, sections, icon_rows=()):
    text = data.decode('utf-8')
    text, n_icons = move_icons.patch_strings(text, icon_rows)
    print('move icons: %d ability buttons changed' % n_icons)
    for n, _c, name, info in abilities.ABILITIES:
        sid = info_id(n)
        if '[%s]\n' % sid not in text.replace('\r\n', '\n'):
            continue
        text = re.sub(r'(\[%s\]\r?\n(?:[^\[\r\n][^\r\n]*\r?\n)*?)Ubertip=[^\r\n]*' % sid,
                      lambda m: m.group(1) + 'Ubertip=' + info, text, count=1)
    new = [(info_id(n), [('Name', 'Ability: %s' % name), ('Art', abilities.NEW_ICONS[n]), ('Buttonpos', '3,1'),
                         ('Tip', 'Ability: |cffffcc00%s|r' % name), ('Ubertip', info)])
           for n, _c, name, info in abilities.ABILITIES if n > OLD_ABILITIES]
    return _append_sections(text, new + list(sections)).encode('utf-8')


def _set_keys(text, sid, pairs):
    """set key=value lines inside section [sid] of a txt file (add the key when the section lacks it)"""
    head = text.find('[%s]' % sid)
    if head < 0:
        raise SystemExit('item text [%s] not found' % sid)
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
            lines.append('%s=%s\n' % (k, v))
        sec = ''.join(lines)
    return text[:start] + sec + text[end:]


def patch_items(slk_data, txt_data, rows, sections, mods=(), txt_mods=()):
    s = slk.Slk(slk_data.decode('latin-1'))
    for tmpl, new, values in rows:
        if s.find(new) is None:
            objects._row_from(s, tmpl, new, values)
    for iid, values in mods:  # v3.4.2: change existing items (Pixie Plate)
        row = s.find(iid)
        if row is None:
            raise SystemExit('item %s not found' % iid)
        for col, v in values.items():
            row[s.name_to_x[col]] = v
    text = _append_sections(txt_data.decode('utf-8'), sections)
    for iid, pairs in txt_mods:
        text = _set_keys(text, iid, pairs)
    return s.to_text().encode('latin-1'), text.encode('utf-8')


def patch_units(w3u, c):
    have = {o.id for o in w3u.all()}
    for o in c.objs:
        if o.id in have:
            raise SystemExit('unit id %s already exists in the v3.3.3 map' % o.id)
        w3u.custom.append(o)
    for shop, items in c.shop_add.items():
        o = w3u.find(shop)
        cur = [x for x in (o.get('usei') or '').split(',') if x]
        o.set('usei', objdata.T_STRING, ','.join(cur + [i for i in items if i not in cur]))
        if len(cur) + len(items) > 12:
            raise SystemExit('%s would sell more than 12 items' % shop)


def build(version, out, dry_run=False):
    if os.path.exists(out) and not dry_run:
        raise SystemExit('refusing to overwrite %s (bump tools/v34/version.txt)' % out)
    base = mpq.MPQ(BASE_MAP)
    script = open(SCRIPT, 'rb').read()
    if ('call SetMapName("Pokemon Arena v%s")' % version).encode() not in script:
        raise SystemExit('v34/war3map.j is not for version %s: run tools/v34/apply.py first' % version)
    w3u_data = base.read('war3map.w3u')
    w3u = objdata.ObjFile(w3u_data)
    if w3u.to_bytes() != w3u_data:
        raise SystemExit('war3map.w3u does not round-trip through objdata: not touching it')
    units = {o.id: o for o in w3u.custom}
    c = content.make(open(BASE_SCRIPT, encoding='utf-8').read(), units, base, with_files=True)
    patch_units(w3u, c)
    extra, warns = mega_look.map_files(w3u)
    for w in warns + [r for r in c.report if r.startswith('WARNING')]:
        print('warning:', w)
    item_slk, item_txt = patch_items(base.read(objects.ITEM_SLK), base.read(objects.ITEM_TXT), c.item_rows, c.item_txt,
                                     getattr(c, 'item_mods', ()), getattr(c, 'item_txt_mods', ()))
    files = {
        'scripts\\war3map.j': script,
        'war3map.w3i': patch_w3i(base.read('war3map.w3i'), version),
        'war3map.w3u': w3u.to_bytes(),
        'war3map.w3e': league_area.repaint(base.read('war3map.w3e'))[0],  # v3.4.2: League room floor
        objects.ITEM_SLK: item_slk,
        objects.ITEM_TXT: item_txt,
        objects.ABIL_SLK: patch_ability_slk(base.read(objects.ABIL_SLK), c.abil_rows),
        objects.ABIL_TXT: patch_ability_txt(base.read(objects.ABIL_TXT), c.abil_txt,
                                            move_icons.plan(open(BASE_SCRIPT, encoding='utf-8').read())),
    }
    imported = dict(c.files)
    imported.update(extra)
    clash = [n for n in imported if base.has(n) and base.read(n) != imported[n]]
    if clash:
        raise SystemExit('imported files would replace files of the map: %s' % clash[:10])
    files.update(imported)
    known = [l.strip() for l in open(KNOWN_NAMES, encoding='latin-1') if l.strip()]
    listfile = sorted(set(base.listfile()) | set(files) | set(mpq.discover_names(base, known)))
    for n in sorted(files):
        if n in imported:
            continue
        print('%-36s %9d bytes' % (n, len(files[n])))
    print('imported files: %d (%.1f MB); listfile %d names (hash table %d)'
          % (len(imported), sum(map(len, imported.values())) / 1048576.0, len(listfile), HASH_SIZE))
    if len(listfile) > HASH_SIZE * 0.9:
        raise SystemExit('too many files for the hash table')
    if dry_run:
        print('dry run: nothing written (would write %s)' % out)
        return
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=HASH_SIZE, extra_names=known)
    print('wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    version = open(os.path.join(HERE, 'version.txt')).read().strip()
    build(version, a.out or os.path.join(MAPS, 'Pokemon Arena v%s.w3x' % version), a.dry_run)


if __name__ == '__main__':
    main()
