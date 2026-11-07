// ---- timed effects (v3.4). Kinds: 1 damage over time (amt HP per second, dealt by Ab_FxSrc), 2 slow (move, amt =
// fraction), 3 stun, 4 attack slow (amt = fraction; heroes through Hero_HPSync, others by their cooldown),
// 5 armor down (amt), 6 disarm ('Abun'), 7 invulnerable, 8 invisible ('Apiv'). A refresh keeps the stronger amount.
// The slot of (unit, kind) is kept in Ab_HT key 90 + kind of the unit (slot + 1), so a lookup is one hashtable read.
function Ab_FxFind takes unit u, integer kind returns integer
    local integer i = LoadInteger(Ab_HT, GetHandleId(u), 90 + kind) - 1
    if i >= 0 and Ab_FxU[i] == u and Ab_FxKind[i] == kind then
        return i
    endif
    return -1
endfunction

// a free slot: scan on from the last one given (Ab_FxNext)
function Ab_FxFree takes nothing returns integer
    local integer n = 0
    loop
        exitwhen n >= Ab_FxMax
        set Ab_FxNext = Ab_FxNext + 1
        if Ab_FxNext >= Ab_FxMax then
            set Ab_FxNext = 0
        endif
        if Ab_FxU[Ab_FxNext] == null then
            return Ab_FxNext
        endif
        set n = n + 1
    endloop
    return -1
endfunction

// damage from an Ability (no Ability / type multipliers: Ab_Busy)
function Ab_Deal takes unit src, unit t, real d returns nothing
    if d <= 0.0 or t == null or not Ab_Alive(t) then
        return
    endif
    set Ab_Busy = true
    call UnitDamageTarget(src, t, d, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_UNIVERSAL, WEAPON_TYPE_WHOKNOWS)
    set Ab_Busy = false
endfunction

function Ab_Heal takes unit u, real amt returns nothing
    local real mx = I2R(BlzGetUnitMaxHP(u))
    local real hp = GetWidgetLife(u) + amt
    if amt <= 0.0 or not Ab_Alive(u) then
        return
    endif
    if hp > mx then
        set hp = mx
    endif
    call SetWidgetLife(u, hp)
endfunction

function Ab_FxAdd takes unit u, integer kind, real dur, real amt returns nothing
    local integer h = GetHandleId(u)
    local integer i = Ab_FxFind(u, kind)
    local boolean fresh = false
    local real old = 0.0
    if u == null or not Ab_Alive(u) then
        return
    endif
    if i < 0 then
        set i = Ab_FxFree()
        if i < 0 then
            return
        endif
        set fresh = true
        set Ab_FxU[i] = u
        set Ab_FxKind[i] = kind
        set Ab_FxEnd[i] = Mega_Time + dur
        call SaveInteger(Ab_HT, h, 90 + kind, i + 1)
    else
        set old = Ab_FxAmt[i]
        if amt < old then
            set amt = old
        endif
        if Mega_Time + dur > Ab_FxEnd[i] then
            set Ab_FxEnd[i] = Mega_Time + dur
        endif
    endif
    set Ab_FxAmt[i] = amt
    set Ab_FxSrc[i] = Ab_FxCur
    if kind == 2 then
        if LoadReal(Ab_HT, h, 11) <= 0.0 then
            call SaveReal(Ab_HT, h, 11, GetUnitMoveSpeed(u))
        endif
        call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11) * (1.0 - amt))
    elseif kind == 3 then
        call PauseUnit(u, true)
    elseif kind == 4 then
        if not IsUnitType(u, UNIT_TYPE_HERO) then
            if fresh then
                call SaveReal(Ab_HT, h, 12, BlzGetUnitAttackCooldown(u, 0))
            endif
            if LoadReal(Ab_HT, h, 12) > 0.0 and amt < 0.9 then
                call BlzSetUnitAttackCooldown(u, LoadReal(Ab_HT, h, 12) / (1.0 - amt), 0)
            endif
        endif
    elseif kind == 5 then
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + old - amt)
    elseif kind == 6 then
        if fresh then
            call UnitAddAbility(u, 'Abun')
        endif
    elseif kind == 7 then
        call SetUnitInvulnerable(u, true)
    elseif kind == 8 then
        if fresh then
            call UnitAddAbility(u, 'Apiv')
        endif
    endif
endfunction

// end slot i: undo what the effect changed
function Ab_FxStop takes integer i returns nothing
    local unit u = Ab_FxU[i]
    local integer kind = Ab_FxKind[i]
    local integer h = GetHandleId(u)
    local real amt = Ab_FxAmt[i]
    set Ab_FxU[i] = null
    set Ab_FxSrc[i] = null
    if LoadInteger(Ab_HT, h, 90 + kind) == i + 1 then
        call SaveInteger(Ab_HT, h, 90 + kind, 0)
    endif
    if kind == 2 and Ab_FxFind(u, 2) < 0 then
        if LoadReal(Ab_HT, h, 11) > 0.0 then
            call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11))
        endif
        call SaveReal(Ab_HT, h, 11, 0.0)
    elseif kind == 3 and Ab_FxFind(u, 3) < 0 then
        call PauseUnit(u, false)
    elseif kind == 4 then
        if not IsUnitType(u, UNIT_TYPE_HERO) and LoadReal(Ab_HT, h, 12) > 0.0 then
            call BlzSetUnitAttackCooldown(u, LoadReal(Ab_HT, h, 12), 0)
        endif
    elseif kind == 5 then
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + amt)
    elseif kind == 6 then
        call UnitRemoveAbility(u, 'Abun')
    elseif kind == 7 then
        call SetUnitInvulnerable(u, false)
    elseif kind == 8 then
        call UnitRemoveAbility(u, 'Apiv')
    endif
    set u = null
