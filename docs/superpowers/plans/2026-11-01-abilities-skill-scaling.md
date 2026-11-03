# Abilities and skill scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Pokemon Arena v2.8: an Ability per Pokemon/Mega and skill damage that scales with the hero's main attribute.

**Architecture:** `tools/ability_data.py` holds the data; `objects.py` writes the passive info abilities and item bonus abilities; `inject.py` generates `Ab_InitData`; `tools/jass/mega.j` gets `Ab_*` functions and one damage trigger; `build_v2.py` ties it together.

**Tech Stack:** Python 3 + pytest, JASS (WC3 Reforged 1.36), existing tools in `tools/`.

**Spec:** `docs/superpowers/specs/2026-11-01-abilities-skill-scaling-design.md`

## Global Constraints
- Run everything from `_PokemonArena2.0_work` with `python -I`; tests: `python -I -m pytest tests -q` (128 pass before this plan).
- New version file `tools/version.txt` = `2.8`, output `../Pokemon Arena v2.8.w3x`; old files stay.
- Ability ids: info passives `AB` + two base-36 chars (`AB00`...), bonus abilities `AXA4 AXA6 AXS4 AXS7`.
- Hashtable `Ab_HT` for all Ability state; Mega_Time is the clock. No ReplaceUnit calls.
- Write code with backslashes using Write/Edit tools, not heredocs.

## Review Focus
- A hero whose type has no Ability (the 9 v2.3 lines, wild creeps, legends) must not error or get an info button.
- Ability effects must never re-trigger themselves (damage dealt by an Ability is ignored by `Ab_OnDamaging`).
- Damage to allies, to self and zero damage must pass through unchanged.
- Mega start/end and evolution must swap the Ability within a second without leaving stale bonus abilities.
- The v1.8 script must still pass the checker blocks (`//MEGA_*`) with zero errors.

---

