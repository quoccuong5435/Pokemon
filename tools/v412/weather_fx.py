"""Import weather visual effects (terrain fog and ambient thunder) from v3.4.16 into v4.1.2."""


def patch_script(s):
    # 1. Terrain fog in Wth_Set
    old_set = '''    if Wth_Fx != null then
        call EnableWeatherEffect(Wth_Fx, true)
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, s)'''
    new_set = '''    if Wth_Fx != null then
        call EnableWeatherEffect(Wth_Fx, true)
    endif
    if w == 1 then  // v3.4.16 colored fog
        call SetTerrainFogEx(0, 900.0, 5000.0, 0.5, 0.25, 0.35, 0.55)
    elseif w == 2 then
        call SetTerrainFogEx(0, 1200.0, 6000.0, 0.5, 1.0, 0.75, 0.35)
    elseif w == 3 then
        call SetTerrainFogEx(0, 500.0, 3500.0, 0.5, 0.75, 0.6, 0.35)
    elseif w == 4 then
        call SetTerrainFogEx(0, 700.0, 4000.0, 0.5, 0.85, 0.9, 1.0)
    else
        call ResetTerrainFog()
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, s)'''
    if old_set not in s:
        raise SystemExit('weather_fx: old Wth_Set block not found')
    s = s.replace(old_set, new_set, 1)

    # 2. Wth_Thunder function definition
    thunder_fn = '''function Wth_Thunder takes nothing returns nothing
    local unit u = null
    local integer k = GetRandomInt(0, 11)
    if Wth_Cur != 1 then
        return
    endif
    call GroupEnumUnitsOfPlayer(Fx_TmpG, Player(k), null)
    loop
        set u = FirstOfGroup(Fx_TmpG)
        exitwhen u == null
        call GroupRemoveUnit(Fx_TmpG, u)
        if IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Other\\\\Monsoon\\\\MonsoonBoltTarget.mdl", GetUnitX(u) + GetRandomReal(-700.0, 700.0), GetUnitY(u) + GetRandomReal(-700.0, 700.0)))
        endif
    endloop
    set u = null
endfunction

function Wth_Tick takes nothing returns nothing'''
    if 'function Wth_Tick takes nothing returns nothing' not in s:
        raise SystemExit('weather_fx: function Wth_Tick not found')
    s = s.replace('function Wth_Tick takes nothing returns nothing', thunder_fn, 1)

    # 3. Start Wth_Thunder timer
    old_timer = '    call TimerStart(CreateTimer(), 300.0, true, function Wth_Tick)'
    new_timer = '''    call TimerStart(CreateTimer(), 300.0, true, function Wth_Tick)
    call TimerStart(CreateTimer(), 3.0, true, function Wth_Thunder)'''
    if old_timer not in s:
        raise SystemExit('weather_fx: Wth_Tick timer start not found')
    s = s.replace(old_timer, new_timer, 1)

    return s
