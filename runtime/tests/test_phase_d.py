#!/usr/bin/env python3
"""
Phase D Validation Test — Social + Factions acceptance tests.

Tests:
  1. Social data tables (character_tags, court_tags, faction_actions)
  2. World-building tables (government, society, religion)
  3. NPC generation with voice cards
  4. Faction turn processing
  5. Diplomacy script (persuasion, bribery, negotiation)
  6. Consequence tracker
  7. Schema v7.5.0 with D/E/F fields
  8. Reference documents exist
  9. CLI commands (generate-npc, reaction-roll, faction-turn)
"""

import os
import sys
import json
import subprocess

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(RUNTIME_DIR)
SCRIPTS_DIR = os.path.join(RUNTIME_DIR, "scripts")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "3-resolution", "skills")
SOCIAL_TABLES = os.path.join(SKILLS_DIR, "social", "tables")
SOCIAL_SCRIPTS = os.path.join(SKILLS_DIR, "social", "scripts")
SOCIAL_REFS = os.path.join(SKILLS_DIR, "social", "references")
WB_TABLES = os.path.join(SKILLS_DIR, "world-building", "tables")
CORE_SCRIPTS = os.path.join(SKILLS_DIR, "core", "scripts")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")
CLI = os.path.join(SCRIPTS_DIR, "emergence_cli.py")
STATE_FILE = os.path.join(RUNTIME_DIR, "state.json")

# Add paths for imports
for d in [SOCIAL_TABLES, SOCIAL_SCRIPTS, WB_TABLES, CORE_SCRIPTS]:
    if os.path.isdir(d) and d not in sys.path:
        sys.path.insert(0, d)


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


def run_cli(args_list):
    """Run emergence_cli.py with given args."""
    cmd = [sys.executable, CLI] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return result.returncode, result.stdout, result.stderr


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: Social Data Tables
# ══════════════════════════════════════════════════════════════════════════════

