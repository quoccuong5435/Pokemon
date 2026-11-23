"""v4.1.2 Vietnamese ACCENTED localization module for Pokemon Arena.
Localizes in-game announcements, event alerts, item/loot descriptions,
the -help / -quest / -me / -up / -forge command text, and move descriptions
into natural, beautiful Vietnamese Unicode WITH DIACRITICS (có dấu chuẩn),
while strictly preserving English Pokemon names, Move names, item proper names, and chat commands.
"""
import re


def _rep(s, old, new):
    if old not in s:
        raise ValueError("Missing anchor for Vietnamese localization:\n" + repr(old[:120]))
    return s.replace(old, new, 1)


def patch_script(s):
    # Normalize version banner from prior builds
    s = re.sub(r'v4\.1\.2-ver2[a-z]* - PvP & [^\n\r]+', 'v4.1.2-ver2g - PvP & Cân Bằng Huyền Thoại', s)
    s = s.replace('POKEMON ARENA v4.1.2-ver2 COMMANDS', 'POKEMON ARENA v4.1.2-ver2g COMMANDS')
    s = s.replace('POKEMON ARENA v4.1.2-ver2c COMMANDS', 'POKEMON ARENA v4.1.2-ver2g COMMANDS')
    s = s.replace('POKEMON ARENA v4.1.2-ver2f COMMANDS', 'POKEMON ARENA v4.1.2-ver2g COMMANDS')
    s = s.replace('BANG HUONG DAN LENH POKEMON ARENA', 'BẢNG HƯỚNG DẪN LỆNH POKEMON ARENA')

    # 1. Welcome Banner
    banner_pattern = r'call PAX_Announce\("\s*\|cffffd166POKEMON ARENA v4\.1\.2-ver2[a-z]*\|r[^\n\r]+", 10\.0\)\r?\n\s*call PAX_Announce\("\s*\|cff7dd3fc-help\|r[^\n\r]+", 10\.0\)\r?\n\s*call PAX_Announce\("\s*\|cffe8ecf2(?:Base Shops|Cua Hang Can Cu):[^\n\r]+", 10\.0\)'
    new_banner = (
        'call PAX_Announce("  |cffffd166POKEMON ARENA v4.1.2-ver2g|r  |cff94a3b8- PvP & Cân Bằng Huyền Thoại|r", 10.0)\n'
        '    call PAX_Announce("  |cff7dd3fc-help|r |cffe8ecf2Tất Cả Lệnh  |  |cff7dd3fc-up|r |cffe8ecf2Luyện Tập  |  |cff7dd3fc-quest|r |cffe8ecf2Thức Tỉnh  |  |cff7dd3fc-solo|r |cffe8ecf21v1 Cướp Đồ  |  |cff7dd3fc-pet|r |cffe8ecf2Thú Cưng|r", 10.0)\n'
        '    call PAX_Announce("  |cffe8ecf2Cửa Hàng Căn Cứ:|r |cffffd166Form Shop|r |cff64748b/|r |cffd896ffParadox Form Shop|r", 10.0)'
    )
    s, n = re.subn(banner_pattern, new_banner, s, count=1)
    if n == 0:
        # Fallback manual replacement
        s = s.replace(
            'POKEMON ARENA v4.1.2-ver2f|r  |cff94a3b8- PvP & Can Bang Huyen Thoai|r',
            'POKEMON ARENA v4.1.2-ver2g|r  |cff94a3b8- PvP & Cân Bằng Huyền Thoại|r'
        )
        s = s.replace(
            '-help|r |cffe8ecf2Tat Ca Lenh  |  -up|r |cffe8ecf2Luyen Tap  |  -quest|r |cffe8ecf2Thuc Tinh  |  -solo|r |cffe8ecf21v1 Cuop Do  |  -pet|r |cffe8ecf2Thu Cung|r',
            '-help|r |cffe8ecf2Tất Cả Lệnh  |  -up|r |cffe8ecf2Luyện Tập  |  -quest|r |cffe8ecf2Thức Tỉnh  |  -solo|r |cffe8ecf21v1 Cướp Đồ  |  -pet|r |cffe8ecf2Thú Cưng|r'
        )
        s = s.replace(
            'Cua Hang Can Cu:|r |cffffd166Form Shop|r |cff64748b/|r |cffd896ffParadox Form Shop|r',
            'Cửa Hàng Căn Cứ:|r |cffffd166Form Shop|r |cff64748b/|r |cffd896ffParadox Form Shop|r'
        )

    # 2. Comprehensive -help command display
    new_help = (
        'function PAX_Help_OnChat takes nothing returns nothing\n'
        '    local player trigPl = GetTriggerPlayer()\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=================== BẢNG HƯỚNG DẪN LỆNH POKEMON ARENA ===================|r")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pick|r / |cff7dd3fc-repick|r : Chọn / đổi Pokémon ngẫu nhiên (2 phút đầu, tối đa 2 lần)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-moves|r : Menu học / đổi 4 chiêu Q-W-E-R   |   |cff7dd3fc-quest|r : Tiến độ Thức Tỉnh Thần")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-up|r / |cff7dd3fc-train|r : Luyện tập chỉ số cuối game (All Stats, Máu, Giáp, Dược Phẩm)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-forge|r : Tiệm Rèn đập đồ +1..+5 [MYTHIC] / Dung hợp đồ (hoặc bấm vào Tượng)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gym|r : Xem trạng thái & đội hình 8 Gym   |   |cff7dd3fc-league|r : Khiêu chiến Champion Lance")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-me|r : Xem chi tiết chỉ số ẩn (Relic, Bùa Charm, Hút máu, Chí mạng, Tiền thưởng, Cổ ngữ)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-home|r / |cff7dd3fc-stuck|r : Biến về căn cứ sau 5s (CD 30s, chặn khi đang mang Legend Soul)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-tp|r : Dịch chuyển tức thời về căn cứ và hồi đầy Máu / Mana")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-solo [1..12]|r / |cff7dd3fc-yes|r / |cff7dd3fc-no|r : Thách đấu Sinh Tử 1v1 cướp 1 món trang bị")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-duel [1..12]|r / |cff7dd3fc-accept|r / |cff7dd3fc-rank|r : Đấu giao hữu 1v1 tính điểm xếp hạng")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gamble|r : Vòng quay may mắn (1.000 vàng/lượt)   |   |cff7dd3fc-ez|r / |cff7dd3fc-taunt|r : Khiêu khích")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pet|r : Đổi / bật tắt Thú Cưng mini (+1% Mana/s)   |   |cff7dd3fc-title|r : Đổi danh hiệu bay trên đầu")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cffffd166[HOST]|r |cff7dd3fc-random|r (random all) | |cff7dd3fc-fog|r (bật/tắt sương) | |cff7dd3fc-win <N>|r (đặt điểm thắng)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=============================================================================|r")\n'
        '    set trigPl = null\n'
        'endfunction'
    )
    help_pattern = r'function PAX_Help_OnChat takes nothing returns nothing[\s\S]*?endfunction'
    s = re.sub(help_pattern, new_help, s, count=1)

    # 3. -me Stats display
    s = s.replace('"Khong co"', '"Không có"')
    s = s.replace('|cff7dd3fc[CHI SO]|r |cffe8ecf2Hay chon mot Pokemon truoc.|r', '|cff7dd3fc[CHỈ SỐ]|r |cffe8ecf2Hãy chọn một Pokémon trước.|r')
    s = s.replace('|cff38bdf8Toc Do (', '|cff38bdf8Tốc Độ (')
    s = s.replace('|cffff5c5cCuong No (', '|cffff5c5cCuồng Nộ (')
    s = s.replace('|cff4ade80Hoi Phuc (', '|cff4ade80Hồi Phục (')
    s = s.replace('(Cap ', '(Cấp ')
    s = s.replace('Ha/Chet:', 'Hạ/Chết:')
    s = s.replace('Chuoi ha:', 'Chuỗi hạ:')
    s = s.replace('Tien thuong mang:', 'Tiền thưởng mạng:')
    s = s.replace('Huy hieu Gym:', 'Huy hiệu Gym:')
    s = s.replace('Chi so Loot:', 'Chỉ số Loot:')
    s = s.replace('Giap,', 'Giáp,')
    s = s.replace('Mau', 'Máu')
    s = s.replace('Bua Charm:', 'Bùa Charm:')
    s = s.replace('Hut mau ', 'Hút máu ')
    s = s.replace('Chi mang ', 'Chí mạng ')
    s = s.replace('Phan don ', 'Phản đòn ')
    s = s.replace('Co ngu:', 'Cổ ngữ:')

    # 4. -up / -train (Luyện tập cuối game)
    s = s.replace('Tang All Stats +10 (Toi da 15/15)', 'Tăng All Stats +10 (Tối đa 15/15)')
    s = s.replace('Tang All Stats +10 (', 'Tăng All Stats +10 (')
    s = s.replace('+500 Mau & +3 Giap (Toi da 10/10)', '+500 Máu & +3 Giáp (Tối đa 10/10)')
    s = s.replace('+500 Mau & +3 Giap (', '+500 Máu & +3 Giáp (')
    s = s.replace('Duoc Pham Chien Dau (Con ', 'Dược Phẩm Chiến Đấu (Còn ')
    s = s.replace('Duoc Pham (+15% Dmg/-10% Nhan/+15% MS, 3p)', 'Dược Phẩm (+15% Dmg/-10% Nhận/+15% MS, 3p)')
    s = s.replace('Luyen Tap Cuoi Game & Tiem Vang (-up)', 'Luyện Tập Cuối Game & Tiệm Vàng (-up)')
    s = s.replace('Hom Do Bi An (Hiem/Su Thi/Huyen Thoai)', 'Hòm Đồ Bí Ẩn (Hiếm/Sử Thi/Huyền Thoại)')
    s = s.replace('"Dong"', '"Đóng"')

    s = s.replace('[LUYEN TAP]|r Can mot Pokemon con song.', '[LUYỆN TẬP]|r Cần một Pokémon còn sống.')
    s = s.replace('[LUYEN TAP]|r Nang cap All Stats da dat TOI DA', '[LUYỆN TẬP]|r Nâng cấp All Stats đã đạt TỐI ĐA')
    s = s.replace('[LUYEN TAP]|r Can ', '[LUYỆN TẬP]|r Cần ')
    s = s.replace('[LUYEN TAP]|r Da nang cap All Stats +10', '[LUYỆN TẬP]|r Đã nâng cấp All Stats +10')
    s = s.replace('[LUYEN TAP]|r Nang cap Mau & Giap da dat TOI DA', '[LUYỆN TẬP]|r Nâng cấp Máu & Giáp đã đạt TỐI ĐA')
    s = s.replace('[LUYEN TAP]|r Da nang cap +500 Mau Toi Da & +3 Giap', '[LUYỆN TẬP]|r Đã nâng cấp +500 Máu Tối Đa & +3 Giáp')
    s = s.replace('[LUYEN TAP]|r Can 3.500 vang de mo Hom Do Bi An.', '[LUYỆN TẬP]|r Cần 3.500 vàng để mở Hòm Đồ Bí Ẩn.')
    s = s.replace('[HOM DO BI AN]|r Da mo ra ', '[HÒM ĐỒ BÍ ẨN]|r Đã mở ra ')
    s = s.replace('[LUYEN TAP]|r Can 3.000 vang de mua Duoc Pham Chien Dau.', '[LUYỆN TẬP]|r Cần 3.000 vàng để mua Dược Phẩm Chiến Đấu.')
    s = s.replace('[DUOC PHAM]|r Co hieu luc trong 3 phut (+15% Sat thuong, -10% Sat thuong nhan, +15% Toc chay; mat khi chet)!',
                  '[DƯỢC PHẨM]|r Có hiệu lực trong 3 phút (+15% Sát thương, -10% Sát thương nhận, +15% Tốc chạy; mất khi chết)!')

    # 5. -forge (Tiệm Rèn Thần Bí)
    s = s.replace('TIEM REN THAN BI - Nang cap & Dung hop Do Loot', 'TIỆM RÈN THẦN BÍ - Nâng cấp & Dung hợp Đồ Loot')
    s = s.replace('"O " + I2S(slot + 1) + ": " + GetItemName(curIt) + " (TOI DA)"', '"Ô " + I2S(slot + 1) + ": " + GetItemName(curIt) + " (TỐI ĐA)"')
    s = s.replace('"O " + I2S(slot + 1) + ": " + GetItemName(curIt) + " -> +"', '"Ô " + I2S(slot + 1) + ": " + GetItemName(curIt) + " -> +"')
    s = s.replace('Dung hop 2 do thap nhat -> Bac ke (60/40/20%, 1500 vang)', 'Dung hợp 2 đồ thấp nhất -> Bậc kế (60/40/20%, 1500 vàng)')
    s = s.replace('[TIEM REN]|r Can mot Pokemon con song.', '[TIỆM RÈN]|r Cần một Pokémon còn sống.')
    s = s.replace('[TIEM REN]|r Can 1.500 vang de Dung hop.', '[TIỆM RÈN]|r Cần 1.500 vàng để Dung hợp.')
    s = s.replace('[TIEM REN]|r Can it nhat 2 trang bi Loot Thuong/Hiem/Su Thi trong tui do de dung hop!',
                  '[TIỆM RÈN]|r Cần ít nhất 2 trang bị Loot Thường/Hiếm/Sử Thi trong túi đồ để dung hợp!')
    s = s.replace('[TIEM REN]|r Dung hop thanh cong! Tao ra trang bi ', '[TIỆM RÈN]|r Dung hợp thành công! Tạo ra trang bị ')
    s = s.replace('[TIEM REN]|r Dung hop that bai! 1 trang bi phoi da vo vun thanh tro bui.',
                  '[TIỆM RÈN]|r Dung hợp thất bại! 1 trang bị phôi đã vỡ vụn thành tro bụi.')
    s = s.replace('[TIEM REN]|r Trang bi nay da dat toi da [MYTHIC +5]!', '[TIỆM RÈN]|r Trang bị này đã đạt tối đa [MYTHIC +5]!')
    s = s.replace('[TIEM REN]|r Can " + I2S(cost) + " vang de nang cap.', '[TIỆM RÈN]|r Cần " + I2S(cost) + " vàng để nâng cấp.')
    s = s.replace('[TIEM REN]|r Nang cap thanh cong! Dat moc ', '[TIỆM RÈN]|r Nâng cấp thành công! Đạt mốc ')
    s = s.replace('[TIEM REN]|r Nang cap that bai! Trang bi bi tut cap xuong +', '[TIỆM RÈN]|r Nâng cấp thất bại! Trang bị bị tụt cấp xuống +')
    s = s.replace('[TIEM REN]|r Nang cap len +1 that bai (trang bi an toan, khong tut cap).',
                  '[TIỆM RÈN]|r Nâng cấp lên +1 thất bại (trang bị an toàn, không tụt cấp).')
    s = s.replace('[REN THAN THOAI +5!]', '[RÈN THẦN THOẠI +5!]')
    s = s.replace('da ren thanh cong', 'đã rèn thành công')
    s = s.replace('(+120% Chi so/Hieu ung)!', '(+120% Chỉ số/Hiệu ứng)!')

    # 6. -solo / -duel
    s = s.replace('[SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r da tu choi Solo! (So qua chay mat dep! =)))',
                  '[SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r đã từ chối Solo! (Sợ quá chạy mất dép! =)))')
    s = s.replace('[SOLO]|r Dang co mot keo Solo dien ra hoac dang cho tra loi.',
                  '[SOLO]|r Đang có một kèo Solo diễn ra hoặc đang chờ trả lời.')
    s = s.replace('[SOLO]|r Can mot Pokemon con song de thach dau.',
                  '[SOLO]|r Cần một Pokémon còn sống để thách đấu.')
    s = s.replace('[SOLO]|r Cach dung: -solo <so thu tu doi thu 1..12> (hoac go -solo de tu chon doi thu dau tien).',
                  '[SOLO]|r Cách dùng: -solo <số thứ tự đối thủ 1..12> (hoặc gõ -solo để tự chọn đối thủ đầu tiên).')
    s = s.replace('[SOLO]|r Doi thu khong co Pokemon con song.',
                  '[SOLO]|r Đối thủ không có Pokémon còn sống.')
    s = s.replace('[THACH DAU SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r da thach dau |cff7dd3fc" + GetPlayerName(Player(targetPid)) + "|r SOLO SINH TU 1v1 (thua roi 1 do)! Go |cff4ade80-yes|r hoac |cffff5c5c-no|r trong 20s!',
                  '[THÁCH ĐẤU SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r đã thách đấu |cff7dd3fc" + GetPlayerName(Player(targetPid)) + "|r SOLO SINH TỬ 1v1 (thua rơi 1 đồ)! Gõ |cff4ade80-yes|r hoặc |cffff5c5c-no|r trong 20s!')
    s = s.replace('[SOLO SINH TU!]', '[SOLO SINH TỬ!]')
    s = s.replace('DAU DEN CHET tai Trung Tam! Ke thua roi 1 do ngau nhien!', 'ĐẤU ĐẾN CHẾT tại Trung Tâm! Kẻ thua rơi 1 đồ ngẫu nhiên!')
    s = s.replace('[SOLO CHIEN THANG!]', '[SOLO CHIẾN THẮNG!]')
    s = s.replace('da de bep', 'đã đè bẹp')
    s = s.replace('va cuop duoc', 'và cướp được')
    s = s.replace('[SOLO]|r Huy Solo: ca hai nguoi choi phai co Pokemon con song.',
                  '[SOLO]|r Hủy Solo: cả hai người chơi phải có Pokémon còn sống.')
    s = s.replace('[SOLO]|r Loi moi Solo Sinh Tu da het han.',
                  '[SOLO]|r Lời mời Solo Sinh Tử đã hết hạn.')
    s = s.replace('[SOLO]|r Tran Solo Sinh Tu ket thuc hoa (het 90s).',
                  '[SOLO]|r Trận Solo Sinh Tử kết thúc hòa (hết 90s).')

    # 7. Events & Announcements
    s = s.replace('[SU KIEN ALTAR #', '[SỰ KIỆN ALTAR #')
    s = s.replace('Ban tho Trung Tam da |cffffd166KICH HOAT|r! Giu |cff4ade8020s|r de nhan |cffffd166Vang Toan Doi + 2 Do Loot|r!',
                  'Bàn thờ Trung Tâm đã |cffffd166KÍCH HOẠT|r! Giữ |cff4ade8020s|r để nhận |cffffd166Vàng Toàn Đội + 2 Đồ Loot|r!')
    s = s.replace('[CHIEM DUOC ALTAR!]', '[CHIẾM ĐƯỢC ALTAR!]')
    s = s.replace('da chiem Ban tho Trung Tam! (|cffffd166+" + I2S(rewardGold) + " vang|r moi nguoi, |cffd896ff2 Do Loot Thuong|r)',
                  'đã chiếm Bàn thờ Trung Tâm! (|cffffd166+" + I2S(rewardGold) + " vàng|r mỗi người, |cffd896ff2 Đồ Loot Thưởng|r)')
    s = s.replace('[LENH TRUY NA!]', '[LỆNH TRUY NÃ!]')
    s = s.replace('dang bi TRUY NA trong |cffffd16690 giay|r! Tieu diet nhan |cffffd166+1.200 VANG|r - song sot nhan |cffffd166+1.000 VANG|r!',
                  'đang bị TRUY NÃ trong |cffffd16690 giây|r! Tiêu diệt nhận |cffffd166+1.200 VÀNG|r - sống sót nhận |cffffd166+1.000 VÀNG|r!')
    s = s.replace('[TRUY NA KET THUC!]', '[TRUY NÃ KẾT THÚC!]')
    s = s.replace('da song sot qua lenh truy na!', 'đã sống sót qua lệnh truy nã!')
    s = s.replace('[TIEN THUONG TRUY NA!]', '[TIỀN THƯỞNG TRUY NÃ!]')
    s = s.replace('da san thanh cong muc tieu truy na', 'đã săn thành công mục tiêu truy nã')
    s = s.replace('[KHO BAU HOANG KIM]', '[KHO BÁU HOÀNG KIM]')
    s = s.replace('da xuat hien gan Trung Tam! San duoi ngay trong vong 60s de nhan|r |cffffd166+1.800 VANG & Do Quy|r!',
                  'đã xuất hiện gần Trung Tâm! Săn đuổi ngay trong vòng 60s để nhận|r |cffffd166+1.800 VÀNG & Đồ Quý|r!')
    s = s.replace('[KHO BAU BI HA!]', '[KHO BÁU BỊ HẠ!]')
    s = s.replace('da bat duoc', 'đã bắt được')
    s = s.replace('[MAGIKARP KHONG LO]', '[MAGIKARP KHỔNG LỒ]')
    s = s.replace('Mot con Magikarp khong lo dang ngo xuat hien gan Trung Tam! Vang mien phi... hay la mot cai bay?',
                  'Một con Magikarp khổng lồ đáng ngờ xuất hiện gần Trung Tâm! Vàng miễn phí... hay là một cái bẫy?')
    s = s.replace('[DINH BAY ROI!]', '[DÍNH BẪY RỒI!]')
    s = s.replace('Magikarp khong lo da tien hoa thanh |cffff5c5cGYARADOS DO THINH NO|r! Tieu diet de nhan |cffffd166+3.000 VANG & Do Su Thi/Huyen Thoai|r!',
                  'Magikarp khổng lồ đã tiến hóa thành |cffff5c5cGYARADOS ĐỎ THỊNH NỘ|r! Tiêu diệt để nhận |cffffd166+3.000 VÀNG & Đồ Sử Thi/Huyền Thoại|r!')
    s = s.replace('[GYARADOS DO BI HA!]', '[GYARADOS ĐỎ BỊ HẠ!]')
    s = s.replace('da chinh phuc |cffff5c5cGyarados Do Thinh No|r!', 'đã chinh phục |cffff5c5cGyarados Đỏ Thịnh Nộ|r!')
    s = s.replace('[CO NGU]', '[CỔ NGỮ]')
    s = s.replace('Co ngu ', 'Cổ ngữ ')
    s = s.replace('da xuat hien tai', 'đã xuất hiện tại')
    s = s.replace('da nhat|r |cff38bdf8Co Ngu Toc Do|r (+35% Toc chay/danh trong 60s)!',
                  'đã nhặt|r |cff38bdf8Cổ Ngữ Tốc Độ|r (+35% Tốc chạy/đánh trong 60s)!')
    s = s.replace('da nhat|r |cffff5c5cCo Ngu Cuong No|r (+25% Sat thuong trong 60s)!',
                  'đã nhặt|r |cffff5c5cCổ Ngữ Cuồng Nộ|r (+25% Sát thương trong 60s)!')
    s = s.replace('da nhat|r |cff4ade80Co Ngu Hoi Phuc|r (8% Mau & 12% Mana/s trong 10s)!',
                  'đã nhặt|r |cff4ade80Cổ Ngữ Hồi Phục|r (8% Máu & 12% Mana/s trong 10s)!')
    s = s.replace('da nhat|r |cffffd166Co Ngu Tai Phu|r (|cffffd166+600 vang & +500 XP|r toan doi)!',
                  'đã nhặt|r |cffffd166Cổ Ngữ Tài Phú|r (|cffffd166+600 vàng & +500 XP|r toàn đội)!')

    # 8. Startup quest message
    s = re.sub(
        r'call QuestMessageBJ\(GetPlayersAll\(\),\s*bj_QUESTMESSAGE_ALWAYSHINT,\s*"[^"]*"\)',
        'call QuestMessageBJ(GetPlayersAll(),bj_QUESTMESSAGE_ALWAYSHINT,"Chọn 1 Pokémon farm cùng đồng đội, up cấp, tiến hóa, săn Pokémon Huyền Thoại, thi đấu Pk...\\n\\nGõ -help hoặc bấm [F9] để xem hướng dẫn chi tiết.\\n")',
        s
    )

    # 9. Startup pick / repick text
    s = s.replace(
        'Chu phong go -random de phat ngau nhien Pokemon cho moi nguoi. Nguoi chua chon sau 45s se nhan ngau nhien. Go -repick trong 2 phut dau de doi Pokemon khac (toi da 2 lan, giu cap & do).',
        'Chủ phòng gõ -random để phát ngẫu nhiên Pokémon cho mọi người. Người chưa chọn sau 45s sẽ nhận ngẫu nhiên. Gõ -repick trong 2 phút đầu để đổi Pokémon khác (tối đa 2 lần, giữ cấp & đồ).'
    )
    s = s.replace(
        'Ban da co Pokemon roi. Go -repick trong 2 phut dau neu muon doi ngau nhien Pokemon khac.',
        'Bạn đã có Pokémon rồi. Gõ -repick trong 2 phút đầu nếu muốn đổi ngẫu nhiên Pokémon khác.'
    )
    s = s.replace('Nguoi choi khac da chon Pokemon nay roi.', 'Người chơi khác đã chọn Pokémon này rồi.')
    s = s.replace('Chi chu phong moi co the go lenh -random.', 'Chỉ chủ phòng mới có thể gõ lệnh -random.')
    s = s.replace('Chi duoc phep doi lai Pokemon trong 2 phut dau tran.', 'Chỉ được phép đổi lại Pokémon trong 2 phút đầu trận.')
    s = s.replace('Ban da het so luot doi Pokemon.', 'Bạn đã hết số lượt đổi Pokémon.')
    s = s.replace('Ban can Pokemon con song (khong o dang Mega) de doi.', 'Bạn cần Pokémon còn sống (không ở dạng Mega) để đổi.')
    s = s.replace('Hay chon mot Pokemon truoc.', 'Hãy chọn một Pokémon trước.')
    s = s.replace('-tp: bien ve can cu va hoi phuc sau 3 giay...', '-tp: biến về căn cứ và hồi phục sau 3 giây...')
    s = s.replace('-home: tro ve nha sau 5 giay...', '-home: trở về nhà sau 5 giây...')
    s = s.replace('Day Thoat Hiem: ve can cu sau 3 giay...', 'Dây Thoát Hiểm: về căn cứ sau 3 giây...')
    s = s.replace(
        'Pokemon League: buoc vao vong tron dau truong khi du 8 huy hieu (hoac go -league). Cong Exit dan ve can cu.',
        'Pokemon League: bước vào vòng tròn đấu trường khi đủ 8 huy hiệu (hoặc gõ -league). Cổng Exit dẫn về căn cứ.'
    )

    # 10. Localize Move Descriptions (Mv_Text templates)
    # Common headers
    s = s.replace('Special move (INT, vs Sp. Def):', 'Chiêu Đặc Biệt (INT, kháng bởi Sp. Def):')
    s = s.replace('Physical move (STR, vs Def):', 'Chiêu Vật Lý (STR, kháng bởi Def):')
    s = s.replace('Physical move (AGI, vs Def):', 'Chiêu Vật Lý (AGI, kháng bởi Def):')
    s = s.replace('Status move:', 'Chiêu Trạng Thái:')
    s = s.replace(', Power ', ', Uy lực ')
    s = s.replace('Effect:|r Heals 50% of the damage.', 'Hiệu ứng:|r Hồi máu bằng 50% lượng sát thương.')
    s = s.replace('Effect:|r No extra effect: +10% damage.', 'Hiệu ứng:|r Không có hiệu ứng phụ: +10% sát thương.')
    s = s.replace('Effect:|r Never misses (ignores lowered accuracy).', 'Hiệu ứng:|r Không bao giờ trượt (bỏ qua giảm chính xác).')
    s = s.replace('Roots the target for 3 seconds, dealing @1 damage per second.', 'Trói mục tiêu trong 3 giây, gây @1 sát thương mỗi giây.')
    s = s.replace('Deals @1 damage, then @2 damage every few seconds.', 'Gây @1 sát thương, sau đó gây @2 sát thương mỗi vài giây.')
    s = s.replace('Sends a wave that deals @1 damage to every enemy in a line.', 'Phóng luồng sóng gây @1 sát thương cho kẻ địch trên đường thẳng.')

    return s


