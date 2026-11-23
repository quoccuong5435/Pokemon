"""v4.1.2 Vietnamese localization module for Pokemon Arena.
Localizes in-game announcements, event alerts, item/loot descriptions,
and the -help / -quest / -me / -up / -forge command text into clean, non-accented Vietnamese,
while strictly preserving English Pokemon names, Move names, and original chat commands.
"""
import re



def _rep(s, old, new):
    if old not in s:
        raise ValueError("Missing anchor for Vietnamese localization:\n" + repr(old[:120]))
    return s.replace(old, new, 1)


def patch_script(s):
    # Normalize version banner from ver2 if building from ver2/ver2b
    s = s.replace('v4.1.2-ver2 - PvP & Legend Balance', 'v4.1.2-ver2c - PvP & Legend Balance')
    s = s.replace('POKEMON ARENA v4.1.2-ver2 COMMANDS', 'POKEMON ARENA v4.1.2-ver2c COMMANDS')
    s = s.replace('POKEMON ARENA v4.1.2-ver2|r', 'POKEMON ARENA v4.1.2-ver2c|r')

    # 1. Welcome Banner
    s = _rep(s,
             '    call PAX_Announce("  |cffffd166POKEMON ARENA v4.1.2-ver2c|r  |cff94a3b8- PvP & Legend Balance|r", 10.0)\n'
             '    call PAX_Announce("  |cff7dd3fc-help|r |cffe8ecf2All Commands  |  |cff7dd3fc-up|r |cffe8ecf2Train  |  |cff7dd3fc-quest|r |cffe8ecf2Awakening  |  |cff7dd3fc-solo|r |cffe8ecf21v1 Loot  |  |cff7dd3fc-pet|r |cffe8ecf2Mini Pet|r", 10.0)\n'
             '    call PAX_Announce("  |cffe8ecf2Base Shops:|r |cffffd166Form Shop|r |cff64748b/|r |cffd896ffParadox Form Shop|r", 10.0)',
             '    call PAX_Announce("  |cffffd166POKEMON ARENA v4.1.2-ver2c|r  |cff94a3b8- PvP & Can Bang Huyen Thoai|r", 10.0)\n'
             '    call PAX_Announce("  |cff7dd3fc-help|r |cffe8ecf2Tat Ca Lenh  |  |cff7dd3fc-up|r |cffe8ecf2Luyen Tap  |  |cff7dd3fc-quest|r |cffe8ecf2Thuc Tinh  |  |cff7dd3fc-solo|r |cffe8ecf21v1 Cuop Do  |  |cff7dd3fc-pet|r |cffe8ecf2Thu Cung|r", 10.0)\n'
             '    call PAX_Announce("  |cffe8ecf2Cua Hang Can Cu:|r |cffffd166Form Shop|r |cff64748b/|r |cffd896ffParadox Form Shop|r", 10.0)')

    # 2. Comprehensive -help command display
    old_help = (
        'function PAX_Help_OnChat takes nothing returns nothing\n'
        '    local player trigPl = GetTriggerPlayer()\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "|cffffd166=============== POKEMON ARENA v4.1.2-ver2c COMMANDS ===============|r")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-pick|r / |cff7dd3fc-repick|r : Chon / doi lai Pokemon (2 phut dau, 2 lan)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-moves|r : Hoc / doi 4 chieu Q-W-E-R   |   |cff7dd3fc-quest|r : Tien do Thuc tinh Than")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-up|r / |cff7dd3fc-train|r : Tieu vang late game   |   |cff7dd3fc-forge|r : Dap do +1..+5 [MYTHIC] (hoac click Tuong o nha)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-me|r : Xem chi so an (Relic, Charm, Lifesteal, Crit, Bounty, Rune)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-home|r / |cff7dd3fc-stuck|r : Ve nha / giai ket (CD 30s, chan khi cam Legend Soul)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-solo [1..12]|r / |cff7dd3fc-yes|r / |cff7dd3fc-no|r : Ga solo den chet cuop 1 mon do")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-duel|r / |cff7dd3fc-accept|r / |cff7dd3fc-rank|r : Dau giao huu 1v1   |   |cff7dd3fc-league|r : Dau Champion")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-ez|r / |cff7dd3fc-taunt|r : Gay ca khia   |   |cff7dd3fc-gamble|r : Quay nhan pham (1000g)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cff7dd3fc-pet|r : Doi / tat thu cung mini (+1% Mana/s)   |   |cff7dd3fc-title|r : Doi danh hieu bay")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "  |cffffd166[HOST]|r |cff7dd3fc-random|r (random all) | |cff7dd3fc-fog|r (bat/tat suong) | |cff7dd3fc-win <N>|r (doi diem thang)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 14.0, "|cffffd166=============================================================|r")\n'
        '    set trigPl = null\n'
        'endfunction'
    )
    new_help = (
        'function PAX_Help_OnChat takes nothing returns nothing\n'
        '    local player trigPl = GetTriggerPlayer()\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=================== BANG HUONG DAN LENH POKEMON ARENA ===================|r")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pick|r / |cff7dd3fc-repick|r : Chon / doi Pokemon ngau nhien (2 phut dau, toi da 2 lan)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-moves|r : Menu hoc / doi 4 chieu Q-W-E-R   |   |cff7dd3fc-quest|r : Tien do Thuc Tinh Than")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-up|r / |cff7dd3fc-train|r : Luyen tap chi so cuoi game (All Stats, Mau, Giap, Duoc Pham)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-forge|r : Tiem Ren dap do +1..+5 [MYTHIC] / Dung hop do (hoac bam vao Tuong)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gym|r : Xem trang thai & doi hinh 8 Gym   |   |cff7dd3fc-league|r : Khieu chien Champion Lance")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-me|r : Xem chi tiet chi so an (Relic, Bua Charm, Hut mau, Chi mang, Tien thuong, Co ngu)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-home|r / |cff7dd3fc-stuck|r : Bien ve can cu sau 5s (CD 30s, chan khi dang mang Legend Soul)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-tp|r : Dich chuyen tuc thoi ve can cu va hoi day Mau / Mana")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-solo [1..12]|r / |cff7dd3fc-yes|r / |cff7dd3fc-no|r : Thach dau Sinh Tu 1v1 cuop 1 mon trang bi")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-duel [1..12]|r / |cff7dd3fc-accept|r / |cff7dd3fc-rank|r : Dau giao huu 1v1 tinh diem xep hang")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-gamble|r : Vong quay may man (1.000 vang/luot)   |   |cff7dd3fc-ez|r / |cff7dd3fc-taunt|r : Khieu khich")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cff7dd3fc-pet|r : Doi / bat tat Thu Cung mini (+1% Mana/s)   |   |cff7dd3fc-title|r : Doi danh hieu bay tren dau")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "  |cffffd166[HOST]|r |cff7dd3fc-random|r (random all) | |cff7dd3fc-fog|r (bat/tat suong) | |cff7dd3fc-win <N>|r (dat diem thang)")\n'
        '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 15.0, "|cffffd166=============================================================================|r")\n'
        '    set trigPl = null\n'
        'endfunction'
    )
    s = _rep(s, old_help, new_help)

    # 3. -me Stats display
    s = _rep(s,
             '    local string runeStr = "None"\n'
             '    if uHero == null then\n'
             '        call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cff7dd3fc[STATS]|r |cffe8ecf2Pick a Pokemon first.|r")\n',
             '    local string runeStr = "Khong co"\n'
             '    if uHero == null then\n'
             '        call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cff7dd3fc[CHI SO]|r |cffe8ecf2Hay chon mot Pokemon truoc.|r")\n')

    s = _rep(s,
             '    if LoadInteger(PAX_Item_HT, h, 130) > 15000 then  // v4.1.4\n'
             '        set hpNote = " (of " + I2S(LoadInteger(PAX_Item_HT, h, 130)) + ": the first 15,000 in full, the rest half)"\n'
             '    endif\n'
             '    set lsPct = LoadInteger(PAX_Item_HT, h, 111)\n'
             '    set critPct = LoadInteger(PAX_Item_HT, h, 114)\n'
             '    set thornsPct = LoadInteger(PAX_Item_HT, h, 116)\n'
             '    if Mega_Time < LoadReal(PAX_Leg_HT, h, 170) then\n'
             '        set runeStr = "|cff38bdf8Haste (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 170) - Mega_Time)) + "s)|r"\n'
             '    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 171) then\n'
             '        set runeStr = "|cffff5c5cFury (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 171) - Mega_Time)) + "s)|r"\n'
             '    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 172) then\n'
             '        set runeStr = "|cff4ade80Regen (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 172) - Mega_Time)) + "s)|r"\n'
             '    endif\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "|cff7dd3fc====== " + GetUnitName(uHero) + " (Lv " + I2S(GetHeroLevel(uHero)) + ") ======|r")\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2K/D:|r |cffff5c5c" + I2S(F9[pid + 1]) + "|r/|cff6699ff" + I2S(G9[pid + 1]) + "|r  |  |cffe8ecf2Streak:|r |cffffd166" + I2S(PAX_KillStreak[pid]) + "|r  |  |cffe8ecf2Bounty:|r |cffffd166" + I2S(bounty) + "g|r  |  |cffe8ecf2Gym:|r |cffffd166" + I2S(PAX_MB_BadgeCount(pid)) + "/8|r")\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Loot Stats:|r +" + I2S(rStr) + " STR, +" + I2S(rAgi) + " AGI, +" + I2S(rInt) + " INT, +" + I2S(rArm) + " Armor, +" + I2S(rHp) + " HP" + hpNote)\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Charms:|r Lifesteal " + I2S(lsPct) + "% (max 25%)  |  Crit " + I2S(critPct) + "% (max 60%)  |  Thorns " + I2S(thornsPct) + "%  |  |cffe8ecf2Rune:|r " + runeStr)',
             '    if LoadInteger(PAX_Item_HT, h, 130) > 15000 then  // v4.1.4\n'
             '        set hpNote = " (tren tong " + I2S(LoadInteger(PAX_Item_HT, h, 130)) + ": 15.000 dau nhan du, phan du nhan 50%)"\n'
             '    endif\n'
             '    set lsPct = LoadInteger(PAX_Item_HT, h, 111)\n'
             '    set critPct = LoadInteger(PAX_Item_HT, h, 114)\n'
             '    set thornsPct = LoadInteger(PAX_Item_HT, h, 116)\n'
             '    if Mega_Time < LoadReal(PAX_Leg_HT, h, 170) then\n'
             '        set runeStr = "|cff38bdf8Toc Do (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 170) - Mega_Time)) + "s)|r"\n'
             '    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 171) then\n'
             '        set runeStr = "|cffff5c5cCuong No (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 171) - Mega_Time)) + "s)|r"\n'
             '    elseif Mega_Time < LoadReal(PAX_Leg_HT, h, 172) then\n'
             '        set runeStr = "|cff4ade80Hoi Phuc (" + I2S(R2I(LoadReal(PAX_Leg_HT, h, 172) - Mega_Time)) + "s)|r"\n'
             '    endif\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "|cff7dd3fc====== " + GetUnitName(uHero) + " (Cap " + I2S(GetHeroLevel(uHero)) + ") ======|r")\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Ha/Chet:|r |cffff5c5c" + I2S(F9[pid + 1]) + "|r/|cff6699ff" + I2S(G9[pid + 1]) + "|r  |  |cffe8ecf2Chuoi ha:|r |cffffd166" + I2S(PAX_KillStreak[pid]) + "|r  |  |cffe8ecf2Tien thuong mang:|r |cffffd166" + I2S(bounty) + " vang|r  |  |cffe8ecf2Huy hieu Gym:|r |cffffd166" + I2S(PAX_MB_BadgeCount(pid)) + "/8|r")\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Chi so Loot:|r +" + I2S(rStr) + " STR, +" + I2S(rAgi) + " AGI, +" + I2S(rInt) + " INT, +" + I2S(rArm) + " Giap, +" + I2S(rHp) + " Mau" + hpNote)\n'
             '    call DisplayTimedTextToPlayer(trigPl, 0, 0, 10.0, "  |cffe8ecf2Bua Charm:|r Hut mau " + I2S(lsPct) + "% (toi da 25%)  |  Chi mang " + I2S(critPct) + "% (toi da 60%)  |  Phan don " + I2S(thornsPct) + "%  |  |cffe8ecf2Co ngu:|r " + runeStr)')

    # 4. -up / -train (Luyen tap cuoi game)
    s = _rep(s,
             '    if PAX_Up_StatLv[pid] >= 15 then\n'
             '        set statLabel = "All Stats +10 (MAX 15/15)"\n'
             '    else\n'
             '        set statLabel = "All Stats +10 (" + I2S(PAX_Up_StatLv[pid]) + "/15) - " + I2S(statCost) + "g"\n'
             '    endif\n'
             '    if PAX_Up_VitLv[pid] >= 10 then\n'
             '        set vitLabel = "+500 HP & +3 Armor (MAX 10/10)"\n'
             '    else\n'
             '        set vitLabel = "+500 HP & +3 Armor (" + I2S(PAX_Up_VitLv[pid]) + "/10) - " + I2S(vitCost) + "g"\n'
             '    endif\n'
             '    if Mega_Time < PAX_Up_ElixirEnd[pid] then\n'
             '        set elixLabel = "Battle Elixir (Active " + I2S(R2I(PAX_Up_ElixirEnd[pid] - Mega_Time)) + "s) - 3000g"\n'
             '    else\n'
             '        set elixLabel = "Battle Elixir (+15% Dmg/-10% Taken/+15% MS, 3m) - 3000g"\n'
             '    endif\n'
             '    call DialogClear(PAX_Up_Dlg[pid])\n'
             '    call DialogSetMessage(PAX_Up_Dlg[pid], "Late-Game Training & Gold Shop (-up)")\n'
             '    set PAX_Up_Btn[baseIdx + 0] = DialogAddButton(PAX_Up_Dlg[pid], statLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 1] = DialogAddButton(PAX_Up_Dlg[pid], vitLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 2] = DialogAddButton(PAX_Up_Dlg[pid], "Mystery Loot Box (Rare/Epic/Leg) - 3500g", 0)\n'
             '    set PAX_Up_Btn[baseIdx + 3] = DialogAddButton(PAX_Up_Dlg[pid], elixLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 4] = DialogAddButton(PAX_Up_Dlg[pid], "Close", 0)',
             '    if PAX_Up_StatLv[pid] >= 15 then\n'
             '        set statLabel = "Tang All Stats +10 (Toi da 15/15)"\n'
             '    else\n'
             '        set statLabel = "Tang All Stats +10 (" + I2S(PAX_Up_StatLv[pid]) + "/15) - " + I2S(statCost) + " vang"\n'
             '    endif\n'
             '    if PAX_Up_VitLv[pid] >= 10 then\n'
             '        set vitLabel = "+500 Mau & +3 Giap (Toi da 10/10)"\n'
             '    else\n'
             '        set vitLabel = "+500 Mau & +3 Giap (" + I2S(PAX_Up_VitLv[pid]) + "/10) - " + I2S(vitCost) + " vang"\n'
             '    endif\n'
             '    if Mega_Time < PAX_Up_ElixirEnd[pid] then\n'
             '        set elixLabel = "Duoc Pham Chien Dau (Con " + I2S(R2I(PAX_Up_ElixirEnd[pid] - Mega_Time)) + "s) - 3000 vang"\n'
             '    else\n'
             '        set elixLabel = "Duoc Pham (+15% Dmg/-10% Nhan/+15% MS, 3p) - 3000 vang"\n'
             '    endif\n'
             '    call DialogClear(PAX_Up_Dlg[pid])\n'
             '    call DialogSetMessage(PAX_Up_Dlg[pid], "Luyen Tap Cuoi Game & Tiem Vang (-up)")\n'
             '    set PAX_Up_Btn[baseIdx + 0] = DialogAddButton(PAX_Up_Dlg[pid], statLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 1] = DialogAddButton(PAX_Up_Dlg[pid], vitLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 2] = DialogAddButton(PAX_Up_Dlg[pid], "Hom Do Bi An (Hiem/Su Thi/Huyen Thoai) - 3500 vang", 0)\n'
             '    set PAX_Up_Btn[baseIdx + 3] = DialogAddButton(PAX_Up_Dlg[pid], elixLabel, 0)\n'
             '    set PAX_Up_Btn[baseIdx + 4] = DialogAddButton(PAX_Up_Dlg[pid], "Dong", 0)')

    s = _rep(s, '|cffff5c5c[TRAIN]|r You need a living Pokemon.', '|cffff5c5c[LUYEN TAP]|r Can mot Pokemon con song.')
    s = _rep(s, '|cffffd166[TRAIN]|r All Stats upgrade is already MAX (15/15).', '|cffffd166[LUYEN TAP]|r Nang cap All Stats da dat TOI DA (15/15).')
    s = _rep(s, '|cffff5c5c[TRAIN]|r Need " + I2S(cost) + "g.', '|cffff5c5c[LUYEN TAP]|r Can " + I2S(cost) + " vang.')
    s = _rep(s, '|cff4ade80[TRAIN]|r Upgraded All Stats +10 (', '|cff4ade80[LUYEN TAP]|r Da nang cap All Stats +10 (')
    s = _rep(s, '|cffffd166[TRAIN]|r HP & Armor upgrade is already MAX (10/10).', '|cffffd166[LUYEN TAP]|r Nang cap Mau & Giap da dat TOI DA (10/10).')
    s = _rep(s, '|cff4ade80[TRAIN]|r Upgraded +500 Max HP & +3 Armor (', '|cff4ade80[LUYEN TAP]|r Da nang cap +500 Mau Toi Da & +3 Giap (')
    s = _rep(s, '|cffff5c5c[TRAIN]|r Need 3500g for Mystery Loot Box.', '|cffff5c5c[LUYEN TAP]|r Can 3.500 vang de mo Hom Do Bi An.')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[LOOT BOX]|r Opened a " + PAX_Loot_TierColor(tier) + PAX_Loot_TierName(tier) + "|r Loot at your feet!")',
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cffd896ff[HOM DO BI AN]|r Da mo ra " + PAX_Loot_TierColor(tier) + "Do Loot " + PAX_Loot_TierName(tier) + "|r duoi chan!")')
    s = _rep(s, '|cffff5c5c[TRAIN]|r Need 3000g for Battle Elixir.', '|cffff5c5c[LUYEN TAP]|r Can 3.000 vang de mua Duoc Pham Chien Dau.')
    s = _rep(s,
             '|cffffd166[ELIXIR]|r Active for 3 minutes (+15% Dmg, -10% Taken, +15% MS; lost on death)!',
             '|cffffd166[DUOC PHAM]|r Co hieu luc trong 3 phut (+15% Sat thuong, -10% Sat thuong nhan, +15% Toc chay; mat khi chet)!')

    # 5. -forge (Tiem Ren Than Bi)
    s = _rep(s,
             '    call DialogClear(PAX_Forge_Dlg[pid])\n'
             '    call DialogSetMessage(PAX_Forge_Dlg[pid], "MYTHIC FORGE - Upgrade & Fuse Loot")\n'
             '    loop\n'
             '        exitwhen slot >= 6\n'
             '        set curIt = UnitItemInSlot(uHero, slot)\n'
             '        if curIt != null and PAX_IsLootItemId(GetItemTypeId(curIt)) then\n'
             '            set h = GetHandleId(curIt)\n'
             '            if LoadInteger(PAX_Item_HT, h, 0) > 0 then\n'
             '                set lv = LoadInteger(PAX_Item_HT, h, 20)\n'
             '                if lv >= 5 then\n'
             '                    set label = "Slot " + I2S(slot + 1) + ": " + GetItemName(curIt) + " (MAX)"\n'
             '                else\n'
             '                    set cost = PAX_Forge_Cost(lv)\n'
             '                    set rate = PAX_Forge_Rate(lv)\n'
             '                    set label = "Slot " + I2S(slot + 1) + ": " + GetItemName(curIt) + " -> +" + I2S(lv + 1) + " (" + I2S(rate) + "%, " + I2S(cost) + "g)"\n'
             '                endif\n'
             '                set PAX_Forge_Btn[baseIdx + btnIdx] = DialogAddButton(PAX_Forge_Dlg[pid], label, 0)\n'
             '                set PAX_Forge_SlotMap[baseIdx + btnIdx] = slot\n'
             '                set btnIdx = btnIdx + 1\n'
             '            endif\n'
             '        endif\n'
             '        set slot = slot + 1\n'
             '    endloop\n'
             '    set PAX_Forge_Btn[baseIdx + 6] = DialogAddButton(PAX_Forge_Dlg[pid], "Fuse 2 Lowest Loot -> Next Tier (60/40/20%, 1500g)", 0)\n'
             '    set PAX_Forge_Btn[baseIdx + 7] = DialogAddButton(PAX_Forge_Dlg[pid], "Close", 0)',
             '    call DialogClear(PAX_Forge_Dlg[pid])\n'
             '    call DialogSetMessage(PAX_Forge_Dlg[pid], "TIEM REN THAN BI - Nang cap & Dung hop Do Loot")\n'
             '    loop\n'
             '        exitwhen slot >= 6\n'
             '        set curIt = UnitItemInSlot(uHero, slot)\n'
             '        if curIt != null and PAX_IsLootItemId(GetItemTypeId(curIt)) then\n'
             '            set h = GetHandleId(curIt)\n'
             '            if LoadInteger(PAX_Item_HT, h, 0) > 0 then\n'
             '                set lv = LoadInteger(PAX_Item_HT, h, 20)\n'
             '                if lv >= 5 then\n'
             '                    set label = "O " + I2S(slot + 1) + ": " + GetItemName(curIt) + " (TOI DA)"\n'
             '                else\n'
             '                    set cost = PAX_Forge_Cost(lv)\n'
             '                    set rate = PAX_Forge_Rate(lv)\n'
             '                    set label = "O " + I2S(slot + 1) + ": " + GetItemName(curIt) + " -> +" + I2S(lv + 1) + " (" + I2S(rate) + "%, " + I2S(cost) + " vang)"\n'
             '                endif\n'
             '                set PAX_Forge_Btn[baseIdx + btnIdx] = DialogAddButton(PAX_Forge_Dlg[pid], label, 0)\n'
             '                set PAX_Forge_SlotMap[baseIdx + btnIdx] = slot\n'
             '                set btnIdx = btnIdx + 1\n'
             '            endif\n'
             '        endif\n'
             '        set slot = slot + 1\n'
             '    endloop\n'
             '    set PAX_Forge_Btn[baseIdx + 6] = DialogAddButton(PAX_Forge_Dlg[pid], "Dung hop 2 do thap nhat -> Bac ke (60/40/20%, 1500 vang)", 0)\n'
             '    set PAX_Forge_Btn[baseIdx + 7] = DialogAddButton(PAX_Forge_Dlg[pid], "Dong", 0)')

    s = _rep(s, '|cffff5c5c[MYTHIC FORGE]|r You need a living Pokemon.', '|cffff5c5c[TIEM REN]|r Can mot Pokemon con song.')
    s = _rep(s, '|cffff5c5c[FORGE]|r Need 1,500g to Fuse.', '|cffff5c5c[TIEM REN]|r Can 1.500 vang de Dung hop.')
    s = _rep(s, '|cffff5c5c[FORGE]|r Need at least 2 Common/Rare/Epic Loot items in inventory to Fuse!',
             '|cffff5c5c[TIEM REN]|r Can it nhat 2 trang bi Loot Thuong/Hiem/Su Thi trong tui do de dung hop!')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 7.0, "|cff4ade80[FORGE]|r Fusion succeeded! Created a " + PAX_Loot_TierColor(nextTier) + PAX_Loot_TierName(nextTier) + "|r Loot!")',
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 7.0, "|cff4ade80[TIEM REN]|r Dung hop thanh cong! Tao ra trang bi " + PAX_Loot_TierColor(nextTier) + "Do Loot " + PAX_Loot_TierName(nextTier) + "|r!")')
    s = _rep(s, '|cffff5c5c[FORGE]|r Fusion failed! 1 fodder item shattered into dust.',
             '|cffff5c5c[TIEM REN]|r Dung hop that bai! 1 trang bi phoi da vo vun thanh tro bui.')
    s = _rep(s, '|cffffd166[FORGE]|r This item is already [MYTHIC +5]!', '|cffffd166[TIEM REN]|r Trang bi nay da dat toi da [MYTHIC +5]!')
    s = _rep(s, '|cffff5c5c[FORGE]|r Need " + I2S(cost) + "g to upgrade.', '|cffff5c5c[TIEM REN]|r Can " + I2S(cost) + " vang de nang cap.')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cff4ade80[FORGE]|r Success! Upgraded to |cffffd166" + GetItemName(targetIt) + "|r!")',
             'call DisplayTimedTextToPlayer(trigPl, 0, 0, 6.0, "|cff4ade80[TIEM REN]|r Nang cap thanh cong! Dat moc |cffffd166" + GetItemName(targetIt) + "|r!")')
    s = _rep(s, '|cffff5c5c[FORGE]|r Upgrade failed! Item dropped back to +" + I2S(lv) + ".',
             '|cffff5c5c[TIEM REN]|r Nang cap that bai! Trang bi bi tut cap xuong +" + I2S(lv) + ".')
    s = _rep(s, '|cffff5c5c[FORGE]|r Upgrade to +1 failed (item safe).',
             '|cffff5c5c[TIEM REN]|r Nang cap len +1 that bai (trang bi an toan, khong tut cap).')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff3366", "[MYTHIC +5 FORGED!]", "|cff7dd3fc" + GetPlayerName(trigPl) + "|r successfully forged |cffff3366" + GetItemName(targetIt) + "|r (+120% Stats/Effects)!", 10.0)',
             'call PAX_MajorEvent("|cffff3366", "[REN THAN THOAI +5!]", "|cff7dd3fc" + GetPlayerName(trigPl) + "|r da ren thanh cong |cffff3366" + GetItemName(targetIt) + "|r (+120% Chi so/Hieu ung)!", 10.0)')

    # 6. -solo, -yes, -no (Thach dau Sinh Tu)
    s = _rep(s,
             'call PAX_Announce("|cff94a3b8[SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r declined the Deathmatch Solo! (So qua chay mat dep! =)))", 7.0)',
             'call PAX_Announce("|cff94a3b8[SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r da tu choi Solo! (So qua chay mat dep! =)))", 7.0)')
    s = _rep(s, '|cffff5c5c[SOLO]|r A Deathmatch Solo is already pending or in progress.',
             '|cffff5c5c[SOLO]|r Dang co mot keo Solo dien ra hoac dang cho tra loi.')
    s = _rep(s, '|cffff5c5c[SOLO]|r You need a living Pokemon to challenge.',
             '|cffff5c5c[SOLO]|r Can mot Pokemon con song de thach dau.')
    s = _rep(s, '|cffffd166[SOLO]|r Usage: -solo <enemy player 1..12> (or just -solo to pick first enemy).',
             '|cffffd166[SOLO]|r Cach dung: -solo <so thu tu doi thu 1..12> (hoac go -solo de tu chon doi thu dau tien).')
    s = _rep(s, '|cffff5c5c[SOLO]|r Target enemy does not have a living Pokemon.',
             '|cffff5c5c[SOLO]|r Doi thu khong co Pokemon con song.')
    s = _rep(s,
             'call PAX_Announce("|cffff5c5c[SOLO CHALLENGE]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r challenged |cff7dd3fc" + GetPlayerName(Player(targetPid)) + "|r to a |cffffd1661v1 DEATHMATCH|r (loser drops 1 item)! Type |cff4ade80-yes|r or |cffff5c5c-no|r within 20s!", 10.0)',
             'call PAX_Announce("|cffff5c5c[THACH DAU SOLO]|r |cff7dd3fc" + GetPlayerName(trigPl) + "|r da thach dau |cff7dd3fc" + GetPlayerName(Player(targetPid)) + "|r SOLO SINH TU 1v1 (thua roi 1 do)! Go |cff4ade80-yes|r hoac |cffff5c5c-no|r trong 20s!", 10.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[DEATHMATCH SOLO!]", "|cff7dd3fc" + GetPlayerName(Player(pidA)) + "|r vs |cff7dd3fc" + GetPlayerName(Player(pidB)) + "|r TO THE DEATH at Center! Loser drops 1 random item!", 10.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[SOLO SINH TU!]", "|cff7dd3fc" + GetPlayerName(Player(pidA)) + "|r vs |cff7dd3fc" + GetPlayerName(Player(pidB)) + "|r DAU DEN CHET tai Trung Tam! Ke thua roi 1 do ngau nhien!", 10.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[SOLO VICTORY!]", "|cff7dd3fc" + GetPlayerName(Player(winPid)) + "|r crushed |cff7dd3fc" + GetPlayerName(Player(losePid)) + "|r and looted |cffffd166" + lootTxt + "|r!", 10.0)',
             'call PAX_MajorEvent("|cffffd166", "[SOLO CHIEN THANG!]", "|cff7dd3fc" + GetPlayerName(Player(winPid)) + "|r da de bep |cff7dd3fc" + GetPlayerName(Player(losePid)) + "|r va cuop duoc |cffffd166" + lootTxt + "|r!", 10.0)')
    s = _rep(s, 'call PAX_Announce("|cffff5c5c[SOLO]|r Solo cancelled: both players must have living Pokemon.", 6.0)',
             'call PAX_Announce("|cffff5c5c[SOLO]|r Huy Solo: ca hai nguoi choi phai co Pokemon con song.", 6.0)')
    s = _rep(s, 'call PAX_Announce("|cff94a3b8[SOLO]|r Deathmatch Solo invite expired.", 5.0)',
             'call PAX_Announce("|cff94a3b8[SOLO]|r Loi moi Solo Sinh Tu da het han.", 5.0)')
    s = _rep(s, 'call PAX_Announce("|cff94a3b8[SOLO]|r Deathmatch Solo ended in a draw (90s timeout).", 6.0)',
             'call PAX_Announce("|cff94a3b8[SOLO]|r Tran Solo Sinh Tu ket thuc hoa (het 90s).", 6.0)')

    # 7. Chaos Mode
    s = _rep(s,
             'call PAX_MajorEvent("|cff38bdf8", "[CHAOS MODE: TURBO SPEED!]", "All Pokemon run at MAX SPEED (522) for |cffffd16630 seconds|r!", 9.0)',
             'call PAX_MajorEvent("|cff38bdf8", "[HON LOAN: TOC DO TOI DA!]", "Tat ca Pokemon di chuyen TOC DO TOI DA (522) trong |cffffd16630 giay|r!", 9.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffd896ff", "[CHAOS MODE: KAIJU BRAWL!]", "All Pokemon grew |cffffd166x1.8 GIANT SIZE|r for |cffffd16630 seconds|r!", 9.0)',
             'call PAX_MajorEvent("|cffd896ff", "[HON LOAN: KHONG LO HOA!]", "Tat ca Pokemon hoa |cffffd166KHONG LO x1.8 LAN|r trong |cffffd16630 giay|r!", 9.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[CHAOS MODE: GOLD FEVER!]", "Every PvP Hero kill awards |cffffd166+1,000g BONUS GOLD|r for |cffffd16630 seconds|r!", 9.0)',
             'call PAX_MajorEvent("|cffffd166", "[HON LOAN: CON SOT VANG!]", "Moi mang ha guc tuong PvP nhan them |cffffd166+1.000 VANG THUONG|r trong |cffffd16630 giay|r!", 9.0)')
    s = _rep(s,
             'call PAX_Announce("|cff94a3b8[CHAOS MODE]|r |cffe8ecf2Chaos Mode ended! Back to normal.|r", 6.0)',
             'call PAX_Announce("|cff94a3b8[CHE DO HON LOAN]|r |cffe8ecf2Che do Hon Loan ket thuc! Dau truong tro lai binh thuong.|r", 6.0)')

    # 8. Events: Altar, Wanted, Golden Treasure, Magikarp, Red Gyarados, Runes
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[ALTAR EVENT #" + I2S(PAX_Altar_Wave) + "]", "Center Altar is |cffffd166ACTIVE|r! Hold |cff4ade8020s|r for |cffffd166Team Gold + 2 Bonus Loot|r!", 11.0)',
             'call PAX_MajorEvent("|cffffd166", "[SU KIEN ALTAR #" + I2S(PAX_Altar_Wave) + "]", "Ban tho Trung Tam da |cffffd166KICH HOAT|r! Giu |cff4ade8020s|r de nhan |cffffd166Vang Toan Doi + 2 Do Loot|r!", 11.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[ALTAR CAPTURED]", teamName + " captured the Center Altar! (|cffffd166+" + I2S(rewardGold) + "g|r each, |cffd896ff2 Bonus Loot|r)", 11.0)',
             'call PAX_MajorEvent("|cffffd166", "[CHIEM DUOC ALTAR!]", teamName + " da chiem Ban tho Trung Tam! (|cffffd166+" + I2S(rewardGold) + " vang|r moi nguoi, |cffd896ff2 Do Loot Thuong|r)", 11.0)')
    s = _rep(s,
             'call PAX_Announce("|cffffd166[ALTAR EVENT]|r |cffe8ecf2Center Altar activates in|r |cffff5c5c60 seconds|r! |cffe8ecf2Prepare to contest!|r", 8.0)',
             'call PAX_Announce("|cffffd166[SU KIEN ALTAR]|r |cffe8ecf2Ban tho Thuc Tinh o giua ban do mo sau|r |cffff5c5c60 giay|r! |cffe8ecf2Chuan bi tranh doat!|r", 8.0)')
    s = _rep(s,
             'call PAX_Announce("|cffaaaaaa[ALTAR EVENT]|r Center Awakening Altar expired unclaimed. Next event in 7 minutes.", 7.0)',
             'call PAX_Announce("|cffaaaaaa[SU KIEN ALTAR]|r Khong ai chiem duoc Ban tho Trung Tam. Su kien tiep theo sau 7 phut.", 7.0)')

    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[WANTED!]", "|cff7dd3fc" + GetPlayerName(Player(bestPid)) + "|r is WANTED for |cffffd16690s|r! Hunt for |cffffd166+1,200g|r - or survive for |cffffd166+1,000g|r!", 10.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[LENH TRUY NA!]", "|cff7dd3fc" + GetPlayerName(Player(bestPid)) + "|r dang bi TRUY NA trong |cffffd16690 giay|r! Tieu diet nhan |cffffd166+1.200 VANG|r - song sot nhan |cffffd166+1.000 VANG|r!", 10.0)')
    s = _rep(s,
             'call PAX_Announce("|cff4ade80[ESCAPED!]|r |cff7dd3fc" + GetPlayerName(Player(PAX_Fun_WantPid)) + "|r |cffe8ecf2survived the Wanted contract!|r (|cffffd166+1,000g|r)", 8.0)',
             'call PAX_Announce("|cff4ade80[TRUY NA KET THUC!]|r |cff7dd3fc" + GetPlayerName(Player(PAX_Fun_WantPid)) + "|r |cffe8ecf2da song sot qua lenh truy na!|r (|cffffd166+1.000 VANG|r)", 8.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[BOUNTY CLAIMED!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r hunted down WANTED |cff7dd3fc" + GetPlayerName(Player(deadPid)) + "|r! (|cffffd166+1,200g|r)", 9.0)',
             'call PAX_MajorEvent("|cffffd166", "[TIEN THUONG TRUY NA!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da san thanh cong muc tieu truy na |cff7dd3fc" + GetPlayerName(Player(deadPid)) + "|r! (|cffffd166+1.200 VANG THUONG|r)", 9.0)')

    s = _rep(s,
             'call PAX_Announce("|cffffd166[TREASURE]|r A |cffffd166Golden Treasure|r |cffe8ecf2appeared near Center! Catch it within 60s for|r |cffffd166+1,800g & Bonus Loot|r!", 9.0)',
             'call PAX_Announce("|cffffd166[KHO BAU HOANG KIM]|r Mot |cffffd166Kho Bau Hoang Kim|r |cffe8ecf2da xuat hien gan Trung Tam! San duoi ngay trong vong 60s de nhan|r |cffffd166+1.800 VANG & Do Quy|r!", 9.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[TREASURE SLAIN!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r caught the |cffffd166Golden Treasure|r! (|cffffd166+1,800g + Bonus Loot|r)", 9.0)',
             'call PAX_MajorEvent("|cffffd166", "[KHO BAU BI HA!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da bat duoc |cffffd166Kho Bau Hoang Kim|r! (|cffffd166+1.800 VANG + Do Quy|r)", 9.0)')
    s = _rep(s,
             'call PAX_Announce("|cff94a3b8[TREASURE]|r |cffe8ecf2The Golden Treasure escaped! Next spawn in 5 minutes.|r", 6.0)',
             'call PAX_Announce("|cff94a3b8[KHO BAU HOANG KIM]|r |cffe8ecf2Kho Bau Hoang Kim da tau thoat! Xuat hien lai sau 5 phut.|r", 6.0)')

    s = _rep(s,
             'call PAX_Announce("|cffffd166[GIANT MAGIKARP]|r |cffe8ecf2A suspicious Giant Magikarp splashed near Center! Free gold... or a trap?|r", 8.0)',
             'call PAX_Announce("|cffffd166[MAGIKARP KHONG LO]|r |cffe8ecf2Mot con Magikarp khong lo dang ngo xuat hien gan Trung Tam! Vang mien phi... hay la mot cai bay?|r", 8.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[IT\'S A TRAP!]", "Giant Magikarp evolved into |cffff5c5cRAGING RED GYARADOS|r! Defeat it for |cffffd166+3,000g & High-Tier Loot|r!", 10.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[DINH BAY ROI!]", "Magikarp khong lo da tien hoa thanh |cffff5c5cGYARADOS DO THINH NO|r! Tieu diet de nhan |cffffd166+3.000 VANG & Do Su Thi/Huyen Thoai|r!", 10.0)')
    s = _rep(s,
             'call PAX_Announce("|cffffd166[MAGIKARP]|r |cff7dd3fc" + GetPlayerName(killerP) + "|r |cffe8ecf2caught Giant Magikarp (+1,500g + Loot)!|r", 7.0)',
             'call PAX_Announce("|cffffd166[MAGIKARP]|r |cff7dd3fc" + GetPlayerName(killerP) + "|r |cffe8ecf2da bat duoc Magikarp khong lo (+1.500 VANG + Do Loot)!|r", 7.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[RED GYARADOS SLAIN!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r conquered |cffff5c5cRaging Red Gyarados|r! (|cffffd166+3,000g + Epic/Legendary Loot|r)", 9.0)',
             'call PAX_MajorEvent("|cffffd166", "[GYARADOS DO BI HA!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da chinh phuc |cffff5c5cGyarados Do Thinh No|r! (|cffffd166+3.000 VANG + Do Su Thi/Huyen Thoai|r)", 9.0)')

    s = _rep(s,
             'call PAX_Announce("|cff7dd3fc[RUNE]|r A " + PAX_Rune_Name(PAX_Rune_Kind) + " |cffe8ecf2spawned at|r |cffffd166" + locName + "|r!", 7.0)',
             'call PAX_Announce("|cff7dd3fc[CO NGU]|r Co ngu " + PAX_Rune_Name(PAX_Rune_Kind) + " |cffe8ecf2da xuat hien tai|r |cffffd166" + locName + "|r!", 7.0)')
    s = _rep(s,
             'call PAX_Announce("|cff38bdf8[RUNE]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2picked up|r |cff38bdf8Haste Rune|r (+35% MS/AS for 60s)!", 7.0)',
             'call PAX_Announce("|cff38bdf8[CO NGU]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2da nhat|r |cff38bdf8Co Ngu Toc Do|r (+35% Toc chay/danh trong 60s)!", 7.0)')
    s = _rep(s,
             'call PAX_Announce("|cffff5c5c[RUNE]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2picked up|r |cffff5c5cFury Rune|r (+25% Damage for 60s)!", 7.0)',
             'call PAX_Announce("|cffff5c5c[CO NGU]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2da nhat|r |cffff5c5cCo Ngu Cuong No|r (+25% Sat thuong trong 60s)!", 7.0)')
    s = _rep(s,
             'call PAX_Announce("|cff4ade80[RUNE]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2picked up|r |cff4ade80Regen Rune|r (8% HP & 12% Mana/s for 10s)!", 7.0)',
             'call PAX_Announce("|cff4ade80[CO NGU]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2da nhat|r |cff4ade80Co Ngu Hoi Phuc|r (8% Mau & 12% Mana/s trong 10s)!", 7.0)')
    s = _rep(s,
             'call PAX_Announce("|cffffd166[RUNE]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2picked up|r |cffffd166Bounty Rune|r (|cffffd166+600g & +500 XP|r for whole team)!", 8.0)',
             'call PAX_Announce("|cffffd166[CO NGU]|r |cff7dd3fc" + GetPlayerName(Player(pid)) + "|r |cffe8ecf2da nhat|r |cffffd166Co Ngu Tai Phu|r (|cffffd166+600 vang & +500 XP|r toan doi)!", 8.0)')

    # 9. Awakening Quest chain (-quest)
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cff4ade80[STAGE 1 COMPLETE]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Awakening Stage 2: collect 6 Blood Points from Elites, Legends or enemy Heroes (|cff7dd3fc-quest|r).|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cff4ade80[BUOC 1 HOAN TAT]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Buoc 2: Thu thap 6 Diem Huyet Te tu Quai Tinh Anh, Boss hoac Tuong dich (|cff7dd3fc-quest|r).|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffd896ff[STAGE 2 COMPLETE]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Stage 3: hold the Awakening Ritual at the Center Altar for|r |cffffd16660s|r!")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 10.0, "|cffd896ff[BUOC 2 HOAN TAT]|r |cffffd166" + PAX_Leg_Name(idx) + "|r |cffe8ecf2Buoc 3: Chiem giu Ban tho Thuc Tinh Trung Tam trong|r |cffffd16660 giay|r!")')
    s = _rep(s,
             'call PAX_Announce("|cffff5c5c[RITUAL]|r |cff7dd3fc" + GetPlayerName(p) + "|r (|cffffd166" + PAX_Leg_Name(idx) + "|r) |cffe8ecf2started Awakening at the Center Altar!|r", 10.0)',
             'call PAX_Announce("|cffff5c5c[NGHI LE]|r |cff7dd3fc" + GetPlayerName(p) + "|r (|cffffd166" + PAX_Leg_Name(idx) + "|r) |cffe8ecf2bat dau Nghi Le Thuc Tinh tai Ban tho Trung Tam!|r", 10.0)')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff4444" + PAX_Leg_Name(idx) + "\'s Awakening Ritual was disrupted! The quest regresses to Stage 2 and the attacker receives 1500 gold.|r")',
             'call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff4444Nghi Le Thuc Tinh cua " + PAX_Leg_Name(idx) + " da bi gian doan! Nhiem vu tro ve Buoc 2 va ke tan cong nhan 1500 vang.|r")')
    s = _rep(s,
             'call PAX_MajorEvent("|cffd896ff", "[AWAKENING COMPLETE]", "|cff7dd3fc" + GetPlayerName(p) + "|r\'s |cffffd166" + PAX_Leg_Name(idx) + "|r has awakened its Hidden Power!", 12.0)',
             'call PAX_MajorEvent("|cffd896ff", "[THUC TINH HOAN TAT]", "|cff7dd3fc" + GetPlayerName(p) + "|r da Thuc Tinh suc manh tiem an Hidden Power cua |cffffd166" + PAX_Leg_Name(idx) + "|r!", 12.0)')

    # -quest command chat output
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cff66ddff[Stage 1/3]|r Reach |cff00ff99Lv " + I2S(PAX_Leg_ReqLv(idx)) + "|r and earn 20 Wild points |cff00ff99(" + I2S(LoadInteger(PAX_Leg_HT, qk, 1)) + "/20)|r or 150000 damage |cff00ff99(" + I2S(R2I(LoadReal(PAX_Leg_HT, qk, 2))) + "/150000)|r.")\n'
             '                elseif stage == 2 then\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff9933[Stage 2/3]|r Blood Points |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 3)) + "/6|r. Kill Wild Elites (+2), enemy Heroes (+3) or Legend bosses (+6).")\n'
             '                elseif stage == 3 then\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff66cc[Stage 3/3]|r Ritual |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 4)) + "/60s|r at the Awakening Altar (Center).")\n'
             '                else\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffd896ff[AWAKENED]|r |cffffd166" + heroName + "|r |cffe8ecf2has awakened its Hidden Power!|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cff66ddff[Giai Doan 1/3]|r Dat |cff00ff99Cap " + I2S(PAX_Leg_ReqLv(idx)) + "|r va kiem 20 diem quai rung |cff00ff99(" + I2S(LoadInteger(PAX_Leg_HT, qk, 1)) + "/20)|r hoac 150.000 sat thuong |cff00ff99(" + I2S(R2I(LoadReal(PAX_Leg_HT, qk, 2))) + "/150000)|r.")\n'
             '                elseif stage == 2 then\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff9933[Giai Doan 2/3]|r Diem Huyet Te |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 3)) + "/6|r. Tieu diet Quai Tinh Anh (+2), Tuong dich (+3) hoac Boss Legend (+6).")\n'
             '                elseif stage == 3 then\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 10.0, title + " " + heroName + " |cffff66cc[Giai Doan 3/3]|r Nghi Le |cff00ff99" + I2S(LoadInteger(PAX_Leg_HT, qk, 4)) + "/60s|r tai Ban tho Thuc Tinh (Trung Tam).")\n'
             '                else\n'
             '                    call DisplayTimedTextToPlayer(p, 0, 0, 8.0, "|cffd896ff[DA THUC TINH]|r |cffffd166" + heroName + "|r |cffe8ecf2da Thuc Tinh suc manh tiem an Hidden Power!|r")')

    s = _rep(s,
             'call DialogSetMessage(d, "Legend Selection (page " + I2S(page + 1) + " of " + I2S(pages) + ")")',
             'call DialogSetMessage(d, "Chon Pokemon Huyen Thoai (trang " + I2S(page + 1) + " / " + I2S(pages) + ")")')
    s = _rep(s, 'DialogAddButton(d, "< Prev page", 0)', 'DialogAddButton(d, "< Trang truoc", 0)')
    s = _rep(s, 'DialogAddButton(d, "Next page >", 0)', 'DialogAddButton(d, "Trang sau >", 0)')

    # 10. Gym & League
    s = _rep(s,
             '|cffffcc00No gym battle right now.|r',
             '|cffffcc00Hien tai khong co tran dau Gym nao dang dien ra.|r')
    s = _rep(s,
             'set s = "|cffffcc00Gym " + I2S(g + 1) + "|r: " + GetPlayerName(Player(Gym_Pid[g])) + ", Pokemon " + I2S(Gym_Stage[g] + 1) + " of 6"',
             'set s = "|cffffcc00Gym " + I2S(g + 1) + "|r: " + GetPlayerName(Player(Gym_Pid[g])) + ", Pokemon " + I2S(Gym_Stage[g] + 1) + " / 6"')
    s = _rep(s,
             'set s = s + ", current: none (it will be spawned again)"',
             'set s = s + ", hien tai: khong co (sap xuat hien lai)"')
    s = _rep(s,
             'set s = s + ", current: " + GetUnitName(Gym_Cur[g]) + " " + I2S(R2I(GetWidgetLife(Gym_Cur[g]))) + " HP at " + I2S(R2I(SquareRoot((GetUnitX(Gym_Cur[g]) - Gym_X[g]) * (GetUnitX(Gym_Cur[g]) - Gym_X[g]) + (GetUnitY(Gym_Cur[g]) - Gym_Y[g]) * (GetUnitY(Gym_Cur[g]) - Gym_Y[g])))) + " from the centre"',
             'set s = s + ", hien tai: " + GetUnitName(Gym_Cur[g]) + " " + I2S(R2I(GetWidgetLife(Gym_Cur[g]))) + " Mau, cach tam dai " + I2S(R2I(SquareRoot((GetUnitX(Gym_Cur[g]) - Gym_X[g]) * (GetUnitX(Gym_Cur[g]) - Gym_X[g]) + (GetUnitY(Gym_Cur[g]) - Gym_Y[g]) * (GetUnitY(Gym_Cur[g]) - Gym_Y[g]))))')
    s = _rep(s, 'set s = "  team:"', 'set s = "  doi hinh:"')

    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00You need a Pokemon.|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Ban can co mot Pokemon.|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffff4040The Pokemon League needs all 8 badges (you have " + I2S(Badge_Count(pid)) + ").|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffff4040Khieu chien Tu Dai Thien Vuong can du ca 8 huy hieu (hien co " + I2S(Badge_Count(pid)) + ").|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Finish your gym battle first.|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Hay hoan thanh tran dau Gym truoc.|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Pokemon League: ready again in " + I2S(R2I(League_Cool[pid] - Mega_Time + 0.99)) + "s.|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 6.0, "|cffffcc00Khieu chien Tu Dai Thien Vuong: co the thu lai sau " + I2S(R2I(League_Cool[pid] - Mega_Time + 0.99)) + " giay.|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 8.0, "|cffff4040Pokemon League: " + why + " Try again in 30 seconds.|r")',
             'call DisplayTimedTextToPlayer(Player(League_Pid), 0, 0, 8.0, "|cffff4040Khieu chien Tu Dai Thien Vuong: " + why + " Thu lai sau 30 giay.|r")')
    s = _rep(s,
             'call PAX_MajorEvent("|cffffd166", "[LEAGUE CHAMPION]", "|cff7dd3fc" + GetPlayerName(p) + "|r defeated Champion Lance and is the new Pokemon Champion!", 15.0)',
             'call PAX_MajorEvent("|cffffd166", "[QUAN QUAN LEAGUE]", "|cff7dd3fc" + GetPlayerName(p) + "|r da danh bai Nha Vo Dich Lance va tro thanh Quan Quan Pokemon moi!", 15.0)')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(p, 0, 0, 15.0, "|cff66ff66Title [Champion]: +15% STR / AGI / INT, Champion Aura (allies within 800: +10% damage, -10% damage taken), 10000 gold, a Mega Ring, Shiny Charm (Shiny 1/20).|r")',
             'call DisplayTimedTextToPlayer(p, 0, 0, 15.0, "|cff66ff66Danh hieu [Champion]: +15% STR / AGI / INT, Hao quang Quan Quan (dong minh trong 800: +10% sat thuong, -10% sat thuong nhan), 10.000 vang, 1 Nhan Mega Ring, Shiny Charm (ti le Shiny 1/20).|r")')

    # 11. Duel
    s = _rep(s,
             'call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff8800Duel: " + GetPlayerName(Player(a)) + " vs " + GetPlayerName(Player(b)) + "! The first Pokemon under 15% HP loses.|r")',
             'call DisplayTimedTextToPlayer(GetLocalPlayer(), 0, 0, 8.0, "|cffff8800Dau giao huu: " + GetPlayerName(Player(a)) + " vs " + GetPlayerName(Player(b)) + "! Pokemon dau tien duoi 15% Mau se thua cuoc.|r")')
    s = _rep(s,
             'call PAX_Announce("|cff4ade80[DUEL VICTORY]|r |cff7dd3fc" + GetPlayerName(Player(win)) + "|r |cffe8ecf2beat|r |cff7dd3fc" + GetPlayerName(Player(lose)) + "|r! (|cffffd166+500g|r)", 8.0)',
             'call PAX_Announce("|cff4ade80[GIAO HUU CHIEN THANG]|r |cff7dd3fc" + GetPlayerName(Player(win)) + "|r |cffe8ecf2da danh bai|r |cff7dd3fc" + GetPlayerName(Player(lose)) + "|r! (|cffffd166+500 vang|r)", 8.0)')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Nobody is waiting for your answer.|r")',
             'call DisplayTimedTextToPlayer(Player(me), 0, 0, 6.0, "|cffffcc00Khong co ai dang cho cau tra loi cua ban.|r")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00" + GetPlayerName(Player(me)) + " declined the duel.|r")',
             'call DisplayTimedTextToPlayer(Player(a), 0, 0, 6.0, "|cffffcc00" + GetPlayerName(Player(me)) + " da tu choi loi moi dau giao huu.|r")')

    # 12. Underdog Supply & Match Point & First Blood & Shutdown
    s = _rep(s,
             'call PAX_MajorEvent("|cff4ade80", "[UNDERDOG SUPPLY]", teamName + " is trailing by 10+ Points! Every ally got |cffffd166+1,000g|r and a |cffd896ffSupply Loot|r at Base!", 9.0)',
             'call PAX_MajorEvent("|cff4ade80", "[TIEP TE LAT KEO]", teamName + " dang bi dan tu 10 diem tro len! Moi dong minh nhan |cffffd166+1.000 VANG|r va 1 |cffd896ffHom Tiep Te|r tai can cu!", 9.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[MATCH POINT!]", "|cff66ccffTeam 1|r is only |cffffd166" + I2S(PAX_Win_Target - t1Pts) + " Points|r away from victory!", 10.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[DIEM TRAN DAU!]", "|cff66ccffDoi 1|r chi con cach chien thang |cffffd166" + I2S(PAX_Win_Target - t1Pts) + " Diem|r!", 10.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[MATCH POINT!]", "|cffff7777Team 2|r is only |cffffd166" + I2S(PAX_Win_Target - t2Pts) + " Points|r away from victory!", 10.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[DIEM TRAN DAU!]", "|cffff7777Doi 2|r chi con cach chien thang |cffffd166" + I2S(PAX_Win_Target - t2Pts) + " Diem|r!", 10.0)')
    s = _rep(s,
             'call PAX_MajorEvent("|cffff5c5c", "[FIRST BLOOD!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r drew First Blood on |cff7dd3fc" + GetPlayerName(victimP) + "|r (|cffffd166+800g|r)!", 9.0)',
             'call PAX_MajorEvent("|cffff5c5c", "[CHIEN CONG DAU!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da doat Chien Cong Dau tu |cff7dd3fc" + GetPlayerName(victimP) + "|r (|cffffd166+800 vang|r)!", 9.0)')
    s = _rep(s,
             '                call PAX_MajorEvent("|cffff5c5c", "[SHUTDOWN!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r ended |cff7dd3fc" + GetPlayerName(victimP) + "|r\'s |cffff5c5c" + I2S(vicStreak) + "-kill streak|r (" + victimLabel + ", |cffffd166+" + I2S(bounty) + "g|r)!", 9.0)\n'
             '            else\n'
             '                call PAX_Announce("|cffff5c5c[SHUTDOWN]|r |cff7dd3fc" + GetPlayerName(killerP) + "|r |cffe8ecf2ended|r |cff7dd3fc" + GetPlayerName(victimP) + "|r\'s |cffff5c5c" + I2S(vicStreak) + "-kill streak|r (|cffffd166+" + I2S(bounty) + "g|r)!", 8.0)\n'
             '            endif\n'
             '        else\n'
             '            call PAX_MajorEvent("|cffff5c5c", "[SHUTDOWN!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r defeated |cffffd166" + victimLabel + "|r (|cffffd166+" + I2S(bounty) + "g|r)!", 9.0)',
             '                call PAX_MajorEvent("|cffff5c5c", "[CHAM DUT CHUOI!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da cham dut chuoi |cffff5c5c" + I2S(vicStreak) + " mang|r cua |cff7dd3fc" + GetPlayerName(victimP) + "|r (" + victimLabel + ", |cffffd166+" + I2S(bounty) + " vang|r)!", 9.0)\n'
             '            else\n'
             '                call PAX_Announce("|cffff5c5c[CHAM DUT CHUOI]|r |cff7dd3fc" + GetPlayerName(killerP) + "|r |cffe8ecf2da cham dut chuoi|r |cffff5c5c" + I2S(vicStreak) + " mang|r cua |cff7dd3fc" + GetPlayerName(victimP) + "|r (|cffffd166+" + I2S(bounty) + " vang|r)!", 8.0)\n'
             '            endif\n'
             '        else\n'
             '            call PAX_MajorEvent("|cffff5c5c", "[HA GUC MUC TIEU LON!]", "|cff7dd3fc" + GetPlayerName(killerP) + "|r da danh bai |cffffd166" + victimLabel + "|r (|cffffd166+" + I2S(bounty) + " vang|r)!", 9.0)')

    # 13. God Chu & Ash's Cap
    s = _rep(s,
             'call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cffffd166[GOD CHU]|r |cffe8ecf2Reached Stage " + I2S(stage) + ":|r |cffffd166+" + I2S(R2I(pct * 100.0)) + "% All Base Stats|r (max +500 each)!")',
             'call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0, 0, 8.0, "|cffffd166[GOD CHU]|r |cffe8ecf2Dat Giai Doan " + I2S(stage) + ":|r |cffffd166+" + I2S(R2I(pct * 100.0)) + "% Tat Ca Chi So Co Ban|r (toi da +500 moi chi so)!")')
    s = _rep(s,
             'call DisplayTimedTextToPlayer(ownerPl, 0, 0, 6.0, "|cffff5c5c[ASH\'S CAP]|r Only |cffffd166Pikachu|r (before evolving into Raichu) can wear Ash\'s Cap! 500g refunded.")',
             'call DisplayTimedTextToPlayer(ownerPl, 0, 0, 6.0, "|cffff5c5c[MU CUA ASH]|r Chi |cffffd166Pikachu|r (truoc khi tien hoa thanh Raichu) moi doi duoc Mu Cua Ash! Hoan tra lai 500 vang.")')

    # 14. -title Overhead title messages
    s = _rep(s,
             '|cff94a3b8[TITLE]|r No titles unlocked yet (5 kills, Legend Boss, Jackpot, 20k gold, Champion, Wanted).',
             '|cff94a3b8[DANH HIEU]|r Chua mo khoa danh hieu nao (5 mang ha guc, Boss Legend, Jackpot, 20k vang, Champion, Wanted).')
    s = _rep(s,
             '|cff7dd3fc[TITLE]|r Overhead title |cff94a3b8hidden|r.',
             '|cff7dd3fc[DANH HIEU]|r Da |cff94a3b8an|r danh hieu tren dau.')
    s = _rep(s,
             '|cff7dd3fc[TITLE]|r Switched to ',
             '|cff7dd3fc[DANH HIEU]|r Da chuyen sang ')

    # 15. Loot items tooltips and stat names
    s = _rep(s, 'return "All Stats +" + I2S(value)', 'return "Tat ca chi so +" + I2S(value)')
    s = _rep(s, 'return "Armor +" + I2S(value)', 'return "Giap +" + I2S(value)')
    s = _rep(s, 'return "Max HP +" + I2S(value)', 'return "Mau toi da +" + I2S(value)')
    s = _rep(s, 'return "Attack Speed +" + I2S(value) + "%"', 'return "Toc do danh +" + I2S(value) + "%"')
    s = _rep(s, 'return "Move Speed +" + I2S(value)', 'return "Toc do chay +" + I2S(value)')

    s = _rep(s, 'local string kindName = "Stat Relic"', 'local string kindName = "Co Vat Chi So"')
    s = _rep(s, 'set kindName = "Effect Charm"', 'set kindName = "Bua Hieu Ung"')

    s = _rep(s,
             '    if tier == 1 then\n'
             '        return "Common"\n'
             '    elseif tier == 2 then\n'
             '        return "Rare"\n'
             '    elseif tier == 3 then\n'
             '        return "Epic"\n'
             '    endif\n'
             '    return "Legendary"',
             '    if tier == 1 then\n'
             '        return "Thuong"\n'
             '    elseif tier == 2 then\n'
             '        return "Hiem"\n'
             '    elseif tier == 3 then\n'
             '        return "Su Thi"\n'
             '    endif\n'
             '    return "Huyen Thoai"')

    s = _rep(s,
             'set details = "Lifesteal " + I2S(effectVal) + "% of damage"',
             'set details = "Hut Mau: Hut " + I2S(effectVal) + "% sat thuong don danh thanh Mau"')
    s = _rep(s,
             'set details = "Critical: " + I2S(effectVal) + "% chance for x1.5 attack/move damage"',
             'set details = "Chi Mang: " + I2S(effectVal) + "% co hoi gay x1.5 sat thuong don danh/chieu thuc"')
    s = _rep(s,
             'set details = "Thorns: reflect " + I2S(effectVal) + "% incoming damage (0.5s ICD)"',
             'set details = "Gai Phan Don: Phan lai " + I2S(effectVal) + "% sat thuong ganh chiu (Hoi 0.5s)"')
    s = _rep(s,
             'set details = "Treasure Hunter: +" + I2S(effectVal) + "% kill gold"',
             'set details = "Tho San: Nhan them +" + I2S(effectVal) + "% vang khi ha guc muc tieu"')

    # Replace sell string in loot item creation and forge
    s = s.replace('"|nSell: " + I2S(sell) + "g"', '"|nGia ban: " + I2S(sell) + " vang"')
    s = s.replace('"|nSell: " + I2S(PAX_Loot_SellValue(tier) * (100 + newLv * 40) / 100) + "g"',
                  '"|nGia ban: " + I2S(PAX_Loot_SellValue(tier) * (100 + newLv * 40) / 100) + " vang"')

    # 26. Startup pick, repick and utility commands
    s = s.replace('"|cffffcc00The host types -random and every player gets a random Pokemon. Players who have not chosen after 45 seconds get one automatically. Type -repick in the first 2 minutes to get another random Pokemon (2 times, level and items are kept).|r"',
                  '"|cffffcc00Chu phong go -random de phat ngau nhien Pokemon cho moi nguoi. Nguoi chua chon sau 45s se nhan ngau nhien. Go -repick trong 2 phut dau de doi Pokemon khac (toi da 2 lan, giu cap & do).|r"')
    s = s.replace('"|cffffcc00You already have a Pokemon. Type -repick in the first 2 minutes to get a random one instead.|r"',
                  '"|cffffcc00Ban da co Pokemon roi. Go -repick trong 2 phut dau neu muon doi ngau nhien Pokemon khac.|r"')
    s = s.replace('"|cffffcc00Another player already has that Pokemon.|r"',
                  '"|cffffcc00Nguoi choi khac da chon Pokemon nay roi.|r"')
    s = s.replace('"|cffffcc00Only the host can type -random.|r"',
                  '"|cffffcc00Chi chu phong moi co the go lenh -random.|r"')
    s = s.replace('"|cffffcc00Repick is only allowed in the first 2 minutes.|r"',
                  '"|cffffcc00Chi duoc phep doi lai Pokemon trong 2 phut dau tran.|r"')
    s = s.replace('"|cffffcc00You have no repicks left.|r"',
                  '"|cffffcc00Ban da het so luot doi Pokemon.|r"')
    s = s.replace('"|cffffcc00You need a living Pokemon (not in Mega form) to repick.|r"',
                  '"|cffffcc00Ban can Pokemon con song (khong o dang Mega) de doi.|r"')
    s = s.replace('"|cffffcc00Pick a living Pokemon first.|r"',
                  '"|cffffcc00Hay chon mot Pokemon truoc.|r"')
    s = s.replace('"|cffffcc00-tp: back to your base and healed in 3 seconds...|r"',
                  '"|cffffcc00-tp: bien ve can cu va hoi phuc sau 3 giay...|r"')
    s = s.replace('"|cffffcc00-home: returning home in 5 seconds...|r"',
                  '"|cffffcc00-home: tro ve nha sau 5 giay...|r"')
    s = s.replace('"|cffffcc00Escape Rope: back to base in 3 seconds...|r"',
                  '"|cffffcc00Day Thoat Hiem: ve can cu sau 3 giay...|r"')
    s = s.replace('"|cffffcc00Pokemon League: walk into the arena circle with 8 badges (or type -league). The Exit portal leads back to your base.|r"',
                  '"|cffffcc00Pokemon League: buoc vao vong tron dau truong khi du 8 huy hieu (hoac go -league). Cong Exit dan ve can cu.|r"')

    # Clean up old corrupt TCVN3 startup hint (fixes font issue in chat/quest prompt)
    s = re.sub(
        r'call QuestMessageBJ\(GetPlayersAll\(\),\s*bj_QUESTMESSAGE_ALWAYSHINT,\s*"Pick 1 Pokemon[^"]*"\)',
        'call QuestMessageBJ(GetPlayersAll(),bj_QUESTMESSAGE_ALWAYSHINT,"Chon 1 Pokemon farm cung dong doi, up cap, tien hoa, san Pokemon Huyen Thoai, thi dau Pk...\\n\\nGo -help hoac bam [F9] de xem huong dan chi tiet.\\n")',
        s
    )

    return s


