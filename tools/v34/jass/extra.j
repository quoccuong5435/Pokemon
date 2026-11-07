// ---------------------------------------------------------------------------------------------
// v3.4 extras (docs/v3.4/3-item-league-tinh-nang.md): battle items, weather, Shiny, legend Mega.
// Ab_HT on a hero: 120..122 Str/Agi/Int bonus applied (Shiny 10%, Champion 15%), 123 Shiny, 124 Shiny decided,
// 125 legend Mega, 126 Focus Sash ready time, 127 last XP (Lucky Egg), 128 Champion Aura until, 129 aura effect,
// 140 + k holds item k (Itm_Id[k]; Itm_Refresh every second and on pickup). Mega_HT on an item type: 91 = k + 1.
// ---------------------------------------------------------------------------------------------
function Itm_Flag takes unit u, integer k returns boolean
    return LoadInteger(Ab_HT, GetHandleId(u), 140 + k) == 1
endfunction

function Itm_Refresh takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer k = 0
    local integer s = 0
    local item it = null
    loop
        exitwhen k >= Itm_N
        call SaveInteger(Ab_HT, h, 140 + k, 0)
        set k = k + 1
    endloop
    loop
        exitwhen s >= 6
        set it = UnitItemInSlot(u, s)
        if it != null then
            set k = LoadInteger(Mega_HT, GetItemTypeId(it), 91) - 1
            if k >= 0 then
                call SaveInteger(Ab_HT, h, 140 + k, 1)
            endif
        endif
        set s = s + 1
    endloop
    set it = null
endfunction

// removes one item of type id from u (berries)
function Itm_Use takes unit u, integer id returns nothing
    local integer s = 0
    loop
        exitwhen s >= 6
        if GetItemTypeId(UnitItemInSlot(u, s)) == id then
            call RemoveItem(UnitItemInSlot(u, s))
            call SaveInteger(Ab_HT, GetHandleId(u), 140 + LoadInteger(Mega_HT, id, 91) - 1, 0)
            return
        endif
        set s = s + 1
    endloop
endfunction

// ---- Shiny: 1/100 when a Pokemon is picked, bought, randomed or made by a Soul (1/20 for a Champion);
// evolutions and Mega keep it (Mega_SafeReplace copies keys 123 / 124)
function Shiny_Tint takes unit u returns nothing
    local integer id = GetUnitTypeId(u)
    call SetUnitVertexColor(u, 110 + ModuloInteger(id, 146), 110 + ModuloInteger(id / 7, 146), 110 + ModuloInteger(id / 13, 146), 255)
endfunction

function Shiny_Decide takes unit u returns nothing
    local integer h = GetHandleId(u)
    local player p = GetOwningPlayer(u)
    local integer chance = Shiny_Chance
    if HaveSavedInteger(Ab_HT, h, 124) then
        if LoadInteger(Ab_HT, h, 123) == 1 then
            call Shiny_Tint(u)
        endif
        set p = null
        return
    endif
    call SaveInteger(Ab_HT, h, 124, 1)
    if GetPlayerId(p) < 12 and League_Champ[GetPlayerId(p)] then
        set chance = Shiny_ChanceChamp
    endif
    if GetPlayerId(p) < 12 and GetRandomInt(1, chance) == 1 then
        call SaveInteger(Ab_HT, h, 123, 1)
        call Shiny_Tint(u)
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\HolyBolt\\HolyBoltSpecialArt.mdl", u, "origin"))
        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffffff00* " + GetPlayerName(p) + " got a SHINY " + GetHeroProperName(u) + "! (+10% STR / AGI / INT) *|r")
    endif
    set p = null
endfunction

// ---- weather, every 5 minutes: 0 clear, 1 rain, 2 sun, 3 sandstorm, 4 hail
function Wth_Set takes integer w returns nothing
    local string s = "|cffaaddffThe weather clears up.|r"
    if Wth_Fx != null then
        call RemoveWeatherEffect(Wth_Fx)
        set Wth_Fx = null
    endif
    set Wth_Cur = w
    if w == 1 then
        set Wth_Fx = AddWeatherEffect(bj_mapInitialPlayableArea, 'RAhr')
        set s = "|cff66aaffIt started to rain!|r Water moves +30%, Fire moves -30%, Swift Swim is faster."
    elseif w == 2 then
        set Wth_Fx = AddWeatherEffect(bj_mapInitialPlayableArea, 'LRaa')
        set s = "|cffffcc33The sunlight turned harsh!|r Fire moves +30%, Water moves -30%, Chlorophyll is faster."
    elseif w == 3 then
        set Wth_Fx = AddWeatherEffect(bj_mapInitialPlayableArea, 'WOcw')
        set s = "|cffd2b48cA sandstorm kicked up!|r Pokemon that are not Rock / Ground / Steel lose HP; Sand Veil dodges more."
    elseif w == 4 then
        set Wth_Fx = AddWeatherEffect(bj_mapInitialPlayableArea, 'SNbs')
        set s = "|cffccffffIt started to hail!|r Pokemon that are not Ice lose HP; Snow Cloak dodges more."
    endif
    if Wth_Fx != null then
        call EnableWeatherEffect(Wth_Fx, true)
    endif
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, s)
endfunction

