"""v3.4: an icon that matches the name of each of the 319 learned moves (built-in WC3 icons the map already uses,
analysis/builtin_icons.txt), instead of one icon per type. build_v34 writes them into the Art= line of the 4 slot
abilities of each move ('A' + V/W/Y/Z + 2 base-36 digits of the move); docs/v3.4-move-icons.md lists them.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
KNOWN = os.path.join(WORK, 'analysis', 'builtin_icons.txt')
BTN = 'ReplaceableTextures\\CommandButtons\\BTN%s.blp'
SLOTS = 'VWYZ'
B36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# first match wins: (regex on the lower-case move name, icon)
RULES = [
    (r'swords dance|dragon dance|quiver dance|shell smash|work up|howl', 'Berserk'),
    (r'protect|detect|endure|king.s shield|baneful', 'DivineIntervention'),
    (r'recover|roost|rest\b|synthesis|moonlight|morning sun|soft-boiled|milk drink|slack off|heal pulse|wish', 'Heal'),
    (r'agility|rock polish|autotomize', 'BootsOfSpeed'),
    (r'calm mind|nasty plot|amnesia', 'Brilliance'),
    (r'bulk up|coil|growth', 'StrengthOfTheWild'),
    (r'reflect|light screen|barrier|cosmic power', 'SpellShieldAmulet'),
    (r'iron defense|harden|withdraw|defense curl|acid armor', 'HumanArmorUpThree'),
    (r'hypnosis|sleep powder|spore|sing|yawn|lovely kiss', 'Sleep'),
    (r'will-o-wisp', 'WispSplode'),
    (r'leech seed|leech life|drain|absorb', 'LifeDrain'),
    (r'taunt|torment', 'Taunt'),
    (r'\broar\b|noble roar', 'BattleRoar'),
    (r'growl|screech|scary face|leer|metal sound', 'HowlOfTerror'),
    (r'rain dance', 'Monsoon'),
    (r'sunny day', 'SunKey'),
    (r'sandstorm|sand attack|sand tomb', 'Dust'),
    (r'eruption|lava|magma', 'Volcano'),
    (r'fire blast|inferno|blast burn|overheat|burn up|mystical fire|incinerate', 'Incinerate'),
    (r'flamethrower|flame|flare|fire|ember|heat|burn|blaze|pyro|mind blown', 'BreathOfFire'),
    (r'hydro|surf|wave|whirlpool|muddy water|crabhammer|liquidation|dive|origin pulse', 'CrushingWave'),
    (r'water|aqua|bubble|scald|brine|razor shell|octazooka', 'SummonWaterElemental'),
    (r'blizzard|hail|sheer cold', 'Blizzard'),
    (r'freeze|frost|icy wind|powder snow|ice shard|icicle|avalanche|glaciate|ice beam|ice fang|ice punch|aurora',
     'FrostBolt'),
    (r'discharge|chain|parabolic', 'ChainLightning'),
    (r'thunder wave|stun spore|glare|nuzzle', 'Purge'),
    (r'thunder|bolt|zap|volt|spark|shock|electro|charge beam|wild charge|plasma', 'StormBolt'),
    (r'earthquake|magnitude|fissure|earth power|precipice', 'Earthquake'),
    (r'bulldoze|stomp|drill run|high horsepower|land', 'WarStomp'),
    (r'\bdig\b|mud|bone', 'Impale'),
    (r'stone edge|rock slide|rock tomb|ancient power|power gem|head smash|rock wrecker|diamond', 'Stone'),
    (r'rock|meteor beam|smack down', 'GolemStormBolt'),
    (r'hurricane|gust|twister|air cutter|air slash|whirlwind|defog|tailwind|bleakwind', 'Tornado'),
    (r'brave bird|wing|fly\b|sky attack|dragon ascent|aerial|peck|beak', 'WarEagle'),
    (r'quick attack|extreme speed|acrobatics|u-turn|flip turn|volt switch|accelerock|feint|first impression',
     'WindWalkOn'),
    (r'future sight|doom desire|meteor mash|draco meteor|spacial rend', 'Starfall'),
    (r'dream eater|psycho boost|psystrike|psyshock|psychic|expanding force|stored power|psychic noise', 'ManaBurn'),
    (r'confusion|psybeam|extrasensory|zen|psycho cut|psychic fangs|teleport', 'CrystalBall'),
    (r'shadow ball|hex|night shade|bitter malice|poltergeist|infernal parade', 'DeathCoil'),
    (r'shadow|phantom|astonish|lick|spite|curse|ominous', 'Possession'),
    (r'night slash|sucker punch|foul play|pursuit|assurance|throat chop|knock off|payback|false surrender', 'Ambush'),
    (r'dark pulse|snarl|fiery wrath|wicked', 'OrbOfDarkness'),
    (r'crunch|bite|fang|jaw', 'Devour'),
    (r'sludge|acid|gunk|smog|venoshock|belch', 'AcidBomb'),
    (r'poison|toxic|venom|cross poison|barb', 'EnvenomedSpear'),
    (r'aura sphere|focus blast|vacuum wave', 'OrbOfLightning'),
    (r'close combat|cross chop|brick break|karate|chop|hammer arm|superpower|sacred sword', 'Smash'),
    (r'punch|uppercut|fist|mach|jab|drain punch|dynamic', 'GauntletsOfOgrePower'),
    (r'kick|seismic|submission|low sweep|reversal|counter|revenge', 'Bash'),
    (r'iron|steel|metal|flash cannon|gyro|heavy slam|bullet|anchor|smart strike|make it rain', 'SteelMelee'),
    (r'outrage|dragon rush|dragon claw|dragon tail|breaking swipe|scale shot|dual chop', 'RedDragonDevour'),
    (r'dragon|roar of time|clanging', 'RedDragon'),
    (r'moonblast|moon', 'MoonStone'),
    (r'dazzling|fairy|disarming|sparkl|draining kiss|play rough|spirit break|charm|sweet', 'StarWand'),
    (r'leaf storm|petal|frenzy plant|solar', 'Tranquility'),
    (r'vine|grass knot|power whip|wood hammer|horn leech|bullet seed|seed|razor leaf|leaf|magical leaf|trailblaze',
     'EntanglingRoots'),
    (r'energy ball|giga drain|grass|flower', 'NatureTouchGrow'),
    (r'bug buzz|signal beam|lunge|pounce', 'CarrionScarabs'),
    (r'silver wind|struggle bug|infestation', 'LocustSwarm'),
    (r'megahorn|horn', 'Impale'),
    (r'pin missile|twineedle|fell stinger', 'QuillSpray'),
    (r'x-scissor|fury cutter|attack order', 'VorpalBlades'),
    (r'explosion|self-destruct|misty explosion', 'SelfDestructOn'),
    (r'swift', 'StarWand'),
    (r'hyper beam|giga impact|tri attack|hyper voice|boomburst|judgment', 'Brilliance'),
    (r'body slam|body press|take down|double.edge|headbutt|tackle|rapid spin|slam|crush|pound|raging bull|meteor assault', 'Smash'),
    (r'slash|scratch|fury|claw|cut', 'ClawsOfAttack'),
]
TYPE_ICON = {'Fire': 'Fire', 'Water': 'CrushingWave', 'Ice': 'FrostBolt', 'Electric': 'ChainLightning',
             'Grass': 'EntanglingRoots', 'Ground': 'Earthquake', 'Rock': 'GolemStormBolt', 'Flying': 'Tornado',
             'Psychic': 'ManaBurn', 'Ghost': 'DeathCoil', 'Dark': 'ShadowStrike', 'Poison': 'AcidBomb',
             'Fighting': 'GauntletsOfOgrePower', 'Steel': 'SteelMelee', 'Dragon': 'RedDragon', 'Fairy': 'MoonStone',
             'Normal': 'Bash', 'Bug': 'CarrionScarabs'}


def known_icons():
    return {ln.strip().split('\\')[-1][3:-4] for ln in open(KNOWN, encoding='utf-8') if ln.strip()}


def plan(script):
    """[(move index, name, type, icon name, how)] for the learned moves of the script (Mv_Label)"""
    known = known_icons()
    bad = sorted({ic for _r, ic in RULES if ic not in known} | {ic for ic in TYPE_ICON.values() if ic not in known})
    if bad:
        raise ValueError('icons not known to exist: %s' % bad)
    out = []
    for i, lab in re.findall(r'set Mv_Label\[(\d+)\] = "([^"]*)"', script):
        m = re.match(r'(.*?) \((\w+)', lab)
        name, ty = (m.group(1), m.group(2)) if m else (lab, '')
        icon, how = None, 'type'
        for rx, ic in RULES:
            if re.search(rx, name.lower()):
                icon, how = ic, 'name'
                break
        if icon is None:
            icon = TYPE_ICON.get(ty, 'Bash')
        out.append((int(i), name, ty, icon, how))
    return out


def ability_ids(m):
    return ['A' + sl + B36[m // 36] + B36[m % 36] for sl in SLOTS]


def patch_strings(text, rows):
    """set the Art= line of the move abilities (sections [AV00] ..) in CampaignAbilityStrings.txt"""
    parts = []
    pos = 0
    targets = {}
    for m, _n, _t, icon, _how in rows:
        for aid in ability_ids(m):
            targets[aid] = BTN % icon
    changed = 0
    for mt in re.finditer(r'(?m)^\[(\w{4})\]\r?$', text):
        aid = mt.group(1)
        if aid not in targets:
            continue
        start = mt.end()
        nxt = text.find('\n[', start)
        end = len(text) if nxt < 0 else nxt
        sec = text[start:end]
        new = re.sub(r'(?m)^Art=[^\r\n]*', 'Art=' + targets[aid].replace('\\', '\\\\'), sec, count=1)
        if new != sec:
            parts.append(text[pos:start])
            parts.append(new)
            pos = end
            changed += 1
    parts.append(text[pos:])
    return ''.join(parts), changed


def write_doc(rows, path):
    lines = ['# v3.4: icon của 319 move học được', '',
             'Icon chọn theo tên chiêu (cột "Theo" = tên); không khớp từ khóa nào thì dùng icon theo hệ (cột "Theo" = hệ).',
             'Chỉ dùng icon có sẵn của Warcraft III mà map đã dùng (`analysis/builtin_icons.txt`).', '',
             '| # | Move | Hệ | Icon | Theo |', '|---|---|---|---|---|']
    for m, name, ty, icon, how in rows:
        lines.append('| %d | %s | %s | BTN%s | %s |' % (m, name, ty, icon, 'tên' if how == 'name' else 'hệ'))
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
