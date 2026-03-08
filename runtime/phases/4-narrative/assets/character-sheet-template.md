# Character Sheet Display Template

Render at end-of-turn when character status changes, or on player request.

## Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {{character.name}} — {{character.class}} {{character.level}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Stat | Value |   | Stat | Value |
|------|-------|---|------|-------|
| STR  | {{character.attributes.strength}}  | | HP   | {{character.hp.current}}/{{character.hp.max}} |
| DEX  | {{character.attributes.dexterity}} | | AC   | {{character.armor_class}} |
| CON  | {{character.attributes.constitution}} | | AB   | +{{character.attack_bonus}} |
| INT  | {{character.attributes.intelligence}} | | Phys | {{character.saving_throws.physical}}+ |
| WIS  | {{character.attributes.wisdom}}  | | Evad | {{character.saving_throws.evasion}}+ |
| CHA  | {{character.attributes.charisma}} | | Ment | {{character.saving_throws.mental}}+ |

**System Strain**: {{character.system_strain.current}}/{{character.system_strain.max}}
**Effort**: {{character.effort.current}}/{{character.effort.max}}
**XP**: {{character.xp}}

**Conditions**: {{conditions_list OR "None"}}

── Equipment (Readied) ──────────────
{{#each character.equipment.readied}}
  • {{this}}
{{/each}}

── Equipment (Stowed) ───────────────
{{#each character.equipment.stowed}}
  • {{this}}
{{/each}}

── Coins ────────────────────────────
{{#each character.equipment.coins}}
  {{@key}}: {{this}}
{{/each}}

── Foci ─────────────────────────────
{{#each character.foci}}
  • {{this}}
{{/each}}

── Class Abilities ──────────────────
{{#each character.class_abilities}}
  • {{this}}
{{/each}}

── Skills ───────────────────────────
{{#each character.skills}}
  {{@key}}: {{this}}
{{/each}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Compact Combat View

Use during active combat when full sheet would be verbose:

```
{{character.name}} | HP {{character.hp.current}}/{{character.hp.max}} | AC {{character.armor_class}} | Strain {{character.system_strain.current}}/{{character.system_strain.max}} | Effort {{character.effort.current}}/{{character.effort.max}} | {{conditions_list OR "OK"}}
```

## Field Sources

All fields are derived from `state.json` root object `character`:

| Template Variable | State Path | Notes |
|---|---|---|
| `character.name` | `character.name` | |
| `character.class` | `character.class` | Capitalize for display |
| `character.level` | `character.level` | |
| `character.hp.*` | `character.hp.current`, `character.hp.max` | |
| `character.armor_class` | `character.armor_class` | |
| `character.attack_bonus` | `character.attack_bonus` | |
| `character.saving_throws.*` | `character.saving_throws.{physical,evasion,mental}` | Display as "N+" |
| `character.system_strain.*` | `character.system_strain.current`, `character.system_strain.max` | |
| `character.effort.*` | `character.effort.current`, `character.effort.max` | Omit section if null |
| `character.xp` | `character.xp` | Omit if not present |
| `conditions_list` | `combat_state.combatants[is_pc=true].conditions` | From active combat; else "None" |
| `character.equipment.readied` | `character.equipment.readied` | |
| `character.equipment.stowed` | `character.equipment.stowed` | |
| `character.equipment.coins` | `character.equipment.coins` | |
| `character.foci` | `character.foci` | Omit section if empty/null |
| `character.class_abilities` | `character.class_abilities` | Omit section if empty/null |
| `character.skills` | `character.skills` | Key-value pairs |

## Display Rules

- Show full sheet on: session start, level up, equipment change, player request.
- Show compact view on: each combat round, status effect change.
- Omit sections that are empty or null rather than showing blank entries.