### Task 1: Ability data
**Files:** Create `tools/ability_data.py`; Test `tests/test_ability_data.py`.
**Interfaces:** Produces `Effect(fam, x, y, z, w, s, raw)`, `Ability(name, effects, text, icon)`, `ABILITIES` (ordered list, index+1 = JASS id), `FAMILY` (name → int), `RAW_ABILITIES` (`{'AXA4': ('AIde', 4), 'AXA6': ('AIde', 6), 'AXS4': ('AIms', 40), 'AXS7': ('AIms', 70)}`), `info_id(i)`, `species_abilities()` (`{pokemon name: ability name}`), `mega_abilities()` (`{Mega name: ability name}`), `type_abilities(w3u)` (`{unit type id: ability index}`), `mega_ability_index()` (`{mega.index: ability index}`).
- [ ] Tests: every Ability has 1-2 effects and non-empty text; `info_id(0) == 'AB00'`; all 137 v1.8 heroes except the 21 v2.3 forms get an ability in `type_abilities(w3u)` (V18 map); all 25 Megas covered; every `Effect.raw` is a key of `RAW_ABILITIES`; family names unique.
- [ ] Implement the module from `analysis/ability_list.py` (same abilities, with the spec's numbers).
- [ ] Run `python -I -m pytest tests/test_ability_data.py -q` → pass.

### Task 2: Objects
**Files:** Modify `tools/objects.py` (`_abilities`, `_poke_skill` tooltip); Test `tests/test_ability_objects.py`.
**Interfaces:** Consumes Task 1. Produces rows/text in AbilityData.slk and CampaignAbilityStrings.txt for every `info_id(i)` and the four `RAW_ABILITIES`; info buttons at `Buttonpos=3,1`, Name `Ability: <name>`.
- [ ] Tests: built ability SLK contains all ids; info rows are passive (code `AEev`, hero 0, DataA1 0); bonus rows use `AIde`/`AIms` with the Data values; txt sections have `Buttonpos=3,1` and the effect text; new skill Ubertip of a damage template ends with the scaling line, BUFF/EVADE/CRIT/BASH ones do not.
- [ ] Implement `_ability_objects(s, strings, a)` and call it from `_abilities` when `a.abilities` is set; extend `_poke_skill`.
- [ ] Run the test file and `tests/test_poke_objects.py` → pass.

### Task 3: Data generation and checker
**Files:** Modify `tools/inject.py` (`gen_ab_init(abil)`, `gen_data_init`, `module_source`, `inject`), `tools/jasscheck.py`; Test `tests/test_inject.py`.
**Interfaces:** Produces `abil` dict `{'abilities': ABILITIES, 'types': {type id: index}, 'megas': {mega index: index}}`; JASS `Ab_InitData` sets `Ab_N`, `Ab_Name[a]`, `Ab_Info[a]`, per effect `e = a*2+k`: `Ab_Fam[e] Ab_X[e] Ab_Y[e] Ab_Z[e] Ab_W[e] Ab_S[e] Ab_Raw[e]`, `Ab_MegaAb[megaIdx]`, and `call SaveInteger(Ab_HT, '<type>', 0, a)`.
- [ ] Tests: `gen_ab_init(None)` is a function with `Ab_N = 0`; with data it contains the expected lines for Blaze (`Ab_Fam`, `SaveInteger(Ab_HT, 'E003', 0, ...)`); checker accepts new natives (`GetEventDamage`, `BlzGetEventDamageType`, `IsUnitEnemy`, `PauseUnit`, `GetUnitMoveSpeed`, `SetUnitMoveSpeed`, `SubString`, `GroupEnumUnitsInRange`, `SetUnitState`, `GetUnitState`, `SetWidgetLife`, ...).
- [ ] Implement; extend NATIVES/KNOWN_GLOBALS.
- [ ] Run `tests/test_inject.py tests/test_jasscheck.py` → pass.

### Task 4: JASS module
**Files:** Modify `tools/jass/mega.j`; Test `tests/test_abilities_module.py`, update `tests/test_legends.py`.
**Interfaces:** Consumes Task 3 arrays. Produces `Ab_OnDamaging` (condition of the single `EVENT_PLAYER_UNIT_DAMAGING` trigger, calls `Leg_OnDamage` first), `Ab_SkillMult(real stat)`, `Ab_Sync(unit)`, `Ab_Tick` (0.5s timer, every 2nd tick = beat), `Ab_OnRevive`.
- [ ] Tests (string level on `module_source`): checker passes; constants `Ab_ScaleK = 0.011`, `Ab_ScaleBase = 50.0`, `Ab_ScaleMax = 10.0`; `Ab_OnDamaging` skips when `Ab_Busy`, uses `BlzGetEventDamageType() != DAMAGE_TYPE_NORMAL`, `IsUnitEnemy`, `Ab_SkillMult`; Ability families handled by code (`Ab_Fam[e] == 1` ... 18); `Mega_Init` registers one damaging trigger with `Ab_OnDamaging` and the 0.5s timer and the revive event; info ability added/removed in `Ab_Sync`.
- [ ] Implement the functions per the spec; keep every effect in its own small function (`Ab_Out`, `Ab_In`, `Ab_Slow`, `Ab_Stun`, `Ab_AddDot`, `Ab_Beat`).
- [ ] Run the new tests + whole suite → pass.

### Task 5: Build, verify, document
**Files:** Modify `tools/build_v2.py`, `tools/version.txt`, `CLAUDE.md`, `docs/pokemon-abilities-proposal.md` generator; Test `tests/test_build.py`.
- [ ] Test: built map has `AB00` and `AXA4` in AbilityData.slk, `call Ab_InitData` data lines and `Ab_OnDamaging` in the script, injected blocks pass `jasscheck`.
- [ ] Wire `a.abilities`/`abil` into the build; set version 2.8; run full suite; build `../Pokemon Arena v2.8.w3x`; verify name, readable files, checker on `//MEGA_*` blocks.
- [ ] Update CLAUDE.md, the memory notes and the proposal text (Slow Start / Synchronize deviations).
