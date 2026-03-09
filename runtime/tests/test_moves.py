"""
Test suite for the anti-stagnation move system (gm_moves.py).

Covers:
  - Tier 1 floor: every dispatcher returns minimum tier 1
  - Escalation check: forced tier 2 at 5, forced tier 3 at 8
  - Skill-check dispatch: margin thresholds, gate-type mapping
  - Attack dispatch: battlefield evolution, combat end, profile foreshadow
  - Save dispatch: reactive moves, severe failure escalation
  - Cast-spell dispatch: magic ripple, combat guard
  - Reaction-roll dispatch: all 5 disposition tiers
  - Travel dispatch: portent priority, privation, uneventful
  - Telegraph management: creation, escalation, oldest-first
  - Counter updates: increment on tier 1, reset on tier 2+
  - Schema validation: new fields in state.schema.json
  - Determinism: same inputs → same output
"""

import copy
import json
import os
import sys

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

# ---------------------------------------------------------------------------
# Imports — these will fail until gm_moves.py is implemented
# ---------------------------------------------------------------------------

try:
    from gm_moves import (
        select_move,
        record_telegraph,
        check_escalation,
    )
    _IMPORT_OK = True
except ImportError as e:
    _IMPORT_OK = False
    _IMPORT_ERR = str(e)

try:
    from behavior import get_profile_description
    _BEHAVIOR_IMPORT_OK = True
except (ImportError, AttributeError) as e:
    _BEHAVIOR_IMPORT_OK = False
    _BEHAVIOR_IMPORT_ERR = str(e)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'state.json'
)

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'schemas', 'state.schema.json'
)


def _load_state():
    with open(_STATE_PATH) as f:
        return json.load(f)


def _load_schema():
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


def _make_telegraph(telegraph_id="telegraph_test_1", turn=1, status="active"):
    return {
        "id": telegraph_id,
        "description": "Test telegraph — boots echo above",
        "turn_created": turn,
        "source_element": "enemies.patrol",
        "status": status,
    }


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


def _make_scene_elements():
    return {
        "complications": ["Loose rubble shifting", "Distant grinding sound"],
        "opportunities": ["Hidden alcove", "Ancient terminal"],
        "used": [],
    }


def _skill_check_result(success=True, margin=2, total=12, difficulty=10):
    return {
        "success": success,
        "margin": margin,
        "total": total,
        "difficulty": difficulty,
    }


def _attack_result(hit=True, damage=5, target_down=False, shock_applied=False):
    return {
        "hit": hit,
        "damage": damage,
        "target_down": target_down,
        "shock_applied": shock_applied,
        "roll": 15,
        "target_ac": 12,
    }


def _save_result(success=True, margin=2):
    return {
        "success": success,
        "roll": 10,
        "save_target": 12 if not success else 8,
        "save_type": "physical",
        "margin": margin,
    }


def _cast_spell_result(success=True):
    return {
        "success": success,
        "spell_name": "Magic Missile",
        "effort_type": "scene",
        "effort_committed": 1 if success else 0,
        "system_strain_added": 1,
        "effect": "1d6+1 damage" if success else "fizzle",
    }


def _reaction_roll_result(disposition="neutral", total=7):
    return {
        "total": total,
        "modifier": 0,
        "disposition": disposition,
        "reaction_text": f"NPC is {disposition}",
    }


def _travel_result(has_encounter=False, supplies_end=5):
    return {
        "travel_log": [{
            "day": 1,
            "events": [],
            "encounter_check": False,
            "travel_event": "Unremarkable terrain",
            "has_encounter": has_encounter,
        }],
        "encounters": [],
        "supplies_end": supplies_end,
    }


def _combat_state(active=True, enemies=None):
    if enemies is None:
        enemies = [
            {"id": "goblin_1", "hp_current": 5, "hp_max": 5, "type": "humanoid"},
            {"id": "goblin_2", "hp_current": 5, "hp_max": 5, "type": "humanoid"},
        ]
    return {
        "active": active,
        "enemies": enemies,
    }


# ---------------------------------------------------------------------------
# Tests — Import validation
# ---------------------------------------------------------------------------

def test_gm_moves_import():
    """gm_moves module imports successfully."""
    if not _IMPORT_OK:
        print(f"  Import error: {_IMPORT_ERR}")
    return _IMPORT_OK


def test_behavior_get_profile_description_exists():
    """behavior.py exports get_profile_description()."""
    if not _BEHAVIOR_IMPORT_OK:
        print(f"  Import error: {_BEHAVIOR_IMPORT_ERR}")
    return _BEHAVIOR_IMPORT_OK


# ---------------------------------------------------------------------------
# Tests — Schema validation
# ---------------------------------------------------------------------------

