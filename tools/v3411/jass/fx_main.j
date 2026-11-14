// =============================================================================================
// v3.4.11 move / status engine, part 2 (inserted before Ext_AfterHit). Earlier code reaches it through
// ExecuteFunc("Fx_...X") with the Fx_Arg* globals. Data layout: see part 1 (before Hero_HPSync).
// =============================================================================================
function Fx_Track takes unit u returns nothing
    if not IsUnitInGroup(u, Fx_G) then
        call GroupAddUnit(Fx_G, u)
    endif
endfunction

function Fx_Say takes unit u, string s, integer red, integer grn, integer blu, unit other returns nothing
    local player plyA = GetOwningPlayer(u)
    local player plyB = plyA
    if other != null then
        set plyB = GetOwningPlayer(other)
    endif
    call Ab_Say(u, s, red, grn, blu, plyA, plyB)
    set plyA = null
    set plyB = null
endfunction

function Fx_Legend takes unit u returns integer
    return LoadInteger(Fx_HT, GetUnitTypeId(u), 3)
endfunction

function Fx_HasType takes unit u, integer ty returns boolean
    return Ty_Of(u, 0) == ty or Ty_Of(u, 1) == ty
endfunction

function Fx_DefOf takes unit u, integer which returns real
    local integer base = LoadInteger(Fx_HT, GetUnitTypeId(u), which)
    if base <= 0 then
        return 80.0
    endif
    return I2R(base)
endfunction

// ---- stat stages (-4 .. +4, each +-25%, Speed +-15%)
function Fx_StageImmune takes unit u, integer s, unit src returns boolean
    local integer abil = Ab_Num(u)
    local integer lcode = Fx_Legend(u)
    if src == null or src == u or not IsUnitEnemy(src, GetOwningPlayer(u)) then
        return false
    endif
    if abil == AB_CLEARBODY or lcode == 15 then
        return true
    endif
    if abil == AB_HYPERCUTTER and s == 1 then
        return true
    endif
    if lcode >= 1 and lcode <= 9 then  // Pressure (legend): no stat drops
        return true
    endif
    return false
endfunction

function Fx_StageAdd takes unit u, integer s, integer delta, real dur, unit src returns nothing
    local integer hand = 0
    local integer stage = 0
    local string word = ""
    if u == null or delta == 0 or not Ab_Alive(u) then
        return
    endif
    if delta < 0 and src != null and src != u and Ab_Num(u) == AB_MAGICBOUNCE and IsUnitEnemy(src, GetOwningPlayer(u)) then
        call Fx_Say(u, "Bounced!", 200, 160, 255, src)
        set u = src
        set src = null
    endif
    if delta < 0 and Fx_StageImmune(u, s, src) then
        return
    endif
    set hand = GetHandleId(u)
    set stage = LoadInteger(Fx_HT, hand, s)
    if Mega_Time >= LoadReal(Fx_HT, hand, 10 + s) then
        set stage = 0
    endif
    set stage = stage + delta
    if stage > 4 then
        set stage = 4
    elseif stage < -4 then
        set stage = -4
    endif
    call SaveInteger(Fx_HT, hand, s, stage)
    call SaveReal(Fx_HT, hand, 10 + s, Mega_Time + dur)
    call Fx_Track(u)
    if delta > 0 then
        set word = "+" + I2S(delta) + " " + Fx_StatName[s]
        call Fx_Say(u, word, 120, 255, 120, src)
    else
        set word = I2S(delta) + " " + Fx_StatName[s]
        call Fx_Say(u, word, 255, 120, 120, src)
    endif
endfunction

// stun that cannot chain forever: a second hard CC within 6s lasts half as long
function Fx_HardCC takes unit t, real dur, unit src returns nothing
    local integer hand = GetHandleId(t)
    if not Ab_Alive(t) then
        return
    endif
    if Mega_Time < LoadReal(Fx_HT, hand, 35) then
        set dur = dur * 0.5
    endif
    call SaveReal(Fx_HT, hand, 35, Mega_Time + 6.0)
    set Ab_FxCur = src
    call Ab_FxAdd(t, 3, dur, 1.0)
    set Ab_FxCur = null
endfunction

function Fx_Cure takes unit u returns nothing
    local integer hand = GetHandleId(u)
    local integer st = LoadInteger(Fx_HT, hand, 20)
    local integer slot = 0
    if st == 0 then
        return
    endif
    call SaveInteger(Fx_HT, hand, 20, 0)
    call SaveReal(Fx_HT, hand, 21, 0.0)
    if st <= 3 then
        set slot = Ab_FxFind(u, 1)
    elseif st == 4 then
        set slot = Ab_FxFind(u, 2)
        if slot >= 0 then
            call Ab_FxStop(slot)
        endif
        set slot = Ab_FxFind(u, 4)
    else
        set slot = Ab_FxFind(u, 3)
    endif
    if slot >= 0 then
        call Ab_FxStop(slot)
    endif
endfunction

// main status: 1 burn, 2 poison, 3 toxic, 4 paralysis, 5 sleep, 6 freeze. One at a time; type immunities.
function Fx_Status takes unit t, integer kind, unit src returns boolean
    local integer hand = GetHandleId(t)
    local integer abil = 0
    local real mx = 0.0
    local real dur = 6.0
    if t == null or kind <= 0 or not Ab_Alive(t) or Fx_HasStatus(t) then
        return false
    endif
    if Mega_Time < LoadReal(Fx_HT, hand, 43) and LoadReal(Fx_HT, hand, 42) > 0.0 then
        return false  // shield up (Substitute, Mewtwo)
    endif
    if Mega_Time < LoadReal(Fx_HT, hand, 61) then
        return false  // Protect
    endif
    set abil = Ab_Num(t)
    if src != null and src != t and abil == AB_MAGICBOUNCE and IsUnitEnemy(src, GetOwningPlayer(t)) then
        call Fx_Say(t, "Bounced!", 200, 160, 255, src)
        set hand = 0
        return Fx_Status(src, kind, null)
    endif
    if (kind == 1 and Fx_HasType(t, T_FIRE)) or (kind == 4 and Fx_HasType(t, T_ELECTRIC)) then
        return false
    endif
    if (kind == 2 or kind == 3) and (Fx_HasType(t, T_POISON) or Fx_HasType(t, T_STEEL)) then
        return false
    endif
    if kind == 6 and Fx_HasType(t, T_ICE) then
        return false
    endif
    if kind == 5 and abil == AB_INSOMNIA then
        return false
    endif
    set mx = I2R(BlzGetUnitMaxHP(t))
    set Ab_FxCur = src
    if kind == 1 then
        call Ab_FxAdd(t, 1, 6.0, 0.01 * mx)
        call Ab_Pop(t, "Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl", "chest")
    elseif kind == 2 then
        call Ab_FxAdd(t, 1, 6.0, 0.015 * mx)
        call Ab_Pop(t, "Abilities\\Weapons\\ChimaeraAcidMissile\\ChimaeraAcidMissile.mdl", "chest")
    elseif kind == 3 then
        set dur = 8.0
        call Ab_FxAdd(t, 1, 8.0, 0.01 * mx)
        call SaveInteger(Fx_HT, hand, 22, 0)
        call Ab_Pop(t, "Abilities\\Weapons\\ChimaeraAcidMissile\\ChimaeraAcidMissile.mdl", "chest")
    elseif kind == 4 then
        set dur = 5.0
        call Ab_FxAdd(t, 2, 5.0, 0.4)
        call Ab_FxAdd(t, 4, 5.0, 0.25)
        call Ab_Pop(t, "Abilities\\Spells\\Orc\\Purge\\PurgeBuffTarget.mdl", "chest")
    elseif kind == 5 then
        set dur = 2.0
        if abil == AB_EARLYBIRD then
            set dur = 1.0
        endif
        set Ab_FxCur = null
        call Fx_HardCC(t, dur, src)
        call Ab_Pop(t, "Abilities\\Spells\\Undead\\Sleep\\SleepTarget.mdl", "overhead")
    elseif kind == 6 then
        set dur = 1.5
        set Ab_FxCur = null
        call Fx_HardCC(t, dur, src)
        call Ab_Pop(t, "Abilities\\Spells\\Undead\\FrostNova\\FrostNovaTarget.mdl", "origin")
    endif
    set Ab_FxCur = null
    call SaveInteger(Fx_HT, hand, 20, kind)
    call SaveReal(Fx_HT, hand, 21, Mega_Time + dur)
    if src != null then
        call SaveUnitHandle(Fx_HT, hand, 23, src)
    endif
    call Fx_Track(t)
    call Fx_Say(t, Fx_StName[kind], 255, 200, 80, src)
    if abil == AB_SYNCHRONIZE and src != null and src != t and IsUnitEnemy(src, GetOwningPlayer(t)) then
        call Fx_Status(src, kind, null)
    endif
    return true
endfunction

function Fx_Confuse takes unit t, real dur, unit src returns nothing
    call SaveReal(Fx_HT, GetHandleId(t), 24, Mega_Time + dur)
    call Fx_Track(t)
    call Fx_Say(t, "Confused!", 220, 120, 255, src)
endfunction

function Fx_Silence takes unit t, real dur, unit src returns nothing
    call SaveReal(Fx_HT, GetHandleId(t), 25, Mega_Time + dur)
    call Fx_Say(t, "Silenced!", 160, 160, 255, src)
    call Ab_Pop(t, "Abilities\\Spells\\Other\\Silence\\SilenceTarget.mdl", "overhead")
endfunction

// type index of the type item a unit holds (a player's item, or the item a gym Pokemon carries), -1 = none
function Fx_HeldType takes unit u returns integer
    local integer slot = 0
    local integer lcode = 0
    local item it = null
    local integer gym = LoadInteger(Fx_HT, GetHandleId(u), 34)
    if gym > 0 then
        return gym - 1
    endif
    if not IsUnitType(u, UNIT_TYPE_HERO) then
        return -1
    endif
    loop
        exitwhen slot >= 6
        set it = UnitItemInSlot(u, slot)
        if it != null then
            set lcode = LoadInteger(Fx_HT, GetItemTypeId(it), 1)
            if lcode > 0 then
                set it = null
                return lcode - 1
            endif
        endif
        set slot = slot + 1
    endloop
    set it = null
    return -1
endfunction

