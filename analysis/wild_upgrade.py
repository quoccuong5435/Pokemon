"""One-off: wild creeps that nobody fought yet change to the species of the new tier when the tier goes up."""
import io

NL = chr(10)


def edit(path, old, new, enc='latin-1'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


J = 'tools/jass/mega.j'
edit(J, 'unit Npc_Man = null ',
     'integer Wild_UpTier = 0                 // v3.3: tier the creeps were last upgraded to' + NL +
     'integer array Wild_UpT                  // new species chosen per camp during an upgrade' + NL +
     'unit Npc_Man = null ')

# a creep remembers the power it was spawned with (key 31)
edit(J, '        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)' + NL + '        call Wild_Apply(u)' + NL,
     '        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)' + NL +
     '        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)' + NL +
     '        call Wild_Apply(u)' + NL)

edit(J, '// ---------------------------------------------------------------------------------------------' + NL +
     '// Random legends' + NL,
     '// v3.3: when the tier goes up, creeps that were not hit yet (full HP) become the species of the new tier,' + NL +
     '// one species per camp, keeping position, camp, elite status and HP' + NL +
     'function Wild_Upgrade takes nothing returns nothing' + NL +
     '    local integer c = 0' + NL +
     '    local unit u = null' + NL +
     '    local unit nu = null' + NL +
     '    local integer h = 0' + NL +
     '    local integer pow = 0' + NL +
     '    loop' + NL +
     '        exitwhen c >= Wild_CampN' + NL +
     '        set Wild_UpT[c] = 0' + NL +
     '        set c = c + 1' + NL +
     '    endloop' + NL +
     '    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)' + NL +
     '    loop' + NL +
     '        set u = FirstOfGroup(Wild_Tmp)' + NL +
     '        exitwhen u == null' + NL +
     '        call GroupRemoveUnit(Wild_Tmp, u)' + NL +
     '        set h = GetHandleId(u)' + NL +
     '        set c = LoadInteger(Mega_HT, h, 25) - 1' + NL +
     '        if c >= 0 and Wild_IsWildType(GetUnitTypeId(u)) and GetWidgetLife(u) > 0.405 and GetUnitLifePercent(u) >= 99.9 then' + NL +
     '            set pow = Wild_CampPow[c] + Wild_Tier' + NL +
     '            if pow > 10 then' + NL +
     '                set pow = 10' + NL +
     '            endif' + NL +
     '            if LoadInteger(Mega_HT, h, 31) < pow then' + NL +
     '                if Wild_UpT[c] == 0 then' + NL +
     '                    set Wild_UpT[c] = Wild_PickType(pow)' + NL +
     '                endif' + NL +
     '                set nu = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_UpT[c], GetUnitX(u), GetUnitY(u), GetUnitFacing(u))' + NL +
     '                call SaveInteger(Mega_HT, GetHandleId(nu), 25, c + 1)' + NL +
     '                call SaveInteger(Mega_HT, GetHandleId(nu), 31, pow)' + NL +
     '                call Wild_Apply(nu)' + NL +
     '                if LoadInteger(Mega_HT, h, 29) == 1 then' + NL +
     '                    call Wild_MakeElite(nu)' + NL +
     '                endif' + NL +
     '                call FlushChildHashtable(Mega_HT, h)' + NL +
     '                call RemoveUnit(u)' + NL +
     '            endif' + NL +
     '        endif' + NL +
     '    endloop' + NL +
     '    set u = null' + NL +
     '    set nu = null' + NL +
     'endfunction' + NL + NL +
     '// ---------------------------------------------------------------------------------------------' + NL +
     '// Random legends' + NL)

edit(J, '        call Wild_UpdateTier()' + NL,
     '        call Wild_UpdateTier()' + NL +
     '        if Wild_Tier > Wild_UpTier then' + NL +
     '            set Wild_UpTier = Wild_Tier' + NL +
     '            call Wild_Upgrade()' + NL +
     '        endif' + NL)
print('ok')
