"""Generate the Mega data init and inject tools/jass/mega.j into war3map.j."""
import os
import re

from mega_data import MEGAS

HERE = os.path.dirname(os.path.abspath(__file__))
MEGA_J = os.path.join(HERE, 'jass', 'mega.j')
GLOBALS_BEGIN = '//MEGA_GLOBALS_BEGIN'
GLOBALS_END = '//MEGA_GLOBALS_END'
PRELUDE_BEGIN = '//MEGA_PRELUDE_BEGIN'
PRELUDE_END = '//MEGA_PRELUDE_END'
FUNCS_BEGIN = '//MEGA_FUNCTIONS_BEGIN'
FUNCS_END = '//MEGA_FUNCTIONS_END'
MAIN = 'function main takes nothing returns nothing'
REVIVE_SLEEP_OLD = 'call TriggerSleepAction(I2R((1*GetUnitLevel(GetTriggerUnit()))))'
REVIVE_SLEEP_NEW = 'call TriggerSleepAction(10.00)'
REVIVE_MSG_OLD = '" will revive after "+(("|cffffcc00"+I2S(GetUnitLevel(GetDyingUnit())))'
REVIVE_MSG_NEW = '" will revive after "+(("|cffffcc00"+"10")'


def _jstr(s):
    return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')


def wild_inputs(script, w3u):
    """Data for Wild_InitData: wild types, spawn pool (type, power) and camps, from the v1.8 script/w3u."""
    import wild_data
    objs = {o.new: o for o in w3u.custom}
    old = wild_data.wild_types(w3u)
    pool = []
    for t in old:
        lv = wild_data.NOGL_LEVEL if t == 'nogl' else objs[t].get('ulev')
        pool.append((t, wild_data.power_for_level(lv)))
    pool += [(s.id, s.power) for s in wild_data.SPECIES]
    names = {t: ('Machamp' if t == 'nogl' else objs[t].get('unam')) for t in old}
    return {'types': old + [s.id for s in wild_data.SPECIES], 'pool': pool, 'names': names,
            'camps': wild_data.camps(script, w3u), 'souls': wild_data.wild_souls(w3u)}


def wild_kit_lines():
    """Wild_KitSkill[(kit-1)*5 + j]: the 5 skills of each type's kit; species type id key 30 = kit number."""
    import skill_data
    import wild_data
    types = sorted(skill_data.HERO_TYPE)
    lines = []
    for k, typ in enumerate(types, 1):
        for j, sk in enumerate(skill_data.kit_for_type(typ)):
            lines.append("    set Wild_KitSkill[%d] = '%s'" % ((k - 1) * 5 + j, sk.id))
    for s in wild_data.SPECIES:
        typ = wild_data.SPECIES_TYPE.get(s.name)
        if typ in types:
            lines.append("    call SaveInteger(Mega_HT, '%s', 30, %d)" % (s.id, types.index(typ) + 1))
    return lines


def gen_wild_init(wild):
    from wild_data import CAMP_SIZE_MULT
    wild = wild or {'types': [], 'pool': [], 'camps': [], 'souls': []}
    souls = wild.get('souls', [])
    new = [s for s in souls if s.new]
    lines = ['function Wild_InitData takes nothing returns nothing',
             '    set Wild_TypeN = %d' % len(wild['types']),
             '    set Wild_PoolN = %d' % len(wild['pool']),
             '    set Wild_CampN = %d' % len(wild['camps']),
             '    set Soul_N = %d' % len(new)]
    for s in souls:  # wild type -> Soul of its own species (key 8 under the type id)
        lines += ["    call SaveInteger(Mega_HT, '%s', 8, '%s')" % (t, s.item) for t in s.wild_types]
    for i, s in enumerate(new):  # Souls we add: transform in the centre circle
        lines += ["    set Soul_Item[%d] = '%s'" % (i, s.item), "    set Soul_Hero[%d] = '%s'" % (i, s.hero)]
    for i, t in enumerate(wild['types']):
        lines.append("    set Wild_Type[%d] = '%s'" % (i, t))
    for i, (t, p) in enumerate(wild['pool']):
        lines += ["    set Wild_Pool[%d] = '%s'" % (i, t), '    set Wild_PoolPow[%d] = %d' % (i, p)]
    for i, c in enumerate(wild['camps']):
        lines += ['    set Wild_CampX[%d] = %.1f' % (i, c.x), '    set Wild_CampY[%d] = %.1f' % (i, c.y),
                  '    set Wild_CampSize[%d] = %d' % (i, c.count * CAMP_SIZE_MULT), '    set Wild_CampPow[%d] = %d' % (i, c.power)]
    import learn_data
    import type_items
    from wild_data import SPECIES, SPECIES_TYPE
    for sp in SPECIES:  # key 34 under a wild type id: the type item a gym Pokemon of it holds
        if type_items.item_for_type(SPECIES_TYPE.get(sp.name, '')):
            lines.append("    call SaveInteger(Mega_HT, '%s', 34, '%s')" % (sp.id, type_items.item_for_type(SPECIES_TYPE[sp.name])))
    for t, name in (wild.get('names') or {}).items():  # v1.8 wild creeps: type from the species data
        info = learn_data.SPECIES.get(learn_data.slug(name))
        item = type_items.item_for_type(info['types'][0]) if info and info.get('types') else ''
        if item:
            lines.append("    call SaveInteger(Mega_HT, '%s', 34, '%s')" % (t, item))
    lines += wild_kit_lines()
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


