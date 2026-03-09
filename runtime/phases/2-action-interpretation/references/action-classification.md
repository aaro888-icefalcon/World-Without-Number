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
