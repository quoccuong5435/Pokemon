"""Proposal data for the 56 Hidden Abilities that have no code in the 4.2x map (review page docs/hidden-ability-plan.html).

Usage (from _PokemonArena2.0_work):
  python -I analysis/hidden_ability_plan.py analysis/jass_ref/_tmp_v42a_war3map.j analysis/hidden_ability_plan.json
Each entry: name, Pokemon that have it, the map's own (Vietnamese) design text, the proposed effect, how hard it is
(1 one hook / data, 2 a few hooks, 3 new system) and whether the proposal differs from the map's design text.
"""
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
import hidden_ability  # noqa: E402

# name -> (proposed effect, difficulty 1..3, differs from the map's design text, hook in the map)
PLAN = {
    'Unnerve': ('Hero địch trong 700 nhận hồi máu ít hơn 30% (mọi nguồn hồi).', 3, True, 'hàm hồi máu chung'),
    'Sheer Force': ('Chiêu có hiệu ứng phụ (trạng thái, giảm chỉ số, khựng, rối) mất hiệu ứng đó nhưng +30% sát thương.', 2, False, 'Ab_OutMult + Fx_AfterHit'),
    'Telepathy': ('Nhận ít hơn 20% sát thương từ chiêu khi có hero đồng minh trong 600. Map không có sát thương đồng đội nên bỏ phần đó.', 1, True, 'Ab_InMult'),
    'Analytic': ('+30% sát thương chiêu lên mục tiêu vừa ra chiêu trong 3 giây trước.', 1, True, 'Ab_OutMult (giờ ra chiêu của mục tiêu)'),
    'Justified': ('Trúng chiêu hệ Dark: +1 Attack (12 giây).', 1, False, 'Fx_AfterHit + Fx_StageAdd'),
    'Moxie': ('Hạ gục hero, quái tinh anh hoặc boss: +1 Attack (30 giây, cộng dồn tới +6).', 1, False, 'Fx_OnDeath'),
    'Weak Armor': ('Bị đánh thường: −1 Defense, +2 Speed (12 giây, hồi 5 giây).', 1, False, 'Fx_AfterHit + Fx_StageAdd'),
    'Infiltrator': ('Chiêu và đòn đánh bỏ qua các bậc tăng Defense / Sp. Def của mục tiêu.', 2, True, 'Fx_StageMult'),
    'Vital Spirit': ('Miễn ngủ.', 1, False, 'Fx_Status'),
    'Regenerator': ('Không đánh và không bị đánh 4 giây: hồi 2% máu tối đa mỗi giây. Bản dùng chung, khác bản Legend của Ho-Oh.', 2, True, 'Ab_Tick'),
    'Rain Dish': ('Trời mưa: hồi 2% máu tối đa mỗi giây.', 1, False, 'Ab_Tick + Wth_Cur'),
    'Light Metal': ('+30 tốc chạy và không bị đẩy lùi (Dragon Tail, Circle Throw).', 2, True, 'Ab_Tick + đẩy lùi'),
    'Damp': ('Chiêu nổ (Explosion, Self-Destruct, Misty Explosion) của địch trong 800 giảm 50% sát thương.', 2, False, 'Ab_OutMult'),
    'Rattled': ('Trúng chiêu hệ Bug, Ghost hoặc Dark: +1 Speed (12 giây).', 1, False, 'Fx_AfterHit + Fx_StageAdd'),
    'Unburden': ('Dùng một món đồ tiêu hao: +100% tốc chạy 6 giây (hồi 20 giây).', 2, False, 'sự kiện dùng đồ'),
    'Big Pecks': ('Không bị giảm Defense và không bị trừ giáp.', 1, False, 'Fx_StageAdd + Ab_FxAdd'),
    'Magic Guard': ('Không mất máu vì bỏng, độc, thời tiết, phản dame, sát thương theo thời gian.', 3, False, 'nhiều chỗ gây sát thương gián tiếp'),
    'Hustle': ('+30% sát thương đòn đánh thường; 10% đòn đánh thường bị trượt.', 1, True, 'Ab_OutMult'),
    'Gluttony': ('Máu xuống dưới 50%: hồi ngay 10% máu tối đa (hồi 60 giây). Map không có Berry.', 1, True, 'Ab_Tick'),
    'Plus': ('Có hero đồng minh mang Plus hoặc Minus trong 600: +20% sát thương chiêu.', 1, False, 'Ab_OutMult'),
    'Minus': ('Có hero đồng minh mang Plus hoặc Minus trong 600: +20% sát thương chiêu.', 1, False, 'Ab_OutMult'),
    'Frisk': ('Hero địch trong 700 bị lộ, kể cả khi đang núp bụi cỏ.', 2, True, 'Ab_Tick + bụi cỏ'),
    'Stench': ('Đòn đánh và chiêu: 10% làm khựng 0,5 giây.', 1, False, 'Fx_AfterHit'),
    'Overcoat': ('Không mất máu vì bão cát / mưa đá; miễn chiêu dạng bột (Spore, Sleep Powder, Stun Spore, Poison Powder).', 2, False, 'thời tiết + move trạng thái'),
    'Tinted Lens': ('Chiêu bị kháng hệ gây sát thương như bình thường (x2 so với hiện tại).', 1, False, 'bảng khắc hệ'),
    'Hydration': ('Trời mưa: mỗi giây hết trạng thái xấu.', 1, False, 'Ab_Tick'),
    'Ice Body': ('Mưa đá: hồi 2% máu tối đa mỗi giây, không mất máu vì mưa đá.', 1, False, 'Ab_Tick'),
    'Contrary': ('Mọi thay đổi chỉ số bị đảo ngược (Leaf Storm, Overheat thành tăng Sp. Atk).', 1, False, 'Fx_StageAdd'),
    'Bulletproof': ('Miễn chiêu dạng cầu / bom (Shadow Ball, Sludge Bomb, Focus Blast, Energy Ball, Aura Sphere...).', 2, False, 'danh sách move'),
    'Magician': ('Chiêu trúng hero địch: 20% cướp 1 bậc chỉ số đang tăng của mục tiêu (hồi 8 giây).', 2, True, 'Fx_AfterHit + Fx_StageAdd'),
    'Protean': ('Mọi chiêu được tính như cùng hệ với Pokemon (thưởng cùng hệ cho mọi chiêu).', 2, True, 'chỗ tính thưởng cùng hệ'),
    'Galvanize': ('Chiêu hệ Normal thành hệ Electric và +20% sát thương (giống Aerilate / Pixilate đang có).', 1, False, 'Ab_OutMult (chép Pixilate)'),
    'Cloud Nine': ('Bản thân không chịu hiệu ứng thời tiết; hero địch trong 900 không nhận buff thời tiết (Swift Swim, Chlorophyll...).', 3, True, 'mọi chỗ đọc Wth_Cur'),
    'Healer': ('Mỗi 5 giây: 30% chữa trạng thái xấu cho 1 hero đồng minh trong 600.', 1, False, 'Ab_Tick'),
    'Rough Skin': ('Kẻ đánh cận chiến mất 4% máu tối đa của nó (Rocky Helmet là 3%).', 1, True, 'Ab_InContact'),
    'Own Tempo': ('Miễn rối và miễn Taunt.', 1, False, 'Fx_Confuse + Taunt'),
    'Cud Chew': ('Nhận hồi máu: 3 giây sau hồi thêm 50% lượng đó.', 3, True, 'hàm hồi máu chung'),
    'Sand Rush': ('Bão cát: +60 tốc chạy, +30% tốc đánh (giống Swift Swim trong mưa).', 1, True, 'Ab_Tick'),
    'Aftermath': ('Bị hạ gục: kẻ hạ gục mất 20% máu tối đa của Pokemon này.', 1, True, 'Fx_OnDeath'),
    'Quick Feet': ('Đang có trạng thái xấu: +50% tốc chạy.', 1, False, 'Ab_Tick'),
    'Marvel Scale': ('Đang có trạng thái xấu: +50% giáp.', 1, False, 'Ab_Tick'),
    'Sniper': ('Chí mạng gây x2,25 thay vì x1,5.', 1, False, 'chỗ tính chí mạng'),
    'Harvest': ('Mỗi 10 giây (nắng: 5 giây): 50% hồi 3% máu tối đa. Map không có Berry.', 1, True, 'Ab_Tick'),
    'Anticipation': ('Trúng chiêu siêu hiệu quả lần đầu mỗi 30 giây: đòn đó giảm 50% sát thương.', 1, True, 'Ab_InMult'),
    'Friend Guard': ('Hero đồng minh trong 600 nhận ít hơn 15% sát thương (không tính bản thân).', 2, True, 'Ab_InMult'),
    'Storm Drain': ('Miễn chiêu hệ Water; trúng chiêu Water: +1 Sp. Atk (12 giây).', 1, False, 'Ab_InMult (giống Water Absorb)'),
    'Poison Touch': ('Đòn đánh cận chiến: 30% gây độc.', 1, False, 'Ab_OnHit'),
    'Pickpocket': ('Bị hero địch đánh cận chiến: lấy 50 vàng của người chơi đó (hồi 15 giây).', 1, True, 'Ab_InContact'),
    'Slush Rush': ('Mưa đá: +60 tốc chạy, +30% tốc đánh.', 1, True, 'Ab_Tick'),
    'Unaware': ('Bỏ qua các bậc chỉ số của đối thủ khi đánh và khi bị đánh.', 2, False, 'Fx_StageMult'),
    'Imposter': ('Lần đầu đánh hero địch mỗi 60 giây: chép Attack / Sp. Atk / Defense / Sp. Def của nó trong 15 giây.', 3, True, 'hệ chỉ số'),
    'Dry Skin': ('Mưa: hồi 2% máu mỗi giây; miễn chiêu Water (hồi 25% máu thay vì mất); nhận thêm 25% sát thương hệ Fire.', 1, False, 'Ab_Tick + Ab_InMult'),
    'Drizzle': ('Gọi mưa như Drought gọi nắng (dùng lại code Drought).', 1, True, 'chép Drought'),
    'Prankster': ('Move trạng thái hồi chiêu nhanh hơn 50%.', 1, False, 'Fx_CdScale'),
    'Scrappy': ('Chiêu Normal / Fighting đánh trúng hệ Ghost bình thường; miễn Intimidate.', 1, False, 'bảng khắc hệ + Intimidate'),
    'Effect Spore': ('Bị đánh cận chiến: 30% kẻ đánh bị độc, tê liệt hoặc ngủ (ngẫu nhiên).', 1, False, 'Ab_InContact'),
}


