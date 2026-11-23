// ===== v4.2x Ability rework, main part (before Ab_OnDamaging) =====

function RW_IsFoe takes unit v, player p returns boolean
    return v != null and Ab_Alive(v) and IsUnitEnemy(v, p) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) and GetUnitAbilityLevel(v, 'Aloc') == 0
endfunction

function RW_Set takes unit u, integer amountKey, real amount, integer endKey, real dur returns nothing
    local integer rwHandle = GetHandleId(u)
    if Mega_Time < LoadReal(RW_HT, rwHandle, endKey) and LoadReal(RW_HT, rwHandle, amountKey) > amount then
        return  // a stronger one is running
    endif
    call SaveReal(RW_HT, rwHandle, amountKey, amount)
    call SaveReal(RW_HT, rwHandle, endKey, Mega_Time + dur)
endfunction

function RW_Ready takes unit u, integer cdKey, real cooldown returns boolean
    local integer rwHandle = GetHandleId(u)
    if Mega_Time < LoadReal(RW_HT, rwHandle, cdKey) then
        return false
    endif
    call SaveReal(RW_HT, rwHandle, cdKey, Mega_Time + cooldown)
    return true
endfunction

function RW_MaxHP takes unit u returns real
    return I2R(BlzGetUnitMaxHP(u))
endfunction

function RW_Shield takes unit u, real amount, real dur returns nothing
    call RW_Set(u, 47, amount, 48, dur)
    call Ab_Pop(u, "Abilities\\Spells\\Human\\ManaShield\\ManaShieldCaster.mdl", "origin")
endfunction

function RW_AddMana takes unit u, real fraction returns nothing
    call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MANA) + fraction * GetUnitState(u, UNIT_STATE_MAX_MANA))
endfunction

function RW_MainStat takes unit u returns real
    if not IsUnitType(u, UNIT_TYPE_HERO) then
        return 50.0
    endif
    return RMaxBJ(I2R(GetHeroStr(u, true)), I2R(GetHeroInt(u, true)))
endfunction

function RW_Cleanse takes unit u returns nothing
    local integer rwKind = 1
    local integer rwHandle = GetHandleId(u)
    call Ab_Cleanse(u)
    loop
        exitwhen rwKind > 6
        if Fx_HasKind(u, rwKind) then
            call Fx_CureKind(u, rwKind)
        endif
        set rwKind = rwKind + 1
    endloop
    call SaveReal(Fx_HT, rwHandle, 24, 0.0)  // confusion
    call SaveReal(Fx_HT, rwHandle, 25, 0.0)  // silence
    call SaveReal(Fx_HT, rwHandle, 26, 0.0)  // accuracy down
    call Fx_Show(u)
endfunction

// lower every cooldown of the unit's abilities by sec seconds
function RW_CdReduce takes unit u, real sec returns nothing
    local integer rwIndex = 0
    local ability rwSpell = null
    local integer rwSpellId = 0
    local real rwLeft = 0.0
    loop
        exitwhen rwIndex > 23
        set rwSpell = BlzGetUnitAbilityByIndex(u, rwIndex)
        exitwhen rwSpell == null
        set rwSpellId = BlzGetAbilityId(rwSpell)
        set rwLeft = BlzGetUnitAbilityCooldownRemaining(u, rwSpellId)
        if rwLeft > 0.05 then
            if rwLeft - sec <= 0.05 then
                call BlzEndUnitAbilityCooldown(u, rwSpellId)
            else
                call BlzStartUnitAbilityCooldown(u, rwSpellId, rwLeft - sec)
            endif
        endif
        set rwIndex = rwIndex + 1
    endloop
    set rwSpell = null
endfunction

// lightning that jumps from t to up to `count` other enemies of src within 500
function RW_Chain takes unit src, unit t, real dmg, integer count returns nothing
    local unit rwVictim = null
    local player rwOwner = GetOwningPlayer(src)
    local integer rwHits = 0
    call GroupEnumUnitsInRange(RW_Grp, GetUnitX(t), GetUnitY(t), 500.0, null)
    loop
        set rwVictim = FirstOfGroup(RW_Grp)
        exitwhen rwVictim == null
        call GroupRemoveUnit(RW_Grp, rwVictim)
        if rwHits < count and rwVictim != t and RW_IsFoe(rwVictim, rwOwner) then
            call Ab_Deal(src, rwVictim, dmg)
            call Ab_Pop(rwVictim, "Abilities\\Weapons\\Bolt\\BoltImpact.mdl", "origin")
            set rwHits = rwHits + 1
        endif
    endloop
    set rwVictim = null
    set rwOwner = null
endfunction

// take one raised stat stage from t and give it to src
function RW_StealStage takes unit src, unit t returns boolean
    local integer rwStat = 1
    local integer rwTarget = GetHandleId(t)
    loop
        exitwhen rwStat > 5
        if Fx_StageNow(t, rwStat) > 0 then
            call SaveInteger(Fx_HT, rwTarget, rwStat, LoadInteger(Fx_HT, rwTarget, rwStat) - 1)
            call Fx_StatSync(t)
            call Fx_StageAdd(src, rwStat, 1, 12.0, src)
            call Fx_Say(src, "Stolen!", 255, 220, 120, t)
            return true
        endif
        set rwStat = rwStat + 1
    endloop
    return false
endfunction

function RW_CritImmune takes integer ta returns boolean
    return ta == AB_SHELLARMOR or ta == AB_BATTLEARMOR or ta == AB_RW_SHELLARMOR or ta == AB_RW_BATTLEARMOR
endfunction

// the move just used has an extra effect (status, flinch, stat change, confusion)
function RW_MoveHasSide takes unit src returns boolean
    local integer rwMoveKey = Fx_CurMove(src)
    if rwMoveKey == 0 then
        return false
    endif
    return LoadInteger(Fx_HT, rwMoveKey, 4) > 0 or LoadInteger(Fx_HT, rwMoveKey, 6) > 0 or LoadInteger(Fx_HT, rwMoveKey, 7) > 0 or LoadInteger(Fx_HT, rwMoveKey, 8) > 0 or LoadInteger(Fx_HT, rwMoveKey, 9) > 0
endfunction

function RW_EnemyHeroesNear takes unit u, real radius returns integer
    local unit rwVictim = null
    local player rwOwner = GetOwningPlayer(u)
    local integer rwCount = 0
    call GroupEnumUnitsInRange(RW_Grp, GetUnitX(u), GetUnitY(u), radius, null)
    loop
        set rwVictim = FirstOfGroup(RW_Grp)
        exitwhen rwVictim == null
        call GroupRemoveUnit(RW_Grp, rwVictim)
        if IsUnitType(rwVictim, UNIT_TYPE_HERO) and RW_IsFoe(rwVictim, rwOwner) then
            set rwCount = rwCount + 1
        endif
    endloop
    set rwVictim = null
    set rwOwner = null
    return rwCount
endfunction