endfunction

// runs every 0.5s
function Ab_FxRun takes nothing returns nothing
    local integer i = 0
    local unit u = null
    local unit s = null
    local real d = 0.0
    loop
        exitwhen i >= Ab_FxMax
        set u = Ab_FxU[i]
        if u != null then
            if not Ab_Alive(u) or Mega_Time >= Ab_FxEnd[i] then
                call Ab_FxStop(i)
            elseif Ab_FxKind[i] == 1 then
                set d = Ab_FxAmt[i] * 0.5
                set s = Ab_FxSrc[i]
                if s != null and GetUnitTypeId(s) != 0 then
                    call Ab_Deal(s, u, d)
                elseif GetWidgetLife(u) - d > 1.0 then
                    call SetWidgetLife(u, GetWidgetLife(u) - d)
                endif
            endif
        endif
        set i = i + 1
    endloop
    set i = 0
    loop  // chain lightning bolts
        exitwhen i >= Ab_LtMax
        if Ab_Lt[i] != null and Mega_Time >= Ab_LtEnd[i] then
            call DestroyLightning(Ab_Lt[i])
            set Ab_Lt[i] = null
        endif
        set i = i + 1
    endloop
    set u = null
    set s = null
endfunction

// true if the unit has a harmful timed effect of ours (burn, poison, slow, stun, attack slow, armor down, disarm)
function Ab_HasBad takes unit u returns boolean
    local integer k = 1
    loop
        exitwhen k > 6
        if Ab_FxFind(u, k) >= 0 then
            return true
        endif
        set k = k + 1
    endloop
    return false
endfunction

// remove the harmful effects (ours and the game's negative buffs)
function Ab_Cleanse takes unit u returns nothing
    local integer k = 1
    local integer i = 0
    loop
        exitwhen k > 6
        set i = Ab_FxFind(u, k)
        if i >= 0 then
            call Ab_FxStop(i)
        endif
        set k = k + 1
    endloop
    call UnitRemoveBuffs(u, false, true)
    call Ab_Pop(u, "Abilities\\Spells\\Human\\DispelMagic\\DispelMagicTarget.mdl", "origin")
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

// main attribute (v3.2.16: strength or intelligence, whichever is higher = PokemonDB max(Atk, SpA); agility = speed)
function Ab_MainStat takes unit u returns real
    local real s = I2R(GetHeroStr(u, true))
    local real i = I2R(GetHeroInt(u, true))
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

// damage multiplier of a skill (v3.2.16): main stat / Ab_ScaleBase (x1 at 50, like the stat it grows 2% per level),
// at least 0.1, at most Ab_ScaleMax
function Ab_SkillMult takes real stat returns real
    local real m = stat / Ab_ScaleBase
    if m < 0.1 then
        set m = 0.1
    endif
    if m > Ab_ScaleMax then
        set m = Ab_ScaleMax
    endif
    return m
endfunction

// damage of an Ability's own hit (chain lightning): the hero's main stat, a creep's attack damage
function Ab_ProcDmg takes unit u returns real
    if IsUnitType(u, UNIT_TYPE_HERO) then
        return Ab_MainStat(u)
    endif
    return I2R(BlzGetUnitBaseDamage(u, 0)) + 10.0
endfunction

function Ab_Bolt takes unit a, unit b returns nothing
    local integer i = 0
    loop
        exitwhen i >= Ab_LtMax
        if Ab_Lt[i] == null then
            set Ab_Lt[i] = AddLightningEx("CLPB", true, GetUnitX(a), GetUnitY(a), 60.0, GetUnitX(b), GetUnitY(b), 60.0)
            set Ab_LtEnd[i] = Mega_Time + 0.4
            return
        endif
        set i = i + 1
    endloop
endfunction

// Static: lightning that jumps to 4 enemies (500 range), d damage each and a 0.5s stun
function Ab_Chain takes unit src, unit first, real d returns nothing
    local unit cur = first
    local unit prev = src
    local unit v = null
    local unit best = null
    local real bd = 0.0
    local real dx = 0.0
    local real dy = 0.0
    local integer n = 0
    local player p = GetOwningPlayer(src)
    call GroupClear(Ab_HitG)
    loop
        exitwhen cur == null or n >= 4
        call GroupAddUnit(Ab_HitG, cur)
        call Ab_Bolt(prev, cur)
        call Ab_Pop(cur, "Abilities\\Weapons\\Bolt\\BoltImpact.mdl", "origin")
        call Ab_Deal(src, cur, d)
        set Ab_FxCur = src
        call Ab_FxAdd(cur, 3, 0.5, 0.0)
        set n = n + 1
        set prev = cur
        set best = null
        set bd = 250000.0
        call GroupEnumUnitsInRange(Ab_Group, GetUnitX(cur), GetUnitY(cur), 500.0, null)
        loop
            set v = FirstOfGroup(Ab_Group)
            exitwhen v == null
            call GroupRemoveUnit(Ab_Group, v)
            if Ab_Alive(v) and IsUnitEnemy(v, p) and not IsUnitInGroup(v, Ab_HitG) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
                set dx = GetUnitX(v) - GetUnitX(cur)
                set dy = GetUnitY(v) - GetUnitY(cur)
                if dx * dx + dy * dy < bd then
                    set bd = dx * dx + dy * dy
                    set best = v
                endif
            endif
        endloop
        set cur = best
    endloop
    set Ab_FxCur = null
    call GroupClear(Ab_HitG)
    set cur = null
    set prev = null
    set v = null
    set best = null
    set p = null
