# Execution Plan: WWN5 Optional Classes + Gyre Classes + Traditional Education Focus

- **Owner:** Development team
- **Status:** In Progress
- **Start Date:** 2026-03-08
- **Related:** `2026-03-08-character-creation-expansion-plan.md` (M6 deferred scope)

## Objective

Add 11 new partial classes, 1 new full class option, and 1 new focus to the character creation system:

**WWN5 Optional Classes (4):**
1. **Accursed** — Partial Mage. Eldritch pact powers. Pairs with Expert, Warrior, or Mage.
2. **Bard** — Partial Expert. Performance-based arts. Pairs with Warrior or Mage.
3. **Mageslayer** — Partial Warrior. Anti-magic combat arts. Pairs with Expert or Warrior only (NO Mage).
4. **Wise** — Partial Expert. Low-magic scholar/priest. Pairs with Warrior, Mage, or Expert.

**WWN4 Gyre Classes (6):**
5. **Adunic Invoker** — Full OR Partial Mage. Spell points instead of Vancian slots.
6. **Darian Skinshifter** — Partial Mage only. Shapeshifting arts.
7. **Kistian Duelist** — Partial Mage only. Martial fencing arts. Fragility flaw with Partial Warrior.
8. **Llaigisan Beastmaster** — Partial Mage only. Animal companion arts.
9. **Sarulite Blood Priest** — Partial Mage only. Divine miracle arts.
10. **Vothite Thought Noble** — Partial Mage only. Psychic arts. No Effort.

**New Focus (1):**
11. **Traditional Education** — Invoker-only. Grants access to one tradition's spell list + starting arts.

## Architecture Decisions

### A1: New partial class types extend the Adventurer system

New classes are NOT new base class enum values. They are new partial class options that slot into the existing Adventurer multiclass framework. The `class` field stays as `["warrior", "expert", "mage", "adventurer"]`.

Exception: Full Adunic Invoker is handled as `class="mage"` with `tradition="invoker"`.

### A2: Partial class categorization

Each partial class has a "base type" that determines which standard partial it replaces:
- **Expert-type:** expert, bard, wise
- **Warrior-type:** warrior, mageslayer
- **Mage-type:** mage, accursed, invoker, skinshifter, duelist, beastmaster, blood_priest, thought_noble

### A3: New PARTIAL_CLASSES definition dict

A new `PARTIAL_CLASSES` dict in a new file `partial_classes.py` defines each non-standard partial class with: base_type, bonus_skill, effort_formula, arts, art_progression, restrictions.

### A4: Explicit ADVENTURER_PROGRESSION entries

WWN5 classes have explicit combo tables from the PDF (different HD/AB than standard combos). Gyre classes use the same HD/AB as standard partial_mage combos but need their own keys for discoverability.

### A5: Combo restriction validation

Enforce restrictions: Mageslayer cannot pair with any Mage-type partial. Kistian Duelist with Partial Warrior uses d6 HD (Fragility flaw). Two partials of the same base type are invalid (e.g., Bard+Expert).

## Scope

### In scope:
- `partial_classes.py` (new) — All 10 new partial class definitions with arts/abilities
- `classes.py` — New ADVENTURER_PROGRESSION entries for all valid combos
- `foci.py` — Add Traditional Education focus
- `traditions.py` — Add `invoker` tradition for full Adunic Invoker
- `character.py` — Expand create_character() for new partial classes
- `state.schema.json` — Expand partial_classes enum, add invoker tradition
- `emergence_cli.py` — Expand --partial-classes and --tradition choices
- Test suite — Comprehensive tests for all new classes

### Out of scope:
- WWN5 Maqqatban Knight / Amundi Godblood / Arcane Secret foci (separate PR)
- Non-Human Origin foci (separate PR)
- Heroic classes and Legates (WWN4 advanced content)
- Runtime combat mechanics for new arts
- Level advancement mechanics

## File Changes

| File | Change | Surfaces |
|------|--------|----------|
| `tables/partial_classes.py` | NEW — 10 partial class definitions | Rules logic |
| `tables/classes.py` | EDIT — Add ~18 ADVENTURER_PROGRESSION entries | Rules logic |
| `tables/foci.py` | EDIT — Add Traditional Education | Rules logic |
| `tables/traditions.py` | EDIT — Add invoker tradition | Rules logic |
| `scripts/character.py` | EDIT — New partial class handling, effort, validation | Rules logic, state |
| `schemas/state.schema.json` | EDIT — Expand enums | State schema |
| `scripts/emergence_cli.py` | EDIT — Expand CLI choices | CLI |
| `tests/test_expanded_classes.py` | NEW — Tests for all new classes | Validation |

