# Pokemon Arena v2.0 — Mega Evolution (design)

Ngày: 2026-10-31 · Map gốc: `Pokemon Arena v1.8.w3x` (tác giả Dinh Hai Ha) · Kết quả: `Pokemon Arena v2.0.w3x`

## Mục tiêu

Nâng map lên v2.0 và thêm hệ thống Mega Evolution để chơi với bạn bè trên Warcraft III Reforged 1.36.1.
Thành công = map mới mở được trên 1.36.1, mua Mega Stone, Pokemon dạng cuối bấm "Mega Evolve" thì đổi model/chỉ số
trong 60 giây rồi trở lại bình thường, không làm hỏng các cơ chế cũ (tiến hóa, giới hạn item theo hệ, hồi sinh).

## Ràng buộc

- File `Pokemon Arena v1.8.w3x` không bị sửa. Mọi thay đổi ra file mới.
- Map gốc bị optimize (không có `war3map.wtg`, object data item/ability nằm trong SLK). Không mở bằng World Editor;
  mọi thay đổi làm bằng tool Python trong `_PokemonArena2.0_work/tools`.
- Dùng native Reforged (`BlzSetUnitSkin`, `BlzStartUnitAbilityCooldown`, …) → map v2.0 cần Reforged 1.32+.
- Định dạng map giữ nguyên (w3i v25, w3u v2, SLK) — chỉ thêm dữ liệu.

## Gameplay

### Danh sách Mega (16 dạng)

| # | Mega | Unit gốc | Viên đá (giá) | Model | Bonus STR/AGI/INT |
|---|------|----------|---------------|-------|-------------------|
| 0 | Mega Venusaur | E002 | Venusaurite (5000) | PKL `MegaBisaflor` | 15/5/10 |
| 1 | Mega Charizard X | E00E | Charizardite X (5000) | PKL `MegaGlurakX` | 20/5/5 |
| 2 | Mega Charizard Y | E00E | Charizardite Y (5000) | PKL `MegaGlurakY` | 5/5/20 |
| 3 | Mega Blastoise | E000 | Blastoisinite (5000) | PKL `MegaTurtok` | 10/0/20 |
| 4 | Mega Beedrill | E02K | Beedrillite (5000) | fallback (model gốc) | 10/20/0 |
| 5 | Mega Pidgeot | E00D | Pidgeotite (5000) | PKL `MegaTauboss` | 0/15/15 |
| 6 | Mega Alakazam | E00I | Alakazite (5000) | PKL `MegaSimsala` | 0/10/20 |
| 7 | Mega Gengar | E01G | Gengarite (5000) | PKL `MegaGengar` | 0/10/20 |
| 8 | Mega Kangaskhan | E02P | Kangaskhanite (5000) | model gốc + Kid (PKL `KidKangama`) | 15/10/5 |
| 9 | Mega Pinsir | E03W | Pinsirite (5000) | PKL `MegaPinsir` | 15/10/5 |
| 10 | Mega Gyarados | E03F | Gyaradosite (5000) | PKL `MegaGarados` | 20/0/10 |
| 11 | Mega Steelix | E03V | Steelixite (5000) | PKL `MegaSteelix` | 25/0/5 |
| 12 | Mega Scizor | E03M | Scizorite (5000) | PKL `MegaScherox` | 20/5/5 |
| 13 | Mega Mewtwo X | E026 | Mewtwonite X (7000) | fallback | 25/5/0 |
| 14 | Mega Mewtwo Y | E026 | Mewtwonite Y (7000) | fallback | 5/5/20 |
| 15 | Mega Rayquaza | E029 | Meteorite (7000) | fallback | 10/10/10 |

Bonus chỉ số lấy theo mức tăng chỉ số của Mega trong game gốc (Atk → STR, SpA → INT, Spe → AGI), tổng 30 điểm.
Bonus chung cho mọi Mega: +5 giáp, +40 tốc chạy, +25% tốc đánh.

### Shop

Hai shop mới mỗi phe (dựa trên `ngme` như các shop cũ, model `pokemart.mdl` nhuộm tím, bất tử):

- Mega Shop I: Mega Stone #0–#7. Vị trí (-5248, 384) hướng 0° và (5248, 384) hướng 180°.
- Mega Shop II: Mega Stone #8–#15. Vị trí (-5248, -384) hướng 0° và (5248, -384) hướng 180°.
- Hai vị trí này nằm giữa Poke Mart (±5248, 0) và Waygate/Haunt Legendary (±5120, ±640), đối xứng như shop cũ.
  Shop tạo bằng `CreateUnit` cho `Player(PLAYER_NEUTRAL_PASSIVE)` trong `Mega_Init`.

Mega Stone: class Permanent, không có ability, bán lại được, chỉ một unit cầm (không stack).

### Luồng Mega

