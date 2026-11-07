"""One-off (v3.4.2): easier gyms 1-4 (a level 30 Pokemon could not clear gyms 1-2): per-gym HP / damage
multipliers, no 1.7x attack speed and a lower skill-cast chance for gyms 1-4. Gyms 5-8 and the League unchanged."""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


# gym index 0..7, then the League (8)
HP = [0.35, 0.45, 0.70, 0.85, 1.0, 1.0, 1.0, 1.0, 1.0]
DMG = [0.45, 0.55, 0.75, 0.85, 1.0, 1.0, 1.0, 1.0, 1.0]
AI = [0.25, 0.25, 0.45, 0.45, 0.6, 0.6, 0.6, 0.6, 0.6]
FAST = [False, False, False, False, True, True, True, True, True]

s = open('tools/v34/jass/globals.j', encoding='utf-8').read().rstrip('\n')
s += '\nreal array Gym_DiffHP                  // v3.4.2: per gym (8 = League) HP / damage+armor multipliers, skill-cast\nreal array Gym_DiffDmg                 // chance and whether its Pokemon attack 1.7x faster (extras.py)\nreal array Gym_DiffAI\nboolean array Gym_Fast\n'
open('tools/v34/jass/globals.j', 'w', encoding='utf-8').write(s)
print('edited globals.j')

lines = []
for g in range(9):
    lines += ['    set Gym_DiffHP[%d] = %s' % (g, repr(HP[g])), '    set Gym_DiffDmg[%d] = %s' % (g, repr(DMG[g])),
              '    set Gym_DiffAI[%d] = %s' % (g, repr(AI[g])), '    set Gym_Fast[%d] = %s' % (g, 'true' if FAST[g] else 'false')]
edit('tools/v34/extras.py', [(
    """    # ---------------- Elite Four and Champion""",
    """    # ---------------- v3.4.2: gym difficulty (gyms 1-4 easier; analysis/patch_gym_difficulty.py has the table)
    c.data += %r

    # ---------------- Elite Four and Champion""" % lines)])

edit('tools/v34/jass/gym.j', [
    ("""    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult))""",
     """    call BlzSetUnitMaxHP(u, R2I(I2R(150 + 160 * lv) * m * Gym_HPMult * Gym_DiffHP[g]))"""),
    ("""    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8), 0)""",
     """    call BlzSetUnitBaseDamage(u, R2I(I2R(6 * lv) * m * 0.8 * Gym_DiffDmg[g]), 0)"""),
    ("""    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m)
    call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Hero_ASBoost, 0)""",
     """    call BlzSetUnitArmor(u, I2R(lv) / 4.0 * m * Gym_DiffDmg[g])
    if Gym_Fast[g] then  // v3.4.2: gyms 1-4 do not get the 1.7x attack speed
        call BlzSetUnitAttackCooldown(u, BlzGetUnitAttackCooldown(u, 0) / Hero_ASBoost, 0)
    endif
    call SaveReal(Ab_HT, h, 88, Gym_DiffAI[g])  // skill-cast chance of Ai_Tick"""),
])
edit('tools/v34/jass/ai.j', [
    ("""        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_CastChance then""",
     """        if not IsUnitType(u, UNIT_TYPE_STUNNED) and GetRandomReal(0.0, 1.0) < Ai_Chance(h) then"""),
    ("""function Ai_Unit takes unit u returns nothing""",
     """// v3.4.2: chance per second to cast (gym Pokemon of gyms 1-4 cast less: Ab_HT key 88)
function Ai_Chance takes integer h returns real
    if HaveSavedReal(Ab_HT, h, 88) then
        return LoadReal(Ab_HT, h, 88)
    endif
    return Ai_CastChance
endfunction

function Ai_Unit takes unit u returns nothing"""),
])
