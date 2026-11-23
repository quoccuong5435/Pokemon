// ===========================================================================
// PAX_TestCommands: -gen <1..4>, -c <dex/name>, -nolvl, -lvl <n>, -clear
// ===========================================================================
globals
    group PAX_Gen_Group = null
    texttag array PAX_Gen_Tags
    integer PAX_Gen_TagCount = 0
    boolean PAX_NoLevelCap = false
    integer array PAX_Dex_Hero
    string array PAX_Dex_Name
endglobals

function PAX_Test_InitData01 takes nothing returns nothing
    set PAX_Dex_Hero[1] = 'E008'
    set PAX_Dex_Name[1] = "Bulbasaur"
    set PAX_Dex_Hero[2] = 'E001'
    set PAX_Dex_Name[2] = "Ivysaur"
    set PAX_Dex_Hero[3] = 'E002'
    set PAX_Dex_Name[3] = "Venusaur"
    set PAX_Dex_Hero[4] = 'E003'
    set PAX_Dex_Name[4] = "Charmander"
    set PAX_Dex_Hero[5] = 'E007'
    set PAX_Dex_Name[5] = "Charmeleon"
    set PAX_Dex_Hero[6] = 'E00E'
    set PAX_Dex_Name[6] = "Charizard"
    set PAX_Dex_Hero[7] = 'E004'
    set PAX_Dex_Name[7] = "Squirtle"
    set PAX_Dex_Hero[8] = 'E009'
    set PAX_Dex_Name[8] = "Wartortle"
    set PAX_Dex_Hero[9] = 'E000'
    set PAX_Dex_Name[9] = "Blastoise"
    set PAX_Dex_Hero[10] = 'E01N'
    set PAX_Dex_Name[10] = "Caterpie"
    set PAX_Dex_Hero[11] = 'E01P'
    set PAX_Dex_Name[11] = "Metapod"
    set PAX_Dex_Hero[12] = 'E01Q'
    set PAX_Dex_Name[12] = "Butterfree"
    set PAX_Dex_Hero[13] = 'E02I'
    set PAX_Dex_Name[13] = "Weedle"
    set PAX_Dex_Hero[14] = 'E02J'
    set PAX_Dex_Name[14] = "Kakuna"
    set PAX_Dex_Hero[15] = 'E02K'
    set PAX_Dex_Name[15] = "Beedrill"
    set PAX_Dex_Hero[16] = 'E00B'
    set PAX_Dex_Name[16] = "Pidgey"
    set PAX_Dex_Hero[17] = 'E00C'
    set PAX_Dex_Name[17] = "Pidgeotto"
    set PAX_Dex_Hero[18] = 'E00D'
    set PAX_Dex_Name[18] = "Pidgeot"
    set PAX_Dex_Hero[19] = 'E00T'
    set PAX_Dex_Name[19] = "Rattata"
    set PAX_Dex_Hero[20] = 'E00U'
    set PAX_Dex_Name[20] = "Raticate"
    set PAX_Dex_Hero[21] = 'EG00'
    set PAX_Dex_Name[21] = "Spearow"
    set PAX_Dex_Hero[22] = 'EG01'
    set PAX_Dex_Name[22] = "Fearow"
    set PAX_Dex_Hero[23] = 'P18A'
    set PAX_Dex_Name[23] = "Ekans"
    set PAX_Dex_Hero[24] = 'P09A'
    set PAX_Dex_Name[24] = "Arbok"
    set PAX_Dex_Hero[25] = 'E005'
    set PAX_Dex_Name[25] = "Pikachu"
    set PAX_Dex_Hero[26] = 'E006'
    set PAX_Dex_Name[26] = "Raichu"
    set PAX_Dex_Hero[27] = 'E00A'
    set PAX_Dex_Name[27] = "Sandshrew"
    set PAX_Dex_Hero[28] = 'E00F'
    set PAX_Dex_Name[28] = "Sandslash"
    set PAX_Dex_Hero[29] = 'EG02'
    set PAX_Dex_Name[29] = "Nidoran F"
    set PAX_Dex_Hero[30] = 'EG03'
    set PAX_Dex_Name[30] = "Nidorina"
    set PAX_Dex_Hero[31] = 'EG04'
    set PAX_Dex_Name[31] = "Nidoqueen"
    set PAX_Dex_Hero[32] = 'E01M'
    set PAX_Dex_Name[32] = "Nidoran"
    set PAX_Dex_Hero[33] = 'E01L'
    set PAX_Dex_Name[33] = "Nidorino"
    set PAX_Dex_Hero[34] = 'E01J'
    set PAX_Dex_Name[34] = "Nidoking"
    set PAX_Dex_Hero[35] = 'P0RA'
    set PAX_Dex_Name[35] = "Clefairy"
    set PAX_Dex_Hero[36] = 'P0QA'
    set PAX_Dex_Name[36] = "Clefable"
    set PAX_Dex_Hero[37] = 'E04O'
    set PAX_Dex_Name[37] = "Vulpix"
    set PAX_Dex_Hero[38] = 'E04P'
    set PAX_Dex_Name[38] = "Ninetales"
    set PAX_Dex_Hero[39] = 'P20A'
    set PAX_Dex_Name[39] = "Jigglypuff"
    set PAX_Dex_Hero[40] = 'P4IA'
    set PAX_Dex_Name[40] = "Wigglytuff"
    set PAX_Dex_Hero[41] = 'E046'
    set PAX_Dex_Name[41] = "Zubat"
    set PAX_Dex_Hero[42] = 'E048'
    set PAX_Dex_Name[42] = "Golbat"
    set PAX_Dex_Hero[43] = 'P30A'
    set PAX_Dex_Name[43] = "Oddish"
    set PAX_Dex_Hero[44] = 'P1OA'
    set PAX_Dex_Name[44] = "Gloom"
    set PAX_Dex_Hero[45] = 'P4GA'
    set PAX_Dex_Name[45] = "Vileplume"
    set PAX_Dex_Hero[46] = 'EG05'
    set PAX_Dex_Name[46] = "Paras"
    set PAX_Dex_Hero[47] = 'EG06'
    set PAX_Dex_Name[47] = "Parasect"
    set PAX_Dex_Hero[48] = 'EG07'
    set PAX_Dex_Name[48] = "Venonat"
    set PAX_Dex_Hero[49] = 'EG08'
    set PAX_Dex_Name[49] = "Venomoth"
    set PAX_Dex_Hero[50] = 'P11A'
    set PAX_Dex_Name[50] = "Diglett"
    set PAX_Dex_Hero[51] = 'P14A'
    set PAX_Dex_Name[51] = "Dugtrio"
    set PAX_Dex_Hero[52] = 'P2QA'
    set PAX_Dex_Name[52] = "Meowth"
    set PAX_Dex_Hero[53] = 'P31A'
    set PAX_Dex_Name[53] = "Persian"
    set PAX_Dex_Hero[54] = 'P36A'
    set PAX_Dex_Name[54] = "Psyduck"
    set PAX_Dex_Hero[55] = 'P1PA'
    set PAX_Dex_Name[55] = "Golduck"
    set PAX_Dex_Hero[56] = 'E02S'
    set PAX_Dex_Name[56] = "Mankey"
    set PAX_Dex_Hero[57] = 'E02T'
    set PAX_Dex_Name[57] = "Primeape"
    set PAX_Dex_Hero[58] = 'E02F'
    set PAX_Dex_Name[58] = "Growlithe"
    set PAX_Dex_Hero[59] = 'E01C'
    set PAX_Dex_Name[59] = "Arcanine"
    set PAX_Dex_Hero[60] = 'E012'
    set PAX_Dex_Name[60] = "Poliwag"
    set PAX_Dex_Hero[61] = 'E013'
    set PAX_Dex_Name[61] = "Poliwhirl"
    set PAX_Dex_Hero[62] = 'E014'
    set PAX_Dex_Name[62] = "Poliwrath"
    set PAX_Dex_Hero[63] = 'E00G'
    set PAX_Dex_Name[63] = "Abra"
    set PAX_Dex_Hero[64] = 'E00H'
    set PAX_Dex_Name[64] = "Kadabra"
    set PAX_Dex_Hero[65] = 'E00I'
    set PAX_Dex_Name[65] = "Alakazam"
    set PAX_Dex_Hero[66] = 'E00Y'
    set PAX_Dex_Name[66] = "Machop"
    set PAX_Dex_Hero[67] = 'E00Z'
    set PAX_Dex_Name[67] = "Machoke"
    set PAX_Dex_Hero[68] = 'E010'
    set PAX_Dex_Name[68] = "Machamp"
    set PAX_Dex_Hero[69] = 'E02B'
    set PAX_Dex_Name[69] = "Bellsprout"
    set PAX_Dex_Hero[70] = 'E01A'
    set PAX_Dex_Name[70] = "Weepinbell"
    set PAX_Dex_Hero[71] = 'E02C'
    set PAX_Dex_Name[71] = "Victreebel"
    set PAX_Dex_Hero[72] = 'E02D'
    set PAX_Dex_Name[72] = "Tentacool"
    set PAX_Dex_Hero[73] = 'E01I'
    set PAX_Dex_Name[73] = "Tentacruel"
    set PAX_Dex_Hero[74] = 'E00N'
    set PAX_Dex_Name[74] = "Geodude"
    set PAX_Dex_Hero[75] = 'E00O'
    set PAX_Dex_Name[75] = "Graveler"
    set PAX_Dex_Hero[76] = 'E00P'
    set PAX_Dex_Name[76] = "Golem"
    set PAX_Dex_Hero[77] = 'E01B'
    set PAX_Dex_Name[77] = "Ponyta"
    set PAX_Dex_Hero[78] = 'E01H'
    set PAX_Dex_Name[78] = "Rapidash"
    set PAX_Dex_Hero[79] = 'P3PA'
    set PAX_Dex_Name[79] = "Slowpoke"
    set PAX_Dex_Hero[80] = 'P3NA'
    set PAX_Dex_Name[80] = "Slowbro"
    set PAX_Dex_Hero[81] = 'E031'
    set PAX_Dex_Name[81] = "Magnemite"
    set PAX_Dex_Hero[82] = 'E032'
    set PAX_Dex_Name[82] = "Magneton"
    set PAX_Dex_Hero[83] = 'P1EA'
    set PAX_Dex_Name[83] = "Farfetch'd"
    set PAX_Dex_Hero[84] = 'EG09'
    set PAX_Dex_Name[84] = "Doduo"
    set PAX_Dex_Hero[85] = 'EG0A'
    set PAX_Dex_Name[85] = "Dodrio"
    set PAX_Dex_Hero[86] = 'P3HA'
    set PAX_Dex_Name[86] = "Seel"
    set PAX_Dex_Hero[87] = 'P10A'
    set PAX_Dex_Name[87] = "Dewgong"
    set PAX_Dex_Hero[88] = 'EG0B'
    set PAX_Dex_Name[88] = "Grimer"
    set PAX_Dex_Hero[89] = 'EG0C'
    set PAX_Dex_Name[89] = "Muk"
    set PAX_Dex_Hero[90] = 'E02E'
    set PAX_Dex_Name[90] = "Shellder"
    set PAX_Dex_Hero[91] = 'E01F'
    set PAX_Dex_Name[91] = "Cloyster"
    set PAX_Dex_Hero[92] = 'E02G'
    set PAX_Dex_Name[92] = "Gastly"
    set PAX_Dex_Hero[93] = 'E02H'
    set PAX_Dex_Name[93] = "Haunter"
    set PAX_Dex_Hero[94] = 'E01G'
    set PAX_Dex_Name[94] = "Gengar"
    set PAX_Dex_Hero[95] = 'E03U'
    set PAX_Dex_Name[95] = "Onix"
    set PAX_Dex_Hero[96] = 'P13A'
    set PAX_Dex_Name[96] = "Drowzee"
    set PAX_Dex_Hero[97] = 'P1ZA'
    set PAX_Dex_Name[97] = "Hypno"
    set PAX_Dex_Hero[98] = 'E03C'
    set PAX_Dex_Name[98] = "Krabby"
    set PAX_Dex_Hero[99] = 'E03D'
    set PAX_Dex_Name[99] = "Kingler"
    set PAX_Dex_Hero[100] = 'E01D'
    set PAX_Dex_Name[100] = "Voltorb"
    set PAX_Dex_Hero[101] = 'E01X'
    set PAX_Dex_Name[101] = "Electrode"
    set PAX_Dex_Hero[102] = 'E02U'
    set PAX_Dex_Name[102] = "Exeggcute"
    set PAX_Dex_Hero[103] = 'E02W'
    set PAX_Dex_Name[103] = "Exeggutor"
    set PAX_Dex_Hero[104] = 'P0VA'
    set PAX_Dex_Name[104] = "Cubone"
    set PAX_Dex_Hero[105] = 'P2PA'
    set PAX_Dex_Name[105] = "Marowak"
    set PAX_Dex_Hero[106] = 'E03Y'
    set PAX_Dex_Name[106] = "Hitmonlee"
    set PAX_Dex_Hero[107] = 'E01Z'
    set PAX_Dex_Name[107] = "Hitmonchan"
    set PAX_Dex_Hero[108] = 'EG0D'
    set PAX_Dex_Name[108] = "Lickitung"
    set PAX_Dex_Hero[109] = 'E01V'
    set PAX_Dex_Name[109] = "Koffing"
    set PAX_Dex_Hero[110] = 'E019'
    set PAX_Dex_Name[110] = "Weezing"
    set PAX_Dex_Hero[111] = 'E02Y'
    set PAX_Dex_Name[111] = "Rhyhorn"
    set PAX_Dex_Hero[112] = 'E02Z'
    set PAX_Dex_Name[112] = "Rhydon"
    set PAX_Dex_Hero[113] = 'P0MA'
    set PAX_Dex_Name[113] = "Chansey"
    set PAX_Dex_Hero[114] = 'P40A'
    set PAX_Dex_Name[114] = "Tangela"
    set PAX_Dex_Hero[115] = 'E02P'
    set PAX_Dex_Name[115] = "Kangaskhan"
    set PAX_Dex_Hero[116] = 'P1VA'
    set PAX_Dex_Name[116] = "Horsea"
    set PAX_Dex_Hero[117] = 'P3GA'
    set PAX_Dex_Name[117] = "Seadra"
    set PAX_Dex_Hero[118] = 'EG0E'
    set PAX_Dex_Name[118] = "Goldeen"
    set PAX_Dex_Hero[119] = 'EG0F'
    set PAX_Dex_Name[119] = "Seaking"
    set PAX_Dex_Hero[120] = 'E04N'
    set PAX_Dex_Name[120] = "Staryu"
