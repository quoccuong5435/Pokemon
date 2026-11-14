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
constant integer Fx_StatBase = 320      // v3.4.12: first status move (58 of them, tools/v3411/status_moves.py)
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
