"""
Random Events System for Gilderhaven
=====================================

Ambient events, room events, and world events that fire randomly.
Creates life and unexpected occurrences in the world.

Event Types:
- Ambient: Flavor messages with no mechanical effect
- Room Events: Things that happen in specific locations
- World Events: Global events affecting multiple areas
- Personal Events: Random things that happen to specific characters

Usage:
    # Register events for a room
    from world.random_events import register_room_events
    register_room_events(room, ["rustling_leaves", "bird_song", "distant_thunder"])
    
    # Fire random events (called by tick script)
    from world.random_events import tick_random_events
    tick_random_events()
"""

import random
import time
from evennia.utils import logger

# =============================================================================
# Event Definitions
# =============================================================================

# Ambient events - pure flavor, no mechanics
AMBIENT_EVENTS = {
    # Nature
    "rustling_leaves": {
        "messages": [
            "Leaves rustle in a passing breeze.",
            "A gentle wind stirs the foliage.",
            "The trees whisper among themselves.",
        ],
        "conditions": {"outdoors": True},
        "weight": 10,
    },
    "bird_song": {
        "messages": [
            "A bird trills somewhere nearby.",
            "Birdsong echoes through the area.",
            "A melody of birdsong fills the air.",
        ],
        "conditions": {"outdoors": True, "time": ["morning", "day"]},
        "weight": 8,
    },
    "owl_hoot": {
        "messages": [
            "An owl hoots in the darkness.",
            "A distant owl calls out.",
        ],
        "conditions": {"outdoors": True, "time": ["night"]},
        "weight": 6,
    },
    "cricket_chirp": {
        "messages": [
            "Crickets chirp in the darkness.",
            "The rhythmic chirping of crickets fills the night.",
        ],
        "conditions": {"outdoors": True, "time": ["evening", "night"]},
        "weight": 7,
    },
    
    # Weather-related
    "distant_thunder": {
        "messages": [
            "Thunder rumbles in the distance.",
            "A low growl of thunder rolls across the sky.",
        ],
        "conditions": {"weather": ["storm", "rain"]},
        "weight": 5,
    },
    "rain_intensifies": {
        "messages": [
            "The rain picks up momentarily.",
            "A heavier sheet of rain sweeps through.",
        ],
        "conditions": {"weather": ["rain", "storm"]},
        "weight": 6,
    },
    "wind_gust": {
        "messages": [
            "A sudden gust of wind sweeps through.",
            "The wind picks up momentarily.",
        ],
        "conditions": {"weather": ["storm", "clear"]},
        "weight": 5,
    },
    
    # Market/Urban
    "distant_voices": {
        "messages": [
            "Distant voices carry on the wind.",
            "You hear conversation from somewhere nearby.",
            "Laughter echoes from afar.",
        ],
        "conditions": {"tags": ["urban", "market", "social"]},
        "weight": 8,
    },
    "merchant_call": {
        "messages": [
            "A merchant calls out their wares somewhere nearby.",
            "\"Fresh goods! Come see!\" echoes from a nearby stall.",
        ],
        "conditions": {"tags": ["market"]},
        "weight": 7,
    },
    
    # Mystical
    "magical_shimmer": {
        "messages": [
            "The air shimmers with faint magical energy.",
            "You catch a flicker of arcane light at the edge of your vision.",
        ],
        "conditions": {"tags": ["magical", "grove", "museum"]},
        "weight": 4,
    },
    "whispers": {
        "messages": [
            "You could swear you hear whispering...",
            "Faint whispers seem to come from nowhere.",
            "Was that... a voice?",
        ],
        "conditions": {"tags": ["haunted", "magical", "mysterious"]},
        "weight": 3,
    },
    
    # Animals
    "scurrying": {
        "messages": [
            "Something small scurries past.",
            "You hear tiny feet pattering nearby.",
            "A small creature darts into hiding.",
        ],
        "conditions": {},
        "weight": 6,
    },
    "cat_watching": {
        "messages": [
            "A cat watches you from a nearby perch.",
            "You notice a cat's eyes gleaming from the shadows.",
        ],
        "conditions": {"tags": ["urban", "market", "grove"]},
        "weight": 4,
    },
}


