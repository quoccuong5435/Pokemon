# Pokemon Arena v3.4.16
**Đã build 2026-11-18** (`Pokemon Arena v3.4.16.w3x`, 164.5 MB, pjass 0 lỗi). **Chưa chơi thử.** Bảng hash của map nới lên 8192 ô
(`mpq._grow_hash_table` giữ 8 file v1.8 không tên ở vị trí cũ; tên tìm thêm: `tools/v3411/names_v3410.txt`). Sửa theo góp ý sau
khi chơi 3.4.15 + hiệu ứng chiêu mới.

**Stage (Atk / Def / Spe ...) thấy được và mạnh hơn** (góp ý: chữ trên đầu vướng, Def -1 không trừ thẳng, buff
không thấy khác biệt, tăng Spe ít tác dụng):
- Bỏ dòng chữ thường trực trên đầu. Thay bằng **icon ở hàng buff** (18 icon: tăng / giảm từng chỉ số, Burn, Poison,
  Bad poison, Paralysis, Sleep, Freeze, Confused, Accuracy down) + ánh sáng cũ trên đầu.
- **Attack** = số công cộng / trừ thẳng (xanh / đỏ) trên bảng chỉ số; **Defense** = giáp ±3 mỗi bậc; **Speed** = tốc
  chạy ±25% mỗi bậc (trước 15%) + tốc đánh (+2 = +30%, -2 = -20%). Sp. Atk / Sp. Def vẫn tính khi trúng chiêu.
  (ability item ẩn AF0A / AF0D / AF0S chỉnh số theo từng unit, `Fx_StatSync`; đòn đánh thường không còn nhân hệ số
  Atk / Def ngầm nữa để không tính hai lần.)
- Mỗi bậc mạnh như game gốc: +1 x1.5, +2 x2, -1 x0.67, -2 x0.5 (trước ±25%). Kéo dài **20 giây** (trước 12).
  Lúc dùng hiện "+2 Attack (x2.0)". `-stats` ghi bậc, hệ số, số giây còn lại, Confused / Protect / Shield.
**Debuff nhiều hơn** (góp ý: giảm chính xác hồi quá lâu, debuff ít):
- Giảm chính xác: trượt 30% (trước 20%), Sand Attack kéo dài 10 giây (trước 6), hồi 8 giây (trước 15).
- 9 move debuff mới (67 move trạng thái): Feather Dance, Cotton Spore, Tickle, Eerie Impulse, Confide, Baby-Doll Eyes,
  Smokescreen, Kinesis, Sweet Kiss (học theo learnset PokeAPI ở NPC dạy move).
