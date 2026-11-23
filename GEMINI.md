# GEMINI.md: luật làm việc cho map Pokemon Arena

Đọc hết file này trước khi làm bất cứ việc gì. Luật ở đây là bắt buộc, trừ khi người dùng nói khác trong chat.
Nếu luật mâu thuẫn với yêu cầu của người dùng, hỏi lại một câu rồi làm theo câu trả lời.

## 1. Dự án là gì
- Mod map Warcraft III Reforged "Pokemon Arena" (tác giả gốc Dinh Hai Ha). Thư mục làm việc: `_PokemonArena2.0_work`,
  nằm trong `Documents\Warcraft III\Maps\Download`. Các file map `.w3x` nằm ở thư mục cha (`..\`).
- Map không sửa bằng World Editor. Mọi thứ do Python sinh ra: đọc map gốc, vá script `war3map.j` và dữ liệu object,
  ghi ra file `.w3x` mới.
- Người dùng nói tiếng Việt. **Luôn trả lời bằng tiếng Việt**, ngắn gọn, nói rõ cái gì đã làm và cái gì chưa kiểm tra.

## 2. Bản đang làm (cập nhật 2026-11-22)
- Dòng hiện tại là **`v4.2x`**, nối tiếp v4.1.2-ver2 → v4.1.3 (c … k) → v4.2. Bản mới nhất đã build: `Pokemon Arena v4.2a.w3x`.
- Bản đang code: **v4.2b** (`tools/v412/build_v42b.py`, test `tests/test_v42b.py`). Chưa có file map v4.2b.
- Mỗi bản có một script build riêng `tools/v412/build_v42X.py`. Script đọc map của bản liền trước (`BASE_MAP`), vá script và dữ liệu,
  rồi ghi map mới (`NAME`, `OUT_MAP`). Mỗi bản có test riêng `tests/test_v42X.py`.
  Bản mới (ví dụ v4.2c) = chép script build và test của bản liền trước, đổi `BASE_MAP` sang map vừa build, đổi `NAME`, sửa phần thay đổi.
  Xem `build_v42b.py` để biết mẫu.
- Script đã tách sẵn để đọc: `analysis/jass_ref/_tmp_v42a_war3map.j` (4.2a) và `_tmp_v42b_war3map.j` (4.2b đang code).
  Tài liệu cơ chế và danh sách hero: `docs/GAME_LOGIC_AND_HERO_ROSTER_v42b.md`. Báo cáo lỗi rơi đồ của 4.2a: `docs/so-tay-v4.2a.html`.
- Bản chưa ai chơi thử thì nói rõ "chưa chơi thử". Không có công cụ chạy game, người dùng tự chơi rồi báo lỗi.
- Các dòng khác (3.4.x, 4.3.x) là lịch sử. Không trộn code giữa các dòng khi chưa được yêu cầu.
  Tính năng của dòng 3.4.16 / 4.3 cần "engine 3.4.16" nên không dán thẳng vào dòng v4.2x được.

## 3. Việc cấm làm
1. **Không build map mới khi người dùng chưa nói "build".** Được phép sửa code, chạy test, chạy pjass, chạy `--dry-run`.
2. **Không ghi đè, không xóa file map cũ.** Mỗi bản là một file mới với tên mới. Build script phải tự từ chối nếu file đã tồn tại.
   Chỉ xóa map cũ khi người dùng bảo "clear / dọn" và đã xem danh sách sẽ xóa.
3. **Không sửa `Pokemon Arena v1.8.w3x`** và các map nguồn (Pokemon World, PKLegends...). Chỉ đọc.
4. **Không commit, không push git** khi người dùng chưa bảo.
5. **Không viết tính năng "đã có" nếu chưa kiểm tra trong script hoặc dữ liệu map.** Đã từng có ghi chú build nói "9 move
   debuff mới" nhưng map không có. Trước khi nói tính năng có trong map, grep script hoặc đọc dữ liệu của chính file `.w3x` đó.
6. Không đưa tên, email hay thông tin cá nhân của người dùng vào dịch vụ bên ngoài.

## 4. Quy trình mỗi lần sửa
1. Đọc code liên quan trước khi sửa. Nếu là tính năng mới hoặc đổi cân bằng lớn: viết đề xuất ngắn (bảng hoặc danh sách) và
   chờ người dùng duyệt. Lỗi rõ ràng thì sửa luôn.
2. Sửa trong `tools/`, không sửa tay file đã sinh ra.
3. Chạy test: `python -I -m pytest tests -q` (hoặc chỉ file test của bản đang làm).
4. Kiểm tra script JASS bằng pjass: map phải **0 lỗi**, nếu không lobby báo "map unavailable or corrupted".
   Dùng `python -I analysis/pjass_map.py <map.w3x>` (hoặc `tools/v34/check.py` cho script rời).
5. Chạy `--dry-run` của script build để xem danh sách file sẽ ghi.
6. Khi người dùng nói "build": chạy build, đưa ra tên file, dung lượng, và nói rõ chưa chơi thử.
   Nếu file đang bị khóa vì game mở, build với `--out out\x.w3x` rồi báo người dùng chép sau khi đóng game.
7. Cuối việc: nói ngắn gọn đã đổi gì, đã kiểm tra bằng gì, còn chưa kiểm tra gì.

## 5. Cách vá script (quan trọng nhất)
- Script `war3map.j` được xử lý như text `latin-1`. Vá bằng hàm thay thế theo **đoạn mốc chính xác** (anchor): đoạn mốc phải
  xuất hiện đúng 1 lần, nếu không phải báo lỗi và dừng (xem `_rep` trong `tools/v412/boss_buff.py`). Không thay mò bằng regex rộng.
- Xuống dòng: script v4.1.2 có chỗ dùng `\r\n`, có chỗ `\r\r\n`, phần v1.8 có chỗ chỉ dùng `\r`. Không xóa hay đổi `\r`
  của đoạn không liên quan. Module cần LF thì bọc bằng hàm `lf(...)` như trong `build_ver2.py`.
- Chỉ dùng native có trong `common.j` / `blizzard.j` (thư mục `analysis/jass_ref/`). Không dùng `UnitAlive`, dùng `GetWidgetLife(u) > 0.405`.
- Tên biến local trong JASS phải **dài và riêng** (ví dụ `lootFactorValue`). Tên 2 chữ cái (`pa`, `cc`, `p1`) trùng hàm của v1.8.
- `code` là từ khóa kiểu của JASS, không đặt tên biến là `code`.
- Hàm phải khai báo **trước** chỗ gọi. Nhớ đúng thứ tự hàm trong file.
- Giới hạn số lệnh khi khởi tạo: khối dữ liệu lớn chia nhỏ, chạy bằng `ExecuteFunc`.
- Hashtable `PAX_Item_HT` khóa 130 là Max HP gốc của đồ. Không dùng lại khóa đang có. Kiểm tra trước khi thêm khóa mới.
- Id object (unit, ability, item) phải bắt đầu bằng chữ in hoa nếu là hero. Kiểm tra id chưa tồn tại trước khi tạo.

## 6. Cách viết file bằng công cụ
- Trong shell, heredoc làm mất dấu `\` (vd `\\` thành `\`). Code hoặc đường dẫn Windows có `\` phải ghi bằng công cụ ghi file,
  không dùng `python - <<EOF` hay `echo`.
- Python in tiếng Việt trên Windows dễ lỗi mã hóa. Chạy với `PYTHONIOENCODING=utf-8`.
- Chạy script Python bằng `python -I` (không nạp thư viện từ thư mục hiện tại).
- Ghi file map cũng như mọi file dữ liệu bằng `tools/mpq.py` (`MPQ.save_with`). Archive cần block dạng sector, WC3 không đọc được SINGLE_UNIT.

## 7. Luật nội dung game
- **Chữ trong game (thông báo, `-help`, tên move, tên Pokémon, ability, tooltip) giữ tiếng Anh.** Chỉ patch note và tài liệu viết tiếng Việt.
- Mỗi bản mới phải đổi chuỗi phiên bản trong script và `war3map.w3i` (xem `bump_version` trong `tools/v412/loot_balance.py`).
- Không làm gãy các tính năng đang có. Khi thêm gì, kiểm tra trong test rằng tính năng cũ vẫn còn:
  loot cân bằng theo bãi, soft cap Max HP loot, Charm, gym theo thứ tự và level, Dynamax, boss x20, `-repick` ngẫu nhiên,
  Form Orb / Paradox, event, thức tỉnh Hidden Power, Mythic Forge.
- Số liệu cân bằng (tỉ lệ rơi, giá, hệ số máu...) lấy từ code. Không đoán, không làm tròn trong tài liệu.
- Model và icon lấy từ map nguồn đã có trong máy. Không tự bịa đường dẫn texture. Kiểm tra file có trong archive trước khi dùng.
  Icon dạng BLP palette (như icon hệ `BTNPkmn*.blp`) cần decoder riêng, Pillow không đọc được trực tiếp.
- Đường dẫn trong dữ liệu object của WC3 dùng **một** dấu `\`. Lỗi gấp đôi dấu `\` từng làm icon hiện ô xanh.

## 8. Patch note và tài liệu
- Patch note chỉ mô tả **tính năng hiện có của bản đó**, không nói chuyện "gộp từ bản khác", không so sánh với bản cũ
  (trừ khi người dùng đòi bản changelog).
- Mỗi dòng phải kiểm tra được trong script hoặc dữ liệu. Chưa chắc thì ghi "chưa kiểm tra" hoặc bỏ.
- Viết cho người mới đọc: tiếng Việt thường ngày, tên Pokémon / move / lệnh giữ nguyên tiếng Anh, bỏ thuật ngữ nội bộ
  (tên hàm, khóa hashtable). Ví dụ số cụ thể thì ghi rõ là ví dụ.
- Bản patch note chia sẻ hiện tại là artifact HTML có tab, nguồn nằm trong thư mục scratchpad của phiên Claude. Nếu cần làm lại,
  tạo từ `analysis/patchnote/`.

## 9. Việc cần làm khi bắt đầu phiên mới
1. Đọc `CLAUDE.md`, `HANDOFF-v3.4.md` và `docs/v4.1.2-ver2c.md` (lịch sử các bản ver2).
2. Liệt kê map `Pokemon Arena v4.2*.w3x` đang có, xác định bản mới nhất.
3. Tóm tắt cho người dùng trong 5 dòng: bản mới nhất là gì, việc đang mở, rồi chờ người dùng giao việc.

## 10. Luật xếp Melee / Ranged cho hero (người dùng duyệt 2026-11-22)
Áp vào bản build kế tiếp của dòng PAX (hiện là 4.2b, `tools/v412/build_v42b.py`; nếu 4.2b đã build thì vào bản sau).
Luật 3.1 vẫn giữ: chưa nói "build" thì không build.

**Cách xếp.** Kết quả cho cả 360 hero đã tính sẵn trong `analysis/melee_ranged.json`, do `analysis/melee_ranged.py` sinh ra.
Bảng giải thích nằm ở `docs/so-tay-v4.2a.html`, mục Melee / Ranged.
1. Chênh = Sp.Atk − Attack. Dùng chỉ số gốc của loài từ PokeAPI. 28 Legend không có trong `tools/learnsets.json` được nhập tay trong script.
2. Chỉnh = round(40 × (số chiêu special / số chiêu gây sát thương − 0,5)). Chỉ tính khi có từ 4 chiêu gây sát thương; ít hơn thì Chỉnh = 0.
3. Điểm = Chênh + Chỉnh. Điểm ≥ +20 → Ranged (`R`), Điểm ≤ −20 → Melee (`M`), còn lại → Tầm trung (`H`).
4. Ra `R` mà stat chính là STR, hoặc ra `M` mà stat chính là INT, thì hạ về `H`.
- Không đổi ngưỡng, không xếp tay từng con khi người dùng chưa duyệt. Có hero mới thì chạy lại `analysis/melee_ranged.py`.
- Kết quả hiện tại: 144 M, 122 H, 94 R (R gồm 75 con tầm 500, 11 con 450, 8 con 600). 194 con đổi lớp, 318 con đổi tầm.

**Ghi vào `war3map.w3u`.** Cả 360 hero đều nhân bản từ `Emoo`, là hero đánh xa. Trong map 4.2a chỉ 2 con có `ua1w`, nên
hiện chưa hero nào được game tính là melee attacker.

| Lớp | `ua1r` (int) | `ua1w` (string) |
|---|---|---|
| M | 150 | `normal` |
| H | 300 | `missile` |
| R | 500; 450 nếu (Def + SpDef) / 2 ≥ 105; 600 nếu Sp.Atk ≥ 120 và (Def + SpDef) / 2 < 85 | `missile` |

- Build đọc `cls` và `rng` từ json rồi ghi `ua1r = rng`. Không tính lại công thức trong script build.
- Đặt `ua1w` cho đủ 360 con, không dựa vào giá trị mặc định của `Emoo`. Riêng Staryu `E04N` và Starmie `E04M` (cả hai là R) giữ `mbounce`.
- Đặt `uacq` (unreal) = max(`ua1r`, 600) để hero tự nhắm mục tiêu đủ xa.
- 8 con H hoặc R đang có `ua1m = ".mdl"` (đạn rỗng) phải được gán đạn thật: Exeggcute `E02U`, Exeggutor `E02W`, Magikarp `E03E`,
  Omanyte `E03Q`, Omastar `E03R`, Dialga `E04C`, Palkia `E04D`, Lucario `EN0J`. Lấy đường dẫn `Abilities\Weapons\...` của một hero
  cùng hệ chính đang có trong map. Không bịa đường dẫn mới.
- Dạng biến đổi lấy lớp và tầm của hero gốc. Gồm 48 unit clone từ `Emoo` (`hM00`..`hM0W`, `hM20`..`hM26`, `hZ00`, `hMPK`, `hMPG`, `hMLL`, `hMF4`,
  `hMF7`, `hMF8`, `hMF9`) và `E022`, `P07A`. Tìm hero gốc trong script (`Mega_SafeReplace`, bảng Mega). Không tìm được thì giữ nguyên
  và báo người dùng.

**Hệ quả phải ghi vào patch note.** Đã kiểm tra trong script 4.2a và 4.2b.
- Hero Melee trở thành melee attacker, nên hiệu ứng chạm bắt đầu có tác dụng với đòn đánh thường của họ:
  - Static, Flame Body, Poison Point: 30% gây trạng thái lên kẻ đánh (`Ab_InContact`).
  - Hard Stone phản 15% sát thương; Zapdos 30% gây tê liệt (`Fx_AfterHit`).
  - Trước bản này không hero nào kích hoạt các hiệu ứng trên.
- Rocky Helmet tính kẻ đánh có tầm ≤ 250 (`Ext_AfterHit`). Trước có 304 hero tầm ≤ 250; sau còn đúng 144 hero Melee. Không cần sửa code.
- Phần bù cho lớp Melee (máu, giáp, tốc chạy) chưa có số. Không tự thêm; viết bảng đề xuất rồi chờ người dùng duyệt.

**Kiểm tra trước khi báo xong.**
- Test trong file test của bản đó (vd `tests/test_v42b.py`):
  - Đủ 360 hero, mỗi lớp có `ua1r` và `ua1w` đúng bảng.
  - Đếm đúng 144 M / 122 H / 94 R.
  - 8 con kể trên không còn `.mdl`.
  - Dạng biến đổi cùng lớp với hero gốc.
- pjass 0 lỗi, rồi chạy `--dry-run`.

## 11. Sửa move / ability theo PokeAPI (người dùng duyệt 2026-11-22)
Không dùng accuracy và PP (người dùng đã quyết định). Code và test đã có sẵn, Gemini chỉ cần gắn vào bản build kế tiếp
của dòng PAX (cùng bản với mục 10):
- Trong script build, sau khi đọc `scripts\war3map.j`, gọi `script = move_ability_fix.patch(script)`
  (`tools/v412/move_ability_fix.py`). Hàm tự báo lỗi nếu mốc không khớp hoặc chạy hai lần. Không sửa tay dữ liệu move.
- Test: `python -I -m pytest tests/test_move_ability_fix.py -q`, sau đó pjass 0 lỗi.
- Hàm này sửa:
  - Confusion, Dynamic Punch, Hurricane, Psybeam, Water Pulse: tooltip ghi "x% confusion" nhưng trước đây không bao giờ
    gây rối. Thêm khóa move 9 (tỉ lệ rối) và đoạn đọc khóa này ngay trước chỗ tính khựng trong `Fx_AfterHit`.
  - 11 move thiếu hoặc sai hiệu ứng: Ancient Power, Bounce, Chilling Water, Facade, Freeze-Dry, Pounce, Rapid Spin,
    Scorching Sands, Sky Attack, Trailblaze, Venoshock. Tooltip được sửa theo.
  - Double Team: hệ Bug thành Normal.
  - 17 hero đổi sang ability thật của loài đã có code trong map (danh sách `ABILITIES` trong file).
- Dữ liệu nguồn: `tools/pokeapi/` (`moves.json`, `abilities.json`, `pokemon_abilities.json`, tải bằng `tools/pokeapi/fetch.py`).
  Báo cáo so sánh: `python -I analysis/move_ability_audit.py <script> analysis/move_ability_audit.json`.
- Hidden Ability (món Ability Patch 10.000 vàng): gọi thêm `script = hidden_ability.patch(script)`
  (`tools/v412/hidden_ability.py`, test `tests/test_hidden_ability.py`). Thứ tự gọi với `move_ability_fix` không quan trọng.
  - Mở Hidden Ability thì Pokemon chuyển hẳn sang ability đó, giữ nguyên khi tiến hóa. Mega và dạng Form vẫn dùng ability riêng.
  - Có hiệu lực cho 38 Hidden Ability đã có code (119 Pokemon). 56 Hidden Ability còn lại (218 Pokemon) chưa có code:
    shop từ chối bán và hoàn 10.000 vàng. Mua lần hai cho con đã mở cũng được hoàn tiền.
- Phần còn thiếu của mục này (56 Hidden Ability chưa có code, ability mặc định của hero) đã làm xong ở mục 12.

## 12. Rework toàn bộ ability (người dùng duyệt 2026-11-22, 3 vòng trên trang làm chung)
Code và test đã có sẵn. Gemini gắn vào bản build kế tiếp của dòng PAX, cùng đợt với mục 10 và 11.
- **Thứ tự gọi trong script build**, sau khi đọc `scripts\war3map.j`:
  `script = move_ability_fix.patch(script)` → `script = ability_rw.patch(script)` → `script = hidden_ability.patch(script)`.
  `hidden_ability` phải chạy sau `ability_rw`, vì nó đọc tên ability và bản làm lại phải thắng.
- **Dữ liệu object:** thêm nút thông tin cho 105 ability mới.
  - `strings = ability_rw.patch_objects(abil, strings)`, với `abil` là `slk.Slk` của `Units\AbilityData.slk` và
    `strings` là text của `Units\CampaignAbilityStrings.txt`.
  - Ghi lại cả hai file vào map.
  - Thiếu bước này thì ability vẫn chạy nhưng nút thông tin (ô 3,1) không hiện.
- **File:**
  - Module: `tools/v412/ability_rw.py`, tooltip tiếng Anh ở `ability_rw_text.py`, dữ liệu ở `ability_rw_data.json`.
  - JASS: `tools/v412/jass/ability_rw_early.j`, `_mid.j`, `_main.j`, `_data.j`.
  - Bản chốt: `analysis/ability_final.json`.
- **Test:** `python -I -m pytest tests/test_ability_rw.py tests/test_hidden_ability.py tests/test_move_ability_fix.py -q`,
  sau đó pjass 0 lỗi trên map đã build.
- **Nội dung:**
  - 105 ability chạy bằng số mới (`AB_RW_*`, từ 91 tới 195): 66 cái trước đây chưa có code và 39 cái làm lại. Số cũ vẫn giữ cho quái hoang, Mega và Form.
  - 5 ability đổi số ngay trong code cũ: Air Lock, Bad Dreams, Slow Start, Zen Mode, Magic Bounce.
  - 323 hero nhận ability mặc định đã duyệt. 37 Legend giữ nội tại riêng.
- **Lệnh thử trong game:** host chọn hero của mình, gõ `-abtest <tên ability>`. Gõ `-abtest off` để trả lại ability gốc.
  Bảng thử từng ability: `docs/ability-test-checklist.md`.
- **Không sửa tay số liệu ability trong script.** Muốn đổi cân bằng thì sửa file JASS / module rồi chạy lại test.

## 13. Kích thước model, đi bộ / bay, và model gây crash (người dùng yêu cầu 2026-11-22)
Lỗi đã gặp ở 4.2b (`gen14_expansion.py`):
- Pokemon giai đoạn cuối (`stage == 2`) được clone từ `E00E` (Charizard), giữ nguyên `umvt = hover`, `umvh = 180`.
  Vì vậy con đi bộ bị lơ lửng (Furret, Ariados, Quagsire, Forretress, Donphan, Miltank...), con bay thì bay quá cao (Ledian, Xatu...).
- Một số con bị quá to (Steelix 1.45, Feraligatr 1.50, Donphan 1.22) hoặc quá nhỏ so với con tiến hóa trước (Croconaw 1.05).

**Luật đi bộ / bay.** Mỗi khi clone unit từ một mẫu, luôn đặt lại `umvt` và `umvh` theo đúng con đó, không giữ của mẫu:

| Loại Pokemon | `umvt` | `umvh` |
|---|---|---|
| Không phải hệ Flying và không có Levitate | `foot` | 0 |
| Hệ Flying hoặc có Levitate (Ledian, Xatu, Skarmory, Gengar...) | `fly` | 60–80 |
| Legend bay lớn (Lugia, Ho-Oh, Rayquaza...) | `fly` | tối đa 100 |

**Luật kích thước (`usca`).**
- So với con tiến hóa trước: giai đoạn sau to hơn tối đa khoảng 1,25 lần. Không được nhỏ hơn con tiến hóa trước.
- Model gốc vốn đã to (Onix, Steelix, Wailord, Donphan, Snorlax...): giữ 0,90–1,00.
- Mọi `usca` trên 1,30 phải có lý do ghi trong code và người dùng xem trong game.
- Thấy con nào to choán màn hình thì giảm, đừng chờ lý do khác.
- Số người dùng đã chốt:

| Pokemon | `usca` | Ghi chú |
|---|---|---|
| #159 Croconaw | 1,20–1,25 | Hiện 1,05, nhỏ so với Totodile |
| #160 Feraligatr | 1,15–1,20 | Hiện 1,50, quá to |
| #208 Steelix | 0,90 | Hiện 1,45, choán màn hình như Onix trước đây |
| #241 Miltank | 0,90–1,00 | Kèm `umvt = foot`, `umvh = 0` |
| #232 Donphan | 0,95 | Hiện 1,22, kèm `umvt = foot`, `umvh = 0` |

**Luật model gây crash.**
- Không đưa vào map model 2.5D "billboard" tự sinh (các chunk `BONE/GEOS/MTLS/LAYS` do code tạo ra).
- WC3 Reforged crash ngay khi nạp model loại này: `-gen 3` crash ở #268 Cascoon, `-gen 4` crash ở #401 Kricketot.
- Hiện có 39 model như vậy: 21 của Gen 3 và 18 của Gen 4.
- Chỉ dùng model thật lấy từ map nguồn có trong máy. Pokemon chưa có model thật thì dùng tạm model thật của con gần giống nhất, hoặc chưa đưa con đó vào.
- Model mới phải được người dùng tạo thử trong game (ví dụ bằng `-gen <n>`) trước khi báo xong.

**Test bắt buộc trong file test của bản đó:**
- Không hero nào ngoài hệ Flying / Levitate có `umvh` > 0 hoặc `umvt` khác `foot`.
- Không hero nào có `umvh` > 100.
- Không hero nào có `usca` > 1,30, trừ danh sách ngoại lệ ghi trong test.
- Các số `usca` trong bảng trên đúng như đã chốt.

**Công cụ đo bắt buộc** (`tools/v412/model_size_check.py`): AI phải đo, không đoán kích thước.
- Sau mỗi lần build có thêm hoặc đổi Pokemon, chạy:
  `python -I tools/v412/model_size_check.py "../Pokemon Arena v4.2X.w3x" --md docs/hero-model-size-v4.2X.md`
- Cách công cụ đo:
  - Kích thước trên màn hình = max(chiều cao, 0,4 × chiều dài) của model (đọc từ file .mdx trong map) × `usca`.
  - Mục tiêu = 80 × (chiều cao thật / 0,4 m)^0,45, giữ trong khoảng 55–230. Chiều cao thật lấy từ PokeAPI, file
    `tools/pokeapi/pokemon_size.json` (tải lại bằng `tools/pokeapi/fetch_size.py`).
  - Trên 1,35 × mục tiêu là "quá to", dưới 0,7 × mục tiêu là "quá nhỏ". Công cụ ghi kèm scale đề xuất.
- Trước khi báo build xong:
  - Không còn dòng "lơ lửng sai", "bay quá cao", "khác số đã chốt".
  - Dòng "quá to" / "quá nhỏ" thì sửa theo scale đề xuất, hoặc ghi lý do giữ nguyên.
  - Dòng "model lạ" (model cao dưới 15 hoặc trên 800 đơn vị) thì kiểm tra model trước khi dùng.
- Số bạn đã chốt nằm trong `USER_SCALE` của công cụ. Thêm số mới thì sửa ở đó, không sửa tay trong map.
- Kết quả trên bản 4.2b: `docs/hero-model-size-v4.2b.md`. 567 hero, 233 bị đánh dấu: 87 quá to, 68 quá nhỏ,
  73 lơ lửng sai, 28 bay quá cao, 4 model lạ, 5 khác số đã chốt.

## 14. NPC học move và hỏi khi lên level (người dùng yêu cầu 2026-11-22)

Module `tools/v412/move_tutor.py` (JASS trong `tools/v412/jass/move_tutor_*.j`). Module `tools/v412/wild_mix.py` và `tools/v412/random_gen.py`. Đã viết, test và tích hợp hoàn chỉnh vào `build_v42b.py`.
- **NPC học move:** thay `Npc_Show` / `Npc_OnClick`. Bấm NPC (hoặc gõ `-moves`) ra menu chính gồm
  "Level-up moves", "TM/HM moves", "Forget a move", "Close".
  - Danh sách chỉ hiện move chưa biết, xếp mạnh trước: power, cộng 50% nếu cùng hệ với hero (ghi "STAB").
    Mỗi trang 9 move.
  - Bấm vào move: còn slot trống thì học luôn. Đủ 4 move thì hiện "Replace which move?" với 4 slot và nút Cancel.
  - Giá giữ nguyên: move theo level dùng `Npc_LearnCost`, TM dùng `PAX_Npc_TMCost` (3k–15k).
- **Lên level:** move mới vẫn tự vào slot trống. Đủ 4 move thì người chơi thật được hỏi
  "<hero> wants to learn <move>. Forget which move?", chọn 1 trong 4 slot hoặc Skip.
  - Bỏ qua thì vẫn học lại được ở NPC.
  - Còn địch trong 900 range thì chờ, vì dialog khoá điều khiển. Game báo một lần.
  - Máy và neutral giữ luật cũ (move mới mạnh hơn thì tự thay move yếu nhất).
- **Cách gắn vào build:** trong `build_data`, sau mọi patch script khác và trước khi đổi lại CRLF, gọi
  `script = move_tutor.patch_script(script)`. Script phải đang ở dạng LF, như trong `build_v42b.build_data`.
  Module đứng độc lập, chạy chung được với `move_ability_fix` / `ability_rw` / `hidden_ability`
  (gộp cả 4 trên script 4.2b_test: pjass 0 lỗi).
- **Test:** `python -I -m pytest tests/test_move_tutor.py -q` (gồm pjass).
- Sửa menu NPC hay `Mv_Sync` thì sửa trong module này, không vá chồng lên `Npc_Show`.

## 15. Bãi quái nhiều loài và `-random <gen>` (người dùng yêu cầu 2026-11-22)

Hai module `tools/v412/wild_mix.py` và `tools/v412/random_gen.py`, dùng chung helper `tools/v412/jpatch.py`.
Module `tools/v412/wild_mix.py` và `tools/v412/random_gen.py`. Đã viết, test và tích hợp hoàn chỉnh vào `build_v42b.py`.
- **Bãi quái (`wild_mix`):** mỗi con trong bãi là một loài riêng. Loài lấy từ wild pool theo power của bãi
  (chính là các model wild đang có).
  - Loài đang sống ở bất kỳ đâu trên map thì không chọn lại, trừ khi pool của power đó đã hết.
  - Ưu tiên loài có Soul, cho phép lệch power ±1.
  - Elite vẫn là một con ngẫu nhiên trong bãi, nên Soul rơi ra đa dạng hơn.
  - Thay `Wild_SpawnCamp`, `Wild_ReinforceCamp` (2 con quân tiếp viện cũng khác loài), `Wild_Upgrade`
    (lên tier thì từng con tiến hoá theo dạng của chính nó, hoặc đổi sang loài mới chưa dùng, không còn cả bãi
    thành một loài).
  - Mega_HT `c + 500` key 3 vẫn lưu loài của con đầu tiên, để code cũ đọc key này không bị lỗi.
- **`-random [gen]` (`random_gen`):** host gõ `-random` như cũ, hoặc `-random 3` / `-random gen3` để chỉ ra
  Pokemon Gen 3. Nhập số ngoài 1–9 thì game báo cách gõ. Gen nào không có con nào thì random từ mọi gen.
  - Bảng gen của từng hero trong `Rand_Type` được tạo lúc build từ `upro` trong war3map.w3u và dex PokeAPI
    (`tools/pokeapi/pokemon_size.json`), nên hero mới thêm sẽ tự có gen.
  - Bản 4.2b_test: 249 hero, gen 1–7 có lần lượt 84 / 49 / 63 / 39 / 8 / 5 / 1 con.
  - Lỗi trong file v4.3.w3x (đã sửa trong code 2026-11-22, cần build lại): 110 hero Gen 2–4 có `upro` dạng
    "#172 Pichu" nên không tìm được dex, chỉ 139/249 hero có gen (`-random 2` ra 20 con). `random_gen.proper_name`
    giờ bỏ tiền tố "#số ".
  - Test của move_tutor / item_fix / wild_mix_random_gen đọc script CHƯA vá ở
    `analysis/jass_ref/_tmp_v42b_test_war3map.j` (tách từ v4.2b_test.w3x). Không ghi đè file này bằng script đã vá.
- Danh sách Pokemon + điều kiện tiến hoá của một map: `python -I analysis/evo_list.py <war3map.j> <map.w3x> <out.json>`.
- **Cách gắn vào build** (trong `build_data`, sau các patch script khác, trước khi đổi lại CRLF; cần `w3u`):
  `script = wild_mix.patch_script(script)` và `script, gen_stats = random_gen.patch_script(script, w3u)`.
- **Test:** `python -I -m pytest tests/test_wild_mix_random_gen.py -q`. Gộp với move_ability_fix / ability_rw /
  hidden_ability / move_tutor: pjass 0 lỗi.

## 16. Sửa Shell Bell, hút máu, badge Gym 8 và Rocky Helmet (người dùng báo lỗi 2026-11-22)

Module `tools/v412/item_fix.py` (JASS `tools/v412/jass/item_fix.j`). Đã viết, test và tích hợp vào `build_v42b.py`.
- **Shell Bell (`I01P`):** trước đây chỉ có ability Life Steal gốc của WC3 (`A09S`, gốc `AIva`, 10%).
  `Ab_OnDamaging` viết lại damage của mọi đòn đánh, và orb không cộng dồn với orb khác, nên máu hút được gần
  như bằng 0.
  - Giờ hút 10% damage cuối khi đánh thường, 5% khi dùng skill, tính chung với charm Lifesteal trong
    `PAX_Loot_OnHitEx`.
  - `A09S` DataA1 đặt về 0 để không hút hai lần.
- **Charm Lifesteal (Effect Charm):** code vẫn hút máu nhưng không hiện gì. Giờ hiện số xanh "+N" trên hero,
  tối đa một lần mỗi giây.
- **Badge Gym 8 (`I01B`):** từ 4.1.3f là một hệ số damage ẩn (`V413_ArmorCut`), giáp của mục tiêu không giảm
  trên giao diện, và aura `A040` trên item có 0 giáp.
  - Giờ mỗi đòn đánh làm giáp mục tiêu giảm 20% trong 3 giây và hiện "-N armor". Đánh tiếp thì làm mới
    thời gian.
  - `GA_Tick` (mỗi 0,5 giây) trả lại giáp khi hết hạn.
  - Tooltip đổi thành "lower the target's armor by 20% for 3 seconds".
  - Đồng đội cùng đánh mục tiêu đó cũng được hưởng phần giáp bị giảm.
- **Rocky Helmet (`IB07`):** trước đây kẻ đánh cận chiến mất 3% máu tối đa CỦA CHÍNH NÓ (boss / quái to
  mất rất nhiều, quái nhỏ gần như không mất). Giờ nhận damage bằng 5% máu tối đa của NGƯỜI CẦM item mỗi đòn
  (người dùng yêu cầu). Tooltip đã đổi.
- **Cách gắn vào build** (trong `build_data`, sau các patch script khác, trước khi đổi lại CRLF):
  `script = item_fix.patch_script(script)`, `item_fix.patch_objects(abil)`,
  `item_func = item_fix.patch_item_text(item_func)`.
- **Test:** `python -I -m pytest tests/test_item_fix.py -q`. Gộp với 6 module ở mục 11–15: pjass 0 lỗi.

## 17. Cơ chế Boss: Boss Thụ Động, Giới Hạn Tầm Bãi (Leash 700) & Bảo Vệ Người Chơi Dưới Cấp 100 (người dùng yêu cầu 2026-11-22)

Module `tools/v412/boss_isolation.py`. Đã viết, test và tích hợp vào `build_v42b.py` và `build_v43.py`.
- **Boss Thụ Động (`SetUnitAcquireRange = 0.0`):** Boss hoang dã đứng yên tại bãi, không chủ động phát hiện
  hay lao vào tấn công bất kỳ Pokemon nào đi ngang qua. Người chơi đi qua đường lộ hoặc farm bãi không bị dí.
- **Bảo vệ người chơi dưới cấp 100:**
  - Người chơi < Lv 100 vào bãi farm có Legend xuất hiện vẫn thoải mái farm quái rừng bình thường.
  - Legend không bao giờ tấn công người < Lv 100 (không target, không rượt theo).
  - Nếu người chơi lỡ tung chiêu diện rộng (AoE) trúng Boss: Sát thương lên Boss tự động triệt tiêu về 0
    và Boss hoàn toàn không phản đòn.
  - Trong `Ai_Unit`, Boss bỏ qua toàn bộ hero < Lv 100, không cast 5 skill kit lên người chơi < Lv 100.
  - Trong `Ab_OnDamaging`, bất kỳ sát thương nào từ Boss lên hero < Lv 100 đều bị set về 0 và Boss lập tức dừng đánh (`stop`).
- **Chỉ phản đòn khi bị sát thương thực sự vào máu (Damage Retaliation):**
  - Chỉ khi một Hero cấp 100 gây sát thương thực sự (damage > 0) vào máu Boss, Boss mới nổi giận và target
    kẻ tấn công đó để phản đòn.
- **Thu hẹp tầm hoạt động (Leash Radius = 700 units):**
  - Trong `PAX_Boss_Tick`, bán kính rượt đuổi tối đa giảm từ 2500 xuống 700 units từ tâm bãi `(hx, hy)`.
  - Nếu bị kéo ra khỏi bãi (> 700 units): Boss lập tức ngắt thù hận (`stop`), xóa target, và quay đầu đi về
    tâm bãi. Trong khi quay về, Boss hồi 3% máu/giây.
  - Nếu bị kéo/đẩy quá 1200 units (chiêu dịch chuyển/hất tung): Boss lập tức dịch chuyển về tâm bãi (`SetUnitPosition`).
  - Khắc phục triệt để tình trạng 2 Boss bãi gần nhau chạy sang đánh chung một người.
- **Nhịp độ ra Boss (Spawn Pacing & Legendary Frenzy sau phút 30):**
  - Giai đoạn 0–30 phút: Đợt đầu xuất hiện lúc 4:00, sau đó cứ 4 phút (240s) ra 2 Boss (đẩy nhanh so với 6 phút trước đây).
  - Sau phút 30 (`Wild_Time >= 1800.0`): Kích hoạt chế độ **Legendary Frenzy** với thông báo toàn map! Nhịp độ tăng tốc đột biến: **cứ mỗi 90 giây (1.5 phút) ra 3 Boss một đợt**, giúp người chơi late game liên tục có Boss để săn mà không phải chờ đợi lâu.
- **Cách gắn vào build** (trong `build_data`, sau các patch script khác):
  `script = boss_isolation.patch_script(script)`.
- **Test:** `pytest _PokemonArena2.0_work/tests/test_boss_isolation.py`.
- **Trạng thái Build:** Đã hoàn tất đóng gói vào map `Pokemon Arena v4.2b.w3x` (187.0 MB) cùng toàn bộ các module của Claude (Hidden Ability, Move Tutor, Ability RW, Move/Item Fix, Wild Mix, Random Gen).

## 18. Pokemon Arena v4.3: Phiên bản Tối Ưu Hóa Online Multiplayer (2026-11-22)

Module build riêng: `tools/v412/build_v43.py`.
Output map: `c:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\Pokemon Arena v4.3.w3x` (187.0 MB).

- **Tách nhánh & Bảo lưu 100% Code Dev Test:**
  - File `tools/v412/test_commands.py` và `build_v42b.py` vẫn giữ nguyên vẹn 100%.
  - `build_v43.py` hỗ trợ cờ `--dev`:
    - Khi cần test các Gen sau (Gen 5, 6, 7...), chỉ cần chạy: `python tools/v412/build_v43.py --dev` -> toàn bộ lệnh `-gen`, `-legend`, `-c`, `-lvl`, `-nolvl` sẽ được nạp lại đầy đủ ngay lập tức.
- **Tối ưu hóa Online Multiplayer mượt mà & Chống Lag/Cheat:**
  - **Lược bỏ lệnh test/cheat:** Bản mặc định loại bỏ hoàn toàn các lệnh `-gen 1..4`, `-legend`, `-c`, `-lvl`, `-nolvl`, `-clear`, tránh việc người chơi troll/gian lận hoặc spam cùng lúc 50–100 model làm sụt giảm FPS đột ngột hay văng game (disconnect).
  - **Tối ưu Trigger Chat:** Gỡ bỏ trigger bắt chuỗi chat rỗng (`""`), loại bỏ hoàn toàn việc CPU phải scan chuỗi liên tục trên mỗi tin nhắn của 10–12 người chơi cùng lúc.
  - **Giữ lại các lệnh Utility cần thiết cho Online:**
    - Host drafting: `-random` hoặc `-random 1..9` (chọn Pokemon ngẫu nhiên theo Gen).
    - Host win condition: `-win <10..200>`.
    - Di chuyển / Tiện ích: `-tp`, `-mid`, `-cam`, `-ms`, `-stat`, `-stuck`, `-unstuck`, `-repick`, v.v.
  - **Tích hợp toàn bộ tối ưu hiệu năng từ v4.2b:**
    - Cơ chế quái rừng 5s respawn chỉ khi chết hết bãi, tối đa 6 con/bãi (không dồn quái gây lag late game).
    - Boss Thụ động (`SetUnitAcquireRange = 0.0`), Leash bãi 700 units (không chạy lộn xộn kéo sang nhau).
    - Bảo vệ người chơi < 100 an toàn farm bãi có Legend.
    - Sửa lỗi Item đổi Hidden Ability (`hidden_ability.py`), Move Tutor, Rework chiêu thức/item của Claude.

## 19. v4.3a: sửa lỗi "map is unavailable or corrupted" của 4.3 và 4.2b (Claude, 2026-11-22, người dùng duyệt)

- **Triệu chứng:** `Pokemon Arena v4.3.w3x` và `v4.2b.w3x` không vào được game ("There was an error trying to load the
  selected map. The map is unavailable or corrupted"). Nguyên nhân: script có lỗi JASS. `python -I analysis/pjass_map.py <map>`:
  - 4.3: 4 lỗi, 4.2b: 5 lỗi (thêm `PAX_ShowcaseLegends` không tồn tại). 4.2b chưa sửa, chưa build lại.
  - `Ai_Unit` (do `boss_isolation.py` thay) gọi `Leg_IsLegend` / `Leg_PlayerLevel`, mà 2 hàm này nằm SAU nó trong
    script. JASS bắt buộc hàm phải khai báo phía trên chỗ gọi.
  - `Leg_OnDamage` gọi `BlzGetEventDamage()`: hàm không tồn tại, phải là `GetEventDamage()`.
- **Sửa trong `tools/v412/boss_isolation.py`:** `NEW_AI_UNIT` đặt thêm `BossIso_IsLegend` / `BossIso_PlayerLevel` (cùng code
  với `Leg_*`) ngay trên `Ai_Unit` và `Ai_Unit` gọi chúng. `BlzGetEventDamage()` -> `GetEventDamage()`.
  `tests/test_boss_isolation.py` kiểm thêm thứ tự khai báo và không còn `BlzGetEventDamage()`.
- **Sửa trong `tools/v412/build_v43.py`:**
  - `random_gen.patch_script` dời xuống ngay sau `gen14_expansion`. Trước đó nó chạy khi 110 hero Gen 1-4 của gen14
    chưa có trong w3u / pool, nên 4.3 chỉ có 139/249 con có gen. 4.3a: 249/249 (84/49/63/39/8/5/1 cho Gen 1-7).
  - `NAME = "v4.3a"` (tên file và tên trong lobby). Bản build tiếp theo: đổi NAME trước, không ghi đè.
- **Luôn chạy `python -I analysis/pjass_map.py "<map vừa build>"` sau khi build**, và đọc dòng "Parse successful" /
  "Parse failed". Bước pjass trong build đã không chặn được bản 4.3 lỗi (có thể build chạy với `--skip-pjass`, hoặc pjass bị
  bỏ qua vì OSError trong sandbox).
- `build_v43.py` phải chạy bằng `python tools/v412/build_v43.py` (không có `-I`, vì nó import `map_optimizer` từ chính thư mục).
- **Đã build:** `Pokemon Arena v4.3a.w3x` (187.0 MB, 21:07). pjass trên map: 0 lỗi. Chưa ai chơi thử.

## 20. v4.3a crash khi nạp map: model do code sinh từ .glb bị sai định dạng (Claude, 2026-11-22)

- **Triệu chứng:** 4.3a crash khoảng 15 giây sau khi bắt đầu nạp map (Errors/2026-11-22 23.13.47, ACCESS_VIOLATION).
  Dấu hiệu crash (đuôi địa chỉ `...B098` <- `...0DBF`) giống 5 lần crash của 4.2b sáng 22/11 (08:50-09:43).
  Trong stack có giá trị `0x6769726F` = chữ "orig" của "origin Ref".
- **Nguyên nhân:** `tools/v412/glb_to_mdx.py` (sinh 968 file `imports/pokemon_3d_mdx/*.mdx`, 204 file dùng cho Gen 1-4
  của gen14 = `PkFx\G14\*.mdx`) viết sai MDX 800:
  - Mỗi attachment trong chunk ATCH thiếu 4 byte kích thước ở đầu (đúng là 364 = 4 + node 96 + path 260 + id 4).
    Game đọc "orig" thành kích thước rồi crash.
  - KGTR của bone Root trỏ global sequence 0 trong khi model không có global sequence (đúng là -1).
- **Đã sửa:**
  - `glb_to_mdx.py` viết đúng 2 chỗ trên.
  - `tools/v412/fix_glb_mdx.py` vá các file đã sinh (đã chạy: 968 file). Bản cũ sao lưu ở
    `imports/pokemon_3d_mdx_backup_before_atch_fix/`. File vá xong giống hệt file mà `glb_to_mdx.py` đã sửa sinh lại từ .glb.
  - `tools/v412/mdx_check.py`: kiểm tra cấu trúc MDX 800 (chunk, ATCH/BONE/HELP, pivot, material, texture, face index,
    global sequence). Model thật của 4.2a: 1.314 file, chỉ 2 file bị đánh dấu (Lucario.mdx, Mega3D\DeoxysDefense.mdx,
    có từ trước và game vẫn nạp được). 4.3a: thêm 203 file G14 bị đánh dấu.
  - `build_v43.py`: model `PkFx\G14\*.mdx` nào không qua `mdx_check` thì build dừng. `NAME = "v4.3b"`.
  - Test: `tests/test_glb_mdx.py`.
- **Luật:** model nào do code sinh ra (glb_to_mdx, billboard...) phải qua `python -I tools/v412/mdx_check.py <file|thư mục>`
  trước khi vào map, và người dùng phải tạo thử trong game. Qua được mdx_check chưa chắc game nạp được, nó chỉ bắt lỗi cấu trúc.
- **Đã build:** `Pokemon Arena v4.3b.w3x` (187.0 MB, 2026-11-22). pjass trên map: 0 lỗi. mdx_check trên 1.393 model của
  map: chỉ còn Lucario.mdx (có từ 4.2a). `-random` gen: 249/249. Chưa ai chơi thử, chưa ai thử model G14 trong game.

## 21. v4.3b: Pokemon Gen 1-4 mới quá to / nằm sai hướng (Claude, 2026-11-22, người dùng báo kèm ảnh)

- **Triệu chứng (4.3b, trong game):** nhiều Pokemon to choán màn hình; Gastrodon chọn được nhưng không thấy model
  (model cao 8.921, camera nằm bên trong).
- **Đo** (`model_size_check.py`, sau khi sửa để bỏ tiền tố "#172 " trong tên, trước đó 205 con báo "không có dữ liệu loài"):
  chiều cao model của 205 con G14 từ 17 đến 34.564; 78 con to hơn 3 lần mục tiêu (Seviper 229x, Gastrodon 85x),
  Barboach chỉ 0,2x.
- **Nguyên nhân:** `glb_to_mdx.py` đọc thẳng tọa độ mesh, bỏ qua cây node của glTF: scale của node (Seviper 0,01),
  xoay (Gastrodon -90 độ quanh X), skeleton (Pichu, Spearow: scale 2,54 + xoay). Sau đó nhân cố định 100.
- **Đã sửa:**
  - `glb_to_mdx.py`: áp ma trận world của node; mesh có skin thì linear blend skinning (JOINTS_0 / WEIGHTS_0, ma trận
    world(joint) x inverseBind) theo tư thế lưu trong file. Tham số mới `target_size`: thu phóng để
    max(cao, 0,4 x dài) = target_size, đặt đáy model ở z = 0 và căn giữa x/y.
  - `tools/v412/g14_reconvert.py`: chuyển lại từ .glb mọi model LOCAL_3D mà gen14 dùng (204), cỡ =
    `model_size_check.target_size(chiều cao thật)`. Đã chạy: 204/204, qua mdx_check. Bản trước khi sửa sao lưu ở
    `imports/pokemon_3d_mdx_backup_before_resize/` (mdx + textures).
  - `gen14_expansion.py`: scale của model LOCAL_3D = 1.0 (model đã đúng cỡ), Donphan / Miltank 0,95 (số người dùng chốt,
    mục 13). Trước đó 0,95 / 1,10 / 1,25 theo giai đoạn, không áp được ngoại lệ Donphan / Miltank.
  - `build_v43.py`: `NAME = "v4.3c"`.
  - Test: `tests/test_glb_mdx.py` kiểm cỡ = mục tiêu (sai số 2%), đáy ở z = 0, scale 1.0 trừ Donphan / Miltank.
- **Còn lại / chưa kiểm:** chưa thấy trong game. Vài con dài (Seviper, Huntail, Gorebyss) đứng dựng đứng vì file .glb lưu
  ở tư thế đó và không có animation. Model G14 chỉ có 1 bone (đứng / đi / đánh / chết là nhún nhẹ).
- **Bản quyền:** các .glb lấy từ Sketchfab, metadata ghi tác giả và giấy phép (ví dụ Barboach: CC-BY-4.0, cần ghi tên tác giả
  khi phát hành map).
- **Đã build:** `Pokemon Arena v4.3c.w3x` (187.8 MB, 2026-11-22). pjass 0 lỗi; mdx_check chỉ còn Lucario.mdx (có từ 4.2a).
  `model_size_check`: 204 model G14 đúng cỡ mục tiêu (trung vị 1,0x); còn Chimecho 1,6x (model RPG79, không qua g14_reconvert).
  Chưa ai chơi thử.

## 22. Chỉ giữ Pokemon có form (người dùng yêu cầu 2026-11-23)

Người dùng chọn: không đưa đủ 1025 loài vào map. Chỉ thêm các form (Mega, Primal, Alola, Galar, Hisui, Paldea,
Gigantamax, Terastal, dung hợp, Paradox, Origin / Therian / Rotom ...) có model, và loại các Pokemon không có form khỏi danh sách chọn.
- **Danh sách form:** 245 form từ PokeAPI (bỏ form chỉ khác hình thức: mũ Pikachu, Totem, màu Minior, cỡ Pumpkaboo,
  giới tính, Koraidon/Miraidon...). So với v4.3c: 56 form đã có model thật, 7 chỉ đổi màu (Mega Beedrill,
  Mega Kangaskhan, Dialga / Palkia Origin, 3 chim Galar), 14 có model ở map khác, 168 không có model.
  Trang patch note: https://claude.ai/artifact/5ZMsHXsxwVaMjGc8dcJN2g
- **Loại khỏi danh sách chọn (`tools/v412/form_roster.py`, đã gắn vào `build_v43.py`, CHƯA build):**
  - Người dùng chọn giữ cả dòng tiến hóa: dòng có ít nhất 1 con có form thì giữ cả dòng.
  - Paradox (PokeAPI tính là loài riêng) được tính là form của con nó giống, như Booster Energy trong map
    (Jigglypuff -> Scream Tail). Lần đầu quên điều này nên các dòng Jigglypuff / Magnemite / Misdreavus / Deino bị loại nhầm.
  - Tiến hóa vùng (loài riêng chỉ tiến hóa từ dạng vùng: Kleavor, Wyrdeer, Ursaluna, Sneasler, Obstagoon, Clodsire...)
    cũng tính là form (comment của người dùng trên trang cây phả hệ 2026-11-23: "scyther còn dạng nguyên thủy").
  - Người dùng tạm bỏ khỏi danh sách chọn (comment 2026-11-23): Darumaka, Darmanitan, Wooper, Qwilfish, Burmy và hero
    Mr. Mime bị trùng `P2WA` (dòng Mime Jr. đã có Mr. Mime `E040`) -> `user_drop_families`.
  - So với nationaldex.io gen 1-9 (người dùng gửi 2026-11-23): thêm Cherrim Sunshine, Shellos / Gastrodon East Sea
    (PokeAPI chỉ có ở pokemon-form) -> giữ dòng Cherubi, Shellos; Spiky-eared Pichu vẽ trên cây. Không thêm form chỉ khác
    hình thức mà trang đó có (mũ Pikachu, Vivillon, Alcremie, Minior, Arceus / Silvally theo hệ, Genesect drive...).
  - Kết quả (sau comment và nationaldex): giữ 104/243 dòng (229 loài), loại 139 dòng (280 loài; trước đó 106 dòng, `form_roster_data.json` -> `drop_ids`, tạo từ v4.3c
    bằng `analysis/evo_list.py`).
  - Hero bị loại chỉ biến mất khỏi 4 quán (`useu`: 43 -> 31), `-pick` (`Pick_InitData` dựng lại theo nhóm hệ:
    206 -> 79) và `-random` (`Rand_Type` / `Rand_N`: 249 -> 110). Unit vẫn nằm trong map, nên quái rừng, Gym, Soul
    và tiến hóa không đổi.
  - Test: `python -m pytest tests/test_form_roster.py -q` (đọc map v4.3c; có kiểm tra pjass). Dry-run build: pjass rc=0.
- **Thêm form (người dùng chọn chỉ thêm form có model, CHƯA làm):** 14 form có model thật:
  - Pokemon World `Unit\2003..2022`: Alolan Exeggutor, Marowak, Vulpix, Ninetales; Galarian Farfetch'd;
    Lycanroc Midnight; Hisuian Typhlosion, Sneasel; 5 Rotom (Heat, Mow, Frost, Fan, Wash).
  - PKLegends 3.2: Galarian Meowth (`MeowthGalarian4.mdx`).
  - Paldean Tauros 3 dạng đã có sẵn trong map (`P42A..P44A`). Galarian Weezing trong Pokemon World dùng model Weezing
    thường, nên không tính. Model trong 79.PokemonRPG không có tên file nên chưa đối chiếu.
- **Paradox (22 con):** 10 con đã có qua Booster Energy (`IM1A..IM1H`, `PAX_Form_ItemMatches` slot 8..17), nhưng chỉ
  đổi màu model gốc (`PAX_Form_Appearance` formId 10..19). `imports/pokemon_3d_all` có .glb thật cho 15/22 con
  (thiếu 986, 988, 989, 991, 992, 993, 1022). Trong đó có .glb để thay model đổi màu: Walking Wake, Gouging Fire,
  Raging Bolt, Roaring Moon, Flutter Mane, Scream Tail, Iron Thorns, Iron Valiant. Chưa có trong map nhưng có .glb:
  Great Tusk, Iron Treads, Iron Moth, Koraidon, Miraidon, Iron Leaves, Iron Crown.
- **Cây phả hệ có nhánh form (đề xuất, chưa làm):** https://claude.ai/artifact/PRCJqC7NXVA7uVbP13vCFU
  - Mỗi dòng có các nhánh: Mega Stone, Regional Charm (dạng vùng tách từ con trước, ví dụ Pikachu -> Alolan Raichu),
    Booster Energy (Paradox), Dynamax Band (Gigantamax), dung hợp, Tera, đổi dạng.
  - Người dùng (comment 2026-11-23): chỉ nhánh form cuối có Hidden Power, con tiến hóa thường không có
    (Eevee: "chỉ dynamax có hidden power").
  - Đề xuất item đổi dạng dùng được ở mọi bậc, đổi sang dạng cùng bậc, không lùi về dạng dưới (Mismagius ->
    Flutter Mane; map 4.3c đã cho Misdreavus / Mismagius cùng dùng Booster Energy). Người dùng DUYỆT 2026-11-23.

## 23. Tải model cho nhánh form: rule cho Gemini và người dùng (2026-11-23)

Chi tiết, danh sách và prompt mẫu: `docs/form-models/README.md`. Danh sách máy đọc: `docs/form-models/can-tai.csv`
(114 dòng; uu_tien 0 = đã có model, Claude chuyển; 1 = tải trước, 50 con; 2 = thay model đổi màu, 4 con; 3 = Gigantamax / Mega Z-A, 33 con).
- Code dựa trên map **v4.2a** qua `tools/v412/build_v43.py`. Không sửa tay map nào.
- Model tải về để ở `Maps\Download\imports\pokemon_3d_forms\<key>.glb` (key theo CSV), một file .glb có texture,
  ≤ 20 MB, mỗi mesh ≤ 65 535 đỉnh, đứng bình thường, không nền / đế. Không ghi đè file có sẵn.
- Chỉ CC0 hoặc CC-BY. Mỗi file một dòng trong `imports\pokemon_3d_forms\LICENSES.csv`
  (key, ten, tac_gia, giay_phep, url, ngay_tai, ghi_chu). CC-BY phải ghi tên tác giả trong credit map.
- Kiểm tra: `python tools/v412/check_form_glb.py [key ...]` (chỉ đọc; chuyển thử bằng glb_to_mdx + mdx_check, báo DAT / LOI / CHUA CO).
- Gemini KHÔNG sửa build_v43.py, không build, không xoá file, không đưa model thẳng vào map; Claude nối model vào map
  sau khi kiểm tra đạt.
- "Chỉ con đầu dòng" (người dùng duyệt 2026-11-23): `form_roster` gỡ khỏi quán / -pick / -random các hero có tiến hóa trước
  mà con đó chọn được (`not_first_stage_ids`: Pikachu, Clefairy, Jigglypuff, Mr. Mime E040, Snorlax, Lucario, Alolan
  Sandslash / Graveler / Golem), và thêm 3 tiến hóa cho dòng Alolan (`EXTRA_EVO`, hàm `Roster_EvoData` chạy sau `G14_Data27`).
  Alolan Raichu tạm vẫn chọn thẳng (chưa có Regional Charm). Còn 99 con chọn được lúc đầu (README mục 5);
  -pick 206 -> 72, -random 249 -> 101. Dry-run build: pjass rc=0.
- **Kiểm tra 2026-11-23 (Claude):** `imports/pokemon_3d_forms` đã có đủ 87/87 file; cả 87 chuyển glb -> mdx không lỗi
  (`check_form_glb.py`). Theo rule giấy phép (`--check-license`) chỉ 33 đạt: 30 ghi "Game Rip", 6 "Derived" (sửa từ model khác),
  1 "WC3 Map Rip", 17 chưa có dòng trong LICENSES.csv. Người khác đã đổi `check_form_glb.py` để mặc định BỎ QUA giấy phép;
  muốn kiểm đủ thì chạy thêm `--check-license`. Nhiều Mega Z-A nặng 8–13 MB (21–33 texture). Chưa nối model nào vào map.
- **Legend / Mythical / Ultra Beast (2026-11-23):** 105 con theo PokeAPI (71 Legendary, 23 Mythical, 11 Ultra Beast).
  Map 4.3c có 54 con (boss ngẫu nhiên và / hoặc chọn chơi qua Soul). 51 con chưa có, 50 con có .glb trong `pokemon_3d_all`
  (thiếu Terapagos). Form Legend trước đó không nằm trong `can-tai.csv` (chỉ lấy theo dòng hero thường): đã thêm 37 dòng
  `uu_tien = 4`. Arceus / Silvally theo hệ và Genesect theo drive chỉ khác màu, đề xuất đổi màu bằng code thay vì tải model.

## 24. Hướng model: mọi model chuyển từ .glb phải nhìn về +X (Claude, 2026-11-23, người dùng báo "model đi ngang")

- **Triệu chứng (New Pokemon Arena 1.0, trong game):** nhiều Pokemon đi ngang. Unit WC3 ở góc 0 độ nhìn về **+X**, trái = +Y.
- **Nguyên nhân:** `tools/v412/glb_to_mdx.py` đổi glTF (x, y, z) -> WC3 (x, -z, y). File .glb Pokemon nhìn về +Z, nên mặt model
  rơi vào **-Y**, lệch 90 độ. Dính **204 model G14 (Gen 1-4)** và **92 model form** từ .glb (Mega3D, HD, Pokemon World, PKL không dính,
  vì đó là MDX có sẵn). Đo bằng mdx-m3-viewer: nhìn từ +X thì model gốc thấy mặt, model chuyển từ .glb thấy cạnh bên; Arcanine
  Hisui dài theo Y (57 x 104), Linoone Galar 38 x 111.
- **Đã sửa:**
  - Map mới là (x, y, z) -> (z, x, y): xoay 90 độ quanh trục đứng, không lật mặt (det +1). Lao tới khi đánh (`KGTR` giây 3000) giờ đi theo +X.
  - `CONVERTER_REV` (hiện 3) nằm trong khoá cache của `form_assets.py`: model form chuyển trước bản sửa không bị dùng lại.
  - `FACING_FIX_DEG` (theo `model_name`, ví dụ `Pk_369`): xoay riêng cho file .glb nhìn hướng khác. Hiện có Relicanth (-90).
  - G14 chuyển lại bằng `python tools/v412/g14_reconvert.py` (204/204). Sao lưu bản trước: `out/backup_before_orient_fix/`.
  - Test: `tests/test_glb_mdx.py` (mũi nhọn tổng hợp phải ở +X, lao tới +X, 7 model thật dài theo X, ghi đè hướng của Relicanth).
- **Luật cho model mới từ .glb:** trước khi đưa vào map, nhìn model **từ camera đặt ở +X**: phải thấy mặt. Thấy cạnh bên hoặc lưng thì thêm
  dòng vào `FACING_FIX_DEG` (+90 quay ngược chiều kim đồng hồ nhìn từ trên xuống, +X thành +Y) và thử lại. Nhìn cạnh bên (profile)
  dễ đọc nhầm; dùng góc nhìn trước. Kiểm hàng loạt: trang render mdx-m3-viewer 4 hướng (camera ở +X, -X, +Y, -Y).
- **Chưa làm:** 764 file `imports/pokemon_3d_mdx/*.mdx` không dùng trong map vẫn hướng cũ (-Y). Nếu sau này dùng, chạy lại bằng
  `glb_to_mdx.py` mới. Model chỉ có 1 bone nên không có animation đi thật, chỉ nhún nhẹ.