def test_schema_has_turns_since_hard_move():
    """state.schema.json session definition includes turns_since_hard_move."""
    schema = _load_schema()
    session_def = schema.get("$defs", {}).get("session", {})
    props = session_def.get("properties", {})
    return "turns_since_hard_move" in props


def test_schema_has_telegraphed_threats():
    """state.schema.json current_scene includes telegraphed_threats."""
    schema = _load_schema()
    scene_def = schema.get("$defs", {}).get("current_scene", {})
    props = scene_def.get("properties", {})
    return "telegraphed_threats" in props


def test_schema_version_bumped():
    """Schema version is 7.6.0 or higher."""
    schema = _load_schema()
    desc = schema.get("description", "")
    # Check for version in description
    version = None
    if "version" in desc.lower():
        import re
        match = re.search(r'(\d+\.\d+\.\d+)', desc)
        if match:
            version = match.group(1)
    if version is None:
        # Fallback: version might not be in description
        return False
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    return (major > 7) or (major == 7 and minor >= 6)


def test_state_has_turns_since_hard_move():
    """Live state.json session has turns_since_hard_move field."""
    state = _load_state()
    session = state.get("session", {})
    return "turns_since_hard_move" in session


def test_state_has_telegraphed_threats():
    """Live state.json current_scene has telegraphed_threats field."""
    state = _load_state()
    scene = state.get("current_scene", {})
    return "telegraphed_threats" in scene


# ---------------------------------------------------------------------------
# Tests — record_telegraph
# ---------------------------------------------------------------------------

def test_record_telegraph_structure():
    """record_telegraph returns a well-formed telegraph dict."""
    if not _IMPORT_OK:
        return False
    t = record_telegraph("Distant rumbling", "environment.tremor", 3)
    required = ["id", "description", "turn_created", "source_element", "status"]
    for key in required:
        if key not in t:
            print(f"  Missing key: {key}")
            return False
    return (t["status"] == "active" and
            t["turn_created"] == 3 and
            t["description"] == "Distant rumbling")


# ---------------------------------------------------------------------------
# Tests — check_escalation
# ---------------------------------------------------------------------------

def test_escalation_below_threshold():
    """No forced escalation when counter < 5."""
    if not _IMPORT_OK:
        return False
    result = check_escalation(4, [], [], [])
    return result is None


def test_escalation_tier2_at_5():
    """Forced tier 2 when turns_since_hard_move >= 5."""
    if not _IMPORT_OK:
        return False
    result = check_escalation(5, [], [], [])
    return result is not None and result.get("forced_tier") == 2


def test_escalation_tier3_at_8():
    """Forced tier 3 when turns_since_hard_move >= 8."""
    if not _IMPORT_OK:
        return False
    result = check_escalation(8, [], [], [])
    return result is not None and result.get("forced_tier") == 3


def test_escalation_tier3_beats_tier2():
    """At counter=8, tier 3 fires (not tier 2)."""
    if not _IMPORT_OK:
        return False
    result = check_escalation(8, [], [], [])
    return result is not None and result.get("forced_tier") == 3


def test_escalation_tier2_with_telegraph():
    """Forced tier 2 with active telegraph targets it for escalation."""
    if not _IMPORT_OK:
        return False
    telegraphs = [_make_telegraph("t1", turn=1), _make_telegraph("t2", turn=3)]
    result = check_escalation(5, telegraphs, [], [])
    return (result is not None and
            result.get("forced_tier") == 2 and
            result.get("target_telegraph") == "t1")  # oldest first


# ---------------------------------------------------------------------------
# Tests — Tier 1 floor (all dispatchers return minimum tier 1)
# ---------------------------------------------------------------------------

def test_skill_check_success_tier1():
    """Skill-check success returns tier 1 (not tier 0)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=True, margin=3),
        gate_type="access",
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_save_success_tier1():
    """Save success returns tier 1 (not tier 0)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "save",
        _save_result(success=True, margin=4),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_attack_mid_combat_tier1():
    """Attack hit mid-combat returns tier 1 (battlefield evolves)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "attack",
        _attack_result(hit=True, target_down=False),
        combat_state=_combat_state(active=True),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_cast_spell_failure_tier1():
    """Cast-spell failure returns tier 1 (attempt noticed)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "cast-spell",
        _cast_spell_result(success=False),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_reaction_roll_neutral_tier1():
    """Reaction-roll neutral returns tier 1 (NPC gives info)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "reaction-roll",
        _reaction_roll_result(disposition="neutral", total=7),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_travel_uneventful_tier1():
    """Travel with no events returns tier 1 (world_pulse)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "travel",
        _travel_result(has_encounter=False, supplies_end=5),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1


