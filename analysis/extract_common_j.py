"""Extract common.j and Blizzard.j from the map that embeds them, into analysis/jass_ref/ (reference for pjass)."""
import os
import sys

sys.path.insert(0, 'tools')
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[1])
os.makedirs(sys.argv[2], exist_ok=True)
for name, out in (('common.j', 'common.j'), ('Blizzard.j', 'Blizzard.j')):
    data = a.read(name)
    open(os.path.join(sys.argv[2], out), 'wb').write(data)
    t = data.decode('latin-1')
    print(name, len(data), 'bytes', t.count('native '), 'natives;',
          {k: (k in t) for k in ('UnitAlive', 'BlzGetEventDamageTarget', 'BlzGetEventIsAttack', 'BlzGetUnitMaxHP',
                                 'EVENT_PLAYER_HERO_REVIVE_FINISH', 'BlzSetEventDamage', 'GetEventDamage')})
