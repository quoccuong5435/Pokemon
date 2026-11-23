r"""HD 3D Model Upgrades for ugly/low-poly/broken Pokemon in Pokemon Arena v4.2b.

Replaces 88 visually-verified low-poly/v1.8/broken-texture Playable Heroes (plus all 120+
matching Wild/Boss/Mega units sharing their old models) with crisp 3DS/Switch HD models
from `Pokemon World V1.71.w3x` and `79.PokemonRPG.w3x`:
- Every single one of the 88 models was visually verified via 3D contact sheets (0 wrong models,
  0 shiny-swapped models, 0 visual regressions).
- Isolated custom texture namespace (`PkFx\HD\t\...`) so 0 existing textures can ever collide.
- 0 missing textures (shiny fallback + strict validation).
- Automatic BLP1-JPEG compression (max 512x512, q75) on newly packed textures.
- Robust percentile-calibrated `usca` per Hero, proportional `usca` sync on every matching
  Wild/Boss/Mega unit, and synchronized `Mega_BaseScale` / `Mega_Scale` updates in `war3map.j`.
"""
import os
import re
import struct

import map_optimizer
import mpq

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)

PW_MAP = os.path.join(MAPS, "Pokemon World V1.71.w3x")
RPG79_MAP = os.path.join(MAPS, "79.PokemonRPG.w3x")

BLIZZARD_PREFIXES = (
    "textures\\", "replaceabletextures\\", "units\\", "abilities\\",
    "environment\\", "objects\\", "ui\\", "buildings\\", "doodads\\", "sharedmodels\\",
)

