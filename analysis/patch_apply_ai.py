"""One-off edit of tools/v34/apply.py: caster AI wiring (orders data, elite / legend patches, timer)."""
p = 'tools/v34/apply.py'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)


rep("def gen_ty_init(moves, gym_pool, gym_evo):", "def gen_ty_init(moves, gym_pool, gym_evo, orders=()):")
rep("""            lines.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (a, 301 + 2 * k, lv))
    lines.append('endfunction')
""", """            lines.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (a, 301 + 2 * k, lv))
    for abil, order in orders:  # Ai_Tick: order string of each kit skill (Ab_HT key 58 on the skill)
        lines.append("    call SaveStr(Ab_HT, '%s', 58, %s)" % (abil, jstr(order)))
    lines.append('endfunction')
""")
rep("""def old_ability_links(script):""", """def kit_orders(map_path, script):
    \"\"\"[(skill id, order string)] for the 90 kit skills (Wild_KitSkill), read from CampaignAbilityStrings.txt\"\"\"
    text = mpq.MPQ(map_path).read('Units\\\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    out = []
    for abil in dict.fromkeys(re.findall(r"set Wild_KitSkill\\[\\d+\\] = '(\\w{4})'", script)):
        m = re.search(r'\\[%s\\]\\r?\\n((?:[^\\[\\r\\n][^\\r\\n]*\\r?\\n?)*)' % abil, text)
        o = re.search(r'(?m)^Order=(\\w+)', m.group(1)) if m else None
        if o:
            out.append((abil, o.group(1)))
    return out


def old_ability_links(script):""")
rep("""GYM_HEADER = """, """ELITE_OLD = ('            call UnitAddAbility(u, Wild_KitSkill[(k - 1) * 5 + j])\\n'
             '            set j = j + 1\\n'
             '        endloop\\n'
             '    endif\\n')
ELITE_NEW = ('            call UnitAddAbility(u, Wild_KitSkill[(k - 1) * 5 + j])\\n'
             '            set j = j + 1\\n'
             '        endloop\\n'
             '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\\n'
             '    endif\\n')
LEG_OLD = '    call SaveInteger(Ab_HT, GetHandleId(lg), 0, LoadInteger(Ab_HT, Leg_Type[i], 0))  // v3.3: legends have an Ability\\n'
LEG_NEW = LEG_OLD + '    call Ai_GiveKit(lg)  // v3.4: and the 5 skills of their type, cast by Ai_Tick\\n'
GYM_HEADER = """)
rep("def assemble(base_script, units, version):", "def assemble(base_script, units, version, orders=()):")
rep("gen_ty_init(moves, gym_pool, gym_evo)", "gen_ty_init(moves, gym_pool, gym_evo, orders)")
rep("""    script = replace_once(script, GYM_HEADER, snippet('types.j') + GYM_HEADER)""",
    """    script = replace_once(script, GYM_HEADER, snippet('types.j') + snippet('ai.j') + GYM_HEADER)
    script = replace_once(script, ELITE_OLD, ELITE_NEW)
    script = replace_once(script, LEG_OLD, LEG_NEW)""")
rep("""                          '    call TriggerAddCondition(t, Condition(function Ty_OnDeath))\\n')""",
    """                          '    call TriggerAddCondition(t, Condition(function Ty_OnDeath))\\n'
                          '    call TimerStart(CreateTimer(), 1.0, true, function Ai_Tick)\\n')""")
rep("""    script, report = assemble(base, units, version)""",
    """    script, report = assemble(base, units, version, kit_orders(args.map, base))""")
open(p, 'w', encoding='utf-8').write(s)
print('apply.py patched')
