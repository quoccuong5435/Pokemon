//MEGA_GLOBALS_BEGIN
hashtable Mega_HT = InitHashtable()
group Mega_Group = CreateGroup()
group Mega_Tmp = CreateGroup()
timer Mega_Timer = CreateTimer()
real Mega_Time = 0.0
real Mega_Duration = 60.0
real Mega_Cooldown = 150.0
integer Mega_N = 16
integer Mega_KangIdx = 8
integer Mega_KidId = 'hMK0'
integer array Mega_Base
integer array Mega_Stone
integer array Mega_Skin
integer array Mega_Evolve
integer array Mega_PStr
integer array Mega_PAgi
integer array Mega_PInt
integer Mega_PctPerPoint = 3
real Mega_DamageBonus = 0.5
integer array Mega_Price
integer array Mega_R
integer array Mega_G
integer array Mega_B
real array Mega_Scale
real array Mega_BaseScale
string array Mega_Name
string array Mega_StoneName
string array Mega_Fx
// wild creeps: tiers every 5 minutes, respawning camps
timer Wild_Timer = CreateTimer()
group Wild_Tmp = CreateGroup()
real Wild_Time = 0.0
real Wild_LevelCheck = 300.0
real Wild_NextCheck = 0.0
integer Wild_LevelsPerTier = 10
integer Wild_AvgLevel = 1
integer Wild_TierMax = 10
real Wild_TierStep = 0.15
integer Wild_TierArmor = 2
real Wild_Respawn = 60.0
real Wild_CampRadius = 600.0
integer Wild_Tier = 0
integer Wild_TypeN = 0
integer array Wild_Type
integer Wild_PoolN = 0
integer array Wild_Pool
integer array Wild_PoolPow
integer Wild_CampN = 0
real array Wild_CampX
real array Wild_CampY
integer array Wild_CampSize
integer array Wild_CampPow
integer array Wild_CampAlive
real array Wild_CampDue
// random legends (lv 100, only lv 100 Pokemon can hurt them) and Souls dropped by wild creeps
integer Leg_N = 0
integer array Leg_Type
integer array Leg_Soul
string array Leg_Name
integer Leg_Alive = 0
integer Leg_Max = 2
real Leg_Interval = 300.0
real Leg_Next = 300.0
integer Leg_SoulChance = 50
integer Leg_MinLevel = 100
real array Leg_Warned
group Leg_Tmp = CreateGroup()
real Wild_SoulChance = 0.5
// own-species Souls added in v2.6 (transform in the circle at the map centre, rect Hi of the map script)
integer Soul_N = 0
integer array Soul_Item
integer array Soul_Hero
// "t la ga" / "chicken": once per player, +10 levels and +3000 gold
integer Chicken_Levels = 10
integer Chicken_Gold = 3000
boolean array Chicken_Used
// random starter: "-random" and automatic random for players still holding the picker wisp
timer Rand_Timer = CreateTimer()
group Rand_Tmp = CreateGroup()
real Rand_AutoSeconds = 45.0
integer Rand_N = 0
integer array Rand_Type
// repick: first 2 minutes, twice per player; XP and items carry over (items kept under parent key 900 + player id)
real Repick_Window = 120.0
integer Repick_Max = 2
integer array Repick_Count
integer array Repick_XP
boolean array Repick_Pending
// evolutions of the new Pokemon (level based and item based)
integer Evo_N = 0
integer array Evo_From
integer array Evo_To
integer array Evo_Level
integer Evo_ItemN = 0
integer array Evo_ItemFrom
integer array Evo_Item
integer array Evo_ItemTo
// Pokemon Abilities (v2.8): data filled by Ab_InitData; effect e of Ability a is e = a*2 + k
hashtable Ab_HT = InitHashtable()
integer Ab_N = 0
integer array Ab_Fam
real array Ab_X
real array Ab_Y
real array Ab_Z
real array Ab_W
string array Ab_S
integer array Ab_Raw
string array Ab_Name
string array Ab_Info
integer array Ab_MegaAb
// effect families (ability_data.FAMILY order)
constant integer Ab_F_PINCH = 1
constant integer Ab_F_CONTACT = 2
constant integer Ab_F_ABSORB = 3
constant integer Ab_F_INTIMIDATE = 4
constant integer Ab_F_PRESSURE = 5
constant integer Ab_F_STURDY = 6
constant integer Ab_F_DEFENSE = 7
constant integer Ab_F_MULTISCALE = 8
constant integer Ab_F_RECOVERY = 9
constant integer Ab_F_POWER = 10
constant integer Ab_F_RISING = 11
constant integer Ab_F_SPEED = 12
constant integer Ab_F_LUCKY = 13
constant integer Ab_F_DODGE = 14
constant integer Ab_F_AURA = 15
constant integer Ab_F_REFLECT = 16
constant integer Ab_F_MULTITYPE = 17
constant integer Ab_F_SLOWSTART = 18
// skill damage scales with the hero's main attribute: 1 + K * (stat - Base), at most Max
constant real Ab_ScaleK = 0.011
constant real Ab_ScaleBase = 50.0
constant real Ab_ScaleMax = 10.0
// timed effects on units (dot, slow, stun), one slot per effect
constant integer Ab_FxMax = 64
unit array Ab_FxU
integer array Ab_FxKind
real array Ab_FxEnd
real array Ab_FxAmt
boolean Ab_Busy = false
integer Ab_Beat = 0
group Ab_Group = CreateGroup()
group Ab_Tmp = CreateGroup()
timer Ab_Timer = CreateTimer()
//MEGA_GLOBALS_END
//MEGA_PRELUDE_BEGIN
// Replaces every ReplaceUnitBJ of the original map (inserted right after endglobals so all triggers can use it).
// An evolution trigger runs once per level gained and waits 1.5s; several level-ups inside that wait used to
// replace the same unit several times, leaving duplicate Pokemon. Only the first replacement of a unit counts.
function Mega_SafeReplace takes unit u, integer newId, integer method returns nothing
    local integer h = GetHandleId(u)
    if u == null or GetUnitTypeId(u) == 0 or GetUnitTypeId(u) == newId then
        return
    endif
    if HaveSavedReal(Mega_HT, h, 9) and Mega_Time - LoadReal(Mega_HT, h, 9) < 10.0 then
        return
    endif
    call SaveReal(Mega_HT, h, 9, Mega_Time)
    call ReplaceUnitBJ(u, newId, method)
endfunction
//MEGA_PRELUDE_END
// ---------------------------------------------------------------------------------------------
// Mega Evolution (Pokemon Arena v2.0). Per-unit state in Mega_HT, parent key = handle id:
//   0 = active mega index + 1 (0 = not mega), 1 = end time, 2 = original proper name,
//   3 = aura effect, 4 = Kangaskhan Kid, 5 = last Kid hit time, 100 + i = cooldown end of button i
// ---------------------------------------------------------------------------------------------
function Mega_HasStone takes unit u, integer idx returns boolean
    local integer i = 0
    local integer n = UnitInventorySize(u)
    loop
        exitwhen i >= n
        if GetItemTypeId(UnitItemInSlot(u, i)) == Mega_Stone[idx] then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// add / remove the Mega Evolve buttons of a hero that is not in Mega form
function Mega_SyncAbility takes unit u returns nothing
    local integer id = GetUnitTypeId(u)
    local integer h = GetHandleId(u)
    local integer i = 0
    local real left = 0.0
    loop
        exitwhen i >= Mega_N
        if Mega_Base[i] == id then
            if Mega_HasStone(u, i) then
                if GetUnitAbilityLevel(u, Mega_Evolve[i]) == 0 then
                    call UnitAddAbility(u, Mega_Evolve[i])
                    set left = LoadReal(Mega_HT, h, 100 + i) - Mega_Time
                    if left > 0.0 then
                        call BlzStartUnitAbilityCooldown(u, Mega_Evolve[i], left)
                    endif
                endif
            elseif GetUnitAbilityLevel(u, Mega_Evolve[i]) > 0 then
                set left = BlzGetUnitAbilityCooldownRemaining(u, Mega_Evolve[i])
                call SaveReal(Mega_HT, h, 100 + i, Mega_Time + left)
                call UnitRemoveAbility(u, Mega_Evolve[i])
            endif
        endif
        set i = i + 1
    endloop
