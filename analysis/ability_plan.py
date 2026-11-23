"""Full Ability plan for the 4.2x map: every real Ability (default + hidden) of the 360 heroes, from PokeAPI.

Usage (from _PokemonArena2.0_work):
  python -I analysis/ability_plan.py analysis/jass_ref/_tmp_v42a_war3map.j analysis/ability_plan.json
Output: {"abilities": [...], "heroes": [...], "summary": {...}}
- abilities: name, status ("code" = the map already runs it for any Pokemon, "new" = to write), effect (map tooltip for
  "code", proposal for "new"), difficulty / differs / hook for "new", Pokemon that have it as default or hidden.
- heroes: id, name, default Ability now, proposed default (current one if it is a real one, else the species' first
  real default Ability), real default Abilities, Hidden Ability (map table = PokeAPI hidden one).
The 25 legends that use the legend system (no Ab_HT key 0) keep their legend powers and are listed as such.
"""
import json
import os
import re
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'analysis'))
sys.path.insert(0, os.path.join(WORK, 'tools', 'v412'))
from hidden_ability_plan import PLAN as HIDDEN_PLAN  # noqa: E402
from ability_rating import RATING  # noqa: E402

# default Abilities with no code that are not in HIDDEN_PLAN: (effect, difficulty, differs from canon, hook)
DEFAULT_PLAN = {
    'Oblivious': ('Miễn Taunt và Intimidate.', 1, False, 'Taunt + Fx_IntimidateX'),
    'Illuminate': ('Không bị giảm chính xác (Accuracy down).', 1, True, 'Fx_AccDown'),
    'Forewarn': ('Chiêu đầu tiên trúng nó sau 10 giây không giao tranh giảm 40% sát thương.', 1, True, 'Ab_InMult'),
    'Tangled Feet': ('Đang bị rối: né 50% đòn đánh thường.', 1, False, 'Ab_InMult'),
    'Limber': ('Miễn tê liệt.', 1, False, 'Fx_Status'),
    'Rivalry': ('+15% sát thương lên hero địch (map không có giới tính).', 1, True, 'Ab_OutMult'),
    'Arena Trap': ('Hero địch không phải hệ Flying trong 400 bị chậm 15%.', 2, True, 'Ab_Tick + Ab_FxAdd'),
    'Liquid Ooze': ('Kẻ dùng chiêu hút máu đánh nó mất lượng máu đáng lẽ được hồi.', 2, False, 'chỗ hút máu của move'),
    'Neutralizing Gas': ('Hero địch trong 600 mất tác dụng ability (khóa ability đang có sẵn trong map).', 1, False, 'Ab_Tick + khóa ability (Ab_HT 77)'),
    'Shield Dust': ('Miễn hiệu ứng phụ của chiêu gây sát thương (trạng thái, giảm chỉ số, khựng, rối).', 1, False, 'Fx_AfterHit'),
    'Filter': ('Chiêu siêu hiệu quả trúng nó giảm 25% sát thương.', 1, False, 'Ab_InMult'),
    'Solid Rock': ('Chiêu siêu hiệu quả trúng nó giảm 25% sát thương.', 1, False, 'Ab_InMult'),
    'Snow Warning': ('Gọi mưa đá như Drought gọi nắng (dùng lại code Drought).', 1, False, 'chép Drought'),
    'Poison Heal': ('Đang bị độc: hồi 3% máu tối đa mỗi giây thay vì mất máu.', 2, False, 'chỗ trừ máu vì độc'),
    'Suction Cups': ('Không bị đẩy lùi.', 1, False, 'chỗ đẩy lùi'),
    'Magma Armor': ('Miễn đóng băng.', 1, False, 'Fx_Status'),
    'Download': ('+15% sát thương chiêu nếu chiêu đánh vào chỉ số phòng thủ thấp hơn của mục tiêu.', 1, True, 'Ab_OutMult + Fx_DefOf'),
    'Cursed Body': ('Trúng chiêu: 30% kẻ đánh bị khóa chiêu 3 giây.', 1, True, 'Fx_AfterHit + silence'),
    'Sharpness': ('Chiêu chém (Slash, Cut, X-Scissor, Leaf Blade, Night Slash, Psycho Cut, Air Slash, Sacred Sword...) +50% sát thương.', 2, False, 'danh sách move'),
    'Beast Boost': ('Hạ gục hero, tinh anh hoặc boss: +1 chỉ số cao nhất (30 giây).', 1, False, 'Fx_OnDeath'),
    'Stance Change': ('Vừa ra chiêu: +30% sát thương chiêu, nhận thêm 15% sát thương trong 4 giây; lúc khác nhận ít hơn 20% sát thương.', 2, True, 'Ab_OutMult + Ab_InMult'),
    'Surge Surfer': ('Trời mưa: +60 tốc chạy.', 1, True, 'Ab_Tick'),
    'Motor Drive': ('Miễn chiêu Electric; trúng chiêu Electric: +1 Speed (12 giây).', 1, False, 'Ab_Absorbs'),
    'Supreme Overlord': ('+5% sát thương cho mỗi hero đồng minh đang chết (tối đa +25%).', 1, False, 'Ab_OutMult'),
    'Pickup': ('Hạ quái: 10% nhận thêm 20 vàng.', 1, True, 'Fx_OnDeath'),
    'Stall': ('Nhận ít hơn 10% sát thương; tốc đánh chậm hơn 10%.', 1, True, 'Ab_InMult + tốc đánh'),
    'Wonder Guard': ('Chiêu không siêu hiệu quả và đòn đánh thường chỉ gây 50% sát thương lên nó.', 1, True, 'Ab_InMult'),
    'Immunity': ('Miễn độc.', 1, False, 'Fx_Status'),
    'White Smoke': ('Không bị đối thủ giảm chỉ số.', 1, False, 'Fx_StageAdd'),
}
PLAN = dict(HIDDEN_PLAN)
PLAN.update(DEFAULT_PLAN)
EXTRA_SLUG = {'latias & latios': 'latias', 'zygarde': 'zygarde-50', 'mr. mime': 'mr-mime'}


