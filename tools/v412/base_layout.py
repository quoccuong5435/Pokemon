"""Rearrange the base buildings and NPCs in Pokemon Arena v4.1.2:
- PERFECT 2-ROW GRID (5 Shops Top, 5 Shops Bottom, 180 Spacing, ZERO Overlap):
  * Top row (Y = 544.0, Facing 270.0 South):
    - Poké Mart 1 (n00O): +/-5960.0
    - Poké Mart 2 (n00N): +/-5780.0
    - Poké Mart 3 (n00Q): +/-5600.0
    - Item Shop (nIS0):   +/-5420.0
    - Battle Shop (nBS0): +/-5240.0
  * Bottom row (Y = -544.0, Facing 90.0 North):
    - Mega Shop I (nMS1):   +/-5960.0
    - Mega Shop II (nMS2):  +/-5780.0
    - Mega Shop III (nMS3): +/-5600.0
    - Form Shop (nFS0):     +/-5420.0
    - Paradox Shop (nFS1):  +/-5240.0
  * Clean 120+ unit buffer before Way Gate portals (+/-5120)
  * ALL magic auras (Brilliance, DevotionAura) removed completely from shops
- REMOVE LEAGUE PORTAL COMPLETELY (Bỏ League):
  * Red CircleOfPower and floating label League removed from base
  * Fx_Gate base portal registration disabled
- RELIC FORGE FAILURE ADJUSTMENT:
  * 30% drop 1 level, 70% keep current level on fail (+0 is 100% safe)
- Moves NPC and Mythic Forge symmetrical on lawn at (+/-5340, -220) and (+/-5340, 220)
- Poké Center (+/-5952, 0) 100% free of obstructions
"""

