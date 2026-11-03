"""Pick template heroes and non-scripted source abilities for phase 2 (read-only)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import objdata  # noqa: E402
import slk  # noqa: E402

base = sys.argv[2]
w3u = objdata.ObjFile(open(base + '/war3map.w3u', 'rb').read())
s = slk.Slk(open(base + '/Units/AbilityData.slk', encoding='latin-1').read())
script = open(base + '/scripts/war3map.j', encoding='latin-1').read()
sections = {}
cur = None
for line in open(base + '/Units/CampaignAbilityStrings.txt', encoding='utf-8', errors='replace'):
    line = line.rstrip('\n')
    if line.startswith('[') and line.endswith(']'):
        cur = line[1:-1]
        sections[cur] = {}
    elif cur and '=' in line:
        k, v = line.split('=', 1)
        sections[cur][k] = v

print('== templates')
for t in ('E003', 'E007', 'E01C', 'E008', 'E001', 'E002', 'E00N', 'E00O', 'E00P', 'E00G', 'E00H', 'E00I', 'E010',
          'E01S', 'E01T', 'E01K', 'E031', 'E032', 'E03V', 'E01Z', 'E03I', 'E00E'):
    o = w3u.find(t)
    g = o.get
    print(t, g('upro'), 'umvt=', g('umvt'), 'ua1t=', g('ua1t'), 'udty=', g('udty'), 'ua1w=', g('ua1w'),
          'ua1r=', g('ua1r'), 'abi=', g('uabi'), 'pra=', g('upra'), 'uhot=', g('uhot'))

print('== source abilities (engine codes, not referenced by script)')
want = ('AUcs', 'AOsh', 'AHtb', 'AOws', 'AHtc', 'AOcl', 'Absk', 'AOcr', 'AEev', 'AHbh', 'AHbz', 'ANbf', 'AEsh',
        'AUfn', 'AEsf', 'ANst')
for code in want:
    rows = [r for r in s.rows if s.get(r, 'code') == code]
    free = [r for r in rows if "'%s'" % s.get(r, 'alias') not in script]
    print(code, 'rows', len(rows), 'unscripted', [s.get(r, 'alias') for r in free][:8])
    for r in free[:1]:
        a = s.get(r, 'alias')
        vals = {c: s.get(r, c) for c in s.cols.values() if c.endswith('1') and s.get(r, c) not in (None, '', '0', '-')}
        print('   ', a, s.get(r, 'levels'), s.get(r, 'reqLevel'), vals)
        print('   strings', {k: v[:60] for k, v in sections.get(a, {}).items()})