- Chiêu sát thương có hiệu ứng giảm chỉ số: tỉ lệ gây ra gấp đôi.
**Khắc hệ rõ hơn:** "Super effective! x2", "EXTREMELY effective! x4" (nổ to), "Not very effective... x0.5",
"Barely effective... x0.25".
**Huyền thoại ngẫu nhiên = boss** (yêu cầu 2026-11-17): máu x20 (~600k–900k), công đánh thường x5, giáp x3, lúc sinh
ra (`Leg_Spawn`, hằng `Leg_BuffHP / Leg_BuffDmg / Leg_BuffArmor`; sát thương chiêu kit không đổi). Dưới 50% máu thì
**nổi giận**: công x1.5, đỏ người, gọi 2 Pokemon hoang mạnh nhất. Chết: **20 000 vàng chia theo % sát thương**, người
gây nhiều nhất nhận **Soul vào túi** hero, bảng xếp hạng hiện cho mọi người (`jass/leg_boss.j` thay Leg_OnDamage /
Leg_OnDeath).
**Trưởng Gym / Elite Four**: 13 NPC model huấn luyện viên của Pokemon World (Brock, Misty, Lt. Surge, Erika, Janine,
Sabrina, Blaine, Giovanni; Will, Koga, Bruno, Karen, Lance) đứng ở Gym (phía bắc sân) và trong phòng League; nói thoại
khi bắt đầu thách đấu và khi bạn thắng Gym (unit nT00..nT0C, `fx_more.TRAINERS`).
**Dạng vùng miền**: 10% quái hoang của 14 loài là dạng vùng miền thật (đổi ngoại hình, tên, **hệ**; vàng x1.5):
Alolan Vulpix / Ninetales / Exeggutor / Marowak / Raichu / Sandshrew / Sandslash / Geodude / Graveler / Golem, Hisuian
Typhlosion / Sneasel, Gyarados đỏ (`fx_more.REGIONAL`, skin nR00.., Ty_Of đọc hệ theo từng unit).
**33 Pokemon chơi được mới: bộ khởi đầu Gen 2–7** (`tools/v3411/starters.py`, unit EP00..EP0W): Totodile, Mudkip,
Turtwig, Chimchar, Piplup, Snivy, Tepig, Chespin, Fennekin, Froakie, Litten và 2 dạng tiến hoá của mỗi con. Model + icon
của Pokemon World (texture shiny thiếu được trỏ về texture thường), chỉ số / hệ / Ability (Overgrow / Blaze / Torrent) /
chiêu học theo cấp và TM lấy từ PokeAPI (`analysis/starters_v3416.txt`, `fetch_pokeapi.py` thêm nhóm 'starter'),
tiến hoá đúng cấp game gốc, có trong menu chọn (nhóm Lửa / Nước / Cỏ), -random và đội hình Gym.
Bộ khởi đầu cũng là **quái hoang** (nZ00..nZ0W, bậc 1–2 / 3–5 / 6–10) và rơi **Soul** (IZ00..IZ0W) như các loài cũ;
dạng cuối có Ability riêng: Feraligatr Strong Jaw, Torterra Shell Armor, Infernape Iron Fist, Emboar Reckless,
Incineroar Intimidate, Greninja **Protean** (Ability mới 79: hệ đổi theo chiêu vừa dùng).
**4 Mega mới** (`tools/v3411/megas.py`): Mega Swampert, Sableye, Garchomp, Abomasnow (đá IM0X..IM10 ở shop Mega 1–3 và
Super Mart 2, 6000 vàng; Mega Abomasnow có **Snow Warning**, Ability mới 80: gọi mưa đá, 60 giây/lần). Chưa có model Mega nên giống các Mega thiếu model khác: model gốc to hơn 40%, đổi màu, hào quang.
**Team Rocket** (`fx_main.j` Fx_Rocket*, số trong `fx_globals.j`): phút 10 rồi mỗi 15 phút, Jessie + lính Rocket dẫn
**8 Pokemon elite** (Arbok, Weezing, Meowth, Ekans, Koffing, Persian; bậc hiện tại **+6**, máu **x3**, công **x1.6**, giáp
x1.5) đánh vào căn cứ của một phe, **120 giây**. Mỗi con +600 vàng; hạ hết: cả phe +3000 vàng. Thua: mỗi người phe đó
mất **30% vàng** (ít nhất 1500) và Pokemon bị **giảm mọi chỉ số -1 trong 120 giây**.
**Nhiệm vụ** (`-quest`): mỗi người luôn có 1 nhiệm vụ ngẫu nhiên (hạ 12 Pokemon hoang của 1 hệ / hạ 30 Pokemon hoang /
thắng 1 Gym / góp sức hạ 1 huyền thoại / hạ 3 Pokemon của Team Rocket), thưởng 1500 vàng + Rare Candy x5.
**Dynamax** (item **Dynamax Band** IDMX, 8000 vàng ở Super Mart 2; ability ADMX, order robogoblin): Pokemon cấp 20+
bấm dùng: 20 giây to x2, máu tối đa x1.5, mọi chiêu là Max Move (+50% sát thương + vụ nổ lớn theo hệ, `fx_more.MAX_FX`).
**Hồi chiêu 150 giây**, dùng nhiều lần trong trận (không phải 1 lần / trận).
**NPC dạy move** (`jass/npc_moves.j` thay Npc_Show / Npc_OnClick; giá trong `fx_main.j` Fx_MovePrice):
giá theo từng chiêu (tăng ~3 lần theo yêu cầu; hằng Fx_Price* trong fx_globals.j) — học theo cấp 500 + 40 x Power
(move trạng thái 2000), TM 2000 + 80 x Power (move trạng thái 5000);
điều kiện mua TM: Power 70+ cấp 15, 90+ cấp 30 + 1 huy hiệu, 120+ cấp 45 + 3 huy hiệu (move trạng thái cấp 10);
bấm vào chiêu → màn xác nhận + **mô tả đầy đủ trong chat** (sát thương theo Pokemon của bạn, hiệu ứng, giá, điều kiện);
sau khi mua tooltip của nút chiêu được cập nhật (Mv_Tips).
**Thời tiết**: mỗi loại đổi màu sương toàn map; trời mưa có sét đánh quanh hero.
**Vitamin** (Protein, Calcium, Carbos, HP Up, bản x5): shop 99 cái, hồi 1 giây (trước 10 / 1 cái).
**Ditto** chơi được: Transform (move trạng thái mới: ngoại hình + bậc tăng của mục tiêu 30 giây) + bộ chiêu của Mew.
**Huy hiệu Gym:** thắng Gym thì huy hiệu Kanto của Gym đó (Boulder, Cascade, Thunder, Rainbow, Soul, Marsh, Volcano,
Earth; model Pokemon World) hiện trên đầu 6 giây.
**Hiệu ứng chiêu** (`tools/v3411/fx_more.py`, báo cáo `v3411/fx_more_report.txt`):
- 169 chiêu gây sát thương chưa có hiệu ứng riêng (103 cận chiến chỉ lướt chung, 66 tầm xa đạn WC3) nay có bộ riêng;
  41 chiêu dùng model mà chính Pokemon World gán (Bubble Beam, Seed Bomb, Metal Claw, Crunch, Mega Punch, Tri Attack...).
