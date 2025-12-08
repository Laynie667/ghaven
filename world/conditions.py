"""
Condition System for Gilderhaven

Persistent character states that affect descriptions, abilities,
and interactions. Includes arousal, exhaustion, wounds, and
visible conditions that appear in shortcodes.

Separate from combat resources - these are RP/world states.
"""

from random import random, choice
from evennia.utils import delay

# =============================================================================
# AROUSAL SYSTEM
# =============================================================================

AROUSAL_LEVELS = {
    0: {
        "name": "calm",
        "display": "calm",
        "desc": "completely composed",
        "shortcode_hints": [],
    },
    1: {
        "name": "warm",
        "display": "slightly warm",
        "desc": "a hint of warmth in &their cheeks",
        "shortcode_hints": ["slight flush"],
    },
    2: {
        "name": "flushed",
        "display": "flushed",
        "desc": "visibly flushed, breathing a bit faster",
        "shortcode_hints": ["flushed cheeks", "quickened breath"],
    },
    3: {
        "name": "aroused",
        "display": "aroused",
        "desc": "clearly aroused, skin flushed and warm",
        "shortcode_hints": ["heated skin", "dilated pupils", "heavy breathing"],
    },
    4: {
        "name": "needy",
        "display": "very aroused",
        "desc": "visibly needy, squirming slightly",
        "shortcode_hints": ["trembling slightly", "biting lip", "restless movement"],
    },
    5: {
        "name": "desperate",
        "display": "desperately aroused",
        "desc": "desperately aroused, barely containing &themselves",
        "shortcode_hints": ["panting", "flushed all over", "trembling", "distracted"],
    },
    6: {
        "name": "overwhelmed",
        "display": "overwhelmed with need",
        "desc": "completely overwhelmed, on the edge of losing control",
        "shortcode_hints": ["glazed eyes", "constant trembling", "whimpering", "dripping"],
    },
}

MAX_AROUSAL = 6
AROUSAL_DECAY_RATE = 1  # Points per decay tick
AROUSAL_DECAY_INTERVAL = 300  # Seconds (5 minutes)

# What triggers arousal increases
AROUSAL_TRIGGERS = {
    "tease": 1,
    "grope": 1,
    "kiss": 1,
    "aphrodisiac_weak": 1,
    "aphrodisiac_medium": 2,
    "aphrodisiac_strong": 3,
    "scene_mild": 1,
    "scene_moderate": 2,
    "scene_intense": 3,
    "composure_damage": 1,  # Per 10 composure lost
    "denial": 1,  # Being denied increases need
    "edging": 2,
    "orgasm_denied": 2,
}

# =============================================================================
# EXHAUSTION SYSTEM
# =============================================================================

EXHAUSTION_LEVELS = {
    0: {
        "name": "rested",
        "display": "well-rested",
        "desc": "looking fresh and energetic",
        "shortcode_hints": [],
        "stamina_mult": 1.0,
        "action_penalty": 0,
    },
    1: {
        "name": "active",
        "display": "active",
        "desc": "showing signs of recent exertion",
        "shortcode_hints": ["light perspiration"],
        "stamina_mult": 1.0,
        "action_penalty": 0,
    },
    2: {
        "name": "winded",
        "display": "winded",
        "desc": "breathing heavier, a sheen of sweat",
        "shortcode_hints": ["sweating lightly", "breathing hard"],
        "stamina_mult": 0.9,
        "action_penalty": -5,
    },
    3: {
        "name": "tired",
        "display": "tired",
        "desc": "visibly tired, movements slower",
        "shortcode_hints": ["sweating", "sluggish movements", "heavy breathing"],
        "stamina_mult": 0.75,
        "action_penalty": -10,
    },
    4: {
        "name": "exhausted",
        "display": "exhausted",
        "desc": "exhausted, struggling to keep going",
        "shortcode_hints": ["drenched in sweat", "trembling from fatigue", "gasping"],
        "stamina_mult": 0.5,
        "action_penalty": -20,
    },
    5: {
        "name": "collapsed",
        "display": "collapsed",
        "desc": "barely able to stand, completely spent",
        "shortcode_hints": ["collapsed", "unable to continue", "utterly spent"],
        "stamina_mult": 0.25,
        "action_penalty": -40,
        "can_act": False,
    },
}

