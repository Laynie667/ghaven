"""
Room Atmosphere
===============

Atmosphere presets, ambient messages, and time-of-day effects.

Usage:
    room.atmosphere_preset = "tavern"
    room.do_ambient_tick()  # Called by game loop
"""

from typing import Dict, List, Optional
from enum import Enum
from random import choice, random


# =============================================================================
# TIME OF DAY
# =============================================================================

class TimeOfDay(Enum):
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    DUSK = "dusk"
    NIGHT = "night"
    MIDNIGHT = "midnight"


TIME_DESCRIPTIONS = {
    TimeOfDay.DAWN: {
        "sky": "The sky lightens with the first hints of dawn.",
        "light": "dim",
        "outdoor_mod": "The world stirs awake.",
    },
    TimeOfDay.MORNING: {
        "sky": "Morning light streams across the sky.",
        "light": "normal",
        "outdoor_mod": "The day has begun in earnest.",
    },
    TimeOfDay.MIDDAY: {
        "sky": "The sun hangs high overhead.",
        "light": "bright",
        "outdoor_mod": "Heat shimmers in the air.",
    },
    TimeOfDay.AFTERNOON: {
        "sky": "The afternoon sun casts long shadows.",
        "light": "normal",
        "outdoor_mod": "The day wears on.",
    },
    TimeOfDay.EVENING: {
        "sky": "The sun sinks toward the horizon.",
        "light": "dim",
        "outdoor_mod": "The world prepares for night.",
    },
    TimeOfDay.DUSK: {
        "sky": "The last light of day fades.",
        "light": "dim",
        "outdoor_mod": "Shadows lengthen and merge.",
    },
    TimeOfDay.NIGHT: {
        "sky": "Stars glitter in the dark sky.",
        "light": "dark",
        "outdoor_mod": "The world sleeps.",
    },
    TimeOfDay.MIDNIGHT: {
        "sky": "Darkness blankets everything.",
        "light": "dark",
        "outdoor_mod": "The deepest hours of night.",
    },
}


def get_time_of_day(hour: int) -> TimeOfDay:
    """Get time of day from game hour (0-23)."""
    if hour < 5:
        return TimeOfDay.MIDNIGHT
    elif hour < 7:
        return TimeOfDay.DAWN
    elif hour < 10:
        return TimeOfDay.MORNING
    elif hour < 14:
        return TimeOfDay.MIDDAY
    elif hour < 17:
        return TimeOfDay.AFTERNOON
    elif hour < 19:
        return TimeOfDay.EVENING
    elif hour < 21:
        return TimeOfDay.DUSK
    else:
        return TimeOfDay.NIGHT


# =============================================================================
# ATMOSPHERE PRESETS
# =============================================================================