- 31 chiêu của v3.4.9 giữ bộ cũ và thêm một lớp model kiểu Pokemon (`V349_PW`): Razor Leaf (lá), Swift (sao băng),
  Hyper Beam (Kamehameha), Shadow Ball, Hydro Pump, Fire / Ice / Thunder Punch (nắm đấm)...
- 67 move trạng thái có hiệu ứng lớn (`STATUS_SPEC`) trên người dùng / mục tiêu.
- Script Pokemon World đã giải mã (`analysis/pw_decrypt.py`, `pw_models_from_script.py`, `pw_spell_fx.py`,
  `pw_fx_pool.py`). Model từ Pokemon World nhập vào `PkFx\PW_*.mdx`; tổng phần nhập thêm (cả trainer, dạng vùng miền, 33 Pokemon mới) ~25,9 MB. Map Pokemon Mew RPG 3.20B đã quét: không có model cho các Mega còn thiếu.
  Bán kính **đo trên ảnh render** (mdx-m3-viewer 5.12.0 qua analysis/render/, 95% điểm sáng nhìn từ trên,
  tools/v3411/fx_render_pw.json, scale tối đa x5); 6 model không thấy gì khi render vẫn dùng khung MDX (tối đa x3).

---

# Pokemon Arena v3.4.15: hiển thị buff / debuff, giảm chính xác có tác dụng thật
**Đã build 2026-11-14** (`Pokemon Arena v3.4.15.w3x`, 156.6 MB, pjass 0 lỗi). **Chưa chơi thử.**

**Hiển thị** (trước đây chỉ có dòng chữ nổi lên một lần lúc dùng chiêu):
- Dòng chữ thường trực trên đầu hero (Pokémon người chơi, gym, Elite Four), đi theo Pokémon, tự mất khi hết hiệu lực.
  Ví dụ: `Atk+2 Def-1 Burn Acc- Confused Protect Shield`. Xanh = tăng, đỏ = giảm, vàng = trạng thái xấu.
- Ánh sáng trên đầu khi có bậc tăng (hiệu ứng Inner Fire); dấu hiệu ở ngực khi có bậc giảm (hiệu ứng Cripple). Quái
  thường cũng có, nhưng không có dòng chữ (WC3 giới hạn khoảng 100 dòng chữ cùng lúc).

