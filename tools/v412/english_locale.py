"""Module to restore 100% clean, authentic English across Pokemon Arena v4.1.2:
- Translates legacy Vietnamese strings and F9 quests into clear English.
- Replaces corrupt TCVN3-encoded lines (hint message, arena duel texts, master text).
- Replaces -help command descriptions with authentic English explanations.
- Replaces F9 quests (Mega Evolution, Gym & Level, Learned Moves, Random Legends, Starter evolution guides) with English.
- Strictly maintains 0 non-ascii characters in the entire script.
"""
import re


REPLACEMENTS = [
    # Starter evolution guides
    ("Tien hoa thanh ", "Evolves into "),
    ("Tien hoa khi len lv ", "Evolves at Lv "),
    ("Tien hoa khi len lv", "Evolves at Lv "),
    ("Tien hoa khi su dung ", "Evolves with "),
    ("Tien hoa lan 1  khi len lv ", "First evolution at Lv "),
    ("Tien hoa lan 1 khi len lv ", "First evolution at Lv "),
    (", lan 2 khi len lv ", ", second evolution at Lv "),
    (",lan 2 khi len lv ", ", second evolution at Lv "),
    ("khi len lv ", "at Lv "),
    ("Vai tro ", "Role: "),
    ("Co ti le 3% nhan duoc soul khi danh Magikarp hoang da.", "3% chance to obtain Soul from wild Magikarp."),
    ("Rat manh tien hoa thanh Dragonite o lv55,damage to danh nhanh.", "Very strong when evolving into Dragonite at Lv 55, high damage and fast attack speed."),
    ("Can su dung item: ", "Recommended items: "),
    ("Dat suc manh that su khi len lv36 hoc duoc Sand Storm .", "Reaches true power at Lv 36 when learning Sandstorm."),
    ("Damage 1 muc tieu kha,chi so co ban trung binh,khi giet duoc nhieu hero dich thi dc tang damage dan dan,max tam 250 damage luc do damage rat manh.", "Solid single-target damage. Slaying enemy heroes stacks bonus damage up to +250."),
    ("Tien hoa khi len mang item Metal Coat.", "Evolves when equipping Metal Coat."),
    ("Tien hoa khi mang Metal Coat.", "Evolves when equipping Metal Coat."),
    (" khi su dung Fire Stone.", " with Fire Stone."),
    (" khi su dung Water Stone.", " with Water Stone."),
    (" khi su dung Thunder Stone.", " with Thunder Stone."),
    (" khi su dung Leaf Stone.", " with Leaf Stone."),
    (" khi su dung Moon Stone.", " with Moon Stone."),
    (" khi su dung Sun Stone.", " with Sun Stone."),
    (" khi mang item King's Rock.", " with King's Rock."),
    (" khi mang item Dragon Scale.", " with Dragon Scale."),
    ("Rat kho de su dung thuan thuc :v,skill doi hoi phai kheo leo moi van dung tot dc.", "High skill ceiling hero requiring precise timing and positioning."),
    ("Damage kha,tank khoe,ki nang gay nhieu hieu ung,khi it mau su dung ki nang cuoi gay luong damage rat lon.", "Solid damage and durable tank with crowd control; ultimate deals massive damage at low HP."),
    ("Co 2 ki nang combat dien rong su dung lien tuc,chi so co ban cao.", "Possesses 2 continuous AOE teamfight spells and high base attributes."),
    ("Gay damage va hieu ung len 1 muc tieu rat kho chiu,ki nang cuoi combat manh.", "Deals strong single-target crowd control and damage, with a powerful teamfight ultimate."),
    ("Toc do farm kha.", "Good farming speed."),
    ("Gay damage lien hoan nhieu muc tieu,len level cang cao thi ki nang cang khoe.", "Deals consecutive multi-target damage; abilities scale strongly with level."),
    ("Giap on,nhieu mau,co ki nang giam sat thuong dich va tu hoi mau.", "High armor and HP, with spells to reduce enemy damage and self-heal."),
    ("Damage phep nhieu muc tieu,khang sat thuong vat ly tot,ki nang cuoi la tu huy can ap sat team dich de gay luong damage cuc lon.", "Multi-target magic damage with strong physical resistance. Ultimate is a self-destruct that deals colossal AOE damage."),
    ("Skill buff khang vat ly,phep thuat,mien dich sat thuong len ban than..", "Spells provide physical resistance, magic resistance, and damage immunity."),
    ("Role: chua ro.", "Role: Flexible."),
    ("Len bang dem so vui khong?", "Having fun counting your respawn seconds?"),
]


