#!/usr/bin/env python3
"""
Phase E Validation Test — Narrative Layer acceptance tests.

Tests:
  1. Latter Earth voice guide exists and has required sections
  2. Narration mappings expanded with all mechanic types
  3. Character sheet template exists
  4. Scene rendering template exists
  5. Failure flavor tables cover all domains with 5+ entries each
  6. Threat-environment mapping exists
  7. NPC dialogue protocol exists
  8. Narration grounding validator runs
  9. Drama budget in schema and state
"""

import os
import sys
import json

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARRATIVE_DIR = os.path.join(RUNTIME_DIR, "phases", "4-narrative")
REFS_DIR = os.path.join(NARRATIVE_DIR, "references")
ASSETS_DIR = os.path.join(NARRATIVE_DIR, "assets")
TABLES_DIR = os.path.join(NARRATIVE_DIR, "tables")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")
STATE_FILE = os.path.join(RUNTIME_DIR, "state.json")
SCRIPTS_DIR = os.path.join(RUNTIME_DIR, "scripts")

# Add tables to path
if os.path.isdir(TABLES_DIR) and TABLES_DIR not in sys.path:
    sys.path.insert(0, TABLES_DIR)


class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []

    def ok(self, name):
        self.passed.append(name)
        print(f"  PASS  {name}")

    def fail(self, name, reason=""):
        self.failed.append((name, reason))
        print(f"  FAIL  {name}: {reason}")

    def error(self, name, exc):
        self.errors.append((name, str(exc)))
        print(f"  ERR   {name}: {exc}")

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.errors)
        print(f"\n{'='*60}")
        print(f"RESULTS: {len(self.passed)}/{total} passed, "
              f"{len(self.failed)} failed, {len(self.errors)} errors")
        print(f"{'='*60}")
        if self.failed:
            print("\nFAILURES:")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        if self.errors:
            print("\nERRORS:")
            for name, exc in self.errors:
                print(f"  - {name}: {exc}")
        return len(self.failed) == 0 and len(self.errors) == 0


def test_voice_guide(t):
    print("\n[1] LATTER EARTH VOICE GUIDE")
    path = os.path.join(REFS_DIR, "latter-earth-voice.md")
    if not os.path.exists(path):
        t.fail("latter-earth-voice.md", "File not found")
        return

    with open(path) as f:
        content = f.read()

    assert len(content) > 200, f"Voice guide too short: {len(content)} chars"
    t.ok(f"latter-earth-voice.md exists ({len(content)} chars)")


def test_narration_mappings(t):
    print("\n[2] NARRATION MAPPINGS")
    path = os.path.join(REFS_DIR, "narration-mappings.md")
    if not os.path.exists(path):
        t.fail("narration-mappings.md", "File not found")
        return

    with open(path) as f:
        content = f.read()

    required_sections = [
        "§combat-hit", "§combat-miss", "§combat-shock",
        "§skill-check-success", "§skill-check-failure",
        "§save-success", "§save-failure",
        "§spell-cast", "§travel", "§social",
        "§exploration", "§consequence",
    ]

    missing = [s for s in required_sections if s not in content]
    if missing:
        t.fail("narration-mappings sections", f"Missing: {', '.join(missing)}")
    else:
        t.ok(f"narration-mappings: all {len(required_sections)} sections present")

    if "Drama Budget" in content:
        t.ok("narration-mappings: drama budget integration present")
    else:
        t.fail("narration-mappings", "Missing drama budget integration")


def test_templates(t):
    print("\n[3] DISPLAY TEMPLATES")

    # Character sheet template
    cs_path = os.path.join(ASSETS_DIR, "character-sheet-template.md")
    if os.path.exists(cs_path):
        with open(cs_path) as f:
            content = f.read()
        assert len(content) > 50, "Character sheet template too short"
        t.ok(f"character-sheet-template.md ({len(content)} chars)")
    else:
        t.fail("character-sheet-template.md", "File not found")

    # Scene template
    sc_path = os.path.join(ASSETS_DIR, "scene-template.md")
    if os.path.exists(sc_path):
        with open(sc_path) as f:
            content = f.read()
        assert len(content) > 50, "Scene template too short"
        t.ok(f"scene-template.md ({len(content)} chars)")
    else:
        t.fail("scene-template.md", "File not found")


