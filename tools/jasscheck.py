"""Small static checker for the JASS we add (names, arg counts, declaration order, block balance).

Not a full compiler: it catches typos and structural mistakes before the map reaches the game.
"""
import re

# natives / Blizzard.j functions used by tools/jass/mega.j -> argument count (WC3 1.36 common.j / Blizzard.j)
NATIVES = {
    # hashtable
    'InitHashtable': 0, 'SaveInteger': 4, 'LoadInteger': 3, 'SaveReal': 4, 'LoadReal': 3, 'SaveStr': 4,
    'LoadStr': 3, 'SaveEffectHandle': 4, 'LoadEffectHandle': 3, 'SaveUnitHandle': 4, 'LoadUnitHandle': 3,
    'FlushChildHashtable': 2, 'HaveSavedInteger': 3, 'RemoveSavedHandle': 3, 'GetHandleId': 1,
    # dialogs (learned moves)
    'DialogCreate': 0, 'DialogClear': 1, 'DialogSetMessage': 2, 'DialogAddButton': 3, 'DialogDisplay': 3,
    'TriggerRegisterDialogEvent': 2, 'GetClickedDialog': 0, 'GetClickedButton': 0,
    # units
    'GetUnitTypeId': 1, 'GetOwningPlayer': 1, 'IsUnitType': 2, 'GetWidgetLife': 1, 'GetUnitX': 1,
    'GetUnitY': 1, 'GetUnitFacing': 1, 'SetUnitFacing': 2, 'SetUnitPosition': 3, 'SetUnitScale': 4,
    'SetUnitVertexColor': 5, 'UnitAddAbility': 2, 'UnitAddItemById': 2, 'UnitRemoveAbility': 2, 'GetUnitAbilityLevel': 2,
    'UnitMakeAbilityPermanent': 3, 'UnitInventorySize': 1, 'UnitItemInSlot': 2, 'GetItemTypeId': 1,
    'CreateUnit': 5, 'RemoveUnit': 1, 'KillUnit': 1, 'IssuePointOrder': 4, 'SetUnitAnimation': 2,
    'QueueUnitAnimation': 2, 'UnitDamageTarget': 8, 'GetHeroStr': 2, 'GetHeroProperName': 1,
    'GetHeroAgi': 2, 'GetHeroInt': 2, 'SetHeroStr': 3, 'SetHeroAgi': 3, 'SetHeroInt': 3,
    'BlzSetUnitBaseDamage': 3, 'BlzGetUnitMaxHP': 1, 'BlzSetUnitMaxHP': 2, 'BlzGetUnitArmor': 1,
    'BlzSetUnitArmor': 2, 'BlzGetUnitIntegerField': 2, 'BlzSetUnitIntegerField': 3, 'GetUnitLifePercent': 1,
    'SetUnitLifePercentBJ': 2, 'GetRandomInt': 2, 'GetRandomReal': 2, 'SaveBoolean': 4, 'LoadBoolean': 3,
    'SetUnitInvulnerable': 2, 'SetUnitPathing': 2, 'IsUnitInGroup': 2, 'UnitApplyTimedLife': 3,
    'SetUnitMoveSpeed': 2, 'SuspendHeroXP': 2, 'SetPlayerAlliance': 4, 'GetPlayerAlliance': 3, 'GetEventPlayerChatString': 0, 'StringCase': 2, 'ReviveHero': 4, 'BlzSetAbilityExtendedTooltip': 3,
    # Reforged natives
    'BlzSetUnitSkin': 2, 'BlzStartUnitAbilityCooldown': 3, 'BlzGetUnitAbilityCooldownRemaining': 2,
    'BlzSetHeroProperName': 2, 'BlzGetUnitBaseDamage': 2, 'BlzGetUnitWeaponIntegerField': 3,
    'BlzEndUnitAbilityCooldown': 2, 'ReplaceUnitBJ': 3, 'HaveSavedReal': 3,
    # groups
    'CreateGroup': 0, 'GroupEnumUnitsOfPlayer': 3, 'FirstOfGroup': 1, 'GroupRemoveUnit': 2,
    'GroupAddUnit': 2, 'GroupClear': 1, 'ForGroup': 2, 'GetEnumUnit': 0,
    'GetTriggerPlayer': 0, 'GetHeroLevel': 1, 'TriggerSleepAction': 1, 'RemoveItem': 1,
    'GetManipulatedItem': 0, 'BlzGetEventDamageTarget': 0, 'BlzSetEventDamage': 1, 'PingMinimap': 3,
    'CreateItem': 3, 'GetUnitName': 1, 'GetEnteringUnit': 0, 'TriggerRegisterEnterRectSimple': 2,
    'SetHeroLevel': 3, 'SetPlayerState': 3, 'GetPlayerState': 2, 'GetHeroXP': 1, 'SetHeroXP': 3, 'UnitRemoveItem': 2, 'SetItemVisible': 2,
    'SaveItemHandle': 4, 'LoadItemHandle': 3, 'UnitAddItem': 2, 'GetSoldUnit': 0, 'GetSoldItem': 0, 'GroupEnumUnitsInRange': 5, 'GetUnitFacing': 1, 'BlzSetUnitIntegerField': 3, 'SetTextTagColor': 5, 'SetTextTagVelocity': 3, 'SetTextTagLifespan': 2, 'SetTextTagFadepoint': 2, 'CreateTextTag': 0, 'SetTextTagText': 3, 'SetTextTagPos': 4, 'SetTextTagPermanent': 2,
    'SetTextTagVisibility': 2, 'SetUnitInvulnerable': 2, 'GetItemName': 1, 'StringLength': 1, 'SubString': 3, 'UnitRemoveItem': 2, 'GetBuyingUnit': 0, 'SetUnitPosition': 3, 'PanCameraToTimedForPlayer': 4, 'GetUnitLevel': 1, 'TriggerRegisterPlayerChatEvent': 4, 'TriggerRegisterPlayerUnitEvent': 4, 'SelectUnitForPlayerSingle': 2,
    # events / triggers / timers
    'CreateTrigger': 0, 'TriggerRegisterAnyUnitEventBJ': 2, 'TriggerAddAction': 2, 'TriggerAddCondition': 2,
    'Condition': 1, 'GetTriggerUnit': 0, 'GetSpellAbilityId': 0, 'GetAttacker': 0, 'GetDyingUnit': 0,
    'CreateTimer': 0, 'TimerStart': 4, 'GetEventDamageSource': 0,
    # effects / text / players / misc
    'AddSpecialEffectTarget': 3, 'AddSpecialEffect': 3, 'DestroyEffect': 1, 'Player': 1, 'GetPlayerName': 1,
    'DisplayTimedTextToPlayer': 5, 'GetLocalPlayer': 0, 'CreateQuestBJ': 4, 'ConvertAttackType': 1,
    'I2S': 1, 'R2I': 1, 'I2R': 1, 'R2S': 1, 'SquareRoot': 1, 'Cos': 1, 'Sin': 1, 'Atan2': 2,
    'GetPlayerId': 1, 'GetPlayerController': 1, 'GetPlayerSlotState': 1, 'StringLength': 1,
    # abilities (v2.8)
    'GetEventDamage': 0, 'BlzGetEventDamageType': 0, 'BlzGetEventIsAttack': 0, 'IsUnitEnemy': 2,
    'SetWidgetLife': 2, 'GetUnitState': 2, 'SetUnitState': 3, 'SubString': 3, 'GetUnitMoveSpeed': 1,
    'PauseUnit': 2, 'GroupEnumUnitsInRange': 5,  # UnitAlive is NOT a WC3 native: use GetWidgetLife(u) > 0.405
    # whole map visible (v3.2)
    'FogEnable': 1, 'FogMaskEnable': 1,
    # NPC dialogs (v3.2)
    'DialogCreate': 0, 'DialogClear': 1, 'DialogAddButton': 3, 'DialogSetMessage': 2, 'DialogDisplay': 3,
    'TriggerRegisterDialogEvent': 2, 'GetClickedDialog': 0, 'GetClickedButton': 0,
}

