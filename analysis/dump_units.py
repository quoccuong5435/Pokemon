import sys, os
sys.path.insert(0, sys.argv[1])
import objdata
d = open(sys.argv[2],'rb').read()
f = objdata.ObjFile(d, leveled=sys.argv[3]=='1')
print('version', f.version, 'orig', len(f.original), 'custom', len(f.custom))
for o in f.all():
    print('==', o.orig, o.new, ' '.join(repr(m) for m in o.mods))
