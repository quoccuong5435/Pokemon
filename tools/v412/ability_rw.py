"""Ability rework for the v4.2x line (approved by the user on 2026-11-22, 3 rounds on the shared review page).

What it does to a map script (`patch(script)`):
- 105 Abilities get new numbers (AB_RW_*, from 91) and run in new JASS (tools/v412/jass/ability_rw_*.j):
  66 that had no code and 39 reworked ones. Their old numbers stay for wild creeps, Megas and forms.
- 5 Abilities keep their numbers and get their new values in place (Air Lock, Bad Dreams, Slow Start, Zen Mode,
  Magic Bounce: legend / skin code is tied to them).
- Every roster hero gets its approved default Ability (Ab_HT '<id>' key 0), tools/v412/ability_rw_data.json.
- Hooks: about 30 anchored insertions in the damage, status, stage, heal, slow, push and stat-sync code.
- In-game test command for the host: `-abtest <Ability name>` gives the selected own hero that Ability,
  `-abtest off` gives its own back.
Object data (`patch_objects`): one info button per new number ('AB2J' ..), cloned from 'AB01'.

Order in a build script: script = ability_rw.patch(script) BEFORE hidden_ability.patch (that one reads the Ability
names, and the reworked ones must win). move_ability_fix.patch can run before or after.
Every anchor must be found exactly once, otherwise ValueError: nothing is guessed.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
JASS = os.path.join(HERE, 'jass')
FIRST = 91

from ability_rw_text import RW_TEXT, SPECIAL_TEXT  # noqa: E402


def _load():
    with open(os.path.join(HERE, 'ability_rw_data.json'), encoding='utf-8') as fh:
        return json.load(fh)


DATA = _load()
RW_ORDER = DATA['rw_order']
RW_MAX = FIRST + len(RW_ORDER) - 1


def const_name(name):
    return 'AB_RW_' + re.sub(r'[^A-Z0-9]', '', name.upper())


RW_INDEX = {name: FIRST + i for i, name in enumerate(RW_ORDER)}


def info_id(index):
    """object id of the info button of Ability `index` (same formula as Ab_InfoId)"""
    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    i = index - 1
    return 'AB' + digits[i // 36] + digits[i % 36]


def _read(name):
    with open(os.path.join(JASS, name), encoding='utf-8') as fh:
        return fh.read()


def _lines(text, eol):
    return text.replace('\r\n', '\n').replace('\n', eol)


def _jstr(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


class Patcher:
    def __init__(self, script):
        self.s = script
        self.eol = '\r\n' if '\r\n' in script else '\n'

    def find_block(self, lines):
        """(block text, times found, line ending used right after the block in the script)"""
        for eol in ('\r\n', '\n'):
            block = eol.join(lines)
            n = self.s.count(block)
            if n:
                at = self.s.find(block) + len(block)
                after = '\r\n' if self.s.startswith('\r\n', at) else '\n'
                return block, n, (eol if len(lines) > 1 else after)
        return None, 0, self.eol

    def replace(self, old_lines, new_lines, what):
        block, n, eol = self.find_block(old_lines)
        if n != 1:
            raise ValueError('[ability_rw] anchor found %d times: %s' % (n, what))
        self.s = self.s.replace(block, eol.join(new_lines))

    def insert_before(self, anchor_lines, new_text, what):
        block, n, eol = self.find_block(anchor_lines)
        if n != 1:
            raise ValueError('[ability_rw] anchor found %d times: %s' % (n, what))
        self.s = self.s.replace(block, _lines(new_text, eol) + eol + block)

    def insert_after(self, anchor_lines, new_text, what):
        block, n, eol = self.find_block(anchor_lines)
        if n != 1:
            raise ValueError('[ability_rw] anchor found %d times: %s' % (n, what))
        self.s = self.s.replace(block, block + eol + _lines(new_text, eol).rstrip(eol))

    def in_function(self, header, old, new, what):
        """replace `old` (one line) with `new` inside the function that starts with `header` (exactly once there)"""
        start = self.s.find(header)
        if start < 0 or self.s.count(header) != 1:
            raise ValueError('[ability_rw] function not found once: %s' % header)
        end = self.s.find('endfunction', start)
        body = self.s[start:end]
        eol = '\r\n' if '\r\n' in body else '\n'
        old = old.replace('\n', eol)
        new = new.replace('\n', eol)
        if body.count(old) != 1:
            raise ValueError('[ability_rw] %s: %r found %d times in the function' % (what, old, body.count(old)))
        self.s = self.s[:start] + body.replace(old, new) + self.s[end:]


def _globals():
    out = [
        '    hashtable RW_HT = InitHashtable()  // v4.2x Ability rework (tools/v412/ability_rw.py)',
        '    boolean RW_Proc = false',
        '    unit RW_ProcSrc = null',
        '    unit RW_ProcTgt = null',
        '    integer RW_DmgType = -1',
        '    boolean RW_LastCrit = false',
        '    boolean RW_Converted = false',
        '    boolean RW_TextsDone = false',
        '    group RW_Grp = CreateGroup()',
        '    group RW_Heroes = CreateGroup()',
        '    timer RW_Timer = null',
        '    integer RW_Beat = 0',
        '    constant integer AB_RW_FIRST = %d' % FIRST,
        '    constant integer RW_MAX = %d' % RW_MAX,
    ]
    for name in RW_ORDER:
        out.append('    constant integer %s = %d' % (const_name(name), RW_INDEX[name]))
    return '\n'.join(out)


def _old_index(script):
    index = {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', script):
        index.setdefault(m.group(2), int(m.group(1)))
    return index


def _data_block(script):
    old = _old_index(script)
    out = ['// ===== v4.2x Ability rework, data part: names, tooltips, test command, start =====',
           'function RW_Texts takes nothing returns nothing']
    for name in RW_ORDER:
        n = RW_INDEX[name]
        text = _jstr(RW_TEXT[name])
        out += ['    set Ab_Name[%d] = "%s"' % (n, _jstr(name)),
                '    set Ab_Info[%d] = "%s"' % (n, text),
                '    call BlzSetAbilityTooltip(Ab_InfoId(%d), "Ability: |cffffcc00%s|r", 0)' % (n, _jstr(name)),
                '    call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), "%s", 0)' % (n, text)]
    for name, text in sorted(SPECIAL_TEXT.items()):
        if name not in old:
            raise ValueError('[ability_rw] Ability %s not in the map' % name)
        n = old[name]
        out += ['    set Ab_Info[%d] = "%s"' % (n, _jstr(text)),
                '    call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), "%s", 0)' % (n, _jstr(text))]
    out.append('endfunction')
    out.append(_read('ability_rw_data.j'))
    return '\n'.join(out)


def _hooks(p):
    # ---- Ab_Want: the -abtest Ability first
    p.insert_after([
        'function Ab_Want takes unit u returns integer',
        '    local integer mi = LoadInteger(Mega_HT, GetHandleId(u), 0) - 1',
        '    local integer formId = PAX_Form_Id(u)',
    ], '''    if LoadInteger(RW_HT, GetHandleId(u), 90) > 0 then  // v4.2x: -abtest
        return LoadInteger(RW_HT, GetHandleId(u), 90)
    endif''', 'Ab_Want locals')
    # ---- Ab_Deal: Magic Guard takes no indirect damage; Rock Head takes nothing sent back by its target
    p.insert_before([
        '    set Ab_Busy = true',
        '    call UnitDamageTarget(src, t, d, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_UNIVERSAL, WEAPON_TYPE_WHOKNOWS)',
        '    set Ab_Busy = false',
        'endfunction',
    ], '''    if RW_Ab(t) == AB_RW_MAGICGUARD then  // v4.2x
        return
    endif
    if RW_Proc and t == RW_ProcSrc and src == RW_ProcTgt and RW_Ab(t) == AB_RW_ROCKHEAD then
        return
    endif''', 'Ab_Deal')
    # ---- Ab_FxAdd: slows / stuns / armor cuts the Ability stops or shortens
    p.insert_after([
        '    if u == null or not Ab_Alive(u) then',
        '        return',
        '    endif',
        '    if Ab_Num(u) == AB_MULTITYPE and kind >= 1 and kind <= 6 and Ab_FxCur != u then',
        '        set dur = dur * 0.5',
        '    endif',
    ], '''    set dur = dur * RW_FxDurMult(u, kind)  // v4.2x
    if dur <= 0.0 then
        return
    endif''', 'Ab_FxAdd')
    # ---- healing received (Damp, Unnerve, Drought)
    hm_start = p.s.find('function PAX_HealMult takes unit u returns real')
    hm_body = p.s[hm_start:p.s.find('endfunction', hm_start)] if hm_start >= 0 else ''
    heal_old = '        return 0.50' if 'return 0.50' in hm_body else '        return 0.40'
    p.in_function('function PAX_HealMult takes unit u returns real', heal_old,
                  heal_old + ' * RW_HealMult(u)', 'PAX_HealMult first branch')
    p.replace(['        return 0.60', '    endif', '    return 1.0', 'endfunction'],
              ['        return 0.60 * RW_HealMult(u)', '    endif', '    return RW_HealMult(u)', 'endfunction'], 'PAX_HealMult end')
    # ---- move speed / armor / attack speed of the Ability
    p.insert_before(['    set b = b + Fx_MSBonus(u)  // v3.4.11: Speed stage'],
                    '    set b = b + RW_MSBonus(u)  // v4.2x', 'Ab_MoveBonus')
    p.replace(['        set want = R2I(Fx_ArmorStep * I2R(Fx_StageNow(u, 2)))'],
              ['        set want = R2I(Fx_ArmorStep * I2R(Fx_StageNow(u, 2))) + RW_ArmorBonus(u)'], 'Fx_StatSync armor')
    p.replace(['        set want = R2I(1000.0 * 0.6 * (Fx_StageMult(u, 5) - 1.0))'],
              ['        set want = R2I(1000.0 * 0.6 * (Fx_StageMult(u, 5) - 1.0)) + R2I(1000.0 * RW_ASBonus(u))'],
              'Fx_StatSync attack speed')
    # ---- Thick Fat: +15% max HP
    if 'set want = want + R2I(0.1 * I2R(LoadInteger(Mega_HT, t, 80)) * f)' in p.s:
        p.replace([
            '    if LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_THICKFAT then  // v3.4: Thick Fat +10% max HP',
            '        set want = want + R2I(0.1 * I2R(LoadInteger(Mega_HT, t, 80)) * f)',
            '    endif',
        ], [
            '    if LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_THICKFAT then  // v3.4: Thick Fat +10% max HP',
            '        set want = want + R2I(0.1 * I2R(LoadInteger(Mega_HT, t, 80)) * f)',
            '    elseif LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_RW_THICKFAT then  // v4.2x: +15%',
            '        set want = want + R2I(0.15 * I2R(LoadInteger(Mega_HT, t, 80)) * f)',
            '    endif',
        ], 'Thick Fat HP')
    else:
        p.replace([
            '    if LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_THICKFAT then  // v3.4: Thick Fat +10% max HP',
            '        set want = want + R2I(0.1 * I2R(baseHP100) * fHP)',
            '    endif',
        ], [
            '    if LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_THICKFAT then  // v3.4: Thick Fat +10% max HP',
            '        set want = want + R2I(0.1 * I2R(baseHP100) * fHP)',
            '    elseif LoadInteger(Ab_HT, GetHandleId(u), 0) == AB_RW_THICKFAT then  // v4.2x: +15%',
            '        set want = want + R2I(0.15 * I2R(baseHP100) * fHP)',
            '    endif',
        ], 'Thick Fat HP (v4.2)')
    # ---- crits: the reworked Shell / Battle Armor cannot be crit; a crit is remembered (Anger Point)
    p.replace([
        '    if atk and critc > 0.0 and ta != AB_SHELLARMOR and ta != AB_BATTLEARMOR and GetRandomReal(0.0, 1.0) < critc then',
        '        set m = m * cm',
    ], [
        '    if atk and critc > 0.0 and ta != AB_SHELLARMOR and ta != AB_BATTLEARMOR and ta != AB_RW_SHELLARMOR and ta != AB_RW_BATTLEARMOR and GetRandomReal(0.0, 1.0) < critc then',
        '        set m = m * cm',
        '        set RW_LastCrit = true  // v4.2x',
    ], 'Ab_OutMult crit')
    p.replace([
        '                set mult = mult * 1.5',
        '                call Fx_Say(t, "Critical!", 255, 80, 80, src)',
    ], [
        '                if RW_Ab(src) == AB_RW_SNIPER then  // v4.2x Sniper',
        '                    set mult = mult * 2.25',
        '                else',
        '                    set mult = mult * 1.5',
        '                endif',
        '                set RW_LastCrit = true',
        '                call Fx_Say(t, "Critical!", 255, 80, 80, src)',
    ], 'Fx_OutMult move crit')
    # ---- stages
    p.insert_after([
        'function Fx_StageImmune takes unit u, integer s, unit src returns boolean',
        '    local integer abil = Ab_Num(u)',
        '    local integer lcode = Fx_Legend(u)',
        '    if src == null or src == u or not IsUnitEnemy(src, GetOwningPlayer(u)) then',
        '        return false',
        '    endif',
    ], '''    if RW_StageImmune(u, s) then  // v4.2x
        return true
    endif''', 'Fx_StageImmune')
    p.insert_before(['    if delta < 0 and Fx_StageImmune(u, s, src) then'], '''    if RW_Ab(u) == AB_RW_CONTRARY then  // v4.2x Contrary
        set delta = -delta
    endif
    if delta < 0 and src != null and src != u and RW_Ab(u) == AB_RW_SYNCHRONIZE and IsUnitEnemy(src, GetOwningPlayer(u)) then
        call Fx_StageAdd(src, s, delta, dur, null)
    endif''', 'Fx_StageAdd')
    # ---- hard CC, statuses, confusion, damage over time of statuses, push
    p.insert_after([
        'function Fx_HardCC takes unit t, real dur, unit src returns nothing',
        '    local integer hand = GetHandleId(t)',
        '    if not Ab_Alive(t) then',
        '        return',
        '    endif',
    ], '''    set dur = RW_HardCC(t, dur, src)  // v4.2x
    if dur <= 0.0 then
        return
    endif''', 'Fx_HardCC')
    p.insert_after([
        '    if t == null or kind < 1 or kind > 6 or not Ab_Alive(t) then',
        '        return false',
        '    endif',
        '    set hand = GetHandleId(t)',
        '    set wasActive = Fx_HasKind(t, kind)',
    ], '''    if RW_StatusBlock(t, kind, src) then  // v4.2x
        return false
    endif''', 'Fx_Status block')
    p.insert_before([
        '    if kind == 1 then',
        r'        call Ab_Pop(t, "Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl", "chest")',
    ], '''    set dur = dur * RW_StatusDur(t, kind, src)  // v4.2x
    call RW_QuickFeet(t)''', 'Fx_Status duration')
    p.replace([
        '        if abil == AB_SYNCHRONIZE then',
        '            call Fx_Status(src, kind, null)',
    ], [
        '        if abil == AB_SYNCHRONIZE or abil == AB_RW_SYNCHRONIZE then',
        '            call Fx_Status(src, kind, null)',
    ], 'Fx_Status Synchronize')
    p.insert_after(['function Fx_Confuse takes unit t, real dur, unit src returns nothing'], '''    if RW_ConfuseBlock(t) then  // v4.2x
        call Fx_Say(t, "No confusion", 200, 200, 200, src)
        return
    endif''', 'Fx_Confuse')
    p.insert_after([
        '    local unit src = LoadUnitHandle(Fx_HT, hand, 90 + kind)',
        '    if u != null and amount > 0.0 and Ab_Alive(u) then',
    ], '''        if RW_Ab(u) == AB_RW_MAGICGUARD then  // v4.2x
            set src = null
            return
        endif''', 'Fx_StatusDot')
    p.insert_after([
        'function Fx_Push takes unit u, real fromx, real fromy, real dist returns nothing',
        '    local real ang = Atan2(GetUnitY(u) - fromy, GetUnitX(u) - fromx)',
        '    local real nx = GetUnitX(u) + dist * Cos(ang)',
        '    local real ny = GetUnitY(u) + dist * Sin(ang)',
    ], '''    if RW_NoPush(u) then  // v4.2x
        return
    endif''', 'Fx_Push')
    # ---- move effects after a hit (Fx_AfterHit)
    header = 'function Fx_AfterHit takes unit src, unit t, boolean atk, boolean skill, integer mt, real dealt returns nothing'
    p.in_function(header, '        set mkey = Fx_CurMove(src)\n',
                  '        set mkey = Fx_CurMove(src)\n        if RW_NoSideFx(src, t) then  // v4.2x Sheer Force / Shield Dust\n            set mkey = 0\n        endif\n',
                  'Fx_AfterHit move key')
    p.in_function(header, '    if Ab_Num(src) == AB_SERENEGRACE or lcode == 16 then',
                  '    if Ab_Num(src) == AB_SERENEGRACE or Ab_Num(src) == AB_RW_SERENEGRACE or lcode == 16 then',
                  'Serene Grace')
    p.in_function(header, 'and Ab_Num(t) != AB_INNERFOCUS and not (tcode >= 1 and tcode <= 9) then',
                  'and Ab_Num(t) != AB_INNERFOCUS and Ab_Num(t) != AB_RW_INNERFOCUS and not (tcode >= 1 and tcode <= 9) then',
                  'Inner Focus flinch')
    p.in_function(header, '            if amount > 0.0 and Ab_Num(src) != AB_ROCKHEAD then',
                  '            if RW_Ab(src) == AB_RW_RECKLESS then  // v4.2x\n                set amount = amount * 0.7\n            endif\n'
                  '            if amount > 0.0 and Ab_Num(src) != AB_ROCKHEAD and Ab_Num(src) != AB_RW_ROCKHEAD and Ab_Num(src) != AB_RW_MAGICGUARD then',
                  'recoil')
    p.replace(['    if Ab_Num(v) == AB_INNERFOCUS then', '        call Fx_Say(v, "Unshaken", 200, 200, 200, Fx_ArgV)'],
              ['    if Ab_Num(v) == AB_INNERFOCUS or RW_NoIntimidate(v) then', '        call Fx_Say(v, "Unshaken", 200, 200, 200, Fx_ArgV)'],
              'Fx_IntimidateX')
    # ---- sandstorm / hail damage: Overcoat and Magic Guard take none
    p.replace([
        '        if (Wth_Cur == 3 and not Ty_Has(u, T_ROCK) and not Ty_Has(u, T_GROUND) and not Ty_Has(u, T_STEEL)) or (Wth_Cur == 4 and not Ty_Has(u, T_ICE)) then',
        '            call SetWidgetLife(u, GetWidgetLife(u) - 0.01 * mx)',
    ], [
        '        if ((Wth_Cur == 3 and not Ty_Has(u, T_ROCK) and not Ty_Has(u, T_GROUND) and not Ty_Has(u, T_STEEL)) or (Wth_Cur == 4 and not Ty_Has(u, T_ICE))) and RW_Ab(u) != AB_RW_OVERCOAT and RW_Ab(u) != AB_RW_MAGICGUARD then',
        '            call SetWidgetLife(u, GetWidgetLife(u) - 0.01 * mx)',
    ], 'weather damage')
    # ---- the damage trigger (Ab_OnDamaging)
    p.insert_before(['    set m = m * Ab_StateMult(src, skill, mt)'], '''    set RW_Converted = false  // v4.2x Ability rework
    set RW_LastCrit = false
    if skill and mt == T_NORMAL and s_ab == AB_RW_GALVANIZE then
        set mt = T_ELECTRIC
        set RW_Converted = true
    elseif skill and mt == T_NORMAL and s_ab == AB_RW_PIXILATE then
        set mt = T_FAIRY
        set RW_Converted = true
    endif
    set m = m * RW_Out(src, t, s_ab, ta, atk, skill, mt)''', 'Ab_OnDamaging out')
    p.replace(['        set m = m * eff', '    endif', '    set m = m * PAX_LightBallDamageMult(src, atk or skill)'],
              ['        set m = m * eff', '        set m = m * RW_Eff(src, t, s_ab, ta, atk, skill, mt, eff)  // v4.2x', '    endif',
               '    set m = m * PAX_LightBallDamageMult(src, atk or skill)'], 'Ab_OnDamaging type chart')
    p.insert_before(['    // the target\'s Ability (Mold Breaker ignores it)', '    if ta > 0 and s_ab != AB_MOLDBREAKER then'],
                    '''    set RW_Proc = true  // v4.2x: hits sent back by t inside this damage event
    set RW_ProcSrc = src
    set RW_ProcTgt = t
    set RW_DmgType = mt''', 'Ab_OnDamaging target section')
    p.replace(['        if skill and Ab_Absorbs(t, ta, mt, dmg * m) then'],
              ['        if skill and (Ab_Absorbs(t, ta, mt, dmg * m) or RW_Absorbs(t, ta, mt, dmg * m)) then'], 'Ab_Absorbs')
    p.replace(['        set m = m * Ab_InMult(src, t, ta, s_ab, atk, skill, mt, dmg * m)'],
              ['        set m = m * Ab_InMult(src, t, ta, s_ab, atk, skill, mt, dmg * m)',
               '        set m = m * RW_In(src, t, ta, s_ab, atk, skill, mt, dmg * m)  // v4.2x'], 'Ab_InMult')
    if '        call Fx_AfterHit(src, t, atk, skill, mt, dmg * m)  // v3.4.11' in p.s:
        p.replace(['        call Fx_AfterHit(src, t, atk, skill, mt, dmg * m)  // v3.4.11'],
                  ['        call Fx_AfterHit(src, t, atk, skill, mt, dmg * m)  // v3.4.11',
                   '        call RW_After(src, t, s_ab, ta, atk, skill, mt, dmg * m, eff)  // v4.2x'], 'Fx_AfterHit call')
        p.insert_before(['    if m > 0.0 then', '        call PAX_Leg_OnDamageProgress(src, dmg * m)'],
                        '''    set RW_Proc = false  // v4.2x
    set RW_DmgType = -1''', 'Ab_OnDamaging end of hits')
    else:
        p.replace(['        call Fx_AfterHit(src, t, atk, skill, mt, dealt)  // v3.4.11'],
                  ['        call Fx_AfterHit(src, t, atk, skill, mt, dealt)  // v3.4.11',
                   '        call RW_After(src, t, s_ab, ta, atk, skill, mt, dealt, eff)  // v4.2x',
                   '        set RW_Proc = false  // v4.2x',
                   '        set RW_DmgType = -1'], 'Fx_AfterHit call (v4.2)')
    # ---- start
    p.replace(['    call AbilityPatch_Init()'], ['    call AbilityPatch_Init()', '    call ExecuteFunc("RW_Init")  // v4.2x Ability rework'],
              'Mega_Init start')


def _specials(p):
    """the 5 Abilities kept on their numbers: new values in the old code"""
    p.replace(['        if a == AB_LEVITATE or a == AB_INNERFOCUS or a == AB_AIRLOCK then'],
              ['        if a == AB_LEVITATE or a == AB_INNERFOCUS then'], 'Air Lock dodge 1')
    p.replace(['        elseif a == AB_LEAFGUARD or a == AB_INSOMNIA or (a == AB_DEOXYSFORM and PAX_Form_Id(t) == 9) then'],
              ['        elseif a == AB_LEAFGUARD or a == AB_INSOMNIA or a == AB_AIRLOCK or (a == AB_DEOXYSFORM and PAX_Form_Id(t) == 9) then'],
              'Air Lock dodge 2')
    p.replace(['    elseif a == AB_PRESSURE or a == AB_AIRLOCK or a == AB_SANDSTREAM then', '        call Ab_Aura(u, a, 600.0)'],
              ['    elseif a == AB_AIRLOCK then', '        call Ab_Aura(u, a, 700.0)',
               '    elseif a == AB_PRESSURE or a == AB_SANDSTREAM then', '        call Ab_Aura(u, a, 600.0)'], 'Air Lock radius')
    p.replace(['                    if LoadInteger(Ab_HT, hv, 0) != AB_INSOMNIA then', '                        call Ab_Deal(u, v, 0.02 * mx)'],
              ['                    if LoadInteger(Ab_HT, hv, 0) != AB_INSOMNIA then', '                        call Ab_Deal(u, v, 0.03 * mx)'],
              'Bad Dreams')
    p.replace(['            set m = 0.7', '        else', '            set m = 1.5', '        endif', '    elseif a == AB_TOUGHCLAWS then'],
              ['            set m = 0.7', '        else', '            set m = 1.6', '        endif', '    elseif a == AB_TOUGHCLAWS then'],
              'Slow Start damage')
    p.replace(['    elseif a == AB_SLOWSTART then', '        if Mega_Time - LoadReal(Ab_HT, h, 9) >= 8.0 then', '            set m = 1.2'],
              ['    elseif a == AB_SLOWSTART then', '        if Mega_Time - LoadReal(Ab_HT, h, 9) >= 8.0 then', '            set m = 1.25'],
              'Slow Start attack speed')
    p.replace(['        if LoadInteger(Ab_HT, h, 85) == 1 then', '            if atk then', '                set m = 0.5'],
              ['        if LoadInteger(Ab_HT, h, 85) == 1 then', '            if atk then', '                set m = 0.7'], 'Zen Mode attacks')
    p.replace(['            if GetRandomReal(0.0, 1.0) < 0.2 then', '                set m = 0.0', '                call Ab_Say(t, "Bounce", 160, 120, 255, plA, plB)'],
              ['            if GetRandomReal(0.0, 1.0) < 0.25 then', '                set m = 0.0', '                call Ab_Say(t, "Bounce", 160, 120, 255, plA, plB)'],
              'Magic Bounce block')
    p.replace(['            else', '                call Ab_Deal(t, src, 0.35 * d)', '            endif'],
              ['            else', '                call Ab_Deal(t, src, 0.40 * d)', '            endif'], 'Magic Bounce reflect')


def _defaults(p):
    """approved default Ability of every roster hero (new number for reworked / new ones)"""
    old = _old_index(p.s)
    for hid, name in sorted(DATA['hero_default'].items()):
        if name in RW_INDEX:
            num = RW_INDEX[name]
        elif name in old:
            num = old[name]
        else:
            raise ValueError('[ability_rw] %s: Ability %s has no number' % (hid, name))
        pat = re.compile(r"call SaveInteger\(Ab_HT, '%s', 0, \d+\)" % re.escape(hid))
        hits = pat.findall(p.s)
        if not hits:  # some heroes have 2 lines (a later line overrides, e.g. Entei / Suicune): all get the new one
            raise ValueError('[ability_rw] hero %s has no Ability line' % hid)
        p.s = pat.sub("call SaveInteger(Ab_HT, '%s', 0, %d)" % (hid, num), p.s)


def patch(script):
    if 'RW_HT' in script:
        raise ValueError('[ability_rw] already applied')
    p = Patcher(script)
    p.insert_after(['    hashtable AbilityPatch_HT = null'], _globals(), 'globals')
    p.insert_after(['endglobals', '// ======== [END FILE: 01_clean_globals.j] ========'], _read('ability_rw_early.j'), 'endglobals')
    p.insert_before(['function Fx_StageImmune takes unit u, integer s, unit src returns boolean'], _read('ability_rw_mid.j'), 'middle part')
    p.insert_before(['// condition of the one damage trigger: Leg_OnDamage first, then the skill scale, the move\'s type and the Abilities',
                     'function Ab_OnDamaging takes nothing returns boolean'], _read('ability_rw_main.j'), 'main part')
    p.insert_before(['function Mega_Init takes nothing returns nothing'], _data_block(script), 'data part')
    _hooks(p)
    _specials(p)
    _defaults(p)
    return p.s


# ---------------------------------------------------------------- object data
def patch_objects(abil_slk, strings_text):
    """info buttons for the new numbers: AbilityData.slk rows (tools/slk.Slk) cloned from 'AB01', and their
    CampaignAbilityStrings.txt sections. Returns the new strings text."""
    base = abil_slk.find('AB01')
    if base is None:
        raise ValueError('[ability_rw] AB01 not in AbilityData.slk')
    art = re.search(r'\[AB01\][^\[]*?Art=([^\r\n]*)', strings_text)
    icon = art.group(1) if art else r'ReplaceableTextures\CommandButtons\BTNSpellBookBLS.blp'
    eol = '\r\n' if '\r\n' in strings_text else '\n'
    add = []
    for name in RW_ORDER:
        oid = info_id(RW_INDEX[name])
        if abil_slk.find(oid) is not None:
            raise ValueError('[ability_rw] %s already exists' % oid)
        row = dict(base)
        row[1] = '"%s"' % oid
        abil_slk.rows.append(row)
        add.append(eol.join(['[%s]' % oid, 'Name=Ability: %s' % name, 'Art=%s' % icon, 'Buttonpos=3,1',
                             'Tip=Ability: |cffffcc00%s|r' % name, 'Ubertip=%s' % RW_TEXT[name]]))
    return strings_text.rstrip('\r\n') + eol + eol.join(add) + eol
