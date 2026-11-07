"""One-off edit of tools/v34/jass/gym.j: Elite Four + Champion (League, gym slot 8 = the arena of gym 8)."""
p = 'tools/v34/jass/gym.j'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("""function Gym_Busy takes integer pid returns boolean
    local integer g = 0
""", """function Gym_Busy takes integer pid returns boolean
    local integer g = 0
    if League_Pid == pid then  // v3.4: the Elite Four counts as a gym battle
        return true
    endif
""")
rep("""    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800Gym " + I2S(g + 1) + ": " + nm + " (Pokemon " + I2S(k + 1) + " of 6, Lv " + I2S(lv) + ")|r")
    if k == 5 and kt >= 0 then""", """    if g == 8 then
        call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800" + League_Name[League_Stage] + ": " + nm + " (Pokemon " + I2S(k + 1) + " of 6, Lv " + I2S(lv) + ")|r")
    else
        call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800Gym " + I2S(g + 1) + ": " + nm + " (Pokemon " + I2S(k + 1) + " of 6, Lv " + I2S(lv) + ")|r")
    endif
    if k == 5 and kt >= 0 and g < 8 then""")
rep("""                if not started and pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' and not Gym_Busy(pid) then""",
    """                if not started and pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' and not Gym_Busy(pid) and not (g == 7 and League_Pid >= 0) then""")

