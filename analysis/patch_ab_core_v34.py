"""One-off edit of tools/v34/jass/ab_core.j: Strong Jaw, Solar Power, Skill Link, Zen Mode."""
p = 'tools/v34/jass/ab_core.j'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


rep("""    elseif a == AB_SUPERLUCK then
        set critc = 0.25
        set cm = 1.5
    endif
""", """    elseif a == AB_SUPERLUCK then
        set critc = 0.25
        set cm = 1.5
    elseif a == AB_STRONGJAW then
        if atk then
            set m = 1.3
        endif
    elseif a == AB_SOLARPOWER then
        if skill then
            set m = 1.4
        endif
    elseif a == AB_SKILLLINK then
        if skill then
            set m = 1.2
        endif
    elseif a == AB_ZENMODE then
        if LoadInteger(Ab_HT, h, 85) == 1 then
            if atk then
                set m = 0.5
            elseif skill then
                set m = 1.5
            endif
        endif
    endif
""")
rep("""    elseif a == AB_RECKLESS then
        if GetWidgetLife(src) - 0.05 * d > 1.0 then
            call SetWidgetLife(src, GetWidgetLife(src) - 0.05 * d)
        endif
    endif
endfunction
""", """    elseif a == AB_RECKLESS then
        if GetWidgetLife(src) - 0.05 * d > 1.0 then
            call SetWidgetLife(src, GetWidgetLife(src) - 0.05 * d)
        endif
    elseif a == AB_STRONGJAW then
        if atk and GetRandomReal(0.0, 1.0) < 0.2 then
            call Ab_Deal(src, t, 0.5 * d)
            set Ab_FxCur = src
            call Ab_FxAdd(t, 1, 3.0, 0.01 * mx)
            set Ab_FxCur = null
            call Ab_Pop(t, "Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodFootman.mdl", "chest")
        endif
    elseif a == AB_SKILLLINK then
        if atk and GetRandomReal(0.0, 1.0) < 0.3 then
            call Ab_Deal(src, t, 0.5 * d)
            call Ab_Deal(src, t, 0.5 * d)
            call Ab_Say(t, "x3!", 255, 200, 60, GetOwningPlayer(src), GetOwningPlayer(t))
        endif
    endif
endfunction
""")
rep("""    elseif a == AB_SHADOWTAG then
        call Ab_Aura(u, a, 450.0)
    endif
    call Ab_MoveBonus(u, a)
""", """    elseif a == AB_SHADOWTAG then
        call Ab_Aura(u, a, 450.0)
    elseif a == AB_SOLARPOWER then
        if idle < 3.0 and GetWidgetLife(u) - 0.01 * mx > 0.3 * mx then
            call SetWidgetLife(u, GetWidgetLife(u) - 0.01 * mx)
        endif
    elseif a == AB_ZENMODE then
        if GetWidgetLife(u) < 0.5 * mx then
            if LoadInteger(Ab_HT, h, 85) != 1 and Ab_ZenSkin != 0 then
                call SaveInteger(Ab_HT, h, 85, 1)
                call BlzSetUnitSkin(u, Ab_ZenSkin)
                call SetUnitScale(u, Ab_ZenScale, Ab_ZenScale, Ab_ZenScale)
                call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + Ab_ZenArmor)
                call Ab_Pop(u, "Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl", "origin")
                call Ab_Say(u, "Zen Mode!", 200, 120, 255, GetOwningPlayer(u), GetOwningPlayer(u))
            endif
        elseif LoadInteger(Ab_HT, h, 85) == 1 then
            call SaveInteger(Ab_HT, h, 85, 0)
            call BlzSetUnitSkin(u, GetUnitTypeId(u))
            call SetUnitScale(u, Ab_ZenBase, Ab_ZenBase, Ab_ZenBase)
            call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - Ab_ZenArmor)
        endif
    endif
    call Ab_MoveBonus(u, a)
""")
open(p, 'w', encoding='utf-8').write(s)
print('ab_core.j patched')