# constants from common.j / Blizzard.j used by mega.j
KNOWN_GLOBALS = {
    'EVENT_PLAYER_UNIT_SPELL_EFFECT', 'EVENT_PLAYER_UNIT_SELECTED', 'EVENT_PLAYER_UNIT_SELL_ITEM', 'UNIT_IF_LEVEL', 'EVENT_PLAYER_UNIT_DAMAGED', 'EVENT_PLAYER_UNIT_DEATH', 'EVENT_PLAYER_UNIT_ATTACKED',
    'UNIT_TYPE_HERO', 'UNIT_TYPE_DEAD', 'UNIT_TYPE_STRUCTURE', 'PLAYER_NEUTRAL_PASSIVE', 'bj_MAX_PLAYERS',
    'bj_QUESTTYPE_OPT_DISCOVERED', 'bj_DEGTORAD', 'DAMAGE_TYPE_NORMAL', 'WEAPON_TYPE_WHOKNOWS',
    'UNIT_WEAPON_IF_ATTACK_ATTACK_TYPE', 'PLAYER_NEUTRAL_AGGRESSIVE', 'EVENT_PLAYER_HERO_LEVEL', 'PLAYER_STATE_RESOURCE_GOLD', 'Hi', 'EVENT_PLAYER_UNIT_DAMAGING', 'EVENT_PLAYER_UNIT_SELL', 'UNIT_IF_LEVEL',
    'EVENT_PLAYER_UNIT_PICKUP_ITEM', 'bj_UNIT_STATE_METHOD_RELATIVE', 'UNIT_IF_GOLD_BOUNTY_AWARDED_BASE', 'ATTACK_TYPE_HERO', 'MAP_CONTROL_USER', 'PLAYER_SLOT_STATE_PLAYING', 'bj_lastReplacedUnit',
    'DAMAGE_TYPE_UNIVERSAL', 'ATTACK_TYPE_NORMAL', 'UNIT_STATE_LIFE', 'UNIT_STATE_MANA', 'UNIT_STATE_MAX_LIFE', 'UNIT_STATE_MAX_MANA', 'ALLIANCE_PASSIVE',
    'EVENT_PLAYER_HERO_REVIVE_FINISH',
}

