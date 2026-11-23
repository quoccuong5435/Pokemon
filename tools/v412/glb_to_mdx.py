"""Converts Draco-compressed .glb 3D models with WebP textures into Warcraft III Reforged .mdx + .blp assets."""
import io
import json
import math
import os
import struct
import sys
import numpy as np
from PIL import Image
import DracoPy

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import glb_rig
import map_optimizer

# Bump when the geometry the converter writes changes: cached conversions (form_assets) are keyed on it.
# 6 = procedural multi-bone rigging for static GLBs + facing/emissive fixes; 5 = rigged GLB skeletons.
CONVERTER_REV = 6

# The Pokemon .glb files face +Z (glTF convention), so the standard mapping makes them face +X. A file that does not
# gets a turn about the up axis here, keyed by the model_name the caller passes ("Pk_<dex>" for G14, "Pk_<key>" for
# forms). Positive = counter-clockwise seen from above (+X turns into +Y).
FACING_FIX_DEG = {
    "Pk_363": 180.0,            # Spheal faces -Z in source glb
    "Pk_369": -90.0,            # Relicanth
    "Pk_electrode-hisui": 90.0, # Faces -Y after standard mapping
    "Pk_iron-treads": 90.0,     # Faces -Y after standard mapping
    "Pk_victreebel-mega": 180.0,# Mega Victreebel faces -Z in source glb
    "Pk_voltorb-hisui": 90.0,   # Faces -Y after standard mapping
    "Pk_zigzagoon-galar": 90.0, # Faces -Y after standard mapping
}

def _euler_quat(roll_x: float = 0.0, pitch_y: float = 0.0, yaw_z: float = 0.0):
    """Returns WC3 unit quaternion (x, y, z, w) from Euler angles in degrees."""
    rx, ry, rz = math.radians(roll_x) * 0.5, math.radians(pitch_y) * 0.5, math.radians(yaw_z) * 0.5
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    qx = sx * cy * cz - cx * sy * sz
    qy = cx * sy * cz + sx * cy * sz
    qz = cx * cy * sz - sx * sy * cz
    qw = cx * cy * cz + sx * sy * sz
    return (qx, qy, qz, qw)


def _yaw(a, deg):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return np.stack([a[:, 0] * c - a[:, 1] * s, a[:, 0] * s + a[:, 1] * c, a[:, 2]], axis=1)

def _node_local(nd):
    """4x4 local matrix of a glTF node (matrix, or translation * rotation * scale)"""
    if "matrix" in nd:
        return np.array(nd["matrix"], dtype=np.float64).reshape(4, 4).T  # glTF stores column-major
    x, y, z, w = nd.get("rotation", [0.0, 0.0, 0.0, 1.0])
    rot = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
    m = np.eye(4)
    m[:3, :3] = rot * np.array(nd.get("scale", [1.0, 1.0, 1.0]), dtype=np.float64)
    m[:3, 3] = nd.get("translation", [0.0, 0.0, 0.0])
    return m


