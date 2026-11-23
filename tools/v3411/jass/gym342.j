// v4.3: the gym features of 3.4.2 that 3.4.16 lacks (tools/v3411/gym342.py inserts each section before the
// function named in its marker; docs/superpowers/specs/2026-11-21-merge-3.4.2-into-3.4.16-design.md)

// ==== BEFORE Gym_Spawn
// v3.4.2 gym difficulty, per gym (0..7 = gyms 1..8, 8 = the League): gyms 1-4 are easier, the later ones and the
// League are as before. Functions instead of arrays so no init code is needed.
function Gym_DiffHP takes integer g returns real
    if g == 0 then
        return 0.35
    elseif g == 1 then
        return 0.45
    elseif g == 2 then
        return 0.7
    elseif g == 3 then
        return 0.85
    endif
    return 1.0
endfunction
function Gym_DiffDmg takes integer g returns real
    if g == 0 then
        return 0.45
    elseif g == 1 then
        return 0.55
    elseif g == 2 then
        return 0.75
    elseif g == 3 then
        return 0.85
    endif
    return 1.0
endfunction
function Gym_DiffAI takes integer g returns real
    if g == 0 or g == 1 then
        return 0.25
    elseif g == 2 or g == 3 then
        return 0.45
    endif
    return 0.6
endfunction
function Gym_Fast takes integer g returns boolean
    return g >= 4
endfunction

// ==== BEFORE Ai_Unit
// v3.4.2: the skill-cast chance of one unit (Ab_HT key 88, set for gym Pokemon), else the global chance
function Ai_Chance takes integer h returns real
    if HaveSavedReal(Ab_HT, h, 88) then
        return LoadReal(Ab_HT, h, 88)
    endif
    return Ai_CastChance
endfunction

// ==== BEFORE Gym_OnDeath
// v3.4.2 "-gym": state of the gym you are in (or of all busy gyms)
function Gym_OnChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local integer g = 0
    local integer k = 0
    local string s = ""
    local boolean any = false
    loop
        exitwhen g >= 9
        if Gym_Pid[g] >= 0 then
            set any = true
            set s = "|cffffcc00Gym " + I2S(g + 1) + "|r: " + GetPlayerName(Player(Gym_Pid[g])) + ", Pokemon " + I2S(Gym_Stage[g] + 1) + " of 6"
            if Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0 then
                set s = s + ", current: none (it will be spawned again)"
            else
                set s = s + ", current: " + GetUnitName(Gym_Cur[g]) + " " + I2S(R2I(GetWidgetLife(Gym_Cur[g]))) + " HP at " + I2S(R2I(SquareRoot((GetUnitX(Gym_Cur[g]) - Gym_X[g]) * (GetUnitX(Gym_Cur[g]) - Gym_X[g]) + (GetUnitY(Gym_Cur[g]) - Gym_Y[g]) * (GetUnitY(Gym_Cur[g]) - Gym_Y[g])))) + " from the centre"
            endif
            call DisplayTimedTextToPlayer(p, 0, 0, 15.0, s)
            if Gym_Pid[g] == pid then
                set s = "  team:"
                set k = 0
                loop
                    exitwhen k >= 6
                    set s = s + " " + I2S(k + 1) + "=" + GetObjectName(Gym_Team[g * 6 + k])
                    set k = k + 1
                endloop
                call DisplayTimedTextToPlayer(p, 0, 0, 15.0, s)
            endif
        endif
        set g = g + 1
    endloop
    if not any then
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00No gym battle right now.|r")
    endif
    set p = null
endfunction
// v3.4.2: ExecuteFunc entry points (arguments in Gym_ArgG / Gym_ArgK)
function Gym_StartIt takes nothing returns nothing
    local integer g = Gym_ArgG
    call Gym_BuildTeam(g, Gym_Hero[g])
    call Gym_Spawn(g, 0)
endfunction

function Gym_SpawnIt takes nothing returns nothing
    call Gym_Spawn(Gym_ArgG, Gym_ArgK)
endfunction

function Gym_AdvanceIt takes nothing returns nothing
    if Gym_Pid[Gym_ArgG] >= 0 and Gym_Cur[Gym_ArgG] != null then
        call Gym_Advance(Gym_ArgG, Gym_Cur[Gym_ArgG])
    endif
endfunction
