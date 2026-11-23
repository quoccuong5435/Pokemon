"""Render 3D PNG thumbnails of all showcase models in New Pokemon Arena 1.0.w3x
and build docs/model-size-gallery.html showing visuals, scale, on-screen size,
PokeAPI target size, movement type, and any size/hover flags.
"""
import html
import json
import math
import os
import re
import struct
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.dirname(WORK)
sys.path[:0] = [os.path.join(WORK, "tools"), HERE]

import form_assets  # noqa: E402
import map_optimizer  # noqa: E402
import model_size_check  # noqa: E402
import mpq  # noqa: E402
import objdata  # noqa: E402

MAP_PATH = os.path.join(MAPS, "New Pokemon Arena 1.0.w3x")
THUMBS_DIR = os.path.join(WORK, "docs", "model_thumbs")
OUT_HTML = os.path.join(WORK, "docs", "model-size-gallery.html")


def decode_blp_any(raw: bytes):
    """Decodes BLP1 (comp 0 JPEG or comp 1 paletted) to RGBA uint8 array."""
    if len(raw) < 164 or raw[:4] != b"BLP1":
        return None
    comp, abits, w, h, _extra, _mip = struct.unpack_from("<IIIIII", raw, 4)
    if comp == 0:
        try:
            rgba, ab, _ = map_optimizer.decode_blp1_jpeg(raw)
            if ab == 0:
                rgba[:, :, 3] = 255
            return rgba
        except Exception:
            return None
    if comp == 1:
        pal = np.frombuffer(raw, dtype=np.uint8, count=1024, offset=160).reshape(256, 4)
        offs0, = struct.unpack_from("<I", raw, 28)
        npix = w * h
        idx = np.frombuffer(raw, dtype=np.uint8, count=npix, offset=offs0)
        bgra = pal[idx]
        rgba = np.empty((h, w, 4), dtype=np.uint8)
        rgba[..., 0] = bgra[..., 2].reshape(h, w)
        rgba[..., 1] = bgra[..., 1].reshape(h, w)
        rgba[..., 2] = bgra[..., 0].reshape(h, w)
        if abits == 8 and offs0 + npix * 2 <= len(raw):
            alp = np.frombuffer(raw, dtype=np.uint8, count=npix, offset=offs0 + npix).reshape(h, w)
            rgba[..., 3] = alp
        else:
            rgba[..., 3] = 255
        return rgba
    return None


