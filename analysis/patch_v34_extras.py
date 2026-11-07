"""One-off edits for the v3.4 extras: ab_head.j / ab_core.j / ab_tick.j hooks, content.py -> extras.py,
apply.py patches of the v3.3.3 script (Everstone, Shiny copy, Mega Ring, elite Mega, creep forms, item limit,
stones / Souls, wiring)."""
import re


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


edit('tools/v34/jass/ab_head.j', [(
    """        call Ab_Strip(u)
        set have = 0
""", """        call Ab_Strip(u)
        set have = 0
        call Shiny_Decide(u)  // v3.4
""")])

core = open('tools/v34/jass/ab_core.j', encoding='utf-8').read()
m = re.search(r'(?ms)^function Ab_ASMult takes.*?\n(    return m\nendfunction)', core)
core = core[:m.start(1)] + ('    if IsUnitType(u, UNIT_TYPE_HERO) and Itm_Flag(u, 3) then  // v3.4 Choice Scarf\n'
                            '        set m = m * 1.2\n'
                            '    endif\n') + core[m.start(1):]
open('tools/v34/jass/ab_core.j', 'w', encoding='utf-8').write(core)
edit('tools/v34/jass/ab_core.j', [
    ("""            set dodge = 0.25
        endif
""", """            set dodge = 0.25
        endif
        if (a == AB_SANDVEIL and Wth_Cur == 3) or (a == AB_SNOWCLOAK and Wth_Cur == 4) then  // v3.4 weather
            set dodge = dodge + 0.15
        endif
"""),
    ("""    if Mega_Time < LoadReal(Ab_HT, h, 69) then  // Run Away dash""",
     """    if (a == AB_SWIFTSWIM and Wth_Cur == 1) or (a == AB_CHLOROPHYLL and Wth_Cur == 2) then  // v3.4 weather
        set b = b + 0.3 * GetUnitDefaultMoveSpeed(u)
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) then  // v3.4 Choice Scarf / Band / Specs
        if Itm_Flag(u, 3) then
            set b = b + 0.3 * GetUnitDefaultMoveSpeed(u)
        endif
        if Itm_Flag(u, 1) or Itm_Flag(u, 2) then
            set b = b - 0.1 * GetUnitDefaultMoveSpeed(u)
        endif
    endif
    if Mega_Time < LoadReal(Ab_HT, h, 69) then  // Run Away dash"""),
])
edit('tools/v34/jass/ab_tick.j', [
    ("""    call Ab_Pulse(u, a)
endfunction""", """    call Ab_Pulse(u, a)
    call Ext_Pulse(u)
endfunction"""),
    ("""        set m = m * eff
    endif
""", """        set m = m * eff
    endif
    set m = m * Ext_DamageMult(src, t, atk, skill, mt, eff)  // v3.4 weather, items, Champion Aura, legend Mega
"""),
    ("""            call Ab_AfterHit(t, ta, dmg * m)
        endif
""", """            call Ab_AfterHit(t, ta, dmg * m)
        endif
        call Ext_AfterHit(src, t, atk, dmg * m)
        if GetUnitTypeId(t) == Leg_MewtwoId or GetUnitTypeId(t) == Leg_RayquazaId then
            call Leg_TryMega(t, dmg * m)
        endif
        call League_TryMega(t, dmg * m)
"""),
    ("""    call SaveReal(Ab_HT, ht, 1, Mega_Time)
    call BlzSetEventDamage(dmg * m)""", """    call SaveReal(Ab_HT, ht, 1, Mega_Time)
    set m = Ext_Final(t, dmg * m) / dmg  // v3.4 Focus Sash
    call BlzSetEventDamage(dmg * m)"""),
])
edit('tools/v34/content.py', [(
    """    _wild(c, script, allu, ids, by_name, links, soul_n, base, with_files)
    return c""", """    _wild(c, script, allu, ids, by_name, links, soul_n, base, with_files)
    import extras
    allu.update(c.units)
    extras.add(c, script, units, allu, ids, by_name, base)
    return c""")])
edit('tools/v34/extras.py', [(
    """    c.data += ["    set Ext_Shop[0] = 'nBS0'", "    set Ext_Shop[1] = 'nIS0'"]""",
    """    c.data += ["    set Ext_Shop[0] = 'nBS0'", "    set Ext_Shop[1] = 'nIS0'"]
    spots = [(-5392, -544), (-6304, -544), (-5088, -544), (-5392, -848), (-5696, -848), (-6000, -848),
             (-6304, -848), (-5088, -848), (-4784, -544), (-4784, -848)]
    for i, (x, y) in enumerate(spots):
        c.data += ['    set Ext_SpotX[%d] = %s' % (i, repr(float(-x))), '    set Ext_SpotY[%d] = %s' % (i, repr(float(y)))]
    c.data.append('    set Ext_SpotN = %d' % len(spots))""")])

