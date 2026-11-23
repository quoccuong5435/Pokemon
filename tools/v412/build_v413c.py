"""Build Pokemon Arena v4.1.3c on top of v4.1.3b: move cooldown / mana balance (proposals 1-4).

  1. Cooldown follows power (before: 10-14 s for every power from 15 to 130):
       power <= 25 -> 5 s, 26-39 -> 6 s, 40-80 -> 10 s, 81-89 -> 12 s, 90-130 -> 14 s.
     Moves with a long cooldown (the 150-power ones, 40-45 s) are not touched.
  2. Type balance, through cooldown only (the tooltips of the moves hold fixed damage numbers):
       Grass / Poison / Rock -1 s (minimum 4 s); Fire / Fairy +0.5 s.
  3. Power 100-130 moves cost at least 175 mana.
  4. The weak 15-25 power moves (point 1) get the 5 s cooldown.
Only Cool1 / Cost1 of AV, AW, AY, AZ (the four slot buttons) and AK (the real spell) of moves 0..318 are changed.
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

BS = chr(92)
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3b.w3x')
NAME = 'v4.1.3c'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
TYPES = ['Bug', 'Dark', 'Dragon', 'Electr', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass',
         'Ground', 'Ice', 'Normal', 'Poison', 'Psy', 'Rock', 'Steel', 'Water']
FASTER = {'Grass', 'Poison', 'Rock'}
SLOWER = {'Fire', 'Fairy'}


def tag(i):
    return B36[i // 36] + B36[i % 36]


def cd_for(power):
    if power <= 25:
        return 5.0
    if power <= 39:
        return 6.0
    if power <= 80:
        return 10.0
    if power <= 89:
        return 12.0
    return 14.0


def fmt(v):
    return str(int(v)) if float(v) == int(v) else ('%.1f' % v)


def balance(abil, script):
    pw = {int(a): int(b) for a, b in re.findall(r'set Mv_Pow\[(\d+)\] = (-?\d+)', script)}
    ty = {int(a): int(b) for a, b in re.findall(r'set Mv_Type\[(\d+)\] = (-?\d+)', script)}
    cx, mx = abil.name_to_x['Cool1'], abil.name_to_x['Cost1']
    rows = {}
    for r in abil.rows:
        k = abil.unquote(r.get(1))
        if k and len(k) == 4 and k[:2] in ('AV', 'AW', 'AY', 'AZ', 'AK'):
            rows[k] = r
    stat = {'cool': 0, 'mana': 0, 'moves': 0}
    for m in range(319):
        p = pw.get(m, 0)
        if p <= 0 or p >= 140:
            continue
        t = TYPES[ty[m]] if 0 <= ty.get(m, -1) < len(TYPES) else ''
        cd = cd_for(p)
        if t in FASTER:
            cd = max(4.0, cd - 1.0)
        elif t in SLOWER:
            cd += 0.5
        touched = False
        for pre in ('AV', 'AW', 'AY', 'AZ', 'AK'):
            r = rows.get(pre + tag(m))
            if not r:
                continue
            cur = abil.unquote(r.get(cx))
            if cur is not None and float(cur) <= 14.0:
                r[cx] = fmt(cd)
                stat['cool'] += 1
                touched = True
            if 100 <= p <= 130:
                cm = abil.unquote(r.get(mx))
                if cm is not None and float(cm) < 175.0:
                    r[mx] = '175'
                    stat['mana'] += 1
        stat['moves'] += touched
    return stat


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = base.read('scripts' + BS + 'war3map.j').decode('utf-8')
    abil = slk.Slk(base.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    stat = balance(abil, script)
    print('balance:', stat)
    script = script.replace('v4.1.3b', NAME)
    w3i = base.read('war3map.w3i').replace(b'4.1.3b', NAME.encode('latin-1')[1:])
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i,
             'Units' + BS + 'AbilityData.slk': abil.to_text().encode('latin-1')}
    if dry:
        print('Dry run OK.')
        return
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))
    if os.path.exists(PJASS):
        tmp = os.path.join(REF, '_tmp_v413c_war3map.j')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                           capture_output=True, text=True)
        print('PJASS rc=%d' % r.returncode)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
