"""All balance knobs of the map in one place (v3.2). Change a number here, then build.

Python values are read by wild_data, legend_data and objects; the values in JASS (tools/jass/mega.j) are written into
the script by inject._split_module, so the same number is used everywhere.
"""

# wild creeps (hoang da)
WILD_TIER_STEP = 0.08      # +8% HP, damage and gold per tier (tier 10 = x1.8)
WILD_DMG_MULT = 0.5         # v3.4: wild creep damage -20% (all tiers, elites included)
WILD_TIER_ARMOR = 1        # +1 armor per tier
WILD_RESPAWN = 10.0        # seconds before a dead camp respawns
CAMP_SIZE_MULT = 2         # creeps per camp = map camp size x this
WILD_SOUL_CHANCE = 20.0    # % chance an ELITE drops the Soul of its species (normal creeps drop none)
WILD_STONE_CHANCE = 5.0    # % chance an ELITE drops a random Mega Stone
# elite creep of each camp
ELITE_HP = 2.0
ELITE_DMG = 1.4
ELITE_ARMOR = 3.0
ELITE_GOLD = 3.0
ELITE_SCALE = 1.15
# legends
LEG_INTERVAL = 180.0       # seconds between two spawns
LEG_SPAWN_COUNT = 3        # legends per spawn
LEG_MAX = 99               # cap on legends alive at the same time
# Pokemon (playable)
SKILL_SCALE_K = 0.05       # skill damage x(1 + K * (main stat - 50)), at most x5 (Ab_ScaleMax in mega.j)
LEVEL_SKILL_K = 0.02       # extra skill damage per hero level above 50 (x(1 + K * (level - 50)))
BASIC_MULT = 1.8           # basic attacks of user Pokemon
