"""Read-only: which built map is the closest ancestor of a map (function bodies in common), and its new files.

python -I analysis/fork_point.py "../Pokemon Arena v3.4.10.w3x" "../Pokemon Arena v3.4.0.w3x" "../Pokemon Arena v3.4.1.w3x" ...
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402


def funcs(path):
    m = mpq.MPQ(path)
    j = m.read('scripts\\war3map.j' if m.has('scripts\\war3map.j') else 'war3map.j').decode('latin-1')
    j = j.replace('\r\n', '\n').replace('\r', '\n')
    out = {}
    for mt in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction', j):
        out[mt.group(1)] = re.sub(r'//[^\n]*', '', mt.group(0)).strip()
    names = set(l.strip() for l in m.read('(listfile)').decode('latin-1').replace(';', '\n').splitlines() if l.strip())
    return out, names


tgt, tnames = funcs(sys.argv[1])
print('target', os.path.basename(sys.argv[1]), len(tgt), 'functions')
for p in sys.argv[2:]:
    f, names = funcs(p)
    same = sum(1 for k in tgt if f.get(k) == tgt[k])
    only_t = [k for k in tgt if k not in f]
    only_f = [k for k in f if k not in tgt]
    diff = [k for k in tgt if k in f and f[k] != tgt[k]]
    print('\n%-32s identical %5d  changed %4d  only target %4d  only this %3d' % (
        os.path.basename(p), same, len(diff), len(only_t), len(only_f)))
    print('   only in this map:', ' '.join(sorted(only_f))[:600])
    v34 = [k for k in diff if re.match(r'(Gym|League|Ext|Itm|Mv|Ai|Wild|Mega|Ab|Ty|Wth|Shiny|Leg|Hero)_', k)]
    print('   changed v3.4 functions (%d):' % len(v34), ' '.join(sorted(v34))[:1500])
    new = sorted(tnames - names)
    root = [n for n in new if '\\' not in n]
    print('   new files in target: %d (root %d, e.g. %s)' % (len(new), len(root), root[:12]))
