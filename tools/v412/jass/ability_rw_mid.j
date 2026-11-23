// ===== v4.2x Ability rework, middle part (before Fx_StageImmune): checks called by the status / stage code =====

// enemy stat drops that do not land
function RW_StageImmune takes unit u, integer s returns boolean
    local integer rwAbility = RW_Ab(u)
    if rwAbility == AB_RW_CLEARBODY then
        return true
    elseif s == 2 and rwAbility == AB_RW_BIGPECKS then
        return true
    elseif s == 1 and (rwAbility == AB_RW_SCRAPPY or rwAbility == AB_RW_HYPERCUTTER) then
        return true
    endif
    return false
endfunction

// Quick Feet: a hard CC or a status gives a dash and ends slows (every 8s)
function RW_QuickFeet takes unit u returns nothing
    local integer rwHandle = GetHandleId(u)
    local integer rwSlot = 0
    if RW_Ab(u) != AB_RW_QUICKFEET or Mega_Time < LoadReal(RW_HT, rwHandle, 52) then
        return
    endif
    call SaveReal(RW_HT, rwHandle, 52, Mega_Time + 8.0)
    call SaveReal(RW_HT, rwHandle, 43, 0.8)
    call SaveReal(RW_HT, rwHandle, 44, Mega_Time + 2.0)
    call SaveReal(RW_HT, rwHandle, 77, Mega_Time + 2.0)
    set rwSlot = Ab_FxFind(u, 2)
    if rwSlot >= 0 then
        call Ab_FxStop(rwSlot)
    endif
    call Fx_Say(u, "Quick Feet!", 120, 220, 255, null)
endfunction

// Fx_HardCC: new duration of a hard CC on t (0 = blocked)
function RW_HardCC takes unit t, real dur, unit src returns real
    local integer rwAbility = RW_Ab(t)
    local integer rwHandle = GetHandleId(t)
    if rwAbility == AB_RW_OBLIVIOUS and Mega_Time >= LoadReal(RW_HT, rwHandle, 52) then
        call SaveReal(RW_HT, rwHandle, 52, Mega_Time + 12.0)
        call Ab_Heal(t, 0.05 * I2R(BlzGetUnitMaxHP(t)))
        call Fx_Say(t, "Oblivious", 200, 200, 255, src)
        return 0.0
    endif
    if rwAbility == AB_RW_SUCTIONCUPS or rwAbility == AB_RW_EARLYBIRD then
        set dur = dur * 0.5
    endif
    call RW_QuickFeet(t)
    return dur
endfunction

// powder moves (Overcoat): the move key the source used last
function RW_IsPowder takes unit src returns boolean
    local integer rwKey = 0
    local integer rwMove = 0
    local string rwLabel = ""
    if src == null then
        return false
    endif
    set rwKey = LoadInteger(Fx_HT, GetHandleId(src), 30)
    if rwKey < 100000 or rwKey >= 100000 + Mv_N then
        return false
    endif
    set rwMove = rwKey - 100000
    set rwLabel = Mv_Label[rwMove]
    return SubString(rwLabel, 0, 5) == "Spore" or SubString(rwLabel, 0, 12) == "Sleep Powder" or SubString(rwLabel, 0, 10) == "Stun Spore" or SubString(rwLabel, 0, 14) == "Poison Powder " or SubString(rwLabel, 0, 12) == "Cotton Spore" or SubString(rwLabel, 0, 11) == "Rage Powder"
endfunction

// Fx_Status: statuses that do not land on t
function RW_StatusBlock takes unit t, integer kind, unit src returns boolean
    local integer rwAbility = RW_Ab(t)
    if kind == 5 and (rwAbility == AB_RW_VITALSPIRIT or rwAbility == AB_RW_INSOMNIA) then
        return true
    endif
    if kind == 4 and rwAbility == AB_RW_LIMBER then
        return true
    endif
    if rwAbility == AB_RW_SHIELDDUST and RW_TimedOn(t, 48) and LoadReal(RW_HT, GetHandleId(t), 47) > 0.0 and src != null and src != t then
        return true
    endif
    if rwAbility == AB_RW_OVERCOAT and RW_IsPowder(src) then
        call Fx_Say(t, "Overcoat", 200, 200, 200, src)
        return true
    endif
    return false
endfunction

// Fx_Status: duration multiplier (Serene Grace source +50%, Early Bird sleep / Suction Cups freeze halved)
function RW_StatusDur takes unit t, integer kind, unit src returns real
    local real rwMult = 1.0
    if src != null and RW_Ab(src) == AB_RW_SERENEGRACE then
        set rwMult = 1.5
    endif
    if (kind == 5 or kind == 6) and (RW_Ab(t) == AB_RW_EARLYBIRD or RW_Ab(t) == AB_RW_SUCTIONCUPS) then
        set rwMult = rwMult * 0.5
    endif
    return rwMult
endfunction

function RW_ConfuseBlock takes unit t returns boolean
    local integer rwAbility = RW_Ab(t)
    return rwAbility == AB_RW_OWNTEMPO or rwAbility == AB_RW_INSOMNIA
endfunction

// Fx_AfterHit: the extra effects of the move do not apply (Sheer Force user, Shield Dust target behind its shield)
function RW_NoSideFx takes unit src, unit t returns boolean
    if RW_Ab(src) == AB_RW_SHEERFORCE then
        return true
    endif
    return RW_Ab(t) == AB_RW_SHIELDDUST and RW_TimedOn(t, 48) and LoadReal(RW_HT, GetHandleId(t), 47) > 0.0
endfunction

function RW_NoPush takes unit u returns boolean
    local integer rwAbility = RW_Ab(u)
    return rwAbility == AB_RW_LIGHTMETAL or rwAbility == AB_RW_SUCTIONCUPS
endfunction

// Intimidate does not lower the Attack of these
function RW_NoIntimidate takes unit u returns boolean
    local integer rwAbility = RW_Ab(u)
    return rwAbility == AB_RW_INNERFOCUS or rwAbility == AB_RW_SCRAPPY or rwAbility == AB_RW_UNAWARE or rwAbility == AB_RW_OWNTEMPO or rwAbility == AB_RW_OBLIVIOUS
endfunction
// ===== end of the middle part =====