// ---- damage multiplier from the engine (stages, statuses, move flags, Def / Sp. Def, held type item, legends)
function Fx_OutMult takes unit src, unit t, boolean atk, boolean skill, integer mt returns real
    local real mult = 1.0
    local integer hs = GetHandleId(src)
    local integer ht = GetHandleId(t)
    local boolean phys = atk
    local integer mkey = 0
    local integer bits = 0
    local integer lcode = Fx_Legend(src)
    local integer tcode = Fx_Legend(t)
    local real def = 80.0
    local real dm = 1.0
    local real chance = 0.25
    if skill then
        set phys = Fx_CurPhys(src) == 1
        set mkey = Fx_CurMove(src)
    endif
    // confusion / lowered accuracy: a basic attack may miss
    if atk and Mega_Time < LoadReal(Fx_HT, hs, 24) and GetRandomReal(0.0, 1.0) < 0.3 then
        if GetWidgetLife(src) - 0.03 * I2R(BlzGetUnitMaxHP(src)) > 1.0 then
            call SetWidgetLife(src, GetWidgetLife(src) - 0.03 * I2R(BlzGetUnitMaxHP(src)))
        endif
        call Fx_Say(src, "It hurt itself!", 220, 120, 255, t)
        return 0.0
    endif
    if atk and Mega_Time < LoadReal(Fx_HT, hs, 26) and Ab_Num(src) != AB_KEENEYE and GetRandomReal(0.0, 1.0) < 0.2 then
        call Fx_Say(t, "Miss", 210, 210, 210, src)
        return 0.0
    endif
    if tcode == 6 and GetRandomReal(0.0, 1.0) < 0.15 then  // Giratina: the hit passes through
        call Fx_Say(t, "Phased", 180, 120, 255, src)
        return 0.0
    endif
    if tcode == 19 and atk and GetRandomReal(0.0, 1.0) < 0.06 then  // Latias & Latios: 20% dodge in total
        call Fx_Say(t, "Miss", 210, 210, 210, src)
        return 0.0
    endif
    if Mega_Time < LoadReal(Fx_HT, ht, 61) then  // Protect / Detect
        call Fx_Say(t, "Protected", 200, 230, 255, src)
        return 0.0
    endif
    if (atk or skill) and LoadInteger(Fx_HT, hs, 65) > 0 then  // Focus Energy
        call SaveInteger(Fx_HT, hs, 65, LoadInteger(Fx_HT, hs, 65) - 1)
        if GetRandomReal(0.0, 1.0) < 0.5 then
            set mult = mult * 1.5
            call Fx_Say(t, "Critical!", 255, 80, 80, src)
        endif
    endif
    if phys and Mega_Time < LoadReal(Fx_HT, ht, 62) then  // Reflect
        set mult = mult * 0.7
    elseif skill and not phys and Mega_Time < LoadReal(Fx_HT, ht, 63) then  // Light Screen
        set mult = mult * 0.7
    endif
    // attacker
    if phys then
        set mult = mult * Fx_StageMult(src, 1)
        if Fx_StatusOf(src) == 1 and Ab_Num(src) != AB_GUTS then
            set mult = mult * 0.75
        endif
    elseif skill then
        set mult = mult * Fx_StageMult(src, 3)
    endif
    if mkey != 0 then
        set bits = LoadInteger(Fx_HT, mkey, 1)
        if ModuloInteger(bits, 2) == 1 then  // recharge moves hit harder
            set mult = mult * 1.2
        endif
        if ModuloInteger(bits / 4096, 2) == 1 then  // no extra effect: +10%
            set mult = mult * 1.1
        endif
        if ModuloInteger(bits / 16, 2) == 1 then  // high critical rate
            if Ab_Num(src) == AB_SUPERLUCK then
                set chance = 0.5
            endif
            if GetRandomReal(0.0, 1.0) < chance then
                set mult = mult * 1.5
                call Fx_Say(t, "Critical!", 255, 80, 80, src)
            endif
        endif
        if ModuloInteger(bits / 2048, 2) == 1 and Fx_HasStatus(src) then  // Facade
            set mult = mult * 2.0
        endif
        if ModuloInteger(bits / 8192, 2) == 1 and Fx_StatusOf(t) == 5 then  // Dream Eater
            set mult = mult * 2.0
        endif
        if ModuloInteger(bits / 131072, 2) == 1 and Ab_Num(src) == AB_IRONFIST then  // punching moves
            set mult = mult * 1.25
        endif
    endif
    if skill and mt >= 0 and Fx_HeldType(src) == mt then  // type item: moves of its type +20%
        set mult = mult * 1.2
    endif
    if skill then
        if (lcode == 1 or lcode == 7) and mt == T_PSYCHIC then
            if lcode == 1 then
                set mult = mult * 1.2
            else
                set mult = mult * 1.15
            endif
        elseif lcode == 6 and (mt == T_GHOST or mt == T_DRAGON) then
            set mult = mult * 1.15
        elseif lcode == 16 then
            set mult = mult * 1.1
        elseif lcode == 19 and (mt == T_DRAGON or mt == T_PSYCHIC) then
            set mult = mult * 1.2
        elseif lcode == 20 and (mt == T_DRAGON or mt == T_FLYING) then
            set mult = mult * 1.2
        endif
        if LoadInteger(Fx_HT, GetUnitTypeId(src), 4) == 4 and GetRandomReal(0.0, 1.0) < 0.2 then  // Palkia
            set mult = mult * 1.5
            call Fx_Say(t, "Critical!", 255, 80, 80, src)
        endif
    endif
    if Mega_Time < LoadReal(Fx_HT, hs, 51) and LoadInteger(Fx_HT, hs, 52) == 2 then  // legend Pressure: -1 Atk / SpA
        set mult = mult * 0.8
    endif
    if skill and Mega_Time < LoadReal(Fx_HT, hs, 47) then  // Kyogre's rain
        if mt == T_WATER and not IsUnitEnemy(src, Player(LoadInteger(Fx_HT, hs, 48) - 1)) then
            set mult = mult * 1.3
        elseif mt == T_FIRE and IsUnitEnemy(src, Player(LoadInteger(Fx_HT, hs, 48) - 1)) then
            set mult = mult * 0.5
        endif
    endif
    if skill and mt == T_WATER and Mega_Time < LoadReal(Fx_HT, hs, 49) and IsUnitEnemy(src, Player(LoadInteger(Fx_HT, hs, 50) - 1)) then
        set mult = mult * 0.5  // Groudon's sun
    endif
    // target: Defense / Sp. Defense
    if atk then
        set mult = mult / Fx_StageMult(t, 2)
    elseif skill then
        if phys then
            set def = Fx_DefOf(t, 1) * Fx_StageMult(t, 2)
        else
            set def = Fx_DefOf(t, 2) * Fx_StageMult(t, 4)
        endif
        set dm = 2.0 / (1.0 + def / 80.0)
        if dm < 0.5 then
            set dm = 0.5
        elseif dm > 1.5 then
            set dm = 1.5
        endif
        set mult = mult * dm
    endif
    return mult
endfunction

function Fx_Cap takes real x returns real
    if x > 3.0 then
        return 3.0
    endif
    return x
endfunction

// ---- held type item effects (scale with the hit). Fire / Grass work from Fx_Tick, Rock when hit.
function Fx_ItemProc takes unit src, unit t, integer ty, real dealt returns nothing
    local unit v = null
    local player po = GetOwningPlayer(src)
    if ty == T_WATER then
        set Ab_FxCur = src
        call Ab_FxAdd(t, 2, 2.5, 0.25)
        set Ab_FxCur = null
    elseif ty == T_ELECTRIC then
        if GetRandomReal(0.0, 1.0) < 0.3 then
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Orc\\Purge\\PurgeBuffTarget.mdl", GetUnitX(t), GetUnitY(t)))
            call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(t), GetUnitY(t), 350.0, null)
            loop
                set v = FirstOfGroup(Fx_AoeG)
                exitwhen v == null
                call GroupRemoveUnit(Fx_AoeG, v)
                if Ab_Alive(v) and IsUnitEnemy(v, po) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
                    call Ab_Deal(src, v, 0.4 * dealt)
                endif
            endloop
        endif
    elseif ty == T_BUG then
        if GetRandomReal(0.0, 1.0) < 0.4 then
            call Ab_Deal(src, t, 0.25 * dealt)
            call Fx_HardCC(t, 0.5, src)
        endif
    elseif ty == T_POISON then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            call Fx_Status(t, 2, src)
        endif
    elseif ty == T_ICE then
        if GetRandomReal(0.0, 1.0) < 0.15 then
            call Fx_Status(t, 6, src)
        endif
    elseif ty == T_DRAGON then
        if GetRandomReal(0.0, 1.0) < 0.15 then
            call Ab_Deal(src, t, 0.5 * dealt)
            call Fx_HardCC(t, 1.0, src)
        endif
    elseif ty == T_FIGHTING then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            call Ab_Deal(src, t, dealt)
            call Fx_HardCC(t, 0.2, src)
        endif
    elseif ty == T_DARK then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            call Fx_Silence(t, 3.0, src)
        endif
    elseif ty == T_GROUND then
        if GetRandomReal(0.0, 1.0) < 0.25 then
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Orc\\EarthQuake\\EarthQuakeTarget.mdl", GetUnitX(t), GetUnitY(t)))
            call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(t), GetUnitY(t), 300.0, null)
            loop
                set v = FirstOfGroup(Fx_AoeG)
                exitwhen v == null
                call GroupRemoveUnit(Fx_AoeG, v)
                if Ab_Alive(v) and IsUnitEnemy(v, po) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
                    call Ab_Deal(src, v, 0.5 * dealt)
                    set Ab_FxCur = src
                    call Ab_FxAdd(v, 2, 2.0, 0.4)
                    set Ab_FxCur = null
                endif
            endloop
        endif
    elseif ty == T_FAIRY then
        if GetRandomReal(0.0, 1.0) < 0.2 then
            call Fx_StageAdd(t, 1, -1, 6.0, src)
        endif
    endif
    set v = null
    set po = null
endfunction

// knock u away from (fx, fy) by dist (only onto walkable ground)
function Fx_Push takes unit u, real fromx, real fromy, real dist returns nothing
    local real ang = Atan2(GetUnitY(u) - fromy, GetUnitX(u) - fromx)
    local real nx = GetUnitX(u) + dist * Cos(ang)
    local real ny = GetUnitY(u) + dist * Sin(ang)
    if not IsTerrainPathable(nx, ny, PATHING_TYPE_WALKABILITY) then
        call SetUnitPosition(u, nx, ny)
    endif
