# Đề xuất 7: dọn căn cứ cho gọn và đẹp hơn

Trạng thái: **chờ duyệt**. Chưa sửa code, chưa build. Đề xuất này dựa trên ảnh chụp trong game (căn cứ bên trái, Farfetch'd cấp 1) và các tọa độ đọc được từ `v34/war3map.j` của bản 3.4.2.

## 1. Vấn đề

Trong một khu căn cứ nhỏ đang có cùng lúc:
- 6 khối shop lớn (3 xanh ở trên, 3 tím ở dưới), gồm Poke Mart / Mega Shop của v1.8;
- NPC "MOVES" nằm sát một shop và cổng GYM;
- 2 vòng cổng dịch chuyển bên phải, thêm cổng GYM ở góc trên;
- đống lửa, xương, vòng ma thuật và các đối tượng trang trí khác ở giữa đường đi.

Tôi chỉ nhận ra một số đối tượng từ ảnh. Sau Bước A (xem mục 5), đã biết:
- Các khối shop và NPC đều do script đặt (`CreateUnit`), map **không có** file `war3mapUnits.doo`.
- Đồ trang trí là doodad trong `war3map.doo`, đọc được bằng `analysis/read_doodads.py`.
- Tên loại doodad (ví dụ `YPpp`, `YTct`) không có trong map, nên chưa biết tên thật. Đống lửa và xương trong ảnh không nằm trong danh sách doodad gần căn cứ, nên có thể là unit ẩn hoặc hiệu ứng.

## 2. Những gì đã biết chắc (từ `war3map.j`, bản 3.4.2)

Các đối tượng do script đặt, tọa độ bên phải căn cứ phía đông (x dương), căn cứ phía tây đối xứng qua tâm:

| Đối tượng | Mã | Vị trí (x, y) |
|---|---|---|
| Mega Shop I | `n00N` | (5696, 544) |
| Mega Shop II | `n00Q` | (5392, 544) |
| Mega Shop III | `n00O` | (6000, 544) |
| Poke Mart (cửa hàng chính) | `n00P` | (5952, 0) |
| Poke Mart khác (`nMS1`/`nMS2`/`nMS3`) | `nMS1` `nMS2` `nMS3` | (6000 / 5696 / 5392, -544) |
| Công trình 'nwgt' | `nwgt` | (5120, -640) |
| Công trình 'n030' | `n030` | (5120, 640) |
| Công trình 'ncop' | `ncop` | (4992, 0), (4608, 0) |
| Cổng căn cứ | (gate) | (5392, -288) |
| Vị trí shop mới (Battle Shop, Item Shop) | — | (5696, ±288), (5392, ±288), (5904, ±288) |

Bên phía tây có đối xứng với các giá trị trên (x đổi dấu).

Tên trong cột "Đối tượng" là **đoán** từ thói quen đặt tên của v1.8 và từ `HANDOFF-v3.4.md`, chưa kiểm chứng. Chỉ mã (cột "Mã") là chắc chắn. Cần đọc tên thật từ `war3map.w3u` trước khi quyết định.

Ghi chú:
- Ảnh cho thấy khối xanh/tím là một trong các nhóm trên. Cần đọc `war3mapUnits.doo` để biết khối nào là khối nào.
- Vòng cổng dịch chuyển và đống lửa là **doodad**, không phải unit. Chúng nằm trong `war3map.doo`.
- Tọa độ của 6 vị trí shop mới phụ thuộc vào hàng shop cũ. Nếu dời hàng cũ, các vị trí này phải được tính lại.

## 3. Đề xuất

### Bước A: đọc dữ liệu (không đổi gì)
- Viết bộ đọc `war3mapUnits.doo` và `war3map.doo`, xuất danh sách: loại, vị trí, góc, tỉ lệ.
- Kiểm tra bộ đọc: đọc hết file, số byte còn lại phải bằng 0. Đối chiếu số unit với `war3map.j`.
- Vẽ lại bản đồ căn cứ có đánh dấu từng đối tượng (kiểu `analysis/base_layout.py`).

### Bước B: dời các khối (sau khi bạn duyệt vị trí mới)
- Gom 6 khối shop thành 1 hàng thẳng (ví dụ 3 xanh + 3 tím đặt đối diện nhau, cách đều nhau 256 đơn vị).
- Dời NPC "MOVES" ra khỏi cạnh shop, đặt gần lối vào căn cứ để người chơi dễ tìm.
- Đặt cổng GYM và 2 vòng cổng dịch chuyển ở một góc riêng, không để chung với đường đi.
- Giữ lối đi từ Poke Center đến cửa căn cứ luôn thông (đã kiểm tra bằng `war3map.wpm`).

### Bước C: bỏ bớt trang trí
- Bỏ đống lửa, xương và vòng ma thuật thừa ở giữa đường đi. Giữ lại tối đa 1–2 chi tiết ở góc để căn cứ vẫn có không khí.
- Chỉ xóa doodad, **không xóa unit chức năng** (shop, NPC, cổng).

### Cập nhật code liên quan
- `tools/v34/extras.py` (dòng 137): cập nhật danh sách vị trí shop mới.
- `tools/v34/league_area.py`: cổng căn cứ `BASE_GATE` giữ nguyên nếu không dời cổng.
- Chạy lại `check.py` và `build_v34.py --dry-run` để kiểm tra.

## 4. Rủi ro

- **Dời NPC hoặc shop có thể làm lệch logic:** các hàm như `Mega_Start` và `Ext_Spot` dựa trên tọa độ cố định. Phải kiểm tra từng chỗ dùng tọa độ đó.
- **Dời cổng hoặc đường đi có thể làm người chơi kẹt.** Phải kiểm tra bằng `war3map.wpm` và thử đi qua trong game.
- **Đống lửa và vòng ma thuật có thể là hiệu ứng gắn với một unit ẩn.** Nếu xóa nhầm, có thể mất chức năng ẩn. Cần xác nhận khi đọc dữ liệu ở Bước A.
- **Không thể kiểm tra giao diện tự động.** Bạn cần xem lại trong game sau khi build.

## 5. Kết quả Bước A (chỉ đọc, không đổi map)

Chạy: `python -I analysis/read_doodads.py "../Pokemon Arena v3.4.2.w3x" --base`

- File doo đọc đúng: 1395 doodad, số byte khớp (đã kiểm tra).
- Gần hai căn cứ (|x| > 4000, |y| < 1500) có 268 doodad:
  - `YPpp` 137 cái: tường và hàng rào. Các hàng ở y = -992 và y = 1056 (x từ -6048 đến -4704 và từ 4832 đến 5472) và cột x = ±4704 / ±4768 chạy dọc viền căn cứ.
  - `YTct` 128 cái: cây ở ngoài căn cứ (x từ 6800 đến 10200), không ảnh hưởng căn cứ.
  - `DTg7` 2 cái ở (±4864, 0): có thể là hai vòng tròn ma thuật trong ảnh, chưa kiểm chứng.
  - `OTsp` 1 cái ở (-8576, 128): ngoài căn cứ.
- Đối chiếu với ảnh: 6 khối lớn (3 trên, 3 dưới) khớp với các unit do script đặt ở y = ±544 (`n00N`, `n00O`, `n00Q`) và y = -544 (`nMS1`, `nMS2`, `nMS3`). Khối nhỏ giữa là vị trí shop mới (±5392, ±288) mà `extras.py` đặt. Nhà đỏ bên trái là `n00P` ở (-5952, 0).

Hệ quả: phần lộn xộn chủ yếu do unit do script đặt và các shop mới, không phải do doodad. Muốn dọn gọn thì phải sửa vị trí trong code (`war3map.j` và `extras.py`), còn doodad chỉ cần sửa nếu muốn bỏ tường hay trang trí.

## 6. Trạng thái Bước B (đã làm trong code, chưa build)

Thay đổi thực tế khác với đề xuất ban đầu, vì số liệu cho thấy:
- Sáu khối v1.8 (`n00N`, `n00O`, `n00Q`, `nMS1`, `nMS2`, `nMS3`) **đã** xếp thành lưới 2×3 gọn gàng. Không cần gom lại, nên giữ nguyên.
- Phần lộn xộn chính là hai shop mới (Battle Shop, Item Shop) nằm ở khe 288 giữa hai hàng, tại (±5696, ±288).
- Đã đổi danh sách vị trí trong `tools/v34/extras.py` sang cột trống (±5120, ±288), cách unit gần nhất 315 đơn vị và đi được (kiểm tra bằng `war3map.wpm`). Các vị trí cũ vẫn là phương án dự phòng.
- NPC "MOVES" (`Npc_X` = ±5568, `Npc_Y` = 0) **không đổi**: đứng ở khoảng trống giữa căn cứ, không còn bị shop mới che.
- Cổng GYM, cổng league và các pillar không đổi.
- `tools/v34/version.txt` đã tăng từ 3.4.2 lên **3.4.3**.

Kiểm tra: `apply.py` chạy xong, `check.py` 0 lỗi pjass, `build_v34.py --dry-run` đúng tên `Pokemon Arena v3.4.3.w3x`. **Chưa ghi file .w3x** vì bạn chưa bảo "build". Chưa kiểm tra được trong game.

Bước C (bỏ trang trí) chưa làm.

## 7. Câu hỏi cho bạn

1. Bạn muốn giữ đủ mọi shop và NPC, hay bỏ hẳn shop nào đó?
2. Bạn có muốn bỏ hết đống lửa, xương, vòng ma thuật, hay chỉ bớt một phần?
3. Có cần giữ đối xứng hai bên căn cứ không?

Sau khi bạn trả lời và duyệt, bắt đầu từ Bước A.