A = 'tools/v34/apply.py'
s = open(A, encoding='utf-8').read()
consts = '''# ---- v3.4 extras: patches of the v3.3.3 script (docs/v3.5-items-league-features-proposal.md)
EARLY_HELPERS = (
    '// v3.4: does u carry an item of type id (early helper: Everstone, Mega Ring)\\n'
    'function Itm_Has takes unit u, integer id returns boolean\\n'
    '    local integer s = 0\\n'
    '    if id == 0 then\\n'
    '        return false\\n'
    '    endif\\n'
    '    loop\\n'
    '        exitwhen s >= 6\\n'
    '        if GetItemTypeId(UnitItemInSlot(u, s)) == id then\\n'
    '            return true\\n'
    '        endif\\n'
    '        set s = s + 1\\n'
    '    endloop\\n'
    '    return false\\n'
    'endfunction\\n\\n'
    '// v3.4: is `to` a direct evolution of `from` (gym evolution data: Ab_HT 299 / 300 + 2k on the type)\\n'
    'function Mega_IsEvolution takes integer from, integer to returns boolean\\n'
    '    local integer k = 0\\n'
    '    loop\\n'
    '        exitwhen k >= LoadInteger(Ab_HT, from, 299)\\n'
    '        if LoadInteger(Ab_HT, from, 300 + 2 * k) == to then\\n'
    '            return true\\n'
    '        endif\\n'
    '        set k = k + 1\\n'
    '    endloop\\n'
    '    return false\\n'
    'endfunction\\n\\n')
SAFE_OLD = ('    if HaveSavedReal(Mega_HT, h, 9) and Mega_Time - LoadReal(Mega_HT, h, 9) < 10.0 then\\n'
            '        return\\n'
            '    endif\\n')
SAFE_NEW = ('    if not Mega_EvoItem and Itm_Has(u, Itm_Everstone) and Mega_IsEvolution(GetUnitTypeId(u), newId) then\\n'
            '        return  // v3.4 Everstone: no level evolution (stones and Souls set Mega_EvoItem)\\n'
            '    endif\\n') + SAFE_OLD
SHINY_OLD = '    set nu = bj_lastReplacedUnit\\n    if nu != null then\\n'
SHINY_NEW = SHINY_OLD + ('        call SaveInteger(Ab_HT, GetHandleId(nu), 123, LoadInteger(Ab_HT, h, 123))  // v3.4 Shiny stays\\n'
                         '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)\\n')
RING_DUR_OLD = '    call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration)\\n'
RING_DUR_NEW = ('    if Itm_Has(u, Itm_MegaRing) then  // v3.4 Mega Ring: 90s\\n'
                '        call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration + 30.0)\\n'
                '    else\\n'
                '        call SaveReal(Mega_HT, h, 1, Mega_Time + Mega_Duration)\\n'
                '    endif\\n')
RING_CD_OLD = '            call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown)\\n'
RING_CD_NEW = ('            if Itm_Has(u, Itm_MegaRing) then  // v3.4 Mega Ring: recharges 30% faster\\n'
               '                call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown * 0.7)\\n'
               '            else\\n'
               '                call SaveReal(Mega_HT, h, 100 + i, Mega_Time + Mega_Cooldown)\\n'
               '            endif\\n')
ELITE_MEGA = (
    '// v3.4: an elite of a species that has a Mega is a Mega elite 1 time in 4 (Mega skin, +20% HP and damage,\\n'
    '// 5% to drop its Mega Stone). Mega_HT: key 41 on the type = Mega index + 1, key 44 on the unit\\n'
    'function Wild_EliteMega takes unit u returns nothing\\n'
    '    local integer mi = LoadInteger(Mega_HT, GetUnitTypeId(u), 41) - 1\\n'
    '    local real sc = 0.0\\n'
    '    if mi < 0 or mi >= Mega_N or GetRandomReal(0.0, 1.0) >= Wild_MegaChance then\\n'
    '        return\\n'
    '    endif\\n'
    '    call SaveInteger(Mega_HT, GetHandleId(u), 44, mi + 1)\\n'
    '    call BlzSetUnitSkin(u, Mega_Skin[mi])\\n'
    '    set sc = Wild_EliteScale * Mega_Scale[mi] / RMaxBJ(Mega_BaseScale[mi], 0.1)\\n'
    '    call SetUnitScale(u, sc, sc, sc)\\n'
    '    call SetUnitVertexColor(u, Mega_R[mi], Mega_G[mi], Mega_B[mi], 255)\\n'
    '    call BlzSetUnitName(u, Mega_Name[mi])\\n'
    '    call Wild_Scale(u)\\n'
    'endfunction\\n\\n')
SCALE_OLD = ('    if LoadInteger(Mega_HT, h, 29) == 1 then\\n'
             '        set hpf = Wild_EliteHP\\n'
             '        set dmf = Wild_EliteDmg\\n'
             '        set goldf = Wild_EliteGold\\n'
             '        set armf = Wild_EliteArmor\\n'
             '    endif\\n')
SCALE_NEW = SCALE_OLD + ('    if LoadInteger(Mega_HT, h, 44) > 0 then  // v3.4 Mega elite\\n'
                         '        set hpf = hpf * 1.2\\n'
                         '        set dmf = dmf * 1.2\\n'
                         '    endif\\n')
DROP_OLD = '        // v3.3.3: wild creeps no longer drop Mega Stones (only from the Mega Shops)\\n'
DROP_NEW = ('        if LoadInteger(Mega_HT, h, 44) > 0 and GetRandomReal(0.0, 100.0) < 5.0 then  // v3.4 Mega elite\\n'
            '            call CreateItem(Mega_Stone[LoadInteger(Mega_HT, h, 44) - 1], GetUnitX(u), GetUnitY(u))\\n'
            '            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff66ccA Mega elite dropped its Mega Stone!|r")\\n'
            '        endif\\n') + DROP_OLD
NEXT_FORM = (
    '// v3.4: what a camp becomes when the tier goes up: its own next form once that form\\'s power is reached\\n'
    '// (Mega_HT on the type: 45 next form, 47 / 48 the powers it appears at), the same species while still in range,\\n'
    '// else a random species of the power as before\\n'
    'function Wild_NextForm takes integer t, integer pow returns integer\\n'
    '    local integer cur = t\\n'
    '    local integer nt = LoadInteger(Mega_HT, t, 45)\\n'
    '    local integer guard = 0\\n'
    '    loop\\n'
    '        exitwhen nt == 0 or LoadInteger(Mega_HT, nt, 47) > pow or guard >= 3\\n'
    '        set cur = nt\\n'
    '        set nt = LoadInteger(Mega_HT, cur, 45)\\n'
    '        set guard = guard + 1\\n'
    '    endloop\\n'
    '    if cur != t then\\n'
    '        return cur\\n'
    '    endif\\n'
    '    if LoadInteger(Mega_HT, t, 48) >= pow then\\n'
    '        return t\\n'
    '    endif\\n'
    '    return Wild_PickType(pow)\\n'
    'endfunction\\n\\n')
UPG_OLD = '                    set Wild_UpT[c] = Wild_PickType(pow)\\n'
UPG_NEW = '                    set Wild_UpT[c] = Wild_NextForm(GetUnitTypeId(u), pow)\\n'
LIMIT_OLD = '    if k == 1 then\\n        set lim = Item_MaxBadges\\n    endif\\n'
LIMIT_NEW = LIMIT_OLD + '    if k == 3 then  // v3.4 battle items\\n        set lim = 3\\n    endif\\n'
LIMIT_MSG_OLD = ('        if k == 1 then\\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most " + I2S(lim) + " gym badges can be carried.|r")\\n'
                 '        else\\n')
LIMIT_MSG_NEW = ('        if k == 1 then\\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most " + I2S(lim) + " gym badges can be carried.|r")\\n'
                 '        elseif k == 3 then\\n'
                 '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffff4040At most 3 battle items can be held.|r")\\n'
                 '        else\\n')
EVO_ITEM_OLD = '            call Mega_SafeReplace(u, Evo_ItemTo[i], bj_UNIT_STATE_METHOD_RELATIVE)\\n'
EVO_ITEM_NEW = ('            set Mega_EvoItem = true\\n' + EVO_ITEM_OLD + '            set Mega_EvoItem = false\\n')
SOUL_OLD = '            call Mega_SafeReplace(u, Soul_Hero[i], bj_UNIT_STATE_METHOD_RELATIVE)\\n'
SOUL_NEW = ('            set Mega_EvoItem = true\\n' + SOUL_OLD + '            set Mega_EvoItem = false\\n'
            '            if bj_lastReplacedUnit != null then  // v3.4: a Soul rolls Shiny anew\\n'
            '                call RemoveSavedInteger(Ab_HT, GetHandleId(bj_lastReplacedUnit), 124)\\n'
            '                call SaveInteger(Ab_HT, GetHandleId(bj_lastReplacedUnit), 123, 0)\\n'
            '            endif\\n')
WIRING = ('    call TimerStart(CreateTimer(), 1.0, true, function League_Tick)\\n'
          '    call TimerStart(CreateTimer(), 300.0, true, function Wth_Tick)\\n'
          '    set t = CreateTrigger()\\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)\\n'
          '    call TriggerAddCondition(t, Condition(function League_OnDeath))\\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnKill))\\n'
          '    set t = CreateTrigger()\\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_PICKUP_ITEM)\\n'
          '    call TriggerAddCondition(t, Condition(function Ext_OnPickup))\\n'
          '    set t = CreateTrigger()\\n'
          '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_USE_ITEM)\\n'
          '    call TriggerAddAction(t, function Ext_OnUseItem)\\n'
          '    set t = CreateTrigger()\\n'
          '    set i = 0\\n'
          '    loop\\n'
          '        exitwhen i >= 12\\n'
          '        call TriggerRegisterPlayerChatEvent(t, Player(i), "-league", true)\\n'
          '        set i = i + 1\\n'
          '    endloop\\n'
          '    call TriggerAddAction(t, function League_OnChat)\\n')
'''
assert s.count('GYM_HEADER = ') == 1
s = s.replace('GYM_HEADER = ', consts + 'GYM_HEADER = ', 1)
s = s.replace("""             '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\\n'
             '    endif\\n')""", """             '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\\n'
             '    endif\\n'
             '    call Wild_EliteMega(u)\\n')""", 1)
