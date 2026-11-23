"""v4.1.4: Max HP from loot items has a soft cap instead of a hard one.

v4.1.3 (and v4.1.2) cut the total Max HP of all loot items at +15,000 (`PAX_TestItem_SyncEx`: `if newHP > 15000
then set newHP = 15000`), so a hero with 10,000 HP and 23,000 HP of loot ended with 25,000 and the second relic was
wasted without a word. Now the first 15,000 count in full and everything above counts half (23,000 of loot -> 19,000,
10,000 + 19,000 = 29,000). The raw total is kept (PAX_Item_HT key 130 of the hero), the player gets a message when the
loot is over the soft cap, and `-me` shows the raw total and the caps of Lifesteal (25%) and Crit (60%).

`patch_script(s)` works on the raw script (CRLF line ends); a missing anchor raises ValueError.
"""
from loot_balance import _rep

SOFT_CAP = 15000


def patch_script(s):
    # ---- the soft cap
    s = _rep(s, '    if newHP > 15000 then\n        set newHP = 15000\n    endif\n',
             '    // v4.1.4: soft cap: the first 15,000 Max HP of loot count in full, the rest half (was a hard cap)\n'
             '    call SaveInteger(PAX_Item_HT, h, 130, newHP)  // raw total, for the message and -me\n'
             '    if newHP > 15000 then\n        set newHP = 15000 + (newHP - 15000) / 2\n    endif\n')
    # ---- tell the player when the loot is over the soft cap (only when the counted HP changes)
    s = _rep(s, '    if newHP != oldHP then\n        set lifePct = GetUnitLifePercent(u)\n',
             '    if newHP != oldHP then\n'
             '        if LoadInteger(PAX_Item_HT, h, 130) > 15000 then  // v4.1.4\n'
             '            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cffffcc00[LOOT] Max HP from loot: +" + '
             'I2S(LoadInteger(PAX_Item_HT, h, 130)) + ", counted +" + I2S(newHP) + " (the first 15,000 count in full, the rest half).|r")\n'
             '        endif\n'
             '        set lifePct = GetUnitLifePercent(u)\n')
    # ---- -me
    s = _rep(s, '    local integer rHp = 0\n', '    local integer rHp = 0\n    local string hpNote = ""  // v4.1.4\n')
    s = _rep(s, '    set rHp = LoadInteger(PAX_Item_HT, h, 104)\n',
             '    set rHp = LoadInteger(PAX_Item_HT, h, 104)\n'
             '    if LoadInteger(PAX_Item_HT, h, 130) > 15000 then  // v4.1.4\n'
             '        set hpNote = " (of " + I2S(LoadInteger(PAX_Item_HT, h, 130)) + ": the first 15,000 in full, the rest half)"\n'
             '    endif\n')
    s = _rep(s, '+ I2S(rHp) + " HP")', '+ I2S(rHp) + " HP" + hpNote)')
    s = _rep(s, 'Lifesteal " + I2S(lsPct) + "%  |  Crit " + I2S(critPct) + "%  |  Thorns "',
             'Lifesteal " + I2S(lsPct) + "% (max 25%)  |  Crit " + I2S(critPct) + "% (max 60%)  |  Thorns "')
    return s
