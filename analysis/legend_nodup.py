"""One-off: random legends never spawn twice at the same time; legend HP x2.5 (0.5 -> 1.25 of the v1.8 boss HP)."""
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
edit(J, 'integer Leg_Alive = 0' + NL, 'integer Leg_Alive = 0' + NL + 'integer array Leg_Up   // v3.3: 1 while that legend is alive (no duplicates)' + NL, 'latin-1')
edit(J,
     '    set i = GetRandomInt(0, Leg_N - 1)' + NL,
     '    loop' + NL +
     '        set i = GetRandomInt(0, Leg_N - 1)' + NL +
     '        set tries = tries + 1' + NL +
     '        exitwhen Leg_Up[i] == 0 or tries >= 40' + NL +
     '    endloop' + NL +
     '    if Leg_Up[i] > 0 then' + NL +
     '        return' + NL +
     '    endif' + NL, 'latin-1')
edit(J, 'function Leg_Spawn takes nothing returns nothing' + NL + '    local unit lg = null' + NL,
     'function Leg_Spawn takes nothing returns nothing' + NL + '    local unit lg = null' + NL + '    local integer tries = 0' + NL, 'latin-1')
edit(J, '    set Leg_Alive = Leg_Alive + 1' + NL + '    call PingMinimap',
     '    set Leg_Alive = Leg_Alive + 1' + NL + '    set Leg_Up[i] = 1' + NL + '    call PingMinimap', 'latin-1')
edit(J, '            set Leg_Alive = Leg_Alive - 1' + NL + '            if GetRandomInt(1, 100) <= Leg_SoulChance then',
     '            set Leg_Alive = Leg_Alive - 1' + NL + '            set Leg_Up[i] = 0' + NL + '            if GetRandomInt(1, 100) <= Leg_SoulChance then', 'latin-1')

# HP x2.5 of the current value: 0.5 -> 1.25
edit('tools/objects.py', '    """Legend bosses (v3.2 balance): level 100, HP x0.5, damage x0.8, armor at most 35."""',
     '    """Legend bosses (v3.3 balance): level 100, HP x1.25 (v3.2 was x0.5; x2.5 on top), damage x0.8, armor at most 35."""')
edit('tools/objects.py', "o.set('uhpm', T_INT, int(round(o.get('uhpm') * 0.5)))\n        o.set('ua1b'",
     "o.set('uhpm', T_INT, int(round(o.get('uhpm') * LEGEND_HP_MULT)))\n        o.set('ua1b'")
edit('tools/objects.py', 'POKE_CENTER_HEAL_MULT = 3.0', 'LEGEND_HP_MULT = 1.25  # legend HP: x0.5 (v3.2) times 2.5' + NL + 'POKE_CENTER_HEAL_MULT = 3.0')
print('ok')
