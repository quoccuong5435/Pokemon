"""Hidden Power of the FINAL forms (Mega, form, Gigantamax, final hero form): one awakening quest slot per form.

Before: every final form of a player shared quest slot 58, so finishing the quest with one made all of them awakened.
Now `Form_QuestIdx` returns a slot of the form itself (59 and up); Legends keep their own index 1..57.

Slots, in this order: Megas by Mega index, form ids 1.., Gigantamax skins, final hero types (Mega_HT key 998).
`PAX_Leg_QKey(pid, idx) = 1000 + pid * 256 + idx` (was * 64: only 64 slots per player).
`PAX_Leg_Count()` stays 58: it also sizes the paged Legend dialog. `PAX_Quest_Last()` is the last slot, used by the
"unlock everything" command.

Usage from a build script:  script = hidden_power.patch(script)   (after form_expansion.patch_all, which defines the forms)
"""
import re

FIRST_SLOT = 59
LAST_ALLOWED = 255  # PAX_Leg_QKey allows idx 0..255 per player


def assign_slots(final_keys):
    """{key: slot}, 59, 60, ... in the order given. Keys look like mega:<index>, form:<id>, gmax:<skin id>, type:<unit id>."""
    if len(final_keys) > LAST_ALLOWED - FIRST_SLOT + 1:
        raise ValueError("[hidden_power] %d final forms do not fit in slots %d..%d" % (len(final_keys), FIRST_SLOT, LAST_ALLOWED))
    return {key: FIRST_SLOT + i for i, key in enumerate(final_keys)}


def _body(script, header):
    i = script.find(header)
    if i < 0:
        raise ValueError("[hidden_power] %r not found" % header)
    return script[i:script.index("endfunction", i)]


def _form_names(script):
    """{form id >= 1: name}, from the branches of PAX_Form_Appearance (`set name = "..."`)."""
    body = _body(script, "function PAX_Form_Appearance")
    names = {}
    for m in re.finditer(r'(?:if|elseif) formId == (\d+) then\n(.*?)(?=\n    elseif formId|\n    endif)', body, re.S):
        nm = re.search(r'set name = "([^"]*)"', m.group(2))
        if nm and int(m.group(1)) >= 1:
            names[int(m.group(1))] = nm.group(1)
    return names


def collect_final_keys(script):
    """The final forms the script defines, in slot order."""
    mega_n = max(int(n) for n in re.findall(r"set Mega_N = (\d+)", script))
    keys = ["mega:%d" % i for i in range(mega_n)]
    keys += ["form:%d" % i for i in sorted(_form_names(script))]
    keys += ["gmax:" + s for s in sorted(set(re.findall(r"return '(hG\d\d)'", _body(script, "function Gmax_SkinId"))))]
    keys += ["type:" + t for t in sorted(set(re.findall(r"SaveBoolean\(Mega_HT, '(\w{4})', 998, true\)", script)))]
    return keys


