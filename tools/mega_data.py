"""Single source of truth for the 16 Mega Evolutions (see docs/superpowers/specs)."""
from dataclasses import dataclass

DURATION = 60.0
COOLDOWN = 150.0
SHOP1_ID = 'nMS1'
SHOP2_ID = 'nMS2'
KID_ID = 'hMK0'
BONUS_IDS = ('AMB1', 'AMB2', 'AMB3')  # armor, move speed, attack speed
BONUS_VALUES = {'AMB1': '10', 'AMB2': '80', 'AMB3': '0.40'}
ATTR_PCT_PER_POINT = 3   # each stat point of a Mega = +3% of the hero's current stat
DAMAGE_BONUS = 0.5       # +50% of (base damage + highest stat)
FALLBACK_SCALE = 1.25
FALLBACK_FX = 'Abilities\\Spells\\Other\\GeneralAuraTarget\\GeneralAuraTarget.mdl'
KID_MODEL_PKL = 'KidKangama'
_HEX = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # base36 index digit


@dataclass(frozen=True)
class Mega:
    index: int
    key: str
    name: str
    base_unit: str
    base_name: str
    stone_name: str
    price: int
    str_: int
    agi: int
    int_: int
    pkl_model: object      # PKL model stem or None
    pkl_icon: object       # PKL BTN file name or None
    tint: tuple
    fx: str
    order: str

    @property
    def skin_id(self):
        return 'hM0' + _HEX[self.index]

    @property
    def stone_id(self):
        return 'IM0' + _HEX[self.index]

    @property
    def evolve_id(self):
        return 'AM0' + _HEX[self.index]


