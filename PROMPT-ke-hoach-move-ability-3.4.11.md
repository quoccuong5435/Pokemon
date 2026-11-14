# Prompt: kế hoạch đã duyệt – chiêu thức, Ability, Elite Four, item (bản 3.4.11 và 3.4.12)

Ngày 2026-11-14. Người dùng đã duyệt cả 15 mục ("Duyệt hết"). Tài liệu gốc (bảng, số liệu đầy đủ):
https://claude.ai/artifact/PQ6rB4jucWYxdxaP14uhWv. Tài khoản kia có thể không mở được link, nên prompt dưới đây tự đủ thông tin.

Cách dùng: mở phiên Claude Code của tài khoản đang giữ code 3.4.10, dán nguyên đoạn giữa hai dấu `---`.

---

Đây là kế hoạch tôi **đã duyệt** cho các bản tiếp theo của map (sau 3.4.10). Làm đúng theo kế hoạch. Chỗ nào code thực
tế khác với mô tả (tên hàm, key hashtable đã dùng, cách 3.4.10 đang làm) thì báo tôi trước khi tự đổi thiết kế.

Quy tắc:
- Trả lời tôi bằng tiếng Việt.
- **Không build** khi tôi chưa bảo. Được sửa code, chạy pjass, build thử `--dry-run`.
- Chia 2 đợt:
  - **Đợt 1 = bản 3.4.11;**
  - **Đợt 2 = bản 3.4.12.**
- Mỗi bản một số mới. Không ghi đè, không xóa map cũ.
- Tôi tự chơi thử rồi báo lỗi.
- Nếu trước đó tôi đã gửi prompt "ý tưởng cho 3.4.10" (nhóm A sửa lỗi, B tính năng, C kế hoạch), thì làm nhóm A trước. Mục C1
  (công / thủ Vật lý – Phép) làm cùng đợt 1 dưới đây.

## Thứ tự làm
**Đợt 1 – 3.4.11**
1. Việc độc lập, làm trước:
   - sửa item hệ (mục G);
   - không cầm 2 item giống nhau (mục H);
   - item hệ cho gym / Elite Four (mục I);
   - Elite Four vào phòng Darkrai, chặn PvP (mục J);
   - Ability huyền thoại và Pressure mới (mục E).
2. Bộ hiệu ứng chung (mục A), làm cùng công / thủ Vật lý – Phép (mục K).
3. Hiệu ứng của 319 move tấn công (mục B).
4. Rework 23 Ability (mục D).
5. Tooltip từng move ghi đúng hiệu ứng thật. Rồi pjass 0 lỗi, `--dry-run`, và bảng ví dụ sát thương trước / sau cho tôi xem.

**Đợt 2 – 3.4.12**
1. 58 move trạng thái mới (mục C): ability ẩn `AK..` theo cách 3.4.10 đang làm với move, icon, tooltip, learnset.
2. NPC dạy move bán các move này. Tự học khi lên cấp chỉ lấy move tấn công.
3. AI dùng move mới (mục F).

## A. Bộ hiệu ứng chung (một module JASS mới)
- **Dữ liệu:** mỗi move có một dòng hiệu ứng, sinh bằng Python từ `tools/learnsets.json` (`moves[...]`: `class`,
  `power`, `priority`, `effect` = mô tả ngắn của PokeAPI), kèm danh sách chỉnh tay.
- **Gắn vào code:** lúc dùng chiêu (trigger spell effect của hệ move 3.4.10) và lúc tính sát thương (`Ab_OnDamaging` /
  `Ext_DamageMult`).
- **Một đồng hồ chung 0,25 giây** cho mọi hiệu ứng có thời hạn, không tạo timer riêng cho từng hiệu ứng.
- **Bậc chỉ số:**
  - Attack, Defense, Sp. Atk, Sp. Def, Speed;
  - **từ −4 đến +4, mỗi bậc ±25%** (Speed: ±15% tốc đánh và tốc chạy);
  - kéo dài 12 giây, dùng lại thì làm mới thời gian;
  - Attack tăng đòn đánh thường và move Vật lý; Sp. Atk tăng move Đặc biệt;
  - Defense giảm đòn đánh thường và move Vật lý nhận vào; Sp. Def giảm move Đặc biệt nhận vào.
