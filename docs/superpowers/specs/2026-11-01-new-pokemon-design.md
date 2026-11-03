# Pokemon Arena v2.2 — 8 dòng Pokemon mới (design)

Ngày: 2026-11-01 · Tiếp nối spec Mega + spec quái/legend · Build: `tools/build_v2.py`, `tools/version.txt` = `2.2`.

## Mục tiêu

Thêm 21 Pokemon chơi được (8 dòng, model PKLegends), 45 chiêu mang tên chiêu thật, tiến hóa theo level, 9 dạng Mega,
tavern thứ 5, Mega Shop III; đưa 8 dạng đầu vào `-random`.

## Pokemon

ID hero mới `EN00`–`EN0K` (chữ đầu viết hoa = hero). Mỗi dạng **sao chép object của hero Arena mẫu** (giữ hệ tấn công/giáp,
máu, chỉ số, tốc độ, kiểu di chuyển, đạn), rồi đổi: `unam`/`upro` (tên), `umdl`, `uico`, `usca`, `uhab` (bộ chiêu),
`uabi` = `AInv` (bỏ nội tại riêng của mẫu), tooltip tavern/hồi sinh, `uhot`/`ubpx`/`ubpy` (ô trong tavern).

| ID | Dạng | Mẫu | Tiến hóa | Bộ chiêu |
|----|------|-----|----------|----------|
| EN00 | Torchic | E003 Charmander | lv 16 → EN01 | K1 |
| EN01 | Combusken | E007 Charmeleon | lv 36 → EN02 | K1 |
| EN02 | Blaziken | E01C Arcanine | — | K1 |
| EN03 | Treecko | E008 Bulbasaur | lv 16 → EN04 | K2 |
| EN04 | Grovyle | E001 Ivysaur | lv 36 → EN05 | K2 |
| EN05 | Sceptile | E002 Venusaur | — | K2 |
| EN06 | Larvitar | E00N Geodude | lv 30 → EN07 | K3 |
| EN07 | Pupitar | E00O Graveler | lv 55 → EN08 | K3 |
| EN08 | Tyranitar | E00P Golem | — | K3 |
| EN09 | Ralts | E00G Abra | lv 20 → EN0A | K4 |
| EN0A | Kirlia | E00H Kadabra | lv 30 → EN0B; nhặt Sun Stone (`I00P`) → EN0C | K4 |
| EN0B | Gardevoir | E00I Alakazam | — | K4 |
| EN0C | Gallade | E010 Machamp | — | K5 |
| EN0D | Bagon | E01S Dratini | lv 30 → EN0E | K6 |
| EN0E | Shelgon | E01T Dragonair | lv 50 → EN0F | K6 |
| EN0F | Salamence | E01K Dragonite | — | K6 |
| EN0G | Beldum | E031 Magnemite | lv 20 → EN0H | K7 |
| EN0H | Metang | E032 Magneton | lv 45 → EN0I | K7 |
| EN0I | Metagross | E03V Steelix | — | K7 |
| EN0J | Lucario | E01Z Hitmonchan | — | K8 |
| EN0K | Absol | E03I Umbreon | — | K9 |

