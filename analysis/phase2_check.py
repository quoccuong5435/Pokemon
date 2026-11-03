"""Phase 2 checks: PKL models for the 8 new lines + calibration numbers of Arena skills (read-only)."""
import sys

sys.path.insert(0, sys.argv[1])
import assets  # noqa: E402
import mdx  # noqa: E402
import mpq  # noqa: E402
import slk  # noqa: E402

FORMS = ['Torchic', 'Combusken', 'Blaziken', 'Treecko', 'Grovyle', 'Sceptile', 'Larvitar', 'Pupitar', 'Tyranitar',
         'Ralts', 'Kirlia', 'Gardevoir', 'Gallade', 'Bagon', 'Shelgon', 'Salamence', 'Beldum', 'Metang',
         'Metagross', 'Lucario', 'Absol']
MEGA_STEMS = ['MegaLohgock', 'MegaGewaldro', 'MegaDespotar', 'GardevoirMega', 'MegaGallade', 'MegaBrutalanda',
              'MegaMetagross', 'MegaLucario', 'MegaAbsol']
pkl = mpq.MPQ(sys.argv[2])
idx = assets.pkl_species_index(pkl)
total = 0
for f in FORMS:
    if f.lower() not in idx:
        print('MISSING', f)
        continue
    mdl, ico = idx[f.lower()]
    d = pkl.read(mdl[:-4] + '.mdx')
    info = mdx.inspect(d)
    size = len(d) + sum(len(pkl.read(t)) for _, t in info['textures'] if t and pkl.has(t))
    total += size
    print('%-10s %-38s %8d seq=%s' % (f, mdl, size, ','.join(info['sequences'])[:70]))
for stem in MEGA_STEMS:
    for n in ('war3mapImported\\' + stem + '.mdx', stem + '.mdx'):
        if pkl.has(n):
            d = pkl.read(n)
            info = mdx.inspect(d)
            size = len(d) + sum(len(pkl.read(t)) for _, t in info['textures'] if t and pkl.has(t))
            total += size
            print('MEGA %-14s %8d' % (stem, size))
            break
    else:
        print('MEGA MISSING', stem)
print('total bytes', total)
s = slk.Slk(open(sys.argv[3] + '/Units/AbilityData.slk', encoding='latin-1').read())
for a in ('A013', 'A01Z', 'A00C', 'A06B', 'A026', 'A0B5', 'A05F', 'A014'):
    r = s.find(a)
    if r is None:
        continue
    cols = ['code', 'reqLevel', 'Cool1', 'Cool3', 'Cost1', 'Cost3', 'Rng1', 'Area1', 'Dur1', 'HeroDur1',
            'DataA1', 'DataA3', 'DataB1', 'DataB3', 'DataC1', 'DataD1']
    print(a, {c: s.get(r, c) for c in cols if s.get(r, c) not in (None, '')})
