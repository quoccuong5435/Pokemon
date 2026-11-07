# 6. Đề xuất: hiệu ứng move mới từ PKLegends v3.2 (chờ duyệt)

Ngày 2026-11-08. Chưa sửa code phần này.

## Vì sao
- Mọi move đánh một mục tiêu hiện là **đạn bay**, kể cả chiêu cận chiến như Iron Tail, Dragon Claw, Crunch, Close Combat. Lý do: v3.1 dựng chúng từ Storm Bolt / Shadow Strike (ném) và Shockwave / Carrion Swarm (sóng).
- Hình đạn hiện chỉ đổi theo hệ, dùng model có sẵn của game.

## Nguồn hiệu ứng
- **PKLegends v3.2** (đã có trên máy, map Pokémon, file mở được): khoảng 80 model hiệu ứng riêng.
  - chém / vuốt: `slash-luc`, `purple claw`, `Zornklinge`, `Coup de Grace Purple`;
  - đánh / đấm: `AnimatedBash`, `hitvfx1`; lao tới: `Blitzangriff`; điện: `galvanattack`;
  - đạn theo hệ: `Ember`, `Firebolt`, `Water Shot`, `Icebeam`, `Psionic Shot`, `Spectral Missile`, `Voidbolt`, `FeatherMissile`, `Faerie Missile`, `Sonic Missile`, `GreenShot`, `boomerrangbone`…;
  - diện rộng: `GreenBoom`, `VioletPulse`, `SandTornado`, `Stormfall`, `Tangroots`, `SS2 Lightning`.
- **79.PokemonRPG.w3x**: map có nhắc tới 293 model nhưng file bị khóa, không lấy được.
- **Hive Workshop** (trên mạng, miễn phí): còn nhiều hiệu ứng chém / đấm / nổ đẹp hơn. Nếu muốn dùng thì mình gửi link từng file và hỏi bạn trước khi tải.

## Đề xuất
- **Cận chiến** (106 move vật lý chạm người): tầm 150 (phải đứng sát), không có đạn bay, hiệu ứng chém / đấm hiện ngay trên mục tiêu. Sát thương, hồi chiêu và hiệu ứng phụ (choáng, độc…) giữ nguyên.
- **Đạn theo hệ** (81 move): đạn bay lấy model của PKL theo hệ; với Fire và Dark, Power càng cao đạn càng to (Minor / Medium / Major).
- **Diện rộng** (66 move): hiệu ứng nổ / sóng theo hệ.
- **Hiệu ứng riêng theo tên** (10 move): Ice Beam (tia băng), Tri Attack (tia số), Hurricane / Thunder (bão), Razor Leaf, Bonemerang…
- **Giữ nguyên**: 56 move.
- Dung lượng thêm: khoảng 1,5 MB (35 model).

## Model sẽ dùng (số move dùng)

`AnimatedBash` (62), `WarStompCaster` (24), `VioletPulse` (19), `Tangroots` (16), `Water Shot` (14), `Sonic Missile` (12), `GreenShot` (10), `Coup de Grace Purple` (10), `Blitzangriff` (9), `FeatherMissile` (9), `slash-luc` (9), `SS2 Lightning` (7), `Wizardry Missile` (7), `Voidbolt Major` (6), `purple claw` (5), `Holy Missile` (4), `Zornklinge` (4), `Stormfall` (3), `Spectral Missile` (3), `Voidbolt Medium` (3), `blue energy arrow` (3), `Psionic Shot Silver` (3), `Firebolt Minor` (3), `Arcade Bolt Psyche` (3), `galvanattack` (3), `Icebeam` (2), `GreenBoom` (2), `boomerrangbone` (1), `Ember` (1), `GolemAlolanProjectile4` (1), `Powerwhip` (1), `Voidball Minor` (1), `RazorLeafSelf` (1), `Firebolt Medium` (1), `Digital Ray` (1)

## Từng move

