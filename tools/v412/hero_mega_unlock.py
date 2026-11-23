"""Gold '+' Hero Skill Mega & Form Unlock System for Pokemon Arena v4.1.3i:
- Moves ALL 44 Mega/Orb evolutions (AM00..AM0W, AMDL, AM20..AM26) and ALL 8 Form/Plate abilities (AM10..AM17)
  out of shops and directly into each Hero's Gold '+' Hero Skill learn menu (`uhab` in war3map.w3u)!
- Level-gated & Gold-free:
  * Normal Megas unlock at Lv 50 (0 Gold).
  * Legend Megas / Primals / Origins / Forms unlock at Lv 70 (0 Gold).
- Once unlocked via Gold '+', the transform button appears directly on Row 1 of the Command Card
  (Buttonpos 1,1 [D] for 1st form; Buttonpos 2,1 [F] for 2nd form) - 100% separate from Q-W-E-R!
- Grants passive +40 (Mega) / +60 (Form) All Stats automatically upon learning (no inventory slot needed!).
- Removes Mega Shop I/II/III (nMS1, nMS2, nMS3) and Form Shop (nFS0) from the base courtyard.
- Applies real 3D BlzSetUnitSkin swaps in PAX_Form_Appearance for Giratina Origin & Deoxys Attack/Defense/Speed!
"""
import re

# Legend Hero IDs that require Lv 70 to unlock their Mega/Form (normal Megas require Lv 50)
LEGEND_HERO_IDS = {
    'E020', 'E03J', 'E021', 'E026', 'E024', 'P39A', 'P1DA', 'P3XA', 'E022', 'P1TA', 'PZZA',
    'P26A', 'P4UA', 'E029', 'PV2A', 'P21A', 'P3BA', 'E04C', 'E04D', 'E028', 'E023', 'E025',
    'E027', 'E02A', 'P0JA',
    'EL00', 'EL01', 'EL02', 'EL03', 'EL04', 'EL05', 'EL06', 'EL07', 'EL08', 'EL09', 'EL0A',
    'EL0B', 'EL0C', 'EL0D', 'EL0E', 'EL0F', 'EL0G', 'EL0H', 'EL0I', 'EL0J', 'EL0K', 'EL0L',
    'EL0M', 'EL0N', 'EL0O',
}

# Form & Plate abilities (AM10..AM17) -> target Hero unit IDs
FORM_ABIL_TO_HERO = {
    'AM10': ('E02A', 'Arceus Legend Plate', 'ReplaceableTextures\\CommandButtons\\BTNArceus (64 x 64).blp'),
    'AM11': ('E020', 'Galarian Articuno Form', 'ReplaceableTextures\\CommandButtons\\BTNArticuno (64 x 64).blp'),
    'AM12': ('E03J', 'Galarian Zapdos Form', 'ReplaceableTextures\\CommandButtons\\BTNZapdos (64 x 64).blp'),
    'AM13': ('E021', 'Galarian Moltres Form', 'ReplaceableTextures\\CommandButtons\\BTNMoltres (64 x 64).blp'),
    'AM14': ('E028', 'Giratina Origin Form', 'ReplaceableTextures\\CommandButtons\\BTNGiratina (64 x 64).blp'),
    'AM15': ('E04C', 'Dialga Origin Form', 'ReplaceableTextures\\CommandButtons\\BTNDialga (64 x 64).blp'),
    'AM16': ('E04D', 'Palkia Origin Form', 'ReplaceableTextures\\CommandButtons\\BTNPalkia (64 x 64).blp'),
    'AM17': ('E027', 'Deoxys Form Switch', 'ReplaceableTextures\\CommandButtons\\BTNDeoxys (64 x 64).blp'),
}


def _extract_mega_entries(script: str):
    """Returns dict idx -> {Base, Evolve, Name} from Mega_InitData in script."""
    megas = {}
    for field, idx, val in re.findall(r'set Mega_(\w+)\[(\d+)\]\s*=\s*([^\r\n]+)', script):
        if field in ('Base', 'Evolve', 'Name'):
            megas.setdefault(int(idx), {})[field] = val.strip().strip("'\"")
    return megas