endfunction

function Mega_KidFollow takes unit u, unit kid returns nothing
    local real a = (GetUnitFacing(u) + 150.0) * bj_DEGTORAD
    local real tx = GetUnitX(u) + 90.0 * Cos(a)
    local real ty = GetUnitY(u) + 90.0 * Sin(a)
    local real dx = tx - GetUnitX(kid)
    local real dy = ty - GetUnitY(kid)
    local real d = SquareRoot(dx * dx + dy * dy)
    if d > 600.0 then
        call SetUnitPosition(kid, tx, ty)
        call SetUnitFacing(kid, GetUnitFacing(u))
    elseif d > 50.0 then
        call IssuePointOrder(kid, "move", tx, ty)
    else
        call SetUnitFacing(kid, GetUnitFacing(u))
    endif
endfunction

function Mega_End takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer idx = LoadInteger(Mega_HT, h, 0) - 1
    local effect fx = null
    local unit kid = null
    if idx < 0 then
        return
    endif
    set fx = LoadEffectHandle(Mega_HT, h, 3)
    set kid = LoadUnitHandle(Mega_HT, h, 4)
    call SaveInteger(Mega_HT, h, 0, 0)
    call GroupRemoveUnit(Mega_Group, u)
    if fx != null then
        call DestroyEffect(fx)
        call RemoveSavedHandle(Mega_HT, h, 3)
    endif
    if kid != null then
        call RemoveUnit(kid)
        call RemoveSavedHandle(Mega_HT, h, 4)
    endif
    if GetUnitTypeId(u) != 0 then
        // remove exactly the bonus Mega_Start added (stats may have grown meanwhile)
        call SetHeroStr(u, GetHeroStr(u, false) - LoadInteger(Mega_HT, h, 10), true)
        call SetHeroAgi(u, GetHeroAgi(u, false) - LoadInteger(Mega_HT, h, 11), true)
        call SetHeroInt(u, GetHeroInt(u, false) - LoadInteger(Mega_HT, h, 12), true)
        call BlzSetUnitBaseDamage(u, BlzGetUnitBaseDamage(u, 0) - LoadInteger(Mega_HT, h, 13), 0)
        call UnitRemoveAbility(u, 'AMB1')
        call UnitRemoveAbility(u, 'AMB2')
        call UnitRemoveAbility(u, 'AMB3')
        call BlzSetUnitSkin(u, GetUnitTypeId(u))
        call SetUnitScale(u, Mega_BaseScale[idx], Mega_BaseScale[idx], Mega_BaseScale[idx])
        call SetUnitVertexColor(u, 255, 255, 255, 255)
        call BlzSetHeroProperName(u, LoadStr(Mega_HT, h, 2))
        call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\DispelMagic\\DispelMagicTarget.mdl", GetUnitX(u), GetUnitY(u)))
    endif
    set fx = null
    set kid = null
endfunction

function Mega_Start takes unit u, integer idx returns nothing
    local integer h = GetHandleId(u)
    local integer i = 0
    local player p = GetOwningPlayer(u)
    local integer bs = 0
    local integer b_agi = 0
    local integer bi = 0
    local integer bd = 0
    if LoadInteger(Mega_HT, h, 0) > 0 then
        set p = null
        return
    endif
    // stat bonus = points * 3% of the current stat (at least the points themselves)
    set bs = R2I(I2R(GetHeroStr(u, true)) * I2R(Mega_PStr[idx] * Mega_PctPerPoint) / 100.0)
    if bs < Mega_PStr[idx] then
        set bs = Mega_PStr[idx]
    endif
    set b_agi = R2I(I2R(GetHeroAgi(u, true)) * I2R(Mega_PAgi[idx] * Mega_PctPerPoint) / 100.0)
    if b_agi < Mega_PAgi[idx] then
        set b_agi = Mega_PAgi[idx]
    endif
    set bi = R2I(I2R(GetHeroInt(u, true)) * I2R(Mega_PInt[idx] * Mega_PctPerPoint) / 100.0)
    if bi < Mega_PInt[idx] then
        set bi = Mega_PInt[idx]
    endif
    // damage bonus = 50% of (base damage + highest stat)
    set bd = GetHeroStr(u, true)
    if GetHeroAgi(u, true) > bd then
        set bd = GetHeroAgi(u, true)
    endif
    if GetHeroInt(u, true) > bd then
        set bd = GetHeroInt(u, true)
    endif
    set bd = R2I(Mega_DamageBonus * I2R(BlzGetUnitBaseDamage(u, 0) + bd))
    call SaveInteger(Mega_HT, h, 10, bs)
    call SaveInteger(Mega_HT, h, 11, b_agi)
    call SaveInteger(Mega_HT, h, 12, bi)
    call SaveInteger(Mega_HT, h, 13, bd)
    call SaveInteger(Mega_HT, h, 0, idx + 1)
    call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration)
    call SaveStr(Mega_HT, h, 2, GetHeroProperName(u))
    // X and Y buttons of the same Pokemon share the cooldown
    loop
        exitwhen i >= Mega_N
        if Mega_Base[i] == Mega_Base[idx] then
            call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown)
            if i != idx and GetUnitAbilityLevel(u, Mega_Evolve[i]) > 0 then
                call BlzStartUnitAbilityCooldown(u, Mega_Evolve[i], Mega_Cooldown)
            endif
        endif
        set i = i + 1
    endloop
    call GroupAddUnit(Mega_Group, u)
    call BlzSetUnitSkin(u, Mega_Skin[idx])
    call SetUnitScale(u, Mega_Scale[idx], Mega_Scale[idx], Mega_Scale[idx])
    call SetUnitVertexColor(u, Mega_R[idx], Mega_G[idx], Mega_B[idx], 255)
    call BlzSetHeroProperName(u, Mega_Name[idx])
    call SetHeroStr(u, GetHeroStr(u, false) + bs, true)
    call SetHeroAgi(u, GetHeroAgi(u, false) + b_agi, true)
    call SetHeroInt(u, GetHeroInt(u, false) + bi, true)
    call BlzSetUnitBaseDamage(u, BlzGetUnitBaseDamage(u, 0) + bd, 0)
    call UnitAddAbility(u, 'AMB1')
    call UnitAddAbility(u, 'AMB2')
    call UnitAddAbility(u, 'AMB3')
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl", GetUnitX(u), GetUnitY(u)))
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Items\\AIim\\AIimTarget.mdl", GetUnitX(u), GetUnitY(u)))
    if Mega_Fx[idx] != "" then
        call SaveEffectHandle(Mega_HT, h, 3, AddSpecialEffectTarget(Mega_Fx[idx], u, "origin"))
    endif
    if idx == Mega_KangIdx then
        call SaveUnitHandle(Mega_HT, h, 4, CreateUnit(p, Mega_KidId, GetUnitX(u), GetUnitY(u), GetUnitFacing(u)))
        call SaveReal(Mega_HT, h, 5, 0.0)
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, GetPlayerName(p) + "'s " + LoadStr(Mega_HT, h, 2) + " Mega Evolved into |cffff66cc" + Mega_Name[idx] + "|r!")
    set p = null
endfunction

// ---------------------------------------------------------------------------------------------
// Wild creeps. Per-unit keys in Mega_HT: 20 base max HP, 21 base damage, 22 base armor, 23 base gold,
// 24 applied tier + 1, 25 camp + 1. Wild unit types are marked with key 7 under their type id.
// ---------------------------------------------------------------------------------------------
function Wild_IsWildType takes integer id returns boolean
    return LoadBoolean(Mega_HT, id, 7)
endfunction

