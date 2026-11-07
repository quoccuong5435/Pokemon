"""Make v34/war3map_v333.j (the base of apply.py) from "Pokemon Arena v3.3.3.w3x": its war3map.j with LF line breaks.
The v1.8 part of the script uses bare CR as line breaks: turn CRLF and CR into LF (never just delete CR).
It holds the v1.8 author's code, so it is not in git (.gitignore): run this after a fresh clone.

    python -I tools/v34/extract_base.py [--check]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mpq  # noqa: E402
import apply  # noqa: E402


def base_text(map_path=apply.BASE_MAP):
    a = mpq.MPQ(map_path)
    name = 'scripts\\war3map.j' if a.has('scripts\\war3map.j') else 'war3map.j'
    text = a.read(name).decode('utf-8', 'replace')
    return text.replace('\r\n', '\n').replace('\r', '\n')


def main():
    text = base_text()
    if '--check' in sys.argv:
        same = os.path.exists(apply.BASE_SCRIPT) and open(apply.BASE_SCRIPT, encoding='utf-8').read() == text
        print('v34/war3map_v333.j matches the map' if same else 'v34/war3map_v333.j DIFFERS from the map')
        return
    os.makedirs(os.path.dirname(apply.BASE_SCRIPT), exist_ok=True)
    with open(apply.BASE_SCRIPT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote', apply.BASE_SCRIPT)


if __name__ == '__main__':
    main()