KEYWORDS = {
    'function', 'takes', 'returns', 'nothing', 'endfunction', 'globals', 'endglobals', 'local', 'set',
    'call', 'if', 'then', 'elseif', 'else', 'endif', 'loop', 'endloop', 'exitwhen', 'return', 'constant',
    'array', 'and', 'or', 'not', 'true', 'false', 'null', 'native', 'type', 'extends', 'debug',
}

TOKEN = re.compile(r"""\s*(?:
    (?P<str>"(?:[^"\\]|\\.)*")|
    (?P<raw>'[^']*')|
    (?P<num>\$[0-9A-Fa-f]+|0[xX][0-9A-Fa-f]+|\d+\.\d*|\.\d+|\d+)|
    (?P<id>[A-Za-z_][A-Za-z0-9_]*)|
    (?P<op>==|!=|<=|>=|[-+*/=<>()\[\],])
)""", re.X)


def _strip_comment(line):
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            j = i + 1
            while j < len(line) and line[j] != '"':
                j += 2 if line[j] == '\\' else 1
            out.append(line[i:j + 1])
            i = j + 1
            continue
        if c == "'":
            j = line.find("'", i + 1)
            j = len(line) - 1 if j < 0 else j
            out.append(line[i:j + 1])
            i = j + 1
            continue
        if line.startswith('//', i):
            break
        out.append(c)
        i += 1
    return ''.join(out)


def _tokens(line):
    toks = []
    pos = 0
    line = line.rstrip()
    while pos < len(line):
        m = TOKEN.match(line, pos)
        if not m or m.end() == pos:
            raise ValueError('cannot tokenize at %r' % line[pos:pos + 20])
        kind = m.lastgroup
        toks.append((kind, m.group(kind)))
        pos = m.end()
    return toks


class _Fn:
    def __init__(self, name, nargs, line):
        self.name, self.nargs, self.line = name, nargs, line


