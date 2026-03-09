# Exploration Domain — Tag Tables Population

**Status:** In Progress
**Start date:** 2026-03-08
**Surfaces touched:** Phase 3 tables (new files), Phase manifest (update), Tests (new), Documentation (index.md)

## Objective

Populate the three tag table files that `scene.py` already imports but which don't exist, completing the scene generation pipeline. This is the highest-impact gap: scene.py falls back to 4 hardcoded descriptions per type instead of generating emergent content from tag combinations.

## Scope

### In scope
- T1: Create `exploration/tables/` directory
- T2: Create `wilderness_tags.py` with WILDERNESS_TAGS (20+ entries)
- T3: Create `ruin_tags.py` with RUIN_TAGS (20+ entries)
- T4: Create `community_tags.py` with COMMUNITY_TAGS (20+ entries)
- T5: Create `exploration/index.md` (content inventory)
- T6: Update `phase-manifest.md` to list new table files
- T7: Create `test_exploration_tables.py` (validates tag structure + scene.py integration)
- T8: Register test in `run_all_tests.py` OPTIONAL_MODULES

### Out of scope (future work)
- Encounter content tables for travel.py (requires script modification)
- Magic item tables for treasure.py (requires script modification)
- scene_pressure.py / adventure.py (referenced in checklist but don't exist yet)

## Tag Schema Contract

scene.py expects each tag to be a dict with these keys (lines 60-70):
```python
{
    "name": str,           # tag name (used in scene_seed)
    "description": str,    # narrative description (used in scene_seed)
    "enemies": str,        # enemy element for this tag
    "friends": str,        # friendly NPC/creature element
    "complications": str,  # complication element
    "things": str,         # notable object/item element
    "places": str,         # location element
}
```

All keys use `.get()` (optional access), so missing keys won't crash — but all should be populated for content depth.

## Implementation Order

1. T7 first (test-first approach) — write test that validates tag structure and scene.py integration
2. T1 — create tables directory
3. T2, T3, T4 — create tag files (parallelizable)
4. T5 — create index.md
5. T6 — update phase-manifest.md
6. T8 — register test
7. Run validation suite

## Tag Content Guidelines

- Each tag file should have 20-25 entries for good combinatorial variety
- Tags should be genre-appropriate (Latter Earth / Worlds Without Number tone: post-apocalyptic fantasy, ancient ruins, dying civilizations)
- wilderness_tags: natural environments, terrain features, flora/fauna, weather phenomena, magical residue
- ruin_tags: ancient structures, traps, architectural features, former inhabitants, depth-appropriate threats
- community_tags: settlement types, social dynamics, local concerns, notable features, trade/economy
- Every tag MUST have all 6 content keys populated (name, description, enemies, friends, complications, things, places)
- No `__init__.py` needed — scene.py uses sys.path insertion to import bare module names

## Test Requirements

- Test validates tag schema: every tag in every table has all 6 required keys, all values are non-empty strings
- Test validates tag name uniqueness within each table (prevents duplicate scene seeds)
- Test validates import path: scene.py's `_load_tags()` returns the actual table (not empty list)
- Test validates scene generation: `generate_scene()` returns tag-based output (not fallback) — asserts `"fallback" not in result["tags_used"]`
- Test validates `generate_ruin()` returns depth_level and has_treasure keys
- Test uses `random.seed()` for deterministic assertions
- Test must be self-contained (no external fixtures)
- Test follows `run_test()` convention used by run_all_tests.py

## Risks

- **R1 (low):** sys.path bare-name imports could collide if another domain adds identically-named files — accepted (existing pattern across all domains)
- **R2 (low):** community_tags overlap with social domain — mitigated by scope being exploration-scene-specific (scene.py owns this import)
- **R3 (none):** No existing scripts modified — zero regression risk to travel.py or treasure.py

## Exit Criteria

1. `scene.py._load_tags("wilderness")` returns 20+ tags
2. `scene.py._load_tags("ruin")` returns 20+ tags
3. `scene.py._load_tags("community")` returns 20+ tags
4. `scene.py.generate_scene()` no longer falls back to `_generate_fallback_scene()`
5. All tag dicts have all 6 required keys with non-empty string values
6. `test_exploration_tables.py` passes
7. `run_all_tests.py` passes (existing tests unbroken)
8. `phase-manifest.md` lists the 3 new table files
9. `exploration/index.md` lists all scripts and tables

## Analysis Pass 1 — Weaknesses Found & Fixed

| # | Weakness | Resolution |
|---|----------|------------|
| W1 | sys.path collision risk | Documented in Risks as R1 (accepted, existing pattern) |
| W2 | No __init__.py question | Confirmed not needed (no other domain uses them) |
| W3 | Tag schema not validated at import | Test Requirements section added |
| W5 | No random.seed in test plan | Test Requirements: "uses random.seed()" |
| W6 | Content tone not specified | Tag Content Guidelines expanded with Latter Earth tone |
| W7 | Active plans index.md not updated | Added to implementation steps |

## Analysis Pass 2 — Weaknesses Found & Fixed

| # | Weakness | Resolution |
|---|----------|------------|
| W8 | Tag name uniqueness not enforced | Test Requirements: "validates tag name uniqueness within each table" |
| W9 | generate_ruin() not tested | Test Requirements: "validates generate_ruin() returns depth_level and has_treasure keys" |
| W10 | Test module naming convention | Already consistent: test_exploration_tables.py matches test_state_schema.py |
| W11 | change-integration-checklist.md inaccurate | Pre-existing issue, out of scope |
| W12 | Exit criterion 4 hard to test | Clarified: assert "fallback" not in result["tags_used"] (scene.py line 130) |
| W13 | run_all_tests.py import discovery | Confirmed: auto-adds tables/ to sys.path; test will use both direct import and scene.py |
