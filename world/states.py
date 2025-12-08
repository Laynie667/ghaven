"""
Character State System for Gilderhaven

Tracks persistent character states like arousal, energy, and condition.
Provides shortcodes for dynamic descriptions based on state.

Separate from combat resources - these are RP/exploration states.
"""

from random import random, randint
from evennia.utils import delay

# =============================================================================
# STATE DEFINITIONS
# =============================================================================

# Arousal levels and their effects
AROUSAL_LEVELS = {
    0: {
        "name": "calm",
        "display": "calm",
        "desc": "",
        "color": "|w",
    },
    1: {
        "name": "aware",
        "display": "slightly warm",
        "desc": "A faint warmth stirs within &them.",
        "color": "|Y",
    },
    2: {
        "name": "interested",
        "display": "flushed",
        "desc": "&Their cheeks are flushed, breathing slightly quickened.",
        "color": "|y",
    },
    3: {
        "name": "aroused",
        "display": "visibly aroused",
        "desc": "&They &are clearly aroused, skin flushed and breath unsteady.",
        "color": "|M",
    },
    4: {
        "name": "needy",
        "display": "desperately needy",
        "desc": "&Their body trembles with need, eyes glazed with desire.",
        "color": "|m",
    },
    5: {
        "name": "desperate",
        "display": "overwhelmed with lust",
        "desc": "&They &are practically dripping with need, barely coherent.",
        "color": "|R",
    },
}

MAX_AROUSAL = 5
AROUSAL_DECAY_RATE = 1  # Points per decay tick
AROUSAL_DECAY_INTERVAL = 300  # Seconds between decay (5 min)

# Energy levels (out of combat stamina)
ENERGY_LEVELS = {
    "exhausted": {
        "range": (0, 20),
        "display": "exhausted",
        "desc": "&They look utterly spent, barely able to stand.",
        "color": "|r",
        "move_penalty": 0.5,
        "gather_penalty": 0.3,
    },
    "tired": {
        "range": (21, 40),
        "display": "tired",
        "desc": "&Their movements are sluggish, fatigue evident.",
        "color": "|y",
        "move_penalty": 0.8,
        "gather_penalty": 0.7,
    },
    "winded": {
        "range": (41, 60),
        "display": "a bit winded",
        "desc": "&They &are breathing a little heavily.",
        "color": "|Y",
        "move_penalty": 0.95,
        "gather_penalty": 0.9,
    },
    "rested": {
        "range": (61, 80),
        "display": "rested",
        "desc": "",
        "color": "|g",
        "move_penalty": 1.0,
        "gather_penalty": 1.0,
    },
    "energized": {
        "range": (81, 100),
        "display": "full of energy",
        "desc": "&They practically bounce with energy.",
        "color": "|G",
        "move_penalty": 1.0,
        "gather_penalty": 1.1,  # Bonus!
    },
}

MAX_ENERGY = 100
ENERGY_REGEN_RATE = 5  # Points per tick when resting
ENERGY_REGEN_INTERVAL = 60  # Seconds
ENERGY_COSTS = {
    "move": 1,
    "run": 3,
    "gather": 5,
    "mine": 8,
    "fish": 4,
    "forage": 3,
    "combat_round": 2,
    "craft": 3,
}

# Health condition (injuries, not HP)
CONDITION_LEVELS = {
    "critical": {
        "range": (0, 10),
        "display": "critically injured",
        "desc": "&They &are gravely wounded, barely clinging to consciousness.",
        "color": "|R",
    },
    "wounded": {
        "range": (11, 30),
        "display": "badly wounded",
        "desc": "Visible wounds mar &their body, blood staining &their skin.",
        "color": "|r",
    },
    "injured": {
        "range": (31, 50),
        "display": "injured",
        "desc": "Bruises and scrapes cover &them, wincing with movement.",
        "color": "|y",
    },
    "roughed_up": {
        "range": (51, 70),
        "display": "a bit roughed up",
        "desc": "A few marks and bruises are visible.",
        "color": "|Y",
    },
    "healthy": {
        "range": (71, 100),
        "display": "healthy",
        "desc": "",
        "color": "|g",
    },
}