TAVERNS = ('n000', 'n00B', 'n01G', 'n01H')


def random_pool(w3u, extra=()):
    """Pokemon sold by the four taverns (the starters a player can pick), plus extra starters."""
    objs = {o.new: o for o in w3u.custom}
    pool = []
    for t in TAVERNS:
        pool += [x for x in (objs[t].get('useu') or '').split(',') if x]
    return pool + list(extra)


def evo_inputs():
    """Evolutions of the new Pokemon: level based (from, to, level) and item based (from, item, to)."""
    import poke_data
    return {'level': [(f.id, f.evolves_to, f.level) for f in poke_data.FORMS if f.evolves_to],
            'item': list(poke_data.ITEM_EVOLUTIONS)}


def gen_evo_init(evo):
    """Evo_InitData: evolution tables, plus tavern 5 and Mega Shop III when the new Pokemon are built in."""
    import poke_data
    import type_taverns
    from mega_data import SHOP3_ID
    lines = ['function Evo_InitData takes nothing returns nothing']
    lvl = evo['level'] if evo else []
    item = evo['item'] if evo else []
    lines += ['    set Evo_N = %d' % len(lvl), '    set Evo_ItemN = %d' % len(item)]
    for i, (frm, to, level) in enumerate(lvl):
        lines += ["    set Evo_From[%d] = '%s'" % (i, frm), "    set Evo_To[%d] = '%s'" % (i, to),
                  '    set Evo_Level[%d] = %d' % (i, level)]
    for i, (frm, it, to) in enumerate(item):
        lines += ["    set Evo_ItemFrom[%d] = '%s'" % (i, frm), "    set Evo_Item[%d] = '%s'" % (i, it),
                  "    set Evo_ItemTo[%d] = '%s'" % (i, to)]
    if evo:
        x, y, face = poke_data.TAVERN_POS
        lines += ["    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), '%s', %.1f, %.1f, %.1f)"
                  % (poke_data.TAVERN_ID, x, y, face)]
        lines += [
                  "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), '%s', -4416.0, 1088.0, 0.0)" % SHOP3_ID,
                  "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), '%s', 4416.0, -1088.0, 180.0)" % SHOP3_ID]
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def gen_rand_init(rand):
    rand = rand or []
    lines = ['function Rand_InitData takes nothing returns nothing', '    set Rand_N = %d' % len(rand)]
    lines += ["    set Rand_Type[%d] = '%s'" % (i, t) for i, t in enumerate(rand)]
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def gen_leg_init(legends):
    """Leg_InitData: the random legend types, their Souls and names."""
    legends = legends or []
    lines = ['function Leg_InitData takes nothing returns nothing', '    set Leg_N = %d' % len(legends)]
    for i, leg in enumerate(legends):
        lines += ["    set Leg_Type[%d] = '%s'" % (i, leg.id), "    set Leg_Soul[%d] = '%s'" % (i, leg.soul),
                  '    set Leg_Name[%d] = %s' % (i, _jstr(leg.name))]
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def gen_ab_init(abil):
    """Ab_InitData: the Pokemon Abilities (1-based numbers, as in ability_data.ABILITIES), their effects, the unit
    types that carry each one and the Ability of each Mega. Effect e of Ability a is e = a*2 + k (k = 0, 1)."""
    from ability_data import FAMILY
    abil = abil or {}
    abilities = abil.get('abilities') or []
    lines = ['function Ab_InitData takes nothing returns nothing', '    set Ab_N = %d' % len(abilities)]
    for a, ab in enumerate(abilities, 1):
        lines += ['    set Ab_Name[%d] = %s' % (a, _jstr(ab.name)), '    set Ab_Info[%d] = %s' % (a, _jstr(ab.text))]
        for k, ef in enumerate(ab.effects):
            e = a * 2 + k
            lines += ['    set Ab_Fam[%d] = %d' % (e, FAMILY[ef.fam]),
                      '    set Ab_X[%d] = %.4f' % (e, ef.x), '    set Ab_Y[%d] = %.4f' % (e, ef.y),
                      '    set Ab_Z[%d] = %.4f' % (e, ef.z), '    set Ab_W[%d] = %.4f' % (e, ef.w),
                      '    set Ab_S[%d] = %s' % (e, _jstr(ef.s)),
                      "    set Ab_Raw[%d] = %s" % (e, "'%s'" % ef.raw if ef.raw else '0')]
    for t, a in sorted(abil.get('types', {}).items()):
        lines.append("    call SaveInteger(Ab_HT, '%s', 0, %d)" % (t, a))
    for m, a in sorted(abil.get('megas', {}).items()):
        lines.append('    set Ab_MegaAb[%d] = %d' % (m, a))
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def gen_mv_init(moves):
    """Mv_InitData: the learnable moves (label, score) and, per unit type, its candidate moves: key 99 = count,
    100 + 2k = move index, 101 + 2k = hero level at which candidate k becomes available."""
    plan_moves = moves.moves if moves else []
    lines = ['function Mv_InitData takes nothing returns nothing', '    set Mv_N = %d' % len(plan_moves)]
    import objects
    for m in plan_moves:
        text, base = objects.move_tip_tokens(m)
        lines += ['    set Mv_Label[%d] = %s' % (m.index, _jstr('%s (%s, power %d)' % (m.name, m.type.capitalize(), m.power))),
                  '    set Mv_Score[%d] = %d' % (m.index, m.score)]
        if base[0]:  # damage moves: the tooltip is rebuilt for the hero's current damage multiplier
            lines += ['    set Mv_Text[%d] = %s' % (m.index, _jstr(text)), '    set Mv_D1[%d] = %d' % (m.index, base[0]),
                      '    set Mv_D2[%d] = %d' % (m.index, base[1])]
    if moves:
        for uid, cands in sorted(moves.by_unit.items()):
            lines.append("    call SaveInteger(Ab_HT, '%s', 99, %d)" % (uid, len(cands)))
            for k, (lv, mi) in enumerate(cands):
                lines += ["    call SaveInteger(Ab_HT, '%s', %d, %d)" % (uid, 100 + 2 * k, mi),
                          "    call SaveInteger(Ab_HT, '%s', %d, %d)" % (uid, 101 + 2 * k, lv)]
        for uid, tms in sorted(moves.tm_by_unit.items()):
            lines.append("    call SaveInteger(Ab_HT, '%s', 299, %d)" % (uid, len(tms)))
            for k, mi in enumerate(tms):
                lines.append("    call SaveInteger(Ab_HT, '%s', %d, %d)" % (uid, 300 + k, mi))
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


