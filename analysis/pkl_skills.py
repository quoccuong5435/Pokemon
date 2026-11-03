"""Inspect how PKLegends implements Pokemon skills (read-only)."""
import collections
import re
import sys

sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402
import objdata  # noqa: E402

pkl = mpq.MPQ(sys.argv[2])
wts = {}
t = pkl.read('war3map.wts').decode('utf-8', 'replace')
for m in re.finditer(r'STRING (\d+)[^{]*\{\r?\n(.*?)\r?\n\}', t, re.S):
    wts[int(m.group(1))] = m.group(2)


def res(v):
    if isinstance(v, str) and v.startswith('TRIGSTR_'):
        return wts.get(int(v[8:].split()[0] or 0), v)
    return v


w3a = objdata.ObjFile(pkl.read('war3map.w3a'), leveled=True)
print('w3a version', w3a.version, 'custom abilities', len(w3a.custom))
bases = collections.Counter(o.orig for o in w3a.custom)
print('most used base abilities:', bases.most_common(15))
j = pkl.read('war3map.j').decode('latin-1')
print('script size', len(j), 'functions', j.count('\nfunction '))
ids = [o.new for o in w3a.custom]
in_script = sum(1 for i in ids if "'%s'" % i in j)
print('custom abilities referenced by script:', in_script, '/', len(ids))
names = []
for o in w3a.custom[:400]:
    n = res(o.get('anam'))
    if n:
        names.append(str(n))
print('sample names:', ', '.join(names[:60]))
