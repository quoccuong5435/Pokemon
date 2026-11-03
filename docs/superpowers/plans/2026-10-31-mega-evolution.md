# Pokemon Arena v2.0 Mega Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `Pokemon Arena v2.0.w3x` from the untouched v1.8 map, adding 16 Mega Evolutions (stones, shops, Mega Evolve abilities, skins, stat bonuses, Kangaskhan Kid).

**Architecture:** A Python build pipeline (`tools/build_v2.py`) reads the v1.8 MPQ, imports Mega assets (PKLegends models or `mega_models/` overrides or fallback), appends object data (w3u units, SLK items/abilities + strings), injects a hand-written JASS module (`tools/jass/mega.j` + generated data init) into `scripts\war3map.j`, renames the map, and writes a new MPQ that keeps every original block. One table (`tools/mega_data.py`) is the single source of truth for all 16 Megas.

**Tech Stack:** Python 3.11 (stdlib + Pillow 12 for BLP), pytest 9, JASS (WC3 Reforged 1.36.1 natives).

**Spec:** `docs/superpowers/specs/2026-10-31-mega-evolution-design.md`

## Global Constraints

- Input `../Pokemon Arena v1.8.w3x` is read-only; output `../Pokemon Arena v2.0.w3x`.
- Asset source map `../PKLegendsv3.1b.w3x` is read-only.
- Map format unchanged: w3i v25, w3u v2, SLK object data. Only additions (plus map-name strings).
- Reforged natives allowed (target 1.36.1): `BlzSetUnitSkin`, `BlzStartUnitAbilityCooldown`, `BlzGetUnitAbilityCooldownRemaining`, `BlzSetHeroProperName`, `BlzGetUnitBaseDamage`, `BlzGetUnitWeaponIntegerField`.
- New IDs: skins `hM00`–`hM0F`, Kid `hMK0`, shops `nMS1`/`nMS2`, stones `IM00`–`IM0F`, Mega Evolve `AM00`–`AM0F`, attribute bonus `AMA0`–`AMAF`, shared bonus `AMB1` (armor +5), `AMB2` (move speed +40), `AMB3` (attack speed +25%).
- Mega duration 60 s, cooldown 150 s, Kid bonus 25% (base damage + STR), Kid proc at most once per 0.5 s, fallback scale ×1.25.
- Stone prices: #0–#12 = 5000 gold, #13–#15 = 7000 gold.
- Shops at (±5248, 384) [Shop I, stones #0–#7] and (±5248, −384) [Shop II, stones #8–#15]; west facing 0°, east 180°; owner `Player(PLAYER_NEUTRAL_PASSIVE)`.
- Imported Mega assets live under `war3mapImported\Mega\` (models and their textures); icons under `ReplaceableTextures\CommandButtons\` / `CommandButtonsDisabled\`.
- All JASS identifiers added by us start with `Mega_` (functions/globals).
- Not a git repo: no commit steps. Tests live in `_PokemonArena2.0_work/tests/`, run with `python -I -m pytest tests -q` from `_PokemonArena2.0_work`.

## Review Focus

- A texture name in a PKL model equal to an existing v1.8 file (e.g. `Abra.blp`) must not overwrite it → Task 3 test `test_texture_paths_are_namespaced`.
- Charizard/Mewtwo holding both X and Y stones: both buttons present, using one puts the other on cooldown → Task 6 JASS + Task 8 manual check line; Task 4 test `test_mega_evolve_orders_unique` keeps their orders distinct.
- Dropping and re-picking a stone must not reset cooldown → Task 6 (`Mega_SyncAbility` restores remaining time); manual check in Task 8.
- Hero dying (or removed by `ReplaceUnitBJ`) while Mega must fully revert and not leave a Kid behind → Task 6 (`Mega_End` on death; tick cleans units whose type id is 0).
- Hash table capacity: the v1.8 archive has 1024 slots / 790 used; the build must fail loudly, not corrupt, if slots run out → Task 1 test `test_save_refuses_when_full`.

---

### Task 1: MPQ/objdata/SLK round-trip safety

**Files:**
- Modify: `tools/mpq.py` (`MPQ.save_with`: replace the `needed * 1.3` check with "raise `RuntimeError('hash table full')` only when no free/deleted slot remains")
- Create: `tests/test_formats.py`

**Interfaces:**
- Produces: `mpq.MPQ(path)`, `.read(name) -> bytes`, `.has(name) -> bool`, `.save_with(out_path, replace_files: dict[str, bytes], delete_files=(), extra_listfile: bytes|None)`; `objdata.ObjFile(data, leveled=False)`, `.to_bytes()`, `.custom: list[Obj]`; `objdata.Obj(orig, new, mods)`, `.set(field, typ, value, level=0, data=0)`, `.get(field)`; `slk.Slk(text)`, `.find(id)`, `.get(row, col)`, `.rows`, `.to_text()`.

- [ ] **Step 1: Write tests** in `tests/test_formats.py`:
  - `test_mpq_roundtrip_keeps_all_blocks`: save v1.8 with `{'war3map.j': b'x'}` to a tmp file; reopen; every name in `extracted_v1.8/_names.txt` except `war3map.j` reads back byte-identical to the original archive; `read('war3map.j') == b'x'`.
  - `test_mpq_adds_new_file`: save with `{'war3mapImported\\Mega\\t.txt': b'hello'}`; reopen; `read(...) == b'hello'`.
  - `test_save_refuses_when_full`: build a dict of 300 new names → `pytest.raises(RuntimeError, match='hash table full')`.
  - `test_w3u_roundtrip`: `ObjFile(w3u).to_bytes() == w3u` for `extracted_v1.8/war3map.w3u`.
  - `test_slk_roundtrip_values`: parse `ItemData.slk` → `to_text()` → parse again; for every row and column, values equal.
- [ ] **Step 2: Run** `python -I -m pytest tests/test_formats.py -q` → expect `test_mpq_adds_new_file` or `test_save_refuses_when_full` to fail (capacity check is too strict).
- [ ] **Step 3: Fix** the capacity check in `save_with`.
- [ ] **Step 4: Run** the same command → all PASS.

### Task 2: Mega data table

**Files:**
- Create: `tools/mega_data.py`
- Create: `tests/test_mega_data.py`

**Interfaces:**
- Produces: `MEGAS: list[Mega]` (16 entries, index = spec `#`), dataclass `Mega(index:int, key:str, name:str, base_unit:str, base_name:str, stone_id:str, stone_name:str, price:int, skin_id:str, evolve_id:str, attr_id:str, str_:int, agi:int, int_:int, pkl_model:str|None, pkl_icon:str|None, tint:tuple[int,int,int], fx:str, order:str)`; constants `SHOP1_ID='nMS1'`, `SHOP2_ID='nMS2'`, `KID_ID='hMK0'`, `BONUS_IDS=('AMB1','AMB2','AMB3')`, `DURATION=60.0`, `COOLDOWN=150.0`.
- Keys (used for `mega_models/<key>.mdx`): `MegaVenusaur, MegaCharizardX, MegaCharizardY, MegaBlastoise, MegaBeedrill, MegaPidgeot, MegaAlakazam, MegaGengar, MegaKangaskhan, MegaPinsir, MegaGyarados, MegaSteelix, MegaScizor, MegaMewtwoX, MegaMewtwoY, MegaRayquaza`.
- `pkl_model` = PKL stem (`MegaBisaflor`, `MegaGlurakX`, `MegaGlurakY`, `MegaTurtok`, None, `MegaTauboss`, `MegaSimsala`, `MegaGengar`, None (Kangaskhan uses base model + Kid), `MegaPinsir`, `MegaGarados`, `MegaSteelix`, `MegaScherox`, None, None, None); `pkl_icon` = PKL BTN filename from the analysis (`BTNMegaBisaflor.blp`, `BTNMegaGlurakX.blp`, `BTNMegaGlurakY.blp`, `BTNMegaTurtok.blp`, None, `BTNTauboss.blp`, `BTNMegaSimsala.blp`, `BTNMegaGengar.blp`, `BTNMega-Kangama.blp`, `BTNMegaPinsir.blp`, `BTNMegaGarados.blp`, `BTNMSteelix.blp`, `BTNMegaScherox.blp`, None, None, None).
- `fx`: `''` for PKL models; fallback aura `Abilities\\Spells\\Other\\GeneralAuraTarget\\GeneralAuraTarget.mdl` for #4, #13, #14, #15. Tints: #4 (255,220,90), #13 (170,200,255), #14 (225,170,255), #15 (140,255,170), others (255,255,255).
- `order`: 16 distinct Channel base orders not used by any v1.8 ability (Task 4 test enforces).

- [ ] **Step 1: Write tests** `test_sixteen_megas_in_spec_order` (names/base units/stones/prices exactly as the spec table), `test_attribute_bonus_totals_30` (each `str_+agi+int_ == 30`, values equal the spec table), `test_ids_unique_and_in_ranges` (`skin_id` hM00–hM0F, `stone_id` IM00–IM0F, `evolve_id` AM00–AM0F, `attr_id` AMA0–AMAF, all distinct).
- [ ] **Step 2: Run** `python -I -m pytest tests/test_mega_data.py -q` → FAIL (module missing).
- [ ] **Step 3: Implement** `tools/mega_data.py` with the values above and the spec table.
- [ ] **Step 4: Run** → PASS.

### Task 3: Asset collection (models, textures, icons)

**Files:**
- Modify: `tools/mdx.py` (add `patch_texture_paths(data: bytes, mapping: dict[str, str]) -> bytes` — rewrites `TEXS` 260-byte path fields, zero-padded, size unchanged)
- Create: `tools/assets.py`
- Create: `tests/test_assets.py`

**Interfaces:**
- Consumes: `mpq.MPQ`, `mega_data.MEGAS`.
- Produces: `collect(pkl: MPQ|None, base: MPQ, override_dir: str) -> Assets` with `Assets.files: dict[str, bytes]` (archive path → content), `Assets.model_path: dict[int, str]` (mega index → model path to write into `umdl`, `.mdl` extension like v1.8 uses), `Assets.icon_path: dict[int, str]`, `Assets.kid_model: str`, `Assets.warnings: list[str]`.
- Resolution order per Mega: `mega_models/<key>.mdx` (textures referenced by it looked up next to it) → PKL model → fallback (base unit's `umdl` from v1.8 w3u, no files). Icon: `mega_models/BTN<key>.blp` → PKL icon → base unit's `uico`.
- Model files go to `war3mapImported\Mega\<key>.mdx` (+ `<key>_portrait.mdx` when the source has one); each referenced texture goes to `war3mapImported\Mega\<texture basename>` and the model's `TEXS` paths are patched to that; textures with empty path (replaceable id) are left alone. Kid: `war3mapImported\Mega\KidKangama.mdx`.
- Icons go to `ReplaceableTextures\CommandButtons\BTN<key>.blp` and `ReplaceableTextures\CommandButtonsDisabled\DISBTN<key>.blp`; when the source has no DISBTN, create one with Pillow: decode, convert to greyscale at 60% brightness, save as BLP1 (`blp_version="BLP1"`).

- [ ] **Step 1: Write tests** (use the real PKL map, module-scoped fixture):
  - `test_all_pkl_megas_resolved`: for indices 0,1,2,3,5,6,7,9,10,11,12 `model_path[i] == 'war3mapImported\\Mega\\<key>.mdl'` and `<key>.mdx` is in `files`.
  - `test_fallbacks_use_base_model`: indices 4,8,13,14,15 → `model_path[i]` equals the base unit's v1.8 `umdl`.
  - `test_texture_paths_are_namespaced`: every non-empty texture path inside every imported `.mdx` starts with `war3mapImported\Mega\` and exists in `files`.
  - `test_no_existing_file_overwritten`: no key of `files` exists in the v1.8 archive.
  - `test_every_mega_has_btn_and_disbtn`: 16 × (BTN, DISBTN) present in `files`, each decodes with Pillow.
  - `test_override_dir_wins`: write PKL `MegaGengar.mdx` into a tmp dir as `MegaRayquaza.mdx` together with its texture file `MegaGengar.blp`; `collect(..., override_dir=tmp).model_path[15] == 'war3mapImported\\Mega\\MegaRayquaza.mdl'` and `war3mapImported\\Mega\\MegaGengar.blp` is in `files`.
- [ ] **Step 2: Run** `python -I -m pytest tests/test_assets.py -q` → FAIL.
- [ ] **Step 3: Implement** `patch_texture_paths` and `tools/assets.py`.
- [ ] **Step 4: Run** → PASS.

### Task 4: Object data (units, items, abilities)

**Files:**
- Create: `tools/objects.py`
- Create: `tests/test_objects.py`

**Interfaces:**
- Consumes: `objdata`, `slk`, `mega_data`, `assets.Assets`.
- Produces: `apply(files: dict[str, bytes], assets: Assets) -> dict[str, bytes]` returning new contents for `war3map.w3u`, `Units\ItemData.slk`, `Units\ItemFunc.txt`, `Units\AbilityData.slk`, `Units\CampaignAbilityStrings.txt`.
- Units (w3u custom table, base `hfoo` for skins/Kid, `ngme` for shops copying all mods of `n00O`): skin `umdl`=model path, `uico`=icon, `unam`=Mega name, `usca`= base unit scale (fallback ×1.25). Kid: `umdl` Kid model, `uabi`='Aloc,Avul', `umvs`=400, `ucol`=0, `uaen`=0 (attacks disabled; damage comes from the trigger), `unam`='Kangaskhan Kid'. Shops: `unam`='Mega Shop I'/'Mega Shop II', `usei`= stone ids, tint `uclr`=200 `uclg`=120 `uclb`=255.
- Items: one row per stone copied from row `I012` (Permanent, Hard Stone) with `abilList` empty, `goldcost`=price, `stockMax`=1, `stockRegen`=60; ItemFunc section `[IMxx]` with `Name`, `Tip=Purchase |cffffcc00<stone>|r`, `Ubertip` (which Pokemon, how to use, "Mega 60s, cooldown 150s"), `Art`=Mega icon, `Buttonpos` = slot in its shop (index % 8 → x = i%4, y = i//4).
- Abilities: copy existing rows by code when present, else build from column names: `AM0x` code `ANcl` (levels 1, Cool1 150, Cost1 0, DataB1 0 = no target, DataC1 1 = visible, DataF1 = mega.order, targs1 `_`), strings `[AM0x]` `Name=Mega Evolve`, `Tip=Mega Evolve - <Mega name> |cffffcc00[D]|r`, `Hotkey=D`, `Buttonpos=3,1`, `Art`=Mega icon, `Ubertip`; `AMAx` code `Aamk` DataA1=agi DataB1=int DataC1=str DataD1=1 (hide); `AMB1` code `AIde` DataA1=5; `AMB2` code `AIms` DataA1=40; `AMB3` code `AIsx` DataA1=0.25. Bonus abilities: `item`=1, no Art.

- [ ] **Step 1: Write tests**:
  - `test_units_added`: reparsed w3u has `hM00`…`hM0F`, `hMK0`, `nMS1`, `nMS2`; `hM01.umdl == 'war3mapImported\\Mega\\MegaCharizardX.mdl'`; `nMS1.usei == 'IM00,IM01,IM02,IM03,IM04,IM05,IM06,IM07'`; `nMS2.usei == 'IM08,…,IM0F'`; original 364 objects unchanged.
  - `test_items_rows_and_strings`: `IM0D` goldcost `7000`, `IM00` goldcost `5000`, class `Permanent`; `[IM01]` section has `Name=Charizardite X`.
  - `test_abilities_rows`: `AM00` code `ANcl`, Cool1 `150`; `AMA1` DataC1 `20` DataA1 `5` DataB1 `5`; `AMB2` DataA1 `40`.
  - `test_mega_evolve_orders_unique`: the 16 `DataF1` orders are distinct and none appears as an order/DataF value in the v1.8 `AbilityData.slk` or `CampaignAbilityStrings.txt` (`Order=`/`Orderon=`/`Orderoff=` keys).
- [ ] **Step 2: Run** `python -I -m pytest tests/test_objects.py -q` → FAIL.
- [ ] **Step 3: Implement** `tools/objects.py` (pick the 16 orders in `mega_data.py` so the uniqueness test passes).
- [ ] **Step 4: Run** → PASS.

### Task 5: JASS checker

**Files:**
- Create: `tools/jasscheck.py`
- Create: `tests/test_jasscheck.py`

**Interfaces:**
- Produces: `check(source: str, known_functions: dict[str, int], known_globals: set[str]) -> list[str]` (empty list = OK). Checks: balanced `globals/endglobals`, `function/endfunction`, `if/elseif/else/endif`, `loop/endloop`; every called identifier is defined in `source` or in `known_functions` with the right argument count; every referenced variable is a local, parameter, our global, or in `known_globals`; `set` targets exist; no duplicate function names. `NATIVES: dict[str, int]` — name → arg count for every native/BJ the module uses (list them; counts per 1.36 `common.j`/`Blizzard.j`).

- [ ] **Step 1: Write tests** `test_ok_snippet` (small valid function → `[]`), `test_unknown_function` (`call Foo()` → message containing `Foo`), `test_wrong_arg_count` (`call DestroyEffect(a, b)` → message), `test_unbalanced_if` (missing `endif` → message), `test_undeclared_variable`.
- [ ] **Step 2: Run** `python -I -m pytest tests/test_jasscheck.py -q` → FAIL.
- [ ] **Step 3: Implement** a line-based tokenizer (strings, rawcodes `'xxxx'`, `//` comments) and the checks above.
- [ ] **Step 4: Run** → PASS.

### Task 6: Mega JASS module + injection

**Files:**
- Create: `tools/jass/mega.j` (hand-written; globals block between `//MEGA_GLOBALS_BEGIN`/`//MEGA_GLOBALS_END` markers, functions after)
- Create: `tools/inject.py`
- Create: `tests/test_inject.py`

**Interfaces:**
- Consumes: `mega_data`, `jasscheck.check`.
- Produces: `gen_data_init() -> str` (JASS `function Mega_InitData takes nothing returns nothing` filling arrays from `MEGAS`, incl. base scale from v1.8 w3u), `inject(war3map_j: str) -> str` (inserts globals before the first `endglobals`, functions + `Mega_InitData` before `function main takes nothing returns nothing`, `call Mega_Init()` as the last line of `main`, replaces `SetMapName("Pokemon Arena v1.8")` with `SetMapName("Pokemon Arena v2.0")`).
- JASS API (all in `mega.j`):
  - Globals: `hashtable Mega_HT`, `real Mega_Time`, arrays `Mega_Base, Mega_Stone, Mega_Skin, Mega_Evolve, Mega_Attr` (integer), `Mega_Name, Mega_Fx` (string), `Mega_Scale, Mega_BaseScale` (real), `Mega_R, Mega_G, Mega_B` (integer), `integer Mega_N=16`, `group Mega_Group`.
  - `Mega_IndexForUnit(u) -> integer` / `Mega_HasStone(u, idx) -> boolean`: index of first Mega whose base type matches and whose stone is in inventory, else −1.
  - `Mega_SyncAbility(u)`: called each tick for every hero of players 0–11 not in Mega form: for each idx with matching base type, add `Mega_Evolve[idx]` when stone held (then `BlzStartUnitAbilityCooldown` with stored remaining = `cdEnd - Mega_Time` if > 0), remove when not held (store remaining first via `BlzGetUnitAbilityCooldownRemaining`).
  - `Mega_Start(u, idx)`: on `EVENT_PLAYER_UNIT_SPELL_EFFECT` of `Mega_Evolve[idx]`; stores state (idx+1, end = `Mega_Time+60`, cdEnd = `Mega_Time+150`, original proper name), puts other X/Y button on cooldown 150, transform effect, `BlzSetUnitSkin`, scale, tint, `BlzSetHeroProperName("Mega …")`, adds `Mega_Attr[idx]`, `AMB1`, `AMB2`, `AMB3`, aura `Mega_Fx` if non-empty, Kid for index 8, message to all players.
  - `Mega_End(u)`: reverse all of the above; called at expiry, on death, and for removed units (type id 0).
  - `Mega_KidFollow(u)`: move order to point 90 units behind-right of the mother when farther than 50, teleport when farther than 600, else face mother's facing.
  - `Mega_OnAttacked()`: attacker is Mega Kangaskhan and last proc ≥ 0.5 s ago → Kid plays `attack`, `UnitDamageTarget(mother, target, 0.25 * (BlzGetUnitBaseDamage(mother,0) + GetHeroStr(mother,true)), true, false, ConvertAttackType(BlzGetUnitWeaponIntegerField(mother, UNIT_WEAPON_IF_ATTACK_ATTACK_TYPE, 0)), DAMAGE_TYPE_NORMAL, WEAPON_TYPE_WHOKNOWS)`.
  - `Mega_Init()`: `Mega_InitData()`, triggers (cast, death, attacked), timer 0.25 s periodic `Mega_Tick`, 4 shops, quest "Mega Evolution" (`CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, …)`) listing stones, prices, rules, credits ("Mega models: PKLegends team & Hive Workshop authors").

- [ ] **Step 1: Write tests**:
  - `test_injected_script_passes_checker`: `jasscheck.check(globals+functions of injected module)` with `NATIVES` → `[]`.
  - `test_inject_positions`: in `inject(v18)`, `Mega_HT` declared before first `endglobals`; `function Mega_Init` appears before `function main`; the text between `function main` and its `endfunction` ends with `call Mega_Init()`; `SetMapName("Pokemon Arena v2.0")` present and `v1.8` absent; the original script with our inserted spans removed equals v1.8 except the map name.
  - `test_data_init_matches_table`: `gen_data_init()` contains `set Mega_Base[1]='E00E'`, `set Mega_Stone[13]='IM0D'`, `set Mega_Skin[15]='hM0F'`.
- [ ] **Step 2: Run** `python -I -m pytest tests/test_inject.py -q` → FAIL.
- [ ] **Step 3: Implement** `tools/jass/mega.j` and `tools/inject.py`.
- [ ] **Step 4: Run** → PASS.

### Task 7: Build script + map info

**Files:**
- Create: `tools/build_v2.py` (CLI: `python -I tools/build_v2.py --src "../Pokemon Arena v1.8.w3x" --pkl "../PKLegendsv3.1b.w3x" --models mega_models --out "../Pokemon Arena v2.0.w3x"`)
- Create: `tests/test_build.py`

**Interfaces:**
- Consumes: Tasks 1–6.
- Produces: `build(src, pkl, models_dir, out) -> BuildReport(added: int, replaced: int, size: int, warnings: list[str])`. Also patches `war3map.w3i`: every `Pokemon Arena v1.8\0` → `Pokemon Arena v2.0\0`; description string `Release new ver when have 2000 times download` → `v2.0: Mega Evolution! Mua Mega Stone o Mega Shop.` (null-terminated string swap). Writes `(listfile)` with all known names. Prints the report.

- [ ] **Step 1: Write tests** (build once into tmp, module fixture):
  - `test_output_opens_and_v18_untouched`: output parses; sha256 of v1.8 file unchanged before/after.
  - `test_all_references_exist`: every `umdl`/`uico` of new units and every `Art` of new items/abilities resolves in the output archive (`.mdl` → `.mdx`), or is a game path for fallbacks that exists in v1.8.
  - `test_w3i_renamed`: output `war3map.w3i` contains `Pokemon Arena v2.0` and not `v1.8`.
  - `test_script_contains_module`: output `scripts\war3map.j` contains `call Mega_Init()`.
- [ ] **Step 2: Run** `python -I -m pytest tests/test_build.py -q` → FAIL.
- [ ] **Step 3: Implement** `tools/build_v2.py`.
- [ ] **Step 4: Run** `python -I -m pytest tests -q` → all PASS, then run the CLI → report shows 0 warnings except the 4 known fallbacks (#4, #13, #14, #15).

### Task 8: In-game verification

**Files:** none (verification only).

- [ ] **Step 1:** With the user's OK, launch `D:\Warcraft III Reforged\_retail_\x86_64\Warcraft III.exe -launch -loadfile "<path>\Pokemon Arena v2.0.w3x"`; then read `Documents\Warcraft III\Logs\War3Log.txt` for the map load lines and any script/JASS error. Expected: map loads into game, no script error.
- [ ] **Step 2:** Hand the user this check list: buy Charizardite X → Charizard shows "Mega Evolve" (D); cast → Mega Charizard X model/icon/name, +stats, back after 60 s; cooldown 150 s; hold X+Y → two buttons, one cast puts both on cooldown; drop/re-pick stone keeps cooldown; die while Mega → revives normal; Kangaskhan Kid follows and adds damage; type-restricted items still behave as in v1.8.