// scale a wild creep to the current tier, always from its stored base values
function Wild_Apply takes unit u returns nothing
    local integer h = GetHandleId(u)
    local real m = 1.0 + Wild_TierStep * I2R(Wild_Tier)
    local real pct = 0.0
    if LoadInteger(Mega_HT, h, 24) == Wild_Tier + 1 then
        return
    endif
    if LoadInteger(Mega_HT, h, 24) == 0 then
        call SaveInteger(Mega_HT, h, 20, BlzGetUnitMaxHP(u))
        call SaveInteger(Mega_HT, h, 21, BlzGetUnitBaseDamage(u, 0))
        call SaveReal(Mega_HT, h, 22, BlzGetUnitArmor(u))
        call SaveInteger(Mega_HT, h, 23, BlzGetUnitIntegerField(u, UNIT_IF_GOLD_BOUNTY_AWARDED_BASE))
    endif
    call SaveInteger(Mega_HT, h, 24, Wild_Tier + 1)
    if Wild_Tier == 0 then
        return
    endif
    set pct = GetUnitLifePercent(u)
    call BlzSetUnitMaxHP(u, R2I(I2R(LoadInteger(Mega_HT, h, 20)) * m))
    call SetUnitLifePercentBJ(u, pct)
    call BlzSetUnitBaseDamage(u, R2I(I2R(LoadInteger(Mega_HT, h, 21)) * m), 0)
    call BlzSetUnitArmor(u, LoadReal(Mega_HT, h, 22) + I2R(Wild_Tier * Wild_TierArmor))
    call BlzSetUnitIntegerField(u, UNIT_IF_GOLD_BOUNTY_AWARDED_BASE, R2I(I2R(LoadInteger(Mega_HT, h, 23)) * m))
endfunction

// shown level of a wild creep = max(its own level, average hero level); key 26 own level, 27 applied level
function Wild_ApplyLevel takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer lv = 0
    if not HaveSavedInteger(Mega_HT, h, 26) then
        call SaveInteger(Mega_HT, h, 26, GetUnitLevel(u))
    endif
    set lv = LoadInteger(Mega_HT, h, 26)
    if Wild_AvgLevel > lv then
        set lv = Wild_AvgLevel
    endif
    if LoadInteger(Mega_HT, h, 27) != lv then
        call SaveInteger(Mega_HT, h, 27, lv)
        call BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, lv)
    endif
endfunction

function Wild_Scan takes nothing returns nothing
    local unit u = null
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if not IsUnitType(u, UNIT_TYPE_DEAD) and Wild_IsWildType(GetUnitTypeId(u)) then
            call Wild_Apply(u)
            call Wild_ApplyLevel(u)
        endif
    endloop
endfunction

// tier = average level of the players' Pokemon / 10 (max 10)
// every 5 minutes: tier = average level of the 2 lowest players / 10 (each player = their highest hero)
function Wild_UpdateTier takes nothing returns nothing
    local integer i = 0
    local integer n = 0
    local integer best = 0
    local integer low_a = 0
    local integer low_b = 0
    local integer t = 0
    local unit u = null
    loop
        exitwhen i >= 12
        set best = 0
        call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(i), null)
        loop
            set u = FirstOfGroup(Wild_Tmp)
            exitwhen u == null
            call GroupRemoveUnit(Wild_Tmp, u)
            if IsUnitType(u, UNIT_TYPE_HERO) and GetUnitTypeId(u) != 'earc' and GetHeroLevel(u) > best then
                set best = GetHeroLevel(u)
            endif
        endloop
        if best > 0 then
            set n = n + 1
            if n == 1 or best < low_a then
                set low_b = low_a
                set low_a = best
            elseif n == 2 or best < low_b then
                set low_b = best
            endif
        endif
        set i = i + 1
    endloop
    if n == 0 then
        return
    endif
    if n == 1 then
        set Wild_AvgLevel = low_a
    else
        set Wild_AvgLevel = (low_a + low_b) / 2
    endif
    set t = Wild_AvgLevel / Wild_LevelsPerTier
    if t > Wild_TierMax then
        set t = Wild_TierMax
    endif
    if t > Wild_Tier then
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff8800Wild Pokemon grew stronger! (Tier " + I2S(t) + ", average level " + I2S(Wild_AvgLevel) + ")|r")
    endif
    set Wild_Tier = t
endfunction

// pick a random pool type of the wanted power (or the closest lower power that exists)
function Wild_PickType takes integer pow returns integer
    local integer p = pow
    local integer i = 0
    local integer n = 0
    local integer k = 0
    loop
        exitwhen p < 1
        set n = 0
        set i = 0
        loop
            exitwhen i >= Wild_PoolN
            if Wild_PoolPow[i] == p then
                set n = n + 1
            endif
            set i = i + 1
        endloop
        if n > 0 then
            set k = GetRandomInt(1, n)
            set i = 0
            loop
                exitwhen i >= Wild_PoolN
                if Wild_PoolPow[i] == p then
                    set k = k - 1
                    if k == 0 then
                        return Wild_Pool[i]
                    endif
                endif
                set i = i + 1
            endloop
        endif
        set p = p - 1
    endloop
    return Wild_Pool[0]
endfunction

function Wild_SpawnCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer t = 0
    local integer i = 0
    local unit u = null
    if pow > 10 then
        set pow = 10
    endif
    set t = Wild_PickType(pow)
    set Wild_CampDue[c] = 0.0
    set Wild_CampAlive[c] = Wild_CampSize[c]
    loop
        exitwhen i >= Wild_CampSize[c]
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), t, Wild_CampX[c] + GetRandomReal(-150.0, 150.0), Wild_CampY[c] + GetRandomReal(-150.0, 150.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call Wild_Apply(u)
        set i = i + 1
    endloop
    set u = null
endfunction

// ---------------------------------------------------------------------------------------------
// Random legends
// ---------------------------------------------------------------------------------------------
function Leg_IsLegend takes integer id returns boolean
    local integer i = 0
    loop
        exitwhen i >= Leg_N
        if Leg_Type[i] == id then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// highest hero level of a player (damage may come from a skill dummy, so look at the owner)
function Leg_PlayerLevel takes player p returns integer
    local unit u = null
    local integer best = 0
    call GroupEnumUnitsOfPlayer(Leg_Tmp, p, null)
    loop
        set u = FirstOfGroup(Leg_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Leg_Tmp, u)
        if IsUnitType(u, UNIT_TYPE_HERO) and GetHeroLevel(u) > best then
            set best = GetHeroLevel(u)
        endif
    endloop
    return best
endfunction

function Leg_Spawn takes nothing returns nothing
    local integer i = 0
    local integer c = 0
    local real x = 0.0
    local real y = 0.0
    if Leg_N == 0 then
        return
    endif
    set i = GetRandomInt(0, Leg_N - 1)
    if Wild_CampN > 0 then
        set c = GetRandomInt(0, Wild_CampN - 1)
        set x = Wild_CampX[c]
        set y = Wild_CampY[c]
    endif
    call CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Leg_Type[i], x, y, 270.0)
    set Leg_Alive = Leg_Alive + 1
    call PingMinimap(x, y, 5.0)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff66ccA wild " + Leg_Name[i] + " (Lv 100) appeared! Only level 100 Pokemon can hurt it.|r")
endfunction

function Leg_OnDamage takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local player p = null
    local integer pid = 0
    if Leg_IsLegend(GetUnitTypeId(t)) then
        set p = GetOwningPlayer(GetEventDamageSource())
        set pid = GetPlayerId(p)
        if pid < 12 and Leg_PlayerLevel(p) < Leg_MinLevel then
            call BlzSetEventDamage(0.0)
            if Mega_Time - Leg_Warned[pid] > 3.0 then
                set Leg_Warned[pid] = Mega_Time
                call DisplayTimedTextToPlayer(p, 0, 0, 3.0, "|cffff0000Only level 100 Pokemon can hurt " + GetUnitName(t) + "!|r")
            endif
        endif
    endif
    set t = null
    set p = null
    return false
endfunction

