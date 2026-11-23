"""Shell Bell lifesteal, visible lifesteal heals, Gym 8 badge armor break (GEMINI.md section 16).

Found on 4.2b_test (2026-11-22):
- Shell Bell (I01P) only had the WC3 Life Steal ability (A09S, base AIva, 10%). The map rewrites every attack's
  damage in Ab_OnDamaging (stat added, own defense formula, DAMAGE_TYPE_UNIVERSAL), and an orb does not stack
  with other orbs, so the native heal was tiny or missing. Fix: 10% of the final damage on attacks (5% on
  skills), counted with the Lifesteal charms in PAX_Loot_OnHitEx; A09S DataA1 set to 0 so it never heals twice.
- Lifesteal charms (PAX_Item_HT key 111) did heal, but nothing showed it. Fix: a green "+N" over the hero
  (at most once a second) for every lifesteal heal.
- Gym 8 badge (I01B): since 4.1.3f a hidden damage multiplier (V413_ArmorCut); the armor never looked lower and
  the A040 aura on the item has 0 armor. Fix: each hit lowers the target's armor by 20% for 3s ("-N armor"),
  refreshed while the holder keeps hitting, given back by GA_Tick (0.5s). Tooltip updated.
- Rocky Helmet (IB07): melee attackers lost 3% of THEIR OWN max HP (big creeps / bosses took huge damage, small
  ones almost none). Now they take 5% of the HOLDER's max HP per hit (user's request). Tooltip updated.

Usage in build_data (script with LF line ends):
    import item_fix
    script = item_fix.patch_script(script)
    item_fix.patch_objects(abil)                 # abil = slk.Slk of Units\\AbilityData.slk
    item_func = item_fix.patch_item_text(item_func)
"""
import jpatch

WHO = 'item_fix'
MARK = '// item_fix (tools/v412/item_fix.py)'
GLOBALS = (MARK + ': Shell Bell lifesteal and Gym 8 armor break\nconstant integer IF_BellLS = 10\n'
           'hashtable IF_HT = InitHashtable()\nhashtable GA_HT = InitHashtable()\ngroup GA_G = CreateGroup()\n'
           'constant real GA_Pct = 0.20\nconstant real GA_Dur = 3.0\nconstant real IF_HelmetPct = 0.05\n')

OLD_LS = """    set val = LoadInteger(PAX_Item_HT, h, 111)
    if val > 0 and GetWidgetLife(src) > 0.405 then
        if not isAtk and isSkill then
            set lsMult = 0.50
        endif
        set heal = GetWidgetLife(src) + finalDmg * I2R(val) * 0.01 * lsMult * PAX_HealMult(src)
        if heal > I2R(BlzGetUnitMaxHP(src)) then
            set heal = I2R(BlzGetUnitMaxHP(src))
        endif
        call SetWidgetLife(src, heal)
    endif
"""
NEW_LS = """    set val = LoadInteger(PAX_Item_HT, h, 111) + IF_BellPct(src)  // item_fix: + Shell Bell
    if val > 0 and GetWidgetLife(src) > 0.405 then
        if not isAtk and isSkill then
            set lsMult = 0.50
        endif
        set heal = GetWidgetLife(src) + finalDmg * I2R(val) * 0.01 * lsMult * PAX_HealMult(src)
        if heal > I2R(BlzGetUnitMaxHP(src)) then
            set heal = I2R(BlzGetUnitMaxHP(src))
        endif
        call IF_ShowHeal(src, heal - GetWidgetLife(src))
        call SetWidgetLife(src, heal)
    endif
"""
OLD_LS_V42 = """    set val = LoadInteger(PAX_Item_HT, h, 111)
    if val > 0 and GetWidgetLife(src) > 0.405 then
        set heal = GetWidgetLife(src) + finalDmg * I2R(val) * 0.01 * PAX_HealMult(src)
        if heal > I2R(BlzGetUnitMaxHP(src)) then
            set heal = I2R(BlzGetUnitMaxHP(src))
        endif
        if heal > GetWidgetLife(src) then
            call SetWidgetLife(src, heal)
"""
NEW_LS_V42 = """    set val = LoadInteger(PAX_Item_HT, h, 111) + IF_BellPct(src)  // item_fix: + Shell Bell
    if val > 0 and GetWidgetLife(src) > 0.405 then
        set heal = GetWidgetLife(src) + finalDmg * I2R(val) * 0.01 * PAX_HealMult(src)
        if heal > I2R(BlzGetUnitMaxHP(src)) then
            set heal = I2R(BlzGetUnitMaxHP(src))
        endif
        if heal > GetWidgetLife(src) then
            call IF_ShowHeal(src, heal - GetWidgetLife(src))
            call SetWidgetLife(src, heal)
"""
OLD_EXT_SHELL_V42 = """        if d > 0.0 and ((atk and not Ab_IsMelee(heroSrc)) or (not atk and skill)) and Itm_Has(heroSrc, 'I01P') and GetWidgetLife(heroSrc) > 0.405 then
            call SetWidgetLife(heroSrc, RMinBJ(mx, GetWidgetLife(heroSrc) + 0.10 * d * PAX_HealMult(heroSrc)))
            if Mega_Time - LoadReal(PAX_Item_HT, GetHandleId(heroSrc), 124) >= 0.8 then
                call SaveReal(PAX_Item_HT, GetHandleId(heroSrc), 124, Mega_Time)
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Undead\\\\VampiricAura\\\\VampiricAuraTarget.mdl", heroSrc, "origin"))
            endif
        endif
"""
OLD_GYM8_B = """    if Itm_Has(src, 'I01B') then  // v4.2b: Gym 8 badge, ignore 20% of the target's armor
        set m = m * V413_ArmorCut(t)
    endif
"""
OLD_GYM8_A = """    if Itm_Has(src, 'I01B') then  // v4.2a: Gym 8 badge, ignore 20% of the target's armor
        set m = m * V413_ArmorCut(t)
    endif
"""
OLD_GYM8 = OLD_GYM8_B
NEW_GYM8 = """    if Itm_Has(src, 'I01B') then  // item_fix: Gym 8 badge, the target's armor -20% for 3s (visible)
        call GA_Shred(src, t)
    endif
"""
OLD_RH = "        call Ab_Deal(t, src, 0.03 * I2R(BlzGetUnitMaxHP(src)))  // Rocky Helmet\n"
NEW_RH = ("        call Ab_Deal(t, src, IF_HelmetPct * I2R(BlzGetUnitMaxHP(t)))"
          "  // Rocky Helmet (item_fix: % of the holder's max HP)\n")
