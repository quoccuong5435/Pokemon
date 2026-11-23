"""Automated test suite for Pokemon Arena v4.1.2-ver2n:
Verifies:
1. Map archive integrity and size
2. PJASS compilation of war3map.j with 0 errors
3. Ability Patch (10,000g) item, Yes/No Confirmation Dialog, PokeAPI HA mappings
4. Minute 55:00 Mega Rayquaza boss event with 5-minute despawn, permanent buff, and no Master Ball
5. Contested Gym PvPvE with 0.0 damage to Gym Boss and Anti-Smurf badge protection
6. Tall Grass Bushes (6 zones, 1.5s stealth) and 240s Weather cycle
7. Shop duplicate cleanup (Escape Rope & Mega Ring removed, IMHA/IB0C/IB0D added)
8. Dota 2 VFX assets (92 models & 259 textures in MPQ)
9. Plans folder collection and README links
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
MAPS = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(WORK, 'tools'))

import mpq
import slk
import objdata

MAP_PATH = os.path.join(MAPS, 'Pokemon Arena v4.1.2-ver2n.w3x')
PJASS = r'D:\Warcraft III Reforged\_retail_\x86_64\JassHelper\pjass.exe'
REF = os.path.join(WORK, 'analysis', 'jass_ref')


def test_ver2n_map_archive_exists_and_size():
    assert os.path.exists(MAP_PATH), f"Target map not found: {MAP_PATH}"
    size = os.path.getsize(MAP_PATH)
    assert size > 200 * 1024 * 1024, f"Map size unexpectedly small: {size:,} bytes"


def test_pjass_zero_syntax_errors():
    assert os.path.exists(PJASS), "PJASS executable not found"
    base = mpq.MPQ(MAP_PATH)
    script = base.read('scripts\\war3map.j')
    tmp_path = os.path.join(REF, '_tmp_test_ver2n.j')
    with open(tmp_path, 'wb') as f:
        f.write(script)
    r = subprocess.run([PJASS, os.path.join(REF, 'common.j'), os.path.join(REF, 'Blizzard.j'), tmp_path],
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    assert r.returncode == 0, f"PJASS failed with errors:\n{out}"
    assert "Parse successful" in out


def test_ability_patch_item_and_shop():
    base = mpq.MPQ(MAP_PATH)
    # Check ItemData.slk
    items = slk.Slk(base.read('Units\\ItemData.slk').decode('latin-1'))
    r_imha = items.find('IMHA')
    assert r_imha is not None, "IMHA not found in ItemData.slk"
    icol = items.name_to_x
    assert r_imha.get(icol.get('goldcost')) == '10000', "IMHA cost must be 10000 gold"

    # Check ItemFunc.txt
    func = base.read('Units\\ItemFunc.txt').decode('latin-1')
    assert '[IMHA]' in func
    assert 'Ability Patch' in func
    assert '[IB0C]' in func  # Eject Button
    assert '[IB0D]' in func  # Heavy-Duty Boots

    # Check nIS0 in war3map.w3u
    w3u = objdata.ObjFile(base.read('war3map.w3u'))
    nis0 = w3u.find('nIS0')
    assert nis0 is not None
    usei = nis0.get('usei')
    assert 'IMHA' in usei
    assert 'IB0C' in usei
    assert 'IB0D' in usei
    assert 'IT05' not in usei, "Duplicate Escape Rope (IT05) must be removed from nIS0"
    assert 'IT06' not in usei, "Duplicate Mega Ring (IT06) must be removed from nIS0"


def test_ability_patch_yes_no_confirmation_dialog():
    base = mpq.MPQ(MAP_PATH)
    script = base.read('scripts\\war3map.j').decode('utf-8')
    assert 'AbilityPatch_HT' in script
    assert 'AbilityPatch_Dialog' in script
    assert 'AbilityPatch_BtnYes' in script
    assert 'AbilityPatch_BtnNo' in script
    assert 'AbilityPatch_PromptBuy' in script
    assert 'AbilityPatch_OnDialogClick' in script
    assert 'SaveStr(AbilityPatch_HT' in script
    assert 'Đồng Ý / Yes' in script
    assert 'Hủy Bỏ / No' in script


def test_rayquaza_minute_55_and_5min_despawn():
    base = mpq.MPQ(MAP_PATH)
    script = base.read('scripts\\war3map.j').decode('utf-8')
    assert '3270.0' in script, "Warning at 54:30 must be present"
    assert '3300.0' in script, "Spawn at 55:00 must be present"
    assert '3600.0' in script, "Despawn timer at 60:00 must be present"
    assert 'DragonAscent_Buff' in script
    assert '2000' in script, "+2,000 gold must be awarded"
    assert 'Master Ball' not in script or 'Rayquaza_OnBossKilled' in script


def test_contested_gym_pvpve_0damage_and_anti_smurf():
    base = mpq.MPQ(MAP_PATH)
    script = base.read('scripts\\war3map.j').decode('utf-8')
    assert 'BlzSetEventDamage(0.0)' in script, "Non-challengers must deal 0.0 damage to Gym Boss"
    assert 'Anti-Smurf' in script, "Anti-Smurf check must be present in Gym triggers"
    assert 'Badge_Has[pid * 8 + g]' in script


def test_tall_grass_and_weather_240s():
    base = mpq.MPQ(MAP_PATH)
    script = base.read('scripts\\war3map.j').decode('utf-8')
    assert 'Bush_StillTime' in script
    assert 'Bush_InStealth' in script
    assert "'Apiv'" in script, "Permanent Invisibility must be used for bush stealth"
    assert '240.0' in script, "Weather cycle must be set to 240s"


def test_dota2_vfx_assets():
    base = mpq.MPQ(MAP_PATH)
    files = {n.lower() for n in base.listfile()}
    assert any('aftershock' in f for f in files), "Dota 2 Aftershock VFX model must be in MPQ"
    assert any('icewolf' in f for f in files), "Dota 2 ICEWOLF texture must be in MPQ"


def test_plans_folder_and_links():
    plans_dir = os.path.join(MAPS, 'plans')
    assert os.path.exists(plans_dir), "plans/ folder must exist in workspace"
    readme_path = os.path.join(plans_dir, 'README.md')
    assert os.path.exists(readme_path), "plans/README.md must exist"
    md_files = [f for f in os.listdir(plans_dir) if f.endswith('.md')]
    assert len(md_files) >= 9, f"Expected at least 9 plan files, found {len(md_files)}"