**Giảm chính xác:**

| Trước (3.4.11–3.4.14) | Bây giờ |
|---|---|
| Mud-Slap, Muddy Water, Sand Attack chỉ làm **đòn đánh thường** trượt 20%; move không bao giờ trượt; không có dấu hiệu gì nên gần như không thấy | Trượt 20% cho **cả đòn đánh thường lẫn move**; hiện chữ "Miss" |
| | Biểu tượng đầu lâu (hiệu ứng Curse) trên đầu Pokémon trong thời gian bị giảm chính xác |
| | Move không trượt (Aerial Ace, Swift, Aura Sphere, Shock Wave, Magical Leaf…) bỏ qua hiệu ứng này; Keen Eye miễn |
| | `-stats` hiện "Accuracy down"; tooltip ghi rõ |

---

# Pokemon Arena v3.4.14: sửa lỗi chậm / đứng yên vĩnh viễn
**Đã build 2026-11-14** (`Pokemon Arena v3.4.14.w3x`, 156.6 MB, pjass 0 lỗi). **Chưa chơi thử.**

| Lỗi | Nguyên nhân | Sửa |
|---|---|---|
| Pokémon **đứng yên vĩnh viễn** sau khi dùng move tụ lực (Solar Beam, Solar Blade, Sky Attack, Meteor Beam) | Bản 3.4.11–3.4.13: bấm lại phím chiêu trong 1,2 giây đang tụ lực thì unit bị dừng (`BlzPauseUnitEx`, có bộ đếm) thêm một lần mà chỉ được mở một lần | Đang tụ lực thì không dừng thêm; đồng hồ an toàn tự mở sau 1,5 giây |
| Pokémon **chạy chậm vĩnh viễn** (ví dụ chậm khoảng 13%) | Có từ 3.4.0, hay gặp hơn từ khi có bậc Speed: hết làm chậm thì tốc chạy được trả về giá trị chụp lúc bắt đầu bị chậm. Mega Evolve / đổi Ability trong lúc bị chậm làm giá trị đó cũ đi và không ai sửa lại | Hero hết làm chậm thì về tốc chạy mặc định cộng phần cộng / trừ hiện tại (`Ab_MoveBonus`) |

---

# Pokemon Arena v3.4.13
**Đã build 2026-11-14** (`Pokemon Arena v3.4.13.w3x`, 156.6 MB, pjass 0 lỗi). **Chưa chơi thử.**

Gồm toàn bộ 3.4.12. Thêm: elite, Pokémon gym, Elite Four và huyền thoại có **nút move trạng thái thật**, thay cho 1 trong
5 skill của bộ kit (không thêm ô). AI bấm nút đó theo luật của 3.4.12, có hoạt ảnh và hồi chiêu.

Mỗi hệ bỏ skill kit mang tên move trạng thái nếu có, không có thì bỏ skill thứ 5:

| Hệ | Bỏ | Move trạng thái (gym 1–4) |
|---|---|---|
| Bug | Quiver Dance | Quiver Dance |
| Dark | Swords Dance | Nasty Plot |
| Dragon | Dragon Dance | Dragon Dance |
| Electric | Charge | Thunder Wave |
| Fairy | Charm | Moonlight |
| Fighting | Bulk Up | Bulk Up |
| Fire | Blast Burn | Will-O-Wisp |
| Flying | Roost | Roost |
| Ghost | Shadow Force | Confuse Ray (Curse) |
| Grass | Agility | Sleep Powder (Synthesis) |
| Ground | Earth Crush | Sand Attack |
| Ice | Blizzard | Amnesia |
| Normal | Growth | Swords Dance |
| Poison | Toxic | Toxic |
| Psychic | Future Sight | Calm Mind |
| Rock | Stone Edge | Rock Polish |
| Steel | Meteor Mash | Iron Defense |
| Water | Withdraw | Aqua Ring |

---

# Pokemon Arena v3.4.12 (đợt 2)
**Đã build 2026-11-14** (`Pokemon Arena v3.4.12.w3x`, 156.6 MB, pjass 0 lỗi). **Chưa chơi thử.**