function Wth_Tick takes nothing returns nothing
    local integer w = GetRandomInt(0, 4)
    if w == Wth_Cur then
        set w = ModuloInteger(w + 1, 5)
    endif
    call Wth_Set(w)
endfunction

// ---- damage dealt / taken from weather, held items, Champion Aura and legend Mega (Ab_OnDamaging)
function Ext_DamageMult takes unit src, unit t, boolean atk, boolean skill, integer mt, real eff returns real
    local integer hs = GetHandleId(src)
    local integer ht = GetHandleId(t)
    local real m = 1.0
    if skill and mt == T_WATER then
        if Wth_Cur == 1 then
            set m = m * 1.3
        elseif Wth_Cur == 2 then
            set m = m * 0.7
        endif
    elseif skill and mt == T_FIRE then
        if Wth_Cur == 2 then
            set m = m * 1.3
        elseif Wth_Cur == 1 then
            set m = m * 0.7
        endif
    endif
    if IsUnitType(src, UNIT_TYPE_HERO) then
        if (atk or skill) and Itm_Flag(src, 0) then
            set m = m * 1.3
        endif
        if atk and Itm_Flag(src, 1) then
            set m = m * 1.35
        endif
        if skill and Itm_Flag(src, 2) then
            set m = m * 1.35
        endif
        if eff >= 1.99 and Itm_Flag(src, 6) then
            set m = m * 1.25
        endif
        if atk and Itm_Flag(src, 9) and GetRandomReal(0.0, 1.0) < 0.15 then
            set m = m * 1.5
            call Ab_Say(t, "Crit!", 255, 60, 60, GetOwningPlayer(src), GetOwningPlayer(t))
        endif
    endif
    if IsUnitType(t, UNIT_TYPE_HERO) then
        if skill and Itm_Flag(t, 8) then
            set m = m * 0.75
        endif
        if Itm_Flag(t, 11) and LoadInteger(Ab_HT, GetUnitTypeId(t), 299) > 0 then
            set m = m * 0.8
        endif
    endif
    if Mega_Time < LoadReal(Ab_HT, hs, 128) then
        set m = m * 1.1
    endif
    if Mega_Time < LoadReal(Ab_HT, ht, 128) then
        set m = m * 0.9
    endif
    if LoadInteger(Ab_HT, hs, 125) == 1 then
        set m = m * 1.3
    endif
    return m
endfunction

// ---- Mewtwo and Rayquaza (the legends at fixed places) Mega Evolve once at 50% HP: heal 20%, +30% damage
function Leg_TryMega takes unit t, real d returns nothing
    local integer id = GetUnitTypeId(t)
    local integer mi = -1
    local real mx = I2R(BlzGetUnitMaxHP(t))
    if LoadInteger(Ab_HT, GetHandleId(t), 125) == 1 or GetWidgetLife(t) - d > 0.5 * mx then
        return
    endif
    if id == Leg_MewtwoId then
        set mi = Leg_MegaMewtwo + GetRandomInt(0, 1)
    elseif id == Leg_RayquazaId then
        set mi = Leg_MegaRayquaza
    endif
    if mi < 0 or mi >= Mega_N then
        return
    endif
    call SaveInteger(Ab_HT, GetHandleId(t), 125, 1)
    call BlzSetUnitSkin(t, Mega_Skin[mi])
    call SetUnitScale(t, BlzGetUnitRealField(t, UNIT_RF_SCALING_VALUE) * 1.25, BlzGetUnitRealField(t, UNIT_RF_SCALING_VALUE) * 1.25, BlzGetUnitRealField(t, UNIT_RF_SCALING_VALUE) * 1.25)
    call SetUnitVertexColor(t, Mega_R[mi], Mega_G[mi], Mega_B[mi], 255)
    if Mega_Fx[mi] != "" then
        call AddSpecialEffectTarget(Mega_Fx[mi], t, "origin")
    endif
    call BlzSetUnitName(t, Mega_Name[mi])
    call SetWidgetLife(t, GetWidgetLife(t) + 0.2 * mx)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl", t, "origin"))
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff66ccThe wild legend Mega Evolved into " + Mega_Name[mi] + "!|r")
endfunction
