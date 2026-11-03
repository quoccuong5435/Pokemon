# Nhật ký làm việc qua đêm (Pokemon Arena)

Bắt đầu từ bản 3.2.10. Giới hạn: không sửa/xóa map gốc, không ghi đè bản đã build, không thao tác game.

## Bước 1: Đọc tài liệu
- Đọc `CLAUDE.md` và `HANDOFF.md`. Các mục mở chính: lỗi elite nhỏ, nút Mega, ability cũ, chưa có khu boss.

## Bước 2: Danh sách legend gen 1–9
- File: `analysis\legendary_gen1_9.json` (94 loài legendary/mythical, lấy từ PokeAPI).
- Phân bố theo gen: I 5, II 6, III 10, IV 14, V 13, VI 6, VII 16, VIII 12, IX 12.
- Lưu ý: danh sách có các loài tiền tiến hóa (Cosmog, Cosmoem, Kubfu, Meltan) và các loài không phải boss mạnh. Cần lọc khi chọn boss.

## Việc còn lại (chưa làm)
1. Chọn danh sách boss (ví dụ 1 boss/gen, hoặc toàn bộ 94) và kiểm tra model có sẵn trong PKL.
2. Thiết kế khu boss: vị trí (chưa có tọa độ khu trống), cách vào (dịch chuyển bằng lệnh).
3. Cốt truyện nhẹ: thứ tự boss theo gen.
4. Các lỗi trong HANDOFF: elite nhỏ, nút Mega, ability cũ — cần bạn xác nhận trong game.
5. Build bản mới (3.2.11) sau khi có các bước trên và test pass.

## Câu hỏi cần bạn quyết định khi thức dậy
- Chọn boss: lấy hết 94 con, hay chỉ 1 con mỗi gen?
- Vị trí khu boss: dùng khu trống có sẵn (cần `-pos`), hay bỏ qua khu này?
- Có cần cốt truyện chi tiết không, hay chỉ tên gen và thứ tự?

## Cập nhật: map Big
- Đã tạo `POKEMON NEW\Pokemon Arena Big.w3x` (script/unit từ 3.2.10, nền từ Naruto 416×480). pjass pass.
- Đã vẽ tổng quan nền: `analysis\map_overview.png` (script `analysis\render_terrain.py`).
- Vấn đề đã báo: phòng boss/gym bị lệch trên nền Big. Chưa sửa: cần xác định lại tọa độ phòng theo nền mới (cần đọc wpm/doodad và kiểm tra trong game).
- Lỗi cần bạn xem: game văng về menu trong lúc quét minimap (hộp thoại "There was an error in handling the request.").
- Chưa làm: TM/HM 3k, 94 boss, cốt truyện, hiệu ứng skill. Các mục này cần dữ liệu hoặc quyết định của bạn (xem câu hỏi bên dưới).

## Câu hỏi khi thức dậy
- Dùng nền Big (có lệch phòng) hay quay về 160×160 + dịch chuyển?
- Chọn 94 boss hay 1 con mỗi gen?
- TM/HM: thế hệ nào?

## Duyệt cuối (tối nay)
- Đã có dữ liệu TM/HM thế hệ 9: `analysis\tmhm_scarlet_violet.json` (229 mục từ PokeAPI).
- Chưa làm: spawn 94 legend (cần kiểm tra unit type và model cho từng loài; hiện chỉ có 14 legend trong map), TM/HM trong NPC, build 3.2.11.
- Lý do dừng: bạn không onl, và việc spawn 94 legend cần kiểm tra model trước khi build.

## Yêu cầu mới: 120 PKLegends playable
- Chỉ số: theo PKLegends. Model: chỉ dùng model có sẵn (bỏ lo��i thiếu).
- Danh sách cần thêm: `analysis\pkl_not_in_arena.txt` (120 dòng). Dữ liệu chỉ số: `analysis\pklegends_pokedex.json`.
- Chưa làm: kiểm tra model từng loài, tạo unit và chiêu, build.

