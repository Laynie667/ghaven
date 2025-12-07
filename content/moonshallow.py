"""
Moonshallow Pond Content
========================

Fishing area south of the Grove. Fish, frogs, water lilies.
Safe newbie area with LIGHT water-related hazards.

Areas:
- Pond Shore (tutorial, common fish)
- Lily Pad Shallows (frogs, small fish, plants)
- Deep Pool (bigger fish, deeper hazards)
- Moonlit Cove (rare night fish, mysterious)
"""

from world.scenes import register_scene
from world.triggers import add_trigger
from world.resources import create_resource_node

# =============================================================================
# RESOURCE DEFINITIONS  
# =============================================================================

MOONSHALLOW_RESOURCES = {
    # POND SHORE
    "basic_fishing_spot": {
        "key": "calm waters",
        "type": "fishing",
        "yields": [
            {"key": "pond minnow", "rarity": "common", "weight": 50},
            {"key": "bluegill", "rarity": "common", "weight": 30},
            {"key": "small carp", "rarity": "uncommon", "weight": 15},
            {"key": "golden koi", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 300,
        "per_player": True,
        "desc": "A peaceful stretch of shore, perfect for beginner fishing.",
    },
    
    "lily_pad_cluster": {
        "key": "lily pad cluster",
        "type": "forage",
        "yields": [
            {"key": "water lily", "rarity": "common", "weight": 60},
            {"key": "lotus blossom", "rarity": "uncommon", "weight": 30},
            {"key": "moonpetal lily", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 3,
        "respawn_time": 600,
        "desc": "A cluster of lily pads with beautiful flowers.",
    },
    
    # LILY PAD SHALLOWS
    "frog_spot": {
        "key": "muddy bank",
        "type": "bugs",  # Frogs count as catchable creatures
        "yields": [
            {"key": "green frog", "rarity": "common", "weight": 50},
            {"key": "spotted frog", "rarity": "common", "weight": 30},
            {"key": "tree frog", "rarity": "uncommon", "weight": 15},
            {"key": "golden frog", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 4,
        "respawn_time": 450,
        "desc": "A muddy bank where frogs like to gather.",
    },
    
    "shallow_fish": {
        "key": "shallow pool",
        "type": "fishing",
        "yields": [
            {"key": "tadpole", "rarity": "common", "weight": 40},
            {"key": "pond snail", "rarity": "common", "weight": 30},
            {"key": "freshwater shrimp", "rarity": "uncommon", "weight": 20},
            {"key": "crawdad", "rarity": "uncommon", "weight": 10},
        ],
        "max_harvests": 6,
        "respawn_time": 300,
        "desc": "A shallow pool teeming with small aquatic life.",
    },
    
    # DEEP POOL
    "deep_fishing": {
        "key": "deep waters",
        "type": "fishing",
        "yields": [
            {"key": "largemouth bass", "rarity": "common", "weight": 40},
            {"key": "catfish", "rarity": "common", "weight": 30},
            {"key": "pike", "rarity": "uncommon", "weight": 20},
            {"key": "giant carp", "rarity": "rare", "weight": 8},
            {"key": "ancient koi", "rarity": "epic", "weight": 2},
        ],
        "max_harvests": 3,
        "respawn_time": 900,
        "desc": "Deep, dark waters where larger fish lurk.",
    },
    
    # MOONLIT COVE
    "night_fishing": {
        "key": "moonlit waters",
        "type": "fishing",
        "yields": [
            {"key": "moonfish", "rarity": "uncommon", "weight": 40},
            {"key": "silverscale", "rarity": "uncommon", "weight": 30},
            {"key": "starlight bass", "rarity": "rare", "weight": 20},
            {"key": "lunar eel", "rarity": "epic", "weight": 8},
            {"key": "ghost fish", "rarity": "legendary", "weight": 2},
        ],
        "max_harvests": 2,
        "respawn_time": 1800,
        "time_available": ["night", "midnight"],
        "desc": "Waters that shimmer with reflected moonlight.",
    },
    
    "glowing_algae": {
        "key": "glowing algae patch",
        "type": "forage",
        "yields": [
            {"key": "bioluminescent algae", "rarity": "uncommon", "weight": 70},
            {"key": "moonmoss", "rarity": "rare", "weight": 25},
            {"key": "starlight essence", "rarity": "epic", "weight": 5},
        ],
        "max_harvests": 2,
        "respawn_time": 1200,
        "time_available": ["night", "midnight"],
        "desc": "Patches of algae that glow softly in the darkness.",
    },
}


# =============================================================================
# ROOM TRIGGERS
# =============================================================================

MOONSHALLOW_TRIGGERS = {
    # Pond Shore - welcoming
    "shore_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|gWelcome to Moonshallow Pond!|n

The water stretches before you, calm and inviting. Fish dart 
beneath the surface, and frogs croak from the lily pads.

|wTip:|n Use |wfish|n to try your luck, or |wcatch|n for frogs!
"""}
        ],
    },
    
    "shore_splash": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "A fish jumps, catching the light before splashing back down."}
        ],
    },
    
    # Lily Pad Shallows
    "shallows_frogs": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "A chorus of frogs serenades you from the lily pads."}
        ],
    },
    
    "shallows_dragonfly": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.15}],
        "effects": [
            {"type": "message", "text": "A brilliant blue dragonfly hovers in front of your face before darting away."}
        ],
    },
    
    # Deep Pool - slightly ominous
    "deep_warning": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
The water here is darker, deeper. You can't see the bottom.

Something large moves beneath the surface. Probably just a big 
fish. Probably.

The fishing is better here, but be careful leaning too close to 
the edge.
"""}
        ],
    },
    
    "deep_ripple": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.25}],
        "effects": [
            {"type": "message", "text": "|xSomething large displaces water near the center of the pool. You don't see what.|n"}
        ],
    },
    
    # Moonlit Cove - magical at night
    "cove_night": {
        "type": "enter",
        "conditions": [
            {"type": "time_in", "values": ["night", "midnight"]}
        ],
        "effects": [
            {"type": "message", "text": "The cove glows with reflected moonlight and bioluminescent algae. It's breathtaking."}
        ],
    },
    
    "cove_day": {
        "type": "enter",
        "conditions": [
            {"type": "time_in", "values": ["morning", "noon", "afternoon"]}
        ],
        "effects": [
            {"type": "message", "text": "The cove is peaceful but ordinary in daylight. It's said to be magical at night..."}
        ],
    },
}


