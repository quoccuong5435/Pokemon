"""Random legends (v2.5): clones of the level-100 legend bosses that wander in, and the Souls they drop."""
from dataclasses import dataclass

import balance

SPAWN_SECONDS = balance.LEG_INTERVAL
MAX_ALIVE = balance.LEG_MAX
SOUL_CHANCE = 100       # % chance a random legend drops its Soul (v3.3: always)
WILD_SOUL_CHANCE = balance.WILD_SOUL_CHANCE
MIN_LEVEL = 100         # only Pokemon of this level can damage a random legend
CONSOLATION = ('I00B', 'I001', 'I000')  # Rare Candy x5, Calcium x5, Carbos x5 (same as the bosses)


@dataclass(frozen=True)
class Legend:
    index: int
    name: str
    boss: str   # v1.8 legend boss unit the random legend is cloned from
    soul: str   # its Soul item (transforms a Pokemon in the circle at the map centre)

    @property
    def id(self):
        return 'nL%02X' % self.index


PKL_LEGEND_NAMES = ('Raikou', 'Entei', 'Suicune', 'Ho-Oh', 'Regirock', 'Kyogre', 'Jirachi', 'Groudon', 'Buzzwole')
# legends that have a room (teleport item in the Haunt Legendary shop): they stay in their rooms
ROOM_LEGENDS = ('Articuno', 'Moltres', 'Lugia', 'Darkrai', 'Mew', 'Mewtwo', 'Giratina', 'Deoxys', 'Arceus', 'Rayquaza',
                'Celebi')

LEGENDS = [Legend(i, *r) for i, r in enumerate((
    ('Articuno', 'n00C', 'I01C'), ('Moltres', 'n00D', 'I01D'), ('Lugia', 'n01I', 'I01E'),
    ('Darkrai', 'n00F', 'I01F'), ('Mew', 'n01L', 'I01G'), ('Regigigas', 'n01K', 'I01H'),
    ('Mewtwo', 'n01O', 'I01I'), ('Giratina', 'n01M', 'I01J'), ('Deoxys', 'n01N', 'I01K'),
    ('Arceus', 'n01J', 'I01L'), ('Rayquaza', 'n00G', 'I01M'), ('Zapdos', 'n001', 'I01Q'),
    ('Dialga', 'n033', 'I01V'), ('Palkia', 'n034', 'I01W'), ('Celebi', 'n035', 'ISCE'),
    # v3.3: PKLegends legends (boss template n00C, PKLegends model); Souls ISL0.. turn a Pokemon into the playable form
    ('Raikou', 'n00C', 'ISL0'), ('Entei', 'n00C', 'ISL1'), ('Suicune', 'n00C', 'ISL2'), ('Ho-Oh', 'n00C', 'ISL3'),
    ('Regirock', 'n00C', 'ISL4'), ('Kyogre', 'n00C', 'ISL5'), ('Jirachi', 'n00C', 'ISL6'),
    ('Groudon', 'n00C', 'ISL7'), ('Buzzwole', 'n00C', 'ISL8'),
))]

# v3.3: only the legends without a room spawn outside, 2 every 3 minutes (no duplicates)
SPAWN_LEGENDS = [lg for lg in LEGENDS if lg.name not in ROOM_LEGENDS]