MAX_CONDITION = 100
CONDITION_REGEN_RATE = 2  # Points per tick when resting
CONDITION_REGEN_INTERVAL = 120  # 2 minutes

# Hygiene/cleanliness
CLEANLINESS_LEVELS = {
    "filthy": {
        "range": (0, 20),
        "display": "filthy",
        "desc": "&They &are covered in grime, sweat, and worse.",
        "color": "|x",
    },
    "dirty": {
        "range": (21, 40),
        "display": "dirty",
        "desc": "Dirt and sweat cling to &their skin.",
        "color": "|X",
    },
    "messy": {
        "range": (41, 60),
        "display": "a bit messy",
        "desc": "&Their hair is disheveled, clothes rumpled.",
        "color": "|Y",
    },
    "presentable": {
        "range": (61, 80),
        "display": "presentable",
        "desc": "",
        "color": "|w",
    },
    "pristine": {
        "range": (81, 100),
        "display": "pristine",
        "desc": "&They &are immaculately clean and well-groomed.",
        "color": "|W",
    },
}

MAX_CLEANLINESS = 100
CLEANLINESS_DECAY_RATE = 1  # Per activity
CLEANLINESS_COSTS = {
    "move": 0,
    "gather": 2,
    "mine": 5,
    "combat": 10,
    "sex": 15,
    "swim": -20,  # Negative = cleans
    "bath": -50,
}

# Intoxication
INTOXICATION_LEVELS = {
    "sober": {
        "range": (0, 10),
        "display": "sober",
        "desc": "",
        "color": "|w",
    },
    "tipsy": {
        "range": (11, 30),
        "display": "tipsy",
        "desc": "&They &have a slight flush, movements loosened.",
        "color": "|Y",
    },
    "drunk": {
        "range": (31, 60),
        "display": "drunk",
        "desc": "&They sway slightly, words occasionally slurred.",
        "color": "|y",
    },
    "wasted": {
        "range": (61, 80),
        "display": "very drunk",
        "desc": "&They can barely walk straight, giggling at nothing.",
        "color": "|M",
    },
    "blackout": {
        "range": (81, 100),
        "display": "barely conscious",
        "desc": "&They &are barely standing, eyes unfocused.",
        "color": "|r",
    },
}

MAX_INTOXICATION = 100
INTOXICATION_DECAY_RATE = 5  # Per tick
INTOXICATION_DECAY_INTERVAL = 300  # 5 minutes


# =============================================================================
# State Retrieval Functions
# =============================================================================

def get_arousal(character):
    """Get character's arousal level (0-5)."""
    if not hasattr(character, "db"):
        return 0
    return character.db.arousal or 0


def set_arousal(character, value):
    """Set character's arousal level."""
    value = max(0, min(MAX_AROUSAL, value))
    character.db.arousal = value
    return value


def modify_arousal(character, amount):
    """Modify arousal by amount. Returns new value."""
    current = get_arousal(character)
    return set_arousal(character, current + amount)


def get_arousal_level(character):
    """Get arousal level data dict."""
    arousal = get_arousal(character)
    return AROUSAL_LEVELS.get(arousal, AROUSAL_LEVELS[0])


def get_energy(character):
    """Get character's energy (0-100)."""
    if not hasattr(character, "db"):
        return MAX_ENERGY
    if character.db.energy is None:
        character.db.energy = MAX_ENERGY
    return character.db.energy


def set_energy(character, value):
    """Set character's energy."""
    value = max(0, min(MAX_ENERGY, value))
    character.db.energy = value
    return value


def modify_energy(character, amount):
    """Modify energy by amount. Returns new value."""
    current = get_energy(character)
    return set_energy(character, current + amount)


def get_energy_level(character):
    """Get energy level data dict."""
    energy = get_energy(character)
    for level_key, level_data in ENERGY_LEVELS.items():
        low, high = level_data["range"]
        if low <= energy <= high:
            return level_data
    return ENERGY_LEVELS["rested"]


def get_condition(character):
    """Get character's physical condition (0-100)."""
    if not hasattr(character, "db"):
        return MAX_CONDITION
    if character.db.condition is None:
        character.db.condition = MAX_CONDITION
    return character.db.condition


