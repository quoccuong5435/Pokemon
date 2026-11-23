"""v4.1.3: every monster camp gives the same expected loot.

v4.1.2 drops item loot with a fixed chance per kill (elite 15%, normal creep 5%) and every camp has exactly one elite
(`Wild_SpawnCamp`), so a camp of `size` creeps was worth 15 + 5 * (size - 1) percent of a loot item per clear: 0.20 for
a camp of 2, 0.70 for the camp of 12. Now the chance of the creeps of a camp is multiplied by
`PAX_Loot_CampFactor` = 32 / (15 + 5 * (size - 1)), so every camp is worth 0.32 (the average of the 55 camps, so the
total amount of loot stays the same). Legends / fixed bosses and creeps that are not part of a camp are unchanged.

`patch_script(s)` works on the raw script of the v4.1.2 map (CRLF line ends); a missing anchor raises ValueError.
"""

FACTOR = '''// v4.1.3: every camp is worth the same loot. A camp has 1 elite (15%) and size - 1 normal creeps (5%), so a clear
// was worth 15 + 5 * (size - 1) percent of a loot item. The chance of its creeps is scaled to the average camp (32).
function PAX_Loot_CampFactor takes unit dead returns real
    local integer c = LoadInteger(Mega_HT, GetHandleId(dead), 25) - 1
    local integer size = 0
    if c < 0 or c >= Wild_CampN then
        return 1.0
    endif
    set size = Wild_CampSize[c]
    if size < 1 then
        return 1.0
    endif
    return 32.0 / (15.0 + 5.0 * I2R(size - 1))
endfunction
'''

APPLY = '''    if not isLegend then  // v4.1.3: the same expected loot for every camp
        set chance = RMinBJ(100.0, chance * PAX_Loot_CampFactor(dead))
    endif
'''


def _crlf(text):
    return text.replace('\r\n', '\n').replace('\n', '\r\n')


def _rep(s, old, new, count=1):
    old, new = _crlf(old), _crlf(new)
    n = s.count(old)
    if n != count:
        raise ValueError('loot_balance: expected %d match(es), found %d:\n%s' % (count, n, old[:300]))
    return s.replace(old, new)


def patch_script(s):
    s = _rep(s, 'function PAX_Loot_OnDeath takes', FACTOR + '\nfunction PAX_Loot_OnDeath takes')
    s = _rep(s, '    if PAX_Loot_TestMode and (isLegend or isElite or isWild) then\n',
             APPLY + '    if PAX_Loot_TestMode and (isLegend or isElite or isWild) then\n')
    return s


def bump_version(script, w3i, expect_script, expect_w3i, version='4.1.3'):
    """v4.1.2 -> v<version> in the script (SetMapName, texts) and in war3map.w3i (it needs the same length)."""
    if len(version) != len('4.1.2'):
        raise ValueError('loot_balance: the version must have the length of 4.1.2 (the w3i text is patched in place)')
    if script.count('v4.1.2') != expect_script or w3i.count(b'v4.1.2') != expect_w3i:
        raise ValueError('loot_balance: version text found %d times in the script, %d in the w3i'
                         % (script.count('v4.1.2'), w3i.count(b'v4.1.2')))
    return script.replace('v4.1.2', 'v' + version), w3i.replace(b'v4.1.2', ('v' + version).encode('latin-1'))
