"""Safe MPQ size optimization & Legend 3D scale normalization for Pokemon Arena.

1. Normalizes oversized PkFx\\Leg25 Legend Hero/Boss/Mega 3D scales (`usca` + `Mega_Scale`).
2. Finds strictly unreferenced orphan .mdx / .blp / .tga files (never touching icons, UI, SLK, TXT, or live TEXS).
3. Re-encodes oversized BLP1-JPEG textures (>= 90 KB or > 512px) to clean WC3-compatible
   BLP1-JPEG (max 512x512, quality 76, 4-channel BGRA/CMYK subsampling=0, full mipmaps, header <= 624 B).
4. Compacts MPQ archives cleanly (0 dead slack space, preserves every unnamed & encrypted block).
"""
import io
import os
import re
import struct
import numpy as np
from PIL import Image

import mpq

# Normalized `usca` scales for oversized new PkFx\Leg25 Legend Heroes (target renderedH ~160-210, renderedW <= 430)
LEG25_HERO_SCALES = {
    "EL0J": 0.40,  # Lunala     (raw 505x884  -> 202x354)
    "EL0C": 0.42,  # Xerneas    (raw 497x497  -> 209x209)
    "EL0E": 0.45,  # Zygarde    (raw 448x436  -> 202x196)
    "EL0I": 0.45,  # Solgaleo   (raw 365x895  -> 164x403)
    "EL08": 0.55,  # Reshiram   (raw 261x865  -> 144x475)
    "EL0A": 0.65,  # Kyurem     (raw 293x569  -> 191x370)
    "EL0O": 0.65,  # Eternatus  (raw 285x629  -> 186x409)
    "EL09": 0.72,  # Zekrom     (raw 254x523  -> 183x377)
    "EL01": 1.90,  # Registeel  (user report: was 0.82 which is tiny, scale up to match Regice/Regirock)
    "EL0N": 0.85,  # Zacian     (raw 221x278  -> 188x236)
    "EL0D": 0.85,  # Yveltal    (raw 200x414  -> 170x352)
    "EL05": 1.40,  # Heatran    (user report: was reduced to 0.88 which was too small, restore to 1.40)
    "EL0B": 0.95,  # Genesect   (raw 165x396  -> 157x376)
    "EL0H": 1.00,  # Volcanion  (raw 178x227  -> 178x227)
    "EL0K": 1.05,  # Necrozma   (raw 174x254  -> 183x267)
}

# Matching Mega skin `usca` in war3map.w3u and `Mega_Scale` / `Mega_BaseScale` in war3map.j
LEG25_MEGA_W3U_SCALES = {
    "hM22": 0.80,  # Black Kyurem  (raw 267x496 -> 213x397)
    "hM23": 0.65,  # White Kyurem  (raw 337x652 -> 219x424)
    "hM25": 0.88,  # Hoopa Unbound (raw 245x396 -> 215x348)
    "hM26": 1.08,  # Ultra Necrozma (raw 191x428 -> 206x463)
}

LEG25_MEGA_JASS_PATCHES = [
    ("    set Mega_Scale[39] = 1.500", "    set Mega_Scale[39] = 0.800"),
    ("    set Mega_BaseScale[39] = 1.350", "    set Mega_BaseScale[39] = 0.650"),
    ("    set Mega_Scale[40] = 1.500", "    set Mega_Scale[40] = 0.650"),
    ("    set Mega_BaseScale[40] = 1.350", "    set Mega_BaseScale[40] = 0.650"),
    ("    set Mega_Scale[42] = 1.550", "    set Mega_Scale[42] = 0.880"),
    ("    set Mega_Scale[43] = 1.550", "    set Mega_Scale[43] = 1.080"),
    ("    set Mega_BaseScale[43] = 1.300", "    set Mega_BaseScale[43] = 1.050"),
]


