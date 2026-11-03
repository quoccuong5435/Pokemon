import sys
sys.path.insert(0, sys.argv[1])
import objdata
f = objdata.ObjFile(open(sys.argv[2],'rb').read())
for o in f.custom:
    g = o.get
    print('%s<%s> %-14s mdl=%-26s %-22s hp=%s mp=%s dmg=%s def=%s str/agi/int=%s/%s/%s prim=%s hab=%s abi=%s scale=%s' % (
        o.new, o.orig, g('upro') or g('unam'), g('umdl'), g('unam'), g('uhpm'), g('umpm'), g('ua1b'), g('udef'),
        g('ustr'), g('uagi'), g('uint'), g('upra'), g('uhab'), g('uabi'), g('usca')))
