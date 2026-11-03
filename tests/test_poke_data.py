import os

import objdata
import poke_data as pd
import slk
from conftest import EXTRACTED

W3U = objdata.ObjFile(open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read())
ABIL = slk.Slk(open(os.path.join(EXTRACTED, 'Units', 'AbilityData.slk'), encoding='latin-1').read())

SPEC_FORMS = [  # id, name, template, evolves_to, level, item, kit
    ('EN00', 'Torchic', 'E003', 'EN01', 16, None, 'K1'),
    ('EN01', 'Combusken', 'E007', 'EN02', 36, None, 'K1'),
    ('EN02', 'Blaziken', 'E01C', None, None, None, 'K1'),
    ('EN03', 'Treecko', 'E008', 'EN04', 16, None, 'K2'),
    ('EN04', 'Grovyle', 'E001', 'EN05', 36, None, 'K2'),
    ('EN05', 'Sceptile', 'E002', None, None, None, 'K2'),
    ('EN06', 'Larvitar', 'E00N', 'EN07', 30, None, 'K3'),
    ('EN07', 'Pupitar', 'E00O', 'EN08', 55, None, 'K3'),
    ('EN08', 'Tyranitar', 'E00P', None, None, None, 'K3'),
    ('EN09', 'Ralts', 'E00G', 'EN0A', 20, None, 'K4'),
    ('EN0A', 'Kirlia', 'E00H', 'EN0B', 30, None, 'K4'),
    ('EN0B', 'Gardevoir', 'E00I', None, None, None, 'K4'),
    ('EN0C', 'Gallade', 'E010', None, None, None, 'K5'),
    ('EN0D', 'Bagon', 'E01S', 'EN0E', 30, None, 'K6'),
    ('EN0E', 'Shelgon', 'E01T', 'EN0F', 50, None, 'K6'),
    ('EN0F', 'Salamence', 'E01K', None, None, None, 'K6'),
    ('EN0G', 'Beldum', 'E031', 'EN0H', 20, None, 'K7'),
    ('EN0H', 'Metang', 'E032', 'EN0I', 45, None, 'K7'),
    ('EN0I', 'Metagross', 'E03V', None, None, None, 'K7'),
    ('EN0J', 'Lucario', 'E01Z', None, None, None, 'K8'),
    ('EN0K', 'Absol', 'E03I', None, None, None, 'K9'),
]


def test_forms_match_spec():
    got = [(f.id, f.name, f.template, f.evolves_to, f.level, f.kit) for f in pd.FORMS][:len(SPEC_FORMS)]  # v3.3: the first 21 are the spec; the rest are PKLegends forms
    assert got == [(a, b, c, d, e, g) for a, b, c, d, e, _f, g in SPEC_FORMS]
    assert pd.ITEM_EVOLUTIONS == [('EN0A', 'I00P', 'EN0C')]
    assert pd.STARTERS == ['EN00', 'EN03', 'EN06', 'EN09', 'EN0D', 'EN0G', 'EN0J', 'EN0K']
    assert (pd.TAVERN_ID, pd.TAVERN_TEMPLATE, pd.TAVERN_POS) == ('nTV5', 'n01H', (-128.0, 4544.0, 270.0))


def test_templates_exist_in_v18():
    for f in pd.FORMS:
        assert W3U.find(f.template) is not None, f.template
    for t in pd.TEMPLATES.values():
        assert ABIL.find(t.code) is not None, t.code


def test_ids_unused_in_v18():
    script = open(os.path.join(EXTRACTED, 'scripts', 'war3map.j'), encoding='latin-1').read()
    ids = [f.id for f in pd.FORMS] + [s.id for k in pd.KITS.values() for s in k] + [pd.TAVERN_ID]
    assert len(ids) == len(set(ids)) == len(pd.FORMS) + 45 + 1
    for i in ids:
        assert W3U.find(i) is None and ABIL.find(i) is None and "'%s'" % i not in script, i


def test_kits_have_distinct_codes():
    assert sorted(pd.KITS) == ['K%d' % i for i in range(1, 10)]
    for kit, skills in pd.KITS.items():
        assert [s.slot for s in skills] == ['Q', 'W', 'E', 'P', 'R'], kit
        codes = [pd.TEMPLATES[s.template].code for s in skills]
        assert len(set(codes)) == 5, (kit, codes)


def test_skill_ids_sequential_base36():
    ids = [s.id for k in sorted(pd.KITS) for s in pd.KITS[k]]
    assert ids[0] == 'AP00' and ids[9] == 'AP09' and ids[10] == 'AP0A' and ids[44] == 'AP18'


def test_template_numbers_match_spec():
    t = pd.TEMPLATES
    assert t['WAVE'].values['DataA'] == (150, 250, 350) and t['WAVE'].cooldown == 10
    assert t['LINE'].values['DataA'] == (175, 275, 375)
    assert t['BOLT'].values['DataA'] == (200, 325, 450) and t['BOLT'].values['Dur'] == (1, 1.25, 1.5)
    assert t['STOMP'].values['Area'] == (300, 300, 300)
    assert t['BUFF'].values['DataB'] == (0.25, 0.45, 0.65)
    assert t['CRIT'].values['DataA'] == (15, 20, 25) and t['CRIT'].values['DataB'] == (2, 2.5, 3)
    assert t['ULT_WAVE'].values['DataA'] == (450, 700, 950) and t['ULT_WAVE'].cooldown == 40
    assert t['ULT_RAIN'].values['DataA'] == (8, 10, 12) and t['ULT_RAIN'].mana == (250, 400, 550)
    assert t['ULT_STAR'].cooldown == 60
    assert pd.SLOTS['Q'] == (3, '0,2', 'Q') and pd.SLOTS['R'] == (36, '2,1', 'R') and pd.SLOTS['P'][0] == 33


def test_kit_k1_spec():
    k = pd.KITS['K1']
    assert [(s.name, s.template) for s in k] == [('Ember', 'CONE'), ('Double Kick', 'BOLT'),
                                                  ('Blaze Kick', 'STOMP'), ('Blaze', 'CRIT'),
                                                  ('Blast Burn', 'ULT_WAVE')]
    assert all(s.element == 'fire' for s in k)
