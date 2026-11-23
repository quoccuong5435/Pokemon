"""Build Pokemon Arena v4.1.3 on top of the finished ver2o map.

What changes against ver2o:
  * Effect wiring: the Dota 2, Tranquil (Varioius Spells) and Wight models that ver2o packs but never uses are
    used INSTEAD of the old PkFx effects (old layers removed) for every move that already has a PkFx effect set.
    The model depends on the move type and on the move shape:
      tgt  = hit on the target spot / target unit (PkFx modes 0, 2, 4)
      nova = burst around the caster (PkFx mode 1)
      line = end of a line / cone move (PkFx mode 3)
    Melee dash moves (slot 90) are left alone.
  * Version text 4.1.3 in the script and war3map.w3i.
Nothing else is touched. The scale / life of every model is in EFX below, so tuning after an in-game test is a
one-line change.
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
sys.path.insert(0, HERE)

import mpq  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2o.w3x')
NAME = 'v4.1.3b'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')

B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
TYPES = ['Bug', 'Dark', 'Dragon', 'Electr', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass',
         'Ground', 'Ice', 'Normal', 'Poison', 'Psy', 'Rock', 'Steel', 'Water']

BS = chr(92)
T = 'Spells' + BS + 'Tranquil' + BS
W = 'Spells' + BS + 'Wight' + BS
D = 'Dota2Fx' + BS

# type -> (tgt, nova, line); each = (model, scale, life seconds)
EFX = {
    'Bug':      ((D + 'SpiderlingsVenom.mdx', 1.0, 1.5), (D + 'SpiderlingsBirth.mdx', 0.6, 2.0), (D + 'PoisonAttack.MDX', 1.0, 1.5)),
    'Dark':     ((T + 'Shadow Blast.mdx', 1.0, 2.0), (D + 'ScreamOfPain.mdx', 0.5, 2.0), (D + 'ShadowStrikeBuff.mdx', 1.0, 1.5)),
    'Dragon':   ((D + 'HellFireTarget.mdx', 1.0, 1.5), (D + 'NetherBlast.mdx', 0.35, 2.0), (T + 'Dragonhawk Attachment.mdx', 1.5, 1.5)),
    'Electr':   ((T + 'Lightning Bolt Small.mdx', 1.0, 1.5), (T + 'Shock Effect.mdx', 1.5, 1.5), (T + 'Lightning Bolt Big.mdx', 1.0, 1.5)),
    'Fairy':    ((T + 'Holy Blessing.mdx', 1.0, 1.5), (T + 'Purify Target.mdx', 1.5, 2.0), (T + 'Arcane Bolt White.mdx', 1.0, 1.5)),
    'Fighting': ((T + 'Stun Small.mdx', 1.0, 1.5), (T + 'Battle Cry.mdx', 1.5, 2.0), (T + 'Stun Small.mdx', 1.5, 1.5)),
    'Fire':     ((D + 'HellFireTarget.mdx', 1.0, 1.5), (T + 'Fire Nova.mdx', 1.5, 2.0), (T + 'Fire Effect.mdx', 1.5, 1.5)),
    'Flying':   ((D + 'Up.MDX', 0.5, 2.0), (D + 'SonicWave.mdx', 0.8, 2.0), (D + 'SonicWave.mdx', 0.5, 1.5)),
    'Ghost':    ((W + 'DeathCurse.mdx', 1.0, 1.5), (W + 'ExpirationAura.mdx', 1.0, 1.5), (W + 'SpiritBolt.mdx', 1.0, 1.5)),
    'Grass':    ((T + 'Nature Attachment.mdx', 1.5, 1.5), (T + 'Health Boon.mdx', 1.5, 1.5), (T + 'Nature Attachment.mdx', 1.5, 1.5)),
    'Ground':   ((D + 'AfterShock.MDX', 0.8, 2.0), (D + 'EchoSlamCaster.MDX', 0.3, 2.0), (D + 'AfterShock.MDX', 0.45, 2.0)),
    'Ice':      ((D + 'ColdFeetTarget.MDX', 1.0, 1.5), (T + 'Frost Nova.mdx', 1.5, 2.0), (T + 'Frost Effect.mdx', 1.5, 1.5)),
    'Normal':   ((T + 'Enchant.mdx', 1.0, 1.5), (D + 'SonicWave.mdx', 0.8, 2.0), (T + 'Enchant.mdx', 1.5, 1.5)),
    'Poison':   ((D + 'ViperStrike.MDX', 1.0, 1.5), (T + 'Poison Cloud Arrow.mdx', 1.5, 1.5), (D + 'PoisonAttack.MDX', 1.0, 1.5)),
    'Psy':      ((T + 'Arcane Burn.mdx', 1.0, 1.5), (T + 'Arcane Blast.mdx', 1.5, 2.0), (T + 'Arcane Missile.mdx', 1.0, 1.5)),
    'Rock':     ((D + 'AfterShock.MDX', 0.7, 2.0), (D + 'EchoSlamCaster.MDX', 0.3, 2.0), (D + 'AfterShock.MDX', 0.4, 2.0)),
    'Steel':    ((W + 'DiskOfScythes.mdx', 0.7, 2.0), (W + 'DiskOfScythes.mdx', 0.9, 2.0), (T + 'Shock Attachment.mdx', 1.5, 1.5)),
    'Water':    ((T + 'Tide Effect.mdx', 1.5, 1.5), (T + 'Sea Effect.mdx', 2.0, 1.5), (T + 'Deep Effect.mdx', 1.5, 1.5)),
}

IMPACT_OLD = '    call PkFx_Layer(fxIdx, 70, fxX, fxY, fxYaw, fxDelay + 0.1)\n'
IMPACT_NEW = IMPACT_OLD + '    call PkFx_Layer(fxIdx, 80, fxX, fxY, fxYaw, fxDelay + 0.05)\n'
INIT_OLD = '    call ExecuteFunc("PkFx_Data10")\n'
INIT_NEW = INIT_OLD + '    call ExecuteFunc("V413_FxData")\n'


def from_b36(tag):
    return B36.index(tag[0]) * 36 + B36.index(tag[1])


def jstr(s):
    return s.replace(BS, BS + BS)


def make_fx_data(script, have):
    mv_type = {int(a): int(b) for a, b in re.findall(r'set Mv_Type\[(\d+)\] = (-?\d+)', script)}
    abil = re.findall(r"SaveInteger\(PkFx_HT, '(\w{4})', 0, (\d+)\)", script)
    mode = {int(a): int(b) for a, b in re.findall(r'SaveInteger\(PkFx_HT, (\d+), 0, (\d+)\)', script)}
    melee = {int(a) for a in re.findall(r'SaveInteger\(PkFx_HT, (\d+), 90, 1\)', script)}
    idx_type = {}
    for a, i in abil:
        try:
            mi = from_b36(a[2:])
        except ValueError:
            continue
        t = mv_type.get(mi, -1)
        if 0 <= t < len(TYPES):
            idx_type.setdefault(int(i), t)
    lines = ['function V413_FxData takes nothing returns nothing']
    stats = {'tgt': 0, 'nova': 0, 'line': 0, 'skip': 0}
    for i in sorted(idx_type):
        if i in melee or i not in mode:
            stats['skip'] += 1
            continue
        md = mode[i]
        cls = 1 if md == 1 else (2 if md == 3 else 0)
        model, scale, life = EFX[TYPES[idx_type[i]]][cls]
        assert model.lower() in have, model
        stats[('tgt', 'nova', 'line')[cls]] += 1
        # remove every old layer (missile 10, impact 20, 30, trail 40, ring 50, caster 60, extra 70)
        for slot in (10, 20, 30, 40, 50, 60, 70):
            lines.append('    call RemoveSavedString(PkFx_HT, %d, %d)' % (i, slot))
        lines.append('    call SaveInteger(PkFx_HT, %d, 6, 1)' % i)
        lines.append('    call SaveInteger(PkFx_HT, %d, 8, 0)' % i)
        lines.append('    call SaveStr(PkFx_HT, %d, 20, "%s")' % (i, jstr(model)))
        lines.append('    call SaveReal(PkFx_HT, %d, 21, %.2f)' % (i, scale))
        lines.append('    call SaveReal(PkFx_HT, %d, 22, %.2f)' % (i, life))
        if cls == 2:  # line / cone: the same model repeated along the whole length
            lines.append('    call SaveStr(PkFx_HT, %d, 40, "%s")' % (i, jstr(model)))
            lines.append('    call SaveReal(PkFx_HT, %d, 41, %.2f)' % (i, scale))
            lines.append('    call SaveReal(PkFx_HT, %d, 42, %.2f)' % (i, life))
            lines.append('    call SaveReal(PkFx_HT, %d, 7, 160.0)' % i)
    lines.append('endfunction')
    return '\n'.join(lines) + '\n\n', stats


def build_data():
    base = mpq.MPQ(BASE_MAP)
    have = {n.lower() for n in base.listfile()}
    script = base.read('scripts' + BS + 'war3map.j').decode('utf-8')
    crlf = '\r\n' in script
    script = script.replace('\r\n', '\n')
    for old in (INIT_OLD, 'function PkFx_Init takes nothing returns nothing\n'):
        if script.count(old) != 1:
            raise SystemExit('anchor not found exactly once: %r (%d)' % (old, script.count(old)))
    fx, stats = make_fx_data(script, have)
    script = script.replace(INIT_OLD, INIT_NEW, 1)
    script = script.replace('function PkFx_Init takes nothing returns nothing\n', fx + 'function PkFx_Init takes nothing returns nothing\n', 1)
    script = re.sub(r'v4\.1\.2-ver2o', NAME, script)
    if crlf:
        script = script.replace('\n', '\r\n')
    w3i = base.read('war3map.w3i').replace(b'v4.1.2-ver2o', NAME.encode('latin-1')).replace(b'ver2o', b'4.1.3b')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i}
    return base, files, script, stats


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base, files, script, stats = build_data()
    print('PkFx effect sets patched:', stats)
    if dry:
        print('Dry run OK, nothing written.')
        return
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))
    if os.path.exists(PJASS):
        tmp = os.path.join(REF, '_tmp_v413_war3map.j')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                           capture_output=True, text=True)
        o = (r.stdout + r.stderr).strip()
        print('PJASS rc=%d' % r.returncode)
        print('\n'.join(o.splitlines()[:10]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
