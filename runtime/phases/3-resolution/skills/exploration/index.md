# Exploration Domain — Content Inventory

Phase 3 domain for travel, scene generation, and treasure mechanics.

## Scripts

| Script | Purpose | CLI Command |
|--------|---------|-------------|
| `scripts/travel.py` | Overland travel, foraging, privation, encounters | `travel --terrain --days --supplies` |
| `scripts/scene.py` | Tag-based scene generation (wilderness, ruin, community) | `generate-scene --scene-type` |
| `scripts/treasure.py` | Treasure rolls by tier (1-5) with coins and items | `treasure --tier` |

## Tables

| Table | Purpose | Entries |
|-------|---------|--------|
| `tables/wilderness_tags.py` | Wilderness environment tags for scene generation | 22 tags |
| `tables/ruin_tags.py` | Ruin/dungeon environment tags for scene generation | 22 tags |
| `tables/community_tags.py` | Community/settlement tags for scene generation | 22 tags |

## Known Gaps

- No terrain-specific encounter content tables (travel.py uses binary encounter check only)
- No magic item tables (treasure.py has mundane items only)
- No `scene_pressure.py` or `adventure.py` (referenced in checklist but not yet created)
