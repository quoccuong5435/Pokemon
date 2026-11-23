"""v4.1.2-ver2: Dynamax (item Dynamax Band IDMX, ability ADMX) ported from the 3.4.16 pipeline (tools/v3411).

Level 20+ Pokemon: 20 s twice as big, max HP x1.5, every move is a Max Move (+50% damage and a big blast of its type
through PkFx_OnCast). Cooldown 150 s, usable again and again. The JASS is taken from tools/v3411/jass (the same text
as in 4.3.x), `patch_script(s)` works on the script with LF line ends and raises ValueError on a missing anchor.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
JASS = os.path.join(os.path.dirname(HERE), 'v3411', 'jass')


def _fn(text, name):
    m = re.search(r'(?ms)^function %s takes.*?^endfunction\n' % name, text)
    if not m:
        raise ValueError('dynamax: function %s not found in the source' % name)
    return m.group(0)


def _rep(s, old, new):
    if s.count(old) != 1:
        raise ValueError('dynamax: expected 1 match, found %d:\n%s' % (s.count(old), old[:200]))
    return s.replace(old, new)


def patch_script(s):
    src = open(os.path.join(JASS, 'fx_main.j'), encoding='utf-8').read().replace('\r\n', '\n')
    glob = open(os.path.join(JASS, 'fx_globals.j'), encoding='utf-8').read().replace('\r\n', '\n')
    lines = [l for l in glob.split('\n') if re.match(r'(constant (integer|real) Fx_Dyna\w+|string array Fx_MaxFx|real array Fx_MaxScale)', l)]
    if len(lines) != 7:
        raise ValueError('dynamax: expected 7 global lines, found %d' % len(lines))
    s = _rep(s, '\nendglobals', '\n' + '\n'.join(lines) + '\nendglobals')
    funcs = ''.join(_fn(src, n) + '\n' for n in ('Fx_IsDyna', 'Fx_DynaEnd', 'Fx_DynaCast'))
    s = _rep(s, 'function Fx_Tick takes', funcs + 'function Fx_Tick takes')
    s = _rep(s, '        set mult = mult * Fx_StageMult(src, 3)\n    endif\n',
             '        set mult = mult * Fx_StageMult(src, 3)\n    endif\n'
             '    if skill and Mega_Time < LoadReal(Fx_HT, hs, 87) then  // Dynamax Max Move\n        set mult = mult * Fx_DynaDmg\n    endif\n')
    s = _rep(s, 'Aqua Ring / Ingrain: 2% per second\n                call Ab_Heal(u, 0.01 * I2R(BlzGetUnitMaxHP(u)))\n            endif\n',
             'Aqua Ring / Ingrain: 2% per second\n                call Ab_Heal(u, 0.01 * I2R(BlzGetUnitMaxHP(u)))\n            endif\n'
             '            if HaveSavedReal(Fx_HT, hand, 87) and Mega_Time >= LoadReal(Fx_HT, hand, 87) then  // Dynamax over\n'
             '                call Fx_DynaEnd(u)\n            endif\n')
    tail = '    set fxCaster = null\n    set fxTarget = null\n    return false\nendfunction\n'
    i = s.find('function PkFx_OnCast takes')
    j = s.find(tail, i)
    if i < 0 or j < 0 or s.find('endfunction', i) != j + len(tail) - len('endfunction\n'):
        raise ValueError('dynamax: tail of PkFx_OnCast not found')
    blast = ('    if Fx_IsDyna(fxCaster) then  // Max Move\n        set fxStep = Ty_MoveOf(fxAbil)\n'
             '        if fxStep >= 0 and Mv_Type[fxStep] >= 0 and Fx_MaxFx[Mv_Type[fxStep]] != "" then\n'
             '            call PkFx_At(Fx_MaxFx[Mv_Type[fxStep]], fxDstX, fxDstY, fxAngle, Fx_MaxScale[Mv_Type[fxStep]], 2.0, 0.3)\n'
             '        endif\n    endif\n')
    s = s[:j] + blast + s[j:]
    data = open(os.path.join(HERE, 'dynamax_data.j'), encoding='utf-8').read().replace('\r\n', '\n')
    s = _rep(s, 'function Fx_Init takes', data + 'function Fx_Init takes')
    s = _rep(s, '    call ExecuteFunc("Fx_Texts")\n', '    call ExecuteFunc("Fx_Texts")\n    call ExecuteFunc("Dyna_Data")\n')
    return s


DYN_TEXT = ('Dynamax for 20s: twice as big, +50% max HP, every move is a Max Move (+50% damage and a big blast'
            ' of its type). Cooldown 150s. Pokemon of level 20 or more.')
DYN_ICON = 'ReplaceableTextures\\CommandButtons\\BTNBerserk.blp'


def objects(abil, items, strings, func, shop_mods, set_keys, copy_section):
    """ADMX (a copy of the Mega Evolve ability AM0W with its own order) and IDMX (a copy of the Mega Stone IM0W), sold by
    the item shop (shop_mods = the mods of unit n00Q). Returns the new (strings, func) texts."""
    if abil.find('ADMX') is not None or items.find('IDMX') is not None:
        raise ValueError('dynamax: ids ADMX / IDMX already used')
    row = dict(abil.find('AM0W'))
    row[1] = '"ADMX"'
    row[abil.name_to_x['DataF1']] = '"robogoblin"'
    row[abil.name_to_x['Cool1']] = '150'
    abil.rows.append(row)
    row = dict(items.find('IM0W'))
    row[1] = '"IDMX"'
    row[items.name_to_x['abilList']] = '"ADMX"'
    row[items.name_to_x['goldcost']] = '8000'
    items.rows.append(row)
    strings = copy_section(strings, 'AM0W', 'ADMX')
    strings = set_keys(strings, 'ADMX', [('Name', 'Dynamax'), ('Art', DYN_ICON), ('Tip', '|cffff5080Dynamax|r'),
                                         ('Ubertip', '"%s"' % DYN_TEXT), ('Order', 'robogoblin')])
    func = copy_section(func, 'IM0W', 'IDMX')
    func = set_keys(func, 'IDMX', [('Name', 'Dynamax Band'), ('Tip', 'Purchase |cffff5080Dynamax Band|r'),
                                   ('Ubertip', '"|cffffcc00Use (click in the inventory):|r %s"' % DYN_TEXT),
                                   ('Description', 'Lets a Pokemon Dynamax again and again.'), ('Art', DYN_ICON)])
    for md in shop_mods:
        if md.field == 'usei' and 'IDMX' not in md.value:
            md.value = md.value + ',IDMX'
    return strings, func
