"""WWN command chain registry — deterministic action expansion and post-command chaining.

This module is the single source of truth for:
  1. Pre-command rules: state-dependent commands that must run BEFORE a primary command
  2. Post-command chains: commands that must run AFTER a primary command completes
  3. Action expansion: given a classified action type + state, returns a full command sequence

The turn loop calls expand_action() after Phase 2 classification (step 1.5) and
get_post_chains() after each command execution (step 4) to build the complete
command sequence for a turn.

Does NOT handle player intent classification (that's Phase 2 / action-classification.md).
Does NOT handle state-delta detection (that's check_post_resolution in triggers.py).
"""


# ─────────────────────────────────────────────────────────────────────────────
# Chain rule definitions
# ─────────────────────────────────────────────────────────────────────────────

# Post-command chains: after command X completes, also run command Y.
# Each rule has:
#   - "follow_up": command name to run
#   - "condition": "always" | callable(command_result) -> bool
#   - "args_from_result": dict mapping follow-up arg names to result JSON keys
#                         (dot notation for nested: "days_elapsed" -> result["days_elapsed"])
#   - "args_static": dict of static args (used when args don't come from result)
#   - "reason": human-readable reason for the chain
#   - "priority": "high" (must run) | "medium" (GM decides) | "low" (optional)

POST_COMMAND_CHAINS = {
    "travel": [
        {
            "follow_up": "world-tick",
            "condition": "always",
            "args_from_result": {"days": "days"},
            "reason": "Travel advances in-game time",
            "priority": "high",
        },
    ],
    "world-tick": [
        {
            "follow_up": "check-triggers",
            "condition": "always",
            "args_static": {},
            "reason": "Clock/consequence advancement may trigger portents",
            "priority": "high",
        },
    ],
    "attack": [
        {
            "follow_up": "treasure",
            "condition": lambda result: result.get("target_down", False),
            "args_static": {"tier": 1},
            "reason": "Defeated enemy — loot check (GM confirms loot exists)",
            "priority": "medium",
        },
    ],
    "rest": [
        {
            "follow_up": "world-tick",
            "condition": "always",
            "args_static": {"days": 1},
            "reason": "Overnight rest advances 1 in-game day",
            "priority": "high",
        },
    ],
}

# Pre-command rules: state-dependent commands that run BEFORE the primary command.
# Each rule has:
#   - "when_action": the classified action type this rule applies to
#   - "prepend": command to run before the primary
#   - "state_condition": callable(state) -> bool
#   - "args_from_state": callable(state) -> dict of args for the prepended command
#   - "reason": human-readable reason
#
# These handle the "generate-npc before reaction-roll if NPC unknown" pattern.

