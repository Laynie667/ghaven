"""
Tidepools Content
=================

Beach area south of Moonshallow Pond. Shells, crabs, shore creatures.
Safe newbie area with water-themed hazards - tides, things that grab,
hidden treasures.

Areas:
- Sandy Beach (shells, sandcastles, beachcombing)
- Tidepool Rocks (crabs, small fish, sea plants)
- Rocky Shore (shore fishing, mussels, sea glass)
- Hidden Cove (rare shells, treasure, low tide only)
"""

from world.scenes import register_scene
from world.triggers import add_trigger
from world.resources import create_resource_node

# =============================================================================
# RESOURCE DEFINITIONS
# =============================================================================

TIDEPOOLS_RESOURCES = {
    # SANDY BEACH
    "shell_scatter": {
        "key": "shell-scattered sand",
        "type": "forage",
        "yields": [
            {"key": "common shell", "rarity": "common", "weight": 50},
            {"key": "spiral shell", "rarity": "common", "weight": 30},
            {"key": "sand dollar", "rarity": "uncommon", "weight": 15},
            {"key": "perfect conch", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 6,
        "respawn_time": 300,
        "desc": "Shells scattered across the sand, left by the tide.",
    },
    
    "driftwood_pile": {
        "key": "driftwood pile",
        "type": "forage",
        "yields": [
            {"key": "driftwood", "rarity": "common", "weight": 60},
            {"key": "smooth driftwood", "rarity": "uncommon", "weight": 30},
            {"key": "carved driftwood", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 4,
        "respawn_time": 600,
        "desc": "A pile of sun-bleached driftwood.",
    },
    
    # TIDEPOOL ROCKS
    "tidepool": {
        "key": "tidepool",
        "type": "bugs",  # Crabs count as catchable
        "yields": [
            {"key": "hermit crab", "rarity": "common", "weight": 40},
            {"key": "shore crab", "rarity": "common", "weight": 35},
            {"key": "starfish", "rarity": "uncommon", "weight": 15},
            {"key": "sea urchin", "rarity": "uncommon", "weight": 8},
            {"key": "blue crab", "rarity": "rare", "weight": 2},
        ],
        "max_harvests": 4,
        "respawn_time": 450,
        "desc": "A pool of seawater left by the retreating tide.",
    },
    
    "seaweed_rocks": {
        "key": "seaweed-covered rocks",
        "type": "forage",
        "yields": [
            {"key": "green seaweed", "rarity": "common", "weight": 50},
            {"key": "kelp", "rarity": "common", "weight": 30},
            {"key": "sea lettuce", "rarity": "uncommon", "weight": 15},
            {"key": "dulse", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 400,
        "desc": "Rocks covered in various types of edible seaweed.",
    },
    
    "tidepool_fish": {
        "key": "deep tidepool",
        "type": "fishing",
        "yields": [
            {"key": "tidepool sculpin", "rarity": "common", "weight": 50},
            {"key": "blenny", "rarity": "common", "weight": 30},
            {"key": "pipefish", "rarity": "uncommon", "weight": 15},
            {"key": "tiny octopus", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 3,
        "respawn_time": 500,
        "desc": "A deeper tidepool where small fish have been trapped.",
    },
    
    # ROCKY SHORE
    "mussel_bed": {
        "key": "mussel bed",
        "type": "forage",
        "yields": [
            {"key": "common mussel", "rarity": "common", "weight": 60},
            {"key": "blue mussel", "rarity": "uncommon", "weight": 30},
            {"key": "pearl mussel", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 5,
        "respawn_time": 600,
        "desc": "Clusters of mussels clinging to the rocks.",
    },
    
    "sea_glass_spot": {
        "key": "tumbled rocks",
        "type": "forage",
        "yields": [
            {"key": "green sea glass", "rarity": "common", "weight": 40},
            {"key": "brown sea glass", "rarity": "common", "weight": 30},
            {"key": "blue sea glass", "rarity": "uncommon", "weight": 20},
            {"key": "red sea glass", "rarity": "rare", "weight": 8},
            {"key": "purple sea glass", "rarity": "epic", "weight": 2},
        ],
        "max_harvests": 4,
        "respawn_time": 900,
        "desc": "Smooth stones tumbled by the waves, with sea glass mixed in.",
    },
    
    "shore_fishing": {
        "key": "rocky outcrop",
        "type": "fishing",
        "yields": [
            {"key": "rockfish", "rarity": "common", "weight": 40},
            {"key": "sea bass", "rarity": "common", "weight": 30},
            {"key": "flounder", "rarity": "uncommon", "weight": 20},
            {"key": "lobster", "rarity": "rare", "weight": 8},
            {"key": "giant crab", "rarity": "epic", "weight": 2},
        ],
        "max_harvests": 3,
        "respawn_time": 900,
        "desc": "A rocky outcrop jutting into deeper water.",
    },
    
    # HIDDEN COVE
    "rare_shells": {
        "key": "pristine sand",
        "type": "forage",
        "yields": [
            {"key": "iridescent shell", "rarity": "uncommon", "weight": 40},
            {"key": "nautilus shell", "rarity": "rare", "weight": 35},
            {"key": "ancient shell", "rarity": "epic", "weight": 20},
            {"key": "mermaid's shell", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 2,
        "respawn_time": 1800,
        "desc": "Untouched sand where rare shells wash up.",
    },
    
    "treasure_spot": {
        "key": "suspicious sand",
        "type": "forage",
        "yields": [
            {"key": "old coin", "rarity": "uncommon", "weight": 50},
            {"key": "silver coin", "rarity": "rare", "weight": 30},
            {"key": "gold coin", "rarity": "epic", "weight": 15},
            {"key": "treasure map piece", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 1,
        "respawn_time": 7200,
        "desc": "The sand here looks like it's been disturbed recently.",
    },
}


# =============================================================================
# ROOM TRIGGERS
# =============================================================================

TIDEPOOLS_TRIGGERS = {
    # Sandy Beach
    "beach_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|gWelcome to the Tidepools!|n

The sound of waves fills the air as you step onto soft sand. 
Seagulls wheel overhead, and shells crunch underfoot.

|wTip:|n Use |wforage|n to collect shells and sea treasures!

|yNote:|n The tide comes in and out. Some areas are only 
accessible at low tide, and getting caught by the tide can 
be... exciting.
"""}
        ],
    },
    
    "beach_waves": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "A wave crashes against the shore, sending spray into the air."}
        ],
    },
    
    "beach_seagulls": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "Seagulls squabble over something in the sand nearby."}
        ],
    },
    
    # Tidepool Rocks
    "pools_splash": {
        "type": "enter",
        "effects": [
            {"type": "message", "text": "Water splashes between the rocks, filling pools with tiny ecosystems."}
        ],
    },
    
    "pools_scuttle": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.25}],
        "effects": [
            {"type": "message", "text": "Crabs scuttle away at your approach, hiding under rocks."}
        ],
    },
    
    # Rocky Shore
    "shore_spray": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "Waves crash against the rocks, sending salt spray across your face."}
        ],
    },
    
    "shore_warning": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
The rocks here are slippery with seaweed and spray. Better 
fishing than the beach, but watch your footing.

And keep an eye on the tide. You don't want to get cut off.
"""}
        ],
    },
    
    # Hidden Cove
    "cove_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
You slip through a narrow gap in the rocks and find yourself 
in a hidden cove, sheltered from the wind and waves.

The sand here is pristine. Shells that would be crushed 
elsewhere lie perfect and whole. And there's something in 
the air—a sense of secrets, of treasure waiting to be found.

But the entrance will be underwater at high tide. Don't 
linger too long.
"""}
        ],
    },
    
    "cove_treasure_feeling": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "You have a strange feeling that something valuable is buried nearby..."}
        ],
    },
}


# =============================================================================
# SCENES
# =============================================================================

# Crab encounter - they fight back
CRAB_ENCOUNTER_SCENE = {
    "id": "tidepools_crab_01",
    "title": "Crabby Customer",
    "tags": ["encounter", "crab", "tidepools", "comedy"],
    
    "start": {
        "text": """
You reach into a tidepool to grab a crab—

And the crab grabs back.

Not a little crab, you realize too late. A |ybig|n crab. With 
claws like bolt cutters. And an attitude.

It locks onto your finger and |yclamps down|n.

|rOW!|n
""",
        "choices": [
            {"text": "Shake it off wildly", "goto": "shake"},
            {"text": "Dunk your hand back in the water", "goto": "dunk"},
            {"text": "Accept defeat and carefully remove it", "goto": "careful"},
            {"text": "Tickle it", "goto": "tickle"},
        ]
    },
    
    "shake": {
        "text": """
You flail your arm like a madman. The crab holds on with the 
determination of a creature that has never known fear.

People on the beach are staring. A child points and laughs.

Eventually, the crab gets bored (or dizzy) and releases, 
flying through the air and landing in a distant pool with a 
satisfying plop.

Your finger is bruised and bleeding. Your dignity is in worse 
shape.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "crab_pinch", 
             "category": "debuff", "duration": 1200},
            {"type": "apply_effect", "effect_key": "embarrassed", 
             "category": "status", "duration": 600}
        ],
        "end": True
    },
    
    "dunk": {
        "text": """
You shove your hand back into the water. The crab, finding 
itself in its element, relaxes slightly—just enough for you 
to shake it loose.

It sinks to the bottom of the pool, claws raised threateningly. 
You swear it's glaring at you.

Your finger is sore, but at least you still have it. The crab 
won this round.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "sore_finger", 
             "category": "debuff", "duration": 600}
        ],
        "end": True
    },
    
    "careful": {
        "text": """
You grit your teeth and carefully work to release the claw. 
The crab seems surprised by your patience—most victims panic.

Slowly, carefully, you apply pressure to the right spots and 
the claw opens.

The crab drops into the pool and scuttles away, looking 
almost disappointed.

Your finger is bruised but intact. And you've learned 
something about crab anatomy that might be useful later.
""",
        "effects": [
            {"type": "add_tag", "tag": "crab_wise", "category": "encounters"}
        ],
        "end": True
    },
    
    "tickle": {
        "text": """
In desperation, you try tickling the crab's underside.

The crab freezes. Its eyes waggle in apparent confusion. Then, 
incredibly, the claw loosens.

You withdraw your finger, and the crab sinks back into the 
pool, looking deeply unsettled by the experience.

You're not sure what just happened, but you're keeping that 
trick in your back pocket.
""",
        "effects": [
            {"type": "add_tag", "tag": "crab_tickler", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("tidepools_crab_01", CRAB_ENCOUNTER_SCENE)


# Tide coming in
TIDE_SCENE = {
    "id": "tidepools_tide_01",
    "title": "Rising Waters",
    "tags": ["hazard", "tide", "tidepools", "action"],
    
    "start": {
        "text": """
You've been exploring the rocks, finding treasures, when you 
notice something troubling.

The water is higher than it was.

Much higher.

You turn to head back to the beach and realize the path you 
took is now underwater. Waves are crashing over the rocks 
between you and safety.

The tide came in while you weren't paying attention.
""",
        "choices": [
            {"text": "Wade through the shallows", "goto": "wade"},
            {"text": "Wait it out on the rocks", "goto": "wait"},
            {"text": "Swim for it", "goto": "swim"},
            {"text": "Look for another way", "goto": "look"},
        ]
    },
    
    "wade": {
        "text": """
You step into the water, feeling for footing on the slippery 
rocks beneath.

The current is stronger than it looks. Water swirls around 
your knees, then your thighs. A wave splashes over you.

But you keep your footing, barely, and eventually stagger 
onto the beach—soaked, salty, but safe.

Note to self: watch the tide tables next time.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "soaked", 
             "category": "debuff", "duration": 1800}
        ],
        "end": True
    },
    
    "wait": {
        "text": """
You find the highest rock and settle in to wait.

And wait.

And wait.

The tide takes hours to go back out. You're cold, wet from 
spray, hungry, and thoroughly miserable by the time the path 
is passable again.

But at least you didn't drown. Small victories.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "chilled", 
             "category": "debuff", "duration": 3600},
            {"type": "apply_effect", "effect_key": "hungry", 
             "category": "debuff", "duration": 1800}
        ],
        "end": True
    },
    
    "swim": {
        "text": """
You dive in and start swimming.

Bad idea.

The current grabs you immediately, pulling you sideways. You 
fight against it, swallowing salt water, arms burning.

Just when you think you can't go on, your feet touch sand. 
You stagger onto the beach and collapse, gasping.

A group of fishermen applaud sarcastically from the dock.

"Tide tables are free, friend," one calls.

You're never living this down.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "exhausted", 
             "category": "debuff", "duration": 3600},
            {"type": "apply_effect", "effect_key": "soaked", 
             "category": "debuff", "duration": 1800},
            {"type": "apply_effect", "effect_key": "embarrassed", 
             "category": "status", "duration": 600}
        ],
        "end": True
    },
    
    "look": {
        "text": """
You scan the rocks, looking for another route. There—a line 
of higher stones, still above the water, leading around the 
flooded section.

It requires some climbing and a few precarious jumps, but you 
make it across without getting more than your feet wet.

From the beach, you look back at the rising water covering 
the path you took. That was close.

But you also spotted something interesting during your 
detour—a cave entrance, normally hidden by the tide. Worth 
investigating later...
""",
        "effects": [
            {"type": "add_tag", "tag": "found_sea_cave", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("tidepools_tide_01", TIDE_SCENE)


# Something grabs you from the water
GRABBY_THING_SCENE = {
    "id": "tidepools_grab_01",
    "title": "Something in the Pool",
    "tags": ["encounter", "creature", "tidepools", "mild_spooky"],
    
    "start": {
        "text": """
You're reaching into a deep pool, feeling for shells, when 
something wraps around your wrist.

Not a crab. Something softer. More flexible. With |ysuction 
cups|n.

A tentacle.

It's not pulling hard—yet—but it's definitely not letting go.

In the dim water, you see more movement. Whatever this is, 
it's bigger than the pool should be able to hold.
""",
        "choices": [
            {"text": "Yank your arm out", "goto": "yank"},
            {"text": "Freeze and stay calm", "goto": "calm"},
            {"text": "Reach in with your other hand", "goto": "reach"},
            {"text": "Speak to it", "goto": "speak"},
        ]
    },
    
    "yank": {
        "text": """
You rip your arm free, stumbling backward. The tentacle 
releases with a wet pop, leaving round red marks where the 
suction cups gripped.

In the pool, something dark sinks deeper, vanishing into a 
crevice that leads to the sea. Two large eyes catch the light 
for just a moment.

Then it's gone.

You don't reach into pools without looking first anymore.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "sucker_marks", 
             "category": "status", "duration": 3600}
        ],
        "end": True
    },
    
    "calm": {
        "text": """
You force yourself to stay still. The tentacle explores your 
wrist, your fingers. It seems curious, not aggressive.

After a long moment, it releases you—and something presses 
into your palm. Hard. Round. Smooth.

When you withdraw your hand, you're holding a pearl. Perfect, 
iridescent, valuable.

A gift? An apology? A bribe?

Whatever it was sinks back into the deep, leaving you with 
a treasure and a story.
""",
        "effects": [
            {"type": "give_item", "key": "sea pearl", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "reach": {
        "text": """
Against all good sense, you reach in with your other hand to 
see what you're dealing with.

Another tentacle catches it.

Now both your arms are in the pool, and the creature is 
pulling you closer. Your face is inches from the water.

This was a mistake—

But then the pulling stops. The creature surfaces slightly, 
and you see it: a small octopus, barely bigger than a cat. 
It blinks at you with intelligent eyes, tentacles still 
wrapped around your wrists.

It's not attacking. It's... playing?

After a moment, it releases you, does a little flip, and 
squirts away. Apparently you passed some kind of test.
""",
        "effects": [
            {"type": "add_tag", "tag": "octopus_friend", "category": "encounters"}
        ],
        "end": True
    },
    
    "speak": {
        "text": """
"Um. Hello?"

The tentacle pauses. In the pool, something shifts.

Two enormous eyes rise to just below the surface, watching 
you. The creature is bigger than you thought—much bigger.

|y*Hello.*|n

The voice is in your head, wet and strange.

|y*You are the first to speak. Most scream.*|n

The tentacle releases you, but the eyes stay fixed on yours.

|y*I am old. I remember when this was deep water. Now I am 
trapped in the shallows, waiting for the tide.*|n

It sinks slightly.

|y*Visit me when the water is high. I have stories to trade.*|n

The eyes vanish into the deep. When the tide goes out later, 
the pool is empty.

But you know it'll be back.
""",
        "effects": [
            {"type": "add_tag", "tag": "pool_ancient", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("tidepools_grab_01", GRABBY_THING_SCENE)


# Hidden cove treasure
COVE_TREASURE_SCENE = {
    "id": "tidepools_treasure_01",
    "title": "X Marks the Spot",
    "tags": ["discovery", "treasure", "tidepools", "adventure"],
    
    "start": {
        "text": """
You're digging in the hidden cove's sand—just idly, really— 
when your fingers hit something solid.

Wood.

Heart pounding, you dig faster. A corner emerges. Then a 
edge. Then a clasp.

It's a chest. An actual treasure chest, buried in the sand 
of a hidden cove. Like something out of a story.

It's locked, but the wood is old and salt-worn.
""",
        "choices": [
            {"text": "Break it open", "goto": "break"},
            {"text": "Try to pick the lock", "goto": "pick"},
            {"text": "Look for a key nearby", "goto": "search"},
            {"text": "Take the whole chest", "goto": "take_chest"},
        ]
    },
    
    "break": {
        "text": """
You find a rock and smash the lock. The old metal gives way 
easily, and the lid creaks open.

Inside: coins. Old ones, tarnished by salt and time, but 
definitely valuable. And beneath them, wrapped in oilcloth, 
a dagger with a jeweled hilt.

Not a king's ransom, but not bad for a day at the beach.

At the bottom of the chest is a piece of paper—a fragment 
of a map, showing what looks like an island.

There might be more where this came from.
""",
        "effects": [
            {"type": "give_currency", "amount": 200},
            {"type": "give_item", "key": "jeweled dagger", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "treasure map fragment", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "pick": {
        "text": """
You pull out a hairpin (doesn't everyone carry one?) and 
wiggle it in the lock. It's a simple mechanism, corroded 
by years of salt air.

|yClick.|n

The chest opens.

Inside, nestled in rotting velvet, is a necklace—gold chain, 
single sapphire pendant, still gleaming despite its age. 
And beneath it, a leather pouch of coins.

But the real treasure is at the bottom: a complete treasure 
map, showing the location of something called "The Captain's 
Hoard."

Whoever buried this chest wasn't done burying treasure.
""",
        "effects": [
            {"type": "give_currency", "amount": 150},
            {"type": "give_item", "key": "sapphire necklace", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "treasure map", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "treasure_hunter", "category": "encounters"}
        ],
        "end": True
    },
    
    "search": {
        "text": """
You dig around the chest, thinking like a pirate. Where 
would you hide a key?

Your fingers find something buried nearby—a bottle, sealed 
with wax. Inside is a small brass key and a note:

"For the clever ones. The chest is yours, but the real 
treasure is still waiting. Find the cave where the tide 
sings. The key opens more than you know."

The key fits the chest perfectly. Inside: modest coins and 
a golden compass that always points toward the Grove.

But the note is the real find. A treasure hunt awaits.
""",
        "effects": [
            {"type": "give_currency", "amount": 100},
            {"type": "give_item", "key": "golden compass", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "mysterious key", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "pirate's note", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "treasure_quest", "category": "encounters"}
        ],
        "end": True
    },
    
    "take_chest": {
        "text": """
Why break it when you can take the whole thing?

You dig out the chest—it's lighter than expected—and haul 
it up to the beach. Passersby stare as you walk past with 
an actual pirate chest under your arm.

You'll open it at home, properly. With tools. And maybe 
some dramatic lighting.

Whatever's inside, the story of finding it is almost better 
than the treasure itself.

Almost.
""",
        "effects": [
            {"type": "give_item", "key": "unopened treasure chest", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    }
}

register_scene("tidepools_treasure_01", COVE_TREASURE_SCENE)


# Mermaid sighting (rare)
MERMAID_SCENE = {
    "id": "tidepools_mermaid_01",
    "title": "A Face in the Waves",
    "tags": ["encounter", "mermaid", "tidepools", "magical", "rare"],
    
    "start": {
        "text": """
You're alone in the hidden cove when you hear singing.

It's not coming from the beach. It's coming from the water.

A head breaks the surface about fifty feet out—humanoid, 
but wrong. Too large eyes. Skin that shimmers like scales. 
Hair that floats like seaweed.

The singing stops. The mermaid—because that's what it is— 
watches you with ancient, curious eyes.
""",
        "choices": [
            {"text": "Wave hello", "goto": "wave"},
            {"text": "Stay very still", "goto": "still"},
            {"text": "Wade into the water", "goto": "wade"},
            {"text": "Run away", "goto": "run"},
        ]
    },
    
    "wave": {
        "text": """
You raise a hand and wave, feeling slightly foolish.

The mermaid tilts her head. Then, slowly, she raises a 
webbed hand and waves back.

She laughs—a sound like water over stones—and sinks beneath 
the waves.

A moment later, something washes up at your feet: a shell, 
perfect and spiraled, glowing faintly from within.

A gift. Or maybe just a hello.

You don't see her again that day. But sometimes, in the 
weeks to come, you hear singing from the water. And you 
wave at the waves, hoping she sees.
""",
        "effects": [
            {"type": "give_item", "key": "mermaid's shell", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "mermaid_friend", "category": "encounters"}
        ],
        "end": True
    },
    
    "still": {
        "text": """
You freeze, hardly daring to breathe. The mermaid watches 
you for a long moment, those too-large eyes unblinking.

Then she sings again—just a few notes, haunting and 
beautiful—and sinks beneath the surface.

You stand there until the sun sets, hoping she'll return.

She doesn't. Not today.

But you carry those notes in your memory, and sometimes 
you catch yourself humming them without realizing. You 
wonder if that's significant.
""",
        "effects": [
            {"type": "add_tag", "tag": "mermaid_seen", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "sea_longing", 
             "category": "status", "duration": 7200}
        ],
        "end": True
    },
    
    "wade": {
        "text": """
Before you can think better of it, you step into the water.

The mermaid's eyes widen. She dives, vanishing beneath the 
waves.

You wade deeper, hoping—

A hand grabs your ankle and pulls.

You go under with a yelp, salt water filling your mouth. 
For a terrifying moment, you're dragged deeper—

Then you're at the surface, gasping, and the mermaid is 
inches from your face, holding you up.

She says something in a language you don't understand. It 
sounds like a scolding.

Then she pushes you toward shore, not gently, and vanishes.

You stagger onto the beach, coughing, confused, and alive.

On your wrist, where she grabbed you, is a mark—a pattern 
of scales, fading even as you watch.

What does it mean? You have no idea.

But something tells you this isn't over.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "mermaid_marked", 
             "category": "status", "duration": 86400},
            {"type": "add_tag", "tag": "mermaid_touched", "category": "encounters"}
        ],
        "end": True
    },
    
    "run": {
        "text": """
You turn and scramble for the cove's exit. Behind you, you 
hear laughter—strange, watery, not entirely amused.

When you look back, she's gone.

You don't return to the cove for a week. When you do, 
there's nothing but waves and shells.

But sometimes, when you're on the beach at sunset, you 
catch a flash of scales in the deep water. Watching.

Maybe running wasn't the best choice.
""",
        "effects": [
            {"type": "add_tag", "tag": "mermaid_fled", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("tidepools_mermaid_01", MERMAID_SCENE)


# =============================================================================
# BUILDER HELPER FUNCTION
# =============================================================================

def setup_tidepools_room(room, area_type):
    """
    Set up a Tidepools room with resources and triggers.
    
    Args:
        room: The room object
        area_type: One of "beach", "pools", "shore", "cove"
    """
    from world.triggers import add_trigger
    from world.random_events import register_ambient_events
    
    # Ambient events
    register_ambient_events(room, [
        "wave_crash",
        "seagull_cry", 
        "distant_ship"
    ])
    
    if area_type == "beach":
        for key in ["beach_entry", "beach_waves", "beach_seagulls"]:
            trigger = TIDEPOOLS_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
    
    elif area_type == "pools":
        for key in ["pools_splash", "pools_scuttle"]:
            trigger = TIDEPOOLS_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Crab encounter
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "tidepools_crab_01"}],
            conditions=[{"type": "random", "chance": 0.04}]
        )
        
        # Grabby thing (rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "tidepools_grab_01"}],
            conditions=[
                {"type": "random", "chance": 0.02},
                {"type": "lacks_tag", "tag": "pool_ancient", "category": "encounters"}
            ]
        )
    
    elif area_type == "shore":
        for key in ["shore_spray", "shore_warning"]:
            trigger = TIDEPOOLS_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Tide scene (when lingering)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "tidepools_tide_01"}],
            conditions=[{"type": "random", "chance": 0.03}]
        )
    
    elif area_type == "cove":
        for key in ["cove_entry", "cove_treasure_feeling"]:
            trigger = TIDEPOOLS_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Treasure discovery (rare, once)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "tidepools_treasure_01"}],
            conditions=[
                {"type": "random", "chance": 0.1},
                {"type": "lacks_tag", "tag": "found_treasure_chest", "category": "encounters"}
            ]
        )
        
        # Mermaid sighting (very rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "tidepools_mermaid_01"}],
            conditions=[
                {"type": "random", "chance": 0.02},
                {"type": "lacks_tag", "tag": "mermaid_seen", "category": "encounters"},
                {"type": "lacks_tag", "tag": "mermaid_friend", "category": "encounters"},
                {"type": "time_in", "values": ["dawn", "dusk"]}
            ]
        )
