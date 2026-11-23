"""Pokemon Arena v4.1.2-ver2: the v4.1.2 map with the ideas of both patch notes that fit it.

From the v4.1.x line: loot balance per camp, soft cap for loot Max HP, stronger Storm Shock / Soul Burn / Mana Surge.
From the v4.3 line: gyms in order with a minimum level, -gym / gym busy message / stuck-gym fixes / easy gyms 1-4,
-repick = one random Pokemon, Poke Center mana as fast as HP. Not portable (they need the 3.4.16 engine): status
moves and stages, move effects, starters, Team Rocket, quests. Dynamax and the x20 boss numbers are ported.

    python -I tools/v412/build_ver2.py [--dry-run]     -> ..\Pokemon Arena v4.1.2-ver2.w3x (never overwrites)
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v3411'))
sys.path.insert(0, HERE)
import mpq  # noqa: E402
import slk  # noqa: E402
import loot_balance  # noqa: E402
import loot_hp  # noqa: E402
import charm_buff  # noqa: E402
import gym_order  # noqa: E402
import gym342  # noqa: E402
import repick_random  # noqa: E402
import dynamax  # noqa: E402
import fx_more  # noqa: E402
import boss_buff  # noqa: E402
import objdata  # noqa: E402
import importlib.util  # noqa: E402

BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.2.w3x')
NAME = 'v4.1.2-ver2'


def _v3411_build():
    spec = importlib.util.spec_from_file_location('v3411_build', os.path.join(WORK, 'tools', 'v3411', 'build.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules['v3411_build'] = mod
    spec.loader.exec_module(mod)
    return mod


def _fx_effects(s, entries):
    """fx_more.patch_script without its PkFx_Badges part (badges, leaders, regional forms, Rocket, Max Move blasts:
    those need 3.4.16 globals; the blasts are done by dynamax_data.j): only the per-move effect data."""
    data, calls = fx_more.jass(entries)
    anchor = 'function PkFx_Init takes nothing returns nothing\n'
    hook = '    call TriggerRegisterAnyUnitEventBJ(fxTrig, EVENT_PLAYER_UNIT_SPELL_EFFECT)\n'
    if s.count(anchor) != 1:
        raise SystemExit('fx effects: PkFx_Init not found once')
    s = s.replace(anchor, data + '\n' + anchor)
    pos = s.index(hook, s.index(anchor))
    return s[:pos] + calls + s[pos:]


def lf(fn, s):
    """run a module that expects LF line ends on a CRLF script"""
    return fn(s.replace('\r\n', '\n')).replace('\n', '\r\n')


def build(out, dry):
    base = mpq.MPQ(BASE_MAP)
    script = base.read('scripts\war3map.j').decode('latin-1')
    script = script.replace('\r\r\n', '\r\n')  # a few regions use CR CR LF
    w3i = base.read('war3map.w3i')
    script = loot_balance.patch_script(script)
    script = loot_hp.patch_script(script)
    script = charm_buff.patch_script(script)
    script = lf(gym342.patch_script, script)
    script = lf(gym_order.patch_script, script)
    script = lf(repick_random.patch_script, script)
    script = lf(dynamax.patch_script, script)  # Dynamax
    script = lf(boss_buff.patch_script, script)  # random legends: HP x20, attack x5, armor x3
    if script.count('v4.1.2') != 6 or w3i.count(b'v4.1.2') != 4:
        raise SystemExit('version text not found as expected')
    script = script.replace('v4.1.2', NAME)
    w3i = w3i.replace(b'v4.1.2', NAME.encode('latin-1'))  # w3i strings end with a zero byte: the length may change
    abil = slk.Slk(base.read('Units\AbilityData.slk').decode('latin-1'))
    row = abil.find('ANre')
    if row is None or abil.get(row, 'DataA1') != '0.05':
        raise SystemExit('ANre (Poke Center mana aura) not found or not 0.05')
    row[abil.name_to_x['DataA1']] = '0.15'  # Poke Center: mana as fast as HP (ACnr is 0.15)
    # Dynamax Band (IDMX) and its ability (ADMX), sold by the item shop n00Q
    vb = _v3411_build()
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    strings = base.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
    func = base.read('Units\\ItemFunc.txt').decode('utf-8', 'replace')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    shop = next(o for o in w3u.custom if o.new == 'n00Q')
    strings, func = dynamax.objects(abil, items, strings, func, shop.mods, vb.set_keys, vb.copy_section)
    # effects for the 169 damaging moves (and the status moves) the v3.4.9 engine left without one (tools/v3411/fx_more.py)
    orig = base.read('scripts\\war3map.j').decode('latin-1').replace('\r\r\n', '\r\n').replace('\r\n', '\n')
    secs = fx_more.parse_strings(strings)
    entries, pw_models = fx_more.plan(orig, abil, secs)
    script = lf(lambda t: _fx_effects(t, entries), script)
    col = abil.name_to_x
    buff_cols = [c for c in col if re.match(r'(BuffID|EfctID)\d+$', c)]
    move_entries = [e for e in entries if not e[2].get('status')]
    for e in move_entries:
        row = abil.find(e[1])
        if row is None:
            raise SystemExit('fx_more: ability %s not found' % e[1])
        for c in buff_cols:  # the moves with new effects use the art-less buff copies of v3.4.9
            v = abil.get(row, c)
            if v:
                nv = ','.join(fx_more.BUFF_COPY.get(b, b) for b in v.split(','))
                if nv != v:
                    row[col[c]] = '"%s"' % nv
    for e in move_entries:  # old art off; melee missile moves travel at the dash speed
        pairs = [(k, '') for k in fx_more.ART_KEYS]
        base_code = abil.get(abil.find(e[1]), 'code')
        if e[2]['melee'] and base_code in fx_more.MISSILE_BASES:
            pairs.append(('Missilespeed', '%d' % int(e[2]['dash'])))
        strings = vb.set_keys(strings, e[1], pairs)
    have = {n.lower() for n in base.listfile()}
    extra = {}
    for path, data in fx_more.pw_files(sorted(pw_models)).items():  # Pokemon World effect models (+ textures)
        if path.lower() in have:
            if base.read(path) != data:
                raise SystemExit('fx_more: %s already in the map with other content' % path)
        else:
            extra[path] = data
    files = {'scripts\war3map.j': script.encode('latin-1'), 'war3map.w3i': w3i,
             'Units\AbilityData.slk': abil.to_text().encode('latin-1'),
             'Units\\ItemData.slk': items.to_text().encode('latin-1'), 'Units\\CampaignAbilityStrings.txt': strings.encode('utf-8'),
             'Units\\ItemFunc.txt': func.encode('utf-8'), 'war3map.w3u': w3u.to_bytes()}
    files.update(extra)  # the Pokemon World effect models
    for n in sorted(files):
        print('%-24s %9d bytes' % (n, len(files[n])))
    if dry:
        print('dry run: nothing written (would write %s)' % out)
        return
    if os.path.exists(out):
        raise SystemExit('refusing to overwrite %s' % out)
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'), hash_size=None, extra_names=listfile)
    print('wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    build(a.out or os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME), a.dry_run)
