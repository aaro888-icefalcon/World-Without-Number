# Exploration Domain — Content Inventory

Phase 3 domain for travel, scene generation, treasure, and dungeon mechanics.

## Scripts

| Script | Purpose | CLI Command |
|--------|---------|-------------|
| `scripts/travel.py` | Overland travel, foraging, privation, encounters | `travel --terrain --days --supplies` |
| `scripts/scene.py` | Tag-based scene generation (wilderness, ruin, community) | `generate-scene --scene-type` |
| `scripts/treasure.py` | Treasure rolls by tier (1-5) with coins, items, and magic items (tier 3+) | `treasure --tier` |
| `scripts/dungeon.py` | Procedural dungeon generation with rooms, encounters, hazards | `generate-dungeon --depth [--theme]` |

## Tables

| Table | Purpose | Entries |
|-------|---------|--------|
| `tables/wilderness_tags.py` | Wilderness environment tags for scene generation | 52+ tags |
| `tables/ruin_tags.py` | Ruin/dungeon environment tags for scene generation | 50+ tags |
| `tables/community_tags.py` | Community/settlement tags for scene generation | 50+ tags |

## Cross-Domain References

| External Table | Location | Used By |
|---------------|----------|---------|
| `core/tables/magic_items.py` | 36 tiered magic items | treasure.py (tier 3+ treasure) |
| `combat/tables/encounter_tables.py` | Terrain-creature mapping | travel.py encounter resolution, dungeon.py |
| `combat/tables/bestiary.py` | 83 creature stat blocks | encounter_tables.py (via get_creature()) |

## Known Gaps

- No `scene_pressure.py` or `adventure.py` (referenced in checklist but not yet created)
