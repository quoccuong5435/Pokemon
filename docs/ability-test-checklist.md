# Bảng thử ability trong game (v4.2x)

Dùng sau khi Gemini build bản có `tools/v412/ability_rw.py`. Chưa ai chơi thử bản này.

## Cách thử

1. Tạo phòng, chọn một Pokemon bất kỳ (bạn phải là host).
2. Chọn hero của mình, gõ `-abtest <tên ability tiếng Anh>`, ví dụ `-abtest Rough Skin`.
   Game báo tên và mô tả ability vừa gán; nút thông tin ability (ô 3,1) cũng đổi theo.
3. Làm theo cột "Cách thử", so với cột "Kết quả cần thấy", đánh dấu cột Đạt.
4. Gõ `-abtest off` để trả lại ability gốc của Pokemon.

Ghi chú:
- Bậc chỉ số (stage) trong map tối đa ±4, nên các hiệu ứng cộng bậc (Moxie, Weak Armor, Motor Drive...) dừng ở ±4.
- Speed Boost dùng tầng riêng (tối đa 6 tầng, mỗi tầng +6% tốc chạy và tốc đánh), không dùng bậc Speed.
- Pressure: hồi chiêu của địch chậm 30% (cơ chế Pressure sẵn có của map chỉ có mức 20% hoặc 30%; bản duyệt ghi 25%).
- Hidden Ability: mua Ability Patch (10.000 vàng) cho Pokemon rồi kiểm tra nút ability đổi sang Hidden Ability.

