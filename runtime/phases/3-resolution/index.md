# Phase 3 — Mechanical Resolution: Content Inventory

All game mechanics are resolved through emergence_cli.py subcommands. Scripts and tables are physically co-located with their domain skills.

## Domains

| Domain | Directory | Purpose |
|---|---|---|
| core | `skills/core/` | Dice, character creation, conditions, magic, base mechanics |
| combat | `skills/combat/` | Attack resolution, morale, bestiary, zone positioning, behavior AI, encounters |
| exploration | `skills/exploration/` | Travel, scene generation, treasure |
| social | `skills/social/` | NPC generation, reaction rolls, faction turns, diplomacy, consequences |
| world-building | `skills/world-building/` | World tick, clock advancement, world pulse |
| downtime | `skills/downtime/` | Crafting, alchemy, training (placeholder) |

## Domain: Core

### Scripts
| File | Purpose |
|---|---|
| `skills/core/scripts/dice.py` | Seedable deterministic dice roller with arithmetic trace |
| `skills/core/scripts/character.py` | Character creation engine |
| `skills/core/scripts/conditions.py` | Status effects and System Strain tracking |
| `skills/core/scripts/magic.py` | Spell casting, Effort, arts, tradition management |

### Tables
| File | Purpose |
|---|---|
| `skills/core/tables/attributes.py` | Attribute modifiers (3-18 → -2 to +2) |
| `skills/core/tables/skills.py` | 22 skill definitions with difficulty thresholds |
| `skills/core/tables/equipment.py` | Weapons, armor, gear with traits and costs |
| `skills/core/tables/classes.py` | Class progression (warrior/expert/mage), XP table |
| `skills/core/tables/backgrounds.py` | 20 backgrounds with growth/learning tables |
| `skills/core/tables/foci.py` | Focus definitions with level 1/2 effects |

## Domain: Combat

### Scripts
| File | Purpose |
|---|---|
| `skills/combat/scripts/combat.py` | Attack resolution, shock, morale, zone-based positioning |
| `skills/combat/scripts/behavior.py` | Creature combat AI, behavior trees, decision-making |
| `skills/combat/scripts/encounter.py` | Random encounter generation by terrain/threat |

### Tables
| File | Purpose |
|---|---|
| `skills/combat/tables/bestiary.py` | Creature stat blocks |

### References
| File | Purpose |
|---|---|
| `skills/combat/references/combat-rules.md` | WWN combat procedures (initiative, actions, damage, shock, morale) |

## Domain: Exploration

### Scripts
| File | Purpose |
|---|---|
| `skills/exploration/scripts/travel.py` | Multi-day overland travel, foraging, privation, encounters |
| `skills/exploration/scripts/scene.py` | Tag-based scene generation |
| `skills/exploration/scripts/treasure.py` | Treasure rolls by tier (1-5) |

## Domain: Social

### Scripts
| File | Purpose |
|---|---|
| `skills/social/scripts/npc.py` | NPC generation with voice cards, personality, motivation |
| `skills/social/scripts/faction.py` | Faction turn processing, AI-driven action selection |
| `skills/social/scripts/diplomacy.py` | Persuasion checks, bribe costs, negotiation, favor tracking |
| `skills/social/scripts/consequence.py` | Consequence tracker — timer-based trigger checking |

### Tables
| File | Purpose |
|---|---|
| `skills/social/tables/character_tags.py` | d100 NPC character tags |
| `skills/social/tables/court_tags.py` | Court intrigue environment tags |
| `skills/social/tables/faction_actions.py` | Faction action definitions with costs/requirements |

### References
| File | Purpose |
|---|---|
| `skills/social/references/npc-reactions.md` | NPC reaction table, modifiers, disposition changes |
| `skills/social/references/faction-rules.md` | Faction turn structure, assets, conflict resolution |
| `skills/social/references/court-intrigue.md` | Court structure, social maneuvering, schemes |

## Domain: World-Building

### Scripts
| File | Purpose |
|---|---|
| `skills/world-building/scripts/world_tick.py` | World state advancement, clock management, world pulse |

### Tables
| File | Purpose |
|---|---|
| `skills/world-building/tables/government_tables.py` | Government types and generation tables |
| `skills/world-building/tables/society_tables.py` | Society types and cultural features |
| `skills/world-building/tables/religion_tables.py` | Religion types, practices, leadership |

## Domain: Downtime

(Placeholder — to be implemented in Phase G)
