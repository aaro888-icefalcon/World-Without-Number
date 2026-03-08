"""WWN scene generation — create playable scenes from tags and tables.

Combines multiple tags to create emergent scene seeds.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
if _tables_dir not in sys.path:
    sys.path.insert(0, _tables_dir)


def _load_tags(tag_type):
    """Load tags from the appropriate table module."""
    try:
        if tag_type == "wilderness":
            from wilderness_tags import WILDERNESS_TAGS
            return WILDERNESS_TAGS
        elif tag_type == "ruin":
            from ruin_tags import RUIN_TAGS
            return RUIN_TAGS
        elif tag_type == "community":
            from community_tags import COMMUNITY_TAGS
            return COMMUNITY_TAGS
    except ImportError:
        pass
    return []


def generate_scene(scene_type, tag_count, threat_level):
    """Generate a scene seed from tags.

    Args:
        scene_type: "wilderness", "ruin", or "community"
        tag_count: number of tags to combine (recommended: 2)
        threat_level: overall threat level (1-10)

    Returns:
        dict with scene seed, selected tags, combined elements
    """
    tags = _load_tags(scene_type)

    if not tags:
        # Fallback if no tags extracted yet
        return _generate_fallback_scene(scene_type, threat_level)

    tag_count = min(tag_count, len(tags))
    selected_tags = random.sample(tags, tag_count)

    # Combine tag elements
    enemies = []
    friends = []
    complications = []
    things = []
    places = []

    for tag in selected_tags:
        if tag.get("enemies"):
            enemies.append(tag["enemies"])
        if tag.get("friends"):
            friends.append(tag["friends"])
        if tag.get("complications"):
            complications.append(tag["complications"])
        if tag.get("things"):
            things.append(tag["things"])
        if tag.get("places"):
            places.append(tag["places"])

    return {
        "scene_type": scene_type,
        "threat_level": threat_level,
        "tags_used": [t["name"] for t in selected_tags],
        "tag_details": selected_tags,
        "combined_elements": {
            "enemies": enemies,
            "friends": friends,
            "complications": complications,
            "things": things,
            "places": places,
        },
        "scene_seed": _build_scene_seed(selected_tags, scene_type, threat_level),
        "arithmetic_trace": f"Scene ({scene_type}): {tag_count} tags, threat {threat_level}",
    }


def _build_scene_seed(tags, scene_type, threat_level):
    """Build a narrative seed from combined tags."""
    tag_names = [t["name"] for t in tags]
    descriptions = [t.get("description", "") for t in tags if t.get("description")]

    seed = f"A {scene_type} scene combining: {', '.join(tag_names)}."
    if descriptions:
        seed += " " + " ".join(descriptions[:2])

    return seed


def _generate_fallback_scene(scene_type, threat_level):
    """Generate a basic scene without tags (fallback for unextracted content)."""
    fallback_scenes = {
        "wilderness": [
            "A clearing in dense woodland, old stone markers half-hidden in the undergrowth.",
            "A rocky hilltop with commanding views of the surrounding lands.",
            "A dried riverbed winding through scrubland, with animal tracks everywhere.",
            "A natural cave mouth in a cliff face, dark and unwelcoming.",
        ],
        "ruin": [
            "Crumbling stone walls mark the outline of an ancient structure.",
            "A partially collapsed tower, its upper floors open to the sky.",
            "An underground chamber, accessible through a broken floor.",
            "An overgrown courtyard with a dry fountain at its center.",
        ],
        "community": [
            "A small village with a handful of timber buildings around a central well.",
            "A fortified trading post at a crossroads.",
            "A riverside hamlet with a ferry crossing.",
            "A hillside settlement built into terraced slopes.",
        ],
    }

    descriptions = fallback_scenes.get(scene_type, fallback_scenes["wilderness"])
    desc = random.choice(descriptions)

    return {
        "scene_type": scene_type,
        "threat_level": threat_level,
        "tags_used": ["fallback"],
        "tag_details": [],
        "combined_elements": {
            "enemies": [], "friends": [], "complications": [],
            "things": [], "places": [],
        },
        "scene_seed": desc,
        "arithmetic_trace": f"Fallback scene ({scene_type}), threat {threat_level}",
    }


def generate_ruin(depth_level, tag_count=2):
    """Generate a dungeon/ruin exploration scene.

    Args:
        depth_level: how deep into the ruin (affects threat and treasure)
        tag_count: number of ruin tags to use

    Returns:
        dict with ruin scene details
    """
    threat_level = min(10, depth_level + 2)
    scene = generate_scene("ruin", tag_count, threat_level)
    scene["depth_level"] = depth_level
    scene["has_treasure"] = random.random() < (0.3 + depth_level * 0.1)
    return scene
