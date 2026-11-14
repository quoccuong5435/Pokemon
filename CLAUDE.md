# Pokemon Arena v2.x mod — handoff for a new Claude session

## READ FIRST (2026-11-14, branch `v3.4.10`): the game now continues from `..\Pokemon Arena v3.4.10.w3x`
- v3.4.10 was made by another account from 3.4.0 (its source was never pushed). v3.4.11+ is built here FROM THAT MAP:
  `tools/v3411/apply.py` (patches the 3.4.10 script, generates data) -> `python -I tools/v34/check.py v3411/war3map.j`
  (pjass 0 errors) -> `tools/v3411/build.py [--dry-run]` (object data; never overwrites). Version: `tools/v3411/version.txt`.
- New JASS: `tools/v3411/jass/fx_globals.j`, `fx_core.j` (before Hero_HPSync), `fx_main.j` (before Ext_AfterHit).
  Status moves: `tools/v3411/status_moves.py` (move indices 320..377). Notes / changelog: `docs/v3.4.11/README.md`.
- Built: 3.4.11 .. 3.4.14 (none played yet; 3.4.14 fixes a permanent pause and a permanent slow). Next: 3.4.15. `v3411/` (generated script with v1.8 code) is not in git.
- JASS gotchas: `code` is a type keyword; 2-letter locals (pa, pb ...) collide with v1.8 functions.
- The sections below describe the older lineage (v3.4.0 .. v3.4.6 built from the v3.3.3 map).

## READ FIRST (2026-11-08): `HANDOFF-v3.4.md` = current state, user rules, pitfalls, open items (latest map v3.4.2)

