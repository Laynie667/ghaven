"""
Character Stats System - HARD MODE
===================================

Stats have real consequences. Hit zero? Face the outcome.
Manage your resources or get managed.

RESOURCE STATS (0-100, depleted and recovered):
    - Stamina: Physical energy
    - Composure: Mental/emotional stability  
    - Arousal: Sexual state

THRESHOLD STATS (1-20, resistance values):
    - Willpower: Resistance to mental manipulation
    - Sensitivity: How easily arousal builds
    - Resilience: Physical toughness

ACCUMULATION STATS (0-100, hard to reduce):
    - Corruption: Permanent mark of what's been done
    - Notoriety: How known/infamous you are

HARD MODE RULES:
    - Stamina 0 = Collapsed. Can't move, flee, or resist.
    - Composure 0 = Broken. Can't refuse commands.
    - Arousal 100 = Overwhelmed. Consequences trigger.
    - Combined states create compounding vulnerability.
"""

from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from evennia.utils import logger


# =============================================================================
# CONSTANTS
# =============================================================================

# Resource stat ranges
RESOURCE_MIN = 0
RESOURCE_MAX = 100

# Threshold stat ranges
THRESHOLD_MIN = 1
THRESHOLD_MAX = 20

# Accumulation stat ranges
ACCUMULATION_MIN = 0
ACCUMULATION_MAX = 100


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

STAMINA_STATES = {
    (70, 100): "energized",
    (40, 69): "normal",
    (20, 39): "tired",
    (1, 19): "exhausted",
    (0, 0): "collapsed",
}

COMPOSURE_STATES = {
    (70, 100): "composed",
    (40, 69): "flustered",
    (20, 39): "shaken",
    (1, 19): "breaking",
    (0, 0): "broken",
}

AROUSAL_STATES = {
    (0, 10): "calm",
    (11, 30): "warm",
    (31, 50): "aroused",
    (51, 70): "needy",
    (71, 90): "desperate",
    (91, 99): "edge",
    (100, 100): "overwhelmed",
}

CORRUPTION_STATES = {
    (0, 10): "pure",
    (11, 30): "touched",
    (31, 50): "tainted",
    (51, 70): "corrupted",
    (71, 90): "twisted",
    (91, 100): "lost",
}

NOTORIETY_STATES = {
    (0, 10): "unknown",
    (11, 30): "recognized",
    (31, 50): "known",
    (51, 70): "notorious",
    (71, 90): "infamous",
    (91, 100): "legendary",
}


# =============================================================================
# COMBINED STATES (triggered by multiple conditions)
# =============================================================================

def get_combined_states(character) -> List[str]:
    """
    Determine combined states from multiple stat conditions.
    These compound vulnerabilities trigger special mechanics.
    
    Returns:
        List of active combined state names
    """
    states = []
    
    stamina = get_stat(character, "stamina")
    composure = get_stat(character, "composure")
    arousal = get_stat(character, "arousal")
    corruption = get_stat(character, "corruption")
    
    # HELPLESS: Can't resist anything
    # Low stamina + low composure = completely vulnerable
    if stamina <= 20 and composure <= 20:
        states.append("helpless")
    
    # DESPERATE: Aching need overrides thought
    # Low composure + high arousal = will do anything for release
    if composure <= 30 and arousal >= 70:
        states.append("desperate")
    
    # BROKEN_IN: Conditioning taking hold
    # Low willpower from repeated breaking + high corruption
    if composure <= 10 and corruption >= 50:
        states.append("broken_in")
    
    # FERAL: Base instincts taking over
    # Collapsed stamina + high arousal = body acts on its own
    if stamina <= 10 and arousal >= 80:
        states.append("feral")
    
    # PLIABLE: Easy to manipulate
    # Tired + flustered = resistance is low
    if stamina <= 40 and composure <= 40:
        states.append("pliable")
    
    # OVERWHELMED: Everything is too much
    # Multiple stats in critical ranges
    if stamina <= 30 and composure <= 30 and arousal >= 60:
        states.append("overwhelmed")
    
    # IN_HEAT: Arousal dominant state
    # Very high arousal regardless of other stats
    if arousal >= 85:
        states.append("in_heat")
    
    # MARKED: Corruption is showing
    # High corruption affects appearance/reactions
    if corruption >= 70:
        states.append("marked")
    
    return states


