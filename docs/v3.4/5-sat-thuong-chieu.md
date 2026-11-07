# 5. Sát thương của 319 move học được (skill gốc, hiệu ứng, số liệu từ v3.4.1)

## Nguồn của chiêu
- **Dữ liệu chiêu** (tên, hệ, Power, vật lý/đặc biệt, Pokémon nào học được ở level nào): PokeAPI (`tools/learnsets.json`, làm từ v3.1 bằng `tools/learn_data.py`).
- **Cách chiêu chạy**: mỗi move là một skill có sẵn của Warcraft III, chọn theo hình dạng chiêu và Power (11 loại: Storm Bolt, Shadow Strike, Frost Nova, Carrion Swarm, Shockwave, Thunder Clap, War Stomp, Breath of Fire, Entangling Roots, Impale, Blizzard). Sát thương gốc theo Power (`tools/poke_data.py`, TEMPLATES).
- **Hiệu ứng hình ảnh**: model có sẵn của game. Đạn bay đổi theo hệ của chiêu (`ELEMENT_ART`), phần còn lại là hiệu ứng của skill gốc. Icon từ v3.4: icon có sẵn khớp tên chiêu (`4-icon-chieu.md`).

## Sát thương ra sao
1. **Sát thương gốc** = cột "Gốc" (D1, D2) trong bảng dưới.
2. **× chỉ số chính / 50** (chỉ số chính = STR hoặc INT, lấy cái lớn hơn; từ x0,1 đến x15). Tooltip trong game hiện đúng số này. Ví dụ chỉ số 600: x12, nên chiêu gốc 100 hiện 1200.
3. **× khắc hệ**: x2 khi khắc, x0,5 khi bị kháng, x0,25 khi miễn nhiễm (có chữ "Super effective!" / "Not very effective...").
4. **× Ability**:
   - của người đánh: Adaptability, Technician, Blaze…;
   - của mục tiêu: Thick Fat x0,5 với Fire/Ice; Multiscale x0,6 khi trên 80% máu; Levitate miễn Ground; Water/Volt Absorb hút chiêu; Magic Bounce chặn 20%;
   - **Sturdy / Sand Force**: một đòn lẽ ra hạ gục chỉ đưa mục tiêu về 15% máu, 60 giây một lần (Geodude, Onix, Steelix…).
5. **× thời tiết, item, Champion Aura** (Life Orb, Choice Specs, Assault Vest…).
6. **Giáp không giảm sát thương chiêu.** Bảng hệ số của map cho skill gây 100% lên mọi loại giáp, kể cả hero. Con số **vàng nổi lên** khi trúng là sát thương thật cuối cùng.

Vì vậy tooltip 1200 mà không hạ được quái 1000 máu thường là do một trong các trường hợp:
- bị kháng hệ (x0,5 → 600);
- Ability của mục tiêu (Sturdy, Multiscale, Thick Fat);
- quái elite (máu x1,6, sát thương x1,6);
- chiêu gây sát thương theo giây (cột "Theo giây": số trong tooltip là mỗi giây, không phải một lần).

