import sys

sys.path.insert(0, sys.argv[1])
import mdx  # noqa: E402
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
models = ['MegaBisaflor', 'MegaGlurakX', 'MegaGlurakY', 'MegaTurtok', 'MegaTauboss', 'MegaSimsala', 'MegaGengar',
          'Kangaskhan', 'KidKangama', 'MegaPinsir', 'MegaGarados', 'MegaSteelix', 'MegaScherox']
icons = ['BTNMegaBisaflor', 'BTNMegaGlurakX', 'BTNMegaGlurakY', 'BTNMegaTurtok', 'BTNTauboss', 'BTNMegaSimsala',
         'BTNMegaGengar', 'BTNMega-Kangama', 'BTNMegaPinsir', 'BTNMegaGarados', 'BTNMSteelix', 'BTNMegaScherox']
total = 0
for m in models:
    for suffix in ('', '_portrait', '_Portrait'):
        name = 'war3mapImported\\' + m + suffix + '.mdx'
        if not a.has(name):
            if suffix == '':
                print('MISSING', name)
            continue
        d = a.read(name)
        i = mdx.inspect(d)
        total += len(d)
        print('%-45s v%s %7d bytes seqs=%s' % (name, i['version'], len(d), ','.join(i['sequences'])[:150]))
        for rid, tp in i['textures']:
            if tp:
                ok = a.has(tp)
                if ok:
                    total += len(a.read(tp))
                print('      tex %-55s %s' % (tp, 'OK' if ok else ('(game asset?)' if tp.lower().startswith(('textures', 'units', 'abilities')) else 'MISSING')))
            else:
                print('      tex replaceable id', rid)
for ic in icons:
    for pre in ('ReplaceableTextures\\CommandButtons\\', 'ReplaceableTextures\\CommandButtonsDisabled\\DIS'):
        n = pre + ic + '.blp'
        print('icon', n, a.has(n))
print('total bytes', total)
