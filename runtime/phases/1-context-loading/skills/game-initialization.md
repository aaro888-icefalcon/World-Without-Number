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

## Campaign

All games use the **NYC — Carven Peaks Campaign**. No campaign selection step.

## Interactive Initialization Protocol (6 Steps)

### Step 1: Welcome and Character Description

Welcome the player. Ask them to describe their character:

- "Who are you? Describe your character in a few sentences — name, who they are, what they're good at, what matters to them."

Use their response to determine:
- Character name
- Attribute assignment priorities (which stats should be highest)
- Background selection (which of the 20 backgrounds best fits)
- Recommended class, foci, and skills

Do not proceed without a player response.

### Step 2: Attributes and Background (Auto-Generated)

Based on the player's description, the GM:

1. **Rolls attributes** using `boosted_3d6` method:
   - Roll 3d6 for each of the six attributes
   - Replace the lowest rolled score with 14 (guaranteeing at least one strong stat)
   - GM assigns the rolled scores to attributes based on the character concept
   - Present the rolls and assignment to the player for confirmation

2. **Selects background** (from the 20 WWN backgrounds) that best fits the description. The background provides:
   - **2 skills at level 0** — chosen by GM from the background's skill list to match the concept
   - **+2 to one physical attribute** (Strength, Dexterity, or Constitution)
   - **+2 to one mental attribute** (Intelligence, Wisdom, or Charisma)
   - Choose boost targets that reinforce the character concept

Present the background, skills, and boosts to the player. Show final attribute scores after boosts (capped at 18).

### Step 3: Background Focus

Present available foci and recommend 1-2 that complement the character concept and background. This is the character's first focus pick.

Wait for player choice.

### Step 4: Class Selection

Present the four WWN classes:

```
Classes:
  Warrior  — Combat specialist. Best HP, attack bonus, and Killing Blow ability.
  Expert   — Skill specialist. Reroll failed skill checks, extra skill points.
  Mage     — Arcane caster. Spells and Effort system, tradition-based magic.
  Adventurer — Dual-class. Pick two partial classes for hybrid abilities.
```

If **Adventurer** is chosen, ask which two partial classes:
- Core: warrior, expert, mage
- Extended: accursed, bard, mageslayer, wise, invoker, skinshifter, duelist, beastmaster, blood_priest, thought_noble

If a partial class includes mage (or is a magic tradition), prompt for tradition selection.

Wait for player choice.

### Step 5: Second Focus and Free Skill

Present available foci (filtered by class restrictions from Step 4). This is the character's second focus pick.

Then ask for one free skill pick (any skill set to level 0).

Wait for player choices.

### Step 6: Execute and Confirm

Run the initialization:

```
python runtime/scripts/emergence_cli.py initialize-game \
  --name "<name>" \
  --class <class> \
  --background <id> \
  --method boosted_3d6 \
  --attribute-assignments "strength=X,dexterity=X,constitution=X,intelligence=X,wisdom=X,charisma=X" \
  --background-skills "skill1,skill2" \
  --physical-boost <str|dex|con> \
  --mental-boost <int|wis|cha> \
  --foci "focus1,focus2" \
  --free-skill <skill> \
  [--partial-classes "cls1,cls2"] \
  [--tradition <tradition>] \
  [--equipment-package <package>] \
  --seed <seed>
```

After execution:
1. Parse the JSON output
2. Write `state.json` with the `state` field from the output
3. Validate with `python runtime/scripts/validate_state.py runtime/state.json`
4. Display the character sheet using the character-sheet-template
5. Render the opening scene using the scene-template
6. Present the opening narrative (see Opening Scene Protocol below)

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

## Background Quick Reference

| ID | Name | Free Skill | Skill Pool |
|---|---|---|---|
| 1 | Artisan | Craft | Connect, Exert, Know, Notice, Trade |
| 2 | Barbarian | Survive | Exert, Notice, Punch, Sneak, Survive |
| 3 | Carter | Ride | Connect, Craft, Exert, Notice, Trade |
| 4 | Courtesan | Perform | Connect, Convince, Notice, Perform, Sneak |
| 5 | Criminal | Sneak | Connect, Convince, Notice, Sneak, Trade |
| 6 | Hunter | Shoot | Exert, Notice, Sneak, Survive, Shoot |
| 7 | Laborer | Exert | Connect, Craft, Exert, Notice, Survive |
| 8 | Merchant | Trade | Connect, Convince, Know, Notice, Trade |
| 9 | Noble | Lead | Administer, Connect, Convince, Know, Lead |
| 10 | Nomad | Ride | Exert, Notice, Ride, Survive, Shoot |
| 11 | Peasant | Exert | Connect, Craft, Exert, Notice, Survive |
| 12 | Performer | Perform | Connect, Convince, Notice, Perform, Sneak |
| 13 | Physician | Heal | Convince, Heal, Know, Notice, Trade |
| 14 | Priest | Pray | Administer, Convince, Know, Lead, Pray |
| 15 | Sailor | Sail | Connect, Exert, Notice, Sail, Survive |
| 16 | Scholar | Know | Administer, Connect, Convince, Know, Notice |
| 17 | Slave | Exert | Craft, Exert, Notice, Sneak, Survive |
| 18 | Soldier | Stab | Exert, Lead, Notice, Ride, Stab |
| 19 | Thug | Punch | Connect, Convince, Exert, Notice, Punch |
| 20 | Wanderer | Survive | Connect, Notice, Ride, Sneak, Survive |

The GM picks 2 skills from the background's pool (free skill + quick skills combined) that best fit the player's description.

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
| Attribute assignment mismatch | No score >= 14 in assignments | At least one assigned score must be >= 14 |