ATMOSPHERE_PRESETS: Dict[str, Dict] = {
    # -------------------------------------------------------------------------
    # INDOOR - SOCIAL
    # -------------------------------------------------------------------------
    "tavern": {
        "name": "Tavern",
        "scent": "ale, woodsmoke, and roasted meat",
        "sounds": "the clink of mugs and low conversation",
        "ambient_messages": [
            "Someone laughs loudly at a joke.",
            "A barmaid weaves between tables with drinks.",
            "The fire crackles in the hearth.",
            "Dice clatter on a table nearby.",
            "A drunk sways unsteadily on their feet.",
            "The smell of fresh bread wafts from the kitchen.",
            "Someone calls for another round.",
            "A bard tunes their instrument in the corner.",
        ],
        "npc_types": ["ambient", "service"],
        "lighting": "dim",
    },
    
    "brothel": {
        "name": "Brothel",
        "scent": "perfume, incense, and musk",
        "sounds": "soft music and occasional moans from behind curtains",
        "ambient_messages": [
            "Silken curtains rustle in a doorway.",
            "Someone giggles behind a closed door.",
            "A worker leads a client upstairs.",
            "Incense smoke curls through the air.",
            "Soft music plays from somewhere.",
            "Someone adjusts their revealing attire.",
            "The madam surveys the room with a knowing smile.",
            "A muffled cry of pleasure echoes from above.",
        ],
        "npc_types": ["service", "companion"],
        "lighting": "dim",
    },
    
    "bathhouse": {
        "name": "Bathhouse",
        "scent": "steam, oils, and clean water",
        "sounds": "splashing water and soft conversation",
        "ambient_messages": [
            "Steam rises from the heated pools.",
            "Water splashes as someone enters a bath.",
            "An attendant offers fresh towels.",
            "Oil glistens on wet skin.",
            "Someone sighs contentedly in the warm water.",
            "Droplets of water patter on stone.",
            "The scent of bath oils intensifies.",
            "Soft laughter echoes off the tiles.",
        ],
        "npc_types": ["service", "ambient"],
        "lighting": "normal",
    },
    
    # -------------------------------------------------------------------------
    # INDOOR - PRIVATE
    # -------------------------------------------------------------------------
    "bedroom": {
        "name": "Bedroom",
        "scent": "clean linens and faint perfume",
        "sounds": "the creak of the bed and muffled sounds from beyond the walls",
        "ambient_messages": [
            "Candlelight flickers on the walls.",
            "The bed linens rustle softly.",
            "A draft stirs the curtains.",
            "Shadows dance in the corners.",
            "The bed creaks as weight shifts.",
            "Faint sounds drift through the walls.",
        ],
        "npc_types": [],
        "lighting": "dim",
    },
    
    "dungeon_cell": {
        "name": "Dungeon Cell",
        "scent": "damp stone and old straw",
        "sounds": "distant dripping and the rattle of chains",
        "ambient_messages": [
            "Water drips somewhere in the darkness.",
            "Chains rattle against stone.",
            "A rat scurries in the shadows.",
            "Cold seeps from the walls.",
            "A distant scream echoes briefly.",
            "Torchlight flickers under the door.",
            "The straw shifts with unseen movement.",
            "Metal creaks as old restraints settle.",
        ],
        "npc_types": ["guard"],
        "lighting": "dark",
    },
    
    "playroom": {
        "name": "Playroom",
        "scent": "leather, oil, and clean linen",
        "sounds": "the creak of equipment and occasional gasps",
        "ambient_messages": [
            "Leather creaks as equipment shifts.",
            "A chain sways gently.",
            "Someone tests a restraint's tightness.",
            "Oil gleams on waiting implements.",
            "A gasp escapes someone's lips.",
            "Buckles jingle softly.",
            "The bench groans under weight.",
            "A whimper echoes briefly.",
        ],
        "npc_types": [],
        "lighting": "dim",
    },
    
    # -------------------------------------------------------------------------
    # INDOOR - KENNEL/STABLE
    # -------------------------------------------------------------------------
    "kennel": {
        "name": "Kennel",
        "scent": "animal musk, straw, and leather",
        "sounds": "the shuffle of paws and occasional whines",
        "ambient_messages": [
            "A cage rattles as something shifts inside.",
            "A whimper comes from one of the pens.",
            "Claws click on the floor.",
            "A tail thumps against a cage wall.",
            "Someone pants softly in the darkness.",
            "Straw rustles in a nearby pen.",
            "A collar jingles as its wearer moves.",
            "A bowl scrapes against stone.",
        ],
        "npc_types": ["feral", "companion"],
        "lighting": "dim",
    },
    
    "stable": {
        "name": "Stable",
        "scent": "hay, horse, and leather",
        "sounds": "snorting, stamping hooves, and the swish of tails",
        "ambient_messages": [
            "A horse stamps in its stall.",
            "Hay rustles as something shifts.",
            "A tail swishes against wood.",
            "Bridles jingle on their hooks.",
            "Someone snorts and shakes their mane.",
            "Hooves clop against the floor.",
            "A whinny echoes through the stable.",
            "The smell of fresh hay fills the air.",
        ],
        "npc_types": ["feral"],
        "lighting": "dim",
    },
    
    # -------------------------------------------------------------------------
    # OUTDOOR - NATURAL
    # -------------------------------------------------------------------------
    "forest": {
        "name": "Forest",
        "scent": "pine, earth, and growing things",
        "sounds": "birdsong, rustling leaves, and distant animal calls",
        "ambient_messages": [
            "A bird calls from the canopy.",
            "Leaves rustle in the breeze.",
            "Sunlight dapples through the branches.",
            "A squirrel chatters angrily.",
            "Something moves in the underbrush.",
            "The scent of wildflowers drifts by.",
            "A branch creaks overhead.",
            "Insects buzz lazily in the air.",
        ],
        "npc_types": ["feral"],
        "time_aware": True,
    },
    
    "forest_clearing": {
        "name": "Forest Clearing",
        "scent": "grass, flowers, and fresh air",
        "sounds": "birdsong and the buzz of insects",
        "ambient_messages": [
            "Butterflies dance over the wildflowers.",
            "Grass sways in the gentle breeze.",
            "A deer peers from the treeline, then vanishes.",
            "Bees drone among the blossoms.",
            "Sunlight warms the open space.",
            "A rabbit nibbles at the grass nearby.",
            "Birds swoop overhead.",
            "The meadow hums with life.",
        ],
        "npc_types": ["feral"],
        "time_aware": True,
    },
    
    "wolf_den": {
        "name": "Wolf Den",
        "scent": "wolf musk, earth, and old bones",
        "sounds": "soft panting, growls, and the pad of paws",
        "ambient_messages": [
            "Yellow eyes gleam in the darkness.",
            "A wolf yawns, showing fangs.",
            "Tails thump against the earth.",
            "A low growl rumbles from somewhere.",
            "Paws pad softly on packed earth.",
            "Fur brushes against fur.",
            "Someone stretches and resettles.",
            "The alpha lifts their head, alert.",
        ],
        "npc_types": ["feral"],
        "lighting": "dark",
    },
    
    # -------------------------------------------------------------------------
    # OUTDOOR - WATER
    # -------------------------------------------------------------------------
    "lake_shore": {
        "name": "Lake Shore",
        "scent": "water, fish, and wet sand",
        "sounds": "lapping waves and distant waterfowl",
        "ambient_messages": [
            "Waves lap gently at the shore.",
            "A fish jumps, splashing back down.",
            "Ducks call from the water.",
            "Sand shifts underfoot.",
            "The water glitters in the light.",
            "Reeds sway at the water's edge.",
            "A frog croaks nearby.",
            "Something ripples beneath the surface.",
        ],
        "npc_types": ["feral"],
        "time_aware": True,
    },
    
    "hot_spring": {
        "name": "Hot Spring",
        "scent": "minerals, steam, and wet stone",
        "sounds": "bubbling water and contented sighs",
        "ambient_messages": [
            "Steam rises from the heated water.",
            "Bubbles break the surface.",
            "The mineral smell intensifies.",
            "Warm mist drifts across the pool.",
            "Someone sighs contentedly.",
            "Water splashes as someone shifts.",
            "The heat soaks deep into muscles.",
            "Stone glistens with moisture.",
        ],
        "npc_types": [],
        "lighting": "normal",
    },
    
    # -------------------------------------------------------------------------
    # SPECIAL
    # -------------------------------------------------------------------------
    "ritual_chamber": {
        "name": "Ritual Chamber",
        "scent": "incense, candle wax, and something older",
        "sounds": "soft chanting and the crackle of candles",
        "ambient_messages": [
            "Candle flames dance without wind.",
            "Shadows move at the edge of vision.",
            "The air feels thick and heavy.",
            "Ancient symbols seem to pulse.",
            "A chill runs down your spine.",
            "Whispers echo from nowhere.",
            "The incense smoke forms strange shapes.",
            "Power hums in the very stones.",
        ],
        "npc_types": ["unique"],
        "lighting": "dim",
    },
    
    "market": {
        "name": "Market",
        "scent": "spices, fresh bread, and too many bodies",
        "sounds": "haggling, shouting vendors, and clinking coins",
        "ambient_messages": [
            "A vendor calls out their wares.",
            "Coins clink as a sale is made.",
            "Someone haggles loudly.",
            "A child runs through the crowd.",
            "Exotic spices scent the air.",
            "A cart rumbles over cobblestones.",
            "Fabric rustles as merchants display goods.",
            "The crowd ebbs and flows around you.",
        ],
        "npc_types": ["service", "ambient"],
        "lighting": "bright",
        "time_aware": True,
    },
    
    # -------------------------------------------------------------------------
    # SPECIES-SPECIFIC AREAS
    # -------------------------------------------------------------------------
    "canine_den": {
        "name": "Canine Den",
        "scent": "canine musk, warm fur, and earth",
        "sounds": "soft panting, tail thumps, and occasional whines",
        "ambient_messages": [
            "A wolf stretches and yawns, showing fangs.",
            "Tails wag as pack members greet each other.",
            "Someone scratches behind their ear with a hindpaw.",
            "A contented rumble comes from the pile of furred bodies.",
            "Ears perk up at a distant sound.",
            "A wet nose nudges for attention.",
            "The warmth of many bodies fills the space.",
            "Someone circles three times before settling down.",
        ],
        "npc_types": ["feral"],
        "lighting": "dim",
    },
    
    "feline_lounge": {
        "name": "Feline Lounge",
        "scent": "feline musk, catnip, and warm sunbeams",
        "sounds": "purring, the pad of soft paws, and occasional meows",
        "ambient_messages": [
            "A cat stretches luxuriously in a sunbeam.",
            "Someone grooms their fur meticulously.",
            "A tail flicks with idle interest.",
            "Claws knead a soft surface contentedly.",
            "Eyes track invisible prey.",
            "A lazy yawn reveals sharp fangs.",
            "Someone pounces on absolutely nothing.",
            "Purring rumbles like distant thunder.",
        ],
        "npc_types": ["feral"],
        "lighting": "normal",
    },
    
    "equine_stable": {
        "name": "Equine Stable",
        "scent": "horse, hay, leather, and oats",
        "sounds": "soft nickers, stamping hooves, and the rustle of hay",
        "ambient_messages": [
            "A horse stamps impatiently.",
            "Hay crunches as someone eats.",
            "A tail swishes at flies.",
            "Hooves shift on the straw-covered floor.",
            "A soft nicker greets a newcomer.",
            "Someone tosses their mane.",
            "The smell of fresh hay intensifies.",
            "A horse nudges a pocket hopefully.",
        ],
        "npc_types": ["feral"],
        "lighting": "dim",
    },
    
    # -------------------------------------------------------------------------
    # DUNGEON/BDSM SPACES
    # -------------------------------------------------------------------------
    "playroom_public": {
        "name": "Public Play Space",
        "scent": "leather, sweat, and arousal",
        "sounds": "moans, the crack of impact, and heavy breathing",
        "ambient_messages": [
            "Someone cries out in pleasure or pain.",
            "Leather creaks under strain.",
            "Chains rattle as someone shifts.",
            "A paddle lands with a sharp crack.",
            "Whispered negotiations drift by.",
            "Someone begs breathlessly.",
            "A zipper slides open.",
            "Appreciative murmurs come from watchers.",
        ],
        "npc_types": ["service"],
        "lighting": "dim",
    },
    
    "breeding_room": {
        "name": "Breeding Chamber",
        "scent": "heavy musk, arousal, and pheromones",
        "sounds": "panting, wet sounds, and cries of pleasure",
        "ambient_messages": [
            "The scent of arousal hangs thick in the air.",
            "Flesh slaps against flesh.",
            "Someone moans loudly.",
            "A growl of possession rumbles nearby.",
            "The breeding bench creaks rhythmically.",
            "Panting fills the air.",
            "A knot swells to fullness.",
            "Someone cries out in climax.",
        ],
        "npc_types": ["feral", "companion"],
        "lighting": "dim",
    },
    
    "heat_room": {
        "name": "Heat Chamber",
        "scent": "overwhelming pheromones and desperate arousal",
        "sounds": "whimpering, panting, and needy whines",
        "ambient_messages": [
            "The air is thick with heat pheromones.",
            "Someone writhes in need.",
            "A desperate whine fills the room.",
            "The scent of a bitch in heat permeates everything.",
            "Restless movement from every corner.",
            "Someone presents themselves needfully.",
            "The heat is almost visible in the air.",
            "Instinct overwhelms thought.",
        ],
        "npc_types": ["feral"],
        "lighting": "dim",
    },
    
    # -------------------------------------------------------------------------
    # OUTDOOR - EXPANDED
    # -------------------------------------------------------------------------
    "meadow": {
        "name": "Meadow",
        "scent": "wildflowers, grass, and fresh air",
        "sounds": "buzzing bees, birdsong, and wind through grass",
        "ambient_messages": [
            "Butterflies dance among the flowers.",
            "Bees hum from bloom to bloom.",
            "The grass ripples in the breeze.",
            "A rabbit bounds away in the distance.",
            "Wildflowers sway gently.",
            "The sun warms your skin.",
            "A gentle breeze carries flower scent.",
            "Grasshoppers leap from underfoot.",
        ],
        "npc_types": ["feral"],
        "time_aware": True,
    },
    
    "swamp": {
        "name": "Swamp",
        "scent": "decay, stagnant water, and mud",
        "sounds": "croaking frogs, buzzing insects, and bubbling mud",
        "ambient_messages": [
            "Mud squelches underfoot.",
            "A frog croaks nearby.",
            "Mosquitoes whine around your head.",
            "Bubbles rise from the murky water.",
            "Something slithers through the reeds.",
            "The ground feels unstable.",
            "Mist curls across the water.",
            "An alligator's eyes watch from the shallows.",
        ],
        "npc_types": ["feral"],
        "lighting": "dim",
    },
    
    "mountain_cave": {
        "name": "Mountain Cave",
        "scent": "cold stone, mineral water, and ancient air",
        "sounds": "dripping water, echoes, and distant rumbles",
        "ambient_messages": [
            "Water drips with a steady rhythm.",
            "Your voice echoes into darkness.",
            "Stalactites glisten in what light there is.",
            "A cold draft comes from deeper within.",
            "Something scurries in the dark.",
            "The stone is cold and damp.",
            "Minerals sparkle in the walls.",
            "The cave seems to breathe.",
        ],
        "npc_types": ["feral"],
        "lighting": "dark",
    },
    
    # -------------------------------------------------------------------------
    # DOMESTIC/HOUSEHOLD
    # -------------------------------------------------------------------------
    "pet_bed": {
        "name": "Pet Quarters",
        "scent": "warm fur, treats, and familiar smells",
        "sounds": "soft breathing, the jingle of tags, and content sighs",
        "ambient_messages": [
            "A collar jingles as someone shifts.",
            "Soft snoring comes from a pile of pets.",
            "Someone's tail wags in their sleep.",
            "The pet bed creaks as weight shifts.",
            "A content sigh escapes someone.",
            "Food bowls sit in the corner.",
            "Chew toys lay scattered about.",
            "The warmth of the bed is inviting.",
        ],
        "npc_types": ["companion", "feral"],
        "lighting": "dim",
    },
    
    "owner_bedroom": {
        "name": "Master's Bedroom",
        "scent": "clean sheets, their perfume, and authority",
        "sounds": "soft music, the creak of the bed, and whispered commands",
        "ambient_messages": [
            "The bed dominates the room.",
            "Restraints hang from the headboard.",
            "A leash coils on the nightstand.",
            "The sheets are luxuriously soft.",
            "A collar awaits on the dresser.",
            "The room speaks of control.",
            "Candles flicker romantically.",
            "Commands seem to echo here.",
        ],
        "npc_types": [],
        "lighting": "dim",
    },
}


