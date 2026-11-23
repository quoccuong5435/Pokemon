"""Asset pipeline for all 105 active non-map form models of the 104 kept evolution lines.

Reads active (off == 0) F_* nodes from docs/form-models/cay-pha-he.html and converts/extracts:
- 80 .glb files from <Maps/Download>/imports/pokemon_3d_forms/<key>.glb
- 12 .glb files from <Maps/Download>/imports/pokemon_3d_all/<dex>.glb
- 12 .mdx files from Pokemon World V1.71.w3x (Unit\\2003..2022)
-  1 .mdx file  from PKLegendsv3.2.w3x (MeowthGalarian4.mdx)

Every model is isolated under PkFx\\Forms\\<key>.mdx and PkFx\\Forms\\t\\<key>\\...,
scaled to PokeAPI target_size (usca=1.0 for converted .glb, computed usca for PW/PKL .mdx),
compressed to BLP1-JPEG (max_dim 256 for >=8-texture heavy forms else 512, q=75),
verified via mdx_check, and cached per source file mtime/size for fast incremental rebuilds.
"""
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path[:0] = [os.path.join(WORK, "tools"), HERE]

import form_pokeapi  # noqa: E402
import glb_to_mdx  # noqa: E402
import map_optimizer  # noqa: E402
import mdx_check  # noqa: E402
import model_size_check  # noqa: E402
import mpq  # noqa: E402

CAY_PHA_HE = os.path.join(WORK, "docs", "form-models", "cay-pha-he.html")
PSIZE_JSON = os.path.join(WORK, "tools", "pokeapi", "pokemon_size.json")
FORMS_DIR = os.path.join(MAPS, "imports", "pokemon_3d_forms")
ALL_GLB_DIR = os.path.join(MAPS, "imports", "pokemon_3d_all")
PW_MAP = os.path.join(MAPS, "Pokemon World V1.71.w3x")
PKL_MAP = os.path.join(MAPS, "PKLegendsv3.2.w3x")
CACHE_DIR = os.path.join(HERE, ".form_cache")

BLIZZARD_PREFIXES = (
    "textures\\", "replaceabletextures\\", "units\\", "abilities\\",
    "environment\\", "objects\\", "ui\\", "buildings\\", "doodads\\", "sharedmodels\\",
)

PW_FORMS = {
    "exeggutor-alola": "Unit\\2003.mdx",
    "marowak-alola": "Unit\\2004.mdx",
    "vulpix-alola": "Unit\\2007.mdx",
    "ninetales-alola": "Unit\\2008.mdx",
    "farfetchd-galar": "Unit\\2009.mdx",
    "typhlosion-hisui": "Unit\\2011.mdx",
    "rotom-heat": "Unit\\2014.mdx",
    "rotom-mow": "Unit\\2015.mdx",
    "rotom-frost": "Unit\\2016.mdx",
    "rotom-fan": "Unit\\2017.mdx",
    "rotom-wash": "Unit\\2018.mdx",
    "sneasel-hisui": "Unit\\2022.mdx",
}
PKL_FORMS = {
    "meowth-galar": "MeowthGalarian4.mdx",
}
ALL_GLB_FORMS = {
    "obstagoon": "862.glb",
    "wyrdeer": "899.glb",
    "kleavor": "900.glb",
    "ursaluna": "901.glb",
    "sneasler": "903.glb",
    "great-tusk": "984.glb",
    "scream-tail": "985.glb",
    "flutter-mane": "987.glb",
    "iron-treads": "990.glb",
    "iron-thorns": "995.glb",
    "roaring-moon": "1005.glb",
    "iron-valiant": "1006.glb",
}


class _PWArchive(mpq.MPQ):
    def _find_header(self):
        return 1024


def load_active_tree():
    """Returns parsed JSON `DATA` from cay-pha-he.html and list of active (off==0) families."""
    with open(CAY_PHA_HE, encoding="utf-8") as fh:
        html = fh.read()
    m = re.search(r"const DATA = (\{[\s\S]*?\});", html)
    if not m:
        raise ValueError("[form_assets] const DATA not found in cay-pha-he.html")
    data = json.loads(m.group(1))
    active = [fam for fam in data["families"] if not fam.get("off")]
    return data, active


