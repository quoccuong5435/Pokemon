"""Skeleton & animation extraction for rigged glTF (.glb) -> Warcraft III MDX 800.

Handles multi-skin glTF rigs (e.g. Legends Z-A / SV / Blender exports):
1. Collects all used skin joint nodes across all skins (plus animated mesh parent nodes),
   skipping UV-scroll helper nodes (CusAnimMat_*).
2. Collapses fine micro-bones (eyelids, fingers, toes) up to <= MAX_BONES major bones so every
   WC3 geoset stays well within the 255 uint8 GNDX vertex-group limit and keeps files compact.
3. Selects Stand, Walk, Attack, Death clips from glTF animations (removing horizontal Walk root
   drift so WC3 unit movement doesn't rubberband). If a rigged model has no Walk/Run clip in
   the .glb, synthesizes a real multi-bone limb gait on its actual leg/arm/wing/spine/tail bones.
4. Converts glTF animation transforms into exact WC3 bone-local KGTR/KGRT/KGSC deltas around PIVT.
"""
import math
import re
import struct
import numpy as np

MAX_BONES = 34
MAX_GEOSET_GROUPS = 240

# Exact sequence windows matching WC3 conventions
SEQ_WINDOWS = [
    ("Stand", 0, 1200, 0.0, 0),
    ("Walk", 1500, 2500, 250.0, 0),
    ("Attack", 2800, 3700, 0.0, 1),
    ("Death", 4000, 5000, 0.0, 1),
]
SAMPLE_COUNTS = {"Stand": 9, "Walk": 13, "Attack": 10, "Death": 8}

_KEEP_KW = (
    "root", "origin", "waist", "hip", "pelvis", "spine", "chest", "torso", "body",
    "neck", "head", "jaw", "thigh", "upperleg", "calf", "lowerleg", "shin", "leg",
    "foot", "ankle", "shoulder", "clavicle", "upperarm", "forearm", "arm", "hand",
    "wing", "tail", "fin", "ear",
)
_DROP_KW = (
    "eyelid", "eye_", "_eye", "pupil", "iris", "brow", "lash", "lip", "tooth", "teeth",
    "tongue", "mouth", "finger", "thumb", "index", "middle", "ring", "pinky", "toe",
    "claw", "cusanimmat", "_end", "cheek", "nostril",
)


def _quat_to_mat3(q) -> np.ndarray:
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return np.eye(3)
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ], dtype=np.float64)


def _mat3_to_quat(R: np.ndarray) -> np.ndarray:
    tr = R[0, 0] + R[1, 1] + R[2, 2]
    if tr > 0.0:
        s = 2.0 * math.sqrt(tr + 1.0)
        q = np.array([(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, 0.25 * s])
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * math.sqrt(max(1e-12, 1.0 + R[0, 0] - R[1, 1] - R[2, 2]))
        q = np.array([0.25 * s, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s])
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * math.sqrt(max(1e-12, 1.0 + R[1, 1] - R[0, 0] - R[2, 2]))
        q = np.array([(R[0, 1] + R[1, 0]) / s, 0.25 * s, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s])
    else:
        s = 2.0 * math.sqrt(max(1e-12, 1.0 + R[2, 2] - R[0, 0] - R[1, 1]))
        q = np.array([(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, 0.25 * s, (R[1, 0] - R[0, 1]) / s])
    return q / max(np.linalg.norm(q), 1e-12)


def _quat_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ], dtype=np.float64)


def _slerp(q0: np.ndarray, q1: np.ndarray, alpha: float) -> np.ndarray:
    dot = float(np.dot(q0, q1))
    if dot < 0.0:
        q1 = -q1
        dot = -dot
    if dot > 0.9995:
        q = q0 + alpha * (q1 - q0)
        return q / max(np.linalg.norm(q), 1e-12)
    theta0 = math.acos(min(1.0, max(-1.0, dot)))
    theta = theta0 * alpha
    sin_t = math.sin(theta)
    sin_t0 = math.sin(theta0)
    s0 = math.cos(theta) - dot * sin_t / sin_t0
    s1 = sin_t / sin_t0
    return s0 * q0 + s1 * q1