# Room events - can have mechanical effects
ROOM_EVENTS = {
    "wandering_merchant": {
        "message": "A wandering merchant passes through, glancing around before moving on.",
        "conditions": {"tags": ["market", "road", "plaza"]},
        "weight": 2,
        "effects": [],  # Could spawn temporary merchant NPC
    },
    "guard_patrol": {
        "message": "A guard patrol marches through, eyeing everyone briefly.",
        "conditions": {"tags": ["urban", "market", "plaza"]},
        "weight": 3,
        "effects": [],
    },
    "mysterious_figure": {
        "message": "A cloaked figure slips through the shadows at the edge of your vision.",
        "conditions": {"time": ["evening", "night"]},
        "weight": 1,
        "effects": [],
    },
    "street_performer": {
        "message": "A street performer begins playing a lively tune nearby.",
        "conditions": {"tags": ["market", "plaza", "social"]},
        "weight": 2,
        "effects": [],
        "duration": 60,  # Performer stays for 60 seconds
    },
    "dropped_coin": {
        "message": "Something glints on the ground - someone dropped a coin!",
        "conditions": {"tags": ["market", "plaza", "urban"]},
        "weight": 1,
        "effects": [
            {"type": "spawn_object", "key": "dropped coin", "value": 1}
        ],
    },
    "rare_butterfly": {
        "message": "A beautiful, unusual butterfly flutters past!",
        "conditions": {"outdoors": True, "time": ["morning", "day"]},
        "weight": 1,
        "effects": [
            {"type": "spawn_temporary", "key": "rare butterfly", "duration": 30}
        ],
    },
}


# Personal events - happen TO a specific character
PERSONAL_EVENTS = {
    "pocket_lint": {
        "message": "You find some lint in your pocket.",
        "weight": 1,
        "effects": [],
    },
    "deja_vu": {
        "message": "You experience a sudden sense of déjà vu...",
        "weight": 2,
        "effects": [],
    },
    "sneeze": {
        "message": "You sneeze suddenly.",
        "room_message": "{character} sneezes.",
        "weight": 3,
        "effects": [],
    },
    "yawn": {
        "message": "A yawn escapes you.",
        "room_message": "{character} yawns.",
        "weight": 4,
        "effects": [],
    },
    "chill": {
        "message": "A chill runs down your spine for no apparent reason.",
        "weight": 2,
        "effects": [],
        "conditions": {"time": ["night", "evening"]},
    },
    "pocket_picked": {
        "message": "|rYou feel a brush against your pocket... wait, where's your coin pouch?|n",
        "weight": 0.5,
        "conditions": {"tags": ["market", "crowded"]},
        "effects": [
            {"type": "take_currency", "amount": 5, "min_balance": 10}
        ],
    },
    "lucky_find": {
        "message": "|gYou spot a coin on the ground!|n",
        "weight": 1,
        "effects": [
            {"type": "give_currency", "amount": 1}
        ],
    },
}


# World events - affect multiple rooms/areas
WORLD_EVENTS = {
    "shooting_star": {
        "message": "A shooting star streaks across the sky!",
        "conditions": {"time": ["night"], "weather": ["clear"]},
        "scope": "outdoors",  # All outdoor rooms
        "weight": 0.5,
        "effects": [],
    },
    "rainbow": {
        "message": "A beautiful rainbow arcs across the sky!",
        "conditions": {"weather": ["rain"], "time": ["day"]},
        "scope": "outdoors",
        "weight": 1,
        "duration": 120,
        "effects": [],
    },
    "eclipse": {
        "message": "|yThe sun begins to darken... an eclipse!|n",
        "conditions": {"time": ["day"]},
        "scope": "all",
        "weight": 0.1,
        "duration": 300,
        "effects": [
            {"type": "temporary_time", "value": "night"}
        ],
    },
    "market_sale": {
        "message": "|gA merchant in the market announces a flash sale!|n",
        "conditions": {},
        "scope": "tags:market",
        "weight": 0.5,
        "duration": 300,
        "effects": [],
    },
}


# =============================================================================
# Event Checking & Firing
# =============================================================================

def check_event_conditions(event, room=None, character=None):
    """
    Check if an event's conditions are met.
    
    Args:
        event: Event dict
        room: Room to check (optional)
        character: Character to check (optional)
    
    Returns:
        bool: True if conditions met
    """
    conditions = event.get("conditions", {})
    
    # Check outdoors
    if "outdoors" in conditions:
        if room:
            is_outdoor = room.tags.has("outdoor", category="room_type") or \
                        room.db.outdoor
            if conditions["outdoors"] != is_outdoor:
                return False
    
    # Check time
    if "time" in conditions:
        try:
            from world.world_state import get_time_period
            current_time = get_time_period()
            if current_time not in conditions["time"]:
                return False
        except ImportError:
            pass
    
    # Check weather
    if "weather" in conditions:
        try:
            from world.world_state import get_weather
            current_weather = get_weather()
            if current_weather not in conditions["weather"]:
                return False
        except ImportError:
            pass
    
    # Check room tags
    if "tags" in conditions and room:
        required_tags = conditions["tags"]
        has_any = False
        for tag in required_tags:
            if room.tags.has(tag):
                has_any = True
                break
        if not has_any:
            return False
    
    return True


