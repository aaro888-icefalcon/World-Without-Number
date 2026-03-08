# Scene Rendering Template

Render when the scene changes, at session start, or when significant environmental shifts occur.

## Template

```
┌─────────────────────────────────────┐
│  {{current_scene.location}}
│  {{current_scene.region}} · {{scene_type_label}}
│  Day {{current_day}} · {{current_time}} · {{time_of_day_label}}
│  {{weather_description}}
└─────────────────────────────────────┘

{{threat_environment_description}}

{{visible_features}}

{{npc_presence}}

{{active_objectives}}
```

## Field Sources and Derivation

### Header Block

| Display Element | Source | Derivation |
|---|---|---|
| Location | `current_scene.location` | Direct |
| Region | `current_scene.region` | Direct |
| Scene type label | `current_scene.scene_type` | Capitalize; map: combat->"Hostile Ground", exploration->"Exploration", social->"Social Encounter", downtime->"Respite", travel->"Passage" |
| Day | `current_day` | Direct |
| Time | `current_time` | HH:MM format |
| Time of day | `current_time` | Derive: 05-08 dawn, 08-12 morning, 12-14 midday, 14-17 afternoon, 17-20 evening, 20-22 dusk, 22-05 night |
| Weather | `world_pulse` or scene context | GM generates from season/region; not stored in state |

### Threat Environment

Derive from `current_scene.threat_level`. See `references/threat-environment-mapping.md` for full sensory details per level.

| Threat Level | Display Prefix |
|---|---|
| 0 | *The air is calm.* |
| 1-2 | *Something feels unsettled.* |
| 3-4 | *Danger is near.* |
| 5+ | *This place wants you dead.* |

Follow the prefix with 1-2 sentences of environmental detail drawn from the threat mapping tables. Weave threat cues into the scene naturally — do not label them mechanically.

### Visible Features

List notable environmental features the PC can perceive. Draw from:
- `current_scene` context (GM-maintained scene description)
- `known_locations` entries matching current region
- Environmental objects relevant to current scene type

Format as short narrative sentences, not bullet lists:

> *A stone bridge spans the chasm ahead, its mortar crumbling. To the east, firelight flickers in the treeline. The path behind you has gone dark.*

### NPC Presence

For each NPC visible in the current scene:
1. Load from `known_npcs` by matching location/scene context
2. Display name, brief posture/activity, and disposition cue

> *Maren the chandler stands behind her counter, arms folded, watching you with guarded interest. Near the door, a hooded figure nurses a cup of something that steams faintly in the cold air — you do not recognize them.*

Known NPCs show name and disposition cue. Unknown NPCs show only observable details.

### Active Objectives

Pull from `active_quests` where status is active. Show as brief reminders:

```
── Objectives ───────────────────────
  ◆ {{quest.name}}: {{quest.current_step OR quest.description}}
  ◆ ...
```

Display at most 3 active quests. If more exist, show the 3 most recently updated and note "(+N more)".

## Display Rules

- **Full render**: Scene change, session start, major environmental shift, player requests "look around."
- **Partial update**: Only re-render sections that changed (e.g., NPC leaves, threat level shifts, time advances).
- **Combat scenes**: Omit objectives block; add combatant positions from `combat_state.zones` instead.
- **Travel scenes**: Emphasize weather and time of day; minimize NPC block unless caravan/companion travel.
