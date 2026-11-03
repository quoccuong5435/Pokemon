import os
import re
import sys

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
d = a.read('Units\\UnitUI.slk')
paths = set(m.group(1).decode('latin-1') for m in re.finditer(rb'K"([^"]+\.md[lx])"', d, re.I))
imp = [p for p in paths if p.lower().startswith('war3mapimported')]
print('model refs', len(paths), 'imported', len(imp))
found = 0
missing = []
for p in sorted(imp):
    stem = p[:-4]
    ok = a.has(stem + '.mdx') or a.has(stem + '.mdl')
    found += ok
    if not ok:
        missing.append(p)
print('found', found, 'missing', len(missing))
print('mega missing:', [m for m in missing if 'mega' in m.lower()])
print('mega found:', [p for p in imp if 'mega' in p.lower() and p not in missing])
print('sample found:', [p for p in imp if p not in missing][:10])
