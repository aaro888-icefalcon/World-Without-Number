# Phase 3 — Mechanical Resolution: Content Inventory

All game mechanics are resolved through emergence_cli.py subcommands. Scripts and tables are physically co-located with their domain skills.

## Domains

| Domain | Directory | Purpose |
|---|---|---|
| core | `skills/core/` | Dice, character creation, conditions, base mechanics |
| combat | `skills/combat/` | Attack resolution, morale, bestiary, zone positioning |

## Domain: Core

### Scripts
| File | Purpose |
|---|---|
| `skills/core/scripts/dice.py` | Seedable deterministic dice roller with arithmetic trace |
| `skills/core/scripts/character.py` | Character creation engine |
| `skills/core/scripts/conditions.py` | Status effects and System Strain tracking |

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

### Tables
| File | Purpose |
|---|---|
| `skills/combat/tables/bestiary.py` | Creature stat blocks |

### References
| File | Purpose |
|---|---|
| `skills/combat/references/combat-rules.md` | WWN combat procedures (initiative, actions, damage, shock, morale) |
