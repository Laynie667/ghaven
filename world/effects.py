"""
Effects & Status System for Gilderhaven
========================================

Manages effects, statuses, conditions, transformations, and flags on any object.
Does NOT require Character.py modifications - effects are stored as tags + attributes.

Effects have:
- A key (unique identifier)
- A category (for grouping: "curse", "transformation", "buff", etc.)
- Optional duration (permanent if not set)
- Optional stacking behavior
- Optional data payload
- Optional callbacks on apply/remove/tick

Usage:
    from world.effects import apply_effect, remove_effect, has_effect, get_effects
    
    # Apply a timed effect
    apply_effect(character, "poisoned", category="debuff", duration=300)
    
    # Apply permanent effect with data
    apply_effect(character, "transformed_mare", category="transformation", 
                 data={"original_form": "human", "species": "fae_horse"})
    
    # Check for effect
    if has_effect(character, "in_heat"):
        ...
    
    # Remove effect
    remove_effect(character, "cursed")
    
    # Get all effects of a category
    transformations = get_effects(character, category="transformation")
"""

import time
from evennia.utils import logger

# =============================================================================
# Effect Categories - define your effect types here
# =============================================================================

EFFECT_CATEGORIES = {
    "buff": "Positive temporary effects",
    "debuff": "Negative temporary effects", 
    "curse": "Magical afflictions requiring removal",
    "transformation": "Physical form changes",
    "status": "General status flags",
    "breeding": "Breeding-related states",
    "museum": "Museum/Curator imposed effects",
    "environmental": "Effects from location/weather",
    "quest": "Quest-related flags",
}

# Effects that prevent certain actions
BLOCKING_EFFECTS = {
    "paralyzed": ["move", "attack", "use"],
    "silenced": ["speak", "cast"],
    "bound": ["move", "attack"],
    "displayed": ["move", "leave"],  # Can't leave exhibit
    "in_breeding": ["move", "leave"],
}

# Effects that modify stats (STUB - implement when stats exist)
STAT_MODIFIERS = {
    # "effect_key": {"stat": modifier_value}
    "weakened": {"strength": -5},
    "empowered": {"strength": 5},
    "fertile": {"fertility": 10},
    "in_heat": {"arousal": 5, "fertility": 3},
}


# =============================================================================
# Core Effect Functions
# =============================================================================

def apply_effect(target, effect_key, category="status", duration=None, 
                 data=None, stacks=False, max_stacks=1, silent=False,
                 on_apply=None, on_remove=None, on_tick=None):
    """
    Apply an effect to a target.
    
    Args:
        target: Any object with .tags and .db (Character, NPC, Object, Room)
        effect_key: str, unique identifier for this effect
        category: str, effect category (see EFFECT_CATEGORIES)
        duration: int/float, seconds until expiry (None = permanent)
        data: dict, arbitrary data stored with effect
        stacks: bool, whether multiple applications stack
        max_stacks: int, maximum stack count if stacking
        silent: bool, suppress application message
        on_apply: callable, called when effect applied (receives target, effect_key, data)
        on_remove: callable, called when effect removed
        on_tick: callable, called each tick while active (for DoT, etc.)
    
    Returns:
        bool: True if effect was applied (False if blocked/at max stacks)
    """
    # Check if already has effect
    if has_effect(target, effect_key):
        if not stacks:
            # Refresh duration if not stacking
            if duration:
                _set_effect_expiry(target, effect_key, duration)
            return True
        else:
            # Handle stacking
            current_stacks = get_stack_count(target, effect_key)
            if current_stacks >= max_stacks:
                return False
            # Increment stack count
            _set_stack_count(target, effect_key, current_stacks + 1)
            return True
    
    # Apply the effect tag
    target.tags.add(effect_key, category=f"effect_{category}")
    
    # Store effect data
    effect_data = {
        "applied_at": time.time(),
        "category": category,
        "duration": duration,
        "stacks": 1 if stacks else None,
        "max_stacks": max_stacks if stacks else None,
        "data": data or {},
    }
    
    # Store callbacks if provided (as references, not serialized)
    if on_apply or on_remove or on_tick:
        # Store callback info - actual callbacks handled by effect definitions
        effect_data["has_callbacks"] = True
    
    _set_effect_data(target, effect_key, effect_data)
    
    # Set expiry if duration specified
    if duration:
        _set_effect_expiry(target, effect_key, duration)
        # Start expiry script
        _start_expiry_timer(target, effect_key, duration)
    
    # Call on_apply callback
    if on_apply:
        try:
            on_apply(target, effect_key, data)
        except Exception as e:
            logger.log_err(f"Effect on_apply callback error: {e}")
    
    # Message target
    if not silent and hasattr(target, 'msg'):
        msg = _get_apply_message(effect_key, category)
        if msg:
            target.msg(msg)
    
    return True


