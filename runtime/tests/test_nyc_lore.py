#!/usr/bin/env python3
"""
NYC Lore Integration Test — Validates the Carven Peaks setting content.

Tests:
  1. NYC nation files exist (11 regions) with required §sections
  2. NYC lore files exist (5 cross-cutting references)
  3. Gallery system file covers all 9 levels
  4. NYC factions file covers internal power blocs and boroughs
  5. NYC situation file covers timeline pressures
  6. NYC magic file covers manifestation and attunement
  7. Imperator file covers surge dynamics
  8. Integration touchpoints updated (indexes, manifest, lore-loading)
  9. Key NPCs documented (Still City house leaders, Amundi rulers, Black Pact contacts)
  10. [UNKNOWN] markers present in new nation files
"""

import os
import sys

# Paths
RUNTIME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(RUNTIME_DIR)
LORE_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "lore")
NATIONS_DIR = os.path.join(LORE_DIR, "nations")
SKILLS_DIR = os.path.join(RUNTIME_DIR, "phases", "1-context-loading", "skills")
PHASES_DIR = os.path.join(RUNTIME_DIR, "phases")


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


# --- NYC Nation files (regions the PC can visit) ---
NYC_NATION_FILES = [
    "carven-peaks.md",    # Manhattan + cavern + boroughs overview
    "manthva.md",         # Still Cities on the Gebed Mur
    "mishar.md",          # Arena Kingdom (nearest Amundi)
    "nabardura.md",       # Fragmented Kingdom
    "fidach.md",          # Highland Clans
    "pelegrin.md",        # Ascendant Threat
    "qasir.md",           # Compromised Kingdom
    "vois.md",            # Cautious Republic
    "couront.md",         # Monastic Kingdom
    "verdancy.md",        # The Verdancy threat region
    "black-pact.md",      # Black Pact territories
]

# --- NYC cross-cutting lore files ---
NYC_LORE_FILES = [
    "gallery-system.md",  # 9-level gallery dungeon reference
    "nyc-factions.md",    # Internal NYC power blocs and boroughs
    "nyc-situation.md",   # Dynamic start situation and timeline
    "nyc-magic.md",       # Magic manifestation and attunement
    "imperator.md",       # Caged entity and surge dynamics
]

# Required §-anchored sections for nation files
REQUIRED_NATION_SECTIONS = [
    "§history", "§geography", "§government", "§culture",
    "§sensory-palette", "§voice-notes", "§adventure-hooks",
]


def test_nyc_nation_files(t):
    """Test 1: NYC nation files exist with required §sections."""
    print("\n[1] NYC NATION FILES")

    for fname in NYC_NATION_FILES:
        fpath = os.path.join(NATIONS_DIR, fname)
        if not os.path.exists(fpath):
            t.fail(f"nation/{fname}", "File not found")
            continue

        with open(fpath) as f:
            content = f.read()

        if len(content) < 500:
            t.fail(f"nation/{fname}", f"Too short ({len(content)} chars, need 500+)")
            continue

        missing = [s for s in REQUIRED_NATION_SECTIONS if s not in content]
        if missing:
            t.fail(f"nation/{fname}", f"Missing sections: {', '.join(missing)}")
        else:
            t.ok(f"nation/{fname}: all §sections present ({len(content)} chars)")


def test_nyc_lore_files(t):
    """Test 2: NYC cross-cutting lore files exist with meaningful content."""
    print("\n[2] NYC LORE FILES")

    for fname in NYC_LORE_FILES:
        fpath = os.path.join(LORE_DIR, fname)
        if not os.path.exists(fpath):
            t.fail(f"lore/{fname}", "File not found")
            continue

        with open(fpath) as f:
            content = f.read()

        if len(content) < 500:
            t.fail(f"lore/{fname}", f"Too short ({len(content)} chars, need 500+)")
        else:
            t.ok(f"lore/{fname}: exists ({len(content)} chars)")


