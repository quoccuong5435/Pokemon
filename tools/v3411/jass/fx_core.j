// =============================================================================================
// v3.4.11 move / status engine, part 1 (inserted before Hero_HPSync): only reads data, no calls into later code.
// Fx_HT layout (the move / Ability rework plan approved 2026-11-14)
//   unit handle: 1..5 stat stage (1 Atk 2 Def 3 SpA 4 SpD 5 Spe), 11..15 stage end time, 20 main status
//     (1 burn 2 poison 3 toxic 4 paralysis 5 sleep 6 freeze), 21 status end, 22 toxic step, 24 confusion end,
//     25 silence end, 26 accuracy-down end, 30 move key of the last cast, 31 cast time, 32 cast serial,
//     33 serial whose self effects are done, 34 held gym type item + 1, 35 hard-CC window end, 36 item proc time,
//     37 charging (1), 38 fake-out armed serial, 41 Mewtwo shield ready, 42 shield HP, 43 shield end,
//     44 Ho-Oh rebirth ready, 45 Regirock Sturdy ready, 46 last speed tick, 47 rain zone end, 48 rain owner + 1,
//     49 sun zone end, 50 sun owner + 1, 51 pressure end, 52 pressure tier, 53 Slow Start stage given, 60 portal ready
//   move key (100000 + move index) or kit skill ability id: 1 flags, 2 recoil permille, 3 drain permille, 4 status,
//     5 status chance, 6 flinch chance, 7 self chance, 8 target chance, 10..14 self stage, 20..24 target stage,
//     26 accuracy down (1), 30 class (1 physical, 2 special), 31 type + 1
//   unit type: 1 Def, 2 Sp. Def, 3 legend code, 4 Pressure tier (2 legend, 3 Dialga, 4 Palkia)
//   item type: 1 type index + 1 (type items), 2 = 1 one per Pokemon, 3 gold price
//   200000 + type index: 1 type item, 2 ability count, 10 + k abilities of the item (gym holders)
// =============================================================================================
function Fx_StageMult takes unit u, integer s returns real
    local integer hand = GetHandleId(u)
    local integer stage = LoadInteger(Fx_HT, hand, s)
    local real step = 0.25
    if stage == 0 or Mega_Time >= LoadReal(Fx_HT, hand, 10 + s) then
        return 1.0
    endif
    if s == 5 then
        set step = 0.15
    endif
    if stage > 0 then
        return 1.0 + step * I2R(stage)
    endif
    return 1.0 / (1.0 + step * I2R(-stage))
endfunction

function Fx_HasStatus takes unit u returns boolean
    local integer hand = GetHandleId(u)
    return LoadInteger(Fx_HT, hand, 20) > 0 and Mega_Time < LoadReal(Fx_HT, hand, 21)
endfunction

function Fx_StatusOf takes unit u returns integer
    if Fx_HasStatus(u) then
        return LoadInteger(Fx_HT, GetHandleId(u), 20)
    endif
    return 0
endfunction

function Fx_Silenced takes unit u returns boolean
    return Mega_Time < LoadReal(Fx_HT, GetHandleId(u), 25)
endfunction

// key of the move a unit cast within Ty_Window (100000 + move index, or the kit skill id), 0 = none
function Fx_CurMove takes unit u returns integer
    local integer hand = GetHandleId(u)
    if Mega_Time - LoadReal(Fx_HT, hand, 31) <= Ty_Window then
        return LoadInteger(Fx_HT, hand, 30)
    endif
    return 0
endfunction

function Fx_MoveHas takes unit u, integer flag returns boolean
    local integer mkey = Fx_CurMove(u)
    local integer bits = 0
    if mkey == 0 then
        return false
    endif
    set bits = LoadInteger(Fx_HT, mkey, 1)
    return ModuloInteger(bits / flag, 2) == 1
endfunction

// class of the move a unit just used: 1 physical, 2 special (Ty_OnCast keeps it in Ab_HT 56)
function Fx_CurPhys takes unit u returns integer
    local integer hand = GetHandleId(u)
    if LoadInteger(Ab_HT, hand, 51) > 0 and Mega_Time - LoadReal(Ab_HT, hand, 52) <= Ty_Window then
        if LoadInteger(Ab_HT, hand, 56) == 1 then
            return 1
        endif
    endif
    return 2
