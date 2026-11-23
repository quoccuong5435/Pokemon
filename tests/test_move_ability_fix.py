"""Tests for tools/v412/move_ability_fix.py on the 4.2a / 4.2b reference scripts."""
import os
import re
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import move_ability_fix as F  # noqa: E402

REFS = [os.path.join(WORK, 'analysis', 'jass_ref', n) for n in ('_tmp_v42a_war3map.j', '_tmp_v42b_war3map.j')]


def load(path, crlf=False):
    """the reference files were saved with CR CR LF; the map script itself uses CR LF"""
    with open(path, 'rb') as fh:
        s = fh.read().decode('latin-1').replace('\r\r\n', '\r\n')
    return s if crlf else s.replace('\r\n', '\n')


def record(s, idx):
    return {int(m.group(1)): int(m.group(2))
            for m in re.finditer(r'call SaveInteger\(Fx_HT, %d, (\d+), (-?\d+)\)' % (100000 + idx), s)}


@pytest.mark.parametrize('path', [p for p in REFS if os.path.isfile(p)])
@pytest.mark.parametrize('crlf', [False, True])
def test_patch(path, crlf):
    src = load(path, crlf)
    out = F.patch(src)
    # every move record is the new one, other moves untouched
    for idx, (_label, _old, new, _ot, new_txt) in F.MOVES.items():
        assert record(out, idx) == new
        if new_txt:
            assert ('set Mv_Text[%d] = "' % idx) in out and ('Effect:|r ' + new_txt + '"') in out
    assert record(out, 0) == record(src, 0)
    # the confusion roll sits right before the flinch roll, with the file's line ending
    eol = '\r\n' if crlf else '\n'
    block = eol.join(F.CONFUSE_LINES) + eol + F.FLINCH_ANCHOR
    assert out.count(block) == 1
    assert 'set Mv_Type[319] = 12' in out
    index = F._ability_index(out)
    for hid, (_n, _old, new_name) in F.ABILITIES.items():
        assert "call SaveInteger(Ab_HT, '%s', 0, %d)" % (hid, index[new_name]) in out
    # only the intended lines changed: 4 new lines, same line count otherwise for records
    assert out.count('\r\n') == (out.count('\n') if crlf else 0)
    with pytest.raises(ValueError):
        F.patch(out)  # a second run is refused


def test_tooltips_say_what_the_data_does():
    for idx, (_label, _old, new, old_txt, new_txt) in F.MOVES.items():
        txt = new_txt or old_txt
        if 9 in new:
            assert '%d%% confusion' % new[9] in txt
        if 4 in new:
            assert '%d%% ' % new[5] in txt
        if 'No extra effect' in txt:
            assert new.get(1, 0) & 4096
