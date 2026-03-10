# Game Initialization — New Game Startup Protocol

This skill governs how a new game session is started from scratch. It produces a valid, playable state.json through a streamlined 3-step flow.

## When This Runs

- When state.json contains placeholder data (character.name == "Unnamed Hero")
- When the player explicitly requests a new game
- When session_number is 0 in state.json meta

## Detection: New Game vs. Returning Session

Check these conditions in order:

1. `meta.session_number == 0` → **New game** — run full initialization
2. `character.name == "Unnamed Hero"` → **New game** — run full initialization
3. `meta.session_number >= 1` AND valid character → **Returning session** — skip to session resume (increment session_number, reset drama budget, load context per lore-loading.md)

## Campaign

All games use the **NYC — Carven Peaks Campaign**. No campaign selection step.

## Core Principle: Use Python Tables, Not Markdown Lists

**NEVER** present options from memory or from this document's text. Instead:

1. Run `query-chargen-options` CLI command to get valid options from Python tables
2. Use that output as the ONLY source of truth for foci, arts, class abilities, skills, and backgrounds
3. If a player asks "what are my options?", run the query and present from the result

This prevents hallucination and ensures options match the actual game data.

## Streamlined Initialization Protocol (3 Steps)

### Step 1: Character Concept

Ask the player one question:

> "Who are you? Describe your character — name, who they are, what they're good at, what matters to them. Where in the city were you when everything changed? Who matters to you here?"

Wait for response. **Save concept immediately** to state.json:

```json
{
  "meta": {
    "session_number": 0,
    "creation_progress": {
      "step": 1,
      "concept": "<player's description>",
      "name": "<extracted name>"
    }
  }
}
```

This ensures the concept survives conversation compression.

### Step 2: GM Builds the Character (Deterministic)

Based on the player's concept, the GM makes ALL mechanical choices:

#### 2a. Query valid options

```bash
python runtime/scripts/emergence_cli.py query-chargen-options \
  --class <chosen_class> \
  --partial-classes "<pc1>,<pc2>" \
  --background <bg_id>
```

This returns filtered foci, arts, class abilities, backgrounds, and skills from the Python tables.

#### 2b. GM decides everything

Using the concept and query results, the GM selects:

1. **Class** — warrior / expert / mage / adventurer (+ partial classes if adventurer)
2. **Background** — best-fitting from the 20 backgrounds (use query result `all_backgrounds`)
3. **Attributes** — Roll via `boosted_3d6`, assign scores to match concept
4. **Background boosts** — +2 physical, +2 mental (reinforce concept)
5. **Background skills** — 2 skills from the background's pool (use query result `background.quick_skills`)
6. **Foci** — 2 picks from `valid_foci` in query result (1 background focus + 1 class focus)
7. **Free skill** — 1 skill at level-0 (from `all_skills` in query result)
8. **Arts** (if applicable) — from `arts_by_class` in query result. Use `--known-arts` to pass explicit picks
9. **Class abilities** — from `class_abilities` in query result. Use `--class-ability-overrides` if player requests changes
10. **Spells** (if applicable) — from tradition spell lists

#### 2c. Present complete build for approval

Present the ENTIRE build as a single block:

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
  • [art 2] — [effect summary]

  CLASS ABILITIES:
  • [ability] — [effect summary]

  DERIVED STATS:
  HP: [val]  AC: [val]  AB: [val]
  Effort: [val]  System Strain: 0/[max]
  Saves: Phys [val] Eva [val] Mental [val] Luck [val]