s = s.rstrip('\n') + """

// ---------------------------------------------------------------------------------------------
// v3.4 Elite Four + Champion ("-league", 8 badges): 5 battles in a row in the arena of gym 8 (gym slot 8 of the
// Gym_* arrays), 6 Pokemon of one type each (Will Psychic, Koga Poison, Bruno Fighting, Karen Dark), then Champion
// Lance (Dragon) whose Pokemon Mega Evolve at 50% HP. Win: title [Champion] (+15% STR / AGI / INT, Champion Aura),
// 10000 gold, a Mega Ring, Shiny Charm (Shiny 1/20). Loss: 60s before the next try.
// ---------------------------------------------------------------------------------------------
function League_Hero takes integer pid returns unit
    local unit u = null
    local unit r = null
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(pid), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if r == null and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' then
            set r = u
        endif
    endloop
    return r
endfunction

// the team of stage League_Stage: Pokemon of its type from the gym pool (one per line), or the Champion's six
function League_BuildTeam takes nothing returns nothing
    local integer ty = League_Type[League_Stage]
    local integer i = 0
    local integer n = 0
    local integer k = 0
    local integer pick = 0
    local integer form = 0
    loop
        exitwhen i >= Gym_PoolN
        set form = Gym_FormAt(Gym_Pool[i], Gym_Level(Gym_Base[8], 3))
        if Ty_OfType(form, 0) == ty or Ty_OfType(form, 1) == ty then
            set League_Cand[n] = Gym_Pool[i]
            set n = n + 1
        endif
        set i = i + 1
    endloop
    loop
        exitwhen k >= 6
        if League_Stage == 4 then
            set Gym_Root[48 + k] = League_ChampTeam[k]
            set Gym_Team[48 + k] = League_ChampTeam[k]
        else
            if n > 0 then
                set pick = GetRandomInt(0, n - 1)
                set Gym_Root[48 + k] = League_Cand[pick]
                set League_Cand[pick] = League_Cand[n - 1]
                set n = n - 1
            else
                set Gym_Root[48 + k] = Gym_Pool[GetRandomInt(0, Gym_PoolN - 1)]
            endif
            set Gym_Team[48 + k] = Gym_FormAt(Gym_Root[48 + k], Gym_Level(Gym_Base[8], k))
        endif
        set Gym_TeamKit[48 + k] = ty
        set k = k + 1
    endloop
endfunction

function League_NextStage takes nothing returns nothing
    local unit u = League_Unit
    call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
    call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Heal\\\\HealTarget.mdl", u, "origin"))
    set Gym_Base[8] = GetHeroLevel(u) + League_Stage + 1
    set Gym_Stage[8] = 0
    call League_BuildTeam()
    if League_Stage == 4 then
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(Player(League_Pid)) + " challenges Champion Lance!|r")
    else
        call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 8.0, "|cffffcc00Elite Four " + I2S(League_Stage + 1) + "/4: " + League_Name[League_Stage] + " (" + Ty_Name[League_Type[League_Stage]] + ")|r")
    endif
    call Gym_Spawn(8, 0)
    set u = null
endfunction

function League_End takes nothing returns nothing
    if Gym_Cur[8] != null then
        call RemoveUnit(Gym_Cur[8])
    endif
    set Gym_Cur[8] = null
    set Gym_Pid[8] = -1
    set League_Pid = -1
    set League_Unit = null
endfunction

function League_Lose takes string why returns nothing
    call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 8.0, "|cffff4040Pokemon League: " + why + " Try again in 60 seconds.|r")
    set League_Cool[League_Pid] = Mega_Time + 60.0
    call League_End()
endfunction

function League_Win takes nothing returns nothing
    local integer pid = League_Pid
    local player p = Player(pid)
    if not League_Champ[pid] then
        set League_Champ[pid] = true
        call SetPlayerName(p, "[Champion] " + GetPlayerName(p))
    endif
    call AdjustPlayerStateBJ(10000, p, PLAYER_STATE_RESOURCE_GOLD)
    call UnitAddItemById(League_Unit, Itm_Id[18])
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 15.0, "|cffffcc00*** " + GetPlayerName(p) + " defeated Champion Lance and is the new Pokemon Champion! ***|r")
    call DisplayTimedTextToPlayer(p, 0, 0, 15.0, "|cff66ff66Title [Champion]: +15% STR / AGI / INT, Champion Aura (allies within 800: +10% damage, -10% damage taken), 10000 gold, a Mega Ring, Shiny Charm (Shiny 1/20).|r")
    call SetUnitPosition(League_Unit, League_RX, League_RY)
    call PanCameraToTimedForPlayer(p, League_RX, League_RY, 0.3)
    call League_End()
    set p = null
endfunction

function League_Start takes integer pid returns nothing
    local unit u = League_Hero(pid)
    local player p = Player(pid)
    if u == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00You need a Pokemon.|r")
    elseif Badge_Count(pid) < 8 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffff4040The Pokemon League needs all 8 badges (you have " + I2S(Badge_Count(pid)) + ").|r")
    elseif League_Pid >= 0 or Gym_Pid[7] >= 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00The League arena (gym 8) is busy. Try again soon.|r")
    elseif Gym_Busy(pid) then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Finish your gym battle first.|r")
    elseif Mega_Time < League_Cool[pid] then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Pokemon League: ready again in " + I2S(R2I(League_Cool[pid] - Mega_Time + 0.99)) + "s.|r")
    else
        set League_Pid = pid
        set League_Unit = u
        set League_Stage = 0
        set League_RX = GetUnitX(u)
        set League_RY = GetUnitY(u)
        set Gym_Pid[8] = pid
        set Gym_X[8] = Gym_X[7]
        set Gym_Y[8] = Gym_Y[7]
        call SetUnitPosition(u, Gym_X[8], Gym_Y[8] - 250.0)
        call PanCameraToTimedForPlayer(p, Gym_X[8], Gym_Y[8], 0.3)
        call League_NextStage()
    endif
    set u = null
    set p = null
endfunction

function League_OnChat takes nothing returns nothing
    call League_Start(GetPlayerId(GetTriggerPlayer()))
endfunction

function League_Tick takes nothing returns nothing
    local integer k = 0
    local real dx = 0.0
    local real dy = 0.0
    loop
        exitwhen k >= 6
        if Gym_Dead[48 + k] != null and GetWidgetLife(Gym_Dead[48 + k]) <= 0.405 then
            call RemoveUnit(Gym_Dead[48 + k])
            set Gym_Dead[48 + k] = null
        endif
        set k = k + 1
    endloop
    if League_Pid >= 0 then
        if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or GetWidgetLife(League_Unit) <= 0.405 then
            call League_Lose("you lost.")
        else
            set dx = GetUnitX(League_Unit) - Gym_X[8]
            set dy = GetUnitY(League_Unit) - Gym_Y[8]
            if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                call League_Lose("you left the arena.")
            endif
        endif
    endif
endfunction

function League_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    if League_Pid >= 0 and Gym_Cur[8] != null and d == Gym_Cur[8] then
        call Gym_ClearItems(d)
        set Gym_Dead[48 + Gym_Stage[8]] = d
        set Gym_Cur[8] = null
        set Gym_Stage[8] = Gym_Stage[8] + 1
        if Gym_Stage[8] < 6 then
            call Gym_Spawn(8, Gym_Stage[8])
        elseif League_Stage < 4 then
            call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 6.0, "|cff66ff66" + League_Name[League_Stage] + " is defeated!|r")
            set League_Stage = League_Stage + 1
            call League_NextStage()
        else
            call League_Win()
        endif
    endif
    set d = null
    return false
endfunction

// the Champion's Pokemon Mega Evolve once at 50% HP (Ab_OnDamaging)
function League_TryMega takes unit t, real d returns nothing
    local integer i = 0
    if League_Pid < 0 or League_Stage != 4 or t != Gym_Cur[8] or LoadInteger(Mega_HT, GetHandleId(t), 0) > 0 then
        return
    endif
    if GetWidgetLife(t) - d > 0.5 * I2R(BlzGetUnitMaxHP(t)) then
        return
    endif
    loop
        exitwhen i >= Mega_N
        if Mega_Base[i] == GetUnitTypeId(t) then
            call Mega_Start(t, i)
            return
        endif
        set i = i + 1
    endloop
endfunction
"""
open(p, 'w', encoding='utf-8').write(s)
print('gym.j patched')