## Kiểm tra model PKLegends (đã làm)
- Chạy `pkl_roster.py`: 266 loài có model trong PKLegends, 168 loài chưa playable trong arena.
- Bỏ 2 mục không phải Pokémon (Heimsuchung, Maschinedramon) → **166 loài** ứng viên.
- Danh sách: `analysis\pkl_playable_plan.json`.
- Chưa làm: tạo unit (objects/poke_data), chiêu, TM/HM trong NPC, build 3.2.11. Đây là các bước code lớn cần làm từng phần và kiểm tra bằng pjass + test.

## Bước A: bảng 166 Pokémon PKLegends (đã làm)
- Tạo `tools\pkl_forms.py`: 166 mục (id hero, tên, level PKL). Chưa nối vào build.
- 10 loài chưa khớp tên trong `pklegends_pokedex.json` (Chikorita, Claydol, Diglett, Farfetch'd, Houndour, Mamoswine, Mr. Mime, Noctowl, Politeod, Sirfetch'd): cần sửa tên hoặc chỉ số thủ công.
- Còn lại (chưa làm): unit/model/icon cho từng loài trong `assets.collect_poke`, chỉ số, cách lấy Pokémon (tavern hoặc ngẫu nhiên — cần bạn chọn), chiêu theo learnsets, test (test cũ kiểm tra số 21), build 3.2.11.

## Tavern (đã chọn)
- 166 Pokémon chia theo hệ, mỗi hệ một tavern, đặt gần tavern hiện có (448, 4512).
- Chưa làm: tạo tavern theo hệ trong `objects.py`/`inject.py`, gắn danh sách bán, test và build.

## Thiết kế tavern mới (đã ghi)
- Ô hệ mở danh sách chọn như chọn chiêu; wisp chuyển vào khu tavern; chọn xong hero dịch chuyển về Poké Center. Chờ tọa độ Poké Center.

## Đã chọn (tavern)
- Hồi máu: vị trí bắt đầu của người chơi. Menu: nhiều trang, 10 con mỗi trang.
- Chưa làm: code menu tavern theo trang, dịch chuyển về vị trí bắt đầu, tạo tavern theo hệ, build.

## Build 3.2.11 (làm xong mục 1, 3, 5)
- Mục 1: `tools\poke_data.py` thêm 166 dạng PKLegends (từ `tools\pkl_forms.py`), unit P00A..; kit rỗng, chỉ số lấy từ hero E003 (chưa quy đổi theo PKL). Test đã cập nhật (số 21 → len(FORMS)).
- Mục 3: Menu chọn Pokémon theo trang (9 con/trang, Trang trước/sau, Close) trong `mega.j`: chọn tavern nTV5 hoặc gõ `-pick` khi còn giữ wisp. Dữ liệu từ `Pick_InitData` (inject.gen_pick_init).
- Mục 5: Test 184/184, pjass pass, build `Pokemon Arena v3.2.11.w3x` (91 MB).
- Chưa làm: tavern theo hệ (mục 2), dịch chuyển về vị trí bắt đầu (mục 4), chỉ số theo PKL, TM/HM, 94 boss, kiểm tra trong game.

## Build 3.2.12 (menu theo hệ + TM/HM 3.000)
- Dữ liệu: `tools\learnsets.json` tạo lại bằng `analysis\fetch_pokeapi.py` (curl, cache v2): 282 loài, 528 chiêu, có `tm` (TM/HM thế hệ 9 hoặc mới nhất có dữ liệu). Bản cũ: `analysis\learnsets_before_tm.json`.
- Menu chọn Pokémon: chọn hệ trước (tối đa 8 hệ mỗi trang), rồi danh sách Pokémon của hệ (8 con mỗi trang), có nút Back to types, Prev, Next, Close.
- TM/HM: NPC học chiêu có nút "TM/HM moves (3000 gold)" trong màn chọn slot; danh sách TM theo từng loài (chiêu có sát thương, tối đa 40), 8 chiêu mỗi trang. Dữ liệu: key 299 (số lượng) và 300+k trong `Ab_HT`.
- Test 184/184, pjass pass, build `Pokemon Arena v3.2.12.w3x` (91 MB).
- Chưa làm: 94 boss legend (spawn 1–2 con mỗi phút, 100% rớt đồ, không giới hạn), tavern theo hệ như building riêng, dịch chuyển về vị trí bắt đầu, quy đổi chỉ số PKLegends, thử trong game.