endfunction

function PAX_Test_InitData02 takes nothing returns nothing
    set PAX_Dex_Hero[121] = 'E04M'
    set PAX_Dex_Name[121] = "Starmie"
    set PAX_Dex_Hero[122] = 'E040'
    set PAX_Dex_Name[122] = "Mr.mime"
    set PAX_Dex_Hero[123] = 'E03L'
    set PAX_Dex_Name[123] = "Scyther"
    set PAX_Dex_Hero[124] = 'P23A'
    set PAX_Dex_Name[124] = "Jynx"
    set PAX_Dex_Hero[125] = 'P19A'
    set PAX_Dex_Name[125] = "Electabuzz"
    set PAX_Dex_Hero[126] = 'P2JA'
    set PAX_Dex_Name[126] = "Magmar"
    set PAX_Dex_Hero[127] = 'E03W'
    set PAX_Dex_Name[127] = "Pinsir"
    set PAX_Dex_Hero[128] = 'E018'
    set PAX_Dex_Name[128] = "Tauros"
    set PAX_Dex_Hero[129] = 'E03E'
    set PAX_Dex_Name[129] = "Magikarp"
    set PAX_Dex_Hero[130] = 'E03F'
    set PAX_Dex_Name[130] = "Gyarados"
    set PAX_Dex_Hero[131] = 'P29A'
    set PAX_Dex_Name[131] = "Lapras"
    set PAX_Dex_Hero[132] = 'P12A'
    set PAX_Dex_Name[132] = "Ditto"
    set PAX_Dex_Hero[133] = 'E03A'
    set PAX_Dex_Name[133] = "Eevee"
    set PAX_Dex_Hero[134] = 'E037'
    set PAX_Dex_Name[134] = "Vaporeon"
    set PAX_Dex_Hero[135] = 'E01E'
    set PAX_Dex_Name[135] = "Jolteon"
    set PAX_Dex_Hero[136] = 'E038'
    set PAX_Dex_Name[136] = "Flareon"
    set PAX_Dex_Hero[137] = 'P35A'
    set PAX_Dex_Name[137] = "Porygon"
    set PAX_Dex_Hero[138] = 'E03Q'
    set PAX_Dex_Name[138] = "Omanyte"
    set PAX_Dex_Hero[139] = 'E03R'
    set PAX_Dex_Name[139] = "Omastar"
    set PAX_Dex_Hero[140] = 'E03P'
    set PAX_Dex_Name[140] = "Kabuto"
    set PAX_Dex_Hero[141] = 'E035'
    set PAX_Dex_Name[141] = "Kabutops"
    set PAX_Dex_Hero[142] = 'P02A'
    set PAX_Dex_Name[142] = "Aerodactyl"
    set PAX_Dex_Hero[143] = 'P3TA'
    set PAX_Dex_Name[143] = "Snorlax"
    set PAX_Dex_Hero[144] = 'E020'
    set PAX_Dex_Name[144] = "Articuno"
    set PAX_Dex_Hero[145] = 'E03J'
    set PAX_Dex_Name[145] = "Zapdos"
    set PAX_Dex_Hero[146] = 'E021'
    set PAX_Dex_Name[146] = "Moltres"
    set PAX_Dex_Hero[147] = 'E01S'
    set PAX_Dex_Name[147] = "Dratini"
    set PAX_Dex_Hero[148] = 'E01T'
    set PAX_Dex_Name[148] = "Dragonair"
    set PAX_Dex_Hero[149] = 'E01K'
    set PAX_Dex_Name[149] = "Dragonite"
    set PAX_Dex_Hero[150] = 'E026'
    set PAX_Dex_Name[150] = "Mewtwo"
    set PAX_Dex_Hero[151] = 'E024'
    set PAX_Dex_Name[151] = "Mew"
    set PAX_Dex_Hero[152] = 'P0NA'
    set PAX_Dex_Name[152] = "Chikorita"
    set PAX_Dex_Hero[153] = 'P0CA'
    set PAX_Dex_Name[153] = "Bayleef"
    set PAX_Dex_Hero[154] = 'PV0A'
    set PAX_Dex_Name[154] = "Meganium"
    set PAX_Dex_Hero[155] = 'P0WA'
    set PAX_Dex_Name[155] = "Cyndaquil"
    set PAX_Dex_Hero[156] = 'P38A'
    set PAX_Dex_Name[156] = "Quilava"
    set PAX_Dex_Hero[157] = 'P4DA'
    set PAX_Dex_Name[157] = "Typhlosion"
    set PAX_Dex_Hero[158] = 'EP00'
    set PAX_Dex_Name[158] = "Totodile"
    set PAX_Dex_Hero[159] = 'EP01'
    set PAX_Dex_Name[159] = "Croconaw"
    set PAX_Dex_Hero[160] = 'EP02'
    set PAX_Dex_Name[160] = "Feraligatr"
    set PAX_Dex_Hero[161] = 'EG0G'
    set PAX_Dex_Name[161] = "Sentret"
    set PAX_Dex_Hero[162] = 'EG0H'
    set PAX_Dex_Name[162] = "Furret"
    set PAX_Dex_Hero[163] = 'P1UA'
    set PAX_Dex_Name[163] = "Hoothoot"
    set PAX_Dex_Hero[164] = 'P2ZA'
    set PAX_Dex_Name[164] = "Noctowl"
    set PAX_Dex_Hero[165] = 'EG0I'
    set PAX_Dex_Name[165] = "Ledyba"
    set PAX_Dex_Hero[166] = 'EG0J'
    set PAX_Dex_Name[166] = "Ledian"
    set PAX_Dex_Hero[167] = 'EG0K'
    set PAX_Dex_Name[167] = "Spinarak"
    set PAX_Dex_Hero[168] = 'EG0L'
    set PAX_Dex_Name[168] = "Ariados"
    set PAX_Dex_Hero[169] = 'E049'
    set PAX_Dex_Name[169] = "Crobat"
    set PAX_Dex_Hero[170] = 'P0OA'
    set PAX_Dex_Name[170] = "Chinchou"
    set PAX_Dex_Hero[171] = 'P28A'
    set PAX_Dex_Name[171] = "Lanturn"
    set PAX_Dex_Hero[172] = 'EG0M'
    set PAX_Dex_Name[172] = "Pichu"
    set PAX_Dex_Hero[173] = 'EG0N'
    set PAX_Dex_Name[173] = "Cleffa"
    set PAX_Dex_Hero[174] = 'EG0O'
    set PAX_Dex_Name[174] = "Igglybuff"
    set PAX_Dex_Hero[175] = 'P46A'
    set PAX_Dex_Name[175] = "Togepi"
    set PAX_Dex_Hero[176] = 'P47A'
    set PAX_Dex_Name[176] = "Togetic"
    set PAX_Dex_Hero[177] = 'EG0P'
    set PAX_Dex_Name[177] = "Natu"
    set PAX_Dex_Hero[178] = 'EG0Q'
    set PAX_Dex_Name[178] = "Xatu"
    set PAX_Dex_Hero[179] = 'P2OA'
    set PAX_Dex_Name[179] = "Mareep"
    set PAX_Dex_Hero[180] = 'P1GA'
    set PAX_Dex_Name[180] = "Flaaffy"
    set PAX_Dex_Hero[181] = 'P08A'
    set PAX_Dex_Name[181] = "Ampharos"
    set PAX_Dex_Hero[182] = 'P0EA'
    set PAX_Dex_Name[182] = "Bellossom"
    set PAX_Dex_Hero[183] = 'EG0R'
    set PAX_Dex_Name[183] = "Marill"
    set PAX_Dex_Hero[184] = 'EG0S'
    set PAX_Dex_Name[184] = "Azumarill"
    set PAX_Dex_Hero[185] = 'P3WA'
    set PAX_Dex_Name[185] = "Sudowoodo"
    set PAX_Dex_Hero[186] = 'P34A'
    set PAX_Dex_Name[186] = "Politoed"
    set PAX_Dex_Hero[187] = 'EG0T'
    set PAX_Dex_Name[187] = "Hoppip"
    set PAX_Dex_Hero[188] = 'EG0U'
    set PAX_Dex_Name[188] = "Skiploom"
    set PAX_Dex_Hero[189] = 'EG0V'
    set PAX_Dex_Name[189] = "Jumpluff"
    set PAX_Dex_Hero[190] = 'EG0W'
    set PAX_Dex_Name[190] = "Aipom"
    set PAX_Dex_Hero[191] = 'EG0X'
    set PAX_Dex_Name[191] = "Sunkern"
    set PAX_Dex_Hero[192] = 'EG0Y'
    set PAX_Dex_Name[192] = "Sunflora"
    set PAX_Dex_Hero[193] = 'EG0Z'
    set PAX_Dex_Name[193] = "Yanma"
    set PAX_Dex_Hero[194] = 'EG10'
    set PAX_Dex_Name[194] = "Wooper"
    set PAX_Dex_Hero[195] = 'EG11'
    set PAX_Dex_Name[195] = "Quagsire"
    set PAX_Dex_Hero[196] = 'E03H'
    set PAX_Dex_Name[196] = "Espeon"
    set PAX_Dex_Hero[197] = 'E03I'
    set PAX_Dex_Name[197] = "Umbreon"
    set PAX_Dex_Hero[198] = 'EG12'
    set PAX_Dex_Name[198] = "Murkrow"
    set PAX_Dex_Hero[199] = 'P3OA'
    set PAX_Dex_Name[199] = "Slowking"
    set PAX_Dex_Hero[200] = 'P2UA'
    set PAX_Dex_Name[200] = "Misdreavus"
    set PAX_Dex_Hero[201] = 'EG13'
    set PAX_Dex_Name[201] = "Unown"
    set PAX_Dex_Hero[202] = 'P4JA'
    set PAX_Dex_Name[202] = "Wobbuffet"
    set PAX_Dex_Hero[203] = 'EG14'
    set PAX_Dex_Name[203] = "Girafarig"
    set PAX_Dex_Hero[204] = 'EG15'
    set PAX_Dex_Name[204] = "Pineco"
    set PAX_Dex_Hero[205] = 'EG16'
    set PAX_Dex_Name[205] = "Forretress"
    set PAX_Dex_Hero[206] = 'EG17'
    set PAX_Dex_Name[206] = "Dunsparce"
    set PAX_Dex_Hero[207] = 'EG18'
    set PAX_Dex_Name[207] = "Gligar"
    set PAX_Dex_Hero[208] = 'E03V'
    set PAX_Dex_Name[208] = "Steelix"
    set PAX_Dex_Hero[209] = 'P3VA'
    set PAX_Dex_Name[209] = "Snubbull"
    set PAX_Dex_Hero[210] = 'P1QA'
    set PAX_Dex_Name[210] = "Granbull"
    set PAX_Dex_Hero[211] = 'EG19'
    set PAX_Dex_Name[211] = "Qwilfish"
    set PAX_Dex_Hero[212] = 'E03M'
    set PAX_Dex_Name[212] = "Scizor"
    set PAX_Dex_Hero[213] = 'EG1A'
    set PAX_Dex_Name[213] = "Shuckle"
    set PAX_Dex_Hero[214] = 'P1SA'
    set PAX_Dex_Name[214] = "Heracross"
    set PAX_Dex_Hero[215] = 'P3SA'
    set PAX_Dex_Name[215] = "Sneasel"
    set PAX_Dex_Hero[216] = 'EG1B'
    set PAX_Dex_Name[216] = "Teddiursa"
    set PAX_Dex_Hero[217] = 'EG1C'
    set PAX_Dex_Name[217] = "Ursaring"
    set PAX_Dex_Hero[218] = 'P3QA'
    set PAX_Dex_Name[218] = "Slugma"
    set PAX_Dex_Hero[219] = 'P2IA'
    set PAX_Dex_Name[219] = "Magcargo"
    set PAX_Dex_Hero[220] = 'P3ZA'
    set PAX_Dex_Name[220] = "Swinub"
    set PAX_Dex_Hero[221] = 'P32A'
    set PAX_Dex_Name[221] = "Piloswine"
    set PAX_Dex_Hero[222] = 'EG1D'
    set PAX_Dex_Name[222] = "Corsola"
    set PAX_Dex_Hero[223] = 'EG1E'
    set PAX_Dex_Name[223] = "Remoraid"
    set PAX_Dex_Hero[224] = 'EG1F'
    set PAX_Dex_Name[224] = "Octillery"
    set PAX_Dex_Hero[225] = 'EG1G'
    set PAX_Dex_Name[225] = "Delibird"
    set PAX_Dex_Hero[226] = 'EG1H'
    set PAX_Dex_Name[226] = "Mantine"
    set PAX_Dex_Hero[227] = 'EG1I'
    set PAX_Dex_Name[227] = "Skarmory"
    set PAX_Dex_Hero[228] = 'P1XA'
    set PAX_Dex_Name[228] = "Houndour"
    set PAX_Dex_Hero[229] = 'P1WA'
    set PAX_Dex_Name[229] = "Houndoom"
    set PAX_Dex_Hero[230] = 'P24A'
    set PAX_Dex_Name[230] = "Kingdra"
    set PAX_Dex_Hero[231] = 'EG1J'
    set PAX_Dex_Name[231] = "Phanpy"
    set PAX_Dex_Hero[232] = 'EG1K'
    set PAX_Dex_Name[232] = "Donphan"
    set PAX_Dex_Hero[233] = 'PV1A'
    set PAX_Dex_Name[233] = "Porygon2"
    set PAX_Dex_Hero[234] = 'EG1L'
    set PAX_Dex_Name[234] = "Stantler"
    set PAX_Dex_Hero[235] = 'EG1M'
    set PAX_Dex_Name[235] = "Smeargle"
    set PAX_Dex_Hero[236] = 'P4EA'
    set PAX_Dex_Name[236] = "Tyrogue"
    set PAX_Dex_Hero[237] = 'E03Z'
    set PAX_Dex_Name[237] = "Hitmontop"
    set PAX_Dex_Hero[238] = 'P3RA'
    set PAX_Dex_Name[238] = "Smoochum"
    set PAX_Dex_Hero[239] = 'P1CA'
    set PAX_Dex_Name[239] = "Elekid"
    set PAX_Dex_Hero[240] = 'P2HA'
    set PAX_Dex_Name[240] = "Magby"
