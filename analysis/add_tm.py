"""One-off: TM/HM moves (3000 gold at the NPC). Python data side (learn_data, inject) + JASS (mega.j)."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    assert s.count(old) == 1, (path, old[:60], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


# ---------------------------------------------------------------- learn_data
edit('tools/learn_data.py', 'from dataclasses import dataclass', 'from dataclasses import dataclass, field')
edit('tools/learn_data.py',
     '    by_unit: dict    # unit type id -> [(available hero level, move index)]' + NL,
     '    by_unit: dict    # unit type id -> [(available hero level, move index)]' + NL +
     '    tm_by_unit: dict = field(default_factory=dict)  # v3.3: unit type id -> [move index] of its TM/HM moves' + NL)
edit('tools/learn_data.py',
     'def build_plan(units):',
     'TM_MAX = 40  # TM/HM moves kept per species (the strongest damaging ones)' + NL + NL + NL +
     'def tm_candidates(species_slug):' + NL +
     '    """Damaging TM/HM moves (move slugs) of a species, strongest first."""' + NL +
     '    s = SPECIES.get(species_slug)' + NL +
     '    if s is None:' + NL +
     '        return []' + NL +
     '    mv = [m for m in s.get("tm", []) if m in MOVES and MOVES[m]["power"] > 0]' + NL +
     '    return sorted(mv, key=lambda m: (-score(MOVES[m]), m))[:TM_MAX]' + NL + NL + NL +
     'def build_plan(units):')
edit('tools/learn_data.py',
     '    slugs = sorted({mv for lst in per_unit.values() for _, mv in lst})',
     '    tm_unit = {uid: [m for m in tm_candidates(slug(name)) if MOVES[m]["name"].lower() not in kit_names(uid)]'
     + NL + '               for uid, name in units.items()}' + NL +
     '    slugs = sorted({mv for lst in per_unit.values() for _, mv in lst} | {m for lst in tm_unit.values() for m in lst})')
edit('tools/learn_data.py',
     '    return MovePlan(moves, by_unit)',
     '    tm_by_unit = {uid: [index[m] for m in lst] for uid, lst in tm_unit.items() if lst}' + NL +
     '    return MovePlan(moves, by_unit, tm_by_unit)')

# ---------------------------------------------------------------- inject: TM keys (299 = count, 300 + k = move index)
edit('tools/inject.py',
     "    lines.append('endfunction')" + NL + "    return '\\n'.join(lines) + '\\n'" + NL + NL + NL + 'def gen_data_init',
     "    if moves:" + NL +
     "        for uid, tms in sorted(moves.tm_by_unit.items()):" + NL +
     "            lines.append(\"    call SaveInteger(Ab_HT, '%s', 299, %d)\" % (uid, len(tms)))" + NL +
     "            for k, mi in enumerate(tms):" + NL +
     "                lines.append(\"    call SaveInteger(Ab_HT, '%s', %d, %d)\" % (uid, 300 + k, mi))" + NL +
     "    lines.append('endfunction')" + NL + "    return '\\n'.join(lines) + '\\n'" + NL + NL + NL + 'def gen_data_init') \
    if False else None
print('python side prepared (inject patched separately)')
