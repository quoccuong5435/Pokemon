globals
    integer Gym_Dummy = 0
endglobals

function Ai_Unit takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, h, 87)
    local unit t = LoadUnitHandle(Ab_HT, h, 86)
    local integer pick0 = 0
    local integer j = 0
    if kit > 0 and t != null and GetWidgetLife(t) > 0.405 and Mega_Time - LoadReal(Ab_HT, h, 60) <= Ai_Memory then
        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_CastChance then
            set pick0 = GetRandomInt(0, 4)
            loop
                exitwhen j >= 5
                if Ai_TryCast(u, t, Wild_KitSkill[(kit - 1) * 5 + ModuloInteger(pick0 + j, 5)]) then
                    set j = 5
                endif
                set j = j + 1
            endloop
        endif
    endif
    set t = null
endfunction

function Gym_Spawn takes integer g, integer k returns nothing
    local integer lv = Gym_Level(Gym_Base[g], k)
    local real m = 1.0 + 0.1 * I2R(g)
    local integer id = Gym_Team[g * 6 + k]
    local integer kt = Gym_TeamKit[g * 6 + k]
    local integer ty = Ty_OfType(id, 0)
    local unit u = null
    local integer h = 0
    local integer i = 0
    local integer ti = 0
    local string nm = ""
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
    if u == null and Gym_Root[g * 6 + k] != 0 then  // v3.4.3: never leave the gym without a Pokemon
        set id = Gym_Root[g * 6 + k]
        set Gym_Team[g * 6 + k] = id
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
    endif
    set h = GetHandleId(u)
    call SaveInteger(Mega_HT, h, 33, 1)
    if IsUnitType(u, UNIT_TYPE_HERO) then
        call SetHeroLevel(u, lv, false)
        call SuspendHeroXP(u, true)
        set nm = GetHeroProperName(u)
    else
        call BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, lv)
        set nm = GetUnitName(u)
    endif
    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult))
    call SetUnitLifePercentBJ(u, 100.0)
    call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8), 0)
    call BlzSetUnitDiceNumber(u, 1, 0)
    call BlzSetUnitDiceSides(u, 4, 0)
    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m)
    call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Gym_ASBoost, 0)
    call SaveInteger(Ab_HT, h, 0, LoadInteger(Ab_HT, id, 0))  // the Ability of its species
    if kt >= 0 then  // the 5 kit skills of its type (the 6th Pokemon: the type that counters the challenger)
        loop
            exitwhen i >= 5
            if Wild_KitSkill[kt * 5 + i] != 0 then
                call UnitAddAbility(u, Wild_KitSkill[kt * 5 + i])
            endif
            set i = i + 1
        endloop
        call SaveInteger(Ab_HT, h, 87, kt + 1)  // Ai_Tick casts these skills (the creep AI never does)
        set Fx_ArgU = u  // v3.4.13: a status move button in place of one kit skill
        set Fx_ArgK = kt
        set Fx_ArgJ = g
        call ExecuteFunc("Fx_KitStatusX")
    endif
    if ty >= 0 then  // it holds the item of its first type (gym Pokemon drop nothing but the badge)
        set i = 0
        loop
            exitwhen i >= Type_N
            if Type_Word[i] == Ty_Name[ty] then
                set ti = Type_Item[i]
            endif
            set i = i + 1
        endloop
    endif
    set Fx_ArgU = u  // v3.4.11: the type item's abilities, no real item (nothing to drop)
    set Fx_ArgI = ty
    set Fx_ArgJ = g
    call ExecuteFunc("Fx_GymItemX")
    set Gym_Cur[g] = u
    if g == 8 then
        call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800" + League_Name[League_Stage] + ": " + nm + " (Pokemon " + I2S(k + 1) + " of 6, Lv " + I2S(lv) + ")|r")
    else
        call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800Gym " + I2S(g + 1) + ": " + nm + " (Pokemon " + I2S(k + 1) + " of 6, Lv " + I2S(lv) + ")|r")
    endif
    if k == 5 and kt >= 0 and g < 8 then
        call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040The last Pokemon uses " + Ty_Name[kt] + " moves: strong against your Pokemon!|r")
    endif
    set u = null
endfunction