endfunction

function PAX_Test_InitData03 takes nothing returns nothing
    set PAX_Dex_Hero[241] = 'EG1N'
    set PAX_Dex_Name[241] = "Miltank"
    set PAX_Dex_Hero[242] = 'P0GA'
    set PAX_Dex_Name[242] = "Blissey"
    set PAX_Dex_Hero[243] = 'P39A'
    set PAX_Dex_Name[243] = "Raikou"
    set PAX_Dex_Hero[244] = 'P1DA'
    set PAX_Dex_Name[244] = "Entei"
    set PAX_Dex_Hero[245] = 'P3XA'
    set PAX_Dex_Name[245] = "Suicune"
    set PAX_Dex_Hero[246] = 'EN06'
    set PAX_Dex_Name[246] = "Larvitar"
    set PAX_Dex_Hero[247] = 'EN07'
    set PAX_Dex_Name[247] = "Pupitar"
    set PAX_Dex_Hero[248] = 'EN08'
    set PAX_Dex_Name[248] = "Tyranitar"
    set PAX_Dex_Hero[249] = 'EG1O'
    set PAX_Dex_Name[249] = "Lugia"
    set PAX_Dex_Hero[250] = 'P1TA'
    set PAX_Dex_Name[250] = "Ho-Oh"
    set PAX_Dex_Hero[251] = 'PZZA'
    set PAX_Dex_Name[251] = "Celebi"
    set PAX_Dex_Hero[252] = 'EN03'
    set PAX_Dex_Name[252] = "Treecko"
    set PAX_Dex_Hero[253] = 'EN04'
    set PAX_Dex_Name[253] = "Grovyle"
    set PAX_Dex_Hero[254] = 'EN05'
    set PAX_Dex_Name[254] = "Sceptile"
    set PAX_Dex_Hero[255] = 'EN00'
    set PAX_Dex_Name[255] = "Torchic"
    set PAX_Dex_Hero[256] = 'EN01'
    set PAX_Dex_Name[256] = "Combusken"
    set PAX_Dex_Hero[257] = 'EN02'
    set PAX_Dex_Name[257] = "Blaziken"
    set PAX_Dex_Hero[258] = 'EP03'
    set PAX_Dex_Name[258] = "Mudkip"
    set PAX_Dex_Hero[259] = 'EP04'
    set PAX_Dex_Name[259] = "Marshtomp"
    set PAX_Dex_Hero[260] = 'EP05'
    set PAX_Dex_Name[260] = "Swampert"
    set PAX_Dex_Hero[261] = 'EG1P'
    set PAX_Dex_Name[261] = "Poochyena"
    set PAX_Dex_Hero[262] = 'EG1Q'
    set PAX_Dex_Name[262] = "Mightyena"
    set PAX_Dex_Hero[263] = 'EG1R'
    set PAX_Dex_Name[263] = "Zigzagoon"
    set PAX_Dex_Hero[264] = 'EG1S'
    set PAX_Dex_Name[264] = "Linoone"
    set PAX_Dex_Hero[265] = 'EG1T'
    set PAX_Dex_Name[265] = "Wurmple"
    set PAX_Dex_Hero[266] = 'EG1U'
    set PAX_Dex_Name[266] = "Silcoon"
    set PAX_Dex_Hero[267] = 'EG1V'
    set PAX_Dex_Name[267] = "Beautifly"
    set PAX_Dex_Hero[268] = 'EG1W'
    set PAX_Dex_Name[268] = "Cascoon"
    set PAX_Dex_Hero[269] = 'EG1X'
    set PAX_Dex_Name[269] = "Dustox"
    set PAX_Dex_Hero[270] = 'P2FA'
    set PAX_Dex_Name[270] = "Lotad"
    set PAX_Dex_Hero[271] = 'P2EA'
    set PAX_Dex_Name[271] = "Lombre"
    set PAX_Dex_Hero[272] = 'P2GA'
    set PAX_Dex_Name[272] = "Ludicolo"
    set PAX_Dex_Hero[273] = 'EG1Y'
    set PAX_Dex_Name[273] = "Seedot"
    set PAX_Dex_Hero[274] = 'EG1Z'
    set PAX_Dex_Name[274] = "Nuzleaf"
    set PAX_Dex_Hero[275] = 'EG20'
    set PAX_Dex_Name[275] = "Shiftry"
    set PAX_Dex_Hero[276] = 'EG21'
    set PAX_Dex_Name[276] = "Taillow"
    set PAX_Dex_Hero[277] = 'EG22'
    set PAX_Dex_Name[277] = "Swellow"
    set PAX_Dex_Hero[278] = 'EG23'
    set PAX_Dex_Name[278] = "Wingull"
    set PAX_Dex_Hero[279] = 'EG24'
    set PAX_Dex_Name[279] = "Pelipper"
    set PAX_Dex_Hero[280] = 'EN09'
    set PAX_Dex_Name[280] = "Ralts"
    set PAX_Dex_Hero[281] = 'EN0A'
    set PAX_Dex_Name[281] = "Kirlia"
    set PAX_Dex_Hero[282] = 'EN0B'
    set PAX_Dex_Name[282] = "Gardevoir"
    set PAX_Dex_Hero[283] = 'EG25'
    set PAX_Dex_Name[283] = "Surskit"
    set PAX_Dex_Hero[284] = 'EG26'
    set PAX_Dex_Name[284] = "Masquerain"
    set PAX_Dex_Hero[285] = 'P3LA'
    set PAX_Dex_Name[285] = "Shroomish"
    set PAX_Dex_Hero[286] = 'P0IA'
    set PAX_Dex_Name[286] = "Breloom"
    set PAX_Dex_Hero[287] = 'EG27'
    set PAX_Dex_Name[287] = "Slakoth"
    set PAX_Dex_Hero[288] = 'EG28'
    set PAX_Dex_Name[288] = "Vigoroth"
    set PAX_Dex_Hero[289] = 'EG29'
    set PAX_Dex_Name[289] = "Slaking"
    set PAX_Dex_Hero[290] = 'P2XA'
    set PAX_Dex_Name[290] = "Nincada"
    set PAX_Dex_Hero[291] = 'P2YA'
    set PAX_Dex_Name[291] = "Ninjask"
    set PAX_Dex_Hero[292] = 'P3JA'
    set PAX_Dex_Name[292] = "Shedinja"
    set PAX_Dex_Hero[293] = 'EG2A'
    set PAX_Dex_Name[293] = "Whismur"
    set PAX_Dex_Hero[294] = 'EG2B'
    set PAX_Dex_Name[294] = "Loudred"
    set PAX_Dex_Hero[295] = 'EG2C'
    set PAX_Dex_Name[295] = "Exploud"
    set PAX_Dex_Hero[296] = 'EG2D'
    set PAX_Dex_Name[296] = "Makuhita"
    set PAX_Dex_Hero[297] = 'EG2E'
    set PAX_Dex_Name[297] = "Hariyama"
    set PAX_Dex_Hero[298] = 'EG2F'
    set PAX_Dex_Name[298] = "Azurill"
    set PAX_Dex_Hero[299] = 'EG2G'
    set PAX_Dex_Name[299] = "Nosepass"
    set PAX_Dex_Hero[300] = 'EG2H'
    set PAX_Dex_Name[300] = "Skitty"
    set PAX_Dex_Hero[301] = 'EG2I'
    set PAX_Dex_Name[301] = "Delcatty"
    set PAX_Dex_Hero[302] = 'P3DA'
    set PAX_Dex_Name[302] = "Sableye"
    set PAX_Dex_Hero[303] = 'EG2J'
    set PAX_Dex_Name[303] = "Mawile"
    set PAX_Dex_Hero[304] = 'EG2K'
    set PAX_Dex_Name[304] = "Aron"
    set PAX_Dex_Hero[305] = 'EG2L'
    set PAX_Dex_Name[305] = "Lairon"
    set PAX_Dex_Hero[306] = 'EG2M'
    set PAX_Dex_Name[306] = "Aggron"
    set PAX_Dex_Hero[307] = 'EG2N'
    set PAX_Dex_Name[307] = "Meditite"
    set PAX_Dex_Hero[308] = 'EG2O'
    set PAX_Dex_Name[308] = "Medicham"
    set PAX_Dex_Hero[309] = 'P1BA'
    set PAX_Dex_Name[309] = "Electrike"
    set PAX_Dex_Hero[310] = 'P2NA'
    set PAX_Dex_Name[310] = "Manectric"
    set PAX_Dex_Hero[311] = 'EG2P'
    set PAX_Dex_Name[311] = "Plusle"
    set PAX_Dex_Hero[312] = 'EG2Q'
    set PAX_Dex_Name[312] = "Minun"
    set PAX_Dex_Hero[313] = 'EG2R'
    set PAX_Dex_Name[313] = "Volbeat"
    set PAX_Dex_Hero[314] = 'EG2S'
    set PAX_Dex_Name[314] = "Illumise"
    set PAX_Dex_Hero[315] = 'EG2T'
    set PAX_Dex_Name[315] = "Roselia"
    set PAX_Dex_Hero[316] = 'EG2U'
    set PAX_Dex_Name[316] = "Gulpin"
    set PAX_Dex_Hero[317] = 'EG2V'
    set PAX_Dex_Name[317] = "Swalot"
    set PAX_Dex_Hero[318] = 'P0KA'
    set PAX_Dex_Name[318] = "Carvanha"
    set PAX_Dex_Hero[319] = 'P3IA'
    set PAX_Dex_Name[319] = "Sharpedo"
    set PAX_Dex_Hero[320] = 'EG2W'
    set PAX_Dex_Name[320] = "Wailmer"
    set PAX_Dex_Hero[321] = 'EG2X'
    set PAX_Dex_Name[321] = "Wailord"
    set PAX_Dex_Hero[322] = 'EG2Y'
    set PAX_Dex_Name[322] = "Numel"
    set PAX_Dex_Hero[323] = 'EG2Z'
    set PAX_Dex_Name[323] = "Camerupt"
    set PAX_Dex_Hero[324] = 'P49A'
    set PAX_Dex_Name[324] = "Torkoal"
    set PAX_Dex_Hero[325] = 'EG30'
    set PAX_Dex_Name[325] = "Spoink"
    set PAX_Dex_Hero[326] = 'EG31'
    set PAX_Dex_Name[326] = "Grumpig"
    set PAX_Dex_Hero[327] = 'EG32'
    set PAX_Dex_Name[327] = "Spinda"
    set PAX_Dex_Hero[328] = 'P4BA'
    set PAX_Dex_Name[328] = "Trapinch"
    set PAX_Dex_Hero[329] = 'P4FA'
    set PAX_Dex_Name[329] = "Vibrava"
    set PAX_Dex_Hero[330] = 'P1HA'
    set PAX_Dex_Name[330] = "Flygon"
    set PAX_Dex_Hero[331] = 'EG33'
    set PAX_Dex_Name[331] = "Cacnea"
    set PAX_Dex_Hero[332] = 'EG34'
    set PAX_Dex_Name[332] = "Cacturne"
    set PAX_Dex_Hero[333] = 'P3YA'
    set PAX_Dex_Name[333] = "Swablu"
    set PAX_Dex_Hero[334] = 'EG35'
    set PAX_Dex_Name[334] = "Altaria"
    set PAX_Dex_Hero[335] = 'EG36'
    set PAX_Dex_Name[335] = "Zangoose"
    set PAX_Dex_Hero[336] = 'EG37'
    set PAX_Dex_Name[336] = "Seviper"
    set PAX_Dex_Hero[337] = 'EG38'
    set PAX_Dex_Name[337] = "Lunatone"
    set PAX_Dex_Hero[338] = 'EG39'
    set PAX_Dex_Name[338] = "Solrock"
    set PAX_Dex_Hero[339] = 'EG3A'
    set PAX_Dex_Name[339] = "Barboach"
    set PAX_Dex_Hero[340] = 'EG3B'
    set PAX_Dex_Name[340] = "Whiscash"
    set PAX_Dex_Hero[341] = 'EG3C'
    set PAX_Dex_Name[341] = "Corphish"
    set PAX_Dex_Hero[342] = 'EG3D'
    set PAX_Dex_Name[342] = "Crawdaunt"
    set PAX_Dex_Hero[343] = 'P0BA'
    set PAX_Dex_Name[343] = "Baltoy"
    set PAX_Dex_Hero[344] = 'P0PA'
    set PAX_Dex_Name[344] = "Claydol"
    set PAX_Dex_Hero[345] = 'P2CA'
    set PAX_Dex_Name[345] = "Lileep"
    set PAX_Dex_Hero[346] = 'P0TA'
    set PAX_Dex_Name[346] = "Cradily"
    set PAX_Dex_Hero[347] = 'EG3E'
    set PAX_Dex_Name[347] = "Anorith"
    set PAX_Dex_Hero[348] = 'EG3F'
    set PAX_Dex_Name[348] = "Armaldo"
    set PAX_Dex_Hero[349] = 'P1FA'
    set PAX_Dex_Name[349] = "Feebas"
    set PAX_Dex_Hero[350] = 'P2TA'
    set PAX_Dex_Name[350] = "Milotic"
    set PAX_Dex_Hero[351] = 'EG3G'
    set PAX_Dex_Name[351] = "Castform"
    set PAX_Dex_Hero[352] = 'EG3H'
    set PAX_Dex_Name[352] = "Kecleon"
    set PAX_Dex_Hero[353] = 'EG3I'
    set PAX_Dex_Name[353] = "Shuppet"
    set PAX_Dex_Hero[354] = 'EG3J'
    set PAX_Dex_Name[354] = "Banette"
    set PAX_Dex_Hero[355] = 'P17A'
    set PAX_Dex_Name[355] = "Duskull"
    set PAX_Dex_Hero[356] = 'P15A'
    set PAX_Dex_Name[356] = "Dusclops"
    set PAX_Dex_Hero[357] = 'EG3K'
    set PAX_Dex_Name[357] = "Tropius"
    set PAX_Dex_Hero[358] = 'EG3L'
    set PAX_Dex_Name[358] = "Chimecho"
    set PAX_Dex_Hero[359] = 'EN0K'
    set PAX_Dex_Name[359] = "Absol"
    set PAX_Dex_Hero[360] = 'P4KA'
    set PAX_Dex_Name[360] = "Wynaut"
