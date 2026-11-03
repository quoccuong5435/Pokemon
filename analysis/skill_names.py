"""Dump every playable hero of the built map with its type, skills (ids and names) to JSON-ish text."""
import re
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402
import objdata  # noqa: E402

a = mpq.MPQ(sys.argv[1])
w3u = objdata.ObjFile(a.read('war3map.w3u'))
heroes = [o for o in w3u.custom if o.new[:1].isupper() and o.get('uhab')]
txt = {}
for n in a.listfile():
    if n.startswith('Units\\') and n.endswith(('Func.txt', 'Strings.txt')):
        t = a.read(n).decode('utf-8', 'replace').replace('\r\n', '\n')
        cur = None
        for line in t.split('\n'):
            m = re.match(r'\[(\w{4})\]', line)
            if m:
                cur = m.group(1)
                txt.setdefault(cur, {})
            elif cur and '=' in line:
                k, v = line.split('=', 1)
                txt[cur].setdefault(k, v)
print('heroes', len(heroes), 'txt sections', len(txt))
missing = set()
for o in heroes:
    skills = [s for s in o.get('uhab').split(',') if s]
    out = []
    for s in skills:
        d = txt.get(s)
        if not d:
            missing.add(s)
            out.append('%s=?' % s)
        else:
            out.append('%s=%s' % (s, (d.get('Name') or d.get('Tip') or '?').split(',')[0][:30]))
    print(o.new, o.get('upro'), '|', o.get('unam'), '|', ' ; '.join(out))
print('missing', sorted(missing))