PRE_COMMAND_RULES = [
    {
        "when_action": "reaction-roll",
        "prepend": "generate-npc",
        "state_condition": lambda state: _npc_context_is_unknown(state),
        "args_from_state": lambda state: {
            "importance": "minor",
            "region": state.get("current_scene", {}).get("region", "unknown"),
            "tags": 1,
        },
        "reason": "NPC not in known_npcs — generate before rolling reaction",
    },
    {
        "when_action": "generate-scene",
        "prepend": None,  # No prepend — this is a routing override
        "state_condition": lambda state: _location_is_known(state),
        "skip_primary": False,  # Don't skip; just flag for GM awareness
        "reason": "Location already in known_locations — consider narrative instead of generate-scene",
        "advisory": True,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# State condition helpers
# ─────────────────────────────────────────────────────────────────────────────

def _npc_context_is_unknown(state):
    """Check if the current interaction target NPC is not in known_npcs.

    Heuristic: if the current_scene has a pending_npc_interaction flag or
    the most recent action references an NPC name not in known_npcs.
    Falls back to False (safe default — don't prepend generate-npc).
    """
    pending = state.get("current_scene", {}).get("pending_npc_name")
    if not pending:
        return False
    known_names = {
        npc.get("name", "").lower()
        for npc in state.get("known_npcs", [])
    }
    return pending.lower() not in known_names


def _location_is_known(state):
    """Check if the current location is already in known_locations."""
    current_loc = state.get("current_scene", {}).get("location", "")
    if not current_loc:
        return False
    known = {
        loc.get("name", "").lower()
        for loc in state.get("known_locations", [])
    }
    return current_loc.lower() in known


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────

def expand_action(action_type, state):
    """Expand a classified action type into a full command sequence.

    Called after Phase 2 classification (turn loop step 1.5).

    Args:
        action_type: string, the classified CLI command name (e.g., "travel", "attack")
        state: full state.json dict for evaluating pre-command conditions

    Returns:
        dict with:
          - pre_commands: list of commands to run before the primary
          - primary: the original classified command (unchanged)
          - declared_chains: list of post-command chain rules that WILL fire
                            (conditions evaluated as "always" are included;
                             result-dependent conditions are flagged as "conditional")
          - advisories: list of non-blocking notes for the GM
          - arithmetic_trace: string summary
    """
    # Narrative pseudo-command: no CLI execution, no chains, no pre-commands.
    # The turn loop skips CLI (step 5 narrative branch) and calls
    # select_move("narrative", {}) which dispatches to _move_narrative_fallback.
    if action_type == "narrative":
        return {
            "action_type": "narrative",
            "primary": "narrative",
            "skip_cli": True,
            "pre_commands": [],
            "declared_chains": [],
            "advisories": [],
            "arithmetic_trace": "Action: narrative | No CLI execution | GM move still fires via narrative fallback",
        }

    pre_commands = []
    advisories = []

    # Evaluate pre-command rules
    for rule in PRE_COMMAND_RULES:
        if rule["when_action"] != action_type:
            continue

        if rule.get("advisory"):
            try:
                if rule["state_condition"](state):
                    advisories.append({
                        "message": rule["reason"],
                        "for_action": action_type,
                    })
            except Exception:
                pass
            continue

        try:
            if rule["state_condition"](state):
                pre_cmd = {
                    "command": rule["prepend"],
                    "args": rule["args_from_state"](state) if rule.get("args_from_state") else {},
                    "reason": rule["reason"],
                    "source": "pre_command_rule",
                }
                pre_commands.append(pre_cmd)
        except Exception:
            pass

    # Declare post-command chains (known before execution)
    declared_chains = []
    for chain_rule in POST_COMMAND_CHAINS.get(action_type, []):
        entry = {
            "follow_up": chain_rule["follow_up"],
            "reason": chain_rule["reason"],
            "priority": chain_rule["priority"],
        }
        if chain_rule["condition"] == "always":
            entry["status"] = "will_fire"
            entry["args"] = chain_rule.get("args_static", {})
        else:
            entry["status"] = "conditional"
            entry["condition_note"] = "Depends on command result"
        declared_chains.append(entry)

    # Build trace
    parts = [f"Action: {action_type}"]
    if pre_commands:
        pre_names = [c["command"] for c in pre_commands]
        parts.append(f"Pre: {' → '.join(pre_names)}")
    parts.append(f"Primary: {action_type}")
    if declared_chains:
        chain_names = [c["follow_up"] for c in declared_chains]
        parts.append(f"Post: {' → '.join(chain_names)}")
    if advisories:
        parts.append(f"Advisories: {len(advisories)}")

    return {
        "action_type": action_type,
        "pre_commands": pre_commands,
        "primary": action_type,
        "declared_chains": declared_chains,
        "advisories": advisories,
        "arithmetic_trace": " | ".join(parts),
    }


def get_post_chains(command_name, command_result):
    """Get concrete follow-up commands after a command completes.

    Called after each command execution in step 4. Evaluates result-dependent
    conditions and resolves args from the command's output JSON.

    Args:
        command_name: string, the command that just ran
        command_result: dict, the JSON output of the command

    Returns:
        list of dicts, each with:
          - command: follow-up command name
          - args: concrete args dict (resolved from result)
          - reason: human-readable reason
          - priority: "high" | "medium" | "low"
          - source: "chain_registry"
    """
    chains = POST_COMMAND_CHAINS.get(command_name, [])
    follow_ups = []

    for rule in chains:
        # Evaluate condition
        condition = rule["condition"]
        if condition == "always":
            should_fire = True
        elif callable(condition):
            try:
                should_fire = condition(command_result)
            except Exception:
                should_fire = False
        else:
            should_fire = False

        if not should_fire:
            continue

        # Resolve args
        args = dict(rule.get("args_static", {}))

        # Override with args from result
        for arg_name, result_key in rule.get("args_from_result", {}).items():
            value = _resolve_result_key(command_result, result_key)
            if value is not None:
                args[arg_name] = value

        follow_ups.append({
            "command": rule["follow_up"],
            "args": args,
            "reason": rule["reason"],
            "priority": rule["priority"],
            "source": "chain_registry",
        })

    return follow_ups


def _resolve_result_key(result, key):
    """Resolve a key from command result JSON.

    Supports simple keys ("days_elapsed") and dot-notation ("target.hp_after").
    Returns None if key not found.
    """
    parts = key.split(".")
    current = result
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def get_all_chain_rules():
    """Return all chain rules for documentation/testing.

    Returns:
        dict with post_chains and pre_commands for introspection.
    """
    # Serialize chain rules (replace lambdas with descriptions)
    post_chains = {}
    for cmd, rules in POST_COMMAND_CHAINS.items():
        post_chains[cmd] = []
        for rule in rules:
            entry = {
                "follow_up": rule["follow_up"],
                "condition": "always" if rule["condition"] == "always" else "result-dependent",
                "reason": rule["reason"],
                "priority": rule["priority"],
            }
            if rule.get("args_from_result"):
                entry["args_from_result"] = rule["args_from_result"]
            if rule.get("args_static"):
                entry["args_static"] = rule["args_static"]
            post_chains[cmd].append(entry)

    pre_commands = []
    for rule in PRE_COMMAND_RULES:
        pre_commands.append({
            "when_action": rule["when_action"],
            "prepend": rule.get("prepend"),
            "reason": rule["reason"],
            "advisory": rule.get("advisory", False),
        })

    return {
        "post_chains": post_chains,
        "pre_commands": pre_commands,
    }
