"""One-off: Souls turn a Pokemon into the BASE form of the family; heroes whose level allows an evolution evolve
(every second, Evo_Check in Hero_Tick), so a Soul at level 100 no longer leaves a half-evolved Pokemon."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# poke_data: root of an evolution family
edit('tools/poke_data.py', 'FORM_BY_ID = {f.id: f for f in FORMS}' + NL,
     'FORM_BY_ID = {f.id: f for f in FORMS}' + NL + NL + NL +
     'def base_form_id(fid):' + NL +
     '    """First form of the evolution family of a form (the form itself when nothing evolves into it)."""' + NL +
     '    parents = {f.evolves_to: f.id for f in FORMS if f.evolves_to}' + NL +
     '    while fid in parents:' + NL +
     '        fid = parents[fid]' + NL +
     '    return fid' + NL)

# wild_data: Souls give the base form
edit('tools/wild_data.py',
     "        out.append(WildSoul(name, heroes[name.lower()], item, new, tuple(types[name])))",
     "        out.append(WildSoul(name, poke_data.base_form_id(heroes[name.lower()]), item, new, tuple(types[name])))")

# objects: the Soul text names the form the Pokemon becomes
edit('tools/objects.py',
     "                ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to become '" + NL +
     "                            '|cffffcc00%s|r.' % w.name),",
     "                ('Ubertip', 'Equip in slot 1 and walk into the circle at the centre of the map to become '" + NL +
     "                            '|cffffcc00%s|r.' % (pd.FORM_BY_ID[w.hero].name if w.hero in pd.FORM_BY_ID else w.name)),")

# JASS: Evo_Check, called every second for every hero
J = 'tools/jass/mega.j'
edit(J, "// v3.3: playable Pokemon max HP x2 in total.",
     "// v3.3: a hero whose level allows its next evolution evolves (also after a Soul or a level reached by other means)" + NL +
     "function Evo_Check takes unit u returns nothing" + NL +
     "    local integer id = GetUnitTypeId(u)" + NL +
     "    local integer i = 0" + NL +
     "    if LoadInteger(Mega_HT, GetHandleId(u), 0) > 0 then" + NL +
     "        return" + NL +
     "    endif" + NL +
     "    loop" + NL +
     "        exitwhen i >= Evo_N" + NL +
     "        if Evo_From[i] == id and GetHeroLevel(u) >= Evo_Level[i] then" + NL +
     "            call DestroyEffect(AddSpecialEffectTarget(\"Abilities\\\\Spells\\\\Undead\\\\DarkRitual\\\\DarkRitualTarget.mdl\", u, \"chest\"))" + NL +
     "            call Mega_SafeReplace(u, Evo_To[i], bj_UNIT_STATE_METHOD_RELATIVE)" + NL +
     "            return" + NL +
     "        endif" + NL +
     "        set i = i + 1" + NL +
     "    endloop" + NL +
     "endfunction" + NL + NL +
     "// v3.3: playable Pokemon max HP x2 in total.", 'latin-1')
edit(J, "                call Hero_HPSync(u)" + NL + "                call Mega_SyncAbility(u)" + NL,
     "                call Hero_HPSync(u)" + NL + "                call Mega_SyncAbility(u)" + NL + "                call Evo_Check(u)" + NL, 'latin-1')
print('ok')
