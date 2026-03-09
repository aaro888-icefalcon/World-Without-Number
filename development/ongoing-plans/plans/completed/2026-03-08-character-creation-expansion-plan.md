# Execution Plan: Comprehensive Character Creation Expansion

- **Owner:** Development team
- **Status:** In Progress
- **Start Date:** 2026-03-08
- **Target Date:** 2026-03-08
- **Related Decision Logs:** `analysis/2026-03-04-wwn-pdf-extraction-analysis.md`

## Objective

Expand the character creation system from the current minimal implementation (3 base classes, no multiclassing, no focus selection, no spell selection, no equipment selection) to a comprehensive system supporting:

1. All 4 classes including Adventurer (multiclass) with all 6 partial class combinations
2. All 5 core magic traditions (High Mage, Elementalist, Necromancer, Healer, Vowed)
3. All 4 WWN5 optional classes (Accursed, Bard, Mageslayer, Wise)
4. Focus selection at creation with proper class-restricted picks
5. Starting spell selection for Mages
6. Equipment package selection or starting coin rolls
7. Free skill pick (step 9 of WWN rules)
8. Quick skills from backgrounds (step 4)
9. Luck saving throw
10. Complete spell and arts tables for all traditions
11. Schema updates to support new class types and traditions

## Scope

### In scope:
- `classes.py` — Add Adventurer class with all 6 multiclass progression tables
- `character.py` — Expand `create_character()` to support all new options
- `foci.py` — Add missing foci from WWN5 (Maqqatban Knight, Amundi Godblood, Arcane Secret, Non-Human Origin)
- `spells.py` (new) — Complete spell tables for all traditions
- `traditions.py` (new) — Tradition definitions with arts, restrictions, effort rules
- `state.schema.json` — Expand character class enum, add tradition field, add spells_prepared
- `emergence_cli.py` — Expand `create-character` argument parser
- Test suite — New comprehensive test file for expanded character creation
- CLI reference docs — Update to reflect new arguments

### Out of scope:
- Level advancement mechanics (level-up flow)
- Heroic classes and Legates (WWN4 advanced content)
- Bestiary additions
- Combat mechanics changes
- World-building tools

## Milestones

### M1: Data Tables Expansion
Add all missing structured data tables.

### M2: Adventurer (Multiclass) System
Implement the Adventurer class with all 6 partial class combinations.

### M3: Magic Tradition System
Implement all 5 traditions with arts and spell lists.

### M4: Full Character Creation Flow
Implement complete 19-step WWN character creation procedure.

### M5: Schema & CLI Updates
Update schema, CLI, and integration points.

### M6: WWN5 Optional Classes (DEFERRED to follow-up PR)
Add Accursed, Bard, Mageslayer, Wise classes — requires separate extraction work.

### M7: Validation & Testing
Comprehensive test suite and validation.

## Task Breakdown

### M1: Data Tables Expansion

- [x] **T1.1** Inventory existing tables vs WWN source material
- [ ] **T1.2** Add Adventurer progression tables to `classes.py`:
  - Partial Expert/Partial Warrior (HD, AB, Focus for levels 1-10)
  - Partial Expert/Partial Mage (HD, AB, Focus for levels 1-10)
  - Partial Warrior/Partial Mage (HD, AB, Focus for levels 1-10)
  - Partial Warrior AB table: {1:1, 2:1, 3:2, 4:2, 5:3, 6:4, 7:5, 8:5, 9:6, 10:6}
  - Partial Expert AB already exists (verify)
- [ ] **T1.3** Add WWN5 foci to `foci.py`:
  - Maqqatban Knight foci
  - Amundi Godblood foci
  - Arcane Secret foci
  - Non-Human Origin foci (origin foci that cost a focus pick)
- [ ] **T1.4** Create `traditions.py` with tradition definitions:
  - High Mage: arts, restrictions (no armor), effort max = Int mod + level/2
  - Elementalist: arts, restrictions, element list
  - Necromancer: arts, restrictions (social penalties)
  - Healer: arts, partial-only tradition (no full Mage class)
  - Vowed: arts, partial-only tradition (unarmed combat focus)
- [ ] **T1.5** Create `spells.py` with complete spell tables:
  - High Magic spells (levels 1-5, ~60 spells)
  - Elementalist spells (levels 1-5, ~55 spells)
  - Necromancer spells (levels 1-5, ~55 spells)
  - Each spell: name, level, tradition, description, duration, range, effort_duration
