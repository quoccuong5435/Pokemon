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
real Wild_TierStep = 0.08
integer Wild_TierArmor = 1
real Wild_EliteHP = 2.0
real Wild_EliteDmg = 1.4
real Wild_DmgMult = 1.0
real Wild_EliteArmor = 3.0
real Wild_EliteGold = 3.0
real Wild_GoldMult = 2.0
real Wild_EliteScale = 1.15
real Wild_Respawn = 15.0
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
integer array Leg_Up   // v3.3: 1 while that legend is alive (no duplicates)
integer Leg_Max = 99  // v3.2: no practical limit
real Leg_Interval = 300.0
real Leg_Next = 300.0
integer Leg_SoulChance = 100
integer Leg_MinLevel = 100
real array Leg_Warned
group Leg_Tmp = CreateGroup()
real Wild_SoulChance = 10.0  // v3.2: only elite creeps drop a Soul, 10%
real Wild_StoneChance = 5.0  // v3.2: elite creeps drop a random Mega Stone, 5%
integer array Wild_KitSkill
// own-species Souls added in v2.6 (transform in the circle at the map centre, rect Hi of the map script)
integer Soul_N = 0
integer array Soul_Item
integer array Soul_Hero
// "t la ga" / "chicken": once per player, +10 levels and +10000 gold
integer Chicken_Levels = 10
integer Chicken_Gold = 10000
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
constant real Ab_ScaleK = 0.02
constant real Ab_LevelK = 0.01  // extra skill damage per hero level above 50
// basic attacks of user Pokemon: x1.5 (v3.2 request: playable basic attacks were too weak)
constant real Ab_BasicMult = 1.5
constant real Ab_ScaleBase = 50.0
constant real Ab_ScaleMax = 5.0
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
timer Hero_Timer = CreateTimer()
// learned moves (Mv_InitData): label such as "Flare Blitz (Fire, power 120)", score = power x accuracy
integer Mv_N = 0
string array Mv_Label
integer array Mv_Score
string array Mv_Text                    // move description with @1 / @2 where a damage number goes
integer array Mv_D1
integer array Mv_D2
constant integer Mv_Slots = 4
// Pokemon picker at the tavern (v3.3): menu of the new Pokemon, 9 per page. Data: Pick_InitData
integer Pick_N = 0
integer array Pick_Type
string array Pick_Name
dialog array Pick_Dlg
integer array Pick_Page
button array Pick_Btn
integer array Pick_Val
integer array Pick_Grp
integer Pick_TN = 0
string array Pick_TName
integer array Pick_TFirst
integer array Pick_TCount
// NPC for learned moves (v3.2): "-moves" near the NPC. Learning costs gold, forgetting leaves the slot empty.
constant real Npc_X = 2356.0
constant real Npc_Y = -43.0
constant real Hero_StrHP = 25.0   // HP per Strength point (v3.3 playable HP x2)
constant real Hero_HPExtra = 1.0  // extra HP = Strength * 25 * this
constant real Npc_Range = 800.0
constant integer Npc_LearnCost = 500
constant integer Npc_TMCost = 3000      // TM/HM moves (v3.3)
integer Dmg_Tags = 0                    // v3.3: floating damage numbers created in the current second (cap Dmg_TagMax)
constant integer Dmg_TagMax = 40
integer Wild_UpTier = 0                 // v3.3: tier the creeps were last upgraded to
integer array Wild_UpT                  // new species chosen per camp during an upgrade
// Gym teams (v3.3): 8 gyms, arrays indexed 0..7
constant real Gym_Start = 900.0         // a hero this close to the gym leader spot starts the challenge
constant real Gym_Leave = 2200.0        // farther than this = the challenge is abandoned (starts over)
real array Gym_X
real array Gym_Y
integer array Gym_Item
integer array Gym_Pid                   // challenger player id (-1 = nobody)
integer array Gym_Stage                 // 0..5 = index of the Pokemon being fought
integer array Gym_Base                  // level of the challenger when the challenge started
real array Gym_Cool
unit array Gym_Hero
unit array Gym_Cur
integer array Gym_Chain
integer array Gym_Used                  // g * 6 + k: wild type of the k-th Pokemon of the current challenge
// badges and level cap (v3.4): a cleared gym gives a badge; XP stops at the level cap of the badges
boolean array Badge_Has                 // pid * 8 + gym index
// duel (v3.4): -duel <player>, -accept, -decline, -rank
integer array Duel_Foe                  // opponent player id while dueling (-1 = none)
integer array Duel_Ask                  // player id that challenged this player (-1 = none)
unit array Duel_U
real array Duel_RX
real array Duel_RY
real array Duel_T
boolean array Duel_Allied               // a * 12 + b: they were allies before the duel
integer array Duel_Wins
integer array Duel_Losses
timer Duel_Timer = CreateTimer()
// type items can only be bought by Pokemon of that type (v3.3)
integer Type_N = 0
integer array Type_Item
string array Type_Word
integer array Type_Cost
unit Npc_Man = null                     // the moves NPC (click it to open the dialog)
integer array Npc_Mode                  // 0 = normal view, 1 = TM/HM list
integer array Npc_TMPage
dialog array Npc_Dlg
button array Npc_Btn
integer array Npc_Kind
integer array Npc_Val
integer array Npc_Slot
unit array Npc_Unit
//MEGA_GLOBALS_END
//MEGA_PRELUDE_BEGIN
// Replaces every ReplaceUnitBJ of the original map (inserted right after endglobals so all triggers can use it).
// An evolution trigger runs once per level gained and waits 1.5s; several level-ups inside that wait used to
// replace the same unit several times, leaving duplicate Pokemon. Only the first replacement of a unit counts.
// v3.3: forms reached through a Soul (the 14 legend heroes of the map and every form a Soul of ours gives) start with
// no learned moves, so they learn the moves of their own species instead of keeping the old Pokemon's
function Mega_ResetsMoves takes integer id returns boolean
    local integer i = 0
    if id == 'E020' or id == 'E021' or id == 'E022' or id == 'E023' or id == 'E024' or id == 'E025' or id == 'E026' then
        return true
    endif
    if id == 'E027' or id == 'E028' or id == 'E029' or id == 'E02A' or id == 'E03J' or id == 'E04C' or id == 'E04D' then
        return true
    endif
    loop
        exitwhen i >= Soul_N
        if Soul_Hero[i] == id then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

function Mega_SafeReplace takes unit u, integer newId, integer method returns nothing
    local integer h = GetHandleId(u)
    local integer i = 0
    local integer xp = 0
    local unit nu = null
    if u == null or GetUnitTypeId(u) == 0 or GetUnitTypeId(u) == newId then
        return
    endif
    if HaveSavedReal(Mega_HT, h, 9) and Mega_Time - LoadReal(Mega_HT, h, 9) < 10.0 then
        return
    endif
    call SaveReal(Mega_HT, h, 9, Mega_Time)
    if IsUnitType(u, UNIT_TYPE_HERO) then
        set xp = GetHeroXP(u)
    endif
    call ReplaceUnitBJ(u, newId, method)
    // learned moves (slots 40..43, "already considered" flags 200 + move) stay with the Pokemon
    set nu = bj_lastReplacedUnit
    if nu != null then
        // experience (and so the level) stays with the Pokemon when it is replaced or evolves
        if IsUnitType(nu, UNIT_TYPE_HERO) and xp > 0 then
            call SetHeroXP(nu, xp, false)
        endif
        if not Mega_ResetsMoves(newId) then
            set i = 40
            loop
                exitwhen i > 43
                call SaveInteger(Ab_HT, GetHandleId(nu), i, LoadInteger(Ab_HT, h, i))
                set i = i + 1
            endloop
            set i = 0
            loop
                exitwhen i >= Mv_N
                call SaveInteger(Ab_HT, GetHandleId(nu), 200 + i, LoadInteger(Ab_HT, h, 200 + i))
                set i = i + 1
            endloop
        endif
    endif
    set nu = null
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

// v3.3: a hero whose level allows its next evolution evolves (also after a Soul or a level reached by other means)
function Evo_Check takes unit u returns nothing
    local integer id = GetUnitTypeId(u)
    local integer i = 0
    if LoadInteger(Mega_HT, GetHandleId(u), 0) > 0 then
        return
    endif
    if GetHeroLevel(u) <= LoadInteger(Mega_HT, GetHandleId(u), 35) then
        return
    endif
    loop
        exitwhen i >= Evo_N
        if Evo_From[i] == id and GetHeroLevel(u) >= Evo_Level[i] then
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DarkRitual\\DarkRitualTarget.mdl", u, "chest"))
            call Mega_SafeReplace(u, Evo_To[i], bj_UNIT_STATE_METHOD_RELATIVE)
            return
        endif
        set i = i + 1
    endloop
endfunction

// v3.3: playable Pokemon max HP x2 in total. Most of their HP comes from Strength (25 per point), so the
// extra is total Strength * 25 * (Hero_HPExtra), kept in Mega_HT key 60 so it can be corrected later.
function Badge_Count takes integer pid returns integer
    local integer g = 0
    local integer n = 0
    loop
        exitwhen g >= 8
        if Badge_Has[pid * 8 + g] then
            set n = n + 1
        endif
        set g = g + 1
    endloop
    return n