def remove_effect(target, effect_key, silent=False, expired=False):
    """
    Remove an effect from a target.
    
    Args:
        target: Object with the effect
        effect_key: str, effect to remove
        silent: bool, suppress removal message
        expired: bool, True if removed due to expiry (for messaging)
    
    Returns:
        bool: True if effect was removed, False if not present
    """
    if not has_effect(target, effect_key):
        return False
    
    # Get effect data before removal
    effect_data = get_effect_data(target, effect_key)
    category = effect_data.get("category", "status") if effect_data else "status"
    
    # Remove the tag
    target.tags.remove(effect_key, category=f"effect_{category}")
    
    # Clear stored data
    _clear_effect_data(target, effect_key)
    
    # Cancel any expiry timer
    _cancel_expiry_timer(target, effect_key)
    
    # Message target
    if not silent and hasattr(target, 'msg'):
        msg = _get_remove_message(effect_key, category, expired)
        if msg:
            target.msg(msg)
    
    return True


def has_effect(target, effect_key, category=None):
    """
    Check if target has an effect.
    
    Args:
        target: Object to check
        effect_key: str, effect to check for
        category: str, optional category filter
    
    Returns:
        bool: True if effect is present
    """
    if category:
        return target.tags.has(effect_key, category=f"effect_{category}")
    
    # Check all effect categories
    for cat in EFFECT_CATEGORIES:
        if target.tags.has(effect_key, category=f"effect_{cat}"):
            return True
    return False


def get_effects(target, category=None):
    """
    Get all effects on a target.
    
    Args:
        target: Object to check
        category: str, optional category filter
    
    Returns:
        list: List of effect keys
    """
    effects = []
    
    if category:
        categories = [category]
    else:
        categories = EFFECT_CATEGORIES.keys()
    
    for cat in categories:
        tags = target.tags.get(category=f"effect_{cat}", return_list=True)
        if tags:
            effects.extend(tags)
    
    return effects


def get_effect_data(target, effect_key):
    """
    Get stored data for an effect.
    
    Args:
        target: Object with effect
        effect_key: str, effect to get data for
    
    Returns:
        dict: Effect data or None
    """
    all_effects = target.db.effect_data or {}
    return all_effects.get(effect_key)


def get_stack_count(target, effect_key):
    """Get current stack count for a stacking effect."""
    data = get_effect_data(target, effect_key)
    if data:
        return data.get("stacks", 1)
    return 0


def get_remaining_duration(target, effect_key):
    """
    Get remaining duration for a timed effect.
    
    Returns:
        float: Seconds remaining, or None if permanent
    """
    data = get_effect_data(target, effect_key)
    if not data or not data.get("duration"):
        return None
    
    applied_at = data.get("applied_at", time.time())
    duration = data.get("duration")
    elapsed = time.time() - applied_at
    remaining = duration - elapsed
    
    return max(0, remaining)


def clear_all_effects(target, category=None, silent=False):
    """
    Remove all effects from a target.
    
    Args:
        target: Object to clear
        category: str, optional - only clear this category
        silent: bool, suppress messages
    
    Returns:
        int: Number of effects removed
    """
    effects = get_effects(target, category)
    count = 0
    
    for effect_key in effects:
        if remove_effect(target, effect_key, silent=silent):
            count += 1
    
    return count


# =============================================================================
# Action Blocking
# =============================================================================

def can_perform(target, action):
    """
    Check if target can perform an action based on effects.
    
    Args:
        target: Object to check
        action: str, action to check ("move", "attack", "speak", etc.)
    
    Returns:
        tuple: (bool can_perform, str blocking_effect or None)
    """
    for effect_key, blocked_actions in BLOCKING_EFFECTS.items():
        if has_effect(target, effect_key):
            if action in blocked_actions:
                return False, effect_key
    return True, None


def get_blocking_effects(target):
    """Get all effects currently blocking actions on target."""
    blocking = {}
    for effect_key, blocked_actions in BLOCKING_EFFECTS.items():
        if has_effect(target, effect_key):
            blocking[effect_key] = blocked_actions
    return blocking


# =============================================================================
# Effect Queries
# =============================================================================

def is_transformed(target):
    """Check if target has any transformation effect."""
    return bool(get_effects(target, category="transformation"))


def is_cursed(target):
    """Check if target has any curse effect."""
    return bool(get_effects(target, category="curse"))


def is_in_breeding(target):
    """Check if target is in a breeding situation."""
    return has_effect(target, "in_breeding") or has_effect(target, "breeding_program")


def is_displayed(target):
    """Check if target is on display (museum exhibit)."""
    return has_effect(target, "displayed") or has_effect(target, "living_exhibit")


# =============================================================================
# Transformation Helpers
# =============================================================================

def apply_transformation(target, transform_key, original_form=None, 
                        species=None, features=None, duration=None, **kwargs):
    """
    Apply a transformation effect with standard data structure.
    
    Args:
        target: Object to transform
        transform_key: str, unique transformation identifier
        original_form: str, what they were before (stored for reversal)
        species: str, what they're becoming
        features: dict, physical feature changes
        duration: int, seconds until auto-reversal (None = permanent until cured)
        **kwargs: Additional data to store
    
    Returns:
        bool: True if transformation applied
    """
    # Store original form if not already transformed
    if not is_transformed(target) and original_form is None:
        original_form = target.db.current_form or "default"
    
    data = {
        "original_form": original_form,
        "species": species,
        "features": features or {},
        **kwargs
    }
    
    return apply_effect(
        target, 
        transform_key, 
        category="transformation",
        duration=duration,
        data=data
    )


