"""Pokemon Arena v4.1.3k Gameplay & Bug Fixes (patched on top of v4.1.3j):
1. Soulbound & Drop-on-Death Overhaul:
   - Common ('ofir') & Rare ('ocor') loot: immediately Soulbound on pickup, NEVER drop on death.
   - Mystery Loot Box (-up), Gamble (-gamble), and Mythic Forge (-forge) loot: immediately Soulbound
     to the opening player on creation (cannot be stolen, NEVER drops on death even if Epic/Legendary).
   - Epic ('oli2') & Legendary ('tgrh') wild/boss drops (+ Legend Souls & Paradox Boosters):
     drop on death ONLY if held < 60 seconds; once held >= 60s, permanently Soulbound!
   - Fixes the TWO root bugs that broke Soulbound timers in v4.1.3j:
     (a) PAX_SoulboundTick was never called anywhere (wired now into PAX_Leg_Tick1s every 1.0s).
     (b) PAX_SoulboundTick & PAX_HauntPortalTick used LoadUnitHandle(PAX_Leg_HT, p, 1) which was
         always null; now scans all living non-illusion heroes via GroupEnumUnitsOfPlayer.
   - Uses clean dedicated child keys 210..213 on PAX_Leg_HT (zero collision with unit buff keys 100..104).
2. First 10 Minutes No Wild Camp Reinforcement Spam:
   - Wild_ReinforceCamp (+2 creeps +1 Elite every 30s) is disabled while Wild_Time < 600.0 (first 10m).
3. -up Mystery Loot Box Drop Rates:
   - Common 75% | Rare 10% | Epic 3% | Legendary 0.5% | Empty Box (miss) 11.5%.
4. Vitamin Shop Stock Start Delay Fix (ItemData.slk):
   - Fixes stockStart='999' (999s start delay!) on I000..I006 -> stockStart='0', stockMax='100', stockRegen='1'.
   - Also sets stockStart='0' on IL02 and IMHA.
"""


def _once(s: str, old: str, new: str, label: str) -> str:
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError(f"[v413k_fixes] Anchor {label!r} matched {cnt} times (expected 1)")
    return s.replace(old, new, 1)


OLD_SOULBOUND_PROTECTED = """function PAX_IsSoulboundProtectedItem takes integer id returns boolean
    // Legend Souls (I01C..I01M, I01Q, I01V, I01W, ISCE, ISL0..ISL9)
    if (id >= 'I01C' and id <= 'I01M') or id == 'I01Q' or id == 'I01V' or id == 'I01W' or id == 'ISCE' or ((id >= 'ISL0' and id <= 'ISL9') or (id >= 'IL20' and id <= 'IL2O')) then
        return true
    endif
    // 4 Tiered Loot items (ofir, ocor, oli2, tgrh)
    if id == 'ofir' or id == 'ocor' or id == 'oli2' or id == 'tgrh' then
        return true
    endif
    // Mega Stones (IM00..IM17)
    if id >= 'IM00' and id <= 'IM17' then
        return true
    endif
    // Paradox Booster Energy (IM18..IM1H)
    if id >= 'IM18' and id <= 'IM1H' then
        return true
    endif
    return false
endfunction"""

NEW_SOULBOUND_PROTECTED = """function PAX_IsInstantSoulboundItem takes integer itemTypeId returns boolean
    // Common Loot ('ofir') and Rare Loot ('ocor'): immediately Soulbound on pickup, never drop on death
    return itemTypeId == 'ofir' or itemTypeId == 'ocor'
endfunction

function PAX_Soulbound_BindNow takes item targetItem, integer ownerPlayerId returns nothing
    local integer itemHandleId = 0
    if targetItem == null or ownerPlayerId < 0 or ownerPlayerId >= 12 then
        return
    endif
    set itemHandleId = GetHandleId(targetItem)
    call SaveInteger(PAX_Leg_HT, itemHandleId, 210, 1)
    call SaveInteger(PAX_Leg_HT, itemHandleId, 211, ownerPlayerId)
    call SaveInteger(PAX_Leg_HT, itemHandleId, 212, 60)
    call SaveInteger(PAX_Leg_HT, itemHandleId, 213, 1)
endfunction

function PAX_Soulbound_ClearKeys takes item targetItem returns nothing
    local integer itemHandleId = 0
    if targetItem == null then
        return
    endif
    set itemHandleId = GetHandleId(targetItem)
    call RemoveSavedInteger(PAX_Leg_HT, itemHandleId, 210)
    call RemoveSavedInteger(PAX_Leg_HT, itemHandleId, 211)
    call RemoveSavedInteger(PAX_Leg_HT, itemHandleId, 212)
    call RemoveSavedInteger(PAX_Leg_HT, itemHandleId, 213)
endfunction

function PAX_IsSoulboundProtectedItem takes integer id returns boolean
    // Legend Souls (I01C..I01M, I01Q, I01V, I01W, ISCE, ISL0..ISL9, IL20..IL2O)
    if (id >= 'I01C' and id <= 'I01M') or id == 'I01Q' or id == 'I01V' or id == 'I01W' or id == 'ISCE' or ((id >= 'ISL0' and id <= 'ISL9') or (id >= 'IL20' and id <= 'IL2O')) then
        return true
    endif
    // Epic ('oli2') & Legendary ('tgrh') Loot ONLY (Common 'ofir' & Rare 'ocor' NEVER drop on death)
    if id == 'oli2' or id == 'tgrh' then
        return true
    endif
    // Legacy Mega Stones (IM00..IM17)
    if id >= 'IM00' and id <= 'IM17' then
        return true
    endif
    // Paradox Booster Energy (IM18..IM1H)
    if id >= 'IM18' and id <= 'IM1H' then
        return true
    endif
    return false
endfunction"""


