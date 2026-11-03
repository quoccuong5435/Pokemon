"""One-off: tests for the boss Soul patch and the legend damage/armor x2.5."""
import io

NL = chr(10)


def edit(path, old, new):
    s = io.open(path, encoding='utf-8', newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:60], s.count(old))
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))


edit('tests/test_inject.py',
     "    expected = expected.replace(inject.REVIVE_MSG_OLD, inject.REVIVE_MSG_NEW)" + NL +
     "    assert re.sub",
     "    expected = expected.replace(inject.REVIVE_MSG_OLD, inject.REVIVE_MSG_NEW)" + NL +
     "    expected = inject.patch_boss_souls(expected)  # v3.3: boss Soul chance 30% -> 100%" + NL +
     "    assert re.sub")

# legend damage x2.0 (0.8 x 2.5) and armor x2.5 on top of the old cap 35
edit('tools/objects.py', "        o.set('ua1b', T_INT, int(round(o.get('ua1b') * 0.8)))" + NL +
     "        o.set('udef', T_INT, min(o.get('udef') or 0, 35))",
     "        o.set('ua1b', T_INT, int(round(o.get('ua1b') * LEGEND_DMG_MULT)))" + NL +
     "        o.set('udef', T_INT, int(round(min(o.get('udef') or 0, 35) * LEGEND_ARMOR_MULT)))")
edit('tools/objects.py', 'LEGEND_HP_MULT = 1.25  # legend HP: x0.5 (v3.2) times 2.5',
     'LEGEND_HP_MULT = 1.25  # legend HP: x0.5 (v3.2) times 2.5' + NL +
     'LEGEND_DMG_MULT = 2.0   # legend damage: x0.8 (v3.2) times 2.5' + NL +
     'LEGEND_ARMOR_MULT = 2.5  # legend armor: min(armor, 35) (v3.2) times 2.5')
edit('tools/objects.py',
     '    """Legend bosses (v3.3 balance): level 100, HP x1.25 (v3.2 was x0.5; x2.5 on top), damage x0.8, armor at most 35."""',
     '    """Legend bosses (v3.3 balance): level 100, HP x1.25, damage x2.0, armor min(armor, 35) x2.5 (all x2.5 over v3.2)."""')
edit('tests/test_objects.py',
     "        assert o.get('ua1b') == int(round(b.get('ua1b') * 0.8))" + NL +
     "        assert o.get('udef') == min(b.get('udef') or 0, 35)",
     "        assert o.get('ua1b') == int(round(b.get('ua1b') * objects.LEGEND_DMG_MULT))  # v3.3: x2.0" + NL +
     "        assert o.get('udef') == int(round(min(b.get('udef') or 0, 35) * objects.LEGEND_ARMOR_MULT))  # v3.3: x2.5")
print('ok')
