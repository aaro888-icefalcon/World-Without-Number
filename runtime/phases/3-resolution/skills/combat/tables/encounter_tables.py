"""Terrain-based encounter tables mapping terrain types to creature pools.

Each terrain has a list of (creature_id, weight) tuples. Weight determines
relative frequency. Use get_encounter(terrain, threat_level) to roll an
encounter, or get_creature() from bestiary to resolve stat blocks.
"""

import random
import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from bestiary import get_creature, CREATURES

# Terrain → list of (creature_id, weight)
# Weight is relative; higher = more common
TERRAIN_CREATURE_TABLE = {
    "road": [
        ("bandit", 4),
        ("bandit_captain", 2),
        ("wolf", 2),
        ("guard", 1),
        ("cultist", 2),
    ],
    "plains": [
        ("wolf", 3),
        ("dire_wolf", 2),
        ("boar_wild", 2),
        ("razorhorn", 2),
        ("bandit", 2),
        ("horse_riding", 1),
        ("hawk_giant", 1),
        ("griffon", 1),
    ],
    "forest": [
        ("wolf", 3),
        ("bear_black", 3),
        ("giant_spider", 3),
        ("owlbear", 2),
        ("boar_wild", 2),
        ("vine_horror", 2),
        ("thornblight", 2),
        ("bandit", 2),
        ("displacer_beast", 1),
        ("giant_snake_constrictor", 1),
    ],
    "hills": [
        ("wolf", 2),
        ("dire_wolf", 2),
        ("bear_cave", 1),
        ("giant_scorpion", 2),
        ("manticore", 1),
        ("wyvern", 1),
        ("bandit", 2),
        ("giant_bat", 2),
        ("chimera", 1),
    ],
    "mountains": [
        ("bear_cave", 2),
        ("giant_bat", 3),
        ("wyvern", 2),
        ("griffon", 2),
        ("chimera", 1),
        ("giant_scorpion", 2),
        ("stone_golem", 1),
        ("iron_sentinel", 1),
    ],
    "desert": [
        ("giant_scorpion", 3),
        ("salt_devil", 3),
        ("ashcrawler", 2),
        ("giant_snake_venomous", 2),
        ("bandit", 2),
        ("mummy", 1),
        ("flame_imp", 1),
        ("animated_skeleton", 1),
    ],
    "swamp": [
        ("crocodile", 3),
        ("giant_snake_constrictor", 2),
        ("giant_snake_venomous", 2),
        ("swamp_leech_giant", 3),
        ("shambling_corpse", 2),
        ("ghoul", 2),
        ("vine_horror", 2),
        ("mushroom_sentinel", 1),
        ("carnivorous_tree", 1),
    ],
    "coast": [
        ("crocodile", 2),
        ("giant_bat", 1),
        ("bandit", 2),
        ("flying_jellyfish", 1),
        ("hawk_giant", 1),
        ("swamp_leech_giant", 1),
        ("wolf", 1),
        ("guard", 1),
    ],
    "jungle": [
        ("giant_spider", 3),
        ("giant_snake_constrictor", 3),
        ("giant_snake_venomous", 2),
        ("carnivorous_tree", 2),
        ("vine_horror", 2),
        ("mushroom_sentinel", 2),
        ("blightwood_treant", 1),
        ("owlbear", 1),
        ("spiderhound", 2),
        ("phase_serpent", 1),
    ],
}

# Threat level adjustments — higher threat can pull tougher creatures
# threat_level: 1=low, 2=moderate, 3=high, 4=deadly
THREAT_BONUS_POOL = {
    "road": [
        ("assassin", 2),
        ("knight", 1),
        ("cultist", 2),
        ("cult_priest", 1),
    ],
    "plains": [
        ("manticore", 1),
        ("chimera", 1),
        ("hydra_five_headed", 1),
    ],
    "forest": [
        ("bear_cave", 1),
        ("basilisk", 1),
        ("fey_knight", 1),
        ("blightwood_treant", 1),
    ],
    "hills": [
        ("hydra_five_headed", 1),
        ("greater_demon", 1),
        ("death_knight", 1),
    ],
    "mountains": [
        ("hydra_five_headed", 1),
        ("greater_demon", 1),
        ("crystal_golem", 1),
    ],
    "desert": [
        ("void_spawn", 1),
        ("greater_demon", 1),
        ("death_knight", 1),
    ],
    "swamp": [
        ("hydra_five_headed", 1),
        ("wraith_lord", 1),
        ("revenant", 1),
        ("corpse_titan", 1),
    ],
    "coast": [
        ("wyvern", 1),
        ("shadow_stalker", 1),
    ],
    "jungle": [
        ("basilisk", 1),
        ("hydra_five_headed", 1),
        ("cockatrice", 1),
        ("void_spawn", 1),
    ],
}

