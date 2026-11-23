"""PokeAPI ability slugs <-> the ability numbers of the map script.

The map knows an Ability by its number and its name: `set Ab_Name[<number>] = "<name>"` (ability_rw.py adds the reworked ones
after the old ones, so the LAST definition of a name wins, exactly as hidden_ability.ability_table reads it).
"""
import re

_SMALL_WORDS = {"of", "the"}


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def slug_to_name(slug):
    """'quark-drive' -> 'Quark Drive', 'power-of-alchemy' -> 'Power of Alchemy'."""
    words = slug.split("-")
    return " ".join(w if (i and w in _SMALL_WORDS) else w.capitalize() for i, w in enumerate(words))


def ability_index(script):
    """{ability name: number} from every `set Ab_Name[n] = "name"` line of the script."""
    index = {}
    for m in re.finditer(r'set Ab_Name\[(\d+)\] = "(.*?)"', script):
        index[m.group(2)] = int(m.group(1))
    return index


def first_known(index, slugs):
    """The number of the first slug (PokeAPI order) the map has an Ability for, ignoring case and punctuation; else None."""
    by_norm = {_norm(name): number for name, number in index.items()}
    for slug in slugs:
        number = by_norm.get(_norm(slug))
        if number is not None:
            return number
    return None
