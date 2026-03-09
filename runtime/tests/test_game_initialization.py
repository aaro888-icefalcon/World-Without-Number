"""
Game Initialization — Validation Test Suite

Tests that the initialize-game command produces valid, complete state.json
for all supported campaign types and character configurations.
"""

import sys
import os
import json
import random

# Path setup
_test_dir = os.path.dirname(os.path.abspath(__file__))
_runtime_dir = os.path.join(_test_dir, '..')
_scripts_dir = os.path.join(_runtime_dir, 'scripts')
sys.path.insert(0, _scripts_dir)
sys.path.insert(0, _runtime_dir)

_skills_dir = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills')
if os.path.isdir(_skills_dir):
    for _domain in os.listdir(_skills_dir):
        for _subdir in ['scripts', 'tables']:
            _p = os.path.join(_skills_dir, _domain, _subdir)
            if os.path.isdir(_p) and _p not in sys.path:
                sys.path.insert(0, _p)


def _load_schema():
    """Load state schema for validation."""
    schema_path = os.path.join(_runtime_dir, 'schemas', 'state.schema.json')
    with open(schema_path) as f:
        return json.load(f)


def _validate_state_structure(state, schema):
    """Check all required top-level keys are present and have correct types."""
    errors = []
    required = schema.get("required", [])
    for key in required:
        if key not in state:
            errors.append(f"Missing required key: {key}")
    return errors


def _validate_character(character):
    """Validate character has all required fields."""
    errors = []
    required_fields = ["name", "level", "class", "attributes", "hp",
                       "armor_class", "attack_bonus", "skills", "equipment",
                       "saving_throws", "system_strain"]
    for field in required_fields:
        if field not in character:
            errors.append(f"Character missing required field: {field}")

    if character.get("name") in (None, "", "Unnamed Hero"):
        errors.append("Character name should not be placeholder")

    attrs = character.get("attributes", {})
    for attr in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        val = attrs.get(attr)
        if val is None:
            errors.append(f"Missing attribute: {attr}")
        elif not (3 <= val <= 18):
            errors.append(f"Attribute {attr}={val} out of range [3,18]")

    if character.get("level") != 1:
        errors.append(f"New character should be level 1, got {character.get('level')}")

    hp = character.get("hp", {})
    if hp.get("current", 0) < 1 or hp.get("max", 0) < 1:
        errors.append(f"HP should be at least 1, got {hp}")

    saves = character.get("saving_throws", {})
    for save_type in ["physical", "evasion", "mental", "luck"]:
        if save_type not in saves:
            errors.append(f"Missing saving throw: {save_type}")

    return errors


def _validate_scene(scene):
    """Validate scene has all required fields."""
    errors = []
    for field in ["scene_id", "location", "region", "threat_level", "scene_type"]:
        if field not in scene:
            errors.append(f"Scene missing required field: {field}")
    return errors


def _validate_campaign(campaign):
    """Validate campaign metadata."""
    errors = []
    for field in ["name", "start_date", "current_day", "current_time", "current_location"]:
        if field not in campaign:
            errors.append(f"Campaign missing required field: {field}")
    return errors


def _validate_nyc_clocks(clocks):
    """Validate NYC campaign clocks are properly seeded."""
    errors = []
    if len(clocks) < 6:
        errors.append(f"NYC campaign should have at least 6 clocks, got {len(clocks)}")

    expected_names = {
        "Food Crisis", "Verdancy Western Front", "Pelegrinian Pressure",
        "Gallery Seal Degradation", "Manthva Succession", "Borough Divergence"
    }
    actual_names = {c.get("name") for c in clocks}
    missing = expected_names - actual_names
    if missing:
        errors.append(f"Missing NYC clocks: {missing}")

    for clock in clocks:
        if clock.get("current", -1) != 0:
            errors.append(f"Clock '{clock.get('name')}' should start at 0")
        if clock.get("max", 0) < 1:
            errors.append(f"Clock '{clock.get('name')}' has invalid max")
        if "portents" not in clock:
            errors.append(f"Clock '{clock.get('name')}' missing portents")

    return errors


def test_default_campaign_warrior():
    """Test: Default campaign with warrior class."""
    from initialize_game import initialize_game
    random.seed(42)
    result = initialize_game(
        name="Kael",
        class_name="warrior",
        background_id=1,
        method="standard_array",
        campaign="default",
        seed=42,
    )

    errors = []
    if result["initialization_report"]["status"] != "success":
        errors.append("Initialization did not report success")

    state = result["state"]
    errors.extend(_validate_state_structure(state, _load_schema()))
    errors.extend(_validate_character(state["character"]))
    errors.extend(_validate_scene(state["current_scene"]))
    errors.extend(_validate_campaign(state["campaign"]))

    if state["meta"]["session_number"] != 1:
        errors.append(f"Session number should be 1, got {state['meta']['session_number']}")
    if len(state["clocks"]) != 0:
        errors.append(f"Default campaign should have 0 clocks, got {len(state['clocks'])}")
    if len(state["chronicle"]) < 1:
        errors.append("Chronicle should have at least 1 entry")

    return errors