OLD_RH_TIP = 'Melee attackers lose 3% of their max HP per hit.'
NEW_RH_TIP = "Melee attackers take damage equal to 5% of the holder's max HP per hit."
TIMER_ANCHOR ='    call TimerStart(CreateTimer(), 1.0, true, function Ai_Tick)\n'
OLD_TIP = "Its holder's hits ignore 20% of the target's armor."
NEW_TIP = "Its holder's hits lower the target's armor by 20% for 3 seconds."


def patch_script(s):
    jpatch.check_lf(s, MARK, WHO)
    s = jpatch.once(s, 'real Wild_SoulChance = 20.0\n', 'real Wild_SoulChance = 20.0\n' + GLOBALS, 'globals', WHO)
    s = jpatch.once(s, '\nfunction PAX_Loot_OnHitEx takes',
                    '\n' + jpatch.read_jass('item_fix.j') + 'function PAX_Loot_OnHitEx takes', 'before OnHitEx', WHO)
    if OLD_LS in s:
        s = jpatch.once(s, OLD_LS, NEW_LS, 'charm lifesteal', WHO)
    else:
        s = jpatch.once(s, OLD_LS_V42, NEW_LS_V42, 'charm lifesteal (v4.2)', WHO)
        if OLD_EXT_SHELL_V42 in s:
            s = jpatch.once(s, OLD_EXT_SHELL_V42, '', 'remove duplicate v4.2 Shell Bell in Ext_AfterHit', WHO)
    if OLD_GYM8_B in s:
        s = jpatch.once(s, OLD_GYM8_B, NEW_GYM8, 'Gym 8 in Ab_OnDamaging', WHO)
    else:
        s = jpatch.once(s, OLD_GYM8_A, NEW_GYM8, 'Gym 8 in Ab_OnDamaging', WHO)
    if OLD_RH in s:
        s = jpatch.once(s, OLD_RH, NEW_RH, 'Rocky Helmet in Ext_AfterHit', WHO)
    elif 'reflectMult * I2R(BlzGetUnitMaxHP(t))' not in s:
        raise ValueError('[%s] Rocky Helmet anchor missing in Ext_AfterHit' % WHO)
    s = jpatch.once(s, TIMER_ANCHOR, TIMER_ANCHOR + '    call TimerStart(CreateTimer(), 0.5, true, function GA_Tick)\n',
                    'GA_Tick timer', WHO)
    return s


def patch_objects(abil):
    """the native Life Steal of the Shell Bell heals 0 (the script does it now)"""
    row = abil.find('A09S')
    x = abil.name_to_x.get('DataA1')
    if row is None or x is None:
        raise ValueError('[item_fix] A09S / DataA1 not found in AbilityData.slk')
    row[x] = '0'
    return abil


def patch_item_text(item_func):
    if OLD_TIP not in item_func:
        raise ValueError('[item_fix] Gym 8 tooltip not found in ItemFunc.txt')
    out = item_func.replace(OLD_TIP, NEW_TIP)
    if OLD_RH_TIP in out:
        out = out.replace(OLD_RH_TIP, NEW_RH_TIP)
    elif 'Reflects 1% of your max HP to Heroes' not in out:
        raise ValueError('[item_fix] Rocky Helmet tooltip not found in ItemFunc.txt')
    return out
