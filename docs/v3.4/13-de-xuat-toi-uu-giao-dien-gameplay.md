# 13. Đề xuất tối ưu giao diện và gameplay (chờ duyệt)

Trạng thái: **chưa sửa code.** Các mục dưới đây dựa trên code v3.4.6 hiện tại. Mục nào được duyệt sẽ làm riêng, không gộp hết một lượt.

## A. Giao diện

| # | Đề xuất | Lý do / chỗ trong code | Độ khó |
|---|---|---|---|
| A1 | Đánh dấu cổng League, gym và NPC trên minimap (ping hoặc icon) | Hiện chỉ có text tag; người chơi mới khó tìm | Thấp |
| A2 | Dialog item hiện số item trận đấu đang giữ (x/3) và vàng hiện có | `Ish_Show` chỉ có giá; giới hạn 3 item chỉ báo khi mua lỗi | Thấp |
| A3 | Thông báo quan trọng (Shiny, Mega, thời tiết, cảnh báo trụ) hiện ở một dòng cố định trên đầu màn hình, không đè lên nhau | Hiện dùng `DisplayTimedTextToPlayer` cho nhiều loại, dễ trôi | Trung bình |
| A4 | Trạng thái gym đã thắng / đang bận đổi màu text tag hoặc thêm dấu tick | Người chơi không biết gym nào đã xong | Thấp |
| A5 | Tooltip skill/item có sát thương tương đối và tác dụng cụ thể (vd "+30% sát thương chiêu") | Mô tả item đã có, mô tả skill chưa đồng bộ | Trung bình |
| A6 | Thống nhất nguồn icon: một bộ icon cho item (đang trộn icon map và icon ảnh TrainerOps) | Bản quyền ảnh TrainerOps cần được xác nhận trước khi phát hành công khai | Cần quyết định |
| A7 | Hộp thoại chọn Pokémon/move: thêm nút "đóng" cố định và tiêu đề có số trang | Dialog có nhiều nút, dễ nhầm trang | Thấp |

## B. Gameplay

| # | Đề xuất | Lý do | Độ khó |
|---|---|---|---|
| B1 | Cân bằng item: Life Orb cộng dồn với Choice Band/Specs/Scarf có thể quá mạnh. Thử giới hạn tổng bonus sát thương, hoặc giảm Life Orb xuống 25% | Chưa chơi thử, nên cần số liệu từ trận | Cần thử |
| B2 | Bright Powder hiện chỉ là hoàn lại 10% sát thương, không phải né thật. Đổi thành né thật (bỏ qua sát thương) hoặc đổi tên | Đúng với tên gọi và mô tả | Trung bình |
| B3 | Thêm Quick Claw và Weakness Policy (đã có trong đề xuất 12, còn thiếu hook) | Còn 2 item chưa làm | Trung bình |
| B4 | Thời tiết: báo trước 30 giây trước khi đổi | Hiện đổi đột ngột | Thấp |
| B5 | Gym: hiện độ khó (HP/sát thương/AI) trên label gym để người chơi chọn thứ tự | Đã có dữ liệu `Gym_Diff*` nhưng người chơi không thấy | Thấp |
| B6 | Cooldown Escape Rope và cổng League (3 giây): hiện đếm ngược cho người dùng | Hiện chỉ có chữ | Thấp |
| B7 | Học move: dialog hiện "đã học n/4 slot" và move nào đang trùng loại (lý do Marowak chỉ học 2) | Giảm thắc mắc như trường hợp Marowak | Thấp |
| B8 | Melee: kiểm tra tầm 150 bằng trận thật, vì con melee đánh gần có thể bị kẹt khi vào gym | Đề xuất 9 chưa test trong game | Cần thử |
| B9 | League: cho thời gian nghỉ giữa các trận Elite Four (vd 30 giây) để người chơi hồi máu | Hiện trận liên tiếp, khó theo kịp | Thấp |

## C. Tối ưu kỹ thuật (không đổi trải nghiệm)

| # | Đề xuất | Lý do |
|---|---|---|
| C1 | `Itm_Refresh` chạy mỗi giây cho từng hero: 21 lần `SaveInteger` mỗi lần. Chỉ cập nhật khi nhặt, dùng, mua item (đã có `Itm_Refresh` ở các điểm đó) và bỏ việc làm mới mỗi giây | Giảm tải với 12 hero |
| C2 | Gộp bộ đếm cổng League (`League_PortalTick` 0.5 giây) với `Ext_Pulse` | Giảm số timer |

## Câu hỏi cho bạn
1. Duyệt nhóm nào: A (giao diện), B (gameplay), C (kỹ thuật), hay chọn từng mục?
2. A6: giữ icon đã chọn (có rủi ro bản quyền) hay quay lại icon của map?
3. B1: muốn giảm Life Orb hay giới hạn tổng bonus?

## Trạng thái thực hiện (v3.4.6, chưa build, chưa test trong game)

- Đã làm: A1 (minimap: NPC, cổng League, gym), A2 (dialog hiện vàng và x/3 item trận đấu), A3 (`Note_Say`: thông báo thời tiết và Shiny thay dòng cũ), A4 (nhãn gym đổi thành "cleared by"), A6 (giữ icon TrainerOps: map riêng tư), A7 (dialog hiện trang x/y), B1 (Life Orb +25%), B2 (Bright Powder né thật: 10% hit không gây sát thương), B3 (Quick Claw IB0F, Weakness Policy IB10), B4 (cảnh báo 30 giây trước khi đổi thời tiết), B5 (nhãn gym có độ khó), B6 (đếm lùi Escape Rope; báo thời gian chờ cổng League), B7 (dialog học move báo n/4 slot), B9 (nghỉ 30 giây giữa các Elite Four, được hồi máu ngay), C1 (làm mới item mỗi 5 giây và khi nhặt, mua, dùng), C2 (kiểm tra cổng League trong `Ext_Pulse`, bỏ timer riêng).
- Chưa làm: A5 (mô tả skill có sát thương tương đối: khối lượng lớn, cần duyệt riêng); B8 (tầm đánh melee: cần thử trong game).
- Quick Claw: "chiêu đầu tiên" được hiểu là chiêu đầu tiên đang hồi chiêu trong danh sách kỹ năng của Pokémon.
