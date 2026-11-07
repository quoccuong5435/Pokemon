// ---------------------------------------------------------------------------------------------
// v3.4 extras that need the Ability helpers (Ab_Deal, Ab_Heal, Ab_FxAdd ...): item effects after a hit, the
// per-second work of the players' heroes (items, weather, Shiny, Champion title), shops, Escape Rope, Amulet Coin
// ---------------------------------------------------------------------------------------------
function Ext_AfterHit takes unit src, unit t, boolean atk, real d returns nothing
    local real mx = 0.0
    if IsUnitType(src, UNIT_TYPE_HERO) then
        set mx = I2R(BlzGetUnitMaxHP(src))
        if Itm_Flag(src, 0) and GetWidgetLife(src) - 0.01 * mx > 0.2 * mx then  // Life Orb
            call SetWidgetLife(src, GetWidgetLife(src) - 0.01 * mx)
        endif
        if atk and Itm_Flag(src, 10) and GetRandomReal(0.0, 1.0) < 0.1 then  // King's Rock
            set Ab_FxCur = src
            call Ab_FxAdd(t, 3, 1.0, 0.0)
            set Ab_FxCur = null
        endif
    endif
    if atk and IsUnitType(t, UNIT_TYPE_HERO) and Itm_Flag(t, 7) and BlzGetUnitWeaponRealField(src, UNIT_WEAPON_RF_ATTACK_RANGE, 0) <= 250.0 then
        call Ab_Deal(t, src, 0.03 * I2R(BlzGetUnitMaxHP(src)))  // Rocky Helmet
    endif
endfunction

// Focus Sash: the final damage d of a hit on t
function Ext_Final takes unit t, real d returns real
    local integer ht = GetHandleId(t)
    if IsUnitType(t, UNIT_TYPE_HERO) and Itm_Flag(t, 5) and d >= GetWidgetLife(t) - 0.405 then
        if GetWidgetLife(t) > 0.5 * I2R(BlzGetUnitMaxHP(t)) and Mega_Time >= LoadReal(Ab_HT, ht, 126) then
            call SaveReal(Ab_HT, ht, 126, Mega_Time + 60.0)
            call Ab_Say(t, "Focus Sash!", 255, 200, 60, GetOwningPlayer(t), GetOwningPlayer(t))
            return GetWidgetLife(t) - 1.0
        endif
    endif
    return d
endfunction

// pct % more Str / Agi / Int (Shiny 10, Champion 15); keys 120..122 hold what was added
function Ext_Bonus takes unit u, integer pct returns nothing
    local integer h = GetHandleId(u)
    local integer strOld = LoadInteger(Ab_HT, h, 120)
    local integer agiOld = LoadInteger(Ab_HT, h, 121)
    local integer intOld = LoadInteger(Ab_HT, h, 122)
    local integer strNew = (GetHeroStr(u, false) - strOld) * pct / 100
    local integer agiNew = (GetHeroAgi(u, false) - agiOld) * pct / 100
    local integer intNew = (GetHeroInt(u, false) - intOld) * pct / 100
    if strNew != strOld then
        call SetHeroStr(u, GetHeroStr(u, false) - strOld + strNew, true)
        call SaveInteger(Ab_HT, h, 120, strNew)
    endif
    if agiNew != agiOld then
        call SetHeroAgi(u, GetHeroAgi(u, false) - agiOld + agiNew, true)
        call SaveInteger(Ab_HT, h, 121, agiNew)
    endif
    if intNew != intOld then
        call SetHeroInt(u, GetHeroInt(u, false) - intOld + intNew, true)
        call SaveInteger(Ab_HT, h, 122, intNew)
    endif
endfunction

