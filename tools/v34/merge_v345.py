"""Build "Pokemon Arena v3.4.5.w3x" from "Pokemon Arena v3.4.4.w3x".

1. Home gates in the Darkrai and Celebi rooms. The other boss rooms of v1.8 (Articuno, Mew, Deoxys...) have a
   gate doodad (DTfp / DTfx) over a 128 x 128 rect that sends heroes to the rect Hi (the town). The two rooms of
   the Haunt Legendary shop (v3.3, reached with the Celebi / Darkrai teleport items) had none.
   -> war3map.doo: a DTfp gate (copy of the Articuno gate) north of each boss, on walkable ground of the room;
      war3map.j: HomeGate_Init, the same teleport as the v1.8 gates (player heroes only).
2. Revive / Max Revive in a gym. They are Reincarnation (AIrc, 1 s delay): the hero has 0 HP for a moment, and
   Gym_Tick (every 1 s) took that as a lost battle and reset the gym. Same for the Elite Four (League_Tick).
   -> the gym / Elite Four is lost only if the challenger stays dead for Gym_ReviveGrace = 3 s.

    python -I merge_v345.py "<...>/Pokemon Arena v3.4.4.w3x" "<...>/Pokemon Arena v3.4.5.w3x" [--tools <tools>]
"""
import argparse
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = '3.4.4', '3.4.5'
# gate centre (x, y) and terrain height z (war3map.w3e) - 128 x 128 rect like the v1.8 gates
GATES = [('Darkrai', -10048.0, -1856.0, 0.0),   # boss n00F at (-10020, -2209), teleport item lands at (-9600, -2209)
         ('Celebi', 10112.0, -2240.0, -1.25)]   # boss n035 at (10104, -2588), teleport item lands at (9600, -2588)

GATE_JASS = r'''// v3.4.5: home gates in the Darkrai / Celebi rooms (Haunt Legendary shop), like the v1.8 boss-room gates:
// a player's hero that steps on it goes to the town (rect Hi). The gate doodads are in war3map.doo.
function HomeGate_OnEnter takes nothing returns boolean
    local unit u = GetTriggerUnit()
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        call SetUnitPosition(u, GetRectCenterX(Hi), GetRectCenterY(Hi))
        call PanCameraToTimedForPlayer(GetOwningPlayer(u), GetUnitX(u), GetUnitY(u), 0.25)
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIil\\AIilTarget.mdl", u, "chest"))
    endif
    set u = null
    return false
endfunction

function HomeGate_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
%s    call TriggerAddCondition(t, Condition(function HomeGate_OnEnter))
    set t = null
endfunction

// v3.4.5: Revive / Max Revive (Reincarnation, 1 s) leave the challenger at 0 HP for a moment: the battle is lost
// only after Gym_ReviveGrace seconds dead. g = 0..7 gyms, 8 = Elite Four.
function Gym_Down takes integer g, unit u returns boolean
    if GetWidgetLife(u) > 0.405 then
        set Gym_DownSince[g] = 0.0
        return false
    endif
    if Gym_DownSince[g] <= 0.0 then
        set Gym_DownSince[g] = Mega_Time + 0.001
        return false
    endif
    return Mega_Time - Gym_DownSince[g] >= Gym_ReviveGrace
endfunction

'''


def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit('%s: expected 1 match, found %d' % (what, n))
    return s.replace(old, new)


def func(s, name):
    m = re.search(r'^function %s takes.*?^endfunction\n' % re.escape(name), s, re.M | re.S)
    if not m:
        raise SystemExit('war3map.j: function %s not found' % name)
    return m


