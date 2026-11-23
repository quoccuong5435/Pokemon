"""v4.1.2: 33 playable starter heroes (Gen 2-7) and wild types with Souls.
Data is split into 4 chunked functions (Fx_Data13..16) called via ExecuteFunc.
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
import starters
import status_moves as SM


def chunk_functions(lines, prefix, n_funcs):
    size = max(1, (len(lines) + n_funcs - 1) // n_funcs)
    out = []
    for k in range(n_funcs):
        out.append('function %s%d takes nothing returns nothing' % (prefix, k + 13))
        out += lines[k * size:(k + 1) * size]
        out.append('endfunction\n')
    return '\n'.join(out)


def patch_script(script):
    slugs = {starters.slug(mv[0]): SM.STAT_BASE + k for k, mv in enumerate(SM.MOVES)}
    st_lines, counts = starters.data_lines(script, slugs)
    w_lines = starters.wild_data_lines()
    all_lines = st_lines + w_lines

    # 1. Chunked functions Fx_Data13..16
    chunked = chunk_functions(all_lines, 'Fx_Data', 4)

    # Insert right after Fx_Data12
    p = script.find('function Fx_Data12')
    if p < 0:
        raise SystemExit('starters_v412: function Fx_Data12 not found')
    p_end = script.find('endfunction', p)
    if p_end < 0:
        raise SystemExit('starters_v412: endfunction of Fx_Data12 not found')
    insert_pos = p_end + len('endfunction')
    script = script[:insert_pos] + '\n\n' + chunked + script[insert_pos:]

    # 2. Add ExecuteFunc calls
    old_call = '    call ExecuteFunc("Fx_Data12")'
    new_call = '''    call ExecuteFunc("Fx_Data12")
    call ExecuteFunc("Fx_Data13")
    call ExecuteFunc("Fx_Data14")
    call ExecuteFunc("Fx_Data15")
    call ExecuteFunc("Fx_Data16")'''
    if old_call not in script:
        raise SystemExit('starters_v412: call ExecuteFunc("Fx_Data12") not found')
    script = script.replace(old_call, new_call, 1)

    # 3. Patch picker and wild
    script = starters.patch_picker(script)
    script = starters.patch_wild(script)

    return script
