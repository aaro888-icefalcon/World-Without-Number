"""WWN creature stat blocks. Extracted from WWN 4 pp.283-321, WWN 5 pp.148-155.

Each creature has: name, hd (hit dice), ac, atk (attack bonus and count),
dmg (damage dice), shock (damage/ac_threshold or None), move (feet),
ml (morale), inst (instinct), skill (skill bonus), save (target number),
and optional special abilities as text.
"""

# Master stat block templates for on-the-fly NPC/creature generation
# From WWN 4 p.283
HUMAN_TEMPLATES = [
    {"name": "Peaceful Human", "id": "peaceful_human", "hd": 1, "ac": 10, "atk": "+0", "dmg": "1d4", "shock": None, "move": "30'", "ml": 6, "inst": 5, "skill": "+0", "save": "15+"},
    {"name": "Petty Thug", "id": "petty_thug", "hd": 1, "ac": 12, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+1", "save": "15+"},
    {"name": "Veteran Soldier", "id": "veteran_soldier", "hd": 2, "ac": 16, "atk": "+3", "dmg": "1d8", "shock": "2/15", "move": "20'", "ml": 8, "inst": 3, "skill": "+1", "save": "14+"},
    {"name": "Elite Warrior", "id": "elite_warrior", "hd": 4, "ac": 16, "atk": "+6 x2", "dmg": "1d10+2", "shock": "4/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+1", "save": "13+"},
    {"name": "Skilled Champion", "id": "skilled_champion", "hd": 6, "ac": 17, "atk": "+8 x2", "dmg": "1d10+4", "shock": "5/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+2", "save": "12+"},
    {"name": "Great Warrior Lord", "id": "great_warrior_lord", "hd": 8, "ac": 18, "atk": "+10 x2", "dmg": "1d10+6", "shock": "6/15", "move": "20'", "ml": 10, "inst": 3, "skill": "+2", "save": "11+"},
    {"name": "Famous Swordmaster", "id": "famous_swordmaster", "hd": 10, "ac": 20, "atk": "+12 x3", "dmg": "1d12+6", "shock": "8/-", "move": "20'", "ml": 10, "inst": 3, "skill": "+3", "save": "10+"},
    {"name": "Great Warrior King", "id": "great_warrior_king", "hd": 12, "ac": 20, "atk": "+14 x3", "dmg": "2d6+6", "shock": "10/-", "move": "30'", "ml": 10, "inst": 3, "skill": "+3", "save": "9+"},
]

SPELLCASTER_TEMPLATES = [
    {"name": "Petty Mage", "hd": 2, "ac": 11, "atk": "+0", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Veteran Spellcaster", "hd": 4, "ac": 13, "atk": "+2", "dmg": "1d6+1", "shock": None, "move": "30'", "ml": 8, "inst": 4, "skill": "+2", "save": "13+"},
    {"name": "Expert Wizard", "hd": 6, "ac": 15, "atk": "+4", "dmg": "1d8+2", "shock": None, "move": "30'", "ml": 8, "inst": 4, "skill": "+2", "save": "12+"},
    {"name": "Master Sorcerer", "hd": 8, "ac": 17, "atk": "+6", "dmg": "1d8+4", "shock": None, "move": "30'", "ml": 9, "inst": 4, "skill": "+3", "save": "11+"},
    {"name": "Famous Arch-Mage", "hd": 10, "ac": 19, "atk": "+8", "dmg": "1d10+4", "shock": None, "move": "30'", "ml": 9, "inst": 4, "skill": "+3", "save": "10+"},
]

ANIMAL_TEMPLATES = [
    {"name": "Small Pack Predator", "id": "small_pack_predator", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d4", "shock": None, "move": "40'", "ml": 7, "inst": 4, "skill": "+1", "save": "15+"},
    {"name": "Large Pack Predator", "id": "large_pack_predator", "hd": 2, "ac": 13, "atk": "+3 x2", "dmg": "1d6+1", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Medium Solo Predator", "id": "medium_solo_predator", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+"},
    {"name": "Large Solo Predator", "id": "large_solo_predator", "hd": 5, "ac": 14, "atk": "+7 x2", "dmg": "1d10+2", "shock": "3/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "12+"},
    {"name": "Terrible Beast", "id": "terrible_beast", "hd": 8, "ac": 16, "atk": "+10 x2", "dmg": "2d6+2", "shock": "4/15", "move": "40'", "ml": 9, "inst": 4, "skill": "+2", "save": "11+"},
    {"name": "Elephantine Grazer", "id": "elephantine_grazer", "hd": 6, "ac": 14, "atk": "+7", "dmg": "2d8", "shock": "3/-", "move": "40'", "ml": 7, "inst": 5, "skill": "+1", "save": "12+"},
]

# Named creatures from WWN 4 and WWN 5
CREATURES = [
    # Animals (WWN 4 p.301)
    {"name": "Ashcrawler", "id": "ashcrawler", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d10+2", "shock": "3/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+2", "save": "12+", "type": "animal"},
    {"name": "Betrayer Bird", "id": "betrayer_bird", "hd": 1, "ac": 13, "atk": "+2", "dmg": "1d4", "shock": None, "move": "10'/60' fly", "ml": 7, "inst": 4, "skill": "+1", "save": "15+", "type": "animal"},
    {"name": "Razorhorn", "id": "razorhorn", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d10+1", "shock": "3/15", "move": "50'", "ml": 9, "inst": 4, "skill": "+1", "save": "13+", "type": "animal"},
    {"name": "Salt Devil", "id": "salt_devil", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+2", "save": "14+", "type": "animal"},

    # Beasts (WWN 5 pp.148-150)
    {"name": "Cattle of Dis", "id": "cattle_of_dis", "hd": 3, "ac": 13, "atk": "+5", "dmg": "1d8+1", "shock": None, "move": "40'", "ml": 9, "inst": 3, "skill": "+1", "save": "14+", "type": "beast"},
    {"name": "Flying Jellyfish", "id": "flying_jellyfish", "hd": 8, "ac": 13, "atk": "+10 x2", "dmg": "1d6+1", "shock": None, "move": "30' fly", "ml": 8, "inst": 4, "skill": "+2", "save": "11+", "type": "beast",
     "special": "Skyward Stealth: +4 Sneak when unfed at night. Stinging Grasp: two Physical saves; fail one = 1d6 System Strain, fail both or max Strain = paralyzed for scene."},
    {"name": "Spiderhound", "id": "spiderhound", "hd": 2, "ac": 13, "atk": "+4", "dmg": "1d8", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "beast"},
    {"name": "Sunbird", "id": "sunbird", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d4+1", "shock": None, "move": "50' fly", "ml": 8, "inst": 4, "skill": "+1", "save": "13+", "type": "beast",
     "special": "Sunbeam: 300' range, all in 10' radius, 2d6 fire damage, Evasion save for half. Daylight only."},

    # Mounts (WWN 5 p.149)
    {"name": "Horse, Riding", "id": "horse_riding", "hd": 2, "ac": 13, "atk": "+3 x2", "dmg": "1d4", "shock": None, "move": "80'", "ml": 7, "inst": 5, "skill": "+1", "save": "14+", "type": "mount"},
    {"name": "Horse, War", "id": "horse_war", "hd": 3, "ac": 13, "atk": "+5 x2", "dmg": "1d4+1", "shock": None, "move": "60'", "ml": 9, "inst": 4, "skill": "+1", "save": "14+", "type": "mount"},
    {"name": "Warmount, Lesser", "id": "warmount_lesser", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d8", "shock": None, "move": "50'", "ml": 9, "inst": 4, "skill": "+1", "save": "13+", "type": "mount"},
    {"name": "Warmount, Blooded", "id": "warmount_blooded", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d10+1", "shock": "3/13", "move": "60'", "ml": 9, "inst": 3, "skill": "+2", "save": "12+", "type": "mount"},

    # Brass Legion Automatons (WWN 4 p.302)
    {"name": "Brass Legion Scytheman", "id": "brass_legion_scytheman", "hd": 3, "ac": 16, "atk": "+5 x2", "dmg": "1d10+1", "shock": "3/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "automaton",
     "special": "Immune to non-magical damage."},
    {"name": "Brass Legion Hulk", "id": "brass_legion_hulk", "hd": 8, "ac": 18, "atk": "+10 x2", "dmg": "2d8+3", "shock": "6/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "11+", "type": "automaton",
     "special": "Immune to non-magical damage."},

    # Undead (WWN 4 p.321)
    {"name": "Animated Skeleton", "id": "animated_skeleton", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 12, "inst": 2, "skill": "+0", "save": "15+", "type": "undead"},
    {"name": "Shambling Corpse", "id": "shambling_corpse", "hd": 2, "ac": 12, "atk": "+3", "dmg": "1d8", "shock": "2/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+0", "save": "14+", "type": "undead"},
    {"name": "Ravenous Husk", "id": "ravenous_husk", "hd": 3, "ac": 13, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "undead"},
    {"name": "Angry Shade", "id": "angry_shade", "hd": 4, "ac": 15, "atk": "+6", "dmg": "1d10", "shock": "2/-", "move": "30' fly", "ml": 12, "inst": 3, "skill": "+1", "save": "13+", "type": "undead",
     "special": "Incorporeal: immune to non-magical weapons. Draining Touch: Physical save or 1d4 System Strain."},
    {"name": "Wraith Lord", "id": "wraith_lord", "hd": 8, "ac": 17, "atk": "+10 x2", "dmg": "1d10+3", "shock": "5/-", "move": "30' fly", "ml": 12, "inst": 3, "skill": "+2", "save": "11+", "type": "undead",
     "special": "Incorporeal. Draining Touch: Physical save or 1d6 System Strain. Fear Aura: Mental save or flee for 1d6 rounds."},

    # Outsiders (WWN 4 p.319)
    {"name": "Jikegida Beastborn", "id": "jikegida_beastborn", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "outsider"},
    {"name": "Jikegida City Lord", "id": "jikegida_city_lord", "hd": 10, "ac": 18, "atk": "+12 x3", "dmg": "1d12+4", "shock": "6/-", "move": "30'", "ml": 10, "inst": 3, "skill": "+3", "save": "10+", "type": "outsider"},

    # --- Animals ---
    {"name": "Wolf", "id": "wolf", "hd": 2, "ac": 13, "atk": "+3", "dmg": "1d6+1", "shock": None, "move": "50'", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "animal"},
    {"name": "Dire Wolf", "id": "dire_wolf", "hd": 4, "ac": 14, "atk": "+6 x2", "dmg": "1d8+2", "shock": "2/15", "move": "50'", "ml": 9, "inst": 4, "skill": "+1", "save": "13+", "type": "animal"},
    {"name": "Bear, Black", "id": "bear_black", "hd": 3, "ac": 13, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 7, "inst": 4, "skill": "+1", "save": "14+", "type": "animal"},
    {"name": "Bear, Cave", "id": "bear_cave", "hd": 7, "ac": 15, "atk": "+9 x2", "dmg": "2d6+2", "shock": "4/15", "move": "40'", "ml": 9, "inst": 4, "skill": "+2", "save": "12+", "type": "animal"},
    {"name": "Giant Spider", "id": "giant_spider", "hd": 3, "ac": 14, "atk": "+5", "dmg": "1d8", "shock": None, "move": "40'", "ml": 8, "inst": 4, "skill": "+2", "save": "14+", "type": "animal",
     "special": "Venomous Bite: Physical save or 1d4 poison damage per round for 3 rounds. Web: Evasion save or immobilized for 1 round."},
    {"name": "Hawk, Giant", "id": "hawk_giant", "hd": 2, "ac": 14, "atk": "+3", "dmg": "1d6", "shock": None, "move": "10'/80' fly", "ml": 7, "inst": 4, "skill": "+2", "save": "14+", "type": "animal"},
    {"name": "Boar, Wild", "id": "boar_wild", "hd": 3, "ac": 13, "atk": "+5", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 9, "inst": 4, "skill": "+1", "save": "14+", "type": "animal"},
    {"name": "Giant Snake, Constrictor", "id": "giant_snake_constrictor", "hd": 4, "ac": 13, "atk": "+6", "dmg": "1d8+2", "shock": "2/15", "move": "30'", "ml": 7, "inst": 4, "skill": "+2", "save": "13+", "type": "animal",
     "special": "Constrict: on hit, automatic 1d8 damage each subsequent round until escaped (opposed Str check)."},
    {"name": "Giant Snake, Venomous", "id": "giant_snake_venomous", "hd": 3, "ac": 14, "atk": "+5", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+2", "save": "14+", "type": "animal",
     "special": "Deadly Venom: Physical save or take 2d6 poison damage and lose 1 System Strain."},
    {"name": "Crocodile", "id": "crocodile", "hd": 4, "ac": 15, "atk": "+6", "dmg": "1d10+1", "shock": "2/15", "move": "20'/40' swim", "ml": 7, "inst": 4, "skill": "+1", "save": "13+", "type": "animal"},
    {"name": "Giant Scorpion", "id": "giant_scorpion", "hd": 5, "ac": 16, "atk": "+7 x2", "dmg": "1d8+1", "shock": "2/15", "move": "40'", "ml": 8, "inst": 4, "skill": "+1", "save": "12+", "type": "animal",
     "special": "Sting: additional tail attack at +7 for 1d6, Physical save or 2d6 poison damage."},
    {"name": "Giant Bat", "id": "giant_bat", "hd": 2, "ac": 13, "atk": "+3", "dmg": "1d6", "shock": None, "move": "10'/60' fly", "ml": 7, "inst": 4, "skill": "+1", "save": "14+", "type": "animal"},
    {"name": "Swamp Leech, Giant", "id": "swamp_leech_giant", "hd": 3, "ac": 11, "atk": "+5", "dmg": "1d6", "shock": None, "move": "20'/30' swim", "ml": 8, "inst": 4, "skill": "+1", "save": "14+", "type": "animal",
     "special": "Blood Drain: on hit, attaches and drains 1d4 hp per round automatically until removed."},

    # --- Beasts ---
    {"name": "Chimera", "id": "chimera", "hd": 9, "ac": 16, "atk": "+11 x3", "dmg": "1d10+2", "shock": "4/15", "move": "30'/60' fly", "ml": 9, "inst": 3, "skill": "+2", "save": "11+", "type": "beast",
     "special": "Fire Breath: 30' cone, 3d6 fire damage, Evasion save for half. Usable every 1d4 rounds."},
    {"name": "Manticore", "id": "manticore", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d8+2", "shock": "3/15", "move": "30'/50' fly", "ml": 9, "inst": 3, "skill": "+2", "save": "12+", "type": "beast",
     "special": "Tail Spikes: 150' range, +8, 1d6 damage, 6 volleys per day of 1d4 spikes each."},
    {"name": "Wyvern", "id": "wyvern", "hd": 7, "ac": 15, "atk": "+9 x2", "dmg": "1d10+2", "shock": "3/15", "move": "20'/60' fly", "ml": 8, "inst": 4, "skill": "+1", "save": "12+", "type": "beast",
     "special": "Tail Sting: additional attack at +9 for 1d6, Physical save or 2d8 poison damage."},
    {"name": "Griffon", "id": "griffon", "hd": 7, "ac": 15, "atk": "+9 x2", "dmg": "1d10+1", "shock": "3/15", "move": "30'/70' fly", "ml": 8, "inst": 4, "skill": "+2", "save": "12+", "type": "beast"},
    {"name": "Basilisk", "id": "basilisk", "hd": 6, "ac": 16, "atk": "+8", "dmg": "1d10+2", "shock": "3/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+1", "save": "12+", "type": "beast",
     "special": "Petrifying Gaze: Physical save or turned to stone. Averting eyes imposes -4 to hit."},
    {"name": "Cockatrice", "id": "cockatrice", "hd": 5, "ac": 14, "atk": "+7", "dmg": "1d6+1", "shock": None, "move": "30'/50' fly", "ml": 7, "inst": 4, "skill": "+1", "save": "12+", "type": "beast",
     "special": "Petrifying Touch: Physical save or turned to stone over 1d6 rounds."},
    {"name": "Hydra, Five-Headed", "id": "hydra_five_headed", "hd": 10, "ac": 15, "atk": "+12 x5", "dmg": "1d8+1", "shock": "2/15", "move": "30'", "ml": 9, "inst": 3, "skill": "+2", "save": "10+", "type": "beast",
     "special": "Regeneration: regrows a severed head in 1d4 rounds unless cauterized. Each head attacks independently."},
    {"name": "Owlbear", "id": "owlbear", "hd": 5, "ac": 14, "atk": "+7 x2", "dmg": "1d10+1", "shock": "3/15", "move": "40'", "ml": 9, "inst": 4, "skill": "+1", "save": "12+", "type": "beast",
     "special": "Bear Hug: if both attacks hit same target, automatic 2d6 crushing damage."},
    {"name": "Displacer Beast", "id": "displacer_beast", "hd": 6, "ac": 16, "atk": "+8 x2", "dmg": "1d8+1", "shock": None, "move": "50'", "ml": 8, "inst": 3, "skill": "+2", "save": "12+", "type": "beast",
     "special": "Displacement: first attack each round against it automatically misses."},
    {"name": "Phase Serpent", "id": "phase_serpent", "hd": 5, "ac": 15, "atk": "+7", "dmg": "1d10+1", "shock": None, "move": "40'", "ml": 7, "inst": 4, "skill": "+2", "save": "12+", "type": "beast",
     "special": "Phase Shift: can become ethereal as a Move action. Attacks from ethereal state bypass armor."},

    # --- Undead ---
    {"name": "Ghoul", "id": "ghoul", "hd": 2, "ac": 13, "atk": "+3 x2", "dmg": "1d6", "shock": None, "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "undead",
     "special": "Paralyzing Touch: Physical save or paralyzed for 1d4 rounds. Does not affect elves."},
    {"name": "Wight", "id": "wight", "hd": 4, "ac": 15, "atk": "+6", "dmg": "1d8+1", "shock": "2/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "13+", "type": "undead",
     "special": "Level Drain: on hit, Physical save or lose 1 level (1 HD for monsters)."},
    {"name": "Revenant", "id": "revenant", "hd": 6, "ac": 16, "atk": "+8 x2", "dmg": "1d10+2", "shock": "3/15", "move": "30'", "ml": 12, "inst": 3, "skill": "+2", "save": "12+", "type": "undead",
     "special": "Undying Purpose: regenerates 2 hp per round unless destroyed by fire or holy power. Tracks its killer relentlessly."},
    {"name": "Death Knight", "id": "death_knight", "hd": 10, "ac": 20, "atk": "+12 x2", "dmg": "1d12+4", "shock": "6/-", "move": "30'", "ml": 12, "inst": 3, "skill": "+3", "save": "10+", "type": "undead",
     "special": "Dread Aura: Mental save or -2 to hit and saves within 30'. Can cast one spell per round as a free action."},
    {"name": "Bone Horror", "id": "bone_horror", "hd": 8, "ac": 17, "atk": "+10 x3", "dmg": "1d8+2", "shock": "4/-", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "11+", "type": "undead",
     "special": "Bone Storm: once per encounter, all within 15' take 3d6 damage, Evasion save for half."},
    {"name": "Specter", "id": "specter", "hd": 5, "ac": 15, "atk": "+7", "dmg": "1d8+1", "shock": "2/-", "move": "30' fly", "ml": 12, "inst": 3, "skill": "+2", "save": "12+", "type": "undead",
     "special": "Incorporeal. Life Drain: Physical save or 1d4 System Strain. Sunlight vulnerability: -2 to all rolls in daylight."},
    {"name": "Mummy", "id": "mummy", "hd": 6, "ac": 15, "atk": "+8", "dmg": "1d12", "shock": "3/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "12+", "type": "undead",
     "special": "Mummy Rot: on hit, Physical save or cursed wound that cannot heal naturally. Fear Aura: Mental save or paralyzed 1 round."},
    {"name": "Vampire", "id": "vampire", "hd": 9, "ac": 18, "atk": "+11 x2", "dmg": "1d10+3", "shock": "4/-", "move": "40'/50' fly", "ml": 10, "inst": 3, "skill": "+3", "save": "11+", "type": "undead",
     "special": "Charm Gaze: Mental save or charmed. Regeneration 3 hp/round unless in sunlight. Immune to non-magical weapons."},
    {"name": "Skeletal Champion", "id": "skeletal_champion", "hd": 3, "ac": 15, "atk": "+5 x2", "dmg": "1d8+1", "shock": "2/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "undead"},
    {"name": "Corpse Titan", "id": "corpse_titan", "hd": 12, "ac": 17, "atk": "+14 x2", "dmg": "2d8+4", "shock": "6/-", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "9+", "type": "undead",
     "special": "Massive: immune to being knocked prone or grappled. Stomp: all within 10' take 2d6, Evasion save to avoid."},

    # --- Outsiders ---
    {"name": "Lesser Demon", "id": "lesser_demon", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d8+1", "shock": "2/15", "move": "30'", "ml": 9, "inst": 3, "skill": "+1", "save": "13+", "type": "outsider",
     "special": "Immune to non-magical weapons. Fire Resistance: half damage from fire."},
    {"name": "Shadow Stalker", "id": "shadow_stalker", "hd": 5, "ac": 16, "atk": "+7 x2", "dmg": "1d8+2", "shock": None, "move": "40'", "ml": 8, "inst": 3, "skill": "+3", "save": "12+", "type": "outsider",
     "special": "Shadow Step: can teleport between shadows within 60' as a Move action. +4 Sneak in dim light."},
    {"name": "Void Spawn", "id": "void_spawn", "hd": 7, "ac": 17, "atk": "+9 x2", "dmg": "1d10+3", "shock": "3/-", "move": "30'", "ml": 10, "inst": 3, "skill": "+2", "save": "12+", "type": "outsider",
     "special": "Void Aura: all within 15' take 1d4 cold damage per round. Immune to cold. Mental save or -1 to hit within aura."},
    {"name": "Flame Imp", "id": "flame_imp", "hd": 2, "ac": 14, "atk": "+3", "dmg": "1d6+1", "shock": None, "move": "30'/40' fly", "ml": 7, "inst": 4, "skill": "+2", "save": "14+", "type": "outsider",
     "special": "Fire Touch: attacks deal fire damage. Immune to fire. Vulnerable to cold (double damage)."},
    {"name": "Greater Demon", "id": "greater_demon", "hd": 12, "ac": 20, "atk": "+14 x3", "dmg": "2d6+4", "shock": "6/-", "move": "30'/40' fly", "ml": 10, "inst": 3, "skill": "+3", "save": "9+", "type": "outsider",
     "special": "Immune to non-magical weapons. Fear Aura: Mental save or flee 1d6 rounds. Can cast one spell per round."},
    {"name": "Chaos Hound", "id": "chaos_hound", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d8", "shock": "2/15", "move": "50'", "ml": 9, "inst": 3, "skill": "+1", "save": "14+", "type": "outsider",
     "special": "Warp Howl: once per encounter, all within 30' must Mental save or be confused for 1 round."},
    {"name": "Fey Knight", "id": "fey_knight", "hd": 6, "ac": 17, "atk": "+8 x2", "dmg": "1d10+2", "shock": "3/15", "move": "40'", "ml": 8, "inst": 3, "skill": "+3", "save": "12+", "type": "outsider",
     "special": "Glamour: can appear as any humanoid. Iron vulnerability: takes double damage from iron weapons."},

    # --- Automatons ---
    {"name": "Iron Sentinel", "id": "iron_sentinel", "hd": 6, "ac": 18, "atk": "+8 x2", "dmg": "1d10+2", "shock": "4/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "12+", "type": "automaton",
     "special": "Immune to non-magical damage. Immune to poison, fear, and mind-affecting effects."},
    {"name": "Crystal Golem", "id": "crystal_golem", "hd": 10, "ac": 20, "atk": "+12 x2", "dmg": "2d6+3", "shock": "5/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "10+", "type": "automaton",
     "special": "Immune to non-magical damage. Prismatic Burst: once per encounter, 20' radius, 4d6 damage, Evasion save for half."},
    {"name": "Steam Walker", "id": "steam_walker", "hd": 5, "ac": 17, "atk": "+7 x2", "dmg": "1d10+1", "shock": "3/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "12+", "type": "automaton",
     "special": "Steam Vent: once per encounter, 15' cone, 2d6 fire damage, Evasion save for half."},
    {"name": "Clockwork Spider", "id": "clockwork_spider", "hd": 2, "ac": 15, "atk": "+3", "dmg": "1d6+1", "shock": None, "move": "40'", "ml": 12, "inst": 2, "skill": "+2", "save": "14+", "type": "automaton",
     "special": "Climb any surface. Self-destruct: on destruction, 10' radius, 2d6 damage, Evasion save for half."},
    {"name": "Brass Archer", "id": "brass_archer", "hd": 3, "ac": 15, "atk": "+5", "dmg": "1d8+1", "shock": None, "move": "30'", "ml": 12, "inst": 2, "skill": "+2", "save": "14+", "type": "automaton",
     "special": "Immune to non-magical damage. Integrated Bow: 200' range, +5, 1d8+1 damage."},

    # --- Constructs ---
    {"name": "Animated Armor", "id": "animated_armor", "hd": 4, "ac": 18, "atk": "+6", "dmg": "1d8+2", "shock": "2/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+0", "save": "13+", "type": "construct",
     "special": "Immune to poison, fear, and mind-affecting effects."},
    {"name": "Living Statue", "id": "living_statue", "hd": 5, "ac": 16, "atk": "+7", "dmg": "1d10+1", "shock": "3/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+0", "save": "12+", "type": "construct",
     "special": "Stone Form: appears as an ordinary statue when motionless. Surprise on 1-4 on d6."},
    {"name": "Stone Golem", "id": "stone_golem", "hd": 12, "ac": 22, "atk": "+14 x2", "dmg": "2d8+4", "shock": "8/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "9+", "type": "construct",
     "special": "Immune to non-magical damage. Immune to spells of 4th level or below. Slow: once per 2 rounds, 60' range, Physical save or slowed."},
    {"name": "Clay Guardian", "id": "clay_guardian", "hd": 8, "ac": 17, "atk": "+10 x2", "dmg": "2d6+2", "shock": "4/-", "move": "20'", "ml": 12, "inst": 2, "skill": "+0", "save": "11+", "type": "construct",
     "special": "Immune to non-magical damage. Absorb Magic: spells targeting it heal it for 1 hp per spell level."},
    {"name": "Bone Construct", "id": "bone_construct", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d10+2", "shock": "3/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+0", "save": "12+", "type": "construct",
     "special": "Reassemble: if reduced to 0 hp, reforms in 1d4 rounds unless remains are scattered or burned."},

    # --- Plants ---
    {"name": "Carnivorous Tree", "id": "carnivorous_tree", "hd": 8, "ac": 14, "atk": "+10 x3", "dmg": "1d8+2", "shock": "3/-", "move": "0'", "ml": 12, "inst": 2, "skill": "+0", "save": "11+", "type": "plant",
     "special": "Grasping Branches: 30' reach. Swallow: on two hits to same target, engulfed for 2d6 acid damage per round. Fire vulnerability: double damage from fire."},
    {"name": "Vine Horror", "id": "vine_horror", "hd": 5, "ac": 13, "atk": "+7 x2", "dmg": "1d8+1", "shock": "2/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "12+", "type": "plant",
     "special": "Entangle: all within 15' must Evasion save or be restrained. Regeneration 1 hp/round in sunlight."},
    {"name": "Mushroom Sentinel", "id": "mushroom_sentinel", "hd": 4, "ac": 14, "atk": "+6", "dmg": "1d8+1", "shock": "2/15", "move": "20'", "ml": 12, "inst": 2, "skill": "+1", "save": "13+", "type": "plant",
     "special": "Spore Cloud: once per encounter, 20' radius, Physical save or 1d6 poison damage and blinded for 1 round."},
    {"name": "Thornblight", "id": "thornblight", "hd": 3, "ac": 14, "atk": "+5 x2", "dmg": "1d6+1", "shock": "2/15", "move": "30'", "ml": 12, "inst": 2, "skill": "+1", "save": "14+", "type": "plant",
     "special": "Thorn Burst: attackers in melee take 1d4 piercing damage when they hit."},
    {"name": "Blightwood Treant", "id": "blightwood_treant", "hd": 10, "ac": 17, "atk": "+12 x2", "dmg": "2d8+3", "shock": "5/-", "move": "20'", "ml": 9, "inst": 3, "skill": "+1", "save": "10+", "type": "plant",
     "special": "Massive: immune to being knocked prone. Animate Trees: can command 1d4 nearby trees to attack as Thornblights. Fire vulnerability."},

    # --- Humans ---
    {"name": "Bandit", "id": "bandit", "hd": 1, "ac": 13, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 7, "inst": 4, "skill": "+1", "save": "15+", "type": "human"},
    {"name": "Bandit Captain", "id": "bandit_captain", "hd": 4, "ac": 15, "atk": "+6 x2", "dmg": "1d8+2", "shock": "3/15", "move": "30'", "ml": 8, "inst": 3, "skill": "+2", "save": "13+", "type": "human"},
    {"name": "Cultist", "id": "cultist", "hd": 1, "ac": 11, "atk": "+1", "dmg": "1d6", "shock": None, "move": "30'", "ml": 8, "inst": 4, "skill": "+0", "save": "15+", "type": "human"},
    {"name": "Cult Priest", "id": "cult_priest", "hd": 5, "ac": 14, "atk": "+4", "dmg": "1d8+1", "shock": None, "move": "30'", "ml": 9, "inst": 3, "skill": "+2", "save": "12+", "type": "human",
     "special": "Can cast one spell per round: Heal 1d8+2, Command (Mental save or obey one order), or Blight (1d10 necrotic, 60' range)."},
    {"name": "Assassin", "id": "assassin", "hd": 6, "ac": 15, "atk": "+8 x2", "dmg": "1d8+3", "shock": None, "move": "40'", "ml": 8, "inst": 3, "skill": "+3", "save": "12+", "type": "human",
     "special": "Sneak Attack: deals double damage when attacking a surprised or flanked target."},
    {"name": "Guard", "id": "guard", "hd": 1, "ac": 15, "atk": "+1", "dmg": "1d8", "shock": None, "move": "20'", "ml": 7, "inst": 4, "skill": "+0", "save": "15+", "type": "human"},
    {"name": "Knight", "id": "knight", "hd": 5, "ac": 18, "atk": "+7 x2", "dmg": "1d10+2", "shock": "3/15", "move": "20'", "ml": 9, "inst": 3, "skill": "+1", "save": "12+", "type": "human"},
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


def get_creature(creature_id):
    """Look up a creature by stable ID."""
    for c in CREATURES:
        if c.get("id") == creature_id:
            return c
    return None