// ---- damage dealt by src (Ability a = s_ab; also effects of auras / marks on either side)
function RW_Out takes unit src, unit t, integer a, integer ta, boolean atk, boolean skill, integer mt returns real
    local integer rwSrc = GetHandleId(src)
    local integer rwTgt = GetHandleId(t)
    local real rwMult = 1.0
    local real rwLife = GetWidgetLife(src) / RMaxBJ(1.0, RW_MaxHP(src))
    local real rwDef = 0.0
    local integer rwStat = 2
    local integer rwMarker = 0
    if atk and RW_TimedOn(src, 15) and GetRandomReal(0.0, 1.0) < LoadReal(RW_HT, rwSrc, 14) then
        call Ab_Say(t, "Miss", 210, 210, 210, GetOwningPlayer(src), GetOwningPlayer(t))
        return 0.0  // Sand Stream
    endif
    if RW_TimedOn(src, 13) then
        set rwMult = rwMult * (1.0 - LoadReal(RW_HT, rwSrc, 12))  // Stench
    endif
    if skill and RW_TimedOn(t, 23) and (mt == T_WATER or mt == T_ELECTRIC) then
        set rwMult = rwMult * 1.25  // Drizzle: wet
    endif
    if RW_TimedOn(t, 21) then
        set rwMarker = LoadInteger(RW_HT, rwTgt, 22) - 1
        if rwMarker >= 0 and IsUnitAlly(src, Player(rwMarker)) then
            set rwMult = rwMult * 1.10  // Frisk mark
        endif
    endif
    if a <= 0 then
        return rwMult
    endif
    set rwMult = rwMult * (1.0 + RW_Timed(src, 45, 46))  // Anger Point / Flash Fire
    if atk or (skill and Ty_CurPhys == 1) then
        set rwStat = 2
    else
        set rwStat = 4
    endif
    if a == AB_RW_SHEERFORCE then
        if skill and RW_MoveHasSide(src) then
            set rwMult = rwMult * 1.3
        endif
    elseif a == AB_RW_ANALYTIC then
        if (atk or skill) and LoadInteger(RW_HT, rwSrc, 49) == rwTgt and Mega_Time - LoadReal(RW_HT, rwSrc, 50) <= 2.0 then
            set rwMult = rwMult * 1.25
        endif
    elseif a == AB_RW_HUSTLE then
        if atk then
            if GetRandomInt(1, 100) <= 10 then
                call Ab_Say(t, "Miss", 210, 210, 210, GetOwningPlayer(src), GetOwningPlayer(t))
                return 0.0
            endif
            set rwMult = rwMult * 1.3
        endif
    elseif a == AB_RW_INFILTRATOR then
        if Fx_StageNow(t, rwStat) > 0 then
            set rwMult = rwMult * Fx_StageMult(t, rwStat)
        endif
    elseif a == AB_RW_UNAWARE then
        if atk or skill then
            set rwMult = rwMult * Fx_StageMult(t, rwStat)
        endif
    elseif a == AB_RW_JUSTIFIED then
        if Ty_Has(t, T_DARK) then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_BIGPECKS then
        if atk and Ab_FxFind(t, 5) >= 0 then
            set rwMult = rwMult * 1.2
        endif
    elseif a == AB_RW_GALVANIZE then
        if RW_Converted then
            set rwMult = rwMult * 1.2
        endif
    elseif a == AB_RW_PIXILATE then
        if RW_Converted then
            set rwMult = rwMult * 1.3
        endif
        if Ty_Has(t, T_DRAGON) or Ty_Has(t, T_DARK) then
            set rwMult = rwMult * 1.1
        endif
    elseif a == AB_RW_MAGICGUARD then
        if skill then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_OWNTEMPO then
        if atk and LoadInteger(RW_HT, rwSrc, 49) == rwTgt and Mega_Time - LoadReal(RW_HT, rwSrc, 50) <= 2.0 and LoadInteger(RW_HT, rwSrc, 51) >= 2 then
            set rwMult = rwMult * 1.6
        endif
    elseif a == AB_RW_PLUS then
        if skill then
            set rwMult = rwMult * (1.0 + 0.12 * I2R(LoadInteger(RW_HT, rwSrc, 54)))
        endif
    elseif a == AB_RW_PROTEAN then
        if skill and mt >= 0 and LoadInteger(RW_HT, rwSrc, 58) - 1 == mt and RW_TimedOn(src, 59) then
            set rwMult = rwMult * 1.3
        endif
    elseif a == AB_RW_STORMDRAIN then
        if skill and RW_TimedOn(src, 55) then
            set rwMult = rwMult * (1.0 + 0.08 * I2R(LoadInteger(RW_HT, rwSrc, 54)))
        endif
    elseif a == AB_RW_STANCECHANGE then
        if RW_TimedOn(src, 57) then
            set rwMult = rwMult * 1.35
        endif
    elseif a == AB_RW_IMPOSTER then
        if LoadInteger(RW_HT, rwSrc, 69) == rwTgt and IsUnitType(t, UNIT_TYPE_HERO) then
            set rwMult = rwMult * RMinBJ(1.5, RMaxBJ(0.75, RW_MainStat(t) / RMaxBJ(1.0, RW_MainStat(src))))
            if skill and mt >= 0 and Ty_Has(t, mt) then
                set rwMult = rwMult * 1.2
            endif
        endif
    elseif a == AB_RW_DRYSKIN then
        set rwMult = rwMult * (1.0 + RMinBJ(0.25, 0.3 * (1.0 - rwLife)))
    elseif a == AB_RW_OVERGROW then
        if rwLife < 0.5 then
            set rwMult = rwMult * 1.5
        endif
    elseif a == AB_RW_CHLOROPHYLL then
        if skill and mt == T_GRASS and Wth_Cur == 2 then
            set rwMult = rwMult * 1.2
        endif
    elseif a == AB_RW_FLASHFIRE then
        if skill and mt == T_FIRE then
            set rwMult = rwMult * 1.1
        endif
    elseif a == AB_RW_WATERABSORB then
        if skill and mt == T_WATER then
            set rwMult = rwMult * 1.1
        endif
    elseif a == AB_RW_VOLTABSORB then
        if skill and mt == T_ELECTRIC then
            set rwMult = rwMult * 1.1
        endif
    elseif a == AB_RW_LIGHTNINGROD then
        if skill and mt == T_ELECTRIC then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_GUTS then
        if (atk or (skill and Ty_CurPhys == 1)) and RW_TimedOn(src, 76) then
            set rwMult = rwMult * 1.5
        endif
    elseif a == AB_RW_TECHNICIAN then
        if skill and Ty_CurPow <= 60 then
            set rwMult = rwMult * 1.5
        elseif skill and Ty_CurPow <= 80 then
            set rwMult = rwMult * 1.2
        endif
    elseif a == AB_RW_KEENEYE then
        if atk then
            set rwDef = Fx_DefOf(t, 1)
            set rwMult = rwMult * (100.0 + rwDef) / (100.0 + 0.85 * rwDef)
            if not RW_CritImmune(ta) and GetRandomInt(1, 100) <= 20 then
                set rwMult = rwMult * 2.0
                set RW_LastCrit = true
                call Ab_Say(t, "Crit!", 255, 60, 60, GetOwningPlayer(src), GetOwningPlayer(t))
            endif
        endif
    elseif a == AB_RW_RECKLESS then
        if atk then
            set rwMult = rwMult * 1.15
        elseif skill and LoadInteger(Fx_HT, Fx_CurMove(src), 2) > 0 then
            set rwMult = rwMult * 1.35
        endif
    elseif a == AB_RW_ROCKHEAD then
        if skill and LoadInteger(Fx_HT, Fx_CurMove(src), 2) > 0 then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_COMPETITIVE then
        if skill then
            set rwMult = rwMult * (1.0 + 0.06 * I2R(IMinBJ(5, RW_EnemyHeroesNear(src, 800.0))))
        endif
    elseif a == AB_RW_HYPERCUTTER then
        if atk and RW_TimedOn(t, 29) and LoadInteger(RW_HT, rwTgt, 28) >= 5 then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_SERENEGRACE then
        if skill then
            set rwMult = rwMult * 1.1
        endif
    elseif a == AB_RW_SANDFORCE then
        if skill and (mt == T_ROCK or mt == T_GROUND or mt == T_STEEL) then
            set rwMult = rwMult * 1.3
        endif
        if Wth_Cur == 3 then
            set rwMult = rwMult * 1.15
        endif
    elseif a == AB_RW_SCRAPPY then
        if skill and (mt == T_NORMAL or mt == T_FIGHTING) then
            set rwMult = rwMult * 1.25
        endif
    elseif a == AB_RW_SANDRUSH then
        if atk and LoadInteger(RW_HT, rwSrc, 54) == 1 then
            set rwMult = rwMult * 1.4
        endif
    endif
    return rwMult
endfunction

