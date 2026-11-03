import mega_data
from mega_data import MEGAS

SPEC = [
    # name, base unit, stone, price, str, agi, int
    ('Mega Venusaur', 'E002', 'Venusaurite', 5000, 15, 5, 10),
    ('Mega Charizard X', 'E00E', 'Charizardite X', 5000, 20, 5, 5),
    ('Mega Charizard Y', 'E00E', 'Charizardite Y', 5000, 5, 5, 20),
    ('Mega Blastoise', 'E000', 'Blastoisinite', 5000, 10, 0, 20),
    ('Mega Beedrill', 'E02K', 'Beedrillite', 5000, 10, 20, 0),
    ('Mega Pidgeot', 'E00D', 'Pidgeotite', 5000, 0, 15, 15),
    ('Mega Alakazam', 'E00I', 'Alakazite', 5000, 0, 10, 20),
    ('Mega Gengar', 'E01G', 'Gengarite', 5000, 0, 10, 20),
    ('Mega Kangaskhan', 'E02P', 'Kangaskhanite', 5000, 15, 10, 5),
    ('Mega Pinsir', 'E03W', 'Pinsirite', 5000, 15, 10, 5),
    ('Mega Gyarados', 'E03F', 'Gyaradosite', 5000, 20, 0, 10),
    ('Mega Steelix', 'E03V', 'Steelixite', 5000, 25, 0, 5),
    ('Mega Scizor', 'E03M', 'Scizorite', 5000, 20, 5, 5),
    ('Mega Mewtwo X', 'E026', 'Mewtwonite X', 7000, 25, 5, 0),
    ('Mega Mewtwo Y', 'E026', 'Mewtwonite Y', 7000, 5, 5, 20),
    ('Mega Rayquaza', 'E029', 'Meteorite', 7000, 10, 10, 10),
    ('Mega Blaziken', 'EN02', 'Blazikenite', 6000, 20, 10, 0),
    ('Mega Sceptile', 'EN05', 'Sceptilite', 6000, 5, 15, 10),
    ('Mega Tyranitar', 'EN08', 'Tyranitarite', 6000, 20, 5, 5),
    ('Mega Gardevoir', 'EN0B', 'Gardevoirite', 6000, 0, 10, 20),
    ('Mega Gallade', 'EN0C', 'Galladite', 6000, 20, 10, 0),
    ('Mega Salamence', 'EN0F', 'Salamencite', 6000, 15, 10, 5),
    ('Mega Metagross', 'EN0I', 'Metagrossite', 6000, 20, 5, 5),
    ('Mega Lucario', 'EN0J', 'Lucarionite', 6000, 10, 10, 10),
    ('Mega Absol', 'EN0K', 'Absolite', 6000, 15, 10, 5),
]


def test_new_mega_ids_and_shop():
    assert [MEGAS[i].skin_id for i in (16, 24)] == ['hM0G', 'hM0O']
    assert [MEGAS[i].stone_id for i in (16, 24)] == ['IM0G', 'IM0O']
    assert [MEGAS[i].evolve_id for i in (16, 24)] == ['AM0G', 'AM0O']
    assert mega_data.SHOP3_ID == 'nMS3'
    assert [m.order for m in MEGAS[16:]] == ['coldarrows', 'coldarrowstarg', 'faeriefireon', 'faeriefireoff',
                                             'tankpilot', 'tankdroppilot', 'tankloadpilot', 'townbelloff', 'volcano']
    assert all(m.pkl_model for m in MEGAS[16:])


def test_sixteen_megas_in_spec_order():
    assert len(MEGAS) == 25
    for i, (m, s) in enumerate(zip(MEGAS, SPEC)):
        assert m.index == i
        assert (m.name, m.base_unit, m.stone_name, m.price) == s[:4]


def test_attribute_bonus_totals_30():
    for m, s in zip(MEGAS, SPEC):
        assert (m.str_, m.agi, m.int_) == s[4:]
        assert m.str_ + m.agi + m.int_ == 30


def test_ids_unique_and_in_ranges():
    hexd = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, m in enumerate(MEGAS):
        assert m.skin_id == 'hM0' + hexd[i]
        assert m.stone_id == 'IM0' + hexd[i]
        assert m.evolve_id == 'AM0' + hexd[i]
        assert not hasattr(m, 'attr_id')
    ids = [x for m in MEGAS for x in (m.skin_id, m.stone_id, m.evolve_id)]
    assert len(ids) == len(set(ids))
    assert len({m.order for m in MEGAS}) == len(MEGAS)
    assert len({m.key for m in MEGAS}) == len(MEGAS)


def test_constants():
    assert mega_data.DURATION == 60.0
    assert mega_data.COOLDOWN == 150.0
    assert mega_data.BONUS_IDS == ('AMB1', 'AMB2', 'AMB3')
    assert mega_data.BONUS_VALUES == {'AMB1': '10', 'AMB2': '80', 'AMB3': '0.40'}
    assert mega_data.ATTR_PCT_PER_POINT == 3
    assert mega_data.DAMAGE_BONUS == 0.5
    assert (mega_data.SHOP1_ID, mega_data.SHOP2_ID, mega_data.KID_ID) == ('nMS1', 'nMS2', 'hMK0')


def test_fallbacks_have_aura_and_tint():
    for i in (4, 13, 14, 15):
        assert MEGAS[i].pkl_model is None
        assert MEGAS[i].fx.endswith('GeneralAuraTarget.mdl')
        assert MEGAS[i].tint != (255, 255, 255)
    for i in (0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 12):
        assert MEGAS[i].pkl_model and MEGAS[i].fx == ''
