//@replace Ab_Num
// v3.4: the Ability that works now: none while an enemy Air Lock is near (key 77), the copied one for Trace (key 76)
function Ab_Num takes unit u returns integer
    local integer h = GetHandleId(u)
    local integer a = LoadInteger(Ab_HT, h, 0)
    if a == 0 then
        return 0
    endif
    if Mega_Time < LoadReal(Ab_HT, h, 77) then
        return 0
    endif
    if a == AB_TRACE and LoadInteger(Ab_HT, h, 76) > 0 then
        return LoadInteger(Ab_HT, h, 76)
    endif
    return a
endfunction
//@replace Ab_Sync
// model shown on a hero that has an aura Ability (v3.4)
function Ab_AuraModel takes integer a returns string
    if a == AB_FLAMEBODY then
        return "Abilities\\Spells\\NightElf\\Immolation\\ImmolationTarget.mdl"
    elseif a == AB_PRESSURE then
        return "Abilities\\Spells\\Undead\\UnholyAura\\UnholyAura.mdl"
    elseif a == AB_BADDREAMS then
        return "Abilities\\Spells\\Undead\\VampiricAura\\VampiricAura.mdl"
    elseif a == AB_DROUGHT then
        return "Abilities\\Spells\\Human\\Brilliance\\Brilliance.mdl"
    elseif a == AB_SANDSTREAM then
        return "Abilities\\Spells\\Orc\\CommandAura\\CommandAura.mdl"
    elseif a == AB_SHADOWTAG then
        return "Abilities\\Spells\\Human\\DevotionAura\\DevotionAura.mdl"
    elseif a == AB_MAGNETPULL then
        return "Abilities\\Spells\\Orc\\EnduranceAura\\EnduranceAura.mdl"
    elseif a == AB_AIRLOCK then
        return "Abilities\\Spells\\NightElf\\TrueshotAura\\TrueshotAura.mdl"
    endif
    return ""
endfunction

// give the hero the info button of its Ability (and the aura model); swap them when the Ability changes.
// v3.4: no item bonus abilities any more (Ab_Strip still removes the old ones)
function Ab_Sync takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer want = Ab_Want(u)
    local integer have = LoadInteger(Ab_HT, h, 0)
    local string fx = ""
    if not HaveSavedInteger(Ab_HT, h, 10) then
        call SaveInteger(Ab_HT, h, 10, 1)
        call SaveReal(Ab_HT, h, 9, Mega_Time)
        call Ab_Strip(u)
        set have = 0
        call Shiny_Decide(u)  // v3.4
    endif
    if want != have then
        if have > 0 then
            call UnitRemoveAbility(u, Ab_InfoId(have))
        endif
        if HaveSavedHandle(Ab_HT, h, 80) then
            call DestroyEffect(LoadEffectHandle(Ab_HT, h, 80))
            call RemoveSavedHandle(Ab_HT, h, 80)
        endif
        if LoadReal(Ab_HT, h, 83) != 0.0 then
            call SetUnitMoveSpeed(u, GetUnitDefaultMoveSpeed(u))
            call SaveReal(Ab_HT, h, 83, 0.0)
        endif
        call SaveInteger(Ab_HT, h, 76, 0)
        call SaveInteger(Ab_HT, h, 62, 0)
        if LoadInteger(Ab_HT, h, 85) == 1 then  // leaves Zen Mode with the Ability
            call SaveInteger(Ab_HT, h, 85, 0)
            call BlzSetUnitSkin(u, GetUnitTypeId(u))
            call SetUnitScale(u, Ab_ZenBase, Ab_ZenBase, Ab_ZenBase)
            call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - Ab_ZenArmor)
        endif
        if want > 0 then
            call UnitAddAbility(u, Ab_InfoId(want))
            set fx = Ab_AuraModel(want)
            if fx != "" then
                call SaveEffectHandle(Ab_HT, h, 80, AddSpecialEffectTarget(fx, u, "origin"))
            endif
        endif
        call SaveInteger(Ab_HT, h, 0, want)
    endif
endfunction
