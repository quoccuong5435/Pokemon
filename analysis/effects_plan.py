"""Read-only: proposal of new move effects from PKLegends v3.2 (docs/v3.4/6-de-xuat-hieu-ung-chieu.md).
Contact moves (punch, bite, claw, tail, tackle ...) that are flying projectiles today become melee hits; ranged moves
get a projectile of their type; area moves an area effect.

python -I analysis/effects_plan.py ["../Pokemon Arena v3.4.1.w3x"]
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, 'tools'))
import mpq  # noqa: E402
import slk  # noqa: E402

MAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(WORK), 'Pokemon Arena v3.4.1.w3x')
BASE_NAME = {'AHtb': 'Storm Bolt', 'AEsh': 'Shadow Strike', 'AUfn': 'Frost Nova', 'AUcs': 'Carrion Swarm',
             'AOsh': 'Shockwave', 'AHtc': 'Thunder Clap', 'AOws': 'War Stomp', 'ANbf': 'Breath of Fire',
             'AEer': 'Entangling Roots', 'AUim': 'Impale', 'AHbz': 'Blizzard'}
PROJECTILE_BASES = {'AHtb', 'AEsh', 'AUcs', 'AOsh'}   # a missile flies to the target / along a line
CONTACT = (r'punch|kick|chop|fist|jab|slam|tackle|headbutt|head smash|bite|fang|crunch|claw|slash|cut|scratch|tail|'
           r'horn|wing attack|peck|strike|smash|hammer|body press|take down|double.edge|close combat|cross chop|'
           r'brick break|dynamic|mach|x-scissor|fury|leaf blade|night slash|sacred sword|giga impact|quick attack|'
           r'extreme speed|play rough|iron head|zen headbutt|wild charge|volt tackle|flare blitz|brave bird|aqua jet|'
           r'waterfall|dragon rush|outrage|superpower|crabhammer|seismic toss|submission|rapid spin|u-turn|'
           r'acrobatics|aerial ace|pound|covet|facade|return|retaliate|revenge|reversal|counter|first impression|'
           r'lunge|leech life|lash out|knock off|payback|assurance|sucker punch|foul play|throat chop|sky uppercut|'
           r'low sweep|meteor mash|bullet|smart strike|power whip|wood hammer|horn leech|trailblaze|steel wing|'
           r'drill run|dig|bone|stomp|bulldoze|rock smash|force palm|body slam|raging bull|flip turn|liquidation|'
           r'psychic fangs|poison jab|cross poison|shadow sneak|phantom force|dual chop|breaking swipe|spirit break')
# melee hit effects (PKLegends models)
MELEE = [
    (r'claw|slash|cut|scratch|leaf blade|night slash|sacred sword|x-scissor|fury|smart strike|cross poison|dual chop|'
     r'breaking swipe', None),   # decided below by type
    (r'close combat|giga impact|superpower|head smash|outrage|dragon rush|flare blitz|brave bird|volt tackle|'
     r'wood hammer|meteor mash|hammer|crabhammer|spirit break', 'Coup de Grace Purple'),
    (r'quick attack|extreme speed|aqua jet|u-turn|flip turn|acrobatics|aerial ace|first impression|sucker punch|'
     r'shadow sneak|feint', 'Blitzangriff'),
    (r'thunder|volt|wild charge|spark|plasma', 'galvanattack'),
    (r'power whip|vine|horn leech|trailblaze', 'Powerwhip'),
    (r'bone|dig|drill run|bulldoze|stomp', 'WarStompCaster'),
]
CLAW_BY_TYPE = {'Ghost': 'purple claw', 'Dark': 'purple claw', 'Dragon': 'purple claw', 'Poison': 'purple claw',
                'Psychic': 'Zornklinge', 'Bug': 'Zornklinge', 'Steel': 'Zornklinge'}
DEFAULT_MELEE = 'AnimatedBash'        # punch, kick, tackle, bite ...
# projectiles by type (power picks Minor / Medium / Major for Fire and Dark)
PROJ = {'Fire': ['Ember', 'Firebolt Minor', 'Firebolt Medium', 'Firebolt Major'], 'Water': ['Water Shot'],
        'Ice': ['Icebeam'], 'Psychic': ['Psionic Shot Teal', 'Arcade Bolt Psyche'], 'Ghost': ['Spectral Missile'],
        'Dark': ['Voidball Minor', 'Voidbolt Medium', 'Voidbolt Major'], 'Flying': ['FeatherMissile'],
        'Fairy': ['Faerie Missile'], 'Normal': ['Sonic Missile'], 'Grass': ['GreenShot'],
        'Electric': ['blue energy arrow'], 'Rock': ['GolemAlolanProjectile4'], 'Ground': ['boomerrangbone'],
        'Dragon': ['Voidbolt Major'], 'Poison': ['GreenShot'], 'Steel': ['Psionic Shot Silver'],
        'Fighting': ['Holy Missile'], 'Bug': ['Wizardry Missile']}
AREA = {'Poison': 'GreenBoom', 'Grass': 'Tangroots', 'Psychic': 'VioletPulse', 'Ghost': 'VioletPulse',
        'Ground': 'WarStompCaster', 'Rock': 'WarStompCaster', 'Electric': 'SS2 Lightning', 'Flying': 'Stormfall',
        'Fairy': 'VioletPulse'}
SPECIAL_NAMES = {'Ice Beam': 'Icebeam', 'Aurora Beam': 'Icebeam', 'Tri Attack': 'Digital Ray', 'Signal Beam': 'Digital Ray',
                 'Psybeam': 'Arcade Bolt Psyche', 'Hurricane': 'Stormfall', 'Thunder': 'Stormfall',
                 'Sandstorm': 'SandTornado', 'Razor Leaf': 'RazorLeafSelf', 'Bonemerang': 'boomerrangbone',
                 'Bone Rush': 'boomerrangbone', 'Ember': 'Ember', 'Water Gun': 'Water Shot'}

a = mpq.MPQ(MAP)
script = a.read('scripts\\war3map.j' if a.has('scripts\\war3map.j') else 'war3map.j').decode('utf-8', 'replace')
abil = slk.Slk(a.read('Units\\AbilityData.slk').decode('latin-1'))
cx, rx = abil.name_to_x['code'], abil.name_to_x.get('Rng1')
strings = a.read('Units\\CampaignAbilityStrings.txt').decode('utf-8', 'replace')
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
labels = dict((int(i), v) for i, v in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script))
texts = dict((int(i), v) for i, v in re.findall(r'set Mv_Text\[(\d+)\] = "([^"]*)"', script))


def art(aid):
    m = re.search(r'\[%s\]\r?\n(.*?)(?=\r?\n\[|\Z)' % aid, strings, re.S)
    d = dict(re.findall(r'(?m)^(\w+)=([^\r\n]*)', m.group(1))) if m else {}
    p = d.get('Missileart') or d.get('Effectart') or d.get('Targetart') or d.get('Casterart') or ''
    return re.sub(r'\.md[lx]$', '', p.replace('/', '\\').split('\\')[-1], flags=re.I)


rows, models = [], {}
for m in sorted(labels):
    mm = re.match(r'(.*?) \((\w+), power (\d+)\)', labels[m])
    name, ty, pw = (mm.group(1), mm.group(2), int(mm.group(3))) if mm else (labels[m], 'Normal', 0)
    aid = 'AV' + B36[m // 36] + B36[m % 36]
    row = abil.find(aid) or {}
    code = row.get(cx, '').strip('"')
    rng = row.get(rx, '') if rx else ''
    phys = 'Physical move' in texts.get(m, '')
    now = '%s, %s, tầm %s' % (BASE_NAME.get(code, code), art(aid) or 'hiệu ứng gốc', rng)
    low = name.lower()
    if phys and code in PROJECTILE_BASES and re.search(CONTACT, low):
        eff = None
        for rx_, md in MELEE:
            if re.search(rx_, low):
                eff = md or CLAW_BY_TYPE.get(ty, 'slash-luc')
                break
        eff = eff or (CLAW_BY_TYPE.get(ty, 'slash-luc') if re.search(r'claw|slash|cut', low) else DEFAULT_MELEE)
        new = 'Cận chiến (tầm 150, không đạn): %s trên mục tiêu' % eff
        kind = 'melee'
    elif name in SPECIAL_NAMES:
        eff = SPECIAL_NAMES[name]
        new = 'Hiệu ứng riêng: %s' % eff
        kind = 'special'
    elif code in PROJECTILE_BASES:
        lst = PROJ.get(ty, ['Sonic Missile'])
        eff = lst[min(len(lst) - 1, (pw - 1) // 40)] if len(lst) > 1 else lst[0]
        new = 'Đạn hệ %s: %s' % (ty, eff)
        kind = 'projectile'
    elif code in ('AHtc', 'AOws', 'AUfn', 'AHbz', 'ANbf', 'AEer', 'AUim') and ty in AREA:
        eff = AREA[ty]
        new = 'Diện rộng: %s' % eff
        kind = 'area'
    else:
        eff, new, kind = '', 'Giữ nguyên', 'keep'
    if eff:
        models[eff] = models.get(eff, 0) + 1
    rows.append((m, name, ty, 'Vật lý' if phys else 'Đặc biệt', pw, now, new, kind))

count = {}
for r in rows:
    count[r[7]] = count.get(r[7], 0) + 1
lines = ['# 6. Đề xuất: hiệu ứng move mới từ PKLegends v3.2 (chờ duyệt)', '',
         'Ngày 2026-11-08. Chưa sửa code phần này.', '',
         '## Vì sao',
         '- Mọi move đánh một mục tiêu hiện là **đạn bay**, kể cả chiêu cận chiến như Iron Tail, Dragon Claw, Crunch, '
         'Close Combat. Lý do: v3.1 dựng chúng từ Storm Bolt / Shadow Strike (ném) và Shockwave / Carrion Swarm (sóng).',
         '- Hình đạn hiện chỉ đổi theo hệ, dùng model có sẵn của game.', '',
         '## Nguồn hiệu ứng',
         '- **PKLegends v3.2** (đã có trên máy, map Pokémon, file mở được): khoảng 80 model hiệu ứng riêng.',
         '  - chém / vuốt: `slash-luc`, `purple claw`, `Zornklinge`, `Coup de Grace Purple`;',
         '  - đánh / đấm: `AnimatedBash`, `hitvfx1`; lao tới: `Blitzangriff`; điện: `galvanattack`;',
         '  - đạn theo hệ: `Ember`, `Firebolt`, `Water Shot`, `Icebeam`, `Psionic Shot`, `Spectral Missile`, `Voidbolt`, '
         '`FeatherMissile`, `Faerie Missile`, `Sonic Missile`, `GreenShot`, `boomerrangbone`…;',
         '  - diện rộng: `GreenBoom`, `VioletPulse`, `SandTornado`, `Stormfall`, `Tangroots`, `SS2 Lightning`.',
         '- **79.PokemonRPG.w3x**: map có nhắc tới 293 model nhưng file bị khóa, không lấy được.',
         '- **Hive Workshop** (trên mạng, miễn phí): còn nhiều hiệu ứng chém / đấm / nổ đẹp hơn. Nếu muốn dùng thì mình gửi '
         'link từng file và hỏi bạn trước khi tải.', '',
         '## Đề xuất',
         '- **Cận chiến** (%d move vật lý chạm người): tầm 150 (phải đứng sát), không có đạn bay, hiệu ứng chém / đấm '
         'hiện ngay trên mục tiêu. Sát thương, hồi chiêu và hiệu ứng phụ (choáng, độc…) giữ nguyên.' % count.get('melee', 0),
         '- **Đạn theo hệ** (%d move): đạn bay lấy model của PKL theo hệ; với Fire và Dark, Power càng cao đạn càng to '
         '(Minor / Medium / Major).' % count.get('projectile', 0),
         '- **Diện rộng** (%d move): hiệu ứng nổ / sóng theo hệ.' % count.get('area', 0),
         '- **Hiệu ứng riêng theo tên** (%d move): Ice Beam (tia băng), Tri Attack (tia số), Hurricane / Thunder '
         '(bão), Razor Leaf, Bonemerang…' % count.get('special', 0),
         '- **Giữ nguyên**: %d move.' % count.get('keep', 0),
         '- Dung lượng thêm: khoảng 1,5 MB (%d model).' % len(models), '',
         '## Model sẽ dùng (số move dùng)', '',
         ', '.join('`%s` (%d)' % (k, v) for k, v in sorted(models.items(), key=lambda kv: -kv[1])), '',
         '## Từng move', '', '| # | Move | Hệ | Loại | Power | Hiện tại (skill gốc, hiệu ứng, tầm) | Đề xuất |',
         '|---|---|---|---|---|---|---|']
for m, name, ty, cls, pw, now, new, _k in rows:
    lines.append('| %d | %s | %s | %s | %d | %s | %s |' % (m, name, ty, cls, pw, now, new))
out = os.path.join(WORK, 'docs', 'v3.4', '6-de-xuat-hieu-ung-chieu.md')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote', out, count, len(models), 'models')