endfunction

// Poison Point: 6% of max HP over 4s and 20% slow
function Ab_Poison takes unit src, unit t returns nothing
    set Ab_FxCur = src
    call Ab_FxAdd(t, 1, 4.0, 0.015 * I2R(BlzGetUnitMaxHP(t)))
    call Ab_FxAdd(t, 2, 4.0, 0.2)
    set Ab_FxCur = null
    call Ab_Pop(t, "Abilities\\Weapons\\ChimaeraAcidMissile\\ChimaeraAcidMissile.mdl", "chest")
endfunction

// boosts and weakens that sit on the attacker: Flash Fire (keys 7, 8), Intimidate (5, 6), Lightning Rod (72, moves),
// Drought of an ally (78, Fire moves)
function Ab_StateMult takes unit u, boolean skill, integer mt returns real
    local integer h = GetHandleId(u)
    local real m = 1.0
    if Mega_Time < LoadReal(Ab_HT, h, 7) then
        set m = m * (1.0 + LoadReal(Ab_HT, h, 8))
    endif
    if Mega_Time < LoadReal(Ab_HT, h, 5) then
        set m = m * (1.0 - LoadReal(Ab_HT, h, 6))
    endif
    if skill and Mega_Time < LoadReal(Ab_HT, h, 72) then
        set m = m * 1.3
    endif
    if skill and mt == T_FIRE and Mega_Time < LoadReal(Ab_HT, h, 78) then
        set m = m * 1.3
    endif
    return m
endfunction

// damage dealt by the attacker src from its Ability a (ta = the target's Ability, for Shell / Battle Armor)
function Ab_OutMult takes unit src, unit t, integer a, integer ta, boolean atk, boolean skill, integer mt returns real
    local integer h = GetHandleId(src)
    local real r = GetWidgetLife(src) / I2R(BlzGetUnitMaxHP(src))
    local real m = 1.0
    local real critc = 0.0
    local real cm = 2.0
    local integer n = 0
    if a >= AB_OVERGROW and a <= AB_SWARM then
        if r < 0.4 then
            set m = 1.5
        endif
    elseif a == AB_IRONFIST then
        if atk then
            set m = 1.35
            set n = LoadInteger(Ab_HT, h, 70) + 1
            if n >= 4 then
                set m = 2.7
                set n = 0
                call Ab_Pop(t, "Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl", "origin")
            endif
            call SaveInteger(Ab_HT, h, 70, n)
        endif
    elseif a == AB_ADAPTABILITY then
        if skill and Ty_Has(src, mt) then
            set m = 1.4
        endif
    elseif a == AB_TECHNICIAN then
        if skill and Ty_CurPow <= 60 then
            set m = 1.5
        endif
    elseif a == AB_RECKLESS then
        set m = 1.35
    elseif a == AB_GUTS then
        if atk and (r < 0.5 or Ab_HasBad(src)) then
            set m = 1.4
        endif
    elseif a == AB_ANGERPOINT then
        if Mega_Time < LoadReal(Ab_HT, h, 66) then
            set m = 1.6
        endif
    elseif a == AB_STEADFAST then
        if Mega_Time < LoadReal(Ab_HT, h, 3) then
            set m = 1.0 + 0.06 * I2R(LoadInteger(Ab_HT, h, 2))
        endif
    elseif a == AB_MULTITYPE then
        set m = 1.15
    elseif a == AB_SLOWSTART then
        if Mega_Time - LoadReal(Ab_HT, h, 9) < 30.0 then
            set m = 0.6
        else
            set m = 1.4
        endif
    elseif a == AB_TOUGHCLAWS then
        if atk then
            set m = 1.4
        elseif skill and Ty_CurPhys == 1 then
            set m = 1.2
        endif
    elseif a == AB_MEGALAUNCHER then
        if skill and Ty_CurPhys == 2 then
            set m = 1.4
        endif
    elseif a == AB_AERILATE then
        if skill and mt == T_FLYING then
            set m = 1.3
        endif
    elseif a == AB_PIXILATE then
        if skill and mt == T_FAIRY then
            set m = 1.3
        endif
    elseif a == AB_MOLDBREAKER then
        set m = 1.2
    elseif a == AB_MEGAADAPT then
        if skill and Ty_Has(src, mt) then
            set m = 1.6
        endif
    elseif a == AB_MEGATECH then
        if skill and Ty_CurPow <= 60 then
            set m = 1.6
        endif
    elseif a == AB_SANDFORCE then
        if skill and (mt == T_ROCK or mt == T_GROUND or mt == T_STEEL) then
            set m = 1.2
        endif
    elseif a == AB_PARENTALBOND then
        if skill then
            set m = 1.25
        endif
    elseif a == AB_NOGUARD then
        set m = 1.25
        set critc = 0.15
    elseif a == AB_KEENEYE then
        set critc = 0.15
    elseif a == AB_COMPOUNDEYES then
        set critc = 0.2
        set cm = 1.75
        if skill then
            set m = 1.1
        endif
    elseif a == AB_SUPERLUCK then
        set critc = 0.25
        set cm = 1.5
    elseif a == AB_STRONGJAW then
        if atk then
            set m = 1.3
        endif
    elseif a == AB_SOLARPOWER then
        if skill then
            set m = 1.4
        endif
    elseif a == AB_SKILLLINK then
        if skill then
            set m = 1.2
        endif
    elseif a == AB_ZENMODE then
        if LoadInteger(Ab_HT, h, 85) == 1 then
            if atk then
                set m = 0.5
            elseif skill then
                set m = 1.5
            endif
        endif
    endif
    if atk and critc > 0.0 and ta != AB_SHELLARMOR and ta != AB_BATTLEARMOR and GetRandomReal(0.0, 1.0) < critc then
        set m = m * cm
        call Ab_Say(t, "Crit!", 255, 60, 60, GetOwningPlayer(src), GetOwningPlayer(t))
        call Ab_Pop(t, "Abilities\\Spells\\Other\\Stampede\\StampedeMissileDeath.mdl", "origin")
    endif
    return m