## Code (chưa build): bỏ dạng 2/3 khỏi menu chọn + Ability cho mọi Pokémon
- Tiến hóa PKLegends: `tools\pkl_forms.py` có `PKL_EVOLUTIONS` (55 liên kết, tạo bằng `analysis\gen_pkl_evolutions.py` từ `tools\evolutions.json`). Dạng tiến hóa (stage 2/3) không còn hiện trong menu chọn; người chơi tiến hóa trong game theo level (đá/trade/hạnh phúc dùng level 36 hoặc 55).
- Ability cho mọi Pokémon: `ability_data.ability_key_for` (bảng riêng → ability thật có trong danh sách → ability đặc trưng theo hệ). `type_abilities` giờ bao gồm hero v1.8, 166 dạng PKL, quái hoang dã và legend (380 unit type). Quái hoang dã và legend nhận Ability khi spawn (`Wild_Apply`, `Leg_Spawn`).
- Test 184/184. Chưa build theo yêu cầu.

## Danh sách playable (code, chưa build)
- Bỏ 20 tên trùng với 21 dạng có sẵn và lỗi gõ "Politeod" khỏi PKL_FORMS (còn 146 PKLegends, tổng 167 dạng mới).
- Làm lại `tools\evolutions.json` cho toàn bộ loài: 75 liên kết tiến hóa. Menu chọn (tavern): 85 con dạng gốc, không gồm 7 legend (Entei, Ho-Oh, Jirachi, Kyogre, Raikou, Regirock, Suicune).
- Danh sách đầy đủ: `analysis\playable_list.md`.
- Ability theo tiến hóa/Mega: `Ab_Sync` so sánh Ability của unit type hiện tại (hoặc Mega) với Ability đang áp dụng, đổi nút info và bonus khi tiến hóa hoặc Mega.

## Tavern theo hệ (code, chưa build)
- `tools\type_taverns.py`: 16 tavern theo hệ cho các Pokémon PKLegends dạng gốc (không legend), mỗi tavern bán các Pokémon cùng hệ (tối đa 11), icon tavern là icon hệ, nút bán sắp xếp 4 cột.
- Lưới 3 cột x 6 hàng trên bãi cỏ bên trái sân tavern: x = -1250, -1050, -850; y = 4800 → 4000 (cách 160). Ô đầu (-1250, 4800) là tavern Gen 3-4 (nTV5) đã dời từ (448, 4512). Tọa độ ước lượng từ ảnh, cần xem trong game rồi dời nếu cần (sửa `GRID_X`, `GRID_Y` trong `type_taverns.py`).
- Menu danh sách không mở khi chọn tavern nữa (chỉ còn `-pick`). Random starter (-random) lấy cả Pokémon của các tavern hệ.
- Test 184/184. Chưa build.

## Poke Center heal x3 và teleport Celebi/Darkrai (code, chưa build)
- Poke Center (unit n00P): aura hồi máu ACnr DataA1 x3 (`POKE_CENTER_HEAL_MULT` trong objects.py), dự kiến 5% → 15% máu tối đa mỗi giây.
- Shop Haunt Legendary (n030): thêm 2 item teleport `IL00` (Celebi's Location) và `IL01` (Darkrai's Location), nút (2,1) và (3,1), phím C và D. Script `LegTele_OnSell` dịch chuyển người mua tới (9600, -2588) và (-9600, -2209), gần chỗ boss (10104, -2588) và (-10019, -2209). Tọa độ ước lượng, cần thử trong game.
- Vibrava tiến hóa thành Flygon ở level 45 (Trapinch → Vibrava ở level 35).
- Chưa rõ: "spam legend không xuất hiện": hỏi lại người dùng.

## Code chưa build (cập nhật mới nhất)
- Celebi playable (hero `PZZA`, model/icon của boss n035, có Teleport), Soul Celebi (`ISCE`), thêm Celebi vào legend spawn ngẫu nhiên (15 legend).
- Soul của quái hoang dã giờ biến thành dạng gốc của họ Pokémon (poke_data.base_form_id). `Evo_Check` chạy mỗi giây trong `Hero_Tick`: hero đủ level để tiến hóa thì tự tiến hóa (kể cả sau khi dùng Soul).
- Icon teleport Celebi dùng icon BTNCelebi của boss. Item IL00/IL01 trong shop Haunt Legendary.
- Test 184/184.

