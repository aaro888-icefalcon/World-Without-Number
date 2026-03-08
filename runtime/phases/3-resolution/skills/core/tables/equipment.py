"""WWN equipment tables. Extracted from WWN 1 pp.32-37."""

# Currency exchange rates
EXCHANGE_RATES = {
    "copper_per_silver": 100,
    "silver_per_gold": 10,
    "base_unit": "silver pieces (sp)",
}

# Weapon traits and their meanings
WEAPON_TRAITS = {
    "2H": "Requires two hands to wield",
    "AP": "Armor-piercing; ignores non-magical armor AC bonus",
    "FX": "Fixed; cannot be moved once emplaced",
    "L": "Long; can attack targets 10 feet away",
    "LL": "Less Lethal; victims reduced to 0 HP are unconscious, not dying",
    "N": "Numerous; five can be readied in one item slot",
    "PM": "Precisely Murderous; add skill level to damage on a hit",
    "R": "Reload; requires a Main Action to reload after each shot",
    "S": "Subtle; easily concealed",
    "SR": "Slow Reload; requires two Main Actions to reload",
    "SS": "Single Shot; requires 4 rounds to reload (hurlants)",
    "T": "Throwable; can be hurled with listed range",
}

# All weapons with mechanical data
# Shock format: "damage/AC_threshold" or None
WEAPONS = [
    {"name": "Axe, Hand", "damage": "1d6", "shock": "1/15", "attribute": "Str/Dex", "range": "10/30", "traits": ["T"], "cost_sp": 10, "enc": 1},
    {"name": "Axe, War", "damage": "1d10", "shock": "3/15", "attribute": "Str", "range": None, "traits": ["2H"], "cost_sp": 50, "enc": 2},
    {"name": "Blackjack", "damage": "1d4", "shock": None, "attribute": "Str/Dex", "range": None, "traits": ["S", "LL"], "cost_sp": 1, "enc": 1},
    {"name": "Bow, Large", "damage": "1d8", "shock": None, "attribute": "Dex", "range": "100/600", "traits": ["2H", "R", "PM"], "cost_sp": 20, "enc": 2},
    {"name": "Bow, Small", "damage": "1d6", "shock": None, "attribute": "Dex", "range": "50/300", "traits": ["2H", "R", "PM"], "cost_sp": 20, "enc": 1},
    {"name": "Claw Blades", "damage": "1d6", "shock": "2/13", "attribute": "Str/Dex", "range": None, "traits": ["S"], "cost_sp": 10, "enc": 1},
    {"name": "Club", "damage": "1d4", "shock": None, "attribute": "Str/Dex", "range": "10/30", "traits": ["T", "LL"], "cost_sp": 0, "enc": 1},
    {"name": "Club, Great", "damage": "1d10", "shock": "2/15", "attribute": "Str", "range": None, "traits": ["2H"], "cost_sp": 1, "enc": 2},
    {"name": "Crossbow", "damage": "1d10", "shock": None, "attribute": "Dex", "range": "100/300", "traits": ["2H", "SR", "PM"], "cost_sp": 10, "enc": 1},
    {"name": "Dagger", "damage": "1d4", "shock": "1/15", "attribute": "Str/Dex", "range": "30/60", "traits": ["S", "T", "PM"], "cost_sp": 3, "enc": 1},
    {"name": "Halberd", "damage": "1d10", "shock": "2/15", "attribute": "Str", "range": None, "traits": ["2H", "L"], "cost_sp": 50, "enc": 2},
    {"name": "Hammer, Great", "damage": "1d10", "shock": "2/18", "attribute": "Str", "range": None, "traits": ["2H"], "cost_sp": 50, "enc": 2},
    {"name": "Hammer, War", "damage": "1d8", "shock": "1/18", "attribute": "Str", "range": None, "traits": [], "cost_sp": 30, "enc": 1},
    {"name": "Hurlant, Great", "damage": "3d10", "shock": None, "attribute": "Dex", "range": "600/2400", "traits": ["FX", "SS", "AP"], "cost_sp": 10000, "enc": 15},
    {"name": "Hurlant, Hand", "damage": "1d12", "shock": None, "attribute": "Dex", "range": "30/60", "traits": ["SS", "AP"], "cost_sp": 1000, "enc": 1},
    {"name": "Hurlant, Long", "damage": "2d8", "shock": None, "attribute": "Dex", "range": "200/600", "traits": ["2H", "SS", "AP", "PM"], "cost_sp": 4000, "enc": 2},
    {"name": "Mace", "damage": "1d6", "shock": "1/18", "attribute": "Str", "range": None, "traits": ["LL"], "cost_sp": 15, "enc": 1},
    {"name": "Pike", "damage": "1d8", "shock": "1/18", "attribute": "Str", "range": None, "traits": ["2H", "L"], "cost_sp": 10, "enc": 2},
    {"name": "Shield Bash, Large", "damage": "1d6", "shock": "1/13", "attribute": "Str", "range": None, "traits": ["LL"], "cost_sp": 0, "enc": 0},
    {"name": "Shield Bash, Small", "damage": "1d4", "shock": None, "attribute": "Str/Dex", "range": None, "traits": ["LL"], "cost_sp": 0, "enc": 0},
    {"name": "Spear, Heavy", "damage": "1d10", "shock": "2/15", "attribute": "Str", "range": None, "traits": ["2H"], "cost_sp": 10, "enc": 2},
    {"name": "Spear, Light", "damage": "1d6", "shock": "2/13", "attribute": "Str/Dex", "range": "30/60", "traits": ["T"], "cost_sp": 5, "enc": 1},
    {"name": "Staff", "damage": "1d6", "shock": "1/13", "attribute": "Str/Dex", "range": None, "traits": ["2H", "LL"], "cost_sp": 1, "enc": 1},
    {"name": "Stiletto", "damage": "1d4", "shock": "1/18", "attribute": "Dex", "range": None, "traits": ["S", "PM"], "cost_sp": 10, "enc": 1},
    {"name": "Sword, Great", "damage": "1d12", "shock": "2/15", "attribute": "Str", "range": None, "traits": ["2H"], "cost_sp": 250, "enc": 2},
    {"name": "Sword, Long", "damage": "1d8", "shock": "2/13", "attribute": "Str/Dex", "range": None, "traits": [], "cost_sp": 100, "enc": 1},
    {"name": "Sword, Short", "damage": "1d6", "shock": "2/15", "attribute": "Str/Dex", "range": None, "traits": [], "cost_sp": 10, "enc": 1},
    {"name": "Throwing Blade", "damage": "1d4", "shock": None, "attribute": "Dex", "range": "30/60", "traits": ["S", "T", "N"], "cost_sp": 3, "enc": 1},
    {"name": "Unarmed Attack", "damage": "1d2+Skill", "shock": None, "attribute": "Str/Dex", "range": None, "traits": ["LL"], "cost_sp": 0, "enc": 0},
]