endfunction

function Badge_Cap takes integer pid returns integer
    local integer c = 30 + 10 * Badge_Count(pid)
    if c > 100 then
        set c = 100
    endif
    return c
endfunction

// each gym badge (item) a hero carries gives +5 x gym number to Strength, Agility and Intelligence (tracked at key 36)
function Badge_Buff takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer want = 0
    local integer old = LoadInteger(Mega_HT, h, 36)
    local integer s = 0
    local integer g = 0
    local item it = null
    loop
        exitwhen s >= 6
        set it = UnitItemInSlot(u, s)
        if it != null then
            set g = 0
            loop
                exitwhen g >= 8
                if GetItemTypeId(it) == Gym_Item[g] then
                    set want = want + 5 * (g + 1)
                endif
                set g = g + 1
            endloop
        endif
        set s = s + 1
    endloop
    if want != old then
        call SetHeroStr(u, GetHeroStr(u, false) + want - old, true)
        call SetHeroAgi(u, GetHeroAgi(u, false) + want - old, true)
        call SetHeroInt(u, GetHeroInt(u, false) + want - old, true)
        call SaveInteger(Mega_HT, h, 36, want)
    endif
    set it = null
endfunction

function Hero_HPSync takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer old = LoadInteger(Mega_HT, h, 60)
    local integer want = R2I(GetHeroStr(u, true) * Hero_StrHP * Hero_HPExtra)
    local real pct = 0.0
    if want != old then
        set pct = GetUnitLifePercent(u)
        call BlzSetUnitMaxHP(u, BlzGetUnitMaxHP(u) + want - old)
        call SetUnitLifePercentBJ(u, pct)
        call SaveInteger(Mega_HT, h, 60, want)
    endif
endfunction

// every second: the Strength HP bonus and the Mega Evolve button (on the card) of every Pokemon
function Hero_Tick takes nothing returns nothing
    local integer pid = 0
    local unit u = null
    loop
        exitwhen pid >= 12
        call GroupEnumUnitsOfPlayer(Rand_Tmp, Player(pid), null)
        loop
            set u = FirstOfGroup(Rand_Tmp)
            exitwhen u == null
            call GroupRemoveUnit(Rand_Tmp, u)
            if IsUnitType(u, UNIT_TYPE_HERO) and (GetWidgetLife(u) > 0.405) then
                call Hero_HPSync(u)
                call Mega_SyncAbility(u)
                call Evo_Check(u)
                call Badge_Buff(u)
                call SuspendHeroXP(u, GetHeroLevel(u) >= Badge_Cap(pid))
            endif
        endloop
        set pid = pid + 1
    endloop
    set u = null
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
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffff66ccMega refused: already in Mega form|r")
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
function Wild_Scale takes unit u returns nothing
    local integer h = GetHandleId(u)
    local real m = 1.0 + Wild_TierStep * I2R(Wild_Tier)
    local real hpf = 1.0
    local real dmf = 1.0
    local real goldf = 1.0
    local real armadd = 0.0
    local real pct = 0.0
    if LoadInteger(Mega_HT, h, 29) == 1 then
        set hpf = Wild_EliteHP
        set dmf = Wild_EliteDmg
        set goldf = Wild_EliteGold
        set armadd = Wild_EliteArmor
    endif
    set pct = GetUnitLifePercent(u)
    call BlzSetUnitMaxHP(u, R2I(I2R(LoadInteger(Mega_HT, h, 20)) * m * hpf))
    call SetUnitLifePercentBJ(u, pct)
    call BlzSetUnitBaseDamage(u, R2I(I2R(LoadInteger(Mega_HT, h, 21)) * m * dmf * Wild_DmgMult), 0)
    call BlzSetUnitArmor(u, LoadReal(Mega_HT, h, 22) + I2R(Wild_Tier * Wild_TierArmor) + armadd)
    call BlzSetUnitIntegerField(u, UNIT_IF_GOLD_BOUNTY_AWARDED_BASE, R2I(I2R(LoadInteger(Mega_HT, h, 23)) * m * goldf * Wild_GoldMult))
endfunction

// scale a wild creep to the current tier, always from its stored base values
function Wild_Apply takes unit u returns nothing
    local integer h = GetHandleId(u)
    if LoadInteger(Mega_HT, h, 33) == 1 then
        return
    endif
    call SaveInteger(Ab_HT, h, 0, LoadInteger(Ab_HT, GetUnitTypeId(u), 0))  // v3.3: wild creeps have the Ability of their species
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
    if Wild_Tier == 0 and LoadInteger(Mega_HT, h, 29) != 1 then
        return
    endif
    call Wild_Scale(u)
endfunction

// an elite creep of a camp: more HP, damage, armor and gold, bigger and gold-coloured
function Wild_MakeElite takes unit u returns nothing
    local integer k = LoadInteger(Mega_HT, GetUnitTypeId(u), 30)
    local integer j = 0
    call SaveInteger(Mega_HT, GetHandleId(u), 29, 1)
    call Wild_Scale(u)
    call SetUnitScale(u, Wild_EliteScale, Wild_EliteScale, Wild_EliteScale)
    call SetUnitVertexColor(u, 255, 215, 0, 255)
    // the elite fights with the 5 skills of its type
    if k > 0 then
        loop
            exitwhen j >= 5
            call UnitAddAbility(u, Wild_KitSkill[(k - 1) * 5 + j])
            set j = j + 1
        endloop
    endif
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
        if not IsUnitType(u, UNIT_TYPE_DEAD) and Wild_IsWildType(GetUnitTypeId(u)) and LoadInteger(Mega_HT, GetHandleId(u), 33) != 1 then
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
    local integer elite = -1
    if pow > 10 then
        set pow = 10
    endif
    set t = Wild_PickType(pow)
    set Wild_CampDue[c] = 0.0
    set Wild_CampAlive[c] = Wild_CampSize[c]
    if Wild_CampSize[c] > 0 then
        set elite = GetRandomInt(0, Wild_CampSize[c] - 1)
    endif
    loop
        exitwhen i >= Wild_CampSize[c]
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), t, Wild_CampX[c] + GetRandomReal(-150.0, 150.0), Wild_CampY[c] + GetRandomReal(-150.0, 150.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        if i == elite then
            call Wild_MakeElite(u)
        endif
        set i = i + 1
    endloop
    set u = null
endfunction

// v3.3: when the tier goes up, creeps that were not hit yet (full HP) become the species of the new tier,
// one species per camp, keeping position, camp, elite status and HP
function Wild_Upgrade takes nothing returns nothing
    local integer c = 0
    local unit u = null
    local unit nu = null
    local integer h = 0
    local integer pow = 0
    loop
        exitwhen c >= Wild_CampN
        set Wild_UpT[c] = 0
        set c = c + 1
    endloop
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        set h = GetHandleId(u)
        set c = LoadInteger(Mega_HT, h, 25) - 1
        if c >= 0 and Wild_IsWildType(GetUnitTypeId(u)) and GetWidgetLife(u) > 0.405 and GetUnitLifePercent(u) >= 99.9 then
            set pow = Wild_CampPow[c] + Wild_Tier
            if pow > 10 then
                set pow = 10
            endif
            if LoadInteger(Mega_HT, h, 31) < pow then
                if Wild_UpT[c] == 0 then
                    set Wild_UpT[c] = Wild_PickType(pow)
                endif
                set nu = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_UpT[c], GetUnitX(u), GetUnitY(u), GetUnitFacing(u))
                call SaveInteger(Mega_HT, GetHandleId(nu), 25, c + 1)
                call SaveInteger(Mega_HT, GetHandleId(nu), 31, pow)
                call Wild_Apply(nu)
                if LoadInteger(Mega_HT, h, 29) == 1 then
                    call Wild_MakeElite(nu)
                endif
                call FlushChildHashtable(Mega_HT, h)
                call RemoveUnit(u)
            endif
        endif
    endloop
    set u = null
    set nu = null
endfunction

// ---------------------------------------------------------------------------------------------
// Gym teams of 6 (v3.3), levels follow the challenger
// ---------------------------------------------------------------------------------------------
function Gym_Level takes integer base, integer k returns integer
    local integer lv = base
    if k < 5 then  // Pokemon 1..5 are 30, 25, 20, 15, 10 levels below the challenger, Pokemon 6 equals it
        set lv = base - (30 - 5 * k)
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
    loop
        exitwhen g >= 8
        if Gym_Pid[g] == pid then
            return true
        endif
        set g = g + 1
    endloop
    return false
endfunction

