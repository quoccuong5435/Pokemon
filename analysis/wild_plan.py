"""Read-only: proposal of the new wild creeps (every non-legend playable species that has no wild creep yet).

python -I analysis/wild_plan.py  ->  analysis/wild_plan.json + markdown table on stdout

Power range of a species (the camps pick a species of their power 1..10):
  start level L = 1 for a first form, else the level it evolves at (same evolution data as the gyms);
  p_min = highest power whose level (Wild_PowLv) is <= L; p_max = p_min of its next form - 1, or 10 for a last form;
  a Pokemon with no evolution at all starts by its base stat total (PokeAPI cache).
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import apply as A  # noqa: E402

POW_LV = {p: lv for p, (lv, _hp) in A.POWER_LV_HP.items()}
EXTRA = {'Meganium': ('Bayleef', 32, ['Grass']), 'Porygon2': ('Porygon', 50, ['Normal'])}  # new forms of v3.4
SKIP = {'Latias & Latios', 'Leafleon'}  # Leafleon = second unit of Leafeon


def power_of_level(lv):
    p = 1
    for k in sorted(POW_LV):
        if POW_LV[k] <= lv:
            p = k
    return p


def bst(name):
    n = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-').replace('.', ''))
    n = n.replace('alolan-', '') + ('-alola' if name.startswith('Alolan-') else '')
    for cand in (n, n.split('-')[0]):
        p = os.path.join(WORK, 'analysis', 'pokeapi_cache', 'pokemon__%s.json' % cand)
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8'))
            st = d.get('stats') or []
            return sum(s['base_stat'] if isinstance(s, dict) else s for s in st) or None
    return None


def single_start(total):
    if total is None:
        return 3
    for lim, p in ((330, 1), (400, 2), (450, 3), (480, 4), (500, 5), (520, 6), (540, 7)):
        if total < lim:
            return p
    return 8


def main():
    script = open(A.BASE_SCRIPT, encoding='utf-8').read()
    units = A.unit_data(A.BASE_MAP)
    report = []
    _out, edges, ids, names = A.gym_evolutions(script, units, report)
    _by_id, by_name = A.hero_types(units)
    for new, (pre, lv, ty) in EXTRA.items():
        edges[(pre, new)] = lv
        ids.setdefault(new, ['(new)'])
        by_name[new] = ty
    # species that already have a wild creep
    wild = set()
    for i, t in re.findall(r"set Wild_Pool\[(\d+)\] = '(\w{4})'", script):
        o = units.get(t)
        n = (o.get('unam') if o else t) or t
        wild.add(A._norm(n[5:] if n.startswith('Wild ') else n))
    wild.add('nidoran')
    incoming, outgoing = {}, {}
    for (a, b), lv in edges.items():
        incoming[b] = min(lv, incoming.get(b, 999))
        outgoing.setdefault(a, []).append(b)
    seen, rows = set(), []
    for sp in sorted(ids, key=str.lower):
        key = A._norm(sp)
        if sp in A.LEGENDS or sp in SKIP or key in seen or key in wild:
            continue
        seen.add(key)
        total = bst(sp)
        if sp in incoming:
            lv = incoming[sp]
            pmin = power_of_level(lv)
        elif sp in outgoing:
            lv, pmin = 1, 1
        else:
            lv, pmin = None, single_start(total)
        nexts = [power_of_level(edges[(sp, b)]) for b in outgoing.get(sp, [])]
        pmax = max(pmin, min(nexts) - 1) if nexts else 10
        rows.append(dict(species=sp, ids=ids[sp], types=by_name.get(sp, []), level=lv, bst=total,
                         pmin=pmin, pmax=pmax))
    json.dump(rows, open(os.path.join(WORK, 'analysis', 'wild_plan.json'), 'w', encoding='utf-8'), indent=1)
    per = {p: 0 for p in range(1, 11)}
    for r in rows:
        for p in range(r['pmin'], r['pmax'] + 1):
            per[p] += 1
    print('new wild species:', len(rows))
    print('species per power (new only):', per)
    print()
    groups = {}
    for r in sorted(rows, key=lambda r: r['species'].lower()):
        rng = str(r['pmin']) if r['pmin'] == r['pmax'] else '%d-%d' % (r['pmin'], r['pmax'])
        groups.setdefault(r['pmin'], []).append('%s (%s)' % (r['species'], rng))
    for p in sorted(groups):
        print('- **Bac %d tro len** (%d loai): %s' % (p, len(groups[p]), ', '.join(groups[p])))
    print()
    print('| # | Pokemon | He | Form tu lv | Bac quai | Soul -> |')
    print('|---|---|---|---|---|---|')
    for i, r in enumerate(sorted(rows, key=lambda r: (r['pmin'], r['species'].lower())), 1):
        lv = '-' if r['level'] is None else str(r['level'])
        if r['level'] is None:
            lv = '1 dang (BST %s)' % r['bst']
        rng = str(r['pmin']) if r['pmin'] == r['pmax'] else '%d-%d' % (r['pmin'], r['pmax'])
        print('| %d | %s | %s | %s | %s | %s |' % (i, r['species'], '/'.join(r['types']), lv, rng, r['species']))


if __name__ == '__main__':
    main()
