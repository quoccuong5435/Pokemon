"""Read-only: docs/v3.4/5-sat-thuong-chieu.md = every learned move (game skill it is made from, effect model, base damage and
damage at several main-stat values) + the moves each playable Pokemon learns.

python -I analysis/move_damage_doc.py ["../Pokemon Arena v3.4.1.w3x"]
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402

MAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x')
BASE_NAME = {'AHtb': 'Storm Bolt', 'AEsh': 'Shadow Strike', 'AUfn': 'Frost Nova', 'AUcs': 'Carrion Swarm',
             'AOsh': 'Shockwave', 'AHtc': 'Thunder Clap', 'AOws': 'War Stomp', 'ANbf': 'Breath of Fire',
             'AEer': 'Entangling Roots', 'AUim': 'Impale', 'AHbz': 'Blizzard'}
STATS = (100, 200, 400, 600)   # main stat (max of STR / INT): damage = base x stat / 50 (x0.1 .. x15)
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

a = mpq.MPQ(MAP)
script = a.read('scripts\\war3map.j' if a.has('scripts\\war3map.j') else 'war3map.j').decode('utf-8', 'replace')
abil = slk.Slk(a.read('Units\\AbilityData.slk').decode('latin-1'))
code_x = abil.name_to_x['code']
strings = a.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')


def arr(name, kind=r'(-?\d+)'):
    return dict((int(i), v) for i, v in re.findall(r'set %s\[(\d+)\] = %s' % (name, kind), script))


label, text = arr('Mv_Label', r'"([^"]*)"'), arr('Mv_Text', r'"([^"]*)"')
d1, d2 = arr('Mv_D1'), arr('Mv_D2')


def section(aid):
    m = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % aid, strings, re.S)
    return dict(re.findall(r'(?m)^(\w+)=([^\r\n]*)', m.group(1))) if m else {}


def model(path):
    return re.sub(r'\.md[lx]$', '', path.replace('/', '\\').split('\\')[-1], flags=re.I) if path else ''


def clean(t):
    t = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', t).replace('|n', ' ')
    return t.replace('|', '/')


rows = []
for m in sorted(label):
    lab = label[m]
    mm = re.match(r'(.*?) \((\w+), power (\d+)\)', lab)
    name, ty, pw = (mm.group(1), mm.group(2), int(mm.group(3))) if mm else (lab, '', 0)
    aid = 'AV' + B36[m // 36] + B36[m % 36]
    row = abil.find(aid) or {}
    code = row.get(code_x, '').strip('"')
    sec = section(aid)
    fx = model(sec.get('Missileart')) or model(sec.get('Effectart')) or model(sec.get('Targetart')) or \
        model(sec.get('Casterart')) or '(effect of %s)' % BASE_NAME.get(code, code)
    desc = clean(text.get(m, ''))
    phys = 'Vật lý' if 'Physical move' in text.get(m, '') else 'Đặc biệt'
    desc = re.sub(r'\s*Physical move:.*|\s*Special move:.*', '', desc)
    b1, b2 = int(d1.get(m, 0)), int(d2.get(m, 0))
    per_sec = 'per second' in desc or 'every few seconds' in desc
    shown = desc.replace('@1', str(b1)).replace('@2', str(b2))
    rows.append((m, name, ty, phys, pw, BASE_NAME.get(code, code), fx, shown, b1, b2, per_sec))

lines = ['# 5. Sát thương của 319 move học được (skill gốc, hiệu ứng, số liệu từ v3.4.1)', '',
         '## Nguồn của chiêu',
         '- **Dữ liệu chiêu** (tên, hệ, Power, vật lý/đặc biệt, Pokémon nào học được ở level nào): PokeAPI '
         '(`tools/learnsets.json`, làm từ v3.1 bằng `tools/learn_data.py`).',
         '- **Cách chiêu chạy**: mỗi move là một skill có sẵn của Warcraft III, chọn theo hình dạng chiêu và Power '
         '(11 loại: Storm Bolt, Shadow Strike, Frost Nova, Carrion Swarm, Shockwave, Thunder Clap, War Stomp, '
         'Breath of Fire, Entangling Roots, Impale, Blizzard). Sát thương gốc theo Power (`tools/poke_data.py`, TEMPLATES).',
         '- **Hiệu ứng hình ảnh**: model có sẵn của game. Đạn bay đổi theo hệ của chiêu (`ELEMENT_ART`), phần còn lại '
         'là hiệu ứng của skill gốc. Icon từ v3.4: icon có sẵn khớp tên chiêu (`4-icon-chieu.md`).', '',
         '## Sát thương ra sao',
         '1. **Sát thương gốc** = cột "Gốc" (D1, D2) trong bảng dưới.',
         '2. **× chỉ số chính / 50** (chỉ số chính = STR hoặc INT, lấy cái lớn hơn; từ x0,1 đến x15). Tooltip trong game '
         'hiện đúng số này. Ví dụ chỉ số 600: x12, nên chiêu gốc 100 hiện 1200.',
         '3. **× khắc hệ**: x2 khi khắc, x0,5 khi bị kháng, x0,25 khi miễn nhiễm (có chữ "Super effective!" / '
         '"Not very effective...").',
         '4. **× Ability**:',
         '   - của người đánh: Adaptability, Technician, Blaze…;',
         '   - của mục tiêu: Thick Fat x0,5 với Fire/Ice; Multiscale x0,6 khi trên 80% máu; Levitate miễn Ground; '
         'Water/Volt Absorb hút chiêu; Magic Bounce chặn 20%;',
         '   - **Sturdy / Sand Force**: một đòn lẽ ra hạ gục chỉ đưa mục tiêu về 15% máu, 60 giây một lần '
         '(Geodude, Onix, Steelix…).',
         '5. **× thời tiết, item, Champion Aura** (Life Orb, Choice Specs, Assault Vest…).',
         '6. **Giáp không giảm sát thương chiêu.** Bảng hệ số của map cho skill gây 100% lên mọi loại giáp, kể cả hero. '
         'Con số **vàng nổi lên** khi trúng là sát thương thật cuối cùng.', '',
         'Vì vậy tooltip 1200 mà không hạ được quái 1000 máu thường là do một trong các trường hợp:',
         '- bị kháng hệ (x0,5 → 600);',
         '- Ability của mục tiêu (Sturdy, Multiscale, Thick Fat);',
         '- quái elite (máu x1,6, sát thương x1,6);',
         '- chiêu gây sát thương theo giây (cột "Theo giây": số trong tooltip là mỗi giây, không phải một lần).', '',
         '| # | Move | Hệ | Loại | Power | Skill gốc | Hiệu ứng (model) | Gốc D1 / D2 | Theo giây | '
         + ' | '.join('x%s (chỉ số %d)' % (('%g' % (s / 50.0)).replace('.', ','), s) for s in STATS) + ' | Mô tả |',
         '|' + '---|' * (10 + len(STATS))]
for m, name, ty, phys, pw, base, fx, shown, b1, b2, per_sec in rows:
    scaled = ['%d / %d' % (b1 * s // 50, b2 * s // 50) if b2 else '%d' % (b1 * s // 50) for s in STATS]
    lines.append('| %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s |' % (
        m, name, ty, phys, pw, base, fx, ('%d / %d' % (b1, b2)) if b2 else str(b1), 'có' if per_sec else '',
        ' | '.join(scaled), shown))

# moves of each playable Pokemon (Ab_HT on the unit type: 99 = number, 100 + 2k = move, 101 + 2k = level)
units = {o.id: o for o in objdata.ObjFile(a.read('war3map.w3u')).custom}
lines += ['', '## Move của từng Pokémon (level học được)', '',
          '| Pokémon | Hệ | Move (level) |', '|---|---|---|']
learn = {}
for uid, k, v in re.findall(r"call SaveInteger\(Ab_HT, '(\w{4})', (\d+), (\d+)\)", script):
    k = int(k)
    if uid[0].isupper() and 100 <= k < 199:
        learn.setdefault(uid, {})[k] = int(v)
seen = set()
for uid in sorted(learn, key=lambda u: (units[u].get('upro') or u) if u in units else u):
    o = units.get(uid)
    if not o:
        continue
    pro = (o.get('upro') or uid).split(',')[0].strip()
    if pro in seen:
        continue
    seen.add(pro)
    d = learn[uid]
    pairs = []
    for k in range(100, 199, 2):
        if k in d and k + 1 in d:
            mv = d[k]
            nm = re.sub(r' \(.*', '', label.get(mv, str(mv)))
            pairs.append('%s (%d)' % (nm, d[k + 1]))
    ty = (o.get('unam') or '').replace(' Pokemon', '').replace('&', '/')
    lines.append('| %s | %s | %s |' % (pro, ty, ', '.join(pairs)))
out = os.path.join(WORK, 'docs', 'v3.4', '5-sat-thuong-chieu.md')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote', out, '-', len(rows), 'moves,', len(seen), 'Pokemon')