def normalize_legend_scales(w3u, script: str) -> str:
    """Normalizes oversized Leg25 Hero (`EL0*`), Boss (`nL2*` = 1.15x Hero), and Mega skin (`hM2*`) scales."""
    by_id = {u.id: u for u in w3u.custom}
    for hero_id, h_scale in LEG25_HERO_SCALES.items():
        if hero_id in by_id:
            by_id[hero_id].set("usca", 2, h_scale)
        boss_id = "nL2" + hero_id[3]
        if boss_id in by_id:
            by_id[boss_id].set("usca", 2, round(h_scale * 1.15, 2))
    for skin_id, m_scale in LEG25_MEGA_W3U_SCALES.items():
        if skin_id in by_id:
            by_id[skin_id].set("usca", 2, m_scale)
    for old, new in LEG25_MEGA_JASS_PATCHES:
        cnt = script.count(old)
        if cnt != 1:
            raise ValueError(f"[map_optimizer] Anchor {old!r} matched {cnt} times")
        script = script.replace(old, new, 1)
    return script


def mdx_textures(raw: bytes) -> list:
    """Returns lowercased normalized texture paths from an MDX's TEXS chunk."""
    texs = []
    pos = 4
    n = len(raw)
    while pos + 8 <= n:
        tag = raw[pos:pos + 4]
        sz, = struct.unpack_from("<I", raw, pos + 4)
        pos += 8
        if tag == b"TEXS":
            end = min(n, pos + sz)
            p = pos
            while p + 268 <= end:
                path = raw[p + 4:p + 264].split(b"\x00", 1)[0].decode("latin1", errors="ignore").strip()
                if path:
                    texs.append(path.lower().replace("/", "\\"))
                p += 268
            break
        pos += sz
    return texs


def collect_orphan_deletes(arch: mpq.MPQ, modified_files: dict) -> list:
    """Collects strictly unreferenced orphan .mdx/.blp/.tga files safe to delete from MPQ."""
    mod_lower = {k.lower().replace("/", "\\"): v for k, v in modified_files.items()}
    names = arch.listfile()
    all_files = {}
    for nm in names:
        hi = arch.find_hash(nm)
        if hi is None:
            continue
        bi = arch.hash_table[hi][4]
        if bi >= len(arch.block_table):
            continue
        kl = nm.lower().replace("/", "\\")
        data = mod_lower[kl] if kl in mod_lower else arch.read_block(bi, nm)
        all_files[kl] = (nm, data)

    # Concatenate every non-asset metadata file for reference scanning
    meta_parts = []
    for kl, (nm, data) in all_files.items():
        if not kl.endswith((".blp", ".mdx", ".tga", ".mp3", ".wav", ".ttf")):
            meta_parts.append(data.lower().replace(b"/", b"\\").replace(b"\\\\", b"\\"))
    meta_blob = b"\n".join(meta_parts)

    # Pass 1: all live MDXs (referenced by path OR stem >= 4 chars, plus *_portrait.mdx)
    live_mdx = set()
    for kl in all_files:
        if kl.endswith(".mdx"):
            base_no_ext = kl[:-4].encode("latin1", errors="ignore")
            stem = os.path.splitext(os.path.basename(kl))[0].encode("latin1", errors="ignore")
            if base_no_ext in meta_blob or (len(stem) >= 4 and stem in meta_blob):
                live_mdx.add(kl)
    for kl in list(live_mdx):
        pk = kl[:-4] + "_portrait.mdx"
        if pk in all_files:
            live_mdx.add(pk)

    # Pass 2: all textures referenced by live MDXs (exact path, war3mapImported\ fallback, and root basename if bare)
    live_tex_exact = set()
    for kl in live_mdx:
        for tx in mdx_textures(all_files[kl][1]):
            live_tex_exact.add(tx)
            if not tx.startswith("war3mapimported\\"):
                live_tex_exact.add("war3mapimported\\" + tx)
            if "\\" not in tx:
                live_tex_exact.add(tx)
            # Some MDX files omit extension or use .tga/.blp interchangeably
            if tx.endswith(".tga"):
                live_tex_exact.add(tx[:-4] + ".blp")
                live_tex_exact.add("war3mapimported\\" + tx[:-4] + ".blp")
            elif tx.endswith(".blp"):
                live_tex_exact.add(tx[:-4] + ".tga")

    deletes = []
    for kl, (nm, _data) in all_files.items():
        # Never touch icons, UI, Units, Scripts, root war3map* system files, or fonts
        if kl.startswith(("replaceabletextures\\", "ui\\", "units\\", "scripts\\")):
            continue
        if kl.startswith("war3map") and not kl.startswith("war3mapimported\\"):
            continue
        if kl.startswith("("):
            continue
        if kl.endswith(".mdx"):
            if kl not in live_mdx:
                deletes.append(nm)
        elif kl.endswith((".blp", ".tga")):
            kb = kl.encode("latin1", errors="ignore")
            base_no_ext = kl[:-4].encode("latin1", errors="ignore")
            if kl not in live_tex_exact and kb not in meta_blob and base_no_ext not in meta_blob:
                deletes.append(nm)
    return deletes


