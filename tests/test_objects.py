import re
import tempfile

import pytest

import assets
import mpq
import objdata
import objects
import poke_data
import skill_data
import slk
from conftest import PKL, V18
from mega_data import MEGAS


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


def test_units_added(built):
    files, new, a = built
    old = objdata.ObjFile(files['war3map.w3u'])
    f = objdata.ObjFile(new['war3map.w3u'])
    ids = {o.id for o in f.custom}
    for m in MEGAS:
        assert m.skin_id in ids
    assert {'hMK0', 'nMS1', 'nMS2'} <= ids
    assert f.find('hM01').get('umdl') == 'war3mapImported\\Mega\\MegaCharizardX.mdl'
    assert f.find('hM01').get('uico') == 'ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp'
    assert f.find('hM01').get('usca') == pytest.approx(a.scale[1])
    assert f.find('nMS1').get('usei') == 'IM00,IM01,IM02,IM03,IM04,IM05,IM06,IM07'
    assert f.find('nMS2').get('usei') == 'IM08,IM09,IM0A,IM0B,IM0C,IM0D,IM0E,IM0F'
    assert f.find('nMS1').get('unam') == 'Mega Shop I'
    assert f.find('hMK0').get('uabi') == 'Aloc,Avul'
    assert f.find('hMK0').get('umdl') == a.kid_model
    assert len(f.original) == len(old.original)
    n_old = len(old.custom)
    assert [o.id for o in f.custom[:n_old]] == [o.id for o in old.custom]
    reskilled = set(skill_data.hero_types())  # v3.0: their skills (uhab) change on purpose
    def _mods(o):  # v3.3: dangling ability references are dropped on purpose
        return repr([(m.field, m.value) if m.field != 'uabi' else ('uabi', ','.join(
            x for x in str(m.value).split(',') if x not in objects.DANGLING_ABILITIES)) for m in o.mods])
    assert [(o.id, _mods(o)) for o in f.custom[:n_old] if o.id not in set(LEGENDS) | reskilled | {'n030'}] == \
        [(o.id, _mods(o)) for o in old.custom if o.id not in set(LEGENDS) | reskilled | {'n030'}]
    assert len(f.custom) == n_old + 25 + 1 + 3 + 30 + len(poke_data.FORMS) + 1 + 1  # Celebi hero; skins, kid, 3 shops, wild, heroes, tavern


def test_skins_clone_base_unit_art(built):
    files, new, a = built
    old = objdata.ObjFile(files['war3map.w3u'])
    f = objdata.ObjFile(new['war3map.w3u'])
    for m in MEGAS:
        base, skin = (old.find(m.base_unit) or f.find(m.base_unit)), f.find(m.skin_id)
        assert skin.orig == base.orig
        for field in ('ua1m', 'usnd', 'uspa', 'ua1t', 'umvs', 'upro'):
            assert skin.get(field) == base.get(field), (m.key, field)
        assert skin.get('umdl') == a.model_path[m.index]


def test_items_rows_and_strings(built):
    _, new, _ = built
    s = slk.Slk(new['Units\\ItemData.slk'].decode('latin-1'))
    assert s.get(s.find('IM0D'), 'goldcost') == '7000'
    assert s.get(s.find('IM00'), 'goldcost') == '5000'
    assert s.get(s.find('IM00'), 'class') == 'Permanent'
    assert s.get(s.find('IM00'), 'abilList') == ''  # v3.3: the Mega button is on the Pokemon's card, not the stone
    assert s.get(s.find('IM00'), 'pickRandom') == '0'
    sec = _sections(new['Units\\ItemFunc.txt'].decode('utf-8'))
    assert sec['IM01']['Name'] == 'Charizardite X'
    assert sec['IM01']['Art'] == 'ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp'
    assert sec['IM09']['Buttonpos'] == '1,0'
    assert sec['IM0G']['Buttonpos'] == '0,0' and sec['IM0O']['Buttonpos'] == '0,2'
    assert '+60% STR' in sec['IM01']['Ubertip'] and '+50% damage' in sec['IM01']['Ubertip']
    assert 'I012' in sec  # old sections kept


