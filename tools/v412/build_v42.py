"""Release Pokemon Arena v4.2.w3x from v4.1.3k with updated version strings across:
- 512-byte HM3W lobby header ('Pokemon Arena v4.2')
- war3map.w3i map name & description ('Pokemon Arena v4.2')
- scripts\\war3map.j in-game version strings ('v4.2')
Preserves Pokemon Arena v4.1.3k.w3x untouched per GEMINI.md.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, "tools"))

import mpq  # noqa: E402

BS = chr(92)
SRC_MAP = os.path.join(MAPS, "Pokemon Arena v4.1.3k.w3x")
OUT_MAP = os.path.join(MAPS, "Pokemon Arena v4.2.w3x")
NEW_NAME = "Pokemon Arena v4.2"


def patch_hm3w_header(path: str, new_title: str) -> None:
    with open(path, "r+b") as f:
        hdr = bytearray(f.read(512))
        assert hdr[:4] == b"HM3W", "Not a valid HM3W .w3x file"
        # Existing format: b'HM3W' + uint32(0) + cstring(title) + uint32(flags) + uint32(maxPlayers) + zero padding
        nul = hdr.index(0, 8)
        flags, max_players = struct.unpack_from("<II", hdr, nul + 1)
        new_hdr = bytearray(512)
        new_hdr[:4] = b"HM3W"
        title_b = new_title.encode("utf-8") + b"\x00"
        new_hdr[8:8 + len(title_b)] = title_b
        struct.pack_into("<II", new_hdr, 8 + len(title_b), flags, max_players)
        f.seek(0)
        f.write(new_hdr)


def main():
    if os.path.exists(OUT_MAP):
        raise SystemExit(f"Output exists, refusing to overwrite per GEMINI.md: {OUT_MAP}")

    base = mpq.MPQ(SRC_MAP)
    script = base.read("scripts" + BS + "war3map.j").decode("utf-8")
    script = script.replace("v4.1.3k", "v4.2")
    w3i = base.read("war3map.w3i").replace(b"4.1.3k", b"4.2")

    files = {
        "scripts" + BS + "war3map.j": script.encode("utf-8"),
        "war3map.w3i": w3i,
    }

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    base.save_with(
        OUT_MAP,
        files,
        extra_listfile=("\r\n".join(listfile) + "\r\n").encode("latin-1"),
        extra_names=listfile,
    )
    patch_hm3w_header(OUT_MAP, NEW_NAME)
    print(f"Wrote {OUT_MAP} ({os.path.getsize(OUT_MAP) / 1048576.0:.1f} MB)")


if __name__ == "__main__":
    main()
