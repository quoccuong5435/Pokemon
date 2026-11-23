import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
MAPS = os.path.dirname(ROOT)
V18 = os.path.join(MAPS, 'Pokemon Arena v1.8.w3x')
PKL = os.path.join(MAPS, 'PKLegendsv3.2.w3x')
EXTRACTED = os.path.join(ROOT, 'extracted_v1.8')

import pytest  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'tools', 'v412'))


@pytest.fixture(scope='session')
def npa_data():
    """New Pokemon Arena 1.0 as `build_npa10.build_data` produces it (no asset optimisation, no dev commands), built once
    per session (about a minute). `script` is for READING only: every line break is LF (the file itself keeps the v1.8
    part's bare CR line breaks)."""
    import build_npa10
    if not os.path.isfile(build_npa10.BASE_MAP):
        pytest.skip('v4.2 base map not here')
    _base, files, _dels, opt_stats, script = build_npa10.build_data(optimize_assets=False, dev_mode=False)
    return {'script': script.replace('\r\n', '\n').replace('\r', '\n'), 'files': files, 'opt_stats': opt_stats}
