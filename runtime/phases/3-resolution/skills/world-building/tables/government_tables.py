"""WWN world-building government tables.

Government types, generation tables, and complications for procedural
settlement and polity creation. No external dependencies.
"""

# Each entry: type, description, stability_modifier, traits
GOVERNMENT_TYPES = [
    {
        "type": "Monarchy",
        "description": "A single hereditary ruler holds supreme authority, supported by a court of nobles and advisors.",
        "stability_modifier": 1,
        "traits": ["hereditary succession", "noble court", "royal decree"],
    },
    {
        "type": "Oligarchy",
        "description": "A small group of wealthy or influential families share power among themselves.",
        "stability_modifier": 0,
        "traits": ["ruling families", "factional politics", "wealth-based authority"],
    },
    {
        "type": "Theocracy",
        "description": "Religious leaders govern in the name of a deity or spiritual principle.",
        "stability_modifier": 1,
        "traits": ["divine mandate", "temple law", "priestly hierarchy"],
    },
    {
        "type": "Republic",
        "description": "Elected or appointed representatives govern on behalf of the citizenry.",
        "stability_modifier": 0,
        "traits": ["elected officials", "civic debate", "public assemblies"],
    },
    {
        "type": "Military Junta",
        "description": "A council of military officers rules through martial authority.",
        "stability_modifier": -1,
        "traits": ["martial law", "officer caste", "conscription"],
    },
    {
        "type": "Merchant Council",
        "description": "A council of guild masters and trade magnates directs policy for commercial advantage.",
        "stability_modifier": 0,
        "traits": ["trade guilds", "commercial law", "market regulation"],
    },
    {
        "type": "Tribal Confederation",
        "description": "Multiple clans or tribes unite under a shared council or paramount chief.",
        "stability_modifier": -1,
        "traits": ["clan elders", "tribal moots", "kinship bonds"],
    },
    {
        "type": "Magocracy",
        "description": "Sorcerers or arcanists rule by virtue of their magical power and knowledge.",
        "stability_modifier": 0,
        "traits": ["arcane hierarchy", "spell-law", "magical infrastructure"],
    },
    {
        "type": "Feudal",
        "description": "A lord grants land to vassals in exchange for military service and loyalty.",
        "stability_modifier": 1,
        "traits": ["vassalage", "land grants", "oaths of fealty"],
    },
    {
        "type": "Imperial Province",
        "description": "A distant empire administers this region through appointed governors.",
        "stability_modifier": 1,
        "traits": ["imperial governor", "tribute obligations", "distant authority"],
    },
    {
        "type": "Free City",
        "description": "An independent city-state governed by its own charter and civic institutions.",
        "stability_modifier": 0,
        "traits": ["city charter", "civic militia", "urban autonomy"],
    },
    {
        "type": "Despotism",
        "description": "A single tyrant rules through personal power, fear, and a network of enforcers.",
        "stability_modifier": -2,
        "traits": ["secret police", "personality cult", "arbitrary justice"],
    },
    {
        "type": "Elected Chieftain",
        "description": "A war-leader or chief is chosen by the community and may be deposed by them.",
        "stability_modifier": 0,
        "traits": ["popular mandate", "limited tenure", "warrior prestige"],
    },
    {
        "type": "Bureaucratic State",
        "description": "A class of trained administrators manages governance through codified procedures.",
        "stability_modifier": 2,
        "traits": ["civil examinations", "record-keeping", "departmental hierarchy"],
    },
    {
        "type": "Anarchic Commune",
        "description": "No formal government exists; decisions are made by consensus or local custom.",
        "stability_modifier": -2,
        "traits": ["consensus rule", "mutual aid", "no standing authority"],
    },
    {
        "type": "Diarchy",
        "description": "Two co-rulers share power, often balancing military and civil authority.",
        "stability_modifier": 0,
        "traits": ["dual authority", "balanced powers", "co-rule traditions"],
    },
    {
        "type": "Necrocracy",
        "description": "The undead or the spirits of the dead hold formal authority over the living.",
        "stability_modifier": 1,
        "traits": ["ancestor edicts", "deathless rulers", "mortuary law"],
    },
    {
        "type": "Kritarchy",
        "description": "Judges or legal scholars rule by interpreting a foundational code of law.",
        "stability_modifier": 1,
        "traits": ["judicial supremacy", "legal precedent", "courts of appeal"],
    },
]

# Complications that may affect a government — roll or choose
GOVERNMENT_COMPLICATIONS = [
    "The current ruler is a figurehead controlled by a hidden power behind the throne.",
    "A succession crisis looms as multiple claimants vie for authority.",
    "Corruption is endemic; officials openly sell favors and offices.",
    "A recent coup has left the government fragile and distrusted.",
    "A powerful external patron props up the government in exchange for concessions.",
    "The treasury is nearly empty, forcing desperate measures.",
    "A popular reform movement threatens to overturn the existing order.",
    "Religious authorities contest the government's legitimacy.",
    "A separatist region or faction demands independence.",
    "The military is loyal to its own commanders rather than the state.",
    "A prophecy or omen has shaken public confidence in the rulers.",
    "Foreign spies have infiltrated key positions of power.",
    "Ancient laws grant unexpected rights that complicate modern governance.",
    "A charismatic demagogue is rallying the common people against the elite.",
    "The government depends on a magical resource that is becoming scarce.",
    "Two branches of the ruling family are locked in a bitter feud.",
    "The previous ruler vanished under mysterious circumstances.",
    "A secret society manipulates policy from the shadows.",
    "Border wars drain resources and attention from internal governance.",
    "The ruler is competent but deeply unpopular for personal reasons.",
]
