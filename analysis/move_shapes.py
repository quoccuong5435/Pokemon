"""One-off: the skill template of a move follows the SHAPE of the move (single target / line / cone / area around the user),
decided by the move name, and its class and power only choose the variant and the tier. Before, only the power chose the
template, so most strong moves became lines."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


old = (
    "def template_for(info):" + NL +
    '    """(poke_data template key, level column 1..3) of a damaging move."""' + NL +
    "    p = info['power']" + NL +
    "    for top, phys, spec, a, b in _BANDS:" + NL +
    "        if p <= top:" + NL +
    "            return (phys if info['class'] == 'physical' else spec), (1 if p <= a else 2 if p <= b else 3)" + NL +
    "    raise AssertionError(p)" + NL)
new = (
    "# v3.3: the shape of the skill follows the move (names), not only its power" + NL +
    "AREA_MOVES = {'earthquake', 'surf', 'discharge', 'explosion', 'self-destruct', 'hyper voice', 'bulldoze', 'rock slide'," + NL +
    "              'heat wave', 'blizzard', 'muddy water', 'sludge wave', 'razor leaf', 'air cutter', 'icy wind', 'magnitude'," + NL +
    "              'boomburst', 'petal blizzard', 'eruption', 'water spout', 'twister', 'parabolic charge', 'sparkling aria'," + NL +
    "              'precipice blades', 'lava plume', 'overdrive', 'snarl', 'dazzling gleam', 'misty explosion', 'mind blown'," + NL +
    "              'earth power', 'rock tomb', 'sandstorm', 'hurricane', 'thunder', 'fire blast', 'inferno', 'judgment'," + NL +
    "              'supercell slam', 'stomping tantrum', 'high horsepower', 'diamond storm', 'springtide storm'}" + NL +
    "LINE_WORDS = ('beam', 'ray', 'cannon', 'laser', 'pulse', 'driver', 'lance')" + NL +
    "CONE_WORDS = ('flamethrower', 'breath', 'spray', 'gas', 'powder', 'whirlwind', 'overheat', 'burn out', 'sludge bomb')" + NL + NL + NL +
    "def shape_of(info):" + NL +
    '    """\'area\' (around the user), \'line\', \'cone\' or \'single\' (a target) from the move name."""' + NL +
    "    name = (info.get('name') or '').lower()" + NL +
    "    if name in AREA_MOVES:" + NL +
    "        return 'area'" + NL +
    "    if any(w in name for w in LINE_WORDS):" + NL +
    "        return 'line'" + NL +
    "    if any(w in name for w in CONE_WORDS):" + NL +
    "        return 'cone'" + NL +
    "    return 'single'" + NL + NL + NL +
    "def template_for(info):" + NL +
    '    """(poke_data template key, level column 1..3) of a damaging move: the shape picks the template family, the"""' + NL +
    '    """class (physical / special) the variant and the power the tier."""' + NL +
    "    p = info['power']" + NL +
    "    special = info['class'] != 'physical'" + NL +
    "    for top, _phys, _spec, a, b in _BANDS:" + NL +
    "        if p <= top:" + NL +
    "            tier = 1 if p <= a else 2 if p <= b else 3" + NL +
    "            break" + NL +
    "    else:" + NL +
    "        raise AssertionError(p)" + NL +
    "    shape = shape_of(info)" + NL +
    "    if shape == 'area':" + NL +
    "        return ('ULT_STOMP' if p > 115 and not special else ('NOVA' if special else 'STOMP')), tier" + NL +
    "    if shape == 'line':" + NL +
    "        return ('ULT_WAVE' if p > 115 else ('WAVE' if special else 'LINE')), tier" + NL +
    "    if shape == 'cone':" + NL +
    "        return 'CONE', tier" + NL +
    "    if p <= 60:" + NL +
    "        return ('CHAIN' if special else 'DAGGER'), tier" + NL +
    "    return 'BOLT', tier" + NL)
edit('tools/learn_data.py', old, new)

# tests
edit('tests/test_learn_data.py',
     "    assert t({'class': 'physical', 'power': 80})[0] == 'BOLT' and t({'class': 'special', 'power': 80})[0] == 'WAVE'" + NL +
     "    assert t({'class': 'physical', 'power': 100})[0] == 'LINE' and t({'class': 'special', 'power': 100})[0] == 'NOVA'" + NL +
     "    assert t({'class': 'physical', 'power': 120}) == ('ULT_STOMP', 1) and t({'class': 'special', 'power': 150}) == ('ULT_WAVE', 3)",
     "    # v3.3: the move name decides the shape; without a name a move is single target" + NL +
     "    assert t({'class': 'physical', 'power': 80})[0] == 'BOLT' and t({'class': 'special', 'power': 80})[0] == 'BOLT'" + NL +
     "    assert t({'class': 'physical', 'power': 100})[0] == 'BOLT' and t({'class': 'special', 'power': 150}) == ('BOLT', 3)" + NL +
     "    assert t({'name': 'Earthquake', 'class': 'physical', 'power': 100})[0] == 'STOMP'" + NL +
     "    assert t({'name': 'Blizzard', 'class': 'special', 'power': 110})[0] == 'NOVA'" + NL +
     "    assert t({'name': 'Hyper Beam', 'class': 'special', 'power': 150}) == ('ULT_WAVE', 3)" + NL +
     "    assert t({'name': 'Flamethrower', 'class': 'special', 'power': 90})[0] == 'CONE'" + NL +
     "    assert t({'name': 'Iron Tail', 'class': 'physical', 'power': 100})[0] == 'BOLT'")
print('ok')