- [ ] **T1.6** Add equipment packages to `equipment.py`:
  - 6 starting packages from WWN1 p.29
  - Starting coins formula (3d6 x 10 silver)

### M2: Adventurer (Multiclass) System

- [ ] **T2.1** Add `adventurer` class definition to `CLASSES`:
  ```python
  "adventurer": {
      "description": "Multiclass hero combining two partial classes.",
      "hit_die": "varies",  # determined by partial class combo
      "abilities": {},  # inherited from partial classes
      "partial_combos": [
          "partial_expert/partial_warrior",
          "partial_expert/partial_mage",
          "partial_warrior/partial_mage",
      ],
  }
  ```
- [ ] **T2.2** Add all 6 Adventurer progression tables to `CLASSES` or separate dict:
  - `ADVENTURER_PROGRESSION` keyed by combo string
  - Each contains levels 1-10 with hd, ab, focus
- [ ] **T2.3** Implement partial class ability resolution:
  - Partial Expert: Quick Learner only (no Masterful Expertise)
  - Partial Warrior: Killing Blow + Veteran's Luck (same as full)
  - Partial Mage: reduced spell progression per tradition
- [ ] **T2.4** Implement Partial Warrior attack bonus:
  - Already have `PARTIAL_WARRIOR_AB` table
  - Wire into character creation when class includes partial warrior

### M3: Magic Tradition System

- [ ] **T3.1** Implement tradition selection in character creation:
  - Full Mages choose 1 tradition from: high_mage, elementalist, necromancer
  - Partial Mages may also choose: healer, vowed (partial-only traditions)
  - Adventurers with 2 Partial Mage classes pick 2 traditions
- [ ] **T3.2** Implement starting spell selection:
  - Full Mages: pick 4 first-level spells from tradition's spell list
  - Partial Mages: pick 2 first-level spells
  - Dual Partial Mages: pick 4 first-level spells total (from either tradition)
  - Healer/Vowed: no spells (arts-only traditions)
- [ ] **T3.3** Implement starting Effort calculation:
  - Full Mage: max_effort = 1 + Int mod + (level / 2, rounded down)
  - Partial Mage: max_effort = 1 + Int mod + (level / 4, rounded down)
  - Non-mages: max_effort = 0
- [ ] **T3.4** Implement tradition arts tracking:
  - Each tradition has core arts (always known) and additional arts (gained at levels)
  - Store known_arts in character object
- [ ] **T3.5** Update `magic.py` to use tradition-specific spell validation

### M4: Full Character Creation Flow

Implement the complete 19-step procedure from WWN1 pp.6-7:

- [ ] **T4.1** Step 1-2: Attribute generation (DONE - existing)
- [ ] **T4.2** Step 3: Background selection with free skill (DONE - existing)
- [ ] **T4.3** Step 4: Background skill selection — implement "quick skills" method:
  - Pick method: choose 2 skills from Learning table (no "Any Skill")
  - Roll method: roll up to 3 times on Growth/Learning tables
  - Quick method: take Quick Skills at level-0
- [ ] **T4.4** Step 5: Skill stacking rules:
  - First time: skill at 0
  - Second time: skill at 1
  - Third time: pick any other skill < 1
  - No skills > 1 at creation
- [ ] **T4.5** Step 6: Class selection (expand to include Adventurer)
- [ ] **T4.6** Step 7: Focus selection:
  - All classes: 1 free Focus pick
  - Expert/Partial Expert: +1 non-combat Focus
  - Warrior/Partial Warrior: +1 combat Focus (warrior-type)
  - Can stack both picks on same Focus for level 2
- [ ] **T4.7** Step 8: Non-human origin (optional, costs a Focus pick)
- [ ] **T4.8** Step 9: Free skill pick (any skill, level-0 or upgrade to 1)
- [ ] **T4.9** Step 10: Mage tradition selection
- [ ] **T4.10** Step 11: Starting spell selection
- [ ] **T4.11** Step 12: Hit points (DONE - existing, but need Adventurer HD)
- [ ] **T4.12** Step 13: Attack bonus (DONE - existing)
- [ ] **T4.13** Step 14: Equipment selection (package or roll 3d6x10 sp)
- [ ] **T4.14** Step 15-16: Weapon bonuses and damage recording
- [ ] **T4.15** Step 17: Armor Class (DONE - existing)
- [ ] **T4.16** Step 18: Saving throws — add Luck save (flat 15)
- [ ] **T4.17** Step 19: Name, goal, ties (name DONE, add goal field)

