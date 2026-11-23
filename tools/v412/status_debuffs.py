"""v4.1.2: 9 new debuff moves, Transform (Ditto), and visible stat stage buff icons.
Adds the missing 10 status moves (indices 58..67) and 18 visible stage buff auras (AF1A.. / BF1A..).
"""
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import status_moves as SM
import build as v3411_build

STAGE_ICONS = v3411_build.STAGE_ICONS
copy_section = v3411_build.copy_section
set_keys = v3411_build.set_keys


def patch_objects(abil, buffs, strings):
    col = abil.name_to_x
    dig = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    templates = {0: ('AV8V', 'AW8V', 'AY8V', 'AZ8V'), 1: ('AV00', 'AW00', 'AY00', 'AZ00')}
    buttons = []

    # 1. Add missing status moves (indices 58..67)
    for k in range(58, len(SM.MOVES)):
        name, ty, _act, tt, _params, cd, mana, icon, desc = SM.MOVES[k]
        mi = SM.STAT_BASE + k
        for slot, letter in enumerate('VWYZ'):
            new = 'A%s%s%s' % (letter, dig[mi // 36], dig[mi % 36])
            tmpl = templates[tt][slot]
            if abil.find(new) is None:
                r = dict(abil.find(tmpl))
                r[1] = '"%s"' % new
                r[col['Cool1']] = str(cd)
                r[col['Cost1']] = str(mana)
                if tt == 1:
                    r[col['Rng1']] = '600'
                    r[col['targs1']] = '"air,ground,enemy,neutral"'
                abil.rows.append(r)
            buttons.append((new, tmpl, name, ty, icon, desc))

    # 2. Add bonus stat abilities AF0A, AF0D, AF0S
    bonus_new = []
    for new, tmpl in (('AF0A', 'A08H'), ('AF0D', 'AId2'), ('AF0S', 'AMB3')):
        if abil.find(new) is None:
            r = dict(abil.find(tmpl))
            r[1] = '"%s"' % new
            r[col['levels']] = '2'
            r[col['item']] = '1'
            for c in ('DataA1', 'DataA2'):
                r[col[c]] = '0'
            abil.rows.append(r)
            bonus_new.append((new, tmpl))

    # 3. Add 18 visible stage buff icons AF1A.. / BF1A..
    icon_new = []
    for k, (_tip, _txt, _icon) in enumerate(STAGE_ICONS):
        aid, bid = 'AF1' + chr(65 + k), 'BF1' + chr(65 + k)
        if abil.find(aid) is None:
            r = dict(abil.find('AOae'))
            r[1] = '"%s"' % aid
            r[col['levels']] = '1'
            r[col['item']] = '1'
            r[col['hero']] = '0'
            r[col['DataA1']] = '0'
            r[col['DataB1']] = '0'
            r[col['Area1']] = '10'
            r[col['targs1']] = '"self"'
            r[col['BuffID1']] = '"%s"' % bid
            abil.rows.append(r)
        if buffs.find(bid) is None:
            r = dict(buffs.find('BOae'))
            r[1] = '"%s"' % bid
            buffs.rows.append(r)
        icon_new.append((aid, bid, k))

    # 4. Strings tooltips
    for new, tmpl, name, ty, icon, desc in buttons:
        tm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % tmpl, strings, re.S)
        hot = re.search(r'\[(\w)\]', re.search(r'(?m)^Tip=(.*)$', tm.group(1)).group(1)).group(1)
        strings = copy_section(strings, tmpl, new)
        strings = set_keys(strings, new, [('Name', name), ('Art', SM.ICON % icon),
                                          ('Tip', '|cffffcc00%s [%s]|r' % (name, hot)),
                                          ('Ubertip', '"%s|n|cffffcc00Status move:|r %s."' % (desc, ty.capitalize()))])

    for new, tmpl in bonus_new:
        strings = copy_section(strings, tmpl, new)
        strings = set_keys(strings, new, [('Name', 'Stage bonus'), ('EditorSuffix', '(v3.4.16)')])

    for aid, bid, k in icon_new:
        tip, txt, icon = STAGE_ICONS[k]
        strings = copy_section(strings, 'AOae', aid)
        strings = set_keys(strings, aid, [('Name', tip), ('Targetart', ''), ('Casterart', ''), ('Areaeffectart', ''),
                                          ('Specialart', '')])
        strings = copy_section(strings, 'BOae', bid)
        strings = set_keys(strings, bid, [('Bufftip', tip), ('Buffubertip', '"%s"' % txt),
                                          ('Buffart', 'ReplaceableTextures\\CommandButtons\\' + icon + '.blp'),
                                          ('Targetart', ''), ('Effectart', ''), ('Specialart', '')])

    return strings


def patch_script(s):
    # 1. Add globals
    old_glob = 'hashtable Fx_HT = InitHashtable()'
    new_glob = '''hashtable Fx_HT = InitHashtable()
constant integer Fx_IconUp = 'AF1A'     // v3.4.16: buff icons
constant integer Fx_IconDown = 'AF1F'
constant integer Fx_IconStatus = 'AF1K'
constant integer Fx_IconConf = 'AF1Q'
constant integer Fx_IconAcc = 'AF1R'
constant real Fx_ArmorStep = 3.0
constant integer Fx_AbAtk = 'AF0A'
constant integer Fx_AbDef = 'AF0D'
constant integer Fx_AbSpd = 'AF0S' '''
    if old_glob not in s:
        raise SystemExit('status_debuffs: hashtable Fx_HT not found')
    s = s.replace(old_glob, new_glob, 1)

    # 2. Add helper functions before Fx_Show
    helper_code = '''function Fx_BonusSet takes unit u, integer abil returns ability
    if GetUnitAbilityLevel(u, abil) == 0 then
        call UnitAddAbility(u, abil)
        call UnitMakeAbilityPermanent(u, true, abil)
    endif
    return BlzGetUnitAbility(u, abil)
endfunction

function Fx_BonusRefresh takes unit u, integer abil returns nothing
    call IncUnitAbilityLevel(u, abil)
    call DecUnitAbilityLevel(u, abil)
endfunction

function Fx_Icon takes unit u, integer abil, boolean on returns nothing
    if on and GetUnitAbilityLevel(u, abil) == 0 then
        call UnitAddAbility(u, abil)
        call UnitMakeAbilityPermanent(u, true, abil)
        call BlzUnitHideAbility(u, abil, true)
    elseif not on and GetUnitAbilityLevel(u, abil) > 0 then
        call UnitRemoveAbility(u, abil)
    endif
endfunction

function Fx_StageNow takes unit u, integer k returns integer
    local integer hand = GetHandleId(u)
    if Mega_Time >= LoadReal(Fx_HT, hand, 10 + k) then
        return 0
    endif
    return LoadInteger(Fx_HT, hand, k)
endfunction

function Fx_StatSync takes unit u returns nothing
    local integer hand = GetHandleId(u)
    local integer want = 0
    local integer k = 1
    local integer stage = 0
    local integer st = 0
    local boolean alive = (u != null and GetWidgetLife(u) > 0.405)
    local ability fxAbil = null
    // attack damage
    if alive then
        set want = R2I(I2R(BlzGetUnitBaseDamage(u, 0)) * (Fx_StageMult(u, 1) - 1.0))
    endif
    if want != LoadInteger(Fx_HT, hand, 82) then
        set fxAbil = Fx_BonusSet(u, Fx_AbAtk)
        call BlzSetAbilityIntegerLevelField(fxAbil, ABILITY_ILF_ATTACK_BONUS, 0, want)
        call Fx_BonusRefresh(u, Fx_AbAtk)
        call SaveInteger(Fx_HT, hand, 82, want)
    endif
    // armor
    set want = 0
    if alive then
        set want = R2I(Fx_ArmorStep * I2R(Fx_StageNow(u, 2)))
    endif
    if want != LoadInteger(Fx_HT, hand, 83) then
        set fxAbil = Fx_BonusSet(u, Fx_AbDef)
        call BlzSetAbilityIntegerLevelField(fxAbil, ABILITY_ILF_DEFENSE_BONUS_IDEF, 0, want)
        call Fx_BonusRefresh(u, Fx_AbDef)
        call SaveInteger(Fx_HT, hand, 83, want)
    endif
    // attack speed
    set want = 0
    if alive then
        set want = R2I(1000.0 * 0.6 * (Fx_StageMult(u, 5) - 1.0))
    endif
    if want != LoadInteger(Fx_HT, hand, 84) then
        set fxAbil = Fx_BonusSet(u, Fx_AbSpd)
        call BlzSetAbilityRealLevelField(fxAbil, ABILITY_RLF_ATTACK_SPEED_INCREASE_ISX1, 0, I2R(want) / 1000.0)
        call Fx_BonusRefresh(u, Fx_AbSpd)
        call SaveInteger(Fx_HT, hand, 84, want)
    endif
    // buff bar icons
    loop
        exitwhen k > 5
        set stage = 0
        if alive then
            set stage = Fx_StageNow(u, k)
        endif
        call Fx_Icon(u, Fx_IconUp + k - 1, stage > 0)
        call Fx_Icon(u, Fx_IconDown + k - 1, stage < 0)
        set k = k + 1
    endloop
    set st = 0
    if alive and Fx_HasStatus(u) then
        set st = LoadInteger(Fx_HT, hand, 20)
    endif
    set k = 1
    loop
        exitwhen k > 6
        call Fx_Icon(u, Fx_IconStatus + k - 1, st == k)
        set k = k + 1
    endloop
    call Fx_Icon(u, Fx_IconConf, alive and Mega_Time < LoadReal(Fx_HT, hand, 24))
    call Fx_Icon(u, Fx_IconAcc, alive and Mega_Time < LoadReal(Fx_HT, hand, 26))
    set fxAbil = null
endfunction

function Fx_ShowLine takes unit u returns string'''
    if 'function Fx_ShowLine takes unit u returns string' not in s:
        raise SystemExit('status_debuffs: function Fx_ShowLine not found')
    s = s.replace('function Fx_ShowLine takes unit u returns string', helper_code, 1)

    # 3. Add act == 29 (Transform) to Fx_DoStatusMove
    old_taunt = '''    elseif act == 28 then
        call SaveReal(Fx_HT, GetHandleId(tgt), 66, Mega_Time + 4.0)
        call Fx_Say(tgt, "Taunted!", 255, 120, 120, u)
    endif'''
    new_taunt = '''    elseif act == 28 then
        call SaveReal(Fx_HT, GetHandleId(tgt), 66, Mega_Time + 4.0)
        call Fx_Say(tgt, "Taunted!", 255, 120, 120, u)
    elseif act == 29 then  // v3.4.16 Transform: the target's look for 30 s + its raised stats
        call BlzSetUnitSkin(u, GetUnitTypeId(tgt))
        set kind = 1
        loop
            exitwhen kind > 5
            if Fx_StageNow(tgt, kind) > 0 then
                call Fx_StageAdd(u, kind, Fx_StageNow(tgt, kind), 20.0, u)
            endif
            set kind = kind + 1
        endloop
        call SaveReal(Fx_HT, hand, 85, Mega_Time + 30.0)
        call Fx_Track(u)
        call Fx_Say(u, "Transformed into " + GetUnitName(tgt) + "!", 255, 200, 255, tgt)
    endif'''
    if old_taunt not in s:
        raise SystemExit('status_debuffs: act == 28 block in Fx_DoStatusMove not found')
    s = s.replace(old_taunt, new_taunt, 1)

    # 4. Call Fx_StatSync in Fx_Show and Fx_Unshow
    old_show = '''function Fx_Show takes unit u returns nothing
    local integer hand = GetHandleId(u)
    local string line = Fx_ShowLine(u)
    local texttag tt = null
    local boolean up = false
    local boolean down = false
    local integer k = 1
    local integer stage = 0
    if u == null or not Ab_Alive(u) then
        call Fx_Unshow(u)
        set tt = null
        return
    endif'''
    new_show = old_show + '\n    call Fx_StatSync(u)  // v3.4.16 visible sync'
    if old_show not in s:
        raise SystemExit('status_debuffs: Fx_Show block not found')
    s = s.replace(old_show, new_show, 1)

    old_unshow = '''function Fx_Unshow takes unit u returns nothing
    local integer hand = 0
    if u == null then
        return
    endif
    set hand = GetHandleId(u)
    if HaveSavedHandle(Fx_HT, hand, 74) then'''
    new_unshow = '''function Fx_Unshow takes unit u returns nothing
    local integer hand = 0
    if u == null then
        return
    endif
    call Fx_StatSync(u)  // v3.4.16
    set hand = GetHandleId(u)
    if HaveSavedHandle(Fx_HT, hand, 74) then'''
    if old_unshow not in s:
        raise SystemExit('status_debuffs: Fx_Unshow block not found')
    s = s.replace(old_unshow, new_unshow, 1)

    # 5. Vitamin Stat Item Cap (Protein, Calcium, Carbos, HP Up): Infinite stock, max 100 consumption per Pokemon
    old_item_pickup = '''    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif'''

    new_item_pickup = '''    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    // Vitamin Stat Cap (Protein, Calcium, Carbos, HP Up): Infinite purchases, max 100 consumption per Pokemon
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set s = GetItemTypeId(it)
        set n = 0
        set lim = 0
        if s == 'I005' then      // Protein (+1 Str, 200g)
            set n = 1
            set lim = 200
        elseif s == 'I004' then  // Calcium (+1 Int, 200g)
            set n = 1
            set lim = 200
        elseif s == 'I006' then  // Carbos (+1 Agi, 200g)
            set n = 1
            set lim = 200
        elseif s == 'I003' then  // HP Up (+50 HP, 200g)
            set n = 1
            set lim = 200
        elseif s == 'I002' then  // Protein x5 (+5 Str, 150g)
            set n = 5
            set lim = 150
        elseif s == 'I001' then  // Calcium x5 (+5 Int, 150g)
            set n = 5
            set lim = 150
        elseif s == 'I000' then  // Carbos x5 (+5 Agi, 150g)
            set n = 5
            set lim = 150
        endif
        if n > 0 then
            set k = LoadInteger(PAX_Leg_HT, GetHandleId(u), 90)
            if k + n > 100 then
                // Revert stat gain
                if s == 'I005' or s == 'I002' then
                    call SetHeroStr(u, GetHeroStr(u, false) - n, true)
                elseif s == 'I004' or s == 'I001' then
                    call SetHeroInt(u, GetHeroInt(u, false) - n, true)
                elseif s == 'I006' or s == 'I000' then
                    call SetHeroAgi(u, GetHeroAgi(u, false) - n, true)
                elseif s == 'I003' then
                    call BlzSetUnitMaxHP(u, BlzGetUnitMaxHP(u) - 50)
                    if GetWidgetLife(u) > I2R(BlzGetUnitMaxHP(u)) then
                        call SetWidgetLife(u, I2R(BlzGetUnitMaxHP(u)))
                    endif
                endif
                // Refund gold
                call AdjustPlayerStateBJ(lim, GetOwningPlayer(u), PLAYER_STATE_RESOURCE_GOLD)
                call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff5c5c[VITAMINS]|r Maximum 100 Vitamin limit reached (" + I2S(k) + "/100)! Gold refunded.|r")
                set u = null
                set it = null
                set x = null
                return
            else
                call SaveInteger(PAX_Leg_HT, GetHandleId(u), 90, k + n)
                call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 4.0, "|cff4ade80[VITAMINS]|r Vitamin applied (" + I2S(k + n) + "/100).|r")
            endif
        endif
    endif'''
    if old_item_pickup not in s:
        raise SystemExit('status_debuffs: old_item_pickup block not found')
    s = s.replace(old_item_pickup, new_item_pickup, 1)

    return s