═══════════════════════════════════════════
```

Wait for player approval or adjustments. Players may:
- Ask to swap foci, arts, skills, or abilities
- Request different attribute assignments
- Change class or partial classes

If adjustments are needed, re-run `query-chargen-options` with updated class/partial-classes and rebuild. Do NOT reprint the full option lists — just describe the change and present the updated build.

**Save progress** after presenting build:

```json
{
  "meta": {
    "creation_progress": {
      "step": 2,
      "concept": "<player's description>",
      "name": "<name>",
      "class": "<class>",
      "partial_classes": ["<pc1>", "<pc2>"],
      "background_id": <id>,
      "foci": ["<f1>", "<f2>"],
      "known_arts": ["<art1>", "<art2>"],
      "attribute_assignments": {"strength": 14, ...},
      "background_skills": ["<s1>", "<s2>"],
      "physical_boost": "<attr>",
      "mental_boost": "<attr>",
      "free_skill": "<skill>"
    }
  }
}
```

#### 2d. Extract world seeds from concept

After the build is approved, review the player's concept for world-relevant details:

- **Named NPCs mentioned** → seed into `known_npcs` with basic voice cards after `initialize-game` runs
- **Locations mentioned** → add to `known_locations` (merge with NYC defaults)
- **Faction affiliations implied** → adjust `pc_standing` entries (e.g., if player describes being a cop → JDA standing +1)
- **Relationships mentioned** → seed into appropriate trackers

These concept-derived overrides are applied to the generated state AFTER `initialize-game` runs (Step 3), before writing the final state.json. This is the same pattern as any Phase 5 persistence — the CLI produces the base state; the GM enriches it from the concept.

### Step 3: Execute and Confirm

Once the player approves, run initialization with all parameters:

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
1. Parse the JSON output
2. Apply concept-derived world seeds from Step 2d:
   - Merge concept-extracted NPCs into `state.known_npcs`
   - Adjust `state.pc_standing` based on implied affiliations
   - Add concept-mentioned locations to `state.known_locations`
   - Store concept text in `state.meta.character_concept` for future reference
3. Write `state.json` with the enriched state (removes `creation_progress`)
4. Validate with `python runtime/scripts/validate_state.py runtime/state.json`
5. Display the character sheet using the character-sheet-template
6. Render the opening scene using the scene-template
7. Present the opening narrative (see Opening Scene Protocol below)

## Resuming Interrupted Creation

If `creation_progress` exists in `meta` when loading state:

- **step 1**: Concept saved — skip to Step 2 (GM build) using saved concept
- **step 2**: Build saved — present saved build for approval, skip to Step 3 if approved

This handles conversation compression gracefully — no need to re-ask questions.

## Attribute Generation Reference

The **boosted_3d6** method:
1. Roll 3d6 for each of the six attributes (range: 3–18 each)
2. Replace the lowest rolled score with 14
3. GM assigns scores to attributes based on character concept

After background boosts (+2 physical, +2 mental), typical final ranges:
- Boosted stat: 14 + 2 = 16 (modifier +1)
- Good rolls: 10–13 (modifier 0), or 14+ (modifier +1)
- Low rolls: 3–7 (modifier -1 to -2) — the lowest is replaced, but second-lowest may still be weak
- Cap: 18 (modifier +2)

## Opening Scene Protocol

After character creation, render the first scene:

Load `lore/nyc-situation.md` §Initial Material State and §Immediate Pressures.
Set the scene on Day 1 — the moment of or morning after the Transport:

> The world changed overnight. Yesterday this was Manhattan. Today the skyline
> ends where it shouldn't — beyond the bridges, green wilderness stretches to
> distant mountains that have no business being there. Every screen is dead.
> Every engine is silent. The subways are tombs.

Present 2-3 immediate options drawn from the NYC situation:
- Investigate the changed surroundings
- Seek information from other people
- Secure supplies and shelter

## Canonical References

- Character creation: `phases/3-resolution/skills/core/scripts/character.py` (create_character)
- Chargen query: `phases/3-resolution/skills/core/scripts/chargen_query.py` (query_chargen_options)
- State schema: `schemas/state.schema.json` (v7.5.0)
- Scene template: `phases/4-narrative/assets/scene-template.md`
- Character sheet template: `phases/4-narrative/assets/character-sheet-template.md`
- NYC situation: `phases/1-context-loading/lore/nyc-situation.md`
- GM protocol: `phases/1-context-loading/references/gm-protocol.md`

## Scripts

| Script | Purpose |
|---|---|
| `scripts/emergence_cli.py query-chargen-options` | Get filtered options from Python tables |
| `scripts/emergence_cli.py initialize-game` | Generate complete initial state |
| `scripts/validate_state.py` | Validate generated state |

## Output Format

The `initialize-game` command outputs JSON:
```json
{
  "state": { ... },           // Complete state.json content
  "character_summary": { ... }, // Human-readable character overview
  "initialization_report": {   // Status and metadata
    "status": "success",
    "campaign": "nyc",
    "character_created": true,
    "clocks_initialized": 6,
    "starting_scene": "Carven Peaks — Lower Manhattan",
    "seed": 42
  },
  "seed": 42
}
```

## Common Failures

| Failure | Cause | Resolution |
|---|---|---|
| Invalid class/background combo | Player picked incompatible options | Re-query with valid options |
| Schema validation fails | Generated state missing required field | Bug — halt and report |
| Partial class validation fails | Invalid adventurer combo | Re-query with valid partial class pairs |
| Focus validation fails | Class-restricted focus selected | Re-query with class-appropriate foci |
| Attribute assignment mismatch | No score >= 14 in assignments | At least one assigned score must be >= 14 |