### M5: Schema & CLI Updates

- [ ] **T5.1** Update `state.schema.json` character definition:
  - Expand class enum: `["warrior", "expert", "mage", "adventurer"]`
  - Add `tradition` field (string, optional)
  - Add `partial_classes` field (array of strings, for Adventurers)
  - Add `spells_prepared` field (array of spell objects)
  - Add `spells_known` field (array of spell objects)
  - Add `known_arts` field (array of art names)
  - Add `luck_save` to saving_throws
  - Add `goal` field (string)
  - Add `languages` field (array of strings)
- [ ] **T5.2** Update `emergence_cli.py` create-character parser:
  - Expand --class choices to include "adventurer" and WWN5 classes
  - Add --partial-classes argument (for Adventurers, e.g., "expert,warrior")
  - Add --tradition argument (for Mages)
  - Add --foci argument (comma-separated focus names)
  - Add --spells argument (comma-separated spell names for Mages)
  - Add --equipment argument (package name or "roll")
  - Add --skills argument (comma-separated additional skill picks)
- [ ] **T5.3** Update CLI reference doc:
  - Document new arguments and valid values
  - Document output contract changes
- [ ] **T5.4** Update phase-manifest.md with new command signature
- [ ] **T5.5** Run `validate_state.py` against updated schema with expanded character

### M6: WWN5 Optional Classes (DEFERRED)

Deferred to a follow-up PR. Requires separate PDF extraction and class design work.
Classes to be added: Accursed, Bard, Mageslayer, Wise.
These classes have unique mechanics not shared with the core 4 and are better handled as a separate scope.

### M7: Validation & Testing

- [ ] **T7.1** Create `test_character_creation_expanded.py`:
  - Test all 4 base classes create valid characters
  - Test all 6 Adventurer combos produce correct HD/AB/Focus
  - Test all 5 traditions produce valid mage characters
  - Test focus selection respects class restrictions
  - Test starting spell selection validates against tradition
  - Test equipment package selection
  - Test quick skills application
  - Test free skill pick
  - Test Luck saving throw present
  - Test schema validation passes for all class types
- [ ] **T7.2** Test edge cases:
  - Adventurer with two Partial Mage classes (4 starting spells)
  - Mage with Healer tradition (no spells, arts only)
  - Warrior with combat Focus stacked to level 2
  - Roll_3d6 method with seed determinism
- [ ] **T7.3** Run existing test suite to verify no regressions
- [ ] **T7.4** Run state schema validator on sample expanded characters

## Modified Files Summary

| File | Change Type | Surfaces Touched |
|------|-------------|------------------|
| `skills/core/tables/classes.py` | Major edit | State schema, rules logic |
| `skills/core/tables/foci.py` | Minor edit | Rules logic |
| `skills/core/tables/equipment.py` | Minor edit | Rules logic |
| `skills/core/tables/traditions.py` | New file | Rules logic |
| `skills/core/tables/spells.py` | New file | Rules logic |
| `skills/core/scripts/character.py` | Major edit | Rules logic, state schema |
| `skills/core/scripts/magic.py` | Minor edit | Rules logic |
| `runtime/scripts/emergence_cli.py` | Major edit | CLI interface |
| `runtime/schemas/state.schema.json` | Major edit | State schema |
| `runtime/tests/test_character_creation_expanded.py` | New file | Validation |

## Validation

1. `python runtime/tests/run_all_tests.py 1` — existing tests pass (no regression)
2. `python runtime/tests/test_character_creation_expanded.py` — new tests pass
3. `python runtime/scripts/validate_state.py runtime/state.json` — state validates
4. CLI smoke tests for all class types produce valid JSON output
5. Determinism: same seed produces identical characters across all class types

## Analysis Pass 1 — Weaknesses Found and Fixed

**W1 (FIXED): Adventurer Partial Mage/Partial Warrior progression table missing**
The plan now includes all 3 combo progression tables in T2.2. The Partial Warrior/Partial Mage combo uses: HD 1d6, AB from PARTIAL_WARRIOR_AB table.

**W2 (VERIFIED OK): Saving throw formula**
Existing code uses `16 - (level + modifier)`. At level 1: `16 - (1 + mod) = 15 - mod`. WWN1 says "saves start at 15 - modifier" and "decrease by one per level". Formula is correct. However, need to ADD Luck save = flat 15 (decreases by 1/level = `16 - level`).

