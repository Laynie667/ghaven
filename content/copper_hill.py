"""
Copper Hill Content
===================

Mining area east of the Grove. Ore, gems, fossils, cave creatures.
Safe newbie area with cave-themed hazards - getting stuck, cave-ins,
creatures that live in the dark.

Areas:
- Hill Base (tutorial, surface rocks, tool vendor)
- Copper Tunnels (copper ore, stone, occasional gems)
- Crystal Cavern (better gems, cave bugs, glowing fungi)
- Deep Shaft (rare ore, fossils, mysterious depths)
"""

from world.scenes import register_scene
from world.triggers import add_trigger
from world.resources import create_resource_node

# =============================================================================
# RESOURCE DEFINITIONS
# =============================================================================

COPPER_HILL_RESOURCES = {
    # HILL BASE
    "surface_rocks": {
        "key": "loose rocks",
        "type": "mining",
        "yields": [
            {"key": "stone", "rarity": "common", "weight": 60},
            {"key": "flint", "rarity": "common", "weight": 25},
            {"key": "copper nugget", "rarity": "uncommon", "weight": 15},
        ],
        "max_harvests": 6,
        "respawn_time": 300,
        "desc": "Loose rocks on the hillside, easy to gather.",
    },
    
    "clay_deposit": {
        "key": "clay deposit",
        "type": "mining",
        "yields": [
            {"key": "clay", "rarity": "common", "weight": 70},
            {"key": "ite clay", "rarity": "uncommon", "weight": 25},
            {"key": "ite clay", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 400,
        "desc": "A deposit of workable clay.",
    },
    
    # COPPER TUNNELS
    "copper_vein": {
        "key": "copper vein",
        "type": "mining",
        "yields": [
            {"key": "copper ore", "rarity": "common", "weight": 60},
            {"key": "rich copper ore", "rarity": "uncommon", "weight": 30},
            {"key": "native copper", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 4,
        "respawn_time": 900,
        "desc": "Greenish-blue veins of copper ore in the rock.",
    },
    
    "coal_seam": {
        "key": "coal seam",
        "type": "mining",
        "yields": [
            {"key": "coal", "rarity": "common", "weight": 80},
            {"key": "jet", "rarity": "uncommon", "weight": 15},
            {"key": "black diamond", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 5,
        "respawn_time": 600,
        "desc": "A dark seam of coal running through the rock.",
    },
    
    "tunnel_bugs": {
        "key": "dark crevice",
        "type": "bugs",
        "yields": [
            {"key": "cave cricket", "rarity": "common", "weight": 50},
            {"key": "mining beetle", "rarity": "common", "weight": 30},
            {"key": "blind cave spider", "rarity": "uncommon", "weight": 15},
            {"key": "crystal beetle", "rarity": "rare", "weight": 5},
        ],
        "max_harvests": 3,
        "respawn_time": 600,
        "desc": "A dark crevice where cave creatures hide.",
    },
    
    # CRYSTAL CAVERN
    "quartz_cluster": {
        "key": "quartz cluster",
        "type": "mining",
        "yields": [
            {"key": "quartz", "rarity": "common", "weight": 50},
            {"key": "rose quartz", "rarity": "uncommon", "weight": 25},
            {"key": "smoky quartz", "rarity": "uncommon", "weight": 15},
            {"key": "amethyst", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 3,
        "respawn_time": 1200,
        "desc": "A beautiful cluster of crystalline quartz.",
    },
    
    "gem_pocket": {
        "key": "gem pocket",
        "type": "mining",
        "yields": [
            {"key": "rough garnet", "rarity": "uncommon", "weight": 40},
            {"key": "rough topaz", "rarity": "uncommon", "weight": 30},
            {"key": "rough emerald", "rarity": "rare", "weight": 20},
            {"key": "rough diamond", "rarity": "epic", "weight": 10},
        ],
        "max_harvests": 2,
        "respawn_time": 1800,
        "desc": "A pocket in the rock where gems have formed.",
    },
    
    "glowing_mushrooms": {
        "key": "glowcap cluster",
        "type": "forage",
        "yields": [
            {"key": "glowcap mushroom", "rarity": "common", "weight": 60},
            {"key": "bright glowcap", "rarity": "uncommon", "weight": 30},
            {"key": "eternal glowcap", "rarity": "rare", "weight": 10},
        ],
        "max_harvests": 4,
        "respawn_time": 900,
        "desc": "Mushrooms that glow with soft blue-green light.",
    },
    
    # DEEP SHAFT
    "iron_vein": {
        "key": "iron vein",
        "type": "mining",
        "yields": [
            {"key": "iron ore", "rarity": "common", "weight": 50},
            {"key": "rich iron ore", "rarity": "uncommon", "weight": 35},
            {"key": "magnetite", "rarity": "rare", "weight": 15},
        ],
        "max_harvests": 3,
        "respawn_time": 1200,
        "desc": "Rusty-red veins of iron ore.",
    },
    
    "silver_vein": {
        "key": "silver vein",
        "type": "mining",
        "yields": [
            {"key": "silver ore", "rarity": "uncommon", "weight": 60},
            {"key": "native silver", "rarity": "rare", "weight": 30},
            {"key": "electrum", "rarity": "epic", "weight": 10},
        ],
        "max_harvests": 2,
        "respawn_time": 2400,
        "desc": "Gleaming veins of silver in the deep rock.",
    },
    
    "fossil_bed": {
        "key": "fossil bed",
        "type": "mining",
        "yields": [
            {"key": "common fossil", "rarity": "common", "weight": 40},
            {"key": "shell fossil", "rarity": "uncommon", "weight": 30},
            {"key": "bone fossil", "rarity": "rare", "weight": 20},
            {"key": "complete skeleton", "rarity": "epic", "weight": 8},
            {"key": "ancient creature fossil", "rarity": "legendary", "weight": 2},
        ],
        "max_harvests": 2,
        "respawn_time": 3600,
        "desc": "Ancient creatures preserved in stone.",
    },
}


# =============================================================================
# ROOM TRIGGERS
# =============================================================================

COPPER_HILL_TRIGGERS = {
    # Hill Base
    "base_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|gWelcome to Copper Hill!|n

The hillside rises before you, dotted with mine entrances and 
the glint of exposed ore. You can hear the distant ring of 
pickaxes from deeper within.

|wTip:|n Use |wmine|n to extract ore and gems. You'll need a 
pickaxe for the harder deposits!

|yNote:|n The deeper tunnels can be dangerous. Watch your step.
"""}
        ],
    },
    
    "base_miners": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "A group of miners trudges past, covered in dust, pickaxes over their shoulders."}
        ],
    },
    
    # Copper Tunnels
    "tunnels_drip": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "Water drips steadily from the tunnel ceiling. The sound echoes in the darkness."}
        ],
    },
    
    "tunnels_creak": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.1}],
        "effects": [
            {"type": "message", "text": "|xThe support timbers creak ominously. Probably nothing to worry about.|n"}
        ],
    },
    
    # Crystal Cavern
    "cavern_entry": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
You step into the Crystal Cavern and catch your breath.

The walls glitter with countless gems, catching the light of 
glowing mushrooms and reflecting it in a thousand colors. It's 
like standing inside a geode.

Somewhere in the darkness, something skitters.
"""}
        ],
    },
    
    "cavern_glow": {
        "type": "enter",
        "effects": [
            {"type": "message", "text": "Bioluminescent mushrooms pulse with soft blue-green light, making the crystals shimmer."}
        ],
    },
    
    # Deep Shaft
    "deep_warning": {
        "type": "enter",
        "conditions": [{"type": "first_visit"}],
        "effects": [
            {"type": "message", "text": """
|yWarning: Deep Shaft|n

The air here is different—colder, staler. Your torchlight barely 
penetrates the darkness ahead.

Experienced miners speak of strange things in the deep places. 
Things that lived here before the mines. Things that don't like 
visitors.

Proceed with caution.
"""}
        ],
    },
    
    "deep_sounds": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.3}],
        "effects": [
            {"type": "message", "text": "|xYou hear something moving in the darkness below. Heavy. Slow. Patient.|n"}
        ],
    },
    
    "deep_cold": {
        "type": "enter",
        "conditions": [{"type": "random", "chance": 0.2}],
        "effects": [
            {"type": "message", "text": "A chill wind blows from somewhere deep below. It smells of old stone and older things."}
        ],
    },
}


# =============================================================================
# SCENES
# =============================================================================

# Getting stuck in a tight space
STUCK_IN_CAVE_SCENE = {
    "id": "copper_stuck_01",
    "title": "Tight Squeeze",
    "tags": ["hazard", "cave", "copper_hill", "mild"],
    
    "start": {
        "text": """
You spot a glint of something valuable in a narrow crevice and 
reach in to grab it.

Your hand closes on... something. A gem? But when you try to 
pull back, you realize you're stuck. The rock has pinched 
around your arm.

You tug. Nothing. You tug harder. Still nothing.

This is embarrassing.
""",
        "choices": [
            {"text": "Keep pulling", "goto": "pull"},
            {"text": "Try to relax and wiggle free", "goto": "wiggle"},
            {"text": "Call for help", "goto": "call"},
            {"text": "Use your pickaxe to chip the rock", "goto": "chip",
             "condition": {"type": "has_item", "item": "pickaxe"}},
        ]
    },
    
    "pull": {
        "text": """
You brace your feet and pull with all your strength.

There's a moment of resistance, then your arm scrapes free— 
leaving a fair amount of skin behind on the rough stone.

|rOw.|n

You stumble backward, arm stinging, but at least you're free. 
And you're still holding whatever you grabbed.

It's... a rock. Just a shiny rock.

Worth it? Debatable.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "scraped_arm", 
             "category": "debuff", "duration": 1800},
            {"type": "give_item", "key": "shiny rock", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "wiggle": {
        "text": """
You force yourself to relax. Panicking won't help. You rotate 
your wrist, shift your fingers, find the angle that lets your 
arm slide free.

It takes a few minutes of patient maneuvering, but eventually 
you're free without a scratch.

You even managed to keep hold of what you grabbed: a small but 
genuine gemstone.

Patience pays off.
""",
        "effects": [
            {"type": "give_item", "key": "rough garnet", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    },
    
    "call": {
        "text": """
"Hello? Is anyone there? I'm stuck!"

Your voice echoes through the tunnels. For a long moment, 
nothing.

Then footsteps, and a weathered face appears in the torchlight. 
An old miner, grinning at your predicament.

"New to the caves, eh? Hold still."

She produces a small bottle of oil and works it around your 
trapped arm. A minute later, you slide free.

"Happens to everyone once," she says. "Only the fools let it 
happen twice."

She wanders off, chuckling, leaving you embarrassed but free.
""",
        "end": True
    },
    
    "chip": {
        "text": """
You carefully work your pickaxe into the crevice, chipping away 
at the rock that's pinching your arm.

It's awkward work—one-handed, in the dark—but eventually you 
create enough space to slide free.

In the process, you also uncover a small pocket of gems that 
was hidden behind the rock.

Maybe getting stuck was lucky after all.
""",
        "effects": [
            {"type": "give_item", "key": "rough garnet", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "rough topaz", 
             "typeclass": "typeclasses.objects.Object"}
        ],
        "end": True
    }
}

register_scene("copper_stuck_01", STUCK_IN_CAVE_SCENE)


# Cave creature encounter
CAVE_CREATURE_SCENE = {
    "id": "copper_creature_01",
    "title": "Something in the Dark",
    "tags": ["encounter", "creature", "copper_hill", "mysterious"],
    
    "start": {
        "text": """
Your torch flickers. Just a draft, probably.

Then it flickers again. And goes out.

In the sudden darkness, you become aware of something breathing. 
Something large. Something very close.

Two points of light appear in the blackness—eyes, reflecting 
the last embers of your torch. They're at about knee height, 
which means whatever owns them is either very short or very 
low to the ground.

The breathing continues. Slow. Patient.
""",
        "choices": [
            {"text": "Stay perfectly still", "goto": "still"},
            {"text": "Try to relight your torch", "goto": "light"},
            {"text": "\"Hello?\"", "goto": "greet"},
            {"text": "Run", "goto": "run"},
        ]
    },
    
    "still": {
        "text": """
You hold your breath. The creature continues to watch you with 
those glowing eyes.

Minutes pass. Neither of you moves.

Eventually, the eyes blink once, slowly. Then they move away, 
accompanied by the soft scraping of something heavy dragging 
across stone.

When you finally get your torch relit, the tunnel is empty. 
But there are marks in the dust—wide, serpentine tracks leading 
deeper into the mountain.

Whatever that was, it decided you weren't interesting.

You're not sure if you should be relieved or offended.
""",
        "end": True
    },
    
    "light": {
        "text": """
Your hands shake as you fumble for your flint. One strike. Two.

On the third strike, the torch catches—and you see the creature.

It's a cave wyrm. About six feet long, pale and eyeless except 
for those bioluminescent patches that looked like eyes. It 
flinches from the light, hissing, and retreats into a crevice.

Not dangerous, apparently. Just startling.

You make a note to carry extra torches.
""",
        "effects": [
            {"type": "add_tag", "tag": "saw_cave_wyrm", "category": "encounters"}
        ],
        "end": True
    },
    
    "greet": {
        "text": """
"Hello?"

The eyes tilt, as if the creature is cocking its head. Then a 
voice emerges from the darkness—not spoken exactly, more felt:

|y*You... speak? Surfacer who speaks to dark things. Unusual.*|n

The eyes come closer. You can feel warmth now, and the smell 
of deep stone and old mushrooms.

|y*Most run. Most fear. You greet. Why?*|n
""",
        "choices": [
            {"text": "\"I didn't want to be rude.\"", "goto": "polite"},
            {"text": "\"What are you?\"", "goto": "what_are_you"},
            {"text": "\"I'm actually terrified.\"", "goto": "honest"},
        ]
    },
    
    "run": {
        "text": """
You bolt into the darkness, hands outstretched, praying you 
don't run into a wall.

Behind you, something makes a sound—laughter? disappointment?— 
and doesn't give chase.

You run until you see light ahead, bursting out of the tunnels 
into the blessed openness of the main shaft.

You don't go back into the deep tunnels for a while after that.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "shaken", 
             "category": "debuff", "duration": 1800}
        ],
        "end": True
    },
    
    "polite": {
        "text": """
"I didn't want to be rude."

The creature makes a sound like grinding stones—laughter, maybe.

|y*Rude. Polite. Surface words. But... appreciated.*|n

Something presses against your palm in the darkness. Cold, 
smooth, heavy.

|y*Gift. For politeness. Rare, in the deep.*|n

When you finally relight your torch, the creature is gone. In 
your hand is a gem unlike any you've seen—dark, with inner fire 
that seems to move.

A gift from the dark.
""",
        "effects": [
            {"type": "give_item", "key": "deepfire gem", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "deep_friend", "category": "encounters"}
        ],
        "end": True
    },
    
    "what_are_you": {
        "text": """
"What are you?"

|y*Old. Very old. Older than the tunnels. Older than the hill. 
We were here before your kind learned to dig.*|n

The eyes move in a slow circle around you.

|y*We are the dark. The deep. The patient stone. We do not 
harm those who do not harm us.*|n

It pauses.

|y*But we remember those who dig too deep. Those who take too 
much. Those who wake things that should sleep.*|n

The eyes begin to recede into the darkness.

|y*Mine carefully, surfacer. Not everything in the mountain 
is as patient as we are.*|n

You're left alone with a warning and a lot of questions.
""",
        "effects": [
            {"type": "add_tag", "tag": "deep_warned", "category": "encounters"}
        ],
        "end": True
    },
    
    "honest": {
        "text": """
"I'm actually terrified."

|y*Honest.*|n The creature sounds almost pleased. |y*Fear is 
wise, in the dark. But you did not run. That is also wise.*|n

The eyes come closer, until you can feel the creature's breath 
on your face. It smells like minerals and centuries.

|y*Fear and bravery. Good combination. You will survive here.*|n

Something touches your forehead—cold, rough, like stone. And 
then the creature is gone, leaving you in darkness with a 
strange blessing humming in your bones.

When you relight your torch, you feel different. More aware of 
the stone around you. More at home in the dark.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "stone_sense", 
             "category": "buff", "duration": 7200},
            {"type": "add_tag", "tag": "deep_blessed", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("copper_creature_01", CAVE_CREATURE_SCENE)


# Cave-in/collapse scene
CAVE_IN_SCENE = {
    "id": "copper_cavein_01",
    "title": "Collapse",
    "tags": ["hazard", "cave", "copper_hill", "action"],
    
    "start": {
        "text": """
The first warning is a trickle of dust from the ceiling.

The second warning is a crack that echoes through the tunnel 
like a gunshot.

There is no third warning.

|rThe ceiling is coming down.|n
""",
        "choices": [
            {"text": "Dive forward!", "goto": "forward"},
            {"text": "Dive backward!", "goto": "backward"},
            {"text": "Find cover!", "goto": "cover"},
        ]
    },
    
    "forward": {
        "text": """
You throw yourself forward, rolling as rocks crash down behind 
you. Dust fills the air, blinding and choking.

When the rumbling stops, you're alive. Bruised, covered in dust, 
but alive.

The tunnel behind you is completely blocked. Tons of rock fill 
the space where you were standing a moment ago.

You'll have to find another way out. But at least you're on 
the right side of the collapse.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "dusty", 
             "category": "status", "duration": 600},
            {"type": "apply_effect", "effect_key": "bruised", 
             "category": "debuff", "duration": 1800}
        ],
        "end": True
    },
    
    "backward": {
        "text": """
You throw yourself backward, scrambling away from the collapse. 
Rocks thunder down, filling the tunnel ahead with rubble.

When the dust settles, you're safe—but the way forward is 
completely blocked.

The good news: you're alive, and you can go back the way you 
came.

The bad news: whatever was in that tunnel is staying there. 
Hopefully the miners can clear it eventually.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "dusty", 
             "category": "status", "duration": 600}
        ],
        "end": True
    },
    
    "cover": {
        "text": """
You spot a support beam and dive beneath it as the ceiling 
comes down. Rocks hammer the beam above you—but it holds.

You curl into a ball, arms over your head, as the world shakes 
and roars.

Then silence.

You're in a small pocket, surrounded by rubble but protected 
by the beam. It's dark and dusty and terrifying.

But you hear voices. Distant, muffled, but voices.

"HELLO?" you scream. "I'M IN HERE!"

The rescue takes an hour, but they get you out. Shaken, scared, 
but unharmed.

The other miners buy you drinks for a week.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "survivor", 
             "category": "buff", "duration": 3600},
            {"type": "add_tag", "tag": "cave_in_survivor", "category": "encounters"}
        ],
        "end": True
    }
}

