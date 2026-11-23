"""Tests for Pokemon Arena v4.1.2-ver2d.w3x:
- Map existence and basic properties (192x192, layout, weather, starters, debuffs)
- Vietnamese localization:
  * Welcome banner in Vietnamese
  * -help command displays all commands in clear Vietnamese
  * -me stats breakdown in Vietnamese
  * Late-game training (-up) dialog in Vietnamese
  * Mythic Forge (-forge) dialog and notifications in Vietnamese
  * Solo deathmatch (-solo) announcements in Vietnamese
  * Chaos Mode event broadcasts in Vietnamese
  * Altar, Wanted, Treasure, Magikarp, Red Gyarados, and Rune announcements in Vietnamese
  * Awakening quest (-quest) stage messages in Vietnamese
  * Gym and League defeat/champion messages in Vietnamese
  * Duel notifications in Vietnamese
  * Battle items & Loot tooltips in ItemFunc.txt in Vietnamese
"""
import os
import struct
import mpq
import slk
import objdata

MAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Pokemon Arena v4.1.2-ver2d.w3x')


def test_map_exists():
    assert os.path.exists(MAP_PATH), 'Pokemon Arena v4.1.2-ver2d.w3x must exist'


def test_vietnamese_script_localization():
    arc = mpq.MPQ(MAP_PATH)
    j = arc.read('scripts\\war3map.j').decode('utf-8')

    # 1. Welcome banner
    assert 'POKEMON ARENA v4.1.2-ver2d|r  |cff94a3b8- PvP & Cân Bằng Huyền Thoại|r' in j
    assert 'Tất Cả Lệnh' in j
    assert 'Luyện Tập' in j
    assert 'Cửa Hàng Căn Cứ' in j

    # 2. -help command
    assert 'BẢNG HƯỚNG DẪN LỆNH POKEMON ARENA' in j
    assert 'Chọn / đổi Pokémon ngẫu nhiên (2 phút đầu, tối đa 2 lần)' in j
    assert 'Menu học / đổi 4 chiêu Q-W-E-R' in j
    assert 'Tiệm Rèn đập đồ +1..+5 [MYTHIC]' in j
    assert 'Xem trạng thái & đội hình 8 Gym' in j
    assert 'Xem chi tiết chỉ số ẩn (Relic, Bùa Charm, Hút máu, Chí mạng, Tiền thưởng, Cổ ngữ)' in j
    assert 'Biến về căn cứ sau 5s (CD 30s, chặn khi đang mang Legend Soul)' in j
    assert 'Thách đấu Sinh Tử 1v1 cướp 1 món trang bị' in j
    assert 'Đấu giao hữu 1v1 tính điểm xếp hạng' in j
    assert 'Vòng quay may mắn (1.000 vàng/lượt)' in j
    assert 'Đổi / bật tắt Thú Cưng mini (+1% Mana/s)' in j

    # 3. -me Stats
    assert '|cff7dd3fc[CHỈ SỐ]|r |cffe8ecf2Hãy chọn một Pokémon trước.|r' in j
    assert '15.000 đầu nhận đủ, phần dư nhận 50%' in j
    assert 'Bùa Charm:|r Hút máu' in j
    assert 'Tiền thưởng mạng:' in j
    assert 'Chỉ số Loot:' in j

    # 4. -up / -train
    assert 'Luyện Tập Cuối Game & Tiệm Vàng (-up)' in j
    assert 'Tăng All Stats +10' in j
    assert '+500 Máu & +3 Giáp' in j
    assert 'Hòm Đồ Bí Ẩn (Hiếm/Sử Thi/Huyền Thoại) - 3500 vàng' in j
    assert 'Dược Phẩm Chiến Đấu' in j
    assert '|cffff5c5c[LUYỆN TẬP]|r Cần một Pokémon còn sống.' in j

    # 5. -forge
    assert 'TIỆM RÈN THẦN BÍ - Nâng cấp & Dung hợp Đồ Loot' in j
    assert 'Dung hợp 2 đồ thấp nhất -> Bậc kế (60/40/20%, 1500 vàng)' in j
    assert '|cffff5c5c[TIỆM RÈN]|r Cần một Pokémon còn sống.' in j
    assert 'RÈN THẦN THOẠI +5!' in j

    # 6. -solo
    assert 'THÁCH ĐẤU SOLO' in j
    assert 'SOLO SINH TỬ!' in j
    assert 'SOLO CHIẾN THẮNG!' in j
    assert 'Sợ quá chạy mất dép! =)))' in j

    # 7. Chaos Mode
    assert 'HỖN LOẠN: TỐC ĐỘ TỐI ĐA!' in j
    assert 'HỖN LOẠN: KHỔNG LỒ HÓA!' in j
    assert 'HỖN LOẠN: CƠN SỐT VÀNG!' in j
    assert 'Chế độ Hỗn Loạn kết thúc! Đấu trường trở lại bình thường.' in j

    # 8. Events
    assert 'SỰ KIỆN ALTAR' in j
    assert 'LỆNH TRUY NÃ!' in j
    assert 'TIỀN THƯỞNG TRUY NÃ!' in j
    assert 'KHO BÁU HOÀNG KIM' in j
    assert 'MAGIKARP KHỔNG LỒ' in j
    assert 'DÍNH BẪY RỒI!' in j
    assert 'GYARADOS ĐỎ BỊ HẠ!' in j
    assert 'Cổ Ngữ Tốc Độ' in j
    assert 'Cổ Ngữ Cuồng Nộ' in j
    assert 'Cổ Ngữ Hồi Phục' in j
    assert 'Cổ Ngữ Tài Phú' in j

    # 9. Awakening Quest & Gym & League & Duels
    assert 'BƯỚC 1 HOÀN TẤT' in j
    assert 'BƯỚC 2 HOÀN TẤT' in j
    assert 'THỨC TỈNH HOÀN TẤT' in j
    assert 'QUÁN QUÂN LEAGUE' in j
    assert 'GIAO HỮU CHIẾN THẮNG' in j
    assert 'TIẾP TẾ LẬT KÈO' in j
    assert 'ĐIỂM TRẬN ĐẤU!' in j
    assert 'CHIẾN CÔNG ĐẦU!' in j
    assert 'CHẤM DỨT CHUỖI!' in j
    assert 'MŨ CỦA ASH' in j
    assert 'Cổ Vật Chỉ Số' in j
    assert 'Bùa Hiệu Ứng' in j


