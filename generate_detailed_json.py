import json

with open('_PokemonArena2.0_work/abilities_not_in_map.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define full descriptions and mechanics for each of the abilities not in map
descriptions = {
    # 1. Offensive & Combat Boost
    "Protean": "Đổi hệ của Pokémon sang hệ của chiêu thức vừa sử dụng ngay trước khi tung chiêu, nhận 1.5x STAB cho mọi kỹ năng. (Hidden Ability)",
    "Moxie": "Mỗi khi hạ gục một tướng địch hoặc quái lớn, nhận vĩnh viễn +10% Sát thương Vật lý (cộng dồn tối đa 5 tầng, kéo dài 60s). (Hidden Ability)",
    "Sheer Force": "Loại bỏ hoàn toàn các hiệu ứng phụ (slow/stun/burn) của kỹ năng để tăng thẳng +30% Sát thương gốc cho kỹ năng đó. (Normal/Hidden)",
    "Sniper": "Sát thương từ các đòn đánh Chí mạng (Critical Strike) tăng từ 150% lên 225%. (Normal/Hidden)",
    "Sharpness": "Các đòn tấn công dạng kiếm, chém, vuốt sắt (Sacred Sword, Night Slash, Leaf Blade...) được gia tăng +50% sát thương. (Normal)",
    "Supreme Overlord": "Nhận thêm +5% Sát thương tổng cho mỗi đồng đội đã bị hạ gục trước đó trong giao tranh (tối đa +25%). (Normal)",
    "Contrary": "Đảo ngược mọi hiệu ứng buff/debuff chỉ số: các chiêu thức tự giảm chỉ số (như Leaf Storm, Overheat) sẽ biến thành TĂNG chỉ số tương ứng. (Hidden Ability)",
    "Download": "Khi bước vào tầm giao tranh với tướng địch: nếu Giáp địch thấp hơn Kháng phép, nhận +25% Sát thương Vật lý; nếu Kháng phép thấp hơn, nhận +25% Sát thương Phép. (Normal)",
    "Analytic": "Nếu hành động/ra chiêu sau mục tiêu, kỹ năng gây thêm +30% sát thương. (Hidden Ability)",
    "Galvanize": "Chuyển toàn bộ kỹ năng và đòn đánh hệ Normal (Thường) sang hệ Electric (Điện) và tăng thêm +20% sát thương. (Hidden Ability)",
    "Scrappy": "Đòn đánh và kỹ năng hệ Normal/Fighting có thể đánh trúng và gây sát thương đầy đủ lên hệ Ghost (Bóng ma), miễn nhiễm hiệu ứng Intimidate. (Normal/Hidden)",
    "Hustle": "Tăng +50% Sát thương Tấn công cơ bản nhưng giảm 15% độ chính xác (15% tỉ lệ đánh trượt). (Normal/Hidden)",
    "Rivalry": "Gây thêm +25% sát thương lên mục tiêu cùng giới tính hoặc quái rừng trung lập; giảm 20% sát thương nếu khác giới tính. (Normal)",
    "Tinted Lens": "Các kỹ năng bị khắc chế (Not very effective / Kháng đòn) được nhân đôi sát thương (trở về 100% sát thương bình thường). (Hidden Ability)",
    "Stance Change": "Chuyển đổi dạng: Tung chiêu tấn công sẽ chuyển sang Dạng Kiếm (+Attack, -Armor); Dùng khiên/phòng thủ sẽ chuyển sang Dạng Khiên (+Armor, +Kháng phép). (Normal)",

    # 2. Retaliation, Contact & Curse
    "Rough Skin": "Kẻ địch khi tung đòn đánh vật lý tiếp xúc cận chiến sẽ bị phản lại 12% Máu tối đa dưới dạng sát thương chuẩn. (Normal/Hidden)",
    "Cursed Body": "Khi bị trúng kỹ năng từ đối phương, có 30% tỉ lệ khóa chiêu thức đó của kẻ địch trong 4 giây. (Normal)",
    "Effect Spore": "Khi nhận đòn đánh vật lý, có 30% cơ hội khiến kẻ tấn công ngẫu nhiên dính phải: Trúng Độc, Tê Liệt (Stun 1.5s), hoặc Ngủ say (Sleep 2s). (Normal/Hidden)",
    "Poison Touch": "Tất cả các đòn đánh cận chiến có 30% tỉ lệ đầu độc đối thủ (gây sát thương DPS và giảm 25% tốc độ hồi máu). (Hidden Ability)",
    "Liquid Ooze": "Kẻ địch cố tình hút máu (Life Drain, Giga Drain, Leech Seed) lên người này sẽ bị phản sát thương bằng đúng lượng máu muốn hút thay vì được hồi phục. (Normal)",
    "Aftermath": "Khi tử trận, phát nổ gây sát thương diện rộng bằng 25% Máu tối đa của bản thân lên tất cả kẻ địch xung quanh. (Hidden Ability)",
    "Pickpocket": "Khi bị đối phương đánh cận chiến, đánh cắp ngay lập tức 50-100 vàng từ người đánh (hồi chiêu 15s). (Hidden Ability)",
    "Magician": "Tung chiêu trúng kẻ địch sẽ đánh cắp 1 điểm tích lũy buff hoặc tạm thời phong ấn trang bị kích hoạt của địch trong 3s. (Hidden Ability)",
    "Stench": "Mỗi đòn đánh hoặc kỹ năng gây sát thương có 10% cơ hội làm choáng (micro-stun 0.5s) đối thủ. (Hidden Ability)",

    # 3. Defense, Absorption & Immunity
    "Wonder Guard": "Chỉ nhận sát thương từ các đòn đánh Siêu Hiệu Quả (Super Effective). Miễn nhiễm 100% mọi sát thương từ các hệ đòn đánh khác! (Normal)",
    "Magic Guard": "Miễn nhiễm hoàn toàn với mọi dạng sát thương gián tiếp: không bị mất máu bởi Độc, Bỏng, Bão cát, Mưa đá hay Phản đòn. (Normal/Hidden)",
    "Bulletproof": "Miễn nhiễm 100% sát thương và hiệu ứng từ các kỹ năng dạng đạn pháo, cầu năng lượng, bom (Shadow Ball, Sludge Bomb, Gyro Ball, Focus Blast...). (Hidden Ability)",
    "Solid Rock": "Giảm 25% sát thương nhận vào từ các đòn đánh Siêu Hiệu Quả (Super Effective). (Normal)",
    "Marvel Scale": "Khi đang bị dính bất kỳ hiệu ứng bất lợi nào (Stun, Slow, Burn, Poison, Freeze), Giáp và Kháng phép được tăng vọt +50%. (Normal/Hidden)",
    "Unaware": "Bỏ qua hoàn toàn các chỉ số cộng thêm (Attack boost, Defense buff) của mục tiêu khi tính toán sát thương gây ra và nhận vào. (Hidden Ability)",
    "Shield Dust": "Ngăn chặn và miễn nhiễm 100% với các hiệu ứng phụ bất lợi kèm theo của mọi chiêu thức đối thủ. (Normal)",
    "Weak Armor": "Khi nhận đòn đánh vật lý, giảm 2 Giáp nhưng nhận ngay +25% Tốc độ di chuyển trong 4s (cộng dồn). (Hidden Ability)",
    "Overcoat": "Miễn nhiễm hoàn toàn sát thương bão cát/mưa đá và các chiêu thức dạng bột phấn (Spore, Sleep Powder). (Hidden Ability)",
    "Suction Cups": "Bám chặt vào mặt đất, miễn nhiễm hoàn toàn với các kỹ năng hất tung, đẩy lùi, kéo giật hoặc dịch chuyển cưỡng chế. (Normal)",
    "White Smoke": "Khói trắng bảo hộ ngăn không cho đối phương làm suy giảm bất kỳ chỉ số cơ bản nào. (Normal)",
    "Big Pecks": "Giáp không thể bị bào mòn hoặc giảm bởi bất kỳ chiêu thức phá giáp nào. (Hidden Ability)",
    "Limber": "Cơ thể dẻo dai miễn nhiễm hoàn toàn với trạng thái Tê Liệt (Paralysis) và Làm choáng (Stun). (Normal)",
    "Immunity": "Hệ miễn dịch tuyệt đối, không thể bị Trúng Độc (Poison/Toxic). (Normal)",
    "Magma Armor": "Thân nhiệt dung nham, miễn nhiễm hoàn toàn với trạng thái Đóng băng (Freeze) và Đòn làm chậm băng giá. (Normal)",
    "Vital Spirit": "Tinh thần hưng phấn, miễn nhiễm hoàn toàn với trạng thái Buồn ngủ / Ngủ say (Sleep). (Normal/Hidden)",
    "Damp": "Tỏa ra độ ẩm ức chế: khóa hoàn toàn các kỹ năng Tự sát (Self-Destruct, Explosion) và giảm 40% sát thương nổ diện rộng trong phạm vi 800. (Normal/Hidden)",

    # 4. Weather & Terrain Synergy
    "Sand Rush": "Tăng gấp đôi (+100%) Tốc độ di chuyển và Tốc độ đánh khi Thời tiết là Bão Cát (Sandstorm). (Hidden Ability)",
    "Slush Rush": "Tăng gấp đôi (+100%) Tốc độ di chuyển và Tốc độ đánh khi Thời tiết là Mưa Đá (Hail / Snow). (Hidden Ability)",
    "Rain Dish": "Hồi phục 3% Máu tối đa mỗi giây liên tục khi Thời tiết là Mưa Rào (Rain). (Normal/Hidden)",
    "Ice Body": "Hồi phục 3% Máu tối đa mỗi giây và miễn nhiễm sát thương đóng băng khi Thời tiết là Mưa Đá (Hail). (Hidden Ability)",
    "Dry Skin": "Hồi 2% Máu/s trong Mưa và hồi máu khi trúng đòn Nước; nhưng nhận thêm +25% sát thương trong Nắng và từ hệ Lửa. (Normal/Hidden)",
    "Storm Drain": "Hút mọi kỹ năng hệ Nước về phía bản thân, miễn nhiễm sát thương nước và nhận ngay +25% Sát thương Phép. (Hidden Ability)",
    "Motor Drive": "Hấp thụ mọi kỹ năng hệ Điện: miễn nhiễm sát thương điện và tăng +30% Tốc độ di chuyển trong 6s. (Normal)",
    "Surge Surfer": "Tốc độ di chuyển tăng gấp đôi (+100%) khi đứng trong Vùng Địa Hình Điện (Electric Terrain) hoặc gần tháp/nhà sét. (Normal)",
    "Cloud Nine": "Hào quang xóa sổ thời tiết: khi có mặt trên sân, toàn bộ hiệu ứng môi trường (Nắng, Mưa, Cát, Tuyết) đều bị vô hiệu hóa. (Normal/Hidden)",
    "Hydration": "Tự động hóa giải và thanh lọc mọi trạng thái bất lợi (Stun/Slow/Burn/Poison) vào cuối mỗi giây nếu trời mưa. (Normal/Hidden)",
    "Harvest": "Sau khi ăn quả Berries, có 50% cơ hội mỗi 10 giây (100% nếu trời Nắng) tự động mọc lại quả Berry đó trong hòm đồ. (Hidden Ability)",

    # 5. Mobility, Crowd Control & Inversion
    "Neutralizing Gas": "Tỏa ra khí độc đặc biệt dập tắt và vô hiệu hóa toàn bộ Kỹ năng Bị động (Abilities) của tất cả Pokémon xung quanh trong phạm vi 700! (Normal)",
    "Unburden": "Khi sử dụng hết một vật phẩm tiêu hao (Potion, Berry, Scroll), Tốc độ di chuyển tăng vọt +100% trong 8 giây. (Hidden Ability)",
    "Prankster": "Tất cả các chiêu thức trạng thái, khống chế, buff/debuff và hồi phục được giảm 50% thời gian hồi chiêu và thi triển tức thì. (Hidden Ability)",
    "Arena Trap": "Khóa chặt mặt đất, ngăn không cho tất cả Pokémon không bay trong phạm vi 600 bỏ chạy hoặc dịch chuyển tức thời. (Normal)",
    "Quick Feet": "Khi bị dính hiệu ứng bất lợi, Tốc độ chạy tăng thêm +50% và bỏ qua giới hạn tốc độ chạy tối đa. (Normal/Hidden)",
    "Rattled": "Khi bị trúng đòn đánh từ hệ Bug, Ghost hoặc Dark, tốc độ di chuyển tăng thêm +25% trong 5 giây. (Hidden Ability)",
    "Unnerve": "Phát ra khí tức căng thẳng khiến tất cả kẻ địch trong phạm vi 800 không thể cắn Berries hay dùng bình máu/mana. (Normal/Hidden)",
    "Stall": "Đòn đánh luôn đi sau đối thủ một nhịp, nhưng mỗi đòn đánh được tích lũy thêm uy lực và giảm 20% sát thương nhận vào. (Normal)",
    "Tangled Feet": "Khi bị rơi vào trạng thái Rối loạn (Confusion), Tỉ lệ né tránh đòn đánh tăng vọt lên +50%. (Normal)",
    "Own Tempo": "Nhịp điệu tự nhiên giúp miễn nhiễm hoàn toàn với trạng thái Rối loạn (Confusion) và Khiêu khích (Taunt). (Normal/Hidden)",
    "Anticipation": "Cảm nhận được đòn hiểm: nếu đối thủ sở hữu chiêu thức Siêu Hiệu Quả hoặc One-hit KO, lập tức phát ra cảnh báo và nhận giáp ảo 200 HP. (Normal/Hidden)",

    # 6. Team Support, Sustain & Utility
    "Friend Guard": "Giảm 25% toàn bộ sát thương mà đồng đội xung quanh nhận phải trong bán kính 600. (Hidden Ability)",
    "Healer": "Mỗi 5 giây, có 30% tỉ lệ tự động hóa giải một hiệu ứng bất lợi trên người đồng minh đứng cạnh. (Hidden Ability)",
    "Poison Heal": "Thay vì mất máu khi Trúng Độc (Poison/Toxic), Pokémon này sẽ được hồi lại 12.5% Máu tối đa mỗi 2 giây! (Normal)",
    "Justified": "Mỗi khi nhận sát thương từ kỹ năng hệ Dark (Bóng tối), Sát thương Tấn công được tăng thêm +25% trong 8 giây. (Hidden Ability)",
    "Telepathy": "Miễn nhiễm hoàn toàn với mọi sát thương diện rộng và kỹ năng do đồng đội gây ra (chống Friendly Fire). (Hidden Ability)",
    "Illuminate": "Tầm nhìn đêm và ngày tăng thêm +500 phạm vi, đồng thời phát hiện tàng hình (True Sight) trong phạm vi 400. (Normal)",
    "Forewarn": "Khi lại gần tướng địch, tự động phát hiện và cảnh báo chiêu thức có sát thương cơ bản cao nhất của kẻ địch đó. (Normal)",
    "Frisk": "Phát hiện trang bị và lượng vàng mà tướng địch đang mang trên người ngay khi vừa chạm mặt. (Hidden Ability)",
    "Gluttony": "Tự động sử dụng Berries sớm hơn bình thường (ngay khi Máu xuống dưới 50% thay vì chờ đến 25%). (Hidden Ability)",
    "Cud Chew": "Nhai lại: sau khi ăn quả Berry, vào lượt tiếp theo sẽ tự động nhận thêm một lần hiệu ứng của quả Berry đó miễn phí. (Hidden Ability)",
    "Plus": "Khi đứng gần đồng minh có Đặc tính Plus hoặc Minus, cả hai cùng nhận thêm +20% Sát thương Phép. (Hidden Ability)",
    "Minus": "Khi đứng gần đồng minh có Đặc tính Plus hoặc Minus, cả hai cùng nhận thêm +20% Sát thương Phép. (Hidden Ability)",
    "Imposter": "Tự động sao chép hoàn toàn ngoại hình, kỹ năng và chỉ số cơ bản của tướng địch đối diện ngay khi vào giao tranh. (Hidden Ability)"
}

# Attach descriptions
for item in data:
    name = item['name']
    item['desc'] = descriptions.get(name, "Đặc tính chiến đấu đặc trưng theo hệ thống PokeAPI canon.")

with open('_PokemonArena2.0_work/abilities_not_in_map_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved abilities_not_in_map_detailed.json with descriptions!")
