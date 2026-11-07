// ---------------------------------------------------------------------------------------------
// Type chart (v3.4). A move deals Ty_Eff[move type * 18 + target type] for each type of the target, the product kept
// in [Ty_ImmuneMult, Ty_MaxMult]. Types of a unit type: Ab_HT keys 53, 54 = type + 1 (Ty_InitUnits).
// Type of a move: learned moves from Mv_Type (the move index is in the ability id, see Mv_Id), kit skills from
// Ab_HT key 50 on the ability id (Ty_InitKits). The last move a unit cast: Ab_HT keys 51 type + 1, 52 time,
// 55 power, 56 class (1 physical, 2 special); the same per player in Ty_P* for the dummy units of a move.
// ---------------------------------------------------------------------------------------------
function Ty_OfType takes integer uid, integer k returns integer
    return LoadInteger(Ab_HT, uid, 53 + k) - 1
endfunction

// v3.4: a Mega has the types of its Mega form (Mega Charizard X: Fire/Dragon); Zen Mode Darmanitan is Fire/Psychic
function Ty_Of takes unit u, integer k returns integer
    local integer h = GetHandleId(u)
    local integer mi = LoadInteger(Mega_HT, h, 0) - 1
    if k == 1 and LoadInteger(Ab_HT, h, 85) == 1 then
        return T_PSYCHIC
    endif
    if mi >= 0 and IsUnitType(u, UNIT_TYPE_HERO) and HaveSavedInteger(Ab_HT, Mega_Skin[mi], 53) then
        return LoadInteger(Ab_HT, Mega_Skin[mi], 53 + k) - 1
    endif
    return LoadInteger(Ab_HT, GetUnitTypeId(u), 53 + k) - 1
endfunction

function Ty_Has takes unit u, integer ty returns boolean
    return ty >= 0 and (Ty_Of(u, 0) == ty or Ty_Of(u, 1) == ty)
endfunction

// multiplier of a move of type mt against a unit type (gyms use it before the unit exists)
function Ty_TypeMult takes integer mt, integer uid returns real
    local integer a = LoadInteger(Ab_HT, uid, 53) - 1
    local integer b = LoadInteger(Ab_HT, uid, 54) - 1
    local real m = 1.0
    local real e = 0.0
    if mt < 0 then
        return 1.0
    endif
    if a >= 0 then
        set e = Ty_Eff[mt * 18 + a]
        if e <= 0.0 then
            set e = Ty_ImmuneMult
        endif
        set m = m * e
    endif
    if b >= 0 and b != a then
        set e = Ty_Eff[mt * 18 + b]
        if e <= 0.0 then
            set e = Ty_ImmuneMult
        endif
        set m = m * e
    endif
    if m < Ty_ImmuneMult then
        set m = Ty_ImmuneMult
    endif
    if m > Ty_MaxMult then
        set m = Ty_MaxMult
    endif
    return m
endfunction

function Ty_Mult takes integer mt, unit t returns real
    return Ty_TypeMult(mt, GetUnitTypeId(t))
endfunction

// true if one of the types of unit type att hits unit type def super effectively
function Ty_Counters takes integer att, integer def returns boolean
    local integer a = Ty_OfType(att, 0)
    local integer b = Ty_OfType(att, 1)
    return (a >= 0 and Ty_TypeMult(a, def) >= 1.99) or (b >= 0 and Ty_TypeMult(b, def) >= 1.99)
endfunction

// the type of unit type att that hits def best (for the skills a gym Pokemon gets), -1 if it has no type
function Ty_BestVs takes integer att, integer def returns integer
    local integer a = Ty_OfType(att, 0)
    local integer b = Ty_OfType(att, 1)
    if b >= 0 and (a < 0 or Ty_TypeMult(b, def) > Ty_TypeMult(a, def)) then
        return b
    endif
    return a
endfunction

// value of a base-36 digit character code, -1 if it is not one
function Ty_Undig takes integer c returns integer
    if c >= 48 and c <= 57 then
        return c - 48
    endif
    if c >= 65 and c <= 90 then
        return c - 55
    endif
    return -1
endfunction

// learned move index from its ability id ('A' + V/W/Y/Z + 2 base-36 digits, see Mv_Id), -1 if it is not one
function Ty_MoveOf takes integer id returns integer
    local integer a = id / 16777216
    local integer b = id / 65536 - a * 256
    local integer c = id / 256 - (id / 65536) * 256
    local integer d = id - (id / 256) * 256
    local integer hi = Ty_Undig(c)
    local integer lo = Ty_Undig(d)
    if a != 65 or (b != 86 and b != 87 and b != 89 and b != 90) or hi < 0 or lo < 0 then
        return -1
    endif
    if hi * 36 + lo >= Mv_N then
        return -1
    endif
    return hi * 36 + lo
