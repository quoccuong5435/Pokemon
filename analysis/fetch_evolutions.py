"""Evolution chains of the PKLegends species that are not playable yet (PokeAPI, cached).

Output: tools/evolutions.json = {species name: {"chain": [[from, to, trigger, level or item, min happiness]...],
                                                  "stage": 1-based stage of this species in its chain}}
Usage (from _PokemonArena2.0_work):  python -I analysis/fetch_evolutions.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join('analysis'))
import fetch_pokeapi as fp  # noqa: E402


def species_chain(name):
    s = fp.slug(name)
    sp = fp.get('pokemon-species/' + s)
    if sp is None or not sp.get('evolution_chain'):
        return None
    return sp['evolution_chain']


def walk(node, out, parent=None):
    """Flatten a chain tree into (from, to, trigger, level/item) edges."""
    for ev in node.get('evolves_to', []):
        d = ev.get('evolution_details', [{}])[0]
        frm = node['species']['name']
        to = ev['species']['name']
        item = d.get('item') or {}
        out.append([frm, to, d.get('trigger', {}).get('name'), d.get('min_level') or (item.get('name') if item else '') or ''])
        walk(ev, out, frm)


def main():
    names = [l.strip() for l in open(os.path.join('analysis', 'pkl_not_in_arena.txt'), encoding='utf-8') if l.strip()]
    res, missing = {}, []
    done_chain = {}
    for name in names:
        if name.strip().lower() in fp.SKIP:
            continue
        url = species_chain(name)
        if url is None:
            missing.append(name)
            continue
        cid = url['url'].rstrip('/').split('/')[-1]
        if cid not in done_chain:
            node = fp.get('evolution-chain/' + cid)
            edges = []
            walk(node['chain'], edges)
            done_chain[cid] = edges
        res[name] = {'chain_id': cid, 'chain': done_chain[cid]}
    out = {'source': 'PokeAPI evolution-chain (cached in analysis/pokeapi_cache)', 'species': res, 'missing': missing}
    json.dump(out, open(os.path.join('tools', 'evolutions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('species', len(res), 'chains', len(done_chain), 'missing', missing)


if __name__ == '__main__':
    main()