- **Trạng thái chính** (mỗi Pokémon chỉ một cái cùng lúc):
  - **Thiêu đốt:** 1% máu tối đa/giây trong 6 giây, sát thương Vật lý −25%.
  - **Độc:** 1,5%/giây trong 6 giây. Độc nặng (Toxic) tăng dần từ 1% lên 4%/giây.
  - **Tê liệt:** tốc chạy −40%, tốc đánh −25% trong 5 giây.
  - **Ngủ:** choáng tối đa 2 giây, bị đánh thì tỉnh.
  - **Đóng băng:** choáng 1,5 giây; trúng chiêu Fire thì tan ngay.
- **Trạng thái phụ:**
  - **Lú lẫn:** 4 giây; mỗi đòn đánh 30% trượt và tự mất 3% máu.
  - **Chùn bước:** choáng 0,5 giây.
- **Miễn theo hệ:** Fire không bị thiêu đốt, Electric không tê liệt, Poison / Steel không bị độc, Ice không đóng băng,
  Grass miễn move dạng bột, Ground miễn Thunder Wave.
- **Chống khóa cứng:** ngủ / đóng băng / chùn bước lên cùng mục tiêu trong 6 giây thì lần sau chỉ còn nửa thời gian.
- **Hiệu ứng theo move:**
  - Nghỉ sau chiêu: đứng yên 2 giây, chữ "Recharging".
  - Tụ lực: niệm 1,2 giây (Solar Beam dưới nắng bắn ngay).
  - Biến mất: ẩn và bất tử 1 giây (Dig, Fly, Bounce, Phantom Force).
  - Hút máu: 50% sát thương (Draining Kiss 75%).
  - Phản sát thương: 1/4, 1/3 hoặc 1/2 theo game.
  - Đánh nhiều lần: 2–5 đòn, tổng trung bình như cũ; Skill Link luôn 5.
  - Chí mạng cao: 25% x1,5.
  - Ưu tiên: ra chiêu tức thì, lao tới, hồi chiêu ngắn hơn 30%.
  - Đánh rồi lùi: nhảy lùi 300.
  - Không trượt: bỏ qua né.
- **Trần tổng hệ số sát thương** (bậc + Life Orb + Choice + Champion Aura): ví dụ x3.

## B. 319 move tấn công (giữ hình dạng và hiệu ứng hình ảnh của 3.4.10)
- **113 move không có hiệu ứng phụ trong game:** bỏ choáng / chậm / trói đang mượn từ skill gốc WC3; sát thương +10% để bù.
- **Nhóm theo game gốc** (một move có thể thuộc nhiều nhóm):