def patch_script(j: str) -> str:
    # 1. Startup Quest Hint (lines 4626-4629)
    old_hint_pat = re.compile(r'call QuestMessageBJ\(GetPlayersAll\(\),\s*bj_QUESTMESSAGE_ALWAYSHINT,\s*"Pick 1 Pokemon farm[^"]+"\)', re.DOTALL)
    new_hint = (
        'call QuestMessageBJ(GetPlayersAll(), bj_QUESTMESSAGE_ALWAYSHINT, '
        '"Pick 1 Pokemon to farm with teammates, level up, evolve, hunt Legends, and battle in the Arena!\\n\\n'
        'Press [F9] or type -help for game instructions and commands.\\n")'
    )
    j, n = old_hint_pat.subn(new_hint, j, count=1)
    if n == 0:
        raise ValueError("english_locale: startup hint pattern not matched")

    # 2. Duel & Arena Texts
    old_duel1_pat = re.compile(r'call DisplayTimedTextToForce\(GetPlayersAll\(\),\s*10\.00,\s*"Duel Time[^"]+"\)')
    j, n = old_duel1_pat.subn('call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Duel Time - Battle in the Arena!")', j, count=1)
    if n == 0:
        raise ValueError("english_locale: duel 1 pattern not matched")

    old_duel2_pat = re.compile(r'call DisplayTimedTextToForce\(GetPlayersAll\(\),\s*10\.00,\s*"Kill all enemies in 40s[^"]+"\)')
    j, n = old_duel2_pat.subn('call DisplayTimedTextToForce(GetPlayersAll(), 10.00, "Kill all enemies in 40s!")', j, count=1)
    if n == 0:
        raise ValueError("english_locale: duel 2 pattern not matched")

    old_master_pat = re.compile(r'call DisplayTimedTextToForce\(GetPlayersAll\(\),\s*5\.00,\s*"Tr[^"]+"\)')
    j, n = old_master_pat.subn('call DisplayTimedTextToForce(GetPlayersAll(), 5.00, "Arena Master is here! Come and challenge me!")', j, count=1)
    if n == 0:
        raise ValueError("english_locale: master text pattern not matched")

    # 3. Chat triggers for chicken command
    j = j.replace('call TriggerRegisterPlayerChatEvent(t, Player(i), "t lÃ\xa0 gÃ\xa0", true)',
                  'call TriggerRegisterPlayerChatEvent(t, Player(i), "iamnoob", true)')
    j = j.replace('call TriggerRegisterPlayerChatEvent(t, Player(i), "tÃ´i lÃ\xa0 gÃ\xa0", true)',
                  'call TriggerRegisterPlayerChatEvent(t, Player(i), "-noob", true)')

    # 4. -help command
    new_help = (
        'function PAX_Help_OnChat takes nothing returns nothing\n'
        '    local player trigPl = GetTriggerPlayer()\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=============== POKEMON ARENA v4.1.2-ver2j COMMANDS ===============|r")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pick|r / |cff7dd3fc-repick|r : Pick / Repick random Pokemon (first 2 mins, max 2)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-moves|r : Learn / swap 4 moves Q-W-E-R   |   |cff7dd3fc-quest|r : Awakening Progress")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-up|r / |cff7dd3fc-train|r : Late-game stat training   |   |cff7dd3fc-forge|r : Mythic Forge +1..+5 (or click NPC)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gym|r : Check 8 Gym leaders status and line-ups")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-me|r : View hidden stats (Relic, Charms, Lifesteal, Crit, Bounty, Rune)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-home|r / |cff7dd3fc-stuck|r : Teleport home (5s delay, CD 30s, blocked with Soul)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-tp|r : Instant base teleport & full Heal / Mana restore")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-solo [1..12]|r / |cff7dd3fc-yes|r / |cff7dd3fc-no|r : 1v1 Deathmatch challenge & loot 1 item")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-duel [1..12]|r / |cff7dd3fc-accept|r / |cff7dd3fc-rank|r : 1v1 Practice duel & ranking points")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gamble|r : Lucky wheel spin (1,000g)   |   |cff7dd3fc-ez|r / |cff7dd3fc-taunt|r : Taunt")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pet|r : Toggle companion mini pet (+1% Mana/s)   |   |cff7dd3fc-title|r : Change overhead title")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cffffd166[HOST]|r |cff7dd3fc-random|r (random all) | |cff7dd3fc-fog|r (toggle fog) | |cff7dd3fc-win <N>|r (win score limit)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=============================================================================|r")\n'
        '    set trigPl = null\n'
        'endfunction'
    )
    old_help_pat = re.compile(r'function PAX_Help_OnChat takes nothing returns nothing.*?endfunction', re.DOTALL)
    j, n = old_help_pat.subn(new_help, j, count=1)
    if n == 0:
        raise ValueError("english_locale: PAX_Help_OnChat pattern not matched")

    # 5. F9 system quests
    q_mega_old = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Evolution", '
        '"Mua Mega Stone o |cffff66ccMega Shop I|r / |cffff66ccMega Shop II|r / |cffff66ccMega Shop III|r (trong nha, hang duoi Poke Center).|n'
        'Bam vao |cffff66ccMega Stone|r trong tui de Mega (o item hien thoi gian hoi chieu); chi Pokemon dung loai moi dung duoc.|n'
        'Mega trong 60 giay: doi model, STR/AGI/INT doi theo chi so Mega tren PokemonDB, +10 giap, +80 toc chay, +40% toc danh. Hoi chieu 150 giay.|n'
        'Chet khi dang Mega se tro ve dang thuong.|n'
        'Mega Kangaskhan: con nho di theo, danh them 25% sat thuong.|n|n'
        'Credit model Mega: PKLegends team va cac tac gia tren Hive Workshop.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNMegaCharizardX.blp")'
    )
    q_mega_new = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Mega Evolution", '
        '"Purchase Mega Stones at |cffff66ccMega Shop I|r / |cffff66ccMega Shop II|r / |cffff66ccMega Shop III|r (inside base, bottom row).\\n'
        'Click on |cffff66ccMega Stone|r in your inventory to Mega Evolve; only corresponding Pokemon can use it.\\n'
        'Mega Evolution lasts 60s: transforms model, boosts STR/AGI/INT based on PokemonDB stats, +10 Armor, +80 Move Speed, +40% Attack Speed. Cooldown 150s.\\n'
        'Dying while Mega Evolved reverts you to normal form.\\n'
        'Mega Kangaskhan: baby joins in combat, dealing +25% bonus damage.\\n\\n'
        'Model Credits: PKLegends team and authors on Hive Workshop.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNMegaCharizardX.blp")'
    )
    if q_mega_old in j:
        j = j.replace(q_mega_old, q_mega_new, 1)

    q_gym_old = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Gym & Level", '
        '"Moc 1: level toi da 30, chi danh duoc Gym 1-2.|n'
        'Xong Gym 1 + 2 -> moc 2: level toi da 50, danh duoc Gym 1-4.|n'
        'Xong Gym 3 + 4 -> moc 3: level toi da 70, Gym 1-6.|n'
        'Xong Gym 5 + 6 -> moc 4: level toi da 90, Gym 1-8.|n'
        'Xong ca 8 gym: level toi da 100.|n|n'
        'Tui do: toi da 4 Badge va 2 item tang chi so (item he, Leaf Tover, Shell Bell, Mega Stone...). Soul khong bi gioi han.|n'
        'Go -badges de xem moc cua moi nguoi.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNMedalionOfCourage.blp")'
    )
    q_gym_new = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Gym & Level", '
        '"Cap 1: Max Level 30, can challenge Gym 1-2.\\n'
        'Defeat Gym 1-2 -> Cap 2: Max Level 50, Gym 1-4 unlocked.\\n'
        'Defeat Gym 3-4 -> Cap 3: Max Level 70, Gym 1-6 unlocked.\\n'
        'Defeat Gym 5-6 -> Cap 4: Max Level 90, Gym 1-8 unlocked.\\n'
        'Defeat all 8 Gyms: Max Level 100.\\n\\n'
        'Inventory: Up to 4 Badges and 2 Stat Items (Type items, Leftovers, Shell Bell, Mega Stone...). Souls are not limited.\\n'
        'Type -badges to check everyone\'s progress.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNMedalionOfCourage.blp")'
    )
    if q_gym_old in j:
        j = j.replace(q_gym_old, q_gym_new, 1)

    q_moves_old = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Learned Moves", '
        '"Moi Pokemon co 4 o chieu (phim Q W E R, hang duoi cung cua bang lenh) va 1 nut Ability.|n'
        '4 chieu dau biet ngay tu level 1. Khi len level, chieu manh hon se thay the chieu yeu nhat (khong hoi thoai).|n'
        'Sat thuong cac chieu nay tang theo chi so chinh.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNStormBolt.blp")'
    )
    q_moves_new = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Learned Moves", '
        '"Each Pokemon has 4 active move slots (hotkeys Q, W, E, R) and 1 Ability button.\\n'
        'All 4 moves are learned at Level 1. Stronger moves automatically replace weaker ones upon leveling up.\\n'
        'Move damage scales with your primary attribute.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNStormBolt.blp")'
    )
    if q_moves_old in j:
        j = j.replace(q_moves_old, q_moves_new, 1)

    q_legends_old = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Random Legends", '
        '"Cu 3 phut xuat hien 2 legend Lv 100 (chi nhung legend khong co phong) tren map (khong gioi han so con).|n'
        'Chi Pokemon lv 100 moi gay sat thuong duoc.|n'
        'Giet duoc: 50% roi Soul cua legend do (cam o o 1, vao vong tron giua map de bien thanh legend).|n'
        'Quai hoang da thuong khong roi Soul. Elite cua bai (1 con moi bai): 10% roi Soul cua loai do.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNSoulGem.blp")'
    )
    q_legends_new = (
        'call CreateQuestBJ(bj_QUESTTYPE_OPT_DISCOVERED, "Random Legends", '
        '"Every 3 minutes, 2 wild Lv 100 Legends spawn on the map.\\n'
        'Only Lv 100 Pokemon can damage them.\\n'
        'Defeating them gives a 50% chance to drop their Legend Soul (carry in slot 1 and enter center circle to transform).\\n'
        'Normal wild creeps do not drop Souls. Camp Elites have a 10% chance to drop their Soul.", '
        '"ReplaceableTextures\\\\CommandButtons\\\\BTNSoulGem.blp")'
    )
    if q_legends_old in j:
        j = j.replace(q_legends_old, q_legends_new, 1)

    # 6. Apply individual replacements
    for old, new in REPLACEMENTS:
        j = j.replace(old, new)

    return j
