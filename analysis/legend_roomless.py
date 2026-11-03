"""One-off: Groudon and Buzzwole join the legends; only the legends WITHOUT a room spawn outside (2 every 3 minutes)."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


edit('tools/legend_data.py',
     "('Regirock', 'n00C', 'ISL4'), ('Kyogre', 'n00C', 'ISL5'), ('Jirachi', 'n00C', 'ISL6'),",
     "('Regirock', 'n00C', 'ISL4'), ('Kyogre', 'n00C', 'ISL5'), ('Jirachi', 'n00C', 'ISL6')," + NL +
     "    ('Groudon', 'n00C', 'ISL7'), ('Buzzwole', 'n00C', 'ISL8'),")
edit('tools/legend_data.py',
     "PKL_LEGEND_NAMES = ('Raikou', 'Entei', 'Suicune', 'Ho-Oh', 'Regirock', 'Kyogre', 'Jirachi')",
     "PKL_LEGEND_NAMES = ('Raikou', 'Entei', 'Suicune', 'Ho-Oh', 'Regirock', 'Kyogre', 'Jirachi', 'Groudon', 'Buzzwole')" + NL +
     "# legends that have a room (teleport item in the Haunt Legendary shop): they stay in their rooms" + NL +
     "ROOM_LEGENDS = ('Articuno', 'Moltres', 'Lugia', 'Darkrai', 'Mew', 'Mewtwo', 'Giratina', 'Deoxys', 'Arceus', 'Rayquaza'," + NL +
     "                'Celebi')")
edit('tools/legend_data.py', ')]' + NL, ')]' + NL + NL +
     "# v3.3: only the legends without a room spawn outside, 2 every 3 minutes (no duplicates)" + NL +
     "SPAWN_LEGENDS = [lg for lg in LEGENDS if lg.name not in ROOM_LEGENDS]" + NL)
edit('tools/poke_data.py', "LEGENDARY_NAMES = {'Entei', 'Ho-Oh', 'Jirachi', 'Kyogre', 'Raikou', 'Regirock', 'Suicune'}",
     "LEGENDARY_NAMES = {'Entei', 'Ho-Oh', 'Jirachi', 'Kyogre', 'Raikou', 'Regirock', 'Suicune', 'Groudon', 'Buzzwole'}")
edit('tools/build_v2.py', 'a.legends = legend_data.LEGENDS', 'a.legends = legend_data.SPAWN_LEGENDS')
print('ok')
