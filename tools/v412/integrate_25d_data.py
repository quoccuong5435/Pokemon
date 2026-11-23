"""Integrate 39 2.5D Pokemon into gen14_pokedex.json, gen14_models.json, and g14_icons_cache.
"""
import json
import os
import sys
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, HERE)

import map_optimizer

POKEDEX_JSON = os.path.join(HERE, "gen14_pokedex.json")
MODELS_JSON = os.path.join(HERE, "gen14_models.json")
ICON_CACHE = os.path.join(HERE, "g14_icons_cache")
SPRITES_DIR = os.path.join(WORK, "analysis", "home_sprites")
FETCHED_JSON = os.path.join(HERE, "fetched_missing_38.json")

os.makedirs(ICON_CACHE, exist_ok=True)

EVO_MAP = {
    268: [[269, 10]],       # Cascoon -> Dustox
    273: [[274, 14]],       # Seedot -> Nuzleaf
    274: [[275, 36]],       # Nuzleaf -> Shiftry (Leaf Stone / Lv36)
    276: [[277, 22]],       # Taillow -> Swellow
    278: [[279, 25]],       # Wingull -> Pelipper
    300: [[301, 30]],       # Skitty -> Delcatty (Moon Stone / Lv30)
    316: [[317, 26]],       # Gulpin -> Swalot
    325: [[326, 32]],       # Spoink -> Grumpig
    339: [[340, 30]],       # Barboach -> Whiscash
    353: [[354, 37]],       # Shuppet -> Banette
    401: [[402, 10]],       # Kricketot -> Kricketune
    412: [[413, 20]],       # Burmy -> Wormadam
    418: [[419, 26]],       # Buizel -> Floatzel
    420: [[421, 25]],       # Cherubi -> Cherrim
    422: [[423, 30]],       # Shellos -> Gastrodon
    431: [[432, 38]],       # Glameow -> Purugly
    434: [[435, 34]],       # Stunky -> Skuntank
}

ALL_39 = [
    268, 273, 274, 275, 276, 277, 278, 279, 300, 301,
    316, 317, 325, 326, 339, 340, 351, 352, 353, 354,
    370, 401, 402, 412, 413, 414, 418, 419, 420, 421,
    422, 423, 431, 432, 434, 435, 441, 455, 430
]

def update_pokedex():
    with open(POKEDEX_JSON, "r", encoding="utf-8") as f:
        pokedex = json.load(f)

    with open(FETCHED_JSON, "r", encoding="utf-8") as f:
        fetched = json.load(f)

    existing_dexes = {e["dex"] for e in pokedex}

    # Update Wurmple #265 to evolve into Cascoon #268 as well
    for e in pokedex:
        if e["dex"] == 265:
            evos = e.get("evo_to", [])
            has_268 = any(ev[0] == 268 for ev in evos)
            if not has_268:
                evos.append([268, 7])
                e["evo_to"] = evos

    for entry in fetched:
        d = entry["dex"]
        if d in existing_dexes:
            continue
        if d in EVO_MAP:
            entry["evo_to"] = EVO_MAP[d]
        pokedex.append(entry)

    pokedex.sort(key=lambda x: x["dex"])

    with open(POKEDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(pokedex, f, indent=2)
    print(f"Updated {POKEDEX_JSON}: now has {len(pokedex)} species!")

def update_models():
    with open(MODELS_JSON, "r", encoding="utf-8") as f:
        models = json.load(f)

    with open(POKEDEX_JSON, "r", encoding="utf-8") as f:
        pokedex = {e["dex"]: e for e in json.load(f)}

    for d in ALL_39:
        ds = str(d)
        sp = pokedex.get(d, {})
        stage = sp.get("stage", 0)
        bh = 55.0 if stage == 0 else (75.0 if stage == 1 else 95.0)
        models[ds] = {
            "src": "2.5D",
            "ref": os.path.join("analysis", "home_sprites", f"{d}.png"),
            "bh": bh,
            "btn": None
        }

    with open(MODELS_JSON, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2)
    print(f"Updated {MODELS_JSON}: now has {len(models)} models!")

def generate_icons():
    print(f"Generating BTN & DISBTN icons for {len(ALL_39)} Pokemon into {ICON_CACHE}...")
    for d in ALL_39:
        png_path = os.path.join(SPRITES_DIR, f"{d}.png")
        if not os.path.isfile(png_path):
            print(f"Warning: missing sprite {png_path}")
            continue

        im = Image.open(png_path).convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            cropped = im.crop(bbox)
        else:
            cropped = im

        w, h = cropped.size
        dim = max(w, h)
        # Pad with 5% margin to look great inside button frame
        pad = int(dim * 0.08)
        dim_padded = dim + pad * 2
        sq = Image.new("RGBA", (dim_padded, dim_padded), (0, 0, 0, 0))
        sq.paste(cropped, (pad + (dim - w) // 2, pad + (dim - h) // 2))

        # BTN: 64x64
        btn_im = sq.resize((64, 64), Image.LANCZOS)
        btn_arr = np.array(btn_im, dtype=np.uint8)
        btn_bytes = map_optimizer.encode_blp1_jpeg(btn_arr, abits=8, quality=85, max_dim=64)
        btn_path = os.path.join(ICON_CACHE, f"BTN_{d:03d}.blp")
        with open(btn_path, "wb") as f:
            f.write(btn_bytes)

        # DISBTN: 64x64 darkened grayscale
        gray_arr = np.array(btn_im, dtype=np.float32)
        lum = 0.299 * gray_arr[..., 0] + 0.587 * gray_arr[..., 1] + 0.114 * gray_arr[..., 2]
        gray_arr[..., 0] = lum * 0.45
        gray_arr[..., 1] = lum * 0.45
        gray_arr[..., 2] = lum * 0.45
        dis_im = Image.fromarray(gray_arr.astype(np.uint8), mode="RGBA")
        dis_bytes = map_optimizer.encode_blp1_jpeg(np.array(dis_im, dtype=np.uint8), abits=8, quality=85, max_dim=64)
        dis_path = os.path.join(ICON_CACHE, f"DISBTN_{d:03d}.blp")
        with open(dis_path, "wb") as f:
            f.write(dis_bytes)

    print(f"Successfully generated all icons for {len(ALL_39)} Pokemon!")

def main():
    update_pokedex()
    update_models()
    generate_icons()
    print("All 2.5D Pokemon data & icons integrated successfully!")

if __name__ == "__main__":
    main()
