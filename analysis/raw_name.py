import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[1])
for n in a.listfile():
    if n.startswith('Units\\') and n.endswith(('Func.txt', 'Strings.txt')):
        t = a.read(n)
        for key in sys.argv[2:]:
            i = t.find(('[%s]' % key).encode())
            if i >= 0:
                print(n, key, t[i:i + 420].replace(b'\r', b''))