def patch_objects_and_units(script: str, w3u, abil, strings: str):
    """Converts all Mega/Form abilities to Gold '+' Hero Abilities and attaches them to Hero `uhab`."""
    megas = _extract_mega_entries(script)
    acol = abil.name_to_x
    by_id = {u.id: u for u in w3u.original + w3u.custom}

    # Build hero_id -> list of (abil_id, display_name, req_lv, is_form)
    hero_to_abs = {}
    for idx in sorted(megas):
        mg = megas[idx]
        hid = mg.get('Base')
        aid = mg.get('Evolve')
        nm = mg.get('Name', f'Mega {idx}')
        if not hid or not aid:
            continue
        req_lv = 70 if hid in LEGEND_HERO_IDS else 50
        hero_to_abs.setdefault(hid, []).append((aid, nm, req_lv, False))

    for aid, (hid, nm, _art) in FORM_ABIL_TO_HERO.items():
        hero_to_abs.setdefault(hid, []).append((aid, nm, 70, True))

    # Move PAXT from (1,1) to (0,1) so (1,1) [D] is always 100% free for Mega/Form button!
    strings = re.sub(
        r'(\[PAXT\][\s\S]*?)Buttonpos=1,1',
        r'\1Buttonpos=0,1',
        strings,
        count=1,
    )

    converted = 0
    for hid, ab_list in hero_to_abs.items():
        u = by_id.get(hid)
        if not u:
            continue
        # Set uhab on Hero unit in war3map.w3u (deduplicated, preserving order)
        cur_uhab = [x.strip() for x in str(u.get('uhab') or '').split(',') if x.strip()]
        for aid, _nm, _rlv, _isf in ab_list:
            if aid not in cur_uhab:
                cur_uhab.append(aid)
        u.set('uhab', 3, ','.join(cur_uhab))

        # Patch each ability in AbilityData.slk & CampaignAbilityStrings.txt
        for slot_i, (aid, nm, req_lv, is_form) in enumerate(ab_list):
            row = abil.find(aid)
            if not row:
                continue
            row[acol['hero']] = '1'
            row[acol['item']] = '0'
            row[acol['levels']] = '1'
            row[acol['reqLevel']] = str(req_lv)
            row[acol['DataC1']] = '1'  # Channel Visible bit
            if is_form and aid != 'AM10':
                row[acol['Cool1']] = '60'  # 60s CD for form switches (down from 600s)

            # Command Card slot: 1st = (1,1) [D], 2nd = (2,1) [F], 3rd = (0,1) [G]
            bp = ('1,1', '2,1', '0,1')[min(slot_i, 2)]
            hk = ('D', 'F', 'G')[min(slot_i, 2)]
            rbp = (f'{slot_i},0')

            sec_pat = re.compile(rf'(?m)^\[{re.escape(aid)}\]\r?\n([\s\S]*?)(?=^\[|\Z)')
            sm = sec_pat.search(strings)
            if sm:
                body = sm.group(1)
                m_art = re.search(r'^Art=([^\r\n]+)', body, re.M)
                art_path = m_art.group(1).strip() if m_art else 'ReplaceableTextures\\CommandButtons\\BTNArcaneOrb.blp'

                # Update Buttonpos & Hotkey
                if re.search(r'^Buttonpos=', body, re.M):
                    body = re.sub(r'^Buttonpos=[^\r\n]+', f'Buttonpos={bp}', body, count=1, flags=re.M)
                else:
                    body = f'Buttonpos={bp}\n' + body
                if re.search(r'^Hotkey=', body, re.M):
                    body = re.sub(r'^Hotkey=[^\r\n]+', f'Hotkey={hk}', body, count=1, flags=re.M)
                else:
                    body = f'Hotkey={hk}\n' + body

                # Add Research fields for Gold '+' Hero Skill learn screen (shows exact gold cost!)
                unlock_cost = 8000 if req_lv >= 70 else 5000
                stat_note = '+60 passive All Stats' if is_form else '+40 passive All Stats'
                rtip = f'Unlock |cffff66cc{nm}|r (Lv {req_lv}, {unlock_cost:,}g) |cffffcc00[{hk}]|r'
                ruber = f'"Unlocks |cffff66cc{nm}|r on your command card [{hk}] at Lv {req_lv} for |cffffd166{unlock_cost:,} Gold|r (one-time payment, no inventory slot needed, {stat_note} once paid)."'
                for k, v in (
                    ('Researchart', art_path),
                    ('Researchbuttonpos', rbp),
                    ('Researchhotkey', hk),
                    ('Researchtip', rtip),
                    ('Researchubertip', ruber),
                ):
                    if re.search(rf'^{k}=', body, re.M):
                        body = re.sub(rf'^{k}=[^\r\n]+', lambda _m, _k=k, _v=v: f'{_k}={_v}', body, count=1, flags=re.M)
                    else:
                        body = body.rstrip('\r\n') + f'\n{k}={v}\n'

                strings = strings[:sm.start(1)] + body + strings[sm.end(1):]
            converted += 1

    print(f"[hero_mega_unlock] Converted {converted} Mega/Form abilities across {len(hero_to_abs)} heroes into Gold '+' Hero Skills.")
    return strings


