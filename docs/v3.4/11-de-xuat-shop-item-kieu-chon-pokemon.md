# 11. Đề xuất: chọn item theo kiểu chọn Pokémon (chờ duyệt)

Trạng thái: **chưa sửa code.** Đề xuất này thay cho việc đặt Battle Shop và Item Shop thành tòa nhà riêng (xem đề xuất 7).

## 1. Ý tưởng

Lúc bắt đầu, người chơi chọn Pokémon qua một hộp thoại có danh sách nút. Item cũng làm như vậy:
- Một NPC duy nhất, **Cửa hàng item**, đặt cạnh NPC "MOVES" (cùng kiểu NPC, không cần tòa nhà).
- Click NPC mở hộp thoại danh sách item, mỗi nút là một item kèm giá, ví dụ `Life Orb - 4000`.
- Click một item để xem công dụng (hiện trong tin nhắn của hộp thoại), rồi bấm **Mua**.
- Item vào túi đồ của người chơi và trừ vàng, giống cách mua TM ở NPC MOVES.

## 2. Lợi ích

- Không cần Battle Shop và Item Shop trên bản đồ, nên căn cứ bớt rối (đề xuất 7).
- Không còn giới hạn 12 item mỗi shop, nên không cần chia item vào các shop có sẵn.
- Thêm item mới chỉ cần thêm một dòng trong `extras.py`, danh sách hộp thoại tự cập nhật.

## 3. Cách làm

- **Nhiều trang:** một hộp thoại tối đa 12 nút, nên 21 item chia thành 2 trang (như danh sách TM hiện tại). Có nút "Trang sau" và "Trang trước".
- **Nội dung nút:** `Tên - giá`. Công dụng hiện khi chọn item, trước khi mua.
- **Quy tắc:** giữ giới hạn 3 item trận đấu (`BATTLE_LIMIT_KIND`) và giới hạn từng loại đá tiến hóa như hiện tại.
- **Vị trí NPC:** cạnh NPC MOVES, ở vùng trống giữa căn cứ. Cần kiểm tra không chắn cổng gym (xem `analysis/gym_path_check.py`).
- **Cập nhật:** tên, giá và công dụng lấy từ `tools/v34/extras.py`, cùng nguồn với `10-danh-sach-item.md`.

## 4. Rủi ro

- Phải tách item ra khỏi tòa nhà shop, nên cần sửa `Ext_PlaceShops` và `Ext_Shop` (chưa dùng ở chỗ nào khác).
- Nếu hộp thoại không mở được (quá nhiều nút, hoặc người chơi đang trong trận), phải có thông báo rõ.
- Chưa kiểm tra trong game; cần thử mở hộp thoại và mua thử.

## 5. Câu hỏi cho bạn

1. Có muốn một NPC item thay cho hai shop không?
2. Có để NPC này cạnh NPC MOVES không, hay ở chỗ khác?
3. Chia 2 trang như đề xuất có ổn không?

## Trạng thái thực hiện (v3.4.5, chưa build)

- Đã làm: NPC "ITEM SHOP" tại (-5376, 0), cạnh NPC MOVES, không chắn đường gym. Click NPC hoặc gõ `-items` gần NPC để mở danh sách. Danh sách 8 item một trang, có nút trang trước / sau. Chọn item hiện công dụng, rồi Mua hoặc Quay lại. Mua trừ vàng, đưa item vào túi hero, giới hạn 3 item trận đấu.
- Code: `tools/v34/jass/item_shop.j`, khai báo biến trong `globals.j`, gọi `Ish_Init()` sau `Ext_PlaceShops()` trong `apply.py`.
- Battle Shop / Item Shop không còn được đặt trên bản đồ (`Ext_SpotN = 0`), nên không còn bài toán 4 item thừa.
- Chưa kiểm tra trong game: mở hộp thoại, mua, giới hạn và phân trang.
