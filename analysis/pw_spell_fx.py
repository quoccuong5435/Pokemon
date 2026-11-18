"""Read-only: which effect models each Pokemon World move uses (decoded script + war3map.w3a names).

    python -I analysis/pw_spell_fx.py    -> out/pkworld/spell_fx.json, out/pkworld/spell_fx.csv
Run analysis/pw_models_from_script.py first.
"""
import csv
import json
import os
import re
import struct
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WORK, 'out', 'pkworld')


def parse_obj(path, extra):
    d = open(path, 'rb').read()
    p = 0
    ver = struct.unpack_from('<i', d, p)[0]
    p += 4
    out = {}
    for _table in range(2):
        n = struct.unpack_from('<i', d, p)[0]
        p += 4
        for _ in range(n):
            orig, new = d[p:p + 4], d[p + 4:p + 8]
            p += 8
            sets = 1
            if ver >= 3:
                sets = struct.unpack_from('<i', d, p)[0]
                p += 4
            mods = {}
            for _s in range(sets):
                if ver >= 3:
                    p += 4
                nm = struct.unpack_from('<i', d, p)[0]
                p += 4
                for _m in range(nm):
                    mid = d[p:p + 4].decode('latin-1')
                    t = struct.unpack_from('<i', d, p + 4)[0]
                    p += 8
                    if extra:
                        p += 8
                    if t == 0:
                        v = struct.unpack_from('<i', d, p)[0]
                        p += 4
                    elif t in (1, 2):
                        v = struct.unpack_from('<f', d, p)[0]
                        p += 4
                    else:
                        e = d.index(b'\0', p)
                        v = d[p:e].decode('utf-8', 'replace')
                        p = e + 1
                    p += 4
                    mods.setdefault(mid, v)
            key = (new if new != b'\0\0\0\0' else orig).decode('latin-1')
            out.setdefault(key, {'base': orig.decode('latin-1')}).update(mods)
    return out


def main():
    abil = parse_obj(os.path.join(OUT, 'war3map.w3a'), True)
    for k, v in parse_obj(os.path.join(OUT, 'war3mapSkin.w3a'), True).items():
        abil.setdefault(k, {}).update({x: y for x, y in v.items() if x != 'base'})
    names = {k: v.get('anam', '') for k, v in abil.items()}
    src = open(os.path.join(OUT, 'war3map_decoded.j'), encoding='latin-1').read()
    # code variables: set X=function F  ->  use the function name directly
    cvar = dict(re.findall(r'^set (\w+)=function (\w+)\s*$', src, re.M))
    src = re.sub(r'Condition\((\w+)\)', lambda m: 'Condition(function %s)' % cvar[m.group(1)]
                 if m.group(1) in cvar else m.group(0), src)
    src = re.sub(r'TriggerAddAction\((\w+),(\w+)\)', lambda m: 'TriggerAddAction(%s,function %s)' % (
        m.group(1), cvar[m.group(2)]) if m.group(2) in cvar else m.group(0), src)
    funcs = {}
    for m in re.finditer(r'^function (\w+) takes.*?^endfunction', src, re.M | re.S):
        funcs[m.group(1)] = m.group(0)
    model_re = re.compile(r'"([^"]+\.(?:mdx|mdl))"', re.I)
    call_re = re.compile(r'\b(\w+)\(')
    fref_re = re.compile(r'function (\w+)')

    def models_of(fn, depth=4, seen=None):
        seen = set() if seen is None else seen
        if fn in seen or fn not in funcs or depth < 0:
            return []
        seen.add(fn)
        body = funcs[fn]
        out = model_re.findall(body)
        for c in set(call_re.findall(body)) | set(fref_re.findall(body.split('\n', 1)[1])):
            if c in funcs and c != fn:
                out += models_of(c, depth - 1, seen)
        return out

    # condition functions: abilities they accept
    cond = {}
    for fn, body in funcs.items():
        if 'GetSpellAbilityId()' not in body:
            continue
        ids = re.findall(r'==\$(41[0-9a-fA-F]{6})', body)
        if ids:
            cond[fn] = [bytes.fromhex(x).decode('latin-1') for x in ids]
    # trigger wiring: Condition(function C) ... TriggerAddAction(t, function A) in the same function
    rows = []
    for fn, body in funcs.items():
        for cm in re.finditer(r'TriggerAddCondition\((\w+),Condition\(function (\w+)\)\)', body):
            trig, c = cm.group(1), cm.group(2)
            if c not in cond:
                continue
            acts = re.findall(r'TriggerAddAction\(%s,function (\w+)\)' % re.escape(trig), body)
            fx = []
            for a in acts:
                fx += models_of(a)
            fx = list(dict.fromkeys(fx))
            for aid in cond[c]:
                rows.append({'id': aid, 'name': names.get(aid, ''), 'base': abil.get(aid, {}).get('base', ''),
                             'action': ','.join(acts), 'models': fx})
    # merge by id
    by = {}
    for r in rows:
        e = by.setdefault(r['id'], dict(r, models=[]))
        e['models'] = list(dict.fromkeys(e['models'] + r['models']))
    res = sorted(by.values(), key=lambda r: r['name'])
    json.dump(res, open(os.path.join(OUT, 'spell_fx.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, 'spell_fx.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'base', 'models'])
        for r in res:
            w.writerow([r['id'], r['name'], r['base'], '; '.join(r['models'])])
    print(len(res), 'spell ids with a trigger;', sum(1 for r in res if r['models']), 'with effect models')


if __name__ == '__main__':
    main()