MAX_EXHAUSTION = 5
EXHAUSTION_RECOVERY_RATE = 1  # Points per recovery tick
EXHAUSTION_RECOVERY_INTERVAL = 180  # Seconds (3 minutes) when resting

# =============================================================================
# WOUND STATES
# =============================================================================

WOUND_LEVELS = {
    0: {
        "name": "healthy",
        "display": "healthy",
        "desc": "unmarked and healthy",
        "shortcode_hints": [],
    },
    1: {
        "name": "scratched",
        "display": "lightly scratched",
        "desc": "bearing a few minor scratches",
        "shortcode_hints": ["minor scratches"],
    },
    2: {
        "name": "bruised",
        "display": "bruised",
        "desc": "showing bruises and scrapes",
        "shortcode_hints": ["visible bruises", "scrapes"],
    },
    3: {
        "name": "wounded",
        "display": "wounded",
        "desc": "sporting visible wounds",
        "shortcode_hints": ["bleeding cuts", "painful bruises", "wincing"],
    },
    4: {
        "name": "badly_wounded",
        "display": "badly wounded",
        "desc": "badly wounded, blood staining &their skin",
        "shortcode_hints": ["blood-stained", "limping", "favoring injuries"],
    },
    5: {
        "name": "critical",
        "display": "critically wounded",
        "desc": "barely standing, grievously wounded",
        "shortcode_hints": ["blood-soaked", "pale", "shaking from pain"],
    },
}

MAX_WOUNDS = 5

# =============================================================================
# VISIBLE CONDITIONS
# =============================================================================
# Temporary or permanent visible states that show in descriptions

VISIBLE_CONDITIONS = {
    # Fluids
    "sweaty": {
        "name": "sweaty",
        "desc": "glistening with sweat",
        "category": "exertion",
        "duration": 600,  # 10 minutes
    },
    "cum_covered": {
        "name": "cum-covered",
        "desc": "splattered with cum",
        "category": "fluids",
        "duration": None,  # Until cleaned
        "requires_cleaning": True,
    },
    "cum_filled": {
        "name": "cum-filled",
        "desc": "filled and dripping",
        "category": "fluids",
        "duration": 1800,  # 30 minutes
        "internal": True,
    },
    "wet": {
        "name": "wet",
        "desc": "dripping wet",
        "category": "fluids",
        "duration": 600,
    },
    "slime_covered": {
        "name": "slime-covered",
        "desc": "coated in slippery slime",
        "category": "fluids",
        "duration": None,
        "requires_cleaning": True,
    },
    
    # States
    "disheveled": {
        "name": "disheveled",
        "desc": "clothes askew and hair mussed",
        "category": "appearance",
        "duration": None,
        "until_fixed": True,
    },
    "naked": {
        "name": "naked",
        "desc": "completely bare",
        "category": "clothing",
        "duration": None,
    },
    "bound": {
        "name": "bound",
        "desc": "wrists bound together",
        "category": "restraint",
        "duration": None,
    },
    "gagged": {
        "name": "gagged",
        "desc": "gagged and unable to speak clearly",
        "category": "restraint",
        "duration": None,
    },
    "blindfolded": {
        "name": "blindfolded",
        "desc": "blindfolded and sightless",
        "category": "restraint",
        "duration": None,
    },
    "collared": {
        "name": "collared",
        "desc": "wearing a collar",
        "category": "worn",
        "duration": None,
        "permanent": True,
    },
    "leashed": {
        "name": "leashed",
        "desc": "on a leash",
        "category": "restraint",
        "duration": None,
    },
    
    # Marks
    "freshly_spanked": {
        "name": "freshly spanked",
        "desc": "rear reddened from a recent spanking",
        "category": "marks",
        "duration": 1200,  # 20 minutes
    },
    "bite_marks": {
        "name": "bite-marked",
        "desc": "bearing fresh bite marks",
        "category": "marks",
        "duration": 3600,  # 1 hour
    },
    "love_bites": {
        "name": "marked with love bites",
        "desc": "neck and shoulders dotted with love bites",
        "category": "marks",
        "duration": 7200,  # 2 hours
    },
    "rope_marks": {
        "name": "rope-marked",
        "desc": "showing rope marks on &their skin",
        "category": "marks",
        "duration": 1800,
    },
    
    # Post-scene
    "freshly_used": {
        "name": "freshly used",
        "desc": "clearly freshly used",
        "category": "state",
        "duration": 900,  # 15 minutes
    },
    "bred": {
        "name": "bred",
        "desc": "recently and thoroughly bred",
        "category": "state",
        "duration": 1800,
    },
    "milked": {
        "name": "recently milked",
        "desc": "breasts tender from recent milking",
        "category": "state",
        "duration": 1200,
    },
    "drained": {
        "name": "drained",
        "desc": "drained and sensitive",
        "category": "state",
        "duration": 900,
    },
    
    # Special
    "glowing": {
        "name": "glowing",
        "desc": "with a faint magical glow",
        "category": "magic",
        "duration": 1800,
    },
    "in_heat": {
        "name": "in heat",
        "desc": "visibly in heat, pheromones thick in the air",
        "category": "state",
        "duration": None,  # Until resolves
    },
    "knotted": {
        "name": "knotted",
        "desc": "locked in place by a swollen knot",
        "category": "state",
        "duration": 300,  # 5 minutes
    },
}


