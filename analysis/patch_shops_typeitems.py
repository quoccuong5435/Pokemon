"""One-off (v3.4.2): fixed spots for Battle Shop / Item Shop inside both bases, Ground and Fairy type items
(Soft Sand registered, Pixie Plate sold in Super Mart 2 with its own effect), item text fixes."""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


edit('tools/v34/extras.py', [
    ("""    spots = [(-5392, -544), (-6304, -544), (-5088, -544), (-5392, -848), (-5696, -848), (-6000, -848),
             (-6304, -848), (-5088, -848), (-4784, -544), (-4784, -848)]""",
     """    # v3.4.2: the shop rows of a base (y = +-544: Poke Mart / Super Marts, Mega Shops) are full and the first spots
    # of v3.4.0 sat on Mega Shop III / Haunt Legendary: the free band between the rows, either side of the walkway
    # from the Poke Center to the door (checked walkable in war3map.wpm, analysis/base_layout.py)
    spots = [(-5696, 288), (-5696, -288), (-5392, 288), (-5392, -288), (-5904, 288), (-5904, -288)]"""),
    ("""    # ---------------- Elite Four and Champion""",
     """    # ---------------- v3.4.2: type items for all 18 types (Ground: Soft Sand was not registered; Fairy had none)
    c.item_mods = [('ITFY', {'abilList': '"A03C,A03A"', 'goldcost': '3000', 'stockMax': '1', 'stockRegen': '60'})]
    c.item_txt_mods = [
        ('ITFY', [('Name', 'Pixie Plate'), ('Tip', 'Purchase |cffffcc00Pixie Plate|r'),
                  ('Ubertip', 'Raise 20% damage and recover 50 HP per second.|n|n|cffffcc00Equip with Fairy Pokemon|r'),
                  ('Description', 'Equip with Fairy Pokemon.'), ('Buttonpos', '2,1')]),
        ('I013', [('Name', 'Soft Sand'), ('Tip', 'Purchase |cffffcc00Soft Sand [Z]|r')]),
        ('I01X', [('Ubertip', 'Raise 20% damage and 15 armor.|n|n|cffffcc00Equip with Steel Pokemon. Onix and Scyther '
                              'evolve with it (they may buy it).|r')]),
    ]
    c.shop_add.setdefault('n00Q', []).append('ITFY')
    c.report.append('type items: Ground (I013 Soft Sand) and Fairy (ITFY Pixie Plate, Super Mart 2) added')

    # ---------------- Elite Four and Champion"""),
])

edit('tools/v34/build_v34.py', [
    ("""def patch_items(slk_data, txt_data, rows, sections):
    s = slk.Slk(slk_data.decode('latin-1'))
    for tmpl, new, values in rows:
        if s.find(new) is None:
            objects._row_from(s, tmpl, new, values)
    return s.to_text().encode('latin-1'), _append_sections(txt_data.decode('utf-8'), sections).encode('utf-8')""",
     """def _set_keys(text, sid, pairs):
    \"\"\"set key=value lines inside section [sid] of a txt file (add the key when the section lacks it)\"\"\"
    head = text.find('[%s]' % sid)
    if head < 0:
        raise SystemExit('item text [%s] not found' % sid)
    start = text.find('\\n', head) + 1
    nxt = text.find('\\n[', start)
    end = len(text) if nxt < 0 else nxt + 1
    sec = text[start:end]
    for k, v in pairs:
        lines = sec.splitlines(True)
        for i, ln in enumerate(lines):
            if ln.split('=', 1)[0] == k:
                lines[i] = '%s=%s%s' % (k, v, '\\r\\n' if ln.endswith('\\r\\n') else '\\n')
                break
        else:
            lines.append('%s=%s\\n' % (k, v))
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
    return s.to_text().encode('latin-1'), text.encode('utf-8')"""),
    ("""    item_slk, item_txt = patch_items(base.read(objects.ITEM_SLK), base.read(objects.ITEM_TXT), c.item_rows, c.item_txt)""",
     """    item_slk, item_txt = patch_items(base.read(objects.ITEM_SLK), base.read(objects.ITEM_TXT), c.item_rows, c.item_txt,
                                     getattr(c, 'item_mods', ()), getattr(c, 'item_txt_mods', ()))"""),
])

edit('tools/v34/apply.py', [
    ("""TYPE_SELL_OLD = """,
     """# v3.4.2: type items for all 18 types (Soft Sand was sold but not registered as Ground; Fairy had no item)
TYPE_INIT_OLD = '    set Type_N = 16\\n'
TYPE_INIT_NEW = ('    set Type_N = 18\\n'
                 "    set Type_Item[16] = 'I013'\\n"
                 '    set Type_Word[16] = "Ground"\\n'
                 '    set Type_Cost[16] = 3000\\n'
                 "    set Type_Item[17] = 'ITFY'\\n"
                 '    set Type_Word[17] = "Fairy"\\n'
                 '    set Type_Cost[17] = 3000\\n')
TYPE_SELL_OLD = """),
    ("""    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
""", """    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
    script = replace_once(script, TYPE_INIT_OLD, TYPE_INIT_NEW)
"""),
])
