"""WWN NPC generation — create NPCs with voice cards, personality, motivation.

NPCs generated here are compatible with state.json known_npcs schema.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_tables_dir = os.path.join(os.path.dirname(_this_dir), "tables")
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
for p in [_tables_dir, _core_scripts]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dice import roll_dice, roll_check


# Name pools by region flavor
FIRST_NAMES = [
    "Aldric", "Brenna", "Callum", "Dara", "Elric", "Fenna",
    "Gareth", "Halla", "Isen", "Jora", "Kael", "Lira",
    "Maren", "Nils", "Orla", "Pell", "Riven", "Sela",
    "Thane", "Ulra", "Varn", "Wren", "Xara", "Yren", "Zara",
]

SURNAMES = [
    "Ashford", "Blackwood", "Cragborn", "Deepwell", "Ember",
    "Foxglove", "Greysteel", "Hawkridge", "Ironhand", "Kettleburn",
    "Longshore", "Moorfield", "Northwind", "Oakenshield", "Pinefall",
    "Ravenscar", "Stonewall", "Thornwick", "Underhill", "Winterborn",
]

PERSONALITY_TRAITS = [
    "cautious and observant", "bold and outspoken", "quiet and thoughtful",
    "cheerful and generous", "grim and pragmatic", "devious and charming",
    "loyal and stubborn", "nervous and talkative", "stoic and patient",
    "ambitious and cunning", "kind but naive", "bitter and resentful",
    "scholarly and absent-minded", "jovial and boisterous", "suspicious and guarded",
    "diplomatic and smooth", "blunt and honest", "melancholy and poetic",
]

SPEECH_PATTERNS = [
    "speaks in short, clipped sentences",
    "uses formal, archaic phrasing",
    "peppers speech with nautical metaphors",
    "speaks very slowly and deliberately",
    "uses trade jargon and merchant expressions",
    "speaks in the third person about themselves",
    "tends to whisper important things",
    "laughs nervously between statements",
    "uses colorful local idioms",
    "speaks with military precision",
    "frequently quotes proverbs",
    "trails off mid-sentence, then restarts",
]

KEY_PHRASES = [
    "As my grandmother used to say...",
    "Mark my words.",
    "The world is what it is.",
    "You see how it is.",
    "Fortune favors the prepared.",
    "There's always a price.",
    "In the old days...",
    "Between you and me...",
    "The gods willing.",
    "Nothing lasts forever.",
]

MOTIVATIONS = [
    "protect their family above all else",
    "accumulate wealth and influence",
    "seek revenge for a past wrong",
    "preserve ancient knowledge",
    "maintain order and stability",
    "escape their past",
    "earn glory and renown",
    "serve their faith or ideology",
    "find a cure for a loved one's illness",
    "discover the truth about a mystery",
    "gain power to change the world",
    "simply survive another day",
]

ROLES = {
    "minor": ["merchant", "farmer", "guard", "servant", "craftsperson", "beggar", "traveler"],
    "major": ["noble", "captain", "priest", "guild master", "scholar", "spy", "healer"],
    "faction_leader": ["lord", "warlord", "high priest", "archmage", "crime boss", "governor"],
}


def generate_npc(importance="minor", region="unknown", tag_count=1):
    """Generate an NPC with full voice card and personality.

    Args:
        importance: "minor", "major", or "faction_leader"
        region: region name for flavor
        tag_count: number of character tags to apply

    Returns:
        dict compatible with known_npcs schema + voice card
    """
    name = f"{random.choice(FIRST_NAMES)} {random.choice(SURNAMES)}"
    role = random.choice(ROLES.get(importance, ROLES["minor"]))
    personality = random.choice(PERSONALITY_TRAITS)
    speech = random.choice(SPEECH_PATTERNS)
    phrase = random.choice(KEY_PHRASES)
    motivation = random.choice(MOTIVATIONS)

    # Generate voice card
    voice_card = (
        f"{name} is {personality}. They {speech}. "
        f"They often say: \"{phrase}\""
    )

    # Load character tags if available
    tags = []
    try:
        from character_tags import CHARACTER_TAGS
        if CHARACTER_TAGS:
            selected = random.sample(CHARACTER_TAGS, min(tag_count, len(CHARACTER_TAGS)))
            tags = [t["tag"] if isinstance(t, dict) else str(t) for t in selected]
    except ImportError:
        pass

    npc_id = f"npc_{random.randint(100, 999)}"

    return {
        "id": npc_id,
        "name": name,
        "faction": "unaffiliated",
        "role": role,
        "disposition": "neutral",
        "status": "active",
        "last_seen": region,
        "trust": 5,
        "motivation": motivation,
        "secret": None,
        # Voice card fields (extended schema for Phase D)
        "personality_traits": personality,
        "speech_patterns": speech,
        "key_phrases": [phrase],
        "voice_card": voice_card,
        "character_tags": tags,
        "importance": importance,
        "arithmetic_trace": f"Generated NPC: {name} ({role}, {importance})",
    }


def reaction_roll(modifier=0):
    """Roll 2d6 + modifier for NPC initial reaction.

    Returns:
        dict with roll, disposition, and description
    """
    rolls = roll_dice(2, 6)
    total = sum(rolls) + modifier

    if total <= 3:
        disposition = "hostile"
        description = "Hostile — attacks if not clearly overpowered"
    elif total <= 5:
        disposition = "unfriendly"
        description = "Hostile — may attack if provoked"
    elif total <= 8:
        disposition = "uncertain"
        description = "Uncertain — can be convinced"
    elif total <= 10:
        disposition = "neutral"
        description = "Neutral — open to negotiation"
    elif total == 11:
        disposition = "friendly"
        description = "Friendly — inclined to help"
    else:
        disposition = "enthusiastic"
        description = "Enthusiastically friendly"

    return {
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "disposition": disposition,
        "description": description,
        "arithmetic_trace": f"Reaction: 2d6=[{rolls[0]}+{rolls[1]}]+{modifier} = {total} → {disposition}",
    }
