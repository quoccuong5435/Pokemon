"""Pokemon Arena v4.1.2-ver2m Features:
1. Celebi Boss Death Drop Fix: drops ISCE (Celebi Soul), Rare Candy, Stat Boosters upon death.
2. Haunt Legend Mid Teleport:
   - IL02 (Map Center Teleport) item in shop n030.
   - CircleOfPower at (+/-5120, -/+740) steps on to warp to Center Altar (-128.0, 16.0).
3. Soulbound Equipment (120s) & High-Stakes Legend Drop on Death:
   - Holding item for >= 120s permanently binds it to player.
   - Other players picking up soulbound item have it dropped immediately.
   - Heroes carrying unbound Legend items drop them on death at dying location.
4. Command Card Attribute & Type Status Icon at (Row 1, Col 1):
   - Ability PAXT (Buttonpos = 1, 1).
   - Tooltip details: STR/INT/AGI formulas, STAB, 18-type chart.
   - In-game chat commands -stat and -type.
5. Custom VFX Integration:
   - Imports 56 Tranquil models and 90 Wight assets into MPQ archive.
   - Wires Stun Small to PAX_Leg_Stun, Shield Buff to barriers, etc.
"""
import os
import re

TRANQUIL_DIR = r"C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\Varioius Spells Effects"
WIGHT_DIR = r"C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\Wight  Spell Models"


def load_custom_vfx_files() -> dict:
    """Loads all 56 Tranquil models and 90 Wight assets into a dict of {mpq_path: bytes}."""
    assets = {}
    if os.path.exists(TRANQUIL_DIR):
        for f in os.listdir(TRANQUIL_DIR):
            if f.endswith('.mdx'):
                fp = os.path.join(TRANQUIL_DIR, f)
                with open(fp, 'rb') as s:
                    assets[f"Spells\\Tranquil\\{f}"] = s.read()

    if os.path.exists(WIGHT_DIR):
        for root, dirs, files in os.walk(WIGHT_DIR):
            for f in files:
                if f.endswith(('.mdx', '.blp')):
                    fp = os.path.join(root, f)
                    rel = os.path.relpath(fp, WIGHT_DIR)
                    with open(fp, 'rb') as s:
                        assets[f"Spells\\Wight\\{rel}"] = s.read()

    print(f"[ver2m_features] Loaded {len(assets)} custom VFX assets from Tranquil and Wight packs.")
    return assets


