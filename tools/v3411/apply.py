"""v3.4.11: build the script from the v3.4.10 map (its source is not on this PC) + the approved plan
(docs: "Kế hoạch rework chiêu thức và Ability", 2026-11-14): move effects, statuses, stat stages, physical /
special defense, held type items rewritten, one of each held item, gym / Elite Four type items, Elite Four in
Darkrai's room without PvP, legend Abilities and the new Pressure, -tp.

    python -I tools/v3411/apply.py      -> v3411/war3map.j (+ v3411/plan.json for build.py)
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)
import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402
import league_area  # noqa: E402
import status_moves as SM  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v3.4.10.w3x')
OUT_DIR = os.path.join(WORK, 'v3411')
VERSION = open(os.path.join(HERE, 'version.txt')).read().strip()

T = {'bug': 0, 'dark': 1, 'dragon': 2, 'electric': 3, 'fairy': 4, 'fighting': 5, 'fire': 6, 'flying': 7, 'ghost': 8,
     'grass': 9, 'ground': 10, 'ice': 11, 'normal': 12, 'poison': 13, 'psychic': 14, 'rock': 15, 'steel': 16,
     'water': 17}

# ------------------------------------------------------------------ move effects
F_RECHARGE, F_CHARGE, F_VANISH, F_MULTI, F_CRIT, F_PRIO, F_TRAP, F_PIVOT = 1, 2, 4, 8, 16, 32, 64, 128
F_NOMISS, F_EXPLODE, F_PAYDAY, F_FACADE, F_PLAIN, F_DREAM, F_FAKEOUT, F_THRASH = 256, 512, 1024, 2048, 4096, 8192, \
    16384, 32768
F_PUSH, F_PUNCH, F_BITE, F_PULSE, F_CONTACT, F_SOLAR, F_METEOR, F_FELL = 65536, 131072, 262144, 524288, 1048576, \
    2097152, 4194304, 8388608
F_CHANNEL = 16777216

STATUS_CH = {'thunder': 30, 'body-slam': 30, 'discharge': 30, 'spark': 30, 'lick': 30, 'force-palm': 30,
             'dragon-breath': 30, 'nuzzle': 100, 'zap-cannon': 100, 'sludge-bomb': 30, 'poison-jab': 30,
             'gunk-shot': 30, 'poison-sting': 30, 'scald': 30, 'lava-plume': 30, 'sacred-fire': 50, 'water-pulse': 20,
             'hurricane': 30, 'dynamic-punch': 100, 'dizzy-punch': 20, 'tri-attack': 20, 'poison-fang': 50,
             'twineedle': 20, 'smog': 40, 'sludge': 30, 'searing-shot': 30, 'bounce': 30, 'blue-flare': 20,
             'bolt-strike': 20, 'inferno': 100, 'mortal-spin': 100}
FLINCH_CH = {'air-slash': 30, 'iron-head': 30, 'bite': 30, 'rock-slide': 30, 'headbutt': 30, 'stomp': 30,
             'astonish': 30, 'needle-arm': 30, 'snore': 30, 'heart-stamp': 30, 'sky-attack': 30, 'icicle-crash': 30,
             'rolling-kick': 30, 'steamroller': 30, 'zen-headbutt': 20, 'dark-pulse': 20, 'dragon-rush': 20,
             'twister': 20, 'waterfall': 20, 'extrasensory': 10, 'hyper-fang': 10, 'fire-fang': 10, 'ice-fang': 10,
             'thunder-fang': 10, 'bone-club': 10, 'fake-out': 100, 'upper-hand': 100}
TARGET_CH = {'crunch': 20, 'iron-tail': 30, 'shadow-ball': 20, 'moonblast': 30, 'liquidation': 20, 'razor-shell': 50,
             'crush-claw': 50, 'muddy-water': 30, 'bubble-beam': 10, 'bubble': 10, 'play-rough': 10,
             'aurora-beam': 10, 'psychic': 10, 'bug-buzz': 10, 'earth-power': 10, 'flash-cannon': 10,
             'energy-ball': 10, 'focus-blast': 10, 'acid': 10, 'seed-flare': 40, 'mist-ball': 50, 'luster-purge': 50,
             'night-daze': 40, 'mirror-shot': 30, 'octazooka': 50, 'mud-bomb': 30, 'leaf-tornado': 50,
             'rock-smash': 50, 'constrict': 10, 'icy-wind': 100, 'bulldoze': 100, 'rock-tomb': 100, 'mud-shot': 100,
             'mud-slap': 100, 'mystical-fire': 100, 'snarl': 100, 'struggle-bug': 100, 'electroweb': 100,
             'low-sweep': 100}
SELF_CH = {'charge-beam': 70, 'metal-claw': 10, 'steel-wing': 10, 'meteor-mash': 20, 'ancient-power': 10,
           'silver-wind': 10, 'ominous-wind': 10, 'fiery-dance': 50}
RECOIL = {'head-smash': 500, 'take-down': 250, 'submission': 250, 'wild-charge': 250, 'high-jump-kick': 250,
          'jump-kick': 250}
CHARGE = {'solar-beam', 'solar-blade', 'sky-attack', 'meteor-beam', 'razor-wind', 'skull-bash'}
VANISH = {'dig', 'fly', 'bounce', 'phantom-force', 'shadow-force', 'dive'}
PIVOT = {'u-turn', 'volt-switch', 'flip-turn'}
PUSH = {'dragon-tail', 'circle-throw'}
THRASH = {'outrage', 'petal-dance', 'thrash', 'raging-fury'}
PULSE = {'water-pulse', 'dark-pulse', 'dragon-pulse', 'aura-sphere', 'origin-pulse'}
STATS = {'attack': 1, 'defense': 2, 'special attack': 3, 'special defense': 4, 'speed': 5}
AMOUNT = {'one': 1, 'two': 2, 'three': 3, 'four': 4}


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace("'", '').replace('.', '')).strip('-')


def stage_changes(text):
    """[(who 'user'|'target', {stat: delta}, has_chance)] from a PokeAPI short effect"""
    out = []
    for m in re.finditer(r"(lower|raise)s? (?:the |all )?(user|target|targets)(?:'s|') ([A-Za-z ,]+?) by (one|two|three)"
                         r" stages?", text, re.I):
        sign = -1 if m.group(1).lower() == 'lower' else 1
        who = 'user' if m.group(2).lower() == 'user' else 'target'
        names = re.split(r',\s*|\s+and\s+', m.group(3).lower().strip())
        deltas = {}
        for n in names:
            n = n.strip()
            if n in STATS:
                deltas[STATS[n]] = sign * AMOUNT[m.group(4).lower()]
            elif n == 'accuracy':
                deltas['acc'] = sign
        if deltas:
            out.append((who, deltas))
    return out


def parse_move(name, info):
    """effect record for one move (info = tools/learnsets.json moves[slug])"""
    s = slug(name)
    eff = (info.get('effect') or '').replace('\u2019', "'")
    low = eff.lower()
    rec = {'flags': 0, 'class': 1 if info.get('class') == 'physical' else 2}
    f = 0
    if 'recharge' in low:
        f |= F_RECHARGE
    if s in CHARGE:
        f |= F_CHARGE
        if s in ('solar-beam', 'solar-blade'):
            f |= F_SOLAR
        if s == 'meteor-beam':
            f |= F_METEOR
    if s in VANISH:
        f |= F_VANISH
    if re.search(r'hits (2|two|3|three)|2-5 times|twice|multiple times|two to five', low):
        f |= F_MULTI
    if 'critical' in low:
        f |= F_CRIT
    if (info.get('priority') or 0) > 0:
        f |= F_PRIO
    if re.search(r'prevents the target from (leaving|fleeing)|traps|trap', low):
        f |= F_TRAP
    if s in PIVOT:
        f |= F_PIVOT
    if s in PUSH:
        f |= F_PUSH
    if 'never misses' in low:
        f |= F_NOMISS
    if 'user faints' in low or s in ('explosion', 'self-destruct', 'misty-explosion'):
        f |= F_EXPLODE
    if s == 'pay-day':
        f |= F_PAYDAY
    if s == 'facade':
        f |= F_FACADE
    if s == 'dream-eater':
        f |= F_DREAM
    if s == 'fake-out':
        f |= F_FAKEOUT
    if s in THRASH:
        f |= F_THRASH
    if 'punch' in s or s in ('meteor-mash', 'hammer-arm', 'sky-uppercut'):
        f |= F_PUNCH
    if 'fang' in s or s in ('bite', 'crunch', 'jaw-lock'):
        f |= F_BITE
    if s in PULSE:
        f |= F_PULSE
    if s == 'fell-stinger':
        f |= F_FELL
    # recoil / drain
    if 'recoil' in low:
        rec['recoil'] = RECOIL.get(s, 500 if '1/2' in low or 'half' in low else 250 if '1/4' in low else 333)
    elif s in RECOIL:
        rec['recoil'] = RECOIL[s]
    if 'drain' in low or 'heals the user by half the damage' in low:
        rec['drain'] = 750 if s == 'draining-kiss' else 500
    # statuses
    kind = 0
    if s == 'tri-attack':
        kind = 9
    elif 'badly poison' in low or s == 'poison-fang':
        kind = 3
    elif 'burn' in low:
        kind = 1
    elif 'paralyz' in low:
        kind = 4
    elif 'poison' in low and s not in ('dream-eater',):
        kind = 2
    elif 'freeze' in low:
        kind = 6
    elif 'sleep' in low and s not in ('dream-eater', 'snore', 'uproar'):
        kind = 5
    if 'confus' in low and s not in THRASH:
        rec['confuse'] = STATUS_CH.get(s, 10)
    if kind:
        rec['status'] = kind
        rec['status_ch'] = STATUS_CH.get(s, 10)
    if 'flinch' in low:
        rec['flinch'] = FLINCH_CH.get(s, 20)
    # stat stages
    for who, deltas in stage_changes(eff):
        if s in ('fell-stinger', 'meteor-beam'):
            continue
        if who == 'user':
            rec['self'] = {k: v for k, v in deltas.items() if k != 'acc'}
            rec['self_ch'] = SELF_CH.get(s, 10 if 'chance' in low else 100)
        else:
            rec['target'] = {k: v for k, v in deltas.items() if k != 'acc'}
            if 'acc' in deltas:
                rec['acc'] = 1
            rec['target_ch'] = TARGET_CH.get(s, 10 if 'chance' in low else 100)
    if rec['class'] == 1:
        f |= F_CONTACT
    side = ('recoil', 'drain', 'status', 'flinch', 'self', 'target', 'acc', 'confuse')
    if not (f & ~(F_CONTACT | F_PUNCH | F_BITE | F_PULSE)) and not any(k in rec for k in side):
        f |= F_PLAIN
    rec['flags'] = f
    return rec


def describe(rec):
    """English effect line for the tooltip"""
    f = rec['flags']
    bits = []
    names = {1: 'Attack', 2: 'Defense', 3: 'Sp. Atk', 4: 'Sp. Def', 5: 'Speed'}
    st = {1: 'burn', 2: 'poison', 3: 'bad poison', 4: 'paralysis', 5: 'sleep', 6: 'freeze', 9: 'burn / paralysis / freeze'}
    if f & F_PLAIN:
        return 'No extra effect: +10% damage.'
    if f & F_RECHARGE:
        bits.append('+20% damage, then the user rests 2s')
    if f & F_CHARGE:
        bits.append('charges 1.2s first' + (' (not in harsh sun)' if f & F_SOLAR else ''))
    if f & F_METEOR:
        bits.append('+1 Sp. Atk while charging')
    if f & F_VANISH:
        bits.append('the user is out of reach for 1s')
    if f & F_PRIO:
        bits.append('instant, shorter cooldown')
    if f & F_MULTI:
        bits.append('multi-hit move (Skill Link: +50%)')
    if f & F_CRIT:
        bits.append('high critical rate')
    if 'recoil' in rec:
        bits.append('recoil %s of the damage' % {250: '1/4', 333: '1/3', 500: '1/2'}.get(rec['recoil'], '1/3'))
    if 'drain' in rec:
        bits.append('heals %d%% of the damage' % (rec['drain'] // 10))
    if 'status' in rec:
        bits.append('%d%% %s' % (rec['status_ch'], st[rec['status']]))
    if 'confuse' in rec:
        bits.append('%d%% confusion' % rec['confuse'])
    if 'flinch' in rec:
        bits.append('%d%% flinch' % rec['flinch'] if not f & F_FAKEOUT else 'flinches (only right after entering combat)')
    if 'target' in rec or 'acc' in rec:
        parts = ['%+d %s' % (v, names[k]) for k, v in sorted(rec.get('target', {}).items())]
        if rec.get('acc'):
            parts.append('lower accuracy: 20% of its attacks and moves miss for 4s')
        bits.append('target %s (%d%%)' % (', '.join(parts), rec['target_ch']))
    if 'self' in rec:
        parts = ['%+d %s' % (v, names[k]) for k, v in sorted(rec['self'].items())]
        ch = rec['self_ch']
        bits.append('user %s%s' % (', '.join(parts), '' if ch >= 100 else ' (%d%%)' % ch))
    if f & F_TRAP:
        bits.append('traps the target 3s (slowed 90%, 1% max HP per second)')
    if f & F_NOMISS:
        bits.append('never misses (ignores lowered accuracy)')
    if f & F_PIVOT:
        bits.append('the user jumps back')
    if f & F_PUSH:
        bits.append('pushes the target back')
    if f & F_EXPLODE:
        bits.append('the user loses half its HP')
    if f & F_PAYDAY:
        bits.append('extra gold')
    if f & F_FACADE:
        bits.append('double damage if the user has a status')
    if f & F_DREAM:
        bits.append('double damage on a sleeping target')
    if f & F_THRASH:
        bits.append('the user is confused afterwards')
    if f & F_FELL:
        bits.append('+3 Attack on a knock-out')
    s = '; '.join(bits)
    return s[:1].upper() + s[1:] + '.' if s else ''


def rec_lines(key, rec):
    out = []
    put = lambda k, v: out.append('    call SaveInteger(Fx_HT, %s, %d, %d)' % (key, k, v))  # noqa: E731
    if rec['flags']:
        put(1, rec['flags'])
    if rec.get('recoil'):
        put(2, rec['recoil'])
    if rec.get('drain'):
        put(3, rec['drain'])
    if rec.get('status'):
        put(4, rec['status'])
        put(5, rec['status_ch'])
    if rec.get('flinch'):
        put(6, rec['flinch'])
    if rec.get('self'):
        put(7, rec['self_ch'])
        for k, v in rec['self'].items():
            put(10 + k, v)
    if rec.get('target') or rec.get('acc'):
        put(8, rec['target_ch'])
        for k, v in rec.get('target', {}).items():
            put(20 + k, v)
        if rec.get('acc'):
            put(26, 1)
    put(30, rec['class'])
    return out


# ------------------------------------------------------------------ helpers on the base map
def read_slk(m, name):
    return slk.Slk(m.read(name).decode('latin-1'))


def norm_name(n):
    n = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', n or '').strip()
    n = re.sub(r'^(Wild|Elite|Mega|Shiny)\s+', '', n)
    n = re.sub(r'\s+[XY]$', '', n)
    return n


def unit_species(m, species):
    """unit type id -> species record of tools/learnsets.json (by unit / hero proper name)"""
    w3u = objdata.ObjFile(m.read('war3map.w3u'))
    by_name = {v['name'].lower(): v for v in species.values()}
    out = {}
    names = {}
    for o in w3u.custom:
        nm, pro = o.get('unam') or '', o.get('upro') or ''
        key = norm_name(pro.split(',')[0] if pro else nm)
        names[o.new] = key
        if key.lower() in by_name:
            out[o.new] = by_name[key.lower()]
    return out, names


def legend_codes(names):
    table = {'Mewtwo': 1, 'Zapdos': 2, 'Articuno': 3, 'Moltres': 4, 'Raikou': 5, 'Giratina': 6, 'Deoxys': 7,
             'Dialga': 8, 'Palkia': 9, 'Entei': 10, 'Suicune': 11, 'Ho-Oh': 12, 'Kyogre': 13, 'Groudon': 14,
             'Regirock': 15, 'Jirachi': 16, 'Buzzwole': 17, 'Regigigas': 18, 'Latias & Latios': 19, 'Latias': 19,
             'Latios': 19, 'Rayquaza': 20, 'Darkrai': 21}
    out = {}
    for uid, nm in names.items():
        if nm in table:
            out[uid] = table[nm]
    out['nL19'] = 21
    return out


# ability index each legend gets (codes 1..9: the legend Pressure, 74)
LEGEND_AB = {1: 74, 2: 74, 3: 74, 4: 74, 5: 74, 6: 74, 7: 74, 8: 74, 9: 74, 10: 14, 11: 11, 12: 76, 13: 75, 16: 77,
             17: 78}
PRESSURE_TIER = {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 3, 9: 4}

NEW_ABILITIES = [
    (74, 'Pressure', 'Legend Pressure: enemies within 800 pay double mana for moves, their cooldowns run 30% slower,'
     ' -25% attack speed and -1 Attack / Sp. Atk. The holder ignores stat drops and flinching. Mewtwo: Psychic +20%,'
     ' a psychic shield (20% max HP, 8s) below 50% HP every 90s. Zapdos: 30% paralysis on melee attackers. Articuno'
     ' / Moltres: +20% freeze / burn. Raikou: +1 Speed every 8s in combat. Giratina: 15% of hits pass through.'
     ' Deoxys: Psychic +15%, cooldowns -15%. Dialga: own cooldowns -25%. Palkia: 20% critical, enemies slowed.'),
    (75, 'Drizzle', 'Rain within 700: allies deal +30% with Water moves, enemies deal -50% with Fire moves. Heals 1%'
     ' max HP per second.'),
    (76, 'Regenerator', 'Out of combat for 3s: heals 3% max HP per second. Once every 120s a knock-out leaves it at'
     ' 40% HP (Rebirth).'),
    (77, 'Serene Grace', 'The extra effects of its moves (status, flinch, stat changes) are twice as likely. Moves'
     ' deal +10% damage.'),
    (78, 'Beast Boost', 'Each knock-out: +1 Attack for 30s (up to +4).'),
]
# texts of reworked Abilities: ('set', text) replaces, ('add', text) appends to the 3.4.10 text
AB_TEXTS = {
    16: ('set', 'Enemies within 600 pay double mana for moves, their cooldowns run 20% slower and they attack 15%'
         ' slower.'),
    21: ('set', 'Takes no recoil damage from its moves. Takes 10% less damage.'),
    31: ('set', 'Recoil moves and High Jump Kick deal +30% damage; attacks deal +15%.'),
    72: ('add', 'Multi-hit moves always hit 5 times (+50%).'),
    27: ('add', 'Punching moves deal +25% damage.'),
    70: ('add', 'Biting moves deal +40% damage.'),
    49: ('set', 'Attacks and contact (physical) moves deal +30% damage.'),
    50: ('set', 'Pulse / aura moves (Water Pulse, Dark Pulse, Dragon Pulse, Aura Sphere) +50%; other special moves'
         ' +15%.'),
    32: ('set', 'While burned, poisoned or paralyzed: physical damage +50% (burn does not weaken it). Low HP or a'
         ' harmful effect: +20% attack speed.'),
    15: ('set', 'Entering combat (every 20s): enemies within 500 get -1 Attack for 8s.'),
    20: ('add', 'Enemies cannot lower its stats.'),
    29: ('add', 'Its Attack cannot be lowered.'),
    37: ('add', 'Its accuracy cannot be lowered.'),
    42: ('add', 'Cannot flinch; ignores Intimidate.'),
    5: ('set', '30% chance to paralyze a melee attacker. Its attacks: 20% chance for chain lightning.'),
    6: ('set', '30% chance to burn a melee attacker. Burning aura around it.'),
    7: ('set', '30% chance to poison a melee attacker, and 30% with its own attacks.'),
    9: ('add', 'A status given to it is given back to the one who caused it.'),
    24: ('add', 'Every 3s: 30% chance to cure its status.'),
    26: ('add', 'Out of combat for 3s: cures its status.'),
    62: ('add', 'Cannot fall asleep.'),
    25: ('add', 'Sleep lasts half as long.'),
    67: ('set', 'Every 8s in combat: +1 Speed (up to +4).'),
    34: ('add', 'In harsh sun: +30% attack speed.'),
    35: ('add', 'In rain: +30% attack speed.'),
    39: ('set', '10% chance to dodge attacks, 30% in a sandstorm; a dodge slows the attacker.'),
    40: ('set', '10% chance to dodge attacks, 30% in hail; a dodge slows the attacker.'),
    68: ('add', 'Stat drops and statuses from enemies bounce back to them.'),
    47: ('set', 'First 15s after spawning or reviving: 30% less damage; then +50% damage, +30% attack speed and +2'
         ' Attack.'),
    56: ('add', 'Groudon: enemy Water moves in the sun deal -50%.'),
    43: ('add', 'Rayquaza: Dragon / Flying moves +20%.'),
    45: ('add', 'Darkrai: sleeping enemies within 500 lose 8% max HP per second; its moves have a 20% sleep chance.'),
    10: ('add', 'Latias & Latios: Dragon / Psychic moves +20%, 20% dodge.'),
    14: ('add', 'Entei: its attacks have a 20% burn chance.'),
    11: ('add', 'Suicune: out of combat for 3s it cures its status.'),
}

ITEM_TEXT = {
    'Fire': 'Enemies within 350 burn for 1% of their max HP per second.',
    'Grass': 'Regenerates 1.5% max HP per second.',
    'Water': 'Attacks and Water moves slow the target by 25% for 2.5s.',
    'Electric': '30% chance: a shock deals 40% of the hit to enemies within 350.',
    'Bug': '40% chance: a 0.5s stun and 25% more damage.',
    'Poison': '20% chance to poison.',
    'Ice': '15% chance to freeze (1.5s).',
    'Dragon': '+15 all stats. 15% chance: +50% damage and a 1s stun.',
    'Flying': '+5 armor, +30% attack speed.',
    'Normal': '+10 all stats, +1000 HP.',
    'Psychic': '15% chance to dodge attacks.',
    'Fighting': '20% chance: double damage and a 0.2s stun.',
    'Rock': 'Melee attackers take 15% of their hit back.',
    'Steel': '+15 armor.',
    'Dark': '20% chance to silence the target for 3s.',
    'Ghost': '+5 armor, 10% chance to dodge attacks.',
    'Ground': '25% chance: a quake deals 50% of the hit to enemies within 300 and slows them by 40% for 2s.',
    'Fairy': '20% chance: the target gets -1 Attack for 6s.',
}
KEEP_CODES = {'ACac', 'AIab', 'AIml', 'AIde', 'AIas', 'AEev', 'AIsx', 'AIim', 'AIgm', 'AIsm'}


def plan(m, script):
    """everything apply / build need, computed from the base map"""
    L = json.load(open(os.path.join(WORK, 'tools', 'learnsets.json'), encoding='utf-8'))
    moves_db = L['moves']
    stat_order = L.get('stat_order') or ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
    i_def, i_spd = stat_order.index('defense'), stat_order.index('special-defense')
    labels = {int(i): v for i, v in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script)}
    orders = {int(i): v for i, v in re.findall(r'set Mv_Ord\[(\d+)\] = OrderId\("(\w+)"\)', script)}
    texts = {int(i): v for i, v in re.findall(r'set Mv_Text\[(\d+)\] = "(.*)"\s*$', script, re.M)}
    p = {'moves': {}, 'kits': {}, 'missing': []}
    for i, lab in sorted(labels.items()):
        name = re.sub(r'\s*\(.*$', '', lab)
        info = moves_db.get(slug(name))
        if info is None or name == 'Double Team':
            if name != 'Double Team':
                p['missing'].append(name)
            continue
        rec = parse_move(name, info)
        rec['name'] = name
        if orders.get(i) == 'blizzard':  # channelled: a recharge waits for the channel to end
            rec['flags'] |= F_CHANNEL
        p['moves'][i] = rec
    abil_txt = m.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    for _i, aid in re.findall(r"set Wild_KitSkill\[(\d+)\] = '(\w{4})'", script):
        mm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % aid, abil_txt, re.S)
        nm = re.search(r'(?m)^Name=(.*)$', mm.group(1)).group(1).strip() if mm else ''
        info = moves_db.get(slug(nm))
        p.setdefault('kit_class', {})[aid] = (info or {}).get('class') or ''
        if info and info.get('class') in ('physical', 'special') and aid not in p['kits']:
            rec = parse_move(nm, info)
            rec['flags'] &= ~F_PLAIN  # kit skills keep their v1.8 effects
            rec['name'] = nm
            p['kits'][aid] = rec
    sp, names = unit_species(m, L['species'])
    p['sp'] = sp
    p['defs'] = {uid: (rec['stats'][i_def], rec['stats'][i_spd]) for uid, rec in sp.items() if rec.get('stats')}
    p['legends'] = legend_codes(names)
    p['texts'] = texts
    p['names'] = names
    return p


# ------------------------------------------------------------------ object data plan (items, abilities)
def item_plan(m, script):
    items = read_slk(m, 'Units\\ItemData.slk')
    abil = read_slk(m, 'Units\\AbilityData.slk')
    w3a = objdata.ObjFile(m.read('war3map.w3a'), leveled=True)
    w3a_code = {o.new: o.orig for o in w3a.custom}
    words = dict(re.findall(r'set Type_Word\[(\d+)\] = "(\w+)"', script))
    ids = dict(re.findall(r"set Type_Item\[(\d+)\] = '(\w{4})'", script))
    type_items = {}
    for k, word in words.items():
        type_items[T[word.lower()]] = (ids[k], word)
    type_items[T['ground']] = ('I013', 'Ground')
    type_items[T['fairy']] = ('ITFY', 'Fairy')

    def code_of(a):
        row = abil.find(a)
        return abil.get(row, 'code') if row is not None else w3a_code.get(a, '')

    out = {'type_items': {}, 'abil_lists': {}, 'prices': {}, 'unique': []}
    for t, (iid, word) in sorted(type_items.items()):
        row = items.find(iid)
        al = [a for a in (items.get(row, 'abilList') or '').split(',') if a]
        keep = [a for a in al if code_of(a) in KEEP_CODES] or ['A03A']
        if 'A03A' not in keep:
            keep.append('A03A')
        out['type_items'][t] = (iid, word)
        out['abil_lists'][iid] = keep
    out['abil_lists']['ITGD'] = ['A03A']
    names = {}
    func = m.read('Units\\ItemFunc.txt').decode('utf-8', 'replace')
    for iid, _w in out['type_items'].values():
        mm = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % iid, func, re.S)
        nm = re.search(r'(?m)^Name=(.*)$', mm.group(1)).group(1).strip() if mm else iid
        names[iid] = 'Soft Sand' if iid == 'I013' else nm
    out['item_names'] = names
    uniq = [iid for iid, _w in out['type_items'].values()] + ['ITGD']
    uniq += ['IB0%s' % c for c in '0123456789AB'] + ['IT00', 'IT01', 'IT02', 'IT06']
    for r in items.rows:
        rid = slk.Slk.unquote(r.get(1))
        if rid and re.match(r'^IM[0-9A-Z]{2}$', rid):
            uniq.append(rid)
    out['unique'] = sorted(set(uniq))
    for iid in out['unique']:
        row = items.find(iid)
        if row is not None:
            try:
                out['prices'][iid] = int(float(items.get(row, 'goldcost') or 0))
            except ValueError:
                out['prices'][iid] = 0
    if not out['prices'].get('ITFY'):
        out['prices']['ITFY'] = 3000
    return out


# ------------------------------------------------------------------ JASS data
def data_lines(p, ip, script, m):
    lines = []
    for i, rec in sorted(p['moves'].items()):
        lines += rec_lines(str(100000 + i), rec)
    for aid, rec in sorted(p['kits'].items()):
        lines += rec_lines("'%s'" % aid, rec)
    for uid, (d, s) in sorted(p['defs'].items()):
        lines.append("    call SaveInteger(Fx_HT, '%s', 1, %d)" % (uid, d))
        lines.append("    call SaveInteger(Fx_HT, '%s', 2, %d)" % (uid, s))
    for uid, code in sorted(p['legends'].items()):
        lines.append("    call SaveInteger(Fx_HT, '%s', 3, %d)" % (uid, code))
        if code in PRESSURE_TIER:
            lines.append("    call SaveInteger(Fx_HT, '%s', 4, %d)" % (uid, PRESSURE_TIER[code]))
        if code in LEGEND_AB:
            lines.append("    call SaveInteger(Ab_HT, '%s', 0, %d)" % (uid, LEGEND_AB[code]))
    for t, (iid, word) in sorted(ip['type_items'].items()):
        al = ip['abil_lists'][iid]
        lines.append("    call SaveInteger(Fx_HT, %d, 1, '%s')" % (200000 + t, iid))
        lines.append('    call SaveInteger(Fx_HT, %d, 2, %d)' % (200000 + t, len(al)))
        for k, a in enumerate(al):
            lines.append("    call SaveInteger(Fx_HT, %d, %d, '%s')" % (200000 + t, 10 + k, a))
        lines.append('    set Fx_TItemName[%d] = "%s"' % (t, ip['item_names'][iid]))
        lines.append("    call SaveInteger(Fx_HT, '%s', 1, %d)" % (iid, t + 1))
    lines.append("    call SaveInteger(Fx_HT, 'ITGD', 1, %d)" % (T['ground'] + 1))
    for iid in ip['unique']:
        lines.append("    call SaveInteger(Fx_HT, '%s', 2, 1)" % iid)
        lines.append("    call SaveInteger(Fx_HT, '%s', 3, %d)" % (iid, ip['prices'].get(iid, 0)))
    # League room
    f = lambda v: repr(float(v))  # noqa: E731
    la = league_area
    lines += ['    set Fx_LAX = %s' % f(la.ARENA[0]), '    set Fx_LAY = %s' % f(la.ARENA[1]),
              '    set Fx_LLX = %s' % f(la.LOBBY[0]), '    set Fx_LLY = %s' % f(la.LOBBY[1]),
              '    set Fx_LEX = %s' % f(la.EXIT[0]), '    set Fx_LEY = %s' % f(la.EXIT[1]),
              '    set Fx_LGX = %s' % f(la.BASE_GATE[0]), '    set Fx_LGY = %s' % f(la.BASE_GATE[1]),
              '    set Fx_LRX0 = %s' % f(la.ROOM[0]), '    set Fx_LRY0 = %s' % f(la.ROOM[1]),
              '    set Fx_LRX1 = %s' % f(la.ROOM[2]), '    set Fx_LRY1 = %s' % f(la.ROOM[3])]
    by_name = {}
    for uid, nm in p['names'].items():
        by_name.setdefault(nm, []).append(uid)
    k = 0
    for who, poke, ang in la.STATUES:
        cands = sorted(by_name.get(poke, []), key=lambda u: (u[0] not in 'EP', u))
        if not cands:
            continue
        x = la.ARENA[0] + la.STATUE_R * math.cos(math.radians(ang))
        y = la.ARENA[1] + la.STATUE_R * math.sin(math.radians(ang))
        lines += ["    set Fx_StatueType[%d] = '%s'" % (k, cands[0]), '    set Fx_StatueX[%d] = %s' % (k, f(x)),
                  '    set Fx_StatueY[%d] = %s' % (k, f(y)), '    set Fx_StatueName[%d] = "%s"' % (k, who)]
        k += 1
    lines.append('    set Fx_StatueN = %d' % k)
    # v3.4.12: the 58 status moves (move system data, action data, AI choice, learnsets)
    for k, (name, ty, act, tt, params, _cd, _mana, _icon, desc) in enumerate(SM.MOVES):
        mi = SM.STAT_BASE + k
        tname = ty.capitalize()
        lines += ['    set Mv_Label[%d] = %s' % (mi, jstr('%s (%s, status)' % (name, tname))),
                  '    set Mv_Score[%d] = 0' % mi,
                  '    set Mv_Text[%d] = %s' % (mi, jstr('%s|n|cffffcc00Status move:|r %s.' % (desc, tname))),
                  '    set Mv_D1[%d] = 0' % mi, '    set Mv_D2[%d] = 0' % mi, '    set Mv_Ord[%d] = 0' % mi,
                  '    set Mv_TT[%d] = %d' % (mi, tt), '    set Mv_Type[%d] = %d' % (mi, T[ty]),
                  '    set Mv_Pow[%d] = 0' % mi, '    set Mv_Phys[%d] = 2' % mi,
                  '    set Fx_SName[%d] = %s' % (k, jstr(name)),
                  '    call SaveInteger(Fx_HT, %d, 40, %d)' % (100000 + mi, act)]
        for key, val in sorted(params.items()):
            lines.append('    call SaveInteger(Fx_HT, %d, %d, %d)' % (100000 + mi, key, val))
    lines.append('    set Mv_N = %d' % (SM.STAT_BASE + len(SM.MOVES)))
    for ty, name in SM.AI_MOVE.items():
        lines.append('    set Fx_AiMove[%d] = %d' % (T[ty], SM.index_of(name)))
        lines.append('    set Fx_AiEasy[%d] = %d' % (T[ty], SM.index_of(SM.AI_EASY[ty])))
    # v3.4.13: the kit skill each type gives up for its status move button (one that deals no damage, else the 5th)
    kit = {int(i): a for i, a in re.findall(r"set Wild_KitSkill\[(\d+)\] = '(\w{4})'", script)}
    p['kit_drop'] = {}
    for kt in range(18):
        skills = [kit.get(kt * 5 + j) for j in range(5) if kit.get(kt * 5 + j)]
        if not skills:
            continue
        cands = [a for a in skills if p.get('kit_class', {}).get(a) == 'status']
        drop = cands[0] if cands else skills[-1]
        p['kit_drop'][kt] = drop
        lines.append("    set Fx_KitDrop[%d] = '%s'" % (kt, drop))
    slugs = {slug(mv[0]): SM.STAT_BASE + k for k, mv in enumerate(SM.MOVES)}
    n_lv = n_tm = 0
    for uid, rec in sorted(p['sp'].items()):
        if uid[0] not in 'EP':
            continue
        lv_moves = {}
        for lvl, mslug in rec.get('moves', []):
            if mslug in slugs and mslug not in lv_moves:
                lv_moves[mslug] = max(1, int(lvl))
        for mslug, mi in slugs.items():
            if mslug in lv_moves:
                lines.append("    call Fx_AddLv('%s', %d, %d)" % (uid, mi, lv_moves[mslug]))
                n_lv += 1
            elif mslug in (rec.get('tm') or []):
                lines.append("    call Fx_AddTm('%s', %d)" % (uid, mi))
                n_tm += 1
    p['learn_counts'] = (n_lv, n_tm)
    # Darkrai: a random legend now (its room is the League)
    lines += ["    set Leg_Type[Leg_N] = 'nL19'", "    set Leg_Soul[Leg_N] = 'I01F'", '    set Leg_Name[Leg_N] = "Darkrai"',
              '    set Leg_N = Leg_N + 1', "    call SaveInteger(Ab_HT, 'nL19', 0, AB_BADDREAMS)",
              "    call SaveInteger(Ab_HT, 'nL19', 53, LoadInteger(Ab_HT, 'n00F', 53))",
              "    call SaveInteger(Ab_HT, 'nL19', 54, LoadInteger(Ab_HT, 'n00F', 54))"]
    return lines


def jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def texts_function(script):
    old = {int(i): v for i, v in re.findall(r'set Ab_Info\[(\d+)\] = "(.*)"\s*$', script, re.M)}
    out = ['function Fx_Texts takes nothing returns nothing', '    set Ab_N = 78']
    for idx, name, info in NEW_ABILITIES:
        out += ['    set Ab_Name[%d] = %s' % (idx, jstr(name)), '    set Ab_Info[%d] = %s' % (idx, jstr(info)),
                '    call BlzSetAbilityTooltip(Ab_InfoId(%d), %s, 0)' % (idx, jstr('Ability: |cffffcc00%s|r' % name)),
                '    call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), %s, 0)' % (idx, jstr(info))]
    for idx, (how, txt) in sorted(AB_TEXTS.items()):
        new = txt if how == 'set' else (old.get(idx, '').replace('\\"', '"') + ' ' + txt).strip()
        out += ['    set Ab_Info[%d] = %s' % (idx, jstr(new)),
                '    call BlzSetAbilityExtendedTooltip(Ab_InfoId(%d), %s, 0)' % (idx, jstr(new))]
    out.append('endfunction')
    return out


def chunk_functions(lines, prefix, n_funcs):
    size = max(1, (len(lines) + n_funcs - 1) // n_funcs)
    out = []
    for k in range(n_funcs):
        out.append('function %s%d takes nothing returns nothing' % (prefix, k + 1))
        out += lines[k * size:(k + 1) * size]
        out.append('endfunction')
    return out


# ------------------------------------------------------------------ tooltips of the moves
CC_RX = [r' and stuns it for [\d.]+ seconds', r' and stuns for [\d.]+ seconds',
         r' and slows it by \d+% for [\d.]+ seconds', r', slowing for [\d.]+ seconds', r' and slows(?=\.)',
         r' and a [\d.]+ second stun']


def new_move_text(old, rec):
    m = re.match(r'(.*?)(\|n\|cffffcc00(Physical|Special) move:\|r)(.*)$', old)
    if not m:
        return old
    base, cls, rest = m.group(1), m.group(3), m.group(4)
    for rx in CC_RX:
        base = re.sub(rx, '', base)
    scale = ' (STR, vs Def)' if cls == 'Physical' else ' (INT, vs Sp. Def)'
    s = base + '|n|cffffcc00%s move%s:|r%s' % (cls, scale, rest)
    eff = describe(rec)
    if eff:
        s += '|n|cff99ccffEffect:|r ' + eff
    return s


# ------------------------------------------------------------------ script patches
def rep(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise SystemExit('patch: expected %d match(es), found %d:\n%s' % (count, n, old[:300]))
    return s.replace(old, new)


def rename_locals(s, fname, pairs):
    head = s.find('function %s takes' % fname)
    end = s.find('endfunction', head)
    if head < 0:
        raise SystemExit('function %s not found' % fname)
    body = s[head:end]
    for a, b in pairs:
        body = re.sub(r'\b%s\b' % a, b, body)
    return s[:head] + body + s[end:]


def patch_script(s):
    # 3.4.10 pjass errors: locals named like v1.8 functions
    s = rename_locals(s, 'Mv_Fire', [('s2', 'mvSlot2'), ('m2', 'mvMove2'), ('ra', 'mvReal2')])
    s = rename_locals(s, 'Mv_CloneSpawn', [('sc', 'cloneScale')])
    # damage: PvP into the League, physical / special stat, engine multiplier, after-hit, last word
    s = rep(s, '    set tp = GetOwningPlayer(t)\n    set atk = BlzGetEventIsAttack()\n',
            '    set tp = GetOwningPlayer(t)\n'
            '    if Fx_LeagueBlock(src, t) then  // v3.4.11: no PvP into an Elite Four battle\n'
            '        call BlzSetEventDamage(0.0)\n        set t = null\n        set src = null\n'
            '        set sp = null\n        set tp = null\n        return false\n    endif\n'
            '    set atk = BlzGetEventIsAttack()\n')
    s = rep(s, '            set stat = Ab_MainStat(src)\n        else\n            set stat = Ab_PlayerStat(sp)',
            '            set stat = Fx_SkillStat(src)  // v3.4.11: STR for physical moves, INT for special moves\n'
            '        else\n            set stat = Ab_PlayerStat(sp)')
    s = rep(s, '    set m = m * Ext_DamageMult(src, t, atk, skill, mt, eff)  // v3.4 weather, items, Champion Aura, legend Mega',
            '    set m = m * Fx_Cap(Ext_DamageMult(src, t, atk, skill, mt, eff) * Fx_OutMult(src, t, atk, skill, mt))'
            '  // v3.4.11: + stages, statuses, move effects, Def / Sp. Def, type item (capped x3)')
    s = rep(s, '        call Ext_AfterHit(src, t, atk, dmg * m)\n',
            '        call Ext_AfterHit(src, t, atk, dmg * m)\n'
            '        call Fx_AfterHit(src, t, atk, skill, mt, dmg * m)  // v3.4.11\n')
    s = rep(s, '    set m = Ext_Final(t, dmg * m) / dmg  // v3.4 Focus Sash\n',
            '    set m = Ext_Final(t, dmg * m) / dmg  // v3.4 Focus Sash\n'
            '    set m = Fx_Final(src, t, dmg * m) / dmg  // v3.4.11: Mewtwo shield, Ho-Oh rebirth, Regirock Sturdy\n')
    # cast hook
    s = rep(s, '            set Ty_PPhys[pid] = ph\n        endif\n    endif\n',
            '            set Ty_PPhys[pid] = ph\n        endif\n    endif\n'
            '    set Fx_ArgU = u  // v3.4.11: move effects, Pressure, cooldowns\n    set Fx_ArgI = m\n'
            '    set Fx_ArgJ = id\n    set Fx_ArgV = GetSpellTargetUnit()\n    call ExecuteFunc("Fx_OnCastX")\n')
    # v3.4.13: elites / legends / gym Pokemon: one kit skill becomes the button of their status move
    s = rep(s, '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\n',
            '        call SaveInteger(Ab_HT, GetHandleId(u), 87, k)  // v3.4: Ai_Tick casts them\n'
            '        set Fx_ArgU = u  // v3.4.13: a status move button in place of one kit skill\n'
            '        set Fx_ArgK = k - 1\n        set Fx_ArgJ = -1\n        call ExecuteFunc("Fx_KitStatusX")\n')
    s = rep(s, '    call SaveInteger(Ab_HT, GetHandleId(u), 87, kit)\nendfunction',
            '    call SaveInteger(Ab_HT, GetHandleId(u), 87, kit)\n'
            '    set Fx_ArgU = u  // v3.4.13: a status move button in place of one kit skill\n'
            '    set Fx_ArgK = kit - 1\n    set Fx_ArgJ = -1\n    call ExecuteFunc("Fx_KitStatusX")\nendfunction')
    s = rep(s, '        call SaveInteger(Ab_HT, h, 87, kt + 1)  // Ai_Tick casts these skills (the creep AI never does)\n',
            '        call SaveInteger(Ab_HT, h, 87, kt + 1)  // Ai_Tick casts these skills (the creep AI never does)\n'
            '        set Fx_ArgU = u  // v3.4.13: a status move button in place of one kit skill\n'
            '        set Fx_ArgK = kt\n        set Fx_ArgJ = g\n        call ExecuteFunc("Fx_KitStatusX")\n')
    # speeds
    s = rep(s, '        set pct = pct * LoadReal(Ab_HT, h, 84)\n    endif\n',
            '        set pct = pct * LoadReal(Ab_HT, h, 84)\n    endif\n    set pct = pct * Fx_ASMult(u)  // v3.4.11\n')
    s = rep(s, '    if b != LoadReal(Ab_HT, h, 83) and Ab_FxFind(u, 2) < 0 then',
            '    set b = b + Fx_MSBonus(u)  // v3.4.11: Speed stage\n'
            '    if b != LoadReal(Ab_HT, h, 83) and Ab_FxFind(u, 2) < 0 then')
    # silence: the creep AI does not cast
    s = rep(s, '    if abil == 0 or orderstr == null or orderstr == "" or GetUnitAbilityLevel(u, abil) <= 0 then',
            '    if abil == 0 or orderstr == null or orderstr == "" or GetUnitAbilityLevel(u, abil) <= 0 or Fx_Silenced(u) then')
    # Choice Band / Specs / Assault Vest follow the move class
    s = rep(s, '        if atk and Itm_Flag(src, 1) then',
            '        if (atk or (skill and Fx_CurPhys(src) == 1)) and Itm_Flag(src, 1) then  // v3.4.11')
    s = rep(s, '        if skill and Itm_Flag(src, 2) then',
            '        if skill and Fx_CurPhys(src) == 2 and Itm_Flag(src, 2) then  // v3.4.11')
    s = rep(s, '        if skill and Itm_Flag(t, 8) then',
            '        if skill and Fx_CurPhys(src) == 2 and Itm_Flag(t, 8) then  // v3.4.11')
    # charging moves
    s = rep(s, '    call TimerStart(t, 0.0, false, function Mv_Dispatch)',
            '    call TimerStart(t, Fx_QueueDelay(u, Mv_Slot(u, s)), false, function Mv_Dispatch)  // v3.4.11 charge')
    s = rep(s, '            call Mv_Fire(u, s, tgt, LoadReal(Ab_HT, k, 3), LoadReal(Ab_HT, k, 4), LoadInteger(Ab_HT, k, 5))',
            '            call Fx_ChargeEnd(u)\n'
            '            call Mv_Fire(u, s, tgt, LoadReal(Ab_HT, k, 3), LoadReal(Ab_HT, k, 4), LoadInteger(Ab_HT, k, 5))')
    # gym / Elite Four type items
    s = rep(s, '    // v3.4.3: no held type item any more (the v1.8 pickup triggers dropped it or evolved the Pokemon)\n',
            '    set Fx_ArgU = u  // v3.4.11: the type item\'s abilities, no real item (nothing to drop)\n'
            '    set Fx_ArgI = ty\n    set Fx_ArgJ = g\n    call ExecuteFunc("Fx_GymItemX")\n')
    # League: its own arena in Darkrai's room, a queue, 30s retry, next in queue
    s = rep(s, '    elseif League_Pid >= 0 or Gym_Pid[7] >= 0 then\n'
               '        call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00The League arena (gym 8) is busy. Try again soon.|r")',
            '    elseif League_Pid >= 0 then  // v3.4.11: queue\n'
            '        set Fx_ArgI = pid\n        call ExecuteFunc("Fx_LeagueQueueX")')
    s = rep(s, '        set Gym_X[8] = Gym_X[7]\n        set Gym_Y[8] = Gym_Y[7]\n',
            '        set Gym_X[8] = Fx_LAX  // v3.4.11: the arena in Darkrai\'s room\n        set Gym_Y[8] = Fx_LAY\n')
    s = rep(s, ' Try again in 60 seconds.|r")\n    set League_Cool[League_Pid] = Mega_Time + 60.0',
            ' Try again in 30 seconds.|r")\n    set League_Cool[League_Pid] = Mega_Time + 30.0')
    s = rep(s, '    set League_Pid = -1\n    set League_Unit = null\nendfunction',
            '    set League_Pid = -1\n    set League_Unit = null\n    call ExecuteFunc("Fx_LeagueNextX")  // v3.4.11\nendfunction')
    s = rep(s, "    elseif it == 'IL01' then\n        call SetUnitPosition(b, -9600.0, -2209.0)",
            "    elseif it == 'IL01' then\n        call SetUnitPosition(b, Fx_LLX, Fx_LLY)  // v3.4.11: the Pokemon League lobby")
    s = rep(s, '                call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), Ext_Shop[k], x, y, 90.0)\n',
            '                call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), Ext_Shop[k], x, y, 90.0)\n'
            '                if k == 1 then  // v3.4.11: the League portal goes next to the Item Shop\n'
            '                    set Fx_GateX[side] = x\n                    set Fx_GateY[side] = y\n'
            '                endif\n')
    # one of each held item
    s = rep(s, '    if IsUnitType(GetTriggerUnit(), UNIT_TYPE_HERO) then\n        call Itm_Refresh(GetTriggerUnit())\n    endif\n',
            '    if IsUnitType(GetTriggerUnit(), UNIT_TYPE_HERO) then\n        call Itm_Refresh(GetTriggerUnit())\n'
            '        call Fx_OnPickup(GetTriggerUnit(), GetManipulatedItem())  // v3.4.11\n    endif\n')
    # -stats
    s = rep(s, ' + " | wild tier " + I2S(Wild_Tier))\n    endif\n',
            ' + " | wild tier " + I2S(Wild_Tier))\n        call Fx_Stats(p, h)  // v3.4.11\n    endif\n')
    # Abilities
    s = rep(s, '    elseif a == AB_RECKLESS then\n        set m = 1.35\n',
            '    elseif a == AB_RECKLESS then  // v3.4.11\n        if atk then\n            set m = 1.15\n'
            '        elseif skill and (LoadInteger(Fx_HT, Fx_CurMove(src), 2) > 0) then\n            set m = 1.3\n'
            '        endif\n')
    s = rep(s, '        if atk and (r < 0.5 or Ab_HasBad(src)) then\n            set m = 1.4\n',
            '        if (atk or (skill and Ty_CurPhys == 1)) and Fx_HasStatus(src) then  // v3.4.11\n            set m = 1.5\n')
    s = rep(s, '        if atk then\n            set m = 1.4\n        elseif skill and Ty_CurPhys == 1 then\n            set m = 1.2\n',
            '        if atk then  // v3.4.11 Tough Claws\n            set m = 1.3\n        elseif skill and Ty_CurPhys == 1 then\n'
            '            set m = 1.3\n')
    s = rep(s, '    elseif a == AB_MEGALAUNCHER then\n        if skill and Ty_CurPhys == 2 then\n            set m = 1.4\n',
            '    elseif a == AB_MEGALAUNCHER then  // v3.4.11\n        if skill and Fx_MoveHas(src, 524288) then\n'
            '            set m = 1.5\n        elseif skill and Ty_CurPhys == 2 then\n            set m = 1.15\n')
    s = rep(s, '    elseif a == AB_STRONGJAW then\n        if atk then\n            set m = 1.3\n        endif\n',
            '    elseif a == AB_STRONGJAW then\n        if atk then\n            set m = 1.3\n'
            '        elseif skill and Fx_MoveHas(src, 262144) then  // v3.4.11 biting moves\n            set m = 1.4\n'
            '        endif\n')
    s = rep(s, '    elseif a == AB_SKILLLINK then\n        if skill then\n            set m = 1.2\n',
            '    elseif a == AB_SKILLLINK then\n        if skill and Fx_MoveHas(src, 8) then  // v3.4.11 multi-hit: 5 hits\n'
            '            set m = 1.5\n        elseif skill then\n            set m = 1.2\n')
    s = rep(s, '        if Mega_Time - LoadReal(Ab_HT, h, 9) < 30.0 then\n            set m = 0.6\n        else\n            set m = 1.4\n',
            '        if Mega_Time - LoadReal(Ab_HT, h, 9) < 15.0 then  // v3.4.11\n            set m = 0.7\n        else\n'
            '            set m = 1.5\n')
    s = rep(s, '        elseif a == AB_SANDVEIL or a == AB_SNOWCLOAK or a == AB_LEAFGUARD or a == AB_INSOMNIA then\n            set dodge = 0.2\n',
            '        elseif a == AB_LEAFGUARD or a == AB_INSOMNIA then\n            set dodge = 0.2\n'
            '        elseif a == AB_SANDVEIL or a == AB_SNOWCLOAK then  // v3.4.11: 10%, 30% in their weather\n'
            '            set dodge = 0.1\n')
    s = rep(s, '            set dodge = dodge + 0.15\n', '            set dodge = dodge + 0.2\n')
    s = rep(s, '    elseif a == AB_ROCKHEAD then\n        if atk and GetRandomReal(0.0, 1.0) < 0.15 then\n',
            '    elseif a == AB_ROCKHEAD then  // v3.4.11: no recoil instead of the stun\n        if false then\n')
    s = rep(s, '        if GetWidgetLife(src) - 0.05 * d > 1.0 then\n            call SetWidgetLife(src, GetWidgetLife(src) - 0.05 * d)\n        endif\n',
            '        // v3.4.11: Reckless no longer hurts the user\n')
    s = rep(s, '    elseif a == AB_POISONPOINT then\n        if atk and GetRandomReal(0.0, 1.0) < 0.25 then\n            call Ab_Poison(src, t)\n        endif\n',
            '    elseif a == AB_POISONPOINT then\n        if atk then  // v3.4.11: 30% poison status\n'
            '            set Fx_ArgU = t\n            set Fx_ArgV = src\n            set Fx_ArgI = 2\n            set Fx_ArgJ = 30\n'
            '            call ExecuteFunc("Fx_StatusX")\n        endif\n')
    # contact: Static / Flame Body / Poison Point give statuses (30%)
    s = rep(s, '    if a == AB_STATIC then\n        if GetRandomReal(0.0, 1.0) < 0.2 then\n            call Ab_Chain(t, src, Ab_ProcDmg(t))\n        endif\n'
               '    elseif a == AB_FLAMEBODY then\n        if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then\n'
               '            set Ab_FxCur = t\n            call Ab_FxAdd(src, 1, 3.0, 0.01 * mx)\n            set Ab_FxCur = null\n        endif\n'
               '    elseif a == AB_POISONPOINT then\n        if GetRandomReal(0.0, 1.0) < 0.25 then\n            call Ab_Poison(t, src)\n        endif\n',
            '    if a == AB_STATIC or a == AB_FLAMEBODY or a == AB_POISONPOINT then  // v3.4.11: 30% status on the attacker\n'
            '        if IsUnitType(src, UNIT_TYPE_MELEE_ATTACKER) then\n            set Fx_ArgU = src\n            set Fx_ArgV = t\n'
            '            set Fx_ArgI = 4\n            if a == AB_FLAMEBODY then\n                set Fx_ArgI = 1\n'
            '            elseif a == AB_POISONPOINT then\n                set Fx_ArgI = 2\n            endif\n'
            '            set Fx_ArgJ = 30\n            call ExecuteFunc("Fx_StatusX")\n        endif\n')
    # Intimidate: -1 Attack (stage) to enemies within 500
    s = rep(s, '    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(u), GetUnitY(u), 600.0, null)\n    loop\n        set v = FirstOfGroup(Ab_Group)\n'
               '        exitwhen v == null\n        call GroupRemoveUnit(Ab_Group, v)\n'
               '        if Ab_Alive(v) and IsUnitEnemy(v, p) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then\n'
               '            call SaveReal(Ab_HT, GetHandleId(v), 5, Mega_Time + 6.0)\n            call SaveReal(Ab_HT, GetHandleId(v), 6, 0.25)\n'
               '            call Ab_FxAdd(v, 5, 6.0, 5.0)\n',
            '    call GroupEnumUnitsInRange(Ab_Group, GetUnitX(u), GetUnitY(u), 500.0, null)  // v3.4.11\n    loop\n'
            '        set v = FirstOfGroup(Ab_Group)\n        exitwhen v == null\n        call GroupRemoveUnit(Ab_Group, v)\n'
            '        if Ab_Alive(v) and IsUnitEnemy(v, p) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) then\n'
            '            set Fx_ArgU = v\n            set Fx_ArgV = u\n            call ExecuteFunc("Fx_IntimidateX")\n')
    # Speed Boost works through the Speed stage now
    s = rep(s, '        set b = 10.0 * I2R(LoadInteger(Ab_HT, h, 62))\n', '        set b = 0.0  // v3.4.11: Speed stage\n')
    s = rep(s, '        set m = 1.0 + 0.08 * I2R(LoadInteger(Ab_HT, h, 62))\n', '        set m = 1.0  // v3.4.11: Speed stage\n')
    # v3.4.12: status move buttons are the move (like Double Team); the level-up auto-learn skips them
    s = rep(s, '            if m == Mv_DoubleTeam then\n                call Mv_DoubleTeamCast(u)\n            elseif Mv_Ord[m] != 0 then\n',
            '            if m == Mv_DoubleTeam then\n                call Mv_DoubleTeamCast(u)\n'
            '            elseif m >= Fx_StatBase then  // v3.4.12: status moves\n                set Fx_ArgU = u\n'
            '                set Fx_ArgV = GetSpellTargetUnit()\n                set Fx_ArgI = m\n'
            '                call ExecuteFunc("Fx_StatusMoveX")\n            elseif Mv_Ord[m] != 0 then\n')
    s = rep(s, '            if LoadInteger(Ab_HT, h, 200 + m) == 0 then\n                if Mv_Known(u, m) then\n',
            '            if LoadInteger(Ab_HT, h, 200 + m) == 0 and m < Fx_StatBase then  // v3.4.12: status moves only at the NPC\n'
            '                if Mv_Known(u, m) then\n')
    s = rep(s, '    return out + "|n|cff66ff66Damage now x"',
            '    if Mv_Pow[m] <= 0 then  // v3.4.12: status moves deal no damage\n        return out\n    endif\n'
            '    return out + "|n|cff66ff66Damage now x"')
    s = rep(s, '    if BlzGetUnitAbilityCooldownRemaining(u, abil) > 0.0 then\n        return false\n    endif\n    // unit target',
            '    if BlzGetUnitAbilityCooldownRemaining(u, abil) > 0.0 then\n        return false\n    endif\n'
            '    if ModuloInteger(LoadInteger(Fx_HT, abil, 1), 2) == 1 and t != null and GetWidgetLife(t) > 0.35 * I2R(BlzGetUnitMaxHP(t)) then\n'
            '        return false  // v3.4.12: the AI keeps recharge moves to finish a target\n    endif\n    // unit target')
    # v3.4.14: a slow on a hero ends at default speed + its current bonus (Ab_MoveBonus, key 83), not at the speed
    # saved when the slow began (that one could be stale after a Mega / Ability change: a slow for good)
    s = rep(s, '        if LoadReal(Ab_HT, h, 11) > 0.0 then\n            call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11))\n        endif\n'
               '        call SaveReal(Ab_HT, h, 11, 0.0)\n',
            '        if IsUnitType(u, UNIT_TYPE_HERO) then  // v3.4.14: no stale speed for heroes\n'
            '            call SetUnitMoveSpeed(u, GetUnitDefaultMoveSpeed(u) + LoadReal(Ab_HT, h, 83))\n'
            '        elseif LoadReal(Ab_HT, h, 11) > 0.0 then\n            call SetUnitMoveSpeed(u, LoadReal(Ab_HT, h, 11))\n        endif\n'
            '        call SaveReal(Ab_HT, h, 11, 0.0)\n')
    # init
    s = rep(s, '    call PkFx_Init()  // v3.4.9\n',
            '    call PkFx_Init()  // v3.4.9\n    call ExecuteFunc("Fx_Init")  // v3.4.11\n')
    s = rep(s, 'call SetMapName("Pokemon Arena v3.4.10")', 'call SetMapName("Pokemon Arena v%s")' % VERSION)
    return s


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    m = mpq.MPQ(BASE_MAP)
    script = m.read('scripts\\war3map.j').decode('latin-1')
    script = script.replace('\r\n', '\n')
    p = plan(m, script)
    ip = item_plan(m, script)
    s = patch_script(script)
    # move tooltips
    def fix_text(mt):
        i = int(mt.group(1))
        rec = p['moves'].get(i)
        return mt.group(0) if rec is None else 'set Mv_Text[%d] = "%s"' % (i, new_move_text(mt.group(2), rec))
    s, n_txt = re.subn(r'set Mv_Text\[(\d+)\] = "(.*)"(?=\s*$)', fix_text, s, flags=re.M)
    left = [t for t in re.findall(r'set Mv_Text\[\d+\] = "(.*)"', s) if re.search(r'stun|slow', t.split('|n')[0])]
    # code
    jdir = os.path.join(HERE, 'jass')
    glob = open(os.path.join(jdir, 'fx_globals.j'), encoding='utf-8').read()
    core = open(os.path.join(jdir, 'fx_core.j'), encoding='utf-8').read()
    main_j = open(os.path.join(jdir, 'fx_main.j'), encoding='utf-8').read()
    data = data_lines(p, ip, script, m)
    data_j = '\n'.join(chunk_functions(data, 'Fx_Data', 12) + texts_function(script)) + '\n'
    eg = re.search(r'(?m)^endglobals', s)
    if not eg:
        raise SystemExit('endglobals not found')
    s = s[:eg.start()] + glob + s[eg.start():]
    s = rep(s, 'function Hero_HPSync takes', core + '\nfunction Hero_HPSync takes')
    s = rep(s, 'function Ext_AfterHit takes', main_j + '\nfunction Ext_AfterHit takes')
    s = rep(s, 'function Mega_Init takes', data_j + 'function Mega_Init takes')
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, 'war3map.j')
    open(out, 'w', encoding='latin-1', newline='\n').write(s)
    summary = {'moves': len(p['moves']), 'kits': len(p['kits']), 'defs': len(p['defs']), 'legends': len(p['legends']),
               'missing': p['missing'], 'tooltips': n_txt, 'cc_words_left': left[:10],
               'status_moves': len(SM.MOVES), 'status_learn_level_tm': p.get('learn_counts'),
               'groups': {}}
    for rec in p['moves'].values():
        for name, bit in (('plain', F_PLAIN), ('recharge', F_RECHARGE), ('charge', F_CHARGE), ('prio', F_PRIO),
                          ('multi', F_MULTI), ('crit', F_CRIT)):
            if rec['flags'] & bit:
                summary['groups'][name] = summary['groups'].get(name, 0) + 1
        for k in ('status', 'flinch', 'recoil', 'drain', 'self', 'target'):
            if k in rec:
                summary['groups'][k] = summary['groups'].get(k, 0) + 1
    json.dump({'moves': {str(k): v for k, v in p['moves'].items()}, 'items': ip, 'version': VERSION},
              open(os.path.join(OUT_DIR, 'plan.json'), 'w', encoding='utf-8'), indent=1, default=list)
    print(json.dumps(summary, indent=1))
    print('wrote', out, len(s), 'chars')


if __name__ == '__main__':
    main()