def get_transformation_data(target):
    """Get data about current transformation, if any."""
    transforms = get_effects(target, category="transformation")
    if transforms:
        # Return most recent transformation
        return get_effect_data(target, transforms[-1])
    return None


def revert_transformation(target, transform_key=None, silent=False):
    """
    Revert a transformation.
    
    Args:
        target: Transformed object
        transform_key: Specific transformation to revert (None = all)
        silent: Suppress messages
    
    Returns:
        bool: True if reverted
    """
    if transform_key:
        return remove_effect(target, transform_key, silent=silent)
    else:
        # Revert all transformations
        return clear_all_effects(target, category="transformation", silent=silent) > 0


# =============================================================================
# Internal Helpers
# =============================================================================

def _set_effect_data(target, effect_key, data):
    """Store effect data on target."""
    if target.db.effect_data is None:
        target.db.effect_data = {}
    target.db.effect_data[effect_key] = data


def _clear_effect_data(target, effect_key):
    """Remove stored effect data."""
    if target.db.effect_data:
        target.db.effect_data.pop(effect_key, None)


def _set_effect_expiry(target, effect_key, duration):
    """Set/update effect expiry time."""
    data = get_effect_data(target, effect_key)
    if data:
        data["applied_at"] = time.time()
        data["duration"] = duration
        _set_effect_data(target, effect_key, data)


def _set_stack_count(target, effect_key, count):
    """Update stack count for effect."""
    data = get_effect_data(target, effect_key)
    if data:
        data["stacks"] = count
        _set_effect_data(target, effect_key, data)


def _start_expiry_timer(target, effect_key, duration):
    """
    Start a timer script to auto-remove effect.
    
    STUB: This creates an Evennia Script for effect expiry.
    Implement EffectExpiryScript in scripts/effect_scripts.py
    """
    # STUB: Create expiry script
    # from typeclasses.scripts import EffectExpiryScript
    # EffectExpiryScript.create(target, effect_key, duration)
    pass


def _cancel_expiry_timer(target, effect_key):
    """
    Cancel an effect's expiry timer.
    
    STUB: Find and delete the expiry script.
    """
    # STUB: Find and cancel expiry script
    # scripts = target.scripts.get("effect_expiry_{effect_key}")
    # for script in scripts:
    #     script.delete()
    pass


def _get_apply_message(effect_key, category):
    """Get message to show when effect is applied."""
    # STUB: Pull from EFFECT_MESSAGES dict or effect definitions
    messages = {
        "poisoned": "|rYou feel poison coursing through your veins.|n",
        "in_heat": "|mA familiar warmth spreads through you...|n",
        "cursed": "|rYou feel a dark energy settle over you.|n",
        "transformed": "|yYour body begins to change...|n",
        "displayed": "|yYou are now on display.|n",
        "paralyzed": "|rYou can't move!|n",
    }
    return messages.get(effect_key)


def _get_remove_message(effect_key, category, expired):
    """Get message to show when effect is removed."""
    messages = {
        "poisoned": "|gThe poison fades from your system.|n",
        "in_heat": "|gThe heat subsides... for now.|n",
        "cursed": "|gThe curse lifts!|n",
        "paralyzed": "|gYou can move again.|n",
    }
    
    if expired:
        base = messages.get(effect_key, f"|gThe {effect_key} effect fades.|n")
    else:
        base = messages.get(effect_key, f"|gThe {effect_key} effect is removed.|n")
    
    return base


# =============================================================================
# Predefined Effects (convenience functions)
# =============================================================================

def poison(target, duration=300, damage_per_tick=5):
    """Apply poison effect."""
    return apply_effect(target, "poisoned", category="debuff", 
                       duration=duration, data={"damage": damage_per_tick})


def paralyze(target, duration=60):
    """Apply paralysis effect."""
    return apply_effect(target, "paralyzed", category="debuff", duration=duration)


def induce_heat(target, duration=None, intensity=1):
    """Apply heat/arousal effect."""
    return apply_effect(target, "in_heat", category="breeding",
                       duration=duration, data={"intensity": intensity})


def curse(target, curse_name, duration=None, cure_method=None, **data):
    """Apply a curse effect."""
    data["cure_method"] = cure_method
    return apply_effect(target, curse_name, category="curse",
                       duration=duration, data=data)


def mark_displayed(target, exhibit_name, location=None, duration=None):
    """Mark target as being on display."""
    return apply_effect(target, "displayed", category="museum",
                       duration=duration,
                       data={"exhibit": exhibit_name, "location": location})


def enter_breeding_program(target, program_id, partner=None, duration=None):
    """Mark target as in breeding program."""
    return apply_effect(target, "breeding_program", category="breeding",
                       duration=duration,
                       data={"program": program_id, "partner": partner})