function Leg_OnDeath takes unit u returns nothing
    local integer i = 0
    loop
        exitwhen i >= Leg_N
        if Leg_Type[i] == GetUnitTypeId(u) then
            set Leg_Alive = Leg_Alive - 1
            if GetRandomInt(1, 100) <= Leg_SoulChance then
                call CreateItem(Leg_Soul[i], GetUnitX(u), GetUnitY(u))
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff66cc" + Leg_Name[i] + " dropped its Soul!|r")
            else
                call CreateItem('I00B', GetUnitX(u), GetUnitY(u))
                call CreateItem('I001', GetUnitX(u), GetUnitY(u))
                call CreateItem('I000', GetUnitX(u), GetUnitY(u))
            endif
            return
        endif
        set i = i + 1
    endloop
endfunction

function Wild_Tick takes nothing returns nothing
    local integer c = 0
    set Wild_Time = Wild_Time + 2.0
    if Wild_Time >= Wild_NextCheck then
        set Wild_NextCheck = Wild_Time + Wild_LevelCheck
        call Wild_UpdateTier()
    endif
    if Wild_Time >= Leg_Next then
        set Leg_Next = Leg_Next + Leg_Interval
        if Leg_Alive < Leg_Max then
            call Leg_Spawn()
        endif
    endif
    call Wild_Scan()
    loop
        exitwhen c >= Wild_CampN
        if Wild_CampDue[c] > 0.0 and Wild_Time >= Wild_CampDue[c] then
            call Wild_SpawnCamp(c)
        endif
        set c = c + 1
    endloop
endfunction

function Wild_OnDeath takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer c = LoadInteger(Mega_HT, h, 25) - 1
    local integer soul = 0
    if c >= 0 then
        set Wild_CampAlive[c] = Wild_CampAlive[c] - 1
        if Wild_CampAlive[c] <= 0 then
            set Wild_CampDue[c] = Wild_Time + Wild_Respawn
        endif
    endif
    if Wild_IsWildType(GetUnitTypeId(u)) then
        // only the Soul of its own species, and only species that have a playable version
        set soul = LoadInteger(Mega_HT, GetUnitTypeId(u), 8)
        if soul != 0 and GetRandomReal(0.0, 100.0) < Wild_SoulChance then
            call CreateItem(soul, GetUnitX(u), GetUnitY(u))
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff66ccA wild " + GetUnitName(u) + " dropped its Soul!|r")
        endif
        call FlushChildHashtable(Mega_HT, h)
    endif
endfunction

// pre-placed wild creeps join the nearest camp
function Wild_RegisterCamps takes nothing returns nothing
    local unit u = null
    local integer i = 0
    local integer best = 0
    local real bd = 0.0
    local real d = 0.0
    loop
        exitwhen i >= Wild_TypeN
        call SaveBoolean(Mega_HT, Wild_Type[i], 7, true)
        set i = i + 1
    endloop
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        if Wild_IsWildType(GetUnitTypeId(u)) then
            set best = -1
            set bd = Wild_CampRadius * Wild_CampRadius
            set i = 0
            loop
                exitwhen i >= Wild_CampN
                set d = (GetUnitX(u) - Wild_CampX[i]) * (GetUnitX(u) - Wild_CampX[i]) + (GetUnitY(u) - Wild_CampY[i]) * (GetUnitY(u) - Wild_CampY[i])
                if d < bd then
                    set bd = d
                    set best = i
                endif
                set i = i + 1
            endloop
            if best >= 0 then
                call SaveInteger(Mega_HT, GetHandleId(u), 25, best + 1)
                set Wild_CampAlive[best] = Wild_CampAlive[best] + 1
            endif
        endif
    endloop
endfunction

// ---------------------------------------------------------------------------------------------
// Repick
// ---------------------------------------------------------------------------------------------
function Repick_Do takes player p returns nothing
    local integer pid = GetPlayerId(p)
    local unit h = null
    local unit u = null
    local item it = null
    local integer i = 0
    if Mega_Time >= Repick_Window then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Repick is only allowed in the first 2 minutes.|r")
        return
    endif
    if Repick_Count[pid] >= Repick_Max then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You have no repicks left.|r")
        return
    endif
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) then
            set h = u
        endif
    endloop
    if h == null or IsUnitType(h, UNIT_TYPE_DEAD) or LoadInteger(Mega_HT, GetHandleId(h), 0) > 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You need a living Pokemon (not in Mega form) to repick.|r")
        set h = null
        return
    endif
    set Repick_Count[pid] = Repick_Count[pid] + 1
    set Repick_XP[pid] = GetHeroXP(h)
    set Repick_Pending[pid] = true
    loop
        exitwhen i >= 6
        set it = UnitItemInSlot(h, i)
        if it != null then
            call UnitRemoveItem(h, it)
            call SetItemVisible(it, false)
        endif
        call SaveItemHandle(Mega_HT, 900 + pid, i, it)
        set i = i + 1
    endloop
    call RemoveUnit(h)
    set u = CreateUnit(p, 'earc', -128.0, 4544.0, 270.0)
    call SelectUnitForPlayerSingle(u, p)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r repicked (" + I2S(Repick_Count[pid]) + "/2)")
    set h = null
    set u = null
    set it = null
endfunction

// give the XP and items of the repicked Pokemon to the player's new one
function Repick_Restore takes unit u returns nothing
    local integer pid = GetPlayerId(GetOwningPlayer(u))
    local integer i = 0
    local item it = null
    if not Repick_Pending[pid] or not IsUnitType(u, UNIT_TYPE_HERO) then
        return
    endif
    set Repick_Pending[pid] = false
    call SetHeroXP(u, Repick_XP[pid], true)
    loop
        exitwhen i >= 6
        set it = LoadItemHandle(Mega_HT, 900 + pid, i)
        if it != null then
            call SetItemVisible(it, true)
            call UnitAddItem(u, it)
        endif
        set i = i + 1
    endloop
    call FlushChildHashtable(Mega_HT, 900 + pid)
    set it = null
endfunction

function Repick_OnChat takes nothing returns nothing
    call Repick_Do(GetTriggerPlayer())
endfunction

function Repick_OnSell takes nothing returns nothing
    call Repick_Restore(GetSoldUnit())
endfunction

// ---------------------------------------------------------------------------------------------
// Random starter Pokemon
// ---------------------------------------------------------------------------------------------
function Rand_FindWisp takes player p returns unit
    local unit u = null
    local unit w = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if GetUnitTypeId(u) == 'earc' then
            set w = u
        endif
    endloop
    return w
endfunction

function Rand_IsTaken takes integer t returns boolean
    local integer i = 0
    local boolean taken = false
    local unit u = null
    loop
        exitwhen i >= bj_MAX_PLAYERS or taken
        call GroupEnumUnitsOfPlayer(Rand_Tmp, Player(i), null)
        loop
            set u = FirstOfGroup(Rand_Tmp)
            exitwhen u == null
            call GroupRemoveUnit(Rand_Tmp, u)
            if GetUnitTypeId(u) == t then
                set taken = true
            endif
        endloop
        set i = i + 1
    endloop
    return taken
endfunction

function Rand_Give takes player p returns nothing
    local unit w = Rand_FindWisp(p)
    local unit h = null
    local integer t = 0
    local integer tries = 0
    if w == null or Rand_N == 0 then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You already have a Pokemon.|r")
        return
    endif
    loop
        set t = Rand_Type[GetRandomInt(0, Rand_N - 1)]
        set tries = tries + 1
        exitwhen tries >= 20 or not Rand_IsTaken(t)
    endloop
    set h = CreateUnit(p, t, GetUnitX(w), GetUnitY(w), 270.0)
    call Repick_Restore(h)
    call RemoveUnit(w)
    call SelectUnitForPlayerSingle(h, p)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r Has Choosen (random) |cffffcc00" + GetHeroProperName(h) + "|r")
    set w = null
    set h = null
endfunction

// the host is the lowest slot that is playing; host commands (-random, chicken) apply to everyone
function Host_Id takes nothing returns integer
    local integer i = 0
    loop
        exitwhen i >= 12 or GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING
        set i = i + 1
    endloop
    return i
