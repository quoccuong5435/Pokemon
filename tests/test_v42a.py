"""Tests for Pokemon Arena v4.2a: Player-ID ownership lock removed while keeping 60s safe-on-death rules."""
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, os.path.join(WORK, "tools", "v412"))

import build_v42a  # noqa: E402


def test_player_id_lock_removed_and_safe_on_death_preserved():
    _, files, script = build_v42a.build_data()
    s = script.replace("\r\n", "\n")

    # 1. Player-ID ownership rejection MUST be completely gone
    assert "This item belongs to Player" not in s
    assert "LoadInteger(PAX_Leg_HT, itH, 210) == 1 and LoadInteger(PAX_Leg_HT, itH, 211) != ownerPid" not in s

    # 2. Safe-on-death rules MUST remain intact
    assert "function PAX_IsInstantSoulboundItem" in s
    assert "return itemTypeId == 'ofir' or itemTypeId == 'ocor'" in s
    assert "if id == 'oli2' or id == 'tgrh' then" in s
    assert "if sbHoldSec >= 60 then" in s
    assert "call PAX_SoulboundTick()" in s
    assert "if PAX_IsSoulboundProtectedItem(dropId) and LoadInteger(PAX_Leg_HT, dropH, 210) == 0 then" in s
    assert s.count("call PAX_Soulbound_BindNow(dropIt, pid)") == 2
    assert "call PAX_Soulbound_BindNow(newIt, pid)" in s

    # 3. Anti-crash creep caps + Ai_Unit leak fix
    assert "function Wild_CountTotalAlive" in s
    assert "local integer capRemain = 6 - Wild_CampAlive[c]" in s
    assert "Wild_CountTotalAlive() >= 260" in s
    assert "if Wild_CampSize[c] > 6 then" in s
    assert "elseif Wild_CampAlive[c] < 6 and Wild_Time - LoadReal(Mega_HT, c + 500, 1) >= 90.0 and LoadInteger(Mega_HT, c + 500, 2) < 1 then" in s
    assert "set weak = null" in s

    # 4. Version updated cleanly in w3i & script
    assert "v4.2a" in s
    assert b"Pokemon Arena v4.2a" in files["war3map.w3i"]
