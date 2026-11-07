"""One-off (v3.4.2): the Pokemon League moves into Darkrai's room (approved 2026-11-08).
league_area.py: data lines; extras.py: data, Darkrai legend nL19, item IL01 text; gym.j: setup / portals / start in
the arena; apply.py: LegTele IL01 target, wiring, gym 8 no longer locked; build_v34.py: repainted war3map.w3e."""
import re


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


# ---------------------------------------------------------------- league_area.py: JASS data
s = open('tools/v34/league_area.py', encoding='utf-8').read()
s = s.replace('v3.4.3 (proposal): the Pokemon League', 'v3.4.2: the Pokemon League', 1)
s += '''

def jass_lines(ids):
    """data lines for V34_Data: arena, lobby, portals, statues (ids: proper name -> [unit ids])"""
    import math
    f = lambda v: repr(float(v))  # noqa: E731
    lines = ['    set League_AX = %s' % f(ARENA[0]), '    set League_AY = %s' % f(ARENA[1]),
             '    set League_LX = %s' % f(LOBBY[0]), '    set League_LY = %s' % f(LOBBY[1]),
             '    set League_EX = %s' % f(EXIT[0]), '    set League_EY = %s' % f(EXIT[1]),
             '    set League_GX = %s' % f(BASE_GATE[0]), '    set League_GY = %s' % f(BASE_GATE[1]),
             '    set League_RoomX0 = %s' % f(ROOM[0]), '    set League_RoomY0 = %s' % f(ROOM[1]),
             '    set League_RoomX1 = %s' % f(ROOM[2]), '    set League_RoomY1 = %s' % f(ROOM[3])]
    for k, (who, poke, ang) in enumerate(STATUES):
        x = ARENA[0] + STATUE_R * math.cos(math.radians(ang))
        y = ARENA[1] + STATUE_R * math.sin(math.radians(ang))
        lines += ["    set League_StatueType[%d] = '%s'" % (k, ids[poke][0]),
                  '    set League_StatueX[%d] = %s' % (k, f(x)), '    set League_StatueY[%d] = %s' % (k, f(y)),
                  '    set League_StatueName[%d] = "%s"' % (k, who)]
    lines.append('    set League_StatueN = %d' % len(STATUES))
    return lines
'''
open('tools/v34/league_area.py', 'w', encoding='utf-8').write(s)
print('edited league_area.py')

# ---------------------------------------------------------------- extras.py
edit('tools/v34/extras.py', [(
    """    # ---------------- Elite Four and Champion""",
    """    # ---------------- v3.4.2: the League in Darkrai's room; its Darkrai becomes a random legend (nL19)
    import league_area
    c.data += league_area.jass_lines(ids)
    o = clone(units['n00F'], 'nL19')
    setf(o, 'unam', 'Wild Darkrai', T_STRING)
    c.objs.append(o)
    leg_n = int(re.search(r'set Leg_N = (\\d+)', script).group(1)) + 1   # + Latias & Latios (content.py)
    c.data += ["    set Leg_Type[%d] = 'nL19'" % leg_n, "    set Leg_Soul[%d] = 'I01F'" % leg_n,
               '    set Leg_Name[%d] = "Darkrai"' % leg_n, '    set Leg_N = %d' % (leg_n + 1)]
    import abilities
    c.links.append(('nL19', abilities.by_name()['Bad Dreams']))
    c.item_txt_mods.append(('IL01', [
        ('Name', 'Pokemon League'), ('Tip', 'Teleport to the |cffffcc00Pokemon League [D]|r'),
        ('Ubertip', 'Teleport to the Pokemon League (Elite Four and Champion, 8 badges). The exit portal there '
                    'brings you back to your base.'),
        ('Description', 'Teleport to the Pokemon League.'),
        ('Art', 'ReplaceableTextures\\\\CommandButtons\\\\BTNMedalionOfCourage.blp')]))
    c.report.append('League: Darkrai room, Darkrai -> random legend nL19 (Leg %d)' % leg_n)

    # ---------------- Elite Four and Champion""")])

# ---------------------------------------------------------------- globals
s = open('tools/v34/jass/globals.j', encoding='utf-8').read().rstrip('\\n')
s += '''
real League_AX = 0.0                    // v3.4.2 League in Darkrai's room (league_area.py): arena centre,
real League_AY = 0.0
real League_LX = 0.0                    // lobby (where the portals send you),
real League_LY = 0.0
real League_EX = 0.0                    // exit portal (to your base),
real League_EY = 0.0
real League_GX = 0.0                    // entrance portal of the west base (the east base mirrors x)
real League_GY = 0.0
real League_RoomX0 = 0.0
real League_RoomY0 = 0.0
real League_RoomX1 = 0.0
real League_RoomY1 = 0.0
integer League_StatueN = 0
integer array League_StatueType
real array League_StatueX
real array League_StatueY
string array League_StatueName
unit array League_Gate                  // 0 west base, 1 east base, 2 exit
'''
open('tools/v34/jass/globals.j', 'w', encoding='utf-8').write(s)
print('edited globals.j')

