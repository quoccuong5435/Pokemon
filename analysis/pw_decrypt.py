"""Read-only: decode the RxL(...) strings of the protected "Pokemon World V1.71.w3x" script.

The map's chE(): every printable character (32..126) is shifted by key[k] (k cycles 0..5 over the shifted
characters only) and wrapped into 32..126; other characters are kept.

    python -I analysis/pw_decrypt.py out/pkworld/war3map.j out/pkworld/strings.json
"""
import json
import re
import sys

KEY = [59, 42, 54, 27, 41, 48]


def unescape(s):
    return re.sub(r'\\(.)', lambda m: {'n': '\n', 't': '\t', 'r': '\r'}.get(m.group(1), m.group(1)), s)


def decode(s, key=KEY):
    out, k = [], 0
    for ch in s:
        c = ord(ch)
        if 32 <= c < 127:
            c += key[k]
            if c < 32:
                c += 95
            elif c > 126:
                c -= 95
            out.append(chr(c))
            k = (k + 1) % 6
        else:
            out.append(ch)
    return ''.join(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    text = open(src, encoding='latin-1').read()
    found = {}
    for lit in re.findall(r'RxL\("((?:[^"\\]|\\.)*)"\)', text):
        found[lit] = decode(unescape(lit))
    json.dump(found, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(found), 'strings')
    for k in list(found)[:15]:
        print(repr(k), '->', repr(found[k]))


if __name__ == '__main__':
    main()