# =============================================================================
# CORE STAT FUNCTIONS
# =============================================================================

def get_stat(character, stat_name: str) -> int:
    """
    Get a character's current stat value.
    
    Args:
        character: Character object
        stat_name: Name of the stat
        
    Returns:
        Current stat value (int)
    """
    stats = character.db.stats or {}
    
    # Default values
    defaults = {
        # Resource stats
        "stamina": 100,
        "composure": 100,
        "arousal": 0,
        # Threshold stats
        "willpower": 10,
        "sensitivity": 10,
        "resilience": 10,
        # Accumulation stats
        "corruption": 0,
        "notoriety": 0,
    }
    
    return stats.get(stat_name, defaults.get(stat_name, 0))


def set_stat(character, stat_name: str, value: int, silent: bool = False) -> int:
    """
    Set a character's stat to a specific value.
    Clamps to valid range and triggers threshold effects.
    
    Args:
        character: Character object
        stat_name: Name of the stat
        value: New value
        silent: If True, don't send messages
        
    Returns:
        Final stat value after clamping
    """
    # Determine range based on stat type
    if stat_name in ("stamina", "composure", "arousal"):
        min_val, max_val = RESOURCE_MIN, RESOURCE_MAX
    elif stat_name in ("willpower", "sensitivity", "resilience"):
        min_val, max_val = THRESHOLD_MIN, THRESHOLD_MAX
    elif stat_name in ("corruption", "notoriety"):
        min_val, max_val = ACCUMULATION_MIN, ACCUMULATION_MAX
    else:
        min_val, max_val = 0, 100
    
    # Clamp value
    old_value = get_stat(character, stat_name)
    new_value = max(min_val, min(max_val, value))
    
    # Store
    if not character.db.stats:
        character.db.stats = {}
    character.db.stats[stat_name] = new_value
    
    # Check for threshold crossings
    if not silent:
        _check_threshold_effects(character, stat_name, old_value, new_value)
    
    return new_value


def modify_stat(
    character, 
    stat_name: str, 
    amount: int, 
    reason: str = "",
    silent: bool = False
) -> Tuple[int, int, bool]:
    """
    Modify a stat by a given amount.
    
    Args:
        character: Character object
        stat_name: Name of the stat
        amount: Amount to add (negative to subtract)
        reason: Why this is happening (for messages)
        silent: If True, don't send messages
        
    Returns:
        Tuple of (old_value, new_value, crossed_threshold)
    """
    old_value = get_stat(character, stat_name)
    new_value = set_stat(character, stat_name, old_value + amount, silent=True)
    
    crossed = _check_threshold_effects(character, stat_name, old_value, new_value, reason, silent)
    
    return old_value, new_value, crossed