endfunction

// ---- after a hit lands (Ab_OnDamaging): move effects, item effects, contact effects
function Fx_AfterHit takes unit src, unit t, boolean atk, boolean skill, integer mt, real dealt returns nothing
    local integer hs = GetHandleId(src)
    local integer ht = GetHandleId(t)
    local integer mkey = 0
    local integer bits = 0
    local integer serial = LoadInteger(Fx_HT, hs, 32)
    local integer grace = 1
    local integer kind = 0
    local integer chance = 0
    local integer s = 1
    local integer delta = 0
    local integer lcode = Fx_Legend(src)
    local integer tcode = Fx_Legend(t)
    local integer ty = -1
    local integer st = Fx_StatusOf(t)
    local real amount = 0.0
    if dealt <= 0.0 then
        return
    endif
    // sleep ends when hit; fire moves thaw
    if st == 5 and LoadReal(Fx_HT, ht, 21) - Mega_Time < 1.7 then
        call Fx_Cure(t)
    elseif st == 6 and skill and mt == T_FIRE then
        call Fx_Cure(t)
    endif
    if Ab_Num(src) == AB_SERENEGRACE or lcode == 16 then
        set grace = 2
    endif
    if skill then
        set mkey = Fx_CurMove(src)
    endif
    if mkey != 0 then
        set bits = LoadInteger(Fx_HT, mkey, 1)
        set kind = LoadInteger(Fx_HT, mkey, 4)
        set chance = LoadInteger(Fx_HT, mkey, 5) * grace
        if lcode == 2 and mt == T_ELECTRIC and kind == 0 then
            set kind = 4
        endif
        if lcode == 3 and mt == T_ICE and kind == 0 then
            set kind = 6
        endif
        if lcode == 4 and mt == T_FIRE and kind == 0 then
            set kind = 1
        endif
        if (lcode == 2 and mt == T_ELECTRIC) or (lcode == 3 and mt == T_ICE) or (lcode == 4 and mt == T_FIRE) then
            set chance = chance + 20
        endif
        if lcode == 21 and kind == 0 then  // Darkrai: its moves put to sleep
            set kind = 5
            set chance = 20
        endif
        if kind == 9 then  // Tri Attack
            set kind = 1
            if GetRandomInt(1, 3) == 2 then
                set kind = 4
            elseif GetRandomInt(1, 2) == 2 then
                set kind = 6
            endif
        endif
        if kind > 0 and GetRandomInt(1, 100) <= chance then
            call Fx_Status(t, kind, src)
        endif
        set chance = LoadInteger(Fx_HT, mkey, 6) * grace
        if ModuloInteger(bits / 16384, 2) == 1 then  // Fake Out: only right after entering combat
            set chance = 0
            if LoadInteger(Fx_HT, hs, 38) == serial then
                set chance = 100
            endif
        endif
        if chance > 0 and GetRandomInt(1, 100) <= chance and Ab_Num(t) != AB_INNERFOCUS and not (tcode >= 1 and tcode <= 9) then
            call Fx_HardCC(t, 0.5, src)
            call Fx_Say(t, "Flinched", 255, 220, 120, src)
        endif
        set chance = LoadInteger(Fx_HT, mkey, 8) * grace
        if chance > 0 and GetRandomInt(1, 100) <= chance then
            set s = 1
            loop
                exitwhen s > 5
                set delta = LoadInteger(Fx_HT, mkey, 20 + s)
                if delta != 0 then
                    call Fx_StageAdd(t, s, delta, 12.0, src)
                endif
                set s = s + 1
            endloop
            if LoadInteger(Fx_HT, mkey, 26) == 1 and Ab_Num(t) != AB_KEENEYE then
                call SaveReal(Fx_HT, ht, 26, Mega_Time + 4.0)
                call Fx_Say(t, "Accuracy down", 255, 120, 120, src)
            endif
        endif
        set amount = I2R(LoadInteger(Fx_HT, mkey, 3))
        if amount > 0.0 then
            call Ab_Heal(src, dealt * amount / 1000.0)
        endif
        if ModuloInteger(bits / 65536, 2) == 1 then  // Dragon Tail: pushes the target
            call Fx_Push(t, GetUnitX(src), GetUnitY(src), 300.0)
        endif
        if ModuloInteger(bits / 64, 2) == 1 then  // Wrap / Fire Spin / Whirlpool: trapped 3s, damage per second
            set Ab_FxCur = src
            call Ab_FxAdd(t, 2, 3.0, 0.9)
            call Ab_FxAdd(t, 1, 3.0, 0.01 * I2R(BlzGetUnitMaxHP(t)))
            set Ab_FxCur = null
        endif
        // once per cast: effects on the user
        if LoadInteger(Fx_HT, hs, 33) != serial then
            call SaveInteger(Fx_HT, hs, 33, serial)
            set amount = I2R(LoadInteger(Fx_HT, mkey, 2))
            if amount > 0.0 and Ab_Num(src) != AB_ROCKHEAD then
                set amount = dealt * amount / 1000.0
                if GetWidgetLife(src) - amount < 1.0 then
                    set amount = GetWidgetLife(src) - 1.0
                endif
                if amount > 0.0 then
                    call SetWidgetLife(src, GetWidgetLife(src) - amount)
                    call Fx_Say(src, "Recoil", 255, 150, 90, t)
                endif
            endif
            set chance = LoadInteger(Fx_HT, mkey, 7)
            if chance > 0 and GetRandomInt(1, 100) <= chance * grace then
                set s = 1
                loop
                    exitwhen s > 5
                    set delta = LoadInteger(Fx_HT, mkey, 10 + s)
                    if delta != 0 then
                        call Fx_StageAdd(src, s, delta, 12.0, src)
                    endif
                    set s = s + 1
                endloop
            endif
            if ModuloInteger(bits / 512, 2) == 1 then  // Explosion: the user loses half its HP
                call SetWidgetLife(src, RMaxBJ(1.0, GetWidgetLife(src) * 0.5))
            endif
            if ModuloInteger(bits / 1024, 2) == 1 and GetPlayerId(GetOwningPlayer(src)) < 12 then  // Pay Day
                call AdjustPlayerStateBJ(5 + R2I(dealt * 0.05), GetOwningPlayer(src), PLAYER_STATE_RESOURCE_GOLD)
            endif
            if ModuloInteger(bits / 128, 2) == 1 then  // U-turn / Volt Switch: jump back
                call Fx_Push(src, GetUnitX(t), GetUnitY(t), 300.0)
            endif
        endif
    endif
    // held type item
    set ty = Fx_HeldType(src)
    if ty >= 0 and (atk or (skill and mt == ty)) and Mega_Time >= LoadReal(Fx_HT, hs, 36) then
        call SaveReal(Fx_HT, hs, 36, Mega_Time + 0.4)
        call Fx_ItemProc(src, t, ty, dealt)
    endif
    // legends: Entei's attacks burn
    if atk and lcode == 10 and GetRandomReal(0.0, 1.0) < 0.2 then
        call Fx_Status(t, 1, src)
    endif
    // contact (melee basic attack) on the target
    if atk and IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then
        if Fx_HeldType(t) == T_ROCK then  // Hard Stone
            call Ab_Deal(t, src, 0.15 * dealt)
        endif
        if tcode == 2 and GetRandomReal(0.0, 1.0) < 0.3 then  // Zapdos
            call Fx_Status(src, 4, t)
        endif
    endif
endfunction

// ---- last word on the damage: Mewtwo's shield, Ho-Oh's rebirth, Regirock's Sturdy
function Fx_Final takes unit src, unit t, real d returns real
    local integer ht = GetHandleId(t)
    local integer lcode = Fx_Legend(t)
    local real mx = I2R(BlzGetUnitMaxHP(t))
    local real hp = GetWidgetLife(t)
    local real take = 0.0
    if d <= 0.0 then
        return d
    endif
    if lcode == 1 then
        if Mega_Time >= LoadReal(Fx_HT, ht, 41) and hp - d < 0.5 * mx then
            call SaveReal(Fx_HT, ht, 41, Mega_Time + 90.0)
            call SaveReal(Fx_HT, ht, 42, 0.2 * mx)
            call SaveReal(Fx_HT, ht, 43, Mega_Time + 8.0)
            call Fx_Say(t, "Psychic shield!", 200, 140, 255, src)
            call Ab_Pop(t, "Abilities\\Spells\\Human\\ManaShield\\ManaShieldCaster.mdl", "origin")
        endif
    endif
    if Mega_Time < LoadReal(Fx_HT, ht, 43) and LoadReal(Fx_HT, ht, 42) > 0.0 then  // any shield (Substitute too)
        set take = RMinBJ(d, LoadReal(Fx_HT, ht, 42))
        call SaveReal(Fx_HT, ht, 42, LoadReal(Fx_HT, ht, 42) - take)
        set d = d - take
    endif
    if d >= hp then
        if lcode == 12 and Mega_Time >= LoadReal(Fx_HT, ht, 44) then
            call SaveReal(Fx_HT, ht, 44, Mega_Time + 120.0)
            call SetWidgetLife(t, 0.4 * mx)
            call Fx_Say(t, "Rebirth!", 255, 180, 60, src)
            call Ab_Pop(t, "Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl", "origin")
            return 0.0
        endif
        if lcode == 15 and Mega_Time >= LoadReal(Fx_HT, ht, 45) then
            call SaveReal(Fx_HT, ht, 45, Mega_Time + 60.0)
            call Fx_Say(t, "Sturdy!", 220, 220, 220, src)
            if hp > 0.15 * mx then
                return hp - 0.15 * mx
            endif
            return 0.0
        endif
    endif
    return d
endfunction

// ---- cast hook (Ty_OnCast -> ExecuteFunc): the move just used, recharge, vanish, Pressure, cooldown changes
function Fx_CdTimer takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer k = GetHandleId(tm)
    local unit u = LoadUnitHandle(Fx_HT, k, 0)
    local integer abid = LoadInteger(Fx_HT, k, 1)
    local integer mvi = LoadInteger(Fx_HT, k, 2)
    local real fac = LoadReal(Fx_HT, k, 3)
    local real cd = 0.0
    local integer s = 0
    if u != null and GetUnitTypeId(u) != 0 then
        set cd = BlzGetUnitAbilityCooldownRemaining(u, abid)
        if cd > 0.0 then
            call BlzStartUnitAbilityCooldown(u, abid, cd * fac)
            if mvi >= 0 then
                loop
                    exitwhen s >= Mv_Slots
                    if Mv_Slot(u, s) == mvi then
                        call BlzStartUnitAbilityCooldown(u, Mv_Id(s, mvi), cd * fac)
                    endif
                    set s = s + 1
                endloop
            endif
        endif
    endif
    call FlushChildHashtable(Fx_HT, k)
    call DestroyTimer(tm)
    set tm = null
    set u = null