OLD_PORTAL_AND_TICK = r"""function PAX_HauntPortalTick takes nothing returns nothing
    local integer p = 0
    local unit u = null
    local real x = 0.0
    local real y = 0.0
    local real distA = 0.0
    local real distB = 0.0
    loop
        exitwhen p >= 12
        set u = LoadUnitHandle(PAX_Leg_HT, p, 1)
        if u != null and GetWidgetLife(u) > 0.405 then
            set x = GetUnitX(u)
            set y = GetUnitY(u)
            // Team 1 Haunt Portal (-5120.0, 740.0)
            set distA = (x - (-5120.0)) * (x - (-5120.0)) + (y - 740.0) * (y - 740.0)
            // Team 2 Haunt Portal (5120.0, -740.0)
            set distB = (x - 5120.0) * (x - 5120.0) + (y - (-740.0)) * (y - (-740.0))
            if distA <= 14400.0 or distB <= 14400.0 then // 120 range
                call SetUnitPosition(u, -128.0, 16.0)
                call PanCameraToTimedForPlayer(GetOwningPlayer(u), -128.0, 16.0, 0.25)
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", u, "origin"))
            endif
        endif
        set p = p + 1
    endloop
    set u = null
endfunction

function PAX_SoulboundTick takes nothing returns nothing
    local integer p = 0
    local unit u = null
    local integer s = 0
    local item it = null
    local integer itH = 0
    local real timeHeld = 0.0
    loop
        exitwhen p >= 12
        set u = LoadUnitHandle(PAX_Leg_HT, p, 1)
        if u != null and GetWidgetLife(u) > 0.405 then
            set s = 0
            loop
                exitwhen s >= 6
                set it = UnitItemInSlot(u, s)
                if it != null then
                    set itH = GetHandleId(it)
                    set timeHeld = LoadReal(PAX_Leg_HT, itH, 101)
                    if timeHeld > 0.0 and LoadInteger(PAX_Leg_HT, itH, 100) == 0 then
                        if Mega_Time - timeHeld >= 120.0 then
                            call SaveInteger(PAX_Leg_HT, itH, 100, 1)
                            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cff00ffcc[SOULBOUND]|r |cffffcc00" + GetItemName(it) + "|r |cffe8ecf2is now permanently locked to you!|r")
                        endif
                    endif
                endif
                set s = s + 1
            endloop
        endif
        set p = p + 1
    endloop
    set u = null
    set it = null
endfunction"""