Cùng pipeline `tools/v3411/` (`version.txt` = 3.4.12), gồm mọi thứ của 3.4.11 bên dưới, thêm:

| Phần | Nội dung |
|---|---|
| 58 move trạng thái | 14 buff, 20 phòng thủ, 24 gây bất lợi (bảng: `tools/v3411/status_moves.py`). Mỗi move là nút Channel giống Double Team (232 nút mới, icon có sẵn của game), có hồi chiêu và mana riêng; move chọn mục tiêu có tầm 600 |
| Hiệu ứng mới | Protect / Detect, Reflect, Light Screen, Substitute (khiên), hồi máu theo giây, Wish, Focus Energy, Belly Drum, Rest, Yawn, Leech Seed, Taunt (bị Taunt thì không dùng được move trạng thái) |
| Học move | Theo learnset của game gốc: 948 lượt học theo cấp, 1776 lượt học bằng TM, ở NPC dạy move (500 / 3000 vàng). Lên cấp không tự học move trạng thái |
| AI | Elite, Pokémon gym, Elite Four, huyền thoại: mỗi hệ một move trạng thái (Dragon Dance, Nasty Plot, Thunder Wave, Recover…). Luật dùng: hồi máu khi dưới 40% máu; buff khi trên 50%; Protect khi dưới 30% và có từ 2 kẻ đánh; màn chắn khi có từ 2 địch; gây bất lợi lên mục tiêu chưa bị trạng thái. Gym 1–4 không dùng ngủ / lú lẫn. Move nghỉ sau chiêu chỉ dùng khi mục tiêu dưới 35% máu |

Build: `python -I tools/v3411/apply.py` → `python -I tools/v34/check.py v3411/war3map.j` (0 lỗi) →
`python -I tools/v3411/build.py` (ghi `Pokemon Arena v3.4.12.w3x`).

---

# Pokemon Arena v3.4.11

