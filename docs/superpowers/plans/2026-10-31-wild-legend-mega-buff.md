# Wild tiers, camps, legend lv 100, Mega buff — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the v2.0 build with a percentage-based Mega buff, 5-minute wild creep tiers, respawning camps with 30 new species, and level-100 legend bosses.

**Architecture:** Same pipeline (`tools/build_v2.py`). New data module `tools/wild_data.py` (species table, wild-type rule, camps from the v1.8 script); assets/objects/inject extended; JASS added to `tools/jass/mega.j` with `Wild_` prefix and run from the existing 0.25 s tick and death trigger.

**Tech Stack:** Python 3.11 + pytest, JASS (Reforged 1.36 natives incl. `BlzSetUnitMaxHP`, `BlzSetUnitBaseDamage`, `BlzSetUnitArmor`, `BlzGetUnitArmor`, `BlzSetUnitIntegerField`/`BlzGetUnitIntegerField` with `UNIT_IF_GOLD_BOUNTY_AWARDED_BASE`, `SetHeroStr/Agi/Int`).

**Spec:** `docs/superpowers/specs/2026-10-31-wild-legend-mega-buff-design.md`

## Global Constraints

- v1.8 and PKL maps are read-only; output `../Pokemon Arena v2.0.w3x` (built to `out/` first while the game locks the file).
- Hash table: 1024 slots, must stay below 1024 used (test).
- New IDs: wild species `nW00`–`nW1D`; JASS identifiers `Wild_*`; assets under `war3mapImported\Wild\`.
- Numbers: tier every 300 s, max 10, m = 1 + 0.15·t, armor +2·t; respawn 60 s, offset ≤ 150; Mega: attr % = points·3 (min = points), damage +50 % of (base + max attr), AMB1 +10 armor, AMB2 +80 MS, AMB3 +0.40 AS; legends ulev 100, HP ×1.5, dmg ×1.25, armor +20.
- Not a git repo: no commits; ledger in `.superpowers/sdd/2026-10-31-wild-legend-mega-buff/progress.md`.

## Review Focus

- A tier applied twice to the same creep must not stack → Task 4 `test_wild_apply_uses_stored_bases` (module computes from stored base values at keys 20–23, never from current values).
- Mega ending after a level-up or tome must remove exactly the bonus it added → Task 1 asserts stored-bonus subtraction in `Mega_End`.
- Camps containing gym/legend/Loc units must never respawn them → Task 2 `test_camps_only_wild_types`.
- Hash table overflow from 30 species → Task 4 `test_build_hash_capacity`.
- Legend list must not include gym bosses → Task 3 `test_legends_level_100`.

---

### Task 1: Mega buff

**Files:** Modify `tools/mega_data.py`, `tools/objects.py`, `tools/jass/mega.j`, `tests/test_objects.py`, `tests/test_inject.py`, `tests/test_mega_data.py`.

**Interfaces:** Produces `mega_data.BONUS_VALUES = {'AMB1': '10', 'AMB2': '80', 'AMB3': '0.40'}`, `mega_data.ATTR_PCT_PER_POINT = 3`, `mega_data.DAMAGE_BONUS = 0.5`; `Mega.attr_id` removed.

- [ ] Tests: `test_abilities_rows` expects AMB1 `10`, AMB2 `80`, AMB3 `0.40` and no `AMA0` row; `test_mega_buff_in_module` asserts `mega.j` contains `SetHeroStr(`, `SetHeroAgi(`, `SetHeroInt(`, `BlzSetUnitBaseDamage(` in both `Mega_Start` and `Mega_End`, and saves bonuses under hashtable keys 10–13; stone/ability tooltips contain `+50% damage`.
- [ ] Run `python -I -m pytest tests -q` → FAIL.
- [ ] Implement: data constants, drop AMAx rows/sections, data init `Mega_PStr/PAgi/PInt` arrays (points), JASS bonus apply/revert (keys 10 str, 11 agi, 12 int, 13 dmg).
- [ ] Run → PASS.

### Task 2: Wild data (types, species, camps)

**Files:** Create `tools/wild_data.py`, `tests/test_wild_data.py`.

**Interfaces:** Produces `SPECIES: list[Species]` (30; fields `index, id ('nW00'..), name, power 1–10, pkl_name, level, hp, dmg, armor, gold`), `wild_types(w3u_objs) -> list[str]` (rule from spec, plus `nogl`), `camps(script, w3u_objs) -> list[Camp(x, y, count, power)]`, `power_for_level(lv) -> int`.

- [ ] Tests: `test_species_table_matches_spec` (30 rows, powers 1..10 ×3, stats per spec table), `test_wild_types_rule` (contains n00I, n01R, n02G, n028, nogl; excludes n00R, n01E, n031, n032, n02H, n01O), `test_camps_only_wild_types` (every camp built only from wild-type CreateUnit calls; total units equals count of wild CreateUnit in init; Caterpie camp power 1, Tentacruel lv12 camp power 3), `test_power_for_level` (2→1, 6→2, 12→3, 75→10).
- [ ] Run `python -I -m pytest tests/test_wild_data.py -q` → FAIL.
- [ ] Implement.
- [ ] Run → PASS.

### Task 3: Wild assets + object data + legends

**Files:** Modify `tools/assets.py` (add `collect_wild(pkl) -> WildAssets(files, model_path, icon_path, scale)`), `tools/objects.py` (wild units cloned from `n00T` with spec stats, melee `ua1w='normal'`, `ua1r=100`; legend edits), tests in `tests/test_assets.py`, `tests/test_objects.py`.

- [ ] Tests: `test_wild_assets_namespaced` (all model texture paths under `war3mapImported\Wild\`, no v1.8 overwrite, 30 models + 30 icons), `test_wild_units` (nW00…nW1D exist with spec stats, umdl/uico resolve), `test_legends_level_100` (the 16 ids have ulev 100, HP ×1.5, dmg ×1.25, armor +20 vs v1.8; n00R/n01E unchanged).
- [ ] Run → FAIL. Implement. Run → PASS.

### Task 4: Wild JASS module + build

**Files:** Modify `tools/jass/mega.j`, `tools/inject.py` (data init: `Wild_TypeN/Wild_Type[]`, `Wild_SpeciesN/Wild_Species[]/Wild_SpeciesPow[]`, `Wild_CampN/Wild_CampX/Y/Count/Pow[]`), `tools/jasscheck.py` (new natives/constants), `tools/build_v2.py`, tests `tests/test_inject.py`, `tests/test_build.py`.

**JASS API:** `Wild_IsWild(u) -> boolean`, `Wild_Apply(u)` (stores base HP/dmg/armor/bounty at keys 20–23 on first sight, applies current tier, key 24 = applied tier), `Wild_Scan()` (every 2 s), `Wild_TierUp()` (every 300 s), `Wild_RegisterCamps()` (init: nearest camp per pre-placed wild unit, key 25 = camp+1), `Wild_OnDeath(u)` (camp count−1 → due time +60), `Wild_SpawnCamp(i)` (species by power, register, apply).

- [ ] Tests: module passes `jasscheck`; data init contains `set Wild_Species[0] = 'nW00'`, camp arrays; build test `test_build_hash_capacity` (used slots < 1024) and wild models present.
- [ ] Run → FAIL. Implement. Run full suite → PASS. Build to `out/`, copy to `../Pokemon Arena v2.0.w3x` when unlocked.

### Task 5: In-game check (user)

- [ ] User checks: Mega clearly stronger; "Wild Pokemon grew stronger! (Tier 1)" at 5:00; a cleared camp respawns a different species after 60 s; legend shows lv 100; evolution makes one Pokemon; revive after 10 s.
