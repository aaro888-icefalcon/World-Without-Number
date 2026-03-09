"""WWN creature combat AI — deterministic behavior trees.

Replaces LLM tactical decisions (AI Limitation L2). Given creature stats
and battlefield state, outputs the chosen action deterministically.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(_this_dir)), "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice


# Behavior profiles — each creature type maps to a profile
BEHAVIOR_PROFILES = {
    "aggressive": {
        "description": "Charges strongest target, fights to the death",
        "flee_threshold": 0.0,  # never flees
        "target_priority": "strongest",
        "uses_tactics": False,
    },
    "cautious": {
        "description": "Attacks weakest target, flees when bloodied",
        "flee_threshold": 0.5,  # flees at 50% HP
        "target_priority": "weakest",
        "uses_tactics": True,
    },
    "pack": {
        "description": "Focuses fire on same target, flees when half the group is down",
        "flee_threshold": 0.25,  # flees at 25% HP
        "target_priority": "focused",  # attack same target as allies
        "uses_tactics": True,
    },
    "guardian": {
        "description": "Holds position, attacks only those who approach",
        "flee_threshold": 0.0,  # never flees
        "target_priority": "nearest",
        "uses_tactics": False,
    },
    "spellcaster": {
        "description": "Stays at range, uses spells, flees when threatened in melee",
        "flee_threshold": 0.4,
        "target_priority": "weakest",
        "uses_tactics": True,
    },
    "ambush": {
        "description": "Attacks from surprise, retreats if surprise is lost",
        "flee_threshold": 0.6,  # flees easily
        "target_priority": "weakest",
        "uses_tactics": True,
    },
}


def get_profile_description(profile_name):
    """Return a narrative foreshadow string for a behavior profile.

    Used by the anti-stagnation move system to generate Tier 1 foreshadow
    text when an enemy is downed but others remain.

    Args:
        profile_name: one of the BEHAVIOR_PROFILES keys

    Returns:
        A short narrative string describing the remaining enemies' reaction.
    """
    descriptions = {
        "aggressive": "The remaining creatures press their attack with renewed fury",
        "cautious": "The survivors hesitate, reassessing their approach",
        "pack": "The remaining pack members regroup, coordinating their next move",
        "guardian": "The defenders hold their ground, unflinching",
        "spellcaster": "The caster steps back, gathering energy for a retaliatory strike",
        "ambush": "The creature melts back into shadow, repositioning",
    }
    return descriptions.get(profile_name, "The remaining enemies regroup")


def get_profile_for_creature(creature):
    """Determine behavior profile from creature stats and type."""
    creature_type = creature.get("type", "")
    ml = creature.get("ml", 7)
    special = creature.get("special", "")

    if "spell" in special.lower() or "magic" in special.lower():
        return "spellcaster"
    if creature_type == "undead":
        return "aggressive"
    if creature_type == "automaton":
        return "guardian"
    if ml >= 10:
        return "aggressive"
    if ml <= 6:
        return "cautious"
    if creature_type == "animal":
        return "pack" if creature.get("hd", 1) <= 3 else "cautious"
    return "cautious"


def choose_target(combatants, profile_name, creature_id):
    """Select a target based on behavior profile.

    Args:
        combatants: list of dicts [{id, hp_current, hp_max, zone, is_pc}]
        profile_name: behavior profile name
        creature_id: this creature's id (to exclude from targets)

    Returns:
        target id string, or None if no valid targets
    """
    profile = BEHAVIOR_PROFILES.get(profile_name, BEHAVIOR_PROFILES["cautious"])
    priority = profile["target_priority"]

    # Filter to valid targets (PCs that are alive)
    targets = [c for c in combatants
               if c.get("is_pc", False) and c["hp_current"] > 0
               and c["id"] != creature_id]

    if not targets:
        return None

    if priority == "weakest":
        targets.sort(key=lambda c: c["hp_current"])
        return targets[0]["id"]
    elif priority == "strongest":
        targets.sort(key=lambda c: c["hp_current"], reverse=True)
        return targets[0]["id"]
    elif priority == "nearest":
        # Prefer melee targets, then near, then far
        zone_order = {"melee": 0, "near": 1, "far": 2, "distant": 3}
        targets.sort(key=lambda c: zone_order.get(c.get("zone", "near"), 1))
        return targets[0]["id"]
    elif priority == "focused":
        # Attack the target with lowest HP (already being focused)
        targets.sort(key=lambda c: c["hp_current"])
        return targets[0]["id"]
    else:
        return targets[0]["id"]


def decide_action(creature, creature_state, combatants, ally_count, ally_casualties):
    """Determine a creature's action for this round.

    Args:
        creature: creature stat block from bestiary
        creature_state: dict {id, hp_current, hp_max, zone, conditions}
        combatants: all combatants [{id, hp_current, hp_max, zone, is_pc}]
        ally_count: total allies this creature started with
        ally_casualties: number of allies that have been killed

    Returns:
        dict with action_type, target, reasoning
    """
    profile_name = get_profile_for_creature(creature)
    profile = BEHAVIOR_PROFILES[profile_name]

    hp_ratio = creature_state["hp_current"] / max(1, creature_state["hp_max"])
    group_ratio = (ally_count - ally_casualties) / max(1, ally_count)

    # Check morale-based flee condition
    should_flee = False
    flee_reason = None

    if profile["flee_threshold"] > 0 and hp_ratio <= profile["flee_threshold"]:
        should_flee = True
        flee_reason = f"HP at {hp_ratio:.0%}, below flee threshold {profile['flee_threshold']:.0%}"

    if ally_count > 1 and ally_casualties >= ally_count / 2:
        if profile_name not in ("aggressive", "guardian"):
            should_flee = True
            flee_reason = f"Half of allies down ({ally_casualties}/{ally_count})"

    if should_flee:
        return {
            "action_type": "flee",
            "target": None,
            "reasoning": f"[{profile_name}] {flee_reason}. Creature flees.",
            "profile": profile_name,
        }

    # Select target
    target_id = choose_target(combatants, profile_name, creature_state["id"])

    if target_id is None:
        return {
            "action_type": "hold",
            "target": None,
            "reasoning": f"[{profile_name}] No valid targets. Creature holds position.",
            "profile": profile_name,
        }

    # Determine action type
    action_type = "melee_attack"
    if creature_state.get("zone", "near") != "melee":
        # Not in melee — move to melee or ranged attack
        if profile_name == "spellcaster":
            action_type = "ranged_attack"
        elif profile_name == "guardian":
            action_type = "hold"  # guardians don't chase
        else:
            action_type = "move_and_attack"

    return {
        "action_type": action_type,
        "target": target_id,
        "reasoning": f"[{profile_name}] HP {hp_ratio:.0%}, targeting {target_id} ({profile['target_priority']} priority).",
        "profile": profile_name,
    }


def resolve_creature_round(creatures_with_state, combatants, casualties_by_side):
    """Resolve actions for all creatures in a round.

    Args:
        creatures_with_state: list of (creature_stat_block, creature_combat_state)
        combatants: all combatants in the fight
        casualties_by_side: dict {side: casualty_count}

    Returns:
        list of action dicts, one per creature
    """
    actions = []
    enemy_casualties = casualties_by_side.get("enemy", 0)
    total_enemies = len(creatures_with_state)

    for creature, state in creatures_with_state:
        if state["hp_current"] <= 0:
            continue  # skip dead creatures

        action = decide_action(
            creature, state, combatants,
            ally_count=total_enemies,
            ally_casualties=enemy_casualties,
        )
        actions.append(action)

    return actions