def main():
    script_path, out_path = sys.argv[1], sys.argv[2]
    with open(script_path, 'rb') as fh:
        s = fh.read().decode('utf-8', 'replace')
    table = hidden_ability.ability_table(s)
    desc = {m.group(1): m.group(2) for m in re.finditer(r"SaveStr\(AbilityPatch_HT, '(\w{4})', 2, \"(.*?)\"\)", s)}
    with open(os.path.join(WORK, 'analysis', 'melee_ranged.json'), encoding='utf-8') as fh:
        names = {r['id']: r['name'] for r in json.load(fh)}
    for m in re.finditer(r"call SaveStr\(AbilityPatch_HT, '(\w{4})', 1,", s):
        names.setdefault(m.group(1), m.group(1))
    groups = {}
    for uid, (name, num) in table.items():
        if not num:
            groups.setdefault(name, []).append(uid)
    missing = sorted(set(groups) - set(PLAN))
    if missing:
        raise SystemExit('no plan for: %s' % missing)
    out = []
    for name, uids in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        effect, diff, differs, hook = PLAN[name]
        texts = sorted({desc.get(u, '') for u in uids}, key=len, reverse=True)
        # Mega / form units (hM.., hZ..) use their own Ability in Ab_Want, so only base Pokemon are listed
        base = [u for u in uids if not u.startswith('h')]
        out.append({'name': name, 'count': len(base), 'mega_forms': len(uids) - len(base),
                    'pokemon': sorted({names.get(u, u) for u in base}),
                    'map_text': texts[0] if texts else '', 'effect': effect, 'difficulty': diff,
                    'differs': differs, 'hook': hook})
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(len(out), 'abilities,', sum(e['count'] for e in out), 'Pokemon')


if __name__ == '__main__':
    main()
