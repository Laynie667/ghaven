"""
Trigger System for Gilderhaven
===============================

Base framework for triggering events based on conditions.
Triggers can be attached to rooms, objects, or run globally.

Trigger Types:
- Room triggers: fire on enter/exit/stay
- Object triggers: fire on get/drop/use/look/touch
- Conditional triggers: fire when conditions met
- Timed triggers: fire on schedule
- Random triggers: fire with probability

Usage:
    from world.triggers import RoomTrigger, ObjectTrigger, ConditionalTrigger
    
    # Room that triggers on entry
    class HauntedRoom(Room):
        def at_object_receive(self, obj, source):
            super().at_object_receive(obj, source)
            check_room_triggers(self, obj, "enter")

    # Object with pickup trigger
    class CursedItem(Object):
        def at_get(self, getter):
            super().at_get(getter)
            check_object_triggers(self, getter, "get")
"""

import random
import time
from evennia.utils import logger

# =============================================================================
# Trigger Definitions Storage
# =============================================================================

# Triggers are stored on objects in .db.triggers as a list of dicts
# Each trigger dict has:
# {
#     "id": "unique_trigger_id",
#     "type": "enter" | "exit" | "get" | "use" | etc.,
#     "conditions": [...],  # List of condition dicts
#     "effects": [...],     # List of effect dicts
#     "once": False,        # If True, trigger removes itself after firing
#     "cooldown": 0,        # Seconds before can fire again
#     "probability": 1.0,   # Chance to fire (0.0-1.0)
#     "last_fired": None,   # Timestamp of last fire
#     "enabled": True,
# }


# =============================================================================
# Trigger Types
# =============================================================================

ROOM_TRIGGER_TYPES = [
    "enter",      # Character enters room
    "exit",       # Character exits room
    "look",       # Character looks at room
    "stay",       # Character stays in room (timed)
    "time",       # Specific time of day
    "weather",    # Weather condition met
    "night",      # Night falls in room
    "dawn",       # Dawn breaks in room
]

OBJECT_TRIGGER_TYPES = [
    "get",        # Object picked up
    "drop",       # Object dropped
    "give",       # Object given to someone
    "use",        # Object used
    "look",       # Object looked at
    "touch",      # Object touched/interacted with
    "equip",      # Object equipped
    "unequip",    # Object unequipped
    "break",      # Object breaks/destroyed
]

GLOBAL_TRIGGER_TYPES = [
    "time",       # Global time changes
    "weather",    # Global weather changes
    "tick",       # Periodic tick
]


# =============================================================================
# Condition Types
# =============================================================================