endfunction

function Fx_CdScale takes unit u, integer abid, integer mvi, real fac returns nothing
    local timer tm = CreateTimer()
    local integer k = GetHandleId(tm)
    call SaveUnitHandle(Fx_HT, k, 0, u)
    call SaveInteger(Fx_HT, k, 1, abid)
    call SaveInteger(Fx_HT, k, 2, mvi)
    call SaveReal(Fx_HT, k, 3, fac)
    call TimerStart(tm, 0.0, false, function Fx_CdTimer)
    set tm = null
endfunction

function Fx_RechargeGo takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local unit u = LoadUnitHandle(Fx_HT, GetHandleId(tm), 0)
    if u != null and Ab_Alive(u) then
        set Ab_FxCur = u
        call Ab_FxAdd(u, 3, 2.0, 1.0)
        set Ab_FxCur = null
        call Fx_Say(u, "Recharging...", 255, 220, 120, null)
    endif
    call FlushChildHashtable(Fx_HT, GetHandleId(tm))
    call DestroyTimer(tm)
    set tm = null
    set u = null
endfunction

function Fx_OnCastX takes nothing returns nothing
    local unit u = Fx_ArgU
    local integer mvi = Fx_ArgI
    local integer abid = Fx_ArgJ
    local integer hand = GetHandleId(u)
    local integer mkey = 0
    local integer bits = 0
    local integer serial = 0
    local integer tier = 0
    local integer lvl = 0
    local real fac = 1.0
    local timer tm = null
    local integer lcode = Fx_Legend(u)
    local unit tgt0 = Fx_ArgV
    if mvi >= Fx_StatBase and GetPlayerId(GetOwningPlayer(u)) >= 12 then  // v3.4.13: an AI status move button
        set Fx_ArgU = u
        set Fx_ArgI = mvi
        set Fx_ArgV = tgt0
        call ExecuteFunc("Fx_StatusMoveX")
        set u = null
        set tgt0 = null
        return
    endif
    set tgt0 = null
    if mvi >= 0 and Mv_OfReal(abid) < 0 then  // the slot button: the hidden spell that follows is the real cast
        set u = null
        return
    endif
    // Pressure of a nearby enemy: the move costs its mana again and cools down slower
    if Mega_Time < LoadReal(Fx_HT, hand, 51) then
        set tier = LoadInteger(Fx_HT, hand, 52)
        set lvl = GetUnitAbilityLevel(u, abid)
        if lvl > 0 then
            call SetUnitState(u, UNIT_STATE_MANA, RMaxBJ(0.0, GetUnitState(u, UNIT_STATE_MANA) - I2R(BlzGetUnitAbilityManaCost(u, abid, lvl - 1))))
        endif
        if tier == 1 then
            set fac = 1.2
        else
            set fac = 1.3
        endif
    endif
    if lcode == 8 then  // Dialga
        set fac = fac * 0.75
    elseif lcode == 7 then  // Deoxys
        set fac = fac * 0.85
    endif
    if fac < 0.99 or fac > 1.01 then
        call Fx_CdScale(u, abid, mvi, fac)
    endif
    if mvi >= 0 then
        set mkey = 100000 + mvi
    elseif LoadInteger(Fx_HT, abid, 30) > 0 then
        set mkey = abid
    endif
    if mkey == 0 then
        set u = null
        return
    endif
    set serial = LoadInteger(Fx_HT, hand, 32) + 1
    call SaveInteger(Fx_HT, hand, 32, serial)
    call SaveInteger(Fx_HT, hand, 30, mkey)
    call SaveReal(Fx_HT, hand, 31, Mega_Time)
    if Mega_Time - LoadReal(Ab_HT, hand, 60) > 8.0 then
        call SaveInteger(Fx_HT, hand, 38, serial)  // Fake Out works
    endif
    set bits = LoadInteger(Fx_HT, mkey, 1)
    if ModuloInteger(bits, 2) == 1 then  // recharge: after the cast (channelled moves: when the channel ends)
        if ModuloInteger(bits / 16777216, 2) == 1 then
            call SaveInteger(Fx_HT, hand, 39, abid)
        else
            set tm = CreateTimer()
            call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, u)
            call TimerStart(tm, 0.6, false, function Fx_RechargeGo)
        endif
    endif
    if ModuloInteger(bits / 4, 2) == 1 then  // Dig / Fly: out of reach for a moment
        set Ab_FxCur = u
        call Ab_FxAdd(u, 7, 1.0, 1.0)
        set Ab_FxCur = null
    endif
    if ModuloInteger(bits / 4194304, 2) == 1 then  // Meteor Beam
        call Fx_StageAdd(u, 3, 1, 12.0, u)
    endif
    if ModuloInteger(bits / 32768, 2) == 1 then  // Outrage / Thrash / Petal Dance
        call Fx_Confuse(u, 3.0, u)
    endif
    set u = null
    set tm = null
endfunction

// EVENT_PLAYER_UNIT_SPELL_ENDCAST: a channelled recharge move (Blast Burn, Frenzy Plant) ended -> rest now
function Fx_OnEndCast takes nothing returns boolean
    local unit u = GetTriggerUnit()
    local integer hand = GetHandleId(u)
    if LoadInteger(Fx_HT, hand, 39) != 0 and LoadInteger(Fx_HT, hand, 39) == GetSpellAbilityId() then
        call SaveInteger(Fx_HT, hand, 39, 0)
        if Ab_Alive(u) then
            set Ab_FxCur = u
            call Ab_FxAdd(u, 3, 2.0, 1.0)
            set Ab_FxCur = null
            call Fx_Say(u, "Recharging...", 255, 220, 120, null)
        endif
    endif
    set u = null
    return false
endfunction

// Ab_InContact / Ab_OnHit / Intimidate (earlier code) apply statuses and stages through these
function Fx_StatusX takes nothing returns nothing
    if GetRandomInt(1, 100) <= Fx_ArgJ then
        call Fx_Status(Fx_ArgU, Fx_ArgI, Fx_ArgV)
    endif
endfunction

function Fx_IntimidateX takes nothing returns nothing
    local unit v = Fx_ArgU
    if Ab_Num(v) == AB_INNERFOCUS then
        call Fx_Say(v, "Unshaken", 200, 200, 200, Fx_ArgV)
    else
        call Fx_StageAdd(v, 1, -1, 8.0, Fx_ArgV)
    endif
    set v = null
endfunction

// EVENT_PLAYER_UNIT_SPELL_CAST: a silenced unit cannot cast
function Fx_OnSpellCast takes nothing returns boolean
    local unit u = GetTriggerUnit()
    if Fx_Silenced(u) then
        call IssueImmediateOrder(u, "stop")
        call Fx_Say(u, "Silenced!", 160, 160, 255, null)
    elseif Mega_Time < LoadReal(Fx_HT, GetHandleId(u), 66) and Ty_MoveOf(GetSpellAbilityId()) >= Fx_StatBase then
        call IssueImmediateOrder(u, "stop")  // Taunt: no status moves
        call Fx_Say(u, "Taunted!", 255, 120, 120, null)
    endif
    set u = null
    return false
endfunction

// ---- gym / Elite Four Pokemon carry the abilities of their type item (no real item: nothing to drop or trigger)
function Fx_GymItemX takes nothing returns nothing
    local unit u = Fx_ArgU
    local integer ty = Fx_ArgI
    local integer g = Fx_ArgJ
    local integer n = 0
    local integer k = 0
    if u == null or ty < 0 then
        set u = null
        return
    endif
    set n = LoadInteger(Fx_HT, 200000 + ty, 2)
    if g < 4 then  // gyms 1-4: only the +20% damage
        call UnitAddAbility(u, 'A03A')
    else
        loop
            exitwhen k >= n
            call UnitAddAbility(u, LoadInteger(Fx_HT, 200000 + ty, 10 + k))
            set k = k + 1
        endloop
        call SaveInteger(Fx_HT, GetHandleId(u), 34, ty + 1)
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) and Fx_TItemName[ty] != null and Fx_TItemName[ty] != "" then
        call BlzSetHeroProperName(u, GetHeroProperName(u) + " (" + Fx_TItemName[ty] + ")")
    endif
    set u = null
endfunction

// ---- one of each held item: a second copy is refunded (bought) or dropped (picked up / given)
function Fx_OnSell takes nothing returns boolean
    call SaveInteger(Fx_HT, GetHandleId(GetSoldItem()), 1, 1)
    return false
endfunction

function Fx_PickupGo takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer k = GetHandleId(tm)
    local unit u = LoadUnitHandle(Fx_HT, k, 0)
    local item it = LoadItemHandle(Fx_HT, k, 1)
    local integer id = 0
    local integer slot = 0
    local integer cnt = 0
    local player po = null
    if u != null and it != null and UnitHasItem(u, it) then
        set id = GetItemTypeId(it)
        loop
            exitwhen slot >= 6
            if GetItemTypeId(UnitItemInSlot(u, slot)) == id then
                set cnt = cnt + 1
            endif
            set slot = slot + 1
        endloop
        if cnt > 1 then
            set po = GetOwningPlayer(u)
            if LoadInteger(Fx_HT, GetHandleId(it), 1) == 1 then
                call AdjustPlayerStateBJ(LoadInteger(Fx_HT, id, 3), po, PLAYER_STATE_RESOURCE_GOLD)
                call RemoveItem(it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffffcc00You already hold this item: gold refunded.|r")
            else
                call UnitRemoveItem(u, it)
                call DisplayTimedTextToPlayer(po, 0, 0, 6.0, "|cffffcc00You already hold this item.|r")
            endif
            call Itm_Refresh(u)
        endif
    endif
    call FlushChildHashtable(Fx_HT, k)
    call DestroyTimer(tm)
    set tm = null
    set u = null
    set it = null
    set po = null
endfunction

function Fx_OnPickup takes unit u, item it returns nothing
    local timer tm = null
    if it == null or LoadInteger(Fx_HT, GetItemTypeId(it), 2) != 1 or not IsUnitType(u, UNIT_TYPE_HERO) then
        return
    endif
    set tm = CreateTimer()
    call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, u)
    call SaveItemHandle(Fx_HT, GetHandleId(tm), 1, it)
    call TimerStart(tm, 0.0, false, function Fx_PickupGo)
    set tm = null