NEW_PORTAL_AND_TICK = r"""function PAX_HauntPortalTick takes nothing returns nothing
    local integer portalPid = 0
    local group portalScanG = CreateGroup()
    local unit portalHero = null
    local real portalX = 0.0
    local real portalY = 0.0
    local real portalDistA = 0.0
    local real portalDistB = 0.0
    loop
        exitwhen portalPid >= 12
        call GroupEnumUnitsOfPlayer(portalScanG, Player(portalPid), null)
        loop
            set portalHero = FirstOfGroup(portalScanG)
            exitwhen portalHero == null
            call GroupRemoveUnit(portalScanG, portalHero)
            if IsUnitType(portalHero, UNIT_TYPE_HERO) and not IsUnitIllusion(portalHero) and GetWidgetLife(portalHero) > 0.405 then
                set portalX = GetUnitX(portalHero)
                set portalY = GetUnitY(portalHero)
                // Team 1 Haunt Portal (-5120.0, 740.0)
                set portalDistA = (portalX - (-5120.0)) * (portalX - (-5120.0)) + (portalY - 740.0) * (portalY - 740.0)
                // Team 2 Haunt Portal (5120.0, -740.0)
                set portalDistB = (portalX - 5120.0) * (portalX - 5120.0) + (portalY - (-740.0)) * (portalY - (-740.0))
                if portalDistA <= 14400.0 or portalDistB <= 14400.0 then
                    call SetUnitPosition(portalHero, -128.0, 16.0)
                    call PanCameraToTimedForPlayer(Player(portalPid), -128.0, 16.0, 0.25)
                    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", portalHero, "origin"))
                endif
            endif
        endloop
        set portalPid = portalPid + 1
    endloop
    call DestroyGroup(portalScanG)
    set portalScanG = null
    set portalHero = null
endfunction

function PAX_SoulboundTick takes nothing returns nothing
    local integer sbPid = 0
    local group sbScanG = CreateGroup()
    local unit sbHero = null
    local integer sbSlot = 0
    local item sbItem = null
    local integer sbHandle = 0
    local integer sbItemId = 0
    local integer sbHoldSec = 0
    loop
        exitwhen sbPid >= 12
        call GroupEnumUnitsOfPlayer(sbScanG, Player(sbPid), null)
        loop
            set sbHero = FirstOfGroup(sbScanG)
            exitwhen sbHero == null
            call GroupRemoveUnit(sbScanG, sbHero)
            if IsUnitType(sbHero, UNIT_TYPE_HERO) and not IsUnitIllusion(sbHero) and GetWidgetLife(sbHero) > 0.405 then
                set sbSlot = 0
                loop
                    exitwhen sbSlot >= 6
                    set sbItem = UnitItemInSlot(sbHero, sbSlot)
                    if sbItem != null then
                        set sbHandle = GetHandleId(sbItem)
                        set sbItemId = GetItemTypeId(sbItem)
                        if LoadInteger(PAX_Leg_HT, sbHandle, 210) == 0 then
                            if PAX_IsInstantSoulboundItem(sbItemId) then
                                call PAX_Soulbound_BindNow(sbItem, sbPid)
                            elseif PAX_IsSoulboundProtectedItem(sbItemId) then
                                if LoadInteger(PAX_Leg_HT, sbHandle, 213) == 0 or LoadInteger(PAX_Leg_HT, sbHandle, 211) != sbPid then
                                    call SaveInteger(PAX_Leg_HT, sbHandle, 211, sbPid)
                                    call SaveInteger(PAX_Leg_HT, sbHandle, 212, 1)
                                    call SaveInteger(PAX_Leg_HT, sbHandle, 213, 1)
                                else
                                    set sbHoldSec = LoadInteger(PAX_Leg_HT, sbHandle, 212) + 1
                                    call SaveInteger(PAX_Leg_HT, sbHandle, 212, sbHoldSec)
                                    if sbHoldSec >= 60 then
                                        call PAX_Soulbound_BindNow(sbItem, sbPid)
                                        call DisplayTimedTextToPlayer(Player(sbPid), 0, 0, 5.0, "|cff00ffcc[SOULBOUND]|r |cffffcc00" + GetItemName(sbItem) + "|r |cffe8ecf2is now permanently locked to you (safe on death)!|r")
                                    endif
                                endif
                            endif
                        endif
                    endif
                    set sbSlot = sbSlot + 1
                endloop
            endif
        endloop
        set sbPid = sbPid + 1
    endloop
    call DestroyGroup(sbScanG)
    set sbScanG = null
    set sbHero = null
    set sbItem = null
endfunction"""


OLD_DEATH_DROP = """            if PAX_IsSoulboundProtectedItem(dropId) and LoadInteger(PAX_Leg_HT, dropH, 100) == 0 then
                call UnitRemoveItem(dead, dropSlotIt)
                call SetItemPosition(dropSlotIt, GetUnitX(dead), GetUnitY(dead))
                call PAX_Announce("|cffff5c5c[LEGEND DROP]|r |cffffcc00" + GetUnitName(dead) + "|r |cffe8ecf2dropped unbound|r |cffffd166" + GetItemName(dropSlotIt) + "|r!", 8.0)
            endif"""

NEW_DEATH_DROP = """            if PAX_IsSoulboundProtectedItem(dropId) and LoadInteger(PAX_Leg_HT, dropH, 210) == 0 then
                call SaveInteger(PAX_Leg_HT, dropH, 212, 0)
                call SaveInteger(PAX_Leg_HT, dropH, 213, 0)
                call UnitRemoveItem(dead, dropSlotIt)
                call SetItemPosition(dropSlotIt, GetUnitX(dead), GetUnitY(dead))
                call PAX_Announce("|cffff5c5c[LEGEND DROP]|r |cffffcc00" + GetUnitName(dead) + "|r |cffe8ecf2dropped unbound|r |cffffd166" + GetItemName(dropSlotIt) + "|r!", 8.0)
            endif"""


OLD_TICK1S_ANCHOR = """    call PAX_Leg_BurnTick()
    call PAX_Leg_DummyTick()"""

NEW_TICK1S_ANCHOR = """    call PAX_Leg_BurnTick()
    call PAX_Leg_DummyTick()
    call PAX_HauntPortalTick()
    call PAX_SoulboundTick()"""


