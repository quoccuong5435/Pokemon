# Danh sách ý tưởng chờ duyệt (Pokemon Arena)

Duyệt bằng cách ghi "OK" hoặc "Không" cạnh từng mục. Mình chỉ làm mục đã OK.

## A. Lỗi đang mở (ưu tiên)
1. **Phòng boss/gym lệch trên map Big** — sửa tọa độ theo nền Naruto, build bản mới (3.2.11). [ ]
2. **Đường thẳng (LINE) chỉ trúng mục tiêu** — tự tính va chạm dọc đường bay, trúng mọi đơn vị đi qua. [ ]
3. **Elite bị nhỏ** — cần bạn cho biết elite nào, mình kiểm tra scale. [ ]
4. **Nút Mega không hoạt động** — bản 3.2.5 đã đưa về card; chờ bạn thử lại. [ ]
5. **Ability cũ 1.8 còn sót** — đã bỏ ở 3.2.4; chờ bạn xác nhận. [ ]

## B. Nội dung mới
6. **Khu boss legend gen 1–9** (94 con, đã có danh sách trong `analysis\legendary_gen1_9.json`) — chọn: lấy hết / 1 con mỗi gen. [ ]
7. **Cốt truyện nhẹ theo gen** — mỗi gen một khu boss, thứ tự từ gen 1 đến gen 9. [ ]
8. **Teleport cho boss mới** — dùng ability A005 của map, giống Celebi/Darkrai. [ ]
9. **TM/HM 3.000 vàng** — lấy từ PokeAPI, chọn thế hệ (ví dụ thế hệ 9). [ ]
10. **Thêm Pokémon playable** — chọn: 120 PKLegends / toàn bộ PokeAPI (cần model). [ ]

## C. Cân bằng
11. **Máu playable** — hiện x2 phần máu gốc, cần bổ sung phần Strength để đủ x2 tổng. [ ]
12. **Độ khó gym** — tăng máu/sát thương/armor của đối thủ, chọn mức (ví dụ x1.5). [ ]
13. **Sát thương skill** — đã giảm (cap x3). Chờ bạn thử lại. [ ]

## D. Hiệu ứng và giao diện
14. **Hiệu ứng skill** — tham khảo WC3 (ví dụ hiệu ứng đường thẳng, nổ vòng, hồi máu). Mình tự code hiệu ứng có sẵn trong WC3. [ ]
15. **Icon hệ** — chờ bạn gửi file hoặc chọn icon. [ ]
16. **NPC học chiêu** — đổi thành người đi, đã làm; chờ bạn xác nhận. [ ]

## Câu hỏi cần quyết
- Nền Big hay 160×160 + dịch chuyển?
- Thế hệ TM/HM và số Pokémon playable?

## Quyết định đã chọn (qua lựa chọn nhanh)
- Nền: **Big 416×480** (cần sửa lệch phòng gym).
- Boss: **lấy hết 94** legendary/mythical gen 1–9.
- TM/HM: **thế hệ 9**.
- Pokemon playable thêm: **120 PKLegends**.

## Khu giải đố (mới, đã chọn)
- Không đố theo thứ tự. Mỗi legend có **phòng riêng**, phòng mang theo hệ/môi trường của legend.
  - Ví dụ: phòng chim băng → nền băng; phòng chim lửa → nền nham thạch.
- Số phòng: 94 (mỗi legend một phòng), đi cùng khu boss.
- Cần làm thêm: chọn nền (texture) cho từng hệ. Mình có thể đổi texture mặt đất trong dữ liệu map (w3e), nhưng phải xem danh sách texture có sẵn của nền Big để chọn đúng loại băng, nham thạch, cỏ, nước...

# DUYỆT LẦN CUỐI
Nền: **Pokemon Arena gốc (160×160)**. Không dùng nền Big nữa. File Big vẫn giữ nguyên, không xóa.

