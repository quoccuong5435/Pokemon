"""Run the real pjass compiler (with the common.j/Blizzard.j extracted to analysis/jass_ref) on the script of a map."""
import os
import subprocess
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402

PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join('analysis', 'jass_ref')


def check(map_path, keep=None):
    script = mpq.MPQ(map_path).read('scripts\\war3map.j')
    path = keep or os.path.join(REF, '_tmp_war3map.j')
    open(path, 'wb').write(script)
    r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), path],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip().replace('\r', '')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        out = check(p)
        lines = out.split('\n')
        print('==', os.path.basename(p), '|', len(lines), 'lines of output')
        print('\n'.join(lines[:12]))
