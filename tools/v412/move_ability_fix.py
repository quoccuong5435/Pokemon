"""Move and Ability fixes from PokeAPI data for the v4.2x line (script patch, no object data).

Found by analysis/move_ability_audit.py (map moves vs tools/pokeapi/moves.json, hero Abilities vs
tools/pokeapi/pokemon_abilities.json). Accuracy and PP are not used on purpose (the user's decision, 2026-11-22).

What patch(script) changes:
1. Confusion of damaging moves: the tooltips of Confusion, Dynamic Punch, Hurricane, Psybeam and Water Pulse said
   "x% confusion" but the chance was never stored, so these moves never confused. New move key 9 = confusion chance,
   read in Fx_AfterHit next to the flinch roll (Fx_Confuse 3 s, doubled by Serene Grace like the other chances).
2. Move effects that were missing or wrong (16 moves): Ancient Power, Bounce, Chilling Water, Facade, Freeze-Dry,
   Pounce, Rapid Spin, Scorching Sands, Sky Attack, Trailblaze, Venoshock + the 5 moves of point 1. Each move's record
   (Fx_HT key 100000 + move index) is checked against the expected old value first, then rewritten.
3. Double Team (move 319) had type Bug (Mv_Type 0); it is Normal.
4. (removed) Ability changes of heroes now come from tools/v412/ability_rw.py (the full approved rework).

Usage from a build script:  import move_ability_fix;  script = move_ability_fix.patch(script)
Each anchor must be found exactly once (or the old record must match), otherwise ValueError: nothing is guessed.
"""
import re

T_NORMAL = 12

# move index -> (label prefix, old record, new record, old effect text, new effect text or None)
# record keys: 1 flags, 2 recoil, 3 drain, 4 status, 5 status chance, 6 flinch, 7 self chance, 9 confusion chance,
# 8 target chance, 10 + s self stage, 20 + s target stage, 26 accuracy down, 30 class (s: 1 Atk 2 Def 3 SpA 4 SpD 5 Spe)
MOVES = {
    9: ('Ancient Power', {1: 4096, 30: 2},
        {7: 10, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 30: 2},
        'No extra effect: +10% damage.',
        'User +1 Attack, +1 Defense, +1 Sp. Atk, +1 Sp. Def, +1 Speed (10%).'),
    29: ('Bounce', {1: 1048580, 30: 1},
         {1: 1048580, 4: 4, 5: 30, 30: 1},
         'The user is out of reach for 1s.',
         'The user is out of reach for 1s; 30% paralysis.'),
    43: ('Chilling Water', {1: 4096, 30: 2},
         {8: 100, 21: -1, 30: 2},
         'No extra effect: +10% damage.',
         'Target -1 Attack (100%).'),
    46: ('Confusion', {30: 2}, {9: 10, 30: 2}, '10% confusion.', None),
    78: ('Dynamic Punch', {1: 1179648, 30: 1}, {1: 1179648, 9: 100, 30: 1}, '100% confusion.', None),
    90: ('Facade', {1: 1050624, 4: 1, 5: 10, 30: 1},
         {1: 1050624, 30: 1},
         '10% burn; double damage if the user has a status.',
         'Double damage if the user has a status.'),
    113: ('Freeze Dry', {1: 4096, 30: 2},
          {4: 6, 5: 10, 30: 2},
          'No extra effect: +10% damage.',
          '10% freeze.'),
    134: ('Hurricane', {30: 2}, {9: 30, 30: 2}, '30% confusion.', None),
    202: ('Pounce', {1: 1052672, 30: 1},
          {1: 1048576, 8: 100, 25: -1, 30: 1},
          'No extra effect: +10% damage.',
          'Target -1 Speed (100%).'),
    208: ('Psybeam', {30: 2}, {9: 10, 30: 2}, '10% confusion.', None),
    221: ('Rapid Spin', {1: 1052672, 30: 1},
          {1: 1048576, 7: 100, 15: 1, 30: 1},
          'No extra effect: +10% damage.',
          'User +1 Speed.'),
    239: ('Scorching Sands', {4: 1, 5: 10, 30: 2},
          {4: 1, 5: 30, 30: 2},
          '10% burn.',
          '30% burn.'),
    249: ('Sky Attack', {1: 1048578, 6: 30, 30: 1},
          {1: 1048594, 6: 30, 30: 1},
          'Charges 1.2s first; 30% flinch.',
          'Charges 1.2s first; high critical rate; 30% flinch.'),
    290: ('Trailblaze', {1: 1052672, 30: 1},
          {1: 1048576, 7: 100, 15: 1, 30: 1},
          'No extra effect: +10% damage.',
          'User +1 Speed.'),
    299: ('Venoshock', {4: 2, 5: 10, 30: 2},
          {1: 4096, 30: 2},
          '10% poison.',
          'No extra effect: +10% damage.'),
    306: ('Water Pulse', {1: 524288, 30: 2}, {1: 524288, 9: 20, 30: 2}, '20% confusion.', None),
}
KEY_ORDER = [1, 2, 3, 4, 5, 9, 6, 7, 11, 12, 13, 14, 15, 8, 21, 22, 23, 24, 25, 26, 30, 31]

