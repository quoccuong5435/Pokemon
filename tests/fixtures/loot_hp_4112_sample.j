globals
    integer Gym_Dummy = 0
endglobals
function PAX_TestItem_SyncEx takes unit u, item excludeItem returns nothing
    local integer i = 0
    local integer h = 0
    local integer oldSTR = 0
    local integer oldAGI = 0
    local integer oldINT = 0
    local integer oldArmor = 0
    local integer oldHP = 0
    local integer oldAS = 0
    local integer oldMS = 0
    local integer oldShock = 0
    local integer oldBurn = 0
    local integer oldManaProc = 0
    local integer oldThorns = 0
    local integer newSTR = 0
    local integer newAGI = 0
    local integer newINT = 0
    local integer newArmor = 0
    local integer newHP = 0
    local integer newAS = 0
    local integer newMS = 0
    local integer effectType = 0
    local integer effectVal = 0
    local integer effectVal2 = 0
    local integer k = 0
    local integer eff1 = 0
    local integer eff2 = 0
    local integer eff3 = 0
    local integer eff4 = 0
    local integer eff5 = 0
    local integer eff6 = 0
    local integer eff7 = 0
    local integer killMana = 0
    local real lifePct = 0.0
    local real newMaxHP = 0.0
    local item it = null
    if u == null or not IsUnitType(u, UNIT_TYPE_HERO) or GetPlayerId(GetOwningPlayer(u)) >= 12 then
        set it = null
        return
    endif
    set h = GetHandleId(u)
    set oldSTR = LoadInteger(PAX_Item_HT, h, 100)
    set oldAGI = LoadInteger(PAX_Item_HT, h, 101)
    set oldINT = LoadInteger(PAX_Item_HT, h, 102)
    set oldArmor = LoadInteger(PAX_Item_HT, h, 103)
    set oldHP = LoadInteger(PAX_Item_HT, h, 104)
    set oldAS = LoadInteger(PAX_Item_HT, h, 105)
    set oldMS = LoadInteger(PAX_Item_HT, h, 106)
    set oldShock = LoadInteger(PAX_Item_HT, h, 112)
    set oldBurn = LoadInteger(PAX_Item_HT, h, 113)
    set oldManaProc = LoadInteger(PAX_Item_HT, h, 115)
    set oldThorns = LoadInteger(PAX_Item_HT, h, 116)
    loop
        exitwhen i >= 6
        set it = UnitItemInSlot(u, i)
        if it != null and it != excludeItem and PAX_IsLootItemId(GetItemTypeId(it)) then
            set k = GetHandleId(it)
            call SaveInteger(PAX_Item_HT, k, 19, 1)
            if LoadInteger(PAX_Item_HT, k, 1) == 1 then
                set newSTR = newSTR + LoadInteger(PAX_Item_HT, k, 2)
                set newAGI = newAGI + LoadInteger(PAX_Item_HT, k, 3)
                set newINT = newINT + LoadInteger(PAX_Item_HT, k, 4)
                set newArmor = newArmor + LoadInteger(PAX_Item_HT, k, 5)
                set newHP = newHP + LoadInteger(PAX_Item_HT, k, 6)
                set newAS = newAS + LoadInteger(PAX_Item_HT, k, 7)
                set newMS = newMS + LoadInteger(PAX_Item_HT, k, 8)
            else
                set effectType = LoadInteger(PAX_Item_HT, k, 10)
                set effectVal = LoadInteger(PAX_Item_HT, k, 11)
                set effectVal2 = LoadInteger(PAX_Item_HT, k, 12)
                if effectType == 1 then
                    set eff1 = eff1 + effectVal
                elseif effectType == 2 then
                    set eff2 = eff2 + effectVal
                elseif effectType == 3 then
                    set eff3 = eff3 + effectVal
                elseif effectType == 4 then
                    set eff4 = eff4 + effectVal
                elseif effectType == 5 then
                    set eff5 = eff5 + effectVal
                elseif effectType == 6 then
                    set eff6 = eff6 + effectVal
                elseif effectType == 7 then
                    set eff7 = eff7 + effectVal
                endif
                if effectType == 5 then
                    set killMana = killMana + effectVal2
                endif
            endif
        endif
        set i = i + 1
    endloop
    if newHP > 15000 then
        set newHP = 15000
    endif
    if eff1 > 25 then
        set eff1 = 25
    endif
    if eff4 > 60 then
        set eff4 = 60
    endif
    if oldShock == 0 and eff2 > 0 then
        call SaveReal(PAX_Item_HT, h, 120, Mega_Time - 2.0)
    endif
    if oldBurn == 0 and eff3 > 0 then
        call SaveReal(PAX_Item_HT, h, 121, Mega_Time - 1.5)
    endif
    if oldManaProc == 0 and eff5 > 0 then
        call SaveReal(PAX_Item_HT, h, 122, Mega_Time - 1.5)
    endif
    if oldThorns == 0 and eff6 > 0 then
        call SaveReal(PAX_Item_HT, h, 123, Mega_Time - 0.5)
    endif
    call SetHeroStr(u, GetHeroStr(u, false) + newSTR - oldSTR, true)
    call SetHeroAgi(u, GetHeroAgi(u, false) + newAGI - oldAGI, true)
    call SetHeroInt(u, GetHeroInt(u, false) + newINT - oldINT, true)
    if newArmor != oldArmor then
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + I2R(newArmor - oldArmor))
    endif
    if newHP != oldHP then
        set lifePct = GetUnitLifePercent(u)
        set newMaxHP = I2R(BlzGetUnitMaxHP(u) + newHP - oldHP)
        if newMaxHP < 1.0 then
            set newMaxHP = 1.0
        endif
        call BlzSetUnitMaxHP(u, R2I(newMaxHP))
        call SetWidgetLife(u, newMaxHP * lifePct * 0.01)
    endif
    if newMS != oldMS then
        call SetUnitMoveSpeed(u, GetUnitMoveSpeed(u) + I2R(newMS - oldMS))
    endif
    call SaveInteger(PAX_Item_HT, h, 100, newSTR)
    call SaveInteger(PAX_Item_HT, h, 101, newAGI)
    call SaveInteger(PAX_Item_HT, h, 102, newINT)
    call SaveInteger(PAX_Item_HT, h, 103, newArmor)
    call SaveInteger(PAX_Item_HT, h, 104, newHP)
    call SaveInteger(PAX_Item_HT, h, 105, newAS)
    call SaveInteger(PAX_Item_HT, h, 106, newMS)
    call SaveInteger(PAX_Item_HT, h, 111, eff1)
    call SaveInteger(PAX_Item_HT, h, 112, eff2)
    call SaveInteger(PAX_Item_HT, h, 113, eff3)
    call SaveInteger(PAX_Item_HT, h, 114, eff4)
    call SaveInteger(PAX_Item_HT, h, 115, eff5)
    call SaveInteger(PAX_Item_HT, h, 116, eff6)
    call SaveInteger(PAX_Item_HT, h, 117, eff7)
    call SaveInteger(PAX_Item_HT, h, 118, killMana)
    set it = null
