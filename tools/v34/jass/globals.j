// ===== v3.4 (tools/v34): gym teams, attack speed, wild HP by tier, type chart, Abilities rework =====
//V34_GEN_GLOBALS
constant real Hero_ASBoost = 1.7        // v3.4: the players' Pokemon attack 1.7x faster (Hero_HPSync)
constant real Gym_ClearCool = 5.0       // v3.4: seconds before a player may challenge the gym he just cleared again
real array Gym_PCool                    // pid * 8 + gym: time from which that player may challenge that gym
integer array Gym_Team                  // g * 6 + k: unit type of the k-th Pokemon of the current challenge
integer array Gym_Root                  // g * 6 + k: first form of its evolution line (no two of one line)
integer array Gym_TeamKit               // g * 6 + k: type (0..17) of the skills it gets
unit array Gym_Dead                     // the last gym Pokemon that died (heroes do not decay: removed next tick)
integer Gym_PoolN = 0                   // first forms that gyms may use (one per line, no legends), Ty_InitData
integer array Gym_Pool
// evolutions for the gym forms (the map's Evo_*, the v1.8 level triggers, PokeAPI / hand levels for stone and trade
// evolutions), Ty_InitData: Ab_HT of the unit type, key 299 = number, 300 + 2k = evolved type, 301 + 2k = level
real array Wild_PowHP                   // v3.4: HP of a wild creep by power 1..10 (the v3.2.15 table), x tier step
integer array Wild_PowLv                // level of each power (creeps with no stored power use their own level)
// type chart, types in kit order 0..17: bug dark dragon electric fairy fighting fire flying ghost grass ground ice
// normal poison psychic rock steel water
real array Ty_Eff                       // attacker type * 18 + defender type: 2.0 / 1.0 / 0.5 / 0.0 (immune)
string array Ty_Name
integer array Mv_Type                   // learned move -> type, -1 = none
integer array Mv_Pow
integer array Mv_Phys                   // 1 physical, 2 special
integer array Ty_PType                  // pid: type + 1 of the last move the player's units cast
real array Ty_PTime
integer array Ty_PPow
integer array Ty_PPhys
integer Ty_CurPow = 60                  // power / class of the move found by Ty_Resolve
integer Ty_CurPhys = 2
constant real Ty_Window = 6.0           // damage within 6s of a cast counts as that move's damage
constant real Ty_ImmuneMult = 0.25      // an immune type still takes 25% (never 0)
constant real Ty_MaxMult = 2.0          // dual weakness is still x2
unit array Ab_FxSrc                     // source of a damage-over-time slot (kill credit)
unit Ab_FxCur = null                    // source given to the next Ab_FxAdd
lightning array Ab_Lt                   // chain lightning bolts, destroyed by Ab_FxRun
real array Ab_LtEnd
constant integer Ab_LtMax = 32
group Ab_HitG = CreateGroup()
integer Ab_FxNext = 0                  // Ab_FxFree goes on from here
group Ai_G = CreateGroup()              // v3.4 Ai_Tick: neutral units that cast their kit skills
constant real Ai_CastChance = 0.6       // chance per second to try a skill while fighting
constant real Ai_Memory = 4.0           // seconds without hits before a caster forgets its target
integer Ab_ZenSkin = 0                  // v3.4 Zen Mode of Darmanitan: skin unit, scales (V34_Data), armor bonus
real Ab_ZenScale = 1.0
real Ab_ZenBase = 1.0
constant real Ab_ZenArmor = 25.0
real array Wild_PowDmg                  // v3.4: damage / armor / gold of the new wild species by the power of the camp
real array Wild_PowArm
integer array Wild_PowGold
integer array Wild_PowCnt               // Wild_IndexPool: number of pool entries of each power,
integer array Wild_PowAt                // and their pool indexes at power * Wild_PowStride + k
constant integer Wild_PowStride = 400
// v3.4 extras (extra.j, extra_late.j, League in gym.j; docs/v3.5-items-league-features-proposal.md)
integer Itm_N = 0
integer array Itm_Id                    // held / utility item k (Ab_HT key 140 + k on the holder)
integer Itm_Everstone = 0
integer Itm_MegaRing = 0
integer Itm_Rope = 0
boolean Mega_EvoItem = false            // a stone or a Soul is replacing the unit: Everstone does not stop it
constant integer Shiny_Chance = 100
constant integer Shiny_ChanceChamp = 20
integer Wth_Cur = 0                     // 0 clear, 1 rain, 2 sun, 3 sandstorm, 4 hail
weathereffect Wth_Fx = null
group Ext_G = CreateGroup()
integer array Ext_Shop
real array Ext_SpotX                    // shop spots of the west base (the east base mirrors x)
real array Ext_SpotY
integer Ext_SpotN = 0
constant real Wild_MegaChance = 0.25
constant integer Leg_MewtwoId = 'n01O'
constant integer Leg_RayquazaId = 'n00G'
constant integer Leg_MegaMewtwo = 13
constant integer Leg_MegaRayquaza = 15
integer League_Pid = -1
integer League_Stage = 0
unit League_Unit = null
real League_RX = 0.0
real League_RY = 0.0
real array League_Cool
boolean array League_Champ
integer array League_Type
string array League_Name
integer array League_ChampTeam
integer array League_Cand