endfunction

// Intimidate (on the first hit after 10s out of combat, once every 20s): enemies within 600 deal 25% less damage
// and have 5 less armor for 6s
function Ab_Intimidate takes unit u returns nothing
    local unit v = null
    local player p = GetOwningPlayer(u)
    local integer h = GetHandleId(u)
    if Mega_Time < LoadReal(Ab_HT, h, 73) then
        set p = null
        return
    endif
    call SaveReal(Ab_HT, h, 73, Mega_Time + 20.0)
    call Ab_Pop(u, "Abilities\\Spells\\Other\\HowlOfTerror\\HowlCaster.mdl", "origin")
    set Ab_FxCur = u
    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(u), GetUnitY(u), 600.0, null)
    loop
        set v = FirstOfGroup(Ab_Group)
        exitwhen v == null
        call GroupRemoveUnit(Ab_Group, v)
        if Ab_Alive(v) and IsUnitEnemy(v, p) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
            call SaveReal(Ab_HT, GetHandleId(v), 5, Mega_Time + 6.0)
            call SaveReal(Ab_HT, GetHandleId(v), 6, 0.25)
            call Ab_FxAdd(v, 5, 6.0, 5.0)
        endif
    endloop
    set Ab_FxCur = null
    set v = null
    set p = null
endfunction

// damage taken by the holder t of Ability a (multiplier of the incoming damage d). srcab = the attacker's Ability.
function Ab_InMult takes unit src, unit t, integer a, integer srcab, boolean atk, boolean skill, integer mt, real d returns real
    local integer h = GetHandleId(t)
    local real mx = I2R(BlzGetUnitMaxHP(t))
    local real hp = GetWidgetLife(t)
    local real m = 1.0
    local real dodge = 0.0
    local real nd = 0.0
    local integer stacks = 0
    local player plA = GetOwningPlayer(src)
    local player plB = GetOwningPlayer(t)
    // dodge, attacks only (attacks of Keen Eye and No Guard cannot be dodged)
    if atk and srcab != AB_KEENEYE and srcab != AB_NOGUARD then
        if a == AB_LEVITATE or a == AB_INNERFOCUS or a == AB_AIRLOCK then
            set dodge = 0.15
        elseif a == AB_SWIFTSWIM then
            set dodge = 0.1
        elseif a == AB_SANDVEIL or a == AB_SNOWCLOAK or a == AB_LEAFGUARD or a == AB_INSOMNIA then
            set dodge = 0.2
        elseif a == AB_TRACE or a == AB_DELTASTREAM or a == AB_MEGAINNERFOCUS then
            set dodge = 0.25
        endif
        if (a == AB_SANDVEIL and Wth_Cur == 3) or (a == AB_SNOWCLOAK and Wth_Cur == 4) then  // v3.4 weather
            set dodge = dodge + 0.15
        endif
        if dodge > 0.0 and GetRandomReal(0.0, 1.0) < dodge then
            call Ab_Say(t, "Miss", 210, 210, 210, plA, plB)
            set Ab_FxCur = t
            if a == AB_SANDVEIL then
                call Ab_FxAdd(src, 2, 2.0, 0.2)
            elseif a == AB_SNOWCLOAK then
                call Ab_FxAdd(src, 2, 2.0, 0.4)
                call Ab_Pop(src, "Abilities\\Spells\\Undead\\FrostNova\\FrostNovaTarget.mdl", "origin")
            elseif a == AB_LEAFGUARD then
                call Ab_Heal(t, 0.03 * mx)
            endif
            set Ab_FxCur = null
            set plA = null
            set plB = null
            return 0.0
        endif
    endif
    if a == AB_MULTISCALE then
        if hp >= 0.8 * mx then
            set m = 0.6
        endif
    elseif a == AB_MULTITYPE then
        set m = 0.85
    elseif a == AB_LEVITATE then
        if skill and mt == T_GROUND then
            set m = 0.0
            call Ab_Say(t, "Immune", 210, 210, 210, plA, plB)
        endif
    elseif a == AB_SHELLARMOR then
        if atk then
            set m = 0.8
        endif
    elseif a == AB_BATTLEARMOR then
        if atk and d > 0.0 then
            set nd = d - 2.0 * I2R(GetUnitLevel(t))
            if nd < 0.0 then
                set nd = 0.0
            endif
            set m = nd / d
        endif
    elseif a == AB_CLEARBODY then
        if skill then
            set m = 0.85
        endif
    elseif a == AB_ROCKHEAD then
        set m = 0.9
    elseif a == AB_SOUNDPROOF then
        if skill then
            set m = 0.7
        endif
    elseif a == AB_INNERFOCUS then
        if skill then
            set m = 0.8
        endif
    elseif a == AB_MEGAINNERFOCUS then
        if skill then
            set m = 0.7
        endif
    elseif a == AB_SANDSTREAM then
        if skill then
            set m = 0.8
        endif
    elseif a == AB_THICKFAT then
        if skill and (mt == T_FIRE or mt == T_ICE) then
            set m = 0.5
        endif
    elseif a == AB_MAGICBOUNCE then
        if skill then
            if GetRandomReal(0.0, 1.0) < 0.2 then
                set m = 0.0
                call Ab_Say(t, "Bounce", 160, 120, 255, plA, plB)
                call Ab_Pop(t, "Abilities\\Spells\\Items\\SpellShieldAmulet\\SpellShieldCaster.mdl", "origin")
            else
                call Ab_Deal(t, src, 0.35 * d)
            endif
        endif
    elseif a == AB_SYNCHRONIZE then
        if skill then
            call Ab_Deal(t, src, 0.25 * d)
            set Ab_FxCur = t
            call Ab_FxAdd(src, 2, 3.0, 0.3)
            set Ab_FxCur = null
        endif
    elseif a == AB_STEADFAST then
        set stacks = LoadInteger(Ab_HT, h, 2)
        if Mega_Time < LoadReal(Ab_HT, h, 3) then
            set stacks = stacks + 1
            if stacks > 6 then
                set stacks = 6
            endif
        else
            set stacks = 1
        endif
        call SaveInteger(Ab_HT, h, 2, stacks)
        call SaveReal(Ab_HT, h, 3, Mega_Time + 5.0)
    endif
    // Sturdy / Sand Force: a lethal hit leaves 15% HP and 1.5s of invulnerability, once every 60s
    if (a == AB_STURDY or a == AB_SANDFORCE) and d > 0.0 and d * m >= hp and Mega_Time >= LoadReal(Ab_HT, h, 4) then
        set nd = hp - 0.15 * mx
        if nd < 0.0 then
            set nd = 0.0
        endif
        set m = nd / d
        call SaveReal(Ab_HT, h, 4, Mega_Time + 60.0)
        set Ab_FxCur = null
        call Ab_FxAdd(t, 7, 1.5, 0.0)
        call Ab_Pop(t, "Abilities\\Spells\\Human\\DivineShield\\DivineShieldTarget.mdl", "origin")
        call Ab_Say(t, "Sturdy!", 255, 220, 120, plA, plB)
    endif
    set plA = null
    set plB = null
    return m