function Gym_Tick takes nothing returns nothing
    local integer g = 0
    local integer k = 0
    local integer pid = 0
    local unit u = null
    local real dx = 0.0
    local real dy = 0.0
    local boolean started = false
    loop
        exitwhen g >= 8
        set k = 0
        loop  // dead gym Pokemon are heroes (they do not decay): remove them
            exitwhen k >= 6
            if Gym_Dead[g * 6 + k] != null and GetWidgetLife(Gym_Dead[g * 6 + k]) <= 0.405 then
                call RemoveUnit(Gym_Dead[g * 6 + k])
                set Gym_Dead[g * 6 + k] = null
            endif
            set k = k + 1
        endloop
        if Gym_Pid[g] >= 0 then
            if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or Gym_Down(g, Gym_Hero[g]) then  // v3.4.5: Revive
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you lost. The gym starts over.|r")
                call Gym_Reset(g)
            elseif Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0 then
                set Gym_Cur[g] = null  // v3.4.3: the gym Pokemon was removed / replaced: bring it back
                call Gym_Spawn(g, Gym_Stage[g])
            else
                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]
                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]
                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                endif
            endif
        else
            set started = false
            call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)
            loop
                set u = FirstOfGroup(Wild_Tmp)
                exitwhen u == null
                call GroupRemoveUnit(Wild_Tmp, u)
                set pid = GetPlayerId(GetOwningPlayer(u))
                if not started and pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' and not Gym_Busy(pid) and not (g == 7 and League_Pid >= 0) then
                    if not Gym_Allowed(pid, g) then
                        if Mega_Time >= Gym_Warn[pid] then
                            set Gym_Warn[pid] = Mega_Time + 10.0
                            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + " is locked: you can challenge gyms 1-" + I2S(2 * (Gym_Milestone(pid) + 1)) + " (clear 2 gyms to open 2 more).|r")
                        endif
                    elseif Mega_Time < Gym_PCool[pid * 8 + g] then
                        if Mega_Time >= Gym_Warn[pid] then
                            set Gym_Warn[pid] = Mega_Time + 2.0
                            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 3.0, "|cffffcc00Gym " + I2S(g + 1) + ": ready again in " + I2S(R2I(Gym_PCool[pid * 8 + g] - Mega_Time + 0.99)) + "s.|r")
                        endif
                    else
                        set started = true
                        set Gym_Pid[g] = pid
                        set Gym_Hero[g] = u
                        set Fx_ArgK = g  // v3.4.16
                        call ExecuteFunc("Fx_LeaderHiX")
                        set Gym_Base[g] = GetHeroLevel(u)
                        set Gym_Stage[g] = 0
                        set Gym_DownSince[g] = 0.0
                        // v3.4: the challenger starts with full HP and mana
                        call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
                        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
                        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
                        call Gym_BuildTeam(g, u)
                        call Gym_Spawn(g, 0)
                    endif
                endif
            endloop
        endif
        set g = g + 1
    endloop
    set u = null
endfunction

function Gym_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    local integer g = 0
    local integer pid = 0
    loop
        exitwhen g >= 8
        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then
            call Gym_ClearItems(d)  // v3.3.2: gym Pokemon drop nothing but the badge
            set Gym_Dead[g * 6 + Gym_Stage[g]] = d
            set Gym_Cur[g] = null
            set Gym_Stage[g] = Gym_Stage[g] + 1
            if Gym_Stage[g] >= 6 then
                set pid = Gym_Pid[g]
                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
                set Badge_Has[pid * 8 + g] = true
                set Fx_ArgU = Gym_Hero[g]  // v3.4.16
                set Fx_ArgK = g
                call ExecuteFunc("Fx_BadgeX")
                call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(pid)) + "/8, level cap " + I2S(Badge_Cap(pid)) + ".|r")
                set Gym_PCool[pid * 8 + g] = Mega_Time + Gym_ClearCool
                call Gym_Reset(g)
            else
                call Gym_Spawn(g, Gym_Stage[g])
            endif
        endif
        set g = g + 1
    endloop
    set d = null
    return false
endfunction

function Chat_Init takes nothing returns nothing
    call TriggerAddAction(t, function League_OnChat)
    set t = null
endfunction
