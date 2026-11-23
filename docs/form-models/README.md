# Tải model cho các nhánh form (Pokemon Arena, sau 4.3c)

Tài liệu này dành cho người dùng và Gemini. Claude viết ngày 2026-11-23.
Nó dựa trên trang cây phả hệ https://claude.ai/artifact/PRCJqC7NXVA7uVbP13vCFU và GEMINI.md mục 22–23.

## 1. Code đang dựa vào bản nào

- Bản build hiện tại là `tools/v412/build_v43.py`.
- Nó đọc map gốc **Pokemon Arena v4.2a.w3x**, vá thêm các module (gen14, form_roster…) rồi ghi ra `Pokemon Arena v4.3x.w3x`.
- Mọi thay đổi cho bản sau (4.3d) đều đi qua `build_v43.py`. Không sửa tay map 4.2a hay map 4.3x.
- Phần lọc danh sách chọn (`tools/v412/form_roster.py`) đã gắn vào `build_v43.py` nhưng chưa build.

## 2. Danh sách cần tải

File `docs/form-models/can-tai.csv` (mở bằng Excel được) có 114 dòng. Ý nghĩa cột `uu_tien`:

| uu_tien | Nghĩa | Số model |
|---|---|---|
| 0 | Đã có model trên máy, Claude sẽ chuyển. **Không cần tải.** | 27 |
| 1 | Nhánh của dòng chọn được, chưa có model nào. **Tải trước.** | 50 |
| 2 | Map đang dùng model gốc đổi màu, tải để thay. | 4 |
| 3 | Gigantamax, Mega mới Z-A, Ash-Pikachu, Spiky-eared Pichu. Tải sau. | 33 |
| 4 | Form của Legend / Mythical (thêm 2026-11-23): Therian, Crowned, Origin, Galarian 3 chim, Zygarde, Necrozma, Calyrex, Urshifu, Ogerpon, Terapagos (cả dạng thường)… | 37 |

**Ưu tiên 1 (50 model):**

- Alola: rattata-alola raticate-alola diglett-alola dugtrio-alola meowth-alola persian-alola grimer-alola muk-alola
- Galar: ponyta-galar rapidash-galar slowpoke-galar slowbro-galar weezing-galar mr-mime-galar
  corsola-galar zigzagoon-galar linoone-galar darumaka-galar darmanitan-galar-standard darmanitan-galar-zen
- Hisui: growlithe-hisui arcanine-hisui voltorb-hisui electrode-hisui qwilfish-hisui
- Paldea: wooper-paldea
- Mega: sableye-mega mawile-mega aggron-mega medicham-mega camerupt-mega banette-mega glalie-mega lopunny-mega abomasnow-mega
- Paradox: iron-bundle iron-hands
- Tiến hóa vùng: perrserker cursola mr-rime
- Đổi dạng: aegislash-blade greninja-ash castform-sunny castform-rainy castform-snowy cherrim-sunshine shellos-east gastrodon-east wormadam-sandy wormadam-trash

**Ưu tiên 2 (4):** beedrill-mega kangaskhan-mega iron-jugulis sandy-shocks

**Ưu tiên 3 (33):** 12 Gigantamax (venusaur, charizard, blastoise, butterfree, pikachu, meowth, machamp, gengar, kingler,
lapras, eevee, snorlax + `-gmax`), 19 Mega Z-A (raichu-mega-x, raichu-mega-y, clefable-mega, victreebel-mega, starmie-mega,
dragonite-mega, meganium-mega, feraligatr-mega, skarmory-mega, chimecho-mega, absol-mega-z, staraptor-mega,
garchomp-mega-z, lucario-mega-z, emboar-mega, chandelure-mega, chesnaught-mega, delphox-mega, greninja-mega),
pikachu-world-cap, pichu-spiky-eared.

## 3. Rule tải model (bắt buộc)

1. **Chỗ để:** `Maps\Download\imports\pokemon_3d_forms\<key>.glb`. `<key>` lấy đúng cột `key` trong `can-tai.csv`,
   viết thường, ví dụ `raichu-alola.glb`, `charizard-gmax.glb`.
   - Không để vào `pokemon_3d_all`.
   - Không ghi đè file đã có. Muốn thay thì đổi tên file cũ thành `<key>.old.glb` trước.
2. **Định dạng:**
   - Một file `.glb` (glTF binary), texture nằm sẵn trong file. Không dùng .fbx, .obj, .blend hay .gltf rời.
   - File nén Draco vẫn được.
3. **Giới hạn:**
   - File ≤ 20 MB.
   - Mỗi mesh ≤ 65 535 đỉnh, vì bộ chuyển `glb_to_mdx` từ chối file nặng hơn.
   - Nên dưới 15 000 tam giác cho mượt khi chơi online.
4. **Tư thế:**
   - Model đứng bình thường, kiểu T-pose hoặc idle.
   - Không lấy model đang nằm, đang ngủ hay gắn kèm cảnh nền, đế hay chữ.
   - Một con, một file.
