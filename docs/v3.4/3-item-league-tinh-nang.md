# 3. Item mới, Elite Four, Shiny, thời tiết, đá tiến hóa, Mega cho elite / huyền thoại

Ngày 2026-11-07. Lúc đầu đề xuất làm v3.5.0; bạn duyệt và cho **gộp vào v3.4.0** (đã build). Khắc hệ đã có từ trước nên không nằm ở đây. Bảng dưới là bản đề xuất đã duyệt; phần "Trạng thái" cuối file ghi những gì đã làm khác đi. Amulet Coin không chạy ở 3.4.0, đã sửa ở 3.4.1.

## 1. Item mới (lấy từ game Pokémon)

Map đang bán: đá tiến hóa, kẹo/vitamin (Poke Mart); thuốc, Revive, Shell Bell (Poke Center); 18 item hệ (Super Mart 1–2); Mega Stone; vé dịch chuyển tới huyền thoại.

Đề xuất thêm một cửa hàng **Battle Shop** cạnh Poke Center ở mỗi căn cứ, bán 12 item cầm theo. Mỗi Pokémon cầm tối đa **3 item chiến đấu khác nhau**, giống luật giới hạn 2 item chỉ số hiện có.

| # | Item | Giá | Tác dụng |
|---|---|---|---|
| 1 | Life Orb | 4000 | Đòn đánh và skill +30% sát thương; mỗi lần gây sát thương mất 1% máu tối đa (không dưới 20% máu). |
| 2 | Choice Band | 4000 | Đòn đánh thường +35% sát thương, −10% tốc độ chạy. |
| 3 | Choice Specs | 4000 | Skill +35% sát thương, −10% tốc độ chạy. |
| 4 | Choice Scarf | 4000 | +30% tốc độ chạy, +20% tốc độ đánh. |
| 5 | Leftovers | 3500 | Hồi 1% máu tối đa mỗi giây. |
| 6 | Focus Sash | 5000 | Đòn lẽ ra hạ gục khi đang trên 50% máu: còn 1 máu (hồi chiêu 60 giây). |
| 7 | Expert Belt | 3500 | Đòn khắc hệ (x2) gây thêm +25%. |
| 8 | Rocky Helmet | 3500 | Kẻ cận chiến đánh trúng mất 3% máu tối đa của nó. |
| 9 | Assault Vest | 4000 | Nhận ít hơn 25% sát thương từ skill. |
| 10 | Scope Lens | 3500 | +15% cơ hội chí mạng x1,5 cho đòn đánh. |
| 11 | King's Rock | 3000 | Đòn đánh 10% làm choáng 1 giây. |
| 12 | Eviolite | 3000 | Pokémon còn tiến hóa được: +30% giáp, nhận ít hơn 20% sát thương. |

**Item tiện ích** bán ở Poke Mart / Poke Center (thêm ô bán khi cần):

| # | Item | Giá | Tác dụng |
|---|---|---|---|
| 13 | Lucky Egg | 3000 | +50% kinh nghiệm nhận được. |
| 14 | Amulet Coin | 3000 | +50% vàng khi hạ quái. |
| 15 | Everstone | 500 | Không tự tiến hóa khi lên cấp (bỏ đá ra thì tiến hóa ở lần lên cấp sau). Đi kèm Eviolite. |
| 16 | Sitrus Berry | 150 | Dùng 1 lần: máu xuống dưới 50% thì tự hồi 25% máu. |
| 17 | Lum Berry | 150 | Dùng 1 lần: tự xóa choáng, làm chậm, độc, cháy. |
| 18 | Escape Rope | 200 | Về căn cứ sau 3 giây (không dùng được khi đang ở gym). |
| 19 | Mega Ring | 8000 | Mega kéo dài 90 giây thay vì 60, đá Mega hồi nhanh hơn 30%. |
| 20 | Ice Stone, Shiny Stone | 1250 | Đá tiến hóa mới (xem mục 5). |

## 2. Elite Four + Champion

