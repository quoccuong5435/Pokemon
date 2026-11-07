// v3.4: Pokemon 1..5 are 5, 4, 3, 2, 1 levels below the challenger, Pokemon 6 equals it
// (v3.3 had 30, 25, 20, 15, 10 below: a level 30 challenger met level 1 and level 5 Pokemon)
function Gym_Level takes integer base, integer k returns integer
    local integer lv = base
    if k < 5 then
        set lv = base - (5 - k)
    endif
    if lv > 100 then
        set lv = 100
    endif
    if lv < 1 then
        set lv = 1
    endif
    return lv
endfunction

function Gym_Busy takes integer pid returns boolean
    local integer g = 0
    if League_Pid == pid then  // v3.4: the Elite Four counts as a gym battle
        return true
    endif
    loop
        exitwhen g >= 8
        if Gym_Pid[g] == pid then
            return true
        endif
        set g = g + 1
    endloop
    return false
endfunction

// v3.4: the form of evolution line `root` at level lv: follow the evolutions whose level is reached (Ab_HT of the
// unit type: 299 = number, 300 + 2k = evolved type, 301 + 2k = level), a random branch when there are several (Eevee)
function Gym_FormAt takes integer root, integer lv returns integer
    local integer cur = root
    local integer k = 0
    local integer n = 0
    local integer cnt = 0
    local integer pick = 0
    local integer nxt = 0
    local integer guard = 0
    loop
        exitwhen guard >= 4
        set cnt = LoadInteger(Ab_HT, cur, 299)
        set n = 0
        set k = 0
        loop
            exitwhen k >= cnt
            if lv >= LoadInteger(Ab_HT, cur, 301 + 2 * k) then
                set n = n + 1
            endif
            set k = k + 1
        endloop
        exitwhen n == 0
        set pick = GetRandomInt(1, n)
        set nxt = 0
        set k = 0
        loop
            exitwhen k >= cnt or nxt != 0
            if lv >= LoadInteger(Ab_HT, cur, 301 + 2 * k) then
                set pick = pick - 1
                if pick == 0 then
                    set nxt = LoadInteger(Ab_HT, cur, 300 + 2 * k)
                endif
            endif
            set k = k + 1
        endloop
        exitwhen nxt == 0
        set cur = nxt
        set guard = guard + 1
    endloop
    return cur
endfunction

// v3.4: the 6 Pokemon of a challenge, chosen when it starts: 6 different evolution lines (first forms of Gym_Pool),
// each in the form of its level (lv 35 Charmeleon, lv 36 Charizard). The 6th one must have a type that hits the
// challenger super effectively, and it gets the skills of that type.
function Gym_BuildTeam takes integer g, unit hero returns nothing
    local integer k = 0
    local integer j = 0
    local integer tries = 0
    local integer root = 0
    local integer form = 0
    local integer lv = 0
    local integer def = GetUnitTypeId(hero)
    local boolean ok = false
    loop
        exitwhen k >= 6
        set lv = Gym_Level(Gym_Base[g], k)
        set tries = 0
        loop
            if Gym_PoolN > 0 then
                set root = Gym_Pool[GetRandomInt(0, Gym_PoolN - 1)]
                set form = Gym_FormAt(root, lv)
            else
                set root = Wild_PickType(lv / 10 + 1)
                set form = root
            endif
            set ok = true
            set j = 0
            loop
                exitwhen j >= k
                if Gym_Root[g * 6 + j] == root then
                    set ok = false
                endif
                set j = j + 1
            endloop
            if ok and k == 5 and tries < 100 then
                set ok = Ty_Counters(form, def)
            endif
            set tries = tries + 1
            exitwhen ok or tries >= 150
        endloop
        set Gym_Root[g * 6 + k] = root
        set Gym_Team[g * 6 + k] = form
        if k == 5 then
            set Gym_TeamKit[g * 6 + k] = Ty_BestVs(form, def)
        else
            set Gym_TeamKit[g * 6 + k] = Ty_OfType(form, 0)
        endif
        set k = k + 1
    endloop
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
    if id == 0 or Ty_OfType(id, 0) < 0 then  // v3.4.2: an empty or broken team slot gets a Pokemon of the pool
        set id = Gym_FormAt(Gym_Pool[GetRandomInt(0, Gym_PoolN - 1)], lv)
        set Gym_Team[g * 6 + k] = id
        set ty = Ty_OfType(id, 0)
        if kt < 0 then
            set kt = ty
        endif
    endif
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), id, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
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
    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult * Gym_DiffHP[g]))
    call SetUnitLifePercentBJ(u, 100.0)
    call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8 * Gym_DiffDmg[g]), 0)
    call BlzSetUnitDiceNumber(u, 1, 0)
    call BlzSetUnitDiceSides(u, 4, 0)
    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m * Gym_DiffDmg[g])
    if Gym_Fast[g] then  // v3.4.2: gyms 1-4 do not get the 1.7x attack speed
        call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Hero_ASBoost, 0)
    endif
    call SaveReal(Ab_HT, h, 88, Gym_DiffAI[g])  // skill-cast chance of Ai_Tick
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
    if ti != 0 then
        if UnitInventorySize(u) == 0 then
            call UnitAddAbility(u, 'AInv')
        endif
        call SetItemDropOnDeath(UnitAddItemById(u, ti), false)
    endif
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

