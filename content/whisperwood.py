"""
Whisperwood Content
===================

Forest area west of the Grove. Bug catching, foraging, mushrooms.
Safe newbie area with LIGHT hazards - nothing extreme, but flavor.

Areas:
- Forest Edge (tutorial, common resources)
- Shady Paths (more bugs, mushrooms, berry bushes)
- Mossy Clearing (rare night bugs, herb patches)
- Ancient Stump (special spawns, seasonal events)
"""

from world.scenes import register_scene
from world.triggers import add_trigger
from world.resources import create_resource_node
from world.traps import create_hazardous_plant
from world.effects import apply_effect

# =============================================================================
# RESOURCE DEFINITIONS
# =============================================================================

WHISPERWOOD_RESOURCES = {
    # FOREST EDGE
    "common_butterfly_spot": {
        "key": "flowering bush",
        "type": "bugs",
        "yields": [
            {"key": "common butterfly", "rarity": "common", "weight": 70},
            {"key": "cabbage moth", "rarity": "common", "weight": 25},
            {"key": "painted lady", "rarity": "uncommon", "weight": 5},
        ],
        "max_harvests": 3,
        "respawn_time": 300,
        "desc": "A bush covered in small flowers, attracting butterflies.",
    },
    
    "berry_bush": {
        "key": "wild berry bush",
        "type": "forage",
        "yields": [
            {"key": "wild berries", "rarity": "common", "weight": 80},
            {"key": "sweet berries", "rarity": "uncommon", "weight": 15},
            {"key": "golden berry", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 600,
        "seasons": ["summer", "autumn"],
        "desc": "A bush heavy with ripe berries.",
    },
    
    # SHADY PATHS
    "beetle_log": {
        "key": "rotting log",
        "type": "bugs",
        "yields": [
            {"key": "grove beetle", "rarity": "common", "weight": 60},
            {"key": "stag beetle", "rarity": "uncommon", "weight": 25},
            {"key": "rhinoceros beetle", "rarity": "rare", "weight": 10},
            {"key": "golden scarab", "rarity": "epic", "weight": 5},
        ],
        "max_harvests": 4,
        "respawn_time": 900,
        "desc": "A mossy fallen log, home to various beetles.",
    },
    
    "mushroom_patch": {
        "key": "mushroom cluster",
        "type": "forage",
        "yields": [
            {"key": "common mushroom", "rarity": "common", "weight": 50},
            {"key": "button mushroom", "rarity": "common", "weight": 30},
            {"key": "chanterelle", "rarity": "uncommon", "weight": 12},
            {"key": "morel", "rarity": "rare", "weight": 6},
            {"key": "truffle", "rarity": "epic", "weight": 2},
        ],
        "max_harvests": 6,
        "respawn_time": 1200,
        "seasons": ["autumn", "spring"],
        "desc": "A cluster of various mushrooms growing in the shade.",
    },
    
    # MOSSY CLEARING
    "night_moth_spot": {
        "key": "moonlit flowers",
        "type": "bugs",
        "yields": [
            {"key": "whisperwood moth", "rarity": "uncommon", "weight": 50},
            {"key": "luna moth", "rarity": "rare", "weight": 30},
            {"key": "death's head moth", "rarity": "epic", "weight": 15},
            {"key": "ethereal moth", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 2,
        "respawn_time": 1800,
        "time_available": ["night", "midnight"],
        "desc": "Pale flowers that bloom only at night, attracting rare moths.",
    },
    
    "herb_patch": {
        "key": "herb garden",
        "type": "forage",
        "yields": [
            {"key": "chamomile", "rarity": "common", "weight": 40},
            {"key": "lavender", "rarity": "common", "weight": 30},
            {"key": "feverfew", "rarity": "uncommon", "weight": 20},
            {"key": "moonpetal", "rarity": "rare", "weight": 8},
            {"key": "dreamwort", "rarity": "epic", "weight": 2},
        ],
        "max_harvests": 4,
        "respawn_time": 900,
        "desc": "A patch of wild medicinal herbs.",
    },
    
    # ANCIENT STUMP
    "amber_sap_node": {
        "key": "ancient tree wound",
        "type": "forage",
        "yields": [
            {"key": "amber sap", "rarity": "rare", "weight": 70},
            {"key": "crystallized amber", "rarity": "epic", "weight": 25},
            {"key": "ancient amber", "rarity": "legendary", "weight": 5},
        ],
        "max_harvests": 1,
        "respawn_time": 7200,  # 2 hours
        "desc": "Golden sap oozes slowly from a wound in the ancient stump.",
    },
    
    "rare_beetle_spot": {
        "key": "sacred hollow",
        "type": "bugs",
        "yields": [
            {"key": "jewel beetle", "rarity": "rare", "weight": 50},
            {"key": "forest guardian beetle", "rarity": "epic", "weight": 35},
            {"key": "ancient scarab", "rarity": "legendary", "weight": 15},
        ],
        "max_harvests": 1,
        "respawn_time": 3600,
        "desc": "A hollow in the stump where rare beetles gather.",
    },
}


# =============================================================================
# HAZARDOUS FLORA
# =============================================================================

WHISPERWOOD_HAZARDS = {
    "drowsy_bloom": {
        "key": "drowsy bloom",
        "type": "pollen_sleep",
        "chance": 0.2,
        "effect_key": "drowsy",
        "duration": 300,
        "message": "The flower releases a puff of glittering pollen. You feel suddenly sleepy...",
        "room_message": "{name} disturbs a drowsy bloom and yawns hugely.",
        "desc": "A soft purple flower that seems to sway even without wind.",
    },
    
    "giggle_blossom": {
        "key": "giggle blossom",
        "type": "pollen_euphoria",
        "chance": 0.15,
        "effect_key": "giggly",
        "duration": 600,
        "message": "Pink pollen swirls around you. Everything seems funnier suddenly...",
        "room_message": "{name} gets a face full of giggle pollen and starts laughing.",
        "desc": "A bright pink flower that seems to be laughing at you.",
    },
    
    "sticky_pitcher": {
        "key": "sticky pitcher plant",
        "type": "sap_adhesive",
        "chance": 0.1,
        "effect_key": "sticky",
        "duration": 180,
        "message": "Your hand gets stuck in the plant's sticky residue!",
        "room_message": "{name} gets their hand stuck in a pitcher plant.",
        "desc": "A large pitcher-shaped plant with glistening inner walls.",
    },
    
    # Slightly spicier but still mild
    "blush_bloom": {
        "key": "blush bloom",
        "type": "pollen_mild_arousal",
        "chance": 0.1,
        "effect_key": "flushed",
        "duration": 300,
        "message": "The flower's sweet scent makes your cheeks warm and your heart race...",
        "room_message": "{name}'s face turns red after sniffing a blush bloom.",
        "desc": "A deep red flower with an intoxicating fragrance.",
    },
}


# =============================================================================
# ROOM TRIGGERS
# =============================================================================

WHISPERWOOD_TRIGGERS = {
    # Forest Edge - welcoming, tutorial-ish
    "forest_edge_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|gWelcome to Whisperwood!|n

The forest stretches before you, dappled sunlight filtering through 
the canopy. You can see butterflies flitting between the flowers, 
and hear the rustle of small creatures in the underbrush.

|wTip:|n Try |wforage|n to gather plants, or |wcatch|n to catch bugs!
"""}
        ],
    },
    
    "forest_edge_ambient": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "A butterfly lands briefly on your shoulder before fluttering away."}
        ],
    },
    
    # Shady Paths - slightly darker, mysterious
    "shady_paths_whispers": {
        "type": "enter",
        "conditions": [
            {"type": "time_in", "values": ["dusk", "night", "midnight"]},
            {"type": "random", "chance": 0.2}
        ],
        "effects": [
            {"type": "message", "text": "|xYou could swear you hear whispering among the trees...|n"}
        ],
    },
    
    "shady_paths_mushroom_glow": {
        "type": "enter",
        "conditions": [
            {"type": "time_in", "values": ["night", "midnight"]},
            {"type": "random", "chance": 0.4}
        ],
        "effects": [
            {"type": "message", "text": "Bioluminescent mushrooms pulse with soft blue light, guiding your path."}
        ],
    },
    
    # Mossy Clearing - magical at night
    "clearing_fireflies": {
        "type": "enter",
        "conditions": [
            {"type": "time_in", "values": ["night", "midnight"]},
        ],
        "effects": [
            {"type": "message", "text": "Fireflies dance through the clearing, their lights creating patterns in the darkness."}
        ],
    },
    
    "clearing_fairy_ring": {
        "type": "enter",
        "conditions": [
            {"type": "random", "chance": 0.05},
            {"type": "time_is", "value": "midnight"}
        ],
        "effects": [
            {"type": "message", "text": "|mA ring of mushrooms glows softly. You feel watched by something ancient and amused.|n"},
            {"type": "apply_effect", "effect_key": "fae_noticed", "category": "status", "duration": 3600}
        ],
    },
    
    # Ancient Stump - special location
    "stump_presence": {
        "type": "enter",
        "effects": [
            {"type": "message", "text": "The ancient stump radiates a sense of deep, patient awareness. This tree was old when the world was young."}
        ],
    },
    
    "stump_blessing": {
        "type": "enter",
        "conditions": [
            {"type": "random", "chance": 0.02},
            {"type": "lacks_effect", "effect": "forest_blessed"}
        ],
        "effects": [
            {"type": "message", "text": "|gThe stump pulses with warm light. You feel the forest's approval.|n"},
            {"type": "apply_effect", "effect_key": "forest_blessed", "category": "buff", "duration": 7200}
        ],
    },
}


# =============================================================================
# SCENES - Forest Encounters
# =============================================================================

# Light, playful encounter - appropriate for safe zone
CURIOUS_SLIME_SCENE = {
    "id": "whisperwood_slime_01",
    "title": "Curious Forest Slime",
    "tags": ["encounter", "slime", "whisperwood", "safe", "cute"],
    
    "start": {
        "text": """
A small blob of translucent green goo drops from a branch above, 
landing on your head with a wet |wsplat|n.

Before you can panic, it oozes down to your shoulder and forms 
what might be a face—two darker spots for eyes, a curved line 
for a mouth. It's... smiling at you?

The little slime makes a questioning burble, like it's asking 
permission to stay.
""",
        "choices": [
            {"text": "Gently set it down", "goto": "set_down"},
            {"text": "Let it stay on your shoulder", "goto": "keep"},
            {"text": "Shake it off frantically", "goto": "shake"},
            {"text": "Offer it a berry", "goto": "berry",
             "condition": {"type": "has_item", "item": "wild berries"}},
        ]
    },
    
    "set_down": {
        "text": """
You carefully cup the slime in your hands and set it on a nearby 
mushroom. It makes a disappointed burble but doesn't protest, 
reforming into a little puddle.

As you walk away, you could swear it waves a tiny pseudopod at 
you.

Cute little thing, really.
""",
        "end": True
    },
    
    "keep": {
        "text": """
The slime wiggles happily, settling into a comfortable blob on 
your shoulder. It's pleasantly cool and barely weighs anything.

Over the next few minutes, it occasionally burbles at things 
you pass—flowers, beetles, other mushrooms. It seems fascinated 
by everything.

Eventually it gets distracted by a particularly shiny leaf and 
oozes off to investigate, leaving a faint trail of sparkly 
residue on your clothes.

You find yourself oddly charmed by the encounter.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "slime_sparkle", 
             "category": "buff", "duration": 1800}
        ],
        "end": True
    },
    
    "shake": {
        "text": """
You flail wildly, shaking your head and shoulders. The slime 
makes a startled squeak and goes flying, landing in a bush with 
a wet squelch.

It reforms slowly, its little face-impression looking hurt and 
confused. Then it turns away and oozes deeper into the forest, 
leaving a sad trail of goo behind it.

You feel kind of bad, actually. It wasn't hurting anything.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "mild_guilt", 
             "category": "status", "duration": 300}
        ],
        "end": True
    },
    
    "berry": {
        "text": """
You pull out a berry and offer it to the slime. Its little eyes 
go wide—well, the spots get bigger—and it lunges for the treat, 
engulfing the berry entirely.

You can see the berry dissolving inside its translucent body. 
The slime turns a faint purple color and vibrates with apparent 
joy.

Then it does something unexpected: it produces a small, perfectly 
round pearl from somewhere inside itself and drops it into your 
palm. A gift, apparently.

The slime burbles happily and oozes away, leaving you with a 
mysterious pearl and a story to tell.
""",
        "effects": [
            {"type": "take_item", "key": "wild berries"},
            {"type": "give_item", "key": "slime pearl", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "slime_friend", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("whisperwood_slime_01", CURIOUS_SLIME_SCENE)


# Bug catching mishap - mild consequences
BUG_CATCHING_MISHAP = {
    "id": "whisperwood_bugmishap_01",
    "title": "Bug Catching Gone Wrong",
    "tags": ["hazard", "bugs", "whisperwood", "safe", "comedy"],
    
    "start": {
        "text": """
You spot a beautiful beetle on a low branch—iridescent wings 
catching the light. You creep closer, net ready...

And step directly into a hidden hornets' nest.

The air fills with angry buzzing. Dozens of furious insects 
pour out of the ground, and they are |ynot happy|n.
""",
        "choices": [
            {"text": "RUN!", "goto": "run"},
            {"text": "Freeze and hope they lose interest", "goto": "freeze"},
            {"text": "Dive into the nearby stream", "goto": "stream"},
        ]
    },
    
    "run": {
        "text": """
You bolt through the underbrush, hornets in hot pursuit. Branches 
whip at your face, roots grab at your feet, but pure adrenaline 
keeps you moving.

By the time you finally stop, gasping for breath, you've collected 
a few stings and absolutely no beetles. Your pride hurts worse 
than the welts.

At least you got some exercise?
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "stung", 
             "category": "debuff", "duration": 600},
            {"type": "message_room", "text": "{name} comes crashing through the bushes, flailing wildly."}
        ],
        "end": True
    },
    
    "freeze": {
        "text": """
You go absolutely still, barely breathing. The hornets swarm 
around you, investigating this strange statue that disturbed 
their home.

For an agonizing minute, they crawl over your arms, your face, 
your neck. Every instinct screams at you to move.

But you don't. And eventually, deciding you're not a threat 
(or not worth the effort), they return to their nest.

You wait another five minutes before risking a single twitch. 
Your nerves are shot, but you're unharmed.

That beetle is long gone, though.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "shaky", 
             "category": "debuff", "duration": 300}
        ],
        "end": True
    },
    
    "stream": {
        "text": """
You spot the stream and don't hesitate—throwing yourself into 
the water with a tremendous splash. The cold hits you like a 
slap, but the hornets break off their pursuit, unwilling to 
follow you into the current.

You surface, sputtering, as the swarm buzzes angrily on the 
bank before eventually dispersing.

You're soaked, cold, and have definitely lost whatever dignity 
you came in with. But at least you're not covered in stings.

Your net is... somewhere upstream. Probably.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "soaked", 
             "category": "debuff", "duration": 900}
        ],
        "end": True
    }
}

