"""Soul icons: the pokemondb HOME sprite of each Soul's species on a dark, glowing tile (like the patch-note page).
Output: analysis/soul_icons/BTNSoul<ITEM>.blp (+ DISBTNSoul<ITEM>.blp). Sprites cached in analysis/soul_sprites.
Usage (from _PokemonArena2.0_work):  python -I analysis/make_soul_icons.py"""
import os, subprocess, sys
sys.path.insert(0, 'tools')
from PIL import Image, ImageDraw, ImageFilter, ImageOps  # noqa: E402
import make_type_icons as mti  # noqa: E402
import mpq, objdata, wild_data  # noqa: E402

def slug(n):
    s = n.lower().replace("'", '').replace('.', '').replace(' ', '-')
    for pre, suf in (('alolan-', '-alolan'), ('galarian-', '-galarian'), ('hisuian-', '-hisui'), ('paldean-', '-paldean')):
        if s.startswith(pre): s = s[len(pre):] + suf
    return s

w3u = objdata.ObjFile(mpq.MPQ('../Pokemon Arena v1.8.w3x').read('war3map.w3u'))
S = mti.SIZE
miss = []
for w in wild_data.wild_souls(w3u):
    if not w.new:
        continue
    f = os.path.join('analysis', 'soul_sprites', slug(w.name) + '.png')
    if not os.path.exists(f):
        subprocess.run(['curl', '-sfL', '-o', f, 'https://img.pokemondb.net/sprites/home/normal/%s.png' % slug(w.name)])
    try:
        spr = Image.open(f).convert('RGBA')
    except Exception:  # noqa: BLE001
        if os.path.exists(f): os.remove(f)
        miss.append(w.name); continue
    bb = spr.getbbox()
    if bb: spr = spr.crop(bb)
    spr.thumbnail((S - 12, S - 12), Image.LANCZOS)
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1, 1, S - 2, S - 2], radius=10, fill=(24, 18, 44, 255), outline=(150, 90, 230, 255), width=3)
    glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([8, 8, S - 8, S - 8], fill=(150, 90, 230, 150))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(spr, ((S - spr.width) // 2, (S - spr.height) // 2))
    mti.write_blp1(img, 'analysis/soul_icons/BTNSoul%s.blp' % w.item)
    g = ImageOps.grayscale(img.convert('RGB')).convert('RGBA'); g.putalpha(img.getchannel('A'))
    mti.write_blp1(g, 'analysis/soul_icons/DISBTNSoul%s.blp' % w.item)
print('made', len(os.listdir('analysis/soul_icons')) // 2, 'missing', miss)
