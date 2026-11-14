# Ý tưởng cho bản tiếp theo của nhánh 3.4.10 + prompt dán sang tài khoản kia

Ngày 2026-11-14. Nguồn ý tưởng: so sánh map `Pokemon Arena v3.4.10.w3x` với nhánh code ở máy này (3.4.1–3.4.6) và các
đề xuất đang chờ (docs/v3.4: 7, 9, 12, 13, 14, kế hoạch công / thủ).

Cách dùng: mở phiên Claude Code của tài khoản đang giữ code 3.4.10 và dán nguyên đoạn giữa hai dấu `---` bên dưới.

---

Tôi có một danh sách ý tưởng cho bản tiếp theo của map (sau 3.4.10). Danh sách được tổng hợp từ một nhánh code khác của
cùng dự án: nhánh đó cũng tách từ 3.4.0, có 3.4.1–3.4.6 riêng, nên một số sửa lỗi / tính năng bên đó chưa có ở bản của bạn.

Cách làm:
- **Kiểm tra trước từng mục trong code của bạn:** có thể bạn đã có rồi.
- **Viết đề xuất** thành file md dạng bảng: mục, đã có chưa, cách làm, file sửa, rủi ro. Rồi chờ tôi trả lời "Duyệt…".
- **Lỗi rõ ràng ở nhóm A:** xác nhận có thật trong code thì sửa luôn.
- **Không build** khi tôi chưa bảo. Bản tiếp theo là **3.4.11**, không ghi đè map cũ.
- Trả lời tôi bằng tiếng Việt.

## A. Lỗi cần kiểm tra (có trong 3.4.0, bản 3.4.10 vẫn còn)
1. **`Ext_OnKill` không bao giờ chạy.**
   - Lỗi: trong phần nối trigger (`Mega_Init`), `Ext_OnKill` được gắn vào **cùng trigger chết** với `League_OnDeath`, bằng 2 lệnh
     `TriggerAddCondition`. Điều kiện đầu trả về false thì điều kiện sau bị bỏ qua.
   - Hậu quả: Amulet Coin và mọi hiệu ứng khi hạ quái không có tác dụng.
   - Sửa: tạo trigger chết riêng cho `Ext_OnKill`.
2. **Người thách đấu tiến hóa giữa trận gym làm gym bị reset.**
   - Lỗi: Pokémon lên cấp nhờ XP rồi tiến hóa, `Mega_SafeReplace` thay unit mới. `Gym_Hero[g]` / `League_Unit` vẫn trỏ vào
     unit cũ đã bị xóa, nên gym coi như người chơi đã rời trận.
   - Sửa trong `Mega_SafeReplace`:
     - trỏ lại `Gym_Hero[i]` và `League_Unit` sang unit mới;
     - **không bao giờ thay** Pokémon của gym (đánh dấu bằng `Mega_HT` key 33 khi tạo);
     - chép cả key Shiny 123 / 124 sang unit mới.
3. **Shop có thể không xuất hiện hoặc nằm sai chỗ.**
   - Lỗi: `Ext_PlaceShops` / `Ext_ShopSpot` lấy ô trống đi được đầu tiên gần Mega Shop. Người chơi bản 3.4.0 / 3.4.1 không tìm
     thấy Battle Shop / Item Shop.
   - Sửa: đặt cố định ở (±5696, ±288) và (±5392, ±288), giữa hàng shop trên và hàng Mega Shop, hai bên lối từ Poke Center
     ra cửa. Hoặc làm mục B4 (NPC bán item).
4. **Phím Q ra chiêu của ô E / W:** bản 3.4.10 (nút Channel + ability ẩn) có lẽ đã sửa. Chỉ cần xác nhận lại.

## B. Tính năng của nhánh kia (cần duyệt)
1. **Độ khó riêng cho từng gym.** Người chơi lv30 không đánh nổi gym 1–2, mỗi ải 6 con.

   | Gym | Máu | Sát thương | Tỉ lệ dùng skill (AI) | Đánh nhanh x1,7 |
   |---|---|---|---|---|
   | 1 | x0,35 | x0,45 | 0,25 | không |
   | 2 | x0,45 | x0,55 | 0,25 | không |
   | 3 | x0,70 | x0,75 | 0,45 | không |
   | 4 | x0,85 | x0,85 | 0,45 | không |
   | 5–8, Elite Four | x1,0 | x1,0 | 0,6 | có |
2. **Lệnh `-gym`:** in trạng thái gym của mình (ải mấy / 6, Pokémon hiện tại còn sống không, ai đang thách đấu). Dùng để
   báo lỗi gym kẹt.
3. **Item hệ đủ 18 hệ:**
   - thêm Soft Sand (Ground), Pixie Plate (Fairy) nếu chưa có;
   - Pokémon tiến hóa bằng item của hệ khác được mua item đó dù khác hệ (Onix / Scyther + Metal Coat).
4. **Một NPC bán item, mở danh sách dạng dialog,** thay cho 2 nhà Battle Shop / Item Shop:
   - dialog hiện giá, vàng đang có, số item chiến đấu đang giữ (x / 3);
   - NPC dùng hình Goblin Merchant.
5. **Item mới:**
   - Shell Bell (3000): hồi 10% sát thương gây ra.
   - Bright Powder (3000): 10% đòn nhận vào không gây sát thương (né thật).
   - Wise Glasses (3500): chiêu +10% sát thương.
   - Oran Berry (150): máu dưới 30% thì hồi 20% máu tối đa, rồi mất item.
   - Quick Claw (3500): mỗi đòn đánh thường có 15% làm chiêu đầu tiên đang hồi chiêu hồi xong ngay.
   - Weakness Policy (3500): bị đánh bằng chiêu khắc hệ thì +30% sát thương trong 10 giây.
   - Life Orb giảm từ +30% xuống +25%.
