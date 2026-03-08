"""WWN class progression tables. Extracted from WWN 1 pp.18-21, 64; WWN 2 pp.66-87."""

# XP progression
XP_TABLE = {
    1: 0,
    2: 1500,
    3: 3000,
    4: 6000,
    5: 12000,
    6: 24000,
    7: 48000,
    8: 96000,
    9: 192000,
    10: 384000,
}

# Skill point costs by target level
SKILL_POINT_COSTS = {
    0: {"cost": 1, "min_level": 1},
    1: {"cost": 2, "min_level": 1},
    2: {"cost": 3, "min_level": 3},
    3: {"cost": 4, "min_level": 6},
    4: {"cost": 5, "min_level": 9},
}

# Attribute boost costs
ATTRIBUTE_BOOST_COST = {"cost": 1, "max_value": 18}

# Class definitions with progression tables
# Each level entry: (hit_dice, attack_bonus, focus_picks_at_this_level)
CLASSES = {
    "warrior": {
        "description": "Masters of combat, distinguished by their ability to deal and survive damage.",
        "hit_die": "1d6+2",
        "abilities": {
            "killing_blow": "Add half level (rounded up) to all damage rolls and Shock damage",
            "veterans_luck": "Once per scene, force a reroll of a hit against you or turn a miss into a hit. 1/scene.",
        },
        "progression": {
            1: {"hd": "1d6+2", "ab": 1, "focus": "1 Any + 1 Warrior"},
            2: {"hd": "2d6+4", "ab": 2, "focus": "+1 Any"},
            3: {"hd": "3d6+6", "ab": 3, "focus": None},
            4: {"hd": "4d6+8", "ab": 4, "focus": None},
            5: {"hd": "5d6+10", "ab": 5, "focus": "+1 Any"},
            6: {"hd": "6d6+12", "ab": 6, "focus": None},
            7: {"hd": "7d6+14", "ab": 7, "focus": "+1 Any"},
            8: {"hd": "8d6+16", "ab": 8, "focus": None},
            9: {"hd": "9d6+18", "ab": 9, "focus": None},
            10: {"hd": "10d6+20", "ab": 10, "focus": "+1 Any"},
        },
    },
    "expert": {
        "description": "Skilled professionals who excel outside of combat.",
        "hit_die": "1d6",
        "abilities": {
            "masterful_expertise": "Once per scene, reroll a failed non-combat skill check",
            "quick_learner": "Gain 1 extra non-combat skill point per level",
        },
        "progression": {
            1: {"hd": "1d6", "ab": 0, "focus": "1 Any + 1 Non-Combat"},
            2: {"hd": "2d6", "ab": 1, "focus": "+1 Any"},
            3: {"hd": "3d6", "ab": 1, "focus": None},
            4: {"hd": "4d6", "ab": 2, "focus": None},
            5: {"hd": "5d6", "ab": 2, "focus": "+1 Any"},
            6: {"hd": "6d6", "ab": 3, "focus": None},
            7: {"hd": "7d6", "ab": 3, "focus": "+1 Any"},
            8: {"hd": "8d6", "ab": 4, "focus": None},
            9: {"hd": "9d6", "ab": 4, "focus": None},
            10: {"hd": "10d6", "ab": 5, "focus": "+1 Any"},
        },
    },
    "mage": {
        "description": "Wielders of arcane power, masters of one or more magical traditions.",
        "hit_die": "1d6-1",
        "abilities": {
            "arcane_tradition": "Choose one magical tradition (High Mage, Elementalist, Necromancer, Healer, Vowed)",
        },
        "progression": {
            1: {"hd": "1d6-1", "ab": 0, "focus": "1 Any"},
            2: {"hd": "2d6-2", "ab": 0, "focus": "+1 Any"},
            3: {"hd": "3d6-3", "ab": 0, "focus": None},
            4: {"hd": "4d6-4", "ab": 0, "focus": None},
            5: {"hd": "5d6-5", "ab": 1, "focus": "+1 Any"},
            6: {"hd": "6d6-6", "ab": 1, "focus": None},
            7: {"hd": "7d6-7", "ab": 1, "focus": "+1 Any"},
            8: {"hd": "8d6-8", "ab": 1, "focus": None},
            9: {"hd": "9d6-9", "ab": 1, "focus": None},
            10: {"hd": "10d6-10", "ab": 2, "focus": "+1 Any"},
        },
    },
}

# Adventurer (multi-class) partial class attack bonus progression
PARTIAL_WARRIOR_AB = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 5, 8: 5, 9: 6, 10: 6}
PARTIAL_EXPERT_AB = {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 3}

# Full Mage spellcasting progression
FULL_MAGE_CASTING = {
    1: {"max_level": 1, "spells_cast": 1, "spells_prepared": 4},
    2: {"max_level": 1, "spells_cast": 1, "spells_prepared": 5},
    3: {"max_level": 2, "spells_cast": 2, "spells_prepared": 8},
    4: {"max_level": 2, "spells_cast": 2, "spells_prepared": 9},
    5: {"max_level": 3, "spells_cast": 3, "spells_prepared": 12},
    6: {"max_level": 3, "spells_cast": 3, "spells_prepared": 13},
    7: {"max_level": 4, "spells_cast": 4, "spells_prepared": 16},
    8: {"max_level": 4, "spells_cast": 4, "spells_prepared": 17},
    9: {"max_level": 5, "spells_cast": 5, "spells_prepared": 20},
    10: {"max_level": 5, "spells_cast": 6, "spells_prepared": 24},
}