## Gym (thông tin mới, chưa làm)
- Vị trí (từ `-pos`): gym 1 (-1543, 5719), gym 2 (-2704, 5392), gym 3 (-3984, 5392), gym 4 (-5424, 5424), gym 5 (1136, 5392), gym 6 (2448, 5392), gym 7 (3760, 5392), gym 8 (5408, 5424).
- Unit leader trong script v1.8: gym 1 `n00S` (Raticate), gym 2 `n00R`, gym 3 `n00X`, gym 4 `n010`, gym 5 `n014`, gym 6 `n018`, gym 7 `n019`, gym 8 `n00I`/`n01B`.
- Gym 1 trong v1.8: chuỗi 3 unit `n00S` → `n00U` → `n00T` (n00T mang item `I014`), chết hết thì hồi sinh `n00S` sau 60 giây.
- Yêu cầu mới: đội 6 con, level bằng level người tham chiến, mỗi con tăng thêm 10% (tối đa 100; nếu 100 thì cả đội 100); thua thì reset từ đầu.
- Chưa làm: quái hoang dã tự đổi dạng theo tier (đang kẹt dạng 1), cập nhật icon.

## Legend spawn (code, chưa build)
- 15 legend spawn ngẫu nhiên: Articuno, Moltres, Lugia, Darkrai, Mew, Regigigas, Mewtwo, Giratina, Deoxys, Arceus, Rayquaza, Zapdos, Dialga, Palkia, Celebi.
- Có phòng teleport trong shop Haunt Legendary (11): Lugia, Rayquaza, Giratina, Moltres, Arceus ("God's Location"), Mew, Articuno, Deoxys, Mewtwo, Celebi, Darkrai.
- Không có phòng teleport (4): Regigigas, Zapdos, Dialga, Palkia.
- Không spawn trùng: `Leg_Up[i]` giữ 1 khi legend đó còn sống; không có legend nào chưa sống thì bỏ lượt spawn.
- Máu legend x2.5 so với 3.2 (0.5 → 1.25 máu boss gốc), `LEGEND_HP_MULT` trong objects.py.
- Item hệ "không ràng buộc": chưa tìm thấy code ràng buộc item theo hệ trong script v1.8 hay trong mod, cần ví dụ cụ thể.

## 7 legend PKLegends vào spawn (code, chưa build)
- Raikou, Entei, Suicune, Ho-Oh, Regirock, Kyogre, Jirachi: boss mẫu `n00C` (Articuno) với model/icon/scale của PKLegends (x1.5), Soul riêng `ISL0..ISL6` biến Pokémon thành dạng playable. Tổng 22 legend spawn, không trùng, máu x1.25 boss gốc.
- Chưa có phòng teleport cho 11 legend: Regigigas, Zapdos, Dialga, Palkia và 7 con mới.
- Test 184/184. Chưa build.

## PKLegends v3.2, legend, Soul (code, chưa build)
- Nguồn model mới: `PKLegendsv3.2.w3x` (tests/conftest.py đã đổi). Lệnh build dùng `--pkl "../PKLegendsv3.2.w3x"`. v3.2 có thêm Groudon, Honedge/Doublade/Aegislash, Pawniard/Bisharp/Kingambit, Alolan Sandshrew/Sandslash; chưa có Latias và Latios (chỉ có texture/icon, không có model, cũng không có trong Pokedex).
- `Pokedex.html` đã chuyển thành `analysis\pklegends_pokedex_v32.json` (738 dòng: HP, giáp, sát thương, tốc độ, kỹ năng).
- Groudon và Buzzwole thành legend (Soul `ISL7`, `ISL8`); tổng 24 legend. Chỉ legend không có phòng spawn ngoài map: 13 con (Regigigas, Zapdos, Dialga, Palkia, Raikou, Entei, Suicune, Ho-Oh, Regirock, Kyogre, Jirachi, Groudon, Buzzwole), 2 con mỗi 3 phút, không trùng.
- Soul rớt 100%: legend spawn ngoài (`Leg_SoulChance` 100) và boss trong phòng (14 hàm xác suất v1.8 đổi 30% → 100% trong `inject.patch_boss_souls`). Hero chết rớt mọi item có tên kết thúc bằng "Soul" (`Soul_DropOnDeath`).
- Legend: máu x1.25, sát thương x2.0, giáp x2.5 (so với 3.2 là x2.5 mỗi chỉ số).
- Test 184/184.