endfunction

function PAX_Test_InitData04 takes nothing returns nothing
    set PAX_Dex_Hero[361] = 'EG3M'
    set PAX_Dex_Name[361] = "Snorunt"
    set PAX_Dex_Hero[362] = 'EG3N'
    set PAX_Dex_Name[362] = "Glalie"
    set PAX_Dex_Hero[363] = 'EG3O'
    set PAX_Dex_Name[363] = "Spheal"
    set PAX_Dex_Hero[364] = 'EG3P'
    set PAX_Dex_Name[364] = "Sealeo"
    set PAX_Dex_Hero[365] = 'EG3Q'
    set PAX_Dex_Name[365] = "Walrein"
    set PAX_Dex_Hero[366] = 'EG3R'
    set PAX_Dex_Name[366] = "Clamperl"
    set PAX_Dex_Hero[367] = 'EG3S'
    set PAX_Dex_Name[367] = "Huntail"
    set PAX_Dex_Hero[368] = 'EG3T'
    set PAX_Dex_Name[368] = "Gorebyss"
    set PAX_Dex_Hero[369] = 'EG3U'
    set PAX_Dex_Name[369] = "Relicanth"
    set PAX_Dex_Hero[370] = 'EG3V'
    set PAX_Dex_Name[370] = "Luvdisc"
    set PAX_Dex_Hero[371] = 'EN0D'
    set PAX_Dex_Name[371] = "Bagon"
    set PAX_Dex_Hero[372] = 'EN0E'
    set PAX_Dex_Name[372] = "Shelgon"
    set PAX_Dex_Hero[373] = 'EN0F'
    set PAX_Dex_Name[373] = "Salamence"
    set PAX_Dex_Hero[374] = 'EN0G'
    set PAX_Dex_Name[374] = "Beldum"
    set PAX_Dex_Hero[375] = 'EN0H'
    set PAX_Dex_Name[375] = "Metang"
    set PAX_Dex_Hero[376] = 'EN0I'
    set PAX_Dex_Name[376] = "Metagross"
    set PAX_Dex_Hero[377] = 'P3BA'
    set PAX_Dex_Name[377] = "Regirock"
    set PAX_Dex_Hero[378] = 'EL00'
    set PAX_Dex_Name[378] = "Regice"
    set PAX_Dex_Hero[379] = 'EL01'
    set PAX_Dex_Name[379] = "Registeel"
    set PAX_Dex_Hero[380] = 'PV2A'
    set PAX_Dex_Name[380] = "Latias & Latios"
    set PAX_Dex_Hero[381] = 'PV2A'
    set PAX_Dex_Name[381] = "Latias & Latios"
    set PAX_Dex_Hero[382] = 'P26A'
    set PAX_Dex_Name[382] = "Kyogre"
    set PAX_Dex_Hero[383] = 'P4UA'
    set PAX_Dex_Name[383] = "Groudon"
    set PAX_Dex_Hero[384] = 'E029'
    set PAX_Dex_Name[384] = "Rayquaza"
    set PAX_Dex_Hero[385] = 'P21A'
    set PAX_Dex_Name[385] = "Jirachi"
    set PAX_Dex_Hero[386] = 'E027'
    set PAX_Dex_Name[386] = "Deoxys"
    set PAX_Dex_Hero[387] = 'EP06'
    set PAX_Dex_Name[387] = "Turtwig"
    set PAX_Dex_Hero[388] = 'EP07'
    set PAX_Dex_Name[388] = "Grotle"
    set PAX_Dex_Hero[389] = 'EP08'
    set PAX_Dex_Name[389] = "Torterra"
    set PAX_Dex_Hero[390] = 'EP09'
    set PAX_Dex_Name[390] = "Chimchar"
    set PAX_Dex_Hero[391] = 'EP0A'
    set PAX_Dex_Name[391] = "Monferno"
    set PAX_Dex_Hero[392] = 'EP0B'
    set PAX_Dex_Name[392] = "Infernape"
    set PAX_Dex_Hero[393] = 'EP0C'
    set PAX_Dex_Name[393] = "Piplup"
    set PAX_Dex_Hero[394] = 'EP0D'
    set PAX_Dex_Name[394] = "Prinplup"
    set PAX_Dex_Hero[395] = 'EP0E'
    set PAX_Dex_Name[395] = "Empoleon"
    set PAX_Dex_Hero[396] = 'EG3W'
    set PAX_Dex_Name[396] = "Starly"
    set PAX_Dex_Hero[397] = 'EG3X'
    set PAX_Dex_Name[397] = "Staravia"
    set PAX_Dex_Hero[398] = 'EG3Y'
    set PAX_Dex_Name[398] = "Staraptor"
    set PAX_Dex_Hero[399] = 'EG3Z'
    set PAX_Dex_Name[399] = "Bidoof"
    set PAX_Dex_Hero[400] = 'EG40'
    set PAX_Dex_Name[400] = "Bibarel"
    set PAX_Dex_Hero[401] = 'EG41'
    set PAX_Dex_Name[401] = "Kricketot"
    set PAX_Dex_Hero[402] = 'EG42'
    set PAX_Dex_Name[402] = "Kricketune"
    set PAX_Dex_Hero[403] = 'EG43'
    set PAX_Dex_Name[403] = "Shinx"
    set PAX_Dex_Hero[404] = 'EG44'
    set PAX_Dex_Name[404] = "Luxio"
    set PAX_Dex_Hero[405] = 'EG45'
    set PAX_Dex_Name[405] = "Luxray"
    set PAX_Dex_Hero[406] = 'EG46'
    set PAX_Dex_Name[406] = "Budew"
    set PAX_Dex_Hero[407] = 'EG47'
    set PAX_Dex_Name[407] = "Roserade"
    set PAX_Dex_Hero[408] = 'EG48'
    set PAX_Dex_Name[408] = "Cranidos"
    set PAX_Dex_Hero[409] = 'EG49'
    set PAX_Dex_Name[409] = "Rampardos"
    set PAX_Dex_Hero[410] = 'EG4A'
    set PAX_Dex_Name[410] = "Shieldon"
    set PAX_Dex_Hero[411] = 'EG4B'
    set PAX_Dex_Name[411] = "Bastiodon"
    set PAX_Dex_Hero[412] = 'EG4C'
    set PAX_Dex_Name[412] = "Burmy"
    set PAX_Dex_Hero[413] = 'EG4D'
    set PAX_Dex_Name[413] = "Wormadam"
    set PAX_Dex_Hero[414] = 'EG4E'
    set PAX_Dex_Name[414] = "Mothim"
    set PAX_Dex_Hero[415] = 'EG4F'
    set PAX_Dex_Name[415] = "Combee"
    set PAX_Dex_Hero[416] = 'EG4G'
    set PAX_Dex_Name[416] = "Vespiquen"
    set PAX_Dex_Hero[417] = 'EG4H'
    set PAX_Dex_Name[417] = "Pachirisu"
    set PAX_Dex_Hero[418] = 'EG4I'
    set PAX_Dex_Name[418] = "Buizel"
    set PAX_Dex_Hero[419] = 'EG4J'
    set PAX_Dex_Name[419] = "Floatzel"
    set PAX_Dex_Hero[420] = 'EG4K'
    set PAX_Dex_Name[420] = "Cherubi"
    set PAX_Dex_Hero[421] = 'EG4L'
    set PAX_Dex_Name[421] = "Cherrim"
    set PAX_Dex_Hero[422] = 'EG4M'
    set PAX_Dex_Name[422] = "Shellos"
    set PAX_Dex_Hero[423] = 'EG4N'
    set PAX_Dex_Name[423] = "Gastrodon"
    set PAX_Dex_Hero[424] = 'EG4O'
    set PAX_Dex_Name[424] = "Ambipom"
    set PAX_Dex_Hero[425] = 'EG4P'
    set PAX_Dex_Name[425] = "Drifloon"
    set PAX_Dex_Hero[426] = 'EG4Q'
    set PAX_Dex_Name[426] = "Drifblim"
    set PAX_Dex_Hero[427] = 'EG4R'
    set PAX_Dex_Name[427] = "Buneary"
    set PAX_Dex_Hero[428] = 'EG4S'
    set PAX_Dex_Name[428] = "Lopunny"
    set PAX_Dex_Hero[429] = 'P2VA'
    set PAX_Dex_Name[429] = "Mismagius"
    set PAX_Dex_Hero[430] = 'EG4T'
    set PAX_Dex_Name[430] = "Honchkrow"
    set PAX_Dex_Hero[431] = 'EG4U'
    set PAX_Dex_Name[431] = "Glameow"
    set PAX_Dex_Hero[432] = 'EG4V'
    set PAX_Dex_Name[432] = "Purugly"
    set PAX_Dex_Hero[433] = 'EG4W'
    set PAX_Dex_Name[433] = "Chingling"
    set PAX_Dex_Hero[434] = 'EG4X'
    set PAX_Dex_Name[434] = "Stunky"
    set PAX_Dex_Hero[435] = 'EG4Y'
    set PAX_Dex_Name[435] = "Skuntank"
    set PAX_Dex_Hero[436] = 'EG4Z'
    set PAX_Dex_Name[436] = "Bronzor"
    set PAX_Dex_Hero[437] = 'EG50'
    set PAX_Dex_Name[437] = "Bronzong"
    set PAX_Dex_Hero[438] = 'P0HA'
    set PAX_Dex_Name[438] = "Bonsly"
    set PAX_Dex_Hero[439] = 'EG51'
    set PAX_Dex_Name[439] = "Mime Jr."
    set PAX_Dex_Hero[440] = 'EG52'
    set PAX_Dex_Name[440] = "Happiny"
    set PAX_Dex_Hero[441] = 'EG53'
    set PAX_Dex_Name[441] = "Chatot"
    set PAX_Dex_Hero[442] = 'EG54'
    set PAX_Dex_Name[442] = "Spiritomb"
    set PAX_Dex_Hero[443] = 'P1NA'
    set PAX_Dex_Name[443] = "Gible"
    set PAX_Dex_Hero[444] = 'P1IA'
    set PAX_Dex_Name[444] = "Gabite"
    set PAX_Dex_Hero[445] = 'P1LA'
    set PAX_Dex_Name[445] = "Garchomp"
    set PAX_Dex_Hero[446] = 'EG55'
    set PAX_Dex_Name[446] = "Munchlax"
    set PAX_Dex_Hero[447] = 'EG56'
    set PAX_Dex_Name[447] = "Riolu"
    set PAX_Dex_Hero[448] = 'EN0J'
    set PAX_Dex_Name[448] = "Lucario"
    set PAX_Dex_Hero[449] = 'EG57'
    set PAX_Dex_Name[449] = "Hippopotas"
    set PAX_Dex_Hero[450] = 'EG58'
    set PAX_Dex_Name[450] = "Hippowdon"
    set PAX_Dex_Hero[451] = 'EG59'
    set PAX_Dex_Name[451] = "Skorupi"
    set PAX_Dex_Hero[452] = 'EG5A'
    set PAX_Dex_Name[452] = "Drapion"
    set PAX_Dex_Hero[453] = 'P0UA'
    set PAX_Dex_Name[453] = "Croagunk"
    set PAX_Dex_Hero[454] = 'P4AA'
    set PAX_Dex_Name[454] = "Toxicroak"
    set PAX_Dex_Hero[455] = 'EG5B'
    set PAX_Dex_Name[455] = "Carnivine"
    set PAX_Dex_Hero[456] = 'EG5C'
    set PAX_Dex_Name[456] = "Finneon"
    set PAX_Dex_Hero[457] = 'EG5D'
    set PAX_Dex_Name[457] = "Lumineon"
    set PAX_Dex_Hero[458] = 'EG5E'
    set PAX_Dex_Name[458] = "Mantyke"
    set PAX_Dex_Hero[459] = 'P3UA'
    set PAX_Dex_Name[459] = "Snover"
    set PAX_Dex_Hero[460] = 'P00A'
    set PAX_Dex_Name[460] = "Abomasnow"
    set PAX_Dex_Hero[461] = 'P4HA'
    set PAX_Dex_Name[461] = "Weavile"
    set PAX_Dex_Hero[462] = 'P2LA'
    set PAX_Dex_Name[462] = "Magnezone"
    set PAX_Dex_Hero[463] = 'EG5F'
    set PAX_Dex_Name[463] = "Lickilicky"
    set PAX_Dex_Hero[464] = 'P3CA'
    set PAX_Dex_Name[464] = "Rhyperior"
    set PAX_Dex_Hero[465] = 'P41A'
    set PAX_Dex_Name[465] = "Tangrowth"
    set PAX_Dex_Hero[466] = 'P1AA'
    set PAX_Dex_Name[466] = "Electivire"
    set PAX_Dex_Hero[467] = 'P2KA'
    set PAX_Dex_Name[467] = "Magmortar"
    set PAX_Dex_Hero[468] = 'P45A'
    set PAX_Dex_Name[468] = "Togekiss"
    set PAX_Dex_Hero[469] = 'EG5G'
    set PAX_Dex_Name[469] = "Yanmega"
    set PAX_Dex_Hero[470] = 'E03S'
    set PAX_Dex_Name[470] = "Leafleon"
    set PAX_Dex_Hero[471] = 'E03T'
    set PAX_Dex_Name[471] = "Glaceon"
    set PAX_Dex_Hero[472] = 'EG5H'
    set PAX_Dex_Name[472] = "Gliscor"
    set PAX_Dex_Hero[473] = 'P2MA'
    set PAX_Dex_Name[473] = "Mamoswine"
    set PAX_Dex_Hero[474] = 'EG5I'
    set PAX_Dex_Name[474] = "Porygon-Z"
    set PAX_Dex_Hero[475] = 'EN0C'
    set PAX_Dex_Name[475] = "Gallade"
    set PAX_Dex_Hero[476] = 'EG5J'
    set PAX_Dex_Name[476] = "Probopass"
    set PAX_Dex_Hero[477] = 'P16A'
    set PAX_Dex_Name[477] = "Dusknoir"
    set PAX_Dex_Hero[478] = 'EG5K'
    set PAX_Dex_Name[478] = "Froslass"
    set PAX_Dex_Hero[479] = 'EG5L'
    set PAX_Dex_Name[479] = "Rotom"
    set PAX_Dex_Hero[480] = 'EL02'
    set PAX_Dex_Name[480] = "Uxie"