VER2M_JASS_HEADER = '''
// ============================================================================
// Pokemon Arena v4.1.2-ver2m: New Features & Overhauls
// ============================================================================

function PAX_IsSoulboundProtectedItem takes integer id returns boolean
    // Legend Souls (I01C..I01M, I01Q, I01V, I01W, ISCE, ISL0..ISL9)
    if (id >= 'I01C' and id <= 'I01M') or id == 'I01Q' or id == 'I01V' or id == 'I01W' or id == 'ISCE' or (id >= 'ISL0' and id <= 'ISL9') then
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
endfunction

function PAX_CelebiDeathCondition takes nothing returns boolean
    return GetUnitTypeId(GetTriggerUnit()) == 'n035'
endfunction

function PAX_CelebiDeathAction takes nothing returns nothing
    local unit dead = GetTriggerUnit()
    local real x = GetUnitX(dead)
    local real y = GetUnitY(dead)
    call CreateItem('ISCE', x, y)
    call CreateItem('I00B', x, y)
    call CreateItem('I001', x, y)
    call CreateItem('I000', x, y)
    call CreateItem('I002', x, y)
    call PAX_Announce("|cffffd166[SOUL DROP]|r |cffffd166Celebi|r |cffe8ecf2dropped its Soul!|r", 10.0)
    set dead = null
endfunction

function PAX_CelebiDeathInit takes nothing returns nothing
    local trigger trg = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(trg, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(trg, Condition(function PAX_CelebiDeathCondition))
    call TriggerAddAction(trg, function PAX_CelebiDeathAction)
endfunction

function PAX_PrintStatHelp takes player p returns nothing
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00=== POKEMON STAT & DAMAGE FORMULAS ===|r")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffff8000Physical Moves:|r Base Dmg x (|cffff8000STR|r / 50.0)")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff00ccffSpecial Moves:|r Base Dmg x (|cff00ccffINT|r / 50.0)")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff33ff33Agility:|r Increases Attack Speed & +1 Armor per 5 AGI")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffffd166STAB Bonus:|r +25% ~ +50% Damage when using same-type moves")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff00ffccScaling:|r 50 stat = 1.0x, 150 = 3.0x, 300 = 6.0x, 750 (max) = 15.0x")
endfunction

function PAX_PrintTypeHelp takes player p returns nothing
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "|cffffcc00=== 18-TYPE EFFECTIVENESS (x2.0 Super Effective) ===|r")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffff4040Fire|r > Grass, Ice, Bug, Steel | |cff4080ffWater|r > Fire, Ground, Rock")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffffff00Electric|r > Water, Flying (x0 vs Ground) | |cff40ff40Grass|r > Water, Ground, Rock")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff80ffffIce|r > Grass, Ground, Flying, Dragon | |cffff8000Fighting|r > Normal, Ice, Rock, Dark, Steel")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffa040a0Poison|r > Grass, Fairy | |cffb07030Ground|r > Fire, Electric, Poison, Rock, Steel")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff90a0ffFlying|r > Grass, Fighting, Bug | |cffff60a0Psychic|r > Fighting, Poison (x0 vs Dark)")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffa0b020Bug|r > Grass, Psychic, Dark | |cffb09040Rock|r > Fire, Ice, Flying, Bug")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff705090Ghost|r > Psychic, Ghost (x0 vs Normal) | |cff7030f0Dragon|r > Dragon (x0 vs Fairy)")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cff504040Dark|r > Psychic, Ghost | |cff9090a0Steel|r > Ice, Rock, Fairy")
    call DisplayTimedTextToPlayer(p, 0, 0, 12.0, "• |cffffa0c0Fairy|r > Fighting, Dragon, Dark")
endfunction

function PAX_StatChatCmd takes nothing returns nothing
    call PAX_PrintStatHelp(GetTriggerPlayer())
endfunction

function PAX_TypeChatCmd takes nothing returns nothing
    call PAX_PrintTypeHelp(GetTriggerPlayer())
endfunction

function PAX_InitChatHelp takes nothing returns nothing
    local trigger trgA = CreateTrigger()
    local trigger trgB = CreateTrigger()
    local integer i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(trgA, Player(i), "-stat", true)
        call TriggerRegisterPlayerChatEvent(trgB, Player(i), "-type", true)
        set i = i + 1
    endloop
    call TriggerAddAction(trgA, function PAX_StatChatCmd)
    call TriggerAddAction(trgB, function PAX_TypeChatCmd)
endfunction

function PAX_HauntPortalTick takes nothing returns nothing
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
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", u, "origin"))
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
endfunction
'''