function Gym_Spawn takes integer g, integer k returns nothing
    local integer lv = Gym_Level(Gym_Base[g], k)
    local integer pow = lv / 10
    local real m = 1.0 + 0.1 * I2R(g)
    local unit u = null
    local integer ti = 0
    local integer wt = 0
    local integer j = 0
    local integer tries = 0
    local boolean dup = false
    if pow < 1 then
        set pow = 1
    endif
    if pow > 10 then
        set pow = 10
    endif
    loop
        set wt = Wild_PickType(pow)
        set j = 0
        set dup = LoadInteger(Mega_HT, wt, 34) == 0  // gym Pokemon must be able to hold an item (type item known)
        loop
            exitwhen j >= k
            if Gym_Used[g * 6 + j] == wt then
                set dup = true
            endif
            set j = j + 1
        endloop
        set tries = tries + 1
        exitwhen not dup or tries >= 30
    endloop
    set Gym_Used[g * 6 + k] = wt
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), wt, Gym_X[g] + 110.0 * I2R(k - 2), Gym_Y[g], 270.0)
    call SaveInteger(Mega_HT, GetHandleId(u), 33, 1)
    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m))
    call SetUnitLifePercentBJ(u, 100.0)
    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8), 0)
    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m)
    call BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, lv)
    call SetUnitScale(u, 1.2, 1.2, 1.2)
    set ti = LoadInteger(Mega_HT, GetUnitTypeId(u), 34)
    if ti != 0 then  // each gym Pokemon holds the item of its type (dropped when it dies)
        call UnitAddAbility(u, 'AInv')
        call UnitAddItemById(u, ti)
    endif
    set Gym_Cur[g] = u
    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff8800Gym " + I2S(g + 1) + ": Pokemon " + I2S(k + 1) + " of 6 (Lv " + I2S(lv) + ")|r")
    set u = null
endfunction

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
    local unit u = null
    local real dx = 0.0
    local real dy = 0.0
    local boolean started = false
    loop
        exitwhen g >= 8
        if Gym_Pid[g] >= 0 then
            if Gym_Hero[g] == null or GetUnitTypeId(Gym_Hero[g]) == 0 or GetWidgetLife(Gym_Hero[g]) <= 0.405 then
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you lost. The gym starts over.|r")
                call Gym_Reset(g)
                set Gym_Cool[g] = Mega_Time + 10.0
            else
                set dx = GetUnitX(Gym_Hero[g]) - Gym_X[g]
                set dy = GetUnitY(Gym_Hero[g]) - Gym_Y[g]
                if SquareRoot(dx * dx + dy * dy) > Gym_Leave then
                    call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 6.0, "|cffff4040Gym " + I2S(g + 1) + ": you left. The gym starts over.|r")
                    call Gym_Reset(g)
                    set Gym_Cool[g] = Mega_Time + 10.0
                endif
            endif
        elseif Mega_Time >= Gym_Cool[g] then
            set started = false
            call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], Gym_Start, null)
            loop
                set u = FirstOfGroup(Wild_Tmp)
                exitwhen u == null
                call GroupRemoveUnit(Wild_Tmp, u)
                if not started and GetPlayerId(GetOwningPlayer(u)) < 12 and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 and GetUnitTypeId(u) != 'earc' and not Gym_Busy(GetPlayerId(GetOwningPlayer(u))) then
                    set started = true
                    set Gym_Pid[g] = GetPlayerId(GetOwningPlayer(u))
                    set Gym_Hero[g] = u
                    set Gym_Base[g] = GetHeroLevel(u)
                    set Gym_Stage[g] = 0
                    call Gym_Spawn(g, 0)
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
    loop
        exitwhen g >= 8
        if Gym_Pid[g] >= 0 and Gym_Cur[g] != null and d == Gym_Cur[g] then
            set Gym_Stage[g] = Gym_Stage[g] + 1
            if Gym_Stage[g] >= 6 then
                call CreateItem(Gym_Item[g], GetUnitX(d), GetUnitY(d))
                set Badge_Has[Gym_Pid[g] * 8 + g] = true
                call DisplayTimedTextToPlayer(Player(Gym_Pid[g]), 0, 0, 8.0, "|cff66ff66Gym " + I2S(g + 1) + " cleared! The gym item dropped. Badges " + I2S(Badge_Count(Gym_Pid[g])) + "/8, level cap " + I2S(Badge_Cap(Gym_Pid[g])) + ".|r")
                call Gym_Reset(g)
                set Gym_Cool[g] = Mega_Time + 60.0
            else
                set Gym_Cur[g] = null
                call Gym_Spawn(g, Gym_Stage[g])
            endif
        endif
        set g = g + 1
    endloop
    set d = null
    return false
endfunction

function Gym_IsChain takes integer id returns boolean
    local integer i = 0
    loop
        exitwhen i >= 24
        if Gym_Chain[i] == id then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// the original leader chains are replaced by the teams above
function Gym_Init takes nothing returns nothing
    local unit u = null
    local integer g = 0
    local trigger gdt = CreateTrigger()
    set Gym_X[0] = -1405.5
    set Gym_Y[0] = 5887.1
    set Gym_Item[0] = 'I014'
    set Gym_Pid[0] = -1
    set Gym_X[1] = -2683.8
    set Gym_Y[1] = 5896.7
    set Gym_Item[1] = 'I015'
    set Gym_Pid[1] = -1
    set Gym_X[2] = -3969.1
    set Gym_Y[2] = 5890.0
    set Gym_Item[2] = 'I016'
    set Gym_Pid[2] = -1
    set Gym_X[3] = -5377.2
    set Gym_Y[3] = 5888.7
    set Gym_Item[3] = 'I017'
    set Gym_Pid[3] = -1
    set Gym_X[4] = 1154.9
    set Gym_Y[4] = 5877.8
    set Gym_Item[4] = 'I019'
    set Gym_Pid[4] = -1
    set Gym_X[5] = 2436.6
    set Gym_Y[5] = 5898.4
    set Gym_Item[5] = 'I018'
    set Gym_Pid[5] = -1
    set Gym_X[6] = 3716.3
    set Gym_Y[6] = 5866.3
    set Gym_Item[6] = 'I01A'
    set Gym_Pid[6] = -1
    set Gym_X[7] = 5379.5
    set Gym_Y[7] = 5879.2
    set Gym_Item[7] = 'I01B'
    set Gym_Pid[7] = -1
    set Gym_Chain[0] = 'n00S'
    set Gym_Chain[1] = 'n00U'
    set Gym_Chain[2] = 'n00T'
    set Gym_Chain[3] = 'n00R'
    set Gym_Chain[4] = 'n00W'
    set Gym_Chain[5] = 'n00V'
    set Gym_Chain[6] = 'n00X'
    set Gym_Chain[7] = 'n00Y'
    set Gym_Chain[8] = 'n00Z'
    set Gym_Chain[9] = 'n010'
    set Gym_Chain[10] = 'n012'
    set Gym_Chain[11] = 'n011'
    set Gym_Chain[12] = 'n014'
    set Gym_Chain[13] = 'n013'
    set Gym_Chain[14] = 'n015'
    set Gym_Chain[15] = 'n018'
    set Gym_Chain[16] = 'n016'
    set Gym_Chain[17] = 'n017'
    set Gym_Chain[18] = 'n019'
    set Gym_Chain[19] = 'n01A'
    set Gym_Chain[20] = 'n01B'
    set Gym_Chain[21] = 'n01C'
    set Gym_Chain[22] = 'n01D'
    set Gym_Chain[23] = 'n01E'
    loop
        exitwhen g >= 8
        call GroupEnumUnitsInRange(Wild_Tmp, Gym_X[g], Gym_Y[g], 700.0, null)
        loop
            set u = FirstOfGroup(Wild_Tmp)
            exitwhen u == null
            call GroupRemoveUnit(Wild_Tmp, u)
            if Gym_IsChain(GetUnitTypeId(u)) then
                call RemoveUnit(u)
            endif
        endloop
        set g = g + 1
    endloop
    call TriggerRegisterAnyUnitEventBJ(gdt, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(gdt, Condition(function Gym_OnDeath))
    call TimerStart(CreateTimer(), 1.0, true, function Gym_Tick)
    set u = null
    set gdt = null
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
    local unit lg = null
    local integer tries = 0
    local integer i = 0
    local integer c = 0
    local real x = 0.0
    local real y = 0.0
    if Leg_N == 0 then
        return
    endif
    loop
        set i = GetRandomInt(0, Leg_N - 1)
        set tries = tries + 1
        exitwhen Leg_Up[i] == 0 or tries >= 40
    endloop
    if Leg_Up[i] > 0 then
        return
    endif
    if Wild_CampN > 0 then
        set c = GetRandomInt(0, Wild_CampN - 1)
        set x = Wild_CampX[c]
        set y = Wild_CampY[c]
    endif
    set lg = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Leg_Type[i], x, y, 270.0)
    call SaveInteger(Ab_HT, GetHandleId(lg), 0, LoadInteger(Ab_HT, Leg_Type[i], 0))  // v3.3: legends have an Ability
    set lg = null
    set Leg_Alive = Leg_Alive + 1
    set Leg_Up[i] = 1
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
            set Leg_Up[i] = 0
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
        if Wild_Tier > Wild_UpTier then
            set Wild_UpTier = Wild_Tier
            call Wild_Upgrade()
        endif
    endif
    if Wild_Time >= Leg_Next then
        set Leg_Next = Leg_Next + Leg_Interval
        if Leg_Alive < Leg_Max then
            call Leg_Spawn()
        endif
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
        if soul != 0 and LoadInteger(Mega_HT, h, 29) == 1 and GetRandomReal(0.0, 100.0) < Wild_SoulChance then
            call CreateItem(soul, GetUnitX(u), GetUnitY(u))
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff66ccA wild " + GetUnitName(u) + " dropped its Soul!|r")
        endif
        // v3.2: an elite drops a random Mega Stone of the map
        if LoadInteger(Mega_HT, h, 29) == 1 and Mega_N > 0 and GetRandomReal(0.0, 100.0) < Wild_StoneChance then
            call CreateItem(Mega_Stone[GetRandomInt(0, Mega_N - 1)], GetUnitX(u), GetUnitY(u))
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