OLD_PICKUP_BLOCK = """    local integer itH = 0
    local integer ownerPid = 0
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set itH = GetHandleId(it)
        set ownerPid = GetPlayerId(GetOwningPlayer(u))
        if LoadInteger(PAX_Leg_HT, itH, 100) == 1 and LoadInteger(PAX_Leg_HT, itH, 102) != ownerPid then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040[SOULBOUND] This item belongs to Player " + I2S(LoadInteger(PAX_Leg_HT, itH, 102) + 1) + " and cannot be used!|r")
            set u = null
            set it = null
            return
        endif
        if LoadReal(PAX_Leg_HT, itH, 101) == 0.0 then
            call SaveReal(PAX_Leg_HT, itH, 101, Mega_Time)
            call SaveInteger(PAX_Leg_HT, itH, 102, ownerPid)
            call SaveInteger(PAX_Leg_HT, itH, 100, 0)
        endif
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif"""

NEW_PICKUP_BLOCK = """    local integer itH = 0
    local integer ownerPid = 0
    local integer pickupItemId = 0
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set itH = GetHandleId(it)
        set ownerPid = GetPlayerId(GetOwningPlayer(u))
        set pickupItemId = GetItemTypeId(it)
        if LoadInteger(PAX_Leg_HT, itH, 210) == 1 and LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040[SOULBOUND] This item belongs to Player " + I2S(LoadInteger(PAX_Leg_HT, itH, 211) + 1) + " and cannot be used!|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    if IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 and PAX_IsLootItemId(GetItemTypeId(it)) then
        if PAX_CountLootExcept(u, null) > 2 then
            call UnitRemoveItem(u, it)
            call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 5.0, "|cffff4040At most 2 dropped items can be equipped.|r")
            set u = null
            set it = null
            set x = null
            return
        endif
    endif
    if u != null and it != null and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        if LoadInteger(PAX_Leg_HT, itH, 210) == 0 then
            if PAX_IsInstantSoulboundItem(pickupItemId) then
                call PAX_Soulbound_BindNow(it, ownerPid)
            elseif PAX_IsSoulboundProtectedItem(pickupItemId) then
                if LoadInteger(PAX_Leg_HT, itH, 213) == 0 or LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid then
                    call SaveInteger(PAX_Leg_HT, itH, 211, ownerPid)
                    call SaveInteger(PAX_Leg_HT, itH, 212, 0)
                    call SaveInteger(PAX_Leg_HT, itH, 213, 1)
                    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 6.0, "|cffffd166[UNBOUND]|r Hold |cffffcc00" + GetItemName(it) + "|r for |cffffd16660s|r to Soulbind it (drops on death until bound)!")
                endif
            endif
        endif
    endif"""


OLD_UP_BTN_LABEL = '    set PAX_Up_Btn[baseIdx + 2] = DialogAddButton(PAX_Up_Dlg[pid], "Mystery Loot Box (Rare/Epic/Leg) - 3500g", 0)'
NEW_UP_BTN_LABEL = '    set PAX_Up_Btn[baseIdx + 2] = DialogAddButton(PAX_Up_Dlg[pid], "Mystery Loot Box (75% C / 10% R / 3% E / 0.5% L) - 3500g", 0)'

OLD_UP_LOCALS = """    local integer baseIdx = pid * 5
    local integer gold = GetPlayerState(trigPl, PLAYER_STATE_RESOURCE_GOLD)
    local integer cost = 0
    local integer roll = 0
    local integer tier = 2"""
NEW_UP_LOCALS = """    local integer baseIdx = pid * 5
    local integer gold = GetPlayerState(trigPl, PLAYER_STATE_RESOURCE_GOLD)
    local integer cost = 0
    local integer roll = 0
    local real boxRoll = 0.0
    local integer tier = 0"""

OLD_UP_BOX = r"""    elseif btn == PAX_Up_Btn[baseIdx + 2] then
        if gold < 3500 then
            call DisplayTimedTextToPlayer(trigPl, 0, 0, 5.0, "|cffff5c5c[TRAIN]|r Need 3500g for Mystery Loot Box.")
        else
            call AdjustPlayerStateBJ(-3500, trigPl, PLAYER_STATE_RESOURCE_GOLD)
            set roll = GetRandomInt(1, 100)
            if roll <= 12 then
                set tier = 4
            elseif roll <= 50 then
                set tier = 3
            else
                set tier = 2
            endif
            set dropIt = CreateItem(PAX_Loot_ItemId(tier), GetUnitX(uHero), GetUnitY(uHero))
            if dropIt != null then
                call PAX_Loot_RollItem(dropIt, tier, GetRandomInt(1, 2))
            endif
            set dropIt = null
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Resurrect\\ResurrectTarget.mdl", uHero, "origin"))
            call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[LOOT BOX]|r Opened a " + PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + "|r Loot at your feet!")
        endif"""

