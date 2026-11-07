"""One-off: wire jass/moves.j (one move per kind) - Mv_Kind data in extras.py, global, replace in apply.py."""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


s = open('tools/v34/jass/globals.j', encoding='utf-8').read().rstrip('\n')
s += '\ninteger array Mv_Kind                   // v3.4.1: game skill a learned move is made from (moves.j: one per kind)\n'
open('tools/v34/jass/globals.j', 'w', encoding='utf-8').write(s)
print('edited globals.j')

edit('tools/v34/extras.py', [(
    """    # ---------------- Elite Four and Champion""",
    """    # ---------------- v3.4.1: kind of each learned move = the game skill its abilities are made from (same order)
    import slk
    sk = slk.Slk(base.read('Units\\\\AbilityData.slk').decode('latin-1'))
    code_x = sk.name_to_x['code']
    kinds, nk = {}, 0
    b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    n_moves = int(re.search(r'set Mv_N = (\\d+)', script).group(1))
    for m in range(n_moves):
        row = sk.find('AV' + b36[m // 36] + b36[m % 36])
        code = (row or {}).get(code_x, '').strip('"')
        if code not in kinds:
            kinds[code] = len(kinds)
        c.data.append('    set Mv_Kind[%d] = %d' % (m, kinds[code]))
    c.report.append('learned moves: %d kinds of game skill %s' % (len(kinds), sorted(kinds)))

    # ---------------- Elite Four and Champion""")])

edit('tools/v34/apply.py', [(
    """    script = replace_functions(script, snippet('ab_head.j'))
""", """    script = replace_functions(script, snippet('ab_head.j'))
    script = replace_functions(script, snippet('moves.j'))  # v3.4.1: one learned move per kind (no shared button)
""")])
