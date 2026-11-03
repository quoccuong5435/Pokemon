"""Proposal only: build docs/pokemon-abilities-proposal.md (ability per Pokemon + current skills). Changes no map."""
import re
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402
import objdata  # noqa: E402

SKILL_FIX = {'A037': 'Dragon Claw', 'A05G': 'Pin Missile', 'A046': 'Poison Sting'}

# family -> (title, effect)
FAMILIES = {
    'Pinch': ('Pinch', 'Máu dưới 33% thì +40% sát thương gây ra.'),
    'Contact': ('Phản đòn', 'Khi bị đánh: 20% cơ hội gây hiệu ứng lên kẻ đánh (tuỳ tên, xem bên dưới).'),
    'Absorb': ('Miễn/hấp thụ hệ', 'Không nhận sát thương từ Pokemon thuộc hệ đó (tuỳ tên, xem bên dưới).'),
    'Intimidate': ('Intimidate', 'Bị đánh (sau 10s không giao tranh): kẻ địch trong 500 tầm giảm 20% sát thương trong 6s.'),
    'Pressure': ('Pressure', 'Kẻ đánh nó mất 20 mana mỗi lần đánh.'),
    'Sturdy': ('Sturdy', 'Đòn chí mạng chỉ còn lại 10% máu, mỗi 90s một lần.'),
    'Defense': ('Giáp', '+4 giáp.'),
    'Multiscale': ('Multiscale', 'Khi đầy máu: nhận ít hơn 40% sát thương.'),
    'Recovery': ('Hồi phục', '5s không bị đánh thì hồi 2.5% máu tối đa mỗi giây.'),
    'Power': ('Tăng sức mạnh', '+20% sát thương gây ra.'),
    'Rising': ('Càng đánh càng giận', 'Mỗi lần bị đánh +5% sát thương (cộng dồn 6 lần, 5s).'),
    'Speed': ('Tốc độ', '+12% tốc chạy.'),
    'Lucky': ('Đòn may mắn', '12% cơ hội gây gấp đôi sát thương khi đánh thường.'),
    'Dodge': ('Né tránh', '15% cơ hội né đòn.'),
    'Aura': ('Hào quang', 'Ảnh hưởng kẻ địch xung quanh (tuỳ tên, xem bên dưới).'),
    'Unique': ('Đặc biệt', 'Riêng từng con (xem bên dưới).'),
}
ABILITY_NOTES = {
    'Static': 'Contact: choáng kẻ đánh 1s', 'Flame Body': 'Contact: đốt kẻ đánh, mất 3% máu tối đa trong 3s',
    'Poison Point': 'Contact: nhiễm độc kẻ đánh, mất 4% máu tối đa trong 4s',
    'Cute Charm': 'Contact: kẻ đánh -40% tốc chạy 3s',
    'Synchronize': 'Contact: kẻ đánh -40% tốc chạy 3s',
    'Levitate': 'Absorb: miễn sát thương từ Pokemon hệ Ground',
    'Water Absorb': 'Absorb: miễn sát thương từ hệ Water, hồi 25% lượng đó',
    'Volt Absorb': 'Absorb: miễn sát thương từ hệ Electric, hồi 25% lượng đó',
    'Lightning Rod': 'Absorb: miễn sát thương từ hệ Electric, hồi 25% lượng đó',
    'Flash Fire': 'Absorb: miễn sát thương từ hệ Fire, +30% sát thương trong 6s',
    'Magnet Pull': 'Aura: kẻ địch trong 400 tầm -15% tốc chạy',
    'Bad Dreams': 'Aura: kẻ địch trong 450 tầm mất 1% máu tối đa mỗi giây',
    'Multitype': 'Unique: +10% sát thương gây ra và -10% sát thương nhận',
    'Slow Start': 'Unique: 30s đầu sau khi xuất hiện hoặc hồi sinh -40% sát thương gây ra, sau đó +25% sát thương',
}