// a Pokemon bought at a tavern keeps the experience of the owner's best Pokemon (no drop back to level 1)
function Keep_XP takes unit bought returns nothing
    local player p = GetOwningPlayer(bought)
    local unit u = null
    local integer best = 0
    if not IsUnitType(bought, UNIT_TYPE_HERO) then
        set p = null
        return
    endif
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if u != bought and IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitType(u, UNIT_TYPE_DEAD) then
            if GetHeroXP(u) > best then
                set best = GetHeroXP(u)
            endif
        endif
    endloop
    if best > GetHeroXP(bought) then
        call SetHeroXP(bought, best, false)
    endif
    set p = null
    set u = null
endfunction

function Repick_OnSell takes nothing returns nothing
    call Repick_Restore(GetSoldUnit())
    call Keep_XP(GetSoldUnit())
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
            if bj_lastReplacedUnit != null and GetUnitTypeId(bj_lastReplacedUnit) == Soul_Hero[i] then
                // a Soul gives the base form: it evolves only after the next level up (key 35 = level at the Soul)
                call SaveInteger(Mega_HT, GetHandleId(bj_lastReplacedUnit), 35, GetHeroLevel(bj_lastReplacedUnit))
            endif
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
                    // v3.2: the Mega button is the Mega Stone's item ability, no command-card button
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
            call DisplayTimedTextToPlayer(GetOwningPlayer(GetTriggerUnit()), 0, 0, 6.0, "|cffff66ccMega cast received|r")
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
    call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Evolution", "Mua Mega Stone o |cffff66ccMega Shop I|r / |cffff66ccMega Shop II|r (canh Poke Mart).|nBam vao |cffff66ccMega Stone|r trong tui de Mega (o item hien thoi gian hoi chieu).|nMega trong 60 giay: doi model, +30 chi so, +5 giap, +40 toc chay, +25% toc danh. Hoi chieu 150 giay.|nChet khi dang Mega se tro ve dang thuong.|nMega Kangaskhan: con nho di theo, danh them 25% sat thuong.|n|nCredit model Mega: PKLegends team va cac tac gia tren Hive Workshop.", "ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp")
    loop
        exitwhen i >= Mega_N
        set s = s + Mega_StoneName[i] + " (" + I2S(Mega_Price[i]) + ") - " + Mega_Name[i] + "|n"
        set i = i + 1
    endloop
    if Mv_N > 0 then
        call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Learned Moves", "Moi Pokemon co 4 o chieu (phim Q W E R, hang tren cung cua bang lenh) va 1 nut Ability.|n4 chieu dau biet ngay tu level 1. Khi len level, chieu manh hon se thay the chieu yeu nhat (khong hoi thoai).|nSat thuong cac chieu nay tang theo chi so chinh.", "ReplaceableTextures\\CommandButtons\\BTNStormBolt.blp")
    endif
    call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Stones", s, "ReplaceableTextures\\CommandButtons\\BTNMegaGengar.blp")
    if Leg_N > 0 then
        call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Random Legends", "Cu 3 phut xuat hien 2 legend Lv 100 (chi nhung legend khong co phong) tren map (khong gioi han so con).|nChi Pokemon lv 100 moi gay sat thuong duoc.|nGiet duoc: 50% roi Soul cua legend do (cam o o 1, vao vong tron giua map de bien thanh legend).|nQuai hoang da thuong khong roi Soul. Elite cua bai (1 con moi bai): 10% roi Soul cua loai do.", "ReplaceableTextures\\CommandButtons\\BTNSoulGem.blp")
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

// damage multiplier of a skill: 1 + 0.02 * (stat - 50), 1.0 up to 50, at most 10
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

// ---------------------------------------------------------------------------------------------
// Learned moves (docs/superpowers/specs/2026-11-01-learned-moves-design.md). Per unit type in Ab_HT: key 99 = number of
// candidate moves, 100 + 2k = move index, 101 + 2k = hero level at which candidate k becomes available.
// Per hero in Ab_HT (parent = handle id): 40..43 = move index + 1 in slot 0..3, 200 + move = 1 once it was considered.
// ---------------------------------------------------------------------------------------------
// object id of the ability of move m in command-card slot s: A + V/W/Y/Z + two base-36 digits
function Mv_Id takes integer slot, integer m returns integer
    local integer l = 90
    if slot == 0 then
        set l = 86
    elseif slot == 1 then
        set l = 87
    elseif slot == 2 then
        set l = 89
    endif
    return 'A000' - 3158064 + l * 65536 + Ab_Dig(m / 36) * 256 + Ab_Dig(m - (m / 36) * 36)
endfunction

function Mv_Slot takes unit u, integer s returns integer
    return LoadInteger(Ab_HT, GetHandleId(u), 40 + s) - 1
endfunction

function Mv_Known takes unit u, integer m returns boolean
    local integer s = 0
    loop
        exitwhen s >= Mv_Slots
        if Mv_Slot(u, s) == m then
            return true
        endif
        set s = s + 1
    endloop
    return false
endfunction

function Mv_FreeSlot takes unit u returns integer
    local integer s = 0
    loop
        exitwhen s >= Mv_Slots
        if Mv_Slot(u, s) < 0 then
            return s
        endif
        set s = s + 1
    endloop
    return -1
endfunction

// score of the weakest move the hero knows
function Mv_WeakScore takes unit u returns integer
    local integer s = 0
    local integer best = 1000000
    local integer m = 0
    loop
        exitwhen s >= Mv_Slots
        set m = Mv_Slot(u, s)
        if m >= 0 then
            if Mv_Score[m] < best then
                set best = Mv_Score[m]
            endif
        endif
        set s = s + 1
    endloop
    return best
endfunction

// slot of the weakest known move (all slots are full when this is used)
function Mv_WeakSlot takes unit u returns integer
    local integer s = 0
    local integer w = 0
    local integer best = 1000000
    local integer m = 0
    loop
        exitwhen s >= Mv_Slots
        set m = Mv_Slot(u, s)
        if m >= 0 then
            if Mv_Score[m] < best then
                set best = Mv_Score[m]
                set w = s
            endif
        endif
        set s = s + 1
    endloop
    return w
endfunction

// put move m in slot s (the move that was there is forgotten)
function Mv_Put takes unit u, integer s, integer m returns nothing
    local integer h = GetHandleId(u)
    local integer old = LoadInteger(Ab_HT, h, 40 + s) - 1
    if old >= 0 then
        call UnitRemoveAbility(u, Mv_Id(s, old))
    endif
    call SaveInteger(Ab_HT, h, 40 + s, m + 1)
    call UnitAddAbility(u, Mv_Id(s, m))
endfunction

function Mv_Notify takes unit u, integer m returns nothing
    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cff66ff66" + GetHeroProperName(u) + " learned " + Mv_Label[m] + "!|r")
endfunction



// every second for each living hero: keep the abilities of its slots, learn / offer the candidates that became available
function Mv_Sync takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer id = GetUnitTypeId(u)
    local integer lv = GetHeroLevel(u)
    local integer n = LoadInteger(Ab_HT, id, 99)
    local integer k = 0
    local integer s = 0
    local integer m = 0
    loop
        exitwhen s >= Mv_Slots
        set m = Mv_Slot(u, s)
        if m >= 0 then
            if GetUnitAbilityLevel(u, Mv_Id(s, m)) == 0 then
                call UnitAddAbility(u, Mv_Id(s, m))
            endif
        endif
        set s = s + 1
    endloop
    loop
        exitwhen k >= n
        if lv >= LoadInteger(Ab_HT, id, 101 + 2 * k) then
            set m = LoadInteger(Ab_HT, id, 100 + 2 * k)
            if LoadInteger(Ab_HT, h, 200 + m) == 0 then
                if Mv_Known(u, m) then
                    call SaveInteger(Ab_HT, h, 200 + m, 1)
                else
                    set s = Mv_FreeSlot(u)
                    if s >= 0 then
                        call Mv_Put(u, s, m)
                        call Mv_Notify(u, m)
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    elseif Mv_Score[m] > Mv_WeakScore(u) then
                        call Mv_Put(u, Mv_WeakSlot(u), m)
                        call Mv_Notify(u, m)
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    else
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    endif
                endif
            endif
        endif
        set k = k + 1
    endloop
