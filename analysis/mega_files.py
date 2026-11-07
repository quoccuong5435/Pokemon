"""Read-only: do the Mega skin models of a map (and their textures) really exist in the MPQ?

python -I analysis/mega_files.py tools "../Pokemon Arena v3.3.3.w3x"
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402
import mdx  # noqa: E402

GAME = ('textures\\', 'units\\', 'replaceabletextures\\teamcolor', 'replaceabletextures\\teamglow', 'abilities\\',
        'replaceabletextures\\cliff', 'sharedmodels\\')
a = mpq.MPQ(sys.argv[2])
units = {o.id: o for o in objdata.ObjFile(a.read('war3map.w3u')).all()}
for sid in sorted(u for u in units if u.startswith('hM')):
    o = units[sid]
    mdl = o.get('umdl') or ''
    stem = re.sub(r'\.md[lx]$', '', mdl, flags=re.I)
    if not a.has(stem + '.mdx'):
        print(sid, o.get('unam'), mdl, 'NOT IN MAP (built-in or missing)')
        continue
    data = a.read(stem + '.mdx')
    miss = [t for _, t in mdx.inspect(data)['textures'] if t and not a.has(t) and not t.lower().startswith(GAME)]
    print(sid, o.get('unam'), mdl, len(data), 'bytes', 'missing textures: %s' % miss if miss else 'textures ok')
