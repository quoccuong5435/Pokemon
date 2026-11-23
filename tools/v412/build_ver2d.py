"""Build Pokemon Arena v4.1.2-ver2d:
- All features of v4.1.2-ver2c (33 starters, 9 debuff moves, Transform, visible stat stages,
  weather visual fog & ambient thunder, rearranged base courtyard, expanded 192x192 map size)
- PLUS comprehensive Vietnamese localization for in-game announcements, event alerts,
  bounty & wanted contracts, altar & golden treasure & red gyarados events,
  late-game training (-up), mythic forge (-forge), solo deathmatch (-solo),
  duels (-duel), stats breakdown (-me), awakening quest (-quest),
  and complete interactive -help chat command guide.
- Preserves original English Pokémon names, Move names, and chat command keywords.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, HERE)
import mpq  # noqa: E402
import localize_vi  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2c.w3x')
NAME = 'v4.1.2-ver2d'
PREV_NAME = 'v4.1.2-ver2c'


def build(out, dry):
    print('Loading base map: %s' % BASE_MAP)
    base = mpq.MPQ(BASE_MAP)

    # 1. Patch Script with Vietnamese localization
    print('Reading war3map.j...')
    script = base.read('scripts\\war3map.j').decode('utf-8')
    script = script.replace('\r\r\n', '\r\n').replace('\r\n', '\n')

    print('Applying Vietnamese localization patch...')
    script = localize_vi.patch_script(script)

    # Update version string
    script = script.replace(PREV_NAME, NAME)
    script = script.replace('v4.1.2-ver2c: PvP & Legend Balance', 'v4.1.2-ver2d: Tiếng Việt, PvP & Cân Bằng Legend')
    script = script.replace('\n', '\r\n')

    # 2. Patch ItemFunc.txt
    print('Patching ItemFunc.txt with Vietnamese tooltips...')
    func = base.read('Units\\ItemFunc.txt').decode('utf-8')
    func = localize_vi.patch_strings(None, func, None)

    # 3. Patch w3i
    print('Patching war3map.w3i...')
    w3i = base.read('war3map.w3i')
    w3i = w3i.replace(PREV_NAME.encode('latin-1'), NAME.encode('latin-1'))

    files = {
        'scripts\\war3map.j': script.encode('utf-8'),
        'Units\\ItemFunc.txt': func.encode('utf-8'),
        'war3map.w3i': w3i,
    }

    if dry:
        print('Dry run: completed successfully without writing.')
        return

    if os.path.exists(out):
        print('Removing existing file: %s' % out)
        os.remove(out)

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2

    print('Saving map to: %s (hash_size=%d) ...' % (out, hsize))
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=hsize if hsize != len(base.hash_table) else None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    out_path = a.out or os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
    build(out_path, a.dry_run)
