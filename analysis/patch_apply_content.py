"""One-off edit of tools/v34/apply.py: wire tools/v34/content.py (Megas, new Pokemon, legend, wild creeps, Souls)."""
p = 'tools/v34/apply.py'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("import mega_look  # noqa: E402\n", "import mega_look  # noqa: E402\nimport content  # noqa: E402\n")
rep("""           'Regirock', 'Regigigas', 'Buzzwole', 'Kingambit'}""",
    """           'Regirock', 'Regigigas', 'Buzzwole', 'Kingambit', 'Latias & Latios'}""")
rep("""MANUAL_EVOLUTIONS = [
""", """MANUAL_EVOLUTIONS = [
    ('Bayleef', 'Meganium', 32), ('Porygon', 'Porygon2', 50),  # v3.4 new Pokemon (content.py)
""")
# Abilities: REPLACE (Darmanitan -> Zen Mode) for the playable units, extra links / Mega Abilities from content
rep("""    for uid, n in links:
        lines.append("    call SaveInteger(Ab_HT, '%s', 0, %d)" % (uid, n))""",
    """    for uid, o in sorted(units.items()):
        pro = (o.get('upro') or '').split(',')[0].strip()
        if uid[0].isupper() and pro in abilities.REPLACE:
            links = [(u, names[abilities.REPLACE[pro]] if u == uid else n) for u, n in links]
            report.append('Ability of %s %s -> %s' % (uid, pro, abilities.REPLACE[pro]))
    for uid, n in links:
        lines.append("    call SaveInteger(Ab_HT, '%s', 0, %d)" % (uid, n))""")
rep("def assemble(base_script, units, version, orders=()):",
    "def assemble(base_script, units, version, orders=(), extra=None):")
rep("""    links, megas = old_ability_links(script)
""", """    links, megas = old_ability_links(script)
    if extra is not None:
        links += extra.links
        megas += extra.megas
""")
rep("""    gen = '\\n'.join([gen_ab_init(links, megas, units, report), gen_ty_init(moves, gym_pool, gym_evo, orders), gen_ty_units(types)])""",
    """    gen = '\\n'.join([gen_ab_init(links, megas, units, report), gen_ty_init(moves, gym_pool, gym_evo, orders), gen_ty_units(types)])
    calls = ''
    if extra is not None:
        cfuncs, calls = extra.jass()
        gen = cfuncs + '\\n' + gen""")
rep("""    script = replace_once(script, ELITE_OLD, ELITE_NEW)
""", """    script = replace_once(script, ELITE_OLD, ELITE_NEW)
    # wild: pick by power (index), the new species take their stats from the power of the camp
    script = replace_functions(script, snippet('wild.j'))
    script = replace_once(script, '\\nfunction Wild_Apply takes', '\\n' + WILD_POWSTATS + '\\nfunction Wild_Apply takes')
    script = replace_once(script, WILD_APPLY_OLD, WILD_APPLY_NEW)
""")
rep("""    script = replace_once(script, '    call Wild_RegisterCamps()\\n', '    call Wild_RegisterCamps()\\n    call Ty_InitKits()\\n')""",
    """    script = replace_once(script, '    call Wild_RegisterCamps()\\n', calls + '    call ExecuteFunc("Wild_IndexPool")\\n'
                          '    call Wild_RegisterCamps()\\n    call Ty_InitKits()\\n')""")
rep("""GYM_HEADER = """, """# v3.4: the 211 new wild species (Mega_HT key 39 on their type) take damage / armor / gold / level from the power of
# their camp (key 31), so one species can appear at several powers
WILD_POWSTATS = ('function Wild_PowStats takes unit u returns nothing\\n'
                 '    local integer h = GetHandleId(u)\\n'
                 '    local integer powi = LoadInteger(Mega_HT, h, 31)\\n'
                 '    if powi > 10 then\\n'
                 '        set powi = 10\\n'
                 '    endif\\n'
                 '    call SaveReal(Mega_HT, h, 37, Wild_PowDmg[powi])\\n'
                 '    call SaveReal(Mega_HT, h, 22, Wild_PowArm[powi])\\n'
                 '    call SaveInteger(Mega_HT, h, 23, Wild_PowGold[powi])\\n'
                 '    call SaveInteger(Mega_HT, h, 26, Wild_PowLv[powi])\\n'
                 'endfunction\\n')
WILD_APPLY_OLD = ('        if not HaveSavedInteger(Mega_HT, h, 26) then\\n'
                  '            call SaveInteger(Mega_HT, h, 26, GetUnitLevel(u))\\n'
                  '        endif\\n'
                  '    endif\\n')
WILD_APPLY_NEW = ('        if not HaveSavedInteger(Mega_HT, h, 26) then\\n'
                  '            call SaveInteger(Mega_HT, h, 26, GetUnitLevel(u))\\n'
                  '        endif\\n'
                  '        if LoadInteger(Mega_HT, GetUnitTypeId(u), 39) > 0 and LoadInteger(Mega_HT, h, 31) > 0 then\\n'
                  '            call Wild_PowStats(u)\\n'
                  '        endif\\n'
                  '    endif\\n')
GYM_HEADER = """)
rep("""    units = unit_data(args.map)
    script, report = assemble(base, units, version, kit_orders(args.map, base))""",
    """    units = unit_data(args.map)
    extra = content.make(base, units, mpq.MPQ(args.map))
    MEGA_TYPES.update(extra.mega_types)
    units.update(extra.units)
    script, report = assemble(base, units, version, kit_orders(args.map, base), extra)
    report = extra.report + report""")
open(p, 'w', encoding='utf-8').write(s)
print('apply.py patched')