def test_gallery_system_content(t):
    """Test 3: Gallery system file covers all 9 levels."""
    print("\n[3] GALLERY SYSTEM CONTENT")

    fpath = os.path.join(LORE_DIR, "gallery-system.md")
    if not os.path.exists(fpath):
        t.fail("gallery-system.md", "File not found")
        return

    with open(fpath) as f:
        content = f.read()

    # Check for level coverage
    level_markers = {
        "Level 1": False, "Level 2": False, "Level 3": False,
        "Level 4": False, "Level 5": False, "Level 6": False,
        "Level 7": False, "Level 8": False, "Level 9": False,
    }
    for marker in level_markers:
        if marker in content:
            level_markers[marker] = True

    covered = sum(1 for v in level_markers.values() if v)
    if covered >= 9:
        t.ok(f"gallery levels: all 9 levels documented")
    else:
        missing = [k for k, v in level_markers.items() if not v]
        t.fail("gallery levels", f"Missing: {', '.join(missing)}")

    # Check for key concepts
    key_concepts = [
        ("feral undead", "Feral undead inhabitants"),
        ("carver", "Undead carver presence"),
        ("Outsider", "Grand Harmony Outsider construction"),
        ("containment", "Containment seals"),
        ("throne-barrow", "Throne-Barrow reference"),
        ("fatality", "Fatality rates"),
    ]
    for keyword, desc in key_concepts:
        if keyword.lower() in content.lower():
            t.ok(f"gallery concept: {desc}")
        else:
            t.fail(f"gallery concept", f"Missing: {desc} (keyword: {keyword})")


def test_nyc_factions_content(t):
    """Test 4: NYC factions file covers internal power blocs and boroughs."""
    print("\n[4] NYC FACTIONS CONTENT")

    fpath = os.path.join(LORE_DIR, "nyc-factions.md")
    if not os.path.exists(fpath):
        t.fail("nyc-factions.md", "File not found")
        return

    with open(fpath) as f:
        content = f.read()

    # Check for borough coverage
    boroughs = ["Manhattan", "Queens", "Bronx", "Staten Island", "Brooklyn"]
    for borough in boroughs:
        if borough in content:
            t.ok(f"borough: {borough} documented")
        else:
            t.fail(f"borough", f"Missing: {borough}")

    # Check for power blocs
    blocs = ["JDA", "Council of Five"]
    for bloc in blocs:
        if bloc in content:
            t.ok(f"power bloc: {bloc} documented")
        else:
            t.fail(f"power bloc", f"Missing: {bloc}")


def test_nyc_situation_content(t):
    """Test 5: NYC situation file covers timeline pressures."""
    print("\n[5] NYC SITUATION CONTENT")

    fpath = os.path.join(LORE_DIR, "nyc-situation.md")
    if not os.path.exists(fpath):
        t.fail("nyc-situation.md", "File not found")
        return

    with open(fpath) as f:
        content = f.read()

    # Check for timeline phases
    phases = [
        ("food", "Food crisis pressure"),
        ("surge", "Surge event"),
        ("trade", "Trade establishment"),
        ("borough", "Borough divergence"),
    ]
    for keyword, desc in phases:
        if keyword.lower() in content.lower():
            t.ok(f"situation: {desc}")
        else:
            t.fail(f"situation", f"Missing: {desc}")


def test_nyc_magic_content(t):
    """Test 6: NYC magic file covers manifestation and attunement."""
    print("\n[6] NYC MAGIC CONTENT")

    fpath = os.path.join(LORE_DIR, "nyc-magic.md")
    if not os.path.exists(fpath):
        t.fail("nyc-magic.md", "File not found")
        return

    with open(fpath) as f:
        content = f.read()

    concepts = [
        ("Legacy", "Legacy interaction mechanism"),
        ("attunement", "Gallery attunement system"),
        ("Foci", "Foci manifestation"),
    ]
    for keyword, desc in concepts:
        if keyword in content:
            t.ok(f"magic: {desc}")
        else:
            t.fail(f"magic", f"Missing: {desc}")


def test_imperator_content(t):
    """Test 7: Imperator file covers surge dynamics."""
    print("\n[7] IMPERATOR CONTENT")

    fpath = os.path.join(LORE_DIR, "imperator.md")
    if not os.path.exists(fpath):
        t.fail("imperator.md", "File not found")
        return

    with open(fpath) as f:
        content = f.read()

    concepts = [
        ("servitor", "Servitor types"),
        ("surge", "Surge dynamics"),
        ("seal", "Containment seal mechanics"),
        ("cage", "Cage reference"),
    ]
    for keyword, desc in concepts:
        if keyword.lower() in content.lower():
            t.ok(f"imperator: {desc}")
        else:
            t.fail(f"imperator", f"Missing: {desc}")


