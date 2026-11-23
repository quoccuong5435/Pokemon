# 14. Kế hoạch: skill buff, phòng thủ và bị động (chờ duyệt)

Trạng thái: **chưa sửa code.** Ngày 2026-11-08.

## 1. Hiện trạng

- Cả 319 move trong danh sách (`Mv_Label`) đều có sức mạnh > 0. Không có move nào chỉ buff hay phòng thủ. Các move status trong learnset (PokeAPI) đã được đổi thành move sát thương khi dựng map.
- Bị động của Pokémon đã có: 68 khả năng (Ability) trong `docs/v3.4/1-ability.md`, gồm Intimidate, Aura, Pulse, Mold Breaker... Chúng chạy qua `Ab_OutMult`, `Ab_InMult`, `Ab_OnHit`, `Ab_Aura`, `Ab_Pulse` trong `tools/v34/jass/ab_core.j`.
- Chưa có khung chung cho hiệu ứng tạm thời trên đơn vị (buff chỉ số, khiên, giảm sát thương nhận theo thời gian). `Ext_DamageMult` và `Ab_FxAdd` làm một phần việc này nhưng chỉ cho từng trường hợp riêng.

## 2. Mục tiêu

1. Có move **buff tự thân** (tăng công, tốc độ, phòng thủ trong vài giây).
2. Có move **phòng thủ** (khiên, hồi máu theo thời gian, giảm sát thương nhận).
3. Có move **gây bất lợi cho đối thủ** (giảm công, giảm tốc độ), nếu chưa có.
4. Bị động: rà lại 68 Ability để chắc mỗi cái có mô tả rõ, và thêm bị động cho các loài còn thiếu.

## 3. Thiết kế

### 3a. Khung hiệu ứng tạm thời (buff engine)

- Lưu theo `Ab_HT` trên đơn vị: 4 chỉ số (công, phòng thủ, công đặc biệt, tốc độ) dưới dạng bậc từ -6 đến +6 (như game chính), mỗi bậc +/- 50% ở công/phòng thủ, +/- 33% ở tốc độ.
- Hết thời gian thì bậc về 0. Lưu thời điểm hết hạn bằng `Mega_Time + thời gian`, giống key 128 của Champion Aura.
- Hàm chính: `Bf_Add(u, stat, bậc, thời gian)`, `Bf_Mult(u, stat)` (tính hệ số hiện tại), `Bf_Tick` (dọn bậc hết hạn, chạy mỗi giây trong `Ext_Pulse`).
- Dùng `Bf_Mult` trong `Ext_DamageMult` (công, phòng thủ) và `Ab_ASMult` (tốc độ).

### 3b. Khiên và giảm sát thương

- Khiên: lưu lượng máu chặn được ở `Ab_HT`, trừ vào sát thương trước `Ext_Final`. Hết thời gian hoặc hết khiên thì bỏ.
- Giảm sát thương nhận: thêm hệ số vào `Ext_DamageMult` cho đơn vị đang buff phòng thủ.
- Hồi máu theo thời gian: `Ab_Heal` mỗi giây trong `Ext_Pulse`, như Leftovers.

### 3c. Gây bất lợi (đối thủ)

- Giảm công và giảm tốc độ đối thủ dùng cùng `Bf_Add` với bậc âm.
- Có thể tận dụng hàm `Ab_Poison` và `Ab_FxAdd` cho hiệu ứng nhìn thấy.

### 3d. Bị động

- Rà 68 Ability: ghi đúng mô tả (thời gian, phạm vi, tỉ lệ). Đây là việc làm trong văn bản, không đổi cơ chế.
- Thêm bị động cho các loài chưa có. Chọn theo hệ hoặc theo nhóm: loài hệ Thép có bị động giảm sát thương nhận, loài hệ Điện có bị động tăng tốc độ khi bị đánh.

## 4. Chọn move nào

- Một bảng riêng (`tools/v34/status_data.py`), mỗi dòng: tên move, loại (buff / khiên / hồi / giảm địch), giá trị, thời gian. Giống cách `melee_fx.py` làm.
- Ban đầu chọn khoảng 15 move cho 4 nhóm trên. Số lượng cụ thể cần bạn duyệt.
- Mỗi move status vẫn chiếm một slot học như move thường, nên không tăng số slot.

## 5. Các bước

1. Khung buff engine và tests tay trong game: tăng công một đơn vị thử, kiểm tra hết hạn.
2. Khiên và hồi theo thời gian.
3. Move gây bất lợi.
4. Bảng move status và gắn vào `Mv_*`, sửa tên và mô tả.
5. Rà bị động và viết lại mô tả.
6. Kiểm tra AI của creep (`ai.j`) có dùng move status đúng không.

## 6. Rủi ro

- **Cân bằng:** buff chồng lên Life Orb, Choice Band và Champion Aura có thể quá mạnh. Đặt giới hạn tổng bậc +6.
- **Thời gian:** move status tốn lượt của người chơi nhưng không gây sát thương, nên cần đủ mạnh để có ý nghĩa.
- **AI creep:** creep hiện không dùng move hero (xem `ai.j`). Phải thêm logic dùng move status cho creep, nếu không thì chúng chỉ đứng.
- **Kiểm tra:** không test được trong game từ đây; cần bạn thử từng nhóm.

## 7. Câu hỏi cho bạn

1. Duyệt cả 4 nhóm (buff, khiên, gây bất lợi, bị động), hay làm từng nhóm?
2. Số lượng move status ban đầu khoảng 15 có ổn không?
3. Giới hạn bậc +6 hay muốn thấp hơn?
4. Creep có cần dùng move status không, hay chỉ hero?
