"""v4.1.2-ver2 Dynamax (tools/v412/dynamax.py), checked on the real v4.1.2 script."""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import dynamax  # noqa: E402
import mpq  # noqa: E402

MAP = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.1.2.w3x')
pytestmark = pytest.mark.skipif(not os.path.exists(MAP), reason='v4.1.2 map not on this PC')


@pytest.fixture(scope='module')
def patched():
    s = mpq.MPQ(MAP).read('scripts\\war3map.j').decode('latin-1').replace('\r\r\n', '\r\n').replace('\r\n', '\n')
    return dynamax.patch_script(s)


def fn(s, name):
    m = re.search(r'(?ms)^function %s takes.*?^endfunction\n' % name, s)
    assert m, name
    return m.group(0)


def test_globals_and_functions_come_before_use(patched):
    assert patched.index("constant integer Fx_DynaAbil = 'ADMX'") < patched.index('endglobals')
    for n in ('Fx_IsDyna', 'Fx_DynaEnd', 'Fx_DynaCast'):
        assert patched.index('function %s takes' % n) < patched.index('function Fx_Tick takes')
    assert patched.index('function Fx_IsDyna takes') < patched.index('function PkFx_OnCast takes')
    assert patched.index('function Fx_DynaCast takes') < patched.index('function Dyna_Data takes') < patched.index('function Fx_Init takes')


def test_hooks(patched):
    assert 'set mult = mult * Fx_DynaDmg' in fn(patched, 'Fx_OutMult')
    assert 'call Fx_DynaEnd(u)' in fn(patched, 'Fx_Tick')
    assert 'Fx_MaxFx[Mv_Type[fxStep]]' in fn(patched, 'PkFx_OnCast')
    assert 'call ExecuteFunc("Dyna_Data")' in fn(patched, 'Fx_Init')
    d = fn(patched, 'Dyna_Data')
    assert d.count('set Fx_MaxFx[') == 18 and d.count('set Fx_MaxScale[') == 18
    assert 'function Fx_DynaCast))' in d


def test_missing_anchor_raises():
    with pytest.raises(ValueError):
        dynamax.patch_script('globals\nendglobals\n')
