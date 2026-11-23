"""Moves NPC rework + Pokemon-style level-up move question (GEMINI.md section 14).

1. Moves NPC (Npc_Show / Npc_OnClick replaced): home -> "Level-up moves" / "TM/HM moves" / "Forget a move".
   A list shows the moves the hero can still learn, best first (power, +50% when it has the hero's type, marked
   STAB), 9 a page. Click a move: a free slot takes it at once; with 4 moves a "Replace which move?" list follows.
   Prices are unchanged (level-up moves Npc_LearnCost, TM/HM PAX_Npc_TMCost 3k..15k).
2. Level-up (Mv_Sync): a new level-up move still fills a free slot by itself; with 4 moves the human owner gets
   "<hero> wants to learn <move>. Forget which move?" with the 4 slots + Skip. It waits while an enemy is within
   900 (a dialog blocks the controls) and says so once. Computer / neutral owners keep the old rule.

Usage in a build script (the script text must use LF line ends, as build_v42b.build_data has it):
    import move_tutor
    script = move_tutor.patch_script(script)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JASS = os.path.join(HERE, 'jass')
MARK = '// move_tutor (tools/v412/move_tutor.py)'

GLOBALS = MARK + """: sorted move lists, replace dialog, level-up question
constant integer MT_Max = 160
integer array MT_Cand
integer array MT_Sc
integer array MT_CandN
integer array MT_Pend
integer array MT_PendCost
integer array MT_PrevMode
dialog array LvAsk_Dlg
button array LvAsk_Btn
unit array LvAsk_Unit
integer array LvAsk_Move
hashtable LvAsk_HT = InitHashtable()
group LvAsk_G = CreateGroup()
constant real LvAsk_Range = 900.0
"""

OLD_SYNC_TAIL = """                    elseif Mv_Score[m] > Mv_WeakScore(u) then
                        call Mv_Put(u, Mv_WeakSlot(u), m)
                        call Mv_Notify(u, m)
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    else
                        call SaveInteger(Ab_HT, h, 200 + m, 1)
                    endif
"""
NEW_SYNC_TAIL = """                    else
                        call LvAsk_Offer(u, m)  // move_tutor: the owner chooses (computer players: old rule)
                    endif
"""

INIT_ANCHOR = '    call TriggerAddAction(t, function Npc_OnClick)\n'
INIT_ADD = """    set t = CreateTrigger()
    set i = 0
    loop
        exitwhen i >= 12
        set LvAsk_Dlg[i] = DialogCreate()
        call TriggerRegisterDialogEvent(t, LvAsk_Dlg[i])
        set i = i + 1
    endloop
    call TriggerAddAction(t, function LvAsk_OnClick)
"""


def _read(name):
    with open(os.path.join(JASS, name), encoding='utf-8') as fh:
        return fh.read().replace('\r\n', '\n')


def _once(s, old, new, label):
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError('[move_tutor] anchor %r matched %d times (expected 1)' % (label, cnt))
    return s.replace(old, new, 1)


def _replace_function(s, header, body, label):
    start = s.find('\n' + header)
    if start < 0 or s.find('\n' + header, start + 1) >= 0:
        raise ValueError('[move_tutor] function %r not found exactly once' % label)
    start += 1
    end = s.find('\nendfunction\n', start)
    if end < 0:
        raise ValueError('[move_tutor] end of %r not found' % label)
    end += len('\nendfunction\n')
    return s[:start] + body.rstrip('\n') + '\n' + s[end:]


def patch_script(s):
    if '\r\n' in s:
        raise ValueError('[move_tutor] give the script with LF line ends')
    if MARK in s:
        raise ValueError('[move_tutor] script is already patched')
    s = _once(s, 'unit array Npc_Unit\n', 'unit array Npc_Unit\n' + GLOBALS, 'globals after Npc_Unit')
    s = _once(s, '// every second for each living hero:',
              _read('move_tutor_lvask.j') + '// every second for each living hero:', 'before Mv_Sync')
    s = _once(s, OLD_SYNC_TAIL, NEW_SYNC_TAIL, 'Mv_Sync full-slot branch')
    s = _replace_function(s, 'function Npc_Show takes integer pid, unit h, integer s returns nothing',
                          _read('move_tutor_npc.j'), 'Npc_Show')
    s = _replace_function(s, 'function Npc_OnClick takes nothing returns nothing',
                          _read('move_tutor_click.j'), 'Npc_OnClick')
    s = _once(s, INIT_ANCHOR, INIT_ANCHOR + INIT_ADD, 'Npc_OnClick registration')
    return s
