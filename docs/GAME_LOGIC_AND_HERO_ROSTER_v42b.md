# Pokemon Arena v4.2b — Tổng Hợp Toàn Bộ Logic Game & Danh Sách Melee / Archer

> Tài liệu trích xuất trực tiếp từ mã nguồn chuẩn bị cho bản **`Pokemon Arena v4.2b`** (`scripts\war3map.j` & `war3map.w3u`).

---

## PHẦN I — TOÀN BỘ LOGIC HIỆN TẠI CỦA GAME (`v4.2b`)

### 1. Điều kiện Thắng / Thua & Multiboard
- **Mục tiêu điểm thắng (`PAX_Win_Target`):** Mặc định tự động theo số người chơi (`30 / 40 / 50 / 60` điểm; Host đổi bằng `-win <10..200>`).
- **Cảnh báo Match Point:** Khi một team còn cách chiến thắng `<= 5` điểm.
- **Kết thúc trận (`PAX_Win_Finish`):** Hiển thị bảng tổng kết **[MVP]**, **[CHIEN THAN DEM SO]**, **[NONG DAN CHAM CHI]** rồi hiện bảng Victory/Defeat sau `3.5s`.
- **Multiboard live (`PAX_MB_Update`):** Cập nhật mỗi `1s` gồm điểm 2 team, K/D, level, Pokemon đang cầm, thời gian trận.

### 2. Chọn Pokemon, Tiến Hóa, Cấp Độ & Huy Hiệu Gym
- **Chọn tướng:** Chọn ở nhà hoặc gõ `-pick`, `-random`, `-repick` (hoặc chế độ troll `-noob` / `-chicken`), đổi sang Pokemon khác khi dùng **Soul** nhặt từ rừng/Boss.
- **Cấp tối đa & 8 Gym (`-gym`):**
  - Cấp tối đa tăng dần theo số huy hiệu Gym (8 Gym, tối đa **Lv 100**).
  - Mỗi Gym gồm 6 Pokemon; con thứ 6 có bộ skill khắc hệ người thách đấu.
  - Quái Gym/League **không** rớt đồ Loot (chỉ thưởng Huy hiệu & buff Gym).
  - **Badge Gym 8 (`V413_ArmorCut`):** Xuyên `20%` giáp mục tiêu.
- **Pokemon League (`-league`):** Yêu cầu đủ 8 huy hiệu; đấu chuỗi Elite Four & Champion tại phòng Darkrai. Thắng nhận danh hiệu & **Champion Aura (`PAX_Champ`)**.
- **God Chu (`Ash's Cap`):** Pikachu nhặt Ash's Cap tiến hóa thành **God Chu - Legend Slayer** (`×3` sát thương lên Legend địch).

### 3. Cơ Chế Chiến Đấu, Hệ, Skill, Thời Tiết & Trạng Thái
- **Bộ kỹ năng Q/W/E/R (`Mv_*`):** Mỗi Pokemon có 4 chiêu theo hệ + chỉ số Physical/Special (scale theo STR/AGI/INT), có chiêu tụ lực (`1.2s`, tự động mở khóa nếu kẹt sau `1.5s`).
- **Bảng khắc hệ (`Ty_*` / `Dmg_*`):** Super Effective / Not Very Effective / Immunity chuẩn Pokemon.
- **Nội tại (`Ab_*`) & Trạng thái (`Fx_*`):** Burn, Freeze, Paralysis, Poison, Sleep, Confusion, Stat Stages (`-6..+6`), Weather (`Wth_Tick` đổi mỗi `4` phút: Clear / Rain / Harsh Sun / Sandstorm / Hail).
- **Hệ số giáp WC3 (`war3mapMisc.txt`):** Mặc định `0.06` → Giảm sát thương = `(0.06 × Armor) / (1 + 0.06 × Armor)`.

### 4. Mega Evolution & Form Switch (`v4.2b`)
- **Mở khóa trong nút `+` Vàng (`A800..A851`):**
  - Yêu cầu **Lv 50** (`5,000g`, `+40` All Stats vĩnh viễn) cho Pokemon thường, hoặc **Lv 70** (`8,000g`, `+60` All Stats vĩnh viễn) cho Legend.
  - Khi học `+` Vàng: tự động xóa skill giả `A8xx`, gắn vĩnh viễn skill bấm `AMxx` (Unit `ANcl`, `UnitMakeAbilityPermanent`) + tự hồi phục mỗi `1s` (`PAX_HeroMega_KeepAlive`) → **không bao giờ mất nút sau khi bấm**.
- **Chống tràn 12 ô Command Card:** Đã gỡ nút `PAXT` khi đổi Form và ẩn icon passive phụ `Ab_InfoId` trên Legend có 2 Mega (Mewtwo X/Y, Black/White Kyurem).
- **Form Switch CD:** `60 giây` (cả Deoxys và các Legend đổi Form).

### 5. Hệ Thống Quái Rừng & Rớt Đồ Loot (`v4.2b`)
- **Bản đồ rừng cân bằng 50/50 & đa dạng Soul:**
  - **`52` bãi** (**26 bãi Bên Trái vs 26 bãi Bên Phải**; đã bỏ 3 bãi lẻ thừa `camp[38], [39], [46]` bên Phải).
  - **Đã clear toàn bộ `121` con quái cũ lặp loài của map v1.8 lúc vào game** (như `nogl`, `n01R`, `n01V`...) và spawn mới `52` bãi hiện đại rải trong `0:02–0:06`.
  - **Chống trùng loài (`Wild_PickUniqueType`):** Ưu tiên chọn các loài có Soul chơi được và **không trùng với các bãi đang sống khác** (mở rộng `±1` bậc power) → tăng mạnh độ đa dạng Soul trên toàn bản đồ.
