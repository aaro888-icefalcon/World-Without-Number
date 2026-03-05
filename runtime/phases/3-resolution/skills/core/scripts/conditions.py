"""WWN status effects and System Strain tracking.

System Strain is the primary throttle on magical healing in WWN.
Max System Strain = Constitution score. When maxed, no further magical healing.
"""


class SystemStrain:
    """Track a character's System Strain pool."""

    def __init__(self, max_strain):
        self.max = max_strain
        self.current = 0

    def add(self, amount):
        """Add System Strain. Returns actual amount added (may be capped)."""
        actual = min(amount, self.max - self.current)
        self.current += actual
        return actual

    def remove(self, amount):
        """Remove System Strain (e.g., from rest). Returns actual amount removed."""
        actual = min(amount, self.current)
        self.current -= actual
        return actual

    def can_heal(self):
        """Whether magical healing can be applied (strain not maxed)."""
        return self.current < self.max

    def to_dict(self):
        return {"current": self.current, "max": self.max}

    @classmethod
    def from_dict(cls, d):
        ss = cls(max_strain=d["max"])
        ss.current = d["current"]
        return ss


# Named conditions and their mechanical effects
CONDITION_EFFECTS = {
    "poisoned": {
        "description": "Suffering from poison effects",
        "effect": "Varies by poison type. Common: -2 to all checks, or ongoing damage per round.",
        "removal": "Physical saving throw at end of each scene, or Heal skill check (difficulty varies)",
    },
    "prone": {
        "description": "Lying on the ground",
        "effect": "+2 to be hit in melee, -2 to be hit at range. -4 to melee attacks. Must use Move action to stand.",
        "removal": "Stand up (costs Move action)",
    },
    "grappled": {
        "description": "Held by an opponent",
        "effect": "Cannot move. -2 to attacks. Can attempt to break free (opposed Str/Punch or Str/Exert).",
        "removal": "Win opposed check or grappler releases",
    },
    "stunned": {
        "description": "Dazed and unable to act",
        "effect": "Cannot take Main or Move actions. -2 AC.",
        "removal": "Ends at start of next turn unless otherwise specified",
    },
    "blinded": {
        "description": "Cannot see",
        "effect": "-4 to attack rolls. Enemies have +2 to hit you. Cannot target ranged attacks beyond Near zone.",
        "removal": "Depends on source. Heal check or specific cure.",
    },
    "frightened": {
        "description": "Overcome with fear",
        "effect": "Must use Move action to flee from source of fear. -2 to attacks and checks.",
        "removal": "Mental saving throw at end of each round",
    },
    "mortally_wounded": {
        "description": "At 0 HP, dying",
        "effect": "Unconscious. Will die at end of 6th round unless stabilized.",
        "removal": "Ally succeeds Dex/Heal or Int/Heal check (difficulty 8) as Main Action. Stabilized at 1 HP.",
        "rounds_to_death": 6,
    },
}


def apply_condition(condition_name):
    """Look up a condition's effects. Returns the condition dict or raises ValueError."""
    if condition_name not in CONDITION_EFFECTS:
        raise ValueError(f"Unknown condition: '{condition_name}'. "
                         f"Known conditions: {list(CONDITION_EFFECTS.keys())}")
    return CONDITION_EFFECTS[condition_name]
