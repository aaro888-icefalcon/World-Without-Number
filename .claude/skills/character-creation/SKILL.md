---
name: character-creation
description: Guide a player through World Without Number character creation. Use when a new game starts, when state.json has session_number 0 or character.name is "Unnamed Hero", or when the player explicitly asks to create a character.
disable-model-invocation: true
argument-hint: "[concept or empty]"
allowed-tools: Read, Bash, Grep, Glob
---

# WWN Character Creation

Create a World Without Number character through a 3-step interactive flow. All mechanical choices come from Python tables via CLI — never from memory.

## Prerequisites

- `runtime/scripts/emergence_cli.py` must be available
- `runtime/state.json` should exist (even if placeholder)

## Step 1: Character Concept

Ask the player:

> Who are you? Describe your character — name, who they are, what they're good at, what matters to them. Where in the city were you when everything changed? Who matters to you here?

If `$ARGUMENTS` is provided, treat it as the player's concept and skip to Step 2.

Extract the character's **name** from the response.

## Step 2: Build the Character

### 2a. Query valid options

ALWAYS query the Python tables first — never present options from memory:

```bash
python runtime/scripts/emergence_cli.py query-chargen-options \
  --class <chosen_class> \
  --partial-classes "<pc1>,<pc2>" \
  --background <bg_id>
```

### 2b. GM decides all mechanics

Based on the concept and query results, select:

1. **Class** — warrior / expert / mage / adventurer (+ partial classes if adventurer)
2. **Background** — best-fitting from 20 backgrounds (IDs 1–20)
3. **Attributes** — `boosted_3d6` method, assign to match concept
4. **Boosts** — +2 physical (str/dex/con), +2 mental (int/wis/cha)
5. **Background skills** — 2 from background's `quick_skills`
6. **Foci** — 2 picks from `valid_foci` in query result
7. **Free skill** — 1 at level-0 from `all_skills`
8. **Arts** (if applicable) — from `arts_by_class` in query result
9. **Class abilities** — from `class_abilities` in query result
10. **Spells** (if applicable) — from tradition spell lists

### 2c. Present the complete build

Show the entire build at once for approval:

```
═══════════════════════════════════════════
  CHARACTER BUILD — [Name]
═══════════════════════════════════════════
  Class: [class] ([partial classes if adventurer])
  Background: [background name]
  Level: 1

  ATTRIBUTES (after boosts):
  STR [val] ([mod])  DEX [val] ([mod])  CON [val] ([mod])
  INT [val] ([mod])  WIS [val] ([mod])  CHA [val] ([mod])

  SKILLS:
  [skill]: [level], [skill]: [level], ...

  FOCI:
  • [focus 1] — [L1 effect summary]
  • [focus 2] — [L1 effect summary]

  ARTS (if any):
  • [art 1] — [effect summary]

  CLASS ABILITIES:
  • [ability] — [effect summary]

  DERIVED STATS:
  HP: [val]  AC: [val]  AB: [val]
  Effort: [val]  System Strain: 0/[max]
  Saves: Phys [val] Eva [val] Mental [val] Luck [val]
═══════════════════════════════════════════
```

Wait for player approval. Players may swap foci, skills, arts, abilities, or request different attributes. If adjustments are needed, re-run `query-chargen-options` and present the updated build — do NOT reprint full option lists.

## Step 3: Execute

Once approved, run the CLI:

```bash
python runtime/scripts/emergence_cli.py initialize-game \
  --name "<name>" \
  --class <class> \
  --background <bg_id> \
  --method boosted_3d6 \
  --attribute-assignments "strength=X,dexterity=X,constitution=X,intelligence=X,wisdom=X,charisma=X" \
  --background-skills "skill1,skill2" \
  --physical-boost <str|dex|con> \
  --mental-boost <int|wis|cha> \
  --foci "focus1,focus2" \
  --free-skill <skill> \
  --known-arts "art1,art2" \
  --class-ability-overrides "ability1,ability2" \
  [--partial-classes "cls1,cls2"] \
  [--tradition <tradition>] \
  [--equipment-package <package>] \
  --seed <seed>
```

After execution:

1. Parse JSON output
2. Apply concept-derived world seeds (NPCs, locations, faction standings)
3. Write `state.json`
4. Validate: `python runtime/scripts/validate_state.py runtime/state.json`
5. Display character sheet
6. Render opening scene

## Rules

- **Never hallucinate options** — always query Python tables via CLI
- **All dice/stats computed by scripts** — never hand-calculate
- **Record the RNG seed** in state for reproducibility
- **One attribute must be >= 14** after boosted_3d6 generation

## Reference Files

- Character engine: `runtime/phases/3-resolution/skills/core/scripts/character.py`
- Chargen query: `runtime/phases/3-resolution/skills/core/scripts/chargen_query.py`
- Game initialization: `runtime/phases/1-context-loading/skills/game-initialization.md`
- State schema: `runtime/schemas/state.schema.json`
- Character sheet template: `runtime/phases/4-narrative/assets/character-sheet-template.md`
- Classes table: `runtime/phases/3-resolution/skills/core/tables/classes.py`
- Foci table: `runtime/phases/3-resolution/skills/core/tables/foci.py`
- Backgrounds table: `runtime/phases/3-resolution/skills/core/tables/backgrounds.py`
- Traditions table: `runtime/phases/3-resolution/skills/core/tables/traditions.py`
- Partial classes: `runtime/phases/3-resolution/skills/core/tables/partial_classes.py`