# =============================================================================
# NIGHT VARIANTS
# =============================================================================

NIGHT_AMBIENT = {
    "forest": [
        "An owl hoots in the darkness.",
        "Something howls in the distance.",
        "Crickets chirp endlessly.",
        "Glowing eyes watch from the shadows.",
        "The moon filters through the leaves.",
        "A twig snaps somewhere close.",
    ],
    "forest_clearing": [
        "Moonlight bathes the clearing in silver.",
        "Fireflies dance in the darkness.",
        "Nocturnal creatures stir.",
        "The grass is wet with dew.",
        "Stars wheel overhead.",
        "A fox barks in the distance.",
    ],
    "lake_shore": [
        "Moonlight glitters on the water.",
        "Frogs sing their night chorus.",
        "An owl glides silently overhead.",
        "Fish splash in the darkness.",
        "The water is black and still.",
        "Something large moves in the shallows.",
    ],
    "market": [
        "Empty stalls stand silent.",
        "A lone guard makes their rounds.",
        "Cats prowl between the booths.",
        "The cobblestones are slick with dew.",
        "Shuttered windows line the square.",
        "A drunk stumbles through the darkness.",
    ],
}


# =============================================================================
# WEATHER EFFECTS
# =============================================================================

WEATHER_AMBIENT = {
    "rain": [
        "Rain patters on every surface.",
        "Thunder rumbles in the distance.",
        "Water drips from overhangs.",
        "Puddles form in the low spots.",
        "The scent of rain fills the air.",
    ],
    "storm": [
        "Lightning splits the sky.",
        "Thunder crashes overhead.",
        "Wind howls fiercely.",
        "Rain lashes in sheets.",
        "Trees bend in the gale.",
    ],
    "snow": [
        "Snowflakes drift silently down.",
        "The world is muffled in white.",
        "Your breath mists in the cold.",
        "Ice crunches underfoot.",
        "The cold bites exposed skin.",
    ],
    "fog": [
        "Fog swirls around you.",
        "Visibility is limited to a few feet.",
        "Sounds seem muted and strange.",
        "Shapes loom and vanish.",
        "Moisture beads on everything.",
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_atmosphere_preset(key: str) -> Optional[Dict]:
    """Get an atmosphere preset by key."""
    return ATMOSPHERE_PRESETS.get(key)


def list_presets() -> List[str]:
    """List all available preset keys."""
    return list(ATMOSPHERE_PRESETS.keys())


def get_ambient_for_time(preset_key: str, time: TimeOfDay) -> List[str]:
    """Get ambient messages adjusted for time of day."""
    preset = ATMOSPHERE_PRESETS.get(preset_key, {})
    messages = list(preset.get("ambient_messages", []))
    
    # Add night variants if applicable
    if time in (TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT):
        night_msgs = NIGHT_AMBIENT.get(preset_key, [])
        messages.extend(night_msgs)
    
    return messages


def get_ambient_for_weather(weather: str) -> List[str]:
    """Get ambient messages for current weather."""
    return WEATHER_AMBIENT.get(weather, [])


def apply_preset_to_room(room, preset_key: str):
    """Apply an atmosphere preset to a room."""
    preset = ATMOSPHERE_PRESETS.get(preset_key)
    if not preset:
        return False
    
    room.atmosphere_preset = preset_key
    room.scent = preset.get("scent", "")
    room.sounds = preset.get("sounds", "")
    room.ambient_messages = preset.get("ambient_messages", [])
    
    if "lighting" in preset:
        room.db.lighting = preset["lighting"]
    
    return True


__all__ = [
    "TimeOfDay", "TIME_DESCRIPTIONS", "get_time_of_day",
    "ATMOSPHERE_PRESETS", "NIGHT_AMBIENT", "WEATHER_AMBIENT",
    "get_atmosphere_preset", "list_presets",
    "get_ambient_for_time", "get_ambient_for_weather",
    "apply_preset_to_room",
]
