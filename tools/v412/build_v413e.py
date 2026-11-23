"""Build Pokemon Arena v4.1.3e on top of v4.1.3d.

  1. New shop item IGW1 "Grievous Seal" (Item Shop nIS0, 3,000g): a hit by its holder cuts the target's healing
     by 50% for 4 s. It plugs into PAX_HealMult, the one place the script multiplies heals (potions, Ab_Heal,
     PAX_HealUnit). Native HP regeneration is not part of that system and is not cut.
  2. League difficulty is back to the original (the 4.1.3d easing is removed): no per-stage HP / damage factor,
     enemy level = your level + stage + 1, 30 s wait after a loss.
     Rewards instead: +2,500 gold per Elite Four member (kept), final gold 10,000 -> 15,000, a free Ability
     Patch (IMHA, worth 10,000g), Champion title +20% stats (kept).
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))

import mpq  # noqa: E402
import slk  # noqa: E402
import objdata  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3d.w3x')
NAME = 'v4.1.3e'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')
ID = 'IGW1'

LEAGUE_DIFF = '''    if g == 8 then
        if League_Stage <= 1 then
            return 0.85
        elseif League_Stage <= 3 then
            return 0.95
        endif
    endif
    return 1.0
endfunction'''


def once(s, old, new):
    if s.count(old) != 1:
        raise SystemExit('anchor count %d: %r' % (s.count(old), old[:80]))
    return s.replace(old, new, 1)


def patch_script(s):
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    # --- League: undo the 4.1.3d easing
    if s.count(LEAGUE_DIFF) != 2:
        raise SystemExit('league diff blocks: %d' % s.count(LEAGUE_DIFF))
    s = s.replace(LEAGUE_DIFF, '    return 1.0\nendfunction')
    s = once(s, 'set Gym_Base[8] = GetHeroLevel(u) + League_Stage\n', 'set Gym_Base[8] = GetHeroLevel(u) + League_Stage + 1\n')
    s = once(s, 'set League_Cool[League_Pid] = Mega_Time + 5.0', 'set League_Cool[League_Pid] = Mega_Time + 30.0')
    s = once(s, 'Try again in 5 seconds.', 'Try again in 30 seconds.')
    # --- League: rewards
    s = once(s, '    call AdjustPlayerStateBJ(10000, p, PLAYER_STATE_RESOURCE_GOLD)\n    call UnitAddItemById(League_Unit, Itm_Id[18])\n',
             "    call AdjustPlayerStateBJ(15000, p, PLAYER_STATE_RESOURCE_GOLD)\n    call UnitAddItemById(League_Unit, Itm_Id[18])\n    call UnitAddItemById(League_Unit, 'IMHA')\n")
    s = s.replace('10000 gold, a Mega Ring, Shiny Charm (Shiny 1/20).', '15000 gold, a Mega Ring, a free Ability Patch, Shiny Charm (Shiny 1/20).')
    # --- Grievous Seal
    s = once(s, '    if Mega_Time < LoadReal(Fx_HT, h, 81) or Mega_Time < LoadReal(Fx_HT, h, 83) then\n        return 0.60\n    endif\n',
             "    if Mega_Time < LoadReal(Fx_HT, h, 84) then  // v4.1.3e: Grievous Seal\n        return 0.50\n    endif\n"
             '    if Mega_Time < LoadReal(Fx_HT, h, 81) or Mega_Time < LoadReal(Fx_HT, h, 83) then\n        return 0.60\n    endif\n')
    s = once(s, '    set tp = GetOwningPlayer(t)\n    \n    // VER2N CONTESTED GYM PVPVE',
             "    set tp = GetOwningPlayer(t)\n    if Itm_Has(src, '%s') then  // v4.1.3e: Grievous Seal cuts the target's healing by 50%% for 4s\n"
             '        call SaveReal(Fx_HT, GetHandleId(t), 84, Mega_Time + 4.0)\n    endif\n    \n    // VER2N CONTESTED GYM PVPVE' % ID)
    s = s.replace('v4.1.3d', NAME)
    return s.replace('\n', '\r\n') if crlf else s


def add_item(items, func, w3u):
    icol = items.name_to_x
    if items.find(ID):
        raise SystemExit(ID + ' already exists')
    r = dict(items.find('IT00'))
    r[1] = '"%s"' % ID
    r[icol['goldcost']] = '3000'
    items.rows.append(r)
    shop = w3u.find('nIS0')
    cur = shop.get('usei')
    used = set()
    for k in cur.split(','):
        mm = re.search(r'\[' + k + r'\](.*?)(?=\n\[|\Z)', func, re.S)
        if mm:
            bp = re.search(r'^Buttonpos=(\d+),(\d+)', mm.group(1), re.M)
            if bp:
                used.add((int(bp.group(1)), int(bp.group(2))))
    free = [(x, y) for y in range(3) for x in range(4) if (x, y) not in used]
    if not free:
        raise SystemExit('no free shop slot')
    x, y = free[0]
    func += ('\n[%s]\nName=Grievous Seal\nHotkey=G\nTip=Purchase |cff00ffffGrievous Seal|r (|cffffd1663,000g|r)\n'
             'Ubertip="Hits from its holder cut the target\'s healing by 50%% for 4s (potions, heal moves, Abilities and other heals that use the heal system; plain HP regeneration is not cut)."\n'
             'Buttonpos=%d,%d\nArt=ReplaceableTextures%sCommandButtons%sBTNOrbOfCorruption.blp\n') % (ID, x, y, BS, BS)
    shop.set('usei', 3, cur + ',' + ID)
    return func, (x, y), cur


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = patch_script(base.read('scripts' + BS + 'war3map.j').decode('utf-8'))
    items = slk.Slk(base.read('Units' + BS + 'ItemData.slk').decode('latin-1'))
    func = base.read('Units' + BS + 'ItemFunc.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    func, pos, shoplist = add_item(items, func, w3u)
    print('shop list was:', shoplist, '| new item at button', pos)
    w3i = base.read('war3map.w3i').replace(b'4.1.3d', b'4.1.3e')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i,
             'war3map.w3u': w3u.to_bytes(),
             'Units' + BS + 'ItemData.slk': items.to_text().encode('latin-1'),
             'Units' + BS + 'ItemFunc.txt': func.encode('utf-8')}
    if dry:
        print('Dry run OK.')
        return
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))
    if os.path.exists(PJASS):
        tmp = os.path.join(REF, '_tmp_v413e_war3map.j')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                           capture_output=True, text=True)
        print('PJASS rc=%d' % r.returncode)
        if r.returncode:
            print((r.stdout + r.stderr)[:800])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