- **Giới hạn chống crash (`v4.2a` + `v4.2b`):**
  - Tối đa **`6` quái / bãi**, trần toàn bản đồ **`260` quái rừng sống**.
  - Thời gian hồi sinh bãi **`Wild_Respawn = 25s`** (tăng từ `10s` để chống cắm cọc bãi 2 con).
  - 10 phút đầu (`< 600s`) không gọi tiếp viện; sau phút 10 mỗi bãi chưa dọn gọi tiếp viện tối đa `1` lần sau `90s` (+1 thường +1 Elite, không vượt quá 6 con).
  - Đã tắt toàn bộ **18 trigger spawn quái cũ v1.8** (`Ox..xy`) và các single-spawn trùng lặp.
- **Tỉ lệ rớt đồ Loot cố định (chống lạm dụng bãi nhỏ):**
  - Quái thường: **`4%`** · Quái Elite: **`12%`** · Mega Elite: **`18%`** · Boss Legend: **`45%`**.
  - **Rớt Soul khi đánh Elite (thường + Mega Elite):** **`20%`** (`Wild_SoulChance = 20.0`).
  - **Mega Stone từ Mega Elite:** **`5%`**.
- **Tỉ lệ Phẩm chất (Tier) khi rớt:**
  - Quái thường: `75%` Common / `20%` Rare / `4.5%` Epic / `0.5%` Legendary
  - Quái Elite: `45%` Common / `38%` Rare / `14%` Epic / `3%` Legendary
  - Boss Legend: `35%` Rare / `45%` Epic / `20%` Legendary
- **Cấu trúc đồ Loot (`50%` Stat Relic / `50%` Effect Charm):**
  - Giá bán / tự xóa trên đất: Common `1,000g` (`90s`) · Rare `2,500g` (`90s`) · Epic `6,000g` (`180s`) · Legendary `15,000g` (`180s`).
  - **Stat Relic:** Common 1 dòng · Rare 2 dòng · Epic 2–3 dòng · Legendary 3 dòng (STR/AGI/INT, All Stats, Armor, Max HP, AS%, MS).
  - **Effect Charm (7 nội tại):** Lifesteal (`3–12%`), Storm Shock (`50–170%` Main Stat AoE), Soul Burn (`1–3%` HP/s), Critical (`8–28%` `×1.5`), Mana Surge (`3–10%` mana/hit), Thorns (`10–35%` phản dmg), Treasure Hunter (`+15–60%` vàng).
- **Nguồn đồ phụ:**
  - **`-up` → Mystery Box (`3,500g`):** `75%` Common / `10%` Rare / `3%` Epic / `0.5%` Leg / `11.5%` Rỗng *(an toàn ngay)*.
  - **`-gamble` (`1,000g`, CD 60s):** `15%` ra Rare/Epic *(an toàn ngay)*, `15%` Jackpot `+4k`, `20%` `+2k2`, `10%` `+500g`+Haste, `40%` mất.
  - **`-forge`:** Cường hóa `+1..+5` (lên tới **`×2.20`** chỉ số) hoặc ghép 2 món cùng Tier lên Tier trên (`60% / 40% / 20%`).
- **Quy tắc nhặt & rớt khi chết:**
  - **Không khóa Player ID** (đồng đội nhặt & chuyền đồ tự do).
  - Common, Rare và đồ từ `-up`/`-gamble`/`-forge`: **an toàn ngay** (không bao giờ rớt khi chết).
  - Epic, Legendary (nhặt từ quái/Boss/Event), Legend Soul, Mega Stone, Paradox Booster: rớt khi chết nếu cầm **< 60s**; cầm sống đủ **60s** sẽ khóa **`[SAFE]`** vĩnh viễn.

### 6. Hệ Thống Boss Legend (`v4.2b`)
- **Tổng cộng 54 Boss:** `15` Boss phòng cố định + `39` Roaming Wild Legends (spawn ngẫu nhiên tại `52` bãi, `50/50` hai bên).
- **Yêu cầu:** Chỉ Pokemon **Lv 100** mới gây sát thương lên Roaming Legend Boss.
- **Chỉ số chuẩn hóa (`PAX_Boss_Register`):**
  - **HP:** **`1,000,000 – 1,500,000`** *(giữ nguyên)*
  - **ATK:** **`1,500 – 2,500`** (CD đánh `-50%`, Mana vô hạn `10,000`)
  - **Armor:** **`150 – 200`** (giảm `90.0% – 92.3%` sát thương vật lý)
  - **Enrage (`< 50% HP`):** `+35%` ATK, `+25%` Skill dmg, `+12` Armor, `+38%` AS.
  - **Leash:** Ra khỏi vị trí quá xa hoặc hết combat tự chạy về và hồi `2% max HP/s`.
- **World Boss phút 55:00:** Mega Rayquaza xuất hiện giữa bản đồ (tồn tại 5 phút); giết thưởng `+2,000g` và buff Dragon Ascent vĩnh viễn cho cả team.