endfunction

// ---- Pokemon League in Darkrai's room: no PvP into the battle, a queue, the lobby, portals
function Fx_LeagueBlock takes unit src, unit t returns boolean
    local integer ps = GetPlayerId(GetOwningPlayer(src))
    local integer pt = GetPlayerId(GetOwningPlayer(t))
    if League_Pid < 0 or ps >= 12 or pt >= 12 or ps == pt then
        return false
    endif
    if ps != League_Pid and pt != League_Pid then
        return false
    endif
    if Mega_Time >= Fx_LWarn[ps] then
        set Fx_LWarn[ps] = Mega_Time + 4.0
        if ps == League_Pid then
            call DisplayTimedTextToPlayer(Player(ps), 0, 0, 4.0, "|cffffcc00You are battling the Elite Four: no PvP.|r")
        else
            call DisplayTimedTextToPlayer(Player(ps), 0, 0, 4.0, "|cffffcc00That player is battling the Elite Four: no PvP.|r")
        endif
    endif
    return true
endfunction

function Fx_LeagueQueueX takes nothing returns nothing
    local integer pid = Fx_ArgI
    local integer k = 0
    loop
        exitwhen k >= Fx_LQN
        if Fx_LQ[k] == pid then
            call DisplayTimedTextToPlayer(Player(pid), 0, 0, 6.0, "|cffffcc00Pokemon League: you are number " + I2S(k + 1) + " in the queue.|r")
            return
        endif
        set k = k + 1
    endloop
    set Fx_LQ[Fx_LQN] = pid
    set Fx_LQN = Fx_LQN + 1
    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 8.0, "|cffffcc00Pokemon League is busy: you are number " + I2S(Fx_LQN) + " in the queue. You go in automatically when it is your turn.|r")
endfunction

function Fx_LeagueNextGo takes nothing returns nothing
    local integer pid = -1
    local integer k = 0
    call DestroyTimer(GetExpiredTimer())
    if League_Pid >= 0 then
        return
    endif
    loop
        exitwhen Fx_LQN <= 0 or pid >= 0
        set pid = Fx_LQ[0]
        set k = 0
        loop
            exitwhen k >= Fx_LQN - 1
            set Fx_LQ[k] = Fx_LQ[k + 1]
            set k = k + 1
        endloop
        set Fx_LQN = Fx_LQN - 1
        if GetPlayerSlotState(Player(pid)) != PLAYER_SLOT_STATE_PLAYING or Gym_Busy(pid) then
            set pid = -1
        endif
    endloop
    if pid >= 0 then
        call League_Start(pid)
    endif
endfunction

function Fx_LeagueNextX takes nothing returns nothing
    call TimerStart(CreateTimer(), 3.0, false, function Fx_LeagueNextGo)
endfunction

function Fx_Label takes string s, real x, real y, integer red, integer grn, integer blu returns nothing
    local texttag tt = CreateTextTag()
    call SetTextTagText(tt, s, 0.024)
    call SetTextTagPos(tt, x - 60.0, y, 220.0)
    call SetTextTagColor(tt, red, grn, blu, 255)
    call SetTextTagPermanent(tt, true)
    call SetTextTagVisibility(tt, true)
    set tt = null
endfunction

function Fx_PortalAt takes real x, real y, boolean toBase returns nothing
    local unit u = null
    local player po = null
    local real tx = Fx_LLX
    local real ty = Fx_LLY
    call GroupEnumUnitsInRange(Fx_TmpG, x, y, 80.0, null)
    loop
        set u = FirstOfGroup(Fx_TmpG)
        exitwhen u == null
        call GroupRemoveUnit(Fx_TmpG, u)
        set po = GetOwningPlayer(u)
        if GetPlayerId(po) < 12 and IsUnitType(u, UNIT_TYPE_HERO) and Ab_Alive(u) and Mega_Time >= LoadReal(Fx_HT, GetHandleId(u), 60) and GetPlayerId(po) != League_Pid then
            call SaveReal(Fx_HT, GetHandleId(u), 60, Mega_Time + 3.0)
            if toBase then
                set tx = GetStartLocationX(GetPlayerStartLocation(po))
                set ty = GetStartLocationY(GetPlayerStartLocation(po))
            else
                set tx = Fx_LLX
                set ty = Fx_LLY
                call DisplayTimedTextToPlayer(po, 0, 0, 8.0, "|cffffcc00Pokemon League: walk into the arena circle with 8 badges (or type -league). The Exit portal leads back to your base.|r")
            endif
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportCaster.mdl", GetUnitX(u), GetUnitY(u)))
            call SetUnitPosition(u, tx, ty)
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", tx, ty))
            call PanCameraToTimedForPlayer(po, tx, ty, 0.3)
        endif
    endloop
    set u = null
    set po = null
endfunction

function Fx_LeagueTick takes nothing returns nothing
    local unit u = null
    local integer pid = 0
    call Fx_PortalAt(Fx_GateX[0], Fx_GateY[0], false)
    call Fx_PortalAt(Fx_GateX[1], Fx_GateY[1], false)
    call Fx_PortalAt(Fx_LEX, Fx_LEY, true)
    call GroupEnumUnitsInRange(Fx_TmpG, Fx_LAX, Fx_LAY, 1160.0, null)
    loop
        set u = FirstOfGroup(Fx_TmpG)
        exitwhen u == null
        call GroupRemoveUnit(Fx_TmpG, u)
        set pid = GetPlayerId(GetOwningPlayer(u))
        if pid < 12 and IsUnitType(u, UNIT_TYPE_HERO) and Ab_Alive(u) then
            if League_Pid >= 0 and pid != League_Pid then
                call SetUnitPosition(u, Fx_LLX, Fx_LLY)
                if Mega_Time >= Fx_LWarn[pid] then
                    set Fx_LWarn[pid] = Mega_Time + 4.0
                    call DisplayTimedTextToPlayer(Player(pid), 0, 0, 5.0, "|cffffcc00Pokemon League: " + GetPlayerName(Player(League_Pid)) + " is battling. Wait in the lobby (-league to queue).|r")
                endif
            elseif League_Pid < 0 and IsUnitInRange(u, Fx_LCenter, 350.0) then
                if Mega_Time >= Gym_Warn[pid] then
                    set Gym_Warn[pid] = Mega_Time + 8.0
                    call League_Start(pid)
                endif
            endif
        endif
    endloop
    set u = null
endfunction

// the challenger who goes down in the League gets up in the lobby (not at the base)
function Fx_LobbyRevive takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local unit u = LoadUnitHandle(Fx_HT, GetHandleId(tm), 0)
    if u != null and GetUnitTypeId(u) != 0 and not Ab_Alive(u) and IsUnitType(u, UNIT_TYPE_HERO) then
        call ReviveHero(u, Fx_LLX, Fx_LLY, true)
        call PanCameraToTimedForPlayer(GetOwningPlayer(u), Fx_LLX, Fx_LLY, 0.3)
    endif
    call FlushChildHashtable(Fx_HT, GetHandleId(tm))
    call DestroyTimer(tm)
    set tm = null
    set u = null
endfunction

function Fx_OnDeath takes nothing returns boolean
    local unit d = GetDyingUnit()
    local unit killer = GetKillingUnit()
    local timer tm = null
    local integer mkey = 0
    if d == League_Unit and League_Pid >= 0 and IsUnitType(d, UNIT_TYPE_HERO) then
        set tm = CreateTimer()
        call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, d)
        call TimerStart(tm, 3.5, false, function Fx_LobbyRevive)
    endif
    if killer != null and killer != d and IsUnitEnemy(d, GetOwningPlayer(killer)) then
        if Fx_Legend(killer) == 17 then  // Buzzwole: Beast Boost
            call Fx_StageAdd(killer, 1, 1, 30.0, killer)
        endif
        set mkey = Fx_CurMove(killer)
        if mkey != 0 and ModuloInteger(LoadInteger(Fx_HT, mkey, 1) / 8388608, 2) == 1 then  // Fell Stinger
            call Fx_StageAdd(killer, 1, 3, 12.0, killer)
        endif
    endif
    set d = null
    set killer = null
    set tm = null
    return false
endfunction

// ---- -tp: back to the base and fully healed after 3s (not in a gym or League battle), every 60s
function Fx_TpGo takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local unit u = LoadUnitHandle(Fx_HT, GetHandleId(tm), 0)
    local player po = null
    local real x = 0.0
    local real y = 0.0
    if u != null and Ab_Alive(u) then
        set po = GetOwningPlayer(u)
        if Gym_Busy(GetPlayerId(po)) or League_Pid == GetPlayerId(po) then
            call DisplayTimedTextToPlayer(po, 0, 0, 5.0, "|cffff4040-tp cancelled: you are in a battle.|r")
        else
            set x = GetStartLocationX(GetPlayerStartLocation(po))
            set y = GetStartLocationY(GetPlayerStartLocation(po))
            call SetUnitPosition(u, x, y)
            call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
            call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
            call Fx_Cure(u)
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", x, y))
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
            call PanCameraToTimedForPlayer(po, x, y, 0.3)
        endif
    endif
    call FlushChildHashtable(Fx_HT, GetHandleId(tm))
    call DestroyTimer(tm)
    set tm = null
    set u = null
    set po = null
endfunction

function Fx_TpChat takes nothing returns nothing
    local player po = GetTriggerPlayer()
    local integer pid = GetPlayerId(po)
    local unit u = League_Hero(pid)
    local timer tm = null
    if u == null then
        call DisplayTimedTextToPlayer(po, 0, 0, 5.0, "|cffffcc00-tp: you need a living Pokemon.|r")
    elseif Gym_Busy(pid) or League_Pid == pid then
        call DisplayTimedTextToPlayer(po, 0, 0, 5.0, "|cffff4040-tp does not work during a gym or League battle.|r")
    elseif Mega_Time < Fx_TpReady[pid] then
        call DisplayTimedTextToPlayer(po, 0, 0, 5.0, "|cffffcc00-tp: ready again in " + I2S(R2I(Fx_TpReady[pid] - Mega_Time + 0.99)) + "s.|r")
    else
        set Fx_TpReady[pid] = Mega_Time + 60.0
        call DisplayTimedTextToPlayer(po, 0, 0, 3.0, "|cffffcc00-tp: back to your base and healed in 3 seconds...|r")
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportCaster.mdl", u, "origin"))
        set tm = CreateTimer()
        call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, u)
        call TimerStart(tm, 3.0, false, function Fx_TpGo)
    endif
    set po = null
    set u = null
    set tm = null