def check_condition(condition, actor, target=None, context=None):
    """
    Check if a condition is met.
    
    Args:
        condition: dict with "type" and type-specific params
        actor: The character/object triggering
        target: The room/object being triggered
        context: Additional context dict
    
    Returns:
        bool: True if condition met
    """
    cond_type = condition.get("type")
    context = context or {}
    
    # Time conditions
    if cond_type == "time_is":
        from world.world_state import get_time_period
        return get_time_period() == condition.get("value")
    
    if cond_type == "time_between":
        from world.world_state import get_time_period
        period = get_time_period()
        valid = condition.get("values", [])
        return period in valid
    
    # Weather conditions
    if cond_type == "weather_is":
        from world.world_state import get_weather
        return get_weather() == condition.get("value")
    
    if cond_type == "weather_in":
        from world.world_state import get_weather
        weather = get_weather()
        valid = condition.get("values", [])
        return weather in valid
    
    # Season conditions
    if cond_type == "season_is":
        from world.world_state import get_season
        return get_season() == condition.get("value")
    
    # Actor has item
    if cond_type == "has_item":
        item_key = condition.get("item")
        if hasattr(actor, 'contents'):
            return any(obj.key == item_key for obj in actor.contents)
        return False
    
    # Actor has effect
    if cond_type == "has_effect":
        from world.effects import has_effect
        return has_effect(actor, condition.get("effect"))
    
    # Actor lacks effect
    if cond_type == "lacks_effect":
        from world.effects import has_effect
        return not has_effect(actor, condition.get("effect"))
    
    # Actor has tag
    if cond_type == "has_tag":
        tag = condition.get("tag")
        category = condition.get("category")
        return actor.tags.has(tag, category=category)
    
    # Currency check
    if cond_type == "currency_gte":
        from world.currency import balance
        return balance(actor) >= condition.get("amount", 0)
    
    if cond_type == "currency_lt":
        from world.currency import balance
        return balance(actor) < condition.get("amount", 0)
    
    # Random chance
    if cond_type == "random":
        chance = condition.get("chance", 0.5)
        return random.random() < chance
    
    # Attribute check
    if cond_type == "attr_equals":
        attr = condition.get("attr")
        value = condition.get("value")
        return getattr(actor.db, attr, None) == value
    
    if cond_type == "attr_gte":
        attr = condition.get("attr")
        value = condition.get("value", 0)
        return getattr(actor.db, attr, 0) >= value
    
    # Is player (not NPC)
    if cond_type == "is_player":
        return hasattr(actor, 'account') and actor.account is not None
    
    # Is specific character
    if cond_type == "is_character":
        char_key = condition.get("key")
        return actor.key.lower() == char_key.lower()
    
    # First time entering (doesn't have visited flag)
    if cond_type == "first_visit":
        if target:
            visited_key = f"visited_{target.id}"
            return not actor.tags.has(visited_key, category="visited")
        return False
    
    # Always true/false (for testing)
    if cond_type == "always":
        return True
    if cond_type == "never":
        return False
    
    # Unknown condition type - log warning and pass
    logger.log_warn(f"Unknown trigger condition type: {cond_type}")
    return True


def check_all_conditions(conditions, actor, target=None, context=None):
    """
    Check if ALL conditions in a list are met.
    
    Args:
        conditions: List of condition dicts
        actor: Triggering character
        target: Triggered object/room
        context: Additional context
    
    Returns:
        bool: True if all conditions pass
    """
    if not conditions:
        return True
    
    for condition in conditions:
        if not check_condition(condition, actor, target, context):
            return False
    return True


# =============================================================================
# Effect Types
# =============================================================================

