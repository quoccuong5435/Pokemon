"""One-off: wire tools/v34/move_icons.py into build_v34.py (Art= of the move abilities) and apply.py (table doc)."""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:70])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


edit('tools/v34/build_v34.py', [
    ("import content  # noqa: E402\n", "import content  # noqa: E402\nimport move_icons  # noqa: E402\n"),
    ("def patch_ability_txt(data, sections):\n    text = data.decode('utf-8')\n",
     "def patch_ability_txt(data, sections, icon_rows=()):\n    text = data.decode('utf-8')\n"
     "    text, n_icons = move_icons.patch_strings(text, icon_rows)\n"
     "    print('move icons: %d ability buttons changed' % n_icons)\n"),
    ("        objects.ABIL_TXT: patch_ability_txt(base.read(objects.ABIL_TXT), c.abil_txt),",
     "        objects.ABIL_TXT: patch_ability_txt(base.read(objects.ABIL_TXT), c.abil_txt,\n"
     "                                            move_icons.plan(open(BASE_SCRIPT, encoding='utf-8').read())),"),
    ("new tooltip text for the 73 Ability buttons\n", "new tooltip text for the 73 Ability buttons; move icons\n"),
])
edit('tools/v34/apply.py', [(
    "    report = extra.report + report\n",
    "    report = extra.report + report\n"
    "    import move_icons  # the table of the move icons build_v34 writes\n"
    "    rows = move_icons.plan(base)\n"
    "    move_icons.write_doc(rows, os.path.join(WORK, 'docs', 'v3.4-move-icons.md'))\n"
    "    report.append('move icons: %d by name, %d by type (docs/v3.4-move-icons.md)'\n"
    "                  % (sum(1 for r in rows if r[4] == 'name'), sum(1 for r in rows if r[4] != 'name')))\n")])
