"""Build "Pokemon Arena v3.4.6.w3x" from "Pokemon Arena v3.4.5.w3x": 9xHeroDefense effects on Pokemon moves.

Visual only (the user asked not to touch skill damage):
1. Imports the effect models of fx_v346.py from the effect library (WW3/Skill/HieuUng/<folder>/): the model goes to
   PkFx\\<folder>.mdx, its textures keep the path the model asks for.
2. Units\\CampaignAbilityStrings.txt: Missileart of the moves in fx_v346.MISSILE (all 4 slot ids AV/AW/AY/AZ).
3. war3map.j: PkFx_* - on EVENT_PLAYER_UNIT_SPELL_EFFECT a move found in PkFx_HT gets its effect (special effect,
   scaled, removed after its animation). No damage, no unit, no order: nothing else of the move changes.

    python -I merge_v346.py <v3.4.5.w3x> <v3.4.6.w3x> --fx <HieuUng folder> --skills <data.json> [--tools <tools>]
"""
import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fx_v346 as FX  # noqa: E402

OLD, NEW = '3.4.5', '3.4.6'
SLOTS = 'VWYZ'


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


def anim_life(text):
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
    return min(FX.MAX_LIFE, max(0.6, life))


# ---------------------------------------------------------------- abilities in the map
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


def set_missile(txt, aid, model, log):
    m = re.search(r'^\[%s\]\r?\n(.*?)(?=^\[|\Z)' % aid, txt, re.M | re.S)
    body = m.group(1)
    if re.search(r'^Missileart=.*$', body, re.M) is None:
        raise SystemExit('%s has no Missileart' % aid)
    nb = re.sub(r'^Missileart=.*?(\r?)$', lambda x: 'Missileart=%s%s' % (model, x.group(1)), body, count=1, flags=re.M)
    return txt[:m.start(1)] + nb + txt[m.end(1):]


