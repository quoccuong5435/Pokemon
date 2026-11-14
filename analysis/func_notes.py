"""Read-only: the comment lines just above each named function (or every function matching a prefix) of a script.

python -I analysis/func_notes.py out/v3410/scripts_war3map.j PkFx_ Mv_ TyUI_ HomeGate_ Mob_ Gym_Down
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
lines = open(sys.argv[1], encoding='latin-1').read().replace('\r\n', '\n').replace('\r', '\n').split('\n')
prefixes = sys.argv[2:]
for i, l in enumerate(lines):
    m = re.match(r'function (\w+)', l)
    if not m or not any(m.group(1).startswith(p) for p in prefixes):
        continue
    j = i - 1
    notes = []
    while j >= 0 and lines[j].lstrip().startswith('//'):
        notes.insert(0, lines[j].strip())
        j -= 1
    inner = [x.strip() for x in lines[i + 1:i + 40] if x.strip().startswith('//')][:3]
    print('%s  %s' % (m.group(1), ' '.join(notes)[:500]))
    if inner:
        print('      inner: ' + ' | '.join(inner)[:400])
