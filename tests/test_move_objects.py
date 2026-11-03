import tempfile

import pytest

import assets
import learn_data as ld
import mpq
import objdata
import objects
import poke_data as pd
import slk
from conftest import PKL, V18


@pytest.fixture(scope='module')
def built():
    v18 = mpq.MPQ(V18)
    pkl = mpq.MPQ(PKL)
    poke = assets.collect_poke(pkl, v18)
    a = assets.collect(pkl, v18, tempfile.mkdtemp(), poke=poke)
    a.poke = poke
    a.moves = ld.build_plan(ld.hero_species(objdata.ObjFile(v18.read('war3map.w3u'))))
    names = ['war3map.w3u', 'Units\\ItemData.slk', 'Units\\ItemFunc.txt', 'Units\\AbilityData.slk',
             'Units\\CampaignAbilityStrings.txt']
    files = {n: v18.read(n) for n in names}
    return files, objects.apply(files, a), a


def _sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith('[') and line.rstrip().endswith(']'):
            cur = line.strip()[1:-1]
            out[cur] = {}
        elif cur and '=' in line:
            k, v = line.split('=', 1)
            out[cur][k] = v
    return out


def _move(a, name):
    return next(m for m in a.moves.moves if m.name == name)


def test_move_ability_ids_are_free_in_v18(built):
    files, _, a = built
    old = slk.Slk(files['Units\\AbilityData.slk'].decode('latin-1'))
    for s in range(ld.SLOTS):
        for m in a.moves.moves:
            assert old.find(ld.ability_id(s, m.index)) is None, ld.ability_id(s, m.index)


def test_every_move_has_one_single_level_ability_per_slot(built):
    _, new, a = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    for m in a.moves.moves:
        t = pd.TEMPLATES[m.template]
        for slot in range(ld.SLOTS):
            r = s.find(ld.ability_id(slot, m.index))
            assert r is not None, (m.name, slot)
            assert s.get(r, 'code') == t.code and s.get(r, 'hero') == '0' and s.get(r, 'levels') == '1'
            assert s.get(r, 'item') == '0'


def test_values_come_from_the_template_tier(built):
    _, new, a = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    blitz = _move(a, 'Flare Blitz')
    r = s.find(ld.ability_id(0, blitz.index))
    t = pd.TEMPLATES[blitz.template]
    assert blitz.template == 'BOLT' and blitz.tier == 3  # v3.3: a single-target move (the name decides the shape)
    assert float(s.get(r, 'DataA1')) == t.values['DataA'][2] == 450
    assert float(s.get(r, 'Cool1')) == t.cooldown and float(s.get(r, 'Cost1')) == t.mana[2]
    for m in a.moves.moves:
        t = pd.TEMPLATES[m.template]
        r = s.find(ld.ability_id(2, m.index))
        for stem, vals in t.values.items():
            if stem != 'Dur':
                assert float(s.get(r, stem + '1')) == vals[m.tier - 1], (m.name, stem)


def test_text_sections_place_buttons_in_row_zero(built):
    _, new, a = built
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    m = _move(a, 'Flamethrower')
    t = pd.TEMPLATES[m.template]
    for slot in range(ld.SLOTS):
        st = sec[ld.ability_id(slot, m.index)]
        assert st['Name'] == 'Flamethrower' and st['Buttonpos'] == '%d,0' % slot
        assert st['Hotkey'] == 'QWER'[slot]
        assert st['Tip'] == '|cffffcc00Flamethrower [%s]|r' % 'QWER'[slot]
        assert st['Art'] == 'ReplaceableTextures\CommandButtons\BTNPkmnFire.blp'  # type icon (fire)
        assert 'Fire' in st['Ubertip'] and 'Power 90' in st['Ubertip'] and objects.SCALE_TIP in st['Ubertip']
        if 'Missileart' in st:
            assert st['Missileart'] == pd.ELEMENT_ART['fire']


def test_row_count(built):
    files, new, a = built
    old = slk.Slk(files['Units\\AbilityData.slk'].decode('latin-1'))
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    assert len(s.rows) - len(old.rows) >= 4 * len(a.moves.moves)
