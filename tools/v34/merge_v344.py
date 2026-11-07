"""Build "Pokemon Arena v3.4.4.w3x" from "Pokemon Arena v3.4.3.w3x": 18-type display, PokemonDB types only.

1. The unit info panel had only the 7 WC3 attack / armor types, renamed by v1.8 into 7 type groups
   (Fire, Water&Ice, Grass&Poison, Electric, Rock&Ground&Fighting, Normal&Flying, Psychic). The engine has no more
   slots, so 160 Pokemon whose first type is Bug / Dark / Dragon / Ghost / Steel / Fairy showed a wrong group, and
   clones of the PKL template (Charmander) showed "Fire" (Pawniard...).
   -> a text frame above the portrait shows the selected unit's PokemonDB types: "Type: Dark / Steel" in the type
      colours, Mega types included (Ty_Of). The 7 old labels / tips / type icons become neutral.
2. The engine still applied the v1.8 attack-vs-armor table (x0.85 / x1.15) on top of the k rule of v3.4.2.
   -> every DamageBonus row = 1.00: only the PokemonDB chart (k rule) decides type matchups.
3. Wild Nidoqueen (n02Q) and Nidorina (n02T) had no type at all -> Poison / Ground, Poison (PokemonDB).

    python -I merge_v344.py "<...>/Pokemon Arena v3.4.3.w3x" "<...>/Pokemon Arena v3.4.4.w3x" [--tools <tools>]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD, NEW = '3.4.3', '3.4.4'
T4 = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 'flying', 'ghost', 'grass', 'ground', 'ice',
      'normal', 'poison', 'psychic', 'rock', 'steel', 'water']
MISSING = {'n02Q': ('poison', 'ground'), 'n02T': ('poison', None)}  # Nidoqueen, Nidorina (pokemondb.net/pokedex/all)

TYUI = r'''// v3.4.4: the PokemonDB types of the selected unit, above the portrait (the 7 WC3 attack / armor types of the
// info panel cannot show 18 types). Selection is tracked with the synced selection events; only the text is local.
function TyUI_Text takes unit u returns string
    local integer a = Ty_Of(u, 0)
    local integer b = Ty_Of(u, 1)
    local string s = ""
    if a < 0 then
        return ""
    endif
    set s = "Type: " + Type_Color[a + 1] + Type_Label[a + 1] + "|r"
    if b >= 0 and b != a then
        set s = s + " / " + Type_Color[b + 1] + Type_Label[b + 1] + "|r"
    endif
    return s
endfunction

function TyUI_OnSelect takes nothing returns nothing
    set TyUI_Sel[GetPlayerId(GetTriggerPlayer())] = GetTriggerUnit()
endfunction

function TyUI_OnDeselect takes nothing returns nothing
    if TyUI_Sel[GetPlayerId(GetTriggerPlayer())] == GetTriggerUnit() then
        set TyUI_Sel[GetPlayerId(GetTriggerPlayer())] = null
    endif
endfunction

function TyUI_Tick takes nothing returns nothing
    local unit u = TyUI_Sel[GetPlayerId(GetLocalPlayer())]
    local string s = ""
    if u != null and GetUnitTypeId(u) != 0 then
        set s = TyUI_Text(u)
    endif
    call BlzFrameSetText(TyUI_Frame, s)
    call BlzFrameSetVisible(TyUI_Frame, s != "")
    set u = null
endfunction

function TyUI_Init takes nothing returns nothing
    local trigger ts = CreateTrigger()
    local trigger td = CreateTrigger()
    local integer i = 0
    set TyUI_Frame = BlzCreateFrameByType("TEXT", "PokemonTypeText", BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0), "", 0)
    call BlzFrameSetSize(TyUI_Frame, 0.20, 0.016)
    call BlzFrameSetPoint(TyUI_Frame, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_PORTRAIT, 0), FRAMEPOINT_TOP, 0.0, 0.003)
    call BlzFrameSetTextAlignment(TyUI_Frame, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetEnable(TyUI_Frame, false)
    call BlzFrameSetText(TyUI_Frame, "")
    call BlzFrameSetVisible(TyUI_Frame, false)
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerUnitEvent(ts, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
        call TriggerRegisterPlayerUnitEvent(td, Player(i), EVENT_PLAYER_UNIT_DESELECTED, null)
        set i = i + 1
    endloop
    call TriggerAddAction(ts, function TyUI_OnSelect)
    call TriggerAddAction(td, function TyUI_OnDeselect)
    call TimerStart(CreateTimer(), 0.2, true, function TyUI_Tick)
    set ts = null
    set td = null
endfunction
'''

NEUTRAL_ATK = 'Pokemon type: shown above the portrait'
NEUTRAL_TIP = 'Damage follows the Pokemon type chart (PokemonDB): the type of the move, or the first type of the attacker for basic attacks, against the types of the target.'


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
    s = sub1(s, 'integer Dmg_Type = 0                    // type + 1 of the damage being shown (Dmg_OnDamaged)',
             'integer Dmg_Type = 0                    // type + 1 of the damage being shown (Dmg_OnDamaged)\n'
             'framehandle TyUI_Frame = null           // v3.4.4: "Type: X / Y" above the portrait\n'
             'unit array TyUI_Sel                     // v3.4.4: last unit selected by each player', 'globals')
    # wild species without a type
    body = func(s, 'Ty_InitUnits').group(0)
    add = ''
    for uid, (t1, t2) in sorted(MISSING.items()):
        if "'%s', 53," % uid in body:
            continue
        add += "    call SaveInteger(Ab_HT, '%s', 53, %d)  // v3.4.4: missing (pokemondb)\n" % (uid, T4.index(t1) + 1)
        if t2:
            add += "    call SaveInteger(Ab_HT, '%s', 54, %d)\n" % (uid, T4.index(t2) + 1)
    s = s.replace(body, body[:-len('endfunction\n')] + add + 'endfunction\n')
    log.append('types added: ' + ', '.join(sorted(MISSING)))
    m = func(s, 'Mega_Init')
    s = s.replace(m.group(0), TYUI + m.group(0))
    s = sub1(s, '    call Dmg_InitTypes()\n',
             '    call Dmg_InitTypes()\n    call TimerStart(CreateTimer(), 0.1, false, function TyUI_Init)  // v3.4.4\n',
             'Mega_Init TyUI')
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    return s


def patch_skin(t, log):
    out, n_lab, n_tip, n_ico = [], 0, 0, 0
    for line in t.split('\n'):
        key = line.split('=', 1)[0].strip()
        if key.startswith('InfoPanelIconDamage') or key.startswith('InfoPanelIconArmor'):
            n_ico += 1  # back to the WC3 icons (the 7 type icons named groups, not types)
            continue
        if re.match(r'^(DAMAGE|ARMOR)_[A-Z]+$', key):
            out.append('%s=%s' % (key, NEUTRAL_ATK))
            n_lab += 1
            continue
        if re.match(r'^(DAMAGETIP|ARMORTIP)_[A-Z0-9_]+$', key):
            out.append('%s=%s' % (key, NEUTRAL_TIP))
            n_tip += 1
            continue
        out.append(line)
    log.append('skin: %d labels, %d tips neutral, %d type icons removed' % (n_lab, n_tip, n_ico))
    return '\n'.join(out)


def patch_misc(t, log):
    def one(m):
        return m.group(1) + ','.join(['1.00'] * len(m.group(2).split(',')))
    t, n = re.subn(r'^(DamageBonus\w+=)([\d.,]+)', one, t, flags=re.M)
    log.append('misc: %d DamageBonus rows = 1.00' % n)
    return t


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
    skin = patch_skin(arc.read('war3mapSkin.txt').decode('latin-1'), log)
    misc = patch_misc(arc.read('war3mapMisc.txt').decode('latin-1'), log)
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')
    arc.save_with(a.dst, {'scripts\\war3map.j': s.encode('latin-1'), 'war3mapSkin.txt': skin.encode('latin-1'),
                          'war3mapMisc.txt': misc.encode('latin-1'), 'war3map.w3i': w3i})
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