// ---- after the type chart (eff = effectiveness); ta counts unless the attacker has Mold Breaker
function RW_Eff takes unit src, unit t, integer a, integer ta, boolean atk, boolean skill, integer mt, real eff returns real
    local real rwMult = 1.0
    if a == AB_RW_TINTEDLENS and skill and eff > 0.0 and eff < 0.99 then
        set rwMult = RMinBJ(2.0, 1.0 / eff)
    elseif a == AB_RW_SCRAPPY and skill and (mt == T_NORMAL or mt == T_FIGHTING) and Ty_Has(t, T_GHOST) and eff < 0.99 then
        set rwMult = RMinBJ(4.0, 1.0 / RMaxBJ(0.25, eff))
    endif
    if a == AB_MOLDBREAKER then
        return rwMult
    endif
    if ta == AB_RW_ANTICIPATION and eff > 1.01 then
        set rwMult = rwMult * 0.8
        if RW_Ready(t, 52, 20.0) then
            set rwMult = rwMult * 0.5
            call Fx_Say(t, "Anticipated!", 200, 200, 255, src)
        endif
    elseif ta == AB_RW_WONDERGUARD then
        if skill and eff > 1.01 then
            set rwMult = rwMult * 1.5
        elseif skill then
            set rwMult = rwMult * 0.4
        elseif atk then
            set rwMult = rwMult * 0.6
        endif
    endif
    return rwMult
endfunction

// ---- a move of type mt does no damage to t (heal or boost instead)
function RW_Absorbs takes unit t, integer ta, integer mt, real d returns boolean
    if mt < 0 then
        return false
    endif
    if ta == AB_RW_DRYSKIN and (mt == T_WATER or mt == T_ICE) then
        call Ab_Heal(t, 0.2 * d)
    elseif ta == AB_RW_MOTORDRIVE and mt == T_ELECTRIC then
        call Fx_StageAdd(t, 5, 1, 8.0, t)
    elseif ta == AB_RW_FLASHFIRE and mt == T_FIRE then
        call RW_Set(t, 45, 0.4, 46, 8.0)
        call Ab_Pop(t, "Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl", "origin")
    elseif ta == AB_RW_WATERABSORB and mt == T_WATER then
        call Ab_Heal(t, 0.25 * d)
    elseif ta == AB_RW_VOLTABSORB and mt == T_ELECTRIC then
        call Ab_Heal(t, 0.25 * d)
        call RW_Set(t, 41, 0.3, 42, 5.0)
    elseif ta == AB_RW_LIGHTNINGROD and mt == T_ELECTRIC then
        call Ab_Heal(t, 0.25 * d)
        call Fx_StageAdd(t, 3, 1, 12.0, t)
    else
        return false
    endif
    call Ab_Pop(t, "Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", "origin")
    return true
endfunction

// ---- damage taken by t (its Ability ta; d = damage so far); returns the multiplier
function RW_In takes unit src, unit t, integer ta, integer srcab, boolean atk, boolean skill, integer mt, real d returns real
    local integer rwTgt = GetHandleId(t)
    local real rwMax = RW_MaxHP(t)
    local real rwLife = GetWidgetLife(t)
    local real rwMult = 1.0
    local real rwDodge = 0.0
    local real rwShield = 0.0
    local real rwTaken = 0.0
    local real rwLeft = 0.0
    local player rwA = GetOwningPlayer(src)
    local player rwB = GetOwningPlayer(t)
    if d <= 0.0 then
        return 1.0
    endif
    if atk and srcab != AB_KEENEYE and srcab != AB_NOGUARD and srcab != AB_RW_KEENEYE then
        if ta == AB_RW_LIGHTMETAL then
            set rwDodge = 0.10
        elseif ta == AB_RW_LIMBER or ta == AB_RW_INSOMNIA then
            set rwDodge = 0.20
        elseif ta == AB_RW_SANDVEIL then
            set rwDodge = 0.15
            if Wth_Cur == 3 then
                set rwDodge = 0.35
            endif
        elseif ta == AB_RW_SNOWCLOAK then
            set rwDodge = 0.15
            if Wth_Cur == 4 then
                set rwDodge = 0.35
            endif
        endif
        if rwDodge > 0.0 and GetRandomReal(0.0, 1.0) < rwDodge then
            call Ab_Say(t, "Miss", 210, 210, 210, rwA, rwB)
            set Ab_FxCur = t
            if ta == AB_RW_SANDVEIL then
                call Ab_FxAdd(src, 2, 2.0, 0.2)
            elseif ta == AB_RW_SNOWCLOAK then
                call Ab_FxAdd(src, 2, 2.0, 0.4)
            endif
            set Ab_FxCur = null
            set rwA = null
            set rwB = null
            return 0.0
        endif
        if ta == AB_RW_ICEBODY and RW_Ready(t, 52, 15.0) then
            call Fx_HardCC(src, 1.0, t)
            call Ab_Say(t, "Ice Body!", 140, 200, 255, rwA, rwB)
            set rwA = null
            set rwB = null
            return 0.0
        endif
    endif
    if skill then
        if ta == AB_RW_TELEPATHY and GetRandomInt(1, 100) <= 20 then
            call Ab_Say(t, "Foreseen", 200, 160, 255, rwA, rwB)
            set rwA = null
            set rwB = null
            return 0.0
        elseif ta == AB_RW_BULLETPROOF and RW_Ready(t, 52, 10.0) then
            call Ab_Deal(t, src, 0.5 * d)
            call Ab_Say(t, "Blocked!", 200, 200, 200, rwA, rwB)
            set rwA = null
            set rwB = null
            return 0.0
        elseif ta == AB_RW_STANCECHANGE and not RW_TimedOn(t, 57) and Mega_Time - LoadReal(RW_HT, rwTgt, 56) >= 3.0 and RW_Ready(t, 53, 15.0) then
            call Ab_Say(t, "King's Shield!", 255, 220, 120, rwA, rwB)
            set rwA = null
            set rwB = null
            return 0.0
        endif
    endif
    if ta == AB_RW_INNERFOCUS then
        if skill then
            set rwMult = 0.85
        endif
    elseif ta == AB_RW_INTIMIDATE then
        if IsUnitType(src, UNIT_TYPE_HERO) then
            set rwMult = 0.85
        endif
    elseif ta == AB_RW_SHELLARMOR then
        if atk then
            set rwMult = 0.7
        endif
    elseif ta == AB_RW_BATTLEARMOR then
        if atk then
            set rwMult = RMaxBJ(0.0, d - 3.0 * I2R(GetUnitLevel(t))) / d
        endif
    elseif ta == AB_RW_CLEARBODY then
        if skill then
            set rwMult = 0.8
        endif
    elseif ta == AB_RW_ROCKHEAD then
        set rwMult = 0.85
    elseif ta == AB_RW_THICKFAT then
        if skill and (mt == T_FIRE or mt == T_ICE) then
            set rwMult = 0.5
        endif
    elseif ta == AB_RW_OVERCOAT then
        if skill and Ty_CurPhys == 2 then
            set rwMult = 0.85
        endif
    elseif ta == AB_RW_MARVELSCALE then
        if skill and RW_TimedOn(t, 55) then
            set rwMult = 1.0 - 0.04 * I2R(LoadInteger(RW_HT, rwTgt, 54))
        endif
    elseif ta == AB_RW_STANCECHANGE then
        if RW_TimedOn(t, 57) then
            set rwMult = 1.15
        elseif Mega_Time - LoadReal(RW_HT, rwTgt, 56) >= 3.0 then
            set rwMult = 0.7
        endif
    elseif ta == AB_RW_SUCTIONCUPS then
        if LoadReal(RW_HT, rwTgt, 66) > 0.0 and Mega_Time - LoadReal(RW_HT, rwTgt, 66) >= 1.0 then
            set rwMult = 0.8
        endif
    elseif ta == AB_RW_STURDY then
        if rwLife >= 0.9 * rwMax then
            set rwMult = 0.8
        endif
    elseif ta == AB_RW_SYNCHRONIZE then
        if skill and IsUnitEnemy(src, rwB) then
            call Ab_Deal(t, src, 0.4 * d)
            set Ab_FxCur = t
            call Ab_FxAdd(src, 2, 3.0, 0.4)
            set Ab_FxCur = null
        endif
    elseif ta == AB_RW_UNAWARE then
        if atk or (skill and Ty_CurPhys == 1) then
            set rwMult = 1.0 / Fx_StageMult(src, 1)
        elseif skill then
            set rwMult = 1.0 / Fx_StageMult(src, 3)
        endif
    endif
    // shields (Hydration, Friend Guard, Shield Dust)
    set rwTaken = d * rwMult
    if RW_TimedOn(t, 48) then
        set rwShield = LoadReal(RW_HT, rwTgt, 47)
        if rwShield > 0.0 and rwTaken > 0.0 then
            set rwLeft = RMaxBJ(0.0, rwShield - rwTaken)
            set rwTaken = RMaxBJ(0.0, rwTaken - rwShield)
            call SaveReal(RW_HT, rwTgt, 47, rwLeft)
            set rwMult = rwTaken / d
        endif
    endif
    // a lethal hit: Sturdy (20% HP, 2s invulnerable, every 45s) / Sand Force (15% HP, 1.5s, every 60s)
    if rwTaken >= rwLife then
        if ta == AB_RW_STURDY and RW_Ready(t, 52, 45.0) then
            set rwMult = RMaxBJ(0.0, rwLife - 0.2 * rwMax) / d
            call Ab_FxAdd(t, 7, 2.0, 0.0)
            call Ab_Say(t, "Sturdy!", 255, 220, 120, rwA, rwB)
        elseif ta == AB_RW_SANDFORCE and RW_Ready(t, 53, 60.0) then
            set rwMult = RMaxBJ(0.0, rwLife - 0.15 * rwMax) / d
            call Ab_FxAdd(t, 7, 1.5, 0.0)
            call Ab_Say(t, "Sturdy!", 255, 220, 120, rwA, rwB)
        endif
    endif
    set rwA = null
    set rwB = null
    return rwMult