def _load_size_lookup():
    with open(PSIZE_JSON, encoding="utf-8") as fh:
        ps = json.load(fh)
    by_slug = ps
    by_dex = {}
    for v in ps.values():
        by_dex.setdefault(str(v.get("dex")), v)
    return by_slug, by_dex


def _target_size_for(key: str, dex: int, by_slug: dict, by_dex: dict) -> float:
    base_slug = re.sub(
        r"-(mega(-[xyz])?|gmax|alola|galar|hisui|paldea.*|blade|sunny|rainy|snowy|"
        r"sunshine|east|sandy|trash|world-cap|spiky-eared|ash|heat|wash|frost|fan|mow)$",
        "", key,
    )
    info = by_slug.get(key) or by_slug.get(base_slug) or by_dex.get(str(dex)) or {}
    h_m = float(info.get("height_m", 1.0))
    if key.endswith("-gmax"):
        h_m = max(h_m * 1.5, 4.0)
    elif "-mega" in key:
        h_m = h_m * 1.1
    return round(model_size_check.target_size(h_m), 2)


def _compress_blp(
    tdata: bytes,
    max_dim: int = 512,
    quality: int = 75,
    force_opaque_if_zero: bool = False,
    force_opaque: bool = False,
) -> bytes:
    if len(tdata) < 4 or tdata[:4] != b"BLP1":
        return tdata
    comp = struct.unpack_from("<I", tdata, 4)[0]
    if comp != 0:
        return tdata
    try:
        rgba, ab, ex = map_optimizer.decode_blp1_jpeg(tdata)
        fixed_alpha = False
        if (force_opaque and ab > 0) or (
            force_opaque_if_zero and ab > 0 and (rgba[:, :, 3].max() == 0 or rgba[:, :, 3].mean() < 1)
        ):
            rgba[:, :, 3] = 255
            ab = 0
            fixed_alpha = True
        if fixed_alpha or len(tdata) >= 28_000 or rgba.shape[0] > max_dim or rgba.shape[1] > max_dim:
            reenc = map_optimizer.encode_blp1_jpeg(rgba, abits=ab, extra=ex, quality=quality, max_dim=max_dim)
            map_optimizer.decode_blp1_jpeg(reenc)
            if fixed_alpha or len(reenc) < len(tdata):
                return reenc
    except Exception:
        pass
    return tdata


def _glb_trans_tex_indices(glb_bytes: bytes) -> set:
    """Returns texture indices referenced by non-OPAQUE (MASK/BLEND) materials in a GLB."""
    ch0_len, _ = struct.unpack_from("<II", glb_bytes, 12)
    meta = json.loads(glb_bytes[20:20 + ch0_len].decode("utf-8"))
    trans = set()
    for mat in meta.get("materials", []):
        if mat.get("alphaMode", "OPAQUE") != "OPAQUE":
            bct = mat.get("pbrMetallicRoughness", {}).get("baseColorTexture")
            if isinstance(bct, dict) and "index" in bct:
                trans.add(int(bct["index"]))
    return trans


def _resolve_tex_in_arc(arc, tp: str):
    if arc.has(tp):
        return tp
    alt = re.sub(r"(?i)(?:ss(?=[a-z]?\.blp$)|_shiny(?=\.blp$))", "", tp)
    if alt != tp and arc.has(alt):
        return alt
    return None


def _repack_mdx_isolated(raw: bytes, arc, key: str, max_dim: int = 512, quality: int = 75):
    out = bytearray(raw)
    pos, n = 4, len(out)
    tex_out = {}
    tex_cache = {}
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
                    raise RuntimeError(f"[form_assets] Missing texture {tp!r} for {key}")
                ckey = resolved.lower().replace("/", "\\")
                if ckey not in tex_cache:
                    clean_nm = re.sub(r"[^A-Za-z0-9_.-]+", "_", os.path.basename(ckey))
                    dst_tp = f"PkFx\\Forms\\t\\{key}_{clean_nm}"
                    suffix = 1
                    used = {v.lower() for v in tex_cache.values()}
                    while dst_tp.lower() in used:
                        stem, ext = os.path.splitext(clean_nm)
                        dst_tp = f"PkFx\\Forms\\t\\{key}_{stem}_{suffix}{ext}"
                        suffix += 1
                    tdata = _compress_blp(arc.read(resolved), max_dim=max_dim, quality=quality, force_opaque_if_zero=True)
                    tex_cache[ckey] = dst_tp
                    tex_out[dst_tp] = tdata
                dst_tp = tex_cache[ckey]
                enc = dst_tp.encode("latin-1")
                if len(enc) >= 260:
                    raise RuntimeError(f"[form_assets] Texture path too long: {dst_tp}")
                out[at:at + 260] = enc.ljust(260, b"\x00")
            break
        pos += sz
    return bytes(out), tex_out


