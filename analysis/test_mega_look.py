"""Check tools/v34/mega_look.py with a stand-in model (a copy of Mega Gengar from the map as 'MegaMewtwoX').

python -I analysis/test_mega_look.py   (writes nothing outside a temp folder)
"""
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import mpq  # noqa: E402
import objdata  # noqa: E402
import mdx  # noqa: E402
import mega_look  # noqa: E402
import apply as A  # noqa: E402

base = mpq.MPQ(A.BASE_MAP)
units = A.unit_data(A.BASE_MAP)
script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
with tempfile.TemporaryDirectory() as tmp:
    data = base.read('war3mapImported\\Mega\\MegaGengar.mdx')
    open(os.path.join(tmp, 'MegaMewtwoX.mdx'), 'wb').write(data)
    sub = os.path.join(tmp, 'tex')
    os.makedirs(sub)
    for _, t in mdx.inspect(data)['textures']:
        if t and base.has(t):
            open(os.path.join(sub, t.replace('/', '\\').split('\\')[-1]), 'wb').write(base.read(t))
    report = []
    out = mega_look.patch_script(script, base, units, report, models_dir=tmp)
    print('\n'.join(report))
    for f in ('Mega_Scale', 'Mega_Fx', 'Mega_R', 'Mega_G', 'Mega_B'):
        print(re.search(r'    set %s\[13\] = [^\n]*' % f, out).group(0).strip())
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    files, warns = mega_look.map_files(w3u, models_dir=tmp)
    print('files:', sorted(files), 'warnings:', warns)
    print('hM0D umdl ->', w3u.find('hM0D').get('umdl'), '| hM04 umdl ->', w3u.find('hM04').get('umdl'))
    back = objdata.ObjFile(w3u.to_bytes())
    assert back.find('hM0D').get('umdl') == 'war3mapImported\\Mega\\MegaMewtwoX.mdl'
    patched = files['war3mapImported\\Mega\\MegaMewtwoX.mdx']
    print('textures in patched model:', [t for _, t in mdx.inspect(patched)['textures']])
    print('OK')
