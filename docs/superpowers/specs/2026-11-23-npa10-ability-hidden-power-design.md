# NPA 1.0: Ability, Hidden Ability, Hidden Power cho Pokemon mới (thiết kế đã duyệt)

Nguồn: doc Claude Docs https://claude.ai/artifact/SBCQ4SSn7xjkgLkeMQfWxa (người dùng duyệt xong 2026-11-23).
Phạm vi: 285 hero mới của New Pokemon Arena 1.0 = 205 Gen 1-4 (`EG..`), 52 hero form (`PF00..PF51`), 28 Mega mới (`hF00..hF27`),
cộng 12 Gigantamax (`hG..`) và 4 Paradox mới (formId 20..23).

## Mục đích
Pokemon mới đang mang giá trị giữ chỗ hoặc ability theo hệ thay vì ability thật. Hiện trạng đo trên script build 2026-11-23:
- 52 form và 28 Mega: tất cả hệ Normal, ability Pressure, vì cây `docs/form-models/cay-pha-he.html` để trống danh sách hệ của 106 dạng.
- 205 Gen 1-4: hệ đúng, ability chọn theo hệ hoặc theo tên có hằng `AB_` cũ, không có Hidden Ability.
- 4 Paradox mới: không có ability (code `Ab_Want` và `PAX_Form_AbId` dừng ở formId 19).
- Dạng cuối: Hidden Power chỉ là +30% chỉ số, dùng chung 1 ô quest (ô 58) cho mọi dạng cuối của một người chơi.
- 25 Legend thêm sau (idx 33..57) được gán vai trò tank / caster / striker / drain nhưng chỉ tank có code (7 con).

## Quyết định (cột "Quyết định" của doc)
| # | Quyết định |
|---|---|
| 1 | Chưa chọn. Mặc định: một bên build mỗi lần, build ra `out/` rồi mới thay bản 1.0. |
| 2 | Sửa hệ và ability giữ chỗ của 52 form và 28 Mega, làm trước. |
| 3 | Tải PokeAPI; dạng nào thiếu thì lập danh sách cho người dùng duyệt, không tự bịa. |
| 4 | 38+ ability còn thiếu: mỗi ability là một ability riêng (tên, mô tả, hiệu ứng), code bên trong dùng chung được cho cơ chế giống nhau. Người dùng duyệt từng cái. |
| 5 | Hidden Ability (Ability Patch) cho Gen 1-4 và hero form. Mega và Gigantamax không dùng. |
| 6 | Hidden Power dạng cuối: cách B, mỗi dạng cuối 1 ô quest, hiệu ứng theo 4 mẫu vai trò. Viết nốt code caster, striker, drain và dùng luôn cho 18 Legend đang thiếu. |
| 7 | Để sau: chặn `-form` miễn phí, bỏ Regional Charm và Form & Tera Orb. |
| 8 | 4 Paradox mới: thêm 4 nút "+" thay vì 4 Booster Energy, kiểm giới hạn ô lệnh trước. |
| 9 | Không tạo Mega Stone cho 28 Mega mới, không tạo Soul cho 52 hero form. |
| 10 | Để sau: item tiến hóa Gen 2-4, item riêng từng loài. |

## Nguyên tắc
- Không tạo item mới. Mở khóa bằng nút "+" (A800..A879 ở `build_v43.py` / `form_expansion.py`).
- Thứ tự chọn ability giữ nguyên: `-abtest` > Mega > form > Hidden Ability đã mở > mặc định của loài.
- Chữ trong game bằng tiếng Anh.

## Hidden Power cách B
- Mỗi dạng cuối (Mega, Gigantamax, form Paradox, hero form cuối) có 1 ô quest riêng, ô 59 trở đi. Legend giữ ô 1..57.
- Khóa quest `PAX_Leg_QKey(pid, idx) = 1000 + pid * 64 + idx` đổi thành hệ số 256.
- Vai trò chia theo chỉ số: tank nếu (Def + SpDef) / 2 >= 105; striker nếu stat chính là Attack; caster nếu stat chính là Sp.Atk.
  Drain không gán theo luật, chỉ giữ cho Xerneas và Yveltal.
- Hiệu ứng khi đã thức tỉnh (số lấy từ `legend_expansion_data.py`): tank nhận ít hơn 15% sát thương; caster +15% sát thương chiêu;
  striker +12% sát thương đánh và chiêu; drain +12% sát thương và hút 12% sát thương chiêu thành máu.

## Ngoài phạm vi
`-form` miễn phí, Regional Charm / Form & Tera Orb, Mega Stone, Soul cho form, item tiến hóa, item riêng từng loài.

## Việc người dùng phải duyệt trong lúc làm
1. Danh sách dạng không có trên PokeAPI (nhiều khả năng Mega Z-A).
2. Thiết kế từng ability mới (trang duyệt có ô chọn, như 3 vòng ability trước).
3. Trước khi thay `New Pokemon Arena 1.0.w3x` bằng bản build mới.