def execute_effect(effect, actor, target=None, context=None):
    """
    Execute a single trigger effect.
    
    Args:
        effect: dict with "type" and type-specific params
        actor: Character receiving the effect
        target: Object/room that triggered
        context: Additional context
    
    Returns:
        bool: True if effect executed successfully
    """
    effect_type = effect.get("type")
    context = context or {}
    
    try:
        # Message effects
        if effect_type == "message":
            msg = effect.get("text", "")
            if hasattr(actor, 'msg'):
                actor.msg(msg)
            return True
        
        if effect_type == "message_room":
            msg = effect.get("text", "")
            exclude = effect.get("exclude_actor", True)
            if target and hasattr(target, 'msg_contents'):
                exclude_list = [actor] if exclude else []
                target.msg_contents(msg, exclude=exclude_list)
            return True
        
        if effect_type == "message_all":
            # Message both actor and room
            actor_msg = effect.get("actor_text", effect.get("text", ""))
            room_msg = effect.get("room_text", "")
            if hasattr(actor, 'msg'):
                actor.msg(actor_msg)
            if room_msg and actor.location:
                actor.location.msg_contents(room_msg, exclude=[actor])
            return True
        
        # Apply effect/status
        if effect_type == "apply_effect":
            from world.effects import apply_effect
            return apply_effect(
                actor,
                effect.get("effect_key"),
                category=effect.get("category", "status"),
                duration=effect.get("duration"),
                data=effect.get("data")
            )
        
        # Remove effect
        if effect_type == "remove_effect":
            from world.effects import remove_effect
            return remove_effect(actor, effect.get("effect_key"))
        
        # Apply transformation
        if effect_type == "transform":
            from world.effects import apply_transformation
            return apply_transformation(
                actor,
                effect.get("transform_key"),
                species=effect.get("species"),
                features=effect.get("features"),
                duration=effect.get("duration")
            )
        
        # Currency effects
        if effect_type == "give_currency":
            from world.currency import receive
            receive(actor, effect.get("amount", 0), reason=effect.get("reason"))
            return True
        
        if effect_type == "take_currency":
            from world.currency import pay
            return pay(actor, effect.get("amount", 0), reason=effect.get("reason"),
                      force=effect.get("force", False))
        
        # Teleport
        if effect_type == "teleport":
            dest = effect.get("destination")
            if isinstance(dest, str):
                # Look up by key or #dbref
                from evennia.utils.search import search_object
                results = search_object(dest)
                if results:
                    dest = results[0]
                else:
                    logger.log_err(f"Teleport destination not found: {dest}")
                    return False
            
            if dest:
                actor.move_to(dest, quiet=effect.get("quiet", False))
                return True
            return False
        
        # Give item
        if effect_type == "give_item":
            from evennia import create_object
            item_typeclass = effect.get("typeclass", "typeclasses.objects.Object")
            item_key = effect.get("key", "item")
            item = create_object(item_typeclass, key=item_key, location=actor)
            
            # Apply any attributes
            for attr, value in effect.get("attributes", {}).items():
                setattr(item.db, attr, value)
            
            if hasattr(actor, 'msg'):
                actor.msg(f"|gYou receive: {item.key}|n")
            return True
        
        # Take/destroy item from actor
        if effect_type == "take_item":
            item_key = effect.get("key")
            if hasattr(actor, 'contents'):
                for obj in actor.contents:
                    if obj.key.lower() == item_key.lower():
                        if hasattr(actor, 'msg'):
                            actor.msg(f"|rYou lose: {obj.key}|n")
                        obj.delete()
                        return True
            return False
        
        # Set attribute
        if effect_type == "set_attr":
            attr = effect.get("attr")
            value = effect.get("value")
            setattr(actor.db, attr, value)
            return True
        
        # Add tag
        if effect_type == "add_tag":
            tag = effect.get("tag")
            category = effect.get("category")
            actor.tags.add(tag, category=category)
            return True
        
        # Remove tag
        if effect_type == "remove_tag":
            tag = effect.get("tag")
            category = effect.get("category")
            actor.tags.remove(tag, category=category)
            return True
        
        # Mark as visited (for first_visit condition)
        if effect_type == "mark_visited":
            if target:
                actor.tags.add(f"visited_{target.id}", category="visited")
            return True
        
        # Spawn object in room
        if effect_type == "spawn_object":
            from evennia import create_object
            typeclass = effect.get("typeclass", "typeclasses.objects.Object")
            key = effect.get("key", "object")
            location = target if target else actor.location
            
            obj = create_object(typeclass, key=key, location=location)
            for attr, value in effect.get("attributes", {}).items():
                setattr(obj.db, attr, value)
            return True
        
        # Trigger another trigger by ID
        if effect_type == "chain_trigger":
            trigger_id = effect.get("trigger_id")
            if target:
                fire_trigger_by_id(target, trigger_id, actor, context)
            return True
        
        # Run arbitrary Python (DANGEROUS - admin only)
        if effect_type == "exec":
            # STUB: Implement with heavy restrictions
            # code = effect.get("code")
            # exec(code, {"actor": actor, "target": target, "context": context})
            logger.log_warn("exec effect type disabled for security")
            return False
        
        # Start a scene (branching narrative)
        if effect_type == "start_scene":
            from world.scenes import trigger_scene
            scene_id = effect.get("scene")
            if scene_id:
                return trigger_scene(scene_id, actor)
            return False
        
        # Unknown effect type
        logger.log_warn(f"Unknown trigger effect type: {effect_type}")
        return False
        
    except Exception as e:
        logger.log_err(f"Error executing trigger effect {effect_type}: {e}")
        return False


