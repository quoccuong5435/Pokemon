"""Run the real pjass compiler on v34/war3map.j (any error = the lobby says the map is unavailable or corrupted).

    python -I tools/v34/check.py [script.j]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')


def check(path):
    r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), path],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip().replace('\r', ''), r.returncode


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'v34', 'war3map.j')
    out, code = check(path)
    lines = out.split('\n')
    errors = [l for l in lines if not l.startswith('Parse successful')]
    print('\n'.join(errors[:60]) if errors else '\n'.join(lines))
    print('pjass exit %d, %d error lines' % (code, len(errors)))
    sys.exit(1 if errors else 0)
