"""Exploration domain tag tables — structure and integration tests.

Validates that wilderness_tags, ruin_tags, and community_tags:
1. Exist and are importable
2. Have 20+ entries each
3. Every tag dict has all 6 required keys with non-empty string values
4. Tag names are unique within each table
5. scene.py integration: _load_tags returns real data, generate_scene uses tags (not fallback)
6. generate_ruin returns depth_level and has_treasure
"""

import sys
import os
import random

# Add exploration scripts and tables to path
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_runtime_dir = os.path.join(_tests_dir, '..')
_exploration_scripts = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills', 'exploration', 'scripts')
_exploration_tables = os.path.join(_runtime_dir, 'phases', '3-resolution', 'skills', 'exploration', 'tables')

for _p in [_exploration_scripts, _exploration_tables]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

REQUIRED_KEYS = {"name", "description", "enemies", "friends", "complications", "things", "places"}
MIN_TAG_COUNT = 20


def _check_tag_table(table, table_name):
    """Validate a single tag table. Returns list of error strings."""
    errors = []

    if not isinstance(table, list):
        return [f"{table_name}: expected list, got {type(table).__name__}"]

    if len(table) < MIN_TAG_COUNT:
        errors.append(f"{table_name}: expected {MIN_TAG_COUNT}+ entries, got {len(table)}")

    names_seen = set()
    for i, tag in enumerate(table):
        if not isinstance(tag, dict):
            errors.append(f"{table_name}[{i}]: expected dict, got {type(tag).__name__}")
            continue

        # Check required keys
        missing = REQUIRED_KEYS - set(tag.keys())
        if missing:
            errors.append(f"{table_name}[{i}] ({tag.get('name', '?')}): missing keys {missing}")

        # Check non-empty strings
        for key in REQUIRED_KEYS:
            val = tag.get(key)
            if val is not None and (not isinstance(val, str) or not val.strip()):
                errors.append(f"{table_name}[{i}] ({tag.get('name', '?')}): key '{key}' must be non-empty string, got {repr(val)}")

        # Check uniqueness
        name = tag.get("name", "")
        if name in names_seen:
            errors.append(f"{table_name}[{i}]: duplicate name '{name}'")
        names_seen.add(name)

    return errors


def test_wilderness_tags():
    """Test wilderness_tags.py exists and has valid structure."""
    from wilderness_tags import WILDERNESS_TAGS
    errors = _check_tag_table(WILDERNESS_TAGS, "WILDERNESS_TAGS")
    return errors


def test_ruin_tags():
    """Test ruin_tags.py exists and has valid structure."""
    from ruin_tags import RUIN_TAGS
    errors = _check_tag_table(RUIN_TAGS, "RUIN_TAGS")
    return errors


def test_community_tags():
    """Test community_tags.py exists and has valid structure."""
    from community_tags import COMMUNITY_TAGS
    errors = _check_tag_table(COMMUNITY_TAGS, "COMMUNITY_TAGS")
    return errors


def test_scene_load_tags():
    """Test scene.py _load_tags returns real data (not empty fallback)."""
    from scene import _load_tags
    errors = []
    for tag_type in ["wilderness", "ruin", "community"]:
        tags = _load_tags(tag_type)
        if not tags:
            errors.append(f"_load_tags('{tag_type}') returned empty list — table not found")
        elif len(tags) < MIN_TAG_COUNT:
            errors.append(f"_load_tags('{tag_type}') returned {len(tags)} tags, expected {MIN_TAG_COUNT}+")
    return errors


def test_generate_scene_uses_tags():
    """Test generate_scene returns tag-based output, not fallback."""
    from scene import generate_scene
    random.seed(42)
    errors = []
    for scene_type in ["wilderness", "ruin", "community"]:
        result = generate_scene(scene_type, tag_count=2, threat_level=5)
        if "fallback" in result.get("tags_used", []):
            errors.append(f"generate_scene('{scene_type}') fell back to fallback — tags not loaded")
        if not result.get("tag_details"):
            errors.append(f"generate_scene('{scene_type}') has empty tag_details")
        if not result.get("scene_seed"):
            errors.append(f"generate_scene('{scene_type}') has empty scene_seed")
        # Verify combined_elements has content
        elements = result.get("combined_elements", {})
        if not any(elements.get(k) for k in ["enemies", "friends", "complications", "things", "places"]):
            errors.append(f"generate_scene('{scene_type}') has no combined elements")
    return errors


def test_generate_ruin():
    """Test generate_ruin returns depth_level and has_treasure."""
    from scene import generate_ruin
    random.seed(42)
    errors = []
    result = generate_ruin(depth_level=3, tag_count=2)
    if "depth_level" not in result:
        errors.append("generate_ruin() missing 'depth_level' key")
    elif result["depth_level"] != 3:
        errors.append(f"generate_ruin() depth_level={result['depth_level']}, expected 3")
    if "has_treasure" not in result:
        errors.append("generate_ruin() missing 'has_treasure' key")
    if "fallback" in result.get("tags_used", []):
        errors.append("generate_ruin() fell back to fallback — ruin tags not loaded")
    return errors


def run_test():
    """Entry point for run_all_tests.py."""
    all_tests = [
        ("Wilderness tags structure", test_wilderness_tags),
        ("Ruin tags structure", test_ruin_tags),
        ("Community tags structure", test_community_tags),
        ("scene.py _load_tags integration", test_scene_load_tags),
        ("generate_scene uses tags", test_generate_scene_uses_tags),
        ("generate_ruin output", test_generate_ruin),
    ]

    all_passed = True
    for test_name, test_fn in all_tests:
        try:
            errors = test_fn()
            if errors:
                all_passed = False
                print(f"  FAIL: {test_name}")
                for e in errors:
                    print(f"    - {e}")
            else:
                print(f"  PASS: {test_name}")
        except Exception as e:
            all_passed = False
            print(f"  ERROR: {test_name}: {e}")

    return all_passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
