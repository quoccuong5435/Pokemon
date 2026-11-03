"""Extract a WC3 map; discovers file names from listfile + known names + string scanning."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpq  # noqa: E402

KNOWN = """war3map.j scripts\\war3map.j war3map.lua scripts\\war3map.lua war3map.w3i war3map.w3e war3map.doo
war3mapUnits.doo war3map.w3u war3map.w3t war3map.w3a war3map.w3b war3map.w3d war3map.w3h war3map.w3q
war3map.wts war3map.wtg war3map.wct war3map.w3r war3map.w3c war3map.w3s war3map.mmp war3map.shd
war3mapMap.blp war3mapMap.tga war3mapPreview.tga war3map.wpm war3map.imp war3mapMisc.txt war3mapSkin.txt
war3mapExtra.txt war3map.w3f war3mapImported\\ (listfile) (attributes) (signature) (user data)
Units\\UnitData.slk Units\\UnitUI.slk Units\\UnitBalance.slk Units\\UnitAbilities.slk Units\\UnitWeapons.slk
Units\\AbilityData.slk Units\\ItemData.slk Units\\UpgradeData.slk Units\\AbilityBuffData.slk Units\\DestructableData.slk
Units\\CommonAbilityStrings.txt Units\\CampaignUnitStrings.txt Units\\CampaignUnitFunc.txt Units\\CampaignAbilityFunc.txt
Units\\CampaignAbilityStrings.txt Units\\HumanUnitFunc.txt Units\\HumanUnitStrings.txt Units\\ItemFunc.txt Units\\ItemStrings.txt
Units\\CommonAbilityFunc.txt Units\\NeutralUnitFunc.txt Units\\NeutralUnitStrings.txt Units\\NeutralAbilityFunc.txt
Units\\NeutralAbilityStrings.txt Units\\HumanAbilityFunc.txt Units\\HumanAbilityStrings.txt Units\\OrcUnitFunc.txt
Units\\OrcUnitStrings.txt Units\\NightElfUnitFunc.txt Units\\UndeadUnitFunc.txt Units\\MiscData.txt Units\\MiscGame.txt
UI\\WorldEditStrings.txt UI\\TriggerData.txt UI\\TriggerStrings.txt UI\\MiscUI.txt UI\\FrameDef\\GlobalStrings.fdf
Scripts\\common.j Scripts\\Blizzard.j war3map.w3o conversation.json war3mapFrame.toc""".split()

EXT = r'(?:mdx|mdl|blp|tga|dds|wav|mp3|flac|ogg|txt|slk|fdf|toc|j|lua|ai|pld|w3x|tif|jpg)'
PAT = re.compile(rb'[A-Za-z0-9_\\/ ().\-\[\]!#&+]{2,200}\.' + EXT.encode(), re.I)


def candidates_from(data):
    out = set()
    for m in PAT.finditer(data):
        s = m.group(0).decode('latin-1').strip()
        s = s.replace('/', '\\')
        out.add(s)
        # strip leading junk segments one at a time
        parts = s.split(' ')
        for i in range(1, len(parts)):
            out.add(' '.join(parts[i:]))
        if s.lower().endswith('.mdl'):
            out.add(s[:-4] + '.mdx')
        if s.lower().endswith('.mdx') or s.lower().endswith('.mdl'):
            stem = s[:-4]
            out.add(stem + '_portrait.mdx')
            out.add(stem + '_Portrait.mdx')
        if s.lower().endswith('.tga'):
            out.add(s[:-4] + '.blp')
        if s.lower().endswith('.blp'):
            d = s.rsplit('\\', 1)
            if len(d) == 2:
                out.add(d[0] + '\\Disabled\\DIS' + d[1].split('\\')[-1])
                out.add('ReplaceableTextures\\CommandButtonsDisabled\\DIS' + d[1].split('\\')[-1])
            out.add('ReplaceableTextures\\CommandButtonsDisabled\\DIS' + s.split('\\')[-1])
        # also war3mapImported\ variant
        base = s.split('\\')[-1]
        out.add('war3mapImported\\' + base)
        out.add(base)
    return out


def main(src, dst):
    a = mpq.MPQ(src)
    print('base', hex(a.base), 'hdr', a.hdr_size, 'arc', a.arc_size, 'ver', a.fmt_ver,
          'sector', a.sector_size, 'ht', hex(a.ht_pos), a.ht_count, 'bt', hex(a.bt_pos), a.bt_count)
    used = [e for e in a.hash_table if e[4] < mpq.HASH_DELETED]
    print('hash entries used', len(used), 'blocks', len(a.block_table))
    names = set(KNOWN) | set(a.listfile())
    print('listfile entries', len(a.listfile()))
    found = {}
    tried = set()
    pending = set(names)
    while pending:
        new = set()
        for n in pending:
            tried.add(n.lower())
            if n in found:
                continue
            hi = a.find_hash(n)
            if hi is None:
                continue
            bi = a.hash_table[hi][4]
            if bi >= len(a.block_table):
                continue
            try:
                data = a.read_block(bi, n)
            except Exception as ex:  # noqa
                print('FAIL', n, ex)
                continue
            found[n] = (hi, bi, data)
            for c in candidates_from(data):
                if c.lower() not in tried:
                    new.add(c)
        pending = new
    known_his = {v[0] for v in found.values()}
    unknown = [i for i, e in enumerate(a.hash_table) if e[4] < len(a.block_table) and i not in known_his]
    print('found', len(found), 'unknown', len(unknown))
    os.makedirs(dst, exist_ok=True)
    for n, (hi, bi, data) in sorted(found.items()):
        p = os.path.join(dst, *n.split('\\'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
    with open(os.path.join(dst, '_names.txt'), 'w', encoding='utf-8') as f:
        for n, (hi, bi, data) in sorted(found.items()):
            f.write('%s\t%d\t%d\n' % (n, len(data), bi))
    with open(os.path.join(dst, '_unknown.txt'), 'w', encoding='utf-8') as f:
        for i in unknown:
            e = a.hash_table[i]
            blk = a.block_table[e[4]]
            f.write('hi=%d bi=%d off=%d csize=%d fsize=%d flags=%08x\n' % (i, e[4], blk[0], blk[1], blk[2], blk[3]))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