endfunction

// ---- after a hit landed (d = damage dealt)
function RW_After takes unit src, unit t, integer a, integer ta, boolean atk, boolean skill, integer mt, real d, real eff returns nothing
    local integer rwSrc = GetHandleId(src)
    local integer rwTgt = GetHandleId(t)
    local integer rwCount = 1
    local integer rwKind = 0
    local real rwLife = GetWidgetLife(src) / RMaxBJ(1.0, RW_MaxHP(src))
    local real rwTLife = GetWidgetLife(t) / RMaxBJ(1.0, RW_MaxHP(t))
    local player rwPa = GetOwningPlayer(src)
    local player rwPb = GetOwningPlayer(t)
    local boolean rwMelee = atk and IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER)
    local boolean rwHero = IsUnitType(t, UNIT_TYPE_HERO)
    local integer rwGold = 0
    if not (atk or skill) then
        set rwPa = null
        set rwPb = null
        return
    endif
    // consecutive hits on one target (Analytic, Own Tempo)
    if LoadInteger(RW_HT, rwSrc, 49) == rwTgt and Mega_Time - LoadReal(RW_HT, rwSrc, 50) <= 2.0 then
        set rwCount = LoadInteger(RW_HT, rwSrc, 51) + 1
    endif
    call SaveInteger(RW_HT, rwSrc, 49, rwTgt)
    call SaveReal(RW_HT, rwSrc, 50, Mega_Time)
    call SaveInteger(RW_HT, rwSrc, 51, rwCount)
    // ---- the attacker's Ability
    if a == AB_RW_OWNTEMPO then
        if atk and rwCount >= 3 then
            call RW_CdReduce(src, 1.0)
            call SaveInteger(RW_HT, rwSrc, 51, 0)
        endif
    elseif a == AB_RW_PLUS then
        if atk then
            call SaveInteger(RW_HT, rwSrc, 54, IMinBJ(5, LoadInteger(RW_HT, rwSrc, 54) + 1))
        elseif skill then
            call SaveInteger(RW_HT, rwSrc, 54, 0)
        endif
    elseif a == AB_RW_MINUS then
        if skill then
            call RW_AddMana(src, 0.03)
            call RW_CdReduce(src, 1.0)
        endif
    elseif a == AB_RW_RAINDISH then
        if skill and mt == T_WATER then
            call Ab_Heal(src, 0.05 * RW_MaxHP(src))
        endif
    elseif a == AB_RW_GLUTTONY then
        if atk and rwLife < 0.3 then
            call Ab_Heal(src, 0.3 * d)
        endif
    elseif a == AB_RW_FRISK then
        if rwHero and RW_Ready(src, 52, 12.0) then
            call SaveReal(RW_HT, rwTgt, 21, Mega_Time + 8.0)
            call SaveInteger(RW_HT, rwTgt, 22, GetPlayerId(rwPa) + 1)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 5, 8.0, 10.0)
            set Ab_FxCur = null
            call UnitShareVision(t, rwPa, true)
            call Fx_Say(t, "Frisked", 255, 200, 120, src)
        endif
    elseif a == AB_RW_STENCH then
        if GetRandomInt(1, 100) <= 25 then
            call Fx_HardCC(t, 0.7, src)
            call Fx_Say(t, "Flinched", 255, 220, 120, src)
        endif
    elseif a == AB_RW_PICKPOCKET then
        if atk and rwHero and GetRandomInt(1, 100) <= 25 and RW_Ready(src, 52, 6.0) then
            call RW_StealStage(src, t)
            set rwGold = IMinBJ(30, GetPlayerState(rwPb, PLAYER_STATE_RESOURCE_GOLD))
            if rwGold > 0 and GetPlayerId(rwPb) < 12 then
                call SetPlayerState(rwPb, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(rwPb, PLAYER_STATE_RESOURCE_GOLD) - rwGold)
                call SetPlayerState(rwPa, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(rwPa, PLAYER_STATE_RESOURCE_GOLD) + rwGold)
            endif
        endif
    elseif a == AB_RW_MAGICIAN then
        if skill and rwHero and GetRandomInt(1, 100) <= 20 and RW_Ready(src, 52, 8.0) then
            call RW_StealStage(src, t)
        endif
    elseif a == AB_RW_POISONTOUCH then
        if atk and GetRandomInt(1, 100) <= 40 then
            if Fx_HasKind(t, 2) then
                call Fx_Status(t, 3, src)
            else
                call Fx_Status(t, 2, src)
            endif
        elseif skill and Ty_CurPhys == 1 and GetRandomInt(1, 100) <= 25 then
            call Fx_Status(t, 2, src)
        endif
    elseif a == AB_RW_DRIZZLE then
        call SaveReal(RW_HT, rwTgt, 23, Mega_Time + 5.0)
        set Ab_FxCur = src
        call Ab_FxAdd(t, 2, 5.0, 0.15)
        set Ab_FxCur = null
    elseif a == AB_RW_DROUGHT then
        set Ab_FxCur = src
        call Ab_FxAdd(t, 1, 3.0, 0.015 * RW_MaxHP(t))
        set Ab_FxCur = null
        call SaveReal(RW_HT, rwTgt, 17, RMaxBJ(LoadReal(RW_HT, rwTgt, 17), Mega_Time + 3.0))
    elseif a == AB_RW_SLUSHRUSH then
        if atk then
            set rwKind = 1
            if RW_TimedOn(t, 27) then
                set rwKind = LoadInteger(RW_HT, rwTgt, 26) + 1
            endif
            if rwKind >= 5 then
                call SaveInteger(RW_HT, rwTgt, 26, 0)
                call Fx_HardCC(t, 1.0, src)
                call Fx_Say(t, "Frozen!", 140, 200, 255, src)
            else
                call SaveInteger(RW_HT, rwTgt, 26, rwKind)
                call SaveReal(RW_HT, rwTgt, 27, Mega_Time + 6.0)
                set Ab_FxCur = src
                call Ab_FxAdd(t, 2, 3.0, 0.08 * I2R(rwKind))
                set Ab_FxCur = null
            endif
        endif
    elseif a == AB_RW_HYPERCUTTER then
        if atk then
            set rwKind = 1
            if RW_TimedOn(t, 29) then
                set rwKind = IMinBJ(5, LoadInteger(RW_HT, rwTgt, 28) + 1)
            endif
            call SaveInteger(RW_HT, rwTgt, 28, rwKind)
            call SaveReal(RW_HT, rwTgt, 29, Mega_Time + 6.0)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 5, 6.0, 4.0 * I2R(rwKind))
            set Ab_FxCur = null
        endif
    elseif a == AB_RW_LIGHTNINGROD then
        if atk and GetRandomInt(1, 100) <= 20 then
            call RW_Chain(src, t, 0.5 * I2R(GetHeroInt(src, true)), 3)
        endif
    elseif a == AB_RW_STATIC then
        if atk and GetRandomInt(1, 100) <= 10 then
            call RW_Chain(src, t, 0.5 * d, 2)
        endif
    elseif a == AB_RW_SANDRUSH then
        if atk and LoadInteger(RW_HT, rwSrc, 54) == 1 then
            call SaveInteger(RW_HT, rwSrc, 54, 0)
            call SaveReal(RW_HT, rwSrc, 60, 0.0)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 2, 2.0, 0.3)
            set Ab_FxCur = null
        endif
    elseif a == AB_RW_IMPOSTER then
        if rwHero and LoadInteger(RW_HT, rwSrc, 69) != rwTgt and Mega_Time - LoadReal(RW_HT, rwSrc, 70) >= 3.0 then
            call SaveInteger(RW_HT, rwSrc, 69, rwTgt)
            call SaveReal(RW_HT, rwSrc, 70, Mega_Time)
            call Fx_Say(src, "Transform!", 220, 160, 255, t)
        endif
    endif
    // ---- the target's Ability (Mold Breaker ignores it)
    if a == AB_MOLDBREAKER or ta <= 0 or not Ab_Alive(t) then
        set rwPa = null
        set rwPb = null
        return
    endif
    if ta == AB_RW_CUDCHEW then
        if Mega_Time - LoadReal(RW_HT, rwTgt, 64) > 10.0 then
            call SaveReal(RW_HT, rwTgt, 64, Mega_Time)
            call SaveReal(RW_HT, rwTgt, 63, 0.0)
        endif
        call SaveReal(RW_HT, rwTgt, 63, LoadReal(RW_HT, rwTgt, 63) + d)
    elseif ta == AB_RW_WEAKARMOR then
        if atk and RW_Ready(t, 52, 5.0) then
            call Fx_StageAdd(t, 2, -1, 12.0, t)
            call Fx_StageAdd(t, 5, 2, 12.0, t)
        endif
    elseif ta == AB_RW_JUSTIFIED then
        if skill and mt == T_DARK then
            call Fx_StageAdd(t, 1, 1, 12.0, t)
        endif
    elseif ta == AB_RW_RATTLED then
        if rwTLife < 0.5 and RW_Ready(t, 52, 10.0) then
            call RW_Set(t, 43, 0.4, 44, 4.0)
            call RW_Set(t, 41, 0.2, 42, 4.0)
            call Fx_Say(t, "Rattled!", 255, 220, 120, src)
        endif
    elseif ta == AB_RW_UNBURDEN then
        if rwTLife < 0.5 and RW_Ready(t, 52, 30.0) then
            call RW_Set(t, 43, 0.6, 44, 5.0)
            call RW_Set(t, 41, 0.3, 42, 5.0)
            call Fx_Say(t, "Unburden!", 255, 220, 120, src)
        endif
    elseif ta == AB_RW_RUNAWAY then
        if rwTLife < 0.5 and RW_Ready(t, 52, 8.0) then
            call RW_Set(t, 43, 0.5, 44, 2.0)
            call SetUnitPathing(t, false)
            call SaveReal(RW_HT, rwTgt, 75, Mega_Time + 2.0)
        endif
    elseif ta == AB_RW_ANGERPOINT then
        if (rwTLife < 0.5 or RW_LastCrit) and RW_Ready(t, 52, 20.0) then
            call RW_Set(t, 45, 0.6, 46, 8.0)
            call RW_Set(t, 41, 0.4, 42, 8.0)
            call Fx_Say(t, "Anger Point!", 255, 80, 80, src)
        endif
    elseif ta == AB_RW_MARVELSCALE then
        if skill then
            if RW_TimedOn(t, 55) then
                call SaveInteger(RW_HT, rwTgt, 54, IMinBJ(5, LoadInteger(RW_HT, rwTgt, 54) + 1))
            else
                call SaveInteger(RW_HT, rwTgt, 54, 1)
            endif
            call SaveReal(RW_HT, rwTgt, 55, Mega_Time + 6.0)
        endif
    elseif ta == AB_RW_STORMDRAIN then
        if skill then
            call RW_AddMana(t, 0.03)
            if RW_TimedOn(t, 55) then
                call SaveInteger(RW_HT, rwTgt, 54, IMinBJ(5, LoadInteger(RW_HT, rwTgt, 54) + 1))
            else
                call SaveInteger(RW_HT, rwTgt, 54, 1)
            endif
            call SaveReal(RW_HT, rwTgt, 55, Mega_Time + 8.0)
        endif
    elseif ta == AB_RW_CURSEDBODY then
        if skill and GetRandomInt(1, 100) <= 30 then
            call Fx_Silence(src, 3.0, t)
        endif
    elseif ta == AB_RW_ROUGHSKIN then
        if rwMelee then
            call Ab_Deal(t, src, 0.05 * RW_MaxHP(t))
        endif
    elseif ta == AB_RW_EFFECTSPORE then
        if rwMelee and GetRandomInt(1, 100) <= 30 then
            set rwKind = GetRandomInt(1, 3)
            if rwKind == 1 then
                call Fx_Status(src, 2, t)
            elseif rwKind == 2 then
                call Fx_Status(src, 4, t)
            else
                call Fx_Status(src, 5, t)
            endif
        endif
    elseif ta == AB_RW_ICEBODY then
        if rwMelee then
            set Ab_FxCur = t
            call Ab_FxAdd(src, 2, 2.0, 0.3)
            set Ab_FxCur = null
        endif
    elseif ta == AB_RW_STATIC then
        if rwMelee and GetRandomInt(1, 100) <= 20 then
            call Fx_Status(src, 4, t)
        endif
    elseif ta == AB_RW_FLAMEBODY then
        if rwMelee and GetRandomInt(1, 100) <= 40 then
            call Fx_Status(src, 1, t)
        endif
    endif
    set rwPa = null
    set rwPb = null