def patch_script(s, log):
    s = sub1(s, 'unit array TyUI_Sel                     // v3.4.4: last unit selected by each player',
             'unit array TyUI_Sel                     // v3.4.4: last unit selected by each player\n'
             'real array Gym_DownSince                // v3.4.5: when the challenger of gym g (8 = Elite Four) went down\n'
             'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)',
             'globals')
    regs = ''.join('    call TriggerRegisterEnterRectSimple(t, Rect(%.1f, %.1f, %.1f, %.1f))  // %s room\n'
                   % (x - 64, y - 64, x + 64, y + 64, n) for n, x, y, z in GATES)
    jass = GATE_JASS % regs
    first = min(func(s, 'Gym_Tick').start(), func(s, 'League_Tick').start(), func(s, 'Mega_Init').start())
    s = s[:first] + jass + s[first:]
    s = sub1(s, 'if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or GetWidgetLife(Gym_Hero[g]) <= 0.405 then',
             'if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or Gym_Down(g, Gym_Hero[g]) then  // v3.4.5: Revive',
             'Gym_Tick death')
    s = sub1(s, 'if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or GetWidgetLife(League_Unit) <= 0.405 then',
             'if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or Gym_Down(8, League_Unit) then  // v3.4.5: Revive',
             'League_Tick death')
    # a new battle starts with a clean timer
    s = sub1(s, '                        set Gym_Stage[g] = 0\n                        // v3.4: the challenger starts with full HP and mana\n',
             '                        set Gym_Stage[g] = 0\n                        set Gym_DownSince[g] = 0.0\n'
             '                        // v3.4: the challenger starts with full HP and mana\n', 'Gym start')
    m = func(s, 'League_Start')
    b = m.group(0)
    b2 = b.replace('\nendfunction\n', '\n    set Gym_DownSince[8] = 0.0  // v3.4.5\nendfunction\n', 1)
    s = s.replace(b, b2)
    s = sub1(s, '    call TimerStart(CreateTimer(), 0.1, false, function TyUI_Init)  // v3.4.4\n',
             '    call TimerStart(CreateTimer(), 0.1, false, function TyUI_Init)  // v3.4.4\n'
             '    call HomeGate_Init()  // v3.4.5\n', 'Mega_Init HomeGate')
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    log.append('war3map.j: HomeGate (Darkrai, Celebi), Gym_Down grace %s s for gyms and the Elite Four' % '3.0')
    return s


def patch_doo(d, log):
    ver, sub, n = struct.unpack_from('<iii', d, 4)
    if ver != 8:
        raise SystemExit('war3map.doo: version %d not handled' % ver)
    o = 16
    tmpl = None
    max_eid = 0
    for _ in range(n):
        start = o
        did = d[o:o + 4]
        o += 36 + 2
        o += 4
        ns, = struct.unpack_from('<i', d, o)
        o += 4
        for _ in range(ns):
            ni, = struct.unpack_from('<i', d, o)
            o += 4 + 8 * ni
        eid, = struct.unpack_from('<i', d, o)
        o += 4
        max_eid = max(max_eid, eid)
        if did == b'DTfp' and tmpl is None and struct.unpack_from('<f', d, start + 8)[0] == -9920.0:
            tmpl = bytearray(d[start:o])  # the Articuno room gate
    if tmpl is None:
        raise SystemExit('war3map.doo: Articuno gate DTfp not found')
    new = b''
    for i, (name, x, y, z) in enumerate(GATES):
        e = bytearray(tmpl)
        struct.pack_into('<3f', e, 8, x, y, z)
        struct.pack_into('<i', e, len(e) - 4, max_eid + 1 + i)
        new += bytes(e)
    out = d[:12] + struct.pack('<i', n + len(GATES)) + d[16:o] + new + d[o:]  # header: W3do, version, subversion, count
    log.append('war3map.doo: %d -> %d doodads (+%s)' % (n, n + len(GATES), ', '.join(g[0] for g in GATES)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--tools', default=os.path.dirname(HERE))
    a = ap.parse_args()
    if os.path.exists(a.dst):
        raise SystemExit('%s exists, not overwriting' % a.dst)
    sys.path.insert(0, a.tools)
    import mpq
    arc = mpq.MPQ(a.src)
    log = []
    s = patch_script(arc.read('scripts\\war3map.j').decode('latin-1'), log)
    doo = patch_doo(arc.read('war3map.doo'), log)
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')
    arc.save_with(a.dst, {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.doo': doo, 'war3map.w3i': w3i})
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