## NPC moves bấm được (code, chưa build)
- Click NPC (nông dân tại 2356, -43) mở hộp thoại học chiêu, không cần gõ `-moves` (lệnh vẫn dùng được). NPC to 1.8 lần, bất tử, có chữ nổi "MOVES NPC (click)" và ping minimap lúc đầu game để dễ thấy.
- Test 184/184.

## Số sát thương nổi khi tung skill (code, chưa build)
- `Dmg_OnDamaged` (sự kiện EVENT_PLAYER_UNIT_DAMAGED): hiện số sát thương sau giáp trên đầu mục tiêu cho chiêu/skill của người chơi (không hiện cho đòn đánh thường), chỉ người sở hữu thấy, màu vàng, bay lên trong 1.3 giây. Tối đa 40 số mỗi giây để không đầy giới hạn text tag của game.
- Test 184/184.

## Gym, quái hoang dã, item theo hệ, skill (code, chưa build)
- 8 gym thành đội 6 con: level thành viên k = level người thách đấu x (1 + 0.1 k), tối đa 100; gym cao hơn mạnh hơn (chỉ số x (1 + 0.1 x chỉ số gym)). Chết hoặc đi xa 2200 thì reset từ đầu; thắng cả 6 rớt item gym (I014..I01B). Chuỗi leader v1.8 (n00S, n00U, n00T, ...) bị gỡ lúc bắt đầu. Vị trí lấy từ leader v1.8.
- Quái hoang dã chưa bị đánh (máu đầy) tự đổi sang loài của tier mới khi tier tăng (`Wild_Upgrade`, mỗi trại một loài).
- Item hệ (16 item ở Poke Super Mart 1 và 2: Charcoal, Mystic Water, ...) chỉ Pokémon thuộc hệ đó mua được (`Type_OnSell`, hoàn lại 3000 vàng nếu sai hệ). Tên loại của các dạng PKLegends giờ ghi hệ (ví dụ "Fire&Fighting Pokemon").
- Skill: hình dạng chiêu theo tên chiêu (`shape_of` trong learn_data.py): area (STOMP/NOVA), line (LINE/WAVE/ULT_WAVE), cone (CONE), single (DAGGER/CHAIN/BOLT). Tier theo sức mạnh. Trước đây hầu hết chiêu mạnh thành đường thẳng.
- Soul đổi dạng: các dạng qua Soul (14 legend v1.8 và mọi Soul của mình) không giữ chiêu của Pokémon cũ, học lại chiêu của loài mới (`Mega_ResetsMoves`).
- Test 184/184. Chưa build.

## Icon hệ từ Fandom và danh sách playable (code, chưa build)
- 18 icon hệ lấy từ https://pokemon.fandom.com/vi/wiki/Hệ (WebP 64 px, tải qua trình duyệt vì shell không vào được static.wikia): `analysis\type_icons_fandom\*.webp`, dữ liệu gốc trong `fandom_icons_data.py` và `fandom_icons_fix.py`, ảnh xem trước `type_icons_preview.png`. Chuyển sang BLP bằng `make_type_icons_fandom.py` vào `analysis\type_icons` (BTNPkmn<Hệ>.blp và bản DIS xám); icon placeholder cũ lưu ở `analysis\type_icons_placeholder`. Icon dùng cho nút chiêu và tavern theo hệ.
- Danh sách playable đầy đủ (hệ, Ability, chiêu level-up, số TM): `analysis\playable_full_list.md` (294 Pokémon), tạo bằng `analysis\export_playable_full.py`.
- Test 184/184. Chưa build.