endfunction

// ---- a spell was cast (EVENT_PLAYER_UNIT_SPELL_EFFECT)
function RW_HalfCdGo takes nothing returns nothing
    local timer rwClock = GetExpiredTimer()
    local integer rwKey = GetHandleId(rwClock)
    local unit rwCaster = LoadUnitHandle(RW_HT, rwKey, 0)
    local integer rwSpellId = LoadInteger(RW_HT, rwKey, 1)
    local real rwLeft = 0.0
    if rwCaster != null then
        set rwLeft = BlzGetUnitAbilityCooldownRemaining(rwCaster, rwSpellId)
        if rwLeft > 0.1 then
            call BlzStartUnitAbilityCooldown(rwCaster, rwSpellId, rwLeft * 0.5)
        endif
    endif
    call FlushChildHashtable(RW_HT, rwKey)
    call DestroyTimer(rwClock)
    set rwClock = null
    set rwCaster = null
endfunction

function RW_OnCast takes nothing returns boolean
    local unit rwCaster = GetTriggerUnit()
    local integer rwAbility = RW_Ab(rwCaster)
    local integer rwSpellId = GetSpellAbilityId()
    local integer rwMove = Mv_OfReal(rwSpellId)
    local integer rwHandle = GetHandleId(rwCaster)
    local integer rwLevel = 0
    local integer rwType = -1
    local timer rwClock = null
    if rwAbility <= 0 or not IsUnitType(rwCaster, UNIT_TYPE_HERO) then
        set rwCaster = null
        return false
    endif
    if rwMove >= 0 and rwMove < Mv_N then
        set rwType = Mv_Type[rwMove]
    endif
    call SaveReal(RW_HT, rwHandle, 56, Mega_Time)
    if rwAbility == AB_RW_REGENERATOR then
        call Ab_Heal(rwCaster, 0.04 * RW_MaxHP(rwCaster))
    elseif rwAbility == AB_RW_MOTORDRIVE then
        call Fx_StageAdd(rwCaster, 5, 1, 8.0, rwCaster)
    elseif rwAbility == AB_RW_SURGESURFER then
        call RW_Set(rwCaster, 43, 0.4, 44, 2.0)
        if rwType == T_ELECTRIC then
            call RW_CdReduce(rwCaster, 1.0)
        endif
    elseif rwAbility == AB_RW_PROTEAN then
        if rwType >= 0 then
            if LoadInteger(RW_HT, rwHandle, 58) - 1 != rwType then
                call RW_Set(rwCaster, 43, 0.1, 44, 2.0)
            endif
            call SaveInteger(RW_HT, rwHandle, 58, rwType + 1)
            call SaveReal(RW_HT, rwHandle, 59, Mega_Time + 6.0)
        endif
    elseif rwAbility == AB_RW_STANCECHANGE then
        if rwMove >= 0 and rwMove < Mv_N and Mv_Pow[rwMove] > 0 then
            call SaveReal(RW_HT, rwHandle, 57, Mega_Time + 5.0)
        endif
    elseif rwAbility == AB_RW_CLOUDNINE then
        if RW_Ready(rwCaster, 52, 15.0) then
            set rwLevel = GetUnitAbilityLevel(rwCaster, rwSpellId)
            if rwLevel > 0 then
                call SetUnitState(rwCaster, UNIT_STATE_MANA, GetUnitState(rwCaster, UNIT_STATE_MANA) + I2R(BlzGetUnitAbilityManaCost(rwCaster, rwSpellId, rwLevel - 1)))
            endif
            set rwClock = CreateTimer()
            call SaveUnitHandle(RW_HT, GetHandleId(rwClock), 0, rwCaster)
            call SaveInteger(RW_HT, GetHandleId(rwClock), 1, rwSpellId)
            call TimerStart(rwClock, 0.05, false, function RW_HalfCdGo)
            call Fx_Say(rwCaster, "Cloud Nine!", 160, 220, 255, null)
        endif
    elseif rwAbility == AB_RW_PRANKSTER then
        if rwMove >= 0 and rwMove < Mv_N and Mv_Pow[rwMove] <= 0 then
            call Fx_CdScale(rwCaster, rwSpellId, rwMove, 0.5)
        endif
    endif
    set rwCaster = null
    set rwClock = null
    return false