endfunction

// the kit skills (Wild_KitSkill, kit k = type k - 1) carry their type on the ability id
function Ty_InitKits takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= 90
        if Wild_KitSkill[i] != 0 then
            call SaveInteger(Ab_HT, Wild_KitSkill[i], 50, i / 5 + 1)
        endif
        set i = i + 1
    endloop
endfunction

// EVENT_PLAYER_UNIT_SPELL_EFFECT: remember the type of the move a unit just cast
function Ty_OnCast takes nothing returns boolean
    local unit u = GetTriggerUnit()
    local integer id = GetSpellAbilityId()
    local integer m = Ty_MoveOf(id)
    local integer ty = -1
    local integer pw = 60
    local integer ph = 2
    local integer h = GetHandleId(u)
    local integer pid = GetPlayerId(GetOwningPlayer(u))
    if m >= 0 then
        set ty = Mv_Type[m]
        set pw = Mv_Pow[m]
        set ph = Mv_Phys[m]
    else
        set ty = LoadInteger(Ab_HT, id, 50) - 1
    endif
    if ty >= 0 then
        call SaveInteger(Ab_HT, h, 51, ty + 1)
        call SaveReal(Ab_HT, h, 52, Mega_Time)
        call SaveInteger(Ab_HT, h, 55, pw)
        call SaveInteger(Ab_HT, h, 56, ph)
        if pid < 12 then
            set Ty_PType[pid] = ty + 1
            set Ty_PTime[pid] = Mega_Time
            set Ty_PPow[pid] = pw
            set Ty_PPhys[pid] = ph
        endif
    endif
    set u = null
    return false
endfunction

// type of the move behind a skill's damage: the source's own last cast, else its owner's (dummy units of a move);
// -1 when nothing was cast within Ty_Window. Also sets Ty_CurPow / Ty_CurPhys.
function Ty_Resolve takes unit src returns integer
    local integer h = GetHandleId(src)
    local integer pid = GetPlayerId(GetOwningPlayer(src))
    set Ty_CurPow = 60
    set Ty_CurPhys = 2
    if LoadInteger(Ab_HT, h, 51) > 0 and Mega_Time - LoadReal(Ab_HT, h, 52) <= Ty_Window then
        set Ty_CurPow = LoadInteger(Ab_HT, h, 55)
        set Ty_CurPhys = LoadInteger(Ab_HT, h, 56)
        return LoadInteger(Ab_HT, h, 51) - 1
    endif
    if pid < 12 and Ty_PType[pid] > 0 and Mega_Time - Ty_PTime[pid] <= Ty_Window then
        set Ty_CurPow = Ty_PPow[pid]
        set Ty_CurPhys = Ty_PPhys[pid]
        return Ty_PType[pid] - 1
    endif
    return -1
endfunction

// floating text over unit t, seen by players plA and plB (shares the Dmg_Tags cap with the damage numbers)
function Ab_Say takes unit t, string s, integer r, integer g, integer b, player plA, player plB returns nothing
    local texttag tt = null
    if Dmg_Tags >= Dmg_TagMax or t == null then
        return
    endif
    set Dmg_Tags = Dmg_Tags + 1
    set tt = CreateTextTag()
    call SetTextTagText(tt, s, 0.022)
    call SetTextTagPos(tt, GetUnitX(t) - 60.0, GetUnitY(t), 150.0)
    call SetTextTagColor(tt, r, g, b, 255)
    call SetTextTagVelocity(tt, 0.0, 0.03)
    call SetTextTagPermanent(tt, false)
    call SetTextTagLifespan(tt, 1.5)
    call SetTextTagFadepoint(tt, 0.9)
    call SetTextTagVisibility(tt, GetLocalPlayer() == plA or GetLocalPlayer() == plB)
    set tt = null
endfunction

// a one-shot special effect on a unit
function Ab_Pop takes unit u, string model, string attach returns nothing
    if u != null then
        call DestroyEffect(AddSpecialEffectTarget(model, u, attach))
    endif
endfunction

// v3.4: a non-hero unit that dies forgets its Ability data: WC3 gives its handle id to a later unit (a dummy of a
// move would otherwise inherit the dead creep's Ability). Registered last, after every other death trigger.
function Ty_OnDeath takes nothing returns boolean
    local unit u = GetTriggerUnit()
    if not IsUnitType(u, UNIT_TYPE_HERO) then
        call FlushChildHashtable(Ab_HT, GetHandleId(u))
    endif
    set u = null
    return false
endfunction

