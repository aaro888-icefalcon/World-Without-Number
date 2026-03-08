"""WWN creature stat blocks. Extracted from WWN 4 pp.283-321, WWN 5 pp.148-155.

Each creature has: name, hd (hit dice), ac, atk (attack bonus and count),
dmg (damage dice), shock (damage/ac_threshold or None), move (feet),
ml (morale), inst (instinct), skill (skill bonus), save (target number),
and optional special abilities as text.
"""

# Master stat block templates for on-the-fly NPC/creature generation
# From WWN 4 p.283
HUMAN_TEMPLATES = [
    {"name": "Peaceful Human", "hd": 1, "ac": 10, "atk": "+0", "dmg": "1d4", "shock": None, "move": "30'", "ml": 6, "inst": 5, "skill": "+0", "save": "15+"},
    {"name": "Petty Thug", "hd": 1, "ac": 12, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+1", "save": "15+"},
    {"name": "Veteran Soldier", "hd": 2, "ac": 16, "atk": "+3", "dmg": "1d8", "shock": "2/15", "move": "20'", "ml": 8, "inst": 3, "skill": "+1", "save": "14+"},
    {"name": "Elite Warrior", "hd": 4, "ac": 16, "atk": "+6 x2", "dmg": "1d10+2", "shock": "4/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+1", "save": "13+"},
    {"name": "Skilled Champion", "hd": 6, "ac": 17, "atk": "+8 x2", "dmg": "1d10+4", "shock": "5/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+2", "save": "12+"},
    {"name": "Great Warrior Lord", "hd": 8, "ac": 18, "atk": "+10 x2", "dmg": "1d10+6", "shock": "6/15", "move": "20'", "ml": 10, "inst": 3, "skill": "+2", "save": "11+"},
    {"name": "Famous Swordmaster", "hd": 10, "ac": 20, "atk": "+12 x3", "dmg": "1d12+6", "shock": "8/-", "move": "20'", "ml": 10, "inst": 3, "skill": "+3", "save": "10+"},
    {"name": "Great Warrior King", "hd": 12, "ac": 20, "atk": "+14 x3", "dmg": "2d6+6", "shock": "10/-", "move": "30'", "ml": 10, "inst": 3, "skill": "+3", "save": "9+"},
]

SPELLCASTER_TEMPLATES = [
    {"name": "Petty Mage", "hd": 2, "ac": 11, "atk": "+0", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Veteran Spellcaster", "hd": 4, "ac": 13, "atk": "+2", "dmg": "1d6+1", "shock": None, "move": "30'", "ml": 8, "inst": 4, "skill": "+2", "save": "13+"},
    {"name": "Expert Wizard", "hd": 6, "ac": 15, "atk": "+4", "dmg": "1d8+2", "shock": None, "move": "30'", "ml": 8, "inst": 4, "skill": "+2", "save": "12+"},
    {"name": "Master Sorcerer", "hd": 8, "ac": 17, "atk": "+6", "dmg": "1d8+4", "shock": None, "move": "30'", "ml": 9, "inst": 4, "skill": "+3", "save": "11+"},
    {"name": "Famous Arch-Mage", "hd": 10, "ac": 19, "atk": "+8", "dmg": "1d10+4", "shock": None, "move": "30'", "ml": 9, "inst": 4, "skill": "+3", "save": "10+"},
]

ANIMAL_TEMPLATES = [
    {"name": "Small Pack Predator", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d4", "shock": None, "move": "40'", "ml": 7, "inst": 4, "skill": "+1", "save": "15+"},
    {"name": "Large Pack Predator", "hd": 2, "ac": 13, "atk": "+3 x2", "dmg": "1d6+1", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Medium Solo Predator", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Large Solo Predator", "hd": 5, "ac": 14, "atk": "+7 x2", "dmg": "1d10+2", "shock": "3/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "12+"},
    {"name": "Terrible Beast", "hd": 8, "ac": 16, "atk": "+10 x2", "dmg": "2d6+2", "shock": "4/15", "move": "40'", "ml": 9, "inst": 4, "skill": "+2", "save": "11+"},
    {"name": "Elephantine Grazer", "hd": 6, "ac": 14, "atk": "+7", "dmg": "2d8", "shock": "3/-", "move": "40'", "ml": 7, "inst": 5, "skill": "+1", "save": "12+"},
]

# Named creatures from WWN 4 and WWN 5
CREATURES = [
    # Animals (WWN 4 p.301)
    {"name": "Ashcrawler", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d10+2", "shock": "3/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+2", "save": "12+", "type": "animal"},
    {"name": "Betrayer Bird", "hd": 1, "ac": 13, "atk": "+2", "dmg": "1d4", "shock": None, "move": "10'/60' fly", "ml": 7, "inst": 4, "skill": "+1", "save": "15+", "type": "animal"},
    {"name": "Razorhorn", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d10+1", "shock": "3/15", "move": "50'", "ml": 9, "inst": 4, "skill": "+1", "save": "13+", "type": "animal"},
    {"name": "Salt Devil", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+2", "save": "14+", "type": "animal"},

    # Beasts (WWN 5 pp.148-150)
    {"name": "Cattle of Dis", "hd": 3, "ac": 13, "atk": "+5", "dmg": "1d8+1", "shock": None, "move": "40'", "ml": 9, "inst": 3, "skill": "+1", "save": "14+", "type": "beast"},
    {"name": "Flying Jellyfish", "hd": 8, "ac": 13, "atk": "+10 x2", "dmg": "1d6+1", "shock": None, "move": "30' fly", "ml": 8, "inst": 4, "skill": "+2", "save": "11+", "type": "beast",
     "special": "Skyward Stealth: +4 Sneak when unfed at night. Stinging Grasp: two Physical saves; fail one = 1d6 System Strain, fail both or max Strain = paralyzed for scene."},
    {"name": "Spiderhound", "hd": 2, "ac": 13, "atk": "+4", "dmg": "1d8", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "beast"},
    {"name": "Sunbird", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d4+1", "shock": None, "move": "50' fly", "ml": 8, "inst": 4, "skill": "+1", "save": "13+", "type": "beast",
     "special": "Sunbeam: 300' range, all in 10' radius, 2d6 fire damage, Evasion save for half. Daylight only."},

    # Mounts (WWN 5 p.149)
    {"name": "Horse, Riding", "hd": 2, "ac": 13, "atk": "+3 x2", "dmg": "1d4", "shock": None, "move": "80'", "ml": 7, "inst": 5, "skill": "+1", "save": "14+", "type": "mount"},
    {"name": "Horse, War", "hd": 3, "ac": 13, "atk": "+5 x2", "dmg": "1d4+1", "shock": None, "move": "60'", "ml": 9, "inst": 4, "skill": "+1", "save": "14+", "type": "mount"},
    {"name": "Warmount, Lesser", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d8", "shock": None, "move": "50'", "ml": 9, "inst": 4, "skill": "+1", "save": "13+", "type": "mount"},
    {"name": "Warmount, Blooded", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d10+1", "shock": "3/13", "move": "60'", "ml": 9, "inst": 3, "skill": "+2", "save": "12+", "type": "mount"},

    # Brass Legion Automatons (WWN 4 p.302)
    {"name": "Brass Legion Scytheman", "hd": 3, "ac": 16, "atk": "+5 x2", "dmg": "1d10+1", "shock": "3/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "automaton",
     "special": "Immune to non-magical damage."},
    {"name": "Brass Legion Hulk", "hd": 8, "ac": 18, "atk": "+10 x2", "dmg": "2d8+3", "shock": "6/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "11+", "type": "automaton",
     "special": "Immune to non-magical damage."},

    # Undead (WWN 4 p.321)
    {"name": "Animated Skeleton", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 12, "inst": 2, "skill": "+0", "save": "15+", "type": "undead"},
    {"name": "Shambling Corpse", "hd": 2, "ac": 12, "atk": "+3", "dmg": "1d8", "shock": "2/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+0", "save": "14+", "type": "undead"},
    {"name": "Ravenous Husk", "hd": 3, "ac": 13, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "undead"},
    {"name": "Angry Shade", "hd": 4, "ac": 15, "atk": "+6", "dmg": "1d10", "shock": "2/-", "move": "30' fly", "ml": 12, "inst": 3, "skill": "+1", "save": "13+", "type": "undead",
     "special": "Incorporeal: immune to non-magical weapons. Draining Touch: Physical save or 1d4 System Strain."},
    {"name": "Wraith Lord", "hd": 8, "ac": 17, "atk": "+10 x2", "dmg": "1d10+3", "shock": "5/-", "move": "30' fly", "ml": 12, "inst": 3, "skill": "+2", "save": "11+", "type": "undead",
     "special": "Incorporeal. Draining Touch: Physical save or 1d6 System Strain. Fear Aura: Mental save or flee for 1d6 rounds."},

    # Outsiders (WWN 4 p.319)
    {"name": "Jikegida Beastborn", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "outsider"},
    {"name": "Jikegida City Lord", "hd": 10, "ac": 18, "atk": "+12 x3", "dmg": "1d12+4", "shock": "6/-", "move": "30'", "ml": 10, "inst": 3, "skill": "+3", "save": "10+", "type": "outsider"},
]

# Reaction roll table (WWN 4 p.296)
# 2d6 + Cha modifier of most visible PC
REACTION_TABLE = {
    2: "Hostile, attacks if not clearly overpowered",
    3: "Hostile, attacks if not clearly overpowered",
    4: "Hostile, may attack if provoked",
    5: "Hostile, may attack if provoked",
    6: "Uncertain, can be convinced",
    7: "Uncertain, can be convinced",
    8: "Uncertain, can be convinced",
    9: "Neutral, open to negotiation",
    10: "Neutral, open to negotiation",
    11: "Friendly, inclined to help",
    12: "Enthusiastically friendly",
}

# Instinct check thresholds by creature type (WWN 4 pp.298-299)
# Roll 1d10; if result > Instinct score, creature acts on instinct rather than tactics
INSTINCT_BEHAVIORS = {
    "non_combatant_humans": {
        1: "Freeze and do nothing",
        2: "Flee blindly from danger",
        3: "Attack the nearest visible threat",
        4: "Surrender or beg for mercy",
        5: "Try to hide",
        6: "Cry out for help",
    },
    "predatory_beasts": {
        1: "Lunge at the nearest wounded creature",
        2: "Retreat to a safe distance",
        3: "Attack the smallest/weakest target",
        4: "Defend territory aggressively",
        5: "Stalk silently for a better opportunity",
        6: "Call for pack members",
    },
    "undead": {
        1: "Attack the nearest living creature",
        2: "Guard its post/treasure mindlessly",
        3: "Pursue the last creature that harmed it",
        4: "Attempt to grapple and feed",
        5: "Shamble toward the largest group",
        6: "Ignore everything except its original command",
    },
}