# ---------------------------------------------------------------- gym.j
g = 'tools/v34/jass/gym.j'
edit(g, [
    # gym 8 is no longer the League arena
    (" and not (g == 7 and League_Pid >= 0) then", " then"),
    ("""    elseif League_Pid >= 0 or Gym_Pid[7] >= 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00The League arena (gym 8) is busy. Try again soon.|r")""",
     """    elseif League_Pid >= 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00The League arena is busy: " + GetPlayerName(Player(League_Pid)) + " is challenging it. Try again soon.|r")"""),
    ("""        set Gym_X[8] = Gym_X[7]
        set Gym_Y[8] = Gym_Y[7]
        call SetUnitPosition(u, Gym_X[8], Gym_Y[8] - 250.0)""",
     """        set Gym_X[8] = League_AX  // v3.4.2: the arena in Darkrai's room
        set Gym_Y[8] = League_AY
        call SetUnitPosition(u, League_AX + 450.0, League_AY)"""),
    ("""    call SetUnitPosition(League_Unit, League_RX, League_RY)
    call PanCameraToTimedForPlayer(p, League_RX, League_RY, 0.3)""",
     """    call SetUnitPosition(League_Unit, League_LX, League_LY)  // v3.4.2: back to the lobby
    call PanCameraToTimedForPlayer(p, League_LX, League_LY, 0.3)"""),
])
s = open(g, encoding='utf-8').read()
s = s.replace('''// ---------------------------------------------------------------------------------------------
// v3.4 Elite Four + Champion ("-league", 8 badges): 5 battles in a row in the arena of gym 8 (gym slot 8 of the
// Gym_* arrays)''', '''// ---------------------------------------------------------------------------------------------
// v3.4 Elite Four + Champion ("-league" or walking into the arena circle with 8 badges): 5 battles in a row in the
// League arena (Darkrai's old room since v3.4.2; gym slot 8 of the Gym_* arrays)''', 1)
# start by walking into the arena circle (League_Tick)
s = s.replace('''    if League_Pid >= 0 then
        if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or GetWidgetLife(League_Unit) <= 0.405 then''',
'''    if League_Pid < 0 then  // v3.4.2: a hero that walks into the arena circle starts the League
        call GroupEnumUnitsInRange(Ext_G, League_AX, League_AY, 350.0, null)
        loop
            set u = FirstOfGroup(Ext_G)
            exitwhen u == null
            call GroupRemoveUnit(Ext_G, u)
            set pid = GetPlayerId(GetOwningPlayer(u))
            if League_Pid < 0 and pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then
                if Badge_Count(pid) >= 8 and Mega_Time >= League_Cool[pid] and not Gym_Busy(pid) then
                    call League_Start(pid)
                elseif Mega_Time >= Gym_Warn[pid] then
                    set Gym_Warn[pid] = Mega_Time + 8.0
                    call League_Start(pid)  // says why it cannot start (badges, cool-down)
                endif
            endif
        endloop
    endif
    if League_Pid >= 0 then
        if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or GetWidgetLife(League_Unit) <= 0.405 then''', 1)
s = s.replace('''function League_Tick takes nothing returns nothing
    local integer k = 0
    local real dx = 0.0
    local real dy = 0.0''', '''function League_Tick takes nothing returns nothing
    local integer k = 0
    local real dx = 0.0
    local real dy = 0.0
    local unit u = null
    local integer pid = 0''', 1)
