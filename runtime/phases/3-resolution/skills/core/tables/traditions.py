"""WWN magic tradition definitions. Extracted from WWN 1 pp.60-93, WWN 2 pp.1-55."""

TRADITIONS = {
    "high_mage": {
        "description": "Classical wizard tradition. Masters of versatile arcane spells learned through study and practice.",
        "partial_only": False,
        "has_spells": True,
        "restrictions": [
            "Cannot cast spells while wearing armor heavier than normal clothing",
        ],
        "arts": [
            {"name": "Arcane Lexicon", "effort": "none", "description": "Can read any language and identify magical writing. Gain Magic-0 if unskilled."},
            {"name": "Counter Magic", "effort": "scene", "description": "As an Instant action, commit Effort for the scene to negate a spell targeting you or an ally within sight."},
            {"name": "Empowered Sorcery", "effort": "scene", "description": "Commit Effort for the scene to maximize the dice of a spell's damage or healing."},
            {"name": "Hang Sorcery", "effort": "day", "description": "Commit Effort for the day to prepare a spell for instant casting later. Casting the hung spell is an Instant action."},
            {"name": "Inexorable Effect", "effort": "scene", "description": "Commit Effort for the scene. A target that saves against your spell still suffers a lesser version of the effect."},
            {"name": "Preparatory Countermagic", "effort": "scene", "description": "Commit Effort for the scene as an Instant when you detect an incoming spell. You and allies within 20 feet gain +4 on saves against it."},
            {"name": "Reflexive Cast", "effort": "day", "description": "Commit Effort for the day to cast a spell as an Instant action instead of a Main Action. The spell must be level 1."},
            {"name": "Restrained Casting", "effort": "none", "description": "You can shape your area-effect spells to exclude up to 1 ally per caster level from the effect."},
            {"name": "Sense Magic", "effort": "scene", "description": "Commit Effort for the scene to detect magical effects, auras, and enchantments within 100 feet."},
            {"name": "Suppress Magic", "effort": "scene", "description": "Commit Effort for the scene to temporarily suppress a magical effect you can see."},
            {"name": "Swift Casting", "effort": "day", "description": "Commit Effort for the day to cast a prepared spell without losing it from your prepared list."},
            {"name": "Ward Allies", "effort": "scene", "description": "Commit Effort for the scene to grant an ally within 50 feet a +2 bonus to saves against magic."},
        ],
    },
    "elementalist": {
        "description": "Wielder of primal elemental forces — fire, water, earth, air, and combinations thereof.",
        "partial_only": False,
        "has_spells": True,
        "restrictions": [
            "Cannot cast spells while wearing metal armor",
        ],
        "arts": [
            {"name": "Elemental Resilience", "effort": "none", "description": "Gain resistance to one chosen element. Take half damage from that element. Gain Magic-0 if unskilled."},
            {"name": "Elemental Blast", "effort": "scene", "description": "Commit Effort for the scene. Hurl a bolt of elemental energy: 1d8 damage per 2 caster levels, 200 ft range."},
            {"name": "Elemental Sparks", "effort": "none", "description": "Produce minor elemental effects at will: light a candle, chill a drink, stir a breeze, move a handful of earth."},
            {"name": "Pavis of Elements", "effort": "scene", "description": "Commit Effort for the scene. Create an elemental shield granting +2 AC for the scene."},
            {"name": "Elemental Weapon", "effort": "scene", "description": "Commit Effort for the scene. Imbue a weapon with elemental energy: +1d6 elemental damage per hit."},
            {"name": "Beckoned Deluge", "effort": "day", "description": "Commit Effort for the day. Create a 20-foot-radius elemental area effect: 1d6 damage per caster level."},
            {"name": "Elemental Aegis", "effort": "day", "description": "Commit Effort for the day. Grant an ally immunity to one element for the scene."},
        ],
    },
    "necromancer": {
        "description": "Master of death magic, undead creation, and the manipulation of life force.",
        "partial_only": False,
        "has_spells": True,
        "restrictions": [
            "Social penalty: -1 reaction rolls in civilized areas where necromancy is known",
            "Cannot cast spells while wearing metal armor",
        ],
        "arts": [
            {"name": "Charnel Breath", "effort": "none", "description": "Immune to diseases and poisons. Can detect undead within 100 feet. Gain Magic-0 if unskilled."},
            {"name": "Command the Dead", "effort": "scene", "description": "Commit Effort for the scene. Command unintelligent undead within 100 feet. HD of controlled undead cannot exceed caster level x 2."},
            {"name": "Consume Life Energy", "effort": "scene", "description": "Commit Effort for the scene. Touch a freshly dead creature to heal 1d6+level HP."},
            {"name": "Red Harvest", "effort": "scene", "description": "Commit Effort for the scene. When you kill a creature, gain temporary HP equal to its HD."},
            {"name": "Raise the Dead", "effort": "day", "description": "Commit Effort for the day. Raise a corpse as an undead servant with HD equal to half your level."},
            {"name": "Pale Countenance", "effort": "none", "description": "Undead do not attack you unless commanded to. You can communicate with unintelligent undead."},
            {"name": "Life Bridge", "effort": "scene", "description": "Commit Effort for the scene. Transfer HP from yourself to a touched ally, or drain HP from a touched enemy."},
        ],
    },
    "healer": {
        "description": "Magically gifted physician who channels supernatural healing power. Partial tradition only.",
        "partial_only": True,
        "has_spells": False,
        "restrictions": [
            "Must not deliberately cause lethal harm to a creature that has not attacked them or their allies",
        ],
        "arts": [
            {"name": "Healing Touch", "effort": "scene", "description": "Commit Effort for the scene. As a Main Action, heal a touched ally for 2d6+level HP. Gain Heal-0 if unskilled."},
            {"name": "Purge Ailment", "effort": "scene", "description": "Commit Effort for the scene. Cure one disease, poison, or mundane physical ailment in a touched creature."},
            {"name": "Vital Sense", "effort": "none", "description": "Can diagnose any disease, poison, or physical ailment by touch. Sense life and death within 50 feet."},
            {"name": "Empowered Healer", "effort": "day", "description": "Commit Effort for the day. Your next Healing Touch heals maximum dice and removes one condition."},
            {"name": "Stabilize", "effort": "none", "description": "As a Main Action, automatically stabilize a dying creature within touch range. No check required."},
            {"name": "Shield of Life", "effort": "day", "description": "Commit Effort for the day. An ally within sight cannot be reduced below 1 HP for one round."},
        ],
    },
    "vowed": {
        "description": "Ascetic martial artist who channels supernatural power through bodily discipline. Partial tradition only.",
        "partial_only": True,
        "has_spells": False,
        "restrictions": [
            "Cannot wear armor",
            "Cannot use weapons other than unarmed attacks and monk weapons (staff, dagger, short sword)",
        ],
        "arts": [
            {"name": "Unarmed Might", "effort": "none", "description": "Unarmed attacks deal 1d8 damage and are not considered Less Lethal. Gain Punch-0 if unskilled."},
            {"name": "Unarmored Defense", "effort": "none", "description": "While unarmored, AC equals 10 + half level (rounded up) + Wis modifier."},
            {"name": "Flurry of Blows", "effort": "scene", "description": "Commit Effort for the scene. Make two unarmed attacks as a single Main Action."},
            {"name": "Iron Skin", "effort": "scene", "description": "Commit Effort for the scene. Gain damage reduction 2 against all physical attacks."},
            {"name": "Inner Force", "effort": "day", "description": "Commit Effort for the day. Your next unarmed attack deals maximum damage."},
            {"name": "Wind Step", "effort": "scene", "description": "Commit Effort for the scene. Move up to 30 extra feet as a free action once per round."},
        ],
    },
}