PICK_TYPES = ('normal', 'fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 'ground', 'flying',
              'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy')


def gen_type_items_init():
    """Type_InitData: the type items and the type word a buyer's unit name must contain."""
    import type_items
    lines = ['function Type_InitData takes nothing returns nothing', '    set Type_N = %d' % len(type_items.TYPE_ITEMS)]
    for i, (item, word) in enumerate(type_items.TYPE_ITEMS):
        lines += ["    set Type_Item[%d] = '%s'" % (i, item), '    set Type_Word[%d] = %s' % (i, _jstr(word)), '    set Type_Cost[%d] = %d' % (i, type_items.COST)]
    lines.append('endfunction')
    return chr(10).join(lines) + chr(10)


def gen_pick_init(enabled):
    """Pick_InitData: the Pokemon of the tavern picker (every new form that nothing evolves into), grouped by
    primary type (Pick_TFirst/Pick_TCount are runs of the sorted list) and sorted by name inside a type."""
    import learn_data
    import poke_data
    lines = ['function Pick_InitData takes nothing returns nothing']
    if enabled:
        targets = {f.evolves_to for f in poke_data.FORMS if f.evolves_to}

        def ptype(f):
            sp = learn_data.SPECIES.get(learn_data.slug(f.name))
            t = sp['types'][0] if sp and sp.get('types') else 'normal'
            return t if t in PICK_TYPES else 'normal'
        import type_taverns
        later = type_taverns.later_form_names()  # form 2/3 of a family are not offered
        forms = sorted((f for f in poke_data.FORMS if f.id not in targets and f.name not in later
                        and f.name not in poke_data.LEGENDARY_NAMES),
                       key=lambda f: (PICK_TYPES.index(ptype(f)), f.name.lower()))
        lines.append('    set Pick_N = %d' % len(forms))
        for i, f in enumerate(forms):
            lines += ["    set Pick_Type[%d] = '%s'" % (i, f.id), '    set Pick_Name[%d] = %s' % (i, _jstr(f.name))]
        used = [t for t in PICK_TYPES if any(ptype(f) == t for f in forms)]
        lines.append('    set Pick_TN = %d' % len(used))
        for k, t in enumerate(used):
            first = next(i for i, f in enumerate(forms) if ptype(f) == t)
            count = sum(1 for f in forms if ptype(f) == t)
            lines += ['    set Pick_TName[%d] = %s' % (k, _jstr(t.capitalize())), '    set Pick_TFirst[%d] = %d' % (k, first),
                      '    set Pick_TCount[%d] = %d' % (k, count)]
    else:
        lines.append('    set Pick_N = 0')
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def gen_data_init(mega_scale, base_scale, wild=None, rand=None, evo=None, legends=None, abil=None, moves=None):
    megas = [m for m in MEGAS if m.index in mega_scale]  # Megas whose assets are part of this build
    lines = [gen_wild_init(wild).rstrip('\n'), gen_rand_init(rand).rstrip('\n'), gen_evo_init(evo).rstrip('\n'),
             gen_leg_init(legends).rstrip('\n'), gen_ab_init(abil).rstrip('\n'),
             gen_mv_init(moves).rstrip('\n'), gen_pick_init(evo is not None).rstrip('\n'), gen_type_items_init().rstrip('\n'),
             'function Mega_InitData takes nothing returns nothing', '    set Mega_N = %d' % len(megas)]
    for m in megas:
        i = m.index
        r, g, b = m.tint
        lines += [
            "    set Mega_Base[%d] = '%s'" % (i, m.base_unit),
            "    set Mega_Stone[%d] = '%s'" % (i, m.stone_id),
            "    set Mega_Skin[%d] = '%s'" % (i, m.skin_id),
            "    set Mega_Evolve[%d] = '%s'" % (i, m.evolve_id),
            '    set Mega_PStr[%d] = %d' % (i, m.str_),
            '    set Mega_PAgi[%d] = %d' % (i, m.agi),
            '    set Mega_PInt[%d] = %d' % (i, m.int_),
            '    set Mega_Price[%d] = %d' % (i, m.price),
            '    set Mega_Name[%d] = %s' % (i, _jstr(m.name)),
            '    set Mega_StoneName[%d] = %s' % (i, _jstr(m.stone_name)),
            '    set Mega_Fx[%d] = %s' % (i, _jstr(m.fx)),
            '    set Mega_Scale[%d] = %.3f' % (i, mega_scale[i]),
            '    set Mega_BaseScale[%d] = %.3f' % (i, base_scale[i]),
            '    set Mega_R[%d] = %d' % (i, r),
            '    set Mega_G[%d] = %d' % (i, g),
            '    set Mega_B[%d] = %d' % (i, b),
        ]
    lines.append('endfunction')
    return '\n'.join(lines) + '\n'


