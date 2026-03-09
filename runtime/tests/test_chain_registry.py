"""
Test suite for chain_registry.py and post-resolution trigger detection.

Covers:
  - expand_action: pre-commands, declared chains, advisories
  - get_post_chains: result-dependent conditions, args resolution
  - check_post_resolution: day change, location change, combat end, XP threshold
  - create_state_snapshot: correct field extraction
  - Deduplication: already_executed filtering
  - CLI integration: expand-action, state-snapshot, post-resolution commands
"""

import copy
import json
import os
import sys
import subprocess

# Ensure imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

_runtime_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
_skills_dir = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills')
if os.path.isdir(_skills_dir):
    for _domain in os.listdir(_skills_dir):
        for _subdir in ['scripts', 'tables']:
            _p = os.path.join(_skills_dir, _domain, _subdir)
            if os.path.isdir(_p) and _p not in sys.path:
                sys.path.insert(0, _p)

from chain_registry import expand_action, get_post_chains, get_all_chain_rules
from triggers import check_post_resolution, create_state_snapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CLI_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'emergence_cli.py'
)


def _make_state(**overrides):
    """Create a minimal valid state dict for testing."""
    state = {
        "current_day": 1,
        "current_scene": {
            "location": "Test City",
            "threat_level": 1,
            "scene_type": "community",
            "region": "test",
        },
        "combat_state": {"active": False, "enemies": []},
        "character": {"xp": 0, "level": 1},
        "known_npcs": [],
        "known_locations": [{"name": "Test City"}],
        "clocks": [],
        "consequence_tracker": [],
        "campaign_arcs": [],
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    for key, val in overrides.items():
        if "." in key:
            parts = key.split(".")
            target = state
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = val
        else:
            state[key] = val
    return state


# ---------------------------------------------------------------------------
# Tests — expand_action
# ---------------------------------------------------------------------------

def test_expand_travel_has_world_tick_chain():
    """Travel expansion declares world-tick as a post-chain."""
    state = _make_state()
    result = expand_action("travel", state)
    chains = result["declared_chains"]
    wt = [c for c in chains if c["follow_up"] == "world-tick"]
    return len(wt) == 1 and wt[0]["status"] == "will_fire"


def test_expand_attack_has_conditional_treasure():
    """Attack expansion declares treasure as conditional post-chain."""
    state = _make_state()
    result = expand_action("attack", state)
    chains = result["declared_chains"]
    tr = [c for c in chains if c["follow_up"] == "treasure"]
    return len(tr) == 1 and tr[0]["status"] == "conditional"


def test_expand_no_chains_for_roll():
    """Roll has no pre-commands or post-chains."""
    state = _make_state()
    result = expand_action("roll", state)
    return (len(result["pre_commands"]) == 0 and
            len(result["declared_chains"]) == 0)


def test_expand_reaction_roll_prepends_generate_npc():
    """reaction-roll prepends generate-npc when NPC is unknown."""
    state = _make_state()
    state["current_scene"]["pending_npc_name"] = "Stranger"
    state["known_npcs"] = []  # Stranger not known
    result = expand_action("reaction-roll", state)
    pre = result["pre_commands"]
    return len(pre) == 1 and pre[0]["command"] == "generate-npc"


def test_expand_reaction_roll_no_prepend_when_known():
    """reaction-roll does NOT prepend generate-npc when NPC is known."""
    state = _make_state()
    state["current_scene"]["pending_npc_name"] = "Stranger"
    state["known_npcs"] = [{"name": "Stranger"}]
    result = expand_action("reaction-roll", state)
    return len(result["pre_commands"]) == 0


def test_expand_generate_scene_advisory_when_known():
    """generate-scene expansion includes advisory when location is known."""
    state = _make_state()
    # current_scene.location = "Test City" which is in known_locations
    result = expand_action("generate-scene", state)
    return len(result["advisories"]) == 1


def test_expand_generate_scene_no_advisory_when_unknown():
    """generate-scene expansion has no advisory when location is unknown."""
    state = _make_state()
    state["current_scene"]["location"] = "Unknown Place"
    result = expand_action("generate-scene", state)
    return len(result["advisories"]) == 0


def test_expand_arithmetic_trace():
    """expand_action produces a non-empty arithmetic trace."""
    state = _make_state()
    result = expand_action("travel", state)
    return "travel" in result["arithmetic_trace"] and "world-tick" in result["arithmetic_trace"]


# ---------------------------------------------------------------------------
# Tests — get_post_chains
# ---------------------------------------------------------------------------

def test_post_chains_travel_always_fires():
    """Travel post-chain (world-tick) fires regardless of result."""
    result = get_post_chains("travel", {"days": 5, "supplies_remaining": 3})
    wt = [c for c in result if c["command"] == "world-tick"]
    return len(wt) == 1 and wt[0]["args"].get("days") == 5


def test_post_chains_travel_args_from_result():
    """Travel post-chain resolves days from travel result."""
    result = get_post_chains("travel", {"days": 3})
    wt = [c for c in result if c["command"] == "world-tick"]
    return len(wt) == 1 and wt[0]["args"]["days"] == 3


def test_post_chains_attack_target_down():
    """Attack post-chain fires treasure when target_down=true."""
    result = get_post_chains("attack", {"target_down": True, "damage": 8})
    tr = [c for c in result if c["command"] == "treasure"]
    return len(tr) == 1


def test_post_chains_attack_target_alive():
    """Attack post-chain does NOT fire treasure when target_down=false."""
    result = get_post_chains("attack", {"target_down": False, "damage": 3})
    tr = [c for c in result if c["command"] == "treasure"]
    return len(tr) == 0


def test_post_chains_world_tick_chains_check_triggers():
    """World-tick post-chain fires check-triggers."""
    result = get_post_chains("world-tick", {"days_advanced": 3, "clock_updates": []})
    ct = [c for c in result if c["command"] == "check-triggers"]
    return len(ct) == 1


def test_post_chains_unknown_command_empty():
    """Unknown command returns empty post-chains."""
    result = get_post_chains("nonexistent", {})
    return len(result) == 0


# ---------------------------------------------------------------------------
# Tests — create_state_snapshot
# ---------------------------------------------------------------------------

def test_snapshot_captures_day():
    """Snapshot captures current_day."""
    state = _make_state(current_day=5)
    snap = create_state_snapshot(state)
    return snap["current_day"] == 5


def test_snapshot_captures_location():
    """Snapshot captures current_scene.location."""
    state = _make_state()
    state["current_scene"]["location"] = "Penn Station"
    snap = create_state_snapshot(state)
    return snap["current_scene.location"] == "Penn Station"


def test_snapshot_captures_xp():
    """Snapshot captures character XP and level."""
    state = _make_state()
    state["character"]["xp"] = 5
    state["character"]["level"] = 2
    snap = create_state_snapshot(state)
    return snap["character.xp"] == 5 and snap["character.level"] == 2


# ---------------------------------------------------------------------------
# Tests — check_post_resolution
# ---------------------------------------------------------------------------

def test_post_resolution_day_change():
    """Day advancement suggests world-tick."""
    pre = create_state_snapshot(_make_state(current_day=1))
    post = _make_state(current_day=4)
    result = check_post_resolution(pre, post)
    wt = [c for c in result["commands_to_fire"] if c["command"] == "world-tick"]
    return len(wt) == 1 and wt[0]["args"]["days"] == 3


def test_post_resolution_no_change():
    """No state change produces no suggestions."""
    state = _make_state()
    pre = create_state_snapshot(state)
    result = check_post_resolution(pre, state)
    return len(result["commands_to_fire"]) == 0 and len(result["deltas"]) == 0


def test_post_resolution_location_change_unknown():
    """Location change to unknown area suggests generate-scene."""
    pre = create_state_snapshot(_make_state())
    post = _make_state()
    post["current_scene"]["location"] = "Unknown Ruins"
    result = check_post_resolution(pre, post)
    gs = [c for c in result["commands_to_fire"] if c["command"] == "generate-scene"]
    return len(gs) == 1


def test_post_resolution_location_change_known():
    """Location change to known area does NOT suggest generate-scene."""
    pre = create_state_snapshot(_make_state())
    post = _make_state()
    post["current_scene"]["location"] = "Test City"  # already in known_locations
    result = check_post_resolution(pre, post)
    gs = [c for c in result["commands_to_fire"] if c["command"] == "generate-scene"]
    return len(gs) == 0


def test_post_resolution_combat_end():
    """Combat ending suggests treasure check."""
    state_pre = _make_state()
    state_pre["combat_state"]["active"] = True
    pre = create_state_snapshot(state_pre)
    post = _make_state()
    post["combat_state"]["active"] = False
    result = check_post_resolution(pre, post)
    tr = [c for c in result["commands_to_fire"] if c["command"] == "treasure"]
    return len(tr) == 1


def test_post_resolution_xp_level_up():
    """XP crossing level threshold suggests level-up."""
    state_pre = _make_state()
    state_pre["character"]["xp"] = 2
    state_pre["character"]["level"] = 1
    pre = create_state_snapshot(state_pre)
    post = _make_state()
    post["character"]["xp"] = 3  # Level 2 threshold
    post["character"]["level"] = 1
    result = check_post_resolution(pre, post)
    lu = [c for c in result["commands_to_fire"] if c["command"] == "level-up"]
    return len(lu) == 1


def test_post_resolution_deduplication():
    """Already-executed commands are not suggested again."""
    pre = create_state_snapshot(_make_state(current_day=1))
    post = _make_state(current_day=4)
    result = check_post_resolution(pre, post, already_executed={"world-tick"})
    wt = [c for c in result["commands_to_fire"] if c["command"] == "world-tick"]
    return len(wt) == 0


def test_post_resolution_high_threat_encounter():
    """Location change to high-threat area suggests encounter."""
    pre = create_state_snapshot(_make_state())
    post = _make_state()
    post["current_scene"]["location"] = "Dangerous Zone"
    post["current_scene"]["threat_level"] = 3
    result = check_post_resolution(pre, post)
    enc = [c for c in result["commands_to_fire"] if c["command"] == "encounter"]
    return len(enc) == 1


# ---------------------------------------------------------------------------
# Tests — get_all_chain_rules (introspection)
# ---------------------------------------------------------------------------

def test_chain_rules_introspection():
    """get_all_chain_rules returns serializable data."""
    rules = get_all_chain_rules()
    return ("post_chains" in rules and "pre_commands" in rules and
            "travel" in rules["post_chains"])


# ---------------------------------------------------------------------------
# Tests — CLI integration
# ---------------------------------------------------------------------------

def test_cli_expand_action():
    """expand-action CLI runs and returns valid JSON."""
    result = subprocess.run(
        [sys.executable, _CLI_PATH, "expand-action", "--action", "travel", "--seed", "42"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"  CLI error: {result.stderr}")
        return False
    try:
        output = json.loads(result.stdout)
        return "declared_chains" in output and output.get("primary") == "travel"
    except json.JSONDecodeError:
        return False


def test_cli_state_snapshot():
    """state-snapshot CLI runs and returns valid JSON."""
    result = subprocess.run(
        [sys.executable, _CLI_PATH, "state-snapshot", "--seed", "42"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"  CLI error: {result.stderr}")
        return False
    try:
        output = json.loads(result.stdout)
        return "current_day" in output
    except json.JSONDecodeError:
        return False


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # expand_action
    ("Travel has world-tick chain", test_expand_travel_has_world_tick_chain),
    ("Attack has conditional treasure", test_expand_attack_has_conditional_treasure),
    ("Roll has no chains", test_expand_no_chains_for_roll),
    ("Reaction-roll prepends generate-npc (unknown)", test_expand_reaction_roll_prepends_generate_npc),
    ("Reaction-roll no prepend (known)", test_expand_reaction_roll_no_prepend_when_known),
    ("Generate-scene advisory (known)", test_expand_generate_scene_advisory_when_known),
    ("Generate-scene no advisory (unknown)", test_expand_generate_scene_no_advisory_when_unknown),
    ("Expand arithmetic trace", test_expand_arithmetic_trace),
    # get_post_chains
    ("Travel always fires world-tick", test_post_chains_travel_always_fires),
    ("Travel args from result", test_post_chains_travel_args_from_result),
    ("Attack target_down fires treasure", test_post_chains_attack_target_down),
    ("Attack target_alive no treasure", test_post_chains_attack_target_alive),
    ("World-tick chains check-triggers", test_post_chains_world_tick_chains_check_triggers),
    ("Unknown command empty chains", test_post_chains_unknown_command_empty),
    # create_state_snapshot
    ("Snapshot captures day", test_snapshot_captures_day),
    ("Snapshot captures location", test_snapshot_captures_location),
    ("Snapshot captures XP", test_snapshot_captures_xp),
    # check_post_resolution
    ("Day change suggests world-tick", test_post_resolution_day_change),
    ("No change no suggestions", test_post_resolution_no_change),
    ("Location change (unknown) suggests generate-scene", test_post_resolution_location_change_unknown),
    ("Location change (known) no generate-scene", test_post_resolution_location_change_known),
    ("Combat end suggests treasure", test_post_resolution_combat_end),
    ("XP threshold suggests level-up", test_post_resolution_xp_level_up),
    ("Deduplication filters already-executed", test_post_resolution_deduplication),
    ("High threat encounter on location change", test_post_resolution_high_threat_encounter),
    # Introspection
    ("Chain rules introspection", test_chain_rules_introspection),
    # CLI integration
    ("CLI expand-action", test_cli_expand_action),
    ("CLI state-snapshot", test_cli_state_snapshot),
]


def run_test():
    """Entry point for run_all_tests.py. Returns True if all pass."""
    passed = 0
    failed = 0
    for name, fn in ALL_TESTS:
        try:
            result = fn()
            if result:
                passed += 1
                print(f"  [PASS] {name}")
            else:
                failed += 1
                print(f"  [FAIL] {name}")
        except Exception as e:
            failed += 1
            print(f"  [ERR]  {name}: {e}")

    print(f"\n  Chain registry tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
