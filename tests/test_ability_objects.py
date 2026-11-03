import tempfile

import pytest

import assets
import mpq
import objects
import poke_data as pd
import slk
from ability_data import ABILITIES, RAW_ABILITIES, info_id
from conftest import PKL, V18


@pytest.fixture(scope='module')
def built():
    v18 = mpq.MPQ(V18)
    pkl = mpq.MPQ(PKL)
    poke = assets.collect_poke(pkl, v18)
    a = assets.collect(pkl, v18, tempfile.mkdtemp(), poke=poke)
    a.poke = poke
    a.abilities = ABILITIES
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


def test_info_ids_are_free_in_v18(built):
    files, _, _ = built
    old = slk.Slk(files['Units\\AbilityData.slk'].decode('latin-1'))
    for i in range(len(ABILITIES)):
        assert old.find(info_id(i)) is None, info_id(i)
    for raw in RAW_ABILITIES:
        assert old.find(raw) is None, raw


def test_info_rows_are_passive_and_data_only(built):
    _, new, _ = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    for i, ab in enumerate(ABILITIES):
        r = s.find(info_id(i))
        assert r is not None, info_id(i)
        assert s.get(r, 'code') == 'AEev'
        assert s.get(r, 'hero') == '0'
        assert s.get(r, 'DataA1') == '0'


def test_info_text_sections(built):
    _, new, _ = built
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    for i, ab in enumerate(ABILITIES):
        st = sec[info_id(i)]
        assert st['Name'] == 'Ability: %s' % ab.name
        assert st['Buttonpos'] == '3,1'
        assert st['Ubertip'] == ab.text
        assert st['Art'] == ab.icon


def test_bonus_rows(built):
    _, new, _ = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    for raw, (code, value) in RAW_ABILITIES.items():
        r = s.find(raw)
        assert r is not None, raw
        assert s.get(r, 'code') == code
        assert float(s.get(r, 'DataA1')) == value
        assert s.get(r, 'item') == '1'
        assert sec[raw]['Name'] == 'Ability Bonus'


def test_skill_tooltip_scaling_line(built):
    _, new, _ = built
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    for kit in pd.KITS.values():
        for sk in kit:
            ub = sec[sk.id]['Ubertip']
            if sk.template in objects._NO_SCALE:
                assert objects.SCALE_TIP not in ub, sk.id
            else:
                assert ub.count(objects.SCALE_TIP) == 3, sk.id
                assert ub.count('"') == 6, sk.id
