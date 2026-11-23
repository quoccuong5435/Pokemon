# AGENTS.md: luật làm việc cho map Pokemon Arena

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

Module `tools/v412/move_tutor.py` (JASS trong `tools/v412/jass/move_tutor_*.j`). Đã viết và test, CHƯA build.
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
Đã viết và test, CHƯA build.
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
- **Cách gắn vào build** (trong `build_data`, sau các patch script khác, trước khi đổi lại CRLF; cần `w3u`):
  `script = wild_mix.patch_script(script)` và `script, gen_stats = random_gen.patch_script(script, w3u)`.
- **Test:** `python -I -m pytest tests/test_wild_mix_random_gen.py -q`. Gộp với move_ability_fix / ability_rw /
  hidden_ability / move_tutor: pjass 0 lỗi.

## 16. Sửa Shell Bell, hút máu, badge Gym 8 và Rocky Helmet (người dùng báo lỗi 2026-11-22)

Module `tools/v412/item_fix.py` (JASS `tools/v412/jass/item_fix.j`). Đã viết và test, CHƯA build.
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