ABILITY_FAMILY = {}
for fam, names in {
    'Pinch': 'Overgrow Blaze Torrent Swarm', 'Contact': 'Static Flame_Body Poison_Point Cute_Charm Synchronize',
    'Absorb': 'Levitate Water_Absorb Volt_Absorb Lightning_Rod Flash_Fire', 'Intimidate': 'Intimidate',
    'Pressure': 'Pressure', 'Sturdy': 'Sturdy', 'Defense': 'Shell_Armor Battle_Armor Clear_Body Rock_Head Soundproof',
    'Multiscale': 'Multiscale', 'Recovery': 'Shed_Skin Early_Bird Natural_Cure',
    'Power': 'Iron_Fist Adaptability Hyper_Cutter Technician Reckless', 'Rising': 'Guts Anger_Point',
    'Speed': 'Chlorophyll Swift_Swim Run_Away', 'Lucky': 'Keen_Eye Compound_Eyes',
    'Dodge': 'Sand_Veil Snow_Cloak Leaf_Guard Inner_Focus Air_Lock', 'Aura': 'Magnet_Pull Bad_Dreams',
    'Unique': 'Multitype Slow_Start',
}.items():
    for n in names.split():
        ABILITY_FAMILY[n.replace('_', ' ')] = fam

ASSIGN = {}
for ability, who in {
    'Overgrow': 'Bulbasaur Ivysaur Venusaur', 'Blaze': 'Charmander Charmeleon Charizard',
    'Torrent': 'Squirtle Wartortle Blastoise', 'Swarm': 'Weedle Kakuna Beedrill Scyther',
    'Static': 'Pikachu Raichu Voltorb Electrode', 'Synchronize': 'Abra Kadabra Alakazam Mew Espeon Umbreon',
    'Poison Point': 'Nidoran Nidorino Nidoking', 'Flame Body': 'Ponyta Rapidash', 'Cute Charm': 'Sylveon',
    'Levitate': 'Weezing Koffing Gastly Haunter Gengar', 'Water Absorb': 'Poliwag Poliwhirl Poliwrath Vaporeon',
    'Volt Absorb': 'Jolteon', 'Lightning Rod': 'Rhyhorn Rhydon', 'Flash Fire': 'Flareon Vulpix Ninetales',
    'Intimidate': 'Tauros Growlithe Arcanine Gyarados Hitmontop',
    'Pressure': 'Articuno Moltres Zapdos Mewtwo Deoxys Giratina Dialga Palkia',
    'Sturdy': 'Geodude Graveler Golem Steelix',
    'Shell Armor': 'Shellder Cloyster', 'Clear Body': 'Tentacool Tentacruel', 'Battle Armor': 'Kabuto Kabutops',
    'Rock Head': 'Onix', 'Soundproof': 'Mr.mime', 'Multiscale': 'Dragonite Lugia',
    'Shed Skin': 'Dratini Dragonair', 'Early Bird': 'Kangaskhan', 'Natural Cure': 'Staryu Starmie',
    'Iron Fist': 'Hitmonchan', 'Adaptability': 'Eevee', 'Hyper Cutter': 'Krabby Kingler Pinsir',
    'Technician': 'Scizor', 'Reckless': 'Hitmonlee', 'Guts': 'Machop Machoke Machamp',
    'Anger Point': 'Mankey Primeape', 'Chlorophyll': 'Bellsprout Weepinbell Victreebel Exeggcute Exeggutor',
    'Swift Swim': 'Omanyte Omastar', 'Run Away': 'Rattata Raticate', 'Keen Eye': 'Pidgey Pidgeotto Pidgeot',
    'Compound Eyes': 'Caterpie Metapod Butterfree', 'Sand Veil': 'Sandshrew Sandslash', 'Snow Cloak': 'Glaceon',
    'Leaf Guard': 'Leafleon', 'Inner Focus': 'Zubat Golbat Crobat', 'Air Lock': 'Rayquaza',
    'Magnet Pull': 'Magnemite Magneton', 'Bad Dreams': 'Darkrai', 'Multitype': 'Arceus', 'Slow Start': 'Regigigas',
}.items():
    for n in who.split():
        assert n not in ASSIGN, n
        ASSIGN[n] = ability
