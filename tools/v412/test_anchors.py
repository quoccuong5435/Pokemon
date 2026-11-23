import sys, os
sys.path.insert(0, r'c:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\_PokemonArena2.0_work\tools')
import mpq

base_map = r'c:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\Pokemon Arena v4.1.2-ver2b.w3x'
m = mpq.MPQ(base_map)
s = m.read('scripts\\war3map.j').decode('latin-1').replace('\r\r\n', '\r\n').replace('\r\n', '\n')

train_show = 'local integer statCost = 2000 + PAX_Up_StatLv[pid] * 500\n    local integer vitCost = 2000 + PAX_Up_VitLv[pid] * 500'
print('train_show in s:', train_show in s)
print('train_click count for 2000:', s.count('set cost = 2000 + PAX_Up_'))

stones = ["'I00K'", "'I00L'", "'I00M'", "'I00N'", "'I00O'"]
total_stones = sum(s.count(f'call CreateItemLoc({st},GetUnitLoc(GetTriggerUnit()))') for st in stones)
print('total stone drops found:', total_stones)
