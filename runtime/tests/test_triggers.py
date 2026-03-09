"""
Test suite for the check-triggers command (triggers.py).

Covers:
  - Live state produces valid output structure
  - Clock portent detection (missed portents at/below current)
  - Consequence timer expiration
  - Campaign arc beat evaluation (clock-based and free-text)
  - Proactive suggestions (threat-level encounter, faction-turn due)
  - Edge cases: empty state, no clocks, no arcs
  - CLI integration: check-triggers runs without error
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

from triggers import (
    check_all_triggers,
    check_clock_portents,
    check_arc_beats,
    get_clock_status,
    suggest_proactive_commands,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'state.json'
)

_CLI_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'emergence_cli.py'
)


def _load_state():
    with open(_STATE_PATH) as f:
        return json.load(f)


def _make_clock(name="Test Clock", current=0, max_val=6, status="active",
                portents=None, clock_id="clock_test"):
    return {
        "id": clock_id,
        "name": name,
        "current": current,
        "max": max_val,
        "status": status,
        "history": [],
        "portents": portents or [],
    }


def _make_consequence(csq_id="csq_1_100", days_remaining=0, status="pending"):
    return {
        "id": csq_id,
        "trigger_condition": "test_trigger",
        "timer_days": 3,
        "days_remaining": days_remaining,
        "description": "Test consequence fires",
        "source_turn": 1,
        "status": status,
        "resolution": None,
    }


def _make_arc(name="Test Arc", beats=None, status="active", arc_id="arc_test"):
    return {
        "id": arc_id,
        "name": name,
        "status": status,
        "description": "Test arc",
        "beats": beats or [],
    }


# ---------------------------------------------------------------------------
# Tests — Live state
# ---------------------------------------------------------------------------

def test_live_state_check_triggers():
    """check_all_triggers on live state.json produces valid structure."""
    state = _load_state()
    result = check_all_triggers(state)

    required_keys = [
        "current_day", "missed_portents", "triggered_consequences",
        "pending_consequences", "arc_beats", "proactive_suggestions",
        "clock_status", "commands_to_fire", "arithmetic_trace",
    ]
    for key in required_keys:
        if key not in result:
            print(f"  Missing key in result: {key}")
            return False
    return True


def test_live_state_arithmetic_trace():
    """arithmetic_trace is a non-empty string."""
    state = _load_state()
    result = check_all_triggers(state)
    trace = result.get("arithmetic_trace", "")
    return isinstance(trace, str) and len(trace) > 0


# ---------------------------------------------------------------------------
# Tests — Clock portents
# ---------------------------------------------------------------------------

def test_missed_portent_detected():
    """Unfired portent at threshold <= current is detected."""
    clocks = [_make_clock(current=3, portents=[
        {"at": 2, "event": "Early warning", "mechanical": "test", "fired": False},
        {"at": 5, "event": "Late warning", "mechanical": "test", "fired": False},
    ])]
    missed = check_clock_portents(clocks)
    return len(missed) == 1 and missed[0]["portent"] == "Early warning"


def test_fired_portent_not_detected():
    """Already-fired portent is not reported."""
    clocks = [_make_clock(current=3, portents=[
        {"at": 2, "event": "Already fired", "mechanical": "test", "fired": True},
    ])]
    missed = check_clock_portents(clocks)
    return len(missed) == 0


def test_inactive_clock_skipped():
    """Completed/paused clocks are skipped."""
    clocks = [_make_clock(current=3, status="completed", portents=[
        {"at": 2, "event": "Should skip", "mechanical": "test", "fired": False},
    ])]
    missed = check_clock_portents(clocks)
    return len(missed) == 0


def test_portent_at_exact_threshold():
    """Portent at exactly current value is detected."""
    clocks = [_make_clock(current=2, portents=[
        {"at": 2, "event": "Exact threshold", "mechanical": "test", "fired": False},
    ])]
    missed = check_clock_portents(clocks)
    return len(missed) == 1


def test_multiple_missed_portents():
    """Multiple missed portents on same clock are all detected."""
    clocks = [_make_clock(current=5, portents=[
        {"at": 2, "event": "First", "mechanical": "a", "fired": False},
        {"at": 3, "event": "Second", "mechanical": "b", "fired": False},
        {"at": 4, "event": "Third", "mechanical": "c", "fired": False},
        {"at": 6, "event": "Not yet", "mechanical": "d", "fired": False},
    ])]
    missed = check_clock_portents(clocks)
    return len(missed) == 3


# ---------------------------------------------------------------------------
# Tests — Clock status
# ---------------------------------------------------------------------------

def test_clock_status_next_portent():
    """get_clock_status returns the next unfired portent."""
    clocks = [_make_clock(current=1, portents=[
        {"at": 1, "event": "Past", "fired": True},
        {"at": 3, "event": "Next", "fired": False},
        {"at": 5, "event": "Later", "fired": False},
    ])]
    status = get_clock_status(clocks)
    return (len(status) == 1 and
            status[0]["next_portent"]["at"] == 3 and
            status[0]["next_portent"]["event"] == "Next")


def test_clock_status_no_portents():
    """Clock with all portents fired has next_portent=None."""
    clocks = [_make_clock(current=3, portents=[
        {"at": 2, "event": "Done", "fired": True},
    ])]
    status = get_clock_status(clocks)
    return len(status) == 1 and status[0]["next_portent"] is None


# ---------------------------------------------------------------------------
# Tests — Consequences
# ---------------------------------------------------------------------------

def test_expired_consequence_triggered():
    """Consequence with days_remaining <= 0 appears in triggered list."""
    state = {
        "current_day": 5,
        "clocks": [],
        "consequence_tracker": [_make_consequence(days_remaining=0)],
        "campaign_arcs": [],
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    result = check_all_triggers(state)
    return len(result["triggered_consequences"]) == 1


def test_pending_consequence_not_triggered():
    """Consequence with days_remaining > 1 stays pending."""
    state = {
        "current_day": 5,
        "clocks": [],
        "consequence_tracker": [_make_consequence(days_remaining=5)],
        "campaign_arcs": [],
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    result = check_all_triggers(state)
    return (len(result["triggered_consequences"]) == 0 and
            len(result["pending_consequences"]) == 1)


def test_resolved_consequence_ignored():
    """Resolved consequences don't appear in triggered or pending."""
    state = {
        "current_day": 5,
        "clocks": [],
        "consequence_tracker": [_make_consequence(days_remaining=0, status="resolved")],
        "campaign_arcs": [],
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    result = check_all_triggers(state)
    return (len(result["triggered_consequences"]) == 0 and
            len(result["pending_consequences"]) == 0)


# ---------------------------------------------------------------------------
# Tests — Campaign arc beats
# ---------------------------------------------------------------------------

def test_clock_based_beat_triggered():
    """Arc beat with clock condition met is triggered."""
    clocks = [_make_clock(name="Food Crisis", current=4)]
    arcs = [_make_arc(beats=[{
        "beat_name": "Famine begins",
        "trigger_condition": "Food Crisis clock hits 4",
        "status": "pending",
        "payoff_description": "Starvation starts",
    }])]
    result = check_arc_beats(arcs, clocks)
    return len(result["triggered"]) == 1


def test_clock_based_beat_not_met():
    """Arc beat with clock condition not met stays pending."""
    clocks = [_make_clock(name="Food Crisis", current=2)]
    arcs = [_make_arc(beats=[{
        "beat_name": "Famine begins",
        "trigger_condition": "Food Crisis clock hits 4",
        "status": "pending",
        "payoff_description": "Starvation starts",
    }])]
    result = check_arc_beats(arcs, clocks)
    return (len(result["triggered"]) == 0 and
            len(result["pending_mechanical"]) == 1)


def test_freetext_beat_requires_judgment():
    """Arc beat with non-clock condition requires GM judgment."""
    clocks = []
    arcs = [_make_arc(beats=[{
        "beat_name": "Player decision",
        "trigger_condition": "Player decides to locate brother",
        "status": "pending",
        "payoff_description": "Brother found",
    }])]
    result = check_arc_beats(arcs, clocks)
    return (len(result["requires_gm_judgment"]) == 1 and
            len(result["triggered"]) == 0)


def test_completed_beat_skipped():
    """Already completed beats are not evaluated."""
    clocks = [_make_clock(name="Food Crisis", current=4)]
    arcs = [_make_arc(beats=[{
        "beat_name": "Done",
        "trigger_condition": "Food Crisis clock hits 2",
        "status": "completed",
        "payoff_description": "Already done",
    }])]
    result = check_arc_beats(arcs, clocks)
    return (len(result["triggered"]) == 0 and
            len(result["pending_mechanical"]) == 0 and
            len(result["requires_gm_judgment"]) == 0)


def test_clock_reaches_variant():
    """'reaches' variant of clock trigger pattern is recognized."""
    clocks = [_make_clock(name="Borough Divergence", current=3)]
    arcs = [_make_arc(beats=[{
        "beat_name": "Split",
        "trigger_condition": "Borough Divergence clock reaches 3",
        "status": "pending",
        "payoff_description": "Boroughs split",
    }])]
    result = check_arc_beats(arcs, clocks)
    return len(result["triggered"]) == 1


# ---------------------------------------------------------------------------
# Tests — Proactive suggestions
# ---------------------------------------------------------------------------

def test_high_threat_encounter_suggested():
    """Threat level >= 2 triggers encounter suggestion."""
    state = {
        "current_day": 1,
        "current_scene": {"threat_level": 3, "scene_type": "exploration", "region": "manhattan"},
        "meta": {"session_number": 1},
        "human_factions": [],
        "clocks": [],
    }
    suggestions = suggest_proactive_commands(state)
    encounter_sugs = [s for s in suggestions if s["command"] == "encounter"]
    return len(encounter_sugs) == 1


def test_low_threat_no_encounter():
    """Threat level < 2 does not trigger encounter suggestion."""
    state = {
        "current_day": 1,
        "current_scene": {"threat_level": 1},
        "meta": {"session_number": 1},
        "human_factions": [],
        "clocks": [],
    }
    suggestions = suggest_proactive_commands(state)
    encounter_sugs = [s for s in suggestions if s["command"] == "encounter"]
    return len(encounter_sugs) == 0


def test_faction_turn_suggested_after_7_days():
    """Faction turn is suggested when 7+ days have passed."""
    state = {
        "current_day": 10,
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [{"id": "f1", "turn_history": [{"day": 1}]}],
        "clocks": [],
    }
    suggestions = suggest_proactive_commands(state)
    faction_sugs = [s for s in suggestions if s["command"] == "faction-turn"]
    return len(faction_sugs) == 1 and faction_sugs[0]["priority"] == "high"


def test_no_faction_turn_early():
    """Faction turn not suggested within 7 days of last turn."""
    state = {
        "current_day": 5,
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [{"id": "f1", "turn_history": [{"day": 1}]}],
        "clocks": [],
    }
    suggestions = suggest_proactive_commands(state)
    faction_sugs = [s for s in suggestions if s["command"] == "faction-turn"]
    return len(faction_sugs) == 0


# ---------------------------------------------------------------------------
# Tests — Edge cases
# ---------------------------------------------------------------------------

def test_empty_state():
    """Empty state (no clocks, no consequences, no arcs) produces valid output."""
    state = {
        "current_day": 1,
        "clocks": [],
        "consequence_tracker": [],
        "campaign_arcs": [],
        "current_scene": {"threat_level": 0},
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    result = check_all_triggers(state)
    return (len(result["commands_to_fire"]) == 0 and
            len(result["missed_portents"]) == 0 and
            len(result["triggered_consequences"]) == 0)


def test_commands_to_fire_aggregation():
    """commands_to_fire aggregates all trigger sources."""
    state = {
        "current_day": 10,
        "clocks": [_make_clock(current=3, portents=[
            {"at": 2, "event": "Missed", "mechanical": "test", "fired": False},
        ])],
        "consequence_tracker": [_make_consequence(days_remaining=0)],
        "campaign_arcs": [],
        "current_scene": {"threat_level": 3, "scene_type": "exploration", "region": "manhattan"},
        "meta": {"session_number": 1},
        "human_factions": [],
    }
    result = check_all_triggers(state)
    sources = {cmd["source"] for cmd in result["commands_to_fire"]}
    return "clock_portent" in sources and "consequence" in sources and "proactive" in sources


# ---------------------------------------------------------------------------
# Tests — CLI integration
# ---------------------------------------------------------------------------

def test_cli_check_triggers_runs():
    """check-triggers CLI command runs and returns valid JSON."""
    result = subprocess.run(
        [sys.executable, _CLI_PATH, "check-triggers", "--seed", "42"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"  CLI error: {result.stderr}")
        return False
    try:
        output = json.loads(result.stdout)
        return "commands_to_fire" in output and "seed" in output
    except json.JSONDecodeError:
        print(f"  Invalid JSON output: {result.stdout[:200]}")
        return False


def test_cli_day_override():
    """--current-day override changes the evaluation day."""
    result = subprocess.run(
        [sys.executable, _CLI_PATH, "check-triggers", "--current-day", "100", "--seed", "42"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"  CLI error: {result.stderr}")
        return False
    try:
        output = json.loads(result.stdout)
        return output.get("current_day") == 100
    except json.JSONDecodeError:
        return False


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # Live state
    ("Live state check-triggers structure", test_live_state_check_triggers),
    ("Live state arithmetic trace", test_live_state_arithmetic_trace),
    # Clock portents
    ("Missed portent detected", test_missed_portent_detected),
    ("Fired portent not detected", test_fired_portent_not_detected),
    ("Inactive clock skipped", test_inactive_clock_skipped),
    ("Portent at exact threshold", test_portent_at_exact_threshold),
    ("Multiple missed portents", test_multiple_missed_portents),
    # Clock status
    ("Clock status next portent", test_clock_status_next_portent),
    ("Clock status no portents", test_clock_status_no_portents),
    # Consequences
    ("Expired consequence triggered", test_expired_consequence_triggered),
    ("Pending consequence not triggered", test_pending_consequence_not_triggered),
    ("Resolved consequence ignored", test_resolved_consequence_ignored),
    # Campaign arc beats
    ("Clock-based beat triggered", test_clock_based_beat_triggered),
    ("Clock-based beat not met", test_clock_based_beat_not_met),
    ("Free-text beat requires judgment", test_freetext_beat_requires_judgment),
    ("Completed beat skipped", test_completed_beat_skipped),
    ("Clock 'reaches' variant", test_clock_reaches_variant),
    # Proactive suggestions
    ("High threat encounter suggested", test_high_threat_encounter_suggested),
    ("Low threat no encounter", test_low_threat_no_encounter),
    ("Faction turn suggested after 7 days", test_faction_turn_suggested_after_7_days),
    ("No faction turn early", test_no_faction_turn_early),
    # Edge cases
    ("Empty state valid output", test_empty_state),
    ("Commands aggregation", test_commands_to_fire_aggregation),
    # CLI integration
    ("CLI check-triggers runs", test_cli_check_triggers_runs),
    ("CLI day override", test_cli_day_override),
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

    print(f"\n  Trigger tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
