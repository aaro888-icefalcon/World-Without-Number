#!/usr/bin/env python3
"""Worlds Without Number — Self-contained RPG mechanics engine.

All dice rolls, damage calculations, skill checks, saves, combat, travel,
encounters, NPC generation, and treasure are handled deterministically.
Outputs JSON for every command.

Usage:
    python wwn_engine.py <command> [options]
    python wwn_engine.py roll 2d6+3
    python wwn_engine.py skill-check --attribute-mod 1 --skill-level 0 --difficulty 8
    python wwn_engine.py attack --attack-bonus 1 --skill-level 0 --attribute-mod 2 --weapon-damage 1d8 --shock 2/15 --target-ac 14 --target-hp 8
"""

import argparse
import json
import random
import re
import sys
import copy

# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Attribute system
# ═══════════════════════════════════════════════════════════════════════════════

ATTRIBUTE_MODIFIERS = {
    3: -2, 4: -1, 5: -1, 6: -1, 7: -1,
    8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
    14: 1, 15: 1, 16: 1, 17: 1, 18: 2,
}

ATTRIBUTES = {
    "strength": "Lifting, breaking, melee combat, carrying gear",
    "dexterity": "Speed, evasion, manual dexterity, reaction time",
    "constitution": "Hardiness, enduring injury, resisting poisons",
    "intelligence": "Memory, reasoning, intellectual skills",
    "wisdom": "Noticing things, making judgments, intuition",
    "charisma": "Force of character, charming others, loyalty",
}

STANDARD_ARRAY = [14, 12, 11, 10, 9, 7]
BOOSTED_FLOOR = 14


def get_modifier(score):
    if score <= 3: return -2
    elif score <= 7: return -1
    elif score <= 13: return 0
    elif score <= 17: return 1
    else: return 2


# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Skills
# ═══════════════════════════════════════════════════════════════════════════════

SKILLS = {
    "administer": {"attributes": ["intelligence", "charisma"]},
    "connect": {"attributes": ["charisma"]},
    "convince": {"attributes": ["charisma", "wisdom"]},
    "craft": {"attributes": ["intelligence", "dexterity"]},
    "exert": {"attributes": ["strength", "constitution"]},
    "heal": {"attributes": ["intelligence", "wisdom"]},
    "know": {"attributes": ["intelligence"]},
    "lead": {"attributes": ["charisma"]},
    "magic": {"attributes": ["intelligence", "wisdom"]},
    "notice": {"attributes": ["wisdom"]},
    "perform": {"attributes": ["charisma", "dexterity"]},
    "pray": {"attributes": ["wisdom", "charisma"]},
    "punch": {"attributes": ["strength", "dexterity"], "is_combat": True},
    "ride": {"attributes": ["dexterity", "wisdom"]},
    "sail": {"attributes": ["intelligence", "dexterity"]},
    "shoot": {"attributes": ["dexterity"], "is_combat": True},
    "sneak": {"attributes": ["dexterity", "intelligence"]},
    "stab": {"attributes": ["strength", "dexterity"], "is_combat": True},
    "survive": {"attributes": ["wisdom", "constitution"]},
    "trade": {"attributes": ["intelligence", "charisma"]},
    "work": {"attributes": ["varies"]},
}

SKILL_CHECK_DIFFICULTIES = {6: "Trivial", 8: "Routine", 10: "Challenging", 12: "Hard", 14: "Very Hard"}

# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Classes and progression
# ═══════════════════════════════════════════════════════════════════════════════

XP_TABLE = {1: 0, 2: 1500, 3: 3000, 4: 6000, 5: 12000, 6: 24000, 7: 48000, 8: 96000, 9: 192000, 10: 384000}

CLASSES = {
    "warrior": {
        "hit_die": "1d6+2",
        "abilities": {"killing_blow": "Add half level (rounded up) to damage and Shock", "veterans_luck": "Once/scene, force reroll of hit against you or turn miss into hit"},
        "progression": {
            1: {"hd": "1d6+2", "ab": 1, "focus": "1 Any + 1 Warrior"},
            2: {"hd": "2d6+4", "ab": 2, "focus": "+1 Any"},
            3: {"hd": "3d6+6", "ab": 3}, 4: {"hd": "4d6+8", "ab": 4},
            5: {"hd": "5d6+10", "ab": 5, "focus": "+1 Any"},
            6: {"hd": "6d6+12", "ab": 6}, 7: {"hd": "7d6+14", "ab": 7, "focus": "+1 Any"},
            8: {"hd": "8d6+16", "ab": 8}, 9: {"hd": "9d6+18", "ab": 9},
            10: {"hd": "10d6+20", "ab": 10, "focus": "+1 Any"},
        },
    },
    "expert": {
        "hit_die": "1d6",
        "abilities": {"masterful_expertise": "Once/scene, reroll failed non-combat skill check", "quick_learner": "+1 non-combat skill point per level"},
        "progression": {
            1: {"hd": "1d6", "ab": 0, "focus": "1 Any + 1 Non-Combat"},
            2: {"hd": "2d6", "ab": 1, "focus": "+1 Any"},
            3: {"hd": "3d6", "ab": 1}, 4: {"hd": "4d6", "ab": 2},
            5: {"hd": "5d6", "ab": 2, "focus": "+1 Any"},
            6: {"hd": "6d6", "ab": 3}, 7: {"hd": "7d6", "ab": 3, "focus": "+1 Any"},
            8: {"hd": "8d6", "ab": 4}, 9: {"hd": "9d6", "ab": 4},
            10: {"hd": "10d6", "ab": 5, "focus": "+1 Any"},
        },
    },
    "mage": {
        "hit_die": "1d6-1",
        "abilities": {"arcane_tradition": "Choose one magical tradition"},
        "progression": {
            1: {"hd": "1d6-1", "ab": 0, "focus": "1 Any"},
            2: {"hd": "2d6-2", "ab": 0, "focus": "+1 Any"},
            3: {"hd": "3d6-3", "ab": 0}, 4: {"hd": "4d6-4", "ab": 0},
            5: {"hd": "5d6-5", "ab": 1, "focus": "+1 Any"},
            6: {"hd": "6d6-6", "ab": 1}, 7: {"hd": "7d6-7", "ab": 1, "focus": "+1 Any"},
            8: {"hd": "8d6-8", "ab": 1}, 9: {"hd": "9d6-9", "ab": 1},
            10: {"hd": "10d6-10", "ab": 2, "focus": "+1 Any"},
        },
    },
    "adventurer": {
        "hit_die": "varies",
        "abilities": {"partial_classes": "Choose two partial classes"},
        "progression": None,
    },
}