def test_integration_touchpoints(t):
    """Test 8: Integration touchpoints updated."""
    print("\n[8] INTEGRATION TOUCHPOINTS")

    # Check lore/index.md references NYC files
    lore_index = os.path.join(LORE_DIR, "index.md")
    if os.path.exists(lore_index):
        with open(lore_index) as f:
            content = f.read()
        if "gallery-system.md" in content and "nyc-factions.md" in content:
            t.ok("lore/index.md references NYC lore files")
        else:
            t.fail("lore/index.md", "Missing NYC lore file references")
    else:
        t.fail("lore/index.md", "File not found")

    # Check nations/index.md references NYC nations
    nations_index = os.path.join(NATIONS_DIR, "index.md")
    if os.path.exists(nations_index):
        with open(nations_index) as f:
            content = f.read()
        if "carven-peaks.md" in content and "mishar.md" in content:
            t.ok("nations/index.md references NYC nation files")
        else:
            t.fail("nations/index.md", "Missing NYC nation references")
    else:
        t.fail("nations/index.md", "File not found")

    # Check phase-manifest.md references NYC content
    manifest = os.path.join(PHASES_DIR, "phase-manifest.md")
    if os.path.exists(manifest):
        with open(manifest) as f:
            content = f.read()
        if "carven-peaks" in content:
            t.ok("phase-manifest.md references Carven Peaks")
        else:
            t.fail("phase-manifest.md", "Missing Carven Peaks reference")
    else:
        t.fail("phase-manifest.md", "File not found")

    # Check lore-loading.md has NYC loading rules
    lore_loading = os.path.join(SKILLS_DIR, "lore-loading.md")
    if os.path.exists(lore_loading):
        with open(lore_loading) as f:
            content = f.read()
        if "carven-peaks" in content.lower() or "nyc" in content.lower():
            t.ok("lore-loading.md has NYC/Carven Peaks loading rules")
        else:
            t.fail("lore-loading.md", "Missing NYC loading rules")
    else:
        t.fail("lore-loading.md", "File not found")


def test_key_npcs(t):
    """Test 9: Key NPCs documented across files."""
    print("\n[9] KEY NPCs")

    # Still City house leaders
    npc_checks = [
        ("manthva.md", NATIONS_DIR, ["Cassivus", "Meridia", "Viccius"]),
        ("mishar.md", NATIONS_DIR, ["Amiya"]),
        ("pelegrin.md", NATIONS_DIR, ["Gautier"]),
        ("couront.md", NATIONS_DIR, ["Enguerrand"]),
    ]

    for fname, basedir, npcs in npc_checks:
        fpath = os.path.join(basedir, fname)
        if not os.path.exists(fpath):
            t.fail(f"NPCs in {fname}", "File not found")
            continue
        with open(fpath) as f:
            content = f.read()
        missing = [n for n in npcs if n not in content]
        if missing:
            t.fail(f"NPCs in {fname}", f"Missing: {', '.join(missing)}")
        else:
            t.ok(f"NPCs in {fname}: {', '.join(npcs)}")

    # Black Pact contacts
    bp_path = os.path.join(NATIONS_DIR, "black-pact.md")
    if os.path.exists(bp_path):
        with open(bp_path) as f:
            content = f.read()
        if "Shael" in content and "Kadric" in content:
            t.ok("NPCs in black-pact.md: Shael, Kadric")
        else:
            t.fail("NPCs in black-pact.md", "Missing Shael or Kadric")
    else:
        t.fail("NPCs in black-pact.md", "File not found")


def test_unknown_markers(t):
    """Test 10: [UNKNOWN] markers present in new nation files."""
    print("\n[10] [UNKNOWN] MARKERS")

    unknown_count = 0
    checked = 0

    for fname in NYC_NATION_FILES:
        fpath = os.path.join(NATIONS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        checked += 1
        with open(fpath) as f:
            content = f.read()
        if "[UNKNOWN]" in content:
            unknown_count += 1

    if checked == 0:
        t.fail("[UNKNOWN] markers", "No NYC nation files found to check")
    elif unknown_count >= checked * 0.7:  # 70% threshold
        t.ok(f"[UNKNOWN] markers: {unknown_count}/{checked} NYC nation files have markers")
    else:
        t.fail("[UNKNOWN] markers", f"Only {unknown_count}/{checked} files have markers (need 70%)")


def run_test():
    """Entry point for run_all_tests.py integration."""
    print("=" * 60)
    print("NYC LORE INTEGRATION TEST — Carven Peaks Setting")
    print("=" * 60)

    t = TestResult()

    test_nyc_nation_files(t)
    test_nyc_lore_files(t)
    test_gallery_system_content(t)
    test_nyc_factions_content(t)
    test_nyc_situation_content(t)
    test_nyc_magic_content(t)
    test_imperator_content(t)
    test_integration_touchpoints(t)
    test_key_npcs(t)
    test_unknown_markers(t)

    return t.summary()


def main():
    success = run_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
