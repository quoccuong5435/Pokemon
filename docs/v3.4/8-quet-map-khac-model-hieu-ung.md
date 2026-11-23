# 8. Quét các map khác trong thư mục: model hiệu ứng cho move cận chiến

Trạng thái: **chỉ đọc, chưa dùng model nào, chưa sửa code.** Bổ sung cho đề xuất 6 (`6-de-xuat-hieu-ung-chieu.md`).

Dữ liệu: `analysis/map_scan_models.json` (danh sách file trong 45 map `.w3x` của thư mục `Maps\Download`).

## 1. Các map có nhiều model hiệu ứng

| Map | File | Model `.mdx` | Ghi chú |
|---|---|---|---|
| Anime Battle Stadium Rinne | 5715 | 1310 | nhiều chém, đấm, nổ, sóng nhất |
| Anime Battle Stadium 3.4d | 766 | 306 | |
| Fight Of Anime 3.0c | 945 | 351 | chém, nổ, sóng |
| Pokemon Arena God Mode | 2458 | 700 | chứa cả model PKL và model chém / sóng |
| PKLegends v3.2 | 1956 | 558 | đã dùng trong đề xuất 6 |
| DRT-V3-ENG | 1198 | 248 | chủ yếu model nhân vật |
| Boss Battle 1.12.0 | 2993 | 221 | nổ, bóng tối |
| Castle Fight Legend AI 8.3 | 248 | 139 | đạn, aura |
| [DN]Anime Hoi Hoi Kho 2014 | 238 | 99 | có Green Claw, FireSword |

Một số map không lấy được file (khóa hoặc rỗng): 79.PokemonRPG, DL_RFTD, DRDR311, FOCS3, New Anime Battle Royal, Song Tren Hoang Dao, U9_*, _NarutoRPGPlus1, và các map Battlestadium DON.

## 2. Model cận chiến (chém, đấm, va chạm) đáng xem

- **Anime Battle Stadium Rinne:** `6Slash`, `CrescentSlashREd`, `CrossSlash Red`, `Ephemeral Cut Red`, `ESlash5` / `ESlash5Red`, `E Punch1`, `EarthSmash`, `Effect_Shadow_Assault_Slash`, `Blade Skill04C–F`, `Blade Skill06E–J`, `AnginHitNew1` / `AnginHitNew3`, `AZ_Zeusking_Impact-hit`, `CYZ_Hit`.
- **Fight Of Anime 3.0c:** `SlashOne`, `ShadowSlash`, `MoonFireSlash`, `Dimension Slash`, `Dimension Slash2`, `Omnislash`, `CreeperStrike`, `EarthSmash`.
- **Pokemon Arena God Mode:** `Blade Light`, `BladeShockwave` (bản thường, bản fighting), `Chidori Slash`, `Kurama Slash`, `Susanoo Slash`, `Black Stomp`, `FireStomp`, `IceStompMist`, `ThunderStrike`, `White Boom`.
- **[DN]Anime Hoi Hoi Kho 2014:** `Green Claw`, `FireSword`, `DarkImpale`.
- **Boss Battle:** `Ghost Strike`, `Dark Execution`.

## 3. Đạn / hiệu ứng theo hệ đáng xem

- Lửa: `Flamestrike Mystic I`, `FireArrow`, `Firebolt Minor` (đã có trong PKL).
- Băng: `IceSpikedShield2`, `FrostNova`, `Frost Missile` (Random Farm TD).
- Điện: `LightningMilssile`, `LightningWrath`, `ThunderStrike`, `GreatElderHydraLightningOrbV.107`.
- Bóng tối: `DarkOrb`, `DarkImpale`, `DarkLightningNova`, `BlackDragonMissile`.
- Ánh sáng / đạn trắng: `White Holy`, `White Holy Ray`, `WhiteXMissile`, `WhiteShockwave`.

## 4. Lưu ý trước khi dùng

1. **Bản quyền và quyền sử dụng.** Các model này thuộc về tác giả map khác. Trước khi đưa vào map, phải hỏi bạn xem có chấp nhận dùng không. PKL v3.2 đã được dùng ở các bản trước, nên là nguồn an toàn hơn.
2. **Phụ thuộc texture.** Nhiều model dùng texture riêng của map gốc. Khi nhập, phải kiểm tra đủ texture (`.blp`) đi kèm; nếu thiếu, model sẽ hiện ô vuông trắng hoặc ô đen.
3. **Kích thước.** Map Anime Battle Stadium Rinne rất lớn. Chỉ nên lấy đúng những model đã chọn, không sao chép cả thư mục.
4. **Đề xuất tiếp theo:** nếu bạn đồng ý, mình sẽ lập bảng ghép move với model (giống bảng ở đề xuất 6) cho các move cận chiến, rồi kiểm tra dung lượng và texture trước khi nhập.