def execute_effects(effects, actor, target=None, context=None):
    """
    Execute all effects in a list.
    
    Args:
        effects: List of effect dicts
        actor: Character receiving effects
        target: Triggering object/room
        context: Additional context
    
    Returns:
        int: Number of successfully executed effects
    """
    success_count = 0
    for effect in effects:
        if execute_effect(effect, actor, target, context):
            success_count += 1
    return success_count


# =============================================================================
# Trigger Checking & Firing
# =============================================================================

def get_triggers(target, trigger_type=None):
    """
    Get all triggers on a target, optionally filtered by type.
    
    Args:
        target: Object/room with triggers
        trigger_type: Optional type filter
    
    Returns:
        list: Trigger dicts
    """
    triggers = target.db.triggers or []
    
    if trigger_type:
        triggers = [t for t in triggers if t.get("type") == trigger_type]
    
    return [t for t in triggers if t.get("enabled", True)]


def check_trigger(trigger, actor, target, context=None):
    """
    Check if a trigger should fire.
    
    Args:
        trigger: Trigger dict
        actor: Triggering character
        target: Object/room with trigger
        context: Additional context
    
    Returns:
        bool: True if trigger should fire
    """
    # Check if enabled
    if not trigger.get("enabled", True):
        return False
    
    # Check cooldown
    cooldown = trigger.get("cooldown", 0)
    if cooldown > 0:
        last_fired = trigger.get("last_fired")
        if last_fired and (time.time() - last_fired) < cooldown:
            return False
    
    # Check probability
    probability = trigger.get("probability", 1.0)
    if probability < 1.0 and random.random() > probability:
        return False
    
    # Check conditions
    conditions = trigger.get("conditions", [])
    if not check_all_conditions(conditions, actor, target, context):
        return False
    
    return True


def fire_trigger(trigger, actor, target, context=None):
    """
    Fire a trigger, executing its effects.
    
    Args:
        trigger: Trigger dict
        actor: Character receiving effects
        target: Object/room with trigger
        context: Additional context
    
    Returns:
        bool: True if trigger fired
    """
    effects = trigger.get("effects", [])
    execute_effects(effects, actor, target, context)
    
    # Update last_fired
    trigger["last_fired"] = time.time()
    
    # Remove if one-shot
    if trigger.get("once", False):
        triggers = target.db.triggers or []
        trigger_id = trigger.get("id")
        target.db.triggers = [t for t in triggers if t.get("id") != trigger_id]
    
    return True


def check_and_fire_triggers(target, trigger_type, actor, context=None):
    """
    Check and fire all triggers of a type on a target.
    
    Args:
        target: Object/room with triggers
        trigger_type: Type of trigger to check
        actor: Triggering character
        context: Additional context
    
    Returns:
        int: Number of triggers fired
    """
    triggers = get_triggers(target, trigger_type)
    fired_count = 0
    
    for trigger in triggers:
        if check_trigger(trigger, actor, target, context):
            if fire_trigger(trigger, actor, target, context):
                fired_count += 1
    
    return fired_count


def fire_trigger_by_id(target, trigger_id, actor, context=None):
    """Fire a specific trigger by ID."""
    triggers = target.db.triggers or []
    for trigger in triggers:
        if trigger.get("id") == trigger_id:
            if check_trigger(trigger, actor, target, context):
                return fire_trigger(trigger, actor, target, context)
    return False


# =============================================================================
# Convenience Functions for Rooms/Objects
# =============================================================================

def check_room_triggers(room, character, trigger_type):
    """
    Check triggers when something happens in a room.
    Call from room hooks like at_object_receive, at_object_leave.
    
    Args:
        room: The room
        character: Character triggering
        trigger_type: "enter", "exit", "look", etc.
    """
    return check_and_fire_triggers(room, trigger_type, character)


def check_object_triggers(obj, character, trigger_type):
    """
    Check triggers when something happens to an object.
    Call from object hooks like at_get, at_drop, etc.
    
    Args:
        obj: The object
        character: Character triggering
        trigger_type: "get", "drop", "use", etc.
    """
    return check_and_fire_triggers(obj, trigger_type, character)


# =============================================================================
# Trigger Management
# =============================================================================

