# Kích thước và đi bộ / bay của hero: New Pokemon Arena 1.0.w3x

619 hero, 151 bị đánh dấu. Tạo bằng `tools/v412/model_size_check.py` (GEMINI.md mục 13).

Cao trên màn hình = kích thước model x scale. Mục tiêu tính từ chiều cao thật của loài (PokeAPI). Scale đề xuất đưa con đó về đúng mục tiêu; vẫn phải xem trong game.

| Hero | Id | Cao thật (m) | Model cao / dài | Scale | Trên màn hình | Mục tiêu | Scale đề xuất | Di chuyển | Vấn đề |
|---|---|---|---|---|---|---|---|---|---|
| Abra | E00G | 0.9 | 92 / 115 | 0.82 | 76 | 115 | 1.25 | (default) 20 | quá nhỏ; lơ lửng sai ((default), cao 20) |
| Aegislash Blade | PF00 | - | 153 / 334 | 1.00 | 153 | - |  | foot  | không có dữ liệu loài |
| Aerodactyl | P02A | 1.8 | 111 / 285 | 0.90 | 103 | 157 | 1.40 | (default)  | quá nhỏ |
| Alakazam | E00I | 1.5 | 126 / 131 | 1.13 | 142 | 145 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Arceus | E02A | 3.2 | 209 / 171 | 1.50 | 314 | 204 | 1.00 | hover  | quá to; lơ lửng sai (hover, cao 0) |
| Articuno | E020 | 1.7 | 276 / 289 | 0.84 | 232 | 153 | 0.55 | hover 100 | quá to |
| Ash-Greninja | PF14 | - | 145 / 167 | 1.00 | 145 | - |  | foot  | không có dữ liệu loài |
| Ash-Pikachu (m Ash) | PF30 | - | 80 / 74 | 1.00 | 80 | - |  | foot  | không có dữ liệu loài |
| Azelf | EL04 | 0.3 | 137 / 137 | 1.25 | 171 | 70 | 0.50 | (default)  | quá to |
| Baltoy | P0BA | 0.5 | 37 / 48 | 1.60 | 59 | 88 | 2.00 | (default)  | quá nhỏ |
| Bulbasaur | E008 | 0.7 | 161 / 92 | 1.15 | 185 | 103 | 0.65 | (default)  | quá to |
| Castform | EG3G | 0.3 | 70 / 43 | 1.00 | 70 | 70 |  | hover 65 | lơ lửng sai (hover, cao 65) |
| Castform Rainy | PF02 | - | 70 / 37 | 1.00 | 70 | - |  | foot  | không có dữ liệu loài |
| Castform Snowy | PF03 | - | 70 / 68 | 1.00 | 70 | - |  | foot  | không có dữ liệu loài |
| Castform Sunny | PF04 | - | 70 / 64 | 1.00 | 70 | - |  | foot  | không có dữ liệu loài |
| Charizard | E00E | 1.7 | 174 / 323 | 0.96 | 167 | 153 |  | hover 180 | bay quá cao (180) |
| Cherrim Sunshine | PF05 | - | 88 / 98 | 1.00 | 88 | - |  | foot  | không có dữ liệu loài |
| Chesnaught | EP0N | 1.6 | 144 / 165 | 1.65 | 237 | 149 | 1.05 | (default)  | quá to |
| Chikorita | P0NA | 0.9 | 169 / 74 | 1.00 | 169 | 115 | 0.70 | (default)  | quá to |
| Chimchar | EP09 | 0.5 | 48 / 43 | 2.80 | 134 | 88 | 1.85 | (default)  | quá to |
| Chimecho | EG3L | 0.6 | 149 / 44 | 1.00 | 149 | 96 | 0.65 | foot  | quá to |
| Chinchou | P0OA | 0.5 | 82 / 144 | 0.64 | 53 | 88 | 1.10 | (default)  | quá nhỏ |
| Cloyster | E01F | 1.5 | 150 / 172 | 0.66 | 99 | 145 | 0.95 | (default)  | quá nhỏ |
| Cradily | P0TA | 1.5 | 211 / 87 | 1.20 | 253 | 145 | 0.70 | (default)  | quá to |
| Darkrai | E023 | 1.5 | 129 / 136 | 1.50 | 193 | 145 |  | hover 20 | lơ lửng sai (hover, cao 20) |
| Delphox | EP0Q | 1.5 | 178 / 177 | 1.20 | 213 | 145 | 0.80 | (default)  | quá to |
| Deoxys | E027 | 1.7 | 278 / 384 | 0.80 | 222 | 153 | 0.55 | hover  | quá to; lơ lửng sai (hover, cao 0) |
| Dewgong | P10A | 1.7 | 75 / 207 | 1.15 | 95 | 153 | 1.85 | (default)  | quá nhỏ |
| Dialga | E04C | 5.4 | 154 / 238 | 1.50 | 231 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Diglett | P11A | 0.2 | 36 / 51 | 1.10 | 40 | 59 | 1.65 | (default)  | quá nhỏ |
| Doublade | P4PA | 0.8 | 150 / 236 | 1.00 | 150 | 109 | 0.75 | (default)  | quá to |
| Dugtrio | P14A | 0.7 | 84 / 122 | 0.70 | 59 | 103 | 1.20 | (default)  | quá nhỏ |
| Eevee | E03A | 0.3 | 4 / 5 | 22.00 | 78 | 70 |  | (default)  | model lạ (cao 3) |
| Ekans | P18A | 2.0 | 235 / 22 | 1.30 | 305 | 165 | 0.70 | (default)  | quá to |
| Electrike | P1BA | 0.6 | 64 / 109 | 1.05 | 67 | 96 | 1.50 | (default)  | quá nhỏ |
| Electrode | E01X | 1.2 | 115 / 115 | 0.73 | 84 | 131 | 1.15 | hover 30 | quá nhỏ; lơ lửng sai (hover, cao 30) |
| Emboar | EP0K | 1.6 | 173 / 322 | 1.50 | 260 | 149 | 0.85 | (default)  | quá to |
| Empoleon | EP0E | 1.7 | 267 / 213 | 0.95 | 254 | 153 | 0.55 | (default)  | quá to |
| Exeggcute | E02U | 0.4 | 189 / 463 | 0.70 | 132 | 80 | 0.40 | (default)  | quá to |
| Fan Rotom | PF35 | - | 74 / 130 | 0.94 | 70 | - |  | fly 70 | không có dữ liệu loài |
| Feebas | P1FA | 0.6 | 62 / 71 | 1.05 | 65 | 96 | 1.55 | (default)  | quá nhỏ |
| Flareon | E038 | 0.9 | 283 / 220 | 1.15 | 325 | 115 | 0.40 | (default)  | quá to |
| Frost Rotom | PF36 | - | 95 / 155 | 0.74 | 70 | - |  | fly 70 | không có dữ liệu loài |
| Gabite | P1IA | 1.4 | 95 / 135 | 1.00 | 95 | 141 | 1.50 | (default)  | quá nhỏ |
| Galarian Corsola | PF06 | - | 96 / 115 | 1.00 | 96 | - |  | foot  | không có dữ liệu loài |
| Galarian Farfetch'd | PF12 | - | 211 / 321 | 0.52 | 110 | - |  | foot  | không có dữ liệu loài |
| Galarian Linoone | PF18 | - | 76 / 221 | 1.00 | 88 | - |  | foot  | không có dữ liệu loài |
| Galarian Meowth | PF21 | - | 128 / 157 | 0.63 | 81 | - |  | foot  | không có dữ liệu loài |
| Galarian Mr. Mime | PF22 | - | 136 / 164 | 1.00 | 136 | - |  | foot  | không có dữ liệu loài |
| Galarian Ponyta | PF31 | - | 121 / 146 | 1.00 | 121 | - |  | foot  | không có dữ liệu loài |
| Galarian Rapidash | PF32 | - | 153 / 218 | 1.00 | 153 | - |  | foot  | không có dữ liệu loài |
| Galarian Slowbro | PF41 | - | 149 / 217 | 1.00 | 149 | - |  | foot  | không có dữ liệu loài |
| Galarian Slowpoke | PF42 | - | 85 / 328 | 1.00 | 131 | - |  | foot  | không có dữ liệu loài |
| Galarian Weezing | PF49 | - | 131 / 123 | 1.00 | 131 | - |  | fly 70 | không có dữ liệu loài |
| Galarian Zigzagoon | PF51 | - | 80 / 157 | 1.00 | 80 | - |  | foot  | không có dữ liệu loài |
| Gardevoir | EN0B | 1.6 | 119 / 99 | 1.20 | 143 | 149 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Gastly | E02G | 1.3 | 40 / 42 | 1.35 | 54 | 136 | 2.00 | (default) 20 | quá nhỏ |
| Gastrodon (East Sea) | PF13 | - | 115 / 109 | 1.00 | 115 | - |  | foot  | không có dữ liệu loài |
| Gengar | E01G | 1.5 | 156 / 204 | 0.73 | 114 | 145 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Gible | P1NA | 0.7 | 63 / 69 | 1.00 | 63 | 103 | 1.60 | (default)  | quá nhỏ |
| Giratina | E028 | 4.5 | 189 / 264 | 1.50 | 283 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Golbat | E048 | 1.6 | 132 / 314 | 0.66 | 87 | 149 | 1.15 | hover 40 | quá nhỏ |
| Greninja | EP0T | 1.5 | 160 / 185 | 1.25 | 201 | 145 | 0.90 | (default)  | quá to |
| Grotle | EP07 | 1.1 | 61 / 90 | 3.00 | 182 | 126 | 2.00 | (default)  | quá to |
| Grovyle | EN04 | 0.9 | 139 / 126 | 1.20 | 167 | 115 | 0.85 | (default)  | quá to |
| Haunter | E02H | 1.6 | 90 / 125 | 1.04 | 93 | 149 | 1.65 | (default) 20 | quá nhỏ |
| Heat Rotom | PF37 | - | 67 / 132 | 1.05 | 70 | - |  | fly 70 | không có dữ liệu loài |
| Heatran | EL05 | 1.7 | 181 / 410 | 1.40 | 253 | 153 | 0.85 | (default)  | quá to |
| Hisuian Arcanine | PF01 | - | 161 / 209 | 1.00 | 161 | - |  | foot  | không có dữ liệu loài |
| Hisuian Electrode | PF10 | - | 131 / 131 | 1.00 | 131 | - |  | foot  | không có dữ liệu loài |
| Hisuian Growlithe | PF16 | - | 103 / 134 | 1.00 | 103 | - |  | foot  | không có dữ liệu loài |
| Hisuian Sneasel | PF43 | - | 128 / 169 | 0.90 | 115 | - |  | foot  | không có dữ liệu loài |
| Hisuian Typhlosion | PF45 | - | 136 / 107 | 1.12 | 153 | - |  | foot  | không có dữ liệu loài |
| Hisuian Voltorb | PF47 | - | 88 / 94 | 1.00 | 88 | - |  | foot  | không có dữ liệu loài |
| Honedge | P4OA | 0.8 | 187 / 180 | 1.00 | 187 | 109 | 0.60 | (default)  | quá to |
| Hoopa | EL0G | 0.5 | 104 / 173 | 1.25 | 130 | 88 | 0.85 | (default)  | quá to |
| Hydreigon | P1YA | 1.8 | 183 / 186 | 1.20 | 220 | 157 | 0.85 | (default)  | quá to |
| Incineroar | EP0W | 1.8 | 168 / 332 | 1.60 | 269 | 157 | 0.95 | (default)  | quá to |
| Jigglypuff | P20A | 0.5 | 66 / 71 | 0.75 | 50 | 88 | 1.35 | (default)  | quá nhỏ |
| Kadabra | E00H | 1.3 | 101 / 141 | 1.27 | 129 | 136 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Kingdra | P24A | 1.8 | 104 / 90 | 1.05 | 110 | 157 | 1.50 | (default)  | quá nhỏ |
| Kingler | E03D | 1.3 | 94 / 117 | 0.93 | 87 | 136 | 1.45 | (default)  | quá nhỏ |
| Kirlia | EN0A | 0.8 | 68 / 56 | 1.20 | 82 | 109 |  | (default) 20 | lơ lửng sai ((default), cao 20) |
| Koffing | E01V | 0.6 | 151 / 258 | 1.41 | 213 | 96 | 0.65 | (default) 25 | quá to |
| Kyogre | P26A | 4.5 | 55 / 240 | 1.30 | 125 | 230 | 2.00 | (default)  | quá nhỏ |
| Lanturn | P28A | 1.2 | 112 / 240 | 0.70 | 79 | 131 | 1.15 | (default)  | quá nhỏ |
| Lombre | P2EA | 1.2 | 89 / 119 | 0.90 | 80 | 131 | 1.50 | (default)  | quá nhỏ |
| Lotad | P2FA | 0.5 | 50 / 100 | 0.85 | 42 | 88 | 1.75 | (default)  | quá nhỏ |
| Lugia | E022 | 5.2 | 181 / 190 | 1.75 | 317 | 230 | 1.25 | hover 50 | quá to |
| Magearna | EL0L | 1.0 | 64 / 151 | 1.20 | 77 | 121 | 1.90 | (default)  | quá nhỏ |
| Magnemite | P4WA | 0.3 | 45 / 76 | 1.00 | 45 | 70 | 1.55 | (default)  | quá nhỏ |
| Magneton | E032 | 1.0 | 83 / 144 | 0.99 | 83 | 121 | 1.45 | (default)  | quá nhỏ |
| Magnezone | P2LA | 1.2 | 63 / 109 | 1.20 | 75 | 131 | 2.00 | (default)  | quá nhỏ |
| Marshadow | EL0M | 0.7 | 148 / 104 | 1.20 | 177 | 103 | 0.70 | (default)  | quá to |
| Marshtomp | EP04 | 0.7 | 127 / 140 | 1.20 | 152 | 103 | 0.80 | (default)  | quá to |
| Mesprit | EL03 | 0.3 | 132 / 154 | 1.25 | 165 | 70 | 0.55 | (default)  | quá to |
| Mew | E024 | 0.4 | 191 / 191 | 5.00 | 955 | 80 | 0.40 | hover 50 | quá to; lơ lửng sai (hover, cao 50) |
| Mewtwo | E026 | 2.0 | 62 / 67 | 2.50 | 156 | 165 |  | hover  | lơ lửng sai (hover, cao 0) |
| Milotic | P2TA | 6.2 | 531 / 124 | 1.00 | 531 | 230 | 0.45 | (default)  | quá to |
| Moltres | E021 | 2.0 | 260 / 315 | 1.40 | 364 | 165 | 0.65 | hover 20 | quá to |
| Mow Rotom | PF38 | - | 77 / 122 | 0.91 | 70 | - |  | fly 70 | không có dữ liệu loài |
| Nincada | P2XA | 0.5 | 35 / 79 | 0.86 | 30 | 88 | 2.00 | (default)  | quá nhỏ |
| Ninjask | P2YA | 0.8 | 59 / 119 | 1.05 | 62 | 109 | 1.85 | (default)  | quá nhỏ |
| Palkia | E04D | 4.2 | 156 / 296 | 1.50 | 235 | 230 |  | hover  | lơ lửng sai (hover, cao 0) |
| Pidgeot | E00D | 1.5 | 86 / 198 | 1.34 | 115 | 145 |  | hover 180 | bay quá cao (180) |
| Pidgeotto | E00C | 1.1 | 82 / 178 | 1.23 | 100 | 126 |  | hover 180 | bay quá cao (180) |
| Pidgey | E00B | 0.3 | 73 / 166 | 1.12 | 81 | 70 |  | hover 180 | bay quá cao (180) |
| Pignite | EP0J | 1.0 | 131 / 341 | 1.70 | 232 | 121 | 0.90 | (default)  | quá to |
| Poliwag | E012 | 0.6 | 69 / 162 | 0.85 | 58 | 96 | 1.40 | (default)  | quá nhỏ |
| Poliwag | P4YA | 0.6 | 69 / 162 | 0.80 | 55 | 96 | 1.40 | (default)  | quá nhỏ |
| Porygon | P35A | 0.8 | 77 / 124 | 0.80 | 61 | 109 | 1.40 | (default)  | quá nhỏ |
| Ralts | EN09 | 0.4 | 245 / 258 | 0.50 | 123 | 80 | 0.35 | (default) 20 | quá to; lơ lửng sai ((default), cao 20) |
| Rapidash | E01H | 1.7 | 224 / 229 | 1.24 | 278 | 153 | 0.70 | (default)  | quá to |
| Rattata | E00T | 0.3 | 73 / 129 | 1.35 | 99 | 70 | 0.95 | (default)  | quá to |
| Rayquaza | E029 | 7.0 | 294 / 59 | 3.00 | 880 | 230 | 0.80 | hover 130 | quá to; bay quá cao (130) |
| Regigigas | E025 | 3.7 | 296 / 452 | 0.75 | 222 | 218 |  | hover  | lơ lửng sai (hover, cao 0) |
| Registeel | EL01 | 1.9 | 230 / 208 | 1.90 | 437 | 161 | 0.70 | (default)  | quá to |
| Rhyhorn | P50A | 1.0 | 98 / 152 | 0.80 | 79 | 121 | 1.25 | (default)  | quá nhỏ |
| Seadra | P3GA | 1.2 | 88 / 92 | 0.95 | 84 | 131 | 1.50 | (default)  | quá nhỏ |
| Seel | P3HA | 1.1 | 70 / 117 | 1.15 | 81 | 126 | 1.80 | (default)  | quá nhỏ |
| Serperior | EP0H | 3.3 | 448 / 322 | 1.30 | 582 | 207 | 0.45 | (default)  | quá to |
| Servine | EP0G | 0.8 | 256 / 343 | 1.20 | 307 | 109 | 0.45 | (default)  | quá to |
| Shelgon | EN0E | 1.1 | 110 / 109 | 0.80 | 88 | 126 | 1.15 | (default)  | quá nhỏ |
| Shellos (East Sea) | PF40 | - | 70 / 61 | 1.00 | 70 | - |  | foot  | không có dữ liệu loài |
| Shroomish | P3LA | 0.4 | 51 / 67 | 1.00 | 51 | 80 | 1.55 | (default)  | quá nhỏ |
| Sirfetch'd | P3MA | 0.8 | 159 / 93 | 1.25 | 198 | 109 | 0.70 | (default)  | quá to |
| Slowpoke | P3PA | 1.2 | 123 / 402 | 0.50 | 80 | 131 | 0.80 | (default)  | quá nhỏ |
| Snivy | EP0F | 0.6 | 160 / 189 | 1.20 | 192 | 96 | 0.60 | (default)  | quá to |
| Snubbull | P3VA | 0.6 | 61 / 75 | 1.00 | 61 | 96 | 1.55 | (default)  | quá nhỏ |
| Spiky-eared Pichu | PF29 | - | 70 / 69 | 1.00 | 70 | - |  | foot  | không có dữ liệu loài |
| Starmie | E04M | 1.1 | 85 / 141 | 1.00 | 85 | 126 | 1.50 | (default)  | quá nhỏ |
| Swinub | P3ZA | 0.4 | 53 / 82 | 1.00 | 53 | 80 | 1.50 | (default)  | quá nhỏ |
| Sylveon | E03X | 1.0 | 111 / 206 | 1.48 | 165 | 121 | 1.10 | (default)  | quá to |
| Tangela | P40A | 1.0 | 133 / 139 | 0.63 | 84 | 121 | 0.90 | (default)  | quá nhỏ |
| Tentacool | E02D | 0.9 | 63 / 141 | 1.20 | 76 | 115 | 1.85 | hover 45 | quá nhỏ; lơ lửng sai (hover, cao 45) |
| Tentacruel | E01I | 1.6 | 103 / 146 | 1.20 | 123 | 149 |  | hover 50 | lơ lửng sai (hover, cao 50) |
| Tepig | EP0I | 0.5 | 73 / 195 | 1.80 | 140 | 88 | 1.15 | (default)  | quá to |
| Togekiss | P45A | 1.5 | 146 / 320 | 0.50 | 73 | 145 | 1.00 | (default)  | quá nhỏ |
| Torkoal | P49A | 0.5 | 130 / 284 | 1.20 | 156 | 88 | 0.70 | (default)  | quá to |
| Torterra | EP08 | 2.2 | 88 / 117 | 5.00 | 440 | 172 | 1.95 | (default)  | quá to |
| Umbreon | E03I | 1.0 | 8 / 11 | 1.15 | 10 | 121 | 2.00 | (default)  | model lạ (cao 8); quá nhỏ |
| Uxie | EL02 | 0.3 | 131 / 138 | 1.25 | 163 | 70 | 0.55 | (default)  | quá to |
| Vibrava | P4FA | 1.1 | 40 / 55 | 2.00 | 80 | 126 | 2.00 | (default)  | quá nhỏ |
| Victini | EL07 | 0.4 | 112 / 82 | 1.15 | 128 | 80 | 0.70 | (default)  | quá to |
| Vileplume | P4GA | 1.2 | 116 / 194 | 0.60 | 70 | 131 | 1.15 | (default)  | quá nhỏ |
| Voltorb | E01D | 0.5 | 66 / 66 | 1.36 | 90 | 88 |  | hover 20 | lơ lửng sai (hover, cao 20) |
| Vulpix | E04O | 0.6 | 6 / 8 | 2.00 | 11 | 96 | 2.00 | (default)  | model lạ (cao 5); quá nhỏ |
| Wash Rotom | PF39 | - | 102 / 187 | 0.69 | 70 | - |  | fly 70 | không có dữ liệu loài |
| Weezing | E019 | 1.2 | 156 / 258 | 1.19 | 186 | 131 | 0.85 | (default) 25 | quá to |
| Wynaut | P4KA | 0.6 | 65 / 102 | 1.00 | 65 | 96 | 1.50 | (default)  | quá nhỏ |
| Zapdos | E03J | 1.6 | 169 / 262 | 1.47 | 249 | 149 | 0.90 | hover 50 | quá to |
| Abomasnow | P00A | 2.2 | 147 / 253 | 1.08 | 159 | 172 |  | (default)  | ổn |
| Absol | EN0K | 1.2 | 123 / 134 | 1.10 | 135 | 131 |  | (default)  | ổn |
| Aegislash | P4QA | 1.7 | 154 / 321 | 1.10 | 169 | 153 |  | (default)  | ổn |
| Aggron | EG2M | 2.1 | 169 / 240 | 1.00 | 169 | 169 |  | foot  | ổn |
| Aipom | EG0W | 0.8 | 109 / 154 | 1.00 | 109 | 109 |  | foot  | ổn |
| Alolan Diglett | PF08 | 0.2 | 59 / 62 | 1.00 | 59 | 59 |  | foot  | ổn |
| Alolan Dugtrio | PF09 | 0.7 | 103 / 126 | 1.00 | 103 | 103 |  | foot  | ổn |
| Alolan Exeggutor | PF11 | 10.9 | 458 / 371 | 0.50 | 229 | 230 |  | foot  | ổn |
| Alolan Grimer | PF15 | 0.7 | 103 / 111 | 1.00 | 103 | 103 |  | foot  | ổn |
| Alolan Marowak | PF19 | 1.0 | 148 / 166 | 0.82 | 121 | 121 |  | foot  | ổn |
| Alolan Meowth | PF20 | 0.4 | 80 / 97 | 1.00 | 80 | 80 |  | foot  | ổn |
| Alolan Muk | PF24 | 1.0 | 121 / 150 | 1.00 | 121 | 121 |  | foot  | ổn |
| Alolan Ninetales | PF25 | 1.1 | 202 / 435 | 0.63 | 127 | 126 |  | foot  | ổn |
| Alolan Persian | PF28 | 1.1 | 126 / 268 | 1.00 | 126 | 126 |  | foot  | ổn |
| Alolan Raticate | PF33 | 0.7 | 103 / 214 | 1.00 | 103 | 103 |  | foot  | ổn |
| Alolan Rattata | PF34 | 0.3 | 70 / 99 | 1.00 | 70 | 70 |  | foot  | ổn |
| Alolan Vulpix | PF48 | 0.6 | 76 / 292 | 0.82 | 96 | 96 |  | foot  | ổn |
| Alolan-Geodude | P03A | 0.4 | 46 / 202 | 1.00 | 81 | 80 |  | (default)  | ổn |
| Alolan-Golem | P04A | 1.7 | 158 / 150 | 0.85 | 134 | 153 |  | (default)  | ổn |
| Alolan-Graveler | P05A | 1.0 | 101 / 262 | 0.85 | 89 | 121 |  | (default)  | ổn |
| Alolan-Raichu | P06A | 0.7 | 80 / 243 | 1.10 | 107 | 103 |  | (default)  | ổn |
| Alolan-Sandshrew | P4MA | 0.7 | 91 / 70 | 1.00 | 91 | 103 |  | (default)  | ổn |
| Alolan-Sandslash | P4NA | 1.2 | 122 / 105 | 0.90 | 110 | 131 |  | (default)  | ổn |
| Altaria | P07A | 1.1 | 132 / 211 | 1.00 | 132 | 126 |  | (default)  | ổn |
| Altaria | EG35 | 1.1 | 126 / 266 | 1.00 | 126 | 126 |  | hover 65 | ổn |
| Ambipom | EG4O | 1.2 | 131 / 207 | 1.00 | 131 | 131 |  | foot  | ổn |
| Ampharos | P08A | 1.4 | 125 / 100 | 1.00 | 125 | 141 |  | (default)  | ổn |
| Anorith | EG3E | 0.7 | 103 / 192 | 1.00 | 103 | 103 |  | foot  | ổn |
| Arbok | P09A | 3.5 | 271 / 81 | 1.00 | 271 | 212 |  | (default)  | ổn |
| Arcanine | E01C | 1.9 | 136 / 225 | 0.99 | 135 | 161 |  | (default)  | ổn |
| Ariados | EG0L | 1.1 | 126 / 174 | 1.00 | 126 | 126 |  | foot  | ổn |
| Armaldo | EG3F | 1.5 | 145 / 192 | 1.00 | 145 | 145 |  | foot  | ổn |
| Aron | EG2K | 0.4 | 80 / 96 | 1.00 | 80 | 80 |  | foot  | ổn |
| Azumarill | EG0S | 0.8 | 109 / 115 | 1.00 | 109 | 109 |  | foot  | ổn |
| Azurill | EG2F | 0.2 | 44 / 146 | 1.00 | 59 | 59 |  | foot  | ổn |
| Bagon | EN0D | 0.6 | 76 / 52 | 1.09 | 83 | 96 |  | (default)  | ổn |
| Banette | EG3J | 1.1 | 126 / 147 | 1.00 | 126 | 126 |  | foot  | ổn |
| Barboach | EG3A | 0.4 | 80 / 181 | 1.00 | 80 | 80 |  | foot  | ổn |
| Bastiodon | EG4B | 1.3 | 136 / 199 | 1.00 | 136 | 136 |  | foot  | ổn |
| Bayleef | P0CA | 1.2 | 127 / 125 | 1.20 | 152 | 131 |  | (default)  | ổn |
| Beautifly | EG1V | 1.0 | 121 / 182 | 1.00 | 121 | 121 |  | hover 65 | ổn |
| Beedrill | E02K | 1.0 | 122 / 141 | 1.30 | 159 | 121 |  | (default)  | ổn |
| Beldum | EN0G | 0.6 | 112 / 48 | 0.76 | 85 | 96 |  | (default)  | ổn |
| Bellossom | P0EA | 0.4 | 204 / 196 | 0.50 | 102 | 80 |  | (default)  | ổn |
| Bellsprout | E02B | 0.7 | 68 / 61 | 1.47 | 99 | 103 |  | (default)  | ổn |
| Bibarel | EG40 | 1.0 | 121 / 200 | 1.00 | 121 | 121 |  | foot  | ổn |
| Bidoof | EG3Z | 0.5 | 88 / 140 | 1.00 | 88 | 88 |  | foot  | ổn |
| Bisharp | P4SA | 1.6 | 166 / 321 | 0.85 | 142 | 149 |  | (default)  | ổn |
| Blastoise | E000 | 1.6 | 190 / 220 | 0.71 | 135 | 149 |  | (default)  | ổn |
| Blaziken | EN02 | 1.9 | 76 / 75 | 2.00 | 153 | 161 |  | (default)  | ổn |
| Blissey | P0GA | 1.5 | 63 / 75 | 1.80 | 114 | 145 |  | (default)  | ổn |
| Bonsly | P0HA | 0.5 | 95 / 64 | 1.00 | 95 | 88 |  | (default)  | ổn |
| Braixen | EP0P | 1.0 | 122 / 108 | 1.25 | 152 | 121 |  | (default)  | ổn |
| Breloom | P0IA | 1.2 | 193 / 259 | 0.60 | 116 | 131 |  | (default)  | ổn |
| Bronzong | EG50 | 1.3 | 136 / 233 | 1.00 | 136 | 136 |  | foot  | ổn |
| Bronzor | EG4Z | 0.5 | 88 / 78 | 1.00 | 88 | 88 |  | foot  | ổn |
| Budew | EG46 | 0.2 | 59 / 34 | 1.00 | 59 | 59 |  | foot  | ổn |
| Buizel | EG4I | 0.7 | 103 / 104 | 1.00 | 103 | 103 |  | foot  | ổn |
| Buneary | EG4R | 0.4 | 80 / 49 | 1.00 | 80 | 80 |  | foot  | ổn |
| Burmy | EG4C | 0.2 | 59 / 17 | 1.00 | 59 | 59 |  | foot  | ổn |
| Butterfree | E01Q | 1.1 | 103 / 138 | 1.30 | 134 | 126 |  | (default)  | ổn |
| Buzzwole | P0JA | 2.4 | 293 / 312 | 0.70 | 205 | 179 |  | (default)  | ổn |
| Cacnea | EG33 | 0.4 | 80 / 134 | 1.00 | 80 | 80 |  | foot  | ổn |
| Cacturne | EG34 | 1.3 | 136 / 141 | 1.00 | 136 | 136 |  | foot  | ổn |
| Camerupt | EG2Z | 1.9 | 161 / 257 | 1.00 | 161 | 161 |  | foot  | ổn |
| Carnivine | EG5B | 1.4 | 141 / 195 | 1.00 | 141 | 141 |  | foot  | ổn |
| Carvanha | P0KA | 0.8 | 126 / 141 | 0.70 | 88 | 109 |  | (default)  | ổn |
| Cascoon | EG1W | 0.7 | 103 / 151 | 1.00 | 103 | 103 |  | foot  | ổn |
| Caterpie | E01N | 0.3 | 52 / 141 | 1.50 | 85 | 70 |  | (default)  | ổn |
| Celebi | PZZA | 0.6 | 22 / 23 | 4.50 | 100 | 96 |  | (default)  | ổn |
| Chandelure | P0LA | 1.0 | 133 / 274 | 1.20 | 159 | 121 |  | (default)  | ổn |
| Chansey | P0MA | 1.1 | 104 / 144 | 0.90 | 93 | 126 |  | (default)  | ổn |
| Charmander | E003 | 0.6 | 72 / 94 | 1.42 | 102 | 96 |  | (default)  | ổn |
| Charmeleon | E007 | 1.1 | 109 / 130 | 1.26 | 137 | 126 |  | (default)  | ổn |
| Chatot | EG53 | 0.5 | 88 / 148 | 1.00 | 88 | 88 |  | hover 65 | ổn |
| Cherrim | EG4L | 0.5 | 88 / 65 | 1.00 | 88 | 88 |  | foot  | ổn |
| Cherubi | EG4K | 0.4 | 80 / 71 | 1.00 | 80 | 80 |  | foot  | ổn |
| Chespin | EP0L | 0.4 | 68 / 54 | 1.20 | 81 | 80 |  | (default)  | ổn |
| Chingling | EG4W | 0.2 | 59 / 49 | 1.00 | 59 | 59 |  | foot  | ổn |
| Clamperl | EG3R | 0.4 | 80 / 83 | 1.00 | 80 | 80 |  | foot  | ổn |
| Claydol | P0PA | 1.5 | 94 / 88 | 1.10 | 104 | 145 |  | (default)  | ổn |
| Clefable | P0QA | 1.3 | 120 / 157 | 0.80 | 96 | 136 |  | (default)  | ổn |
| Clefairy | P0RA | 0.6 | 74 / 89 | 1.00 | 74 | 96 |  | (default)  | ổn |
| Cleffa | EG0N | 0.3 | 70 / 78 | 1.00 | 70 | 70 |  | foot  | ổn |
| Combee | EG4F | 0.3 | 67 / 176 | 1.00 | 70 | 70 |  | hover 65 | ổn |
| Combusken | EN01 | 0.9 | 88 / 90 | 1.30 | 115 | 115 |  | (default)  | ổn |
| Corphish | EG3C | 0.6 | 96 / 120 | 1.00 | 96 | 96 |  | foot  | ổn |
| Corsola | EG1D | 0.6 | 96 / 102 | 1.00 | 96 | 96 |  | foot  | ổn |
| Cranidos | EG48 | 0.9 | 115 / 89 | 1.00 | 115 | 115 |  | foot  | ổn |
| Crawdaunt | EG3D | 1.1 | 126 / 204 | 1.00 | 126 | 126 |  | foot  | ổn |
| Cresselia | EL06 | 1.5 | 129 / 216 | 1.20 | 154 | 145 |  | (default)  | ổn |
| Croagunk | P0UA | 0.7 | 89 / 129 | 1.00 | 89 | 103 |  | (default)  | ổn |
| Crobat | E049 | 1.8 | 240 / 451 | 0.67 | 161 | 157 |  | hover -50 | ổn |
| Croconaw | EP01 | 1.1 | 113 / 96 | 1.25 | 141 | 126 |  | (default)  | ổn |
| Cubone | P0VA | 0.4 | 62 / 64 | 1.20 | 74 | 80 |  | (default)  | ổn |
| Cursola | PF07 | 1.0 | 121 / 125 | 1.00 | 121 | 121 |  | foot  | ổn |
| Cyndaquil | P0WA | 0.5 | 79 / 110 | 1.00 | 79 | 88 |  | (default)  | ổn |
| Darmanitan | P0XA | 1.3 | 147 / 363 | 0.80 | 117 | 136 |  | (default)  | ổn |
| Darumaka | P0YA | 0.6 | 104 / 148 | 0.75 | 78 | 96 |  | (default)  | ổn |
| Deino | P0ZA | 0.8 | 115 / 109 | 0.90 | 104 | 109 |  | (default)  | ổn |
| Delcatty | EG2I | 1.1 | 126 / 133 | 1.00 | 126 | 126 |  | foot  | ổn |
| Delibird | EG1G | 0.9 | 115 / 109 | 1.00 | 115 | 115 |  | hover 65 | ổn |
| Diancie | EL0F | 0.7 | 70 / 43 | 1.25 | 87 | 103 |  | (default)  | ổn |
| Ditto | P12A | 0.3 | 48 / 63 | 1.10 | 53 | 70 |  | (default)  | ổn |
| Dodrio | EG0A | 1.8 | 157 / 76 | 1.00 | 157 | 157 |  | hover 65 | ổn |
| Doduo | EG09 | 1.4 | 141 / 68 | 1.00 | 141 | 141 |  | hover 65 | ổn |
| Donphan | EG1K | 1.1 | 126 / 221 | 0.95 | 120 | 126 |  | foot  | ổn |
| Dragonair | E01T | 4.0 | 185 / 722 | 0.90 | 260 | 225 |  | (default)  | ổn |
| Dragonite | E01K | 2.2 | 216 / 412 | 0.90 | 194 | 172 |  | hover 40 | ổn |
| Drapion | EG5A | 1.3 | 134 / 340 | 1.00 | 136 | 136 |  | foot  | ổn |
| Dratini | E01S | 1.8 | 133 / 397 | 0.90 | 143 | 157 |  | (default)  | ổn |
| Drifblim | EG4Q | 1.2 | 131 / 142 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Drifloon | EG4P | 0.4 | 80 / 191 | 1.00 | 80 | 80 |  | hover 65 | ổn |
| Drowzee | P13A | 1.0 | 102 / 143 | 1.00 | 102 | 121 |  | (default)  | ổn |
| Dunsparce | EG17 | 1.5 | 134 / 363 | 1.00 | 145 | 145 |  | foot  | ổn |
| Dusclops | P15A | 1.6 | 143 / 290 | 1.00 | 143 | 149 |  | (default)  | ổn |
| Dusknoir | P16A | 2.2 | 151 / 280 | 1.00 | 151 | 172 |  | (default)  | ổn |
| Duskull | P17A | 0.8 | 82 / 126 | 1.00 | 82 | 109 |  | (default)  | ổn |
| Dustox | EG1X | 1.2 | 131 / 156 | 1.00 | 131 | 131 |  | foot  | ổn |
| Eevee | P4VA | 0.3 | 54 / 72 | 1.20 | 65 | 70 |  | (default)  | ổn |
| Electabuzz | P19A | 1.1 | 113 / 201 | 1.15 | 130 | 126 |  | (default)  | ổn |
| Electivire | P1AA | 1.8 | 117 / 170 | 1.10 | 129 | 157 |  | (default)  | ổn |
| Elekid | P1CA | 0.6 | 87 / 116 | 1.00 | 87 | 96 |  | (default)  | ổn |
| Entei | P1DA | 2.1 | 111 / 199 | 1.30 | 145 | 169 |  | (default)  | ổn |
| Espeon | E03H | 0.9 | 170 / 250 | 0.80 | 136 | 115 |  | (default)  | ổn |
| Eternatus | EL0O | 20.0 | 285 / 513 | 0.65 | 185 | 230 |  | (default)  | ổn |
| Exeggutor | E02W | 2.0 | 158 / 235 | 0.97 | 154 | 165 |  | (default)  | ổn |
| Exploud | EG2C | 1.5 | 145 / 180 | 1.00 | 145 | 145 |  | foot  | ổn |
| Farfetch'd | P1EA | 0.8 | 74 / 121 | 1.10 | 81 | 109 |  | (default)  | ổn |
| Fearow | EG01 | 1.2 | 96 / 328 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Fennekin | EP0O | 0.4 | 56 / 57 | 1.20 | 67 | 80 |  | (default)  | ổn |
| Feraligatr | EP02 | 2.3 | 205 / 296 | 1.15 | 236 | 176 |  | (default)  | ổn |
| Finneon | EG5C | 0.4 | 80 / 121 | 1.00 | 80 | 80 |  | foot  | ổn |
| Flaaffy | P1GA | 0.8 | 98 / 103 | 1.00 | 98 | 109 |  | (default)  | ổn |
| Floatzel | EG4J | 1.1 | 126 / 112 | 1.00 | 126 | 126 |  | foot  | ổn |
| Flygon | P1HA | 2.0 | 199 / 251 | 0.90 | 179 | 165 |  | (default)  | ổn |
| Forretress | EG16 | 1.2 | 131 / 162 | 1.00 | 131 | 131 |  | foot  | ổn |
| Froakie | EP0R | 0.3 | 140 / 321 | 0.40 | 56 | 70 |  | (default)  | ổn |
| Frogadier | EP0S | 0.6 | 206 / 321 | 0.55 | 113 | 96 |  | (default)  | ổn |
| Froslass | EG5K | 1.3 | 136 / 71 | 1.00 | 136 | 136 |  | foot  | ổn |
| Furret | EG0H | 1.8 | 103 / 394 | 1.00 | 157 | 157 |  | foot  | ổn |
| Gallade | EN0C | 1.6 | 187 / 103 | 0.94 | 176 | 149 |  | (default)  | ổn |
| Galvantula | P1KA | 0.8 | 95 / 132 | 1.15 | 110 | 109 |  | (default)  | ổn |
| Garchomp | P1LA | 1.9 | 132 / 127 | 1.12 | 147 | 161 |  | (default)  | ổn |
| Gastrodon | EG4N | 0.9 | 115 / 109 | 1.00 | 115 | 115 |  | foot  | ổn |
| Genesect | EL0B | 1.5 | 165 / 280 | 0.95 | 157 | 145 |  | (default)  | ổn |
| Geodude | E00N | 0.4 | 38 / 184 | 1.45 | 107 | 80 |  | (default)  | ổn |
| Girafarig | EG14 | 1.5 | 145 / 141 | 1.00 | 145 | 145 |  | foot  | ổn |
| Glaceon | E03T | 0.8 | 132 / 197 | 1.00 | 132 | 109 |  | (default)  | ổn |
| Glalie | EG3N | 1.5 | 145 / 167 | 1.00 | 145 | 145 |  | foot  | ổn |
| Glameow | EG4U | 0.5 | 88 / 131 | 1.00 | 88 | 88 |  | foot  | ổn |
| Gligar | EG18 | 1.1 | 126 / 127 | 1.00 | 126 | 126 |  | hover 65 | ổn |
| Gliscor | EG5H | 2.0 | 165 / 146 | 1.00 | 165 | 165 |  | hover 65 | ổn |
| Gloom | P1OA | 0.8 | 87 / 101 | 0.90 | 78 | 109 |  | (default)  | ổn |
| Goldeen | EG0E | 0.6 | 96 / 232 | 1.00 | 96 | 96 |  | foot  | ổn |
| Golduck | P1PA | 1.7 | 121 / 147 | 1.00 | 121 | 153 |  | (default)  | ổn |
| Golem | E00P | 1.4 | 129 / 205 | 1.00 | 129 | 141 |  | (default)  | ổn |
| Gorebyss | EG3T | 1.8 | 141 / 394 | 1.00 | 157 | 157 |  | foot  | ổn |
| Granbull | P1QA | 1.4 | 120 / 114 | 0.90 | 108 | 141 |  | (default)  | ổn |
| Graveler | E00O | 1.0 | 106 / 277 | 0.78 | 87 | 121 |  | (default)  | ổn |
| Grimer | EG0B | 0.9 | 103 / 111 | 1.00 | 103 | 115 |  | foot  | ổn |
| Groudon | P4UA | 3.5 | 142 / 256 | 1.39 | 198 | 212 |  | (default)  | ổn |
| Growlithe | E02F | 0.7 | 122 / 290 | 0.88 | 107 | 103 |  | (default)  | ổn |
| Grumpig | EG31 | 0.9 | 115 / 112 | 1.00 | 115 | 115 |  | foot  | ổn |
| Gulpin | EG2U | 0.4 | 80 / 103 | 1.00 | 80 | 80 |  | foot  | ổn |
| Gyarados | E03F | 6.5 | 73 / 120 | 3.00 | 219 | 230 |  | (default)  | ổn |
| Happiny | EG52 | 0.6 | 96 / 69 | 1.00 | 96 | 96 |  | foot  | ổn |
| Hariyama | EG2E | 2.3 | 176 / 287 | 1.00 | 176 | 176 |  | foot  | ổn |
| Heracross | P1SA | 1.5 | 121 / 174 | 1.20 | 145 | 145 |  | (default)  | ổn |
| Hippopotas | EG57 | 0.8 | 109 / 179 | 1.00 | 109 | 109 |  | foot  | ổn |
| Hippowdon | EG58 | 2.0 | 165 / 395 | 1.00 | 165 | 165 |  | foot  | ổn |
| Hitmonchan | E01Z | 1.4 | 49 / 64 | 3.20 | 157 | 141 |  | (default)  | ổn |
| Hitmonlee | E03Y | 1.5 | 140 / 224 | 1.11 | 156 | 145 |  | (default)  | ổn |
| Hitmontop | E03Z | 1.4 | 125 / 121 | 0.86 | 107 | 141 |  | (default)  | ổn |
| Ho-Oh | P1TA | 3.8 | 117 / 252 | 1.70 | 198 | 220 |  | (default)  | ổn |
| Honchkrow | EG4T | 0.9 | 87 / 288 | 1.00 | 115 | 115 |  | hover 65 | ổn |
| Hoothoot | P1UA | 0.7 | 78 / 94 | 1.00 | 78 | 103 |  | (default)  | ổn |
| Hoppip | EG0T | 0.4 | 80 / 98 | 1.00 | 80 | 80 |  | hover 65 | ổn |
| Horsea | P1VA | 0.4 | 48 / 42 | 1.20 | 57 | 80 |  | (default)  | ổn |
| Houndoom | P1WA | 1.4 | 115 / 194 | 1.15 | 132 | 141 |  | (default)  | ổn |
| Houndour | P1XA | 0.6 | 55 / 61 | 1.70 | 94 | 96 |  | (default)  | ổn |
| Huntail | EG3S | 1.7 | 109 / 384 | 1.00 | 153 | 153 |  | foot  | ổn |
| Hypno | P1ZA | 1.6 | 178 / 197 | 0.95 | 169 | 149 |  | (default)  | ổn |
| Igglybuff | EG0O | 0.3 | 70 / 54 | 1.00 | 70 | 70 |  | foot  | ổn |
| Illumise | EG2S | 0.6 | 96 / 80 | 1.00 | 96 | 96 |  | foot  | ổn |
| Infernape | EP0B | 1.2 | 62 / 72 | 2.80 | 173 | 131 |  | (default)  | ổn |
| Ivysaur | E001 | 1.0 | 99 / 129 | 0.92 | 91 | 121 |  | (default)  | ổn |
| Jirachi | P21A | 0.3 | 53 / 66 | 1.30 | 69 | 70 |  | (default)  | ổn |
| Jolteon | E01E | 0.8 | 101 / 104 | 1.24 | 125 | 109 |  | (default)  | ổn |
| Joltik | P22A | 0.1 | 48 / 69 | 1.10 | 53 | 55 |  | (default)  | ổn |
| Jumpluff | EG0V | 0.8 | 109 / 126 | 1.00 | 109 | 109 |  | hover 65 | ổn |
| Jynx | P23A | 1.4 | 96 / 166 | 1.10 | 105 | 141 |  | (default)  | ổn |
| Kabuto | E03P | 0.5 | 104 / 103 | 0.80 | 83 | 88 |  | (default)  | ổn |
| Kabutops | E035 | 1.3 | 135 / 185 | 0.87 | 118 | 136 |  | (default)  | ổn |
| Kakuna | E02J | 0.6 | 82 / 142 | 1.45 | 118 | 96 |  | (default)  | ổn |
| Kangaskhan | E02P | 2.2 | 149 / 196 | 1.34 | 200 | 172 |  | (default)  | ổn |
| Kecleon | EG3H | 1.0 | 121 / 118 | 1.00 | 121 | 121 |  | foot  | ổn |
| Kingambit | P4TA | 2.0 | 272 / 315 | 0.70 | 191 | 165 |  | (default)  | ổn |
| Kleavor | PF17 | 1.8 | 157 / 216 | 1.00 | 157 | 157 |  | foot  | ổn |
| Krabby | E03C | 0.4 | 76 / 108 | 1.07 | 81 | 80 |  | (default)  | ổn |
| Kricketot | EG41 | 0.3 | 70 / 50 | 1.00 | 70 | 70 |  | foot  | ổn |
| Kricketune | EG42 | 1.0 | 121 / 100 | 1.00 | 121 | 121 |  | foot  | ổn |
| Kyurem | EL0A | 3.0 | 293 / 535 | 0.65 | 191 | 198 |  | (default)  | ổn |
| Lairon | EG2L | 0.9 | 115 / 206 | 1.00 | 115 | 115 |  | foot  | ổn |
| Lampent | P27A | 0.6 | 60 / 140 | 1.20 | 72 | 96 |  | (default)  | ổn |
| Lapras | P29A | 2.5 | 149 / 257 | 1.00 | 149 | 182 |  | (default)  | ổn |
| Larvitar | EN06 | 0.6 | 76 / 54 | 1.20 | 92 | 96 |  | (default)  | ổn |
| Latias & Latios | PV2A | 1.4 | 106 / 196 | 1.20 | 127 | 141 |  | (default)  | ổn |
| Leafeon | P2BA | 1.0 | 103 / 169 | 1.20 | 124 | 121 |  | (default)  | ổn |
| Leafleon | E03S | 1.0 | 103 / 169 | 1.35 | 139 | 121 |  | (default)  | ổn |
| Ledian | EG0J | 1.4 | 141 / 89 | 1.00 | 141 | 141 |  | hover 65 | ổn |
| Ledyba | EG0I | 1.0 | 121 / 140 | 1.00 | 121 | 121 |  | hover 65 | ổn |
| Lickilicky | EG5F | 1.7 | 153 / 188 | 1.00 | 153 | 153 |  | foot  | ổn |
| Lickitung | EG0D | 1.2 | 131 / 271 | 1.00 | 131 | 131 |  | foot  | ổn |
| Lileep | P2CA | 1.0 | 107 / 50 | 1.00 | 107 | 121 |  | (default)  | ổn |
| Linoone | EG1S | 0.5 | 76 / 221 | 1.00 | 88 | 88 |  | foot  | ổn |
| Litten | EP0U | 0.4 | 70 / 187 | 0.80 | 60 | 80 |  | (default)  | ổn |
| Litwick | P2DA | 0.3 | 55 / 33 | 1.30 | 72 | 70 |  | (default)  | ổn |
| Lopunny | EG4S | 1.2 | 131 / 218 | 1.00 | 131 | 131 |  | foot  | ổn |
| Loudred | EG2B | 1.0 | 121 / 185 | 1.00 | 121 | 121 |  | foot  | ổn |
| Lucario | EN0J | 1.2 | 138 / 116 | 1.00 | 138 | 131 |  | (default)  | ổn |
| Ludicolo | P2GA | 1.5 | 144 / 208 | 0.96 | 138 | 145 |  | (default)  | ổn |
| Lugia | EG1O | 5.2 | 230 / 429 | 1.00 | 230 | 230 |  | hover 65 | ổn |
| Lumineon | EG5D | 1.2 | 131 / 169 | 1.00 | 131 | 131 |  | foot  | ổn |
| Lunala | EL0J | 4.0 | 505 / 884 | 0.40 | 202 | 225 |  | (default)  | ổn |
| Lunatone | EG38 | 1.0 | 121 / 112 | 1.00 | 121 | 121 |  | foot  | ổn |
| Luvdisc | EG3V | 0.6 | 96 / 94 | 1.00 | 96 | 96 |  | foot  | ổn |
| Luxio | EG44 | 0.9 | 115 / 165 | 1.00 | 115 | 115 |  | foot  | ổn |
| Luxray | EG45 | 1.4 | 141 / 159 | 1.00 | 141 | 141 |  | foot  | ổn |
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
| Makuhita | EG2D | 1.0 | 121 / 165 | 1.00 | 121 | 121 |  | foot  | ổn |
| Mamoswine | P2MA | 2.5 | 184 / 274 | 0.80 | 147 | 182 |  | (default)  | ổn |
| Manaphy | EG5N | 0.3 | 70 / 75 | 1.00 | 70 | 70 |  | foot  | ổn |
| Manectric | P2NA | 1.5 | 132 / 115 | 1.05 | 138 | 145 |  | (default)  | ổn |
| Mankey | E02S | 0.5 | 66 / 118 | 1.44 | 95 | 88 |  | (default)  | ổn |
| Mantine | EG1H | 2.1 | 104 / 422 | 1.00 | 169 | 169 |  | hover 65 | ổn |
| Mantyke | EG5E | 1.0 | 121 / 240 | 1.00 | 121 | 121 |  | hover 65 | ổn |
| Mareep | P2OA | 0.6 | 62 / 118 | 1.20 | 74 | 96 |  | (default)  | ổn |
| Marill | EG0R | 0.4 | 80 / 127 | 1.00 | 80 | 80 |  | foot  | ổn |
| Marowak | P2PA | 1.0 | 116 / 107 | 0.87 | 101 | 121 |  | (default)  | ổn |
| Masquerain | EG26 | 0.8 | 109 / 165 | 1.00 | 109 | 109 |  | hover 65 | ổn |
| Mawile | EG2J | 0.6 | 96 / 158 | 1.00 | 96 | 96 |  | foot  | ổn |
| Medicham | EG2O | 1.3 | 136 / 129 | 1.00 | 136 | 136 |  | foot  | ổn |
| Meditite | EG2N | 0.6 | 96 / 78 | 1.00 | 96 | 96 |  | foot  | ổn |
| Meganium | PV0A | 1.8 | 330 / 355 | 0.60 | 198 | 157 |  | (default)  | ổn |
| Meowth | P2QA | 0.4 | 79 / 90 | 1.00 | 79 | 80 |  | (default)  | ổn |
| Metagross | EN0I | 1.6 | 128 / 224 | 0.90 | 116 | 149 |  | (default)  | ổn |
| Metang | EN0H | 1.2 | 96 / 347 | 0.82 | 114 | 131 |  | (default)  | ổn |
| Metapod | E01P | 0.7 | 75 / 145 | 1.50 | 113 | 103 |  | (default)  | ổn |
| Mightyena | EG1Q | 1.0 | 121 / 179 | 1.00 | 121 | 121 |  | foot  | ổn |
| Miltank | EG1N | 1.2 | 131 / 165 | 0.95 | 125 | 131 |  | foot  | ổn |
| Mime Jr. | EG51 | 0.6 | 96 / 74 | 1.00 | 96 | 96 |  | foot  | ổn |
| Minun | EG2Q | 0.4 | 80 / 71 | 1.00 | 80 | 80 |  | foot  | ổn |
| Misdreavus | P2UA | 0.7 | 73 / 87 | 1.00 | 73 | 103 |  | (default)  | ổn |
| Mismagius | P2VA | 0.9 | 117 / 74 | 1.10 | 129 | 115 |  | (default)  | ổn |
| Monferno | EP0A | 0.9 | 88 / 119 | 1.73 | 152 | 115 |  | (default)  | ổn |
| Mothim | EG4E | 0.9 | 115 / 250 | 1.00 | 115 | 115 |  | hover 65 | ổn |
| Mr. Mime | P2WA | 1.3 | 186 / 295 | 0.60 | 112 | 136 |  | (default)  | ổn |
| Mr. Rime | PF23 | 1.5 | 145 / 175 | 1.00 | 145 | 145 |  | foot  | ổn |
| Mr.mime | E040 | 1.3 | 186 / 294 | 0.70 | 130 | 136 |  | (default)  | ổn |
| Mudkip | EP03 | 0.4 | 40 / 41 | 1.40 | 56 | 80 |  | (default)  | ổn |
| Muk | EG0C | 1.2 | 121 / 151 | 1.00 | 121 | 131 |  | foot  | ổn |
| Munchlax | EG55 | 0.6 | 96 / 92 | 1.00 | 96 | 96 |  | foot  | ổn |
| Murkrow | EG12 | 0.5 | 88 / 105 | 1.00 | 88 | 88 |  | hover 65 | ổn |
| Natu | EG0P | 0.2 | 59 / 70 | 1.00 | 59 | 59 |  | hover 65 | ổn |
| Necrozma | EL0K | 2.4 | 174 / 239 | 1.05 | 183 | 179 |  | (default)  | ổn |
| Nidoking | E01J | 1.4 | 141 / 253 | 1.12 | 158 | 141 |  | (default)  | ổn |
| Nidoqueen | EG04 | 1.3 | 136 / 187 | 1.00 | 136 | 136 |  | foot  | ổn |
| Nidoran | E01M | 0.5 | 55 / 91 | 1.37 | 75 | 88 |  | (default)  | ổn |
| Nidoran F | EG02 | 0.4 | 80 / 90 | 1.00 | 80 | 80 |  | foot  | ổn |
| Nidorina | EG03 | 0.8 | 109 / 142 | 1.00 | 109 | 109 |  | foot  | ổn |
| Nidorino | E01L | 0.9 | 96 / 141 | 0.91 | 88 | 115 |  | (default)  | ổn |
| Ninetales | E04P | 1.1 | 76 / 208 | 2.00 | 167 | 126 |  | (default)  | ổn |
| Noctowl | P2ZA | 1.6 | 126 / 215 | 0.85 | 107 | 149 |  | (default)  | ổn |
| Nosepass | EG2G | 1.0 | 121 / 172 | 1.00 | 121 | 121 |  | foot  | ổn |
| Numel | EG2Y | 0.7 | 103 / 126 | 1.00 | 103 | 103 |  | foot  | ổn |
| Nuzleaf | EG1Z | 1.0 | 121 / 106 | 1.00 | 121 | 121 |  | foot  | ổn |
| Obstagoon | PF26 | 1.6 | 149 / 150 | 1.00 | 149 | 149 |  | foot  | ổn |
| Octillery | EG1F | 0.9 | 115 / 178 | 1.00 | 115 | 115 |  | foot  | ổn |
| Oddish | P30A | 0.5 | 75 / 86 | 1.00 | 75 | 88 |  | (default)  | ổn |
| Omanyte | E03Q | 0.4 | 176 / 240 | 0.50 | 88 | 80 |  | (default)  | ổn |
| Omastar | E03R | 1.0 | 100 / 240 | 1.05 | 105 | 121 |  | (default)  | ổn |
| Onix | E03U | 8.8 | 143 / 639 | 0.90 | 230 | 230 |  | (default)  | ổn |
| Pachirisu | EG4H | 0.4 | 80 / 95 | 1.00 | 80 | 80 |  | foot  | ổn |
| Paras | EG05 | 0.3 | 70 / 103 | 1.00 | 70 | 70 |  | foot  | ổn |
| Parasect | EG06 | 1.0 | 121 / 112 | 1.00 | 121 | 121 |  | foot  | ổn |
| Pawniard | P4RA | 0.5 | 69 / 234 | 1.10 | 103 | 88 |  | (default)  | ổn |
| Pelipper | EG24 | 1.2 | 131 / 299 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Perrserker | PF27 | 0.8 | 109 / 188 | 1.00 | 109 | 109 |  | foot  | ổn |
| Persian | P31A | 1.0 | 93 / 207 | 1.00 | 93 | 121 |  | (default)  | ổn |
| Phanpy | EG1J | 0.5 | 88 / 130 | 1.00 | 88 | 88 |  | foot  | ổn |
| Phione | EG5M | 0.4 | 80 / 124 | 1.00 | 80 | 80 |  | foot  | ổn |
| Pichu | EG0M | 0.3 | 70 / 66 | 1.00 | 70 | 70 |  | foot  | ổn |
| Pikachu | E005 | 0.4 | 68 / 62 | 1.17 | 79 | 80 |  | (default)  | ổn |
| Piloswine | P32A | 1.1 | 133 / 164 | 1.00 | 133 | 126 |  | (default)  | ổn |
| Pineco | EG15 | 0.6 | 96 / 93 | 1.00 | 96 | 96 |  | foot  | ổn |
| Pinsir | E03W | 1.5 | 119 / 198 | 1.17 | 139 | 145 |  | (default)  | ổn |
| Piplup | EP0C | 0.4 | 236 / 145 | 0.30 | 71 | 80 |  | (default)  | ổn |
| Plusle | EG2P | 0.4 | 80 / 71 | 1.00 | 80 | 80 |  | foot  | ổn |
| Politoed | P34A | 1.1 | 116 / 128 | 0.90 | 104 | 126 |  | (default)  | ổn |
| Poliwhirl | E013 | 1.0 | 97 / 168 | 1.00 | 97 | 121 |  | (default)  | ổn |
| Poliwhirl | P4ZA | 1.0 | 97 / 168 | 0.90 | 87 | 121 |  | (default)  | ổn |
| Poliwrath | E014 | 1.3 | 118 / 268 | 0.92 | 108 | 136 |  | (default)  | ổn |
| Ponyta | E01B | 1.0 | 112 / 150 | 1.35 | 151 | 121 |  | (default)  | ổn |
| Poochyena | EG1P | 0.5 | 88 / 127 | 1.00 | 88 | 88 |  | foot  | ổn |
| Porygon-Z | EG5I | 0.9 | 115 / 121 | 1.00 | 115 | 115 |  | foot  | ổn |
| Porygon2 | PV1A | 0.6 | 73 / 120 | 1.00 | 73 | 96 |  | (default)  | ổn |
| Primeape | E02T | 1.0 | 127 / 205 | 0.80 | 101 | 121 |  | (default)  | ổn |
| Prinplup | EP0D | 0.8 | 272 / 198 | 0.50 | 136 | 109 |  | (default)  | ổn |
| Probopass | EG5J | 1.4 | 141 / 191 | 1.00 | 141 | 141 |  | foot  | ổn |
| Psyduck | P36A | 0.8 | 157 / 155 | 0.72 | 113 | 109 |  | (default)  | ổn |
| Pupitar | EN07 | 1.2 | 88 / 74 | 1.20 | 106 | 131 |  | (default)  | ổn |
| Purugly | EG4V | 1.0 | 121 / 128 | 1.00 | 121 | 121 |  | foot  | ổn |
| Quagsire | EG11 | 1.4 | 141 / 186 | 1.00 | 141 | 141 |  | foot  | ổn |
| Quilava | P38A | 0.9 | 97 / 124 | 1.00 | 97 | 115 |  | (default)  | ổn |
| Quilladin | EP0M | 0.7 | 107 / 129 | 1.20 | 128 | 103 |  | (default)  | ổn |
| Qwilfish | EG19 | 0.5 | 88 / 177 | 1.00 | 88 | 88 |  | foot  | ổn |
| Raichu | E006 | 0.8 | 81 / 232 | 1.28 | 119 | 109 |  | (default)  | ổn |
| Raikou | P39A | 1.9 | 113 / 158 | 1.40 | 159 | 161 |  | (default)  | ổn |
| Rampardos | EG49 | 1.6 | 149 / 151 | 1.00 | 149 | 149 |  | foot  | ổn |
| Raticate | E00U | 0.7 | 73 / 164 | 1.45 | 106 | 103 |  | (default)  | ổn |
| Regice | EL00 | 1.8 | 180 / 200 | 0.64 | 115 | 157 |  | (default)  | ổn |
| Regirock | P3BA | 1.7 | 158 / 156 | 1.20 | 190 | 153 |  | (default)  | ổn |
| Relicanth | EG3U | 1.0 | 121 / 174 | 1.00 | 121 | 121 |  | foot  | ổn |
| Remoraid | EG1E | 0.6 | 96 / 121 | 1.00 | 96 | 96 |  | foot  | ổn |
| Reshiram | EL08 | 3.2 | 261 / 800 | 0.55 | 176 | 204 |  | (default)  | ổn |
| Rhydon | E02Z | 1.9 | 179 / 278 | 0.89 | 160 | 161 |  | (default)  | ổn |
| Rhydon | P51A | 1.9 | 179 / 278 | 0.85 | 152 | 161 |  | (default)  | ổn |
| Rhyhorn | E02Y | 1.0 | 98 / 152 | 1.12 | 110 | 121 |  | (default)  | ổn |
| Rhyperior | P3CA | 2.4 | 71 / 100 | 2.00 | 142 | 179 |  | (default)  | ổn |
| Riolu | EG56 | 0.7 | 103 / 94 | 1.00 | 103 | 103 |  | foot  | ổn |
| Roselia | EG2T | 0.3 | 70 / 87 | 1.00 | 70 | 70 |  | foot  | ổn |
| Roserade | EG47 | 0.9 | 115 / 110 | 1.00 | 115 | 115 |  | foot  | ổn |
| Rotom | EG5L | 0.3 | 70 / 150 | 1.00 | 70 | 70 |  | foot  | ổn |
| Sableye | P3DA | 0.5 | 71 / 83 | 1.20 | 85 | 88 |  | (default)  | ổn |
| Salamence | EN0F | 1.5 | 187 / 437 | 0.80 | 150 | 145 |  | hover 40 | ổn |
| Sandshrew | E00A | 0.6 | 70 / 161 | 1.18 | 82 | 96 |  | (default)  | ổn |
| Sandslash | E00F | 1.0 | 119 / 225 | 1.08 | 129 | 121 |  | (default)  | ổn |
| Sceptile | EN05 | 1.7 | 139 / 149 | 1.00 | 139 | 153 |  | (default)  | ổn |
| Scizor | E03M | 1.8 | 156 / 132 | 1.19 | 186 | 157 |  | (default)  | ổn |
| Scyther | E03L | 1.5 | 135 / 270 | 0.99 | 133 | 145 |  | (default)  | ổn |
| Seaking | EG0F | 1.3 | 136 / 189 | 1.00 | 136 | 136 |  | foot  | ổn |
| Sealeo | EG3P | 1.1 | 126 / 283 | 1.00 | 126 | 126 |  | foot  | ổn |
| Seedot | EG1Y | 0.5 | 88 / 66 | 1.00 | 88 | 88 |  | foot  | ổn |
| Sentret | EG0G | 0.8 | 109 / 64 | 1.00 | 109 | 109 |  | foot  | ổn |
| Seviper | EG37 | 2.7 | 189 / 38 | 1.00 | 189 | 189 |  | foot  | ổn |
| Sharpedo | P3IA | 1.8 | 206 / 200 | 0.55 | 113 | 157 |  | (default)  | ổn |
| Shaymin | EG5O | 0.2 | 59 / 82 | 1.00 | 59 | 59 |  | foot  | ổn |
| Shedinja | P3JA | 0.8 | 79 / 97 | 1.00 | 79 | 109 |  | (default)  | ổn |
| Shellder | E02E | 0.3 | 86 / 150 | 0.65 | 56 | 70 |  | (default)  | ổn |
| Shellos | EG4M | 0.3 | 70 / 61 | 1.00 | 70 | 70 |  | foot  | ổn |
| Shieldon | EG4A | 0.5 | 88 / 90 | 1.00 | 88 | 88 |  | foot  | ổn |
| Shiftry | EG20 | 1.3 | 136 / 186 | 1.00 | 136 | 136 |  | foot  | ổn |
| Shinx | EG43 | 0.5 | 88 / 129 | 1.00 | 88 | 88 |  | foot  | ổn |
| Shuckle | EG1A | 0.6 | 96 / 111 | 1.00 | 96 | 96 |  | foot  | ổn |
| Shuppet | EG3I | 0.6 | 96 / 68 | 1.00 | 96 | 96 |  | foot  | ổn |
| Silcoon | EG1U | 0.6 | 96 / 142 | 1.00 | 96 | 96 |  | foot  | ổn |
| Skarmory | EG1I | 1.7 | 153 / 185 | 1.00 | 153 | 153 |  | hover 65 | ổn |
| Skiploom | EG0U | 0.6 | 96 / 173 | 1.00 | 96 | 96 |  | hover 65 | ổn |
| Skitty | EG2H | 0.6 | 96 / 125 | 1.00 | 96 | 96 |  | foot  | ổn |
| Skorupi | EG59 | 0.8 | 88 / 273 | 1.00 | 109 | 109 |  | foot  | ổn |
| Skuntank | EG4Y | 1.0 | 121 / 201 | 1.00 | 121 | 121 |  | foot  | ổn |
| Slaking | EG29 | 2.0 | 165 / 277 | 1.00 | 165 | 165 |  | foot  | ổn |
| Slakoth | EG27 | 0.8 | 109 / 217 | 1.00 | 109 | 109 |  | foot  | ổn |
| Slowbro | P3NA | 1.6 | 225 / 324 | 0.50 | 113 | 149 |  | (default)  | ổn |
| Slowking | P3OA | 2.0 | 295 / 261 | 0.50 | 148 | 165 |  | (default)  | ổn |
| Slugma | P3QA | 0.7 | 64 / 75 | 1.19 | 77 | 103 |  | (default)  | ổn |
| Smeargle | EG1M | 1.2 | 131 / 260 | 1.00 | 131 | 131 |  | foot  | ổn |
| Smoochum | P3RA | 0.4 | 60 / 47 | 1.25 | 75 | 80 |  | (default)  | ổn |
| Sneasel | P3SA | 0.9 | 101 / 134 | 0.90 | 91 | 115 |  | (default)  | ổn |
| Sneasler | PF44 | 1.3 | 136 / 117 | 1.00 | 136 | 136 |  | foot  | ổn |
| Snorlax | P3TA | 2.1 | 177 / 225 | 1.00 | 177 | 169 |  | (default)  | ổn |
| Snorunt | EG3M | 0.7 | 103 / 100 | 1.00 | 103 | 103 |  | foot  | ổn |
| Snover | P3UA | 1.0 | 88 / 153 | 1.00 | 88 | 121 |  | (default)  | ổn |
| Solgaleo | EL0I | 3.4 | 365 / 714 | 0.45 | 164 | 210 |  | (default)  | ổn |
| Solrock | EG39 | 1.2 | 131 / 144 | 1.00 | 131 | 131 |  | foot  | ổn |
| Spearow | EG00 | 0.3 | 70 / 152 | 1.00 | 70 | 70 |  | hover 65 | ổn |
| Spheal | EG3O | 0.8 | 109 / 140 | 1.00 | 109 | 109 |  | foot  | ổn |
| Spinarak | EG0K | 0.5 | 81 / 221 | 1.00 | 88 | 88 |  | foot  | ổn |
| Spinda | EG32 | 1.1 | 126 / 99 | 1.00 | 126 | 126 |  | foot  | ổn |
| Spiritomb | EG54 | 1.0 | 121 / 126 | 1.00 | 121 | 121 |  | foot  | ổn |
| Spoink | EG30 | 0.7 | 103 / 65 | 1.00 | 103 | 103 |  | foot  | ổn |
| Squirtle | E004 | 0.5 | 69 / 74 | 1.29 | 88 | 88 |  | (default)  | ổn |
| Stantler | EG1L | 1.4 | 141 / 115 | 1.00 | 141 | 141 |  | foot  | ổn |
| Staraptor | EG3Y | 1.2 | 108 / 328 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Staravia | EG3X | 0.6 | 96 / 210 | 1.00 | 96 | 96 |  | hover 65 | ổn |
| Starly | EG3W | 0.3 | 63 / 176 | 1.00 | 70 | 70 |  | hover 65 | ổn |
| Staryu | E04N | 0.8 | 83 / 141 | 1.00 | 83 | 109 |  | (default)  | ổn |
| Steelix | E03V | 9.2 | 101 / 551 | 0.90 | 198 | 230 |  | (default)  | ổn |
| Stunky | EG4X | 0.4 | 80 / 111 | 1.00 | 80 | 80 |  | foot  | ổn |
| Sudowoodo | P3WA | 1.2 | 160 / 185 | 0.92 | 148 | 131 |  | (default)  | ổn |
| Suicune | P3XA | 2.0 | 132 / 393 | 1.00 | 157 | 165 |  | (default)  | ổn |
| Sunflora | EG0Y | 0.8 | 109 / 122 | 1.00 | 109 | 109 |  | foot  | ổn |
| Sunkern | EG0X | 0.3 | 70 / 68 | 1.00 | 70 | 70 |  | foot  | ổn |
| Surskit | EG25 | 0.5 | 88 / 99 | 1.00 | 88 | 88 |  | foot  | ổn |
| Swablu | P3YA | 0.4 | 76 / 163 | 0.80 | 61 | 80 |  | (default)  | ổn |
| Swalot | EG2V | 1.7 | 153 / 175 | 1.00 | 153 | 153 |  | foot  | ổn |
| Swampert | EP05 | 1.5 | 153 / 222 | 1.20 | 183 | 145 |  | (default)  | ổn |
| Swellow | EG22 | 0.7 | 103 / 254 | 1.00 | 103 | 103 |  | hover 65 | ổn |
| Taillow | EG21 | 0.3 | 46 / 176 | 1.00 | 70 | 70 |  | hover 65 | ổn |
| Tangrowth | P41A | 2.0 | 107 / 346 | 1.10 | 152 | 165 |  | (default)  | ổn |
| Tauros | E018 | 1.4 | 132 / 279 | 0.92 | 121 | 141 |  | (default)  | ổn |
| Tauros Aqua | P42A | 1.4 | 85 / 211 | 1.60 | 136 | 141 |  | (default)  | ổn |
| Tauros Blaze | P43A | 1.4 | 95 / 214 | 1.60 | 152 | 141 |  | (default)  | ổn |
| Tauros Combat | P44A | 1.4 | 84 / 177 | 1.60 | 135 | 141 |  | (default)  | ổn |
| Teddiursa | EG1B | 0.6 | 96 / 80 | 1.00 | 96 | 96 |  | foot  | ổn |
| Togepi | P46A | 0.3 | 59 / 63 | 1.34 | 79 | 70 |  | (default)  | ổn |
| Togetic | P47A | 0.6 | 87 / 56 | 1.04 | 90 | 96 |  | (default)  | ổn |
| Torchic | EN00 | 0.4 | 108 / 141 | 0.86 | 93 | 80 |  | (default)  | ổn |
| Torracat | EP0V | 0.7 | 111 / 233 | 1.20 | 133 | 103 |  | (default)  | ổn |
| Totodile | EP00 | 0.6 | 111 / 120 | 0.70 | 78 | 96 |  | (default)  | ổn |
| Toxicroak | P4AA | 1.3 | 141 / 244 | 0.80 | 112 | 136 |  | (default)  | ổn |
| Trapinch | P4BA | 0.7 | 242 / 411 | 0.30 | 73 | 103 |  | (default)  | ổn |
| Treecko | EN03 | 0.5 | 51 / 98 | 1.35 | 69 | 88 |  | (default)  | ổn |
| Tropius | EG3K | 2.0 | 165 / 178 | 1.00 | 165 | 165 |  | hover 65 | ổn |
| Turtwig | EP06 | 0.4 | 54 / 56 | 1.50 | 81 | 80 |  | (default)  | ổn |
| Typhlosion | P4DA | 1.7 | 126 / 123 | 1.10 | 138 | 153 |  | (default)  | ổn |
| Tyranitar | EN08 | 2.0 | 165 / 163 | 1.05 | 174 | 165 |  | (default)  | ổn |
| Tyrogue | P4EA | 0.7 | 84 / 85 | 1.15 | 96 | 103 |  | (default)  | ổn |
| Unown | EG13 | 0.5 | 88 / 79 | 1.00 | 88 | 88 |  | hover 65 | ổn |
| Ursaluna | PF46 | 2.4 | 179 / 190 | 1.00 | 179 | 179 |  | foot  | ổn |
| Ursaring | EG1C | 1.8 | 157 / 205 | 1.00 | 157 | 157 |  | foot  | ổn |
| Vaporeon | E037 | 1.0 | 106 / 218 | 1.14 | 120 | 121 |  | (default)  | ổn |
| Venomoth | EG08 | 1.5 | 145 / 202 | 1.00 | 145 | 145 |  | foot  | ổn |
| Venonat | EG07 | 1.0 | 121 / 85 | 1.00 | 121 | 121 |  | foot  | ổn |
| Venusaur | E002 | 2.0 | 138 / 219 | 0.93 | 129 | 165 |  | (default)  | ổn |
| Vespiquen | EG4G | 1.2 | 131 / 148 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Victreebel | E02C | 1.7 | 139 / 384 | 0.92 | 141 | 153 |  | (default)  | ổn |
| Vigoroth | EG28 | 1.4 | 141 / 230 | 1.00 | 141 | 141 |  | foot  | ổn |
| Volbeat | EG2R | 0.7 | 103 / 96 | 1.00 | 103 | 103 |  | foot  | ổn |
| Volcanion | EL0H | 1.7 | 177 / 178 | 1.00 | 177 | 153 |  | (default)  | ổn |
| Wailmer | EG2W | 2.0 | 165 / 296 | 1.00 | 165 | 165 |  | foot  | ổn |
| Wailord | EG2X | 14.5 | 230 / 557 | 1.00 | 230 | 230 |  | foot  | ổn |
| Walrein | EG3Q | 1.4 | 141 / 225 | 1.00 | 141 | 141 |  | foot  | ổn |
| Wartortle | E009 | 1.0 | 128 / 119 | 0.91 | 117 | 121 |  | (default)  | ổn |
| Weavile | P4HA | 1.1 | 117 / 108 | 1.00 | 117 | 126 |  | (default)  | ổn |
| Weedle | E02I | 0.3 | 60 / 138 | 1.50 | 89 | 70 |  | (default)  | ổn |
| Weepinbell | E01A | 1.0 | 118 / 157 | 0.80 | 94 | 121 |  | (default)  | ổn |
| Whiscash | EG3B | 0.9 | 115 / 219 | 1.00 | 115 | 115 |  | foot  | ổn |
| Whismur | EG2A | 0.6 | 96 / 96 | 1.00 | 96 | 96 |  | foot  | ổn |
| Wigglytuff | P4IA | 1.0 | 127 / 138 | 0.80 | 102 | 121 |  | (default)  | ổn |
| Wingull | EG23 | 0.6 | 32 / 240 | 1.00 | 96 | 96 |  | hover 65 | ổn |
| Wobbuffet | P4JA | 1.3 | 109 / 123 | 1.00 | 109 | 136 |  | (default)  | ổn |
| Wooper | EG10 | 0.4 | 80 / 106 | 1.00 | 80 | 80 |  | foot  | ổn |
| Wormadam | EG4D | 0.5 | 88 / 75 | 1.00 | 88 | 88 |  | foot  | ổn |
| Wurmple | EG1T | 0.3 | 70 / 90 | 1.00 | 70 | 70 |  | foot  | ổn |
| Wyrdeer | PF50 | 1.8 | 157 / 109 | 1.00 | 157 | 157 |  | foot  | ổn |
| Xatu | EG0Q | 1.5 | 145 / 107 | 1.00 | 145 | 145 |  | hover 65 | ổn |
| Xerneas | EL0C | 3.0 | 496 / 442 | 0.42 | 209 | 198 |  | (default)  | ổn |
| Yanma | EG0Z | 1.2 | 127 / 328 | 1.00 | 131 | 131 |  | hover 65 | ổn |
| Yanmega | EG5G | 1.9 | 142 / 403 | 1.00 | 161 | 161 |  | hover 65 | ổn |
| Yveltal | EL0D | 5.8 | 200 / 410 | 0.85 | 170 | 230 |  | (default)  | ổn |
| Zacian | EL0N | 2.8 | 221 / 227 | 0.85 | 188 | 192 |  | (default)  | ổn |
| Zangoose | EG36 | 1.3 | 136 / 184 | 1.00 | 136 | 136 |  | foot  | ổn |
| Zekrom | EL09 | 2.9 | 254 / 300 | 0.72 | 183 | 195 |  | (default)  | ổn |
| Zigzagoon | EG1R | 0.4 | 80 / 135 | 1.00 | 80 | 80 |  | foot  | ổn |
| Zubat | E046 | 0.8 | 90 / 134 | 1.60 | 143 | 109 |  | hover  | ổn |
| Zweilous | P4LA | 1.4 | 126 / 174 | 1.00 | 126 | 141 |  | (default)  | ổn |
| Zygarde | EL0E | 5.0 | 448 / 308 | 0.45 | 202 | 230 |  | (default)  | ổn |
