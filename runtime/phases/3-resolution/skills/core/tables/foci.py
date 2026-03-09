"""WWN focus (feat) definitions.

Sources:
  - WWN 1 pp.22-31: Core foci (35 entries)
  - WWN 5 pp.176-183: Maqqatban Knight, Amundi Godblood, Arcane Secret,
    Non-Human Origin foci
"""

# Each focus has level_1 and level_2 effects (some have only level_1).
# Types:
#   "any"         - available to all classes
#   "warrior"     - only Warriors or Partial Warriors
#   "mage_only"   - only Mages or Partial Mages
#   "non_mage"    - cannot be taken by Mages or Partial Mages
#   "expert_only" - only Experts or Partial Experts
#
# Optional fields:
#   "repeatable"       - can be taken multiple times (for different skills/attributes)
#   "category"         - WWN5 focus group (maqqatban_knight, amundi_godblood,
#                        arcane_secret, non_human_origin)
#   "class_restriction" - further restriction beyond type

FOCI = {
    # ══════════════════════════════════════════════════════════════════
    # WWN 1 Core Foci (pp.22-31)
    # ══════════════════════════════════════════════════════════════════

    "alert": {
        "type": "any",
        "level_1": (
            "Gain Notice as a bonus skill. You cannot be surprised, nor can "
            "others use the Execution Attack option on you. +1 bonus to your "
            "side's initiative roll (doesn't stack with other Alert PCs). If "
            "rolling individually, roll twice and take the better result."
        ),
        "level_2": (
            "You always act first in a combat round unless someone else "
            "involved is also this Alert."
        ),
    },
    "armored_magic": {
        "type": "mage_only",
        "level_1": (
            "You can cast spells or use arts while wearing armor with an "
            "Encumbrance value of no more than two. You can use a shield "
            "while casting, provided your other hand is empty for gesturing."
        ),
        "level_2": (
            "You can cast spells while wearing armor of any Encumbrance. "
            "You can cast spells while both your hands are full, though "
            "not bound."
        ),
    },
    "armsmaster": {
        "type": "warrior",
        "level_1": (
            "Gain Stab as a bonus skill. You can Ready a Stowed melee or "
            "thrown weapon as an Instant action. You may add your Stab skill "
            "level to a melee or thrown weapon's damage roll or Shock damage, "
            "assuming it has any to begin with."
        ),
        "level_2": (
            "The Shock from your melee attacks always treats the target as "
            "if they have AC 10. Gain a +1 bonus to hit with all thrown or "
            "melee attacks."
        ),
    },
    "artisan": {
        "type": "any",
        "level_1": (
            "Gain Craft as a bonus skill. Your Craft skill is treated as one "
            "level higher (max 5) for crafting and maintaining mods. Mods you "
            "build require one fewer unit of arcane salvage (min 1). Your "
            "Craft skill applies to any normal crafting profession's work."
        ),
        "level_2": (
            "The first mod you add to an item requires no Maintenance and "
            "only half the silver piece cost. You automatically succeed at "
            "building masterwork gear. Once per month reduce a mod's salvage "
            "cost by one further unit (min 0)."
        ),
    },
    "assassin": {
        "type": "any",
        "level_1": (
            "Gain Sneak as a bonus skill. You can conceal an object no "
            "larger than a knife from anything less invasive than a strip "
            "search. You can draw it as an On Turn action, and your point-"
            "blank thrown or melee attacks during a surprise round with it "
            "cannot miss. Execution Attack advantages per p.44."
        ),
        "level_2": (
            "You can take a Move action on the same round as you make an "
            "Execution Attack, splitting it before and after the attack. "
            "This movement is too quick to alert a victim or be hindered "
            "by bodyguards."
        ),
    },
    "authority": {
        "type": "any",
        "level_1": (
            "Gain Lead as a bonus skill. Once per day, make a request from "
            "a non-hostile NPC with a Cha/Lead check against their Morale "
            "score. On success, they comply if the request is not "
            "significantly harmful or extremely uncharacteristic."
        ),
        "level_2": (
            "NPCs directly led by you gain a Morale and hit roll bonus "
            "equal to your Lead skill and +1 on all skill checks. Followers "
            "and henchmen will not act against your interests unless under "
            "extreme pressure."
        ),
    },
    "close_combatant": {
        "type": "warrior",
        "level_1": (
            "Gain any combat skill as a bonus skill. You can use knife-sized "
            "thrown weapons in melee without penalty. You ignore Shock damage "
            "from melee assailants even if unarmored, but this disrupts any "
            "spellcasting you do that round."
        ),
        "level_2": (
            "The Shock damage from your melee attacks treats all targets as "
            "if they were AC 10. The Fighting Withdrawal combat action is "
            "treated as an On Turn action for you."
        ),
    },
    "connected": {
        "type": "any",
        "level_1": (
            "Gain Connect as a bonus skill. If you've spent at least a week "
            "in a not-entirely-hostile location, you'll have built a web of "
            "contacts willing to do mildly illegal favors. One favor per "
            "game day; GM decides how far they'll go."
        ),
        "level_2": (
            "Once per game session, if not entirely implausible, you meet "
            "someone you know willing to do modest favors. You decide when "
            "and where; GM decides who they are and what they can do."
        ),
    },
    "cultured": {
        "type": "any",
        "level_1": (
            "Gain Connect as a bonus skill. You fluently speak all common "
            "languages of your native region and convey basic information in "
            "uncommon ones. Learn a new language with a week's practice. "
            "Once per game day, automatically gain a minor favor from a "
            "non-hostile NPC."
        ),
        "level_2": (
            "Once per game session, reroll a failed social skill check using "
            "your cultural knowledge."
        ),
    },
    "deadeye": {
        "type": "warrior",
        "level_1": (
            "Gain Shoot as a bonus skill. You can Ready a Stowed ranged "
            "weapon as an Instant action. You may use a bow or two-handed "
            "ranged weapon even in melee range (at -4 hit penalty). Add your "
            "Shoot skill level to a ranged weapon's damage roll."
        ),
        "level_2": (
            "Reload crossbows or slow-loading weapons as an On Turn action. "
            "Use ranged weapons of any size in melee without penalty. Once "
            "per scene, auto-hit an inanimate target unless you roll a 2 on "
            "your Shoot skill check."
        ),
    },
    "dealmaker": {
        "type": "any",
        "level_1": (
            "Gain Trade as a bonus skill. With a half hour of effort you can "
            "find a buyer or seller for any good or service tradeable in the "
            "community, legal or otherwise."
        ),
        "level_2": (
            "Once per session, target a sentient not currently trying to "
            "kill you and make a request it can comprehend. If plausible, "
            "it will negotiate for a price or favor it thinks you can grant."
        ),
    },
    "developed_attribute": {
        "type": "non_mage",
        "repeatable": True,
        "level_1": (
            "Choose an attribute; its modifier is increased by +1, up to a "
            "maximum of +3. The actual score does not change. You can choose "
            "this Focus more than once to improve different attributes. "
            "Cannot be taken by Mage or Partial Mage heroes."
        ),
    },
    "die_hard": {
        "type": "any",
        "level_1": (
            "You gain an extra 2 maximum hit points per level (retroactive). "
            "You automatically stabilize if Mortally Wounded, provided you "
            "have not been incinerated, dismembered, or otherwise torn apart."
        ),
        "level_2": (
            "The first time each day that you are reduced to zero hit points "
            "by an injury, you instead survive with one hit point remaining. "
            "This can't save you from large-scale, instantly-lethal trauma."
        ),
    },
    "diplomatic_grace": {
        "type": "any",
        "level_1": (
            "Gain Convince as a bonus skill. You speak all the common "
            "languages of your region and can learn new ones to workable "
            "level in a week, fluent in a month. Reroll 1s on any skill "
            "check dice related to negotiation or diplomacy."
        ),
        "level_2": (
            "Once per day, silently consecrate a bargain; the target must "
            "make a Mental save to break the deal unless their life or "
            "something equally dear is imperiled. The deal must be specific "
            "and time-limited."
        ),
    },
    "gifted_chirurgeon": {
        "type": "any",
        "level_1": (
            "Gain Heal as a bonus skill. You may attempt to stabilize one "
            "Mortally Wounded adjacent person per round as an On Turn "
            "action. When rolling Heal skill checks, roll 3d6 and drop the "
            "lowest die. Heal twice as many hit points with first aid."
        ),
        "level_2": (
            "Your curative gifts count as magical healing. Heal 1d6+Heal "
            "skill damage to an adjacent wounded ally as a Main Action, "
            "potentially reviving them without lingering Frailty. Each use "
            "adds 1 System Strain to the target (can't exceed max)."
        ),
    },
    "henchkeeper": {
        "type": "any",
        "level_1": (
            "Gain Lead as a bonus skill. You can acquire henchmen within "
            "24 hours of arriving in a community. They won't fight except "
            "to save their lives, but will escort you on adventures and "
            "risk great danger. One henchman per three character levels, "
            "rounded up."
        ),
        "level_2": (
            "Your henchmen are remarkably loyal and will fight against "
            "anything but clearly overwhelming odds. They are treated as "
            "Veteran Soldiers. You can recruit skilled and highly-capable "
            "NPCs as henchmen if you've done them a significant favor."
        ),
    },
    "impervious_defense": {
        "type": "warrior",
        "level_1": (
            "You have an innate Armor Class of 15 plus half your character "
            "level, rounded up. This does not stack with armor, though "
            "Dexterity or shield modifiers apply."
        ),
        "level_2": (
            "Once per day, as an Instant action, shrug off any single "
            "weapon attack or physical trauma inflicted by a foe. "
            "Environmental or falling damage cannot be resisted this way."
        ),
    },
    "impostor": {
        "type": "any",
        "level_1": (
            "Gain Perform or Sneak as a bonus skill. Once per scene, reroll "
            "any failed skill check or save related to maintaining an "
            "imposture or disguise. Create one false identity of no great "
            "social importance; only extremely persuasive proof can connect "
            "you with it."
        ),
        "level_2": (
            "A single Main Action lets you swap between any of three chosen "
            "appearances. You can establish a new false identity in each "
            "city or significant community you spend at least a day in."
        ),
    },
    "lucky": {
        "type": "any",
        "level_1": (
            "Once per week, a blow or effect that would have left you "
            "killed, mortally wounded, or helpless somehow fails to affect "
            "you. You make any rolls related to games of chance twice, "
            "taking the better roll. Requires at least one attribute "
            "modifier of -1 or less."
        ),
        "level_2": (
            "Once per session, in a situation of need or peril, roll 1d6. "
            "On 2+, something fortunate happens to further your goal or "
            "provide an escape. On a 1, the situation immediately grows "
            "much worse."
        ),
    },
    "nullifier": {
        "type": "non_mage",
        "level_1": (
            "You and all allies within twenty feet gain a +2 bonus to all "
            "saving throws against magical effects. As an On Turn action, "
            "feel the presence or use of magic within twenty feet. The "
            "first failed save against a magical effect each day becomes "
            "a success. Cannot be taken by Mages or Partial Mages."
        ),
        "level_2": (
            "Once per day, as an Instant action, you are simply not "
            "affected by an unwanted magical effect or supernatural "
            "monstrous ability, even if it wouldn't normally allow a "
            "saving throw. Immunity to a persistent effect lasts for "
            "the rest of the scene."
        ),
    },
    "poisoner": {
        "type": "any",
        "level_1": (
            "Gain Heal as a bonus skill. Gain a reroll on any failed save "
            "vs poison. Your toxins inflict 2d6 damage plus your level on "
            "hit or Shock, with a Physical save for half. Incapacitating "
            "toxins reduce targets to 0 HP (incapacitated for an hour)."
        ),
        "level_2": (
            "You are immune to poison and can apply a universal antidote "
            "to any poisoned ally as a Main Action. Detecting or saving "
            "against your poisons takes a penalty equal to your Heal skill. "
            "Your ingested poisons count as an Execution Attack against "
            "unsuspecting targets."
        ),
    },
    "polymath": {
        "type": "expert_only",
        "level_1": (
            "Gain any one bonus skill. You treat all non-combat skills as "
            "if they were at least level-0 for purposes of skill checks, "
            "even if you lack them entirely. Only Experts or Partial "
            "Experts can take this Focus."
        ),
        "level_2": (
            "You treat all non-combat skills as if they were at least "
            "level-1 for purposes of skill checks."
        ),
    },
    "rider": {
        "type": "any",
        "level_1": (
            "Gain Ride as a bonus skill. Your steeds all count as Morale 12 "
            "in battle, use your AC if higher than theirs, and can travel "
            "50% further in a day. You can intuitively communicate with "
            "riding beasts, gaining information their intellect can convey."
        ),
        "level_2": (
            "Once per scene, negate a successful attack against your steed "
            "as an Instant action. Once per scene, reroll any failed Ride "
            "check. Telepathically communicate with your bonded steed "
            "within 200 feet. Bond with one steed at a time (1 hour)."
        ),
    },
    "shocking_assault": {
        "type": "warrior",
        "level_1": (
            "Gain Punch or Stab as a bonus skill. The Shock damage of your "
            "weapon treats all targets as if they were AC 10, assuming your "
            "weapon is capable of harming the target and the target is not "
            "immune to Shock."
        ),
        "level_2": (
            "You gain a +2 bonus to the Shock damage rating of all melee "
            "weapons and unarmed attacks that do Shock. Regular hits never "
            "do less damage than this Shock would do on a miss."
        ),
    },
    "snipers_eye": {
        "type": "warrior",
        "level_1": (
            "Gain Shoot as a bonus skill. When making a skill check for a "
            "ranged Execution Attack or target shooting, roll 3d6 and drop "
            "the lowest die."
        ),
        "level_2": (
            "You don't miss ranged Execution Attacks. A target hit by one "
            "takes a -4 penalty on the Physical saving throw to avoid "
            "immediate mortal injury. Even if the save succeeds, the target "
            "takes double the normal damage."
        ),
    },
    "special_origin": {
        "type": "any",
        "level_1": (
            "Placeholder for racial/species origin Foci. PCs who want to "
            "belong to some exotic species or demihuman kind can pick the "
            "origin Focus appropriate to their chosen species. Availability "
            "depends on the campaign and the GM's permission."
        ),
    },
    "specialist": {
        "type": "any",
        "repeatable": True,
        "level_1": (
            "Gain any skill as a bonus, except for Magic, Stab, Shoot, or "
            "Punch. Roll 3d6 and drop the lowest die for all skill checks "
            "in this skill. May take this Focus more than once for "
            "different skills."
        ),
        "level_2": (
            "Roll 4d6 and drop the two lowest dice for all skill checks "
            "in this skill."
        ),
    },
    "spirit_familiar": {
        "type": "any",
        "level_1": (
            "Choose a form for your familiar no smaller than a cat nor "
            "larger than a human. It has the traits of an entity created "
            "by Calculation of the Evoked Servitor (p.68). Summoned or "
            "dismissed as a Main Action. No need for food, water, or "
            "sleep. If killed, re-summon after 24 hours. Once per day, "
            "it can refresh one point of Committed Effort."
        ),
        "level_2": (
            "Pick two benefits from the familiar options list. This level "
            "may be taken more than once, adding two options each time. "
            "Options include: HP equal to 3x your level, attack ability, "
            "+1 skill check bonus, additional shape, flight, or free "
            "language communication."
        ),
    },
    "trapmaster": {
        "type": "any",
        "level_1": (
            "Gain Notice as a bonus skill. Once per scene, reroll any "
            "failed save or skill check related to traps or snares. With "
            "five minutes of work, trap a portal, container, or passage. "
            "Non-lethal traps cost the victim a round; dangerous ones do "
            "1d6 + 2x level damage (save for half). One improvised trap "
            "at a time."
        ),
        "level_2": (
            "Once per scene, your trap-disarming counts as an Extirpate "
            "Arcana spell cast as a Mage of twice your level, using "
            "Int/Notice or Dex/Notice. Works against any stationary "
            "magical effect susceptible to Extirpate Arcana."
        ),
    },
    "unarmed_combatant": {
        "type": "warrior",
        "level_1": (
            "Gain Punch as a bonus skill. Unarmed damage scales with Punch "
            "skill: level-0 = 1d6, level-1 = 1d8, level-2 = 1d10, level-3 "
            "= 1d12, level-4 = 1d12+1. At Punch-1+, unarmed attacks have "
            "Shock equal to Punch skill against AC 15 or less."
        ),
        "level_2": (
            "Even on a miss with a Punch attack, you do an unmodified 1d6 "
            "damage, plus any Shock that the blow might inflict on the "
            "target."
        ),
    },
    "unique_gift": {
        "type": "any",
        "level_1": (
            "Your hero has some unusual ability or magical knack that can't "
            "be adequately described by an existing Focus. The exact effect "
            "should be defined by the player and the GM together, working "
            "out a result that seems fair and reasonable."
        ),
    },
    "valiant_defender": {
        "type": "warrior",
        "level_1": (
            "Gain Stab or Punch as a bonus skill. Gain +2 on all skill "
            "checks for the Screen Ally combat action. Screen against one "
            "more attacker per round than your skill allows. Once per "
            "round, Screen Ally against intangible spells, magical attacks, "
            "or area-effect explosions (opposed skill check using Magic)."
        ),
        "level_2": (
            "The first Screen Ally check in a round is always successful. "
            "Gain +2 AC while screening someone. You can screen against "
            "foes as large as ogres or oxen."
        ),
    },
    "well_met": {
        "type": "any",
        "level_1": (
            "Reaction rolls made by those the party meets are given a +1 "
            "bonus so long as you are present, whether or not you do the "
            "talking. Even hostile encountered beings will usually give "
            "the party a round to parley before attacking."
        ),
        "level_2": (
            "Once per game session, when a reaction roll is made, cause "
            "the subject to be as friendly and helpful as it's plausibly "
            "possible for them to be."
        ),
    },
    "whirlwind_assault": {
        "type": "warrior",
        "level_1": (
            "Gain Stab as a bonus skill. Once per scene, as an On Turn "
            "action, apply your Shock damage to all foes within melee "
            "range, assuming they're susceptible to your Shock."
        ),
        "level_2": (
            "The first time you kill someone in a round with a normal "
            "attack (rolled damage on a hit or Shock damage), instantly "
            "gain a second attack on any target within range using any "
            "Ready weapon you have."
        ),
    },
    "xenoblooded": {
        "type": "any",
        "level_1": (
            "Choose one set of benefits to reflect your alien heritage: "
            "immune to heat/see through smoke; water-adapted/breathe water/"
            "swim 2x speed; heavy/light gravity (+1 Str or Dex modifier, "
            "-1 the other, max +3); or no need for food/sleep/breath and "
            "darkvision."
        ),
    },

    # ══════════════════════════════════════════════════════════════════
    # WWN 5 — Maqqatban Knight Foci (pp.176-177)
    # Warrior/Partial Warrior only. Only one style per character.
    # ══════════════════════════════════════════════════════════════════

    "all_directions_edge_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain a combat skill as a bonus skill. As an On Turn action, "
            "make a normal non-grappling attack (once per round). After "
            "the first use each day, each additional use adds 1 System "
            "Strain. Your hit die is penalized by 2 points."
        ),
        "level_2": (
            "Once per day, as a Main Action, attack every enemy within "
            "range once. For ranged weapons, the maximum targets equal "
            "your Shoot skill plus one."
        ),
    },
    "catalytic_soul_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain Shoot as a bonus skill. Your ranged attacks are physically "
            "intangible to allies. When you make a ranged attack, nominate "
            "an ally within melee range of your target as an Instant action; "
            "the target suffers Shock as if melee attacked by that ally."
        ),
        "level_2": (
            "If you hit a target boosted by level 1, either you or your "
            "ally may gain 1 System Strain and heal 2d6 damage plus the "
            "target's level or hit dice. A subject can heal only once per "
            "scene this way."
        ),
    },
    "ghost_archer_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain Shoot as a bonus skill. As an On Turn action, generate "
            "a zero-encumbrance spiritual copy of any bow you've ever "
            "fired. It vanishes when it leaves your hands but has all "
            "properties of the original. You suffer -4 to hit with "
            "non-bow/crossbow weapons."
        ),
        "level_2": (
            "Once per scene, as an On Turn action, shoot an arrow at any "
            "location within range. You instantly appear where the arrow "
            "lands. Gain 1 System Strain when you use this ability."
        ),
    },
    "one_point_strike_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain a combat skill as a bonus skill. All your attacks use "
            "the better of your Intelligence or Wisdom modifiers in place "
            "of usual attributes. As a Main Action, make a melee attack "
            "that does minimum damage but your hit roll is made at +4."
        ),
        "level_2": (
            "Once per scene, as an Instant action, a melee hit using this "
            "style has its weapon damage maximized."
        ),
    },
    "pyre_of_heaven_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain a combat skill as a bonus skill. Ignore the first 5 "
            "points of fire/heat damage per round. Glow like a torch at "
            "will. As an Instant action, gain 1 System Strain to ignite "
            "your weapon, fist, or ammunition for the round, adding +1d6 "
            "fire damage."
        ),
        "level_2": (
            "Immune to non-magical flame or smoke. When ignited, your "
            "entire body ignites (you choose what to harm). Cannot be "
            "grappled while ignited. The first ignition each scene is "
            "free (no System Strain)."
        ),
    },
    "righteous_iron_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain Exert as a bonus skill. Armor you wear has +1 AC bonus "
            "and no encumbrance value (retains it for Armored Magic "
            "purposes). Armor does not penalize Sneak or Exert checks. "
            "You can sleep comfortably in armor."
        ),
        "level_2": (
            "While armored, you need not eat, drink, sleep, or breathe "
            "and are immune to normal climatic heat or cold. The armor "
            "AC bonus becomes +2 instead of +1."
        ),
    },
    "world_tree_lance_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain Stab as a bonus skill. Your wielded spear has no "
            "encumbrance and always returns if thrown. Throwable spear "
            "ranges are doubled; non-throwable spears gain 30/60 ft "
            "thrown range. Your spear gains +1 bonus to hit and damage."
        ),
        "level_2": (
            "While wielding a spear, your effective melee range is 10 "
            "feet plus your character level. Allies between you and your "
            "target do not hinder your attacks."
        ),
    },
    "wrathful_mountain_style": {
        "type": "warrior",
        "category": "maqqatban_knight",
        "level_1": (
            "Gain Stab or Punch as a bonus skill. Manifest a zero-"
            "encumbrance magical large shield as an Instant action "
            "(functions with both hands occupied). Once per round, when "
            "someone makes a melee attack on an ally you're Screening, "
            "you can make a free melee retaliation against the attacker."
        ),
        "level_2": (
            "Melee retaliation can now apply as a magical ranged attack "
            "against those who make ranged attacks on your Screened ally, "
            "regardless of distance. Accept 1 System Strain as an Instant "
            "action to retaliate against all attackers for the round."
        ),
    },

    # ══════════════════════════════════════════════════════════════════
    # WWN 5 — Amundi Godblood Foci (pp.178-179)
    # Expert/Partial Expert only. Only one Godblood Focus per character.
    # ══════════════════════════════════════════════════════════════════

    "danger_sense": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Notice as a bonus skill. You become aware of Execution "
            "Attacks on yourself or those in your presence just in time to "
            "spoil the attack. Once per day, just before you trigger a "
            "trap, walk into an ambush, or otherwise do something that "
            "would likely get you wounded or killed, you sense your danger "
            "in time to stop."
        ),
        "level_2": (
            "Gain a +1 bonus to your Wisdom modifier. Once per day as an "
            "Instant action when in danger, get an intuitive sense of the "
            "best course of action to escape peril with minimum losses."
        ),
    },
    "folie_a_deux": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Convince as a bonus skill. Your lies or deceptions never "
            "register as such; spells and abilities read you as sincerely "
            "believing what you say. Once per day, make a listener believe "
            "you are absolutely sincere. This belief lasts until the "
            "situation or new evidence would justify disbelief."
        ),
        "level_2": (
            "Gain a +1 Charisma modifier bonus. Once per day, utter a "
            "bald-faced lie; the target must make a Mental save at a "
            "penalty equal to your Convince skill or believe it for "
            "1d4 rounds."
        ),
    },
    "master_tracker": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Survive as a bonus skill. You can follow any trail "
            "created within the past day in a city or past week in the "
            "wilderness, detecting even the minutest traces of passage "
            "and ignoring weather or water obfuscation. Identify numbers "
            "and nature of those who passed."
        ),
        "level_2": (
            "Gain a +1 bonus to your Wisdom modifier. Identify specific "
            "people by their tracks if you've met them before. Once per "
            "day, examine a scene of a past event to gain detailed "
            "information about what happened."
        ),
    },
    "night_walker": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Sneak as a bonus skill. See normally in all but pitch "
            "blackness; even when blinded, function as if sighted out to "
            "30 feet. Your sleep is effectively wakefulness; you are "
            "fully aware of your surroundings while resting."
        ),
        "level_2": (
            "Gain a +1 bonus to your Dexterity modifier. Unless an area "
            "is lit by torchlight or brighter, you are effectively "
            "invisible in it until you draw attention."
        ),
    },
    "pack_beast": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Exert as a bonus skill. Your Strength is treated as 18 "
            "for encumbrance purposes, or 22 if it's already 18."
        ),
        "level_2": (
            "Gain a +1 bonus to your Strength modifier. Once per scene, "
            "as an On Turn action, pick up and move an object weighing "
            "up to 1,000 pounds (must drop or set down by end of turn)."
        ),
    },
    "provident_crafter": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Craft as a bonus skill. Your Strength is treated as 4 "
            "higher for encumbrance purposes. When making a skill check "
            "or using an item, any equipment or items you need are treated "
            "as Readied even if Stowed."
        ),
        "level_2": (
            "Gain +1 to your Dexterity modifier. Once per day, as an "
            "Instant action, you happen to have Stowed a particular normal "
            "item of 2 encumbrance or less if you could have reasonably "
            "bought or made it within the past week."
        ),
    },
    "walk_like_wind": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Exert as a bonus skill. Your base ground movement rate "
            "increases by +10'. You can move normally up or down vertical "
            "surfaces so long as you end your turn on a flat surface or "
            "clinging to a usable handhold."
        ),
        "level_2": (
            "Gain a +1 to your Dexterity modifier. Leap up to 20 feet "
            "horizontally or 10 feet vertically as a Move action. Once "
            "per scene, as an On Turn action, gain a bonus Move action."
        ),
    },
    "wildtongue": {
        "type": "expert_only",
        "category": "amundi_godblood",
        "level_1": (
            "Gain Survive as a bonus skill. You can communicate with "
            "animals, conveying such simple ideas as they are capable of "
            "comprehending. If appeased, animals may do very basic favors "
            "requiring no more than immediate attention."
        ),
        "level_2": (
            "Gain a +1 to your Charisma modifier. Once per day, command "
            "a visible animal for one scene to obey even complex orders "
            "normally impossible for it. Magical beasts get a Mental "
            "saving throw to resist."
        ),
    },

    # ══════════════════════════════════════════════════════════════════
    # WWN 5 — Arcane Secret Foci (pp.180-181)
    # Mage/Partial Mage only. Only one Arcane Secret per character.
    # ══════════════════════════════════════════════════════════════════

    "atlantean_divination": {
        "type": "mage_only",
        "category": "arcane_secret",
        "level_1": (
            "Gain Know as a bonus skill. Spend an hour in a divinatory "
            "ritual; ask a one-sentence question about a future event or "
            "plan. GM secretly rolls Int/Know against difficulty 9; on "
            "success, get a few words reflecting the GM's best judgment. "
            "On failure, get a plausible but false oracle. Cannot see "
            "beyond a week. Each use within 7 days adds +1 difficulty. "
            "Gain 1 System Strain per use."
        ),
    },
    "iteral_pacting": {
        "type": "mage_only",
        "category": "arcane_secret",
        "level_1": (
            "Gain Pray as a bonus skill. Roll or pick a patron portfolio "
            "from the divine portfolios. Once per day, gain 1 System "
            "Strain and gain one of: +4 on a hit roll, +1 on a skill "
            "check, or use a Main Action to cast a first-level spell "
            "related to the patron's portfolio (no prepared spell or slot "
            "needed). Suffer -1 on all social skill checks not related "
            "to intimidation."
        ),
    },
    "nagadi_hemomancy": {
        "type": "mage_only",
        "category": "arcane_secret",
        "level_1": (
            "Gain Heal as a bonus skill. Once per day, as an Instant "
            "action after casting a spell, accept 1d4 damage per level "
            "of the spell; the casting does not count against your "
            "usable spells per day. Gain 1 System Strain each time. "
            "Cannot assist spells that harm others or affect unwilling "
            "targets."
        ),
    },
    "old_empire_sigilism": {
        "type": "mage_only",
        "category": "arcane_secret",
        "level_1": (
            "You can embed spells in small tokens that function as calyxes "
            "only usable by yourself. Creating a token takes ten minutes "
            "per level of the spell and the expenditure of a normal daily "
            "spell use. This expended slot may be recovered normally."
        ),
    },
    "vothite_mind_sorcery": {
        "type": "mage_only",
        "category": "arcane_secret",
        "level_1": (
            "Your spellcasting does not require vocalizations or gestures, "
            "though it still takes a Main Action, can be disrupted by "
            "damage, and still disallows casting in armor for most. Your "
            "spells manifest without any obvious connection to you."
        ),
    },

    # ══════════════════════════════════════════════════════════════════
    # WWN 5 — Non-Human Origin Foci (pp.181-183)
    # Level 1 only. Only one origin Focus per character.
    # ══════════════════════════════════════════════════════════════════

    "man": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Pick any skill but Magic as a bonus skill. Once per day, "
            "gain a +1 bonus on a skill check or +2 bonus to hit as an "
            "Instant action. You are impervious to mind-affecting magical "
            "effects. You otherwise function as a perfectly normal human."
        ),
    },
    "accipiter_anak": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert as a bonus skill. You are an accipiter, with the "
            "Accipiter Flight special ability, a -1 Con modifier penalty, "
            "and a +1 Dex modifier bonus."
        ),
    },
    "aristoi_anak": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Lead and any one other skill except Magic as bonus "
            "skills. Gain +1 to your Wis modifier. Your keen foresight "
            "allows you to use Wis as an applicable attribute for any "
            "weapon, in place of Strength or Dexterity."
        ),
    },
    "choeru_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Convince or Connect as a bonus skill. Gain +1 to your "
            "Cha modifier. When rolling Reaction Rolls with you present, "
            "add +1 to the dice. You can obtain serviceable fluency in a "
            "language with no more than a week of exposure."
        ),
    },
    "deepfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "You can see clearly with any degree of light. You require "
            "only half the food, water, and air of a baseline human. You "
            "may raise one physical attribute to 14 if it is lower. "
            "Exposure of eyes or skin to direct sunlight causes "
            "disadvantages."
        ),
    },
    "ghoul": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "You must eat a pound of fresh human flesh a month, but gain "
            "Sneak as a bonus skill, the benefits of Ghoulish Vigor, and "
            "may add +1 to either your Strength or Dexterity modifier. "
            "After 21 days without cannibalism, make a Mental save daily "
            "or attack the nearest human."
        ),
    },
    "guer_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Notice or Sneak as a bonus skill. Gain +1 to your Wis "
            "or Cha modifiers. You can see clearly in low-light conditions "
            "and add 10' to your ground movement rate."
        ),
    },
    "harbinger_anak": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Sneak or Convince as a bonus skill and the Harbinger's "
            "Face ability. Gain +1 to your Charisma modifier and -1 to "
            "your Constitution modifier."
        ),
    },
    "hua_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert as a bonus skill. Gain +1 to your Str modifier "
            "and -1 to your Dex modifier. Treat Strength as 4 higher for "
            "Encumbrance. Your System Strain maximum is 2 points higher "
            "than normal."
        ),
    },
    "kitsune_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Notice or Convince as a bonus skill. Gain +1 to your "
            "Charisma modifier. Gain the Elemental Sparks Elementalist "
            "art; if you already have it, pick a bonus Elementalist art "
            "instead."
        ),
    },
    "manu_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert or Survive as a bonus skill. Gain +1 to your Con "
            "or Str modifier and -1 to your Dex or Cha modifier. You swim "
            "at normal movement speed, can hold your breath for fifteen "
            "minutes, and your tough hide reduces all Shock damage by 1."
        ),
    },
    "nahu_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Sneak or Notice as a bonus skill. Gain +1 to your Dex "
            "or Cha modifiers. Your claws count as daggers for melee "
            "purposes and you can see clearly in low-light conditions. "
            "During combat, make a Mental save to inflict non-lethal "
            "damage; failure means full lethal damage."
        ),
    },
    "pichi_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Notice as a bonus skill. Gain +1 to your Wis or Dex "
            "modifiers and -1 to your Str or Con modifier. See normally "
            "in low-light. Your senses are sharp enough to interact with "
            "objects within ten feet as if sighted, even if blinded."
        ),
    },
    "piren_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert as a bonus skill. Once per scene as a Move "
            "action, give an ally within melee distance a bonus Main "
            "Action (physical acts only, not spellcasting). A given "
            "ally can only benefit from this once per scene."
        ),
    },
    "sui_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Survive as a bonus skill. Gain +1 to your Constitution "
            "modifier. Immune to mundane poisons. Once per day, continue "
            "acting for 1 full round after falling to zero hit points, "
            "provided you are not hopelessly mangled."
        ),
    },
    "usagi_beastfolk": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert or Sneak as a bonus skill and +1 bonus to all "
            "saving throws. Gain +1 Dex modifier and either -1 Str or "
            "-1 Con modifier. Once per scene, as an On Turn action, "
            "double your ground movement rate for the round."
        ),
    },
    "zakathi": {
        "type": "any",
        "category": "non_human_origin",
        "level_1": (
            "Gain Exert as a bonus skill. If your Constitution is lower "
            "than 14, raise it to 14; if equal or higher, raise it to 18. "
            "Your maximum System Strain increases by 2. You must exhaust "
            "yourself with labor or exertions by the end of each day."
        ),
    },
}