register_scene("copper_cavein_01", CAVE_IN_SCENE)


# Crystal cavern discovery
CRYSTAL_DISCOVERY_SCENE = {
    "id": "copper_crystal_01",
    "title": "Hidden Geode",
    "tags": ["discovery", "treasure", "copper_hill", "wonder"],
    
    "start": {
        "text": """
Your pickaxe breaks through into empty space.

You peer through the hole and gasp. Beyond is a chamber you've 
never seen—a natural geode the size of a room, lined entirely 
with crystals.

Purple amethyst, rose quartz, clear as water, formations that 
catch your torchlight and scatter it into a thousand rainbows.

It's beautiful. And judging by the undisturbed dust, no one has 
been here in a very, very long time.
""",
        "choices": [
            {"text": "Squeeze through and explore", "goto": "explore"},
            {"text": "Reach in and grab what you can", "goto": "grab"},
            {"text": "Mark the location and report it", "goto": "report"},
        ]
    },
    
    "explore": {
        "text": """
You widen the hole enough to squeeze through and enter the 
crystal chamber.

It's even more beautiful up close. The crystals hum faintly, 
resonating with some deep frequency you feel more than hear.

At the center of the chamber, on a natural pedestal of stone, 
sits a single perfect crystal—clear as water, large as your 
fist, glowing with inner light.

It's the most valuable thing you've ever seen.
""",
        "choices": [
            {"text": "Take the crystal", "goto": "take_crystal"},
            {"text": "Leave it and take only smaller crystals", "goto": "take_small"},
            {"text": "Just look and leave", "goto": "just_look"},
        ]
    },
    
    "grab": {
        "text": """
You reach through the hole and grab the nearest crystals, 
prying them from the walls. They come free in your hands, 
glittering and beautiful.

You stuff your pockets full, take everything you can carry, 
and withdraw.

It's a fortune. An absolute fortune. You're rich.

As you leave, you hear a sound from the chamber—a high, keening 
note, like something mourning. But that's just wind through the 
crystals.

Right?
""",
        "effects": [
            {"type": "give_item", "key": "amethyst cluster", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "rose quartz", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "clear quartz", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "apply_effect", "effect_key": "crystal_guilt", 
             "category": "status", "duration": 3600}
        ],
        "end": True
    },
    
    "report": {
        "text": """
You memorize the location and seal the hole back up as best you 
can. A find like this belongs to everyone, not just you.

When you report it to the miners' guild, they're skeptical at 
first—then astonished when they see it for themselves.

They name the chamber after you.

The guild gives you a finder's fee: a generous sum and first 
pick of the crystals once they're properly extracted. Less than 
you could have grabbed, but earned honestly.

And whenever you visit the chamber, now properly excavated and 
lit, you feel a strange sense of pride.

Some things are worth more than money.
""",
        "effects": [
            {"type": "give_currency", "amount": 500},
            {"type": "give_item", "key": "perfect quartz", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "discoverer", "category": "encounters"}
        ],
        "end": True
    },
    
    "take_crystal": {
        "text": """
You reach for the perfect crystal.

The moment your fingers touch it, the chamber goes dark. The 
humming stops. The air goes cold.

Something speaks, not in words but in feeling:

|y*THIEF.*|n

Then the light returns, and you're standing outside the chamber 
with no memory of how you got there. The hole is gone. The wall 
is solid rock.

In your hand is a small, cracked crystal—a fragment of what 
you tried to take.

The geode is gone. Maybe it was never there. Or maybe it just 
doesn't want to be found by you anymore.
""",
        "effects": [
            {"type": "give_item", "key": "cracked crystal", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "apply_effect", "effect_key": "mountain_displeasure", 
             "category": "debuff", "duration": 7200}
        ],
        "end": True
    },
    
    "take_small": {
        "text": """
You leave the central crystal alone—it feels wrong to take it— 
but gather a few of the smaller crystals from the walls.

As you work, you hear that humming again. It sounds almost... 
approving?

When you leave, you swear the central crystal pulses once, 
like a heartbeat. Like a thank-you.

You got your treasure, and you feel good about it. Sometimes 
restraint is its own reward.
""",
        "effects": [
            {"type": "give_item", "key": "pure amethyst", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "give_item", "key": "rose quartz heart", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "mountain_respect", "category": "encounters"}
        ],
        "end": True
    },
    
    "just_look": {
        "text": """
You sit in the crystal chamber and just... look.

It's beautiful. Maybe the most beautiful thing you've ever seen. 
And for this moment, it's yours alone—a secret between you and 
the mountain.

When you finally leave, you take nothing but the memory.

As you squeeze back through the hole, you feel something press 
against your palm—a small crystal that wasn't there before. 
A gift, given freely.

Some things you can't take. They have to choose you.
""",
        "effects": [
            {"type": "give_item", "key": "mountain's gift", 
             "typeclass": "typeclasses.objects.Object"},
            {"type": "add_tag", "tag": "mountain_friend", "category": "encounters"},
            {"type": "apply_effect", "effect_key": "crystal_peace", 
             "category": "buff", "duration": 14400}
        ],
        "end": True
    }
}

