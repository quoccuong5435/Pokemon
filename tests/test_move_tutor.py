"""Tests for tools/v412/move_tutor.py (moves NPC rework + level-up move question) on the latest reference script."""
import os
import re
import subprocess
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import move_tutor as T  # noqa: E402

REF = os.path.join(WORK, 'analysis', 'jass_ref', '_tmp_v42b_test_war3map.j')  # unpatched 4.2b_test script
pytestmark = pytest.mark.skipif(not os.path.isfile(REF), reason='4.2b reference script not here')


def load():
    with open(REF, 'rb') as fh:
        return fh.read().decode('utf-8').replace('\r\r\n', '\r\n').replace('\r\n', '\n')


_cache = {}


def patched():
    if 'out' not in _cache:
        _cache['out'] = T.patch_script(load())
    return _cache['out']


def func(s, name):
    m = re.search(r'\nfunction %s takes[\s\S]*?\nendfunction\n' % re.escape(name), s)
    assert m, name
    return m.group(0)


def test_patch_applies_once():
    out = patched()
    assert out.count(T.MARK) >= 1
    with pytest.raises(ValueError):
        T.patch_script(out)
    with pytest.raises(ValueError):
        T.patch_script(load().replace('\n', '\r\n'))


def test_each_function_defined_once():
    out = patched()
    for name in ('Npc_Show', 'Npc_OnClick', 'MT_Build', 'MT_Buy', 'LvAsk_Offer', 'LvAsk_OnClick', 'Mv_Sync'):
        assert len(re.findall(r'\nfunction %s takes' % name, out)) == 1, name


def test_level_up_asks_instead_of_auto_replace():
    sync = func(patched(), 'Mv_Sync')
    assert 'call LvAsk_Offer(u, m)' in sync
    assert 'Mv_WeakSlot' not in sync
    offer = func(patched(), 'LvAsk_Offer')
    assert 'LvAsk_IsHuman' in offer and 'Mv_WeakSlot' in offer  # computer players keep the old rule
    assert 'LvAsk_EnemyNear' in offer and 'Skip' in offer


def test_order_of_definitions():
    out = patched()
    pos = {n: out.index('\nfunction %s takes' % n) for n in
           ('Mv_Put', 'Mv_Known', 'LvAsk_Offer', 'LvAsk_OnClick', 'Mv_Sync', 'Ty_Has', 'PAX_Npc_ShortMove',
            'Mv_Clear', 'MT_Build', 'Npc_Show', 'Npc_OnClick', 'Mega_Init')}
    assert pos['Mv_Put'] < pos['LvAsk_Offer'] < pos['Mv_Sync']
    assert pos['Mv_Known'] < pos['LvAsk_OnClick'] < pos['Mv_Sync']
    assert pos['Ty_Has'] < pos['MT_Build'] and pos['PAX_Npc_ShortMove'] < pos['Npc_Show']
    assert pos['Mv_Clear'] < pos['Npc_OnClick'] < pos['Mega_Init']
    init = func(out, 'Mega_Init')
    assert 'function LvAsk_OnClick' in init and 'LvAsk_Dlg[i] = DialogCreate()' in init


def test_dialog_fits_12_buttons():
    show = func(patched(), 'Npc_Show')
    assert 'first + 9' in show  # 9 moves + prev + next + back = 12


def test_prices_unchanged():
    out = patched()
    assert 'constant integer Npc_LearnCost = 500' in out
    assert 'return PAX_Npc_TMCost(m)' in func(out, 'MT_CostOf')


def test_pjass(tmp_path):
    check = os.path.join(WORK, 'tools', 'v34', 'check.py')
    if not os.path.isfile(check):
        pytest.skip('pjass checker not available')
    target = tmp_path / 'war3map.j'
    target.write_text(patched().replace('\n', '\r\n'), encoding='utf-8', newline='')
    res = subprocess.run([sys.executable, '-I', check, str(target)], capture_output=True, text=True, cwd=WORK)
    assert 'pjass exit 0, 0 error lines' in (res.stdout + res.stderr), res.stdout[-2000:] + res.stderr[-2000:]
