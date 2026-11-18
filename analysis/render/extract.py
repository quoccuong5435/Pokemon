"""Read-only for the maps: write the Pokemon World effect models used by v3.4.16 (+ their textures) to
out/render_assets/ for the render check (analysis/render/index.html), and out/render_assets/list.json.

    python -I analysis/render/extract.py      (run tools/v3411/apply.py first: it writes v3411/plan.json)
"""
import json
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import mpq  # noqa: E402
import mdxinfo  # noqa: E402

OUT = os.path.join(WORK, 'out', 'render_assets')


class PW(mpq.MPQ):
    def _find_header(self):
        return 1024


def main():
    plan = json.load(open(os.path.join(WORK, 'v3411', 'plan.json'), encoding='utf-8'))
    pool = json.load(open(os.path.join(WORK, 'tools', 'v3411', 'fx_pool_pw.json')))
    names = sorted(plan['fx_more']['pw_models'])
    pw = PW(os.path.join(os.path.dirname(WORK), 'Pokemon World V1.71.w3x'))
    os.makedirs(OUT, exist_ok=True)
    items = []
    for key in names:
        e = pool[key]
        data = pw.read(e['path'])
        rel = 'models/%s.mdx' % key.replace(' ', '_')
        path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'wb').write(data)
        for t in mdxinfo.info(data)['textures']:
            if t and pw.has(t):
                tp = os.path.join(OUT, 'tex', t.replace('\\', '/').lower())
                os.makedirs(os.path.dirname(tp), exist_ok=True)
                open(tp, 'wb').write(pw.read(t))
        seqs = mdxinfo.info(data)['seqs']
        items.append({'key': key, 'url': rel, 'seqs': [s for s, _ in seqs]})
    json.dump(items, open(os.path.join(OUT, 'list.json'), 'w'), indent=0)
    print(len(items), 'models written to', OUT)


if __name__ == '__main__':
    main()