# =============================================================================
# Helper Functions - Arousal
# =============================================================================

def get_arousal(character):
    """Get character's current arousal level (0-6)."""
    if not hasattr(character, "db"):
        return 0
    return character.db.arousal or 0


def set_arousal(character, level):
    """Set character's arousal level."""
    level = max(0, min(MAX_AROUSAL, level))
    character.db.arousal = level
    return level


def modify_arousal(character, amount):
    """Modify arousal by amount. Returns new level."""
    current = get_arousal(character)
    new_level = set_arousal(character, current + amount)
    
    # Announce significant changes
    if hasattr(character, "msg"):
        if amount > 0:
            if new_level >= 5 and current < 5:
                character.msg("|mYou feel desperately needy...|n")
            elif new_level >= 3 and current < 3:
                character.msg("|mArousal washes over you...|n")
            elif amount >= 2:
                character.msg("|mA wave of heat courses through you.|n")
        elif amount < 0:
            if new_level == 0 and current > 0:
                character.msg("|gYou feel calm and composed again.|n")
    
    return new_level


def get_arousal_data(character):
    """Get full arousal data for a character."""
    level = get_arousal(character)
    return AROUSAL_LEVELS.get(level, AROUSAL_LEVELS[0])


def get_arousal_display(character):
    """Get display string for arousal state."""
    data = get_arousal_data(character)
    return data.get("display", "calm")


def get_arousal_desc(character):
    """Get description text for arousal state."""
    data = get_arousal_data(character)
    desc = data.get("desc", "composed")
    
    # Process pronouns
    try:
        from world.body import process_shortcodes
        desc = process_shortcodes(character, desc)
    except ImportError:
        pass
    
    return desc


def trigger_arousal(character, trigger_key, intensity=1):
    """
    Apply arousal from a trigger event.
    
    Args:
        character: The affected character
        trigger_key: Key from AROUSAL_TRIGGERS
        intensity: Multiplier for effect
    """
    base_amount = AROUSAL_TRIGGERS.get(trigger_key, 1)
    amount = int(base_amount * intensity)
    
    if amount > 0:
        return modify_arousal(character, amount)
    return get_arousal(character)


