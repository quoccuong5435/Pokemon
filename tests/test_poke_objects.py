import tempfile

import pytest

import assets
import mpq
import objdata
import objects
import poke_data as pd
import slk
from conftest import PKL, V18
from mega_data import MEGAS, SHOP3_ID


@pytest.fixture(scope='module')
def built():
    v18 = mpq.MPQ(V18)
    pkl = mpq.MPQ(PKL)
    poke = assets.collect_poke(pkl, v18)
    a = assets.collect(pkl, v18, tempfile.mkdtemp(), poke=poke)
    a.wild = assets.collect_wild(pkl, v18)
    a.poke = poke
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


def test_new_heroes(built):
    files, new, a = built
    old = objdata.ObjFile(files['war3map.w3u'])
    f = objdata.ObjFile(new['war3map.w3u'])
    for form in pd.FORMS:
        o, t = f.find(form.id), old.find(form.template)
        assert o is not None, form.id
        assert o.orig == t.orig
        assert o.get('upro') == form.name
        assert o.get('uhab') == ''  # v3.2: moves come from the + system
        assert o.get('uabi') == 'AInv'
        assert o.get('umdl') == a.poke.model_path[form.id]
        assert o.get('uico') == a.poke.icon_path[form.id]
        assert o.get('usca') == pytest.approx(a.poke.scale[form.id])
        assert form.name in o.get('utip') and form.name in o.get('uawt')
        for field in ('ua1t', 'udty', 'ustr', 'umvs'):
            assert o.get(field) == t.get(field), (form.id, field)
        assert o.get('uhpm') == round(t.get('uhpm') * objects.HERO_HP_MULT), form.id  # v3.3 playable HP x2
    starters = [f.find(i) for i in pd.STARTERS]
    assert [(o.get('ubpx'), o.get('ubpy')) for o in starters] == [(i % 4, i // 4) for i in range(8)]
    assert [o.get('uhot') for o in starters] == list(pd.TAVERN_HOTKEYS)


def test_new_skill_rows(built):
    _, new, _ = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    for kit in pd.KITS.values():
        for sk in kit:
            t = pd.TEMPLATES[sk.template]
            r = s.find(sk.id)
            assert r is not None, sk.id
            assert s.get(r, 'code') == t.code
            assert (s.get(r, 'hero'), s.get(r, 'levels'), s.get(r, 'levelSkip')) == ('1', '3', '10')
            assert s.get(r, 'reqLevel') == str(pd.SLOTS[sk.slot][0])
            for stem, vals in t.values.items():
                cols = ['Dur', 'HeroDur'] if stem == 'Dur' else [stem]
                for c in cols:
                    for lv in (1, 2, 3):
                        assert float(s.get(r, '%s%d' % (c, lv))) == pytest.approx(vals[lv - 1]), (sk.id, c, lv)
            if t.cooldown:
                assert [float(s.get(r, 'Cool%d' % lv)) for lv in (1, 2, 3)] == [t.cooldown] * 3
                assert [float(s.get(r, 'Cost%d' % lv)) for lv in (1, 2, 3)] == list(t.mana)
            st = sec[sk.id]
            assert st['Name'] == sk.name
            assert st['Buttonpos'] == pd.SLOTS[sk.slot][1]
            assert st['Tip'].count('Level') == 3 and sk.name in st['Tip']
            assert st['Ubertip'].count('"') == 6
            if 'Missileart' in st and sk.template not in ('ULT_RAIN', 'ULT_STAR'):
                assert st['Missileart'] == pd.ELEMENT_ART[sk.element]


def test_tavern_and_shop3(built):
    _, new, _ = built
    f = objdata.ObjFile(new['war3map.w3u'])
    tav = f.find(pd.TAVERN_ID)
    assert tav.orig == f.find(pd.TAVERN_TEMPLATE).orig
    assert tav.get('useu') == '' and tav.get('unam') == pd.TAVERN_NAME
    shop = f.find(SHOP3_ID)
    assert shop.get('usei') == ','.join(m.stone_id for m in MEGAS[16:])


def test_new_mega_skins_clone_new_heroes(built):
    _, new, a = built
    f = objdata.ObjFile(new['war3map.w3u'])
    for m in MEGAS[16:]:
        skin, base = f.find(m.skin_id), f.find(m.base_unit)
        assert skin.orig == base.orig and skin.get('ua1t') == base.get('ua1t')
        assert skin.get('umdl') == a.model_path[m.index]
