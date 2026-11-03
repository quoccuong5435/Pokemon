import os

import ability_data as ad
import objdata
from conftest import EXTRACTED
from mega_data import MEGAS

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
BY_KEY = {a.key: a for a in ad.ABILITIES}


def test_abilities_are_well_formed():
    assert len(BY_KEY) == len(ad.ABILITIES)
    for a in ad.ABILITIES:
        assert len(a.effects) <= 2 and a.text and a.icon and a.name
        for e in a.effects:
            assert e.fam in ad.FAMILY
            if e.fam in ('DEFENSE', 'SPEED'):
                assert e.raw in ad.RAW_ABILITIES
    assert [a.key for a in ad.ABILITIES if not a.effects] == ['Parental Bond']
    assert len(set(ad.FAMILY.values())) == len(ad.FAMILY)


def test_info_and_raw_ids():
    assert ad.info_id(0) == 'AB00' and ad.info_id(36) == 'AB10'
    assert ad.RAW_ABILITIES == {'AXA4': ('AIde', 4), 'AXA6': ('AIde', 6), 'AXS4': ('AIms', 40), 'AXS7': ('AIms', 70)}


def test_family_numbers_follow_the_proposal():
    blaze = BY_KEY['Blaze'].effects[0]
    assert (blaze.fam, blaze.x, blaze.y) == ('PINCH', 0.33, 0.40)
    static = BY_KEY['Static'].effects[0]
    assert (static.fam, static.x, static.y, static.z) == ('CONTACT', 0.20, 1, 1.0)
    burn, poison = BY_KEY['Flame Body'].effects[0], BY_KEY['Poison Point'].effects[0]
    assert (burn.y, burn.z, burn.w) == (2, 3.0, 0.03) and (poison.y, poison.z, poison.w) == (3, 4.0, 0.04)
    levitate, water = BY_KEY['Levitate'].effects[0], BY_KEY['Water Absorb'].effects[0]
    assert (levitate.s, levitate.x, water.s, water.x) == ('Ground', 0.0, 'Water', 0.25)
    fire = BY_KEY['Flash Fire'].effects[0]
    assert (fire.s, fire.y, fire.z) == ('Fire', 0.30, 6.0)
    assert BY_KEY['Pressure'].effects[0].x == 20 and BY_KEY['Sturdy'].effects[0].z == 90.0
    assert BY_KEY['Multiscale'].effects[0].x == 0.40 and BY_KEY['Iron Fist'].effects[0].x == 0.20
    guts = BY_KEY['Guts'].effects[0]
    assert (guts.x, guts.y, guts.z) == (0.05, 6, 5.0)
    assert BY_KEY['Chlorophyll'].effects[0].raw == 'AXS4' and BY_KEY['Shell Armor'].effects[0].raw == 'AXA4'
    bad, magnet = BY_KEY['Bad Dreams'].effects[0], BY_KEY['Magnet Pull'].effects[0]
    assert (bad.fam, bad.x, bad.y, bad.w) == ('AURA', 450, 2, 0.01) and (magnet.x, magnet.y, magnet.w) == (400, 1, 0.15)
    assert [e.fam for e in BY_KEY['Multitype'].effects] == ['MULTITYPE']
    slow = BY_KEY['Slow Start'].effects[0]
    assert (slow.x, slow.y, slow.z) == (0.40, 30.0, 0.25)


def test_every_v18_hero_gets_an_ability():
    types = ad.type_abilities(W3U)
    heroes = [o for o in W3U.custom if o.new[:1] == 'E' and o.get('upro')]
    assert len(heroes) > 100
    assert [o.get('upro') for o in heroes if o.new not in types] == []
    assert all(1 <= n <= len(ad.ABILITIES) for n in types.values())
    by_name = {o.get('upro'): types[o.new] for o in heroes}
    assert ad.ABILITIES[by_name['Charizard'] - 1].key == 'Blaze'
    assert ad.ABILITIES[by_name['Gengar'] - 1].key == 'Levitate'


def test_the_nine_new_lines_get_no_extra_ability():
    assert not {'Torchic', 'Absol', 'Lucario', 'Gardevoir'} & set(ad.species_abilities())


def test_every_mega_has_an_ability():
    mega = ad.mega_abilities()
    assert set(mega) == {m.name for m in MEGAS}
    assert BY_KEY[mega['Mega Charizard X']].name == 'Tough Claws' and BY_KEY[mega['Mega Beedrill']].name == 'Mega Adaptability'
    assert BY_KEY['Mega Adaptability'].effects[0].x == 0.30 and BY_KEY['Adaptability'].effects[0].x == 0.20
    assert [e.fam for e in BY_KEY['No Guard'].effects] == ['POWER', 'LUCKY']
    assert [e.fam for e in BY_KEY['Sand Force'].effects] == ['STURDY', 'DEFENSE']
    idx = ad.mega_ability_index()
    assert set(idx) == {m.index for m in MEGAS} and all(1 <= n <= len(ad.ABILITIES) for n in idx.values())