### 7. PvP & Sự Kiện Bản Đồ
- **Arena Duel (`Fy4`):** Tự động mỗi **`6` phút** (`360s`), hồi sinh & dịch chuyển 2 team vào đấu trường `40s`, team thắng cả team lên `+1` level.
- **Thách đấu tay đôi:** `-duel` (`-accept`/`-decline`) và `-solo` (`-yes`/`-no`, Deathmatch 90s giữa map).
- **Center Altar (mỗi `7` phút):** Chiếm `20s` nhận `+1,200–2,400g`/người + `2` món Loot (`1` Relic + `1` Charm: `55%` Rare / `35%` Epic / `10%` Leg).
- **Sự kiện giữa bản đồ & toàn map:**
  - **Golden Treasure Goblin** (mỗi 5p): `100%` rớt 1 Loot + `1,800g`.
  - **Giant Magikarp** (mỗi 6p): `70%` cá thật (`+1,500g` + `100%` Rare/Epic/Leg), `30%` bẫy **Red Gyarados** (`+3,000g` + `100%` Epic/Leg).
  - **Rush Hour** (mỗi 12–14p), **Smuggler's Cart** (mỗi 15p), **Weather Storm** (mỗi 10p), **WANTED Bounty** (mỗi 4p), **Chaos Mode 30s** (mỗi 10p).
  - **Cơ chế hỗ trợ team thua:** Comeback (thua ≥6 điểm: `+10%` dmg, `-10%` nhận dmg trong 2p) và Underdog Supply (thua ≥10 điểm: `+1,000g`/người + 1 Loot tại nhà).

### 8. Tối Ưu Kỹ Thuật & Chống Bug (`v4.2b`)
- **Revive Watchdog (`14s`):** Trong `PAX_Leg_Tick1s`, nếu bất kỳ hero nào chết quá `14s` chưa hồi sinh (do nghẽn `CX4` phút 48 / Duel) sẽ tự động gỡ mọi pause kẹt (`BlzPauseUnitEx`) và hồi sinh ngay tại nhà.
- **Dọn leak & tối ưu dung lượng:** Tắt trigger lỗi `ts`, dọn leak `location`/`group`/`force` trong bẫy phòng & Arena Duel, chuẩn hóa kích thước 3D 15 Legend mới `Leg25`, nén gọn MPQ + xóa `1,092` file mồ côi + nén `254` texture BLP quá cỡ.

### 9. Danh Sách Lệnh Chat Hiện Có
| Nhóm | Lệnh | Tác dụng |
|---|---|---|
| Cơ bản / Di chuyển | `-help`, `-cmd`, `-stat`, `-type`, `-moves`, `-ms`, `-ma`, `-me`, `-quest` | Xem hướng dẫn, chỉ số, hệ, bộ skill, tốc chạy |
| Hỗ trợ / Tầm nhìn | `-tp`, `-mid`, `-home`, `-stuck`, `-unstuck`, `-fog` / `-vision` *(Host)*, `-win <n>` *(Host)* | Về nhà (hồi đầy + xóa toàn bộ debuff), ra giữa map (`30s` CD), thoát kẹt, bật/tắt sương mù, đổi điểm thắng |
| Chọn tướng | `-pick`, `-random`, `-repick`, `-noob`, `-chicken` | Chọn / đổi Pokemon đầu trận |
| Kinh tế & Đồ | `-up` / `-train`, `-forge`, `-gamble`, `-pet` | Nâng chỉ số / mở hộp đồ, cường hóa/ghép đồ, quay số, pet |
| Đấu trường & Gym | `-gym`, `-league`, `-duel`, `-accept`, `-decline`, `-solo`, `-yes`, `-no`, `-rank`, `-badges` | Thách đấu Gym, League, PvP 1v1, xem hạng |
| Vui vẻ | `-taunt`, `-ez`, `-title` | Khiêu khích, đổi danh hiệu |

---

## PHẦN II — PHÂN LOẠI TOÀN BỘ 360 POKEMON HERO: MELEE vs ARCHER

### Phát hiện quan trọng về cơ chế đánh trong WC3
- **Tất cả 360/360 Hero đều được clone từ base `Emoo` (Priestess of the Moon)**, nên về mặt engine WC3:
  - `358` con có `weapTp1 = missile`, `2` con có `weapTp1 = mbounce`, **`0` con có `weapTp1 = normal`**.
  - Vì vậy trong WC3, sự khác biệt thực tế giữa **Melee (cận chiến)** và **Archer (đánh xa)** trong map hiện nằm hoàn toàn ở **Tầm đánh (`ua1r`)**:

| Phân loại theo Tầm đánh (`ua1r`) | Chi tiết tầm đánh | Số lượng |
|---|---|---:|
| **Archer / Đánh xa thực thụ (`400 – 600`)** | `400` (`6`) · `450` (`6`) · `500` (`10`) · `600` (`6`) | **`28` con** |
| **Tầm trung / Mid-range (`250 – 350`)** | `250` (`30`) · `300` (`20`) · `350` (`8`) | **`58` con** |
| **Cận chiến thuần (`128 – 180`)** | `128` (`13`) · `150` (`35`) · `180` (`4`) | **`52` con** |
| **Cận chiến tầm `200` (gồm toàn bộ Legend mới `EL*` & Gen 2–9 `P*`)** | `200` (`222`: `44` Legend + `178` thường) | **`222` con** |
| **Tổng cộng** | | **`360` Hero** |

> **Lưu ý rất đáng chú ý:** Toàn bộ **25 Legend mới (`EL00..EL0O`)** và **tất cả Hero Gen 2–9 (`P*`)** hiện đều đang để chung tầm đánh **`200`** (cận chiến) — kể cả các con hệ phép/đánh xa như **Lunala, Reshiram, Kyogre, Hoopa, Cresselia, Necrozma, Eternatus, Jirachi, Raikou, Suicune, Latias & Latios, Hydreigon, Magnezone, Mismagius**! Nếu bạn muốn mình chia lại tầm đánh chuẩn (ví dụ các con phép/bay/bắn xa lên `450–550` Archer, con cận chiến thật về `128–175` Melee), chỉ cần nhắn mình nhé.

---

### 1. Nhóm ARCHER — Đánh Xa Thực Thụ (`Range 400 – 600`, 28 con)

