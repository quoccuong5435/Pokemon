"""Read-only: compare two built maps (file list, sizes, script markers, object data counts).

python -I analysis/inspect_map.py "../Pokemon Arena v3.4.10.w3x" "../Pokemon Arena v3.4.5.w3x"
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402


def block_sizes(m):
    """name -> (compressed, full) for every file named in the listfile."""
    out = {}
    names = m.listfile() or []
    for n in names:
        hi = m.find_hash(n)
        if hi is None:
            continue
        bi = m.hash_table[hi][4]
        if bi >= len(m.block_table):
            continue
        b = m.block_table[bi]
        out[n] = (b[1], b[2])
    return out


def script_of(m):
    for n in ('war3map.j', 'scripts\\war3map.j', 'Scripts\\war3map.j'):
        if m.has(n):
            return m.read(n).decode('latin-1')
    return ''


a_path, b_path = sys.argv[1], sys.argv[2]
A, B = mpq.MPQ(a_path), mpq.MPQ(b_path)
sa, sb = block_sizes(A), block_sizes(B)
print('A', os.path.basename(a_path), 'files', len(sa), 'size', os.path.getsize(a_path))
print('B', os.path.basename(b_path), 'files', len(sb), 'size', os.path.getsize(b_path))
only_a = sorted(set(sa) - set(sb))
only_b = sorted(set(sb) - set(sa))
print('\n== only in A: %d files, %.1f MB compressed' % (len(only_a), sum(sa[n][0] for n in only_a) / 1e6))
dirs = {}
for n in only_a:
    d = '\\'.join(n.split('\\')[:-1]) or '.'
    dirs.setdefault(d, [0, 0])
    dirs[d][0] += 1
    dirs[d][1] += sa[n][0]
for d, (c, s) in sorted(dirs.items(), key=lambda x: -x[1][1])[:60]:
    print('  %-70s %4d files %7.2f MB' % (d, c, s / 1e6))
print('\n== only in B: %d' % len(only_b))
for n in only_b[:40]:
    print('  ', n)
print('\n== changed files (same name, different size)')
for n in sorted(set(sa) & set(sb)):
    if sa[n] != sb[n] and not n.lower().endswith(('.blp', '.mdx', '.dds', '.mdl')):
        print('  %-50s A %9d  B %9d' % (n, sa[n][1], sb[n][1]))
ja, jb = script_of(A), script_of(B)
print('\nscript A %d chars, B %d chars' % (len(ja), len(jb)))
for tag in sorted(set(re.findall(r'v3\.4\.\d+[A-Za-z0-9 ]{0,4}', ja)))[:80]:
    print('  marker', tag)
fa = set(re.findall(r'(?m)^function (\w+)', ja))
fb = set(re.findall(r'(?m)^function (\w+)', jb))
print('\nfunctions only in A (%d):' % len(fa - fb), ' '.join(sorted(fa - fb))[:4000])
print('\nfunctions only in B (%d):' % len(fb - fa), ' '.join(sorted(fb - fa))[:2000])
