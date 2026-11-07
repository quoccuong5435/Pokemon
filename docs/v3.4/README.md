# Pokemon Arena v3.4 — tổng hợp

Cập nhật 2026-11-08. Gom mọi tài liệu của v3.4 (cả phần lúc đầu định làm v3.5) vào thư mục này.

## Các bản

| Bản | Trạng thái | Nội dung |
|---|---|---|
| 3.4.0 | **Đã build** 07/11 (`Pokemon Arena v3.4.0.w3x`, 105 MB) | Toàn bộ tính năng bên dưới |
| 3.4.1 | **Đã build** 08/11 (`Pokemon Arena v3.4.1.w3x`) | Sửa lỗi:<br>- tiến hóa giữa trận làm reset gym;<br>- người thứ 2 vào gym không được báo gì;<br>- phím Q ra chiêu của ô E/W;<br>- Amulet Coin không cộng vàng |
| 3.4.2 | Code xong, pjass 0 lỗi, **chưa build** | Sửa gym kẹt "3/6 không thấy quái", thêm lệnh `-gym`; Onix / Scyther mua được Metal Coat; Battle Shop / Item Shop đặt cố định giữa 2 hàng shop của căn cứ (bản 3.4.0/3.4.1 có thể không đặt được); item hệ đủ 18 hệ (thêm Soft Sand cho Ground, Pixie Plate cho Fairy); **Elite Four chuyển vào phòng của Darkrai** (nền mới, cổng vào / ra, tượng), Darkrai thành huyền thoại ngẫu nhiên; **gym 1–4 dễ hơn** (máu x0,35 / x0,45 / x0,70 / x0,85, sát thương x0,45 / x0,55 / x0,75 / x0,85, không đánh nhanh x1,7, ít dùng skill hơn) |

Tất cả build từ `Pokemon Arena v3.3.3.w3x`, vì mã nguồn của 3.3.x không còn. Cách build ở cuối file.

## Có gì trong v3.4

### Gym, Elite Four
- **Đội 6 con:**
  - chọn lúc bắt đầu: 6 dòng tiến hóa khác nhau, form đúng theo level (lv35 Charmeleon, lv36 Charizard);
  - level: con 1–5 thấp hơn người thách đấu 5..1 cấp, con 6 bằng level người thách đấu;
  - con 6 luôn có hệ khắc bạn và dùng chiêu của hệ đó.
- **Độ khó theo gym** (từ 3.4.2): gym 1–4 có máu, sát thương và tỉ lệ dùng skill thấp hơn, không đánh nhanh x1,7. Gym 5–8 và Elite Four giữ nguyên. Bảng hệ số nằm ở `analysis/patch_gym_difficulty.py`, dữ liệu tạo trong `extras.py`.
- **Vào gym:** được hồi đầy máu và mana. Thua thì đấu lại ngay; clear xong chỉ người vừa clear chờ 5 giây.
- **Elite Four + Champion** (đủ 8 huy hiệu: bước vào vòng sân, hoặc gõ `-league`):
  - Will (Psychic), Koga (Poison), Bruno (Fighting), Karen (Dark), Lance (Dragon); đội của Lance tự Mega khi còn 50% máu;
  - từ 3.4.2 đấu ở **phòng cũ của Darkrai** (góc tây):
    - nền mới: sân tròn đá trắng viền đá đen, lối đi lát gạch, sảnh; 5 tượng đá (Espeon, Weezing, Machamp, Umbreon, Dragonite);
    - **cổng vào** ở mỗi căn cứ (cạnh Item Shop) và item "Pokemon League" ở shop Haunt Legendary; **cổng ra** ở sảnh về đúng căn cứ của mình;
    - xem trước: `league_preview.png`. Bản 3.4.0 / 3.4.1 đấu ở sân gym 8;
  - thắng được danh hiệu **[Champion]**: +15% STR/AGI/INT, Champion Aura (đồng minh trong 800 gây thêm 10% và nhận ít hơn 10% sát thương), 10000 vàng, Mega Ring, tỉ lệ shiny 1/20.
- Chi tiết: `1-ability.md` (phần cuối) và `3-item-league-tinh-nang.md`.

### Chiến đấu
- **Tốc độ đánh:** Pokémon của người chơi đánh nhanh gấp 1,7 lần.
- **Khắc hệ theo hệ của chiêu:** x2 / x0,5 / x0,25 (miễn nhiễm vẫn nhận 25%), có chữ "Super effective!".
  - Khi đang Mega, khắc hệ dùng hệ Mega; Darmanitan ở Zen Mode là Fire/Psychic.
- **73 Ability:** làm lại 68 cái cũ, thêm Super Luck, Strong Jaw, Solar Power, Skill Link, Zen Mode. 21 Pokémon trước đây chưa có Ability và 3 Pokémon mới đã được gán Ability. Chi tiết: `1-ability.md`.
- **Elite, Pokémon gym và huyền thoại dùng 5 skill theo hệ.** Trước đây AI quái không bao giờ dùng skill hero nên quái luôn đầy mana.
- **Mỗi Pokémon giữ tối đa 1 move cho mỗi loại skill gốc** (từ 3.4.1), để nút nào ra đúng chiêu nút đó.
- Cách tính sát thương chiêu và bảng 319 move: `5-sat-thuong-chieu.md`.

