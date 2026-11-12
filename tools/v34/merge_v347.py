"""Build "Pokemon Arena v3.4.7.w3x" from "Pokemon Arena v3.4.5.w3x": 9xHeroDefense effects REPLACE the move art.

Visual only (damage, range, area, cooldown, mana, targets of the moves are untouched):
1. Units\\CampaignAbilityStrings.txt: every art field of the mapped moves (4 slot ids AV/AW/AY/AZ) is set empty
   (Missileart, Casterart, Targetart, Effectart, Specialart, Areaeffectart, LightningEffect).
2. Buffs with a visible target art (roots, frost, burn, shadow strike, impale, slow, blizzard) get an art-less copy
   (fx_v347.BUFF_COPY) used only by the mapped moves; the stun stars (BPSE) stay.
3. Effect models imported from WW3/Skill/HieuUng/<folder>/ as PkFx\\<folder>.mdx (+ their textures).
4. war3map.j: PkFx_* on EVENT_PLAYER_UNIT_SPELL_EFFECT draws the layers of fx_v347.SPEC (projectile at the move's
   missile speed, trail along the line, impact, ring, caster effect), scaled up.

    python -I merge_v347.py <v3.4.5.w3x> <v3.4.7.w3x> --fx <HieuUng folder> --csv <DanhSachHieuUng.csv>
           [--tools <tools>] [--report <csv>]
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fx_v347 as FX  # noqa: E402

OLD, NEW = '3.4.5', '3.4.7'
ART_KEYS = ('Missileart', 'Casterart', 'Targetart', 'Effectart', 'Specialart', 'Areaeffectart', 'LightningEffect')
BUFF_ART_KEYS = ('Targetart', 'Effectart', 'Specialart', 'Missileart', 'Casterart')

# base ability -> mode: 0 missile to a target unit, 1 around the caster, 2 channel AoE at a point,
# 3 line (wave / breath / shockwave / impale), 4 instant on the target
MODE_OF_BASE = {'AHtb': 0, 'AEsh': 0, 'AHtc': 1, 'AOws': 1, 'AHbz': 2,
                'AUcs': 3, 'AOsh': 3, 'ANbf': 3, 'AUim': 3, 'AEer': 4, 'AUfn': 4}
# data column holding the travel distance of a line move
LINE_LEN_COL = {'AUcs': 'DataC1', 'AOsh': 'DataC1', 'ANbf': 'DataC1', 'AUim': 'DataA1'}
SLOT = {'p': 10, 'h': 20, 'h2': 30, 't': 40, 'r': 50, 'c': 60}


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
        if n.startswith(('birth', 'stand')):
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


def clear_art(txt, sid, keys):
    """Set every key of `keys` to empty in section [sid] (existing lines replaced, missing ones added)."""
    m = re.search(SEC_RE % sid, txt, re.M | re.S)
    if not m:
        raise SystemExit('section %s not found' % sid)
    body = m.group(1)
    nl = '\r\n' if '\r\n' in body else '\n'
    lines = [ln for ln in body.splitlines() if ln.split('=', 1)[0] not in keys]
    lines = ['%s=' % k for k in keys] + lines
    nb = nl.join(lines) + nl
    return txt[:m.start(1)] + nb + txt[m.end(1):]


# ---------------------------------------------------------------- JASS
JASS_HEAD = r'''// v3.4.7: 9xHeroDefense effects replace the art of Pokemon moves (visual only: no damage, no unit, no order).
// PkFx_HT[ability id] 0 = move index. PkFx_HT[move index]: 0 mode (0 missile to unit, 1 caster, 2 channel point,
// 3 line, 4 instant target), 1 speed, 2 line length, 3 area, 4 waves, 5 ring radius, 6 hit count, 7 trail step,
// 8 ring count; layers at 10 projectile, 20 impact, 30 impact 2, 40 trail, 50 ring, 60 caster:
// +0 model, +1 scale, +2 seconds before removal (0 = at once, plays its death animation).
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
            call PkFx_Layer(fxIdx, 20, fxX + 70.0 * Cos(fxAng), fxY + 70.0 * Sin(fxAng), fxYaw + GetRandomReal(-0.8, 0.8), fxDelay + 0.2 * fxStep)
        endif
        set fxStep = fxStep + 1
    endloop
    call PkFx_Layer(fxIdx, 30, fxX, fxY, fxYaw, fxDelay)
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
    if fxMode == 1 or (fxMode == 2 and fxDist < 1.0) then
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
def folder_files(fx_root, folder):
    base = os.path.join(fx_root, folder)
    model, files = None, {}
    for dp, _dn, fn in os.walk(base):
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, base).replace('/', '\\')
            if f == 'ThongTin.txt':
                continue
            if f.lower().endswith('.mdx'):
                if model is not None:
                    raise SystemExit('%s: two models' % folder)
                model = full
            else:
                files[rel] = full
    if model is None:
        raise SystemExit('%s: no model' % folder)
    return model, files


def model_radius(row):
    try:
        r = float(row['Ban_kinh'])
    except (ValueError, TypeError):
        return FX.R_UNKNOWN
    if r <= 0 or r > 3000:
        return FX.R_UNKNOWN
    if int(row.get('Particle') or 0) > 0:
        r = max(r, 120.0)       # particles reach further than the geometry
    return max(r, 40.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--fx', required=True, help='WW3/Skill/HieuUng folder')
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
    info = {r['Thu_muc']: r for r in csv.DictReader(open(a.csv, encoding='utf-8-sig')) if r['Nhom'] == 'HieuUng'}
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

    def use(folder):
        if folder in used:
            return used[folder]
        model, files = folder_files(a.fx, folder)
        path = 'PkFx\\%s.mdx' % safe(folder)
        imports[path] = open(model, 'rb').read()
        for rel, full in files.items():
            data = open(full, 'rb').read()
            if rel.lower() in names:
                if arc.read(rel) != data:
                    raise SystemExit('%s: texture %s already in the map with other content' % (folder, rel))
                continue
            if rel in imports and imports[rel] != data:
                raise SystemExit('%s: texture %s imported twice with other content' % (folder, rel))
            imports[rel] = data
        used[folder] = path
        return path

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
    idx = 0
    for mv, spec in FX.SPEC.items():
        ids = sorted(mids.get(mv, []))
        stt = FX.ASSET_OF.get(mv, '')
        if not ids:
            log.append('skip %s (move not in this map)' % mv)
            report.append((stt, mv, '', '', 'không có trong map v3.4.5', ''))
            continue
        aid0 = ids[0]
        base = ab.get(rows[aid0], 'code')
        for aid in ids:
            if ab.get(rows[aid], 'code') != base:
                raise SystemExit('%s: slot ids with other bases' % mv)
        mode = MODE_OF_BASE[base]
        area = num(aid0, 'Area1', 0.0)
        speed = float(secs[aid0].get('Missilespeed') or 0)
        if speed <= 0:
            speed = 1100.0 if mode == 3 else 0.0
        length = num(aid0, LINE_LEN_COL[base], num(aid0, 'Rng1', 700.0)) if mode == 3 else 0.0
        waves = min(FX.WAVES_MAX, int(num(aid0, 'DataA1', 1))) if mode == 2 else 0
        if mode in (1, 2):
            want_h = max(area, 200.0) * FX.AREA_MULT
            ring_r = max(area, 200.0) * 0.75
        elif mode == 4:
            want_h = max(area, FX.R_TARGET)
            ring_r = max(area, 200.0) * 0.6
        elif mode == 3:
            want_h = max(FX.R_LINE_END, area * 2.0)
            ring_r = 160.0
        else:
            want_h = FX.R_TARGET
            ring_r = 140.0
        want = {'h': want_h, 'h2': want_h, 'c': FX.R_CAST, 'p': FX.R_PROJ,
                't': max(area * 1.6, FX.TRAIL_MIN), 'r': max(area, 200.0) * FX.RING_FRAC}
        layers, how = {}, []
        for key, slot in SLOT.items():
            folder = spec.get(key)
            if not folder:
                continue
            if key == 'p' and mode not in (0, 3):
                raise SystemExit('%s: projectile on a base without a missile (%s)' % (mv, base))
            if key == 't' and mode != 3:
                raise SystemExit('%s: trail on a base without a line (%s)' % (mv, base))
            row = info[folder]
            if key + 's' in spec:
                scale = spec[key + 's']
            else:
                scale = want[key] / model_radius(row)
                scale = clamp(scale, FX.PROJ_MIN, FX.PROJ_MAX) if key == 'p' else clamp(scale, FX.SCALE_MIN, FX.SCALE_MAX)
            if key == 't':
                life = anim_life(row['Animation'], FX.TRAIL_LIFE_MAX)
            elif key == 'p':
                life = 0.0
            else:
                life = anim_life(row['Animation'], FX.LIFE_MAX)
            layers[slot] = (use(folder), scale, life)
            how.append('%s=%s x%.2f' % ({'p': 'đạn', 'h': 'trúng', 'h2': 'trúng 2', 't': 'vệt', 'r': 'vòng',
                                         'c': 'người dùng'}[key], folder, scale))
        ring_n = spec.get('rn', 0) if 'r' in spec else 0
        hd = dict(mode=mode, speed=speed, len=length, area=area, waves=max(waves, 1), ring_r=ring_r,
                  multi=spec.get('m', 1), tstep=float(spec.get('tstep', FX.TRAIL_STEP)), ring_n=ring_n)
        idx += 1
        moves.append((idx, ids, hd, layers))
        # old art off
        for aid in ids:
            txt = clear_art(txt, aid, ART_KEYS)
            r = rows[aid]
            for col in buff_cols:
                v = ab.get(r, col)
                if not v:
                    continue
                nv = ','.join(FX.BUFF_COPY.get(b, b) for b in v.split(','))
                if nv != v:
                    r[ab.name_to_x[col]] = '"%s"' % nv
        report.append((stt, mv, ', '.join(ids), base, '; '.join(how),
                       'đạn %d, dài %d, vùng %d%s' % (speed, length, area, (', %d đợt' % hd['waves']) if mode == 2 else '')))

    # ---- script
    s = arc.read('scripts\\war3map.j').decode('latin-1')
    s = sub1(s, 'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)',
             'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)\n'
             'hashtable PkFx_HT = InitHashtable()     // v3.4.7: move effects (9xHeroDefense models)\n'
             'location PkFx_Loc = Location(0.0, 0.0)  // v3.4.7: terrain height of flying effects', 'globals')
    data, calls = jass_data(moves)
    jass = JASS_HEAD + data + JASS_INIT % calls
    first = func(s, 'Mega_Init').start()
    s = s[:first] + jass + s[first:]
    s = sub1(s, '    call HomeGate_Init()  // v3.4.5\n',
             '    call HomeGate_Init()  // v3.4.5\n    call PkFx_Init()  // v3.4.7\n', 'Mega_Init PkFx')
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
    log.append('imports: %d files (%d models), %d KB' % (len(imports), len(used), sum(len(v) for v in imports.values()) // 1024))
    log.append('moves with new effects: %d (%d ability ids)' % (len(moves), sum(len(m[1]) for m in moves)))
    if a.report:
        with open(a.report, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['STT Asset', 'Skill Pokemon', 'Ability id (Q/W/E/R)', 'Gốc WC3', 'Hiệu ứng mới (model x scale)', 'Thông số chiêu (không đổi)'])
            w.writerows(report)
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