## Task Breakdown

### T1: Data Tables — partial_classes.py (NEW)

Create `runtime/phases/3-resolution/skills/core/tables/partial_classes.py` containing:

```python
PARTIAL_CLASSES = {
    # WWN5 Optional Classes
    "accursed": {
        "base_type": "mage",
        "bonus_skill": "magic",
        "effort_formula": "magic_skill + max(int_mod, cha_mod)",
        "has_spells": False,
        "restrictions": [],
        "starting_arts": ["accursed_blade_or_bolt", "any_one"],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1},
        "arts": [
            {"name": "Accursed Blade", ...},
            {"name": "Accursed Bolt", ...},
            # ... 20 total arts
        ],
    },
    "bard": {
        "base_type": "expert",
        "bonus_skill": "perform",
        "effort_formula": "perform_skill + cha_mod",
        "has_spells": False,
        "no_quick_learner": True,  # Bard does NOT get Quick Learner
        "no_bonus_focus": True,    # Bard does NOT get Expert bonus Focus
        "restrictions": [],
        "starting_arts": ["a_thousand_tongues", "any_one"],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1},
        "arts": [...],  # ~16 arts
    },
    "mageslayer": {
        "base_type": "warrior",
        "bonus_skill": "magic",
        "effort_formula": "magic_skill + max(int_mod, con_mod)",
        "has_spells": False,
        "no_bonus_combat_focus": True,  # No Warrior bonus combat Focus
        "no_warrior_hp_bonus": True,    # No +2 HP per die
        "restricted_pairings": ["mage", "accursed", "invoker", "skinshifter",
                                 "duelist", "beastmaster", "blood_priest", "thought_noble"],
        "restrictions": [],
        "starting_arts": ["antimage", "magebane"],
        "art_progression": {1: 2, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1},
        "arts": [...],  # 13 arts, FIXED progression (not player choice)
    },
    "wise": {
        "base_type": "expert",
        "bonus_skill": "pray_or_know_or_magic_or_survive",
        "effort_formula": None,  # Wise do not use Effort
        "has_spells": False,
        "no_quick_learner": True,
        "no_bonus_focus": True,
        "restrictions": [],
        "wise_type": "esoteric",  # Default; GM picks: mundane_priest, witch, seer, esoteric
        "art_categories": ["general", "divination", "curses_and_blessings"],
        "art_progression": {1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1},
        "arts": [...],  # ~16 arts across 3 categories
    },

    # WWN4 Gyre Classes
    "invoker": {
        "base_type": "mage",
        "bonus_skill": "magic",
        "effort_formula": None,  # Uses spell points, not Effort
        "has_spells": True,
        "spell_point_system": True,  # Uses spell points instead of Vancian
        "can_be_full": True,  # Unlike other Gyre classes
        "restrictions": [],
        "arts": [],  # No arts normally (except via Traditional Education focus)
        "full_casting": {
            1: {"max_level": 1, "spell_points": "1+Int", "spells_prepared": "2+Int"},
            # ... levels 2-10
        },
        "partial_casting": {
            1: {"max_level": 1, "spell_points": "1+Int", "spells_prepared": "1+Int"},
            # ... levels 2-10
        },
    },
    "skinshifter": {
        "base_type": "mage",
        "bonus_skill": "survive",
        "effort_formula": "survive_skill + max(con_mod, cha_mod)",
        "has_spells": False,
        "restrictions": [],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 1, 10: 0},
        "form_bonus": {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 6},
        "arts": [...],  # 15 arts
    },
    "duelist": {
        "base_type": "mage",
        "bonus_skill": "stab",
        "effort_formula": "stab_skill + max(dex_mod, int_mod)",
        "has_spells": False,
        "warrior_fragility": True,  # Uses 1d6 HD with Partial Warrior instead of 1d6+2
        "restrictions": ["Cannot benefit from arts while wearing medium/heavy armor or large shield"],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 1, 10: 0},
        "favored_weapon_bonus": {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5},
        "arts": [...],  # 17 arts
    },
    "beastmaster": {
        "base_type": "mage",
        "bonus_skill": "survive",
        "effort_formula": "survive_skill + max(wis_mod, cha_mod)",
        "has_spells": False,
        "restrictions": [],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1},
        "arts": [...],  # 12 arts
    },
    "blood_priest": {
        "base_type": "mage",
        "bonus_skill": "pray",
        "effort_formula": "pray_skill + max(wis_mod, cha_mod)",
        "has_spells": False,
        "restrictions": ["Miracles require vocalization"],
        "art_progression": {1: 2, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1},
        "arts": [...],  # 13 miracles
    },
    "thought_noble": {
        "base_type": "mage",
        "bonus_skill": "notice",
        "effort_formula": "notice_skill + max(int_mod, wis_mod)",
        "has_spells": False,
        "restrictions": ["All arts invisible to non-magical senses",
                          "Successful Mental save = immune for rest of scene"],
        "art_progression": {1: 2, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1},
        "arts": [...],  # 16 arts
    },
}

# Valid combo restrictions
INVALID_COMBOS = {
    "mageslayer": {"mage", "accursed", "invoker", "skinshifter", "duelist",
                   "beastmaster", "blood_priest", "thought_noble"},
}

# Base type mapping for determining combo tables
BASE_TYPE_MAP = {
    "expert": "expert", "bard": "expert", "wise": "expert",
    "warrior": "warrior", "mageslayer": "warrior",
    "mage": "mage", "accursed": "mage", "invoker": "mage",
    "skinshifter": "mage", "duelist": "mage", "beastmaster": "mage",
    "blood_priest": "mage", "thought_noble": "mage",
}
```