| Nhóm | Số move | Ví dụ | Hiệu ứng |
|---|---|---|---|
| Nghỉ sau chiêu | 8 | Hyper Beam, Giga Impact, Blast Burn, Frenzy Plant, Hydro Cannon, Roar of Time, Rock Wrecker, Meteor Assault | Sát thương +20%, nghỉ 2 giây |
| Tụ lực / biến mất | 8 | Solar Beam, Solar Blade, Sky Attack, Meteor Beam (+1 Sp. Atk khi tụ), Dig, Fly, Bounce, Phantom Force | Như mục A |
| Phản sát thương | 9 | Flare Blitz, Brave Bird, Wood Hammer, Double-Edge (1/3); Head Smash (1/2); Take Down, Submission, Wild Charge, High Jump Kick (1/4) | Flare Blitz thêm 10% thiêu đốt |
| Hút máu | 7 | Absorb, Mega Drain, Giga Drain, Leech Life, Drain Punch, Draining Kiss, Dream Eater | Dream Eater x2 lên mục tiêu đang ngủ |
| Tự giảm chỉ số | 7 | Draco Meteor, Leaf Storm, Overheat, Psycho Boost (−2 Sp. Atk); Close Combat, Dragon Ascent (−1 Def, −1 Sp. Def); Superpower (−1 Atk, −1 Def) | |
| Tăng chỉ số bản thân | 7 | Flame Charge (+1 Speed), Charge Beam (70% +1 Sp. Atk), Metal Claw, Steel Wing, Meteor Mash, Fell Stinger (hạ gục: +3 Attack) | |
| Giảm chỉ số mục tiêu | 33 | Speed: Icy Wind, Bulldoze, Rock Tomb, Electroweb, Mud Shot. Def: Crunch, Iron Tail, Liquidation. Sp. Def: Psychic, Shadow Ball, Bug Buzz, Earth Power, Flash Cannon. Attack: Play Rough, Breaking Swipe. Sp. Atk: Moonblast, Mystical Fire, Snarl. Chính xác: Mud-Slap, Muddy Water | −1 bậc theo tỉ lệ game; giảm Speed = làm chậm; giảm chính xác = trượt 20% trong 4 giây |
| Thiêu đốt / tê liệt / độc / đóng băng | 16 / 14 / 11 / 6 | Flamethrower, Thunderbolt, Sludge Bomb, Ice Beam… | Tỉ lệ theo game (10–30%); Poison Fang = độc nặng; Tri Attack 20% ngẫu nhiên 1 trong 3 |
| Lú lẫn | 8 | Confusion, Psybeam, Water Pulse, Hurricane, Dynamic Punch (100%), Outrage, Petal Dance, Thrash | 3 move cuối đánh mạnh 3 giây rồi người dùng tự lú lẫn |
| Chùn bước | 21 | Bite, Air Slash, Dark Pulse, Iron Head, Zen Headbutt, Fake Out | Fake Out chắc chắn, chỉ trong 3 giây đầu giao tranh |
| Đánh nhiều lần | 13 | Bullet Seed, Rock Blast, Icicle Spear, Pin Missile, Fury Swipes, Double Kick, Bonemerang, Triple Axel | |
| Chí mạng cao | 17 | Leaf Blade, Cross Chop, Crabhammer, Air Cutter, Drill Run | |
| Ưu tiên | 13 | Quick Attack, Extreme Speed, Aqua Jet, Mach Punch, Bullet Punch, Ice Shard, Shadow Sneak, Sucker Punch, Vacuum Wave | |
| Trói | 5 | Wrap, Fire Spin, Whirlpool, Sand Tomb, Infestation | Trói 3 giây, sát thương theo giây |
| Đánh rồi lùi | 5 | U-turn, Volt Switch, Flip Turn; Dragon Tail (đẩy mục tiêu 300); Pursuit (x2 lên mục tiêu đang chạy) | |
| Không trượt | 9 | Aerial Ace, Swift, Aura Sphere, Shadow Punch, Shock Wave, Magical Leaf | |
| Tự hủy | 2 | Explosion, Self-Destruct | Người dùng mất 50% máu hiện tại, không chết |

- **Khác:** Pay Day rơi thêm vàng; Facade x2 khi người dùng đang bị trạng thái.
- **90 skill bộ kit** của elite / gym / huyền thoại (đặt tên theo move) dùng chung bảng hiệu ứng.

## C. 58 move trạng thái mới (đợt 2; chỉ học ở NPC: theo cấp 500 vàng, TM 3000 vàng)
- **Buff (14 move)**, kéo dài 12 giây, hồi chiêu 20 giây:

| Move | Hiệu ứng |
|---|---|
| Swords Dance | +2 Atk |
| Nasty Plot | +2 SpA |
| Dragon Dance | +1 Atk +1 Spe |
| Calm Mind | +1 SpA +1 SpD |
| Bulk Up | +1 Atk +1 Def |
| Quiver Dance | +1 SpA +1 SpD +1 Spe |
| Shell Smash | +2 Atk / SpA / Spe, −1 Def / SpD |
| Agility, Rock Polish | +2 Spe |
| Work Up, Growth | +1 Atk +1 SpA (Growth +2 dưới nắng) |
| Curse (không phải hệ Ghost) | +1 Atk +1 Def −1 Spe |
| Focus Energy | 3 đòn / chiêu tiếp 50% chí mạng x1,5 |
| Belly Drum | Mất 50% máu tối đa, Atk lên +4 |

