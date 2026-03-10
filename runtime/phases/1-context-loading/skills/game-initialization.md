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

2. **Selects background** (from the 20 WWN backgrounds) that best fits the description. The background provides:
   - **2 skills at level 0** — chosen by GM from the background's skill list to match the concept
   - **+2 to one physical attribute** (Strength, Dexterity, or Constitution)
   - **+2 to one mental attribute** (Intelligence, Wisdom, or Charisma)
   - Choose boost targets that reinforce the character concept

Present everything together in one block: the rolled scores, attribute assignments, background, background skills, boost targets, and final attribute scores after boosts (capped at 18). Wait for player confirmation before proceeding.

### Step 3: Background Focus

Present all available foci organized by category with descriptions, and recommend 1-2 that complement the character concept and background. This is the character's first focus pick.

**Foci Categories** (present ALL categories with descriptions — player may pick from any they qualify for):

**General Foci** (any class):
- alert — Cannot be surprised, +1 initiative, bonus Notice
- artisan — Enhanced crafting, cheaper mods, bonus Craft
- assassin — Concealed weapons, surprise attacks can't miss, bonus Sneak
- authority — Attract followers, command loyalty, bonus Lead
- close_combatant — Bonus combat skill, +1 AC in melee, improved unarmed/short weapons
- connected — Contacts in every city, find black markets, bonus Connect
- cultured — Social knowledge, language facility, bonus Connect
- dealmaker — Better buying/selling prices, bonus Trade
- die_hard — +2 max HP per level, bonus Physical save
- diplomatic_grace — Defuse hostility, prevent ambushes, bonus Convince
- gifted_chirurgeon — Faster/better healing, stabilize dying, bonus Heal
- henchkeeper — Extra and more loyal henchmen, bonus Lead
- impostor — Master of disguise, false identities, bonus Perform or Sneak
- lucky — Once per week, negate a lethal/crippling outcome
- poisoner — Craft and apply poisons, identify toxins, bonus Heal
- rider — Expert mounted combat and riding, bonus Ride
- specialist (repeatable) — Gain any non-combat skill as bonus, reroll failed checks in it
- spirit_familiar — Magical companion (cat/hawk/etc.) with scouting/spying abilities
- trapmaster — Detect and disarm traps, craft improvised traps, bonus Notice
- unique_gift — Custom unusual ability or magical knack (GM approval)
- well_met — Improved reaction rolls, naturally likable
- xenoblooded — Alien heritage: choose darkvision, natural weapon, or environmental immunity

**Warrior Foci** (Warriors or Partial Warriors only):
- armsmaster — Add Stab to melee/thrown damage, instant weapon swap, bonus Stab
- deadeye — +1 ranged hit, ignore shooting into melee penalty, bonus Shoot
- impervious_defense — Innate AC 15 + half level, bonus to AC in heavy armor
- shocking_assault — Melee damage die explodes, bonus Punch or Stab
- snipers_eye — +2 ranged damage, negate cover penalties, bonus Shoot
- unarmed_combatant — Fists deal 1d6+Punch, improved grappling, bonus Punch
- valiant_defender — Screen ally as instant, +1 AC when defending, bonus Stab or Punch
- whirlwind_assault — Extra melee attack per round at -2, bonus Stab

**Maqqatban Knight Foci** (Warrior/Partial Warrior only, one style max):
- all_directions_edge_style — Bonus combat skill, +1 AC, enhanced Shock
- catalytic_soul_style — Boost allies' Shock, ranged stance, bonus Shoot
- ghost_archer_style — Ranged attacks ignore cover, hit fleeing foes, bonus Shoot
- one_point_strike_style — Massive single-strike damage, bonus combat skill
- pyre_of_heaven_style — Fire-enhanced attacks, area Shock damage, bonus combat skill
- righteous_iron_style — Defensive dueling, counter-attack triggers, bonus Exert
- world_tree_lance_style — Extended reach, charge attacks, mounted synergy, bonus Stab
- wrathful_mountain_style — Heavy weapon mastery, improved Shock, bonus Stab or Punch

