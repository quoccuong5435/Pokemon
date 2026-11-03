"""One-off: (1) Poke Center heals x3 (ACnr), (2) two more teleport items (Celebi, Darkrai) in the Haunt Legendary shop
n030 with the script that teleports the buyer to their rooms."""
import io

NL = chr(10)


def read(path, enc='utf-8'):
    return io.open(path, encoding=enc, newline='').read()


def write(path, s, enc='utf-8'):
    io.open(path, 'w', encoding=enc, newline='').write(s)


def fix(s, text):
    return text.replace(NL, chr(13) + NL) if (chr(13) + NL) in s else text


# ------------------------------------------------------------------ objects.py
p = 'tools/objects.py'
s = read(p)
ret = "    return s.to_text().encode('latin-1'), _append_txt(txt_data, sections)" + NL
i = s.index('def _abilities(')
j = s.index(ret, i)
heal = ("    # v3.3: the Poke Center (unit n00P) heals faster: its regeneration aura ACnr, DataA1 = fraction of max HP per second" + NL +
        "    row = s.find('ACnr')" + NL +
        "    if row is not None:" + NL +
        "        x = s.name_to_x['DataA1']" + NL +
        "        row[x] = repr(round(float(row[x]) * POKE_CENTER_HEAL_MULT, 4))" + NL)
s = s[:j] + heal + s[j:]
s = s.replace('HERO_HP_MULT = 2.0', 'POKE_CENTER_HEAL_MULT = 3.0  # Poke Center regeneration x3 (5% -> 15% of max HP per second)' + NL +
              'HERO_HP_MULT = 2.0', 1)

# two more teleport items for the Haunt Legendary shop n030 (sold items = usei)
tele_consts = (
    "# v3.3: teleport items of the Haunt Legendary shop (n030): id, name, icon, button position, hotkey" + NL +
    "LEGEND_TELE_ITEMS = (('IL00', \"Celebi's Location\", 'BTNMew (64 x 64).blp', '2,1', 'C')," + NL +
    "                     ('IL01', \"Darkrai's Location\", 'BTNDarkrai (64 x 64).blp', '3,1', 'D'))" + NL)
s = s.replace('POKE_CENTER_HEAL_MULT = 3.0', tele_consts + 'POKE_CENTER_HEAL_MULT = 3.0', 1)

# the items: rows in _items (cloned from I025 = Lugia's Location) + text sections
items_end = "    souls = [w for w in (getattr(a, 'wild_souls', None) or ()) if w.new]" + NL
assert s.count(items_end) == 1
add_items = (
    "    for iid, iname, ico, pos, hot in LEGEND_TELE_ITEMS:" + NL +
    "        _row_from(s, 'I025', iid, {})" + NL +
    "        sections.append(_section(iid, [" + NL +
    "            ('Name', iname), ('Hotkey', hot), ('Tip', 'Teleport to |cffffcc00%s [%s]|r' % (iname, hot))," + NL +
    "            ('Ubertip', 'Haunt ' + iname.split(\"'\")[0]), ('Description', 'Haunt ' + iname.split(\"'\")[0])," + NL +
    "            ('Art', ico), ('Buttonpos', pos)]))" + NL)
s = s.replace(items_end, add_items + items_end)

# the shop sells them
hero_anchor = "    poke = getattr(a, 'poke', None)" + NL
assert s.count(hero_anchor) == 1
shop = ("    shop = f.find('n030')" + NL +
        "    if shop is not None:  # v3.3: Haunt Legendary also teleports to Celebi and Darkrai" + NL +
        "        shop.set('usei', T_STRING, shop.get('usei') + ',' + ','.join(i[0] for i in LEGEND_TELE_ITEMS))" + NL)
s = s.replace(hero_anchor, shop + hero_anchor)
write(p, s)

# ------------------------------------------------------------------ mega.j
J = 'tools/jass/mega.j'
m = read(J, 'latin-1')
fn = (
    "// Haunt Legendary shop (v3.3): the Celebi and Darkrai teleport items move the buyer next to their rooms" + NL +
    "function LegTele_OnSell takes nothing returns boolean" + NL +
    "    local integer it = GetItemTypeId(GetSoldItem())" + NL +
    "    local unit b = GetBuyingUnit()" + NL +
    "    if it == 'IL00' then" + NL +
    "        call SetUnitPosition(b, 9600.0, -2588.0)" + NL +
    "    elseif it == 'IL01' then" + NL +
    "        call SetUnitPosition(b, -9600.0, -2209.0)" + NL +
    "    else" + NL +
    "        set b = null" + NL +
    "        return false" + NL +
    "    endif" + NL +
    "    call PanCameraToTimedForPlayer(GetOwningPlayer(b), GetUnitX(b), GetUnitY(b), 0.25)" + NL +
    "    set b = null" + NL +
    "    return false" + NL +
    "endfunction" + NL + NL +
    "function Mega_Init takes nothing returns nothing" + NL)
anchor = "function Mega_Init takes nothing returns nothing" + NL
assert m.count(anchor) == 1
m = m.replace(anchor, fn)
init_anchor = "    call Pick_Init()" + NL
assert m.count(init_anchor) == 1
m = m.replace(init_anchor, init_anchor +
              "    set lt = CreateTrigger()" + NL +
              "    call TriggerRegisterAnyUnitEventBJ(lt, EVENT_PLAYER_UNIT_SELL_ITEM)" + NL +
              "    call TriggerAddCondition(lt, Condition(function LegTele_OnSell))" + NL)
# the local trigger of Mega_Init
head = "function Mega_Init takes nothing returns nothing" + NL + "    local trigger t = CreateTrigger()" + NL
assert m.count(head) == 1
m = m.replace(head, head + "    local trigger lt = null" + NL)
write(J, m, 'latin-1')

# ------------------------------------------------------------------ jasscheck.py
jc = read('tools/jasscheck.py')
a = "'GetSoldUnit': 0,"
assert jc.count(a) == 1
jc = jc.replace(a, a + " 'GetSoldItem': 0, 'GetBuyingUnit': 0, 'SetUnitPosition': 3, 'PanCameraToTimedForPlayer': 4,")
b = "'EVENT_PLAYER_UNIT_SELECTED',"
assert jc.count(b) == 1
jc = jc.replace(b, b + " 'EVENT_PLAYER_UNIT_SELL_ITEM',")
write('tools/jasscheck.py', jc)
print('ok')
