"""How are Arena hero skills built? levels, base codes, trigger use (read-only)."""
import collections
import re
import sys

sys.path.insert(0, sys.argv[1])
import objdata  # noqa: E402
import slk  # noqa: E402

w3u = objdata.ObjFile(open(sys.argv[2] + '/war3map.w3u', 'rb').read())
s = slk.Slk(open(sys.argv[2] + '/Units/AbilityData.slk', encoding='latin-1').read())
script = open(sys.argv[2] + '/scripts/war3map.j', encoding='latin-1').read()
names = {}
cur = None
for line in open(sys.argv[2] + '/Units/CampaignAbilityStrings.txt', encoding='utf-8', errors='replace'):
    line = line.strip()
    if line.startswith('[') and line.endswith(']'):
        cur = line[1:-1]
    elif line.startswith('Name=') and cur:
        names[cur] = line[5:]
hab = collections.Counter()
for o in w3u.custom:
    for a in (o.get('uhab') or '').split(','):
        if a:
            hab[a] += 1
codes = collections.Counter()
scripted = 0
levels = collections.Counter()
for a in sorted(hab):
    r = s.find(a)
    code = s.get(r, 'code') if r else None
    lv = s.get(r, 'levels') if r else None
    req = s.get(r, 'reqLevel') if r else None
    skip = s.get(r, 'levelSkip') if r else None
    in_script = len(re.findall("'%s'" % a, script))
    scripted += in_script > 0
    codes[code] += 1
    levels[(lv, req, skip)] += 1
print('distinct hero abilities', len(hab), 'scripted', scripted)
print('levels/req/skip', levels.most_common(8))
print('codes', codes.most_common(25))
for a in ('A05F', 'A037', 'A00C', 'A014', 'A013', 'A0B5', 'A06B', 'A026'):
    r = s.find(a)
    print(a, names.get(a), s.get(r, 'code'), 'lv', s.get(r, 'levels'), 'req', s.get(r, 'reqLevel'),
          'skip', s.get(r, 'levelSkip'), 'scriptrefs', len(re.findall("'%s'" % a, script)))