| # | Move | Hệ | Loại | Power | Skill gốc | Hiệu ứng (model) | Gốc D1 / D2 | Theo giây | x2 (chỉ số 100) | x4 (chỉ số 200) | x8 (chỉ số 400) | x12 (chỉ số 600) | Mô tả |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Absorb | Grass | Đặc biệt | 20 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 1 | Acid | Poison | Đặc biệt | 40 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 2 | Acid Spray | Poison | Đặc biệt | 40 | Carrion Swarm | ChimaeraAcidMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 3 | Acrobatics | Flying | Vật lý | 55 | Carrion Swarm | ZigguratMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 4 | Aerial Ace | Flying | Vật lý | 60 | Carrion Swarm | ZigguratMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 5 | Aeroblast | Flying | Đặc biệt | 100 | Carrion Swarm | ZigguratMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 6 | Air Cutter | Flying | Đặc biệt | 60 | Thunder Clap | ThunderClapCaster | 150 |  | 300 | 600 | 1200 | 1800 | Deals 150 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 7 | Air Slash | Flying | Đặc biệt | 75 | Carrion Swarm | ZigguratMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 8 | Alluring Voice | Fairy | Đặc biệt | 80 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 9 | Ancient Power | Rock | Đặc biệt | 60 | Frost Nova | ThunderClapCaster | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 10 | Aqua Cutter | Water | Vật lý | 70 | Shadow Strike | WaterElementalMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 11 | Aqua Jet | Water | Vật lý | 40 | Shockwave | WaterElementalMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 12 | Aqua Tail | Water | Vật lý | 90 | Storm Bolt | WaterElementalMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 13 | Assurance | Dark | Vật lý | 60 | Shadow Strike | AvengerMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 14 | Astonish | Ghost | Vật lý | 30 | Shadow Strike | BansheeMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 15 | Aura Sphere | Fighting | Đặc biệt | 80 | Frost Nova | ThunderClapCaster | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 16 | Aurora Beam | Ice | Đặc biệt | 65 | Carrion Swarm | LichMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 17 | Avalanche | Ice | Vật lý | 60 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 18 | Axe Kick | Fighting | Vật lý | 120 | War Stomp | WarStompCaster | 450 |  | 900 | 1800 | 3600 | 5400 | Deals 450 damage to every enemy around and stuns for 2 seconds. |
| 19 | Belch | Poison | Đặc biệt | 120 | Carrion Swarm | ChimaeraAcidMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 20 | Bite | Dark | Vật lý | 60 | Storm Bolt | AvengerMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 21 | Blast Burn | Fire | Đặc biệt | 150 | Blizzard | (effect of Blizzard) | 170 |  | 340 | 680 | 1360 | 2040 | Calls 12 waves that deal 170 damage each to every enemy in an area. |
| 22 | Blaze Kick | Fire | Vật lý | 85 | Storm Bolt | RedDragonMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 23 | Blizzard | Ice | Đặc biệt | 110 | Thunder Clap | ThunderClapCaster | 350 |  | 700 | 1400 | 2800 | 4200 | Deals 350 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 24 | Body Press | Fighting | Vật lý | 80 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 25 | Body Slam | Normal | Vật lý | 85 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 26 | Bone Rush | Ground | Vật lý | 25 | Shockwave | ZigguratMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 27 | Bonemerang | Ground | Vật lý | 50 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 28 | Boomburst | Normal | Đặc biệt | 140 | Blizzard | (effect of Blizzard) | 130 |  | 260 | 520 | 1040 | 1560 | Calls 10 waves that deal 130 damage each to every enemy in an area. |
| 29 | Bounce | Flying | Vật lý | 85 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 30 | Brave Bird | Flying | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 31 | Breaking Swipe | Dragon | Vật lý | 60 | Shockwave | FrostWyrmMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 32 | Brick Break | Fighting | Vật lý | 75 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 33 | Brine | Water | Đặc biệt | 65 | Carrion Swarm | WaterElementalMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 34 | Brutal Swing | Dark | Vật lý | 60 | Storm Bolt | AvengerMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 35 | Bubble Beam | Water | Đặc biệt | 65 | Carrion Swarm | WaterElementalMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 36 | Bug Bite | Bug | Vật lý | 60 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 37 | Bug Buzz | Bug | Đặc biệt | 90 | Breath of Fire | ZigguratMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 38 | Bulldoze | Ground | Vật lý | 60 | War Stomp | WarStompCaster | 175 |  | 350 | 700 | 1400 | 2100 | Deals 175 damage to every enemy around and stuns for 1.25 seconds. |
| 39 | Bullet Punch | Steel | Vật lý | 40 | Storm Bolt | GryphonRiderMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 40 | Bullet Seed | Grass | Vật lý | 25 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 41 | Burning Jealousy | Fire | Đặc biệt | 70 | Breath of Fire | RedDragonMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 42 | Charge Beam | Electric | Đặc biệt | 50 | Carrion Swarm | FarseerMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 43 | Chilling Water | Water | Đặc biệt | 50 | Carrion Swarm | WaterElementalMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 44 | Clear Smog | Poison | Đặc biệt | 50 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 45 | Close Combat | Fighting | Vật lý | 120 | War Stomp | WarStompCaster | 450 |  | 900 | 1800 | 3600 | 5400 | Deals 450 damage to every enemy around and stuns for 2 seconds. |
| 46 | Confusion | Psychic | Đặc biệt | 50 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 47 | Covet | Normal | Vật lý | 60 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 48 | Crabhammer | Water | Vật lý | 100 | Storm Bolt | WaterElementalMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 49 | Cross Chop | Fighting | Vật lý | 100 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 50 | Cross Poison | Poison | Vật lý | 70 | Shadow Strike | ChimaeraAcidMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 51 | Crunch | Dark | Vật lý | 80 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 52 | Crush Claw | Normal | Vật lý | 75 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 53 | Cut | Normal | Vật lý | 50 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 54 | Dark Pulse | Dark | Đặc biệt | 80 | Carrion Swarm | AvengerMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 55 | Darkest Lariat | Dark | Vật lý | 85 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 56 | Dazzling Gleam | Fairy | Đặc biệt | 80 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 57 | Dig | Ground | Vật lý | 80 | Impale | (effect of Impale) | 250 |  | 500 | 1000 | 2000 | 3000 | Spikes burst out in a line: 250 damage to every enemy on the ground in it and a 1 second stun. |
| 58 | Disarming Voice | Fairy | Đặc biệt | 40 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 59 | Discharge | Electric | Đặc biệt | 80 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 60 | Dive | Water | Vật lý | 80 | Shockwave | WaterElementalMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 61 | Doom Desire | Steel | Đặc biệt | 140 | Carrion Swarm | GryphonRiderMissile | 700 |  | 1400 | 2800 | 5600 | 8400 | A huge wave dealing 700 damage to every enemy in its path. |
| 62 | Double Edge | Normal | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 63 | Double Hit | Normal | Vật lý | 35 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 64 | Double Kick | Fighting | Vật lý | 30 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 65 | Draco Meteor | Dragon | Đặc biệt | 130 | Carrion Swarm | FrostWyrmMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 66 | Dragon Ascent | Flying | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 67 | Dragon Breath | Dragon | Đặc biệt | 60 | Breath of Fire | FrostWyrmMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 68 | Dragon Claw | Dragon | Vật lý | 80 | Shadow Strike | FrostWyrmMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 69 | Dragon Pulse | Dragon | Đặc biệt | 85 | Carrion Swarm | FrostWyrmMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 70 | Dragon Rush | Dragon | Vật lý | 100 | Shockwave | FrostWyrmMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 71 | Dragon Tail | Dragon | Vật lý | 60 | Shockwave | FrostWyrmMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 72 | Drain Punch | Fighting | Vật lý | 75 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 73 | Draining Kiss | Fairy | Đặc biệt | 50 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 74 | Dream Eater | Psychic | Đặc biệt | 100 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 75 | Drill Peck | Flying | Vật lý | 80 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 76 | Drill Run | Ground | Vật lý | 80 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 77 | Dual Wingbeat | Flying | Vật lý | 40 | Carrion Swarm | ZigguratMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 78 | Dynamic Punch | Fighting | Vật lý | 100 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 79 | Earth Power | Ground | Đặc biệt | 90 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 80 | Earthquake | Ground | Vật lý | 100 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 81 | Echoed Voice | Normal | Đặc biệt | 40 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 82 | Electroweb | Electric | Đặc biệt | 55 | Frost Nova | BoltImpact | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 83 | Ember | Fire | Đặc biệt | 40 | Breath of Fire | RedDragonMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 84 | Energy Ball | Grass | Đặc biệt | 90 | Entangling Roots | (effect of Entangling Roots) | 65 | có | 130 | 260 | 520 | 780 | Roots the target for 3.5 seconds, dealing 65 damage per second. |
| 85 | Eruption | Fire | Đặc biệt | 150 | Blizzard | (effect of Blizzard) | 170 |  | 340 | 680 | 1360 | 2040 | Calls 12 waves that deal 170 damage each to every enemy in an area. |
| 86 | Expanding Force | Psychic | Đặc biệt | 80 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 87 | Explosion | Normal | Vật lý | 250 | War Stomp | WarStompCaster | 950 |  | 1900 | 3800 | 7600 | 11400 | Deals 950 damage to every enemy around and stuns for 3 seconds. |
| 88 | Extrasensory | Psychic | Đặc biệt | 80 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 89 | Extreme Speed | Normal | Vật lý | 80 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 90 | Facade | Normal | Vật lý | 70 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 91 | Fairy Wind | Fairy | Đặc biệt | 40 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 92 | Fake Out | Normal | Vật lý | 40 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 93 | False Swipe | Normal | Vật lý | 40 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 94 | Feint | Normal | Vật lý | 30 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 95 | Fell Stinger | Bug | Vật lý | 50 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 96 | Fire Blast | Fire | Đặc biệt | 110 | Thunder Clap | ThunderClapCaster | 350 |  | 700 | 1400 | 2800 | 4200 | Deals 350 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 97 | Fire Fang | Fire | Vật lý | 65 | Shadow Strike | RedDragonMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 98 | Fire Pledge | Fire | Đặc biệt | 80 | Breath of Fire | RedDragonMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 99 | Fire Punch | Fire | Vật lý | 75 | Storm Bolt | RedDragonMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 100 | Fire Spin | Fire | Đặc biệt | 35 | Breath of Fire | RedDragonMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 101 | First Impression | Bug | Vật lý | 90 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 102 | Flame Charge | Fire | Vật lý | 50 | Shockwave | RedDragonMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 103 | Flame Wheel | Fire | Vật lý | 60 | Storm Bolt | RedDragonMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 104 | Flamethrower | Fire | Đặc biệt | 90 | Breath of Fire | RedDragonMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 105 | Flare Blitz | Fire | Vật lý | 120 | Shockwave | RedDragonMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 106 | Flash Cannon | Steel | Đặc biệt | 80 | Carrion Swarm | GryphonRiderMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 107 | Flip Turn | Water | Vật lý | 60 | Storm Bolt | WaterElementalMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 108 | Fly | Flying | Vật lý | 90 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 109 | Focus Blast | Fighting | Đặc biệt | 120 | Carrion Swarm | ZigguratMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 110 | Focus Punch | Fighting | Vật lý | 150 | War Stomp | WarStompCaster | 950 |  | 1900 | 3800 | 7600 | 11400 | Deals 950 damage to every enemy around and stuns for 3 seconds. |
| 111 | Force Palm | Fighting | Vật lý | 60 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 112 | Foul Play | Dark | Vật lý | 95 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 113 | Freeze Dry | Ice | Đặc biệt | 70 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 114 | Frenzy Plant | Grass | Đặc biệt | 150 | Blizzard | (effect of Blizzard) | 170 |  | 340 | 680 | 1360 | 2040 | Calls 12 waves that deal 170 damage each to every enemy in an area. |
| 115 | Fury Attack | Normal | Vật lý | 15 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 116 | Fury Cutter | Bug | Vật lý | 40 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 117 | Fury Swipes | Normal | Vật lý | 18 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 118 | Future Sight | Psychic | Đặc biệt | 120 | Carrion Swarm | FaerieDragonMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 119 | Giga Drain | Grass | Đặc biệt | 75 | Entangling Roots | (effect of Entangling Roots) | 65 | có | 130 | 260 | 520 | 780 | Roots the target for 3.5 seconds, dealing 65 damage per second. |
| 120 | Giga Impact | Normal | Vật lý | 150 | Shockwave | ZigguratMissile | 1000 |  | 2000 | 4000 | 8000 | 12000 | A devastating line attack dealing 1000 damage to every enemy in it. |
| 121 | Grass Pledge | Grass | Đặc biệt | 80 | Entangling Roots | (effect of Entangling Roots) | 65 | có | 130 | 260 | 520 | 780 | Roots the target for 3.5 seconds, dealing 65 damage per second. |
| 122 | Grassy Glide | Grass | Vật lý | 55 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 123 | Gunk Shot | Poison | Vật lý | 120 | Shockwave | ChimaeraAcidMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 124 | Gust | Flying | Đặc biệt | 40 | Carrion Swarm | ZigguratMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 125 | Hammer Arm | Fighting | Vật lý | 100 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 126 | Head Smash | Rock | Vật lý | 150 | Shockwave | AncientProtectorMissile | 1000 |  | 2000 | 4000 | 8000 | 12000 | A devastating line attack dealing 1000 damage to every enemy in it. |
| 127 | Headbutt | Normal | Vật lý | 70 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 128 | Heat Wave | Fire | Đặc biệt | 95 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 129 | Hex | Ghost | Đặc biệt | 65 | Frost Nova | DeathCoilSpecialArt | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 130 | Hidden Power | Normal | Đặc biệt | 60 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 131 | High Horsepower | Ground | Vật lý | 95 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 132 | High Jump Kick | Fighting | Vật lý | 130 | War Stomp | WarStompCaster | 450 |  | 900 | 1800 | 3600 | 5400 | Deals 450 damage to every enemy around and stuns for 2 seconds. |
| 133 | Horn Attack | Normal | Vật lý | 65 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 134 | Hurricane | Flying | Đặc biệt | 110 | Thunder Clap | ThunderClapCaster | 350 |  | 700 | 1400 | 2800 | 4200 | Deals 350 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 135 | Hydro Cannon | Water | Đặc biệt | 150 | Carrion Swarm | WaterElementalMissile | 950 |  | 1900 | 3800 | 7600 | 11400 | A huge wave dealing 950 damage to every enemy in its path. |
| 136 | Hydro Pump | Water | Đặc biệt | 110 | Carrion Swarm | WaterElementalMissile | 350 |  | 700 | 1400 | 2800 | 4200 | Sends a wave that deals 350 damage to every enemy in a line. |
| 137 | Hyper Beam | Normal | Đặc biệt | 150 | Carrion Swarm | ZigguratMissile | 950 |  | 1900 | 3800 | 7600 | 11400 | A huge wave dealing 950 damage to every enemy in its path. |
| 138 | Hyper Fang | Normal | Vật lý | 80 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 139 | Hyper Voice | Normal | Đặc biệt | 90 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 140 | Ice Beam | Ice | Đặc biệt | 90 | Carrion Swarm | LichMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 141 | Ice Fang | Ice | Vật lý | 65 | Shadow Strike | LichMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 142 | Ice Punch | Ice | Vật lý | 75 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 143 | Ice Shard | Ice | Vật lý | 40 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 144 | Ice Spinner | Ice | Vật lý | 80 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 145 | Icicle Crash | Ice | Vật lý | 85 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 146 | Icicle Spear | Ice | Vật lý | 25 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 147 | Icy Wind | Ice | Đặc biệt | 55 | Thunder Clap | ThunderClapCaster | 150 |  | 300 | 600 | 1200 | 1800 | Deals 150 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 148 | Incinerate | Fire | Đặc biệt | 60 | Breath of Fire | RedDragonMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 149 | Inferno | Fire | Đặc biệt | 100 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 150 | Infestation | Bug | Đặc biệt | 20 | Breath of Fire | ZigguratMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 151 | Iron Head | Steel | Vật lý | 80 | Shockwave | GryphonRiderMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 152 | Iron Tail | Steel | Vật lý | 100 | Storm Bolt | GryphonRiderMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 153 | Judgment | Normal | Đặc biệt | 100 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 154 | Knock Off | Dark | Vật lý | 65 | Shadow Strike | AvengerMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 155 | Kowtow Cleave | Dark | Vật lý | 85 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 156 | Lash Out | Dark | Vật lý | 75 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 157 | Last Resort | Normal | Vật lý | 140 | Shockwave | ZigguratMissile | 750 |  | 1500 | 3000 | 6000 | 9000 | A devastating line attack dealing 750 damage to every enemy in it. |
| 158 | Lava Plume | Fire | Đặc biệt | 80 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 159 | Leaf Blade | Grass | Vật lý | 90 | Shadow Strike | GreenDragonMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 160 | Leaf Storm | Grass | Đặc biệt | 130 | Blizzard | (effect of Blizzard) | 90 |  | 180 | 360 | 720 | 1080 | Calls 8 waves that deal 90 damage each to every enemy in an area. |
| 161 | Leafage | Grass | Vật lý | 40 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 162 | Leech Life | Bug | Vật lý | 80 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 163 | Lick | Ghost | Vật lý | 30 | Shadow Strike | BansheeMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 164 | Liquidation | Water | Vật lý | 85 | Storm Bolt | WaterElementalMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 165 | Low Sweep | Fighting | Vật lý | 65 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 166 | Lunge | Bug | Vật lý | 80 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 167 | Mach Punch | Fighting | Vật lý | 40 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 168 | Magical Leaf | Grass | Đặc biệt | 60 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 169 | Mega Drain | Grass | Đặc biệt | 40 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 170 | Mega Kick | Normal | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 171 | Mega Punch | Normal | Vật lý | 80 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 172 | Megahorn | Bug | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 173 | Metal Claw | Steel | Vật lý | 50 | Shadow Strike | GryphonRiderMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 174 | Meteor Assault | Fighting | Vật lý | 150 | War Stomp | WarStompCaster | 950 |  | 1900 | 3800 | 7600 | 11400 | Deals 950 damage to every enemy around and stuns for 3 seconds. |
| 175 | Meteor Beam | Rock | Đặc biệt | 120 | Carrion Swarm | AncientProtectorMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 176 | Meteor Mash | Steel | Vật lý | 90 | Storm Bolt | GryphonRiderMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 177 | Misty Explosion | Fairy | Đặc biệt | 100 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 178 | Moonblast | Fairy | Đặc biệt | 95 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 179 | Mud Shot | Ground | Đặc biệt | 55 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 180 | Mud Slap | Ground | Đặc biệt | 20 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 181 | Muddy Water | Water | Đặc biệt | 90 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 182 | Mystical Fire | Fire | Đặc biệt | 75 | Breath of Fire | RedDragonMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 183 | Night Slash | Dark | Vật lý | 70 | Shadow Strike | AvengerMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 184 | Origin Pulse | Water | Đặc biệt | 110 | Carrion Swarm | WaterElementalMissile | 350 |  | 700 | 1400 | 2800 | 4200 | Sends a wave that deals 350 damage to every enemy in a line. |
| 185 | Outrage | Dragon | Vật lý | 120 | Shockwave | FrostWyrmMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 186 | Overheat | Fire | Đặc biệt | 130 | Breath of Fire | RedDragonMissile | 275 / 35 | có | 550 / 70 | 1100 / 140 | 2200 / 280 | 3300 / 420 | Breathes a cone dealing 275 damage to every enemy in it, then 35 damage per second for 5 seconds. |
| 187 | Pay Day | Normal | Vật lý | 40 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 188 | Payback | Dark | Vật lý | 50 | Storm Bolt | AvengerMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 189 | Peck | Flying | Vật lý | 35 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 190 | Petal Blizzard | Grass | Vật lý | 90 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 191 | Petal Dance | Grass | Đặc biệt | 120 | Blizzard | (effect of Blizzard) | 90 |  | 180 | 360 | 720 | 1080 | Calls 8 waves that deal 90 damage each to every enemy in an area. |
| 192 | Phantom Force | Ghost | Vật lý | 90 | Shadow Strike | BansheeMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 193 | Pin Missile | Bug | Vật lý | 25 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 194 | Play Rough | Fairy | Vật lý | 90 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 195 | Pluck | Flying | Vật lý | 60 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 196 | Poison Fang | Poison | Vật lý | 50 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 197 | Poison Jab | Poison | Vật lý | 80 | Shadow Strike | ChimaeraAcidMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 198 | Poison Sting | Poison | Vật lý | 15 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 199 | Poison Tail | Poison | Vật lý | 50 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 200 | Pollen Puff | Bug | Đặc biệt | 90 | Breath of Fire | ZigguratMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 201 | Poltergeist | Ghost | Vật lý | 110 | Shadow Strike | BansheeMissile | 250 / 40 | có | 500 / 80 | 1000 / 160 | 2000 / 320 | 3000 / 480 | Deals 250 damage, then 40 damage every few seconds and slows. |
| 202 | Pounce | Bug | Vật lý | 50 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 203 | Pound | Normal | Vật lý | 40 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 204 | Powder Snow | Ice | Đặc biệt | 40 | Breath of Fire | LichMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 205 | Power Gem | Rock | Đặc biệt | 80 | Frost Nova | ThunderClapCaster | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 206 | Power Whip | Grass | Vật lý | 120 | Shockwave | GreenDragonMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 207 | Precipice Blades | Ground | Vật lý | 120 | War Stomp | WarStompCaster | 450 |  | 900 | 1800 | 3600 | 5400 | Deals 450 damage to every enemy around and stuns for 2 seconds. |
| 208 | Psybeam | Psychic | Đặc biệt | 65 | Carrion Swarm | FaerieDragonMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 209 | Psychic | Psychic | Đặc biệt | 90 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 210 | Psychic Fangs | Psychic | Vật lý | 85 | Shadow Strike | FaerieDragonMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 211 | Psychic Noise | Psychic | Đặc biệt | 75 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 212 | Psycho Boost | Psychic | Đặc biệt | 140 | Carrion Swarm | FaerieDragonMissile | 700 |  | 1400 | 2800 | 5600 | 8400 | A huge wave dealing 700 damage to every enemy in its path. |
| 213 | Psycho Cut | Psychic | Vật lý | 70 | Shadow Strike | FaerieDragonMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 214 | Psyshock | Psychic | Đặc biệt | 80 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 215 | Psystrike | Psychic | Đặc biệt | 100 | Frost Nova | FrostNovaTarget | 300 / 200 |  | 600 / 400 | 1200 / 800 | 2400 / 1600 | 3600 / 2400 | Deals 300 damage to the target and 200 to every enemy around it, slowing for 3 seconds. |
| 216 | Pursuit | Dark | Vật lý | 40 | Storm Bolt | AvengerMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 217 | Quick Attack | Normal | Vật lý | 40 | Shockwave | ZigguratMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 218 | Rage | Normal | Vật lý | 20 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 219 | Rage Fist | Ghost | Vật lý | 50 | Shadow Strike | BansheeMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 220 | Raging Bull | Normal | Vật lý | 90 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 221 | Rapid Spin | Normal | Vật lý | 50 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 222 | Razor Leaf | Grass | Vật lý | 55 | War Stomp | WarStompCaster | 175 |  | 350 | 700 | 1400 | 2100 | Deals 175 damage to every enemy around and stuns for 1.25 seconds. |
| 223 | Razor Shell | Water | Vật lý | 75 | Storm Bolt | WaterElementalMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 224 | Retaliate | Normal | Vật lý | 70 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 225 | Revenge | Fighting | Vật lý | 60 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 226 | Roar Of Time | Dragon | Đặc biệt | 150 | Carrion Swarm | FrostWyrmMissile | 950 |  | 1900 | 3800 | 7600 | 11400 | A huge wave dealing 950 damage to every enemy in its path. |
| 227 | Rock Blast | Rock | Vật lý | 25 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 228 | Rock Slide | Rock | Vật lý | 75 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 229 | Rock Throw | Rock | Vật lý | 50 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 230 | Rock Tomb | Rock | Vật lý | 60 | War Stomp | WarStompCaster | 175 |  | 350 | 700 | 1400 | 2100 | Deals 175 damage to every enemy around and stuns for 1.25 seconds. |
| 231 | Rock Wrecker | Rock | Vật lý | 150 | War Stomp | WarStompCaster | 950 |  | 1900 | 3800 | 7600 | 11400 | Deals 950 damage to every enemy around and stuns for 3 seconds. |
| 232 | Rollout | Rock | Vật lý | 30 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 233 | Round | Normal | Đặc biệt | 60 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 234 | Sacred Fire | Fire | Vật lý | 100 | Storm Bolt | RedDragonMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 235 | Sacred Sword | Fighting | Vật lý | 90 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 236 | Sand Tomb | Ground | Vật lý | 35 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 237 | Scald | Water | Đặc biệt | 80 | Carrion Swarm | WaterElementalMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 238 | Scale Shot | Dragon | Vật lý | 25 | Shockwave | FrostWyrmMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 239 | Scorching Sands | Ground | Đặc biệt | 70 | Impale | (effect of Impale) | 250 |  | 500 | 1000 | 2000 | 3000 | Spikes burst out in a line: 250 damage to every enemy on the ground in it and a 1 second stun. |
| 240 | Scratch | Normal | Vật lý | 40 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 241 | Seed Bomb | Grass | Vật lý | 80 | Entangling Roots | (effect of Entangling Roots) | 65 | có | 130 | 260 | 520 | 780 | Roots the target for 3.5 seconds, dealing 65 damage per second. |
| 242 | Self Destruct | Normal | Vật lý | 200 | War Stomp | WarStompCaster | 950 |  | 1900 | 3800 | 7600 | 11400 | Deals 950 damage to every enemy around and stuns for 3 seconds. |
| 243 | Shadow Ball | Ghost | Đặc biệt | 80 | Frost Nova | DeathCoilSpecialArt | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 244 | Shadow Claw | Ghost | Vật lý | 70 | Shadow Strike | BansheeMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 245 | Shadow Punch | Ghost | Vật lý | 60 | Shadow Strike | BansheeMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 246 | Shadow Sneak | Ghost | Vật lý | 40 | Shadow Strike | BansheeMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 247 | Shock Wave | Electric | Đặc biệt | 60 | Frost Nova | BoltImpact | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 248 | Skitter Smack | Bug | Vật lý | 70 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 249 | Sky Attack | Flying | Vật lý | 140 | Shockwave | ZigguratMissile | 750 |  | 1500 | 3000 | 6000 | 9000 | A devastating line attack dealing 750 damage to every enemy in it. |
| 250 | Slam | Normal | Vật lý | 80 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 251 | Slash | Normal | Vật lý | 70 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 252 | Sludge Bomb | Poison | Đặc biệt | 90 | Breath of Fire | ChimaeraAcidMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 253 | Sludge Wave | Poison | Đặc biệt | 95 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 254 | Smack Down | Rock | Vật lý | 50 | Impale | (effect of Impale) | 150 |  | 300 | 600 | 1200 | 1800 | Spikes burst out in a line: 150 damage to every enemy on the ground in it and a 0.75 second stun. |
| 255 | Smart Strike | Steel | Vật lý | 70 | Storm Bolt | GryphonRiderMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 256 | Smog | Poison | Đặc biệt | 30 | Shadow Strike | ChimaeraAcidMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 257 | Snarl | Dark | Đặc biệt | 55 | Thunder Clap | ThunderClapCaster | 150 |  | 300 | 600 | 1200 | 1800 | Deals 150 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 258 | Snore | Normal | Đặc biệt | 50 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 259 | Solar Beam | Grass | Đặc biệt | 120 | Carrion Swarm | GreenDragonMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 260 | Solar Blade | Grass | Vật lý | 125 | Shockwave | GreenDragonMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 261 | Spacial Rend | Dragon | Đặc biệt | 100 | Breath of Fire | FrostWyrmMissile | 200 / 25 | có | 400 / 50 | 800 / 100 | 1600 / 200 | 2400 / 300 | Breathes a cone dealing 200 damage to every enemy in it, then 25 damage per second for 5 seconds. |
| 262 | Spark | Electric | Vật lý | 65 | Storm Bolt | FarseerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 263 | Steel Beam | Steel | Đặc biệt | 140 | Carrion Swarm | GryphonRiderMissile | 700 |  | 1400 | 2800 | 5600 | 8400 | A huge wave dealing 700 damage to every enemy in its path. |
| 264 | Steel Wing | Steel | Vật lý | 70 | Storm Bolt | GryphonRiderMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 265 | Stomp | Normal | Vật lý | 65 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 266 | Stomping Tantrum | Ground | Vật lý | 75 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 267 | Stone Edge | Rock | Vật lý | 100 | Impale | (effect of Impale) | 250 |  | 500 | 1000 | 2000 | 3000 | Spikes burst out in a line: 250 damage to every enemy on the ground in it and a 1 second stun. |
| 268 | Stored Power | Psychic | Đặc biệt | 20 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 269 | Storm Throw | Fighting | Vật lý | 60 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 270 | Strength | Normal | Vật lý | 80 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 271 | Struggle Bug | Bug | Đặc biệt | 50 | Breath of Fire | ZigguratMissile | 125 / 15 | có | 250 / 30 | 500 / 60 | 1000 / 120 | 1500 / 180 | Breathes a cone dealing 125 damage to every enemy in it, then 15 damage per second for 5 seconds. |
| 272 | Submission | Fighting | Vật lý | 80 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 273 | Sucker Punch | Dark | Vật lý | 70 | Shadow Strike | AvengerMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 274 | Supercell Slam | Electric | Vật lý | 100 | War Stomp | WarStompCaster | 275 |  | 550 | 1100 | 2200 | 3300 | Deals 275 damage to every enemy around and stuns for 1.5 seconds. |
| 275 | Superpower | Fighting | Vật lý | 120 | War Stomp | WarStompCaster | 450 |  | 900 | 1800 | 3600 | 5400 | Deals 450 damage to every enemy around and stuns for 2 seconds. |
| 276 | Surf | Water | Đặc biệt | 90 | Thunder Clap | ThunderClapCaster | 250 |  | 500 | 1000 | 2000 | 3000 | Deals 250 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 277 | Swift | Normal | Đặc biệt | 60 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 278 | Tackle | Normal | Vật lý | 40 | Shockwave | ZigguratMissile | 175 |  | 350 | 700 | 1400 | 2100 | Strikes in a line, dealing 175 damage to every enemy in it. |
| 279 | Take Down | Normal | Vật lý | 90 | Shockwave | ZigguratMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 280 | Temper Flare | Fire | Vật lý | 75 | Storm Bolt | RedDragonMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 281 | Tera Blast | Normal | Đặc biệt | 80 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 282 | Thief | Dark | Vật lý | 60 | Shadow Strike | AvengerMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 283 | Thrash | Normal | Vật lý | 120 | Shockwave | ZigguratMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 284 | Throat Chop | Dark | Vật lý | 80 | Storm Bolt | AvengerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 285 | Thunder | Electric | Đặc biệt | 110 | Thunder Clap | ThunderClapCaster | 350 |  | 700 | 1400 | 2800 | 4200 | Deals 350 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 286 | Thunder Fang | Electric | Vật lý | 65 | Shadow Strike | FarseerMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 287 | Thunder Punch | Electric | Vật lý | 75 | Storm Bolt | FarseerMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 288 | Thunder Shock | Electric | Đặc biệt | 40 | Frost Nova | BoltImpact | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 289 | Thunderbolt | Electric | Đặc biệt | 90 | Frost Nova | BoltImpact | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 290 | Trailblaze | Grass | Vật lý | 50 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 291 | Tri Attack | Normal | Đặc biệt | 80 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 292 | Triple Axel | Ice | Vật lý | 20 | Frost Nova | FrostNovaTarget | 200 / 125 |  | 400 / 250 | 800 / 500 | 1600 / 1000 | 2400 / 1500 | Deals 200 damage to the target and 125 to every enemy around it, slowing for 3 seconds. |
| 293 | Twineedle | Bug | Vật lý | 25 | Shadow Strike | ZigguratMissile | 100 / 20 | có | 200 / 40 | 400 / 80 | 800 / 160 | 1200 / 240 | Deals 100 damage, then 20 damage every few seconds and slows. |
| 294 | Twister | Dragon | Đặc biệt | 40 | Thunder Clap | ThunderClapCaster | 150 |  | 300 | 600 | 1200 | 1800 | Deals 150 damage to every enemy around the user and slows it by 40% for 3 seconds. |
| 295 | U Turn | Bug | Vật lý | 70 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 296 | Upper Hand | Fighting | Vật lý | 65 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 297 | Uproar | Normal | Đặc biệt | 90 | Frost Nova | StarfallTarget | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 298 | Vacuum Wave | Fighting | Đặc biệt | 40 | Frost Nova | ThunderClapCaster | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 299 | Venoshock | Poison | Đặc biệt | 65 | Shadow Strike | ChimaeraAcidMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 300 | Vice Grip | Normal | Vật lý | 55 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 301 | Vine Whip | Grass | Vật lý | 45 | Entangling Roots | (effect of Entangling Roots) | 40 | có | 80 | 160 | 320 | 480 | Roots the target for 3 seconds, dealing 40 damage per second. |
| 302 | Vital Throw | Fighting | Vật lý | 70 | Storm Bolt | ZigguratMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 303 | Volt Switch | Electric | Đặc biệt | 70 | Frost Nova | BoltImpact | 190 / 60 |  | 380 / 120 | 760 / 240 | 1520 / 480 | 2280 / 720 | Blasts the target: 190 damage to every enemy around it, +60 to the target. |
| 304 | Water Gun | Water | Đặc biệt | 40 | Carrion Swarm | WaterElementalMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 305 | Water Pledge | Water | Đặc biệt | 80 | Carrion Swarm | WaterElementalMissile | 250 |  | 500 | 1000 | 2000 | 3000 | Sends a wave that deals 250 damage to every enemy in a line. |
| 306 | Water Pulse | Water | Đặc biệt | 60 | Carrion Swarm | WaterElementalMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 307 | Water Spout | Water | Đặc biệt | 150 | Blizzard | (effect of Blizzard) | 170 |  | 340 | 680 | 1360 | 2040 | Calls 12 waves that deal 170 damage each to every enemy in an area. |
| 308 | Waterfall | Water | Vật lý | 80 | Storm Bolt | WaterElementalMissile | 325 |  | 650 | 1300 | 2600 | 3900 | Deals 325 damage to a target and stuns it for 1.25 seconds. |
| 309 | Wave Crash | Water | Vật lý | 120 | Shockwave | WaterElementalMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 310 | Weather Ball | Normal | Đặc biệt | 50 | Frost Nova | StarfallTarget | 120 / 40 |  | 240 / 80 | 480 / 160 | 960 / 320 | 1440 / 480 | Blasts the target: 120 damage to every enemy around it, +40 to the target. |
| 311 | Whirlpool | Water | Đặc biệt | 35 | Carrion Swarm | WaterElementalMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 312 | Wild Charge | Electric | Vật lý | 90 | Shockwave | FarseerMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |
| 313 | Wing Attack | Flying | Vật lý | 60 | Carrion Swarm | ZigguratMissile | 150 |  | 300 | 600 | 1200 | 1800 | Sends a wave that deals 150 damage to every enemy in a line. |
| 314 | Wood Hammer | Grass | Vật lý | 120 | Shockwave | GreenDragonMissile | 500 |  | 1000 | 2000 | 4000 | 6000 | A devastating line attack dealing 500 damage to every enemy in it. |
| 315 | Wrap | Normal | Vật lý | 15 | Storm Bolt | ZigguratMissile | 200 |  | 400 | 800 | 1600 | 2400 | Deals 200 damage to a target and stuns it for 1 seconds. |
| 316 | X Scissor | Bug | Vật lý | 80 | Shadow Strike | ZigguratMissile | 175 / 30 | có | 350 / 60 | 700 / 120 | 1400 / 240 | 2100 / 360 | Deals 175 damage, then 30 damage every few seconds and slows. |
| 317 | Zap Cannon | Electric | Đặc biệt | 120 | Carrion Swarm | FarseerMissile | 450 |  | 900 | 1800 | 3600 | 5400 | A huge wave dealing 450 damage to every enemy in its path. |
| 318 | Zen Headbutt | Psychic | Vật lý | 80 | Shockwave | FaerieDragonMissile | 275 |  | 550 | 1100 | 2200 | 3300 | Strikes in a line, dealing 275 damage to every enemy in it. |

