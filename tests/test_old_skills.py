import tempfile

import pytest

import assets
import mpq
import objdata
import objects
import poke_data as pd
import skill_data as sd
import slk
from conftest import PKL, V18


@pytest.fixture(scope='module')
def built():
    v18 = mpq.MPQ(V18)
    pkl = mpq.MPQ(PKL)
    poke = assets.collect_poke(pkl, v18)
    a = assets.collect(pkl, v18, tempfile.mkdtemp(), poke=poke)
    a.poke = poke
    a.abilities = __import__('ability_data').ABILITIES
    names = ['war3map.w3u', 'Units\ItemData.slk', 'Units\ItemFunc.txt', 'Units\AbilityData.slk',
             'Units\CampaignAbilityStrings.txt']
    files = {n: v18.read(n) for n in names}
    return files, objects.apply(files, a)


def test_every_v18_pokemon_is_in_exactly_one_type():
    v18 = mpq.MPQ(V18)
    w3u = objdata.ObjFile(v18.read('war3map.w3u'))
    heroes = {o.new for o in w3u.custom if o.new[:1] == 'E' and o.get('upro')}
    assert len(heroes) == 117
    listed = [h for ids in sd.HERO_TYPE.values() for h in ids]
    assert len(listed) == len(set(listed)) == 117 and set(listed) == heroes


def test_kits_have_five_distinct_skills_and_no_id_clash(built):
    files, _ = built
    old = slk.Slk(files['Units\AbilityData.slk'].decode('latin-1'))
    ids = [sk.id for t in sd.HERO_TYPE for sk in sd.kit_for_type(t)]
    for t in sd.HERO_TYPE:
        kit = sd.kit_for_type(t)
        assert len(kit) == 5 and [sk.slot for sk in kit] == ['Q', 'W', 'E', 'P', 'R'], t
    new_ids = {sk.id for sk in sd.new_skills()}
    assert len(new_ids) == 55
    for i in new_ids:
        assert old.find(i) is None, i
    assert set(ids) <= new_ids | {sk.id for k in pd.KITS.values() for sk in k}


def test_hero_uhab_is_its_kit(built):
    _, new = built
    f = objdata.ObjFile(new['war3map.w3u'])
    for t, ids in sd.HERO_TYPE.items():
        want = ','.join(sk.id for sk in sd.kit_for_type(t))
        for h in ids:
            assert f.find(h).get('uhab') == '', h  # v3.2: no fixed kit; want is the old kit


def test_new_skill_rows_and_text(built):
    _, new = built
    s = slk.Slk(new['Units\AbilityData.slk'].decode('latin-1'))
    for sk in sd.new_skills():
        assert s.find(sk.id) is not None, sk.id
        assert s.get(s.find(sk.id), 'code') == pd.TEMPLATES[sk.template].code
    txt = new['Units\CampaignAbilityStrings.txt'].decode('utf-8')
    assert '[AQ00]' in txt and 'Name=Water Pulse' in txt


def test_v18_abilities_removed_from_heroes(built):
    files, new = built  # v3.3: the v1.8 abilities (e.g. A00X) are gone; only the inventory ability stays
    f = objdata.ObjFile(new['war3map.w3u'])
    for t, ids in sd.HERO_TYPE.items():
        for h in ids:
            want = 'AInv,' + objects.TELE_ABILITY if h in objects.TELE_UNITS else 'AInv'
            assert f.find(h).get('uabi') == want, h