def _jstr(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _slot_names_jass(script, slots):
    mega = sorted(s for k, s in slots.items() if k.startswith("mega:"))
    lines = ["function Form_SlotName takes integer idx returns string",
             "    if idx >= %d and idx <= %d then" % (mega[0], mega[-1]),
             "        return Mega_Name[idx - %d]" % mega[0],
             "    endif"]
    names = _form_names(script)
    for key, slot in slots.items():
        kind, ident = key.split(":", 1)
        if kind == "form":
            lines += ["    if idx == %d then" % slot, '        return "%s"' % _jstr(names[int(ident)]), "    endif"]
        elif kind in ("gmax", "type"):
            lines += ["    if idx == %d then" % slot, "        return GetObjectName('%s')" % ident, "    endif"]
    lines += ['    return "Final Form"', "endfunction\n"]
    return "\n".join(lines)


def _final_slot_jass(slots):
    mega = sorted(s for k, s in slots.items() if k.startswith("mega:"))
    forms = sorted((int(k.split(":")[1]), s) for k, s in slots.items() if k.startswith("form:"))
    if [s for _i, s in forms] != list(range(forms[0][1], forms[0][1] + len(forms))) or \
            [i for i, _s in forms] != list(range(1, len(forms) + 1)):
        raise ValueError("[hidden_power] form ids / slots are not contiguous from 1")
    lines = [
        "// the quest slot of the final form that unit u is in right now (same order as Form_IsFinalHP); 58 = unknown form",
        "function Form_FinalSlot takes unit u returns integer",
        "    local integer h = GetHandleId(u)",
        "    local integer t = GetUnitTypeId(u)",
        "    local integer mi = LoadInteger(Mega_HT, h, 0) - 1",
        "    local integer formId = LoadInteger(PAX_Leg_HT, h, 140)",
        "    local integer skin = 0",
        "    if mi >= 0 and mi < %d then" % len(mega),
        "        return %d + mi" % mega[0],
        "    endif",
        "    if formId >= 1 and formId <= %d then" % len(forms),
        "        return %d + formId - 1" % forms[0][1],
        "    endif",
        "    if HaveSavedReal(Fx_HT, h, 87) and Mega_Time < LoadReal(Fx_HT, h, 87) then",
        "        set skin = Gmax_SkinId(t)",
    ]
    for kind, var in (("gmax", "skin"), ("type", "t")):
        items = [(k.split(":", 1)[1], s) for k, s in slots.items() if k.startswith(kind + ":")]
        if kind == "type":
            lines += ["    endif", "    if LoadBoolean(Mega_HT, t, 998) then"]
        for n, (ident, slot) in enumerate(items):
            lines += ["        %s %s == '%s' then" % ("if" if n == 0 else "elseif", var, ident), "            return %d" % slot]
        lines.append("        endif")
    lines += ["    endif", "    return 58", "endfunction\n"]
    return "\n".join(lines)


TANK_BULK = 105  # (Def + SpDef) / 2 at or above this: tank (the same 105 the Melee / Ranged rule uses)
ROLE_CODE = {"tank": 1, "caster": 2, "striker": 3, "drain": 4}


def main_stat(stats):
    """"str" when Attack >= Sp.Atk, else "int". stats = [hp, atk, def, spa, spd, spe]."""
    return "str" if stats[1] >= stats[3] else "int"


def role_for(stats, main):
    """tank if bulk (Def + SpDef) / 2 >= 105, else striker for a "str" main stat, else caster. Never drain."""
    if (stats[2] + stats[4]) / 2.0 >= TANK_BULK:
        return "tank"
    return "striker" if main == "str" else "caster"


def _legend_roles():
    import legend_expansion_data
    return {lg["idx"]: lg["role"] for lg in legend_expansion_data.NEW_LEGENDS}


LEGEND_ROLES = _legend_roles()  # idx 33..57 (the 25 later Legends), as assigned in legend_expansion_data.py


def _slug_of(key, form_stats):
    """PokeAPI slug of a final-form key (mega:i, form:id, gmax:skin, type:unit id), or None."""
    import form_expansion
    import form_pokeapi
    kind, ident = key.split(":", 1)
    if kind == "mega":
        i = int(ident)
        return form_pokeapi.OLD_MEGA_SLUGS.get(i) if i < 44 else form_stats["mega_keys"].get(i)
    if kind == "form":
        return form_pokeapi.FORM_ID_SLUG.get(int(ident))
    if kind == "gmax":
        return form_expansion.GMAX_BASES[int(ident[2:])][0]
    hero_to_key = {hid: k for k, hid in form_expansion.EXISTING_FORM_HEROES.items()}
    hero_to_key.update(form_stats["form_heroes"])
    return hero_to_key.get(ident)


def build_roles(script, form_stats):
    """({idx: role} for the 25 later Legends and every final-form slot, [keys without PokeAPI stats])."""
    import form_pokeapi
    slots = assign_slots(collect_final_keys(script))
    roles = dict(LEGEND_ROLES)
    missing = []
    for key, slot in slots.items():
        rec = form_pokeapi.pokemon(_slug_of(key, form_stats) or "")
        if rec is None:
            missing.append(key)
        else:
            roles[slot] = role_for(rec["stats"], main_stat(rec["stats"]))
    return roles, missing


def _once(script, old, new, what):
    if script.count(old) != 1:
        raise ValueError("[hidden_power] anchor %r found %d times (expected 1)" % (what, script.count(old)))
    return script.replace(old, new, 1)


def patch(script):
    slots = assign_slots(collect_final_keys(script))
    script = _once(script, "    return 1000 + pid * 64 + idx", "    return 1000 + pid * 256 + idx", "PAX_Leg_QKey")

    last = max(slots.values())
    early = _slot_names_jass(script, slots) + "\nfunction PAX_Quest_Last takes nothing returns integer\n    return %d\nendfunction\n\n" % last
    script = _once(script, "function PAX_Leg_Name takes integer idx returns string",
                   early + "function PAX_Leg_Name takes integer idx returns string", "PAX_Leg_Name header")
    script = _once(script, '        return "Final Form (Hidden Power)"\n    endif',
                   '        return "Final Form (Hidden Power)"\n    elseif idx >= %d then\n        return Form_SlotName(idx)\n    endif' % FIRST_SLOT,
                   "PAX_Leg_Name slot 58")

    script = _once(script, "function Form_QuestIdx takes unit u returns integer",
                   _final_slot_jass(slots) + "\nfunction Form_QuestIdx takes unit u returns integer", "Form_QuestIdx header")
    script = _once(script, "    if idx > 0 then\n        return idx\n    endif\n    return 58\nendfunction",
                   "    if idx > 0 then\n        return idx\n    endif\n    return Form_FinalSlot(u)\nendfunction", "Form_QuestIdx tail")

    script = _once(script, "        exitwhen idx > PAX_Leg_Count()\n        set qk = PAX_Leg_QKey(pid, idx)\n        call SaveInteger(PAX_Leg_HT, qk, 0, 4)",
                   "        exitwhen idx > PAX_Quest_Last()\n        set qk = PAX_Leg_QKey(pid, idx)\n        call SaveInteger(PAX_Leg_HT, qk, 0, 4)",
                   "PAX_Leg_UnlockCmd loop")
    return script