endfunction

function PAX_Test_InitData05 takes nothing returns nothing
    set PAX_Dex_Hero[481] = 'EL03'
    set PAX_Dex_Name[481] = "Mesprit"
    set PAX_Dex_Hero[482] = 'EL04'
    set PAX_Dex_Name[482] = "Azelf"
    set PAX_Dex_Hero[483] = 'E04C'
    set PAX_Dex_Name[483] = "Dialga"
    set PAX_Dex_Hero[484] = 'E04D'
    set PAX_Dex_Name[484] = "Palkia"
    set PAX_Dex_Hero[485] = 'EL05'
    set PAX_Dex_Name[485] = "Heatran"
    set PAX_Dex_Hero[486] = 'E025'
    set PAX_Dex_Name[486] = "Regigigas"
    set PAX_Dex_Hero[487] = 'E028'
    set PAX_Dex_Name[487] = "Giratina"
    set PAX_Dex_Hero[488] = 'EL06'
    set PAX_Dex_Name[488] = "Cresselia"
    set PAX_Dex_Hero[489] = 'EG5M'
    set PAX_Dex_Name[489] = "Phione"
    set PAX_Dex_Hero[490] = 'EG5N'
    set PAX_Dex_Name[490] = "Manaphy"
    set PAX_Dex_Hero[491] = 'E023'
    set PAX_Dex_Name[491] = "Darkrai"
    set PAX_Dex_Hero[492] = 'EG5O'
    set PAX_Dex_Name[492] = "Shaymin"
    set PAX_Dex_Hero[493] = 'E02A'
    set PAX_Dex_Name[493] = "Arceus"
