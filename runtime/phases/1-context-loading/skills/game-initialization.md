# Game Initialization — New Game Startup Protocol

This skill governs how a new game session is started from scratch. It produces a valid, playable state.json through an interactive player-facing flow.

## When This Runs

- When state.json contains placeholder data (character.name == "Unnamed Hero")
- When the player explicitly requests a new game
- When session_number is 0 in state.json meta

## Detection: New Game vs. Returning Session

Check these conditions in order:

1. `meta.session_number == 0` → **New game** — run full initialization
2. `character.name == "Unnamed Hero"` → **New game** — run full initialization
3. `meta.session_number >= 1` AND valid character → **Returning session** — skip to session resume (increment session_number, reset drama budget, load context per lore-loading.md)

## Interactive Initialization Protocol (7 Steps)

### Step 1: Welcome and Campaign Selection

Present the player with a welcome and ask which campaign they want to play:

```
Available campaigns:
  1. NYC — Carven Peaks Campaign (modern city transported to the Latter Earth)
  2. Custom — Generic Latter Earth (starting at a crossroads inn)
```

Wait for player choice. Do not proceed without explicit selection.

### Step 2: Character Concept

Ask the player for their character concept in natural language:
- "Describe who your character is in a sentence or two."
- "What's their name?"

Use their response to inform class, background, and focus recommendations in the next steps.

### Step 3: Class Selection

Present the four WWN classes with brief descriptions:

```
Classes:
  Warrior  — Combat specialist. Best HP, attack bonus, and Killing Blow ability.
  Expert   — Skill specialist. Reroll failed skill checks, extra skill points.
  Mage     — Arcane caster. Spells and Effort system, tradition-based magic.
  Adventurer — Dual-class. Pick two partial classes for hybrid abilities.
```

If Adventurer is chosen, also ask for two partial classes. Present the available options:
- Core: warrior, expert, mage
- Extended: accursed, bard, mageslayer, wise, invoker, skinshifter, duelist, beastmaster, blood_priest, thought_noble

If a partial class includes mage (or is a magic tradition), prompt for tradition selection.

Wait for player choice.

### Step 4: Background Selection

Present the 20 WWN backgrounds (by ID) with their names and free skills. Recommend 2-3 that fit the character concept from Step 2.

Wait for player choice.

### Step 5: Focus Selection

Present available foci filtered by class restrictions. Recommend 1-2 that complement the character concept and class. At level 1, characters typically pick 1 focus (warriors get a bonus combat focus).

Wait for player choice.

### Step 6: Final Options

Present remaining choices:
- **Attribute method**: Standard Array (recommended for balanced play) or Roll 3d6 (random, may produce extreme values)
- **Skill method**: Quick (background-based preset) or Manual (choose individually — defer to play)
- **Equipment package**: List available packages, or "roll coins" for random starting wealth
- **Free skill pick**: One skill at level 0 of the player's choice

Wait for player choices.

### Step 7: Execute and Confirm

Run the initialization:

```
python runtime/scripts/emergence_cli.py initialize-game \
  --name "<name>" \
  --class <class> \
  --background <id> \
  --campaign <campaign> \
  --method <method> \
  --seed <seed> \
  [--partial-classes "cls1,cls2"] \
  [--tradition <tradition>] \
  [--foci "focus1,focus2"] \
  [--equipment-package <package>] \
  [--skill-method quick] \
  [--free-skill <skill>]
```

After execution:
1. Parse the JSON output
2. Write `state.json` with the `state` field from the output
3. Validate with `python runtime/scripts/validate_state.py runtime/state.json`
4. Display the character sheet using the character-sheet-template
5. Render the opening scene using the scene-template
6. Present the opening narrative (see Opening Scene Protocol below)

## Opening Scene Protocol

After character creation, render the first scene:

### For NYC Campaign
Load `lore/nyc-situation.md` §Initial Material State and §Immediate Pressures.
Set the scene on Day 1, Hour 8 — the morning after the Transport:

> The world changed overnight. Yesterday this was Manhattan. Today the skyline
> ends where it shouldn't — beyond the bridges, green wilderness stretches to
> distant mountains that have no business being there. Every screen is dead.
> Every engine is silent. The subways are tombs.

Present 2-3 immediate options drawn from the NYC situation:
- Investigate the changed surroundings
- Seek information from other people
- Secure supplies and shelter

### For Default Campaign
Set the scene at the Crossroads Inn on a morning:

> The inn stands where three roads meet, a weathered stone building older than
> anyone can remember. The innkeeper serves watered ale and hard bread. Through
> the window, the land stretches away in all directions — forest to the north,
> plains to the east, and something that might be ruins on the western horizon.

Present 2-3 immediate options:
- Talk to the innkeeper about the area
- Examine the road signs at the crossroads
- Investigate the ruins visible to the west

## Canonical References

- Character creation: `phases/3-resolution/skills/core/scripts/character.py` (create_character)
- State schema: `schemas/state.schema.json` (v7.5.0)
- Scene template: `phases/4-narrative/assets/scene-template.md`
- Character sheet template: `phases/4-narrative/assets/character-sheet-template.md`
- NYC situation: `phases/1-context-loading/lore/nyc-situation.md`
- GM protocol: `phases/1-context-loading/references/gm-protocol.md`

## Scripts

| Script | Purpose |
|---|---|
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
| Invalid class/background combo | Player picked incompatible options | Re-prompt with valid options |
| Schema validation fails | Generated state missing required field | Bug — halt and report |
| Partial class validation fails | Invalid adventurer combo | Re-prompt with valid partial class pairs |
| Focus validation fails | Class-restricted focus selected | Re-prompt with class-appropriate foci |
