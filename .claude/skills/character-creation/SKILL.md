---
name: character-creation
description: Guide a player through World Without Number character creation. Use when starting a new game, when state.json has session_number 0 or character.name is "Unnamed Hero", or when the player explicitly asks to create a character.
disable-model-invocation: true
argument-hint: "[character concept or empty]"
allowed-tools: Read, Bash, Grep, Glob
---

# WWN Character Creation

Guide a player through World Without Number character creation in a 3-step interactive flow. Use ONLY the game data in the supporting reference files below. Never invent options.

## Supporting Reference Files

- For complete class tables and level progression, see [classes-and-progression.md](classes-and-progression.md)
- For backgrounds, skills, and foci tables, see [backgrounds-skills-foci.md](backgrounds-skills-foci.md)
- For magic traditions and all class arts, see [traditions-and-arts.md](traditions-and-arts.md)

Load the relevant reference file when you need its data during character creation.

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

Based on the concept and query results, select all of the following. Consult the supporting reference files for valid options:

1. **Class** — warrior / expert / mage / adventurer (+ partial classes if adventurer). See [classes-and-progression.md](classes-and-progression.md)
2. **Background** — best-fitting from 20 backgrounds (IDs 1–20). See [backgrounds-skills-foci.md](backgrounds-skills-foci.md)
3. **Attributes** — `boosted_3d6` method, assign to match concept
4. **Boosts** — +2 physical (str/dex/con), +2 mental (int/wis/cha)
5. **Background skills** — 2 from background's `quick_skills`
6. **Foci** — 2 picks from `valid_foci` in query result. See [backgrounds-skills-foci.md](backgrounds-skills-foci.md)
7. **Free skill** — 1 at level-0 from `all_skills`
8. **Arts** (if applicable) — from `arts_by_class` in query result. See [traditions-and-arts.md](traditions-and-arts.md)
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
  Level: 1    XP: 0

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
  HP: [val]/[max]  AC: [val]  AB: +[val]
  Effort: [current]/[max]  System Strain: 0/[max]
  Saves — Physical: [val]  Evasion: [val]  Mental: [val]  Luck: 15

  EQUIPMENT:
  [items from package]
  Coins: [val] sp
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

## Derived Stats Reference

- **HP:** Roll class hit die. Minimum 1 HP
- **Armor Class:** From equipment package
- **Attack Bonus:** Warrior +1, Partial Warrior +1, others +0 at level 1
- **Saving Throws** (lower is better):
  - Physical = 15 - max(Str mod, Con mod)
  - Evasion = 15 - max(Dex mod, Int mod)
  - Mental = 15 - max(Wis mod, Cha mod)
  - Luck = 15
- **System Strain:** Max = Constitution score
- **Effort:** Based on class formula (see classes-and-progression.md). Non-casters = 0

**Attribute modifiers:**

| Score | Modifier |
|---|---|
| 3 | -2 |
| 4–7 | -1 |
| 8–13 | 0 |
| 14–17 | +1 |
| 18 | +2 |

## Equipment Packages

| Package | AC | Key Items | Coins |
|---|---|---|---|
| Armored Warrior | 11 | War shirt, short sword, small shield, dagger | 10 sp |
| Archer | 12 | Buff coat, small bow, 20 arrows, short sword | 10 sp |
| Skirmisher | 13 | Linothorax, light spear, dagger, 5 throwing blades | 10 sp |
| Scholar | 10 | Staff, dagger, writing kit, lantern, 2 oil flasks | 20 sp |
| Rogue | 12 | Buff coat, short sword, dagger, thieves' tools, rope | 10 sp |
| Traveler | 10 | Light spear, dagger, lantern, rope, bedroll | 15 sp |

## Key Rules

- **Never hallucinate options** — always query Python tables via CLI
- **All dice/stats computed by scripts** — never hand-calculate
- **Record the RNG seed** in state for reproducibility
- **One attribute must be >= 14** after boosted_3d6 generation
- **Skill stacking**: Same skill gained twice at level 0 becomes level 1. Max level 1 at creation
- **Focus type restrictions** must be respected — a non-Warrior cannot take warrior-type foci
- **Mageslayer** cannot pair with any spellcasting class
- **Healer and Vowed** traditions are partial-only (Adventurer only)
