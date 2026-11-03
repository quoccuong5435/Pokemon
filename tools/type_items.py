"""Type items of the Poke Super Marts (n00N, n00Q): item id -> type word. Only a Pokemon whose type name (the unit name, e.g.
'Fire&Flying Pokemon') contains the word may buy it; the price is refunded otherwise."""
TYPE_ITEMS = (('I00Q', 'Fire'), ('I00R', 'Grass'), ('I00S', 'Water'), ('I00T', 'Electric'), ('I00U', 'Bug'),
              ('I00V', 'Poison'), ('I00W', 'Ice'), ('I00X', 'Dragon'), ('I00Y', 'Flying'), ('I00Z', 'Normal'),
              ('I010', 'Psychic'), ('I011', 'Fighting'), ('I012', 'Rock'), ('I01X', 'Steel'), ('I01Y', 'Dark'),
              ('I020', 'Ghost'))
COST = 3000  # every type item costs 3000 gold in the v1.8 item data
# v3.4: items of the two types the Poke Marts have no item for; only gym Pokemon of that type hold them (id, type word, name, icon)
EXTRA_ITEMS = (('ITGD', 'Ground', 'Soft Sand', 'BTNPkmnGround'), ('ITFY', 'Fairy', 'Pixie Plate', 'BTNPkmnFairy'))


def item_for_type(word):
    """Item id a gym Pokemon of this type holds ('' when none)."""
    for item, w in TYPE_ITEMS:
        if w.lower() == word.lower():
            return item
    for item, w, _n, _i in EXTRA_ITEMS:
        if w.lower() == word.lower():
            return item
    return ''