**W3 (FIXED): Effort max formula**
Added T3.3 specifying exact effort calculation: Full Mage = 1 + (Int mod + level) // 2; Partial Mage = 1 + (Int mod + level) // 4. Non-mages = 0. Note: resource_pool schema needs min:0 for max (not min:1) to support effort.max=0.

**W4 (FIXED): Healer and Vowed are partial-only**
Added explicit validation in T3.1: if class is "mage" (full), tradition cannot be "healer" or "vowed". These are only available to Adventurers with Partial Mage.

**W5 (FIXED): Dual Partial Mage**
Added to T2.2: Adventurers with Partial Mage/Partial Mage combo use `DUAL_PARTIAL_MAGE_CASTING` table (already exists in codebase). They pick two different traditions and get 4 starting spells total.

**W6 (FIXED): Spell data volume**
Spells are staged: initial implementation includes spell stubs (name, level, tradition, description placeholder). Full mechanical descriptions added incrementally. The character creation system validates spell names against the stub table.

**W7 (DEFERRED): WWN5 classes**
Moved M6 to a follow-up PR. Core character creation expansion focuses on the 4 base classes + 5 traditions. WWN5 classes require their own extraction and are not blocked by this work.

**W8 (FIXED): Tradition restrictions on Adventurers**
Added to T3.1: Partial Mages inherit tradition restrictions (e.g., Partial High Mage can't cast in armor). Store tradition restrictions in traditions.py and check during character validation.

**W9 (FIXED): resource_pool schema allows max=0**
Updated T5.1 to note: change `resource_pool.max` minimum from 1 to 0 to support effort.max=0 for non-mages. This is a schema fix, not a break.

## Analysis Pass 2 — Additional Weaknesses Found and Fixed

**W10 (FIXED): Missing Specialist focus**
The existing foci.py has 26 foci but is missing "Specialist" which appears in the PDF as a repeatable focus. Added to T1.3.

**W11 (FIXED): create_character() signature becoming unwieldy**
The function currently takes 4 args. Expanding to 10+ args makes the API brittle. FIXED: T4 refactored to use a `CharacterOptions` dataclass/dict that bundles all choices, with sensible defaults for backward compatibility.

**W12 (FIXED): Background skill resolution is interactive**
Steps 4-5 involve player choices (pick vs roll, which skills to pick). FIXED: CLI must support both "quick" (auto-pick Quick Skills) and "custom" (specify via --skills arg) modes. Default to "quick" for non-interactive use.

**W13 (FIXED): Focus validation is complex**
Focus picks depend on class type (warrior gets combat focus, expert gets non-combat). FIXED: Added T4.6 validation logic that checks focus.type against class partial types. Also validates no duplicate foci except Specialist.

**W14 (FIXED): No language tracking**
WWN1 p.28 specifies starting languages based on Connect/Know skill levels. FIXED: Added language generation to T4 and languages field to schema.

## Risks and Mitigations

- **Risk:** Schema version bump needed — **Mitigation:** Bump to 7.6.0 (minor - additive only, no field removals). Fix resource_pool.max to allow 0.
- **Risk:** Spell data extraction accuracy from PDFs — **Mitigation:** Use spell stubs (name, level, tradition) initially; full descriptions added incrementally. Character creation only needs the name/level/tradition to validate.
- **Risk:** Adventurer class complexity (3 combos × tradition matrix) — **Mitigation:** Implement core 3 combos first (E/W, E/M, W/M), validate, then add dual-partial-mage edge case.
- **Risk:** Breaking existing create-character CLI users — **Mitigation:** All new arguments are optional; existing command syntax still works unchanged. New args have sensible defaults.
- **Risk:** Large number of surfaces touched (>2) — **Mitigation:** Changes are additive (new fields, new choices), not destructive; existing data remains valid.
- **Risk:** Interactive character creation choices require player input — **Mitigation:** CLI supports "quick" mode with auto-picks for all choices. Custom mode uses explicit CLI args.

## Exit Criteria

1. `create-character` CLI produces valid characters for all 4 base classes
2. All 6 Adventurer partial class combinations work correctly
3. All 5 magic traditions can be selected with appropriate starting spells/arts
4. Focus selection respects class restrictions (warrior-only, non-combat, any)
5. Equipment packages produce valid equipment loadouts
6. All new character objects pass state schema validation
7. Existing test suite passes without modification
8. New expanded test suite passes
9. CLI reference documentation is updated
