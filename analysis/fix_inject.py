"""One-off fix: repair the broken return line of gen_pick_init and wire the generator into gen_data_init."""
import io

p = 'tools/inject.py'
s = io.open(p, encoding='utf-8', newline='').read()
bad = "    return '\n'.join(lines) + '\n'\n\n\ndef gen_data_init"
good = "    return '\\n'.join(lines) + '\\n'\n\n\ndef gen_data_init"
assert s.count(bad) == 1, s.count(bad)
s = s.replace(bad, good)
old = "             gen_mv_init(moves).rstrip('\\n'),\n"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "             gen_mv_init(moves).rstrip('\\n'), gen_pick_init(evo is not None).rstrip('\\n'),\n")
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fixed')