register_scene("whisperwood_bugmishap_01", BUG_CATCHING_MISHAP)


# Night encounter - slightly more mysterious
WHISPERWOOD_NIGHT_VISITOR = {
    "id": "whisperwood_night_01",
    "title": "Night Visitor",
    "tags": ["encounter", "night", "whisperwood", "fae", "mysterious"],
    
    "start": {
        "text": """
You're collecting moths by moonlight when you notice you're not 
alone.

A figure sits on a fallen log nearby, watching you with luminous 
eyes. They're small—child-sized—but clearly not a child. Pointed 
ears. Skin like bark. A smile that shows too many teeth.

"Catching pretties, are you?" The voice sounds like wind through 
leaves. "I like pretties too."

They hold up a hand, and three ethereal moths you've never seen 
before spiral around their fingers.

"Want to trade?"
""",
        "choices": [
            {"text": "What kind of trade?", "goto": "ask_trade"},
            {"text": "No thank you", "goto": "refuse_polite"},
            {"text": "Get away from me!", "goto": "refuse_rude"},
            {"text": "What are those moths?", "goto": "ask_moths"},
        ]
    },
    
    "ask_trade": {
        "text": """
The creature's smile widens. "Simple trade. You give me something 
interesting, I give you a pretty." They gesture at the moths. 
"These don't exist in your world. Museum lady would |ylove|n them."

They tilt their head, studying you.

"What do you have that's... interesting?"
""",
        "choices": [
            {"text": "I have gold...", "goto": "offer_gold",
             "condition": {"type": "currency_gte", "amount": 50}},
            {"text": "How about a story?", "goto": "offer_story"},
            {"text": "What about my berries?", "goto": "offer_berry",
             "condition": {"type": "has_item", "item": "wild berries"}},
            {"text": "I don't think I have anything you want", "goto": "decline"},
        ]
    },
    
    "offer_gold": {
        "text": """
The creature makes a face like they've smelled something bad.

"Cold metal. Dead weight. No." They wave dismissively. "I don't 
want what everyone wants. I want something |yinteresting|n."

They tap their chin thoughtfully.

"Tell me a secret instead. Something true that you've never told 
anyone. Then we trade."
""",
        "choices": [
            {"text": "Whisper a secret", "goto": "secret"},
            {"text": "I'd rather not", "goto": "decline"},
        ]
    },
    
    "offer_story": {
        "text": """
The creature's eyes light up—literally, glowing brighter.

"A STORY! Yes, yes. Tell me a story. Make it good. Make it |ytrue|n. 
The best stories are true."

They settle more comfortably on the log, those too-many teeth 
showing in an eager grin.

"Tell me how you came to be here. In the Grove. What path led 
you to catch moths in my forest at midnight?"
""",
        "choices": [
            {"text": "Tell them about your journey", "goto": "tell_story"},
            {"text": "Make something up", "goto": "lie"},
        ]
    },
    
    "tell_story": {
        "text": """
You tell them. About finding the Grove, about the gates, about 
learning to catch bugs and gather herbs. About what brought you 
here in the first place.

The creature listens with rapt attention, occasionally making 
small sounds of interest or surprise. When you finish, they nod 
slowly.

"A good story. True. I can taste the truth in it."

They release one of the moths, and it flutters to you, landing 
on your palm. It's lighter than air.

"Care for it. It doesn't belong here, but it chose to stay. Like 
you, maybe."

When you look up, the creature is gone. Only the moths remain.
""",
        "effects": [
            {"type": "give_item", "key": "fae moth", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "fae_traded", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "fae_touched", 
             "category": "status", "duration": 86400}
        ],
        "end": True
    },
    
    "lie": {
        "text": """
You spin a tale—dramatic, exciting, completely fabricated.

The creature's expression doesn't change, but their eyes stop 
glowing. The forest around you goes very, very quiet.

"Lies," they say softly. "Lies have a taste too. Sour. Rotten."

They stand, moths swirling around them.

"We don't trade with liars. But we remember them."

The shadows seem to reach for you as the creature melts into 
the darkness. You're alone again, but the forest feels... hostile 
now. Watching.

Time to leave.
""",
        "effects": [
            {"type": "add_tag", "tag": "lied_to_fae", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "fae_displeasure", 
             "category": "debuff", "duration": 7200}
        ],
        "end": True
    },
    
    "secret": {
        "text": """
You lean close and whisper something true. Something you've 
never said aloud.

The creature inhales, as if breathing in your words. Their 
eyes close in apparent pleasure.

"Yesss. That's |ydelicious|n. A real secret. Buried deep."

They open their eyes and smile—gentler now, almost kind.

"You're honest. I like honest ones. Here."

All three moths flutter to you, settling on your clothes like 
living jewelry.

"Three secrets for one. More than fair. The museum lady will 
be impressed."

They're gone between one blink and the next.
""",
        "effects": [
            {"type": "give_item", "key": "fae moth", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "fae moth", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "fae moth", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "fae_favor", "category": "encounters"},
        ],
        "end": True
    },
    
    "offer_berry": {
        "text": """
You hold up your berries. The creature laughs—a sound like 
rustling leaves.

"Forest fruit in the forest? You offer me what's already mine!"

But they pluck a single berry from your hand anyway, popping 
it into their mouth.

"Still. The gesture pleases me."

They release the smallest moth, which flutters to you.

"A small gift for a small kindness. Come back when you have 
something more... interesting."

They melt into the shadows, still chewing.
""",
        "effects": [
            {"type": "take_item", "key": "wild berries"},
            {"type": "give_item", "key": "lesser fae moth", 
             "typeclass": "typeclasses.objects.Object"},
        ],
        "end": True
    },
    
    "refuse_polite": {
        "text": """
"No thank you," you say carefully. "I'm happy with what I can 
catch myself."

The creature studies you for a long moment, then nods.

"Polite. Careful. Boring, but polite." They shrug. "The offer 
stays open. Find me again if you change your mind."

They slip off the log and walk into a tree—not around it, 
|yinto|n it—and are gone.

You have a feeling this wasn't the last you'll see of them.
""",
        "effects": [
            {"type": "add_tag", "tag": "met_fae", "category": "encounters"}
        ],
        "end": True
    },
    
    "refuse_rude": {
        "text": """
"Get away from me!"

The forest goes silent. Dead silent. The creature's smile 
doesn't waver, but their eyes go cold.

"Rude little mortal. In MY forest. Catching MY pretties."

They stand, and suddenly seem much larger than before.

"I wasn't going to hurt you. But rudeness has consequences."

They snap their fingers, and you feel something shift inside 
you. A compulsion. An itch you can't scratch.

"Every full moon, you'll come to this clearing. You won't be 
able to help yourself. And I'll be waiting to see if you've 
learned manners."

They're gone. The compulsion settles into your bones like 
a promise.

Oh no.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "fae_compulsion", 
             "category": "curse", "duration": 0},
            {"type": "add_tag", "tag": "fae_cursed", "category": "encounters"},
            {"type": "message", "text": "|rYou've been cursed by the fae. You should find someone who can remove it...|n"}
        ],
        "end": True
    },
    
    "decline": {
        "text": """
"I don't think we have a deal to make."

The creature sighs dramatically. "Mortals. Always so cautious. 
So |yboring|n."

They hop off the log and stretch.

"Fine, fine. Keep catching your common pretties. I'll find 
someone more interesting."

They wander off into the darkness, moths trailing behind them 
like a glowing train.

Part of you wonders if you missed an opportunity. Part of you 
is relieved.
""",
        "effects": [
            {"type": "add_tag", "tag": "met_fae", "category": "encounters"}
        ],
        "end": True
    },
    
    "ask_moths": {
        "text": """
"Spiritmoths," the creature says, holding one up for you to see. 
It's made of moonlight and memory, barely there. "They exist 
between heartbeats. Between thoughts. Very rare. Very pretty."

They let it spiral back to join the others.

"The museum lady collects things. I've seen her. She wants 
these—I can tell. But she can't catch them. Only we can."

That smile again.

"But we can trade them. For the right price."
""",
        "goto": "ask_trade"
    },
}

register_scene("whisperwood_night_01", WHISPERWOOD_NIGHT_VISITOR)


# Mushroom-related scene
STRANGE_MUSHROOM_SCENE = {
    "id": "whisperwood_mushroom_01",
    "title": "Strange Mushroom",
    "tags": ["hazard", "mushroom", "whisperwood", "mild"],
    
    "start": {
        "text": """
You find a mushroom you don't recognize—tall, pale, with 
bioluminescent spots that pulse slowly. It's beautiful.

It's also not in any foraging guide you've seen.

A voice in your head (common sense) suggests leaving it alone. 
Another voice (curiosity) really wants to know what it does.
""",
        "choices": [
            {"text": "Leave it alone", "goto": "leave"},
            {"text": "Pick it carefully", "goto": "pick"},
            {"text": "Smell it first", "goto": "smell"},
            {"text": "Poke it with a stick", "goto": "poke"},
        ]
    },
    
    "leave": {
        "text": """
You step back from the strange fungus. Some things are better 
left alone, especially when they glow.

The mushroom pulses once, almost disappointedly, and you 
continue on your way.

Good call, probably.
""",
        "end": True
    },
    
    "pick": {
        "text": """
You reach for the mushroom—

The moment your fingers touch it, it releases a burst of 
spores directly into your face. The taste is indescribable: 
sweet, earthy, and something else. Something that makes your 
thoughts go fuzzy around the edges.

Colors seem brighter. The trees are breathing. Is that music?

You should probably sit down for a minute.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "mushroom_trip", 
             "category": "debuff", "duration": 1800},
            {"type": "give_item", "key": "strange mushroom", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "smell": {
        "text": """
You lean down to sniff carefully—

The mushroom seems to lean toward you, and before you can 
react, releases a gentle puff of spores.

The effect is... mild. Pleasant, even. The forest seems 
friendlier. Your feet feel like they could walk forever. 
Everything is going to be fine.

You feel great, actually. Probably nothing to worry about.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "mushroom_mild", 
             "category": "buff", "duration": 1200}
        ],
        "end": True
    },
    
    "poke": {
        "text": """
You find a stick and give the mushroom a cautious prod.

It wobbles. The glowing spots pulse faster.

You poke it again.

The mushroom |ycollapses|n, deflating into a sad little 
puddle of goo. Apparently it was more fragile than it looked.

Well. That's one mystery that will remain unsolved.
""",
        "end": True
    }
}

register_scene("whisperwood_mushroom_01", STRANGE_MUSHROOM_SCENE)


# =============================================================================
# BUILDER HELPER FUNCTION
# =============================================================================

def setup_whisperwood_room(room, area_type):
    """
    Set up a Whisperwood room with appropriate resources and triggers.
    
    Args:
        room: The room object
        area_type: One of "edge", "paths", "clearing", "stump"
    """
    from world.triggers import add_trigger
    from world.random_events import register_ambient_events
    
    # Register ambient events for all whisperwood rooms
    register_ambient_events(room, [
        "rustling_leaves", 
        "bird_song", 
        "owl_hoot", 
        "scurrying"
    ])
    
    # Add area-specific triggers
    if area_type == "edge":
        for key in ["forest_edge_entry", "forest_edge_ambient"]:
            trigger = WHISPERWOOD_TRIGGERS[key]
            add_trigger(room, trigger["type"], 
                       trigger["effects"], 
                       trigger.get("conditions"))
    
    elif area_type == "paths":
        for key in ["shady_paths_whispers", "shady_paths_mushroom_glow"]:
            trigger = WHISPERWOOD_TRIGGERS[key]
            add_trigger(room, trigger["type"], 
                       trigger["effects"], 
                       trigger.get("conditions"))
        
        # Small chance of mushroom scene
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "whisperwood_mushroom_01"}],
            conditions=[{"type": "random", "chance": 0.03}]
        )
    
    elif area_type == "clearing":
        for key in ["clearing_fireflies", "clearing_fairy_ring"]:
            trigger = WHISPERWOOD_TRIGGERS[key]
            add_trigger(room, trigger["type"], 
                       trigger["effects"], 
                       trigger.get("conditions"))
        
        # Night visitor scene (rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "whisperwood_night_01"}],
            conditions=[
                {"type": "random", "chance": 0.05},
                {"type": "time_is", "value": "midnight"},
                {"type": "lacks_tag", "tag": "met_fae", "category": "encounters"}
            ]
        )
    
    elif area_type == "stump":
        for key in ["stump_presence", "stump_blessing"]:
            trigger = WHISPERWOOD_TRIGGERS[key]
            add_trigger(room, trigger["type"], 
                       trigger["effects"], 
                       trigger.get("conditions"))
    
    # Random slime encounter (any area, low chance)
    add_trigger(room, "enter",
        effects=[{"type": "start_scene", "scene": "whisperwood_slime_01"}],
        conditions=[{"type": "random", "chance": 0.02}]
    )
    
    # Bug mishap (any area with bug catching, very low chance)
    add_trigger(room, "enter",
        effects=[{"type": "start_scene", "scene": "whisperwood_bugmishap_01"}],
        conditions=[
            {"type": "random", "chance": 0.01},
            {"type": "has_item", "item": "net"}
        ]
    )
