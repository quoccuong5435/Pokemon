"""Tests for tools/v412/ability_rw.py (the approved Ability rework) on the 4.2a / 4.2b reference scripts."""
import os
import re
import shutil
import subprocess
import sys

import pytest

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))

import ability_rw as R  # noqa: E402
import hidden_ability as H  # noqa: E402
import move_ability_fix as F  # noqa: E402

REFS = [os.path.join(WORK, 'analysis', 'jass_ref', n) for n in ('_tmp_v42a_war3map.j', '_tmp_v42b_war3map.j')]
REFS = [p for p in REFS if os.path.isfile(p)]
MAP_42A = os.path.join(os.path.dirname(WORK), 'Pokemon Arena v4.2a.w3x')


def load(path, crlf=True):
    """the reference files were saved with CR CR LF; the map script itself uses CR LF"""
    with open(path, 'rb') as fh:
        s = fh.read().decode('latin-1').replace('\r\r\n', '\r\n')
    return s if crlf else s.replace('\r\n', '\n')


_cache = {}


def patched(path, crlf=True):
    key = (path, crlf)
    if key not in _cache:
        _cache[key] = R.patch(load(path, crlf))
    return _cache[key]


def test_data_matches_texts():
    assert len(R.RW_ORDER) == 105 and R.RW_MAX == 195
    assert set(R.RW_ORDER) == set(R.RW_TEXT)
    for name, text in list(R.RW_TEXT.items()) + list(R.SPECIAL_TEXT.items()):
        assert text and all(ord(c) < 128 for c in text), name  # in-game text stays English
    assert len(R.DATA['hero_default']) == 323


@pytest.mark.parametrize('path', REFS)
@pytest.mark.parametrize('crlf', [True, False])
def test_patch_applies(path, crlf):
    out = patched(path, crlf)
    assert out.count('\r\n') == (out.count('\n') if crlf else 0)
    with pytest.raises(ValueError):
        R.patch(out)


@pytest.mark.parametrize('path', REFS)
def test_every_new_ability_has_code_and_text(path):
    out = patched(path)
    code = out[out.index('// ===== v4.2x Ability rework (tools/v412/ability_rw.py), early part'):out.index('function RW_Texts')]
    for name in R.RW_ORDER:
        const = R.const_name(name)
        assert re.search(r'\b%s\b' % const, code), name + ' has no code'
        n = R.RW_INDEX[name]
        assert 'set Ab_Name[%d] = "%s"' % (n, name) in out
        assert 'call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), ' % n in out


@pytest.mark.parametrize('path', REFS)
def test_hero_defaults(path):
    out = patched(path)
    old = R._old_index(load(path))
    for hid, name in R.DATA['hero_default'].items():
        want = R.RW_INDEX.get(name, old.get(name))
        lines = re.findall(r"call SaveInteger\(Ab_HT, '%s', 0, (\d+)\)" % hid, out)
        assert lines and all(int(v) == want for v in lines), (hid, name, lines, want)


@pytest.mark.parametrize('path', REFS)
def test_hooks_and_specials(path):
    out = patched(path).replace('\r\n', '\n')
    for needle in [
        'set m = m * RW_Out(src, t, s_ab, ta, atk, skill, mt)',
        'set m = m * RW_Eff(src, t, s_ab, ta, atk, skill, mt, eff)',
        'or RW_Absorbs(t, ta, mt, dmg * m)) then',
        'set m = m * RW_In(src, t, ta, s_ab, atk, skill, mt, dmg * m)',
        'call RW_After(src, t, s_ab, ta, atk, skill, mt, dmg * m, eff)',
        'set dur = dur * RW_FxDurMult(u, kind)',
        'return 0.50 * RW_HealMult(u)',
        'set b = b + RW_MSBonus(u)',
        '+ RW_ArmorBonus(u)',
        'R2I(1000.0 * RW_ASBonus(u))',
        'set dur = RW_HardCC(t, dur, src)',
        'if RW_StatusBlock(t, kind, src) then',
        'if RW_ConfuseBlock(t) then',
        'if RW_NoPush(u) then',
        'if RW_NoSideFx(src, t) then',
        'call ExecuteFunc("RW_Init")',
        'if LoadInteger(RW_HT, GetHandleId(u), 90) > 0 then  // v4.2x: -abtest',
        'TriggerRegisterPlayerChatEvent(rwTrig, Player(rwPlayer), "-abtest", false)',
        # the 5 Abilities changed in place
        'call Ab_Aura(u, a, 700.0)',
        'call Ab_Deal(u, v, 0.03 * mx)',
        'set m = 1.6',
        'set m = 1.25',
        'if GetRandomReal(0.0, 1.0) < 0.25 then',
        'call Ab_Deal(t, src, 0.40 * d)',
    ]:
        assert needle in out, needle
    # the main part is placed before the damage trigger, the middle part before the stage code
    assert out.index('function RW_Out takes') < out.index('function Ab_OnDamaging takes')
    assert out.index('function RW_StageImmune takes') < out.index('function Fx_StageImmune takes')
    assert out.index('function RW_Ab takes') < out.index('function PAX_HealMult takes')


@pytest.mark.parametrize('path', REFS)
def test_with_the_other_modules(path):
    """build order: move_ability_fix, ability_rw, hidden_ability"""
    src = load(path)
    out = H.patch(R.patch(F.patch(src)))
    table = H.ability_table(out)
    without = sorted({n for _u, (n, num) in table.items() if not num})
    # after the rework every Hidden Ability of the roster has code; what is left belongs to forms only
    assert len(without) <= 5, without
    for uid, (name, num) in table.items():
        if name in R.RW_INDEX:
            assert num == R.RW_INDEX[name], (uid, name, num)


def test_patch_objects():
    if not os.path.isfile(MAP_42A):
        pytest.skip('4.2a map not here')
    import mpq
    import slk
    arc = mpq.MPQ(MAP_42A)
    abil = slk.Slk(arc.read('Units\\AbilityData.slk').decode('latin-1'))
    strings = arc.read('Units\\CampaignAbilityStrings.txt').decode('utf-8')
    rows = len(abil.rows)
    out = R.patch_objects(abil, strings)
    assert len(abil.rows) == rows + 105
    for name in R.RW_ORDER:
        oid = R.info_id(R.RW_INDEX[name])
        assert abil.find(oid) is not None
        assert '[%s]' % oid in out
    assert R.info_id(2) == 'AB01' and R.info_id(91) == 'AB2I'  # Ab_InfoId: base 36 of (number - 1)


@pytest.mark.skipif(not os.path.isfile(MAP_42A), reason='4.2a map not here')
def test_pjass_on_the_real_42a_script(tmp_path):
    import mpq
    pjass_check = os.path.join(WORK, 'tools', 'v34', 'check.py')
    if not os.path.isfile(pjass_check) or not shutil.which('python'):
        pytest.skip('pjass checker not available')
    script = mpq.MPQ(MAP_42A).read('scripts\\war3map.j').decode('utf-8')
    out = H.patch(R.patch(F.patch(script)))
    target = tmp_path / 'war3map.j'
    target.write_text(out, encoding='utf-8', newline='')
    res = subprocess.run([sys.executable, '-I', pjass_check, str(target)], capture_output=True, text=True, cwd=WORK)
    assert 'pjass exit 0, 0 error lines' in (res.stdout + res.stderr), res.stdout[-2000:] + res.stderr[-2000:]