def decay_arousal(character):
    """Decay arousal naturally over time."""
    current = get_arousal(character)
    if current > 0:
        # Decay slower at higher levels (harder to calm down)
        if current >= 5:
            decay = 0  # Doesn't decay at desperate levels without help
        elif current >= 3:
            decay = 1 if random() < 0.3 else 0  # 30% chance
        else:
            decay = AROUSAL_DECAY_RATE
        
        if decay > 0:
            return modify_arousal(character, -decay)
    return current


def relieve_arousal(character, amount=None):
    """
    Relieve arousal (orgasm or similar).
    
    If amount is None, relieves completely.
    Returns new arousal level.
    """
    if amount is None:
        return set_arousal(character, 0)
    else:
        return modify_arousal(character, -amount)


# =============================================================================
# Helper Functions - Exhaustion
# =============================================================================

def get_exhaustion(character):
    """Get character's exhaustion level (0-5)."""
    if not hasattr(character, "db"):
        return 0
    return character.db.exhaustion or 0


def set_exhaustion(character, level):
    """Set character's exhaustion level."""
    level = max(0, min(MAX_EXHAUSTION, level))
    character.db.exhaustion = level
    return level


def modify_exhaustion(character, amount):
    """Modify exhaustion by amount."""
    current = get_exhaustion(character)
    new_level = set_exhaustion(character, current + amount)
    
    if hasattr(character, "msg"):
        if amount > 0:
            if new_level >= 5 and current < 5:
                character.msg("|rYou collapse from exhaustion!|n")
            elif new_level >= 4 and current < 4:
                character.msg("|rYou're completely exhausted...|n")
            elif new_level >= 3 and current < 3:
                character.msg("|yYou're getting tired.|n")
        elif amount < 0:
            if new_level == 0 and current > 0:
                character.msg("|gYou feel fully rested.|n")
    
    return new_level


def get_exhaustion_data(character):
    """Get full exhaustion data."""
    level = get_exhaustion(character)
    return EXHAUSTION_LEVELS.get(level, EXHAUSTION_LEVELS[0])


def get_exhaustion_display(character):
    """Get display string for exhaustion."""
    data = get_exhaustion_data(character)
    return data.get("display", "rested")


def add_exertion(character, amount=1):
    """Add exhaustion from physical activity."""
    return modify_exhaustion(character, amount)


def rest(character, amount=1):
    """Recover exhaustion from resting."""
    return modify_exhaustion(character, -amount)


def full_rest(character):
    """Fully recover exhaustion."""
    return set_exhaustion(character, 0)


def can_act(character):
    """Check if character can take actions (not collapsed)."""
    data = get_exhaustion_data(character)
    return data.get("can_act", True)


def get_action_penalty(character):
    """Get penalty to actions from exhaustion."""
    data = get_exhaustion_data(character)
    return data.get("action_penalty", 0)


# =============================================================================
# Helper Functions - Wounds
# =============================================================================

def get_wounds(character):
    """Get wound level (0-5)."""
    if not hasattr(character, "db"):
        return 0
    return character.db.wounds or 0


def set_wounds(character, level):
    """Set wound level."""
    level = max(0, min(MAX_WOUNDS, level))
    character.db.wounds = level
    return level


def add_wound(character, amount=1):
    """Add wounds."""
    current = get_wounds(character)
    return set_wounds(character, current + amount)


def heal_wound(character, amount=1):
    """Heal wounds."""
    current = get_wounds(character)
    return set_wounds(character, current - amount)


def full_heal(character):
    """Fully heal wounds."""
    return set_wounds(character, 0)


def get_wound_data(character):
    """Get wound data."""
    level = get_wounds(character)
    return WOUND_LEVELS.get(level, WOUND_LEVELS[0])


def get_wound_display(character):
    """Get display string for wounds."""
    data = get_wound_data(character)
    return data.get("display", "healthy")


