"""Hidden Ability (Ability Patch item, 10,000 gold) for the NEW heroes: the 205 Gen 1-4 species and the 52 form heroes.

hidden_ability.py reads the table of the old heroes (AbilityPatch_HT '<unit id>' key 1 = name, 2 = text, 3 = Ability number)
when the build starts; the new heroes are created later in the build (gen14_expansion, form_expansion), so this module writes
the same three keys for them, after those steps:
  key 1  the Hidden Ability's name as the map spells it
  key 2  its English description (Ab_Info of the Ability number)
  key 3  the Ability number, ONLY when some code runs that Ability (otherwise the Ability Patch refunds, as for the old heroes)

Usage:  entries = collect_entries(script, {hero id: PokeAPI hidden-ability slug or None});  script = patch(script, entries)
Megas and Gigantamax skins are never passed in (they use their own Ability, GEMINI.md rule kept).
"""
import re

import ability_names
import hidden_ability

CHUNK = 100  # heroes per generated function (3 lines each), like AbilityPatch_InitPart_*

_INFO = re.compile(r'set Ab_Info\[(\d+)\] = "((?:[^"\\]|\\.)*)"')


def collect_entries(script, hero_ids):
    """{hero id: Ability name as the map spells it} for the heroes whose hidden Ability the map has."""
    index = ability_names.ability_index(script)
    name_of = {number: name for name, number in index.items()}
    entries = {}
    for hero, slug in hero_ids.items():
        if not slug:
            continue
        number = ability_names.first_known(index, [slug])
        if number is not None:
            entries[hero] = name_of[number]
    return entries


def _once(script, anchor):
    if script.count(anchor) != 1:
        raise ValueError("[hidden_ability_new] anchor found %d times (expected 1): %r" % (script.count(anchor), anchor[:60]))


def patch(script, entries):
    """Adds HiddenAb_InitNew (called right after HiddenAb_InitIdx) that stores the entries."""
    if not entries:
        return script
    call_anchor = "    call HiddenAb_InitIdx()\n"
    func_anchor = "function AbilityPatch_Init takes nothing returns nothing"
    _once(script, call_anchor)
    _once(script, func_anchor)

    index = ability_names.ability_index(script)
    info = {int(n): text for n, text in _INFO.findall(script)}  # raw JASS string contents, already escaped
    used = hidden_ability.used_ability_numbers(script)

    heroes = sorted(entries)
    chunks = [heroes[i:i + CHUNK] for i in range(0, len(heroes), CHUNK)]
    funcs = []
    for ci, chunk in enumerate(chunks, 1):
        lines = ["function HiddenAb_InitNew%d takes nothing returns nothing" % ci]
        for hero in chunk:
            name = entries[hero]
            number = index[name]
            lines.append("    call SaveStr(AbilityPatch_HT, '%s', 1, \"%s\")" % (hero, name))
            lines.append("    call SaveStr(AbilityPatch_HT, '%s', 2, \"%s\")" % (hero, info.get(number, "")))
            if number in used:
                lines.append("    call SaveInteger(AbilityPatch_HT, '%s', 3, %d)" % (hero, number))
        lines.append("endfunction\n")
        funcs.append("\n".join(lines))
    wrapper = ["// Hidden Abilities of the new Gen 1-4 and form heroes (hidden_ability_new.py)",
               "function HiddenAb_InitNew takes nothing returns nothing"]
    wrapper += ["    call HiddenAb_InitNew%d()" % ci for ci in range(1, len(chunks) + 1)]
    wrapper.append("endfunction\n")
    block = "\n".join(funcs) + "\n" + "\n".join(wrapper) + "\n"

    script = script.replace(func_anchor, block + func_anchor, 1)
    return script.replace(call_anchor, call_anchor + "    call HiddenAb_InitNew()\n", 1)
