"""Read-only: unified diff of chosen functions between two dumped scripts (out/<tag>/scripts_war3map.j),
or print whole functions of one script.

python -I analysis/func_diff.py out/v3400/scripts_war3map.j out/v3410/scripts_war3map.j Ab_OnDamaging Ty_Mult
python -I analysis/func_diff.py - out/v3410/scripts_war3map.j Dmg_InitTypes   (just print)
"""
import difflib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')


def funcs(path):
    j = open(path, encoding='latin-1').read().replace('\r\n', '\n').replace('\r', '\n')
    return {m.group(1): m.group(0) for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction', j)}


a = funcs(sys.argv[1]) if sys.argv[1] != '-' else {}
b = funcs(sys.argv[2])
for name in sys.argv[3:]:
    if sys.argv[1] == '-':
        print(b.get(name, '// %s missing' % name))
        continue
    da, db = a.get(name, '').splitlines(), b.get(name, '').splitlines()
    print('\n'.join(difflib.unified_diff(da, db, 'old ' + name, 'new ' + name, n=1, lineterm='')))