def patch_script(s: str) -> str:
    """Applies ver2m JASS changes."""
    # 1. Insert header functions after PAX_Leg_Init
    anchor = "function PAX_Leg_Init takes nothing returns nothing"
    if anchor not in s:
        raise ValueError("[ver2m_features] PAX_Leg_Init anchor not found in script!")
    s = s.replace(anchor, VER2M_JASS_HEADER + "\n" + anchor, 1)

    # 2. Wire CelebiDeathInit and InitChatHelp into map init
    old_init = "call PAX_DecorateMap()"
    new_init = "call PAX_DecorateMap()\n    call PAX_CelebiDeathInit()\n    call PAX_InitChatHelp()"
    if old_init in s:
        s = s.replace(old_init, new_init, 1)

    # 3. Wire IL02 (Map Center Teleport) into LegTele_OnSell
    old_sell = '''    elseif it == 'IL01' then
        call SetUnitPosition(b, Fx_LLX, Fx_LLY)  // v3.4.11: the Pokemon League lobby'''
    new_sell = '''    elseif it == 'IL01' then
        call SetUnitPosition(b, Fx_LLX, Fx_LLY)  // v3.4.11: the Pokemon League lobby
    elseif it == 'IL02' then
        call SetUnitPosition(b, -128.0, 16.0)
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", b, "origin"))'''
    if old_sell in s:
        s = s.replace(old_sell, new_sell, 1)

    # 4. Wire HauntPortalTick and SoulboundTick into PAX_Leg_FastTick
    old_ftick = "call PAX_Boss_Tick()"
    new_ftick = "call PAX_Boss_Tick()\n    call PAX_HauntPortalTick()\n    call PAX_SoulboundTick()"
    if old_ftick in s:
        s = s.replace(old_ftick, new_ftick, 1)

    # 5. Wire Item_OnPickup: declare locals at top and check soulbound ownership
    old_item_locals = '''function Item_OnPickup takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local item it = GetManipulatedItem()
    local integer k = LoadInteger(Mega_HT, GetItemTypeId(it), 90)
    local integer n = 0
    local integer s = 0
    local integer lim = Item_MaxStat
    local item x = null'''
    new_item_locals = '''function Item_OnPickup takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local item it = GetManipulatedItem()
    local integer k = LoadInteger(Mega_HT, GetItemTypeId(it), 90)
    local integer n = 0
    local integer s = 0
    local integer lim = Item_MaxStat
    local item x = null
    local integer itH = 0
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
    endif'''
    if old_item_locals in s:
        s = s.replace(old_item_locals, new_item_locals, 1)

    # 6. Wire PAX_Leg_OnHeroDeath: Unbound Legend Items Drop on Death
    old_death_locals = '''    local player allyP = null
    local group g = null
    local unit u = null'''
    new_death_locals = '''    local player allyP = null
    local group g = null
    local unit u = null
    local integer slotIdx = 0
    local item dropSlotIt = null
    local integer dropH = 0
    local integer dropId = 0'''
    if old_death_locals in s:
        s = s.replace(old_death_locals, new_death_locals, 1)

    old_hero_death_start = '''    set victimP = GetOwningPlayer(dead)
    set pid = GetPlayerId(victimP)'''
    new_hero_death_start = '''    set victimP = GetOwningPlayer(dead)
    set pid = GetPlayerId(victimP)
    set slotIdx = 0
    loop
        exitwhen slotIdx >= 6
        set dropSlotIt = UnitItemInSlot(dead, slotIdx)
        if dropSlotIt != null then
            set dropH = GetHandleId(dropSlotIt)
            set dropId = GetItemTypeId(dropSlotIt)
            if PAX_IsSoulboundProtectedItem(dropId) and LoadInteger(PAX_Leg_HT, dropH, 100) == 0 then
                call UnitRemoveItem(dead, dropSlotIt)
                call SetItemPosition(dropSlotIt, GetUnitX(dead), GetUnitY(dead))
                call PAX_Announce("|cffff5c5c[LEGEND DROP]|r |cffffcc00" + GetUnitName(dead) + "|r |cffe8ecf2dropped unbound|r |cffffd166" + GetItemName(dropSlotIt) + "|r!", 8.0)
            endif
        endif
        set slotIdx = slotIdx + 1
    endloop
    set dropSlotIt = null'''
    if old_hero_death_start in s:
        s = s.replace(old_hero_death_start, new_hero_death_start, 1)

    # 7. Wire PAXT (Command Card Attribute & Type Icon) in Ab_Sync
    old_sync = "call PAX_Leg_Sync(u)"
    new_sync = "call PAX_Leg_Sync(u)\n    call UnitAddAbility(u, 'PAXT')"
    if old_sync in s:
        s = s.replace(old_sync, new_sync, 1)

    # 8. Wire Clean Stun VFX from Tranquil pack into PAX_Leg_Stun
    old_stun = "call BlzPauseUnitEx(u, true)"
    new_stun = 'call BlzPauseUnitEx(u, true)\n        call DestroyEffect(AddSpecialEffectTarget("Spells\\\\Tranquil\\\\Stun Small.mdx", u, "overhead"))'
    if old_stun in s:
        s = s.replace(old_stun, new_stun, 1)

    return s


