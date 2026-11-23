# Pokemon Arena v4.1.4

**Đã build 2026-11-21** (`Pokemon Arena v4.1.4.w3x`, = v4.1.3 + một sửa, pjass 0 lỗi). **Chưa chơi thử.** Code: `tools/v412/loot_hp.py`, test `tests/test_loot_hp.py`.

**Max HP từ loot: cap mềm thay cho cap cứng.** Trước đó `PAX_TestItem_SyncEx` cắt **tổng** Max HP của mọi item loot ở +15.000
(`if newHP > 15000 then set newHP = 15000`), nên hero 10.000 máu + đồ 23.000 chỉ ra 25.000 và item thứ hai bị phí mà không báo gì.
Nay 15.000 đầu tính đủ, phần vượt tính một nửa: đồ 23.000 → tính 19.000, hero ra **29.000**. Dưới 15.000 không đổi.
- Tổng gốc lưu ở `PAX_Item_HT` khóa 130 của hero. Khi tổng vượt 15.000, mỗi lần số HP tính được đổi, người chơi nhận
  "[LOOT] Max HP from loot: +X, counted +Y (the first 15,000 count in full, the rest half)".
- `-me` ghi "+Y HP (of X: the first 15,000 in full, the rest half)", và ghi trần của Lifesteal (max 25%) và Crit (max 60%) cạnh số hiện có.
- Lifesteal 25% và Crit 60% vẫn là trần cứng như cũ (chỉ thêm chữ báo).
- Build: `python -I tools/v412/build.py` (version ở `tools/v412/version.txt`, gồm cả bản sửa cân bằng bãi quái của v4.1.3).

---

# Pokemon Arena v4.1.3

**Đã build 2026-11-21** (`Pokemon Arena v4.1.3.w3x`, từ map `Pokemon Arena v4.1.2.w3x`, pjass 0 lỗi, 209 test pass). **Chưa chơi thử.**
Mã nguồn v4.1.2 không có trên máy (dòng PAX, chỉ có map), nên `tools/v412/build.py` đọc thẳng map, vá script và `war3map.w3i` rồi ghi map mới;
mọi file khác giữ nguyên từng byte (đã so từng file). Không ghi đè map có sẵn. Số bản nằm ở `tools/v412/version.txt`.

## Thay đổi: loot cân bằng giữa các bãi quái
- Trước: tỉ lệ rơi item loot cố định theo loại quái (elite 15%, quái thường 5%), mà mỗi bãi có đúng 1 elite, nên một lần dọn bãi 2 con kỳ vọng
  0,20 món, bãi 12 con kỳ vọng 0,70 món. Có 55 bãi: 14 bãi 2 con, 20 bãi 4 con, 19 bãi 6 con, 1 bãi 8 con, 1 bãi 12 con. Nửa trái 26 bãi / 116 con, nửa phải 29 bãi / 126 con.
- Nay: tỉ lệ rơi của quái trong bãi nhân với `32 / (15 + 5 x (số con - 1))` (`PAX_Loot_CampFactor`), nên **mọi bãi kỳ vọng 0,32 món mỗi lần dọn**
  (0,32 là trung bình của 55 bãi, tổng loot toàn map giữ gần như cũ). Bãi 2 con: elite 24%, thường 8%; bãi 4 con: 16% / 5,3%; bãi 6 con: 12% / 4%; bãi 12 con: 7% / 2,3%.
- Không đổi: huyền thoại và boss cố định (`PAX_IsFixedBoss`), quái không thuộc bãi nào, hạng item khi rơi, các nguồn loot khác.

## Code
`tools/v412/loot_balance.py` (`patch_script`, `bump_version`), `tools/v412/build.py`, test `tests/test_loot_balance.py`
(fixture `tests/fixtures/loot_4112_sample.j`, chép từ script v4.1.2 với CRLF).
Build lại: `python -I tools/v412/build.py` (cần `..\Pokemon Arena v4.1.2.w3x`).

## Cần chơi thử
Dọn bãi 2 con và bãi 6 con nhiều lần xem số món rơi có gần nhau không; boss huyền thoại vẫn rơi như cũ.
