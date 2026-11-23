# Kích thước và đi bộ / bay của hero: Pokemon Arena v4.2b.w3x

567 hero, 233 bị đánh dấu. Tạo bằng `tools/v412/model_size_check.py` (GEMINI.md mục 13).

Cao trên màn hình = kích thước model x scale. Mục tiêu tính từ chiều cao thật của loài (PokeAPI). Scale đề xuất đưa con đó về đúng mục tiêu; vẫn phải xem trong game.

| Hero | Id | Cao thật (m) | Model cao / dài | Scale | Trên màn hình | Mục tiêu | Scale đề xuất | Di chuyển | Vấn đề |
|---|---|---|---|---|---|---|---|---|---|
| Abra | E00G | 0.9 | 92 / 115 | 0.82 | 76 | 115 | 1.25 | (default) 20 | quá nhỏ; lơ lửng sai ((default), cao 20) |
| Aerodactyl | P02A | 1.8 | 111 / 285 | 0.90 | 103 | 157 | 1.40 | (default)  | quá nhỏ |
| Aggron | EG2M | 2.1 | 236 / 394 | 0.66 | 156 | 169 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Alakazam | E00I | 1.5 | 126 / 131 | 1.13 | 142 | 145 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Altaria | EG35 | 1.1 | 132 / 211 | 1.22 | 161 | 126 |  | hover 180 | bay quá cao (180) |
| Ambipom | EG4O | 1.2 | 112 / 194 | 1.35 | 152 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Arceus | E02A | 3.2 | 209 / 171 | 1.50 | 314 | 204 | 1.00 | hover  | quá to; lơ lửng sai (hover, cao 0) |
| Ariados | EG0L | 1.1 | 93 / 339 | 1.35 | 183 | 126 | 0.95 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Armaldo | EG3F | 1.5 | 160 / 185 | 1.02 | 163 | 145 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Aron | EG2K | 0.4 | 54 / 244 | 1.35 | 132 | 80 | 0.80 | (default)  | quá to |
| Articuno | E020 | 1.7 | 276 / 289 | 0.84 | 232 | 153 | 0.55 | hover 100 | quá to |
| Azelf | EL04 | 0.3 | 137 / 137 | 1.25 | 171 | 70 | 0.50 | (default)  | quá to |
| Azumarill | EG0S | 0.8 | 236 / 363 | 0.63 | 149 | 109 | 0.45 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Azurill | EG2F | 0.2 | 84 / 319 | 1.16 | 148 | 59 | 0.45 | (default)  | quá to |
| Baltoy | P0BA | 0.5 | 37 / 48 | 1.60 | 59 | 88 | 2.00 | (default)  | quá nhỏ |
| Bastiodon | EG4B | 1.3 | 173 / 270 | 0.89 | 154 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Beautifly | EG1V | 1.0 | 106 / 158 | 1.35 | 142 | 121 |  | hover 180 | bay quá cao (180) |
| Bibarel | EG40 | 1.0 | 96 / 158 | 1.35 | 129 | 121 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Bidoof | EG3Z | 0.5 | 330 / 396 | 1.35 | 446 | 88 | 0.30 | (default)  | quá to |
| Bronzong | EG50 | 1.3 | 78 / 141 | 1.35 | 105 | 136 |  | hover 180 | bay quá cao (180) |
| Budew | EG46 | 0.2 | 129 / 78 | 0.68 | 87 | 59 | 0.45 | (default)  | quá to |
| Bulbasaur | E008 | 0.7 | 161 / 92 | 1.15 | 185 | 103 | 0.65 | (default)  | quá to |
| Burmy | EG4C | 0.2 | 75 / 40 | 1.35 | 101 | 59 | 0.80 | (default)  | quá to |
| Cacturne | EG34 | 1.3 | 131 / 136 | 1.19 | 156 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Camerupt | EG2Z | 1.9 | 179 / 286 | 0.76 | 136 | 161 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Castform | EG3G | 0.3 | 75 / 45 | 1.35 | 101 | 70 | 0.95 | (default)  | quá to |
| Celebi | PZZA | 0.6 | 22 / 23 | 1.40 | 31 | 96 | 2.00 | (default)  | quá nhỏ |
| Charizard | E00E | 1.7 | 174 / 323 | 0.96 | 167 | 153 |  | hover 180 | bay quá cao (180) |
| Chesnaught | EP0N | 1.6 | 144 / 165 | 1.65 | 237 | 149 | 1.05 | (default)  | quá to |
| Chikorita | P0NA | 0.9 | 169 / 74 | 1.00 | 169 | 115 | 0.70 | (default)  | quá to |
| Chimchar | EP09 | 0.5 | 48 / 43 | 2.80 | 134 | 88 | 1.85 | (default)  | quá to |
| Chimecho | EG3L | 0.6 | 149 / 44 | 1.00 | 149 | 96 | 0.65 | hover 180 | quá to; bay quá cao (180) |
| Chinchou | P0OA | 0.5 | 82 / 144 | 0.64 | 53 | 88 | 1.10 | (default)  | quá nhỏ |
| Chingling | EG4W | 0.2 | 98 / 84 | 0.88 | 87 | 59 | 0.60 | (default)  | quá to |
| Cleffa | EG0N | 0.3 | 30 / 34 | 1.35 | 41 | 70 | 2.00 | (default)  | quá nhỏ |
| Cloyster | E01F | 1.5 | 150 / 172 | 0.66 | 99 | 145 | 0.95 | (default)  | quá nhỏ |
| Corphish | EG3C | 0.6 | 61 / 263 | 1.35 | 142 | 96 | 0.90 | (default)  | quá to |
| Cradily | P0TA | 1.5 | 211 / 87 | 1.20 | 253 | 145 | 0.70 | (default)  | quá to |
| Crawdaunt | EG3D | 1.1 | 118 / 321 | 1.35 | 173 | 126 | 1.00 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Croconaw | EP01 | 1.1 | 113 / 96 | 1.05 | 118 | 126 | 1.23 | (default)  | khác số đã chốt (1.20-1.25) |
| Darkrai | E023 | 1.5 | 129 / 136 | 1.50 | 193 | 145 |  | hover 20 | lơ lửng sai (hover, cao 20) |
| Delibird | EG1G | 0.9 | 92 / 321 | 1.26 | 162 | 115 | 0.90 | (default)  | quá to |
| Delphox | EP0Q | 1.5 | 178 / 177 | 1.20 | 213 | 145 | 0.80 | (default)  | quá to |
| Deoxys | E027 | 1.7 | 278 / 384 | 0.80 | 222 | 153 | 0.55 | hover  | quá to; lơ lửng sai (hover, cao 0) |
| Dewgong | P10A | 1.7 | 75 / 207 | 1.15 | 95 | 153 | 1.85 | (default)  | quá nhỏ |
| Dialga | E04C | 5.4 | 154 / 238 | 1.50 | 231 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Diglett | P11A | 0.2 | 36 / 51 | 1.10 | 40 | 59 | 1.65 | (default)  | quá nhỏ |
| Dodrio | EG0A | 1.8 | 200 / 96 | 0.70 | 140 | 157 |  | hover 180 | bay quá cao (180) |
| Doduo | EG09 | 1.4 | 146 / 70 | 0.58 | 85 | 141 | 0.95 | (default)  | quá nhỏ |
| Donphan | EG1K | 1.1 | 124 / 370 | 1.22 | 181 | 126 | 0.95 | hover 180 | khác số đã chốt (0.95-0.95); lơ lửng sai (hover, cao 180) |
| Doublade | P4PA | 0.8 | 150 / 236 | 1.00 | 150 | 109 | 0.75 | (default)  | quá to |
| Drapion | EG5A | 1.3 | 81 / 309 | 1.35 | 167 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Drifblim | EG4Q | 1.2 | 144 / 264 | 0.98 | 141 | 131 |  | hover 180 | bay quá cao (180) |
| Drifloon | EG4P | 0.4 | 72 / 264 | 1.30 | 137 | 80 | 0.75 | (default)  | quá to |
| Dugtrio | P14A | 0.7 | 84 / 122 | 0.70 | 59 | 103 | 1.20 | (default)  | quá nhỏ |
| Dustox | EG1X | 1.2 | 123 / 152 | 1.25 | 154 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Eevee | E03A | 0.3 | 4 / 5 | 22.00 | 78 | 70 |  | (default)  | model lạ (cao 3) |
| Ekans | P18A | 2.0 | 235 / 22 | 1.30 | 305 | 165 | 0.70 | (default)  | quá to |
| Electrike | P1BA | 0.6 | 64 / 109 | 1.05 | 67 | 96 | 1.50 | (default)  | quá nhỏ |
| Electrode | E01X | 1.2 | 115 / 115 | 0.73 | 84 | 131 | 1.15 | hover 30 | quá nhỏ; lơ lửng sai (hover, cao 30) |
| Emboar | EP0K | 1.6 | 173 / 322 | 1.50 | 260 | 149 | 0.85 | (default)  | quá to |
| Empoleon | EP0E | 1.7 | 267 / 213 | 0.95 | 254 | 153 | 0.55 | (default)  | quá to |
| Exeggcute | E02U | 0.4 | 189 / 463 | 0.70 | 132 | 80 | 0.40 | (default)  | quá to |
| Exploud | EG2C | 1.5 | 151 / 188 | 0.95 | 143 | 145 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Fearow | EG01 | 1.2 | 81 / 278 | 1.35 | 150 | 131 |  | hover 180 | bay quá cao (180) |
| Feebas | P1FA | 0.6 | 62 / 71 | 1.05 | 65 | 96 | 1.55 | (default)  | quá nhỏ |
| Feraligatr | EP02 | 2.3 | 205 / 296 | 1.50 | 308 | 176 | 1.17 | (default)  | khác số đã chốt (1.15-1.20) |
| Flareon | E038 | 0.9 | 283 / 220 | 1.15 | 325 | 115 | 0.40 | (default)  | quá to |
| Forretress | EG16 | 1.2 | 163 / 332 | 1.00 | 163 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Froslass | EG5K | 1.3 | 135 / 240 | 1.10 | 149 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Furret | EG0H | 1.8 | 47 / 175 | 1.35 | 95 | 157 | 2.00 | hover 180 | quá nhỏ; lơ lửng sai (hover, cao 180) |
| Gabite | P1IA | 1.4 | 95 / 135 | 1.00 | 95 | 141 | 1.50 | (default)  | quá nhỏ |
| Gardevoir | EN0B | 1.6 | 119 / 99 | 1.20 | 143 | 149 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Gastly | E02G | 1.3 | 40 / 42 | 1.35 | 54 | 136 | 2.00 | (default) 20 | quá nhỏ |
| Gengar | E01G | 1.5 | 156 / 204 | 0.73 | 114 | 145 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Gible | P1NA | 0.7 | 63 / 69 | 1.00 | 63 | 103 | 1.60 | (default)  | quá nhỏ |
| Girafarig | EG14 | 1.5 | 158 / 307 | 0.54 | 85 | 145 | 0.90 | (default)  | quá nhỏ |
| Giratina | E028 | 4.5 | 189 / 264 | 1.50 | 283 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Glalie | EG3N | 1.5 | 152 / 175 | 1.07 | 163 | 145 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Gliscor | EG5H | 2.0 | 327 / 378 | 0.49 | 160 | 165 |  | hover 180 | bay quá cao (180) |
| Golbat | E048 | 1.6 | 132 / 314 | 0.66 | 87 | 149 | 1.15 | hover 40 | quá nhỏ |
| Gorebyss | EG3T | 1.8 | 60 / 168 | 1.35 | 91 | 157 | 2.00 | hover 180 | quá nhỏ; lơ lửng sai (hover, cao 180) |
| Greninja | EP0T | 1.5 | 160 / 185 | 1.25 | 201 | 145 | 0.90 | (default)  | quá to |
| Grotle | EP07 | 1.1 | 61 / 90 | 3.00 | 182 | 126 | 2.00 | (default)  | quá to |
| Grovyle | EN04 | 0.9 | 139 / 126 | 1.20 | 167 | 115 | 0.85 | (default)  | quá to |
| Hariyama | EG2E | 2.3 | 100 / 192 | 1.35 | 135 | 176 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Haunter | E02H | 1.6 | 90 / 125 | 1.04 | 93 | 149 | 1.65 | (default) 20 | quá nhỏ |
| Hippowdon | EG58 | 2.0 | 73 / 173 | 1.35 | 99 | 165 | 2.00 | hover 180 | quá nhỏ; lơ lửng sai (hover, cao 180) |
| Honchkrow | EG4T | 0.9 | 75 / 111 | 1.35 | 101 | 115 |  | hover 180 | bay quá cao (180) |
| Honedge | P4OA | 0.8 | 187 / 180 | 1.00 | 187 | 109 | 0.60 | (default)  | quá to |
| Hoopa | EL0G | 0.5 | 104 / 173 | 1.25 | 130 | 88 | 0.85 | (default)  | quá to |
| Huntail | EG3S | 1.7 | 49 / 170 | 1.35 | 92 | 153 | 2.00 | hover 180 | quá nhỏ; lơ lửng sai (hover, cao 180) |
| Hydreigon | P1YA | 1.8 | 183 / 186 | 1.20 | 220 | 157 | 0.85 | (default)  | quá to |
| Illumise | EG2S | 0.6 | 77 / 289 | 1.35 | 156 | 96 | 0.85 | (default)  | quá to |
| Incineroar | EP0W | 1.8 | 168 / 332 | 1.60 | 269 | 157 | 0.95 | (default)  | quá to |
| Jigglypuff | P20A | 0.5 | 66 / 71 | 0.75 | 50 | 88 | 1.35 | (default)  | quá nhỏ |
| Jumpluff | EG0V | 0.8 | 108 / 127 | 1.35 | 145 | 109 |  | hover 180 | bay quá cao (180) |
| Kadabra | E00H | 1.3 | 101 / 141 | 1.27 | 129 | 136 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Kingdra | P24A | 1.8 | 104 / 90 | 1.05 | 110 | 157 | 1.50 | (default)  | quá nhỏ |
| Kingler | E03D | 1.3 | 94 / 117 | 0.93 | 87 | 136 | 1.45 | (default)  | quá nhỏ |
| Kirlia | EN0A | 0.8 | 68 / 56 | 1.20 | 82 | 109 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Koffing | E01V | 0.6 | 151 / 258 | 1.41 | 213 | 96 | 0.65 | (default) 25 | quá to |
| Kricketot | EG41 | 0.3 | 75 / 46 | 1.35 | 101 | 70 | 0.95 | (default)  | quá to |
| Kyogre | P26A | 4.5 | 55 / 240 | 1.30 | 125 | 230 | 2.00 | (default)  | quá nhỏ |
| Lairon | EG2L | 0.9 | 103 / 339 | 1.35 | 183 | 115 | 0.85 | (default)  | quá to |
| Lanturn | P28A | 1.2 | 112 / 240 | 0.70 | 79 | 131 | 1.15 | (default)  | quá nhỏ |
| Ledian | EG0J | 1.4 | 141 / 224 | 1.35 | 191 | 141 | 1.00 | hover 180 | quá to; bay quá cao (180) |
| Lickilicky | EG5F | 1.7 | 216 / 199 | 0.71 | 154 | 153 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Lickitung | EG0D | 1.2 | 120 / 246 | 0.74 | 88 | 131 | 1.10 | (default)  | quá nhỏ |
| Linoone | EG1S | 0.5 | 73 / 344 | 1.35 | 186 | 88 | 0.65 | (default)  | quá to |
| Lombre | P2EA | 1.2 | 89 / 119 | 0.90 | 80 | 131 | 1.50 | (default)  | quá nhỏ |
| Lopunny | EG4S | 1.2 | 220 / 386 | 0.74 | 163 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Lotad | P2FA | 0.5 | 50 / 100 | 0.85 | 42 | 88 | 1.75 | (default)  | quá nhỏ |
| Lugia | E022 | 5.2 | 181 / 190 | 1.75 | 317 | 230 | 1.25 | hover 50 | quá to |
| Lugia | EG1O | 5.2 | 273 / 411 | 0.76 | 207 | 230 |  | hover 180 | bay quá cao (180) |
| Lumineon | EG5D | 1.2 | 120 / 155 | 1.20 | 145 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Lunatone | EG38 | 1.0 | 101 / 94 | 1.35 | 136 | 121 |  | hover 180 | bay quá cao (180) |
| Luxray | EG45 | 1.4 | 201 / 258 | 0.81 | 162 | 141 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Magearna | EL0L | 1.0 | 64 / 151 | 1.20 | 77 | 121 | 1.90 | (default)  | quá nhỏ |
| Magnemite | P4WA | 0.3 | 45 / 76 | 1.00 | 45 | 70 | 1.55 | (default)  | quá nhỏ |
| Magneton | E032 | 1.0 | 83 / 144 | 0.99 | 83 | 121 | 1.45 | (default)  | quá nhỏ |
| Magnezone | P2LA | 1.2 | 63 / 109 | 1.20 | 75 | 131 | 2.00 | (default)  | quá nhỏ |
| Makuhita | EG2D | 1.0 | 70 / 95 | 1.19 | 83 | 121 | 1.75 | (default)  | quá nhỏ |
| Manaphy | EG5N | 0.3 | 155 / 94 | 1.17 | 181 | 70 | 0.45 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Mantine | EG1H | 2.1 | 54 / 232 | 1.35 | 126 | 169 |  | hover 180 | bay quá cao (180) |
| Mantyke | EG5E | 1.0 | 49 / 97 | 1.35 | 67 | 121 | 2.00 | (default)  | quá nhỏ |
| Marshadow | EL0M | 0.7 | 148 / 104 | 1.20 | 177 | 103 | 0.70 | (default)  | quá to |
| Marshtomp | EP04 | 0.7 | 127 / 140 | 1.20 | 152 | 103 | 0.80 | (default)  | quá to |
| Masquerain | EG26 | 0.8 | 77 / 116 | 1.35 | 104 | 109 |  | hover 180 | bay quá cao (180) |
| Mawile | EG2J | 0.6 | 128 / 321 | 1.09 | 140 | 96 | 0.75 | (default)  | quá to |
| Medicham | EG2O | 1.3 | 206 / 188 | 0.77 | 159 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Mesprit | EL03 | 0.3 | 132 / 154 | 1.25 | 165 | 70 | 0.55 | (default)  | quá to |
| Mew | E024 | 0.4 | 191 / 191 | 5.00 | 955 | 80 | 0.40 | hover 50 | quá to; lơ lửng sai (hover, cao 50) |
| Mewtwo | E026 | 2.0 | 62 / 67 | 2.50 | 156 | 165 |  | hover  | lơ lửng sai (hover, cao 0) |
| Mightyena | EG1Q | 1.0 | 168 / 250 | 0.90 | 152 | 121 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Milotic | P2TA | 6.2 | 531 / 124 | 1.00 | 531 | 230 | 0.45 | (default)  | quá to |
| Miltank | EG1N | 1.2 | 1079 / 1254 | 0.35 | 378 | 131 | 0.95 | hover 180 | model lạ (cao 1078); khác số đã chốt (0.90-1.00); lơ lửng sai (hover, cao 180) |
| Minun | EG2Q | 0.4 | 95 / 290 | 1.35 | 157 | 80 | 0.70 | (default)  | quá to |
| Moltres | E021 | 2.0 | 260 / 315 | 1.40 | 364 | 165 | 0.65 | hover 20 | quá to |
| Muk | EG0C | 1.2 | 212 / 384 | 0.71 | 151 | 131 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Natu | EG0P | 0.2 | 93 / 110 | 0.99 | 92 | 59 | 0.65 | (default)  | quá to |
| Nidoqueen | EG04 | 1.3 | 162 / 321 | 0.89 | 144 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Nincada | P2XA | 0.5 | 35 / 79 | 0.86 | 30 | 88 | 2.00 | (default)  | quá nhỏ |
| Ninjask | P2YA | 0.8 | 59 / 119 | 1.05 | 62 | 109 | 1.85 | (default)  | quá nhỏ |
| Octillery | EG1F | 0.9 | 92 / 139 | 1.35 | 124 | 115 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Pachirisu | EG4H | 0.4 | 104 / 123 | 1.21 | 126 | 80 | 0.75 | (default)  | quá to |
| Palkia | E04D | 4.2 | 156 / 296 | 1.50 | 235 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Paras | EG05 | 0.3 | 100 / 147 | 1.10 | 110 | 70 | 0.70 | (default)  | quá to |
| Parasect | EG06 | 1.0 | 123 / 114 | 1.35 | 166 | 121 | 1.00 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Phione | EG5M | 0.4 | 72 / 112 | 1.35 | 97 | 80 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Pidgeot | E00D | 1.5 | 86 / 198 | 1.34 | 115 | 145 |  | hover 180 | bay quá cao (180) |
| Pidgeotto | E00C | 1.1 | 82 / 178 | 1.23 | 100 | 126 |  | hover 180 | bay quá cao (180) |
| Pidgey | E00B | 0.3 | 73 / 166 | 1.12 | 81 | 70 |  | hover 180 | bay quá cao (180) |
| Pignite | EP0J | 1.0 | 131 / 341 | 1.70 | 232 | 121 | 0.90 | (default)  | quá to |
| Plusle | EG2P | 0.4 | 95 / 290 | 1.35 | 157 | 80 | 0.70 | (default)  | quá to |
| Poliwag | E012 | 0.6 | 69 / 162 | 0.85 | 58 | 96 | 1.40 | (default)  | quá nhỏ |
| Poliwag | P4YA | 0.6 | 69 / 162 | 0.80 | 55 | 96 | 1.40 | (default)  | quá nhỏ |
| Porygon | P35A | 0.8 | 77 / 124 | 0.80 | 61 | 109 | 1.40 | (default)  | quá nhỏ |
| Porygon-Z | EG5I | 0.9 | 97 / 102 | 1.35 | 131 | 115 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Probopass | EG5J | 1.4 | 142 / 193 | 0.95 | 135 | 141 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Quagsire | EG11 | 1.4 | 95 / 308 | 1.35 | 166 | 141 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Ralts | EN09 | 0.4 | 245 / 258 | 0.50 | 123 | 80 | 0.35 | (default) 20 | quá to; lơ lửng sai ((default), cao 20) |
| Rampardos | EG49 | 1.6 | 146 / 147 | 0.97 | 141 | 149 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Rapidash | E01H | 1.7 | 224 / 229 | 1.24 | 278 | 153 | 0.70 | (default)  | quá to |
| Rattata | E00T | 0.3 | 73 / 129 | 1.35 | 99 | 70 | 0.95 | (default)  | quá to |
| Rayquaza | E029 | 7.0 | 294 / 59 | 3.00 | 880 | 230 | 0.80 | hover 130 | quá to; bay quá cao (130) |
| Regigigas | E025 | 3.7 | 296 / 452 | 0.75 | 222 | 218 |  | hover  | lơ lửng sai (hover, cao 0) |
| Relicanth | EG3U | 1.0 | 177 / 249 | 0.88 | 156 | 121 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Remoraid | EG1E | 0.6 | 47 / 59 | 1.35 | 63 | 96 | 2.00 | (default)  | quá nhỏ |
| Rhyhorn | P50A | 1.0 | 98 / 152 | 0.80 | 79 | 121 | 1.25 | (default)  | quá nhỏ |
| Roselia | EG2T | 0.3 | 128 / 158 | 1.29 | 166 | 70 | 0.55 | (default)  | quá to |
| Roserade | EG47 | 0.9 | 123 / 118 | 1.35 | 166 | 115 | 0.95 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Rotom | EG5L | 0.3 | 86 / 112 | 1.35 | 117 | 70 | 0.80 | hover 180 | quá to; bay quá cao (180) |
| Seadra | P3GA | 1.2 | 88 / 92 | 0.95 | 84 | 131 | 1.50 | (default)  | quá nhỏ |
| Seaking | EG0F | 1.3 | 83 / 141 | 1.35 | 113 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Seel | P3HA | 1.1 | 70 / 117 | 1.15 | 81 | 126 | 1.80 | (default)  | quá nhỏ |
| Serperior | EP0H | 3.3 | 448 / 322 | 1.30 | 582 | 207 | 0.45 | (default)  | quá to |
| Servine | EP0G | 0.8 | 256 / 343 | 1.20 | 307 | 109 | 0.45 | (default)  | quá to |
| Seviper | EG37 | 2.7 | 333 / 59 | 0.43 | 143 | 189 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Shaymin | EG5O | 0.2 | 56 / 83 | 1.35 | 75 | 59 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Shelgon | EN0E | 1.1 | 110 / 109 | 0.80 | 88 | 126 | 1.15 | (default)  | quá nhỏ |
| Shellos | EG4M | 0.3 | 75 / 51 | 1.35 | 101 | 70 | 0.95 | (default)  | quá to |
| Shiftry | EG20 | 1.3 | 75 / 80 | 1.35 | 101 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Shroomish | P3LA | 0.4 | 51 / 67 | 1.00 | 51 | 80 | 1.55 | (default)  | quá nhỏ |
| Shuckle | EG1A | 0.6 | 157 / 221 | 1.35 | 212 | 96 | 0.60 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Sirfetch'd | P3MA | 0.8 | 159 / 93 | 1.25 | 198 | 109 | 0.70 | (default)  | quá to |
| Skarmory | EG1I | 1.7 | 65 / 93 | 1.35 | 87 | 153 | 2.00 | hover 180 | quá nhỏ; bay quá cao (180) |
| Slaking | EG29 | 2.0 | 254 / 491 | 0.59 | 150 | 165 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Slowpoke | P3PA | 1.2 | 123 / 402 | 0.50 | 80 | 131 | 0.80 | (default)  | quá nhỏ |
| Snivy | EP0F | 0.6 | 160 / 189 | 1.20 | 192 | 96 | 0.60 | (default)  | quá to |
| Snubbull | P3VA | 0.6 | 61 / 75 | 1.00 | 61 | 96 | 1.55 | (default)  | quá nhỏ |
| Solrock | EG39 | 1.2 | 146 / 160 | 1.18 | 173 | 131 |  | hover 180 | bay quá cao (180) |
| Spinda | EG32 | 1.1 | 51 / 106 | 1.35 | 69 | 126 | 2.00 | (default)  | quá nhỏ |
| Spiritomb | EG54 | 1.0 | 144 / 150 | 1.15 | 165 | 121 | 0.85 | hover 180 | quá to; lơ lửng sai (hover, cao 180) |
| Stantler | EG1L | 1.4 | 174 / 170 | 0.51 | 89 | 141 | 0.80 | (default)  | quá nhỏ |
| Staraptor | EG3Y | 1.2 | 118 / 375 | 1.35 | 203 | 131 | 0.85 | hover 180 | quá to; bay quá cao (180) |
| Starmie | E04M | 1.1 | 85 / 141 | 1.00 | 85 | 126 | 1.50 | (default)  | quá nhỏ |
| Steelix | E03V | 9.2 | 101 / 551 | 1.45 | 319 | 230 | 0.90 | (default)  | khác số đã chốt (0.90-0.90) |
| Sunflora | EG0Y | 0.8 | 79 / 141 | 1.35 | 106 | 109 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Surskit | EG25 | 0.5 | 234 / 209 | 0.52 | 122 | 88 | 0.40 | (default)  | quá to |
| Swalot | EG2V | 1.7 | 75 / 75 | 1.35 | 101 | 153 | 2.00 | (default)  | quá nhỏ |
| Swinub | P3ZA | 0.4 | 53 / 82 | 1.00 | 53 | 80 | 1.50 | (default)  | quá nhỏ |
| Sylveon | E03X | 1.0 | 111 / 206 | 1.48 | 165 | 121 | 1.10 | (default)  | quá to |
| Taillow | EG21 | 0.3 | 75 / 98 | 1.35 | 101 | 70 | 0.95 | (default)  | quá to |
| Tangela | P40A | 1.0 | 133 / 139 | 0.63 | 84 | 121 | 0.90 | (default)  | quá nhỏ |
| Tentacool | E02D | 0.9 | 63 / 141 | 1.20 | 76 | 115 | 1.85 | hover 45 | quá nhỏ; lơ lửng sai (hover, cao 45) |
| Tentacruel | E01I | 1.6 | 103 / 146 | 1.20 | 123 | 149 |  | hover 50 | lơ lửng sai (hover, cao 50) |
| Tepig | EP0I | 0.5 | 73 / 195 | 1.80 | 140 | 88 | 1.15 | (default)  | quá to |
| Togekiss | P45A | 1.5 | 146 / 320 | 0.50 | 73 | 145 | 1.00 | (default)  | quá nhỏ |
| Torkoal | P49A | 0.5 | 130 / 284 | 1.20 | 156 | 88 | 0.70 | (default)  | quá to |
| Torterra | EP08 | 2.2 | 88 / 117 | 5.00 | 440 | 172 | 1.95 | (default)  | quá to |
| Tropius | EG3K | 2.0 | 300 / 338 | 0.49 | 147 | 165 |  | hover 180 | bay quá cao (180) |
| Umbreon | E03I | 1.0 | 8 / 11 | 1.15 | 10 | 121 | 2.00 | (default)  | model lạ (cao 8); quá nhỏ |
| Uxie | EL02 | 0.3 | 131 / 138 | 1.25 | 163 | 70 | 0.55 | (default)  | quá to |
| Venomoth | EG08 | 1.5 | 114 / 290 | 0.95 | 110 | 145 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Vespiquen | EG4G | 1.2 | 100 / 113 | 1.35 | 135 | 131 |  | hover 180 | bay quá cao (180) |
| Vibrava | P4FA | 1.1 | 40 / 55 | 2.00 | 80 | 126 | 2.00 | (default)  | quá nhỏ |
| Victini | EL07 | 0.4 | 112 / 82 | 1.15 | 128 | 80 | 0.70 | (default)  | quá to |
| Vileplume | P4GA | 1.2 | 116 / 194 | 0.60 | 70 | 131 | 1.15 | (default)  | quá nhỏ |
| Volbeat | EG2R | 0.7 | 97 / 287 | 1.28 | 147 | 103 | 0.90 | (default)  | quá to |
| Voltorb | E01D | 0.5 | 66 / 66 | 1.36 | 90 | 88 |  | hover 20 | lơ lửng sai (hover, cao 20) |
| Vulpix | E04O | 0.6 | 6 / 8 | 2.00 | 11 | 96 | 2.00 | (default)  | model lạ (cao 5); quá nhỏ |
| Wailmer | EG2W | 2.0 | 81 / 146 | 1.16 | 93 | 165 | 2.00 | (default)  | quá nhỏ |
| Wailord | EG2X | 14.5 | 97 / 235 | 1.35 | 131 | 230 | 2.00 | hover 180 | quá nhỏ; lơ lửng sai (hover, cao 180) |
| Walrein | EG3Q | 1.4 | 154 / 321 | 0.95 | 147 | 141 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Weezing | E019 | 1.2 | 156 / 258 | 1.19 | 186 | 131 | 0.85 | (default) 25 | quá to |
| Wurmple | EG1T | 0.3 | 74 / 95 | 1.35 | 100 | 70 | 0.95 | (default)  | quá to |
| Wynaut | P4KA | 0.6 | 65 / 102 | 1.00 | 65 | 96 | 1.50 | (default)  | quá nhỏ |
| Xatu | EG0Q | 1.5 | 53 / 56 | 1.35 | 72 | 145 | 2.00 | hover 180 | quá nhỏ; bay quá cao (180) |
| Yanmega | EG5G | 1.9 | 73 / 322 | 1.35 | 174 | 161 |  | hover 180 | bay quá cao (180) |
| Zangoose | EG36 | 1.3 | 149 / 321 | 1.00 | 149 | 136 |  | hover 180 | lơ lửng sai (hover, cao 180) |
| Zapdos | E03J | 1.6 | 169 / 262 | 1.47 | 249 | 149 | 0.90 | hover 50 | quá to |
| Zigzagoon | EG1R | 0.4 | 66 / 279 | 1.35 | 151 | 80 | 0.70 | (default)  | quá to |
| Abomasnow | P00A | 2.2 | 147 / 253 | 1.08 | 159 | 172 |  | (default)  | ổn |
| Absol | EN0K | 1.2 | 123 / 134 | 1.10 | 135 | 131 |  | (default)  | ổn |
| Aegislash | P4QA | 1.7 | 154 / 321 | 1.10 | 169 | 153 |  | (default)  | ổn |
| Aipom | EG0W | 0.8 | 79 / 121 | 1.13 | 90 | 109 |  | (default)  | ổn |
| Alolan-Geodude | P03A | 0.4 | 46 / 202 | 1.00 | 81 | 80 |  | (default)  | ổn |
| Alolan-Golem | P04A | 1.7 | 158 / 150 | 0.85 | 134 | 153 |  | (default)  | ổn |
| Alolan-Graveler | P05A | 1.0 | 101 / 262 | 0.85 | 89 | 121 |  | (default)  | ổn |
| Alolan-Raichu | P06A | 0.7 | 80 / 243 | 1.10 | 107 | 103 |  | (default)  | ổn |
| Alolan-Sandshrew | P4MA | 0.7 | 91 / 70 | 1.00 | 91 | 103 |  | (default)  | ổn |
| Alolan-Sandslash | P4NA | 1.2 | 122 / 105 | 0.90 | 110 | 131 |  | (default)  | ổn |
| Altaria | P07A | 1.1 | 132 / 211 | 1.00 | 132 | 126 |  | (default)  | ổn |
| Ampharos | P08A | 1.4 | 125 / 100 | 1.00 | 125 | 141 |  | (default)  | ổn |
| Anorith | EG3E | 0.7 | 70 / 128 | 1.35 | 95 | 103 |  | (default)  | ổn |
| Arbok | P09A | 3.5 | 271 / 81 | 1.00 | 271 | 212 |  | (default)  | ổn |
| Arcanine | E01C | 1.9 | 136 / 225 | 0.99 | 135 | 161 |  | (default)  | ổn |
| Bagon | EN0D | 0.6 | 76 / 52 | 1.09 | 83 | 96 |  | (default)  | ổn |
| Banette | EG3J | 1.1 | 75 / 80 | 1.35 | 101 | 126 |  | (default)  | ổn |
| Barboach | EG3A | 0.4 | 75 / 142 | 1.35 | 101 | 80 |  | (default)  | ổn |
| Bayleef | P0CA | 1.2 | 127 / 125 | 1.20 | 152 | 131 |  | (default)  | ổn |
| Beedrill | E02K | 1.0 | 122 / 141 | 1.30 | 159 | 121 |  | (default)  | ổn |
| Beldum | EN0G | 0.6 | 112 / 48 | 0.76 | 85 | 96 |  | (default)  | ổn |
| Bellossom | P0EA | 0.4 | 204 / 196 | 0.50 | 102 | 80 |  | (default)  | ổn |
| Bellsprout | E02B | 0.7 | 68 / 61 | 1.47 | 99 | 103 |  | (default)  | ổn |
| Bisharp | P4SA | 1.6 | 166 / 321 | 0.85 | 142 | 149 |  | (default)  | ổn |
| Blastoise | E000 | 1.6 | 190 / 220 | 0.71 | 135 | 149 |  | (default)  | ổn |
| Blaziken | EN02 | 1.9 | 76 / 75 | 2.00 | 153 | 161 |  | (default)  | ổn |
| Blissey | P0GA | 1.5 | 63 / 75 | 1.80 | 114 | 145 |  | (default)  | ổn |
| Bonsly | P0HA | 0.5 | 95 / 64 | 1.00 | 95 | 88 |  | (default)  | ổn |
| Braixen | EP0P | 1.0 | 122 / 108 | 1.25 | 152 | 121 |  | (default)  | ổn |
| Breloom | P0IA | 1.2 | 193 / 259 | 0.60 | 116 | 131 |  | (default)  | ổn |
| Bronzor | EG4Z | 0.5 | 49 / 156 | 1.35 | 84 | 88 |  | (default)  | ổn |
| Buizel | EG4I | 0.7 | 75 / 125 | 1.35 | 101 | 103 |  | (default)  | ổn |
| Buneary | EG4R | 0.4 | 120 / 258 | 0.78 | 93 | 80 |  | (default)  | ổn |
| Butterfree | E01Q | 1.1 | 103 / 138 | 1.30 | 134 | 126 |  | (default)  | ổn |
| Buzzwole | P0JA | 2.4 | 293 / 312 | 0.70 | 205 | 179 |  | (default)  | ổn |
| Cacnea | EG33 | 0.4 | 74 / 139 | 1.22 | 90 | 80 |  | (default)  | ổn |
| Carnivine | EG5B | 1.4 | 75 / 91 | 1.35 | 101 | 141 |  | (default)  | ổn |
| Carvanha | P0KA | 0.8 | 126 / 141 | 0.70 | 88 | 109 |  | (default)  | ổn |
| Cascoon | EG1W | 0.7 | 75 / 88 | 1.35 | 101 | 103 |  | (default)  | ổn |
| Caterpie | E01N | 0.3 | 52 / 141 | 1.50 | 85 | 70 |  | (default)  | ổn |
| Chandelure | P0LA | 1.0 | 133 / 274 | 1.20 | 159 | 121 |  | (default)  | ổn |
| Chansey | P0MA | 1.1 | 104 / 144 | 0.90 | 93 | 126 |  | (default)  | ổn |
| Charmander | E003 | 0.6 | 72 / 94 | 1.42 | 102 | 96 |  | (default)  | ổn |
| Charmeleon | E007 | 1.1 | 109 / 130 | 1.26 | 137 | 126 |  | (default)  | ổn |
| Chatot | EG53 | 0.5 | 75 / 68 | 1.35 | 101 | 88 |  | (default)  | ổn |
| Cherrim | EG4L | 0.5 | 75 / 60 | 1.35 | 101 | 88 |  | (default)  | ổn |
| Cherubi | EG4K | 0.4 | 75 / 65 | 1.35 | 101 | 80 |  | (default)  | ổn |
| Chespin | EP0L | 0.4 | 68 / 54 | 1.20 | 81 | 80 |  | (default)  | ổn |
| Clamperl | EG3R | 0.4 | 73 / 75 | 1.35 | 98 | 80 |  | (default)  | ổn |
| Claydol | P0PA | 1.5 | 94 / 88 | 1.10 | 104 | 145 |  | (default)  | ổn |
| Clefable | P0QA | 1.3 | 120 / 157 | 0.80 | 96 | 136 |  | (default)  | ổn |
| Clefairy | P0RA | 0.6 | 74 / 89 | 1.00 | 74 | 96 |  | (default)  | ổn |
| Combee | EG4F | 0.3 | 50 / 132 | 1.35 | 71 | 70 |  | (default)  | ổn |
| Combusken | EN01 | 0.9 | 88 / 90 | 1.30 | 115 | 115 |  | (default)  | ổn |
| Corsola | EG1D | 0.6 | 60 / 64 | 1.35 | 81 | 96 |  | (default)  | ổn |
| Cranidos | EG48 | 0.9 | 88 / 68 | 1.02 | 90 | 115 |  | (default)  | ổn |
| Cresselia | EL06 | 1.5 | 129 / 216 | 1.20 | 154 | 145 |  | (default)  | ổn |
| Croagunk | P0UA | 0.7 | 89 / 129 | 1.00 | 89 | 103 |  | (default)  | ổn |
| Crobat | E049 | 1.8 | 240 / 451 | 0.67 | 161 | 157 |  | hover -50 | ổn |
| Cubone | P0VA | 0.4 | 62 / 64 | 1.20 | 74 | 80 |  | (default)  | ổn |
| Cyndaquil | P0WA | 0.5 | 79 / 110 | 1.00 | 79 | 88 |  | (default)  | ổn |
| Darmanitan | P0XA | 1.3 | 147 / 363 | 0.80 | 117 | 136 |  | (default)  | ổn |
| Darumaka | P0YA | 0.6 | 104 / 148 | 0.75 | 78 | 96 |  | (default)  | ổn |
| Deino | P0ZA | 0.8 | 115 / 109 | 0.90 | 104 | 109 |  | (default)  | ổn |
| Delcatty | EG2I | 1.1 | 75 / 55 | 1.35 | 101 | 126 |  | (default)  | ổn |
| Diancie | EL0F | 0.7 | 70 / 43 | 1.25 | 87 | 103 |  | (default)  | ổn |
| Ditto | P12A | 0.3 | 48 / 63 | 1.10 | 53 | 70 |  | (default)  | ổn |
| Dragonair | E01T | 4.0 | 185 / 722 | 0.90 | 260 | 225 |  | (default)  | ổn |
| Dragonite | E01K | 2.2 | 216 / 412 | 0.90 | 194 | 172 |  | hover 40 | ổn |
| Dratini | E01S | 1.8 | 133 / 397 | 0.90 | 143 | 157 |  | (default)  | ổn |
| Drowzee | P13A | 1.0 | 102 / 143 | 1.00 | 102 | 121 |  | (default)  | ổn |
| Dunsparce | EG17 | 1.5 | 81 / 321 | 1.35 | 173 | 145 |  | (default)  | ổn |
| Dusclops | P15A | 1.6 | 143 / 290 | 1.00 | 143 | 149 |  | (default)  | ổn |
| Dusknoir | P16A | 2.2 | 151 / 280 | 1.00 | 151 | 172 |  | (default)  | ổn |
| Duskull | P17A | 0.8 | 82 / 126 | 1.00 | 82 | 109 |  | (default)  | ổn |
| Eevee | P4VA | 0.3 | 54 / 72 | 1.20 | 65 | 70 |  | (default)  | ổn |
| Electabuzz | P19A | 1.1 | 113 / 201 | 1.15 | 130 | 126 |  | (default)  | ổn |
| Electivire | P1AA | 1.8 | 117 / 170 | 1.10 | 129 | 157 |  | (default)  | ổn |
| Elekid | P1CA | 0.6 | 87 / 116 | 1.00 | 87 | 96 |  | (default)  | ổn |
| Entei | P1DA | 2.1 | 111 / 199 | 1.30 | 145 | 169 |  | (default)  | ổn |
| Espeon | E03H | 0.9 | 170 / 250 | 0.80 | 136 | 115 |  | (default)  | ổn |
| Eternatus | EL0O | 20.0 | 285 / 513 | 0.65 | 185 | 230 |  | (default)  | ổn |
| Exeggutor | E02W | 2.0 | 158 / 235 | 0.97 | 154 | 165 |  | (default)  | ổn |
| Farfetch'd | P1EA | 0.8 | 74 / 121 | 1.10 | 81 | 109 |  | (default)  | ổn |
| Fennekin | EP0O | 0.4 | 56 / 57 | 1.20 | 67 | 80 |  | (default)  | ổn |
| Finneon | EG5C | 0.4 | 52 / 79 | 1.35 | 71 | 80 |  | (default)  | ổn |
| Flaaffy | P1GA | 0.8 | 98 / 103 | 1.00 | 98 | 109 |  | (default)  | ổn |
| Floatzel | EG4J | 1.1 | 75 / 61 | 1.35 | 101 | 126 |  | (default)  | ổn |
| Flygon | P1HA | 2.0 | 199 / 251 | 0.90 | 179 | 165 |  | (default)  | ổn |
| Froakie | EP0R | 0.3 | 140 / 321 | 0.40 | 56 | 70 |  | (default)  | ổn |
| Frogadier | EP0S | 0.6 | 206 / 321 | 0.55 | 113 | 96 |  | (default)  | ổn |
| Gallade | EN0C | 1.6 | 187 / 103 | 0.94 | 176 | 149 |  | (default)  | ổn |
| Galvantula | P1KA | 0.8 | 95 / 132 | 1.15 | 110 | 109 |  | (default)  | ổn |
| Garchomp | P1LA | 1.9 | 132 / 127 | 1.12 | 147 | 161 |  | (default)  | ổn |
| Gastrodon | EG4N | 0.9 | 75 / 57 | 1.35 | 101 | 115 |  | (default)  | ổn |
| Genesect | EL0B | 1.5 | 165 / 280 | 0.95 | 157 | 145 |  | (default)  | ổn |
| Geodude | E00N | 0.4 | 38 / 184 | 1.45 | 107 | 80 |  | (default)  | ổn |
| Glaceon | E03T | 0.8 | 132 / 197 | 1.00 | 132 | 109 |  | (default)  | ổn |
| Glameow | EG4U | 0.5 | 75 / 70 | 1.35 | 101 | 88 |  | (default)  | ổn |
| Gligar | EG18 | 1.1 | 192 / 220 | 0.66 | 126 | 126 |  | (default)  | ổn |
| Gloom | P1OA | 0.8 | 87 / 101 | 0.90 | 78 | 109 |  | (default)  | ổn |
| Goldeen | EG0E | 0.6 | 60 / 141 | 1.35 | 81 | 96 |  | (default)  | ổn |
| Golduck | P1PA | 1.7 | 121 / 147 | 1.00 | 121 | 153 |  | (default)  | ổn |
| Golem | E00P | 1.4 | 129 / 205 | 1.00 | 129 | 141 |  | (default)  | ổn |
| Granbull | P1QA | 1.4 | 120 / 114 | 0.90 | 108 | 141 |  | (default)  | ổn |
| Graveler | E00O | 1.0 | 106 / 277 | 0.78 | 87 | 121 |  | (default)  | ổn |
| Grimer | EG0B | 0.9 | 150 / 321 | 0.59 | 89 | 115 |  | (default)  | ổn |
| Groudon | P4UA | 3.5 | 142 / 256 | 1.39 | 198 | 212 |  | (default)  | ổn |
| Growlithe | E02F | 0.7 | 122 / 290 | 0.88 | 107 | 103 |  | (default)  | ổn |
| Grumpig | EG31 | 0.9 | 75 / 78 | 1.35 | 101 | 115 |  | (default)  | ổn |
| Gulpin | EG2U | 0.4 | 75 / 90 | 1.35 | 101 | 80 |  | (default)  | ổn |
| Gyarados | E03F | 6.5 | 73 / 120 | 3.00 | 219 | 230 |  | (default)  | ổn |
| Happiny | EG52 | 0.6 | 61 / 44 | 1.35 | 83 | 96 |  | (default)  | ổn |
| Heatran | EL05 | 1.7 | 181 / 410 | 0.88 | 159 | 153 |  | (default)  | ổn |
| Heracross | P1SA | 1.5 | 121 / 174 | 1.20 | 145 | 145 |  | (default)  | ổn |
| Hippopotas | EG57 | 0.8 | 84 / 139 | 1.06 | 89 | 109 |  | (default)  | ổn |
| Hitmonchan | E01Z | 1.4 | 49 / 64 | 3.20 | 157 | 141 |  | (default)  | ổn |
| Hitmonlee | E03Y | 1.5 | 140 / 224 | 1.11 | 156 | 145 |  | (default)  | ổn |
| Hitmontop | E03Z | 1.4 | 125 / 121 | 0.86 | 107 | 141 |  | (default)  | ổn |
| Ho-Oh | P1TA | 3.8 | 117 / 252 | 1.70 | 198 | 220 |  | (default)  | ổn |
| Hoothoot | P1UA | 0.7 | 78 / 94 | 1.00 | 78 | 103 |  | (default)  | ổn |
| Hoppip | EG0T | 0.4 | 104 / 78 | 0.94 | 98 | 80 |  | (default)  | ổn |
| Horsea | P1VA | 0.4 | 48 / 42 | 1.20 | 57 | 80 |  | (default)  | ổn |
| Houndoom | P1WA | 1.4 | 115 / 194 | 1.15 | 132 | 141 |  | (default)  | ổn |
| Houndour | P1XA | 0.6 | 55 / 61 | 1.70 | 94 | 96 |  | (default)  | ổn |
| Hypno | P1ZA | 1.6 | 178 / 197 | 0.95 | 169 | 149 |  | (default)  | ổn |
| Igglybuff | EG0O | 0.3 | 128 / 99 | 0.66 | 84 | 70 |  | (default)  | ổn |
| Infernape | EP0B | 1.2 | 62 / 72 | 2.80 | 173 | 131 |  | (default)  | ổn |
| Ivysaur | E001 | 1.0 | 99 / 129 | 0.92 | 91 | 121 |  | (default)  | ổn |
| Jirachi | P21A | 0.3 | 53 / 66 | 1.30 | 69 | 70 |  | (default)  | ổn |
| Jolteon | E01E | 0.8 | 101 / 104 | 1.24 | 125 | 109 |  | (default)  | ổn |
| Joltik | P22A | 0.1 | 48 / 69 | 1.10 | 53 | 55 |  | (default)  | ổn |
| Jynx | P23A | 1.4 | 96 / 166 | 1.10 | 105 | 141 |  | (default)  | ổn |
| Kabuto | E03P | 0.5 | 104 / 103 | 0.80 | 83 | 88 |  | (default)  | ổn |
| Kabutops | E035 | 1.3 | 135 / 185 | 0.87 | 118 | 136 |  | (default)  | ổn |
| Kakuna | E02J | 0.6 | 82 / 142 | 1.45 | 118 | 96 |  | (default)  | ổn |
| Kangaskhan | E02P | 2.2 | 149 / 196 | 1.34 | 200 | 172 |  | (default)  | ổn |
| Kecleon | EG3H | 1.0 | 75 / 68 | 1.35 | 101 | 121 |  | (default)  | ổn |
| Kingambit | P4TA | 2.0 | 272 / 315 | 0.70 | 191 | 165 |  | (default)  | ổn |
| Krabby | E03C | 0.4 | 76 / 108 | 1.07 | 81 | 80 |  | (default)  | ổn |
| Kricketune | EG42 | 1.0 | 75 / 49 | 1.35 | 101 | 121 |  | (default)  | ổn |
| Kyurem | EL0A | 3.0 | 293 / 535 | 0.65 | 191 | 198 |  | (default)  | ổn |
| Lampent | P27A | 0.6 | 60 / 140 | 1.20 | 72 | 96 |  | (default)  | ổn |
| Lapras | P29A | 2.5 | 149 / 257 | 1.00 | 149 | 182 |  | (default)  | ổn |
| Larvitar | EN06 | 0.6 | 76 / 54 | 1.20 | 92 | 96 |  | (default)  | ổn |
| Latias & Latios | PV2A | 1.4 | 106 / 196 | 1.20 | 127 | 141 |  | (default)  | ổn |
| Leafeon | P2BA | 1.0 | 103 / 169 | 1.20 | 124 | 121 |  | (default)  | ổn |
| Leafleon | E03S | 1.0 | 103 / 169 | 1.35 | 139 | 121 |  | (default)  | ổn |
| Ledyba | EG0I | 1.0 | 51 / 157 | 1.35 | 85 | 121 |  | (default)  | ổn |
| Lileep | P2CA | 1.0 | 107 / 50 | 1.00 | 107 | 121 |  | (default)  | ổn |
| Litten | EP0U | 0.4 | 70 / 187 | 0.80 | 60 | 80 |  | (default)  | ổn |
| Litwick | P2DA | 0.3 | 55 / 33 | 1.30 | 72 | 70 |  | (default)  | ổn |
| Loudred | EG2B | 1.0 | 100 / 156 | 1.18 | 118 | 121 |  | (default)  | ổn |
| Lucario | EN0J | 1.2 | 138 / 116 | 1.00 | 138 | 131 |  | (default)  | ổn |
| Ludicolo | P2GA | 1.5 | 144 / 208 | 0.96 | 138 | 145 |  | (default)  | ổn |
| Lunala | EL0J | 4.0 | 505 / 884 | 0.40 | 202 | 225 |  | (default)  | ổn |
| Luvdisc | EG3V | 0.6 | 75 / 46 | 1.35 | 101 | 96 |  | (default)  | ổn |
| Luxio | EG44 | 0.9 | 267 / 287 | 0.45 | 120 | 115 |  | (default)  | ổn |
| Machamp | E010 | 1.6 | 160 / 240 | 1.03 | 165 | 149 |  | (default)  | ổn |
| Machoke | E00Z | 1.5 | 135 / 214 | 1.22 | 165 | 145 |  | (default)  | ổn |
| Machop | E00Y | 0.8 | 95 / 127 | 1.47 | 139 | 109 |  | (default)  | ổn |
| Magby | P2HA | 0.7 | 72 / 55 | 1.24 | 89 | 103 |  | (default)  | ổn |
| Magcargo | P2IA | 0.8 | 95 / 139 | 1.00 | 95 | 109 |  | (default)  | ổn |
| Magikarp | E03E | 0.9 | 72 / 112 | 1.20 | 86 | 115 |  | (default)  | ổn |
| Magmar | P2JA | 1.3 | 176 / 182 | 1.00 | 176 | 136 |  | (default)  | ổn |
| Magmortar | P2KA | 1.6 | 157 / 209 | 1.00 | 157 | 149 |  | (default)  | ổn |
| Magnemite | E031 | 0.3 | 45 / 76 | 1.35 | 60 | 70 |  | (default)  | ổn |
| Magneton | P4XA | 1.0 | 83 / 144 | 1.05 | 88 | 121 |  | (default)  | ổn |
| Mamoswine | P2MA | 2.5 | 184 / 274 | 0.80 | 147 | 182 |  | (default)  | ổn |
| Manectric | P2NA | 1.5 | 132 / 115 | 1.05 | 138 | 145 |  | (default)  | ổn |
| Mankey | E02S | 0.5 | 66 / 118 | 1.44 | 95 | 88 |  | (default)  | ổn |
| Mareep | P2OA | 0.6 | 62 / 118 | 1.20 | 74 | 96 |  | (default)  | ổn |
| Marill | EG0R | 0.4 | 74 / 119 | 1.35 | 100 | 80 |  | (default)  | ổn |
| Marowak | P2PA | 1.0 | 116 / 107 | 0.87 | 101 | 121 |  | (default)  | ổn |
| Meditite | EG2N | 0.6 | 104 / 98 | 0.91 | 94 | 96 |  | (default)  | ổn |
| Meganium | PV0A | 1.8 | 330 / 355 | 0.60 | 198 | 157 |  | (default)  | ổn |
| Meowth | P2QA | 0.4 | 79 / 90 | 1.00 | 79 | 80 |  | (default)  | ổn |
| Metagross | EN0I | 1.6 | 128 / 224 | 0.90 | 116 | 149 |  | (default)  | ổn |
| Metang | EN0H | 1.2 | 96 / 347 | 0.82 | 114 | 131 |  | (default)  | ổn |
| Metapod | E01P | 0.7 | 75 / 145 | 1.50 | 113 | 103 |  | (default)  | ổn |
| Mime Jr. | EG51 | 0.6 | 125 / 99 | 0.76 | 95 | 96 |  | (default)  | ổn |
| Misdreavus | P2UA | 0.7 | 73 / 87 | 1.00 | 73 | 103 |  | (default)  | ổn |
| Mismagius | P2VA | 0.9 | 117 / 74 | 1.10 | 129 | 115 |  | (default)  | ổn |
| Monferno | EP0A | 0.9 | 88 / 119 | 1.73 | 152 | 115 |  | (default)  | ổn |
| Mothim | EG4E | 0.9 | 75 / 136 | 1.35 | 101 | 115 |  | (default)  | ổn |
| Mr. Mime | P2WA | 1.3 | 186 / 295 | 0.60 | 112 | 136 |  | (default)  | ổn |
| Mr.mime | E040 | 1.3 | 186 / 294 | 0.70 | 130 | 136 |  | (default)  | ổn |
| Mudkip | EP03 | 0.4 | 40 / 41 | 1.40 | 56 | 80 |  | (default)  | ổn |
| Munchlax | EG55 | 0.6 | 61 / 59 | 1.35 | 83 | 96 |  | (default)  | ổn |
| Murkrow | EG12 | 0.5 | 164 / 248 | 0.62 | 101 | 88 |  | (default)  | ổn |
| Necrozma | EL0K | 2.4 | 174 / 239 | 1.05 | 183 | 179 |  | (default)  | ổn |
| Nidoking | E01J | 1.4 | 141 / 253 | 1.12 | 158 | 141 |  | (default)  | ổn |
| Nidoran | E01M | 0.5 | 55 / 91 | 1.37 | 75 | 88 |  | (default)  | ổn |
| Nidoran F | EG02 | 0.4 | 65 / 170 | 1.35 | 92 | 80 |  | (default)  | ổn |
| Nidorina | EG03 | 0.8 | 95 / 204 | 1.22 | 116 | 109 |  | (default)  | ổn |
| Nidorino | E01L | 0.9 | 96 / 141 | 0.91 | 88 | 115 |  | (default)  | ổn |
| Ninetales | E04P | 1.1 | 76 / 208 | 2.00 | 167 | 126 |  | (default)  | ổn |
| Noctowl | P2ZA | 1.6 | 126 / 215 | 0.85 | 107 | 149 |  | (default)  | ổn |
| Nosepass | EG2G | 1.0 | 99 / 178 | 0.89 | 88 | 121 |  | (default)  | ổn |
| Numel | EG2Y | 0.7 | 206 / 260 | 0.43 | 89 | 103 |  | (default)  | ổn |
| Nuzleaf | EG1Z | 1.0 | 75 / 70 | 1.35 | 101 | 121 |  | (default)  | ổn |
| Oddish | P30A | 0.5 | 75 / 86 | 1.00 | 75 | 88 |  | (default)  | ổn |
| Omanyte | E03Q | 0.4 | 176 / 240 | 0.50 | 88 | 80 |  | (default)  | ổn |
| Omastar | E03R | 1.0 | 100 / 240 | 1.05 | 105 | 121 |  | (default)  | ổn |
| Onix | E03U | 8.8 | 143 / 639 | 0.90 | 230 | 230 |  | (default)  | ổn |
| Pawniard | P4RA | 0.5 | 69 / 234 | 1.10 | 103 | 88 |  | (default)  | ổn |
| Pelipper | EG24 | 1.2 | 75 / 72 | 1.35 | 101 | 131 |  | (default)  | ổn |
| Persian | P31A | 1.0 | 93 / 207 | 1.00 | 93 | 121 |  | (default)  | ổn |
| Phanpy | EG1J | 0.5 | 73 / 107 | 1.17 | 85 | 88 |  | (default)  | ổn |
| Pichu | EG0M | 0.3 | 68 / 64 | 1.34 | 91 | 70 |  | (default)  | ổn |
| Pikachu | E005 | 0.4 | 68 / 62 | 1.17 | 79 | 80 |  | (default)  | ổn |
| Piloswine | P32A | 1.1 | 133 / 164 | 1.00 | 133 | 126 |  | (default)  | ổn |
| Pineco | EG15 | 0.6 | 105 / 321 | 0.90 | 116 | 96 |  | (default)  | ổn |
| Pinsir | E03W | 1.5 | 119 / 198 | 1.17 | 139 | 145 |  | (default)  | ổn |
| Piplup | EP0C | 0.4 | 236 / 145 | 0.30 | 71 | 80 |  | (default)  | ổn |
| Politoed | P34A | 1.1 | 116 / 128 | 0.90 | 104 | 126 |  | (default)  | ổn |
| Poliwhirl | E013 | 1.0 | 97 / 168 | 1.00 | 97 | 121 |  | (default)  | ổn |
| Poliwhirl | P4ZA | 1.0 | 97 / 168 | 0.90 | 87 | 121 |  | (default)  | ổn |
| Poliwrath | E014 | 1.3 | 118 / 268 | 0.92 | 108 | 136 |  | (default)  | ổn |
| Ponyta | E01B | 1.0 | 112 / 150 | 1.35 | 151 | 121 |  | (default)  | ổn |
| Poochyena | EG1P | 0.5 | 83 / 119 | 1.07 | 89 | 88 |  | (default)  | ổn |
| Porygon2 | PV1A | 0.6 | 73 / 120 | 1.00 | 73 | 96 |  | (default)  | ổn |
| Primeape | E02T | 1.0 | 127 / 205 | 0.80 | 101 | 121 |  | (default)  | ổn |
| Prinplup | EP0D | 0.8 | 272 / 198 | 0.50 | 136 | 109 |  | (default)  | ổn |
| Psyduck | P36A | 0.8 | 157 / 155 | 0.72 | 113 | 109 |  | (default)  | ổn |
| Pupitar | EN07 | 1.2 | 88 / 74 | 1.20 | 106 | 131 |  | (default)  | ổn |
| Purugly | EG4V | 1.0 | 75 / 69 | 1.35 | 101 | 121 |  | (default)  | ổn |
| Quilava | P38A | 0.9 | 97 / 124 | 1.00 | 97 | 115 |  | (default)  | ổn |
| Quilladin | EP0M | 0.7 | 107 / 129 | 1.20 | 128 | 103 |  | (default)  | ổn |
| Qwilfish | EG19 | 0.5 | 52 / 103 | 1.35 | 70 | 88 |  | (default)  | ổn |
| Raichu | E006 | 0.8 | 81 / 232 | 1.28 | 119 | 109 |  | (default)  | ổn |
| Raikou | P39A | 1.9 | 113 / 158 | 1.40 | 159 | 161 |  | (default)  | ổn |
| Raticate | E00U | 0.7 | 73 / 164 | 1.45 | 106 | 103 |  | (default)  | ổn |
| Regice | EL00 | 1.8 | 180 / 200 | 0.64 | 115 | 157 |  | (default)  | ổn |
| Regirock | P3BA | 1.7 | 158 / 156 | 1.20 | 190 | 153 |  | (default)  | ổn |
| Registeel | EL01 | 1.9 | 230 / 208 | 0.82 | 189 | 161 |  | (default)  | ổn |
| Reshiram | EL08 | 3.2 | 261 / 800 | 0.55 | 176 | 204 |  | (default)  | ổn |
| Rhydon | E02Z | 1.9 | 179 / 278 | 0.89 | 160 | 161 |  | (default)  | ổn |
| Rhydon | P51A | 1.9 | 179 / 278 | 0.85 | 152 | 161 |  | (default)  | ổn |
| Rhyhorn | E02Y | 1.0 | 98 / 152 | 1.12 | 110 | 121 |  | (default)  | ổn |
| Rhyperior | P3CA | 2.4 | 71 / 100 | 2.00 | 142 | 179 |  | (default)  | ổn |
| Riolu | EG56 | 0.7 | 74 / 269 | 1.27 | 137 | 103 |  | (default)  | ổn |
| Sableye | P3DA | 0.5 | 71 / 83 | 1.20 | 85 | 88 |  | (default)  | ổn |
| Salamence | EN0F | 1.5 | 187 / 437 | 0.80 | 150 | 145 |  | hover 40 | ổn |
| Sandshrew | E00A | 0.6 | 70 / 161 | 1.18 | 82 | 96 |  | (default)  | ổn |
| Sandslash | E00F | 1.0 | 119 / 225 | 1.08 | 129 | 121 |  | (default)  | ổn |
| Sceptile | EN05 | 1.7 | 139 / 149 | 1.00 | 139 | 153 |  | (default)  | ổn |
| Scizor | E03M | 1.8 | 156 / 132 | 1.19 | 186 | 157 |  | (default)  | ổn |
| Scyther | E03L | 1.5 | 135 / 270 | 0.99 | 133 | 145 |  | (default)  | ổn |
| Sealeo | EG3P | 1.1 | 102 / 321 | 1.28 | 164 | 126 |  | (default)  | ổn |
| Seedot | EG1Y | 0.5 | 75 / 54 | 1.35 | 101 | 88 |  | (default)  | ổn |
| Sentret | EG0G | 0.8 | 96 / 94 | 0.99 | 95 | 109 |  | (default)  | ổn |
| Sharpedo | P3IA | 1.8 | 206 / 200 | 0.55 | 113 | 157 |  | (default)  | ổn |
| Shedinja | P3JA | 0.8 | 79 / 97 | 1.00 | 79 | 109 |  | (default)  | ổn |
| Shellder | E02E | 0.3 | 86 / 150 | 0.65 | 56 | 70 |  | (default)  | ổn |
| Shieldon | EG4A | 0.5 | 114 / 137 | 0.82 | 94 | 88 |  | (default)  | ổn |
| Shinx | EG43 | 0.5 | 269 / 393 | 0.35 | 94 | 88 |  | (default)  | ổn |
| Shuppet | EG3I | 0.6 | 75 / 63 | 1.35 | 101 | 96 |  | (default)  | ổn |
| Silcoon | EG1U | 0.6 | 83 / 124 | 1.35 | 112 | 96 |  | (default)  | ổn |
| Skiploom | EG0U | 0.6 | 64 / 114 | 1.35 | 86 | 96 |  | (default)  | ổn |
| Skitty | EG2H | 0.6 | 75 / 89 | 1.35 | 101 | 96 |  | (default)  | ổn |
| Skorupi | EG59 | 0.8 | 52 / 160 | 1.35 | 86 | 109 |  | (default)  | ổn |
| Skuntank | EG4Y | 1.0 | 75 / 101 | 1.35 | 101 | 121 |  | (default)  | ổn |
| Slakoth | EG27 | 0.8 | 116 / 321 | 0.83 | 107 | 109 |  | (default)  | ổn |
| Slowbro | P3NA | 1.6 | 225 / 324 | 0.50 | 113 | 149 |  | (default)  | ổn |
| Slowking | P3OA | 2.0 | 295 / 261 | 0.50 | 148 | 165 |  | (default)  | ổn |
| Slugma | P3QA | 0.7 | 64 / 75 | 1.19 | 77 | 103 |  | (default)  | ổn |
| Smeargle | EG1M | 1.2 | 120 / 237 | 0.99 | 118 | 131 |  | (default)  | ổn |
| Smoochum | P3RA | 0.4 | 60 / 47 | 1.25 | 75 | 80 |  | (default)  | ổn |
| Sneasel | P3SA | 0.9 | 101 / 134 | 0.90 | 91 | 115 |  | (default)  | ổn |
| Snorlax | P3TA | 2.1 | 177 / 225 | 1.00 | 177 | 169 |  | (default)  | ổn |
| Snorunt | EG3M | 0.7 | 69 / 68 | 1.24 | 86 | 103 |  | (default)  | ổn |
| Snover | P3UA | 1.0 | 88 / 153 | 1.00 | 88 | 121 |  | (default)  | ổn |
| Solgaleo | EL0I | 3.4 | 365 / 714 | 0.45 | 164 | 210 |  | (default)  | ổn |
| Spearow | EG00 | 0.3 | 61 / 149 | 1.35 | 83 | 70 |  | (default)  | ổn |
| Spheal | EG3O | 0.8 | 98 / 97 | 0.90 | 88 | 109 |  | (default)  | ổn |
| Spinarak | EG0K | 0.5 | 30 / 214 | 1.35 | 116 | 88 |  | (default)  | ổn |
| Spoink | EG30 | 0.7 | 75 / 45 | 1.35 | 101 | 103 |  | (default)  | ổn |
| Squirtle | E004 | 0.5 | 69 / 74 | 1.29 | 88 | 88 |  | (default)  | ổn |
| Staravia | EG3X | 0.6 | 92 / 221 | 1.35 | 124 | 96 |  | (default)  | ổn |
| Starly | EG3W | 0.3 | 58 / 162 | 1.35 | 87 | 70 |  | (default)  | ổn |
| Staryu | E04N | 0.8 | 83 / 141 | 1.00 | 83 | 109 |  | (default)  | ổn |
| Stunky | EG4X | 0.4 | 75 / 83 | 1.35 | 101 | 80 |  | (default)  | ổn |
| Sudowoodo | P3WA | 1.2 | 160 / 185 | 0.92 | 148 | 131 |  | (default)  | ổn |
| Suicune | P3XA | 2.0 | 132 / 393 | 1.00 | 157 | 165 |  | (default)  | ổn |
| Sunkern | EG0X | 0.3 | 30 / 141 | 1.35 | 76 | 70 |  | (default)  | ổn |
| Swablu | P3YA | 0.4 | 76 / 163 | 0.80 | 61 | 80 |  | (default)  | ổn |
| Swampert | EP05 | 1.5 | 153 / 222 | 1.20 | 183 | 145 |  | (default)  | ổn |
| Swellow | EG22 | 0.7 | 75 / 94 | 1.35 | 101 | 103 |  | (default)  | ổn |
| Tangrowth | P41A | 2.0 | 107 / 346 | 1.10 | 152 | 165 |  | (default)  | ổn |
| Tauros | E018 | 1.4 | 132 / 279 | 0.92 | 121 | 141 |  | (default)  | ổn |
| Tauros Aqua | P42A | 1.4 | 85 / 211 | 1.60 | 136 | 141 |  | (default)  | ổn |
| Tauros Blaze | P43A | 1.4 | 95 / 214 | 1.60 | 152 | 141 |  | (default)  | ổn |
| Tauros Combat | P44A | 1.4 | 84 / 177 | 1.60 | 135 | 141 |  | (default)  | ổn |
| Teddiursa | EG1B | 0.6 | 58 / 51 | 1.35 | 79 | 96 |  | (default)  | ổn |
| Togepi | P46A | 0.3 | 59 / 63 | 1.34 | 79 | 70 |  | (default)  | ổn |
| Togetic | P47A | 0.6 | 87 / 56 | 1.04 | 90 | 96 |  | (default)  | ổn |
| Torchic | EN00 | 0.4 | 108 / 141 | 0.86 | 93 | 80 |  | (default)  | ổn |
| Torracat | EP0V | 0.7 | 111 / 233 | 1.20 | 133 | 103 |  | (default)  | ổn |
| Totodile | EP00 | 0.6 | 111 / 120 | 0.70 | 78 | 96 |  | (default)  | ổn |
| Toxicroak | P4AA | 1.3 | 141 / 244 | 0.80 | 112 | 136 |  | (default)  | ổn |
| Trapinch | P4BA | 0.7 | 242 / 411 | 0.30 | 73 | 103 |  | (default)  | ổn |
| Treecko | EN03 | 0.5 | 51 / 98 | 1.35 | 69 | 88 |  | (default)  | ổn |
| Turtwig | EP06 | 0.4 | 54 / 56 | 1.50 | 81 | 80 |  | (default)  | ổn |
| Typhlosion | P4DA | 1.7 | 126 / 123 | 1.10 | 138 | 153 |  | (default)  | ổn |
| Tyranitar | EN08 | 2.0 | 165 / 163 | 1.05 | 174 | 165 |  | (default)  | ổn |
| Tyrogue | P4EA | 0.7 | 84 / 85 | 1.15 | 96 | 103 |  | (default)  | ổn |
| Unown | EG13 | 0.5 | 76 / 40 | 1.35 | 103 | 88 |  | (default)  | ổn |
| Ursaring | EG1C | 1.8 | 191 / 256 | 0.60 | 115 | 157 |  | (default)  | ổn |
| Vaporeon | E037 | 1.0 | 106 / 218 | 1.14 | 120 | 121 |  | (default)  | ổn |
| Venonat | EG07 | 1.0 | 165 / 145 | 0.53 | 87 | 121 |  | (default)  | ổn |
| Venusaur | E002 | 2.0 | 138 / 219 | 0.93 | 129 | 165 |  | (default)  | ổn |
| Victreebel | E02C | 1.7 | 139 / 384 | 0.92 | 141 | 153 |  | (default)  | ổn |
| Vigoroth | EG28 | 1.4 | 161 / 455 | 0.81 | 147 | 141 |  | (default)  | ổn |
| Volcanion | EL0H | 1.7 | 177 / 178 | 1.00 | 177 | 153 |  | (default)  | ổn |
| Wartortle | E009 | 1.0 | 128 / 119 | 0.91 | 117 | 121 |  | (default)  | ổn |
| Weavile | P4HA | 1.1 | 117 / 108 | 1.00 | 117 | 126 |  | (default)  | ổn |
| Weedle | E02I | 0.3 | 60 / 138 | 1.50 | 89 | 70 |  | (default)  | ổn |
| Weepinbell | E01A | 1.0 | 118 / 157 | 0.80 | 94 | 121 |  | (default)  | ổn |
| Whiscash | EG3B | 0.9 | 75 / 102 | 1.35 | 101 | 115 |  | (default)  | ổn |
| Whismur | EG2A | 0.6 | 60 / 66 | 1.35 | 81 | 96 |  | (default)  | ổn |
| Wigglytuff | P4IA | 1.0 | 127 / 138 | 0.80 | 102 | 121 |  | (default)  | ổn |
| Wingull | EG23 | 0.6 | 75 / 110 | 1.35 | 101 | 96 |  | (default)  | ổn |
| Wobbuffet | P4JA | 1.3 | 109 / 123 | 1.00 | 109 | 136 |  | (default)  | ổn |
| Wooper | EG10 | 0.4 | 58 / 180 | 1.35 | 97 | 80 |  | (default)  | ổn |
| Wormadam | EG4D | 0.5 | 75 / 60 | 1.35 | 101 | 88 |  | (default)  | ổn |
| Xerneas | EL0C | 3.0 | 496 / 442 | 0.42 | 209 | 198 |  | (default)  | ổn |
| Yanma | EG0Z | 1.2 | 69 / 322 | 1.35 | 174 | 131 |  | (default)  | ổn |
| Yveltal | EL0D | 5.8 | 200 / 410 | 0.85 | 170 | 230 |  | (default)  | ổn |
| Zacian | EL0N | 2.8 | 221 / 227 | 0.85 | 188 | 192 |  | (default)  | ổn |
| Zekrom | EL09 | 2.9 | 254 / 300 | 0.72 | 183 | 195 |  | (default)  | ổn |
| Zubat | E046 | 0.8 | 90 / 134 | 1.60 | 143 | 109 |  | hover  | ổn |
| Zweilous | P4LA | 1.4 | 126 / 174 | 1.00 | 126 | 141 |  | (default)  | ổn |
| Zygarde | EL0E | 5.0 | 448 / 308 | 0.45 | 202 | 230 |  | (default)  | ổn |