# Undead encounter pool — used in cursed/haunted areas
UNDEAD_POOL = [
    ("animated_skeleton", 4),
    ("shambling_corpse", 3),
    ("ravenous_husk", 3),
    ("ghoul", 3),
    ("skeletal_champion", 2),
    ("wight", 2),
    ("angry_shade", 2),
    ("specter", 2),
    ("mummy", 1),
    ("revenant", 1),
    ("bone_horror", 1),
    ("wraith_lord", 1),
    ("death_knight", 1),
    ("vampire", 1),
    ("corpse_titan", 1),
]

# Ruin/dungeon encounter pool
RUIN_POOL = [
    ("animated_skeleton", 3),
    ("animated_armor", 3),
    ("clockwork_spider", 2),
    ("brass_archer", 2),
    ("living_statue", 2),
    ("steam_walker", 2),
    ("iron_sentinel", 1),
    ("brass_legion_scytheman", 2),
    ("bone_construct", 1),
    ("clay_guardian", 1),
    ("brass_legion_hulk", 1),
    ("crystal_golem", 1),
    ("stone_golem", 1),
]


def _weighted_choice(pool, rng=None):
    """Pick a creature_id from a weighted pool."""
    if rng is None:
        rng = random
    ids, weights = zip(*pool)
    return rng.choices(ids, weights=weights, k=1)[0]


def get_encounter(terrain, threat_level=1, seed=None):
    """Roll a random encounter for the given terrain and threat level.

    Args:
        terrain: One of the TERRAIN_CREATURE_TABLE keys.
        threat_level: 1-4 (low to deadly).
        seed: Optional RNG seed for reproducibility.

    Returns:
        dict with creature stat block and encounter metadata.
    """
    rng = random.Random(seed)

    base_pool = TERRAIN_CREATURE_TABLE.get(terrain)
    if base_pool is None:
        return {"error": f"Unknown terrain: {terrain}. Valid: {list(TERRAIN_CREATURE_TABLE.keys())}"}

    # For threat >= 3, mix in bonus pool creatures
    pool = list(base_pool)
    if threat_level >= 3:
        bonus = THREAT_BONUS_POOL.get(terrain, [])
        pool.extend(bonus)

    creature_id = _weighted_choice(pool, rng)
    creature = get_creature(creature_id)

    if creature is None:
        return {"error": f"Creature ID '{creature_id}' not found in bestiary"}

    # Determine number appearing based on HD
    hd = creature.get("hd", 1)
    if hd <= 1:
        count = rng.randint(2, 8)
    elif hd <= 3:
        count = rng.randint(1, 6)
    elif hd <= 6:
        count = rng.randint(1, 4)
    elif hd <= 9:
        count = rng.randint(1, 2)
    else:
        count = 1

    return {
        "terrain": terrain,
        "threat_level": threat_level,
        "creature": creature,
        "count": count,
        "seed": seed,
    }


def get_undead_encounter(threat_level=1, seed=None):
    """Roll a random undead encounter."""
    rng = random.Random(seed)
    creature_id = _weighted_choice(UNDEAD_POOL, rng)
    creature = get_creature(creature_id)
    if creature is None:
        return {"error": f"Creature ID '{creature_id}' not found in bestiary"}

    hd = creature.get("hd", 1)
    count = max(1, rng.randint(1, max(1, 6 - hd // 2)))

    return {
        "creature": creature,
        "count": count,
        "seed": seed,
    }


def get_ruin_encounter(depth=1, seed=None):
    """Roll a random ruin/dungeon encounter scaled by depth."""
    rng = random.Random(seed)
    creature_id = _weighted_choice(RUIN_POOL, rng)
    creature = get_creature(creature_id)
    if creature is None:
        return {"error": f"Creature ID '{creature_id}' not found in bestiary"}

    hd = creature.get("hd", 1)
    count = max(1, rng.randint(1, max(1, 6 - hd // 2)))

    return {
        "creature": creature,
        "count": count,
        "depth": depth,
        "seed": seed,
    }


def validate_terrain_coverage():
    """Verify all terrain types have valid creature references."""
    errors = []
    all_terrains = set(TERRAIN_CREATURE_TABLE.keys())

    for terrain, pool in TERRAIN_CREATURE_TABLE.items():
        for creature_id, weight in pool:
            c = get_creature(creature_id)
            if c is None:
                errors.append(f"Terrain '{terrain}': creature_id '{creature_id}' not found in bestiary")

    for terrain, pool in THREAT_BONUS_POOL.items():
        for creature_id, weight in pool:
            c = get_creature(creature_id)
            if c is None:
                errors.append(f"Threat bonus '{terrain}': creature_id '{creature_id}' not found in bestiary")

    for creature_id, weight in UNDEAD_POOL:
        c = get_creature(creature_id)
        if c is None:
            errors.append(f"Undead pool: creature_id '{creature_id}' not found in bestiary")

    for creature_id, weight in RUIN_POOL:
        c = get_creature(creature_id)
        if c is None:
            errors.append(f"Ruin pool: creature_id '{creature_id}' not found in bestiary")

    return {"valid": len(errors) == 0, "errors": errors, "terrains_covered": sorted(all_terrains)}
