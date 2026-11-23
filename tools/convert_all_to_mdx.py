"""Batch converts all downloaded .glb Pokemon models into Warcraft III Reforged .mdx + .blp files."""
import concurrent.futures
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "v412"))
sys.path.insert(0, HERE)
sys.path.insert(0, WORK)

import glb_to_mdx

GLB_DIR = os.path.join(os.path.dirname(WORK), "imports", "pokemon_3d_all")
OUT_DIR = os.path.join(WORK, "imports", "pokemon_3d_mdx")
TEX_DIR = os.path.join(OUT_DIR, "textures")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)

def convert_single(glb_name: str):
    stem = os.path.splitext(glb_name)[0]
    in_path = os.path.join(GLB_DIR, glb_name)
    out_mdx = os.path.join(OUT_DIR, f"{stem}.mdx")

    if os.path.isfile(out_mdx) and os.path.getsize(out_mdx) > 0:
        return stem, True, "cached"

    with open(in_path, "rb") as fp:
        raw_glb = fp.read()

    tex_prefix = f"PkFx\\G14\\t\\{stem}"
    mdx_bytes, blp_dict = glb_to_mdx.convert_glb_to_mdx(
        raw_glb,
        model_name=f"Pk_{stem}",
        tex_path_prefix=tex_prefix,
        scale_multiplier=100.0,
    )

    with open(out_mdx, "wb") as fp:
        fp.write(mdx_bytes)

    for rel_tex, blp_bytes in blp_dict.items():
        base_tex = os.path.basename(rel_tex)
        out_blp = os.path.join(TEX_DIR, base_tex)
        with open(out_blp, "wb") as fp:
            fp.write(blp_bytes)

    return stem, False, f"{len(mdx_bytes)} bytes, {len(blp_dict)} textures"

def main():
    glb_files = [f for f in os.listdir(GLB_DIR) if f.endswith(".glb")]
    print(f"[batch_convert] Starting conversion of {len(glb_files)} GLB files...")
    start_time = time.time()

    success = 0
    failed = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(convert_single, f): f for f in glb_files}
        for idx, f in enumerate(concurrent.futures.as_completed(futures), 1):
            glb_name = futures[f]
            try:
                stem, cached, msg = f.result()
                success += 1
                if idx % 100 == 0 or idx == len(glb_files):
                    elapsed = time.time() - start_time
                    print(f"[batch_convert] Progress: {idx}/{len(glb_files)} ({idx*100//len(glb_files)}%) in {elapsed:.1f}s")
            except Exception as e:
                failed.append((glb_name, str(e)))

    total_time = time.time() - start_time
    print(f"[batch_convert] Complete! Converted {success}/{len(glb_files)} in {total_time:.1f}s. Failed: {len(failed)}")
    if failed:
        print(f"[batch_convert] Sample failures: {failed[:5]}")

if __name__ == "__main__":
    main()