endfunction

// ---- a unit died (Aftermath, Moxie, Gluttony)
function RW_OnDeath takes nothing returns boolean
    local unit rwDead = GetTriggerUnit()
    local unit rwKiller = GetKillingUnit()
    local unit rwVictim = null
    local player rwOwner = GetOwningPlayer(rwDead)
    local real rwBlast = 0.0
    local integer rwKillerAbility = 0
    local boolean rwBig = false
    if RW_Ab(rwDead) == AB_RW_AFTERMATH and IsUnitType(rwDead, UNIT_TYPE_HERO) then
        set rwBlast = 10.0 * RW_MainStat(rwDead)
        call DestroyEffect(AddSpecialEffect("Objects\\Spawnmodels\\Other\\NeutralBuildingExplosion\\NeutralBuildingExplosion.mdl", GetUnitX(rwDead), GetUnitY(rwDead)))
        call GroupEnumUnitsInRange(RW_Grp, GetUnitX(rwDead), GetUnitY(rwDead), 400.0, null)
        loop
            set rwVictim = FirstOfGroup(RW_Grp)
            exitwhen rwVictim == null
            call GroupRemoveUnit(RW_Grp, rwVictim)
            if RW_IsFoe(rwVictim, rwOwner) then
                call Ab_Deal(rwDead, rwVictim, rwBlast)
                set Ab_FxCur = rwDead
                call Ab_FxAdd(rwVictim, 3, 3.0, 1.0)
                set Ab_FxCur = null
            endif
        endloop
    endif
    if rwKiller != null and IsUnitType(rwKiller, UNIT_TYPE_HERO) and IsUnitEnemy(rwDead, GetOwningPlayer(rwKiller)) then
        set rwKillerAbility = RW_Ab(rwKiller)
        set rwBig = IsUnitType(rwDead, UNIT_TYPE_HERO) or Leg_IsLegend(GetUnitTypeId(rwDead)) or PAX_IsFixedBoss(GetUnitTypeId(rwDead))
        if rwKillerAbility == AB_RW_MOXIE and rwBig then
            call Fx_StageAdd(rwKiller, 1, 1, 30.0, rwKiller)
        elseif rwKillerAbility == AB_RW_GLUTTONY then
            call Ab_Heal(rwKiller, 0.08 * RW_MaxHP(rwKiller))
            call RW_AddMana(rwKiller, 0.08)
        endif
    endif
    set rwDead = null
    set rwKiller = null
    set rwVictim = null
    set rwOwner = null
    return false
endfunction

// ---- auras around u (every 0.5s; dots once a second)
function RW_Aura takes unit u, integer a, real radius, boolean beat returns nothing
    local unit rwVictim = null
    local player rwOwner = GetOwningPlayer(u)
    local integer rwVictimHandle = 0
    local real rwSlow = 0.0
    local real rwVictimMax = 0.0
    call GroupEnumUnitsInRange(RW_Grp, GetUnitX(u), GetUnitY(u), radius, null)
    loop
        set rwVictim = FirstOfGroup(RW_Grp)
        exitwhen rwVictim == null
        call GroupRemoveUnit(RW_Grp, rwVictim)
        if RW_IsFoe(rwVictim, rwOwner) then
            set rwVictimHandle = GetHandleId(rwVictim)
            set rwVictimMax = RW_MaxHP(rwVictim)
            set Ab_FxCur = u
            if a == AB_RW_DAMP then
                if IsUnitType(rwVictim, UNIT_TYPE_HERO) then
                    call Ab_FxAdd(rwVictim, 4, 1.2, 0.2)
                    call SaveReal(RW_HT, rwVictimHandle, 17, RMaxBJ(LoadReal(RW_HT, rwVictimHandle, 17), Mega_Time + 1.2))
                endif
            elseif a == AB_RW_UNNERVE then
                if IsUnitType(rwVictim, UNIT_TYPE_HERO) then
                    call SaveReal(RW_HT, rwVictimHandle, 17, RMaxBJ(LoadReal(RW_HT, rwVictimHandle, 17), Mega_Time + 1.2))
                endif
            elseif a == AB_RW_STENCH then
                call Ab_FxAdd(rwVictim, 4, 1.2, 0.15)
                call SaveReal(RW_HT, rwVictimHandle, 12, 0.10)
                call SaveReal(RW_HT, rwVictimHandle, 13, Mega_Time + 1.2)
            elseif a == AB_RW_SANDSTREAM then
                call SaveReal(RW_HT, rwVictimHandle, 14, 0.20)
                call SaveReal(RW_HT, rwVictimHandle, 15, Mega_Time + 1.2)
                if beat and not Ty_Has(rwVictim, T_ROCK) and not Ty_Has(rwVictim, T_GROUND) and not Ty_Has(rwVictim, T_STEEL) then
                    call Ab_FxAdd(rwVictim, 1, 1.2, 0.01 * rwVictimMax)
                endif
            elseif a == AB_RW_FLAMEBODY then
                if beat then
                    call Ab_FxAdd(rwVictim, 1, 1.2, 0.01 * rwVictimMax)
                endif
            elseif a == AB_RW_SHADOWTAG then
                set rwSlow = 0.35
                if GetWidgetLife(rwVictim) < 0.3 * rwVictimMax then
                    set rwSlow = 0.5
                endif
                call Ab_FxAdd(rwVictim, 2, 1.2, rwSlow)
                call Ab_FxAdd(rwVictim, 4, 1.2, 0.2)
            elseif a == AB_RW_MAGNETPULL then
                set rwSlow = 0.25
                if Ty_Has(rwVictim, T_STEEL) then
                    set rwSlow = 0.5
                endif
                call Ab_FxAdd(rwVictim, 2, 1.2, rwSlow)
                call Ab_FxAdd(rwVictim, 5, 1.2, 8.0)
            elseif a == AB_RW_PRESSURE then
                if IsUnitType(rwVictim, UNIT_TYPE_HERO) then
                    call SaveReal(Fx_HT, rwVictimHandle, 51, Mega_Time + 1.2)
                    call SaveInteger(Fx_HT, rwVictimHandle, 52, 3)
                    call Ab_FxAdd(rwVictim, 4, 1.2, 0.15)
                endif
            endif
            set Ab_FxCur = null
        endif
    endloop
    set rwVictim = null
    set rwOwner = null
