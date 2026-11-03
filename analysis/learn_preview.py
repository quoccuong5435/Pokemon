"""Write docs/pokemon-learned-moves-proposal.md: the moves every Pokemon of the map can learn (from tools/learn_data.py).

Usage (from _PokemonArena2.0_work):  python -I analysis/learn_preview.py docs/pokemon-learned-moves-proposal.md
"""
import os
import sys

sys.path.insert(0, 'tools')
import learn_data as ld  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402


def main(path, map_path):
    w3u = objdata.ObjFile(mpq.MPQ(map_path).read('war3map.w3u'))
    units = ld.hero_species(w3u)
    plan = ld.build_plan(units)
    out = ['# Move học theo level (đã làm trong bản 3.0)', '',
           'Quy tắc: mỗi Pokemon có tối đa %d ô move mới (hàng trên cùng của bảng lệnh, phím Z X C V), 5 skill cũ giữ nguyên.' % ld.SLOTS,
           'Mỗi loài có tối đa %d move sát thương mạnh nhất (sức mạnh x độ chính xác) trong danh sách move thật của game gốc.' % ld.CAND_MAX,
           'Move mở ở level thật của nó, nhưng không sớm hơn level %d và move thứ k (k = 0, 1, 2...) không sớm hơn level %d + %d x k, để move đến dần dần. '
           'Ô còn trống thì tự học; hết ô thì hiện hộp thoại chọn move cũ muốn quên '
           '(chỉ hiện nếu move mới mạnh hơn move yếu nhất, và khi %d giây không bị đánh).' % (ld.MIN_OFFER, ld.MIN_OFFER, ld.STEP, 10), '',
           '| Pokemon | Hệ | Các move (level mở: tên, hệ, sức mạnh) |', '|---|---|---|']
    done = set()
    for uid, name in sorted(units.items(), key=lambda kv: kv[1]):
        if name in done:
            continue
        done.add(name)
        s = ld.SPECIES.get(ld.slug(name), {})
        cands = plan.by_unit.get(uid, [])
        cell = '; '.join('Lv%d %s (%s, %d)' % (lv, plan.moves[m].name, plan.moves[m].type, plan.moves[m].power)
                         for lv, m in cands) or '(không có move sát thương)'
        out.append('| %s | %s | %s |' % (name, '/'.join(s.get('types', [])), cell))
    out.append('')
    open(path, 'w', encoding='utf-8').write(chr(10).join(out))
    print('%d Pokemon, %d moves, %d ability rows' % (len(done), len(plan.moves), ld.SLOTS * len(plan.moves)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join('..', 'Pokemon Arena v3.0.w3x'))
