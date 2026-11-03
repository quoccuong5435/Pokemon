# Pokemon Arena v2.0 — Phần 1: Buff Mega, quái theo bậc, bãi quái hồi, legend lv 100 (design)

Ngày: 2026-10-31 · Tiếp nối `2026-10-31-mega-evolution-design.md` · Build vẫn bằng `tools/build_v2.py`.
Đã kèm trong cùng bản build: sửa lỗi tiến hóa ra 2 con (`Mega_SafeReplace`) và hồi sinh 10 giây.

## A. Buff Mega

Thay bonus cố định (+30 điểm, ability `AMA0`–`AMAF`) bằng bonus theo % chỉ số hiện có, tính lúc bấm Mega:

- Mỗi thuộc tính X (STR/AGI/INT) với "điểm" p của Mega đó (bảng điểm cũ trong `mega_data.py`, tổng 30):
  `bonus_X = max(p, floor(GetHeroX(u, true) * p * 3 / 100))` → cộng vào chỉ số gốc bằng `SetHeroStr/Agi/Int`,
  lưu lại và trừ đúng số đó khi hết Mega.
- Sát thương: `bonus_dmg = floor(0.5 * (BlzGetUnitBaseDamage(u, 0) + max(STR, AGI, INT)))` cộng vào base damage, trả lại khi hết.
- Ability chung đổi số: `AMB1` giáp **+10**, `AMB2` tốc chạy **+80**, `AMB3` tốc đánh **+40%**.
- Bỏ 16 ability `AMAx` (không dùng nữa). Tooltip Mega Stone / Mega Evolve ghi số mới
  ("+60% STR, +15% AGI, +15% INT, +50% sát thương, +10 giáp, +80 tốc chạy, +40% tốc đánh").

## B. Quái hoang dã lên bậc mỗi 5 phút

- `Wild_Tier` bắt đầu 0, mỗi 300 giây +1, tối đa 10. Thông báo cho mọi người: "Wild Pokemon grew stronger! (Tier N)".
- "Quái hoang dã" = unit của Neutral Hostile thuộc loại wild: loại custom gốc `nmrm`/`nmrl`/`nmrr` có level ≤ 12 và tên
  không chứa `_Loc` (Caterpie, Metapod, Butterfree, Rattata, Raticate, Sandshrew, Sandslash, Ponyta, Rapidash, Shellder,
  Cloyster, Tentacool, Tentacruel, Pidgeotto, Pidgeot, Magikarp, Tauros, Primeape, Exeggutor), `nogl` (Machamp giữa map)
  và 30 loài mới. Không tính boss gym (lv 25–80), boss legend, quái canh khu legend, dummy, unit hiệu ứng.
  Các đợt quái theo giờ có sẵn của map (phút 5, 10…) giữ nguyên và cũng được tính là quái hoang dã.
- Mỗi 2 giây quét quái hoang dã của Neutral Hostile; con nào chưa áp bậc hiện tại thì áp (quái đặt sẵn, quái đợt,
  quái bãi hồi đều được xử lý giống nhau). Theo bậc t (m = 1 + 0,15·t):
  máu tối đa = máu gốc·m (giữ % máu), sát thương gốc = gốc·m, giáp = gốc + 2t, vàng thưởng = gốc·m.
  Giá trị gốc lưu theo unit lúc gặp lần đầu nên áp lại nhiều lần không bị cộng dồn.

## C. Bãi quái hồi + 30 loài mới

- Bãi = cụm quái hoang dã đặt sẵn lúc đầu game (khoảng cách < 600) tính từ `CreateUnit` của map gốc. Dữ liệu bãi
  (tâm x/y, số con, "sức" ban đầu) sinh sẵn bằng Python vào JASS. Lúc khởi tạo, mỗi quái đặt sẵn được gán vào bãi gần
  nhất. Quái của các đợt theo giờ không thuộc bãi nào (chết không hồi).
- Quái thuộc bãi chết hết → sau **60 giây** hồi lại cùng số con quanh tâm bãi (lệch ngẫu nhiên ≤ 150), loài chọn
  ngẫu nhiên trong các loài có sức = min(10, sức bãi + bậc) (nếu không có loài đúng sức thì lấy sức gần nhất thấp hơn).
- Sức bãi ban đầu theo level quái gốc: lv 1–4 → 1, 5–9 → 2, 10–14 → 3, 15–20 → 4, 21–27 → 5, 28–35 → 6,
  36–44 → 7, 45–55 → 8, 56–70 → 9, > 70 → 10.
- 30 loài mới `nW00`–`nW1D` (model + icon + texture lấy từ PKLegends, import vào `war3mapImported\Wild\`),
  3 loài mỗi sức:

| Sức | Loài | lv | Máu | Sát thương | Giáp | Vàng |
|-----|------|----|-----|------------|------|------|
| 1 | Hoothoot, Lotad, Diglett | 3 | 350 | 15 | 1 | 10 |
| 2 | Mareep, Houndour, Swinub | 7 | 900 | 45 | 2 | 20 |
| 3 | Sneasel, Misdreavus, Chinchou | 12 | 1500 | 80 | 4 | 30 |
| 4 | Noctowl, Flaaffy, Breloom | 18 | 2200 | 120 | 6 | 45 |
| 5 | Manectric, Piloswine, Vibrava | 24 | 3000 | 160 | 8 | 60 |
| 6 | Houndoom, Mismagius, Weavile | 32 | 4000 | 210 | 11 | 80 |
| 7 | Ampharos, Ludicolo, Flygon | 40 | 5500 | 270 | 14 | 100 |
| 8 | Mamoswine, Altaria, Absol | 50 | 7500 | 340 | 18 | 130 |
| 9 | Electivire, Magmortar, Rhyperior | 62 | 10000 | 420 | 22 | 160 |
| 10 | Snorlax, Lapras, Dusknoir | 75 | 13000 | 500 | 26 | 200 |

  Loài mới dựa trên object quái hoang dã có sẵn (`n00T`), đánh cận chiến (tầm 100); scale tính theo chiều cao model
  để cao khoảng 100 + 10·sức đơn vị. Các loài quái cũ trong bãi cũng nằm trong danh sách chọn theo sức của chúng.

## D. Boss legend lv 100

16 boss: `n001` Zapdos, `n00C` Articuno, `n00D` Moltres, `n00F` Darkrai, `n00G` Rayquaza, `n01I` Lugia, `n01J` Arceus,
`n01K` Regigigas, `n01L` Mew, `n01M`/`n037` Giratina, `n01N` Deoxys, `n01O` Mewtwo, `n033` Dialga, `n034` Palkia,
`n035` Celebi → `ulev` = 100, máu ×1,5, sát thương ×1,25, giáp +20 (sửa trong w3u). Không áp dụng bậc 5 phút.

## Kỹ thuật & kiểm tra

- Code JASS mới trong `tools/jass/mega.j` (prefix `Wild_`), dữ liệu bãi/loài sinh trong `inject.gen_data_init`.
- Trigger chết hiện có của module dùng chung: quái hoang dã chết → giảm đếm bãi, lên lịch hồi.
- Tick 0,25 giây hiện có: đếm thời gian bậc và lịch hồi bãi.
- Test Python: dữ liệu loài/bãi, object data (lv/máu legend, 30 loài mới, ability AMB), module qua `jasscheck`,
  map build đọc lại được, bảng hash còn chỗ trống.
- Test trong game do bạn: Mega mạnh rõ rệt, sau 5 phút có thông báo bậc, giết hết bãi 60 giây sau hồi loài khác,
  legend hiện lv 100.