def slug(n):
    return re.sub(r'[^a-z0-9]+', '-', n.lower().replace("'", '')).strip('-')


def main():
    script_path, out_path = sys.argv[1], sys.argv[2]
    with open(script_path, 'rb') as fh:
        s = fh.read().decode('utf-8', 'replace')
    j = lambda *p: json.load(open(os.path.join(WORK, *p), encoding='utf-8'))  # noqa: E731
    api_ab, poke_ab = j('tools', 'pokeapi', 'abilities.json'), j('tools', 'pokeapi', 'pokemon_abilities.json')
    roster, learn = j('analysis', 'melee_ranged.json'), j('tools', 'learnsets.json')['species']

    consts = {m.group(1): int(m.group(2)) for m in re.finditer(r'constant integer (AB_[A-Z0-9_]+) = (\d+)', s)}
    used = {v for k, v in consts.items() if len(re.findall(r'\b%s\b' % k, s)) > 1}
    index, info = {}, {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', s):
        index.setdefault(m.group(2), int(m.group(1)))
    for m in re.finditer(r'set Ab_Info\[(\d+)\] = "(.*?)"\s*$', s, re.M):
        info[int(m.group(1))] = m.group(2)  # later lines win (v3.4.11 rewrites)
    coded = {slug(n): (n, i) for n, i in index.items() if i in used}
    who = {m.group(1): int(m.group(2)) for m in re.finditer(r"call SaveInteger\(Ab_HT, '(\w{4})', 0, (\d+)\)", s)}
    num_name = {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', s):
        num_name.setdefault(int(m.group(1)), m.group(2))
    by_name = {sp['name'].lower(): k for k, sp in learn.items()}

    heroes, ab_use = [], {}
    for r in roster:
        sp = by_name.get(r['name'].lower()) or EXTRA_SLUG.get(r['name'].lower()) or slug(r['name'])
        real = poke_ab.get(sp, [])
        normal = [a for a, h in real if not h]
        hidden = [a for a, h in real if h]
        cur_num = who.get(r['id'], 0)
        cur = num_name.get(cur_num)
        # legends: no Ability line, or an Ability that only legend code runs (Pressure of legends, Drizzle ...)
        legend = r['id'] not in who or (cur_num > 0 and cur_num not in used)
        if legend:
            new = None
        elif cur and slug(cur) in normal:
            new = slug(cur)
        else:
            with_code = [a for a in normal if a in coded]
            new = (with_code or normal or [slug(cur) if cur else None])[0]
        for a in ([new] if new else []):
            ab_use.setdefault(a, {'default': [], 'hidden': []})['default'].append(r['name'])
        for a in hidden:
            if not legend:
                ab_use.setdefault(a, {'default': [], 'hidden': []})['hidden'].append(r['name'])
        heroes.append({'id': r['id'], 'name': r['name'], 'legend': legend, 'now': cur,
                       'new': (api_ab.get(new, {}).get('name') if new else None) or new,
                       'changed': bool(new) and (not cur or slug(cur) != new),
                       'normal': [api_ab.get(a, {}).get('name', a) for a in normal],
                       'hidden': [api_ab.get(a, {}).get('name', a) for a in hidden]})

    abilities, missing = [], []
    for a, use in ab_use.items():
        name = api_ab.get(a, {}).get('name') or a
        rec = {'name': name, 'default': sorted(set(use['default'])), 'hidden': sorted(set(use['hidden'])),
               'pokeapi': api_ab.get(a, {}).get('short_effect', '')}
        if a in coded and a not in ('regenerator', 'drizzle', 'beast-boost'):
            rec.update(status='code', effect=info.get(coded[a][1], ''))
        elif name in PLAN:
            eff, diff, differs, hook = PLAN[name]
            rec.update(status='new', effect=eff, difficulty=diff, differs=differs, hook=hook)
        else:
            missing.append(name)
            continue
        if name not in RATING:
            missing.append(name + ' (rating)')
            continue
        rec['tier'], rec['suggest'], rec['why'] = RATING[name]
        abilities.append(rec)
    if missing:
        raise SystemExit('no plan for: %s' % sorted(missing))
    abilities.sort(key=lambda e: (e['status'] != 'new', -(len(e['default']) + len(e['hidden'])), e['name']))
    summary = {
        'abilities': len(abilities), 'with_code': sum(e['status'] == 'code' for e in abilities),
        'new': sum(e['status'] == 'new' for e in abilities),
        'heroes': len(heroes), 'legend_system': sum(h['legend'] for h in heroes),
        'default_changed': sum(h['changed'] for h in heroes),
    }
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump({'abilities': abilities, 'heroes': heroes, 'summary': summary}, fh, ensure_ascii=False, indent=1)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
