"""Updates all item icons in ItemFunc.txt to authentic Pokemon item icons:
1. Mega Stones (33 items): Exact Mega Pokemon portrait (BTNMegaCharizardX, BTNMegaLucario, etc.)
2. Paradox Boosters (10 items): Exact Pokemon portrait (Suicune, Entei, Raikou, Salamence, Magneton, Misdreavus, Jigglypuff, Tyranitar, Gallade, Hydreigon)
3. Form Items (11 items): Exact Legend Pokemon portrait (Kyogre, Groudon, Arceus, Deoxys, etc.)
4. Evolution Stones & Held Items: Official Pokemon item icons (FireStone, Leftovers, Charcoal, etc.)
"""
import re

# 1. Mega Stones -> Mega Pokemon Portraits (33 items)
MEGA_STONE_ICONS = {
    'IM00': r'ReplaceableTextures\CommandButtons\BTNMegaVenusaur.blp',
    'IM01': r'ReplaceableTextures\CommandButtons\BTNMegaCharizardX.blp',
    'IM02': r'ReplaceableTextures\CommandButtons\BTNMegaCharizardY.blp',
    'IM03': r'ReplaceableTextures\CommandButtons\BTNMegaBlastoise.blp',
    'IM04': r'ReplaceableTextures\CommandButtons\BTNMegaBeedrill.blp',
    'IM05': r'ReplaceableTextures\CommandButtons\BTNMegaPidgeot.blp',
    'IM06': r'ReplaceableTextures\CommandButtons\BTNMegaAlakazam.blp',
    'IM07': r'ReplaceableTextures\CommandButtons\BTNMegaGengar.blp',
    'IM08': r'ReplaceableTextures\CommandButtons\BTNMegaKangaskhan.blp',
    'IM09': r'ReplaceableTextures\CommandButtons\BTNMegaPinsir.blp',
    'IM0A': r'ReplaceableTextures\CommandButtons\BTNMegaGyarados.blp',
    'IM0B': r'ReplaceableTextures\CommandButtons\BTNMegaSteelix.blp',
    'IM0C': r'ReplaceableTextures\CommandButtons\BTNMegaScizor.blp',
    'IM0D': r'ReplaceableTextures\CommandButtons\BTNMegaMewtwoX.blp',
    'IM0E': r'ReplaceableTextures\CommandButtons\BTNMegaMewtwoY.blp',
    'IM0F': r'ReplaceableTextures\CommandButtons\BTNMegaRayquaza.blp',
    'IM0G': r'ReplaceableTextures\CommandButtons\BTNMegaBlaziken.blp',
    'IM0H': r'ReplaceableTextures\CommandButtons\BTNMegaSceptile.blp',
    'IM0I': r'ReplaceableTextures\CommandButtons\BTNMegaTyranitar.blp',
    'IM0J': r'ReplaceableTextures\CommandButtons\BTNMegaGardevoir.blp',
    'IM0K': r'ReplaceableTextures\CommandButtons\BTNMegaGallade.blp',
    'IM0L': r'ReplaceableTextures\CommandButtons\BTNMegaSalamence.blp',
    'IM0M': r'ReplaceableTextures\CommandButtons\BTNMegaMetagross.blp',
    'IM0N': r'ReplaceableTextures\CommandButtons\BTNMegaLucario.blp',
    'IM0O': r'ReplaceableTextures\CommandButtons\BTNMegaAbsol.blp',
    'IM0P': r'ReplaceableTextures\CommandButtons\BTNMegaSlowbro.blp',
    'IM0Q': r'ReplaceableTextures\CommandButtons\BTNMegaSharpedo.blp',
    'IM0R': r'ReplaceableTextures\CommandButtons\BTNMegaAmpharos.blp',
    'IM0S': r'ReplaceableTextures\CommandButtons\BTNMegaHoundoom.blp',
    'IM0T': r'ReplaceableTextures\CommandButtons\BTNMegaAerodactyl.blp',
    'IM0U': r'ReplaceableTextures\CommandButtons\BTNMegaManectric.blp',
    'IM0V': r'ReplaceableTextures\CommandButtons\BTNMegaHeracross.blp',
    'IM0W': r'ReplaceableTextures\CommandButtons\BTNMegaAltaria.blp',
}

# 2. Form Items -> Legend Pokemon Portraits (11 items)
FORM_ITEM_ICONS = {
    'IM0X': r'ReplaceableTextures\CommandButtons\BTNPokeKyogre.blp',
    'IM0Y': r'ReplaceableTextures\CommandButtons\BTNPokeGroudon.blp',
    'IM0Z': r'ReplaceableTextures\CommandButtons\BTNPokeLatiasLatios.blp',
    'IM10': 'BTNArceus (64 x 64).blp',
    'IM11': 'BTNArticuno (64 x 64).blp',
    'IM12': 'BTNZapdos (64 x 64).blp',
    'IM13': 'BTNMoltres (64 x 64).blp',
    'IM14': 'BTNGiratina (64 x 64).blp',
    'IM15': 'BTNDialga (64 x 64).blp',
    'IM16': 'BTNPalkia (64 x 64).blp',
    'IM17': 'BTNDeoxys (64 x 64).blp',
}

