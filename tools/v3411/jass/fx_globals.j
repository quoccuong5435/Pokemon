// ---- v3.4.11: move / status engine, League room, -tp (tools/v3411)
hashtable Fx_HT = InitHashtable()
unit Fx_ArgU = null                     // arguments for ExecuteFunc("Fx_...X") from earlier code
unit Fx_ArgV = null
integer Fx_ArgI = 0
integer Fx_ArgJ = 0
group Fx_G = CreateGroup()              // units with a timed status / stage
group Fx_ScanG = CreateGroup()
group Fx_TmpG = CreateGroup()
group Fx_AoeG = CreateGroup()
integer Fx_TickN = 0
string array Fx_StatName
string array Fx_StName
string array Fx_StatShort               // v3.4.15: Atk / Def / SpA / SpD / Spe (the line over a Pokemon)
string array Fx_StShort                 // v3.4.15: Burn / Poison / Toxic / Para / Sleep / Frozen
string array Fx_TItemName               // type index -> name of its type item
real array Fx_LWarn                     // pid: last League / PvP message
real array Fx_TpReady                   // pid: when -tp works again
integer array Fx_LQ                     // League queue (player ids)
integer Fx_LQN = 0
real array Fx_GateX                     // 0 west / 1 east base: the League portal (next to the Item Shop)
real array Fx_GateY
unit Fx_LCenter = null
real Fx_LAX = 0.0                       // League arena centre (Darkrai's room)
real Fx_LAY = 0.0
real Fx_LLX = 0.0                       // lobby
real Fx_LLY = 0.0
real Fx_LEX = 0.0                       // exit portal
real Fx_LEY = 0.0
real Fx_LGX = 0.0                       // fallback base portal (west; east = -x)
real Fx_LGY = 0.0
real Fx_LRX0 = 0.0
real Fx_LRY0 = 0.0
real Fx_LRX1 = 0.0
real Fx_LRY1 = 0.0
integer array Fx_StatueType
real array Fx_StatueX
real array Fx_StatueY
string array Fx_StatueName
integer Fx_StatueN = 0
constant integer Fx_StatBase = 320      // v3.4.12: first status move (67 since v3.4.16, tools/v3411/status_moves.py)
constant real Fx_StageDur = 20.0        // v3.4.16: seconds a stat stage lasts (was 12)
constant integer Fx_AbAtk = 'AF0A'      // v3.4.16: hidden item bonuses that show a stage as green / red numbers
constant integer Fx_AbDef = 'AF0D'      //   attack damage, armor, attack speed (build.py makes them)
constant integer Fx_AbSpd = 'AF0S'
constant integer Fx_IconUp = 'AF1A'     // v3.4.16: self-only auras = buff icons: AF1A+k-1 raised stat k,
constant integer Fx_IconDown = 'AF1F'   //   AF1F+k-1 lowered stat k, AF1K+s-1 status s (1..6), AF1Q confused,
constant integer Fx_IconStatus = 'AF1K' //   AF1R accuracy down
constant integer Fx_IconConf = 'AF1Q'
constant integer Fx_IconAcc = 'AF1R'
constant real Fx_ArmorStep = 3.0        // v3.4.16: armor per Defense stage
string array Fx_BadgeModel              // v3.4.16: gym 0..7 -> badge model (Pokemon World), shown on a clear
string array Fx_BadgeName
unit array Fx_Leader                   // v3.4.16: 0..7 gym leaders, 8..12 Elite Four + Champion (NPCs)
integer array Fx_LeaderType
string array Fx_LeaderName
string array Fx_LeaderHi
string array Fx_LeaderWin
real array Fx_LeaderX                   // League ones only (gym leaders stand Fx_LeaderOff north of the gym)
real array Fx_LeaderY
constant real Fx_LeaderOff = 420.0
integer array Fx_RegFrom                // v3.4.16: regional forms: wild type -> skin, name, types (Fx_RegionalX)
integer array Fx_RegSkin
string array Fx_RegName
integer array Fx_RegT1
integer array Fx_RegT2
integer Fx_RegN = 0
constant real Fx_RegChance = 0.10
group Fx_QuestG = CreateGroup()         // v3.4.16: quests (scratch group)
integer array Fx_QKind
integer array Fx_QType
integer array Fx_QNeed
integer array Fx_QHave
real array Fx_QNext
constant integer Fx_QuestGold = 1500
group Fx_RocketG = CreateGroup()        // v3.4.16: Team Rocket raid (its Pokemon)
boolean Fx_RocketOn = false
integer Fx_RocketSide = 0
real Fx_RocketEnd = 0.0
real Fx_RocketTX = 0.0
real Fx_RocketTY = 0.0
unit array Fx_RocketNpc
integer array Fx_RocketType
constant integer Fx_RocketJessie = 'nT0D'
constant integer Fx_RocketGrunt = 'nT0E'
constant real Fx_RocketFirst = 600.0
constant real Fx_RocketEvery = 900.0
constant real Fx_RocketTime = 120.0     // v3.4.16 harder (user): 120 s, 8 Pokemon, power +6, HP x3, damage x1.6
constant integer Fx_RocketCount = 8
constant integer Fx_RocketPow = 6
constant real Fx_RocketHP = 3.0
constant real Fx_RocketDmg = 1.6
constant integer Fx_RocketKill = 600
constant integer Fx_RocketWin = 3000
constant integer Fx_RocketSteal = 1500  // penalty: Fx_RocketStealPct % of the gold, at least this
constant integer Fx_RocketStealPct = 30
constant real Fx_RocketCurse = 120.0
constant integer Fx_PriceLvBase = 500    // v3.4.16 moves NPC prices (user: still too cheap, raised ~3x)
constant integer Fx_PriceLvPow = 40      //   level-up move: base + this x power
constant integer Fx_PriceTmBase = 2000
constant integer Fx_PriceTmPow = 80      //   TM move: base + this x power
constant integer Fx_PriceLvStatus = 2000
constant integer Fx_PriceTmStatus = 5000
integer array Npc_Pend                  // v3.4.16 moves NPC: the move on the confirm screen, from the TM list
boolean array Npc_PendTm
constant integer Fx_DynaAbil = 'ADMX'   // v3.4.16 Dynamax (item IDMX): level, duration, size, move damage
constant integer Fx_DynaLevel = 20
constant real Fx_DynaTime = 20.0
constant real Fx_DynaScale = 2.0
constant real Fx_DynaDmg = 1.5
string array Fx_MaxFx                   // type -> big blast of a Max Move (PkFx model), its scale
real array Fx_MaxScale    // penalty: all stats -1 for this long
constant integer Leg_BuffHP = 20        // v3.4.16: random legends: max HP x20, attack damage x5, armor x3
constant integer Leg_BuffDmg = 5
constant integer Leg_BuffArmor = 3
constant real Leg_EnrageDmg = 1.5       // v3.4.16: legend below 50% HP: attack x1.5, Leg_EnrageAdds wild helpers
constant integer Leg_EnrageAdds = 2
constant integer Leg_RewardGold = 20000 // v3.4.16: gold shared by damage dealt; the top dealer gets the Soul
string array Fx_SName                   // status move index - Fx_StatBase -> name
integer array Fx_AiMove                 // kit type -> status move the AI uses
integer array Fx_AiEasy                 // same for gyms 1-4 (no sleep / confusion)
integer array Fx_KitDrop                // v3.4.13: kit type -> the kit skill its status move button replaces
integer Fx_ArgK = 0
constant integer AB_PRESSURELEG = 74    // v3.4.11: new Abilities of the legends
constant integer AB_DRIZZLE = 75
constant integer AB_REGENERATOR = 76
constant integer AB_SERENEGRACE = 77
constant integer AB_BEASTBOOST = 78
constant integer AB_PROTEAN = 79        // v3.4.16: Greninja
constant integer AB_SNOWWARNING = 80    // v3.4.16: Mega Abomasnow
real array Fx_SnowNext                  // v3.4.16: player -> next time its Snow Warning may call hail