# Partial Mage spellcasting progression
PARTIAL_MAGE_CASTING = {
    1: {"max_level": 1, "spells_cast": 1, "spells_prepared": 3},
    2: {"max_level": 1, "spells_cast": 1, "spells_prepared": 4},
    3: {"max_level": 1, "spells_cast": 2, "spells_prepared": 5},
    4: {"max_level": 2, "spells_cast": 2, "spells_prepared": 6},
    5: {"max_level": 2, "spells_cast": 2, "spells_prepared": 8},
    6: {"max_level": 2, "spells_cast": 3, "spells_prepared": 9},
    7: {"max_level": 3, "spells_cast": 3, "spells_prepared": 10},
    8: {"max_level": 3, "spells_cast": 4, "spells_prepared": 12},
    9: {"max_level": 3, "spells_cast": 4, "spells_prepared": 13},
    10: {"max_level": 4, "spells_cast": 5, "spells_prepared": 15},
}

# Adventurer (multi-class) class definition
# Adventurers pick two partial classes; their progression depends on the combination.
CLASSES["adventurer"] = {
    "description": "A versatile multi-class hero who combines two partial classes.",
    "hit_die": "varies",  # depends on partial class combination
    "abilities": {
        "partial_classes": "Choose two partial classes from: Partial Warrior, Partial Expert, Partial Mage",
    },
    "progression": None,  # use ADVENTURER_PROGRESSION below based on combo
}

# Adventurer combo-specific progression tables
# Keys are alphabetically sorted partial class pairs.
# Integer keys are level progression; string keys are metadata.
ADVENTURER_PROGRESSION = {
    "partial_expert/partial_warrior": {
        "hit_die": "1d6+2",
        "abilities": ["masterful_expertise", "veteran_luck_limited"],
        1: {"hd": "1d6+2", "ab": 1, "focus": "1 Expert + 1 Warrior + 1 Any"},
        2: {"hd": "2d6+4", "ab": 2, "focus": "+1 Any"},
        3: {"hd": "3d6+6", "ab": 2, "focus": None},
        4: {"hd": "4d6+8", "ab": 3, "focus": None},
        5: {"hd": "5d6+10", "ab": 4, "focus": "+1 Any"},
        6: {"hd": "6d6+12", "ab": 5, "focus": None},
        7: {"hd": "7d6+14", "ab": 5, "focus": "+1 Any"},
        8: {"hd": "8d6+16", "ab": 6, "focus": None},
        9: {"hd": "9d6+18", "ab": 6, "focus": None},
        10: {"hd": "10d6+20", "ab": 7, "focus": "+1 Any"},
    },
    "partial_expert/partial_mage": {
        "hit_die": "1d6",
        "abilities": ["masterful_expertise"],
        1: {"hd": "1d6", "ab": 0, "focus": "1 Expert + 1 Any"},
        2: {"hd": "2d6", "ab": 0, "focus": "+1 Any"},
        3: {"hd": "3d6", "ab": 0, "focus": None},
        4: {"hd": "4d6", "ab": 1, "focus": None},
        5: {"hd": "5d6", "ab": 1, "focus": "+1 Any"},
        6: {"hd": "6d6", "ab": 1, "focus": None},
        7: {"hd": "7d6", "ab": 2, "focus": "+1 Any"},
        8: {"hd": "8d6", "ab": 2, "focus": None},
        9: {"hd": "9d6", "ab": 2, "focus": None},
        10: {"hd": "10d6", "ab": 3, "focus": "+1 Any"},
    },
    "partial_mage/partial_warrior": {
        "hit_die": "1d6+1",
        "abilities": ["veteran_luck_limited"],
        1: {"hd": "1d6+1", "ab": 1, "focus": "1 Warrior + 1 Any"},
        2: {"hd": "2d6+2", "ab": 1, "focus": "+1 Any"},
        3: {"hd": "3d6+3", "ab": 2, "focus": None},
        4: {"hd": "4d6+4", "ab": 2, "focus": None},
        5: {"hd": "5d6+5", "ab": 3, "focus": "+1 Any"},
        6: {"hd": "6d6+6", "ab": 4, "focus": None},
        7: {"hd": "7d6+7", "ab": 5, "focus": "+1 Any"},
        8: {"hd": "8d6+8", "ab": 5, "focus": None},
        9: {"hd": "9d6+9", "ab": 6, "focus": None},
        10: {"hd": "10d6+10", "ab": 6, "focus": "+1 Any"},
    },
}

# Dual partial caster progression
DUAL_PARTIAL_MAGE_CASTING = {
    1: {"max_level": 1, "spells_cast": 1, "spells_prepared": 3},
    2: {"max_level": 1, "spells_cast": 1, "spells_prepared": 4},
    3: {"max_level": 1, "spells_cast": 2, "spells_prepared": 5},
    4: {"max_level": 2, "spells_cast": 2, "spells_prepared": 6},
    5: {"max_level": 2, "spells_cast": 2, "spells_prepared": 8},
    6: {"max_level": 2, "spells_cast": 3, "spells_prepared": 9},
    7: {"max_level": 3, "spells_cast": 3, "spells_prepared": 10},
    8: {"max_level": 3, "spells_cast": 4, "spells_prepared": 12},
    9: {"max_level": 3, "spells_cast": 4, "spells_prepared": 13},
    10: {"max_level": 4, "spells_cast": 5, "spells_prepared": 15},
}
