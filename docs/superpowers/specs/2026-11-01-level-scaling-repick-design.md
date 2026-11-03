# Pokemon Arena v2.4 — quái theo level trung bình, repick (design)

Ngày: 2026-11-01 · Yêu cầu: "tăng level quái ngoài map thành trung bình level … cho repick 2 lần mỗi người chơi",
"repick trong 2 p đầu game thôi". Hai lựa chọn chưa được trả lời → theo phương án đề xuất (ghi trong ledger).

## Quái hoang dã theo level trung bình

- Mỗi 30 giây (trong `Wild_Tick`): `avg` = level trung bình của các hero thuộc người chơi 0–11 (bỏ Wisp chọn tướng).
  Không có hero nào → giữ nguyên.
- Bậc `Wild_Tier = min(10, avg / 10)` (chia nguyên). Bỏ hẳn lên bậc theo thời gian (`Wild_TierSeconds`, `Wild_NextTier`).
  Bậc tăng → thông báo "Wild Pokemon grew stronger! (Tier N)"; bậc giảm (người chơi rời) → áp lại im lặng.
- Hệ số chỉ số giữ nguyên (+15% máu/sát thương/vàng, +2 giáp mỗi bậc), bãi hồi chọn loài theo sức bãi + bậc.
- Level hiển thị của quái = max(level gốc, avg) qua `BlzSetUnitIntegerField(u, UNIT_IF_LEVEL, …)`; level gốc lưu ở khóa 26,
  level đã áp ở khóa 27 (áp lại khi khác).

## Repick

- Lệnh chat `-repick` (người chơi 0–11). Được phép khi: `Mega_Time < 120` giây, số lần đã repick < 2, người chơi có hero
  còn sống và không ở dạng Mega.
- Khi repick: lưu XP (`GetHeroXP`) và 6 item (bỏ khỏi hero, ẩn đi, giữ trong hashtable theo người chơi), xóa hero, tạo Wisp
  `earc` ở điểm xuất phát (−128, 4544), chọn Wisp, thông báo "<tên> repicked (n/2)".
- Khi người chơi có Pokemon mới (mua ở tavern — sự kiện bán unit — hoặc `-random`): trả XP (`SetHeroXP`, kích hoạt tiến hóa
  như bình thường) và trả item (hiện lại, `UnitAddItem`).
- Lời nhắc đầu game thêm `-repick`.

## Phiên bản

`tools/version.txt` = `2.4`, file `Pokemon Arena v2.4.w3x`.

## Kiểm tra

Test Python: module qua `jasscheck`; hằng số 30 giây / 120 giây / 2 lần; không còn mốc thời gian lên bậc; repick lưu và trả
XP/item ở cả hai đường (tavern, random). Bạn test trong game: repick trong 2 phút (lần 3 bị từ chối, sau 2 phút bị từ chối),
quái lên bậc khi level trung bình qua mốc 10/20/30.
