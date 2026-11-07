# HANDOFF v3.4 — bàn giao cho phiên / tài khoản Claude khác

Cập nhật 2026-11-08, sau khi build **v3.4.2**. Đọc file này cùng `CLAUDE.md` (tự nạp khi mở thư mục này) và
`docs/v3.4/README.md` (tổng hợp tính năng). File `HANDOFF.md` cũ chỉ đúng tới v3.1, nên bỏ qua.

## 1. Người dùng và cách làm việc (bắt buộc)
- **Trả lời bằng tiếng Việt.** Người dùng chơi Warcraft III Reforged 1.36.1 (bản offline repack ở `D:\Warcraft III Reforged`).
- **Không build map mới khi người dùng chưa bảo** (nguyên văn: "Khoan build bản mới khi tôi chưa bảo"). Sửa code, chạy pjass,
  build thử bằng `--dry-run` thì được; ghi file `.w3x` thì phải đợi người dùng nói "build".
- **Mỗi bản mới một số phiên bản mới** (`tools/v34/version.txt`). **Không bao giờ ghi đè hay xóa map cũ** (`build_v34.py`
  tự từ chối ghi đè).
- **Người dùng tự chơi thử.** Claude không chạy được game: mở bằng `-loadfile` thì dừng ở màn lỗi đăng nhập của bản repack.
  Bug do người dùng báo lại sau khi chơi.
- **Thay đổi lớn** (tính năng mới, cân bằng nhiều thứ): viết đề xuất dạng bảng / danh sách (file md) để người dùng duyệt
  ("Duyệt, sửa code") rồi mới làm. Lỗi rõ ràng thì sửa luôn.
- **Git:** chỉ commit / push khi người dùng bảo. Remote: `origin` = github.com/quoccuong5435/Pokemon (nhánh `main`).

## 2. Map và bản đã build (thư mục `Maps\Download`, cha của thư mục này)
| File | Ghi chú |
|---|---|
| `Pokemon Arena v1.8.w3x` | map gốc của tác giả Dinh Hai Ha, **không bao giờ sửa** |
| `Pokemon Arena v3.3.3.w3x` | **gốc của mọi bản v3.4.x**: mã nguồn 3.2.16–3.3.3 đã mất, nên build từ chính map này |
| `PKLegendsv3.2.w3x` | nguồn model / icon / hiệu ứng (Mega, form, khoảng 80 model hiệu ứng) |
| `Pokemon Arena v3.4.0.w3x` | 07/11: toàn bộ tính năng v3.4 (xem `docs/v3.4/README.md`) |
| `Pokemon Arena v3.4.1.w3x` | 08/11: sửa tiến hóa giữa trận làm reset gym, phím Q ra chiêu E/W, Amulet Coin |
| `Pokemon Arena v3.4.2.w3x` | 08/11, **bản mới nhất, chưa chơi thử** |

Bản 3.4.2 gồm:
- gym 1–4 dễ hơn; sửa gym kẹt 3/6; lệnh `-gym`;
- Elite Four chuyển vào phòng cũ của Darkrai (nền mới, cổng vào / ra, tượng); Darkrai thành huyền thoại ngẫu nhiên;
- Battle Shop / Item Shop đặt cố định; item hệ đủ 18 hệ; Onix / Scyther mua được Metal Coat.

**Bản tiếp theo phải là 3.4.3**: sửa `tools/v34/version.txt` trước khi build.

## 3. Cách build (chạy trong `_PokemonArena2.0_work`, Python 3 + pytest, luôn dùng `python -I`)
1. Sau khi clone mới thì chạy `python -I tools/v34/extract_base.py` một lần. Lệnh này tạo `v34/war3map_v333.j` từ map v3.3.3;
   file `v34/*.j` không có trên git vì chứa code của tác giả v1.8.
