"""WWN world-building religion tables.

Religion types, practices, and clergy structures for procedural
world-building and settlement generation. No external dependencies.
"""

# Each entry: type, description, practices, leadership
RELIGION_TYPES = [
    {
        "type": "Ancestor Worship",
        "description": "The spirits of the honored dead guide and protect their descendants.",
        "practices": ["shrine maintenance", "genealogy recitation", "offering of food and drink to the dead"],
        "leadership": "Elder of the oldest lineage",
    },
    {
        "type": "Elemental Pantheon",
        "description": "Multiple gods embody the primal elements — fire, water, earth, air, and beyond.",
        "practices": ["elemental invocations", "seasonal rites tied to dominant elements", "shrine rotation"],
        "leadership": "Council of element-priests",
    },
    {
        "type": "Monotheistic Faith",
        "description": "A single omnipotent deity demands exclusive worship and moral obedience.",
        "practices": ["daily prayer cycles", "scripture study", "confession and penance"],
        "leadership": "High Patriarch or Matriarch",
    },
    {
        "type": "Mystery Cult",
        "description": "Initiates progress through secret rites that reveal hidden cosmic truths.",
        "practices": ["initiation ordeals", "secret ceremonies", "symbolic death and rebirth"],
        "leadership": "Hierophant",
    },
    {
        "type": "Nature Spirits",
        "description": "Every river, mountain, and grove has a living spirit that must be appeased.",
        "practices": ["offerings at natural sites", "taboo areas left undisturbed", "seasonal spirit-walks"],
        "leadership": "Spirit-talker or Shaman",
    },
    {
        "type": "Dead God Worship",
        "description": "The faithful serve a deity that was slain or has fallen silent, awaiting its return.",
        "practices": ["mourning rites", "relic preservation", "vigil-keeping at holy sites"],
        "leadership": "Keeper of the Vigil",
    },
    {
        "type": "Solar Cult",
        "description": "The sun is the source of all life, truth, and justice; darkness is the enemy.",
        "practices": ["dawn ceremonies", "fire-lighting rituals", "solar calendar observances"],
        "leadership": "Sun-Speaker",
    },
    {
        "type": "Dualistic Faith",
        "description": "Two opposing cosmic forces — light and dark, order and chaos — are locked in eternal struggle.",
        "practices": ["balance rituals", "purification rites", "alignment declarations"],
        "leadership": "Twin Prophets (one for each aspect)",
    },
    {
        "type": "Animism",
        "description": "All things possess a spiritual essence; harmony with the spirit world is paramount.",
        "practices": ["spirit negotiations", "totem carving", "trance journeys"],
        "leadership": "Dream-walker",
    },
    {
        "type": "Philosophical Tradition",
        "description": "Not a religion of gods but of principles — ethics, logic, and the examined life.",
        "practices": ["dialectic debates", "ethical meditation", "public lectures"],
        "leadership": "Senior Philosopher",
    },
    {
        "type": "Demon-Binding Covenant",
        "description": "The faithful bargain with infernal powers, trading service for forbidden knowledge.",
        "practices": ["pact rituals", "blood offerings", "warding circles"],
        "leadership": "Pact-Master",
    },
    {
        "type": "Machine God Cult",
        "description": "Devotees worship the remnant intelligence of a pre-collapse artificial mind.",
        "practices": ["data offerings", "ruin pilgrimages", "recitation of code-mantras"],
        "leadership": "Compiler-Priest",
    },
    {
        "type": "Stellar Worship",
        "description": "The stars and celestial bodies are living gods whose movements dictate fate.",
        "practices": ["astrology readings", "observatory maintenance", "constellation festivals"],
        "leadership": "Astronomer-Pontiff",
    },
    {
        "type": "Blood Faith",
        "description": "Sacrifice — animal or otherwise — is the central act of worship and power.",
        "practices": ["ritual sacrifice", "blood anointing", "sacred hunts"],
        "leadership": "Crimson Priest",
    },
    {
        "type": "Dream Religion",
        "description": "The dream world is the true reality; waking life is a shadow to be endured.",
        "practices": ["communal dream sessions", "sleep temples", "vision quests"],
        "leadership": "Oneiromancer",
    },
    {
        "type": "Civic Religion",
        "description": "The state itself is sacred; patriotic duty and civic virtue are acts of worship.",
        "practices": ["civic oaths", "public holidays honoring founders", "oath-bound public service"],
        "leadership": "Chief Magistrate-Priest",
    },
    {
        "type": "Totemism",
        "description": "Clans identify with sacred animals or symbols that embody their spiritual identity.",
        "practices": ["totem dances", "animal taboos", "spirit-animal quests"],
        "leadership": "Totem-keeper",
    },
    {
        "type": "Oracle Tradition",
        "description": "The divine speaks through chosen vessels; prophecy is the highest form of revelation.",
        "practices": ["oracle consultations", "prophetic trances", "interpretation debates"],
        "leadership": "Voice of the Oracle",
    },
]

# Individual religious practices that can be mixed and matched
RELIGIOUS_PRACTICES = [
    "Daily prayer at dawn and dusk.",
    "Ritual fasting during holy periods.",
    "Pilgrimage to a sacred site at least once in a lifetime.",
    "Tithing a portion of income or harvest to the temple.",
    "Wearing a specific symbol or garment as a mark of faith.",
    "Dietary restrictions forbidding specific foods.",
    "Communal worship gatherings on a fixed day of the week.",
    "Ritual purification with water, smoke, or fire before entering holy ground.",
    "Confession of transgressions to a priest or elder.",
    "Charitable obligations to the poor and sick.",
    "Memorization and recitation of sacred texts.",
    "Ritual silence during specific hours of the day.",
    "Anointing the dead with sacred oils before burial.",
    "Burning incense or herbs to carry prayers to the divine.",
    "Tattooing or branding religious symbols on the body.",
    "Observing strict celibacy during holy seasons.",
    "Maintaining a personal altar or shrine in the home.",
    "Ritual combat or athletic contests to honor the gods.",
    "Blood-letting or minor self-mortification as devotion.",
    "Singing or chanting as the only permitted form of prayer.",
]

# Clergy ranks from lowest to highest
CLERGY_RANKS = [
    "Acolyte",
    "Initiate",
    "Deacon",
    "Priest",
    "Curate",
    "Canon",
    "Abbot / Abbess",
    "Bishop",
    "Archpriest",
    "High Priest / High Priestess",
    "Pontiff",
    "Prophet",
]
