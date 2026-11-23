"""Tests for tools/v412/item_fix.py (Shell Bell lifesteal, lifesteal numbers, Gym 8 armor break)."""
import os
import re
import subprocess
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import item_fix as I  # noqa: E402

REF = os.path.join(WORK, 'analysis', 'jass_ref', '_tmp_v42b_test_war3map.j')  # unpatched 4.2b_test script
MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.2b_test.w3x')
pytestmark = pytest.mark.skipif(not os.path.isfile(REF), reason='4.2b reference script not here')
BS = chr(92)


def load():
    with open(REF, 'rb') as fh:
        return fh.read().decode('utf-8').replace('\r\r\n', '\r\n').replace('\r\n', '\n')


def func(s, name):
    m = re.search(r'\nfunction %s takes[\s\S]*?\nendfunction\n' % re.escape(name), s)
    assert m, name
    return m.group(0)


def test_script_patch():
    out = I.patch_script(load())
    hit = func(out, 'PAX_Loot_OnHitEx')
    assert 'IF_BellPct(src)' in hit and 'call IF_ShowHeal(src, heal - GetWidgetLife(src))' in hit
    dmg = func(out, 'Ab_OnDamaging')
    assert 'call GA_Shred(src, t)' in dmg and 'V413_ArmorCut' not in dmg
    assert 'function GA_Tick)' in out
    helmet = func(out, 'Ext_AfterHit')
    assert 'IF_HelmetPct * I2R(BlzGetUnitMaxHP(t))' in helmet and 'BlzGetUnitMaxHP(src)))  // Rocky' not in helmet
    assert 'constant real IF_HelmetPct = 0.05' in out
    assert out.index('function Itm_Has') < out.index('function IF_BellPct') < out.index('function PAX_Loot_OnHitEx')
    assert out.index('function PAX_FloatText') < out.index('function GA_Shred') < out.index('function Ab_OnDamaging')
    with pytest.raises(ValueError):
        I.patch_script(out)


@pytest.mark.skipif(not os.path.isfile(MAP), reason='4.2b_test map not here')
def test_objects_and_text():
    import mpq
    import slk
    arc = mpq.MPQ(MAP)
    abil = slk.Slk(arc.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    row = abil.find('A09S')
    assert abil.get(row, 'code') == 'AIva' and float(abil.get(row, 'DataA1')) == pytest.approx(0.1)
    I.patch_objects(abil)
    assert float(abil.get(abil.find('A09S'), 'DataA1')) == 0.0
    func_txt = arc.read('Units' + BS + 'ItemFunc.txt').decode('utf-8')
    out = I.patch_item_text(func_txt)
    assert I.NEW_TIP in out and I.OLD_TIP not in out
    assert I.NEW_RH_TIP in out and I.OLD_RH_TIP not in out


@pytest.mark.skipif(not os.path.isfile(MAP), reason='4.2b_test map not here')
def test_pjass_all_modules(tmp_path):
    check = os.path.join(WORK, 'tools', 'v34', 'check.py')
    if not os.path.isfile(check):
        pytest.skip('pjass checker not available')
    import mpq
    import objdata
    import move_ability_fix
    import ability_rw
    import hidden_ability
    import move_tutor
    import wild_mix
    import random_gen
    w3u = objdata.ObjFile(mpq.MPQ(MAP).read('war3map.w3u'))
    s = hidden_ability.patch(ability_rw.patch(move_ability_fix.patch(load())))
    s = I.patch_script(wild_mix.patch_script(move_tutor.patch_script(s)))
    s, _ = random_gen.patch_script(s, w3u)
    target = tmp_path / 'war3map.j'
    target.write_text(s.replace('\n', '\r\n'), encoding='utf-8', newline='')
    res = subprocess.run([sys.executable, '-I', check, str(target)], capture_output=True, text=True, cwd=WORK)
    assert 'pjass exit 0, 0 error lines' in (res.stdout + res.stderr), res.stdout[-2000:] + res.stderr[-2000:]