endfunction

// Water Absorb / Volt Absorb / Lightning Rod / Flash Fire: a move of that type does no damage (heal or boost)
function Ab_Absorbs takes unit t, integer a, integer mt, real d returns boolean
    local integer h = GetHandleId(t)
    if mt < 0 then
        return false
    endif
    if (a == AB_WATERABSORB and mt == T_WATER) or ((a == AB_VOLTABSORB or a == AB_LIGHTNINGROD) and mt == T_ELECTRIC) then
        call Ab_Heal(t, 0.25 * d)
        call Ab_Pop(t, "Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", "origin")
        if a == AB_VOLTABSORB then
            call SaveReal(Ab_HT, h, 71, Mega_Time + 5.0)
        elseif a == AB_LIGHTNINGROD then
            call SaveReal(Ab_HT, h, 72, Mega_Time + 6.0)
        endif
        return true
    endif
    if a == AB_FLASHFIRE and mt == T_FIRE then
        call SaveReal(Ab_HT, h, 7, Mega_Time + 8.0)
        call SaveReal(Ab_HT, h, 8, 0.4)
        call Ab_Pop(t, "Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl", "origin")
        return true
    endif
    return false
endfunction

// effects of the attacker's Ability a after its hit landed (d = damage dealt)
function Ab_OnHit takes unit src, unit t, integer a, boolean atk, boolean skill, real d returns nothing
    local integer h = GetHandleId(t)
    local real mx = I2R(BlzGetUnitMaxHP(t))
    local boolean pinch = GetWidgetLife(src) < 0.4 * I2R(BlzGetUnitMaxHP(src))
    local integer n = 0
    if a == AB_BLAZE then
        if atk and pinch then
            set Ab_FxCur = src
            call Ab_FxAdd(t, 1, 3.0, 0.02 * mx)
            set Ab_FxCur = null
            call Ab_Pop(t, "Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl", "chest")
        endif
    elseif a == AB_SWARM then
        if pinch then
            call Ab_Heal(src, 0.2 * d)
        endif
    elseif a == AB_STATIC then
        if atk and GetRandomReal(0.0, 1.0) < 0.2 then
            call Ab_Chain(src, t, Ab_ProcDmg(src))
        endif
    elseif a == AB_POISONPOINT then
        if atk and GetRandomReal(0.0, 1.0) < 0.25 then
            call Ab_Poison(src, t)
        endif
    elseif a == AB_ROCKHEAD then
        if atk and GetRandomReal(0.0, 1.0) < 0.15 then
            set Ab_FxCur = src
            call Ab_FxAdd(t, 3, 1.0, 0.0)
            set Ab_FxCur = null
            call Ab_Pop(t, "Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl", "origin")
        endif
    elseif a == AB_HYPERCUTTER then
        if atk then
            if Mega_Time < LoadReal(Ab_HT, h, 75) then
                set n = LoadInteger(Ab_HT, h, 74)
            endif
            set n = n + 1
            if n > 5 then
                set n = 5
            endif
            call SaveInteger(Ab_HT, h, 74, n)
            call SaveReal(Ab_HT, h, 75, Mega_Time + 6.0)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 5, 6.0, 3.0 * I2R(n))
            set Ab_FxCur = null
        endif
    elseif a == AB_RECKLESS then
        if GetWidgetLife(src) - 0.05 * d > 1.0 then
            call SetWidgetLife(src, GetWidgetLife(src) - 0.05 * d)
        endif
    elseif a == AB_STRONGJAW then
        if atk and GetRandomReal(0.0, 1.0) < 0.2 then
            call Ab_Deal(src, t, 0.5 * d)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 1, 3.0, 0.01 * mx)
            set Ab_FxCur = null
            call Ab_Pop(t, "Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodFootman.mdl", "chest")
        endif
    elseif a == AB_SKILLLINK then
        if atk and GetRandomReal(0.0, 1.0) < 0.3 then
            call Ab_Deal(src, t, 0.5 * d)
            call Ab_Deal(src, t, 0.5 * d)
            call Ab_Say(t, "x3!", 255, 200, 60, GetOwningPlayer(src), GetOwningPlayer(t))
        endif
    endif