# =============================================================================
# SCENES - Pond Encounters
# =============================================================================

# Something grabs your line...
FISHING_SURPRISE_SCENE = {
    "id": "moonshallow_fishing_01",
    "title": "Something's On The Line",
    "tags": ["fishing", "hazard", "moonshallow", "mild"],
    
    "start": {
        "text": """
Your line goes |ytaut|n. Something's pulling hard—much harder 
than the fish around here usually do.

You brace yourself and pull back, but whatever's on the other 
end pulls harder. Your feet start sliding toward the water.

This is either a really big fish or something else entirely.
""",
        "choices": [
            {"text": "Hold on and keep pulling!", "goto": "hold"},
            {"text": "Let go of the rod", "goto": "release"},
            {"text": "Dive in after it", "goto": "dive"},
        ]
    },
    
    "hold": {
        "text": """
You dig your heels in and pull with everything you've got. The 
line screams, your muscles burn—

And then, with a tremendous splash, your catch breaks the surface.

It's... a turtle. A very large, very annoyed turtle, tangled in 
your fishing line. It glares at you with ancient, disappointed 
eyes.

"Hrrrmph," it says. Because apparently this turtle can talk.

"Young folk. Always fishing where they shouldn't. Untangle me."
""",
        "choices": [
            {"text": "Carefully untangle the turtle", "goto": "untangle"},
            {"text": "\"Sorry! I didn't mean to!\"", "goto": "apologize"},
            {"text": "Try to keep it as a catch", "goto": "keep_turtle"},
        ]
    },
    
    "release": {
        "text": """
You let go of the rod. It vanishes into the water instantly, 
pulled under by whatever was on the other end.

For a moment, nothing happens.

Then a turtle head surfaces, your rod clamped in its beak. It 
gives you a look of pure disappointment, drops the rod on the 
shore, and sinks back beneath the water.

You get the distinct impression you've been judged and found 
wanting.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "judged", 
             "category": "status", "duration": 300}
        ],
        "end": True
    },
    
    "dive": {
        "text": """
You abandon all reason and leap into the pond after your catch.

The water is |ycold|n. And dark. And you immediately realize 
this was a terrible idea.

Something large bumps against you underwater. Then something 
else. You flail back to the surface, gasping, to find yourself 
surrounded by curious turtles.

"Brave," rumbles the largest one. "Stupid. But brave."

The turtles escort you back to shore with surprising gentleness, 
then disappear beneath the surface. You're soaked and cold, but 
somehow you feel like you've earned their respect.

Your rod floats to shore a moment later. Still intact, somehow.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "soaked", 
             "category": "debuff", "duration": 900},
            {"type": "add_tag", "tag": "turtle_respect", "category": "encounters"}
        ],
        "end": True
    },
    
    "untangle": {
        "text": """
You wade into the shallows and carefully work the line free 
from the turtle's legs. It's patient, watching you with those 
ancient eyes.

"Better," it says when you finish. "You're polite, at least."

It starts to sink back into the water, then pauses.

"Fish the south shore tomorrow at dawn. The moonfish school 
there, just for an hour. My gift for the help."

Then it's gone, leaving barely a ripple.

That was... weird. But potentially profitable.
""",
        "effects": [
            {"type": "add_tag", "tag": "turtle_tip", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "turtle_blessing", 
             "category": "buff", "duration": 3600}
        ],
        "end": True
    },
    
    "apologize": {
        "text": """
"Sorry! I'm so sorry! I didn't know you were down there!"

The turtle's glare softens slightly. "Hmph. At least you have 
manners. Most just scream or run."

It waits pointedly until you untangle it, then sinks back into 
the deep.

"Be more careful where you cast," it calls back. "The deep 
pool is our home."

You make a mental note to fish more carefully in the future.
""",
        "end": True
    },
    
    "keep_turtle": {
        "text": """
"Maybe I could—" you start.

The turtle's eyes narrow. "Don't. Even. Think about it."

It makes a sound that might be a laugh. "You couldn't lift me 
anyway, small one. But I appreciate the ambition."

With a flick of its tail, it splashes water directly into your 
face and disappears beneath the surface.

You stand there, dripping, as turtle laughter echoes across 
the pond.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "embarrassed", 
             "category": "status", "duration": 300}
        ],
        "end": True
    }
}

register_scene("moonshallow_fishing_01", FISHING_SURPRISE_SCENE)


# Frog encounter - they're everywhere and very friendly
FROG_SWARM_SCENE = {
    "id": "moonshallow_frogs_01",
    "title": "Frog Convention",
    "tags": ["encounter", "frog", "moonshallow", "cute", "comedy"],
    
    "start": {
        "text": """
You're walking along the shore when you notice the frogs.

Not just a few frogs. Dozens of frogs. All of them watching 
you. All of them hopping closer.

"Ribbit," says one.

"Ribbit," agree the others.

They're surrounding you. Adorably. Inescapably.
""",
        "choices": [
            {"text": "Try to walk through them", "goto": "wade"},
            {"text": "Sit down and accept your fate", "goto": "accept"},
            {"text": "Offer them food", "goto": "food",
             "condition": {"type": "has_item", "item": "wild berries"}},
            {"text": "Ribbit back at them", "goto": "ribbit"},
        ]
    },
    
    "wade": {
        "text": """
You try to gently step through the frog congregation, but for 
every one you avoid, three more hop into your path.

Eventually you give up and just... walk. Frogs bounce off your 
feet, hop onto your shoes, hitch rides on your ankles.

By the time you're clear, you have acquired four frogs who 
refuse to leave. They've claimed you.

Maybe they'll get bored eventually?
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "frog_covered", 
             "category": "status", "duration": 600}
        ],
        "end": True
    },
    
    "accept": {
        "text": """
You sit down on a rock. If this is how you die, so be it.

The frogs seem pleased. They hop onto your lap, your shoulders, 
your head. One particularly bold frog settles right on top of 
your hair like a tiny green hat.

You sit there for several minutes, absolutely covered in frogs.

It's... actually kind of nice? They're warm, and their little 
heartbeats are weirdly soothing.

Eventually, as if responding to some signal you can't hear, 
they all hop away at once. The frog meeting is adjourned.

You feel strangely blessed.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "frog_blessed", 
             "category": "buff", "duration": 1800}
        ],
        "end": True
    },
    
    "food": {
        "text": """
You pull out some berries and scatter them on the ground.

The effect is immediate. Every frog in the area goes |yinsane|n, 
hopping over each other to get to the food. In the chaos, you 
slip away unnoticed.

From a safe distance, you watch the frog feeding frenzy. It's 
like a tiny, adorable riot.

Worth one berry, probably.
""",
        "effects": [
            {"type": "take_item", "key": "wild berries"}
        ],
        "end": True
    },
    
    "ribbit": {
        "text": """
"Ribbit," you say, trying to match their tone.

Dead silence. Every frog stares at you.

Then, as one, they all ribbit back. Louder. It sounds almost... 
approving?

The largest frog hops forward and places something at your feet: 
a small, perfectly round pearl. A gift, apparently.

Then the congregation disperses, leaving you alone with your 
new treasure and a lot of questions about frog society.
""",
        "effects": [
            {"type": "give_item", "key": "frog pearl", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "frog_speaker", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("moonshallow_frogs_01", FROG_SWARM_SCENE)


# Something in the deep pool - slightly spookier
DEEP_POOL_SCENE = {
    "id": "moonshallow_deep_01",
    "title": "Something in the Deep",
    "tags": ["encounter", "mysterious", "moonshallow", "mild_spooky"],
    
    "start": {
        "text": """
You're fishing at the deep pool's edge when the water goes 
completely still. Unnaturally still.

Something rises from the depths. Not quickly—slowly, like it 
has all the time in the world.

First you see eyes. Large, luminous, entirely too intelligent 
for something that lives in a pond.

Then the rest of it emerges: a fish the size of a dog, covered 
in scales that shimmer with impossible colors.

It hovers at the surface, watching you.

Waiting.
""",
        "choices": [
            {"text": "\"Hello?\"", "goto": "greet"},
            {"text": "Back away slowly", "goto": "retreat"},
            {"text": "Offer your bait", "goto": "offer"},
            {"text": "Try to catch it", "goto": "catch"},
        ]
    },
    
    "greet": {
        "text": """
"Hello," you say, feeling a bit foolish for talking to a fish.

The fish blinks slowly. Its mouth opens, and a sound emerges— 
not words exactly, but you understand anyway:

|y*Polite. Unusual. Most scream.*|n

It swims in a slow circle, never breaking eye contact.

|y*I am old. I remember when this pond was a sea. What do you 
seek, small one?*|n
""",
        "choices": [
            {"text": "\"I'm just fishing.\"", "goto": "just_fishing"},
            {"text": "\"What are you?\"", "goto": "what_are_you"},
            {"text": "\"I seek nothing. I was just curious.\"", "goto": "curious"},
        ]
    },
    
    "retreat": {
        "text": """
You back away from the water's edge. The ancient fish watches 
you go, its expression unreadable.

Just before you're out of sight, you hear—or feel—something 
like a sigh.

|y*Another time, perhaps.*|n

The fish sinks back into the depths, and the water returns to 
normal. You can't shake the feeling that you missed something 
important.
""",
        "end": True
    },
    
    "offer": {
        "text": """
You hold out your bait, feeling foolish. Why would an ancient 
pond-god want a worm?

The fish makes a sound like bubbling laughter.

|y*Charming. You offer tribute to the deep.*|n

It doesn't take the bait, but it seems pleased by the gesture.

|y*For your courtesy: fish the eastern shore at moonrise. My 
children gather there. They will not flee from you.*|n

It sinks back into the deep, leaving barely a ripple.

That was either very helpful advice or a trap. Only one way to 
find out.
""",
        "effects": [
            {"type": "add_tag", "tag": "deep_blessing", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "fish_favored", 
             "category": "buff", "duration": 7200}
        ],
        "end": True
    },
    
    "catch": {
        "text": """
You cast your line toward the creature before your brain can 
talk you out of it.

The ancient fish doesn't move. Your hook passes right through 
it, like it's made of water and moonlight.

|y*Child.*|n

The voice in your head sounds amused. Condescending. Ancient.

|y*You cannot catch what you cannot comprehend. But your 
ambition is noted.*|n

It sinks back into the depths, and you're left with the 
distinct impression that you've embarrassed yourself in front 
of something very old and very patient.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "humbled", 
             "category": "status", "duration": 600}
        ],
        "end": True
    },
    
    "just_fishing": {
        "text": """
|y*Fishing. In my pool.*|n

The ancient fish sounds neither angry nor pleased. Just... 
observing.

|y*The small ones are yours to take. They are numerous and 
unimportant. But if you ever hook something that pulls like 
the tide itself—let go.*|n

It sinks slowly back into the depths.

|y*Some things are not meant to be caught. Remember.*|n

Solid advice, probably.
""",
        "effects": [
            {"type": "add_tag", "tag": "deep_warning", "category": "encounters"}
        ],
        "end": True
    },
    
    "what_are_you": {
        "text": """
|y*I am what I have always been. What I will always be.*|n

The fish circles slowly, its impossible scales catching light 
that isn't there.

|y*When your kind first came to this place, I was here. When 
your kind is dust and memory, I will still be here. I am the 
Deep. I am the pond's dream of being an ocean.*|n

It fixes you with one enormous eye.

|y*And you, small one, are interesting. I will remember you.*|n

It sinks back into the darkness, leaving you with the distinct 
sense that being remembered by something like that might not be 
entirely comfortable.
""",
        "effects": [
            {"type": "add_tag", "tag": "deep_noticed", "category": "encounters"}
        ],
        "end": True
    },
    
    "curious": {
        "text": """
|y*Curiosity. The most dangerous trait. The most valuable.*|n

The ancient fish seems to smile, if fish can smile.

|y*Curiosity brought your kind to walk upright. Curiosity 
will bring them to the stars. And curiosity—*|n

It leans closer, those vast eyes filling your vision.

|y*—brings you to my pool, to meet something older than names.*|n

It touches your hand with something—a fin? a blessing?—and 
withdraws into the deep.

|y*Be curious, small one. But be careful where your curiosity 
leads. Some depths have no bottom.*|n

Your hand tingles where it touched you. Something has changed, 
though you're not sure what.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "deep_touched", 
             "category": "status", "duration": 86400},
            {"type": "add_tag", "tag": "deep_blessed", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("moonshallow_deep_01", DEEP_POOL_SCENE)


# Moonlit fishing - what you catch at night
MOONLIT_CATCH_SCENE = {
    "id": "moonshallow_moonlit_01",
    "title": "Moonlit Catch",
    "tags": ["fishing", "night", "moonshallow", "magical"],
    
    "start": {
        "text": """
You're fishing the moonlit waters when something strange happens: 
your line begins to |yglow|n.

The light travels down toward the water, and for a moment you 
see the pond lit from within—fish swimming in lazy circles, 
plants swaying, and something rising toward your hook.

The surface breaks, and you find yourself holding a fish made 
entirely of moonlight.

It doesn't struggle. It just... is. Beautiful. Impossible. 
Looking at you with eyes like stars.
""",
        "choices": [
            {"text": "Keep it", "goto": "keep"},
            {"text": "Let it go", "goto": "release"},
            {"text": "\"What are you?\"", "goto": "ask"},
        ]
    },
    
    "keep": {
        "text": """
You carefully place the moonfish in your bucket.

It doesn't flop or gasp. It simply rests there, glowing softly, 
watching you without judgment.

The museum will want this. The Curator especially. Something 
this beautiful, this impossible—she'll have questions.

But for now, it's yours. A piece of captured moonlight.
""",
        "effects": [
            {"type": "give_item", "key": "moonlight fish", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "release": {
        "text": """
You lower your hands to the water. The moonfish slides free, 
swimming in a slow circle before diving back into the depths.

But before it disappears, it brushes against you—and something 
transfers. Warmth. Light. A feeling like being smiled at by the 
moon itself.

You could have kept it. Sold it. Displayed it.

But some things are more valuable free.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "moonblessed", 
             "category": "buff", "duration": 14400},
            {"type": "add_tag", "tag": "moonfish_mercy", "category": "encounters"}
        ],
        "end": True
    },
    
    "ask": {
        "text": """
The moonfish tilts its head—can fish tilt their heads?—and 
you hear the answer without sound:

|y*I am what the moon dreams when it watches the water. I am 
the reflection that swims away. I am the light that lives.*|n

It doesn't answer more than that. Perhaps it can't. Perhaps 
that's all the answer there is.

What do you do with a fish made of dreams?
""",
        "choices": [
            {"text": "Keep this beautiful thing", "goto": "keep"},
            {"text": "Let the dream swim free", "goto": "release"},
        ]
    }
}

