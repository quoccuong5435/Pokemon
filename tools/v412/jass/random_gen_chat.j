function Rand_OnChat takes nothing returns nothing
    local string s = StringCase(GetEventPlayerChatString(), false)
    local integer len = StringLength(s)
    local integer want = 0
    local string arg = ""
    if SubString(s, 0, 7) != "-random" then
        return
    endif
    if len > 7 then
        if SubString(s, 7, 8) != " " then
            return
        endif
        set arg = SubString(s, 8, len)
        if SubString(arg, 0, 4) == "gen " then
            set arg = SubString(arg, 4, StringLength(arg))
        elseif SubString(arg, 0, 3) == "gen" then
            set arg = SubString(arg, 3, StringLength(arg))
        endif
        set want = S2I(arg)
        if want < 1 or want > 9 then
            call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 6.0, "|cffffcc00Type -random, or -random 1 .. 9 for one generation.|r")
            return
        endif
    endif
    if GetPlayerId(GetTriggerPlayer()) != Host_Id() then
        call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 5.0, "|cffffcc00Only the host can type -random.|r")
        return
    endif
    call RandG_Build(want)
    if want > 0 then
        if RandG_ListN == 0 then
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00No Pokemon of Gen " + I2S(want) + " in the pool: random from all generations.|r")
        else
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffcc00Random Pokemon from Gen " + I2S(want) + " (" + I2S(RandG_ListN) + " Pokemon).|r")
        endif
    endif
    call Rand_Auto()
    call RandG_Build(0)
endfunction
