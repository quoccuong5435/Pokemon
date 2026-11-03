"""List of every playable Pokemon (v1.8 heroes + new forms + Celebi) with type, Ability and moves.
Output: analysis/playable_full_list.md (moves = level-up candidates with the hero level they are available at, TM = number of
damaging TM/HM moves the species can buy at the NPC for 3000 gold)."""
import io
import sys

sys.path.insert(0, 'tools')
import ability_data as ad  # noqa: E402
import learn_data as ld  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402
import poke_data as pd  # noqa: E402
import type_taverns as tt  # noqa: E402

v18 = mpq.MPQ('../Pokemon Arena v1.8.w3x')
w3u = objdata.ObjFile(v18.read('war3map.w3u'))
rows = []  # (group, name, unit id, type label)
for o in w3u.custom:
    if o.new[:1] == 'E' and o.get('upro'):
        rows.append(('v1.8 (map goc)', o.get('upro'), o.new, o.get('unam') or ''))
for f in pd.FORMS:
    label = pd.KIT_TYPES[f.kit] if f.kit in pd.KIT_TYPES else tt.type_label(f.name)
    rows.append(('Dang moi (tavern theo he / tien hoa)', f.name, f.id, label))
rows.append(('Dang moi (tavern theo he / tien hoa)', 'Celebi', pd.CELEBI_HERO, 'Psychic&Grass Pokemon'))

out = ['# Danh sach Pokemon playable: he, ability, skill', '',
       'Moi dong: ten (id unit) | he | Ability | chieu hoc theo level (level hero co the hoc) | so TM/HM co the mua (3000 vang).', '']
current = None
n = 0
for group, name, uid, label in sorted(rows, key=lambda r: (r[0], r[1].lower())):
    if group != current:
        current = group
        out += ['', '## ' + group, '']
    slug = ld.slug(name)
    cands = ld.candidates(slug)
    moves = ', '.join('%s (Lv %d)' % (ld.MOVES[m]['name'], lv) for lv, m in cands) or '(khong co chieu level-up co sat thuong)'
    tms = len(ld.tm_candidates(slug))
    key = ad.ability_key_for(name)
    ability = key or '(chua co)'
    typ = label.replace(' Pokemon', '')
    out.append('- **%s** (`%s`) | %s | %s | %s | TM: %d' % (name, uid, typ, ability, moves, tms))
    n += 1
out += ['', 'Tong: %d Pokemon playable (cac dang tien hoa co trong danh sach, chi dang goc co trong menu tavern).' % n]
io.open('analysis/playable_full_list.md', 'w', encoding='utf-8', newline='').write(chr(10).join(out) + chr(10))
print('rows', n)
