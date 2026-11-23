"""Form roster (user request 2026-11-23): players can only pick Pokemon whose evolution family has an official form
(Mega, Primal, Alola, Galar, Hisui, Paldea, Gigantamax, Terastal, Origin / Therian / Rotom ...).

The other families (`form_roster_data.json` -> drop_ids, made from v4.3c with analysis/evo_list.py and PokeAPI) are
taken out of the three ways to pick a hero:
- the taverns (`useu` of the ntav units in war3map.w3u),
- the `-pick` type dialog (`Pick_InitData`, rebuilt with its type groups),
- `-random` (`Rand_Type` / `Rand_N`).
Their units, wild creeps, gym teams, Souls and evolutions stay in the map, so nothing that refers to them breaks.
The start lists also lose the heroes whose pre-evolution is a pickable hero (`not_first_stage_ids`, user
2026-11-23 "chỉ con đầu dòng": Pikachu -> start as Pichu, Lucario -> Riolu); they are still reached by evolving.

Build: `script = form_roster.patch_script(script)` after gen14_expansion and random_gen; `form_roster.patch_taverns(w3u)`.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'form_roster_data.json')


def drop_ids():
    with open(DATA, encoding='utf-8') as fh:
        return set(json.load(fh)['drop_ids'])


def not_first_stage_ids():
    with open(DATA, encoding='utf-8') as fh:
        return set(json.load(fh).get('not_first_stage_ids', []))


def start_exclude():
    """Heroes that must not be offered at the start: dropped families + evolved heroes."""
    return drop_ids() | not_first_stage_ids()


def _patch_pick(script, drop):
    m = re.search(r"function Pick_InitData takes nothing returns nothing\n([\s\S]*?)\nendfunction", script)
    if not m:
        raise ValueError('[form_roster] Pick_InitData not found')
    body = m.group(1)
    types = dict(re.findall(r"set Pick_Type\[(\d+)\] = '(\w{4})'", body))
    names = dict(re.findall(r'set Pick_Name\[(\d+)\] = "([^"]*)"', body))
    tname = dict(re.findall(r'set Pick_TName\[(\d+)\] = "([^"]*)"', body))
    tfirst = dict(re.findall(r'set Pick_TFirst\[(\d+)\] = (\d+)', body))
    tcount = dict(re.findall(r'set Pick_TCount\[(\d+)\] = (\d+)', body))
    out, groups, k = [], [], 0
    for g in sorted(tname, key=int):
        first, cnt = int(tfirst[g]), int(tcount[g])
        start = k
        for i in range(first, first + cnt):
            hid = types[str(i)]
            if hid in drop:
                continue
            out.append("    set Pick_Type[%d] = '%s'" % (k, hid))
            out.append('    set Pick_Name[%d] = "%s"' % (k, names.get(str(i), '')))
            k += 1
        if k > start:
            groups.append((tname[g], start, k - start))
    lines = ['    set Pick_N = %d' % k] + out + ['    set Pick_TN = %d' % len(groups)]
    for gi, (nm, first, cnt) in enumerate(groups):
        lines += ['    set Pick_TName[%d] = "%s"' % (gi, nm), '    set Pick_TFirst[%d] = %d' % (gi, first),
                  '    set Pick_TCount[%d] = %d' % (gi, cnt)]
    new = "function Pick_InitData takes nothing returns nothing\n" + "\n".join(lines) + "\nendfunction"
    return script.replace(m.group(0), new, 1), k, len(types)


def _patch_rand(script, drop):
    # the first block: "set Rand_N = 128" then Rand_Type[0..127]; renumber the kept ones
    m = re.search(r"( *)set Rand_N = (\d+)\n((?: *set Rand_Type\[\d+\] = '\w{4}'\n)+)", script)
    if not m:
        raise ValueError('[form_roster] Rand_Type block not found')
    ind = m.group(1)
    ids = re.findall(r"set Rand_Type\[\d+\] = '(\w{4})'", m.group(3))
    if len(ids) != int(m.group(2)):
        raise ValueError('[form_roster] Rand_N %s but %d Rand_Type lines' % (m.group(2), len(ids)))
    kept = [h for h in ids if h not in drop]
    block = ind + 'set Rand_N = %d\n' % len(kept) + ''.join(
        ind + "set Rand_Type[%d] = '%s'\n" % (i, h) for i, h in enumerate(kept))
    script = script[:m.start()] + block + script[m.end():]
    total = len(ids)
    # later additions: "set Rand_Type[Rand_N] = 'X'" + "set Rand_N = Rand_N + 1"
    pat = re.compile(r" *set Rand_Type\[Rand_N\] = '(\w{4})'\r?\n *set Rand_N = Rand_N \+ 1\r?\n")

    def sub(mm):
        nonlocal total
        total += 1
        if mm.group(1) in drop:
            return ''
        kept.append(mm.group(1))
        return mm.group(0)
    script = pat.sub(sub, script)
    return script, len(kept), total


# The map's Alolan heroes had no evolution between them (each was picked directly). Now that only the first stage is
# offered, link them like the normal lines (Sandshrew -> Sandslash Lv 22, Geodude -> Graveler Lv 25 -> Golem Lv 40).
# Alolan-Raichu stays pickable until the Regional Charm branch exists: Pikachu evolves into Raichu.
EXTRA_EVO = [('P4MA', 'P4NA', 22), ('P03A', 'P05A', 25), ('P05A', 'P04A', 40)]
EVO_ANCHOR = '    call ExecuteFunc("G14_Data27")\n'


def _patch_evo(script):
    """Appends EXTRA_EVO after the last G14 data function (all absolute Evo_N sets ran before it)."""
    if EVO_ANCHOR not in script or 'function Fx_Init takes nothing returns nothing' not in script:
        raise ValueError('[form_roster] Fx_Init / G14_Data27 call not found')
    lines = ['function Roster_EvoData takes nothing returns nothing']
    for a, b, lv in EXTRA_EVO:
        lines += ["    set Evo_From[Evo_N] = '%s'" % a, "    set Evo_To[Evo_N] = '%s'" % b,
                  '    set Evo_Level[Evo_N] = %d' % lv, '    set Evo_N = Evo_N + 1']
    fn = '\n'.join(lines) + '\nendfunction\n\n'
    script = script.replace('function Fx_Init takes nothing returns nothing', fn +
                            'function Fx_Init takes nothing returns nothing', 1)
    return script.replace(EVO_ANCHOR, EVO_ANCHOR + '    call ExecuteFunc("Roster_EvoData")  // form_roster\n', 1)


def patch_script(script):
    drop = start_exclude()
    script, pick_n, pick_was = _patch_pick(script, drop)
    script, rand_n, rand_was = _patch_rand(script, drop)
    script = _patch_evo(script)
    print('[form_roster] -pick %d -> %d, -random %d -> %d, +%d evolutions' % (pick_was, pick_n, rand_was, rand_n,
                                                                            len(EXTRA_EVO)))
    return script


DROP_UNMAPPED_WILD = {'n02Q', 'n02S', 'n02T', 'n02U'}


def collect_dropped_wild_ids(script):
    """Returns wild unit IDs whose playable hero belongs to a dropped family (or unmapped dropped lines)."""
    drop = drop_ids()
    w2s = dict(re.findall(r"call SaveInteger\(Mega_HT, '(\w{4})', 8, '(\w{4})'\)", script))
    # Indexed Soul_Item[i] / Soul_Hero[i]
    s_items = dict(re.findall(r"set Soul_Item\[(\d+)\] = '(\w{4})'", script))
    s_heroes = dict(re.findall(r"set Soul_Hero\[(\d+)\] = '(\w{4})'", script))
    soul_to_hero = {s_items[k]: s_heroes[k] for k in s_items if k in s_heroes}
    # Dynamic Soul_Item[Soul_N] / Soul_Hero[Soul_N] (gen14_expansion)
    for sid, hid in re.findall(
        r"set Soul_Item\[Soul_N\] = '(\w{4})'\s+set Soul_Hero\[Soul_N\] = '(\w{4})'", script
    ):
        soul_to_hero[sid] = hid
    dropped_wild = set()
    for wid, sid in w2s.items():
        hid = soul_to_hero.get(sid)
        if hid in drop:
            dropped_wild.add(wid)
    dropped_wild |= (DROP_UNMAPPED_WILD & set(re.findall(r"set Wild_Pool\[[^\]]+\] = '(\w{4})'", script)))
    return sorted(dropped_wild)


def patch_wild_pool(script):
    """Filters Wild_Type and Wild_Pool right before Wild_IndexPool so wild camps only spawn the 104 kept lines."""
    anchor = '    call ExecuteFunc("Wild_IndexPool")\n'
    target_fn = 'function Wild_IndexPool takes nothing returns nothing'
    if anchor not in script or target_fn not in script:
        raise ValueError('[form_roster] Wild_IndexPool anchor not found')
    drop_wild = collect_dropped_wild_ids(script)
    if not drop_wild:
        return script
    chunks = [drop_wild[i:i + 150] for i in range(0, len(drop_wild), 150)]
    jass = []
    calls = []
    for ci, chunk in enumerate(chunks):
        fn = 'Roster_MarkDropWild%d' % ci
        calls.append('    call ExecuteFunc("%s")' % fn)
        jass.append('function %s takes nothing returns nothing' % fn)
        for wid in chunk:
            jass.append("    call SaveBoolean(Mega_HT, '%s', 999, true)" % wid)
        jass.append('endfunction\n')
    jass.append("""function Roster_FilterWild takes nothing returns nothing
    local integer i = 0
    local integer w = 0
    loop
        exitwhen i >= Wild_TypeN
        if not LoadBoolean(Mega_HT, Wild_Type[i], 999) then
            set Wild_Type[w] = Wild_Type[i]
            set w = w + 1
        endif
        set i = i + 1
    endloop
    set Wild_TypeN = w
    set i = 0
    set w = 0
    loop
        exitwhen i >= Wild_PoolN
        if not LoadBoolean(Mega_HT, Wild_Pool[i], 999) then
            set Wild_Pool[w] = Wild_Pool[i]
            set Wild_PoolPow[w] = Wild_PoolPow[i]
            set w = w + 1
        endif
        set i = i + 1
    endloop
    set Wild_PoolN = w
endfunction
""")
    calls.append('    call ExecuteFunc("Roster_FilterWild")')
    script = script.replace(target_fn, '\n'.join(jass) + target_fn, 1)
    script = script.replace(anchor, '\n'.join(calls) + '\n' + anchor, 1)
    print('[form_roster] wild pool filtered: -%d wild species (104 kept families only)' % len(drop_wild))
    return script


def patch_taverns(w3u):
    """Removes the dropped heroes from every unit that sells heroes (useu). Returns {tavern id: (before, after)}."""
    drop = start_exclude()
    res = {}
    for o in w3u.all():
        v = o.get('useu')
        if not v:
            continue
        ids = [x for x in str(v).split(',') if x]
        kept = [x for x in ids if x not in drop]
        if len(kept) != len(ids):
            typ = next(md.type for md in o.mods if md.field == 'useu')
            o.set('useu', typ, ','.join(kept))
        res[o.id] = (len(ids), len(kept))
    print('[form_roster] taverns', res)
    return res
