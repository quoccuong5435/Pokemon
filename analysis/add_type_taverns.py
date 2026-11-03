"""One-off: type taverns (units, sell lists, grid positions, Evo_InitData creation), old tavern moved, picker select
hook removed, random starter pool extended, tests updated."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    crlf = (chr(13) + NL) in s
    if crlf:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# the Gen 3-4 tavern moves to grid slot 0
edit('tools/poke_data.py', 'TAVERN_POS = (448.0, 4512.0, 270.0)',
     'TAVERN_POS = (-1250.0, 4800.0, 270.0)  # v3.3: slot 0 of the tavern grid (type_taverns.grid_slot(0))')

# objects: the type taverns
edit('tools/objects.py',
     "    tav.set('useu', T_STRING, ','.join(pd.STARTERS))" + NL + "    f.custom.append(tav)" + NL,
     "    tav.set('useu', T_STRING, ','.join(pd.STARTERS))" + NL + "    f.custom.append(tav)" + NL +
     "    import type_taverns" + NL +
     "    for i, (typ, ids) in enumerate(type_taverns.groups(), 1):  # v3.3: one tavern per type" + NL +
     "        tt = _clone(f.find(pd.TAVERN_TEMPLATE), type_taverns.tavern_id(i))" + NL +
     "        tt.set('unam', T_STRING, type_taverns.tavern_name(typ))" + NL +
     "        tt.set('useu', T_STRING, ','.join(ids))" + NL +
     "        tt.set('uico', T_STRING, 'ReplaceableTextures\\\\CommandButtons\\\\%s.blp' % type_taverns.TYPE_ICON[typ])" + NL +
     "        f.custom.append(tt)" + NL +
     "        for k, fid in enumerate(ids):" + NL +
     "            o = f.find(fid)" + NL +
     "            o.set('ubpx', T_INT, k % 4)" + NL +
     "            o.set('ubpy', T_INT, k // 4)" + NL +
     "            o.set('uhot', T_STRING, type_taverns.SELL_HOTKEYS[k])" + NL)

# inject: create the type taverns at their grid slots
edit('tools/inject.py',
     "                  % (poke_data.TAVERN_ID, x, y, face)," + NL,
     "                  % (poke_data.TAVERN_ID, x, y, face)," + NL +
     "                  ] + [\"    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), '%s', %.1f, %.1f, %.1f)\"" + NL +
     "                       % ((type_taverns.tavern_id(i),) + type_taverns.grid_slot(i))" + NL +
     "                       for i in range(1, len(type_taverns.groups()) + 1)]" + NL +
     "        lines += [" + NL)
edit('tools/inject.py',
     "    import poke_data" + NL + "    from mega_data import SHOP3_ID" + NL,
     "    import poke_data" + NL + "    import type_taverns" + NL + "    from mega_data import SHOP3_ID" + NL)

# the picker no longer opens when the tavern is selected (the type taverns are the way to choose now)
edit('tools/jass/mega.j',
     "        call TriggerRegisterPlayerUnitEvent(pk_sel, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)" + NL, "", 'latin-1')
edit('tools/jass/mega.j', "    call TriggerAddAction(pk_sel, function Pick_OnSelect)" + NL, "", 'latin-1')

# random pool: every type tavern Pokemon too
edit('tools/build_v2.py',
     "    rand = inject.random_pool(w3u, poke_data.STARTERS if poke is not None else ())",
     "    import type_taverns" + NL +
     "    rand = inject.random_pool(w3u, (list(poke_data.STARTERS) + [fid for _t, ids in type_taverns.groups() for fid in ids])" + NL +
     "                              if poke is not None else ())")

# tests
tav = 'x, y, face = poke_data.TAVERN_POS'
edit('tests/test_poke_data.py', "('nTV5', 'n01H', (448.0, 4512.0, 270.0))", "('nTV5', 'n01H', (-1250.0, 4800.0, 270.0))")
edit('tests/test_evo.py', "\"'nTV5', 448.0, 4512.0, 270.0\"", "\"'nTV5', -1250.0, 4800.0, 270.0\"")
edit('tests/test_build.py', "\"'nTV5', 448.0, 4512.0, 270.0\" in j", "\"'nTV5', -1250.0, 4800.0, 270.0\" in j")
print('ok')
