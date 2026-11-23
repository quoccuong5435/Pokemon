// ===== v4.2x Ability rework (tools/v412/ability_rw.py), early part: only globals and natives =====
// RW_HT unit handle keys: 10 attack-slow amount / 11 end, 12 damage-down amount / 13 end, 14 miss chance / 15 end,
// 17 heal cut end, 21 Frisk mark end / 22 marker player id + 1, 23 wet end, 24 scorch end / 25 scorch source,
// 26 chill stacks / 27 end, 28 armor-cut stacks / 29 end, 41 attack speed bonus / 42 end, 43 move speed bonus
// (fraction) / 44 end, 45 damage bonus / 46 end, 47 shield HP / 48 end, 49 last target id, 50 last hit time,
// 51 hit count, 52 cooldown A, 53 cooldown B, 54 stacks, 55 stacks end, 56 last cast time, 57 blade end,
// 58 Protean type + 1, 59 Protean end, 60 run start, 61 x, 62 y, 63 damage taken window, 64 window start,
// 66 still since, 67 x, 68 y, 69 copy target id, 70 copy time, 75 pathing end, 76 Guts active end,
// 77 no-slow end (Quick Feet), 78 lethal save ready, 79 low-HP gate (Rattled / Unburden / Anger Point)

// Ability of a unit right now (Ab_Num without the Trace copy; usable before Ab_Num is declared)
function RW_Ab takes unit u returns integer
    local integer rwHandle = 0
    if u == null then
        return 0
    endif
    set rwHandle = GetHandleId(u)
    if Mega_Time < LoadReal(Ab_HT, rwHandle, 77) then
        return 0
    endif
    return LoadInteger(Ab_HT, rwHandle, 0)
endfunction

function RW_TimedOn takes unit u, integer endKey returns boolean
    return u != null and Mega_Time < LoadReal(RW_HT, GetHandleId(u), endKey)
endfunction

// healing received (Damp, Unnerve, Drought)
function RW_HealMult takes unit u returns real
    if RW_TimedOn(u, 17) then
        return 0.70
    endif
    return 1.0
endfunction

// Ab_FxAdd: multiplier of the duration of a timed effect of `kind` on u (0 = blocked)
function RW_FxDurMult takes unit u, integer kind returns real
    local integer rwAbility = RW_Ab(u)
    if kind == 2 then
        if rwAbility == AB_RW_LIMBER or RW_TimedOn(u, 77) or (rwAbility == AB_RW_GUTS and RW_TimedOn(u, 76)) then
            return 0.0
        endif
        if rwAbility == AB_RW_THICKFAT and RW_DmgType == T_ICE then
            return 0.0
        endif
    elseif kind == 3 then
        if rwAbility == AB_RW_SUCTIONCUPS or rwAbility == AB_RW_EARLYBIRD then
            return 0.5
        endif
    elseif kind == 5 then
        if rwAbility == AB_RW_BIGPECKS then
            return 0.0
        endif
    endif
    return 1.0
endfunction

function RW_Timed takes unit u, integer amountKey, integer endKey returns real
    if RW_TimedOn(u, endKey) then
        return LoadReal(RW_HT, GetHandleId(u), amountKey)
    endif
    return 0.0
endfunction

// flat move speed bonus (Ab_MoveBonus)
function RW_MSBonus takes unit u returns real
    local integer rwAbility = RW_Ab(u)
    local real rwBase = GetUnitDefaultMoveSpeed(u)
    local real rwBonus = RW_Timed(u, 43, 44) * rwBase
    local real rwLife = GetWidgetLife(u) / RMaxBJ(1.0, I2R(BlzGetUnitMaxHP(u)))
    if rwAbility == AB_RW_CHLOROPHYLL then
        set rwBonus = rwBonus + 50.0
    elseif rwAbility == AB_RW_LIGHTMETAL then
        set rwBonus = rwBonus + 60.0
    elseif rwAbility == AB_RW_LIMBER then
        set rwBonus = rwBonus + 20.0
    elseif rwAbility == AB_RW_RUNAWAY then
        set rwBonus = rwBonus + 30.0
    elseif rwAbility == AB_RW_VITALSPIRIT and rwLife < 0.5 then
        set rwBonus = rwBonus + 0.2 * rwBase
    elseif rwAbility == AB_RW_SPEEDBOOST and RW_TimedOn(u, 55) then
        set rwBonus = rwBonus + 0.06 * I2R(LoadInteger(RW_HT, GetHandleId(u), 54)) * rwBase
    endif
    return rwBonus
endfunction

// attack speed bonus as a fraction (Fx_StatSync)
function RW_ASBonus takes unit u returns real
    local integer rwAbility = RW_Ab(u)
    local real rwBonus = RW_Timed(u, 41, 42)
    if rwAbility == AB_RW_CHLOROPHYLL then
        set rwBonus = rwBonus + 0.25
        if Wth_Cur == 2 then
            set rwBonus = rwBonus + 0.40
        endif
    elseif rwAbility == AB_RW_VITALSPIRIT then
        set rwBonus = rwBonus + 0.15
    elseif rwAbility == AB_RW_LIGHTMETAL then
        set rwBonus = rwBonus + 0.20
    elseif rwAbility == AB_RW_MOTORDRIVE then
        set rwBonus = rwBonus + 0.15
    elseif rwAbility == AB_RW_GUTS and RW_TimedOn(u, 76) then
        set rwBonus = rwBonus + 0.20
    elseif rwAbility == AB_RW_SPEEDBOOST and RW_TimedOn(u, 55) then
        set rwBonus = rwBonus + 0.06 * I2R(LoadInteger(RW_HT, GetHandleId(u), 54))
    endif
    return rwBonus
endfunction

// armor bonus of its own Ability (Fx_StatSync)
function RW_ArmorBonus takes unit u returns integer
    local integer rwAbility = RW_Ab(u)
    local integer rwHandle = GetHandleId(u)
    if rwAbility == AB_RW_SHELLARMOR or rwAbility == AB_RW_BATTLEARMOR or rwAbility == AB_RW_BIGPECKS then
        return 5
    elseif rwAbility == AB_RW_ICEBODY then
        return 15
    elseif rwAbility == AB_RW_SUCTIONCUPS and LoadReal(RW_HT, rwHandle, 66) > 0.0 and Mega_Time - LoadReal(RW_HT, rwHandle, 66) >= 1.0 then
        return 25
    elseif rwAbility == AB_RW_MARVELSCALE and RW_TimedOn(u, 55) then
        return 6 * LoadInteger(RW_HT, rwHandle, 54)
    elseif rwAbility == AB_RW_STANCECHANGE and RW_TimedOn(u, 57) then
        return -5
    endif
    return 0
endfunction
// ===== end of the early part =====
