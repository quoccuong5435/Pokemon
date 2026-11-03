"""Type icons from the Vietnamese Pokemon wiki (https://pokemon.fandom.com/vi/wiki/Hệ): download the 18 PNG icons into
analysis/type_icons_fandom/ (a folder of its own: downloaded files are untrusted data) and make the BLP icons the map
imports (analysis/type_icons/BTNPkmn<Type>.blp and DISBTNPkmn<Type>.blp). The old placeholder icons are copied to
analysis/type_icons_placeholder/ first.

Usage (from _PokemonArena2.0_work):  python -I analysis/make_type_icons_fandom.py"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, 'tools')
sys.path.insert(0, 'analysis')
from PIL import Image, ImageOps  # noqa: E402

import make_type_icons as mti  # noqa: E402

BASE = 'https://static.wikia.nocookie.net/pokemon/images/%s/%s.png/revision/latest?cb=%s&path-prefix=vi'
# type -> (BTN stem, wiki file name, path, cache-buster) as listed on the page
ICONS = {
    'Normal': ('BTNPkmnNormal', 'Thuong', '7/76', '20210111110129'),
    'Fire': ('BTNPkmnFire', 'Lua', '9/91', '20210111110129'),
    'Water': ('BTNPkmnWater', 'Nuoc', 'e/e2', '20210111110129'),
    'Grass': ('BTNPkmnGrass', 'Co', 'e/e9', '20210111105224'),
    'Electric': ('BTNPkmnElectr', 'Dien', 'e/e5', '20210111105224'),
    'Ice': ('BTNPkmnIce', 'Bang', 'e/e8', '20210111105223'),
    'Fighting': ('BTNPkmnFighting', 'Giacdau', '9/9c', '20210111110128'),
    'Poison': ('BTNPkmnPoison', 'Doc', 'f/f8', '20210111105224'),
    'Ground': ('BTNPkmnGround', 'Dat', 'e/e9', '20210111105224'),
    'Flying': ('BTNPkmnFlying', 'Bay', 'e/e1', '20210111105224'),
    'Psychic': ('BTNPkmnPsy', 'Sieulinh', '7/72', '20210111110129'),
    'Bug': ('BTNPkmnBug', 'Contrung', '4/4e', '20210111105224'),
    'Rock': ('BTNPkmnRock', 'Da', '1/14', '20210111105224'),
    'Ghost': ('BTNPkmnGhost', 'Ma', '6/6c', '20210111110129'),
    'Dragon': ('BTNPkmnDragon', 'Rong', 'a/a0', '20210111110129'),
    'Dark': ('BTNPkmnDark', 'Bongtoi', '7/70', '20210111105224'),
    'Steel': ('BTNPkmnSteel', 'Thep', '8/82', '20210111110129'),
    'Fairy': ('BTNPkmnFairy', 'Tien', '1/16', '20210111110129'),
}
RAW = os.path.join('analysis', 'type_icons_fandom')
OUT = os.path.join('analysis', 'type_icons')
BACKUP = os.path.join('analysis', 'type_icons_placeholder')

import base64
from fandom_icons_data import ICONS_B64  # noqa: E402
from fandom_icons_fix import FIX_B64  # noqa: E402

ICONS_B64.update(FIX_B64)

os.makedirs(RAW, exist_ok=True)
if not os.path.isdir(BACKUP):
    shutil.copytree(OUT, BACKUP)
for typ, (stem, name, path, cb) in ICONS.items():
    dst = os.path.join(RAW, name + '.webp')
    try:
        open(dst, 'wb').write(base64.b64decode(ICONS_B64[name]))
        Image.open(dst).load()
    except Exception as e:  # noqa: BLE001
        print('bad icon data', typ, type(e).__name__)
        continue
    img = Image.open(dst).convert('RGBA')
    img = img.resize((mti.SIZE, mti.SIZE), Image.LANCZOS)
    mti.write_blp1(img, os.path.join(OUT, stem + '.blp'))
    grey = ImageOps.grayscale(img.convert('RGB')).convert('RGBA')
    grey.putalpha(img.getchannel('A'))
    mti.write_blp1(grey, os.path.join(OUT, 'DIS' + stem + '.blp'))
    print('ok', typ, os.path.getsize(dst), 'bytes')
