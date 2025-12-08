"""
Sunny Meadow Content
====================

Flower and herb gathering area southwest of the Grove.
Safe newbie area with LIGHT floral hazards - pollen effects.

Areas:
- Meadow Gate (tutorial, wildflowers)
- Flower Fields (color varieties, bees)
- Herb Garden (useful plants, gardener NPC)
- Sunny Hilltop (rare flowers, scenic view)

This area has slightly more "adult-adjacent" content due to
certain flowers having mild arousal effects. Still safe zone,
but with flavor.
"""

from world.scenes import register_scene
from world.triggers import add_trigger
from world.resources import create_resource_node

# =============================================================================
# RESOURCE DEFINITIONS
# =============================================================================

SUNNY_MEADOW_RESOURCES = {
    # MEADOW GATE
    "wildflower_patch": {
        "key": "wildflower patch",
        "type": "forage",
        "yields": [
            {"key": "daisy", "rarity": "common", "weight": 40},
            {"key": "buttercup", "rarity": "common", "weight": 30},
            {"key": "clover", "rarity": "common", "weight": 20},
            {"key": "violet", "rarity": "uncommon", "weight": 10},
        ],
        "max_harvests": 6,
        "respawn_time": 300,
        "desc": "A cheerful patch of wildflowers swaying in the breeze.",
    },
    
    "common_butterfly_meadow": {
        "key": "flower cluster",
        "type": "bugs",
        "yields": [
            {"key": "meadow butterfly", "rarity": "common", "weight": 50},
            {"key": "white cabbage butterfly", "rarity": "common", "weight": 30},
            {"key": "orange tip butterfly", "rarity": "uncommon", "weight": 15},
            {"key": "swallowtail", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 4,
        "respawn_time": 400,
        "desc": "Flowers buzzing with butterfly activity.",
    },
    
    # FLOWER FIELDS
    "rose_garden": {
        "key": "wild rose bush",
        "type": "forage",
        "yields": [
            {"key": "wild rose", "rarity": "common", "weight": 50},
            {"key": "pink rose", "rarity": "uncommon", "weight": 30},
            {"key": "red rose", "rarity": "uncommon", "weight": 15},
            {"key": "black rose", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 4,
        "respawn_time": 600,
        "seasons": ["spring", "summer"],
        "desc": "A sprawling rose bush with thorny stems and beautiful blooms.",
    },
    
    "sunflower_stand": {
        "key": "sunflower patch",
        "type": "forage",
        "yields": [
            {"key": "sunflower", "rarity": "common", "weight": 60},
            {"key": "giant sunflower", "rarity": "uncommon", "weight": 30},
            {"key": "golden sunflower", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 5,
        "respawn_time": 500,
        "seasons": ["summer", "autumn"],
        "desc": "Tall sunflowers turning their faces to follow the sun.",
    },
    
    "bee_hive": {
        "key": "wild beehive",
        "type": "forage",
        "yields": [
            {"key": "honeycomb", "rarity": "uncommon", "weight": 60},
            {"key": "royal jelly", "rarity": "rare", "weight": 30},
            {"key": "queen bee", "rarity": "epic", "weight": 10},
        ],
        "max_harvests": 1,
        "respawn_time": 7200,
        "desc": "A wild beehive humming with activity. Approach with caution.",
    },
    
    # HERB GARDEN
    "culinary_herbs": {
        "key": "herb patch",
        "type": "forage",
        "yields": [
            {"key": "basil", "rarity": "common", "weight": 30},
            {"key": "thyme", "rarity": "common", "weight": 25},
            {"key": "rosemary", "rarity": "common", "weight": 25},
            {"key": "sage", "rarity": "uncommon", "weight": 15},
            {"key": "saffron", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 450,
        "desc": "A well-tended patch of culinary herbs.",
    },
    
    "medicinal_herbs": {
        "key": "medicinal garden",
        "type": "forage",
        "yields": [
            {"key": "chamomile", "rarity": "common", "weight": 35},
            {"key": "echinacea", "rarity": "common", "weight": 30},
            {"key": "valerian", "rarity": "uncommon", "weight": 20},
            {"key": "feverfew", "rarity": "uncommon", "weight": 10},
            {"key": "moonwort", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 4,
        "respawn_time": 600,
        "desc": "Carefully cultivated medicinal plants.",
    },
    
    # SUNNY HILLTOP
    "rare_flower_spot": {
        "key": "hilltop blooms",
        "type": "forage",
        "yields": [
            {"key": "mountain lily", "rarity": "uncommon", "weight": 40},
            {"key": "sun orchid", "rarity": "rare", "weight": 35},
            {"key": "cloud flower", "rarity": "epic", "weight": 20},
            {"key": "celestial bloom", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 2,
        "respawn_time": 1800,
        "desc": "Rare flowers that only grow at the highest point of the meadow.",
    },
    
    "special_butterfly_spot": {
        "key": "hilltop currents",
        "type": "bugs",
        "yields": [
            {"key": "painted lady", "rarity": "uncommon", "weight": 40},
            {"key": "peacock butterfly", "rarity": "rare", "weight": 35},
            {"key": "apollo butterfly", "rarity": "epic", "weight": 20},
            {"key": "sunfire butterfly", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 2,
        "respawn_time": 1200,
        "desc": "Rare butterflies ride the warm updrafts here.",
    },
}


# =============================================================================
# HAZARDOUS FLORA (slightly spicier than Whisperwood)
# =============================================================================

SUNNY_MEADOW_HAZARDS = {
    "blush_rose": {
        "key": "blush rose",
        "type": "pollen_arousal",
        "chance": 0.15,
        "effect_key": "flushed",
        "duration": 600,
        "message": "The rose's intoxicating scent makes your face warm and your pulse quicken...",
        "room_message": "{name}'s cheeks flush red after smelling the blush rose.",
        "desc": "A deep crimson rose with an unusually sweet fragrance.",
    },
    
    "passion_poppy": {
        "key": "passion poppy",
        "type": "pollen_desire",
        "chance": 0.1,
        "effect_key": "distracted",
        "duration": 900,
        "message": "The poppy's pollen makes your thoughts wander to... distracting places...",
        "room_message": "{name} seems distracted after getting too close to the passion poppies.",
        "desc": "Vivid orange poppies that sway hypnotically in the breeze.",
    },
    
    "dream_lily": {
        "key": "dream lily",
        "type": "pollen_euphoria",
        "chance": 0.12,
        "effect_key": "dreamy",
        "duration": 1200,
        "message": "The lily's scent makes everything feel soft, warm, and pleasantly fuzzy...",
        "room_message": "{name} gets a dreamy look after inhaling the lily's fragrance.",
        "desc": "A pale lily that seems to glow from within.",
    },
    
    "honey_trap_flower": {
        "key": "honey trap flower",
        "type": "adhesive",
        "chance": 0.08,
        "effect_key": "sticky_hands",
        "duration": 300,
        "message": "Your fingers get covered in sweet, impossibly sticky nectar!",
        "room_message": "{name} gets their hands stuck to a honey trap flower.",
        "desc": "A beautiful flower dripping with golden nectar. It looks harmless.",
    },
}


# =============================================================================
# ROOM TRIGGERS
# =============================================================================

SUNNY_MEADOW_TRIGGERS = {
    # Meadow Gate
    "gate_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|gWelcome to Sunny Meadow!|n

Rolling hills of flowers stretch before you, alive with color 
and the hum of bees. Butterflies dance from bloom to bloom.

|wTip:|n Use |wforage|n to gather flowers and herbs!

|yNote:|n Some flowers here have... interesting effects. 
Nothing dangerous, but be aware of what you're sniffing.
"""}
        ],
    },
    
    "gate_breeze": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "A warm breeze carries the mingled scent of a hundred flowers."}
        ],
    },
    
    # Flower Fields
    "fields_bees": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "Bees buzz around you, investigating whether you're a flower. You're not. They move on."}
        ],
    },
    
    "fields_pollen": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.1}],
        "effects": [
            {"type": "message", "text": "A gust of wind sends a cloud of mixed pollen swirling around you. You sneeze."},
            {"type": "apply_effect", "effect_key": "sneezy", "category": "debuff", "duration": 120}
        ],
    },
    
    # Herb Garden
    "garden_fragrance": {
        "type": "enter",
        "effects": [
            {"type": "message", "text": "The herb garden smells wonderful—basil, rosemary, lavender, all mingling together."}
        ],
    },
    
    # Sunny Hilltop
    "hilltop_view": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
You reach the top of the hill and catch your breath.

The view is stunning—the entire Grove spreads out below you, 
with the meadow's colors painting the hills and the pond 
glittering in the distance. You can even see the Museum's 
spires catching the sunlight.

Rare flowers grow up here, found nowhere else in the meadow.
"""}
        ],
    },
    
    "hilltop_wind": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "The wind up here carries flower petals spinning past you like colorful snow."}
        ],
    },
}


# =============================================================================
# SCENES
# =============================================================================

# Bee encounter - can go well or poorly
BEE_ENCOUNTER_SCENE = {
    "id": "meadow_bees_01",
    "title": "Busy Bees",
    "tags": ["encounter", "bees", "meadow", "hazard"],
    
    "start": {
        "text": """
You're reaching for a particularly beautiful flower when you 
hear it: buzzing. A |ylot|n of buzzing.

You've accidentally disturbed a ground nest. Bees—big, fuzzy, 
slightly annoyed bees—are emerging from a hole in the earth, 
and they're looking at you.

They don't seem aggressive yet. Just... curious. And numerous.
""",
        "choices": [
            {"text": "Stay very still", "goto": "still"},
            {"text": "Back away slowly", "goto": "back_away"},
            {"text": "Run!", "goto": "run"},
            {"text": "Offer them a flower", "goto": "offer"},
        ]
    },
    
    "still": {
        "text": """
You freeze. The bees investigate you thoroughly—landing on your 
arms, your shoulders, your hair. Their little feet tickle.

After what feels like an eternity, they decide you're not a 
threat and return to their nest.

One bee stays behind a moment longer, looking at you with 
compound eyes, before flying off.

You let out a breath you didn't know you were holding.
""",
        "end": True
    },
    
    "back_away": {
        "text": """
You step back slowly, hands raised. The bees watch you go, 
buzzing among themselves in what might be a tiny bee committee 
meeting.

One of them follows you for several meters before returning to 
the nest. Making sure you're really leaving, probably.

You find flowers elsewhere. Far from the nest.
""",
        "end": True
    },
    
    "run": {
        "text": """
You bolt.

Bad idea.

The bees take this as a sign of hostility and give chase. You 
crash through the meadow, arms flailing, bees pursuing, until 
you finally outrun them.

You've collected a few stings for your trouble. Nothing serious, 
but definitely uncomfortable. And itchy.

Note to self: don't run from bees.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "bee_stings", 
             "category": "debuff", "duration": 1800}
        ],
        "end": True
    },
    
    "offer": {
        "text": """
Moving slowly, you pluck a nearby flower and hold it out toward 
the bees.

They go quiet. Still.

Then, one by one, they land on the flower, on your hand, your 
arm. Not stinging—just... sitting. Sampling the pollen. Buzzing 
contentedly.

When they've had their fill, they return to the nest. But one 
leaves something behind: a tiny drop of honey on your finger.

A gift. From the bees.

You're not sure what just happened, but you feel oddly honored.
""",
        "effects": [
            {"type": "give_item", "key": "wild honey drop", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "bee_friend", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("meadow_bees_01", BEE_ENCOUNTER_SCENE)


# Passion Poppy scene - slightly spicy but light
PASSION_POPPY_SCENE = {
    "id": "meadow_poppy_01",
    "title": "Field of Poppies",
    "tags": ["hazard", "pollen", "meadow", "mild_adult"],
    
    "start": {
        "text": """
You wander into a field of vivid orange poppies. They sway 
hypnotically in the breeze, releasing clouds of golden pollen 
that catch the sunlight.

It's beautiful. And the scent... sweet, warm, with something 
underneath you can't quite identify.

You feel your thoughts starting to drift. The sun is warm. 
The flowers are pretty. Everything is... nice.

Maybe you should lie down. Just for a minute.
""",
        "choices": [
            {"text": "Leave the poppy field immediately", "goto": "leave"},
            {"text": "Stay and enjoy the flowers", "goto": "stay"},
            {"text": "Lie down in the flowers", "goto": "lie_down"},
            {"text": "Pick some poppies (hold breath)", "goto": "pick"},
        ]
    },
    
    "leave": {
        "text": """
Your common sense wins out over the dreamy warmth. You back out 
of the poppy field, head clearing with each step.

From a safe distance, you can see other creatures in the field— 
bees moving sluggishly, a rabbit lying on its side in apparent 
bliss. The poppies don't discriminate.

Probably best you left when you did. Who knows how long you 
might have stayed?
""",
        "end": True
    },
    
    "stay": {
        "text": """
You sit among the poppies, breathing deeply. The scent fills 
your lungs, your thoughts, everything.

Time becomes... optional. The sun moves overhead but you barely 
notice. You're aware of warmth, color, the soft brush of petals 
against your skin. Your body feels heavy and light at the same 
time.

Eventually—minutes later? Hours?—the spell fades enough for 
you to stand. You're not sure exactly what you experienced, but 
you feel... good. Relaxed. Maybe a little too relaxed.

The poppies sway innocently, waiting for the next visitor.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "poppy_dazed", 
             "category": "debuff", "duration": 1200},
            {"type": "apply_effect", "effect_key": "deeply_relaxed", 
             "category": "buff", "duration": 3600}
        ],
        "end": True
    },
    
    "lie_down": {
        "text": """
You sink into the poppies like they're a bed made of sunshine.

The flowers close around you—not trapping, just... embracing. 
Their pollen drifts down like snow, coating your skin, filling 
your lungs with sweetness.

You dream. Of warmth, and softness, and things that make you 
blush when you finally wake up.

The sun has moved significantly by the time you come back to 
yourself. Hours have passed. You're covered in pollen, flushed, 
and deeply relaxed in ways you can't quite explain.

The poppies seem satisfied with your visit.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "poppy_dreams", 
             "category": "debuff", "duration": 3600},
            {"type": "apply_effect", "effect_key": "deeply_relaxed", 
             "category": "buff", "duration": 7200},
            {"type": "apply_effect", "effect_key": "pollen_covered", 
             "category": "status", "duration": 900}
        ],
        "end": True
    },
    
    "pick": {
        "text": """
You take a deep breath and hold it, diving into the poppy field 
to grab a few flowers before retreating.

It works! Mostly. You get the poppies with only a slight buzz 
from the brief exposure.

The flowers are beautiful—vivid orange petals, golden pollen. 
The Curator might be interested in these. Or you could keep 
them for... personal use. Whatever that means.

You shake off the lingering warmth and continue on your way.
""",
        "effects": [
            {"type": "give_item", "key": "passion poppy", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "apply_effect", "effect_key": "mild_buzz", 
             "category": "debuff", "duration": 300}
        ],
        "end": True
    }
}

register_scene("meadow_poppy_01", PASSION_POPPY_SCENE)


# Rare flower guardian - hilltop encounter
FLOWER_GUARDIAN_SCENE = {
    "id": "meadow_guardian_01",
    "title": "The Flower Guardian",
    "tags": ["encounter", "guardian", "meadow", "rare"],
    
    "start": {
        "text": """
You reach for a particularly beautiful flower—a celestial bloom, 
petals shimmering with impossible colors—when something moves.

Rising from the flowers is a figure made of petals and light. 
Vaguely humanoid. Entirely beautiful. Looking at you with eyes 
like morning dew.

"That one," it says, voice like wind through grass, "is mine."
""",
        "choices": [
            {"text": "\"I'm sorry, I didn't know.\"", "goto": "apologize"},
            {"text": "\"Who are you?\"", "goto": "ask"},
            {"text": "Grab the flower anyway", "goto": "grab"},
            {"text": "\"Could I trade for it?\"", "goto": "trade"},
        ]
    },
    
    "apologize": {
        "text": """
"I'm sorry. I didn't realize these flowers belonged to someone."

The guardian tilts its head, petals rustling.

"Polite. Rare." It considers you. "Most just take. You asked, 
even in apology. That is... unusual."

It waves a hand made of braided stems, and a single flower 
detaches from the field—beautiful, though not the celestial 
bloom you'd reached for.

"A lesser gift. For lesser rudeness. Take it and remember: 
the hilltop's rarest blooms are not for casual picking."

The guardian dissolves back into the flowers, leaving you with 
your gift and a warning.
""",
        "effects": [
            {"type": "give_item", "key": "sun orchid", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "met_guardian", "category": "encounters"}
        ],
        "end": True
    },
    
    "ask": {
        "text": """
"Who are you?"

The guardian spreads arms made of vines and petals.

"I am the meadow's memory. The hilltop's keeper. I was here 
when the first seed sprouted. I will be here when the last 
petal falls."

It looks at you with those dewdrop eyes.

"I am what grows when a place is loved. And I protect what 
is beautiful. These flowers—" it gestures at the celestial 
blooms "—are my children. Would you take them from me?"
""",
        "choices": [
            {"text": "\"No. I understand now.\"", "goto": "understand"},
            {"text": "\"How can I earn one?\"", "goto": "earn"},
        ]
    },
    
    "grab": {
        "text": """
You snatch for the flower—

And find your hand closing on nothing. The flower has moved. 
Or you have. Space is strange here, suddenly.

The guardian doesn't look angry. Just... disappointed.

"Greedy. Like so many."

Vines wrap around your ankles, gentle but firm.

"You will wait here until you understand that beauty cannot be 
taken by force. Only given freely."

The vines don't hurt. But you can't move, either. The guardian 
watches you, patient as a plant, as the sun moves overhead.

When it finally releases you—an hour later? two?—you've had 
plenty of time to think about what you did wrong.

You leave with nothing but a lesson.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "guardian_lesson", 
             "category": "debuff", "duration": 3600},
            {"type": "add_tag", "tag": "guardian_punished", "category": "encounters"}
        ],
        "end": True
    },
    
    "trade": {
        "text": """
"Could I trade for it?"

The guardian pauses. Petals rustle with what might be surprise.

"Trade. An interesting concept. What would you offer for 
something unique? Something that exists nowhere else?"

It leans closer.

"What do you have that is equally precious?"
""",
        "choices": [
            {"text": "\"I have gold...\"", "goto": "offer_gold"},
            {"text": "\"What do you want?\"", "goto": "ask_want"},
            {"text": "\"Nothing, I suppose.\"", "goto": "admit_nothing"},
        ]
    },
    
    "understand": {
        "text": """
"No. I understand now. They're not mine to take."

The guardian smiles—at least, its face rearranges in a way 
that suggests a smile.

"Wisdom. Rarer than the flowers."

It plucks a single petal from its own form and presses it 
into your palm. It feels like sunlight given shape.

"Keep this. It marks you as one who learned. Come back when 
you have truly earned a bloom—through patience, through care, 
through giving rather than taking."

It dissolves back into the flowers, leaving you with a petal 
and a strange sense of honor.
""",
        "effects": [
            {"type": "give_item", "key": "guardian petal", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "guardian_favor", "category": "encounters"}
        ],
        "end": True
    },
    
    "earn": {
        "text": """
"How can I earn one? What would make me worthy?"

The guardian considers this seriously.

"Tend the meadow. Protect what grows. Bring water in drought. 
Clear weeds that choke. Give rather than take, again and again, 
until the flowers know your scent."

It gestures at the hilltop.

"When the meadow loves you—truly loves you—the flowers will 
come to you. You won't need to pick them. They will choose 
to be picked."

It begins to dissolve.

"That is how you earn a celestial bloom. Through being worthy."

You're left alone with a lot to think about.
""",
        "effects": [
            {"type": "add_tag", "tag": "guardian_quest", "category": "encounters"}
        ],
        "end": True
    },
    
    "offer_gold": {
        "text": """
"I have gold—"

The guardian laughs—a sound like chimes and rustling leaves.

"Gold. Cold metal dug from the earth's wounds. What use has 
a flower for gold?"

It shakes its head, petals falling like gentle rain.

"You offer the wrong currency, child. But the attempt is 
noted. Come back when you understand what flowers value."

It sinks back into the blooms, leaving you feeling slightly 
foolish but oddly determined.
""",
        "effects": [
            {"type": "add_tag", "tag": "met_guardian", "category": "encounters"}
        ],
        "end": True
    },
    
    "ask_want": {
        "text": """
"What do you want?"

The guardian thinks. Petals drift around it like thoughts 
taking physical form.

"Stories. Songs. A single honest tear. The first laugh of 
morning. Things that cannot be bought, only given."

It looks at you.

"What do you have that money cannot purchase?"
""",
        "choices": [
            {"text": "Sing a song", "goto": "sing"},
            {"text": "Tell a story", "goto": "tell_story"},
            {"text": "\"I don't have anything like that.\"", "goto": "admit_nothing"},
        ]
    },
    
    "admit_nothing": {
        "text": """
"I don't have anything that precious. Not really."

The guardian nods, something like respect in its dewdrop eyes.

"Honesty. Also rare. Most would lie, claim to have what they 
lack."

It plucks a common flower—beautiful, but not celestial—and 
offers it to you.

"Take this. Not what you wanted, but given freely. When you 
have something worthy to trade, return. I will remember your 
honesty."

It fades into the flowers, leaving you with a simple gift and 
a standing invitation.
""",
        "effects": [
            {"type": "give_item", "key": "sun orchid", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "guardian_respect", "category": "encounters"}
        ],
        "end": True
    },
    
    "sing": {
        "text": """
You sing. Not well, maybe, but honestly—some song from your 
childhood, or something you made up on the spot. It doesn't 
matter. What matters is that you mean it.

The guardian listens, still as a plant. The whole hilltop 
seems to hold its breath.

When you finish, the guardian smiles.

"Payment accepted."

It hands you the celestial bloom—warm, alive, shimmering with 
colors that shouldn't exist. 

"Songs feed the flowers. Remember that. Sing to them, and they 
will love you."

The guardian dissolves into petals, leaving you with something 
precious and the echo of your own voice.
""",
        "effects": [
            {"type": "give_item", "key": "celestial bloom", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "guardian_blessed", "category": "encounters"}
        ],
        "end": True
    },
    
    "tell_story": {
        "text": """
You tell a story. It's not a good one—just something from your 
life, something true. An embarrassing moment, maybe. Or something 
beautiful you witnessed. It doesn't matter. What matters is that 
it's real.

The guardian listens without moving, petals occasionally 
rustling with what might be emotion.

When you finish, it nods slowly.

"A good story. True. I can taste the truth in it."

It offers you the celestial bloom.

"Stories feed the soul of places. This meadow will remember 
yours. And now you have earned what you came for."

You take the flower, warm and impossible in your hands.
""",
        "effects": [
            {"type": "give_item", "key": "celestial bloom", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "guardian_blessed", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("meadow_guardian_01", FLOWER_GUARDIAN_SCENE)


# =============================================================================
# BUILDER HELPER FUNCTION
# =============================================================================

def setup_meadow_room(room, area_type):
    """
    Set up a Sunny Meadow room with resources and triggers.
    
    Args:
        room: The room object
        area_type: One of "gate", "fields", "garden", "hilltop"
    """
    from world.triggers import add_trigger
    from world.random_events import register_ambient_events
    
    # Ambient events for all meadow rooms
    register_ambient_events(room, [
        "rustling_leaves",
        "bird_song",
        "bee_buzz",
    ])
    
    if area_type == "gate":
        for key in ["gate_entry", "gate_breeze"]:
            trigger = SUNNY_MEADOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
    
    elif area_type == "fields":
        for key in ["fields_bees", "fields_pollen"]:
            trigger = SUNNY_MEADOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Bee encounter
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "meadow_bees_01"}],
            conditions=[{"type": "random", "chance": 0.04}]
        )
        
        # Passion poppy field (rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "meadow_poppy_01"}],
            conditions=[{"type": "random", "chance": 0.03}]
        )
    
    elif area_type == "garden":
        trigger = SUNNY_MEADOW_TRIGGERS["garden_fragrance"]
        add_trigger(room, trigger["type"],
                   trigger["effects"],
                   trigger.get("conditions"))
    
    elif area_type == "hilltop":
        for key in ["hilltop_view", "hilltop_wind"]:
            trigger = SUNNY_MEADOW_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Guardian encounter (first visit to rare flowers)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "meadow_guardian_01"}],
            conditions=[
                {"type": "random", "chance": 0.1},
                {"type": "lacks_tag", "tag": "met_guardian", "category": "encounters"},
                {"type": "lacks_tag", "tag": "guardian_punished", "category": "encounters"},
                {"type": "lacks_tag", "tag": "guardian_blessed", "category": "encounters"}
            ]
        )