W = (255, 255, 255)
_ROWS = [
    # key, name, base, base name, stone, price, str, agi, int, pkl model, pkl icon, tint, fallback?, order
    ('MegaVenusaur', 'Mega Venusaur', 'E002', 'Venusaur', 'Venusaurite', 5000, 15, 5, 10,
     'MegaBisaflor', 'BTNMegaBisaflor.blp', W, False, 'acidbomb'),
    ('MegaCharizardX', 'Mega Charizard X', 'E00E', 'Charizard', 'Charizardite X', 5000, 20, 5, 5,
     'MegaGlurakX', 'BTNMegaGlurakX.blp', W, False, 'ancestralspirit'),
    ('MegaCharizardY', 'Mega Charizard Y', 'E00E', 'Charizard', 'Charizardite Y', 5000, 5, 5, 20,
     'MegaGlurakY', 'BTNMegaGlurakY.blp', W, False, 'ancestralspirittarget'),
    ('MegaBlastoise', 'Mega Blastoise', 'E000', 'Blastoise', 'Blastoisinite', 5000, 10, 0, 20,
     'MegaTurtok', 'BTNMegaTurtok.blp', W, False, 'breathoffrost'),
    ('MegaBeedrill', 'Mega Beedrill', 'E02K', 'Beedrill', 'Beedrillite', 5000, 10, 20, 0,
     None, None, (255, 220, 90), True, 'chemicalrage'),
    ('MegaPidgeot', 'Mega Pidgeot', 'E00D', 'Pidgeot', 'Pidgeotite', 5000, 0, 15, 15,
     'MegaTauboss', 'BTNTauboss.blp', W, False, 'cripple'),
    ('MegaAlakazam', 'Mega Alakazam', 'E00I', 'Alakazam', 'Alakazite', 5000, 0, 10, 20,
     'MegaSimsala', 'BTNMegaSimsala.blp', W, False, 'cyclone'),
    ('MegaGengar', 'Mega Gengar', 'E01G', 'Gengar', 'Gengarite', 5000, 0, 10, 20,
     'MegaGengar', 'BTNMegaGengar.blp', W, False, 'disenchant'),
    ('MegaKangaskhan', 'Mega Kangaskhan', 'E02P', 'Kangaskhan', 'Kangaskhanite', 5000, 15, 10, 5,
     None, 'BTNMega-Kangama.blp', W, False, 'drain'),
    ('MegaPinsir', 'Mega Pinsir', 'E03W', 'Pinsir', 'Pinsirite', 5000, 15, 10, 5,
     'MegaPinsir', 'BTNMegaPinsir.blp', W, False, 'faeriefire'),
    ('MegaGyarados', 'Mega Gyarados', 'E03F', 'Gyarados', 'Gyaradosite', 5000, 20, 0, 10,
     'MegaGarados', 'BTNMegaGarados.blp', W, False, 'incineratearrow'),
    ('MegaSteelix', 'Mega Steelix', 'E03V', 'Steelix', 'Steelixite', 5000, 25, 0, 5,
     'MegaSteelix', 'BTNMSteelix.blp', W, False, 'lavamonster'),
    ('MegaScizor', 'Mega Scizor', 'E03M', 'Scizor', 'Scizorite', 5000, 20, 5, 5,
     'MegaScherox', 'BTNMegaScherox.blp', W, False, 'mechanicalcritter'),
    ('MegaMewtwoX', 'Mega Mewtwo X', 'E026', 'Mewtwo', 'Mewtwonite X', 7000, 25, 5, 0,
     None, None, (170, 200, 255), True, 'rainofchaos'),
    ('MegaMewtwoY', 'Mega Mewtwo Y', 'E026', 'Mewtwo', 'Mewtwonite Y', 7000, 5, 5, 20,
     None, None, (225, 170, 255), True, 'soulburn'),
    ('MegaRayquaza', 'Mega Rayquaza', 'E029', 'Rayquaza', 'Meteorite', 7000, 10, 10, 10,
     None, None, (140, 255, 170), True, 'transmute'),
    # v2.2: Megas of the new Pokemon (base units from poke_data), sold in Mega Shop III
    ('MegaBlaziken', 'Mega Blaziken', 'EN02', 'Blaziken', 'Blazikenite', 6000, 20, 10, 0,
     'MegaLohgock', 'BTNMLohgock.blp', W, False, 'coldarrows'),
    ('MegaSceptile', 'Mega Sceptile', 'EN05', 'Sceptile', 'Sceptilite', 6000, 5, 15, 10,
     'MegaGewaldro', 'BTNMegaGewaldro.blp', W, False, 'coldarrowstarg'),
    ('MegaTyranitar', 'Mega Tyranitar', 'EN08', 'Tyranitar', 'Tyranitarite', 6000, 20, 5, 5,
     'MegaDespotar', 'BTNMega-Despotar.blp', W, False, 'faeriefireon'),
    ('MegaGardevoir', 'Mega Gardevoir', 'EN0B', 'Gardevoir', 'Gardevoirite', 6000, 0, 10, 20,
     'GardevoirMega', 'BTNMega-Guardevoir.blp', W, False, 'faeriefireoff'),
    ('MegaGallade', 'Mega Gallade', 'EN0C', 'Gallade', 'Galladite', 6000, 20, 10, 0,
     'MegaGallade', 'BTNMegaGallade.blp', W, False, 'tankpilot'),
    ('MegaSalamence', 'Mega Salamence', 'EN0F', 'Salamence', 'Salamencite', 6000, 15, 10, 5,
     'MegaBrutalanda', 'BTNMBrutalanda.blp', W, False, 'tankdroppilot'),
    ('MegaMetagross', 'Mega Metagross', 'EN0I', 'Metagross', 'Metagrossite', 6000, 20, 5, 5,
     'MegaMetagross', 'BTNMegaMetagross.blp', W, False, 'tankloadpilot'),
    ('MegaLucario', 'Mega Lucario', 'EN0J', 'Lucario', 'Lucarionite', 6000, 10, 10, 10,
     'MegaLucario', 'BTNMega-Lucario.blp', W, False, 'townbelloff'),
    ('MegaAbsol', 'Mega Absol', 'EN0K', 'Absol', 'Absolite', 6000, 15, 10, 5,
     'MegaAbsol', 'BTNMegaAbsol.blp', W, False, 'volcano'),
]
SHOP3_ID = 'nMS3'
SHOP_RANGES = ((SHOP1_ID, 0, 8), (SHOP2_ID, 8, 16), (SHOP3_ID, 16, 25))  # shop id, first, end index

MEGAS = [
    Mega(i, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11],
         FALLBACK_FX if r[12] else '', r[13])
    for i, r in enumerate(_ROWS)
]
