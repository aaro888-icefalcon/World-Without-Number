"""WWN spell tables. Extracted from WWN 1 pp.64-93, WWN 2 pp.1-55.

Each spell has: name, level, tradition, description.
Spells are shared across traditions that can access them.
High Magic spells are available to all spellcasting traditions.
"""

SPELLS = [
    # ── High Magic Level 1 ───────────────────────────────────────────────────
    {"name": "Apprehending the Arcane Form", "level": 1, "tradition": "high_mage",
     "description": "Detect magical effects, items, and auras within 100 feet for one scene."},
    {"name": "The Coruscating Coffin", "level": 1, "tradition": "high_mage",
     "description": "Encase a target in crackling energy. 1d8 damage and they are immobilized for 1 round. Physical save negates."},
    {"name": "Dazzling Prismatic Spray", "level": 1, "tradition": "high_mage",
     "description": "Spray of light blinds creatures in a 20-foot cone for 1 round. Physical save negates."},
    {"name": "Elemental Counterstroke", "level": 1, "tradition": "high_mage",
     "description": "As an Instant, deal 1d6 damage per caster level to a creature that just dealt you damage. Max 5d6."},
    {"name": "The Excellent Prismatic Spray", "level": 1, "tradition": "high_mage",
     "description": "Shoot a ray of prismatic energy at a target within 200 feet. 2d6 damage, half on Physical save."},
    {"name": "Hartley's Hasty Habiliment", "level": 1, "tradition": "high_mage",
     "description": "Instantly don armor and equipment stored in a prepared extradimensional pocket."},
    {"name": "Imperceptible Cerebral Divination", "level": 1, "tradition": "high_mage",
     "description": "Read surface thoughts of a target within 100 feet for one scene. Mental save negates."},
    {"name": "Lexicon of the Unspoken Name", "level": 1, "tradition": "high_mage",
     "description": "Understand and speak any language for one scene."},
    {"name": "Mark of the Last Heir", "level": 1, "tradition": "high_mage",
     "description": "Place a magical mark on an object or location. You can sense its direction and distance for 1 day."},
    {"name": "The Omniscient Mote", "level": 1, "tradition": "high_mage",
     "description": "Create a mote of light you can see and hear through. It moves at your will within 100 feet. Lasts one scene."},
    {"name": "Perfect Transparency", "level": 1, "tradition": "high_mage",
     "description": "Turn invisible for one scene. Attacking or casting another spell ends the invisibility."},
    {"name": "The Pestilential Servitor", "level": 1, "tradition": "high_mage",
     "description": "Summon a vermin swarm that attacks enemies in a 10-foot area. 1d4 damage per round. Lasts one scene."},
    {"name": "Sapient Ward", "level": 1, "tradition": "high_mage",
     "description": "Create a magical alarm on a door, passage, or 20-foot area. Triggers when a creature enters. Lasts 8 hours."},

    # ── High Magic Level 2 ───────────────────────────────────────────────────
    {"name": "Brilliant Effulgence of Solar Wrath", "level": 2, "tradition": "high_mage",
     "description": "Blazing ray deals 3d8 damage to a target within 200 feet. Physical save for half."},
    {"name": "Decree of Merciful Sanctuary", "level": 2, "tradition": "high_mage",
     "description": "Ward a 20-foot area. Creatures entering must make a Mental save or be compelled to leave peacefully. Lasts one scene."},
    {"name": "Eldritch Filaments of Binding", "level": 2, "tradition": "high_mage",
     "description": "Magical cords restrain a target within 100 feet. Physical save to break free. Lasts one scene."},
    {"name": "The Howl of Light", "level": 2, "tradition": "high_mage",
     "description": "Deafening light blast in a 30-foot cone. 2d6 damage and deafened for 1 round. Physical save for half and no deafness."},
    {"name": "Transmutation of Form", "level": 2, "tradition": "high_mage",
     "description": "Transform a willing creature into another creature of similar size. Lasts one scene. Mental save if unwilling."},
    {"name": "Wall of Elemental Barrier", "level": 2, "tradition": "high_mage",
     "description": "Create a wall of fire, ice, or stone up to 60 feet long and 10 feet high. Lasts one scene."},

    # ── High Magic Level 3 ───────────────────────────────────────────────────
    {"name": "Astral Reaching", "level": 3, "tradition": "high_mage",
     "description": "Teleport yourself and up to 3 willing creatures within touch to a location you can see or have visited."},
    {"name": "Compulsive Direction", "level": 3, "tradition": "high_mage",
     "description": "Compel a target to follow a single command of no more than 10 words. Mental save negates. Lasts 1 round."},
    {"name": "Plasmic Torrent", "level": 3, "tradition": "high_mage",
     "description": "Torrent of arcane energy in a 30-foot cone. 5d6 damage. Physical save for half."},

    # ── High Magic Level 4 ───────────────────────────────────────────────────
    {"name": "Disjunctive Blast", "level": 4, "tradition": "high_mage",
     "description": "Dispel all magical effects in a 30-foot radius. Permanent items get a Luck save. Temporary effects are destroyed."},
    {"name": "Sovereign Panoply of Invulnerability", "level": 4, "tradition": "high_mage",
     "description": "Surround yourself with an invulnerable shield. Immune to all damage for 1 round. No actions while shielded."},

    # ── High Magic Level 5 ───────────────────────────────────────────────────
    {"name": "Fury of the Final Conflagration", "level": 5, "tradition": "high_mage",
     "description": "Cataclysmic blast in a 40-foot radius. 10d6 damage. Physical save for half. Ignites flammables."},

    # ── Elementalist Level 1 ─────────────────────────────────────────────────
    {"name": "Call of the Thunderbolt", "level": 1, "tradition": "elementalist",
     "description": "Lightning bolt strikes a target within 200 feet for 1d8+1 damage. Arcs to one adjacent target for half."},
    {"name": "Flame Scrying", "level": 1, "tradition": "elementalist",
     "description": "Gaze into a fire to see and hear events near another fire you have previously visited. Lasts one scene."},
    {"name": "Gust of the Sand Wyrm", "level": 1, "tradition": "elementalist",
     "description": "Fierce gust in a 60-foot line. Creatures must Physical save or be knocked prone. Extinguishes small fires."},
    {"name": "Hands of the Earth", "level": 1, "tradition": "elementalist",
     "description": "Stone hands erupt from the ground and grasp a target. Physical save or immobilized for 1 round."},
    {"name": "Mantle of the Ice Witch", "level": 1, "tradition": "elementalist",
     "description": "Coat yourself in frost armor. +2 AC and creatures that hit you in melee take 1d4 cold damage. Lasts one scene."},
    {"name": "Pyroclastic Bolt", "level": 1, "tradition": "elementalist",
     "description": "Hurl a bolt of molten rock at a target within 200 feet. 2d6 fire damage. Physical save for half."},
    {"name": "Rain of Gentle Restoration", "level": 1, "tradition": "elementalist",
     "description": "Gentle rain falls in a 20-foot area. All allies in the area heal 1d6+1 HP."},
    {"name": "Shattering of the Crystal Vault", "level": 1, "tradition": "elementalist",
     "description": "Shards of ice in a 20-foot cone. 1d6 damage per 2 caster levels (max 3d6). Physical save for half."},
    {"name": "Stone Sense", "level": 1, "tradition": "elementalist",
     "description": "Sense vibrations through stone/earth within 100 feet. Detect hidden creatures, tunnels, and structural weaknesses."},
    {"name": "Tidal Wave", "level": 1, "tradition": "elementalist",
     "description": "A wave of water surges in a 30-foot line. 1d6 damage and knocked prone. Physical save negates prone."},

    # ── Elementalist Level 2 ─────────────────────────────────────────────────
    {"name": "Eruption of the Molten Heart", "level": 2, "tradition": "elementalist",
     "description": "Magma erupts in a 15-foot radius. 3d6 fire damage and the area becomes difficult terrain. Physical save for half."},
    {"name": "Glacial Prison", "level": 2, "tradition": "elementalist",
     "description": "Encase a target in ice. 2d6 cold damage and immobilized. Physical save for half damage and no immobilization."},
    {"name": "Stormwall", "level": 2, "tradition": "elementalist",
     "description": "Create a wall of howling wind 60 feet long. Ranged attacks through it have -4 to hit. Lasts one scene."},

    # ── Elementalist Level 3 ─────────────────────────────────────────────────
    {"name": "Earthquake", "level": 3, "tradition": "elementalist",
     "description": "Violent tremors in a 60-foot radius. 4d6 damage to structures and creatures on the ground. Physical save for half."},
    {"name": "Firestorm", "level": 3, "tradition": "elementalist",
     "description": "Rain of fire in a 40-foot radius. 5d6 fire damage. Physical save for half. Ignites flammables."},

    # ── Necromancer Level 1 ──────────────────────────────────────────────────
    {"name": "Beckoning of the Hungry Grave", "level": 1, "tradition": "necromancer",
     "description": "Raise 1 HD of undead per caster level from available corpses. They serve for one scene."},
    {"name": "Blade of Black Entropy", "level": 1, "tradition": "necromancer",
     "description": "Imbue a weapon with necrotic energy. +1d6 necrotic damage per hit for one scene. Heals wielder for half."},
    {"name": "Caul of Night", "level": 1, "tradition": "necromancer",
     "description": "Create an area of magical darkness in a 30-foot radius. Only you can see through it. Lasts one scene."},
    {"name": "Choking Doom of Dust", "level": 1, "tradition": "necromancer",
     "description": "Dust fills a target's lungs. 1d8 damage per round until Physical save succeeds. Max 3 rounds."},
    {"name": "Cold Grasp of the Departed", "level": 1, "tradition": "necromancer",
     "description": "Spectral hand chills a target for 2d6 cold/necrotic damage. Physical save for half."},
    {"name": "Enfeebling Wave", "level": 1, "tradition": "necromancer",
     "description": "Wave of enervation in a 20-foot cone. -2 to attack rolls and damage for 1 round. Physical save negates."},
    {"name": "Speak with Dead", "level": 1, "tradition": "necromancer",
     "description": "Question a corpse. It answers up to 3 questions truthfully from its knowledge in life."},
    {"name": "The Ravening Swarm", "level": 1, "tradition": "necromancer",
     "description": "Summon a swarm of skeletal vermin. 1d6 damage per round to all in a 10-foot area. Lasts one scene."},
    {"name": "Terrifying Visage", "level": 1, "tradition": "necromancer",
     "description": "Your face becomes terrifyingly gaunt. All enemies within 30 feet must Mental save or flee for 1 round."},
    {"name": "Withering Curse", "level": 1, "tradition": "necromancer",
     "description": "Curse a target within 100 feet. -1 to all rolls for one scene. Mental save negates."},

    # ── Necromancer Level 2 ──────────────────────────────────────────────────
    {"name": "Animate Revenant", "level": 2, "tradition": "necromancer",
     "description": "Create a powerful undead servant from a corpse. HD equal to your level. Serves for 1 day."},
    {"name": "Deathly Convocation", "level": 2, "tradition": "necromancer",
     "description": "Commune with the spirits of the dead in the area. Learn one fact about local history per question (3 max)."},
    {"name": "Soul Shackles", "level": 2, "tradition": "necromancer",
     "description": "Bind a dying creature's soul. They cannot die while bound but suffer 1d6 damage per round. Mental save breaks."},

    # ── Necromancer Level 3 ──────────────────────────────────────────────────
    {"name": "Plague Wind", "level": 3, "tradition": "necromancer",
     "description": "Poisonous wind in a 40-foot cone. 4d6 necrotic damage and poisoned for 1 day. Physical save for half and no poison."},
    {"name": "Reign of the Unliving", "level": 3, "tradition": "necromancer",
     "description": "Raise all corpses within 100 feet as undead servants. Total HD cannot exceed your level x 3. Lasts one scene."},

    # ── Elementalist Level 4 ─────────────────────────────────────────────────
    {"name": "Cataclysm of the Shattered Peak", "level": 4, "tradition": "elementalist",
     "description": "Cause a massive rockslide or avalanche in a 60-foot area. 6d6 bludgeoning damage and the terrain becomes impassable rubble. Physical save for half damage."},
    {"name": "Maelstrom of the Four Winds", "level": 4, "tradition": "elementalist",
     "description": "Summon a howling vortex of all four elements in a 30-foot radius. 5d6 damage of mixed types each round for 3 rounds. Physical save each round for half."},

    # ── Elementalist Level 5 ─────────────────────────────────────────────────
    {"name": "Wrath of the World's Heart", "level": 5, "tradition": "elementalist",
     "description": "Channel the planet's elemental fury. 40-foot radius eruption deals 8d6 fire and earth damage. Terrain permanently altered. Physical save for half."},

    # ── Necromancer Level 4 ──────────────────────────────────────────────────
    {"name": "Legion of the Restless Dead", "level": 4, "tradition": "necromancer",
     "description": "Raise up to 20 HD of undead from available corpses. They serve until destroyed or dismissed. Maximum 3 days duration."},
    {"name": "Soul Harvest", "level": 4, "tradition": "necromancer",
     "description": "When a creature dies within 100 feet, capture its soul energy. Heal 2d8 HP and recover one committed Effort. Lasts one scene."},

    # ── Necromancer Level 5 ──────────────────────────────────────────────────
    {"name": "Dominion of the Grave", "level": 5, "tradition": "necromancer",
     "description": "All undead within 200 feet fall under your absolute control. Living creatures in the area must Mental save or be paralyzed with dread for 1 round. Control lasts one scene."},
]

# Arts are already defined in traditions.py — ARTS list here for import compatibility
ARTS = []
for _trad_name in ["high_mage", "elementalist", "necromancer", "healer", "vowed"]:
    try:
        from traditions import TRADITIONS as _TRADITIONS
        for _art in _TRADITIONS.get(_trad_name, {}).get("arts", []):
            ARTS.append({**_art, "tradition": _trad_name})
    except ImportError:
        pass
