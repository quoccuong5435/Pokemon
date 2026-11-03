"""Make the type icons of the 10 types PKLegends has no icon for (BLP1, 64x64, palette, 8-bit alpha).

Output: analysis/type_icons/BTNPkmn<Type>.blp and DISBTNPkmn<Type>.blp (disabled = grey).
Usage (from _PokemonArena2.0_work):  python -I tools/make_type_icons.py
"""
import os
import struct

from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = os.path.join('analysis', 'type_icons')
SIZE = 64
# type: (stem, colour, two letters)
TYPES = {
    'Fighting': ('BTNPkmnFighting', (0xC0, 0x30, 0x28), 'FT'),
    'Ground': ('BTNPkmnGround', (0xE0, 0xC0, 0x68), 'GN'),
    'Flying': ('BTNPkmnFlying', (0xA8, 0x90, 0xF0), 'FL'),
    'Poison': ('BTNPkmnPoison', (0xA0, 0x40, 0xA0), 'PN'),
    'Bug': ('BTNPkmnBug', (0xA8, 0xB8, 0x20), 'BG'),
    'Ghost': ('BTNPkmnGhost', (0x70, 0x58, 0x98), 'GH'),
    'Ice': ('BTNPkmnIce', (0x98, 0xD8, 0xD8), 'IC'),
    'Steel': ('BTNPkmnSteel', (0xB8, 0xB8, 0xD0), 'ST'),
    'Fairy': ('BTNPkmnFairy', (0xEE, 0x99, 0xAC), 'FA'),
    'Dark': ('BTNPkmnDark', (0x70, 0x58, 0x48), 'DK'),
}


def icon(colour, letters, grey=False):
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, SIZE - 3, SIZE - 3], radius=10, fill=colour + (255,), outline=(40, 40, 40, 255), width=3)
    font = ImageFont.load_default()
    box = d.textbbox((0, 0), letters, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((SIZE - w) / 2 - box[0], (SIZE - h) / 2 - box[1]), letters, fill=(255, 255, 255, 255), font=font)
    if grey:
        rgb = ImageOps.grayscale(img.convert('RGB')).convert('RGBA')
        rgb.putalpha(img.getchannel('A'))
        img = rgb
    return img


def write_blp1(img, path):
    """BLP1 palette texture with 8-bit alpha, one mip level (WC3 reads it)."""
    rgba = img.convert('RGBA')
    pal_img = rgba.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    palette = pal_img.getpalette()[:768]
    palette += [0] * (768 - len(palette))
    indices = pal_img.tobytes()
    alpha = rgba.getchannel('A').tobytes()
    data = indices + alpha
    header = struct.pack('<4sIIIIII', b'BLP1', 1, 8, SIZE, SIZE, 0, 0)
    mip_off = [0] * 16
    mip_size = [0] * 16
    head_len = len(header) + 16 * 4 * 2 + 256 * 4
    mip_off[0] = head_len
    mip_size[0] = len(data)
    body = header + struct.pack('<16I', *mip_off) + struct.pack('<16I', *mip_size)
    pal = bytearray()
    for i in range(256):
        r, g, b = palette[3 * i], palette[3 * i + 1], palette[3 * i + 2]
        pal += bytes([b, g, r, 255])
    open(path, 'wb').write(body + bytes(pal) + data)


def main():
    os.makedirs(OUT, exist_ok=True)
    for typ, (stem, colour, letters) in TYPES.items():
        write_blp1(icon(colour, letters), os.path.join(OUT, stem + '.blp'))
        write_blp1(icon(colour, letters, grey=True), os.path.join(OUT, 'DIS' + stem + '.blp'))
        # check: Pillow must read it back as a 64x64 image
        back = Image.open(os.path.join(OUT, stem + '.blp'))
        assert back.size == (SIZE, SIZE), (typ, back.size)
    print('made', len(TYPES) * 2, 'icons in', OUT)


if __name__ == '__main__':
    main()
