"""One-off: Souls drop 100% (random legends and the legend bosses in their rooms); a hero that dies drops its Souls."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# ---- random legends: 100%
edit('tools/legend_data.py', 'SOUL_CHANCE = 50        # % chance a random legend drops its Soul',
     'SOUL_CHANCE = 100       # % chance a random legend drops its Soul (v3.3: always)')
edit('tools/jass/mega.j', 'integer Leg_SoulChance = 50', 'integer Leg_SoulChance = 100', 'latin-1')

# ---- legend bosses in their rooms: the v1.8 chance functions (30%) become 100%
edit('tools/inject.py', 'def inject(script, mega_scale, base_scale,',
     "# v1.8 chance functions of the Soul drops of the legend bosses in their rooms (each: 30% -> 100%)" + NL +
     "BOSS_SOUL_CHANCE_FUNCS = ('FE4', 'Gs4', 'F14', 'F64', 'FP4', 'FM4', 'FW4', 'G84', 'FZ4', 'Go4', 'F54', 'Gw4', 'Gf4'," + NL +
     "                          'Gj4')" + NL + NL + NL +
     "def patch_boss_souls(script):" + NL +
     "    for fn in BOSS_SOUL_CHANCE_FUNCS:" + NL +
     "        pat = re.compile(r'(function %s takes nothing returns boolean\\s*if\\(not\\(GetRandomInt\\(1,100\\)<=)30(\\)\\))' % fn)" + NL +
     "        script, n = pat.subn(lambda m: m.group(1) + '100' + m.group(2), script, count=1)" + NL +
     "        if n != 1:" + NL +
     "            raise ValueError('boss Soul chance function %s not found' % fn)" + NL +
     "    return script" + NL + NL + NL +
     'def inject(script, mega_scale, base_scale,')
edit('tools/inject.py', "    script = _replace_exact(script, REVIVE_MSG_OLD, REVIVE_MSG_NEW, 2)" + NL,
     "    script = _replace_exact(script, REVIVE_MSG_OLD, REVIVE_MSG_NEW, 2)" + NL + "    script = patch_boss_souls(script)" + NL)

# ---- a hero that dies drops its Souls
J = 'tools/jass/mega.j'
edit(J, 'function Mega_Init takes nothing returns nothing' + NL + '    local trigger t = CreateTrigger()' + NL + '    local trigger lt = null' + NL,
     '// v3.3: a hero that dies drops the Souls it carries (item names end with "Soul")' + NL +
     'function Soul_DropOnDeath takes nothing returns boolean' + NL +
     '    local unit u = GetDyingUnit()' + NL +
     '    local integer s = 0' + NL +
     '    local item it = null' + NL +
     '    local string n = ""' + NL +
     '    local integer len = 0' + NL +
     '    if IsUnitType(u, UNIT_TYPE_HERO) then' + NL +
     '        loop' + NL +
     '            exitwhen s >= 6' + NL +
     '            set it = UnitItemInSlot(u, s)' + NL +
     '            if it != null then' + NL +
     '                set n = GetItemName(it)' + NL +
     '                set len = StringLength(n)' + NL +
     '                if len >= 4 and SubString(n, len - 4, len) == "Soul" then' + NL +
     '                    call UnitRemoveItem(u, it)' + NL +
     '                endif' + NL +
     '            endif' + NL +
     '            set s = s + 1' + NL +
     '        endloop' + NL +
     '    endif' + NL +
     '    set u = null' + NL +
     '    set it = null' + NL +
     '    return false' + NL +
     'endfunction' + NL + NL +
     'function Mega_Init takes nothing returns nothing' + NL + '    local trigger t = CreateTrigger()' + NL + '    local trigger lt = null' + NL +
     '    local trigger sdt = null' + NL, 'latin-1')
edit(J, '    set lt = CreateTrigger()' + NL,
     '    set sdt = CreateTrigger()' + NL +
     '    call TriggerRegisterAnyUnitEventBJ(sdt, EVENT_PLAYER_UNIT_DEATH)' + NL +
     '    call TriggerAddCondition(sdt, Condition(function Soul_DropOnDeath))' + NL +
     '    set lt = CreateTrigger()' + NL, 'latin-1')

# ---- custom checker knows the new natives
edit('tools/jasscheck.py', "'GetSoldItem': 0,",
     "'GetSoldItem': 0, 'GetItemName': 1, 'StringLength': 1, 'SubString': 3, 'UnitRemoveItem': 2,")
print('ok')