6. **Giao diện:**
   - mỗi người chơi một dòng thông báo: thông báo mới thay dòng cũ (`ClearTextMessages` chỉ chạy cho người đó);
   - nhãn trên mỗi gym: tên gym, độ khó (suy từ hệ số máu ở B1), "cleared by …";
   - icon trên minimap cho gym, NPC, cổng League;
   - báo trước 30 giây khi thời tiết sắp đổi;
   - đếm ngược khi Escape Rope / cổng đang hồi;
   - dialog học move hiện "đã học n / 4".
7. **Elite Four:** hồi máu và cho nghỉ 30 giây giữa hai Elite Four (trước trận đầu thì không).
8. **Đòn đánh thường:**
   - loài đánh vật lý (chỉ số gốc Attack ≥ Sp. Attack) mà đang bắn đạn thì đổi sang cận chiến: tầm 128, bỏ đạn. Nhánh kia
     đếm được 98 unit quái hoang / gym;
   - hợp với hiệu ứng lao tới mục tiêu của bạn.
9. **(Tùy chọn, hỏi tôi trước) Elite Four đấu trong phòng cũ của Darkrai:**
   - sơn lại nền, cổng vào ở mỗi căn cứ và cổng ra về đúng căn cứ, 5 tượng;
   - Darkrai thành huyền thoại ngẫu nhiên.

   Mục này đụng chỗ với cổng về thành trong phòng Darkrai mà bạn đã làm, nên cần tôi chọn.

## C. Kế hoạch lớn (viết đề xuất riêng từng mục, chờ duyệt)
1. **Công / thủ Vật lý và Phép** (tôi muốn làm mục này trước trong nhóm C).
   - **Move Vật lý:** hệ số chỉ số = STR / 50; giảm theo **Def** của mục tiêu.
   - **Move Đặc biệt:** hệ số = INT / 50 (thay cho "chỉ số lớn hơn / 50"); giảm theo **SpD**.
   - **Hệ số nhận chiêu** = 2 / (1 + thủ / 80), giới hạn x0,5–x1,5. Thủ 80 nhận đúng x1,0. Ví dụ:
     - Steelix (Def 200, SpD 65): x0,57 vật lý, x1,10 phép;
     - Blissey (Def 10, SpD 135): x1,5 vật lý, x0,74 phép.
   - **Dữ liệu:**
     - Def / SpD của mọi loài (hero, gym, quái hoang, huyền thoại) lấy từ chỉ số gốc PokeAPI, lưu vào `Ab_HT` theo loại unit;
     - chọn key chưa dùng: tránh 53 / 54, 99 / 100+, 299 / 300+ (danh sách TM), 699 / 700+ của bạn;
     - Mega dùng Def / SpD dạng Mega, Darmanitan Zen dùng dạng Zen.
   - **Loại của skill elite / gym:** Vật lý / Đặc biệt theo tên chiêu. Learned move đã có `Mv_Phys`.
   - **Item:**
     - Choice Band: đòn đánh thường và move Vật lý +35%;
     - Choice Specs: move Đặc biệt +35%;
     - Assault Vest: −25% chỉ với move Đặc biệt.
   - **Tooltip move:** ghi "Vật lý – theo STR, giảm theo Def" hoặc "Đặc biệt – theo INT, giảm theo SpD", số sát thương tính
     đúng chỉ số.
   - **Tự học move:** Pokémon thiên phép ưu tiên move Đặc biệt, thiên công ưu tiên move Vật lý.
   - **Lệnh `-stats`:** STR, INT, Def, SpD, hệ số nhận chiêu Vật lý / Phép.
   - **Mặc định:**
     - đòn đánh thường giữ theo chỉ số chính;
     - giáp giữ (Def + SpD) / 4.
   - **Cân bằng:**
     - in bảng ví dụ trước / sau cho vài cặp Pokémon, tính cả luật khắc hệ k của bạn (x0,5–x2);
     - giữ độ mạnh chung gần như cũ.
2. **Move buff / phòng thủ / gây bất lợi:**
   - bậc chỉ số −6..+6 cho công, thủ, công đặc biệt, tốc độ: mỗi bậc ±50% (tốc độ ±33%), có thời hạn;
   - các hàm `Bf_Add`, `Bf_Mult`, `Bf_Tick`; khiên chặn máu; hồi máu theo giây; giảm công / tốc độ địch;
   - khoảng 15 move status đầu tiên; AI quái biết dùng;
   - giới hạn tổng bậc để không chồng quá mạnh với Life Orb / Choice / Champion Aura.
3. **Dọn căn cứ:**
   - gom 6 khối shop thành hàng thẳng;
   - đưa NPC dạy move ra gần lối vào;
   - để cổng gym / cổng dịch chuyển ở góc riêng;
   - bỏ doodad thừa giữa đường;
   - lối từ Poke Center ra cửa phải luôn thông.
4. **Ý tưởng khác (chỉ cần liệt kê, chưa làm):** nhiệm vụ / truy nã, bảng điểm (multiboard), Nature, Raid Boss,
   Save / Load + Pokédex, trứng Pokémon, câu cá, sự kiện Team Rocket, Pokémon đi theo.

## Thứ tự gợi ý
A (sửa lỗi) → B1, B2 (gym) → C1 (công / thủ) → các mục B còn lại → C2, C3.

---
