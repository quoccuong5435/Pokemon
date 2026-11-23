"""Read-only: compare two dumped scripts function by function (line breaks normalised: v1.8 uses bare CR).

python -I analysis/script_cmp.py out/v3216/scripts_war3map.j out/v342/scripts_war3map.j [prefix-report]
Prints: functions only in A / only in B (grouped by name prefix), changed functions with +/- line counts,
globals only in A / only in B.
"""
import collections
import difflib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')


def load(path):
    return open(path, encoding='latin-1').read().replace('\r\n', '\n').replace('\r', '\n')


def funcs(j):
    return {m.group(1): m.group(0) for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction', j)}


def globals_of(j):
    m = re.search(r'(?ms)^globals\n(.*?)^endglobals', j)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.strip()
        g = re.match(r'(?:constant\s+)?(\w+)(?:\s+array)?\s+(\w+)', line)
        if g and not line.startswith('//'):
            out[g.group(2)] = line
    return out


def prefix(name):
    if '_' in name:
        return name.split('_')[0] + '_'
    return '(short v1.8 name)' if len(name) <= 4 else '(other)'


A, B = load(sys.argv[1]), load(sys.argv[2])
fa, fb = funcs(A), funcs(B)
print('A: %d lines, %d functions | B: %d lines, %d functions' % (A.count('\n'), len(fa), B.count('\n'), len(fb)))


def group(names):
    g = collections.defaultdict(list)
    for n in sorted(names):
        g[prefix(n)].append(n)
    return g


for title, names in (('ONLY IN A (removed in B)', set(fa) - set(fb)), ('ONLY IN B (new in B)', set(fb) - set(fa))):
    print('\n== %s: %d' % (title, len(names)))
    for p, ns in sorted(group(names).items(), key=lambda x: -len(x[1])):
        print('  %-20s %4d  %s' % (p, len(ns), ' '.join(ns)[:600]))

print('\n== CHANGED (same name): ')
changed = []
for n in sorted(set(fa) & set(fb)):
    if fa[n] != fb[n]:
        d = list(difflib.unified_diff(fa[n].splitlines(), fb[n].splitlines(), n=0, lineterm=''))
        plus = sum(1 for x in d if x.startswith('+') and not x.startswith('+++'))
        minus = sum(1 for x in d if x.startswith('-') and not x.startswith('---'))
        changed.append((n, minus, plus))
print('  %d changed functions' % len(changed))
for p, ns in sorted(group([c[0] for c in changed]).items(), key=lambda x: -len(x[1])):
    info = {c[0]: c for c in changed}
    print('  %-20s %4d  %s' % (p, len(ns), ' '.join('%s(-%d/+%d)' % (n, info[n][1], info[n][2]) for n in ns)[:900]))

ga, gb = globals_of(A), globals_of(B)
print('\n== globals: A %d, B %d; only A %d, only B %d' % (len(ga), len(gb), len(set(ga) - set(gb)), len(set(gb) - set(ga))))
for title, names in (('globals only in A', set(ga) - set(gb)), ('globals only in B', set(gb) - set(ga))):
    print('  %s:' % title)
    for p, ns in sorted(group(names).items(), key=lambda x: -len(x[1])):
        print('    %-18s %4d  %s' % (p, len(ns), ' '.join(ns)[:500]))