### T2: Data Tables — classes.py (EDIT)

Add new ADVENTURER_PROGRESSION entries. For WWN5 classes with explicit PDF tables:

**Accursed combos (3):**
- `partial_accursed/partial_expert`: L1 1d6/+0, matches Expert/Mage pattern
- `partial_accursed/partial_mage`: L1 1d6-1/+0, dual-mage pattern
- `partial_accursed/partial_warrior`: L1 1d6+2/+1, full Warrior HD pattern

**Bard combos (3):**
- `partial_bard/partial_expert`: L1 1d6/+0
- `partial_bard/partial_mage`: L1 1d6/+0
- `partial_bard/partial_warrior`: L1 1d6+2/+1, full Warrior HD pattern

**Mageslayer combos (2):**
- `partial_expert/partial_mageslayer`: L1 1d6/+1
- `partial_mageslayer/partial_warrior`: L1 1d6+2/+1, full Warrior AB pattern

**Wise combos:** Uses standard Expert-type tables (same as partial_expert combos). Map to existing entries via BASE_TYPE_MAP.

**Gyre class combos:** Use standard partial_mage combo tables (same HD/AB). Map via BASE_TYPE_MAP. Special case: Duelist + Warrior uses 1d6 instead of 1d6+2 (Fragility flaw).

**New Adventurer combo: dual-mage (`partial_accursed/partial_mage`):**
- Not in existing system. Need new table for dual-casting classes.

Total new ADVENTURER_PROGRESSION entries: ~10 explicit + fallback logic for Gyre classes.

### T3: Data Tables — foci.py (EDIT)

Add Traditional Education focus:
```python
"traditional_education": {
    "type": "any",
    "class_restriction": "invoker",
    "level_1": "Learn/prepare spells of a chosen tradition plus High Magic. Gain arts as 1st-level practitioner. Max Effort = Magic skill (min 1).",
    "level_2": None,  # Single-level focus
}
```

### T4: Data Tables — traditions.py (EDIT)

Add invoker as a tradition entry for full Adunic Invoker:
```python
"invoker": {
    "description": "Spell point caster using High Magic spells.",
    "partial_only": False,
    "has_spells": True,
    "spell_point_system": True,
    "restrictions": [],
    "arts": [],  # No arts by default
}
```

### T5: Schema — state.schema.json (EDIT)

Expand:
- `partial_classes.items.enum`: Add all 10 new partial class names
- `tradition.enum`: Add "invoker"
- No new required fields needed

### T6: Character Creation — character.py (EDIT)

Changes to `create_character()`:
1. Accept new partial class values in validation
2. New `_resolve_adventurer_combo()` function that:
   - Validates combo restrictions (mageslayer + mage = error)
   - Looks up explicit ADVENTURER_PROGRESSION entry first
   - Falls back to base-type mapping for Gyre classes
   - Handles Duelist Fragility flaw (reduce HD bonus)
3. New `_calculate_effort_expanded()` for class-specific effort formulas
4. Apply class-specific bonus skills
5. Track class-specific arts in `known_arts`
6. Handle Invoker spell point system (store spell_points in character dict)

### T7: CLI — emergence_cli.py (EDIT)

Expand:
- `--partial-classes` help text to list all valid options
- `--tradition` choices to include "invoker"
- Remove `choices=` constraint on `--partial-classes` (too many to enumerate; validate in character.py)

### T8: Tests — test_expanded_classes.py (NEW)