endfunction

// ---- every 0.5s: statuses (toxic grows, Shed Skin, Natural Cure); every 1s: auras (Pressure, rain / sun of
// Kyogre / Groudon, Bad Dreams, Regenerator, Speed Boost, Slow Start, Charcoal, Miracle Seed)
// ---- v3.4.12: the 58 status moves (Fx_HT[100000 + move] key 40 = action, see tools/v3411/status_moves.py)
function Fx_StageSet5 takes unit u, integer mkey, integer base, unit src returns nothing
    local integer s = 1
    local integer delta = 0
    loop
        exitwhen s > 5
        set delta = LoadInteger(Fx_HT, mkey, base + s)
        if delta != 0 then
            call Fx_StageAdd(u, s, delta, 12.0, src)
        endif
        set s = s + 1
    endloop
endfunction

function Fx_WishGo takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer k = GetHandleId(tm)
    local real x = LoadReal(Fx_HT, k, 1)
    local real y = LoadReal(Fx_HT, k, 2)
    local player po = Player(LoadInteger(Fx_HT, k, 3))
    local unit v = null
    local unit best = null
    local real low = 2.0
    call GroupEnumUnitsInRange(Fx_TmpG, x, y, 250.0, null)
    loop
        set v = FirstOfGroup(Fx_TmpG)
        exitwhen v == null
        call GroupRemoveUnit(Fx_TmpG, v)
        if Ab_Alive(v) and not IsUnitEnemy(v, po) and GetWidgetLife(v) / I2R(BlzGetUnitMaxHP(v)) < low then
            set low = GetWidgetLife(v) / I2R(BlzGetUnitMaxHP(v))
            set best = v
        endif
    endloop
    if best != null then
        call Ab_Heal(best, 0.5 * I2R(BlzGetUnitMaxHP(best)))
        call Ab_Pop(best, "Abilities\\Spells\\Human\\HolyBolt\\HolyBoltSpecialArt.mdl", "origin")
    endif
    call FlushChildHashtable(Fx_HT, k)
    call DestroyTimer(tm)
    set tm = null
    set po = null
    set v = null
    set best = null
endfunction

function Fx_YawnGo takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer k = GetHandleId(tm)
    local unit t = LoadUnitHandle(Fx_HT, k, 0)
    if t != null and Ab_Alive(t) then
        call Fx_Status(t, 5, LoadUnitHandle(Fx_HT, k, 1))
    endif
    call FlushChildHashtable(Fx_HT, k)
    call DestroyTimer(tm)
    set tm = null
    set t = null
endfunction

function Fx_DoStatusMove takes unit u, integer mvi, unit tgt returns nothing
    local integer mkey = 100000 + mvi
    local integer act = LoadInteger(Fx_HT, mkey, 40)
    local integer hand = GetHandleId(u)
    local player po = GetOwningPlayer(u)
    local real mx = I2R(BlzGetUnitMaxHP(u))
    local real amount = 0.0
    local unit v = null
    local timer tm = null
    local integer kind = 0
    local integer immune = 0
    if act == 0 or not Ab_Alive(u) then
        set po = null
        return
    endif
    if act >= 21 and (tgt == null or not Ab_Alive(tgt) or not IsUnitEnemy(tgt, po)) then
        set po = null
        return
    endif
    call Fx_Say(u, Fx_SName[mvi - Fx_StatBase], 170, 220, 255, tgt)
    if act == 1 or act == 2 then
        call Fx_StageSet5(u, mkey, 10, u)
        if act == 2 and Wth_Cur == 2 then
            call Fx_StageSet5(u, mkey, 10, u)
        endif
        call Ab_Pop(u, "Abilities\\Spells\\NightElf\\BattleRoar\\RoarCaster.mdl", "origin")
    elseif act == 3 then
        call SaveInteger(Fx_HT, hand, 65, 3)
        call Ab_Pop(u, "Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", "overhead")
    elseif act == 4 then
        if GetWidgetLife(u) > 0.5 * mx + 1.0 then
            call SetWidgetLife(u, GetWidgetLife(u) - 0.5 * mx)
            call Fx_StageAdd(u, 1, 4, 12.0, u)
        else
            call Fx_Say(u, "But it failed!", 200, 200, 200, null)
        endif
    elseif act == 5 then
        call SaveReal(Fx_HT, hand, 61, Mega_Time + 1.5)
        call Ab_Pop(u, "Abilities\\Spells\\Human\\DivineShield\\DivineShieldTarget.mdl", "origin")
    elseif act == 6 or act == 7 then
        set amount = I2R(LoadInteger(Fx_HT, mkey, 42)) / 1000.0
        if act == 7 then
            set amount = 0.5
            if Wth_Cur == 2 then
                set amount = 0.66
            elseif Wth_Cur > 0 then
                set amount = 0.25
            endif
        endif
        call Ab_Heal(u, amount * mx)
        call Ab_Pop(u, "Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", "origin")
    elseif act == 8 then
        call SetWidgetLife(u, mx)
        call Fx_Cure(u)
        set Ab_FxCur = u
        call Ab_FxAdd(u, 3, 3.0, 1.0)
        set Ab_FxCur = null
        call SaveInteger(Fx_HT, hand, 20, 5)
        call SaveReal(Fx_HT, hand, 21, Mega_Time + 3.0)
        call Fx_Track(u)
        call Ab_Pop(u, "Abilities\\Spells\\Undead\\Sleep\\SleepTarget.mdl", "overhead")
    elseif act == 9 or act == 10 then
        call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(u), GetUnitY(u), 600.0, null)
        loop
            set v = FirstOfGroup(Fx_AoeG)
            exitwhen v == null
            call GroupRemoveUnit(Fx_AoeG, v)
            if Ab_Alive(v) and not IsUnitEnemy(v, po) then
                call SaveReal(Fx_HT, GetHandleId(v), 53 + act, Mega_Time + 8.0)
            endif
        endloop
        call Ab_Pop(u, "Abilities\\Spells\\Human\\Defend\\DefendCaster.mdl", "origin")
    elseif act == 11 then
        if GetWidgetLife(u) > 0.25 * mx + 1.0 then
            call SetWidgetLife(u, GetWidgetLife(u) - 0.25 * mx)
            call SaveReal(Fx_HT, hand, 42, 0.25 * mx)
            call SaveReal(Fx_HT, hand, 43, Mega_Time + 10.0)
            call Ab_Pop(u, "Abilities\\Spells\\Human\\ManaShield\\ManaShieldCaster.mdl", "origin")
        else
            call Fx_Say(u, "But it failed!", 200, 200, 200, null)
        endif
    elseif act == 12 then
        call SaveReal(Fx_HT, hand, 64, Mega_Time + 12.0)
        call Fx_Track(u)
        call Ab_Pop(u, "Abilities\\Spells\\Other\\ANrl\\ANrlTarget.mdl", "origin")
    elseif act == 13 then
        set tm = CreateTimer()
        call SaveReal(Fx_HT, GetHandleId(tm), 1, GetUnitX(u))
        call SaveReal(Fx_HT, GetHandleId(tm), 2, GetUnitY(u))
        call SaveInteger(Fx_HT, GetHandleId(tm), 3, GetPlayerId(po))
        call TimerStart(tm, 2.0, false, function Fx_WishGo)
    elseif act == 20 then
        call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(u), GetUnitY(u), 500.0, null)
        loop
            set v = FirstOfGroup(Fx_AoeG)
            exitwhen v == null
            call GroupRemoveUnit(Fx_AoeG, v)
            if Ab_Alive(v) and IsUnitEnemy(v, po) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
                call Fx_StageSet5(v, mkey, 20, u)
            endif
        endloop
        call Ab_Pop(u, "Abilities\\Spells\\Other\\HowlOfTerror\\HowlCaster.mdl", "origin")
    elseif act == 21 then
        call Fx_StageSet5(tgt, mkey, 20, u)
    elseif act == 22 then
        if Ab_Num(tgt) != AB_KEENEYE then
            call SaveReal(Fx_HT, GetHandleId(tgt), 26, Mega_Time + 6.0)
            call Fx_Say(tgt, "Accuracy down", 255, 120, 120, u)
        endif
    elseif act == 23 then
        set kind = LoadInteger(Fx_HT, mkey, 42)
        set immune = LoadInteger(Fx_HT, mkey, 44)
        if (immune == 1 and Fx_HasType(tgt, T_GRASS)) or (immune == 2 and Fx_HasType(tgt, T_GROUND)) then
            call Fx_Say(tgt, "No effect", 200, 200, 200, u)
        elseif GetRandomInt(1, 100) <= LoadInteger(Fx_HT, mkey, 43) then
            call Fx_Status(tgt, kind, u)
        else
            call Fx_Say(tgt, "Missed", 210, 210, 210, u)
        endif
    elseif act == 24 then
        set tm = CreateTimer()
        call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, tgt)
        call SaveUnitHandle(Fx_HT, GetHandleId(tm), 1, u)
        call TimerStart(tm, 2.0, false, function Fx_YawnGo)
        call Fx_Say(tgt, "Drowsy...", 200, 200, 255, u)
    elseif act == 25 or act == 26 then
        call Fx_Confuse(tgt, 4.0, u)
        if act == 26 then
            call Fx_StageAdd(tgt, 1, 2, 12.0, null)
        endif
    elseif act == 27 then
        if Fx_HasType(tgt, T_GRASS) then
            call Fx_Say(tgt, "No effect", 200, 200, 200, u)
        else
            call SaveReal(Fx_HT, GetHandleId(tgt), 67, Mega_Time + 8.0)
            call SaveUnitHandle(Fx_HT, GetHandleId(tgt), 68, u)
            call Fx_Track(tgt)
            call Ab_Pop(tgt, "Abilities\\Spells\\NightElf\\EntanglingRoots\\EntanglingRootsTarget.mdl", "origin")
        endif
    elseif act == 28 then
        call SaveReal(Fx_HT, GetHandleId(tgt), 66, Mega_Time + 4.0)
        call Fx_Say(tgt, "Taunted!", 255, 120, 120, u)
    endif
    set po = null
    set v = null
    set tm = null