endfunction

// tooltip of a move at the hero's current damage multiplier (main attribute and level)
function Mv_Tip takes integer m, real mult returns string
    local string src = Mv_Text[m]
    local string out = ""
    local string c = ""
    local integer i = 0
    local integer n = StringLength(src)
    loop
        exitwhen i >= n
        set c = SubString(src, i, i + 1)
        if c == "@" and i + 1 < n then
            if SubString(src, i + 1, i + 2) == "1" then
                set out = out + "|cff66ff66" + I2S(R2I(I2R(Mv_D1[m]) * mult)) + "|r"
            else
                set out = out + "|cff66ff66" + I2S(R2I(I2R(Mv_D2[m]) * mult)) + "|r"
            endif
            set i = i + 2
        else
            set out = out + c
            set i = i + 1
        endif
    endloop
    return out + "|n|cff66ff66Damage now x" + I2S(R2I(mult * 100.0)) + "% (grows with main stat and level)|r"
endfunction

function Mv_Tips takes unit u returns nothing
    local player p = GetOwningPlayer(u)
    local real mult = Ab_SkillMult(Ab_MainStat(u))
    local integer lv = GetHeroLevel(u)
    local integer s = 0
    local integer m = 0
    if lv > 50 then
        set mult = mult * (1.0 + Ab_LevelK * I2R(lv - 50))
    endif
    loop
        exitwhen s >= Mv_Slots
        set m = Mv_Slot(u, s)
        if m >= 0 and Mv_Text[m] != null and Mv_Text[m] != "" then
            if GetLocalPlayer() == p then
                call BlzSetAbilityExtendedTooltip(Mv_Id(s, m), Mv_Tip(m, mult), 0)
            endif
        endif
        set s = s + 1
    endloop
    set p = null
endfunction

function Mv_Init takes nothing returns nothing
    call Mv_InitData()
endfunction

function Ab_Hero takes unit u returns nothing
    local integer a = 0
    local integer k = 0
    call Mv_Sync(u)
    call Mv_Tips(u)
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
    if user and atk and IsUnitType(src, UNIT_TYPE_HERO) then
        set m = m * Ab_BasicMult
    endif
    if user and BlzGetEventDamageType() != DAMAGE_TYPE_NORMAL then
        if IsUnitType(src, UNIT_TYPE_HERO) then
            set stat = Ab_MainStat(src)
        else
            set stat = Ab_PlayerStat(sp)
        endif
        set m = m * Ab_SkillMult(stat)
        if IsUnitType(src, UNIT_TYPE_HERO) and GetHeroLevel(src) > 50 then
            set m = m * (1.0 + Ab_LevelK * I2R(GetHeroLevel(src) - 50))
        endif
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
    if ta == 0 and IsUnitType(t, UNIT_TYPE_HERO) then
        call SaveReal(Ab_HT, GetHandleId(t), 1, Mega_Time)
    endif
    call BlzSetEventDamage(dmg * m)
    set t = null
    set src = null
    set sp = null
    return false
endfunction

// tester command "-stats": the numbers that decide balance (hero level, main stat, skill multiplier, HP, armor, tier)
function Dbg_Stats takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local unit u = null
    local unit h = null
    local real st = 0.0
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) and (GetWidgetLife(u) > 0.405) then
            set h = u
        endif
    endloop
    if h == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00-stats: no living Pokemon.|r")
    else
        set st = Ab_MainStat(h)
        call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00" + GetHeroProperName(h) + "|r lv " + I2S(GetHeroLevel(h)) + " | main stat " + I2S(R2I(st)) + " | skill damage x" + I2S(R2I(Ab_SkillMult(st) * 100.0)) + "% | HP " + I2S(R2I(GetWidgetLife(h))) + "/" + I2S(R2I(BlzGetUnitMaxHP(h))) + " | armor " + I2S(R2I(BlzGetUnitArmor(h))) + " | wild tier " + I2S(Wild_Tier))
    endif
    set p = null
    set u = null
    set h = null
endfunction

// tester command "-spawn": the host gets a wild creep of the current tier next to his Pokemon
// tester command "-pos": prints the position of your living Pokemon (for placing NPCs)
function Dbg_Pos takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local unit h = null
    local unit u = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) and (GetWidgetLife(u) > 0.405) then
            set h = u
        endif
    endloop
    if h == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffffcc00-pos: no living Pokemon.|r")
    else
        call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00-pos|r X " + I2S(R2I(GetUnitX(h))) + " Y " + I2S(R2I(GetUnitY(h))))
    endif
    set p = null
    set u = null
    set h = null
endfunction

function Dbg_Spawn takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local unit h = null
    local unit u = null
    local integer pow = Wild_Tier + 1
    if GetPlayerId(p) != Host_Id() then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Only the host can type -spawn.|r")
        set p = null
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
    if pow > 10 then
        set pow = 10
    endif
    if h != null then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_PickType(pow), GetUnitX(h) + 200.0, GetUnitY(h), 0.0)
        call Wild_Apply(u)
    endif
    set p = null
    set h = null
    set u = null
endfunction

// NPC: moves of the hero of player pid in one dialog; kind 1 = slot, 2 = forget, 3 = learn, 4 = back
function Mv_Clear takes unit u, integer s returns nothing
    local integer old = Mv_Slot(u, s)
    if old >= 0 then
        call UnitRemoveAbility(u, Mv_Id(s, old))
    endif
    call SaveInteger(Ab_HT, GetHandleId(u), 40 + s, 0)
endfunction

function Npc_Label takes unit h, integer s returns string
    local integer m = Mv_Slot(h, s)
    if m < 0 then
        return "(empty)"
    endif
    return Mv_Label[m]
endfunction

function Npc_Show takes integer pid, unit h, integer s returns nothing
    local integer b = pid * 12
    local integer k = 0
    local integer n = 0
    local integer id = GetUnitTypeId(h)
    local integer m = 0
    local integer lv = 0
    local integer cnt = 0
    local string msg = ""
    local dialog d = Npc_Dlg[pid]
    local player p = Player(pid)
    set Npc_Slot[pid] = s
    call DialogClear(d)
    if s < 0 then
        set msg = "Moves of " + GetHeroProperName(h) + ". Choose a slot:"
        loop
            exitwhen k >= Mv_Slots
            set Npc_Btn[b + k] = DialogAddButton(d, "Slot " + I2S(k + 1) + ": " + Npc_Label(h, k), 0)
            set Npc_Kind[b + k] = 1
            set Npc_Val[b + k] = k
            set k = k + 1
        endloop
        set n = Mv_Slots
        set Npc_Btn[b + n] = DialogAddButton(d, "Close", 0)
        set Npc_Kind[b + n] = 0
        set n = n + 1
    elseif Npc_Mode[pid] == 1 then
        set msg = "TM/HM moves for slot " + I2S(s + 1) + " (" + I2S(Npc_TMCost) + " gold each, page " + I2S(Npc_TMPage[pid] + 1) + ")"
        set cnt = LoadInteger(Ab_HT, id, 299)
        set k = 0
        set lv = 0
        loop
            exitwhen k >= cnt
            set m = LoadInteger(Ab_HT, id, 300 + k)
            if not Mv_Known(h, m) then
                if lv >= Npc_TMPage[pid] * 8 and lv < Npc_TMPage[pid] * 8 + 8 then
                    set Npc_Btn[b + n] = DialogAddButton(d, Mv_Label[m], 0)
                    set Npc_Kind[b + n] = 6
                    set Npc_Val[b + n] = m
                    set n = n + 1
                endif
                set lv = lv + 1
            endif
            set k = k + 1
        endloop
        if Npc_TMPage[pid] > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
            set Npc_Kind[b + n] = 7
            set n = n + 1
        endif
        if lv > (Npc_TMPage[pid] + 1) * 8 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
            set Npc_Kind[b + n] = 8
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 9
        set n = n + 1
    else
        set msg = "Slot " + I2S(s + 1) + ": " + Npc_Label(h, s) + ". Choose:"
        if Mv_Slot(h, s) >= 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "Forget " + Npc_Label(h, s) + " (free)", 0)
            set Npc_Kind[b + n] = 2
            set Npc_Val[b + n] = s
            set n = n + 1
        endif
        set cnt = LoadInteger(Ab_HT, id, 99)
        loop
            exitwhen k >= cnt or n >= 10
            set m = LoadInteger(Ab_HT, id, 100 + 2 * k)
            set lv = LoadInteger(Ab_HT, id, 101 + 2 * k)
            if lv <= GetHeroLevel(h) and not Mv_Known(h, m) then
                set Npc_Btn[b + n] = DialogAddButton(d, "Learn " + Mv_Label[m] + " (" + I2S(Npc_LearnCost) + " gold)", 0)
                set Npc_Kind[b + n] = 3
                set Npc_Val[b + n] = m
                set n = n + 1
            endif
            set k = k + 1
        endloop
        if LoadInteger(Ab_HT, id, 299) > 0 then
            set Npc_Btn[b + n] = DialogAddButton(d, "TM/HM moves (" + I2S(Npc_TMCost) + " gold)", 0)
            set Npc_Kind[b + n] = 5
            set n = n + 1
        endif
        set Npc_Btn[b + n] = DialogAddButton(d, "Back", 0)
        set Npc_Kind[b + n] = 4
        set n = n + 1
    endif
    call DialogSetMessage(d, msg)
    call DialogDisplay(p, d, true)
    set d = null
    set p = null