| # | Move | Hệ | Loại | Power | Hiện tại (skill gốc, hiệu ứng, tầm) | Đề xuất |
|---|---|---|---|---|---|---|
| 0 | Absorb | Grass | Đặc biệt | 20 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 1 | Acid | Poison | Đặc biệt | 40 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Đạn hệ Poison: GreenShot |
| 2 | Acid Spray | Poison | Đặc biệt | 40 | Carrion Swarm, ChimaeraAcidMissile, tầm 700 | Đạn hệ Poison: GreenShot |
| 3 | Acrobatics | Flying | Vật lý | 55 | Carrion Swarm, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 4 | Aerial Ace | Flying | Vật lý | 60 | Carrion Swarm, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 5 | Aeroblast | Flying | Đặc biệt | 100 | Carrion Swarm, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 6 | Air Cutter | Flying | Đặc biệt | 60 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: Stormfall |
| 7 | Air Slash | Flying | Đặc biệt | 75 | Carrion Swarm, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 8 | Alluring Voice | Fairy | Đặc biệt | 80 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 9 | Ancient Power | Rock | Đặc biệt | 60 | Frost Nova, ThunderClapCaster, tầm 700 | Diện rộng: WarStompCaster |
| 10 | Aqua Cutter | Water | Vật lý | 70 | Shadow Strike, WaterElementalMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 11 | Aqua Jet | Water | Vật lý | 40 | Shockwave, WaterElementalMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 12 | Aqua Tail | Water | Vật lý | 90 | Storm Bolt, WaterElementalMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 13 | Assurance | Dark | Vật lý | 60 | Shadow Strike, AvengerMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 14 | Astonish | Ghost | Vật lý | 30 | Shadow Strike, BansheeMissile, tầm 300 | Đạn hệ Ghost: Spectral Missile |
| 15 | Aura Sphere | Fighting | Đặc biệt | 80 | Frost Nova, ThunderClapCaster, tầm 700 | Giữ nguyên |
| 16 | Aurora Beam | Ice | Đặc biệt | 65 | Carrion Swarm, LichMissile, tầm 700 | Hiệu ứng riêng: Icebeam |
| 17 | Avalanche | Ice | Vật lý | 60 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 18 | Axe Kick | Fighting | Vật lý | 120 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 19 | Belch | Poison | Đặc biệt | 120 | Carrion Swarm, ChimaeraAcidMissile, tầm 800 | Đạn hệ Poison: GreenShot |
| 20 | Bite | Dark | Vật lý | 60 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 21 | Blast Burn | Fire | Đặc biệt | 150 | Blizzard, hiệu ứng gốc, tầm 800 | Giữ nguyên |
| 22 | Blaze Kick | Fire | Vật lý | 85 | Storm Bolt, RedDragonMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 23 | Blizzard | Ice | Đặc biệt | 110 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 24 | Body Press | Fighting | Vật lý | 80 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 25 | Body Slam | Normal | Vật lý | 85 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 26 | Bone Rush | Ground | Vật lý | 25 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): WarStompCaster trên mục tiêu |
| 27 | Bonemerang | Ground | Vật lý | 50 | Impale, hiệu ứng gốc, tầm 700 | Hiệu ứng riêng: boomerrangbone |
| 28 | Boomburst | Normal | Đặc biệt | 140 | Blizzard, hiệu ứng gốc, tầm 800 | Giữ nguyên |
| 29 | Bounce | Flying | Vật lý | 85 | Shockwave, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 30 | Brave Bird | Flying | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 31 | Breaking Swipe | Dragon | Vật lý | 60 | Shockwave, FrostWyrmMissile, tầm 700 | Cận chiến (tầm 150, không đạn): purple claw trên mục tiêu |
| 32 | Brick Break | Fighting | Vật lý | 75 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 33 | Brine | Water | Đặc biệt | 65 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 34 | Brutal Swing | Dark | Vật lý | 60 | Storm Bolt, AvengerMissile, tầm 600 | Đạn hệ Dark: Voidbolt Medium |
| 35 | Bubble Beam | Water | Đặc biệt | 65 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 36 | Bug Bite | Bug | Vật lý | 60 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 37 | Bug Buzz | Bug | Đặc biệt | 90 | Breath of Fire, ZigguratMissile, tầm 375 | Giữ nguyên |
| 38 | Bulldoze | Ground | Vật lý | 60 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 39 | Bullet Punch | Steel | Vật lý | 40 | Storm Bolt, GryphonRiderMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 40 | Bullet Seed | Grass | Vật lý | 25 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 41 | Burning Jealousy | Fire | Đặc biệt | 70 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 42 | Charge Beam | Electric | Đặc biệt | 50 | Carrion Swarm, FarseerMissile, tầm 700 | Đạn hệ Electric: blue energy arrow |
| 43 | Chilling Water | Water | Đặc biệt | 50 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 44 | Clear Smog | Poison | Đặc biệt | 50 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Đạn hệ Poison: GreenShot |
| 45 | Close Combat | Fighting | Vật lý | 120 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 46 | Confusion | Psychic | Đặc biệt | 50 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 47 | Covet | Normal | Vật lý | 60 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 48 | Crabhammer | Water | Vật lý | 100 | Storm Bolt, WaterElementalMissile, tầm 600 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 49 | Cross Chop | Fighting | Vật lý | 100 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 50 | Cross Poison | Poison | Vật lý | 70 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Cận chiến (tầm 150, không đạn): purple claw trên mục tiêu |
| 51 | Crunch | Dark | Vật lý | 80 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 52 | Crush Claw | Normal | Vật lý | 75 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 53 | Cut | Normal | Vật lý | 50 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 54 | Dark Pulse | Dark | Đặc biệt | 80 | Carrion Swarm, AvengerMissile, tầm 700 | Đạn hệ Dark: Voidbolt Medium |
| 55 | Darkest Lariat | Dark | Vật lý | 85 | Storm Bolt, AvengerMissile, tầm 600 | Đạn hệ Dark: Voidbolt Major |
| 56 | Dazzling Gleam | Fairy | Đặc biệt | 80 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: VioletPulse |
| 57 | Dig | Ground | Vật lý | 80 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 58 | Disarming Voice | Fairy | Đặc biệt | 40 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 59 | Discharge | Electric | Đặc biệt | 80 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: SS2 Lightning |
| 60 | Dive | Water | Vật lý | 80 | Shockwave, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 61 | Doom Desire | Steel | Đặc biệt | 140 | Carrion Swarm, GryphonRiderMissile, tầm 800 | Đạn hệ Steel: Psionic Shot Silver |
| 62 | Double Edge | Normal | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 63 | Double Hit | Normal | Vật lý | 35 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 64 | Double Kick | Fighting | Vật lý | 30 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 65 | Draco Meteor | Dragon | Đặc biệt | 130 | Carrion Swarm, FrostWyrmMissile, tầm 800 | Đạn hệ Dragon: Voidbolt Major |
| 66 | Dragon Ascent | Flying | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Đạn hệ Flying: FeatherMissile |
| 67 | Dragon Breath | Dragon | Đặc biệt | 60 | Breath of Fire, FrostWyrmMissile, tầm 375 | Giữ nguyên |
| 68 | Dragon Claw | Dragon | Vật lý | 80 | Shadow Strike, FrostWyrmMissile, tầm 300 | Cận chiến (tầm 150, không đạn): purple claw trên mục tiêu |
| 69 | Dragon Pulse | Dragon | Đặc biệt | 85 | Carrion Swarm, FrostWyrmMissile, tầm 700 | Đạn hệ Dragon: Voidbolt Major |
| 70 | Dragon Rush | Dragon | Vật lý | 100 | Shockwave, FrostWyrmMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 71 | Dragon Tail | Dragon | Vật lý | 60 | Shockwave, FrostWyrmMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 72 | Drain Punch | Fighting | Vật lý | 75 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 73 | Draining Kiss | Fairy | Đặc biệt | 50 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 74 | Dream Eater | Psychic | Đặc biệt | 100 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 75 | Drill Peck | Flying | Vật lý | 80 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 76 | Drill Run | Ground | Vật lý | 80 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): WarStompCaster trên mục tiêu |
| 77 | Dual Wingbeat | Flying | Vật lý | 40 | Carrion Swarm, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 78 | Dynamic Punch | Fighting | Vật lý | 100 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 79 | Earth Power | Ground | Đặc biệt | 90 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: WarStompCaster |
| 80 | Earthquake | Ground | Vật lý | 100 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 81 | Echoed Voice | Normal | Đặc biệt | 40 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 82 | Electroweb | Electric | Đặc biệt | 55 | Frost Nova, BoltImpact, tầm 700 | Diện rộng: SS2 Lightning |
| 83 | Ember | Fire | Đặc biệt | 40 | Breath of Fire, RedDragonMissile, tầm 375 | Hiệu ứng riêng: Ember |
| 84 | Energy Ball | Grass | Đặc biệt | 90 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 85 | Eruption | Fire | Đặc biệt | 150 | Blizzard, hiệu ứng gốc, tầm 800 | Giữ nguyên |
| 86 | Expanding Force | Psychic | Đặc biệt | 80 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 87 | Explosion | Normal | Vật lý | 250 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 88 | Extrasensory | Psychic | Đặc biệt | 80 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 89 | Extreme Speed | Normal | Vật lý | 80 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 90 | Facade | Normal | Vật lý | 70 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 91 | Fairy Wind | Fairy | Đặc biệt | 40 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 92 | Fake Out | Normal | Vật lý | 40 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 93 | False Swipe | Normal | Vật lý | 40 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 94 | Feint | Normal | Vật lý | 30 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 95 | Fell Stinger | Bug | Vật lý | 50 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 96 | Fire Blast | Fire | Đặc biệt | 110 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 97 | Fire Fang | Fire | Vật lý | 65 | Shadow Strike, RedDragonMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 98 | Fire Pledge | Fire | Đặc biệt | 80 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 99 | Fire Punch | Fire | Vật lý | 75 | Storm Bolt, RedDragonMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 100 | Fire Spin | Fire | Đặc biệt | 35 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 101 | First Impression | Bug | Vật lý | 90 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 102 | Flame Charge | Fire | Vật lý | 50 | Shockwave, RedDragonMissile, tầm 700 | Đạn hệ Fire: Firebolt Minor |
| 103 | Flame Wheel | Fire | Vật lý | 60 | Storm Bolt, RedDragonMissile, tầm 600 | Đạn hệ Fire: Firebolt Minor |
| 104 | Flamethrower | Fire | Đặc biệt | 90 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 105 | Flare Blitz | Fire | Vật lý | 120 | Shockwave, RedDragonMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 106 | Flash Cannon | Steel | Đặc biệt | 80 | Carrion Swarm, GryphonRiderMissile, tầm 700 | Đạn hệ Steel: Psionic Shot Silver |
| 107 | Flip Turn | Water | Vật lý | 60 | Storm Bolt, WaterElementalMissile, tầm 600 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 108 | Fly | Flying | Vật lý | 90 | Shockwave, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 109 | Focus Blast | Fighting | Đặc biệt | 120 | Carrion Swarm, ZigguratMissile, tầm 800 | Đạn hệ Fighting: Holy Missile |
| 110 | Focus Punch | Fighting | Vật lý | 150 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 111 | Force Palm | Fighting | Vật lý | 60 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 112 | Foul Play | Dark | Vật lý | 95 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 113 | Freeze Dry | Ice | Đặc biệt | 70 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 114 | Frenzy Plant | Grass | Đặc biệt | 150 | Blizzard, hiệu ứng gốc, tầm 800 | Diện rộng: Tangroots |
| 115 | Fury Attack | Normal | Vật lý | 15 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 116 | Fury Cutter | Bug | Vật lý | 40 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Zornklinge trên mục tiêu |
| 117 | Fury Swipes | Normal | Vật lý | 18 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 118 | Future Sight | Psychic | Đặc biệt | 120 | Carrion Swarm, FaerieDragonMissile, tầm 800 | Đạn hệ Psychic: Arcade Bolt Psyche |
| 119 | Giga Drain | Grass | Đặc biệt | 75 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 120 | Giga Impact | Normal | Vật lý | 150 | Shockwave, ZigguratMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 121 | Grass Pledge | Grass | Đặc biệt | 80 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 122 | Grassy Glide | Grass | Vật lý | 55 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 123 | Gunk Shot | Poison | Vật lý | 120 | Shockwave, ChimaeraAcidMissile, tầm 800 | Đạn hệ Poison: GreenShot |
| 124 | Gust | Flying | Đặc biệt | 40 | Carrion Swarm, ZigguratMissile, tầm 700 | Đạn hệ Flying: FeatherMissile |
| 125 | Hammer Arm | Fighting | Vật lý | 100 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 126 | Head Smash | Rock | Vật lý | 150 | Shockwave, AncientProtectorMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 127 | Headbutt | Normal | Vật lý | 70 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 128 | Heat Wave | Fire | Đặc biệt | 95 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 129 | Hex | Ghost | Đặc biệt | 65 | Frost Nova, DeathCoilSpecialArt, tầm 700 | Diện rộng: VioletPulse |
| 130 | Hidden Power | Normal | Đặc biệt | 60 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 131 | High Horsepower | Ground | Vật lý | 95 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 132 | High Jump Kick | Fighting | Vật lý | 130 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 133 | Horn Attack | Normal | Vật lý | 65 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 134 | Hurricane | Flying | Đặc biệt | 110 | Thunder Clap, ThunderClapCaster, tầm  | Hiệu ứng riêng: Stormfall |
| 135 | Hydro Cannon | Water | Đặc biệt | 150 | Carrion Swarm, WaterElementalMissile, tầm 800 | Đạn hệ Water: Water Shot |
| 136 | Hydro Pump | Water | Đặc biệt | 110 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 137 | Hyper Beam | Normal | Đặc biệt | 150 | Carrion Swarm, ZigguratMissile, tầm 800 | Đạn hệ Normal: Sonic Missile |
| 138 | Hyper Fang | Normal | Vật lý | 80 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 139 | Hyper Voice | Normal | Đặc biệt | 90 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 140 | Ice Beam | Ice | Đặc biệt | 90 | Carrion Swarm, LichMissile, tầm 700 | Hiệu ứng riêng: Icebeam |
| 141 | Ice Fang | Ice | Vật lý | 65 | Shadow Strike, LichMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 142 | Ice Punch | Ice | Vật lý | 75 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 143 | Ice Shard | Ice | Vật lý | 40 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 144 | Ice Spinner | Ice | Vật lý | 80 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 145 | Icicle Crash | Ice | Vật lý | 85 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 146 | Icicle Spear | Ice | Vật lý | 25 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 147 | Icy Wind | Ice | Đặc biệt | 55 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 148 | Incinerate | Fire | Đặc biệt | 60 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 149 | Inferno | Fire | Đặc biệt | 100 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 150 | Infestation | Bug | Đặc biệt | 20 | Breath of Fire, ZigguratMissile, tầm 375 | Giữ nguyên |
| 151 | Iron Head | Steel | Vật lý | 80 | Shockwave, GryphonRiderMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 152 | Iron Tail | Steel | Vật lý | 100 | Storm Bolt, GryphonRiderMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 153 | Judgment | Normal | Đặc biệt | 100 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 154 | Knock Off | Dark | Vật lý | 65 | Shadow Strike, AvengerMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 155 | Kowtow Cleave | Dark | Vật lý | 85 | Storm Bolt, AvengerMissile, tầm 600 | Đạn hệ Dark: Voidbolt Major |
| 156 | Lash Out | Dark | Vật lý | 75 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 157 | Last Resort | Normal | Vật lý | 140 | Shockwave, ZigguratMissile, tầm 800 | Đạn hệ Normal: Sonic Missile |
| 158 | Lava Plume | Fire | Đặc biệt | 80 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 159 | Leaf Blade | Grass | Vật lý | 90 | Shadow Strike, GreenDragonMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 160 | Leaf Storm | Grass | Đặc biệt | 130 | Blizzard, hiệu ứng gốc, tầm 800 | Diện rộng: Tangroots |
| 161 | Leafage | Grass | Vật lý | 40 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 162 | Leech Life | Bug | Vật lý | 80 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 163 | Lick | Ghost | Vật lý | 30 | Shadow Strike, BansheeMissile, tầm 300 | Đạn hệ Ghost: Spectral Missile |
| 164 | Liquidation | Water | Vật lý | 85 | Storm Bolt, WaterElementalMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 165 | Low Sweep | Fighting | Vật lý | 65 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 166 | Lunge | Bug | Vật lý | 80 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 167 | Mach Punch | Fighting | Vật lý | 40 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 168 | Magical Leaf | Grass | Đặc biệt | 60 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 169 | Mega Drain | Grass | Đặc biệt | 40 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 170 | Mega Kick | Normal | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 171 | Mega Punch | Normal | Vật lý | 80 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 172 | Megahorn | Bug | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 173 | Metal Claw | Steel | Vật lý | 50 | Shadow Strike, GryphonRiderMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Zornklinge trên mục tiêu |
| 174 | Meteor Assault | Fighting | Vật lý | 150 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 175 | Meteor Beam | Rock | Đặc biệt | 120 | Carrion Swarm, AncientProtectorMissile, tầm 800 | Đạn hệ Rock: GolemAlolanProjectile4 |
| 176 | Meteor Mash | Steel | Vật lý | 90 | Storm Bolt, GryphonRiderMissile, tầm 600 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 177 | Misty Explosion | Fairy | Đặc biệt | 100 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: VioletPulse |
| 178 | Moonblast | Fairy | Đặc biệt | 95 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 179 | Mud Shot | Ground | Đặc biệt | 55 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 180 | Mud Slap | Ground | Đặc biệt | 20 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 181 | Muddy Water | Water | Đặc biệt | 90 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 182 | Mystical Fire | Fire | Đặc biệt | 75 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 183 | Night Slash | Dark | Vật lý | 70 | Shadow Strike, AvengerMissile, tầm 300 | Cận chiến (tầm 150, không đạn): purple claw trên mục tiêu |
| 184 | Origin Pulse | Water | Đặc biệt | 110 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 185 | Outrage | Dragon | Vật lý | 120 | Shockwave, FrostWyrmMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 186 | Overheat | Fire | Đặc biệt | 130 | Breath of Fire, RedDragonMissile, tầm 375 | Giữ nguyên |
| 187 | Pay Day | Normal | Vật lý | 40 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 188 | Payback | Dark | Vật lý | 50 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 189 | Peck | Flying | Vật lý | 35 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 190 | Petal Blizzard | Grass | Vật lý | 90 | War Stomp, WarStompCaster, tầm  | Diện rộng: Tangroots |
| 191 | Petal Dance | Grass | Đặc biệt | 120 | Blizzard, hiệu ứng gốc, tầm 800 | Diện rộng: Tangroots |
| 192 | Phantom Force | Ghost | Vật lý | 90 | Shadow Strike, BansheeMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 193 | Pin Missile | Bug | Vật lý | 25 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 194 | Play Rough | Fairy | Vật lý | 90 | Frost Nova, StarfallTarget, tầm 700 | Diện rộng: VioletPulse |
| 195 | Pluck | Flying | Vật lý | 60 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Flying: FeatherMissile |
| 196 | Poison Fang | Poison | Vật lý | 50 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 197 | Poison Jab | Poison | Vật lý | 80 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 198 | Poison Sting | Poison | Vật lý | 15 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Đạn hệ Poison: GreenShot |
| 199 | Poison Tail | Poison | Vật lý | 50 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 200 | Pollen Puff | Bug | Đặc biệt | 90 | Breath of Fire, ZigguratMissile, tầm 375 | Giữ nguyên |
| 201 | Poltergeist | Ghost | Vật lý | 110 | Shadow Strike, BansheeMissile, tầm 300 | Đạn hệ Ghost: Spectral Missile |
| 202 | Pounce | Bug | Vật lý | 50 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 203 | Pound | Normal | Vật lý | 40 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 204 | Powder Snow | Ice | Đặc biệt | 40 | Breath of Fire, LichMissile, tầm 375 | Giữ nguyên |
| 205 | Power Gem | Rock | Đặc biệt | 80 | Frost Nova, ThunderClapCaster, tầm 700 | Diện rộng: WarStompCaster |
| 206 | Power Whip | Grass | Vật lý | 120 | Shockwave, GreenDragonMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Powerwhip trên mục tiêu |
| 207 | Precipice Blades | Ground | Vật lý | 120 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 208 | Psybeam | Psychic | Đặc biệt | 65 | Carrion Swarm, FaerieDragonMissile, tầm 700 | Hiệu ứng riêng: Arcade Bolt Psyche |
| 209 | Psychic | Psychic | Đặc biệt | 90 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 210 | Psychic Fangs | Psychic | Vật lý | 85 | Shadow Strike, FaerieDragonMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 211 | Psychic Noise | Psychic | Đặc biệt | 75 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 212 | Psycho Boost | Psychic | Đặc biệt | 140 | Carrion Swarm, FaerieDragonMissile, tầm 800 | Đạn hệ Psychic: Arcade Bolt Psyche |
| 213 | Psycho Cut | Psychic | Vật lý | 70 | Shadow Strike, FaerieDragonMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Zornklinge trên mục tiêu |
| 214 | Psyshock | Psychic | Đặc biệt | 80 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 215 | Psystrike | Psychic | Đặc biệt | 100 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 216 | Pursuit | Dark | Vật lý | 40 | Storm Bolt, AvengerMissile, tầm 600 | Đạn hệ Dark: Voidball Minor |
| 217 | Quick Attack | Normal | Vật lý | 40 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 218 | Rage | Normal | Vật lý | 20 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 219 | Rage Fist | Ghost | Vật lý | 50 | Shadow Strike, BansheeMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 220 | Raging Bull | Normal | Vật lý | 90 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 221 | Rapid Spin | Normal | Vật lý | 50 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 222 | Razor Leaf | Grass | Vật lý | 55 | War Stomp, WarStompCaster, tầm  | Hiệu ứng riêng: RazorLeafSelf |
| 223 | Razor Shell | Water | Vật lý | 75 | Storm Bolt, WaterElementalMissile, tầm 600 | Đạn hệ Water: Water Shot |
| 224 | Retaliate | Normal | Vật lý | 70 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 225 | Revenge | Fighting | Vật lý | 60 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 226 | Roar Of Time | Dragon | Đặc biệt | 150 | Carrion Swarm, FrostWyrmMissile, tầm 800 | Đạn hệ Dragon: Voidbolt Major |
| 227 | Rock Blast | Rock | Vật lý | 25 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 228 | Rock Slide | Rock | Vật lý | 75 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 229 | Rock Throw | Rock | Vật lý | 50 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 230 | Rock Tomb | Rock | Vật lý | 60 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 231 | Rock Wrecker | Rock | Vật lý | 150 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 232 | Rollout | Rock | Vật lý | 30 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 233 | Round | Normal | Đặc biệt | 60 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 234 | Sacred Fire | Fire | Vật lý | 100 | Storm Bolt, RedDragonMissile, tầm 600 | Đạn hệ Fire: Firebolt Medium |
| 235 | Sacred Sword | Fighting | Vật lý | 90 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 236 | Sand Tomb | Ground | Vật lý | 35 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 237 | Scald | Water | Đặc biệt | 80 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 238 | Scale Shot | Dragon | Vật lý | 25 | Shockwave, FrostWyrmMissile, tầm 700 | Đạn hệ Dragon: Voidbolt Major |
| 239 | Scorching Sands | Ground | Đặc biệt | 70 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 240 | Scratch | Normal | Vật lý | 40 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 241 | Seed Bomb | Grass | Vật lý | 80 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 242 | Self Destruct | Normal | Vật lý | 200 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 243 | Shadow Ball | Ghost | Đặc biệt | 80 | Frost Nova, DeathCoilSpecialArt, tầm 700 | Diện rộng: VioletPulse |
| 244 | Shadow Claw | Ghost | Vật lý | 70 | Shadow Strike, BansheeMissile, tầm 300 | Cận chiến (tầm 150, không đạn): purple claw trên mục tiêu |
| 245 | Shadow Punch | Ghost | Vật lý | 60 | Shadow Strike, BansheeMissile, tầm 300 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 246 | Shadow Sneak | Ghost | Vật lý | 40 | Shadow Strike, BansheeMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 247 | Shock Wave | Electric | Đặc biệt | 60 | Frost Nova, BoltImpact, tầm 700 | Diện rộng: SS2 Lightning |
| 248 | Skitter Smack | Bug | Vật lý | 70 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 249 | Sky Attack | Flying | Vật lý | 140 | Shockwave, ZigguratMissile, tầm 800 | Đạn hệ Flying: FeatherMissile |
| 250 | Slam | Normal | Vật lý | 80 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 251 | Slash | Normal | Vật lý | 70 | Shadow Strike, ZigguratMissile, tầm 300 | Cận chiến (tầm 150, không đạn): slash-luc trên mục tiêu |
| 252 | Sludge Bomb | Poison | Đặc biệt | 90 | Breath of Fire, ChimaeraAcidMissile, tầm 375 | Diện rộng: GreenBoom |
| 253 | Sludge Wave | Poison | Đặc biệt | 95 | Thunder Clap, ThunderClapCaster, tầm  | Diện rộng: GreenBoom |
| 254 | Smack Down | Rock | Vật lý | 50 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 255 | Smart Strike | Steel | Vật lý | 70 | Storm Bolt, GryphonRiderMissile, tầm 600 | Cận chiến (tầm 150, không đạn): Zornklinge trên mục tiêu |
| 256 | Smog | Poison | Đặc biệt | 30 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Đạn hệ Poison: GreenShot |
| 257 | Snarl | Dark | Đặc biệt | 55 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 258 | Snore | Normal | Đặc biệt | 50 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 259 | Solar Beam | Grass | Đặc biệt | 120 | Carrion Swarm, GreenDragonMissile, tầm 800 | Đạn hệ Grass: GreenShot |
| 260 | Solar Blade | Grass | Vật lý | 125 | Shockwave, GreenDragonMissile, tầm 800 | Đạn hệ Grass: GreenShot |
| 261 | Spacial Rend | Dragon | Đặc biệt | 100 | Breath of Fire, FrostWyrmMissile, tầm 375 | Giữ nguyên |
| 262 | Spark | Electric | Vật lý | 65 | Storm Bolt, FarseerMissile, tầm 600 | Đạn hệ Electric: blue energy arrow |
| 263 | Steel Beam | Steel | Đặc biệt | 140 | Carrion Swarm, GryphonRiderMissile, tầm 800 | Đạn hệ Steel: Psionic Shot Silver |
| 264 | Steel Wing | Steel | Vật lý | 70 | Storm Bolt, GryphonRiderMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 265 | Stomp | Normal | Vật lý | 65 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): WarStompCaster trên mục tiêu |
| 266 | Stomping Tantrum | Ground | Vật lý | 75 | War Stomp, WarStompCaster, tầm  | Diện rộng: WarStompCaster |
| 267 | Stone Edge | Rock | Vật lý | 100 | Impale, hiệu ứng gốc, tầm 700 | Diện rộng: WarStompCaster |
| 268 | Stored Power | Psychic | Đặc biệt | 20 | Frost Nova, FrostNovaTarget, tầm 800 | Diện rộng: VioletPulse |
| 269 | Storm Throw | Fighting | Vật lý | 60 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Fighting: Holy Missile |
| 270 | Strength | Normal | Vật lý | 80 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 271 | Struggle Bug | Bug | Đặc biệt | 50 | Breath of Fire, ZigguratMissile, tầm 375 | Giữ nguyên |
| 272 | Submission | Fighting | Vật lý | 80 | Storm Bolt, ZigguratMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 273 | Sucker Punch | Dark | Vật lý | 70 | Shadow Strike, AvengerMissile, tầm 300 | Cận chiến (tầm 150, không đạn): Blitzangriff trên mục tiêu |
| 274 | Supercell Slam | Electric | Vật lý | 100 | War Stomp, WarStompCaster, tầm  | Diện rộng: SS2 Lightning |
| 275 | Superpower | Fighting | Vật lý | 120 | War Stomp, WarStompCaster, tầm  | Giữ nguyên |
| 276 | Surf | Water | Đặc biệt | 90 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 277 | Swift | Normal | Đặc biệt | 60 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 278 | Tackle | Normal | Vật lý | 40 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 279 | Take Down | Normal | Vật lý | 90 | Shockwave, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 280 | Temper Flare | Fire | Vật lý | 75 | Storm Bolt, RedDragonMissile, tầm 600 | Đạn hệ Fire: Firebolt Minor |
| 281 | Tera Blast | Normal | Đặc biệt | 80 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 282 | Thief | Dark | Vật lý | 60 | Shadow Strike, AvengerMissile, tầm 300 | Đạn hệ Dark: Voidbolt Medium |
| 283 | Thrash | Normal | Vật lý | 120 | Shockwave, ZigguratMissile, tầm 800 | Đạn hệ Normal: Sonic Missile |
| 284 | Throat Chop | Dark | Vật lý | 80 | Storm Bolt, AvengerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 285 | Thunder | Electric | Đặc biệt | 110 | Thunder Clap, ThunderClapCaster, tầm  | Hiệu ứng riêng: Stormfall |
| 286 | Thunder Fang | Electric | Vật lý | 65 | Shadow Strike, FarseerMissile, tầm 300 | Cận chiến (tầm 150, không đạn): galvanattack trên mục tiêu |
| 287 | Thunder Punch | Electric | Vật lý | 75 | Storm Bolt, FarseerMissile, tầm 600 | Cận chiến (tầm 150, không đạn): galvanattack trên mục tiêu |
| 288 | Thunder Shock | Electric | Đặc biệt | 40 | Frost Nova, BoltImpact, tầm 700 | Diện rộng: SS2 Lightning |
| 289 | Thunderbolt | Electric | Đặc biệt | 90 | Frost Nova, BoltImpact, tầm 700 | Diện rộng: SS2 Lightning |
| 290 | Trailblaze | Grass | Vật lý | 50 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 291 | Tri Attack | Normal | Đặc biệt | 80 | Frost Nova, StarfallTarget, tầm 700 | Hiệu ứng riêng: Digital Ray |
| 292 | Triple Axel | Ice | Vật lý | 20 | Frost Nova, FrostNovaTarget, tầm 800 | Giữ nguyên |
| 293 | Twineedle | Bug | Vật lý | 25 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 294 | Twister | Dragon | Đặc biệt | 40 | Thunder Clap, ThunderClapCaster, tầm  | Giữ nguyên |
| 295 | U Turn | Bug | Vật lý | 70 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 296 | Upper Hand | Fighting | Vật lý | 65 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Fighting: Holy Missile |
| 297 | Uproar | Normal | Đặc biệt | 90 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 298 | Vacuum Wave | Fighting | Đặc biệt | 40 | Frost Nova, ThunderClapCaster, tầm 700 | Giữ nguyên |
| 299 | Venoshock | Poison | Đặc biệt | 65 | Shadow Strike, ChimaeraAcidMissile, tầm 300 | Đạn hệ Poison: GreenShot |
| 300 | Vice Grip | Normal | Vật lý | 55 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 301 | Vine Whip | Grass | Vật lý | 45 | Entangling Roots, hiệu ứng gốc, tầm 700 | Diện rộng: Tangroots |
| 302 | Vital Throw | Fighting | Vật lý | 70 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Fighting: Holy Missile |
| 303 | Volt Switch | Electric | Đặc biệt | 70 | Frost Nova, BoltImpact, tầm 700 | Diện rộng: SS2 Lightning |
| 304 | Water Gun | Water | Đặc biệt | 40 | Carrion Swarm, WaterElementalMissile, tầm 700 | Hiệu ứng riêng: Water Shot |
| 305 | Water Pledge | Water | Đặc biệt | 80 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 306 | Water Pulse | Water | Đặc biệt | 60 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 307 | Water Spout | Water | Đặc biệt | 150 | Blizzard, hiệu ứng gốc, tầm 800 | Giữ nguyên |
| 308 | Waterfall | Water | Vật lý | 80 | Storm Bolt, WaterElementalMissile, tầm 600 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 309 | Wave Crash | Water | Vật lý | 120 | Shockwave, WaterElementalMissile, tầm 800 | Đạn hệ Water: Water Shot |
| 310 | Weather Ball | Normal | Đặc biệt | 50 | Frost Nova, StarfallTarget, tầm 700 | Giữ nguyên |
| 311 | Whirlpool | Water | Đặc biệt | 35 | Carrion Swarm, WaterElementalMissile, tầm 700 | Đạn hệ Water: Water Shot |
| 312 | Wild Charge | Electric | Vật lý | 90 | Shockwave, FarseerMissile, tầm 700 | Cận chiến (tầm 150, không đạn): galvanattack trên mục tiêu |
| 313 | Wing Attack | Flying | Vật lý | 60 | Carrion Swarm, ZigguratMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
| 314 | Wood Hammer | Grass | Vật lý | 120 | Shockwave, GreenDragonMissile, tầm 800 | Cận chiến (tầm 150, không đạn): Coup de Grace Purple trên mục tiêu |
| 315 | Wrap | Normal | Vật lý | 15 | Storm Bolt, ZigguratMissile, tầm 600 | Đạn hệ Normal: Sonic Missile |
| 316 | X Scissor | Bug | Vật lý | 80 | Shadow Strike, ZigguratMissile, tầm 300 | Đạn hệ Bug: Wizardry Missile |
| 317 | Zap Cannon | Electric | Đặc biệt | 120 | Carrion Swarm, FarseerMissile, tầm 800 | Đạn hệ Electric: blue energy arrow |
| 318 | Zen Headbutt | Psychic | Vật lý | 80 | Shockwave, FaerieDragonMissile, tầm 700 | Cận chiến (tầm 150, không đạn): AnimatedBash trên mục tiêu |
