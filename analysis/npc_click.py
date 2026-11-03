"""One-off: the moves NPC opens the move dialog when you click it; it is bigger, invulnerable, has a floating name and a
minimap ping at the start, so it is easy to find."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


J = 'tools/jass/mega.j'
edit(J, 'integer array Npc_Mode ',
     'unit Npc_Man = null                     // the moves NPC (click it to open the dialog)' + NL + 'integer array Npc_Mode ', 'latin-1')
edit(J, 'function Mega_Init takes nothing returns nothing' + NL,
     'function Npc_IsMan takes nothing returns boolean' + NL +
     '    return GetTriggerUnit() == Npc_Man' + NL +
     'endfunction' + NL + NL +
     'function Mega_Init takes nothing returns nothing' + NL, 'latin-1')
edit(J, '    local trigger sdt = null' + NL,
     '    local trigger sdt = null' + NL + '    local trigger nst = null' + NL + '    local texttag ntt = null' + NL, 'latin-1')
edit(J, "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'hpea', Npc_X, Npc_Y, 270.0)" + NL,
     "    set Npc_Man = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'hpea', Npc_X, Npc_Y, 270.0)" + NL +
     "    call SetUnitScale(Npc_Man, 1.8, 1.8, 1.8)" + NL +
     "    call SetUnitInvulnerable(Npc_Man, true)" + NL +
     "    set ntt = CreateTextTag()" + NL +
     "    call SetTextTagText(ntt, \"|cffffcc00MOVES NPC|r (click)\", 0.024)" + NL +
     "    call SetTextTagPos(ntt, Npc_X - 110.0, Npc_Y, 160.0)" + NL +
     "    call SetTextTagPermanent(ntt, true)" + NL +
     "    call SetTextTagVisibility(ntt, true)" + NL +
     "    call PingMinimap(Npc_X, Npc_Y, 8.0)" + NL +
     "    set nst = CreateTrigger()" + NL +
     "    set i = 0" + NL +
     "    loop" + NL +
     "        exitwhen i >= 12" + NL +
     "        call TriggerRegisterPlayerUnitEvent(nst, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)" + NL +
     "        set i = i + 1" + NL +
     "    endloop" + NL +
     "    call TriggerAddCondition(nst, Condition(function Npc_IsMan))" + NL +
     "    call TriggerAddAction(nst, function Npc_OnChat)" + NL, 'latin-1')

# jasscheck: the new natives
edit('tools/jasscheck.py', "'GetSoldItem': 0,",
     "'GetSoldItem': 0, 'CreateTextTag': 0, 'SetTextTagText': 3, 'SetTextTagPos': 4, 'SetTextTagPermanent': 2," + NL +
     "    'SetTextTagVisibility': 2, 'SetUnitInvulnerable': 2,")
print('ok')
