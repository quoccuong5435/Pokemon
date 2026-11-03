"""Re-insert line breaks into an optimizer-squashed war3map.j (for reading only)."""
import re
import sys

KW = ['function', 'endfunction', 'globals', 'endglobals', 'call', 'set', 'local', 'if', 'elseif',
      'else', 'endif', 'loop', 'endloop', 'exitwhen', 'return', 'constant', 'native', 'type']
# keyword glued to previous token: split before it when preceded by ) " or alnum end of a statement
pat = re.compile(r'(?<=[)\"a-zA-Z0-9_\]])(?=(?:' + '|'.join(KW) + r')\b)')


def split_code(code):
    out = []
    i = 0
    buf = ''
    while i < len(code):
        c = code[i]
        if c == '"':
            j = i + 1
            while j < len(code) and code[j] != '"':
                if code[j] == '\\':
                    j += 1
                j += 1
            buf += code[i:j + 1]
            i = j + 1
            continue
        if c == "'":
            j = code.find("'", i + 1)
            buf += code[i:j + 1]
            i = j + 1
            continue
        buf += c
        i += 1
    return buf


def main(src, dst):
    txt = open(src, encoding='latin-1').read()
    # protect strings
    strings = []

    def keep(m):
        strings.append(m.group(0))
        return '\x00%d\x00' % (len(strings) - 1)

    t = re.sub(r'"(?:[^"\\]|\\.)*"', keep, txt, flags=re.S)
    t = pat.sub('\n', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: strings[int(m.group(1))], t)
    open(dst, 'w', encoding='latin-1').write(t)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