### Pokémon, Mega, quái hoang
- **8 Mega mới**, bán đá ở Mega Shop: Slowbro, Sharpedo, Ampharos, Houndoom, Aerodactyl, Manectric, Heracross, Altaria.
- **Pokémon mới:** Meganium (Bayleef lv32), Porygon2 (Porygon lv50), Latias & Latios (huyền thoại ngẫu nhiên, Soul rơi 50%).
- **Darmanitan Zen Mode.**
- **5 Mega không có model riêng** (Beedrill, Kangaskhan, Mewtwo X/Y, Rayquaza): to hơn, đổi màu, có hào quang. Muốn có model thật thì đặt file vào `mega_models/` (tên file ghi trong CLAUDE.md).
- **Quái hoang:**
  - thêm 211 loài, mỗi loài có Soul riêng (chỉ elite rơi, 20%); máu theo tier (elite máu và sát thương x1,6);
  - khi tier tăng, quái tiến hóa lên form tiếp theo của chính nó;
  - elite của loài có Mega có 25% ở dạng Mega và 5% rơi đá Mega;
  - Mewtwo và Rayquaza ở chỗ cố định Mega khi còn 50% máu.
  - Darkrai (từ 3.4.2) không còn ở phòng riêng: thành huyền thoại ngẫu nhiên (Soul 50%); Darkrai ở phút 31 của v1.8 vẫn giữ.
- Chi tiết: `2-mega-form-quai-hoang.md`.

### Item, shop, khác
- **Battle Shop (12 item cầm theo)** và **Item Shop (9 item)** ở hai căn cứ, giữa hàng shop trên và hàng Mega Shop, hai bên lối đi từ Poke Center ra cửa (từ 3.4.2). Mỗi Pokémon cầm tối đa 3 item chiến đấu.
- **Item hệ cho cả 18 hệ** (từ 3.4.2): Soft Sand (Ground) ở Super Mart 1, Pixie Plate (Fairy) ở Super Mart 2.
- **Đá tiến hóa:** 8 nhánh của Eevee và đá cho các loài khác. Pokémon tiến hóa bằng item hệ khác được mua item đó dù khác hệ (Onix / Scyther + Metal Coat, từ 3.4.2).
- **Shiny 1/100** khi pick, `-random` hoặc dùng Soul: đổi màu, +10% chỉ số, báo cả map.
- **Thời tiết đổi mỗi 5 phút:** mưa, nắng, bão cát, mưa đá.
- **Icon chiêu khớp tên chiêu:** 278 move theo tên, 41 move theo hệ. Bảng: `4-icon-chieu.md`.
- Chi tiết: `3-item-league-tinh-nang.md`.

### Lệnh chat mới
`-league` (Elite Four), `-gym` (trạng thái gym, từ 3.4.2).

## Đang chờ bạn
- **Build 3.4.2.**
- **Duyệt `6-de-xuat-hieu-ung-chieu.md`:**
  - 106 move cận chiến thôi là đạn bay;
  - 81 move có đạn riêng theo hệ, 66 move có hiệu ứng diện rộng;
  - model lấy từ PKLegends 3.2, khoảng 1,5 MB.
- Ý tưởng tiếp theo (chưa có đề xuất chi tiết): nhiệm vụ / truy nã, bảng điểm, Nature, Raid Boss, Save/Load + Pokédex.
- Tải map lên Google Drive: cần kết nối extension Claude in Chrome.

## Chưa kiểm tra được trong game
- Mã hiệu ứng thời tiết ('RAhr', 'LRaa', 'WOcw', 'SNbs').
- Chỗ đặt Battle Shop / Item Shop: chỗ trống đầu tiên đi lại được cạnh Mega Shop.
- Hình Mega của elite / huyền thoại.
- Bản sửa gym 3.4.2 (chưa build): nếu gym còn kẹt, gõ `-gym` và gửi lại kết quả.
- Phòng League (3.4.2): cổng vào / ra, tượng, chữ nổi tên các Elite Four, nền mới.

## Các file trong thư mục
| File | Nội dung | Ghi chú |
|---|---|---|
| `1-ability.md` | 68 Ability làm lại (bản đề xuất đã duyệt), 21 Pokémon chưa có Ability, các thay đổi gym / tốc đánh / khắc hệ | viết tay |
| `2-mega-form-quai-hoang.md` | 8 Mega, form mới, 211 loài quái hoang (khoảng bậc từng loài) | viết tay |
| `3-item-league-tinh-nang.md` | item, Elite Four, Shiny, thời tiết, đá tiến hóa, elite / huyền thoại Mega (lúc đầu là đề xuất v3.5) | viết tay |
| `4-icon-chieu.md` | icon của 319 move | `apply.py` tự tạo |
| `5-sat-thuong-chieu.md` | sát thương của 319 move, move của từng Pokémon | `analysis/move_damage_doc.py` |
| `6-de-xuat-hieu-ung-chieu.md` | đề xuất hiệu ứng move mới | `analysis/effects_plan.py`, chờ duyệt |

## Cách build (cho lần sau)
Chạy trong `_PokemonArena2.0_work`:
1. `python -I tools/v34/extract_base.py`: chỉ cần sau khi clone lại; tạo file gốc từ map v3.3.3.
2. Sửa `tools/v34/version.txt`: mỗi bản một số mới, không ghi đè bản cũ.
3. `python -I tools/v34/apply.py`, rồi `python -I tools/v34/check.py` (pjass phải báo 0 lỗi).
4. `python -I tools/v34/build_v34.py --dry-run`, rồi `python -I tools/v34/build_v34.py`.