5. **Giấy phép (đã bỏ bộ lọc ngày 2026-11-23 theo yêu cầu người dùng):**
   - Người dùng đã yêu cầu **bỏ hoàn toàn bộ lọc CC0 / CC-BY** để dùng cho bản fan-made phi thương mại (chấp nhận cả model `Pokemon-3D-api`, `CC-BY-NC`, `Standard` hay không ghi metadata giấy phép, miễn không phải từ trang bán rip trả phí).
   - `check_form_glb.py` chỉ kiểm tra điều kiện kỹ thuật (`<= 20 MB`, `<= 65 535` đỉnh/geoset, chuyển được sang MDX và qua `mdx_check`).
6. **Ghi nguồn (tùy chọn khi có thông tin):** nếu biết tác giả / nguồn URL thì thêm dòng vào `imports\pokemon_3d_forms\LICENSES.csv` gồm:
   - `key`
   - `ten` (tên Pokémon)
   - `tac_gia`
   - `giay_phep`
   - `url` (link trang model)
   - `ngay_tai`
   - `ghi_chu`
7. **Kiểm tra sau khi tải** (chạy trong thư mục `_PokemonArena2.0_work`):
   `python tools/v412/check_form_glb.py`, hoặc kiểm từng con: `python tools/v412/check_form_glb.py raichu-alola`.
   - `DAT`: file đạt.
   - `LOI`: file hỏng, sửa hoặc tìm model khác. Lỗi có thể là: file quá nặng, thiếu dòng giấy phép, giấy phép không hợp lệ, không chuyển được, hoặc `mdx_check` báo lỗi.
   - Công cụ chỉ đọc, không sửa file và không đụng vào map.
8. **Gemini không được:** sửa `build_v43.py`, build map, xoá file, hay đưa model thẳng vào map. Việc chuyển model vào map do Claude làm sau khi kiểm tra đạt (GEMINI.md mục 23).

## 5. Pokémon chọn được lúc đầu (sau khi lọc, theo dữ liệu map 4.3c)

Người dùng duyệt 2026-11-23 "chỉ con đầu dòng": con nào có tiến hóa trước và con đó chọn được thì bị gỡ khỏi bảng chọn đầu, phải tiến hóa mới có.
Ví dụ Pikachu → chọn Pichu, Lucario → Riolu, Snorlax → Munchlax, Clefairy → Cleffa, Jigglypuff → Igglybuff, Mr. Mime → Mime Jr.
Alolan Sandslash, Graveler và Golem giờ đạt được bằng tiến hóa: code mới thêm Alolan Sandshrew → Sandslash ở Lv 22, Alolan Geodude → Graveler ở Lv 25 → Golem ở Lv 40.
Alolan Raichu tạm vẫn chọn thẳng, vì chưa có Regional Charm để Pikachu rẽ nhánh.

Tổng **99 con** khác tên: 29 con bán ở 4 quán và 72 con trong bảng `-pick`. Eevee và Magnemite có mặt ở cả hai chỗ. `-random` cũng chọn trong đúng các con này.

**Quán (29):**
- Quán 1 (n000, starter), 11 con: Weedle, Caterpie, Machop, Geodude, Rattata, Pidgey, Sandshrew, Abra, Squirtle, Charmander, Bulbasaur
- Quán 2 (n00B), 8 con: Vulpix, Krabby, Growlithe, Gastly, Voltorb, Koffing, Dratini, Ponyta
- Quán 3 (n01G), 4 con: Staryu, Bellsprout, Magnemite, Exeggcute
- Quán 4 (n01H), 6 con: Pinsir, Onix, Scyther, Eevee, Kangaskhan, Tauros

**Bảng `-pick` theo hệ (72):**
- Normal (12): Buneary, Castform, Eevee, Farfetch'd, Igglybuff, Meowth, Munchlax, Stantler, Starly, Swablu, Teddiursa, Zigzagoon
- Fire (5): Cyndaquil, Fennekin, Numel, Tepig, Torchic
- Water (8): Carvanha, Corsola, Froakie, Lapras, Mudkip, Shellos, Slowpoke, Totodile
- Grass (5): Cherubi, Chespin, Chikorita, Snover, Treecko
- Electric (6): Alolan Raichu, Electrike, Magnemite, Mareep, Pichu, Rotom
- Ice (3): Alolan Sandshrew, Delibird, Snorunt
- Fighting (6): Makuhita, Meditite, Riolu, Tauros Aqua, Tauros Blaze, Tauros Combat
- Poison (1): Grimer
- Ground (3): Cubone, Diglett, Phanpy
- Psychic (3): Chingling, Mime Jr., Ralts
- Bug (1): Heracross
- Rock (3): Aerodactyl, Alolan Geodude, Larvitar
- Ghost (3): Litwick, Misdreavus, Shuppet
- Dragon (2): Bagon, Gible
- Dark (5): Absol, Deino, Houndour, Sableye, Sneasel
- Steel (5): Aegislash, Aron, Beldum, Mawile, Skarmory
- Fairy (1): Cleffa

Map gốc có hero trùng: Magnemite và Eevee mỗi con có 2 hero, một bán ở quán và một trong `-pick`.
Aegislash vẫn chọn thẳng được, vì Honedge / Doublade trong map không tiến hóa lên nó.
Khi làm nhánh Regional Charm (đã duyệt), các hero Alolan và Paldean Tauros sẽ chuyển thành nhánh của dòng gốc.
