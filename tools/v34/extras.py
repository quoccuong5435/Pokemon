"""v3.4 extras (docs/v3.4/3-item-league-tinh-nang.md, approved 2026-11-07 and folded into v3.4.0):
battle / utility items and two shops, stone evolutions, data for wild creeps that evolve with the tier and elites
that Mega Evolve, the Elite Four. Called from content.make(); the JASS lives in jass/extra.j, extra_late.j, gym.j.
"""
import re

BTN = 'ReplaceableTextures\\CommandButtons\\BTN%s.blp'

# index k (Ab_HT key 140 + k on the holder, Mega_HT key 91 = k + 1 on the item type), id, name, price, kind, icon, text
ITEMS = [
    ('IB00', 'Life Orb', 4000, 'battle', 'OrbOfDarkness',
     'Attacks and moves deal +30% damage; each hit costs 1% max HP (not below 20% HP).'),
    ('IB01', 'Choice Band', 4000, 'battle', 'GauntletsOfOgrePower', 'Attacks deal +35% damage. -10% move speed.'),
    ('IB02', 'Choice Specs', 4000, 'battle', 'MantleOfIntelligence', 'Moves deal +35% damage. -10% move speed.'),
    ('IB03', 'Choice Scarf', 4000, 'battle', 'BootsOfSpeed', '+30% move speed and +20% attack speed.'),
    ('IB04', 'Leftovers', 3500, 'battle', 'Cheese', 'Regenerates 1% max HP per second.'),
    ('IB05', 'Focus Sash', 5000, 'battle', 'Ankh',
     'A hit that would knock it out while above 50% HP leaves it at 1 HP (once every 60s).'),
    ('IB06', 'Expert Belt', 3500, 'battle', 'Belt', 'Super effective moves deal +25% damage.'),
    ('IB07', 'Rocky Helmet', 3500, 'battle', 'HelmutPurple', 'Melee attackers lose 3% of their max HP per hit.'),
    ('IB08', 'Assault Vest', 4000, 'battle', 'ArcaniteArmor', 'Takes 25% less damage from moves.'),
    ('IB09', 'Scope Lens', 3500, 'battle', 'CrystalBall', '15% chance for attacks to deal x1.5 damage.'),
    ('IB0A', "King's Rock", 3000, 'battle', 'Circlet', 'Attacks have a 10% chance to stun for 1s.'),
    ('IB0B', 'Eviolite', 3000, 'battle', 'EnchantedGemstone',
     'A Pokemon that can still evolve takes 20% less damage.'),
    ('IT00', 'Lucky Egg', 3000, 'util', 'PhilosophersStone', '+50% experience.'),
    ('IT01', 'Amulet Coin', 3000, 'util', 'Amulet', '+50% gold from the units it kills.'),
    ('IT02', 'Everstone', 500, 'util', 'Pebble',
     'Its holder does not evolve when it levels up (it evolves at the next level up after the stone is gone).'),
    ('IT03', 'Sitrus Berry', 150, 'berry', 'HealingSalve', 'Used up when HP drops below 50%: heals 25% max HP.'),
    ('IT04', 'Lum Berry', 150, 'berry', 'PotionGreenSmall', 'Used up when it is stunned, slowed or poisoned: cures it.'),
    ('IT05', 'Escape Rope', 200, 'rope', 'ScrollOfTownPortal',
     'Use: back to your base after 3s (not during a gym or League battle).'),
    ('IT06', 'Mega Ring', 8000, 'util', 'GoldRing', 'Mega Evolution lasts 90s instead of 60s; Mega Stones recharge 30% faster.'),
    ('IT07', 'Ice Stone', 1250, 'stone', 'IceShard', 'Evolution stone: Eevee -> Glaceon.'),
    ('IT08', 'Shiny Stone', 1250, 'stone', 'SoulGem', 'Evolution stone: Eevee -> Sylveon, Togetic -> Togekiss.'),
]
BATTLE_LIMIT_KIND = 3   # Mega_HT key 90 of the item type (Item_OnPickup: at most 3 battle items)
ROPE_ABILITY = 'AXR0'
ROPE_ORDER = 'spirittroll'
SHOPS = [('nBS0', 'Battle Shop', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
         ('nIS0', 'Item Shop', [12, 13, 14, 15, 16, 17, 18, 19, 20])]
SHOP_TEMPLATE = 'n00Q'

STONES = {'Fire': 'Fire Stone', 'Water': 'Water Stone', 'Thunder': 'Thunder Stone', 'Leaf': 'Leaf Stone',
          'Moon': 'Moon Stone', 'Sun': 'Sun Stone', 'Ice': 'Ice Stone', 'Shiny': 'Shiny Stone'}
STONE_EVOS = [
    ('Eevee', 'Fire', 'Flareon'), ('Eevee', 'Water', 'Vaporeon'), ('Eevee', 'Thunder', 'Jolteon'),
    ('Eevee', 'Leaf', 'Leafeon'), ('Eevee', 'Sun', 'Espeon'), ('Eevee', 'Moon', 'Umbreon'),
    ('Eevee', 'Ice', 'Glaceon'), ('Eevee', 'Shiny', 'Sylveon'),
    ('Vulpix', 'Fire', 'Ninetales'), ('Growlithe', 'Fire', 'Arcanine'), ('Staryu', 'Water', 'Starmie'),
    ('Shellder', 'Water', 'Cloyster'), ('Poliwhirl', 'Water', 'Poliwrath'), ('Lombre', 'Water', 'Ludicolo'),
    ('Pikachu', 'Thunder', 'Raichu'), ('Exeggcute', 'Leaf', 'Exeggutor'), ('Weepinbell', 'Leaf', 'Victreebel'),
    ('Gloom', 'Leaf', 'Vileplume'), ('Gloom', 'Sun', 'Bellossom'), ('Clefairy', 'Moon', 'Clefable'),
    ('Jigglypuff', 'Moon', 'Wigglytuff'), ('Nidorino', 'Moon', 'Nidoking'), ('Nidorina', 'Moon', 'Nidoqueen'),
    ('Togetic', 'Shiny', 'Togekiss'),
]

LEAGUE = [('Will', 'Psychic'), ('Koga', 'Poison'), ('Bruno', 'Fighting'), ('Karen', 'Dark'), ('Lance', 'Dragon')]
CHAMPION_TEAM = ['Dragonite', 'Charizard', 'Gyarados', 'Salamence', 'Ampharos', 'Altaria']


def _q(s):
    return '"%s"' % s


def _jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _item_names(base):
    text = base.read('Units\\ItemFunc.txt').decode('utf-8', 'replace')
    return dict((name.strip(), sid) for sid, name in re.findall(r'\[(\w{4})\]\r?\n(?:[^\[]*?\n)?Name=([^\r\n]*)', text))


def _v18_stone_evos(script):
    """(from unit, item) pairs the v1.8 pickup triggers already evolve"""
    items = {}
    for m in re.finditer(r'(?m)^function (\w+) takes nothing returns boolean\n(.*?)\nendfunction', script, re.S):
        it = re.findall(r"GetItemTypeId\(GetManipulatedItem\(\)\)=='(\w{4})'", m.group(2))
        ty = re.findall(r"GetUnitTypeId\(GetManipulatingUnit\(\)\)=='(\w{4})'", m.group(2))
        items[m.group(1)] = (it, ty)
    pairs = set()
    for trig, cond, act in re.findall(r"call TriggerAddCondition\((\w+),Condition\(function (\w+)\)\)\n"
                                      r"call TriggerAddAction\(\1,function (\w+)\)", script):
        its = items.get(cond, ([], []))[0]
        if not its:
            continue
        body = re.search(r'(?ms)^function %s takes nothing returns nothing\n(.*?)\nendfunction' % act, script)
        for cf in re.findall(r'if\((\w+)\(\)\)then', body.group(1) if body else ''):
            for ty in items.get(cf, ([], []))[1]:
                for it in its:
                    pairs.add((ty, it))
    return pairs


def add(c, script, units, allu, ids, by_name, base):
    import apply as A
    import objdata
    from content import clone, setf
    T_STRING = objdata.T_STRING
    # ---------------- items, their rows and texts
    names = _item_names(base)
    for k, (iid, name, price, kind, icon, text) in enumerate(ITEMS):
        vals = {'class': _q('Permanent'), 'abilList': None, 'cooldownID': None, 'usable': '0', 'goldcost': str(price),
                'stockMax': '3', 'stockRegen': '1', 'stockStart': '0', 'uses': '0', 'perishable': '0'}
        if kind == 'rope':
            vals.update({'class': _q('Charged'), 'abilList': _q(ROPE_ABILITY), 'cooldownID': _q(ROPE_ABILITY),
                         'usable': '1', 'uses': '1', 'perishable': '1'})
        tmpl = names.get('Fire Stone', 'IM00') if kind == 'stone' else 'IM00'
        if kind == 'stone':
            vals = {'goldcost': str(price)}
        c.item_rows.append((tmpl, iid, vals))
        shop_slot = next(sl.index(k) for _sid, _n, sl in SHOPS if k in sl)
        c.item_txt.append((iid, [('Name', name), ('Tip', 'Purchase |cffffcc00%s|r' % name), ('Ubertip', text),
                                 ('Description', text), ('Art', BTN % icon),
                                 ('Buttonpos', '%d,%d' % (shop_slot % 4, shop_slot // 4))]))
        c.data += ["    set Itm_Id[%d] = '%s'" % (k, iid), "    call SaveInteger(Mega_HT, '%s', 91, %d)" % (iid, k + 1)]
        if kind == 'battle':
            c.data.append("    call SaveInteger(Mega_HT, '%s', 90, %d)" % (iid, BATTLE_LIMIT_KIND))
    ix = {name: ITEMS[k][0] for k, (_i, name, _p, _kd, _ic, _t) in enumerate(ITEMS)}
    c.data += ['    set Itm_N = %d' % len(ITEMS), "    set Itm_Everstone = '%s'" % ix['Everstone'],
               "    set Itm_MegaRing = '%s'" % ix['Mega Ring'], "    set Itm_Rope = '%s'" % ix['Escape Rope']]
    c.abil_rows.append(('AM00', ROPE_ABILITY, {'DataF1': _q(ROPE_ORDER), 'Cool1': '0'}))
    c.abil_txt.append((ROPE_ABILITY, [('Name', 'Escape Rope'), ('Art', BTN % 'ScrollOfTownPortal'), ('Buttonpos', '0,0'),
                                      ('Order', ROPE_ORDER), ('Tip', 'Escape Rope'),
                                      ('Ubertip', 'Back to your base after 3s.')]))
    for sid, sname, slots in SHOPS:
        o = clone(units[SHOP_TEMPLATE], sid)
        setf(o, 'unam', sname, T_STRING)
        setf(o, 'usei', ','.join(ITEMS[k][0] for k in slots), T_STRING)
        c.objs.append(o)
    c.data += ["    set Ext_Shop[0] = 'nBS0'", "    set Ext_Shop[1] = 'nIS0'"]
    # v3.4.2: the shop rows of a base (y = +-544: Poke Mart / Super Marts, Mega Shops) are full and the first spots
    # of v3.4.0 sat on Mega Shop III / Haunt Legendary: the free band between the rows, either side of the walkway
    # from the Poke Center to the door (checked walkable in war3map.wpm, analysis/base_layout.py)
    spots = [(-5696, 288), (-5696, -288), (-5392, 288), (-5392, -288), (-5904, 288), (-5904, -288)]
    for i, (x, y) in enumerate(spots):
        c.data += ['    set Ext_SpotX[%d] = %s' % (i, repr(float(-x))), '    set Ext_SpotY[%d] = %s' % (i, repr(float(y)))]
    c.data.append('    set Ext_SpotN = %d' % len(spots))
    c.report.append('items: %d new (%s), shops nBS0 Battle Shop, nIS0 Item Shop' % (len(ITEMS), ', '.join(ix)))

    # ---------------- stone evolutions (Evo_Item*), skipping the ones v1.8 already does
    stone_id = {k: (names.get(v) or ix.get(v)) for k, v in STONES.items()}
    have = _v18_stone_evos(script)
    n = int(re.search(r'set Evo_ItemN = (\d+)', script).group(1))
    added = []
    for fr, st, to in STONE_EVOS:
        if fr not in ids or to not in ids or not stone_id.get(st):
            continue
        for fid in ids[fr]:
            if (fid, stone_id[st]) in have:
                continue
            c.data += ["    set Evo_ItemFrom[%d] = '%s'" % (n, fid), "    set Evo_Item[%d] = '%s'" % (n, stone_id[st]),
                       "    set Evo_ItemTo[%d] = '%s'" % (n, ids[to][0])]
            n += 1
            added.append('%s+%s' % (fr, st))
    c.data.append('    set Evo_ItemN = %d' % n)
    c.report.append('stone evolutions: %d added (%s); v1.8 already had %d' % (len(added), ', '.join(added), len(have)))

    # ---------------- wild creeps: next form for the tier (keys 45/47/48), elite Mega (key 41)
    report = []
    _out, edges, ids2, _names = A.gym_evolutions(script, allu, report)
    norm = {A._norm(sp): sp for sp in ids2}
    wild = {}   # type -> [species, pmin, pmax]
    pool = dict((int(i), t) for i, t in re.findall(r"set Wild_Pool\[(\d+)\] = '(\w{4})'", script))
    pw = dict((int(i), int(p)) for i, p in re.findall(r"set Wild_PoolPow\[(\d+)\] = (\d+)", script))
    for i, t in pool.items():
        o = allu.get(t)
        nm = ((o.get('unam') if o else '') or '')
        nm = nm[5:] if nm.startswith('Wild ') else nm
        sp = norm.get(A._norm(nm))
        if not sp:
            continue
        w = wild.setdefault(t, [sp, pw.get(i, 1), pw.get(i, 1)])
        w[1], w[2] = min(w[1], pw.get(i, 1)), max(w[2], pw.get(i, 1))
    for r in c.wild:
        wild['nX%s' % _b36(c.wild.index(r))] = [r['species'], r['pmin'], r['pmax']]
    by_species = {}
    for t, (sp, pmin, _pmax) in wild.items():
        if sp not in by_species or pmin < wild[by_species[sp]][1]:
            by_species[sp] = t
    mega_of = {}
    for i, b in re.findall(r"set Mega_Base\[(\d+)\] = '(\w{4})'", script):
        mega_of.setdefault(b, int(i))
    for idx, (key, _n, base_sp, *_rest) in zip(range(25, 33), _megas_list()):
        mega_of.setdefault(ids[base_sp][0], idx)
    n_next = n_mega = 0
    for t, (sp, pmin, pmax) in sorted(wild.items()):
        c.data += ["    call SaveInteger(Mega_HT, '%s', 47, %d)" % (t, pmin), "    call SaveInteger(Mega_HT, '%s', 48, %d)" % (t, pmax)]
        nxt = [b for (a, b) in edges if a == sp and b in by_species]
        if nxt:
            c.data.append("    call SaveInteger(Mega_HT, '%s', 45, '%s')" % (t, by_species[nxt[0]]))
            n_next += 1
        for hid in ids2.get(sp, []):
            if hid in mega_of:
                c.data.append("    call SaveInteger(Mega_HT, '%s', 41, %d)" % (t, mega_of[hid] + 1))
                n_mega += 1
                break
    c.report.append('wild: %d types know their next form, %d can be Mega elites' % (n_next, n_mega))

    # ---------------- v3.4.1: kind of each learned move = the game skill its abilities are made from (same order)
    import slk
    sk = slk.Slk(base.read('Units\\AbilityData.slk').decode('latin-1'))
    code_x = sk.name_to_x['code']
    kinds, nk = {}, 0
    b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    n_moves = int(re.search(r'set Mv_N = (\d+)', script).group(1))
    for m in range(n_moves):
        row = sk.find('AV' + b36[m // 36] + b36[m % 36])
        code = (row or {}).get(code_x, '').strip('"')
        if code not in kinds:
            kinds[code] = len(kinds)
        c.data.append('    set Mv_Kind[%d] = %d' % (m, kinds[code]))
    c.report.append('learned moves: %d kinds of game skill %s' % (len(kinds), sorted(kinds)))

    # ---------------- v3.4.2: evolution items that are type items of another type (Onix / Scyther + Metal Coat):
    # Type_OnSell lets that Pokemon buy it anyway (Mega_HT key 92 on its type = the item)
    type_item = dict(re.findall(r"set Type_Item\[(\d+)\] = '(\w{4})'", script))
    type_word = dict(re.findall(r'set Type_Word\[(\d+)\] = "(\w+)"', script))
    word_of = {type_item[i]: type_word[i] for i in type_item}
    funcs = {m.group(1): m.group(2) for m in re.finditer(
        r'(?ms)^function (\w+) takes nothing returns \w+\n(.*?)\nendfunction', script)}
    allowed = []
    for _t, cond, act in re.findall(r"call TriggerAddCondition\((\w+),Condition\(function (\w+)\)\)\n"
                                    r"call TriggerAddAction\(\1,function (\w+)\)", script):
        its = [i for i in re.findall(r"GetItemTypeId\(GetManipulatedItem\(\)\)=='(\w{4})'", funcs.get(cond, ''))
               if i in word_of]
        if not its:
            continue
        for cf, _new in re.findall(r"if\((\w+)\(\)\)then\n(?:[^\n]*\n){0,6}?call Mega_SafeReplace\(GetManipulatingUnit\(\),'(\w{4})'",
                                   funcs.get(act, '')):
            for ty in re.findall(r"GetUnitTypeId\(GetManipulatingUnit\(\)\)=='(\w{4})'", funcs.get(cf, '')):
                for it in its:
                    if word_of[it] not in (allu.get(ty).get('unam') or '' if allu.get(ty) else ''):
                        c.data.append("    call SaveInteger(Mega_HT, '%s', 92, '%s')" % (ty, it))
                        allowed.append('%s+%s' % ((allu.get(ty).get('upro') if allu.get(ty) else ty), it))
    c.report.append('evolution items of another type allowed: %s' % ', '.join(allowed))

    # ---------------- v3.4.2: type items for all 18 types (Ground: Soft Sand was not registered; Fairy had none)
    c.item_mods = [('ITFY', {'abilList': '"A03C,A03A"', 'goldcost': '3000', 'stockMax': '1', 'stockRegen': '60'})]
    c.item_txt_mods = [
        ('ITFY', [('Name', 'Pixie Plate'), ('Tip', 'Purchase |cffffcc00Pixie Plate|r'),
                  ('Ubertip', 'Raise 20% damage and recover 50 HP per second.|n|n|cffffcc00Equip with Fairy Pokemon|r'),
                  ('Description', 'Equip with Fairy Pokemon.'), ('Buttonpos', '2,1')]),
        ('I013', [('Name', 'Soft Sand'), ('Tip', 'Purchase |cffffcc00Soft Sand [Z]|r')]),
        ('I01X', [('Ubertip', 'Raise 20% damage and 15 armor.|n|n|cffffcc00Equip with Steel Pokemon. Onix and Scyther '
                              'evolve with it (they may buy it).|r')]),
    ]
    c.shop_add.setdefault('n00Q', []).append('ITFY')
    c.report.append('type items: Ground (I013 Soft Sand) and Fairy (ITFY Pixie Plate, Super Mart 2) added')

    # ---------------- v3.4.2: the League in Darkrai's room; its Darkrai becomes a random legend (nL19)
    import league_area
    c.data += league_area.jass_lines(ids)
    o = clone(units['n00F'], 'nL19')
    setf(o, 'unam', 'Wild Darkrai', T_STRING)
    c.objs.append(o)
    leg_n = int(re.search(r'set Leg_N = (\d+)', script).group(1)) + 1   # + Latias & Latios (content.py)
    c.data += ["    set Leg_Type[%d] = 'nL19'" % leg_n, "    set Leg_Soul[%d] = 'I01F'" % leg_n,
               '    set Leg_Name[%d] = "Darkrai"' % leg_n, '    set Leg_N = %d' % (leg_n + 1)]
    import abilities
    c.links.append(('nL19', abilities.by_name()['Bad Dreams']))
    c.item_txt_mods.append(('IL01', [
        ('Name', 'Pokemon League'), ('Tip', 'Teleport to the |cffffcc00Pokemon League [D]|r'),
        ('Ubertip', 'Teleport to the Pokemon League (Elite Four and Champion, 8 badges). The exit portal there '
                    'brings you back to your base.'),
        ('Description', 'Teleport to the Pokemon League.'),
        ('Art', 'ReplaceableTextures\\CommandButtons\\BTNMedalionOfCourage.blp')]))
    c.report.append('League: Darkrai room, Darkrai -> random legend nL19 (Leg %d)' % leg_n)

    # ---------------- v3.4.2: gym difficulty (gyms 1-4 easier; analysis/patch_gym_difficulty.py has the table)
    c.data += ['    set Gym_DiffHP[0] = 0.35', '    set Gym_DiffDmg[0] = 0.45', '    set Gym_DiffAI[0] = 0.25', '    set Gym_Fast[0] = false', '    set Gym_DiffHP[1] = 0.45', '    set Gym_DiffDmg[1] = 0.55', '    set Gym_DiffAI[1] = 0.25', '    set Gym_Fast[1] = false', '    set Gym_DiffHP[2] = 0.7', '    set Gym_DiffDmg[2] = 0.75', '    set Gym_DiffAI[2] = 0.45', '    set Gym_Fast[2] = false', '    set Gym_DiffHP[3] = 0.85', '    set Gym_DiffDmg[3] = 0.85', '    set Gym_DiffAI[3] = 0.45', '    set Gym_Fast[3] = false', '    set Gym_DiffHP[4] = 1.0', '    set Gym_DiffDmg[4] = 1.0', '    set Gym_DiffAI[4] = 0.6', '    set Gym_Fast[4] = true', '    set Gym_DiffHP[5] = 1.0', '    set Gym_DiffDmg[5] = 1.0', '    set Gym_DiffAI[5] = 0.6', '    set Gym_Fast[5] = true', '    set Gym_DiffHP[6] = 1.0', '    set Gym_DiffDmg[6] = 1.0', '    set Gym_DiffAI[6] = 0.6', '    set Gym_Fast[6] = true', '    set Gym_DiffHP[7] = 1.0', '    set Gym_DiffDmg[7] = 1.0', '    set Gym_DiffAI[7] = 0.6', '    set Gym_Fast[7] = true', '    set Gym_DiffHP[8] = 1.0', '    set Gym_DiffDmg[8] = 1.0', '    set Gym_DiffAI[8] = 0.6', '    set Gym_Fast[8] = true']

    # ---------------- Elite Four and Champion
    for s, (who, ty) in enumerate(LEAGUE):
        c.data += ['    set League_Type[%d] = %d' % (s, A.TI[ty]), '    set League_Name[%d] = %s' % (s, _jstr(who))]
    for k, sp in enumerate(CHAMPION_TEAM):
        c.data.append("    set League_ChampTeam[%d] = '%s'" % (k, ids[sp][0]))


def _b36(i):
    b = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return b[i // 36] + b[i % 36]


def _megas_list():
    from content import MEGAS
    return MEGAS