def test_social_tables(t):
    print("\n[1] SOCIAL DATA TABLES")

    # 1a. Character tags
    try:
        from character_tags import CHARACTER_TAGS
        assert isinstance(CHARACTER_TAGS, list), "CHARACTER_TAGS must be a list"
        assert len(CHARACTER_TAGS) >= 50, f"Expected 50+ character tags, got {len(CHARACTER_TAGS)}"
        first = CHARACTER_TAGS[0]
        assert "tag" in first, "Tag must have 'tag'"
        assert "description" in first, "Tag must have 'description'"
        t.ok(f"character_tags: {len(CHARACTER_TAGS)} tags loaded")
    except Exception as e:
        t.error("character_tags", e)

    # 1b. Court tags
    try:
        from court_tags import COURT_TAGS
        assert isinstance(COURT_TAGS, list), "COURT_TAGS must be a list"
        assert len(COURT_TAGS) >= 20, f"Expected 20+ court tags, got {len(COURT_TAGS)}"
        first = COURT_TAGS[0]
        assert "tag" in first, "Court tag must have 'tag'"
        t.ok(f"court_tags: {len(COURT_TAGS)} tags loaded")
    except Exception as e:
        t.error("court_tags", e)

    # 1c. Faction actions
    try:
        from faction_actions import FACTION_ACTIONS
        assert isinstance(FACTION_ACTIONS, dict), "FACTION_ACTIONS must be a dict"
        assert len(FACTION_ACTIONS) >= 10, f"Expected 10+ faction actions, got {len(FACTION_ACTIONS)}"
        first_key = next(iter(FACTION_ACTIONS))
        first = FACTION_ACTIONS[first_key]
        assert "cost" in first, "Faction action must have 'cost'"
        t.ok(f"faction_actions: {len(FACTION_ACTIONS)} actions loaded")
    except Exception as e:
        t.error("faction_actions", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: World-Building Tables
# ══════════════════════════════════════════════════════════════════════════════

def test_wb_tables(t):
    print("\n[2] WORLD-BUILDING TABLES")

    # 2a. Government tables
    try:
        from government_tables import GOVERNMENT_TYPES
        assert isinstance(GOVERNMENT_TYPES, list), "GOVERNMENT_TYPES must be a list"
        assert len(GOVERNMENT_TYPES) >= 10, f"Expected 10+ government types, got {len(GOVERNMENT_TYPES)}"
        t.ok(f"government_tables: {len(GOVERNMENT_TYPES)} types loaded")
    except Exception as e:
        t.error("government_tables", e)

    # 2b. Society tables
    try:
        from society_tables import SOCIETY_TYPES
        assert isinstance(SOCIETY_TYPES, list), "SOCIETY_TYPES must be a list"
        assert len(SOCIETY_TYPES) >= 10, f"Expected 10+ society types, got {len(SOCIETY_TYPES)}"
        t.ok(f"society_tables: {len(SOCIETY_TYPES)} types loaded")
    except Exception as e:
        t.error("society_tables", e)

    # 2c. Religion tables
    try:
        from religion_tables import RELIGION_TYPES
        assert isinstance(RELIGION_TYPES, list), "RELIGION_TYPES must be a list"
        assert len(RELIGION_TYPES) >= 10, f"Expected 10+ religion types, got {len(RELIGION_TYPES)}"
        t.ok(f"religion_tables: {len(RELIGION_TYPES)} types loaded")
    except Exception as e:
        t.error("religion_tables", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: NPC Generation
# ══════════════════════════════════════════════════════════════════════════════

def test_npc_generation(t):
    print("\n[3] NPC GENERATION")

    import random
    random.seed(42)

    try:
        from npc import generate_npc, reaction_roll

        # 3a. Generate NPC
        npc = generate_npc(importance="major", region="coastal", tag_count=2)
        assert "name" in npc, "NPC must have name"
        assert "voice_card" in npc, "NPC must have voice_card"
        assert "personality_traits" in npc, "NPC must have personality_traits"
        assert "speech_patterns" in npc, "NPC must have speech_patterns"
        assert "key_phrases" in npc, "NPC must have key_phrases"
        assert "motivation" in npc, "NPC must have motivation"
        assert npc["importance"] == "major"
        t.ok(f"generate_npc: {npc['name']} ({npc['role']})")

        # 3b. Deterministic NPC generation
        random.seed(42)
        npc2 = generate_npc(importance="major", region="coastal", tag_count=2)
        assert npc["name"] == npc2["name"], "Same seed must produce same NPC"
        t.ok("npc determinism: same seed → same NPC")

        # 3c. Reaction roll
        random.seed(42)
        reaction = reaction_roll(modifier=2)
        assert "disposition" in reaction, "Reaction must have disposition"
        assert "total" in reaction, "Reaction must have total"
        assert "arithmetic_trace" in reaction, "Reaction must have trace"
        t.ok(f"reaction_roll: {reaction['total']} → {reaction['disposition']}")

    except Exception as e:
        t.error("npc_generation", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Faction Turn
# ══════════════════════════════════════════════════════════════════════════════

def test_faction_turn(t):
    print("\n[4] FACTION TURN")

    import random
    random.seed(42)

    try:
        from faction import faction_turn

        factions = [
            {
                "id": "faction_001",
                "name": "Iron Brotherhood",
                "archetype": "aggressive",
                "goal": "Conquer the northern territories",
                "power_level": 7,
                "clock": {"name": "Northern Conquest", "current": 3, "max": 6, "status": "active"},
            },
            {
                "id": "faction_002",
                "name": "Merchant Guild",
                "archetype": "mercantile",
                "goal": "Monopolize trade routes",
                "power_level": 5,
                "clock": {"name": "Trade Monopoly", "current": 1, "max": 8, "status": "active"},
            },
            {
                "id": "faction_003",
                "name": "Shadow Court",
                "archetype": "neutral",
                "goal": "Infiltrate the ruling council",
                "power_level": 4,
                "clock": {"name": "Council Infiltration", "current": 5, "max": 6, "status": "active"},
            },
        ]

        result = faction_turn(factions)
        assert result["faction_count"] == 3, f"Expected 3 factions, got {result['faction_count']}"
        assert result["actions_taken"] > 0, "At least one faction must act"
        assert "results" in result, "Must have results list"
        for r in result["results"]:
            assert "faction" in r, "Each result must name the faction"
            assert "action" in r, "Each result must name the action"
            assert "arithmetic_trace" in r, "Each result must have trace"
        t.ok(f"faction_turn: {result['actions_taken']} factions acted")

    except Exception as e:
        t.error("faction_turn", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 5: Diplomacy
# ══════════════════════════════════════════════════════════════════════════════

def test_diplomacy(t):
    print("\n[5] DIPLOMACY")

    import random
    random.seed(42)

    try:
        from diplomacy import persuasion_check, calculate_bribe_cost

        # 5a. Persuasion check
        result = persuasion_check(skill_mod=1, disposition="neutral", context_modifiers=[])
        assert "outcome" in result, "Persuasion must have outcome field"
        assert "arithmetic_trace" in result, "Persuasion must have trace"
        t.ok(f"persuasion_check: {result['outcome']}")

        # 5b. Bribe cost
        cost = calculate_bribe_cost(npc_importance="major", request_difficulty="moderate")
        assert "total_cost_gp" in cost, "Bribe must have total_cost_gp"
        assert cost["total_cost_gp"] > 0, "Bribe cost must be positive"
        t.ok(f"calculate_bribe_cost: {cost['total_cost_gp']} gp")

    except Exception as e:
        t.error("diplomacy", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 6: Consequence Tracker
# ══════════════════════════════════════════════════════════════════════════════

def test_consequence_tracker(t):
    print("\n[6] CONSEQUENCE TRACKER")

    try:
        from consequence import check_consequences, create_consequence

        # 6a. Create consequence
        c = create_consequence(
            trigger_condition="Player returns to Ironhaven",
            timer_days=5,
            consequence_description="The merchant ambush is sprung",
            source_turn=1,
        )
        assert "id" in c, "Consequence must have id"
        assert c["status"] == "pending", "New consequence must be pending"
        assert c["timer_days"] == 5
        t.ok("create_consequence: consequence created")

        # 6b. Check consequences (not yet triggered — timer decrements by 1)
        tracker = [c]
        result = check_consequences(tracker, current_day=2)
        assert len(result["triggered"]) == 0, "First check should not trigger a 5-day timer"
        t.ok("check_consequences: no early trigger")

        # 6c. Check consequences (triggered by timer — use 1-day timer)
        short_c = create_consequence(
            trigger_condition="Immediate threat",
            timer_days=1,
            consequence_description="Ambush triggered",
            source_turn=2,
        )
        triggered_result = check_consequences([short_c], current_day=2)
        assert len(triggered_result["triggered"]) >= 1, "1-day timer should trigger after one check"
        t.ok("check_consequences: timer trigger works")

    except Exception as e:
        t.error("consequence_tracker", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 7: Schema v7.5.0
# ══════════════════════════════════════════════════════════════════════════════

def test_schema(t):
    print("\n[7] SCHEMA v7.5.0")

    try:
        schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
        with open(schema_path) as f:
            schema = json.load(f)
        assert "7.5.0" in schema["description"], "Schema description must mention 7.5.0"

        # Check new D/E/F fields exist in schema
        props = schema["properties"]
        assert "consequence_tracker" in props, "Schema must have consequence_tracker"
        assert "session" in props, "Schema must have session"

        defs = schema["$defs"]
        assert "consequence_entry" in defs, "Schema must define consequence_entry"
        assert "session" in defs, "Schema must define session"
        assert "campaign_arc" in defs, "Schema must define campaign_arc"

        # Check NPC voice card fields
        npc_props = defs["known_npc"]["properties"]
        assert "voice_card" in npc_props, "NPC schema must have voice_card"
        assert "personality_traits" in npc_props, "NPC schema must have personality_traits"
        assert "speech_patterns" in npc_props, "NPC schema must have speech_patterns"
        assert "key_phrases" in npc_props, "NPC schema must have key_phrases"

        # Check faction expansion
        faction_props = defs["human_faction"]["properties"]
        assert "assets" in faction_props, "Faction schema must have assets"
        assert "turn_history" in faction_props, "Faction schema must have turn_history"

        # Check scene region_id
        scene_props = defs["current_scene"]["properties"]
        assert "region_id" in scene_props, "Scene schema must have region_id"

        t.ok("schema v7.5.0 validated with D/E/F fields")

    except Exception as e:
        t.error("schema", e)

    # Check state.json matches
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        assert state["schema_version"] == "7.5.0", f"State must be v7.5.0, got {state['schema_version']}"
        assert "consequence_tracker" in state, "State must have consequence_tracker"
        assert "session" in state, "State must have session"
        assert state["session"]["drama_budget"] == 3, "Drama budget must start at 3"
        t.ok("state.json matches schema v7.5.0")
    except Exception as e:
        t.error("state.json", e)


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 8: Reference Documents
# ══════════════════════════════════════════════════════════════════════════════

def test_references(t):
    print("\n[8] REFERENCE DOCUMENTS")

    refs = [
        (os.path.join(SOCIAL_REFS, "npc-reactions.md"), "NPC reactions"),
        (os.path.join(SOCIAL_REFS, "faction-rules.md"), "Faction rules"),
        (os.path.join(SOCIAL_REFS, "court-intrigue.md"), "Court intrigue"),
    ]

    for path, name in refs:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert len(content) > 200, f"{name} is too short ({len(content)} chars)"
            t.ok(f"{name}: exists ({len(content)} chars)")
        else:
            t.fail(f"{name}", f"File not found: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 9: CLI Commands
# ══════════════════════════════════════════════════════════════════════════════

def test_cli_commands(t):
    print("\n[9] CLI COMMANDS")

    # 9a. generate-npc
    rc, out, err = run_cli(["generate-npc", "--importance", "major", "--region", "coastal",
                            "--tags", "2", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "name" in data
        assert "voice_card" in data
        t.ok(f"generate-npc: {data['name']}")
    else:
        t.fail("generate-npc", err.strip())

    # 9b. reaction-roll
    rc, out, err = run_cli(["reaction-roll", "--modifier", "2", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "disposition" in data
        t.ok(f"reaction-roll: {data['disposition']}")
    else:
        t.fail("reaction-roll", err.strip())

    # 9c. faction-turn (may have no factions in state)
    rc, out, err = run_cli(["faction-turn", "--seed", "42"])
    if rc == 0:
        data = json.loads(out)
        assert "faction_count" in data
        t.ok(f"faction-turn: {data['faction_count']} factions")
    else:
        t.fail("faction-turn", err.strip())


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("PHASE D ACCEPTANCE TEST — Social + Factions")
    print("=" * 60)

    t = TestResult()

    test_social_tables(t)
    test_wb_tables(t)
    test_npc_generation(t)
    test_faction_turn(t)
    test_diplomacy(t)
    test_consequence_tracker(t)
    test_schema(t)
    test_references(t)
    test_cli_commands(t)

    success = t.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
