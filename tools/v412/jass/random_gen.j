// ===== random_gen (tools/v412/random_gen.py): "-random" or "-random <gen>" (1..9, "gen3" also works) =====
// RandG_HT: hero type -> generation (key 0), filled by RandG_Init. RandG_Want = wanted generation, 0 = any.
function RandG_Build takes integer want returns nothing
    local integer i = 0
    set RandG_Want = want
    set RandG_ListN = 0
    if want <= 0 then
        return
    endif
    loop
        exitwhen i >= Rand_N
        if LoadInteger(RandG_HT, Rand_Type[i], 0) == want then
            set RandG_List[RandG_ListN] = Rand_Type[i]
            set RandG_ListN = RandG_ListN + 1
        endif
        set i = i + 1
    endloop
endfunction

function RandG_Pick takes nothing returns integer
    if RandG_Want > 0 and RandG_ListN > 0 then
        return RandG_List[GetRandomInt(0, RandG_ListN - 1)]
    endif
    return Rand_Type[GetRandomInt(0, Rand_N - 1)]
endfunction

