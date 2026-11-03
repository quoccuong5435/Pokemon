"""One-off: a Pokemon that becomes a legend (or any Soul form) does not keep the moves of the old Pokemon, so each form
learns its own moves (before, every legend had the same moves)."""
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
edit(J, 'function Mega_SafeReplace takes unit u, integer newId, integer method returns nothing' + NL,
     '// v3.3: forms reached through a Soul (the 14 legend heroes of the map and every form a Soul of ours gives) start with' + NL +
     '// no learned moves, so they learn the moves of their own species instead of keeping the old Pokemon\'s' + NL +
     'function Mega_ResetsMoves takes integer id returns boolean' + NL +
     '    local integer i = 0' + NL +
     "    if id == 'E020' or id == 'E021' or id == 'E022' or id == 'E023' or id == 'E024' or id == 'E025' or id == 'E026' then" + NL +
     '        return true' + NL +
     '    endif' + NL +
     "    if id == 'E027' or id == 'E028' or id == 'E029' or id == 'E02A' or id == 'E03J' or id == 'E04C' or id == 'E04D' then" + NL +
     '        return true' + NL +
     '    endif' + NL +
     '    loop' + NL +
     '        exitwhen i >= Soul_N' + NL +
     '        if Soul_Hero[i] == id then' + NL +
     '            return true' + NL +
     '        endif' + NL +
     '        set i = i + 1' + NL +
     '    endloop' + NL +
     '    return false' + NL +
     'endfunction' + NL + NL +
     'function Mega_SafeReplace takes unit u, integer newId, integer method returns nothing' + NL)
edit(J,
     '        set i = 40' + NL +
     '        loop' + NL +
     '            exitwhen i > 43' + NL +
     '            call SaveInteger(Ab_HT, GetHandleId(nu), i, LoadInteger(Ab_HT, h, i))' + NL +
     '            set i = i + 1' + NL +
     '        endloop' + NL +
     '        set i = 0' + NL +
     '        loop' + NL +
     '            exitwhen i >= Mv_N' + NL +
     '            call SaveInteger(Ab_HT, GetHandleId(nu), 200 + i, LoadInteger(Ab_HT, h, 200 + i))' + NL +
     '            set i = i + 1' + NL +
     '        endloop' + NL,
     '        if not Mega_ResetsMoves(newId) then' + NL +
     '            set i = 40' + NL +
     '            loop' + NL +
     '                exitwhen i > 43' + NL +
     '                call SaveInteger(Ab_HT, GetHandleId(nu), i, LoadInteger(Ab_HT, h, i))' + NL +
     '                set i = i + 1' + NL +
     '            endloop' + NL +
     '            set i = 0' + NL +
     '            loop' + NL +
     '                exitwhen i >= Mv_N' + NL +
     '                call SaveInteger(Ab_HT, GetHandleId(nu), 200 + i, LoadInteger(Ab_HT, h, 200 + i))' + NL +
     '                set i = i + 1' + NL +
     '            endloop' + NL +
     '        endif' + NL)
print('ok')
