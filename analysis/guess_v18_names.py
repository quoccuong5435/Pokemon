"""Read-only: try to recover the names of the 8 unnamed v1.8 files of the v3.4.10 map from their hash entries
(name hash A / B) with candidate names from every listfile and model list we have.

    python -I -X utf8 analysis/guess_v18_names.py
"""
import glob
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402

MAPS = os.path.dirname(WORK)


def main():
    m = mpq.MPQ(os.path.join(MAPS, 'Pokemon Arena v3.4.10.w3x'))
    lf = list(m.listfile())
    known = {m.find_hash(n) for n in lf if m.find_hash(n) is not None}
    want = {}
    for i, e in enumerate(m.hash_table):
        if e[4] < mpq.HASH_DELETED and i not in known:
            want[(e[0], e[1])] = e[4]
    print('unnamed files:', len(set(want.values())))
    cands = set()
    for f in glob.glob(os.path.join(WORK, 'out', '*', '*listfile*')) + glob.glob(os.path.join(WORK, 'tools', '*.txt')):
        try:
            cands.update(x.strip() for x in open(f, encoding='latin-1') if x.strip())
        except OSError:
            pass
    for f in (os.path.join(WORK, 'analysis', 'map_scan_models.json'),):
        for v in json.load(open(f, encoding='utf-8')).values():
            cands.update(v.get('list', []))
    for f in ('names.json', 'models_present.json'):
        p = os.path.join(WORK, 'out', 'pkworld', f)
        if os.path.exists(p):
            cands.update(json.load(open(p)))
    p = os.path.join(WORK, 'out', 'pkworld', 'script_models.json')
    if os.path.exists(p):
        cands.update(json.load(open(p))['in_map'])
    # strings in the scripts we have
    for f in glob.glob(os.path.join(WORK, 'out', '*', '*war3map*.j')) + glob.glob(os.path.join(WORK, 'v34', '*.j')):
        t = open(f, encoding='latin-1', errors='replace').read()
        cands.update(re.findall(r'"([^"]{3,120}\.(?:blp|mdx|mdl|tga|wav|mp3))"', t, re.I))
    more = set()
    for c in cands:
        c = c.replace('/', '\\').replace('\\\\', '\\')
        base = c.split('\\')[-1]
        stem = base.rsplit('.', 1)[0]
        for v in (c, base, 'war3mapImported\\' + base):
            more.add(v)
            for ext in ('.blp', '.mdx', '.mdl', '.tga'):
                more.add(v.rsplit('.', 1)[0] + ext)
        more.add('ReplaceableTextures\\CommandButtons\\' + base)
        more.add('ReplaceableTextures\\CommandButtonsDisabled\\DIS' + base)
        more.add('war3mapImported\\' + stem + '_portrait.mdx')
    print('candidates:', len(more))
    found = {}
    for n in more:
        k = (mpq.hash_string(n, mpq.HASH_A), mpq.hash_string(n, mpq.HASH_B))
        if k in want:
            found[want[k]] = n
    print('found:', found)
    out = os.path.join(WORK, 'tools', 'v3411', 'names_v3410.txt')
    old = [x.strip() for x in open(out, encoding='latin-1') if x.strip()] if os.path.exists(out) else []
    open(out, 'w', encoding='latin-1').write('\r\n'.join(sorted(set(old) | set(found.values()))) + '\r\n')


if __name__ == '__main__':
    main()