endfunction


function Rand_Auto takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= 12
        if Rand_FindWisp(Player(i)) != null then
            call Rand_Give(Player(i))
        endif
        set i = i + 1
    endloop
endfunction

function Rand_OnChat takes nothing returns nothing
    if GetPlayerId(GetTriggerPlayer()) != Host_Id() then
        call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 5.0, "|cffffcc00Only the host can type -random.|r")
        return
    endif
    call Rand_Auto()
endfunction

function Rand_Hint takes nothing returns nothing
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 15.0, "|cffffcc00The host types -random and every player gets a random Pokemon. Players who have not chosen after 45 seconds get one automatically. Type -repick in the first 2 minutes to choose again (2 times, level and items are kept).|r")
endfunction

// ---------------------------------------------------------------------------------------------
// Evolution of the new Pokemon (same style as the map's own: effect, 1.5s, guarded replace)
// ---------------------------------------------------------------------------------------------
function Evo_OnLevel takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer id = GetUnitTypeId(u)
    local integer i = 0
    loop
        exitwhen i >= Evo_N
        if Evo_From[i] == id and GetHeroLevel(u) >= Evo_Level[i] then
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DarkRitual\\DarkRitualTarget.mdl", u, "chest"))
            call TriggerSleepAction(1.50)
            call Mega_SafeReplace(u, Evo_To[i], bj_UNIT_STATE_METHOD_RELATIVE)
            set u = null
            return
        endif
        set i = i + 1
    endloop
    set u = null
endfunction

function Evo_OnPickup takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer i = 0
    loop
        exitwhen i >= Evo_ItemN
        if GetUnitTypeId(u) == Evo_ItemFrom[i] and GetItemTypeId(GetManipulatedItem()) == Evo_Item[i] then
            call RemoveItem(GetManipulatedItem())
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DarkRitual\\DarkRitualTarget.mdl", u, "chest"))
            call TriggerSleepAction(1.50)
            call Mega_SafeReplace(u, Evo_ItemTo[i], bj_UNIT_STATE_METHOD_RELATIVE)
            set u = null
            return
        endif
        set i = i + 1
    endloop
    set u = null
endfunction

// ---------------------------------------------------------------------------------------------
// Own-species Souls: holding one in slot 1 and entering the centre circle turns the Pokemon into it
// ---------------------------------------------------------------------------------------------
function Soul_OnEnter takes nothing returns nothing
    local unit u = GetEnteringUnit()
    local item it = UnitItemInSlot(u, 0)
    local integer i = 0
    loop
        exitwhen i >= Soul_N or it == null
        if GetItemTypeId(it) == Soul_Item[i] then
            call RemoveItem(it)
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DarkRitual\\DarkRitualTarget.mdl", u, "chest"))
            call TriggerSleepAction(1.50)
            call Mega_SafeReplace(u, Soul_Hero[i], bj_UNIT_STATE_METHOD_RELATIVE)
            set u = null
            set it = null
            return
        endif
        set i = i + 1
    endloop
    set u = null
    set it = null
endfunction

// ---------------------------------------------------------------------------------------------
// "t la ga": once per player, +10 levels for their Pokemon and +3000 gold
// ---------------------------------------------------------------------------------------------
function Chicken_Do takes player p returns nothing
    local integer pid = GetPlayerId(p)
    local unit h = null
    local unit u = null
    local integer lv = 0
    if Chicken_Used[pid] then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You already used it.|r")
        return
    endif
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            set h = u
        endif
    endloop
    if h == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Pick a living Pokemon first.|r")
        return
    endif
    set Chicken_Used[pid] = true
    set lv = GetHeroLevel(h) + Chicken_Levels
    if lv > 100 then
        set lv = 100
    endif
    call SetHeroLevel(h, lv, true)
    call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) + Chicken_Gold)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r is a chicken: +" + I2S(Chicken_Levels) + " levels, +" + I2S(Chicken_Gold) + " gold.")
    set h = null
endfunction

// only the host can type it; it applies to every player (each player still only once)
function Chicken_OnChat takes nothing returns nothing
    local integer i = 0
    if GetPlayerId(GetTriggerPlayer()) != Host_Id() then
        call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 5.0, "|cffffcc00Only the host can type chicken.|r")
        return
    endif
    loop
        exitwhen i >= 12
        call Chicken_Do(Player(i))
        set i = i + 1
    endloop
endfunction

function Mega_CheckRemoved takes nothing returns nothing
    if GetUnitTypeId(GetEnumUnit()) == 0 then
        call Mega_End(GetEnumUnit())
    endif
endfunction

function Mega_Tick takes nothing returns nothing
    local integer pi = 0
    local integer h = 0
    local unit u = null
    set Mega_Time = Mega_Time + 0.25
    loop
        exitwhen pi >= bj_MAX_PLAYERS
        call GroupEnumUnitsOfPlayer(Mega_Tmp, Player(pi), null)
        loop
            set u = FirstOfGroup(Mega_Tmp)
            exitwhen u == null
            call GroupRemoveUnit(Mega_Tmp, u)
            if IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitType(u, UNIT_TYPE_DEAD) then
                set h = GetHandleId(u)
                if LoadInteger(Mega_HT, h, 0) > 0 then
                    if Mega_Time >= LoadReal(Mega_HT, h, 1) then
                        call Mega_End(u)
                    elseif LoadUnitHandle(Mega_HT, h, 4) != null then
                        call Mega_KidFollow(u, LoadUnitHandle(Mega_HT, h, 4))
                    endif
                else
                    call Mega_SyncAbility(u)
                endif
            endif
        endloop
        set pi = pi + 1
    endloop
    // heroes removed from the game while in Mega form (e.g. ReplaceUnitBJ)
    call ForGroup(Mega_Group, function Mega_CheckRemoved)
endfunction

function Mega_OnCast takes nothing returns boolean
    local integer a = GetSpellAbilityId()
    local integer i = 0
    loop
        exitwhen i >= Mega_N
        if a == Mega_Evolve[i] then
            call Mega_Start(GetTriggerUnit(), i)
            return false
        endif
        set i = i + 1
    endloop
    return false
endfunction

function Mega_OnDeath takes nothing returns boolean
    if LoadInteger(Mega_HT, GetHandleId(GetTriggerUnit()), 0) > 0 then
        call Mega_End(GetTriggerUnit())
    endif
    if GetOwningPlayer(GetTriggerUnit()) == Player(PLAYER_NEUTRAL_AGGRESSIVE) then
        call Wild_OnDeath(GetTriggerUnit())
        call Leg_OnDeath(GetTriggerUnit())
    endif
    return false
endfunction

// Mega Kangaskhan: the Kid hits too (Parental Bond), at most once per 0.5s
function Mega_OnAttacked takes nothing returns boolean
    local unit u = GetAttacker()
    local integer h = GetHandleId(u)
    local unit kid = null
    local real dmg = 0.0
    if LoadInteger(Mega_HT, h, 0) == Mega_KangIdx + 1 then
        set kid = LoadUnitHandle(Mega_HT, h, 4)
        if kid != null and Mega_Time - LoadReal(Mega_HT, h, 5) >= 0.5 then
            call SaveReal(Mega_HT, h, 5, Mega_Time)
            call SetUnitAnimation(kid, "attack")
            call QueueUnitAnimation(kid, "stand")
            set dmg = 0.25 * (I2R(BlzGetUnitBaseDamage(u, 0)) + I2R(GetHeroStr(u, true)))
            call UnitDamageTarget(u, GetTriggerUnit(), dmg, true, false, ConvertAttackType(BlzGetUnitWeaponIntegerField(u, UNIT_WEAPON_IF_ATTACK_ATTACK_TYPE, 0)), DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)
        endif
    endif
    set u = null
    set kid = null
    return false
endfunction