def set_condition(character, value):
    """Set character's condition."""
    value = max(0, min(MAX_CONDITION, value))
    character.db.condition = value
    return value


def modify_condition(character, amount):
    """Modify condition by amount. Returns new value."""
    current = get_condition(character)
    return set_condition(character, current + amount)


def get_condition_level(character):
    """Get condition level data dict."""
    condition = get_condition(character)
    for level_key, level_data in CONDITION_LEVELS.items():
        low, high = level_data["range"]
        if low <= condition <= high:
            return level_data
    return CONDITION_LEVELS["healthy"]


def get_cleanliness(character):
    """Get character's cleanliness (0-100)."""
    if not hasattr(character, "db"):
        return MAX_CLEANLINESS
    if character.db.cleanliness is None:
        character.db.cleanliness = MAX_CLEANLINESS
    return character.db.cleanliness


def set_cleanliness(character, value):
    """Set character's cleanliness."""
    value = max(0, min(MAX_CLEANLINESS, value))
    character.db.cleanliness = value
    return value


def modify_cleanliness(character, amount):
    """Modify cleanliness by amount. Returns new value."""
    current = get_cleanliness(character)
    return set_cleanliness(character, current + amount)


def get_cleanliness_level(character):
    """Get cleanliness level data dict."""
    cleanliness = get_cleanliness(character)
    for level_key, level_data in CLEANLINESS_LEVELS.items():
        low, high = level_data["range"]
        if low <= cleanliness <= high:
            return level_data
    return CLEANLINESS_LEVELS["presentable"]


def get_intoxication(character):
    """Get character's intoxication (0-100)."""
    if not hasattr(character, "db"):
        return 0
    return character.db.intoxication or 0


def set_intoxication(character, value):
    """Set character's intoxication."""
    value = max(0, min(MAX_INTOXICATION, value))
    character.db.intoxication = value
    return value


def modify_intoxication(character, amount):
    """Modify intoxication by amount. Returns new value."""
    current = get_intoxication(character)
    return set_intoxication(character, current + amount)


def get_intoxication_level(character):
    """Get intoxication level data dict."""
    intox = get_intoxication(character)
    for level_key, level_data in INTOXICATION_LEVELS.items():
        low, high = level_data["range"]
        if low <= intox <= high:
            return level_data
    return INTOXICATION_LEVELS["sober"]


# =============================================================================
# State Initialization
# =============================================================================

def initialize_states(character):
    """Initialize all state values for a character."""
    if character.db.arousal is None:
        character.db.arousal = 0
    if character.db.energy is None:
        character.db.energy = MAX_ENERGY
    if character.db.condition is None:
        character.db.condition = MAX_CONDITION
    if character.db.cleanliness is None:
        character.db.cleanliness = MAX_CLEANLINESS
    if character.db.intoxication is None:
        character.db.intoxication = 0


def restore_all_states(character):
    """Restore all states to maximum/default."""
    character.db.arousal = 0
    character.db.energy = MAX_ENERGY
    character.db.condition = MAX_CONDITION
    character.db.cleanliness = MAX_CLEANLINESS
    character.db.intoxication = 0


# =============================================================================
# Energy Cost Functions
# =============================================================================

def spend_energy(character, activity, multiplier=1.0):
    """
    Spend energy for an activity.
    
    Returns:
        tuple: (success, new_energy)
    """
    cost = ENERGY_COSTS.get(activity, 1)
    cost = int(cost * multiplier)
    
    current = get_energy(character)
    
    if current < cost:
        return False, current
    
    new_energy = modify_energy(character, -cost)
    return True, new_energy


def can_afford_energy(character, activity, multiplier=1.0):
    """Check if character has enough energy for activity."""
    cost = ENERGY_COSTS.get(activity, 1)
    cost = int(cost * multiplier)
    return get_energy(character) >= cost


def get_activity_modifier(character, activity_type="gather"):
    """
    Get efficiency modifier based on energy level.
    
    Returns float multiplier (0.3 to 1.1)
    """
    level = get_energy_level(character)
    
    if activity_type == "gather":
        return level.get("gather_penalty", 1.0)
    elif activity_type == "move":
        return level.get("move_penalty", 1.0)
    
    return 1.0