HERO_UNLOCK_JASS = '''
// ============================================================================
// Pokemon Arena v4.1.3j: Gold '+' Hero Skill Mega & Form Unlock (Gold-Gated)
// - Normal Mega: 5,000g one-time unlock cost.
// - Legend Mega / Form / Plate: 8,000g one-time unlock cost.
// - Paid flag stored in PAX_Leg_HT[GetHandleId(u), abid] == 1.
// - If clicked before having enough gold, ability stays on command card (locked)
//   and automatically charges + unlocks + casts when pressed with enough gold!
// ============================================================================
function PAX_HeroUnlock_Cost takes unit heroUnit, integer abid returns integer
    local integer megaIdx = Mega_IndexOfAbility(abid)
    local integer price = 0
    if abid == 'AM10' or PAX_Form_ItemIndex(abid) > 0 then
        return 8000
    endif
    if megaIdx >= 0 then
        set price = Mega_Price[megaIdx]
        if price <= 0 then
            set price = 5000
        endif
        if PAX_Leg_Index(GetUnitTypeId(heroUnit)) > 0 and price < 8000 then
            set price = 8000
        endif
        return price
    endif
    return 0
endfunction

function PAX_HeroUnlock_TryPay takes unit heroUnit, integer abid returns boolean
    local integer h = GetHandleId(heroUnit)
    local player ownerPl = GetOwningPlayer(heroUnit)
    local integer cost = 0
    local integer curGold = 0
    if LoadInteger(PAX_Leg_HT, h, abid) == 1 then
        set ownerPl = null
        return true
    endif
    set cost = PAX_HeroUnlock_Cost(heroUnit, abid)
    if cost <= 0 then
        call SaveInteger(PAX_Leg_HT, h, abid, 1)
        set ownerPl = null
        return true
    endif
    set curGold = GetPlayerState(ownerPl, PLAYER_STATE_RESOURCE_GOLD)
    if curGold < cost then
        call DisplayTimedTextToPlayer(ownerPl, 0, 0, 6.0, "|cffff5c5c[LOCKED]|r Need |cffffd166" + I2S(cost) + " Gold|r (one-time) to unlock this Mega/Form! (You have " + I2S(curGold) + "g)")
        set ownerPl = null
        return false
    endif
    call SetPlayerState(ownerPl, PLAYER_STATE_RESOURCE_GOLD, curGold - cost)
    call SaveInteger(PAX_Leg_HT, h, abid, 1)
    call PAX_Form_SyncHeldStats(heroUnit)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectTarget.mdl", heroUnit, "origin"))
    call DisplayTimedTextToPlayer(ownerPl, 0, 0, 7.0, "|cffff66cc[UNLOCKED]|r Paid |cffffd166" + I2S(cost) + " Gold|r! Mega/Form permanently unlocked on your Command Card (+40/+60 passive All Stats).")
    set ownerPl = null
    return true
endfunction

function PAX_HeroMegaUnlock_OnLearn takes nothing returns boolean
    local unit heroUnit = GetTriggerUnit()
    local integer learnedAbId = GetLearnedSkill()
    local integer megaIdx = Mega_IndexOfAbility(learnedAbId)
    local integer formSlot = PAX_Form_ItemIndex(learnedAbId)
    if megaIdx >= 0 or formSlot > 0 or learnedAbId == 'AM10' then
        call PAX_HeroUnlock_TryPay(heroUnit, learnedAbId)
    endif
    set heroUnit = null
    return false
endfunction

function PAX_HeroMegaUnlock_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_SKILL)
    call TriggerAddCondition(t, Condition(function PAX_HeroMegaUnlock_OnLearn))
endfunction
'''