function Mega_Quests takes nothing returns nothing
    local string s = ""
    local integer i = 0
    call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Evolution", "Mua Mega Stone o |cffff66ccMega Shop I|r / |cffff66ccMega Shop II|r (canh Poke Mart).|nPokemon dang cuoi cam dung da se co nut |cffff66ccMega Evolve|r (phim D, dang Y: phim F).|nMega trong 60 giay: doi model, +30 chi so, +5 giap, +40 toc chay, +25% toc danh. Hoi chieu 150 giay.|nChet khi dang Mega se tro ve dang thuong.|nMega Kangaskhan: con nho di theo, danh them 25% sat thuong.|n|nCredit model Mega: PKLegends team va cac tac gia tren Hive Workshop.", "ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp")
    loop
        exitwhen i >= Mega_N
        set s = s + Mega_StoneName[i] + " (" + I2S(Mega_Price[i]) + ") - " + Mega_Name[i] + "|n"
        set i = i + 1
    endloop
    call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Stones", s, "ReplaceableTextures\\CommandButtons\\BTNMegaGengar.blp")
    if Leg_N > 0 then
        call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Random Legends", "Cu 5 phut co 1 legend Lv 100 xuat hien ngau nhien tren map (toi da 2 con).|nChi Pokemon lv 100 moi gay sat thuong duoc.|nGiet duoc: 50% roi Soul cua legend do (cam o o 1, vao vong tron giua map de bien thanh legend).|nQuai hoang da: 0.5% roi 1 Soul ngau nhien.", "ReplaceableTextures\\CommandButtons\\BTNSoulGem.blp")
    endif
endfunction

// ---------------------------------------------------------------------------------------------
// Pokemon Abilities (v2.8). Per-unit keys in Ab_HT, parent key = handle id:
//   0 applied Ability number (0 = none), 1 last hit taken time, 2 rising stacks, 3 rising expiry,
//   4 sturdy cooldown end, 5/6 weaken until/fraction (Intimidate), 7/8 boost until/fraction (Flash Fire),
//   9 born time (Slow Start), 10 synced flag, 11 base move speed while slowed.
// Ability number of a unit type: SaveInteger(Ab_HT, type, 0, number). Megas: Ab_MegaAb[mega index].
// Effect e of Ability a is e = a*2 + k. Damage is handled in Ab_OnDamaging (one trigger, Ab_Busy guards the
// damage an Ability itself deals).
// ---------------------------------------------------------------------------------------------
function Ab_Num takes unit u returns integer
    return LoadInteger(Ab_HT, GetHandleId(u), 0)
endfunction

// alive check by life: the UnitAlive native is not in every WC3 version and an undeclared function stops the map
function Ab_Alive takes unit u returns boolean
    return GetWidgetLife(u) > 0.405
endfunction

function Ab_Dig takes integer d returns integer
    if d < 10 then
        return 48 + d
    endif
    return 55 + d
endfunction

// passive info button of Ability a: 'AB00' + base-36 digits of a-1 (same as ability_data.info_id)
function Ab_InfoId takes integer a returns integer
    local integer i = a - 1
    local integer hi = i / 36
    local integer lo = i - hi * 36
    return 'AB00' - 12336 + Ab_Dig(hi) * 256 + Ab_Dig(lo)
endfunction

// Ability that a unit should have now: a Mega form's Ability, else its type's Ability
function Ab_Want takes unit u returns integer
    local integer mi = LoadInteger(Mega_HT, GetHandleId(u), 0) - 1
    if mi >= 0 then
        return Ab_MegaAb[mi]
    endif
    return LoadInteger(Ab_HT, GetUnitTypeId(u), 0)
endfunction

// a unit we see for the first time may carry Abilities of the unit it replaced (evolution): remove them all
function Ab_Strip takes unit u returns nothing
    local integer a = 1
    loop
        exitwhen a > Ab_N
        call UnitRemoveAbility(u, Ab_InfoId(a))
        set a = a + 1
    endloop
    call UnitRemoveAbility(u, 'AXA4')
    call UnitRemoveAbility(u, 'AXA6')
    call UnitRemoveAbility(u, 'AXS4')
    call UnitRemoveAbility(u, 'AXS7')
endfunction

// give the hero the info button and the bonus abilities of its Ability; swap them when the Ability changes
function Ab_Sync takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer want = Ab_Want(u)
    local integer have = LoadInteger(Ab_HT, h, 0)
    local integer k = 0
    local integer e = 0
    if not HaveSavedInteger(Ab_HT, h, 10) then
        call SaveInteger(Ab_HT, h, 10, 1)
        call SaveReal(Ab_HT, h, 9, Mega_Time)
        call Ab_Strip(u)
        set have = 0
    endif
    if want != have then
        if have > 0 then
            call UnitRemoveAbility(u, Ab_InfoId(have))
            loop
                exitwhen k > 1
                set e = have * 2 + k
                if Ab_Raw[e] != 0 then
                    call UnitRemoveAbility(u, Ab_Raw[e])
                endif
                set k = k + 1
            endloop
        endif
        set k = 0
        if want > 0 then
            call UnitAddAbility(u, Ab_InfoId(want))
            loop
                exitwhen k > 1
                set e = want * 2 + k
                if Ab_Raw[e] != 0 then
                    call UnitAddAbility(u, Ab_Raw[e])
                endif
                set k = k + 1
            endloop
        endif
        call SaveInteger(Ab_HT, h, 0, want)
    endif
endfunction

// ---- timed effects: kind 1 damage over time (amt HP per second), 2 slow (amt = fraction), 3 stun
function Ab_FxFind takes unit u, integer kind returns integer
    local integer i = 0
    loop
        exitwhen i >= Ab_FxMax
        if Ab_FxU[i] == u and Ab_FxKind[i] == kind then
            return i
        endif
        set i = i + 1
    endloop
    return -1
endfunction

function Ab_FxFree takes nothing returns integer
    local integer i = 0
    loop
        exitwhen i >= Ab_FxMax
        if Ab_FxU[i] == null then
            return i
        endif
        set i = i + 1
    endloop
    return -1
endfunction

// add an effect, or refresh the same kind on the same unit
function Ab_FxAdd takes unit u, integer kind, real dur, real amt returns nothing
    local integer h = GetHandleId(u)
    local integer i = Ab_FxFind(u, kind)
    if i < 0 then
        set i = Ab_FxFree()
        if i < 0 then
            return
        endif
        set Ab_FxU[i] = u
        set Ab_FxKind[i] = kind
    endif
    set Ab_FxEnd[i] = Mega_Time + dur
    set Ab_FxAmt[i] = amt
    if kind == 2 then
        if LoadReal(Ab_HT, h, 11) <= 0.0 then
            call SaveReal(Ab_HT, h, 11, GetUnitMoveSpeed(u))
        endif
        call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11) * (1.0 - amt))
    elseif kind == 3 then
        call PauseUnit(u, true)
    endif
endfunction

// end slot i: restore the speed or the movement when no other effect of that kind is left on the unit
function Ab_FxStop takes integer i returns nothing
    local unit u = Ab_FxU[i]
    local integer kind = Ab_FxKind[i]
    local integer h = GetHandleId(u)
    set Ab_FxU[i] = null
    if kind == 2 and Ab_FxFind(u, 2) < 0 then
        if LoadReal(Ab_HT, h, 11) > 0.0 then
            call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11))
        endif
        call SaveReal(Ab_HT, h, 11, 0.0)
    elseif kind == 3 and Ab_FxFind(u, 3) < 0 then
        call PauseUnit(u, false)
    endif
    set u = null
endfunction

// runs every 0.5s
function Ab_FxRun takes nothing returns nothing
    local integer i = 0
    local unit u = null
    loop
        exitwhen i >= Ab_FxMax
        set u = Ab_FxU[i]
        if u != null then
            if not Ab_Alive(u) or Mega_Time >= Ab_FxEnd[i] then
                call Ab_FxStop(i)
            elseif Ab_FxKind[i] == 1 then
                call SetWidgetLife(u, GetWidgetLife(u) - Ab_FxAmt[i] * 0.5)
            endif
        endif
        set i = i + 1
    endloop
    set u = null