def _check_threshold_effects(
    character,
    stat_name: str,
    old_value: int,
    new_value: int,
    reason: str = "",
    silent: bool = False
) -> bool:
    """
    Check if a stat change crossed critical thresholds.
    Triggers hard mode consequences.
    
    Returns:
        True if a critical threshold was crossed
    """
    crossed = False
    
    # =========================================================================
    # STAMINA THRESHOLDS
    # =========================================================================
    if stat_name == "stamina":
        # Collapsed (hit 0)
        if old_value > 0 and new_value == 0:
            crossed = True
            if not silent:
                character.msg("|rYour body gives out. You collapse, unable to move.|n")
            _apply_state_effect(character, "collapsed")
        
        # Exhausted (dropped below 20)
        elif old_value >= 20 and new_value < 20 and new_value > 0:
            if not silent:
                character.msg("|yExhaustion weighs on you. Every movement is a struggle.|n")
        
        # Recovered from collapse
        elif old_value == 0 and new_value > 0:
            if not silent:
                character.msg("|gYou manage to stir, no longer completely helpless.|n")
            _remove_state_effect(character, "collapsed")
    
    # =========================================================================
    # COMPOSURE THRESHOLDS
    # =========================================================================
    elif stat_name == "composure":
        # Broken (hit 0)
        if old_value > 0 and new_value == 0:
            crossed = True
            if not silent:
                character.msg("|rYour will shatters. You can't refuse. You can't resist.|n")
            _apply_state_effect(character, "broken")
        
        # Breaking (dropped below 20)
        elif old_value >= 20 and new_value < 20 and new_value > 0:
            if not silent:
                character.msg("|yYou're barely holding on. One more push and you'll break.|n")
        
        # Recovered from broken
        elif old_value == 0 and new_value > 0:
            if not silent:
                character.msg("|gSome clarity returns. You're not completely broken anymore.|n")
            _remove_state_effect(character, "broken")
    
    # =========================================================================
    # AROUSAL THRESHOLDS
    # =========================================================================
    elif stat_name == "arousal":
        # Overwhelmed (hit 100)
        if old_value < 100 and new_value == 100:
            crossed = True
            if not silent:
                character.msg("|mPleasure overwhelms you completely. Your body betrays you.|n")
            _trigger_overwhelmed(character, reason)
        
        # Edge (hit 91+)
        elif old_value < 91 and new_value >= 91 and new_value < 100:
            if not silent:
                character.msg("|mYou're right on the edge. One more touch and you'll lose control.|n")
        
        # Desperate (hit 71+)
        elif old_value < 71 and new_value >= 71:
            if not silent:
                character.msg("|mNeed burns through you. It's getting hard to think.|n")
    
    # =========================================================================
    # CORRUPTION THRESHOLDS
    # =========================================================================
    elif stat_name == "corruption":
        # Check for corruption tier changes
        old_state = get_state_for_value(CORRUPTION_STATES, old_value)
        new_state = get_state_for_value(CORRUPTION_STATES, new_value)
        
        if old_state != new_state and new_value > old_value:
            crossed = True
            if not silent:
                messages = {
                    "touched": "|xSomething has changed in you. A faint stain on your essence.|n",
                    "tainted": "|xThe corruption spreads deeper. You can feel it taking hold.|n",
                    "corrupted": "|xDarkness has claimed part of you. There's no ignoring it now.|n",
                    "twisted": "|xYou're becoming something else. The corruption reshapes you.|n",
                    "lost": "|xThe corruption is complete. What you were is gone.|n",
                }
                if new_state in messages:
                    character.msg(messages[new_state])
            
            _trigger_corruption_change(character, old_state, new_state)
    
    return crossed


# =============================================================================
# STATE EFFECT HANDLERS
# =============================================================================

def _apply_state_effect(character, state: str):
    """Apply mechanical effects of entering a state."""
    
    if not character.db.active_states:
        character.db.active_states = []
    
    if state not in character.db.active_states:
        character.db.active_states.append(state)
    
    if state == "collapsed":
        # Can't move
        character.db.movement_blocked = True
        character.db.collapse_reason = "exhaustion"
        
        # Notify room
        if character.location:
            character.location.msg_contents(
                f"|y{character.key} collapses from exhaustion.|n",
                exclude=[character]
            )
    
    elif state == "broken":
        # Can't refuse commands
        character.db.can_refuse = False
        
        # Notify room
        if character.location:
            character.location.msg_contents(
                f"|y{character.key}'s resistance crumbles completely.|n",
                exclude=[character]
            )


def _remove_state_effect(character, state: str):
    """Remove mechanical effects of leaving a state."""
    
    if character.db.active_states and state in character.db.active_states:
        character.db.active_states.remove(state)
    
    if state == "collapsed":
        character.db.movement_blocked = False
        character.db.collapse_reason = None
    
    elif state == "broken":
        character.db.can_refuse = True


