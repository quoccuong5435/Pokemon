# 7. Kế hoạch: công / thủ Vật lý và Phép (bản 3.4.3)

Ngày 2026-11-14. **Chưa sửa code: chờ duyệt.** Làm thành bản 3.4.3 (bản 3.4.2 giữ nguyên) và chỉ build khi bạn bảo.

## Mục tiêu
- **Move Vật lý** (Iron Tail, Close Combat…): sát thương theo **STR** (Attack) của người đánh, bị giảm theo **Def** của mục tiêu.
- **Move Đặc biệt / Phép** (Psychic, Flamethrower…): sát thương theo **INT** (Sp. Atk), bị giảm theo **SpD** của mục tiêu.
- Pokémon trâu vật lý (Steelix, Golem) chịu đòn vật lý tốt nhưng yếu phép; Pokémon trâu phép (Blissey, Snorlax) ngược lại.
- Độ mạnh chung giữ gần như cũ: mục tiêu có thủ trung bình (80) nhận đúng x1,0.

## Cần bạn chốt (mặc định mình đề xuất in đậm)
1. **Đòn đánh thường** tính theo:
   - (a) **giữ như cũ, theo chỉ số chính** (đỡ thay đổi cảm giác đánh tay);
   - (b) luôn theo STR (đúng kiểu Pokémon hơn, nhưng Pokémon thiên phép đánh tay sẽ yếu hẳn).
2. **Giáp:**
   - (a) **giữ (Def + SpD) / 4 như cũ**;
   - (b) đổi thành Def / 2 (thủ vật lý mạnh hẳn với đòn đánh thường, chênh lệch rất lớn: Steelix khoảng 100 giáp, Blissey 5 giáp).
3. **Công thức thủ chiêu:** hệ số nhận = 2 / (1 + thủ / 80), **giới hạn x0,5 đến x1,5**. Có thể nới thành x0,4 đến x1,6 nếu muốn
   khác biệt rõ hơn.
4. **Dạng Mega:** **dùng Def / SpD của dạng Mega** (bảng 33 dòng lấy từ PokemonDB, ghi trong code).

## Ví dụ hệ số nhận chiêu (công thức mục 3)
| Pokémon | Def | SpD | Nhận chiêu Vật lý | Nhận chiêu Phép |
|---|---|---|---|---|
| Steelix | 200 | 65 | x0,57 | x1,10 |
| Golem | 130 | 65 | x0,76 | x1,10 |
| Snorlax | 65 | 110 | x1,10 | x0,84 |
| Blissey | 10 | 135 | x1,5 (chạm trần) | x0,74 |
| Alakazam | 45 | 95 | x1,28 | x0,91 |
| Pikachu | 40 | 50 | x1,33 | x1,23 |
| Dragonite | 95 | 100 | x0,91 | x0,89 |