NEW_UP_BOX = r"""    elseif btn == PAX_Up_Btn[baseIdx + 2] then
        if gold < 3500 then
            call DisplayTimedTextToPlayer(trigPl, 0, 0, 5.0, "|cffff5c5c[TRAIN]|r Need 3500g for Mystery Loot Box.")
        else
            call AdjustPlayerStateBJ(-3500, trigPl, PLAYER_STATE_RESOURCE_GOLD)
            set boxRoll = GetRandomReal(0.0, 100.0)
            set tier = 0
            if boxRoll <= 0.5 then
                set tier = 4
            elseif boxRoll <= 3.5 then
                set tier = 3
            elseif boxRoll <= 13.5 then
                set tier = 2
            elseif boxRoll <= 88.5 then
                set tier = 1
            endif
            if tier > 0 then
                set dropIt = CreateItem(PAX_Loot_ItemId(tier), GetUnitX(uHero), GetUnitY(uHero))
                if dropIt != null then
                    call PAX_Loot_RollItem(dropIt, tier, GetRandomInt(1, 2))
                    call PAX_Soulbound_BindNow(dropIt, pid)
                endif
                set dropIt = null
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Resurrect\\ResurrectTarget.mdl", uHero, "origin"))
                call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[LOOT BOX]|r Opened a " + PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + "|r Loot (|cff00ffccSoulbound|r to you) at your feet!")
            else
                call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffff5c5c[LOOT BOX]|r The Mystery Loot Box was empty! Better luck next time!")
            endif
        endif"""


OLD_GAMBLE_LOOT = r"""        set dropIt = CreateItem(PAX_Loot_ItemId(tier), GetUnitX(uHero), GetUnitY(uHero))
        if dropIt != null then
            call PAX_Loot_RollItem(dropIt, tier, GetRandomInt(1, 2))
        endif
        set dropIt = null
        call PAX_Celebrate(uHero, "LOOT WIN!", "Abilities\\Spells\\Human\\HolyBolt\\HolyBoltSpecialArt.mdl")
        call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[GAMBLE]|r Lucky drop! A Rare/Epic Loot spawned at your feet!")"""

NEW_GAMBLE_LOOT = r"""        set dropIt = CreateItem(PAX_Loot_ItemId(tier), GetUnitX(uHero), GetUnitY(uHero))
        if dropIt != null then
            call PAX_Loot_RollItem(dropIt, tier, GetRandomInt(1, 2))
            call PAX_Soulbound_BindNow(dropIt, pid)
        endif
        set dropIt = null
        call PAX_Celebrate(uHero, "LOOT WIN!", "Abilities\\Spells\\Human\\HolyBolt\\HolyBoltSpecialArt.mdl")
        call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[GAMBLE]|r Lucky drop! A |cff00ffccSoulbound|r Rare/Epic Loot spawned at your feet!")"""


OLD_FORGE_FUSE = """        call FlushChildHashtable(PAX_Item_HT, GetHandleId(it1))
        call FlushChildHashtable(PAX_Item_HT, GetHandleId(it2))
        call RemoveItem(it1)
        call RemoveItem(it2)
        set newIt = CreateItem(PAX_Loot_ItemId(nextTier), GetUnitX(uHero), GetUnitY(uHero))
        if newIt != null then
            call PAX_Loot_RollItem(newIt, nextTier, GetRandomInt(1, 2))
            call SaveInteger(PAX_Item_HT, GetHandleId(newIt), 19, 1)
            call UnitAddItem(uHero, newIt)
        endif"""

NEW_FORGE_FUSE = """        call PAX_Soulbound_ClearKeys(it1)
        call PAX_Soulbound_ClearKeys(it2)
        call FlushChildHashtable(PAX_Item_HT, GetHandleId(it1))
        call FlushChildHashtable(PAX_Item_HT, GetHandleId(it2))
        call RemoveItem(it1)
        call RemoveItem(it2)
        set newIt = CreateItem(PAX_Loot_ItemId(nextTier), GetUnitX(uHero), GetUnitY(uHero))
        if newIt != null then
            call PAX_Loot_RollItem(newIt, nextTier, GetRandomInt(1, 2))
            call SaveInteger(PAX_Item_HT, GetHandleId(newIt), 19, 1)
            call PAX_Soulbound_BindNow(newIt, pid)
            call UnitAddItem(uHero, newIt)
        endif"""


OLD_WILD_REINFORCE_FN = r"""function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer base_t = LoadInteger(Mega_HT, c + 500, 3)
    local integer new_t = 0
    local integer attempts = 0
    local unit u = null
    if pow > 10 then
        set pow = 10
    endif
    set new_t = Wild_PickType(pow)
    loop
        exitwhen new_t != base_t or attempts >= 6
        set new_t = Wild_PickType(pow)
        set attempts = attempts + 1
    endloop
    if new_t == base_t and Wild_PoolN > 1 then
        set new_t = Wild_Pool[ModuloInteger(c + 3, Wild_PoolN)]
    endif
    // Spawn 2 regular creeps of the different elemental type
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)

    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)

    // Spawn 1 additional ELITE creep of the different elemental type!
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
    call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
    call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
    call Wild_Apply(u)
    call Wild_MakeElite(u)

    set Wild_CampAlive[c] = Wild_CampAlive[c] + 3
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", Wild_CampX[c], Wild_CampY[c]))
    call PAX_Fun_PublicFloat(u, "|cffff3333REINFORCED (+ELITE)!|r", 255, 60, 60, 2.5)
    set u = null
endfunction"""