- **Mở khóa:** khi có đủ 8 huy hiệu. NPC "Pokémon League" ở căn cứ đưa bạn vào đấu trường (dùng lại khu Duel của v3.3).
- **Thể thức:**
  - Đánh liên tiếp 5 trận, mỗi trận một đội 6 con theo một hệ. Đội được chọn lúc bắt đầu như gym (6 dòng tiến hóa khác nhau, đúng form theo level).
  - Giữa các trận được hồi đầy máu và mana.
  - Thua trận nào thì về căn cứ, 60 giây sau mới được thử lại từ đầu.

| Trận | Người | Hệ | Level đội |
|---|---|---|---|
| 1 | Will | Psychic | level bạn +1 |
| 2 | Koga | Poison | level bạn +2 |
| 3 | Bruno | Fighting | level bạn +3 |
| 4 | Karen | Dark | level bạn +4 |
| 5 | Champion Lance | Dragon | level bạn +5. Các con có Mega sẽ Mega khi còn 50% máu (Mega Charizard X, Mega Gyarados, Mega Salamence, Mega Ampharos, Mega Altaria, Mega Rayquaza). |

- **Thắng:**
  - Danh hiệu **[Champion]** trước tên trong mọi thông báo, thông báo cho cả map, và +10000 vàng.
  - Một Mega Ring miễn phí.
  - Mở **Shiny Charm**: tỉ lệ shiny của bạn tăng từ 1/100 lên 1/20.

## 3. Shiny

- **Tỉ lệ:** 1/100 mỗi lần pick, `-random` hoặc dùng Soul (1/20 nếu đã có Shiny Charm).
- **Hiệu ứng:**
  - Pokémon shiny có màu riêng: map chưa có model shiny, nên dùng màu nhuộm cố định cho từng loài và hiệu ứng lấp lánh bám người.
  - +10% STR/AGI/INT.
  - Cả map được báo "★ Player có Charizard shiny!".
- **Giữ shiny:** shiny được giữ khi tiến hóa và khi Mega (dạng Mega cũng được nhuộm).

## 4. Thời tiết (đổi mỗi 5 phút)

Thời tiết ngẫu nhiên: Nắng, Mưa, Bão cát, Mưa đá hoặc Trời quang. Có hiệu ứng mưa, tuyết hoặc gió của game trên toàn map, kèm thông báo.

| Thời tiết | Tác dụng |
|---|---|
| Mưa | Skill hệ Water +30%, skill hệ Fire −30%. Swift Swim: +30% tốc độ chạy. |
| Nắng | Skill hệ Fire +30%, skill hệ Water −30%. Chlorophyll: +30% tốc độ chạy. |
| Bão cát | Mọi Pokémon không phải Rock/Ground/Steel mất 1% máu tối đa mỗi 2 giây (không dưới 10%). Hệ Rock +10 giáp. Sand Veil: né +15%. |
| Mưa đá | Mọi Pokémon không phải Ice mất 1% máu tối đa mỗi 2 giây (không dưới 10%). Snow Cloak: né +15%. |
| Trời quang | Không có gì. |

Ability Drought / Sand Stream vẫn chỉ tác dụng quanh Pokémon đó như v3.4.

## 5. Đá tiến hóa

- **Eevee** (giờ là form đầu) chọn nhánh bằng đá:
  - Fire Stone → Flareon, Water Stone → Vaporeon, Thunder Stone → Jolteon, Leaf Stone → Leafeon;
  - Sun Stone → Espeon, Moon Stone → Umbreon;
  - Ice Stone (mới) → Glaceon, Shiny Stone (mới) → Sylveon.
- **Các loài khác dùng đá**, kiểm tra loài nào v1.8 chưa có trigger rồi bổ sung:
  - Fire Stone: Vulpix → Ninetales, Growlithe → Arcanine.
  - Water Stone: Staryu → Starmie, Shellder → Cloyster, Poliwhirl → Poliwrath, Lombre → Ludicolo.
  - Thunder Stone: Pikachu → Raichu.
  - Leaf Stone: Exeggcute → Exeggutor, Weepinbell → Victreebel, Gloom → Vileplume.
  - Sun Stone: Gloom → Bellossom.
  - Moon Stone: Clefairy → Clefable, Jigglypuff → Wigglytuff, Nidorino → Nidoking, Nidorina → Nidoqueen.
  - Shiny Stone: Togetic → Togekiss.
