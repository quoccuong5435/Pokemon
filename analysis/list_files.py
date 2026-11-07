"""Read-only: object data / Mega / Wild / Poke model files listed in a map.  python -I analysis/list_files.py tools <map>"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
names = [ln.strip() for ln in a.read('(listfile)').decode('latin-1').splitlines()] if a.has('(listfile)') else []
low = [n.lower() for n in names]
print('listed files:', len(names))
print('object data:', [n for n in names if n.lower().startswith('units') or n.lower().endswith(('.w3t', '.w3a', '.w3u', '.w3q', '.imp'))])
for key in ('\\wild\\', '\\poke\\', '\\mega\\'):
    sel = [n for n, lo in zip(names, low) if key in lo and lo.endswith('.mdx')]
    print(key, len(sel), sel[:6])
print('mega files:', [n for n in names if 'mega' in n.lower()][:80])