# the nine lines added in v2.3 already carry their ability as skill 4 (a passive)
NEW_LINES = {'Torchic': 'Blaze', 'Combusken': 'Blaze', 'Blaziken': 'Blaze', 'Treecko': 'Overgrow',
             'Grovyle': 'Overgrow', 'Sceptile': 'Overgrow', 'Larvitar': 'Sand Stream', 'Pupitar': 'Sand Stream',
             'Tyranitar': 'Sand Stream', 'Ralts': 'Trace', 'Kirlia': 'Trace', 'Gardevoir': 'Trace',
             'Gallade': 'Sharpness', 'Bagon': 'Intimidate', 'Shelgon': 'Intimidate', 'Salamence': 'Intimidate',
             'Beldum': 'Tough Claws', 'Metang': 'Tough Claws', 'Metagross': 'Tough Claws', 'Lucario': 'Justified',
             'Absol': 'Super Luck'}

MEGA_ABILITY = [
    ('Mega Venusaur', 'Thick Fat', '+6 giáp'),
    ('Mega Charizard X', 'Tough Claws', '+30% sát thương gây ra'),
    ('Mega Charizard Y', 'Drought', 'Kẻ địch trong 450 tầm mất 1% máu tối đa mỗi giây'),
    ('Mega Blastoise', 'Mega Launcher', '+30% sát thương gây ra'),
    ('Mega Beedrill', 'Adaptability', '+30% sát thương gây ra'),
    ('Mega Pidgeot', 'No Guard', '+20% sát thương gây ra và 12% đánh gấp đôi'),
    ('Mega Alakazam', 'Trace', '25% né đòn'),
    ('Mega Gengar', 'Shadow Tag', 'Kẻ địch trong 400 tầm -30% tốc chạy'),
    ('Mega Kangaskhan', 'Parental Bond', 'Con Kangaskhan đi theo và đánh cùng (cơ chế Mega có sẵn)'),
    ('Mega Pinsir', 'Aerilate', '+30% sát thương gây ra'),
    ('Mega Gyarados', 'Mold Breaker', '+30% sát thương gây ra'),
    ('Mega Steelix', 'Sand Force', 'Giữ Sturdy và +6 giáp'),
    ('Mega Scizor', 'Technician', '+30% sát thương gây ra'),
    ('Mega Mewtwo X', 'Steadfast', 'Mỗi lần bị đánh +7% sát thương (cộng dồn 6 lần, 5s)'),
    ('Mega Mewtwo Y', 'Insomnia', '20% né đòn'),
    ('Mega Rayquaza', 'Delta Stream', '25% né đòn'),
    ('Mega Blaziken', 'Speed Boost', '+20% tốc chạy'),
    ('Mega Sceptile', 'Lightning Rod', 'Miễn sát thương hệ Electric, hồi 25% lượng đó'),
    ('Mega Tyranitar', 'Sand Stream', 'Kẻ địch trong 450 tầm mất 1% máu tối đa mỗi giây'),
    ('Mega Gardevoir', 'Pixilate', '+30% sát thương gây ra'),
    ('Mega Gallade', 'Inner Focus', '20% né đòn'),
    ('Mega Salamence', 'Aerilate', '+30% sát thương gây ra'),
    ('Mega Metagross', 'Tough Claws', '+30% sát thương gây ra'),
    ('Mega Lucario', 'Adaptability', '+30% sát thương gây ra'),
    ('Mega Absol', 'Magic Bounce', 'Phản lại 20% sát thương nhận cho kẻ đánh'),
]


