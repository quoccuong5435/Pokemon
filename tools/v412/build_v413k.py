"""Build Pokemon Arena v4.1.3k on top of v4.1.3j:
1. Soulbound & Drop-on-Death Fix:
   - Common ('ofir') & Rare ('ocor') loot: immediately Soulbound on pickup, never drop on death.
   - Mystery Loot Box (-up), Gamble (-gamble), and Forge (-forge) items: immediately Soulbound on creation.
   - Epic ('oli2') & Legendary ('tgrh') wild drops (+ Legend Souls & Paradox Boosters):
     drop on death ONLY if held < 60s; permanently Soulbound after 60s held in inventory.
   - Fixed dead PAX_SoulboundTick (and PAX_HauntPortalTick) by wiring into PAX_Leg_Tick1s (1s) and
     scanning all living heroes via GroupEnumUnitsOfPlayer instead of null LoadUnitHandle(PAX_Leg_HT, p, 1).
2. First 10 Minutes No Camp Stacking Reinforcement:
   - Wild_ReinforceCamp disabled while Wild_Time < 600.0 (first 10 minutes).
3. -up Mystery Loot Box Rates:
   - Common 75% | Rare 10% | Epic 3% | Legendary 0.5% | Empty Box 11.5%.
4. Vitamin Shop 999s Cooldown Bug Fix:
   - Fixed ItemData.slk stockStart='999' -> '0' (stockMax='100', stockRegen='1') for I000..I006.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, HERE)

import mpq  # noqa: E402
import objdata  # noqa: E402
import slk  # noqa: E402
import v413k_fixes  # noqa: E402

BS = chr(92)
BASE_MAP = os.path.join(MAPS, "Pokemon Arena v4.1.3j.w3x")
NAME = "v4.1.3k"
OUT_MAP = os.path.join(MAPS, f"Pokemon Arena {NAME}.w3x")
PJASS = r"D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe"
REF = os.path.join(WORK, "analysis", "jass_ref")


def build_data():
    base = mpq.MPQ(BASE_MAP)
    script = base.read("scripts" + BS + "war3map.j").decode("utf-8")
    crlf = "\r\n" in script
    script = script.replace("\r\r\n", "\r\n").replace("\r\n", "\n")

    items = slk.Slk(base.read("Units" + BS + "ItemData.slk").decode("latin-1"))
    w3u = objdata.ObjFile(base.read("war3map.w3u"))

    script = v413k_fixes.patch_script(script)
    v413k_fixes.patch_items_slk(items)
    v413k_fixes.patch_w3u_bosses(w3u)

    script = script.replace("v4.1.3j", NAME)
    if crlf:
        script = script.replace("\n", "\r\n")

    w3i = base.read("war3map.w3i").replace(b"4.1.3j", b"4.1.3k")

    files = {
        "scripts" + BS + "war3map.j": script.encode("utf-8"),
        "war3map.w3i": w3i,
        "war3map.w3u": w3u.to_bytes(),
        "Units" + BS + "ItemData.slk": items.to_text().encode("latin-1"),
    }
    files.update(v413k_fixes.load_zekrom_fix_assets(mpq))
    return base, files, script, items, w3u


def build(out, dry, skip_pjass=False):
    if not dry and os.path.exists(out):
        raise SystemExit(f"Output exists, refusing to overwrite per GEMINI.md: {out}")

    base, files, script, _, _ = build_data()
    tmp = os.path.join(REF, "_tmp_v413k_war3map.j")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(script)

    if not skip_pjass and os.path.exists(PJASS):
        try:
            r = subprocess.run(
                [PJASS, os.path.join(REF, "common.j"), os.path.join(REF, "Blizzard.j"), tmp],
                capture_output=True,
                text=True,
            )
            print("PJASS rc=%d" % r.returncode)
            if r.returncode:
                print((r.stdout + r.stderr)[:1500])
                raise SystemExit(1)
        except OSError as e:
            print(f"[pjass skipped due to OS sandbox error: {e}]")

    print("Total files modified for %s: %d" % (NAME, len(files)))
    if dry:
        print("Dry run OK.")
        return

    listfile = sorted(set(base.listfile()) | set(files))
    mpq.discover_names = lambda archive, extra=(): set(archive.listfile()) | set(extra)
    hsize = len(base.hash_table)
    while len(base.hash_table) - sum(1 for e in base.hash_table if e[4] == 0xFFFFFFFF) + len(files) > hsize * 3 // 4:
        hsize *= 2
    base.save_with(
        out,
        files,
        extra_listfile=("\r\n".join(listfile) + "\r\n").encode("latin-1"),
        hash_size=hsize if hsize != len(base.hash_table) else None,
        extra_names=listfile,
    )
    print("Wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1048576.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-pjass", action="store_true")
    ap.add_argument("--out", default=OUT_MAP)
    a = ap.parse_args()
    build(a.out, a.dry_run, a.skip_pjass)
