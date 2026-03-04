"""WWN skill definitions. Extracted from WWN 1 pp.9-10."""

# Skill check: 2d6 + skill_level + attribute_modifier >= difficulty

SKILL_CHECK_DIFFICULTIES = {
    6: "A simple task that most people could accomplish given time",
    8: "A significant challenge for a skilled practitioner",
    10: "Something that only a gifted expert could manage",
    12: "A task that only a master could hope to accomplish",
    14: "Something almost beyond human capacity",
}

# Skill levels
SKILL_LEVELS = {
    -1: "Unskilled (no training; -1 penalty on checks)",
    0: "Ordinary competence; an apprentice or hobbyist",
    1: "A veteran practitioner, noticeably better than most",
    2: "The best in a city; a seasoned expert",
    3: "The best in a kingdom; a famous master",
    4: "The best in the known world; a legendary figure",
}

# All 22 skills with descriptions and common associated attributes
SKILLS = {
    "administer": {
        "description": "Managing an organization, running a business, keeping records, and maintaining logistical networks",
        "attributes": ["intelligence", "charisma"],
    },
    "connect": {
        "description": "Finding useful people, knowing the right person for a job, and leveraging social networks",
        "attributes": ["charisma"],
    },
    "convince": {
        "description": "Persuading, deceiving, or intimidating others through force of personality or argument",
        "attributes": ["charisma", "wisdom"],
    },
    "craft": {
        "description": "Making and repairing physical goods, from weapons to clothing to architecture",
        "attributes": ["intelligence", "dexterity"],
    },
    "exert": {
        "description": "Running, jumping, climbing, swimming, and other feats of physical prowess",
        "attributes": ["strength", "constitution"],
    },
    "heal": {
        "description": "Treating wounds, curing diseases, neutralizing poisons, and stabilizing the dying",
        "attributes": ["intelligence", "wisdom"],
    },
    "know": {
        "description": "Knowing facts about history, geography, natural science, and general education",
        "attributes": ["intelligence"],
    },
    "lead": {
        "description": "Inspiring followers, coordinating subordinates, and managing group morale",
        "attributes": ["charisma"],
    },
    "magic": {
        "description": "Casting spells, analyzing magical effects, and understanding arcane traditions",
        "attributes": ["intelligence", "wisdom"],
    },
    "notice": {
        "description": "Perceiving details, detecting ambushes, finding hidden things, and reading situations",
        "attributes": ["wisdom"],
    },
    "perform": {
        "description": "Entertaining, artistic performance, acting, and public speaking",
        "attributes": ["charisma", "dexterity"],
    },
    "pray": {
        "description": "Conducting religious rites, theological knowledge, and invoking divine favor",
        "attributes": ["wisdom", "charisma"],
    },
    "punch": {
        "description": "Unarmed combat, including punching, kicking, and grappling",
        "attributes": ["strength", "dexterity"],
        "is_combat": True,
    },
    "ride": {
        "description": "Riding beasts, managing mounts in combat, and land vehicle operation",
        "attributes": ["dexterity", "wisdom"],
    },
    "sail": {
        "description": "Handling watercraft, navigation by sea, and nautical knowledge",
        "attributes": ["intelligence", "dexterity"],
    },
    "shoot": {
        "description": "Using ranged weapons including bows, crossbows, hurled weapons, and hurlants",
        "attributes": ["dexterity"],
        "is_combat": True,
    },
    "sneak": {
        "description": "Stealth, hiding, moving silently, picking locks, disarming traps, and disguise",
        "attributes": ["dexterity", "intelligence"],
    },
    "stab": {
        "description": "Fighting with melee weapons of all kinds",
        "attributes": ["strength", "dexterity"],
        "is_combat": True,
    },
    "survive": {
        "description": "Hunting, foraging, navigating wilderness, tracking, and enduring harsh environments",
        "attributes": ["wisdom", "constitution"],
    },
    "trade": {
        "description": "Buying and selling goods, appraising valuables, and commercial negotiation",
        "attributes": ["intelligence", "charisma"],
    },
    "work": {
        "description": "Catch-all skill for a specific profession not covered by other skills",
        "attributes": ["varies"],
    },
}