endfunction

function Npc_OnChat takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pid = GetPlayerId(p)
    local unit u = null
    local unit h = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, p, null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if h == null and IsUnitType(u, UNIT_TYPE_HERO) and GetWidgetLife(u) > 0.405 then
            set h = u
        endif
    endloop
    if h == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00You need a living Pokemon.|r")
    elseif SquareRoot((GetUnitX(h) - Npc_X) * (GetUnitX(h) - Npc_X) + (GetUnitY(h) - Npc_Y) * (GetUnitY(h) - Npc_Y)) > Npc_Range then
        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00Go to the moves NPC first.|r")
    else
        set Npc_Unit[pid] = h
        set Npc_Mode[pid] = 0
        call Npc_Show(pid, h, -1)
    endif
    set p = null
    set u = null
    set h = null
endfunction

function Npc_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer b = 0
    local unit h = null
    loop
        exitwhen pid >= 12 or Npc_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid < 12 then
        set b = pid * 12
        loop
            exitwhen i >= 12 or Npc_Btn[b + i] == bt
            set i = i + 1
        endloop
        set h = Npc_Unit[pid]
        if i < 12 and h != null and GetUnitTypeId(h) != 0 then
            if Npc_Kind[b + i] == 0 then
                call DialogDisplay(Player(pid), d, false)
            elseif Npc_Kind[b + i] == 1 then
                call Npc_Show(pid, h, Npc_Val[b + i])
            elseif Npc_Kind[b + i] == 2 then
                call Mv_Clear(h, Npc_Val[b + i])
                call Npc_Show(pid, h, -1)
            elseif Npc_Kind[b + i] == 5 then
                set Npc_Mode[pid] = 1
                set Npc_TMPage[pid] = 0
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 7 then
                set Npc_TMPage[pid] = Npc_TMPage[pid] - 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 8 then
                set Npc_TMPage[pid] = Npc_TMPage[pid] + 1
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 9 then
                set Npc_Mode[pid] = 0
                call Npc_Show(pid, h, Npc_Slot[pid])
            elseif Npc_Kind[b + i] == 6 then
                if GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) >= Npc_TMCost then
                    call SetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) - Npc_TMCost)
                    call Mv_Put(h, Npc_Slot[pid], Npc_Val[b + i])
                    call SaveInteger(Ab_HT, GetHandleId(h), 200 + Npc_Val[b + i], 1)
                    call Mv_Notify(h, Npc_Val[b + i])
                    set Npc_Mode[pid] = 0
                    call Npc_Show(pid, h, -1)
                else
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Not enough gold.|r")
                    call Npc_Show(pid, h, Npc_Slot[pid])
                endif
            elseif Npc_Kind[b + i] == 3 then
                if GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) >= Npc_LearnCost then
                    call SetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(pid), PLAYER_STATE_RESOURCE_GOLD) - Npc_LearnCost)
                    call Mv_Put(h, Npc_Slot[pid], Npc_Val[b + i])
                    call SaveInteger(Ab_HT, GetHandleId(h), 200 + Npc_Val[b + i], 1)
                    call Mv_Notify(h, Npc_Val[b + i])
                    call Npc_Show(pid, h, -1)
                else
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Not enough gold.|r")
                    call Npc_Show(pid, h, Npc_Slot[pid])
                endif
            else
                call Npc_Show(pid, h, -1)
            endif
        endif
    endif
    set d = null
    set bt = null
    set h = null
endfunction

// ---------------------------------------------------------------------------------------------
// Pokemon picker (v3.3): select the tavern (or type -pick) while you still hold the picker wisp
// buttons per player: 9 Pokemon + Prev + Next + Close = 12; Pick_Val: >= 0 Pokemon index, -1 prev, -2 next, -3 close
// ---------------------------------------------------------------------------------------------
function Pick_Show takes integer pid, integer page returns nothing
    local dialog d = Pick_Dlg[pid]
    local integer b = pid * 12
    local integer g = Pick_Grp[pid]
    local integer total = Pick_TN
    local integer base = 0
    local integer k = 0
    local integer n = 0
    local integer pages = 0
    local string msg = ""
    if Pick_N == 0 then
        return
    endif
    if g >= 0 then
        set total = Pick_TCount[g]
        set base = Pick_TFirst[g]
    endif
    set pages = (total + 7) / 8
    if page < 0 then
        set page = 0
    endif
    set Pick_Page[pid] = page
    call DialogClear(d)
    loop
        exitwhen k >= 8 or page * 8 + k >= total
        if g < 0 then
            set Pick_Btn[b + n] = DialogAddButton(d, Pick_TName[page * 8 + k] + " (" + I2S(Pick_TCount[page * 8 + k]) + ")", 0)
            set Pick_Val[b + n] = 1000 + page * 8 + k
        else
            set Pick_Btn[b + n] = DialogAddButton(d, Pick_Name[base + page * 8 + k], 0)
            set Pick_Val[b + n] = base + page * 8 + k
        endif
        set n = n + 1
        set k = k + 1
    endloop
    if page > 0 then
        set Pick_Btn[b + n] = DialogAddButton(d, "< Prev page", 0)
        set Pick_Val[b + n] = -1
        set n = n + 1
    endif
    if page < pages - 1 then
        set Pick_Btn[b + n] = DialogAddButton(d, "Next page >", 0)
        set Pick_Val[b + n] = -2
        set n = n + 1
    endif
    if g >= 0 then
        set Pick_Btn[b + n] = DialogAddButton(d, "Back to types", 0)
        set Pick_Val[b + n] = -4
        set n = n + 1
        set msg = Pick_TName[g] + " Pokemon (page " + I2S(page + 1) + " of " + I2S(pages) + ")"
    else
        set msg = "Choose a type (page " + I2S(page + 1) + " of " + I2S(pages) + ")"
    endif
    set Pick_Btn[b + n] = DialogAddButton(d, "Close", 0)
    set Pick_Val[b + n] = -3
    call DialogSetMessage(d, msg)
    call DialogDisplay(Player(pid), d, true)
    set d = null
endfunction

function Pick_Choose takes integer pid, integer idx returns nothing
    local player p = Player(pid)
    local unit w = Rand_FindWisp(p)
    local unit h = null
    if w == null then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00You already have a Pokemon. Type -repick in the first 2 minutes to choose again.|r")
    elseif Rand_IsTaken(Pick_Type[idx]) then
        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Another player already has that Pokemon.|r")
        call Pick_Show(pid, Pick_Page[pid])
    else
        set h = CreateUnit(p, Pick_Type[idx], GetUnitX(w), GetUnitY(w), 270.0)
        call Repick_Restore(h)
        call RemoveUnit(w)
        call SelectUnitForPlayerSingle(h, p)
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00" + GetPlayerName(p) + "|r has chosen |cffffcc00" + GetHeroProperName(h) + "|r")
    endif
    set p = null
    set w = null
    set h = null
endfunction

function Pick_OnClick takes nothing returns nothing
    local dialog d = GetClickedDialog()
    local button bt = GetClickedButton()
    local integer pid = 0
    local integer i = 0
    local integer b = 0
    loop
        exitwhen pid >= 12 or Pick_Dlg[pid] == d
        set pid = pid + 1
    endloop
    if pid < 12 then
        set b = pid * 12
        loop
            exitwhen i >= 12 or Pick_Btn[b + i] == bt
            set i = i + 1
        endloop
        if i < 12 then
            if Pick_Val[b + i] >= 1000 then
                set Pick_Grp[pid] = Pick_Val[b + i] - 1000
                call Pick_Show(pid, 0)
            elseif Pick_Val[b + i] >= 0 then
                call Pick_Choose(pid, Pick_Val[b + i])
            elseif Pick_Val[b + i] == -4 then
                set Pick_Grp[pid] = -1
                call Pick_Show(pid, 0)
            elseif Pick_Val[b + i] == -1 then
                call Pick_Show(pid, Pick_Page[pid] - 1)
            elseif Pick_Val[b + i] == -2 then
                call Pick_Show(pid, Pick_Page[pid] + 1)
            endif
        endif
    endif
    set d = null
    set bt = null
endfunction

function Pick_OnSelect takes nothing returns nothing
    if GetUnitTypeId(GetTriggerUnit()) == 'nTV5' and Rand_FindWisp(GetTriggerPlayer()) != null then
        set Pick_Grp[GetPlayerId(GetTriggerPlayer())] = -1
        call Pick_Show(GetPlayerId(GetTriggerPlayer()), 0)
    endif
endfunction

