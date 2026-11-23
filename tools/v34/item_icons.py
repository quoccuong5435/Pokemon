"""v3.4.6: item icons from the TrainerOps PNG set the user saved next to the HTML page (approved 2026-11-08).

Each PNG (30x30 or 160x160) is resized to 64x64 and written as BLP1 (palette, 8-bit alpha, the same format as
make_type_icons.py). Disabled copies come from assets._disabled_icon. Files go to war3mapImported\\V34\\Items\\.
Items without a PNG keep the map's own held-item icon (extras._held).
Usage: plan() -> (art, files): art maps item id -> Art path, files maps archive path -> bytes.
"""
import os
import tempfile

from PIL import Image, ImageOps

from make_type_icons import write_blp1, SIZE  # tools/make_type_icons.py (on sys.path through build_v34)

WORK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR_SUFFIX = 'TrainerOps_files'
DEST = 'war3mapImported\\V34\\Items\\'

# item id -> PNG stem (names of the TrainerOps image files)
PNG = {
    # battle items
    'IB00': 'life-orb', 'IB03': 'choice-scarf', 'IB04': 'leftovers', 'IB05': 'focus-sash',
    'IB06': 'expert-belt', 'IB07': 'rocky-helmet', 'IB09': 'scope-lens', 'IB0A': 'kings-rock',
    'IB0C': 'shell-bell', 'IB0D': 'bright-powder', 'IB0E': 'wise-glasses', 'IB0F': 'quick-claw',
    # berries
    'IT03': 'sitrus-berry', 'IT04': 'lum-berry', 'IT09': 'oran-berry',
    # type items (type item id -> type icon)
    'I00Q': 'charcoal', 'I00R': 'miracle-seed', 'I00S': 'mystic-water', 'I00T': 'magnet',
    'I00U': 'silver-powder', 'I00V': 'poison-barb', 'I00W': 'never-melt-ice', 'I00X': 'dragon-fang',
    'I00Y': 'sharp-beak', 'I00Z': 'silk-scarf', 'I010': 'twisted-spoon', 'I011': 'black-belt',
    'I012': 'hard-stone', 'I013': 'soft-sand', 'I01X': 'metal-coat', 'I01Y': 'black-glasses',
    'I020': 'spell-tag', 'ITFY': 'fairy-feather',
}


def _src_dir():
    parent = os.path.dirname(WORK)
    for n in os.listdir(parent):
        if n.endswith(SRC_DIR_SUFFIX):
            return os.path.join(parent, n)
    raise SystemExit('TrainerOps PNG folder not found next to the work folder')


def _blp_bytes(img, tmp):
    write_blp1(img, tmp)
    return open(tmp, 'rb').read()


def plan():
    src = _src_dir()
    names = {n.lower(): n for n in os.listdir(src)}
    art = {}
    files = {}
    tmp = os.path.join(tempfile.gettempdir(), 'pa_item_icon.blp')
    for iid, stem in sorted(PNG.items()):
        png = names.get(stem + '.png')
        if png is None:
            raise SystemExit('missing icon file for %s: %s.png' % (iid, stem))
        img = Image.open(os.path.join(src, png)).convert('RGBA').resize((SIZE, SIZE), Image.LANCZOS)
        data = _blp_bytes(img, tmp)
        # disabled copy: grey and 60% dark, same alpha (Pillow cannot read BLP1 with alpha back, so it is made from RGBA)
        grey = ImageOps.grayscale(img.convert('RGB')).point(lambda v: int(v * 0.6)).convert('RGB')
        grey = Image.merge('RGBA', tuple(grey.getchannel(b) for b in 'RGB') + (img.getchannel('A'),))
        dis = _blp_bytes(grey, tmp)
        base = 'BTNPkmn_' + stem + '.blp'
        files[DEST + base] = data
        files[DEST + 'DIS' + base] = dis
        art[iid] = DEST + base
    if os.path.exists(tmp):
        os.remove(tmp)
    return art, files