## Các bước làm
| # | Việc | File | Kiểm tra |
|---|---|---|---|
| 1 | **Dữ liệu thủ:** ghi Def và SpD của mọi Pokémon (hero chơi được, Pokémon gym, quái hoang, huyền thoại, dạng Mega) vào hashtable `Ab_HT` theo loại unit: key 61 = Def, 62 = SpD. Nguồn: `tools/learnsets.json` (293/294 loài), Leafeon điền tay, Mega theo bảng tay. Quái hoang và huyền thoại lấy theo loài của chúng. | `tools/v34/stats_def.py` (mới), `apply.py` | Số loại unit có dữ liệu = tổng số loại; in danh sách thiếu (phải rỗng) |
| 2 | **Loại của 90 skill elite / gym:** gán Vật lý / Đặc biệt theo tên chiêu (67 tự động, 11 gán tay: Silver Wind = Đặc biệt, Karate Chop = Vật lý…; 12 chiêu trạng thái không gây sát thương). `Ab_HT` trên skill key 59 = 1 Vật lý, 2 Đặc biệt. | `apply.py` | Không còn skill gây sát thương nào chưa có loại |
| 3 | **Tính sát thương chiêu:** trong `Ab_OnDamaging`, hệ số chỉ số = STR / 50 (move Vật lý) hoặc INT / 50 (move Đặc biệt) thay cho "chỉ số lớn hơn / 50"; nhân thêm hệ số thủ của mục tiêu (key 61 / 62, công thức mục 3). Loại của move lấy từ lúc dùng chiêu: learned move dùng `Mv_Phys` (đã có), skill elite / gym dùng key 59. | `jass/ab_tick.j`, `jass/types.j` | pjass 0 lỗi |
| 4 | **Mega và Zen:** lúc đang Mega dùng Def / SpD của dạng Mega; Darmanitan ở Zen Mode dùng Def / SpD của dạng Zen. | `jass/types.j` (hàm lấy chỉ số thủ, giống `Ty_Of`) | pjass |
| 5 | **Item:** Choice Band +35% đòn đánh và move Vật lý; Choice Specs +35% move Đặc biệt; Assault Vest -25% chỉ với move Đặc biệt. Item cộng STR / INT tự đổi ý nghĩa theo bước 3. | `jass/extra.j`, `extras.py` (mô tả) | pjass, mô tả item |
| 6 | **Tooltip move:** số sát thương trong tooltip tính theo STR hoặc INT đúng loại move, kèm dòng "Vật lý – tính theo STR, mục tiêu giảm theo Def" / "Đặc biệt – tính theo INT, giảm theo SpD". | `Mv_Tips` / `Mv_Tip` (bản vá trong `apply.py`) | Đọc lại chuỗi tooltip trong script |
| 7 | **Tự học move khi lên cấp:** khi so độ mạnh move để thay, nhân Power với (STR hoặc INT của Pokémon) / chỉ số chính, để Pokémon thiên phép ưu tiên move Đặc biệt và ngược lại. | `jass/moves.j` | pjass |
| 8 | **Lệnh `-stats`** (hoặc mở rộng lệnh có sẵn): in STR, INT, Def, SpD và hệ số nhận chiêu Vật lý / Phép của Pokémon mình. | `jass/extra_late.j`, `apply.py` | pjass |
| 9 | (Chỉ khi chọn 1b / 2b) đổi đòn đánh thường theo STR / đổi giáp thành Def / 2 trong `Hero_HPSync` và chỉ số gym / quái. | bản vá `apply.py` | pjass |
| 10 | **Tài liệu:** bảng `5-sat-thuong-chieu.md` thêm cột "tính theo STR / INT"; ghi công thức mới vào `README.md` và `HANDOFF-v3.4.md`; tăng `version.txt` lên 3.4.3. | `analysis/move_damage_doc.py`, docs | Đọc lại |
| 11 | **Kiểm tra trước khi đưa bạn:** `apply.py` → `check.py` (pjass 0 lỗi) → `build_v34.py --dry-run`; script in bảng ví dụ (một vài cặp Pokémon đánh nhau: sát thương trước / sau) để bạn xem độ cân bằng. | `analysis/` | Bảng ví dụ hợp lý |
| 12 | **Build 3.4.3 khi bạn bảo**, rồi bạn chơi thử theo danh sách dưới. | | |

## Bạn chơi thử những gì
- Pokémon thiên phép (Alakazam, Gengar) dùng move Đặc biệt đánh Steelix / Golem phải đau; dùng move Vật lý thì yếu.
- Blissey / Snorlax chịu phép tốt nhưng ăn đòn vật lý đau.
- Gym và Elite Four không quá dễ hoặc quá khó so với 3.4.2 (cân bằng chung nên giữ gần như cũ).
- Tooltip move ghi đúng "Vật lý / Đặc biệt" và số sát thương hợp lý; `-stats` hiện đúng.

## Rủi ro
- **Pokémon thiên một bên mà phần lớn move lại thuộc bên kia** sẽ yếu đi. Bước 7 giúp nó tự chọn move hợp hơn khi lên cấp;
  nếu vẫn yếu có thể chỉnh giới hạn hệ số.
- **Move dạng DoT** (cháy, độc theo giây) cũng chịu hệ số thủ, nên trâu thật sự sẽ chịu lâu hơn.
- **Bảng Def / SpD của Mega** gõ tay: mình sẽ ghi nguồn từng dòng để bạn soát.
