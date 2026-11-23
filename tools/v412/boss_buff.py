"""Boss Buff Overhaul for Pokemon Arena v4.1.2:
Formula requested by user:
- x10 HP
- x2 ATK (Base Damage x2 and Dice Sides x2)
- x2 Armor
- Infinite Mana (Max Mana 10,000, 100% mana every 1s)
- 50% Cooldown Reduction (-50% attack cooldown & skill frequency)
- 25% Magic Resistance (-25% skill damage taken)
Applies to ALL 15 fixed room bosses (PAX_IsFixedBoss) and roaming legends (Leg_Spawn).
"""

OLD_BOSS_REGISTER = '''function PAX_Boss_Register takes unit lg, real x, real y returns nothing
    local integer h = 0
    local integer oldMax = 0
    local integer newMax = 0
    local real life = 0.0
    if lg != null then
        set h = GetHandleId(lg)
        if LoadInteger(PAX_Boss_HT, h, 2) == 0 then
            call SaveReal(PAX_Boss_HT, h, 0, x)
            call SaveReal(PAX_Boss_HT, h, 1, y)
            call SaveInteger(PAX_Boss_HT, h, 2, 1)
            call SaveReal(PAX_Boss_HT, h, 3, x)
            call SaveReal(PAX_Boss_HT, h, 4, y)
            call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
            call SaveInteger(PAX_Boss_HT, h, 6, 0)
            call SaveReal(PAX_Boss_HT, h, 7, 0.0)
            call SaveReal(Ab_HT, h, 60, Mega_Time)
            set oldMax = BlzGetUnitMaxHP(lg)
            if oldMax > 0 and oldMax < 150000 then
                set newMax = 150000 + oldMax
                set life = GetWidgetLife(lg)
                if life < I2R(oldMax) then
                    set life = I2R(newMax) * (life / I2R(oldMax))
                else
                    set life = I2R(newMax)
                endif
                call BlzSetUnitMaxHP(lg, newMax)
                call SetWidgetLife(lg, life)
            endif
            call GroupAddUnit(PAX_Leg_G, lg)
        endif
    endif
endfunction'''

NEW_BOSS_REGISTER = '''function PAX_Boss_Register takes unit lg, real x, real y returns nothing
    local integer h = 0
    local integer oldMax = 0
    local integer newMax = 0
    local integer baseDmg = 0
    local integer dice = 0
    local real arm = 0.0
    local real atkCd = 0.0
    if lg != null then
        set h = GetHandleId(lg)
        if LoadInteger(PAX_Boss_HT, h, 2) == 0 then
            call SaveReal(PAX_Boss_HT, h, 0, x)
            call SaveReal(PAX_Boss_HT, h, 1, y)
            call SaveInteger(PAX_Boss_HT, h, 2, 1)
            call SaveReal(PAX_Boss_HT, h, 3, x)
            call SaveReal(PAX_Boss_HT, h, 4, y)
            call SaveReal(PAX_Boss_HT, h, 5, Mega_Time)
            call SaveInteger(PAX_Boss_HT, h, 6, 0)
            call SaveReal(PAX_Boss_HT, h, 7, 0.0)
            call SaveReal(Ab_HT, h, 60, Mega_Time)

            // Uniform Boss Buff: x10 HP, x2 ATK, x2 Armor, Infinite Mana, -50% CD, Flag 65
            if LoadInteger(PAX_Boss_HT, h, 65) == 0 then
                call SaveInteger(PAX_Boss_HT, h, 65, 1)
                
                // x10 HP
                set oldMax = BlzGetUnitMaxHP(lg)
                if oldMax > 0 then
                    set newMax = oldMax * 10
                    call BlzSetUnitMaxHP(lg, newMax)
                    call SetWidgetLife(lg, I2R(newMax))
                endif

                // x2 ATK
                set baseDmg = BlzGetUnitBaseDamage(lg, 0)
                call BlzSetUnitBaseDamage(lg, baseDmg * 2, 0)
                set dice = BlzGetUnitDiceSides(lg, 0)
                if dice > 0 then
                    call BlzSetUnitDiceSides(lg, dice * 2, 0)
                endif

                // x2 Armor
                set arm = BlzGetUnitArmor(lg)
                call BlzSetUnitArmor(lg, arm * 2.0)

                // Infinite Mana (10,000 max mana)
                call BlzSetUnitMaxMana(lg, 10000)
                call SetUnitState(lg, UNIT_STATE_MANA, 10000.0)

                // -50% CD
                set atkCd = BlzGetUnitAttackCooldown(lg, 0)
                if atkCd > 0.40 then
                    call BlzSetUnitAttackCooldown(lg, atkCd * 0.50, 0)
                endif
            endif

            call GroupAddUnit(PAX_Leg_G, lg)
        endif
    endif
endfunction'''


def patch_script(s: str) -> str:
    if OLD_BOSS_REGISTER not in s:
        raise ValueError('boss_buff: OLD_BOSS_REGISTER anchor not found')
    s = s.replace(OLD_BOSS_REGISTER, NEW_BOSS_REGISTER, 1)

    # In PAX_Boss_Tick: replenish infinite mana every 1s for buffed bosses
    old_tick_entry = '''            set curX = GetUnitX(u)
            set curY = GetUnitY(u)'''
    new_tick_entry = '''            set curX = GetUnitX(u)
            set curY = GetUnitY(u)
            if LoadInteger(PAX_Boss_HT, h, 65) == 1 then
                call SetUnitState(u, UNIT_STATE_MANA, 10000.0)
            endif'''
    if old_tick_entry in s:
        s = s.replace(old_tick_entry, new_tick_entry, 1)

    # In PAX_Leg_ModifyIncoming: apply 25% magic resistance to bosses
    old_magic_check = '''    if skill and LoadInteger(PAX_Leg_HT, h, 182) == 1 and Mega_Time <= LoadReal(PAX_Leg_HT, h, 183) then
        set dmg = dmg * 0.80
    endif'''
    new_magic_check = '''    if skill and LoadInteger(PAX_Leg_HT, h, 182) == 1 and Mega_Time <= LoadReal(PAX_Leg_HT, h, 183) then
        set dmg = dmg * 0.80
    endif
    // Boss 25% Magic Resistance (-25% skill damage taken)
    if skill and LoadInteger(PAX_Boss_HT, h, 65) == 1 then
        set dmg = dmg * 0.75
    endif'''
    if old_magic_check in s:
        s = s.replace(old_magic_check, new_magic_check, 1)

    # Broadcast message for roaming legends
    s = s.replace('" (Lv 100) appeared! Only level 100 Pokemon can hurt it.|r")',
                  '" (Lv 100 Boss: HP x10, ATK x2, Armor x2, Infinite Mana, -50% CD) appeared!|r"')

    return s
