"""v4.1.5: the three weak Effect Charms get stronger (raw v4.1.x script, CRLF; a missing anchor raises ValueError).

Storm Shock: 30% chance / 2 s -> 45% / 1.2 s, damage 25/45/70/100% -> 50/80/120/170% of the main stat.
Soul Burn: besides % of the target's current HP (useless on small targets) each tick also deals main stat x 2% x pct
  (pct = 10/15/22/30 for the four tiers).
Mana Surge: twice the mana per hit (3/5/7/10% of max mana). Charms already dropped keep their stored numbers.
"""
from loot_balance import _rep

STORM_OLD = '''            if tier == 1 then
                set effectVal = 25
            elseif tier == 2 then
                set effectVal = 45
            elseif tier == 3 then
                set effectVal = 70
            else
                set effectVal = 100
            endif
            set details = "Storm Shock: 30% chance for " + I2S(effectVal) + "% Main Stat magic damage in 320 AoE (2s ICD)"
'''
STORM_NEW = '''            if tier == 1 then
                set effectVal = 50
            elseif tier == 2 then
                set effectVal = 80
            elseif tier == 3 then
                set effectVal = 120
            else
                set effectVal = 170
            endif
            set details = "Storm Shock: 45% chance for " + I2S(effectVal) + "% Main Stat magic damage in 320 AoE (1.2s ICD)"
'''


def patch_script(s):
    s = _rep(s, STORM_OLD, STORM_NEW)
    s = _rep(s, 'LoadReal(PAX_Item_HT, h, 120) >= 2.0 and GetRandomReal(0.0, 100.0) < 30.0 then',
             'LoadReal(PAX_Item_HT, h, 120) >= 1.2 and GetRandomReal(0.0, 100.0) < 45.0 then  // v4.1.5')
    s = _rep(s, 'set burnDmg = GetWidgetLife(victim) * I2R(pct) * 0.001\n',
             'set burnDmg = GetWidgetLife(victim) * I2R(pct) * 0.001 + PAX_Leg_MainStat(attacker) * I2R(pct) * 0.02  // v4.1.5\n')
    for pct in ('1.0', '1.5', '2.2', '3.0'):
        s = _rep(s, '"Soul Burn: %s%% current HP/sec' % pct, '"Soul Burn (+2%% x pct main stat): %s%% current HP/sec' % pct)
    # the Mythic Forge rebuilds the texts
    s = _rep(s, '"Storm Shock: 30% chance for " + I2S(effVal)', '"Storm Shock: 45% chance for " + I2S(effVal)')
    s = _rep(s, '"Soul Burn: " + I2S(effVal / 10)', '"Soul Burn (+2% x pct main stat): " + I2S(effVal / 10)')
    s = _rep(s, 'I2R(BlzGetUnitMaxMana(src)) * I2R(val) * 0.001', 'I2R(BlzGetUnitMaxMana(src)) * I2R(val) * 0.002  // v4.1.5')
    for old, new in (('5.0% max mana on hit', '10.0% max mana on hit'), ('3.5% max mana on hit', '7.0% max mana on hit'),
                     ('2.5% max mana on hit', '5.0% max mana on hit'), ('1.5% max mana on hit', '3.0% max mana on hit')):  # top down
        s = _rep(s, old, new)
    return s