## READ FIRST: v3.4 works from the v3.3.3 map, not from v1.8 (2026-11-07)
- Summary of everything in v3.4.x (versions, features, open items): `docs/v3.4/README.md`; all v3.4 docs live in `docs/v3.4/`.
- The source of v3.2.16 .. v3.3.3 was never saved here (`tools/version.txt` = 3.2.15, `tools/jass/mega.j` is older;
  its uncommitted `Wish_*` code was never built). The newest playable map is `..\Pokemon Arena v3.3.3.w3x`
  (`Pokemon Arena God Mode.w3x` = same script, other object data). So v3.4+ is made from that map:
  - `v34/war3map_v333.j` = its script, line breaks made LF (the v1.8 part uses bare CR as line breaks: never delete
    `\r`, turn it into `\n`). `v34/war3map.j` = the v3.4 script (generated, do not edit by hand).
  - `tools/v34/jass/*.j` = new / replaced JASS (globals, type chart, gyms, Abilities); `tools/v34/abilities.py` =
    Ability names / texts / the 21 Pokemon that had none; `tools/v34/apply.py` assembles the script and generates
    the data (AB_* / T_* constants, type chart, unit and move types, gym pool and gym evolutions).
  - After a fresh clone: `python -I tools/v34/extract_base.py` (v34/*.j are not in git: they hold the v1.8 code).
  - `python -I tools/v34/apply.py` -> `python -I tools/v34/check.py` (pjass, must say 0 errors) ->
    `python -I tools/v34/build_v34.py --dry-run` -> `python -I tools/v34/build_v34.py` (only when the user says so;
    version in `tools/v34/version.txt`, never overwrites a map).
- v3.4.0 content (not built yet, not played): gyms (team chosen at the start: 6 lines, form of its level, the 6th
  counters the challenger; full HP/mana on entry; only the clearing player waits 5s; no wait after a loss), players'
  attack speed x1.7 (`Hero_ASBoost`), wild HP from the v3.2.15 power table x tier step, type chart on moves (x2 /
  x0.5 / immune x0.25, clamp 0.25..2), 73 Abilities (68 reworked + 5 new; spec: `docs/v3.4/1-ability.md`).
- Gym Pokemon are now the playable hero types owned by Neutral Aggressive (wild pool lacks most lines); the v1.8
  "Kill Hero" trigger (`bS4`) skips neutral heroes. Their corpses are removed by `Gym_Tick`.
- 5 Megas have no Mega model anywhere on this PC (Beedrill, Kangaskhan, Mewtwo X/Y, Rayquaza; their skin unit uses
  the base model). `tools/v34/mega_look.py`: a file `mega_models/<MegaBeedrill|MegaKangaskhan|MegaMewtwoX|MegaMewtwoY|
  MegaRayquaza>.mdx` (+ textures, optional `_portrait.mdx`) is imported by build_v34; without one the Mega is 40%
  bigger, coloured and gets an aura. Mega_Start also tells the owner the Mega Ability (v3.4).
- v3.4 content (approved, coded, not built): `tools/v34/content.py` makes the units / items / abilities / PKL v3.2
  imports of `docs/v3.4/2-mega-form-quai-hoang.md` (8 Megas hM0P.., Meganium/Porygon2/Latias & Latios PV0A..PV2A,
  legend nL18, Zen skin hZ00, 211 wild creeps nX00.. with Souls IU00..); apply.py gets its JASS data (V34_Data1..3,
  ExecuteFunc), build_v34.py writes it. Wild_PickType uses a per-power index (Wild_IndexPool).
- Gym team levels are now challenger -5..-1 and = (v3.3: -30..-10). `jass/ai.j`: elites, gym Pokemon and legends
  cast their kit skills (the creep AI never casts hero skills; Ab_HT key 86 target, 87 kit, 58 order of a skill).
- BUILT 2026-11-07: `Pokemon Arena v3.4.0.w3x` (105 MB) with everything above plus the approved
  `docs/v3.4/3-item-league-tinh-nang.md` (folded into 3.4.0): 21 items + Battle Shop / Item Shop (`extras.py`,
  `jass/extra.j`, `jass/extra_late.j`), Shiny, weather, stone evolutions, elite / legend Mega, creeps evolve with the
  tier (`Wild_NextForm`), Elite Four + Champion (`-league`, gym slot 8 in `jass/gym.j`; title +15% stats + aura),
  move icons (`move_icons.py`, `docs/v3.4/4-icon-chieu.md`). Not played yet. Next version: bump tools/v34/version.txt.
- 3.4.1 (code ready, not built): gym challenger that evolves mid-gym keeps the battle (Mega_SafeReplace retargets
  Gym_Hero / League_Unit and never replaces gym units, key 33), a vanished gym Pokemon is spawned again, others near
  a busy gym get a message; one learned move per game-skill kind (`jass/moves.j`, Mv_Kind: same base ability = same
  order, so the Q button cast the E move); Amulet Coin on its own death trigger.
- 3.4.2 (code ready, not built): gym team / each spawn in its own thread (ExecuteFunc Gym_StartIt / Gym_SpawnIt /
  Gym_AdvanceIt), fallback Pokemon for an empty slot, dead-but-unhandled and wandering gym Pokemon handled, `-gym`
  state command; Onix / Scyther may buy Metal Coat (Mega_HT key 92, Type_OnSell). Shops at fixed spots (+-5696, +-288: the shop rows
  are full; analysis/base_layout.py draws the base from war3map.wpm); Type_N 18 (I013 Ground, ITFY Fairy).
  League in Darkrai's closed room (`tools/v34/league_area.py`: w3e texture repaint in build_v34, positions, statues;
  League_Setup / League_PortalTick in gym.j; base portals +-5392,-288; Darkrai -> random legend nL19, Soul I01F).
  Gym difficulty per gym (Gym_DiffHP / Gym_DiffDmg / Gym_DiffAI / Gym_Fast, data in extras.py): gyms 1-4 easier. Waiting for approval:
  `docs/v3.4/6-de-xuat-hieu-ung-chieu.md` (melee moves, PKL v3.2 effect models; generator analysis/effects_plan.py).
- Heredocs in this shell turn `\\` into `\` even with a quoted EOF: write code with backslashes through the Write tool.
- JASS names: v1.8 has thousands of 2-3 letter function names (`p1`, `cc`, `sa` ...): never use short local names.
- Init op limit: Mega_Init already runs ~20k lines of data; new data functions run through `ExecuteFunc`.

The user (Vietnamese; reply in Vietnamese) upgrades the Warcraft III Reforged map "Pokemon Arena v1.8.w3x"
(author Dinh Hai Ha, untouched, never edit it) into v2.x. Game: WC3 Reforged 1.36.1 offline repack at
`D:\Warcraft III Reforged`. Everything is generated by Python from the v1.8 map; nothing is edited by hand in a map editor.

## Needed files (same folder tree, parent of this folder = `Maps\Download`)
- `..\Pokemon Arena v1.8.w3x` — source map. `..\PKLegendsv3.1b.w3x` — source of Pokemon models/icons.
- Outputs: `..\Pokemon Arena v2.0 … v3.1.w3x` (v2.2 does not exist). Keep every old file.
- Python 3 + pytest only. Run everything from this folder with `python -I`.

## Commands
- Tests (184 pass): `python -I -m pytest tests -q`
- Build (version comes from `tools/version.txt`, output `..\Pokemon Arena v<ver>.w3x`):
  `python -I tools/build_v2.py --src "../Pokemon Arena v1.8.w3x" --pkl "../PKLegendsv3.1b.w3x" --models mega_models`
- Every update gets a new 2.x number: edit `tools/version.txt` first, never overwrite an existing version file.
  If the map is open in the game the file is locked: build with `--out out\x.w3x`, copy after the game is closed.

## Layout
- `tools/mpq.py` MPQ reader/writer (sector-format blocks are REQUIRED, WC3 can't read SINGLE_UNIT; hash table 4096).
- `tools/objdata.py` w3u/w3a parser, `slk.py`, `mdx.py` model helpers.
- Data: `mega_data.py` (25 Megas), `poke_data.py` (21 new Pokemon, 9 skill kits), `skill_data.py` (v3.0: 117 old
  Pokemon -> kit by main type, 11 new kits `AQ..`), `wild_data.py` (30 wild species,
  tiers, own-species Souls), `legend_data.py` (14 random legends).
- `tools/objects.py` writes units/items/abilities; `assets.py` imports models; `inject.py` generates JASS data and injects
  `tools/jass/mega.j` into `war3map.j`; `jasscheck.py` is a custom JASS checker; `build_v2.py` ties it together.
- `tests/` (TDD), `docs/superpowers/specs|plans/`, `.superpowers/sdd/<name>/progress.md` ledgers, `analysis/` one-off scripts.
- Full-script `jasscheck` reports thousands of false errors from the v1.8 script; check only the `//MEGA_*` blocks.

## Gotchas
- Bash heredocs collapse `\\` to `\`: write code containing backslashes with the Write/Edit tools, not `python - <<EOF`.
- The map script is handled as latin-1 text; `inject._split_module` re-encodes mega.j so non-ASCII chat commands
  ("t là gà") stay UTF-8 bytes.
- Hero ids must start with an uppercase letter. v1.8 has ~449 custom units; new ids: `EN00..EN0K`, `nW00..nW1D`,
  `nL00..nL0D`, `IS00..IS1B`, `hM0x/IM0x/AM0x`.
- The game can't be driven automatically: in-game tests are done by the user (Play Offline → Custom Game).
- The user wants updates built as a new 2.x file each time and reports bugs after playing.

## Version history
2.0 Mega Evolution (16) · 2.1 fixes (room creation, evolve = 2 units, revive 10s, stronger Mega, wild upgrades,
legend lv100, `-random`) · 2.3 +21 Pokemon / 8 lines with Megas, tier every 10 min · 2.4 wild level follows players,
`-repick` (2x, first 2 min) · 2.5 random legends every 5 min (lv100 only can hurt them, 50% Soul) · 2.6 wild creeps drop
their own species' Soul (0.5%), tier from the 2 lowest players (every 10 min; v2.7 back to 5 min), Mega shops moved out of the base door,
chat "t là gà"/"chicken" (+10 lv, +3000 gold, once) · 2.7 wild tier check every 5 min · 2.8 Pokemon Abilities (68,
info button at command card 3,1, one damage trigger `Ab_OnDamaging`) + skill damage x(1 + 0.02 (main stat - 50)), max x10 · 3.0 host-only
`-random`/chicken, kits by type for 117 old Pokemon · 3.1 learned moves (4 slots Z X C V, Pokemon-style replace dialog).

## Status / next step
**Current state: `HANDOFF-v3.4.md` (v3.4.x).** The section below and `HANDOFF.md` describe the old v2.x / v3.1 pipeline.
- Latest built map: v3.1 (v3.0 + learned moves, `tools/version.txt` = 3.1). Tests: 184 pass. Not played yet by the user.
- Learned moves: `tools/learn_data.py`, spec `docs/superpowers/specs/2026-11-01-learned-moves-design.md`, table
  `docs/pokemon-learned-moves-proposal.md`; data `tools/learnsets.json` from PokeAPI (`analysis/fetch_pokeapi.py`).
- JASS pitfall: use only natives that exist in common.j (not `UnitAlive`; use `GetWidgetLife(u) > 0.405`). Check a built map with
  `python -I analysis/pjass_map.py <map.w3x>` (real pjass); any error means the lobby will say "unavailable or corrupted".
- Next big item (needs the user's decisions first): the 120 PKLegends species as playable heroes + wild creeps.