| # | Việc | Ghi chú | Duyệt |
|---|------|---------|-------|
| 1 | Khu boss 94 legend gen 1–9, mỗi con một phòng | Chọn chỗ trống trên nền 160×160 (cần đọc dữ liệu đường đi hoặc bạn gửi `-pos`) | [ ] |
| 2 | Phòng theo hệ (nền băng, nham thạch...) | Đổi texture mặt đất trong vùng phòng, dùng texture có sẵn của map | [ ] |
| 3 | Cốt truyện nhẹ theo gen (gen 1 → gen 9) | Nội dung cốt truyện mình sẽ viết, bạn duyệt sau | [ ] |
| 4 | Teleport (A005) cho boss mới | Giống Celebi/Darkrai | [ ] |
| 5 | TM/HM 3.000 vàng, thế hệ 9 | Lấy từ PokeAPI | [ ] |
| 6 | 120 PKLegends playable | Cần kiểm tra model trước | [ ] |
| 7 | Chiêu đường thẳng trúng mọi mục tiêu đi qua | Tự tính va chạm dọc đường bay | [ ] |
| 8 | Elite bị nhỏ | Cần bạn cho biết elite nào | [ ] |
| 9 | Nút Mega không hoạt động | Chờ bạn thử bản 3.2.5 | [ ] |
| 10 | Ability cũ 1.8 còn sót | Đã bỏ ở 3.2.4, chờ xác nhận | [ ] |
| 11 | Máu playable x2 tổng | Thêm phần Strength (25/điểm) | [ ] |
| 12 | Độ khó gym (đối thủ mạnh hơn) | Mức đề xuất x1.5 máu và sát thương | [ ] |
| 13 | Hiệu ứng skill theo WC3 | Đường thẳng, nổ vòng, hồi máu | [ ] |
| 14 | Icon hệ | Cần file icon từ bạn | [ ] |

Đã làm, chờ bạn xác nhận: sát thương skill cap x3 (3.2.9), chiêu học theo level thật (3.2.9), NPC học chiêu là người đi và có nút Close (3.2.6–3.2.7), phím QWER (3.2.1).

## Lựa chọn cuối (đã trả lời)
- Nền: **giữ 160×160**, boss ở khu trống + **dịch chuyển** bằng lệnh.
- Thứ tự: **làm tất cả** (khu boss, lỗi, TM/HM, Pokémon mới).
- Cốt truyện: **ngắn gọn, mỗi gen một đoạn**.

## DUYỆT CUỐI (tối nay)
- **Spawn 94 legend** lên map: **100% rớt đồ**, mỗi phút spawn **1 hoặc 2 con**, **không giới hạn số con**.
- **TM/HM 3.000 vàng**, thế hệ 9 (dữ liệu đã lấy: 229 mục, `analysis\tmhm_scarlet_violet.json`).
- **Build 3.2.11** sửa lỗi, tạo file mới, không ghi đè bản cũ.

## Lựa chọn mới (đã trả lời)
- 120 PKLegends thành playable: **chỉ số lấy theo PKLegends** (quy đổi sang cân bằng map).
- Model: **chỉ dùng model có sẵn**, loài thiếu model thì bỏ qua.

## Tavern (đã trả lời)
- Chia tavern **theo hệ**: mỗi hệ một tavern.
- Vị trí: **đặt gần tavern hiện có** (448, 4512), xếp thành dãy.

## Thiết kế tavern (bạn mô tả, đã ghi)
- Tavern đặt gần (448, 4512). Mỗi **ô hệ** là một tavern: bấm vào mở **danh sách chọn** giống chọn chiêu.
- Chuyển **chỗ đặt wisp** (chọn Pokémon khởi đầu) vào khu tavern.
- Chọn xong, hero được **dịch chuyển về Poké Center** (chỗ hồi máu).
- Cần: tọa độ Poké Center (đứng ở đó gõ `-pos`).

## Đã chọn (tavern)
- Chỗ hồi máu: **vị trí bắt đầu của người chơi** (`GetPlayerStartLocation`), không cần tọa độ.
- Menu tavern: **nhiều trang** (mỗi trang 10 con, có nút Trang sau/Trang trước).