ADVENTURER_PROGRESSION = {
    "partial_expert/partial_warrior": {
        1: {"hd": "1d6+2", "ab": 1, "focus": "1 Expert + 1 Warrior + 1 Any"},
        2: {"hd": "2d6+4", "ab": 2, "focus": "+1 Any"},
        3: {"hd": "3d6+6", "ab": 2}, 4: {"hd": "4d6+8", "ab": 3},
        5: {"hd": "5d6+10", "ab": 4, "focus": "+1 Any"},
        6: {"hd": "6d6+12", "ab": 5}, 7: {"hd": "7d6+14", "ab": 5, "focus": "+1 Any"},
        8: {"hd": "8d6+16", "ab": 6}, 9: {"hd": "9d6+18", "ab": 6},
        10: {"hd": "10d6+20", "ab": 7, "focus": "+1 Any"},
    },
    "partial_expert/partial_mage": {
        1: {"hd": "1d6", "ab": 0, "focus": "1 Expert + 1 Any"},
        2: {"hd": "2d6", "ab": 0, "focus": "+1 Any"},
        3: {"hd": "3d6", "ab": 0}, 4: {"hd": "4d6", "ab": 1},
        5: {"hd": "5d6", "ab": 1, "focus": "+1 Any"},
        6: {"hd": "6d6", "ab": 1}, 7: {"hd": "7d6", "ab": 2, "focus": "+1 Any"},
        8: {"hd": "8d6", "ab": 2}, 9: {"hd": "9d6", "ab": 2},
        10: {"hd": "10d6", "ab": 3, "focus": "+1 Any"},
    },
    "partial_mage/partial_warrior": {
        1: {"hd": "1d6+1", "ab": 1, "focus": "1 Warrior + 1 Any"},
        2: {"hd": "2d6+2", "ab": 1, "focus": "+1 Any"},
        3: {"hd": "3d6+3", "ab": 2}, 4: {"hd": "4d6+4", "ab": 2},
        5: {"hd": "5d6+5", "ab": 3, "focus": "+1 Any"},
        6: {"hd": "6d6+6", "ab": 4}, 7: {"hd": "7d6+7", "ab": 5, "focus": "+1 Any"},
        8: {"hd": "8d6+8", "ab": 5}, 9: {"hd": "9d6+9", "ab": 6},
        10: {"hd": "10d6+10", "ab": 6, "focus": "+1 Any"},
    },
}

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

# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Backgrounds
# ═══════════════════════════════════════════════════════════════════════════════