NEW_WILD_REINFORCE_FN = r"""function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer base_t = LoadInteger(Mega_HT, c + 500, 3)
    local integer new_t = 0
    local integer attempts = 0
    local integer capRemain = 10 - Wild_CampAlive[c]
    local integer spawnedCnt = 0
    local unit u = null
    if capRemain <= 0 then
        return
    endif
    if pow > 10 then
        set pow = 10
    endif
    set new_t = Wild_PickType(pow)
    loop
        exitwhen new_t != base_t or attempts >= 6
        set new_t = Wild_PickType(pow)
        set attempts = attempts + 1
    endloop
    if new_t == base_t and Wild_PoolN > 1 then
        set new_t = Wild_Pool[ModuloInteger(c + 3, Wild_PoolN)]
    endif
    // Hard cap: NEVER exceed 10 alive creeps in any camp (prevents late-game lag/crash)
    if capRemain >= 3 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 2 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 1 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), new_t, Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        call Wild_MakeElite(u)
        set spawnedCnt = spawnedCnt + 1
    endif

    set Wild_CampAlive[c] = Wild_CampAlive[c] + spawnedCnt
    call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", Wild_CampX[c], Wild_CampY[c]))
    if u != null then
        call PAX_Fun_PublicFloat(u, "|cffff3333REINFORCED (+ELITE)!|r", 255, 60, 60, 2.5)
    endif
    set u = null
endfunction"""


OLD_WILD_SPAWN_LOOP = """    set Wild_CampAlive[c] = Wild_CampSize[c]
    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
    call SaveInteger(Mega_HT, c + 500, 2, 0)
    call SaveInteger(Mega_HT, c + 500, 3, t)
    call SaveInteger(Mega_HT, c + 500, 4, 1)
    if Wild_CampSize[c] > 0 then
        set elite = GetRandomInt(0, Wild_CampSize[c] - 1)
    endif
    loop
        exitwhen i >= Wild_CampSize[c]"""

NEW_WILD_SPAWN_LOOP = """    if Wild_CampSize[c] > 10 then
        set Wild_CampAlive[c] = 10
    else
        set Wild_CampAlive[c] = Wild_CampSize[c]
    endif
    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
    call SaveInteger(Mega_HT, c + 500, 2, 0)
    call SaveInteger(Mega_HT, c + 500, 3, t)
    call SaveInteger(Mega_HT, c + 500, 4, 1)
    if Wild_CampAlive[c] > 0 then
        set elite = GetRandomInt(0, Wild_CampAlive[c] - 1)
    endif
    loop
        exitwhen i >= Wild_CampAlive[c]"""


OLD_WILD_REINFORCE_TICK = """            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0 and LoadInteger(Mega_HT, c + 500, 2) < 2 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif"""

NEW_WILD_REINFORCE_TICK = """            if Wild_CampAlive[c] > 0 and Wild_CampDue[c] == 0.0 then
                if Wild_Time < 600.0 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                elseif Wild_CampAlive[c] < 10 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 30.0 and LoadInteger(Mega_HT, c + 500, 2) < 2 then
                    call SaveReal(Mega_HT, c + 500, 1, Wild_Time)
                    call SaveInteger(Mega_HT, c + 500, 2, LoadInteger(Mega_HT, c + 500, 2) + 1)
                    call Wild_ReinforceCamp(c)
                endif
            endif"""


OLD_BOSS_REGISTER = """            // Uniform Boss Buff: x10 HP, x2 ATK, x2 Armor, Infinite Mana, -50% CD, Flag 65
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
            endif"""