- **Phòng thủ (20 move):**

| Move | Hiệu ứng | Hồi chiêu |
|---|---|---|
| Protect, Detect | Miễn mọi sát thương và trạng thái 1,5 giây | 18 giây |
| Recover, Roost, Slack Off, Soft-Boiled | Hồi 50% máu | 30 giây |
| Synthesis, Moonlight, Morning Sun | Hồi 50%; nắng 66%; mưa / bão cát / mưa đá 25% | 30 giây |
| Rest | Hồi đầy máu, xóa trạng thái, ngủ 3 giây | 40 giây |
| Iron Defense, Acid Armor | +2 Def | |
| Amnesia | +2 SpD | |
| Cosmic Power | +1 Def +1 SpD | |
| Reflect / Light Screen | Đồng minh trong 600 −30% sát thương Vật lý / Đặc biệt trong 8 giây | 30 giây |
| Substitute | Mất 25% máu, khiên bằng lượng đó trong 10 giây, còn khiên thì miễn trạng thái | |
| Aqua Ring, Ingrain | Hồi 2%/giây trong 12 giây | |
| Wish | Sau 2 giây, hồi 50% cho Pokémon đứng ở chỗ đã đặt | |

- **Gây bất lợi (24 move)**, tầm 600, hồi chiêu 15–20 giây:

| Move | Hiệu ứng |
|---|---|
| Growl | Địch trong 500 −1 Atk |
| Charm | −2 Atk |
| Leer, Tail Whip | Địch trong 500 −1 Def |
| Screech | −2 Def |
| Fake Tears, Metal Sound | −2 SpD |
| Scary Face | −2 Spe |
| String Shot | Địch trong 500 −1 Spe |
| Sand Attack | Trượt 20% trong 6 giây |
| Thunder Wave | Tê liệt |
| Will-O-Wisp | Thiêu đốt |
| Toxic | Độc nặng |
| Poison Powder, Stun Spore | Độc / tê liệt |
| Hypnosis, Sleep Powder, Spore, Sing | Ngủ 2 giây, 75% thành công (Spore chắc chắn) |
| Yawn | Sau 2 giây ngủ 2 giây |
| Confuse Ray | Lú lẫn |
| Swagger | Lú lẫn, mục tiêu +2 Atk |
| Leech Seed | Hút 2%/giây trong 8 giây (Grass miễn) |
| Taunt | Không dùng được move buff / phòng thủ trong 4 giây |

- **Learnset:** lấy từ `tools/learnsets.json` (`species[...].moves` theo cấp và `tm`).

## D. Rework 23 Ability (dùng bộ hiệu ứng mục A)
| Ability | Hiệu ứng mới |
|---|---|
| Rock Head | Không mất máu do phản sát thương; giữ −10% sát thương nhận |
| Reckless | Move phản sát thương và High Jump Kick +30%; đòn đánh +15% |
| Skill Link | Move đánh nhiều lần luôn 5 đòn |
| Iron Fist | Move đấm +25% |
| Strong Jaw | Move cắn +40% |
| Tough Claws | Move tiếp xúc +30%, đòn đánh +30% |
| Mega Launcher | Move sóng / xung (Water Pulse, Dark Pulse, Dragon Pulse, Aura Sphere) +50%; move Đặc biệt khác +15% |
| Guts | Đang thiêu đốt / độc / tê liệt: Vật lý +50%, không bị thiêu đốt làm yếu |
| Intimidate | Địch trong 500 −1 Atk trong 8 giây, hồi 20 giây |
| Clear Body | Không bị địch giảm chỉ số |
| Hyper Cutter | Không bị giảm Atk |
| Keen Eye | Không bị giảm chính xác |
| Inner Focus | Miễn chùn bước và Intimidate |
| Static / Flame Body / Poison Point | 30% tê liệt / thiêu đốt / độc kẻ đánh cận chiến (Poison Point cả khi đánh) |
| Synchronize | Bị gây trạng thái thì kẻ gây cũng bị |
| Shed Skin / Natural Cure | Xóa trạng thái (Shed Skin 30% mỗi 3 giây; Natural Cure khi ra khỏi giao tranh) |
| Insomnia / Early Bird | Miễn ngủ / ngủ còn một nửa |
| Speed Boost | Mỗi 8 giây trong giao tranh +1 Spe, tối đa +4 |
| Chlorophyll / Swift Swim | Dưới nắng / mưa thêm +2 Spe |
| Sand Veil / Snow Cloak | 10% né; trong bão cát / mưa đá 30% |
| Magic Bounce | Phản move gây bất lợi về kẻ dùng |

