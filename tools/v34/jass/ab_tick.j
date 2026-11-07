function Ab_Hero takes unit u returns nothing
    local integer a = 0
    call Mv_Sync(u)
    call Mv_Tips(u)
    call Ab_Sync(u)
    set a = Ab_Num(u)
    call Ab_Pulse(u, a)
    call Ext_Pulse(u)
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
    local integer h = GetHandleId(GetTriggerUnit())
    call SaveReal(Ab_HT, h, 9, Mega_Time)
    call SaveInteger(Ab_HT, h, 62, 0)  // Speed Boost starts over
    call SaveReal(Ab_HT, h, 63, 0.0)
    call SaveInteger(Ab_HT, h, 76, 0)  // Trace forgets its copy
endfunction

// condition of the one damage trigger: Leg_OnDamage first, then the skill scale, the move's type and the Abilities
function Ab_OnDamaging takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local unit src = null
    local player sp = null
    local player tp = null
    local real dmg = 0.0
    local real m = 1.0
    local real stat = 0.0
    local real eff = 1.0
    local boolean atk = false
    local boolean skill = false
    local boolean user = false
    local integer ta = 0
    local integer s_ab = 0
    local integer mt = -1
    local integer hs = 0
    local integer ht = 0
    call Leg_OnDamage()
    set src = GetEventDamageSource()
    if Ab_Busy or src == null or src == t then
        set t = null
        set src = null
        return false
    endif
    set dmg = GetEventDamage()
    if dmg <= 0.0 then
        set t = null
        set src = null
        return false
    endif
    if Env_IsSource(GetUnitTypeId(src)) then  // v3.3.1: traps / dummies of the legend lands
        set m = m * Env_DamageMult
    endif
    set sp = GetOwningPlayer(src)
    if not IsUnitEnemy(t, sp) then
        set t = null
        set src = null
        set sp = null
        return false
    endif
    set tp = GetOwningPlayer(t)
    set atk = BlzGetEventIsAttack()
    set skill = (not atk) and BlzGetEventDamageType() != DAMAGE_TYPE_NORMAL
    set user = GetPlayerId(sp) < 12
    set hs = GetHandleId(src)
    set ht = GetHandleId(t)
    // v3.4: the target of a neutral caster (Ai_Tick): the unit it hit, or the unit that hit it (no dummies)
    if sp == Player(PLAYER_NEUTRAL_AGGRESSIVE) and LoadInteger(Ab_HT, hs, 87) > 0 then
        call SaveUnitHandle(Ab_HT, hs, 86, t)
    endif
    if tp == Player(PLAYER_NEUTRAL_AGGRESSIVE) and LoadInteger(Ab_HT, ht, 87) > 0 and GetUnitAbilityLevel(src, 'Aloc') == 0 then
        call SaveUnitHandle(Ab_HT, ht, 86, src)
    endif
    set ta = Ab_Num(t)
    set s_ab = Ab_Num(src)
    // Intimidate: the first hit after 10s out of combat, on either side
    if ta == AB_INTIMIDATE and Mega_Time - LoadReal(Ab_HT, ht, 60) > 10.0 then
        call Ab_Intimidate(t)
    endif
    if s_ab == AB_INTIMIDATE and Mega_Time - LoadReal(Ab_HT, hs, 60) > 10.0 then
        call Ab_Intimidate(src)
    endif
    call SaveReal(Ab_HT, hs, 60, Mega_Time)
    call SaveReal(Ab_HT, ht, 60, Mega_Time)
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
    // v3.4: the type of the move (Aerilate / Pixilate turn Normal moves into Flying / Fairy)
    if skill then
        set mt = Ty_Resolve(src)
        if mt == T_NORMAL and s_ab == AB_AERILATE then
            set mt = T_FLYING
        elseif mt == T_NORMAL and s_ab == AB_PIXILATE then
            set mt = T_FAIRY
        endif
    endif
    set m = m * Ab_StateMult(src, skill, mt)
    if s_ab > 0 then
        set m = m * Ab_OutMult(src, t, s_ab, ta, atk, skill, mt)
    endif
    if mt >= 0 then
        set eff = Ty_Mult(mt, t)
        if ta == AB_DELTASTREAM and eff > 1.0 then
            set eff = 1.0
        endif
        set m = m * eff
    endif
    set m = m * Ext_DamageMult(src, t, atk, skill, mt, eff)  // v3.4 weather, items, Champion Aura, legend Mega
    // the target's Ability (Mold Breaker ignores it)
    if ta > 0 and s_ab != AB_MOLDBREAKER then
        if skill and Ab_Absorbs(t, ta, mt, dmg * m) then
            call Ab_Say(t, "Absorbed", 120, 200, 255, sp, tp)
            call BlzSetEventDamage(0.0)
            set t = null
            set src = null
            set sp = null
            set tp = null
            return false
        endif
        set m = m * Ab_InMult(src, t, ta, s_ab, atk, skill, mt, dmg * m)
    endif
    if m > 0.0 then
        if s_ab > 0 then
            call Ab_OnHit(src, t, s_ab, atk, skill, dmg * m)
        endif
        if LoadInteger(Ab_HT, hs, 0) == AB_TRACE and (atk or skill) then
            call Ab_TraceCopy(src, t)
        endif
        if ta > 0 and atk and s_ab != AB_MOLDBREAKER and Ab_Alive(src) then
            call Ab_InContact(src, t, ta)
        endif
        if ta > 0 then
            call Ab_AfterHit(t, ta, dmg * m)
        endif
        call Ext_AfterHit(src, t, atk, dmg * m)
        if GetUnitTypeId(t) == Leg_MewtwoId or GetUnitTypeId(t) == Leg_RayquazaId then
            call Leg_TryMega(t, dmg * m)
        endif
        call League_TryMega(t, dmg * m)
        if mt >= 0 and Mega_Time >= LoadReal(Ab_HT, ht, 57) and (eff >= 1.99 or eff <= 0.51) then
            call SaveReal(Ab_HT, ht, 57, Mega_Time + 1.0)
            if eff >= 1.99 then
                call Ab_Say(t, "Super effective!", 255, 140, 0, sp, tp)
                call Ab_Pop(t, "Abilities\\Spells\\Human\\Feedback\\SpellBreakerAttack.mdl", "chest")
            else
                call Ab_Say(t, "Not very effective...", 170, 170, 170, sp, tp)
            endif
        endif
    endif
    call SaveReal(Ab_HT, ht, 1, Mega_Time)
    set m = Ext_Final(t, dmg * m) / dmg  // v3.4 Focus Sash
    call BlzSetEventDamage(dmg * m)
    set t = null
    set src = null
    set sp = null
    set tp = null
    return false
endfunction