def patch_strings(items_slk, func_txt, strings_txt):
    """Localizes item tooltips in ItemFunc.txt for Battle Items and Loot items with full accents."""
    # Common / Rare / Epic / Legendary Loot
    func_txt = func_txt.replace('Tip=|cffffffffDo Loot Thuong|r', 'Tip=|cffffffffĐồ Loot Thường|r')
    func_txt = func_txt.replace('Tip=|cff3399ffDo Loot Hiem|r', 'Tip=|cff3399ffĐồ Loot Hiếm|r')
    func_txt = func_txt.replace('Tip=|cffcc66ffDo Loot Su Thi|r', 'Tip=|cffcc66ffĐồ Loot Sử Thi|r')
    func_txt = func_txt.replace('Tip=|cffff8800Do Loot Huyen Thoai|r', 'Tip=|cffff8800Đồ Loot Huyền Thoại|r')
    func_txt = func_txt.replace('Tip=|cffffffffCommon Loot|r', 'Tip=|cffffffffĐồ Loot Thường|r')
    func_txt = func_txt.replace('Tip=|cff3399ffRare Loot|r', 'Tip=|cff3399ffĐồ Loot Hiếm|r')
    func_txt = func_txt.replace('Tip=|cffcc66ffEpic Loot|r', 'Tip=|cffcc66ffĐồ Loot Sử Thi|r')
    func_txt = func_txt.replace('Tip=|cffff8800Legendary Loot|r', 'Tip=|cffff8800Đồ Loot Huyền Thoại|r')

    # Battle Items
    # IB01: Choice Band
    func_txt = func_txt.replace(
        'Ubertip=Attacks deal +35% damage. -10% move speed.',
        'Ubertip=Tăng +35% sát thương đòn đánh. Giảm -10% tốc độ di chuyển.'
    )
    func_txt = func_txt.replace(
        'Ubertip=Tang +35% sat thuong don danh. Giam -10% toc do di chuyen.',
        'Ubertip=Tăng +35% sát thương đòn đánh. Giảm -10% tốc độ di chuyển.'
    )
    # IB04: Leftovers
    func_txt = func_txt.replace('Ubertip=Regenerates 1% max HP per second.', 'Ubertip=Hồi phục 1% Máu tối đa mỗi giây.')
    func_txt = func_txt.replace('Ubertip=Hoi phuc 1% Mau toi da moi giay.', 'Ubertip=Hồi phục 1% Máu tối đa mỗi giây.')
    func_txt = func_txt.replace('Description=Regenerates 1% max HP per second.', 'Description=Hồi phục 1% Máu tối đa mỗi giây.')
    func_txt = func_txt.replace('Description=Hoi phuc 1% Mau toi da moi giay.', 'Description=Hồi phục 1% Máu tối đa mỗi giây.')
    # IB05: Focus Sash
    func_txt = func_txt.replace(
        'Ubertip=A hit that would knock it out while above 50% HP leaves it at 1 HP (once every 60s).',
        'Ubertip=Đòn đánh kết liễu khi Máu trên 50% sẽ giữ lại 1 Máu (Hồi chiêu 60 giây một lần).'
    )
    func_txt = func_txt.replace(
        'Ubertip=Don danh ket lieu khi Mau tren 50% se giu lai 1 Mau (Hoi chieu 60 giay mot lan).',
        'Ubertip=Đòn đánh kết liễu khi Máu trên 50% sẽ giữ lại 1 Máu (Hồi chiêu 60 giây một lần).'
    )
    func_txt = func_txt.replace(
        'Description=A hit that would knock it out while above 50% HP leaves it at 1 HP (once every 60s).',
        'Description=Đòn đánh kết liễu khi Máu trên 50% sẽ giữ lại 1 Máu (Hồi chiêu 60 giây một lần).'
    )
    func_txt = func_txt.replace(
        'Description=Don danh ket lieu khi Mau tren 50% se giu lai 1 Mau (Hoi chieu 60 giay mot lan).',
        'Description=Đòn đánh kết liễu khi Máu trên 50% sẽ giữ lại 1 Máu (Hồi chiêu 60 giây một lần).'
    )

    return func_txt