endfunction

// a status move button was cast (Mv_OnCast -> ExecuteFunc)
function Fx_StatusMoveX takes nothing returns nothing
    call Fx_DoStatusMove(Fx_ArgU, Fx_ArgI, Fx_ArgV)
endfunction

// learnsets of the status moves (level list: Ab_HT keys 99 / 100 + 2k / 101 + 2k; TM list: 299 / 300 + k)
function Fx_AddLv takes integer uid, integer mvi, integer lvl returns nothing
    local integer n = LoadInteger(Ab_HT, uid, 99)
    if 101 + 2 * n < 299 then
        call SaveInteger(Ab_HT, uid, 100 + 2 * n, mvi)
        call SaveInteger(Ab_HT, uid, 101 + 2 * n, lvl)
        call SaveInteger(Ab_HT, uid, 99, n + 1)
    endif
endfunction

function Fx_AddTm takes integer uid, integer mvi returns nothing
    local integer n = LoadInteger(Ab_HT, uid, 299)
    call SaveInteger(Ab_HT, uid, 300 + n, mvi)
    call SaveInteger(Ab_HT, uid, 299, n + 1)
endfunction

// v3.4.13: an elite / gym / Elite Four / legend Pokemon gets the button of its status move in place of one of its
// 5 kit skills (no extra slot); Fx_AiStatus presses it. Called from Wild_MakeElite / Ai_GiveKit / Gym_Spawn.
function Fx_KitStatusX takes nothing returns nothing
    local unit u = Fx_ArgU
    local integer kt = Fx_ArgK
    local integer g = Fx_ArgJ
    local integer mvi = -1
    local integer drop = 0
    if u == null or kt < 0 or kt > 17 then
        set u = null
        return
    endif
    set mvi = Fx_AiMove[kt]
    if g >= 0 and g < 4 then
        set mvi = Fx_AiEasy[kt]
    endif
    if mvi < Fx_StatBase then
        set u = null
        return
    endif
    set drop = Fx_KitDrop[kt]
    if drop == 0 then
        set drop = Wild_KitSkill[kt * 5 + 4]
    endif
    if drop != 0 then
        call UnitRemoveAbility(u, drop)
    endif
    call UnitAddAbility(u, Mv_Id(3, mvi))
    call SaveInteger(Fx_HT, GetHandleId(u), 71, mvi + 1)
    set u = null
endfunction

// AI of elites, gym Pokemon, the Elite Four and legends: their status move, by simple rules
function Fx_AiStatus takes unit u returns nothing
    local integer hand = GetHandleId(u)
    local integer kit = LoadInteger(Ab_HT, hand, 87) - 1
    local integer mvi = -1
    local integer act = 0
    local integer g = 0
    local integer foes = 0
    local unit tgt = LoadUnitHandle(Ab_HT, hand, 86)
    local unit v = null
    local real ratio = GetWidgetLife(u) / I2R(BlzGetUnitMaxHP(u))
    local boolean ok = false
    local boolean easy = false
    if kit < 0 or Mega_Time < LoadReal(Fx_HT, hand, 70) or Mega_Time - LoadReal(Ab_HT, hand, 60) > 3.0 or Fx_Silenced(u) then
        set tgt = null
        return
    endif
    loop
        exitwhen g > 3
        if Gym_Cur[g] == u then
            set easy = true
        endif
        set g = g + 1
    endloop
    set mvi = Fx_AiMove[kit]
    if easy then
        set mvi = Fx_AiEasy[kit]
    endif
    if LoadInteger(Fx_HT, hand, 71) > 0 then  // v3.4.13: the move on its button
        set mvi = LoadInteger(Fx_HT, hand, 71) - 1
    endif
    if mvi < Fx_StatBase then
        set tgt = null
        return
    endif
    set act = LoadInteger(Fx_HT, 100000 + mvi, 40)
    call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(u), GetUnitY(u), 600.0, null)
    loop
        set v = FirstOfGroup(Fx_AoeG)
        exitwhen v == null
        call GroupRemoveUnit(Fx_AoeG, v)
        if Ab_Alive(v) and IsUnitEnemy(v, GetOwningPlayer(u)) and IsUnitType(v, UNIT_TYPE_HERO) then
            set foes = foes + 1
        endif
    endloop
    if act == 6 or act == 7 or act == 12 then
        set ok = ratio < 0.4
    elseif act <= 4 then
        set ok = ratio > 0.5
    elseif act == 5 then
        set ok = ratio < 0.3 and foes >= 2
    elseif act == 9 or act == 10 then
        set ok = foes >= 2
    elseif act >= 20 then
        set ok = tgt != null and Ab_Alive(tgt) and IsUnitInRange(tgt, u, 600.0) and not Fx_HasStatus(tgt)
    endif
    if ok and GetUnitAbilityLevel(u, Mv_Id(3, mvi)) > 0 then  // v3.4.13: press the button (cast animation, cooldown)
        if BlzGetUnitAbilityCooldownRemaining(u, Mv_Id(3, mvi)) > 0.0 then
            set ok = false
        elseif Mv_TT[mvi] == 1 then
            set ok = IssueTargetOrderById(u, Mv_SlotOrd[3], tgt)
        else
            set ok = IssueImmediateOrderById(u, Mv_SlotOrd[3])
        endif
        if ok then
            call SaveReal(Fx_HT, hand, 70, Mega_Time + 20.0)
        else
            call SaveReal(Fx_HT, hand, 70, Mega_Time + 2.0)
        endif
    elseif ok then
        call Fx_DoStatusMove(u, mvi, tgt)
        call SaveReal(Fx_HT, hand, 70, Mega_Time + 20.0)
    else
        call SaveReal(Fx_HT, hand, 70, Mega_Time + 2.0)
    endif
    set tgt = null
    set v = null
endfunction

function Fx_ScanFilter takes nothing returns boolean
    local unit u = GetFilterUnit()
    local boolean ok = Ab_Alive(u) and (IsUnitType(u, UNIT_TYPE_HERO) or LoadInteger(Fx_HT, GetUnitTypeId(u), 3) > 0 or LoadInteger(Ab_HT, GetHandleId(u), 87) > 0)
    set u = null
    return ok
endfunction

function Fx_AuraOf takes unit u returns nothing
    local integer hand = GetHandleId(u)
    local integer lcode = Fx_Legend(u)
    local integer tier = LoadInteger(Fx_HT, GetUnitTypeId(u), 4)
    local integer abil = Ab_Num(u)
    local integer ty = Fx_HeldType(u)
    local player po = GetOwningPlayer(u)
    local unit v = null
    local real rad = 800.0
    local real mx = I2R(BlzGetUnitMaxHP(u))
    local boolean fight = Mega_Time - LoadReal(Ab_HT, hand, 60) < 5.0
    if tier == 0 and abil == AB_PRESSURE then
        set tier = 1
        set rad = 600.0
    endif
    if tier > 0 or lcode == 13 or lcode == 14 or lcode == 21 or ty == T_FIRE then
        call GroupEnumUnitsInRange(Fx_AoeG, GetUnitX(u), GetUnitY(u), 800.0, null)
        loop
            set v = FirstOfGroup(Fx_AoeG)
            exitwhen v == null
            call GroupRemoveUnit(Fx_AoeG, v)
            if Ab_Alive(v) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then
                if tier > 0 and IsUnitEnemy(v, po) and IsUnitInRange(v, u, rad) then
                    call SaveReal(Fx_HT, GetHandleId(v), 51, Mega_Time + 1.6)
                    if tier == 2 then
                        call SaveInteger(Fx_HT, GetHandleId(v), 52, 2)
                    else
                        call SaveInteger(Fx_HT, GetHandleId(v), 52, 1)
                    endif
                    set Ab_FxCur = u
                    if tier == 1 then
                        call Ab_FxAdd(v, 4, 1.6, 0.15)
                    elseif tier == 4 then
                        call Ab_FxAdd(v, 2, 1.6, 0.25)
                    else
                        call Ab_FxAdd(v, 4, 1.6, 0.25)
                    endif
                    set Ab_FxCur = null
                endif
                if lcode == 13 and IsUnitInRange(v, u, 700.0) then
                    call SaveReal(Fx_HT, GetHandleId(v), 47, Mega_Time + 1.6)
                    call SaveInteger(Fx_HT, GetHandleId(v), 48, GetPlayerId(po) + 1)
                endif
                if lcode == 14 and IsUnitInRange(v, u, 700.0) then
                    call SaveReal(Fx_HT, GetHandleId(v), 49, Mega_Time + 1.6)
                    call SaveInteger(Fx_HT, GetHandleId(v), 50, GetPlayerId(po) + 1)
                endif
                if lcode == 21 and IsUnitEnemy(v, po) and IsUnitInRange(v, u, 500.0) and Fx_StatusOf(v) == 5 then
                    call Ab_Deal(u, v, 0.08 * I2R(BlzGetUnitMaxHP(v)))
                endif
                if ty == T_FIRE and IsUnitEnemy(v, po) and IsUnitInRange(v, u, 350.0) then
                    call Ab_Deal(u, v, 0.01 * I2R(BlzGetUnitMaxHP(v)))
                endif
            endif
        endloop
    endif
    if lcode == 13 then  // Kyogre heals in its rain
        call Ab_Heal(u, 0.01 * mx)
    endif
    if lcode == 12 and Mega_Time - LoadReal(Ab_HT, hand, 1) >= 3.0 then  // Ho-Oh: Regenerator
        call Ab_Heal(u, 0.03 * mx)
    endif
    if ty == T_GRASS then  // Miracle Seed
        call Ab_Heal(u, 0.015 * mx)
    endif
    if (lcode == 5 or abil == AB_SPEEDBOOST) and fight and Mega_Time - LoadReal(Fx_HT, hand, 46) >= 8.0 then
        call SaveReal(Fx_HT, hand, 46, Mega_Time)
        if lcode != 5 or LoadInteger(Fx_HT, hand, 5) < 3 then
            call Fx_StageAdd(u, 5, 1, 12.0, u)
        endif
    endif
    if LoadInteger(Ab_HT, hand, 87) > 0 and GetPlayerId(po) >= 12 then  // v3.4.12: AI status moves
        call Fx_AiStatus(u)
    endif
    if lcode == 18 then  // Regigigas: +2 Attack once Slow Start is over
        if Mega_Time - LoadReal(Ab_HT, hand, 9) < 15.0 then
            call SaveInteger(Fx_HT, hand, 53, 0)
        elseif LoadInteger(Fx_HT, hand, 53) == 0 then
            call SaveInteger(Fx_HT, hand, 53, 1)
            call Fx_StageAdd(u, 1, 2, 9999.0, u)
        endif
    endif
    set po = null
    set v = null
