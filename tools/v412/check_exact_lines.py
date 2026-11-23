import sys, os
sys.path.insert(0, 'tools')
import mpq

base = mpq.MPQ('../Pokemon Arena v4.1.2-ver2c.w3x')
raw = base.read('scripts\\war3map.j').decode('utf-8').replace('\r\r\n', '\r\n').replace('\r\n', '\n')

lines = raw.split('\n')
for idx, l in enumerate(lines):
    if any(k in l for k in ['[SOLO]', '[DEATHMATCH', '[CHAOS', '[ALTAR', '[WANTED', '[TREASURE', '[GIANT MAGIKARP', '[IT\'S A TRAP', '[RED GYARADOS', '[RUNE]', '[STAGE', '[RITUAL]', 'Awakening Ritual was disrupted', '[AWAKENING COMPLETE]', '[LEAGUE', 'Title [Champion]', 'Duel:', '[FIRST BLOOD', '[SHUTDOWN', '[GOD CHU', '[ASH\'S CAP']):
        print(f"{idx+1}: {l.strip()[:130]}")
