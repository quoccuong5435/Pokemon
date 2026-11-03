"""Look for an embedded common.j / Blizzard.j in the .w3x maps next to the work folder (needed to run pjass)."""
import glob
import os
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402

NAMES = ['scripts\\common.j', 'scripts\\Blizzard.j', 'scripts\\blizzard.j', 'Scripts\\common.j', 'Scripts\\Blizzard.j',
         'common.j', 'Blizzard.j', 'blizzard.j', 'war3map.j', 'scripts\\war3map.j']
for path in sorted(glob.glob(os.path.join(sys.argv[1], '*.w3x')) + glob.glob(os.path.join(sys.argv[1], '*.w3m'))):
    try:
        a = mpq.MPQ(path)
    except Exception as e:  # noqa: BLE001
        print('skip', os.path.basename(path), type(e).__name__)
        continue
    hits = [n for n in NAMES[:8] if a.has(n)]
    if hits:
        print(os.path.basename(path), hits)
print('done')
