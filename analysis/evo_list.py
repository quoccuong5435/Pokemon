"""List the playable Pokemon of a map script and how each one evolves (level, stone, Mega) -> JSON.

python -I analysis/evo_list.py <war3map.j> <map.w3x> <out.json>
Sources: the v1.8 level / item triggers, Evo_* (level) and Evo_Item* (stones) of the mod, Mega_Base / Mega_Stone.
"""
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import model_size_check  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402


def load_script(path):
    with open(path, 'rb') as fh:
        return fh.read().decode('utf-8', 'replace').replace('\r\r\n', '\r\n').replace('\r\n', '\n').replace('\r', '\n')


def evo_tables(s):
    """simulate the set Evo_* lines in file order"""
    lvl, item = {}, {}
    n = {'Evo_N': 0, 'Evo_ItemN': 0}
    pat = re.compile(r"^\s*set (Evo_N|Evo_ItemN) = (?:(\d+)|\1 \+ 1)\s*$|"
                     r"^\s*set (Evo_From|Evo_To|Evo_Level|Evo_ItemFrom|Evo_Item|Evo_ItemTo)\[(\d+|Evo_N|Evo_ItemN)\] = '?(\w+)'?\s*$")
    for line in s.split('\n'):
        if 'Evo_' not in line:
            continue
        m = pat.match(line)
        if not m:
            continue
        if m.group(1):
            n[m.group(1)] = int(m.group(2)) if m.group(2) else n[m.group(1)] + 1
            continue
        arr, idx, val = m.group(3), m.group(4), m.group(5)
        i = n[idx] if not idx.isdigit() else int(idx)
        tab = item if arr.startswith('Evo_Item') else lvl
        tab.setdefault(i, {})[arr] = val
    out = []
    for i, d in lvl.items():
        if i < n['Evo_N'] and 'Evo_From' in d and 'Evo_To' in d:
            out.append((d['Evo_From'], d['Evo_To'], 'lv', int(d.get('Evo_Level', 0))))
    for i, d in item.items():
        if i < n['Evo_ItemN'] and {'Evo_ItemFrom', 'Evo_Item', 'Evo_ItemTo'} <= set(d):
            out.append((d['Evo_ItemFrom'], d['Evo_ItemTo'], 'item', d['Evo_Item']))
    return out


def v18_triggers(s):
    conds = {}
    for m in re.finditer(r'(?m)^function (\w+) takes nothing returns boolean\n(.*?)\nendfunction', s, re.S):
        b = m.group(2)
        lv = re.search(r'Get(?:Unit|Hero)Level\(GetLevelingUnit\(\)\)>(=?)(\d+)', b)
        conds[m.group(1)] = {
            'lv': int(lv.group(2)) + (0 if lv.group(1) else 1) if lv else None,
            'ty': re.findall(r"GetUnitTypeId\(Get(?:LevelingUnit|ManipulatingUnit|TriggerUnit)\(\)\)=='(....)'", b),
            'it': re.findall(r"GetItemTypeId\(GetManipulatedItem\(\)\)=='(....)'", b)}
    acts = {m.group(1): m.group(2) for m in
            re.finditer(r'(?m)^function (\w+) takes nothing returns nothing\n(.*?)\nendfunction', s, re.S)}
    out = []
    for trig, cond, act in re.findall(r"call TriggerAddCondition\((\w+),Condition\(function (\w+)\)\)\n"
                                      r"call TriggerAddAction\(\1,function (\w+)\)", s):
        its = conds.get(cond, {}).get('it', [])
        body = acts.get(act, '')
        for m in re.finditer(r"if\((\w+)\(\)\)then\n(?:[^\n]*\n){0,4}?call Mega_SafeReplace\(Get\w+\(\),'(....)'", body):
            c = conds.get(m.group(1))
            if not c:
                continue
            for fr in c['ty']:
                if its:
                    out.extend((fr, m.group(2), 'item', it) for it in its)
                elif c['lv']:
                    out.append((fr, m.group(2), 'lv', c['lv']))
    return out


def megas(s):
    d = {}
    for arr, i, val in re.findall(r'^\s*set (Mega_Base|Mega_Name|Mega_StoneName|Mega_Skin)\[(\d+)\] = (.+?)\s*$', s, re.M):
        d.setdefault(int(i), {})[arr] = val.strip("'\"")
    return [v for _k, v in sorted(d.items()) if 'Mega_Base' in v and 'Mega_Name' in v]


def main(script_path, map_path, out_path):
    s = load_script(script_path)
    m = mpq.MPQ(map_path)
    w3u = objdata.ObjFile(m.read('war3map.w3u'))
    units = {u.id: u for u in w3u.original + w3u.custom}
    itxt = m.read('Units\\ItemFunc.txt').decode('utf-8', 'replace')
    inames = dict(re.findall(r'\[(\w{4})\]\r?\n(?:[^\[]*?\n)?Name=([^\r\n]*)', itxt))
    with open(os.path.join(WORK, 'tools', 'pokeapi', 'pokemon_size.json'), encoding='utf-8') as fh:
        species = json.load(fh)

    def name(uid):
        u = units.get(uid)
        return re.sub(r'^#\d+\s+', '', (u.get('upro') or '').split(',')[0].strip()) if u else ''

    def is_hero(uid):
        return uid[:1].isupper() and bool(name(uid))

    pool = list(dict.fromkeys(re.findall(r"set Rand_Type\[[^\]]*\] = '(\w{4})'", s)))
    edges = {}
    for a, b, kind, val in v18_triggers(s) + evo_tables(s):
        if a == b or not (is_hero(a) and is_hero(b)):
            continue
        cond = ('Lv %d' % val) if kind == 'lv' else inames.get(val, val)
        edges.setdefault((a, b), [])
        if cond not in edges[(a, b)]:
            edges[(a, b)].append(cond)
    nodes = set(pool) | {x for e in edges for x in e}
    mg = []
    for v in megas(s):
        if v['Mega_Base'] in nodes:
            mg.append({'from': v['Mega_Base'], 'name': v['Mega_Name'], 'stone': v.get('Mega_StoneName', '')})
    parent = {x: x for x in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    fams = {}
    for x in nodes:
        fams.setdefault(find(x), []).append(x)

    def info(uid):
        rec = species.get(model_size_check.slug(name(uid)))
        return {'id': uid, 'name': name(uid), 'dex': int(rec['dex']) if rec else 0,
                'types': rec['types'] if rec else [], 'random': uid in pool}
    out = []
    for members in fams.values():
        mem = set(members)
        inc = {b for (a, b) in edges if a in mem}
        roots = sorted([x for x in mem if x not in inc] or members, key=lambda u: (info(u)['dex'] or 9999, u))
        fam = {'members': {u: info(u) for u in members},
               'edges': [{'from': a, 'to': b, 'cond': c} for (a, b), c in sorted(edges.items()) if a in mem],
               'megas': [x for x in mg if x['from'] in mem], 'roots': roots}
        fam['dex'] = min([v['dex'] for v in fam['members'].values() if v['dex']] or [9999])
        out.append(fam)
    out.sort(key=lambda f: (f['dex'], f['roots'][0]))
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    nm = sum(len(f['members']) for f in out)
    print('families', len(out), 'pokemon', nm, 'edges', len(edges), 'megas', len(mg), 'pool', len(pool),
          'no dex', [v['name'] or v['id'] for f in out for v in f['members'].values() if not v['dex']])


if __name__ == '__main__':
    main(*sys.argv[1:4])
