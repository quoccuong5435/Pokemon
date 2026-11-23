// ver2 Dynamax: the big blast of a Max Move per type (T_ order), models already in the map
function Dyna_Data takes nothing returns nothing
    local trigger t = CreateTrigger()
    set Fx_MaxFx[0] = "PkFx\\SuperBigBombExplosion_Green.mdx"
    set Fx_MaxScale[0] = 0.43
    set Fx_MaxFx[1] = "PkFx\\Black_Stomp.mdx"
    set Fx_MaxScale[1] = 0.83
    set Fx_MaxFx[2] = "PkFx\\Bijuu_Dama_2.mdx"
    set Fx_MaxScale[2] = 0.62
    set Fx_MaxFx[3] = "PkFx\\GreatLightning.mdx"
    set Fx_MaxScale[3] = 1.66
    set Fx_MaxFx[4] = "PkFx\\White_Holy.mdx"
    set Fx_MaxScale[4] = 1.21
    set Fx_MaxFx[5] = "PkFx\\Lion_Fists_Crit_1.mdx"
    set Fx_MaxScale[5] = 0.66
    set Fx_MaxFx[6] = "PkFx\\FireStomp.mdx"
    set Fx_MaxScale[6] = 0.77
    set Fx_MaxFx[7] = "PkFx\\AZ_Air_Dust.mdx"
    set Fx_MaxScale[7] = 0.55
    set Fx_MaxFx[8] = "PkFx\\MS_Tsukuyomi__1.mdx"
    set Fx_MaxScale[8] = 1.38
    set Fx_MaxFx[9] = "PkFx\\Mokuton_Sashiki_All.mdx"
    set Fx_MaxScale[9] = 0.66
    set Fx_MaxFx[10] = "PkFx\\EarthNova.mdx"
    set Fx_MaxScale[10] = 0.71
    set Fx_MaxFx[11] = "PkFx\\IceStomp.mdx"
    set Fx_MaxScale[11] = 0.59
    set Fx_MaxFx[12] = "PkFx\\Super_Big_Explosion_White_2020.mdx"
    set Fx_MaxScale[12] = 0.62
    set Fx_MaxFx[13] = "PkFx\\Doku_Doku_Effect__6_.mdx"
    set Fx_MaxScale[13] = 1.47
    set Fx_MaxFx[14] = "PkFx\\PsiWave.mdx"
    set Fx_MaxScale[14] = 1.53
    set Fx_MaxFx[15] = "PkFx\\Earth_Slam_2020.mdx"
    set Fx_MaxScale[15] = 1.42
    set Fx_MaxFx[16] = "PkFx\\ShockwaveYellow.mdx"
    set Fx_MaxScale[16] = 0.91
    set Fx_MaxFx[17] = "PkFx\\TidalEruption.mdx"
    set Fx_MaxScale[17] = 1.90
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function Fx_DynaCast))
    set t = null
endfunction
