// ===== item_fix (tools/v412/item_fix.py): Shell Bell lifesteal, lifesteal numbers, Gym 8 armor break =====
// Shell Bell (I01P): the WC3 Life Steal ability on the item healed from the raw attack before the map's damage
// formula (and an orb conflicts with other orbs), so it healed almost nothing. It is now 10% of the final damage
// (skills half), added to the Lifesteal charms in PAX_Loot_OnHitEx. A green "+N" shows the heal (at most 1 per s).
// Gym 8 badge (I01B): hits lower the target's armor by 20% for 3s (shown "-N armor", refreshed by each hit);
// before, a hidden damage multiplier did it and the armor never looked lower.
function IF_BellPct takes unit src returns integer
    if Itm_Has(src, 'I01P') then
        return IF_BellLS
    endif
    return 0
endfunction

function IF_ShowHeal takes unit src, real amount returns nothing
    local integer h = GetHandleId(src)
    if amount >= 1.0 and Mega_Time >= LoadReal(IF_HT, h, 0) then
        call SaveReal(IF_HT, h, 0, Mega_Time + 1.0)
        call PAX_FloatText(src, "+" + I2S(R2I(amount)), 90, 255, 90, GetOwningPlayer(src), GetOwningPlayer(src))
    endif
endfunction

function GA_Shred takes unit src, unit t returns nothing
    local integer h = GetHandleId(t)
    local real cut = 0.0
    if t == null or IsUnitType(t, UNIT_TYPE_STRUCTURE) or GetWidgetLife(t) <= 0.405 then
        return
    endif
    if not HaveSavedReal(GA_HT, h, 0) then
        set cut = BlzGetUnitArmor(t) * GA_Pct
        if cut < 0.5 then
            return
        endif
        call BlzSetUnitArmor(t, BlzGetUnitArmor(t) - cut)
        call SaveReal(GA_HT, h, 0, cut)
        call SaveReal(GA_HT, h, 1, BlzGetUnitArmor(t))
        call GroupAddUnit(GA_G, t)
        call PAX_FloatText(t, "-" + I2S(R2I(cut + 0.5)) + " armor", 255, 150, 60, GetOwningPlayer(src), GetOwningPlayer(t))
    endif
    call SaveReal(GA_HT, h, 2, Mega_Time + GA_Dur)
endfunction

function GA_Check takes nothing returns nothing
    local unit u = GetEnumUnit()
    local integer h = GetHandleId(u)
    if GetUnitTypeId(u) == 0 then
        call FlushChildHashtable(GA_HT, h)
        call GroupRemoveUnit(GA_G, u)
    elseif Mega_Time >= LoadReal(GA_HT, h, 2) then
        // give the armor back, unless something set the armor anew meanwhile (wild rescale): then it is already whole
        if BlzGetUnitArmor(u) < LoadReal(GA_HT, h, 1) + LoadReal(GA_HT, h, 0) - 0.01 then
            call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + LoadReal(GA_HT, h, 0))
        endif
        call FlushChildHashtable(GA_HT, h)
        call GroupRemoveUnit(GA_G, u)
    endif
    set u = null
endfunction

function GA_Tick takes nothing returns nothing
    call ForGroup(GA_G, function GA_Check)
endfunction

