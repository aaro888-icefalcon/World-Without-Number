"""WWN character creation engine.

Creates valid WWN characters with all required fields for state.json.
"""

import sys
import os
import random

# Add sibling dirs to path
_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
if _tables_dir not in sys.path:
    sys.path.insert(0, _tables_dir)

from attributes import ATTRIBUTES, get_modifier, STANDARD_ARRAY
from skills import SKILLS
from classes import CLASSES, XP_TABLE
from backgrounds import BACKGROUNDS


def _roll_3d6():
    return sum(random.randint(1, 6) for _ in range(3))


def generate_attributes(method="standard_array"):
    """Generate the six attributes.

    Methods:
        standard_array: Assign [14, 12, 11, 10, 9, 7] to attributes (randomly ordered)
        roll_3d6: Roll 3d6 for each attribute in order
    """
    attr_names = list(ATTRIBUTES.keys())
    if method == "standard_array":
        values = list(STANDARD_ARRAY)
        random.shuffle(values)
        return dict(zip(attr_names, values))
    elif method == "roll_3d6":
        return {name: _roll_3d6() for name in attr_names}
    else:
        raise ValueError(f"Unknown method: {method}. Use 'standard_array' or 'roll_3d6'.")


def calculate_saving_throws(level, attributes):
    """Calculate the three saving throw targets.

    Physical: 16 - (level + best of Str/Con mod)
    Evasion:  16 - (level + best of Int/Dex mod)
    Mental:   16 - (level + best of Wis/Cha mod)
    """
    str_mod = get_modifier(attributes["strength"])
    dex_mod = get_modifier(attributes["dexterity"])
    con_mod = get_modifier(attributes["constitution"])
    int_mod = get_modifier(attributes["intelligence"])
    wis_mod = get_modifier(attributes["wisdom"])
    cha_mod = get_modifier(attributes["charisma"])

    return {
        "physical": 16 - (level + max(str_mod, con_mod)),
        "evasion": 16 - (level + max(int_mod, dex_mod)),
        "mental": 16 - (level + max(wis_mod, cha_mod)),
    }


def calculate_hp(class_name, level, con_mod):
    """Roll HP for a character. At level 1, minimum 1 HP."""
    cls = CLASSES[class_name]
    # Parse hit die (e.g., "1d6+2" → die=6, bonus=2)
    hd = cls["progression"][1]["hd"]
    # Simple parse: take the level-1 entry
    import re
    m = re.match(r'(\d+)d(\d+)([+\-]\d+)?', hd)
    if not m:
        return {"current": 1, "max": 1}
    dice_count = int(m.group(1))
    die_size = int(m.group(2))
    flat_bonus = int(m.group(3)) if m.group(3) else 0

    total = sum(random.randint(1, die_size) for _ in range(dice_count)) + flat_bonus + con_mod
    total = max(1, total)
    return {"current": total, "max": total}


def apply_background(background_id, skills_dict):
    """Apply a background's free skill to the character's skill dict."""
    bg = BACKGROUNDS[background_id]
    free_skill = bg["free_skill"]  # e.g., "Stab-0"
    skill_name = free_skill.split("-")[0].lower()
    if skill_name in skills_dict:
        skills_dict[skill_name] = max(skills_dict[skill_name], 0)
    return bg["name"]


def create_character(name, class_name, background_id, method="standard_array"):
    """Create a complete WWN character.

    Returns a dict suitable for embedding in state.json character field.
    """
    if class_name not in CLASSES:
        raise ValueError(f"Unknown class: {class_name}. Choose from: {list(CLASSES.keys())}")
    if background_id not in BACKGROUNDS:
        raise ValueError(f"Unknown background ID: {background_id}. Range: 1-20.")

    cls = CLASSES[class_name]

    # 1. Generate attributes
    attributes = generate_attributes(method)

    # 2. Initialize skills (all at -1 = unskilled)
    skills_dict = {name: -1 for name in SKILLS.keys()}

    # 3. Apply background free skill
    bg_name = apply_background(background_id, skills_dict)

    # 4. Calculate derived stats
    con_mod = get_modifier(attributes["constitution"])
    dex_mod = get_modifier(attributes["dexterity"])

    level = 1
    hp = calculate_hp(class_name, level, con_mod)
    attack_bonus = cls["progression"][1]["ab"]
    saves = calculate_saving_throws(level, attributes)

    # Base AC = 10 + Dex mod (no armor)
    armor_class = 10 + dex_mod

    character = {
        "name": name,
        "class": class_name,
        "level": level,
        "xp": 0,
        "background": bg_name,
        "attributes": attributes,
        "hp": hp,
        "attack_bonus": attack_bonus,
        "armor_class": armor_class,
        "saving_throws": saves,
        "skills": skills_dict,
        "system_strain": {"current": 0, "max": attributes["constitution"]},
        "effort": {"current": 0, "max": 0},
        "equipment": {
            "readied": [],
            "stowed": [],
            "coins": {"copper": 0, "silver": 0, "gold": 0},
        },
        "foci": [],
        "class_abilities": list(cls["abilities"].keys()),
    }

    return character