# hero id -> (name, old Ability name, new Ability name); the new one is a real Ability of the species (PokeAPI)
ABILITIES = {}  # superseded 2026-11-22: tools/v412/ability_rw.py sets every hero's approved default Ability

FLINCH_ANCHOR = '        set chance = LoadInteger(Fx_HT, mkey, 6) * grace'
CONFUSE_LINES = [
    '        set chance = LoadInteger(Fx_HT, mkey, 9) * grace  // v4.2x: confusion chance of damaging moves',
    '        if chance > 0 and GetRandomInt(1, 100) <= chance then',
    '            call Fx_Confuse(t, 3.0, src)',
    '        endif',
]


def _eol(line):
    return line[len(line.rstrip('\r\n')):] or '\n'


def _one(lines, pred, what):
    hits = [i for i, ln in enumerate(lines) if pred(ln)]
    if len(hits) != 1:
        raise ValueError('[move_ability_fix] %s: found %d times' % (what, len(hits)))
    return hits[0]


def _ability_index(script):
    out = {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', script):
        out.setdefault(m.group(2), int(m.group(1)))
    return out


def patch(script):
    lines = re.findall(r'[^\n]*\n|[^\n]+$', script)  # split on LF only (the v1.8 part has bare CR)

    # 1. confusion roll before the flinch roll
    if any('LoadInteger(Fx_HT, mkey, 9)' in ln for ln in lines):
        raise ValueError('[move_ability_fix] move key 9 is already read: patch applied twice?')
    i = _one(lines, lambda ln: ln.rstrip('\r\n') == FLINCH_ANCHOR, 'flinch anchor')
    eol = _eol(lines[i])
    lines[i:i] = [ln + eol for ln in CONFUSE_LINES]

    # 2. move records and tooltips
    for idx, (label, old, new, old_txt, new_txt) in MOVES.items():
        _one(lines, lambda ln: ln.lstrip().startswith('set Mv_Label[%d] = "%s (' % (idx, label)), 'label of move %d' % idx)
        key = 100000 + idx
        pat = re.compile(r'\s*call SaveInteger\(Fx_HT, %d, (\d+), (-?\d+)\)\s*$' % key)
        at = [n for n, ln in enumerate(lines) if pat.match(ln)]
        if not at:
            raise ValueError('[move_ability_fix] record of move %d (%s) missing' % (idx, label))
        have = {int(pat.match(lines[n]).group(1)): int(pat.match(lines[n]).group(2)) for n in at}
        if have != old:
            raise ValueError('[move_ability_fix] move %d (%s) record is %s, expected %s' % (idx, label, have, old))
        indent = lines[at[0]][:len(lines[at[0]]) - len(lines[at[0]].lstrip())]
        eol = _eol(lines[at[0]])
        block = [indent + 'call SaveInteger(Fx_HT, %d, %d, %d)' % (key, k, new[k]) + eol for k in KEY_ORDER if k in new]
        if set(new) - set(KEY_ORDER):
            raise ValueError('[move_ability_fix] unknown key in move %d' % idx)
        # a record can be split between two Fx_DataN functions: drop every old line, put the new block at the first
        for n in reversed(at[1:]):
            del lines[n]
        lines[at[0]:at[0] + 1] = block
        if new_txt is not None:
            t = _one(lines, lambda ln: ln.lstrip().startswith('set Mv_Text[%d] = "' % idx), 'text of move %d' % idx)
            body = lines[t].rstrip('\r\n')
            tail = 'Effect:|r ' + old_txt + '"'
            if not body.endswith(tail):
                raise ValueError('[move_ability_fix] text of move %d does not end with %r' % (idx, tail))
            lines[t] = body[:-len(tail)] + 'Effect:|r ' + new_txt + '"' + _eol(lines[t])

    # 3. Double Team is Normal
    t = _one(lines, lambda ln: ln.strip() == 'set Mv_Type[319] = 0', 'Mv_Type[319]')
    lines[t] = lines[t].replace('= 0', '= %d' % T_NORMAL)

    # 4. real Abilities
    text = ''.join(lines)
    index = _ability_index(text)
    for hid, (name, old_name, new_name) in ABILITIES.items():
        if old_name not in index or new_name not in index:
            raise ValueError('[move_ability_fix] Ability %s or %s not in the map' % (old_name, new_name))
        old_line = "call SaveInteger(Ab_HT, '%s', 0, %d)" % (hid, index[old_name])
        if text.count(old_line) != 1 or text.count("call SaveInteger(Ab_HT, '%s', 0, " % hid) != 1:
            raise ValueError('[move_ability_fix] %s (%s) does not have exactly one Ability line with %s'
                             % (hid, name, old_name))
        text = text.replace(old_line, "call SaveInteger(Ab_HT, '%s', 0, %d)" % (hid, index[new_name]))
    return text