endfunction

function Ab_HasWord takes string s, string w returns boolean
    local integer n = StringLength(s) - StringLength(w)
    local integer i = 0
    loop
        exitwhen i > n
        if SubString(s, i, i + StringLength(w)) == w then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// main attribute (strength, agility or intelligence, whichever is highest)
function Ab_MainStat takes unit u returns real
    local real s = I2R(GetHeroStr(u, true))
    local real a = I2R(GetHeroAgi(u, true))
    local real i = I2R(GetHeroInt(u, true))
    if a > s then
        set s = a
    endif
    if i > s then
        set s = i
    endif
    return s
endfunction

// best main attribute among the heroes of a player (for dummy units that deal a skill's damage)
function Ab_PlayerStat takes player p returns real
    local real best = 0.0
    local real s = 0.0
    local unit u = null
    call GroupEnumUnitsOfPlayer(Ab_Tmp, p, null)
    loop
        set u = FirstOfGroup(Ab_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Ab_Tmp, u)
        if IsUnitType(u, UNIT_TYPE_HERO) then
            set s = Ab_MainStat(u)
            if s > best then
                set best = s
            endif
        endif
    endloop
    set u = null
    return best
endfunction

// damage multiplier of a skill: 1 + 0.011 * (stat - 50), 1.0 up to 50, at most 10
function Ab_SkillMult takes real stat returns real
    local real m = 1.0 + Ab_ScaleK * (stat - Ab_ScaleBase)
    if stat <= Ab_ScaleBase then
        set m = 1.0
    endif
    if m > Ab_ScaleMax then
        set m = Ab_ScaleMax
    endif
    return m
endfunction

// Flash Fire boost and Intimidate weaken of the attacker
function Ab_StateMult takes unit u returns real
    local integer h = GetHandleId(u)
    local real m = 1.0
    if Mega_Time < LoadReal(Ab_HT, h, 7) then
        set m = m * (1.0 + LoadReal(Ab_HT, h, 8))
    endif
    if Mega_Time < LoadReal(Ab_HT, h, 5) then
        set m = m * (1.0 - LoadReal(Ab_HT, h, 6))
    endif
    return m
endfunction

// damage dealt by the attacker, from its own Ability
function Ab_OutMult takes unit src, integer a, boolean atk returns real
    local integer h = GetHandleId(src)
    local integer k = 0
    local integer e = 0
    local integer fam = 0
    local real m = 1.0
    loop
        exitwhen k > 1
        set e = a * 2 + k
        set fam = Ab_Fam[e]
        if fam == Ab_F_PINCH then
            if GetWidgetLife(src) < Ab_X[e] * BlzGetUnitMaxHP(src) then
                set m = m * (1.0 + Ab_Y[e])
            endif
        elseif fam == Ab_F_POWER or fam == Ab_F_MULTITYPE then
            set m = m * (1.0 + Ab_X[e])
        elseif fam == Ab_F_RISING then
            if Mega_Time < LoadReal(Ab_HT, h, 3) then
                set m = m * (1.0 + Ab_X[e] * I2R(LoadInteger(Ab_HT, h, 2)))
            endif
        elseif fam == Ab_F_LUCKY then
            if atk and GetRandomReal(0.0, 1.0) < Ab_X[e] then
                set m = m * 2.0
            endif
        elseif fam == Ab_F_SLOWSTART then
            if Mega_Time - LoadReal(Ab_HT, h, 9) < Ab_Y[e] then
                set m = m * (1.0 - Ab_X[e])
            else
                set m = m * (1.0 + Ab_Z[e])
            endif
        endif
        set k = k + 1
    endloop
    return m
endfunction

// Intimidate: enemies around the holder deal less damage for a while
function Ab_Intimidate takes unit t, integer e returns nothing
    local unit v = null
    local player p = GetOwningPlayer(t)
    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(t), GetUnitY(t), Ab_X[e], null)
    loop
        set v = FirstOfGroup(Ab_Group)
        exitwhen v == null
        call GroupRemoveUnit(Ab_Group, v)
        if Ab_Alive(v) and IsUnitEnemy(v, p) then
            call SaveReal(Ab_HT, GetHandleId(v), 5, Mega_Time + Ab_Z[e])
            call SaveReal(Ab_HT, GetHandleId(v), 6, Ab_Y[e])
        endif
    endloop
    set v = null
    set p = null
endfunction

// damage taken by the holder t (multiplier of d); also updates the holder's rising stacks and sturdy
function Ab_InMult takes unit src, unit t, integer a, boolean atk, real d returns real
    local integer h = GetHandleId(t)
    local integer k = 0
    local integer e = 0
    local integer fam = 0
    local integer stacks = 0
    local real mx = BlzGetUnitMaxHP(t)
    local real hp = GetWidgetLife(t)
    local real m = 1.0
    local real nd = 0.0
    loop
        exitwhen k > 1
        set e = a * 2 + k
        set fam = Ab_Fam[e]
        if fam == Ab_F_MULTISCALE then
            if hp >= mx - 1.0 then
                set m = m * (1.0 - Ab_X[e])
            endif
        elseif fam == Ab_F_MULTITYPE then
            set m = m * (1.0 - Ab_Y[e])
        elseif fam == Ab_F_DODGE then
            if atk and GetRandomReal(0.0, 1.0) < Ab_X[e] then
                set m = 0.0
            endif
        elseif fam == Ab_F_STURDY then
            if d > 0.0 and d * m >= hp and Mega_Time >= LoadReal(Ab_HT, h, 4) then
                set nd = hp - Ab_X[e] * mx
                if nd < 0.0 then
                    set nd = 0.0
                endif
                set m = nd / d
                call SaveReal(Ab_HT, h, 4, Mega_Time + Ab_Z[e])
            endif
        elseif fam == Ab_F_PRESSURE then
            set nd = GetUnitState(src, UNIT_STATE_MANA) - Ab_X[e]
            if nd < 0.0 then
                set nd = 0.0
            endif
            call SetUnitState(src, UNIT_STATE_MANA, nd)
        elseif fam == Ab_F_REFLECT then
            if d * m * Ab_X[e] > 0.0 then
                set Ab_Busy = true
                call UnitDamageTarget(t, src, d * m * Ab_X[e], false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_UNIVERSAL, WEAPON_TYPE_WHOKNOWS)
                set Ab_Busy = false
            endif
        elseif fam == Ab_F_RISING then
            set stacks = LoadInteger(Ab_HT, h, 2)
            if Mega_Time < LoadReal(Ab_HT, h, 3) then
                set stacks = stacks + 1
                if stacks > R2I(Ab_Y[e]) then
                    set stacks = R2I(Ab_Y[e])
                endif
            else
                set stacks = 1
            endif
            call SaveInteger(Ab_HT, h, 2, stacks)
            call SaveReal(Ab_HT, h, 3, Mega_Time + Ab_Z[e])
        elseif fam == Ab_F_INTIMIDATE then
            if Mega_Time - LoadReal(Ab_HT, h, 1) > 10.0 then
                call Ab_Intimidate(t, e)
            endif
        endif
        set k = k + 1
    endloop
    return m
endfunction

// ABSORB: the holder takes no damage from attackers of its type word; may heal and boost
function Ab_Absorbs takes unit t, unit src, integer a, real d returns boolean
    local integer h = GetHandleId(t)
    local integer k = 0
    local integer e = 0
    local boolean got = false
    local real hp = 0.0
    loop
        exitwhen k > 1
        set e = a * 2 + k
        if Ab_Fam[e] == Ab_F_ABSORB and Ab_HasWord(GetUnitName(src), Ab_S[e]) then
            set got = true
            if Ab_X[e] > 0.0 then
                set hp = GetWidgetLife(t) + Ab_X[e] * d
                if hp > BlzGetUnitMaxHP(t) then
                    set hp = BlzGetUnitMaxHP(t)
                endif
                call SetWidgetLife(t, hp)
            endif
            if Ab_Y[e] > 0.0 then
                call SaveReal(Ab_HT, h, 7, Mega_Time + Ab_Z[e])
                call SaveReal(Ab_HT, h, 8, Ab_Y[e])
            endif
        endif
        set k = k + 1
    endloop
    return got