def check(source, known_functions, known_globals):
    errs = []
    funcs = {}            # our functions defined so far
    gvars = {}            # our globals: name -> is_array
    in_globals = False
    cur = None            # current function name
    lvars = {}
    seen_stmt = False
    stack = []

    def err(ln, msg):
        errs.append('line %d: %s' % (ln, msg))

    def var_known(name):
        return name in lvars or name in gvars or name in known_globals

    def is_array(name):
        if name in lvars:
            return lvars[name]
        return gvars.get(name)

    def check_expr(ln, toks):
        i = 0
        while i < len(toks):
            kind, val = toks[i]
            if kind != 'id' or val in KEYWORDS:
                i += 1
                continue
            prev = toks[i - 1][1] if i > 0 else None
            nxt = toks[i + 1][1] if i + 1 < len(toks) else None
            if prev == 'function':
                if val not in funcs:
                    err(ln, 'code reference to undefined (or later-defined) function %s' % val)
            elif nxt == '(':
                depth, j, commas, empty = 0, i + 1, 0, toks[i + 2][1] == ')' if i + 2 < len(toks) else True
                while j < len(toks):
                    t = toks[j][1]
                    if t in ('(', '['):
                        depth += 1
                    elif t in (')', ']'):
                        depth -= 1
                        if depth == 0:
                            break
                    elif t == ',' and depth == 1:
                        commas += 1
                    j += 1
                if depth != 0:
                    err(ln, 'unbalanced parentheses after %s' % val)
                nargs = 0 if empty else commas + 1
                if val in funcs:
                    want = funcs[val].nargs
                elif val in known_functions:
                    want = known_functions[val]
                else:
                    err(ln, 'unknown function %s' % val)
                    want = None
                if want is not None and want != nargs:
                    err(ln, '%s takes %d argument(s), got %d' % (val, want, nargs))
            elif val in funcs or val in known_functions:
                err(ln, 'function %s used without call parentheses' % val)
            elif not var_known(val):
                err(ln, 'undeclared variable %s' % val)
            else:
                arr = is_array(val)
                if arr is True and nxt != '[':
                    err(ln, 'array %s used without index' % val)
                if arr is False and nxt == '[':
                    err(ln, '%s is not an array' % val)
            i += 1

    for ln, raw in enumerate(source.splitlines(), 1):
        line = _strip_comment(raw).strip()
        if not line:
            continue
        try:
            toks = _tokens(line)
        except ValueError as e:
            err(ln, str(e))
            continue
        words = [v for _, v in toks]
        head = words[0]
        if head == 'globals':
            in_globals = True
            continue
        if head == 'endglobals':
            in_globals = False
            continue
        if in_globals:
            w = words[1:] if head == 'constant' else words
            arr = len(w) > 1 and w[1] == 'array'
            name = w[2] if arr else w[1]
            if name in gvars:
                err(ln, 'duplicate global %s' % name)
            if '=' in w:
                check_expr(ln, toks[words.index('=') + 1:])
            gvars[name] = arr
            continue
        if head in ('function', 'constant') and 'takes' in words:
            w = words[1:] if head == 'constant' else words
            name = w[1]
            if cur is not None:
                err(ln, 'function %s starts before endfunction of %s' % (name, cur))
            if name in funcs or name in known_functions:
                err(ln, 'duplicate function %s' % name)
            params = w[w.index('takes') + 1:w.index('returns')]
            lvars = {}
            nargs = 0
            if params != ['nothing']:
                p = [x for x in params if x != ',']
                for k in range(0, len(p), 2):
                    lvars[p[k + 1]] = False
                nargs = len(p) // 2
            cur = name
            funcs[name] = _Fn(name, nargs, ln)  # recursion allowed
            seen_stmt = False
            stack = []
            continue
        if head == 'endfunction':
            if stack:
                err(ln, 'endfunction with open %s (missing end%s)' % (stack[-1], stack[-1]))
            cur = None
            continue
        if cur is None:
            err(ln, 'statement outside function: %s' % line)
            continue
        if head == 'local':
            if seen_stmt:
                err(ln, 'local declared after statements')
            arr = words[2] == 'array'
            name = words[3] if arr else words[2]
            if '=' in words:
                check_expr(ln, toks[words.index('=') + 1:])
            lvars[name] = arr
            continue
        seen_stmt = True
        if head == 'set':
            name = words[1]
            if not var_known(name):
                err(ln, 'undeclared variable %s' % name)
            check_expr(ln, toks[1:])
        elif head == 'call':
            check_expr(ln, toks[1:])
        elif head == 'if':
            stack.append('if')
            check_expr(ln, toks[1:])
        elif head == 'elseif':
            if not stack or stack[-1] != 'if':
                err(ln, 'elseif without if')
            check_expr(ln, toks[1:])
        elif head == 'else':
            if not stack or stack[-1] != 'if':
                err(ln, 'else without if')
        elif head == 'endif':
            if not stack or stack[-1] != 'if':
                err(ln, 'endif without if')
            else:
                stack.pop()
        elif head == 'loop':
            stack.append('loop')
        elif head == 'endloop':
            if not stack or stack[-1] != 'loop':
                err(ln, 'endloop without loop')
            else:
                stack.pop()
        elif head == 'exitwhen':
            if 'loop' not in stack:
                err(ln, 'exitwhen outside loop')
            check_expr(ln, toks[1:])
        elif head == 'return':
            check_expr(ln, toks[1:])
        else:
            err(ln, 'unknown statement: %s' % line)
    if cur is not None:
        err(0, 'missing endfunction for %s' % cur)
    if in_globals:
        err(0, 'missing endglobals')
    return errs
