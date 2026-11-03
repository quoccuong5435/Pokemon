"""Build analysis/patchnote/index.html: patch note + searchable Pokemon table (sprites, type icons, ability, moves, TM)."""
import base64, html, json, os, re, io
ICON = {'Normal':'Thuong','Fire':'Lua','Water':'Nuoc','Grass':'Co','Electric':'Dien','Ice':'Bang','Fighting':'Giacdau','Poison':'Doc','Ground':'Dat','Flying':'Bay','Psychic':'Sieulinh','Bug':'Contrung','Rock':'Da','Ghost':'Ma','Dragon':'Rong','Dark':'Bongtoi','Steel':'Thep','Fairy':'Tien'}
icons = {t: base64.b64encode(open('type_icons_fandom/%s.webp' % f, 'rb').read()).decode() for t, f in ICON.items()}
rows = []
group = ''
for line in io.open('playable_full_list.md', encoding='utf-8'):
    if line.startswith('## '):
        group = line[3:].strip()
    m = re.match(r'- \*\*(.+?)\*\* \(`(.+?)`\) \| (.*?) \| (.*?) \| (.*) \| TM: (\d+)', line)
    if m:
        n, uid, typ, ab, mv, tm = m.groups()
        moves = [x.strip() for x in re.findall(r'[^,]+? \(Lv \d+\)', mv)]
        rows.append(dict(n=n, id=uid, t=[x for x in typ.split('&')], a=ab, m=moves, tm=int(tm), g=group))
def slug(n):
    s = n.lower().replace("'", '').replace('.', '').replace(' ', '-')
    for pre, suf in (('alolan-', '-alolan'), ('galarian-', '-galarian'), ('hisuian-', '-hisui'), ('paldean-', '-paldean')):
        if s.startswith(pre): s = s[len(pre):] + suf
    return s
import sys
sys.path.insert(0, '../tools')
import poke_data
_by = {f.name: f for f in poke_data.FORMS}
for r in rows:
    r['s'] = slug(r['n'])
    f = _by.get(r['n'])
    r['e'] = ''
    if f and f.evolves_to:
        r['e'] = '%s (Lv %d)' % (poke_data.FORM_BY_ID[f.evolves_to].name, f.level)
import sys
sys.path.insert(0, '../tools')
import mega_data
def mslug(name):
    p = name.replace('Mega ', '').lower().split()
    return p[0] + '-mega' + ('-' + p[1] if len(p) > 1 else '')