# 3. Paradox Booster Energy Items -> Specific Pokemon Portraits (10 items)
PARADOX_ITEM_ICONS = {
    'IM18': r'ReplaceableTextures\CommandButtons\BTNPokeSuicune.blp',        # Walking Wake (Suicune)
    'IM19': r'ReplaceableTextures\CommandButtons\BTNPokeEntei.blp',          # Gouging Fire (Entei)
    'IM1A': r'ReplaceableTextures\CommandButtons\BTNPokeRaikou.blp',         # Raging Bolt (Raikou)
    'IM1B': r'ReplaceableTextures\CommandButtons\BTNMegaSalamence.blp',      # Roaring Moon (Salamence)
    'IM1C': 'BTNMagneton (64 x 64).blp',                                     # Sandy Shocks (Magneton)
    'IM1D': r'ReplaceableTextures\CommandButtons\BTNWildMisdreavus.blp',     # Flutter Mane (Misdreavus)
    'IM1E': r'ReplaceableTextures\CommandButtons\BTNPokeJigglypuff.blp',     # Scream Tail (Jigglypuff)
    'IM1F': 'BTNTyranitar (64 x 64).blp',                                    # Iron Thorns (Tyranitar)
    'IM1G': r'ReplaceableTextures\CommandButtons\BTNMegaGallade.blp',        # Iron Valiant (Gallade)
    'IM1H': r'ReplaceableTextures\CommandButtons\BTNPokeHydreigon.blp',      # Iron Jugulis (Hydreigon)
}

# 4. Authentic Pokemon Held & Evolution Items (Actual Map Item IDs)
HELD_ITEM_ICONS = {
    'I00L': 'BTNFireStone (64 x 64).blp',
    'I00M': 'BTNWaterStone (64 x 64).blp',
    'I00N': 'BTNThunderStone (64 x 64).blp',
    'I00K': 'BTNLeafStone (64 x 64).blp',
    'I00O': 'BTNMoonStone (64 x 64).blp',
    'I00P': 'BTNSunStone (64 x 64).blp',
    'IB04': 'BTNLeftovers (64 x 64).blp',
    'I00Q': 'BTNCharcoal (64 x 64).blp',
    'I00S': 'BTNMystic_Water (64 x 64).blp',
    'I00T': 'BTNMagnet (64 x 64).blp',
    'I00R': 'BTNMiracle_Seed (64 x 64).blp',
    'I012': 'BTNHard_Stone (64 x 64).blp',
    'I011': 'BTNBlack_Belt (64 x 64).blp',
    'I010': 'BTNTwistedSpoon (64 x 64).blp',
    'I020': 'BTNSpell Tag (64 x 64).blp',
    'I00X': 'BTNDragon_Fang (64 x 64).blp',
    'I00W': 'BTNNeverMeltIce (64 x 64).blp',
    'I00Z': 'BTNSilk_Scarf (64 x 64).blp',
    'I01Y': 'BTNBlack Glasses (64 x 64).blp',
    'I00Y': 'BTNSharp_Beak (64 x 64).blp',
    'I00U': 'BTNSilverPowder (64 x 64).blp',
    'I00V': 'BTNPoison_Barb (64 x 64).blp',
}

ALL_ITEM_ICON_UPDATES = {}
ALL_ITEM_ICON_UPDATES.update(MEGA_STONE_ICONS)
ALL_ITEM_ICON_UPDATES.update(FORM_ITEM_ICONS)
ALL_ITEM_ICON_UPDATES.update(PARADOX_ITEM_ICONS)
ALL_ITEM_ICON_UPDATES.update(HELD_ITEM_ICONS)


def patch_item_func(func_txt: str) -> str:
    """Updates Art= for items in ItemFunc.txt to authentic Pokemon icons."""
    sections = re.split(r'(?m)^\[([A-Za-z0-9_]{4})\]\r?\n', func_txt)
    result = [sections[0]]
    patched = 0

    for i in range(1, len(sections), 2):
        item_id = sections[i]
        body = sections[i + 1]

        if item_id in ALL_ITEM_ICON_UPDATES:
            icon = ALL_ITEM_ICON_UPDATES[item_id]
            if 'Art=' in body:
                body = re.sub(r'Art=[^\r\n]+', lambda _: f'Art={icon}', body, count=1)
            else:
                body = f'Art={icon}\n' + body
            patched += 1

        result.append(f'[{item_id}]\n{body}')

    print(f"[pokemon_item_icons] Successfully updated {patched} items with authentic Pokemon portraits and official icons.")
    return ''.join(result)
