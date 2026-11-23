"""-random with an optional generation (GEMINI.md section 15).

The host types "-random" (any generation, as before) or "-random 3" / "-random gen3" (only Gen 3 Pokemon).
The generation of each hero of the random pool (Rand_Type) comes from its proper name (upro in war3map.w3u)
-> PokeAPI dex in tools/pokeapi/pokemon_size.json; the table is generated at build time, so new heroes are
picked up by themselves. A hero whose name is not found only appears in the plain "-random".

Usage (script with LF line ends, w3u = objdata.ObjFile of the map being built), as in build_v42b.build_data:
    import random_gen
    script, gen_stats = random_gen.patch_script(script, w3u)
"""
import json
import os
import re

import jpatch
import model_size_check

WHO = 'random_gen'
MARK = '// random_gen (tools/v412/random_gen.py)'
GLOBALS = (MARK + ': generation of the random pool\nhashtable RandG_HT = InitHashtable()\ninteger RandG_Want = 0\n'
           'integer RandG_ListN = 0\ninteger array RandG_List\n')
GEN_LAST_DEX = [151, 251, 386, 493, 649, 721, 809, 905, 1025]
SIZE_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pokeapi', 'pokemon_size.json')
OLD_HINT = 'The host types -random and every player gets a random Pokemon.'
NEW_HINT = 'The host types -random (or -random 1 .. 9 for one generation) and every player gets a random Pokemon.'


def gen_of_dex(dex):
    for g, last in enumerate(GEN_LAST_DEX, 1):
        if dex <= last:
            return g
    return 0


def proper_name(upro):
    """first proper name, without the "#172 " dex prefix the Gen 2-4 heroes have (4.3)"""
    return re.sub(r'^#\d+\s+', '', (upro or '').split(',')[0].strip())


def hero_gens(s, w3u):
    """{hero id: generation} for every hero of the random pool"""
    with open(SIZE_JSON, encoding='utf-8') as fh:
        species = json.load(fh)
    names = {u.id: proper_name(u.get('upro')) for u in w3u.original + w3u.custom}
    out = {}
    for hid in dict.fromkeys(re.findall(r"set Rand_Type\[[^\]]*\] = '(\w{4})'", s)):
        rec = species.get(model_size_check.slug(names.get(hid, '')))
        out[hid] = gen_of_dex(int(rec['dex'])) if rec else 0
    return out


def patch_script(s, w3u):
    jpatch.check_lf(s, MARK, WHO)
    gens = hero_gens(s, w3u)
    if not gens:
        raise ValueError('[random_gen] no Rand_Type entries found')
    data = ['function RandG_Init takes nothing returns nothing']
    data += ["    call SaveInteger(RandG_HT, '%s', 0, %d)" % (h, g) for h, g in gens.items() if g]
    data.append('endfunction\n')
    s = jpatch.once(s, 'integer array Rand_Type\n', 'integer array Rand_Type\n' + GLOBALS, 'globals', WHO)
    s = jpatch.once(s, '\nfunction Rand_Give takes player p returns nothing\n',
                    '\n' + jpatch.read_jass('random_gen.j') + '\n'.join(data) + '\n'
                    'function Rand_Give takes player p returns nothing\n', 'before Rand_Give', WHO)
    s = jpatch.once(s, '        set t = Rand_Type[GetRandomInt(0, Rand_N - 1)]\n', '        set t = RandG_Pick()\n',
                    'Rand_Give pick', WHO)
    s = jpatch.replace_function(s, 'function Rand_OnChat takes nothing returns nothing',
                                jpatch.read_jass('random_gen_chat.j'), 'Rand_OnChat', WHO)
    s = jpatch.once(s, 'call TriggerRegisterPlayerChatEvent(t, Player(i), "-random", true)',
                    'call TriggerRegisterPlayerChatEvent(t, Player(i), "-random", false)', 'chat event', WHO)
    s = jpatch.once(s, '    call TriggerAddAction(t, function Rand_OnChat)\n',
                    '    call TriggerAddAction(t, function Rand_OnChat)\n    call ExecuteFunc("RandG_Init")\n',
                    'init data', WHO)
    s = jpatch.once(s, OLD_HINT, NEW_HINT, 'hint text', WHO)
    stats = {}
    for g in gens.values():
        stats[g] = stats.get(g, 0) + 1
    return s, stats
