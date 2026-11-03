"""One-off fix: repair the return line of gen_pick_init (newline escape got expanded)."""
import io

p = 'tools/inject.py'
s = io.open(p, encoding='utf-8', newline='').read()
bad = "    return '\n'.join(lines) + '\n'\n\n\ndef gen_data_init"
good = "    return '\\n'.join(lines) + '\\n'\n\n\ndef gen_data_init"
assert s.count(bad) == 1, s.count(bad)
s = s.replace(bad, good)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('fixed')