endfunction

function Fx_Tick takes nothing returns nothing
    local unit u = null
    local integer hand = 0
    local integer st = 0
    local integer step = 0
    local integer abil = 0
    local real mx = 0.0
    set Fx_TickN = Fx_TickN + 1
    call GroupAddGroup(Fx_G, Fx_ScanG)
    loop
        set u = FirstOfGroup(Fx_ScanG)
        exitwhen u == null
        call GroupRemoveUnit(Fx_ScanG, u)
        if GetUnitTypeId(u) == 0 then
            call GroupRemoveUnit(Fx_G, u)
        elseif Ab_Alive(u) then
            set hand = GetHandleId(u)
            set st = LoadInteger(Fx_HT, hand, 20)
            if st > 0 and Mega_Time >= LoadReal(Fx_HT, hand, 21) then
                call SaveInteger(Fx_HT, hand, 20, 0)
                set st = 0
            endif
            if st == 3 and ModuloInteger(Fx_TickN, 2) == 0 then  // toxic: 1% -> 4% per second
                set step = LoadInteger(Fx_HT, hand, 22) + 1
                call SaveInteger(Fx_HT, hand, 22, step)
                set mx = I2R(BlzGetUnitMaxHP(u))
                set Ab_FxCur = LoadUnitHandle(Fx_HT, hand, 23)
                call Ab_FxAdd(u, 1, LoadReal(Fx_HT, hand, 21) - Mega_Time, RMinBJ(0.04, 0.01 + 0.005 * I2R(step)) * mx)
                set Ab_FxCur = null
            endif
            if Mega_Time < LoadReal(Fx_HT, hand, 64) then  // Aqua Ring / Ingrain: 2% per second
                call Ab_Heal(u, 0.01 * I2R(BlzGetUnitMaxHP(u)))
            endif
            if Mega_Time < LoadReal(Fx_HT, hand, 67) then  // Leech Seed: 2% per second to the seeder
                set mx = 0.01 * I2R(BlzGetUnitMaxHP(u))
                if LoadUnitHandle(Fx_HT, hand, 68) != null and Ab_Alive(LoadUnitHandle(Fx_HT, hand, 68)) then
                    call Ab_Deal(LoadUnitHandle(Fx_HT, hand, 68), u, mx)
                    call Ab_Heal(LoadUnitHandle(Fx_HT, hand, 68), mx)
                endif
            endif
            if st > 0 then
                set abil = Ab_Num(u)
                if abil == AB_SHEDSKIN and ModuloInteger(Fx_TickN, 6) == 0 and GetRandomReal(0.0, 1.0) < 0.3 then
                    call Fx_Cure(u)
                    call Fx_Say(u, "Shed Skin", 120, 255, 120, null)
                elseif (abil == AB_NATURALCURE or Fx_Legend(u) == 11) and Mega_Time - LoadReal(Ab_HT, hand, 60) >= 3.0 then
                    call Fx_Cure(u)
                endif
            endif
        else
            call Fx_Cure(u)
        endif
    endloop
    if ModuloInteger(Fx_TickN, 2) == 0 then
        call GroupEnumUnitsInRect(Fx_ScanG, bj_mapInitialPlayableArea, Filter(function Fx_ScanFilter))
        loop
            set u = FirstOfGroup(Fx_ScanG)
            exitwhen u == null
            call GroupRemoveUnit(Fx_ScanG, u)
            call Fx_AuraOf(u)
        endloop
    endif
    set u = null
endfunction

// ---- -stats: the numbers of the new system
function Fx_Stats takes player po, unit h returns nothing
    local integer hand = GetHandleId(h)
    local string s = "|cff99ccffSTR " + I2S(GetHeroStr(h, true)) + " | INT " + I2S(GetHeroInt(h, true)) + " | Def " + I2S(R2I(Fx_DefOf(h, 1))) + " | Sp. Def " + I2S(R2I(Fx_DefOf(h, 2)))
    local integer k = 1
    loop
        exitwhen k > 5
        if LoadInteger(Fx_HT, hand, k) != 0 and Mega_Time < LoadReal(Fx_HT, hand, 10 + k) then
            set s = s + " | " + Fx_StatName[k] + " " + I2S(LoadInteger(Fx_HT, hand, k))
        endif
        set k = k + 1
    endloop
    if Fx_HasStatus(h) then
        set s = s + " | " + Fx_StName[LoadInteger(Fx_HT, hand, 20)]
    endif
    call DisplayTimedTextToPlayer(po, 0, 0, 12.0, s + "|r")
endfunction

// ---- map start: League room (Darkrai leaves; portals, statues, labels)
function Fx_LeagueSetup takes nothing returns nothing
    local rect r = Rect(Fx_LRX0, Fx_LRY0, Fx_LRX1, Fx_LRY1)
    local unit u = null
    local integer k = 0
    local real gx = 0.0
    local real gy = 0.0
    call GroupEnumUnitsInRect(Fx_TmpG, r, null)
    loop
        set u = FirstOfGroup(Fx_TmpG)
        exitwhen u == null
        call GroupRemoveUnit(Fx_TmpG, u)
        if GetUnitTypeId(u) == 'n00F' then
            call RemoveUnit(u)
        endif
    endloop
    call RemoveRect(r)
    set Fx_LCenter = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'hfoo', Fx_LAX, Fx_LAY, 0.0)
    call ShowUnit(Fx_LCenter, false)
    call SetUnitInvulnerable(Fx_LCenter, true)
    call PauseUnit(Fx_LCenter, true)
    // a base portal next to each Item Shop (Ext_PlaceShops keeps where it put them), on walkable ground
    loop
        exitwhen k > 1
        set gx = Fx_GateX[k]
        set gy = Fx_GateY[k]
        if gx == 0.0 and gy == 0.0 then
            set gx = Fx_LGX * (2.0 * I2R(k) - 1.0)
            set gy = Fx_LGY
        elseif not IsTerrainPathable(gx, gy - 230.0, PATHING_TYPE_WALKABILITY) then
            set gy = gy - 230.0
        elseif not IsTerrainPathable(gx - 230.0, gy, PATHING_TYPE_WALKABILITY) then
            set gx = gx - 230.0
        elseif not IsTerrainPathable(gx + 230.0, gy, PATHING_TYPE_WALKABILITY) then
            set gx = gx + 230.0
        else
            set gy = gy + 230.0
        endif
        set Fx_GateX[k] = gx
        set Fx_GateY[k] = gy
        call AddSpecialEffect("buildings\\other\\CircleOfPower\\CircleOfPower.mdl", gx, gy)
        call Fx_Label("Pokemon League", gx, gy, 255, 204, 0)
        set k = k + 1
    endloop
    set k = 0
    call AddSpecialEffect("buildings\\other\\CircleOfPower\\CircleOfPower.mdl", Fx_LEX, Fx_LEY)
    call Fx_Label("Exit", Fx_LEX, Fx_LEY, 255, 120, 80)
    call Fx_Label("Pokemon League", Fx_LAX, Fx_LAY + 300.0, 255, 204, 0)
    loop
        exitwhen k >= Fx_StatueN
        set u = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), Fx_StatueType[k], Fx_StatueX[k], Fx_StatueY[k], bj_RADTODEG * Atan2(Fx_LAY - Fx_StatueY[k], Fx_LAX - Fx_StatueX[k]))
        if u != null then
            call UnitAddAbility(u, 'Aloc')
            call SetUnitInvulnerable(u, true)
            call PauseUnit(u, true)
            call SetUnitVertexColor(u, 150, 150, 165, 255)
            call SetUnitScale(u, 1.6, 1.6, 1.6)
            call SetUnitTimeScale(u, 0.0)
        endif
        call Fx_Label(Fx_StatueName[k], Fx_StatueX[k], Fx_StatueY[k], 220, 220, 230)
        set k = k + 1
    endloop
    set u = null
    set r = null
endfunction

function Fx_Init takes nothing returns nothing
    local trigger t = null
    local integer i = 0
    call ExecuteFunc("Fx_Data1")
    call ExecuteFunc("Fx_Data2")
    call ExecuteFunc("Fx_Data3")
    call ExecuteFunc("Fx_Data4")
    call ExecuteFunc("Fx_Data5")
    call ExecuteFunc("Fx_Data6")
    call ExecuteFunc("Fx_Data7")
    call ExecuteFunc("Fx_Data8")
    call ExecuteFunc("Fx_Data9")
    call ExecuteFunc("Fx_Data10")
    call ExecuteFunc("Fx_Data11")
    call ExecuteFunc("Fx_Data12")
    call ExecuteFunc("Fx_Texts")
    set Fx_StatName[1] = "Attack"
    set Fx_StatName[2] = "Defense"
    set Fx_StatName[3] = "Sp. Atk"
    set Fx_StatName[4] = "Sp. Def"
    set Fx_StatName[5] = "Speed"
    set Fx_StName[1] = "Burned!"
    set Fx_StName[2] = "Poisoned!"
    set Fx_StName[3] = "Badly poisoned!"
    set Fx_StName[4] = "Paralyzed!"
    set Fx_StName[5] = "Asleep!"
    set Fx_StName[6] = "Frozen!"
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_CAST)
    call TriggerAddCondition(t, Condition(function Fx_OnSpellCast))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_ENDCAST)
    call TriggerAddCondition(t, Condition(function Fx_OnEndCast))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(t, Condition(function Fx_OnDeath))
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SELL_ITEM)
    call TriggerAddCondition(t, Condition(function Fx_OnSell))
    set t = CreateTrigger()
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-tp", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function Fx_TpChat)
    call TimerStart(CreateTimer(), 0.5, true, function Fx_Tick)
    call TimerStart(CreateTimer(), 0.5, true, function Fx_LeagueTick)
    call Fx_LeagueSetup()
    set t = null
endfunction