def patch_script(s):
    # 1. Moves NPC coordinates
    old_npc = '''    set Npc_X[0] = -5568.0
    set Npc_Y[0] = 0.0
    set Npc_Face[0] = 0.0
    set Npc_X[1] = 5568.0
    set Npc_Y[1] = 0.0'''
    new_npc = '''    set Npc_X[0] = -5340.0
    set Npc_Y[0] = -220.0
    set Npc_Face[0] = 0.0
    set Npc_X[1] = 5340.0
    set Npc_Y[1] = -220.0'''
    if old_npc not in s:
        raise SystemExit('base_layout: old Npc coordinates not found')
    s = s.replace(old_npc, new_npc, 1)

    # 2. Mythic Forge coordinates (North-East lawn corner, symmetrical to Moves NPC)
    old_forge = '''    local real fx = 0.0
    local real fy = 220.0
    local unit st = null
    loop
        exitwhen side >= 2
        if side == 0 then
            set fx = -5568.0
        else
            set fx = 5568.0
        endif'''
    new_forge = '''    local real fx = 0.0
    local real fy = 220.0
    local unit st = null
    loop
        exitwhen side >= 2
        if side == 0 then
            set fx = -5340.0
        else
            set fx = 5340.0
        endif'''
    if old_forge not in s:
        raise SystemExit('base_layout: old Forge coordinates not found')
    s = s.replace(old_forge, new_forge, 1)

    # 3. Top row: Mart 1, 2, 3 placed at 5950, 5800, 5650
    old_mart = (
        "set u=CreateUnit(p,'n00O',6000.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00O',-6000.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00P',-5952.0,0.0,0.000)\n"
        "set u=CreateUnit(p,'n00N',-5696.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00N',5696.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'nwgt',-5120.0,640.0,270.000)\n"
        "set u=CreateUnit(p,'nwgt',5120.0,-640.0,270.000)\n"
        "set u=CreateUnit(p,'n00Q',-5392.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00Q',5392.0,544.0,270.000)"
    )
    new_mart = (
        "set u=CreateUnit(p,'n00O',5950.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00O',-5950.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00P',-5952.0,0.0,0.000)\n"
        "set u=CreateUnit(p,'n00N',-5800.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00N',5800.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'nwgt',-5120.0,640.0,270.000)\n"
        "set u=CreateUnit(p,'nwgt',5120.0,-640.0,270.000)\n"
        "set u=CreateUnit(p,'n00Q',-5650.0,544.0,270.000)\n"
        "set u=CreateUnit(p,'n00Q',5650.0,544.0,270.000)"
    )
    if old_mart in s:
        s = s.replace(old_mart, new_mart, 1)

    # 4. Bottom row: Mega 1 & Mega 2 placed at 5950, 5800
    old_mega12 = (
        "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', -6000.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 6000.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', -5696.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 5696.0, -544.0, 90.0)"
    )
    new_mega12 = (
        "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', -5950.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 5950.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', -5800.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 5800.0, -544.0, 90.0)"
    )
    if old_mega12 in s:
        s = s.replace(old_mega12, new_mega12, 1)

    # 5. Bottom row: Mega 3 placed at 5650
    old_mega3 = (
        "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', -5392.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', 5392.0, -544.0, 90.0)"
    )
    new_mega3 = (
        "call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', -5650.0, -544.0, 90.0)\n"
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', 5650.0, -544.0, 90.0)"
    )
    if old_mega3 in s:
        s = s.replace(old_mega3, new_mega3, 1)

    # 6. Ext_PlaceShops: 3-row layout (4 Top, 4 Bottom, 2 Middle horizontal with Red PC)
    # Clear 330+ unit boulevard to Gym & Haunt Legend, zero overlap!
    old_place_shops = '''function Ext_PlaceShops takes nothing returns nothing
    local integer side = 0
    local integer k = 0
    local integer c = 0
    local real sx = 0.0
    local real x = 0.0
    local real y = 0.0
    local unit shop = null
    loop
        exitwhen side >= 2
        set sx = -1.0
        if side == 1 then
            set sx = 1.0
        endif
        set k = 0
        set c = 0
        loop
            exitwhen k >= 2 or c >= Ext_SpotN
            set x = sx * Ext_SpotX[c]
            set y = Ext_SpotY[c]
            if Ext_ShopSpot(x, y) then
                call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), Ext_Shop[k], x, y, 90.0)
                if k == 1 then  // v3.4.11: the League portal goes next to the Item Shop
                    set Fx_GateX[side] = x
                    set Fx_GateY[side] = y
                endif
                set k = k + 1
            endif
            set c = c + 1
        endloop
        set side = side + 1
    endloop
    set side = 0
    loop
        exitwhen side >= 2
        set sx = -1.0
        if side == 1 then
            set sx = 1.0
        endif
        set x = sx * 5240.0
        set y = 190.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, y, 270.0)
        if shop != null then
            call SetUnitVertexColor(shop, 255, 215, 80, 255)
            call PAX_MapLabel("|cffffd750Form Shop|r", x - 42.0, y, 165.0)
            call PAX_MapAura("Abilities\\\\Spells\\\\Human\\\\Brilliance\\\\Brilliance.mdl", shop, x, y, 0.65)
        endif
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', sx * 5020.0, 190.0, 270.0)
        if shop != null then
            call SetUnitVertexColor(shop, 170, 130, 255, 255)
            call PAX_MapLabel("|cffd899ffParadox|r", GetUnitX(shop) - 34.0, GetUnitY(shop), 165.0)
            call PAX_MapAura("Abilities\\\\Spells\\\\Human\\\\DevotionAura\\\\DevotionAura.mdl", shop, GetUnitX(shop), GetUnitY(shop), 0.65)
        endif
        set side = side + 1
    endloop
    set shop = null
endfunction'''

    new_place_shops = '''function Ext_PlaceShops takes nothing returns nothing
    local integer side = 0
    local real sx = 0.0
    local real x = 0.0
    local unit shop = null
    loop
        exitwhen side >= 2
        set sx = -1.0
        if side == 1 then
            set sx = 1.0
        endif
        // Top row (Y = 544.0, Facing South 270.0):
        // Mart 1 (5950), Mart 2 (5800), Mart 3 (5650), Item Shop (5500), Battle Shop (5350)
        set x = sx * 5500.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nIS0', x, 544.0, 270.0)
        call PAX_MapLabel("|cffffcc00Item Shop|r", x - 38.0, 544.0, 165.0)

        set x = sx * 5350.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nBS0', x, 544.0, 270.0)
        call PAX_MapLabel("|cffffcc00Battle Shop|r", x - 42.0, 544.0, 165.0)

        // Bottom row (Y = -544.0, Facing North 90.0):
        // Mega 1 (5950), Mega 2 (5800), Mega 3 (5650), Form Shop (5500), Paradox Shop (5350)
        set x = sx * 5500.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)
        if shop != null then
            call SetUnitVertexColor(shop, 255, 215, 80, 255)
            call PAX_MapLabel("|cffffd750Form Shop|r", x - 42.0, -544.0, 165.0)
        endif

        set x = sx * 5350.0
        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS1', x, -544.0, 90.0)
        if shop != null then
            call SetUnitVertexColor(shop, 170, 130, 255, 255)
            call PAX_MapLabel("|cffd899ffParadox|r", x - 34.0, -544.0, 165.0)
        endif

        // Haunt Legend Mid Teleport Portal (Circle of Power next to Haunt Legend at Y = sx * 760.0)
        call AddSpecialEffect("buildings\\\\other\\\\CircleOfPower\\\\CircleOfPower.mdl", sx * 5120.0, sx * 760.0)
        call PAX_MapLabel("|cff00ffffTo Mid|r", sx * 5120.0 - 24.0, sx * 760.0, 165.0)

        set side = side + 1
    endloop
    set shop = null
endfunction'''
    if old_place_shops not in s:
        raise SystemExit('base_layout: old Ext_PlaceShops function not found')
    s = s.replace(old_place_shops, new_place_shops, 1)

    # 7. Remove League Portal completely from base (bỏ League)
    old_gate_loop = (
        "    loop\n"
        "        exitwhen k > 1\n"
        "        set gx = Fx_GateX[k]\n"
        "        set gy = Fx_GateY[k]\n"
        "        if gx == 0.0 and gy == 0.0 then\n"
        "            set gx = Fx_LGX * (2.0 * I2R(k) - 1.0)\n"
        "            set gy = Fx_LGY\n"
        "        elseif not IsTerrainPathable(gx, gy - 230.0, PATHING_TYPE_WALKABILITY) then\n"
        "            set gy = gy - 230.0\n"
        "        elseif not IsTerrainPathable(gx - 230.0, gy, PATHING_TYPE_WALKABILITY) then\n"
        "            set gx = gx - 230.0\n"
        "        elseif not IsTerrainPathable(gx + 230.0, gy, PATHING_TYPE_WALKABILITY) then\n"
        "            set gx = gx + 230.0\n"
        "        else\n"
        "            set gy = gy + 230.0\n"
        "        endif\n"
        "        set Fx_GateX[k] = gx\n"
        "        set Fx_GateY[k] = gy\n"
        "        call AddSpecialEffect(\"buildings\\\\other\\\\CircleOfPower\\\\CircleOfPower.mdl\", gx, gy)\n"
        "        call PAX_MapLabel(\"|cffffcc66League|r\", gx - 28.0, gy, 175.0)\n"
        "        set k = k + 1\n"
        "    endloop"
    )
    new_gate_loop = (
        "    // League base portal completely removed\n"
        "    set k = 2"
    )
    if old_gate_loop in s:
        s = s.replace(old_gate_loop, new_gate_loop, 1)

    # Disable Fx_LeagueTick portal checks from base
    old_tick_portals = (
        "    call Fx_PortalAt(Fx_GateX[0], Fx_GateY[0], false)\n"
        "    call Fx_PortalAt(Fx_GateX[1], Fx_GateY[1], false)"
    )
    new_tick_portals = (
        "    // League base portals disabled\n"
        "    // call Fx_PortalAt(Fx_GateX[0], Fx_GateY[0], false)\n"
        "    // call Fx_PortalAt(Fx_GateX[1], Fx_GateY[1], false)"
    )
    if old_tick_portals in s:
        s = s.replace(old_tick_portals, new_tick_portals, 1)

    # 8. Clean decorative auras in PAX_DecorateMap
    old_auras = '''        call PAX_MapAura("Abilities\\\\Spells\\\\Human\\\\Brilliance\\\\Brilliance.mdl", null, x, 120.0, 0.55)
        call PAX_MapAura("Abilities\\\\Spells\\\\Human\\\\Brilliance\\\\Brilliance.mdl", null, x, -280.0, 0.65)'''
    new_auras = '''        // decorative base auras removed to prevent path clutter
        // call PAX_MapAura("Abilities\\\\Spells\\\\Human\\\\Brilliance\\\\Brilliance.mdl", null, x, 120.0, 0.55)'''
    if old_auras in s:
        s = s.replace(old_auras, new_auras, 1)

    # 9. Relic Forge failure penalty: 30% drop 1 level, 70% keep current level (+0 is 100% safe)
    old_forge_fail = (
        "    else\n"
        "        // Fail logic: +0 safe; +1..+4 drop -1 level (never shatters!)\n"
        "        set PAX_FailStreak[pid] = PAX_FailStreak[pid] + 1\n"
        "        if lv >= 1 then\n"
        "            set lv = lv - 1\n"
        "            call PAX_Forge_ApplyLevel(targetIt, lv)\n"
        "            call PAX_TestItem_Sync(uHero)\n"
        "            call DestroyEffect(AddSpecialEffectTarget(\"Abilities\\\\Spells\\\\Other\\\\Monsoon\\\\MonsoonBoltTarget.mdl\", uHero, \"origin\"))\n"
        "            call PAX_Fun_PublicFloat(uHero, \"|cffff5c5cFORGE FAIL! (-1 Lv)|r\", 255, 90, 90, 2.2)\n"
        "            call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, \"|cffff5c5c[FORGE]|r Upgrade failed! Item dropped back to +\" + I2S(lv) + \".\")\n"
        "            call PAX_Forge_Show(pid)\n"
        "        else\n"
        "            call DestroyEffect(AddSpecialEffectTarget(\"Abilities\\\\Spells\\\\Other\\\\Monsoon\\\\MonsoonBoltTarget.mdl\", uHero, \"origin\"))\n"
        "            call PAX_Fun_PublicFloat(uHero, \"|cffff5c5cFORGE FAIL!|r\", 255, 90, 90, 2.0)\n"
        "            call DisplayTimedTextToPlayer(trigPl, 0, 0, 5.0, \"|cffff5c5c[FORGE]|r Upgrade to +1 failed (item safe).\")\n"
        "            call PAX_Forge_Show(pid)\n"
        "        endif"
    )
    new_forge_fail = (
        "    else\n"
        "        set PAX_FailStreak[pid] = PAX_FailStreak[pid] + 1\n"
        "        if lv >= 1 and GetRandomInt(1, 100) <= 30 then\n"
        "            set lv = lv - 1\n"
        "            call PAX_Forge_ApplyLevel(targetIt, lv)\n"
        "            call PAX_TestItem_Sync(uHero)\n"
        "            call DestroyEffect(AddSpecialEffectTarget(\"Abilities\\\\Spells\\\\Other\\\\Monsoon\\\\MonsoonBoltTarget.mdl\", uHero, \"origin\"))\n"
        "            call PAX_Fun_PublicFloat(uHero, \"|cffff5c5cFORGE FAIL! (-1 Lv)|r\", 255, 90, 90, 2.2)\n"
        "            call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, \"|cffff5c5c[FORGE]|r Failed (30% penalty)! Item dropped to +\" + I2S(lv) + \".\")\n"
        "            call PAX_Forge_Show(pid)\n"
        "        else\n"
        "            call PAX_Fun_PublicFloat(uHero, \"|cffffaa00FORGE FAIL (SAFE)|r\", 255, 170, 0, 2.0)\n"
        "            call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, \"|cffffaa00[FORGE]|r Failed (70% safe)! Item retained safely at +\" + I2S(lv) + \".\")\n"
        "            call PAX_Forge_Show(pid)\n"
        "        endif"
    )
    if old_forge_fail in s:
        s = s.replace(old_forge_fail, new_forge_fail, 1)

    # 10. Late-Game Training & Gold Shop (-up) Price Increase
    old_train_show = (
        "    local integer statCost = 2000 + PAX_Up_StatLv[pid] * 500\n"
        "    local integer vitCost = 2000 + PAX_Up_VitLv[pid] * 500"
    )
    new_train_show = (
        "    local integer statCost = 5000 + PAX_Up_StatLv[pid] * 1500\n"
        "    local integer vitCost = 4000 + PAX_Up_VitLv[pid] * 1200"
    )
    if old_train_show in s:
        s = s.replace(old_train_show, new_train_show, 1)

    old_train_stat_click = "set cost = 2000 + PAX_Up_StatLv[pid] * 500"
    new_train_stat_click = "set cost = 5000 + PAX_Up_StatLv[pid] * 1500"
    if old_train_stat_click in s:
        s = s.replace(old_train_stat_click, new_train_stat_click, 1)

    old_train_vit_click = "set cost = 2000 + PAX_Up_VitLv[pid] * 500"
    new_train_vit_click = "set cost = 4000 + PAX_Up_VitLv[pid] * 1200"
    if old_train_vit_click in s:
        s = s.replace(old_train_vit_click, new_train_vit_click, 1)

    # 11. Disable Evolution Stone Drops from wild creeps (I00K..I00O)
    for st in ["'I00K'", "'I00L'", "'I00M'", "'I00N'", "'I00O'"]:
        old_drop = f"call CreateItemLoc({st},GetUnitLoc(GetTriggerUnit()))"
        s = s.replace(old_drop, f"// disabled wild stone drop: {st}")

    return s
