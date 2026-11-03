"""One-off: Celebi as a playable hero (PZZA, model/icon of the boss n035), its Soul (ISCE), a random legend, a teleport."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# ---- Celebi hero id and soul
edit('tools/poke_data.py', 'PKL_TEMPLATE = ',
     "CELEBI_HERO = 'PZZA'  # v3.3: playable Celebi (the Soul of the random legend Celebi turns a Pokemon into it)" + NL +
     'PKL_TEMPLATE = ')

# wild_data.wild_souls: the Celebi Soul
edit('tools/wild_data.py',
     "        out.append(WildSoul(name, heroes[name.lower()], item, new, tuple(types[name])))" + NL + "    return out",
     "        out.append(WildSoul(name, heroes[name.lower()], item, new, tuple(types[name])))" + NL +
     "    out.append(WildSoul('Celebi', poke_data.CELEBI_HERO, 'ISCE', True, ()))  # v3.3: Soul of the Celebi legend" + NL +
     "    return out")

# legend list
edit('tools/legend_data.py',
     "    ('Dialga', 'n033', 'I01V'), ('Palkia', 'n034', 'I01W'),",
     "    ('Dialga', 'n033', 'I01V'), ('Palkia', 'n034', 'I01W'), ('Celebi', 'n035', 'ISCE'),")

# objects: the hero unit (before the teleport loop) and the Celebi item art
edit('tools/objects.py',
     "    for uid in TELE_UNITS:" + NL,
     "    boss = f.find('n035')" + NL +
     "    if boss is not None and f.find(pd.CELEBI_HERO) is None:  # v3.3: playable Celebi, model and icon of the boss" + NL +
     "        ch = _clone(f.find(pd.PKL_TEMPLATE), pd.CELEBI_HERO)" + NL +
     "        ch.set('upro', T_STRING, 'Celebi')" + NL +
     "        ch.set('unam', T_STRING, 'Psychic&Grass Pokemon')" + NL +
     "        ch.set('umdl', T_STRING, boss.get('umdl'))" + NL +
     "        ch.set('uico', T_STRING, boss.get('uico'))" + NL +
     "        ch.set('usca', T_REAL, 1.4)" + NL +
     "        ch.set('uhab', T_STRING, '')" + NL +
     "        ch.set('uabi', T_STRING, 'AInv')" + NL +
     "        ch.set('utip', T_STRING, 'Celebi')" + NL +
     "        f.custom.append(ch)" + NL +
     "    for uid in TELE_UNITS:" + NL)
edit('tools/objects.py', "TELE_UNITS = ('n00F', 'n035', 'E023')", "TELE_UNITS = ('n00F', 'n035', 'E023', 'PZZA')")
edit('tools/objects.py', "('IL00', \"Celebi's Location\", 'BTNMew (64 x 64).blp', '2,1', 'C')",
     "('IL00', \"Celebi's Location\", 'BTNCelebi (64 x 64).blp', '2,1', 'C')")

# learn_data / ability_data: Celebi is a known hero name
edit('tools/learn_data.py', "    out.update({f.id: f.name for f in poke_data.FORMS})",
     "    out.update({f.id: f.name for f in poke_data.FORMS})" + NL + "    out[poke_data.CELEBI_HERO] = 'Celebi'")
edit('tools/ability_data.py', "    out = {f.id: f.name for f in poke_data.FORMS if f.id[:1] == 'P'}",
     "    out = {f.id: f.name for f in poke_data.FORMS if f.id[:1] == 'P'}" + NL + "    out[poke_data.CELEBI_HERO] = 'Celebi'")
print('ok')
