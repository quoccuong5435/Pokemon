# 12. Đề xuất: thêm item mới cho đa dạng chiến thuật (chờ duyệt)

Trạng thái: **chưa sửa code.** Mỗi item mới cần thêm hiệu ứng trong JASS, nên cần bạn duyệt danh sách trước.

Danh sách hiện có 21 item (xem [10-danh-sach-item.md](10-danh-sach-item.md)). Các item mới đề xuất dưới đây chọn theo hướng chưa có: hồi máu theo sát thương, né đòn, đánh nhanh, và phản đòn theo hệ.

## 1. Item mới đề xuất

| # | Tên | Giá | Loại | Công dụng | Hook cần dùng |
|---|---|---|---|---|---|
| 1 | Shell Bell | 3000 | Trận đấu | Hồi 10% sát thương đã gây ra cho người giữ. | Sát thương gây ra (`Ext_AfterHit`, đã có) |
| 2 | Bright Powder | 3000 | Trận đấu | Đòn đánh của địch có 10% cơ hội trượt. | Sát thương nhận (`Ext_AfterHit`, đã có) |
| 3 | Quick Claw | 3500 | Trận đấu | Mỗi đòn đánh có 15% cơ hội làm hồi chiêu chiêu đầu tiên về 0. | Đòn đánh (cần thêm, bit 14 còn trống) |
| 4 | Wise Glasses | 3500 | Trận đấu | Chiêu gây thêm 10% sát thương. Nhẹ hơn Choice Specs (+35%) nhưng không giảm tốc độ. | Chiêu (bit 17 còn trống) |
| 5 | Weakness Policy | 3500 | Trận đấu | Khi bị đánh bởi chiêu hiệu quả mạnh, tăng 30% sát thương trong 10 giây. | Sát thương nhận + hệ (cần thêm) |
| 6 | Oran Berry | 150 | Berry | Dùng hết khi máu xuống dưới 30%: hồi 20% máu tối đa. | Giống Sitrus Berry (đã có) |

Ghi chú về icon: có thể dùng các icon có sẵn trong `analysis/builtin_icons.txt`, ví dụ `BTNClawsOfAttack` (Quick Claw), `BTNAntiMagicShell` (Bright Powder). Chưa xác nhận từng icon trong game.

## 2. Cách làm

- Thêm 6 dòng vào `ITEMS` trong `tools/v34/extras.py`, bit cờ mới (14, 17, 18...) không trùng với bit đang dùng.
- Viết hiệu ứng trong `tools/v34/jass/extra.j` và `extra_late.j`, theo cách Life Orb và Sitrus Berry đang làm.
- Chạy `items_list.py` để cập nhật danh sách.

## 3. Rủi ro

- **Cân bằng:** Shell Bell và Bright Powder có thể quá mạnh nếu đi cùng Life Orb. Cần thử trong game.
- **Chưa kiểm tra:** cờ mới và hook trong game chưa thử.
- **Hiển thị:** danh sách item khi bấm vào ô (trong ảnh) là đề xuất 11, chưa làm.

## 4. Câu hỏi cho bạn

1. Có chọn đủ 6 item không, hay bỏ bớt item nào?
2. Giá gợi ý có ổn không?
3. Có muốn thêm item hồi máu khác, hoặc item cho hệ cụ thể không?

## Trạng thái thực hiện (v3.4.5, chưa build)

- Đã làm: Shell Bell (IB0C, 3000), Bright Powder (IB0D, 3000), Wise Glasses (IB0E, 3500), Oran Berry (IT09, 150). Hook trong `extra.j` và `extra_late.j`.
- Bright Powder: 10% cơ hội hoàn lại sát thương vừa nhận. Đây là xấp xỉ của "trượt", không phải né thật.
- Chưa làm: Quick Claw và Weakness Policy, vì cần hook mới (hồi chiêu khi đánh; hệ của đòn nhận vào).
- Chưa kiểm tra trong game.
