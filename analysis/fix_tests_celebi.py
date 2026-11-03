"""One-off: tests for the Celebi hero and Soul."""
import io

NL = chr(10)


def edit(p, old, new):
    s = io.open(p, encoding='utf-8', newline='').read()
    assert s.count(old) == 1, (p, old[:50], s.count(old))
    io.open(p, 'w', encoding='utf-8', newline='').write(s.replace(old, new))


edit('tests/test_legends.py',
     '    for l in ld.LEGENDS:' + NL + "        assert '[%s]" + chr(92) + "nName=%s Soul'",
     "    for l in [x for x in ld.LEGENDS if x.soul[:2] != 'IS']:  # v3.3: the Celebi Soul (ISCE) is added by us" + NL +
     "        assert '[%s]" + chr(92) + "nName=%s Soul'")
edit('tests/test_objects.py',
     "+ len(__import__('type_taverns').groups())  # skins",
     "+ len(__import__('type_taverns').groups()) + 1  # Celebi hero; skins")
print('ok')
