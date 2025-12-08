"""
Example Scenes for Gilderhaven
===============================

Demonstrates how to write scene content for the scene system.
These can be triggered by room entry, object interaction, traps,
resource hazards, random events, or anything else.

Each scene is a self-contained narrative. The "NPCs" in these scenes
don't exist as game objects - they exist only within the text.
"""

from world.scenes import register_scene

# =============================================================================
# EXAMPLE 1: Simple Trap Scene
# =============================================================================

PASSION_BLOOM_SCENE = {
    "id": "passion_bloom_01",
    "title": "Passion Bloom",
    "tags": ["trap", "flora", "heat", "grove"],
    
    "start": {
        "text": """
You reach for the vibrant flower, its petals an impossible shade of pink 
that seems to pulse with inner light. The moment your fingers brush the 
stem, the bloom opens wide and releases a cloud of glittering pollen 
directly into your face.

You inhale sharply in surprise—a mistake.

The pollen tastes sweet, almost like honey, and a warmth begins spreading 
through your chest immediately. Your skin flushes. Your heart races.
""",
        "effects": [
            {"type": "message", "text": "|mThe pollen takes effect almost immediately...|n"},
            {"type": "apply_effect", "effect_key": "pollen_heat", "category": "debuff", "duration": 3600},
        ],
        "choices": [
            {"text": "Try to wipe it off", "goto": "wipe"},
            {"text": "Stumble away from the plant", "goto": "flee"},
            {"text": "Breathe deeper...", "goto": "embrace", 
             "condition": {"type": "has_effect", "effect": "curious"}},
        ]
    },
    
    "wipe": {
        "text": """
You frantically scrub at your face, but the pollen has already absorbed 
into your skin. If anything, the rubbing just spreads it further, and 
the warmth intensifies. Your fingers tingle where they touched the 
residue.

|mThe heat settles low in your belly, insistent and distracting.|n

The flower sways innocently, as if nothing happened. Other blooms nearby 
seem to turn toward you, curious about their next victim.
""",
        "end": True
    },
    
    "flee": {
        "text": """
You back away hastily, nearly tripping over a root in your haste to 
escape. The flower doesn't pursue—it doesn't need to. The damage is done.

With every step, you feel the warmth spreading further. By the time 
you've put distance between yourself and the treacherous bloom, your 
whole body feels flushed and sensitive.

|mYou're going to be dealing with this for a while.|n
""",
        "end": True
    },
    
    "embrace": {
        "text": """
Something in you—perhaps the pollen already taking effect—makes you 
lean closer instead of away. You breathe deep, filling your lungs with 
the sweet, glittering cloud.

|mOh.|n

|mOh, that's...|n

The warmth doesn't just spread—it |yignites|n. Every nerve ending lights 
up with desperate sensitivity. Your knees go weak, and you find yourself 
on the ground before the flower, panting, completely overwhelmed by the 
intensity of the sensation.

The flower seems almost smug as it releases another puff of pollen 
directly onto you.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "pollen_overdose", "category": "debuff", "duration": 7200},
            {"type": "apply_effect", "effect_key": "on_knees", "category": "status", "duration": 60},
        ],
        "end": True
    }
}

register_scene("passion_bloom_01", PASSION_BLOOM_SCENE)


# =============================================================================
# EXAMPLE 2: Full Encounter Scene (like CoC/TiTS loss scene)
# =============================================================================

GOBLIN_AMBUSH_SCENE = {
    "id": "goblin_ambush_01",
    "title": "Goblin Ambush",
    "tags": ["encounter", "goblin", "combat_loss", "grove", "forest"],
    
    "start": {
        "text": """
The goblin moves faster than you expected. One moment you're walking 
through the underbrush, the next you're on your back with a small, 
green-skinned figure straddling your chest.

She's tiny—barely three feet tall—but surprisingly strong. Her yellow 
eyes gleam with triumph as she pins your wrists above your head, her 
pointed ears twitching with excitement.

"Caught you!" she chirps, her voice high and gleeful. "Stupid tall-folk, 
walking right into goblin territory. Now you pay toll!"

Her grip is like iron despite her size. You can feel her weight settling 
on your chest, her bare thighs warm against your sides.
""",
        "effects": [
            {"type": "set_flag", "flag": "goblin_sitting_on_chest", "value": True}
        ],
        "choices": [
            {"text": "Struggle against her grip", "goto": "struggle_1"},
            {"text": "Try to negotiate", "goto": "negotiate_1"},
            {"text": "Go limp and submit", "goto": "submit_1",
             "condition": {"type": "has_effect", "effect": "pollen_heat"}},
            {"text": "Offer gold", "goto": "bribe_1",
             "condition": {"type": "currency_gte", "amount": 50}},
        ]
    },
    
    # === STRUGGLE PATH ===
    "struggle_1": {
        "text": """
You buck and thrash beneath her, trying to throw her off. The goblin 
squeaks in surprise but holds on, her fingers digging into your wrists 
with surprising strength.

"Oooh, feisty!" She grins wider, showing sharp little teeth. "Goblin 
like feisty. Makes it more fun when you stop fighting."

Her tail—you hadn't noticed she had one—wraps around your thigh, 
anchoring her in place. She's not going anywhere.

"Keep squirming," she purrs. "Wearing yourself out. Soon you be too 
tired to resist, and then..." She licks her lips.
""",
        "choices": [
            {"text": "Keep struggling", "goto": "struggle_2"},
            {"text": "Stop and catch your breath", "goto": "exhausted_1"},
            {"text": "Try to headbutt her", "goto": "headbutt"},
        ]
    },
    
    "struggle_2": {
        "text": """
You redouble your efforts, muscles straining. For a moment, you think 
you might actually throw her off—one of your wrists slips free of her 
grip—

But she's ready. Quick as a snake, she produces a length of vine from 
somewhere and loops it around your free wrist, yanking it back into 
place and securing both hands together above your head.

"There," she says smugly, tying the vine to an exposed root. "No more 
of that. Now where was goblin?"

You're bound now, helpless beneath her. She takes her time settling 
back onto your chest, wiggling to get comfortable.

"Much better. Now tall-folk can't interrupt."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "bound", "category": "status", "duration": 600}
        ],
        "goto": "bound_1"
    },
    
    "headbutt": {
        "text": """
You rear up suddenly, trying to catch her with your forehead. But she's 
faster—goblins always are—and she jerks back just in time.

"RUDE!" she shrieks. "Goblin was being nice! Was going to make this 
fun for tall-folk too! But NOW..."

Her eyes narrow dangerously. That mischievous gleam turns into something 
harder. Meaner.

"Now goblin show you what happens to rude prey."

Before you can react, she's produced a small vial from her belt and 
forced the contents into your mouth. It tastes like honey and fire.

"That goblin-make. Special recipe. Make you |yvery|n cooperative soon."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "goblin_aphrodisiac", "category": "debuff", "duration": 3600},
            {"type": "set_flag", "flag": "drugged", "value": True}
        ],
        "goto": "drugged_1"
    },
    
    "exhausted_1": {
        "text": """
You stop struggling, chest heaving. The goblin watches you with an 
amused expression, head tilted like a curious bird.

"Tired already? Tall-folk have no stamina." She tsks. "Is okay. Goblin 
have enough for both."

She releases your wrists—but before you can take advantage, she's 
repositioned, sitting on your stomach now with her hands pressing 
down on your shoulders. Her tail coils loosely around your thigh.

"Now. Toll. You pay one way or another. Choice is yours."

She holds up two fingers.

"Gold... or |yservice|n."
""",
        "choices": [
            {"text": "Ask what 'service' means", "goto": "ask_service"},
            {"text": "Pay gold (50)", "goto": "pay_gold",
             "condition": {"type": "currency_gte", "amount": 50}},
            {"text": "Refuse both", "goto": "refuse_both"},
            {"text": "...service", "goto": "accept_service"},
        ]
    },
    
    # === NEGOTIATE PATH ===
    "negotiate_1": {
        "text": """
"Wait, wait!" you say, trying to keep your voice calm. "Let's talk 
about this. What exactly is this 'toll' you mentioned?"

The goblin pauses, surprised. Most people either fight or beg, 
apparently.

"Toll is toll," she says slowly, as if explaining to a child. "You 
enter goblin territory, you pay. Is simple. Everybody know this."

"And what forms of payment do you accept?"

She grins, showing those sharp teeth again.

"Gold, obviously. Goblins love shiny." She leans closer, her breath 
warm on your face. "But tall-folk not always have gold. So... goblins 
accept |yother|n payment too."

Her hips shift against you meaningfully.
""",
        "choices": [
            {"text": "How much gold?", "goto": "ask_gold_amount"},
            {"text": "What 'other payment'?", "goto": "ask_service"},
            {"text": "I refuse to pay anything", "goto": "refuse_both"},
        ]
    },
    
    "ask_gold_amount": {
        "text": """
"Fifty gold," she says immediately. "Standard toll. Fair price for 
not being goblin toy for afternoon."

She eyes you appraisingly.

"You look like you have fifty gold. Do you?"
""",
        "choices": [
            {"text": "Pay the 50 gold", "goto": "pay_gold",
             "condition": {"type": "currency_gte", "amount": 50}},
            {"text": "I don't have that much", "goto": "cant_pay",
             "condition": {"type": "currency_lt", "amount": 50}},
            {"text": "I have it, but I won't pay", "goto": "refuse_both",
             "condition": {"type": "currency_gte", "amount": 50}},
        ]
    },
    
    "ask_service": {
        "text": """
The goblin's grin widens until it seems to split her face.

"Service mean..." She leans down, her lips brushing your ear. Her 
voice drops to a husky whisper. "...you do what goblin want. For 
whole afternoon. Whatever goblin want."

Her hand trails down your chest.

"Goblins get |ylonely|n in forest. Tall-folk are... interesting. 
Different. Fun to play with."

She pulls back to look at you, head tilted.

"Is not so bad. Goblin promise to be gentle." She pauses, then adds 
with a wicked smile: "Maybe. If you be good."
""",
        "choices": [
            {"text": "I'll pay the gold instead", "goto": "pay_gold",
             "condition": {"type": "currency_gte", "amount": 50}},
            {"text": "...fine. Service it is.", "goto": "accept_service"},
            {"text": "Neither. Let me go.", "goto": "refuse_both"},
        ]
    },
    
    # === PAYMENT PATHS ===
    "pay_gold": {
        "text": """
"Fine, fine. Here." You manage to gesture toward your coin pouch.

The goblin's eyes light up. She snatches the gold with practiced 
ease, counting it quickly with nimble fingers.

"Fifty gold! Good tall-folk." She pats your cheek condescendingly. 
"See? Was easy. No need for struggle."

She hops off your chest and tucks the coins into a pouch at her 
belt. For a moment, she considers you thoughtfully.

"You smart. Goblin remember smart ones. Maybe next time, toll be 
less. Or maybe..." She winks. "Maybe next time you choose other 
option. Goblin will be waiting."

And just like that, she's gone, vanishing into the underbrush as 
quickly as she appeared.

You're left on the ground, lighter in the purse but otherwise 
unharmed. This time.
""",
        "effects": [
            {"type": "take_currency", "amount": 50, "reason": "goblin toll"},
            {"type": "add_tag", "tag": "paid_goblin_toll", "category": "encounters"},
        ],
        "end": True
    },
    
    "cant_pay": {
        "text": """
The goblin's expression shifts from calculating to predatory.

"No gold? That is... unfortunate. For you." She doesn't sound 
upset. If anything, she sounds pleased.

"Guess tall-folk pay other way then. Don't worry." Her hands are 
already working at your clothes. "Goblin show you how."
""",
        "goto": "service_begins"
    },
    
    "refuse_both": {
        "text": """
"No."

The goblin blinks. "No?"

"No gold. No 'service'. Let me go."

For a moment, she just stares at you. Then she starts laughing—a 
high, chittering sound that makes the hair on your neck stand up.

"Oh, tall-folk. You think you get choice?" She produces another 
vial, swirling with phosphorescent liquid. "You cute. But no. You 
in goblin territory. You pay goblin toll. One way or other."

She uncorks the vial.

"Goblin prefer volunteers. Is more fun. But..." She shrugs. "This 
work too. You wake up in few hours, toll paid, and you remember 
|yeverything|n. Maybe be nicer next time, yes?"

The liquid hits your face before you can turn away. The world 
goes warm and hazy almost instantly.

"There we go. That better. Now relax. Goblin take good care of 
you..."

Your last clear thought before the haze takes over is that you 
should have just paid the gold.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "goblin_drugged", "category": "debuff", "duration": 3600},
            {"type": "apply_effect", "effect_key": "used", "category": "status", "duration": 300},
            {"type": "set_flag", "flag": "forced_service", "value": True},
        ],
        "goto": "fade_to_black"
    },
    
    "accept_service": {
        "text": """
"...fine. Service."

The word comes out smaller than you intended. The goblin's whole 
face lights up.

"Really? You choose service?" She claps her hands together, 
bouncing excitedly on your stomach. "Oh, this be |yfun|n! Goblin 
have so many ideas!"

She slides off you but keeps hold of your hand, tugging you 
upright.

"Come, come! Goblin show you secret spot. Very comfortable. Very 
private." She winks. "No one hear you there."

Part of you wonders what you've gotten yourself into. A larger 
part doesn't care anymore.

She leads you into the underbrush, her grip on your hand 
surprisingly gentle now that you've agreed. Whatever happens 
next... well. You chose this.
""",
        "effects": [
            {"type": "add_tag", "tag": "goblin_volunteer", "category": "encounters"},
        ],
        "goto": "service_begins"
    },
    
    # === SERVICE PATH ===
    "service_begins": {
        "text": """
|x[The scene continues, but this is where the explicit content 
would go in the full game. The system supports it—just add more 
nodes with text, choices, and effects.]|n

|x[For now, we'll skip ahead to the aftermath...]|n
""",
        "goto": "service_aftermath"
    },
    
    "service_aftermath": {
        "text": """
Some time later—you're not sure how long—the goblin finally 
seems satisfied. She's curled up against your side, surprisingly 
warm for such a small creature, her tail lazily draped across 
your leg.

"Mmm. Tall-folk not bad," she murmurs. "Maybe best toll payment 
goblin have in long time."

You're exhausted. Used. And surprisingly... okay with it?

"You can go now," she says, stretching. "Toll paid. But..." She 
traces a symbol on your chest with one finger. "Goblin mark you. 
Other goblins see, know you... cooperative. Might ask for service 
first instead of fighting."

She grins up at you.

"Assuming you not want to come find goblin again on purpose. 
Many tall-folk do, after."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "goblin_marked", "category": "status", "duration": 86400},
            {"type": "apply_effect", "effect_key": "used", "category": "status", "duration": 300},
            {"type": "apply_effect", "effect_key": "satisfied", "category": "buff", "duration": 3600},
        ],
        "end": True
    },
    
    # === DRUGGED/BOUND PATHS ===
    "drugged_1": {
        "text": """
The world goes soft at the edges. Your muscles relax whether you 
want them to or not. The goblin's weight on your chest feels... 
nice, actually. When did that happen?

"There we go," she coos, watching your eyes glaze. "Much better. 
No more fighting. Just... feeling."

Her hands start to wander, and you can't—don't want to—stop her.

"Goblin going to have |yso|n much fun with you..."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "compliant", "category": "debuff", "duration": 3600},
        ],
        "goto": "service_begins"
    },
    
    "bound_1": {
        "text": """
You tug at the vine binding your wrists, but it holds fast. The 
goblin watches your futile struggles with amusement.

"Don't bother. Goblin-knots. Only goblins know how to undo." She 
taps your nose. "You stuck until goblin say otherwise."

She settles back onto you, taking her time now that she knows 
you can't escape.

"Now. Where was goblin? Oh yes. Toll payment..."
""",
        "choices": [
            {"text": "Keep struggling against the bonds", "goto": "struggle_bound"},
            {"text": "Stop fighting", "goto": "accept_bound"},
        ]
    },
    
    "struggle_bound": {
        "text": """
You thrash and pull, but the vines only seem to tighten. The 
goblin sighs.

"Stubborn. Okay. Goblin speed things up."

Another vial appears. You try to turn your head away, but she 
grabs your chin with surprising strength.

"This easier for both of us. You see."

The liquid is sweet and makes everything... simple.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "goblin_drugged", "category": "debuff", "duration": 3600},
        ],
        "goto": "service_begins"
    },
    
    "accept_bound": {
        "text": """
You go still. There's no point fighting anymore—she's won, and 
you both know it.

The goblin's expression softens slightly. "Smart. Goblin respect 
that." She leans down and, surprisingly gently, kisses your 
forehead.

"You be good, goblin be good to you. Is fair, yes?"

You're not sure you have much choice in the matter anymore.
""",
        "goto": "service_begins"
    },
    
    # === SUBMIT PATH (for characters already in heat) ===
    "submit_1": {
        "text": """
Your body is already burning from... something. The pollen 
earlier, maybe. Or something else you encountered. Whatever 
the cause, your resistance crumbles embarrassingly fast.

You go limp beneath the goblin, and she notices immediately.

"Ohhh?" Her eyes widen, nostrils flaring. "Tall-folk already 
|ywanting|n. Goblin smell it on you."

She leans down, inhaling deeply at your neck.

"Yes. Something got to you already. Made you... ready." She 
grins. "Good. Makes this easy. No need for convincing."

Her hands are already moving, and you don't even pretend to 
resist.

"Goblin like easy prey. More time for fun parts."
""",
        "effects": [
            {"type": "set_flag", "flag": "submitted_willingly", "value": True},
        ],
        "goto": "service_begins"
    },
    
    "fade_to_black": {
        "text": """
The haze takes over completely. You're aware of movement, 
sensation, the goblin's delighted laughter... but it all feels 
distant, dreamlike.

When you finally come back to yourself, you're alone.

Your body aches in interesting ways. There's a mark on your 
chest that wasn't there before—some kind of goblin symbol. 
And despite everything... you feel oddly satisfied.

The goblin is gone, along with however much time has passed. 
You should probably get moving before something else finds you 
in this state.

|x(Toll paid. Whether you wanted to or not.)|n
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "goblin_marked", "category": "status", "duration": 86400},
            {"type": "apply_effect", "effect_key": "used", "category": "status", "duration": 300},
            {"type": "apply_effect", "effect_key": "hazy_memory", "category": "status", "duration": 3600},
        ],
        "end": True
    }
}

