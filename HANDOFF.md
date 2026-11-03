# HANDOFF — read this first (updated end of session, Nov 2026)

Read `CLAUDE.md` (rules, commands, layout, version history), then this file. The user is Vietnamese: **reply in Vietnamese, short**.
Folder: `C:\Users\quocc\OneDrive\Documents\Warcraft III\Maps\Download\_PokemonArena2.0_work` (parent `Maps\Download` holds the maps).
Not a git repo. Run Python as `python -I`. The user tests in the game (offline custom game); Claude cannot run Warcraft III.

## How the user wants to work (read this carefully)
- **Do not build repeatedly.** Gather the changes, run tests, then build ONCE when the user says "build". The user complained that
  rebuilding burns tokens. Build to `out\x.w3x` (the map may be locked by the game).
- `tools/version.txt` changes only when the user says so. It is `3.1` now.
- Never delete the user's files without looking at them first and getting an OK. Move old builds aside (e.g. `..\_old_3.1\`).
- For big designs: list options, let the user choose (they did for Abilities, skill scaling, learned moves, Mega-on-item).
- Answer style: short bullets, what is done / not done, one question at the end.

## Environment checks
- Tests: `python -I -m pytest tests -q` -> **184 passed** (last run).
- **Never use `UnitAlive` in the script**: it is not a WC3 native (pjass: "Undeclared function"). Use `GetWidgetLife(u) > 0.405`.
  `tools/jasscheck.py` no longer lists it, so the checker catches it.
- **Real compiler check after every JASS change: `python -I analysis/pjass_map.py <map.w3x>`** (pjass in `D:\Warcraft III Reforged\...`).
  A JASS error shows in the lobby as "The map is unavailable or corrupted". `tools/jasscheck.py` is only a name/arg checker and misses
  missing natives. The last pjass run was on `out\Pokemon_Arena_v3.1_stone.w3x` (passed). The JASS changes listed below came after it,
  so **run pjass on the next build**.
- Build: `python -I tools/build_v2.py --src "../Pokemon Arena v1.8.w3x" --pkl "../PKLegendsv3.1b.w3x" --models mega_models --out out/<name>.w3x`.

## Files in `Maps\Download` (after the user's clean-up)
- `Pokemon Arena v1.8.w3x` (source, never edit), `PKLegendsv3.1b.w3x` (model source), `Pokemon Arena v2.0` … `v2.7` (play),
  `Pokemon Arena v2.8.w3x` (lobby error, untouched), `Pokemon Arena v3.1.w3x` (FIRST v3.1 build, before the later changes).