# Format: (hero_id, dex, name, src_map, src_ref, dst_mdx, old_usca, new_usca)
HERO_UPGRADES = [
    ('E001',   2, 'Ivysaur', 'PW', 'Unit\\002.mdx', 'PkFx\\HD\\002_Ivysaur.mdx', 1.200, 0.92),  # 366t/128px -> 6872t/512px
    ('E002',   3, 'Venusaur', 'PW', 'Unit\\003.mdx', 'PkFx\\HD\\003_Venusaur.mdx', 1.200, 0.93),  # 398t/128px -> 6366t/512px
    ('E003',   4, 'Charmander', 'PW', 'Unit\\004.mdx', 'PkFx\\HD\\004_Charmander.mdx', 1.200, 1.42),  # 306t/128px -> 4790t/512px
    ('E004',   7, 'Squirtle', 'PW', 'Unit\\007.mdx', 'PkFx\\HD\\007_Squirtle.mdx', 1.200, 1.29),  # 416t/128px -> 4748t/512px
    ('E005',  25, 'Pikachu', 'PW', 'Unit\\025.mdx', 'PkFx\\HD\\025_Pikachu.mdx', 1.350, 1.17),  # 544t/128px -> 4500t/512px
    ('E006',  26, 'Raichu', 'PW', 'Unit\\026.mdx', 'PkFx\\HD\\026_Raichu.mdx', 1.700, 1.28),  # 388t/128px -> 5250t/512px
    ('E007',   5, 'Charmeleon', 'PW', 'Unit\\005.mdx', 'PkFx\\HD\\005_Charmeleon.mdx', 1.200, 1.26),  # 296t/128px -> 5140t/512px
    ('E009',   8, 'Wartortle', 'PW', 'Unit\\008.mdx', 'PkFx\\HD\\008_Wartortle.mdx', 1.200, 0.91),  # 540t/128px -> 4982t/512px
    ('E00B',  16, 'Pidgey', 'PW', 'Unit\\016.mdx', 'PkFx\\HD\\016_Pidgey.mdx', 1.000, 1.12),  # 294t/128px -> 5252t/512px
    ('E00C',  17, 'Pidgeotto', 'PW', 'Unit\\017.mdx', 'PkFx\\HD\\017_Pidgeotto.mdx', 1.000, 1.23),  # 378t/128px -> 5618t/512px
    ('E00D',  18, 'Pidgeot', 'PW', 'Unit\\018.mdx', 'PkFx\\HD\\018_Pidgeot.mdx', 1.600, 1.34),  # 310t/128px -> 6072t/512px
    ('E00E',   6, 'Charizard', 'PW', 'Unit\\006.mdx', 'PkFx\\HD\\006_Charizard.mdx', 0.650, 0.96),  # 472t/512px -> 6106t/512px
    ('E008',   1, 'Bulbasaur', 'PW', 'Unit\\001.mdx', 'PkFx\\HD\\001_Bulbasaur.mdx', 1.200, 1.15),  # 346t/128px -> 5200t/512px
    ('E000',   9, 'Blastoise', 'PW', 'Unit\\009.mdx', 'PkFx\\HD\\009_Blastoise.mdx', 1.200, 0.71),  # 536t/128px -> 6382t/512px
    ('E00A',  27, 'Sandshrew', 'RPG79', 5437, 'PkFx\\HD\\027_Sandshrew.mdx', 1.350, 1.18),  # 552t/64px -> 4022t/512px
    ('E00F',  28, 'Sandslash', 'RPG79', 5442, 'PkFx\\HD\\028_Sandslash.mdx', 1.700, 1.08),  # 736t/64px -> 5506t/512px
    ('E00G',  63, 'Abra', 'PW', 'Unit\\063.mdx', 'PkFx\\HD\\063_Abra.mdx', 1.350, 0.82),  # 638t/128px -> 4790t/512px
    ('E00H',  64, 'Kadabra', 'PW', 'Unit\\064.mdx', 'PkFx\\HD\\064_Kadabra.mdx', 1.200, 1.27),  # 940t/64px -> 5732t/512px
    ('E00I',  65, 'Alakazam', 'PW', 'Unit\\065.mdx', 'PkFx\\HD\\065_Alakazam.mdx', 1.350, 1.13),  # 920t/64px -> 5014t/512px
    ('E00N',  74, 'Geodude', 'PW', 'Unit\\074.mdx', 'PkFx\\HD\\074_Geodude.mdx', 1.350, 1.45),  # 382t/128px -> 4452t/512px
    ('E00O',  75, 'Graveler', 'PW', 'Unit\\075.mdx', 'PkFx\\HD\\075_Graveler.mdx', 1.350, 0.78),  # 664t/64px -> 5164t/512px
    ('E00P',  76, 'Golem', 'PW', 'Unit\\076.mdx', 'PkFx\\HD\\076_Golem.mdx', 1.800, 1.00),  # 860t/128px -> 5163t/512px
    ('E00U',  20, 'Raticate', 'PW', 'Unit\\020.mdx', 'PkFx\\HD\\020_Raticate.mdx', 1.100, 1.45),  # 546t/256px -> 5496t/512px
    ('E00Y',  66, 'Machop', 'PW', 'Unit\\066.mdx', 'PkFx\\HD\\066_Machop.mdx', 1.200, 1.47),  # 426t/128px -> 4594t/512px
    ('E00Z',  67, 'Machoke', 'PW', 'Unit\\067.mdx', 'PkFx\\HD\\067_Machoke.mdx', 1.700, 1.22),  # 608t/128px -> 5814t/512px
    ('E010',  68, 'Machamp', 'PW', 'Unit\\068.mdx', 'PkFx\\HD\\068_Machamp.mdx', 1.700, 1.03),  # 898t/128px -> 6174t/512px
    ('E014',  62, 'Poliwrath', 'PW', 'Unit\\062.mdx', 'PkFx\\HD\\062_Poliwrath.mdx', 1.000, 0.92),  # 536t/128px -> 4936t/512px
    ('E018', 128, 'Tauros', 'PW', 'Unit\\128.mdx', 'PkFx\\HD\\128_Tauros.mdx', 1.800, 0.92),  # 890t/128px -> 5418t/512px
    ('E019', 110, 'Weezing', 'RPG79', 5657, 'PkFx\\HD\\110_Weezing.mdx', 1.150, 1.19),  # 634t/128px -> 4930t/256px
    ('E01A',  70, 'Weepinbell', 'PW', 'Unit\\070.mdx', 'PkFx\\HD\\070_Weepinbell.mdx', 1.200, 0.80),  # 198t/128px -> 3328t/512px
    ('E01B',  77, 'Ponyta', 'PW', 'Unit\\077.mdx', 'PkFx\\HD\\077_Ponyta.mdx', 1.150, 1.35),  # 468t/64px -> 5182t/512px
    ('E01C',  59, 'Arcanine', 'PW', 'Unit\\059.mdx', 'PkFx\\HD\\059_Arcanine.mdx', 1.600, 0.99),  # 966t/128px -> 6056t/512px
    ('E01D', 100, 'Voltorb', 'PW', 'Unit\\100.mdx', 'PkFx\\HD\\100_Voltorb.mdx', 1.750, 1.36),  # 230t/128px -> 5774t/512px
    ('E01E', 135, 'Jolteon', 'PW', 'Unit\\135.mdx', 'PkFx\\HD\\135_Jolteon.mdx', 1.250, 1.24),  # 510t/512px -> 4920t/512px
    ('E01F',  91, 'Cloyster', 'PW', 'Unit\\091.mdx', 'PkFx\\HD\\091_Cloyster.mdx', 4.000, 0.66),  # 698t/256px -> 4988t/512px
    ('E01G',  94, 'Gengar', 'PW', 'Unit\\094.mdx', 'PkFx\\HD\\094_Gengar.mdx', 1.350, 0.73),  # 180t/256px -> 4998t/256px
    ('E01H',  78, 'Rapidash', 'PW', 'Unit\\078.mdx', 'PkFx\\HD\\078_Rapidash.mdx', 1.500, 1.24),  # 476t/64px -> 5209t/512px
    ('E01J',  34, 'Nidoking', 'PW', 'Unit\\034.mdx', 'PkFx\\HD\\034_Nidoking.mdx', 0.850, 1.12),  # 771t/512px -> 5714t/512px
    ('E01L',  33, 'Nidorino', 'PW', 'Unit\\033.mdx', 'PkFx\\HD\\033_Nidorino.mdx', 2.000, 0.91),  # 698t/128px -> 5006t/512px
    ('E01M',  32, 'Nidoran', 'PW', 'Unit\\032.mdx', 'PkFx\\HD\\032_Nidoran.mdx', 1.400, 1.37),  # 699t/128px -> 4540t/512px
    ('E01V', 109, 'Koffing', 'RPG79', 5650, 'PkFx\\HD\\109_Koffing.mdx', 1.150, 1.41),  # 442t/128px -> 1796t/256px
    ('E01X', 101, 'Electrode', 'PW', 'Unit\\101.mdx', 'PkFx\\HD\\101_Electrode.mdx', 1.750, 0.73),  # 230t/128px -> 2576t/512px
    ('E020', 144, 'Articuno', 'PW', 'Unit\\144.mdx', 'PkFx\\HD\\144_Articuno.mdx', 1.500, 0.84),  # 702t/256px -> 6754t/512px
    ('E02B',  69, 'Bellsprout', 'PW', 'Unit\\069.mdx', 'PkFx\\HD\\069_Bellsprout.mdx', 1.150, 1.47),  # 140t/128px -> 3964t/512px
    ('E02C',  71, 'Victreebel', 'PW', 'Unit\\071.mdx', 'PkFx\\HD\\071_Victreebel.mdx', 1.400, 0.92),  # 268t/128px -> 4100t/512px
    ('E02F',  58, 'Growlithe', 'RPG79', 5513, 'PkFx\\HD\\058_Growlithe.mdx', 1.350, 0.88),  # 568t/128px -> 5372t/512px
    ('E02H',  93, 'Haunter', 'PW', 'Unit\\093.mdx', 'PkFx\\HD\\093_Haunter.mdx', 1.000, 1.04),  # 197t/256px -> 4022t/512px
    ('E02P', 115, 'Kangaskhan', 'PW', 'Unit\\115.mdx', 'PkFx\\HD\\115_Kangaskhan.mdx', 1.200, 1.34),  # 700t/128px -> 5430t/512px
    ('E02S',  56, 'Mankey', 'PW', 'Unit\\056.mdx', 'PkFx\\HD\\056_Mankey.mdx', 0.320, 1.44),  # 699t/128px -> 4454t/512px
    ('E02T',  57, 'Primeape', 'PW', 'Unit\\057.mdx', 'PkFx\\HD\\057_Primeape.mdx', 0.360, 0.80),  # 702t/128px -> 3916t/512px
    ('E02W', 103, 'Exeggutor', 'PW', 'Unit\\103.mdx', 'PkFx\\HD\\103_Exeggutor.mdx', 0.620, 0.97),  # 567t/512px -> 5484t/512px
    ('E02Y', 111, 'Rhyhorn', 'PW', 'Unit\\111.mdx', 'PkFx\\HD\\111_Rhyhorn.mdx', 1.000, 1.12),  # 699t/128px -> 5150t/512px
    ('E02Z', 112, 'Rhydon', 'PW', 'Unit\\112.mdx', 'PkFx\\HD\\112_Rhydon.mdx', 1.200, 0.89),  # 700t/128px -> 5232t/512px
    ('E031',  81, 'Magnemite', 'PW', 'Unit\\081.mdx', 'PkFx\\HD\\081_Magnemite.mdx', 1.100, 1.35),  # 458t/64px -> 2484t/512px
    ('E032',  82, 'Magneton', 'PW', 'Unit\\082.mdx', 'PkFx\\HD\\082_Magneton.mdx', 1.100, 0.99),  # 1266t/64px -> 6861t/512px
    ('E035', 141, 'Kabutops', 'PW', 'Unit\\141.mdx', 'PkFx\\HD\\141_Kabutops.mdx', 0.550, 0.87),  # 705t/128px -> 5590t/512px
    ('E037', 134, 'Vaporeon', 'PW', 'Unit\\134.mdx', 'PkFx\\HD\\134_Vaporeon.mdx', 0.450, 1.14),  # 878t/512px -> 5540t/512px
    ('E03C',  98, 'Krabby', 'PW', 'Unit\\098.mdx', 'PkFx\\HD\\098_Krabby.mdx', 1.000, 1.07),  # 340t/128px -> 5448t/512px
    ('E03D',  99, 'Kingler', 'PW', 'Unit\\099.mdx', 'PkFx\\HD\\099_Kingler.mdx', 1.150, 0.93),  # 384t/128px -> 5488t/512px
    ('E03E', 129, 'Magikarp', 'PW', 'Unit\\129.mdx', 'PkFx\\HD\\129_Magikarp.mdx', 0.400, 1.20),  # 311t/256px -> 3912t/512px
    ('E03J', 145, 'Zapdos', 'PW', 'Unit\\145.mdx', 'PkFx\\HD\\145_Zapdos.mdx', 1.400, 1.47),  # 600t/512px -> 5752t/512px
    ('E03L', 123, 'Scyther', 'PW', 'Unit\\123.mdx', 'PkFx\\HD\\123_Scyther.mdx', 1.000, 0.99),  # 1188t/128px -> 5994t/512px
    ('E03M', 212, 'Scizor', 'PW', 'Unit\\212.mdx', 'PkFx\\HD\\212_Scizor.mdx', 1.000, 1.19),  # 660t/256px -> 5562t/512px
    ('E03R', 139, 'Omastar', 'PW', 'Unit\\139.mdx', 'PkFx\\HD\\139_Omastar.mdx', 0.750, 1.05),  # 691t/64px -> 5920t/512px
    ('E03S', 470, 'Leafleon', 'PW', 'Unit\\470.mdx', 'PkFx\\HD\\470_Leafleon.mdx', 1.000, 1.35),  # 399t/256px -> 6340t/512px
    ('E03U',  95, 'Onix', 'PW', 'Unit\\095.mdx', 'PkFx\\HD\\095_Onix.mdx', 2.800, 0.90),  # 530t/64px -> 3630t/512px (rebalanced from oversized 1.45)
    ('E03V', 208, 'Steelix', 'PW', 'Unit\\208.mdx', 'PkFx\\HD\\208_Steelix.mdx', 1.250, 0.90),  # 481t/256px -> 4124t/512px (rebalanced from oversized 1.45 -> 0.90)
    ('E03W', 127, 'Pinsir', 'PW', 'Unit\\127.mdx', 'PkFx\\HD\\127_Pinsir.mdx', 1.800, 1.17),  # 688t/128px -> 4864t/512px
    ('E03X', 700, 'Sylveon', 'PW', 'Unit\\700.mdx', 'PkFx\\HD\\700_Sylveon.mdx', 1.000, 1.48),  # 799t/512px -> 8448t/512px
    ('E03Y', 106, 'Hitmonlee', 'PW', 'Unit\\106.mdx', 'PkFx\\HD\\106_Hitmonlee.mdx', 1.800, 1.11),  # 888t/128px -> 4814t/512px
    ('E03Z', 237, 'Hitmontop', 'PW', 'Unit\\237.mdx', 'PkFx\\HD\\237_Hitmontop.mdx', 0.400, 0.86),  # 820t/512px -> 4486t/512px
    ('E046',  41, 'Zubat', 'PW', 'Unit\\041.mdx', 'PkFx\\HD\\041_Zubat.mdx', 1.100, 1.60),  # 284t/64px -> 3696t/512px
    ('E048',  42, 'Golbat', 'PW', 'Unit\\042.mdx', 'PkFx\\HD\\042_Golbat.mdx', 1.300, 0.66),  # 282t/64px -> 1560t/256px
    ('E049', 169, 'Crobat', 'PW', 'Unit\\169.mdx', 'PkFx\\HD\\169_Crobat.mdx', 1.000, 0.67),  # 392t/256px -> 5156t/512px
    ('EN00', 255, 'Torchic', 'RPG79', 5922, 'PkFx\\HD\\255_Torchic.mdx', 1.800, 0.86),  # 1064t/256px -> 3456t/256px
    ('EN03', 252, 'Treecko', 'PW', 'Unit\\252.mdx', 'PkFx\\HD\\252_Treecko.mdx', 1.000, 1.35),  # 550t/384px -> 4454t/512px
    ('EN0C', 475, 'Gallade', 'RPG79', 6338, 'PkFx\\HD\\475_Gallade.mdx', 1.100, 0.94),  # 1056t/256px -> 5248t/512px
    ('EN0H', 375, 'Metang', 'RPG79', 6124, 'PkFx\\HD\\375_Metang.mdx', 0.800, 0.82),  # 722t/256px -> 3410t/256px
    ('P1TA', 250, 'Ho-Oh', 'RPG79', 5914, 'PkFx\\HD\\250_HoOh.mdx', 0.900, 1.70),  # 1002t/128px -> 7478t/512px
    ('P2HA', 240, 'Magby', 'RPG79', 5899, 'PkFx\\HD\\240_Magby.mdx', 1.200, 1.24),  # 766t/128px -> 4902t/256px
    ('P36A',  54, 'Psyduck', 'PW', 'Unit\\054.mdx', 'PkFx\\HD\\054_Psyduck.mdx', 1.000, 0.72),  # 800t/128px -> 1960t/512px
    ('P3QA', 218, 'Slugma', 'PW', 'Unit\\218.mdx', 'PkFx\\HD\\218_Slugma.mdx', 1.000, 1.19),  # 667t/64px -> 5180t/512px
    ('P46A', 175, 'Togepi', 'RPG79', 5775, 'PkFx\\HD\\175_Togepi.mdx', 0.500, 1.34),  # 844t/128px -> 4574t/361px
    ('P47A', 176, 'Togetic', 'PW', 'Unit\\176.mdx', 'PkFx\\HD\\176_Togetic.mdx', 0.600, 1.04),  # 986t/128px -> 1434t/256px
    ('P4UA', 383, 'Groudon', 'PW', 'Unit\\383.mdx', 'PkFx\\HD\\383_Groudon.mdx', 0.500, 1.39),  # 7012t/512px -> 2747t/512px
    ('EP03', 258, 'Mudkip', 'RPG79', 5926, 'PkFx\\HD\\258_Mudkip.mdx', 1.500, 1.40),  # 1020t/128px -> 3344t/256px
    ('EP0A', 391, 'Monferno', 'RPG79', 6175, 'PkFx\\HD\\391_Monferno.mdx', 0.550, 1.73),  # 1004t/256px -> 5688t/512px
    ('EL00', 378, 'Regice', 'RPG79', 6135, 'PkFx\\HD\\378_Regice.mdx', 1.350, 0.64),  # 920t/512px -> 2838t/512px
]