// v3.4: no gym cool-down for anybody any more (Gym_PCool keeps the 5s of the player who just cleared it)
function Gym_Reset takes integer g returns nothing
    if Gym_Cur[g] != null then
        call RemoveUnit(Gym_Cur[g])
    endif
    set Gym_Cur[g] = null
    set Gym_Hero[g] = null
    set Gym_Pid[g] = -1
    set Gym_Stage[g] = 0
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
            if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or GetWidgetLife(Gym_Hero[g]) <= 0.405 then
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you lost. The gym starts over.|r")
                call Gym_Reset(g)
            else
                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]
                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]
                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                elseif Gym_Stage[g] < 6 and (Gym_Cur[g] == null or GetUnitTypeId(Gym_Cur[g]) == 0) then
                    // v3.4.1: the current gym Pokemon vanished (removed or replaced): bring it back
                    set Gym_ArgG = g
                    set Gym_ArgK = Gym_Stage[g]
                    call ExecuteFunc("Gym_SpawnIt")
                elseif GetWidgetLife(Gym_Cur[g]) <= 0.405 then
                    // v3.4.2: it died but the death trigger did not move the gym on
                    set Gym_ArgG = g
                    call ExecuteFunc("Gym_AdvanceIt")
                else
                    set dx = GetUnitX(Gym_Cur[g]) - Gym_X[g]
                    set dy = GetUnitY(Gym_Cur[g]) - Gym_Y[g]
                    if SquareRoot(dx * dx + dy * dy) > Gym_Leave then  // v3.4.2: it wandered off: back to the gym
                        call SetUnitPosition(Gym_Cur[g], Gym_X[g], Gym_Y[g])
                    endif
                endif
            endif
            if Gym_Pid[g] >= 0 then  // v3.4.1: tell the other players near the gym that it is busy
                call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)
                loop
                    set u = FirstOfGroup(Wild_Tmp)
                    exitwhen u == null
                    call GroupRemoveUnit(Wild_Tmp, u)
                    set pid = GetPlayerId(GetOwningPlayer(u))
                    if pid < 12 and pid != Gym_Pid[g] and IsUnitType(u, UNIT_TYPE_HERO) and Mega_Time >= Gym_Warn[pid] then
                        set Gym_Warn[pid] = Mega_Time + 5.0
                        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Gym " + I2S(g + 1) + " is busy: " + GetPlayerName(Player(Gym_Pid[g])) + " is challenging it (Pokemon " + I2S(Gym_Stage[g] + 1) + " of 6). Wait for your turn or try another gym.|r")
                    endif
                endloop
            endif
        else
            set started = false
            call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)
            loop
                set u = FirstOfGroup(Wild_Tmp)
                exitwhen u == null
                call GroupRemoveUnit(Wild_Tmp, u)
                set pid = GetPlayerId(GetOwningPlayer(u))
                if not started and pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' and not Gym_Busy(pid) then
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
                        set Gym_Base[g] = GetHeroLevel(u)
                        set Gym_Stage[g] = 0
                        // v3.4: the challenger starts with full HP and mana
                        call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
                        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
                        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
                        set Gym_ArgG = g  // v3.4.2: team + first Pokemon in their own thread (op limit)
                        call ExecuteFunc("Gym_StartIt")
                    endif
                endif
            endloop
        endif
        set g = g + 1
    endloop
    set u = null
