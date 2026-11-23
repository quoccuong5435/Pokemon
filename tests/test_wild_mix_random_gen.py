"""Tests for tools/v412/wild_mix.py and tools/v412/random_gen.py on the latest (4.2b_test) script and map."""
import os
import re
import subprocess
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import random_gen as G  # noqa: E402
import wild_mix as W  # noqa: E402

REF = os.path.join(WORK, 'analysis', 'jass_ref', '_tmp_v42b_test_war3map.j')  # unpatched 4.2b_test script
MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.2b_test.w3x')
pytestmark = pytest.mark.skipif(not os.path.isfile(REF), reason='4.2b reference script not here')
_cache = {}


def load():
    with open(REF, 'rb') as fh:
        return fh.read().decode('utf-8').replace('\r\r\n', '\r\n').replace('\r\n', '\n')


def w3u():
    if not os.path.isfile(MAP):
        pytest.skip('4.2b_test map not here')
    if 'w3u' not in _cache:
        import mpq
        import objdata
        _cache['w3u'] = objdata.ObjFile(mpq.MPQ(MAP).read('war3map.w3u'))
    return _cache['w3u']


def func(s, name):
    m = re.search(r'\nfunction %s takes[\s\S]*?\nendfunction\n' % re.escape(name), s)
    assert m, name
    return m.group(0)


def test_wild_mix_each_creep_picks_its_own_species():
    out = W.patch_script(load())
    spawn = func(out, 'Wild_SpawnCamp')
    assert 'call WD_MarkAlive()' in spawn and 'set t = WD_Pick(pow)' in spawn
    assert re.search(r'if i > 0 then\s+set t = WD_Pick\(pow\)', spawn)
    assert 'set elite = GetRandomInt(0, Wild_CampAlive[c] - 1)' in spawn
    reinforce = func(out, 'Wild_ReinforceCamp')
    assert reinforce.count('WD_Pick(pow)') == 2 and 'base_t' not in reinforce
    upgrade = func(out, 'Wild_Upgrade')
    assert 'WD_NextForm(GetUnitTypeId(u), pow)' in upgrade and 'Wild_UpT' not in upgrade
    assert out.index('function WD_Pick') < out.index('function Wild_ReinforceCamp')
    assert out.index('function Wild_PickType') < out.index('function WD_Pick')
    with pytest.raises(ValueError):
        W.patch_script(out)


def test_gen_of_dex():
    assert [G.gen_of_dex(d) for d in (1, 151, 152, 386, 387, 493, 494, 1025)] == [1, 1, 2, 3, 4, 4, 5, 9]


def test_proper_name_drops_dex_prefix():
    # 4.3 names the Gen 2-4 heroes "#172 Pichu": they lost their generation before this fix
    assert G.proper_name('#172 Pichu') == 'Pichu'
    assert G.proper_name('Mr. Mime,x') == 'Mr. Mime'
    assert G.proper_name(None) == ''


def test_random_gen_patch():
    out, stats = G.patch_script(load(), w3u())
    assert stats.get(0, 0) == 0, stats  # every hero of the pool has a generation
    assert stats[1] > 50 and stats[4] > 20
    chat = func(out, 'Rand_OnChat')
    assert 'Host_Id()' in chat and 'RandG_Build(want)' in chat and 'call Rand_Auto()' in chat
    assert 'set t = RandG_Pick()' in func(out, 'Rand_Give')
    assert '"-random", false)' in out and '"-random", true)' not in out
    assert 'call ExecuteFunc("RandG_Init")' in out
    assert out.count("call SaveInteger(RandG_HT, '") == sum(stats.values())
    assert out.index('function RandG_Pick') < out.index('function Rand_Give')


def test_pjass_all_modules(tmp_path):
    check = os.path.join(WORK, 'tools', 'v34', 'check.py')
    if not os.path.isfile(check):
        pytest.skip('pjass checker not available')
    import move_tutor
    out, _ = G.patch_script(W.patch_script(move_tutor.patch_script(load())), w3u())
    target = tmp_path / 'war3map.j'
    target.write_text(out.replace('\n', '\r\n'), encoding='utf-8', newline='')
    res = subprocess.run([sys.executable, '-I', check, str(target)], capture_output=True, text=True, cwd=WORK)
    assert 'pjass exit 0, 0 error lines' in (res.stdout + res.stderr), res.stdout[-2000:] + res.stderr[-2000:]