def test_abilities_rows(built):
    _, new, _ = built
    s = slk.Slk(new['Units\\AbilityData.slk'].decode('latin-1'))
    r = s.find('AM00')
    assert s.get(r, 'code') == 'ANcl'
    assert s.get(r, 'Cool1') == '150'
    assert s.get(r, 'DataF1') == MEGAS[0].order
    assert s.find('AMA1') is None
    assert s.get(s.find('AMB1'), 'DataA1') == '10'
    assert s.get(s.find('AMB2'), 'DataA1') == '80'
    assert s.get(s.find('AMB3'), 'DataA1') == '0.40'
    sec = _sections(new['Units\\CampaignAbilityStrings.txt'].decode('utf-8'))
    assert sec['AM01']['Art'] == 'ReplaceableTextures\\CommandButtons\\BTNMegaCharizardX.blp'
    assert (sec['AM01']['Buttonpos'], sec['AM01']['Hotkey']) == ('1,1', 'D')
    assert (sec['AM02']['Buttonpos'], sec['AM02']['Hotkey']) == ('0,1', 'F')
    assert 'A01Z' in sec


def test_mega_evolve_orders_unique(built):
    files, _, _ = built
    s = slk.Slk(files['Units\\AbilityData.slk'].decode('latin-1'))
    used = set()
    for r in s.rows:
        for lv in '1234':
            v = s.get(r, 'DataF' + lv)
            if v:
                used.add(v.lower())
    text = files['Units\\CampaignAbilityStrings.txt'].decode('utf-8', 'replace')
    used |= {m.group(1).lower() for m in re.finditer(r'^Order(?:on|off)?=(\w+)', text, re.M)}
    orders = [m.order for m in MEGAS]
    assert len(set(orders)) == len(MEGAS)
    assert not (set(orders) & used)


LEGENDS = ('n001', 'n00C', 'n00D', 'n00F', 'n00G', 'n01I', 'n01J', 'n01K', 'n01L', 'n01M', 'n037', 'n01N',
           'n01O', 'n033', 'n034', 'n035')


def test_wild_units(built):
    import wild_data
    files, new, a = built
    f = objdata.ObjFile(new['war3map.w3u'])
    for s in wild_data.SPECIES:
        o = f.find(s.id)
        assert o is not None, s.id
        assert o.orig == f.find('n00T').orig
        assert (o.get('unam'), o.get('ulev'), o.get('uhpm'), o.get('ua1b'), o.get('udef'), o.get('ubba')) ==             (s.name, s.level, s.hp, s.dmg, s.armor, s.gold)
        assert o.get('umdl') == a.wild.model_path[s.index]
        assert o.get('uico') == a.wild.icon_path[s.index]
        assert o.get('ua1w') == 'normal' and o.get('ua1r') == 100
        assert o.get('usca') == pytest.approx(a.wild.scale[s.index])


def test_legends_level_100(built):
    files, new, _ = built
    old = objdata.ObjFile(files['war3map.w3u'])
    f = objdata.ObjFile(new['war3map.w3u'])
    for lid in LEGENDS:
        o, b = f.find(lid), old.find(lid)
        assert o.get('ulev') == 100, lid
        assert o.get('uhpm') == int(round(b.get('uhpm') * objects.LEGEND_HP_MULT))  # v3.3: x1.25
        assert o.get('ua1b') == int(round(b.get('ua1b') * objects.LEGEND_DMG_MULT))  # v3.3: x2.0
        assert o.get('udef') == int(round(min(b.get('udef') or 0, 35) * objects.LEGEND_ARMOR_MULT))  # v3.3: x2.5
    for gym in ('n00R', 'n01E', 'n02H', 'n004'):
        assert repr(f.find(gym).mods) == repr(old.find(gym).mods)