def _src_sig(path: str, ref: str = "") -> str:
    st = os.stat(path)
    return hashlib.sha1(f"{path}|{ref}|{st.st_mtime_ns}|{st.st_size}".encode()).hexdigest()[:16]


def _load_cached(key: str, sig: str):
    meta_p = os.path.join(CACHE_DIR, key + ".json")
    if not os.path.isfile(meta_p):
        return None
    try:
        meta = json.load(open(meta_p, encoding="utf-8"))
        if meta.get("sig") != sig:
            return None
        mdx_bytes = open(os.path.join(CACHE_DIR, meta["mdx_file"]), "rb").read()
        tex_dict = {}
        for mpq_path, local_name in meta["tex"].items():
            tex_dict[mpq_path] = open(os.path.join(CACHE_DIR, local_name), "rb").read()
        return mdx_bytes, tex_dict, meta["usca"]
    except Exception:
        return None


def _save_cached(key: str, sig: str, mdx_bytes: bytes, tex_dict: dict, usca: float) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    key_dir = os.path.join(CACHE_DIR, key)
    os.makedirs(key_dir, exist_ok=True)
    mdx_rel = os.path.join(key, "model.mdx")
    with open(os.path.join(CACHE_DIR, mdx_rel), "wb") as fh:
        fh.write(mdx_bytes)
    tex_map = {}
    for idx, (mpq_path, b) in enumerate(tex_dict.items()):
        rel = os.path.join(key, f"t{idx}.blp")
        with open(os.path.join(CACHE_DIR, rel), "wb") as fh:
            fh.write(b)
        tex_map[mpq_path] = rel
    with open(os.path.join(CACHE_DIR, key + ".json"), "w", encoding="utf-8") as fh:
        json.dump({"sig": sig, "mdx_file": mdx_rel, "tex": tex_map, "usca": usca}, fh)


