"""One-off: gather the v3.4 / v3.5 docs into docs/v3.4/, fix their stale status lines, update the paths in code."""
import os
import subprocess

MOVES = [  # old -> new, tracked in git?
    ('docs/v3.4-ability-rework-proposal.md', 'docs/v3.4/1-ability.md', True),
    ('docs/v3.4-mega-form-wild-proposal.md', 'docs/v3.4/2-mega-form-quai-hoang.md', True),
    ('docs/v3.5-items-league-features-proposal.md', 'docs/v3.4/3-item-league-tinh-nang.md', True),
    ('docs/v3.4-move-icons.md', 'docs/v3.4/4-icon-chieu.md', True),
    ('docs/v3.4-move-damage.md', 'docs/v3.4/5-sat-thuong-chieu.md', False),
    ('docs/v3.4-move-effects-proposal.md', 'docs/v3.4/6-de-xuat-hieu-ung-chieu.md', False),
]
os.makedirs('docs/v3.4', exist_ok=True)
for old, new, tracked in MOVES:
    if os.path.exists(old):
        if tracked:
            subprocess.run(['git', 'mv', old, new], check=True)
        else:
            os.replace(old, new)
        print('moved', old, '->', new)


def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) >= 1, (path, a[:70])
        s = s.replace(a, b)
    open(path, 'w', encoding='utf-8').write(s)
    print('edited', path)


# paths in code, scripts and CLAUDE.md
ref = {old: new for old, new, _t in MOVES}
for path in ('tools/v34/abilities.py', 'tools/v34/content.py', 'tools/v34/extras.py', 'tools/v34/jass/extra.j',
             'tools/v34/jass/globals.j', 'tools/v34/move_icons.py', 'tools/v34/apply.py', 'analysis/effects_plan.py',
             'analysis/move_damage_doc.py', 'CLAUDE.md'):
    s = open(path, encoding='utf-8').read()
    t = s
    for old, new in ref.items():
        t = t.replace(old, new)
    t = t.replace("os.path.join(WORK, 'docs', 'v3.4-move-icons.md')", "os.path.join(WORK, 'docs', 'v3.4', '4-icon-chieu.md')")
    t = t.replace("os.path.join(WORK, 'docs', 'v3.4-move-effects-proposal.md')",
                  "os.path.join(WORK, 'docs', 'v3.4', '6-de-xuat-hieu-ung-chieu.md')")
    t = t.replace("os.path.join(WORK, 'docs', 'v3.4-move-damage.md')", "os.path.join(WORK, 'docs', 'v3.4', '5-sat-thuong-chieu.md')")
    if t != s:
        open(path, 'w', encoding='utf-8').write(t)
        print('paths updated in', path)

# stale facts in the generators
edit('analysis/move_damage_doc.py', [('- quái elite (máu x2);', '- quái elite (máu x1,6, sát thương x1,6);'),
                                     ('`docs/v3.4/4-icon-chieu.md`', '`4-icon-chieu.md`')])
edit('analysis/effects_plan.py', [('# Đề xuất: hiệu ứng move mới từ PKLegends v3.2 (chờ duyệt)',
                                   '# 6. Đề xuất: hiệu ứng move mới từ PKLegends v3.2 (chờ duyệt)')])

# status lines of the three hand-written docs
edit('docs/v3.4/1-ability.md', [
    ('# Pokemon Arena v3.4: đề xuất làm lại Ability (để duyệt)', '# 1. Ability: làm lại 68 Ability, thêm Ability mới'),
    ('Số liệu lấy từ file `Pokemon Arena v3.3.3.w3x` (ngày 07/11/2026). Chưa sửa gì, chưa build.',
     'Số liệu gốc lấy từ `Pokemon Arena v3.3.3.w3x`. **Đã duyệt và đã có trong v3.4.0** (build 07/11/2026). '
     'Sau đó thêm Ability 70–73 (Strong Jaw, Solar Power, Skill Link, Zen Mode), xem `2-mega-form-quai-hoang.md`; '
     'tổng cộng 73 Ability. Bảng dưới là bản đề xuất đã duyệt (cột "Hiện tại" = v3.3.3).'),
    ('Đã duyệt và đã viết code cho v3.4.0 (`tools/v34/`, script `v34/war3map.j`, pjass 0 lỗi). **Chưa build, chưa chơi thử.**',
     'Đã có trong v3.4.0 (`tools/v34/`). Các lưu ý dưới đây ghi lúc làm v3.4.0; những lỗi tìm ra khi chơi thử đã sửa ở '
     '3.4.1 / 3.4.2 (xem README.md).'),
    ('- Giết Pokémon gym (giờ là hero) được exp như giết hero; phần thưởng +500 exp +1 gỗ của v1.8 không áp dụng cho chúng.',
     '- Giết Pokémon gym (giờ là hero) được exp như giết hero; phần thưởng +500 exp +1 gỗ của v1.8 không áp dụng cho chúng. '
     '(Lên cấp tiến hóa giữa trận từng làm gym reset: đã sửa ở 3.4.1.)'),
    ('## Các thay đổi khác đã chốt (đã viết code, chờ bạn bảo build)', '## Các thay đổi khác làm cùng đợt (có trong v3.4.0)'),
])
edit('docs/v3.4/2-mega-form-quai-hoang.md', [
    ('# v3.4.0 (thêm): Mega, form từ PKLegends 3.2 và quái hoang mới — đề xuất để duyệt',
     '# 2. Mega, form từ PKLegends 3.2 và quái hoang mới'),
    ('Ngày 2026-11-07. Gộp vào v3.4.0 vì bản này chưa build. Chưa sửa code: chờ bạn duyệt.',
     'Ngày 2026-11-07. **Đã duyệt và đã có trong v3.4.0.** Bảng dưới là bản đề xuất đã duyệt.'),
    ('rơi theo luật hiện tại (chỉ elite, 10%)', 'rơi theo luật hiện tại (chỉ elite, 20%)'),
    ('## Trạng thái (2026-11-07): đã duyệt và đã code, chưa build, chưa chơi thử',
     '## Trạng thái: đã có trong v3.4.0 (build 2026-11-07)'),
])
edit('docs/v3.4/3-item-league-tinh-nang.md', [
    ('# Đề xuất: item mới, Elite Four, Shiny, thời tiết, đá tiến hóa, Mega cho elite/huyền thoại — để duyệt',
     '# 3. Item mới, Elite Four, Shiny, thời tiết, đá tiến hóa, Mega cho elite / huyền thoại'),
    ('`docs/v3.4-move-icons.md`', '`4-icon-chieu.md`'),
])
s = open('docs/v3.4/3-item-league-tinh-nang.md', encoding='utf-8').read()
first = s.split('\n')[2]
s = s.replace(first, 'Ngày 2026-11-07. Lúc đầu đề xuất làm v3.5.0; bạn duyệt và cho **gộp vào v3.4.0** (đã build). '
              'Khắc hệ đã có từ trước nên không nằm ở đây. Bảng dưới là bản đề xuất đã duyệt; phần "Trạng thái" cuối file '
              'ghi những gì đã làm khác đi. Amulet Coin không chạy ở 3.4.0, đã sửa ở 3.4.1.', 1)
open('docs/v3.4/3-item-league-tinh-nang.md', 'w', encoding='utf-8').write(s)
print('done')
