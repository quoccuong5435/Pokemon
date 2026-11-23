"""Build Pokemon Arena v4.1.3g on top of v4.1.3f: four new events (all text in English, all in script).

  * RUSH HOUR   first at 15:00, then every 12-14 min: a rare elite wild Pokemon (power 10, twice the HP, magenta, big)
                appears in one of the 6 tall-grass bushes for 90 s (minimap ping). Killer: +1,500 gold; it drops its
                species Soul (a Rare Candy when the species has none).
  * WEATHER STORM first at 21:00, then every 10 min: a random weather for 60 s that is stronger: Rain / Sun
                Water and Fire moves x1.6 / x0.5 (normal x1.3 / x0.7), Sandstorm Rock / Ground / Steel moves +25%,
                Hail Ice moves +25%.
  * SMUGGLER'S CART first at 18:00, then every 15 min: a harmless cart (20,000 HP) walks the bush loop for 4 min.
                Killer: +3,000 gold, a Rare loot item, a Rare Candy and a vitamin.
  * COMEBACK    a team 6+ team points behind (PAX_Late_TeamPts) gets +10% damage and -10% damage taken for 120 s,
                at most once per 5 min per team (the 10-point Underdog Supply stays as it is).
No new event starts after 53:20, the Rayquaza boss comes at 55:00.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))

import mpq  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, 'Pokemon Arena v4.1.3f.w3x')
NAME = 'v4.1.3g'
OUT_MAP = os.path.join(MAPS, 'Pokemon Arena %s.w3x' % NAME)
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')

GLOBALS = '''// v4.1.3g events
real V413_NextRush = 900.0
real V413_NextStorm = 1260.0
real V413_NextCart = 1080.0
real V413_StormEnd = 0.0
unit V413_Rush = null
real V413_RushEnd = 0.0
trigger V413_RushTrig = null
unit V413_Cart = null
real V413_CartEnd = 0.0
integer V413_CartWp = 0
trigger V413_CartTrig = null
real array V413_CbEnd
real array V413_CbNext
'''

FUNCS = '''// ======== v4.1.3g events: Rush Hour, Weather Storm, Smuggler's Cart, Comeback ========
function V413_TeamOf takes unit u returns integer
    local integer p = GetPlayerId(GetOwningPlayer(u))
    if p < 6 then
        return 1
    elseif p < 12 then
        return 2
    endif
    return 0
endfunction

function V413_Mult takes unit src, unit t, boolean skill, integer mt returns real
    local real m = 1.0
    local integer ts = V413_TeamOf(src)
    local integer tt = V413_TeamOf(t)
    if ts > 0 and Mega_Time < V413_CbEnd[ts] then
        set m = m * 1.1
    endif
    if tt > 0 and Mega_Time < V413_CbEnd[tt] then
        set m = m * 0.9
    endif
    if skill and Mega_Time < V413_StormEnd then
        if mt == T_WATER then
            if Wth_Cur == 1 then
                set m = m * 1.2307
            elseif Wth_Cur == 2 then
                set m = m * 0.7143
            endif
        elseif mt == T_FIRE then
            if Wth_Cur == 2 then
                set m = m * 1.2307
            elseif Wth_Cur == 1 then
                set m = m * 0.7143
            endif
        elseif Wth_Cur == 3 and (mt == T_ROCK or mt == T_GROUND or mt == T_STEEL) then
            set m = m * 1.25
        elseif Wth_Cur == 4 and mt == T_ICE then
            set m = m * 1.25
        endif
    endif
    return m
endfunction

function V413_BushX takes integer i returns real
    if i == 0 then
        return -2200.0
    elseif i == 1 then
        return 2200.0
    elseif i == 2 then
        return -2200.0
    elseif i == 3 then
        return 2200.0
    endif
    return 0.0
endfunction

function V413_BushY takes integer i returns real
    if i == 0 then
        return 1800.0
    elseif i == 1 then
        return 1800.0
    elseif i == 2 then
        return -1800.0
    elseif i == 3 then
        return -1800.0
    elseif i == 4 then
        return 1500.0
    endif
    return -1500.0
endfunction

// the cart loop: (-2200,1800) (0,1500) (2200,1800) (2200,-1800) (0,-1500) (-2200,-1800)
function V413_WpX takes integer i returns real
    if i == 0 then
        return -2200.0
    elseif i == 1 then
        return 0.0
    elseif i == 2 then
        return 2200.0
    elseif i == 3 then
        return 2200.0
    elseif i == 4 then
        return 0.0
    endif
    return -2200.0
endfunction

function V413_WpY takes integer i returns real
    if i == 0 then
        return 1800.0
    elseif i == 1 then
        return 1500.0
    elseif i == 2 then
        return 1800.0
    elseif i == 3 then
        return -1800.0
    elseif i == 4 then
        return -1500.0
    endif
    return -1800.0
endfunction

function V413_Vit takes nothing returns integer
    local integer r = GetRandomInt(0, 3)
    if r == 0 then
        return 'I003'
    elseif r == 1 then
        return 'I004'
    elseif r == 2 then
        return 'I005'
    endif
    return 'I006'
endfunction

function V413_RushDeath takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local unit k = GetKillingUnit()
    local integer soul = LoadInteger(Mega_HT, GetUnitTypeId(u), 8)
    local string who = "Someone"
    if soul != 0 then
        call CreateItem(soul, GetUnitX(u), GetUnitY(u))
    else
        call CreateItem('I007', GetUnitX(u), GetUnitY(u))
    endif
    if k != null and GetPlayerId(GetOwningPlayer(k)) < 12 then
        call AdjustPlayerStateBJ(1500, GetOwningPlayer(k), PLAYER_STATE_RESOURCE_GOLD)
        set who = GetPlayerName(GetOwningPlayer(k))
    endif
    call PAX_MajorEvent("|cff4ade80", "[RUSH HOUR CLEARED]", "|cff7dd3fc" + who + "|r took down the rare |cffffd166" + GetUnitName(u) + "|r (|cffffd166+1,500g|r and a drop)!", 9.0)
    set V413_Rush = null
    set u = null
    set k = null
endfunction

function V413_RushStart takes nothing returns nothing
    local integer b = GetRandomInt(0, 5)
    local real x = V413_BushX(b)
    local real y = V413_BushY(b)
    local integer t = Wild_PickType(10)
    local integer h = 0
    set V413_Rush = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), t, x, y, GetRandomReal(0.0, 360.0))
    if V413_Rush == null then
        return
    endif
    set h = GetHandleId(V413_Rush)
    call SaveInteger(Mega_HT, h, 31, 10)
    call Wild_Apply(V413_Rush)
    call Wild_MakeElite(V413_Rush)
    call SaveInteger(Mega_HT, h, 29, 0)
    call BlzSetUnitMaxHP(V413_Rush, BlzGetUnitMaxHP(V413_Rush) * 2)
    call SetWidgetLife(V413_Rush, I2R(BlzGetUnitMaxHP(V413_Rush)))
    call SetUnitScale(V413_Rush, 1.6, 1.6, 1.6)
    call SetUnitVertexColor(V413_Rush, 255, 120, 255, 255)
    set V413_RushEnd = Mega_Time + 90.0
    if V413_RushTrig != null then
        call DestroyTrigger(V413_RushTrig)
    endif
    set V413_RushTrig = CreateTrigger()
    call TriggerRegisterUnitEvent(V413_RushTrig, V413_Rush, EVENT_UNIT_DEATH)
    call TriggerAddAction(V413_RushTrig, function V413_RushDeath)
    call PingMinimapEx(x, y, 6.0, 255, 120, 255, true)
    call PAX_MajorEvent("|cffd896ff", "[RUSH HOUR!]", "A rare |cffffd166" + GetUnitName(V413_Rush) + "|r is hiding in the tall grass (see the minimap)! Hunt it within |cffffd16690s|r: |cffffd166+1,500g|r and a guaranteed drop!", 10.0)
endfunction

function V413_CartDeath takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local unit k = GetKillingUnit()
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local item it = CreateItem(PAX_Loot_ItemId(2), x, y)
    local string who = "Someone"
    if it != null then
        call PAX_Loot_RollItem(it, 2, GetRandomInt(1, 2))
    endif
    call CreateItem('I007', x + 40.0, y)
    call CreateItem(V413_Vit(), x - 40.0, y)
    if k != null and GetPlayerId(GetOwningPlayer(k)) < 12 then
        call AdjustPlayerStateBJ(3000, GetOwningPlayer(k), PLAYER_STATE_RESOURCE_GOLD)
        set who = GetPlayerName(GetOwningPlayer(k))
    endif
    call PAX_MajorEvent("|cffffd166", "[SMUGGLER CAUGHT!]", "|cff7dd3fc" + who + "|r raided the Smuggler's Cart (|cffffd166+3,000g|r, Rare loot, Rare Candy and a vitamin)!", 9.0)
    set V413_Cart = null
    set it = null
    set u = null
    set k = null
endfunction

function V413_CartStart takes nothing returns nothing
    local integer t = Wild_PickType(6)
    local integer h = 0
    set V413_Cart = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE), t, V413_WpX(0), V413_WpY(0), 0.0)
    if V413_Cart == null then
        return
    endif
    set h = GetHandleId(V413_Cart)
    call SaveInteger(Mega_HT, h, 31, 6)
    call Wild_Apply(V413_Cart)
    call SaveInteger(Mega_HT, h, 29, 0)
    call BlzSetUnitWeaponBooleanField(V413_Cart, UNIT_WEAPON_BF_ATTACKS_ENABLED, 0, false)
    call BlzSetUnitName(V413_Cart, "Smuggler's Cart")
    call BlzSetUnitMaxHP(V413_Cart, 20000)
    call SetWidgetLife(V413_Cart, 20000.0)
    call SetUnitMoveSpeed(V413_Cart, 90.0)
    call SetUnitScale(V413_Cart, 1.4, 1.4, 1.4)
    call SetUnitVertexColor(V413_Cart, 210, 170, 90, 255)
    set V413_CartWp = 1
    set V413_CartEnd = Mega_Time + 240.0
    call IssuePointOrder(V413_Cart, "move", V413_WpX(1), V413_WpY(1))
    if V413_CartTrig != null then
        call DestroyTrigger(V413_CartTrig)
    endif
    set V413_CartTrig = CreateTrigger()
    call TriggerRegisterUnitEvent(V413_CartTrig, V413_Cart, EVENT_UNIT_DEATH)
    call TriggerAddAction(V413_CartTrig, function V413_CartDeath)
    call PingMinimapEx(V413_WpX(0), V413_WpY(0), 6.0, 255, 210, 90, true)
    call PAX_MajorEvent("|cffffd166", "[SMUGGLER'S CART]", "A Smuggler's Cart is rolling around the tall-grass loop for |cffffd1664 min|r (it does not fight back). Raid it: |cffffd166+3,000g|r, Rare loot, Rare Candy and a vitamin!", 10.0)
endfunction

function V413_StormStart takes nothing returns nothing
    local integer w = GetRandomInt(1, 4)
    local string s = ""
    call Wth_Set(w)
    set V413_StormEnd = Mega_Time + 60.0
    if w == 1 then
        set s = "A violent RAIN storm for 60s: Water moves |cffffd166+60%|r, Fire moves |cffffd166-50%|r!"
    elseif w == 2 then
        set s = "A scorching SUN for 60s: Fire moves |cffffd166+60%|r, Water moves |cffffd166-50%|r!"
    elseif w == 3 then
        set s = "A raging SANDSTORM for 60s: Rock, Ground and Steel moves |cffffd166+25%|r!"
    else
        set s = "A freezing HAIL storm for 60s: Ice moves |cffffd166+25%|r!"
    endif
    call PAX_MajorEvent("|cff38bdf8", "[WEATHER STORM!]", s, 9.0)
endfunction

function V413_EventTick takes nothing returns nothing
    local integer cbPts1 = 0
    local integer cbPts2 = 0
    if Mega_Time < 60.0 then
        return
    endif
    // rare Pokemon of the Rush Hour: gone after 90s
    if V413_Rush != null and Mega_Time >= V413_RushEnd then
        if GetWidgetLife(V413_Rush) > 0.405 then
            call DestroyEffect(AddSpecialEffect("Abilities\\\\Spells\\\\Human\\\\MassTeleport\\\\MassTeleportTarget.mdl", GetUnitX(V413_Rush), GetUnitY(V413_Rush)))
            call RemoveUnit(V413_Rush)
            call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffd896ff[RUSH HOUR]|r The rare Pokemon escaped!")
        endif
        set V413_Rush = null
    endif
    // the cart follows the loop and leaves after 4 min
    if V413_Cart != null then
        if Mega_Time >= V413_CartEnd then
            if GetWidgetLife(V413_Cart) > 0.405 then
                call RemoveUnit(V413_Cart)
                call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffffd166[SMUGGLER'S CART]|r The cart got away!")
            endif
            set V413_Cart = null
        elseif GetWidgetLife(V413_Cart) > 0.405 then
            if (GetUnitX(V413_Cart) - V413_WpX(V413_CartWp)) * (GetUnitX(V413_Cart) - V413_WpX(V413_CartWp)) + (GetUnitY(V413_Cart) - V413_WpY(V413_CartWp)) * (GetUnitY(V413_Cart) - V413_WpY(V413_CartWp)) < 40000.0 then
                set V413_CartWp = ModuloInteger(V413_CartWp + 1, 6)
            endif
            call IssuePointOrder(V413_Cart, "move", V413_WpX(V413_CartWp), V413_WpY(V413_CartWp))
        endif
    endif
    if Mega_Time < 3200.0 then
        if Mega_Time >= V413_NextRush and V413_Rush == null then
            set V413_NextRush = Mega_Time + 720.0 + GetRandomReal(0.0, 120.0)
            call V413_RushStart()
        endif
        if Mega_Time >= V413_NextCart and V413_Cart == null then
            set V413_NextCart = Mega_Time + 900.0
            call V413_CartStart()
        endif
        if Mega_Time >= V413_NextStorm and Mega_Time >= V413_StormEnd then
            set V413_NextStorm = Mega_Time + 600.0
            call V413_StormStart()
        endif
    endif
    // comeback: a team 6+ points behind
    set cbPts1 = PAX_Late_TeamPts(1)
    set cbPts2 = PAX_Late_TeamPts(2)
    if cbPts2 - cbPts1 >= 6 and Mega_Time >= V413_CbNext[1] then
        set V413_CbNext[1] = Mega_Time + 300.0
        set V413_CbEnd[1] = Mega_Time + 120.0
        call PAX_MajorEvent("|cff4ade80", "[COMEBACK!]", "|cff66ccffTeam 1|r is trailing by 6+ points: |cffffd166+10% damage|r and |cffffd166-10% damage taken|r for 2 minutes!", 9.0)
    endif
    if cbPts1 - cbPts2 >= 6 and Mega_Time >= V413_CbNext[2] then
        set V413_CbNext[2] = Mega_Time + 300.0
        set V413_CbEnd[2] = Mega_Time + 120.0
        call PAX_MajorEvent("|cff4ade80", "[COMEBACK!]", "|cffff7777Team 2|r is trailing by 6+ points: |cffffd166+10% damage|r and |cffffd166-10% damage taken|r for 2 minutes!", 9.0)
    endif
endfunction

'''


def once(s, old, new):
    if s.count(old) != 1:
        raise SystemExit('anchor count %d: %r' % (s.count(old), old[:80]))
    return s.replace(old, new, 1)


def patch_script(s):
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    s = once(s, '\nendglobals\n', '\n' + GLOBALS + 'endglobals\n')
    s = once(s, 'function Ext_DamageMult takes unit src, unit t, boolean atk, boolean skill, integer mt, real eff returns real\n',
             FUNCS + 'function Ext_DamageMult takes unit src, unit t, boolean atk, boolean skill, integer mt, real eff returns real\n')
    s = once(s, '    local real m = 1.0\n    if Mega_Time >= LoadReal(Fx_HT, hs, 104) and Mega_Time >= LoadReal(Fx_HT, ht, 104) then\n        if skill and mt == T_WATER then',
             '    local real m = V413_Mult(src, t, skill, mt)\n    if Mega_Time >= LoadReal(Fx_HT, hs, 104) and Mega_Time >= LoadReal(Fx_HT, ht, 104) then\n        if skill and mt == T_WATER then')
    s = once(s, 'call TimerStart(CreateTimer(), 0.5, true, function Ver2n_Tick)',
             'call TimerStart(CreateTimer(), 0.5, true, function Ver2n_Tick)\n    call TimerStart(CreateTimer(), 1.0, true, function V413_EventTick)')
    s = s.replace('v4.1.3f', NAME)
    return s.replace('\n', '\r\n') if crlf else s


def build(out, dry):
    if not dry and os.path.exists(out):
        raise SystemExit('Output exists, refusing to overwrite: %s' % out)
    base = mpq.MPQ(BASE_MAP)
    script = patch_script(base.read('scripts' + BS + 'war3map.j').decode('utf-8'))
    w3i = base.read('war3map.w3i').replace(b'4.1.3f', b'4.1.3g')
    files = {'scripts' + BS + 'war3map.j': script.encode('utf-8'), 'war3map.w3i': w3i}
    if dry:
        tmp = os.path.join(REF, '_tmp_v413g_war3map.j')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp],
                           capture_output=True, text=True)
        print('dry run PJASS rc=%d' % r.returncode)
        print((r.stdout + r.stderr)[:1500])
        return
    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(out, files, extra_listfile=('\r\n'.join(listfile) + '\r\n').encode('latin-1'),
                   hash_size=None, extra_names=listfile)
    print('Wrote %s (%.1f MB)' % (out, os.path.getsize(out) / 1048576.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--out', default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run)