Phần hiện có của các Ability này giữ nguyên nếu không bị thay ở bảng trên.

## E. Ability huyền thoại và Pressure mới (cả huyền thoại hoang lẫn Pokémon của người chơi biến từ Soul)
- **Pressure huyền thoại:**
  - địch trong 800: move tốn gấp đôi mana, hồi chiêu chậm hơn 30%, tốc đánh −25%;
  - địch trong vùng −1 Atk và −1 SpA, làm mới mỗi 3 giây;
  - bản thân không bị giảm chỉ số, không bị chùn bước;
  - cách làm: lúc địch dùng chiêu trong vùng, trừ thêm mana bằng giá chiêu và đặt lại hồi chiêu dài hơn.
- **Pressure thường** (Weavile, Dusclops, Dusknoir, Kingambit, Deino, Zweilous): địch trong 600 tốn gấp đôi mana, hồi chiêu
  chậm hơn 20%, tốc đánh −15%.

| Huyền thoại | Ability mới |
|---|---|
| Mewtwo | Pressure huyền thoại + chiêu Psychic +20%; dưới 50% máu dựng khiên bằng 20% máu tối đa trong 8 giây (90 giây một lần) |
| Zapdos | Pressure huyền thoại + 30% tê liệt kẻ đánh cận chiến, chiêu Electric thêm 20% tê liệt |
| Articuno | Pressure huyền thoại + chiêu Ice thêm 20% đóng băng, miễn mưa đá |
| Moltres | Pressure huyền thoại + chiêu Fire thêm 20% thiêu đốt, miễn thiêu đốt |
| Raikou | Pressure huyền thoại + mỗi 8 giây +1 Spe (tối đa +3) |
| Giratina | Pressure huyền thoại + chiêu Ghost / Dragon +15%, 15% đòn nhận vào đi xuyên qua |
| Deoxys | Pressure huyền thoại + chiêu Psychic +15%, hồi chiêu nhanh hơn 15% |
| Dialga | Hồi chiêu của mình nhanh hơn 25%; địch trong 800 hồi chiêu chậm hơn 30%, tốc đánh −25%, move tốn gấp đôi mana |
| Palkia | Chiêu tầm +25%, 20% chí mạng x1,5; địch trong 800 tốc chạy −25%, move tốn gấp đôi mana |
| Entei | Flash Fire: miễn Fire, trúng Fire +40% sát thương 8 giây; đòn đánh 20% thiêu đốt |
| Suicune | Water Absorb (miễn Water, hồi 25% lượng đó) + Natural Cure |
| Ho-Oh | Regenerator: không bị đánh 3 giây thì hồi 3%/giây; 120 giây một lần, bị hạ thì hồi sinh tại chỗ với 40% máu |
| Kyogre | Drizzle: mưa 700 quanh mình; đồng minh Water +30%, Fire của địch −50%; hồi 1%/giây trong mưa |
| Groudon | Drought như cũ + Water của địch trong vùng −50% |
| Regirock | Sturdy (đòn chí tử để lại 15% máu, 60 giây một lần) + Clear Body |
| Jirachi | Serene Grace: tỉ lệ hiệu ứng phụ của move x2; chiêu +10% |
| Buzzwole | Beast Boost: hạ gục +1 Atk (tối đa +4, giữ 30 giây) |
| Regigigas | Slow Start 15 giây −30%, sau đó +50% sát thương, +30% tốc đánh, +2 Atk |
| Latias & Latios | Levitate + chiêu Dragon / Psychic +20%, 20% né |
| Rayquaza | Air Lock như cũ + miễn thời tiết, chiêu Dragon / Flying +20% |
| Darkrai | Bad Dreams như cũ + địch đang ngủ mất 8%/giây; chiêu của Darkrai 20% gây ngủ |

