# Turn Loop Contract (Runtime)

This document defines the strict turn protocol for runtime play.

## Preconditions

- Canonical script registry reviewed: `scripts/CLAUDE.md`
- Required runtime commands are marked `runtime-safe: yes`
- Canonical state file path is known (typically `state.json`)

## Mandatory sequence

0. **World preamble — check trigger conditions**
   - Run `check-triggers` against canonical state.
   - Review `commands_to_fire` in the output.
   - Execute any `priority: "high"` commands (missed portents, expired consequences, met arc beats) before capturing player input.
   - Log `priority: "medium"` suggestions for potential use during this turn.
   - This step is GM-initiated and does not require player action.

1. **Capture turn input and classify action**
   - Record player intent verbatim.
   - If player message starts with `DEVELOPMENT:`, skip to development mode — no CLI required.
   - Otherwise, classify the player's intent using `phases/2-action-interpretation/references/action-classification.md`.
     - Match intent to an Action Category in the table.
     - Check State-Dependent Routing conditions (same intent may map to different commands).
     - Check GM-Initiated Triggers for non-player-driven commands that should also fire.
   - The classification determines the primary CLI subcommand for step 4.
   - Do not execute mechanics until explicit player action payload is captured.

2. **Expand action into command sequence**
   - Run `expand-action --action <classified-command> --state-path state.json`.
   - This returns:
     - **pre_commands**: commands that must run BEFORE the primary (e.g., `generate-npc` before `reaction-roll` if NPC unknown)
     - **primary**: the classified command (unchanged)
     - **declared_chains**: commands that WILL or MAY fire after the primary (e.g., `world-tick` after `travel`)
     - **advisories**: non-blocking notes (e.g., "location already known — consider skill-check instead")
   - Review advisories and adjust if warranted.
   - The full command sequence for step 4 is: pre_commands → primary → (post-chains resolved after execution).
   - Source of truth for chain rules: `phases/3-resolution/skills/world-building/scripts/chain_registry.py`.

3. **Validate turn input provenance**
   - Run `validate-turn-input` against the action payload JSON.
   - Halt if `player_action_source` is not `user_verbatim` or `action_confirmed` is not `true`.

4. **Pre-validate state and create snapshot**
   - Run `validate-state` against canonical state.
   - If validation fails, halt turn.
   - Run `state-snapshot --state-path state.json` and save the output.
     This snapshot is used in step 7 for post-resolution delta detection.

5. **Apply mechanics via CLI**
   - Execute the command sequence from step 2 in order:
     1. Execute pre_commands (if any).
     2. Execute the primary command.
     3. After each command, evaluate post-chains using the command's result:
        - For `"will_fire"` chains, execute with resolved args.
        - For `"conditional"` chains, evaluate the condition against the result and execute if met.
   - Execute only documented runtime-safe `emergence-cli` commands.
   - Do not substitute hand-rolled mechanics.
   - Track all executed commands in an `executed_commands` set (for deduplication in step 8).
   - Accumulate `chain_results` dict keyed by chain command name → result.

6. **★ Select GM move (anti-stagnation)**
   - Run `select_move(command_name, command_result, ...)` from `gm_moves.py` on the primary result.
   - **Every player-action turn produces minimum Tier 1.** No Tier 0 exits. (Hard Rules #13, #14)
   - **Tier 1** (soft move): foreshadow, telegraph, opportunity, information. Counter increments.
   - **Tier 2** (hard move): consequence lands, telegraph escalates. Forced after 5 consecutive Tier 1 turns. Counter resets.
   - **Tier 3** (world move): clock/faction/environment shift. Forced after 8 consecutive Tier 1 turns. Counter resets.
   - Apply `suggested_mutations` from the move output to state.
   - Execute `suggested_chain` command if specified.
   - Feed `narrative_directive` to Phase 4 narration.
   - Update `session.turns_since_hard_move` per `counter_update`.
   - Six command dispatchers handle player-action primaries differently:
     - `skill-check`: gate-type aware, margin thresholds, telegraph escalation
     - `attack`: battlefield evolves every round, behavior profile foreshadow
     - `save`: reactive — resolves prior threat, event leaves a mark
     - `cast-spell`: magic ripples without double-taxing spell costs
     - `reaction-roll`: disposition IS the move, diplomacy integration
     - `travel`: promote most dramatic event, portents outrank travel events

7. **Persist canonical updates**
   - Write resulting canonical state updates (including move mutations from step 6).
   - Record RNG seed if randomness was used.

8. **Post-resolution trigger check (safety net)**
   - Run `post-resolution --pre-snapshot <snapshot-path> --state-path state.json --already-executed <comma-list>`.
   - Review `commands_to_fire` in the output.
   - Execute any `priority: "high"` follow-ups (day advancement, location change detection, XP threshold).
   - For `priority: "medium"` suggestions (e.g., treasure after combat, encounter at high threat), apply GM judgment.
   - **Depth limit**: repeat this step at most 3 times. If follow-ups generate further follow-ups, stop after 3 iterations and log remaining suggestions in the turn receipt.
   - Re-persist state after any follow-up commands.

9. **Post-validate state**
   - Re-run `validate-state`.
   - If post-validation fails, reject turn and flag remediation in development mode.

10. **Regenerate derived outputs**
    - Update any derived artifacts required by current workflow.
    - Never hand-edit derived artifacts.

11. **Write turn receipt**
    - Persist: full command sequence executed (pre-commands + primary + chains + post-resolution follow-ups + move selection), high-level outputs, files touched, checks run/passed, seeds, move tier fired, and any post-resolution deltas detected.

## Acceptance rule

A turn is accepted only if all steps (0 through 11) complete successfully in order.

## Halt conditions

- Missing required script in `scripts/CLAUDE.md`
- Script marked `runtime-safe: no` or `unknown`
- Script failure/non-zero status
- Missing/invalid player action provenance payload
- Schema validation failure
- Any ambiguous mechanic not resolved by canonical references
- Post-resolution depth limit exceeded (3 iterations) — log and continue, do not halt

## Command execution flow diagram

```
Step 0:  check-triggers ─── fire high-priority pre-turn commands
                │            (includes anti-stagnation check)
                │
Step 1:  Classify intent ─── action-classification.md
                │
Step 2:  expand-action ──── chain_registry.py
                │            ├── pre_commands?
                │            ├── primary
                │            └── declared_chains
                │
Steps 3-4: Validate ─── state-snapshot
                │
Step 5:  Execute ─── pre_commands → primary → post-chains
                │         (evaluate conditions, accumulate chain_results)
                │
Step 6:  ★ Select GM move ─── gm_moves.py
                │         ├── dispatch by command type
                │         ├── minimum Tier 1 (no Tier 0)
                │         ├── Tier 2 forced at 5 consecutive Tier 1
                │         ├── Tier 3 forced at 8 consecutive Tier 1
                │         └── apply mutations, feed narrative_directive
                │
Step 7:  Persist state (+ move mutations + counter update)
                │
Step 8:  post-resolution ─── detect deltas (day, location, combat, XP)
                │               ├── fire high-priority follow-ups
                │               └── repeat up to 3x
                │
Steps 9-11: Validate → Regenerate → Receipt
```