def _between(text, begin, end):
    return text[text.index(begin) + len(begin):text.index(end)].strip('\n') + '\n'


def jass_balance():
    """JASS global name -> value from tools/balance.py (written into mega.j at build time)."""
    import balance as b
    return {
        'Wild_TierStep': b.WILD_TIER_STEP, 'Wild_TierArmor': b.WILD_TIER_ARMOR, 'Wild_DmgMult': b.WILD_DMG_MULT, 'Wild_Respawn': b.WILD_RESPAWN,
        'Wild_SoulChance': b.WILD_SOUL_CHANCE, 'Wild_StoneChance': b.WILD_STONE_CHANCE,
        'Wild_EliteHP': b.ELITE_HP, 'Wild_EliteDmg': b.ELITE_DMG, 'Wild_EliteArmor': b.ELITE_ARMOR,
        'Wild_EliteGold': b.ELITE_GOLD, 'Wild_EliteScale': b.ELITE_SCALE,
        'Leg_Interval': b.LEG_INTERVAL, 'Leg_Next': b.LEG_INTERVAL, 'Leg_Max': b.LEG_MAX,
        'Ab_ScaleK': b.SKILL_SCALE_K, 'Ab_LevelK': b.LEVEL_SKILL_K, 'Ab_BasicMult': b.BASIC_MULT,
    }