def _trigger_overwhelmed(character, reason: str = ""):
    """
    Handle arousal hitting 100.
    
    HARD MODE: This has consequences.
    - If denied/locked: Stuck at edge, composure damage
    - If not denied: Forced orgasm, arousal reset, stamina cost
    """
    is_denied = character.db.orgasm_denied or False
    is_locked = character.db.orgasm_locked or False
    
    if is_denied or is_locked:
        # Denied - stuck at overwhelming arousal, damages composure
        character.msg("|mYou're not permitted release. The denial burns.|n")
        modify_stat(character, "composure", -15, "denial overwhelm", silent=True)
        modify_stat(character, "arousal", -5, "edge stabilize", silent=True)  # Drop just below 100
        
        # Log denied orgasm
        if not character.db.denied_orgasms:
            character.db.denied_orgasms = 0
        character.db.denied_orgasms += 1
        
    else:
        # Not denied - forced orgasm
        character.msg("|mYou can't hold back. Release crashes through you.|n")
        
        if character.location:
            character.location.msg_contents(
                f"|m{character.key} shudders, overcome by pleasure.|n",
                exclude=[character]
            )
        
        # Reset arousal, cost stamina
        set_stat(character, "arousal", 10, silent=True)
        modify_stat(character, "stamina", -20, "orgasm", silent=True)
        
        # Log orgasm
        if not character.db.orgasm_count:
            character.db.orgasm_count = 0
        character.db.orgasm_count += 1
        character.db.last_orgasm = _get_game_time()


def _trigger_corruption_change(character, old_state: str, new_state: str):
    """
    Handle corruption tier changes.
    
    Higher corruption can trigger:
    - Appearance changes
    - New dialogue options
    - NPC reaction changes
    - Unlocked/forced content
    """
    # Store corruption history
    if not character.db.corruption_history:
        character.db.corruption_history = []
    
    character.db.corruption_history.append({
        "from": old_state,
        "to": new_state,
        "time": _get_game_time(),
    })
    
    # Trigger any corruption-specific effects
    # (This hooks into body transformation system when built)
    pass


def _get_game_time():
    """Get current game time for logging."""
    try:
        from typeclasses.scripts import get_world_time
        return get_world_time()
    except ImportError:
        import time
        return {"timestamp": time.time()}


# =============================================================================
# STATE LOOKUP
# =============================================================================

def get_state_for_value(state_dict: Dict, value: int) -> str:
    """Get the state name for a given value."""
    for (low, high), state_name in state_dict.items():
        if low <= value <= high:
            return state_name
    return "unknown"


def get_stamina_state(character) -> str:
    """Get character's stamina state name."""
    return get_state_for_value(STAMINA_STATES, get_stat(character, "stamina"))


def get_composure_state(character) -> str:
    """Get character's composure state name."""
    return get_state_for_value(COMPOSURE_STATES, get_stat(character, "composure"))


def get_arousal_state(character) -> str:
    """Get character's arousal state name."""
    return get_state_for_value(AROUSAL_STATES, get_stat(character, "arousal"))


def get_corruption_state(character) -> str:
    """Get character's corruption state name."""
    return get_state_for_value(CORRUPTION_STATES, get_stat(character, "corruption"))


def get_notoriety_state(character) -> str:
    """Get character's notoriety state name."""
    return get_state_for_value(NOTORIETY_STATES, get_stat(character, "notoriety"))


# =============================================================================
# STATE CHECKS (for mechanics)
# =============================================================================

def is_collapsed(character) -> bool:
    """Check if character is collapsed (stamina 0)."""
    return get_stat(character, "stamina") == 0


def is_broken(character) -> bool:
    """Check if character is broken (composure 0)."""
    return get_stat(character, "composure") == 0


def is_helpless(character) -> bool:
    """Check if character is helpless (collapsed or broken, or both critical)."""
    return is_collapsed(character) or is_broken(character) or "helpless" in get_combined_states(character)


def is_desperate(character) -> bool:
    """Check if character is in desperate state."""
    return "desperate" in get_combined_states(character)


def is_pliable(character) -> bool:
    """Check if character is easily manipulated."""
    return "pliable" in get_combined_states(character) or is_broken(character)