Nếu chơi thử thấy huyền thoại hoang quá khó thì giảm máu của chúng 10–15%.

## F. AI (đợt 2)
- **Bộ kit mới:** mỗi bộ kit của elite / gym / Elite Four / huyền thoại = 4 move tấn công + 1 move trạng thái hợp hệ.
- **Khi nào AI dùng move trạng thái:**
  - Buff: vừa vào giao tranh, máu trên 50%, 20 giây một lần.
  - Hồi máu: máu dưới 40%.
  - Protect: máu dưới 30% và có từ 2 kẻ đánh nó.
  - Reflect / Light Screen: có từ 2 địch trong 600.
  - Gây bất lợi: lên mục tiêu chưa bị trạng thái, ưu tiên Pokémon cấp cao nhất.
  - Move nghỉ sau chiêu: mục tiêu dưới 35% máu hoặc có từ 3 địch trong vùng.
- **Theo nhóm:**
  - gym 1–4 không dùng ngủ / đóng băng / lú lẫn;
  - Elite Four dùng đủ bộ (Lance có Dragon Dance, Karen có Nasty Plot);
  - quái hoang thường chỉ đánh thường.

## G. Sửa item hệ
- **Kết quả kiểm tra map 3.4.10:**

| Item | Vấn đề |
|---|---|
| Black Glasses `I01Y` (ability `A0BH`) | Dùng chung buff đánh dấu `B013` với Poison Barb, nên gây độc; câm không bao giờ xảy ra |
| `ITGD` Soft Sand và `ITFY` Pixie Plate của gym | Mang ability của Charcoal `A03B` |
| Soft Sand `I013` (`A03S`) và Hard Stone `I012` (`A03Q`) | Dựa vào aura `AHad` bán kính 0 làm dấu (`B018` / `B016`), có thể không bật; nếu bật thì cũng chỉ 100 sát thương cố định |
| `I013` | Tên sai "Solf Sand" |
| Silver Powder | Mô tả ghi 40%, dữ liệu 30% |

Mọi hiệu ứng phụ chỉ bật khi đánh thường.

- **Sửa:**
  - viết lại hiệu ứng riêng của 18 item hệ bằng code (cờ item như Battle Shop), bỏ unit giả và aura đánh dấu;
  - số liệu tăng theo sức mạnh (theo % sát thương của đòn, % máu tối đa);
  - move cùng hệ với item +20%; giữ +20% sát thương chung;
  - **Soft Sand mới:** 25% mỗi đòn đánh hoặc chiêu Ground: rung đất 300 quanh mục tiêu, sát thương bằng 50% đòn đó, chậm 40% trong 2 giây;
  - đổi tên "Soft Sand"; Black Glasses câm thật; item của gym dùng đúng hiệu ứng; thêm item Fairy cho người chơi mua.

## H. Không cầm 2 item giống nhau
- **Áp dụng cho item cầm lâu dài:** item hệ, 12 item Battle Shop, Lucky Egg, Amulet Coin, Everstone, Mega Ring, Mega Stone.
- **Không áp dụng cho đồ dùng hết:** Potion, Revive, Berry, Escape Rope, đá tiến hóa.
- **Mua trùng:** lấy lại item, hoàn đủ vàng, báo "Đã cầm item này rồi".
- **Nhặt trùng hoặc đồng đội đưa:** item rơi lại cạnh chân.

## I. Item hệ cho Pokémon gym và Elite Four (không rơi)
- **Ai cầm gì:**
  - mỗi Pokémon gym / Elite Four cầm item của hệ đầu tiên của nó (Ground: Soft Sand, Fairy: Pixie Plate);
  - Elite Four: Will Twisted Spoon, Koga Poison Barb, Bruno Black Belt, Karen Black Glasses, Lance Dragon Fang.
- **Không dùng item thật:** gắn thẳng các ability của item (cột `abilList` của item) vào Pokémon. Như vậy chết không rơi gì,
  không chạy trigger nhặt item của v1.8, không tự tiến hóa.
