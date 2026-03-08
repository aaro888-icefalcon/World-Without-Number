"""WWN world-building society and culture tables.

Society types, cultural features, and taboos for procedural settlement
and civilization generation. No external dependencies.
"""

# Each entry: type, description, values, customs
SOCIETY_TYPES = [
    {
        "type": "Warrior Culture",
        "description": "Martial prowess defines social standing; honor is won and lost in combat.",
        "values": ["courage", "personal honor", "martial skill"],
        "customs": ["ritual dueling", "war trophies displayed publicly", "scars as marks of status"],
    },
    {
        "type": "Merchant Society",
        "description": "Trade and commerce are the highest callings; wealth confers respect.",
        "values": ["enterprise", "fair dealing", "prosperity"],
        "customs": ["elaborate trade rituals", "contract oaths before witnesses", "merchant festivals"],
    },
    {
        "type": "Agrarian Commune",
        "description": "The community revolves around the land and its seasons; cooperation is paramount.",
        "values": ["community", "hard work", "tradition"],
        "customs": ["harvest celebrations", "communal land stewardship", "seasonal rites"],
    },
    {
        "type": "Scholar Society",
        "description": "Knowledge and learning are the most respected pursuits; literacy is universal.",
        "values": ["wisdom", "education", "intellectual achievement"],
        "customs": ["public debates", "apprenticeship traditions", "great libraries open to all"],
    },
    {
        "type": "Nomadic Herders",
        "description": "The people follow their herds across vast territories, valuing mobility and kinship.",
        "values": ["hospitality", "freedom", "kinship"],
        "customs": ["seasonal migrations", "guest-right obligations", "mounted competitions"],
    },
    {
        "type": "Seafaring Culture",
        "description": "The ocean defines life; sailors, fishers, and navigators hold the highest status.",
        "values": ["daring", "self-reliance", "exploration"],
        "customs": ["boat-naming ceremonies", "tide-reading traditions", "sea burials"],
    },
    {
        "type": "Caste Society",
        "description": "Birth determines social role; each caste has defined duties and privileges.",
        "values": ["duty", "order", "purity"],
        "customs": ["caste-specific dress codes", "arranged marriages within caste", "ritual purification"],
    },
    {
        "type": "Artisan Guild Culture",
        "description": "Craft mastery is the path to respect; guilds organize all economic and social life.",
        "values": ["craftsmanship", "innovation", "guild solidarity"],
        "customs": ["masterwork examinations", "guild feast days", "journeyman wandering years"],
    },
    {
        "type": "Ascetic Society",
        "description": "Simplicity and self-denial are virtues; excess is viewed with suspicion.",
        "values": ["discipline", "humility", "spiritual purity"],
        "customs": ["fasting periods", "plain dress requirements", "communal meals"],
    },
    {
        "type": "Hedonistic Culture",
        "description": "Pleasure, beauty, and artistic expression are celebrated as the highest goods.",
        "values": ["beauty", "pleasure", "artistic expression"],
        "customs": ["grand festivals", "patronage of artists", "elaborate cuisine traditions"],
    },
    {
        "type": "Ancestor-Veneration Society",
        "description": "The dead are honored as guides and protectors; lineage defines identity.",
        "values": ["filial piety", "continuity", "remembrance"],
        "customs": ["ancestor shrines in every home", "genealogy recitations", "memorial feasts"],
    },
    {
        "type": "Egalitarian Collective",
        "description": "All members share equal voice; hierarchy is actively resisted.",
        "values": ["equality", "consensus", "mutual aid"],
        "customs": ["rotating leadership duties", "shared meals", "public grievance circles"],
    },
    {
        "type": "Honor-Bound Clans",
        "description": "Extended family clans are the primary social unit; blood debts and alliances shape life.",
        "values": ["loyalty", "clan honor", "reciprocity"],
        "customs": ["blood oaths", "clan tartans or sigils", "vendetta obligations"],
    },
    {
        "type": "Survivalist Enclave",
        "description": "Harsh conditions have forged a pragmatic people who value preparedness above all.",
        "values": ["resourcefulness", "toughness", "pragmatism"],
        "customs": ["stockpiling traditions", "coming-of-age survival trials", "waste taboos"],
    },
    {
        "type": "Mystical Society",
        "description": "Daily life is suffused with magical practice; the mundane and arcane are inseparable.",
        "values": ["arcane knowledge", "harmony with magic", "spiritual insight"],
        "customs": ["daily cantrip rituals", "ley-line pilgrimages", "enchanted household tools"],
    },
    {
        "type": "Bureaucratic Meritocracy",
        "description": "Examinations and demonstrated competence determine social rank and office.",
        "values": ["merit", "order", "public service"],
        "customs": ["civil examinations", "ranked insignia of office", "public posting of results"],
    },
    {
        "type": "Pastoral Theists",
        "description": "Religious devotion and simple rural life are intertwined; clergy guide daily affairs.",
        "values": ["faith", "simplicity", "obedience"],
        "customs": ["dawn prayers", "tithe obligations", "saint-day celebrations"],
    },
    {
        "type": "Cosmopolitan Melting Pot",
        "description": "Diverse peoples mix freely; cultural borrowing and adaptation are the norm.",
        "values": ["tolerance", "adaptability", "curiosity"],
        "customs": ["multilingual signage", "fusion cuisine", "cross-cultural festivals"],
    },
]