endfunction

// effects of the target's Ability a when an attack of src hit it
function Ab_InContact takes unit src, unit t, integer a returns nothing
    local real mx = I2R(BlzGetUnitMaxHP(src))
    if a == AB_STATIC then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            call Ab_Chain(t, src, Ab_ProcDmg(t))
        endif
    elseif a == AB_FLAMEBODY then
        if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then
            set Ab_FxCur = t
            call Ab_FxAdd(src, 1, 3.0, 0.01 * mx)
            set Ab_FxCur = null
        endif
    elseif a == AB_POISONPOINT then
        if GetRandomReal(0.0, 1.0) < 0.25 then
            call Ab_Poison(t, src)
        endif
    elseif a == AB_CUTECHARM then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            set Ab_FxCur = t
            call Ab_FxAdd(src, 6, 1.5, 0.0)
            call Ab_FxAdd(src, 2, 1.5, 0.5)
            set Ab_FxCur = null
            call Ab_Pop(src, "Abilities\\Spells\\Other\\Charm\\CharmTarget.mdl", "overhead")
        endif
    endif
endfunction

// move speed bonus of the hero's Ability (applied only while it is not slowed; key 83 = bonus now applied)
function Ab_MoveBonus takes unit u, integer a returns nothing
    local integer h = GetHandleId(u)
    local real b = 0.0
    if a == AB_CHLOROPHYLL then
        set b = 40.0
    elseif a == AB_SWIFTSWIM then
        set b = 60.0
    elseif a == AB_SPEEDBOOST then
        set b = 10.0 * I2R(LoadInteger(Ab_HT, h, 62))
    endif
    if (a == AB_SWIFTSWIM and Wth_Cur == 1) or (a == AB_CHLOROPHYLL and Wth_Cur == 2) then  // v3.4 weather
        set b = b + 0.3 * GetUnitDefaultMoveSpeed(u)
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) then  // v3.4 Choice Scarf / Band / Specs
        if Itm_Flag(u, 3) then
            set b = b + 0.3 * GetUnitDefaultMoveSpeed(u)
        endif
        if Itm_Flag(u, 1) or Itm_Flag(u, 2) then
            set b = b - 0.1 * GetUnitDefaultMoveSpeed(u)
        endif
    endif
    if Mega_Time < LoadReal(Ab_HT, h, 69) then  // Run Away dash
        set b = b + 0.6 * GetUnitDefaultMoveSpeed(u)
    endif
    if b != LoadReal(Ab_HT, h, 83) and Ab_FxFind(u, 2) < 0 then
        call SetUnitMoveSpeed(u, GetUnitDefaultMoveSpeed(u) + b)
        call SaveReal(Ab_HT, h, 83, b)
    endif
endfunction

// HP thresholds crossed by a hit of `dealt` on the holder t: Anger Point, Run Away, the pinch Abilities
function Ab_AfterHit takes unit t, integer a, real dealt returns nothing
    local integer h = GetHandleId(t)
    local real mx = I2R(BlzGetUnitMaxHP(t))
    local real hp = GetWidgetLife(t)
    local real after = hp - dealt
    local player p = GetOwningPlayer(t)
    if after <= 0.405 then
        set p = null
        return
    endif
    if a == AB_ANGERPOINT then
        if hp >= 0.5 * mx and after < 0.5 * mx and Mega_Time >= LoadReal(Ab_HT, h, 67) then
            call SaveReal(Ab_HT, h, 66, Mega_Time + 6.0)
            call SaveReal(Ab_HT, h, 67, Mega_Time + 30.0)
            call Ab_Pop(t, "Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", "chest")
            call Ab_Say(t, "Anger Point!", 255, 80, 40, p, p)
        endif
    elseif a == AB_RUNAWAY then
        if hp >= 0.3 * mx and after < 0.3 * mx and Mega_Time >= LoadReal(Ab_HT, h, 68) then
            call SaveReal(Ab_HT, h, 68, Mega_Time + 30.0)
            call SaveReal(Ab_HT, h, 69, Mega_Time + 2.0)
            set Ab_FxCur = null
            call Ab_FxAdd(t, 8, 2.0, 0.0)
            call Ab_MoveBonus(t, a)
            call Ab_Say(t, "Run Away!", 200, 255, 200, p, p)
        endif
    elseif a >= AB_OVERGROW and a <= AB_SWARM then
        if hp >= 0.4 * mx and after < 0.4 * mx then
            call Ab_Pop(t, "Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", "chest")
            call Ab_Say(t, Ab_Name[a] + "!", 255, 160, 40, p, p)
        endif
    endif
    set p = null