def parse_mdx_meshes(arc: mpq.MPQ, mdx_bytes: bytes):
    """Parses TEXS, MTLS (first layer tex_id + filterMode), and GEOS into list of mesh dicts."""
    pos = 4
    n = len(mdx_bytes)
    tex_paths = []
    mat_info = []  # (tex_id, filter_mode)
    geos = []

    while pos + 8 <= n:
        tag = mdx_bytes[pos:pos + 4]
        sz, = struct.unpack_from("<I", mdx_bytes, pos + 4)
        blk = mdx_bytes[pos + 8:pos + 8 + sz]
        pos += 8 + sz

        if tag == b"TEXS":
            for k in range(len(blk) // 268):
                tp = blk[k * 268 + 4:k * 268 + 264].split(b"\x00", 1)[0].decode("latin1", errors="ignore").strip()
                tex_paths.append(tp)
        elif tag == b"MTLS":
            o = 0
            while o + 12 <= len(blk):
                msz, = struct.unpack_from("<I", blk, o)
                if msz < 12 or o + msz > len(blk):
                    break
                tex_id, flt = 0, 0
                if blk[o + 12:o + 16] == b"LAYS":
                    nl, = struct.unpack_from("<I", blk, o + 16)
                    if nl > 0 and o + 36 <= len(blk):
                        _lsz, flt, _shd, tex_id = struct.unpack_from("<IIII", blk, o + 20)
                mat_info.append((tex_id, flt))
                o += msz
        elif tag == b"GEOS":
            q = 0
            while q + 4 <= len(blk):
                gsz, = struct.unpack_from("<I", blk, q)
                if gsz < 8 or q + gsz > len(blk):
                    break
                sub = blk[q + 4:q + gsz]
                q += gsz
                p = 0
                verts = faces = uvs = None
                mat_id = 0
                while p + 8 <= len(sub):
                    stag = sub[p:p + 4]
                    if stag == b"VRTX":
                        cnt, = struct.unpack_from("<I", sub, p + 4)
                        verts = np.frombuffer(sub, dtype="<f4", count=cnt * 3, offset=p + 8).reshape(cnt, 3).copy()
                        p += 8 + cnt * 12
                    elif stag == b"NRMS":
                        cnt, = struct.unpack_from("<I", sub, p + 4)
                        p += 8 + cnt * 12
                    elif stag in (b"PTYP", b"PCNT", b"MTGC", b"MATS"):
                        cnt, = struct.unpack_from("<I", sub, p + 4)
                        p += 8 + cnt * 4
                    elif stag == b"PVTX":
                        cnt, = struct.unpack_from("<I", sub, p + 4)
                        raw_f = np.frombuffer(sub, dtype="<u2", count=cnt, offset=p + 8)
                        faces = raw_f[: (cnt // 3) * 3].reshape(-1, 3).copy()
                        p += 8 + cnt * 2
                    elif stag == b"GNDX":
                        cnt, = struct.unpack_from("<I", sub, p + 4)
                        p += 8 + cnt
                    elif stag == b"UVAS":
                        nuv, = struct.unpack_from("<I", sub, p + 4)
                        p += 8
                        for ui in range(nuv):
                            if sub[p:p + 4] == b"UVBS":
                                ucnt, = struct.unpack_from("<I", sub, p + 4)
                                if ui == 0:
                                    uvs = np.frombuffer(sub, dtype="<f4", count=ucnt * 2, offset=p + 8).reshape(ucnt, 2).copy()
                                p += 8 + ucnt * 8
                            else:
                                break
                    else:
                        # Geoset header fields: mat_id(4), sel_grp(4), flags(4), bounds(28), n_ext(4), ext*28
                        mat_id = struct.unpack_from("<I", sub, p)[0]
                        n_ext = struct.unpack_from("<I", sub, p + 40)[0]
                        p += 44 + n_ext * 28
                if verts is not None and faces is not None and len(verts) > 0 and len(faces) > 0:
                    if uvs is None or len(uvs) != len(verts):
                        uvs = np.zeros((len(verts), 2), dtype=np.float32)
                    geos.append({"verts": verts, "faces": faces, "uvs": uvs, "mat_id": mat_id})

    # Load textures
    tex_imgs = {}
    for tid, tp in enumerate(tex_paths):
        if not tp:
            continue
        raw_t = None
        for cand in (tp, "war3mapImported\\" + tp):
            if arc.has(cand):
                raw_t = arc.read(cand)
                break
        if raw_t is not None:
            rgba = decode_blp_any(raw_t)
            if rgba is not None:
                tex_imgs[tid] = rgba

    return geos, mat_info, tex_imgs


def render_mdx_thumb(arc: mpq.MPQ, mdx_bytes: bytes, size: int = 136) -> Image.Image | None:
    """Renders a 3/4 isometric textured z-buffered PNG thumbnail of an MDX model."""
    geos, mat_info, tex_imgs = parse_mdx_meshes(arc, mdx_bytes)
    if not geos:
        return None
    solid_geos = []
    for g in geos:
        _tid, flt = mat_info[g["mat_id"]] if g["mat_id"] < len(mat_info) else (0, 0)
        if flt >= 3:
            continue  # skip additive/modulate ground glow/shadow planes
        v = g["verts"]
        if len(v) <= 16 and float(v[:, 2].max() - v[:, 2].min()) < 25.0 and max(float(v[:, 0].max() - v[:, 0].min()), float(v[:, 1].max() - v[:, 1].min())) > 180.0:
            continue
        solid_geos.append(g)
    if solid_geos:
        geos = solid_geos

    all_v = np.concatenate([g["verts"] for g in geos], axis=0)
    lo = all_v.min(axis=0)
    hi = all_v.max(axis=0)
    ctr = np.array([(lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, lo[2]], dtype=np.float32)

    # Rotate 3/4 around Z (+28 deg yaw) and pitch slightly down (22 deg) so front (-Y) faces viewer
    yaw = math.radians(28.0)
    pitch = math.radians(22.0)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    rz = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, sp], [0.0, -sp, cp]], dtype=np.float32)
    rot = rx @ rz

    rot_all = (all_v - ctr) @ rot.T
    rx_min, rx_max = float(rot_all[:, 0].min()), float(rot_all[:, 0].max())
    rz_min, rz_max = float(rot_all[:, 2].min()), float(rot_all[:, 2].max())
    span_x = max(1e-3, rx_max - rx_min)
    span_z = max(1e-3, rz_max - rz_min)
    pad = 12.0
    scale = min((size - 2 * pad) / span_x, (size - 2 * pad) / span_z)
    cx_p = size * 0.5 - (rx_min + rx_max) * 0.5 * scale
    cy_p = size * 0.5 + (rz_min + rz_max) * 0.5 * scale

    color_buf = np.zeros((size, size, 4), dtype=np.uint8)
    z_buf = np.full((size, size), -1e9, dtype=np.float32)

    # Subtle ground shadow ellipse under feet + WC3 +X forward arrow (green)
    gx, gy = int(round(cx_p)), int(round(cy_p))
    if 0 <= gx < size and 0 <= gy < size:
        cv2.ellipse(color_buf, (gx, min(size - 6, gy)), (max(10, int(span_x * scale * 0.34)), max(4, int(span_x * scale * 0.12))), 0, 0, 360, (25, 32, 46, 95), -1)
    arr_len = max(20.0, float(hi[0] - lo[0]) * 0.55)
    p_orig = (np.array([0.0, 0.0, 0.0], dtype=np.float32)) @ rot.T
    p_fwd = (np.array([arr_len, 0.0, 0.0], dtype=np.float32)) @ rot.T
    ax0, ay0 = int(round(p_orig[0] * scale + cx_p)), int(round(cy_p - p_orig[2] * scale))
    ax1, ay1 = int(round(p_fwd[0] * scale + cx_p)), int(round(cy_p - p_fwd[2] * scale))
    if 0 <= ax0 < size and 0 <= ay0 < size and 0 <= ax1 < size and 0 <= ay1 < size:
        cv2.arrowedLine(color_buf, (ax0, min(size - 4, ay0)), (ax1, min(size - 4, ay1)), (74, 222, 128, 220), 2, tipLength=0.28)

    for g in geos:
        pts = (g["verts"] - ctr) @ rot.T
        sx = pts[:, 0] * scale + cx_p
        sy_ = cy_p - pts[:, 2] * scale
        depth = -pts[:, 1]  # larger depth = closer to camera (since -Y faces viewer)

        f = g["faces"]
        valid_f = (f[:, 0] < len(pts)) & (f[:, 1] < len(pts)) & (f[:, 2] < len(pts))
        f = f[valid_f]
        if len(f) == 0:
            continue

        # Backface check / lighting normal
        p0 = pts[f[:, 0]]
        p1 = pts[f[:, 1]]
        p2 = pts[f[:, 2]]
        tri_norm = np.cross(p1 - p0, p2 - p0)
        n_len = np.linalg.norm(tri_norm, axis=1, keepdims=True)
        tri_norm = tri_norm / np.maximum(n_len, 1e-6)
        # Key light from front-top-left
        light = np.clip(0.68 + 0.32 * np.abs(tri_norm[:, 2] * 0.65 - tri_norm[:, 1] * 0.60 + tri_norm[:, 0] * 0.35), 0.45, 1.05)

        tid, flt = mat_info[g["mat_id"]] if g["mat_id"] < len(mat_info) else (0, 0)
        tex = tex_imgs.get(tid)
        uv = g["uvs"]

        # Screen triangle coordinates
        x0, x1, x2 = sx[f[:, 0]], sx[f[:, 1]], sx[f[:, 2]]
        y0, y1, y2 = sy_[f[:, 0]], sy_[f[:, 1]], sy_[f[:, 2]]
        z0, z1, z2 = depth[f[:, 0]], depth[f[:, 1]], depth[f[:, 2]]
        u0, u1, u2 = uv[f[:, 0], 0], uv[f[:, 1], 0], uv[f[:, 2], 0]
        v0, v1, v2 = uv[f[:, 0], 1], uv[f[:, 1], 1], uv[f[:, 2], 1]

        # Sort back-to-front for alpha cutoff safety, and z-buffer per triangle
        tri_z = (z0 + z1 + z2) / 3.0
        order = np.argsort(tri_z)

        if tex is not None:
            th, tw = tex.shape[:2]
            has_alpha = flt in (1, 2, 3, 4) and tex[:, :, 3].min() < 245

        bx0 = np.clip(np.floor(np.minimum(x0, np.minimum(x1, x2))).astype(np.int32), 0, size - 1)
        bx1 = np.clip(np.ceil(np.maximum(x0, np.maximum(x1, x2))).astype(np.int32), 0, size - 1)
        by0 = np.clip(np.floor(np.minimum(y0, np.minimum(y1, y2))).astype(np.int32), 0, size - 1)
        by1 = np.clip(np.ceil(np.maximum(y0, np.maximum(y1, y2))).astype(np.int32), 0, size - 1)

        area = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)

        for ti in order:
            ar = float(area[ti])
            if abs(ar) < 0.05:
                continue
            ix0, ix1, iy0, iy1 = int(bx0[ti]), int(bx1[ti]), int(by0[ti]), int(by1[ti])
            if ix1 < ix0 or iy1 < iy0:
                continue
            # Fast single-pixel splat for sub-pixel triangles
            if ix0 == ix1 and iy0 == iy1:
                tz = float(tri_z[ti])
                if tz <= z_buf[iy0, ix0]:
                    continue
                if tex is not None:
                    uc = int(((float(u0[ti] + u1[ti] + u2[ti]) / 3.0) % 1.0) * (tw - 1))
                    vc = int(((float(v0[ti] + v1[ti] + v2[ti]) / 3.0) % 1.0) * (th - 1))
                    px = tex[vc, uc]
                    if has_alpha and px[3] < 80:
                        continue
                    rgb = np.clip(px[:3].astype(np.float32) * light[ti], 0, 255).astype(np.uint8)
                else:
                    c = int(175 * light[ti])
                    rgb = (c, c, c)
                z_buf[iy0, ix0] = tz
                color_buf[iy0, ix0, :3] = rgb
                color_buf[iy0, ix0, 3] = 255
                continue

            xs_g = np.arange(ix0, ix1 + 1, dtype=np.float32)[None, :] + 0.5
            ys_g = np.arange(iy0, iy1 + 1, dtype=np.float32)[:, None] + 0.5
            inv_ar = 1.0 / ar
            w0 = ((y1[ti] - y2[ti]) * (xs_g - x2[ti]) + (x2[ti] - x1[ti]) * (ys_g - y2[ti])) * inv_ar
            w1 = ((y2[ti] - y0[ti]) * (xs_g - x2[ti]) + (x0[ti] - x2[ti]) * (ys_g - y2[ti])) * inv_ar
            w2 = 1.0 - w0 - w1
            inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
            if not np.any(inside):
                continue
            zz = w0 * z0[ti] + w1 * z1[ti] + w2 * z2[ti]
            z_sub = z_buf[iy0:iy1 + 1, ix0:ix1 + 1]
            vis = inside & (zz > z_sub)
            if not np.any(vis):
                continue

            if tex is not None:
                uu = w0 * u0[ti] + w1 * u1[ti] + w2 * u2[ti]
                vv = w0 * v0[ti] + w1 * v1[ti] + w2 * v2[ti]
                tx = np.clip((np.mod(uu, 1.0) * (tw - 1)).astype(np.int32), 0, tw - 1)
                ty = np.clip((np.mod(vv, 1.0) * (th - 1)).astype(np.int32), 0, th - 1)
                sampled = tex[ty, tx]
                if has_alpha:
                    vis = vis & (sampled[:, :, 3] >= 80)
                    if not np.any(vis):
                        continue
                rgb = np.clip(sampled[:, :, :3].astype(np.float32) * light[ti], 0, 255).astype(np.uint8)
                z_sub[vis] = zz[vis]
                c_sub = color_buf[iy0:iy1 + 1, ix0:ix1 + 1]
                c_sub[vis, :3] = rgb[vis]
                c_sub[vis, 3] = 255
            else:
                c = int(175 * light[ti])
                z_sub[vis] = zz[vis]
                c_sub = color_buf[iy0:iy1 + 1, ix0:ix1 + 1]
                c_sub[vis, :3] = (c, c, c)
                c_sub[vis, 3] = 255

    return Image.fromarray(color_buf, mode="RGBA")


