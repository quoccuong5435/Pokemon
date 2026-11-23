"""Build Pokemon Arena v4.1.3j on top of v4.1.3h:
Same full Legendary Expansion (25 new Legendaries + 17 real 3D Mega/Form models + Gold '+' Hero Skill unlock
+ Mega/Form shop removal), NOW WITH ONE-TIME GOLD COST when unlocking via Gold '+':
  - Normal Mega (Lv 50): 5,000 Gold one-time unlock cost.
  - Legend Mega / Primal / Origin / Form / Plate (Lv 70): 8,000 Gold one-time unlock cost.
  - Safe if clicked early without enough gold: stays on Command Card locked (no free stats, no cast)
    and automatically pays, unlocks, grants +40/+60 All Stats, and casts when pressed once you have enough gold!
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import slk  # noqa: E402
import objdata  # noqa: E402
import legend_expansion_data  # noqa: E402
import hero_mega_unlock  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3h.w3x')
NAME = 'v4.1.3j'
OUT_MAP = os.path.join(MAPS, f'Pokemon Arena {NAME}.w3x')
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')


def build_data():
    base = mpq.MPQ(BASE_MAP)
    script = base.read('scripts' + BS + 'war3map.j').decode('utf-8')
    crlf = '\r\n' in script
    script = script.replace('\r\r\n', '\r\n').replace('\r\n', '\n')

    abil = slk.Slk(base.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    items = slk.Slk(base.read('Units' + BS + 'ItemData.slk').decode('latin-1'))
    func = base.read('Units' + BS + 'ItemFunc.txt').decode('utf-8')
    strings = base.read('Units' + BS + 'CampaignAbilityStrings.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))

    func, strings = legend_expansion_data.patch_objects(objdata, w3u, abil, items, func, strings)
    script = legend_expansion_data.patch_script(script)

    strings = hero_mega_unlock.patch_objects_and_units(script, w3u, abil, strings)
    script = hero_mega_unlock.patch_script(script)

    script = script.replace('v4.1.3h', NAME)
    if crlf:
        script = script.replace('\n', '\r\n')

    w3i = base.read('war3map.w3i').replace(b'4.1.3h', b'4.1.3j')

    files = {
        'scripts' + BS + 'war3map.j': script.encode('utf-8'),
        'war3map.w3i': w3i,
        'war3map.w3u': w3u.to_bytes(),
        'Units' + BS + 'AbilityData.slk': abil.to_text().encode('latin-1'),
        'Units' + BS + 'ItemData.slk': items.to_text().encode('latin-1'),
        'Units' + BS + 'ItemFunc.txt': func.encode('utf-8'),
        'Units' + BS + 'CampaignAbilityStrings.txt': strings.encode('utf-8'),
    }

    have = {n.lower() for n in base.listfile()}
    assets = legend_expansion_data.load_all_assets(mpq)
    for path, data in assets.items():
        if path.lower() not in have and path not in files:
            files[path] = data

    return base, files, script, abil, items, func, strings, w3u


def build(out, dry, skip_pjass=False):
    if not dry and os.path.exists(out):
        raise SystemExit(f'Output exists, refusing to overwrite per GEMINI.md: {out}')

    base, files, script, *_ = build_data()
    tmp = os.path.join(REF, '_tmp_v413j_war3map.j')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(script)

    if not skip_pjass and os.path.exists(PJASS):
        try:
            r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                               capture_output=True, text=True)
            print('PJASS rc=%d' % r.returncode)
            if r.returncode:
                print((r.stdout + r.stderr)[:1500])
                raise SystemExit(1)
        except OSError as e:
            print(f'[pjass skipped due to OS sandbox error: {e}]')

    print('Total files to package for %s: %d' % (NAME, len(files)))
    if dry:
        print('Dry run OK.')
        return

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--skip-pjass', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run, a.skip_pjass)
