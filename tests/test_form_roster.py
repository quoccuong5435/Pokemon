"""form_roster: only Pokemon families with an official form can be picked (user request 2026-11-23)."""
import json
import os
import re
import subprocess
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import form_roster  # noqa: E402

MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.3c.w3x')


@pytest.fixture(scope='module')
def built():
    if not os.path.isfile(MAP):
        pytest.skip('v4.3c map not here')
    import mpq
    import objdata
    m = mpq.MPQ(MAP)
    script = m.read('scripts\\war3map.j').decode('latin-1').replace('\r\n', '\n')  # build_v43 patches LF text
    return script, objdata.ObjFile(m.read('war3map.w3u'))


def _pick(script):
    body = re.search(r"function Pick_InitData takes nothing returns nothing\n([\s\S]*?)\nendfunction", script).group(1)
    n = int(re.search(r'set Pick_N = (\d+)', body).group(1))
    types = dict(re.findall(r"set Pick_Type\[(\d+)\] = '(\w{4})'", body))
    first = [int(x) for x in re.findall(r'set Pick_TFirst\[\d+\] = (\d+)', body)]
    count = [int(x) for x in re.findall(r'set Pick_TCount\[\d+\] = (\d+)', body)]
    tn = int(re.search(r'set Pick_TN = (\d+)', body).group(1))
    return n, types, first, count, tn


def _rand(script):
    m = re.search(r"set Rand_N = (\d+)\n((?: *set Rand_Type\[\d+\] = '\w{4}'\n)+)", script.replace('\r\n', '\n'))
    ids = re.findall(r"'(\w{4})'", m.group(2))
    later = re.findall(r"set Rand_Type\[Rand_N\] = '(\w{4})'", script)
    return int(m.group(1)), ids, later


def test_drop_list_is_the_families_without_a_form():
    data = json.load(open(form_roster.DATA, encoding='utf-8'))
    assert len(data['drop_ids']) == 280 and len(data['keep_families']) == 104
    keep = {n for f in data['keep_families'] for n in f}
    # Paradox Pokemon count as a form of the Pokemon they resemble (the map's Booster Energy: Jigglypuff -> Scream Tail);
    # regional evolutions too (Stantler -> Wyrdeer, Ursaring -> Ursaluna)
    for nm in ('Charizard', 'Rotom', 'Alolan-Raichu', 'Tauros Aqua', 'Greninja', 'Pikachu', 'Jigglypuff',
               'Magnemite', 'Misdreavus', 'Deino', 'Phanpy', 'Delibird', 'Makuhita', 'Stantler', 'Teddiursa', 'Cherubi', 'Shellos'):
        assert nm in keep
    # taken out on the user's request (tree page comments 2026-11-23), even though they have a form
    user = {n for f in data['user_drop_families'] for n in f}
    assert user == {'Mr. Mime', 'Wooper', 'Quagsire', 'Qwilfish', 'Burmy', 'Wormadam', 'Darumaka', 'Darmanitan'}
    assert not user & keep and 'P2WA' in data['drop_ids'] and 'E040' not in data['drop_ids']
    drop = {n for f in data['drop_families'] for n in f}
    for nm in ('Aipom', 'Azurill', 'Bidoof'):
        assert nm in drop


def test_pick_and_random_lose_only_the_dropped_heroes(built):
    script, _ = built
    drop = form_roster.start_exclude()
    n0, t0, _, _, _ = _pick(script)
    r0n, r0, l0 = _rand(script)
    out = form_roster.patch_script(script)
    n, types, first, count, tn = _pick(out)
    assert n == len(types) == sum(count) and tn == len(first) == len(count)
    assert first == [sum(count[:i]) for i in range(len(count))] and min(count) > 0
    assert not set(types.values()) & drop
    assert sorted(types.values()) == sorted(h for h in t0.values() if h not in drop)
    rn, r, later = _rand(out)
    assert rn == len(r) and not (set(r) | set(later)) & drop
    assert r == [h for h in r0 if h not in drop] and later == [h for h in l0 if h not in drop]
    assert n < n0 and len(r) + len(later) < len(r0) + len(l0)


def test_taverns_sell_no_dropped_hero(built):
    _, w3u = built
    drop = form_roster.start_exclude()
    res = form_roster.patch_taverns(w3u)
    assert len(res) == 4
    for o in w3u.all():
        v = o.get('useu')
        if v:
            assert not {x for x in str(v).split(',') if x} & drop


def test_patched_script_passes_pjass(built, tmp_path):
    pjass = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
    if not os.path.isfile(pjass):
        pytest.skip('pjass not here')
    script, _ = built
    p = tmp_path / 'war3map.j'
    p.write_bytes(form_roster.patch_script(script).encode('latin-1'))
    ref = os.path.join(WORK, 'analysis', 'jass_ref')
    r = subprocess.run([pjass, os.path.join(ref, 'common.j'), os.path.join(ref, 'Blizzard.j'), str(p)],
                       capture_output=True, text=True)
    assert 'Parse successful' in r.stdout + r.stderr, (r.stdout + r.stderr)[:800]


def test_start_lists_only_offer_the_first_stage(built):
    # user 2026-11-23 "Gỡ, chỉ con đầu dòng": evolved heroes whose pre-evolution is pickable are not offered
    script, w3u = built
    evolved = form_roster.not_first_stage_ids()
    assert {'E005', 'EN0J', 'P3TA', 'P4NA', 'P05A', 'P04A'} <= evolved  # Pikachu, Lucario, Snorlax, Alolan Sandslash / Graveler / Golem
    assert 'P4QA' not in evolved and 'P06A' not in evolved  # Aegislash (no linked pre-evolution), Alolan-Raichu (no way to reach it yet)
    out = form_roster.patch_script(script)
    # the Alolan lines had no evolution in the map: they are linked now, run after the last G14 data function
    for a, b, lv in [('P4MA', 'P4NA', 22), ('P03A', 'P05A', 25), ('P05A', 'P04A', 40)]:
        assert ("set Evo_From[Evo_N] = '%s'\n    set Evo_To[Evo_N] = '%s'\n    set Evo_Level[Evo_N] = %d"
                % (a, b, lv)) in out
    assert 'call ExecuteFunc("G14_Data27")\n    call ExecuteFunc("Roster_EvoData")' in out
    body = re.search(r"function Pick_InitData takes nothing returns nothing\n([\s\S]*?)\nendfunction", out).group(1)
    offered = set(re.findall(r"set Pick_Type\[\d+\] = '(\w{4})'", body)) | set(re.findall(r"set Rand_Type\[[^\]]+\] = '(\w{4})'", out))
    form_roster.patch_taverns(w3u)
    for o in w3u.all():
        if o.get('useu'):
            offered |= {x for x in str(o.get('useu')).split(',') if x}
    assert not offered & evolved
    assert 'EG0M' in offered  # Pichu is offered (it evolves into Pikachu in the map)
