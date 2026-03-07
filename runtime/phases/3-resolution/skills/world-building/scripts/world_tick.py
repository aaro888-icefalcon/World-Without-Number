"""WWN world tick — advance the world between sessions.

Processes clocks, generates events, updates world pulse.
"""

import sys
import os
import random

_this_dir = os.path.dirname(os.path.abspath(__file__))
_core_scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))),
                             "core", "scripts")
if _core_scripts not in sys.path:
    sys.path.insert(0, _core_scripts)

from dice import roll_dice


# Rumor templates for world pulse generation
RUMOR_TEMPLATES = [
    "Travelers speak of {event} in the {direction}.",
    "A merchant claims that {event}.",
    "The locals whisper about {event}.",
    "A drunk soldier let slip that {event}.",
    "A peddler brings word of {event} from afar.",
]

EVENTS = [
    "bandits raiding caravans",
    "strange lights in the ruins",
    "a noble's sudden death",
    "crop failure threatening famine",
    "a new vein of silver discovered",
    "refugees fleeing some unknown terror",
    "a holy festival drawing pilgrims",
    "soldiers mustering for war",
    "a plague in a neighboring settlement",
    "an ancient tomb unearthed by storms",
    "a merchant guild raising prices",
    "a sorcerer taking up residence",
]

DIRECTIONS = ["north", "south", "east", "west", "nearby borderlands",
              "coastal settlements", "mountain passes"]


def advance_clocks(clocks, days_elapsed):
    """Advance clock-based events.

    Returns list of clock updates and any triggered events.
    """
    updates = []
    triggered = []

    for clock in clocks:
        if clock.get("status") != "active":
            continue

        # Clocks advance based on their pace (default: 1 per 7 days)
        pace = clock.get("pace_days", 7)
        ticks = days_elapsed // pace

        if ticks > 0:
            old_value = clock["current"]
            new_value = min(clock["max"], old_value + ticks)
            clock["current"] = new_value

            updates.append({
                "clock": clock["name"],
                "old": old_value,
                "new": new_value,
                "change": new_value - old_value,
            })

            # Check portents
            for portent in clock.get("portents", []):
                if not portent.get("fired") and portent["at"] <= new_value:
                    portent["fired"] = True
                    triggered.append({
                        "clock": clock["name"],
                        "portent": portent["event"],
                        "mechanical": portent.get("mechanical", ""),
                    })

            # Check completion
            if new_value >= clock["max"]:
                clock["status"] = "completed"
                triggered.append({
                    "clock": clock["name"],
                    "event": "COMPLETED",
                    "effect": clock.get("completion_effect", "Clock completed."),
                })

    return {"updates": updates, "triggered": triggered}


def generate_world_pulse(current_day, clocks, faction_count):
    """Generate world pulse — news, rumors, trends for the world.

    Returns dict suitable for state.json world_pulse field.
    """
    news = ""
    rumors = []
    trends = []
    arrivals = []

    # Generate 1-3 rumors
    rumor_count = random.randint(1, 3)
    for _ in range(rumor_count):
        template = random.choice(RUMOR_TEMPLATES)
        event = random.choice(EVENTS)
        direction = random.choice(DIRECTIONS)
        rumor = template.format(event=event, direction=direction)
        rumors.append(rumor)

    # Generate news from clock events
    for clock in clocks:
        if clock.get("status") == "completed":
            news = f"Word has spread: {clock.get('completion_effect', clock['name'] + ' has concluded')}."
            break

    if not news:
        news = random.choice([
            "The roads are quiet.",
            "Trade continues as usual.",
            "The weather has been unremarkable.",
            "No major news reaches this far.",
        ])

    return {
        "day": current_day,
        "news": news,
        "rumors": rumors,
        "trends": trends,
        "arrivals": arrivals,
    }


def advance_world(days_elapsed, clocks, factions, current_day):
    """Main world tick entry point.

    Args:
        days_elapsed: how many in-game days have passed
        clocks: list of clock dicts from state.json
        factions: list of faction dicts from state.json
        current_day: current campaign day

    Returns:
        dict with all world advancement results
    """
    clock_results = advance_clocks(clocks, days_elapsed)
    world_pulse = generate_world_pulse(
        current_day + days_elapsed, clocks, len(factions))

    return {
        "days_elapsed": days_elapsed,
        "new_day": current_day + days_elapsed,
        "clock_updates": clock_results["updates"],
        "triggered_events": clock_results["triggered"],
        "world_pulse": world_pulse,
        "arithmetic_trace": f"World tick: {days_elapsed} days, {len(clock_results['updates'])} clock(s) advanced, {len(clock_results['triggered'])} event(s) triggered",
    }