def patch_script(s: str) -> str:
    """Updates Mega_CanStart, PAX_Form_CheckReady, PAX_Form_SyncHeldStats, PAX_Form_Appearance,
    removes Mega Shop I/II/III & Form Shop from base, and adds Gold '+' learn trigger."""
    def once(txt, old, new, label):
        c = txt.count(old)
        if c != 1:
            raise SystemExit(f"hero_mega_unlock: anchor '{label}' matched {c} times")
        return txt.replace(old, new, 1)

    # 1. Remove Badge_Count < 4 check from Mega_CanStart (Hero Skill reqLevel=50/70 already gates progression!)
    old_badge_check = (
        "    if Badge_Count(GetPlayerId(GetOwningPlayer(u))) < 4 then\n"
        "        return \"|cffff66ccMega Evolution requires at least 4 Gym Badges.|r\"\n"
        "    endif\n"
    )
    s = once(s, old_badge_check, "", "Mega_CanStart badge check")

    # 2. Make Form Switching FREE of gold (no 10,000g fee) and reduce cooldown to 60s
    old_form_gold_check = (
        "    if LoadInteger(PAX_Leg_HT, h, 141) == 1 and GetPlayerState(GetOwningPlayer(u), PLAYER_STATE_RESOURCE_GOLD) < 10000 then\n"
        "        return \"Switching form again costs 10,000 gold.\"\n"
        "    endif\n"
    )
    s = once(s, old_form_gold_check, "", "PAX_Form_CheckReady gold check")

    old_form_deduct = (
        "    if LoadInteger(PAX_Leg_HT, h, 141) == 1 then\n"
        "        call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) - 10000)\n"
        "    else\n"
        "        call SaveStr(PAX_Leg_HT, h, 148, GetHeroProperName(u))\n"
        "        call SaveInteger(PAX_Leg_HT, h, 141, 1)\n"
        "    endif\n"
        "    call SaveInteger(PAX_Leg_HT, h, 140, newForm)\n"
        "    call SaveReal(PAX_Leg_HT, h, 142, Mega_Time + 600.0)"
    )
    new_form_deduct = (
        "    if LoadInteger(PAX_Leg_HT, h, 141) == 0 then\n"
        "        call SaveStr(PAX_Leg_HT, h, 148, GetHeroProperName(u))\n"
        "        call SaveInteger(PAX_Leg_HT, h, 141, 1)\n"
        "    endif\n"
        "    call SaveInteger(PAX_Leg_HT, h, 140, newForm)\n"
        "    call SaveReal(PAX_Leg_HT, h, 142, Mega_Time + 60.0)"
    )
    s = once(s, old_form_deduct, new_form_deduct, "PAX_Form_Apply free & 60s CD")

    # 3. Update PAX_Form_SyncHeldStats so learned Gold '+' Hero Skills grant +40 (Mega) / +60 (Form) passive stats!
    old_sync = (
        "    if PAX_Form_HasOrb(u, 0) then\n"
        "        set bonus = 60\n"
        "    else\n"
        "        set ut = GetUnitTypeId(u)\n"
        "        loop\n"
        "            exitwhen s >= 6 or bonus > 0\n"
        "            set it = GetItemTypeId(UnitItemInSlot(u, s))\n"
        "            if it != 0 then\n"
        "                set i = 0\n"
        "                loop\n"
        "                    exitwhen i >= Mega_N or bonus > 0\n"
        "                    if Mega_Base[i] == ut and Mega_Stone[i] == it then\n"
        "                        set bonus = 40\n"
        "                    endif\n"
        "                    set i = i + 1\n"
        "                endloop\n"
        "            endif\n"
        "            set s = s + 1\n"
        "        endloop\n"
        "    endif"
    )
    new_sync = (
        "    set ut = GetUnitTypeId(u)\n"
        "    if PAX_Form_HasOrb(u, 0) or LoadInteger(PAX_Leg_HT, h, 'AM10') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM11') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM12') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM13') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM14') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM15') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM16') == 1 or LoadInteger(PAX_Leg_HT, h, 'AM17') == 1 then\n"
        "        set bonus = 60\n"
        "    else\n"
        "        // Check paid Gold '+' Mega Hero Skills first (no inventory item needed!)\n"
        "        set i = 0\n"
        "        loop\n"
        "            exitwhen i >= Mega_N or bonus > 0\n"
        "            if Mega_Base[i] == ut and LoadInteger(PAX_Leg_HT, h, Mega_Evolve[i]) == 1 then\n"
        "                set bonus = 40\n"
        "            endif\n"
        "            set i = i + 1\n"
        "        endloop\n"
        "        // Fallback: legacy held Mega Stone check\n"
        "        set s = 0\n"
        "        loop\n"
        "            exitwhen s >= 6 or bonus > 0\n"
        "            set it = GetItemTypeId(UnitItemInSlot(u, s))\n"
        "            if it != 0 then\n"
        "                set i = 0\n"
        "                loop\n"
        "                    exitwhen i >= Mega_N or bonus > 0\n"
        "                    if Mega_Base[i] == ut and Mega_Stone[i] == it then\n"
        "                        set bonus = 40\n"
        "                    endif\n"
        "                    set i = i + 1\n"
        "                endloop\n"
        "            endif\n"
        "            set s = s + 1\n"
        "        endloop\n"
        "    endif"
    )
    s = once(s, old_sync, new_sync, "PAX_Form_SyncHeldStats")

    # 3b. Require gold payment in Mega_OnCast if hero clicked '+' before having enough gold!
    old_mega_oncast = (
        "function Mega_OnCast takes nothing returns boolean\n"
        "    local integer abid = GetSpellAbilityId()\n"
        "    local integer idx = Mega_IndexOfAbility(abid)\n"
        "    if PAX_Form_ItemIndex(abid) > 0 then\n"
        "        call PAX_Form_UseItem(GetTriggerUnit(), abid)\n"
        "        return false\n"
        "    endif\n"
        "    if abid == 'AM10' then\n"
        "        call PAX_Plate_Open(GetTriggerUnit())\n"
        "        return false\n"
        "    endif\n"
        "    if idx >= 0 then\n"
        "        call Mega_TryStart(GetTriggerUnit(), idx)\n"
        "    endif\n"
        "    return false\n"
        "endfunction"
    )
    new_mega_oncast = (
        "function Mega_OnCast takes nothing returns boolean\n"
        "    local integer abid = GetSpellAbilityId()\n"
        "    local integer idx = Mega_IndexOfAbility(abid)\n"
        "    local unit castUnit = GetTriggerUnit()\n"
        "    if PAX_Form_ItemIndex(abid) > 0 then\n"
        "        if PAX_HeroUnlock_TryPay(castUnit, abid) then\n"
        "            call PAX_Form_UseItem(castUnit, abid)\n"
        "        endif\n"
        "        set castUnit = null\n"
        "        return false\n"
        "    endif\n"
        "    if abid == 'AM10' then\n"
        "        if PAX_HeroUnlock_TryPay(castUnit, abid) then\n"
        "            call PAX_Plate_Open(castUnit)\n"
        "        endif\n"
        "        set castUnit = null\n"
        "        return false\n"
        "    endif\n"
        "    if idx >= 0 then\n"
        "        if PAX_HeroUnlock_TryPay(castUnit, abid) then\n"
        "            call Mega_TryStart(castUnit, idx)\n"
        "        endif\n"
        "    endif\n"
        "    set castUnit = null\n"
        "    return false\n"
        "endfunction"
    )
    s = once(s, old_mega_oncast, new_mega_oncast, "Mega_OnCast gold gate")

    # 4. Upgrade PAX_Form_Appearance to swap real 3D models via BlzSetUnitSkin for Giratina Origin & Deoxys A/D/S!
    old_gira = (
        "    elseif formId == 4 then\n"
        "        set name = \"Giratina (Origin Form)\"\n"
        "        set red = 205\n"
        "        set green = 170"
    )
    new_gira = (
        "    elseif formId == 4 then\n"
        "        set name = \"Giratina (Origin Form)\"\n"
        "        call BlzSetUnitSkin(u, 'hMF4')"
    )
    s = once(s, old_gira, new_gira, "PAX_Form_Appearance Giratina Origin")

    old_deox = (
        "    elseif formId == 7 then\n"
        "        set name = \"Deoxys (Attack Form)\"\n"
        "        set green = 155\n"
        "        set blue = 135\n"
        "    elseif formId == 8 then\n"
        "        set name = \"Deoxys (Defense Form)\"\n"
        "        set red = 150\n"
        "        set green = 200\n"
        "    elseif formId == 9 then\n"
        "        set name = \"Deoxys (Speed Form)\"\n"
        "        set red = 160\n"
        "        set blue = 200"
    )
    new_deox = (
        "    elseif formId == 7 then\n"
        "        set name = \"Deoxys (Attack Form)\"\n"
        "        call BlzSetUnitSkin(u, 'hMF7')\n"
        "    elseif formId == 8 then\n"
        "        set name = \"Deoxys (Defense Form)\"\n"
        "        call BlzSetUnitSkin(u, 'hMF8')\n"
        "    elseif formId == 9 then\n"
        "        set name = \"Deoxys (Speed Form)\"\n"
        "        call BlzSetUnitSkin(u, 'hMF9')"
    )
    s = once(s, old_deox, new_deox, "PAX_Form_Appearance Deoxys 3D")

    # Reset skin when returning to formId == 0
    old_form_app_head = "    if formId == 1 then\n        set name = \"Galarian Articuno\""
    new_form_app_head = "    if formId == 0 then\n        call BlzSetUnitSkin(u, GetUnitTypeId(u))\n    elseif formId == 1 then\n        set name = \"Galarian Articuno\""
    s = once(s, old_form_app_head, new_form_app_head, "PAX_Form_Appearance reset skin")

    # 5. Remove Mega Shop I, II, III (nMS1, nMS2, nMS3) and Form Shop (nFS0) from Base Courtyard!
    for line in (
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', -5950.0, -544.0, 90.0)",
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS1', 5950.0, -544.0, 90.0)",
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', -5800.0, -544.0, 90.0)",
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS2', 5800.0, -544.0, 90.0)",
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', -5650.0, -544.0, 90.0)",
        "    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nMS3', 5650.0, -544.0, 90.0)",
    ):
        s = once(s, line, "    // Mega Shop removed (moved to Gold '+' Hero Skill)", f"remove {line[:45]}")

    old_nfs0 = (
        "        set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nFS0', x, -544.0, 90.0)\n"
        "        if shop != null then\n"
        "            call SetUnitVertexColor(shop, 255, 215, 80, 255)\n"
        "            call PAX_MapLabel(\"|cffffd750Form Shop|r\", x - 42.0, -544.0, 165.0)\n"
        "        endif"
    )
    s = once(s, old_nfs0, "        // Form Shop removed (Forms moved to Gold '+' Hero Skill)", "remove nFS0 Form Shop")

    # 6. Insert Gold '+' Hero Skill unlock trigger AFTER Mega_IndexOfAbility and wire it in map init
    anchor_init_fn = "function Mega_OnCast takes nothing returns boolean"
    s = once(s, anchor_init_fn, HERO_UNLOCK_JASS + "\n" + anchor_init_fn, "insert HERO_UNLOCK_JASS")

    anchor_init_call = "    call PAX_DecorateMap()"
    s = once(s, anchor_init_call, anchor_init_call + "\n    call PAX_HeroMegaUnlock_Init()", "wire PAX_HeroMegaUnlock_Init")

    return s