def patch_strings(items_slk, func_txt, strings_txt):
    """Localizes item tooltips in ItemFunc.txt for Battle Items and Loot items."""
    # Common / Rare / Epic / Legendary Loot
    func_txt = func_txt.replace('Tip=|cffffffffCommon Loot|r', 'Tip=|cffffffffDo Loot Thuong|r')
    func_txt = func_txt.replace('Tip=|cff3399ffRare Loot|r', 'Tip=|cff3399ffDo Loot Hiem|r')
    func_txt = func_txt.replace('Tip=|cffcc66ffEpic Loot|r', 'Tip=|cffcc66ffDo Loot Su Thi|r')
    func_txt = func_txt.replace('Tip=|cffff8800Legendary Loot|r', 'Tip=|cffff8800Do Loot Huyen Thoai|r')

    # Battle Items
    # IB01: Choice Band
    func_txt = func_txt.replace(
        'Ubertip=Attacks deal +35% damage. -10% move speed.',
        'Ubertip=Tang +35% sat thuong don danh. Giam -10% toc do di chuyen.'
    )
    # IB04: Leftovers
    func_txt = func_txt.replace(
        'Ubertip=Regenerates 1% max HP per second.',
        'Ubertip=Hoi phuc 1% Mau toi da moi giay.'
    )
    func_txt = func_txt.replace(
        'Description=Regenerates 1% max HP per second.',
        'Description=Hoi phuc 1% Mau toi da moi giay.'
    )
    # IB05: Focus Sash
    func_txt = func_txt.replace(
        'Ubertip=A hit that would knock it out while above 50% HP leaves it at 1 HP (once every 60s).',
        'Ubertip=Don danh ket lieu khi Mau tren 50% se giu lai 1 Mau (Hoi chieu 60 giay mot lan).'
    )
    func_txt = func_txt.replace(
        'Description=A hit that would knock it out while above 50% HP leaves it at 1 HP (once every 60s).',
        'Description=Don danh ket lieu khi Mau tren 50% se giu lai 1 Mau (Hoi chieu 60 giay mot lan).'
    )

    return func_txt