# Armor table
ARMOR = [
    # Light armors
    {"name": "No Armor", "ac": 10, "cost_sp": 0, "enc": 0, "type": "light"},
    {"name": "War Shirt", "ac": 11, "cost_sp": 5, "enc": 0, "type": "light"},
    {"name": "Buff Coat", "ac": 12, "cost_sp": 50, "enc": 0, "type": "light"},
    {"name": "Linothorax", "ac": 13, "cost_sp": 20, "enc": 1, "type": "light"},
    {"name": "War Robe", "ac": 14, "cost_sp": 50, "enc": 3, "type": "light"},
    {"name": "Pieced Armor", "ac": 14, "cost_sp": 100, "enc": 2, "type": "light"},
    # Medium armors
    {"name": "Mail Shirt", "ac": 14, "cost_sp": 250, "enc": 1, "type": "medium"},
    {"name": "Cuirass and Greaves", "ac": 15, "cost_sp": 250, "enc": 2, "type": "medium"},
    {"name": "Scaled Armor", "ac": 16, "cost_sp": 500, "enc": 3, "type": "medium"},
    # Heavy armors
    {"name": "Mail Hauberk", "ac": 16, "cost_sp": 750, "enc": 2, "type": "heavy"},
    {"name": "Plate Armor", "ac": 17, "cost_sp": 1000, "enc": 2, "type": "heavy"},
    {"name": "Great Armor", "ac": 19, "cost_sp": 2000, "enc": 3, "type": "heavy"},
    {"name": "Grand Plate", "ac": 16, "cost_sp": 2000, "enc": 3, "type": "heavy"},
    # Shields
    {"name": "Small Shield", "ac": 13, "cost_sp": 20, "enc": 1, "type": "shield"},
    {"name": "Large Shield", "ac": 14, "cost_sp": 10, "enc": 1, "type": "shield"},
]

# Starting equipment packages (WWN 1 p.29)
# Each package provides a starting gear set; player picks one.
EQUIPMENT_PACKAGES = {
    "armored_warrior": {
        "name": "Armored Warrior's Pack",
        "armor_ac": 11,
        "items": [
            "War shirt armor", "Short sword", "Small shield",
            "Dagger", "Backpack", "Rations (1 week)", "Waterskin",
        ],
        "coins_sp": 10,
    },
    "archer": {
        "name": "Archer's Pack",
        "armor_ac": 12,
        "items": [
            "Buff coat armor", "Small bow", "20 arrows", "Short sword",
            "Backpack", "Rations (1 week)", "Waterskin",
        ],
        "coins_sp": 10,
    },
    "skirmisher": {
        "name": "Skirmisher's Pack",
        "armor_ac": 13,
        "items": [
            "Linothorax armor", "Spear, light", "Dagger",
            "5 throwing blades", "Backpack", "Rations (1 week)",
            "Waterskin",
        ],
        "coins_sp": 10,
    },
    "scholar": {
        "name": "Scholar's Pack",
        "armor_ac": 10,
        "items": [
            "Staff", "Dagger", "Writing kit", "Lantern",
            "2 flasks of oil", "Backpack", "Rations (1 week)",
            "Waterskin",
        ],
        "coins_sp": 20,
    },
    "rogue": {
        "name": "Rogue's Pack",
        "armor_ac": 12,
        "items": [
            "Buff coat armor", "Short sword", "Dagger",
            "Thieves' tools", "Rope (50')", "Grappling hook",
            "Backpack", "Rations (1 week)", "Waterskin",
        ],
        "coins_sp": 10,
    },
    "traveler": {
        "name": "Traveler's Pack",
        "armor_ac": 10,
        "items": [
            "Spear, light", "Dagger", "Lantern", "2 flasks of oil",
            "Rope (50')", "Bedroll", "Backpack", "Rations (2 weeks)",
            "Waterskin",
        ],
        "coins_sp": 15,
    },
}