endfunction
function PAX_Me_OnChat takes nothing returns nothing
    local player trigPl = GetTriggerPlayer()
    local integer pid = GetPlayerId(trigPl)
    local unit uHero = PAX_MB_FindHero(pid)
    local integer h = 0
    local integer legIdx = 0
    local integer bounty = 0
    local integer streakBonus = 0
    local integer lsPct = 0
    local integer critPct = 0
    local integer thornsPct = 0
    local integer rStr = 0
    local integer rAgi = 0
    local integer rInt = 0
    local integer rArm = 0
    local integer rHp = 0
    local string runeStr = "None"
    if uHero == null then
        call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cff7dd3fc[STATS]|r |cffe8ecf2Pick a Pokemon first.|r")
        set trigPl = null
        return
    endif
    set h = GetHandleId(uHero)
    set legIdx = PAX_Leg_Index(GetUnitTypeId(uHero))
    if legIdx > 0 then
        if PAX_Leg_Awakened(uHero) then
            set bounty = 2500
        else
            set bounty = 1500
        endif
    endif
    if PAX_KillStreak[pid] >= 3 then
        set streakBonus = PAX_KillStreak[pid] * 300
        if streakBonus > 2100 then
            set streakBonus = 2100
        endif
        set bounty = bounty + streakBonus
    endif
    set rStr = LoadInteger(PAX_Item_HT, h, 100)
    set rAgi = LoadInteger(PAX_Item_HT, h, 101)
    set rInt = LoadInteger(PAX_Item_HT, h, 102)
    set rArm = LoadInteger(PAX_Item_HT, h, 103)
    set rHp = LoadInteger(PAX_Item_HT, h, 104)
    set lsPct = LoadInteger(PAX_Item_HT, h, 111)
    set critPct = LoadInteger(PAX_Item_HT, h, 114)
    set thornsPct = LoadInteger(PAX_Item_HT, h, 116)
    if Mega_Time < LoadReal(PAX_Leg_HT, h, 170) then
        set runeStr = "|cff38bdf8Haste (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 170) - Mega_Time)) + "s)|r"
    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 171) then
        set runeStr = "|cffff5c5cFury (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 171) - Mega_Time)) + "s)|r"
    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 172) then
        set runeStr = "|cff4ade80Regen (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 172) - Mega_Time)) + "s)|r"
    endif
    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "|cff7dd3fc====== " + GetUnitName(uHero) + " (Lv " + I2S(GetHeroLevel(uHero)) + ") ======|r")
    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2K/D:|r |cffff5c5c" + I2S(F9[pid + 1]) + "|r/|cff6699ff" + I2S(G9[pid + 1]) + "|r  |  |cffe8ecf2Streak:|r |cffffd166" + I2S(PAX_KillStreak[pid]) + "|r  |  |cffe8ecf2Bounty:|r |cffffd166" + I2S(bounty) + "g|r  |  |cffe8ecf2Gym:|r |cffffd166" + I2S(PAX_MB_BadgeCount(pid)) + "/8|r")
    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Loot Stats:|r +" + I2S(rStr) + " STR, +" + I2S(rAgi) + " AGI, +" + I2S(rInt) + " INT, +" + I2S(rArm) + " Armor, +" + I2S(rHp) + " HP")
    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Charms:|r Lifesteal " + I2S(lsPct) + "%  |  Crit " + I2S(critPct) + "%  |  Thorns " + I2S(thornsPct) + "%  |  |cffe8ecf2Rune:|r " + runeStr)
    set uHero = null
    set trigPl = null
endfunction
