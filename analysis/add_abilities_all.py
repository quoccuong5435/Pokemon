"""One-off: an Ability for every Pokemon (playable PKL forms, wild creeps, legends, v1.8 heroes).
Priority: explicit table, then the first real (non-hidden) ability we have, then the signature ability of the type."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if chr(13) + NL in s:  # the file uses CRLF
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# ---------------------------------------------------------------- ability_data.py
edit('tools/ability_data.py',
     'def type_abilities(w3u):' + NL +
     '    """Unit type id of every v1.8 hero -> Ability number (1-based index into ABILITIES)."""' + NL +
     '    by_name = species_abilities()' + NL +
     '    return {o.new: _NUMBER[by_name[o.get(\'upro\')]] for o in w3u.custom' + NL +
     '            if o.new[:1] == \'E\' and o.get(\'upro\') and o.get(\'upro\') in by_name}' + NL,
     '# v3.3: signature Ability of a type, for Pokemon whose own Ability we do not have' + NL +
     'TYPE_ABILITY = {' + NL +
     "    'normal': 'Run Away', 'fire': 'Blaze', 'water': 'Torrent', 'grass': 'Overgrow', 'electric': 'Static'," + NL +
     "    'ice': 'Snow Cloak', 'fighting': 'Guts', 'poison': 'Poison Point', 'ground': 'Sand Veil', 'flying': 'Keen Eye'," + NL +
     "    'psychic': 'Synchronize', 'bug': 'Swarm', 'rock': 'Sturdy', 'ghost': 'Levitate', 'dragon': 'Multiscale'," + NL +
     "    'dark': 'Pressure', 'steel': 'Clear Body', 'fairy': 'Cute Charm',}" + NL +
     NL + NL +
     'def _real_name(slug):' + NL +
     "    return ' '.join(w.capitalize() for w in slug.split('-'))" + NL +
     NL + NL +
     'def ability_key_for(name):' + NL +
     '    """Ability key of a species: the explicit table, else its first non-hidden real ability that we have,' + NL +
     '    else the signature Ability of its primary type (None when the species is unknown)."""' + NL +
     '    by_name = species_abilities()' + NL +
     '    if name in by_name:' + NL +
     '        return by_name[name]' + NL +
     '    import learn_data' + NL +
     '    sp = learn_data.SPECIES.get(learn_data.slug(name or \'\'))' + NL +
     '    if sp is None:' + NL +
     '        return None' + NL +
     "    for ab, hidden in sp.get('abilities', []):" + NL +
     '        if not hidden and _real_name(ab) in _NUMBER:' + NL +
     '            return _real_name(ab)' + NL +
     "    return TYPE_ABILITY.get((sp.get('types') or ['normal'])[0], 'Run Away')" + NL +
     NL + NL +
     'def all_unit_names(w3u):' + NL +
     '    """Unit type id -> Pokemon name of the units that get an Ability in v3.3 besides the v1.8 heroes:' + NL +
     '    the PKLegends forms, the wild creeps and the legends (boss units and their random clones)."""' + NL +
     '    import legend_data' + NL +
     '    import poke_data' + NL +
     '    import wild_data' + NL +
     '    out = {f.id: f.name for f in poke_data.FORMS if f.id[:1] == \'P\'}' + NL +
     '    objs = {o.new: o for o in w3u.custom}' + NL +
     '    for t in wild_data.wild_types(w3u):' + NL +
     '        out[t] = wild_data._species_name(objs, t)' + NL +
     '    out.update({s.id: s.name for s in wild_data.SPECIES})' + NL +
     '    for lg in legend_data.LEGENDS:' + NL +
     '        out[lg.id] = lg.name' + NL +
     '        out[lg.boss] = lg.name' + NL +
     '    return out' + NL +
     NL + NL +
     'def type_abilities(w3u):' + NL +
     '    """Unit type id -> Ability number (1-based index into ABILITIES) of every v1.8 hero, PKLegends form, wild' + NL +
     '    creep and legend (every Pokemon has an Ability in v3.3)."""' + NL +
     '    out = {}' + NL +
     '    for o in w3u.custom:' + NL +
     "        if o.new[:1] == 'E' and o.get('upro'):" + NL +
     "            key = ability_key_for(o.get('upro'))" + NL +
     '            if key:' + NL +
     '                out[o.new] = _NUMBER[key]' + NL +
     '    for uid, name in all_unit_names(w3u).items():' + NL +
     '        key = ability_key_for(name)' + NL +
     '        if key:' + NL +
     '            out[uid] = _NUMBER[key]' + NL +
     '    return out' + NL)

# ---------------------------------------------------------------- mega.j: wild creeps and legends carry their Ability
J = 'tools/jass/mega.j'
edit(J,
     'function Wild_Apply takes unit u returns nothing' + NL +
     '    local integer h = GetHandleId(u)' + NL,
     'function Wild_Apply takes unit u returns nothing' + NL +
     '    local integer h = GetHandleId(u)' + NL +
     '    call SaveInteger(Ab_HT, h, 0, LoadInteger(Ab_HT, GetUnitTypeId(u), 0))  // v3.3: wild creeps have the Ability of their species' + NL,
     'latin-1')
edit(J,
     'function Leg_Spawn takes nothing returns nothing' + NL +
     '    local integer i = 0' + NL,
     'function Leg_Spawn takes nothing returns nothing' + NL +
     '    local unit lg = null' + NL +
     '    local integer i = 0' + NL, 'latin-1')
edit(J,
     '    call CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Leg_Type[i], x, y, 270.0)' + NL +
     '    set Leg_Alive = Leg_Alive + 1' + NL,
     '    set lg = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Leg_Type[i], x, y, 270.0)' + NL +
     '    call SaveInteger(Ab_HT, GetHandleId(lg), 0, LoadInteger(Ab_HT, Leg_Type[i], 0))  // v3.3: legends have an Ability' + NL +
     '    set lg = null' + NL +
     '    set Leg_Alive = Leg_Alive + 1' + NL, 'latin-1')
print('ok')