register_scene("goblin_ambush_01", GOBLIN_AMBUSH_SCENE)


# =============================================================================
# EXAMPLE 3: Gate "Malfunction" Scene
# =============================================================================

GATE_MALFUNCTION_SCENE = {
    "id": "gate_malfunction_01",
    "title": "Gate Malfunction",
    "tags": ["gate", "trap", "teleport", "grove"],
    
    "start": {
        "text": """
You step through the gate, expecting the usual momentary 
disorientation of realm-travel. Instead, the world |ytwists|n.

Colors bleed together. Up becomes down. You feel yourself 
being pulled in multiple directions at once, the gate's magic 
clearly malfunctioning—or being tampered with.

Through the chaos, you catch glimpses of possible destinations:
- A dark forest, trees reaching like grasping hands
- A crystalline cavern, beautiful and cold
- A marketplace of some kind, loud and chaotic
- |xSomewhere else. Somewhere wrong.|n

The magic is going to deposit you |ysomewhere|n. You might be 
able to influence where, if you focus...
""",
        "choices": [
            {"text": "Focus on the forest", "goto": "forest"},
            {"text": "Focus on the cavern", "goto": "cavern"},
            {"text": "Focus on the marketplace", "goto": "market"},
            {"text": "Let go and see where fate takes you", "goto": "random"},
        ]
    },
    
    "forest": {
        "text": """
You concentrate on the dark trees, willing yourself toward them. 
The chaos snaps into sudden, jarring focus—

And you tumble out onto soft moss, surrounded by ancient oaks. 
It's not where you intended to go, but at least you're in one 
piece.

The forest is quiet. Too quiet. You should probably find your 
way back to the Grove before something finds you first.
""",
        "effects": [
            {"type": "teleport", "destination": "whisperwood_entrance"},
            {"type": "message", "text": "|yThe gate deposited you in an unfamiliar forest...|n"},
        ],
        "end": True
    },
    
    "cavern": {
        "text": """
Crystals. Cold. Safety.

You focus on the glittering cavern, and the magic responds. The 
chaos collapses, and you find yourself standing in a passage 
lined with luminescent stones, their blue glow providing soft 
illumination.

The air is cool and still. Wherever this is, it feels... old. 
And not entirely natural. Those crystals are growing in 
patterns that suggest intent.

You should explore carefully. Or find a way back.
""",
        "effects": [
            {"type": "teleport", "destination": "crystal_caves_entrance"},
            {"type": "message", "text": "|yThe gate deposited you in a crystalline cavern...|n"},
        ],
        "end": True
    },
    
    "market": {
        "text": """
You grasp for the noise, the chaos of commerce, the safety of 
crowds—

And land hard on cobblestones, narrowly avoiding a cart. Shouts 
in multiple languages surround you. The smell of spices, 
animals, and too many bodies packed together.

This isn't the Grove's market. The architecture is wrong, the 
sky is the wrong color, and you're pretty sure that merchant 
isn't selling anything legal.

But at least you're somewhere civilized. Probably. Time to 
figure out where—and how to get back.
""",
        "effects": [
            {"type": "teleport", "destination": "foreign_market"},
            {"type": "message", "text": "|yThe gate deposited you in a foreign marketplace...|n"},
        ],
        "end": True
    },
    
    "random": {
        "text": """
You stop fighting. Let the magic take you wherever it will.

The chaos intensifies—and then, suddenly, stops.

You're... somewhere. It's dark. Warm. There's a strange smell, 
like copper and flowers.

A voice speaks from the darkness:

"Well, well. What has the gate brought me this time?"

Something moves in the shadows. Something large.

You may have made a mistake.
""",
        "effects": [
            {"type": "teleport", "destination": "curator_basement"},
            {"type": "set_flag", "flag": "gate_delivered_to_curator", "value": True},
        ],
        "choices": [
            {"text": "Hello...?", "goto": "curator_greeting"},
            {"text": "Stay very, very still", "goto": "curator_still"},
            {"text": "Run", "goto": "curator_run"},
        ]
    },
    
    "curator_greeting": {
        "text": """
"So polite." The voice sounds amused. Feminine. Cultured. 
"Most of my accidental guests scream, you know."

Lights flicker on—soft, amber—revealing a lavishly appointed 
room. And its occupant.

She's tall. Blonde. Beautiful in a way that makes your 
hindbrain scream |ypredator|n. And she's looking at you like 
you're the most interesting thing she's seen all day.

"Welcome to my private collection," she says. "I am the 
Curator. And you, little lost thing, have stumbled somewhere 
|yvery|n interesting."

She smiles.

"Let's discuss how you're going to earn your way out."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "curator_interest", "category": "museum"},
        ],
        "end": True
    },
    
    "curator_still": {
        "text": """
You freeze. Maybe if you don't move, whatever's in here won't 
notice you.

The darkness chuckles.

"I can hear your heartbeat, little thing. I know exactly where 
you are." The voice is getting closer. "Staying still won't 
save you. But it |yis|n rather cute that you tried."

A hand touches your cheek—you didn't hear her approach. The 
fingers are cool, the grip firm but not painful.

"Shh. Don't be frightened. I'm not going to hurt you." A 
pause. "Much. Unless you're into that."

The lights come on.

You're face to face with the Curator.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "curator_interest", "category": "museum"},
        ],
        "end": True
    },
    
    "curator_run": {
        "text": """
You bolt.

You make it exactly three steps before something catches your 
ankle and you go down hard. The floor is surprisingly soft—
cushioned, like she expected this.

"They always run," the voice sighs, somewhere above you. "And 
they never get far. My home knows its purpose."

You try to scramble up, but the floor... shifts. Holds you. 
Cushions turn to restraints.

"There we go. Now you'll stay put while we talk."

The lights come on, and the Curator looks down at you with an 
expression of fond exasperation.

"Honestly. If you'd just stayed still, we could have done this 
the comfortable way."
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "restrained", "category": "status", "duration": 300},
            {"type": "apply_effect", "effect_key": "curator_interest", "category": "museum"},
        ],
        "end": True
    }
}

register_scene("gate_malfunction_01", GATE_MALFUNCTION_SCENE)


# =============================================================================
# EXAMPLE 4: Simple Random Event (no choices)
# =============================================================================

FOUND_COIN_SCENE = {
    "id": "found_coin_01",
    "title": "Lucky Find",
    "tags": ["random", "treasure", "simple"],
    
    "start": {
        "text": """
Something glints in the dirt at your feet. You crouch down 
and brush away the soil to reveal a gold coin, half-buried 
and forgotten.

Lucky you.
""",
        "effects": [
            {"type": "give_currency", "amount": 1},
        ],
        "end": True
    }
}

register_scene("found_coin_01", FOUND_COIN_SCENE)


# =============================================================================
# EXAMPLE 5: Fishing Mishap
# =============================================================================

FISHING_TENTACLE_SCENE = {
    "id": "fishing_tentacle_01",
    "title": "Something Grabs Your Line",
    "tags": ["fishing", "hazard", "creature", "tentacle"],
    
    "start": {
        "text": """
Your line goes taut—but not with the familiar tug of a fish. 
This is something heavier. Stronger. And it's not pulling 
away from you.

It's pulling |ytoward|n the water.

Before you can release the rod, a thick tentacle breaks the 
surface, water streaming off its mottled purple hide. It 
wraps around your forearm with alarming speed.

More tentacles follow, reaching for you.
""",
        "choices": [
            {"text": "Drop the rod and run", "goto": "drop_run"},
            {"text": "Try to pull free", "goto": "pull_free"},
            {"text": "Grab your knife", "goto": "grab_knife",
             "condition": {"type": "has_item", "item": "knife"}},
        ]
    },
    
    "drop_run": {
        "text": """
You release the rod and scramble backward, but the tentacle 
is already wrapped around your arm. It |ytugs|n, and you 
stumble toward the water.

Another tentacle catches your leg.

The water is getting closer.
""",
        "choices": [
            {"text": "Keep struggling", "goto": "dragged_in"},
            {"text": "Go limp (maybe it'll lose interest)", "goto": "go_limp"},
        ]
    },
    
    "pull_free": {
        "text": """
You plant your feet and pull with all your strength. The 
tentacle tightens—it's like fighting a constrictor—but you 
manage to keep your footing.

For about three seconds.

Then two more tentacles join the first, and your resistance 
becomes irrelevant.
""",
        "goto": "dragged_in"
    },
    
    "grab_knife": {
        "text": """
Your free hand finds your knife. The blade bites into the 
tentacle, and the creature makes an awful shrieking sound 
from somewhere beneath the water.

The grip on your arm loosens. You tear free and stumble 
backward, putting distance between yourself and the shore.

The tentacles retreat beneath the surface, taking your 
fishing rod with them. Your arm is red and welted where the 
thing grabbed you, but you're free.

Maybe fish somewhere else next time.
""",
        "effects": [
            {"type": "take_item", "key": "fishing rod"},
            {"type": "apply_effect", "effect_key": "welted", "category": "debuff", "duration": 3600},
        ],
        "end": True
    },
    
    "go_limp": {
        "text": """
You stop fighting. Maybe if you're not interesting prey, 
it'll let you go.

The tentacles pause. Consider. You feel them |ytasting|n 
you somehow, sensing your surrender.

Then they pull you into the water anyway.

But... gently. The creature seems intrigued by your 
submission. Perhaps that will work in your favor.

Or perhaps not.
""",
        "effects": [
            {"type": "set_flag", "flag": "submitted", "value": True},
        ],
        "goto": "underwater"
    },
    
    "dragged_in": {
        "text": """
The water closes over your head.

For a terrifying moment, you're sure you're going to drown. 
But the tentacles adjust, pulling you through the water at 
speed but keeping your head above the surface—barely.

The creature is taking you somewhere.

Its lair, probably.

You should have picked a different hobby.
""",
        "goto": "underwater"
    },
    
    "underwater": {
        "text": """
|x[The scene continues with whatever the lake-tentacle-thing 
has planned for you. This is where the content would be 
expanded in the full game.]|n

Some time later, you drag yourself back onto shore, soaking 
wet and thoroughly... interacted with.

The creature let you go eventually. Whether out of boredom, 
satisfaction, or just losing interest, you're not sure. And 
you're not going back to ask.

Your fishing rod is gone. So is most of your dignity. But 
you're alive, and frankly, that's better than you expected.
""",
        "effects": [
            {"type": "take_item", "key": "fishing rod"},
            {"type": "apply_effect", "effect_key": "tentacle_slimed", "category": "debuff", "duration": 3600},
            {"type": "apply_effect", "effect_key": "used", "category": "status", "duration": 300},
        ],
        "end": True
    }
}

register_scene("fishing_tentacle_01", FISHING_TENTACLE_SCENE)
