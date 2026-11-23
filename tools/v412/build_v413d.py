"""Build Pokemon Arena v4.1.3d on top of v4.1.3c: gym badges and Pokemon League.

Badges (aura values and item texts; gym 5 and 8 stay debuffs on enemies within 600, only stronger):
  Gym 1 movement speed 20% -> 25%.  Gym 2 HP regeneration x10 -> x15.
  Gym 5 enemy attack / move speed -15% -> -25%.  Gym 8 enemy armor -25 -> -35.
Pokemon League:
  * Elite Four 1-2 fight at 85% HP / damage of gym 8, Elite Four 3-4 at 95%, the Champion at 100%.
  * Enemy level = your level + stage (0..4) instead of + stage + 1 (1..5).
  * After a loss the cooldown is 5 s instead of 30 s.
  * Each Elite Four member defeated pays 2,500 gold (the final 10,000 gold stays).
  * Champion title +15% -> +20% STR / AGI / INT.
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
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3c.w3x')
NAME = 'v4.1.3d'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')

LEAGUE_DIFF = '''    if g == 8 then
        if League_Stage <= 1 then
            return 0.85
        elseif League_Stage <= 3 then
            return 0.95
        endif
    endif
    return 1.0
endfunction'''

ABIL = {('A03T', 'DataA1'): '0.25', ('A03U', 'DataB1'): '15', ('A03X', 'DataA1'): '-0.25',
        ('A03X', 'DataB1'): '-0.25', ('A040', 'DataA1'): '-35'}
ITEM_TEXT = {
    'I014': ('Raise 20% Movement speed Aura.', 'Raise 25% Movement speed Aura.'),
    'I015': ('Raise x10 origin HP regeneration Aura.', 'Raise x15 origin HP regeneration Aura.'),
    'I019': ('Reduce 15% Attack speed and Movement speed Aura.', 'Reduce 25% Attack speed and Movement speed Aura.'),
    'I01B': ('Reduce 25 armor Aura.', 'Reduce 35 armor Aura.'),
}


def once(s, old, new):
    if s.count(old) != 1:
        raise SystemExit('anchor count %d: %r' % (s.count(old), old[:70]))
    return s.replace(old, new, 1)


def patch_script(s):
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    s = once(s, 'set Gym_Base[8] = GetHeroLevel(u) + League_Stage + 1', 'set Gym_Base[8] = GetHeroLevel(u) + League_Stage')
    for fn in ('Gym_DiffHP', 'Gym_DiffDmg'):
        a = s.index('function %s takes integer g returns real' % fn)
        b = s.index('    return 1.0\nendfunction', a)
        e = b + len('    return 1.0\nendfunction')
        s = s[:b] + LEAGUE_DIFF + s[e:]
    s = once(s, 'set League_Cool[League_Pid] = Mega_Time + 30.0', 'set League_Cool[League_Pid] = Mega_Time + 5.0')
    s = once(s, 'Try again in 30 seconds.', 'Try again in 5 seconds.')
    old = '            call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 6.0, "|cff66ff66" + League_Name[League_Stage] + " is defeated!|r")\n'
    new = ('            call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 6.0, "|cff66ff66" + League_Name[League_Stage] + " is defeated! +2500 gold|r")\n'
           '            call AdjustPlayerStateBJ(2500, Player(League_Pid), PLAYER_STATE_RESOURCE_GOLD)\n')
    s = once(s, old, new)
    s = once(s, '        set pct = pct + 15\n        if not HaveSavedHandle(Ab_HT, h, 129) then', '        set pct = pct + 20\n        if not HaveSavedHandle(Ab_HT, h, 129) then')
    s = once(s, 'Title [Champion]: +15% STR / AGI / INT', 'Title [Champion]: +20% STR / AGI / INT')
    s = s.replace('v4.1.3c', NAME)
    return s.replace('\n', '\r\n') if crlf else s


def patch_abil(abil):
    n = 0
    for (k, col), v in ABIL.items():
        r = abil.find(k)
        x = abil.name_to_x[col]
        assert r is not None and x in r, (k, col)
        r[x] = v
        n += 1
    return n


def patch_items(f):
    for k, (old, new) in ITEM_TEXT.items():
        a = f.index('[%s]' % k)
        m = re.search(r'\n\[', f[a + 1:])
        b = a + 1 + m.start() if m else len(f)
        sec = f[a:b]
        assert sec.count(old) >= 1, k
        f = f[:a] + sec.replace(old, new) + f[b:]
    return f


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = patch_script(base.read('scripts' + BS + 'war3map.j').decode('utf-8'))
    abil = slk.Slk(base.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    print('abilities changed:', patch_abil(abil))
    func = patch_items(base.read('Units' + BS + 'ItemFunc.txt').decode('utf-8'))
    w3i = base.read('war3map.w3i').replace(b'4.1.3c', b'4.1.3d')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i,
             'Units' + BS + 'AbilityData.slk': abil.to_text().encode('latin-1'),
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
        tmp = os.path.join(REF, '_tmp_v413d_war3map.j')
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