- The user cleared all other 3.x maps on request. Nothing new has been copied into `Maps\Download` since.
- Newest build in `_PokemonArena2.0_work\out\`: `Pokemon_Arena_v3.1_stone.w3x` (pjass ok). Not yet tested by the user.

## Lobby error history (important)
- v2.8 and v3.0 (both with Ability JASS) show "unavailable or corrupted" in the game. v2.7 works.
- Bisect builds (user tested): **D = v3.0 with no Ability code at all -> works**. A (Ability functions present but not called) -> fails.
  B (Ability JASS kept, Ability data removed) -> fails. F (only the `Ab_*` globals kept, functions removed) -> built, NOT tested.
  So the cause is in the Ability JASS (globals or functions), not in the data.
  Bisect scripts: `analysis/bisect_v30.py` (modes A, B, D) and `analysis/bisect_v30_F.py`.
  **Next step if the lobby error is still there:** test F. If F fails, bisect the globals; if F works, bisect the functions.
- pjass parses the current build, so the earlier note that `UnitAlive` is the only cause is not proven.

## Current design (what the code does now)
- **Hero skills**: heroes have NO fixed kit any more (`uhab` is empty for the 117 v1.8 Pokemon and the 21 v2.3 forms, see
  `objects._units` and `objects._poke_heroes`). Their moves come only from the learned-move system below.
  `tools/skill_data.py` still holds the kits: wild elite creeps use them (`Wild_KitSkill`, species -> type in `wild_data.SPECIES_TYPE`).
- **Command card of a Pokemon**: row 0 = 4 move slots (hotkeys Z X C V; ability ids `A` + `V/W/Y/Z` + 2 base-36 digits);
  cell 3,1 = the one Ability info button (`AB..`). Mega is NOT on the card: the Mega Stone item carries the Mega ability
  (`objects._items`: `abilList` = evolve id, ability item flag 1), the 150 s cooldown is shown on the item.
- **Learned moves** (`tools/learn_data.py`, `Mv_*` in `mega.j`):
  - 4 slots. The first 4 candidates are known from hero level 1; the others at their real learn level (min 2).
  - Empty slot -> learned at once. Full -> a stronger candidate replaces the WEAKEST known move at once (`Mv_WeakSlot`). No dialog.
  - A candidate whose name equals a kit skill name is skipped (`learn_data.kit_names`).
  - Candidate pool = best 8 damaging moves by power x accuracy (`CAND_MAX` = 8, `SLOTS` = 4).
  - Moves survive evolution/Mega (`Mega_SafeReplace` copies keys 40..43 and `200 + move`).
- **Abilities** (68, `tools/ability_data.py`): one Ability per Pokemon line / Mega, info button at 3,1. Effects in `Ab_*`
  (damage trigger `Ab_OnDamaging`, timer `Ab_Tick` every 0.5 s, state in `Ab_HT`). Mega Adaptability / Technician / Inner Focus keep "Mega" in the name.
- **Skill damage scale**: `min(10, 1 + 0.02 * max(0, mainStat - 50))` (`Ab_SkillMult`); it was 0.011 before the last balance pass.
- **Wild creeps**: tier = average level of the 2 lowest players / 10; tier step +8% HP/damage/gold; armor +1 per tier (max +10);
  HP table at 70% of the old one (`wild_data.POWER_STATS`). Respawn 15 s (`RESPAWN_SECONDS`); camp size x2 (`CAMP_SIZE_MULT`).
  One ELITE per camp (`Wild_MakeElite`): HP x2, damage x1.4, armor +3, gold x3, scale 1.15, gold colour, its type's 5 skills.
  Soul drop only from elites, 10% (`Wild_SoulChance = 10.0`). A tier change updates stats only (the form does not change yet).
- **Legends** (14 random ones in `legend_data.py`, v1.8 boss units in `objects._legends`): HP x0.5, damage x0.8, armor max 35;
  level 100 required to damage them (`Leg_OnDamage`). Spawn every 300 s, 2 per spawn, no cap (`Leg_Max = 99`).
- **Map**: fog off for everybody (`FogEnable(false)`, `FogMaskEnable(false)`). The boss room is NOT excluded yet.
- **Host commands**: `-random` and `chicken` are typed by the host (lowest playing slot, `Host_Id`) and apply to everybody
  (chicken once per player).
- **Evolution / tavern**: experience is kept when a Pokemon is replaced or bought at a tavern (`Mega_SafeReplace`, `Keep_XP`).
  Slow Start keeps its born time when a Pokemon evolves.

## Learnsets (data)
- `tools/learnsets.json` from PokeAPI (253 species, 456 moves). Rebuild: `analysis/fetch_pokeapi.py` (cache `analysis/pokeapi_cache/`).
- The old Serebii batch files (`analysis/batch_serebii_*`, `merge_learnsets.py`) are obsolete; pokemondb summaries were unreliable.
- Suspicious learnsets to re-check: Ivysaur (same as Venusaur in the old data), Machop/Machoke, Kadabra/Alakazam (identical in old data).

## Open items (NOT done; the user has not decided or it is not started)
1. **Ability effects the user says are wrong**: waiting for the user to name the Ability and what happens in game.
2. **Elite "teo mini" bug** (elites look shrunk): no repro yet. Ask which elite and when (spawn or after tier change).
3. **Salamence (playable) basic attacks too weak**: proposal = x1.5 damage on basic attacks of playable Pokemon; not chosen yet.
4. **Skill 1 of Salamence (dragon area skill) hits the whole camp**: check the skill's target flags.
5. **Elite and legend Mega**: not done (Mega only works on hero units; design needed). The user wants elites/legends to Mega and use skills.
   Legend skills: the v1.8 boss units keep their own original abilities (not checked in game).
6. **Creeps change form with tier** (replace the unit with the next species): not done; needs ReplaceUnit + camp bookkeeping (key 25 on the unit handle).
7. **Learned-move damage = power x main stat / 20** (user's idea): pending decision on keeping the status effects (stun, slow, burn).
8. **Armor vs damage type of skills**: not checked (which skill damage types ignore armor).
9. **Move icons do not match the names** (user screenshot): needs icon mapping.
10. **Debug chat commands**: `-stats` is BUILT (`Dbg_Stats` in mega.j: hero level, main stat, skill damage %, HP, armor, wild tier). `-spawn <tier>` not built.
11. **Boss room without fog**: not excluded.
12. **Multiscale "lost" when hit**: this is the effect design (works only at full HP); the user has not decided.
13. **Remove leftover v1.8 skill triggers and data**: proposed, not done (no hero uses them now).
14. **120 PKLegends species as playable Pokemon + wild creeps** (v2.3 pipeline is the model). Open questions for the user: which species/stages,
    where the extra taverns go (a tavern sells at most ~11), how stats map from base stats, which become wild creeps, Ability per species.
    'Heimsuchung' and 'Maschinedramon' in PKL are not Pokemon (skip).
15. Models and moves: PKL already has 296 species with models (about 64 used). Extra model sites were discussed; nothing downloaded
    (downloads need the user's OK).

## Pitfalls already met
- Bash heredocs collapse backslashes and some quotes: write code with backslashes through the Write/Edit tools or a file script.
- `mega.j` has CRLF in places: patch carefully. Several tests read exact strings from the module source; update them with the code.
- A local variable with the name of a v1.8 function fails in pjass (we renamed them). Only natives present in `analysis/jass_ref/common.j`.
- Files locked by the game ("Device or resource busy"): build to `out\`, copy after the game is closed.
- Some test files were edited on disk by other sessions: re-read before patching them.