register_scene("copper_crystal_01", CRYSTAL_DISCOVERY_SCENE)


# =============================================================================
# BUILDER HELPER FUNCTION
# =============================================================================

def setup_copper_hill_room(room, area_type):
    """
    Set up a Copper Hill room with resources and triggers.
    
    Args:
        room: The room object
        area_type: One of "base", "tunnels", "cavern", "deep"
    """
    from world.triggers import add_trigger
    from world.random_events import register_ambient_events
    
    # Ambient events for cave areas
    if area_type == "base":
        register_ambient_events(room, ["pickaxe_sounds", "cart_rumble"])
    else:
        register_ambient_events(room, ["dripping_water", "distant_rumble"])
    
    if area_type == "base":
        for key in ["base_entry", "base_miners"]:
            trigger = COPPER_HILL_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
    
    elif area_type == "tunnels":
        for key in ["tunnels_drip", "tunnels_creak"]:
            trigger = COPPER_HILL_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Getting stuck (rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "copper_stuck_01"}],
            conditions=[{"type": "random", "chance": 0.02}]
        )
        
        # Cave-in (very rare)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "copper_cavein_01"}],
            conditions=[{"type": "random", "chance": 0.005}]
        )
    
    elif area_type == "cavern":
        for key in ["cavern_entry", "cavern_glow"]:
            trigger = COPPER_HILL_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Crystal discovery (rare, first time)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "copper_crystal_01"}],
            conditions=[
                {"type": "random", "chance": 0.05},
                {"type": "lacks_tag", "tag": "found_geode", "category": "encounters"}
            ]
        )
    
    elif area_type == "deep":
        for key in ["deep_warning", "deep_sounds", "deep_cold"]:
            trigger = COPPER_HILL_TRIGGERS[key]
            add_trigger(room, trigger["type"],
                       trigger["effects"],
                       trigger.get("conditions"))
        
        # Deep creature (rare, first time)
        add_trigger(room, "enter",
            effects=[{"type": "start_scene", "scene": "copper_creature_01"}],
            conditions=[
                {"type": "random", "chance": 0.08},
                {"type": "lacks_tag", "tag": "deep_warned", "category": "encounters"},
                {"type": "lacks_tag", "tag": "deep_friend", "category": "encounters"},
                {"type": "lacks_tag", "tag": "deep_blessed", "category": "encounters"}
            ]
        )
