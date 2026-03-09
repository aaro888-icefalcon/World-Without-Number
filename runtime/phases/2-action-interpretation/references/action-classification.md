# Action Classification — WWN

Classify player intent into one of the supported CLI commands. This is the master router for Phase 2.

## Classification Procedure

1. Read the player's declared action in natural language
2. Identify the mechanical category (see table below)
3. Select the correct CLI subcommand and determine required arguments
4. Present the interpreted action back to the player for confirmation before Phase 3 executes

## Intent Confirmation

After classification, confirm with the player:
> "You want to [action description] — this will be resolved as `emergence_cli.py [command] [args]`. Proceed?"

This prevents misinterpretation (AI Limitation L2) and preserves player agency.

## Action Categories

| Player Intent Pattern | Category | CLI Command | Example |
|---|---|---|---|
| "I attack / I swing / I shoot / I stab" | Combat | `attack` | `attack --attack-bonus 1 --skill-level 0 --attribute-mod 2 --weapon-damage 1d8 --shock 2/15 --target-ac 14 --target-hp 8` |
| "I try to / I attempt to [skill-based action]" | Skill Check | `skill-check` | `skill-check --attribute-mod 1 --skill-level 0 --difficulty 8` |
| "I dodge / I resist / I try to avoid" | Saving Throw | `save` | `save --type evasion --level 1 --modifier 1` |
| "Roll [dice]" (explicit dice request) | Dice Roll | `roll` | `roll 1d20+3` |
| "I cast [spell] / I use magic" | Spellcasting | `cast-spell` | `cast-spell --spell-name "Coruscating Coffin" --caster-level 3 --tradition high_magic --current-effort 1 --system-strain 0 --system-strain-max 11` |
| "Let's travel / we head toward / we march" | Travel | `travel` | `travel --terrain forest --days 3 --supplies 10` |
| "I search / I look for treasure / what's in the chest" | Treasure | `treasure` | `treasure --tier 3` |
| "What happens in town / time passes / we rest for a week" | World Tick | `world-tick` | `world-tick --days 7` |
| "I talk to / I approach / how does the NPC react" | Reaction | `reaction-roll` | `reaction-roll --modifier 2` |
| "Describe the NPC / who is this person" | NPC Generation | `generate-npc` | `generate-npc --importance major --region coastal --tags 2` |
| "What are the factions doing / between-session time" | Faction Turn | `faction-turn` | `faction-turn` |
| "What's in this area / describe the scene" | Scene Generation | `generate-scene` | `generate-scene --scene-type wilderness --tag-count 2 --threat-level 3` |
| "Generate an encounter / what do we find" | Encounter | `encounter` | `encounter --terrain forest --threat-level 4` |
| "I level up / I gain a level / advance to level X" | Level Up | `level-up` | `level-up --name Kira --class warrior --current-level 1 --target-level 2 --attributes '{"strength":14,...}' --hp-max 8 --attack-bonus 1` |
| "Explore the dungeon / what's in this dungeon" | Dungeon Gen | `generate-dungeon` | `generate-dungeon --depth 2 --theme tomb` |
| Pure narrative / dialogue / observation | No Mechanic | (none) | Resolve in Phase 4 narratively — no CLI needed |

## Attribute/Skill Selection Guide

When the player's intent maps to a skill check, choose the most appropriate combination:

| Intent | Likely Attribute | Likely Skill |
|---|---|---|
| Sneak past guards | Dexterity | Sneak |
| Persuade an NPC | Charisma | Talk or Lead |
| Climb a wall | Strength | Exert |
| Notice something hidden | Wisdom | Notice |
| Recall knowledge | Intelligence | Know |
| Pick a lock | Dexterity | Fix |
| Forage for food | Wisdom | Survive |
| Navigate wilderness | Intelligence | Survive |
| Treat a wound | Intelligence or Dexterity | Heal |
| Read a foreign text | Intelligence | Know |
| Intimidate someone | Strength or Charisma | Talk or Lead |

## Difficulty Guidelines (per WWN)

