"""Read-only: v1.8 evolutions done by picking up an item (pickup trigger -> Mega_SafeReplace(GetManipulatingUnit(), X))
and whether the item is a type item that Type_OnSell / the v1.8 drop triggers keep from that Pokemon.

python -I analysis/item_evos.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import apply as A  # noqa: E402

script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
units = A.unit_data(A.BASE_MAP)
funcs = {m.group(1): m.group(2) for m in re.finditer(r'(?ms)^function (\w+) takes nothing returns \w+\n(.*?)\nendfunction',
                                                   script)}
type_item = dict(re.findall(r"set Type_Item\[(\d+)\] = '(\w{4})'", script))
type_word = dict(re.findall(r'set Type_Word\[(\d+)\] = "(\w+)"', script))
word_of = {type_item[i]: type_word[i] for i in type_item}
out = []
for trig, cond, act in re.findall(r"call TriggerAddCondition\((\w+),Condition\(function (\w+)\)\)\n"
                                  r"call TriggerAddAction\(\1,function (\w+)\)", script):
    items = re.findall(r"GetItemTypeId\(GetManipulatedItem\(\)\)=='(\w{4})'", funcs.get(cond, ''))
    if not items:
        continue
    body = funcs.get(act, '')
    for cf, new in re.findall(r"if\((\w+)\(\)\)then\n(?:[^\n]*\n){0,6}?call Mega_SafeReplace\(GetManipulatingUnit\(\),'(\w{4})'",
                              body):
        for ty in re.findall(r"GetUnitTypeId\(GetManipulatingUnit\(\)\)=='(\w{4})'", funcs.get(cf, '')):
            for it in items:
                out.append((ty, it, new))
for ty, it, new in out:
    fr = units.get(ty)
    nm = (fr.get('upro') if fr else ty)
    tn = (fr.get('unam') if fr else '')
    w = word_of.get(it)
    blocked = bool(w) and w not in (tn or '')
    print('%s %-12s %-22s + %s%s -> %s %s %s' % (ty, nm, tn, it, ' (%s type item)' % w if w else '', new,
                                                 (units.get(new).get('upro') if units.get(new) else ''),
                                                 'BLOCKED by type rule' if blocked else ''))
