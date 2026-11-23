"""ver2n_dota2_vfx.py:
Loads all 92 MDX models and 259 BLP textures from Massive Dota 2 Special Effects Rip.zip
into a dict of {mpq_path: bytes} ready for packaging into war3map.
"""
import os
import re
import zipfile

ZIP_PATH = r"C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\Massive Dota 2 Special Effects Rip.zip"


def load_dota2_vfx_assets() -> dict:
    assets = {}
    if not os.path.exists(ZIP_PATH):
        print(f"Warning: {ZIP_PATH} not found.")
        return assets

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        # 1. Parse readme.html for custom texture mappings
        html = ""
        try:
            html = z.read("Massive Dota 2 Special Effects Rip/readme.html").decode('utf-8', errors='ignore')
        except Exception:
            pass

        mappings = {}
        for m in re.finditer(r'<li>\s*([\w\.\-]+)\s*=>\s*([^<]+)</li>', html):
            src_file = m.group(1).strip().lower()
            dst_path = m.group(2).strip().replace('/', '\\')
            mappings[src_file] = dst_path

        # 2. Extract MDX and BLP
        for name in z.namelist():
            lower = name.lower()
            if not (lower.endswith('.mdx') or lower.endswith('.blp')):
                continue

            data = z.read(name)
            parts = name.split('/')
            fname = parts[-1]
            fname_lower = fname.lower()
            folder = parts[-2] if len(parts) >= 2 else ""

            if lower.endswith('.mdx'):
                # Store MDX under Dota2Fx\ and war3mapImported\
                assets[f"Dota2Fx\\{fname}"] = data
                if folder and folder != "Massive Dota 2 Special Effects Rip":
                    assets[f"Dota2Fx\\{folder}\\{fname}"] = data
                assets[f"war3mapImported\\{fname}"] = data
            elif lower.endswith('.blp'):
                # 1) If in readme mappings, store at exact path
                if fname_lower in mappings:
                    assets[mappings[fname_lower]] = data
                # 2) Also store relative and folder path
                assets[f"Dota2Fx\\{fname}"] = data
                if folder and folder != "Massive Dota 2 Special Effects Rip":
                    assets[f"Dota2Fx\\{folder}\\{fname}"] = data
                assets[f"war3mapImported\\{fname}"] = data

    print(f"Loaded {len(assets)} Dota 2 VFX assets ready for MPQ packaging.")
    return assets
