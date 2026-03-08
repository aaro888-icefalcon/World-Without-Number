"""
Failure flavor text tables for Phase 4 narrative translation.

Each domain contains short complication/revelation prompts used when the LLM
narrates failed actions. These are seeds for narrative, not complete
descriptions — the LLM expands them into full prose matching the Latter Earth
voice and the specific scene context.

Rule: failures ALWAYS produce a complication or revelation. Nothing simply
"doesn't work." The world responds to every attempt.
"""

FAILURE_FLAVORS = {
    "combat_miss": [
        "Your blade scrapes along the stone wall, sending sparks into the darkness.",
        "The creature sways aside with a boneless fluidity that nothing living should possess.",
        "Your strike meets empty air — it was not where your eyes told you it was.",
        "The edge glances off carapace with a sound like cracking pottery. The weapon holds, but your wrist aches.",
        "You overextend, and for a terrible instant your back is exposed.",
        "The blow lands true on an afterimage. The real thing is already behind you.",
        "Your weapon bites into the wooden beam where the target stood a heartbeat ago. It takes a precious moment to wrench free.",
        "The swing goes wide, but the wind of its passage disturbs something on the far wall — dust, or spores, or something that glitters.",
        "It catches your blade in one hand. Casually. Then lets go, as if to say: again.",
        "Your footing shifts on the blood-slick floor, turning a killing stroke into a graceless stumble.",
    ],

    "skill_check_failure": [
        "The lock resists your picks, and the third tumbler snaps something inside the mechanism. A different approach is needed now.",
        "The rope holds your weight for three handholds, then the fibers begin to part with a sound like tearing cloth.",
        "You recognize the script but not the dialect. The meaning hovers just beyond comprehension, tantalizing and incomplete.",
        "The trail was clear until the stream crossing. On the far bank, the ground is stone, and the tracks simply end.",
        "Your hands know the work, but the material is wrong — older, stranger, made by methods you do not recognize.",
        "The mechanism responds to your touch, then freezes. Something clicks deep inside the wall. That was not the right sequence.",
        "You find the pressure point, but the stone does not move. It is not stuck. It is resisting, as though something on the other side pushes back.",
        "The knot holds for a moment, then slides apart. Silk from the Latter Earth does not behave like honest rope.",
        "You misread the current. The boat turns broadside to the flow and for three long seconds you are not in control.",
        "The disguise is good. The mannerisms are good. But your shadow falls wrong in the lamplight, and one pair of eyes notices.",
    ],

    "spell_failure": [
        "The syllables leave your mouth correctly, but the air refuses to carry them. The spell collapses like a held breath released.",
        "Power gathers in your hands — then disperses in a shower of pale sparks. The ambient sorcery here is wrong, somehow.",
        "The working takes shape for an instant: a lattice of light in the air before you. Then a flaw propagates through it like a crack in ice, and it shatters.",
        "Something answers the invocation, but it is not the intended effect. A smell of copper. A whisper in a language you do not speak. Then nothing.",
        "Your effort surges outward and meets a wall — an older enchantment, buried in the stonework, still functioning after uncounted years. Your spell breaks against it.",
        "The sigil completes itself, then rotates ninety degrees of its own accord and fades. Whatever geometry governs sorcery here follows different rules.",
        "Blood drips from your nose. The art demanded more than you had to give, and your body paid the remainder.",
        "The casting succeeds — briefly. For one heartbeat the effect manifests perfectly. Then it inverts, and you feel the energy snap back into you like a bowstring released.",
        "The working draws the attention of something distant. You feel it turn toward you — vast, incurious, patient. Then the connection severs. The spell is lost.",
        "Effort expended, nothing gained. But the failed pattern lingers in your vision like a sunspot, and in its afterimage you glimpse something the spell was never meant to show.",
    ],

    "travel_hazard": [
        "The bridge looked sound from a distance. Up close, the mortar has turned to powder and the keystone has shifted three inches downward.",
        "Rain turns the path to clay. Your boots sink to the ankle. By the time you find solid ground, an hour has been lost.",
        "The ford the locals described has moved. The river is wider now, faster, and the water is the color of old tea.",
        "A rockslide has remade the valley since the map was drawn. The passage marked in ink is now a wall of broken stone.",
        "The woods thin, then end abruptly at a field of glass — the ground vitrified smooth as a mirror, stretching a quarter mile. Nothing grows on it. Nothing crosses it.",
        "Your mount refuses to continue. Ears flat, nostrils flared, feet planted. Animals know things that maps do not.",
        "The shortcut descends into a hollow where the air is thick and still and tastes of metal. Insects hang motionless in the amber light. You choose the long way around.",
        "Night falls faster than it should. The sun drops behind the ridgeline two hours early, as though the mountain has grown since morning.",
        "The path forks where the map shows none. Both branches look equally traveled. Both lead into shadow.",
        "A tree has fallen across the road — recently, by the pale color of the broken wood. The trunk is too large to move and too high to climb. Something felled it deliberately.",
    ],

    "social_gaffe": [
        "A silence falls over the table. You have said something that carries a meaning here that it does not carry elsewhere.",
        "The elder's expression closes like a shutter. Whatever trust you had built evaporates with that single word.",
        "The merchant's smile does not change, but her hand moves beneath the counter. The price just doubled.",
        "You invoke a name that should not be spoken in this district. Heads turn. Conversations stop. Someone leaves by the back door.",
        "The gesture you intended as respectful is, in this province, a challenge. The room grows very still.",
        "Your offer is generous by any reasonable measure. The insult lies not in the amount but in the offering itself — some things cannot be purchased here.",
        "The joke lands badly. The laughter that follows is not amusement but something more like a warning.",
        "You spoke to the apprentice before the master. In this guild-house, that is not ignorance. It is an accusation.",
        "The truthful answer was the wrong answer. Here, among these people, the polite fiction serves a purpose you did not understand until now.",
        "Your accent betrays you. You are not from where you claimed to be, and now they are wondering what else you lied about.",
    ],

    "save_failure": [
        "The poison moves faster than your constitution can fight. Heat blooms in your chest, then numbness radiates outward.",
        "The floor gives way and you do not move in time. The fall is shorter than you feared — but the landing is harder.",
        "The compulsion settles over your thoughts like oil on water. You know it is there. You cannot make yourself care.",
        "The blast catches you mid-stride. The world goes white, then loud, then quiet in a way that suggests damage.",
        "Something ancient and patient wraps itself around your will. For a moment you see through its eyes — a perspective vast and indifferent and very, very old.",
        "Your body betrays you. Muscles lock, joints stiffen, and for three heartbeats you are a passenger in your own flesh.",
        "The ward-sign flares and you flinch, but the flinch comes too late. The curse has already found its mark — a cold thread wound through your thoughts.",
        "You breathe in before you can stop yourself. The spores taste of nothing. That is the worst part.",
        "The trap triggers and your reflexes fire — but the mechanism was faster. It was always going to be faster.",
        "The ground beneath you lurches, and your balance fails. You fall in a way that will leave bruises and cost time.",
    ],
}
