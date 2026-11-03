"""One-off: 7 PKLegends legends (Raikou, Entei, Suicune, Ho-Oh, Regirock, Kyogre, Jirachi) join the random legends.
Each is a clone of a legend boss with the PKLegends model, has an own Soul (ISL0..ISL6) that turns a Pokemon into the
playable form, and the 22 legends spawn without duplicates."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# legend list
edit('tools/legend_data.py',
     "('Dialga', 'n033', 'I01V'), ('Palkia', 'n034', 'I01W'), ('Celebi', 'n035', 'ISCE'),",
     "('Dialga', 'n033', 'I01V'), ('Palkia', 'n034', 'I01W'), ('Celebi', 'n035', 'ISCE')," + NL +
     "    # v3.3: PKLegends legends (boss template n00C, PKLegends model); Souls ISL0.. turn a Pokemon into the playable form" + NL +
     "    ('Raikou', 'n00C', 'ISL0'), ('Entei', 'n00C', 'ISL1'), ('Suicune', 'n00C', 'ISL2'), ('Ho-Oh', 'n00C', 'ISL3')," + NL +
     "    ('Regirock', 'n00C', 'ISL4'), ('Kyogre', 'n00C', 'ISL5'), ('Jirachi', 'n00C', 'ISL6'),")
edit('tools/legend_data.py', 'LEGENDS = [Legend(i, *r)',
     "PKL_LEGEND_NAMES = ('Raikou', 'Entei', 'Suicune', 'Ho-Oh', 'Regirock', 'Kyogre', 'Jirachi')" + NL + NL +
     'LEGENDS = [Legend(i, *r)')

# Souls of the PKL legends
edit('tools/wild_data.py',
     "    out.append(WildSoul('Celebi', poke_data.CELEBI_HERO, 'ISCE', True, ()))  # v3.3: Soul of the Celebi legend" + NL,
     "    out.append(WildSoul('Celebi', poke_data.CELEBI_HERO, 'ISCE', True, ()))  # v3.3: Soul of the Celebi legend" + NL +
     "    import legend_data" + NL +
     "    for k, lg in enumerate(n for n in legend_data.PKL_LEGEND_NAMES):  # v3.3: Souls of the PKLegends legends" + NL +
     "        form = next(f for f in poke_data.FORMS if f.name == lg)" + NL +
     "        out.append(WildSoul(lg, poke_data.base_form_id(form.id), 'ISL%d' % k, True, ()))" + NL)

# the legend clone gets the PKLegends model
edit('tools/objects.py',
     "        o.set('unam', T_STRING, 'Wild %s' % leg.name)" + NL + "        f.custom.append(o)" + NL,
     "        o.set('unam', T_STRING, 'Wild %s' % leg.name)" + NL +
     "        poke = getattr(a, 'poke', None)" + NL +
     "        if leg.name in legend_data.PKL_LEGEND_NAMES and poke is not None:  # v3.3: PKLegends model, icon and scale" + NL +
     "            form = next(x for x in pd.FORMS if x.name == leg.name)" + NL +
     "            o.set('umdl', T_STRING, poke.model_path[form.id])" + NL +
     "            o.set('uico', T_STRING, poke.icon_path[form.id])" + NL +
     "            o.set('usca', T_REAL, float(poke.scale[form.id]) * 1.5)" + NL +
     "        f.custom.append(o)" + NL)
edit('tools/objects.py', 'import learn_data as ld' + NL, 'import learn_data as ld' + NL + 'import legend_data' + NL)
print('ok')