| ID | Tên Pokemon | Hệ | Nhóm | Stat chính | Tầm đánh (`ua1r`) | Kiểu đạn (`ua1w`) | Hiệu ứng đạn | Mega / Form |
|---|---|---|---|---|---:|---|---|---|
| `E00I` | **Alakazam** | Psychic | Classic (Starter/Evo) | INT | `600` | `missile` | Có | Mega Alakazam |
| `E02G` | **Gastly** | Ghost&Poison | Classic (Starter/Evo) | INT | `600` | `missile` | Có | — |
| `E01G` | **Gengar** | Ghost&Poison | Classic (Starter/Evo) | INT | `600` | `missile` | Có | Mega Gengar |
| `E02H` | **Haunter** | Ghost&Poison | Classic (Starter/Evo) | INT | `600` | `missile` | Có | — |
| `E00D` | **Pidgeot** | Flying | Classic (Starter/Evo) | STR | `600` | `missile` | Có | Mega Pidgeot |
| `EN0B` | **Gardevoir** | Psychic&Fairy | Legend | INT | `600` | `missile` | Có | Mega Gardevoir |
| `E01Q` | **Butterfree** | Bug&Flying | Classic (Starter/Evo) | INT | `500` | `missile` | Có | — |
| `E00H` | **Kadabra** | Psychic | Classic (Starter/Evo) | INT | `500` | `missile` | Có | — |
| `EN0A` | **Kirlia** | Psychic&Fairy | Classic (Starter/Evo) | INT | `500` | `missile` | Có | — |
| `E020` | **Articuno** | Ice&Flying | Legend | INT | `500` | `missile` | Có | Form/Mega |
| `E023` | **Darkrai** | Dark | Legend | INT | `500` | `missile` | Có | — |
| `E027` | **Deoxys** | Psychic | Legend | STR | `500` | `missile` | Có | Form/Mega |
| `E026` | **Mewtwo** | Psychic | Legend | INT | `500` | `missile` | Có | Mega Mewtwo X, Mega Mewtwo Y |
| `E021` | **Moltres** | Fire&Flying | Legend | INT | `500` | `missile` | Có | Form/Mega |
| `E029` | **Rayquaza** | Dragon&Flying | Legend | STR | `500` | `missile` | Có | Mega Rayquaza |
| `E03J` | **Zapdos** | Electric&Flying | Legend | INT | `500` | `missile` | Có | Form/Mega |
| `E000` | **Blastoise** | Water | Classic (Starter/Evo) | INT | `450` | `missile` | Có | Mega Blastoise |
| `EP0E` | **Empoleon** | Water&Steel | Classic (Starter/Evo) | INT | `450` | `missile` | Có | — |
| `EP02` | **Feraligatr** | Water | Classic (Starter/Evo) | STR | `450` | `missile` | Có | — |
| `EP0T` | **Greninja** | Water&Dark | Classic (Starter/Evo) | INT | `450` | `missile` | Có | — |
| `E00C` | **Pidgeotto** | Flying | Classic (Starter/Evo) | STR | `450` | `missile` | Có | — |
| `EP05` | **Swampert** | Water&Ground | Classic (Starter/Evo) | STR | `450` | `missile` | Có | Mega Swampert |
| `E00G` | **Abra** | Psychic | Classic (Starter/Evo) | INT | `400` | `missile` | Có | — |
| `E00E` | **Charizard** | Fire&Flying | Classic (Starter/Evo) | INT | `400` | `missile` | Có | Mega Charizard X, Mega Charizard Y |
| `E006` | **Raichu** | Electric | Classic (Starter/Evo) | STR | `400` | `missile` | Có | — |
| `EN09` | **Ralts** | Psychic&Fairy | Classic (Starter/Evo) | INT | `400` | `missile` | Có | — |
| `E02C` | **Victreebel** | Grass&Poison | Classic (Starter/Evo) | STR | `400` | `missile` | Có | — |
| `E024` | **Mew** | Psychic | Legend | STR | `400` | `missile` | Có | — |

---

### 2. Nhóm TẦM TRUNG — Mid-Range (`Range 250 – 350`, 58 con)

