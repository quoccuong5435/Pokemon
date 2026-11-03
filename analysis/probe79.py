import sys, os
sys.path.insert(0, sys.argv[1])
import mpq
a = mpq.MPQ(sys.argv[2])
print('base', hex(a.base), 'sector', a.sector_size, 'ht', a.ht_count, 'bt', a.bt_count, 'arc', a.arc_size, 'filesize', len(a.raw))
used = sum(1 for e in a.hash_table if e[4] < len(a.block_table))
print('used hash', used)
for n in ['war3map.w3u','war3map.j','scripts/war3map.j','war3map.lua','war3map.w3i','war3mapSkin.w3u','war3map.imp']:
    print(n, a.has(n))
for stem in ['003mega','006mega-x','006mega-Y','150mega-x','384mega','115mega','212mega']:
    for pre in ['war3mapImported/','','war3mapimported/','Units/','models/']:
        for ext in ['.mdx','.mdl','.MDX']:
            if a.has(pre+stem+ext): print('FOUND', pre+stem+ext)
