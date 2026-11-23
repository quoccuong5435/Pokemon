import json, re, sys, collections
WORK, OUT = sys.argv[1], sys.argv[2]
ls = json.load(open(WORK + "/tools/learnsets.json", encoding="utf-8"))
sp = ls["species"]; mv = ls["moves"]
html = open(WORK + "/docs/so-tay-v4.2a.html", encoding="utf-8").read()
roster = json.loads(re.search(r"const ROSTER = (\[.*?\]);\n", html, re.S).group(1))
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
byname = {}
for k, v in sp.items():
    byname[norm(v["name"])] = k; byname[norm(k)] = k
# base stats [hp, atk, def, spa, spd, spe] for species missing from learnsets.json (official base stats)
MANUAL = {
 "Azelf": [75,125,70,125,70,115], "Cresselia": [120,70,110,75,120,85], "Diancie": [50,100,150,100,150,50],
 "Eternatus": [140,85,95,145,95,130], "Genesect": [71,120,95,120,95,99], "Heatran": [91,90,106,130,106,77],
 "Hoopa": [80,110,60,150,130,70], "Kyurem": [125,130,90,130,90,95], "Latias & Latios": [80,85,85,120,120,110],
 "Lunala": [137,113,89,137,107,97], "Magearna": [80,95,115,130,115,65], "Marshadow": [90,125,80,90,90,125],
 "Mesprit": [80,105,105,105,105,80], "Necrozma": [97,107,101,127,89,79], "Regice": [80,50,100,100,200,50],
 "Registeel": [80,75,150,75,150,50], "Reshiram": [100,120,100,150,120,90], "Solgaleo": [137,137,107,113,89,97],
 "Uxie": [75,75,130,75,130,95], "Victini": [100,100,100,100,100,100], "Volcanion": [80,110,120,130,90,70],
 "Xerneas": [126,131,95,131,98,99], "Yveltal": [126,131,95,131,98,99], "Zacian": [92,120,115,80,115,138],
 "Zekrom": [100,150,120,120,100,90], "Zygarde": [108,100,121,81,95,95], "Meganium": [80,82,100,83,100,80],
 "Porygon2": [85,80,90,105,95,60],
}
def move_mix(k):
    phys = spec = 0
    for lv, m in sp[k].get("moves", []):
        c = mv.get(m, {}).get("class")
        if c == "physical": phys += 1
        elif c == "special": spec += 1
    return phys, spec
out = []
for r in roster:
    k = byname.get(norm(r["name"]))
    if k:
        st = sp[k]["stats"]; phys, spec = move_mix(k); src = "pokeapi"
    else:
        st = MANUAL[r["name"]]; phys = spec = 0; src = "manual"
    hp, atk, df, spa, sdf, spe = st
    gap = spa - atk
    nm = phys + spec
    mshift = round(40 * (spec / nm - 0.5)) if nm >= 4 else 0   # move mix shifts at most +-20
    score = gap + mshift
    if score >= 20: cls = "R"
    elif score <= -20: cls = "M"
    else: cls = "H"
    clash = (cls == "R" and r["stat"] == "STR") or (cls == "M" and r["stat"] == "INT")
    if clash: cls = "H"   # step 4: stay consistent with the map's main stat (damage scaling)
    bulk = (df + sdf) / 2
    if cls == "M": rng = 150
    elif cls == "H": rng = 300
    else:
        if spa >= 120 and bulk < 85: rng = 600
        elif bulk >= 105: rng = 450
        else: rng = 500
    out.append(dict(id=r["id"], name=r["name"], atk=atk, spa=spa, df=df, sdf=sdf, spe=spe, phys=phys, spec=spec,
                    gap=gap, mshift=mshift, score=score, clash=clash, cls=cls, rng=rng, cur=r["range"], band=r["band"], stat=r["stat"], src=src))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
c = collections.Counter(o["cls"] for o in out); print("classes", dict(c))
cur_cls = lambda o: "R" if o["cur"] >= 400 else ("H" if o["cur"] >= 250 else "M")
conf = collections.Counter((cur_cls(o), o["cls"]) for o in out); print("current->new", dict(conf))
same = sum(1 for o in out if cur_cls(o) == o["cls"]); print("same class as now:", same)
ms = collections.Counter((o["stat"], o["cls"]) for o in out); print("mainstat x class", dict(ms))
print("rng dist", dict(collections.Counter(o["rng"] for o in out)))
print("moved by moves (class changed by mshift):", sum(1 for o in out if (("R" if o["gap"]>=20 else "M" if o["gap"]<=-20 else "H") != o["cls"])))
for nm in ["Charizard","Gengar","Alakazam","Machamp","Lucario","Pikachu","Mewtwo","Rayquaza","Garchomp","Blissey","Snorlax","Gyarados","Dragonite","Kyogre","Groudon","Pidgeot","Blastoise","Venusaur","Mew","Arceus","Lunala","Zacian","Tyranitar","Metagross","Greninja","Cloyster","Starmie","Magikarp","Ditto","Wobbuffet","Shedinja","Gardevoir","Gallade","Scizor"]:
    for o in out:
        if o["name"] == nm:
            print(f'{nm:10} atk{o["atk"]:4} spa{o["spa"]:4} moves P{o["phys"]}/S{o["spec"]} gap{o["gap"]:+4} shift{o["mshift"]:+3} score{o["score"]:+4} -> {o["cls"]} {o["rng"]} (now {o["cur"]}, {o["stat"]})')
            break
