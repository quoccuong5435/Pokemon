# v2.6 — own-species Souls, team-level tier, shops outside the door, "t là gà"

## Requests (user, 2026-11-01)
1. Wild creeps drop only the Soul of their own species (0.5%).
2. Wild tier re-evaluated every 10 min from the average level of the 2 lowest players.
3. Mega shops were blocking the base doorway — move them outside.
4. Chat command "t là gà" (= "tôi là gà" = "chicken"): +10 levels, +3000 gold.

## Decisions
- Souls: one per wild species that has a playable version (v1.8 heroes by `upro`, plus the new Pokemon forms).
  29 Souls: 28 new items IS00–IS1B (cloned from I01C) and Magikarp's existing I01O.
  Species with no playable version drop nothing. Drop table: `SaveInteger(Mega_HT, <wild type>, 8, <soul>)`.
  New Souls transform in the centre circle (rect `Hi`): item in slot 1 → `Mega_SafeReplace`. Random-legend Soul drops are unchanged (50%); the old "any legend Soul" wild drop is removed.
- Tier: `Wild_LevelCheck = 600`. Each player's highest hero level is taken; the average of the 2 lowest becomes `Wild_AvgLevel` (one player alone → their level). Tier = level / 10.
- Shops (from the rendered pathing map, door gap at y≈0 on the side facing the centre):
  west I (−4416, 640), II (−4416, −640), III (−4416, 1088); east mirrored (4416, −640), (4416, 640), (4416, −1088).
- Chicken: once per player. Commands "t là gà", "tôi là gà", "t la ga", "toi la ga", "chicken", "-chicken".
  Hero level capped at 100. Gold +3000. The script keeps the literals as UTF-8 bytes.
