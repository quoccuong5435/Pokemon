"""Hidden Ability (Ability Patch item, 10,000 gold) for the v4.2x line: make the awakening do something.

In v4.2a the item only stored the Hidden Ability's name on the unit (AbilityPatch_HT handle keys 100 / 101); no code read
it, so the gold bought nothing. patch(script):
1. AbilityPatch_HT unit type key 3 = Ability number of the type's Hidden Ability, for every Hidden Ability whose name is
   an Ability the map already runs for any Pokemon (Ab_Name + code that uses its AB_ constant). Generated function
   HiddenAb_InitIdx, called at the end of AbilityPatch_Init.
2. Ab_Want: an awakened unit (handle key 101 = 1) uses the Hidden Ability of its current type (Mega and form Abilities
   still come first). The Ability info button changes through Ab_Sync, called right after the awakening.
3. Mega_SafeReplace: the awakening stays with the Pokemon when it evolves or is replaced.
4. AbilityPatch_PromptBuy: refunds when the Hidden Ability has no code yet or the unit is already awakened (the old
   message said so, but the code did not check it).

Usage from a build script:  import hidden_ability;  script = hidden_ability.patch(script)
"""
import re

LEGEND_ONLY_NOTE = 'Abilities whose AB_ constant no code uses (they run through legend codes) are left out.'


def _rep(text, old, new, what):
    """replace a block given as a list of lines; it must be found exactly once. The new lines get the line ending
    that follows the block's first line in the file (CR LF or LF)."""
    for eol in ('\r\n', '\n'):
        o = eol.join(old) + eol
        n = text.count(o)
        if n == 1:
            return text.replace(o, eol.join(new) + eol)
        if n > 1:
            break
    raise ValueError('[hidden_ability] anchor not found exactly once: %s' % what)


def used_ability_numbers(script):
    """numbers of the Abilities whose AB_ constant some code uses (one that appears only in its own definition has no code)"""
    consts = {m.group(1): int(m.group(2)) for m in re.finditer(r'constant integer (AB_[A-Z0-9_]+) = (\d+)', script)}
    return {num for name, num in consts.items() if len(re.findall(r'\b%s\b' % name, script)) > 1}


def ability_table(script):
    """{unit type id: (hidden name, Ability number or 0)} and the list of names without code"""
    used = used_ability_numbers(script)
    index = {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', script):
        index[m.group(2)] = int(m.group(1))  # the last one wins: reworked Abilities (ability_rw.py) come later
    table = {}
    for m in re.finditer(r"call SaveStr\(AbilityPatch_HT, '(\w{4})', 1, \"(.*?)\"\)", script):
        num = index.get(m.group(2), 0)
        table[m.group(1)] = (m.group(2), num if num in used else 0)
    return table


def patch(script):
    if 'HiddenAb_InitIdx' in script:
        raise ValueError('[hidden_ability] already applied')
    table = ability_table(script)
    if not table:
        raise ValueError('[hidden_ability] no Hidden Ability table (AbilityPatch_HT) in the script')

    # 1. type -> Ability number, set up with the rest of the Ability Patch data
    body = ['// v4.2x: Ability number of each unit type\'s Hidden Ability (0 / missing = no code for it yet)',
            'function HiddenAb_InitIdx takes nothing returns nothing']
    for uid, (_name, num) in sorted(table.items()):
        if num:
            body.append("    call SaveInteger(AbilityPatch_HT, '%s', 3, %d)" % (uid, num))
    body += ['endfunction', '', 'function AbilityPatch_Init takes nothing returns nothing']
    script = _rep(script, ['function AbilityPatch_Init takes nothing returns nothing'], body, 'AbilityPatch_Init header')
    script = _rep(script, ['    call AbilityPatch_InitPart_7()'],
                  ['    call AbilityPatch_InitPart_7()', '    call HiddenAb_InitIdx()'], 'AbilityPatch_InitPart_7 call')

    # 2. Ab_Want: awakened units use the Hidden Ability of their type
    script = _rep(script, [
        '        return AB_QUARKDRIVE',
        '    endif',
        '    return LoadInteger(Ab_HT, GetUnitTypeId(u), 0)',
    ], [
        '        return AB_QUARKDRIVE',
        '    endif',
        '    if LoadInteger(AbilityPatch_HT, GetHandleId(u), 101) == 1 and LoadInteger(AbilityPatch_HT, GetUnitTypeId(u), 3) > 0 then',
        '        return LoadInteger(AbilityPatch_HT, GetUnitTypeId(u), 3)  // v4.2x: awakened Hidden Ability',
        '    endif',
        '    return LoadInteger(Ab_HT, GetUnitTypeId(u), 0)',
    ], 'end of Ab_Want')

    # ... and switch at once after the awakening
    script = _rep(script, [
        '            call SaveInteger(AbilityPatch_HT, GetHandleId(u), 101, 1)',
    ], [
        '            call SaveInteger(AbilityPatch_HT, GetHandleId(u), 101, 1)',
        '            call Ab_Sync(u)  // v4.2x: the Hidden Ability replaces the Ability now',
    ], 'awakening in AbilityPatch_OnDialogClick')

    # 3. evolution / replacement keeps the awakening
    script = _rep(script, [
        '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)',
    ], [
        '        call SaveInteger(Ab_HT, GetHandleId(nu), 124, 1)',
        '        call SaveInteger(AbilityPatch_HT, GetHandleId(nu), 101, LoadInteger(AbilityPatch_HT, h, 101))  // v4.2x: Hidden Ability stays',
        '        call SaveStr(AbilityPatch_HT, GetHandleId(nu), 100, LoadStr(AbilityPatch_HT, h, 100))',
    ], 'Shiny copy in Mega_SafeReplace')

    # 4. no sale without code, no second awakening
    refund = [
        '        call RemoveItem(it)',
        '        call SetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(p, PLAYER_STATE_RESOURCE_GOLD) + 10000)',
        '        set p = null',
        '        return',
        '    endif',
    ]
    script = _rep(script, [
        '    set AbilityPatch_Unit[pid] = b',
        '    set AbilityPatch_Item[pid] = it',
    ], [
        '    if LoadInteger(AbilityPatch_HT, GetHandleId(b), 101) == 1 then  // v4.2x',
        '        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[Ability Patch]|r " + GetUnitName(b) + " already has its Hidden Ability. Refunded 10,000 Gold.")',
    ] + refund + [
        '    if LoadInteger(AbilityPatch_HT, ut, 3) == 0 then  // v4.2x: Hidden Abilities without code are not sold',
        '        call DisplayTimedTextToPlayer(p, 0, 0, 5.0, "|cffffcc00[Ability Patch]|r Hidden Ability " + ha_name + " is not available yet. Refunded 10,000 Gold.")',
    ] + refund + [
        '',
        '    set AbilityPatch_Unit[pid] = b',
        '    set AbilityPatch_Item[pid] = it',
    ], 'AbilityPatch_PromptBuy body')
    return script