assert 'call Wild_EliteMega(u)' in s
old = """    script = replace_once(script, ELITE_OLD, ELITE_NEW)
"""
new = """    script = replace_once(script, ELITE_OLD, ELITE_NEW)
    # v3.4 extras
    script = replace_once(script, '\\nfunction Mega_SafeReplace takes', '\\n' + EARLY_HELPERS + 'function Mega_SafeReplace takes')
    for o, n in ((SAFE_OLD, SAFE_NEW), (SHINY_OLD, SHINY_NEW), (RING_DUR_OLD, RING_DUR_NEW), (RING_CD_OLD, RING_CD_NEW),
                 (SCALE_OLD, SCALE_NEW), (DROP_OLD, DROP_NEW), (UPG_OLD, UPG_NEW), (LIMIT_OLD, LIMIT_NEW),
                 (LIMIT_MSG_OLD, LIMIT_MSG_NEW), (EVO_ITEM_OLD, EVO_ITEM_NEW), (SOUL_OLD, SOUL_NEW)):
        script = replace_once(script, o, n)
    script = replace_once(script, '\\nfunction Wild_MakeElite takes', '\\n' + ELITE_MEGA + 'function Wild_MakeElite takes')
    script = replace_once(script, '\\nfunction Wild_Upgrade takes', '\\n' + NEXT_FORM + 'function Wild_Upgrade takes')
"""
assert s.count(old) == 1
s = s.replace(old, new)
old = """    script = replace_range(script, 'Ab_Hero', 'Ab_OnDamaging', snippet('ab_tick.j'))
"""
new = """    script = replace_range(script, 'Ab_Hero', 'Ab_OnDamaging', snippet('ab_tick.j'))
    script = replace_once(script, '\\nfunction Ab_Hero takes', '\\n' + snippet('extra_late.j') + '\\nfunction Ab_Hero takes')
"""
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace("snippet('types.j') + snippet('ai.j') + GYM_HEADER", "snippet('types.j') + snippet('ai.j') + snippet('extra.j') + GYM_HEADER", 1)
old = """                          '    call TimerStart(CreateTimer(), 1.0, true, function Ai_Tick)\\n')"""
new = """                          '    call TimerStart(CreateTimer(), 1.0, true, function Ai_Tick)\\n' + WIRING)
    script = replace_once(script, '    call Base_Init()\\n', '    call Base_Init()\\n    call Ext_PlaceShops()\\n')"""
assert s.count(old) == 1
s = s.replace(old, new)
open(A, 'w', encoding='utf-8').write(s)
print('edited', A)
