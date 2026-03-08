#!/usr/bin/env python3
"""
Phase F Validation Test — Atlas + Full Setting acceptance tests.

Tests:
  1. Lore directory structure exists
  2. 40 nation files exist with required §sections
  3. Overview, history, geography, languages files exist
  4. Lore index files exist
  5. Nation files have [UNKNOWN] markers
  6. Lore loading skill exists
  7. Schema has region_id field
"""

import os
import sys
import json

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORE_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "lore")
NATIONS_DIR = os.path.join(LORE_DIR, "nations")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "skills")
SCHEMAS_DIR = os.path.join(RUNTIME_DIR, "schemas")


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


def test_lore_structure(t):
    print("\n[1] LORE DIRECTORY STRUCTURE")

    if os.path.isdir(LORE_DIR):
        t.ok("lore/ directory exists")
    else:
        t.fail("lore/ directory", "Not found")
        return

    if os.path.isdir(NATIONS_DIR):
        t.ok("lore/nations/ directory exists")
    else:
        t.fail("lore/nations/ directory", "Not found")


def test_nation_files(t):
    print("\n[2] NATION FILES")

    if not os.path.isdir(NATIONS_DIR):
        t.fail("nations directory", "Not found")
        return

    nation_files = [f for f in os.listdir(NATIONS_DIR)
                    if f.endswith('.md') and f != 'index.md']

    if len(nation_files) >= 40:
        t.ok(f"nation count: {len(nation_files)} files (target: 40)")
    else:
        t.fail("nation count", f"Only {len(nation_files)} files (need 40)")

    # Check required sections in a sample
    required_sections = ["§history", "§geography", "§government", "§culture",
                         "§sensory-palette", "§voice-notes"]

    sample_size = min(10, len(nation_files))
    sections_ok = 0
    sections_missing = []

    for fname in nation_files[:sample_size]:
        fpath = os.path.join(NATIONS_DIR, fname)
        with open(fpath) as f:
            content = f.read()

        missing = [s for s in required_sections if s not in content]
        if missing:
            sections_missing.append((fname, missing))
        else:
            sections_ok += 1

    if sections_ok == sample_size:
        t.ok(f"nation sections: {sample_size}/{sample_size} sampled files have all required §sections")
    else:
        for fname, missing in sections_missing:
            t.fail(f"nation {fname}", f"Missing sections: {', '.join(missing)}")


def test_overview_files(t):
    print("\n[3] OVERVIEW FILES")

    required_files = [
        ("latter-earth-overview.md", "World primer"),
        ("history-and-ages.md", "Timeline"),
        ("geography.md", "Geographic features"),
        ("languages.md", "Languages"),
    ]

    for fname, desc in required_files:
        fpath = os.path.join(LORE_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                content = f.read()
            if len(content) > 100:
                t.ok(f"{fname}: {desc} ({len(content)} chars)")
            else:
                t.fail(fname, f"Too short ({len(content)} chars)")
        else:
            t.fail(fname, "File not found")


def test_index_files(t):
    print("\n[4] INDEX FILES")

    lore_index = os.path.join(LORE_DIR, "index.md")
    if os.path.exists(lore_index):
        t.ok("lore/index.md exists")
    else:
        t.fail("lore/index.md", "File not found")

    nations_index = os.path.join(NATIONS_DIR, "index.md")
    if os.path.exists(nations_index):
        t.ok("lore/nations/index.md exists")
    else:
        t.fail("lore/nations/index.md", "File not found")


def test_unknown_markers(t):
    print("\n[5] [UNKNOWN] MARKERS")

    if not os.path.isdir(NATIONS_DIR):
        t.fail("[UNKNOWN] markers", "Nations dir not found")
        return

    nation_files = [f for f in os.listdir(NATIONS_DIR)
                    if f.endswith('.md') and f != 'index.md']

    sample_size = min(10, len(nation_files))
    unknown_count = 0

    for fname in nation_files[:sample_size]:
        fpath = os.path.join(NATIONS_DIR, fname)
        with open(fpath) as f:
            content = f.read()
        if "[UNKNOWN]" in content:
            unknown_count += 1

    if unknown_count >= sample_size * 0.8:  # 80% threshold
        t.ok(f"[UNKNOWN] markers: {unknown_count}/{sample_size} sampled files have markers")
    else:
        t.fail("[UNKNOWN] markers", f"Only {unknown_count}/{sample_size} files have markers")


def test_lore_loading_skill(t):
    print("\n[6] LORE LOADING SKILL")

    path = os.path.join(SKILLS_DIR, "lore-loading.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        if len(content) > 200:
            t.ok(f"lore-loading.md exists ({len(content)} chars)")
        else:
            t.fail("lore-loading.md", "Too short")
    else:
        t.fail("lore-loading.md", "File not found")


def test_schema_region(t):
    print("\n[7] SCHEMA REGION FIELDS")

    schema_path = os.path.join(SCHEMAS_DIR, "state.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    scene_props = schema["$defs"]["current_scene"]["properties"]
    if "region_id" in scene_props:
        t.ok("schema: current_scene.region_id defined")
    else:
        t.fail("schema", "current_scene.region_id missing")


def main():
    print("=" * 60)
    print("PHASE F ACCEPTANCE TEST — Atlas + Full Setting")
    print("=" * 60)

    t = TestResult()

    test_lore_structure(t)
    test_nation_files(t)
    test_overview_files(t)
    test_index_files(t)
    test_unknown_markers(t)
    test_lore_loading_skill(t)
    test_schema_region(t)

    success = t.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
