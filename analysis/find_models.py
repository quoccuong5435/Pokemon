"""Read-only: search the (listfile) of local maps for model files whose name matches keywords.

python -I analysis/find_models.py tools <folder> [<folder> ...] -- mewtwo rayquaza beedrill kangaskhan
"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[1])
import mpq  # noqa: E402

args = sys.argv[2:]
cut = args.index('--')
folders, kws = args[:cut], [k.lower() for k in args[cut + 1:]]
for folder in folders:
    for path in sorted(glob.glob(os.path.join(folder, '*.w3x'))):
        try:
            a = mpq.MPQ(path)
            if not a.has('(listfile)'):
                print('%s: no listfile' % os.path.basename(path))
                continue
            names = a.read('(listfile)').decode('latin-1', 'replace').splitlines()
        except Exception as e:  # noqa: BLE001
            print('%s: cannot read (%s)' % (os.path.basename(path), e))
            continue
        hits = [n.strip() for n in names if n.lower().endswith(('.mdx', '.mdl')) and any(k in n.lower() for k in kws)]
        if hits:
            print('%s: %s' % (os.path.basename(path), hits[:12]))