endfunction

// Magnet Pull: pull the nearest enemy hero within 600 by 200 toward u
function RW_Pull takes unit u returns nothing
    local unit rwVictim = null
    local unit rwBest = null
    local player rwOwner = GetOwningPlayer(u)
    local real rwBestDist = 999999.0
    local real rwDist = 0.0
    local real rwAngle = 0.0
    call GroupEnumUnitsInRange(RW_Grp, GetUnitX(u), GetUnitY(u), 600.0, null)
    loop
        set rwVictim = FirstOfGroup(RW_Grp)
        exitwhen rwVictim == null
        call GroupRemoveUnit(RW_Grp, rwVictim)
        if IsUnitType(rwVictim, UNIT_TYPE_HERO) and RW_IsFoe(rwVictim, rwOwner) and not RW_NoPush(rwVictim) then
            set rwDist = SquareRoot((GetUnitX(rwVictim) - GetUnitX(u)) * (GetUnitX(rwVictim) - GetUnitX(u)) + (GetUnitY(rwVictim) - GetUnitY(u)) * (GetUnitY(rwVictim) - GetUnitY(u)))
            if rwDist < rwBestDist then
                set rwBestDist = rwDist
                set rwBest = rwVictim
            endif
        endif
    endloop
    if rwBest != null and rwBestDist > 150.0 then
        set rwAngle = Atan2(GetUnitY(u) - GetUnitY(rwBest), GetUnitX(u) - GetUnitX(rwBest))
        call SetUnitPosition(rwBest, GetUnitX(rwBest) + RMinBJ(200.0, rwBestDist - 120.0) * Cos(rwAngle), GetUnitY(rwBest) + RMinBJ(200.0, rwBestDist - 120.0) * Sin(rwAngle))
        call Fx_Say(rwBest, "Pulled!", 200, 200, 255, u)
    endif
    set rwVictim = null
    set rwBest = null
    set rwOwner = null
endfunction

// Intimidate roar / Snow Warning storm / Friend Guard shields around u
function RW_Burst takes unit u, integer a, real radius returns nothing
    local unit rwVictim = null
    local player rwOwner = GetOwningPlayer(u)
    local real rwDamage = I2R(GetHeroInt(u, true))
    local real rwShield = 0.15 * RW_MaxHP(u)
    call GroupEnumUnitsInRange(RW_Grp, GetUnitX(u), GetUnitY(u), radius, null)
    loop
        set rwVictim = FirstOfGroup(RW_Grp)
        exitwhen rwVictim == null
        call GroupRemoveUnit(RW_Grp, rwVictim)
        if a == AB_RW_FRIENDGUARD then
            if Ab_Alive(rwVictim) and IsUnitType(rwVictim, UNIT_TYPE_HERO) and IsUnitAlly(rwVictim, rwOwner) then
                call RW_Shield(rwVictim, rwShield, 4.0)
            endif
        elseif RW_IsFoe(rwVictim, rwOwner) then
            if a == AB_RW_INTIMIDATE and IsUnitType(rwVictim, UNIT_TYPE_HERO) then
                if not RW_NoIntimidate(rwVictim) and Ab_Num(rwVictim) != AB_INNERFOCUS then
                    call Fx_StageAdd(rwVictim, 1, -1, 6.0, u)
                    call Fx_StageAdd(rwVictim, 3, -1, 6.0, u)
                endif
                call Fx_HardCC(rwVictim, 0.5, u)
            elseif a == AB_RW_SNOWWARNING then
                call Ab_Deal(u, rwVictim, rwDamage)
                set Ab_FxCur = u
                call Ab_FxAdd(rwVictim, 2, 2.0, 0.3)
                set Ab_FxCur = null
                call Ab_Pop(rwVictim, "Abilities\\Spells\\Undead\\FrostNova\\FrostNovaTarget.mdl", "origin")
            endif
        endif
    endloop
    set rwVictim = null
    set rwOwner = null
endfunction

