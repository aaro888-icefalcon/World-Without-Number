"""Faction action definitions for faction turns.

Defines the actions available to factions during the faction turn phase,
along with their costs, requirements, difficulty ratings, and descriptions.
Follows WWN-style faction mechanics where factions spend treasure and
use assets to pursue strategic goals.

Also includes FACTION_ASSET_TYPES categorizing the four asset domains
that factions can develop and deploy.
"""

FACTION_ACTIONS = {
    "Attack": {
        "cost": 0,
        "requirement": "At least one military or intelligence asset in the target location",
        "description": "Launch an attack against a rival faction's asset using one of your own assets. Both sides roll asset hit dice; the loser's asset takes damage.",
        "difficulty": 0,
    },
    "Defend": {
        "cost": 0,
        "requirement": "None",
        "description": "Place the faction on defensive alert. All assets gain a +2 bonus to defensive rolls until the faction's next turn.",
        "difficulty": 0,
    },
    "Expand Territory": {
        "cost": 2,
        "requirement": "An asset present in the target location or an adjacent location",
        "description": "Extend the faction's sphere of influence into a new territory. Opposed by any faction that already controls the area.",
        "difficulty": 8,
    },
    "Recruit Assets": {
        "cost": 1,
        "requirement": "Control of a territory with a suitable population",
        "description": "Gather new followers, soldiers, or agents from controlled territory to form a new minor asset.",
        "difficulty": 6,
    },
    "Create Asset": {
        "cost": "Varies by asset type",
        "requirement": "Sufficient treasure and a controlled territory of the required type",
        "description": "Invest resources to build a new asset from scratch. Cost and time depend on the asset's tier and type.",
        "difficulty": 0,
    },
    "Sell Asset": {
        "cost": 0,
        "requirement": "Ownership of the asset to be sold",
        "description": "Liquidate an existing asset for half its creation cost in treasure, rounded down.",
        "difficulty": 0,
    },
    "Seize Initiative": {
        "cost": 3,
        "requirement": "None",
        "description": "Spend resources to act first in the next faction turn, gaining priority over all other factions.",
        "difficulty": 0,
    },
    "Hire Mercenaries": {
        "cost": 4,
        "requirement": "Access to a settlement with a mercenary market",
        "description": "Recruit a temporary military asset that serves for one faction turn. The mercenaries disband afterward unless re-hired.",
        "difficulty": 6,
    },
    "Sabotage": {
        "cost": 2,
        "requirement": "An intelligence asset in the target location",
        "description": "Attempt to damage or destroy an enemy asset through covert action. The intelligence asset rolls against the target's defenses.",
        "difficulty": 10,
    },
    "Diplomacy": {
        "cost": 1,
        "requirement": "A social asset or leader present in the same location as the target faction",
        "description": "Initiate negotiations with another faction. Success can produce treaties, truces, trade agreements, or mutual aid pacts.",
        "difficulty": 8,
    },
    "Build Infrastructure": {
        "cost": 5,
        "requirement": "Control of the territory where construction occurs",
        "description": "Construct a lasting improvement in controlled territory: roads, fortifications, markets, or temples that provide ongoing benefits.",
        "difficulty": 6,
    },
    "Gather Intelligence": {
        "cost": 1,
        "requirement": "An intelligence asset in the target location",
        "description": "Attempt to learn details about a rival faction's assets, plans, treasure, or hidden weaknesses.",
        "difficulty": 8,
    },
    "Relocate Asset": {
        "cost": 1,
        "requirement": "Ownership of the asset and a viable route to the destination",
        "description": "Move an existing asset from one location to another. Military assets move slowly; intelligence assets move quickly.",
        "difficulty": 0,
    },
    "Establish Trade Route": {
        "cost": 3,
        "requirement": "An economic asset in both the origin and destination locations",
        "description": "Create a commercial link between two locations that generates ongoing treasure income each faction turn.",
        "difficulty": 8,
    },
    "Spread Propaganda": {
        "cost": 2,
        "requirement": "A social asset in the target location",
        "description": "Attempt to shift public opinion in a territory. Success can weaken rival factions' social assets or bolster your own influence.",
        "difficulty": 8,
    },
    "Forge Alliance": {
        "cost": 2,
        "requirement": "Prior successful Diplomacy action with the target faction",
        "description": "Formalize a lasting alliance with another faction, enabling coordinated actions and mutual defense agreements.",
        "difficulty": 10,
    },
    "Purge Traitors": {
        "cost": 2,
        "requirement": "An intelligence asset in your own territory",
        "description": "Root out enemy spies and subversive elements within your own faction. Removes enemy intelligence assets on a success.",
        "difficulty": 10,
    },
    "Raise Levy": {
        "cost": 1,
        "requirement": "Control of a territory with a population center",
        "description": "Call up a temporary militia force from the local population. Cheaper than mercenaries but weaker and temporary.",
        "difficulty": 4,
    },
}

