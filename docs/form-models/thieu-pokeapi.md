# Dạng không có mục riêng trên PokeAPI (2026-11-23)

Kết quả `python -X utf8 -I tools/pokeapi/fetch_forms.py`: 347 bản ghi, 105 khóa form + 44 Mega cũ + 205 con Gen 1-4. Cả 19 Mega Z-A và 28 Mega mới
đều có trên PokeAPI. Chỉ 5 khóa không có mục `/pokemon` riêng.

| Khóa | Là gì | Cách xử lý hiện tại |
|---|---|---|
| `cherrim-sunshine` | dạng đổi theo thời tiết của Cherrim | dùng dữ liệu `cherrim` (Grass, Flower Gift) |
| `shellos-east` | dạng biển Đông của Shellos | dùng dữ liệu `shellos` |
| `gastrodon-east` | dạng biển Đông của Gastrodon | dùng dữ liệu `gastrodon` |
| `pichu-spiky-eared` | Pichu tai nhọn | dùng dữ liệu `pichu` |
| `mega:36` (Mega_Name "Dark Lugia") | không phải dạng chính thức | chưa có dữ liệu; hero này giữ ability hiện có |

Lý do 4 dạng đầu dùng dữ liệu loài gốc: đây là dạng chỉ khác hình thức, hệ và ability chính thức giống hệt loài gốc. Quyết định này ghi trong
sổ `.superpowers/sdd/2026-11-23-npa10-ability-hidden-power/progress.md`. Muốn đổi thì sửa `ALIASES` trong `tools/pokeapi/fetch_forms.py` và chạy lại.