def select_weighted_event(events, room=None, character=None):
    """
    Select an event from a dict based on weight and conditions.
    
    Args:
        events: Dict of event_key: event_dict
        room: Room context
        character: Character context
    
    Returns:
        tuple: (event_key, event_dict) or (None, None)
    """
    valid_events = []
    
    for key, event in events.items():
        if check_event_conditions(event, room, character):
            weight = event.get("weight", 1)
            valid_events.append((key, event, weight))
    
    if not valid_events:
        return None, None
    
    # Weighted selection
    total_weight = sum(e[2] for e in valid_events)
    roll = random.random() * total_weight
    
    cumulative = 0
    for key, event, weight in valid_events:
        cumulative += weight
        if roll <= cumulative:
            return key, event
    
    return valid_events[-1][0], valid_events[-1][1]


def fire_ambient_event(room):
    """
    Fire a random ambient event in a room.
    
    Args:
        room: Room to fire event in
    
    Returns:
        bool: True if event fired
    """
    # Get room's registered ambient events, or use defaults
    registered = room.db.ambient_events
    
    if registered:
        # Filter to registered events
        events = {k: v for k, v in AMBIENT_EVENTS.items() if k in registered}
    else:
        events = AMBIENT_EVENTS
    
    event_key, event = select_weighted_event(events, room=room)
    
    if not event:
        return False
    
    # Select random message
    messages = event.get("messages", [])
    if not messages:
        return False
    
    message = random.choice(messages)
    
    # Send to room
    room.msg_contents(f"|x{message}|n")
    
    return True


def fire_room_event(room):
    """
    Fire a random room event.
    
    Args:
        room: Room to fire event in
    
    Returns:
        bool: True if event fired
    """
    registered = room.db.room_events
    
    if registered:
        events = {k: v for k, v in ROOM_EVENTS.items() if k in registered}
    else:
        events = ROOM_EVENTS
    
    event_key, event = select_weighted_event(events, room=room)
    
    if not event:
        return False
    
    message = event.get("message", "Something happens.")
    room.msg_contents(message)
    
    # Execute effects
    _execute_room_event_effects(event, room)
    
    return True


def fire_personal_event(character):
    """
    Fire a random personal event for a character.
    
    Args:
        character: Character to fire event for
    
    Returns:
        bool: True if event fired
    """
    room = character.location
    
    event_key, event = select_weighted_event(PERSONAL_EVENTS, room=room, character=character)
    
    if not event:
        return False
    
    # Send personal message
    message = event.get("message", "Something happens to you.")
    character.msg(message)
    
    # Send room message if present
    room_message = event.get("room_message")
    if room_message and room:
        formatted = room_message.format(character=character.key)
        room.msg_contents(formatted, exclude=[character])
    
    # Execute effects
    _execute_personal_event_effects(event, character)
    
    return True


def fire_world_event():
    """
    Fire a random world event.
    
    Returns:
        tuple: (event_key, event_dict) or (None, None)
    """
    event_key, event = select_weighted_event(WORLD_EVENTS)
    
    if not event:
        return None, None
    
    message = event.get("message", "Something happens in the world.")
    scope = event.get("scope", "all")
    
    # Get target rooms based on scope
    from evennia.objects.models import ObjectDB
    
    if scope == "all":
        rooms = ObjectDB.objects.filter(db_typeclass_path__contains="Room")
    elif scope == "outdoors":
        rooms = ObjectDB.objects.filter(db_tags__db_key="outdoor")
    elif scope.startswith("tags:"):
        tag = scope.split(":")[1]
        rooms = ObjectDB.objects.filter(db_tags__db_key=tag)
    else:
        rooms = []
    
    # Send message to all matching rooms
    for room_obj in rooms:
        room = room_obj
        if hasattr(room, 'msg_contents'):
            room.msg_contents(f"|y{message}|n")
    
    # Execute global effects
    _execute_world_event_effects(event)
    
    return event_key, event


# =============================================================================
# Effect Execution
# =============================================================================

def _execute_room_event_effects(event, room):
    """Execute effects for a room event."""
    effects = event.get("effects", [])
    
    for effect in effects:
        effect_type = effect.get("type")
        
        if effect_type == "spawn_object":
            from evennia import create_object
            key = effect.get("key", "object")
            typeclass = effect.get("typeclass", "typeclasses.objects.Object")
            obj = create_object(typeclass, key=key, location=room)
            if effect.get("value"):
                obj.db.value = effect["value"]
        
        elif effect_type == "spawn_temporary":
            from evennia import create_object
            key = effect.get("key", "object")
            typeclass = effect.get("typeclass", "typeclasses.objects.Object")
            duration = effect.get("duration", 60)
            obj = create_object(typeclass, key=key, location=room)
            obj.db.despawn_at = time.time() + duration
            # STUB: Create despawn script


