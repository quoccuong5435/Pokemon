import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, "tools"))
sys.path.insert(0, os.path.join(WORK, "tools", "v412"))

import boss_isolation
import build_v42b


def test_boss_isolation_patch():
    base, files, dels, stats, script, w3u, abil, strings, unlock = build_v42b.build_data(optimize_assets=False)
    s = script.replace("\r\n", "\n")

    # 1. SetUnitAcquireRange 0.0 in Leg_Spawn and PAX_Boss_Register
    assert "call SetUnitAcquireRange(lg, 0.0)" in s
    assert s.count("call SetUnitAcquireRange(lg, 0.0)") == 2

    # 2. Leg_OnDamage Under-100 player protection & real damage retaliation
    assert "Only level 100 Pokemon can awaken" in s
    assert "call IssueTargetOrder(t, \"attack\", src)" in s
    assert "call IssueImmediateOrder(src, \"stop\")" in s

    # 3. Ai_Unit ignores heroes below Lv 100
    assert "if not isLeg or BossIso_PlayerLevel(GetOwningPlayer(cand)) >= Leg_MinLevel then" in s
    assert "if isLeg and t != null and BossIso_PlayerLevel(GetOwningPlayer(t)) < Leg_MinLevel then" in s

    # 3b. JASS: a function must be declared above its caller; BlzGetEventDamage does not exist (4.3 failed to load)
    ai = s.index("\nfunction Ai_Unit takes")
    assert s.index("\nfunction BossIso_IsLegend takes") < ai and s.index("\nfunction BossIso_PlayerLevel takes") < ai
    body = s[ai:s.index("\nendfunction", ai)]
    assert "Leg_IsLegend(" not in body.replace("BossIso_IsLegend(", "") and "Leg_PlayerLevel(" not in body.replace("BossIso_PlayerLevel(", "")
    assert "BlzGetEventDamage()" not in s

    # 4. Leash radius 700.0 and Warp 1200.0
    assert "elseif dist > 700.0 then" in s
    assert "if dist > 1200.0 then" in s
    assert "dist > 2500.0" not in s

    # 5. Dynamic pacing: 240s initial, 90s after 30 min (Wild_Time >= 1800.0)
    assert "real Leg_Interval = 240.0" in s
    assert "real Leg_Next = 240.0" in s
    assert "if Wild_Time >= 1800.0 then" in s
    assert "LEGENDARY FRENZY!" in s
