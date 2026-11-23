// -abtest <Ability name>: the host gives the selected own hero any Ability to try it; -abtest off = its own again
function RW_TestCmd takes nothing returns boolean
    local player rwPlayer = GetTriggerPlayer()
    local string rwMsg = GetEventPlayerChatString()
    local string rwName = ""
    local integer rwIndex = 1
    local integer rwFound = 0
    local unit rwHero = null
    if SubString(rwMsg, 0, 7) != "-abtest" then
        set rwPlayer = null
        return false
    endif
    if GetPlayerId(rwPlayer) != Host_Id() then
        call DisplayTimedTextToPlayer(rwPlayer, 0, 0, 5.0, "|cffffcc00[-abtest]|r Only the host can use this test command.")
        set rwPlayer = null
        return false
    endif
    set rwName = StringCase(SubString(rwMsg, 8, StringLength(rwMsg)), false)
    call GroupEnumUnitsSelected(RW_Grp, rwPlayer, null)
    set rwHero = FirstOfGroup(RW_Grp)
    call GroupClear(RW_Grp)
    if rwHero == null or not IsUnitType(rwHero, UNIT_TYPE_HERO) or GetOwningPlayer(rwHero) != rwPlayer then
        call DisplayTimedTextToPlayer(rwPlayer, 0, 0, 5.0, "|cffffcc00[-abtest]|r Select your own hero first, then type -abtest <Ability name> (or -abtest off).")
        set rwPlayer = null
        set rwHero = null
        return false
    endif
    if rwName == "" or rwName == "off" then
        call SaveInteger(RW_HT, GetHandleId(rwHero), 90, 0)
        call Ab_Sync(rwHero)
        call DisplayTimedTextToPlayer(rwPlayer, 0, 0, 5.0, "|cffffcc00[-abtest]|r " + GetUnitName(rwHero) + " has its own Ability again.")
        set rwPlayer = null
        set rwHero = null
        return false
    endif
    loop
        exitwhen rwIndex > Ab_N
        if StringCase(Ab_Name[rwIndex], false) == rwName then
            set rwFound = rwIndex  // the last one wins: reworked Abilities have the higher numbers
        endif
        set rwIndex = rwIndex + 1
    endloop
    if rwFound == 0 then
        call DisplayTimedTextToPlayer(rwPlayer, 0, 0, 5.0, "|cffffcc00[-abtest]|r No Ability named \"" + rwName + "\". Use the English name, e.g. -abtest Rough Skin")
    else
        call SaveInteger(RW_HT, GetHandleId(rwHero), 90, rwFound)
        call Ab_Sync(rwHero)
        call DisplayTimedTextToPlayer(rwPlayer, 0, 0, 8.0, "|cffffcc00[-abtest]|r " + GetUnitName(rwHero) + " now has |cffffcc00" + Ab_Name[rwFound] + "|r: " + Ab_Info[rwFound])
    endif
    set rwPlayer = null
    set rwHero = null
    return false
endfunction

function RW_Init takes nothing returns nothing
    local trigger rwTrig = CreateTrigger()
    local integer rwPlayer = 0
    call TriggerRegisterAnyUnitEventBJ(rwTrig, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(rwTrig, Condition(function RW_OnCast))
    set rwTrig = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(rwTrig, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(rwTrig, Condition(function RW_OnDeath))
    set rwTrig = CreateTrigger()
    loop
        exitwhen rwPlayer >= 12
        call TriggerRegisterPlayerChatEvent(rwTrig, Player(rwPlayer), "-abtest", false)
        set rwPlayer = rwPlayer + 1
    endloop
    call TriggerAddCondition(rwTrig, Condition(function RW_TestCmd))
    set RW_Timer = CreateTimer()
    call TimerStart(RW_Timer, 0.5, true, function RW_Tick)
    set rwTrig = null
endfunction
// ===== end of the Ability rework =====
