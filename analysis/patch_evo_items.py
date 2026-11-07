"""One-off (v3.4.2): a Pokemon may buy a type item of another type when it evolves with it (Onix / Scyther + Metal
Coat). extras.py writes Mega_HT key 92 on the unit type = that item; apply.py patches Type_OnSell."""


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


edit('tools/v34/extras.py', [(
    """    # ---------------- Elite Four and Champion""",
    """    # ---------------- v3.4.2: evolution items that are type items of another type (Onix / Scyther + Metal Coat):
    # Type_OnSell lets that Pokemon buy it anyway (Mega_HT key 92 on its type = the item)
    type_item = dict(re.findall(r"set Type_Item\\[(\\d+)\\] = '(\\w{4})'", script))
    type_word = dict(re.findall(r'set Type_Word\\[(\\d+)\\] = "(\\w+)"', script))
    word_of = {type_item[i]: type_word[i] for i in type_item}
    funcs = {m.group(1): m.group(2) for m in re.finditer(
        r'(?ms)^function (\\w+) takes nothing returns \\w+\\n(.*?)\\nendfunction', script)}
    allowed = []
    for _t, cond, act in re.findall(r"call TriggerAddCondition\\((\\w+),Condition\\(function (\\w+)\\)\\)\\n"
                                    r"call TriggerAddAction\\(\\1,function (\\w+)\\)", script):
        its = [i for i in re.findall(r"GetItemTypeId\\(GetManipulatedItem\\(\\)\\)=='(\\w{4})'", funcs.get(cond, ''))
               if i in word_of]
        if not its:
            continue
        for cf, _new in re.findall(r"if\\((\\w+)\\(\\)\\)then\\n(?:[^\\n]*\\n){0,6}?call Mega_SafeReplace\\(GetManipulatingUnit\\(\\),'(\\w{4})'",
                                   funcs.get(act, '')):
            for ty in re.findall(r"GetUnitTypeId\\(GetManipulatingUnit\\(\\)\\)=='(\\w{4})'", funcs.get(cf, '')):
                for it in its:
                    if word_of[it] not in (allu.get(ty).get('unam') or '' if allu.get(ty) else ''):
                        c.data.append("    call SaveInteger(Mega_HT, '%s', 92, '%s')" % (ty, it))
                        allowed.append('%s+%s' % ((allu.get(ty).get('upro') if allu.get(ty) else ty), it))
    c.report.append('evolution items of another type allowed: %s' % ', '.join(allowed))

    # ---------------- Elite Four and Champion""")])

edit('tools/v34/apply.py', [(
    """GYM_HEADER = """,
    """TYPE_SELL_OLD = '            if not Type_Has(GetUnitName(b), Type_Word[i]) then\\n'
TYPE_SELL_NEW = ('            if not Type_Has(GetUnitName(b), Type_Word[i]) and LoadInteger(Mega_HT, GetUnitTypeId(b), 92) != id then'
                 '  // v3.4.2: unless it evolves with it\\n')
GYM_HEADER = """), (
    """    for o, n in ((SAFE_OLD, SAFE_NEW),""",
    """    script = replace_once(script, TYPE_SELL_OLD, TYPE_SELL_NEW)
    for o, n in ((SAFE_OLD, SAFE_NEW),""")])