def add_trigger(target, trigger_type, effects, conditions=None, 
                trigger_id=None, once=False, cooldown=0, probability=1.0):
    """
    Add a trigger to an object/room.
    
    Args:
        target: Object/room to add trigger to
        trigger_type: Type of trigger
        effects: List of effect dicts
        conditions: List of condition dicts (optional)
        trigger_id: Unique ID (auto-generated if not provided)
        once: If True, trigger only fires once
        cooldown: Seconds between firings
        probability: Chance to fire (0.0-1.0)
    
    Returns:
        str: Trigger ID
    """
    if target.db.triggers is None:
        target.db.triggers = []
    
    if trigger_id is None:
        trigger_id = f"{trigger_type}_{int(time.time())}_{random.randint(1000,9999)}"
    
    trigger = {
        "id": trigger_id,
        "type": trigger_type,
        "conditions": conditions or [],
        "effects": effects,
        "once": once,
        "cooldown": cooldown,
        "probability": probability,
        "enabled": True,
        "last_fired": None,
    }
    
    target.db.triggers.append(trigger)
    return trigger_id


def remove_trigger(target, trigger_id):
    """Remove a trigger by ID."""
    if target.db.triggers:
        target.db.triggers = [t for t in target.db.triggers 
                             if t.get("id") != trigger_id]
        return True
    return False


def clear_triggers(target, trigger_type=None):
    """Remove all triggers, optionally by type."""
    if not target.db.triggers:
        return
    
    if trigger_type:
        target.db.triggers = [t for t in target.db.triggers 
                             if t.get("type") != trigger_type]
    else:
        target.db.triggers = []


def enable_trigger(target, trigger_id, enabled=True):
    """Enable or disable a trigger."""
    if target.db.triggers:
        for trigger in target.db.triggers:
            if trigger.get("id") == trigger_id:
                trigger["enabled"] = enabled
                return True
    return False


# =============================================================================
# Predefined Trigger Templates
# =============================================================================

def add_entry_message_trigger(room, message, conditions=None, once=False):
    """Add a simple message-on-entry trigger."""
    return add_trigger(
        room, "enter",
        effects=[{"type": "message", "text": message}],
        conditions=conditions,
        once=once
    )


def add_first_visit_trigger(room, message, mark_visited=True):
    """Add a trigger that fires only on first visit."""
    effects = [{"type": "message", "text": message}]
    if mark_visited:
        effects.append({"type": "mark_visited"})
    
    return add_trigger(
        room, "enter",
        effects=effects,
        conditions=[{"type": "first_visit"}],
        once=False  # Fires once per player, not once ever
    )


def add_pickup_curse_trigger(obj, effect_key, message=None, duration=None):
    """Add a curse trigger when object is picked up."""
    effects = [
        {"type": "apply_effect", "effect_key": effect_key, 
         "category": "curse", "duration": duration}
    ]
    if message:
        effects.insert(0, {"type": "message", "text": message})
    
    return add_trigger(obj, "get", effects=effects)


def add_trap_trigger(target, trigger_type, effect_key, message, 
                    probability=1.0, once=True):
    """Add a trap that applies an effect."""
    return add_trigger(
        target, trigger_type,
        effects=[
            {"type": "message", "text": message},
            {"type": "apply_effect", "effect_key": effect_key, "category": "debuff"}
        ],
        probability=probability,
        once=once
    )


def add_time_triggered_message(room, time_period, message):
    """Add message that shows at specific time of day."""
    return add_trigger(
        room, "enter",
        effects=[{"type": "message", "text": message}],
        conditions=[{"type": "time_is", "value": time_period}]
    )


def add_weather_triggered_effect(room, weather, effect_key, message=None):
    """Add effect triggered by weather condition."""
    effects = [{"type": "apply_effect", "effect_key": effect_key, 
               "category": "environmental"}]
    if message:
        effects.insert(0, {"type": "message", "text": message})
    
    return add_trigger(
        room, "enter",
        effects=effects,
        conditions=[{"type": "weather_is", "value": weather}]
    )