function Pick_OnChat takes nothing returns nothing
    if Rand_FindWisp(GetTriggerPlayer()) != null then
        set Pick_Grp[GetPlayerId(GetTriggerPlayer())] = -1
        call Pick_Show(GetPlayerId(GetTriggerPlayer()), 0)
    else
        call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 6.0, "|cffffcc00You already have a Pokemon.|r")
    endif
endfunction

function Pick_Init takes nothing returns nothing
    local trigger pk_sel = CreateTrigger()
    local trigger pk_chat = CreateTrigger()
    local trigger pk_dlg = CreateTrigger()
    local integer i = 0
    call Pick_InitData()
    loop
        exitwhen i >= 12
        set Pick_Dlg[i] = DialogCreate()
        set Pick_Grp[i] = -1
        call TriggerRegisterPlayerChatEvent(pk_chat, Player(i), "-pick", true)
        call TriggerRegisterDialogEvent(pk_dlg, Pick_Dlg[i])
        set i = i + 1
    endloop
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerUnitEvent(pk_sel, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
        set i = i + 1
    endloop
    call TriggerAddAction(pk_sel, function Pick_OnSelect)
    call TriggerAddAction(pk_chat, function Pick_OnChat)
    call TriggerAddAction(pk_dlg, function Pick_OnClick)
    set pk_sel = null
    set pk_chat = null
    set pk_dlg = null
endfunction

// Haunt Legendary shop (v3.3): the Celebi and Darkrai teleport items move the buyer next to their rooms
function LegTele_OnSell takes nothing returns boolean
    local integer it = GetItemTypeId(GetSoldItem())
    local unit b = GetBuyingUnit()
    if it == 'IL00' then
        call SetUnitPosition(b, 9600.0, -2588.0)
    elseif it == 'IL01' then
        call SetUnitPosition(b, -9600.0, -2209.0)
    else
        set b = null
        return false
    endif
    call PanCameraToTimedForPlayer(GetOwningPlayer(b), GetUnitX(b), GetUnitY(b), 0.25)
    set b = null
    return false
endfunction

// v3.3: a hero that dies drops the Souls it carries (item names end with "Soul")
function Soul_DropOnDeath takes nothing returns boolean
    local unit u = GetDyingUnit()
    local integer s = 0
    local item it = null
    local string n = ""
    local integer len = 0
    if IsUnitType(u, UNIT_TYPE_HERO) then
        loop
            exitwhen s >= 6
            set it = UnitItemInSlot(u, s)
            if it != null then
                set n = GetItemName(it)
                set len = StringLength(n)
                if len >= 4 and SubString(n, len - 4, len) == "Soul" then
                    call UnitRemoveItem(u, it)
                endif
            endif
            set s = s + 1
        endloop
    endif
    set u = null
    set it = null
    return false
endfunction

// v3.3: floating damage number over the target for skill damage (not basic attacks) dealt by a player; the owner sees it
function Dmg_OnDamaged takes nothing returns boolean
    local unit src = GetEventDamageSource()
    local unit t = GetTriggerUnit()
    local player p = null
    local real d = GetEventDamage()
    local texttag tt = null
    if src != null and d >= 1.0 and Dmg_Tags < Dmg_TagMax and not BlzGetEventIsAttack() then
        set p = GetOwningPlayer(src)
        if GetPlayerId(p) < 12 and IsUnitEnemy(t, p) then
            set Dmg_Tags = Dmg_Tags + 1
            set tt = CreateTextTag()
            call SetTextTagText(tt, I2S(R2I(d)), 0.025)
            call SetTextTagPos(tt, GetUnitX(t) - 40.0, GetUnitY(t), 80.0)
            call SetTextTagColor(tt, 255, 210, 40, 255)
            call SetTextTagVelocity(tt, 0.0, 0.04)
            call SetTextTagPermanent(tt, false)
            call SetTextTagLifespan(tt, 1.3)
            call SetTextTagFadepoint(tt, 0.7)
            call SetTextTagVisibility(tt, GetLocalPlayer() == p)
        endif
    endif
    set src = null
    set t = null
    set p = null
    set tt = null
    return false
endfunction

function Dmg_Reset takes nothing returns nothing
    set Dmg_Tags = 0
endfunction

function Type_Has takes string name, string word returns boolean
    local integer i = 0
    local integer n = StringLength(name)
    local integer w = StringLength(word)
    loop
        exitwhen i + w > n
        if SubString(name, i, i + w) == word then
            return true
        endif
        set i = i + 1
    endloop
    return false
endfunction

// a type item bought by a Pokemon of another type is taken back and the gold refunded
function Type_OnSell takes nothing returns boolean
    local item it = GetSoldItem()
    local unit b = GetBuyingUnit()
    local integer id = GetItemTypeId(it)
    local integer i = 0
    loop
        exitwhen i >= Type_N
        if Type_Item[i] == id then
            if not Type_Has(GetUnitName(b), Type_Word[i]) then
                call RemoveItem(it)
                call SetPlayerState(GetOwningPlayer(b), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(GetOwningPlayer(b), PLAYER_STATE_RESOURCE_GOLD) + Type_Cost[i])
                call DisplayTimedTextToPlayer(GetOwningPlayer(b), 0, 0, 6.0, "|cffffcc00Only " + Type_Word[i] + " type Pokemon can buy this item.|r")
            endif
            set it = null
            set b = null
            return false
        endif
        set i = i + 1
    endloop
    set it = null
    set b = null
    return false
endfunction

// ---------------------------------------------------------------------------------------------
// Duel (v3.4): -duel <player name start>, then the other player types -accept. Both Pokemon are healed and the guest is
// moved next to the challenger; the duel ends when one Pokemon is under 15% HP (or dies), after 2 minutes (draw) or
// when a Pokemon is gone. Winner: +500 gold and a win in -rank.
function Duel_Hero takes integer pid returns unit
    local unit u = null
    local unit r = null
    call GroupEnumUnitsOfPlayer(Rand_Tmp, Player(pid), null)
    loop
        set u = FirstOfGroup(Rand_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Rand_Tmp, u)
        if r == null and IsUnitType(u, UNIT_TYPE_HERO) and GetUnitTypeId(u) != 'earc' and GetWidgetLife(u) > 0.405 then
            set r = u
        endif
    endloop
    set u = null
    return r
endfunction

function Duel_Heal takes unit u returns nothing
    if u != null and GetUnitTypeId(u) != 0 then
        call SetUnitState(u, UNIT_STATE_LIFE, I2R(BlzGetUnitMaxHP(u)))
        call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
    endif
endfunction

function Duel_Find takes string arg, integer self returns integer
    local string a = StringCase(arg, false)
    local string n = ""
    local integer i = 0
    if a == "" then
        return -1
    endif
    loop
        exitwhen i >= 12
        if i != self and GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING then
            set n = StringCase(GetPlayerName(Player(i)), false)
            if SubString(n, 0, StringLength(a)) == a then
                return i
            endif
        endif
        set i = i + 1
    endloop
    return -1
endfunction

function Duel_Finish takes integer a, integer b, integer win returns nothing
    local integer lose = -1
    if win == a then
        set lose = b
    elseif win == b then
        set lose = a
    endif
    call SetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE, Duel_Allied[a * 12 + b])
    call SetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE, Duel_Allied[b * 12 + a])
    if GetUnitTypeId(Duel_U[a]) != 0 then
        if GetWidgetLife(Duel_U[a]) <= 0.405 then
            call ReviveHero(Duel_U[a], GetUnitX(Duel_U[a]), GetUnitY(Duel_U[a]), false)
        endif
        call Duel_Heal(Duel_U[a])
        call SetUnitPosition(Duel_U[a], Duel_RX[a], Duel_RY[a])
    endif
    if GetUnitTypeId(Duel_U[b]) != 0 then
        if GetWidgetLife(Duel_U[b]) <= 0.405 then
            call ReviveHero(Duel_U[b], GetUnitX(Duel_U[b]), GetUnitY(Duel_U[b]), false)
        endif
        call Duel_Heal(Duel_U[b])
        call SetUnitPosition(Duel_U[b], Duel_RX[b], Duel_RY[b])
    endif
    set Duel_Foe[a] = -1
    set Duel_Foe[b] = -1
    set Duel_U[a] = null
    set Duel_U[b] = null
    if win >= 0 then
        set Duel_Wins[win] = Duel_Wins[win] + 1
        set Duel_Losses[lose] = Duel_Losses[lose] + 1
        call SetPlayerState(Player(win), PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(Player(win), PLAYER_STATE_RESOURCE_GOLD) + 500)
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00Duel: " + GetPlayerName(Player(win)) + " beat " + GetPlayerName(Player(lose)) + "! (+500 gold)|r")
    else
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00Duel: " + GetPlayerName(Player(a)) + " and " + GetPlayerName(Player(b)) + " drew.|r")
    endif
endfunction