def test_vietnamese_itemfunc_tooltips():
    arc = mpq.MPQ(MAP_PATH)
    func = arc.read('Units\\ItemFunc.txt').decode('utf-8')

    assert 'Đồ Loot Thường' in func
    assert 'Đồ Loot Hiếm' in func
    assert 'Đồ Loot Sử Thi' in func
    assert 'Đồ Loot Huyền Thoại' in func

    # Choice Band
    assert 'Tăng +35% sát thương đòn đánh. Giảm -10% tốc độ di chuyển.' in func
    # Leftovers
    assert 'Hồi phục 1% Máu tối đa mỗi giây.' in func
    # Focus Sash
    assert 'Đòn đánh kết liễu khi Máu trên 50% sẽ giữ lại 1 Máu (Hồi chiêu 60 giây một lần).' in func


def test_map_dimensions_192():
    arc = mpq.MPQ(MAP_PATH)

    w3e = arc.read('war3map.w3e')
    p = 4 + 4 + 1 + 4
    n_g = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_g * 4
    n_c = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_c * 4
    mx, my, ox, oy = struct.unpack_from('<IIff', w3e, p)
    assert mx == 193 and my == 193
    assert ox == -12288.0 and oy == -12288.0

    wpm = arc.read('war3map.wpm')
    magic, ver, w, h = struct.unpack_from('<4sIII', wpm, 0)
    assert magic == b'MP3W' and w == 768 and h == 768

    shd = arc.read('war3map.shd')
    assert len(shd) == 768 * 768

    w3i = arc.read('war3map.w3i')
    found_192 = False
    for i in range(len(w3i) - 8):
        w, h = struct.unpack_from('<ii', w3i, i)
        if w == 192 and h == 192:
            found_192 = True
            break
    assert found_192


def test_33_starters_and_debuffs_intact():
    arc = mpq.MPQ(MAP_PATH)
    w3u = objdata.ObjFile(arc.read('war3map.w3u'))
    items = slk.Slk(arc.read('Units\\ItemData.slk').decode('latin-1'))
    custom_units = {o.new: o for o in w3u.custom}

    # 33 Hero units
    dig = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for k in range(33):
        hid = 'EP' + dig[k // 36] + dig[k % 36]
        wid = 'nZ' + dig[k // 36] + dig[k % 36]
        sid = 'IZ' + dig[k // 36] + dig[k % 36]
        assert hid in custom_units
        assert wid in custom_units
        assert items.find(sid) is not None

    # Assets
    assert arc.has('PkFx\\Starter\\158.mdx'), 'Totodile model missing'
    assert arc.has('PkFx\\Starter\\658.mdx'), 'Greninja model missing'
    assert arc.has('ReplaceableTextures\\CommandButtons\\BTN_158.blp'), 'Totodile icon missing'

    # Transform & StatSync
    j = arc.read('scripts\\war3map.j').decode('utf-8')
    assert 'act == 29' in j
    assert 'BlzSetUnitSkin(u, GetUnitTypeId(tgt))' in j
    assert 'function Fx_StatSync takes unit u returns nothing' in j