**Expert Foci** (Experts or Partial Experts only):
- polymath — Gain any one bonus skill, versatile expertise

**Amundi Godblood Foci** (Expert/Partial Expert only, one godblood max):
- danger_sense — Preternatural threat awareness, bonus Notice
- folie_a_deux — Shared madness, social manipulation, bonus Convince
- master_tracker — Supernatural tracking ability, bonus Survive
- night_walker — See in darkness, move silently, bonus Sneak
- pack_beast — Superhuman carrying capacity, bonus Exert
- provident_crafter — Craft items from nothing, bonus Craft
- walk_like_wind — Supernatural speed and agility, bonus Exert
- wildtongue — Speak with animals and plants, bonus Survive

**Arcane Secret Foci** (Mages or Partial Mages only, one secret max):
- armored_magic — Cast spells in armor (light at L1, any at L2)
- atlantean_divination — Scrying and detection magic, bonus Know
- iteral_pacting — Bind and bargain with entities, bonus Pray
- nagadi_hemomancy — Blood-powered healing and curses, bonus Heal
- old_empire_sigilism — Embed spells in tokens as traps/wards
- vothite_mind_sorcery — Silent/gestureless casting, mental spell delivery

**Non-Mage Foci** (cannot be taken by Mages/Partial Mages):
- developed_attribute (repeatable) — +1 to chosen attribute modifier (max +2)
- nullifier — +2 saves vs magic for you and nearby allies, disrupt enemy spells

**Non-Human Origin Foci** (any class, one origin max):
- man — Pick any non-Magic bonus skill, +1 to any attribute modifier
- accipiter_anak — Eagle-kin: flight, keen vision, bonus Exert
- aristoi_anak — Noble-born: social authority, bonus Lead + one other
- choeru_beastfolk — Pig-kin: resilient, enhanced smell, bonus Convince or Connect
- deepfolk — Underground dweller: darkvision, stonecunning, bonus skill
- ghoul — Undead eater: must consume flesh, resist poison/disease, darkvision
- guer_beastfolk — Wolf-kin: pack tactics, tracking, bonus Notice or Sneak
- harbinger_anak — Shadow-kin: stealth, intimidation, bonus Sneak or Convince
- hua_beastfolk — Bear-kin: powerful build, natural weapons, bonus Exert
- kitsune_beastfolk — Fox-kin: shapeshifting, social cunning, bonus Notice or Convince
- manu_beastfolk — Bird-kin: gliding, keen senses, bonus Exert or Survive
- nahu_beastfolk — Snake-kin: flexibility, venom, bonus Sneak or Notice
- pichi_beastfolk — Mouse-kin: small, stealthy, perceptive, bonus Notice
- piren_beastfolk — Fish-kin: aquatic breathing, swimming, bonus Exert
- special_origin — Custom racial/species origin (GM approval)
- sui_beastfolk — Lizard-kin: scales, environmental resilience, bonus Survive
- usagi_beastfolk — Rabbit-kin: speed, agility, keen hearing, bonus Exert or Sneak
- zakathi — Reptilian: natural armor, darkvision, bonus Exert

**Extended partial class base types for focus eligibility:**
- Partial Expert includes: expert, bard, wise
- Partial Warrior includes: warrior, mageslayer
- Partial Mage includes: mage, accursed, invoker, skinshifter, duelist, beastmaster, blood_priest, thought_noble

Wait for player choice.

### Step 4: Class Selection

Present the four WWN classes with descriptions:

```
Classes:
  Warrior    — Combat specialist. Best HP, attack bonus, and Killing Blow ability.
  Expert     — Skill specialist. Reroll failed skill checks, extra skill points.
  Mage       — Arcane caster. Spells and Effort system, tradition-based magic.
  Adventurer — Dual-class. Pick two partial classes for hybrid abilities.
```

