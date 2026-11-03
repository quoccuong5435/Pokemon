"""Find identifiers of tools/jass/mega.j that clash with globals/functions of the v1.8 map script (JASS forbids it)."""
import re
import sys

sys.path.insert(0, 'tools')
import jasscheck  # noqa: E402

TYPES = ('integer', 'real', 'string', 'boolean', 'handle', 'code', 'unit', 'player', 'group', 'timer', 'trigger', 'item',
         'effect', 'hashtable', 'location', 'rect', 'region', 'force', 'sound', 'lightning', 'texttag', 'quest',
         'questitem', 'multiboard', 'leaderboard', 'dialog', 'button', 'widget', 'destructable', 'ability', 'timerdialog',
         'unitpool', 'itempool', 'camerasetup', 'gamecache', 'trackable', 'fogmodifier', 'image', 'ubersplat', 'event',
         'boolexpr', 'conditionfunc', 'filterfunc', 'triggercondition', 'triggeraction', 'agent', 'mapcontrol', 'race',
         'alliancetype', 'damagetype', 'attacktype', 'weapontype', 'unitstate', 'playerstate')
KEYWORDS = jasscheck.KEYWORDS | set(TYPES) | {'null', 'true', 'false', 'not', 'and', 'or', 'array', 'native', 'type',
                                              'extends', 'constant', 'takes', 'returns', 'nothing'}


def norm(path):
    return open(path, encoding='latin-1').read().replace('\r\n', '\n').replace('\r', '\n')


def declared(text):
    """(globals, functions, locals-and-params) of a JASS text."""
    globs, funcs, locs = {}, {}, {}
    in_globals = False
    cur = None
    for n, line in enumerate(text.split('\n'), 1):
        s = line.strip()
        if s == 'globals':
            in_globals = True
            continue
        if s == 'endglobals':
            in_globals = False
            continue
        m = re.match(r'function\s+(\w+)\s+takes\s+(.*?)\s+returns', s)
        if m:
            cur = m.group(1)
            funcs[cur] = n
            if m.group(2) != 'nothing':
                for part in m.group(2).split(','):
                    bits = part.split()
                    if len(bits) == 2:
                        locs.setdefault(bits[1], (cur, n))
            continue
        if in_globals:
            m = re.match(r'(?:constant\s+)?(\w+)\s+(?:array\s+)?(\w+)\s*(?:=.*)?$', s)
            if m and m.group(1) in TYPES:
                globs[m.group(2)] = n
        else:
            m = re.match(r'local\s+(\w+)\s+(?:array\s+)?(\w+)', s)
            if m:
                locs.setdefault(m.group(2), (cur, n))
    return globs, funcs, locs


old = norm(sys.argv[1])
new = norm('tools/jass/mega.j')
og, of, ol = declared(old)
ng, nf, nl = declared(new)
print('v1.8 globals', len(og), 'functions', len(of), '| mega.j globals', len(ng), 'functions', len(nf), 'locals/params', len(nl))
old_names = set(og) | set(of)
for what, d in (('global', ng), ('function', nf)):
    for name, line in d.items():
        if name in old_names:
            print('CLASH', what, name, 'mega.j line', line, '(v1.8 global line %s / function line %s)' % (og.get(name), of.get(name)))
for name, (fn, line) in sorted(nl.items()):
    if name in old_names:
        print('CLASH local/param', name, 'in', fn, 'line', line, '| v1.8 global' if name in og else '| v1.8 function')
    if name in ng or name in nf:
        print('SELF-CLASH local/param', name, 'in', fn, 'line', line, '| also mega.j', 'global' if name in ng else 'function')
    if name in KEYWORDS or name in jasscheck.NATIVES:
        print('RESERVED/NATIVE name used as local', name, 'in', fn, 'line', line)
for name, line in list(ng.items()) + list(nf.items()):
    if name in KEYWORDS or name in jasscheck.NATIVES:
        print('RESERVED/NATIVE name declared', name, 'line', line)
