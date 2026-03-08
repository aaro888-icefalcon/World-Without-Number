"""WWN character creation engine.

Creates valid WWN characters with all required fields for state.json.
Supports all 4 classes (Warrior, Expert, Mage, Adventurer), 5 magic traditions,
focus selection, starting spells, equipment packages, and background skills.
"""

import sys
import os
import re
import random

# Add sibling dirs to path
_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
if _tables_dir not in sys.path:
    sys.path.insert(0, _tables_dir)

from attributes import ATTRIBUTES, get_modifier, STANDARD_ARRAY
from skills import SKILLS
from classes import CLASSES, ADVENTURER_PROGRESSION, XP_TABLE
from backgrounds import BACKGROUNDS
from foci import FOCI
from equipment import EQUIPMENT_PACKAGES
from traditions import TRADITIONS


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
    """Calculate the four saving throw targets.

    Physical: 16 - (level + best of Str/Con mod)
    Evasion:  16 - (level + best of Int/Dex mod)
    Mental:   16 - (level + best of Wis/Cha mod)
    Luck:     16 - level (no attribute modifier)
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
        "luck": 16 - level,
    }


def _parse_hit_die(hd_str):
    """Parse hit die string like '1d6+2' into (dice_count, die_size, flat_bonus)."""
    m = re.match(r'(\d+)d(\d+)([+\-]\d+)?', hd_str)
    if not m:
        return 1, 6, 0
    return int(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else 0


def calculate_hp(hit_die_str, con_mod):
    """Roll HP for a character. At level 1, minimum 1 HP."""
    dice_count, die_size, flat_bonus = _parse_hit_die(hit_die_str)
    total = sum(random.randint(1, die_size) for _ in range(dice_count)) + flat_bonus + con_mod
    return {"current": max(1, total), "max": max(1, total)}


def apply_background(background_id, skills_dict):
    """Apply a background's free skill to the character's skill dict."""
    bg = BACKGROUNDS[background_id]
    free_skill = bg["free_skill"]  # e.g., "Stab-0"
    skill_name = free_skill.split("-")[0].lower()
    if skill_name in skills_dict:
        skills_dict[skill_name] = max(skills_dict[skill_name], 0)
    return bg["name"]


def apply_quick_skills(background_id, skills_dict):
    """Apply a background's quick skills (all at level-0)."""
    bg = BACKGROUNDS[background_id]
    for qs in bg.get("quick_skills", []):
        skill_name = qs.split("-")[0].lower()
        if skill_name in skills_dict:
            skills_dict[skill_name] = max(skills_dict[skill_name], 0)


def _get_adventurer_combo_key(partial_classes):
    """Build the ADVENTURER_PROGRESSION key from partial class list."""
    return "/".join(sorted(f"partial_{p}" for p in partial_classes))


def _validate_tradition(class_name, tradition, partial_classes=None):
    """Validate tradition selection for the given class."""
    if tradition is None:
        return
    if tradition not in TRADITIONS:
        raise ValueError(f"Unknown tradition: {tradition}. Choose from: {list(TRADITIONS.keys())}")
    trad = TRADITIONS[tradition]
    if trad["partial_only"]:
        if class_name == "mage":
            raise ValueError(
                f"Tradition '{tradition}' is partial-only and cannot be used by a full Mage. "
                f"Use it with an Adventurer partial mage instead."
            )


def _validate_foci(class_name, foci, partial_classes=None):
    """Validate focus picks against class restrictions."""
    if not foci:
        return
    for f in foci:
        if f not in FOCI:
            raise ValueError(f"Unknown focus: {f}. Choose from: {list(FOCI.keys())}")

    warrior_picks = sum(1 for f in foci if FOCI[f].get("type") == "warrior")

    if class_name == "warrior":
        max_warrior = len(foci)
    elif class_name == "expert":
        max_warrior = 1  # only the "Any" slot accepts warrior-type
    elif class_name == "mage":
        max_warrior = 1
    elif class_name == "adventurer":
        has_warrior = partial_classes and "warrior" in partial_classes
        if has_warrior:
            max_warrior = len(foci)  # warrior slot + any slot all accept warrior
        else:
            max_warrior = 1  # only the any slot
    else:
        max_warrior = len(foci)

    if warrior_picks > max_warrior:
        raise ValueError(
            f"Too many warrior-type foci ({warrior_picks}) for {class_name}. "
            f"Max allowed: {max_warrior}"
        )


def _calculate_effort(class_name, attributes, partial_classes=None):
    """Calculate Effort pool max for mages."""
    is_mage = class_name == "mage"
    is_partial_mage = (class_name == "adventurer" and
                       partial_classes and "mage" in partial_classes)
    if not is_mage and not is_partial_mage:
        return 0
    int_mod = get_modifier(attributes["intelligence"])
    wis_mod = get_modifier(attributes["wisdom"])
    cha_mod = get_modifier(attributes["charisma"])
    return max(1, 1 + max(int_mod, wis_mod, cha_mod))


