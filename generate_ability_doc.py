import json

with open('_PokemonArena2.0_work/pokeapi_abilities.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sample representation for common and popular Pokemon
sample_keys = [
    'Bulbasaur', 'Charmander', 'Squirtle', 'Pikachu', 'Pidgeot', 'Alakazam',
    'Machamp', 'Gengar', 'Gyarados', 'Lapras', 'Eevee', 'Vaporeon', 'Jolteon',
    'Flareon', 'Aerodactyl', 'Snorlax', 'Dragonite', 'Mewtwo', 'Mew',
    'Meganium', 'Typhlosion', 'Feraligatr', 'Ampharos', 'Scizor', 'Heracross',
    'Tyranitar', 'Sceptile', 'Blaziken', 'Swampert', 'Gardevoir', 'Breloom',
    'Aggron', 'Flygon', 'Milotic', 'Salamence', 'Metagross', 'Rayquaza',
    'Infernape', 'Garchomp', 'Lucario', 'Togekiss', 'Electivire', 'Magmortar',
    'Gliscor', 'Mamoswine', 'Giratina', 'Arceus', 'Serperior', 'Chandelure',
    'Greninja', 'Aegislash', 'Sylveon', 'Decidueye', 'Incineroar', 'Mimikyu'
]

print(f"Sample table for {len(sample_keys)} prominent Pokemon:")
for k in sample_keys:
    if k in data:
        v = data[k]
        norm = ', '.join(v.get('normal', []))
        hid = ', '.join(v.get('hidden', [])) if v.get('hidden') else 'None (Pure/Special)'
        print(f"| **{k}** | {norm} | **{hid}** |")
