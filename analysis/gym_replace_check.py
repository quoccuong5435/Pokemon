"""Read-only: can a gym Pokemon (playable hero type, spawned at level lv in the form Gym_FormAt gives) be replaced
right after it spawns by a v1.8 level-up trigger (Mega_SafeReplace(GetTriggerUnit(), ...))? That would leave the gym
pointing at a removed unit (Gym_Cur) and stop the team.

python -I analysis/gym_replace_check.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v34'))
import apply as A  # noqa: E402

script = open(os.path.join(WORK, 'v34', 'war3map.j'), encoding='utf-8').read()
# every hero-level trigger: its condition functions -> (types, level threshold), its actions -> replacements
funcs = {m.group(1): m.group(2) for m in re.finditer(r'(?ms)^function (\w+) takes nothing returns \w+\n(.*?)\nendfunction',
                                                   script)}
level_trigs = re.findall(r'call TriggerRegisterAnyUnitEventBJ\((\w+),EVENT_PLAYER_HERO_LEVEL\)\n'
                         r'(?:call TriggerAddCondition\(\1,Condition\(function (\w+)\)\)\n)?'
                         r'call TriggerAddAction\(\1,function (\w+)\)', script)
print('hero level triggers:', len(level_trigs))
rules = []   # (from type, to type, min level)
for _t, cond, act in level_trigs:
    cbody = funcs.get(cond, '') if cond else ''
    lv = re.search(r'Get(?:Unit|Hero)Level\((?:GetLevelingUnit|GetTriggerUnit)\(\)\)\s*(>=|>)\s*(\d+)', cbody)
    body = funcs.get(act, '')
    for cf, new in re.findall(r"if\((\w+)\(\)\)then\n(?:[^\n]*\n){0,6}?call Mega_SafeReplace\((?:GetTriggerUnit|GetLevelingUnit)\(\),'(\w{4})'",
                              body):
        cb = funcs.get(cf, '')
        tys = re.findall(r"GetUnitTypeId\((?:GetLevelingUnit|GetTriggerUnit)\(\)\)=='(\w{4})'", cb)
        lv2 = re.search(r'Get(?:Unit|Hero)Level\((?:GetLevelingUnit|GetTriggerUnit)\(\)\)\s*(>=|>)\s*(\d+)', cb) or lv
        if lv2:
            mn = int(lv2.group(2)) + (0 if lv2.group(1) == '>=' else 1)
        else:
            mn = 1
        for ty in tys:
            rules.append((ty, new, mn))
print('level replacements found:', len(rules))
# gym evolution data as generated (Ab_HT 299 / 300 + 2k / 301 + 2k)
evo = {}
for a, k, b in re.findall(r"call SaveInteger\(Ab_HT, '(\w{4})', (\d+), '(\w{4})'\)", script):
    if int(k) >= 300 and int(k) % 2 == 0:
        evo.setdefault(a, {})[int(k)] = b
lvl = {}
for a, k, v in re.findall(r"call SaveInteger\(Ab_HT, '(\w{4})', (\d+), (\d+)\)", script):
    if int(k) >= 301 and int(k) % 2 == 1 and int(k) < 320:
        lvl.setdefault(a, {})[int(k)] = int(v)
stale = []
for ty, new, mn in rules:
    # the gym puts `ty` at level lv only if no gym evolution of ty is reached by lv: find levels where ty stays ty
    gym_lv = min([lvl.get(ty, {}).get(k + 1, 999) for k in evo.get(ty, {})] or [999])
    if mn < gym_lv:
        stale.append((ty, new, mn, gym_lv))
units = A.unit_data(A.BASE_MAP)
nm = lambda u: (units[u].get('upro') if u in units else u)  # noqa: E731
print('types a gym can spawn at a level where a v1.8 trigger then replaces them: %d' % len(stale))
for ty, new, mn, gl in stale[:40]:
    print('  %s %s -> %s %s: trigger from lv %d, gym evolves it only at lv %s' % (ty, nm(ty), new, nm(new), mn, gl))
