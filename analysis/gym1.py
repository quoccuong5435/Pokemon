"""One-off: the 8 gyms (v1.8 leader chains) become a team of 6 whose levels follow the challenger:
member k has level base * (1 + 0.1 * k), at most 100 (a level-100 challenger faces six level-100 Pokemon). Higher gyms
are stronger (stats x (1 + 0.1 * gym index)). If the challenger dies (or walks away) the gym starts over. Beating all six
drops the gym item (I014..I01B). The v1.8 leader chains are removed at the start."""
import io

NL = chr(10)


def edit(path, old, new, enc='latin-1'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# gym leader positions (v1.8 CreateUnit) and the item each gym gives
GYMS = [(-1405.5, 5887.1, 'I014'), (-2683.8, 5896.7, 'I015'), (-3969.1, 5890.0, 'I016'), (-5377.2, 5888.7, 'I017'),
        (1154.9, 5877.8, 'I019'), (2436.6, 5898.4, 'I018'), (3716.3, 5866.3, 'I01A'), (5379.5, 5879.2, 'I01B')]
CHAIN = ['n00S', 'n00U', 'n00T', 'n00R', 'n00W', 'n00V', 'n00X', 'n00Y', 'n00Z', 'n010', 'n012', 'n011', 'n014', 'n013',
         'n015', 'n018', 'n016', 'n017', 'n019', 'n01A', 'n01B', 'n01C', 'n01D', 'n01E']

J = 'tools/jass/mega.j'
edit(J, 'unit Npc_Man = null ',
     '// Gym teams (v3.3): 8 gyms, arrays indexed 0..7' + NL +
     'constant real Gym_Start = 500.0         // a hero this close to the gym leader spot starts the challenge' + NL +
     'constant real Gym_Leave = 2200.0        // farther than this = the challenge is abandoned (starts over)' + NL +
     'real array Gym_X' + NL + 'real array Gym_Y' + NL + 'integer array Gym_Item' + NL +
     'integer array Gym_Pid                   // challenger player id (-1 = nobody)' + NL +
     'integer array Gym_Stage                 // 0..5 = index of the Pokemon being fought' + NL +
     'integer array Gym_Base                  // level of the challenger when the challenge started' + NL +
     'real array Gym_Cool' + NL + 'unit array Gym_Hero' + NL + 'unit array Gym_Cur' + NL + 'integer array Gym_Chain' + NL +
     'unit Npc_Man = null ')

# gym units are not touched by the tier scaling of the wild creeps (key 33 = 1)
edit(J, 'function Wild_Apply takes unit u returns nothing' + NL + '    local integer h = GetHandleId(u)' + NL,
     'function Wild_Apply takes unit u returns nothing' + NL + '    local integer h = GetHandleId(u)' + NL +
     '    if LoadInteger(Mega_HT, h, 33) == 1 then' + NL + '        return' + NL + '    endif' + NL)
edit(J, 'function Wild_ApplyLevel takes unit u returns nothing' + NL + '    local integer h = GetHandleId(u)' + NL,
     'function Wild_ApplyLevel takes unit u returns nothing' + NL + '    local integer h = GetHandleId(u)' + NL +
     '    if LoadInteger(Mega_HT, h, 33) == 1 then' + NL + '        return' + NL + '    endif' + NL)

init_lines = ''
for g, (x, y, item) in enumerate(GYMS):
    init_lines += ('    set Gym_X[%d] = %s' % (g, x) + NL + '    set Gym_Y[%d] = %s' % (g, y) + NL +
                   "    set Gym_Item[%d] = '%s'" % (g, item) + NL + '    set Gym_Pid[%d] = -1' % g + NL)
for i, c in enumerate(CHAIN):
    init_lines += "    set Gym_Chain[%d] = '%s'" % (i, c) + NL

gym = (
    '// ---------------------------------------------------------------------------------------------' + NL +
    '// Gym teams of 6 (v3.3), levels follow the challenger' + NL +
    '// ---------------------------------------------------------------------------------------------' + NL +
    'function Gym_Level takes integer base, integer k returns integer' + NL +
    '    local integer lv = R2I(I2R(base) * (1.0 + 0.1 * I2R(k)))' + NL +
    '    if lv > 100 then' + NL + '        set lv = 100' + NL + '    endif' + NL +
    '    if lv < 1 then' + NL + '        set lv = 1' + NL + '    endif' + NL +
    '    return lv' + NL + 'endfunction' + NL + NL +
    'function Gym_Busy takes integer pid returns boolean' + NL +
    '    local integer g = 0' + NL +
    '    loop' + NL + '        exitwhen g >= 8' + NL +
    '        if Gym_Pid[g] == pid then' + NL + '            return true' + NL + '        endif' + NL +
    '        set g = g + 1' + NL + '    endloop' + NL +
    '    return false' + NL + 'endfunction' + NL + NL +
    'function Gym_Spawn takes integer g, integer k returns nothing' + NL +
    '    local integer lv = Gym_Level(Gym_Base[g], k)' + NL +
    '    local integer pow = lv / 10' + NL +
    '    local real m = 1.0 + 0.1 * I2R(g)' + NL +
    '    local unit u = null' + NL +
    '    if pow < 1 then' + NL + '        set pow = 1' + NL + '    endif' + NL +
    '    if pow > 10 then' + NL + '        set pow = 10' + NL + '    endif' + NL +
    '    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_PickType(pow), Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)' + NL +
    '    call SaveInteger(Mega_HT, GetHandleId(u), 33, 1)' + NL +
    '    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m))' + NL +
    '    call SetUnitLifePercentBJ(u, 100.0)' + NL +
    '    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m), 0)' + NL +
    '    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m)' + NL +
    '    call BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, lv)' + NL +
    '    call SetUnitScale(u, 1.2, 1.2, 1.2)' + NL +
    '    set Gym_Cur[g] = u' + NL +
    '    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800Gym " + I2S(g + 1) + ": Pokemon " + I2S(k + 1) + " of 6 (Lv " + I2S(lv) + ")|r")' + NL +
    '    set u = null' + NL + 'endfunction' + NL + NL +
    'function Gym_Reset takes integer g returns nothing' + NL +
    '    if Gym_Cur[g] != null then' + NL + '        call RemoveUnit(Gym_Cur[g])' + NL + '    endif' + NL +
    '    set Gym_Cur[g] = null' + NL + '    set Gym_Hero[g] = null' + NL + '    set Gym_Pid[g] = -1' + NL +
    '    set Gym_Stage[g] = 0' + NL + 'endfunction' + NL + NL +
    'function Gym_Tick takes nothing returns nothing' + NL +
    '    local integer g = 0' + NL + '    local unit u = null' + NL + '    local real dx = 0.0' + NL + '    local real dy = 0.0' + NL +
    '    local boolean started = false' + NL +
    '    loop' + NL + '        exitwhen g >= 8' + NL +
    '        if Gym_Pid[g] >= 0 then' + NL +
    '            if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or GetWidgetLife(Gym_Hero[g]) <= 0.405 then' + NL +
    '                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you lost. The gym starts over.|r")' + NL +
    '                call Gym_Reset(g)' + NL + '                set Gym_Cool[g] = Mega_Time + 10.0' + NL +
    '            else' + NL +
    '                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]' + NL + '                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]' + NL +
    '                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then' + NL +
    '                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")' + NL +
    '                    call Gym_Reset(g)' + NL + '                    set Gym_Cool[g] = Mega_Time + 10.0' + NL +
    '                endif' + NL + '            endif' + NL +
    '        elseif Mega_Time >= Gym_Cool[g] then' + NL +
    '            set started = false' + NL +
    '            call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)' + NL +
    '            loop' + NL + '                set u = FirstOfGroup(Wild_Tmp)' + NL + '                exitwhen u == null' + NL +
    '                call GroupRemoveUnit(Wild_Tmp, u)' + NL +
    '                if not started and GetPlayerId(GetOwningPlayer(u)) < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != \'earc\' and not Gym_Busy(GetPlayerId(GetOwningPlayer(u))) then' + NL +
    '                    set started = true' + NL +
    '                    set Gym_Pid[g] = GetPlayerId(GetOwningPlayer(u))' + NL +
    '                    set Gym_Hero[g] = u' + NL + '                    set Gym_Base[g] = GetHeroLevel(u)' + NL +
    '                    set Gym_Stage[g] = 0' + NL + '                    call Gym_Spawn(g, 0)' + NL +
    '                endif' + NL + '            endloop' + NL + '        endif' + NL +
    '        set g = g + 1' + NL + '    endloop' + NL + '    set u = null' + NL + 'endfunction' + NL + NL +
    'function Gym_OnDeath takes nothing returns boolean' + NL +
    '    local unit d = GetDyingUnit()' + NL + '    local integer g = 0' + NL +
    '    loop' + NL + '        exitwhen g >= 8' + NL +
    '        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then' + NL +
    '            set Gym_Stage[g] = Gym_Stage[g] + 1' + NL +
    '            if Gym_Stage[g] >= 6 then' + NL +
    '                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))' + NL +
    '                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped.|r")' + NL +
    '                call Gym_Reset(g)' + NL + '                set Gym_Cool[g] = Mega_Time + 60.0' + NL +
    '            else' + NL + '                set Gym_Cur[g] = null' + NL + '                call Gym_Spawn(g, Gym_Stage[g])' + NL +
    '            endif' + NL + '        endif' + NL +
    '        set g = g + 1' + NL + '    endloop' + NL + '    set d = null' + NL + '    return false' + NL + 'endfunction' + NL + NL +
    'function Gym_IsChain takes integer id returns boolean' + NL +
    '    local integer i = 0' + NL +
    '    loop' + NL + '        exitwhen i >= 24' + NL +
    '        if Gym_Chain[i] == id then' + NL + '            return true' + NL + '        endif' + NL +
    '        set i = i + 1' + NL + '    endloop' + NL + '    return false' + NL + 'endfunction' + NL + NL +
    '// the v1.8 leader chains are replaced by the teams above' + NL +
    'function Gym_Init takes nothing returns nothing' + NL +
    '    local unit u = null' + NL + '    local integer g = 0' + NL + '    local trigger gdt = CreateTrigger()' + NL +
    init_lines +
    '    loop' + NL + '        exitwhen g >= 8' + NL +
    '        call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], 700.0, null)' + NL +
    '        loop' + NL + '            set u = FirstOfGroup(Wild_Tmp)' + NL + '            exitwhen u == null' + NL +
    '            call GroupRemoveUnit(Wild_Tmp, u)' + NL +
    '            if Gym_IsChain(GetUnitTypeId(u)) then' + NL + '                call RemoveUnit(u)' + NL + '            endif' + NL +
    '        endloop' + NL + '        set g = g + 1' + NL + '    endloop' + NL +
    '    call TriggerRegisterAnyUnitEventBJ(gdt, EVENT_PLAYER_UNIT_DEATH)' + NL +
    '    call TriggerAddCondition(gdt, Condition(function Gym_OnDeath))' + NL +
    '    call TimerStart(CreateTimer(), 1.0, true, function Gym_Tick)' + NL +
    '    set u = null' + NL + '    set gdt = null' + NL + 'endfunction' + NL + NL)
edit(J, '// ---------------------------------------------------------------------------------------------' + NL + '// Random legends' + NL,
     gym + '// ---------------------------------------------------------------------------------------------' + NL + '// Random legends' + NL)
edit(J, '    call Pick_Init()' + NL, '    call Pick_Init()' + NL + '    call Gym_Init()' + NL)

edit('tools/jasscheck.py', "'GetSoldItem': 0,",
     "'GetSoldItem': 0, 'GroupEnumUnitsInRange': 5, 'GetUnitFacing': 1, 'BlzSetUnitIntegerField': 3,", 'utf-8')
edit('tools/jasscheck.py', "'EVENT_PLAYER_UNIT_SELL_ITEM',", "'EVENT_PLAYER_UNIT_SELL_ITEM', 'UNIT_IF_LEVEL',", 'utf-8')
print('ok')
