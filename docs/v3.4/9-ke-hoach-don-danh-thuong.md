# 9. Kế hoạch: đòn đánh thường của các Pokémon (chờ duyệt)

Trạng thái: **chưa sửa code.** Chỉ là kế hoạch dựa trên dữ liệu trong map.

## 1. Vấn đề

- Đòn đánh thường (tấn công cơ bản) của mỗi Pokémon do **unit** quyết định, không do move. Đề xuất 6 chỉ đổi move, nên đòn đánh thường vẫn là đạn bay ở nhiều con.
- Tauros là ví dụ: dạng Aqua / Blaze / Combat có tầm 200 và đạn `LavaSpawnMissile`, nên bắn đạn.

## 2. Số liệu hiện tại (bản 3.4.4 đã build)

Dữ liệu đọc từ `war3map.w3u`, cột `ua1w` (kiểu đánh) và `ua1r` (tầm).

| Nhóm unit | Số lượng | Kiểu đánh hiện tại |
|---|---|---|
| Pokémon chơi được (P…) | 166 | cận chiến, tầm 200 (kể cả Tauros dạng hero) |
| Quái hoang / gym / huyền thoại (nX…) | 211 | 173 bắn đạn (missile), 38 cận chiến |

Phân loại theo chỉ số gốc của loài (`tools/learnsets.json`, chỉ số Attack và Sp. Attack):

| Nhóm | Số loài | Ý nghĩa |
|---|---|---|
| Đạn, Attack ≥ Sp. Attack | 91 | đánh vật lý nhưng bắn đạn: **nên chuyển sang cận chiến** |
| Đạn, Attack < Sp. Attack | 69 | đánh đặc biệt, bắn đạn: giữ |
| Cận chiến, Attack ≥ Sp. Attack | 29 | giữ |
| Cận chiến, Attack < Sp. Attack | 9 | đánh đặc biệt nhưng cận chiến: **nên xem lại** |
| Không có chỉ số (tên không khớp) | 13 | kiểm tra tay |

Phân loại chỉ dựa vào chỉ số, nên không hoàn toàn chính xác: một số loài có kiểu đánh riêng (Electric, Bug...) cần kiểm tra thêm.

## 3. Đề xuất

1. **Đổi đòn đánh thường của 91 loài đánh vật lý sang cận chiến:** `ua1w` = normal, bỏ đạn, tầm 128 (cận chiến chuẩn của WC3), giữ sát thương. Ví dụ Garchomp, Heracross, Tauros.
2. **Với 9 loài đánh đặc biệt nhưng cận chiến:** giữ cận chiến nếu là loài đánh tay (ví dụ Ditto), đổi sang đạn nếu chỉ số cho thấy đánh xa.
3. **Với 13 loài không có chỉ số:** kiểm tra tên map và chỉ số, rồi quyết định tay.
4. **Giữ nguyên** 69 + 29 loài đúng kiểu.
5. **Hiệu ứng đòn đánh thường:** dùng model hit ngắn (`slash-luc` cho đánh tay, `WhiteXMissile` hoặc đạn theo hệ cho đánh xa).

## 4. Rủi ro

- **Tầm đánh:** đổi từ 200 xuống 128 làm quái và hero phải tiến sát hơn, có thể khó đánh hơn. Cần thử trong game.
- **Cân bằng:** các loài đổi sang cận chiến có thể mất lợi thế khi bị đánh từ xa. Cần kiểm tra số liệu sau khi đổi.
- **Ghi đè dữ liệu:** unit có nhiều dạng (Mega, Shiny, Soul) đều phải đổi cùng nhau, nếu không sẽ không đồng nhất.

## 5. Các bước làm

1. Chốt danh sách 91 + 9 + 13 loài (bảng phân loại đầy đủ, xuất ra file).
2. Viết `tools/v34/attack_fx.py`: đổi `ua1w`, `ua1r`, `ua1m` của các unit theo danh sách.
3. Kiểm tra pjass, dry-run, và xác nhận số unit đổi.
4. Build khi bạn yêu cầu, rồi bạn chơi thử từng nhóm loài.

## 6. Câu hỏi cho bạn

1. Có đồng ý đổi 91 loài đánh vật lý sang cận chiến không?
2. Tầm cận chiến 128 có phù hợp không, hay bạn muốn 150?
3. Bạn có muốn Tauros đánh gần hết không, hay chỉ các dạng cụ thể?

## Trạng thái thực hiện (v3.4.5, chưa build)

- Đã làm: `tools/v34/attack_fx.py`, nối vào `build_v34.py`. Đòn đánh thường của **98 unit** (nX…) đổi thành cận chiến: bỏ đạn (`ua1m`), tầm 128 (`ua1r`), kiểu `normal`.
- Con số là 98 chứ không phải 91: thêm 3 dạng Tauros (Aqua, Blaze, Combat) và 5 dạng Alolan, vì đã ghép tên dạng về loài gốc để tra chỉ số.
- Giữ nguyên đạn: Aegislash, Darmanitan, Meganium, Porygon2 (không có trong bảng chỉ số, cần kiểm tra tay), và các loài đánh đặc biệt.
- Chưa làm: 9 loài đánh đặc biệt nhưng cận chiến (cần xem lại tay).
- Pjass 0 lỗi, dry-run đạt. Chưa kiểm tra trong game.
