function Wild_ReinforceCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer capRemain = 6 - Wild_CampAlive[c]
    local integer spawnedCnt = 0
    local unit u = null
    // Anti-crash strict caps: max 6 creeps per camp AND max 260 wild creeps across entire map
    if capRemain <= 0 or Wild_CountTotalAlive() >= 260 then
        return
    endif
    if pow > 10 then
        set pow = 10
    endif
    call WD_MarkAlive()
    // Light reinforcement: at most 1 regular + 1 Elite (+2 max), never exceeding 6/camp; each its own species
    if capRemain >= 2 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), WD_Pick(pow), Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        set spawnedCnt = spawnedCnt + 1
    endif
    if capRemain >= 1 then
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), WD_Pick(pow), Wild_CampX[c] + GetRandomReal(-120.0, 120.0), Wild_CampY[c] + GetRandomReal(-120.0, 120.0), GetRandomReal(0.0, 360.0))
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
endfunction

==SPLIT==
function Wild_SpawnCamp takes integer c returns nothing
    local integer pow = Wild_CampPow[c] + Wild_Tier
    local integer t = 0
    local integer i = 0
    local unit u = null
    local integer elite = -1
    if pow > 10 then
        set pow = 10
    endif
    call WD_MarkAlive()
    set t = WD_Pick(pow)
    set Wild_CampDue[c] = 0.0
    if Wild_CampSize[c] > 6 then
        set Wild_CampAlive[c] = 6
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
        exitwhen i >= Wild_CampAlive[c]
        if i > 0 then
            set t = WD_Pick(pow)
        endif
        set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), t, Wild_CampX[c] + GetRandomReal(-150.0, 150.0), Wild_CampY[c] + GetRandomReal(-150.0, 150.0), GetRandomReal(0.0, 360.0))
        call SaveInteger(Mega_HT, GetHandleId(u), 25, c + 1)
        call SaveInteger(Mega_HT, GetHandleId(u), 31, pow)
        call Wild_Apply(u)
        if i == elite then
            call Wild_MakeElite(u)
        endif
        set i = i + 1
    endloop
    set u = null
endfunction

==SPLIT==
function Wild_Upgrade takes nothing returns nothing
    local integer c = 0
    local unit u = null
    local unit nu = null
    local integer h = 0
    local integer pow = 0
    call WD_MarkAlive()
    call GroupEnumUnitsOfPlayer(Wild_Tmp, Player(PLAYER_NEUTRAL_AGGRESSIVE), null)
    loop
        set u = FirstOfGroup(Wild_Tmp)
        exitwhen u == null
        call GroupRemoveUnit(Wild_Tmp, u)
        set h = GetHandleId(u)
        set c = LoadInteger(Mega_HT, h, 25) - 1
        if c >= 0 and Wild_IsWildType(GetUnitTypeId(u)) and GetWidgetLife(u) > 0.405 and GetUnitLifePercent(u) >= 99.9 then
            set pow = Wild_CampPow[c] + Wild_Tier
            if pow > 10 then
                set pow = 10
            endif
            if LoadInteger(Mega_HT, h, 31) < pow then
                // wild_mix: each creep turns into its own next form (or a new unused species), not one per camp
                set nu = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), WD_NextForm(GetUnitTypeId(u), pow), GetUnitX(u), GetUnitY(u), GetUnitFacing(u))
                call SaveInteger(Mega_HT, GetHandleId(nu), 25, c + 1)
                call SaveInteger(Mega_HT, GetHandleId(nu), 31, pow)
                call Wild_Apply(nu)
                if LoadInteger(Mega_HT, h, 29) == 1 then
                    call Wild_MakeElite(nu)
                endif
                call FlushChildHashtable(Mega_HT, h)
                call RemoveUnit(u)
            endif
        endif
    endloop
    set u = null
    set nu = null
endfunction