def _set_balance(globals_text):
    for name, value in jass_balance().items():
        pat = re.compile(r'(?m)^((?:constant )?(?:real|integer) %s = )[^\r\n]*' % name)
        assert len(pat.findall(globals_text)) == 1, name
        shown = repr(float(value)) if isinstance(value, float) else str(int(value))
        globals_text = pat.sub(lambda m: m.group(1) + shown, globals_text)
    return globals_text


def _split_module():
    """(globals, prelude, functions) of tools/jass/mega.j."""
    text = open(MEGA_J, encoding='utf-8').read().replace('\r\n', '\n')
    # the map script is handled as latin-1 text; keep non-ASCII literals (e.g. "t là gà") as UTF-8 bytes
    text = text.encode('utf-8').decode('latin-1')
    funcs = text[text.index(PRELUDE_END) + len(PRELUDE_END):].strip('\n') + '\n'
    return _set_balance(_between(text, GLOBALS_BEGIN, GLOBALS_END)), _between(text, PRELUDE_BEGIN, PRELUDE_END), funcs


def module_source(mega_scale, base_scale, wild=None, rand=None, evo=None, legends=None, abil=None, moves=None):
    """Stand-alone source (globals block + prelude + functions) for the checker."""
    glob, prelude, funcs = _split_module()
    return ('globals\n' + glob + 'endglobals\n' + prelude
            + gen_data_init(mega_scale, base_scale, wild, rand, evo, legends, abil, moves) + funcs)


def _replace_exact(script, old, new, count):
    if script.count(old) != count:
        raise ValueError('expected %d x %r, found %d' % (count, old, script.count(old)))
    return script.replace(old, new)


# v1.8 chance functions of the Soul drops of the legend bosses in their rooms (each: 30% -> 100%)
BOSS_SOUL_CHANCE_FUNCS = ('FE4', 'Gs4', 'F14', 'F64', 'FP4', 'FM4', 'FW4', 'G84', 'FZ4', 'Go4', 'F54', 'Gw4', 'Gf4',
                          'Gj4')


def patch_boss_souls(script):
    for fn in BOSS_SOUL_CHANCE_FUNCS:
        pat = re.compile(r'(function %s takes nothing returns boolean\s*if\(not\(GetRandomInt\(1,100\)<=)30(\)\))' % fn)
        script, n = pat.subn(lambda m: m.group(1) + '100' + m.group(2), script, count=1)
        if n != 1:
            raise ValueError('boss Soul chance function %s not found' % fn)
    return script


def inject(script, mega_scale, base_scale, wild=None, rand=None, version="2.0", evo=None, legends=None, abil=None,
           moves=None):
    glob, prelude, funcs = _split_module()
    # fixes in the original map script: guarded evolution replacement, 10s revive
    script = _replace_exact(script, 'call ReplaceUnitBJ(', 'call Mega_SafeReplace(', 74)
    script = _replace_exact(script, REVIVE_SLEEP_OLD, REVIVE_SLEEP_NEW, 1)
    script = _replace_exact(script, REVIVE_MSG_OLD, REVIVE_MSG_NEW, 2)
    script = patch_boss_souls(script)
    eg = script.index('endglobals')
    script = script[:eg] + '\n' + GLOBALS_BEGIN + '\n' + glob + GLOBALS_END + '\n' + script[eg:]
    eg = script.index('endglobals') + len('endglobals')
    script = script[:eg] + '\n' + PRELUDE_BEGIN + '\n' + prelude + PRELUDE_END + '\n' + script[eg:]
    mi = script.index(MAIN)
    block = (FUNCS_BEGIN + '\n' + gen_data_init(mega_scale, base_scale, wild, rand, evo, legends, abil, moves) + funcs
             + FUNCS_END + '\n')
    script = script[:mi] + block + script[mi:]
    mi = script.index(MAIN)
    end = script.index('endfunction', mi)
    if not script[:end].endswith('\n'):
        script = script[:end] + '\n' + script[end:]
        end += 1
    script = script[:end] + 'call Mega_Init()\n' + script[end:]
    old = 'call SetMapName("Pokemon Arena v1.8")'
    if old not in script:
        raise ValueError('SetMapName v1.8 not found')
    return script.replace(old, 'call SetMapName("Pokemon Arena v%s")' % version)