endfunction

function PAX_ClearGenTags takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= PAX_Gen_TagCount
        if PAX_Gen_Tags[i] != null then
            call DestroyTextTag(PAX_Gen_Tags[i])
            set PAX_Gen_Tags[i] = null
        endif
        set i = i + 1
    endloop
    set PAX_Gen_TagCount = 0
endfunction

function PAX_ClearAllFieldCreeps takes nothing returns nothing
    local group g = CreateGroup()
    local unit u = null
    // 1. Clear existing showcase units
    if PAX_Gen_Group != null then
        loop
            set u = FirstOfGroup(PAX_Gen_Group)
            exitwhen u == null
            call GroupRemoveUnit(PAX_Gen_Group, u)
            call RemoveUnit(u)
        endloop
    endif
    call PAX_ClearGenTags()
    // 2. Clear all neutral hostile creeps on the map
    call GroupEnumUnitsOfPlayer(g, Player(11), null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if not IsUnitType(u, UNIT_TYPE_HERO) then
            call RemoveUnit(u)
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set u = null
endfunction

function PAX_ShowcaseGen takes player pl, integer genNum returns nothing
    local integer startDex = 1
    local integer endDex = 151
    local integer d = 0
    local integer col = 0
    local integer row = 0
    local integer perRow = 15
    local real startX = -1248.0
    local real startY = 850.0
    local real curX = 0.0
    local real curY = 0.0
    local unit u = null
    local texttag tt = null
    local string genTitle = "Gen 1 (Kanto)"

    if genNum == 1 then
        set startDex = 1
        set endDex = 151
        set genTitle = "Gen 1 (Kanto: #001 - #151)"
    elseif genNum == 2 then
        set startDex = 152
        set endDex = 251
        set genTitle = "Gen 2 (Johto: #152 - #251)"
    elseif genNum == 3 then
        set startDex = 252
        set endDex = 386
        set genTitle = "Gen 3 (Hoenn: #252 - #386)"
    elseif genNum == 4 then
        set startDex = 387
        set endDex = 493
        set genTitle = "Gen 4 (Sinnoh: #387 - #493)"
    else
        call DisplayTimedTextToPlayer(pl, 0, 0, 5.0, "|cffff4040Usage: -gen 1, -gen 2, -gen 3, or -gen 4|r")
        return
    endif

    call PAX_ClearAllFieldCreeps()

    if PAX_Gen_Group == null then
        set PAX_Gen_Group = CreateGroup()
    endif

    set d = startDex
    loop
        exitwhen d > endDex
        if PAX_Dex_Hero[d] != 0 then
            set curX = startX + col * 165.0
            set curY = startY - row * 185.0
            set u = CreateUnit(Player(bj_PLAYER_NEUTRAL_VICTIM), PAX_Dex_Hero[d], curX, curY, 270.0)
            if u != null then
                call PauseUnit(u, true)
                call SetUnitInvulnerable(u, true)
                call GroupAddUnit(PAX_Gen_Group, u)
                if PAX_Gen_TagCount < 8000 then
                    set tt = CreateTextTag()
                    call SetTextTagPos(tt, curX, curY, 90.0)
                    call SetTextTagText(tt, "#" + I2S(d) + " " + PAX_Dex_Name[d], 0.021)
                    call SetTextTagPermanent(tt, true)
                    call SetTextTagVisibility(tt, true)
                    set PAX_Gen_Tags[PAX_Gen_TagCount] = tt
                    set PAX_Gen_TagCount = PAX_Gen_TagCount + 1
                    set tt = null
                endif
            endif
            set col = col + 1
            if col >= perRow then
                set col = 0
                set row = row + 1
            endif
        endif
        set d = d + 1
    endloop

    // Teleport hero to view the showcase
    set u = League_Hero(GetPlayerId(pl))
    if u != null and Ab_Alive(u) then
        call SetUnitPosition(u, startX + 7 * 165.0, startY + 160.0)
        call PanCameraToTimedForPlayer(pl, startX + 7 * 165.0, startY + 160.0, 0.4)
    endif
    set u = null

    call DisplayTimedTextToPlayer(pl, 0, 0, 8.0, "|cff00ffff[Showcase] " + genTitle + " spawned! (" + I2S(endDex - startDex + 1) + " Pokemon)|r")
    call DisplayTimedTextToPlayer(pl, 0, 0, 8.0, "|cffffcc00Type -clear to remove showcase models.|r")
endfunction

function PAX_FindDexByName takes string q returns integer
    local integer i = 1
    local string lowerQ = StringCase(q, false)
    loop
        exitwhen i > 493
        if StringCase(PAX_Dex_Name[i], false) == lowerQ then
            return i
        endif
        set i = i + 1
    endloop
    return 0
endfunction

function PAX_ChangeHeroToDex takes player pl, integer targetDex returns nothing
    local integer pid = GetPlayerId(pl)
    local unit oldHero = League_Hero(pid)
    local unit newHero = null
    local integer newTypeId = 0
    local real hx = 0.0
    local real hy = 0.0

    if targetDex < 1 or targetDex > 493 or PAX_Dex_Hero[targetDex] == 0 then
        call DisplayTimedTextToPlayer(pl, 0, 0, 5.0, "|cffff4040[Error] Pokemon Dex #" + I2S(targetDex) + " not found.|r")
        return
    endif

    if oldHero == null or not Ab_Alive(oldHero) then
        call DisplayTimedTextToPlayer(pl, 0, 0, 5.0, "|cffff4040[Error] You need an active living Pokemon to change.|r")
        return
    endif

    set newTypeId = PAX_Dex_Hero[targetDex]
    set hx = GetUnitX(oldHero)
    set hy = GetUnitY(oldHero)

    call DestroyEffect(AddSpecialEffect("Abilities\Spells\Human\MassTeleport\MassTeleportTarget.mdl", hx, hy))
    set Mega_EvoItem = true
    call Mega_SafeReplace(oldHero, newTypeId, bj_UNIT_STATE_METHOD_RELATIVE)
    set Mega_EvoItem = false
    set newHero = bj_lastReplacedUnit

    if newHero != null then
        // User requirement: reset to Level 1 when changed
        call SetHeroLevel(newHero, 1, false)
        call SetHeroXP(newHero, 0, false)
        call SetUnitState(newHero, UNIT_STATE_LIFE, GetUnitState(newHero, UNIT_STATE_MAX_LIFE))
        call SetUnitState(newHero, UNIT_STATE_MANA, GetUnitState(newHero, UNIT_STATE_MAX_MANA))
        if PAX_NoLevelCap then
            call SuspendHeroXP(newHero, false)
        endif
        call DisplayTimedTextToPlayer(pl, 0, 0, 6.0, "|cff00ff00[Change] Success! Transformed into #" + I2S(targetDex) + " " + PAX_Dex_Name[targetDex] + " (Level 1)!|r")
    endif

    set oldHero = null
    set newHero = null
endfunction

function PAX_TestChatHandler takes nothing returns nothing
    local player pl = GetTriggerPlayer()
    local integer pid = GetPlayerId(pl)
    local string msg = GetEventPlayerChatString()
    local string cmd = ""
    local string param = ""
    local integer targetDex = 0
    local integer lvl = 1
    local unit hero = null

    // Parse command
    if SubString(msg, 0, 3) == "-c " then
        set param = SubString(msg, 3, StringLength(msg))
        set targetDex = S2I(param)
        if targetDex == 0 then
            set targetDex = PAX_FindDexByName(param)
        endif
        call PAX_ChangeHeroToDex(pl, targetDex)

    elseif SubString(msg, 0, 8) == "-change " then
        set param = SubString(msg, 8, StringLength(msg))
        set targetDex = S2I(param)
        if targetDex == 0 then
            set targetDex = PAX_FindDexByName(param)
        endif
        call PAX_ChangeHeroToDex(pl, targetDex)

    elseif SubString(msg, 0, 5) == "-gen " then
        set param = SubString(msg, 5, StringLength(msg))
        call PAX_ShowcaseGen(pl, S2I(param))

    elseif SubString(msg, 0, 4) == "-gen" and StringLength(msg) >= 5 then
        // handles -gen1, -gen2, -gen_1, etc.
        set param = SubString(msg, 4, StringLength(msg))
        if SubString(param, 0, 1) == "_" then
            set param = SubString(param, 1, StringLength(param))
        endif
        call PAX_ShowcaseGen(pl, S2I(param))

    elseif msg == "-nolvl" or msg == "-freelvl" or msg == "-lvlcap" then
        set PAX_NoLevelCap = not PAX_NoLevelCap
        set hero = League_Hero(pid)
        if PAX_NoLevelCap then
            if hero != null then
                call SuspendHeroXP(hero, false)
            endif
            call DisplayTimedTextToPlayer(pl, 0, 0, 6.0, "|cff00ff00[Test] Level Cap is now DISABLED! All Pokemon can level up freely without gym badges.|r")
        else
            if hero != null then
                call Badge_LevelCap(hero, pid)
            endif
            call DisplayTimedTextToPlayer(pl, 0, 0, 6.0, "|cffff8800[Test] Level Cap is now ENABLED. Standard gym badge rules apply.|r")
        endif
        set hero = null

    elseif SubString(msg, 0, 5) == "-lvl " then
        set param = SubString(msg, 5, StringLength(msg))
        set lvl = S2I(param)
        set hero = League_Hero(pid)
        if hero != null and lvl >= 1 and lvl <= 100 then
            call SetHeroLevel(hero, lvl, true)
            if PAX_NoLevelCap then
                call SuspendHeroXP(hero, false)
            endif
            call DisplayTimedTextToPlayer(pl, 0, 0, 5.0, "|cff00ff00[Test] Hero level set to " + I2S(lvl) + "!|r")
        endif
        set hero = null

    elseif msg == "-clear" then
        call PAX_ClearAllFieldCreeps()
        call DisplayTimedTextToPlayer(pl, 0, 0, 5.0, "|cffffcc00[Test] Showcase cleared and field refreshed.|r")
    endif

    set pl = null
endfunction

function PAX_Test_Setup takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0

    // Initialize all 493 Pokemon Dex entries

    call ExecuteFunc("PAX_Test_InitData01")
    call ExecuteFunc("PAX_Test_InitData02")
    call ExecuteFunc("PAX_Test_InitData03")
    call ExecuteFunc("PAX_Test_InitData04")
    call ExecuteFunc("PAX_Test_InitData05")

    // Register chat events for all players 0..11
    set i = 0
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-c ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-change ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-gen", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-nolvl", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-freelvl", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-lvlcap", true)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-lvl ", false)
        call TriggerRegisterPlayerChatEvent(t, Player(i), "-clear", true)
        set i = i + 1
    endloop
    call TriggerAddAction(t, function PAX_TestChatHandler)
    set t = null
endfunction
