# Action Classification — Intent to CLI Routing

## Classification Procedure

1. Read the player's declared action
2. Match to a category below
3. Determine CLI command and arguments
4. Confirm: "You want to [action] — resolving as `[command]`. Proceed?"

## Action Routing Table

| Player Intent | Command | Example |
|---|---|---|
| "I attack / swing / shoot / stab" | `attack` | `attack --attack-bonus 1 --skill-level 0 --attribute-mod 2 --weapon-damage 1d8 --shock 2/15 --target-ac 14 --target-hp 8` |
| "I try to / attempt to [skill action]" | `skill-check` | `skill-check --attribute-mod 1 --skill-level 0 --difficulty 8` |
| "I dodge / resist / avoid" | `save` | `save --type evasion --level 1 --modifier 1` |
| "Roll [dice]" | `roll` | `roll 1d20+3` |
| "I cast [spell] / use magic" | `cast-spell` | `cast-spell --spell-name "Coruscating Coffin" --caster-level 3 --tradition high_magic --current-effort 1 --system-strain 0 --system-strain-max 11` |
| "We travel / head toward / march" | `travel` | `travel --terrain forest --days 3 --supplies 10` |
| "I search / loot / what's in the chest" | `treasure` | `treasure --tier 3` |
| "Time passes / we rest / downtime" | `world-tick` | `world-tick --days 7` |
| "I talk to / approach / NPC reaction" | `reaction-roll` | `reaction-roll --modifier 2` |
| "Describe the NPC / who is this" | `generate-npc` | `generate-npc --importance major --region coastal` |
| "What's in this area / describe scene" | `generate-scene` | `generate-scene --scene-type wilderness --tag-count 2 --threat-level 3` |
| "Generate encounter / what do we find" | `encounter` | `encounter --terrain forest --threat-level 4` |
| "Explore the dungeon" | `generate-dungeon` | `generate-dungeon --depth 2 --theme tomb` |
| Pure narrative / dialogue / observation | No CLI | Resolve narratively |

## Attribute/Skill Selection

| Intent | Attribute | Skill |
|---|---|---|
| Sneak past guards | Dexterity | Sneak |
| Persuade an NPC | Charisma | Talk or Lead |
| Climb a wall | Strength | Exert |
| Notice something hidden | Wisdom | Notice |
| Recall knowledge | Intelligence | Know |
| Pick a lock | Dexterity | Fix |
| Forage for food | Wisdom | Survive |
| Navigate wilderness | Intelligence | Survive |
| Treat a wound | Intelligence | Heal |
| Intimidate someone | Strength or Charisma | Talk or Lead |

## Difficulty Scale

| Difficulty | Target | When |
|---|---|---|
| Trivial | 6 | Almost anyone could do it |
| Routine | 8 | Requires some skill or luck |
| Challenging | 10 | Difficult untrained, reasonable skilled |
| Hard | 12 | Even skilled may fail |
| Very Hard | 14 | Only experts have a good chance |

## State-Dependent Routing

| Intent | If... | Route To | Otherwise |
|---|---|---|---|
| "Describe the area" | Location is new | `generate-scene` | Narrate from known state |
| "I talk to [NPC]" | NPC unknown | `generate-npc` then `reaction-roll` | `reaction-roll` only |
| "I attack" | No active combat | Set up combat, then `attack` | `attack` directly |
| "I rest" | Dangerous area (threat >= 3) | `encounter` check then `world-tick` | `world-tick` directly |

## Compound Actions

| Intent | Primary | Also Runs |
|---|---|---|
| "Talk to stranger" (unknown NPC) | `reaction-roll` | `generate-npc` first |
| "Travel to the coast" | `travel` | `world-tick` after |
| "Rest for the night" | `world-tick --days 1` | Check triggers after |
| "Kill the last goblin" (target dies) | `attack` | `treasure` if loot exists |

## GM-Initiated Triggers

Check these proactively — they fire on world state, not player intent:

| Condition | Command |
|---|---|
| Location threat >= 2, entering new area | `encounter` (rolled, not guaranteed) |
| First interaction with unnamed NPC | `generate-npc` then `reaction-roll` |
| In-game day advances | `world-tick --days N` |
| Environmental hazard | `save` |
| XP >= next level | Prompt player for level-up |

## Fallback Rule

If no command matches a creative action, use `skill-check` with the most appropriate attribute/skill and GM-chosen difficulty. Never say "you can't do that" unless physically impossible.