# =============================================================================
# Helper Functions - Visible Conditions
# =============================================================================

def get_conditions(character):
    """Get list of active conditions."""
    if not hasattr(character, "db"):
        return []
    return character.db.conditions or []


def has_condition(character, condition_key):
    """Check if character has a condition."""
    conditions = get_conditions(character)
    for cond in conditions:
        if cond.get("key") == condition_key:
            return True
    return False


def add_condition(character, condition_key, duration=None, source=None):
    """
    Add a condition to character.
    
    Args:
        condition_key: Key from VISIBLE_CONDITIONS
        duration: Override default duration (seconds, or None for permanent)
        source: What caused this condition
    """
    template = VISIBLE_CONDITIONS.get(condition_key)
    if not template:
        return False
    
    if not character.db.conditions:
        character.db.conditions = []
    
    # Check if already has this condition
    for cond in character.db.conditions:
        if cond.get("key") == condition_key:
            # Refresh duration
            if duration is not None:
                cond["expires_at"] = None  # Would use game time
            return True
    
    # Add new condition
    condition = {
        "key": condition_key,
        "name": template["name"],
        "source": source,
        "applied_at": None,  # Would use game time
    }
    
    # Handle duration
    use_duration = duration if duration is not None else template.get("duration")
    if use_duration:
        condition["duration"] = use_duration
        # Would set actual expiration time
    
    character.db.conditions.append(condition)
    
    return True


def remove_condition(character, condition_key):
    """Remove a condition."""
    if not character.db.conditions:
        return False
    
    for i, cond in enumerate(character.db.conditions):
        if cond.get("key") == condition_key:
            character.db.conditions.pop(i)
            return True
    
    return False


def clear_conditions(character, category=None):
    """
    Clear conditions.
    
    Args:
        category: If provided, only clear conditions in this category
    """
    if not character.db.conditions:
        return
    
    if category:
        character.db.conditions = [
            c for c in character.db.conditions
            if VISIBLE_CONDITIONS.get(c["key"], {}).get("category") != category
        ]
    else:
        character.db.conditions = []


def clean_character(character):
    """Remove all conditions that require cleaning."""
    if not character.db.conditions:
        return
    
    character.db.conditions = [
        c for c in character.db.conditions
        if not VISIBLE_CONDITIONS.get(c["key"], {}).get("requires_cleaning")
    ]


def get_condition_descriptions(character):
    """Get list of condition description strings."""
    conditions = get_conditions(character)
    descriptions = []
    
    for cond in conditions:
        template = VISIBLE_CONDITIONS.get(cond["key"])
        if template:
            desc = template.get("desc", cond.get("name", ""))
            # Process pronouns
            try:
                from world.body import process_shortcodes
                desc = process_shortcodes(character, desc)
            except ImportError:
                pass
            descriptions.append(desc)
    
    return descriptions


# =============================================================================
# State-Based Description Generation
# =============================================================================

def get_state_description(character):
    """
    Generate a description snippet based on character's current state.
    
    Combines arousal, exhaustion, wounds, and conditions into
    readable description text.
    """
    parts = []
    
    # Wounds first (most visible)
    wound_level = get_wounds(character)
    if wound_level >= 2:
        wound_data = get_wound_data(character)
        parts.append(wound_data.get("desc", ""))
    
    # Exhaustion
    exhaustion_level = get_exhaustion(character)
    if exhaustion_level >= 2:
        exhaustion_data = get_exhaustion_data(character)
        hints = exhaustion_data.get("shortcode_hints", [])
        if hints:
            parts.append(choice(hints))
    
    # Arousal
    arousal_level = get_arousal(character)
    if arousal_level >= 2:
        arousal_data = get_arousal_data(character)
        hints = arousal_data.get("shortcode_hints", [])
        if hints:
            parts.append(choice(hints))
    
    # Visible conditions
    condition_descs = get_condition_descriptions(character)
    parts.extend(condition_descs[:3])  # Limit to 3 conditions shown
    
    if not parts:
        return ""
    
    # Combine naturally
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def get_state_hints(character):
    """
    Get list of state hints for shortcode processing.
    
    Returns list of short descriptive phrases.
    """
    hints = []
    
    # Wounds
    wound_data = get_wound_data(character)
    hints.extend(wound_data.get("shortcode_hints", []))
    
    # Exhaustion
    exhaustion_data = get_exhaustion_data(character)
    hints.extend(exhaustion_data.get("shortcode_hints", []))
    
    # Arousal
    arousal_data = get_arousal_data(character)
    hints.extend(arousal_data.get("shortcode_hints", []))
    
    return hints


