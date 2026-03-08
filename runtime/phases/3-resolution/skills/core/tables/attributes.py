"""WWN attribute system tables. Extracted from WWN 1 p.8."""

# Attribute modifier lookup: score -> modifier
ATTRIBUTE_MODIFIERS = {
    3: -2,
    4: -1, 5: -1, 6: -1, 7: -1,
    8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
    14: 1, 15: 1, 16: 1, 17: 1,
    18: 2,
}

# The six attributes and their roles
ATTRIBUTES = {
    "strength": "Lifting, breaking, melee combat, carrying gear",
    "dexterity": "Speed, evasion, manual dexterity, reaction time, combat initiative",
    "constitution": "Hardiness, enduring injury, resisting poisons, going without food or rest",
    "intelligence": "Memory, reasoning, intellectual skills, general education",
    "wisdom": "Noticing things, making judgments, reading situations, intuition",
    "charisma": "Force of character, charming others, attracting attention, winning loyalty",
}

# Standard array for point-buy character creation
STANDARD_ARRAY = [14, 12, 11, 10, 9, 7]


def get_modifier(score):
    """Return the attribute modifier for a given score."""
    if score <= 3:
        return -2
    elif score <= 7:
        return -1
    elif score <= 13:
        return 0
    elif score <= 17:
        return 1
    else:
        return 2