MEGAS = [dict(n=m.name, s=mslug(m.name), base=m.base_name, stone=m.stone_name, price=m.price, st=[m.str_, m.agi, m.int_]) for m in mega_data.MEGAS]
PATCH = [
 ('Chọn Pokémon', ['Một nhà "Pokemon List" ở chỗ wisp: bấm vào để chọn hệ rồi chọn Pokémon (thay các tavern theo hệ).', 'Danh sách và -random chỉ còn form 1; thêm 7 form 1: Eevee, Magnemite, Magneton, Poliwag, Poliwhirl, Rhyhorn, Rhydon.', 'Mỗi Pokémon hiện level tiến hóa (xem bên dưới).']),
 ('Soul', ['Soul cho form 1; sau khi dùng Soul, Pokémon chỉ tiến hóa ở lần lên level kế tiếp (không tiến hóa ngay).', 'Icon Soul là sprite của đúng loài.']),
 ('Chiêu thức', ['Sửa lỗi bấm skill này ra skill khác (mỗi ô Q W E R có order riêng).', 'Mô tả skill hiện sát thương theo chỉ số chính và level hiện tại (màu xanh).', 'Hệ số skill: tối đa x5 (mỗi điểm chỉ số chính 0,05), thêm 0,02 mỗi level trên 50. Đòn đánh thường x1,8.']),
 ('Gym, huy hiệu, level cap', ['Gym 2 đến 8 kích hoạt từ cửa (vùng 900); mỗi gym là 6 Pokémon khác loài (chỉ loài cầm được item), mỗi con cầm item hệ và rớt khi chết. Level 6 con: thấp hơn bạn 30, 25, 20, 15, 10 level rồi bằng bạn; dame gym -20%.', 'Mỗi huy hiệu gym mang theo cộng Str/Agi/Int: +5 x số thứ tự gym (huy hiệu 8: +40, đủ 8 huy hiệu: +180).', 'Clear gym nhận huy hiệu. Level cap = 30 + 10 mỗi huy hiệu (tối đa 100); đạt cap thì ngừng nhận exp. Gõ -badges / -rank để xem.']),
 ('Duel', ['-duel <tên> thách đấu, người kia gõ -accept hoặc -decline. Hồi đầy máu, thua khi dưới 15% máu, hòa sau 2 phút.', 'Thắng nhận 500 vàng, tính vào -rank.']),
 ('Quái hoang dã & legend', ['Quái hoang dã dame x0,5, hồi sinh trại 10 giây, elite rớt Soul 20%.', 'Legend spawn 3 con mỗi lần.', 'Lệnh chicken: +10 level và +10.000 vàng.']),
]
page = '''<!doctype html><html lang="vi"><meta charset="utf-8"><title>Pokemon Arena - Patch Note</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#12151c;color:#e6e8ee}
header{padding:24px 32px;background:linear-gradient(90deg,#c0392b,#8e44ad)}h1{margin:0}
main{max-width:1200px;margin:auto;padding:16px 24px}
.pn{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.pn div{background:#1d222d;border-radius:10px;padding:12px 16px}.pn h3{margin:0 0 6px;color:#ffd166}.pn li{margin:4px 0;font-size:14px}
#bar{position:sticky;top:0;background:#12151c;padding:10px 0;z-index:2;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input,select{padding:8px 10px;border-radius:8px;border:1px solid #333;background:#1d222d;color:#fff;font-size:14px}input{flex:1;min-width:200px}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.c{background:#1d222d;border-radius:10px;padding:12px;display:flex;gap:10px}
.c img.s{width:80px;height:80px;object-fit:contain;background:#12151c;border-radius:8px;flex:none}
.c h4{margin:0 0 4px}.c small{color:#8a93a6}.ty img{width:22px;height:22px;vertical-align:middle;margin-right:3px}
.ab{color:#7bdff2;font-size:13px}.mv{font-size:12px;color:#c5cad6;margin-top:4px;max-height:84px;overflow:auto}
.tm{font-size:12px;color:#ffd166}
</style><header><h1>Pokemon Arena - Patch Note v3.2.15</h1><div>Tìm Pokémon theo tên, hệ, ability hoặc chiêu</div></header><main>
<h2>Thay đổi</h2><div class="pn">%PN%</div>
<h2>Mega Evolution (%NM%)</h2><p>Mua đá Mega ở shop, giữ trong túi: Mega kéo dài %DUR% giây, hồi %CD% giây. Chỉ số Mega cộng thêm %ATTR%% mỗi điểm.</p><div id="mega"></div>
<h2>Pokémon playable (<span id="cnt"></span>)</h2>
<div id="bar"><input id="q" placeholder="Tìm: tên / ability / chiêu..."><select id="t"><option value="">Mọi hệ</option>%OPT%</select></div>
<div id="grid"></div></main>
<script>
const M=%MEGAS%,D=%DATA%,I=%ICONS%;
function show(){const q=document.getElementById('q').value.toLowerCase(),t=document.getElementById('t').value;
const r=D.filter(p=>(!t||p.t.includes(t))&&(!q||(p.n+' '+p.a+' '+p.m.join(' ')+' '+p.t.join(' ')).toLowerCase().includes(q)));
document.getElementById('cnt').textContent=r.length;
document.getElementById('grid').innerHTML=r.map(p=>`<div class="c"><img class="s" loading="lazy" src="https://img.pokemondb.net/sprites/home/normal/${p.s}.png" onerror="this.style.visibility='hidden'">
<div><h4>${p.n} <small>${p.id}</small></h4><div class="ty">${p.t.map(x=>`<img title="${x}" src="data:image/webp;base64,${I[x]||''}">`).join('')}${p.t.join(' / ')}</div>
<div class="ab">Ability: ${p.a}</div><div class="tm">TM/HM: ${p.tm}</div>${p.e?`<div class="ab">Tiến hóa: ${p.e}</div>`:''}<div class="mv">${p.m.join(' · ')}</div></div></div>`).join('')}
document.getElementById('mega').innerHTML='<div id="grid">'+M.map(p=>`<div class="c"><img class="s" loading="lazy" src="https://img.pokemondb.net/sprites/home/normal/${p.s}.png" onerror="this.style.visibility='hidden'"><div><h4>${p.n}</h4><div class="ab">Từ: ${p.base}</div><div class="tm">Đá: ${p.stone} - ${p.price} vàng</div><div class="mv">STR +${p.st[0]} · AGI +${p.st[1]} · INT +${p.st[2]}</div></div></div>`).join('')+'</div>';
document.getElementById('q').oninput=show;document.getElementById('t').onchange=show;show();
</script></html>'''
pn = ''.join('<div><h3>%s</h3><ul>%s</ul></div>' % (html.escape(h), ''.join('<li>%s</li>' % html.escape(x) for x in items)) for h, items in PATCH)
opt = ''.join('<option>%s</option>' % t for t in ICON)
os.makedirs('patchnote', exist_ok=True)
out = page.replace('%PN%', pn).replace('%OPT%', opt).replace('%MEGAS%', json.dumps(MEGAS, ensure_ascii=False)).replace('%NM%', str(len(MEGAS))).replace('%DUR%', str(int(mega_data.DURATION))).replace('%CD%', str(int(mega_data.COOLDOWN))).replace('%ATTR%', str(mega_data.ATTR_PCT_PER_POINT)).replace('%DATA%', json.dumps(rows, ensure_ascii=False)).replace('%ICONS%', json.dumps(icons))
io.open('patchnote/index.html', 'w', encoding='utf-8').write(out)
print(len(rows), 'pokemon', len(out) // 1024, 'KB')
