"""WWN travel system — overland movement, foraging, encounters, privation.

Resolves multi-day travel with per-day events.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice, roll_check


# Movement rates by terrain (miles per day on foot)
TERRAIN_MOVEMENT = {
    "road": 24,
    "plains": 18,
    "forest": 12,
    "hills": 12,
    "mountains": 6,
    "desert": 12,
    "swamp": 6,
    "coast": 18,
    "jungle": 6,
}

# Encounter chance per day by terrain (roll 1d6, encounter on this or below)
TERRAIN_ENCOUNTER_CHANCE = {
    "road": 1,
    "plains": 1,
    "forest": 2,
    "hills": 2,
    "mountains": 2,
    "desert": 1,
    "swamp": 3,
    "coast": 1,
    "jungle": 3,
}

# Foraging difficulty by terrain
TERRAIN_FORAGE_DIFFICULTY = {
    "road": 10,
    "plains": 8,
    "forest": 6,
    "hills": 8,
    "mountains": 10,
    "desert": 12,
    "swamp": 8,
    "coast": 8,
    "jungle": 6,
}

# Travel events (non-combat, rolled on d8 per day)
TRAVEL_EVENTS = {
    1: {"type": "weather", "description": "Harsh weather slows travel"},
    2: {"type": "landmark", "description": "Notable landmark spotted"},
    3: {"type": "tracks", "description": "Fresh tracks or signs of passage"},
    4: {"type": "shelter", "description": "Natural shelter found"},
    5: {"type": "water", "description": "Water source discovered"},
    6: {"type": "remains", "description": "Remains of old camp or ruins spotted"},
    7: {"type": "traveler", "description": "Another traveler encountered"},
    8: {"type": "quiet", "description": "Uneventful travel"},
}


def forage(skill_modifier, terrain):
    """Attempt to forage for food.

    Args:
        skill_modifier: Wis/Survive total modifier
        terrain: terrain type

    Returns:
        dict with foraging result
    """
    difficulty = TERRAIN_FORAGE_DIFFICULTY.get(terrain, 8)
    result = roll_check(modifier=skill_modifier, target=difficulty)
    rations_found = 0
    if result["success"]:
        rations_found = 1
        if result["margin"] >= 4:
            rations_found = 2

    return {
        "success": result["success"],
        "rations_found": rations_found,
        "difficulty": difficulty,
        "terrain": terrain,
        "roll_result": result,
        "arithmetic_trace": f"Forage ({terrain}, DC {difficulty}): {result['arithmetic_trace']} → {rations_found} ration(s)",
    }


def check_encounter(terrain, threat_level):
    """Check if a random encounter occurs during travel.

    Returns:
        dict with encounter check result
    """
    chance = TERRAIN_ENCOUNTER_CHANCE.get(terrain, 1)
    roll = roll_dice(1, 6)[0]
    encounter = roll <= chance

    return {
        "roll": roll,
        "chance": chance,
        "encounter": encounter,
        "terrain": terrain,
        "threat_level": threat_level,
        "arithmetic_trace": f"Encounter check: d6=[{roll}] vs {chance} → {'ENCOUNTER' if encounter else 'clear'}",
    }


def apply_privation(days_without_food, days_without_water):
    """Calculate privation effects.

    Returns:
        dict with privation damage and status
    """
    effects = []
    damage = 0

    if days_without_water >= 1:
        water_damage = days_without_water * 2
        damage += water_damage
        effects.append(f"Dehydration: {water_damage} damage ({days_without_water} day(s) without water)")

    if days_without_food >= 3:
        food_damage = (days_without_food - 2)
        damage += food_damage
        effects.append(f"Starvation: {food_damage} damage ({days_without_food} day(s) without food)")

    return {
        "damage": damage,
        "effects": effects,
        "days_without_food": days_without_food,
        "days_without_water": days_without_water,
        "arithmetic_trace": f"Privation: {damage} total damage" if damage > 0 else "No privation effects",
    }


def resolve_travel(terrain, days, supplies, forage_modifier, threat_level):
    """Resolve multi-day overland travel.

    Args:
        terrain: terrain type string
        days: number of days to travel
        supplies: current ration count
        forage_modifier: Wis/Survive modifier for foraging
        threat_level: area threat level for encounter generation

    Returns:
        dict with day-by-day travel log
    """
    movement_per_day = TERRAIN_MOVEMENT.get(terrain, 18)
    total_distance = 0
    current_supplies = supplies
    travel_log = []

    for day in range(1, days + 1):
        day_result = {
            "day": day,
            "distance_miles": movement_per_day,
            "terrain": terrain,
            "events": [],
        }

        # Consume supplies
        if current_supplies > 0:
            current_supplies -= 1
            day_result["supply_consumed"] = True
        else:
            day_result["supply_consumed"] = False
            # Attempt foraging
            forage_result = forage(forage_modifier, terrain)
            day_result["forage"] = forage_result
            if forage_result["success"]:
                current_supplies += forage_result["rations_found"]
            day_result["events"].append(
                f"Foraging: {'found' if forage_result['success'] else 'failed'}")

        # Check for encounter
        enc_check = check_encounter(terrain, threat_level)
        day_result["encounter_check"] = enc_check
        if enc_check["encounter"]:
            day_result["events"].append("Random encounter!")
            day_result["has_encounter"] = True
        else:
            day_result["has_encounter"] = False

        # Roll travel event
        event_roll = roll_dice(1, 8)[0]
        event = TRAVEL_EVENTS[event_roll]
        day_result["travel_event"] = event
        day_result["events"].append(event["description"])

        total_distance += movement_per_day
        day_result["supplies_remaining"] = current_supplies
        travel_log.append(day_result)

    return {
        "terrain": terrain,
        "days": days,
        "total_distance_miles": total_distance,
        "movement_per_day": movement_per_day,
        "supplies_start": supplies,
        "supplies_end": current_supplies,
        "travel_log": travel_log,
        "encounters": sum(1 for d in travel_log if d.get("has_encounter")),
        "arithmetic_trace": f"Travel {days} days through {terrain}: {total_distance} miles, {sum(1 for d in travel_log if d.get('has_encounter'))} encounter(s)",
    }
