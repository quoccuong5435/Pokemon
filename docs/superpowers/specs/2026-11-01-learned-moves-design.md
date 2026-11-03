# Learned moves by level (design)

Requests (user, 2026-11-01): each Pokemon learns its real moves by level (data from the real games); learned moves go in
**4 new slots, the 5 kit skills stay** (user's answer); then "can it be like choosing to replace the old move" (Pokemon style).
Data: `tools/learnsets.json` (PokeAPI, 253 species, 456 moves). Proposal table: `docs/pokemon-learned-moves-proposal.md`
(milestone version; superseded by the rules below, regenerate it from `learn_data` when the code exists).

## Rules
- Candidates of a species: its damaging level-up moves (power > 0), the best 8 by score = power x accuracy/100 (accuracy 0 =
  never misses = 100). A candidate becomes available at hero level `max(10 + 8k, real learn level)` for the k-th candidate (sorted by that level), so the moves come one after another.
- 4 slots on command card row 0 (cells 0,0 1,0 2,0 3,0, hotkeys Z X C V). A move is a normal single-level ability; because a
  button position is fixed per ability id, every move exists once per slot: id = `A` + `VWYZ[slot]` + two base-36 digits of the
  global move index (`learn_data.ability_id`, `Mv_Id` in JASS).
- When a candidate becomes available: empty slot -> learned at once (message). All 4 slots full -> only offered if its score is
  higher than the weakest slot's score and it is not already known; the offer is a dialog ("<Pokemon> wants to learn <Move>
  (<Type>, power N). Forget which move?": buttons "Forget <move>" x4 + "Do not learn"), shown to the owner only when the hero
  was not hit for 10 s and the player has no open dialog (otherwise it waits). Each candidate is offered at most once.
- Moves stay in the hero when it evolves (`Mega_SafeReplace` copies the Ab_HT keys 40..43 and the 200 + move flags to the replacing unit) and with Mega.
- Template of a move: physical/special x power band (<=60, <=90, <=115, more): DAGGER/CHAIN, BOLT/WAVE, LINE/NOVA,
  ULT_STOMP/ULT_WAVE. Level column (1..3) of the template by the move's place in its band. Damage is scaled by the main stat
  like every skill (`Ab_SkillMult`). Missile art by move type (`poke_data.ELEMENT_ART`).
- State per hero in `Ab_HT` (parent = handle id): 40..43 slot s holds move index + 1, 200 + move index = 1 once the move was considered (learned, known, not stronger than the weakest, or offered).
- Species with fewer than 4 damaging moves simply have free slots. Wild creeps do not learn moves.

## Not in this feature
The 120 PKLegends species, per-move status effects, Mega changes. Version stays 3.0 until the user says otherwise.
