globals
    integer Gym_Dummy = 0
endglobals
function PAX_Loot_OnDeath takes unit dead, unit killer, boolean isWild, boolean isElite, boolean isLegend returns nothing
    local real chance = 0.0
    local real roll = 0.0
    local integer tier = 1
    local integer kind = 1
    local item it = null
    local real x = 0.0
    local real y = 0.0
    if dead == null or killer == null then
        set it = null
        return
    endif
    if GetPlayerId(GetOwningPlayer(killer)) >= 12 then
        set it = null
        return
    endif
    if isLegend then
        set chance = 45.0
    elseif isElite then
        set chance = 15.0
    elseif isWild then
        set chance = 5.0
    else
        set it = null
        return
    endif
    if PAX_Loot_TestMode and (isLegend or isElite or isWild) then
        set chance = 100.0
    endif
    if GetRandomReal(0.0, 100.0) >= chance then
        set it = null
        return
    endif
    set roll = GetRandomReal(0.0, 100.0)
    if isLegend then
        if roll <= 35.0 then
            set tier = 2
        elseif roll <= 80.0 then
            set tier = 3
        else
            set tier = 4
        endif
    elseif isElite then
        if roll <= 45.0 then
            set tier = 1
        elseif roll <= 83.0 then
            set tier = 2
        elseif roll <= 97.0 then
            set tier = 3
        else
            set tier = 4
        endif
    else
        if roll <= 75.0 then
            set tier = 1
        elseif roll <= 95.0 then
            set tier = 2
        elseif roll <= 99.5 then
            set tier = 3
        else
            set tier = 4
        endif
    endif
    set kind = GetRandomInt(1, 2)
    set x = GetUnitX(dead)
    set y = GetUnitY(dead)
    set it = CreateItem(PAX_Loot_ItemId(tier), x, y)
    if it != null then
        call PAX_Loot_RollItem(it, tier, kind)
        if tier >= 3 then
            call PAX_FloatText(dead, PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + " loot dropped!|r", 255, 200, 80, GetOwningPlayer(killer), GetOwningPlayer(killer))
        endif
    endif
    set it = null
endfunction