register_scene("moonshallow_moonlit_01", MOONLIT_CATCH_SCENE)


# =============================================================================
# BUILDER HELPER FUNCTION  
# =============================================================================

def setup_moonshallow_room(room, area_type):
    """
    Set up a Moonshallow Pond room with resources and triggers.
    
    Args:
        room: The room object
        area_type: One of "shore", "shallows", "deep", "cove"
    """
    from world.triggers import add_trigger
    from world.random_events import register_ambient_events
    
    # Ambient events for all pond rooms
    register_ambient_events(room, [
        "rustling_leaves",
        "bird_song",
        "frog_chorus",
    ])
    
    if area_type == "shore":
        for key in ["shore_entry", "shore_splash"]:
            trigger = MOONSHALLOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Frog swarm (rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "moonshallow_frogs_01"}],
            conditions=[{"type": "random", "chance": 0.03}]
        )
    
    elif area_type == "shallows":
        for key in ["shallows_frogs", "shallows_dragonfly"]:
            trigger = MOONSHALLOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # More likely frog encounter here
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "moonshallow_frogs_01"}],
            conditions=[{"type": "random", "chance": 0.05}]
        )
    
    elif area_type == "deep":
        for key in ["deep_warning", "deep_ripple"]:
            trigger = MOONSHALLOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Fishing surprise (turtle)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "moonshallow_fishing_01"}],
            conditions=[
                {"type": "random", "chance": 0.05},
                {"type": "has_item", "item": "fishing rod"}
            ]
        )
        
        # Deep pool entity (rare, first time only)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "moonshallow_deep_01"}],
            conditions=[
                {"type": "random", "chance": 0.02},
                {"type": "lacks_tag", "tag": "deep_noticed", "category": "encounters"},
                {"type": "lacks_tag", "tag": "deep_warning", "category": "encounters"},
                {"type": "lacks_tag", "tag": "deep_blessed", "category": "encounters"}
            ]
        )
    
    elif area_type == "cove":
        for key in ["cove_night", "cove_day"]:
            trigger = MOONSHALLOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Moonlit catch (night only)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "moonshallow_moonlit_01"}],
            conditions=[
                {"type": "random", "chance": 0.08},
                {"type": "time_in", "values": ["night", "midnight"]},
                {"type": "has_item", "item": "fishing rod"}
            ]
        )