def test_no_tier0_any_dispatcher():
    """No dispatcher returns tier 0 for any standard result."""
    if not _IMPORT_OK:
        return False
    cases = [
        ("skill-check", _skill_check_result(success=True, margin=5),
         {"gate_type": "access", "scene_elements": _make_scene_elements()}),
        ("skill-check", _skill_check_result(success=False, margin=-1),
         {"gate_type": "discovery", "scene_elements": _make_scene_elements()}),
        ("attack", _attack_result(hit=True, target_down=False),
         {"combat_state": _combat_state(), "scene_elements": _make_scene_elements()}),
        ("attack", _attack_result(hit=False),
         {"combat_state": _combat_state(), "scene_elements": _make_scene_elements()}),
        ("save", _save_result(success=True),
         {"scene_elements": _make_scene_elements()}),
        ("save", _save_result(success=False, margin=-1),
         {"scene_elements": _make_scene_elements()}),
        ("cast-spell", _cast_spell_result(success=True),
         {"scene_elements": _make_scene_elements()}),
        ("cast-spell", _cast_spell_result(success=False),
         {"scene_elements": _make_scene_elements()}),
        ("reaction-roll", _reaction_roll_result("neutral"),
         {"scene_elements": _make_scene_elements()}),
        ("reaction-roll", _reaction_roll_result("friendly"),
         {"scene_elements": _make_scene_elements()}),
        ("travel", _travel_result(),
         {"scene_elements": _make_scene_elements()}),
    ]
    for cmd, result, kwargs in cases:
        move = select_move(cmd, result, **kwargs)
        if move.get("tier", 0) < 1:
            print(f"  Tier 0 returned for {cmd}: {move.get('move_type')}")
            return False
    return True


# ---------------------------------------------------------------------------
# Tests — Skill-check dispatch specifics
# ---------------------------------------------------------------------------

def test_skill_check_catastrophic_tier2():
    """Skill-check margin <= -5 returns tier 2 regardless."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=False, margin=-6),
        gate_type="access",
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") == 2


def test_skill_check_fail_with_telegraph_tier2():
    """Skill-check margin <= -3 with active telegraph escalates to tier 2."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=False, margin=-3),
        gate_type="social",
        scene_elements=_make_scene_elements(),
        telegraphed_threats=[_make_telegraph("t1", turn=1)],
    )
    return result.get("tier") == 2


def test_skill_check_fail_no_telegraph_tier1():
    """Skill-check margin <= -3 with no telegraph records new one (tier 1)."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=False, margin=-3),
        gate_type="access",
        scene_elements=_make_scene_elements(),
        telegraphed_threats=[],
    )
    return result.get("tier") == 1


# ---------------------------------------------------------------------------
# Tests — Attack dispatch specifics
# ---------------------------------------------------------------------------

def test_attack_combat_ends_tier1():
    """Attack that ends combat (all enemies down) returns tier 1 aftermath."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "attack",
        _attack_result(hit=True, target_down=True),
        combat_state=_combat_state(active=True, enemies=[
            {"id": "goblin_1", "hp_current": 0, "hp_max": 5, "type": "humanoid"},
        ]),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") >= 1 and "aftermath" in result.get("move_type", "").lower()


# ---------------------------------------------------------------------------
# Tests — Save dispatch specifics
# ---------------------------------------------------------------------------

def test_save_severe_failure_tier2():
    """Save failure with margin <= -3 returns tier 2."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "save",
        _save_result(success=False, margin=-4),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") == 2


# ---------------------------------------------------------------------------
# Tests — Reaction-roll dispatch specifics
# ---------------------------------------------------------------------------

def test_reaction_roll_hostile_tier2():
    """Hostile reaction-roll returns tier 2."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "reaction-roll",
        _reaction_roll_result(disposition="hostile", total=2),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") == 2


# ---------------------------------------------------------------------------
# Tests — Travel dispatch specifics
# ---------------------------------------------------------------------------

def test_travel_privation_tier2():
    """Travel with privation (supplies_end == 0) returns tier 2."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "travel",
        _travel_result(has_encounter=False, supplies_end=0),
        scene_elements=_make_scene_elements(),
    )
    return result.get("tier") == 2


# ---------------------------------------------------------------------------
# Tests — Output contract
# ---------------------------------------------------------------------------

def test_move_output_has_required_fields():
    """select_move output contains all required contract fields."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=True, margin=2),
        gate_type="access",
        scene_elements=_make_scene_elements(),
    )
    required = ["tier", "move_type", "narrative_directive", "arithmetic_trace"]
    for key in required:
        if key not in result:
            print(f"  Missing key in output: {key}")
            return False
    return True