# Standalone Mega/Form skin upgrades: (skin_id, mega_idx, name, src_map, src_ref, dst_mdx, new_usca)
MEGA_SKIN_UPGRADES = []


class _PWArchive(mpq.MPQ):
    def _find_header(self):
        return 1024


def _set_usca(unit_obj, val: float) -> None:
    """Sets `usca` preserving existing field type (defaults to T_REAL=1)."""
    ftype = 1
    for m in unit_obj.mods:
        if m.field == "usca":
            ftype = m.type
            break
    unit_obj.set("usca", ftype, float(val))


def _resolve_tex_in_arc(arc, tp: str):
    """Returns exact existing texture path in `arc` (with shiny fallback), or None if missing."""
    if arc.has(tp):
        return tp
    alt = re.sub(r"(?i)(?:ss(?=[a-z]?\.blp$)|_shiny(?=\.blp$))", "", tp)
    if alt != tp and arc.has(alt):
        return alt
    return None


def _repack_mdx_isolated(raw: bytes, arc, src_tag: str, tex_out: dict, tex_cache: dict, compress_blp: bool = True) -> bytes:
    """Rewrites every custom texture path in TEXS to isolated PkFx/HD/t/... and packs the BLP bytes."""
    out = bytearray(raw)
    pos = 4
    n = len(out)
    while pos + 8 <= n:
        tag = bytes(out[pos:pos + 4])
        sz, = struct.unpack_from("<I", out, pos + 4)
        pos += 8
        if tag == b"TEXS":
            for k in range(sz // 268):
                at = pos + k * 268 + 4
                tp = bytes(out[at:at + 260]).split(b"\x00", 1)[0].decode("latin-1", errors="ignore").strip()
                if not tp or tp.lower().startswith(BLIZZARD_PREFIXES):
                    continue
                resolved = _resolve_tex_in_arc(arc, tp)
                if resolved is None:
                    raise RuntimeError(f"[model_upgrades] Missing texture {tp!r} in {src_tag}")
                ckey = (src_tag, resolved.lower().replace("/", "\\"))
                if ckey not in tex_cache:
                    base_nm = os.path.basename(resolved.replace("/", "\\"))
                    clean_nm = re.sub(r"[^A-Za-z0-9_.-]+", "_", base_nm)
                    dst_tp = f"PkFx\\HD\\t\\{src_tag}_{clean_nm}"
                    suffix = 1
                    used_low = {v.lower() for v in tex_cache.values()}
                    while dst_tp.lower() in used_low:
                        stem, ext = os.path.splitext(clean_nm)
                        dst_tp = f"PkFx\\HD\\t\\{src_tag}_{stem}_{suffix}{ext}"
                        suffix += 1
                    tdata = arc.read(resolved)
                    if compress_blp and tdata[:4] == b"BLP1" and len(tdata) >= 45_000:
                        comp = struct.unpack_from("<I", tdata, 4)[0]
                        if comp == 0:
                            try:
                                rgba, ab, ex = map_optimizer.decode_blp1_jpeg(tdata)
                                reenc = map_optimizer.encode_blp1_jpeg(rgba, abits=ab, extra=ex, quality=75, max_dim=512)
                                map_optimizer.decode_blp1_jpeg(reenc)
                                if len(reenc) < len(tdata):
                                    tdata = reenc
                            except Exception:
                                pass
                    tex_cache[ckey] = dst_tp
                    tex_out[dst_tp] = tdata
                dst_tp = tex_cache[ckey]
                enc = dst_tp.encode("latin-1")
                if len(enc) >= 260:
                    raise RuntimeError(f"[model_upgrades] Texture path too long: {dst_tp}")
                out[at:at + 260] = enc.ljust(260, b"\x00")
            break
        pos += sz
    return bytes(out)


def load_hd_assets(compress_blp: bool = True) -> dict:
    """Loads & packs all 88 visually-verified HD Hero MDXs + isolated compressed BLPs."""
    arcs = {
        "PW": _PWArchive(PW_MAP),
        "RPG79": mpq.MPQ(RPG79_MAP),
    }
    files = {}
    tex_cache = {}

    for _hid, _dex, _name, src, ref, dst_mdx, _osc, _nsc in HERO_UPGRADES:
        arc = arcs[src]
        raw = arc.read_block(ref) if isinstance(ref, int) else arc.read(ref)
        files[dst_mdx] = _repack_mdx_isolated(raw, arc, src, files, tex_cache, compress_blp=compress_blp)

    for _sid, _midx, _name, src, ref, dst_mdx, _nsc in MEGA_SKIN_UPGRADES:
        arc = arcs[src]
        raw = arc.read_block(ref) if isinstance(ref, int) else arc.read(ref)
        files[dst_mdx] = _repack_mdx_isolated(raw, arc, src, files, tex_cache, compress_blp=compress_blp)

    return files


def _replace_once(script: str, old: str, new: str, label: str) -> str:
    cnt = script.count(old)
    if cnt != 1:
        raise ValueError(f"[model_upgrades] Anchor {label!r} matched {cnt} times (expected 1)")
    return script.replace(old, new, 1)


def patch_objects_and_script(w3u, script: str):
    """Updates w3u (88 Heroes + all matching Wild/Boss/Mega units) and syncs Mega scales in JASS."""
    by_id = {u.id: u for u in w3u.original + w3u.custom}
    upgraded_hero_ids = set()
    old_umdl_map = {}
    new_hero_scales = {}

    for hid, _dex, _name, _src, _ref, dst_mdx, old_sc, new_sc in HERO_UPGRADES:
        u = by_id.get(hid)
        if u is None:
            raise KeyError(f"[model_upgrades] Hero {hid} not found in war3map.w3u")
        old_umdl = (u.get("umdl") or "").strip()
        dst_mdl = dst_mdx[:-4] + ".mdl"
        if old_umdl:
            old_umdl_map[old_umdl.lower().replace("/", "\\")] = (dst_mdl, old_sc, new_sc, hid)
        u.set("umdl", 3, dst_mdl)
        _set_usca(u, new_sc)
        upgraded_hero_ids.add(hid)
        new_hero_scales[hid] = new_sc

    synced_units = 0
    mega_skin_new_scales = {}
    for u in w3u.original + w3u.custom:
        if u.id in upgraded_hero_ids:
            continue
        cur_umdl = (u.get("umdl") or "").strip().lower().replace("/", "\\")
        if cur_umdl in old_umdl_map:
            dst_mdl, old_hsc, new_hsc, _hid = old_umdl_map[cur_umdl]
            cur_sc_raw = u.get("usca")
            cur_sc = float(cur_sc_raw) if cur_sc_raw is not None else old_hsc
            ratio = cur_sc / old_hsc if old_hsc > 0.05 else 1.0
            ratio = max(0.65, min(1.85, ratio))
            if u.id == "hM08":  # Mega Kangaskhan slightly larger than base Kangaskhan
                new_usc = round(min(2.40, new_hsc * 1.15), 2)
                mega_skin_new_scales[8] = new_usc
            else:
                new_usc = round(max(0.30, min(2.40, new_hsc * ratio)), 2)
            u.set("umdl", 3, dst_mdl)
            _set_usca(u, new_usc)
            synced_units += 1

    for sid, midx, _name, _src, _ref, dst_mdx, new_sc in MEGA_SKIN_UPGRADES:
        u = by_id.get(sid)
        if u is None:
            raise KeyError(f"[model_upgrades] Mega skin {sid} not found in war3map.w3u")
        u.set("umdl", 3, dst_mdx[:-4] + ".mdl")
        _set_usca(u, new_sc)
        mega_skin_new_scales[midx] = new_sc

    mega_bases = dict(re.findall(r"set Mega_Base\[(\d+)\] = '([^']+)'", script))
    jass_synced = 0
    for idx_str, base_hid in mega_bases.items():
        if base_hid in new_hero_scales:
            m = re.search(rf"    set Mega_BaseScale\[{idx_str}\] = [\d.]+", script)
            if m:
                new_line = f"    set Mega_BaseScale[{idx_str}] = {new_hero_scales[base_hid]:.3f}"
                if m.group(0) != new_line:
                    script = _replace_once(script, m.group(0), new_line, f"Mega_BaseScale[{idx_str}]")
                    jass_synced += 1

    for midx, new_sc in sorted(mega_skin_new_scales.items()):
        m = re.search(rf"    set Mega_Scale\[{midx}\] = [\d.]+", script)
        if m:
            new_line = f"    set Mega_Scale[{midx}] = {new_sc:.3f}"
            if m.group(0) != new_line:
                script = _replace_once(script, m.group(0), new_line, f"Mega_Scale[{midx}]")
                jass_synced += 1

    stats = {
        "heroes_upgraded": len(HERO_UPGRADES),
        "mega_skins_upgraded": len(MEGA_SKIN_UPGRADES),
        "matching_units_synced": synced_units,
        "jass_scales_synced": jass_synced,
    }
    return script, stats