| ID | Tên Pokemon | Hệ | Nhóm | Stat chính | Tầm đánh (`ua1r`) | Kiểu đạn (`ua1w`) | Hiệu ứng đạn | Mega / Form |
|---|---|---|---|---|---:|---|---|---|
| `EN0G` | **Beldum** | Steel&Psychic | Classic (Starter/Evo) | STR | `350` | `missile` | Có | — |
| `E01K` | **Dragonite** | Dragon&Flying | Classic (Starter/Evo) | STR | `350` | `missile` | Có | — |
| `E031` | **Magnemite** | Electric&Steel | Classic (Starter/Evo) | INT | `350` | `missile` | Có | — |
| `EN0H` | **Metang** | Steel&Psychic | Classic (Starter/Evo) | STR | `350` | `missile` | Có | — |
| `E04M` | **Starmie** | Water&Psychic | Classic (Starter/Evo) | INT | `350` | `mbounce` | Có | — |
| `E04N` | **Staryu** | Water | Classic (Starter/Evo) | INT | `350` | `mbounce` | Có | — |
| `E032` | **Magneton** | Electric&Steel | Legend | INT | `350` | `missile` | Có | — |
| `EN0F` | **Salamence** | Dragon&Flying | Legend | STR | `350` | `missile` | Có | Mega Salamence |
| `E02K` | **Beedrill** | Bug&Poison | Classic (Starter/Evo) | STR | `300` | `missile` | Có | Mega Beedrill |
| `EP0N` | **Chesnaught** | Grass&Fighting | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E01F` | **Cloyster** | Water&Ice | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E049` | **Crobat** | Poison&Flying | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `EP01` | **Croconaw** | Water | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E01X` | **Electrode** | Electric | Classic (Starter/Evo) | INT | `300` | `missile` | Có | — |
| `EP0S` | **Frogadier** | Water | Classic (Starter/Evo) | INT | `300` | `missile` | Có | — |
| `E048` | **Golbat** | Poison&Flying | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `EP04` | **Marshtomp** | Water&Ground | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E00B` | **Pidgey** | Flying | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `EP0D` | **Prinplup** | Water | Classic (Starter/Evo) | INT | `300` | `missile` | Có | — |
| `EN05` | **Sceptile** | Grass | Classic (Starter/Evo) | INT | `300` | `missile` | Có | Mega Sceptile |
| `EP0H` | **Serperior** | Grass | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E01I` | **Tentacruel** | Water&Poison | Classic (Starter/Evo) | INT | `300` | `missile` | Có | — |
| `EP08` | **Torterra** | Grass&Ground | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E002` | **Venusaur** | Grass&Poison | Classic (Starter/Evo) | INT | `300` | `missile` | Có | Mega Venusaur |
| `E009` | **Wartortle** | Water | Classic (Starter/Evo) | INT | `300` | `missile` | Có | — |
| `E01A` | **Weepinbell** | Grass&Poison | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E019` | **Weezing** | Poison | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E046` | **Zubat** | Poison&Flying | Classic (Starter/Evo) | STR | `300` | `missile` | Có | — |
| `E02B` | **Bellsprout** | Grass&Poison | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0P` | **Braixen** | Fire | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E007` | **Charmeleon** | Fire | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `EN01` | **Combusken** | Fire&Fighting | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E01T` | **Dragonair** | Dragon | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0R` | **Froakie** | Water | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E00P` | **Golem** | Rock&Ground | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP07` | **Grotle** | Grass | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EN04` | **Grovyle** | Grass | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E001` | **Ivysaur** | Grass&Poison | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E01V` | **Koffing** | Poison | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0A` | **Monferno** | Fire&Fighting | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP03` | **Mudkip** | Water | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0J` | **Pignite** | Fire&Fighting | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E005` | **Pikachu** | Electric | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0C` | **Piplup** | Water | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E012` | **Poliwag** | Water | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E013` | **Poliwhirl** | Water | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E014` | **Poliwrath** | Water&Fighting | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0M` | **Quilladin** | Grass | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP0G` | **Servine** | Grass | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EN0E` | **Shelgon** | Dragon&Flying | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E02E` | **Shellder** | Water&Ice | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E004` | **Squirtle** | Water | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E02D` | **Tentacool** | Water&Poison | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `EP0V` | **Torracat** | Fire | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `EP00` | **Totodile** | Water | Classic (Starter/Evo) | STR | `250` | `missile` | Có | — |
| `E01D` | **Voltorb** | Electric | Classic (Starter/Evo) | INT | `250` | `missile` | Có | — |
| `E028` | **Giratina** | Ghost&Dragon | Legend | STR | `250` | `missile` | Có | Form/Mega |
| `EN08` | **Tyranitar** | Rock&Dark | Legend | STR | `250` | `missile` | Có | Mega Tyranitar |

---

### 3. Nhóm CẬN CHIẾN THUẦN — Melee (`Range 128 – 180`, 52 con)

| ID | Tên Pokemon | Hệ | Nhóm | Stat chính | Tầm đánh (`ua1r`) | Kiểu đạn (`ua1w`) | Hiệu ứng đạn | Mega / Form |
|---|---|---|---|---|---:|---|---|---|
| `E03A` | **Eevee** | Normal | Classic (Starter/Evo) | STR | `128` | `missile` | Không | — |
| `E01Z` | **Hitmonchan** | Fighting | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `E03Y` | **Hitmonlee** | Fighting | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `E03Z` | **Hitmontop** | Fighting | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `E02P` | **Kangaskhan** | Normal | Classic (Starter/Evo) | STR | `128` | `missile` | Có | Mega Kangaskhan |
| `EN0J` | **Lucario** | Fighting&Steel | Classic (Starter/Evo) | INT | `128` | `missile` | Có | Mega Lucario |
| `E03W` | **Pinsir** | Bug | Classic (Starter/Evo) | STR | `128` | `missile` | Có | Mega Pinsir |
| `E00U` | **Raticate** | Normal | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `E00T` | **Rattata** | Normal | Classic (Starter/Evo) | STR | `128` | `missile` | Không | — |
| `E03M` | **Scizor** | Bug&Steel | Classic (Starter/Evo) | STR | `128` | `missile` | Có | Mega Scizor |
| `E03L` | **Scyther** | Bug&Flying | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `E03X` | **Sylveon** | Fairy | Classic (Starter/Evo) | INT | `128` | `missile` | Không | — |
| `E018` | **Tauros** | Normal | Classic (Starter/Evo) | STR | `128` | `missile` | Có | — |
| `EN0K` | **Absol** | Dark | Classic (Starter/Evo) | STR | `150` | `missile` | Có | Mega Absol |
| `EN0D` | **Bagon** | Dragon&Flying | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E01N` | **Caterpie** | Bug | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E01S` | **Dratini** | Dragon | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E03H` | **Espeon** | Psychic | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E038` | **Flareon** | Fire | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E00N` | **Geodude** | Rock&Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E03T` | **Glaceon** | Ice | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E01E` | **Jolteon** | Electric | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E03P` | **Kabuto** | Rock&Water | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E035` | **Kabutops** | Rock&Water | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E02J` | **Kakuna** | Bug&Poison | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `EN06` | **Larvitar** | Rock&Dark | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E010` | **Machamp** | Fighting | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E00Z` | **Machoke** | Fighting | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E00Y` | **Machop** | Fighting | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E02S` | **Mankey** | Fighting | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `EN0I` | **Metagross** | Steel&Psychic | Classic (Starter/Evo) | STR | `150` | `missile` | Có | Mega Metagross |
| `E01P` | **Metapod** | Bug | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E03Q` | **Omanyte** | Rock&Water | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E03R` | **Omastar** | Rock&Water | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E03U` | **Onix** | Rock&Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E02T` | **Primeape** | Fighting | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E02Z` | **Rhydon** | Rock&Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E02Y` | **Rhyhorn** | Rock&Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E00A` | **Sandshrew** | Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E00F` | **Sandslash** | Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E03V` | **Steelix** | Steel&Ground | Classic (Starter/Evo) | STR | `150` | `missile` | Có | Mega Steelix |
| `E03I` | **Umbreon** | Dark | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E037` | **Vaporeon** | Water | Classic (Starter/Evo) | INT | `150` | `missile` | Có | — |
| `E02I` | **Weedle** | Bug&Poison | Classic (Starter/Evo) | STR | `150` | `missile` | Có | — |
| `E03S` | **Leafleon** | Grass | Khác | STR | `150` | `missile` | Có | — |
| `E03E` | **Magikarp** | Water | Khác | INT | `150` | `missile` | Có | — |
| `E040` | **Mr.mime** | Psychic | Khác | INT | `150` | `missile` | Có | — |
| `EN0C` | **Gallade** | Psychic&Fighting | Legend | STR | `150` | `missile` | Có | Mega Gallade |
| `E03F` | **Gyarados** | Water&Flying | Classic (Starter/Evo) | STR | `180` | `missile` | Có | Mega Gyarados |
| `E02A` | **Arceus** | God | Legend | STR | `180` | `missile` | Có | Form/Mega |
| `E04C` | **Dialga** | Time | Legend | INT | `180` | `missile` | Có | Form/Mega |
| `E04D` | **Palkia** | Space | Legend | INT | `180` | `missile` | Có | Form/Mega |

---

### 4A. Nhóm Tầm `200` — LEGEND HEROES (44 con)

| ID | Tên Pokemon | Hệ | Nhóm | Stat chính | Tầm đánh (`ua1r`) | Kiểu đạn (`ua1w`) | Hiệu ứng đạn | Mega / Form |
|---|---|---|---|---|---:|---|---|---|
| `EL04` | **Azelf** | Psychic | Legend | STR | `200` | `missile` | Có | — |
| `P0JA` | **Buzzwole** | Bug&Fighting | Legend | STR | `200` | `missile` | Có | — |
| `PZZA` | **Celebi** | Psychic&Grass | Legend | STR | `200` | `missile` | Có | — |
| `EL06` | **Cresselia** | Psychic | Legend | INT | `200` | `missile` | Có | — |
| `EL0F` | **Diancie** | Rock&Fairy | Legend | STR | `200` | `missile` | Có | Mega Diancie |
| `P1DA` | **Entei** | Fire | Legend | STR | `200` | `missile` | Có | — |
| `EL0O` | **Eternatus** | Poison&Dragon | Legend | INT | `200` | `missile` | Có | — |
| `EL0B` | **Genesect** | Bug&Steel | Legend | STR | `200` | `missile` | Có | — |
| `P4UA` | **Groudon** | Ground | Legend | STR | `200` | `missile` | Có | Primal Groudon |
| `EL05` | **Heatran** | Fire&Steel | Legend | INT | `200` | `missile` | Có | — |
| `P1TA` | **Ho-Oh** | Fire&Flying | Legend | STR | `200` | `missile` | Có | — |
| `EL0G` | **Hoopa** | Psychic&Ghost | Legend | INT | `200` | `missile` | Có | Hoopa Unbound |
| `P1YA` | **Hydreigon** | Dark&Dragon | Legend | INT | `200` | `missile` | Có | — |
| `P20A` | **Jigglypuff** | Normal&Fairy | Legend | STR | `200` | `missile` | Có | — |
| `P21A` | **Jirachi** | Steel&Psychic | Legend | STR | `200` | `missile` | Có | — |
| `P26A` | **Kyogre** | Water | Legend | INT | `200` | `missile` | Có | Primal Kyogre |
| `EL0A` | **Kyurem** | Dragon&Ice | Legend | STR | `200` | `missile` | Có | Black Kyurem, White Kyurem |
| `PV2A` | **Latias & Latios** | Dragon&Psychic | Legend | INT | `200` | `missile` | Có | Mega Latias & Latios |
| `EL0J` | **Lunala** | Psychic&Ghost | Legend | INT | `200` | `missile` | Có | — |
| `EL0L` | **Magearna** | Steel&Fairy | Legend | INT | `200` | `missile` | Có | — |
| `P4XA` | **Magneton** | Electric&Steel | Legend | INT | `200` | `missile` | Có | — |
| `P2LA` | **Magnezone** | Electric&Steel | Legend | INT | `200` | `missile` | Có | — |
| `EL0M` | **Marshadow** | Fighting&Ghost | Legend | STR | `200` | `missile` | Có | — |
| `EL03` | **Mesprit** | Psychic | Legend | STR | `200` | `missile` | Có | — |
| `P2UA` | **Misdreavus** | Ghost | Legend | INT | `200` | `missile` | Có | — |
| `P2VA` | **Mismagius** | Ghost | Legend | INT | `200` | `missile` | Có | — |
| `EL0K` | **Necrozma** | Psychic | Legend | INT | `200` | `missile` | Có | Ultra Necrozma |
| `P39A` | **Raikou** | Electric | Legend | INT | `200` | `missile` | Có | — |
| `EL00` | **Regice** | Ice | Legend | INT | `200` | `missile` | Có | — |
| `E025` | **Regigigas** | Normal | Legend | STR | `200` | `missile` | Có | — |
| `P3BA` | **Regirock** | Rock | Legend | STR | `200` | `missile` | Có | — |
| `EL01` | **Registeel** | Steel | Legend | STR | `200` | `missile` | Có | — |
| `EL08` | **Reshiram** | Dragon&Fire | Legend | INT | `200` | `missile` | Có | — |
| `EL0I` | **Solgaleo** | Psychic&Steel | Legend | STR | `200` | `missile` | Có | — |
| `P3XA` | **Suicune** | Water | Legend | INT | `200` | `missile` | Có | — |
| `EL02` | **Uxie** | Psychic | Legend | STR | `200` | `missile` | Có | — |
| `EL07` | **Victini** | Psychic&Fire | Legend | STR | `200` | `missile` | Có | — |
| `EL0H` | **Volcanion** | Fire&Water | Legend | INT | `200` | `missile` | Có | — |
| `P4IA` | **Wigglytuff** | Normal&Fairy | Legend | INT | `200` | `missile` | Có | — |
| `EL0C` | **Xerneas** | Fairy | Legend | STR | `200` | `missile` | Có | — |
| `EL0D` | **Yveltal** | Dark&Flying | Legend | STR | `200` | `missile` | Có | — |
| `EL0N` | **Zacian** | Fairy&Steel | Legend | STR | `200` | `missile` | Có | — |
| `EL09` | **Zekrom** | Dragon&Electric | Legend | STR | `200` | `missile` | Có | — |
| `EL0E` | **Zygarde** | Dragon&Ground | Legend | STR | `200` | `missile` | Có | — |

---

### 4B. Nhóm Tầm `200` — POKEMON THƯỜNG & TIẾN HÓA (178 con)

| ID | Tên Pokemon | Hệ | Nhóm | Stat chính | Tầm đánh (`ua1r`) | Kiểu đạn (`ua1w`) | Hiệu ứng đạn | Mega / Form |
|---|---|---|---|---|---:|---|---|---|
| `E01C` | **Arcanine** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EN02` | **Blaziken** | Fire&Fighting | Classic (Starter/Evo) | STR | `200` | `missile` | Có | Mega Blaziken |
| `E008` | **Bulbasaur** | Grass&Poison | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `E003` | **Charmander** | Fire | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `EP0L` | **Chespin** | Grass | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP09` | **Chimchar** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0Q` | **Delphox** | Fire&Psychic | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `EP0K` | **Emboar** | Fire&Fighting | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E02U` | **Exeggcute** | Grass&Psychic | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `E02W` | **Exeggutor** | Grass&Psychic | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `EP0O` | **Fennekin** | Fire | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `E00O` | **Graveler** | Rock&Ground | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E02F` | **Growlithe** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0W` | **Incineroar** | Fire&Dark | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0B` | **Infernape** | Fire&Fighting | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E03D` | **Kingler** | Water | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E03C` | **Krabby** | Water | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0U` | **Litten** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E01J` | **Nidoking** | Ground&Poison | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E01L` | **Nidorino** | Poison | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E04P` | **Ninetales** | Fire | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `E01B` | **Ponyta** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EN07` | **Pupitar** | Rock&Dark | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E01H` | **Rapidash** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0F` | **Snivy** | Grass | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EP0I` | **Tepig** | Fire | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `EN00` | **Torchic** | Fire&Fighting | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `EN03` | **Treecko** | Grass | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `EP06` | **Turtwig** | Grass | Classic (Starter/Evo) | STR | `200` | `missile` | Có | — |
| `E04O` | **Vulpix** | Fire | Classic (Starter/Evo) | INT | `200` | `missile` | Có | — |
| `P00A` | **Abomasnow** | Grass&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4QA` | **Aegislash** | Steel&Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P02A` | **Aerodactyl** | Rock&Flying | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | Mega Aerodactyl |
| `P03A` | **Alolan-Geodude** | Rock&Electric | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P04A` | **Alolan-Golem** | Rock&Electric | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P05A` | **Alolan-Graveler** | Rock&Electric | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P06A` | **Alolan-Raichu** | Electric&Psychic | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4MA` | **Alolan-Sandshrew** | Ice&Steel | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4NA` | **Alolan-Sandslash** | Ice&Steel | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P08A` | **Ampharos** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | Mega Ampharos |
| `P09A` | **Arbok** | Poison | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0BA` | **Baltoy** | Ground&Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0CA` | **Bayleef** | Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0EA` | **Bellossom** | Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4SA` | **Bisharp** | Dark&Steel | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0GA` | **Blissey** | Normal | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0HA` | **Bonsly** | Rock | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0IA` | **Breloom** | Grass&Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0KA` | **Carvanha** | Water&Dark | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0LA` | **Chandelure** | Ghost&Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0MA` | **Chansey** | Normal | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0NA` | **Chikorita** | Grass | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0OA` | **Chinchou** | Water&Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0PA` | **Claydol** | Ground&Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0QA` | **Clefable** | Fairy | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0RA` | **Clefairy** | Fairy | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0TA` | **Cradily** | Rock&Grass | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0UA` | **Croagunk** | Poison&Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0VA` | **Cubone** | Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0WA` | **Cyndaquil** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P0XA` | **Darmanitan** | Fire | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0YA` | **Darumaka** | Fire | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P0ZA` | **Deino** | Dark&Dragon | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P10A` | **Dewgong** | Water&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P11A` | **Diglett** | Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P12A` | **Ditto** | Normal | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4PA` | **Doublade** | Steel&Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P13A` | **Drowzee** | Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P14A` | **Dugtrio** | Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P15A` | **Dusclops** | Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P16A` | **Dusknoir** | Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P17A` | **Duskull** | Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4VA` | **Eevee** | Normal | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P18A` | **Ekans** | Poison | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P19A` | **Electabuzz** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1AA` | **Electivire** | Electric | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1BA` | **Electrike** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1CA` | **Elekid** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1EA` | **Farfetch'd** | Normal&Flying | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1FA` | **Feebas** | Water | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1GA` | **Flaaffy** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1HA` | **Flygon** | Ground&Dragon | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1IA` | **Gabite** | Dragon&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1KA` | **Galvantula** | Bug&Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1LA` | **Garchomp** | Dragon&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | Mega Garchomp |
| `P1NA` | **Gible** | Dragon&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1OA` | **Gloom** | Grass&Poison | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1PA` | **Golduck** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1QA` | **Granbull** | Fairy | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1SA` | **Heracross** | Bug&Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | Mega Heracross |
| `P4OA` | **Honedge** | Steel&Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P1UA` | **Hoothoot** | Normal&Flying | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1VA` | **Horsea** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1WA` | **Houndoom** | Dark&Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | Mega Houndoom |
| `P1XA` | **Houndour** | Dark&Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P1ZA` | **Hypno** | Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P22A` | **Joltik** | Bug&Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P23A` | **Jynx** | Ice&Psychic | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4TA` | **Kingambit** | Dark&Steel | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P24A` | **Kingdra** | Water&Dragon | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P27A` | **Lampent** | Ghost&Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P28A` | **Lanturn** | Water&Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P29A` | **Lapras** | Water&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2BA` | **Leafeon** | Grass | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2CA` | **Lileep** | Rock&Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2DA` | **Litwick** | Ghost&Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2EA` | **Lombre** | Water&Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2FA` | **Lotad** | Water&Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2GA` | **Ludicolo** | Water&Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2HA` | **Magby** | Fire | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2IA` | **Magcargo** | Fire&Rock | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2JA` | **Magmar** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2KA` | **Magmortar** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4WA` | **Magnemite** | Electric&Steel | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2MA` | **Mamoswine** | Ice&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2NA` | **Manectric** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | Mega Manectric |
| `P2OA` | **Mareep** | Electric | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2PA` | **Marowak** | Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `PV0A` | **Meganium** | Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2QA` | **Meowth** | Normal | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2TA` | **Milotic** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2WA` | **Mr. Mime** | Psychic&Fairy | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P2XA` | **Nincada** | Bug&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2YA` | **Ninjask** | Bug&Flying | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P2ZA` | **Noctowl** | Normal&Flying | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P30A` | **Oddish** | Grass&Poison | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4RA` | **Pawniard** | Dark&Steel | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P31A` | **Persian** | Normal | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P32A` | **Piloswine** | Ice&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P34A` | **Politoed** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4YA` | **Poliwag** | Water | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4ZA` | **Poliwhirl** | Water | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P35A` | **Porygon** | Normal | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `PV1A` | **Porygon2** | Normal | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P36A` | **Psyduck** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P38A` | **Quilava** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P51A` | **Rhydon** | Ground&Rock | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P50A` | **Rhyhorn** | Ground&Rock | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3CA` | **Rhyperior** | Ground&Rock | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3DA` | **Sableye** | Dark&Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3GA` | **Seadra** | Water | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P3HA` | **Seel** | Water | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3IA` | **Sharpedo** | Water&Dark | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | Mega Sharpedo |
| `P3JA` | **Shedinja** | Bug&Ghost | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3LA` | **Shroomish** | Grass | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3MA` | **Sirfetch'd** | Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3NA` | **Slowbro** | Water&Psychic | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | Mega Slowbro |
| `P3OA` | **Slowking** | Water&Psychic | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P3PA` | **Slowpoke** | Water&Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3QA` | **Slugma** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P3RA` | **Smoochum** | Ice&Psychic | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P3SA` | **Sneasel** | Dark&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3TA` | **Snorlax** | Normal | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3UA` | **Snover** | Grass&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3VA` | **Snubbull** | Fairy | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3WA` | **Sudowoodo** | Rock | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3YA` | **Swablu** | Normal&Flying | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P3ZA` | **Swinub** | Ice&Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P40A` | **Tangela** | Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P41A` | **Tangrowth** | Grass | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P42A` | **Tauros Aqua** | Fighting&Water | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P43A` | **Tauros Blaze** | Fighting&Fire | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P44A` | **Tauros Combat** | Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P45A` | **Togekiss** | Fairy&Flying | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P46A` | **Togepi** | Fairy | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P47A` | **Togetic** | Fairy&Flying | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P49A` | **Torkoal** | Fire | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4AA` | **Toxicroak** | Poison&Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4BA` | **Trapinch** | Ground | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4DA` | **Typhlosion** | Fire | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4EA` | **Tyrogue** | Fighting | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4FA` | **Vibrava** | Ground&Dragon | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4GA` | **Vileplume** | Grass&Poison | Gen 2-9 (Wild/Soul) | INT | `200` | `missile` | Có | — |
| `P4HA` | **Weavile** | Dark&Ice | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4JA` | **Wobbuffet** | Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4KA` | **Wynaut** | Psychic | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `P4LA` | **Zweilous** | Dark&Dragon | Gen 2-9 (Wild/Soul) | STR | `200` | `missile` | Có | — |
| `E01M` | **Nidoran** | Poison | Khác | STR | `200` | `missile` | Có | — |