endfunction

// one contact effect: applied to the attacker that hit the holder
function Ab_Hit takes unit src, integer e returns nothing
    local integer kind = R2I(Ab_Y[e])
    if kind == 1 then
        call Ab_FxAdd(src, 3, Ab_Z[e], 0.0)
    elseif kind == 4 then
        call Ab_FxAdd(src, 2, Ab_Z[e], Ab_W[e])
    else
        call Ab_FxAdd(src, 1, Ab_Z[e], Ab_W[e] * BlzGetUnitMaxHP(src) / Ab_Z[e])
    endif
endfunction

function Ab_InContact takes unit src, integer a returns nothing
    local integer k = 0
    local integer e = 0
    loop
        exitwhen k > 1
        set e = a * 2 + k
        if Ab_Fam[e] == Ab_F_CONTACT and GetRandomReal(0.0, 1.0) < Ab_X[e] then
            call Ab_Hit(src, e)
        endif
        set k = k + 1
    endloop
endfunction

// ---- every second, for each hero of the users
function Ab_Recover takes unit u, integer e returns nothing
    local real mx = BlzGetUnitMaxHP(u)
    local real hp = GetWidgetLife(u) + Ab_X[e] * mx
    if Mega_Time - LoadReal(Ab_HT, GetHandleId(u), 1) >= Ab_Y[e] then
        if hp > mx then
            set hp = mx
        endif
        call SetWidgetLife(u, hp)
    endif
endfunction

// AURA: kind 1 slows enemies in range, kind 2 takes w * max HP from them each second
function Ab_Aura takes unit u, integer e returns nothing
    local unit v = null
    local player p = GetOwningPlayer(u)
    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(u), GetUnitY(u), Ab_X[e], null)
    loop
        set v = FirstOfGroup(Ab_Group)
        exitwhen v == null
        call GroupRemoveUnit(Ab_Group, v)
        if v != u and Ab_Alive(v) and IsUnitEnemy(v, p) then
            if R2I(Ab_Y[e]) == 1 then
                call Ab_FxAdd(v, 2, 1.5, Ab_W[e])
            else
                call SetWidgetLife(v, GetWidgetLife(v) - Ab_W[e] * BlzGetUnitMaxHP(v))
            endif
        endif
    endloop
    set v = null
    set p = null
endfunction

function Ab_BeatFx takes unit u, integer e returns nothing
    if Ab_Fam[e] == Ab_F_RECOVERY then
        call Ab_Recover(u, e)
    elseif Ab_Fam[e] == Ab_F_AURA then
        call Ab_Aura(u, e)
    endif
endfunction

function Ab_Hero takes unit u returns nothing
    local integer a = 0
    local integer k = 0
    call Ab_Sync(u)
    set a = Ab_Num(u)
    if a > 0 then
        loop
            exitwhen k > 1
            call Ab_BeatFx(u, a * 2 + k)
            set k = k + 1
        endloop
    endif
endfunction

// 0.5s clock: timed effects every tick, heroes every second (every 2nd tick)
function Ab_Tick takes nothing returns nothing
    local integer pi = 0
    local unit u = null
    set Ab_Beat = Ab_Beat + 1
    call Ab_FxRun()
    if Ab_Beat - (Ab_Beat / 2) * 2 == 0 then
        loop
            exitwhen pi >= 12
            call GroupEnumUnitsOfPlayer(Ab_Tmp, Player(pi), null)
            loop
                set u = FirstOfGroup(Ab_Tmp)
                exitwhen u == null
                call GroupRemoveUnit(Ab_Tmp, u)
                if IsUnitType(u, UNIT_TYPE_HERO) and Ab_Alive(u) then
                    call Ab_Hero(u)
                endif
            endloop
            set pi = pi + 1
        endloop
    endif
    set u = null
endfunction

function Ab_OnRevive takes nothing returns nothing
    call SaveReal(Ab_HT, GetHandleId(GetTriggerUnit()), 9, Mega_Time)
endfunction

// condition of the one damage trigger: Leg_OnDamage first, then the Abilities
function Ab_OnDamaging takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local unit src = null
    local player sp = null
    local real dmg = 0.0
    local real m = 1.0
    local real stat = 0.0
    local boolean atk = false
    local boolean user = false
    local integer ta = 0
    local integer s_ab = 0
    call Leg_OnDamage()
    set src = GetEventDamageSource()
    if Ab_Busy or src == null or src == t then
        return false
    endif
    set dmg = GetEventDamage()
    if dmg <= 0.0 then
        return false
    endif
    set sp = GetOwningPlayer(src)
    if not IsUnitEnemy(t, sp) then
        return false
    endif
    set atk = BlzGetEventIsAttack()
    set user = GetPlayerId(sp) < 12
    set ta = Ab_Num(t)
    set s_ab = Ab_Num(src)
    // skill damage: scaled by the main attribute of the hero (or of the owner's best hero for dummy units)
    if user and BlzGetEventDamageType() != DAMAGE_TYPE_NORMAL then
        if IsUnitType(src, UNIT_TYPE_HERO) then
            set stat = Ab_MainStat(src)
        else
            set stat = Ab_PlayerStat(sp)
        endif
        set m = m * Ab_SkillMult(stat)
    endif
    set m = m * Ab_StateMult(src)
    if s_ab > 0 then
        set m = m * Ab_OutMult(src, s_ab, atk)
    endif
    if ta > 0 then
        if Ab_Absorbs(t, src, ta, dmg * m) then
            call BlzSetEventDamage(0.0)
            return false
        endif
        set m = m * Ab_InMult(src, t, ta, atk, dmg * m)
        call SaveReal(Ab_HT, GetHandleId(t), 1, Mega_Time)
        if atk and m > 0.0 and Ab_Alive(src) then
            call Ab_InContact(src, ta)
        endif
    endif
    call BlzSetEventDamage(dmg * m)
    set t = null
    set src = null
    set sp = null
    return false
endfunction

function Mega_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0
    call Mega_InitData()
    call Rand_InitData()
    call Evo_InitData()
    call Leg_InitData()
    call Ab_InitData()
    call Wild_InitData()
    call Wild_RegisterCamps()
    call TimerStart(Wild_Timer, 2.0, true, function Wild_Tick)
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Mega_OnCast))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(t, Condition(function Mega_OnDeath))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_ATTACKED)
    call TriggerAddCondition(t, Condition(function Mega_OnAttacked))
    call TimerStart(Mega_Timer, 0.25, true, function Mega_Tick)
    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', -4416.0, 640.0, 0.0)
    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', -4416.0, -640.0, 0.0)
    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 4416.0, -640.0, 180.0)
    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 4416.0, 640.0, 180.0)
    call Mega_Quests()
    set t = CreateTrigger()
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-random", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Rand_OnChat)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-repick", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Repick_OnChat)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(t, function Repick_OnSell)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGING)
    call TriggerAddCondition(t, Condition(function Ab_OnDamaging))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_REVIVE_FINISH)
    call TriggerAddAction(t, function Ab_OnRevive)
    call TimerStart(Ab_Timer, 0.5, true, function Ab_Tick)
    set t = CreateTrigger()
    call TriggerRegisterEnterRectSimple(t, Hi)
    call TriggerAddAction(t, function Soul_OnEnter)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "t là gà", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "tôi là gà", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "t la ga", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "toi la ga", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "chicken", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-chicken", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Chicken_OnChat)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_LEVEL)
    call TriggerAddAction(t, function Evo_OnLevel)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_PICKUP_ITEM)
    call TriggerAddAction(t, function Evo_OnPickup)
    call TimerStart(Rand_Timer, Rand_AutoSeconds, false, function Rand_Auto)
    call TimerStart(CreateTimer(), 3.0, false, function Rand_Hint)
    set t = null
endfunction
