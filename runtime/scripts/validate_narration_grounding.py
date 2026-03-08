#!/usr/bin/env python3
"""Narration grounding validator (Phase E / E-IMPL-9).

Checks narrated text for proper nouns that don't appear in loaded context.
Flags potential hallucinations for review.

This is a development-time tool, not a turn-loop blocker.

Usage:
    python validate_narration_grounding.py <narration_text_file> <context_files...>
    python validate_narration_grounding.py --check-lore-dir <lore_dir>
"""

import re
import sys
import os
import json


# Common English proper nouns to whitelist (not WWN-specific)
WHITELIST = {
    # Directions and time
    "North", "South", "East", "West", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
    # Common titles
    "Sir", "Lord", "Lady", "King", "Queen", "Prince", "Princess",
    "Captain", "General", "Master", "Mistress",
    # Generic fantasy terms that aren't setting-specific
    "God", "Gods", "Devil", "Dragon", "Elf", "Dwarf", "Giant",
}


def extract_proper_nouns(text):
    """Extract capitalized multi-word phrases and single capitalized words
    that look like proper nouns (not at sentence starts)."""
    proper_nouns = set()

    # Split into sentences
    sentences = re.split(r'[.!?]\s+', text)

    for sentence in sentences:
        words = sentence.split()
        for i, word in enumerate(words):
            # Skip first word of sentence (always capitalized)
            if i == 0:
                continue
            # Clean punctuation
            clean = re.sub(r'[^a-zA-Z\'-]', '', word)
            if not clean:
                continue
            # Check if capitalized
            if clean[0].isupper() and len(clean) > 1:
                if clean not in WHITELIST:
                    proper_nouns.add(clean)

    return proper_nouns


def extract_known_names(context_files):
    """Extract all proper nouns and names from context files."""
    known = set()

    for filepath in context_files:
        if not os.path.exists(filepath):
            continue

        if filepath.endswith('.json'):
            with open(filepath) as f:
                data = json.load(f)
            # Extract names from state
            _extract_names_from_dict(data, known)
        else:
            with open(filepath) as f:
                text = f.read()
            # Extract all capitalized words
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            known.update(words)
            # Also extract individual words from multi-word names
            for w in words:
                known.update(w.split())

    return known


def _extract_names_from_dict(d, names):
    """Recursively extract string values that look like names."""
    if isinstance(d, dict):
        for key, val in d.items():
            if key in ('name', 'location', 'region', 'faction'):
                if isinstance(val, str):
                    names.add(val)
                    names.update(val.split())
            _extract_names_from_dict(val, names)
    elif isinstance(d, list):
        for item in d:
            _extract_names_from_dict(item, names)


def check_lore_directory(lore_dir):
    """Validate that all lore files are well-formed."""
    issues = []

    if not os.path.isdir(lore_dir):
        return [f"Lore directory not found: {lore_dir}"]

    required_sections = ["§history", "§geography", "§government", "§culture",
                         "§sensory-palette", "§voice-notes"]

    nations_dir = os.path.join(lore_dir, "nations")
    if os.path.isdir(nations_dir):
        for fname in sorted(os.listdir(nations_dir)):
            if not fname.endswith('.md') or fname == 'index.md':
                continue
            fpath = os.path.join(nations_dir, fname)
            with open(fpath) as f:
                content = f.read()

            for section in required_sections:
                if section not in content:
                    issues.append(f"{fname}: missing section {section}")

            # Check for [UNKNOWN] marker
            if "[UNKNOWN]" not in content:
                issues.append(f"{fname}: missing [UNKNOWN] marker")

    # Check for overview files
    for required_file in ["latter-earth-overview.md", "history-and-ages.md",
                          "geography.md", "languages.md"]:
        fpath = os.path.join(lore_dir, required_file)
        if not os.path.exists(fpath):
            issues.append(f"Missing lore file: {required_file}")

    return issues


def validate_narration(narration_text, context_files):
    """Check narration for ungrounded proper nouns.

    Returns:
        dict with flagged nouns and verdict
    """
    narration_nouns = extract_proper_nouns(narration_text)
    context_names = extract_known_names(context_files)

    ungrounded = narration_nouns - context_names - WHITELIST
    grounded = narration_nouns & context_names

    return {
        "total_proper_nouns": len(narration_nouns),
        "grounded": len(grounded),
        "ungrounded": len(ungrounded),
        "flagged_nouns": sorted(ungrounded),
        "verdict": "PASS" if len(ungrounded) == 0 else "REVIEW",
        "message": (
            "All proper nouns grounded in context" if len(ungrounded) == 0
            else f"{len(ungrounded)} potentially hallucinated noun(s): {', '.join(sorted(ungrounded))}"
        ),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_narration_grounding.py <narration_file> <context_files...>")
        print("       validate_narration_grounding.py --check-lore-dir <lore_dir>")
        sys.exit(1)

    if sys.argv[1] == "--check-lore-dir":
        lore_dir = sys.argv[2] if len(sys.argv) > 2 else "runtime/phases/1-context-loading/lore"
        issues = check_lore_directory(lore_dir)
        if issues:
            print(f"Found {len(issues)} lore issue(s):")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("All lore files validated successfully.")
            sys.exit(0)

    narration_file = sys.argv[1]
    context_files = sys.argv[2:]

    with open(narration_file) as f:
        narration_text = f.read()

    result = validate_narration(narration_text, context_files)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
