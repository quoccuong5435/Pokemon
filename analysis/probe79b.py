import sys, os, re
sys.path.insert(0, sys.argv[1])
import mpq
a = mpq.MPQ(sys.argv[2])
for core in ['war3map.j','Units/UnitUI.slk','Units/UnitData.slk','war3map.w3a','war3map.w3t','war3map.w3i']:
    try:
        d = a.read(core)
    except Exception as e:
        print(core, 'ERR', e); continue
    print(core, len(d))
    for m in re.finditer(rb'.{0,80}003mega.{0,40}', d, re.I):
        print('   ', m.group(0))
