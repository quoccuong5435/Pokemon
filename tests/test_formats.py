import os

import pytest

import mpq
import objdata
import slk
from conftest import EXTRACTED, V18


def _names():
    with open(os.path.join(EXTRACTED, '_names.txt'), encoding='utf-8') as f:
        return [line.split('\t')[0] for line in f if line.strip()]


@pytest.fixture(scope='module')
def v18():
    return mpq.MPQ(V18)


def test_mpq_roundtrip_keeps_all_blocks(v18, tmp_path):
    out = str(tmp_path / 'out.w3x')
    v18.save_with(out, {'scripts\\war3map.j': b'x'})
    b = mpq.MPQ(out)
    for n in _names():
        if n.lower() in ('scripts\\war3map.j',):
            continue
        assert b.read(n) == v18.read(n), n
    assert b.read('scripts\\war3map.j') == b'x'


def test_unknown_named_blocks_preserved_raw(v18, tmp_path):
    out = str(tmp_path / 'out.w3x')
    v18.save_with(out, {'war3mapImported\\Mega\\t.txt': b'hello'})
    b = mpq.MPQ(out)
    for i, (off, csize, fsize, flags) in enumerate(v18.block_table):
        assert b.block_table[i] == [off, csize, fsize, flags]
        assert b.raw[b.base + off:b.base + off + csize] == v18.raw[v18.base + off:v18.base + off + csize]
    assert [tuple(e) for e in b.hash_table if e[4] < len(v18.block_table)] == \
        [tuple(e) for e in v18.hash_table if e[4] < len(v18.block_table)]


def test_new_files_use_sector_format_like_wc3_maps(v18, tmp_path):
    # WC3 cannot read MPQ_FILE_SINGLE_UNIT blocks: the map list showed an empty name for v2.0
    out = str(tmp_path / 'out.w3x')
    big = bytes(range(256)) * 20000  # 5 MB, spans 3 sectors of 2 MB
    v18.save_with(out, {'war3map.w3i': v18.read('war3map.w3i'), 'war3mapImported\\Mega\\big.bin': big})
    b = mpq.MPQ(out)
    for name in ('war3map.w3i', 'war3mapImported\\Mega\\big.bin'):
        flags = b.block_table[b.hash_table[b.find_hash(name)][4]][3]
        assert flags == mpq.F_EXISTS | mpq.F_COMPRESS, '%s flags %08x' % (name, flags)
    assert b.read('war3map.w3i') == v18.read('war3map.w3i')
    assert b.read('war3mapImported\\Mega\\big.bin') == big


def test_mpq_adds_new_file(v18, tmp_path):
    out = str(tmp_path / 'out.w3x')
    v18.save_with(out, {'war3mapImported\\Mega\\t.txt': b'hello'})
    assert mpq.MPQ(out).read('war3mapImported\\Mega\\t.txt') == b'hello'


def test_mpq_adds_many_files_until_nearly_full(v18, tmp_path):
    out = str(tmp_path / 'out.w3x')
    files = {'war3mapImported\\Mega\\f%03d.txt' % i: b'%d' % i for i in range(200)}
    v18.save_with(out, files)
    b = mpq.MPQ(out)
    assert all(b.read(n) == v for n, v in files.items())


def test_save_refuses_when_full(v18, tmp_path):
    files = {'war3mapImported\\Mega\\g%03d.txt' % i: b'x' for i in range(300)}
    with pytest.raises(RuntimeError, match='hash table full'):
        v18.save_with(str(tmp_path / 'out.w3x'), files)


def test_w3u_roundtrip():
    data = open(os.path.join(EXTRACTED, 'war3map.w3u'), 'rb').read()
    assert objdata.ObjFile(data).to_bytes() == data


@pytest.mark.parametrize('name', ['ItemData.slk', 'AbilityData.slk', 'AbilityBuffData.slk', 'UpgradeData.slk'])
def test_slk_roundtrip_values(name):
    text = open(os.path.join(EXTRACTED, 'Units', name), encoding='latin-1').read()
    a = slk.Slk(text)
    b = slk.Slk(a.to_text())
    assert a.cols == b.cols
    assert len(a.rows) == len(b.rows)
    for ra, rb in zip(a.rows, b.rows):
        assert {k: v for k, v in ra.items() if v is not None} == {k: v for k, v in rb.items() if v is not None}


def _candidate_homes(table, p):
    n = len(table)
    q = p
    while table[(q - 1) % n][4] != mpq.HASH_EMPTY and (q - 1) % n != p:
        q -= 1
    return [c % n for c in range(q, p + 1)]


EXTRA = open(os.path.join(os.path.dirname(EXTRACTED), 'tools', 'known_names_v18.txt'),
             encoding='utf-8').read().splitlines()


def test_save_with_bigger_hash_table_reads_all_known(v18, tmp_path):
    out = str(tmp_path / 'big.w3x')
    v18.save_with(out, {'war3mapImported\\Mega\\t.txt': b'hello'}, hash_size=4096, extra_names=EXTRA)
    b = mpq.MPQ(out)
    assert len(b.hash_table) == 4096
    assert sum(1 for e in b.hash_table if e[4] < mpq.HASH_DELETED) < 1500
    for n in mpq.discover_names(v18, EXTRA):
        assert b.read(n) == v18.read(n), n
    assert b.read('war3mapImported\\Mega\\t.txt') == b'hello'


def test_unknown_entries_reachable_from_every_candidate_home(v18, tmp_path):
    out = str(tmp_path / 'big.w3x')
    v18.save_with(out, {}, hash_size=4096, extra_names=EXTRA)
    b = mpq.MPQ(out)
    known = {v18.find_hash(n) for n in mpq.discover_names(v18, EXTRA)}
    old = v18.hash_table
    unknown = [i for i, e in enumerate(old) if e[4] < mpq.HASH_DELETED and i not in known
               and v18.block_table[e[4]][2] > 0]
    assert len(unknown) > 0
    for p in unknown:
        a, bb, bi = old[p][0], old[p][1], old[p][4]
        for c in _candidate_homes(old, p):
            for k in range(4):
                h = c + k * 1024
                found = False
                while b.hash_table[h][4] != mpq.HASH_EMPTY:
                    e = b.hash_table[h]
                    if (e[0], e[1], e[4]) == (a, bb, bi):
                        found = True
                        break
                    h = (h + 1) % 4096
                assert found, (p, c, k)


def test_add_300_files_with_bigger_table(v18, tmp_path):
    files = {'war3mapImported\\Poke\\f%03d.txt' % i: b'%d' % i for i in range(300)}
    out = str(tmp_path / 'big.w3x')
    v18.save_with(out, files, hash_size=4096, extra_names=EXTRA)
    b = mpq.MPQ(out)
    assert all(b.read(n) == v for n, v in files.items())
