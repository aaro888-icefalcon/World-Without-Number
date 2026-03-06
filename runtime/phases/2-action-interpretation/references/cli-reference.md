# CLI Reference — emergence_cli.py

Complete command contract for all registered subcommands. Phase 2 uses this to construct correct CLI invocations.

## Global Options

| Option | Type | Description |
|---|---|---|
| `--seed INT` | Optional | Set RNG seed for reproducible output. Record in turn receipt. |

## Commands

### `roll`

Roll dice using standard notation.

```
emergence_cli.py roll <expression> [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `expression` | positional string | Yes | Dice notation: `1d20+3`, `2d6`, `1d8-1`, `3d6` |

**Output JSON:**
```json
{
  "expression": "1d20+3",
  "rolls": [15],
  "modifier": 3,
  "total": 18,
  "arithmetic_trace": "[15]+3 = 18",
  "seed": 42
}
```

---

### `skill-check`

Make a 2d6 + skill + attribute modifier check against a difficulty target.

```
emergence_cli.py skill-check --attribute-mod INT --skill-level INT --difficulty INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--attribute-mod` | int | Yes | Attribute modifier (-2 to +2) |
| `--skill-level` | int | Yes | Skill level (-1 unskilled to 4 master) |
| `--difficulty` | int | Yes | Target number (6-14) |

**Output JSON:**
```json
{
  "rolls": [3, 5],
  "modifier": 1,
  "total": 9,
  "arithmetic_trace": "[3+5]+1 = 9",
  "target": 8,
  "success": true,
  "margin": 1,
  "attribute_mod": 0,
  "skill_level": 1,
  "difficulty": 8,
  "seed": 42
}
```

---

### `save`

Make a saving throw (1d20 >= target).

```
emergence_cli.py save --type TYPE --level INT --modifier INT [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--type` | choice | Yes | `physical`, `evasion`, or `mental` |
| `--level` | int | Yes | Character level |
| `--modifier` | int | Yes | Best relevant attribute modifier |

Save target = 16 - (level + modifier).

**Output JSON:**
```json
{
  "roll": 14,
  "target": 14,
  "success": true,
  "arithmetic_trace": "d20=[14] vs target 14",
  "save_type": "physical",
  "level": 1,
  "modifier": 1,
  "seed": 42
}
```

---

### `attack`

Resolve a combat attack (hit roll + damage or shock).

```
emergence_cli.py attack --attack-bonus INT --skill-level INT --attribute-mod INT \
    --weapon-damage STR --shock STR --target-ac INT --target-hp INT \
    [--killing-blow INT] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--attack-bonus` | int | Yes | Base attack bonus from class |
| `--skill-level` | int | Yes | Combat skill level (Stab, Shoot, Punch) |
| `--attribute-mod` | int | Yes | Relevant attribute modifier (Str for melee, Dex for ranged) |
| `--weapon-damage` | string | Yes | Damage die notation: `1d8`, `1d6+1` |
| `--shock` | string | No | Shock notation: `2/15` or `none` (default: `none`) |
| `--target-ac` | int | Yes | Defender's armor class |
| `--target-hp` | int | Yes | Defender's current HP |
| `--killing-blow` | int | No | Warrior Killing Blow bonus (default: 0) |

**Output JSON:**
```json
{
  "hit_roll": 15,
  "total_roll": 18,
  "attack_bonus_breakdown": "AB=1 + Skill=1 + Attr=1 = +3",
  "target_ac": 14,
  "natural_20": false,
  "natural_1": false,
  "hit": true,
  "damage": 7,
  "damage_roll": [5],
  "damage_trace": "1d8=5+1(attr)+1(KB) = 7",
  "shock_applied": false,
  "shock_damage": 0,
  "arithmetic_trace": "d20=[15]+3 = 18 → HIT! Damage: 1d8=5+1(attr)+1(KB) = 7",
  "target_hp_before": 8,
  "target_hp_after": 1,
  "target_down": false,
  "seed": 42
}
```

---

### `create-character`

Create a new WWN character.

```
emergence_cli.py create-character --name STR --class CLASS --background INT \
    [--method METHOD] [--seed INT]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `--name` | string | Yes | Character name |
| `--class` | choice | Yes | `warrior`, `expert`, or `mage` |
| `--background` | int | Yes | Background ID (1-20) |
| `--method` | choice | No | `standard_array` (default) or `roll_3d6` |

**Output JSON:** Complete character dict with all fields required by state.json `character` schema.