def decode_blp1_jpeg(raw: bytes):
    """Decodes a WC3 BLP1-JPEG texture to (RGBA uint8 ndarray, alpha_bits, extra)."""
    if len(raw) < 164 or raw[:4] != b"BLP1":
        raise ValueError("Not a BLP1 file")
    comp, abits, w, h, extra, _has_mip = struct.unpack_from("<IIIIII", raw, 4)
    if comp != 0:
        raise ValueError("Not BLP1-JPEG")
    offs = struct.unpack_from("<16I", raw, 28)
    sizes = struct.unpack_from("<16I", raw, 92)
    hsz, = struct.unpack_from("<I", raw, 156)
    jhdr = raw[160:160 + hsz]
    jbody = raw[offs[0]:offs[0] + sizes[0]]
    im = Image.open(io.BytesIO(jhdr + jbody))
    arr = 255 - np.array(im, dtype=np.uint8)
    if arr.ndim == 2:
        rgba = np.stack([arr, arr, arr, np.full_like(arr, 255)], axis=-1)
    elif arr.shape[2] == 3:
        rgba = np.concatenate([arr[..., ::-1], np.full(arr.shape[:2] + (1,), 255, dtype=np.uint8)], axis=-1)
    else:
        rgba = arr.copy()
        rgba[..., 0] = arr[..., 2]
        rgba[..., 2] = arr[..., 0]
    return rgba, abits, extra


