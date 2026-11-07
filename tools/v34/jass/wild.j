//@replace Wild_PickType
// v3.4: the pool has ~1000 entries (211 new species, one entry per power they appear at); the old pick scanned it
// twice per camp, too much for one thread when many camps spawn. Wild_IndexPool (once, at init) indexes it by power.
function Wild_IndexPool takes nothing returns nothing
    local integer i = 0
    local integer powi = 0
    loop
        exitwhen i >= Wild_PoolN
        set powi = Wild_PoolPow[i]
        if powi >= 1 and powi <= 10 and Wild_PowCnt[powi] < Wild_PowStride then
            set Wild_PowAt[powi * Wild_PowStride + Wild_PowCnt[powi]] = i
            set Wild_PowCnt[powi] = Wild_PowCnt[powi] + 1
        endif
        set i = i + 1
    endloop
endfunction

// a random species of that power (or of the highest lower power that has one)
function Wild_PickType takes integer pow returns integer
    local integer p = pow
    if p > 10 then
        set p = 10
    endif
    loop
        exitwhen p < 1
        if Wild_PowCnt[p] > 0 then
            return Wild_Pool[Wild_PowAt[p * Wild_PowStride + GetRandomInt(0, Wild_PowCnt[p] - 1)]]
        endif
        set p = p - 1
    endloop
    return Wild_Pool[0]
endfunction