// ---- every 0.5s for one hero with a reworked Ability
function RW_HeroTick takes unit u, boolean beat returns nothing
    local integer rwHandle = GetHandleId(u)
    local integer rwAbility = RW_Ab(u)
    local real rwMax = RW_MaxHP(u)
    local real rwLife = GetWidgetLife(u) / RMaxBJ(1.0, rwMax)
    local real rwIdle = Mega_Time - LoadReal(Ab_HT, rwHandle, 60)
    local real rwMoved = 0.0
    local integer rwStack = 0
    if LoadReal(RW_HT, rwHandle, 75) > 0.0 and Mega_Time >= LoadReal(RW_HT, rwHandle, 75) then
        call SaveReal(RW_HT, rwHandle, 75, 0.0)
        call SetUnitPathing(u, true)
    endif
    if LoadInteger(RW_HT, rwHandle, 22) > 0 and not RW_TimedOn(u, 21) then  // Frisk mark over: no more shared vision
        call UnitShareVision(u, Player(LoadInteger(RW_HT, rwHandle, 22) - 1), false)
        call SaveInteger(RW_HT, rwHandle, 22, 0)
    endif
    if beat and rwAbility == AB_ZENMODE and LoadInteger(Ab_HT, rwHandle, 85) == 1 then
        call Ab_Heal(u, 0.02 * rwMax)  // v4.2x Zen Mode
    endif
    if rwAbility < AB_RW_FIRST then
        return
    endif
    if rwAbility == AB_RW_DAMP then
        call RW_Aura(u, rwAbility, 500.0, beat)
    elseif rwAbility == AB_RW_UNNERVE or rwAbility == AB_RW_PRESSURE then
        call RW_Aura(u, rwAbility, 700.0, beat)
    elseif rwAbility == AB_RW_STENCH or rwAbility == AB_RW_SANDSTREAM then
        call RW_Aura(u, rwAbility, 400.0, beat)
    elseif rwAbility == AB_RW_FLAMEBODY then
        call RW_Aura(u, rwAbility, 250.0, beat)
    elseif rwAbility == AB_RW_SHADOWTAG then
        call RW_Aura(u, rwAbility, 500.0, beat)
    elseif rwAbility == AB_RW_MAGNETPULL then
        call RW_Aura(u, rwAbility, 600.0, beat)
        if RW_EnemyHeroesNear(u, 600.0) > 0 and RW_Ready(u, 52, 10.0) then
            call RW_Pull(u)
        endif
    elseif rwAbility == AB_RW_INTIMIDATE then
        if RW_EnemyHeroesNear(u, 600.0) > 0 and RW_Ready(u, 52, 15.0) then
            call Ab_Pop(u, "Abilities\\Spells\\Other\\HowlOfTerror\\HowlCaster.mdl", "origin")
            call RW_Burst(u, rwAbility, 600.0)
        endif
    elseif rwAbility == AB_RW_SNOWWARNING then
        if RW_EnemyHeroesNear(u, 400.0) > 0 and RW_Ready(u, 52, 8.0) then
            call RW_Burst(u, rwAbility, 400.0)
        endif
    elseif rwAbility == AB_RW_FRIENDGUARD then
        if RW_Ready(u, 52, 12.0) then
            call RW_Burst(u, rwAbility, 600.0)
        endif
    elseif rwAbility == AB_RW_CLEARBODY then
        if (Ab_HasBad(u) or Fx_HasStatus(u)) and RW_Ready(u, 52, 4.0) then
            call RW_Cleanse(u)
        endif
    elseif rwAbility == AB_RW_HEALER then
        if RW_Ready(u, 52, 5.0) then
            call RW_Cleanse(u)
            call Ab_Heal(u, 0.03 * rwMax)
        endif
    elseif rwAbility == AB_RW_HYDRATION then
        if RW_Ready(u, 52, 6.0) then
            call RW_Cleanse(u)
            call RW_Shield(u, 0.08 * rwMax, 3.0)
        endif
    elseif rwAbility == AB_RW_SHIELDDUST then
        if RW_Ready(u, 52, 10.0) then
            call RW_Shield(u, 0.10 * rwMax, 10.0)
        endif
    elseif rwAbility == AB_RW_HARVEST then
        set rwStack = LoadInteger(RW_HT, rwHandle, 54)
        if rwStack < 2 and RW_Ready(u, 52, 12.0) then
            set rwStack = rwStack + 1
        endif
        if rwLife < 0.5 and rwStack > 0 then
            set rwStack = rwStack - 1
            call Ab_Heal(u, 0.15 * rwMax)
            call Fx_Say(u, "Berry!", 120, 255, 120, null)
        endif
        call SaveInteger(RW_HT, rwHandle, 54, rwStack)
    elseif rwAbility == AB_RW_CUDCHEW then
        if RW_Ready(u, 52, 10.0) then
            call Ab_Heal(u, 0.4 * LoadReal(RW_HT, rwHandle, 63))
            call SaveReal(RW_HT, rwHandle, 63, 0.0)
            call SaveReal(RW_HT, rwHandle, 64, Mega_Time)
        endif
    elseif rwAbility == AB_RW_GUTS then
        if Fx_HasStatus(u) or rwLife < 0.4 then
            call SaveReal(RW_HT, rwHandle, 76, Mega_Time + 1.2)
        endif
    elseif rwAbility == AB_RW_SPEEDBOOST then
        if rwIdle < 3.0 then
            call SaveReal(RW_HT, rwHandle, 55, Mega_Time + 5.0)
            if RW_Ready(u, 52, 6.0) then
                call SaveInteger(RW_HT, rwHandle, 54, IMinBJ(6, LoadInteger(RW_HT, rwHandle, 54) + 1))
            endif
        elseif not RW_TimedOn(u, 55) then
            call SaveInteger(RW_HT, rwHandle, 54, 0)
        endif
    elseif rwAbility == AB_RW_SUCTIONCUPS or rwAbility == AB_RW_SANDRUSH then
        set rwMoved = SquareRoot((GetUnitX(u) - LoadReal(RW_HT, rwHandle, 67)) * (GetUnitX(u) - LoadReal(RW_HT, rwHandle, 67)) + (GetUnitY(u) - LoadReal(RW_HT, rwHandle, 68)) * (GetUnitY(u) - LoadReal(RW_HT, rwHandle, 68)))
        call SaveReal(RW_HT, rwHandle, 67, GetUnitX(u))
        call SaveReal(RW_HT, rwHandle, 68, GetUnitY(u))
        if rwAbility == AB_RW_SUCTIONCUPS then
            if rwMoved > 5.0 or LoadReal(RW_HT, rwHandle, 66) <= 0.0 then
                call SaveReal(RW_HT, rwHandle, 66, Mega_Time)
            endif
        elseif rwMoved > 20.0 then
            if LoadReal(RW_HT, rwHandle, 60) <= 0.0 then
                call SaveReal(RW_HT, rwHandle, 60, Mega_Time)
            elseif Mega_Time - LoadReal(RW_HT, rwHandle, 60) >= 2.0 then
                call SaveInteger(RW_HT, rwHandle, 54, 1)
            endif
        else
            call SaveReal(RW_HT, rwHandle, 60, 0.0)
        endif
    endif
    if beat then
        if rwAbility == AB_RW_OVERGROW and rwLife < 0.5 then
            call Ab_Heal(u, 0.02 * rwMax)
        elseif rwAbility == AB_RW_WATERABSORB and rwIdle >= 3.0 then
            call Ab_Heal(u, 0.01 * rwMax)
        elseif rwAbility == AB_RW_RAINDISH or rwAbility == AB_RW_INSOMNIA then
            call Ab_Heal(u, 0.01 * rwMax)
        elseif rwAbility == AB_RW_SNOWCLOAK and Wth_Cur == 4 then
            call Ab_Heal(u, 0.01 * rwMax)
        elseif rwAbility == AB_RW_REGENERATOR and rwIdle >= 3.0 then
            call Ab_Heal(u, 0.04 * rwMax)
        elseif rwAbility == AB_RW_EARLYBIRD and rwIdle >= 2.0 then
            call Ab_Heal(u, 0.03 * rwMax)
        elseif rwAbility == AB_RW_NATURALCURE then
            if rwIdle >= 3.0 then
                if Ab_HasBad(u) or Fx_HasStatus(u) then
                    call RW_Cleanse(u)
                endif
                call Ab_Heal(u, 0.03 * rwMax)
            elseif Fx_HasStatus(u) and RW_Ready(u, 52, 8.0) then
                call Fx_CureKind(u, LoadInteger(Fx_HT, rwHandle, 20))
            endif
        endif
    endif
endfunction

function RW_Tick takes nothing returns nothing
    local integer rwPlayer = 0
    local unit rwHero = null
    local boolean rwBeat = false
    set RW_Beat = RW_Beat + 1
    set rwBeat = ModuloInteger(RW_Beat, 2) == 0
    if Ab_N < RW_MAX then
        set Ab_N = RW_MAX  // Ab_Strip removes the info buttons 1..Ab_N
    endif
    if not RW_TextsDone then  // after Fx_Texts, which runs late in the map start
        set RW_TextsDone = true
        call ExecuteFunc("RW_Texts")
    endif
    loop
        exitwhen rwPlayer >= 12
        call GroupEnumUnitsOfPlayer(RW_Heroes, Player(rwPlayer), null)
        loop
            set rwHero = FirstOfGroup(RW_Heroes)
            exitwhen rwHero == null
            call GroupRemoveUnit(RW_Heroes, rwHero)
            if IsUnitType(rwHero, UNIT_TYPE_HERO) and Ab_Alive(rwHero) then
                call RW_HeroTick(rwHero, rwBeat)
                if RW_Ab(rwHero) >= AB_RW_FIRST or RW_TimedOn(rwHero, 42) or RW_TimedOn(rwHero, 44) then
                    call Fx_StatSync(rwHero)
                    call Ab_MoveBonus(rwHero, Ab_Num(rwHero))
                endif
            endif
        endloop
        set rwPlayer = rwPlayer + 1
    endloop
    set rwHero = null
endfunction
// ===== end of the main part =====