s = s.rstrip('\n') + '''

// v3.4.2: portals. A hero of a player that steps on one goes to the League lobby (base portals) or to its own base
// (exit portal); Ab_HT key 130 = time before it can use a portal again
function League_Portal takes real x, real y, boolean toBase returns nothing
    local unit u = null
    local player p = null
    local real tx = League_LX
    local real ty = League_LY
    call GroupEnumUnitsInRange(Ext_G, x, y, 150.0, null)
    loop
        set u = FirstOfGroup(Ext_G)
        exitwhen u == null
        call GroupRemoveUnit(Ext_G, u)
        set p = GetOwningPlayer(u)
        if GetPlayerId(p) < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and Mega_Time >= LoadReal(Ab_HT, GetHandleId(u), 130) then
            call SaveReal(Ab_HT, GetHandleId(u), 130, Mega_Time + 3.0)
            if toBase then
                set tx = GetStartLocationX(GetPlayerStartLocation(p))
                set ty = GetStartLocationY(GetPlayerStartLocation(p))
            else
                set tx = League_LX
                set ty = League_LY
                call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00Pokemon League: walk into the arena circle with 8 badges to challenge the Elite Four. The portal behind you leads back to your base.|r")
            endif
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportCaster.mdl", GetUnitX(u), GetUnitY(u)))
            call SetUnitPosition(u, tx, ty)
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", tx, ty))
            call PanCameraToTimedForPlayer(p, tx, ty, 0.3)
        endif
    endloop
    set u = null
    set p = null
endfunction

function League_PortalTick takes nothing returns nothing
    call League_Portal(League_GX, League_GY, false)
    call League_Portal(-League_GX, League_GY, false)
    call League_Portal(League_EX, League_EY, true)
endfunction

function League_Label takes string s, real x, real y, integer r, integer gg, integer b returns nothing
    local texttag tt = CreateTextTag()
    call SetTextTagText(tt, s, 0.024)
    call SetTextTagPos(tt, x - 60.0, y, 220.0)
    call SetTextTagColor(tt, r, gg, b, 255)
    call SetTextTagPermanent(tt, true)
    call SetTextTagVisibility(tt, true)
    set tt = null
endfunction

// at map start: Darkrai leaves its room (it is a random legend now), portals, statues and labels
function League_Setup takes nothing returns nothing
    local rect r = Rect(League_RoomX0, League_RoomY0, League_RoomX1, League_RoomY1)
    local unit u = null
    local integer i = 0
    call GroupEnumUnitsInRect(Ext_G, r, null)
    loop
        set u = FirstOfGroup(Ext_G)
        exitwhen u == null
        call GroupRemoveUnit(Ext_G, u)
        if GetUnitTypeId(u) == 'n00F' then
            call RemoveUnit(u)
        endif
    endloop
    call RemoveRect(r)
    set League_Gate[0] = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nwgt', League_GX, League_GY, 270.0)
    set League_Gate[1] = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nwgt', -League_GX, League_GY, 270.0)
    set League_Gate[2] = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nwgt', League_EX, League_EY, 180.0)
    loop
        exitwhen i > 2
        call SetUnitInvulnerable(League_Gate[i], true)
        set i = i + 1
    endloop
    call League_Label("Pokemon League", League_GX, League_GY, 255, 204, 0)
    call League_Label("Pokemon League", -League_GX, League_GY, 255, 204, 0)
    call League_Label("Exit", League_EX, League_EY, 255, 120, 80)
    call League_Label("Pokemon League", League_AX, League_AY + 300.0, 255, 204, 0)
    set i = 0
    loop
        exitwhen i >= League_StatueN
        set u = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), League_StatueType[i], League_StatueX[i], League_StatueY[i], bj_RADTODEG * Atan2(League_AY - League_StatueY[i], League_AX - League_StatueX[i]))
        call UnitAddAbility(u, 'Aloc')
        call SetUnitInvulnerable(u, true)
        call PauseUnit(u, true)
        call SetUnitVertexColor(u, 150, 150, 165, 255)
        call SetUnitScale(u, 1.6, 1.6, 1.6)
        call SetUnitTimeScale(u, 0.0)
        call League_Label(League_StatueName[i], League_StatueX[i], League_StatueY[i], 220, 220, 230)
        set i = i + 1
    endloop
    set u = null
    set r = null
endfunction
'''
open(g, 'w', encoding='utf-8').write(s)
print('edited gym.j (League room)')

# ---------------------------------------------------------------- apply.py
edit('tools/v34/apply.py', [
    ("""TYPE_SELL_OLD = """,
     """LEGTELE_OLD = '        call SetUnitPosition(b, -9600.0, -2209.0)\\n'
LEGTELE_NEW = '        call SetUnitPosition(b, League_LX, League_LY)  // v3.4.2: Darkrai\\'s room is the Pokemon League\\n'
TYPE_SELL_OLD = """),
    ("""    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
""", """    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
    script = replace_once(script, LEGTELE_OLD, LEGTELE_NEW)
"""),
    ("""    script = replace_once(script, '    call Base_Init()\\n', '    call Base_Init()\\n    call Ext_PlaceShops()\\n')""",
     """    script = replace_once(script, '    call Base_Init()\\n', '    call Base_Init()\\n    call Ext_PlaceShops()\\n'
                          '    call ExecuteFunc("League_Setup")\\n'
                          '    call TimerStart(CreateTimer(), 0.5, true, function League_PortalTick)\\n')"""),
])

# ---------------------------------------------------------------- build_v34.py: repainted terrain
edit('tools/v34/build_v34.py', [
    ("""import move_icons  # noqa: E402
""", """import move_icons  # noqa: E402
import league_area  # noqa: E402
"""),
    ("""        'war3map.w3u': w3u.to_bytes(),""",
     """        'war3map.w3u': w3u.to_bytes(),
        'war3map.w3e': league_area.repaint(base.read('war3map.w3e'))[0],  # v3.4.2: League room floor"""),
])