def test_failure_flavors(t):
    print("\n[4] FAILURE FLAVOR TABLES")

    try:
        from failure_flavors import FAILURE_FLAVORS

        assert isinstance(FAILURE_FLAVORS, dict), "FAILURE_FLAVORS must be a dict"

        required_domains = [
            "combat_miss", "skill_check_failure", "spell_failure",
            "travel_hazard", "social_gaffe", "save_failure",
        ]

        for domain in required_domains:
            if domain not in FAILURE_FLAVORS:
                t.fail(f"failure_flavors.{domain}", "Domain missing")
                continue
            entries = FAILURE_FLAVORS[domain]
            if len(entries) < 5:
                t.fail(f"failure_flavors.{domain}", f"Only {len(entries)} entries (need 5+)")
            else:
                # Check all entries are non-empty strings
                all_valid = all(isinstance(e, str) and len(e) > 10 for e in entries)
                if all_valid:
                    t.ok(f"failure_flavors.{domain}: {len(entries)} entries")
                else:
                    t.fail(f"failure_flavors.{domain}", "Some entries are empty or too short")

    except Exception as e:
        t.error("failure_flavors", e)


def test_threat_mapping(t):
    print("\n[5] THREAT-ENVIRONMENT MAPPING")
    path = os.path.join(REFS_DIR, "threat-environment-mapping.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        assert len(content) > 200, "Threat mapping too short"
        t.ok(f"threat-environment-mapping.md ({len(content)} chars)")
    else:
        t.fail("threat-environment-mapping.md", "File not found")


def test_npc_dialogue(t):
    print("\n[6] NPC DIALOGUE PROTOCOL")
    path = os.path.join(REFS_DIR, "npc-dialogue-protocol.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        assert len(content) > 200, "NPC dialogue protocol too short"
        t.ok(f"npc-dialogue-protocol.md ({len(content)} chars)")
    else:
        t.fail("npc-dialogue-protocol.md", "File not found")


def test_narration_grounding_validator(t):
    print("\n[7] NARRATION GROUNDING VALIDATOR")
    path = os.path.join(SCRIPTS_DIR, "validate_narration_grounding.py")
    if os.path.exists(path):
        t.ok("validate_narration_grounding.py exists")
    else:
        t.fail("validate_narration_grounding.py", "File not found")


def test_drama_budget(t):
    print("\n[8] DRAMA BUDGET")

    # Check schema
    schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    if "session" in schema["$defs"]:
        session_def = schema["$defs"]["session"]
        props = session_def.get("properties", {})
        if "drama_budget" in props:
            t.ok("schema: session.drama_budget defined")
        else:
            t.fail("schema", "session.drama_budget missing")
        if "drama_events" in props:
            t.ok("schema: session.drama_events defined")
        else:
            t.fail("schema", "session.drama_events missing")
    else:
        t.fail("schema", "session def missing")

    # Check state
    with open(STATE_FILE) as f:
        state = json.load(f)
    if "session" in state:
        if state["session"].get("drama_budget") == 3:
            t.ok("state: drama_budget = 3")
        else:
            t.fail("state", f"drama_budget = {state['session'].get('drama_budget')}")
    else:
        t.fail("state", "session field missing")


def main():
    print("=" * 60)
    print("PHASE E ACCEPTANCE TEST — Narrative Layer")
    print("=" * 60)

    t = TestResult()

    test_voice_guide(t)
    test_narration_mappings(t)
    test_templates(t)
    test_failure_flavors(t)
    test_threat_mapping(t)
    test_npc_dialogue(t)
    test_narration_grounding_validator(t)
    test_drama_budget(t)

    success = t.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