2. `python -I tools/v34/apply.py` tạo `v34/war3map.j` và bảng `docs/v3.4/4-icon-chieu.md`.
3. `python -I tools/v34/check.py` chạy pjass, **phải báo 0 lỗi**.
4. `python -I tools/v34/build_v34.py --dry-run` chạy mọi bước trừ ghi file.
5. `python -I tools/v34/build_v34.py` ghi `..\Pokemon Arena v<version>.w3x`, **chỉ khi người dùng bảo**.
6. Kiểm tra map vừa build: `python -I analysis/pjass_map.py "../Pokemon Arena v<version>.w3x"`.

## 4. Cấu trúc code v3.4 (`tools/v34/`)
| File | Vai trò |
|---|---|
| `apply.py` | ghép script: v3.3.3 + các file `jass/*.j` + dữ liệu sinh ra; các bản vá chuỗi (`*_OLD` / `*_NEW`), nối vào `Mega_Init` |
| `content.py` | 8 Mega (hM0P–hM0W, đá IM0P–IM0W, ability AM0P–AM0W), Meganium / Porygon2 / Latias & Latios (PV0A–PV2A), Latias huyền thoại nL18 + Soul ISL9, skin Zen hZ00, 211 quái hoang nX00–nX5U + Soul IU00–IU5U; dữ liệu JASS `V34_Data1..n` (chạy qua `ExecuteFunc`) |
| `extras.py` | 21 item (IB00–IB0B, IT00–IT08, ability AXR0), Battle Shop nBS0 / Item Shop nIS0, đá tiến hóa, quái tiến hóa theo tier, elite Mega, Elite Four, item hệ khác hệ (Metal Coat), item hệ 18 hệ, phòng League, Darkrai nL19, độ khó gym |
| `abilities.py` | 73 Ability (tên, mô tả); Pokémon nào có Ability nào |
| `mega_look.py` | 5 Mega không có model riêng; nhập model từ `mega_models/<Key>.mdx` nếu có |
| `move_icons.py` | icon cho 319 move theo tên (chỉ dùng icon có sẵn trong `analysis/builtin_icons.txt`) |
| `league_area.py` | phòng League: vị trí, sơn lại nền (`war3map.w3e`, chỉ đổi texture), tượng |
| `build_v34.py` | ghi map: script, w3i, w3u, ItemData / ItemFunc, AbilityData / Strings, w3e, file nhập từ PKL |
| `jass/globals.j` | biến toàn cục mới |
| `jass/types.j` | bảng khắc hệ, hệ của move |
| `jass/ai.j` | AI dùng skill cho elite / gym / huyền thoại |
| `jass/extra.j` | item, Shiny, thời tiết, huyền thoại Mega |
| `jass/gym.j` | gym + Elite Four / League |
| `jass/ab_*.j` | Ability |
| `jass/moves.j` | một move cho mỗi loại skill gốc |
| `jass/wild.j` | chọn loài quái theo bậc |

Script phân tích hữu ích nằm trong `analysis/`:
- `move_damage_doc.py`: bảng sát thương 319 move;
- `effects_plan.py`: đề xuất hiệu ứng;
- `base_layout.py`: vẽ căn cứ từ `war3map.wpm`;
- `area_render.py`, `room_flood.py`: xem một khu của map, kiểm tra phòng kín;
- `verify_v34_content.py`, `check_items_342.py`: kiểm tra dữ liệu trước khi build;
- `gym_replace_check.py`, `item_evos.py`: tìm lỗi tiến hóa.

Các file `analysis/patch_*.py` là script sửa một lần, đã chạy rồi; **đừng chạy lại**.

