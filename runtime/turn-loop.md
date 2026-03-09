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
     - **advisories**: non-blocking notes (e.g., "location already known — consider narrative")
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
   - Track all executed commands in an `executed_commands` set (for deduplication in step 7).

6. **Persist canonical updates**
   - Write resulting canonical state updates.
   - Record RNG seed if randomness was used.

7. **Post-resolution trigger check (safety net)**
   - Run `post-resolution --pre-snapshot <snapshot-path> --state-path state.json --already-executed <comma-list>`.
   - Review `commands_to_fire` in the output.
   - Execute any `priority: "high"` follow-ups (day advancement, location change detection, XP threshold).
   - For `priority: "medium"` suggestions (e.g., treasure after combat, encounter at high threat), apply GM judgment.
   - **Depth limit**: repeat this step at most 3 times. If follow-ups generate further follow-ups, stop after 3 iterations and log remaining suggestions in the turn receipt.
   - Re-persist state after any follow-up commands.

8. **Post-validate state**
   - Re-run `validate-state`.
   - If post-validation fails, reject turn and flag remediation in development mode.

9. **Regenerate derived outputs**
   - Update any derived artifacts required by current workflow.
   - Never hand-edit derived artifacts.

10. **Write turn receipt**
    - Persist: full command sequence executed (pre-commands + primary + chains + post-resolution follow-ups), high-level outputs, files touched, checks run/passed, seeds, and any post-resolution deltas detected.

## Acceptance rule

A turn is accepted only if all steps (0 through 10) complete successfully in order.

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
                │         (evaluate conditions against each result)
                │
Step 6:  Persist state
                │
Step 7:  post-resolution ─── detect deltas (day, location, combat, XP)
                │               ├── fire high-priority follow-ups
                │               └── repeat up to 3x
                │
Steps 8-10: Validate → Regenerate → Receipt
```
