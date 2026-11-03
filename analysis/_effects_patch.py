"""One-off: new Warcraft III skill templates (Sleep, Healing Wave, Thunder Clap) and status moves in the learn pool."""
import re

# 1. poke_data: three templates copied from standard WC3 abilities that exist in the map's AbilityData
P = 'tools/poke_data.py'
t = open(P, encoding='utf-8').read()
anchor = "    _t('ULT_RAIN', 'AHbz',"
assert t.count(anchor) == 1
new = (
    "    _t('SLEEP', 'AUsl', {'Dur': (3, 4, 5)}, 12, (75, 100, 125), _I + 'BTNSleep.blp',\n"
    "       'Puts a target to sleep for {Dur} seconds.'),\n"
    "    _t('HEAL', 'AOhw', {'DataA': (150, 250, 350), 'DataB': (3, 4, 5)}, 12, (75, 100, 125), _I + 'BTNHealingWave.blp',\n"
    "       'Heals an ally for {DataA} and bounces {DataB} times to nearby allies.'),\n"
    "    _t('CLAP', 'AHtc', {'DataA': (100, 175, 250), 'DataC': (0.2, 0.3, 0.4)}, 12, (75, 100, 125), _I + 'BTNThunderClap.blp',\n"
    "       'Deals {DataA} damage to nearby enemies and slows them by {DataC%} for 5 seconds.'),\n"
)
t = t.replace(anchor, new + anchor)
open(P, 'w', encoding='utf-8').write(t)

# 2. learn_data: status moves with a known effect join the pool (at most 2 per species)
P = 'tools/learn_data.py'
t = open(P, encoding='utf-8').read()
old = "def candidates(species_slug):\n"
assert t.count(old) == 1
t = t.replace(old, (
    "# status moves that get a real effect (v3.2): move name -> template\n"
    "STATUS_EFFECTS = {\n"
    "    'Hypnosis': 'SLEEP', 'Sleep Powder': 'SLEEP', 'Spore': 'SLEEP', 'Yawn': 'SLEEP',\n"
    "    'Recover': 'HEAL', 'Synthesis': 'HEAL', 'Moonlight': 'HEAL', 'Heal Pulse': 'HEAL', 'Soft-Boiled': 'HEAL',\n"
    "    'Thunder Wave': 'CLAP', 'Icy Wind': 'CLAP', 'Bulldoze': 'CLAP', 'Earthquake': 'CLAP',\n"
    "}\n"
    "STATUS_PER_SPECIES = 2\n\n\n" + old))

old2 = "    best = {}\n    for lv, mv in s['moves']:\n        info = MOVES.get(mv)\n        if info is None or info['power'] <= 0:\n            continue\n"
assert t.count(old2) == 1, 'candidates loop'
t = t.replace(old2, "    best = {}\n    for lv, mv in s['moves']:\n        info = MOVES.get(mv)\n        if info is None or (info['power'] <= 0 and info['name'] not in STATUS_EFFECTS):\n            continue\n")

old3 = "    top = sorted(best, key=lambda mv: (-score(MOVES[mv]), best[mv], mv))[:CAND_MAX]\n"
assert t.count(old3) == 1
t = t.replace(old3, (
    "    status = sorted((mv for mv in best if MOVES[mv]['power'] <= 0), key=lambda mv: (best[mv], mv))[:STATUS_PER_SPECIES]\n"
    "    damaging = sorted((mv for mv in best if MOVES[mv]['power'] > 0), key=lambda mv: (-score(MOVES[mv]), best[mv], mv))\n"
    "    top = damaging[:CAND_MAX - len(status)] + status\n"))

old4 = "def template_for(info):\n    \"\"\"(poke_data template key, level column 1..3) of a damaging move.\"\"\"\n    p = info['power']\n"
assert t.count(old4) == 1, 'template_for'
t = t.replace(old4, "def template_for(info):\n    \"\"\"(poke_data template key, level column 1..3) of a damaging move or of a status move with an effect.\"\"\"\n    if info['name'] in STATUS_EFFECTS:\n        return STATUS_EFFECTS[info['name']], 1\n    p = info['power']\n")
open(P, 'w', encoding='utf-8').write(t)
print('patched')
