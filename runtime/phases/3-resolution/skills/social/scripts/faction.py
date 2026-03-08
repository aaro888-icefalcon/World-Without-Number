"""WWN faction turn system — process faction actions between sessions.

Simplified faction turn: each faction chooses an action based on goals and
resources, then executes it. Results update faction state and may generate
events visible through the world pulse.
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


# Simplified faction action set (derived from WWN 4 faction rules)
FACTION_ACTIONS = [
    {
        "name": "Expand Influence",
        "description": "The faction extends its reach into new territory or a new sphere.",
        "effect": "Gain +1 clock progress toward goal.",
    },
    {
        "name": "Gather Resources",
        "description": "The faction focuses on accumulating wealth or materials.",
        "effect": "Build up reserves for future actions.",
    },
    {
        "name": "Attack Rival",
        "description": "The faction takes direct action against a rival faction.",
        "effect": "Rival faction loses 1 clock progress. May trigger conflict.",
    },
    {
        "name": "Defend Territory",
        "description": "The faction fortifies its holdings against threats.",
        "effect": "Block one incoming attack this turn.",
    },
    {
        "name": "Recruit",
        "description": "The faction recruits new members or hires mercenaries.",
        "effect": "Increase power level by 1 (max 10).",
    },
    {
        "name": "Scheme",
        "description": "The faction engages in covert operations.",
        "effect": "Gain intelligence about rival faction goals.",
    },
    {
        "name": "Build",
        "description": "The faction constructs infrastructure or establishes institutions.",
        "effect": "Permanent improvement to faction capabilities.",
    },
]


def _choose_action(faction, all_factions):
    """AI-driven faction action selection based on personality and state."""
    archetype = faction.get("archetype", "neutral")
    power = faction.get("power_level", 5)
    clock = faction.get("clock", {})
    clock_progress = clock.get("current", 0) / max(1, clock.get("max", 6))

    # Simple personality-based action selection
    if archetype in ("aggressive", "militant") and power >= 5:
        # Strong aggressive factions attack
        return FACTION_ACTIONS[2]  # Attack Rival
    elif clock_progress >= 0.75:
        # Close to goal — push toward completion
        return FACTION_ACTIONS[0]  # Expand Influence
    elif power <= 3:
        # Weak factions build up
        return random.choice([FACTION_ACTIONS[1], FACTION_ACTIONS[4]])  # Gather or Recruit
    elif archetype in ("defensive", "mercantile"):
        return random.choice([FACTION_ACTIONS[3], FACTION_ACTIONS[1]])  # Defend or Gather
    else:
        # Default: semi-random from non-aggressive options
        return random.choice([FACTION_ACTIONS[0], FACTION_ACTIONS[1],
                              FACTION_ACTIONS[5], FACTION_ACTIONS[6]])


def execute_faction_action(faction, action, target_faction=None):
    """Execute a single faction's chosen action.

    Returns:
        dict with action result
    """
    result = {
        "faction": faction["name"],
        "faction_id": faction["id"],
        "action": action["name"],
        "description": action["description"],
        "effect": action["effect"],
        "success": True,
    }

    # Roll for action success (2d6, 8+ succeeds)
    rolls = roll_dice(2, 6)
    total = sum(rolls)
    power_bonus = min(3, faction.get("power_level", 5) // 3)
    total += power_bonus

    result["roll"] = rolls
    result["total"] = total
    result["success"] = total >= 8

    if target_faction and action["name"] == "Attack Rival":
        result["target"] = target_faction.get("name", "unknown")

    result["arithmetic_trace"] = (
        f"{faction['name']}: {action['name']} → "
        f"2d6=[{rolls[0]}+{rolls[1]}]+{power_bonus}(power) = {total} "
        f"→ {'SUCCESS' if result['success'] else 'FAILURE'}"
    )

    return result


def faction_turn(factions):
    """Process one faction turn for all active factions.

    Args:
        factions: list of faction dicts from state.json

    Returns:
        dict with all faction actions and results
    """
    results = []

    for faction in factions:
        if not faction.get("clock", {}).get("status", "active") == "active":
            continue

        action = _choose_action(faction, factions)

        # Find a target for attack actions
        target = None
        if action["name"] == "Attack Rival":
            rivals = [f for f in factions if f["id"] != faction["id"]]
            if rivals:
                target = random.choice(rivals)

        result = execute_faction_action(faction, action, target)
        results.append(result)

        # Apply effects
        if result["success"]:
            clock = faction.get("clock", {})
            if action["name"] == "Expand Influence" and clock:
                clock["current"] = min(clock.get("max", 6),
                                       clock.get("current", 0) + 1)

    return {
        "faction_count": len(factions),
        "actions_taken": len(results),
        "results": results,
        "arithmetic_trace": f"Faction turn: {len(results)} factions acted",
    }