NEW_BOSS_REGISTER = """            // Uniform Rebalanced Legend Boss Stats (Fixed Room + Roaming Wild Legends):
            // HP: 1,000,000 .. 1,500,000 | ATK: 1,500 .. 2,500 | Armor: 450 .. 700 (scaled by natural stats)
            if LoadInteger(PAX_Boss_HT, h, 65) == 0 then
                call SaveInteger(PAX_Boss_HT, h, 65, 1)

                // HP mapped from base [19000..58000] -> [1,000,000..1,500,000]
                set oldMax = BlzGetUnitMaxHP(lg)
                set bossHpRatio = (I2R(oldMax) - 19000.0) / 39000.0
                if bossHpRatio < 0.0 then
                    set bossHpRatio = 0.0
                elseif bossHpRatio > 1.0 then
                    set bossHpRatio = 1.0
                endif
                set newMax = 1000000 + R2I(bossHpRatio * 500000.0)
                call BlzSetUnitMaxHP(lg, newMax)
                call SetWidgetLife(lg, I2R(newMax))

                // ATK mapped from base avg [750..1350] -> avg [1600..2350] (range ~1,472..2,538)
                set baseDmg = BlzGetUnitBaseDamage(lg, 0)
                set dice = BlzGetUnitDiceSides(lg, 0)
                set bossAtkRatio = (I2R(baseDmg) + I2R(dice) * 0.5 - 750.0) / 600.0
                if bossAtkRatio < 0.0 then
                    set bossAtkRatio = 0.0
                elseif bossAtkRatio > 1.0 then
                    set bossAtkRatio = 1.0
                endif
                set bossAvgAtk = 1600.0 + bossAtkRatio * 750.0
                set bossAtkLo = R2I(bossAvgAtk * 0.92)
                set bossAtkHi = R2I(bossAvgAtk * 1.08)
                if bossAtkHi < bossAtkLo then
                    set bossAtkHi = bossAtkLo
                endif
                call BlzSetUnitDiceNumber(lg, 1, 0)
                call BlzSetUnitDiceSides(lg, bossAtkHi - bossAtkLo + 1, 0)
                call BlzSetUnitBaseDamage(lg, bossAtkLo - 1, 0)

                // Armor mapped from base [75..225] -> [450..700]
                set arm = BlzGetUnitArmor(lg)
                set bossArmRatio = (arm - 75.0) / 150.0
                if bossArmRatio < 0.0 then
                    set bossArmRatio = 0.0
                elseif bossArmRatio > 1.0 then
                    set bossArmRatio = 1.0
                endif
                call BlzSetUnitArmor(lg, 450.0 + bossArmRatio * 250.0)

                // Infinite Mana (10,000 max mana)
                call BlzSetUnitMaxMana(lg, 10000)
                call SetUnitState(lg, UNIT_STATE_MANA, 10000.0)

                // -50% CD
                set atkCd = BlzGetUnitAttackCooldown(lg, 0)
                if atkCd > 0.40 then
                    call BlzSetUnitAttackCooldown(lg, atkCd * 0.50, 0)
                endif
            endif"""

OLD_BOSS_REG_LOCALS = """function PAX_Boss_Register takes unit lg, real x, real y returns nothing
    local integer h = 0
    local integer oldMax = 0
    local integer newMax = 0
    local integer baseDmg = 0
    local integer dice = 0
    local real arm = 0.0
    local real atkCd = 0.0"""

NEW_BOSS_REG_LOCALS = """function PAX_Boss_Register takes unit lg, real x, real y returns nothing
    local integer h = 0
    local integer oldMax = 0
    local integer newMax = 0
    local integer baseDmg = 0
    local integer dice = 0
    local integer bossAtkLo = 0
    local integer bossAtkHi = 0
    local real arm = 0.0
    local real atkCd = 0.0
    local real bossHpRatio = 0.0
    local real bossAtkRatio = 0.0
    local real bossAvgAtk = 0.0
    local real bossArmRatio = 0.0"""

OLD_LEG_SPAWN_BUFF = """    call BlzSetUnitMaxHP(lg, BlzGetUnitMaxHP(lg) * 20)  // ver2: boss x20 HP, x5 attack, x3 armor
    call SetWidgetLife(lg, I2R(BlzGetUnitMaxHP(lg)))
    call BlzSetUnitBaseDamage(lg, BlzGetUnitBaseDamage(lg, 0) * 5, 0)
    call BlzSetUnitDiceSides(lg, BlzGetUnitDiceSides(lg, 0) * 5, 0)
    call BlzSetUnitArmor(lg, BlzGetUnitArmor(lg) * 3.0)
    call PAX_Boss_Register(lg, x, y)
    set lg = null
    set Leg_Alive = Leg_Alive + 1
    set Leg_Up[i] = 1
    call PingMinimap(x, y, 5.0)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff66ccA wild " + Leg_Name[i] + " (Lv 100, HP x20, attack x5, armor x3) appeared! Only level 100 Pokemon can hurt it.|r")"""

NEW_LEG_SPAWN_BUFF = """    // Uniform Legend Boss scaling handled once inside PAX_Boss_Register (1M-1.5M HP, 1.5k-2.5k ATK, 450-700 Armor)
    call PAX_Boss_Register(lg, x, y)
    set lg = null
    set Leg_Alive = Leg_Alive + 1
    set Leg_Up[i] = 1
    call PingMinimap(x, y, 5.0)
    call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 10.0, "|cffff66ccA wild " + Leg_Name[i] + " (Lv 100 Legend Boss) appeared! Only level 100 Pokemon can hurt it.|r")"""