def _slug_for_form(name: str, form_key: str | None) -> str:
    if form_key:
        base = re.sub(
            r"-(mega(-[xyz])?|gmax|alola|galar|hisui|paldea.*|blade|sunny|rainy|snowy|"
            r"sunshine|east|sandy|trash|world-cap|spiky-eared|ash|heat|wash|frost|fan|mow)$",
            "", form_key,
        )
        return form_key, base
    s = model_size_check.slug(name)
    return s, s


def build_gallery():
    os.makedirs(THUMBS_DIR, exist_ok=True)
    with open(os.path.join(WORK, "tools", "pokeapi", "pokemon_size.json"), encoding="utf-8") as fh:
        species = json.load(fh)
    _, active_fams = form_assets.load_active_tree()
    _, form_meta = form_assets.load_form_assets(compress_blp=False, pack_files=False)

    # Reverse map mdl path -> form key
    mdl_to_form = {v["mdl"].lower(): k for k, v in form_meta.items()}

    arc = mpq.MPQ(MAP_PATH)
    w3u = objdata.ObjFile(arc.read("war3map.w3u"))
    by_id = {u.id: u for u in w3u.custom}
    script = arc.read("scripts\\war3map.j").decode("utf-8", "ignore")

    calls = re.findall(r"call Form_ShowOne\('(\w{4})', \"([^\"]+)\"\)", script)
    seen = set()
    entries = []
    for uid, lbl in calls:
        if uid in seen or uid not in by_id:
            continue
        seen.add(uid)
        u = by_id[uid]
        mdl_val = str(u.get("umdl") or "")
        mdl_low = mdl_val.lower()
        fkey = mdl_to_form.get(mdl_low)
        mdx_bytes = model_size_check.read_model(arc, mdl_val)
        h, l = model_size_check.extents(mdx_bytes)
        scale = float(u.get("usca") or 1.0)
        move = str(u.get("umvt") or "(default)")
        fly_h = float(u.get("umvh") or 0.0)
        size = max(h, 0.4 * (l or 0.0)) if h else None
        screen = size * scale if size else None

        # Lookup PokeAPI height
        sp = None
        if fkey:
            s1, s2 = _slug_for_form(lbl, fkey)
            sp = species.get(s1) or species.get(s2)
        if sp is None:
            clean_lbl = re.sub(r"^#\d+\s+", "", lbl.split("(")[0].strip())
            s = model_size_check.slug(clean_lbl)
            sp = species.get(s)
        real_m = float(sp["height_m"]) if sp else None
        if real_m is not None and fkey:
            if fkey.endswith("-gmax"):
                real_m = max(real_m * 1.5, 4.0)
            elif "-mega" in fkey:
                real_m = real_m * 1.1
        target = model_size_check.target_size(real_m) if real_m is not None else None

        flags = []
        if h and (h < 15 or h > 800):
            flags.append(f"model lạ (cao {round(h)})")
        if screen and target:
            if screen > 1.35 * target:
                flags.append("quá to")
            elif screen < 0.70 * target:
                flags.append("quá nhỏ")
        if sp:
            flies = ("flying" in sp["types"]) or ("levitate" in sp["abilities"]) or (fkey in getattr(sys.modules.get("form_expansion"), "FLYING_OR_LEVITATE_KEYS", set()))
            if not flies and (move in ("hover", "fly") or fly_h > 0):
                flags.append(f"lơ lửng sai ({move}, {int(fly_h)})")
            if flies and fly_h > 100:
                flags.append(f"bay quá cao ({int(fly_h)})")

        if uid.startswith("PF"):
            cat = "form"
        elif uid.startswith("hF"):
            cat = "mega_new"
        elif uid.startswith("hG"):
            cat = "gmax"
        elif uid.startswith("hP"):
            cat = "paradox"
        elif uid.startswith("hM"):
            cat = "mega_old"
        else:
            cat = "base"

        # Render thumbnail
        thumb_rel = f"model_thumbs/{uid}.png"
        thumb_abs = os.path.join(THUMBS_DIR, f"{uid}.png")
        img = render_mdx_thumb(arc, mdx_bytes, size=136) if mdx_bytes else None
        if img is not None:
            img.save(thumb_abs)

        entries.append({
            "id": uid,
            "name": lbl,
            "cat": cat,
            "is_new_form": bool(fkey),
            "mdl": mdl_val,
            "thumb": thumb_rel if img is not None else "",
            "real_m": round(real_m, 2) if real_m is not None else None,
            "model_h": round(h) if h else None,
            "model_l": round(l) if l else None,
            "scale": round(scale, 2),
            "screen": round(screen) if screen else None,
            "target": round(target) if target else None,
            "move": move,
            "fly_h": round(fly_h),
            "flags": flags,
        })

    data_json = json.dumps(entries, ensure_ascii=False)
    html_text = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>New Pokemon Arena 1.0 — Thư viện Model 3D & Kích thước ({len(entries)} models)</title>