// every second for each hero of the players (Ab_Hero)
function Ext_Pulse takes unit u returns nothing
    local integer h = GetHandleId(u)
    local player p = GetOwningPlayer(u)
    local integer pid = GetPlayerId(p)
    local real mx = I2R(BlzGetUnitMaxHP(u))
    local integer xp = GetHeroXP(u)
    local integer last = LoadInteger(Ab_HT, h, 127)
    local integer pct = 0
    local unit v = null
    call Itm_Refresh(u)
    if Itm_Flag(u, 4) then  // Leftovers
        call Ab_Heal(u, 0.01 * mx)
    endif
    if Itm_Flag(u, 15) and GetWidgetLife(u) < 0.5 * mx then  // Sitrus Berry
        call Ab_Heal(u, 0.25 * mx)
        call Itm_Use(u, Itm_Id[15])
        call Ab_Say(u, "Sitrus Berry", 120, 255, 120, p, p)
    endif
    if Itm_Flag(u, 16) and Ab_HasBad(u) then  // Lum Berry
        call Ab_Cleanse(u)
        call Itm_Use(u, Itm_Id[16])
        call Ab_Say(u, "Lum Berry", 120, 255, 120, p, p)
    endif
    if Itm_Flag(u, 12) and last > 0 and xp > last and not IsSuspendedXP(u) then  // Lucky Egg
        call AddHeroXP(u, (xp - last) / 2, true)
    endif
    call SaveInteger(Ab_HT, h, 127, GetHeroXP(u))
    // sandstorm / hail: 1% max HP every 2 seconds (not below 10%)
    if (Wth_Cur == 3 or Wth_Cur == 4) and ModuloInteger(Ab_Beat / 2, 2) == 0 and GetWidgetLife(u) > 0.1 * mx + 0.01 * mx then
        if (Wth_Cur == 3 and not Ty_Has(u, T_ROCK) and not Ty_Has(u, T_GROUND) and not Ty_Has(u, T_STEEL)) or (Wth_Cur == 4 and not Ty_Has(u, T_ICE)) then
            call SetWidgetLife(u, GetWidgetLife(u) - 0.01 * mx)
        endif
    endif
    if LoadInteger(Ab_HT, h, 123) == 1 then
        call Shiny_Tint(u)
        if ModuloInteger(Ab_Beat / 2, 5) == 0 then
            call Ab_Pop(u, "Abilities\\Spells\\Items\\AIam\\AIamTarget.mdl", "overhead")
        endif
        set pct = pct + 10
    endif
    if pid < 12 and League_Champ[pid] then
        set pct = pct + 15
        if not HaveSavedHandle(Ab_HT, h, 129) then
            call SaveEffectHandle(Ab_HT, h, 129, AddSpecialEffectTarget("Abilities\\Spells\\Human\\DevotionAura\\DevotionAura.mdl", u, "origin"))
        endif
        // Champion Aura: allied Pokemon within 800 (and itself) deal 10% more and take 10% less damage
        call GroupEnumUnitsInRange(Ext_G, GetUnitX(u), GetUnitY(u), 800.0, null)
        loop
            set v = FirstOfGroup(Ext_G)
            exitwhen v == null
            call GroupRemoveUnit(Ext_G, v)
            if IsUnitType(v, UNIT_TYPE_HERO) and GetWidgetLife(v) > 0.405 and IsUnitAlly(v, p) then
                call SaveReal(Ab_HT, GetHandleId(v), 128, Mega_Time + 1.5)
            endif
        endloop
    endif
    call Ext_Bonus(u, pct)
    set p = null
endfunction

function Ext_OnPickup takes nothing returns boolean
    if IsUnitType(GetTriggerUnit(), UNIT_TYPE_HERO) then
        call Itm_Refresh(GetTriggerUnit())
    endif
    return false
endfunction

// Amulet Coin: +50% of the bounty of what its holder kills
function Ext_OnKill takes nothing returns boolean
    local unit k = GetKillingUnit()
    local unit d = GetTriggerUnit()
    local integer gold = 0
    if k != null and IsUnitType(k, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(k)) < 12 and Itm_Flag(k, 13) and IsUnitEnemy(d, GetOwningPlayer(k)) then
        set gold = BlzGetUnitIntegerField(d, UNIT_IF_GOLD_BOUNTY_AWARDED_BASE) / 2
        if gold > 0 then
            call AdjustPlayerStateBJ(gold, GetOwningPlayer(k), PLAYER_STATE_RESOURCE_GOLD)
            call Ab_Say(k, "+" + I2S(gold) + " gold", 255, 220, 0, GetOwningPlayer(k), GetOwningPlayer(k))
        endif
    endif
    set k = null
    set d = null
    return false
endfunction

// Escape Rope (a trigger action: it waits 3 seconds)
function Ext_OnUseItem takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local player p = GetOwningPlayer(u)
    local integer pid = GetPlayerId(p)
    local real x = 0.0
    local real y = 0.0
    if GetItemTypeId(GetManipulatedItem()) == Itm_Rope and pid < 12 then
        if Gym_Busy(pid) then
            call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffff4040No Escape Rope during a gym or League battle.|r")
            call UnitAddItemById(u, Itm_Rope)
        else
            call DisplayTimedTextToPlayer(p, 0, 0, 3.0, "|cffffcc00Escape Rope: back to base in 3 seconds...|r")
            call TriggerSleepAction(3.0)
            if GetWidgetLife(u) > 0.405 and not Gym_Busy(pid) then
                set x = GetStartLocationX(GetPlayerStartLocation(p))
                set y = GetStartLocationY(GetPlayerStartLocation(p))
                call SetUnitPosition(u, x, y)
                call PanCameraToTimedForPlayer(p, x, y, 0.3)
                call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", x, y))
            endif
        endif
    endif
    set u = null
    set p = null
endfunction

// Battle Shop and Item Shop next to the Mega Shops of both bases: the first free walkable spots of a list
function Ext_ShopSpot takes real x, real y returns boolean
    local unit v = null
    local boolean ok = not IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY)
    if ok then
        call GroupEnumUnitsInRange(Ext_G, x, y, 170.0, null)
        set v = FirstOfGroup(Ext_G)
        set ok = v == null
        call GroupClear(Ext_G)
    endif
    set v = null
    return ok
endfunction

function Ext_PlaceShops takes nothing returns nothing
    local integer side = 0
    local integer k = 0
    local integer c = 0
    local real sx = 0.0
    local real x = 0.0
    local real y = 0.0
    loop
        exitwhen side >= 2
        set sx = -1.0
        if side == 1 then
            set sx = 1.0
        endif
        set k = 0
        set c = 0
        loop
            exitwhen k >= 2 or c >= Ext_SpotN
            set x = sx * Ext_SpotX[c]
            set y = Ext_SpotY[c]
            if Ext_ShopSpot(x, y) then
                call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), Ext_Shop[k], x, y, 90.0)
                set k = k + 1
            endif
            set c = c + 1
        endloop
        set side = side + 1
    endloop
endfunction
