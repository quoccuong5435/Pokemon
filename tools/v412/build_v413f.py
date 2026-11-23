"""Build Pokemon Arena v4.1.3f on top of v4.1.3e.

  1. Gym 8 badge: the flat -35 armor aura is replaced by "the holder's hits ignore 20% of the target's armor"
     (script, in Ab_OnDamaging; armor math of Warcraft III: damage taken = 1 / (1 + 0.06 x armor)).
  2. Items that had no code at all now work:
       Eject Button (IB0C): +15 armor (item ability); below 30% HP it blinks 700 away from the nearest enemy
         (60 s cooldown, not during a gym / League battle).
       Heavy-Duty Boots (IB0D): +60 movement speed (item ability); damage from legend-land traps and hazards
         (the Env_IsSource units) is blocked. The old text also promised "terrain slow" immunity: not coded, text fixed.
  3. Silk Scarf (Normal): +10 -> +20 all stats and +1000 -> +3000 max HP.
  4. Amulet Coin (+50% gold) is removed from the Item Shop (loot already gives gold).
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
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3e.w3x')
NAME = 'v4.1.3f'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')

FUNCS = '''// v4.1.3f: Gym 8 badge, Eject Button
function V413_ArmorCut takes unit t returns real
    local real a = BlzGetUnitArmor(t)
    if a <= 0.0 then
        return 1.0
    endif
    return (1.0 + 0.06 * a) / (1.0 + 0.048 * a)
endfunction

function V413_Eject takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer pid = GetPlayerId(GetOwningPlayer(u))
    local group g = null
    local unit e = null
    local unit best = null
    local real bd = 1000000000.0
    local real d = 0.0
    local real ang = 0.0
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    if pid >= 12 or Mega_Time < LoadReal(Fx_HT, h, 187) then
        return
    endif
    if GetWidgetLife(u) > 0.30 * I2R(BlzGetUnitMaxHP(u)) or Gym_Busy(pid) then
        return
    endif
    set g = CreateGroup()
    call GroupEnumUnitsInRange(g, x, y, 700.0, null)
    loop
        set e = FirstOfGroup(g)
        exitwhen e == null
        call GroupRemoveUnit(g, e)
        if GetWidgetLife(e) > 0.405 and IsUnitEnemy(e, GetOwningPlayer(u)) and not IsUnitType(e, UNIT_TYPE_STRUCTURE) then
            set d = (GetUnitX(e) - x) * (GetUnitX(e) - x) + (GetUnitY(e) - y) * (GetUnitY(e) - y)
            if d < bd then
                set bd = d
                set best = e
            endif
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    if best != null then
        set ang = Atan2(y - GetUnitY(best), x - GetUnitX(best))
        call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", x, y))
        call SetUnitPosition(u, x + 700.0 * Cos(ang), y + 700.0 * Sin(ang))
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", u, "origin"))
        call SaveReal(Fx_HT, h, 187, Mega_Time + 60.0)
    endif
    set best = null
    set e = null
endfunction

'''


def once(s, old, new):
    if s.count(old) != 1:
        raise SystemExit('anchor count %d: %r' % (s.count(old), old[:80]))
    return s.replace(old, new, 1)


def patch_script(s):
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    s = once(s, 'function Ver2n_Tick takes nothing returns nothing\n', FUNCS + 'function Ver2n_Tick takes nothing returns nothing\n')
    s = once(s, '            // 1. Dragon Ascent permanent buff regen\n',
             "            if Itm_Has(u, 'IB0C') then\n                call V413_Eject(u)\n            endif\n            // 1. Dragon Ascent permanent buff regen\n")
    s = once(s, '        set m = m * Env_DamageMult\n    endif\n',
             "        set m = m * Env_DamageMult\n    endif\n"
             "    if Env_IsSource(GetUnitTypeId(src)) and Itm_Has(t, 'IB0D') then  // v4.1.3f: Heavy-Duty Boots\n        set m = 0.0\n    endif\n")
    s = once(s, "    if Itm_Has(src, 'IGW1') then",
             "    if Itm_Has(src, 'I01B') then  // v4.1.3f: Gym 8 badge, ignore 20%% of the target's armor\n        set m = m * V413_ArmorCut(t)\n    endif\n    if Itm_Has(src, 'IGW1') then".replace('%%', '%'))
    s = s.replace('v4.1.3e', NAME)
    return s.replace('\n', '\r\n') if crlf else s


def set_func_text(func, k, old, new):
    a = func.index('[%s]' % k)
    m = re.search(r'\n\[', func[a + 1:])
    b = a + 1 + m.start() if m else len(func)
    sec = func[a:b]
    if old not in sec:
        raise SystemExit('text not found in %s: %r' % (k, old))
    return func[:a] + sec.replace(old, new) + func[b:]


def patch_objects(abil, items, func, w3u):
    icol = items.name_to_x
    acol = abil.name_to_x
    # new item abilities (copies of the existing AIde / AIms rows)
    for new, src, val in (('AXAF', 'AXA4', '15'), ('AXS6', 'AXS4', '60')):
        assert abil.find(new) is None
        r = dict(abil.find(src))
        r[1] = '"%s"' % new
        r[acol['DataA1']] = val
        abil.rows.append(r)
    items.find('IB0C')[icol['abilList']] = '"AXAF"'
    items.find('IB0D')[icol['abilList']] = '"AXS6"'
    # gym 8 aura off (the effect is the script now)
    abil.find('A040')[acol['DataA1']] = '0'
    # Silk Scarf
    n = sum(1 for r in items.rows if any(a in (items.unquote(r.get(icol['abilList'])) or '') for a in ('A03O', 'A03N')))
    assert n == 1, n
    abil.find('A03O')[acol['DataA1']] = '3000'
    for c in ('DataA1', 'DataB1', 'DataC1'):
        abil.find('A03N')[acol[c]] = '20'
    func = set_func_text(func, 'I00Z', '+10 all stats, +1000 HP', '+20 all stats, +3000 HP')
    func = set_func_text(func, 'I01B', 'Reduce 35 armor Aura.', "Its holder's hits ignore 20% of the target's armor.")
    func = set_func_text(func, 'IB0D', 'Grants 100% immunity to ground traps, hazards, and terrain slow effects.',
                         'Blocks all damage from legend-land traps and hazards.')
    # Amulet Coin out of the shop
    shop = w3u.find('nIS0')
    cur = shop.get('usei').split(',')
    assert 'IT01' in cur
    cur.remove('IT01')
    shop.set('usei', 3, ','.join(cur))
    return func, cur


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = patch_script(base.read('scripts' + BS + 'war3map.j').decode('utf-8'))
    abil = slk.Slk(base.read('Units' + BS + 'AbilityData.slk').decode('latin-1'))
    items = slk.Slk(base.read('Units' + BS + 'ItemData.slk').decode('latin-1'))
    func = base.read('Units' + BS + 'ItemFunc.txt').decode('utf-8')
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    func, shop = patch_objects(abil, items, func, w3u)
    print('Item Shop now:', ','.join(shop))
    w3i = base.read('war3map.w3i').replace(b'4.1.3e', b'4.1.3f')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i,
             'war3map.w3u': w3u.to_bytes(),
             'Units' + BS + 'AbilityData.slk': abil.to_text().encode('latin-1'),
             'Units' + BS + 'ItemData.slk': items.to_text().encode('latin-1'),
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
        tmp = os.path.join(REF, '_tmp_v413f_war3map.j')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                           capture_output=True, text=True)
        print('PJASS rc=%d' % r.returncode)
        if r.returncode:
            print((r.stdout + r.stderr)[:1000])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