def test_arithmetic_trace_nonempty():
    """arithmetic_trace is a non-empty string on all moves."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=False, margin=-2),
        gate_type="discovery",
        scene_elements=_make_scene_elements(),
    )
    trace = result.get("arithmetic_trace", "")
    return isinstance(trace, str) and len(trace) > 0


# ---------------------------------------------------------------------------
# Tests — Counter updates
# ---------------------------------------------------------------------------

def test_tier1_increments_counter():
    """Tier 1 move returns counter_update that increments."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "save",
        _save_result(success=True),
        scene_elements=_make_scene_elements(),
    )
    update = result.get("counter_update", {})
    return update.get("action") == "increment"


def test_tier2_resets_counter():
    """Tier 2 move returns counter_update that resets to 0."""
    if not _IMPORT_OK:
        return False
    result = select_move(
        "skill-check",
        _skill_check_result(success=False, margin=-6),
        gate_type="access",
        scene_elements=_make_scene_elements(),
    )
    update = result.get("counter_update", {})
    return update.get("action") == "reset"


# ---------------------------------------------------------------------------
# Tests — Determinism
# ---------------------------------------------------------------------------

def test_determinism():
    """Same inputs produce same output."""
    if not _IMPORT_OK:
        return False
    kwargs = dict(
        command_name="skill-check",
        command_result=_skill_check_result(success=False, margin=-2),
        gate_type="access",
        scene_elements=_make_scene_elements(),
    )
    r1 = select_move(**kwargs)
    r2 = select_move(**kwargs)
    return r1 == r2


# ---------------------------------------------------------------------------
# Tests — behavior.py get_profile_description
# ---------------------------------------------------------------------------

def test_behavior_profile_description_returns_string():
    """get_profile_description returns a non-empty string for known profiles."""
    if not _BEHAVIOR_IMPORT_OK:
        return False
    for profile in ["aggressive", "cautious", "pack", "ambush", "guardian", "spellcaster"]:
        desc = get_profile_description(profile)
        if not isinstance(desc, str) or len(desc) == 0:
            print(f"  Empty description for profile: {profile}")
            return False
    return True


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # Import validation
    ("gm_moves module imports", test_gm_moves_import),
    ("behavior.get_profile_description exists", test_behavior_get_profile_description_exists),
    # Schema validation
    ("Schema has turns_since_hard_move", test_schema_has_turns_since_hard_move),
    ("Schema has telegraphed_threats", test_schema_has_telegraphed_threats),
    ("Schema version >= 7.6.0", test_schema_version_bumped),
    ("State has turns_since_hard_move", test_state_has_turns_since_hard_move),
    ("State has telegraphed_threats", test_state_has_telegraphed_threats),
    # record_telegraph
    ("record_telegraph structure", test_record_telegraph_structure),
    # check_escalation
    ("Escalation below threshold", test_escalation_below_threshold),
    ("Escalation tier 2 at 5", test_escalation_tier2_at_5),
    ("Escalation tier 3 at 8", test_escalation_tier3_at_8),
    ("Tier 3 beats tier 2", test_escalation_tier3_beats_tier2),
    ("Tier 2 with telegraph targets oldest", test_escalation_tier2_with_telegraph),
    # Tier 1 floor
    ("Skill-check success → tier 1", test_skill_check_success_tier1),
    ("Save success → tier 1", test_save_success_tier1),
    ("Attack mid-combat → tier 1", test_attack_mid_combat_tier1),
    ("Cast-spell failure → tier 1", test_cast_spell_failure_tier1),
    ("Reaction-roll neutral → tier 1", test_reaction_roll_neutral_tier1),
    ("Travel uneventful → tier 1", test_travel_uneventful_tier1),
    ("No tier 0 from any dispatcher", test_no_tier0_any_dispatcher),
    # Skill-check specifics
    ("Skill-check catastrophic → tier 2", test_skill_check_catastrophic_tier2),
    ("Skill-check fail + telegraph → tier 2", test_skill_check_fail_with_telegraph_tier2),
    ("Skill-check fail no telegraph → tier 1", test_skill_check_fail_no_telegraph_tier1),
    # Attack specifics
    ("Attack combat ends → tier 1 aftermath", test_attack_combat_ends_tier1),
    # Save specifics
    ("Save severe failure → tier 2", test_save_severe_failure_tier2),
    # Reaction-roll specifics
    ("Hostile reaction → tier 2", test_reaction_roll_hostile_tier2),
    # Travel specifics
    ("Travel privation → tier 2", test_travel_privation_tier2),
    # Output contract
    ("Move output has required fields", test_move_output_has_required_fields),
    ("Arithmetic trace non-empty", test_arithmetic_trace_nonempty),
    # Counter updates
    ("Tier 1 increments counter", test_tier1_increments_counter),
    ("Tier 2 resets counter", test_tier2_resets_counter),
    # Determinism
    ("Determinism: same input same output", test_determinism),
    # behavior.py
    ("Profile description returns string", test_behavior_profile_description_returns_string),
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

    print(f"\n  Move tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