endfunction

// Trace: the holder copies the Ability of what it hits (none: back to Trace's own dodge)
function Ab_TraceCopy takes unit src, unit t returns nothing
    local integer b = LoadInteger(Ab_HT, GetHandleId(t), 0)
    local integer h = GetHandleId(src)
    if b == AB_TRACE or b == AB_PARENTALBOND or b == AB_MULTITYPE or b == AB_SLOWSTART then
        set b = 0
    endif
    if b != LoadInteger(Ab_HT, h, 76) then
        call SaveInteger(Ab_HT, h, 76, b)
        if b > 0 then
            call Ab_Say(src, "Trace: " + Ab_Name[b], 160, 200, 255, GetOwningPlayer(src), GetOwningPlayer(src))
        endif
    endif
endfunction

// attack speed multiplier of the hero's Ability and of the attack slows on it (stored in key 84 for Hero_HPSync)
function Ab_ASMult takes unit u, integer a returns real
    local integer h = GetHandleId(u)
    local real m = 1.0
    local integer i = 0
    if a == AB_TORRENT then
        if GetWidgetLife(u) < 0.4 * I2R(BlzGetUnitMaxHP(u)) then
            set m = 1.4
        endif
    elseif a == AB_VOLTABSORB then
        if Mega_Time < LoadReal(Ab_HT, h, 71) then
            set m = 1.3
        endif
    elseif a == AB_CHLOROPHYLL then
        set m = 1.2
    elseif a == AB_GUTS then
        if GetWidgetLife(u) < 0.5 * I2R(BlzGetUnitMaxHP(u)) or Ab_HasBad(u) then
            set m = 1.2
        endif
    elseif a == AB_ANGERPOINT then
        if Mega_Time < LoadReal(Ab_HT, h, 66) then
            set m = 1.4
        endif
    elseif a == AB_STEADFAST then
        if Mega_Time < LoadReal(Ab_HT, h, 3) then
            set m = 1.0 + 0.06 * I2R(LoadInteger(Ab_HT, h, 2))
        endif
    elseif a == AB_SPEEDBOOST then
        set m = 1.0 + 0.08 * I2R(LoadInteger(Ab_HT, h, 62))
    elseif a == AB_MEGATECH then
        set m = 1.2
    elseif a == AB_SLOWSTART then
        if Mega_Time - LoadReal(Ab_HT, h, 9) >= 30.0 then
            set m = 1.2
        endif
    endif
    set i = Ab_FxFind(u, 4)
    if i >= 0 then
        set m = m * (1.0 - Ab_FxAmt[i])
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) and Itm_Flag(u, 3) then  // v3.4 Choice Scarf
        set m = m * 1.2
    endif
    return m
endfunction

// auras (every second): r = range
function Ab_Aura takes unit u, integer a, real r returns nothing
    local unit v = null
    local player p = GetOwningPlayer(u)
    local integer hv = 0
    local real mx = 0.0
    local real mana = 0.0
    local boolean mega = LoadInteger(Mega_HT, GetHandleId(u), 0) > 0
    set Ab_FxCur = u
    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(u), GetUnitY(u), r, null)
    loop
        set v = FirstOfGroup(Ab_Group)
        exitwhen v == null
        call GroupRemoveUnit(Ab_Group, v)
        if v != u and Ab_Alive(v) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
            set hv = GetHandleId(v)
            set mx = I2R(BlzGetUnitMaxHP(v))
            if IsUnitEnemy(v, p) then
                if a == AB_FLAMEBODY then
                    call Ab_Deal(u, v, 0.01 * mx)
                elseif a == AB_PRESSURE then
                    call Ab_FxAdd(v, 4, 1.5, 0.2)
                    set mana = GetUnitState(v, UNIT_STATE_MANA) - 0.02 * GetUnitState(v, UNIT_STATE_MAX_MANA)
                    if mana < 0.0 then
                        set mana = 0.0
                    endif
                    call SetUnitState(v, UNIT_STATE_MANA, mana)
                elseif a == AB_MAGNETPULL then
                    if Ty_Has(v, T_STEEL) then
                        call Ab_FxAdd(v, 2, 1.5, 0.4)
                    else
                        call Ab_FxAdd(v, 2, 1.5, 0.2)
                    endif
                    call Ab_FxAdd(v, 5, 1.5, 5.0)
                elseif a == AB_BADDREAMS then
                    if LoadInteger(Ab_HT, hv, 0) != AB_INSOMNIA then
                        call Ab_Deal(u, v, 0.02 * mx)
                    endif
                elseif a == AB_DROUGHT then
                    call Ab_Deal(u, v, 0.01 * mx)
                elseif a == AB_SANDSTREAM then
                    if not (Ty_Has(v, T_ROCK) or Ty_Has(v, T_GROUND) or Ty_Has(v, T_STEEL)) then
                        if mega then
                            call Ab_Deal(u, v, 0.015 * mx)
                        else
                            call Ab_Deal(u, v, 0.01 * mx)
                        endif
                    endif
                elseif a == AB_SHADOWTAG then
                    call Ab_FxAdd(v, 2, 1.5, 0.35)
                    call Ab_FxAdd(v, 4, 1.5, 0.15)
                elseif a == AB_AIRLOCK then
                    call SaveReal(Ab_HT, hv, 77, Mega_Time + 1.5)
                endif
            elseif a == AB_DROUGHT then
                call SaveReal(Ab_HT, hv, 78, Mega_Time + 1.5)
            endif
        endif
    endloop
    if a == AB_DROUGHT then
        call SaveReal(Ab_HT, GetHandleId(u), 78, Mega_Time + 1.5)
    endif
    set Ab_FxCur = null
    set v = null
    set p = null
