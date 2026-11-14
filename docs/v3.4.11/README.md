# Pokemon Arena v3.4.13: code xong, chưa build
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