def test_nyc_campaign_warrior():
    """Test: NYC campaign with warrior class."""
    from initialize_game import initialize_game
    random.seed(42)
    result = initialize_game(
        name="Kael",
        class_name="warrior",
        background_id=1,
        method="standard_array",
        campaign="nyc",
        seed=42,
    )

    errors = []
    state = result["state"]
    errors.extend(_validate_state_structure(state, _load_schema()))
    errors.extend(_validate_character(state["character"]))
    errors.extend(_validate_scene(state["current_scene"]))
    errors.extend(_validate_campaign(state["campaign"]))
    errors.extend(_validate_nyc_clocks(state["clocks"]))

    scene = state["current_scene"]
    if scene.get("region") != "carven-peaks":
        errors.append(f"NYC scene region should be carven-peaks, got {scene.get('region')}")

    world_sit = state.get("world_situation", {})
    if not world_sit:
        errors.append("NYC campaign should have non-empty world_situation")

    return errors


def test_expert_class():
    """Test: Expert class creation."""
    from initialize_game import initialize_game
    random.seed(99)
    result = initialize_game(
        name="Mira",
        class_name="expert",
        background_id=5,
        campaign="default",
        seed=99,
    )
    errors = _validate_character(result["state"]["character"])
    if result["state"]["character"]["class"] != "expert":
        errors.append("Class should be expert")
    return errors


def test_mage_class():
    """Test: Mage class with tradition."""
    from initialize_game import initialize_game
    random.seed(77)
    result = initialize_game(
        name="Aldric",
        class_name="mage",
        background_id=3,
        tradition="high_mage",
        campaign="default",
        seed=77,
    )
    errors = _validate_character(result["state"]["character"])
    char = result["state"]["character"]
    if char["class"] != "mage":
        errors.append("Class should be mage")
    if char.get("tradition") != "high_mage":
        errors.append(f"Tradition should be high_mage, got {char.get('tradition')}")
    if char.get("effort", {}).get("max", 0) < 1:
        errors.append("Mage should have at least 1 Effort")
    return errors


def test_adventurer_class():
    """Test: Adventurer with partial classes."""
    from initialize_game import initialize_game
    random.seed(55)
    result = initialize_game(
        name="Sera",
        class_name="adventurer",
        background_id=2,
        partial_classes=["expert", "warrior"],
        campaign="default",
        seed=55,
    )
    errors = _validate_character(result["state"]["character"])
    char = result["state"]["character"]
    if char["class"] != "adventurer":
        errors.append("Class should be adventurer")
    if not char.get("partial_classes"):
        errors.append("Adventurer should have partial_classes")
    return errors


def test_determinism():
    """Test: Same seed produces identical output."""
    from initialize_game import initialize_game

    random.seed(42)
    result1 = initialize_game(
        name="Kael", class_name="warrior", background_id=1,
        campaign="nyc", seed=42,
    )

    random.seed(42)
    result2 = initialize_game(
        name="Kael", class_name="warrior", background_id=1,
        campaign="nyc", seed=42,
    )

    errors = []
    char1 = result1["state"]["character"]
    char2 = result2["state"]["character"]
    if char1["attributes"] != char2["attributes"]:
        errors.append("Determinism failure: attributes differ with same seed")
    if char1["hp"] != char2["hp"]:
        errors.append("Determinism failure: HP differs with same seed")
    if char1["saving_throws"] != char2["saving_throws"]:
        errors.append("Determinism failure: saves differ with same seed")
    return errors


def test_schema_validation():
    """Test: Generated state passes schema validator."""
    from initialize_game import initialize_game
    import subprocess

    random.seed(42)
    result = initialize_game(
        name="Kael", class_name="warrior", background_id=1,
        campaign="nyc", seed=42,
    )

    # Write state to temp file
    tmp_path = os.path.join(_test_dir, '_test_init_state.json')
    try:
        with open(tmp_path, 'w') as f:
            json.dump(result["state"], f, indent=2)

        # Run validator
        validator = os.path.join(_scripts_dir, 'validate_state.py')
        proc = subprocess.run(
            [sys.executable, validator, tmp_path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            return [f"Schema validation failed: {proc.stdout} {proc.stderr}"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return []


ALL_TESTS = [
    ("Default campaign warrior", test_default_campaign_warrior),
    ("NYC campaign warrior", test_nyc_campaign_warrior),
    ("Expert class", test_expert_class),
    ("Mage class with tradition", test_mage_class),
    ("Adventurer with partial classes", test_adventurer_class),
    ("Determinism (same seed = same output)", test_determinism),
    ("Schema validation", test_schema_validation),
]


def run_test():
    """Run all initialization tests. Returns True if all pass."""
    print("  Game Initialization Tests")
    print("  " + "-" * 40)

    all_passed = True
    for name, test_fn in ALL_TESTS:
        try:
            errors = test_fn()
            if errors:
                print(f"  FAIL: {name}")
                for e in errors:
                    print(f"    - {e}")
                all_passed = False
            else:
                print(f"  PASS: {name}")
        except Exception as e:
            print(f"  ERR:  {name}: {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
