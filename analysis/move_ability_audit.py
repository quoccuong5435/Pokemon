"""Compare the moves / Abilities of a map script with PokeAPI data (tools/pokeapi/*.json).

Usage (from _PokemonArena2.0_work):
  python -I analysis/move_ability_audit.py analysis/jass_ref/_tmp_v42a_war3map.j analysis/move_ability_audit.json
Reads the move tables (Mv_Label / Mv_Pow / Mv_Phys / Mv_Type), the move effect data (Fx_HT key 100000 + move),
the Ability constants (AB_*) and who has which Ability (Ab_HT '<unit>' key 0), then writes one JSON report.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(WORK, 'tools', 'pokeapi')
TYPES = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 'flying', 'ghost', 'grass', 'ground', 'ice',
         'normal', 'poison', 'psychic', 'rock', 'steel', 'water']
STATUS = {1: 'burn', 2: 'poison', 3: 'poison', 4: 'paralysis', 5: 'sleep', 6: 'freeze', 9: 'tri'}
AIL = {'burn': 'burn', 'poison': 'poison', 'paralysis': 'paralysis', 'sleep': 'sleep', 'freeze': 'freeze'}
STAT_KEY = {'attack': 1, 'defense': 2, 'special-attack': 3, 'special-defense': 4, 'speed': 5}
F_MULTI, F_CRIT, F_PRIO = 8, 16, 32


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace("'", '').replace('.', '')).strip('-')


def load(name):
    with open(os.path.join(PK, name), encoding='utf-8') as fh:
        return json.load(fh)


def read_map(path):
    with open(path, encoding='latin-1') as fh:
        s = fh.read()
    moves = defaultdict(dict)
    for key, arr in (('label', 'Mv_Label'), ('pow', 'Mv_Pow'), ('phys', 'Mv_Phys'), ('type', 'Mv_Type'),
                     ('tt', 'Mv_TT')):
        for m in re.finditer(r'set %s\[(\d+)\] = ("?)(.*?)\2\s*$' % arr, s, re.M):
            v = m.group(3)
            moves[int(m.group(1))][key] = v if m.group(2) else int(v) if re.fullmatch(r'-?\d+', v) else v
    fx = defaultdict(dict)
    for m in re.finditer(r'call SaveInteger\(Fx_HT, (1\d{5}), (\d+), (-?\d+)\)', s):
        idx = int(m.group(1)) - 100000
        if idx in moves:
            fx[idx][int(m.group(2))] = int(m.group(3))
    abil_const = {}
    for m in re.finditer(r'constant integer (AB_[A-Z0-9_]+) = (\d+)', s):
        abil_const[int(m.group(2))] = m.group(1)[3:]
    names = {int(m.group(1)): m.group(2) for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', s)}
    infos = {int(m.group(1)): m.group(2) for m in re.finditer(r'set Ab_Info\[(\d+)\] = "(.*?)"\s*$', s, re.M)}
    who = {}
    for m in re.finditer(r"call SaveInteger\(Ab_HT, '(\w{4})', 0, (\d+)\)", s):
        who[m.group(1)] = int(m.group(2))  # later lines win, like in the game
    return moves, fx, abil_const, names, infos, who


def check_move(idx, mv, rec, api):
    """list of (field, map value, PokeAPI value) differences that matter for the effect engine"""
    out = []
    meta = api.get('meta') or {}
    if mv.get('pow', 0) > 0 and api.get('power') and mv['pow'] != api['power']:
        out.append(('power', mv['pow'], api['power']))
    want_cls = 1 if api['class'] == 'physical' else 2 if api['class'] == 'special' else 0
    if want_cls and rec.get(30) and rec[30] != want_cls:
        out.append(('class', rec[30], want_cls))
    if mv.get('type') is not None and isinstance(mv['type'], int) and TYPES[mv['type']] != api['type']:
        out.append(('type', TYPES[mv['type']], api['type']))
    if api['class'] == 'status':
        return out
    ail = AIL.get(meta.get('ailment') or '')
    have = STATUS.get(rec.get(4, 0))
    if ail and meta.get('ailment_chance', 0) and have != 'tri' and (have != ail or rec.get(5) != meta['ailment_chance']):
        out.append(('status', '%s %s%%' % (have, rec.get(5)) if have else '-', '%s %s%%' % (ail, meta['ailment_chance'])))
    if not ail and have and have != 'tri':
        out.append(('status', '%s %s%%' % (have, rec.get(5)), '-'))
    if (meta.get('ailment') == 'confusion') and meta.get('ailment_chance'):
        out.append(('confusion', 'not stored', '%s%%' % meta['ailment_chance']))
    fl = meta.get('flinch_chance') or 0
    if fl != rec.get(6, 0):
        out.append(('flinch', rec.get(6, 0), fl))
    drain = meta.get('drain') or 0
    if drain > 0 and rec.get(3, 0) != drain * 10:
        out.append(('drain', rec.get(3, 0) // 10, drain))
    if drain < 0 and rec.get(2, 0) != -drain * 10:
        out.append(('recoil', rec.get(2, 0) // 10, -drain))
    if drain == 0 and (rec.get(3) or rec.get(2)):
        out.append(('drain/recoil', '%s/%s' % (rec.get(3, 0) // 10, rec.get(2, 0) // 10), '0/0'))
    if (meta.get('healing') or 0) > 0:
        out.append(('healing', '-', meta['healing']))
    changes = {STAT_KEY[k]: v for k, v in api.get('stat_changes') or [] if k in STAT_KEY}
    acc_down = any(k == 'accuracy' and v < 0 for k, v in api.get('stat_changes') or [])
    if changes or acc_down:
        self_side = api['target'] == 'user' or all(v > 0 for v in changes.values()) and meta.get('category') == 'damage-raise'
        base, ch_key = (10, 7) if self_side else (20, 8)
        have_st = {k - base: v for k, v in rec.items() if base < k < base + 6}
        want_ch = meta.get('stat_chance') or 100
        if have_st != changes or rec.get(ch_key, 0) != want_ch:
            out.append(('stages ' + ('self' if self_side else 'target'),
                        '%s @%s%%' % (have_st, rec.get(ch_key, 0)), '%s @%s%%' % (changes, want_ch)))
    else:
        for side, base, ch_key in (('self', 10, 7), ('target', 20, 8)):
            have_st = {k - base: v for k, v in rec.items() if base < k < base + 6}
            if have_st:
                out.append(('stages ' + side, '%s @%s%%' % (have_st, rec.get(ch_key, 0)), '-'))
    flags = rec.get(1, 0)
    if (meta.get('max_hits') or 0) > 1 and not flags & F_MULTI:
        out.append(('multi-hit', '-', '%s-%s' % (meta.get('min_hits'), meta.get('max_hits'))))
    if (meta.get('crit_rate') or 0) > 0 and not flags & F_CRIT:
        out.append(('high crit', '-', '+%s' % meta['crit_rate']))
    if (api.get('priority') or 0) > 0 and not flags & F_PRIO:
        out.append(('priority', '-', api['priority']))
    return out


def main():
    script, out_path = sys.argv[1], sys.argv[2]
    api_moves = load('moves.json')
    api_abil = load('abilities.json')
    poke_ab = load('pokemon_abilities.json')
    with open(os.path.join(WORK, 'analysis', 'melee_ranged.json'), encoding='utf-8') as fh:
        roster = json.load(fh)
    learn = load(os.path.join('..', 'learnsets.json'))
    moves, fx, abil_const, names, infos, who = read_map(script)

    report = {'moves': [], 'abilities': [], 'heroes': []}
    kinds = Counter()
    for idx in sorted(moves):
        mv = moves[idx]
        name = re.sub(r'\s*\(.*$', '', mv.get('label', ''))
        api = api_moves.get(slug(name))
        if not api:
            report['moves'].append({'idx': idx, 'name': name, 'missing_in_api': True})
            continue
        diffs = check_move(idx, mv, fx.get(idx, {}), api)
        for d in diffs:
            kinds[d[0]] += 1
        report['moves'].append({'idx': idx, 'name': name, 'class': api['class'], 'diffs': diffs})

    by_name = {sp['name'].lower(): slug_ for slug_, sp in learn['species'].items()}
    extra = {'latias & latios': 'latias', 'zygarde': 'zygarde-50', 'mr. mime': 'mr-mime'}
    used = Counter()
    for r in roster:
        n = r['name'].lower()
        sp = by_name.get(n) or extra.get(n) or slug(r['name'])
        real = poke_ab.get(sp, [])
        ab = who.get(r['id'])
        used[ab] += 1
        cname = (names.get(ab) or abil_const.get(ab, '?')) if ab else None
        match = bool(cname) and any(slug(cname) == a for a, _h in real)
        report['heroes'].append({'id': r['id'], 'name': r['name'], 'map_ability': cname, 'real': real, 'match': match})
    for k in sorted(abil_const):
        nm = names.get(k) or abil_const[k].title()
        api = api_abil.get(slug(nm))
        report['abilities'].append({'idx': k, 'name': nm, 'heroes': used.get(k, 0), 'info': infos.get(k, ''),
                                    'pokeapi': (api or {}).get('short_effect', '')})

    report['summary'] = {
        'moves': len(moves), 'moves_with_diffs': sum(1 for m in report['moves'] if m.get('diffs')),
        'diff_kinds': dict(kinds.most_common()),
        'heroes': len(roster), 'heroes_without_ability': sum(1 for h in report['heroes'] if not h['map_ability']),
        'heroes_real_ability': sum(1 for h in report['heroes'] if h['match']),
        'map_abilities': len(abil_const),
        'real_abilities_of_roster': len({a for h in report['heroes'] for a, _h in h['real']}),
    }
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(json.dumps(report['summary'], indent=1))


if __name__ == '__main__':
    main()