| Difficulty | Target | When to Use |
|---|---|---|
| Trivial | 6 | Almost anyone could do it |
| Routine | 8 | Requires some skill or luck |
| Challenging | 10 | Difficult for untrained, reasonable for skilled |
| Hard | 12 | Even skilled characters may fail |
| Very Hard | 14 | Only experts have a good chance |

## Fallback Rule

If no specific CLI command matches the player's creative action, fall back to `skill-check` with the most appropriate attribute/skill combination and a GM-chosen difficulty. Never respond with "you can't do that" unless the action is physically impossible.

---

## Command Expansion (Step 1.5)

After classifying the player's intent, run `expand-action` to get the full command sequence:

```
emergence_cli.py expand-action --action <classified-command> --state-path state.json
```

This returns pre-commands (that must run before the primary), the primary command, and declared post-chains (that will fire after). Execute the full sequence in order. See `chain_registry.py` for the authoritative chain rules.

## GM-Initiated Triggers

These commands fire based on world state, **not** player intent. The GM must check these conditions proactively. `check-triggers` (step 0) evaluates most automatically; the table below covers cases requiring GM judgment.

| Condition | Command | When to Check | Priority |
|---|---|---|---|
| Location `threat_level` >= 2 | `encounter` (rolled, not guaranteed) | Every location transition | Medium |
| NPC not in `known_npcs` and player interacts | `generate-npc` → `reaction-roll` | First interaction with unnamed NPC | High |
| In-game day advances (any cause) | `world-tick --days N` | After travel, rest, or time-skip | High |
| 7+ days since last faction turn | `faction-turn` | After any `world-tick` | High |
| Environmental hazard in scene | `save` (type varies) | Player enters or interacts with hazard | High |
| PC XP >= next level threshold | Prompt player for `level-up` | Session start or after XP gain | Medium |
| Consequence timer expires | Fire consequence (hard rule #12) | Checked by `check-triggers` automatically | High |
| Clock portent unfired at/below current | Fire portent narrative | Checked by `check-triggers` automatically | High |

## Compound Actions

Some player intents require multiple commands executed in sequence. Classify as the **primary** action; `expand-action` handles chaining automatically.

| Player Intent | Primary Command | Also Runs (via chain registry) | Notes |
|---|---|---|---|
| "I talk to the stranger" (unknown NPC) | `reaction-roll` | `generate-npc` (pre-command) | expand-action prepends generate-npc if NPC not in known_npcs |
| "We travel to the coast" | `travel` | `world-tick` (post-chain) | Days elapsed from travel feed into world-tick |
| "We rest for the night" | `world-tick --days 1` | `check-triggers` (post-chain) | Time advancement chains trigger evaluation |
| "I kill the last goblin" (target dies) | `attack` | `treasure` (conditional post-chain) | Only fires if target_down=true; GM confirms loot exists |
| "I search the ruins and loot the bodies" | `skill-check` then `treasure` | — | Classify as skill-check first; if successful, run treasure separately |

## State-Dependent Routing

The same player intent may map to different commands depending on game state. Check these conditions during classification:

| Player Intent | State Condition | Route To | Otherwise |
|---|---|---|---|
| "Describe the area" / scene description | Location NOT in `known_locations` | `generate-scene` | Narrate from existing `current_scene` (no CLI) |
| "I talk to [NPC name]" | NPC NOT in `known_npcs` | `generate-npc` → `reaction-roll` | `reaction-roll` only (NPC already exists) |
| "I attack" | `combat_state.active` is false | Start combat: set up combat state, THEN `attack` | `attack` directly (combat already active) |
| "I rest / camp for the night" | In dangerous area (`threat_level` >= 3) | `encounter` check THEN `world-tick` | `world-tick --days 1` directly |

## Post-Resolution Safety Net (Step 5.5)

After persisting state, the turn loop runs `post-resolution` to detect state changes the chain registry might have missed. This catches:
- Day advancement from any source → suggests `world-tick`
- Location transitions → suggests `generate-scene` if location unknown
- Combat ending → suggests `treasure`
- XP crossing level threshold → suggests `level-up`

See `triggers.py:check_post_resolution()` for the authoritative delta detection logic.