# =============================================================================
# Arousal Functions
# =============================================================================

def arouse(character, amount=1, source=None):
    """
    Increase arousal.
    
    Args:
        character: Target character
        amount: How much to increase (1-5 typically)
        source: What caused the arousal (for messaging)
    
    Returns:
        tuple: (old_level, new_level, crossed_threshold)
    """
    old = get_arousal(character)
    new = modify_arousal(character, amount)
    
    crossed = new > old and new in AROUSAL_LEVELS
    
    if crossed and hasattr(character, "msg"):
        level_data = AROUSAL_LEVELS[new]
        if source:
            character.msg(f"|m{source} leaves you feeling {level_data['display']}.|n")
        else:
            character.msg(f"|mYou feel {level_data['display']}.|n")
    
    return old, new, crossed


def calm_down(character, amount=1):
    """
    Decrease arousal.
    
    Returns:
        tuple: (old_level, new_level)
    """
    old = get_arousal(character)
    new = modify_arousal(character, -amount)
    return old, new


def is_aroused(character):
    """Check if character is noticeably aroused (level 2+)."""
    return get_arousal(character) >= 2


def is_desperate(character):
    """Check if character is desperately aroused (level 4+)."""
    return get_arousal(character) >= 4


# =============================================================================
# Cleanliness Functions
# =============================================================================

def dirty(character, activity="generic"):
    """Make character dirtier from activity."""
    cost = CLEANLINESS_COSTS.get(activity, 2)
    if cost > 0:
        modify_cleanliness(character, -cost)


def clean(character, method="wash"):
    """Clean character."""
    if method == "bath":
        set_cleanliness(character, MAX_CLEANLINESS)
    elif method == "swim":
        modify_cleanliness(character, 20)
    elif method == "wash":
        modify_cleanliness(character, 30)
    else:
        modify_cleanliness(character, 10)


def is_dirty(character):
    """Check if character is noticeably dirty."""
    return get_cleanliness(character) < 60


def is_filthy(character):
    """Check if character is very dirty."""
    return get_cleanliness(character) < 30


# =============================================================================
# Intoxication Functions
# =============================================================================

def intoxicate(character, amount, source="drink"):
    """
    Increase intoxication.
    
    Returns new intoxication level.
    """
    old = get_intoxication(character)
    new = modify_intoxication(character, amount)
    
    # Check for level change
    old_level = None
    new_level = None
    for level_key, level_data in INTOXICATION_LEVELS.items():
        low, high = level_data["range"]
        if low <= old <= high:
            old_level = level_key
        if low <= new <= high:
            new_level = level_key
    
    if old_level != new_level and hasattr(character, "msg"):
        level_data = INTOXICATION_LEVELS.get(new_level, {})
        character.msg(f"|yYou feel {level_data.get('display', 'different')}.|n")
    
    return new


def sober_up(character, amount=None):
    """
    Decrease intoxication.
    
    If amount is None, uses decay rate.
    """
    if amount is None:
        amount = INTOXICATION_DECAY_RATE
    return modify_intoxication(character, -amount)


def is_drunk(character):
    """Check if character is noticeably drunk."""
    return get_intoxication(character) >= 30


def is_wasted(character):
    """Check if character is very drunk."""
    return get_intoxication(character) >= 60


# =============================================================================
# State Display Functions
# =============================================================================

def get_state_summary(character):
    """Get a one-line summary of notable states."""
    parts = []
    
    # Arousal
    arousal = get_arousal(character)
    if arousal >= 2:
        level = AROUSAL_LEVELS[arousal]
        parts.append(f"{level['color']}{level['display']}|n")
    
    # Energy
    energy_level = get_energy_level(character)
    if energy_level.get("range", (100, 100))[1] < 60:
        parts.append(f"{energy_level['color']}{energy_level['display']}|n")
    
    # Condition
    cond_level = get_condition_level(character)
    if cond_level.get("range", (100, 100))[1] < 70:
        parts.append(f"{cond_level['color']}{cond_level['display']}|n")
    
    # Cleanliness
    clean_level = get_cleanliness_level(character)
    if clean_level.get("range", (100, 100))[1] < 60:
        parts.append(f"{clean_level['color']}{clean_level['display']}|n")
    
    # Intoxication
    intox_level = get_intoxication_level(character)
    if intox_level.get("range", (0, 0))[0] > 10:
        parts.append(f"{intox_level['color']}{intox_level['display']}|n")
    
    return ", ".join(parts) if parts else ""


