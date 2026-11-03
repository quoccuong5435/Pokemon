"""One-off: type items (Charcoal, Mystic Water...) can only be bought by Pokemon of that type; the PKLegends heroes get a
type label (unam, e.g. 'Fire&Fighting Pokemon') so the check works for them too."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


io.open('tools/type_items.py', 'w', encoding='utf-8', newline='').write(
    '"""Type items of the Poke Super Marts (n00N, n00Q): item id -> type word. Only a Pokemon whose type name (the unit name, e.g.\n'
    '\'Fire&Flying Pokemon\') contains the word may buy it; the price is refunded otherwise."""' + NL +
    "TYPE_ITEMS = (('I00Q', 'Fire'), ('I00R', 'Grass'), ('I00S', 'Water'), ('I00T', 'Electric'), ('I00U', 'Bug')," + NL +
    "              ('I00V', 'Poison'), ('I00W', 'Ice'), ('I00X', 'Dragon'), ('I00Y', 'Flying'), ('I00Z', 'Normal')," + NL +
    "              ('I010', 'Psychic'), ('I011', 'Fighting'), ('I012', 'Rock'), ('I01X', 'Steel'), ('I01Y', 'Dark')," + NL +
    "              ('I020', 'Ghost'))" + NL +
    'COST = 3000  # every type item costs 3000 gold in the v1.8 item data' + NL)

# type label of a species
edit('tools/type_taverns.py', 'def pickable_forms():',
     'def type_label(name):' + NL +
     '    """Unit type name of a PKLegends form, like the v1.8 heroes: \'Fire&Fighting Pokemon\'."""' + NL +
     '    sp = learn_data.SPECIES.get(learn_data.slug(name))' + NL +
     "    types = [t for t in (sp.get('types') if sp else None) or ['normal'] if t in PICK_TYPES] or ['normal']" + NL +
     "    return '&'.join(t.capitalize() for t in types) + ' Pokemon'" + NL + NL + NL +
     'def pickable_forms():')
edit('tools/objects.py', "        o.set('unam', T_STRING, pd.KIT_TYPES.get(form.kit, 'Pokemon'))",
     "        o.set('unam', T_STRING, pd.KIT_TYPES[form.kit] if form.kit in pd.KIT_TYPES else __import__('type_taverns').type_label(form.name))")

# generated data
edit('tools/inject.py', 'def gen_pick_init(enabled):',
     'def gen_type_items_init():' + NL +
     '    """Type_InitData: the type items and the type word a buyer\'s unit name must contain."""' + NL +
     '    import type_items' + NL +
     "    lines = ['function Type_InitData takes nothing returns nothing', '    set Type_N = %d' % len(type_items.TYPE_ITEMS)]" + NL +
     '    for i, (item, word) in enumerate(type_items.TYPE_ITEMS):' + NL +
     "        lines += [\"    set Type_Item[%d] = '%s'\" % (i, item), '    set Type_Word[%d] = %s' % (i, _jstr(word)), '    set Type_Cost[%d] = %d' % (i, type_items.COST)]" + NL +
     "    lines.append('endfunction')" + NL +
     "    return chr(10).join(lines) + chr(10)" + NL + NL + NL +
     'def gen_pick_init(enabled):')
edit('tools/inject.py', "gen_pick_init(evo is not None).rstrip('\\n'),",
     "gen_pick_init(evo is not None).rstrip('\\n'), gen_type_items_init().rstrip('\\n'),")

# JASS
J = 'tools/jass/mega.j'
edit(J, 'unit Npc_Man = null ',
     '// type items can only be bought by Pokemon of that type (v3.3)' + NL +
     'integer Type_N = 0' + NL + 'integer array Type_Item' + NL + 'string array Type_Word' + NL + 'integer array Type_Cost' + NL +
     'unit Npc_Man = null ', 'latin-1')
edit(J, 'function Npc_IsMan takes nothing returns boolean' + NL,
     'function Type_Has takes string name, string word returns boolean' + NL +
     '    local integer i = 0' + NL +
     '    local integer n = StringLength(name)' + NL +
     '    local integer w = StringLength(word)' + NL +
     '    loop' + NL +
     '        exitwhen i + w > n' + NL +
     '        if SubString(name, i, i + w) == word then' + NL +
     '            return true' + NL +
     '        endif' + NL +
     '        set i = i + 1' + NL +
     '    endloop' + NL +
     '    return false' + NL +
     'endfunction' + NL + NL +
     '// a type item bought by a Pokemon of another type is taken back and the gold refunded' + NL +
     'function Type_OnSell takes nothing returns boolean' + NL +
     '    local item it = GetSoldItem()' + NL +
     '    local unit b = GetBuyingUnit()' + NL +
     '    local integer id = GetItemTypeId(it)' + NL +
     '    local integer i = 0' + NL +
     '    loop' + NL +
     '        exitwhen i >= Type_N' + NL +
     '        if Type_Item[i] == id then' + NL +
     '            if not Type_Has(GetUnitName(b), Type_Word[i]) then' + NL +
     '                call RemoveItem(it)' + NL +
     '                call SetPlayerState(GetOwningPlayer(b), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(GetOwningPlayer(b), PLAYER_STATE_RESOURCE_GOLD) + Type_Cost[i])' + NL +
     '                call DisplayTimedTextToPlayer(GetOwningPlayer(b), 0, 0, 6.0, "|cffffcc00Only " + Type_Word[i] + " type Pokemon can buy this item.|r")' + NL +
     '            endif' + NL +
     '            set it = null' + NL +
     '            set b = null' + NL +
     '            return false' + NL +
     '        endif' + NL +
     '        set i = i + 1' + NL +
     '    endloop' + NL +
     '    set it = null' + NL +
     '    set b = null' + NL +
     '    return false' + NL +
     'endfunction' + NL + NL +
     'function Npc_IsMan takes nothing returns boolean' + NL, 'latin-1')
edit(J, '    local trigger dmt = null' + NL, '    local trigger dmt = null' + NL + '    local trigger tyt = null' + NL, 'latin-1')
edit(J, '    set dmt = CreateTrigger()' + NL,
     '    call Type_InitData()' + NL +
     '    set tyt = CreateTrigger()' + NL +
     '    call TriggerRegisterAnyUnitEventBJ(tyt, EVENT_PLAYER_UNIT_SELL_ITEM)' + NL +
     '    call TriggerAddCondition(tyt, Condition(function Type_OnSell))' + NL +
     '    set dmt = CreateTrigger()' + NL, 'latin-1')
print('ok')
