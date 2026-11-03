"""One-off: floating damage numbers for skill damage dealt by the players (shown to the owner, after armor)."""
import io

NL = chr(10)


def edit(path, old, new, enc='utf-8'):
    s = io.open(path, encoding=enc, newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding=enc, newline='').write(s.replace(old, new))


J = 'tools/jass/mega.j'
edit(J, 'unit Npc_Man = null ',
     'integer Dmg_Tags = 0                    // v3.3: floating damage numbers created in the current second (cap Dmg_TagMax)' + NL +
     'constant integer Dmg_TagMax = 40' + NL + 'unit Npc_Man = null ', 'latin-1')
edit(J, 'function Npc_IsMan takes nothing returns boolean' + NL,
     '// v3.3: floating damage number over the target for skill damage (not basic attacks) dealt by a player; the owner sees it' + NL +
     'function Dmg_OnDamaged takes nothing returns boolean' + NL +
     '    local unit src = GetEventDamageSource()' + NL +
     '    local unit t = GetTriggerUnit()' + NL +
     '    local player p = null' + NL +
     '    local real d = GetEventDamage()' + NL +
     '    local texttag tt = null' + NL +
     '    if src != null and d >= 1.0 and Dmg_Tags < Dmg_TagMax and not BlzGetEventIsAttack() then' + NL +
     '        set p = GetOwningPlayer(src)' + NL +
     '        if GetPlayerId(p) < 12 and IsUnitEnemy(t, p) then' + NL +
     '            set Dmg_Tags = Dmg_Tags + 1' + NL +
     '            set tt = CreateTextTag()' + NL +
     '            call SetTextTagText(tt, I2S(R2I(d)), 0.025)' + NL +
     '            call SetTextTagPos(tt, GetUnitX(t) - 40.0, GetUnitY(t), 80.0)' + NL +
     '            call SetTextTagColor(tt, 255, 210, 40, 255)' + NL +
     '            call SetTextTagVelocity(tt, 0.0, 0.04)' + NL +
     '            call SetTextTagPermanent(tt, false)' + NL +
     '            call SetTextTagLifespan(tt, 1.3)' + NL +
     '            call SetTextTagFadepoint(tt, 0.7)' + NL +
     '            call SetTextTagVisibility(tt, GetLocalPlayer() == p)' + NL +
     '        endif' + NL +
     '    endif' + NL +
     '    set src = null' + NL +
     '    set t = null' + NL +
     '    set p = null' + NL +
     '    set tt = null' + NL +
     '    return false' + NL +
     'endfunction' + NL + NL +
     'function Dmg_Reset takes nothing returns nothing' + NL +
     '    set Dmg_Tags = 0' + NL +
     'endfunction' + NL + NL +
     'function Npc_IsMan takes nothing returns boolean' + NL, 'latin-1')
edit(J, '    local trigger nst = null' + NL,
     '    local trigger nst = null' + NL + '    local trigger dmt = null' + NL, 'latin-1')
edit(J, '    set nst = CreateTrigger()' + NL,
     '    set dmt = CreateTrigger()' + NL +
     '    call TriggerRegisterAnyUnitEventBJ(dmt, EVENT_PLAYER_UNIT_DAMAGED)' + NL +
     '    call TriggerAddCondition(dmt, Condition(function Dmg_OnDamaged))' + NL +
     '    call TimerStart(CreateTimer(), 1.0, true, function Dmg_Reset)' + NL +
     '    set nst = CreateTrigger()' + NL, 'latin-1')
edit('tools/jasscheck.py', "'GetSoldItem': 0,",
     "'GetSoldItem': 0, 'SetTextTagColor': 5, 'SetTextTagVelocity': 3, 'SetTextTagLifespan': 2, 'SetTextTagFadepoint': 2,")
edit('tools/jasscheck.py', "'EVENT_PLAYER_UNIT_SELL_ITEM',", "'EVENT_PLAYER_UNIT_SELL_ITEM', 'EVENT_PLAYER_UNIT_DAMAGED',")
print('ok')