def get_state_display(character, verbose=False):
    """
    Get formatted display of all states.
    
    Args:
        character: Character to display
        verbose: If True, show numeric values
    """
    lines = ["|w=== STATUS ===|n"]
    
    # Energy
    energy = get_energy(character)
    energy_level = get_energy_level(character)
    bar = _make_bar(energy, MAX_ENERGY, "|g")
    if verbose:
        lines.append(f"Energy:     {bar} {energy}/{MAX_ENERGY} ({energy_level['display']})")
    else:
        lines.append(f"Energy:     {bar} {energy_level['display']}")
    
    # Condition
    condition = get_condition(character)
    cond_level = get_condition_level(character)
    bar = _make_bar(condition, MAX_CONDITION, "|y")
    if verbose:
        lines.append(f"Condition:  {bar} {condition}/{MAX_CONDITION} ({cond_level['display']})")
    else:
        lines.append(f"Condition:  {bar} {cond_level['display']}")
    
    # Arousal
    arousal = get_arousal(character)
    arousal_level = get_arousal_level(character)
    bar = _make_arousal_bar(arousal)
    if verbose:
        lines.append(f"Arousal:    {bar} {arousal}/{MAX_AROUSAL} ({arousal_level['display']})")
    else:
        lines.append(f"Arousal:    {bar} {arousal_level['display']}")
    
    # Cleanliness
    clean = get_cleanliness(character)
    clean_level = get_cleanliness_level(character)
    bar = _make_bar(clean, MAX_CLEANLINESS, "|c")
    if verbose:
        lines.append(f"Cleanliness:{bar} {clean}/{MAX_CLEANLINESS} ({clean_level['display']})")
    else:
        lines.append(f"Cleanliness:{bar} {clean_level['display']}")
    
    # Intoxication (only show if > 0)
    intox = get_intoxication(character)
    if intox > 0:
        intox_level = get_intoxication_level(character)
        bar = _make_bar(intox, MAX_INTOXICATION, "|m")
        if verbose:
            lines.append(f"Intoxication:{bar} {intox}/{MAX_INTOXICATION} ({intox_level['display']})")
        else:
            lines.append(f"Intoxication:{bar} {intox_level['display']}")
    
    return "\n".join(lines)


def _make_bar(current, maximum, color, length=10):
    """Create a visual bar."""
    filled = int((current / maximum) * length) if maximum > 0 else 0
    empty = length - filled
    return f"{color}{'█' * filled}|n{'░' * empty}"


def _make_arousal_bar(level, length=5):
    """Create arousal bar (discrete levels)."""
    colors = ["|w", "|Y", "|y", "|M", "|m", "|R"]
    filled = level
    empty = MAX_AROUSAL - level
    
    bar = ""
    for i in range(filled):
        bar += f"{colors[min(i+1, 5)]}♥|n"
    bar += "♡" * empty
    
    return bar


# =============================================================================
# State-Based Shortcodes
# =============================================================================

STATE_SHORTCODES = {
    # Energy
    "<state.energy>": lambda c: get_energy_level(c).get("display", "rested"),
    "<state.energy.desc>": lambda c: get_energy_level(c).get("desc", ""),
    
    # Condition
    "<state.condition>": lambda c: get_condition_level(c).get("display", "healthy"),
    "<state.condition.desc>": lambda c: get_condition_level(c).get("desc", ""),
    
    # Arousal
    "<state.arousal>": lambda c: get_arousal_level(c).get("display", "calm"),
    "<state.arousal.desc>": lambda c: get_arousal_level(c).get("desc", ""),
    "<state.arousal.level>": lambda c: str(get_arousal(c)),
    
    # Cleanliness
    "<state.clean>": lambda c: get_cleanliness_level(c).get("display", "presentable"),
    "<state.clean.desc>": lambda c: get_cleanliness_level(c).get("desc", ""),
    
    # Intoxication
    "<state.drunk>": lambda c: get_intoxication_level(c).get("display", "sober"),
    "<state.drunk.desc>": lambda c: get_intoxication_level(c).get("desc", ""),
    
    # Combined / summary
    "<state.summary>": lambda c: get_state_summary(c),
    
    # Conditional shortcodes (return text only if condition met)
    "<if.aroused>": lambda c: "" if get_arousal(c) < 2 else get_arousal_level(c).get("desc", ""),
    "<if.tired>": lambda c: "" if get_energy(c) > 60 else get_energy_level(c).get("desc", ""),
    "<if.hurt>": lambda c: "" if get_condition(c) > 70 else get_condition_level(c).get("desc", ""),
    "<if.dirty>": lambda c: "" if get_cleanliness(c) > 60 else get_cleanliness_level(c).get("desc", ""),
    "<if.drunk>": lambda c: "" if get_intoxication(c) < 20 else get_intoxication_level(c).get("desc", ""),
}