def _read_mat4s(meta, bin_data, accessor_idx):
    acc = meta["accessors"][accessor_idx]
    bv = meta["bufferViews"][acc["bufferView"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride", 64)
    out = []
    for i in range(acc["count"]):
        vals = struct.unpack_from("<16f", bin_data, off + i * stride)
        out.append(np.array(vals, dtype=np.float64).reshape(4, 4).T)
    return out


def _mesh_instances(meta, bin_data):
    """[(node index, mesh index, 4x4 matrix placing that mesh, jmats, skin_idx)] + (world, parent) tree.

    Plain mesh: the node's world matrix. Skinned mesh: the bind pose, world(joint 0) x inverseBind(joint 0)
    (glTF ignores the skinned node's own transform)."""
    nodes = meta.get("nodes", [])
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get("children", []):
            parent[c] = i
    world = {}

    def get_world(i):
        if i not in world:
            local = _node_local(nodes[i])
            world[i] = get_world(parent[i]) @ local if i in parent else local
        return world[i]

    for i in range(len(nodes)):
        get_world(i)

    out = []
    for i, nd in enumerate(nodes):
        if nd.get("mesh") is None:
            continue
        mtx = get_world(i)
        jmats = None
        skin_idx = nd.get("skin")
        if skin_idx is not None:
            skin = meta["skins"][skin_idx]
            joints = skin.get("joints", [])
            if joints:
                if "inverseBindMatrices" in skin:
                    ibms = _read_mat4s(meta, bin_data, skin["inverseBindMatrices"])
                else:
                    ibms = [np.eye(4)] * len(joints)
                jmats = np.stack([get_world(j) @ ibm for j, ibm in zip(joints, ibms)])
                mtx = jmats[0]  # fallback when a primitive has no joint weights
        out.append((i, nd["mesh"], mtx, jmats, skin_idx))
    if not out:  # no node tree: every mesh as it is
        out = [(None, m, np.eye(4), None, None) for m in range(len(meta.get("meshes", [])))]
    return out, world, parent


def _draco_attr(dmesh, prim, name):
    ids = prim["extensions"]["KHR_draco_mesh_compression"].get("attributes", {})
    if name not in ids:
        return None
    a = dmesh.get_attribute_by_unique_id(ids[name])
    return None if not a or a.get("data") is None else np.asarray(a["data"])


_GLTF_DTYPES = {
    5120: (np.int8, 127.0),
    5121: (np.uint8, 255.0),
    5122: (np.int16, 32767.0),
    5123: (np.uint16, 65535.0),
    5125: (np.uint32, None),
    5126: (np.float32, None),
}
_GLTF_COUNTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def _read_accessor(meta, bin_data, acc_idx):
    """Read a glTF 2.0 bufferView accessor (supports strided/interleaved and normalized integer attributes)."""
    acc = meta["accessors"][acc_idx]
    if "bufferView" not in acc:
        return None
    bv = meta["bufferViews"][acc["bufferView"]]
    dt, norm_div = _GLTF_DTYPES[acc["componentType"]]
    n_comp = _GLTF_COUNTS[acc["type"]]
    count = acc["count"]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    elem_bytes = n_comp * np.dtype(dt).itemsize
    stride = bv.get("byteStride") or elem_bytes
    if stride == elem_bytes:
        arr = np.frombuffer(bin_data, dtype=dt, count=count * n_comp, offset=off).reshape(count, n_comp)
    else:
        raw = np.frombuffer(bin_data, dtype=np.uint8, count=count * stride, offset=off).reshape(count, stride)
        arr = np.ascontiguousarray(raw[:, :elem_bytes]).view(dt).reshape(count, n_comp)
    if acc.get("normalized") and norm_div is not None:
        arr = arr.astype(np.float64) / norm_div
        if acc["componentType"] in (5120, 5122):
            arr = np.maximum(arr, -1.0)
    return arr[:, 0] if n_comp == 1 else arr


def convert_glb_to_mdx(glb_bytes: bytes, model_name: str, tex_path_prefix: str, scale_multiplier: float = 100.0,
                       target_size: float | None = None) -> tuple[bytes, dict[str, bytes]]:
    """Converts a .glb byte buffer to (mdx_bytes, dict_of_blp_files {rel_path: blp_bytes}).

    target_size: scale the model so max(height, 0.4 x length) equals it (WC3 units); None = metres x scale_multiplier."""
    magic, ver, length = struct.unpack_from("<III", glb_bytes, 0)
    if magic != 0x46546C67:
        raise ValueError("Invalid glTF magic")

    ch0_len, ch0_type = struct.unpack_from("<II", glb_bytes, 12)
    meta = json.loads(glb_bytes[20:20 + ch0_len].decode("utf-8"))
    ch1_offset = 20 + ch0_len
    ch1_len, ch1_type = struct.unpack_from("<II", glb_bytes, ch1_offset)
    bin_data = glb_bytes[ch1_offset + 8:ch1_offset + 8 + ch1_len]

    # 1. Extract & convert textures to BLP
    blp_files = {}
    tex_paths = []
    images_meta = meta.get("images", [])
    textures_meta = meta.get("textures", [])

    for t_idx, tex_info in enumerate(textures_meta):
        # find image source
        img_src_idx = None
        if "extensions" in tex_info and "EXT_texture_webp" in tex_info["extensions"]:
            img_src_idx = tex_info["extensions"]["EXT_texture_webp"]["source"]
        elif "source" in tex_info:
            img_src_idx = tex_info["source"]

        if img_src_idx is not None and img_src_idx < len(images_meta):
            img_meta = images_meta[img_src_idx]
            bv = meta["bufferViews"][img_meta["bufferView"]]
            img_raw = bin_data[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
            im = Image.open(io.BytesIO(img_raw)).convert("RGBA")
            # Ensure dimensions are power-of-two (max 512 for Warcraft III units)
            w, h = im.size
            nw = min(512, 1 << (w - 1).bit_length())
            nh = min(512, 1 << (h - 1).bit_length())
            if (w, h) != (nw, nh):
                im = im.resize((nw, nh), Image.LANCZOS)
            arr = np.array(im, dtype=np.uint8)
            # Check alpha: if alpha has transparency, keep abits=8; if all opaque, abits=0 or 8
            has_trans = arr[:, :, 3].min() < 250
            abits = 8 if has_trans else 0
            blp_bytes = map_optimizer.encode_blp1_jpeg(arr, abits=abits, quality=80, max_dim=512)
            rel_tex_path = f"{tex_path_prefix}_{t_idx}.blp"
            blp_files[rel_tex_path] = blp_bytes
            tex_paths.append(rel_tex_path)
        else:
            rel_tex_path = f"{tex_path_prefix}_{t_idx}.blp"
            tex_paths.append(rel_tex_path)

    if not tex_paths:
        # Default placeholder texture
        rel_tex_path = f"{tex_path_prefix}_0.blp"
        im = Image.new("RGBA", (64, 64), (200, 200, 200, 255))
        blp_files[rel_tex_path] = map_optimizer.encode_blp1_jpeg(np.array(im), abits=0, quality=75, max_dim=64)
        tex_paths.append(rel_tex_path)

    # 2. Extract & decode all meshes / primitives
    all_verts = []
    geosets_bytes = bytearray()
    geoset_bounds_list = []
    mat_entries = []

    material_to_tex = {}
    material_alpha_mode = {}
    solid_color_tex = {}
    mats_meta = meta.get("materials", [])
    for m_idx, mat_info in enumerate(mats_meta):
        pbr = mat_info.get("pbrMetallicRoughness", {})
        material_alpha_mode[m_idx] = mat_info.get("alphaMode", "OPAQUE")
        if "baseColorTexture" in pbr:
            material_to_tex[m_idx] = pbr["baseColorTexture"].get("index", 0)
        elif "emissiveTexture" in mat_info:
            material_to_tex[m_idx] = mat_info["emissiveTexture"].get("index", 0)
        elif "baseColorFactor" in pbr:
            bcf = pbr["baseColorFactor"]
            rgb = tuple(max(0, min(255, int(round((max(0.0, min(1.0, c)) ** (1.0 / 2.2)) * 255.0)))) for c in bcf[:3])
            if rgb not in solid_color_tex:
                tid = len(tex_paths)
                rel_tp = f"{tex_path_prefix}_{tid}.blp"
                im = Image.new("RGBA", (32, 32), (rgb[0], rgb[1], rgb[2], 255))
                blp_files[rel_tp] = map_optimizer.encode_blp1_jpeg(np.array(im), abits=0, quality=85, max_dim=32)
                tex_paths.append(rel_tp)
                solid_color_tex[rgb] = tid
            material_to_tex[m_idx] = solid_color_tex[rgb]
        else:
            material_to_tex[m_idx] = 0

    # Each mesh is placed by the node that uses it: node scale / rotation / translation (and the skeleton's bind pose
    # for skinned meshes) must be applied, or models come out 100x too big (Seviper: node scale 0.01) or lying on
    # their side (Gastrodon: node rotation -90 deg). 4.3b used the raw mesh coordinates.
    mesh_list, world_bind, parent_map = _mesh_instances(meta, bin_data)
    jobs = []
    for node_idx, mesh_idx_ref, mtx, jmats, skin_idx in mesh_list:
        node_jobs = []
        prims = meta["meshes"][mesh_idx_ref].get("primitives", [])
        for prim in prims:
            if prim.get("mode", 4) != 4:
                continue
            pm_idx = prim.get("material", 0)
            pm_name = mats_meta[pm_idx].get("name", "").lower() if pm_idx < len(mats_meta) else ""
            if "plane" in pm_name and len(prims) > 1:
                continue  # strip stray Blender export floor planes (e.g. zigzagoon-galar)
            if "extensions" in prim and "KHR_draco_mesh_compression" in prim["extensions"]:
                draco_bv = prim["extensions"]["KHR_draco_mesh_compression"]["bufferView"]
                bv = meta["bufferViews"][draco_bv]
                chunk = bin_data[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
                dmesh = DracoPy.decode(chunk)
                pts = np.asarray(dmesh.points, dtype=np.float64).reshape(-1, 3)
                if len(pts) == 0:
                    continue
                nrm = getattr(dmesh, "normals", None)
                nrm = np.asarray(nrm, dtype=np.float64).reshape(-1, 3) if nrm is not None and len(nrm) == len(pts) else None
                uv = getattr(dmesh, "tex_coord", None)
                uv = np.asarray(uv, dtype=np.float64).reshape(-1, 2) if uv is not None and len(uv) == len(pts) else None
                faces = np.asarray(dmesh.faces, dtype=np.int64).reshape(-1, 3)
                jidx = _draco_attr(dmesh, prim, "JOINTS_0") if jmats is not None else None
                wts = _draco_attr(dmesh, prim, "WEIGHTS_0") if jmats is not None else None
            else:
                attrs = prim.get("attributes", {})
                if "POSITION" not in attrs:
                    continue
                pts_raw = _read_accessor(meta, bin_data, attrs["POSITION"])
                if pts_raw is None or len(pts_raw) == 0:
                    continue
                pts = np.asarray(pts_raw, dtype=np.float64).reshape(-1, 3)
                nrm_raw = _read_accessor(meta, bin_data, attrs["NORMAL"]) if "NORMAL" in attrs else None
                nrm = np.asarray(nrm_raw, dtype=np.float64).reshape(-1, 3) if nrm_raw is not None and len(nrm_raw) == len(pts) else None
                uv_raw = _read_accessor(meta, bin_data, attrs["TEXCOORD_0"]) if "TEXCOORD_0" in attrs else None
                uv = np.asarray(uv_raw, dtype=np.float64).reshape(-1, 2) if uv_raw is not None and len(uv_raw) == len(pts) else None
                if "indices" in prim:
                    idx_raw = _read_accessor(meta, bin_data, prim["indices"])
                    faces = np.asarray(idx_raw, dtype=np.int64).reshape(-1, 3)
                else:
                    faces = np.arange((len(pts) // 3) * 3, dtype=np.int64).reshape(-1, 3)
                jidx = _read_accessor(meta, bin_data, attrs["JOINTS_0"]) if (jmats is not None and "JOINTS_0" in attrs) else None
                wts = _read_accessor(meta, bin_data, attrs["WEIGHTS_0"]) if (jmats is not None and "WEIGHTS_0" in attrs) else None
            # node transform, or linear blend skinning in the pose the file is saved in (Seviper is coiled, its bind
            # pose is a straight line); then glTF (Y up, the model FACES +Z, its left side is +X) -> WC3 (Z up, a unit
            # at facing angle 0 faces +X, its left side is +Y): (x, y, z) -> (z, x, y), a pure rotation (det +1).
            if jidx is not None and wts is not None and len(jidx) == len(pts) and len(wts) == len(pts):
                jidx = np.clip(jidx.astype(np.int64).reshape(len(pts), -1), 0, len(jmats) - 1)
                wts = wts.astype(np.float64).reshape(len(pts), -1)
                wts /= np.maximum(wts.sum(axis=1, keepdims=True), 1e-9)
                per_v = np.einsum("vk,vkab->vab", wts, jmats[jidx])  # one 4x4 per vertex
                pts = np.einsum("vab,vb->va", per_v[:, :3, :3], pts) + per_v[:, :3, 3]
                if nrm is not None:
                    nrm = np.einsum("vab,vb->va", per_v[:, :3, :3], nrm)
                    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
                det = np.linalg.det(jmats[0][:3, :3])
            else:
                pts = pts @ mtx[:3, :3].T + mtx[:3, 3]
                if nrm is not None:
                    nrm = nrm @ np.linalg.inv(mtx[:3, :3])
                    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
                det = np.linalg.det(mtx[:3, :3])
            if det < 0:  # mirrored node: keep the faces pointing out
                faces = faces[:, [0, 2, 1]]
            # NPA 1.0 mapped this to (x, -z, y): the nose ended on -Y and every converted model walked sideways.
            pts = np.stack([pts[:, 2], pts[:, 0], pts[:, 1]], axis=1)
            if nrm is not None:
                nrm = np.stack([nrm[:, 2], nrm[:, 0], nrm[:, 1]], axis=1)
            fix = FACING_FIX_DEG.get(model_name, 0.0)
            if fix:
                pts = _yaw(pts, fix)
                if nrm is not None:
                    nrm = _yaw(nrm, fix)
            node_jobs.append((prim, pts, nrm, uv, faces, skin_idx, node_idx, jidx, wts))
        if node_jobs:
            jobs.append(node_jobs)
    if not jobs:
        raise ValueError("No valid vertices found in glb")

    # Size: with target_size the model is scaled so that max(height, 0.4 x length) == target_size (GEMINI.md section 13:
    # usca 1.0 then shows the Pokemon at its target size); otherwise glTF metres x scale_multiplier.
    # It always stands on the ground (lowest point z = 0) and is centred on x / y.
    every = np.concatenate([p for node_jobs in jobs for _pr, p, _n, _u, _f, _s, _ni, _ji, _wi in node_jobs])
    lo, hi = every.min(axis=0), every.max(axis=0)
    size = max(hi[2] - lo[2], 0.4 * max(hi[0] - lo[0], hi[1] - lo[1]))
    k = (target_size / size) if (target_size and size > 0) else scale_multiplier
    shift = np.array([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2]])

    rig = None
    total_h_wc3 = float((hi[2] - lo[2]) * k)
    if glb_rig.is_rigged_glb(meta):
        fix_deg = FACING_FIX_DEG.get(model_name, 0.0)
        rad_f = math.radians(fix_deg)
        cf, sf = math.cos(rad_f), math.sin(rad_f)
        P_zxy = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64)
        R_yaw = np.array([[cf, -sf, 0.0], [sf, cf, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)
        F_mat = np.eye(4, dtype=np.float64)
        F_mat[:3, :3] = k * (R_yaw @ P_zxy)
        F_mat[:3, 3] = -k * shift
        rig = glb_rig.build_skeleton(meta, _read_accessor, bin_data, jobs, world_bind, parent_map, F_mat, total_h_wc3)
    if rig is None:
        geoset_pts_wc3 = [(p - shift) * k for node_jobs in jobs for _pr, p, _n, _u, _f, _s, _ni, _ji, _wi in node_jobs]
        rig = glb_rig.build_procedural_skeleton(geoset_pts_wc3, model_name, total_h_wc3)

    mesh_idx = 0
    for node_jobs in jobs:
        for prim, pts, nrm, uv, raw_faces, _skin_idx, _nidx, _ji, _wi in node_jobs:
            vcount = len(pts)
            if vcount > 65535:
                raise ValueError("geoset with %d vertices (MDX face indices are 16-bit)" % vcount)
            pts = (pts - shift) * k
            pts_wc3 = [tuple(map(float, p)) for p in pts]
            all_verts.extend(pts_wc3)
            nrms_wc3 = [tuple(map(float, n)) for n in nrm] if nrm is not None else [(0.0, 0.0, 1.0)] * vcount
            uvs_wc3 = [(float(a), float(b)) for a, b in uv] if uv is not None else [(0.0, 0.0)] * vcount

            # Flatten faces (triangles)
            flat_indices = []
            for f in raw_faces:
                # Reverse triangle winding if needed for WC3 backface culling
                flat_indices.extend([int(f[0]), int(f[2]), int(f[1])])
            icount = len(flat_indices)

            # Bounding box for this geoset
            xs = [v[0] for v in pts_wc3]
            ys = [v[1] for v in pts_wc3]
            zs = [v[2] for v in pts_wc3]
            min_b = (min(xs), min(ys), min(zs))
            max_b = (max(xs), max(ys), max(zs))
            r = math.sqrt(max(abs(min_b[0]), abs(max_b[0]))**2 + max(abs(min_b[1]), abs(max_b[1]))**2 + max(abs(min_b[2]), abs(max_b[2]))**2)
            gbounds = struct.pack("<7f", r, min_b[0], min_b[1], min_b[2], max_b[0], max_b[1], max_b[2])

            # Sub-chunks of Geoset
            vrtx_data = bytearray()
            for v in pts_wc3:
                vrtx_data += struct.pack("<3f", v[0], v[1], v[2])
            vrtx = b"VRTX" + struct.pack("<I", vcount) + bytes(vrtx_data)

            nrms_data = bytearray()
            for n in nrms_wc3:
                nrms_data += struct.pack("<3f", n[0], n[1], n[2])
            nrms = b"NRMS" + struct.pack("<I", vcount) + bytes(nrms_data)

            ptyp = b"PTYP" + struct.pack("<I", 1) + struct.pack("<I", 4)  # 4 = Triangles
            pcnt = b"PCNT" + struct.pack("<I", 1) + struct.pack("<I", icount)
            pvtx = b"PVTX" + struct.pack("<I", icount) + struct.pack(f"<{icount}H", *flat_indices)
            if rig is not None:
                gndx_bytes, grp_list = rig["geoset_skin_groups"][mesh_idx]
                gndx = b"GNDX" + struct.pack("<I", vcount) + gndx_bytes
                mtgc_vals = [len(grp) for grp in grp_list]
                mats_vals = [b for grp in grp_list for b in grp]
                mtgc = b"MTGC" + struct.pack("<I", len(mtgc_vals)) + struct.pack(f"<{len(mtgc_vals)}I", *mtgc_vals)
                mats = b"MATS" + struct.pack("<I", len(mats_vals)) + struct.pack(f"<{len(mats_vals)}I", *mats_vals)
            else:
                gndx = b"GNDX" + struct.pack("<I", vcount) + (b"\x00" * vcount)  # all vertices attached to group 0
                mtgc = b"MTGC" + struct.pack("<I", 1) + struct.pack("<I", 1)
                mats = b"MATS" + struct.pack("<I", 1) + struct.pack("<I", 0)   # bone 0

            # Material index for this primitive
            prim_mat = prim.get("material", 0)
            target_tex_id = material_to_tex.get(prim_mat, 0)
            if target_tex_id >= len(tex_paths):
                target_tex_id = 0
            amode = material_alpha_mode.get(prim_mat, "OPAQUE")
            flt_mode = 1 if amode in ("MASK", "BLEND") else 0

            # Create Material entry (0x10 = TwoSided + WC3 3D shading enabled, NO 0x01 Unshaded flat plastic look)
            mat_idx = len(mat_entries)
            layer = struct.pack("<IIIIiIf", 28, flt_mode, 0x10, target_tex_id, -1, 0, 1.0)
            lays = b"LAYS" + struct.pack("<I", 1) + layer
            mat_chunk = struct.pack("<III", 12 + len(lays), 0, 0) + lays
            mat_entries.append(mat_chunk)

            hdr = struct.pack("<III", mat_idx, 0, 0) + gbounds + struct.pack("<I", 0)

            uv_data = bytearray()
            for uv in uvs_wc3:
                uv_data += struct.pack("<2f", uv[0], uv[1])
            uvbs = b"UVBS" + struct.pack("<I", vcount) + bytes(uv_data)
            uvas = b"UVAS" + struct.pack("<I", 1) + uvbs

            geoset_data = vrtx + nrms + ptyp + pcnt + pvtx + gndx + mtgc + mats + hdr + uvas
            geoset_total = struct.pack("<I", 4 + len(geoset_data)) + geoset_data
            geosets_bytes += geoset_total
            geoset_bounds_list.append((r, min_b, max_b))
            mesh_idx += 1

    if not all_verts:
        raise ValueError("No valid vertices found in glb")

    # Global Model Bounds
    all_xs = [v[0] for v in all_verts]
    all_ys = [v[1] for v in all_verts]
    all_zs = [v[2] for v in all_verts]
    g_min = (min(all_xs), min(all_ys), min(all_zs))
    g_max = (max(all_xs), max(all_ys), max(all_zs))
    total_h = g_max[2] - g_min[2]
    g_rad = math.sqrt(max(abs(g_min[0]), abs(g_max[0]))**2 + max(abs(g_min[1]), abs(g_max[1]))**2 + max(abs(g_min[2]), abs(g_max[2]))**2)
    global_bounds = struct.pack("<7f", g_rad, g_min[0], g_min[1], g_min[2], g_max[0], g_max[1], g_max[2])

    # 3. Assemble MDX Chunks
    # VERS
    vers = b"VERS" + struct.pack("<I", 4) + struct.pack("<I", 800)

    # MODL
    modl_name = model_name.encode("latin-1")[:80].ljust(80, b"\x00")
    anim_file = b"\x00" * 260
    modl = b"MODL" + struct.pack("<I", 372) + modl_name + anim_file + global_bounds + struct.pack("<I", 150)

    # SEQS
    if rig is not None:
        seqs = rig["seqs"]
    else:
        seqs = [
            ("Stand", 0, 1000, 0.0, 0),
            ("Walk", 1333, 2333, 250.0, 0),
            ("Attack", 2667, 3667, 0.0, 1),
            ("Death", 4000, 5000, 0.0, 1),
        ]
    seq_bytes = bytearray()
    for sname, start, end, movespeed, nonloop in seqs:
        sn = sname.encode("latin-1")[:80].ljust(80, b"\x00")
        seq_bytes += sn
        seq_bytes += struct.pack("<II", start, end)
        seq_bytes += struct.pack("<f", movespeed)
        seq_bytes += struct.pack("<I", nonloop)
        seq_bytes += struct.pack("<fI", 0.0, 0)
        seq_bytes += global_bounds
    seqs_chunk = b"SEQS" + struct.pack("<I", len(seq_bytes)) + bytes(seq_bytes)

    # MTLS
    all_mats_data = b"".join(mat_entries)
    mtls_chunk = b"MTLS" + struct.pack("<I", len(all_mats_data)) + all_mats_data

    # TEXS
    tex_bytes = bytearray()
    for tp in tex_paths:
        enc_tp = tp.encode("latin-1")[:260].ljust(260, b"\x00")
        tex_bytes += struct.pack("<I", 0) + enc_tp + struct.pack("<I", 0)
    texs_chunk = b"TEXS" + struct.pack("<I", len(tex_bytes)) + bytes(tex_bytes)

    # GEOS
    geos_chunk = b"GEOS" + struct.pack("<I", len(geosets_bytes)) + bytes(geosets_bytes)

    if rig is not None:
        bone_chunk = rig["bone_chunk"]
        n_bones = rig["n_bones"]
        piv_pts = rig["bone_pivots"] + [(0.0, 0.0, 0.0), (0.0, 0.0, total_h + 10.0), (0.0, 0.0, total_h * 0.5)]
        pivt_data = bytearray()
        for px, py, pz in piv_pts:
            pivt_data += struct.pack("<3f", px, py, pz)
        pivt_chunk = b"PIVT" + struct.pack("<I", len(pivt_data)) + bytes(pivt_data)
        atch_entries = [
            ("origin Ref", n_bones, 0),
            ("overhead Ref", n_bones + 1, 0),
            ("chest Ref", n_bones + 2, 0),
        ]
    else:
        # BONE: single Root bone with natural subtle breathing & attack movement
        node_name = b"Root".ljust(80, b"\x00")
        node_base = node_name + struct.pack("<III", 0, 0xffffffff, 0x00000100)

        kgtr_keys = [
            # Stand breathing bob
            (0, (0.0, 0.0, 0.0)),
            (500, (0.0, 0.0, max(1.2, total_h * 0.025))),
            (1000, (0.0, 0.0, 0.0)),
            # Walk rhythmic step bounce
            (1333, (0.0, 0.0, 0.0)),
            (1583, (0.0, 0.0, max(3.5, total_h * 0.075))),
            (1833, (0.0, 0.0, 0.0)),
            (2083, (0.0, 0.0, max(3.5, total_h * 0.075))),
            (2333, (0.0, 0.0, 0.0)),
            # Attack coil back + explosive forward lunge (+X)
            (2667, (0.0, 0.0, 0.0)),
            (2820, (-max(2.0, total_h * 0.06), 0.0, 0.0)),
            (3000, (max(5.0, total_h * 0.22), 0.0, max(2.0, total_h * 0.06))),
            (3667, (0.0, 0.0, 0.0)),
            # Death collapse
            (4000, (0.0, 0.0, 0.0)),
            (5000, (-max(5.0, total_h * 0.12), 0.0, -max(8.0, total_h * 0.28))),
        ]
        kgtr_body = struct.pack("<IIi", len(kgtr_keys), 1, -1)
        for time_ms, pos in kgtr_keys:
            kgtr_body += struct.pack("<I3f", time_ms, pos[0], pos[1], pos[2])
        kgtr = b"KGTR" + kgtr_body

        # KGRT: organic breathing sway, walk lean + stride waddle, attack recoil/strike, death topple
        kgrt_keys = [
            (0, _euler_quat(0.0, 0.0, 0.0)),
            (500, _euler_quat(1.2, -2.5, 0.0)),
            (1000, _euler_quat(0.0, 0.0, 0.0)),
            (1333, _euler_quat(0.0, 7.0, 0.0)),
            (1583, _euler_quat(5.0, 10.0, 2.0)),
            (1833, _euler_quat(0.0, 7.0, 0.0)),
            (2083, _euler_quat(-5.0, 10.0, -2.0)),
            (2333, _euler_quat(0.0, 7.0, 0.0)),
            (2667, _euler_quat(0.0, 0.0, 0.0)),
            (2820, _euler_quat(0.0, -10.0, 0.0)),
            (3000, _euler_quat(0.0, 15.0, 0.0)),
            (3667, _euler_quat(0.0, 0.0, 0.0)),
            (4000, _euler_quat(0.0, 0.0, 0.0)),
            (4850, _euler_quat(8.0, -82.0, 0.0)),
            (5000, _euler_quat(8.0, -85.0, 0.0)),
        ]
        kgrt_body = struct.pack("<IIi", len(kgrt_keys), 1, -1)
        for time_ms, q in kgrt_keys:
            kgrt_body += struct.pack("<I4f", time_ms, q[0], q[1], q[2], q[3])
        kgrt = b"KGRT" + kgrt_body

        # KGSC: breathing chest expansion & impact squash
        kgsc_keys = [
            (0, (1.0, 1.0, 1.0)),
            (500, (1.015, 1.015, 1.028)),
            (1000, (1.0, 1.0, 1.0)),
            (1333, (1.02, 1.02, 0.97)),
            (1583, (0.98, 0.98, 1.03)),
            (1833, (1.02, 1.02, 0.97)),
            (2083, (0.98, 0.98, 1.03)),
            (2333, (1.0, 1.0, 1.0)),
            (2667, (1.0, 1.0, 1.0)),
            (2820, (1.04, 1.04, 0.95)),
            (3000, (1.05, 0.98, 1.04)),
            (3667, (1.0, 1.0, 1.0)),
        ]
        kgsc_body = struct.pack("<IIi", len(kgsc_keys), 1, -1)
        for time_ms, sc in kgsc_keys:
            kgsc_body += struct.pack("<I3f", time_ms, sc[0], sc[1], sc[2])
        kgsc = b"KGSC" + kgsc_body

        tracks = kgtr + kgrt + kgsc
        node_len = 4 + len(node_base) + len(tracks)
        # Total bone = inclusiveNodeLen + nodeBase + tracks + geosetId (-1) + geosetAnimId (-1)
        bone_body = struct.pack("<I", node_len) + node_base + tracks + struct.pack("<ii", -1, -1)
        bone_chunk = b"BONE" + struct.pack("<I", len(bone_body)) + bone_body

        # PIVT
        pivt_chunk = b"PIVT" + struct.pack("<I", 12 + 3 * 12) + struct.pack("<3f", 0.0, 0.0, 0.0) + struct.pack("<3f", 0.0, 0.0, 0.0) + struct.pack("<3f", 0.0, 0.0, total_h + 10.0) + struct.pack("<3f", 0.0, 0.0, total_h * 0.5)

        # ATCH
        atch_entries = [
            ("origin Ref", 1, 0),
            ("overhead Ref", 2, 0),
            ("chest Ref", 3, 0),
        ]
    atch_body = bytearray()
    for k, (aname, aoid, apid) in enumerate(atch_entries):
        an = aname.encode("latin-1")[:80].ljust(80, b"\x00")
        node = struct.pack("<I", 96) + an + struct.pack("<III", aoid, apid, 0x00000800)
        # Attachment = inclusiveSize (4) + Node (96) + path (260) + attachmentId (4) = 364.
        # Without the leading size WC3 reads "orig" of "origin Ref" as a size and crashes while loading the map (4.3a).
        att_entry = node + (b"\x00" * 260) + struct.pack("<I", k)
        atch_body += struct.pack("<I", 4 + len(att_entry)) + att_entry

    atch_chunk = b"ATCH" + struct.pack("<I", len(atch_body)) + bytes(atch_body)

    # CAMS: portrait camera aimed from front-right (+X, -Y) toward chest/head
    cam_name = b"Portrait".ljust(80, b"\x00")
    cam_pos = (g_max[0] + max(95.0, total_h * 1.15), -max(35.0, total_h * 0.35), max(45.0, total_h * 0.68))
    cam_tgt = (0.0, 0.0, max(25.0, total_h * 0.55))
    cam_entry = cam_name + struct.pack("<3f3f3f", *cam_pos, 0.785398, 10000.0, 10.0, *cam_tgt)
    cams_body = struct.pack("<I", 4 + len(cam_entry)) + cam_entry
    cams_chunk = b"CAMS" + struct.pack("<I", len(cams_body)) + cams_body

    mdx_bytes = b"MDLX" + vers + modl + seqs_chunk + mtls_chunk + texs_chunk + geos_chunk + bone_chunk + atch_chunk + pivt_chunk + cams_chunk
    return mdx_bytes, blp_files