def patch_script(s: str) -> str:
    s = _once(s, OLD_BOSS_REG_LOCALS, NEW_BOSS_REG_LOCALS, "PAX_Boss_Register locals")
    s = _once(s, OLD_BOSS_REGISTER, NEW_BOSS_REGISTER, "PAX_Boss_Register uniform rebalance")
    s = _once(s, OLD_LEG_SPAWN_BUFF, NEW_LEG_SPAWN_BUFF, "Leg_Spawn remove double multiplier")
    s = _once(s, OLD_SOULBOUND_PROTECTED, NEW_SOULBOUND_PROTECTED, "PAX_IsSoulboundProtectedItem")
    s = _once(s, OLD_PORTAL_AND_TICK, NEW_PORTAL_AND_TICK, "PAX_HauntPortalTick+PAX_SoulboundTick")
    s = _once(s, OLD_DEATH_DROP, NEW_DEATH_DROP, "PAX_Leg_OnHeroDeath drop")
    s = _once(s, OLD_TICK1S_ANCHOR, NEW_TICK1S_ANCHOR, "PAX_Leg_Tick1s wiring")
    s = _once(s, OLD_PICKUP_BLOCK, NEW_PICKUP_BLOCK, "Item_OnPickup soulbound")
    s = _once(s, OLD_UP_BTN_LABEL, NEW_UP_BTN_LABEL, "PAX_Up_Show button 2 label")
    s = _once(s, OLD_UP_LOCALS, NEW_UP_LOCALS, "PAX_Up_OnClick locals")
    s = _once(s, OLD_UP_BOX, NEW_UP_BOX, "PAX_Up_OnClick Mystery Loot Box")
    s = _once(s, OLD_GAMBLE_LOOT, NEW_GAMBLE_LOOT, "PAX_Fun_Gamble loot soulbound")
    s = _once(s, OLD_FORGE_FUSE, NEW_FORGE_FUSE, "PAX_Forge_Fuse loot soulbound")
    s = _once(s, OLD_WILD_REINFORCE_FN, NEW_WILD_REINFORCE_FN, "Wild_ReinforceCamp max 10 cap")
    s = _once(s, OLD_WILD_SPAWN_LOOP, NEW_WILD_SPAWN_LOOP, "Wild_SpawnCamp max 10 cap")
    s = _once(s, OLD_WILD_REINFORCE_TICK, NEW_WILD_REINFORCE_TICK, "Wild_Tick 10m grace + max 10 cap")
    return s


def patch_w3u_bosses(w3u) -> None:
    """Normalize the 25 new wild bosses (nL20..nL2O) to the exact same base scale as original bosses
    (base HP ~19k..58k, base ATK ~650..1350, base Armor ~90..225) so PAX_Boss_Register maps ALL 54
    Legend Bosses cleanly into 1.0M-1.5M HP, 1.5k-2.5k ATK, and 450-700 Armor by authentic stats."""
    import legend_expansion_data

    for leg in legend_expansion_data.NEW_LEGENDS:
        u = w3u.find(leg["wild"])
        if not u:
            continue
        hp, atk, def_, spa, spd, spe = leg["stats"]
        off = max(atk, spa)
        base_hp = int(round(hp * 387.0))
        base_atk = int(round(off * 7.2))
        base_sides = max(20, int(round(off * 2.4)))
        base_arm = int(round(def_ * 1.5))
        u.set("uhpm", 0, base_hp)
        u.set("ua1b", 0, base_atk)
        u.set("ua1d", 0, 1)
        u.set("ua1s", 0, base_sides)
        u.set("udef", 0, base_arm)


def load_zekrom_fix_assets(mpq_mod) -> dict:
    """Load authentic Zekrom (#644) 3D MDX (block 6601) + textures (644a/b/c.blp) from 79.PokemonRPG.w3x."""
    import legend_expansion_data

    rpg = mpq_mod.MPQ(legend_expansion_data.RPG79_MAP)
    mdx_bytes = rpg.read_block(6601)
    assert mdx_bytes[:4] == b"MDLX", "Block 6601 in 79.PokemonRPG.w3x is not MDLX"
    out = {"PkFx\\Legends\\Zekrom.mdx": mdx_bytes}
    for tex in ("644a.blp", "644b.blp", "644c.blp"):
        out[tex] = rpg.read(tex)
    return out


def patch_items_slk(items_slk) -> None:
    col = items_slk.name_to_x
    sx_max = col["stockMax"]
    sx_reg = col["stockRegen"]
    sx_start = col["stockStart"]

    # Fix Vitamins I000..I006: stockStart was '999' (999s delay at game start!) -> '0' delay, 100 max, 1s regen
    for iid in ["I000", "I001", "I002", "I003", "I004", "I005", "I006"]:
        row = items_slk.find(iid)
        if not row:
            raise ValueError(f"[v413k_fixes] Item {iid} not found in ItemData.slk")
        row[sx_start] = "0"
        row[sx_max] = "100"
        row[sx_reg] = "1"

    # Also ensure IL02 (Map Center Teleport) & IMHA (Ability Patch) have 0s stockStart delay
    row_il02 = items_slk.find("IL02")
    if row_il02:
        row_il02[sx_start] = "0"
        row_il02[sx_max] = "99"
        row_il02[sx_reg] = "1"

    row_imha = items_slk.find("IMHA")
    if row_imha:
        row_imha[sx_start] = "0"
