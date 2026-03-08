# State Persistence — Update Procedure

This skill governs how state.json is updated after each turn.

## When This Runs
- After Phase 4 narrative is complete
- Before Phase 6 validation

## Update Procedure

### Step 1: Identify State Changes

Review CLI output from Phase 3 for any state mutations:

| CLI Result | State Field(s) to Update |
|---|---|
| Attack damage dealt TO player | `character.hp.current` |
| Attack damage dealt BY player | (enemy HP tracked in scene, not state unless named NPC) |
| Skill check result | (usually no state change — narrative only) |
| Saving throw failure | Apply condition to character if applicable |
| Character creation | Replace entire `character` object |
| HP change | `character.hp.current` (never exceed `character.hp.max`) |
| System Strain change | `character.system_strain.current` |
| Equipment change | `character.equipment.readied` / `stowed` / `coins` |
| Scene change | `current_scene.*` fields |
| Time passage | `campaign.current_day`, `campaign.current_time`, `current_day`, `current_time` |
| NPC interaction | `known_npcs[].last_interaction_summary`, `.trust`, `.disposition` |
| Faction turn | `human_factions[].turn_history`, `.current_action` |
| Consequence created | Append to `consequence_tracker` |
| Consequence triggered | Update `consequence_tracker[].status` to `"triggered"` |
| Drama event | Decrement `session.drama_budget`, append to `session.drama_events` |
| Scene type tracking | Append to `campaign.scene_rhythm` (keep last 10 entries) |
| Supply change | Update `campaign.supplies.*` |
| Arc beat triggered | Update `campaign_arcs[].beats[].status` to `"triggered"` |
| Region change | Update `current_scene.region_id` |

### Step 2: Apply Changes

- Update fields atomically — all changes from one turn apply together
- Never update `character.hp.current` to exceed `character.hp.max`
- Never update `system_strain.current` to exceed `system_strain.max`
- Keep `current_day` and `campaign.current_day` synchronized
- Keep `current_time` and `campaign.current_time` synchronized

### Step 3: Append Chronicle Entry

If the turn involved a significant event, append to `chronicle`:
```json
{
  "day": <current_day>,
  "time": "<current_time>",
  "event": "<what happened>",
  "significance": "minor|moderate|major|critical",
  "tags": ["combat", "social", "exploration", ...]
}
```

Not every turn needs a chronicle entry. Skip for routine actions (looking around, asking basic questions).

### Step 4: Update Timestamps

- `meta.last_played` → current ISO-8601 timestamp
- `last_played` → same value (top-level mirror)

### Step 5: Write state.json

Write the updated state to disk.

### Step 6: Generate Turn Receipt (Optional)

For significant turns, record a turn receipt with:
- Commands executed and their arguments
- CLI output summaries
- State delta (fields changed, old → new values)
- RNG seed used
- Validation status

## Constraints

- **Never create fields** that don't exist in the schema. If a turn produces data that has no schema home, halt and flag for development.
- **Never delete required fields.** If a value should be "empty," use the appropriate zero value (0, "", [], {}).
- **Sync invariants:** `current_day == campaign.current_day`, `current_time == campaign.current_time`.
