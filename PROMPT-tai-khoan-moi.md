# Prompt dán vào phiên Claude Code mới (tài khoản khác)

Mở Claude Code trong thư mục:

`C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\_PokemonArena2.0_work`

Nếu dùng máy khác: clone https://github.com/quoccuong5435/Pokemon vào đúng chỗ `Maps\Download\_PokemonArena2.0_work`.
Code mới nhất (3.4.2) nằm ở nhánh `v3.4.2`, hoặc ở `main` nếu đã gộp. Rồi chạy `python -I tools/v34/extract_base.py`.
Các map `.w3x` không có trên git: phải chép thư mục `Maps\Download` sang (ít nhất `Pokemon Arena v3.3.3.w3x`,
`PKLegendsv3.2.w3x`, `Pokemon Arena v1.8.w3x` và các bản v3.4.x).

Rồi dán đoạn dưới đây làm tin nhắn đầu tiên:

---

Bạn đang tiếp tục dự án mod map Warcraft III Reforged "Pokemon Arena" của tôi. Thư mục làm việc là
`_PokemonArena2.0_work` (bên trong `Documents\Warcraft III\Maps\Download`).

Trước khi làm gì, hãy đọc kỹ 3 file sau, theo thứ tự:
1. `CLAUDE.md`
2. `HANDOFF-v3.4.md`: trạng thái hiện tại, quy tắc, bẫy kỹ thuật, việc đang mở
3. `docs/v3.4/README.md`: tổng hợp tính năng của v3.4.x

Quy tắc bắt buộc:
- Luôn trả lời tôi bằng tiếng Việt.
- **Không build map mới khi tôi chưa bảo "build".** Được sửa code, chạy pjass (`python -I tools/v34/check.py`) và build thử
  (`python -I tools/v34/build_v34.py --dry-run`).
- Mỗi bản mới phải tăng số phiên bản trong `tools/v34/version.txt` (bản tiếp theo là **3.4.3**). Không bao giờ ghi đè hay xóa
  map cũ.
- Tôi tự chơi thử trong game rồi báo lỗi. Bạn không chạy được game.
- Tính năng mới hoặc thay đổi lớn: viết đề xuất (bảng / danh sách trong file md) để tôi duyệt trước, tôi trả lời
  "Duyệt, sửa code" thì mới làm. Lỗi rõ ràng thì sửa luôn.
- Chỉ commit hoặc push git khi tôi bảo.
- Code có dấu `\` thì viết bằng công cụ Write (heredoc bash làm mất dấu `\`). Biến local trong JASS phải đặt tên dài, vì tên
  ngắn trùng tên hàm của v1.8.

Bản mới nhất là `Pokemon Arena v3.4.2.w3x` (chưa chơi thử). Việc đang mở xem ở mục 6 của `HANDOFF-v3.4.md`.

Đọc xong thì tóm tắt ngắn cho tôi bạn hiểu dự án đang ở đâu và các việc đang mở, rồi chờ tôi giao việc.

---
