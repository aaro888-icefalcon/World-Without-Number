"""WWN dungeon generation — procedural dungeon with rooms, encounters, and treasure.

Generates a connected dungeon layout with themed rooms, hazards,
encounters, and treasure scaled by depth.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice


# Dungeon themes
DUNGEON_THEMES = [
    "Ancient Temple", "Collapsed Mine", "Sorcerer's Sanctum",
    "Buried Fortress", "Flooded Catacombs", "Clockwork Vault",
    "Bone Cathedral", "Fungal Caverns", "Prison Complex",
    "Tomb of the Forgotten", "Alchemical Laboratory", "Beast Warren",
]

# Room types
ROOM_TYPES = [
    "corridor", "chamber", "hall", "shrine", "storeroom",
    "barracks", "workshop", "cistern", "gallery", "vault",
    "throne_room", "laboratory", "crypt", "arena", "library",
]

# Hazard types
HAZARD_TYPES = [
    {"type": "pit_trap", "description": "A concealed pit trap, 10 feet deep. Evasion save or 1d6 falling damage."},
    {"type": "poison_dart", "description": "Pressure plate triggers poison darts. Physical save or 1d4 damage and poisoned."},
    {"type": "collapsing_ceiling", "description": "Weakened ceiling section. Evasion save or 2d6 bludgeoning damage."},
    {"type": "gas_vent", "description": "Toxic gas seeps from cracks. Physical save or -2 to all rolls for 1 hour."},
    {"type": "alarm_glyph", "description": "A magical alarm that alerts all creatures in adjacent rooms."},
    {"type": "swinging_blade", "description": "A pendulum blade swings across the passage. Evasion save or 1d8 slashing damage."},
    {"type": "flooding_room", "description": "The door seals and water begins to rise. Must find the drain mechanism."},
    {"type": "illusory_floor", "description": "The floor is an illusion over a 15-foot drop. Evasion save to catch the edge."},
]


def generate_dungeon(depth, theme=None):
    """Generate a procedural dungeon.

    Args:
        depth: dungeon depth level (affects room count, threat, and treasure)
        theme: optional theme string, or None for random

    Returns:
        dict with rooms, connections, encounters, hazards, treasure, theme
    """
    depth = max(1, min(10, depth))

    if theme is None:
        theme = random.choice(DUNGEON_THEMES)

    room_count = 3 + depth + roll_dice(1, 4)[0]
    threat_level = min(10, depth + 2)
    treasure_tier = max(1, min(5, (depth + 1) // 2))

    rooms = []
    for i in range(room_count):
        is_boss = (i == room_count - 1)
        room = _generate_room(i, depth, threat_level, treasure_tier, is_boss, theme)
        rooms.append(room)

    # Connect rooms: linear chain with branching
    for i in range(len(rooms) - 1):
        rooms[i]["connections"].append(rooms[i + 1]["id"])
        rooms[i + 1]["connections"].append(rooms[i]["id"])

    # Add branches (30% chance per room after the first 2)
    for i in range(2, len(rooms)):
        if random.random() < 0.30:
            branch_target = random.randint(0, i - 2)
            if rooms[branch_target]["id"] not in rooms[i]["connections"]:
                rooms[i]["connections"].append(rooms[branch_target]["id"])
                rooms[branch_target]["connections"].append(rooms[i]["id"])

    return {
        "depth": depth,
        "theme": theme,
        "room_count": room_count,
        "threat_level": threat_level,
        "treasure_tier": treasure_tier,
        "rooms": rooms,
        "arithmetic_trace": f"Dungeon (depth {depth}, {theme}): {room_count} rooms, threat {threat_level}, tier {treasure_tier}",
    }


def _generate_room(index, depth, threat_level, treasure_tier, is_boss, theme):
    """Generate a single dungeon room."""
    room_id = f"room_{index + 1}"
    room_type = random.choice(ROOM_TYPES)

    room = {
        "id": room_id,
        "type": room_type,
        "connections": [],
        "is_boss": is_boss,
        "description": _room_description(room_type, theme, is_boss),
    }

    # Encounter chance: 40% normal, 100% boss
    if is_boss or random.random() < 0.40:
        room["has_encounter"] = True
        enc_threat = threat_level + (2 if is_boss else 0)
        room["encounter_threat"] = min(10, enc_threat)
    else:
        room["has_encounter"] = False

    # Hazard chance: 30% per room (not boss)
    if not is_boss and random.random() < 0.30:
        room["hazard"] = random.choice(HAZARD_TYPES)
    else:
        room["hazard"] = None

    # Treasure chance: scales with depth, guaranteed in boss room
    treasure_chance = 0.2 + depth * 0.05
    if is_boss or random.random() < treasure_chance:
        room["has_treasure"] = True
        room["treasure_tier"] = treasure_tier + (1 if is_boss else 0)
        room["treasure_tier"] = min(5, room["treasure_tier"])
    else:
        room["has_treasure"] = False

    return room


def _room_description(room_type, theme, is_boss):
    """Generate a brief room description."""
    if is_boss:
        return f"The heart of the {theme}. This {room_type} radiates danger and the promise of reward."

    descriptions = {
        "corridor": f"A narrow passage through the {theme}, walls damp with condensation.",
        "chamber": f"A medium-sized chamber, its purpose in the {theme} unclear.",
        "hall": f"A grand hall with vaulted ceilings, echoing with emptiness.",
        "shrine": f"A small shrine to forgotten powers, its altar still stained.",
        "storeroom": f"A storeroom with collapsed shelves and scattered debris.",
        "barracks": f"Old living quarters, cots and personal effects left behind.",
        "workshop": f"A workspace with rusted tools and half-finished projects.",
        "cistern": f"A water cistern, partially filled with dark, still water.",
        "gallery": f"A long gallery with alcoves that once held statues or trophies.",
        "vault": f"A reinforced room with a heavy door, designed to protect its contents.",
        "throne_room": f"A ceremonial chamber with a raised seat at the far end.",
        "laboratory": f"An ancient laboratory with broken glassware and stained workbenches.",
        "crypt": f"Burial niches line the walls, some sealed, others broken open.",
        "arena": f"A sunken pit designed for combat, viewing galleries above.",
        "library": f"Shelves of crumbling texts, most illegible with age.",
    }
    return descriptions.get(room_type, f"A room within the {theme}.")