## Move của từng Pokémon (level học được)

| Pokémon | Hệ | Move (level) |
|---|---|---|
| Abomasnow | Grass/Ice | Ice Punch (1), Leafage (1), Powder Snow (1), Ice Shard (15), Razor Leaf (20), Icy Wind (25), Wood Hammer (43), Blizzard (49) |
| Absol | Dark | Quick Attack (1), Knock Off (10), Slash (25) |
| Aegislash | Steel/Ghost | Head Smash (1), Sacred Sword (1), Iron Head (1), Night Slash (1), Retaliate (1), Slash (1), Aerial Ace (1), Shadow Sneak (1) |
| Aerodactyl | Rock/Flying | Ancient Power (1), Rock Slide (20), Crunch (30), Iron Head (35), Take Down (40), Stone Edge (45), Hyper Beam (55), Giga Impact (60) |
| Alakazam | Psychic | Psybeam (5), Psycho Cut (20), Psyshock (30) |
| Alolan-Geodude | Rock/Electric | Spark (12), Smack Down (18), Thunder Punch (22), Self Destruct (24), Discharge (34), Explosion (36), Double Edge (40), Stone Edge (42) |
| Alolan-Golem | Rock/Electric | Spark (12), Smack Down (18), Thunder Punch (22), Self Destruct (24), Discharge (40), Explosion (44), Double Edge (50), Stone Edge (54) |
| Alolan-Graveler | Rock/Electric | Spark (12), Smack Down (18), Thunder Punch (22), Self Destruct (24), Discharge (40), Explosion (44), Double Edge (50), Stone Edge (54) |
| Alolan-Raichu | Electric/Psychic | Psychic (1), Discharge (1), Thunder (1), Iron Tail (1), Spark (1), Quick Attack (1), Thunder Shock (1), Thunderbolt (5) |
| Alolan-Sandshrew | Ice/Steel | Scratch (1), Powder Snow (6), Rapid Spin (15), Metal Claw (18), Swift (21), Slash (30), Iron Head (33), Blizzard (45) |
| Alolan-Sandslash | Ice/Steel | Icicle Spear (1), Icicle Crash (1), Slash (1), Metal Claw (1) |
| Altaria | Dragon/Flying | Dragon Pulse (1), Pluck (1), Disarming Voice (1), Round (16), Dragon Breath (20), Take Down (38), Moonblast (44), Sky Attack (56) |
| Ampharos | Electric | Thunder Punch (1), Dragon Pulse (1), Fire Punch (1), Take Down (20), Power Gem (35), Discharge (40), Dazzling Gleam (51), Thunder (62) |
| Arbok | Poison | Crunch (1), Fire Fang (1), Ice Fang (1), Thunder Fang (1), Bite (1), Sludge Bomb (39), Belch (48), Gunk Shot (63) |
| Arcanine | Fire | Extreme Speed (1), Flare Blitz (1), Play Rough (1), Crunch (1), Take Down (1), Retaliate (1), Fire Fang (1), Flamethrower (5) |
| Arceus | God | Earth Power (20), Extreme Speed (40), Future Sight (60), Judgment (100) |
| Articuno | Ice/Flying | Gust (1), Powder Snow (5), Ancient Power (25), Freeze Dry (35), Ice Beam (45), Hurricane (55) |
| Bagon | Dragon/Flying | Bite (5), Headbutt (15), Crunch (25), Zen Headbutt (35), Flamethrower (45), Outrage (50), Double Edge (55) |
| Baltoy | Ground/Psychic | Rapid Spin (3), Rock Tomb (9), Psybeam (15), Ancient Power (18), Extrasensory (27), Earth Power (30), Self Destruct (33), Explosion (42) |
| Bayleef | Grass | Razor Leaf (1), Tackle (1), Magical Leaf (22), Body Slam (40), Giga Drain (50), Solar Beam (54) |
| Beedrill | Bug/Poison | Twineedle (1), Rage (14), Pursuit (17), Venoshock (23), Assurance (26), Poison Jab (35), Fell Stinger (44) |
| Beldum | Steel/Psychic | Tackle (1) |
| Bellossom | Grass | Petal Blizzard (1), Petal Dance (1), Moonblast (1), Giga Drain (1), Acid (1), Mega Drain (1), Absorb (1) |
| Bellsprout | Grass/Poison | Vine Whip (1), Wrap (11), Acid (23), Knock Off (27), Razor Leaf (39), Poison Jab (41), Slam (47), Power Whip (52) |
| Bisharp | Dark/Steel | Metal Claw (1), Scratch (1), Fury Cutter (1), Assurance (25), Slash (35), Night Slash (40), Retaliate (50), Iron Head (57) |
| Blastoise | Water | Flash Cannon (1), Tackle (1), Rapid Spin (9), Bite (12), Wave Crash (56) |
| Blaziken | Fire/Fighting | Quick Attack (1), Flame Charge (9), Aerial Ace (20), Slash (25), Bounce (30), Flare Blitz (56), Brave Bird (63) |
| Blissey | Normal | Covet (1), Disarming Voice (1), Pound (1), Echoed Voice (8), Take Down (24), Double Edge (40), Last Resort (48) |
| Bonsly | Rock | Rock Throw (8), Rock Tomb (20), Sucker Punch (28), Rock Slide (32), Double Edge (44) |
| Breloom | Grass/Fighting | Mach Punch (1), Tackle (1), Headbutt (15), Force Palm (28), Brick Break (39), Seed Bomb (44), Dynamic Punch (50), Focus Punch (55) |
| Bulbasaur | Grass/Poison | Tackle (1), Vine Whip (3), Razor Leaf (12), Seed Bomb (18), Take Down (21), Power Whip (33), Solar Beam (36) |
| Butterfree | Bug/Flying | Gust (1), Tackle (1), Confusion (8), Psybeam (16), Air Slash (24), Bug Buzz (32) |
| Buzzwole | Bug/Fighting | Fell Stinger (10), Vital Throw (15), Mega Punch (35), Lunge (40), Dynamic Punch (50), Hammer Arm (60), Superpower (65), Focus Punch (70) |
| Carvanha | Water/Dark | Aqua Jet (1), Poison Fang (4), Bite (16), Ice Fang (20), Crunch (32), Liquidation (40), Take Down (44) |
| Caterpie | Bug | Tackle (1) |
| Celebi | Psychic/Grass | Confusion (1), Magical Leaf (10), Ancient Power (30), Future Sight (70), Leaf Storm (90) |
| Chandelure | Ghost/Fire | Overheat (1), Shadow Ball (1), Hex (1), Inferno (1), Ember (1), Astonish (1), Fire Spin (1), Smog (1) |
| Chansey | Normal | Covet (1), Disarming Voice (1), Pound (1), Echoed Voice (8), Take Down (24), Double Edge (40), Last Resort (48) |
| Charizard | Fire/Flying | Air Slash (1), Heat Wave (1), Dragon Claw (1), Dragon Breath (12), Fire Fang (19), Slash (24), Flamethrower (30), Flare Blitz (62) |
| Charmander | Fire | Scratch (1), Dragon Breath (12), Fire Fang (17), Slash (20), Flamethrower (24), Inferno (36), Flare Blitz (40) |
| Charmeleon | Fire | Scratch (1), Dragon Breath (12), Fire Fang (19), Slash (24), Flamethrower (30), Inferno (48), Flare Blitz (54) |
| Chikorita | Grass | Tackle (1), Razor Leaf (6), Magical Leaf (20), Body Slam (34), Giga Drain (42), Solar Beam (45) |
| Chinchou | Water/Electric | Water Gun (1), Bubble Beam (12), Spark (20), Discharge (28), Take Down (40), Hydro Pump (44) |
| Claydol | Ground/Psychic | Hyper Beam (1), Rock Tomb (9), Psybeam (15), Ancient Power (18), Extrasensory (27), Earth Power (30), Self Destruct (33), Explosion (48) |
| Clefable | Fairy | Moonblast (1), Meteor Mash (1) |
| Clefairy | Fairy | Disarming Voice (1), Pound (1), Stored Power (4), Meteor Mash (32), Moonblast (44) |
| Cloyster | Water/Ice | Ice Beam (1), Icicle Crash (1), Aurora Beam (1), Ice Shard (1), Tackle (1), Water Gun (1), Razor Shell (5) |
| Combusken | Fire/Fighting | Quick Attack (1), Flame Charge (9), Aerial Ace (20), Slash (25), Bounce (30), Flare Blitz (55) |
| Cradily | Rock/Grass | Acid (1), Astonish (1), Wrap (1), Ancient Power (16), Mega Drain (20), Brine (24), Giga Drain (36), Energy Ball (48) |
| Croagunk | Poison/Fighting | Mud Slap (1), Poison Sting (1), Astonish (4), Venoshock (20), Sucker Punch (24), Poison Jab (32), Sludge Bomb (44), Belch (48) |
| Crobat | Poison/Flying | Cross Poison (1), Astonish (1), Poison Fang (15), Air Cutter (27), Bite (34), Venoshock (48), Air Slash (62), Leech Life (69) |
| Cubone | Ground | False Swipe (8), Headbutt (12), Retaliate (16), Stomping Tantrum (24), Bone Rush (29), Bonemerang (40), Thrash (44), Double Edge (48) |
| Cyndaquil | Fire | Flame Wheel (19), Flame Charge (28), Swift (31), Lava Plume (37), Flamethrower (40), Double Edge (55), Overheat (58), Eruption (64) |
| Darkrai | Dark | Quick Attack (11), Dream Eater (84), Dark Pulse (93) |
| Darmanitan | Fire | Hammer Arm (1), Fire Fang (20), Headbutt (24), Fire Punch (28), Uproar (32), Flare Blitz (44), Thrash (50), Superpower (56) |
| Darumaka | Fire | Bite (8), Fire Fang (20), Headbutt (24), Fire Punch (28), Uproar (32), Flare Blitz (40), Thrash (44), Superpower (48) |
| Deino | Dark/Dragon | Dragon Breath (4), Headbutt (20), Crunch (32), Dragon Pulse (40), Body Slam (44), Hyper Voice (48), Dragon Rush (52), Outrage (60) |
| Deoxys | Psychic | Wrap (1), Knock Off (19), Psyshock (25), Zen Headbutt (49), Psycho Boost (67), Hyper Beam (73) |
| Dewgong | Water/Ice | Headbutt (1), Icy Wind (1), Aurora Beam (27), Brine (33), Take Down (39), Dive (45), Aqua Tail (49), Ice Beam (55) |
| Dialga | Time | Slash (24), Flash Cannon (32), Dragon Claw (40), Aura Sphere (48), Power Gem (56), Earth Power (72), Iron Tail (80), Roar Of Time (88) |
| Diglett | Ground | Scratch (1), Astonish (8), Bulldoze (16), Sucker Punch (20), Slash (24), Dig (32), Earth Power (36), Earthquake (40) |
| Doublade | Steel/Ghost | Shadow Sneak (1), Tackle (1), Aerial Ace (12), Slash (20), Night Slash (24), Retaliate (28), Iron Head (38), Sacred Sword (56) |
| Dragonair | Dragon | Twister (1), Wrap (1), Dragon Tail (15), Slam (25), Aqua Tail (33), Dragon Rush (39), Outrage (67), Hyper Beam (74) |
| Dragonite | Dragon/Flying | Hurricane (1), Extreme Speed (1), Fire Punch (1), Thunder Punch (1), Aqua Tail (33), Dragon Rush (39), Outrage (41), Hyper Beam (80) |
| Dratini | Dragon | Wrap (1), Twister (5), Dragon Tail (15), Slam (25), Aqua Tail (31), Dragon Rush (35), Outrage (55), Hyper Beam (60) |
| Drowzee | Psychic | Pound (1), Confusion (9), Headbutt (13), Psybeam (21), Zen Headbutt (29), Psychic (37), Psyshock (45), Future Sight (49) |
| Dugtrio | Ground | Tri Attack (1), Night Slash (1), Bulldoze (16), Sucker Punch (20), Slash (24), Dig (36), Earth Power (42), Earthquake (48) |
| Dusclops | Ghost | Shadow Punch (1), Fire Punch (1), Ice Punch (1), Thunder Punch (1), Payback (20), Hex (32), Shadow Ball (42), Future Sight (48) |
| Dusknoir | Ghost | Fire Punch (1), Ice Punch (1), Thunder Punch (1), Shadow Punch (1), Payback (20), Hex (32), Shadow Ball (42), Future Sight (48) |
| Duskull | Ghost | Astonish (1), Shadow Sneak (8), Payback (20), Hex (32), Shadow Ball (40), Future Sight (44) |
| Eevee | Normal | Covet (1), Quick Attack (10), Swift (20), Bite (25), Take Down (40), Double Edge (50), Last Resort (55) |
| Ekans | Poison | Wrap (1), Poison Sting (4), Bite (9), Acid (20), Acid Spray (28), Sludge Bomb (33), Belch (38), Gunk Shot (49) |
| Electabuzz | Electric | Quick Attack (1), Swift (12), Shock Wave (16), Thunder Punch (28), Discharge (34), Thunderbolt (46), Thunder (58), Giga Impact (64) |
| Electivire | Electric | Quick Attack (1), Swift (12), Shock Wave (16), Thunder Punch (28), Discharge (34), Thunderbolt (46), Thunder (58), Giga Impact (64) |
| Electrike | Electric | Tackle (1), Quick Attack (12), Shock Wave (16), Bite (20), Thunder Fang (24), Discharge (32), Wild Charge (40), Thunder (44) |
| Electrode | Electric | Tackle (1), Charge Beam (16), Swift (20), Self Destruct (26), Discharge (41), Explosion (47) |
| Elekid | Electric | Quick Attack (1), Thunder Shock (4), Swift (12), Shock Wave (16), Thunder Punch (28), Discharge (32), Thunderbolt (40), Thunder (48) |
| Entei | Fire | Stomp (1), Flame Wheel (6), Fire Fang (30), Crunch (42), Extrasensory (48), Lava Plume (54), Fire Blast (72), Eruption (78) |
| Espeon | Psychic | Double Edge (1), Take Down (1), Bite (1), Covet (1), Psybeam (25), Last Resort (55) |
| Exeggcute | Grass/Psychic | Absorb (1), Mega Drain (15), Confusion (20), Giga Drain (35), Extrasensory (40), Uproar (45), Solar Beam (55) |
| Exeggutor | Grass/Psychic | Solar Beam (1), Wood Hammer (1), Uproar (1), Extrasensory (1), Psyshock (1), Seed Bomb (1), Giga Drain (1) |
| Farfetch'd | Normal/Flying | Cut (15), Aerial Ace (20), Air Cutter (25), Knock Off (30), Slash (40), Air Slash (50), Leaf Blade (55), Brave Bird (65) |
| Feebas | Water | Tackle (15) |
| Flaaffy | Electric | Tackle (1), Thunder Shock (6), Take Down (20), Power Gem (34), Discharge (38), Dazzling Gleam (47), Thunder (56) |
| Flareon | Fire | Double Edge (1), Take Down (1), Covet (1), Swift (1), Fire Fang (30), Lava Plume (40), Flare Blitz (50), Last Resort (55) |
| Flygon | Ground/Dragon | Dragon Claw (1), Bulldoze (1), Bug Buzz (28), Earth Power (38), Earthquake (44), Uproar (52), Dragon Rush (60), Boomburst (68) |
| Gabite | Dragon/Ground | Dragon Breath (1), Bulldoze (18), Bite (27), Slash (34), Dragon Claw (42), Dig (50), Take Down (66), Dragon Rush (74) |
| Gallade | Psychic/Fighting | Slash (1), Future Sight (1), Dream Eater (1), Leaf Blade (1), Psychic (1), Sacred Sword (1), Aqua Cutter (1) |
| Galvantula | Bug/Electric | Bug Bite (1), Electroweb (1), Fury Cutter (1), Absorb (1), Sucker Punch (28), Slash (32), Discharge (39), Bug Buzz (56) |
| Garchomp | Dragon/Ground | Crunch (1), Dragon Breath (1), Bulldoze (18), Slash (34), Dragon Claw (42), Dig (52), Take Down (72), Dragon Rush (82) |
| Gardevoir | Psychic/Fairy | Dazzling Gleam (1), Mystical Fire (1), Psybeam (18), Dream Eater (56) |
| Gastly | Ghost/Poison | Payback (12), Hex (24), Sucker Punch (32), Dark Pulse (36), Dream Eater (48) |
| Gengar | Ghost/Poison | Shadow Punch (1), Payback (12), Hex (24), Sucker Punch (36), Dark Pulse (42), Dream Eater (60) |
| Geodude | Rock/Ground | Bulldoze (12), Rock Throw (16), Smack Down (18), Self Destruct (24), Explosion (36), Double Edge (40) |
| Gible | Dragon/Ground | Dragon Breath (12), Bulldoze (18), Bite (25), Slash (30), Dragon Claw (36), Dig (42), Take Down (54), Dragon Rush (60) |
| Giratina | Ghost/Dragon | Dragon Breath (7), Hex (21), Slash (28), Shadow Claw (42), Aura Sphere (56), Dragon Claw (63), Earth Power (70) |
| Glaceon | Ice | Double Edge (1), Take Down (1), Covet (1), Swift (1), Ice Fang (30), Freeze Dry (40), Last Resort (55) |
| Gloom | Grass/Poison | Acid (1), Absorb (1), Mega Drain (12), Giga Drain (20), Moonblast (32), Petal Dance (50) |
| Golbat | Poison/Flying | Astonish (1), Absorb (1), Poison Fang (15), Air Cutter (27), Bite (34), Venoshock (48), Air Slash (62), Leech Life (69) |
| Golduck | Water | Confusion (1), Aqua Jet (1), Scratch (1), Water Gun (1), Water Pulse (12), Zen Headbutt (18), Aqua Tail (24), Hydro Pump (40) |
| Golem | Rock/Ground | Rock Throw (16), Smack Down (18), Bulldoze (22), Self Destruct (24), Explosion (44), Double Edge (50) |
| Granbull | Fairy | Outrage (1), Fire Fang (1), Ice Fang (1), Thunder Fang (1), Headbutt (19), Last Resort (35), Play Rough (43), Crunch (59) |
| Graveler | Rock/Ground | Bulldoze (12), Rock Throw (16), Smack Down (18), Self Destruct (24), Explosion (44), Double Edge (50) |
| Groudon | Ground | Precipice Blades (1), Lava Plume (1), Earth Power (9), Earthquake (27), Hammer Arm (36), Fire Blast (72), Solar Beam (81), Eruption (90) |
| Grovyle | Grass | Leafage (1), Pound (1), Quick Attack (1), Assurance (20), Giga Drain (25), Slam (30) |
| Growlithe | Fire | Bite (8), Fire Fang (24), Retaliate (28), Crunch (32), Take Down (36), Flamethrower (40), Play Rough (48), Flare Blitz (56) |
| Gyarados | Water/Flying | Brine (12), Waterfall (21), Crunch (24), Hurricane (44), Thrash (48), Hyper Beam (52) |
| Haunter | Ghost/Poison | Shadow Punch (1), Payback (12), Hex (24), Sucker Punch (36), Dark Pulse (42), Dream Eater (60) |
| Heracross | Bug/Fighting | Tackle (1), Aerial Ace (15), Horn Attack (20), Brick Break (30), Throat Chop (40), Thrash (45), Megahorn (55), Close Combat (60) |
| Hitmonchan | Fighting | Drain Punch (1), Fake Out (1), Fire Punch (24), Ice Punch (24), Thunder Punch (24), Mega Punch (32), Focus Punch (44) |
| Hitmonlee | Fighting | Low Sweep (1), Sucker Punch (16), Blaze Kick (24), Mega Kick (32), High Jump Kick (44), Axe Kick (50) |
| Hitmontop | Fighting | Fake Out (1), Tackle (1), Feint (1), Quick Attack (4), Rapid Spin (16), Sucker Punch (24), Dig (32) |
| Ho-Oh | Fire/Flying | Ancient Power (1), Weather Ball (1), Extrasensory (36), Sacred Fire (54), Fire Blast (72), Future Sight (81), Sky Attack (90), Overheat (99) |
| Honedge | Steel/Ghost | Tackle (1), Shadow Sneak (4), Aerial Ace (12), Slash (20), Night Slash (24), Retaliate (28), Iron Head (36), Sacred Sword (48) |
| Hoothoot | Normal/Flying | Tackle (3), Confusion (9), Air Slash (18), Extrasensory (21), Take Down (24), Uproar (27), Moonblast (33), Dream Eater (39) |
| Horsea | Water | Water Gun (1), Twister (10), Dragon Breath (20), Bubble Beam (25), Water Pulse (35), Dragon Pulse (40), Hydro Pump (45) |
| Houndoom | Dark/Fire | Thunder Fang (1), Bite (16), Incinerate (20), Fire Fang (30), Foul Play (45), Flamethrower (50), Crunch (56), Inferno (62) |
| Houndour | Dark/Fire | Ember (1), Bite (16), Incinerate (20), Fire Fang (28), Foul Play (40), Flamethrower (44), Crunch (49), Inferno (56) |
| Hydreigon | Dark/Dragon | Tri Attack (1), Crunch (32), Dragon Pulse (40), Body Slam (44), Hyper Voice (48), Dragon Rush (54), Outrage (68), Hyper Beam (76) |
| Hypno | Psychic | Confusion (1), Pound (1), Headbutt (13), Psybeam (21), Zen Headbutt (32), Psychic (42), Psyshock (51), Future Sight (56) |
| Ivysaur | Grass/Poison | Vine Whip (1), Tackle (1), Razor Leaf (12), Seed Bomb (20), Take Down (25), Power Whip (45), Solar Beam (50) |
| Jigglypuff | Normal/Fairy | Disarming Voice (1), Pound (1), Echoed Voice (4), Covet (8), Round (16), Body Slam (24), Hyper Voice (36), Double Edge (44) |
| Jirachi | Steel/Psychic | Swift (7), Zen Headbutt (28), Psychic (42), Meteor Mash (49), Future Sight (70), Double Edge (77), Last Resort (91), Doom Desire (98) |
| Jolteon | Electric | Double Edge (1), Take Down (1), Bite (1), Covet (1), Thunder Fang (30), Discharge (40), Last Resort (55) |
| Joltik | Bug/Electric | Fury Cutter (1), Absorb (1), Electroweb (4), Bug Bite (8), Sucker Punch (28), Slash (32), Discharge (37), Bug Buzz (48) |
| Jynx | Ice/Psychic | Pound (1), Powder Snow (1), Lick (1), Confusion (12), Covet (16), Ice Punch (28), Psychic (34), Blizzard (58) |
| Kabuto | Rock/Water | Scratch (5), Aqua Jet (15), Mud Shot (25), Ancient Power (30), Brine (35), Leech Life (45), Liquidation (50) |
| Kabutops | Rock/Water | Slash (1), Night Slash (1), Mud Shot (25), Ancient Power (30), Brine (35), Leech Life (49), Liquidation (56) |
| Kadabra | Psychic | Psybeam (5), Psycho Cut (20), Psyshock (30) |
| Kangaskhan | Normal | Pound (1), Bite (12), Stomp (16), Headbutt (24), Sucker Punch (28), Crunch (36), Outrage (48), Last Resort (52) |
| Kingambit | Dark/Steel | Kowtow Cleave (1), Metal Claw (1), Scratch (1), Assurance (25), Slash (35), Night Slash (40), Retaliate (50), Iron Head (57) |
| Kingdra | Water/Dragon | Twister (1), Water Gun (1), Dragon Breath (20), Bubble Beam (25), Water Pulse (37), Dragon Pulse (44), Hydro Pump (51), Wave Crash (72) |
| Kingler | Water | Hammer Arm (1), Metal Claw (1), Mud Shot (12), Bubble Beam (20), Stomp (24), Razor Shell (36), Slam (42), Crabhammer (54) |
| Kirlia | Psychic/Fairy | Disarming Voice (1), Draining Kiss (12), Psybeam (18), Dream Eater (48) |
| Koffing | Poison | Tackle (1), Clear Smog (12), Assurance (16), Self Destruct (28), Belch (40), Explosion (44) |
| Krabby | Water | Water Gun (1), Metal Claw (8), Mud Shot (12), Bubble Beam (20), Stomp (24), Razor Shell (32), Slam (36), Crabhammer (44) |
| Kyogre | Water | Origin Pulse (1), Body Slam (1), Aqua Tail (9), Muddy Water (27), Ice Beam (36), Hydro Pump (72), Double Edge (81), Water Spout (90) |
| Lampent | Ghost/Fire | Ember (1), Astonish (1), Smog (1), Hex (16), Fire Spin (24), Shadow Ball (36), Inferno (40), Overheat (58) |
| Lanturn | Water/Electric | Water Gun (1), Bubble Beam (12), Spark (20), Discharge (30), Take Down (48), Hydro Pump (54) |
| Lapras | Water/Ice | Water Gun (1), Ice Shard (20), Water Pulse (30), Brine (35), Body Slam (40), Ice Beam (45), Hydro Pump (55) |
| Larvitar | Rock/Dark | Bite (9), Stomping Tantrum (18), Thrash (36), Hyper Beam (42) |
| Latias & Latios | Dragon/Psychic | Dragon Breath (1), Confusion (1), Psybeam (20), Dragon Pulse (35), Zen Headbutt (40), Psychic (45), Dragon Claw (50), Draco Meteor (70) |
| Leafeon | Grass | Double Edge (1), Take Down (1), Bite (1), Covet (1), Swift (1), Giga Drain (40), Leaf Blade (50), Last Resort (55) |
| Leafleon | Grass | Double Edge (1), Take Down (1), Bite (1), Covet (1), Swift (1), Giga Drain (40), Last Resort (55) |
| Lileep | Rock/Grass | Astonish (1), Wrap (1), Acid (4), Ancient Power (16), Mega Drain (20), Brine (24), Giga Drain (36), Energy Ball (44) |
| Litwick | Ghost/Fire | Astonish (1), Smog (1), Ember (4), Hex (16), Fire Spin (24), Shadow Ball (36), Inferno (40), Overheat (52) |
| Lombre | Water/Grass | Knock Off (1), Fake Out (1), Water Gun (1), Bubble Beam (24), Giga Drain (36), Zen Headbutt (50), Energy Ball (57), Hydro Pump (64) |
| Lotad | Water/Grass | Astonish (1), Absorb (3), Water Gun (6), Mega Drain (12), Bubble Beam (20), Giga Drain (28), Zen Headbutt (38), Energy Ball (43) |
| Lucario | Fighting/Steel | Metal Claw (1), Quick Attack (1), Meteor Mash (48), Dragon Pulse (52), Close Combat (60) |
| Ludicolo | Water/Grass | Bubble Beam (1), Fake Out (1) |
| Lugia | Psychic/Water | Ancient Power (1), Weather Ball (1), Gust (1), Extrasensory (36), Aeroblast (54), Hydro Pump (72), Sky Attack (90) |
| Machamp | Fighting | Revenge (1), Low Sweep (12), Knock Off (16), Vital Throw (24), Strength (31), Dynamic Punch (54), Cross Chop (60), Double Edge (66) |
| Machoke | Fighting | Revenge (1), Low Sweep (12), Knock Off (16), Vital Throw (24), Strength (31), Dynamic Punch (54), Cross Chop (60), Double Edge (66) |
| Machop | Fighting | Revenge (8), Low Sweep (12), Knock Off (16), Vital Throw (24), Strength (29), Dynamic Punch (44), Cross Chop (48), Double Edge (52) |
| Magby | Fire | Smog (1), Ember (4), Clear Smog (12), Flame Wheel (16), Fire Punch (28), Lava Plume (32), Flamethrower (40), Fire Blast (48) |
| Magcargo | Fire/Rock | Earth Power (1), Clear Smog (20), Ancient Power (22), Incinerate (27), Rock Slide (29), Lava Plume (34), Body Slam (43), Flamethrower (54) |
| Magikarp | Water | Tackle (15) |
| Magmar | Fire | Ember (1), Clear Smog (12), Flame Wheel (16), Fire Punch (28), Lava Plume (34), Flamethrower (46), Fire Blast (58), Hyper Beam (64) |
| Magmortar | Fire | Ember (1), Clear Smog (12), Flame Wheel (16), Fire Punch (28), Lava Plume (34), Flamethrower (46), Fire Blast (58), Hyper Beam (64) |
| Magnemite | Electric/Steel | Tackle (1), Flash Cannon (32), Discharge (36), Zap Cannon (52) |
| Magneton | Electric/Steel | Tri Attack (1), Tackle (1), Flash Cannon (34), Discharge (40), Zap Cannon (64) |
| Magnezone | Electric/Steel | Tri Attack (1), Tackle (1), Thunder Shock (1), Spark (20), Flash Cannon (34), Discharge (40), Zap Cannon (64) |
| Mamoswine | Ice/Ground | Ice Fang (1), Ancient Power (1), Powder Snow (1), Icy Wind (30), Take Down (44), Earthquake (51), Blizzard (58), Thrash (65) |
| Manectric | Electric | Fire Fang (1), Tackle (1), Shock Wave (16), Bite (20), Thunder Fang (24), Discharge (36), Wild Charge (48), Thunder (54) |
| Mankey | Fighting | Covet (1), Scratch (1), Cross Chop (22), Assurance (26), Thrash (29), Stomping Tantrum (40), Outrage (44) |
| Mareep | Electric | Tackle (1), Thunder Shock (8), Take Down (18), Power Gem (29), Discharge (32), Dazzling Gleam (39), Thunder (46) |
| Marowak | Ground | False Swipe (1), Headbutt (12), Retaliate (16), Stomping Tantrum (24), Bone Rush (31), Bonemerang (48), Thrash (54), Double Edge (60) |
| Meganium | Grass | Razor Leaf (1), Tackle (1), Magical Leaf (22), Body Slam (40), Giga Drain (50), Solar Beam (54), Petal Blizzard (32), Petal Dance (60) |
| Meowth | Normal | Fake Out (1), Feint (4), Scratch (8), Pay Day (12), Bite (16), Assurance (24), Slash (36), Play Rough (44) |
| Metagross | Steel/Psychic | Hammer Arm (1), Confusion (1), Flash Cannon (16), Take Down (26), Psychic (34), Hyper Beam (82) |
| Metang | Steel/Psychic | Confusion (1), Metal Claw (1), Flash Cannon (18), Take Down (26), Psychic (34), Hyper Beam (74) |
| Mew | Psychic | Pound (1), Ancient Power (30), Aura Sphere (90) |
| Mewtwo | Psychic | Swift (1), Ancient Power (8), Psycho Cut (16), Aura Sphere (40), Psystrike (72) |
| Milotic | Water | Water Pulse (1), Tackle (1), Water Gun (1), Disarming Voice (4), Dragon Tail (24), Aqua Tail (32), Surf (40), Hydro Pump (52) |
| Misdreavus | Ghost | Confusion (1), Astonish (10), Hex (23), Psybeam (28), Payback (37), Shadow Ball (41), Power Gem (50) |
| Mismagius | Ghost | Phantom Force (1), Power Gem (1), Mystical Fire (1), Magical Leaf (1), Astonish (1) |
| Moltres | Fire/Flying | Wing Attack (15), Ancient Power (25), Incinerate (30), Air Slash (35), Heat Wave (45), Hurricane (55), Overheat (65), Sky Attack (70) |
| Mr. Mime | Psychic/Fairy | Pound (1), Confusion (12), Psybeam (28), Sucker Punch (40), Dazzling Gleam (44), Psychic (48) |
| Mr.mime | Psychic | Pound (1), Psybeam (28), Sucker Punch (40), Dazzling Gleam (44) |
| Nidoking | Ground/Poison | Megahorn (1), Earth Power (1), Poison Jab (1), Horn Attack (1), Peck (1), Double Kick (1), Fury Attack (1) |
| Nidoran | Poison | Peck (5), Fury Attack (15), Double Kick (25), Horn Attack (30), Poison Jab (50), Earth Power (55) |
| Nidorino | Poison | Peck (1), Fury Attack (15), Double Kick (29), Horn Attack (36), Poison Jab (64), Earth Power (71) |
| Nincada | Bug/Ground | Scratch (1), False Swipe (10), Mud Slap (15), Absorb (21), Metal Claw (25), Fury Swipes (30), Dig (40) |
| Ninetales | Fire | Flamethrower (1), Quick Attack (1) |
| Ninjask | Bug/Flying | Dig (1), Aerial Ace (1), Metal Claw (1), False Swipe (1), Scratch (1), Bug Bite (29), Slash (50), X Scissor (64) |
| Noctowl | Normal/Flying | Sky Attack (1), Confusion (9), Air Slash (18), Extrasensory (23), Take Down (28), Uproar (33), Moonblast (43), Dream Eater (53) |
| Oddish | Grass/Poison | Absorb (1), Acid (4), Mega Drain (12), Giga Drain (20), Moonblast (28), Petal Dance (40) |
| Omanyte | Rock/Water | Rollout (5), Water Gun (15), Mud Shot (25), Ancient Power (30), Brine (35), Rock Blast (45), Surf (50), Hydro Pump (60) |
| Omastar | Rock/Water | Rollout (1), Water Gun (15), Mud Shot (25), Ancient Power (30), Brine (35), Surf (56), Hydro Pump (70) |
| Onix | Rock/Ground | Smack Down (4), Dragon Breath (12), Slam (36), Dig (44), Iron Tail (48), Double Edge (56) |
| Palkia | Space | Slash (24), Aura Sphere (48), Power Gem (56), Earth Power (72), Spacial Rend (80) |
| Pawniard | Dark/Steel | Scratch (1), Fury Cutter (5), Metal Claw (10), Assurance (25), Slash (35), Night Slash (40), Retaliate (50), Iron Head (55) |
| Persian | Normal | Power Gem (1), Fake Out (1), Scratch (1), Pay Day (12), Bite (16), Assurance (24), Slash (42), Play Rough (54) |
| Pidgeot | Flying | Gust (1), Quick Attack (1), Tackle (1), Twister (22) |
| Pidgeotto | Flying | Gust (1), Tackle (1), Quick Attack (13), Twister (22) |
| Pidgey | Flying | Tackle (1), Gust (9), Quick Attack (13), Twister (21) |
| Pikachu | Electric | Quick Attack (1), Feint (16), Iron Tail (28), Discharge (32) |
| Piloswine | Ice/Ground | Ice Fang (1), Ancient Power (1), Powder Snow (1), Icy Wind (30), Take Down (44), Earthquake (51), Blizzard (58), Thrash (65) |
| Pinsir | Bug | Vice Grip (1), Storm Throw (20), Vital Throw (28), X Scissor (32), Strength (36), Submission (44), Superpower (52) |
| Politoed | Water | Bounce (1), Hydro Pump (1), Pound (1) |
| Poliwag | Water | Water Gun (1), Pound (6), Mud Shot (12), Bubble Beam (18), Body Slam (30), Earth Power (36), Double Edge (54) |
| Poliwhirl | Water | Mud Shot (1), Pound (1), Water Gun (1), Bubble Beam (18), Body Slam (32), Earth Power (40), Double Edge (66) |
| Poliwrath | Water/Fighting | Dynamic Punch (1), Body Slam (1), Bubble Beam (1) |
| Ponyta | Fire | Tackle (1), Flame Charge (15), Flame Wheel (25), Stomp (30), Take Down (41), Inferno (45), Fire Blast (50), Flare Blitz (55) |
| Porygon | Normal | Tackle (1), Thunder Shock (15), Psybeam (20), Discharge (40), Tri Attack (45), Double Edge (50), Zap Cannon (60) |
| Porygon2 | Normal | Tackle (1), Thunder Shock (15), Psybeam (20), Discharge (40), Tri Attack (45), Double Edge (50), Zap Cannon (60) |
| Primeape | Fighting | Scratch (1), Cross Chop (22), Assurance (26), Thrash (30), Rage Fist (35), Stomping Tantrum (48), Outrage (53) |
| Psyduck | Water | Scratch (1), Water Gun (3), Confusion (6), Fury Swipes (9), Water Pulse (12), Zen Headbutt (18), Aqua Tail (24) |
| Pupitar | Rock/Dark | Bite (9), Stomping Tantrum (18), Thrash (42), Hyper Beam (52) |
| Quilava | Fire | Flame Wheel (20), Swift (31), Flame Charge (35), Lava Plume (42), Flamethrower (46), Double Edge (64), Overheat (68), Eruption (75) |
| Raichu | Electric | Thunder Punch (1), Discharge (1), Iron Tail (1), Quick Attack (1) |
| Raikou | Electric | Extreme Speed (1), Spark (6), Bite (12), Thunder Fang (30), Crunch (42), Extrasensory (48), Discharge (54), Thunder (72) |
| Ralts | Psychic/Fairy | Disarming Voice (1), Draining Kiss (12), Psybeam (18), Dream Eater (36) |
| Rapidash | Fire | Smart Strike (1), Megahorn (1), Poison Jab (1), Flame Wheel (25), Stomp (30), Take Down (43), Fire Blast (56), Flare Blitz (63) |
| Raticate | Normal | Quick Attack (1), Bite (10), Hyper Fang (16), Assurance (19), Crunch (24), Sucker Punch (29), Double Edge (39) |
| Rattata | Normal | Quick Attack (4), Bite (10), Hyper Fang (16), Assurance (19), Crunch (22), Sucker Punch (25), Double Edge (31) |
| Rayquaza | Dragon/Flying | Dragon Ascent (1), Crunch (9), Extreme Speed (27), Dragon Pulse (36), Hyper Voice (45), Fly (63), Outrage (81), Hyper Beam (90) |
| Regigigas | Normal | Facade (12), Stomp (18), Knock Off (30), Mega Punch (36), Body Press (42), Zen Headbutt (54), Hammer Arm (66), Giga Impact (72) |
| Regirock | Rock | Bulldoze (6), Stomp (18), Rock Slide (24), Hammer Arm (42), Stone Edge (48), Superpower (54), Hyper Beam (72), Explosion (78) |
| Rhydon | Rock/Ground | Hammer Arm (1), Horn Attack (15), Stomp (25), Drill Run (35), Take Down (40), Earthquake (47), Stone Edge (54), Megahorn (61) |
| Rhyhorn | Rock/Ground | Horn Attack (15), Stomp (25), Drill Run (35), Take Down (40), Earthquake (45), Stone Edge (50), Megahorn (55) |
| Rhyperior | Ground/Rock | Hammer Arm (1), Horn Attack (15), Drill Run (35), Take Down (40), Earthquake (47), Stone Edge (54), Megahorn (61), Rock Wrecker (75) |
| Sableye | Dark/Ghost | Scratch (1), Shadow Sneak (9), Knock Off (27), Shadow Claw (33), Power Gem (39), Zen Headbutt (42), Shadow Ball (45), Foul Play (48) |
| Salamence | Dragon/Flying | Fly (1), Bite (1), Headbutt (15), Crunch (25), Zen Headbutt (39), Flamethrower (55), Double Edge (73) |
| Sandshrew | Ground | Scratch (1), Fury Cutter (12), Rapid Spin (15), Swift (21), Slash (30), Earthquake (45) |
| Sandslash | Ground | Crush Claw (1), Scratch (1), Rapid Spin (15), Swift (21), Slash (36), Earthquake (61) |
| Sceptile | Grass | Leafage (1), Pound (1), Quick Attack (1), Assurance (20), Giga Drain (25), Slam (30) |
| Scizor | Bug/Steel | Bullet Punch (1), Air Slash (1), Wing Attack (1), False Swipe (1), Metal Claw (12), Slash (24), Iron Head (36), X Scissor (40) |
| Scyther | Bug/Flying | Quick Attack (1), Fury Cutter (4), False Swipe (8), Wing Attack (12), Double Hit (20), Slash (24), Air Slash (36), X Scissor (40) |
| Seadra | Water | Twister (1), Water Gun (1), Dragon Breath (20), Bubble Beam (25), Water Pulse (37), Dragon Pulse (44), Hydro Pump (51) |
| Seel | Water | Headbutt (1), Icy Wind (11), Aurora Beam (27), Brine (33), Take Down (37), Dive (41), Aqua Tail (43), Ice Beam (47) |
| Sharpedo | Water/Dark | Slash (1), Night Slash (1), Poison Fang (1), Bite (16), Ice Fang (20), Crunch (34), Liquidation (46), Take Down (52) |
| Shedinja | Bug/Ghost | Dig (1), Shadow Claw (1), Metal Claw (1), False Swipe (1), Scratch (1), Shadow Sneak (29), Shadow Ball (50), Phantom Force (64) |
| Shelgon | Dragon/Flying | Bite (1), Headbutt (15), Crunch (25), Zen Headbutt (39), Flamethrower (53), Outrage (60), Double Edge (67) |
| Shellder | Water/Ice | Tackle (1), Water Gun (1), Ice Shard (8), Whirlpool (16), Aurora Beam (24), Razor Shell (32), Ice Beam (40) |
| Shroomish | Grass | Tackle (1), Absorb (1), Mega Drain (12), Headbutt (15), Giga Drain (26), Seed Bomb (36) |
| Sirfetch'd | Fighting | First Impression (1), Brutal Swing (20), Knock Off (30), Brick Break (40), Slam (50), Leaf Blade (55), Brave Bird (65), Meteor Assault (70) |
| Slowbro | Water/Psychic | Tackle (1), Water Gun (1), Confusion (12), Water Pulse (18), Headbutt (21), Zen Headbutt (24), Surf (30), Psychic (36) |
| Slowking | Water/Psychic | Power Gem (1), Tackle (1), Water Gun (1), Confusion (12), Water Pulse (18), Headbutt (21), Surf (30), Psychic (36) |
| Slowpoke | Water/Psychic | Tackle (1), Water Gun (6), Confusion (12), Water Pulse (18), Headbutt (21), Zen Headbutt (24), Surf (30), Psychic (36) |
| Slugma | Fire | Clear Smog (20), Ancient Power (22), Incinerate (27), Rock Slide (29), Lava Plume (34), Body Slam (41), Flamethrower (48), Earth Power (50) |
| Smoochum | Ice/Psychic | Pound (1), Lick (1), Powder Snow (4), Confusion (12), Covet (16), Ice Punch (28), Psychic (32), Blizzard (48) |
| Sneasel | Dark/Ice | Scratch (1), Quick Attack (12), Metal Claw (18), Icy Wind (24), Fury Swipes (30), Slash (60) |
| Snorlax | Normal | Last Resort (1), Covet (1), Crunch (24), Body Slam (28), High Horsepower (40), Hammer Arm (44), Belch (52), Giga Impact (56) |
| Snover | Grass/Ice | Powder Snow (1), Leafage (5), Ice Shard (15), Razor Leaf (20), Icy Wind (25), Wood Hammer (41), Blizzard (45) |
| Snubbull | Fairy | Fire Fang (1), Ice Fang (1), Thunder Fang (1), Bite (7), Headbutt (19), Last Resort (31), Play Rough (37), Crunch (49) |
| Squirtle | Water | Tackle (1), Water Gun (3), Rapid Spin (9), Bite (12), Wave Crash (36) |
| Starmie | Water/Psychic | Psychic (1), Surf (1), Power Gem (1), Brine (1), Psybeam (1), Swift (1), Rapid Spin (1) |
| Staryu | Water | Rapid Spin (12), Swift (20), Psybeam (24), Brine (28), Power Gem (36), Psychic (40), Surf (44) |
| Steelix | Steel/Ground | Crunch (1), Fire Fang (1), Ice Fang (1), Rock Slide (20), Dig (44), Iron Tail (48), Stone Edge (52), Double Edge (56) |
| Sudowoodo | Rock | Slam (1), Wood Hammer (1), Hammer Arm (1), Stone Edge (1), Sucker Punch (28), Rock Slide (32), Double Edge (44), Head Smash (48) |
| Suicune | Water | Water Pulse (6), Bite (12), Ice Fang (30), Crunch (42), Extrasensory (48), Surf (54), Hydro Pump (72), Blizzard (78) |
| Swablu | Normal/Flying | Peck (1), Disarming Voice (4), Fury Attack (12), Round (16), Dragon Breath (20), Take Down (36), Moonblast (40) |
| Swinub | Ice/Ground | Tackle (1), Mud Slap (1), Powder Snow (5), Ice Shard (15), Icy Wind (30), Take Down (40), Earthquake (45), Blizzard (50) |
| Sylveon | Fairy | Double Edge (1), Take Down (1), Bite (1), Covet (1), Swift (20), Draining Kiss (30), Moonblast (50), Last Resort (55) |
| Tangela | Grass | Absorb (1), Mega Drain (12), Vine Whip (16), Ancient Power (24), Knock Off (28), Giga Drain (32), Slam (40), Power Whip (48) |
| Tangrowth | Grass | Absorb (1), Mega Drain (12), Vine Whip (16), Ancient Power (24), Knock Off (28), Giga Drain (32), Slam (40), Power Whip (48) |
| Tauros | Normal | Payback (10), Assurance (15), Horn Attack (20), Zen Headbutt (30), Raging Bull (35), Thrash (50), Double Edge (55), Giga Impact (60) |
| Tauros Aqua | Fighting/Water | Tackle (1), Aqua Jet (15), Headbutt (20), Zen Headbutt (30), Raging Bull (35), Thrash (50), Wave Crash (55), Close Combat (60) |
| Tauros Blaze | Fighting/Fire | Tackle (1), Flame Charge (15), Headbutt (20), Zen Headbutt (30), Raging Bull (35), Thrash (50), Flare Blitz (55), Close Combat (60) |
| Tauros Combat | Fighting | Tackle (1), Assurance (15), Headbutt (20), Zen Headbutt (30), Raging Bull (35), Thrash (50), Double Edge (55), Close Combat (60) |
| Tentacool | Water/Poison | Water Gun (1), Bubble Beam (24), Hex (28), Poison Jab (36), Surf (40), Sludge Wave (44) |
| Tentacruel | Water/Poison | Acid (1), Bubble Beam (24), Hex (28), Poison Jab (40), Surf (46), Sludge Wave (52) |
| Togekiss | Fairy/Flying | Air Slash (1), Last Resort (1), Sky Attack (1), Double Edge (1), Aura Sphere (1), Extreme Speed (1), Tri Attack (1), Ancient Power (1) |
| Togepi | Fairy | Pound (1), Ancient Power (16), Double Edge (32), Last Resort (48) |
| Togetic | Fairy/Flying | Fairy Wind (1), Pound (1), Ancient Power (16), Double Edge (32), Last Resort (48) |
| Torchic | Fire/Fighting | Scratch (1), Flame Charge (9), Aerial Ace (18), Slash (21), Bounce (24), Flamethrower (30), Flare Blitz (39) |
| Torkoal | Fire | Rapid Spin (8), Clear Smog (16), Flame Wheel (20), Lava Plume (28), Body Slam (32), Flamethrower (40), Heat Wave (48), Eruption (64) |
| Toxicroak | Poison/Fighting | Astonish (1), Mud Slap (1), Poison Sting (1), Venoshock (20), Sucker Punch (24), Poison Jab (32), Sludge Bomb (48), Belch (54) |
| Trapinch | Ground | Astonish (1), Bite (8), Bulldoze (20), Dig (24), Crunch (28), Earth Power (36), Earthquake (40), Superpower (44) |
| Treecko | Grass | Pound (1), Leafage (3), Quick Attack (6), Assurance (18), Giga Drain (21), Slam (24), Energy Ball (30) |
| Typhlosion | Fire | Eruption (1), Double Edge (1), Flame Wheel (20), Swift (31), Flame Charge (35), Lava Plume (43), Flamethrower (48), Overheat (74) |
| Tyranitar | Rock/Dark | Dark Pulse (1), Stomping Tantrum (18), Thrash (42), Hyper Beam (52), Giga Impact (59) |
| Tyrogue | Fighting | Fake Out (1), Tackle (1) |
| Umbreon | Dark | Double Edge (1), Take Down (1), Bite (1), Covet (1), Swift (1), Assurance (25), Dark Pulse (40), Last Resort (55) |
| Vaporeon | Water | Double Edge (1), Take Down (1), Bite (1), Covet (1), Aurora Beam (30), Muddy Water (40), Last Resort (55) |
| Venusaur | Grass/Poison | Petal Blizzard (1), Petal Dance (1), Vine Whip (1), Razor Leaf (12), Seed Bomb (20), Take Down (25), Power Whip (51), Solar Beam (58) |
| Vibrava | Ground/Dragon | Dragon Breath (1), Dig (1), Bug Buzz (28), Earth Power (38), Earthquake (44), Uproar (50), Dragon Rush (56), Boomburst (62) |
| Victreebel | Grass/Poison | Razor Leaf (1), Vine Whip (1) |
| Vileplume | Grass/Poison | Petal Blizzard (1), Petal Dance (1), Moonblast (1), Giga Drain (1), Acid (1), Mega Drain (1), Absorb (1) |
| Voltorb | Electric | Tackle (1), Charge Beam (16), Swift (20), Self Destruct (26), Discharge (37), Explosion (41) |
| Vulpix | Fire | Quick Attack (8), Incinerate (16), Extrasensory (28), Flamethrower (32), Fire Spin (40), Inferno (48), Fire Blast (52) |
| Wartortle | Water | Tackle (1), Water Gun (1), Rapid Spin (9), Bite (12), Wave Crash (50) |
| Weavile | Dark/Ice | Slash (1), Assurance (1), Ice Shard (1), Quick Attack (1), Metal Claw (18), Icy Wind (24), Night Slash (60), Dark Pulse (66) |
| Weedle | Bug/Poison | Poison Sting (1) |
| Weepinbell | Grass/Poison | Vine Whip (1), Wrap (1), Acid (24), Knock Off (29), Razor Leaf (44), Poison Jab (47), Slam (54), Power Whip (58) |
| Weezing | Poison | Heat Wave (1), Clear Smog (12), Assurance (16), Self Destruct (28), Belch (44), Explosion (50) |
| Wigglytuff | Normal/Fairy | Double Edge (1), Hyper Voice (1), Body Slam (1), Covet (1), Round (1), Disarming Voice (1), Echoed Voice (1), Play Rough (5) |
| Zapdos | Electric/Flying | Peck (1), Pluck (15), Ancient Power (25), Drill Peck (35), Discharge (45), Zap Cannon (70) |
| Zubat | Poison/Flying | Absorb (1), Astonish (5), Poison Fang (15), Air Cutter (25), Bite (30), Venoshock (40), Air Slash (50), Leech Life (55) |
| Zweilous | Dark/Dragon | Bite (1), Headbutt (20), Crunch (32), Dragon Pulse (40), Body Slam (44), Hyper Voice (48), Dragon Rush (54), Outrage (66) |
