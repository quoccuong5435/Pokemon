"""Brute-force names of v1.8's unknown files from Pokemon/move/item names and naming patterns (read-only)."""
import re
import sys

sys.path.insert(0, sys.argv[1])
import assets  # noqa: E402
import mpq  # noqa: E402

a = mpq.MPQ(sys.argv[2])
pkl = mpq.MPQ(sys.argv[3])
known_names = mpq.discover_names(a)
known = {a.find_hash(n) for n in known_names}
unknown = {p for p, e in enumerate(a.hash_table) if e[4] < mpq.HASH_DELETED and p not in known}
print('unknown before', len(unknown))

words = set()
for n in known_names:
    base = n.split('\\')[-1].rsplit('.', 1)[0]
    words.add(base)
    for w in re.split(r'[ _\-()]+', base):
        if w:
            words.add(w)
for n in assets.pkl_species_index(pkl):
    words.add(n.title())
    words.add(n)
txt = ''
for f in ('Units\\CampaignAbilityStrings.txt', 'Units\\ItemFunc.txt'):
    txt += a.read(f).decode('utf-8', 'replace')
for m in re.finditer(r'^Name=(.+)$', txt, re.M):
    words.add(m.group(1).strip())
MOVES = """Absorb Acid Acid Armor Aerial Ace Agility Air Slash Amnesia Ancient Power Aqua Jet Aqua Tail Aura Sphere
Aurora Beam Barrier Bite Blizzard Body Slam Bone Club Bonemerang Bone Rush Brick Break Bubble Bubble Beam Bulk Up
Bullet Punch Bullet Seed Calm Mind Charge Beam Close Combat Confusion Confuse Ray Cosmic Power Crabhammer Cross Chop
Crunch Cut Dark Pulse Defense Curl Dig Disable Discharge Dizzy Punch Double Edge Double Kick Double Slap Draco Meteor
Dragon Claw Dragon Dance Dragon Pulse Dragon Rage Dragon Rush Drain Punch Dream Eater Drill Peck Dynamic Punch
Earth Power Earthquake Egg Bomb Ember Energy Ball Explosion Extreme Speed Fire Blast Fire Fang Fire Punch Fissure
Flamethrower Flame Wheel Flare Blitz Flash Cannon Fly Focus Blast Focus Punch Frenzy Plant Future Sight Giga Drain
Giga Impact Glare Gunk Shot Gust Harden Haze Headbutt Heat Wave Hidden Power High Jump Kick Horn Attack Horn Drill
Hurricane Hydro Cannon Hydro Pump Hyper Beam Hyper Fang Hypnosis Ice Beam Ice Fang Ice Punch Ice Shard Icicle Spear
Iron Defense Iron Head Iron Tail Karate Chop Leaf Blade Leaf Storm Leech Life Leech Seed Leer Lick Light Screen
Low Kick Mach Punch Magical Leaf Magnet Bomb Mega Drain Mega Kick Mega Punch Megahorn Metal Claw Meteor Mash
Mirror Coat Mist Moonblast Mud Shot Mud Slap Night Shade Night Slash Outrage Petal Dance Pin Missile Poison Fang
Poison Jab Poison Sting Pound Power Gem Power Whip Psybeam Psychic Psycho Cut Psywave Quick Attack Rage Razor Leaf
Razor Wind Recover Reflect Rest Roar Rock Blast Rock Slide Rock Smash Rock Throw Rock Tomb Rolling Kick Sand Attack
Sand Tomb Sandstorm Scratch Screech Seed Bomb Seismic Toss Self Destruct Shadow Ball Shadow Claw Shadow Punch
Sharpen Signal Beam Skull Bash Sky Attack Slam Slash Sleep Powder Sludge Sludge Bomb Smog Snore Solar Beam Spark
Spore Steel Wing Stomp Stone Edge Strength String Shot Stun Spore Submission Sucker Punch Super Fang Superpower Surf
Swift Swords Dance Tackle Tail Whip Take Down Teleport Thrash Thunder Thunder Fang Thunder Punch Thunder Shock
Thunder Wave Thunderbolt Toxic Transform Tri Attack Twineedle U-turn Vacuum Wave Vice Grip Vine Whip Water Gun
Water Pulse Waterfall Whirlpool Wing Attack Withdraw Wrap X-Scissor Zap Cannon Zen Headbutt Volt Tackle
Water Fall Twi Needle Shock Wave Fire Spin Hydro Canon Flash Canon Thunder Bolt Flame Thrower Ice Shard"""
_m = MOVES.replace('\n', ' ').split(' ')
for i in range(len(_m)):
    for j in range(i + 1, min(i + 4, len(_m) + 1)):
        words.add(' '.join(_m[i:j]))
for i in range(0, 500):
    words.update({'%d' % i, '%03d' % i})
words.update({'Mix%d' % i for i in range(30)})

pats = ['%s.blp', '%s.mdx', '%s.mdl', 'BTN%s (64 x 64).blp', 'BTN%s.blp', 'PAS%s (64 x 64).blp',
        'ReplaceableTextures\\CommandButtonsDisabled\\DISBTN%s (64 x 64).blp',
        'ReplaceableTextures\\CommandButtonsDisabled\\DISBTN%s.blp',
        'ReplaceableTextures\\CommandButtonsDisabled\\DISPAS%s (64 x 64).blp',
        'ReplaceableTextures\\CommandButtons\\BTN%s.blp', 'ReplaceableTextures\\PassiveButtons\\PASBTN%s.blp',
        'war3mapImported\\%s.blp', 'war3mapImported\\%s.mdx', '%s_portrait.mdx', '%s_Portrait.mdx', '%s_Texture.blp',
        '%s.tga', 'Textures\\%s.blp', '%s.TTF', '%s.ttf', 'Fonts\\%s.ttf']
hits = {}
for w in words:
    for p in pats:
        name = p % w
        hi = a.find_hash(name)
        if hi in unknown and hi not in hits:
            hits[hi] = name
print('found', len(hits))
for hi, n in sorted(hits.items()):
    print(hi, n)
print('still unknown', sorted(unknown - set(hits)))