# ---------------------------------------------------------------- JASS
JASS_HEAD = r'''// v3.4.6: 9xHeroDefense effects on Pokemon moves (visual only: no damage, no unit, no order).
// PkFx_HT[ability id]: 0 model, 1 mode (0 target, 1 caster, 2 point, 3 line, 4 line end), 2 scale,
// 3 seconds before the effect is removed (0 = at once, plays its death animation), 4 missile speed (0 = none),
// 5 line length, 6 effects on the line.
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
    if fxDelay < 0.05 then
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

function PkFx_OnCast takes nothing returns boolean
    local integer fxAbil = GetSpellAbilityId()
    local unit fxCaster
    local unit fxTarget
    local string fxModel
    local integer fxMode
    local integer fxCount
    local integer fxStep
    local real fxScale
    local real fxLife
    local real fxSpeed
    local real fxLen
    local real fxSrcX
    local real fxSrcY
    local real fxDstX
    local real fxDstY
    local real fxAngle
    local real fxDist
    if not HaveSavedString(PkFx_HT, fxAbil, 0) then
        return false
    endif
    set fxCaster = GetTriggerUnit()
    set fxTarget = GetSpellTargetUnit()
    set fxModel = LoadStr(PkFx_HT, fxAbil, 0)
    set fxMode = LoadInteger(PkFx_HT, fxAbil, 1)
    set fxScale = LoadReal(PkFx_HT, fxAbil, 2)
    set fxLife = LoadReal(PkFx_HT, fxAbil, 3)
    set fxSpeed = LoadReal(PkFx_HT, fxAbil, 4)
    set fxLen = LoadReal(PkFx_HT, fxAbil, 5)
    set fxCount = LoadInteger(PkFx_HT, fxAbil, 6)
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
    if fxMode == 1 or (fxMode == 2 and fxDist < 1.0) then
        call PkFx_At(fxModel, fxSrcX, fxSrcY, fxAngle, fxScale, fxLife, 0.0)
    elseif fxMode == 0 or fxMode == 2 then
        if fxSpeed > 0.0 then
            call PkFx_At(fxModel, fxDstX, fxDstY, fxAngle, fxScale, fxLife, fxDist / fxSpeed)
        else
            call PkFx_At(fxModel, fxDstX, fxDstY, fxAngle, fxScale, fxLife, 0.0)
        endif
    elseif fxMode == 4 then
        call PkFx_At(fxModel, fxSrcX + fxLen * Cos(fxAngle), fxSrcY + fxLen * Sin(fxAngle), fxAngle, fxScale, fxLife, fxLen / fxSpeed)
    else
        set fxStep = 1
        loop
            exitwhen fxStep > fxCount
            set fxDist = fxLen * fxStep / fxCount
            call PkFx_At(fxModel, fxSrcX + fxDist * Cos(fxAngle), fxSrcY + fxDist * Sin(fxAngle), fxAngle, fxScale, fxLife, fxDist / fxSpeed)
            set fxStep = fxStep + 1
        endloop
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


def jass_data(entries):
    """entries: [(ability id, model, mode, scale, life, speed, length, count)] -> data functions (ExecuteFunc)."""
    funcs, names = [], []
    for i in range(0, len(entries), 40):
        name = 'PkFx_Data%d' % (len(names) + 1)
        body = []
        for aid, model, mode, scale, life, speed, length, count in entries[i:i + 40]:
            body.append("    call SaveStr(PkFx_HT, '%s', 0, %s)\n" % (aid, jstr(model)))
            body.append("    call SaveInteger(PkFx_HT, '%s', 1, %d)\n" % (aid, mode))
            body.append("    call SaveReal(PkFx_HT, '%s', 2, %.2f)\n" % (aid, scale))
            body.append("    call SaveReal(PkFx_HT, '%s', 3, %.2f)\n" % (aid, life))
            body.append("    call SaveReal(PkFx_HT, '%s', 4, %.1f)\n" % (aid, speed))
            body.append("    call SaveReal(PkFx_HT, '%s', 5, %.1f)\n" % (aid, length))
            body.append("    call SaveInteger(PkFx_HT, '%s', 6, %d)\n" % (aid, count))
        funcs.append('function %s takes nothing returns nothing\n%sendfunction\n\n' % (name, ''.join(body)))
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--fx', required=True, help='WW3/Skill/HieuUng folder')
    ap.add_argument('--csv', required=True, help='DanhSachHieuUng.csv')
    ap.add_argument('--skills', required=True, help='data.json of DanhSachKyNang.html (hero skill areas)')
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
    skills = {x['id']: x for x in json.load(open(a.skills, encoding='utf-8'))['S']}
    txt = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    secs = parse_strings(txt)
    mids = move_ids(secs)
    ab = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    rows = {ab.unquote(r.get(1)): r for r in ab.rows}

    def num(aid, col, default):
        v = ab.get(rows[aid], col)
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    imports, used, log, report, entries = {}, {}, [], [], []

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

    for stt, (sid, folder, moves) in sorted(FX.ASSET.items()):
        sk = skills[sid]
        asset_area = float((sk.get('ar') or [450])[0] or 450)
        r = info[folder]
        try:
            rad = float(r['Ban_kinh'])
            if rad > 5000:
                rad = None
        except ValueError:
            rad = None
        life = anim_life(r['Animation'])
        for mv in moves:
            ids = sorted(mids.get(mv, []))
            if not ids:
                log.append('skip %s (move not in this map)' % mv)
                report.append((stt, sk['n'], sid, mv, '', '', 'không có trong map'))
                continue
            aid0 = ids[0]
            base = ab.get(rows[aid0], 'code')
            missile = FX.MISSILE.get(mv)
            how = []
            if missile:
                mp = use(missile)
                for aid in ids:
                    txt = set_missile(txt, aid, mp, log)
                how.append('Missileart = %s' % missile)
            if missile and mv not in FX.END_AFTER_MISSILE:
                report.append((stt, sk['n'], sid, mv, ', '.join(ids), base, '; '.join(how)))
                continue
            mode = FX.MODE_OF_BASE[base]
            area = num(aid0, 'Area1', 0.0)
            rng = num(aid0, 'Rng1', 600.0)
            speed = float(secs[aid0].get('Missilespeed') or 0) if base in ('AHtb', 'AEsh') else 0.0
            count = 0
            if mode == 3:
                speed = float(secs[aid0].get('Missilespeed') or 1000)
                if folder in FX.BIG_FOR_LINE or missile:
                    mode = 4
                count = 3 if rng >= 600 else 2
            want = 150.0 if base in FX.SINGLE_TARGET else (130.0 if mode == 3 else max(area, 150.0))
            ref = asset_area if (rad is None or rad >= 150) else max(rad * 2.5, 60.0)
            scale = max(0.5, min(1.5, want / ref))
            if mode == 4:
                scale = max(0.5, min(1.0, scale))
            mp = use(folder)
            for aid in ids:
                entries.append((aid, mp, mode, scale, life, speed, rng, count))
            how.append('%s %s x%.2f %.1fs' % (folder, ['trên mục tiêu', 'quanh người dùng', 'tại điểm chọn',
                                                     'dọc đường đi', 'cuối đường đi'][mode], scale, life))
            report.append((stt, sk['n'], sid, mv, ', '.join(ids), base, '; '.join(how)))

    s = arc.read('scripts\\war3map.j').decode('latin-1')
    s = sub1(s, 'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)',
             'constant real Gym_ReviveGrace = 3.0     // v3.4.5: seconds dead before the battle is lost (Revive = 1 s)\n'
             'hashtable PkFx_HT = InitHashtable()     // v3.4.6: move effects (9xHeroDefense models)', 'globals')
    data, calls = jass_data(entries)
    jass = JASS_HEAD + data + JASS_INIT % calls
    first = func(s, 'Mega_Init').start()
    s = s[:first] + jass + s[first:]
    s = sub1(s, '    call HomeGate_Init()  // v3.4.5\n',
             '    call HomeGate_Init()  // v3.4.5\n    call PkFx_Init()  // v3.4.6\n', 'Mega_Init PkFx')
    s = sub1(s, 'call SetMapName("Pokemon Arena v%s")' % OLD, 'call SetMapName("Pokemon Arena v%s")' % NEW, 'map name')
    w3i = arc.read('war3map.w3i')
    for x in ('Pokemon Arena v%s', 'v%s:'):
        w3i = w3i.replace((x % OLD).encode(), (x % NEW).encode())
    if ('Pokemon Arena v%s' % NEW).encode() not in w3i:
        raise SystemExit('w3i: name not found')

    lst = arc.read('(listfile)').decode('latin-1').rstrip('\r\n') + '\r\n' + '\r\n'.join(sorted(imports)) + '\r\n'
    rep = {'scripts\\war3map.j': s.encode('latin-1'), 'war3map.w3i': w3i,
           'Units\\CampaignAbilityStrings.txt': txt.encode('utf-8')}
    rep.update(imports)
    arc.save_with(a.dst, rep, extra_listfile=lst.encode('latin-1'))
    log.append('imports: %d files (%d models), %d KB' % (len(imports), len(used), sum(len(v) for v in imports.values()) // 1024))
    log.append('JASS effects on %d ability ids, missile art on %d moves'
               % (len(entries), sum(1 for m in FX.MISSILE if m in mids)))
    if a.report:
        with open(a.report, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['STT Asset', 'Skill asset', 'ID asset', 'Skill Pokemon', 'Ability id (Q/W/E/R)', 'Gốc WC3', 'Hiệu ứng gắn'])
            w.writerows(report)
    for line in log:
        print(line)
    print('wrote', a.dst)


if __name__ == '__main__':
    main()