Build 2026-11-14 (`Pokemon Arena v3.4.11.w3x`, 156.6 MB). **Chưa chơi thử.**
- **Gốc:** dựng từ map `Pokemon Arena v3.4.10.w3x` (nhánh của tài khoản kia; mã nguồn của nhánh đó không có trên máy này).
- **Nội dung:** đợt 1 của kế hoạch đã duyệt ("Kế hoạch rework chiêu thức và Ability", Claude Docs
  https://claude.ai/artifact/PQ6rB4jucWYxdxaP14uhWv), cộng thêm lệnh `-tp`.

## Cách build lại
Chạy trong `_PokemonArena2.0_work`:
1. `python -I tools/v3411/apply.py`: sinh `v3411/war3map.j` và `v3411/plan.json` từ map 3.4.10.
2. `python -I tools/v34/check.py v3411/war3map.j`: pjass phải 0 lỗi.
3. `python -I tools/v3411/build.py --dry-run`, rồi `python -I tools/v3411/build.py` (không ghi đè map đã có).

Code JASS mới nằm ở `tools/v3411/jass/`:
- `fx_globals.j`: biến toàn cục;
- `fx_core.j`: chèn trước `Hero_HPSync`;
- `fx_main.j`: chèn trước `Ext_AfterHit`.

`apply.py` sinh dữ liệu và vá script; `build.py` sửa dữ liệu object.

## Thay đổi
| Phần | Nội dung |
|---|---|
| Sửa lỗi 3.4.10 | 4 lỗi pjass (biến cục bộ `s2`, `m2`, `ra` trong `Mv_Fire`, `sc` trong `Mv_CloneSpawn` trùng tên hàm v1.8) |
| Bộ hiệu ứng | Bậc chỉ số −4..+4 (±25%, Speed ±15%, 12 giây). Trạng thái thiêu đốt / độc / độc nặng / tê liệt / ngủ / đóng băng, lú lẫn, câm. Miễn theo hệ; chống khóa cứng (lần choáng thứ 2 trong 6 giây chỉ còn một nửa thời gian) |
| 319 move | Hiệu ứng theo game gốc (dữ liệu PokeAPI trong `tools/learnsets.json`): nghỉ sau chiêu, tụ lực, biến mất, phản sát thương, hút máu, tự giảm / tăng chỉ số, giảm chỉ số mục tiêu, trạng thái, chùn bước, trói, đánh rồi lùi, chí mạng cao, ưu tiên (hồi chiêu −30%). Bỏ choáng / làm chậm mượn từ skill gốc ở 210 chiêu ẩn; 110 move không có hiệu ứng phụ được +10% sát thương. Tooltip ghi đúng hiệu ứng |
| Công / thủ | Move Vật lý tính theo STR, giảm theo Def; move Đặc biệt tính theo INT, giảm theo Sp. Def (2 / (1 + thủ / 80), giới hạn x0,5–x1,5). Def / Sp. Def của 667 loại unit. Choice Band / Specs, Assault Vest theo loại move. `-stats` hiện thêm STR, INT, Def, Sp. Def, các bậc chỉ số và trạng thái |
| Ability | 23 Ability làm lại. 5 Ability mới cho huyền thoại: Pressure huyền thoại, Drizzle, Regenerator, Serene Grace, Beast Boost. Pressure thường mạnh hơn |
| Item hệ | Hiệu ứng riêng của 18 item viết lại bằng code, tăng theo sức mạnh; move cùng hệ +20%. Sửa Black Glasses (câm thật), Soft Sand (đổi tên, hiệu ứng mới), item của gym; Pixie Plate bán ở Super Mart 2 |
| Item | Không cầm 2 item giống nhau (mua trùng thì hoàn vàng, nhặt trùng thì item rơi lại) |
| Gym / Elite Four | Pokémon gym và Elite Four cầm item hệ (gắn ability, không rơi). Gym 1–4 chỉ có +20% sát thương |
| Elite Four | Đấu ở phòng Darkrai (nền mới, 5 tượng, cổng cạnh Item Shop ở mỗi căn cứ, cổng ra về căn cứ, item "Pokemon League"). Darkrai thành huyền thoại ngẫu nhiên. Chặn PvP, xếp hàng, thua thì hồi sinh ở sảnh, chờ 30 giây |
| `-tp` | Niệm 3 giây rồi về căn cứ, hồi đầy máu và mana. Không dùng được trong gym / League; hồi chiêu 60 giây |

## Chưa làm / làm khác kế hoạch
- **Đợt 2 (3.4.12):** 58 move buff / phòng thủ / gây bất lợi, AI dùng move mới.
- **Move đánh nhiều lần:** không có thêm đòn thật; tổng sát thương như cũ, Skill Link cho +50%.
- **Palkia:** chưa làm "tầm chiêu +25%". **Rayquaza:** chưa làm "miễn thời tiết". **Pursuit:** chưa có hiệu ứng riêng.
- **Dạng Mega:** dùng Def / Sp. Def của loài gốc.
- **90 skill bộ kit** của elite / gym / huyền thoại: giữ choáng / làm chậm của v1.8, chỉ thêm hiệu ứng mới theo tên.

## Cần chơi thử
1. **Sát thương:** Pokémon thiên INT dùng move Vật lý yếu đi; Steelix chịu đòn vật lý tốt, sợ phép.
2. **Hyper Beam, Solar Beam:** nghỉ 2 giây sau Hyper Beam; Solar Beam tụ lực 1,2 giây (dưới nắng thì bắn ngay).
3. **Trạng thái:** chữ hiện trên đầu Pokémon; độc / thiêu đốt mất máu đều; ngủ bị đánh thì tỉnh.
4. **Phòng League:**
   - cổng ở căn cứ có nằm cạnh Item Shop không, có chắn đường đi không;
   - nền và tượng;
   - PvP bị chặn;
   - thua thì hồi sinh ở sảnh.
5. **Item:** mua 2 item giống nhau thì được hoàn vàng; Soft Sand / Black Glasses có hiệu ứng.
6. **Lệnh:** `-tp`, `-stats`.
