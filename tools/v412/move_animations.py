"""Inject authentic attack and spell casting animations for all Pokémon in v4.1.2."""

def patch_script(s):
    # 1. PkFx_OnCast: animate caster on every move cast
    target_pkfx = '    call PkFx_Layer(fxIdx, 60, fxSrcX, fxSrcY, fxAngle, 0.0)\n    if LoadInteger(PkFx_HT, fxIdx, 90) == 1 then'
    anim_code = '''    call PkFx_Layer(fxIdx, 60, fxSrcX, fxSrcY, fxAngle, 0.0)
    if LoadInteger(PkFx_HT, fxIdx, 90) != 1 and fxCaster != null and GetWidgetLife(fxCaster) > 0.405 then
        if Fx_CurPhys(fxCaster) == 1 then
            call SetUnitAnimation(fxCaster, "attack")
        else
            call SetUnitAnimation(fxCaster, "spell")
        endif
        call QueueUnitAnimation(fxCaster, "stand")
    endif
    if LoadInteger(PkFx_HT, fxIdx, 90) == 1 then'''
    if target_pkfx not in s:
        raise SystemExit('move_animations: target_pkfx anchor not found')
    s = s.replace(target_pkfx, anim_code, 1)

    # 2. Mv_OnCast: animate abilities not handled by PkFx (e.g. status moves)
    target_mv = '''        loop
            exitwhen s >= Mv_Slots
            if Mv_Slot(u, s) == m then
                call BlzStartUnitAbilityCooldown(u, Mv_Id(s, m), BlzGetUnitAbilityCooldown(u, id, 0))
            endif
            set s = s + 1
        endloop'''
    new_mv = '''        loop
            exitwhen s >= Mv_Slots
            if Mv_Slot(u, s) == m then
                call BlzStartUnitAbilityCooldown(u, Mv_Id(s, m), BlzGetUnitAbilityCooldown(u, id, 0))
            endif
            set s = s + 1
        endloop
        if GetWidgetLife(u) > 0.405 and not HaveSavedInteger(PkFx_HT, id, 0) then
            if Fx_CurPhys(u) == 1 then
                call SetUnitAnimation(u, "attack")
            else
                call SetUnitAnimation(u, "spell")
            endif
            call QueueUnitAnimation(u, "stand")
        endif'''
    if target_mv not in s:
        raise SystemExit('move_animations: target_mv anchor not found')
    s = s.replace(target_mv, new_mv, 1)

    return s