1. Pokemon (hero) **đúng unit gốc** đang cầm **đúng viên đá** → được thêm ability "Mega Evolve" tương ứng (16 ability,
   mỗi cái có icon/tooltip riêng). Bỏ đá → ability bị gỡ. Charizard/Mewtwo cầm cả X và Y → có cả 2 nút.
2. Bấm "Mega Evolve" (không mục tiêu, 0 mana, hồi chiêu 150 giây): hiệu ứng biến hình, rồi trong **60 giây**:
   - đổi skin sang unit skin Mega (model + icon), đổi scale/tint, đổi tên hero thành "Mega …";
   - thêm ability ẩn: bonus chỉ số riêng + bonus chung;
   - Mega Kangaskhan: tạo "Kangaskhan Kid" (locust, bất tử) đi theo; mỗi đòn đánh của mẹ (tối đa 1 lần/0,5 giây)
     con đánh phụ thêm 25% (sát thương gốc + STR), cùng attack type của mẹ.
   - Pokemon có 2 nút X/Y: nút còn lại cũng vào hồi chiêu.
3. Hết 60 giây, hoặc chết → trở về như cũ (skin gốc, scale/tint gốc, tên gốc, gỡ bonus, xóa Kid).
4. Hồi chiêu lưu theo unit; bỏ đá rồi nhặt lại thì nút được thêm lại với hồi chiêu còn lại (không reset).
5. Thông báo cho mọi người chơi: "<Tên người chơi>'s Charizard Mega Evolved into Mega Charizard X!".

### Hiển thị khác

- Quest "Mega Evolution" (hướng dẫn + danh sách đá + credit model).
- Tên map: `Pokemon Arena v2.0` (w3i + `SetMapName`), mô tả map nhắc tới Mega Evolution.

## Kỹ thuật

### Asset

- Model PKL được import vào `war3mapImported\Mega\<Tên>.mdx` (+ `_portrait.mdx` nếu có). Đường dẫn texture trong
  chunk `TEXS` được sửa thành `war3mapImported\Mega\<tên texture>` để không đụng file cũ của Arena.
- Icon: `ReplaceableTextures\CommandButtons\BTNMega*.blp` và bản `DISBTN` tương ứng (tạo bản xám nếu PKL thiếu).
- Thư mục `mega_models/` cho phép thay model sau này: file `<Key>.mdx` + texture cùng thư mục sẽ được ưu tiên
  hơn model PKL/fallback khi build. Key = `MegaVenusaur`, `MegaCharizardX`, … (xem bảng).
- Fallback (không có model): skin = model gốc, scale ×1.25, tint riêng, gắn thêm hiệu ứng hào quang.

### Object data (ID mới, đã kiểm không trùng)

- Unit (w3u): 16 unit skin `hM00`–`hM0F`, Kid `hMK0`, shop `nMS1`, `nMS2`.
- Item (ItemData.slk + ItemFunc.txt): `IM00`–`IM0F`.
- Ability (AbilityData.slk + CampaignAbilityStrings.txt): Mega Evolve `AM00`–`AM0F` (Channel, order riêng không
  trùng ability có sẵn), bonus chỉ số `AMA0`–`AMAF` (Attribute Bonus), bonus chung `AMB1` giáp, `AMB2` tốc chạy,
  `AMB3` tốc đánh.

### Script

- Một khối JASS mới (`mega.j`) chèn vào `scripts\war3map.j`: biến global trước `endglobals`, các hàm `Mega_*` trước
  `function main`, và `call Mega_Init()` ở cuối `main`.
- Trạng thái theo unit lưu trong hashtable riêng; một timer 0,25 giây quản lý: thêm/gỡ nút theo đá, hết giờ Mega,
  Kid đi theo. Trigger: cast (`EVENT_PLAYER_UNIT_SPELL_EFFECT`), chết, bị tấn công (cho Kid).
- Không sửa code cũ ngoài `SetMapName` và dòng gọi `Mega_Init`.

### Build

`tools/build_v2.py`: đọc map 1.8 → áp dụng thay đổi → ghi `Pokemon Arena v2.0.w3x` (giữ nguyên block cũ, thêm block
mới, ghi lại hash/block table, cập nhật `(listfile)`). Chạy lại được bất cứ lúc nào (ví dụ khi có model mới).

## Kiểm tra

- Tool tự kiểm: đọc lại map vừa build, mọi file tham chiếu (model, texture, icon) đều tồn tại; object data parse lại
  được; JASS thêm vào qua bộ kiểm cú pháp/tên hàm.
- Chạy map bằng Warcraft III 1.36.1 trên máy (nếu bạn đồng ý) để xác nhận script load không lỗi.
- Bạn test gameplay: mua đá, Mega, hết giờ, chết khi Mega, Kangaskhan Kid, bỏ/nhặt đá.

## Ngoài phạm vi

Mega cho Pokemon không chơi được (Lucario, Tyranitar, Aerodactyl…), Primal/Gigantamax, chỉnh lại cân bằng skill cũ.
