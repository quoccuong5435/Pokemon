"""Build Pokemon Arena v4.1.3h on top of v4.1.3g: the Dark Orb of Lugia (a Shadow / Dark Lugia form).

It is one more entry of the Mega system, built exactly like the Primal Kyogre / Groudon orbs (entry 33 / 34):
  * Mega_Base = Mega_Skin = E022 (the playable Lugia): same unit, only a dark purple tint and a bigger size.
  * Stone item IMDL "[Lugia] Dark Orb" (8,000g, Form / Paradox kind 2, sold at the Paradox Shop nFS1) with the item
    ability AMDL (Channel, a free base order id, 150 s cooldown, copy of AM0X).
  * 60 s Mega: +25% STR, +10% AGI, +35% INT. No special power, no change of type (Lugia stays Psychic / Water).
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
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3g.w3x')
NAME = 'v4.1.3h'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')
STONE, ABIL, IDX, PRICE = 'IMDL', 'AMDL', 36, 8000
CANDIDATE_ORDERS = ('banish', 'stasistrap', 'innerfire', 'polymorph', 'thunderbolt', 'frostarmor', 'raisedead', 'tornado', 'slow', 'inferno', 'curse', 'scout', 'blizzard', 'flamestrike')
ART = 'ReplaceableTextures' + BS + 'CommandButtons' + BS + 'BTNOrbOfDarkness.blp'

ENTRY = '''    set Mega_Base[36] = 'E022'
    set Mega_Stone[36] = 'IMDL'
    set Mega_Skin[36] = 'E022'
    set Mega_Evolve[36] = 'AMDL'
    set Mega_PStr[36] = 25
    set Mega_PAgi[36] = 10
    set Mega_PInt[36] = 35
    set Mega_Price[36] = 8000
    set Mega_Name[36] = "Dark Lugia"
    set Mega_StoneName[36] = "Dark Orb"
    set Mega_Fx[36] = "Abilities\\\\Spells\\\\Undead\\\\AnimateDead\\\\AnimateDeadTarget.mdl"
    set Mega_Scale[36] = 2.000
    set Mega_BaseScale[36] = 1.750
    set Mega_R[36] = 90
    set Mega_G[36] = 55
    set Mega_B[36] = 150
    set Mega_N = 37
'''


def once(s, old, new):
    if s.count(old) != 1:
        raise SystemExit('anchor count %d: %r' % (s.count(old), old[:80]))
    return s.replace(old, new, 1)


def patch_script(s):
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    # the blank-line style of the Mega_InitData section is irrelevant: anchor on the single statement
    s = once(s, '    set Mega_N = 36\n', ENTRY)
    s = once(s, "    call SaveInteger(Mega_HT, 'IM0Z', 90, 2)\n", "    call SaveInteger(Mega_HT, 'IM0Z', 90, 2)\n    call SaveInteger(Mega_HT, 'IMDL', 90, 2)\n")
    s = once(s, "    call SaveInteger(Fx_HT, 'IM0Z', 3, 7000)\n",
             "    call SaveInteger(Fx_HT, 'IM0Z', 3, 7000)\n    call SaveInteger(Fx_HT, 'IMDL', 2, 1)\n    call SaveInteger(Fx_HT, 'IMDL', 3, 8000)\n")
    s = s.replace('v4.1.3g', NAME)
    return s.replace('\n', '\r\n') if crlf else s


def patch_objects(abil, items, func, strings, w3u):
    acol, icol = abil.name_to_x, items.name_to_x
    assert abil.find(ABIL) is None and items.find(STONE) is None
    used_orders = {abil.get(r, 'DataF1') for r in abil.rows}
    order = next(o for o in CANDIDATE_ORDERS if o not in used_orders)
    print('order id for the Dark Orb ability:', order)
    ra = dict(abil.find('AM0X'))
    ra[1] = '"%s"' % ABIL
    ra[acol['DataF1']] = order
    abil.rows.append(ra)
    ri = dict(items.find('IM0X'))
    ri[1] = '"%s"' % STONE
    ri[icol['abilList']] = '"%s"' % ABIL
    ri[icol['cooldownID']] = '"%s"' % ABIL
    ri[icol['goldcost']] = str(PRICE)
    items.rows.append(ri)
    shop = w3u.find('nFS1')
    cur = shop.get('usei')
    used = set()
    for k in cur.split(','):
        mm = re.search(r'\[' + k + r'\](.*?)(?=\n\[|\Z)', func, re.S)
        bp = re.search(r'^Buttonpos=(\d+),(\d+)', mm.group(1), re.M) if mm else None
        if bp:
            used.add((int(bp.group(1)), int(bp.group(2))))
    free = [(x, y) for y in range(3) for x in range(4) if (x, y) not in used]
    x, y = free[0]
    func += ('\n[%s]\nName=[Lugia] Dark Orb\nArt=%s\nButtonpos=%d,%d\nTip=[Lugia] Purchase |cff9966ffDark Orb|r\n'
             'Ubertip="[Lugia] Shadow Reversion: Only Lugia. Become Dark Lugia with +25%% STR, +10%% AGI, +35%% INT for 60 seconds."\n') % (STONE, ART, x, y)
    strings += ('\n[%s]\nName=[Lugia] Shadow Reversion - Lugia\nArt=%s\nButtonpos=1,1\nTip=[Lugia] Shadow Reversion - Lugia\n'
                'Ubertip="[Lugia] Shadow Reversion: Only Lugia. Become Dark Lugia: +25%% STR, +10%% AGI, +35%% INT for 60s."\n') % (ABIL, ART)
    shop.set('usei', 3, cur + ',' + STONE)
    return func, strings, (x, y)


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = patch_script(base.read('scripts' + BS + 'war3map.j').decode('utf-8'))
    abil = slk.Slk(base.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    items = slk.Slk(base.read('Units' + BS + 'ItemData.slk').decode('latin-1'))
    func = base.read('Units' + BS + 'ItemFunc.txt').decode('utf-8')
    strings = base.read('Units' + BS + 'CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    func, strings, pos = patch_objects(abil, items, func, strings, w3u)
    print('Dark Orb button in the Paradox Shop at', pos)
    w3i = base.read('war3map.w3i').replace(b'4.1.3g', b'4.1.3h')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i, 'war3map.w3u': w3u.to_bytes(),
             'Units' + BS + 'AbilityData.slk': abil.to_text().encode('latin-1'),
             'Units' + BS + 'ItemData.slk': items.to_text().encode('latin-1'),
             'Units' + BS + 'ItemFunc.txt': func.encode('utf-8'),
             'Units' + BS + 'CampaignAbilityStrings.txt': strings.encode('utf-8')}
    tmp = os.path.join(REF, '_tmp_v413h_war3map.j')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(script)
    r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp], capture_output=True, text=True)
    print('PJASS rc=%d' % r.returncode)
    if r.returncode:
        print((r.stdout + r.stderr)[:1000])
        raise SystemExit(1)
    if dry:
        print('Dry run OK.')
        return
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