Write BEFORE implementation. Test groups:
1. Partial class data table completeness (all 10 defined with required fields)
2. ADVENTURER_PROGRESSION completeness (all valid combos have entries)
3. Character creation for each WWN5 class (all valid combos)
4. Character creation for each Gyre class (all valid combos)
5. Combo restriction enforcement (mageslayer+mage = error)
6. Effort calculation per class
7. Bonus skill application per class
8. Duelist Fragility flaw (reduced HD with Warrior)
9. Full Invoker creation (class=mage, tradition=invoker)
10. Traditional Education focus validation
11. Schema validation for all new class types
12. CLI integration for new classes
13. Determinism for new classes
14. Backward compatibility (existing 43 tests still pass)

## Analysis Pass 1 — Weaknesses

**W1 (FIXED): Combo explosion.** 10 new partials × existing partials = many combos. Not all are valid. FIXED: Use BASE_TYPE_MAP fallback — only store explicit tables for combos that differ from standard. Gyre classes reuse existing partial_mage tables.

**W2 (FIXED): Wise class has no Effort.** The Wise doesn't use Effort at all — arts are constant or daily-use. FIXED: effort_formula=None, effort stays at 0/0.

**W3 (FIXED): Invoker spell points vs Vancian.** The Invoker uses spell points instead of spell slots. The current system tracks effort.max but not spell_points. FIXED: Add optional `spell_points` field to character dict (only for Invoker). Schema uses `additionalProperties: true` so no schema change needed.

**W4 (FIXED): Mageslayer arts are FIXED progression.** Unlike other classes where players choose arts, the Mageslayer gains specific arts at specific levels (Antimage+Magebane at L1, Witchfinder+Spellshield at L2, etc.). FIXED: Mark as `fixed_progression: True` in definition. Character creation assigns arts based on level.

**W5 (FIXED): Same-base-type combos.** Can you pair Bard (expert-type) with Expert? The PDF shows Partial Expert/Bard tables, so yes. Can you pair Mageslayer (warrior-type) with Warrior? The PDF shows Partial Warrior/Mageslayer tables, so yes. FIXED: Allow same-base-type combos when explicit tables exist.

**W6 (FIXED): Wise bonus skill is GM-chosen.** Wise gets "Pray, Know, Magic, Survive, or other GM-approved." FIXED: Accept any valid skill name as bonus_skill parameter; default to "pray".

## Analysis Pass 2 — Additional Weaknesses

**W7 (FIXED): Bard + Mage combo.** The Bard is a Partial Expert, but Partial Mage/Bard has its own table in the PDF. This is a cross-type combo (expert-type + mage-type) which already works in the existing system. FIXED: Add explicit table entry.

**W8 (FIXED): Duelist Fragility interacts with combo tables.** When Duelist pairs with Warrior, the HD should be 1d6 instead of the standard 1d6+2. This means a Duelist/Warrior combo needs its own progression table. FIXED: Create explicit `partial_duelist/partial_warrior` entry with 1d6 HD.

**W9 (FIXED): Two new partial classes of same type in one combo.** E.g., Bard (expert-type) + Wise (expert-type). This is likely invalid but not explicitly restricted. FIXED: Add validation — two partials of the same base_type are invalid UNLESS they have an explicit combo table.

**W10 (FIXED): Full Invoker class handling.** Full Invoker uses class="mage" with tradition="invoker". But the existing Mage class gives "arcane_tradition" as a class_ability. The Invoker should get different abilities. FIXED: When tradition="invoker", override class_abilities with Invoker-specific abilities.

**W11 (FIXED): Backward compatibility of partial_classes schema.** Current schema enum is ["expert", "warrior", "mage"]. Adding new values is additive — existing characters remain valid. FIXED: Just extend the enum array.

## Implementation Order

1. Write tests (T8) — validates completion criteria
2. Create partial_classes.py (T1) — all class data
3. Update classes.py (T2) — combo progression tables
4. Update foci.py (T3) — Traditional Education
5. Update traditions.py (T4) — Invoker tradition
6. Update state.schema.json (T5) — enum expansion
7. Update character.py (T6) — creation logic
8. Update emergence_cli.py (T7) — CLI expansion
9. Run all tests, fix issues
10. Verify backward compatibility (existing 43 tests pass)

## Exit Criteria

1. All 10 new partial classes can create valid Adventurer characters
2. Full Invoker creates valid Mage character
3. Combo restrictions enforced (Mageslayer+Mage = error)
4. Duelist Fragility flaw reduces HD with Warrior
5. Each class has correct bonus skill, effort, and starting arts
6. Traditional Education focus works for Invoker class
7. All new characters pass schema validation
8. Existing 43 tests still pass (backward compatibility)
9. CLI accepts all new partial class names
10. Determinism verified for all new class types