endfunction

// the stat that scales a hero's move: STR for physical moves, INT for special moves (v3.4.11, was the larger one)
function Fx_SkillStat takes unit u returns real
    if Fx_CurPhys(u) == 1 then
        return I2R(GetHeroStr(u, true))
    endif
    return I2R(GetHeroInt(u, true))
endfunction

// attack speed factor: Speed stage, Chlorophyll / Swift Swim in their weather, Regigigas after Slow Start
function Fx_ASMult takes unit u returns real
    local integer hand = GetHandleId(u)
    local integer abil = LoadInteger(Ab_HT, hand, 0)
    local real mult = Fx_StageMult(u, 5)
    if (abil == AB_CHLOROPHYLL and Wth_Cur == 2) or (abil == AB_SWIFTSWIM and Wth_Cur == 1) then
        set mult = mult * 1.3
    endif
    if LoadInteger(Fx_HT, GetUnitTypeId(u), 3) == 18 and Mega_Time - LoadReal(Ab_HT, hand, 9) >= 15.0 then
        set mult = mult * 1.3
    endif
    return mult
endfunction

// extra move speed from the Speed stage (Ab_MoveBonus adds it)
function Fx_MSBonus takes unit u returns real
    return (Fx_StageMult(u, 5) - 1.0) * GetUnitDefaultMoveSpeed(u)
endfunction

// v3.4.14 safety: a charge never keeps the user paused longer than 1.5s (key 72 = charge serial)
function Fx_ChargeTimeout takes nothing returns nothing
    local timer tm = GetExpiredTimer()
    local integer k = GetHandleId(tm)
    local unit u = LoadUnitHandle(Fx_HT, k, 0)
    if u != null and LoadInteger(Fx_HT, GetHandleId(u), 37) == 1 and LoadInteger(Fx_HT, GetHandleId(u), 72) == LoadInteger(Fx_HT, k, 1) then
        call SaveInteger(Fx_HT, GetHandleId(u), 37, 0)
        call BlzPauseUnitEx(u, false)
    endif
    call FlushChildHashtable(Fx_HT, k)
    call DestroyTimer(tm)
    set tm = null
    set u = null
endfunction

// Mv_Queue: a charging move (Solar Beam, Sky Attack ...) waits 1.2s, the user cannot act meanwhile.
// v3.4.14: pressing the move again while it charges must not pause the user a second time (BlzPauseUnitEx counts:
// two pauses and one unpause left the Pokemon frozen for good).
function Fx_QueueDelay takes unit u, integer mvi returns real
    local integer bits = 0
    local integer hand = GetHandleId(u)
    local timer tm = null
    if mvi < 0 then
        return 0.0
    endif
    set bits = LoadInteger(Fx_HT, 100000 + mvi, 1)
    if ModuloInteger(bits / 2, 2) == 0 then
        return 0.0
    endif
    if ModuloInteger(bits / 2097152, 2) == 1 and Wth_Cur == 2 then  // Solar Beam / Solar Blade in harsh sun
        return 0.0
    endif
    if LoadInteger(Fx_HT, hand, 37) == 1 then  // already charging: no second pause
        return 1.2
    endif
    call SaveInteger(Fx_HT, hand, 37, 1)
    call SaveInteger(Fx_HT, hand, 72, LoadInteger(Fx_HT, hand, 72) + 1)
    call BlzPauseUnitEx(u, true)
    set tm = CreateTimer()
    call SaveUnitHandle(Fx_HT, GetHandleId(tm), 0, u)
    call SaveInteger(Fx_HT, GetHandleId(tm), 1, LoadInteger(Fx_HT, hand, 72))
    call TimerStart(tm, 1.5, false, function Fx_ChargeTimeout)
    set tm = null
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Invisibility\\InvisibilityTarget.mdl", u, "origin"))
    return 1.2
endfunction

function Fx_ChargeEnd takes unit u returns nothing
    local integer hand = GetHandleId(u)
    if LoadInteger(Fx_HT, hand, 37) == 1 then
        call SaveInteger(Fx_HT, hand, 37, 0)
        call BlzPauseUnitEx(u, false)
    endif
endfunction
