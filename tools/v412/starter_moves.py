"""Generate starter move learnsets for all 33 Gen 2-7 starters in v4.1.2.
Uses existing Fx_AddLv / Fx_AddTm in war3map.j.
Inserts chunked Fx_StarterMoves1..5 right after Fx_AddTm, and calls Mv_Sync upon hero pick.
"""
import os

def get_move_lines():
    txt_path = 'c:/Users/quocc/.gemini/antigravity/brain/e9418865-9cd5-47e4-8e76-8fc6a79e9474/scratch/starter_move_lines.txt'
    with open(txt_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def chunk_lines(lines, chunk_size=350):
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunks.append(lines[i:i + chunk_size])
    return chunks

def patch_script(s):
    lines = get_move_lines()
    chunks = chunk_lines(lines)

    # 1. Create chunked functions containing the 1,578 move/TM calls
    code = []
    for idx, c in enumerate(chunks, 1):
        code.append(f"function Fx_StarterMoves{idx} takes nothing returns nothing")
        for l in c:
            code.append(f"    call {l}" if not l.startswith('call') else f"    {l}")
        code.append("endfunction\n")

    starter_code = '\n'.join(code)

    # Insert right after Fx_AddTm function
    addtm_end = 'function Fx_AddTm takes integer uid, integer mvi returns nothing\n    local integer n = LoadInteger(Ab_HT, uid, 299)\n    call SaveInteger(Ab_HT, uid, 300 + n, mvi)\n    call SaveInteger(Ab_HT, uid, 299, n + 1)\nendfunction'
    if addtm_end not in s:
        raise SystemExit('starter_moves: Fx_AddTm anchor not found')
    s = s.replace(addtm_end, addtm_end + '\n\n' + starter_code, 1)

    # 2. Add ExecuteFunc calls in Base_Init
    exec_calls = '\n'.join([f'    call ExecuteFunc("Fx_StarterMoves{i}")' for i in range(1, len(chunks) + 1)])
    old_base = 'function Base_Init takes nothing returns nothing'
    new_base = f'function Base_Init takes nothing returns nothing\n{exec_calls}'
    s = s.replace(old_base, new_base, 1)

    # 3. Call Mv_Sync(h) upon hero pick in Pick_Choose (where Mv_Sync is already defined)
    old_pick = 'set h = CreateUnit(p, Pick_Type[idx], GetUnitX(w), GetUnitY(w), 270.0)\n        call Repick_Restore(h)'
    new_pick = 'set h = CreateUnit(p, Pick_Type[idx], GetUnitX(w), GetUnitY(w), 270.0)\n        call Repick_Restore(h)\n        call Mv_Sync(h)'
    if old_pick in s:
        s = s.replace(old_pick, new_pick, 1)

    return s