def _execute_personal_event_effects(event, character):
    """Execute effects for a personal event."""
    effects = event.get("effects", [])
    
    for effect in effects:
        effect_type = effect.get("type")
        
        if effect_type == "give_currency":
            from world.currency import receive
            amount = effect.get("amount", 1)
            receive(character, amount, reason="random find", silent=False)
        
        elif effect_type == "take_currency":
            from world.currency import balance, pay
            amount = effect.get("amount", 1)
            min_balance = effect.get("min_balance", 0)
            
            if balance(character) >= min_balance:
                pay(character, min(amount, balance(character)), 
                    reason="pickpocketed", silent=True)
        
        elif effect_type == "apply_effect":
            from world.effects import apply_effect
            apply_effect(
                character,
                effect.get("effect_key"),
                category=effect.get("category", "status"),
                duration=effect.get("duration")
            )


def _execute_world_event_effects(event):
    """Execute effects for a world event."""
    effects = event.get("effects", [])
    
    for effect in effects:
        effect_type = effect.get("type")
        
        if effect_type == "temporary_time":
            # STUB: Temporarily override world time
            pass


# =============================================================================
# Event Registration
# =============================================================================

def register_ambient_events(room, event_keys):
    """
    Register which ambient events can fire in a room.
    
    Args:
        room: Room object
        event_keys: List of event keys from AMBIENT_EVENTS
    """
    room.db.ambient_events = event_keys


def register_room_events(room, event_keys):
    """
    Register which room events can fire in a room.
    
    Args:
        room: Room object  
        event_keys: List of event keys from ROOM_EVENTS
    """
    room.db.room_events = event_keys


def add_custom_ambient_event(room, key, messages, conditions=None, weight=5):
    """
    Add a custom ambient event to a room.
    
    Args:
        room: Room object
        key: Unique event key
        messages: List of possible messages
        conditions: Condition dict
        weight: Event weight
    """
    if room.db.custom_ambient_events is None:
        room.db.custom_ambient_events = {}
    
    room.db.custom_ambient_events[key] = {
        "messages": messages,
        "conditions": conditions or {},
        "weight": weight,
    }


# =============================================================================
# Tick Function (called by global script)
# =============================================================================

def tick_random_events(ambient_chance=0.1, room_event_chance=0.02, 
                       personal_chance=0.05, world_chance=0.001):
    """
    Process random events for the tick.
    Called periodically by a global script.
    
    Args:
        ambient_chance: Probability per room of ambient event
        room_event_chance: Probability per room of room event
        personal_chance: Probability per character of personal event
        world_chance: Probability of world event
    
    Returns:
        dict: Summary of events fired
    """
    from evennia.objects.models import ObjectDB
    
    summary = {
        "ambient": 0,
        "room": 0,
        "personal": 0,
        "world": 0,
    }
    
    # Get all rooms with characters in them
    occupied_rooms = set()
    characters = ObjectDB.objects.filter(db_typeclass_path__contains="Character")
    
    for char_obj in characters:
        if hasattr(char_obj, 'location') and char_obj.location:
            occupied_rooms.add(char_obj.location)
    
    # Process ambient events for occupied rooms
    for room in occupied_rooms:
        if random.random() < ambient_chance:
            if fire_ambient_event(room):
                summary["ambient"] += 1
        
        if random.random() < room_event_chance:
            if fire_room_event(room):
                summary["room"] += 1
    
    # Process personal events for characters
    for char_obj in characters:
        # Skip NPCs (check for account)
        if hasattr(char_obj, 'account') and char_obj.account:
            if random.random() < personal_chance:
                if fire_personal_event(char_obj):
                    summary["personal"] += 1
    
    # Process world events
    if random.random() < world_chance:
        event_key, event = fire_world_event()
        if event_key:
            summary["world"] += 1
    
    return summary


# =============================================================================
# Script for Periodic Event Ticks
# =============================================================================

"""
STUB: RandomEventTickScript

This script should be created to call tick_random_events periodically.
Add to typeclasses/scripts.py or world/scripts.py:

class RandomEventTickScript(DefaultScript):
    '''
    Global script that fires random events periodically.
    '''
    
    def at_script_creation(self):
        self.key = "random_event_ticker"
        self.desc = "Fires random ambient and world events"
        self.interval = 60  # Every 60 seconds
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        from world.random_events import tick_random_events
        tick_random_events()

# Start the script (run once):
# @py from typeclasses.scripts import RandomEventTickScript; RandomEventTickScript.create()
"""