def load_form_assets(compress_blp: bool = True, pack_files: bool = True):
    """Returns `(files_to_pack, form_meta)` for all 105 active non-map form keys.

    Set `pack_files=False` for fast dry-runs/metadata inspection without full conversion.
    """
    _, active = load_active_tree()
    by_slug, by_dex = _load_size_lookup()

    nodes = {}
    for fam in active:
        for nid, n in fam["nodes"].items():
            if nid.startswith("F_") and n.get("st") != "map":
                k = n.get("key", nid[2:])
                nodes[k] = n

    files = {}
    meta = {}
    arcs = {}
    pkl_lf = None

    # The family tree leaves `t` empty for every form: take the types from PokeAPI. A form with neither stops the build
    # (it used to become Normal with the Pressure Ability).
    types_of = {}
    no_types = []
    for key, n in nodes.items():
        types = list(n.get("t") or [])
        if not types:
            rec = form_pokeapi.pokemon(key)
            types = list(rec["types"]) if rec else []
        if types:
            types_of[key] = types
        else:
            no_types.append(key)
    if no_types:
        raise RuntimeError("[form_assets] no types (empty tree `t` and no PokeAPI record, see "
                           "tools/pokeapi/fetch_forms.py) for: " + ", ".join(sorted(no_types)))

    for key, n in sorted(nodes.items()):
        dst_mdx = f"PkFx\\Forms\\{key}.mdx"
        tgt = _target_size_for(key, n.get("d", 1), by_slug, by_dex)
        m_info = {
            "key": key,
            "dex": int(n.get("d", 0)),
            "name": n.get("n", key),
            "types": types_of[key],
            "hp": bool(n.get("hp")),
            "mdx": dst_mdx,
            "mdl": dst_mdx[:-4] + ".mdl",
            "target_size": tgt,
            "usca": 1.0,
        }

        if key in PW_FORMS:
            ref = PW_FORMS[key]
            sig = _src_sig(PW_MAP, ref)
            cached = _load_cached(key, sig)
            if cached:
                mdx_bytes, tex_dict, usca = cached
            elif pack_files:
                if "PW" not in arcs:
                    arcs["PW"] = _PWArchive(PW_MAP)
                raw = arcs["PW"].read(ref)
                mdx_bytes, tex_dict = _repack_mdx_isolated(raw, arcs["PW"], key)
                h, l = model_size_check.extents(mdx_bytes)
                raw_sz = max(h or 0.0, 0.4 * (l or 0.0)) or tgt
                usca = round(max(0.25, min(3.0, tgt / raw_sz)), 2)
                _save_cached(key, sig, mdx_bytes, tex_dict, usca)
            else:
                mdx_bytes, tex_dict, usca = b"", {}, 1.0
        elif key in PKL_FORMS:
            ref = PKL_FORMS[key]
            sig = _src_sig(PKL_MAP, ref)
            cached = _load_cached(key, sig)
            if cached:
                mdx_bytes, tex_dict, usca = cached
            elif pack_files:
                if "PKL" not in arcs:
                    arcs["PKL"] = mpq.MPQ(PKL_MAP)
                    pkl_lf = {x.lower(): x for x in arcs["PKL"].listfile()}
                exact = pkl_lf[ref.lower()]
                raw = arcs["PKL"].read(exact)
                mdx_bytes, tex_dict = _repack_mdx_isolated(raw, arcs["PKL"], key)
                h, l = model_size_check.extents(mdx_bytes)
                raw_sz = max(h or 0.0, 0.4 * (l or 0.0)) or tgt
                usca = round(max(0.25, min(3.0, tgt / raw_sz)), 2)
                _save_cached(key, sig, mdx_bytes, tex_dict, usca)
            else:
                mdx_bytes, tex_dict, usca = b"", {}, 1.0
        else:
            if key in ALL_GLB_FORMS:
                glb_path = os.path.join(ALL_GLB_DIR, ALL_GLB_FORMS[key])
            else:
                glb_path = os.path.join(FORMS_DIR, key + ".glb")
            if not os.path.isfile(glb_path):
                raise FileNotFoundError(f"[form_assets] Missing source .glb for {key}: {glb_path}")
            # v2 = alpha fix; rev = glb_to_mdx.CONVERTER_REV (2 = faces +X). A model cached before the facing fix
            # (front on -Y, walks sideways) must be converted again.
            sig = _src_sig(glb_path, f"sz={tgt}|comp={int(compress_blp)}|v2|rev={glb_to_mdx.CONVERTER_REV}")
            cached = _load_cached(key, sig)
            if cached:
                mdx_bytes, tex_dict, usca = cached
            elif pack_files:
                with open(glb_path, "rb") as fh:
                    glb_bytes = fh.read()
                trans_idx = _glb_trans_tex_indices(glb_bytes)
                mdx_bytes, raw_tex = glb_to_mdx.convert_glb_to_mdx(
                    glb_bytes, f"Pk_{key}", f"PkFx\\Forms\\t\\{key}", target_size=tgt
                )
                errs = mdx_check.check(mdx_bytes)
                if errs:
                    raise RuntimeError(f"[form_assets] mdx_check failed for {key}: {errs[0]}")
                max_dim = 256 if len(raw_tex) >= 8 else 512
                tex_dict = {}
                for tp, tb in raw_tex.items():
                    m_tid = re.search(r"_(\d+)\.blp$", tp)
                    is_opaque_mat = bool(m_tid and int(m_tid.group(1)) not in trans_idx)
                    tex_dict[tp] = _compress_blp(
                        tb,
                        max_dim=max_dim if compress_blp else 512,
                        quality=75 if compress_blp else 85,
                        force_opaque_if_zero=is_opaque_mat,
                        force_opaque=is_opaque_mat,
                    )
                usca = 1.0
                _save_cached(key, sig, mdx_bytes, tex_dict, usca)
            else:
                mdx_bytes, tex_dict, usca = b"", {}, 1.0

        m_info["usca"] = usca
        meta[key] = m_info
        if pack_files:
            files[dst_mdx] = mdx_bytes
            files.update(tex_dict)

    print(f"[form_assets] Ready {len(meta)} active form models ({len(files)} packed files)")
    return files, meta
