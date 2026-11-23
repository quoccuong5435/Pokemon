"""Tests for tools/v412/hidden_ability.py on the 4.2a / 4.2b reference scripts."""
import os
import re
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import hidden_ability as H  # noqa: E402
import move_ability_fix as F  # noqa: E402

REFS = [os.path.join(WORK, 'analysis', 'jass_ref', n) for n in ('_tmp_v42a_war3map.j', '_tmp_v42b_war3map.j')]


def load(path, crlf=False):
    """the reference files were saved with CR CR LF; the map script itself uses CR LF"""
    with open(path, 'rb') as fh:
        s = fh.read().decode('latin-1').replace('\r\r\n', '\r\n')
    return s if crlf else s.replace('\r\n', '\n')


@pytest.mark.parametrize('path', [p for p in REFS if os.path.isfile(p)])
@pytest.mark.parametrize('crlf', [False, True])
def test_patch(path, crlf):
    src = load(path, crlf)
    out = H.patch(src)
    eol = '\r\n' if crlf else '\n'
    assert out.count('\r\n') == (out.count('\n') if crlf else 0)  # one line ending everywhere
    table = H.ability_table(src)
    with_code = {u: n for u, (_name, n) in table.items() if n}
    # before the Ability rework 116..119 types have a coded Hidden Ability (Pressure counts once the legend
    # Pressure, which only legend code runs, wins the name); after ability_rw every roster one has code
    assert len(table) == 337 and 110 <= len(with_code) <= 119
    for uid, num in with_code.items():
        assert "call SaveInteger(AbilityPatch_HT, '%s', 3, %d)" % (uid, num) in out
    # legend-only Abilities (no code uses their constant) are not offered
    assert not any(table[u][0] in ('Regenerator', 'Drizzle') and table[u][1] for u in table)
    # the init function exists before AbilityPatch_Init and is called by it
    assert out.index('function HiddenAb_InitIdx') < out.index('function AbilityPatch_Init takes')
    assert ('    call AbilityPatch_InitPart_7()' + eol + '    call HiddenAb_InitIdx()') in out
    want = out[out.index('function Ab_Want'):]
    want = want[:want.index('endfunction')]
    assert 'LoadInteger(AbilityPatch_HT, GetUnitTypeId(u), 3)' in want
    assert want.index('AB_QUARKDRIVE') < want.index('AbilityPatch_HT')
    assert 'call Ab_Sync(u)  // v4.2x' in out
    assert 'LoadInteger(AbilityPatch_HT, h, 101)' in out[out.index('function Mega_SafeReplace'):]
    buy = out[out.index('function AbilityPatch_PromptBuy'):]
    buy = buy[:buy.index('endfunction')]
    assert 'is not available yet' in buy and 'already has its Hidden Ability' in buy
    with pytest.raises(ValueError):
        H.patch(out)


@pytest.mark.parametrize('path', [p for p in REFS if os.path.isfile(p)])
def test_works_with_move_fix(path):
    src = load(path, True)
    a = H.patch(F.patch(src))
    b = F.patch(H.patch(src))
    assert a == b