def create_character(name, class_name, background_id, method="standard_array",
                     partial_classes=None, tradition=None, foci=None,
                     spells=None, equipment_package=None, skill_method=None,
                     free_skill=None):
    """Create a complete WWN character.

    Args:
        name: Character name.
        class_name: One of warrior, expert, mage, adventurer.
        background_id: Background ID (1-20).
        method: Attribute generation method (standard_array or roll_3d6).
        partial_classes: For adventurer, list of 2 partial class names.
        tradition: Magic tradition name for mage or partial mage.
        foci: List of focus names to pick at level 1.
        spells: List of spell names for starting spells (mages only).
        equipment_package: Equipment package key or "roll_coins".
        skill_method: "quick" to use background quick skills.
        free_skill: Skill name for free skill pick (set to level-0).

    Returns a dict suitable for embedding in state.json character field.
    """
    if class_name not in CLASSES:
        raise ValueError(f"Unknown class: {class_name}. Choose from: {list(CLASSES.keys())}")
    if background_id not in BACKGROUNDS:
        raise ValueError(f"Unknown background ID: {background_id}. Range: 1-20.")

    # Adventurer requires partial_classes
    if class_name == "adventurer":
        if not partial_classes or len(partial_classes) != 2:
            raise ValueError("Adventurer class requires exactly 2 partial_classes.")
        valid_partials = {"expert", "warrior", "mage"}
        if not set(partial_classes).issubset(valid_partials):
            raise ValueError(f"Invalid partial classes. Choose 2 from: {valid_partials}")
        if len(set(partial_classes)) != 2:
            raise ValueError("Adventurer must have 2 different partial classes.")

    # Validate tradition
    _validate_tradition(class_name, tradition, partial_classes)

    # Validate foci
    _validate_foci(class_name, foci, partial_classes)

    cls = CLASSES[class_name]

    # 1. Generate attributes
    attributes = generate_attributes(method)

    # 2. Initialize skills (all at -1 = unskilled)
    skills_dict = {s: -1 for s in SKILLS.keys()}

    # 3. Apply background free skill
    bg_name = apply_background(background_id, skills_dict)

    # 4. Apply quick skills if requested
    if skill_method == "quick":
        apply_quick_skills(background_id, skills_dict)

    # 5. Apply free skill pick
    if free_skill and free_skill in skills_dict:
        skills_dict[free_skill] = max(skills_dict[free_skill], 0)

    # 6. Calculate derived stats
    con_mod = get_modifier(attributes["constitution"])
    dex_mod = get_modifier(attributes["dexterity"])
    level = 1

    # Determine hit die and attack bonus based on class
    if class_name == "adventurer":
        combo_key = _get_adventurer_combo_key(partial_classes)
        if combo_key not in ADVENTURER_PROGRESSION:
            raise ValueError(f"Unknown adventurer combo: {combo_key}")
        adv_prog = ADVENTURER_PROGRESSION[combo_key]
        hit_die_str = adv_prog[1]["hd"]
        attack_bonus = adv_prog[1]["ab"]
        class_abilities = list(adv_prog.get("abilities", []))
    else:
        hit_die_str = cls["progression"][1]["hd"]
        attack_bonus = cls["progression"][1]["ab"]
        class_abilities = list(cls["abilities"].keys())

    hp = calculate_hp(hit_die_str, con_mod)
    saves = calculate_saving_throws(level, attributes)

    # Base AC = 10 + Dex mod (no armor)
    armor_class = 10 + dex_mod

    # 7. Calculate effort
    effort_max = _calculate_effort(class_name, attributes, partial_classes)

    # 8. Apply equipment package
    readied = []
    stowed = []
    coins = {"copper": 0, "silver": 0, "gold": 0}

    if equipment_package == "roll_coins":
        coins["silver"] = sum(random.randint(1, 6) for _ in range(3)) * 10
    elif equipment_package and equipment_package in EQUIPMENT_PACKAGES:
        pkg = EQUIPMENT_PACKAGES[equipment_package]
        readied = list(pkg["items"])
        coins["silver"] = pkg.get("coins_sp", 0)
        pkg_ac = pkg.get("armor_ac", 10)
        if pkg_ac > 10:
            armor_class = max(armor_class, pkg_ac + dex_mod)

    # 9. Build spells_known
    spells_known = []
    if spells and (class_name == "mage" or
                   (class_name == "adventurer" and partial_classes and "mage" in partial_classes)):
        if tradition and TRADITIONS.get(tradition, {}).get("has_spells", False):
            spells_known = list(spells)

    # 10. Build character dict
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
        "effort": {"current": 0, "max": effort_max},
        "equipment": {
            "readied": readied,
            "stowed": stowed,
            "coins": coins,
        },
        "foci": list(foci) if foci else [],
        "class_abilities": class_abilities,
    }

    # Adventurer-specific fields
    if class_name == "adventurer":
        character["partial_classes"] = sorted(partial_classes)

    # Magic-specific fields
    if tradition:
        character["tradition"] = tradition
    character["spells_known"] = spells_known

    return character
