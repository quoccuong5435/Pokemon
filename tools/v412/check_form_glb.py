"""Checks the form models downloaded for the form branches (GEMINI.md section 23, docs/form-models/README.md).

For every row of docs/form-models/can-tai.csv that needs a download, looks for
  <Maps/Download>/imports/pokemon_3d_forms/<key>.glb
and its line in imports/pokemon_3d_forms/LICENSES.csv, converts it in memory with glb_to_mdx (the converter the
map build uses) and runs mdx_check on the result. Writes nothing; prints one line per model and a summary.

    python tools/v412/check_form_glb.py            # all rows
    python tools/v412/check_form_glb.py raichu-alola kleavor
"""
import csv
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(WORK, 'tools'), HERE]
import glb_to_mdx  # noqa: E402
import mdx_check  # noqa: E402

FORMS_DIR = os.path.join(os.path.dirname(WORK), 'imports', 'pokemon_3d_forms')
NEEDED = os.path.join(WORK, 'docs', 'form-models', 'can-tai.csv')
LICENSES = os.path.join(FORMS_DIR, 'LICENSES.csv')
MAX_MB = 20.0
MAX_VERTS = 65535  # per geoset, glb_to_mdx refuses more
OK_LICENSES = ('CC0', 'CC-BY', 'CC BY')  # CC-BY needs the author named in the map credits


def needed_rows():
    with open(NEEDED, encoding='utf-8-sig') as fh:
        return [r for r in csv.DictReader(fh) if r['trang_thai'].startswith('TAI MOI')]


def licenses():
    if not os.path.isfile(LICENSES):
        return {}
    with open(LICENSES, encoding='utf-8-sig') as fh:
        return {r['key'].strip(): r for r in csv.DictReader(fh)}


def geoset_verts(mdx):
    p, out = 4, []
    while p + 8 <= len(mdx):
        tag, size = mdx[p:p + 4], struct.unpack_from('<I', mdx, p + 4)[0]
        if tag == b'GEOS':
            q, end = p + 8, p + 8 + size
            while q < end:
                out.append(struct.unpack_from('<I', mdx, q + 8)[0])
                q += struct.unpack_from('<I', mdx, q)[0]
        p += 8 + size
    return out


def check(key, lic, skip_license=True):
    path = os.path.join(FORMS_DIR, key + '.glb')
    if not os.path.isfile(path):
        return 'CHUA CO', ''
    mb = os.path.getsize(path) / 1048576.0
    probs = []
    if mb > MAX_MB:
        probs.append('file %.1f MB > %d MB' % (mb, MAX_MB))
    row = lic.get(key)
    if not skip_license:
        if not row or not row.get('url', '').strip():
            probs.append('thieu dong trong LICENSES.csv')
        elif not row.get('giay_phep', '').strip().upper().startswith(OK_LICENSES):
            probs.append('giay phep "%s" khong phai CC0 / CC-BY' % row.get('giay_phep', ''))
    try:
        with open(path, 'rb') as fh:
            mdx, tex = glb_to_mdx.convert_glb_to_mdx(fh.read(), 'Pk_' + key, 'PkFx\\Forms\\t\\' + key,
                                                     target_size=100.0)
    except Exception as e:  # noqa: BLE001 - report any converter failure for this file
        return 'LOI', '; '.join(probs + ['khong chuyen duoc: %s' % e])
    errs = mdx_check.check(mdx)
    if errs:
        probs.append('mdx_check: ' + errs[0])
    verts = geoset_verts(mdx)
    if verts and max(verts) > MAX_VERTS:
        probs.append('geoset %d dinh > %d' % (max(verts), MAX_VERTS))
    info = '%.1f MB, %d geoset, %d dinh, %d texture' % (mb, len(verts), sum(verts), len(tex))
    return ('LOI' if probs else 'DAT'), '; '.join([info] + probs)


def main(argv):
    skip_license = '--check-license' not in argv
    keys = [a for a in argv if a not in ('--skip-license', '--check-license')]
    rows = needed_rows()
    if keys:
        rows = [r for r in rows if r['key'] in keys]
    lic = licenses()
    count = {}
    for r in rows:
        st, msg = check(r['key'], lic, skip_license=skip_license)
        count[st] = count.get(st, 0) + 1
        if st != 'CHUA CO' or keys:
            print('%-8s %-28s %s' % (st, r['key'], msg))
    print('Tong %d model can tai: %s' % (len(rows), ', '.join('%s %d' % kv for kv in sorted(count.items()))))
    return 1 if count.get('LOI') else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