def load(path):
    a = mpq.MPQ(path)
    w3u = objdata.ObjFile(a.read('war3map.w3u'))
    txt = {}
    for n in a.listfile():
        if n.startswith('Units\\') and n.endswith(('Func.txt', 'Strings.txt')):
            cur = None
            for line in a.read(n).decode('utf-8', 'replace').replace('\r\n', '\n').split('\n'):
                m = re.match(r'\[(\w{4})\]', line)
                if m:
                    cur = m.group(1)
                    txt.setdefault(cur, {})
                elif cur and '=' in line:
                    k, v = line.split('=', 1)
                    txt[cur].setdefault(k, v)
    heroes = [o for o in w3u.custom if o.new[:1].isupper() and o.get('uhab')]

    def sname(s):
        if s in SKILL_FIX:
            return SKILL_FIX[s]
        d = txt.get(s, {})
        return (d.get('Name') or d.get('Tip') or s).split(',')[0]

    return [(o.new, o.get('upro'), o.get('unam').replace(' Pokemon', ''),
             [sname(s) for s in o.get('uhab').split(',') if s]) for o in heroes]


def main():
    heroes = load(sys.argv[1])
    out = ['# Pokemon Arena — danh sách Ability (đề xuất, chưa áp dụng vào map)', '',
           'Ability là nội dung thụ động riêng của từng Pokemon (hiện chưa Pokemon nào có). Khi lên Mega thì đổi sang Ability của Mega. Các hệ trong nhóm Miễn/hấp thụ chỉ có tác dụng với Pokemon của người chơi và legend (quái hoang dã không có hệ).', '',
           '## Nhóm hiệu ứng', '']
    for fam, (title, eff) in FAMILIES.items():
        names = [n for n, f in ABILITY_FAMILY.items() if f == fam]
        out.append('- **%s** (%s): %s' % (title, ', '.join(names), eff))
        for n in names:
            if n in ABILITY_NOTES:
                out.append('  - %s — %s' % (n, ABILITY_NOTES[n]))
    out += ['', '## Pokemon: Ability và skill hiện có', '',
            '| Pokemon | Hệ | Ability đề xuất | Skill hiện có |', '|---|---|---|---|']
    missing = []
    rows = {}
    for hid, name, typ, skills in heroes:
        ab = ASSIGN.get(name) or NEW_LINES.get(name)
        if ab is None:
            missing.append(name)
            continue
        key = (typ, ab, tuple(skills))
        rows.setdefault(key, []).append(name + ('*' if name in NEW_LINES else ''))
    for (typ, ab, skills), names in rows.items():
        out.append('| %s | %s | %s | %s |' % (' / '.join(names), typ, ab, ', '.join(skills)))
    out += ['', '`*` = dòng thêm ở v2.3, Ability đã có sẵn dưới dạng skill thụ động số 4.', '',
            '## Mega: Ability của Mega', '', '| Mega | Ability | Hiệu ứng |', '|---|---|---|']
    out += ['| %s | %s | %s |' % m for m in MEGA_ABILITY]
    out += ['', '## Hệ số sát thương kỹ năng (v2.8)', '',
            'Vấn đề: skill có sát thương cố định, còn quái lên bậc thì máu tăng rất nhiều, nên skill mất tác dụng.',
            'Cách sửa: sát thương skill (không tính đòn đánh thường) nhân với hệ số theo chỉ số chính của hero (sức mạnh, nhanh nhẹn hoặc trí tuệ, cao nhất): **x(1 + 0.011 x (chỉ số - 50))**, tối đa x10, chỉ số từ 50 trở xuống thì x1.', '',
            '| Chỉ số chính | 50 | 100 | 200 | 400 | 868 trở lên |', '|---|---|---|---|---|---|',
            '| Hệ số | x1.00 | x1.55 | x2.65 | x4.85 | x10 (tối đa) |', '',
            'Áp dụng cho mọi skill của mọi Pokemon người chơi, cả PvP. Hiệu ứng của Ability đều tính theo phần trăm (hoặc phần trăm máu tối đa) nên tự theo kịp quái, không có con số cố định.']
    open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('rows', len(rows), 'heroes', len(heroes), 'missing', missing)


main()