| Đạt | Ability | Lệnh | Cách thử | Kết quả cần thấy |
|---|---|---|---|---|
| [ ] | Aftermath | `-abtest Aftermath` | Hạ vài con quái (hoặc để bị hạ, với Aftermath). | Bị hạ gục: nổ vùng 400, gây sát thương bằng 1000% chỉ số chính (STR hoặc INT) và choáng 3 giây mọi địch trong vùng. |
| [ ] | Air Lock | `-abtest Air Lock` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 700: địch mất ability; né 20% đòn đánh. Rayquaza: chiêu Dragon / Flying +20%. |
| [ ] | Analytic | `-abtest Analytic` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn thứ hai liên tiếp lên cùng một mục tiêu trong 2 giây: +25% sát thương (đòn đánh và chiêu). |
| [ ] | Anger Point | `-abtest Anger Point` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Máu xuống dưới 50% hoặc bị chí mạng: +60% sát thương, +40% tốc đánh trong 8 giây (hồi 20 giây). |
| [ ] | Anticipation | `-abtest Anticipation` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mọi đòn siêu hiệu quả trúng nó −20%; đòn siêu hiệu quả đầu tiên mỗi 20 giây −50%. |
| [ ] | Bad Dreams | `-abtest Bad Dreams` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 500: địch mất 3% máu tối đa mỗi giây. Darkrai: địch đang ngủ mất 8% mỗi giây; chiêu 30% gây ngủ. |
| [ ] | Battle Armor | `-abtest Battle Armor` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Miễn chí mạng; mỗi đòn đánh trúng nó bị chặn 3 x level sát thương; +5 giáp. |
| [ ] | Big Pecks | `-abtest Big Pecks` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Không bị giảm Defense hay trừ giáp; +5 giáp; đòn đánh +20% lên mục tiêu đang bị trừ giáp. |
| [ ] | Bulletproof | `-abtest Bulletproof` | Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu. | Chặn hẳn 1 chiêu mỗi 10 giây; chặn được thì phản 50% sát thương đó về kẻ ra chiêu. |
| [ ] | Chlorophyll | `-abtest Chlorophyll` | Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so). | +50 tốc chạy, +25% tốc đánh. Nắng: +40% tốc đánh và chiêu Grass +20% sát thương. |
| [ ] | Clear Body | `-abtest Clear Body` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Giải trạng thái xấu mỗi 4 giây; nhận ít hơn 20% sát thương chiêu; không bị giảm chỉ số. |
| [ ] | Cloud Nine | `-abtest Cloud Nine` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 15 giây: chiêu kế tiếp không tốn mana và được hoàn 50% thời gian hồi chiêu. |
| [ ] | Competitive | `-abtest Competitive` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Mỗi hero địch trong 800: +6% sát thương chiêu (tối đa +30%). |
| [ ] | Contrary | `-abtest Contrary` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Mọi thay đổi chỉ số bị đảo ngược (Leaf Storm, Overheat thành tăng Sp. Atk). |
| [ ] | Cud Chew | `-abtest Cud Chew` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 10 giây: hồi 40% lượng máu đã mất trong 10 giây vừa qua. |
| [ ] | Cursed Body | `-abtest Cursed Body` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Trúng chiêu: 30% kẻ đánh bị khóa chiêu 3 giây. |
| [ ] | Damp | `-abtest Damp` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 500: hero địch −20% tốc đánh và nhận ít hơn 30% hồi máu. |
| [ ] | Drizzle | `-abtest Drizzle` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh và chiêu làm mục tiêu Ướt 5 giây: nhận thêm 25% sát thương chiêu Water / Electric và chậm 15% (không gọi thời tiết). |
| [ ] | Drought | `-abtest Drought` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh và chiêu thiêu đốt mục tiêu: mất 1,5% máu tối đa mỗi giây trong 3 giây và nhận ít hơn 30% hồi máu (không gọi thời tiết). |
| [ ] | Dry Skin | `-abtest Dry Skin` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu Water / Ice trúng nó hồi máu bằng 20% sát thương đó thay vì mất máu; mỗi 1% máu đã mất: +0,3% sát thương (tối đa +25%). |
| [ ] | Early Bird | `-abtest Early Bird` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Ra khỏi giao tranh 2 giây: hồi 3% máu mỗi giây; ngủ và choáng ngắn hơn 50%. |
| [ ] | Effect Spore | `-abtest Effect Spore` | Để quái cận chiến (melee) đánh mình vài lần. | Bị đánh cận chiến: 30% kẻ đánh bị độc, tê liệt hoặc ngủ (ngẫu nhiên). |
| [ ] | Flame Body | `-abtest Flame Body` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | 40% đốt kẻ đánh cận chiến; hào quang 250 đốt địch 1% máu tối đa mỗi giây. |
| [ ] | Flash Fire | `-abtest Flash Fire` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Miễn chiêu Fire; luôn +10% sát thương chiêu Fire; trúng chiêu Fire: +40% sát thương 8 giây. |
| [ ] | Friend Guard | `-abtest Friend Guard` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Mỗi 12 giây: khiên bằng 15% máu tối đa của Pokemon này cho chính nó và mọi hero đồng minh trong 600 (4 giây). |
| [ ] | Frisk | `-abtest Frisk` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Đòn đầu tiên lên một hero địch đánh dấu nó 8 giây (hồi 12 giây): lộ vị trí, −10 giáp, đồng minh gây thêm 10% sát thương lên nó. |
| [ ] | Galvanize | `-abtest Galvanize` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu hệ Normal thành hệ Electric và +20% sát thương (giống Aerilate / Pixilate đang có). |
| [ ] | Gluttony | `-abtest Gluttony` | Hạ vài con quái (hoặc để bị hạ, với Aftermath). | Hạ quái hoặc hero: hồi 8% máu và 8% mana. Máu dưới 30%: đòn đánh hút 30% sát thương. |
| [ ] | Guts | `-abtest Guts` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Có trạng thái xấu hoặc máu dưới 40%: +50% sát thương vật lý, +20% tốc đánh, không bị chậm vì trạng thái. |
| [ ] | Harvest | `-abtest Harvest` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Mỗi 12 giây mọc 1 quả (giữ tối đa 2); máu xuống dưới 50% thì tự ăn 1 quả, hồi 15% máu tối đa. |
| [ ] | Healer | `-abtest Healer` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 5 giây: chắc chắn (100%) tự giải trạng thái xấu và hồi 3% máu tối đa. |
| [ ] | Hustle | `-abtest Hustle` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | +30% sát thương đòn đánh thường; 10% đòn đánh thường bị trượt. |
| [ ] | Hydration | `-abtest Hydration` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 6 giây: giải mọi trạng thái xấu và nhận khiên bằng 8% máu tối đa trong 3 giây. |
| [ ] | Hyper Cutter | `-abtest Hyper Cutter` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh trừ 4 giáp trong 6 giây (cộng 5 tầng); mục tiêu đủ 5 tầng nhận thêm 15% sát thương; không bị giảm Attack. |
| [ ] | Ice Body | `-abtest Ice Body` | Để quái cận chiến (melee) đánh mình vài lần. | +15 giáp; kẻ đánh cận chiến bị chậm 30% trong 2 giây; mỗi 15 giây chặn hẳn 1 đòn đánh và đóng băng kẻ đánh 1 giây. |
| [ ] | Imposter | `-abtest Imposter` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Luôn chép Attack / Sp. Atk / Defense / Sp. Def và hệ của mục tiêu đang đánh; đổi mục tiêu thì chép theo mục tiêu mới (cách nhau ít nhất 3 giây). |
| [ ] | Infiltrator | `-abtest Infiltrator` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Chiêu và đòn đánh bỏ qua các bậc tăng Defense / Sp. Def của mục tiêu. |
| [ ] | Inner Focus | `-abtest Inner Focus` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Miễn khựng và Intimidate; nhận ít hơn 15% sát thương chiêu (bỏ né 15%). |
| [ ] | Insomnia | `-abtest Insomnia` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Né 20% đòn đánh; miễn ngủ và rối; hồi 1% máu mỗi giây. |
| [ ] | Intimidate | `-abtest Intimidate` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hero địch trong 500 gây ít hơn 15% sát thương lên nó; mỗi 15 giây gầm: địch trong 600 −1 Attack, −1 Sp. Atk 6 giây và choáng 0,5 giây. |
| [ ] | Justified | `-abtest Justified` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Luôn +15% sát thương lên hệ Dark; trúng chiêu Dark: +1 Attack 12 giây. |
| [ ] | Keen Eye | `-abtest Keen Eye` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | 20% chí mạng x2 cho đòn đánh; đòn đánh bỏ qua 15% giáp; không bị giảm chính xác, không bị né. |
| [ ] | Light Metal | `-abtest Light Metal` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | +60 tốc chạy, +20% tốc đánh, né 10% đòn đánh; không bị đẩy lùi. |
| [ ] | Lightning Rod | `-abtest Lightning Rod` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Miễn chiêu Electric (hồi 25%), trúng chiêu Electric +1 Sp. Atk 12 giây; chiêu Electric +15%; đòn đánh 20% phóng sét lan 3 mục tiêu (50% INT). |
| [ ] | Limber | `-abtest Limber` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Miễn tê liệt, làm chậm và trói; né 20% đòn đánh; +20 tốc chạy. |
| [ ] | Magic Bounce | `-abtest Magic Bounce` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu: 25% chặn hẳn, còn lại phản 40% sát thương; trạng thái và giảm chỉ số bị phản lại. |
| [ ] | Magic Guard | `-abtest Magic Guard` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Chỉ nhận sát thương từ đòn đánh và chiêu trúng trực tiếp (miễn độc, bỏng, hào quang, phản dame, sát thương theo thời gian); chiêu +15% sát thương. |
| [ ] | Magician | `-abtest Magician` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu trúng hero địch: 20% cướp 1 bậc chỉ số đang tăng của mục tiêu (hồi 8 giây). |
| [ ] | Magnet Pull | `-abtest Magnet Pull` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 600: địch chậm 25% (hệ Steel 50%) và −8 giáp; mỗi 10 giây kéo hero địch gần nhất trong 600 lại gần 200. |
| [ ] | Marvel Scale | `-abtest Marvel Scale` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Mỗi lần trúng chiêu nhận 1 vảy (tối đa 5, giữ 6 giây): mỗi vảy +6 giáp và nhận ít hơn 4% sát thương chiêu. |
| [ ] | Minus | `-abtest Minus` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Mỗi chiêu trúng mục tiêu: hồi 3% mana và giảm 1 giây hồi chiêu các chiêu khác. |
| [ ] | Motor Drive | `-abtest Motor Drive` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Miễn chiêu Electric; luôn +15% tốc đánh; trúng chiêu Electric hoặc dùng chiêu: +1 Speed (tối đa +4, 8 giây). |
| [ ] | Moxie | `-abtest Moxie` | Hạ vài con quái (hoặc để bị hạ, với Aftermath). | Hạ gục hero, quái tinh anh hoặc boss: +1 Attack (30 giây, cộng dồn tới +6). |
| [ ] | Natural Cure | `-abtest Natural Cure` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Ra khỏi giao tranh 3 giây: giải trạng thái và hồi 3% máu mỗi giây; trong giao tranh mỗi 8 giây giải 1 trạng thái. |
| [ ] | Oblivious | `-abtest Oblivious` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Chặn 1 khống chế cứng (choáng, ngủ, mê hoặc, đóng băng) mỗi 12 giây; chặn được thì hồi 5% máu tối đa. |
| [ ] | Overcoat | `-abtest Overcoat` | Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so). | Không mất máu vì bão cát / mưa đá; miễn chiêu dạng bột; nhận ít hơn 15% sát thương chiêu đặc biệt. |
| [ ] | Overgrow | `-abtest Overgrow` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Máu dưới 50%: +50% sát thương và hồi 2% máu mỗi giây. |
| [ ] | Own Tempo | `-abtest Own Tempo` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh thứ 3 liên tiếp lên cùng mục tiêu gây thêm 60% sát thương và giảm 1 giây hồi chiêu mọi chiêu; miễn rối. |
| [ ] | Pickpocket | `-abtest Pickpocket` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh trúng hero địch: 25% cướp 1 bậc chỉ số đang tăng của nó và 30 vàng (hồi 6 giây). |
| [ ] | Pixilate | `-abtest Pixilate` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu Normal thành Fairy và +30%; mọi chiêu +10% lên hệ Dragon / Dark. |
| [ ] | Plus | `-abtest Plus` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh tích 1 điện tích (tối đa 5); chiêu kế tiếp dùng hết điện tích, mỗi điện tích +12% sát thương. |
| [ ] | Poison Touch | `-abtest Poison Touch` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh 40% gây độc; mục tiêu đang độc thì chuyển sang Toxic. Chiêu vật lý 25% gây độc. |
| [ ] | Prankster | `-abtest Prankster` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Move trạng thái hồi chiêu nhanh hơn 50%. |
| [ ] | Pressure | `-abtest Pressure` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 700: địch tốn gấp đôi mana, hồi chiêu chậm 25%, tốc đánh −15%. |
| [ ] | Protean | `-abtest Protean` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Sau mỗi chiêu, Pokemon mang hệ của chiêu đó 6 giây: chiêu hệ đó +30%; mỗi lần đổi sang hệ khác: +10% tốc chạy 2 giây. |
| [ ] | Quick Feet | `-abtest Quick Feet` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Mỗi lần bị khống chế hoặc dính trạng thái xấu: +80% tốc chạy 2 giây và hết làm chậm (hồi 8 giây). |
| [ ] | Rain Dish | `-abtest Rain Dish` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Luôn hồi 1% máu mỗi giây; mỗi chiêu Water trúng mục tiêu hồi thêm 5% máu tối đa. |
| [ ] | Rattled | `-abtest Rattled` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Bị trúng đòn khi máu dưới 50%: +40% tốc chạy và +20% tốc đánh trong 4 giây (hồi 10 giây). |
| [ ] | Reckless | `-abtest Reckless` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Chiêu có phản dame +35%; đòn đánh +15%; phản dame bản thân giảm 30%. |
| [ ] | Regenerator | `-abtest Regenerator` | Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu. | Mỗi lần dùng chiêu: hồi 4% máu tối đa; không đánh và không bị đánh 3 giây: hồi 4% mỗi giây. |
| [ ] | Rock Head | `-abtest Rock Head` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Không mất máu vì phản dame của chiêu lẫn sát thương phản lại khi đánh thường (Rough Skin, Rocky Helmet, Static, Iron Barbs...); nhận ít hơn 15% sát thương; chiêu có phản dame +15%. |
| [ ] | Rough Skin | `-abtest Rough Skin` | Để quái cận chiến (melee) đánh mình vài lần. | Kẻ đánh cận chiến mất máu bằng 5% máu tối đa của Pokemon mang Rough Skin. |
| [ ] | Run Away | `-abtest Run Away` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Luôn +30 tốc chạy; bị đánh khi máu dưới 50%: +50% tốc chạy 2 giây và đi xuyên unit (hồi 8 giây). |
| [ ] | Sand Force | `-abtest Sand Force` | Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so). | Thoát chết mỗi 60 giây; chiêu Rock / Ground / Steel +30%; trong bão cát mọi sát thương +15%. |
| [ ] | Sand Rush | `-abtest Sand Rush` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Chạy liên tục 2 giây: đòn đánh kế tiếp +40% sát thương và làm chậm mục tiêu 30% trong 2 giây. |
| [ ] | Sand Stream | `-abtest Sand Stream` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang cát 400: địch mất 1% máu tối đa mỗi giây và trượt 20% đòn đánh (không gọi thời tiết). |
| [ ] | Sand Veil | `-abtest Sand Veil` | Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so). | Né 15% đòn đánh (bão cát 35%), né thì làm chậm kẻ đánh. |
| [ ] | Scrappy | `-abtest Scrappy` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu Normal / Fighting đánh trúng hệ Ghost bình thường và +25% sát thương; miễn Intimidate và mọi giảm Attack. |
| [ ] | Serene Grace | `-abtest Serene Grace` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Hiệu ứng phụ của chiêu x2 tỉ lệ và kéo dài thêm 50%; chiêu +10% sát thương. |
| [ ] | Shadow Tag | `-abtest Shadow Tag` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hào quang 500: địch chậm 35%, tốc đánh −20%; địch dưới 30% máu trong hào quang chậm 50%. |
| [ ] | Sheer Force | `-abtest Sheer Force` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu có hiệu ứng phụ (trạng thái, giảm chỉ số, khựng, rối) mất hiệu ứng đó nhưng +30% sát thương. |
| [ ] | Shell Armor | `-abtest Shell Armor` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Miễn chí mạng; nhận ít hơn 30% sát thương đòn đánh thường; +5 giáp. |
| [ ] | Shield Dust | `-abtest Shield Dust` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 10 giây tự tạo khiên bằng 10% máu tối đa; khi còn khiên thì miễn hiệu ứng phụ của chiêu. |
| [ ] | Slow Start | `-abtest Slow Start` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | 8 giây đầu sau khi ra trận / hồi sinh: −30% sát thương; sau đó +60% sát thương, +25% tốc đánh. Regigigas: +2 Attack. |
| [ ] | Slush Rush | `-abtest Slush Rush` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Đòn đánh làm mục tiêu cóng: −8% tốc chạy mỗi lần (cộng 5 lần); đủ 5 lần thì đóng băng 1 giây. |
| [ ] | Sniper | `-abtest Sniper` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chí mạng gây x2,25 thay vì x1,5. |
| [ ] | Snow Cloak | `-abtest Snow Cloak` | Chờ tới lúc có thời tiết đó (hoặc thử khi trời quang để so). | Né 15% đòn đánh (mưa đá 35%), né thì làm chậm kẻ đánh 40% trong 2 giây; mưa đá: hồi 1% máu mỗi giây. |
| [ ] | Snow Warning | `-abtest Snow Warning` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 8 giây: bão tuyết vùng 400 quanh nó gây sát thương bằng 100% INT và làm chậm 30% trong 2 giây (không gọi thời tiết). |
| [ ] | Speed Boost | `-abtest Speed Boost` | Đứng chờ đủ thời gian hồi ghi trong hiệu ứng, nhìn hiệu ứng / máu. | Mỗi 6 giây trong giao tranh: +1 Speed (tối đa +6); ra khỏi giao tranh vẫn giữ 5 giây. |
| [ ] | Stance Change | `-abtest Stance Change` | Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu. | Ra chiêu gây sát thương: thế Kiếm 5 giây (+35% sát thương, −15% giáp). Không ra chiêu 3 giây: thế Khiên (nhận ít hơn 30% sát thương, chặn hẳn 1 chiêu mỗi 15 giây). |
| [ ] | Static | `-abtest Static` | Để quái cận chiến (melee) đánh mình vài lần. | 20% tê liệt kẻ đánh cận chiến; đòn đánh 10% phóng sét lan. |
| [ ] | Stench | `-abtest Stench` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Đòn đánh và chiêu: 25% khựng 0,7 giây; hào quang 400: địch −15% tốc đánh và gây ít hơn 10% sát thương. |
| [ ] | Storm Drain | `-abtest Storm Drain` | Để địch dùng chiêu lên mình (đấu với quái tinh anh / boss biết ra chiêu, hoặc thử với người khác). | Mỗi chiêu trúng nó: hồi 3% mana và tích 1 tầng (tối đa 5, 8 giây), mỗi tầng +8% sát thương chiêu. |
| [ ] | Sturdy | `-abtest Sturdy` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Đòn chí tử để lại 20% máu và bất tử 2 giây (mỗi 45 giây); máu trên 90%: nhận ít hơn 20% sát thương. |
| [ ] | Suction Cups | `-abtest Suction Cups` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Không bị đẩy hay kéo; choáng ngắn hơn 50%; đứng yên 1 giây: +25 giáp và nhận ít hơn 20% sát thương. |
| [ ] | Surge Surfer | `-abtest Surge Surfer` | Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu. | Mỗi lần dùng chiêu: +40% tốc chạy 2 giây; chiêu Electric giảm 1 giây hồi chiêu các chiêu khác. |
| [ ] | Synchronize | `-abtest Synchronize` | Dùng chiêu liên tục, nhìn thông báo nổi trên đầu và hồi chiêu. | Phản 40% sát thương chiêu và làm chậm kẻ ra chiêu 40% trong 3 giây; trạng thái và giảm chỉ số bị trả lại kẻ gây. |
| [ ] | Technician | `-abtest Technician` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu power ≤ 60: x1,5 sát thương; power ≤ 80: x1,2. |
| [ ] | Telepathy | `-abtest Telepathy` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Né 20% chiêu (move) của địch. |
| [ ] | Thick Fat | `-abtest Thick Fat` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Nhận ít hơn 50% sát thương Fire / Ice; +15% máu tối đa; không bị chậm vì chiêu Ice. |
| [ ] | Tinted Lens | `-abtest Tinted Lens` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Chiêu bị kháng hệ gây sát thương như bình thường (x2 so với hiện tại). |
| [ ] | Unaware | `-abtest Unaware` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Bỏ qua mọi bậc chỉ số của đối thủ khi đánh và khi bị đánh; miễn Intimidate. |
| [ ] | Unburden | `-abtest Unburden` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Máu xuống dưới 50% lần đầu mỗi 30 giây: +60% tốc chạy, +30% tốc đánh trong 5 giây. |
| [ ] | Unnerve | `-abtest Unnerve` | Đứng gần quái hoặc hero địch vài giây, nhìn tốc chạy / tốc đánh / máu của chúng. | Hero địch trong 700 nhận hồi máu ít hơn 30% (mọi nguồn hồi). |
| [ ] | Vital Spirit | `-abtest Vital Spirit` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Miễn ngủ; +15% tốc đánh; máu dưới 50%: +20% tốc chạy. |
| [ ] | Volt Absorb | `-abtest Volt Absorb` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Miễn chiêu Electric (hồi 25%), sau đó +30% tốc đánh 5 giây; +10% sát thương chiêu Electric. |
| [ ] | Water Absorb | `-abtest Water Absorb` | Vào giao tranh với quái và quan sát hiệu ứng ghi bên cạnh. | Miễn chiêu Water (hồi 25%); +10% sát thương chiêu Water; ngoài giao tranh hồi 1% mỗi giây. |
| [ ] | Weak Armor | `-abtest Weak Armor` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Bị đánh thường: −1 Defense, +2 Speed (12 giây, hồi 5 giây). |
| [ ] | Wonder Guard | `-abtest Wonder Guard` | Đánh thường vào quái, nhìn chữ nổi (Crit!, Miss, Flinched...) và sát thương. | Chiêu không siêu hiệu quả −60% và đòn đánh thường −40% lên nó; chiêu siêu hiệu quả +50%. |
| [ ] | Zen Mode | `-abtest Zen Mode` | Để quái đánh tới khi máu qua ngưỡng ghi trong hiệu ứng. | Máu dưới 50% vào Zen: chiêu +50%, +25 giáp, hồi 2% máu mỗi giây; đòn đánh −30%. Trên 50% thì trở lại. |

Ability giữ nguyên (không cần thử lại): Adaptability, Blaze, Compound Eyes, Cute Charm, Defiant, Iron Fist, Leaf Guard, Levitate, Multiscale, Multitype, No Guard, Poison Point, Shed Skin, Solar Power, Soundproof, Steadfast, Super Luck, Swarm, Swift Swim, Torrent, Trace.
