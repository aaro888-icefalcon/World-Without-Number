"""Court intrigue environment tags for political and social encounter generation.

Provides tags that characterize the nature of a court, noble household, or
political body. Each tag carries an intrigue_modifier that adjusts the baseline
difficulty of social maneuvering within that environment.

Also includes a COURT_COMPLICATIONS table for injecting unexpected twists
into court-based encounters and faction interactions.
"""

COURT_TAGS = [
    {
        "tag": "Decadent",
        "description": "The court wallows in luxury and excess. Officials are easily bribed but quick to betray.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Militant",
        "description": "Military hierarchy dominates court life. Rank and martial prowess determine standing.",
        "intrigue_modifier": -1,
    },
    {
        "tag": "Scholarly",
        "description": "Learning and intellectual debate are prized. Arguments must be well-reasoned to gain traction.",
        "intrigue_modifier": 0,
    },
    {
        "tag": "Corrupt",
        "description": "Graft and bribery are the accepted currency of influence. Everyone has a price.",
        "intrigue_modifier": 2,
    },
    {
        "tag": "Theocratic",
        "description": "Religious authority intertwines with secular power. Piety opens doors; heresy closes them permanently.",
        "intrigue_modifier": 0,
    },
    {
        "tag": "Paranoid",
        "description": "The ruler trusts no one. Spies watch spies, and loyalty is tested constantly.",
        "intrigue_modifier": 3,
    },
    {
        "tag": "Mercantile",
        "description": "Commerce drives politics. Wealth speaks louder than blood or blade.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Feuding",
        "description": "Rival factions within the court are locked in open hostility. Neutrality is impossible.",
        "intrigue_modifier": 2,
    },
    {
        "tag": "Traditionalist",
        "description": "Ancient customs and precedent govern all decisions. Innovation is viewed with deep suspicion.",
        "intrigue_modifier": -1,
    },
    {
        "tag": "Progressive",
        "description": "The court embraces reform and new ideas. Old guard members resist from the shadows.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Puppet regime",
        "description": "The nominal ruler is controlled by a hidden power. Real decisions happen behind closed doors.",
        "intrigue_modifier": 3,
    },
    {
        "tag": "Meritocratic",
        "description": "Competence and results determine advancement. Birth and connections matter less than ability.",
        "intrigue_modifier": -2,
    },
    {
        "tag": "Xenophobic",
        "description": "Outsiders are distrusted or despised. Foreigners face steep barriers to acceptance.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Cosmopolitan",
        "description": "The court welcomes diverse peoples and ideas. Multiple factions compete for cultural dominance.",
        "intrigue_modifier": 0,
    },
    {
        "tag": "Dying dynasty",
        "description": "The ruling line is failing. Succession crises loom, and ambitious nobles position themselves.",
        "intrigue_modifier": 3,
    },
    {
        "tag": "Newly established",
        "description": "The current regime recently seized power. Loyalties are uncertain and old allegiances dangerous.",
        "intrigue_modifier": 2,
    },
    {
        "tag": "Isolationist",
        "description": "The court shuns foreign entanglements and turns inward. External threats are ignored or denied.",
        "intrigue_modifier": -1,
    },
    {
        "tag": "Expansionist",
        "description": "The court is focused on conquest and growth. Hawks dominate policy and doves are marginalized.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Bureaucratic",
        "description": "Layers of administrators and functionaries control access to power. Procedure trumps personality.",
        "intrigue_modifier": 0,
    },
    {
        "tag": "Secretive",
        "description": "Court business is conducted behind veils of secrecy. Information is the most valuable commodity.",
        "intrigue_modifier": 2,
    },
    {
        "tag": "Festive",
        "description": "Endless celebrations, tournaments, and gatherings mask the serious business of politics beneath.",
        "intrigue_modifier": 1,
    },
    {
        "tag": "Austere",
        "description": "The court operates with grim frugality. Displays of wealth are frowned upon or forbidden.",
        "intrigue_modifier": -1,
    },
    {
        "tag": "Haunted",
        "description": "Supernatural forces or ancient curses influence court politics. Fear shapes every decision.",
        "intrigue_modifier": 2,
    },
    {
        "tag": "Enlightened",
        "description": "The ruler genuinely seeks the common good. Corruption exists but is actively opposed.",
        "intrigue_modifier": -2,
    },
    {
        "tag": "Tyrannical",
        "description": "Rule by fear and absolute authority. Dissent is crushed and obedience is the only virtue.",
        "intrigue_modifier": 2,
    },
]

COURT_COMPLICATIONS = [
    {
        "complication": "Assassination attempt",
        "description": "Someone tries to kill a key figure, throwing the court into chaos and suspicion.",
    },
    {
        "complication": "Forbidden romance",
        "description": "A politically disastrous love affair threatens to upend alliances and enrage powerful families.",
    },
    {
        "complication": "Succession crisis",
        "description": "The heir is dead, missing, or declared unfit. Multiple claimants emerge with competing support.",
    },
    {
        "complication": "Foreign embassy",
        "description": "Diplomats from a rival power arrive with demands that split the court into factions.",
    },
    {
        "complication": "Treasury scandal",
        "description": "The coffers are empty or funds have been embezzled. Someone must take the blame.",
    },
    {
        "complication": "Religious schism",
        "description": "A doctrinal dispute divides the faithful, and both sides demand the court choose a side.",
    },
    {
        "complication": "Plague rumor",
        "description": "Reports of a deadly illness spread panic. Quarantine measures threaten trade and travel.",
    },
    {
        "complication": "Exposed spy",
        "description": "A trusted courtier is revealed as an agent of a foreign power or rival faction.",
    },
    {
        "complication": "Popular uprising",
        "description": "Common folk riot or protest, and the court must decide between concession and crackdown.",
    },
    {
        "complication": "Contested inheritance",
        "description": "A disputed estate or title drags multiple noble houses into a bitter legal and political fight.",
    },
    {
        "complication": "Magical disruption",
        "description": "Sorcery or a magical catastrophe disrupts normal court operations and terrifies the populace.",
    },
    {
        "complication": "Military defeat",
        "description": "News arrives of a disastrous battle. Blame must be assigned and a response organized.",
    },
    {
        "complication": "Secret alliance revealed",
        "description": "A hidden pact between unlikely parties comes to light, reshuffling the balance of power.",
    },
    {
        "complication": "Royal madness",
        "description": "The ruler exhibits increasingly erratic behavior. Loyalists cover while rivals circle.",
    },
    {
        "complication": "Ancient claim surfaces",
        "description": "A long-lost document or heir emerges that challenges the legitimacy of the current order.",
    },
]
