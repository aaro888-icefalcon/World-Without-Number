"""WWN magic system — spell casting, Effort, arts, and tradition management.

All spellcasting mechanics flow through this module. The LLM never determines
spell effects — they come from the spells table data.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
if _tables_dir not in sys.path:
    sys.path.insert(0, _tables_dir)

_core_scripts = _this_dir
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll, roll_dice


EFFORT_DURATIONS = ["scene", "day", "indefinite"]

TRADITIONS = ["high_magic", "elementalist", "necromancer", "healer"]


def get_max_spell_level(caster_level):
    """Mages can cast spells up to ceil(level/2), max 5."""
    return min(5, (caster_level + 1) // 2)


def can_cast(caster_level, spell_level):
    """Check if a caster of given level can cast a spell of given level."""
    return spell_level <= get_max_spell_level(caster_level)


def cast_spell(spell_name, caster_level, tradition, effort_current,
               system_strain_current, system_strain_max,
               target_save_type=None, target_save_target=None):
    """Resolve a spell casting attempt.

    Args:
        spell_name: Name of the spell being cast
        caster_level: Caster's character level
        tradition: Caster's magical tradition
        effort_current: Current uncommitted Effort
        system_strain_current: Current System Strain
        system_strain_max: Max System Strain (Constitution score)
        target_save_type: If spell allows a save, the save type
        target_save_target: If spell allows a save, the target number

    Returns:
        dict with casting result, effort changes, and any save resolution.
    """
    try:
        from spells import SPELLS
        matching = [s for s in SPELLS
                    if s["name"].lower() == spell_name.lower()]
    except ImportError:
        matching = []

    spell_data = matching[0] if matching else {
        "name": spell_name, "level": 1, "tradition": tradition,
        "description": "Spell effect resolved per rules."
    }

    spell_level = spell_data.get("level", 1)

    # Validate caster can cast this level
    max_level = get_max_spell_level(caster_level)
    if spell_level > max_level:
        return {
            "success": False,
            "error": f"Spell level {spell_level} exceeds max castable level {max_level} for level {caster_level} caster",
            "spell": spell_data["name"],
        }

    # Check Effort availability
    if effort_current < 1:
        return {
            "success": False,
            "error": "No Effort available to commit for this spell",
            "spell": spell_data["name"],
            "effort_current": effort_current,
        }

    result = {
        "success": True,
        "spell": spell_data["name"],
        "spell_level": spell_level,
        "tradition": spell_data.get("tradition", tradition),
        "description": spell_data.get("description", ""),
        "effort_committed": 1,
        "effort_duration": "scene",  # default; some spells vary
        "effort_before": effort_current,
        "effort_after": effort_current - 1,
        "arithmetic_trace": f"Cast {spell_data['name']} (level {spell_level}): Effort {effort_current}→{effort_current - 1}",
    }

    # Resolve target save if applicable
    if target_save_type and target_save_target:
        save_roll = roll_dice(1, 20)[0]
        save_success = save_roll >= target_save_target
        result["target_save"] = {
            "type": target_save_type,
            "roll": save_roll,
            "target": target_save_target,
            "success": save_success,
            "arithmetic_trace": f"d20=[{save_roll}] vs {target_save_target} → {'SAVED' if save_success else 'FAILED'}",
        }
        result["arithmetic_trace"] += f" | Target save: {result['target_save']['arithmetic_trace']}"

    return result


def use_art(art_name, tradition, effort_current):
    """Activate a tradition art (passive or active ability).

    Returns:
        dict with art activation result and effort changes.
    """
    try:
        from spells import ARTS
        matching = [a for a in ARTS
                    if a["name"].lower() == art_name.lower()]
    except ImportError:
        matching = []

    art_data = matching[0] if matching else {
        "name": art_name, "tradition": tradition,
        "description": "Art effect resolved per rules."
    }

    # Most arts commit Effort for the scene
    if effort_current < 1:
        return {
            "success": False,
            "error": "No Effort available to commit for this art",
            "art": art_data["name"],
            "effort_current": effort_current,
        }

    return {
        "success": True,
        "art": art_data["name"],
        "tradition": art_data.get("tradition", tradition),
        "description": art_data.get("description", ""),
        "effort_committed": 1,
        "effort_duration": "scene",
        "effort_before": effort_current,
        "effort_after": effort_current - 1,
        "arithmetic_trace": f"Activate {art_data['name']}: Effort {effort_current}→{effort_current - 1}",
    }


def recover_effort(rest_type, effort_committed_scene, effort_committed_day):
    """Calculate Effort recovery from rest.

    Args:
        rest_type: "scene_end", "nights_rest", or "full_day"
        effort_committed_scene: Effort committed for the scene
        effort_committed_day: Effort committed for the day

    Returns:
        dict with effort recovery details.
    """
    recovered_scene = 0
    recovered_day = 0

    if rest_type == "scene_end":
        recovered_scene = effort_committed_scene
    elif rest_type == "nights_rest":
        recovered_scene = effort_committed_scene
        recovered_day = effort_committed_day
    elif rest_type == "full_day":
        recovered_scene = effort_committed_scene
        recovered_day = effort_committed_day

    return {
        "rest_type": rest_type,
        "effort_recovered_scene": recovered_scene,
        "effort_recovered_day": recovered_day,
        "total_recovered": recovered_scene + recovered_day,
        "arithmetic_trace": f"Rest ({rest_type}): recover {recovered_scene} scene + {recovered_day} day = {recovered_scene + recovered_day} Effort",
    }
