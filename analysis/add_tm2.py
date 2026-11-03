"""One-off: TM/HM data keys in Mv_InitData (inject.py) and the NPC TM menu (mega.j)."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# ---- inject: TM keys (299 = count, 300 + k = move index)
edit('tools/inject.py',
     "                          \"    call SaveInteger(Ab_HT, '%s', %d, %d)\" % (uid, 101 + 2 * k, lv)]" + NL +
     "    lines.append('endfunction')",
     "                          \"    call SaveInteger(Ab_HT, '%s', %d, %d)\" % (uid, 101 + 2 * k, lv)]" + NL +
     "        for uid, tms in sorted(moves.tm_by_unit.items()):" + NL +
     "            lines.append(\"    call SaveInteger(Ab_HT, '%s', 299, %d)\" % (uid, len(tms)))" + NL +
     "            for k, mi in enumerate(tms):" + NL +
     "                lines.append(\"    call SaveInteger(Ab_HT, '%s', %d, %d)\" % (uid, 300 + k, mi))" + NL +
     "    lines.append('endfunction')")

# ---- JASS
J = 'tools/jass/mega.j'
enc = 'latin-1'
edit(J, 'constant integer Npc_LearnCost = 500' + NL,
     'constant integer Npc_LearnCost = 500' + NL +
     'constant integer Npc_TMCost = 3000      // TM/HM moves (v3.3)' + NL +
     'integer array Npc_Mode                  // 0 = normal view, 1 = TM/HM list' + NL +
     'integer array Npc_TMPage' + NL, enc)

# Npc_Show: TM list view (mode 1) before the normal slot view
edit(J,
     '    else' + NL +
     '        set msg = "Slot " + I2S(s + 1) + ": " + Npc_Label(h, s) + ". Choose:"' + NL,
     '    elseif Npc_Mode[pid] == 1 then' + NL +
     '        set msg = "TM/HM moves for slot " + I2S(s + 1) + " (" + I2S(Npc_TMCost) + " gold each, page " + I2S(Npc_TMPage[pid] + 1) + ")"' + NL +
     '        set cnt = LoadInteger(Ab_HT, id, 299)' + NL +
     '        set k = 0' + NL +
     '        set lv = 0' + NL +
     '        loop' + NL +
     '            exitwhen k >= cnt' + NL +
     '            set m = LoadInteger(Ab_HT, id, 300 + k)' + NL +
     '            if not Mv_Known(h, m) then' + NL +
     '                if lv >= Npc_TMPage[pid] * 8 and lv < Npc_TMPage[pid] * 8 + 8 then' + NL +
     '                    set Npc_Btn[b + n] = DialogAddButton(d, Mv_Label[m], 0)' + NL +
     '                    set Npc_Kind[b + n] = 6' + NL +
     '                    set Npc_Val[b + n] = m' + NL +
     '                    set n = n + 1' + NL +
     '                endif' + NL +
     '                set lv = lv + 1' + NL +
     '            endif' + NL +
     '            set k = k + 1' + NL +
     '        endloop' + NL +
     '        if Npc_TMPage[pid] > 0 then' + NL +
     '            set Npc_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)' + NL +
     '            set Npc_Kind[b + n] = 7' + NL +
     '            set n = n + 1' + NL +
     '        endif' + NL +
     '        if lv > (Npc_TMPage[pid] + 1) * 8 then' + NL +
     '            set Npc_Btn[b + n] = DialogAddButton(d, "Next page >", 0)' + NL +
     '            set Npc_Kind[b + n] = 8' + NL +
     '            set n = n + 1' + NL +
     '        endif' + NL +
     '        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)' + NL +
     '        set Npc_Kind[b + n] = 9' + NL +
     '        set n = n + 1' + NL +
     '    else' + NL +
     '        set msg = "Slot " + I2S(s + 1) + ": " + Npc_Label(h, s) + ". Choose:"' + NL, enc)

# normal slot view: a button to open the TM list (keep 12 buttons at most: candidates stop at 10)
edit(J,
     '            exitwhen k >= cnt or n >= 11' + NL,
     '            exitwhen k >= cnt or n >= 10' + NL, enc)
edit(J,
     '        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)' + NL +
     '        set Npc_Kind[b + n] = 4' + NL,
     '        if LoadInteger(Ab_HT, id, 299) > 0 then' + NL +
     '            set Npc_Btn[b + n] = DialogAddButton(d, "TM/HM moves (" + I2S(Npc_TMCost) + " gold)", 0)' + NL +
     '            set Npc_Kind[b + n] = 5' + NL +
     '            set n = n + 1' + NL +
     '        endif' + NL +
     '        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)' + NL +
     '        set Npc_Kind[b + n] = 4' + NL, enc)

# click handler: kinds 5..9
edit(J,
     '            elseif Npc_Kind[b + i] == 3 then' + NL,
     '            elseif Npc_Kind[b + i] == 5 then' + NL +
     '                set Npc_Mode[pid] = 1' + NL +
     '                set Npc_TMPage[pid] = 0' + NL +
     '                call Npc_Show(pid, h, Npc_Slot[pid])' + NL +
     '            elseif Npc_Kind[b + i] == 7 then' + NL +
     '                set Npc_TMPage[pid] = Npc_TMPage[pid] - 1' + NL +
     '                call Npc_Show(pid, h, Npc_Slot[pid])' + NL +
     '            elseif Npc_Kind[b + i] == 8 then' + NL +
     '                set Npc_TMPage[pid] = Npc_TMPage[pid] + 1' + NL +
     '                call Npc_Show(pid, h, Npc_Slot[pid])' + NL +
     '            elseif Npc_Kind[b + i] == 9 then' + NL +
     '                set Npc_Mode[pid] = 0' + NL +
     '                call Npc_Show(pid, h, Npc_Slot[pid])' + NL +
     '            elseif Npc_Kind[b + i] == 6 then' + NL +
     '                if GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) >= Npc_TMCost then' + NL +
     '                    call SetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) - Npc_TMCost)' + NL +
     '                    call Mv_Put(h, Npc_Slot[pid], Npc_Val[b + i])' + NL +
     '                    call SaveInteger(Ab_HT, GetHandleId(h), 200 + Npc_Val[b + i], 1)' + NL +
     '                    call Mv_Notify(h, Npc_Val[b + i])' + NL +
     '                    set Npc_Mode[pid] = 0' + NL +
     '                    call Npc_Show(pid, h, -1)' + NL +
     '                else' + NL +
     '                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Not enough gold.|r")' + NL +
     '                    call Npc_Show(pid, h, Npc_Slot[pid])' + NL +
     '                endif' + NL +
     '            elseif Npc_Kind[b + i] == 3 then' + NL, enc)
# opening the NPC always starts in the normal view
edit(J,
     '        set Npc_Unit[pid] = h' + NL + '        call Npc_Show(pid, h, -1)' + NL,
     '        set Npc_Unit[pid] = h' + NL + '        set Npc_Mode[pid] = 0' + NL + '        call Npc_Show(pid, h, -1)' + NL, enc)
print('ok')
