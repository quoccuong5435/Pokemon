"""Writes docs/v3.4/10-danh-sach-item.md from the item table of extras.py (ITEMS, SHOPS), so the list is always the
same as the map. Edit the item in extras.py, run this script, review the markdown file.

python -I tools/v34/items_list.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
import extras  # noqa: E402

OUT = os.path.join(WORK, 'docs', 'v3.4', '10-danh-sach-item.md')
KIND = {'battle': 'Trận đấu', 'util': 'Tiện ích', 'berry': 'Berry', 'rope': 'Dịch chuyển', 'stone': 'Đá tiến hóa'}


def shop_of(index):
    for sid, name, slots in extras.SHOPS:
        if index in slots:
            return name
    return 'Không bán (nhận từ gym / quái)'


def main():
    lines = ['# 10. Danh sách item (v3.4)', '',
             'Tự động tạo từ `tools/v34/extras.py` bằng `tools/v34/items_list.py`. Sửa item trong `extras.py`, chạy lại script.',
             '', '| # | Tên | ID | Giá | Loại | Bán ở | Công dụng |', '|---|---|---|---|---|---|---|']
    for k, (iid, name, price, kind, _icon, text) in enumerate(extras.ITEMS):
        lines.append('| %d | %s | %s | %d | %s | %s | %s |' % (
            k, name, iid, price, KIND.get(kind, kind), shop_of(k), text.replace('|', '/')))
    lines += ['', 'Số item: %d. Tổng giá trị: %d vàng.' % (len(extras.ITEMS), sum(i[2] for i in extras.ITEMS))]
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', OUT, len(extras.ITEMS), 'items')


if __name__ == '__main__':
    main()
