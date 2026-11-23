"""Wild camps with mixed species (GEMINI.md section 15).

Before: a camp = 5-6 creeps of ONE species (one of them elite). Now every creep of a camp is its own species, taken
from the wild pool of the camp's power (the existing wild models), and a species that is already alive anywhere on
the map is not picked again until the pool of that power runs out. Soul species are picked first. The elite is
still one random creep of the camp, so the Souls you can farm are much more varied.
Also: reinforcements pick their own species; on a tier change each creep becomes its own next form (or a new
unused species) instead of the whole camp becoming one species.

Usage (script with LF line ends, as in build_v42b.build_data):
    import wild_mix
    script = wild_mix.patch_script(script)
"""
import jpatch

WHO = 'wild_mix'
MARK = '// wild_mix (tools/v412/wild_mix.py)'
GLOBALS = MARK + ': living wild species set (stamp)\nhashtable WD_HT = InitHashtable()\ninteger WD_Stamp = 0\n'


def patch_script(s):
    jpatch.check_lf(s, MARK, WHO)
    s = jpatch.once(s, 'real Wild_SoulChance = 20.0\n', 'real Wild_SoulChance = 20.0\n' + GLOBALS, 'globals', WHO)
    s = jpatch.once(s, '\nfunction Wild_CountTotalAlive takes nothing returns integer\n',
                    '\n' + jpatch.read_jass('wild_mix.j') + 'function Wild_CountTotalAlive takes nothing returns integer\n',
                    'before Wild_CountTotalAlive', WHO)
    reinforce, spawn, upgrade = jpatch.read_jass('wild_mix_funcs.j').split('==SPLIT==\n')
    s = jpatch.replace_function(s, 'function Wild_ReinforceCamp takes integer c returns nothing', reinforce,
                                'Wild_ReinforceCamp', WHO)
    s = jpatch.replace_function(s, 'function Wild_SpawnCamp takes integer c returns nothing', spawn, 'Wild_SpawnCamp', WHO)
    s = jpatch.replace_function(s, 'function Wild_Upgrade takes nothing returns nothing', upgrade, 'Wild_Upgrade', WHO)
    return s
