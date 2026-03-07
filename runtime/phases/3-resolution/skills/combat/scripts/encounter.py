"""WWN encounter generation — random encounters from terrain and threat level.

Instantiates creatures from bestiary with rolled HP and initial positions.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_combat_tables = os.path.join(os.path.dirname(_this_dir), "tables")
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(_this_dir)), "core", "scripts")
for p in [_combat_tables, _core_scripts]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dice import roll_dice
from bestiary import CREATURES, HUMAN_TEMPLATES, ANIMAL_TEMPLATES


# Terrain-to-creature-type mapping
TERRAIN_ENCOUNTERS = {
    "forest": ["animal", "beast", "outsider"],
    "plains": ["animal", "mount", "human"],
    "mountains": ["animal", "beast", "automaton"],
    "desert": ["animal", "beast", "undead"],
    "swamp": ["beast", "undead", "outsider"],
    "coast": ["animal", "beast", "human"],
    "ruins": ["undead", "automaton", "outsider"],
    "urban": ["human"],
    "dungeon": ["undead", "automaton", "outsider", "beast"],
    "wilderness": ["animal", "beast", "human", "outsider"],
}

# Threat level to HD range
THREAT_HD_RANGE = {
    1: (1, 2),
    2: (1, 3),
    3: (2, 4),
    4: (3, 6),
    5: (4, 8),
    6: (5, 10),
    7: (6, 10),
    8: (8, 12),
    9: (8, 12),
    10: (10, 12),
}

# Threat level to encounter size
THREAT_COUNT_RANGE = {
    1: (1, 3),
    2: (1, 4),
    3: (1, 4),
    4: (1, 3),
    5: (1, 3),
    6: (1, 2),
    7: (1, 2),
    8: (1, 2),
    9: (1, 1),
    10: (1, 1),
}


def _roll_hp(hd):
    """Roll HP for a creature with given hit dice (d8 per HD)."""
    return sum(roll_dice(hd, 8))


def _pick_creatures(terrain, threat_level, count):
    """Select appropriate creatures for the encounter."""
    valid_types = TERRAIN_ENCOUNTERS.get(terrain, ["animal", "human"])
    hd_min, hd_max = THREAT_HD_RANGE.get(threat_level, (1, 4))

    # Filter creatures by type and HD range
    candidates = [c for c in CREATURES
                  if c.get("type", "") in valid_types
                  and hd_min <= c.get("hd", 1) <= hd_max]

    # Fallback to templates if no named creatures match
    if not candidates:
        if "human" in valid_types:
            candidates = [t for t in HUMAN_TEMPLATES
                          if hd_min <= t.get("hd", 1) <= hd_max]
        if not candidates:
            candidates = [t for t in ANIMAL_TEMPLATES
                          if hd_min <= t.get("hd", 1) <= hd_max]

    if not candidates:
        # Ultimate fallback
        candidates = [{"name": "Wild Beast", "hd": max(1, hd_min),
                       "ac": 13, "atk": "+2", "dmg": "1d6",
                       "shock": None, "move": "40'", "ml": 7,
                       "inst": 4, "skill": "+1", "save": "14+",
                       "type": "animal"}]

    selected = []
    for _ in range(count):
        creature = random.choice(candidates)
        selected.append(creature)

    return selected


def generate_encounter(terrain, threat_level):
    """Generate a random encounter for given terrain and threat level.

    Returns:
        dict with encounter details, creature list with rolled HP, zones.
    """
    threat_level = max(1, min(10, threat_level))

    count_min, count_max = THREAT_COUNT_RANGE.get(threat_level, (1, 3))
    count = random.randint(count_min, count_max)

    creatures = _pick_creatures(terrain, threat_level, count)

    # Instantiate with rolled HP and zone positions
    combatants = []
    for i, creature in enumerate(creatures):
        hp = _roll_hp(creature["hd"])
        combatant_id = f"enemy_{i+1}"

        # Starting zone: most start at near, ranged types at far
        start_zone = "near"
        if creature.get("type") == "automaton":
            start_zone = "melee"  # guardians are already positioned

        combatants.append({
            "id": combatant_id,
            "name": creature["name"],
            "creature_stats": creature,
            "hp_current": hp,
            "hp_max": hp,
            "zone": start_zone,
            "conditions": [],
            "is_pc": False,
        })

    return {
        "terrain": terrain,
        "threat_level": threat_level,
        "creature_count": count,
        "combatants": combatants,
        "encounter_description": _describe_encounter(combatants, terrain),
        "arithmetic_trace": f"Encounter: {count} creatures in {terrain} (threat {threat_level})",
    }


def _describe_encounter(combatants, terrain):
    """Generate a brief encounter description for narrative purposes."""
    names = {}
    for c in combatants:
        n = c["name"]
        names[n] = names.get(n, 0) + 1

    parts = []
    for name, count in names.items():
        if count == 1:
            parts.append(f"a {name}")
        else:
            parts.append(f"{count} {name}s")

    creature_desc = ", ".join(parts)
    return f"Encounter in {terrain}: {creature_desc}"
