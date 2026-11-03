"""Merge a batch of Serebii level-up tables into tools/learnsets.json.

Input rows: (level, move, serebii category, power). Level 'Evolve', '-' or '--' means known from the start (level 1).
Serebii 'Other' is a status move (power 0). Power '??' or missing counts as 0.
"""
import json
import sys

PATH = 'tools/learnsets.json'


def convert(rows):
    out = []
    for lv, mv, _type, cat, pw in rows:
        lvl = 1 if lv in ('Evolve', '-', '--', '—') else int(lv)
        c = 'Status' if cat == 'Other' else cat
        try:
            p = int(pw)
        except ValueError:
            p = 0
        if c == 'Status':
            p = 0
        out.append([lvl, mv, c, p])
    return out


def merge(batch):
    d = json.load(open(PATH, encoding='utf-8'))
    for name, rows in batch.items():
        d['species'][name] = convert(rows)
    d['source'] = ('Serebii (https://www.serebii.net/pokedex-sv/<species>/): level-up tables, Scarlet/Violet. '
                   'Evolve, dash and double dash rows count as level 1.')
    json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return sorted(d['species'])


if __name__ == '__main__':
    batch = json.load(open(sys.argv[1], encoding='utf-8'))
    print(len(merge(batch)), 'species in learnsets.json')