def is_in_heat(character) -> bool:
    """Check if character is in heat (very high arousal)."""
    return get_stat(character, "arousal") >= 85


def can_resist(character) -> bool:
    """Check if character can resist commands/manipulation."""
    if is_broken(character):
        return False
    if is_helpless(character):
        return False
    return True


def can_move(character) -> bool:
    """Check if character can move freely."""
    if is_collapsed(character):
        return False
    if character.db.movement_blocked:
        return False
    return True


def can_flee(character) -> bool:
    """Check if character can flee from a situation."""
    if not can_move(character):
        return False
    if get_stat(character, "stamina") < 20:
        return False  # Too exhausted to run
    return True


# =============================================================================
# RESISTANCE CHECKS
# =============================================================================

def check_willpower(character, difficulty: int = 10, modifier: int = 0) -> Tuple[bool, int]:
    """
    Make a willpower check against manipulation/commands.
    
    Args:
        character: Character making the check
        difficulty: Base difficulty (1-20)
        modifier: Situational modifier (negative = harder)
        
    Returns:
        Tuple of (success, margin)
    """
    import random
    
    if is_broken(character):
        return False, -100  # Auto-fail when broken
    
    willpower = get_stat(character, "willpower")
    composure = get_stat(character, "composure")
    
    # Low composure penalizes willpower checks
    composure_penalty = 0
    if composure < 40:
        composure_penalty = (40 - composure) // 10  # -1 to -4
    
    effective_willpower = willpower - composure_penalty + modifier
    roll = random.randint(1, 20)
    
    total = roll + effective_willpower
    margin = total - difficulty
    
    return margin >= 0, margin


def check_resilience(character, difficulty: int = 10, modifier: int = 0) -> Tuple[bool, int]:
    """
    Make a resilience check against physical effects.
    
    Args:
        character: Character making the check
        difficulty: Base difficulty (1-20)
        modifier: Situational modifier
        
    Returns:
        Tuple of (success, margin)
    """
    import random
    
    resilience = get_stat(character, "resilience")
    stamina = get_stat(character, "stamina")
    
    # Low stamina penalizes resilience checks
    stamina_penalty = 0
    if stamina < 40:
        stamina_penalty = (40 - stamina) // 10
    
    effective_resilience = resilience - stamina_penalty + modifier
    roll = random.randint(1, 20)
    
    total = roll + effective_resilience
    margin = total - difficulty
    
    return margin >= 0, margin


def calculate_arousal_gain(character, base_amount: int) -> int:
    """
    Calculate actual arousal gain based on sensitivity.
    
    Higher sensitivity = more arousal from stimulation.
    """
    sensitivity = get_stat(character, "sensitivity")
    
    # Sensitivity 10 is baseline (1.0x)
    # Sensitivity 1 is 0.5x
    # Sensitivity 20 is 2.0x
    multiplier = 0.5 + (sensitivity * 0.075)  # 0.575 to 2.0
    
    # Heat state increases gain
    if is_in_heat(character):
        multiplier *= 1.5
    
    return int(base_amount * multiplier)


# =============================================================================
# STAT MODIFICATION HELPERS
# =============================================================================