def patch_objects(abil_slk, items_slk, func_txt: str, strings_txt: str, w3u) -> tuple:
    """Adds PAXT ability and IL02 item object definitions."""
    # 1. Define PAXT in AbilityData.slk (Cloned from AEev, passive info button at 1,1)
    col = abil_slk.name_to_x
    if not abil_slk.find('PAXT'):
        orig = abil_slk.find('AEev')
        if orig:
            r = dict(orig)
            r[1] = '"PAXT"'
            if 'hero' in col:
                r[col['hero']] = '0'
            if 'item' in col:
                r[col['item']] = '0'
            if 'levels' in col:
                r[col['levels']] = '1'
            if 'DataA1' in col:
                r[col['DataA1']] = '0'
            if 'abpx' in col:
                r[col['abpx']] = '1'
            if 'abpy' in col:
                r[col['abpy']] = '1'
            if 'art' in col:
                r[col['art']] = '"ReplaceableTextures\\CommandButtons\\BTNArcaneOrb.blp"'
            abil_slk.rows.append(r)

    # 2. Define PAXT in CampaignAbilityStrings.txt
    paxt_strings = """
[PAXT]
Name=Pokemon Attributes & Types
Art=ReplaceableTextures\\CommandButtons\\BTNArcaneOrb.blp
Buttonpos=1,1
Hotkey=T
Tip=|cffffcc00Pokemon Type & Attributes [T]|r
Ubertip="|cffffcc00[DAMAGE SCALING FORMULAS]|r|n• |cffff8000Physical Moves:|r Base Dmg x (|cffff8000STR|r / 50.0)|n• |cff00ccffSpecial Moves:|r Base Dmg x (|cff00ccffINT|r / 50.0)|n• |cff33ff33Agility:|r +Attack Speed & +1 Armor per 5 AGI|n• |cffffd166STAB Bonus:|r +25% ~ +50% Dmg for same-type moves|n|n|cffffcc00[TYPE EFFECTIVENESS (x2.0 Super Effective)]|r|n• Fire > Grass, Ice, Bug, Steel|n• Water > Fire, Ground, Rock|n• Electric > Water, Flying (x0 vs Ground)|n• Grass > Water, Ground, Rock|n• Ice > Grass, Ground, Flying, Dragon|n• Fighting > Normal, Ice, Rock, Dark, Steel|n• Poison > Grass, Fairy|n• Ground > Fire, Electric, Poison, Rock, Steel|n• Flying > Grass, Fighting, Bug|n• Psychic > Fighting, Poison (x0 vs Dark)|n• Bug > Grass, Psychic, Dark|n• Rock > Fire, Ice, Flying, Bug|n• Ghost > Psychic, Ghost (x0 vs Normal)|n• Dragon > Dragon (x0 vs Fairy)|n• Dark > Psychic, Ghost|n• Steel > Ice, Rock, Fairy|n• Fairy > Fighting, Dragon, Dark|n|n|cff00ffffType -stat or -type in chat for live statistics.|r"
"""
    if '[PAXT]' not in strings_txt:
        strings_txt += paxt_strings

    # 3. Define IL02 in ItemData.slk (Map Center Teleport item)
    icol = items_slk.name_to_x
    if not items_slk.find('IL02'):
        orig_i = items_slk.find('IL00')
        if orig_i:
            ir = dict(orig_i)
            ir[1] = '"IL02"'
            if 'goldcost' in icol:
                ir[icol['goldcost']] = '0'
            if 'stockMax' in icol:
                ir[icol['stockMax']] = '999'
            if 'stockRegen' in icol:
                ir[icol['stockRegen']] = '0'
            if 'stockStart' in icol:
                ir[icol['stockStart']] = '999'
            items_slk.rows.append(ir)

    # 4. Define IL02 in ItemFunc.txt
    il02_func = """
[IL02]
Name=Map Center Teleport
Hotkey=M
Tip=Teleport to |cffffcc00Map Center [M]|r
Ubertip="Instantly teleports your Pokemon to the Center Altar of the map."
Description=Teleport to Map Center
Art=ReplaceableTextures\\CommandButtons\\BTNMassTeleport.blp
Buttonpos=1,1
"""
    if '[IL02]' not in func_txt:
        func_txt += il02_func

    # 5. Add IL02 to Haunt Legend (n030) usei
    u_haunt = w3u.find('n030')
    if u_haunt:
        cur_usei = u_haunt.get('usei') or ''
        if 'IL02' not in cur_usei:
            u_haunt.set('usei', 3, cur_usei + ',IL02')

    return func_txt, strings_txt
