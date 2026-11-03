"""Minimal MPQ (v1) reader/writer for Warcraft III maps (.w3x/.w3m).

Supports: encrypted hash/block tables, encrypted files (incl. FIX_KEY),
zlib / bzip2 / pkware-implode sector compression, single-unit files.
Writing: appends new file data to an existing archive and rewrites the
hash + block tables, keeping every untouched block (even unknown-named
ones) byte-for-byte.
"""
import re
import struct
import zlib
import bz2
import os

# ---------------------------------------------------------------- crypto
_CRYPT = [0] * 0x500


def _init_crypt():
    seed = 0x00100001
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            t1 = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            t2 = seed & 0xFFFF
            _CRYPT[idx] = t1 | t2
            idx += 0x100


_init_crypt()

HASH_OFFSET, HASH_A, HASH_B, HASH_KEY = 0, 1, 2, 3


def hash_string(s, htype):
    s = s.upper().replace('/', '\\')
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in s.encode('latin-1', 'replace'):
        seed1 = (_CRYPT[(htype << 8) + ch] ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def decrypt(data, key):
    n = len(data) // 4
    out = bytearray(data)
    seed = 0xEEEEEEEE
    vals = struct.unpack_from('<%dI' % n, data)
    res = []
    for v in vals:
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        d = (v ^ (key + seed)) & 0xFFFFFFFF
        res.append(d)
        key = ((((~key) << 0x15) + 0x11111111) | (key >> 0x0B)) & 0xFFFFFFFF
        seed = (d + seed + (seed << 5) + 3) & 0xFFFFFFFF
    struct.pack_into('<%dI' % n, out, 0, *res)
    return bytes(out)


def encrypt(data, key):
    n = len(data) // 4
    out = bytearray(data)
    seed = 0xEEEEEEEE
    vals = struct.unpack_from('<%dI' % n, data)
    res = []
    for v in vals:
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        e = (v ^ (key + seed)) & 0xFFFFFFFF
        res.append(e)
        key = ((((~key) << 0x15) + 0x11111111) | (key >> 0x0B)) & 0xFFFFFFFF
        seed = (v + seed + (seed << 5) + 3) & 0xFFFFFFFF
    struct.pack_into('<%dI' % n, out, 0, *res)
    return bytes(out)


# ---------------------------------------------------------------- pkware explode
def _explode(data, out_size):
    """PKWARE DCL decompression (used by old MPQ 'implode')."""
    lit_bits_len = [
        11, 12, 12, 12, 12, 12, 12, 12, 12, 8, 7, 12, 12, 7, 12, 12,
        12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12,
        4, 10, 8, 12, 10, 12, 10, 8, 7, 7, 8, 9, 7, 6, 7, 8,
        7, 6, 7, 7, 7, 7, 8, 7, 7, 8, 8, 12, 11, 7, 9, 11,
        12, 6, 7, 6, 6, 5, 7, 8, 8, 6, 11, 9, 6, 7, 6, 6,
        7, 11, 6, 6, 6, 7, 9, 8, 9, 9, 11, 8, 11, 9, 12, 8,
        12, 5, 6, 6, 6, 5, 6, 6, 6, 5, 11, 7, 5, 6, 5, 5,
        6, 10, 5, 5, 5, 5, 8, 7, 8, 8, 10, 11, 11, 12, 12, 12,
    ] + [13] * 128
    lit_codes = [
        0x0490, 0x0FE0, 0x07E0, 0x0BE0, 0x03E0, 0x0DE0, 0x05E0, 0x09E0,
        0x01E0, 0x00B8, 0x0062, 0x0EE0, 0x06E0, 0x0022, 0x0AE0, 0x02E0,
        0x0CE0, 0x04E0, 0x08E0, 0x00E0, 0x0F60, 0x0760, 0x0B60, 0x0360,
        0x0D60, 0x0560, 0x1240, 0x0960, 0x0160, 0x0E60, 0x0660, 0x0A60,
        0x000F, 0x0250, 0x0038, 0x0260, 0x0050, 0x0C60, 0x0390, 0x00D8,
        0x0042, 0x0002, 0x0058, 0x01B0, 0x007C, 0x0029, 0x003C, 0x0098,
        0x005C, 0x0009, 0x001C, 0x006C, 0x002C, 0x004C, 0x0018, 0x000C,
        0x0074, 0x00E8, 0x0068, 0x0460, 0x0090, 0x0034, 0x00B0, 0x0710,
        0x0860, 0x0031, 0x0054, 0x0011, 0x0021, 0x0017, 0x0014, 0x00A8,
        0x0028, 0x0001, 0x0310, 0x0130, 0x003E, 0x0064, 0x001E, 0x002E,
        0x0024, 0x0510, 0x000E, 0x0036, 0x0016, 0x0044, 0x0030, 0x00C8,
        0x01D0, 0x00D0, 0x0110, 0x0048, 0x0610, 0x0150, 0x0060, 0x0088,
        0x0FA0, 0x0007, 0x0026, 0x0006, 0x003A, 0x001B, 0x001A, 0x002A,
        0x000A, 0x000B, 0x0210, 0x0004, 0x0013, 0x0032, 0x0003, 0x001D,
        0x0012, 0x0190, 0x000D, 0x0015, 0x0005, 0x0019, 0x0008, 0x0078,
        0x00F0, 0x0070, 0x0290, 0x0410, 0x0010, 0x07A0, 0x0BA0, 0x03A0,
        0x0240, 0x1C40, 0x0C40, 0x1440, 0x0440, 0x1840, 0x0840, 0x1040,
        0x0040, 0x1F80, 0x0F80, 0x1780, 0x0780, 0x1B80, 0x0B80, 0x1380,
        0x0380, 0x1D80, 0x0D80, 0x1580, 0x0580, 0x1980, 0x0980, 0x1180,
        0x0180, 0x1E80, 0x0E80, 0x1680, 0x0680, 0x1A80, 0x0A80, 0x1280,
        0x0280, 0x1C80, 0x0C80, 0x1480, 0x0480, 0x1880, 0x0880, 0x1080,
        0x0080, 0x1F00, 0x0F00, 0x1700, 0x0700, 0x1B00, 0x0B00, 0x1300,
        0x0DA0, 0x05A0, 0x09A0, 0x01A0, 0x0EA0, 0x06A0, 0x0AA0, 0x02A0,
        0x0CA0, 0x04A0, 0x08A0, 0x00A0, 0x0F20, 0x0720, 0x0B20, 0x0320,
        0x0D20, 0x0520, 0x0920, 0x0120, 0x0E20, 0x0620, 0x0A20, 0x0220,
        0x0C20, 0x0420, 0x0820, 0x0020, 0x0FC0, 0x07C0, 0x0BC0, 0x03C0,
        0x0DC0, 0x05C0, 0x09C0, 0x01C0, 0x0EC0, 0x06C0, 0x0AC0, 0x02C0,
        0x0CC0, 0x04C0, 0x08C0, 0x00C0, 0x0F40, 0x0740, 0x0B40, 0x0340,
        0x0300, 0x0D40, 0x1D00, 0x0D00, 0x1500, 0x0540, 0x0500, 0x1900,
        0x0900, 0x0940, 0x1100, 0x0100, 0x1E00, 0x0E00, 0x0140, 0x1600,
        0x0600, 0x1A00, 0x0E40, 0x0640, 0x0A40, 0x0A00, 0x1200, 0x0200,
        0x1C00, 0x0C00, 0x1400, 0x0400, 0x1800, 0x0800, 0x1000, 0x0000,
    ]
    len_bits = [3, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7]
    len_code = [0x05, 0x03, 0x01, 0x06, 0x0A, 0x02, 0x0C, 0x14,
                0x04, 0x18, 0x08, 0x30, 0x10, 0x20, 0x40, 0x00]
    ex_len_bits = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    len_base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 22, 38, 70, 134, 262]
    dist_bits = [2, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
    dist_code = [0x03, 0x0D, 0x05, 0x19, 0x09, 0x11, 0x01, 0x3E,
                 0x1E, 0x2E, 0x0E, 0x36, 0x16, 0x26, 0x06, 0x3A,
                 0x1A, 0x2A, 0x0A, 0x32, 0x12, 0x22, 0x42, 0x02,
                 0x7C, 0x3C, 0x5C, 0x1C, 0x6C, 0x2C, 0x4C, 0x0C,
                 0x74, 0x34, 0x54, 0x14, 0x64, 0x24, 0x44, 0x04,
                 0x78, 0x38, 0x58, 0x18, 0x68, 0x28, 0x48, 0x08,
                 0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10,
                 0xE0, 0x60, 0xA0, 0x20, 0xC0, 0x40, 0x80, 0x00]

    def build(codes, bits):
        table = {}
        for sym, (c, b) in enumerate(zip(codes, bits)):
            table[(b, c)] = sym
        return table

    lit_t = build(lit_codes, lit_bits_len)
    len_t = build(len_code, len_bits)
    dist_t = build(dist_code, dist_bits)

    ctype, dsize_bits = data[0], data[1]
    pos = 2
    bitbuf = 0
    nbits = 0
    out = bytearray()

    def need(n):
        nonlocal bitbuf, nbits, pos
        while nbits < n:
            if pos >= len(data):
                raise EOFError
            bitbuf |= data[pos] << nbits
            pos += 1
            nbits += 8

    def getbits(n):
        nonlocal bitbuf, nbits
        need(n)
        v = bitbuf & ((1 << n) - 1)
        bitbuf >>= n
        nbits -= n
        return v

    def decode(table, maxlen):
        code = 0
        for length in range(1, maxlen + 1):
            code |= getbits(1) << (length - 1)
            if (length, code) in table:
                return table[(length, code)]
        raise ValueError('bad huffman code')

    try:
        while len(out) < out_size:
            if getbits(1):
                li = decode(len_t, 7)
                length = len_base[li] + getbits(ex_len_bits[li]) + 2
                if length == 519:
                    break
                di = decode(dist_t, 8)
                if length == 2:
                    dist = (di << 2) | getbits(2)
                else:
                    dist = (di << dsize_bits) | getbits(dsize_bits)
                start = len(out) - dist - 1
                for i in range(length):
                    out.append(out[start + i])
            else:
                if ctype == 0:
                    out.append(getbits(8))
                else:
                    out.append(decode(lit_t, 13))
    except EOFError:
        pass
    return bytes(out[:out_size])


# ---------------------------------------------------------------- archive
F_IMPLODE = 0x00000100
F_COMPRESS = 0x00000200
F_ENCRYPTED = 0x00010000
F_FIX_KEY = 0x00020000
F_SINGLE_UNIT = 0x01000000
F_DELETE = 0x02000000
F_SECTOR_CRC = 0x04000000
F_EXISTS = 0x80000000

HASH_EMPTY = 0xFFFFFFFF
HASH_DELETED = 0xFFFFFFFE


def _decompress_sector(buf, out_size):
    if len(buf) >= out_size:
        return buf[:out_size]
    mask = buf[0]
    data = buf[1:]
    # Order of decompression: bzip2 -> implode -> zlib (reverse of compression)
    if mask & 0x10:
        data = bz2.decompress(data)
    if mask & 0x08:
        data = _explode(data, out_size)
    if mask & 0x02:
        data = zlib.decompressobj().decompress(data)
    if mask & ~(0x02 | 0x08 | 0x10):
        raise NotImplementedError('compression mask 0x%02x' % mask)
    return data


class MPQ:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            self.raw = f.read()
        self.base = self._find_header()
        h = self.raw[self.base:self.base + 32]
        (magic, self.hdr_size, self.arc_size, self.fmt_ver, self.sector_shift,
         self.ht_pos, self.bt_pos, self.ht_count, self.bt_count) = struct.unpack('<4sIIHHIIII', h)
        self.sector_size = 512 << self.sector_shift
        self._read_tables()

    def _find_header(self):
        off = 0
        while off < len(self.raw):
            if self.raw[off:off + 4] == b'MPQ\x1a':
                return off
            off += 0x200
        raise ValueError('no MPQ header')

    def _read_tables(self):
        b = self.base
        # hash table (WC3 ignores high-bit tricks, clamp to file size)
        ht_bytes = self.raw[b + self.ht_pos:b + self.ht_pos + self.ht_count * 16]
        ht_bytes = ht_bytes[:len(ht_bytes) // 16 * 16]
        ht = decrypt(ht_bytes, hash_string('(hash table)', HASH_KEY))
        self.hash_table = [struct.unpack_from('<IIHHI', ht, i * 16) for i in range(len(ht) // 16)]
        bt_bytes = self.raw[b + self.bt_pos:b + self.bt_pos + self.bt_count * 16]
        bt_bytes = bt_bytes[:len(bt_bytes) // 16 * 16]
        bt = decrypt(bt_bytes, hash_string('(block table)', HASH_KEY))
        self.block_table = [list(struct.unpack_from('<IIII', bt, i * 16)) for i in range(len(bt) // 16)]

    # -- lookup
    def find_hash(self, name):
        n = len(self.hash_table)
        if n == 0:
            return None
        start = hash_string(name, HASH_OFFSET) & (n - 1)
        a = hash_string(name, HASH_A)
        bb = hash_string(name, HASH_B)
        i = start
        while True:
            e = self.hash_table[i]
            if e[4] == HASH_EMPTY:
                return None
            if e[0] == a and e[1] == bb and e[4] != HASH_DELETED:
                return i
            i = (i + 1) & (n - 1)
            if i == start:
                return None

    def has(self, name):
        hi = self.find_hash(name)
        if hi is None:
            return False
        bi = self.hash_table[hi][4]
        return bi < len(self.block_table)

    def read(self, name):
        hi = self.find_hash(name)
        if hi is None:
            raise KeyError(name)
        bi = self.hash_table[hi][4]
        return self.read_block(bi, name)

    def read_block(self, bi, name=None):
        off, csize, fsize, flags = self.block_table[bi]
        start = self.base + off
        data = self.raw[start:start + csize]
        key = None
        if flags & F_ENCRYPTED:
            if name is None:
                raise ValueError('encrypted file needs a name')
            base_name = name.replace('/', '\\').split('\\')[-1]
            key = hash_string(base_name, HASH_KEY)
            if flags & F_FIX_KEY:
                key = ((key + off) ^ fsize) & 0xFFFFFFFF
        if flags & F_SINGLE_UNIT:
            if key is not None:
                data = decrypt(data[:len(data) // 4 * 4], key) + data[len(data) // 4 * 4:]
            if flags & F_COMPRESS:
                return _decompress_sector(data, fsize)
            if flags & F_IMPLODE and csize < fsize:
                return _explode(data, fsize)
            return data[:fsize]
        if not (flags & (F_COMPRESS | F_IMPLODE)):
            if key is None:
                return data[:fsize]
            out = bytearray()
            nsec = (fsize + self.sector_size - 1) // self.sector_size
            for s in range(nsec):
                chunk = data[s * self.sector_size:(s + 1) * self.sector_size]
                n4 = len(chunk) // 4 * 4
                out += decrypt(chunk[:n4], (key + s) & 0xFFFFFFFF) + chunk[n4:]
            return bytes(out[:fsize])
        nsec = (fsize + self.sector_size - 1) // self.sector_size
        ntab = nsec + 1
        tab_raw = data[:ntab * 4]
        if key is not None:
            tab_raw = decrypt(tab_raw, (key - 1) & 0xFFFFFFFF)
        offs = struct.unpack('<%dI' % ntab, tab_raw)
        out = bytearray()
        for s in range(nsec):
            chunk = data[offs[s]:offs[s + 1]]
            if key is not None:
                n4 = len(chunk) // 4 * 4
                chunk = decrypt(chunk[:n4], (key + s) & 0xFFFFFFFF) + chunk[n4:]
            usize = min(self.sector_size, fsize - s * self.sector_size)
            if flags & F_COMPRESS:
                out += _decompress_sector(chunk, usize)
            elif len(chunk) < usize:
                out += _explode(chunk, usize)
            else:
                out += chunk[:usize]
        return bytes(out[:fsize])

    def listfile(self):
        try:
            txt = self.read('(listfile)').decode('latin-1')
        except Exception:
            return []
        return [l.strip() for l in txt.replace(';', '\n').splitlines() if l.strip()]

    # -- writing (append mode)
    def _pack_sectors(self, content):
        """Sector offset table + zlib-compressed sectors (raw sector when compression does not help)."""
        sectors = []
        for s in range(0, max(len(content), 1), self.sector_size):
            raw = content[s:s + self.sector_size]
            comp = zlib.compress(raw, 9)
            sectors.append(b'\x02' + comp if len(comp) + 1 < len(raw) else raw)
        offs = [4 * (len(sectors) + 1)]
        for sec in sectors:
            offs.append(offs[-1] + len(sec))
        return struct.pack('<%dI' % len(offs), *offs) + b''.join(sectors)

    def _grow_hash_table(self, hash_table, new_size, extra_names=()):
        """Re-lay the hash table at new_size (power of two, multiple of the old size).

        Entries whose name is known are placed by name. For an unknown name only the
        old position p is known; its real home is somewhere in the run of occupied
        slots ending at p, and in the bigger table it is that home + k*old_size.
        A copy is inserted (linear probing) from every such candidate home, so the
        lookup by the real name, which starts at the real home, always finds it.
        """
        n = len(self.hash_table)
        if new_size % n or new_size & (new_size - 1):
            raise ValueError('hash_size must be a power of two multiple of %d' % n)
        empty = [0xFFFFFFFF, 0xFFFFFFFF, 0xFFFF, 0xFFFF, HASH_EMPTY]
        table = [list(empty) for _ in range(new_size)]

        def insert(start, entry):
            i = start & (new_size - 1)
            while table[i][4] != HASH_EMPTY:
                i = (i + 1) & (new_size - 1)
            table[i] = list(entry)

        known = {}
        for name in discover_names(self, extra_names):
            hi = self.find_hash(name)
            if hi is not None:
                known[hi] = name
        for hi, name in known.items():
            if hash_table[hi][4] < HASH_DELETED:
                insert(hash_string(name, HASH_OFFSET), hash_table[hi])
        for p, e in enumerate(hash_table):
            if e[4] >= HASH_DELETED or p in known:
                continue
            if e[4] < len(self.block_table) and self.block_table[e[4]][2] == 0:
                continue  # unknown zero-byte file: nothing to keep
            q = p
            while self.hash_table[(q - 1) % n][4] != HASH_EMPTY and (q - 1) % n != p:
                q -= 1
            for c in range(q, p + 1):
                for k in range(new_size // n):
                    insert((c % n) + k * n, e)
        return table

    def save_with(self, out_path, replace_files, delete_files=(), extra_listfile=None, hash_size=None,
                  extra_names=()):
        """Write a new archive = original blocks + new/replaced files.

        replace_files: {name: bytes}. Files are stored zlib-compressed in sectors,
        unencrypted. Names not present get new hash entries. hash_size grows the
        hash table (see _grow_hash_table).
        """
        b = self.base
        head = bytearray(self.raw[:b])  # HM3W header (512 bytes)
        body = bytearray(self.raw[b:b + max(self.ht_pos, self.bt_pos, 32)])
        # Keep everything up to the earliest table (old tables are dropped),
        # or further if some block lives behind the tables.
        data_end = min(self.ht_pos, self.bt_pos)
        for off, csize, _fs, fl in self.block_table:
            if fl & F_EXISTS:
                data_end = max(data_end, off + csize)
        body = bytearray(self.raw[b:b + data_end])
        hash_table = [list(e) for e in self.hash_table]
        block_table = [list(e) for e in self.block_table]

        for name in delete_files:
            hi = self.find_hash(name)
            if hi is not None:
                hash_table[hi][0] = hash_table[hi][1] = 0xFFFFFFFF
                hash_table[hi][2] = 0xFFFF
                hash_table[hi][3] = 0xFFFF
                hash_table[hi][4] = HASH_DELETED

        if hash_size and hash_size > len(hash_table):
            hash_table = self._grow_hash_table(hash_table, hash_size, extra_names)

        names = dict(replace_files)
        if extra_listfile is not None:
            names['(listfile)'] = extra_listfile

        # Keep at least one empty slot so lookups terminate.
        used = sum(1 for e in hash_table if e[4] < HASH_DELETED)
        new_names = sum(1 for nm in names if self.find_hash(nm) is None)
        if used + new_names >= len(hash_table):
            raise RuntimeError('hash table full: %d used + %d new >= %d slots'
                               % (used, new_names, len(hash_table)))

        for name, content in names.items():
            stored = self._pack_sectors(content)
            flags = F_EXISTS | F_COMPRESS  # WC3 cannot read MPQ_FILE_SINGLE_UNIT blocks
            while len(body) % 4:
                body.append(0)
            off = len(body)
            body += stored
            blk = [off, len(stored), len(content), flags]
            hi = None
            # find existing
            nn = len(hash_table)
            start = hash_string(name, HASH_OFFSET) & (nn - 1)
            a = hash_string(name, HASH_A)
            bb = hash_string(name, HASH_B)
            i = start
            first_free = None
            while True:
                e = hash_table[i]
                if e[4] == HASH_EMPTY:
                    if first_free is None:
                        first_free = i
                    break
                if e[4] == HASH_DELETED and first_free is None:
                    first_free = i
                if e[0] == a and e[1] == bb and e[4] < HASH_DELETED:
                    hi = i
                    break
                i = (i + 1) & (nn - 1)
                if i == start:
                    break
            if hi is not None:
                old_bi = hash_table[hi][4]
                if old_bi < len(block_table):
                    block_table[old_bi] = blk
                else:
                    block_table.append(blk)
                    hash_table[hi][4] = len(block_table) - 1
            else:
                if first_free is None:
                    raise RuntimeError('hash table full')
                block_table.append(blk)
                hash_table[first_free] = [a, bb, 0, 0, len(block_table) - 1]

        while len(body) % 4:
            body.append(0)
        ht_pos = len(body)
        ht_raw = b''.join(struct.pack('<IIHHI', *e) for e in hash_table)
        body += encrypt(ht_raw, hash_string('(hash table)', HASH_KEY))
        bt_pos = len(body)
        bt_raw = b''.join(struct.pack('<IIII', *e) for e in block_table)
        body += encrypt(bt_raw, hash_string('(block table)', HASH_KEY))
        hdr = struct.pack('<4sIIHHIIII', b'MPQ\x1a', 32, len(body), 0, self.sector_shift,
                          ht_pos, bt_pos, len(hash_table), len(block_table))
        body[0:32] = hdr
        with open(out_path, 'wb') as f:
            f.write(head)
            f.write(body)
        return out_path


# ---------------------------------------------------------------- name discovery
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
Units\\NeutralUpgradeStrings.txt UI\\WorldEditStrings.txt UI\\TriggerData.txt UI\\TriggerStrings.txt UI\\MiscUI.txt
UI\\FrameDef\\GlobalStrings.fdf Scripts\\common.j Scripts\\Blizzard.j war3map.w3o conversation.json
war3mapFrame.toc""".split()

_EXT = r'(?:mdx|mdl|blp|tga|dds|wav|mp3|flac|ogg|txt|slk|fdf|toc|j|lua|ai|pld|w3x|tif|jpg|ttf)'
_PAT = re.compile(rb'[A-Za-z0-9_\\/ ().\-\[\]!#&+]{2,200}\.' + _EXT.encode(), re.I)


def candidates_from(data):
    """File names a file's content may refer to (plus common variants)."""
    out = set()
    for m in _PAT.finditer(data):
        s = m.group(0).decode('latin-1').strip().replace('/', '\\')
        while '\\\\' in s:  # JASS string literals double their backslashes
            s = s.replace('\\\\', '\\')
        out.add(s)
        parts = s.split(' ')
        for i in range(1, len(parts)):
            out.add(' '.join(parts[i:]))
        low = s.lower()
        if low.endswith('.mdl'):
            out.add(s[:-4] + '.mdx')
        if low.endswith(('.mdx', '.mdl')):
            out.add(s[:-4] + '_portrait.mdx')
            out.add(s[:-4] + '_Portrait.mdx')
        if low.endswith('.tga'):
            out.add(s[:-4] + '.blp')
        base = s.split('\\')[-1]
        if low.endswith('.blp'):
            d = s.rsplit('\\', 1)
            if len(d) == 2:
                out.add(d[0] + '\\Disabled\\DIS' + base)
            out.add('ReplaceableTextures\\CommandButtonsDisabled\\DIS' + base)
        out.add('war3mapImported\\' + base)
        out.add(base)
    return out


def discover_names(archive, extra=()):
    """Names of files present in the archive: listfile + well-known/extra names + names found in file contents."""
    cache = getattr(archive, '_names', None)
    if cache is None:
        cache = archive._names = {}
    key = tuple(sorted(extra))
    if key in cache:
        return cache[key]
    found = set()
    tried = set()
    pending = set(KNOWN) | set(archive.listfile()) | set(extra)
    while pending:
        new = set()
        for n in pending:
            tried.add(n.lower())
            hi = archive.find_hash(n)
            if hi is None or archive.hash_table[hi][4] >= len(archive.block_table):
                continue
            if any(f.lower() == n.lower() for f in found):
                continue
            try:
                data = archive.read_block(archive.hash_table[hi][4], n)
            except Exception:  # noqa: BLE001 - unreadable/encrypted with another name
                continue
            found.add(n)
            for c in candidates_from(data):
                if c.lower() not in tried:
                    new.add(c)
        pending = new
    cache[key] = found
    return found