def _sample_channel(times: np.ndarray, vals: np.ndarray, interp: str, path: str, t: float) -> np.ndarray:
    """Samples a pre-decoded glTF animation channel (LINEAR, STEP, or CUBICSPLINE) at time t."""
    if len(times) == 0:
        return None
    stride = 3 if interp == "CUBICSPLINE" else 1

    def _val_at(idx):
        return vals[idx * 3 + 1] if stride == 3 else vals[idx]

    if t <= times[0]:
        v = _val_at(0)
        return v / max(np.linalg.norm(v), 1e-12) if path == "rotation" else v
    if t >= times[-1]:
        v = _val_at(len(times) - 1)
        return v / max(np.linalg.norm(v), 1e-12) if path == "rotation" else v

    hi = int(np.searchsorted(times, t, side="right"))
    lo = max(0, hi - 1)
    hi = min(len(times) - 1, hi)
    dt = float(times[hi] - times[lo])
    if interp == "STEP" or dt < 1e-9:
        v = _val_at(lo)
        return v / max(np.linalg.norm(v), 1e-12) if path == "rotation" else v

    u = (t - float(times[lo])) / dt
    if interp == "CUBICSPLINE" and stride == 3:
        p0 = vals[lo * 3 + 1]
        b0 = vals[lo * 3 + 2] * dt
        p1 = vals[hi * 3 + 1]
        a1 = vals[hi * 3] * dt
        u2, u3 = u * u, u * u * u
        v = (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * b0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * a1
        return v / max(np.linalg.norm(v), 1e-12) if path == "rotation" else v

    v0 = _val_at(lo)
    v1 = _val_at(hi)
    if path == "rotation":
        return _slerp(v0 / max(np.linalg.norm(v0), 1e-12), v1 / max(np.linalg.norm(v1), 1e-12), u)
    return (1.0 - u) * v0 + u * v1


def _decompose_node_trs(nd: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns bind-pose (translation[3], rotation_xyzw[4], scale[3]) for a glTF node."""
    if "matrix" in nd:
        m = np.array(nd["matrix"], dtype=np.float64).reshape(4, 4).T
        tr = m[:3, 3].copy()
        sx = float(np.linalg.norm(m[:3, 0]))
        sy = float(np.linalg.norm(m[:3, 1]))
        sz = float(np.linalg.norm(m[:3, 2]))
        if np.linalg.det(m[:3, :3]) < 0:
            sx = -sx
        rm = np.column_stack([
            m[:3, 0] / (sx if abs(sx) > 1e-9 else 1.0),
            m[:3, 1] / (sy if abs(sy) > 1e-9 else 1.0),
            m[:3, 2] / (sz if abs(sz) > 1e-9 else 1.0),
        ])
        return tr, _mat3_to_quat(rm), np.array([sx, sy, sz], dtype=np.float64)
    tr = np.array(nd.get("translation", [0.0, 0.0, 0.0]), dtype=np.float64)
    rot = np.array(nd.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=np.float64)
    rot = rot / max(np.linalg.norm(rot), 1e-12)
    sc = np.array(nd.get("scale", [1.0, 1.0, 1.0]), dtype=np.float64)
    return tr, rot, sc


def _compose_trs(tr: np.ndarray, rot: np.ndarray, sc: np.ndarray) -> np.ndarray:
    m = np.eye(4, dtype=np.float64)
    m[:3, :3] = _quat_to_mat3(rot) * sc
    m[:3, 3] = tr
    return m


def _pick_clips(anims: list[dict]) -> dict[str, dict | None]:
    """Selects best glTF animation clip for each WC3 sequence (Stand, Walk, Attack, Death)."""
    items = [(idx, (a.get("name") or "").lower(), a) for idx, a in enumerate(anims)]

    def pick(rules):
        for pat, excl in rules:
            for _idx, nm, a in items:
                if pat(nm) and not any(bad in nm for bad in excl):
                    return a
        return None

    stand = pick([
        (lambda s: "00001_battlewait01_loop" in s, ("turn",)),
        (lambda s: "battlewait01_loop" in s, ("turn",)),
        (lambda s: "ba10_waita01" in s, ()),
        (lambda s: "defaultwait01_loop" in s, ()),
        (lambda s: "battle idle" in s, ()),
        (lambda s: "idle" in s or "wait" in s or "stand" in s, ("eye", "mouth", "turn")),
    ])

    walk = pick([
        (lambda s: "walk01_loop w/" in s or "in place" in s, ("turn",)),
        (lambda s: "00030_walk01_loop" in s, ("turn",)),
        (lambda s: "20030_walk01_loop" in s, ("turn",)),
        (lambda s: "walk01_loop" in s, ("turn",)),
        (lambda s: "00100_run01_loop" in s, ("turn",)),
        (lambda s: "20100_run01_loop" in s, ("turn",)),
        (lambda s: "run01_loop" in s, ("turn",)),
        (lambda s: "bd_walk" in s, ()),
        (lambda s: "bd_run" in s, ()),
        (lambda s: ("walk" in s or "awlk" in s or re.search(r"\brun\b", s) is not None), ("turn", "damage", "jump")),
    ])

    attack = pick([
        (lambda s: "00400_attack01" in s or "20400_attack01" in s, ()),
        (lambda s: "ba20_buturi01" in s, ()),
        (lambda s: s == "attack 1" or "attack01" in s, ()),
        (lambda s: "bd_attack" in s, ()),
        (lambda s: "attack" in s or "buturi" in s or "tokusyu" in s or "roar" in s, ("damage",)),
    ])

    death = pick([
        (lambda s: s == "down" or "00500_damage01" in s or "20500_damage01" in s, ()),
        (lambda s: "down" in s, ("jumpdown",)),
        (lambda s: "damage" in s or "ko" in s or "faint" in s, ("jumpdown",)),
    ])

    return {"Stand": stand, "Walk": walk, "Attack": attack, "Death": death}


def is_rigged_glb(meta: dict) -> bool:
    """True when the glTF has >=1 skin, >=1 animation, and at least one primitive with JOINTS_0."""
    if not meta.get("skins") or not meta.get("animations"):
        return False
    return any(
        "JOINTS_0" in pr.get("attributes", {}) and "WEIGHTS_0" in pr.get("attributes", {})
        for m in meta.get("meshes", [])
        for pr in m.get("primitives", [])
    )


def _ancestors(u: int, pmap: dict):
    cur = pmap.get(u)
    while cur is not None:
        yield cur
        cur = pmap.get(cur)


def build_skeleton(meta: dict, read_accessor, bin_data: bytes, jobs: list, world_bind: dict,
                   parent_map: dict, F_mat: np.ndarray, total_h: float):
    """Builds collapsed WC3 skeleton hierarchy, vertex skin groups, and keyframe tracks.

    `jobs` is the list of `node_jobs` from glb_to_mdx, where each job tuple carries:
    `(prim, pts, nrm, uv, raw_faces, skin_idx, mesh_node_idx, jidx, wts)`.
    """
    nodes = meta.get("nodes", [])
    skins = meta.get("skins", [])
    n_nodes = len(nodes)

    # 1. Measure vertex usage per glTF node index across all primitives
    node_weight_sum = np.zeros(n_nodes, dtype=np.float64)
    used_nodes = set()
    for node_jobs in jobs:
        for _prim, pts, _nrm, _uv, _faces, skin_idx, mnode, jidx, wts in node_jobs:
            if skin_idx is not None and jidx is not None and wts is not None and len(jidx) == len(pts):
                joints = skins[skin_idx].get("joints", [])
                if not joints:
                    continue
                ji = np.clip(jidx.astype(np.int64).reshape(len(pts), -1), 0, len(joints) - 1)
                wt = wts.astype(np.float64).reshape(len(pts), -1)
                wt = wt / np.maximum(wt.sum(axis=1, keepdims=True), 1e-9)
                for col in range(ji.shape[1]):
                    g_nodes = np.asarray(joints, dtype=np.int64)[ji[:, col]]
                    mask = wt[:, col] > 0.05
                    if np.any(mask):
                        np.add.at(node_weight_sum, g_nodes[mask], wt[mask, col])
                        used_nodes.update(int(x) for x in np.unique(g_nodes[mask]))
            elif mnode is not None:
                node_weight_sum[mnode] += float(len(pts))
                used_nodes.add(int(mnode))

    if not used_nodes:
        return None

    # Include structural ancestors of used nodes that belong to skins or armature
    skin_node_set = {int(j) for s in skins for j in s.get("joints", [])}
    skeleton_set = set(used_nodes)
    for u in list(used_nodes):
        cur = parent_map.get(u)
        while cur is not None:
            if cur in skin_node_set:
                skeleton_set.add(cur)
            cur = parent_map.get(cur)

    def _sk_parent(u):
        cur = parent_map.get(u)
        while cur is not None:
            if cur in skeleton_set:
                return cur
            cur = parent_map.get(cur)
        return None

    depth_cache = {}

    def _depth(u):
        if u not in depth_cache:
            p = _sk_parent(u)
            depth_cache[u] = 0 if p is None else _depth(p) + 1
        return depth_cache[u]

    def _keep_score(u):
        nm = (nodes[u].get("name") or "").lower()
        d = _depth(u)
        if any(dk in nm for dk in _DROP_KW):
            base = -1000.0
        elif any(kk in nm for kk in _KEEP_KW):
            base = 500.0
        else:
            base = 0.0
        return (base - d * 25.0 + min(200.0, node_weight_sum[u] * 0.2), -d, -u)

    roots = [u for u in sorted(skeleton_set) if _sk_parent(u) is None]
    kept = set(roots)
    for u in sorted(skeleton_set):
        nm_u = (nodes[u].get("name") or "").lower()
        if (
            len(kept) < MAX_BONES - 1
            and _depth(u) <= 2
            and not any(dk in nm_u for dk in _DROP_KW)
        ):
            kept.add(u)
    candidates = [u for u in sorted(skeleton_set) if u not in kept]
    candidates.sort(key=_keep_score, reverse=True)
    for u in candidates:
        if len(kept) >= MAX_BONES - 1:
            break
        kept.add(u)

    top_kept = [u for u in sorted(kept) if _sk_parent(u) is None or not any(
        p in kept for p in _ancestors(u, parent_map)
    )]

    # Build ordered kept bone list; add synthetic Root only if >1 disconnected kept roots exist
    ordered_nodes = []  # (wc3_idx, gltf_node_or_None, parent_wc3_idx, name)
    use_synth_root = len(top_kept) > 1 or len(kept) == 0
    node_to_bone = {}
    if use_synth_root:
        ordered_nodes.append((0, None, -1, "Root"))

    def _visit(u, p_wc3):
        bidx = len(ordered_nodes)
        nm = (nodes[u].get("name") or f"Bone_{u}").encode("latin-1", "replace").decode("latin-1")[:79]
        if not nm:
            nm = f"Bone_{u}"
        ordered_nodes.append((bidx, u, p_wc3, nm))
        node_to_bone[u] = bidx
        children = []
        for cand in sorted(kept):
            if cand == u:
                continue
            for anc in _ancestors(cand, parent_map):
                if anc in kept:
                    if anc == u:
                        children.append(cand)
                    break
        for c in children:
            _visit(c, bidx)

    for r in sorted(top_kept):
        _visit(r, 0 if use_synth_root else -1)

    full_node_to_bone = dict(node_to_bone)
    for u in range(n_nodes):
        if u in full_node_to_bone:
            continue
        mapped = 0
        for anc in _ancestors(u, parent_map):
            if anc in node_to_bone:
                mapped = node_to_bone[anc]
                break
        full_node_to_bone[u] = mapped

    # 2. Precompute WC3 world bind pivots PIVT for all bones 0..N-1
    n_bones = len(ordered_nodes)
    bone_pivots = []
    for _bidx, gnode, _p_wc3, _nm in ordered_nodes:
        if gnode is None:
            bone_pivots.append((0.0, 0.0, 0.0))
        else:
            p_g = np.append(world_bind[gnode][:3, 3], 1.0)
            p_w = (F_mat @ p_g)[:3]
            bone_pivots.append((float(p_w[0]), float(p_w[1]), float(p_w[2])))

    # 3. Assign per-vertex bone groups (GNDX, MTGC, MATS) for each primitive job
    geoset_skin_groups = []
    for node_jobs in jobs:
        for _prim, pts, _nrm, _uv, _faces, skin_idx, mnode, jidx, wts in node_jobs:
            vcount = len(pts)
            fallback_bone = full_node_to_bone.get(mnode, 0) if mnode is not None else 0
            if skin_idx is not None and jidx is not None and wts is not None and len(jidx) == vcount:
                joints = skins[skin_idx].get("joints", [])
                ji = np.clip(jidx.astype(np.int64).reshape(vcount, -1), 0, len(joints) - 1)
                wt = wts.astype(np.float64).reshape(vcount, -1)
                wt = wt / np.maximum(wt.sum(axis=1, keepdims=True), 1e-9)
                j2b = np.array([full_node_to_bone.get(int(g), fallback_bone) for g in joints], dtype=np.int32)
                b_mat = j2b[ji]

                primary = np.empty(vcount, dtype=np.int32)
                secondary = np.full(vcount, -1, dtype=np.int32)
                for vi in range(vcount):
                    acc = {}
                    for col in range(b_mat.shape[1]):
                        b = int(b_mat[vi, col])
                        acc[b] = acc.get(b, 0.0) + float(wt[vi, col])
                    ranked = sorted(acc.items(), key=lambda kv: kv[1], reverse=True)
                    primary[vi] = ranked[0][0]
                    if len(ranked) > 1 and ranked[1][1] >= 0.25 and ranked[1][0] != ranked[0][0]:
                        secondary[vi] = ranked[1][0]

                grp_map = {}
                grp_list = []
                gndx = bytearray(vcount)
                for vi in range(vcount):
                    b0 = int(primary[vi])
                    b1 = int(secondary[vi])
                    key = (min(b0, b1), max(b0, b1)) if b1 >= 0 else (b0,)
                    gid = grp_map.get(key)
                    if gid is None:
                        gid = len(grp_list)
                        grp_map[key] = gid
                        grp_list.append(key)
                    gndx[vi] = gid if gid < 255 else 0

                if len(grp_list) > MAX_GEOSET_GROUPS:
                    grp_map = {}
                    grp_list = []
                    for vi in range(vcount):
                        key = (int(primary[vi]),)
                        gid = grp_map.get(key)
                        if gid is None:
                            gid = len(grp_list)
                            grp_map[key] = gid
                            grp_list.append(key)
                        gndx[vi] = gid if gid < 255 else 0
            else:
                grp_list = [(fallback_bone,)]
                gndx = b"\x00" * vcount

            geoset_skin_groups.append((bytes(gndx), grp_list))

    # 4. Precompute bind TRS & pre-decode clip channels for fast evaluation
    bind_trs = [_decompose_node_trs(nd) for nd in nodes]
    clips = _pick_clips(meta.get("animations", []))
    F_inv = np.linalg.inv(F_mat)
    world_bind_inv = {u: np.linalg.inv(world_bind[u]) for u in skeleton_set}

    decoded_clips = {}
    clip_durations = {}
    for sname, clip in clips.items():
        if clip is None:
            continue
        dec = []
        tmax = 0.0
        for ch in clip.get("channels", []):
            tgt = ch.get("target", {})
            nidx = tgt.get("node")
            path = tgt.get("path")
            if nidx is None or path not in ("translation", "rotation", "scale"):
                continue
            sp = clip["samplers"][ch["sampler"]]
            times = read_accessor(meta, bin_data, sp["input"])
            vals = read_accessor(meta, bin_data, sp["output"])
            if times is None or vals is None or len(times) == 0:
                continue
            t_arr = np.asarray(times, dtype=np.float64)
            v_arr = np.asarray(vals, dtype=np.float64)
            tmax = max(tmax, float(np.max(t_arr)))
            dec.append((nidx, path, t_arr, v_arr, sp.get("interpolation", "LINEAR")))
        decoded_clips[sname] = dec
        clip_durations[sname] = tmax

    def _eval_decoded_at(dec_channels: list, t_sec: float):
        ch_trs = {}
        for nidx, path, t_arr, v_arr, interp in dec_channels:
            val = _sample_channel(t_arr, v_arr, interp, path, t_sec)
            if val is not None:
                ch_trs[(nidx, path)] = val

        world_anim = {}

        def get_wa(u):
            if u not in world_anim:
                btr, brot, bsc = bind_trs[u]
                tr = ch_trs.get((u, "translation"), btr)
                rot = ch_trs.get((u, "rotation"), brot)
                sc = ch_trs.get((u, "scale"), bsc)
                loc = _compose_trs(tr, rot, sc)
                world_anim[u] = get_wa(parent_map[u]) @ loc if u in parent_map else loc
            return world_anim[u]

        res = {}
        for bidx, u, p_wc3, _nm in ordered_nodes:
            if u is None:
                res[bidx] = (np.zeros(3), np.array([0.0, 0.0, 0.0, 1.0]), np.ones(3))
                continue
            W_j = get_wa(u)
            p_gnode = ordered_nodes[p_wc3][1] if p_wc3 >= 0 else None
            if p_gnode is None:
                H_p_inv = np.eye(4)
            else:
                W0_p = world_bind[p_gnode]
                W_p = get_wa(p_gnode)
                H_p_inv = F_mat @ W0_p @ np.linalg.inv(W_p) @ F_inv

            H_j = F_mat @ W_j @ world_bind_inv[u] @ F_inv
            D_j = H_p_inv @ H_j
            P0 = np.array(bone_pivots[bidx], dtype=np.float64)
            T_pos = np.eye(4)
            T_pos[:3, 3] = P0
            T_neg = np.eye(4)
            T_neg[:3, 3] = -P0
            E_j = T_neg @ D_j @ T_pos

            kgtr = E_j[:3, 3].copy()
            M3 = E_j[:3, :3]
            U, _, Vt = np.linalg.svd(M3)
            R = U @ Vt
            if np.linalg.det(R) < 0.0:
                U[:, -1] *= -1.0
                R = U @ Vt
            kgsc = np.diag(R.T @ M3).copy()
            kgrt = _mat3_to_quat(R)
            res[bidx] = (kgtr, kgrt, kgsc)
        return res

    # Base posture for fallback Walk synthesis: Stand(t=0) if available so models don't snap to T-pose
    base_stand_pose = None
    if decoded_clips.get("Stand") and clip_durations.get("Stand", 0.0) > 1e-4:
        base_stand_pose = _eval_decoded_at(decoded_clips["Stand"], 0.0)

    def _axis_q(ax, deg):
        rad = math.radians(deg) * 0.5
        sn, cs = math.sin(rad), math.cos(rad)
        return np.array([ax[0] * sn, ax[1] * sn, ax[2] * sn, cs])

    def _is_chain_subseg(lo_nm: str, prefix: str) -> bool:
        """True if name looks like a secondary segment (_02.._09, _b.._f) so angles don't stack 5x."""
        m = re.search(rf"{prefix}[_a-z]*_0([2-9])$", lo_nm)
        if m:
            return True
        return False

    # Find shallowest wing & tail bones so multi-segment chains don't over-rotate
    wing_bones = {bidx for bidx, _g, _p, nm in ordered_nodes if "wing" in nm.lower()}
    tail_bones = {bidx for bidx, _g, _p, nm in ordered_nodes if "tail" in nm.lower()}
    wing_heads = {b for b in wing_bones if ordered_nodes[b][2] not in wing_bones}
    tail_heads = {b for b in tail_bones if ordered_nodes[b][2] not in tail_bones}

    def _synth_walk_pose(phase: float) -> dict[int, tuple]:
        ang = 2.0 * math.pi * phase
        s = math.sin(ang)
        out = {}
        for bidx, _gnode, p_wc3, nm in ordered_nodes:
            lo_nm = nm.lower()
            is_left = any(w in lo_nm for w in ("left", "_l_", "_l", ".l")) or lo_nm.startswith("l_")
            is_right = any(w in lo_nm for w in ("right", "_r_", "_r", ".r")) or lo_nm.startswith("r_")
            side = 1.0 if is_left else (-1.0 if is_right else 0.0)
            b_tr, b_q, b_sc = base_stand_pose[bidx] if base_stand_pose else (np.zeros(3), np.array([0.0, 0.0, 0.0, 1.0]), np.ones(3))
            d_tr = np.zeros(3)
            d_q = np.array([0.0, 0.0, 0.0, 1.0])

            if p_wc3 == -1:
                d_tr = np.array([0.0, 0.0, max(1.5, total_h * 0.028) * (0.5 - 0.5 * math.cos(2.0 * ang))])
                d_q = _axis_q((0.0, 0.0, 1.0), 3.0 * s)
            elif "hips" in lo_nm or "waist" in lo_nm or "pelvis" in lo_nm:
                d_q = _axis_q((0.0, 0.0, 1.0), 3.5 * s)
            elif any(w in lo_nm for w in ("thigh", "upperleg", "leg_01")) and side != 0.0:
                d_q = _axis_q((0.0, 1.0, 0.0), 18.0 * side * s)
            elif any(w in lo_nm for w in ("calf", "lowerleg", "leg_02")) and side != 0.0:
                # Knee bends backward briefly on recovery swing
                bend = max(0.0, side * s) * 16.0
                d_q = _axis_q((0.0, 1.0, 0.0), bend)
            elif bidx in wing_heads and side != 0.0:
                d_q = _axis_q((1.0, 0.0, 0.0), 14.0 * side * s)
            elif bidx in wing_bones and side != 0.0:
                d_q = _axis_q((1.0, 0.0, 0.0), 5.0 * side * s)
            elif ("arm_01" in lo_nm or "upperarm" in lo_nm or ("shoulder" not in lo_nm and "arm" in lo_nm and not _is_chain_subseg(lo_nm, "arm"))) and side != 0.0:
                d_q = _axis_q((0.0, 1.0, 0.0), -12.0 * side * s)
            elif bidx in tail_heads:
                d_q = _axis_q((0.0, 0.0, 1.0), 10.0 * s)
            elif bidx in tail_bones:
                d_q = _axis_q((0.0, 0.0, 1.0), 4.0 * s)
            elif any(w in lo_nm for w in ("spine", "chest", "neck", "head")) and not _is_chain_subseg(lo_nm, "spine"):
                d_q = _axis_q((0.0, 0.0, 1.0), -2.5 * s)
            out[bidx] = (b_tr + d_tr, _quat_mul(b_q, d_q), b_sc)
        return out

    def _synth_stand_pose(phase: float) -> dict[int, tuple]:
        ang = 2.0 * math.pi * phase
        s = math.sin(ang)
        out = {}
        for bidx, _gnode, p_wc3, nm in ordered_nodes:
            lo_nm = nm.lower()
            is_left = any(w in lo_nm for w in ("left", "_l_", "_l", ".l")) or lo_nm.startswith("l_")
            is_right = any(w in lo_nm for w in ("right", "_r_", "_r", ".r")) or lo_nm.startswith("r_")
            side = 1.0 if is_left else (-1.0 if is_right else 0.0)
            tr = np.array([0.0, 0.0, max(0.8, total_h * 0.015) * (0.5 - 0.5 * math.cos(ang))]) if (p_wc3 == -1 or "spine" in lo_nm) else np.zeros(3)
            q = np.array([0.0, 0.0, 0.0, 1.0])
            if "wing" in lo_nm and side != 0.0:
                q = _axis_q((1.0, 0.0, 0.0), 10.0 * side * s)
            elif "tail" in lo_nm:
                q = _axis_q((0.0, 0.0, 1.0), 6.0 * s)
            out[bidx] = (tr, q, np.ones(3))
        return out

    def _synth_attack_pose(phase: float) -> dict[int, tuple]:
        out = {}
        lunge = math.sin(phase * math.pi)
        pitch = -10.0 * math.sin(phase * 2.0 * math.pi)
        for bidx, _gnode, p_wc3, nm in ordered_nodes:
            lo_nm = nm.lower()
            tr = np.array([max(4.0, total_h * 0.16) * lunge, 0.0, 0.0]) if p_wc3 == -1 else np.zeros(3)
            q = _axis_q((0.0, 1.0, 0.0), pitch) if (p_wc3 == -1 or "spine" in lo_nm) else np.array([0.0, 0.0, 0.0, 1.0])
            out[bidx] = (tr, q, np.ones(3))
        return out

    def _synth_death_pose(phase: float) -> dict[int, tuple]:
        out = {}
        p = min(1.0, phase * 1.15)
        q_fall = _axis_q((0.0, 1.0, 0.0), -84.0 * p)
        for bidx, _gnode, p_wc3, _nm in ordered_nodes:
            tr = np.array([-max(4.0, total_h * 0.1), 0.0, -max(6.0, total_h * 0.22) * p]) if p_wc3 == -1 else np.zeros(3)
            q = q_fall if p_wc3 == -1 else np.array([0.0, 0.0, 0.0, 1.0])
            out[bidx] = (tr, q, np.ones(3))
        return out

    # 5. Sample all 4 WC3 sequences across bones
    bone_tracks = {b: {"tr": [], "rt": [], "sc": []} for b in range(n_bones)}
    for sname, s_start, s_end, _ms, nonloop in SEQ_WINDOWS:
        n_samples = SAMPLE_COUNTS[sname]
        dec = decoded_clips.get(sname)
        clip_dur = clip_durations.get(sname, 0.0)
        seq_poses = []

        for si in range(n_samples):
            frac = si / float(n_samples - 1)
            tms = int(round(s_start + frac * (s_end - s_start)))
            if dec and clip_dur > 1e-4:
                pose = _eval_decoded_at(dec, frac * clip_dur)
            else:
                eff_frac = 0.0 if (nonloop == 0 and si == n_samples - 1) else frac
                if sname == "Walk":
                    pose = _synth_walk_pose(eff_frac)
                elif sname == "Attack":
                    pose = _synth_attack_pose(eff_frac)
                elif sname == "Death":
                    pose = _synth_death_pose(eff_frac)
                else:
                    pose = _synth_stand_pose(eff_frac)
            seq_poses.append((tms, pose))

        # Remove horizontal root locomotion drift in Walk (SV/Z-A walk01_loop moves forward +2..4m)
        if sname == "Walk" and dec and clip_dur > 1e-4:
            for bidx, _g, p_wc3, bname in ordered_nodes:
                lo_nm = bname.lower()
                is_root_loco = (
                    p_wc3 == -1
                    or (p_wc3 >= 0 and ordered_nodes[p_wc3][2] == -1)
                    or "origin" in lo_nm
                    or "root" in lo_nm
                    or lo_nm.startswith("pm")
                )
                if is_root_loco:
                    xs = [p[bidx][0][0] for _t, p in seq_poses]
                    ys = [p[bidx][0][1] for _t, p in seq_poses]
                    if max(xs) - min(xs) > 1.5 or max(ys) - min(ys) > 1.5:
                        x0, y0 = xs[0], ys[0]
                        for _t, p in seq_poses:
                            p[bidx][0][0] = x0
                            p[bidx][0][1] = y0

        # Ensure seamless looping on Stand/Walk so end keyframe matches start keyframe
        if nonloop == 0 and len(seq_poses) > 1:
            seq_poses[-1] = (seq_poses[-1][0], seq_poses[0][1])

        for tms, pose in seq_poses:
            for bidx in range(n_bones):
                tr, q, sc = pose[bidx]
                bone_tracks[bidx]["tr"].append((tms, (float(tr[0]), float(tr[1]), float(tr[2]))))
                bone_tracks[bidx]["rt"].append((tms, (float(q[0]), float(q[1]), float(q[2]), float(q[3]))))
                bone_tracks[bidx]["sc"].append((tms, (float(sc[0]), float(sc[1]), float(sc[2]))))

    # 6. Serialize BONE chunk with continuous quaternion hemisphere alignment
    bone_chunk_body = bytearray()
    for bidx, _gnode, p_wc3, bname in ordered_nodes:
        tr_keys = bone_tracks[bidx]["tr"]
        rt_keys = bone_tracks[bidx]["rt"]
        sc_keys = bone_tracks[bidx]["sc"]

        tracks = bytearray()
        if any(max(abs(v[0]), abs(v[1]), abs(v[2])) > 1e-3 for _, v in tr_keys):
            tracks += b"KGTR" + struct.pack("<IIi", len(tr_keys), 1, -1)
            for tms, v in tr_keys:
                tracks += struct.pack("<I3f", tms, v[0], v[1], v[2])

        if any(max(abs(q[0]), abs(q[1]), abs(q[2])) > 1e-4 or abs(q[3] - 1.0) > 1e-4 for _, q in rt_keys):
            tracks += b"KGRT" + struct.pack("<IIi", len(rt_keys), 1, -1)
            prev_q = None
            for tms, q in rt_keys:
                if prev_q is not None and sum(a * b for a, b in zip(prev_q, q)) < 0.0:
                    q = (-q[0], -q[1], -q[2], -q[3])
                prev_q = q
                tracks += struct.pack("<I4f", tms, q[0], q[1], q[2], q[3])

        if any(max(abs(s[0] - 1.0), abs(s[1] - 1.0), abs(s[2] - 1.0)) > 1e-3 for _, s in sc_keys):
            tracks += b"KGSC" + struct.pack("<IIi", len(sc_keys), 1, -1)
            for tms, s in sc_keys:
                tracks += struct.pack("<I3f", tms, s[0], s[1], s[2])

        nm_bytes = bname.encode("latin-1", "replace")[:80].ljust(80, b"\x00")
        parent_u32 = 0xFFFFFFFF if p_wc3 < 0 else int(p_wc3)
        node_base = nm_bytes + struct.pack("<III", bidx, parent_u32, 0x00000100)
        node_len = 4 + len(node_base) + len(tracks)
        bone_chunk_body += struct.pack("<I", node_len) + node_base + tracks + struct.pack("<ii", -1, -1)

    return {
        "n_bones": n_bones,
        "seqs": SEQ_WINDOWS,
        "geoset_skin_groups": geoset_skin_groups,
        "bone_chunk": b"BONE" + struct.pack("<I", len(bone_chunk_body)) + bytes(bone_chunk_body),
        "bone_pivots": bone_pivots,
    }



def build_procedural_skeleton(geoset_pts_wc3: list[np.ndarray], model_name: str, total_h: float):
    """Way-2 procedural multi-bone limb rigging & gait for unrigged static .glb meshes.

    Splits vertices cleanly into torso core + limbs (legs/arms/wings/head/tail) with smooth
    50/50 joint collars (MTGC=2) at hips/shoulders, keeping Bone 0 (Root) Attack lunge key
    at t=3000ms along +X for WC3 & test compatibility.
    """
    total_v = sum(len(p) for p in geoset_pts_wc3)
    if total_v < 40 or total_h <= 1e-3:
        return None

    all_v = np.concatenate(geoset_pts_wc3, axis=0)
    lo, hi = all_v.min(axis=0), all_v.max(axis=0)
    L = max(1e-3, float(hi[0] - lo[0]))
    W = max(1e-3, float(hi[1] - lo[1]))
    H = max(1e-3, float(hi[2] - lo[2]))
    cx = float((lo[0] + hi[0]) * 0.5)
    hw = W * 0.5
    nm = model_name.lower()

    is_blob = any(b in nm for b in (
        "voltorb", "electrode", "castform", "diglett", "dugtrio", "grimer", "muk",
        "cherrim", "corsola", "cursola", "shellos", "gastrodon", "chimecho",
        "weezing", "iron-treads", "201", "363", "433",
    ))
    is_winged = (not is_blob) and (
        any(w in nm for w in ("butterfree", "charizard", "beedrill", "roaring-moon",
                              "skarmory", "jugulis", "staraptor", "altaria", "rotom", "aegislash"))
        or W > 1.45 * H
    )
    has_front_feet = bool(np.any((all_v[:, 2] < 0.32 * H) & (all_v[:, 0] > cx + 0.12 * L)))
    has_back_feet = bool(np.any((all_v[:, 2] < 0.32 * H) & (all_v[:, 0] < cx - 0.12 * L)))
    is_quad = (not is_blob) and (not is_winged) and L > 1.05 * H and has_front_feet and has_back_feet

    # Define candidate child bones: (role, mask_all, collar_all, default_pivot)
    candidates = []

    if is_winged:
        ym = 0.17 * hw
        zm = 0.34 * H
        m_wl = (all_v[:, 2] > zm) & (all_v[:, 1] > ym)
        c_wl = (all_v[:, 2] > zm - 0.04 * H) & (all_v[:, 1] > ym * 0.65) & (~m_wl)
        m_wr = (all_v[:, 2] > zm) & (all_v[:, 1] < -ym)
        c_wr = (all_v[:, 2] > zm - 0.04 * H) & (all_v[:, 1] < -ym * 0.65) & (~m_wr)
        z_wing = float(all_v[m_wl | m_wr, 2].mean()) if np.any(m_wl | m_wr) else 0.60 * H
        candidates.append(("WingL", m_wl, c_wl, (cx, ym, z_wing)))
        candidates.append(("WingR", m_wr, c_wr, (cx, -ym, z_wing)))
        m_hd = (all_v[:, 2] > 0.64 * H) & (all_v[:, 0] > cx - 0.05 * L) & (np.abs(all_v[:, 1]) <= ym * 1.1)
        c_hd = (all_v[:, 2] > 0.58 * H) & (all_v[:, 0] > cx - 0.08 * L) & (np.abs(all_v[:, 1]) <= ym * 1.1) & (~m_hd)
        candidates.append(("Head", m_hd, c_hd, (cx + 0.08 * L, 0.0, 0.64 * H)))
        m_tl = (all_v[:, 0] < cx - 0.25 * L) & (all_v[:, 2] < 0.58 * H) & (np.abs(all_v[:, 1]) <= ym * 1.3)
        c_tl = (all_v[:, 0] < cx - 0.19 * L) & (all_v[:, 2] < 0.58 * H) & (np.abs(all_v[:, 1]) <= ym * 1.3) & (~m_tl)
        candidates.append(("Tail", m_tl, c_tl, (cx - 0.24 * L, 0.0, 0.36 * H)))
    elif is_quad:
        zhip = 0.38 * H
        ygap = 0.04 * hw
        xgap = 0.05 * L
        m_fl = (all_v[:, 2] < zhip) & (all_v[:, 0] > cx + xgap) & (all_v[:, 1] > ygap)
        c_fl = (all_v[:, 2] < zhip + 0.07 * H) & (all_v[:, 0] > cx + xgap) & (all_v[:, 1] > ygap) & (~m_fl)
        m_fr = (all_v[:, 2] < zhip) & (all_v[:, 0] > cx + xgap) & (all_v[:, 1] < -ygap)
        c_fr = (all_v[:, 2] < zhip + 0.07 * H) & (all_v[:, 0] > cx + xgap) & (all_v[:, 1] < -ygap) & (~m_fr)
        m_bl = (all_v[:, 2] < zhip) & (all_v[:, 0] < cx - xgap) & (all_v[:, 1] > ygap)
        c_bl = (all_v[:, 2] < zhip + 0.07 * H) & (all_v[:, 0] < cx - xgap) & (all_v[:, 1] > ygap) & (~m_bl)
        m_br = (all_v[:, 2] < zhip) & (all_v[:, 0] < cx - xgap) & (all_v[:, 1] < -ygap)
        c_br = (all_v[:, 2] < zhip + 0.07 * H) & (all_v[:, 0] < cx - xgap) & (all_v[:, 1] < -ygap) & (~m_br)
        candidates.extend([
            ("LegFL", m_fl, c_fl, None), ("LegFR", m_fr, c_fr, None),
            ("LegBL", m_bl, c_bl, None), ("LegBR", m_br, c_br, None),
        ])
        m_hd = (all_v[:, 2] > 0.54 * H) & (all_v[:, 0] > cx + 0.14 * L)
        c_hd = (all_v[:, 2] > 0.48 * H) & (all_v[:, 0] > cx + 0.08 * L) & (~m_hd)
        candidates.append(("Head", m_hd, c_hd, (cx + 0.16 * L, 0.0, 0.56 * H)))
        m_tl = (all_v[:, 2] > 0.28 * H) & (all_v[:, 0] < cx - 0.30 * L)
        c_tl = (all_v[:, 2] > 0.24 * H) & (all_v[:, 0] < cx - 0.24 * L) & (~m_tl)
        candidates.append(("Tail", m_tl, c_tl, (cx - 0.28 * L, 0.0, 0.48 * H)))
    elif not is_blob:
        # Biped / Upright
        zhip = 0.36 * H
        ygap = 0.035 * hw
        m_ll = (all_v[:, 2] < zhip) & (all_v[:, 1] > ygap)
        c_ll = (all_v[:, 2] < zhip + 0.06 * H) & (all_v[:, 1] > ygap) & (~m_ll)
        m_lr = (all_v[:, 2] < zhip) & (all_v[:, 1] < -ygap)
        c_lr = (all_v[:, 2] < zhip + 0.06 * H) & (all_v[:, 1] < -ygap) & (~m_lr)
        yarm = 0.25 * hw
        m_al = (all_v[:, 2] >= 0.38 * H) & (all_v[:, 2] <= 0.80 * H) & (all_v[:, 1] > yarm)
        c_al = (all_v[:, 2] >= 0.36 * H) & (all_v[:, 2] <= 0.82 * H) & (all_v[:, 1] > yarm * 0.72) & (~m_al)
        m_ar = (all_v[:, 2] >= 0.38 * H) & (all_v[:, 2] <= 0.80 * H) & (all_v[:, 1] < -yarm)
        c_ar = (all_v[:, 2] >= 0.36 * H) & (all_v[:, 2] <= 0.82 * H) & (all_v[:, 1] < -yarm * 0.72) & (~m_ar)
        m_hd = (all_v[:, 2] > 0.68 * H) & (np.abs(all_v[:, 1]) <= yarm * 1.05)
        c_hd = (all_v[:, 2] > 0.62 * H) & (np.abs(all_v[:, 1]) <= yarm * 1.05) & (~m_hd)
        m_tl = (all_v[:, 2] < 0.56 * H) & (all_v[:, 0] < cx - 0.28 * L) & (np.abs(all_v[:, 1]) <= yarm)
        c_tl = (all_v[:, 2] < 0.58 * H) & (all_v[:, 0] < cx - 0.22 * L) & (np.abs(all_v[:, 1]) <= yarm) & (~m_tl)
        candidates.extend([
            ("LegL", m_ll, c_ll, None), ("LegR", m_lr, c_lr, None),
            ("ArmL", m_al, c_al, None), ("ArmR", m_ar, c_ar, None),
            ("Head", m_hd, c_hd, (cx, 0.0, 0.68 * H)),
            ("Tail", m_tl, c_tl, (cx - 0.25 * L, 0.0, 0.34 * H)),
        ])
    else:
        # Blob / Floating / Crawler
        m_up = (all_v[:, 2] > 0.58 * H) & (np.abs(all_v[:, 1]) <= 0.35 * hw)
        c_up = (all_v[:, 2] > 0.50 * H) & (np.abs(all_v[:, 1]) <= 0.35 * hw) & (~m_up)
        m_sl = (all_v[:, 2] >= 0.30 * H) & (all_v[:, 1] > 0.28 * hw)
        c_sl = (all_v[:, 2] >= 0.26 * H) & (all_v[:, 1] > 0.20 * hw) & (~m_sl)
        m_sr = (all_v[:, 2] >= 0.30 * H) & (all_v[:, 1] < -0.28 * hw)
        c_sr = (all_v[:, 2] >= 0.26 * H) & (all_v[:, 1] < -0.20 * hw) & (~m_sr)
        candidates.extend([
            ("Head", m_up, c_up, (cx, 0.0, 0.58 * H)),
            ("ArmL", m_sl, c_sl, None),
            ("ArmR", m_sr, c_sr, None),
        ])

    # Keep only meaningful regions (>= 14 vertices) and resolve exclusive ownership
    bone_names = ["Root"]
    bone_pivots = [(cx, 0.0, 0.42 * H)]
    vert_primary = np.zeros(total_v, dtype=np.int32)
    vert_collar = np.zeros(total_v, dtype=np.int32)

    assigned = np.zeros(total_v, dtype=bool)
    for role, mask, collar, piv in candidates:
        own = mask & (~assigned)
        if int(np.sum(own)) < 14:
            continue
        bidx = len(bone_names)
        bone_names.append(role)
        assigned |= own
        vert_primary[own] = bidx
        col_own = collar & (~assigned)
        vert_collar[col_own] = bidx
        if piv is None:
            pts_r = all_v[own]
            if role.startswith("Leg"):
                px = float(pts_r[:, 0].mean())
                py = float(pts_r[:, 1].mean())
                pz = float(pts_r[:, 2].max())
                piv = (px, py, pz)
            elif role in ("ArmL", "WingL"):
                px = float(pts_r[:, 0].mean())
                py = float(pts_r[:, 1].min())
                pz = float(pts_r[:, 2].mean())
                piv = (px, py, pz)
            elif role in ("ArmR", "WingR"):
                px = float(pts_r[:, 0].mean())
                py = float(pts_r[:, 1].max())
                pz = float(pts_r[:, 2].mean())
                piv = (px, py, pz)
            else:
                piv = (float(pts_r[:, 0].mean()), float(pts_r[:, 1].mean()), float(pts_r[:, 2].mean()))
        bone_pivots.append(piv)

    # Split per geoset into GNDX, MTGC, MATS
    geoset_skin_groups = []
    offset = 0
    for pts in geoset_pts_wc3:
        vc = len(pts)
        vp = vert_primary[offset:offset + vc]
        vcol = vert_collar[offset:offset + vc]
        offset += vc
        grp_map = {}
        grp_list = []
        gndx = bytearray(vc)
        for vi in range(vc):
            b0 = int(vp[vi])
            bc = int(vcol[vi])
            key = (0, bc) if (b0 == 0 and bc > 0) else (b0,)
            gid = grp_map.get(key)
            if gid is None:
                gid = len(grp_list)
                grp_map[key] = gid
                grp_list.append(key)
            gndx[vi] = gid if gid < 255 else 0
        geoset_skin_groups.append((bytes(gndx), grp_list))

    # Build clean procedural tracks with EXACT Attack time 3000 lunge on Root!
    seqs = [
        ("Stand", 0, 1000, 0.0, 0),
        ("Walk", 1333, 2333, 250.0, 0),
        ("Attack", 2667, 3667, 0.0, 1),
        ("Death", 4000, 5000, 0.0, 1),
    ]

    def _ax_q(ax, deg):
        rad = math.radians(deg) * 0.5
        sn, cs = math.sin(rad), math.cos(rad)
        return (ax[0] * sn, ax[1] * sn, ax[2] * sn, cs)

    bone_chunk_body = bytearray()
    for bidx, role in enumerate(bone_names):
        tr_keys = []
        rt_keys = []
        sc_keys = []
        if bidx == 0:
            tr_keys = [
                (0, (0.0, 0.0, 0.0)),
                (500, (0.0, 0.0, max(1.2, total_h * 0.022))),
                (1000, (0.0, 0.0, 0.0)),
                (1333, (0.0, 0.0, 0.0)),
                (1583, (0.0, 0.0, max(2.2, total_h * 0.036))),
                (1833, (0.0, 0.0, 0.0)),
                (2083, (0.0, 0.0, max(2.2, total_h * 0.036))),
                (2333, (0.0, 0.0, 0.0)),
                (2667, (0.0, 0.0, 0.0)),
                (2820, (-max(2.0, total_h * 0.06), 0.0, 0.0)),
                (3000, (max(5.0, total_h * 0.22), 0.0, max(2.0, total_h * 0.06))),
                (3667, (0.0, 0.0, 0.0)),
                (4000, (0.0, 0.0, 0.0)),
                (5000, (-max(5.0, total_h * 0.12), 0.0, -max(8.0, total_h * 0.28))),
            ]
            # Subtle Root motion (NO excessive 10-deg nose-dive!): Stand breath, Walk +/-2.5 deg twist & 3 deg lean
            rt_keys = [
                (0, _ax_q((0.0, 1.0, 0.0), 0.0)),
                (500, _ax_q((0.0, 1.0, 0.0), -1.8)),
                (1000, _ax_q((0.0, 1.0, 0.0), 0.0)),
                (1333, _ax_q((0.0, 1.0, 0.0), 3.0)),
                (1583, _ax_q((0.0, 0.0, 1.0), 3.0)),
                (1833, _ax_q((0.0, 1.0, 0.0), 3.0)),
                (2083, _ax_q((0.0, 0.0, 1.0), -3.0)),
                (2333, _ax_q((0.0, 1.0, 0.0), 3.0)),
                (2667, _ax_q((0.0, 1.0, 0.0), 0.0)),
                (2820, _ax_q((0.0, 1.0, 0.0), -9.0)),
                (3000, _ax_q((0.0, 1.0, 0.0), 14.0)),
                (3667, _ax_q((0.0, 1.0, 0.0), 0.0)),
                (4000, _ax_q((0.0, 1.0, 0.0), 0.0)),
                (4850, _ax_q((0.0, 1.0, 0.0), -82.0)),
                (5000, _ax_q((0.0, 1.0, 0.0), -85.0)),
            ]
            sc_keys = [
                (0, (1.0, 1.0, 1.0)),
                (500, (1.015, 1.015, 1.024)),
                (1000, (1.0, 1.0, 1.0)),
                (1333, (1.0, 1.0, 1.0)),
                (2333, (1.0, 1.0, 1.0)),
                (2667, (1.0, 1.0, 1.0)),
                (2820, (1.04, 1.04, 0.95)),
                (3000, (1.05, 0.98, 1.04)),
                (3667, (1.0, 1.0, 1.0)),
            ]
        elif role in ("LegL", "LegR", "LegFL", "LegFR", "LegBL", "LegBR"):
            sign = 1.0 if role in ("LegL", "LegFL", "LegBR") else -1.0
            deg = 20.0 * sign
            rt_keys = [
                (0, (0.0, 0.0, 0.0, 1.0)),
                (1000, (0.0, 0.0, 0.0, 1.0)),
                (1333, (0.0, 0.0, 0.0, 1.0)),
                (1583, _ax_q((0.0, 1.0, 0.0), deg)),
                (1833, (0.0, 0.0, 0.0, 1.0)),
                (2083, _ax_q((0.0, 1.0, 0.0), -deg)),
                (2333, (0.0, 0.0, 0.0, 1.0)),
                (2667, (0.0, 0.0, 0.0, 1.0)),
                (3667, (0.0, 0.0, 0.0, 1.0)),
            ]
        elif role in ("ArmL", "ArmR"):
            # Arms counter-swing opposite matching leg (ArmL swings with LegR)
            sign = -1.0 if role == "ArmL" else 1.0
            deg = 16.0 * sign
            rt_keys = [
                (0, (0.0, 0.0, 0.0, 1.0)),
                (500, _ax_q((1.0, 0.0, 0.0), 4.0 if role == "ArmL" else -4.0)),
                (1000, (0.0, 0.0, 0.0, 1.0)),
                (1333, (0.0, 0.0, 0.0, 1.0)),
                (1583, _ax_q((0.0, 1.0, 0.0), deg)),
                (1833, (0.0, 0.0, 0.0, 1.0)),
                (2083, _ax_q((0.0, 1.0, 0.0), -deg)),
                (2333, (0.0, 0.0, 0.0, 1.0)),
                (2667, (0.0, 0.0, 0.0, 1.0)),
                (2820, _ax_q((0.0, 1.0, 0.0), -22.0)),
                (3000, _ax_q((0.0, 1.0, 0.0), 26.0)),
                (3667, (0.0, 0.0, 0.0, 1.0)),
            ]
        elif role in ("WingL", "WingR"):
            sign = 1.0 if role == "WingL" else -1.0
            rt_keys = [
                (0, (0.0, 0.0, 0.0, 1.0)),
                (250, _ax_q((1.0, 0.0, 0.0), 14.0 * sign)),
                (500, (0.0, 0.0, 0.0, 1.0)),
                (750, _ax_q((1.0, 0.0, 0.0), -12.0 * sign)),
                (1000, (0.0, 0.0, 0.0, 1.0)),
                (1333, (0.0, 0.0, 0.0, 1.0)),
                (1583, _ax_q((1.0, 0.0, 0.0), 24.0 * sign)),
                (1833, (0.0, 0.0, 0.0, 1.0)),
                (2083, _ax_q((1.0, 0.0, 0.0), -20.0 * sign)),
                (2333, (0.0, 0.0, 0.0, 1.0)),
                (2667, (0.0, 0.0, 0.0, 1.0)),
                (3000, _ax_q((1.0, 0.0, 0.0), 24.0 * sign)),
                (3667, (0.0, 0.0, 0.0, 1.0)),
            ]
        elif role == "Head":
            rt_keys = [
                (0, (0.0, 0.0, 0.0, 1.0)),
                (500, _ax_q((0.0, 1.0, 0.0), 3.0)),
                (1000, (0.0, 0.0, 0.0, 1.0)),
                (1333, (0.0, 0.0, 0.0, 1.0)),
                (1583, _ax_q((0.0, 0.0, 1.0), -3.5)),
                (1833, _ax_q((0.0, 1.0, 0.0), -2.5)),
                (2083, _ax_q((0.0, 0.0, 1.0), 3.5)),
                (2333, (0.0, 0.0, 0.0, 1.0)),
                (2667, (0.0, 0.0, 0.0, 1.0)),
                (3000, _ax_q((0.0, 1.0, 0.0), 10.0)),
                (3667, (0.0, 0.0, 0.0, 1.0)),
            ]
        elif role == "Tail":
            rt_keys = [
                (0, (0.0, 0.0, 0.0, 1.0)),
                (500, _ax_q((0.0, 0.0, 1.0), 6.0)),
                (1000, (0.0, 0.0, 0.0, 1.0)),
                (1333, (0.0, 0.0, 0.0, 1.0)),
                (1583, _ax_q((0.0, 0.0, 1.0), 13.0)),
                (1833, (0.0, 0.0, 0.0, 1.0)),
                (2083, _ax_q((0.0, 0.0, 1.0), -13.0)),
                (2333, (0.0, 0.0, 0.0, 1.0)),
                (2667, (0.0, 0.0, 0.0, 1.0)),
                (3667, (0.0, 0.0, 0.0, 1.0)),
            ]

        tracks = bytearray()
        if tr_keys:
            tracks += b"KGTR" + struct.pack("<IIi", len(tr_keys), 1, -1)
            for tms, v in tr_keys:
                tracks += struct.pack("<I3f", tms, v[0], v[1], v[2])
        if rt_keys:
            tracks += b"KGRT" + struct.pack("<IIi", len(rt_keys), 1, -1)
            prev_q = None
            for tms, q in rt_keys:
                if prev_q is not None and sum(a * b for a, b in zip(prev_q, q)) < 0.0:
                    q = (-q[0], -q[1], -q[2], -q[3])
                prev_q = q
                tracks += struct.pack("<I4f", tms, q[0], q[1], q[2], q[3])
        if sc_keys:
            tracks += b"KGSC" + struct.pack("<IIi", len(sc_keys), 1, -1)
            for tms, s in sc_keys:
                tracks += struct.pack("<I3f", tms, s[0], s[1], s[2])

        nm_bytes = role.encode("latin-1", "replace")[:80].ljust(80, b"\x00")
        parent_u32 = 0xFFFFFFFF if bidx == 0 else 0
        node_base = nm_bytes + struct.pack("<III", bidx, parent_u32, 0x00000100)
        node_len = 4 + len(node_base) + len(tracks)
        bone_chunk_body += struct.pack("<I", node_len) + node_base + tracks + struct.pack("<ii", -1, -1)

    return {
        "n_bones": len(bone_names),
        "seqs": seqs,
        "geoset_skin_groups": geoset_skin_groups,
        "bone_chunk": b"BONE" + struct.pack("<I", len(bone_chunk_body)) + bytes(bone_chunk_body),
        "bone_pivots": bone_pivots,
    }