endfunction

function Gym_ClearItems takes unit d returns nothing
    local integer s = 0
    local item it = null
    loop
        exitwhen s >= 6
        set it = UnitItemInSlot(d, s)
        if it != null then
            call RemoveItem(it)
        endif
        set s = s + 1
    endloop
    set it = null
endfunction

// the current gym Pokemon d of gym g is down: next one, or the badge after the 6th
function Gym_Advance takes integer g, unit d returns nothing
    local integer pid = Gym_Pid[g]
    call Gym_ClearItems(d)  // v3.3.2: gym Pokemon drop nothing but the badge
    set Gym_Dead[g * 6 + Gym_Stage[g]] = d
    set Gym_Cur[g] = null
    set Gym_Stage[g] = Gym_Stage[g] + 1
    if Gym_Stage[g] >= 6 then
        call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
        set Badge_Has[pid * 8 + g] = true
        call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(pid)) + "/8, level cap " + I2S(Badge_Cap(pid)) + ".|r")
        set Gym_PCool[pid * 8 + g] = Mega_Time + Gym_ClearCool
        call Gym_Reset(g)
    else
        set Gym_ArgG = g
        set Gym_ArgK = Gym_Stage[g]
        call ExecuteFunc("Gym_SpawnIt")  // v3.4.2: own thread (op limit)
    endif
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

function Gym_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    local integer g = 0
    loop
        exitwhen g >= 8
        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then
            call Gym_Advance(g, d)
        endif
        set g = g + 1
    endloop
    set d = null
    return false
endfunction

// ---------------------------------------------------------------------------------------------
// v3.4 Elite Four + Champion ("-league" or walking into the arena circle with 8 badges): 5 battles in a row in the
// League arena (Darkrai's old room since v3.4.2; gym slot 8 of the Gym_* arrays), 6 Pokemon of one type each (Will Psychic, Koga Poison, Bruno Fighting, Karen Dark), then Champion
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
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
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
    call SetUnitPosition(League_Unit, League_LX, League_LY)  // v3.4.2: back to the lobby
    call PanCameraToTimedForPlayer(p, League_LX, League_LY, 0.3)
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
    elseif League_Pid >= 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00The League arena is busy: " + GetPlayerName(Player(League_Pid)) + " is challenging it. Try again soon.|r")
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
        set Gym_X[8] = League_AX  // v3.4.2: the arena in Darkrai's room
        set Gym_Y[8] = League_AY
        call SetUnitPosition(u, League_AX + 450.0, League_AY)
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
    local unit u = null
    local integer pid = 0
    loop
        exitwhen k >= 6
        if Gym_Dead[48 + k] != null and GetWidgetLife(Gym_Dead[48 + k]) <= 0.405 then
            call RemoveUnit(Gym_Dead[48 + k])
            set Gym_Dead[48 + k] = null
        endif
        set k = k + 1
    endloop
    if League_Pid < 0 then  // v3.4.2: a hero that walks into the arena circle starts the League
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
        if League_Unit == null or GetUnitTypeId(League_Unit) == 0 or GetWidgetLife(League_Unit) <= 0.405 then
            call League_Lose("you lost.")
        else
            set dx = GetUnitX(League_Unit) - Gym_X[8]
            set dy = GetUnitY(League_Unit) - Gym_Y[8]
            if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                call League_Lose("you left the arena.")
            elseif Gym_Stage[8] < 6 and (Gym_Cur[8] == null or GetUnitTypeId(Gym_Cur[8]) == 0) then
                call Gym_Spawn(8, Gym_Stage[8])
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
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportCaster.mdl", GetUnitX(u), GetUnitY(u)))
            call SetUnitPosition(u, tx, ty)
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", tx, ty))
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