def drain_stamina(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Convenience function to drain stamina."""
    _, new_val, _ = modify_stat(character, "stamina", -abs(amount), reason, silent)
    return new_val


def restore_stamina(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Convenience function to restore stamina."""
    _, new_val, _ = modify_stat(character, "stamina", abs(amount), reason, silent)
    return new_val


def drain_composure(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Convenience function to drain composure."""
    _, new_val, _ = modify_stat(character, "composure", -abs(amount), reason, silent)
    return new_val


def restore_composure(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Convenience function to restore composure."""
    _, new_val, _ = modify_stat(character, "composure", abs(amount), reason, silent)
    return new_val


def build_arousal(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """
    Build arousal, applying sensitivity modifier.
    """
    actual_amount = calculate_arousal_gain(character, amount)
    _, new_val, _ = modify_stat(character, "arousal", actual_amount, reason, silent)
    return new_val


def reduce_arousal(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Reduce arousal (slower than building)."""
    _, new_val, _ = modify_stat(character, "arousal", -abs(amount), reason, silent)
    return new_val


def add_corruption(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """
    Add corruption. This is hard to remove.
    """
    _, new_val, _ = modify_stat(character, "corruption", abs(amount), reason, silent)
    return new_val


def add_notoriety(character, amount: int, reason: str = "", silent: bool = False) -> int:
    """Add notoriety from public events."""
    _, new_val, _ = modify_stat(character, "notoriety", abs(amount), reason, silent)
    return new_val


# =============================================================================
# STAT DISPLAY
# =============================================================================

def get_stat_bar(value: int, max_val: int = 100, width: int = 20) -> str:
    """Generate a visual stat bar."""
    filled = int((value / max_val) * width)
    empty = width - filled
    
    # Color based on percentage
    pct = value / max_val
    if pct >= 0.7:
        color = "|g"
    elif pct >= 0.4:
        color = "|y"
    elif pct >= 0.2:
        color = "|r"
    else:
        color = "|R"
    
    return f"{color}[{'█' * filled}{'░' * empty}]|n {value}/{max_val}"


def get_arousal_bar(value: int, width: int = 20) -> str:
    """Generate arousal bar with appropriate coloring."""
    filled = int((value / 100) * width)
    empty = width - filled
    
    if value >= 91:
        color = "|M"  # Bright magenta at edge
    elif value >= 71:
        color = "|m"  # Magenta when desperate
    elif value >= 31:
        color = "|r"  # Red when aroused
    else:
        color = "|n"  # Normal when low
    
    return f"{color}[{'█' * filled}{'░' * empty}]|n {value}/100"


def display_stats(character) -> str:
    """Generate full stat display for a character."""
    lines = []
    lines.append("|w=== Character Stats ===|n")
    lines.append("")
    
    # Resource stats
    lines.append("|wResource Stats:|n")
    lines.append(f"  Stamina:   {get_stat_bar(get_stat(character, 'stamina'))} ({get_stamina_state(character)})")
    lines.append(f"  Composure: {get_stat_bar(get_stat(character, 'composure'))} ({get_composure_state(character)})")
    lines.append(f"  Arousal:   {get_arousal_bar(get_stat(character, 'arousal'))} ({get_arousal_state(character)})")
    lines.append("")
    
    # Threshold stats
    lines.append("|wThreshold Stats:|n")
    lines.append(f"  Willpower:   {get_stat(character, 'willpower')}/20")
    lines.append(f"  Sensitivity: {get_stat(character, 'sensitivity')}/20")
    lines.append(f"  Resilience:  {get_stat(character, 'resilience')}/20")
    lines.append("")
    
    # Accumulation stats
    lines.append("|wAccumulation Stats:|n")
    lines.append(f"  Corruption: {get_stat_bar(get_stat(character, 'corruption'))} ({get_corruption_state(character)})")
    lines.append(f"  Notoriety:  {get_stat_bar(get_stat(character, 'notoriety'))} ({get_notoriety_state(character)})")
    lines.append("")
    
    # Combined states
    combined = get_combined_states(character)
    if combined:
        lines.append(f"|wActive States:|n {', '.join(combined)}")
    
    # Flags
    flags = []
    if character.db.orgasm_denied:
        flags.append("|rdenied|n")
    if character.db.orgasm_locked:
        flags.append("|rlocked|n")
    if not can_move(character):
        flags.append("|rimmobile|n")
    if not can_resist(character):
        flags.append("|rcannot resist|n")
    
    if flags:
        lines.append(f"|wFlags:|n {', '.join(flags)}")
    
    return "\n".join(lines)


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_stats(character, template: str = "default"):
    """
    Initialize stats for a new character.
    
    Templates:
        default - Balanced starting stats
        resilient - Higher willpower/resilience
        sensitive - Higher sensitivity, lower willpower
        corrupted - Starts with some corruption
    """
    templates = {
        "default": {
            "stamina": 100,
            "composure": 100,
            "arousal": 0,
            "willpower": 10,
            "sensitivity": 10,
            "resilience": 10,
            "corruption": 0,
            "notoriety": 0,
        },
        "resilient": {
            "stamina": 100,
            "composure": 100,
            "arousal": 0,
            "willpower": 14,
            "sensitivity": 8,
            "resilience": 14,
            "corruption": 0,
            "notoriety": 0,
        },
        "sensitive": {
            "stamina": 100,
            "composure": 100,
            "arousal": 10,
            "willpower": 6,
            "sensitivity": 16,
            "resilience": 8,
            "corruption": 0,
            "notoriety": 0,
        },
        "corrupted": {
            "stamina": 100,
            "composure": 80,
            "arousal": 20,
            "willpower": 8,
            "sensitivity": 14,
            "resilience": 10,
            "corruption": 30,
            "notoriety": 10,
        },
    }
    
    stats = templates.get(template, templates["default"])
    character.db.stats = dict(stats)
    
    # Initialize tracking
    character.db.active_states = []
    character.db.orgasm_denied = False
    character.db.orgasm_locked = False
    character.db.orgasm_count = 0
    character.db.denied_orgasms = 0
    character.db.can_refuse = True
    character.db.movement_blocked = False
    
    return stats


# =============================================================================
# SHORTCODE INTEGRATION
# =============================================================================

def get_stat_shortcodes(character) -> Dict[str, str]:
    """
    Get all stat-related shortcode replacements for a character.
    
    Returns dict that can be used for string replacement.
    
    Usage in descriptions:
        "<char.stamina_state>" -> "exhausted"
        "<char.arousal>" -> "75"
        "<char.is_broken>" -> "true" or "false"
    """
    return {
        # Raw values
        "char.stamina": str(get_stat(character, "stamina")),
        "char.composure": str(get_stat(character, "composure")),
        "char.arousal": str(get_stat(character, "arousal")),
        "char.corruption": str(get_stat(character, "corruption")),
        "char.notoriety": str(get_stat(character, "notoriety")),
        "char.willpower": str(get_stat(character, "willpower")),
        "char.sensitivity": str(get_stat(character, "sensitivity")),
        "char.resilience": str(get_stat(character, "resilience")),
        
        # State names
        "char.stamina_state": get_stamina_state(character),
        "char.composure_state": get_composure_state(character),
        "char.arousal_state": get_arousal_state(character),
        "char.corruption_state": get_corruption_state(character),
        "char.notoriety_state": get_notoriety_state(character),
        
        # Boolean checks (as strings for replacement)
        "char.is_collapsed": "true" if is_collapsed(character) else "false",
        "char.is_broken": "true" if is_broken(character) else "false",
        "char.is_helpless": "true" if is_helpless(character) else "false",
        "char.is_desperate": "true" if is_desperate(character) else "false",
        "char.is_in_heat": "true" if is_in_heat(character) else "false",
        "char.can_resist": "true" if can_resist(character) else "false",
        "char.can_move": "true" if can_move(character) else "false",
        
        # Combined states as comma-separated
        "char.states": ", ".join(get_combined_states(character)) or "none",
    }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Core functions
    "get_stat",
    "set_stat", 
    "modify_stat",
    "initialize_stats",
    
    # State getters
    "get_stamina_state",
    "get_composure_state",
    "get_arousal_state",
    "get_corruption_state",
    "get_notoriety_state",
    "get_combined_states",
    
    # State checks
    "is_collapsed",
    "is_broken",
    "is_helpless",
    "is_desperate",
    "is_pliable",
    "is_in_heat",
    "can_resist",
    "can_move",
    "can_flee",
    
    # Resistance checks
    "check_willpower",
    "check_resilience",
    "calculate_arousal_gain",
    
    # Convenience modifiers
    "drain_stamina",
    "restore_stamina",
    "drain_composure",
    "restore_composure",
    "build_arousal",
    "reduce_arousal",
    "add_corruption",
    "add_notoriety",
    
    # Display
    "display_stats",
    "get_stat_bar",
    
    # Shortcodes
    "get_stat_shortcodes",
]
