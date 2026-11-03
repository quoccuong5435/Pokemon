# New Pokemon (8 lines) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Pokemon Arena v2.2 with 21 new playable Pokemon (8 lines), 45 data-only skills, level/item evolution, 9 new Megas, tavern 5, Mega Shop III and an enlarged MPQ hash table.

**Architecture:** New data module `tools/poke_data.py` (forms, kits, skill templates); `mega_data.MEGAS` grows to 25; `assets.collect_poke` imports models; `objects.apply` adds heroes/skills/tavern/shop III; JASS `Evo_*` added to `tools/jass/mega.j`; `mpq.save_with(hash_size=4096)` relocates entries (named by name, unknown via candidate-home duplication).

**Tech Stack:** Python 3.11 + pytest; JASS (Reforged 1.36).

**Spec:** `docs/superpowers/specs/2026-11-01-new-pokemon-design.md`

## Global Constraints

- IDs: heroes `EN00`–`EN0K`, skills `AP00`–`AP18` (base36), Mega `hM0G`–`hM0O`/`IM0G`–`IM0O`/`AM0G`–`AM0O`, tavern `nTV5`, shop `nMS3`; all must be unused in v1.8 (test).
- Skill slots: reqLevel 3/6/10/33/36, levels 3, levelSkip 10, buttons Q 0,2 · W 1,2 · E 2,2 · passive 3,2 · R 2,1.
- 5 skills of one kit have 5 distinct base codes.
- New hero `uabi` = `AInv`; scale = template usca × template model height / new model height (0.2–6).
- Version file bumped to `2.2`; output `../Pokemon Arena v2.2.w3x`; older files untouched.
- Not a git repo: no commits; ledger `.superpowers/sdd/2026-11-01-new-pokemon/progress.md`.

## Review Focus

- An unknown-named file must stay reachable after the hash table grows → Task 1 `test_unknown_entries_reachable_from_every_candidate_home`.
- Two skills of a kit sharing an order would break casting → Task 2 `test_kits_have_distinct_codes`.
- Mega of a new Pokemon needs the new hero object to exist before its skin clone → Task 4 `test_new_mega_skins_clone_new_heroes`.
- Kirlia with Sun Stone must not also level-evolve twice into two units → guarded by `Mega_SafeReplace` (Task 5 asserts Evo uses it).
- Random must include new starters → Task 5 `test_random_pool_includes_new_starters`.

---

### Task 1: MPQ hash table growth
**Files:** `tools/mpq.py` (move name discovery from `tools/extract.py` into `discover_names(archive) -> set[str]`; `save_with(..., hash_size=None)`), `tests/test_formats.py`.
- [ ] Tests: `test_save_with_bigger_hash_table_reads_all_known` (hash_size 4096: every discovered name reads identical, header count 4096), `test_unknown_entries_reachable_from_every_candidate_home` (for each original unknown entry, from every candidate home in the new table a forward probe meets its hashA/hashB before an empty slot), `test_add_300_files_with_bigger_table`.
- [ ] Run → FAIL; implement; run → PASS.

### Task 2: Pokemon data
**Files:** create `tools/poke_data.py`, `tests/test_poke_data.py`; modify `tools/mega_data.py` (+9 Megas, base36 ids, `MEGA_SHOP3_ID='nMS3'`), `tests/test_mega_data.py`.
**Produces:** `FORMS` (21: id, name, template, evolves_to, level, item, kit), `KITS` (9 × 5 `Skill(id, name, template, slot, element, icon)`), `TEMPLATES` (17: code, per-level values), `STARTERS`, `TAVERN_ID='nTV5'`, `TAVERN_POS`.
- [ ] Tests: forms/evolutions match spec table; `test_kits_have_distinct_codes`; skill ids AP00–AP18 unique; template numbers match spec table; 25 Megas, new ids base36, orders unique and unused by v1.8.
- [ ] Run → FAIL; implement; run → PASS.

### Task 3: Assets for new Pokemon and Megas
**Files:** `tools/assets.py` (`collect_poke(pkl, base) -> PokeAssets(files, model_path, icon_path, scale, model_height)`; `collect(..., poke=None)` uses poke heights/scales for Mega bases not in v1.8; PKL model lookup also at archive root), `tests/test_assets.py`.
- [ ] Tests: 21 models + BTN + DISBTN under `war3mapImported\Poke\` / CommandButtons, textures namespaced, no v1.8 overwrite; scale formula; all 25 Megas resolve (9 new from PKL incl. root `MegaGallade.mdx`).
- [ ] Run → FAIL; implement; run → PASS.

### Task 4: Object data
**Files:** `tools/objects.py` (heroes cloned from templates; 45 skill rows + strings; tavern `nTV5`; shop `nMS3`; stones/abilities/skins for Megas 16–24 after heroes exist), `tests/test_objects.py`.
- [ ] Tests: 21 heroes with uhab = kit ids, uabi `AInv`, names/tooltips; each skill row levels 3, reqLevel per slot, template numbers per level, strings with 3-level Tip/Ubertip and button positions; tavern sells 8 starters; shop III sells IM0G–IM0O; `test_new_mega_skins_clone_new_heroes`.
- [ ] Run → FAIL; implement; run → PASS.

### Task 5: JASS evolution + wiring + build v2.2
**Files:** `tools/jass/mega.j` (`Evo_OnLevel`, `Evo_OnPickup`, tavern + shop III creation, `Mega_N` from data), `tools/inject.py` (Evo data init, Mega_N), `tools/build_v2.py` (poke assets, rand pool + starters, hash_size 4096), `tools/version.txt` → `2.2`, tests `tests/test_inject.py`, `tests/test_build.py`, `tests/test_random.py`.
- [ ] Tests: module passes `jasscheck`; data init has `set Evo_From[0] = 'EN00'` … and `set Mega_N = 25`; Evo uses `Mega_SafeReplace`; `test_random_pool_includes_new_starters`; build v2.2 opens, hash table 4096, new heroes/skills/models present, every referenced art file exists.
- [ ] Run → FAIL; implement; run → PASS; build `../Pokemon Arena v2.2.w3x`.

### Task 6: In-game check (user)
- [ ] Tavern 5 sells 8 Pokemon; Torchic → Combusken at 16; Kirlia + Sun Stone → Gallade; skills learnable at 3/6/10/33/36 and castable; new Megas; `-random` can give new Pokemon.