# Distinctive cultural features — roll or choose one or more
CULTURAL_FEATURES = [
    "Elaborate tattoo or scarification traditions mark life milestones.",
    "A unique musical instrument is central to ceremonies and communication.",
    "An annual grand tournament determines political or social standing.",
    "Architecture incorporates living plants or trees as structural elements.",
    "A complex sign language supplements spoken communication.",
    "Masks are worn during all formal occasions; faces are private.",
    "Cooking is considered a sacred art; master chefs hold priestly status.",
    "Children are raised communally rather than by individual families.",
    "Colors carry strict social meaning; wearing the wrong hue is an offense.",
    "All adults carry a personal weapon as a symbol of citizenship.",
    "Storytelling competitions are the primary form of entertainment.",
    "Names are earned through deeds; birth names are never used publicly.",
    "Animals are considered legal persons with defined rights.",
    "Dream interpretation guides major community decisions.",
    "A distinctive hat or headcovering signals profession and rank.",
    "Silence is valued; unnecessary speech is considered rude.",
    "Elaborate greeting rituals take several minutes to complete.",
    "The dead are honored with month-long mourning periods.",
    "Public baths serve as the primary social gathering place.",
    "Gift-giving follows rigid reciprocal rules that outsiders find baffling.",
]

# Cultural taboos — roll or choose
TABOOS = [
    "Eating meat from a specific animal considered sacred or unclean.",
    "Speaking the names of the recently dead.",
    "Entering a dwelling without removing footwear.",
    "Refusing offered food or drink from a host.",
    "Using the left hand for formal gestures or eating.",
    "Cutting one's hair before a certain age or life event.",
    "Displaying open anger or raising one's voice in public.",
    "Touching someone's head, considered the seat of the soul.",
    "Working or trading on holy days.",
    "Whistling after dark, believed to summon malevolent spirits.",
    "Wearing a specific color reserved for royalty or clergy.",
    "Pointing at the moon or stars with a bare finger.",
    "Spilling salt, considered an invitation to misfortune.",
    "Marrying outside one's social class or clan.",
    "Speaking during meals; eating is a meditative act.",
    "Killing spiders, believed to be messengers of the gods.",
    "Building structures taller than the local temple or shrine.",
    "Turning one's back on a fire, seen as disrespecting the hearth spirits.",
    "Writing down certain sacred words; they may only be spoken aloud.",
    "Allowing blood to touch bare earth; it must be caught on cloth or stone.",
]
