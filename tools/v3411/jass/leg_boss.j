// v3.4.16: random legends as raid bosses (replaces Leg_OnDamage / Leg_OnDeath of the base script).
// Ab_HT on the legend: 125 Mega done (Leg_TryMega), 139 enraged (1), 140 + pid damage dealt by player pid,
// 160 + pid last hero of player pid that hit it.
function Leg_OnDamage takes nothing returns boolean
    local unit t = BlzGetEventDamageTarget()
    local unit src = GetEventDamageSource()
    local player p = null
    local integer pid = 0
    local integer h = 0
    local integer k = 0
    local real x = 0.0
    local real y = 0.0
    local unit mn = null
    if Leg_IsLegend(GetUnitTypeId(t)) then
        set p = GetOwningPlayer(src)
        set pid = GetPlayerId(p)
        set h = GetHandleId(t)
        if pid < 12 and Leg_PlayerLevel(p) < Leg_MinLevel then
            call BlzSetEventDamage(0.0)
            if Mega_Time - Leg_Warned[pid] > 3.0 then
                set Leg_Warned[pid] = Mega_Time
                call DisplayTimedTextToPlayer(p, 0, 0, 3.0, "|cffff0000Only level 100 Pokemon can hurt " + GetUnitName(t) + "!|r")
            endif
        elseif pid < 12 and GetEventDamage() > 0.0 then
            // contribution (damage before the multipliers of the damage trigger)
            call SaveReal(Ab_HT, h, 140 + pid, LoadReal(Ab_HT, h, 140 + pid) + GetEventDamage())
            if IsUnitType(src, UNIT_TYPE_HERO) then
                call SaveUnitHandle(Ab_HT, h, 160 + pid, src)
            endif
            // phase 2 below half HP: +50% attack, red, two strong wild Pokemon join
            if LoadInteger(Ab_HT, h, 139) == 0 and GetWidgetLife(t) - GetEventDamage() < 0.5 * I2R(BlzGetUnitMaxHP(t)) then
                call SaveInteger(Ab_HT, h, 139, 1)
                call BlzSetUnitBaseDamage(t, R2I(I2R(BlzGetUnitBaseDamage(t, 0)) * Leg_EnrageDmg), 0)
                call SetUnitVertexColor(t, 255, 120, 120, 255)
                call AddSpecialEffectTarget("Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", t, "overhead")
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\HowlOfTerror\\HowlCaster.mdl", t, "origin"))
                set x = GetUnitX(t)
                set y = GetUnitY(t)
                loop
                    exitwhen k >= Leg_EnrageAdds
                    set mn = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), Wild_PickType(10), x + 250.0 * Cos(2.0944 * I2R(k)), y + 250.0 * Sin(2.0944 * I2R(k)), 270.0)
                    call Wild_Apply(mn)
                    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", GetUnitX(mn), GetUnitY(mn)))
                    set k = k + 1
                endloop
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff3030" + GetUnitName(t) + " is enraged! Attack +50% and wild Pokemon come to help it.|r")
            endif
        endif
    endif
    set t = null
    set src = null
    set p = null
    set mn = null
    return false
endfunction

function Leg_OnDeath takes unit u returns nothing
    local integer i = 0
    local integer h = GetHandleId(u)
    local integer pid = 0
    local integer best = -1
    local real total = 0.0
    local real d = 0.0
    local integer gold = 0
    local unit hero = null
    local string line = ""
    loop
        exitwhen i >= Leg_N
        if Leg_Type[i] == GetUnitTypeId(u) then
            set Leg_Alive = Leg_Alive - 1
            // v3.3.4: Leg_Up stays 1, the legend never comes back
            set pid = 0
            loop
                exitwhen pid >= 12
                set d = LoadReal(Ab_HT, h, 140 + pid)
                set total = total + d
                if d > 0.0 and (best < 0 or d > LoadReal(Ab_HT, h, 140 + best)) then
                    set best = pid
                endif
                set pid = pid + 1
            endloop
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 15.0, "|cffff66cc" + Leg_Name[i] + " was defeated! Damage dealt:|r")
            if total > 0.0 then
                set pid = 0
                loop
                    exitwhen pid >= 12
                    set d = LoadReal(Ab_HT, h, 140 + pid)
                    if d > 0.0 then
                        set gold = R2I(I2R(Leg_RewardGold) * d / total)
                        call AdjustPlayerStateBJ(gold, Player(pid), PLAYER_STATE_RESOURCE_GOLD)
                        set line = GetPlayerName(Player(pid)) + ": " + I2S(R2I(100.0 * d / total)) + "% -> +" + I2S(gold) + " gold"
                        if pid == best then
                            set line = line + " and the Soul"
                        endif
                        call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 15.0, "|cffffcc00" + line + "|r")
                        set Fx_ArgK = pid  // v3.4.16: quest "help defeat a wild legend"
                        call ExecuteFunc("Fx_QuestLegendX")
                    endif
                    set pid = pid + 1
                endloop
            endif
            // the Soul goes to the top damage dealer (in its hero's bag, else on the ground)
            if GetRandomInt(1, 100) <= Leg_SoulChance then
                if best >= 0 then
                    set hero = LoadUnitHandle(Ab_HT, h, 160 + best)
                endif
                if hero != null and GetWidgetLife(hero) > 0.405 then
                    call UnitAddItemById(hero, Leg_Soul[i])
                else
                    call CreateItem(Leg_Soul[i], GetUnitX(u), GetUnitY(u))
                endif
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff66cc" + Leg_Name[i] + " dropped its Soul!|r")
            endif
            call CreateItem('I00B', GetUnitX(u), GetUnitY(u))
            call CreateItem('I001', GetUnitX(u), GetUnitY(u))
            call CreateItem('I000', GetUnitX(u), GetUnitY(u))
            set hero = null
            return
        endif
        set i = i + 1
    endloop
    set hero = null
endfunction