endfunction

// every second, for each hero of the players: regeneration, cleansing, stacks, auras, move and attack speed
function Ab_Pulse takes unit u, integer a returns nothing
    local integer h = GetHandleId(u)
    local real mx = I2R(BlzGetUnitMaxHP(u))
    local real idle = Mega_Time - LoadReal(Ab_HT, h, 60)
    local integer n = 0
    if a == AB_OVERGROW then
        if GetWidgetLife(u) < 0.4 * mx then
            call Ab_Heal(u, 0.02 * mx)
        endif
    elseif a == AB_WATERABSORB then
        if idle >= 3.0 then
            call Ab_Heal(u, 0.01 * mx)
        endif
    elseif a == AB_EARLYBIRD then
        if idle >= 3.0 then
            call Ab_Heal(u, 0.02 * mx)
        endif
    elseif a == AB_NATURALCURE then
        if idle >= 3.0 then
            call Ab_Heal(u, 0.03 * mx)
            if Ab_HasBad(u) then
                call Ab_Cleanse(u)
            endif
        endif
    elseif a == AB_SHEDSKIN then
        if Mega_Time >= LoadReal(Ab_HT, h, 79) then
            call SaveReal(Ab_HT, h, 79, Mega_Time + 5.0)
            if GetRandomReal(0.0, 1.0) < 0.3 then
                call Ab_Cleanse(u)
                call Ab_Heal(u, 0.05 * mx)
            endif
        endif
    elseif a == AB_CLEARBODY then
        if Mega_Time >= LoadReal(Ab_HT, h, 79) then
            call SaveReal(Ab_HT, h, 79, Mega_Time + 6.0)
            if Ab_HasBad(u) then
                call Ab_Cleanse(u)
            endif
        endif
    elseif a == AB_SPEEDBOOST then
        if idle < 3.0 then
            set n = LoadInteger(Ab_HT, h, 62)
            if LoadReal(Ab_HT, h, 63) <= 0.0 then
                call SaveReal(Ab_HT, h, 63, Mega_Time + 10.0)
            elseif Mega_Time >= LoadReal(Ab_HT, h, 63) and n < 5 then
                call SaveInteger(Ab_HT, h, 62, n + 1)
                call SaveReal(Ab_HT, h, 63, Mega_Time + 10.0)
                call Ab_Pop(u, "Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", "chest")
            endif
        endif
    elseif a == AB_FLAMEBODY then
        call Ab_Aura(u, a, 350.0)
    elseif a == AB_PRESSURE or a == AB_AIRLOCK or a == AB_SANDSTREAM then
        call Ab_Aura(u, a, 600.0)
    elseif a == AB_MAGNETPULL or a == AB_BADDREAMS then
        call Ab_Aura(u, a, 500.0)
    elseif a == AB_DROUGHT then
        call Ab_Aura(u, a, 700.0)
    elseif a == AB_SHADOWTAG then
        call Ab_Aura(u, a, 450.0)
    elseif a == AB_SOLARPOWER then
        if idle < 3.0 and GetWidgetLife(u) - 0.01 * mx > 0.3 * mx then
            call SetWidgetLife(u, GetWidgetLife(u) - 0.01 * mx)
        endif
    elseif a == AB_ZENMODE then
        if GetWidgetLife(u) < 0.5 * mx then
            if LoadInteger(Ab_HT, h, 85) != 1 and Ab_ZenSkin != 0 then
                call SaveInteger(Ab_HT, h, 85, 1)
                call BlzSetUnitSkin(u, Ab_ZenSkin)
                call SetUnitScale(u, Ab_ZenScale, Ab_ZenScale, Ab_ZenScale)
                call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + Ab_ZenArmor)
                call Ab_Pop(u, "Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl", "origin")
                call Ab_Say(u, "Zen Mode!", 200, 120, 255, GetOwningPlayer(u), GetOwningPlayer(u))
            endif
        elseif LoadInteger(Ab_HT, h, 85) == 1 then
            call SaveInteger(Ab_HT, h, 85, 0)
            call BlzSetUnitSkin(u, GetUnitTypeId(u))
            call SetUnitScale(u, Ab_ZenBase, Ab_ZenBase, Ab_ZenBase)
            call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - Ab_ZenArmor)
        endif
    endif
    call Ab_MoveBonus(u, a)
    call SaveReal(Ab_HT, h, 84, Ab_ASMult(u, a))
endfunction
