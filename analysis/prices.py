import sys
sys.path.insert(0, sys.argv[1])
import slk
s = slk.Slk(open(sys.argv[2], encoding='latin-1').read())
names = {}
cur = None
for line in open(sys.argv[3], encoding='utf-8', errors='replace'):
    line = line.strip()
    if line.startswith('[') and line.endswith(']'):
        cur = line[1:-1]
    elif line.startswith('Name=') and cur:
        names[cur] = line[5:]
for iid in sys.argv[4].split(','):
    r = s.find(iid)
    print(iid, names.get(iid), 'gold=', s.get(r, 'goldcost') if r else None, 'class=', s.get(r, 'class') if r else None, 'abil=', s.get(r,'abilList') if r else None)