def process_state_shortcodes(character, text):
    """
    Process state-based shortcodes in text.
    
    Args:
        character: Character for state lookup
        text: Text containing shortcodes
        
    Returns:
        str: Text with shortcodes replaced
    """
    if not text or not character:
        return text or ""
    
    result = text
    
    for shortcode, func in STATE_SHORTCODES.items():
        if shortcode in result:
            try:
                replacement = func(character)
                result = result.replace(shortcode, replacement or "")
            except Exception:
                result = result.replace(shortcode, "")
    
    # Process pronoun placeholders in state descriptions
    # &they, &them, &their, &are, &have
    result = _process_pronouns(character, result)
    
    # Clean up double spaces from empty replacements
    while "  " in result:
        result = result.replace("  ", " ")
    
    return result.strip()


def _process_pronouns(character, text):
    """Replace pronoun placeholders with character's pronouns."""
    if not text:
        return text
    
    # Get pronouns (default to they/them)
    pronouns = {}
    if hasattr(character, "db") and character.db.pronouns:
        pronouns = character.db.pronouns
    
    subject = pronouns.get("subject", "they")
    obj = pronouns.get("object", "them")
    possessive = pronouns.get("possessive", "their")
    
    # Verb conjugation
    is_singular = subject.lower() in ("he", "she", "it")
    are_form = "is" if is_singular else "are"
    have_form = "has" if is_singular else "have"
    
    # Replace
    result = text
    result = result.replace("&they", subject)
    result = result.replace("&They", subject.capitalize())
    result = result.replace("&them", obj)
    result = result.replace("&their", possessive)
    result = result.replace("&Their", possessive.capitalize())
    result = result.replace("&are", are_form)
    result = result.replace("&have", have_form)
    
    return result


# =============================================================================
# Decay/Regen Tick Functions
# =============================================================================

def tick_arousal_decay(character):
    """Process arousal decay for a character."""
    current = get_arousal(character)
    if current > 0:
        calm_down(character, AROUSAL_DECAY_RATE)


def tick_energy_regen(character):
    """Process energy regeneration for a character."""
    # Only regen if resting (not in combat, not moving recently)
    if hasattr(character, "ndb"):
        if character.ndb.combat or character.ndb.encounter:
            return  # No regen in combat
    
    current = get_energy(character)
    if current < MAX_ENERGY:
        # Check if sitting/resting for bonus
        try:
            from world.positions import is_standing
            if not is_standing(character):
                # Resting bonus
                modify_energy(character, ENERGY_REGEN_RATE * 2)
            else:
                modify_energy(character, ENERGY_REGEN_RATE)
        except ImportError:
            modify_energy(character, ENERGY_REGEN_RATE)


def tick_condition_regen(character):
    """Process condition regeneration."""
    current = get_condition(character)
    if current < MAX_CONDITION:
        modify_condition(character, CONDITION_REGEN_RATE)


def tick_intoxication_decay(character):
    """Process intoxication decay."""
    current = get_intoxication(character)
    if current > 0:
        sober_up(character)


def tick_all_states(character):
    """Process all state ticks for a character."""
    tick_arousal_decay(character)
    tick_energy_regen(character)
    tick_condition_regen(character)
    tick_intoxication_decay(character)
