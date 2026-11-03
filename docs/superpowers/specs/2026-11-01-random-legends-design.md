# Pokemon Arena v2.5 — legend ngẫu nhiên + Soul từ quái hoang dã (design)

Ngày: 2026-11-01. Yêu cầu: legend xuất hiện ngẫu nhiên, lv 100, 50% rớt Soul, chỉ Pokemon lv 100 mới gây sát thương;
quái hoang dã 0,5% rớt Soul. Chốt với bạn: 50% rớt Soul; điều kiện lv 100 chỉ cho legend ngẫu nhiên; mỗi 5 phút
(tối đa 2 con cùng lúc).

## Legend ngẫu nhiên

- 14 loại (ID mới `nL00`–`nL0D`, sao chép boss legend đã lên lv 100 trong v2.1): Articuno n00C/I01C, Moltres n00D/I01D,
  Lugia n01I/I01E, Darkrai n00F/I01F, Mew n01L/I01G, Regigigas n01K/I01H, Mewtwo n01O/I01I, Giratina n01M/I01J,
  Deoxys n01N/I01K, Arceus n01J/I01L, Rayquaza n00G/I01M, Zapdos n001/I01Q, Dialga n033/I01V, Palkia n034/I01W
  (boss gốc / Soul). Tên hiển thị "Wild <Tên>".
- Từ phút 5, mỗi 5 phút: nếu đang có < 2 legend ngẫu nhiên thì sinh 1 con loại ngẫu nhiên ở tâm một bãi quái ngẫu nhiên
  (chỗ đi được), thông báo "A wild <Tên> (Lv 100) appeared!" và ping minimap 5 giây.
- Chỉ Pokemon lv 100 gây sát thương: sự kiện `EVENT_PLAYER_UNIT_DAMAGING`; mục tiêu là legend ngẫu nhiên và người gây
  sát thương (kể cả qua dummy của chiêu) có hero cao nhất < lv 100 → `BlzSetEventDamage(0)`, nhắc tối đa 1 lần/3 giây.
- Chết: 50% rớt Soul của chính nó; 50% rớt item an ủi như boss gốc (`I00B`, `I001`, `I000`). Soul dùng ở vòng tròn
  giữa map như cũ.

## Quái hoang dã rớt Soul

- Mỗi quái hoang dã chết: 0,5% rớt 1 Soul ngẫu nhiên trong 14 Soul trên, kèm thông báo cho mọi người.

## Khác

- Quest "Random Legends" giải thích luật. Phiên bản 2.5.

## Kiểm tra

Test Python: bảng 14 legend (ID không trùng v1.8, Soul đúng), object clone lv 100, module qua `jasscheck` + các hằng
(300 giây, tối đa 2, 50%, 0,5%, lv 100), build v2.5. Bạn test trong game: phút 5 có legend, lv < 100 đánh ra 0,
lv 100 đánh được, rớt Soul ~ một nửa số lần.