- **Cách dùng:** cách cũ của map, nhặt đá vào túi là tiến hóa. Đá không đúng loài thì không mất.

## 6. Hoàn thiện phần còn dở

- **Elite biết Mega:** elite của loài có Mega có 25% xuất hiện ở dạng Mega (model Mega, +20% chỉ số). Khi chết có 5% rơi Mega Stone của nó.
- **Huyền thoại biết Mega:** Mewtwo và Rayquaza ở vị trí cố định Mega khi còn 50% máu (Mewtwo ngẫu nhiên X hoặc Y), hồi 20% máu và +30% sát thương.
  - v3.4.0 đã cho huyền thoại 5 skill theo hệ và AI dùng skill.
- **Quái đổi form theo tier:** khi tier tăng, quái chưa bị đánh tiến hóa lên form tiếp theo của chính nó nếu tới bậc đó, ví dụ trại Charmander → Charmeleon. Loài đã ở form cuối thì giữ nguyên và chỉ tăng chỉ số. Bản cũ đổi sang một loài ngẫu nhiên khác.
- **Icon chiêu khớp tên:** 319 move học được sẽ có icon theo tên chiêu, dùng icon có sẵn của game. Ví dụ Flamethrower → biểu tượng lửa, Thunderbolt → sét, Ice Beam → băng, Earthquake → đất nứt. Mình lập bảng 319 move → icon để bạn xem trước.

## Thứ tự đề xuất
1. Item (mục 1) và đá tiến hóa (mục 5): nhanh, dùng ngay.
2. Shiny và thời tiết.
3. Elite/huyền thoại Mega và quái đổi form theo tier.
4. Elite Four + Champion: lớn nhất, làm sau cùng vì dùng lại phần gym.
5. Icon chiêu: lập bảng cho bạn xem trước rồi mới đổi.

## Trạng thái (2026-11-07): đã duyệt, đã code và đã build vào v3.4.0 (chưa chơi thử)
- Bạn duyệt toàn bộ, thêm yêu cầu: danh hiệu Champion phải có chỉ số và aura. Đã làm:
  - **[Champion]:** +15% STR/AGI/INT cho Pokémon của người chơi đó (giữ khi tiến hóa).
  - **Champion Aura:** model hào quang vàng; Pokémon đồng minh trong 800 (kể cả chính nó) gây thêm 10% và nhận ít hơn 10% sát thương.
- Gộp vào **v3.4.0** theo yêu cầu, không tách v3.5. File `Pokemon Arena v3.4.0.w3x`.
- Code:
  - `tools/v34/extras.py`: dữ liệu item, shop, đá tiến hóa, quái theo tier, elite Mega, Elite Four.
  - `jass/extra.j`, `jass/extra_late.j`: item, Shiny, thời tiết, huyền thoại Mega.
  - `jass/gym.j`: League.
  - `tools/v34/move_icons.py`: icon chiêu; bảng ở `4-icon-chieu.md`.
- Cách dùng:
  - **Elite Four:** gõ `-league` khi đủ 8 huy hiệu. Đấu ở khu gym 8; gym 8 bị khóa trong lúc đấu.
  - **Shop mới:** Battle Shop và Item Shop xuất hiện cạnh Mega Shop ở hai căn cứ, ở chỗ trống đầu tiên đi lại được.
- Đá tiến hóa: thêm 18 cách tiến hóa mới (8 nhánh Eevee cho cả 2 bản Eevee, Poliwhirl, Lombre, Gloom, Clefairy, Jigglypuff, Togetic). Các loài v1.8 đã có trigger đá thì giữ nguyên.
- Icon chiêu: 278 move chọn theo tên, 41 move theo hệ.
- Chưa kiểm tra được trong game:
  - mã hiệu ứng thời tiết ('RAhr', 'LRaa', 'WOcw', 'SNbs');
  - vị trí 2 shop mới;
  - hình Mega của elite/huyền thoại (5 Mega không có model riêng chỉ đổi màu và kích thước).
