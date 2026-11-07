"""Read-only: built-in (not imported) button icons the v3.3.3 map already references -> analysis/builtin_icons.txt.
These are known to exist in the game, so new items / move icons pick from them.  python -I analysis/builtin_icons.py"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

a = mpq.MPQ(os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.3.3.w3x'))
arts = set()
for fn in a.listfile():
    if fn.lower().endswith('.txt') and fn.lower().startswith('units\\'):
        t = a.read(fn).decode('utf-8', 'replace')
        arts.update(x.strip() for x in re.findall(r'(?im)^(?:Art|Researchart|Unart)=([^\r\n,]+)', t))
built = sorted(x for x in arts if x.lower().startswith('replaceabletextures\\commandbuttons\\') and not a.has(x))
open(os.path.join(WORK, 'analysis', 'builtin_icons.txt'), 'w', encoding='utf-8').write('\n'.join(built) + '\n')
print(len(arts), 'art paths,', len(built), 'built-in button icons')
print(' '.join(b.split('\\')[-1][3:-4] for b in built))