If **Adventurer** is chosen, present ALL partial class options with descriptions:

**Core Partial Classes:**
- warrior — Partial combat specialist. Veteran's Luck (negate hit once/scene), bonus Warrior focus
- expert — Partial skill specialist. Masterful Expertise (reroll one non-combat check/scene), bonus non-combat skill
- mage — Partial arcane caster. Reduced spell slots but access to tradition spells and Effort

**Extended Partial Classes (expert-type, replaces partial expert):**
- bard — Performer charged with the Legacy's power through music, song, and speech. Uses Perform skill + Cha for Effort. Arts include Battle Cry, Cursed Tune, Entangle Incantation, Rally
- wise — Low-magic scholar, priest, or oracle. No Effort pool. Arts include divination, curses, blessings, and social influence

**Extended Partial Classes (warrior-type, replaces partial warrior):**
- mageslayer — Anti-magic combat specialist focused on countering spellcasters. Uses Magic skill for Effort. Fixed art progression: Antimage, Magebane, Spellshield, etc.

**Extended Partial Classes (mage-type, replaces partial mage):**
- accursed — Eldritch pact-wielder. **Magic is the combat skill** (used for Accursed Blade/Bolt attack and damage rolls). Effort = Magic + max(Int, Cha) mod. Arts: Accursed Blade (1d8 melee, +Magic damage), Accursed Bolt (1d8+Magic ranged, 200'), plus curses and shadow powers
- invoker — Adunic spell-point caster. Casts High Magic spells using spell points instead of Vancian slots. No arts. Uses Magic skill
- skinshifter — Darian shapeshifter who masters alternate animal and humanoid forms. Effort = Survive + max(Con, Cha) mod. Arts: Change Form, natural weapons, wings, armor
- duelist — Kistian martial fencer specializing in evasion and single-weapon combat. Effort = Stab + max(Dex, Int) mod. Arts: Favored Weapon, Dodge Doom, Code Duello
- beastmaster — Llaigisan animal companion specialist who bonds with a loyal beast. Effort = Survive + max(Wis, Cha) mod. Arts: Bind Companion, natural weapons, telepathic link
- blood_priest — Sarulite divine miracle worker channeling faith through prayer. Effort = Pray + max(Wis, Cha) mod. Arts: Merciful Healing, Smite the Wicked, Turn False Life
- thought_noble — Vothite psychic who manipulates minds with invisible mental arts. Effort = Notice + max(Int, Wis) mod. Arts: telepathy, mind reading, telekinesis, psychic damage

**Invalid combinations:** mageslayer cannot pair with any mage-type partial class.

If the class is **Mage** or any partial class has base type mage (mage, accursed, invoker, skinshifter, duelist, beastmaster, blood_priest, thought_noble), prompt for **tradition selection**:

```
Mage Traditions:
  high_mage     — Classical wizard. Versatile arcane spells through study.
  elementalist  — Wielder of primal elemental forces (fire, water, earth, air).
  necromancer   — Master of death magic, undead creation, and life force.
  healer        — Supernatural healing physician. (Partial tradition only)
  vowed         — Ascetic martial artist channeling power through discipline. (Partial tradition only)
  invoker       — Adunic spell-point caster using High Magic spells without Vancian slots.
```

Note: healer and vowed are partial-only traditions (Adventurer with partial mage, not full Mage class).

Wait for player choice.

### Step 5: Second Focus and Free Skill

Present the full foci list again (same categories and descriptions as Step 3, filtered by class restrictions from Step 4). This is the character's second focus pick. The player may not pick the same focus twice (unless it is marked repeatable, e.g., specialist, developed_attribute).

Then ask for one free skill pick (any skill set to level 0). Note: if a skill is gained from multiple sources (background + free pick + focus bonus + class bonus), each additional grant stacks to a maximum of level 1.

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
