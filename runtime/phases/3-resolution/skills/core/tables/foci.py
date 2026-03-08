"""WWN focus (feat) definitions. Extracted from WWN 1 pp.22-31."""

# Each focus has level_1 and level_2 effects. Some are combat-only or non-combat-only.
FOCI = {
    "alert": {
        "type": "any",
        "level_1": "Gain Notice-0 if unskilled. +1 initiative. Cannot be surprised.",
        "level_2": "+2 initiative. Immune to first-round ambush attacks against you.",
    },
    "armsmaster": {
        "type": "warrior",
        "level_1": "Gain Stab-0 if unskilled. Ready or stow a weapon as a free action. +1 to hit with melee weapons.",
        "level_2": "+2 damage with all melee weapons. Draw any number of readied items per round.",
    },
    "assassin": {
        "type": "any",
        "level_1": "Gain Sneak-0 if unskilled. +2 damage against surprised or unaware targets.",
        "level_2": "Damage dice are maximized against surprised or unaware targets.",
    },
    "authority": {
        "type": "any",
        "level_1": "Gain Lead-0 if unskilled. Hirelings and followers have +1 morale. Gain +1 reaction roll.",
        "level_2": "Hirelings and followers have +2 morale. Once per scene, reroll any failed Lead check.",
    },
    "close_combatant": {
        "type": "warrior",
        "level_1": "Gain Punch-0 if unskilled. +1 to hit with unarmed/small weapons. Unarmed damage is 1d6+Skill.",
        "level_2": "+2 AC in melee. +1d4 bonus unarmed/small weapon damage on a hit.",
    },
    "connected": {
        "type": "any",
        "level_1": "Gain Connect-0 if unskilled. Once per session, find a useful contact in a community.",
        "level_2": "Contacts are more helpful and reliable. Once per session, get a significant favor.",
    },
    "deadly_sniper": {
        "type": "warrior",
        "level_1": "Gain Shoot-0 if unskilled. No penalty for long range. +1 to hit with ranged weapons.",
        "level_2": "+2 damage with ranged weapons. Can target specific body parts without penalty.",
    },
    "dealmaker": {
        "type": "any",
        "level_1": "Gain Trade-0 if unskilled. 10% discount on purchases. Can always find a buyer.",
        "level_2": "25% discount on purchases. Once per session, discover a profitable opportunity.",
    },
    "dev_cunning": {
        "type": "any",
        "level_1": "Gain Convince-0 if unskilled. Once per scene, make a Cha/Convince check to deceive without evidence.",
        "level_2": "Targets of deception need a Wis/Notice check to suspect anything. +2 to deception checks.",
    },
    "die_hard": {
        "type": "warrior",
        "level_1": "The character is not incapacitated at 0 HP; can keep acting until reaching negative max HP.",
        "level_2": "Once per day, when reduced to 0 HP, immediately heal to 1 HP.",
    },
    "diplomat": {
        "type": "any",
        "level_1": "Gain Convince-0 if unskilled. Can attempt to halt combat for parley once per fight.",
        "level_2": "+2 to Convince checks during formal negotiations. Immune to magical persuasion.",
    },
    "gifted_chirurgeon": {
        "type": "any",
        "level_1": "Gain Heal-0 if unskilled. Stabilize dying characters as a Main Action automatically (no check).",
        "level_2": "Heal 1d6+Heal_skill HP with 10 minutes of work, once per target per day. No System Strain cost.",
    },
    "hacker": {
        "type": "any",
        "level_1": "Gain Sneak-0 if unskilled. +1 to checks to pick locks, disable traps, and bypass security.",
        "level_2": "+2 to all lock/trap/security checks. Automatically detect simple traps within 10 feet.",
    },
    "healer": {
        "type": "any",
        "level_1": "Gain Heal-0 if unskilled. Can attempt long-term care on patients to restore additional HP.",
        "level_2": "Long-term care restores double HP. Can treat two patients simultaneously.",
    },
    "impervious_defense": {
        "type": "warrior",
        "level_1": "+1 AC while wearing armor. Can use shields with two-handed weapons.",
        "level_2": "+2 AC while wearing armor. Immune to Shock damage.",
    },
    "lucky": {
        "type": "any",
        "level_1": "Once per session, reroll any one die roll and take the preferred result.",
        "level_2": "Once per session, cause an enemy to reroll a successful attack or check.",
    },
    "nullifier": {
        "type": "warrior",
        "level_1": "+2 to all saving throws against magical effects.",
        "level_2": "+4 to all saving throws against magical effects. Magic attacks deal minimum damage to you.",
    },
    "rider": {
        "type": "any",
        "level_1": "Gain Ride-0 if unskilled. Mounts never check morale. +2 to ride-related checks.",
        "level_2": "Can fight from horseback without penalty. Mount gains +2 AC and +2 HP per your level.",
    },
    "savage_fray": {
        "type": "warrior",
        "level_1": "Deal 2 automatic damage to all lesser foes within melee range at the start of your turn.",
        "level_2": "Automatic damage increases to your level. Applies to any foe with HD less than your level.",
    },
    "shock_trooper": {
        "type": "warrior",
        "level_1": "+2 Shock damage with all melee weapons.",
        "level_2": "+4 Shock damage with all melee weapons. Shock is dealt even to targets with higher AC than threshold.",
    },
    "spirit_familiar": {
        "type": "any",
        "level_1": "Gain a small spirit companion. It can scout up to 100' away and communicate simple impressions.",
        "level_2": "Familiar can scout up to 1 mile. Can see and hear through its senses. +1 to Magic checks.",
    },
    "trapmaster": {
        "type": "any",
        "level_1": "Gain Notice-0 if unskilled. Automatically detect traps within 10'. +2 to disarm traps.",
        "level_2": "Can craft simple traps. Traps you set have +2 difficulty to detect and disarm.",
    },
    "unique_gift": {
        "type": "any",
        "level_1": "Gain a unique supernatural or extraordinary ability, determined with GM approval.",
        "level_2": "The unique gift grows in power or scope, determined with GM approval.",
    },
    "wanderer": {
        "type": "any",
        "level_1": "Gain Survive-0 if unskilled. +1 to foraging, navigation, and travel checks. Carry +2 enc.",
        "level_2": "Never get lost in the wilderness. Group foraging checks auto-succeed in reasonable terrain.",
    },
    "well_met": {
        "type": "any",
        "level_1": "Gain Connect-0 if unskilled. NPCs start with +1 reaction to you.",
        "level_2": "NPCs start with +2 reaction. Once per session, turn a hostile NPC neutral for one scene.",
    },
    "xenoblooded": {
        "type": "any",
        "level_1": "Gain a minor physical mutation or alien trait with a small mechanical benefit.",
        "level_2": "The trait intensifies. +1 to a chosen attribute (max 18) and an additional minor power.",
    },
    "specialist": {
        "type": "any",
        "repeatable": True,
        "level_1": "Gain skill-0 in a chosen skill if unskilled. Choose a skill; gain +1 to non-combat checks with it.",
        "level_2": "+2 to non-combat checks with the chosen skill. Can take this focus multiple times for different skills.",
    },
}