BACKGROUNDS = {
    1: {"name": "Artisan", "free_skill": "craft"},
    2: {"name": "Barbarian", "free_skill": "survive"},
    3: {"name": "Carter", "free_skill": "ride"},
    4: {"name": "Courtesan", "free_skill": "perform"},
    5: {"name": "Criminal", "free_skill": "sneak"},
    6: {"name": "Hunter", "free_skill": "shoot"},
    7: {"name": "Laborer", "free_skill": "exert"},
    8: {"name": "Merchant", "free_skill": "trade"},
    9: {"name": "Noble", "free_skill": "lead"},
    10: {"name": "Nomad", "free_skill": "ride"},
    11: {"name": "Peasant", "free_skill": "exert"},
    12: {"name": "Performer", "free_skill": "perform"},
    13: {"name": "Physician", "free_skill": "heal"},
    14: {"name": "Priest", "free_skill": "pray"},
    15: {"name": "Sailor", "free_skill": "sail"},
    16: {"name": "Scholar", "free_skill": "know"},
    17: {"name": "Slave", "free_skill": "exert"},
    18: {"name": "Soldier", "free_skill": "stab"},
    19: {"name": "Thug", "free_skill": "punch"},
    20: {"name": "Wanderer", "free_skill": "survive"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Weapons and equipment
# ═══════════════════════════════════════════════════════════════════════════════

WEAPONS = [
    {"name": "Axe, Hand", "damage": "1d6", "shock": "1/15", "traits": ["T"]},
    {"name": "Axe, War", "damage": "1d10", "shock": "3/15", "traits": ["2H"]},
    {"name": "Bow, Large", "damage": "1d8", "shock": None, "traits": ["2H", "R", "PM"]},
    {"name": "Bow, Small", "damage": "1d6", "shock": None, "traits": ["2H", "R", "PM"]},
    {"name": "Club", "damage": "1d4", "shock": None, "traits": ["T", "LL"]},
    {"name": "Crossbow", "damage": "1d10", "shock": None, "traits": ["2H", "SR", "PM"]},
    {"name": "Dagger", "damage": "1d4", "shock": "1/15", "traits": ["S", "T", "PM"]},
    {"name": "Halberd", "damage": "1d10", "shock": "2/15", "traits": ["2H", "L"]},
    {"name": "Mace", "damage": "1d6", "shock": "1/18", "traits": ["LL"]},
    {"name": "Spear, Heavy", "damage": "1d10", "shock": "2/15", "traits": ["2H"]},
    {"name": "Spear, Light", "damage": "1d6", "shock": "2/13", "traits": ["T"]},
    {"name": "Staff", "damage": "1d6", "shock": "1/13", "traits": ["2H", "LL"]},
    {"name": "Sword, Great", "damage": "1d12", "shock": "2/15", "traits": ["2H"]},
    {"name": "Sword, Long", "damage": "1d8", "shock": "2/13"},
    {"name": "Sword, Short", "damage": "1d6", "shock": "2/15"},
    {"name": "Unarmed", "damage": "1d2", "shock": None, "traits": ["LL"]},
]

EQUIPMENT_PACKAGES = {
    "armored_warrior": {"armor_ac": 11, "items": ["War shirt", "Short sword", "Small shield", "Dagger", "Backpack", "Rations (1 week)", "Waterskin"], "coins_sp": 10},
    "archer": {"armor_ac": 12, "items": ["Buff coat", "Small bow", "20 arrows", "Short sword", "Backpack", "Rations (1 week)", "Waterskin"], "coins_sp": 10},
    "skirmisher": {"armor_ac": 13, "items": ["Linothorax", "Light spear", "Dagger", "5 throwing blades", "Backpack", "Rations (1 week)", "Waterskin"], "coins_sp": 10},
    "scholar": {"armor_ac": 10, "items": ["Staff", "Dagger", "Writing kit", "Lantern", "2 flasks oil", "Backpack", "Rations (1 week)", "Waterskin"], "coins_sp": 20},
    "rogue": {"armor_ac": 12, "items": ["Buff coat", "Short sword", "Dagger", "Thieves' tools", "Rope (50')", "Grappling hook", "Backpack", "Rations (1 week)", "Waterskin"], "coins_sp": 10},
    "traveler": {"armor_ac": 10, "items": ["Light spear", "Dagger", "Lantern", "2 flasks oil", "Rope (50')", "Bedroll", "Backpack", "Rations (2 weeks)", "Waterskin"], "coins_sp": 15},
}

# ═══════════════════════════════════════════════════════════════════════════════
# TABLES — Encounter / travel / treasure
# ═══════════════════════════════════════════════════════════════════════════════

TERRAIN_MOVEMENT = {"road": 24, "plains": 18, "forest": 12, "hills": 12, "mountains": 6, "desert": 12, "swamp": 6, "coast": 18, "jungle": 6}
TERRAIN_ENCOUNTER_CHANCE = {"road": 1, "plains": 1, "forest": 2, "hills": 2, "mountains": 2, "desert": 1, "swamp": 3, "coast": 1, "jungle": 3}
TERRAIN_FORAGE_DIFFICULTY = {"road": 10, "plains": 8, "forest": 6, "hills": 8, "mountains": 10, "desert": 12, "swamp": 8, "coast": 8, "jungle": 6}
THREAT_HD_RANGE = {1: (1,2), 2: (1,3), 3: (2,4), 4: (3,6), 5: (4,8), 6: (5,10), 7: (6,10), 8: (8,12), 9: (8,12), 10: (10,12)}
THREAT_COUNT_RANGE = {1: (1,3), 2: (1,4), 3: (1,4), 4: (1,3), 5: (1,3), 6: (1,2), 7: (1,2), 8: (1,2), 9: (1,1), 10: (1,1)}
COIN_TABLES = {1: ("3d6", "0"), 2: ("3d6*5", "1d6"), 3: ("3d6*10", "2d6"), 4: ("3d6*20", "3d6*2"), 5: ("3d6*50", "3d6*5")}

CREATURE_TEMPLATES = [
    {"name": "Bandit", "hd": 1, "ac": 12, "atk": "+1", "dmg": "1d6", "shock": "1/15", "ml": 7, "type": "human"},
    {"name": "Bandit Leader", "hd": 3, "ac": 14, "atk": "+4", "dmg": "1d8+1", "shock": "2/15", "ml": 9, "type": "human"},
    {"name": "Guard", "hd": 1, "ac": 14, "atk": "+1", "dmg": "1d8", "shock": "2/15", "ml": 8, "type": "human"},
    {"name": "Soldier", "hd": 2, "ac": 15, "atk": "+3", "dmg": "1d8+1", "shock": "2/15", "ml": 9, "type": "human"},
    {"name": "Knight", "hd": 4, "ac": 17, "atk": "+6", "dmg": "1d10+2", "shock": "3/18", "ml": 10, "type": "human"},
    {"name": "Wolf", "hd": 2, "ac": 13, "atk": "+3", "dmg": "1d6", "shock": None, "ml": 7, "type": "animal"},
    {"name": "Bear", "hd": 5, "ac": 14, "atk": "+7", "dmg": "2d6", "shock": None, "ml": 8, "type": "animal"},
    {"name": "Giant Spider", "hd": 3, "ac": 13, "atk": "+4", "dmg": "1d8", "shock": None, "ml": 8, "type": "beast"},
    {"name": "Ogre", "hd": 4, "ac": 14, "atk": "+6", "dmg": "1d10+2", "shock": "3/15", "ml": 9, "type": "beast"},
    {"name": "Skeleton", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d6", "shock": None, "ml": 12, "type": "undead"},
    {"name": "Zombie", "hd": 2, "ac": 11, "atk": "+2", "dmg": "1d8", "shock": None, "ml": 12, "type": "undead"},
    {"name": "Ghoul", "hd": 3, "ac": 13, "atk": "+4", "dmg": "1d6", "shock": None, "ml": 10, "type": "undead"},
    {"name": "Wight", "hd": 5, "ac": 15, "atk": "+7", "dmg": "1d10", "shock": None, "ml": 11, "type": "undead"},
    {"name": "Guardian Automaton", "hd": 4, "ac": 17, "atk": "+6", "dmg": "1d10+1", "shock": "2/18", "ml": 12, "type": "automaton"},
    {"name": "Hunting Automaton", "hd": 6, "ac": 16, "atk": "+8", "dmg": "2d6+2", "shock": "3/15", "ml": 12, "type": "automaton"},
    {"name": "Outsider, Lesser", "hd": 4, "ac": 15, "atk": "+6", "dmg": "1d10", "shock": None, "ml": 10, "type": "outsider"},
    {"name": "Outsider, Greater", "hd": 8, "ac": 17, "atk": "+10", "dmg": "2d8", "shock": None, "ml": 11, "type": "outsider"},
]

TERRAIN_CREATURE_TYPES = {
    "forest": ["animal", "beast", "outsider"], "plains": ["animal", "human"],
    "mountains": ["animal", "beast", "automaton"], "desert": ["animal", "beast", "undead"],
    "swamp": ["beast", "undead", "outsider"], "coast": ["animal", "beast", "human"],
    "ruins": ["undead", "automaton", "outsider"], "urban": ["human"],
    "dungeon": ["undead", "automaton", "outsider", "beast"], "wilderness": ["animal", "beast", "human", "outsider"],
}

NPC_FIRST_NAMES = ["Aldric", "Brenna", "Callum", "Dara", "Elric", "Fenna", "Gareth", "Halla", "Isen", "Jora", "Kael", "Lira", "Maren", "Nils", "Orla", "Pell", "Riven", "Sela", "Thane", "Ulra", "Varn", "Wren", "Xara", "Yren", "Zara"]
NPC_SURNAMES = ["Ashford", "Blackwood", "Cragborn", "Deepwell", "Ember", "Foxglove", "Greysteel", "Hawkridge", "Ironhand", "Kettleburn", "Longshore", "Moorfield", "Northwind", "Oakenshield", "Pinefall", "Ravenscar", "Stonewall", "Thornwick", "Underhill", "Winterborn"]
NPC_TRAITS = ["cautious and observant", "bold and outspoken", "quiet and thoughtful", "cheerful and generous", "grim and pragmatic", "devious and charming", "loyal and stubborn", "nervous and talkative", "stoic and patient", "ambitious and cunning", "kind but naive", "bitter and resentful"]
NPC_SPEECH = ["speaks in short, clipped sentences", "uses formal, archaic phrasing", "peppers speech with nautical metaphors", "speaks very slowly and deliberately", "uses trade jargon", "tends to whisper important things", "laughs nervously between statements", "uses colorful local idioms", "speaks with military precision", "frequently quotes proverbs"]
NPC_PHRASES = ["As my grandmother used to say...", "Mark my words.", "The world is what it is.", "Fortune favors the prepared.", "There's always a price.", "In the old days...", "Between you and me...", "The gods willing.", "Nothing lasts forever."]
NPC_MOTIVATIONS = ["protect their family", "accumulate wealth", "seek revenge", "preserve ancient knowledge", "maintain order", "escape their past", "earn glory", "serve their faith", "find a cure", "discover the truth", "gain power", "simply survive"]
NPC_ROLES = {"minor": ["merchant", "farmer", "guard", "servant", "craftsperson", "beggar", "traveler"], "major": ["noble", "captain", "priest", "guild master", "scholar", "spy", "healer"], "faction_leader": ["lord", "warlord", "high priest", "archmage", "crime boss", "governor"]}

MUNDANE_ITEMS = ["Well-made rope (50')", "Sealed jar of preserved food", "Set of lockpicks", "Brass spyglass", "Bundle of torches (6)", "Healer's kit", "Waterproof map case", "Steel mirror", "Tinderbox", "Iron crowbar"]
MINOR_TREASURES = ["Silver ring with blue stone (10sp)", "Carved ivory figurine (15sp)", "Gold-chased dagger (25sp)", "Bolt of fine silk (20sp)", "Ancient coin collection (30sp)", "Silver holy symbol (15sp)", "Jeweled hairpin (20sp)", "Crystal vial of perfume (10sp)"]
MAJOR_TREASURES = ["Gold-and-sapphire necklace (200sp)", "Jeweled crown fragment (150sp)", "Masterwork longsword (100sp)", "Bolt of cloth-of-gold (175sp)", "Large cut gemstone (250sp)", "Golden tableware set (200sp)"]

TRAVEL_EVENTS = {1: "Harsh weather slows travel", 2: "Notable landmark spotted", 3: "Fresh tracks or signs of passage", 4: "Natural shelter found", 5: "Water source discovered", 6: "Remains of old camp or ruins", 7: "Another traveler encountered", 8: "Uneventful travel"}

# ═══════════════════════════════════════════════════════════════════════════════
# CORE — Dice rolling
# ═══════════════════════════════════════════════════════════════════════════════

def parse_dice(expression):
    expression = expression.strip().lower()
    m = re.match(r'^(\d+)d(\d+)\s*([+\-]\s*\d+)?$', expression)
    if not m:
        raise ValueError(f"Invalid dice notation: '{expression}'")
    return int(m.group(1)), int(m.group(2)), int(m.group(3).replace(' ', '')) if m.group(3) else 0


def roll_dice(count, sides):
    return [random.randint(1, sides) for _ in range(count)]


def roll(expression):
    count, sides, modifier = parse_dice(expression)
    rolls = roll_dice(count, sides)
    dice_sum = sum(rolls)
    total = dice_sum + modifier
    rolls_str = "+".join(str(r) for r in rolls)
    if modifier > 0: trace = f"[{rolls_str}]+{modifier} = {total}"
    elif modifier < 0: trace = f"[{rolls_str}]{modifier} = {total}"
    else: trace = f"[{rolls_str}] = {total}"
    return {"expression": expression, "rolls": rolls, "modifier": modifier, "total": total, "arithmetic_trace": trace}


def roll_check(modifier=0, target=None):
    rolls = roll_dice(2, 6)
    total = sum(rolls) + modifier
    result = {"rolls": rolls, "modifier": modifier, "total": total, "arithmetic_trace": f"[{rolls[0]}+{rolls[1]}]+{modifier} = {total}"}
    if target is not None:
        result["target"] = target
        result["success"] = total >= target
        result["margin"] = total - target
    return result


def roll_save(save_target):
    die = roll_dice(1, 20)[0]
    return {"roll": die, "target": save_target, "success": die >= save_target, "arithmetic_trace": f"d20=[{die}] vs target {save_target}"}


def roll_attack(attack_bonus):
    die = roll_dice(1, 20)[0]
    total = die + attack_bonus
    return {"die": die, "bonus": attack_bonus, "total": total, "natural_20": die == 20, "natural_1": die == 1, "arithmetic_trace": f"d20=[{die}]+{attack_bonus} = {total}"}


# ═══════════════════════════════════════════════════════════════════════════════
# COMBAT — Attack resolution, shock, morale
# ═══════════════════════════════════════════════════════════════════════════════

def parse_shock(shock_str):
    if shock_str is None or shock_str == "None" or shock_str == "none":
        return None
    parts = shock_str.split("/")
    if len(parts) != 2: return None
    return {"damage": int(parts[0]), "ac_threshold": None if parts[1] == "-" else int(parts[1])}


def resolve_shock(shock_str, attribute_mod=0, target_ac=10, killing_blow_bonus=0):
    parsed = parse_shock(shock_str)
    if parsed is None:
        return {"shock_applied": False, "shock_damage": 0, "reason": "No shock"}
    if parsed["ac_threshold"] is not None and target_ac > parsed["ac_threshold"]:
        return {"shock_applied": False, "shock_damage": 0, "reason": f"AC {target_ac} > threshold {parsed['ac_threshold']}"}
    total = max(0, parsed["damage"] + attribute_mod + killing_blow_bonus)
    return {"shock_applied": True, "shock_damage": total, "reason": f"Shock {parsed['damage']}+{attribute_mod}(attr)+{killing_blow_bonus}(KB) = {total}"}


def resolve_attack(attacker, defender):
    ab = attacker["attack_bonus"]
    skill = attacker["skill_level"]
    attr_mod = attacker["attribute_mod"]
    weapon = attacker["weapon"]
    kb_bonus = attacker.get("killing_blow_bonus", 0)
    target_ac = defender["armor_class"]
    total_bonus = ab + skill + attr_mod
    atk = roll_attack(total_bonus)
    hit = atk["total"] >= target_ac or atk["natural_20"]
    if atk["natural_1"]: hit = False
    result = {"hit_roll": atk["die"], "total_roll": atk["total"], "attack_bonus_breakdown": f"AB={ab} + Skill={skill} + Attr={attr_mod} = +{total_bonus}", "target_ac": target_ac, "natural_20": atk["natural_20"], "natural_1": atk["natural_1"], "hit": hit, "damage": 0, "shock_applied": False, "shock_damage": 0, "arithmetic_trace": atk["arithmetic_trace"]}
    if hit:
        dmg = roll(weapon["damage"])
        base_damage = max(1, dmg["total"] + attr_mod + kb_bonus)
        result["damage"] = base_damage
        result["damage_roll"] = dmg["rolls"]
        result["damage_trace"] = f"{weapon['damage']}={dmg['total']}+{attr_mod}(attr)+{kb_bonus}(KB) = {base_damage}"
        result["arithmetic_trace"] += f" → HIT! Damage: {result['damage_trace']}"
    else:
        shock = resolve_shock(weapon.get("shock"), attr_mod, target_ac, kb_bonus)
        result["shock_applied"] = shock["shock_applied"]
        result["shock_damage"] = shock["shock_damage"]
        if shock["shock_applied"]:
            result["damage"] = shock["shock_damage"]
            result["arithmetic_trace"] += f" → MISS, Shock: {shock['reason']}"
        else:
            result["arithmetic_trace"] += f" → MISS. {shock['reason']}"
    new_hp = max(0, defender["hp"]["current"] - result["damage"])
    result["target_hp_before"] = defender["hp"]["current"]
    result["target_hp_after"] = new_hp
    result["target_down"] = new_hp <= 0
    return result


def check_morale(morale_score):
    rolls = roll_dice(2, 6)
    total = sum(rolls)
    routs = total > morale_score
    return {"rolls": rolls, "total": total, "morale_score": morale_score, "routs": routs, "arithmetic_trace": f"2d6=[{rolls[0]}+{rolls[1]}]={total} vs ML {morale_score} → {'ROUT' if routs else 'HOLDS'}"}


# ═══════════════════════════════════════════════════════════════════════════════
# MAGIC — Spell casting and Effort
# ═══════════════════════════════════════════════════════════════════════════════

def cast_spell(spell_name, caster_level, tradition, effort_current, system_strain, system_strain_max):
    max_level = min(5, (caster_level + 1) // 2)
    spell_level = 1  # Default; caller should specify if known
    if effort_current < 1:
        return {"success": False, "error": "No Effort available", "spell": spell_name, "effort_current": effort_current}
    return {"success": True, "spell": spell_name, "spell_level": spell_level, "tradition": tradition, "effort_committed": 1, "effort_before": effort_current, "effort_after": effort_current - 1, "arithmetic_trace": f"Cast {spell_name}: Effort {effort_current}→{effort_current - 1}"}


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER — Creation and level-up
# ═══════════════════════════════════════════════════════════════════════════════

_CHARGEN_SKILL_CAP = 1

def generate_attributes(method="boosted_3d6", assignments=None):
    attr_names = list(ATTRIBUTES.keys())
    if method == "boosted_3d6":
        if assignments:
            return dict(assignments)
        attrs = {n: sum(random.randint(1, 6) for _ in range(3)) for n in attr_names}
        lowest = min(attrs, key=attrs.get)
        if attrs[lowest] < BOOSTED_FLOOR:
            attrs[lowest] = BOOSTED_FLOOR
        return attrs
    elif method == "standard_array":
        values = list(STANDARD_ARRAY)
        random.shuffle(values)
        return dict(zip(attr_names, values))
    elif method == "roll_3d6":
        return {n: sum(random.randint(1, 6) for _ in range(3)) for n in attr_names}
    raise ValueError(f"Unknown method: {method}")


def calculate_saving_throws(level, attributes):
    s, d, c = get_modifier(attributes["strength"]), get_modifier(attributes["dexterity"]), get_modifier(attributes["constitution"])
    i, w, ch = get_modifier(attributes["intelligence"]), get_modifier(attributes["wisdom"]), get_modifier(attributes["charisma"])
    return {"physical": 16 - (level + max(s, c)), "evasion": 16 - (level + max(i, d)), "mental": 16 - (level + max(w, ch)), "luck": 16 - level}


def create_character(name, class_name, background_id, method="boosted_3d6", partial_classes=None, tradition=None, foci=None, spells=None, equipment_package=None, free_skill=None, attribute_assignments=None, background_skills=None, physical_boost=None, mental_boost=None):
    if class_name not in CLASSES: raise ValueError(f"Unknown class: {class_name}")
    if background_id not in BACKGROUNDS: raise ValueError(f"Unknown background: {background_id}")
    attributes = generate_attributes(method, attribute_assignments)
    if physical_boost and mental_boost:
        attributes[physical_boost] = min(18, attributes[physical_boost] + 2)
        attributes[mental_boost] = min(18, attributes[mental_boost] + 2)
    skills_dict = {s: -1 for s in SKILLS.keys()}
    bg = BACKGROUNDS[background_id]
    if background_skills:
        for sk in background_skills:
            if sk in skills_dict: skills_dict[sk] = min(_CHARGEN_SKILL_CAP, skills_dict[sk] + 1)
    else:
        fs = bg["free_skill"]
        if fs in skills_dict: skills_dict[fs] = min(_CHARGEN_SKILL_CAP, skills_dict[fs] + 1)
    if free_skill and free_skill in skills_dict:
        skills_dict[free_skill] = min(_CHARGEN_SKILL_CAP, skills_dict[free_skill] + 1)
    con_mod = get_modifier(attributes["constitution"])
    dex_mod = get_modifier(attributes["dexterity"])
    level = 1
    if class_name == "adventurer" and partial_classes:
        combo_key = "/".join(sorted(f"partial_{p}" for p in partial_classes))
        if combo_key not in ADVENTURER_PROGRESSION:
            raise ValueError(f"Unknown adventurer combo: {combo_key}")
        prog = ADVENTURER_PROGRESSION[combo_key]
        hit_die = prog[1]["hd"]
        attack_bonus = prog[1]["ab"]
    else:
        cls = CLASSES[class_name]
        hit_die = cls["progression"][1]["hd"]
        attack_bonus = cls["progression"][1]["ab"]
    count, sides, mod = parse_dice(hit_die)
    hp_total = max(1, sum(random.randint(1, sides) for _ in range(count)) + mod + con_mod)
    saves = calculate_saving_throws(level, attributes)
    armor_class = 10 + dex_mod
    if equipment_package and equipment_package in EQUIPMENT_PACKAGES:
        pkg = EQUIPMENT_PACKAGES[equipment_package]
        pkg_ac = pkg.get("armor_ac", 10)
        if pkg_ac > 10: armor_class = max(armor_class, pkg_ac + dex_mod)
    # Effort for mages
    int_mod = get_modifier(attributes["intelligence"])
    wis_mod = get_modifier(attributes["wisdom"])
    cha_mod = get_modifier(attributes["charisma"])
    is_mage = class_name == "mage"
    is_partial_mage = class_name == "adventurer" and partial_classes and "mage" in partial_classes
    effort_max = max(1, 1 + max(int_mod, wis_mod, cha_mod)) if (is_mage or is_partial_mage) else 0
    readied = list(EQUIPMENT_PACKAGES.get(equipment_package, {}).get("items", []))
    coins_sp = EQUIPMENT_PACKAGES.get(equipment_package, {}).get("coins_sp", 0)
    char = {
        "name": name, "class": class_name, "level": level, "xp": 0,
        "background": bg["name"], "attributes": attributes,
        "hp": {"current": hp_total, "max": hp_total},
        "attack_bonus": attack_bonus, "armor_class": armor_class,
        "saving_throws": saves, "skills": skills_dict,
        "system_strain": {"current": 0, "max": attributes["constitution"]},
        "effort": {"current": 0, "max": effort_max},
        "equipment": {"readied": readied, "stowed": [], "coins": {"copper": 0, "silver": coins_sp, "gold": 0}},
        "foci": list(foci) if foci else [], "class_abilities": list(CLASSES.get(class_name, {}).get("abilities", {}).keys()),
    }
    if class_name == "adventurer" and partial_classes:
        char["partial_classes"] = sorted(partial_classes)
    if tradition: char["tradition"] = tradition
    char["spells_known"] = list(spells) if spells else []
    return char


def level_up(character, target_level):
    current_level = character.get("level", 1)
    if target_level <= current_level:
        return {"error": f"Target {target_level} must be > current {current_level}", "character": character}
    class_name = character["class"]
    partial_classes = character.get("partial_classes")
    changes = []
    if class_name == "adventurer" and partial_classes:
        combo_key = "/".join(sorted(f"partial_{p}" for p in partial_classes))
        prog = ADVENTURER_PROGRESSION.get(combo_key)
    elif class_name in CLASSES and CLASSES[class_name].get("progression"):
        prog = CLASSES[class_name]["progression"]
    else:
        return {"error": f"No progression for {class_name}", "character": character}
    if not prog:
        return {"error": f"No progression for {class_name}", "character": character}
    for lvl in range(current_level + 1, min(target_level + 1, 11)):
        if lvl not in prog: break
        entry = prog[lvl]
        con_mod = get_modifier(character["attributes"]["constitution"])
        count, sides, mod = parse_dice(entry["hd"])
        new_hp = max(character["hp"]["max"] + 1, max(1, sum(random.randint(1, sides) for _ in range(count)) + mod + con_mod))
        gained = new_hp - character["hp"]["max"]
        character["hp"]["max"] = new_hp
        character["hp"]["current"] += gained
        character["attack_bonus"] = entry["ab"]
        character["level"] = lvl
        character["saving_throws"] = calculate_saving_throws(lvl, character["attributes"])
        changes.append(f"L{lvl}: HP +{gained} (max {new_hp}), AB {entry['ab']}")
        if entry.get("focus"): changes.append(f"L{lvl}: Focus pick: {entry['focus']}")
    return {"character": character, "changes": changes, "old_level": current_level, "new_level": character["level"]}


# ═══════════════════════════════════════════════════════════════════════════════
# ENCOUNTER — Random encounter generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_encounter(terrain, threat_level):
    threat_level = max(1, min(10, threat_level))
    count_min, count_max = THREAT_COUNT_RANGE.get(threat_level, (1, 3))
    count = random.randint(count_min, count_max)
    valid_types = TERRAIN_CREATURE_TYPES.get(terrain, ["animal", "human"])
    hd_min, hd_max = THREAT_HD_RANGE.get(threat_level, (1, 4))
    candidates = [c for c in CREATURE_TEMPLATES if c.get("type", "") in valid_types and hd_min <= c.get("hd", 1) <= hd_max]
    if not candidates:
        candidates = [{"name": "Wild Beast", "hd": max(1, hd_min), "ac": 13, "atk": "+2", "dmg": "1d6", "shock": None, "ml": 7, "type": "animal"}]
    combatants = []
    for i in range(count):
        creature = random.choice(candidates)
        hp = sum(roll_dice(creature["hd"], 8))
        combatants.append({"id": f"enemy_{i+1}", "name": creature["name"], "stats": creature, "hp_current": hp, "hp_max": hp, "zone": "near"})
    names = {}
    for c in combatants:
        names[c["name"]] = names.get(c["name"], 0) + 1
    desc = ", ".join(f"{v} {k}{'s' if v > 1 else ''}" if v > 1 else f"a {k}" for k, v in names.items())
    return {"terrain": terrain, "threat_level": threat_level, "creature_count": count, "combatants": combatants, "description": f"Encounter in {terrain}: {desc}", "arithmetic_trace": f"Encounter: {count} creatures in {terrain} (threat {threat_level})"}


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL — Overland travel resolution
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_travel(terrain, days, supplies, forage_modifier=0, threat_level=3):
    movement = TERRAIN_MOVEMENT.get(terrain, 18)
    total_distance = 0
    current_supplies = supplies
    log = []
    for day in range(1, days + 1):
        day_r = {"day": day, "distance": movement, "events": []}
        if current_supplies > 0:
            current_supplies -= 1
        else:
            diff = TERRAIN_FORAGE_DIFFICULTY.get(terrain, 8)
            forage = roll_check(modifier=forage_modifier, target=diff)
            rations = 1 if forage["success"] else 0
            if forage.get("margin", 0) >= 4: rations = 2
            current_supplies += rations
            day_r["forage"] = {"success": forage["success"], "rations": rations}
            day_r["events"].append(f"Foraging: {'found' if forage['success'] else 'failed'}")
        enc_roll = roll_dice(1, 6)[0]
        chance = TERRAIN_ENCOUNTER_CHANCE.get(terrain, 1)
        has_enc = enc_roll <= chance
        day_r["has_encounter"] = has_enc
        if has_enc: day_r["events"].append("Random encounter!")
        event_roll = roll_dice(1, 8)[0]
        day_r["events"].append(TRAVEL_EVENTS[event_roll])
        day_r["supplies_remaining"] = current_supplies
        total_distance += movement
        log.append(day_r)
    enc_count = sum(1 for d in log if d.get("has_encounter"))
    return {"terrain": terrain, "days": days, "total_distance": total_distance, "movement_per_day": movement, "supplies_start": supplies, "supplies_end": current_supplies, "travel_log": log, "encounters": enc_count, "arithmetic_trace": f"Travel {days}d through {terrain}: {total_distance}mi, {enc_count} encounter(s)"}


# ═══════════════════════════════════════════════════════════════════════════════
# NPC — Generation and reaction rolls
# ═══════════════════════════════════════════════════════════════════════════════

def generate_npc(importance="minor", region="unknown", tag_count=1):
    name = f"{random.choice(NPC_FIRST_NAMES)} {random.choice(NPC_SURNAMES)}"
    role = random.choice(NPC_ROLES.get(importance, NPC_ROLES["minor"]))
    personality = random.choice(NPC_TRAITS)
    speech = random.choice(NPC_SPEECH)
    phrase = random.choice(NPC_PHRASES)
    motivation = random.choice(NPC_MOTIVATIONS)
    return {"id": f"npc_{random.randint(100, 999)}", "name": name, "role": role, "importance": importance, "disposition": "neutral", "motivation": motivation, "personality_traits": personality, "speech_patterns": speech, "key_phrases": [phrase], "voice_card": f"{name} is {personality}. They {speech}. Often says: \"{phrase}\"", "last_seen": region, "arithmetic_trace": f"Generated NPC: {name} ({role}, {importance})"}


def reaction_roll(modifier=0):
    rolls = roll_dice(2, 6)
    total = sum(rolls) + modifier
    if total <= 3: disp, desc = "hostile", "Hostile — attacks if not overpowered"
    elif total <= 5: disp, desc = "unfriendly", "Hostile — may attack if provoked"
    elif total <= 8: disp, desc = "uncertain", "Uncertain — can be convinced"
    elif total <= 10: disp, desc = "neutral", "Neutral — open to negotiation"
    elif total == 11: disp, desc = "friendly", "Friendly — inclined to help"
    else: disp, desc = "enthusiastic", "Enthusiastically friendly"
    return {"rolls": rolls, "modifier": modifier, "total": total, "disposition": disp, "description": desc, "arithmetic_trace": f"Reaction: 2d6=[{rolls[0]}+{rolls[1]}]+{modifier} = {total} → {disp}"}


# ═══════════════════════════════════════════════════════════════════════════════
# TREASURE — Treasure generation
# ═══════════════════════════════════════════════════════════════════════════════

def roll_treasure(tier):
    tier = max(1, min(5, tier))
    silver_expr, gold_expr = COIN_TABLES.get(tier, COIN_TABLES[1])
    silver = gold = 0
    if silver_expr != "0":
        if "*" in silver_expr:
            base, mult = silver_expr.split("*")
            silver = roll(base)["total"] * int(mult)
        else:
            silver = roll(silver_expr)["total"]
    if gold_expr != "0":
        if "*" in gold_expr:
            base, mult = gold_expr.split("*")
            gold = roll(base)["total"] * int(mult)
        else:
            gold = roll(gold_expr)["total"]
    items = random.sample(MUNDANE_ITEMS, min(random.randint(1, 2), len(MUNDANE_ITEMS)))
    if tier >= 2:
        n = random.randint(0, min(tier - 1, 2))
        if n: items.extend(random.sample(MINOR_TREASURES, min(n, len(MINOR_TREASURES))))
    if tier >= 4:
        if random.randint(0, 1): items.extend(random.sample(MAJOR_TREASURES, 1))
    total_value = silver + gold * 10
    return {"tier": tier, "coins": {"silver": silver, "gold": gold}, "items": items, "estimated_value_sp": total_value, "arithmetic_trace": f"Treasure (tier {tier}): {silver}sp + {gold}gp + {len(items)} items = ~{total_value}sp"}


# ═══════════════════════════════════════════════════════════════════════════════
# SCENE — Scene generation (fallback-based)
# ═══════════════════════════════════════════════════════════════════════════════

SCENE_SEEDS = {
    "wilderness": ["A clearing in dense woodland, old stone markers half-hidden in undergrowth.", "A rocky hilltop with commanding views.", "A dried riverbed with animal tracks.", "A cave mouth in a cliff face, dark and unwelcoming.", "A ford across a sluggish river, wooden posts marking the crossing.", "A stand of ancient trees, their trunks wider than a man's armspan."],
    "ruin": ["Crumbling stone walls mark an ancient structure.", "A partially collapsed tower, upper floors open to sky.", "An underground chamber accessible through a broken floor.", "An overgrown courtyard with a dry fountain.", "A gallery of faded murals, the paint still vivid in places.", "A sealed door of Legacy metal, untouched by ages."],
    "community": ["A small village with timber buildings around a central well.", "A fortified trading post at a crossroads.", "A riverside hamlet with a ferry crossing.", "A hillside settlement built into terraced slopes.", "A walled market town with a gate tax.", "A fishing village where the nets are always drying."],
}

def generate_scene(scene_type, tag_count=2, threat_level=3):
    descriptions = SCENE_SEEDS.get(scene_type, SCENE_SEEDS["wilderness"])
    desc = random.choice(descriptions)
    return {"scene_type": scene_type, "threat_level": threat_level, "description": desc, "arithmetic_trace": f"Scene ({scene_type}), threat {threat_level}"}


# ═══════════════════════════════════════════════════════════════════════════════
# DUNGEON — Procedural dungeon generation
# ═══════════════════════════════════════════════════════════════════════════════

DUNGEON_THEMES = ["tomb", "laboratory", "prison", "temple", "mine", "fortress", "library", "warren"]
ROOM_FEATURES = ["collapsed ceiling", "pool of stagnant water", "bas-relief carvings", "rusted machinery", "phosphorescent fungi", "broken furniture", "ancient graffiti", "scattered bones", "sealed alcove", "ventilation shaft"]
ROOM_CONTENTS = ["empty", "empty", "monster", "monster", "trap", "treasure", "puzzle", "monster + treasure"]

def generate_dungeon(depth, theme=None):
    if not theme: theme = random.choice(DUNGEON_THEMES)
    rooms = max(3, depth * 2 + random.randint(1, 3))
    dungeon_rooms = []
    for i in range(rooms):
        content = random.choice(ROOM_CONTENTS)
        feature = random.choice(ROOM_FEATURES)
        room = {"room": i + 1, "feature": feature, "content": content}
        if "monster" in content:
            threat = min(10, depth + 2)
            room["threat_level"] = threat
        if "treasure" in content:
            room["treasure_tier"] = min(5, max(1, depth))
        dungeon_rooms.append(room)
    return {"theme": theme, "depth": depth, "room_count": rooms, "rooms": dungeon_rooms, "arithmetic_trace": f"Dungeon ({theme}): depth {depth}, {rooms} rooms"}


# ═══════════════════════════════════════════════════════════════════════════════
# WORLD TICK — Time advancement
# ═══════════════════════════════════════════════════════════════════════════════

def advance_world(days_elapsed, clocks=None, factions=None, current_day=1):
    clocks = clocks or []
    factions = factions or []
    new_day = current_day + days_elapsed
    clock_events = []
    for clock in clocks:
        progress = clock.get("progress", 0)
        max_val = clock.get("max", 6)
        if progress < max_val:
            advance = days_elapsed // max(1, clock.get("interval_days", 7))
            if advance > 0:
                new_progress = min(max_val, progress + advance)
                clock_events.append({"clock": clock.get("name", "unnamed"), "old": progress, "new": new_progress, "completed": new_progress >= max_val})
    return {"days_elapsed": days_elapsed, "old_day": current_day, "new_day": new_day, "clock_events": clock_events, "arithmetic_trace": f"World-tick: +{days_elapsed} days (day {current_day}→{new_day}), {len(clock_events)} clock events"}


# ═══════════════════════════════════════════════════════════════════════════════
# GM MOVES — Anti-stagnation system
# ═══════════════════════════════════════════════════════════════════════════════

TIER2_THRESHOLD = 5
TIER3_THRESHOLD = 8

def select_move(command_name, command_result, turns_since_hard_move=0, telegraphed_threats=None):
    telegraphed_threats = telegraphed_threats or []
    # Check forced escalation
    if turns_since_hard_move >= TIER3_THRESHOLD:
        return {"tier": 3, "move_type": "world_event", "directive": "The world acts. Advance a clock, fire a faction action, or shift the environment.", "counter_action": "reset", "arithmetic_trace": f"Forced Tier 3 (turns_since={turns_since_hard_move})"}
    if turns_since_hard_move >= TIER2_THRESHOLD:
        active = [t for t in telegraphed_threats if t.get("status") == "active"]
        if active:
            target = sorted(active, key=lambda t: t.get("turn_created", 0))[0]
            return {"tier": 2, "move_type": "telegraph_escalates", "target": target.get("id"), "directive": f"Escalate telegraph '{target.get('description', '')}' into hard consequence.", "counter_action": "reset", "arithmetic_trace": f"Forced Tier 2: escalate telegraph (turns_since={turns_since_hard_move})"}
        return {"tier": 2, "move_type": "world_consequence", "directive": "A consequence touches the PC directly.", "counter_action": "reset", "arithmetic_trace": f"Forced Tier 2 (turns_since={turns_since_hard_move})"}
    # Natural move based on command result
    success = command_result.get("success", command_result.get("hit", True))
    margin = command_result.get("margin", 0)
    if command_name == "attack":
        if command_result.get("target_down"):
            return {"tier": 1, "move_type": "combat_aftermath" if not command_result.get("enemies_remain") else "target_down_foreshadow", "directive": "Foreshadow what comes next.", "counter_action": "increment", "arithmetic_trace": "Attack: target down. Tier 1."}
        return {"tier": 1, "move_type": "battlefield_evolves", "directive": "The battlefield shifts — terrain, enemy capability, or position changes.", "counter_action": "increment", "arithmetic_trace": "Attack: combat continues. Tier 1."}
    if command_name == "skill-check":
        if not success and margin is not None and margin <= -5:
            return {"tier": 2, "move_type": "catastrophic_failure", "directive": "Catastrophic failure. Consequence is binding.", "forced_consequence": True, "counter_action": "reset", "arithmetic_trace": f"Skill-check catastrophic (margin {margin}). Tier 2."}
        if success:
            return {"tier": 1, "move_type": "foreshadow", "directive": "Success, but something stirs.", "counter_action": "increment", "arithmetic_trace": f"Skill-check success (margin +{margin}). Tier 1."}
        return {"tier": 1, "move_type": "failure_telegraph", "directive": "Failure. Telegraph the consequence.", "counter_action": "increment", "arithmetic_trace": f"Skill-check fail (margin {margin}). Tier 1."}
    if command_name == "save":
        if not success and margin is not None and margin <= -3:
            return {"tier": 2, "move_type": "severe_save_failure", "directive": "Severe save failure. Consequence lands.", "forced_consequence": True, "counter_action": "reset", "arithmetic_trace": f"Save severe failure (margin {margin}). Tier 2."}
        return {"tier": 1, "move_type": "environment_reacts", "directive": "The threat was resolved, but the scene changed.", "counter_action": "increment", "arithmetic_trace": f"Save {'success' if success else 'failure'} (margin {margin}). Tier 1."}
    if command_name == "reaction-roll":
        if command_result.get("disposition") == "hostile":
            return {"tier": 2, "move_type": "npc_hostile", "directive": "NPC acts against the PC.", "counter_action": "reset", "arithmetic_trace": "Reaction: hostile. Tier 2."}
        return {"tier": 1, "move_type": "npc_interaction", "directive": f"NPC is {command_result.get('disposition', 'neutral')}.", "counter_action": "increment", "arithmetic_trace": f"Reaction: {command_result.get('disposition')}. Tier 1."}
    # Default / narrative
    return {"tier": 1, "move_type": "world_breathes", "directive": "The world breathes. Reveal something through scene detail.", "counter_action": "increment", "arithmetic_trace": f"{command_name or 'narrative'}. Tier 1."}


# ═══════════════════════════════════════════════════════════════════════════════
# CLI — Argument parser and dispatch
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="WWN RPG Engine")
    parser.add_argument("--seed", type=int, help="RNG seed for reproducibility")
    subs = parser.add_subparsers(dest="command")
    seed_parent = argparse.ArgumentParser(add_help=False)
    seed_parent.add_argument("--seed", type=int)

    # roll
    p = subs.add_parser("roll", parents=[seed_parent])
    p.add_argument("expression")

    # skill-check
    p = subs.add_parser("skill-check", parents=[seed_parent])
    p.add_argument("--attribute-mod", type=int, required=True)
    p.add_argument("--skill-level", type=int, required=True)
    p.add_argument("--difficulty", type=int, required=True)

    # save
    p = subs.add_parser("save", parents=[seed_parent])
    p.add_argument("--type", type=str, required=True, choices=["physical", "evasion", "mental"])
    p.add_argument("--level", type=int, required=True)
    p.add_argument("--modifier", type=int, required=True)

    # attack
    p = subs.add_parser("attack", parents=[seed_parent])
    p.add_argument("--attack-bonus", type=int, required=True)
    p.add_argument("--skill-level", type=int, required=True)
    p.add_argument("--attribute-mod", type=int, required=True)
    p.add_argument("--weapon-damage", type=str, required=True)
    p.add_argument("--shock", type=str, default="none")
    p.add_argument("--target-ac", type=int, required=True)
    p.add_argument("--target-hp", type=int, required=True)
    p.add_argument("--killing-blow", type=int, default=0)

    # cast-spell
    p = subs.add_parser("cast-spell", parents=[seed_parent])
    p.add_argument("--spell-name", type=str, required=True)
    p.add_argument("--caster-level", type=int, required=True)
    p.add_argument("--tradition", type=str, required=True)
    p.add_argument("--current-effort", type=int, required=True)
    p.add_argument("--system-strain", type=int, required=True)
    p.add_argument("--system-strain-max", type=int, required=True)

    # encounter
    p = subs.add_parser("encounter", parents=[seed_parent])
    p.add_argument("--terrain", type=str, required=True)
    p.add_argument("--threat-level", type=int, required=True)

    # travel
    p = subs.add_parser("travel", parents=[seed_parent])
    p.add_argument("--terrain", type=str, required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--supplies", type=int, required=True)
    p.add_argument("--forage-mod", type=int, default=0)
    p.add_argument("--threat-level", type=int, default=3)

    # generate-scene
    p = subs.add_parser("generate-scene", parents=[seed_parent])
    p.add_argument("--scene-type", type=str, required=True, choices=["wilderness", "ruin", "community"])
    p.add_argument("--tag-count", type=int, default=2)
    p.add_argument("--threat-level", type=int, default=3)

    # treasure
    p = subs.add_parser("treasure", parents=[seed_parent])
    p.add_argument("--tier", type=int, required=True, choices=[1, 2, 3, 4, 5])

    # generate-npc
    p = subs.add_parser("generate-npc", parents=[seed_parent])
    p.add_argument("--importance", type=str, default="minor", choices=["minor", "major", "faction_leader"])
    p.add_argument("--region", type=str, default="unknown")
    p.add_argument("--tags", type=int, default=1)

    # reaction-roll
    p = subs.add_parser("reaction-roll", parents=[seed_parent])
    p.add_argument("--modifier", type=int, default=0)

    # morale
    p = subs.add_parser("morale", parents=[seed_parent])
    p.add_argument("--morale-score", type=int, required=True)

    # world-tick
    p = subs.add_parser("world-tick", parents=[seed_parent])
    p.add_argument("--days", type=int, required=True)

    # create-character
    p = subs.add_parser("create-character", parents=[seed_parent])
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--class", type=str, required=True, dest="char_class", choices=["warrior", "expert", "mage", "adventurer"])
    p.add_argument("--background", type=int, required=True)
    p.add_argument("--method", type=str, default="boosted_3d6")
    p.add_argument("--partial-classes", type=str, default=None)
    p.add_argument("--tradition", type=str, default=None)
    p.add_argument("--foci", type=str, default=None)
    p.add_argument("--spells", type=str, default=None)
    p.add_argument("--equipment-package", type=str, default=None)
    p.add_argument("--free-skill", type=str, default=None)

    # generate-dungeon
    p = subs.add_parser("generate-dungeon", parents=[seed_parent])
    p.add_argument("--depth", type=int, required=True)
    p.add_argument("--theme", type=str, default=None)

    # select-move
    p = subs.add_parser("select-move", parents=[seed_parent])
    p.add_argument("--command-name", type=str, required=True)
    p.add_argument("--result-json", type=str, required=True)
    p.add_argument("--turns-since-hard-move", type=int, default=0)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.seed is not None:
        random.seed(args.seed)

    try:
        if args.command == "roll":
            result = roll(args.expression)
        elif args.command == "skill-check":
            modifier = args.attribute_mod + args.skill_level
            result = roll_check(modifier=modifier, target=args.difficulty)
            result.update({"attribute_mod": args.attribute_mod, "skill_level": args.skill_level, "difficulty": args.difficulty})
        elif args.command == "save":
            save_target = 16 - (args.level + args.modifier)
            result = roll_save(save_target)
            result.update({"save_type": args.type, "level": args.level, "modifier": args.modifier})
        elif args.command == "attack":
            attacker = {"attack_bonus": args.attack_bonus, "skill_level": args.skill_level, "attribute_mod": args.attribute_mod, "weapon": {"damage": args.weapon_damage, "shock": args.shock if args.shock != "none" else None}, "killing_blow_bonus": args.killing_blow or 0}
            defender = {"armor_class": args.target_ac, "hp": {"current": args.target_hp, "max": args.target_hp}}
            result = resolve_attack(attacker, defender)
        elif args.command == "cast-spell":
            result = cast_spell(args.spell_name, args.caster_level, args.tradition, args.current_effort, args.system_strain, args.system_strain_max)
        elif args.command == "encounter":
            result = generate_encounter(args.terrain, args.threat_level)
        elif args.command == "travel":
            result = resolve_travel(args.terrain, args.days, args.supplies, args.forage_mod, args.threat_level)
        elif args.command == "generate-scene":
            result = generate_scene(args.scene_type, args.tag_count, args.threat_level)
        elif args.command == "treasure":
            result = roll_treasure(args.tier)
        elif args.command == "generate-npc":
            result = generate_npc(args.importance, args.region, args.tags)
        elif args.command == "reaction-roll":
            result = reaction_roll(args.modifier)
        elif args.command == "morale":
            result = check_morale(args.morale_score)
        elif args.command == "world-tick":
            result = advance_world(args.days)
        elif args.command == "create-character":
            partial = [p.strip() for p in args.partial_classes.split(",")] if args.partial_classes else None
            foci = [f.strip() for f in args.foci.split(",")] if args.foci else None
            spells = [s.strip() for s in args.spells.split(",")] if args.spells else None
            result = create_character(args.name, args.char_class, args.background, args.method, partial, args.tradition, foci, spells, args.equipment_package, args.free_skill)
        elif args.command == "generate-dungeon":
            result = generate_dungeon(args.depth, args.theme)
        elif args.command == "select-move":
            cmd_result = json.loads(args.result_json)
            result = select_move(args.command_name, cmd_result, args.turns_since_hard_move)
        else:
            result = {"error": f"Unknown command: {args.command}"}

        if args.seed is not None:
            result["seed"] = args.seed
        print(json.dumps(result, indent=2, default=str))

    except Exception as e:
        print(json.dumps({"error": True, "command": args.command, "message": str(e), "type": type(e).__name__}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