FACTION_ASSET_TYPES = {
    "military": {
        "description": "Armed forces, fortifications, and war material used for direct confrontation and territorial control.",
        "examples": [
            {"name": "Militia", "tier": 1, "cost": 2, "hp": 4, "attack": "d6", "defense": "d6"},
            {"name": "Soldiers", "tier": 2, "cost": 4, "hp": 6, "attack": "d8", "defense": "d6"},
            {"name": "Elite Warriors", "tier": 3, "cost": 8, "hp": 8, "attack": "d10", "defense": "d8"},
            {"name": "Fortification", "tier": 2, "cost": 6, "hp": 10, "attack": "None", "defense": "d10"},
            {"name": "War Fleet", "tier": 3, "cost": 10, "hp": 8, "attack": "d10", "defense": "d6"},
            {"name": "Siege Engines", "tier": 3, "cost": 8, "hp": 4, "attack": "d12", "defense": "d4"},
        ],
    },
    "economic": {
        "description": "Trade networks, markets, resource extraction, and financial instruments that generate and manage treasure.",
        "examples": [
            {"name": "Market Stall", "tier": 1, "cost": 2, "hp": 2, "income": 1},
            {"name": "Trade House", "tier": 2, "cost": 5, "hp": 4, "income": 2},
            {"name": "Merchant Guild", "tier": 3, "cost": 10, "hp": 6, "income": 4},
            {"name": "Mine", "tier": 2, "cost": 6, "hp": 4, "income": 2},
            {"name": "Smuggling Ring", "tier": 2, "cost": 4, "hp": 3, "income": 3},
            {"name": "Banking House", "tier": 3, "cost": 12, "hp": 4, "income": 5},
        ],
    },
    "intelligence": {
        "description": "Spy networks, informants, saboteurs, and covert operatives used for information gathering and subversion.",
        "examples": [
            {"name": "Informers", "tier": 1, "cost": 2, "hp": 2, "attack": "d4", "stealth": 1},
            {"name": "Spy Network", "tier": 2, "cost": 5, "hp": 3, "attack": "d6", "stealth": 2},
            {"name": "Master Assassin", "tier": 3, "cost": 8, "hp": 4, "attack": "d10", "stealth": 3},
            {"name": "Saboteurs", "tier": 2, "cost": 4, "hp": 3, "attack": "d8", "stealth": 2},
            {"name": "Counterintelligence", "tier": 2, "cost": 5, "hp": 4, "attack": "d4", "stealth": 1},
            {"name": "Shadow Court", "tier": 3, "cost": 10, "hp": 5, "attack": "d8", "stealth": 3},
        ],
    },
    "social": {
        "description": "Reputation, religious authority, popular support, and cultural influence used to shape public opinion and legitimacy.",
        "examples": [
            {"name": "Popular Support", "tier": 1, "cost": 2, "hp": 3, "influence": 1},
            {"name": "Temple", "tier": 2, "cost": 5, "hp": 5, "influence": 2},
            {"name": "Court Patronage", "tier": 2, "cost": 4, "hp": 3, "influence": 2},
            {"name": "Propaganda Network", "tier": 2, "cost": 4, "hp": 2, "influence": 3},
            {"name": "Cultural Icon", "tier": 3, "cost": 8, "hp": 4, "influence": 4},
            {"name": "Holy Order", "tier": 3, "cost": 10, "hp": 6, "influence": 3},
        ],
    },
}