# =============================================================================
# Integration Functions
# =============================================================================

def sync_from_combat(character):
    """
    Sync condition states from combat resource pools.
    
    Call after combat ends to translate combat damage
    into visible conditions.
    """
    try:
        from world.combat import get_resource, get_max_resource
        
        # HP -> Wounds
        hp = get_resource(character, "hp")
        max_hp = get_max_resource(character, "hp")
        hp_pct = hp / max_hp if max_hp > 0 else 1.0
        
        if hp_pct < 0.2:
            set_wounds(character, 5)
        elif hp_pct < 0.4:
            set_wounds(character, 4)
        elif hp_pct < 0.6:
            set_wounds(character, 3)
        elif hp_pct < 0.8:
            set_wounds(character, 2)
        elif hp_pct < 1.0:
            set_wounds(character, 1)
        else:
            set_wounds(character, 0)
        
        # Stamina -> Exhaustion
        stamina = get_resource(character, "stamina")
        max_stamina = get_max_resource(character, "stamina")
        stam_pct = stamina / max_stamina if max_stamina > 0 else 1.0
        
        if stam_pct < 0.1:
            set_exhaustion(character, 5)
        elif stam_pct < 0.3:
            set_exhaustion(character, 4)
        elif stam_pct < 0.5:
            set_exhaustion(character, 3)
        elif stam_pct < 0.7:
            set_exhaustion(character, 2)
        elif stam_pct < 0.9:
            set_exhaustion(character, 1)
        else:
            set_exhaustion(character, 0)
        
        # Composure -> Arousal
        composure = get_resource(character, "composure")
        max_composure = get_max_resource(character, "composure")
        comp_pct = composure / max_composure if max_composure > 0 else 1.0
        
        if comp_pct < 0.1:
            set_arousal(character, 6)
        elif comp_pct < 0.25:
            set_arousal(character, 5)
        elif comp_pct < 0.4:
            set_arousal(character, 4)
        elif comp_pct < 0.55:
            set_arousal(character, 3)
        elif comp_pct < 0.7:
            set_arousal(character, 2)
        elif comp_pct < 0.85:
            set_arousal(character, 1)
        else:
            set_arousal(character, 0)
    
    except ImportError:
        pass


def apply_defeat_conditions(character, defeat_type, victor=None):
    """
    Apply appropriate conditions after combat defeat.
    
    Args:
        character: The defeated character
        defeat_type: How they were defeated (hp, stamina, composure)
        victor: Who defeated them
    """
    if defeat_type == "hp":
        add_condition(character, "bruised")
        set_wounds(character, 3)
    
    elif defeat_type == "stamina":
        add_condition(character, "sweaty")
        set_exhaustion(character, 4)
    
    elif defeat_type == "composure":
        set_arousal(character, 5)
        add_condition(character, "disheveled")
    
    elif defeat_type == "submission":
        add_condition(character, "disheveled")


def initialize_conditions(character):
    """Initialize condition system for a character."""
    if not hasattr(character, "db"):
        return
    
    if character.db.arousal is None:
        character.db.arousal = 0
    if character.db.exhaustion is None:
        character.db.exhaustion = 0
    if character.db.wounds is None:
        character.db.wounds = 0
    if character.db.conditions is None:
        character.db.conditions = []
