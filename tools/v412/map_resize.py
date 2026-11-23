"""Resize the map from 160x160 to 192x192 (+16 tiles / +2048 units on each side).
Keeps (0, 0) centered so all existing bases, units, camps and rects keep their exact coordinates.
"""
import struct


def resize_w3e(w3e):
    p = 4 + 4 + 1 + 4
    n_g = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_g * 4
    n_c = struct.unpack_from('<I', w3e, p)[0]
    p += 4 + n_c * 4
    header_p = p
    mx, my, ox, oy = struct.unpack_from('<IIff', w3e, p)
    p += 16
    tiles = w3e[p:]

    new_mx, new_my = 193, 193
    new_ox, new_oy = -12288.0, -12288.0
    border_corner = tiles[:7]

    new_tiles = bytearray(new_mx * new_my * 7)
    for ny in range(new_my):
        for nx in range(new_mx):
            dst_idx = (ny * new_mx + nx) * 7
            if 16 <= nx <= 176 and 16 <= ny <= 176:
                ox_idx = ((ny - 16) * mx + (nx - 16)) * 7
                new_tiles[dst_idx:dst_idx + 7] = tiles[ox_idx:ox_idx + 7]
            else:
                new_tiles[dst_idx:dst_idx + 7] = border_corner

    new_w3e = bytearray(w3e[:header_p])
    new_w3e += struct.pack('<IIff', new_mx, new_my, new_ox, new_oy)
    new_w3e += new_tiles
    return bytes(new_w3e)


def resize_wpm(wpm):
    cells = wpm[16:]
    new_cells = bytearray(b'\x0a' * (768 * 768))  # 0x0a = unwalkable / unbuildable boundary
    for cy in range(640):
        src_p = cy * 640
        dst_p = (cy + 64) * 768 + 64
        new_cells[dst_p:dst_p + 640] = cells[src_p:src_p + 640]
    new_header = struct.pack('<4sIII', b'MP3W', 0, 768, 768)
    return new_header + bytes(new_cells)


def resize_shd(shd):
    new_shd = bytearray(b'\xff' * (768 * 768))
    for cy in range(640):
        src_p = cy * 640
        dst_p = (cy + 64) * 768 + 64
        new_shd[dst_p:dst_p + 640] = shd[src_p:src_p + 640]
    return bytes(new_shd)


def resize_w3i(w3i):
    b = bytearray(w3i)
    # Find dynamic offset of (160, 160) (map width and height)
    target_offset = -1
    for i in range(len(b) - 8):
        w, h = struct.unpack_from('<ii', b, i)
        if w == 160 and h == 160:
            target_offset = i
            break
    if target_offset < 0:
        raise SystemExit('map_resize: (160, 160) not found in w3i')

    # pack width, height = 192, 192
    struct.pack_into('<ii', b, target_offset, 192, 192)
    # camera bounds is 48 bytes before width & height (12 ints / 4 margins + 8 floats)
    cam_offset = target_offset - 48
    cam = (-11776.0, -12032.0, 11776.0, 12032.0, -11776.0, 12032.0, 11776.0, -12032.0)
    struct.pack_into('<8f', b, cam_offset, *cam)
    return bytes(b)


def patch_script(s):
    old_cam = 'call SetCameraBounds(-10240.0+GetCameraMargin(CAMERA_MARGIN_LEFT),-10240.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM),10240.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),10240.0-GetCameraMargin(CAMERA_MARGIN_TOP),-10240.0+GetCameraMargin(CAMERA_MARGIN_LEFT),10240.0-GetCameraMargin(CAMERA_MARGIN_TOP),10240.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),-10240.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM))'
    new_cam = 'call SetCameraBounds(-12288.0+GetCameraMargin(CAMERA_MARGIN_LEFT),-12288.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM),12288.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),12288.0-GetCameraMargin(CAMERA_MARGIN_TOP),-12288.0+GetCameraMargin(CAMERA_MARGIN_LEFT),12288.0-GetCameraMargin(CAMERA_MARGIN_TOP),12288.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),-12288.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM))'
    if old_cam in s:
        s = s.replace(old_cam, new_cam, 1)
    return s