function Duel_Start takes integer a, integer b returns nothing
    local unit dha = Duel_Hero(a)
    local unit dhb = Duel_Hero(b)
    if dha == null or dhb == null then
        call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
        call DisplayTimedTextToPlayer(Player(b), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
    else
        set Duel_Foe[a] = b
        set Duel_Foe[b] = a
        set Duel_Ask[a] = -1
        set Duel_Ask[b] = -1
        set Duel_U[a] = dha
        set Duel_U[b] = dhb
        set Duel_T[a] = 0.0
        set Duel_RX[a] = GetUnitX(dha)
        set Duel_RY[a] = GetUnitY(dha)
        set Duel_RX[b] = GetUnitX(dhb)
        set Duel_RY[b] = GetUnitY(dhb)
        set Duel_Allied[a * 12 + b] = GetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE)
        set Duel_Allied[b * 12 + a] = GetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE)
        call SetPlayerAlliance(Player(a), Player(b), ALLIANCE_PASSIVE, false)
        call SetPlayerAlliance(Player(b), Player(a), ALLIANCE_PASSIVE, false)
        call SetUnitPosition(dhb, GetUnitX(dha) + 400.0, GetUnitY(dha))
        call Duel_Heal(dha)
        call Duel_Heal(dhb)
        call PanCameraToTimedForPlayer(Player(b), GetUnitX(dhb), GetUnitY(dhb), 0.25)
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff8800Duel: " + GetPlayerName(Player(a)) + " vs " + GetPlayerName(Player(b)) + "! The first Pokemon under 15% HP loses.|r")
    endif
    set dha = null
    set dhb = null
endfunction

function Duel_Tick takes nothing returns nothing
    local integer a = 0
    local integer b = 0
    local unit dha = null
    local unit dhb = null
    loop
        exitwhen a >= 12
        set b = Duel_Foe[a]
        if b > a then
            set Duel_T[a] = Duel_T[a] + 0.25
            if GetUnitTypeId(Duel_U[a]) == 0 then
                set Duel_U[a] = Duel_Hero(a)
            endif
            if GetUnitTypeId(Duel_U[b]) == 0 then
                set Duel_U[b] = Duel_Hero(b)
            endif
            set dha = Duel_U[a]
            set dhb = Duel_U[b]
            if dha == null or GetUnitTypeId(dha) == 0 then
                call Duel_Finish(a, b, b)
            elseif dhb == null or GetUnitTypeId(dhb) == 0 then
                call Duel_Finish(a, b, a)
            elseif GetWidgetLife(dha) <= 0.405 or GetWidgetLife(dha) < 0.15 * I2R(BlzGetUnitMaxHP(dha)) then
                call Duel_Finish(a, b, b)
            elseif GetWidgetLife(dhb) <= 0.405 or GetWidgetLife(dhb) < 0.15 * I2R(BlzGetUnitMaxHP(dhb)) then
                call Duel_Finish(a, b, a)
            elseif Duel_T[a] >= 120.0 then
                call Duel_Finish(a, b, -1)
            endif
        endif
        set a = a + 1
    endloop
    set dha = null
    set dhb = null
endfunction

function Duel_OnChat takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local string s = GetEventPlayerChatString()
    local string arg = SubString(s, 6, StringLength(s))
    local integer foe = Duel_Find(arg, me)
    if Duel_Foe[me] >= 0 then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00You are already in a duel.|r")
    elseif foe < 0 then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 8.0, "|cffffcc00Type -duel and the start of a player's name, for example -duel Ash.|r")
    elseif Duel_Foe[foe] >= 0 or Gym_Busy(me) or Gym_Busy(foe) then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00That player (or you) is busy in a duel or gym.|r")
    elseif Duel_Hero(me) == null or Duel_Hero(foe) == null then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Both players need a Pokemon.|r")
    else
        set Duel_Ask[foe] = me
        call DisplayTimedTextToPlayer(Player(foe), 0, 0, 12.0, "|cffff8800" + GetPlayerName(Player(me)) + " challenges you to a duel! Type -accept or -decline.|r")
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 8.0, "|cffffcc00Challenge sent to " + GetPlayerName(Player(foe)) + ".|r")
    endif
endfunction

function Duel_OnAccept takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local integer a = Duel_Ask[me]
    if a < 0 or Duel_Foe[a] >= 0 or Duel_Foe[me] >= 0 or Gym_Busy(me) or Gym_Busy(a) then
        call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Nobody is waiting for your answer.|r")
    else
        call Duel_Start(a, me)
    endif
endfunction

function Duel_OnDecline takes nothing returns nothing
    local integer me = GetPlayerId(GetTriggerPlayer())
    local integer a = Duel_Ask[me]
    if a >= 0 then
        set Duel_Ask[me] = -1
        call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00" + GetPlayerName(Player(me)) + " declined the duel.|r")
    endif
endfunction

function Duel_OnRank takes nothing returns nothing
    local integer i = 0
    local player p = GetTriggerPlayer()
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00Duel record (wins / losses) and badges:|r")
    loop
        exitwhen i >= 12
        if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING then
            call DisplayTimedTextToPlayer(p, 0, 0, 12.0, GetPlayerName(Player(i)) + ": " + I2S(Duel_Wins[i]) + " / " + I2S(Duel_Losses[i]) + " | badges " + I2S(Badge_Count(i)) + "/8, level cap " + I2S(Badge_Cap(i)))
        endif
        set i = i + 1
    endloop
    set p = null
endfunction

function Duel_Init takes nothing returns nothing
    local trigger dq1 = CreateTrigger()
    local trigger dq2 = CreateTrigger()
    local trigger dq3 = CreateTrigger()
    local trigger duelq4 = CreateTrigger()
    local integer i = 0
    loop
        exitwhen i >= 12
        set Duel_Foe[i] = -1
        set Duel_Ask[i] = -1
        call TriggerRegisterPlayerChatEvent(dq1, Player(i), "-duel", false)
        call TriggerRegisterPlayerChatEvent(dq2, Player(i), "-accept", true)
        call TriggerRegisterPlayerChatEvent(dq3, Player(i), "-decline", true)
        call TriggerRegisterPlayerChatEvent(duelq4, Player(i), "-rank", true)
        call TriggerRegisterPlayerChatEvent(duelq4, Player(i), "-badges", true)
        set i = i + 1
    endloop
    call TriggerAddAction(dq1, function Duel_OnChat)
    call TriggerAddAction(dq2, function Duel_OnAccept)
    call TriggerAddAction(dq3, function Duel_OnDecline)
    call TriggerAddAction(duelq4, function Duel_OnRank)
    call TimerStart(Duel_Timer, 0.25, true, function Duel_Tick)
    set dq1 = null
    set dq2 = null
    set dq3 = null
    set duelq4 = null
endfunction

function Npc_IsMan takes nothing returns boolean
    return GetTriggerUnit() == Npc_Man
endfunction

function Mega_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    local trigger lt = null
    local trigger sdt = null
    local trigger nst = null
    local trigger dmt = null
    local trigger tyt = null
    local texttag ntt = null
    local integer i = 0
    call Mega_InitData()
    call Rand_InitData()
    call Evo_InitData()
    call Leg_InitData()
    call Ab_InitData()
    call Mv_Init()
    call Pick_Init()
    call Gym_Init()
    call Duel_Init()
    set sdt = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(sdt, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(sdt, Condition(function Soul_DropOnDeath))
    set lt = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(lt, EVENT_PLAYER_UNIT_SELL_ITEM)
    call TriggerAddCondition(lt, Condition(function LegTele_OnSell))
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
    call FogEnable(false)
    call FogMaskEnable(false)
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
    call TimerStart(Hero_Timer, 1.0, true, function Hero_Tick)
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
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-stats", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Dbg_Stats)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-spawn", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Dbg_Spawn)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-pos", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Dbg_Pos)
    set Npc_Man = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'hpea', Npc_X, Npc_Y, 270.0)
    call SetUnitScale(Npc_Man, 1.8, 1.8, 1.8)
    call SetUnitInvulnerable(Npc_Man, true)
    set ntt = CreateTextTag()
    call SetTextTagText(ntt, "|cffffcc00MOVES NPC|r (click)", 0.024)
    call SetTextTagPos(ntt, Npc_X - 110.0, Npc_Y, 160.0)
    call SetTextTagPermanent(ntt, true)
    call SetTextTagVisibility(ntt, true)
    call PingMinimap(Npc_X, Npc_Y, 8.0)
    call Type_InitData()
    set tyt = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(tyt, EVENT_PLAYER_UNIT_SELL_ITEM)
    call TriggerAddCondition(tyt, Condition(function Type_OnSell))
    set dmt = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(dmt, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddCondition(dmt, Condition(function Dmg_OnDamaged))
    call TimerStart(CreateTimer(), 1.0, true, function Dmg_Reset)
    set nst = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerUnitEvent(nst, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
        set i = i + 1
    endloop
    call TriggerAddCondition(nst, Condition(function Npc_IsMan))
    call TriggerAddAction(nst, function Npc_OnChat)
    set i = 0
    loop
        exitwhen i >= 12
        set Npc_Dlg[i] = DialogCreate()
        set i = i + 1
    endloop
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterDialogEvent(t, Npc_Dlg[i])
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Npc_OnClick)
    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-moves", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Npc_OnChat)
    call TimerStart(CreateTimer(), 3.0, false, function Rand_Hint)
    set t = null
endfunction