- Gym 1–4 chỉ lấy phần +20% sát thương.
- Tên item ghi sau tên Pokémon, ví dụ "Arcanine (Charcoal)".

## J. Elite Four ở phòng Darkrai, không bị PvP chen vào
- **Lấy code có sẵn:** `git fetch origin v3.4.2`, rồi đọc:
  - `tools/v34/league_area.py`: tọa độ, sơn nền `war3map.w3e`, tượng, ảnh xem trước;
  - các hàm `League_*` trong `tools/v34/jass/gym.j`: `League_Setup`, `League_PortalTick`, `League_Label`;
  - phần sơn nền trong `build_v34.py`;
  - Darkrai `nL19` trong `extras.py`.
- **Tọa độ:** phòng (−10240, −5120) đến (−6816, −160); tâm sân (−8768, −2640), sân bán kính 900, viền 1060; sảnh (−7360, −2640);
  cổng ra (−7040, −2640); cổng vào ở căn cứ (±5392, −288).
- **Tượng:** Will / Espeon 150°, Koga / Weezing 210°, Bruno / Machamp 120°, Karen / Umbreon 240°, Lance / Dragonite 180°,
  bán kính 1250.
- **Item:** "Darkrai's Location" (`IL01`) ở shop Haunt Legendary đổi thành "Pokemon League".
- **Cổng về thành:** cổng hiện có trong phòng Darkrai thành cổng ra, đưa về đúng căn cứ của mình.
- **Darkrai:** thành huyền thoại ngẫu nhiên (có Soul).
- **Sân riêng:** Elite Four không dùng chung sân với gym 8 nữa.
- **Chặn PvP khi có người đang đấu:**
  - người chơi khác vào sân bị đẩy ra sảnh, báo "Pokemon League đang có người đấu";
  - người chơi khác không gây sát thương lên người thách đấu; người thách đấu cũng không gây sát thương lên người chơi
    khác (báo "Đang đấu Elite Four");
  - người thách đấu vẫn bị hạ hoặc tự rời sân: tính thua, hồi sinh ngay ở sảnh League (không về căn cứ), chờ 30 giây
    (thay cho 60) là đấu lại được;
  - hai người cùng muốn đấu thì xếp hàng: báo thứ tự, tới lượt tự vào sân.
- **Revive / Max Revive** vẫn theo luật 3 giây hiện có.

## K. Công / thủ Vật lý – Phép (làm cùng đợt 1)
- **Hệ số chỉ số:** move Vật lý = STR / 50, move Đặc biệt = INT / 50 (thay cho "chỉ số lớn hơn / 50").
- **Hệ số thủ của mục tiêu** = 2 / (1 + thủ / 80), giới hạn x0,5–x1,5. Thủ là Def với move Vật lý, SpD với move Đặc biệt;
  bậc Def / SpD ở mục A nhân thêm vào.
- **Dữ liệu Def / SpD:** chỉ số gốc theo loài từ `tools/learnsets.json` (`species[...].stats`, thứ tự trong `stat_order`).
  Lưu vào `Ab_HT` theo loại unit, ở key chưa dùng (tránh 53/54, 99/100+, 299/300+, 699/700+). Mega dùng chỉ số dạng Mega,
  Zen dùng dạng Zen.
- **Item:** Choice Band = đòn đánh thường và move Vật lý +35%; Choice Specs = move Đặc biệt +35%; Assault Vest = −25% chỉ với
  move Đặc biệt.
- **Mặc định:** đòn đánh thường vẫn theo chỉ số chính; giáp giữ (Def + SpD) / 4.
- **Thêm:** tooltip ghi "Vật lý – theo STR, giảm theo Def" hoặc "Đặc biệt – theo INT, giảm theo SpD"; lệnh `-stats` hiện
  STR, INT, Def, SpD, các bậc chỉ số và trạng thái đang có.

Xong mỗi đợt, gửi tôi:
1. danh sách đã làm / chưa làm;
2. kết quả pjass và `--dry-run`;
3. bảng ví dụ sát thương trước / sau;
4. danh sách những gì tôi cần chơi thử.

---