- Model/icon lấy từ PKLegends (`pkl_species_index`), import vào `war3mapImported\Poke\` (texture đổi đường dẫn như Mega);
  icon `ReplaceableTextures\CommandButtons\BTNPoke<Tên>.blp` + bản `DISBTN` (tạo xám nếu thiếu).
- Scale: để Pokemon mới cao bằng Pokemon mẫu trên màn hình: `usca = usca_mẫu × cao_model_mẫu / cao_model_mới`
  (giới hạn 0,2–6).
- Tiến hóa: module JASS `Evo_` — khi lên level ≥ mốc thì hiệu ứng, chờ 1,5 giây, `Mega_SafeReplace`; Kirlia nhặt Sun Stone
  thì xóa đá và biến thành Gallade. Dùng chung chống "ra 2 con".

## Tavern & Random

- Tavern mới `nTV5` (sao chép `n01H`, tên "Tavern Gen 3-4") tại (448, 4512), hướng 270, bán EN00, EN03, EN06, EN09, EN0D,
  EN0G, EN0J, EN0K (ô 4×2, phím Q W E R / A S D F).
- `-random` và tự random thêm 8 dạng trên (pool 43 → 51).

## Chiêu (45 = 9 bộ × 5)

ID `AP00`–`AP18` (2 ký tự base36). Mỗi chiêu = sao chép dòng skill gốc WC3 có sẵn trong `AbilityData.slk` của map (cùng mã),
đặt `hero=1`, `levels=3`, `levelSkip=10`, `reqLevel` theo ô, số liệu theo mẫu dưới; chuỗi viết mới (Name, Tip/Ubertip 3 cấp,
Research…, Art, Hotkey, Buttonpos) + art đạn/hiệu ứng theo hệ. 5 chiêu trong một bộ luôn khác mã gốc.

Ô và mốc học: Q lv 3 · W lv 6 · E lv 10 · passive lv 33 · R (tuyệt chiêu) lv 36.
Vị trí nút: Q 0,2 · W 1,2 · E 2,2 · passive 3,2 · R 2,1 (giống ult của Arena; 1,1 là Mega Evolve). Phím: Q W E R, passive
không phím. Nút học skill cùng cột, hàng 0.

Mẫu số liệu (cấp 1/2/3):

| Mẫu (mã) | Số liệu chính | Hồi chiêu | Mana |
|----------|---------------|-----------|------|
| WAVE (AUcs) | sát thương 150/250/350, tối đa 600/1000/1400, xa 800 | 10 | 75/125/175 |
| LINE (AOsh) | sát thương 175/275/375, tối đa 700/1100/1500, xa 800 | 11 | 90/140/190 |
| CONE (ANbf) | sát thương 125/200/275 + đốt 15/25/35 mỗi giây 5 giây | 10 | 75/125/175 |
| CHAIN (AOcl) | 120/190/260 mỗi mục tiêu, 4/5/6 mục tiêu | 10 | 90/140/190 |
| BOLT (AHtb) | 200/325/450 + choáng 1/1,25/1,5 giây | 12 | 100/150/200 |
| DAGGER (AEsh) | 100/175/250 tức thì + 20/30/40 mỗi giây 6 giây, làm chậm | 12 | 90/130/170 |
| STOMP (AOws) | 175/275/375 vùng 300, choáng 1,25/1,5/1,75 | 14 | 120/170/220 |
| NOVA (AUfn) | mục tiêu 200/300/400, vùng 125/200/275, làm chậm 3 giây | 12 | 110/160/210 |
| BUFF (Absk) | +15/25/35% tốc chạy, +25/45/65% tốc đánh, nhận +10% sát thương, 10 giây | 18 | 75/100/125 |
| CRIT (AOcr) | 15/20/25% chí mạng ×2/2,5/3 | — | — |
| EVADE (AEev) | né 12/18/24% | — | — |
| BASH (AHbh) | 15/20/25% +60/120/180 sát thương, choáng 0,75 | — | — |
| ULT_WAVE (AUcs) | 450/700/950, tối đa 2000/3000/4000, xa 1000 | 40 | 250/400/550 |
| ULT_LINE (AOsh) | 500/750/1000, tối đa 2000/3000/4000, xa 1000 | 40 | 250/400/550 |
| ULT_RAIN (AHbz) | 8/10/12 đợt, 90/130/170 mỗi đợt, vùng 300 | 45 | 250/400/550 |
| ULT_STAR (AEsf) | 60/90/120 mỗi sao, 15 giây, vùng 800 | 60 | 300/450/600 |
| ULT_STOMP (AOws) | 450/700/950 vùng 450, choáng 2/2,5/3 | 40 | 250/400/550 |

Bộ chiêu (Q / W / E / passive / R):

| Bộ | Q (lv 3) | W (lv 6) | E (lv 10) | Passive (lv 33) | R (lv 36) | Hệ art |
|----|----------|----------|-----------|-----------------|-----------|--------|
| K1 Blaziken | Ember CONE | Double Kick BOLT | Blaze Kick STOMP | Blaze CRIT | Blast Burn ULT_WAVE | lửa |
| K2 Sceptile | Bullet Seed CHAIN | Leaf Blade DAGGER | Agility BUFF | Overgrow EVADE | Leaf Storm ULT_LINE | cỏ |
| K3 Tyranitar | Rock Slide LINE | Crunch BOLT | Earthquake STOMP | Sand Stream BASH | Stone Edge ULT_RAIN | đá |
| K4 Gardevoir | Confusion WAVE | Psychic BOLT | Moonblast NOVA | Trace EVADE | Future Sight ULT_STAR | tâm linh |
| K5 Gallade | Psycho Cut LINE | Night Slash DAGGER | Swords Dance BUFF | Sharpness CRIT | Close Combat ULT_STOMP | tâm linh |
| K6 Salamence | Dragon Breath CONE | Dragon Claw BOLT | Dragon Dance BUFF | Intimidate BASH | Draco Meteor ULT_RAIN | rồng |
| K7 Metagross | Bullet Punch BOLT | Zen Headbutt LINE | Earthquake STOMP | Tough Claws CRIT | Meteor Mash ULT_RAIN | thép |
| K8 Lucario | Aura Sphere BOLT | Force Palm STOMP | Extreme Speed BUFF | Justified CRIT | Aura Storm ULT_WAVE | aura |
| K9 Absol | Night Slash DAGGER | Sucker Punch BOLT | Swords Dance BUFF | Super Luck CRIT | Future Sight ULT_STAR | bóng tối |

Art theo hệ (đạn/sóng; dùng model có sẵn trong WC3):
lửa `Abilities\Weapons\RedDragonBreath\RedDragonMissile.mdl`, cỏ `Abilities\Weapons\GreenDragonMissile\GreenDragonMissile.mdl`,
đá `Abilities\Weapons\AncientProtectorMissile\AncientProtectorMissile.mdl`, tâm linh `Abilities\Weapons\FaerieDragonMissile\FaerieDragonMissile.mdl`,
rồng `Abilities\Weapons\FrostWyrmMissile\FrostWyrmMissile.mdl`, thép
`Abilities\Weapons\GryphonRiderMissile\GryphonRiderMissile.mdl`, aura `Abilities\Weapons\ZigguratMissile\ZigguratMissile.mdl`,
bóng tối `Abilities\Weapons\AvengerMissile\AvengerMissile.mdl`. Chiêu không có đạn (STOMP, BUFF, passive, ULT_RAIN, ULT_STAR)
giữ hiệu ứng gốc. Icon chiêu dùng icon có sẵn trong WC3 phù hợp mẫu (vd. BTNBreathOfFire, BTNStormBolt…).

## Mega (9 dạng mới, chỉ số 4–24 tiếp bảng cũ)

ID tiếp nối: skin `hM0G`–`hM0O`, đá `IM0G`–`IM0O`, nút `AM0G`–`AM0O` (base36), order Channel mới (không trùng map):
`coldarrows`, `coldarrowstarg`, `faeriefireon`, `faeriefireoff`, `tankpilot`, `tankdroppilot`, `tankloadpilot`,
`townbelloff`, `volcano`. Giá 6000. Mega Shop III `nMS3` tại (−4864, 0) hướng 0 và (4864, 0) hướng 180.

| # | Mega | Unit gốc | Đá | Model PKL | Điểm STR/AGI/INT |
|---|------|----------|----|-----------|------------------|
| 16 | Mega Blaziken | EN02 | Blazikenite | MegaLohgock | 20/10/0 |
| 17 | Mega Sceptile | EN05 | Sceptilite | MegaGewaldro | 5/15/10 |
| 18 | Mega Tyranitar | EN08 | Tyranitarite | MegaDespotar | 20/5/5 |
| 19 | Mega Gardevoir | EN0B | Gardevoirite | GardevoirMega | 0/10/20 |
| 20 | Mega Gallade | EN0C | Galladite | MegaGallade | 20/10/0 |
| 21 | Mega Salamence | EN0F | Salamencite | MegaBrutalanda | 15/10/5 |
| 22 | Mega Metagross | EN0I | Metagrossite | MegaMetagross | 20/5/5 |
| 23 | Mega Lucario | EN0J | Lucarionite | MegaLucario | 10/10/10 |
| 24 | Mega Absol | EN0K | Absolite | MegaAbsol | 15/10/5 |

## Bảng file (MPQ)

Bảng hash 1024 không đủ. `save_with` nhận `hash_size` (4096): file có tên được xếp lại theo tên; 73 file không rõ tên được
chép vào mọi vị trí "nhà" có thể (từ đầu cụm liên tiếp tới vị trí cũ, cộng k·1024, k = 0..3) bằng chèn dò tuyến tính, nên
tra cứu theo tên thật luôn tìm thấy. Danh sách tên có sẵn tìm bằng bộ dò tên của `extract.py` (chuyển vào `mpq.py`).

## Ngoài phạm vi / hạn chế

- Item giới hạn theo hệ của map gốc không biết Pokemon mới → Pokemon mới mặc được mọi item hệ.
- Chiêu mới không có hiệu ứng code riêng như một số chiêu Arena; chỉ dùng cơ chế skill gốc WC3.

## Kiểm tra

Test Python: dữ liệu dạng/chiêu/Mega; object data (21 hero, 45 chiêu 3 cấp, 5 chiêu một bộ khác mã, tavern, shop);
mở rộng bảng hash (mọi tên đọc lại được, mọi file không rõ tên tra được từ mọi nhà khả dĩ); module `Evo_` qua `jasscheck`;
build v2.2 đọc lại được. Bạn test trong game: mua ở tavern 5, tiến hóa đúng mốc, Kirlia + Sun Stone → Gallade, chiêu học
được và dùng được, Mega mới, `-random` ra cả Pokemon mới.
