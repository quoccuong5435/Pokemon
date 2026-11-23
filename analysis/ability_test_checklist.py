"""Write docs/ability-test-checklist.md: how to try every new / reworked Ability in game with -abtest.

Usage (from _PokemonArena2.0_work):  python -I analysis/ability_test_checklist.py
Source: analysis/ability_final.json (approved effects) + tools/v412/ability_rw.py (which ones run in the new code).
"""
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import ability_rw  # noqa: E402

HINTS = [
    (r'[Hh]ào quang|trong \d{3}', 'Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng.'),
    (r'cận chiến', 'Để quái cận chiến (melee) đánh mình vài lần.'),
    (r'[Hh]ạ gục|[Hh]ạ quái|[Bb]ị hạ', 'Hạ vài con quái (hoặc để bị hạ, với Aftermath).'),
    (r'[Mm]áu (xuống )?dưới|[Mm]áu trên', 'Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng.'),
    (r'mưa đá|bão cát|[Nn]ắng|[Tt]rời mưa|[Mm]ưa:', 'Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so).'),
    (r'[Tt]rúng chiêu|bị trúng|[Mm]ỗi chiêu trúng nó|chiêu trúng nó', 'Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác).'),
    (r'[Dd]ùng chiêu|[Rr]a chiêu|[Mm]ỗi lần dùng', 'Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu.'),
    (r'[Đđ]òn đánh|đánh thường', 'Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương.'),
    (r'khiên|[Mm]ỗi \d+ giây', 'Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu.'),
]


def hint(text):
    for pat, h in HINTS:
        if re.search(pat, text):
            return h
    return 'Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh.'


def main():
    with open(os.path.join(WORK, 'analysis', 'ability_final.json'), encoding='utf-8') as fh:
        final = json.load(fh)
    rows = [o for o in final['abilities'] if o['change'] != 'same']
    out = ['# Bảng thử ability trong game (v4.2x)', '',
           'Dùng sau khi Gemini build bản có `tools/v412/ability_rw.py`. Chưa ai chơi thử bản này.', '',
           '## Cách thử', '',
           '1. Tạo phòng, chọn một Pokemon bất kỳ (bạn phải là host).',
           '2. Chọn hero của mình, gõ `-abtest <tên ability tiếng Anh>`, ví dụ `-abtest Rough Skin`.',
           '   Game báo tên và mô tả ability vừa gán; nút thông tin ability (ô 3,1) cũng đổi theo.',
           '3. Làm theo cột "Cách thử", so với cột "Kết quả cần thấy", đánh dấu cột Đạt.',
           '4. Gõ `-abtest off` để trả lại ability gốc của Pokemon.', '',
           'Ghi chú:',
           '- Bậc chỉ số (stage) trong map tối đa ±4, nên các hiệu ứng cộng bậc (Moxie, Weak Armor, Motor Drive...) dừng ở ±4.',
           '- Speed Boost dùng tầng riêng (tối đa 6 tầng, mỗi tầng +6% tốc chạy và tốc đánh), không dùng bậc Speed.',
           '- Pressure: hồi chiêu của địch chậm 30% (cơ chế Pressure sẵn có của map chỉ có mức 20% hoặc 30%; bản duyệt ghi 25%).',
           '- Hidden Ability: mua Ability Patch (10.000 vàng) cho Pokemon rồi kiểm tra nút ability đổi sang Hidden Ability.', '',
           '| Đạt | Ability | Lệnh | Cách thử | Kết quả cần thấy |', '|---|---|---|---|---|']
    for o in sorted(rows, key=lambda o: o['name']):
        out.append('| [ ] | %s | `-abtest %s` | %s | %s |' % (o['name'], o['name'], hint(o['final']), o['final'].replace('|', '/')))
    out += ['', 'Ability giữ nguyên (không cần thử lại): ' + ', '.join(sorted(o['name'] for o in final['abilities'] if o['change'] == 'same')) + '.', '']
    path = os.path.join(WORK, 'docs', 'ability-test-checklist.md')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('wrote', path, len(rows), 'rows')


if __name__ == '__main__':
    main()