<style>
:root {{
  --bg: #0f131a; --panel: #181e28; --panel2: #121720; --fg: #eef2f8; --muted: #94a3b8;
  --line: #273142; --accent: #38bdf8; --ok: #4ade80; --warn: #facc15; --bad: #fb7185;
  --mono: ui-monospace, SFMono-Regular, Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 14px/1.45 "Segoe UI", system-ui, sans-serif; }}
.wrap {{ max-width: 1440px; margin: 0 auto; padding: 20px 20px 60px; }}
h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: -0.02em; }}
.sub {{ color: var(--muted); margin: 0 0 14px; font-size: 13px; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 10px 22px; margin-bottom: 14px; padding: 12px 16px; background: var(--panel); border: 1px solid var(--line); border-radius: 10px; }}
.stat strong {{ display: block; font-size: 22px; font-variant-numeric: tabular-nums; }}
.stat span {{ font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
.controls {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 14px; position: sticky; top: 0; z-index: 10; background: var(--bg); padding: 10px 0; border-bottom: 1px solid var(--line); }}
.controls input {{ flex: 1 1 220px; min-width: 180px; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--panel); color: var(--fg); font: inherit; }}
.controls select, .controls button {{ padding: 7px 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--panel); color: var(--fg); cursor: pointer; font: 600 12px/1.2 inherit; }}
.controls button[aria-pressed="true"] {{ background: var(--accent); color: #09111a; border-color: var(--accent); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(225px, 1fr)); gap: 12px; }}
.card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 6px; }}
.card.flagged {{ border-color: rgba(250, 204, 21, 0.55); }}
.thumb-box {{ height: 148px; background: radial-gradient(circle at 50% 65%, #232d3f 0%, var(--panel2) 75%); border-radius: 8px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 6px; position: relative; overflow: hidden; }}
.thumb-box img {{ max-height: 136px; max-width: 136px; object-fit: contain; transition: transform .15s; transform-origin: bottom center; }}
.id-tag {{ position: absolute; top: 6px; left: 7px; font: 600 11px var(--mono); padding: 2px 6px; border-radius: 5px; background: rgba(9,13,20,0.85); color: #cbd5e1; border: 1px solid var(--line); }}
.cat-tag {{ position: absolute; top: 6px; right: 7px; font: 600 10px inherit; padding: 2px 6px; border-radius: 5px; text-transform: uppercase; }}
.cat-form {{ background: #134e4a; color: #5eead4; }}
.cat-mega_new {{ background: #4c1d95; color: #ddd6fe; }}
.cat-gmax {{ background: #881337; color: #fecdd3; }}
.cat-paradox {{ background: #312e81; color: #c7d2fe; }}
.cat-mega_old {{ background: #78350f; color: #fde68a; }}
.cat-base {{ background: #1e293b; color: #94a3b8; }}
.title {{ font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.mdl {{ font: 11px var(--mono); color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.bar-wrap {{ display: flex; flex-direction: column; gap: 3px; font-size: 11px; }}
.bar-track {{ height: 8px; background: var(--panel2); border-radius: 99px; overflow: hidden; position: relative; border: 1px solid var(--line); }}
.bar-fill {{ height: 100%; border-radius: 99px; background: var(--accent); }}
.bar-target {{ position: absolute; top: 0; bottom: 0; width: 2px; background: #fff; opacity: 0.85; }}
.kv {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px 8px; font-size: 11px; color: var(--muted); }}
.kv b {{ color: var(--fg); font-weight: 600; font-family: var(--mono); }}
.flags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: auto; }}
.flag {{ font-size: 10px; padding: 2px 6px; border-radius: 99px; font-weight: 600; }}
.flag.ok {{ background: rgba(74,222,128,0.14); color: var(--ok); }}
.flag.warn {{ background: rgba(250,204,21,0.16); color: var(--warn); }}
</style>
</head>
<body>
<div class="wrap">
  <h1>New Pokemon Arena 1.0 — Thư viện Model 3D & Kích thước</h1>
  <p class="sub">Render trực tiếp từ MPQ của <code>New Pokemon Arena 1.0.w3x</code> (tất cả {len(entries)} model trong <code>-show</code>, gồm 105 model Form/Mega/G-Max/Paradox mới). Vạch trắng trên thanh đo là kích thước mục tiêu PokeAPI.</p>
  <div class="stats" id="stats"></div>
  <div class="controls">
    <input id="q" type="search" placeholder="Tìm theo tên hoặc mã unit (vd: Aegislash, Iron Treads, PF00, hF20)...">
    <button class="fbtn" data-cat="all" aria-pressed="true">Tất cả</button>
    <button class="fbtn" data-cat="new" aria-pressed="false">105 Form mới</button>
    <button class="fbtn" data-cat="form" aria-pressed="false">Regional / Switch (PF)</button>
    <button class="fbtn" data-cat="mega_new" aria-pressed="false">Mega mới (hF)</button>
    <button class="fbtn" data-cat="gmax" aria-pressed="false">G-Max (hG)</button>
    <button class="fbtn" data-cat="paradox" aria-pressed="false">Paradox (hP)</button>
    <button class="fbtn" data-cat="mega_old" aria-pressed="false">Mega cũ (hM)</button>
    <button class="fbtn" data-cat="base" aria-pressed="false">Base 104 dòng</button>
    <button id="flagOnly" aria-pressed="false">Chỉ hiện có cảnh báo</button>
    <button id="propMode" aria-pressed="false" title="Co giãn ảnh theo chiều cao in-game (Trên màn hình / 230)">So tỷ lệ thật</button>
    <select id="sortBy">
      <option value="order">Thứ tự -show</option>
      <option value="screen_desc">Trên màn hình: Lớn -> Nhỏ</option>
      <option value="screen_asc">Trên màn hình: Nhỏ -> Lớn</option>
      <option value="name">Tên A -> Z</option>
    </select>
  </div>
  <div class="sub" id="shownCount"></div>
  <div class="grid" id="grid"></div>
</div>
<script>
const ITEMS = {data_json};
const CAT_LABEL = {{
  form: "Form", mega_new: "Mega+", gmax: "G-Max", paradox: "Paradox", mega_old: "Mega", base: "Base"
}};
let activeCat = "all", flagOnly = false, propMode = false;

function renderStats() {{
  const total = ITEMS.length;
  const newF = ITEMS.filter(x => x.is_new_form).length;
  const flagged = ITEMS.filter(x => x.flags.length > 0).length;
  const missing = ITEMS.filter(x => !x.thumb).length;
  document.getElementById("stats").innerHTML = `
    <div class="stat"><strong>${{total}}</strong><span>Tổng Model (-show)</span></div>
    <div class="stat"><strong>${{newF}}</strong><span>Form / Mega / G-Max / Paradox mới</span></div>
    <div class="stat"><strong>${{total - flagged}}</strong><span>Kích thước & bay chuẩn</span></div>
    <div class="stat"><strong>${{flagged}}</strong><span>Có cảnh báo size/bay</span></div>
    <div class="stat"><strong>${{missing}}</strong><span>Lỗi đọc model</span></div>`;
}}

function render() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  const sortBy = document.getElementById("sortBy").value;
  let list = ITEMS.filter(x => {{
    if (activeCat === "new" && !x.is_new_form) return false;
    else if (activeCat !== "all" && activeCat !== "new" && x.cat !== activeCat) return false;
    if (flagOnly && x.flags.length === 0) return false;
    if (q && !(x.name.toLowerCase().includes(q) || x.id.toLowerCase().includes(q) || x.mdl.toLowerCase().includes(q))) return false;
    return true;
  }});
  if (sortBy === "screen_desc") list = [...list].sort((a,b) => (b.screen||0) - (a.screen||0));
  else if (sortBy === "screen_asc") list = [...list].sort((a,b) => (a.screen||9999) - (b.screen||9999));
  else if (sortBy === "name") list = [...list].sort((a,b) => a.name.localeCompare(b.name));

  document.getElementById("shownCount").textContent = `Đang hiển thị ${{list.length}} / ${{ITEMS.length}} model`;
  const grid = document.getElementById("grid");
  grid.innerHTML = list.map(x => {{
    const pct = Math.min(100, Math.round(((x.screen || 0) / 250) * 100));
    const tpct = x.target ? Math.min(100, Math.round((x.target / 250) * 100)) : null;
    const scaleCss = propMode && x.screen ? `transform: scale(${{Math.max(0.28, Math.min(1.15, x.screen / 210)).toFixed(2)}})` : "";
    const flagsHtml = x.flags.length
      ? x.flags.map(f => `<span class="flag warn">${{f}}</span>`).join("")
      : `<span class="flag ok">Chuẩn (ổn)</span>`;
    return `<div class="card ${{x.flags.length ? "flagged" : ""}}">
      <div class="thumb-box">
        <span class="id-tag">${{x.id}}</span>
        <span class="cat-tag cat-${{x.cat}}">${{CAT_LABEL[x.cat] || x.cat}}</span>
        ${{x.thumb ? `<img loading="lazy" src="${{x.thumb}}" alt="${{x.name}}" style="${{scaleCss}}">` : `<span>No preview</span>`}}
      </div>
      <div class="title" title="${{x.name}}">${{x.name}}</div>
      <div class="mdl" title="${{x.mdl}}">${{x.mdl}}</div>
      <div class="bar-wrap">
        <div style="display:flex;justify-content:space-between;">
          <span>Màn hình: <b>${{x.screen ?? "?"}}</b></span>
          <span>Mục tiêu: <b>${{x.target ?? "-"}}</b> ${{x.real_m ? `(${{x.real_m}}m)` : ""}}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width:${{pct}}%"></div>
          ${{tpct !== null ? `<div class="bar-target" style="left:${{tpct}}%"></div>` : ""}}
        </div>
      </div>
      <div class="kv">
        <span>Model H/L: <b>${{x.model_h ?? "?"}} / ${{x.model_l ?? "?"}}</b></span>
        <span>Scale: <b>${{x.scale.toFixed(2)}}</b></span>
        <span>Di chuyển: <b>${{x.move}}</b></span>
        <span>Độ cao bay: <b>${{x.fly_h}}</b></span>
      </div>
      <div class="flags">${{flagsHtml}}</div>
    </div>`;
  }}).join("");
}}

document.querySelectorAll(".fbtn").forEach(btn => btn.addEventListener("click", () => {{
  activeCat = btn.dataset.cat;
  document.querySelectorAll(".fbtn").forEach(b => b.setAttribute("aria-pressed", b === btn));
  render();
}}));
document.getElementById("flagOnly").addEventListener("click", e => {{
  flagOnly = !flagOnly;
  e.currentTarget.setAttribute("aria-pressed", flagOnly);
  render();
}});
document.getElementById("propMode").addEventListener("click", e => {{
  propMode = !propMode;
  e.currentTarget.setAttribute("aria-pressed", propMode);
  render();
}});
document.getElementById("q").addEventListener("input", render);
document.getElementById("sortBy").addEventListener("change", render);
renderStats();
render();
</script>
</body>
</html>"""

    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html_text)
    print(f"Wrote {OUT_HTML} ({len(entries)} models, {sum(1 for e in entries if e['thumb'])} rendered PNGs)")


if __name__ == "__main__":
    build_gallery()
