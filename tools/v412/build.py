"""v4.1.3: the v4.1.2 map with the camp loot balance (tools/v412/loot_balance.py).

The source of v4.1.2 is not on this PC (only the map), so this reads the map itself, patches its script and
war3map.w3i and writes a new archive; every other file is copied unchanged. Never overwrites a map.

    python -I tools/v412/build.py --dry-run
    python -I tools/v412/build.py            -> ..\\Pokemon Arena v4.1.3.w3x
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
import loot_balance  # noqa: E402
import loot_hp  # noqa: E402
import charm_buff  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2.w3x')


def build(out, dry, version):
    base = mpq.MPQ(BASE_MAP)
    script = base.read('scripts\\war3map.j').decode('latin-1')
    w3i = base.read('war3map.w3i')
    script = loot_balance.patch_script(script)  # v4.1.3: the same expected loot for every camp
    script = loot_hp.patch_script(script)  # v4.1.4: soft cap for the Max HP of loot
    script = charm_buff.patch_script(script)  # v4.1.5: stronger Storm Shock, Soul Burn, Mana Surge
    script, w3i = loot_balance.bump_version(script, w3i, 6, 4, version)
    files = {'scripts\\war3map.j': script.encode('latin-1'), 'war3map.w3i': w3i}
    for name in sorted(files):
        print('%-24s %9d bytes' % (name, len(files[name])))
    if dry:
        print('dry run: nothing written (would write %s)' % out)
        return
    if os.path.exists(out):
        raise SystemExit('refusing to overwrite %s' % out)
    listfile = sorted(set(base.listfile()) | set(files))
    # the archive has a full listfile: re-lay the hash table by those names only (reading every file of the
    # 150 MB map for more names would be slow); entries without a known name are kept by mpq
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    version = open(os.path.join(HERE, 'version.txt')).read().strip()
    build(a.out or os.path.join(MAPS, 'Pokemon Arena v%s.w3x' % version), a.dry_run, version)


if __name__ == '__main__':
    main()
