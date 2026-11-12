"""Build "Pokemon Arena v3.4.8.w3x" from "Pokemon Arena v3.4.5.w3x": 9xHeroDefense effects REPLACE the move art,
bigger, and contact moves become melee dashes.

Visual / movement only (damage, range, area, cooldown, mana, targets of the moves are untouched):
1. Units\\CampaignAbilityStrings.txt: every art field of the mapped moves (4 slot ids AV/AW/AY/AZ) is set empty
   (Missileart, Casterart, Targetart, Effectart, Specialart, Areaeffectart, LightningEffect). Melee moves without a
   mapped effect lose only their Missileart (the user is the missile now). Missilespeed of melee moves = dash speed,
   so the hit lands when the user arrives.
2. Buffs with a visible target art get an art-less copy (fx_v348.BUFF_COPY) used only by the mapped moves.
3. Effect models imported from WW3/Skill/<group>/<folder>/ as PkFx\\<folder>.mdx (+ their textures).
4. war3map.j: PkFx_* on EVENT_PLAYER_UNIT_SPELL_EFFECT draws the layers of fx_v348.SPEC; melee moves move the user
   to the target first (PkFx_Dash*: SetUnitX/Y every 0.02 s, stops at walls, 90 before a target unit).

    python -I merge_v348.py <v3.4.5.w3x> <v3.4.8.w3x> --fx <WW3/Skill folder> --csv <DanhSachHieuUng.csv>
           [--tools <tools>] [--report <csv>]
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fx_v348 as FX  # noqa: E402

OLD, NEW = '3.4.5', '3.4.8'
ART_KEYS = ('Missileart', 'Casterart', 'Targetart', 'Effectart', 'Specialart', 'Areaeffectart', 'LightningEffect')
BUFF_ART_KEYS = ('Targetart', 'Effectart', 'Specialart', 'Missileart', 'Casterart')

# base ability -> mode: 0 missile to a target unit, 1 around the caster, 2 channel AoE at a point,
# 3 line (wave / breath / shockwave / impale), 4 instant on the target
MODE_OF_BASE = {'AHtb': 0, 'AEsh': 0, 'AHtc': 1, 'AOws': 1, 'AHbz': 2,
                'AUcs': 3, 'AOsh': 3, 'ANbf': 3, 'AUim': 3, 'AEer': 4, 'AUfn': 4}
MELEE_BASES = {'AHtb', 'AEsh', 'AUcs', 'AOsh', 'AUim', 'AEer', 'AUfn'}
MISSILE_BASES = {'AHtb', 'AEsh', 'AUcs', 'AOsh'}   # their hit travels at Missilespeed
# data column holding the travel distance of a line move
LINE_LEN_COL = {'AUcs': 'DataC1', 'AOsh': 'DataC1', 'ANbf': 'DataC1', 'AUim': 'DataA1'}
SLOT = {'p': 10, 'h': 20, 'h2': 30, 't': 40, 'r': 50, 'c': 60, 'h3': 70}
NAME = {'p': 'đạn/hào quang', 'h': 'trúng', 'h2': 'trúng 2', 'h3': 'trúng 3', 't': 'vệt', 'r': 'vòng', 'c': 'người dùng'}


def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit('%s: expected 1 match, found %d' % (what, n))
    return s.replace(old, new)


def func(s, name):
    m = re.search(r'^function %s takes.*?^endfunction\n' % re.escape(name), s, re.M | re.S)
    if not m:
        raise SystemExit('war3map.j: function %s not found' % name)
    return m


def jstr(path):
    return '"' + path.replace('\\', '\\\\') + '"'


def safe(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def anim_life(text, cap):
    """Seconds to keep an effect: birth + stand animations; 0 = destroy at once (death animation only)."""
    life, death = 0.0, False
    for name, sec in re.findall(r'([A-Za-z][^,(]*?)\s*\(([\d.]+)s\)', text or ''):
        n = name.strip().lower()
        if n.startswith(('birth', 'stand', 'attack')):
            life += float(sec)
        elif n.startswith('death'):
            death = True
    if life <= 0.0:
        return 0.0 if death else 1.5
    return min(cap, max(0.8, life))


# ---------------------------------------------------------------- text data
SEC_RE = r'^\[%s\]\r?\n(.*?)(?=^\[|\Z)'


def parse_strings(txt):
    secs = {}
    for m in re.finditer(r'^\[(\w{4})\]\r?\n(.*?)(?=^\[|\Z)', txt, re.M | re.S):
        d = {}
        for line in m.group(2).splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                d[k] = v
        secs[m.group(1)] = d
    return secs


def move_ids(secs):
    out = {}
    for k, d in secs.items():
        if re.match(r'A[VWYZ][0-9A-Z]{2}$', k) and 'Name' in d:
            out.setdefault(d['Name'], []).append(k)
    return out


def set_keys(txt, sid, values):
    """values: {key: value}; existing lines of these keys are replaced, missing ones added (section [sid])."""
    m = re.search(SEC_RE % sid, txt, re.M | re.S)
    if not m:
        raise SystemExit('section %s not found' % sid)
    body = m.group(1)
    nl = '\r\n' if '\r\n' in body else '\n'
    lines = [ln for ln in body.splitlines() if ln.split('=', 1)[0] not in values]
    lines = ['%s=%s' % kv for kv in values.items()] + lines
    nb = nl.join(lines) + nl
    return txt[:m.start(1)] + nb + txt[m.end(1):]


# ---------------------------------------------------------------- JASS
JASS_HEAD = r'''// v3.4.8: 9xHeroDefense effects replace the art of Pokemon moves; contact moves dash to the target.
// Visual / movement only: no damage, no unit, no order.
// PkFx_HT[ability id] 0 = move index. PkFx_HT[move index]: 0 mode (0 missile to unit, 1 caster, 2 channel point,
// 3 line, 4 instant target), 1 speed, 2 line length, 3 area, 4 waves, 5 ring radius, 6 hit count, 7 trail step,
// 8 ring count, 90 melee (1 = dash), 91 dash speed; layers at 10 projectile / dash aura, 20 impact, 30 impact 2,
// 40 trail, 50 ring, 60 caster, 70 impact 3: +0 model, +1 scale, +2 seconds before removal (0 = at once).
// PkFx_HT[handle of a dashing unit] 0 = 1 while it dashes.
function PkFx_Z takes real fxX, real fxY returns real
    call MoveLocation(PkFx_Loc, fxX, fxY)
    return GetLocationZ(PkFx_Loc)
endfunction

function PkFx_Kill takes nothing returns nothing
    local timer fxTimer = GetExpiredTimer()
    local integer fxKey = GetHandleId(fxTimer)
    call DestroyEffect(LoadEffectHandle(PkFx_HT, fxKey, 0))
    call FlushChildHashtable(PkFx_HT, fxKey)
    call DestroyTimer(fxTimer)
    set fxTimer = null
endfunction

function PkFx_Make takes string fxModel, real fxX, real fxY, real fxYaw, real fxScale, real fxLife returns nothing
    local effect fxEff = AddSpecialEffect(fxModel, fxX, fxY)
    local timer fxTimer
    call BlzSetSpecialEffectScale(fxEff, fxScale)
    call BlzSetSpecialEffectYaw(fxEff, fxYaw)
    if fxLife <= 0.0 then
        call DestroyEffect(fxEff)
    else
        set fxTimer = CreateTimer()
        call SaveEffectHandle(PkFx_HT, GetHandleId(fxTimer), 0, fxEff)
        call TimerStart(fxTimer, fxLife, false, function PkFx_Kill)
    endif
    set fxEff = null
    set fxTimer = null
endfunction

function PkFx_Late takes nothing returns nothing
    local timer fxTimer = GetExpiredTimer()
    local integer fxKey = GetHandleId(fxTimer)
    call PkFx_Make(LoadStr(PkFx_HT, fxKey, 0), LoadReal(PkFx_HT, fxKey, 1), LoadReal(PkFx_HT, fxKey, 2), LoadReal(PkFx_HT, fxKey, 3), LoadReal(PkFx_HT, fxKey, 4), LoadReal(PkFx_HT, fxKey, 5))
    call FlushChildHashtable(PkFx_HT, fxKey)
    call DestroyTimer(fxTimer)
    set fxTimer = null
endfunction

function PkFx_At takes string fxModel, real fxX, real fxY, real fxYaw, real fxScale, real fxLife, real fxDelay returns nothing
    local timer fxTimer
    local integer fxKey
    if fxDelay < 0.03 then
        call PkFx_Make(fxModel, fxX, fxY, fxYaw, fxScale, fxLife)
        return
    endif
    set fxTimer = CreateTimer()
    set fxKey = GetHandleId(fxTimer)
    call SaveStr(PkFx_HT, fxKey, 0, fxModel)
    call SaveReal(PkFx_HT, fxKey, 1, fxX)
    call SaveReal(PkFx_HT, fxKey, 2, fxY)
    call SaveReal(PkFx_HT, fxKey, 3, fxYaw)
    call SaveReal(PkFx_HT, fxKey, 4, fxScale)
    call SaveReal(PkFx_HT, fxKey, 5, fxLife)
    call TimerStart(fxTimer, fxDelay, false, function PkFx_Late)
    set fxTimer = null
endfunction

function PkFx_Layer takes integer fxIdx, integer fxSlot, real fxX, real fxY, real fxYaw, real fxDelay returns nothing
    if HaveSavedString(PkFx_HT, fxIdx, fxSlot) then
        call PkFx_At(LoadStr(PkFx_HT, fxIdx, fxSlot), fxX, fxY, fxYaw, LoadReal(PkFx_HT, fxIdx, fxSlot + 1), LoadReal(PkFx_HT, fxIdx, fxSlot + 2), fxDelay)
    endif
endfunction

function PkFx_Impact takes integer fxIdx, real fxX, real fxY, real fxYaw, real fxDelay returns nothing
    local integer fxCount = LoadInteger(PkFx_HT, fxIdx, 6)
    local integer fxStep = 0
    local real fxRad = LoadReal(PkFx_HT, fxIdx, 5)
    local real fxAng
    loop
        exitwhen fxStep >= fxCount
        if fxStep == 0 then
            call PkFx_Layer(fxIdx, 20, fxX, fxY, fxYaw, fxDelay)
        else
            set fxAng = GetRandomReal(0.0, 6.2832)
            call PkFx_Layer(fxIdx, 20, fxX + 80.0 * Cos(fxAng), fxY + 80.0 * Sin(fxAng), fxYaw + GetRandomReal(-0.8, 0.8), fxDelay + 0.18 * fxStep)
        endif
        set fxStep = fxStep + 1
    endloop
    call PkFx_Layer(fxIdx, 30, fxX, fxY, fxYaw, fxDelay)
    call PkFx_Layer(fxIdx, 70, fxX, fxY, fxYaw, fxDelay + 0.1)
    set fxCount = LoadInteger(PkFx_HT, fxIdx, 8)
    set fxStep = 0
    loop
        exitwhen fxStep >= fxCount
        set fxAng = fxYaw + 6.2832 * fxStep / fxCount
        call PkFx_Layer(fxIdx, 50, fxX + fxRad * Cos(fxAng), fxY + fxRad * Sin(fxAng), fxAng, fxDelay + 0.12)
        set fxStep = fxStep + 1
    endloop
endfunction

function PkFx_FlyTick takes nothing returns nothing
    local timer fxTimer = GetExpiredTimer()
    local integer fxKey = GetHandleId(fxTimer)
    local effect fxEff = LoadEffectHandle(PkFx_HT, fxKey, 0)
    local unit fxTarget = LoadUnitHandle(PkFx_HT, fxKey, 1)
    local real fxX = LoadReal(PkFx_HT, fxKey, 4)
    local real fxY = LoadReal(PkFx_HT, fxKey, 5)
    local real fxTx = LoadReal(PkFx_HT, fxKey, 2)
    local real fxTy = LoadReal(PkFx_HT, fxKey, 3)
    local real fxStep = LoadReal(PkFx_HT, fxKey, 6)
    local integer fxTicks = LoadInteger(PkFx_HT, fxKey, 8) + 1
    local real fxDist
    local real fxAng
    if fxTarget != null and GetWidgetLife(fxTarget) > 0.405 then
        set fxTx = GetUnitX(fxTarget)
        set fxTy = GetUnitY(fxTarget)
        call SaveReal(PkFx_HT, fxKey, 2, fxTx)
        call SaveReal(PkFx_HT, fxKey, 3, fxTy)
    endif
    set fxDist = SquareRoot((fxTx - fxX) * (fxTx - fxX) + (fxTy - fxY) * (fxTy - fxY))
    set fxAng = Atan2(fxTy - fxY, fxTx - fxX)
    if fxDist <= fxStep or fxTicks > 150 then
        call DestroyEffect(fxEff)
        call PkFx_Impact(LoadInteger(PkFx_HT, fxKey, 7), fxTx, fxTy, fxAng, 0.0)
        call FlushChildHashtable(PkFx_HT, fxKey)
        call DestroyTimer(fxTimer)
    else
        set fxX = fxX + fxStep * Cos(fxAng)
        set fxY = fxY + fxStep * Sin(fxAng)
        call BlzSetSpecialEffectPosition(fxEff, fxX, fxY, PkFx_Z(fxX, fxY) + 70.0)
        call BlzSetSpecialEffectYaw(fxEff, fxAng)
        call SaveReal(PkFx_HT, fxKey, 4, fxX)
        call SaveReal(PkFx_HT, fxKey, 5, fxY)
        call SaveInteger(PkFx_HT, fxKey, 8, fxTicks)
    endif
    set fxTimer = null
    set fxEff = null
    set fxTarget = null
endfunction

function PkFx_Fly takes integer fxIdx, real fxX, real fxY, unit fxTarget, real fxTx, real fxTy, real fxAng returns nothing
    local effect fxEff = AddSpecialEffect(LoadStr(PkFx_HT, fxIdx, 10), fxX, fxY)
    local timer fxTimer = CreateTimer()
    local integer fxKey = GetHandleId(fxTimer)
    call BlzSetSpecialEffectScale(fxEff, LoadReal(PkFx_HT, fxIdx, 11))
    call BlzSetSpecialEffectYaw(fxEff, fxAng)
    call BlzSetSpecialEffectPosition(fxEff, fxX, fxY, PkFx_Z(fxX, fxY) + 70.0)
    call SaveEffectHandle(PkFx_HT, fxKey, 0, fxEff)
    if fxTarget != null then
        call SaveUnitHandle(PkFx_HT, fxKey, 1, fxTarget)
    endif
    call SaveReal(PkFx_HT, fxKey, 2, fxTx)
    call SaveReal(PkFx_HT, fxKey, 3, fxTy)
    call SaveReal(PkFx_HT, fxKey, 4, fxX)
    call SaveReal(PkFx_HT, fxKey, 5, fxY)
    call SaveReal(PkFx_HT, fxKey, 6, LoadReal(PkFx_HT, fxIdx, 1) * 0.03)
    call SaveInteger(PkFx_HT, fxKey, 7, fxIdx)
    call SaveInteger(PkFx_HT, fxKey, 8, 0)
    call TimerStart(fxTimer, 0.03, true, function PkFx_FlyTick)
    set fxEff = null
    set fxTimer = null
endfunction

// ---- melee: the user dashes to the target. Timer data: 0 aura effect, 1 user, 2 target unit, 3 / 4 goal x / y,
// 5 step per tick, 6 distance left, 7 move index, 8 ticks, 9 distance since the last trail effect.
function PkFx_Blocked takes unit fxUnit, real fxX, real fxY returns boolean
    if IsUnitType(fxUnit, UNIT_TYPE_FLYING) then
        return IsTerrainPathable(fxX, fxY, PATHING_TYPE_FLYABILITY)
    endif
    return IsTerrainPathable(fxX, fxY, PATHING_TYPE_WALKABILITY)
endfunction

function PkFx_DashEnd takes integer fxKey, real fxAng returns nothing
    local unit fxUser = LoadUnitHandle(PkFx_HT, fxKey, 1)
    local unit fxTarget = LoadUnitHandle(PkFx_HT, fxKey, 2)
    local integer fxIdx = LoadInteger(PkFx_HT, fxKey, 7)
    local real fxX
    local real fxY
    if HaveSavedHandle(PkFx_HT, fxKey, 0) then
        call DestroyEffect(LoadEffectHandle(PkFx_HT, fxKey, 0))
    endif
    if fxTarget != null and GetWidgetLife(fxTarget) > 0.405 then
        set fxX = GetUnitX(fxTarget)
        set fxY = GetUnitY(fxTarget)
    else
        set fxX = GetUnitX(fxUser) + 60.0 * Cos(fxAng)
        set fxY = GetUnitY(fxUser) + 60.0 * Sin(fxAng)
    endif
    call PkFx_Impact(fxIdx, fxX, fxY, fxAng, 0.0)
    if GetWidgetLife(fxUser) > 0.405 then
        call SetUnitAnimation(fxUser, "attack")
        call QueueUnitAnimation(fxUser, "stand")
    endif
    call RemoveSavedInteger(PkFx_HT, GetHandleId(fxUser), 0)
    call FlushChildHashtable(PkFx_HT, fxKey)
    set fxUser = null
    set fxTarget = null
endfunction

function PkFx_DashTick takes nothing returns nothing
    local timer fxTimer = GetExpiredTimer()
    local integer fxKey = GetHandleId(fxTimer)
    local unit fxUser = LoadUnitHandle(PkFx_HT, fxKey, 1)
    local unit fxTarget = LoadUnitHandle(PkFx_HT, fxKey, 2)
    local real fxGx = LoadReal(PkFx_HT, fxKey, 3)
    local real fxGy = LoadReal(PkFx_HT, fxKey, 4)
    local real fxStep = LoadReal(PkFx_HT, fxKey, 5)
    local real fxLeft = LoadReal(PkFx_HT, fxKey, 6)
    local integer fxTicks = LoadInteger(PkFx_HT, fxKey, 8) + 1
    local real fxTrail = LoadReal(PkFx_HT, fxKey, 9)
    local integer fxIdx = LoadInteger(PkFx_HT, fxKey, 7)
    local real fxX = GetUnitX(fxUser)
    local real fxY = GetUnitY(fxUser)
    local real fxStop = 0.0
    local real fxDist
    local real fxAng
    local real fxNx
    local real fxNy
    local boolean fxDone = false
    if fxTarget != null and GetWidgetLife(fxTarget) > 0.405 then
        set fxGx = GetUnitX(fxTarget)
        set fxGy = GetUnitY(fxTarget)
        set fxStop = PkFx_DashStop
    endif
    set fxDist = SquareRoot((fxGx - fxX) * (fxGx - fxX) + (fxGy - fxY) * (fxGy - fxY))
    if fxDist < 1.0 then
        set fxAng = GetUnitFacing(fxUser) * bj_DEGTORAD
    else
        set fxAng = Atan2(fxGy - fxY, fxGx - fxX)
    endif
    if GetWidgetLife(fxUser) <= 0.405 or fxTicks > 60 or fxLeft <= 0.0 or fxDist <= fxStop + 1.0 then
        set fxDone = true
    else
        if fxStep > fxDist - fxStop then
            set fxStep = fxDist - fxStop
        endif
        if fxStep > fxLeft then
            set fxStep = fxLeft
        endif
        set fxNx = fxX + fxStep * Cos(fxAng)
        set fxNy = fxY + fxStep * Sin(fxAng)
        if PkFx_Blocked(fxUser, fxNx, fxNy) then
            set fxDone = true
        else
            call SetUnitX(fxUser, fxNx)
            call SetUnitY(fxUser, fxNy)
            call SetUnitFacing(fxUser, fxAng * bj_RADTODEG)
            if HaveSavedHandle(PkFx_HT, fxKey, 0) then
                call BlzSetSpecialEffectPosition(LoadEffectHandle(PkFx_HT, fxKey, 0), fxNx, fxNy, PkFx_Z(fxNx, fxNy) + 60.0)
                call BlzSetSpecialEffectYaw(LoadEffectHandle(PkFx_HT, fxKey, 0), fxAng)
            endif
            set fxTrail = fxTrail + fxStep
            if fxTrail >= LoadReal(PkFx_HT, fxIdx, 7) then
                set fxTrail = 0.0
                call PkFx_Layer(fxIdx, 40, fxNx, fxNy, fxAng, 0.0)
            endif
            call SaveReal(PkFx_HT, fxKey, 6, fxLeft - fxStep)
            call SaveReal(PkFx_HT, fxKey, 9, fxTrail)
            call SaveInteger(PkFx_HT, fxKey, 8, fxTicks)
            if fxDist - fxStep <= fxStop + 1.0 or fxLeft - fxStep <= 0.0 then
                set fxDone = true
            endif
        endif
    endif
    if fxDone then
        call PkFx_DashEnd(fxKey, fxAng)
        call DestroyTimer(fxTimer)
    endif
    set fxTimer = null
    set fxUser = null
    set fxTarget = null
endfunction

function PkFx_Dash takes integer fxIdx, unit fxUser, unit fxTarget, real fxGx, real fxGy, real fxMax returns nothing
    local timer fxTimer
    local integer fxKey
    local effect fxEff
    local real fxAng = Atan2(fxGy - GetUnitY(fxUser), fxGx - GetUnitX(fxUser))
    if LoadInteger(PkFx_HT, GetHandleId(fxUser), 0) == 1 or GetUnitDefaultMoveSpeed(fxUser) <= 0.0 or IsUnitType(fxUser, UNIT_TYPE_STRUCTURE) then
        // already dashing / cannot move: the hit is shown on the target only
        call PkFx_Impact(fxIdx, fxGx, fxGy, fxAng, 0.0)
        return
    endif
    call SaveInteger(PkFx_HT, GetHandleId(fxUser), 0, 1)
    set fxTimer = CreateTimer()
    set fxKey = GetHandleId(fxTimer)
    if HaveSavedString(PkFx_HT, fxIdx, 10) then
        set fxEff = AddSpecialEffect(LoadStr(PkFx_HT, fxIdx, 10), GetUnitX(fxUser), GetUnitY(fxUser))
        call BlzSetSpecialEffectScale(fxEff, LoadReal(PkFx_HT, fxIdx, 11))
        call BlzSetSpecialEffectYaw(fxEff, fxAng)
        call SaveEffectHandle(PkFx_HT, fxKey, 0, fxEff)
    endif
    call SaveUnitHandle(PkFx_HT, fxKey, 1, fxUser)
    if fxTarget != null and fxTarget != fxUser then
        call SaveUnitHandle(PkFx_HT, fxKey, 2, fxTarget)
    endif
    call SaveReal(PkFx_HT, fxKey, 3, fxGx)
    call SaveReal(PkFx_HT, fxKey, 4, fxGy)
    call SaveReal(PkFx_HT, fxKey, 5, LoadReal(PkFx_HT, fxIdx, 91) * 0.02)
    call SaveReal(PkFx_HT, fxKey, 6, fxMax)
    call SaveInteger(PkFx_HT, fxKey, 7, fxIdx)
    call SaveInteger(PkFx_HT, fxKey, 8, 0)
    call SaveReal(PkFx_HT, fxKey, 9, 0.0)
    call SetUnitAnimation(fxUser, "walk")
    call TimerStart(fxTimer, 0.02, true, function PkFx_DashTick)
    set fxTimer = null
    set fxEff = null
endfunction

function PkFx_OnCast takes nothing returns boolean
    local integer fxAbil = GetSpellAbilityId()
    local integer fxIdx
    local integer fxMode
    local integer fxStep
    local integer fxCount
    local unit fxCaster
    local unit fxTarget
    local real fxSpeed
    local real fxLen
    local real fxArea
    local real fxSrcX
    local real fxSrcY
    local real fxDstX
    local real fxDstY
    local real fxAngle
    local real fxDist
    local real fxTrail
    local real fxOff
    if not HaveSavedInteger(PkFx_HT, fxAbil, 0) then
        return false
    endif
    set fxIdx = LoadInteger(PkFx_HT, fxAbil, 0)
    set fxMode = LoadInteger(PkFx_HT, fxIdx, 0)
    set fxSpeed = LoadReal(PkFx_HT, fxIdx, 1)
    set fxLen = LoadReal(PkFx_HT, fxIdx, 2)
    set fxArea = LoadReal(PkFx_HT, fxIdx, 3)
    set fxCaster = GetTriggerUnit()
    set fxTarget = GetSpellTargetUnit()
    set fxSrcX = GetUnitX(fxCaster)
    set fxSrcY = GetUnitY(fxCaster)
    if fxTarget != null then
        set fxDstX = GetUnitX(fxTarget)
        set fxDstY = GetUnitY(fxTarget)
    else
        set fxDstX = GetSpellTargetX()
        set fxDstY = GetSpellTargetY()
    endif
    set fxDist = SquareRoot((fxDstX - fxSrcX) * (fxDstX - fxSrcX) + (fxDstY - fxSrcY) * (fxDstY - fxSrcY))
    if fxDist < 1.0 then
        set fxAngle = GetUnitFacing(fxCaster) * bj_DEGTORAD
    else
        set fxAngle = Atan2(fxDstY - fxSrcY, fxDstX - fxSrcX)
    endif
    call PkFx_Layer(fxIdx, 60, fxSrcX, fxSrcY, fxAngle, 0.0)
    if LoadInteger(PkFx_HT, fxIdx, 90) == 1 then
        // melee: line moves dash at most their line length, the others up to the target
        if fxMode == 3 and fxLen > 0.0 and fxDist > fxLen then
            set fxDist = fxLen
        endif
        if fxTarget == null and fxDist < 1.0 then
            set fxDist = 300.0
            set fxDstX = fxSrcX + fxDist * Cos(fxAngle)
            set fxDstY = fxSrcY + fxDist * Sin(fxAngle)
        endif
        call PkFx_Dash(fxIdx, fxCaster, fxTarget, fxDstX, fxDstY, fxDist)
    elseif fxMode == 1 or (fxMode == 2 and fxDist < 1.0) then
        call PkFx_Impact(fxIdx, fxSrcX, fxSrcY, fxAngle, 0.0)
    elseif fxMode == 2 then
        set fxCount = LoadInteger(PkFx_HT, fxIdx, 4)
        set fxStep = 0
        loop
            exitwhen fxStep >= fxCount
            if fxStep == 0 then
                call PkFx_Impact(fxIdx, fxDstX, fxDstY, fxAngle, 0.0)
            else
                set fxOff = GetRandomReal(0.0, 6.2832)
                set fxDist = GetRandomReal(0.0, fxArea * 0.5)
                call PkFx_Impact(fxIdx, fxDstX + fxDist * Cos(fxOff), fxDstY + fxDist * Sin(fxOff), fxAngle, 1.0 * fxStep)
            endif
            set fxStep = fxStep + 1
        endloop
    elseif fxMode == 3 then
        set fxDstX = fxSrcX + fxLen * Cos(fxAngle)
        set fxDstY = fxSrcY + fxLen * Sin(fxAngle)
        if HaveSavedString(PkFx_HT, fxIdx, 40) then
            set fxTrail = LoadReal(PkFx_HT, fxIdx, 7)
            set fxDist = fxTrail
            loop
                exitwhen fxDist > fxLen - fxTrail * 0.5
                call PkFx_Layer(fxIdx, 40, fxSrcX + fxDist * Cos(fxAngle), fxSrcY + fxDist * Sin(fxAngle), fxAngle, fxDist / fxSpeed)
                set fxDist = fxDist + fxTrail
            endloop
        endif
        if HaveSavedString(PkFx_HT, fxIdx, 10) then
            call PkFx_Fly(fxIdx, fxSrcX, fxSrcY, null, fxDstX, fxDstY, fxAngle)
        else
            call PkFx_Impact(fxIdx, fxDstX, fxDstY, fxAngle, fxLen / fxSpeed)
        endif
    elseif (fxMode == 0 or fxMode == 4) and HaveSavedString(PkFx_HT, fxIdx, 40) and not HaveSavedString(PkFx_HT, fxIdx, 10) then
        // trail caster -> target, timed with the missile (instant moves: a quick sweep)
        if fxSpeed <= 0.0 then
            set fxSpeed = 2500.0
        endif
        set fxTrail = LoadReal(PkFx_HT, fxIdx, 7)
        set fxOff = fxTrail
        loop
            exitwhen fxOff > fxDist - fxTrail * 0.5
            call PkFx_Layer(fxIdx, 40, fxSrcX + fxOff * Cos(fxAngle), fxSrcY + fxOff * Sin(fxAngle), fxAngle, fxOff / fxSpeed)
            set fxOff = fxOff + fxTrail
        endloop
        call PkFx_Impact(fxIdx, fxDstX, fxDstY, fxAngle, fxDist / fxSpeed)
    elseif fxMode == 0 and HaveSavedString(PkFx_HT, fxIdx, 10) then
        call PkFx_Fly(fxIdx, fxSrcX, fxSrcY, fxTarget, fxDstX, fxDstY, fxAngle)
    elseif fxMode == 0 then
        call PkFx_Impact(fxIdx, fxDstX, fxDstY, fxAngle, fxDist / fxSpeed)
    else
        call PkFx_Impact(fxIdx, fxDstX, fxDstY, fxAngle, 0.0)
    endif
    set fxCaster = null
    set fxTarget = null
    return false
endfunction

'''

JASS_INIT = r'''function PkFx_Init takes nothing returns nothing
    local trigger fxTrig = CreateTrigger()
%s    call TriggerRegisterAnyUnitEventBJ(fxTrig, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(fxTrig, Condition(function PkFx_OnCast))
    set fxTrig = null
endfunction

'''


def jass_data(moves):
    """moves: [(index, [ability ids], header dict, {slot: (model path, scale, life)})] -> data functions."""
    lines = []
    for idx, ids, hd, layers in moves:
        blk = []
        for aid in ids:
            blk.append("    call SaveInteger(PkFx_HT, '%s', 0, %d)\n" % (aid, idx))
        blk.append('    call SaveInteger(PkFx_HT, %d, 0, %d)\n' % (idx, hd['mode']))
        blk.append('    call SaveReal(PkFx_HT, %d, 1, %.1f)\n' % (idx, hd['speed']))
        blk.append('    call SaveReal(PkFx_HT, %d, 2, %.1f)\n' % (idx, hd['len']))
        blk.append('    call SaveReal(PkFx_HT, %d, 3, %.1f)\n' % (idx, hd['area']))
        blk.append('    call SaveInteger(PkFx_HT, %d, 4, %d)\n' % (idx, hd['waves']))
        blk.append('    call SaveReal(PkFx_HT, %d, 5, %.1f)\n' % (idx, hd['ring_r']))
        blk.append('    call SaveInteger(PkFx_HT, %d, 6, %d)\n' % (idx, hd['multi']))
        blk.append('    call SaveReal(PkFx_HT, %d, 7, %.1f)\n' % (idx, hd['tstep']))
        blk.append('    call SaveInteger(PkFx_HT, %d, 8, %d)\n' % (idx, hd['ring_n']))
        if hd['melee']:
            blk.append('    call SaveInteger(PkFx_HT, %d, 90, 1)\n' % idx)
            blk.append('    call SaveReal(PkFx_HT, %d, 91, %.1f)\n' % (idx, hd['dash']))
        for slot, (path, scale, life) in sorted(layers.items()):
            blk.append('    call SaveStr(PkFx_HT, %d, %d, %s)\n' % (idx, slot, jstr(path)))
            blk.append('    call SaveReal(PkFx_HT, %d, %d, %.2f)\n' % (idx, slot + 1, scale))
            blk.append('    call SaveReal(PkFx_HT, %d, %d, %.2f)\n' % (idx, slot + 2, life))
        lines.append(''.join(blk))
    funcs, names = [], []
    for i in range(0, len(lines), 12):
        name = 'PkFx_Data%d' % (len(names) + 1)
        funcs.append('function %s takes nothing returns nothing\n%sendfunction\n\n' % (name, ''.join(lines[i:i + 12])))
        names.append(name)
    calls = ''.join('    call ExecuteFunc("%s")\n' % n for n in names)
    return ''.join(funcs), calls


# ---------------------------------------------------------------- main
def split_name(name):
    """'Folder' -> ('HieuUng', 'Folder'); 'Group/Folder' -> ('Group', 'Folder')."""
    if '/' in name:
        g, f = name.split('/', 1)
        return g, f
    return 'HieuUng', name


def folder_files(fx_root, name):
    group, folder = split_name(name)
    base = os.path.join(fx_root, group, folder)
    model, files = None, {}
    for dp, _dn, fn in os.walk(base):
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, base).replace('/', '\\')
            if f == 'ThongTin.txt':
                continue
            if f.lower().endswith('.mdx'):
                if model is not None:
                    raise SystemExit('%s: two models' % name)
                model = full
            else:
                files[rel] = full
    if model is None:
        raise SystemExit('%s: no model in %s' % (name, base))
    return model, files


def model_radius(row):
    if row is None:
        return FX.R_UNKNOWN
    try:
        r = float(row['Ban_kinh'])
    except (ValueError, TypeError):
        return FX.R_UNKNOWN
    if r <= 0 or r > 5000:
        return FX.R_UNKNOWN
    if int(row.get('Particle') or 0) > 0:
        r = max(r, 120.0)       # particles reach further than the geometry
    return max(r, 40.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--fx', required=True, help='WW3/Skill folder (holds HieuUng, ChuaDungTrongMap, ModelTrieuHoi)')
    ap.add_argument('--csv', required=True, help='DanhSachHieuUng.csv')
    ap.add_argument('--tools', default=os.path.dirname(HERE))
    ap.add_argument('--report', default=None)
    a = ap.parse_args()
    if os.path.exists(a.dst):
        raise SystemExit('%s exists, not overwriting' % a.dst)
    sys.path.insert(0, a.tools)
    import mpq
    import slk

    arc = mpq.MPQ(a.src)
    names = set(n.lower() for n in arc.listfile())
    info = {}
    for r in csv.DictReader(open(a.csv, encoding='utf-8-sig')):
        info['%s/%s' % (r['Nhom'], r['Thu_muc'])] = r
    txt = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    secs = parse_strings(txt)
    mids = move_ids(secs)
    ab_text = arc.read('Units\\AbilityData.slk').decode('latin-1')
    ab = slk.Slk(ab_text)
    rows = {ab.unquote(r.get(1)): r for r in ab.rows}
    bd = slk.Slk(arc.read('Units\\AbilityBuffData.slk').decode('latin-1'))
    brows = {bd.unquote(r.get(1)): r for r in bd.rows}

    def num(aid, col, default):
        v = ab.get(rows[aid], col)
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    imports, used, log, report, moves = {}, {}, [], [], []

    def use(name):
        if name.startswith('war3:'):
            return name[5:]
        if name in used:
            return used[name]
        model, files = folder_files(a.fx, name)
        path = 'PkFx\\%s.mdx' % safe(split_name(name)[1])
        imports[path] = open(model, 'rb').read()
        for rel, full in files.items():
            data = open(full, 'rb').read()
            if rel.lower() in names:
                if arc.read(rel) != data:
                    raise SystemExit('%s: texture %s already in the map with other content' % (name, rel))
                continue
            if rel in imports and imports[rel] != data:
                raise SystemExit('%s: texture %s imported twice with other content' % (name, rel))
            imports[rel] = data
        used[name] = path
        return path

    def row_of(name):
        if name.startswith('war3:'):
            return None
        g, f = split_name(name)
        r = info.get('%s/%s' % (g, f))
        if r is None:
            raise SystemExit('%s not in %s' % (name, a.csv))
        return r

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    # ---- buff copies (art-less)
    for old, new in FX.BUFF_COPY.items():
        if new in brows or new in secs:
            raise SystemExit('buff id %s already used' % new)
        if old not in brows or old not in secs:
            raise SystemExit('buff %s not in the map' % old)
        nr = dict(brows[old])
        nr[1] = '"%s"' % new
        bd.rows.append(nr)
        body = re.search(SEC_RE % old, txt, re.M | re.S).group(1)
        nl = '\r\n' if '\r\n' in body else '\n'
        keep = [ln for ln in body.splitlines() if ln.split('=', 1)[0] not in BUFF_ART_KEYS and not ln.startswith('EditorName')]
        nb = nl.join(['%s=' % k for k in BUFF_ART_KEYS] + keep) + nl
        txt = txt.rstrip('\r\n') + nl + '[%s]%s%s' % (new, nl, nb)

    buff_cols = [c for c in ab.name_to_x if re.match(r'(BuffID|EfctID)\d+$', c)]

    # moves to handle: every mapped move + every melee move
    todo = list(FX.SPEC.items())
    for mv in sorted(FX.MELEE):
        if mv not in FX.SPEC:
            todo.append((mv, None))

    idx = 0
    for mv, spec in todo:
        ids = sorted(mids.get(mv, []))
        stt = FX.ASSET_OF.get(mv, '')
        aname = FX.ASSET_NAME.get(mv, '')
        if not ids:
            log.append('skip %s (move not in this map)' % mv)
            report.append((stt, aname, mv, '', '', '', 'không có trong map v3.4.5', ''))
            continue
        aid0 = ids[0]
        base = ab.get(rows[aid0], 'code')
        for aid in ids:
            if ab.get(rows[aid], 'code') != base:
                raise SystemExit('%s: slot ids with other bases' % mv)
        melee = mv in FX.MELEE and base in MELEE_BASES
        mapped = spec is not None
        if not mapped:
            # melee move without a 9xHeroDefense effect: keep its art, its missile model bursts on the target
            if not melee:
                continue
            old_missile = secs[aid0].get('Missileart') or ''
            spec = dict(t=FX.GENERIC_TRAIL, h=FX.GENERIC_HIT, hs=0.9)
            if old_missile:
                spec['h2'] = 'war3:' + old_missile
                spec['h2s'] = 1.8
        mode = MODE_OF_BASE[base]
        area = num(aid0, 'Area1', 0.0)
        speed = float(secs[aid0].get('Missilespeed') or 0)
        dash = float(spec.get('ds', FX.DASH_SPEED)) if melee else 0.0
        if melee and base in MISSILE_BASES:
            speed = dash
        if speed <= 0:
            speed = 1100.0 if mode == 3 else 0.0
        length = num(aid0, LINE_LEN_COL[base], num(aid0, 'Rng1', 700.0)) if mode == 3 else 0.0
        waves = min(FX.WAVES_MAX, int(num(aid0, 'DataA1', 1))) if mode == 2 else 0
        if mode in (1, 2):
            want_h = max(area, 200.0) * FX.AREA_MULT
            ring_r = max(area, 200.0) * 0.8
        elif mode == 4:
            want_h = max(area * 1.3, FX.R_TARGET)
            ring_r = max(area, 200.0) * 0.7
        elif mode == 3 and not melee:
            want_h = max(FX.R_LINE_END, area * 2.5)
            ring_r = 190.0
        else:
            want_h = FX.R_TARGET
            ring_r = 170.0
        want = {'h': want_h, 'h2': want_h, 'h3': want_h, 'c': FX.R_CAST, 'p': FX.R_PROJ,
                't': max(area * 2.0, FX.TRAIL_MIN), 'r': max(area, 200.0) * FX.RING_FRAC}
        layers, how = {}, []
        for key, slot in SLOT.items():
            folder = spec.get(key)
            if not folder:
                continue
            if not melee and key == 'p' and mode not in (0, 3):
                raise SystemExit('%s: projectile on a base without a missile (%s)' % (mv, base))
            if not melee and key == 't' and mode not in (0, 3, 4):
                raise SystemExit('%s: trail on a base without a line (%s)' % (mv, base))
            row = row_of(folder)
            rad = model_radius(row)
            if key + 's' in spec:
                scale = spec[key + 's']
            else:
                scale = want[key] / rad
                lo = FX.SMALL_MIN if rad > 1000 else None
                if key == 'p':
                    scale = clamp(scale, lo or FX.PROJ_MIN, FX.PROJ_MAX)
                else:
                    scale = clamp(scale, lo or FX.SCALE_MIN, FX.SCALE_MAX)
            anim = row['Animation'] if row else 'Birth (1.0s)'
            if key == 't':
                life = anim_life(anim, FX.TRAIL_LIFE_MAX)
            elif key == 'p':
                life = 0.0
            else:
                life = anim_life(anim, FX.LIFE_MAX)
            layers[slot] = (use(folder), scale, life)
            how.append('%s=%s x%.2f' % (NAME[key], folder.replace('war3:', ''), scale))
        ring_n = spec.get('rn', 0) if 'r' in spec else 0
        hd = dict(mode=mode, speed=speed, len=length, area=area, waves=max(waves, 1), ring_r=ring_r,
                  multi=spec.get('m', 1), tstep=float(spec.get('tstep', FX.TRAIL_STEP)), ring_n=ring_n,
                  melee=melee, dash=dash)
        idx += 1
        moves.append((idx, ids, hd, layers))
        for aid in ids:
            vals = {}
            if mapped:
                # old art off, buffs without art
                vals.update({k: '' for k in ART_KEYS})
                r = rows[aid]
                for col in buff_cols:
                    v = ab.get(r, col)
                    if not v:
                        continue
                    nv = ','.join(FX.BUFF_COPY.get(b, b) for b in v.split(','))
                    if nv != v:
                        r[ab.name_to_x[col]] = '"%s"' % nv
            elif melee:
                vals['Missileart'] = ''
            if melee and base in MISSILE_BASES:
                vals['Missilespeed'] = '%d' % int(dash)
            if vals:
                txt = set_keys(txt, aid, vals)
        kind = 'cận chiến (lướt %d)' % dash if melee else 'tầm xa'
        report.append((stt, aname, mv, ', '.join(ids), base, kind, '; '.join(how) if mapped else
                       'giữ hiệu ứng cũ; ' + '; '.join(how),
                       'tầm %s, vùng %d%s' % (secs[aid0].get('Rng1') or ab.get(rows[aid0], 'Rng1') or '-', area,
                                             (', %d đợt' % hd['waves']) if mode == 2 else '')))

    # ---- script
    s = arc.read('scripts\\war3map.j').decode('latin-1')
    s = sub1(s, 'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)',
             'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)\n'
             'hashtable PkFx_HT = InitHashtable()     // v3.4.8: move effects (9xHeroDefense models), melee dashes\n'
             'location PkFx_Loc = Location(0.0, 0.0)  // v3.4.8: terrain height of flying effects\n'
             'constant real PkFx_DashStop = %.1f     // v3.4.8: a dash ends this far from its target unit' % FX.DASH_STOP,
             'globals')
    data, calls = jass_data(moves)
    jass = JASS_HEAD + data + JASS_INIT % calls
    first = func(s, 'Mega_Init').start()
    s = s[:first] + jass + s[first:]
    s = sub1(s, '    call HomeGate_Init()  // v3.4.5\n',
             '    call HomeGate_Init()  // v3.4.5\n    call PkFx_Init()  // v3.4.8\n', 'Mega_Init PkFx')
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')

    lst = arc.read('(listfile)').decode('latin-1').rstrip('\r\n') + '\r\n' + '\r\n'.join(sorted(imports)) + '\r\n'
    rep = {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.w3i': w3i,
           'Units\\CampaignAbilityStrings.txt': txt.encode('utf-8'),
           'Units\\AbilityData.slk': ab.to_text().encode('latin-1'),
           'Units\\AbilityBuffData.slk': bd.to_text().encode('latin-1')}
    rep.update(imports)
    arc.save_with(a.dst, rep, extra_listfile=lst.encode('latin-1'))
    n_mapped = sum(1 for r in report if r[0] != '' and r[3])
    n_melee = sum(1 for m in moves if m[2]['melee'])
    log.append('imports: %d files (%d models), %d KB' % (len(imports), len(used), sum(len(v) for v in imports.values()) // 1024))
    log.append('moves: %d with new effects, %d melee (dash), %d entries (%d ability ids)'
               % (n_mapped, n_melee, len(moves), sum(len(m[1]) for m in moves)))
    if a.report:
        with open(a.report, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['STT Asset', 'Skill asset', 'Skill Pokemon', 'Ability id (Z/X/C/V)', 'Gốc WC3', 'Kiểu',
                        'Hiệu ứng (model x scale)', 'Thông số chiêu (không đổi)'])
            w.writerows(report)
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