def encode_blp1_jpeg(rgba: np.ndarray, abits: int = 8, extra: int = 5, quality: int = 76, max_dim: int = 512) -> bytes:
    """Encodes RGBA ndarray into WC3-compatible BLP1-JPEG (4-ch BGRA/CMYK, subsampling=0, full mipmaps)."""
    h, w = rgba.shape[:2]
    if w > max_dim or h > max_dim:
        scale = min(max_dim / float(w), max_dim / float(h))
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))
        rgba = np.array(Image.fromarray(rgba, mode="RGBA").resize((nw, nh), Image.LANCZOS), dtype=np.uint8)
        h, w = rgba.shape[:2]

    mips = []
    cur = rgba
    while True:
        bgra = cur.copy()
        bgra[..., 0] = cur[..., 2]
        bgra[..., 2] = cur[..., 0]
        cmyk = Image.fromarray(255 - bgra, mode="CMYK")
        buf = io.BytesIO()
        cmyk.save(buf, format="JPEG", quality=quality, subsampling=0, optimize=True)
        mips.append(buf.getvalue())
        if len(mips) == 16 or (cur.shape[0] == 1 and cur.shape[1] == 1):
            break
        nh = max(1, cur.shape[0] // 2)
        nw = max(1, cur.shape[1] // 2)
        cur = np.array(Image.fromarray(cur, mode="RGBA").resize((nw, nh), Image.LANCZOS), dtype=np.uint8)

    sof_idx = mips[0].find(b"\xff\xc0")
    if sof_idx <= 2 or sof_idx > 624:
        raise ValueError(f"Invalid BLP1 JPEG shared header size: {sof_idx}")
    jhdr = mips[0][:sof_idx]
    bodies = []
    for m in mips:
        if not m.startswith(jhdr):
            raise ValueError("Mipmap shared JPEG header mismatch")
        bodies.append(m[len(jhdr):])

    base_off = 160 + len(jhdr)
    offs = [0] * 16
    sizes = [0] * 16
    cur_off = base_off
    for i, b in enumerate(bodies):
        offs[i] = cur_off
        sizes[i] = len(b)
        cur_off += len(b)

    out = bytearray()
    out += b"BLP1"
    out += struct.pack("<IIIIII", 0, abits, w, h, extra, 1)
    out += struct.pack("<16I", *offs)
    out += struct.pack("<16I", *sizes)
    out += struct.pack("<I", len(jhdr))
    out += jhdr
    for b in bodies:
        out += b
    return bytes(out)


def optimize_live_blps(arch: mpq.MPQ, delete_names: list, min_size: int = 90_000, quality: int = 76, max_dim: int = 512):
    """Re-encodes oversized live BLP1-JPEG textures, returning ({name: bytes}, stats_dict)."""
    del_set = {d.lower().replace("/", "\\") for d in delete_names}
    optimized = {}
    saved_bytes = 0
    count = 0
    for nm in arch.listfile():
        kl = nm.lower().replace("/", "\\")
        if kl in del_set or not kl.endswith(".blp"):
            continue
        if kl.startswith(("replaceabletextures\\", "ui\\")):
            continue
        hi = arch.find_hash(nm)
        if hi is None:
            continue
        bi = arch.hash_table[hi][4]
        if bi >= len(arch.block_table):
            continue
        raw = arch.read_block(bi, nm)
        if len(raw) < 164 or raw[:4] != b"BLP1":
            continue
        comp, abits, w, h, extra, _ = struct.unpack_from("<IIIIII", raw, 4)
        if comp != 0:
            continue
        if len(raw) < min_size and w <= max_dim and h <= max_dim:
            continue
        try:
            rgba, ab, ex = decode_blp1_jpeg(raw)
            reenc = encode_blp1_jpeg(rgba, abits=ab, extra=ex, quality=quality, max_dim=max_dim)
            # Round-trip decode sanity check
            decode_blp1_jpeg(reenc)
        except Exception:
            continue
        # Only replace if resized from > max_dim OR saves at least 25%
        if (w > max_dim or h > max_dim) or len(reenc) <= int(len(raw) * 0.75):
            if len(reenc) < len(raw):
                optimized[nm] = reenc
                saved_bytes += len(raw) - len(reenc)
                count += 1
    return optimized, {"blps_optimized": count, "raw_bytes_saved": saved_bytes}


def save_compact(arch: mpq.MPQ, out_path: str, replace_files: dict, delete_files=(), extra_listfile=None) -> str:
    """Writes a 100%-compacted MPQ archive with zero dead slack space.

    Preserves every surviving unnamed & encrypted (non-FIX_KEY) block byte-for-byte,
    and keeps the exact hash_table size so unnamed linear-probe chains stay intact.
    """
    b = arch.base
    head = bytearray(arch.raw[:b])  # 512-byte HM3W header
    hash_table = [list(e) for e in arch.hash_table]
    nn = len(hash_table)

    # Verify no F_FIX_KEY blocks exist before relocating offsets
    for bi, (_off, _cs, _fs, fl) in enumerate(arch.block_table):
        if fl & mpq.F_FIX_KEY:
            raise RuntimeError(f"[save_compact] Block {bi} has F_FIX_KEY; cannot relocate raw encrypted bytes safely")

    # 1. Mark deleted files as HASH_DELETED (keeps probe chains intact for colliding unnamed entries)
    for name in delete_files:
        hi = arch.find_hash(name)
        if hi is not None:
            hash_table[hi][0] = hash_table[hi][1] = 0xFFFFFFFF
            hash_table[hi][2] = 0xFFFF
            hash_table[hi][3] = 0xFFFF
            hash_table[hi][4] = mpq.HASH_DELETED

    names = dict(replace_files)
    if extra_listfile is not None:
        names["(listfile)"] = extra_listfile

    # Map existing hash slot -> replaced name (if any)
    replaced_by_hi = {}
    new_additions = []
    for name, content in names.items():
        # Lookup in updated hash_table
        start = mpq.hash_string(name, mpq.HASH_OFFSET) & (nn - 1)
        ha = mpq.hash_string(name, mpq.HASH_A)
        hb = mpq.hash_string(name, mpq.HASH_B)
        i = start
        found_hi = None
        while True:
            e = hash_table[i]
            if e[4] == mpq.HASH_EMPTY:
                break
            if e[0] == ha and e[1] == hb and e[4] < mpq.HASH_DELETED:
                found_hi = i
                break
            i = (i + 1) & (nn - 1)
            if i == start:
                break
        if found_hi is not None:
            replaced_by_hi[found_hi] = (name, content)
        else:
            new_additions.append((name, content))

    # 2. Rebuild contiguous body + new_block_table for all surviving blocks
    body = bytearray(32)  # Reserve 32-byte MPQ header
    new_block_table = []
    old_bi_to_new_bi = {}

    for hi, e in enumerate(hash_table):
        old_bi = e[4]
        if old_bi >= mpq.HASH_DELETED:
            continue
        if hi in replaced_by_hi:
            _nm, content = replaced_by_hi[hi]
            stored = arch._pack_sectors(content)
            flags = mpq.F_EXISTS | mpq.F_COMPRESS
            while len(body) % 4:
                body.append(0)
            off = len(body)
            body += stored
            new_bi = len(new_block_table)
            new_block_table.append([off, len(stored), len(content), flags])
            e[4] = new_bi
        else:
            if old_bi in old_bi_to_new_bi:
                e[4] = old_bi_to_new_bi[old_bi]
            else:
                if old_bi >= len(arch.block_table):
                    continue
                old_off, old_cs, old_fs, old_fl = arch.block_table[old_bi]
                raw_blk = arch.raw[b + old_off:b + old_off + old_cs]
                while len(body) % 4:
                    body.append(0)
                off = len(body)
                body += raw_blk
                new_bi = len(new_block_table)
                new_block_table.append([off, old_cs, old_fs, old_fl])
                old_bi_to_new_bi[old_bi] = new_bi
                e[4] = new_bi

    # 3. Insert any brand-new files into hash_table + new_block_table
    for name, content in new_additions:
        stored = arch._pack_sectors(content)
        flags = mpq.F_EXISTS | mpq.F_COMPRESS
        while len(body) % 4:
            body.append(0)
        off = len(body)
        body += stored
        new_bi = len(new_block_table)
        new_block_table.append([off, len(stored), len(content), flags])

        start = mpq.hash_string(name, mpq.HASH_OFFSET) & (nn - 1)
        ha = mpq.hash_string(name, mpq.HASH_A)
        hb = mpq.hash_string(name, mpq.HASH_B)
        i = start
        slot = None
        while True:
            if hash_table[i][4] in (mpq.HASH_EMPTY, mpq.HASH_DELETED):
                slot = i
                break
            i = (i + 1) & (nn - 1)
            if i == start:
                break
        if slot is None:
            raise RuntimeError("[save_compact] Hash table full")
        hash_table[slot] = [ha, hb, 0, 0, new_bi]

    # 4. Write encrypted hash_table + block_table + MPQ header
    while len(body) % 4:
        body.append(0)
    ht_pos = len(body)
    ht_raw = b"".join(struct.pack("<IIHHI", *e) for e in hash_table)
    body += mpq.encrypt(ht_raw, mpq.hash_string("(hash table)", mpq.HASH_KEY))
    bt_pos = len(body)
    bt_raw = b"".join(struct.pack("<IIII", *e) for e in new_block_table)
    body += mpq.encrypt(bt_raw, mpq.hash_string("(block table)", mpq.HASH_KEY))
    hdr = struct.pack(
        "<4sIIHHIIII",
        b"MPQ\x1a", 32, len(body), 0, arch.sector_shift,
        ht_pos, bt_pos, len(hash_table), len(new_block_table),
    )
    body[0:32] = hdr
    with open(out_path, "wb") as f:
        f.write(head)
        f.write(body)
    return out_path