## 5. Bẫy kỹ thuật đã gặp
- **Heredoc bash** đổi `\\` thành `\` (kể cả khi dùng `'EOF'`). Code có dấu `\` (đường dẫn model trong JASS) phải viết bằng
  công cụ Write, không viết qua heredoc.
- **Tên biến local ngắn trong JASS** (`sc`, `s0`, `a1`, `s2`, `p1`…) trùng tên hàm 2–3 ký tự của v1.8, khiến pjass báo
  "already defined as function". Phải dùng tên dài.
- **Giới hạn số lệnh của một luồng JASS:** dữ liệu lớn và việc nặng phải chạy qua `ExecuteFunc` (luồng riêng). Gym dựng đội
  và gọi từng con qua `Gym_StartIt` / `Gym_SpawnIt` / `Gym_AdvanceIt`.
- **Nhiều `TriggerAddCondition` trên một trigger:** điều kiện trả `false` làm các điều kiện sau không chạy. Mỗi handler dùng
  trigger riêng (lỗi Amulet Coin ở 3.4.0 là do việc này).
- **Hai ability cùng skill gốc trên một unit** có chung lệnh, nên nút sau ra chiêu của nút trước. Vì vậy mỗi Pokémon chỉ giữ
  một move cho mỗi loại (`Mv_Kind`).
- **Mọi thay unit** (tiến hóa, Soul, v1.8) đều đi qua `Mega_SafeReplace`: nó chép move, Shiny, chuyển người thách đấu gym
  sang unit mới, và không bao giờ thay Pokémon gym (Mega_HT key 33).
- **Pokémon gym / League là hero** của Neutral Aggressive (dùng chính unit chơi được).
- **Bảng hash của MPQ là 4096 ô**, hiện dùng 2623; `build_v34` dừng nếu vượt 90%. Bắt buộc dùng block dạng sector.
- **Chỉ số trong code:** Soul quái rơi 20% (chỉ elite); elite máu và sát thương x1,6; skill x(chỉ số chính / 50), tối đa x15;
  bảng hệ số sát thương của map cho skill gây 100% lên mọi loại giáp.
- **Key hashtable:** `Ab_HT` trên unit dùng 0–12, 51–98, 120–130, 140+k (item); `Mega_HT` trên loại unit dùng 7, 8, 30, 39,
  41, 45, 47, 48, 80–86, 90–92. Mô tả chi tiết nằm ở đầu các file JASS.

## 6. Việc đang mở
1. **Chơi thử 3.4.2** rồi sửa lỗi người dùng báo. Nếu gym kẹt, nhờ người dùng gõ `-gym` và gửi lại kết quả.
2. **Đề xuất hiệu ứng chiêu** `docs/v3.4/6-de-xuat-hieu-ung-chieu.md`: **chờ duyệt**.
   - 106 move cận chiến bỏ đạn bay, tầm 150, hiệu ứng chém / đấm của PKL;
   - 81 move có đạn theo hệ, 66 move diện rộng, 10 move có hiệu ứng riêng;
   - dùng 35 model của PKLegends 3.2, khoảng 1,5 MB.
3. **Ý tưởng chưa làm** (người dùng chưa chọn): nhiệm vụ / truy nã; bảng điểm (multiboard); Nature; Raid Boss; Save/Load code
   + Pokédex; trứng Pokémon; câu cá; Team Rocket; Pokémon đồng hành.
4. **Git:** `main` đang ở commit `9184ca7` (code v3.4.0). Mọi thay đổi của 3.4.1, 3.4.2 và thư mục `docs/v3.4/` **chưa commit**.
   Các file sửa dở từ trước (`tools/jass/mega.j`, `tools/jasscheck.py`, `analysis/make_patchnote.py`, trang patch note,
   `analysis/edit_wish.py`) không thuộc v3.4: không commit nếu không được hỏi.
5. **Tải map lên Google Drive:** cần extension Claude in Chrome đã kết nối; mỗi lần tải file lên tối đa 10 MB, nên phải cắt map
   thành nhiều phần rồi ghép lại trong trang Drive. `out/drive_parts/` hiện chứa các phần của **v3.4.0, đã cũ**; làm lại với map
   mới nhất.
6. **Model Mega:** Beedrill, Kangaskhan, Mewtwo X / Y, Rayquaza chưa có model Mega riêng. Đặt file vào
   `mega_models/MegaBeedrill.mdx` (cùng tên cho các con kia) thì build sẽ tự nhập.
7. **Chưa kiểm tra được trong game:**
   - mã hiệu ứng thời tiết ('RAhr', 'LRaa', 'WOcw', 'SNbs');
   - cổng và tượng của League;
   - hình Mega của elite / huyền thoại;
   - độ khó gym sau khi giảm.
